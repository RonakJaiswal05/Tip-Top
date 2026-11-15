"""Background jobs for requests: staff email, Google Sheets row, withdrawal confirmation, daily summary."""
import logging
from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone

from core.models import SiteSettings

from .models import Request, Withdrawal

log = logging.getLogger(__name__)


def admin_url(req: Request) -> str:
    return f"{settings.SITE_URL}/admin/leads/request/{req.pk}/change/"


@shared_task
def after_new_request(request_id: int):
    """Called once per new actionable request (after the database commit)."""
    notify_staff.delay(request_id)
    sync_to_sheet.delay(request_id)


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=30, retry_backoff_max=900, max_retries=6)
def notify_staff(self, request_id: int):
    req = Request.objects.filter(pk=request_id).select_related("withdrawal", "shop").first()
    if not req or req.notified_at:
        return
    s = SiteSettings.load()
    to = s.notify_list
    if not to:
        return
    ctx = {"r": req, "url": admin_url(req), "wa": f"https://wa.me/{req.phone_digits}" if req.phone_digits else ""}
    subject = f"Neue Anfrage: {req.get_kind_display()} · {req.device or '–'} · {req.name or req.email or '–'}"
    body = render_to_string("emails/staff_new_request.txt", ctx)
    EmailMessage(subject[:180], body, settings.DEFAULT_FROM_EMAIL, to, reply_to=[req.email] if req.email else None).send()
    Request.objects.filter(pk=req.pk).update(notified_at=timezone.now())


SHEET_HEADER = ["Eingegangen", "Nr.", "Art", "Status", "Name", "Telefon", "E-Mail", "Gerät", "Reparatur / Anliegen",
                "Angezeigter Preis", "Beschreibung", "Reparaturweg", "Kontakt über", "Sprache", "Filiale", "Admin-Link"]


def sheet_row(req: Request) -> list:
    return [
        timezone.localtime(req.created_at).strftime("%d.%m.%Y %H:%M"), req.pk, req.get_kind_display(), req.get_status_display(),
        req.name, req.phone, req.email, req.device, req.repairs_text, req.total_text, req.problem,
        req.get_method_display() if req.method else "", req.get_contact_via_display() if req.contact_via else "",
        req.language.upper(), req.shop.short if req.shop else "", admin_url(req),
    ]


def _append(sheet_id: str, tab: str, row: list):
    import gspread

    gc = gspread.service_account(filename=settings.GOOGLE_SERVICE_ACCOUNT_FILE)
    sh = gc.open_by_key(sheet_id)
    try:
        ws = sh.worksheet(tab)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=tab, rows=1000, cols=len(SHEET_HEADER))
    if not ws.row_values(1):
        ws.append_row(SHEET_HEADER, value_input_option="RAW")
    # RAW: a phone number like +4930… or a name starting with "=" stays text, never a formula
    ws.append_row([str(x) if x is not None else "" for x in row], value_input_option="RAW")


@shared_task(bind=True, max_retries=8)
def sync_to_sheet(self, request_id: int):
    """Write the request as a row to the shared Google Sheet (and the shop's own sheet, if set). Retries with backoff."""
    req = Request.objects.filter(pk=request_id).select_related("shop").first()
    s = SiteSettings.load()
    if not req or req.sheet_synced_at or not (s.sheets_enabled and s.google_sheet_id):
        return
    try:
        row = sheet_row(req)
        _append(s.google_sheet_id, s.google_sheet_tab or "Anfragen", row)
        if req.shop and req.shop.sheet_id and req.shop.sheet_id != s.google_sheet_id:
            _append(req.shop.sheet_id, s.google_sheet_tab or "Anfragen", row)
        Request.objects.filter(pk=req.pk).update(sheet_synced_at=timezone.now(), sheet_error="")
    except Exception as e:  # network, quota, auth: keep the request, try again later
        Request.objects.filter(pk=req.pk).update(sheet_attempts=req.sheet_attempts + 1, sheet_error=str(e)[:300])
        log.warning("sheet sync failed for request %s: %s", request_id, e)
        raise self.retry(exc=e, countdown=min(60 * 2 ** self.request.retries, 3600))


@shared_task
def retry_unsynced():
    """Safety net (every 10 minutes): rows that never reached the sheet, e.g. after an outage."""
    s = SiteSettings.load()
    if not (s.sheets_enabled and s.google_sheet_id):
        return 0
    since = timezone.now() - timedelta(days=7)
    ids = list(Request.objects.filter(kind__in=Request.ACTIONABLE, sheet_synced_at__isnull=True, created_at__gte=since,
                                      sheet_attempts__lt=30).values_list("pk", flat=True)[:50])
    for pk in ids:
        sync_to_sheet.delay(pk)
    return len(ids)


def _withdrawal_mail(wd: Withdrawal) -> tuple[str, str]:
    req = wd.request
    lang = req.language
    at = timezone.localtime(wd.received_at)
    from core.page import date_long

    ctx = {"wd": wd, "r": req, "date": date_long(at.date(), lang), "time": at.strftime("%H:%M"), "s": SiteSettings.load()}
    subject = "Eingangsbestätigung: dein Widerruf" if lang == "de" else "Confirmation of receipt: your withdrawal"
    body = render_to_string(f"emails/withdrawal_confirmation_{lang}.txt", ctx)
    return subject, body


def send_withdrawal_confirmation(withdrawal_id: int, inline: bool = False) -> bool:
    """Send the confirmation with content, date and time immediately. On failure, keep trying in the background."""
    wd = Withdrawal.objects.select_related("request").get(pk=withdrawal_id)
    if wd.confirmation_sent_at:
        return True
    subject, body = _withdrawal_mail(wd)
    Withdrawal.objects.filter(pk=wd.pk).update(confirmation_subject=subject, confirmation_body=body)
    s = SiteSettings.load()
    try:
        bcc = s.notify_list[:1]  # the shop keeps a copy of every confirmation
        EmailMessage(subject, body, settings.DEFAULT_FROM_EMAIL, [wd.confirmation_to], bcc=bcc, reply_to=[s.contact_email]).send()
        Withdrawal.objects.filter(pk=wd.pk).update(confirmation_sent_at=timezone.now(), confirmation_error="")
        return True
    except Exception as e:
        log.error("withdrawal confirmation %s failed: %s", withdrawal_id, e)
        Withdrawal.objects.filter(pk=wd.pk).update(confirmation_error=str(e)[:300])
        if inline:
            retry_withdrawal_confirmation.apply_async((withdrawal_id,), countdown=60)
            return False
        raise


@shared_task(bind=True, max_retries=20)
def retry_withdrawal_confirmation(self, withdrawal_id: int):
    try:
        send_withdrawal_confirmation(withdrawal_id)
    except Exception as e:
        raise self.retry(exc=e, countdown=min(120 * 2 ** self.request.retries, 3600))


@shared_task
def send_daily_summary():
    s = SiteSettings.load()
    if not s.summary_list:
        return
    now = timezone.localtime()
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today = Request.objects.filter(created_at__gte=start)
    by_kind = {k.label: today.filter(kind=k).count() for k in Request.Kind}
    waiting = Request.objects.filter(kind__in=Request.ACTIONABLE, status=Request.Status.NEW,
                                     created_at__lte=now - timedelta(hours=2)).order_by("created_at")
    ctx = {"date": now, "by_kind": by_kind, "total": today.count(), "waiting": waiting[:50], "waiting_n": waiting.count(),
           "withdrawals": Withdrawal.objects.filter(received_at__gte=start), "site": settings.SITE_URL}
    body = render_to_string("emails/daily_summary.txt", ctx)
    EmailMessage(f"Tageszusammenfassung {now:%d.%m.%Y}: {ctx['total']} Anfragen", body, settings.DEFAULT_FROM_EMAIL, s.summary_list).send()
