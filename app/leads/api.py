"""POST /api/requests/: callback, repair request form, withdrawal, buyback offer with photos, plus WhatsApp-start and
sale beacons.

Accepts JSON (the page script), multipart (buyback photos) or a normal form post (works without JavaScript; answers
with a redirect).
"""
import json
import logging
import re
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpResponseRedirect, JsonResponse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from catalog.models import DeviceModel
from core.routes import page_url

from . import spam
from .models import Request, Withdrawal

log = logging.getLogger(__name__)

ACTIONABLE = {"callback", "form", "withdrawal", "offer"}
BEACONS = {"whatsapp", "sale"}
METHODS = ["moabit", "mailin"]  # walk in at Beusselstraße 18, or send it in (no second shop, no pickup since 17 Nov 2026)
VIAS = {"whatsapp", "phone"}


def _clip(v, n):
    return re.sub(r"\s+", " ", str(v or "")).strip()[:n]


def _text(v, n):
    return str(v or "").strip()[:n]


def _amount(v):
    try:
        d = Decimal(str(v))
    except (InvalidOperation, TypeError, ValueError):
        return None
    return d if Decimal("0") <= d < Decimal("100000") else None


def _repairs(raw) -> list[dict]:
    out = []
    if not isinstance(raw, list):
        return out
    for r in raw[:20]:
        if not isinstance(r, dict):
            continue
        out.append({
            "key": _clip(r.get("key"), 30), "tier": _clip(r.get("tier"), 2), "name": _clip(r.get("name"), 80),
            "price": float(a) if (a := _amount(r.get("price"))) is not None else None, "from": bool(r.get("from")),
        })
    return out


def _payload(request) -> tuple[dict, bool]:
    ctype = request.META.get("CONTENT_TYPE", "")
    if ctype.startswith("application/json"):
        try:
            data = json.loads(request.body or b"{}")
        except (json.JSONDecodeError, UnicodeDecodeError):
            data = {}
        return (data if isinstance(data, dict) else {}), True
    data = request.POST.dict()
    # chips on the no-JS form post their index
    if "method_i" in data and "method" not in data:
        i = str(data["method_i"])
        data["method"] = METHODS[int(i) if i.isdigit() and int(i) < len(METHODS) else 0]
    if "via_i" in data and "contact_via" not in data:
        data["contact_via"] = ["whatsapp", "phone"][1 if str(data.get("via_i")) == "1" else 0]
    # the page script sends photos as multipart and asks for a JSON answer
    return data, "application/json" in request.META.get("HTTP_ACCEPT", "")


def _answer(is_json, status=200, back=None, **body):
    if is_json:
        return JsonResponse(body, status=status)
    target = back or "/"
    if status >= 400:
        sep = "&" if "?" in target else "?"
        return HttpResponseRedirect(f"{target}{sep}error={body.get('error', 'send')}")
    return HttpResponseRedirect(target)


@require_POST
def submit(request):
    data, is_json = _payload(request)
    kind = str(data.get("kind", ""))
    lang = "en" if data.get("lang") == "en" else "de"
    back = str(data.get("back") or "")
    # only a path on this site: "//evil.example" or "https://…" would be an open redirect
    if not (back.startswith("/") and not back.startswith(("//", "/\\"))
            and url_has_allowed_host_and_scheme(back, allowed_hosts={request.get_host()}, require_https=request.is_secure())):
        back = None

    if kind not in ACTIONABLE | BEACONS:
        return _answer(is_json, 400, back, error="kind")

    # rate limits: actionable forms are strict, beacons only stop floods
    if kind in ACTIONABLE:
        if spam.rate_limited(request, "form", settings.FORM_RATE_LIMIT, settings.FORM_RATE_WINDOW):
            return _answer(is_json, 429, back, error="rate")
    elif spam.rate_limited(request, "beacon", 60, 600):
        return _answer(is_json, 429, back, error="rate")

    # honeypot: answer like a success so bots learn nothing, store nothing
    if spam.honeypot_hit(data):
        log.info("honeypot hit on %s", kind)
        return _answer(is_json, 200, back, ok=True)
    if kind in ACTIONABLE and spam.too_fast(data):
        log.info("timing check failed on %s", kind)
        return _answer(is_json, 400, back, error="timing")

    fields = {
        "kind": kind, "language": lang, "source": _clip(data.get("source"), 200),
        "category": _clip(data.get("category"), 20), "device": _clip(data.get("device"), 160),
    }
    model_id = data.get("model_id")
    if model_id:
        fields["device_model"] = DeviceModel.objects.filter(pk=model_id if str(model_id).isdigit() else 0).first()

    if kind in ("callback", "form", "offer"):
        name, phone = _clip(data.get("name"), 120), _clip(data.get("phone"), 40)
        if not name:
            return _answer(is_json, 400, back, error="name", field="name")
        if len(re.sub(r"\D", "", phone)) < 6 or not re.fullmatch(r"[0-9+()/.\- ]{6,40}", phone):
            return _answer(is_json, 400, back, error="phone", field="phone")
        fields.update(name=name, phone=phone)
    if kind == "callback" or kind == "whatsapp":
        fields.update(
            repairs=_repairs(data.get("repairs")), repairs_text=_clip(data.get("repairs_text"), 400),
            total_text=_clip(data.get("total"), 80), total_amount=_amount(data.get("total_amount")),
        )
        if kind == "whatsapp" and data.get("method") == "pickup":
            fields["method"] = "pickup"
    if kind == "form":
        method = data.get("method") if data.get("method") in METHODS else ""
        fields.update(problem=_text(data.get("problem"), 2000), method=method,
                      contact_via=data.get("contact_via") if data.get("contact_via") in VIAS else "")
    if kind in ("sale", "offer"):
        fields.update(condition=_clip(data.get("condition"), 40))
    if kind == "offer":
        files = request.FILES.getlist("photos")
        if not files or len(files) > settings.OFFER_PHOTO_MAX:
            return _answer(is_json, 400, back, error="photos", field="photos")
        fields.update(repairs_text=_clip(data.get("repairs_text"), 400), total_text=f"{len(files)} Foto(s)")
        from .photos import PhotoError, save_photos

        try:
            with transaction.atomic():
                req = Request.objects.create(**fields)
                save_photos(req, files)
        except PhotoError as e:
            return _answer(is_json, 400, back, error="photo", field="photos", reason=str(e))
        from .tasks import after_new_request

        transaction.on_commit(lambda: after_new_request.delay(req.pk))
        return _answer(is_json, 200, back, ok=True, id=req.pk)

    if kind == "withdrawal":
        name, email, ref = _clip(data.get("name"), 120), _clip(data.get("email"), 254), _clip(data.get("reference"), 120)
        if not name:
            return _answer(is_json, 400, back, error="name", field="name")
        try:
            validate_email(email)
        except ValidationError:
            return _answer(is_json, 400, back, error="email", field="email")
        if not ref:
            return _answer(is_json, 400, back, error="reference", field="reference")
        device, message = _clip(data.get("device"), 160), _text(data.get("message"), 2000)
        with transaction.atomic():
            req = Request.objects.create(
                kind=kind, language=lang, source=fields["source"], name=name, email=email, device=device,
                repairs_text=f"Widerruf: {ref}", problem=message, contact_via=Request.Via.EMAIL,
            )
            wd = Withdrawal.objects.create(request=req, reference=ref, device=device, message=message,
                                           received_at=req.created_at, confirmation_to=email)
        from .tasks import after_new_request, send_withdrawal_confirmation

        mail_ok = send_withdrawal_confirmation(wd.pk, inline=True)  # immediately, in this request (§ 356a BGB)
        transaction.on_commit(lambda: after_new_request.delay(req.pk))
        received = timezone.localtime(wd.received_at)
        if not is_json:
            from django.core import signing

            token = signing.dumps(wd.pk, salt="wd-receipt")
            return HttpResponseRedirect(f"{page_url('withdraw', lang)}?receipt={token}")
        return JsonResponse({"ok": True, "id": req.pk, "received_at": received.isoformat(), "mail_ok": mail_ok,
                             "withdrawal": {"reference": ref, "device": device, "message": message}})

    req = Request.objects.create(**fields)
    if kind in ACTIONABLE:
        from .tasks import after_new_request

        transaction.on_commit(lambda: after_new_request.delay(req.pk))
    if not is_json:
        return HttpResponseRedirect(f"{back or page_url('request', lang)}?sent=1")
    return JsonResponse({"ok": True, "id": req.pk})
