from django.contrib import admin, messages

from core.roles import RoleAdminMixin

from .models import Holiday, OpeningHours, Shop, SpecialHours

CONTENT = {"view": ["Owner", "Manager"], "add": ["Owner", "Manager"], "change": ["Owner", "Manager"],
           "delete": ["Owner", "Manager"]}


class HoursInline(admin.TabularInline):
    model = OpeningHours
    extra = 0
    verbose_name_plural = "Öffnungszeiten (pro Wochentag eine Zeile; zwei Zeilen für eine Mittagspause; ohne Zeile = geschlossen)"


@admin.register(Shop)
class ShopAdmin(RoleAdminMixin, admin.ModelAdmin):
    list_display = ["area", "street", "phone_display", "rating", "rating_count", "rating_fetched_at", "active"]
    inlines = [HoursInline]
    readonly_fields = ["rating", "rating_count", "rating_fetched_at", "rating_error"]
    fieldsets = [
        (None, {"fields": [("area", "short"), "street", ("postal_code", "city"), ("phone", "phone_display"), "email",
                           ("is_workshop", "is_mail_in"), ("order", "active"), "photo"]}),
        ("Google", {"fields": ["google_place_id", "google_name", "maps_query", ("rating", "rating_count"), "rating_fetched_at",
                               "rating_error", ("latitude", "longitude")]}),
        ("Google Sheets", {"fields": ["sheet_id"]}),
    ]
    autocomplete_fields = ["photo"]
    actions = ["fetch_ratings"]
    role_perms = {**CONTENT, "add": ["Owner"], "delete": []}

    @admin.action(description="Google-Bewertung jetzt abrufen")
    def fetch_ratings(self, request, queryset):
        from .tasks import fetch_rating

        for s in queryset:
            ok, msg = fetch_rating(s)
            if ok:
                messages.success(request, f"{s.short}: {msg}")
            else:
                messages.warning(request, f"{s.short}: {msg}")


@admin.register(SpecialHours)
class SpecialHoursAdmin(RoleAdminMixin, admin.ModelAdmin):
    list_display = ["date", "shop", "closed", "opens", "closes", "note_de"]
    list_filter = ["shop", "closed"]
    date_hierarchy = "date"
    role_perms = CONTENT


@admin.register(Holiday)
class HolidayAdmin(RoleAdminMixin, admin.ModelAdmin):
    list_display = ["date", "name_de", "closed"]
    list_editable = ["closed"]
    date_hierarchy = "date"
    role_perms = CONTENT
