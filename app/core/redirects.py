"""Where old Shopify addresses go. Explicit rules from the admin win; otherwise the closest new page."""
import re

from django.core.cache import cache

from .models import Redirect, normalise_path

DEFAULTS = {
    "/policies/legal-notice": "/de/impressum/",
    "/policies/privacy-policy": "/de/datenschutz/",
    "/policies/terms-of-service": "/de/agb/",
    "/policies/refund-policy": "/de/widerruf/",
    "/policies/shipping-policy": "/de/agb/",
    "/policies/contact-information": "/de/impressum/",
    "/pages/contact": "/de/#shops",
    "/pages/kontakt": "/de/#shops",
    "/pages/impressum": "/de/impressum/",
    "/pages/datenschutz": "/de/datenschutz/",
    "/pages/agb": "/de/agb/",
    "/pages/ankauf": "/de/#sell",
    "/pages/geschaftskunde-werden": "/de/",
    "/collections/all": "/de/reparatur/",
    "/cart": "/de/",
    "/account": "/de/",
    "/search": "/de/",
}


def _map() -> dict[str, str]:
    m = cache.get("redirect-map")
    if m is None:
        m = dict(Redirect.objects.filter(active=True).values_list("old_path", "new_path"))
        cache.set("redirect-map", m, 300)
    return m


def _model_for_handle(handle: str) -> str | None:
    """Best effort: a Shopify product handle like 'iphone-13-display-reparatur' -> that model's page."""
    from catalog.models import DeviceModel

    words = [w for w in re.split(r"[^a-z0-9]+", handle.lower()) if w]
    if not words:
        return None
    best, best_len = None, 0
    for slug, brand_slug in DeviceModel.objects.filter(active=True).values_list("slug", "brand__slug"):
        name_part = slug[len(brand_slug) + 1:] if slug.startswith(brand_slug + "-") else slug
        cand = name_part.split("-")
        n = len(cand)
        for i in range(len(words) - n + 1):
            if words[i:i + n] == cand and len(name_part) > best_len:
                best, best_len = slug, len(name_part)
    return best


def resolve_legacy(path: str) -> str | None:
    p = normalise_path(path)
    m = _map()
    if p in m:
        return m[p]
    if p in DEFAULTS:
        return DEFAULTS[p]
    if p.startswith("/products/"):
        slug = _model_for_handle(p.split("/", 2)[2])
        return f"/de/reparatur/{slug}/" if slug else "/de/reparatur/"
    if p.startswith("/collections/"):
        return "/de/reparatur/"
    if p.startswith(("/pages/", "/blogs/", "/policies/", "/account", "/cart", "/search")):
        return "/de/"
    return None
