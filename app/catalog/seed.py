"""Seed the catalogue from the approved prototype.

The data comes from app/seed/prototype.json, which seed/extract_prototype.js builds from prototype/index.html
(the catalogue part is prototype/src/js/engine.js, spliced in by assemble.py). Prices are the prototype's
placeholders, computed by the prototype's own price() so they match it exactly, until the client's price list is
imported with `manage.py import_prices`.

Running the seed again is safe: it updates names and lists, adds what is missing and never overwrites a price that
was imported or edited in the admin (unless reset_prices=True).
"""
import json
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.db import transaction
from simple_history.utils import bulk_create_with_history

from .models import (
    Brand, CabinetDrawer, Category, CategoryPrice, DeviceModel, FeaturedRepair, Price, PriceSource, RepairName,
    RepairOption, RepairType, Tier, slugify_de,
)

SEED_FILE = Path(settings.BASE_DIR) / "seed" / "prototype.json"
LOGO_DIR = Path(settings.REPO_DIR) / "prototype" / "img" / "brands"

# Brand -> logo file name in prototype/img/brands (see README.txt there). Valve has no own logo; its drawer uses steam.svg.
BRAND_LOGO_FILE = {
    "Apple": "apple", "Samsung": "samsung", "Google": "google", "Xiaomi": "xiaomi", "Huawei": "huawei",
    "OnePlus": "oneplus", "Oppo": "oppo", "Sony": "sony", "Motorola": "motorola", "Lenovo": "lenovo", "HP": "hp",
    "Dell": "dell", "ASUS": "asus", "Acer": "acer", "Microsoft": "microsoft", "MSI": "msi", "Nintendo": "nintendo",
}
# Drawers whose logo differs from the brand's own
DRAWER_OWN_LOGO = {"PlayStation": "playstation", "DualSense": "playstation", "Xbox": "xbox", "Steam Deck": "steam"}
CONSOLE_TYPES = "BbHP"


def load() -> dict:
    return json.loads(SEED_FILE.read_text(encoding="utf-8"))


def _logo_path(name: str) -> Path | None:
    for ext in ("svg", "png", "webp"):
        p = LOGO_DIR / f"{name}.{ext}"
        if p.is_file():
            return p
    return None


@transaction.atomic
def seed_catalog(reset_prices: bool = False, log=print) -> dict:
    d = load()
    T, SV, SV_CAT = d["T"], d["SV"], d["SV_CAT"]
    stats = {}

    # Categories
    cats = {}
    for i, key in enumerate(d["CATS"]):
        cats[key], _ = Category.objects.update_or_create(key=key, defaults=dict(
            name_de=T["de"][f"cat_{key}"], name_en=T["en"][f"cat_{key}"],
            subtitle_de=T["de"][f"cat_{key}_s"], subtitle_en=T["en"][f"cat_{key}_s"],
            tip_de=T["de"][f"tip_{key}"], tip_en=T["en"][f"tip_{key}"], order=i,
        ))
    stats["categories"] = len(cats)

    # Repair types, per-category names
    fixed, frm, K = set(d["FIXED"]), set(d["FROM"]), d["K"]
    icon_of = {"cport": "port"}
    reps = {}
    for i, (key, (en, de)) in enumerate(SV.items()):
        reps[key], _ = RepairType.objects.update_or_create(key=key, defaults=dict(
            name_de=de, name_en=en, icon=icon_of.get(key, key), has_tiers=(key == "display"), fixed_price=key in fixed,
            default_from=key in frm, price_weight=Decimal(str(K.get(key, 0.5))), order=i,
        ))
    for cat, m in SV_CAT.items():
        for key, (en, de) in m.items():
            RepairName.objects.update_or_create(repair=reps[key], category=cats[cat], defaults=dict(name_de=de, name_en=en))
    stats["repair_types"] = len(reps)

    # Which repairs each device gets (LISTS, CON). Console rows with no type are the list for unknown consoles (CON.X).
    RepairOption.objects.all().delete()
    for cat in ("phone", "tablet", "laptop"):
        for i, key in enumerate(d["LISTS"][cat]):
            req = "face_id" if key == "faceid" and cat == "phone" else "jack" if key == "jack" and cat == "phone" else ""
            RepairOption.objects.create(category=cats[cat], repair=reps[key], order=i, requires=req)
    for ctype, keys in d["CON"].items():
        for i, key in enumerate(keys):
            RepairOption.objects.create(category=cats["console"], console_type="" if ctype == "X" else ctype, repair=reps[key], order=i)

    FeaturedRepair.objects.all().delete()
    for cat, keys in d["TOP6"].items():
        for i, key in enumerate(keys):
            FeaturedRepair.objects.create(category=cats[cat], repair=reps[key], order=i)

    # Base prices (BASE)
    for cat, m in d["BASE"].items():
        for key, v in m.items():
            if isinstance(v, list):  # [original, premium]
                for tier, amount in ((Tier.ORIGINAL, v[0]), (Tier.PREMIUM, v[1])):
                    CategoryPrice.objects.update_or_create(category=cats[cat], repair=reps[key], tier=tier, defaults={"amount": amount})
            else:
                CategoryPrice.objects.update_or_create(category=cats[cat], repair=reps[key], tier=Tier.STANDARD, defaults={"amount": v})

    # Brands, in order of first appearance
    brands = {}
    order = 0
    for cat in d["CATS"]:
        for b in d["M"][cat]:
            if b not in brands:
                brands[b], created = Brand.objects.get_or_create(name=b, defaults={"slug": slugify_de(b), "order": order})
                order += 1
    logos = 0
    for name, brand in brands.items():
        f = BRAND_LOGO_FILE.get(name)
        p = _logo_path(f) if f else None
        if p and not brand.logo:
            with p.open("rb") as fh:
                brand.logo.save(p.name, File(fh), save=True)
            logos += 1
    stats["brands"] = len(brands)

    # Brand cabinet
    labels = {"br_phone": "phone", "br_laptop": "laptop", "br_console": "console"}
    for lab, items in d["BRANDWALL"]:
        for i, item in enumerate(items):
            label, cat, b = item[:3]
            own = DRAWER_OWN_LOGO.get(label)
            drawer, _ = CabinetDrawer.objects.update_or_create(group=labels[lab], label=label, defaults=dict(
                category=cats[cat], brand=brands[b], order=i, use_brand_logo=own is None,
            ))
            p = _logo_path(own) if own else None
            if p and not drawer.logo:
                with p.open("rb") as fh:
                    drawer.logo.save(p.name, File(fh), save=True)
                logos += 1
    stats["logos_attached"] = logos

    # Device models, newest first as in the prototype lists
    real_ids = set(d["REAL"])
    models = []
    for cat in d["CATS"]:
        for b, entries in d["M"][cat].items():
            for i, e in enumerate(entries.split("|")):
                name, f, fl = e.split(":")
                ctype = next((c for c in fl if c in CONSOLE_TYPES), "")
                dm = DeviceModel.objects.filter(category=cats[cat], brand=brands[b], name=name).first() or DeviceModel(
                    category=cats[cat], brand=brands[b], name=name
                )
                dm.price_factor = Decimal(f)
                dm.popular = "p" in fl
                dm.has_face_id = "F" in fl
                dm.has_headphone_jack = "J" in fl
                dm.console_type = ctype
                dm.sort_order = i * 10
                dm.legacy_key = slugify_de(f"{cat}-{b}-{name}")
                dm.save(keep_factor=True)
                models.append(dm)
    stats["models"] = len(models)

    # Placeholder prices exactly as the prototype computed them
    created = 0
    by_entry = {(p["cat"], p["brand"], p["name"]): p for p in d["PRICES"]}
    if reset_prices:
        Price.objects.all().delete()
    existing = set(Price.objects.values_list("model_id", "repair_id", "tier"))
    new = []
    for dm in models:
        p = by_entry[(dm.category.key, dm.brand.name, dm.name)]
        source = PriceSource.WEBSITE if p["id"] in real_ids else PriceSource.PLACEHOLDER
        for key, v in p["prices"].items():
            rep = reps[key]
            if rep.fixed_price:
                continue  # comes from the category base price
            rows = [(Tier.PREMIUM, v[0]), (Tier.ORIGINAL, v[1])] if isinstance(v, list) else [(Tier.STANDARD, v)]
            for tier, amount in rows:
                if amount is None or (dm.id, rep.id, tier) in existing:
                    continue
                new.append(Price(model=dm, repair=rep, tier=tier, amount=amount, is_from=rep.default_from, source=source))
    bulk_create_with_history(new, Price, batch_size=500, default_change_reason="Startdaten aus dem Prototyp")
    created += len(new)
    stats["prices_created"] = created
    stats["prices_total"] = Price.objects.count()
    log(", ".join(f"{k}: {v}" for k, v in stats.items()))
    return stats
