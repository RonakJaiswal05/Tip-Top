"""Open status for every hour of a week, with a holiday and special hours (SOW F1, F10)."""
from datetime import date, datetime, time, timedelta

from shops.hours import is_open_now, summary
from shops.models import BERLIN, Holiday, OpeningHours, Shop, SpecialHours

from .base import SeededTestCase


class HoursTests(SeededTestCase):
    def test_every_hour_of_a_week_including_a_holiday(self):
        moabit = Shop.objects.get(key="moabit")
        start = date(2026, 12, 21)  # Monday; 25 and 26 December are holidays in Berlin
        self.assertTrue(Holiday.objects.filter(date=date(2026, 12, 25)).exists())
        for day in range(7):
            d = start + timedelta(days=day)
            for hour in range(24):
                now = datetime.combine(d, time(hour, 30), BERLIN)
                fresh = Shop.objects.get(pk=moabit.pk)  # no cached schedule
                is_open, _ = is_open_now(fresh, now)
                expected = d.weekday() < 6 and 10 <= hour < 20 and d not in (date(2026, 12, 25), date(2026, 12, 26))
                self.assertEqual(is_open, expected, f"{d} {hour}:30")

    def test_next_opening_skips_sunday_and_holidays(self):
        s = Shop.objects.get(key="moabit")
        _, at = is_open_now(s, datetime(2026, 12, 24, 21, 0, tzinfo=BERLIN))  # Thu evening -> 25/26 holidays, 27 Sunday
        self.assertEqual(at, datetime(2026, 12, 28, 10, 0, tzinfo=BERLIN))

    def test_special_hours_win(self):
        s = Shop.objects.get(key="moabit")
        SpecialHours.objects.create(shop=s, date=date(2026, 12, 25), opens=time(12), closes=time(16))
        SpecialHours.objects.create(shop=None, date=date(2026, 12, 23), closed=True)
        fresh = Shop.objects.get(pk=s.pk)
        self.assertTrue(is_open_now(fresh, datetime(2026, 12, 25, 13, 0, tzinfo=BERLIN))[0])
        self.assertFalse(is_open_now(Shop.objects.get(pk=s.pk), datetime(2026, 12, 23, 13, 0, tzinfo=BERLIN))[0])

    def test_one_shop_only(self):
        """Client, 17 Nov 2026: only Beusselstraße 18. Spandau stays in the database (old requests) but is off."""
        from django.test import Client

        self.assertEqual(list(Shop.objects.filter(active=True).values_list("key", flat=True)), ["moabit"])
        html = Client().get("/de/").content.decode()
        self.assertNotIn("Spandau", html)
        self.assertNotIn("Havelstra", html)
        self.assertIn("10553 Berlin-Moabit", html)

    def test_hours_one_day_per_line_follow_the_admin(self):
        mo = Shop.objects.get(key="moabit")
        mo.hours.filter(weekday=5).update(closes=time(18))
        shops = list(Shop.objects.filter(active=True).prefetch_related("hours").order_by("order"))
        self.assertEqual(summary(shops, "de"), "Mo–Fr 10–20 Uhr; Sa 10–18 Uhr")
        self.assertEqual(summary(shops, "en", long=True), "Monday to Friday, 10:00 to 20:00; Saturday, 10:00 to 18:00")
        from django.core.cache import cache
        from django.test import Client

        cache.clear()
        html = Client().get("/de/").content.decode()
        self.assertIn("<li><span>Samstag</span><span>10:00–18:00 Uhr</span></li>".replace("<li>", ""), html.replace(' class="today"', ""))
        self.assertIn("<span>Sonntag</span><span><b>geschlossen</b></span>", html)
        en = Client().get("/en/").content.decode()
        self.assertIn("<span>Sunday</span><span><b>closed</b></span>", en)
