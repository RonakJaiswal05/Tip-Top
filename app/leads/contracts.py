"""Ankauf at the counter (A7): check, sign on the tablet, store the contract as PDF."""
import base64
import io
import re

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.files.base import ContentFile
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from core.models import SiteSettings
from core.roles import user_in

from .models import PurchaseContract

# Seller declarations, quoted from the terms (AGB Teil B, § 14 Abs. 2 and § 15) so contract and terms say the same.
DECLARATIONS = [
    "Der Verkäufer versichert, dass er Eigentümer des Geräts ist und frei darüber verfügen darf, dass das Gerät nicht "
    "gestohlen, unterschlagen, finanziert, geleast oder mit Rechten Dritter belastet ist und dass seine Angaben zum Zustand stimmen.",
    "Der Verkäufer sichert und löscht seine Daten vor dem Verkauf und setzt das Gerät auf Werkseinstellungen zurück. TipTop löscht "
    "verbleibende Daten vor dem Weiterverkauf mit einem zertifizierten Löschverfahren und ist nicht verpflichtet, Daten zu sichern "
    "oder herauszugeben.",
]
SIG_RE = re.compile(r"^data:image/png;base64,([A-Za-z0-9+/=]+)$")


def _check_access(request):
    if not user_in(request.user, "Owner", "Manager", "Front desk"):
        raise PermissionDenied


def sign_view(request, pk):
    _check_access(request)
    c = get_object_or_404(PurchaseContract, pk=pk)
    if c.status == PurchaseContract.Status.COMPLETED:
        return redirect("admin:leads_purchasecontract_change", pk)
    errors = c.completion_errors()
    if request.method == "POST":
        m = SIG_RE.match(request.POST.get("signature", ""))
        if not request.POST.get("confirm"):
            errors.append("Bitte bestätigen, dass der Verkäufer die Erklärungen gelesen hat.")
        if not m or len(m.group(1)) < 2000 or len(m.group(1)) > 2_000_000:
            errors.append("Bitte unterschreiben lassen.")
        if not errors:
            c.signature = request.POST["signature"]
            c.signed_at = timezone.now()
            c.status = PurchaseContract.Status.COMPLETED
            c.save()
            c.pdf.save(f"{c.number}.pdf", ContentFile(build_pdf(c)), save=True)
            messages.success(request, f"Ankaufvertrag {c.number} abgeschlossen und als PDF gespeichert.")
            return redirect("admin:leads_purchasecontract_change", pk)
    return render(request, "admin/leads/sign.html", {
        "c": c, "errors": errors, "declarations": DECLARATIONS, "title": f"Ankaufvertrag {c.number} unterschreiben",
        "opts": PurchaseContract._meta, "has_view_permission": True,
    })


def pdf_view(request, pk):
    _check_access(request)
    c = get_object_or_404(PurchaseContract, pk=pk)
    if not c.pdf:
        raise Http404
    return FileResponse(c.pdf.open("rb"), content_type="application/pdf", filename=f"{c.number}.pdf")


def build_pdf(c: PurchaseContract) -> bytes:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    from legal.models import LegalPage

    s = SiteSettings.load()
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=16 * mm, bottomMargin=16 * mm,
                            title=f"Ankaufvertrag {c.number}", author="TipTop Service 24")
    ss = getSampleStyleSheet()
    h = ParagraphStyle("h", parent=ss["Heading1"], fontSize=18, spaceAfter=4)
    h2 = ParagraphStyle("h2", parent=ss["Heading3"], fontSize=11.5, spaceBefore=10, spaceAfter=4)
    p = ParagraphStyle("p", parent=ss["BodyText"], fontSize=9.5, leading=13)
    small = ParagraphStyle("s", parent=p, fontSize=8, leading=10.5, textColor=colors.HexColor("#5A606E"))

    def table(rows):
        t = Table([[Paragraph(f"<b>{a}</b>", p), Paragraph(str(b or "–"), p)] for a, b in rows], colWidths=[52 * mm, None])
        t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 0), (-1, -1), 0.3, colors.HexColor("#DADEE5")),
                               ("BOTTOMPADDING", (0, 0), (-1, -1), 4), ("TOPPADDING", (0, 0), (-1, -1), 4)]))
        return t

    signed = timezone.localtime(c.signed_at) if c.signed_at else None
    shop = c.shop
    iban = c.iban.replace(" ", "")
    iban_masked = f"{iban[:4]} … {iban[-4:]}" if len(iban) > 8 else iban
    story = [
        Paragraph(f"Ankaufvertrag {c.number}", h),
        Paragraph(f"TLAMO GmbH, handelnd unter „TipTop Service 24“, {shop.street if shop else 'Beusselstraße 18'}, "
                  f"{shop.postal_code if shop else '10553'} {shop.city if shop else 'Berlin'} (Käufer)", p),
        Spacer(1, 4),
        Paragraph("Verkäufer", h2),
        table([("Name", c.seller_name), ("Anschrift", f"{c.seller_street}, {c.seller_postal_code} {c.seller_city}"),
               ("Geburtsdatum", c.seller_birth_date.strftime("%d.%m.%Y") if c.seller_birth_date else ""),
               ("Ausweis", f"{c.get_id_type_display()}, Nr. {c.id_number}")]),
        Paragraph("Gerät", h2),
        table([("Gerät", c.device), ("IMEI / Seriennummer", c.imei), ("Speicher / Farbe", c.storage_colour), ("Zubehör", c.accessories)]),
        Paragraph("Prüfung bei Ankauf", h2),
        table([("Display und Touch", "geprüft" if c.check_screen else "nicht geprüft"),
               ("Akkuzustand", f"{c.check_battery_health} %" if c.check_battery_health is not None else ""),
               ("Aktivierungssperre", "aufgehoben" if c.check_activation_lock_off else "NICHT aufgehoben"),
               ("Feuchtigkeitsindikator", c.get_check_water_display()),
               ("Sperrlistenprüfung", ("nicht gesperrt" if c.blocklist_clear else "auffällig") + (f" ({c.blocklist_reference})" if c.blocklist_reference else "")),
               ("Mängel / Notizen", c.check_notes)]),
        Paragraph("Kaufpreis", h2),
        table([("Kaufpreis", f"{c.price:.2f} €".replace(".", ",")),
               ("Zahlung", c.get_payment_display() + (f", IBAN {iban_masked}" if c.payment == "transfer" and iban else ""))]),
        Paragraph("Erklärungen des Verkäufers", h2),
    ]
    for d in DECLARATIONS:
        story.append(Paragraph("• " + d, p))
    agb = LegalPage.objects.filter(key="agb").first()
    v = agb.current("de") if agb else None
    story += [
        Spacer(1, 4),
        Paragraph(f"Es gelten die Allgemeinen Geschäftsbedingungen von TipTop Service 24, Teil B: Ankauf von Geräten"
                  f"{f' (Stand {v.stand})' if v else ''}, abrufbar unter {s.contact_email and 'tiptophandyreparatur.de/de/agb/'}.", p),
        Paragraph("Unterschrift Verkäufer", h2),
    ]
    if c.signature:
        raw = base64.b64decode(c.signature.split(",", 1)[1])
        story.append(Image(io.BytesIO(raw), width=70 * mm, height=26 * mm, kind="proportional"))
    story += [
        Paragraph(f"Berlin, {signed:%d.%m.%Y um %H:%M} Uhr" if signed else "", p),
        Spacer(1, 8),
        Paragraph(f"Für TipTop Service 24: {c.staff.get_full_name() or c.staff.username if c.staff else ''}"
                  f"{f', Filiale {shop.short}' if shop else ''}", p),
    ]
    if not (v and v.lawyer_approved):
        story += [Spacer(1, 10), Paragraph("Hinweis: Vertragsvorlage, vor dem Einsatz anwaltlich prüfen lassen.", small)]
    doc.build(story)
    return buf.getvalue()
