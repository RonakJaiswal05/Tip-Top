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
        s = Shop.objects.get(key="spandau")
        SpecialHours.objects.create(shop=s, date=date(2026, 12, 25), opens=time(12), closes=time(16))
        SpecialHours.objects.create(shop=None, date=date(2026, 12, 23), closed=True)
        fresh = Shop.objects.get(pk=s.pk)
        self.assertTrue(is_open_now(fresh, datetime(2026, 12, 25, 13, 0, tzinfo=BERLIN))[0])
        self.assertFalse(is_open_now(Shop.objects.get(pk=s.pk), datetime(2026, 12, 23, 13, 0, tzinfo=BERLIN))[0])

    def test_different_hours_per_shop_show_in_texts(self):
        sp = Shop.objects.get(key="spandau")
        sp.hours.all().delete()
        for d in range(4):
            OpeningHours.objects.create(shop=sp, weekday=d, opens=time(10), closes=time(20, 30))
        for d in (4, 5):
            OpeningHours.objects.create(shop=sp, weekday=d, opens=time(10), closes=time(21))
        shops = list(Shop.objects.prefetch_related("hours").order_by("order"))
        self.assertEqual(summary(shops, "de"), "Moabit Mo–Sa 10–20 Uhr; Spandau Mo–Do 10–20:30 Uhr; Fr–Sa 10–21 Uhr")
        self.assertEqual(summary(shops[:1], "en", long=True), "Monday to Saturday, 10:00 to 20:00")
        from django.core.cache import cache
        from django.test import Client

        cache.clear()
        html = Client().get("/de/").content.decode()
        self.assertIn("Spandau Mo–Do 10–20:30 Uhr", html)
