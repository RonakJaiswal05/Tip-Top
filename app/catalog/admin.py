"""Catalogue admin: prices (A3), devices (A4), repair types (A5), brands and the brand cabinet."""
from django import forms
from django.contrib import admin, messages
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import path, reverse
from django.utils.html import format_html
from simple_history.admin import SimpleHistoryAdmin

from core.roles import RoleAdminMixin

from .models import (
    LEVEL_FACTORS, Brand, BuybackPrice, CabinetDrawer, Category, CategoryPrice, DeviceModel, FeaturedRepair, Price, PriceLevel,
    PriceSource, RepairName, RepairOption, RepairType, ScheduledPriceChange, Tier, starting_price,
)

CATALOG = {"view": ["Owner", "Manager"], "add": ["Owner", "Manager"], "change": ["Owner", "Manager"], "delete": ["Owner", "Manager"]}
CATALOG_VIEW_DESK = {**CATALOG, "view": ["Owner", "Manager", "Front desk"]}


class FeaturedInline(admin.TabularInline):
    model = FeaturedRepair
    extra = 0
    verbose_name = "Große Fotokarte"
    verbose_name_plural = "Große Fotokarten im Rechner (für Smartphones auch auf der Startseite), in dieser Reihenfolge"


@admin.register(Category)
class CategoryAdmin(RoleAdminMixin, admin.ModelAdmin):
    list_display = ["name_de", "name_en", "key", "order"]
    inlines = [FeaturedInline]
    readonly_fields = ["key"]
    role_perms = {**CATALOG, "add": [], "delete": []}

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Brand)
class BrandAdmin(RoleAdminMixin, admin.ModelAdmin):
    list_display = ["logo_preview", "name", "slug", "order", "active", "n_models"]
    list_display_links = ["name"]
    list_editable = ["order", "active"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ["name"]}
    role_perms = CATALOG

    @admin.display(description="Logo")
    def logo_preview(self, b):
        return format_html('<img src="{}" alt="" style="height:22px;max-width:90px">', b.logo.url) if b.logo else "–"

    @admin.display(description="Modelle")
    def n_models(self, b):
        return b.models.filter(active=True).count()


@admin.register(CabinetDrawer)
class CabinetDrawerAdmin(RoleAdminMixin, admin.ModelAdmin):
    list_display = ["label", "group", "category", "brand", "has_logo", "order", "active"]
    list_editable = ["order", "active"]
    list_filter = ["group"]
    role_perms = CATALOG

    @admin.display(description="Logo", boolean=True)
    def has_logo(self, d):
        return bool(d.logo_file)


class RepairNameInline(admin.TabularInline):
    model = RepairName
    extra = 0
    verbose_name_plural = "Andere Namen je Kategorie (z. B. „Ladebuchse / DC-Buchse“ für Laptops)"


@admin.register(RepairType)
class RepairTypeAdmin(RoleAdminMixin, admin.ModelAdmin):
    list_display = ["name_de", "name_en", "key", "order", "duration_minutes", "warranty_months", "has_tiers", "fixed_price", "default_from"]
    list_editable = ["order", "duration_minutes", "warranty_months"]
    search_fields = ["key", "name_de", "name_en"]
    readonly_fields = ["key"]
    autocomplete_fields = ["image"]
    inlines = [RepairNameInline]
    fieldsets = [
        (None, {"fields": ["key", ("name_de", "name_en"), ("desc_de", "desc_en"), ("icon", "image"), "order"]}),
        ("Ablauf", {"fields": [("duration_minutes", "warranty_months")]}),
        ("Preise", {"fields": ["has_tiers", "fixed_price", "default_from", "price_weight"]}),
    ]
    role_perms = {**CATALOG, "add": [], "delete": []}

    def has_add_permission(self, request):
        return False  # the 30 repairs are wired into the calculator; rename or reorder them instead

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(RepairOption)
class RepairOptionAdmin(RoleAdminMixin, admin.ModelAdmin):
    list_display = ["repair", "category", "console_type", "order", "requires"]
    list_editable = ["order", "requires"]
    list_filter = ["category", "console_type"]
    role_perms = CATALOG


class PriceLevelForm(forms.ModelForm):
    class Meta:
        model = DeviceModel
        fields = "__all__"
        help_texts = {
            "price_level": "Beim Anlegen werden daraus Startpreise für jede Reparatur berechnet. Danach in der Preisübersicht anpassen.",
        }

    def clean(self):
        data = super().clean()
        cat = data.get("category")
        if cat and cat.key == "console" and not data.get("console_type"):
            self.add_error("console_type", "Bitte den Konsolentyp wählen, er bestimmt die Reparaturen.")
        if not self.instance.pk and not data.get("price_level"):
            self.add_error("price_level", "Bitte eine Preisstufe wählen, damit Startpreise angelegt werden.")
        return data


def create_starting_prices(model: DeviceModel) -> int:
    """Starting prices for a new model from its category's base prices and the price level (the prototype's formula)."""
    opts = RepairOption.objects.filter(category=model.category)
    if model.category.key == "console":
        opts = opts.filter(console_type=model.console_type)
    else:
        opts = opts.filter(console_type="")
    keys = {o.repair_id for o in opts}
    base = CategoryPrice.objects.filter(category=model.category, repair_id__in=keys).select_related("repair")
    made = 0
    for cp in base:
        if cp.repair.fixed_price:
            continue
        amount = starting_price(float(cp.amount), float(model.price_factor), float(cp.repair.price_weight))
        _, created = Price.objects.get_or_create(
            model=model, repair=cp.repair, tier=cp.tier,
            defaults={"amount": amount, "is_from": cp.repair.default_from, "source": PriceSource.LEVEL},
        )
        made += created
    return made


@admin.register(DeviceModel)
class DeviceModelAdmin(RoleAdminMixin, admin.ModelAdmin):
    form = PriceLevelForm
    list_display = ["__str__", "category", "brand", "release_year", "popular", "active", "n_prices", "edit_prices", "page"]
    list_filter = ["category", "brand", "active", "popular", "console_type"]
    list_editable = ["popular", "active"]
    search_fields = ["name", "brand__name", "slug"]
    autocomplete_fields = ["brand"]
    readonly_fields = ["slug", "price_factor", "merged_into"]
    actions = ["deactivate", "activate", "merge"]
    fieldsets = [
        (None, {"fields": ["category", "brand", "name", "release_year", "photo"]}),
        ("Preise", {"fields": ["price_level", "price_factor"]}),
        ("Was die Reparaturliste beeinflusst", {"fields": [("has_face_id", "has_headphone_jack"), "console_type"]}),
        ("Anzeige", {"fields": ["popular", "active", "sort_order", "slug", "merged_into"]}),
    ]
    role_perms = {**CATALOG_VIEW_DESK, "delete": ["Owner"]}

    def get_changeform_initial_data(self, request):
        return {"sort_order": -10, "price_level": PriceLevel.STANDARD}

    def save_model(self, request, obj, form, change):
        if not change and obj.price_level:
            obj.price_factor = LEVEL_FACTORS[obj.price_level]
        super().save_model(request, obj, form, change)
        if not change:
            n = create_starting_prices(obj)
            messages.success(request, f"{n} Startpreise angelegt. Das Modell ist jetzt im Rechner buchbar und hat eine eigene Modellseite.")

    @admin.display(description="Preise")
    def n_prices(self, m):
        return m.prices.count()

    @admin.display(description="")
    def edit_prices(self, m):
        return format_html('<a href="{}?model={}">Preise bearbeiten</a>', reverse("admin:catalog_price_editor"), m.pk)

    @admin.display(description="Seite")
    def page(self, m):
        return format_html('<a href="/de/reparatur/{}/" target="_blank">ansehen</a>', m.slug) if m.active else "–"

    @admin.action(description="Ausblenden (nicht mehr reparieren, Historie bleibt)")
    def deactivate(self, request, queryset):
        n = queryset.update(active=False)
        from core.cache import bump

        bump()
        messages.success(request, f"{n} Modelle ausgeblendet.")

    @admin.action(description="Wieder einblenden")
    def activate(self, request, queryset):
        n = queryset.update(active=True)
        from core.cache import bump

        bump()
        messages.success(request, f"{n} Modelle eingeblendet.")

    @admin.action(description="Doppelte zusammenführen …")
    def merge(self, request, queryset):
        if "target" in request.POST:
            target = DeviceModel.objects.filter(pk=request.POST["target"]).first()
            if not target:
                messages.error(request, "Bitte ein Ziel wählen.")
                return None
            with transaction.atomic():
                from leads.models import Request

                for m in queryset.exclude(pk=target.pk):
                    Request.objects.filter(device_model=m).update(device_model=target)
                    for p in m.prices.all():
                        if not Price.objects.filter(model=target, repair=p.repair, tier=p.tier).exists():
                            p.model = target
                            p._change_reason = f"Zusammengeführt aus {m}"
                            p.save()
                    m.active = False
                    m.merged_into = target
                    m.save()
            messages.success(request, f"Zusammengeführt in {target}. Die doppelten Einträge sind ausgeblendet, ihre Anfragen zeigen auf {target}.")
            return None
        candidates = DeviceModel.objects.filter(category__in=queryset.values("category")).order_by("brand__name", "name")
        return render(request, "admin/catalog/merge.html", {
            "items": queryset, "candidates": candidates, "title": "Doppelte Modelle zusammenführen",
            "opts": self.model._meta, "action": "merge",
        })


@admin.register(CategoryPrice)
class CategoryPriceAdmin(RoleAdminMixin, SimpleHistoryAdmin):
    list_display = ["category", "repair", "tier", "amount"]
    list_editable = ["amount"]
    list_filter = ["category", "repair__fixed_price"]
    role_perms = CATALOG


class PriceSourceFilter(admin.SimpleListFilter):
    title = "Herkunft"
    parameter_name = "herkunft"

    def lookups(self, request, model_admin):
        return PriceSource.choices

    def queryset(self, request, qs):
        return qs.filter(source=self.value()) if self.value() else qs


@admin.register(Price)
class PriceAdmin(RoleAdminMixin, SimpleHistoryAdmin):
    """List and history of every price. Editing happens in the price editor (one table per model)."""

    list_display = ["model", "repair", "tier", "amount", "is_from", "source", "updated_at"]
    list_filter = ["model__category", "repair", "tier", PriceSourceFilter, "model__brand"]
    search_fields = ["model__name", "model__brand__name", "repair__name_de"]
    autocomplete_fields = ["model"]
    history_list_display = ["amount", "is_from", "source"]
    change_list_template = "admin/catalog/price/change_list.html"
    role_perms = CATALOG

    def get_urls(self):
        from . import admin_views as v

        w = self.admin_site.admin_view
        return [
            path("editor/", w(v.price_editor), name="catalog_price_editor"),
            path("bulk/", w(v.bulk_change), name="catalog_price_bulk"),
            path("copy/", w(v.copy_prices), name="catalog_price_copy"),
            path("import/", w(v.import_view), name="catalog_price_import"),
            path("export/", w(v.export_view), name="catalog_price_export"),
        ] + super().get_urls()


@admin.register(ScheduledPriceChange)
class ScheduledPriceChangeAdmin(RoleAdminMixin, admin.ModelAdmin):
    list_display = ["model", "repair", "tier", "amount", "effective_at", "applied_at", "created_by"]
    list_filter = ["applied_at", "repair"]
    autocomplete_fields = ["model"]
    search_fields = ["model__name"]
    role_perms = CATALOG

    def save_model(self, request, obj, form, change):
        if not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(BuybackPrice)
class BuybackPriceAdmin(RoleAdminMixin, admin.ModelAdmin):
    list_display = ["model", "condition", "low", "high"]
    list_filter = ["model__category", "condition"]
    autocomplete_fields = ["model"]
    search_fields = ["model__name"]
    role_perms = {**CATALOG, "view": ["Owner", "Manager", "Front desk"]}
