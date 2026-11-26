"""Seed the shop (with the Google rating snapshot of 15 Nov 2026) and Berlin public holidays.

One shop only since the client's feedback of 17 Nov 2026: Beusselstraße 18, Berlin-Moabit. The Spandau shop is gone."""
from datetime import datetime, time
from decimal import Decimal

import holidays as hol

from .models import BERLIN, Holiday, OpeningHours, Shop

SHOPS = [
    dict(key="moabit", area="Berlin-Moabit", short="Moabit", street="Beusselstraße 18", postal_code="10553",
         phone="+493081475791", phone_display="030 814 757 91", is_workshop=True, is_mail_in=True, order=0,
         google_place_id="ChIJA6sIHRNRqEcRdYbk2bTKeB4", google_name="Meisterwerkstatt TipTop Service 24 Handy Reparatur Berlin",
         maps_query="Meisterwerkstatt TipTop Service 24, Beusselstraße 18, 10553 Berlin", rating=Decimal("4.9"), rating_count=321),
]
SNAPSHOT_AT = datetime(2026, 11, 15, 12, 0, tzinfo=BERLIN)
# Mon–Sat 10:00–20:00, Sunday closed (site and Google profile agree).
DEFAULT_HOURS = [(d, time(10), time(20)) for d in range(6)]


def seed_shops() -> int:
    n = 0
    # Spandau is closed for the site (client, 17 Nov 2026). Switched off, not deleted: old requests still point to it.
    Shop.objects.filter(key="spandau", active=True).update(active=False, is_mail_in=False, is_workshop=False)
    for data in SHOPS:
        rating, count = data.pop("rating"), data.pop("rating_count")
        shop, created = Shop.objects.get_or_create(key=data["key"], defaults=data)
        data["rating"], data["rating_count"] = rating, count
        if created:
            n += 1
            shop.rating, shop.rating_count, shop.rating_fetched_at = rating, count, SNAPSHOT_AT
            shop.save()
        if not shop.hours.exists():
            OpeningHours.objects.bulk_create([OpeningHours(shop=shop, weekday=d, opens=o, closes=c) for d, o, c in DEFAULT_HOURS])
    return n


def seed_holidays(years=(2026, 2027, 2028)) -> int:
    de = hol.country_holidays("DE", subdiv="BE", years=years, language="de")
    en = hol.country_holidays("DE", subdiv="BE", years=years, language="en_US")
    n = 0
    for day, name in sorted(de.items()):
        _, created = Holiday.objects.get_or_create(date=day, defaults={"name_de": name, "name_en": en.get(day, "")})
        n += created
    return n
