"""Retention rules (SOW section 12, A8, A12). Runs nightly."""
from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.utils import timezone


@shared_task
def apply_retention() -> dict:
    from auditlog.models import LogEntry

    from leads.models import Request, Withdrawal
    from legal.models import ConsentRecord

    now = timezone.now()
    out = {}
    # requests that never became a repair: 6 months
    out["requests"] = Request.objects.filter(
        created_at__lt=now - timedelta(days=183),
        status__in=[Request.Status.NEW, Request.Status.CONTACTED, Request.Status.LOST],
    ).exclude(kind=Request.Kind.WITHDRAWAL).delete()[0]
    # withdrawals and consent records: 3 years, as proof
    old = now - timedelta(days=3 * 365)
    out["withdrawals"] = Request.objects.filter(kind=Request.Kind.WITHDRAWAL, created_at__lt=old).delete()[0]
    out["withdrawals_orphans"] = Withdrawal.objects.filter(received_at__lt=old).delete()[0]
    out["consent"] = ConsentRecord.objects.filter(created_at__lt=old).delete()[0]
    # buyback photos: 30 days unless a purchase contract follows (privacy policy, client feedback 17 Nov 2026)
    from leads.photos import delete_expired

    out["offer_photos"] = delete_expired(now)
    # audit log: 12 months
    out["audit"] = LogEntry.objects.filter(timestamp__lt=now - timedelta(days=settings.AUDIT_RETENTION_DAYS)).delete()[0]
    return out
