from django.contrib import admin, messages
from django.shortcuts import redirect
from django.utils.html import format_html

from core.roles import RoleAdminMixin
from core.routes import page_url

from .models import ConsentRecord, LegalPage, LegalPageVersion


class VersionInline(admin.TabularInline):
    model = LegalPageVersion
    extra = 0
    fields = ["language", "version", "status", "title", "stand", "lawyer_approved", "published_at", "edit"]
    readonly_fields = ["language", "version", "status", "title", "stand", "lawyer_approved", "published_at", "edit"]
    can_delete = False
    show_change_link = False

    def has_add_permission(self, request, obj=None):
        return False

    @admin.display(description="")
    def edit(self, v):
        from django.urls import reverse

        return format_html('<a href="{}">öffnen</a>', reverse("admin:legal_legalpageversion_change", args=[v.pk]))


@admin.register(LegalPage)
class LegalPageAdmin(RoleAdminMixin, admin.ModelAdmin):
    list_display = ["__str__", "key", "live_de", "live_en"]
    inlines = [VersionInline]
    readonly_fields = ["key"]
    role_perms = {"view": ["Owner", "Manager"], "change": ["Owner", "Manager"], "add": [], "delete": []}

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def _live(self, p, lang):
        v = p.current(lang)
        if not v:
            return "–"
        flag = "anwaltlich geprüft" if v.lawyer_approved else "Vorlage, ungeprüft"
        return format_html('<a href="{}" target="_blank">v{}</a> ({})', page_url(p.key, lang), v.version, flag)

    @admin.display(description="Live (Deutsch)")
    def live_de(self, p):
        return self._live(p, "de")

    @admin.display(description="Live (Englisch)")
    def live_en(self, p):
        return self._live(p, "en")


@admin.register(LegalPageVersion)
class LegalPageVersionAdmin(RoleAdminMixin, admin.ModelAdmin):
    """Every version stays on record. Published versions are read-only: copy one into a new draft to change it."""

    list_display = ["page", "language", "version", "status", "title", "stand", "lawyer_approved", "published_at", "created_by"]
    list_filter = ["page", "language", "status", "lawyer_approved"]
    readonly_fields = ["version", "published_at", "created_by", "created_at"]
    fields = ["page", "language", "version", "status", "title", "nav_title", "stand", "intro", "body_html", "change_note",
              "lawyer_approved", "approval_note", "published_at", "created_by", "created_at"]
    actions = ["new_draft", "publish"]
    role_perms = {"view": ["Owner", "Manager"], "change": ["Owner", "Manager"], "add": ["Owner", "Manager"], "delete": []}

    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        ro = list(super().get_readonly_fields(request, obj))
        if obj and obj.status != LegalPageVersion.Status.DRAFT:
            ro += ["page", "language", "title", "nav_title", "stand", "intro", "body_html", "change_note", "status"]
            if obj.lawyer_approved:
                ro += ["lawyer_approved", "approval_note"]
        return ro

    def save_model(self, request, obj, form, change):
        if not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    @admin.action(description="Als neuen Entwurf kopieren")
    def new_draft(self, request, queryset):
        last = None
        for v in queryset:
            last = LegalPageVersion.objects.create(
                page=v.page, language=v.language, status=LegalPageVersion.Status.DRAFT, title=v.title, nav_title=v.nav_title,
                intro=v.intro, body_html=v.body_html, stand=v.stand, change_note=f"Kopie von v{v.version}", created_by=request.user,
            )
        messages.success(request, "Entwurf angelegt. Text ändern, „Stand“ anpassen und dann veröffentlichen.")
        if last and queryset.count() == 1:
            return redirect("admin:legal_legalpageversion_change", last.pk)
        return None

    @admin.action(description="Veröffentlichen (ersetzt die bisherige Fassung)")
    def publish(self, request, queryset):
        for v in queryset.filter(status=LegalPageVersion.Status.DRAFT):
            v.status = LegalPageVersion.Status.PUBLISHED
            v.save()
        messages.success(request, "Veröffentlicht. Die vorherige Fassung bleibt archiviert.")


@admin.register(ConsentRecord)
class ConsentRecordAdmin(RoleAdminMixin, admin.ModelAdmin):
    """Consent log (A8): search a visitor's proof ID to find their record."""

    list_display = ["created_at", "proof_id", "version", "action", "stats", "marketing", "language"]
    list_filter = ["action", "version", "language", ("created_at", admin.DateFieldListFilter)]
    search_fields = ["proof_id"]
    date_hierarchy = "created_at"
    role_perms = {"view": ["Owner", "Manager", "Front desk"], "change": [], "add": [], "delete": []}

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
