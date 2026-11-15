import io

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import translation

from catalog.services import snapshot
from core.page import base_context
from core.routes import alternates

ERRORS = {"name": "err_name", "phone": "err_phone", "rate": "err_rate", "timing": "err_send", "kind": "err_send", "send": "err_send"}


def request_page(request):
    """/anfrage: the shareable repair request page (SOW F12)."""
    lang = translation.get_language()
    from legal.views import canonical_redirect

    redirect = canonical_redirect(request, "request", lang)
    if redirect:
        return redirect
    ctx = base_context(request, "request", alt=alternates("request"))
    T = ctx["T"]
    snap = snapshot()
    ctx.update({
        "page_title": T.get("lf_h", "").replace("­", ""),
        "cats": [{"key": c, "name": T[f"cat_{c}"]} for c in ("phone", "tablet", "laptop", "console")],
        "phone_models": [m[lang] for m in snap["models"] if m["cat"] == "phone"],
        "sent": request.GET.get("sent") == "1",
        "error_text": T.get(ERRORS.get(request.GET.get("error", ""), ""), "") if request.GET.get("error") else "",
        "prefill": request.GET.get("q", "")[:300],
    })
    return render(request, "site/request.html", ctx)


def qr(request, fmt: str):
    """QR code for the request page, for print (receipts, shop window). /qr/anfrage.png or .svg"""
    import qrcode

    url = f"{settings.SITE_URL}/anfrage"
    key = f"qr:{fmt}:{url}"
    data = cache.get(key)
    if data is None:
        if fmt == "svg":
            import qrcode.image.svg

            img = qrcode.make(url, image_factory=qrcode.image.svg.SvgPathImage, box_size=20, border=4)
        else:
            q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=40, border=4)
            q.add_data(url)
            q.make(fit=True)
            img = q.make_image(fill_color="#12141C", back_color="white")
        buf = io.BytesIO()
        img.save(buf)
        data = buf.getvalue()
        cache.set(key, data, 24 * 3600)
    resp = HttpResponse(data, content_type="image/svg+xml" if fmt == "svg" else "image/png")
    resp["Content-Disposition"] = f'inline; filename="tiptop-anfrage-qr.{fmt}"'
    return resp
