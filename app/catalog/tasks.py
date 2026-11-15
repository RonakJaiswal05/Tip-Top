from celery import shared_task
from django.db import transaction
from django.utils import timezone

from .models import Price, PriceSource, ScheduledPriceChange


@shared_task
def apply_scheduled_prices() -> int:
    """Every minute: apply price changes whose date has come (A3 scheduled price changes)."""
    n = 0
    due = ScheduledPriceChange.objects.filter(applied_at__isnull=True, effective_at__lte=timezone.now()).select_related("model", "repair")
    for s in due:
        with transaction.atomic():
            p = Price.objects.filter(model=s.model, repair=s.repair, tier=s.tier).first() or Price(model=s.model, repair=s.repair, tier=s.tier)
            p.amount, p.is_from, p.source = s.amount, s.is_from, PriceSource.SCHEDULED
            p._change_reason = f"Geplante Änderung #{s.pk}" + (f": {s.note}" if s.note else "")
            if s.created_by_id:
                p._history_user = s.created_by
            p.save()
            s.applied_at = timezone.now()
            s.save(update_fields=["applied_at"])
            n += 1
    return n
