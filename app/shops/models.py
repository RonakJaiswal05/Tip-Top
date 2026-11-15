"""Shops, opening hours, special hours and Berlin public holidays (A9), plus the cached Google rating (F1, F10)."""
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from django.core.exceptions import ValidationError
from django.db import models

BERLIN = ZoneInfo("Europe/Berlin")
WEEKDAYS = [(0, "Montag"), (1, "Dienstag"), (2, "Mittwoch"), (3, "Donnerstag"), (4, "Freitag"), (5, "Samstag"), (6, "Sonntag")]


class Shop(models.Model):
    key = models.SlugField("Schlüssel", max_length=30, unique=True)
    area = models.CharField("Bezeichnung", max_length=60, help_text="z. B. Berlin-Moabit")
    short = models.CharField("Kurzname", max_length=30, help_text="z. B. Moabit")
    street = models.CharField("Straße und Hausnummer", max_length=120)
    postal_code = models.CharField("PLZ", max_length=10)
    city = models.CharField("Ort", max_length=60, default="Berlin")
    phone = models.CharField("Telefon (international)", max_length=20, help_text="z. B. +493081475791")
    phone_display = models.CharField("Telefon (Anzeige)", max_length=30)
    email = models.EmailField("E-Mail", blank=True)
    is_workshop = models.BooleanField("Meisterwerkstatt", default=False)
    is_mail_in = models.BooleanField("Adresse für Einsendungen", default=False)
    order = models.PositiveSmallIntegerField("Reihenfolge", default=0)
    active = models.BooleanField("Aktiv", default=True)
    photo = models.ForeignKey(
        "content.MediaAsset", verbose_name="Foto der Filiale", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )

    google_place_id = models.CharField("Google Place ID", max_length=80, blank=True)
    google_name = models.CharField("Name im Google-Profil", max_length=120, blank=True)
    maps_query = models.CharField(
        "Suchtext für Google Maps", max_length=200, blank=True, help_text="Wird für „Route planen“ verwendet."
    )
    rating = models.DecimalField("Google-Bewertung", max_digits=2, decimal_places=1, null=True, blank=True, editable=False)
    rating_count = models.PositiveIntegerField("Anzahl Bewertungen", null=True, blank=True, editable=False)
    rating_fetched_at = models.DateTimeField("Bewertung abgerufen am", null=True, blank=True, editable=False)
    rating_error = models.CharField("Letzter Abruffehler", max_length=300, blank=True, editable=False)
    latitude = models.DecimalField("Breitengrad", max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField("Längengrad", max_digits=9, decimal_places=6, null=True, blank=True)

    sheet_id = models.CharField(
        "Eigenes Google Sheet (optional)", max_length=120, blank=True,
        help_text="Anfragen für diese Filiale zusätzlich in dieses Sheet schreiben. Leer = nur das Haupt-Sheet.",
    )

    class Meta:
        verbose_name = "Filiale"
        verbose_name_plural = "Filialen"
        ordering = ["order"]

    def __str__(self):
        return self.area

    @property
    def maps_url(self) -> str:
        from urllib.parse import quote

        q = quote(self.maps_query or f"{self.street}, {self.postal_code} {self.city}")
        url = f"https://www.google.com/maps/search/?api=1&query={q}"
        if self.google_place_id:
            url += f"&query_place_id={self.google_place_id}"
        return url

    # ----- opening hours -----
    def intervals_on(self, day: date) -> list[tuple[datetime, datetime]]:
        """Opening intervals on one Berlin date, after special hours and public holidays."""
        special = [s for s in self._special_cache().get(day, [])]
        shop_specific = [s for s in special if s.shop_id == self.id]
        chosen = shop_specific or [s for s in special if s.shop_id is None]
        if chosen:
            if any(s.closed for s in chosen):
                return []
            pairs = [(s.opens, s.closes) for s in chosen if s.opens and s.closes]
        elif day in self._holiday_cache():
            return []
        else:
            pairs = [(h.opens, h.closes) for h in self._hours_cache() if h.weekday == day.weekday()]
        out = []
        for o, c in sorted(pairs):
            start = datetime.combine(day, o, BERLIN)
            end = datetime.combine(day, c, BERLIN) if c > o else datetime.combine(day + timedelta(days=1), c, BERLIN)
            out.append((start, end))
        return out

    def schedule(self, start: date | None = None, days: int = 15) -> list[tuple[datetime, datetime]]:
        start = start or datetime.now(BERLIN).date()
        res = []
        for i in range(days):
            res += self.intervals_on(start + timedelta(days=i))
        return res

    def _hours_cache(self):
        if not hasattr(self, "_hours"):
            self._hours = list(self.hours.all())
        return self._hours

    def _special_cache(self):
        if not hasattr(self, "_special"):
            m = {}
            for s in SpecialHours.objects.filter(models.Q(shop=self) | models.Q(shop__isnull=True), date__gte=date.today() - timedelta(days=2)):
                m.setdefault(s.date, []).append(s)
            self._special = m
        return self._special

    def _holiday_cache(self):
        if not hasattr(self, "_holidays"):
            self._holidays = set(Holiday.objects.filter(closed=True, date__gte=date.today() - timedelta(days=2)).values_list("date", flat=True))
        return self._holidays

    def weekly_hours(self) -> dict[int, list[tuple[time, time]]]:
        out = {d: [] for d in range(7)}
        for h in sorted(self._hours_cache(), key=lambda x: (x.weekday, x.opens)):
            out[h.weekday].append((h.opens, h.closes))
        return out


class OpeningHours(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="hours")
    weekday = models.PositiveSmallIntegerField("Wochentag", choices=WEEKDAYS)
    opens = models.TimeField("Öffnet")
    closes = models.TimeField("Schließt")

    class Meta:
        verbose_name = "Öffnungszeit"
        verbose_name_plural = "Öffnungszeiten"
        ordering = ["shop", "weekday", "opens"]

    def __str__(self):
        return f"{self.get_weekday_display()} {self.opens:%H:%M}–{self.closes:%H:%M}"


class SpecialHours(models.Model):
    shop = models.ForeignKey(
        Shop, verbose_name="Filiale", null=True, blank=True, on_delete=models.CASCADE, related_name="special_hours",
        help_text="Leer = gilt für alle Filialen.",
    )
    date = models.DateField("Datum")
    closed = models.BooleanField("Geschlossen", default=False)
    opens = models.TimeField("Öffnet", null=True, blank=True)
    closes = models.TimeField("Schließt", null=True, blank=True)
    note_de = models.CharField("Hinweis (Deutsch)", max_length=120, blank=True)
    note_en = models.CharField("Hinweis (Englisch)", max_length=120, blank=True)

    class Meta:
        verbose_name = "Sonderöffnungszeit"
        verbose_name_plural = "Sonderöffnungszeiten"
        ordering = ["date", "shop"]

    def clean(self):
        if not self.closed and not (self.opens and self.closes):
            raise ValidationError("Entweder „Geschlossen“ ankreuzen oder Öffnungs- und Schließzeit eintragen.")

    def __str__(self):
        where = self.shop.short if self.shop else "Alle Filialen"
        what = "geschlossen" if self.closed else f"{self.opens:%H:%M}–{self.closes:%H:%M}"
        return f"{self.date:%d.%m.%Y} {where}: {what}"


class Holiday(models.Model):
    """Public holidays in Berlin. Shops are closed unless special hours for that date say otherwise."""

    date = models.DateField("Datum", unique=True)
    name_de = models.CharField("Name (Deutsch)", max_length=80)
    name_en = models.CharField("Name (Englisch)", max_length=80, blank=True)
    closed = models.BooleanField("Geschlossen", default=True)

    class Meta:
        verbose_name = "Feiertag"
        verbose_name_plural = "Feiertage (Berlin)"
        ordering = ["date"]

    def __str__(self):
        return f"{self.date:%d.%m.%Y} {self.name_de}"
