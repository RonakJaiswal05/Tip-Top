"""Admin dashboard (A2): the day at a glance."""
from collections import Counter
from datetime import datetime, timedelta

from django.db.models import Count, Q
from django.http import JsonResponse
from django.utils import timezone

from catalog.models import Price, PriceSource
from leads.models import Request, Withdrawal
from legal.models import LegalPageVersion
from shops.models import BERLIN, Holiday, Shop, SpecialHours

from .roles import user_in

CHANNELS = [("whatsapp", "WhatsApp"), ("callback", "Rückruf"), ("form", "Formular"), ("walkin", "Laufkundschaft")]
BOOKED = ["booked", "in_repair", "ready", "collected"]


def _status(shop: Shop, now: datetime) -> str:
    for a, b in shop.schedule(now.date() - timedelta(days=1), days=16):
        if a <= now < b:
            return f"Geöffnet bis {b:%H:%M}"
        if a > now:
            days = (a.date() - now.date()).days
            when = "heute" if days == 0 else "morgen" if days == 1 else f"{a:%d.%m.}"
            return f"Geschlossen, öffnet {when} um {a:%H:%M}"
    return "Geschlossen"


def dashboard_context(request) -> dict:
    user = request.user
    now = timezone.localtime()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week = today - timedelta(days=today.weekday())
    month = today.replace(day=1)
    qs = Request.objects.all()
    tech_only = user_in(user, "Technician") and not user_in(user, "Owner", "Manager", "Front desk")
    if tech_only:
        qs = qs.filter(assignee=user)

    def by_channel(since):
        c = dict(qs.filter(created_at__gte=since).values_list("kind").annotate(n=Count("id")))
        return [{"label": label, "n": c.get(k, 0)} for k, label in CHANNELS]

    actionable = qs.filter(kind__in=Request.ACTIONABLE)
    waiting = actionable.filter(status="new", created_at__lte=now - timedelta(hours=2)).order_by("created_at")
    stale = actionable.filter(status="new", created_at__lte=now - timedelta(hours=24)).count()
    last30 = actionable.filter(created_at__gte=now - timedelta(days=30)).exclude(kind="withdrawal")
    total30 = last30.count()
    booked30 = last30.filter(status__in=BOOKED).count()

    models_c, repairs_c = Counter(), Counter()
    for device, repairs in qs.filter(created_at__gte=month, kind__in=["callback", "form", "whatsapp"]).values_list("device", "repairs"):
        if device:
            models_c[device] += 1
        for r in repairs or []:
            if r.get("name"):
                repairs_c[r["name"]] += 1

    ctx = {
        "dash": True,
        "tech_only": tech_only,
        "today": by_channel(today), "week": by_channel(week),
        "today_total": qs.filter(created_at__gte=today).count(), "week_total": qs.filter(created_at__gte=week).count(),
        "waiting": waiting[:15], "waiting_n": waiting.count(), "stale": stale,
        "booking_rate": round(100 * booked30 / total30) if total30 else None, "total30": total30,
        "top_models": models_c.most_common(10), "top_repairs": repairs_c.most_common(10),
    }
    if not tech_only:
        nowb = datetime.now(BERLIN)
        shops = list(Shop.objects.filter(active=True).prefetch_related("hours"))
        upcoming = []
        horizon = nowb.date() + timedelta(days=21)
        for sp in SpecialHours.objects.filter(date__gte=nowb.date(), date__lte=horizon).select_related("shop"):
            upcoming.append((sp.date, str(sp)))
        for h in Holiday.objects.filter(date__gte=nowb.date(), date__lte=horizon, closed=True):
            upcoming.append((h.date, f"{h.date:%d.%m.%Y} Feiertag: {h.name_de} (beide Filialen geschlossen)"))
        ctx.update({
            "shops": [{"name": s.area, "status": _status(s, nowb), "rating": s.rating, "count": s.rating_count,
                       "fetched": s.rating_fetched_at, "error": s.rating_error} for s in shops],
            "upcoming": [x[1] for x in sorted(upcoming)],
            "placeholder_prices": Price.objects.filter(source=PriceSource.PLACEHOLDER).count(),
            "sheet_errors": Request.objects.filter(kind__in=Request.ACTIONABLE, sheet_synced_at__isnull=True).exclude(sheet_error="").count(),
            "open_refunds": Withdrawal.objects.filter(refund_status="open").count(),
            "unsent_confirmations": Withdrawal.objects.filter(confirmation_sent_at__isnull=True).count(),
            "legal_unapproved": LegalPageVersion.objects.filter(status="published", lawyer_approved=False).count(),
        })
    return ctx


def dashboard_poll(request):
    qs = Request.objects.filter(kind__in=Request.ACTIONABLE)
    if user_in(request.user, "Technician") and not user_in(request.user, "Owner", "Manager", "Front desk"):
        qs = qs.filter(assignee=request.user)
    r = qs.order_by("-pk").first()
    return JsonResponse({"latest": r.pk if r else 0, "new": qs.filter(status="new").count(),
                         "text": f"{r.get_kind_display()}: {r.device or ''}" if r else ""})
