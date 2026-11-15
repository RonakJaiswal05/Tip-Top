"""Where old Shopify addresses go (SOW section 10: "Redirects from every current Shopify URL to its new page").

seed/shopify_redirects.csv holds every URL from the old sitemap (fetched 15 Nov 2026) with its target; `manage.py
seed_redirects` loads it into the Redirect table, where the team can change any rule in the admin. Addresses that are
not in the table (e.g. new links Google finds later) are mapped on the fly by best_target().
"""
import re

from django.core.cache import cache

from .models import Redirect, normalise_path

PAGES = {
    "kontakt": "/de/#shops", "reparaturablauf": "/de/#shops", "uber-uns": "/de/#workshop", "faq": "/de/#faq",
    "pushdaddy-faq-1": "/de/#faq", "geschaftskunde-werden": "/de/", "geschaftskunden-login": "/de/", "impressum": "/de/impressum/",
    "datenschutz": "/de/datenschutz/", "agb": "/de/agb/", "widerruf": "/de/widerruf/", "ankauf": "/de/#sell",
    "netzteile-und-netzstecker": "/de/", "weiteres-zubehor": "/de/", "zubehor": "/de/", "test-1": "/de/", "testing": "/de/",
}
POLICIES = {
    "legal-notice": "/de/impressum/", "privacy-policy": "/de/datenschutz/", "terms-of-service": "/de/agb/",
    "refund-policy": "/de/widerruf/", "shipping-policy": "/de/agb/", "contact-information": "/de/impressum/",
}
# brand words in old handles -> (category, brand slug) anchor on the model index
BRANDS = [
    (("macbook",), "laptop", "apple"), (("ipad",), "tablet", "apple"), (("iphone", "apple"), "phone", "apple"),
    (("galaxy-tab", "tab"), "tablet", "samsung"), (("samsung", "galaxy"), "phone", "samsung"),
    (("pixel", "google", "nexus"), "phone", "google"), (("xiaomi", "redmi", "poco"), "phone", "xiaomi"),
    (("matebook",), "laptop", "huawei"), (("matepad", "mediapad"), "tablet", "huawei"), (("huawei", "mate", "p-serie", "y-serie"), "phone", "huawei"),
    (("oneplus",), "phone", "oneplus"), (("oppo",), "phone", "oppo"), (("xperia", "sony"), "phone", "sony"),
    (("motorola", "moto"), "phone", "motorola"), (("playstation", "ps4", "ps5", "dualshock", "dualsense"), "console", "sony"),
    (("xbox",), "console", "microsoft"), (("switch", "nintendo", "joy-con"), "console", "nintendo"),
    (("thinkpad", "lenovo"), "laptop", "lenovo"), (("surface",), "laptop", "microsoft"),
]
OLD_BRANDS_WITHOUT_MODELS = ("htc", "lg", "nokia", "lumia", "blackberry", "wiko", "alcatel", "zte", "one-serie", "smartphone",
                             "weitere-hersteller", "weitere-htc", "weitere-sony")


def _map() -> dict[str, str]:
    m = cache.get("redirect-map")
    if m is None:
        m = dict(Redirect.objects.filter(active=True).values_list("old_path", "new_path"))
        cache.set("redirect-map", m, 300)
    return m


def _models():
    from catalog.models import DeviceModel

    out = []
    for slug, brand_slug, cat, name in DeviceModel.objects.filter(active=True).values_list("slug", "brand__slug", "category__key", "name"):
        name_part = slug[len(brand_slug) + 1:] if slug.startswith(brand_slug + "-") else slug
        cands = {name_part}
        if brand_slug == "samsung" and name_part.startswith("galaxy-"):
            cands.add(name_part[len("galaxy-"):])  # old handles say "samsung-s23", not "galaxy-s23"
        for c in cands:
            out.append((c.split("-"), slug, cat, brand_slug))
    return out


# words in an old handle that name a brand (the handle must name the model's brand, so "macbook-air-13" never
# becomes "OnePlus 13" and "samsung-a80" never "Oppo A80")
BRAND_WORDS = {
    "apple": ("apple", "iphone", "ipad", "macbook"), "samsung": ("samsung", "galaxy"), "google": ("google", "pixel"),
    "xiaomi": ("xiaomi", "redmi", "poco"), "huawei": ("huawei", "mate", "matepad", "matebook"), "oneplus": ("oneplus", "nord"),
    "oppo": ("oppo", "reno", "find"), "sony": ("sony", "xperia", "playstation", "ps4", "ps5", "dualsense", "dualshock"),
    "motorola": ("motorola", "moto"), "microsoft": ("microsoft", "surface", "xbox"), "nintendo": ("nintendo", "switch", "joy"),
    "lenovo": ("lenovo", "thinkpad", "ideapad", "yoga", "legion"), "hp": ("hp", "elitebook", "pavilion", "envy", "omen"),
    "dell": ("dell", "xps", "latitude", "inspiron"), "asus": ("asus", "zenbook", "vivobook", "rog"), "acer": ("acer", "aspire", "swift", "nitro"),
    "msi": ("msi",), "valve": ("steam",),
}
VARIANTS = {"lite", "pro", "plus", "max", "mini", "ultra", "fe", "edge", "neo", "compact", "premium", "air", "xl", "s", "e", "5g", "c", "t"}


def model_for_handle(handle: str, models=None) -> str | None:
    """'iphone-13-reparatur-akku' -> 'apple-iphone-13' (longest whole-word match of the same brand)."""
    words = [w for w in re.split(r"[^a-z0-9]+", handle.lower()) if w]
    brands = {b for b, ws in BRAND_WORDS.items() if any(w in words for w in ws)}
    if not brands:
        return None
    best, best_len = None, 0
    for cand, slug, _cat, brand in (models or _models()):
        if brand not in brands:
            continue
        n = len(cand)
        for i in range(len(words) - n + 1):
            if words[i:i + n] != cand:
                continue
            nxt = words[i + n] if i + n < len(words) else ""
            if nxt in VARIANTS:  # "p30-lite" is not the P30
                continue
            if len("-".join(cand)) > best_len:
                best, best_len = slug, len("-".join(cand))
    return best


def index_anchor(handle: str) -> str:
    """No matching model: the brand's section of the model index, or the phone section for brands no longer listed."""
    h = handle.lower()
    for words, cat, brand in BRANDS:
        if any(re.search(rf"(^|-){re.escape(w)}(-|$)", h) or h.startswith(w) for w in words):
            return f"/de/reparatur/#{cat}-{brand}"
    if any(h.startswith(b) or f"-{b}-" in f"-{h}-" for b in OLD_BRANDS_WITHOUT_MODELS):
        return "/de/reparatur/#phone"
    return "/de/reparatur/"


def best_target(path: str, models=None) -> str | None:
    p = normalise_path(path)
    parts = p.strip("/").split("/")
    if not parts or not parts[0]:
        return None
    kind = parts[0]
    handle = parts[1] if len(parts) > 1 else ""
    if kind == "policies":
        return POLICIES.get(handle, "/de/impressum/")
    if kind == "pages":
        if handle in PAGES:
            return PAGES[handle]
        slug = model_for_handle(handle, models)
        return f"/de/reparatur/{slug}/" if slug else index_anchor(handle)
    if kind in ("products", "collections"):
        if handle in ("b2b-geschaftskunden", "geschaftskunde-werden"):
            return "/de/"
        if handle in ("all", "best-selling-collection", "best-selling-products", "frontpage"):
            return "/de/reparatur/"
        if "datenrettung" in handle or "data-recovery" in handle:
            slug = model_for_handle(handle, models)
            return f"/de/reparatur/{slug}/" if slug else "/de/#workshop"
        slug = model_for_handle(handle, models)
        return f"/de/reparatur/{slug}/" if slug else index_anchor(handle)
    if kind in ("blogs", "cart", "account", "search", "checkout", "orders"):
        return "/de/"
    return None


def resolve_legacy(path: str) -> str | None:
    p = normalise_path(path)
    return _map().get(p) or best_target(p)
