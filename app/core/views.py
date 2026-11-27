from datetime import datetime
from urllib.parse import quote

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils import translation
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.views.decorators.http import require_GET

from catalog.services import fmt_eur, min_price, repair_name, repair_photo, snapshot
from content.models import FAQ, BeforeAfter, WorkshopCard
from content.texts import fill
from shops.hours import is_open_now, t_fmt
from shops.models import BERLIN, Shop

from .cache import site_version
from .models import SiteSettings
from .page import base_context, images
from .templatetags.tt import FILM_MEDIA
from .structured import dump, faq_page, local_business

REP_ROT = [-9, 7, -5, 10, -12, 6]
CAB_GROUPS = [("br_phone", "phone"), ("br_laptop", "laptop"), ("br_console", "console")]


def wa_link(number: str, msg: str) -> str:
    return f"https://wa.me/{number}?text={quote(msg)}"


def status_text(shop: Shop, T: dict, lang: str) -> tuple[bool, str]:
    """Server-side first paint of the open status; the page script keeps it current every minute."""
    now = datetime.now(BERLIN)
    is_open, at = is_open_now(shop, now)
    if is_open:
        return True, fill(T["open"], t=t_fmt(at.timetz(), lang))
    if at is None:
        return False, T.get("closed_now", "")
    days = (at.date() - now.date()).days
    label = T["today"] if days == 0 else T["tomorrow"] if days == 1 else T["days"][(at.weekday() + 1) % 7]
    return False, fill(T["closed"], d=label, t=t_fmt(at.timetz(), lang))


def shop_status(T, lang) -> dict:
    out = {}
    for s in Shop.objects.filter(active=True).prefetch_related("hours"):
        out[s.key] = status_text(s, T, lang)
    return out


def home(request):
    lang = translation.get_language()
    request.is_home = True
    ctx = base_context(request, "home")
    T, snap = ctx["T"], ctx["snap"]
    S = SiteSettings.load()
    cats = [{"key": c, "name": T[f"cat_{c}"], "sub": T[f"cat_{c}_s"]} for c in ("phone", "tablet", "laptop", "console")]
    rail = []
    for i, k in enumerate(snap["top"].get("phone", [])[:6]):
        p = min_price(snap, "phone", k)
        rep = snap["rep"][k]
        rail.append({
            "key": k, "img": repair_photo(snap, "phone", "Apple", k) or rep["img"] or "rep-display",
            "name": repair_name(snap, k, "phone", lang),
            "price": fmt_eur(p, lang) if p is not None else "", "delay": f"{(i % 3) * .08:g}",
            "d": f"{.45 + (i % 3) * .12:.2f}", "r": REP_ROT[i % len(REP_ROT)],
        })
    cab = []
    for lab, g in CAB_GROUPS:
        items = [d for d in snap["drawers"] if d["group"] == g]
        cab.append({"label": T[lab], "g": g, "items": [dict(d, d=f"{i * .04:.2f}") for i, d in enumerate(items)]})
    pair = BeforeAfter.objects.filter(active=True).select_related("before", "after").first()
    lab = [
        {"img": c.image.key, "title": c.title(lang), "text": c.text(lang), "repair": c.repair.key if c.repair_id else ""}
        for c in WorkshopCard.objects.filter(active=True).select_related("image", "repair")
    ]
    faq = [{"q": f.q(lang), "a": f.a(lang)} for f in FAQ.objects.filter(active=True)]
    status = shop_status(T, lang)
    main = ctx["MAIN_SHOP"]
    try:
        count = int(str(T.get("lab_count", "20000")).replace(".", "").replace(",", ""))
    except ValueError:
        count = 20000
    sell_cond = 1
    ctx.update({
        "cats": cats, "rail": rail, "cab": cab, "pair": pair, "lab": lab, "faq": faq, "status": status,
        "main_status": status.get(main["key"]) if main else (False, ""),
        "lab_note_html": mark_safe(escape(T.get("lab_note", "")).replace(
            "{n}", f'<b data-count="{count}">{count:,}</b>'.replace(",", "." if lang == "de" else ","))),
        "sell_cond": sell_cond,
        "sell_wa": wa_link(S.whatsapp_number, fill(T["wa_sell"], c=T["cat_phone"], m="?", k=T["conds"][sell_cond])),
        "pick_wa": wa_link(S.whatsapp_number, T["wa_pick"]),
        "general_wa": wa_link(S.whatsapp_number, T["wa_general"]),
        "hero_video": S.hero_video.url if S.hero_video else "",
        # desktop shows the film's first frame instead of the repair photo, so the start of the film doesn't jump
        "hero_film": "hero-film" if S.hero_video and "hero-film" in ctx["IMGS"] else "",
        "film_media": FILM_MEDIA, "film_media_not": f"not all and {FILM_MEDIA}",
        "photo_max": settings.OFFER_PHOTO_MAX,
        "page_title": "",
        "ld_json": dump([local_business(sh, S, lang) for sh in ctx["SHOPS"]] + ([faq_page(faq)] if faq else [])),
    })
    return render(request, "site/home.html", ctx)


@require_GET
def catalog_json(request):
    """Models, repairs and prices for the price calculator. Versioned URL, so it can be cached for long."""
    data = dict(snapshot())
    # responsive image URLs for the repair photos the calculator may show (iPhone, Android, tablet, laptop, console sets)
    im = images()
    keys = {v for group in data.get("rimg", {}).values() for v in group.values()}
    data["img"] = {k: im[k] for k in sorted(keys) if k in im}
    resp = JsonResponse(data, json_dumps_params={"ensure_ascii": False, "separators": (",", ":")})
    if request.GET.get("v") == str(site_version()):
        resp["Cache-Control"] = "public, max-age=31536000, immutable"
    else:
        resp["Cache-Control"] = "public, max-age=30"
    return resp


def healthz(request):
    return HttpResponse("ok", content_type="text/plain")


def robots(request):
    lines = ["User-agent: *", "Disallow: /admin/", "Disallow: /api/"]
    if getattr(settings, "ENVIRONMENT", "") != "production":
        lines = ["User-agent: *", "Disallow: /"]
    lines.append(f"Sitemap: {settings.SITE_URL}/sitemap.xml")
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain")
