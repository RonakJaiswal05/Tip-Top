"""Catalogue data for the site: one cached snapshot per site version, used by the price calculator JSON, the home
page stickers and the model pages. The rules are the prototype's (servicesFor, price, priceLabel, totalOf)."""
from decimal import Decimal
from pathlib import Path

from core.cache import cached

from .models import (
    BuybackPrice, CabinetDrawer, Category, CategoryPrice, DeviceModel, FeaturedRepair, Price, RepairName, RepairOption, RepairType, Tier,
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
    excluded, extra = {}, {}
    for model_id, key in DeviceModel.excluded_repairs.through.objects.values_list("devicemodel_id", "repairtype__key"):
        excluded.setdefault(model_id, []).append(key)
    for model_id, key, order in DeviceModel.extra_repairs.through.objects.values_list(
        "devicemodel_id", "repairtype__key", "repairtype__order"
    ).order_by("repairtype__order"):
        extra.setdefault(model_id, []).append(key)
    for m in DeviceModel.objects.filter(active=True).select_related("brand", "category").order_by(
        "category__order", "brand__order", "sort_order", "name"
    ):
        row = {
            "id": m.id, "cat": m.category.key, "brand": m.brand.name, "name": m.name, "slug": m.slug, "fl": m.flags(),
            "de": m.full_name("de"), "en": m.full_name("en"), "nde": m.base_name("de"), "nen": m.base_name("en"),
            "ct": m.console_type, "year": m.release_year, "photo": m.photo.url if m.photo else None,
        }
        if m.id in excluded:
            row["no"] = sorted(excluded[m.id])
        if m.id in extra:
            row["add"] = extra[m.id]  # repairs this model gets on top of its category's list (admin: "Zusätzlich")
        models.append(row)
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

    buy = {}
    for model_id, cond, low, high in BuybackPrice.objects.filter(model__active=True).values_list("model_id", "condition", "low", "high"):
        buy.setdefault(str(model_id), {})[cond] = [_num(low), _num(high)]

    drawers = [drawer_row(d) for d in CabinetDrawer.objects.filter(active=True).select_related("category", "brand").order_by("group", "order")]
    return {
        "cats": [c.key for c in cats],
        "catn": {c.key: {"de": c.name_de, "en": c.name_en} for c in cats},
        "rep": rep, "lists": lists, "top": top, "base": base, "models": models,
        "prices": {str(k): v for k, v in prices.items()},
        "from": {str(k): sorted(v) for k, v in froms.items()},
        "drawers": drawers,
        "buy": buy,
        "rimg": repair_photos(),
    }


# Repair photos per device type (client, 17 and 25 Nov 2026): the iPhone set only for Apple phones, the Android set for
# every other phone, own sets for tablets, laptops and consoles. A photo shows once its media asset exists and is
# published (Inhalte > Medien, same key); until then the card is a tile in the device colour.
REPAIR_PHOTO_KEYS = {
    "phone_apple": {"display": "rep-display", "battery": "rep-battery", "port": "rep-port", "back": "rep-back",
                    "camera": "rep-camera", "water": "rep-water"},
    "phone": {"display": "and-display", "battery": "and-battery", "port": "and-port", "back": "and-back",
              "camera": "and-camera", "water": "and-water"},
    "tablet": {"display": "tab-display", "battery": "tab-battery", "port": "tab-port", "back": "tab-back",
               "camera": "tab-camera", "water": "tab-water"},
    "laptop": {"display": "lap-display", "battery": "lap-battery", "keyboard": "lap-keyboard", "port": "lap-port",
               "fan": "lap-fan", "water": "lap-water"},
    "console": {"hdmi": "con-hdmi", "fan": "con-fan", "tmr": "con-drift", "display": "con-display",
                "drive": "con-drive", "psu": "con-psu"},
}


def repair_photos() -> dict:
    from content.models import MediaAsset

    have = set(MediaAsset.objects.filter(published=True).exclude(image="").values_list("key", flat=True))
    return {group: {k: v for k, v in m.items() if v in have} for group, m in REPAIR_PHOTO_KEYS.items()}


def repair_photo(snap: dict, cat: str, brand: str, key: str) -> str | None:
    group = "phone_apple" if cat == "phone" and brand == "Apple" else cat
    return snap.get("rimg", {}).get(group, {}).get(key)


def drawer_row(d: CabinetDrawer) -> dict:
    """A brand cabinet drawer. Wordmark logos already spell the brand, so the label drops the repeated brand word
    ("Sony Xperia" -> [SONY] Xperia, "Samsung" -> logo only), as in the prototype's drwLabel()."""
    f = d.logo_file
    own = bool(d.logo)
    wm = bool(f) and not own and d.brand.logo_is_wordmark
    text = d.label
    if wm and text.lower().startswith(d.brand.name.lower()):
        text = text[len(d.brand.name):].strip()
    lg = (Path(f.name).stem.split("_")[0].lower() if own else d.brand.slug) if f else ""
    return {"group": d.group, "label": d.label, "text": text, "cat": d.category.key, "brand": d.brand.name,
            "logo": f.url if f else None, "wm": wm, "lg": lg}


def snapshot() -> dict:
    return cached("catalog", build)


# ---------- rules (same as the prototype) ----------

def model_repairs(model: DeviceModel, with_diagnosis: bool = True) -> list[RepairType]:
    """Repairs a saved model gets (database version of services_for): its category's list, the console type's list
    for consoles, Face ID / headphone jack only where fitted, plus the diagnosis."""
    opts = RepairOption.objects.filter(category=model.category).select_related("repair").order_by("order")
    opts = opts.filter(console_type=model.console_type if model.category.key == "console" else "")
    excluded = set(model.excluded_repairs.values_list("key", flat=True)) if model.pk else set()
    out = []
    for o in opts:
        if not _fits(o.requires, model.has_face_id, model.has_touch_id, model.has_headphone_jack):
            continue
        if o.repair.key in excluded:
            continue
        out.append(o.repair)
    if model.pk:
        have = {r.key for r in out}
        out += [r for r in model.extra_repairs.order_by("order") if r.key not in have and r.key != "diagnosis"]
    if with_diagnosis and all(r.key != "diagnosis" for r in out):
        d = RepairType.objects.filter(key="diagnosis").first()
        if d:
            out.append(d)
    return out


def services_for(snap: dict, m: dict | None, custom_cat: str | None = None) -> list[str]:
    """Repair keys for a model dict from the snapshot, or for an unlisted model of custom_cat."""
    cat = m["cat"] if m else custom_cat
    lists = snap["lists"].get(cat, {})
    if cat == "console":
        rows = lists.get(m["ct"] if m and m.get("ct") else "", [])
    else:
        rows = lists.get("", [])
    no = set(m.get("no", ())) if m else set()
    out = []
    for key, req in rows:
        if m and not _fits(req, "F" in m["fl"], "T" in m["fl"], "J" in m["fl"]):
            continue
        if key in no:
            continue
        out.append(key)
    if m:
        out += [k for k in m.get("add", ()) if k not in out and k in snap["rep"]]
    return out


def _fits(requires: str, face_id: bool, touch_id: bool, jack: bool) -> bool:
    """A repair with a condition only shows on models that have the feature (admin switches on the model)."""
    return not ((requires == "face_id" and not face_id) or (requires == "touch_id" and not touch_id)
                or (requires == "jack" and not jack))


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
