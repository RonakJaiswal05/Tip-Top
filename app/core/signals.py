"""Bump the site version whenever something the public pages show is saved (see core.cache)."""
from django.apps import apps
from django.db.models.signals import post_delete, post_save

from .cache import bump

# app_label.ModelName of everything that is rendered on public pages
PUBLIC_MODELS = [
    "core.SiteSettings",
    "catalog.Category", "catalog.Brand", "catalog.DeviceModel", "catalog.RepairType", "catalog.RepairName",
    "catalog.RepairOption", "catalog.FeaturedRepair", "catalog.Price", "catalog.CategoryPrice", "catalog.BuybackPrice",
    "shops.Shop", "shops.OpeningHours", "shops.SpecialHours", "shops.Holiday",
    "content.ContentBlock", "content.FAQ", "content.MediaAsset", "content.BeforeAfter", "content.WorkshopCard",
    "legal.LegalPage", "legal.LegalPageVersion",
]


def connect_all():
    for label in PUBLIC_MODELS:
        try:
            model = apps.get_model(label)
        except LookupError:
            continue
        post_save.connect(bump, sender=model, dispatch_uid=f"bump-save-{label}")
        post_delete.connect(bump, sender=model, dispatch_uid=f"bump-del-{label}")
