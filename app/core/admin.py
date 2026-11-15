"""Settings (A11), redirects, users and roles (A1), audit log (A12)."""
from auditlog.registry import auditlog
from django.apps import apps
from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group, User
from django.shortcuts import redirect

from .models import Redirect, SiteSettings
from .roles import ROLE_LABELS, RoleAdminMixin, user_in


@admin.register(SiteSettings)
class SiteSettingsAdmin(RoleAdminMixin, admin.ModelAdmin):
    fieldsets = [
        ("Kontakt", {"fields": ["whatsapp_number", ("phone", "phone_display"), "contact_email", "instagram_url", "b2b_url"]}),
        ("Benachrichtigungen", {"fields": ["notify_emails", "summary_emails"]}),
        ("Google Sheets", {"fields": ["sheets_enabled", "google_sheet_id", "google_sheet_tab"]}),
        ("Statistik und Werbung (Cookie-Banner)", {"fields": ["analytics_enabled", ("matomo_url", "matomo_site_id"), "ads_enabled",
                                                              ("google_ads_id", "meta_pixel_id"), "consent_version"]}),
        ("Website", {"fields": ["prices_are_placeholders", "maintenance_mode", "maintenance_text_de", "maintenance_text_en"]}),
    ]
    readonly_fields = ["consent_version"]
    role_perms = {"view": ["Owner"], "change": ["Owner"], "add": [], "delete": []}

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = SiteSettings.load()
        return redirect("admin:core_sitesettings_change", obj.pk)


@admin.register(Redirect)
class RedirectAdmin(RoleAdminMixin, admin.ModelAdmin):
    list_display = ["old_path", "new_path", "note", "active"]
    list_editable = ["active"]
    search_fields = ["old_path", "new_path"]
    role_perms = {"view": ["Owner", "Manager"], "change": ["Owner", "Manager"], "add": ["Owner", "Manager"], "delete": ["Owner", "Manager"]}


admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class StaffUserAdmin(RoleAdminMixin, UserAdmin):
    """Owner manages accounts. Switching 'Aktiv' off signs a person out immediately (A1)."""

    list_display = ["username", "first_name", "last_name", "email", "roles", "is_active", "two_factor", "last_login"]
    list_filter = ["is_active", "groups"]
    fieldsets = [
        (None, {"fields": ["username", "password"]}),
        ("Person", {"fields": [("first_name", "last_name"), "email"]}),
        ("Rolle und Zugang", {"fields": ["is_active", "is_staff", "groups"],
                              "description": "Rolle wählen: Owner (Inhaber), Manager (Filialleitung), Front desk (Empfang) oder "
                                             "Technician (Technik). „Mitarbeiter-Status“ muss an sein, damit die Person sich anmelden kann."}),
        ("Verlauf", {"fields": ["last_login", "date_joined"]}),
    ]
    readonly_fields = ["last_login", "date_joined"]
    role_perms = {"view": ["Owner"], "change": ["Owner"], "add": ["Owner"], "delete": ["Owner"]}
    actions = ["reset_two_factor"]

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return super().get_fieldsets(request, obj)
        fs = list(self.fieldsets)
        if request.user.is_superuser:
            fs[2] = ("Rolle und Zugang", {"fields": ["is_active", "is_staff", "is_superuser", "groups"]})
        return fs

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs if request.user.is_superuser else qs.filter(is_superuser=False)

    @admin.display(description="Rolle")
    def roles(self, u):
        return ", ".join(ROLE_LABELS.get(g.name, g.name) for g in u.groups.all()) or ("Superuser" if u.is_superuser else "–")

    @admin.display(description="2FA", boolean=True)
    def two_factor(self, u):
        from django_otp.plugins.otp_totp.models import TOTPDevice

        return TOTPDevice.objects.filter(user=u, confirmed=True).exists()

    @admin.action(description="Zwei-Faktor-Anmeldung zurücksetzen (neues Telefon)")
    def reset_two_factor(self, request, queryset):
        from django_otp.plugins.otp_static.models import StaticDevice
        from django_otp.plugins.otp_totp.models import TOTPDevice

        for u in queryset:
            TOTPDevice.objects.filter(user=u).delete()
            StaticDevice.objects.filter(user=u).delete()
        self.message_user(request, "Zurückgesetzt. Beim nächsten Anmelden wird die App neu eingerichtet.")


@admin.register(Group)
class RoleAdmin(RoleAdminMixin, GroupAdmin):
    role_perms = {"view": ["Owner"], "change": [], "add": [], "delete": []}

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser  # the matrix is set by `manage.py setup_roles`


# ----- Audit log (A12): every change to prices, devices, content, users and settings -----
AUDITED = [
    "catalog.Category", "catalog.Brand", "catalog.DeviceModel", "catalog.RepairType", "catalog.RepairName", "catalog.RepairOption",
    "catalog.FeaturedRepair", "catalog.Price", "catalog.CategoryPrice", "catalog.ScheduledPriceChange", "catalog.BuybackPrice",
    "catalog.CabinetDrawer", "shops.Shop", "shops.OpeningHours", "shops.SpecialHours", "shops.Holiday",
    "content.ContentBlock", "content.FAQ", "content.MediaAsset", "content.BeforeAfter", "content.WorkshopCard",
    "legal.LegalPage", "legal.LegalPageVersion", "core.SiteSettings", "core.Redirect",
    "leads.Request", "leads.Withdrawal", "leads.PurchaseContract",
]
for label in AUDITED:
    model = apps.get_model(label)
    if not auditlog.contains(model):
        exclude = ["signature"] if label == "leads.PurchaseContract" else []
        auditlog.register(model, exclude_fields=exclude)
for model in (User, Group):
    if not auditlog.contains(model):
        auditlog.register(model, exclude_fields=["password", "last_login"])
