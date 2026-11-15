"""Catalogue data for the site: one cached snapshot per site version, used by the price calculator JSON, the home
page stickers and the model pages. The rules are the prototype's (servicesFor, price, priceLabel, totalOf)."""
from decimal import Decimal

from core.cache import cached

from .models import (
    CabinetDrawer, Category, CategoryPrice, DeviceModel, FeaturedRepair, Price, RepairName, RepairOption, RepairType, Tier,
)

TIER_CODE = {Tier.PREMIUM: "p", Tier.ORIGINAL: "o", Tier.STANDARD: ""}


def _num(d: Decimal | None):
    if d is None:
        return None
    return int(d) if d == d.to_integral_value() else float(d)


def build() -> dict:
    cats = list(Category.objects.order_by("order"))
    reps = list(RepairType.objects.order_by("order"))
    names = {}
    for rn in RepairName.objects.select_related("category", "repair"):
        names.setdefault(rn.repair.key, {})[rn.category.key] = {"de": rn.name_de, "en": rn.name_en}
    rep = {}
    for r in reps:
        rep[r.key] = {
            "de": r.name_de, "en": r.name_en, "n": names.get(r.key, {}), "icon": r.icon or r.key,
            "img": r.image.key if r.image_id else None, "fix": r.fixed_price, "from": r.default_from, "tiers": r.has_tiers,
            "dur": r.duration_minutes, "war": r.warranty_months, "order": r.order,
            "dde": r.desc_de, "den": r.desc_en,
        }
    lists = {c.key: {} for c in cats}
    for o in RepairOption.objects.select_related("category", "repair").order_by("order"):
        lists[o.category.key].setdefault(o.console_type, []).append([o.repair.key, o.requires])
    top = {c.key: [] for c in cats}
    for f in FeaturedRepair.objects.select_related("category", "repair").order_by("order"):
        top[f.category.key].append(f.repair.key)
    base = {c.key: {} for c in cats}
    for cp in CategoryPrice.objects.select_related("category", "repair"):
        code = TIER_CODE[cp.tier]
        slot = base[cp.category.key]
        if code:
            slot.setdefault(cp.repair.key, {})[code] = _num(cp.amount)
        else:
            slot[cp.repair.key] = _num(cp.amount)

    models = []
    for m in DeviceModel.objects.filter(active=True).select_related("brand", "category").order_by(
        "category__order", "brand__order", "sort_order", "name"
    ):
        models.append({
            "id": m.id, "cat": m.category.key, "brand": m.brand.name, "name": m.name, "slug": m.slug, "fl": m.flags(),
            "de": m.full_name("de"), "en": m.full_name("en"), "nde": m.base_name("de"), "nen": m.base_name("en"),
            "ct": m.console_type, "year": m.release_year, "photo": m.photo.url if m.photo else None,
        })
    active_ids = {m["id"] for m in models}
    prices, froms = {}, {}
    for model_id, key, tier, amount, is_from in Price.objects.filter(model__active=True).values_list(
        "model_id", "repair__key", "tier", "amount", "is_from"
    ):
        if model_id not in active_ids:
            continue
        slot = prices.setdefault(model_id, {})
        code = TIER_CODE[tier]
        if code:
            cur = slot.get(key)
            if not isinstance(cur, dict):
                cur = slot[key] = {}
            cur[code] = _num(amount)
        else:
            slot[key] = _num(amount)
        if is_from:
            froms.setdefault(model_id, set()).add(key)

    drawers = [
        {"group": d.group, "label": d.label, "cat": d.category.key, "brand": d.brand.name,
         "logo": d.logo_file.url if d.logo_file else None}
        for d in CabinetDrawer.objects.filter(active=True).select_related("category", "brand").order_by("group", "order")
    ]
    return {
        "cats": [c.key for c in cats],
        "catn": {c.key: {"de": c.name_de, "en": c.name_en} for c in cats},
        "rep": rep, "lists": lists, "top": top, "base": base, "models": models,
        "prices": {str(k): v for k, v in prices.items()},
        "from": {str(k): sorted(v) for k, v in froms.items()},
        "drawers": drawers,
    }


def snapshot() -> dict:
    return cached("catalog", build)


# ---------- rules (same as the prototype) ----------

def services_for(snap: dict, m: dict | None, custom_cat: str | None = None) -> list[str]:
    """Repair keys for a model dict from the snapshot, or for an unlisted model of custom_cat."""
    cat = m["cat"] if m else custom_cat
    lists = snap["lists"].get(cat, {})
    if cat == "console":
        rows = lists.get(m["ct"] if m and m.get("ct") else "", [])
    else:
        rows = lists.get("", [])
    out = []
    for key, req in rows:
        if m and req == "face_id" and "F" not in m["fl"]:
            continue
        if m and req == "jack" and "J" not in m["fl"]:
            continue
        out.append(key)
    return out


def price(snap: dict, m: dict | None, key: str, tier: str = "p", cat: str | None = None):
    """Price for a repair on a model; tier is 'p' or 'o' for repairs with two parts. None means 'on request'."""
    cat = m["cat"] if m else cat
    if m:
        v = snap["prices"].get(str(m["id"]), {}).get(key)
        if v is not None:
            return v.get(tier) if isinstance(v, dict) else v
    r = snap["rep"].get(key)
    if r and r["fix"]:
        b = snap["base"].get(cat, {}).get(key)
        return b.get(tier) if isinstance(b, dict) else b
    return None


def is_from(snap: dict, m: dict | None, key: str) -> bool:
    if m and str(m["id"]) in snap["from"]:
        return key in snap["from"][str(m["id"])]
    if m and key in snap["prices"].get(str(m["id"]), {}):
        return False
    r = snap["rep"].get(key)
    return bool(r and r["from"])


def repair_name(snap: dict, key: str, cat: str, lang: str) -> str:
    r = snap["rep"][key]
    return (r["n"].get(cat) or r)[lang]


def min_price(snap: dict, cat: str, key: str):
    best = None
    for m in snap["models"]:
        if m["cat"] != cat or key not in services_for(snap, m):
            continue
        if snap["rep"][key]["tiers"]:
            vals = [x for x in (price(snap, m, key, "p"), price(snap, m, key, "o")) if x is not None]
            v = min(vals) if vals else None
        else:
            v = price(snap, m, key)
        if v is not None and (best is None or v < best):
            best = v
    return best


def model_by_slug(snap: dict, slug: str) -> dict | None:
    for m in snap["models"]:
        if m["slug"] == slug:
            return m
    return None


def fmt_eur(v, lang: str) -> str:
    """Whole euros like Intl.NumberFormat(…, {currency:'EUR', maximumFractionDigits:0}): '149 €' / '€149'."""
    if v is None:
        return ""
    n = round(float(v))
    s = f"{n:,}"
    if lang == "de":
        return s.replace(",", ".") + " €"
    return "€" + s
