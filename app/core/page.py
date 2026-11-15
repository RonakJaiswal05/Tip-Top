"""Everything a public page needs: texts, shops, images and the data block for the page script."""
import json
import time
from datetime import date

from django.core import signing

from django.middleware.csrf import get_token
from django.utils import translation

from catalog.services import fmt_eur, min_price, snapshot
from content.models import MediaAsset
from content.texts import fill, texts
from core.cache import cached, site_version
from shops.hours import footer_lines, open_data, summary
from shops.models import Shop

from legal.cookies import cookie_table

from .models import SiteSettings
from .routes import PAGES, alternates, page_url

# The only inline script: adds the motion class before first paint so the hero animation starts with the page.
# Its hash is allowed in the Content-Security-Policy (see core.middleware); keep the two in sync via HEAD_JS_HASH.
HEAD_JS = 'if(!matchMedia("(prefers-reduced-motion: reduce)").matches)document.documentElement.classList.add("anim")'
HEAD_JS_HASH = "sha256-" + __import__("base64").b64encode(__import__("hashlib").sha256(HEAD_JS.encode()).digest()).decode()

MONTHS = {
    "de": ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"],
    "en": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
}


def date_long(d: date, lang: str) -> str:
    if lang == "de":
        return f"{d.day}. {MONTHS['de'][d.month - 1]} {d.year}"
    return f"{d.day} {MONTHS['en'][d.month - 1]} {d.year}"


def images() -> dict:
    def build():
        out = {}
        for a in MediaAsset.objects.filter(published=True):
            u = a.urls()
            if "s" not in u:
                continue
            u["alt"] = {"de": a.alt("de"), "en": a.alt("en")}
            out[a.key] = u
        return out

    return cached("images", build)


def shops_data(lang: str) -> list[dict]:
    def build():
        out = []
        shops = list(Shop.objects.filter(active=True).prefetch_related("hours").order_by("order"))
        for s in shops:
            out.append({
                "key": s.key, "area": s.area, "short": s.short, "street": s.street, "zip": f"{s.postal_code} {s.city}",
                "postal_code": s.postal_code, "city": s.city, "tel": s.phone, "telTxt": s.phone_display, "email": s.email,
                "maps": s.maps_url, "rating": float(s.rating) if s.rating is not None else None, "count": s.rating_count,
                "asof": date_long(s.rating_fetched_at.date(), lang) if s.rating_fetched_at else "",
                "photo": s.photo.key if s.photo_id else f"shop-{s.key}", "workshop": s.is_workshop, "mailin": s.is_mail_in,
                "hours": summary([s], lang), "lat": float(s.latitude) if s.latitude is not None else None,
                "lng": float(s.longitude) if s.longitude is not None else None, "place_id": s.google_place_id,
                "weekly": {d: [(o.strftime("%H:%M"), c.strftime("%H:%M")) for o, c in iv] for d, iv in s.weekly_hours().items()},
            })
        return out

    return cached(f"shops-{lang}", build)


def page_texts(lang: str) -> dict:
    def build():
        T = dict(texts(lang))
        shops = list(Shop.objects.filter(active=True).prefetch_related("hours").order_by("order"))
        long_h, short_h = summary(shops, lang, long=True), summary(shops, lang)
        for k in ("shops_p", "lf_p"):
            if isinstance(T.get(k), str):
                T[k] = fill(T[k], hours=long_h)
        if isinstance(T.get("wi_s"), str):
            T["wi_s"] = fill(T["wi_s"], hours=short_h)
        T["f_hours_lines"] = footer_lines(shops, lang, T.get("f_hours_sun", ""))
        return T

    return cached(f"page-texts-{lang}", build)


JS_IMAGES = ("hero", "cat-phone", "cat-tablet", "cat-laptop", "cat-console", "rep-display", "rep-battery", "rep-port",
             "rep-back", "rep-camera", "rep-water")


def base_context(request, key: str = "home", alt: dict | None = None, title: str = "", description: str = "") -> dict:
    lang = translation.get_language() or "de"
    S = SiteSettings.load()
    T = page_texts(lang)
    IMGS = images()
    snap = snapshot()
    shops = shops_data(lang)
    request.alternates = alt or alternates(key)
    get_token(request)  # sets the csrftoken cookie the page script sends with form posts
    consent_cats = S.consent_categories
    data = {
        "lang": lang,
        "t": T,
        "wa": S.whatsapp_number,
        "urls": {k: page_url(k, lang) for k in PAGES},
        "api": {"catalog": f"/api/catalog.json?v={site_version()}", "request": "/api/requests/", "consent": "/api/consent/"},
        "shops": [{k: s[k] for k in ("key", "area", "short", "street", "zip", "tel", "telTxt", "maps", "mailin")} for s in shops],
        "open": open_data(),
        "img": {k: IMGS[k] for k in JS_IMAGES if k in IMGS},
        "consent": {"v": S.consent_version, "cats": consent_cats},
        "mailin": next((f"TipTop Service 24, {s['street']}, {s['zip']}" for s in shops if s["mailin"]), ""),
        "home": key == "home",
        "page": key,
        "ts": signing.dumps(int(time.time()), salt="form-ts"),
        "cookies": cookie_table(lang, consent_cats),
    }
    if S.analytics_enabled and S.matomo_url:
        data["matomo"] = {"url": S.matomo_url, "site": S.matomo_site_id}
    if S.ads_enabled and S.google_ads_id:
        data["ads"] = {"gads": S.google_ads_id}
    main = next((s for s in shops if s["workshop"]), shops[0] if shops else None)
    return {
        "T": T, "IMGS": IMGS, "SHOPS": shops, "MAIN_SHOP": main, "snap": snap, "page_key": key,
        "page_title": title, "page_description": description,
        "page_data": json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/"),
        "hero_price": fmt_eur(min_price(snap, "phone", "display"), lang) if snap["models"] else "",
        "consent_cats": consent_cats,
    }
