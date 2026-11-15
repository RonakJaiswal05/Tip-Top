from django.contrib import admin, messages
from django.utils.html import format_html

from core.roles import RoleAdminMixin

from .models import FAQ, BeforeAfter, ContentBlock, MediaAsset, WorkshopCard

CONTENT = {"view": ["Owner", "Manager"], "add": ["Owner", "Manager"], "change": ["Owner", "Manager"], "delete": ["Owner", "Manager"]}

WHERE = [
    ("Startseite", "/de/", "/en/"), ("Navigation", "/de/", "/en/"), ("Footer", "/de/#shops", "/en/#shops"),
    ("Preisrechner", "/de/#rechner=phone", "/en/#calculator=phone"), ("Kategorien", "/de/", "/en/"),
    ("Anfrageformular", "/de/anfrage/", "/en/request/"), ("Widerruf", "/de/vertrag-widerrufen/", "/en/withdraw-contract/"),
    ("Rechtstexte", "/de/impressum/", "/en/legal-notice/"), ("Cookie-Banner", "/de/cookies/", "/en/cookies/"),
]


@admin.register(ContentBlock)
class ContentBlockAdmin(RoleAdminMixin, admin.ModelAdmin):
    list_display = ["key", "group", "short_de", "short_en", "updated_at"]
    list_filter = ["group", "format"]
    search_fields = ["key", "text_de", "text_en", "note"]
    readonly_fields = ["key", "format", "preview"]
    fields = ["key", "group", "format", "text_de", "text_en", "note", "preview"]
    role_perms = {**CONTENT, "add": [], "delete": []}

    def has_add_permission(self, request):
        return False

    @admin.display(description="Deutsch")
    def short_de(self, b):
        return (b.text_de[:90] + "…") if len(b.text_de) > 90 else b.text_de

    @admin.display(description="Englisch")
    def short_en(self, b):
        return (b.text_en[:90] + "…") if len(b.text_en) > 90 else b.text_en

    @admin.display(description="Vorschau auf der Website")
    def preview(self, b):
        de, en = next(((d, e) for g, d, e in WHERE if (b.group or "").startswith(g)), ("/de/", "/en/"))
        return format_html('<a href="{}" target="_blank">Deutsch ansehen</a> · <a href="{}" target="_blank">Englisch ansehen</a> '
                           '(nach dem Speichern sofort sichtbar)', de, en)


@admin.register(FAQ)
class FAQAdmin(RoleAdminMixin, admin.ModelAdmin):
    list_display = ["question_de", "question_en", "order", "active"]
    list_editable = ["order", "active"]
    role_perms = CONTENT


@admin.register(MediaAsset)
class MediaAssetAdmin(RoleAdminMixin, admin.ModelAdmin):
    list_display = ["thumb", "key", "title", "published", "decorative", "generated", "size", "updated_at"]
    list_filter = ["published", "generated", "decorative"]
    search_fields = ["key", "title", "alt_de", "alt_en"]
    readonly_fields = ["thumb_large", "size", "variants_list"]
    fields = ["key", "title", "image", "thumb_large", "size", ("alt_de", "alt_en"), ("focus_x", "focus_y"), "published", "decorative",
              "generated", "variants_list"]
    actions = ["regenerate"]
    role_perms = CONTENT

    @admin.display(description="")
    def thumb(self, a):
        u = a.urls()
        return format_html('<img src="{}" alt="" style="height:48px;border-radius:6px">', u["s"]["jpg"]) if "s" in u else "–"

    @admin.display(description="Vorschau mit Fokuspunkt")
    def thumb_large(self, a):
        u = a.urls()
        if "s" not in u:
            return "–"
        return format_html(
            '<img src="{}" alt="" style="width:280px;border-radius:10px;object-fit:cover;object-position:{}% {}%;aspect-ratio:1"> '
            '<img src="{}" alt="" style="width:420px;border-radius:10px;object-fit:cover;object-position:{}% {}%;aspect-ratio:16/9">',
            u["s"]["jpg"], a.focus_x, a.focus_y, u["s"]["jpg"], a.focus_x, a.focus_y)

    @admin.display(description="Größe")
    def size(self, a):
        return f"{a.width} × {a.height}" if a.width else "–"

    @admin.display(description="Erzeugte Dateien")
    def variants_list(self, a):
        u = a.urls()
        rows = [f"{k}: {v.get('w')} px · " + ", ".join(f for f in ("avif", "webp", "jpg") if f in v) for k, v in u.items() if isinstance(v, dict)]
        return format_html("<br>".join(["{}"] * len(rows)), *rows) if rows else "–"

    @admin.action(description="Größen und Formate neu erzeugen")
    def regenerate(self, request, queryset):
        for a in queryset:
            a.save(regenerate=True)
        messages.success(request, f"{queryset.count()} Bilder neu erzeugt.")


@admin.register(BeforeAfter)
class BeforeAfterAdmin(RoleAdminMixin, admin.ModelAdmin):
    list_display = ["__str__", "order", "active"]
    list_editable = ["order", "active"]
    autocomplete_fields = ["before", "after"]
    role_perms = CONTENT


@admin.register(WorkshopCard)
class WorkshopCardAdmin(RoleAdminMixin, admin.ModelAdmin):
    list_display = ["title_de", "title_en", "repair", "order", "active"]
    list_editable = ["order", "active"]
    autocomplete_fields = ["image"]
    role_perms = CONTENT
