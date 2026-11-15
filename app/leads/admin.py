"""Request inbox (A6), withdrawals (A8) and purchase contracts (A7) in the admin."""
import csv
from datetime import timedelta

from django.contrib import admin, messages
from django.db.models import Q
from django.http import HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html

from core.roles import RoleAdminMixin, user_in

from .models import PurchaseContract, Request, Withdrawal

STATUS_COLOURS = {
    "new": "#3048F0", "contacted": "#8A5A00", "booked": "#1FA67A", "in_repair": "#6B46C1", "ready": "#0E7490",
    "collected": "#5A606E", "lost": "#B3261E",
}


class KindFilter(admin.SimpleListFilter):
    title = "Art"
    parameter_name = "art"

    def lookups(self, request, model_admin):
        return [("actionable", "Zu bearbeiten (Rückruf, Formular, Widerruf, Laufkundschaft)")] + list(Request.Kind.choices)

    def queryset(self, request, qs):
        v = self.value()
        if v == "actionable":
            return qs.filter(kind__in=Request.ACTIONABLE)
        if v:
            return qs.filter(kind=v)
        return qs


class WaitingFilter(admin.SimpleListFilter):
    title = "Wartet"
    parameter_name = "wartet"

    def lookups(self, request, model_admin):
        return [("2h", "Neu seit über 2 Stunden"), ("24h", "Ohne Status seit über 24 Stunden")]

    def queryset(self, request, qs):
        hours = {"2h": 2, "24h": 24}.get(self.value())
        if hours:
            return qs.filter(kind__in=Request.ACTIONABLE, status=Request.Status.NEW, created_at__lte=timezone.now() - timedelta(hours=hours))
        return qs


@admin.action(description="Ausgewählte als CSV exportieren")
def export_csv(modeladmin, request, queryset):
    if not user_in(request.user, "Owner", "Manager"):
        messages.error(request, "Exporte sind Inhaber und Filialleitung vorbehalten.")
        return None
    resp = HttpResponse(content_type="text/csv; charset=utf-8")
    resp["Content-Disposition"] = f'attachment; filename="anfragen-{timezone.localdate():%Y-%m-%d}.csv"'
    resp.write("﻿")
    w = csv.writer(resp, delimiter=";")
    w.writerow(["Nr.", "Eingegangen", "Art", "Status", "Name", "Telefon", "E-Mail", "Gerät", "Reparatur", "Preis", "Beschreibung",
                "Reparaturweg", "Kontakt", "Filiale", "Zuständig", "Sprache"])
    for r in queryset.select_related("shop", "assignee"):
        w.writerow([r.pk, timezone.localtime(r.created_at).strftime("%d.%m.%Y %H:%M"), r.get_kind_display(), r.get_status_display(),
                    r.name, r.phone, r.email, r.device, r.repairs_text, r.total_text, r.problem, r.get_method_display() if r.method else "",
                    r.get_contact_via_display() if r.contact_via else "", r.shop or "", r.assignee or "", r.language])
    return resp


def _set_status(status):
    @admin.action(description=f"Status: {Request.Status(status).label}")
    def act(modeladmin, request, queryset):
        n = 0
        for r in queryset:
            if status == Request.Status.LOST and not r.lost_reason:
                continue
            r.status = status
            r.save()
            n += 1
        messages.success(request, f"{n} Anfragen auf „{Request.Status(status).label}“ gesetzt.")
    act.__name__ = f"set_{status}"
    return act


class WithdrawalInline(admin.StackedInline):
    model = Withdrawal
    can_delete = False
    extra = 0
    readonly_fields = ["reference", "device", "message", "received_at", "confirmation_to", "confirmation_sent_at",
                       "confirmation_error", "confirmation_subject", "confirmation_body"]
    fields = ["reference", "device", "message", "received_at", "confirmation_to", "confirmation_sent_at", "confirmation_error",
              "confirmation_subject", "confirmation_body", "refund_status", "refunded_at"]


@admin.register(Request)
class RequestAdmin(RoleAdminMixin, admin.ModelAdmin):
    list_display = ["number", "received", "kind_badge", "status_badge", "name", "phone_link", "device", "repairs_text", "total_text",
                    "shop", "assignee", "sheet"]
    list_display_links = ["number", "name"]
    list_filter = [KindFilter, "status", WaitingFilter, "shop", "assignee", "language", ("created_at", admin.DateFieldListFilter)]
    search_fields = ["name", "phone", "email", "device", "repairs_text", "problem", "notes", "withdrawal__reference"]
    date_hierarchy = "created_at"
    list_per_page = 50
    actions = [_set_status(s) for s in ("contacted", "booked", "in_repair", "ready", "collected")] + [export_csv]
    autocomplete_fields = ["device_model"]
    readonly_fields = ["created_at", "kind", "language", "source", "repairs_view", "first_contact_at", "status_changed_at",
                       "notified_at", "sheet_synced_at", "sheet_error_view", "quick_contact"]
    inlines = [WithdrawalInline]
    fieldsets = [
        (None, {"fields": [("kind", "created_at"), ("status", "lost_reason"), ("shop", "assignee"), "quick_contact"]}),
        ("Kunde", {"fields": [("name", "phone", "email"), "contact_via"]}),
        ("Gerät und Reparatur", {"fields": [("category", "device", "device_model"), "repairs_text", "repairs_view",
                                            ("total_text", "total_amount"), "problem", ("method", "condition")]}),
        ("Intern", {"fields": ["notes"]}),
        ("Verlauf", {"classes": ["collapse"], "fields": [("first_contact_at", "status_changed_at"), ("notified_at", "sheet_synced_at"),
                                                         "sheet_error_view", ("language", "source")]}),
    ]
    role_perms = {"view": ["Owner", "Manager", "Front desk", "Technician"], "change": ["Owner", "Manager", "Front desk", "Technician"],
                  "add": ["Owner", "Manager", "Front desk"], "delete": ["Owner"]}

    class Media:
        js = ["admin/tiptop/inbox.js"]
        css = {"all": ["admin/tiptop/admin.css"]}

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related("shop", "assignee")
        # Technicians only see requests assigned to them (A1 matrix)
        if user_in(request.user, "Technician") and not user_in(request.user, "Owner", "Manager", "Front desk") and not request.user.is_superuser:
            qs = qs.filter(assignee=request.user)
        return qs

    def changelist_view(self, request, extra_context=None):
        if not request.GET and not request.META.get("QUERY_STRING"):
            from django.shortcuts import redirect

            return redirect(f"{request.path}?art=actionable")
        return super().changelist_view(request, extra_context)

    @admin.display(description="Nr.", ordering="pk")
    def number(self, r):
        return f"#{r.pk}"

    @admin.display(description="Eingegangen", ordering="created_at")
    def received(self, r):
        local = timezone.localtime(r.created_at)
        late = r.status == Request.Status.NEW and r.is_actionable and timezone.now() - r.created_at > timedelta(hours=2)
        return format_html('<span class="{}">{}</span>', "tt-late" if late else "", local.strftime("%d.%m. %H:%M"))

    @admin.display(description="Art", ordering="kind")
    def kind_badge(self, r):
        return format_html('<span class="tt-badge tt-k-{}">{}</span>', r.kind, r.get_kind_display())

    @admin.display(description="Status", ordering="status")
    def status_badge(self, r):
        return format_html('<span class="tt-badge" style="background:{};color:#fff">{}</span>', STATUS_COLOURS.get(r.status, "#555"),
                           r.get_status_display())

    @admin.display(description="Telefon")
    def phone_link(self, r):
        if not r.phone:
            return r.email or "–"
        return format_html('<a href="tel:{}">{}</a>', r.phone, r.phone)

    @admin.display(description="Sheet", boolean=True)
    def sheet(self, r):
        return bool(r.sheet_synced_at) if r.is_actionable else None

    @admin.display(description="Kontakt")
    def quick_contact(self, r):
        if not r.pk:
            return "–"
        parts = []
        if r.phone:
            parts.append(format_html('<a class="button" href="tel:{}">Anrufen</a>', r.phone))
        if r.phone_digits:
            parts.append(format_html('<a class="button" href="https://wa.me/{}" target="_blank" rel="noopener">WhatsApp</a>', r.phone_digits))
        if r.email:
            parts.append(format_html('<a class="button" href="mailto:{}">E-Mail</a>', r.email))
        return format_html(" ".join(["{}"] * len(parts)), *parts) if parts else "–"

    @admin.display(description="Positionen")
    def repairs_view(self, r):
        if not r.repairs:
            return "–"
        rows = "".join(
            format_html("<tr><td>{}</td><td>{}</td><td style='text-align:right'>{}</td></tr>", x.get("name") or x.get("key"),
                        {"p": "Premium", "o": "Original"}.get(x.get("tier"), ""),
                        ("ab " if x.get("from") else "") + (f"{x['price']:.0f} €" if x.get("price") is not None else "auf Anfrage"))
            for x in r.repairs
        )
        return format_html("<table>{}</table>", format_html(rows))

    @admin.display(description="Sheet-Fehler")
    def sheet_error_view(self, r):
        return r.sheet_error or "–"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change and obj.is_actionable:
            from .tasks import sync_to_sheet

            sync_to_sheet.delay(obj.pk)

    def get_urls(self):
        from django.urls import path

        return [path("poll/", self.admin_site.admin_view(self.poll), name="leads_request_poll")] + super().get_urls()

    def poll(self, request):
        """Latest actionable request for the inbox's 5-second check (no personal data beyond what the inbox shows)."""
        from django.http import JsonResponse

        qs = self.get_queryset(request).filter(kind__in=Request.ACTIONABLE).order_by("-pk")
        r = qs.first()
        return JsonResponse({"latest": r.pk if r else 0, "text": f"{r.get_kind_display()}: {r.device or ''}" if r else ""})


@admin.register(Withdrawal)
class WithdrawalAdmin(RoleAdminMixin, admin.ModelAdmin):
    list_display = ["received_at", "name", "reference", "confirmation_to", "confirmation_ok", "refund_status"]
    list_filter = ["refund_status", ("received_at", admin.DateFieldListFilter)]
    search_fields = ["request__name", "confirmation_to", "reference", "device"]
    readonly_fields = ["request_link", "reference", "device", "message", "received_at", "confirmation_to", "confirmation_sent_at",
                       "confirmation_error", "confirmation_subject", "confirmation_body"]
    fields = ["request_link", "reference", "device", "message", "received_at", "confirmation_to", "confirmation_sent_at",
              "confirmation_error", "confirmation_subject", "confirmation_body", "refund_status", "refunded_at"]
    actions = ["resend"]
    role_perms = {"view": ["Owner", "Manager", "Front desk"], "change": ["Owner", "Manager"], "add": [], "delete": []}

    def has_add_permission(self, request):
        return False

    @admin.display(description="Name", ordering="request__name")
    def name(self, w):
        return w.request.name

    @admin.display(description="Bestätigung gesendet", boolean=True)
    def confirmation_ok(self, w):
        return bool(w.confirmation_sent_at)

    @admin.display(description="Anfrage")
    def request_link(self, w):
        return format_html('<a href="{}">#{}</a>', reverse("admin:leads_request_change", args=[w.request_id]), w.request_id)

    @admin.action(description="Bestätigung erneut senden (nur wenn noch nicht gesendet)")
    def resend(self, request, queryset):
        from .tasks import send_withdrawal_confirmation

        ok = sum(1 for w in queryset if send_withdrawal_confirmation(w.pk, inline=True))
        messages.info(request, f"{ok} von {queryset.count()} Bestätigungen gesendet.")


@admin.register(PurchaseContract)
class PurchaseContractAdmin(RoleAdminMixin, admin.ModelAdmin):
    list_display = ["number", "created_at", "seller", "device", "imei", "price", "status", "has_pdf"]
    list_filter = ["status", "shop", "payment", ("created_at", admin.DateFieldListFilter)]
    search_fields = ["number", "seller_first_name", "seller_last_name", "imei", "device", "id_number"]
    readonly_fields = ["number", "status", "signed_at", "pdf_link", "created_at", "data_erased_at", "complete_link"]
    autocomplete_fields = ["offer_request"]
    fieldsets = [
        (None, {"fields": [("number", "status"), ("shop", "staff"), "offer_request", "complete_link"]}),
        ("Verkäufer", {"fields": [("seller_first_name", "seller_last_name"), "seller_street", ("seller_postal_code", "seller_city"),
                                  "seller_birth_date", ("id_type", "id_number")]}),
        ("Gerät", {"fields": [("category", "device"), ("imei", "storage_colour"), "accessories"]}),
        ("Prüfung", {"fields": [("check_screen", "check_battery_health"), "check_activation_lock_off", "check_water", "check_notes",
                                ("blocklist_checked", "blocklist_clear"), "blocklist_reference"]}),
        ("Kaufpreis", {"fields": [("price", "payment"), "iban"]}),
        ("Abschluss", {"fields": [("data_erased", "data_erased_at"), "signed_at", "pdf_link", "created_at"]}),
    ]
    role_perms = {"view": ["Owner", "Manager", "Front desk"], "change": ["Owner", "Manager", "Front desk"],
                  "add": ["Owner", "Manager", "Front desk"], "delete": ["Owner"]}

    def get_readonly_fields(self, request, obj=None):
        ro = list(super().get_readonly_fields(request, obj))
        if obj and obj.status == PurchaseContract.Status.COMPLETED:
            # a signed contract is a record: only the data-erasure note may still change
            ro += [f.name for f in obj._meta.fields if f.name not in ("data_erased",) and f.name not in ro and f.editable]
        return ro

    @admin.display(description="Verkäufer", ordering="seller_last_name")
    def seller(self, c):
        return c.seller_name

    @admin.display(description="PDF", boolean=True)
    def has_pdf(self, c):
        return bool(c.pdf)

    @admin.display(description="Vertrag (PDF)")
    def pdf_link(self, c):
        return format_html('<a href="{}" target="_blank">PDF öffnen</a>', reverse("admin:leads_purchasecontract_pdf", args=[c.pk])) if c.pdf else "–"

    @admin.display(description="Unterschrift")
    def complete_link(self, c):
        if not c.pk:
            return "Erst speichern, dann unterschreiben lassen."
        if c.status == PurchaseContract.Status.COMPLETED:
            return f"Unterschrieben am {timezone.localtime(c.signed_at):%d.%m.%Y %H:%M}"
        return format_html('<a class="button" href="{}">Prüfen und am Tablet unterschreiben lassen</a>',
                           reverse("admin:leads_purchasecontract_sign", args=[c.pk]))

    def save_model(self, request, obj, form, change):
        if not obj.staff_id:
            obj.staff = request.user
        super().save_model(request, obj, form, change)

    def get_urls(self):
        from django.urls import path

        from .contracts import pdf_view, sign_view

        return [
            path("<int:pk>/sign/", self.admin_site.admin_view(sign_view), name="leads_purchasecontract_sign"),
            path("<int:pk>/pdf/", self.admin_site.admin_view(pdf_view), name="leads_purchasecontract_pdf"),
        ] + super().get_urls()
