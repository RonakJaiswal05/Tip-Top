from django.core.cache import cache
from django.core.validators import RegexValidator
from django.db import models


class SiteSettings(models.Model):
    """One place for the details that rarely change (A11). There is exactly one row."""

    whatsapp_number = models.CharField(
        "WhatsApp-Nummer", max_length=20, default="4917672746296",
        validators=[RegexValidator(r"^\d{8,15}$", "Nur Ziffern im internationalen Format ohne +, z. B. 4917672746296.")],
        help_text="Wird für alle WhatsApp-Schaltflächen und vorausgefüllten Nachrichten verwendet.",
    )
    phone = models.CharField("Telefon (Hauptnummer, international)", max_length=20, default="+493081475791")
    phone_display = models.CharField("Telefon (Anzeige)", max_length=30, default="030 814 757 91")
    contact_email = models.EmailField("Kontakt-E-Mail", default="info@tiptophandyreparatur.de")
    instagram_url = models.URLField("Instagram", blank=True, default="https://www.instagram.com/tiptopservice24/")
    b2b_url = models.CharField(
        "Link „Geschäftskunden“", max_length=200, blank=True,
        help_text="Leer lassen, um den Link im Footer auszublenden.",
    )

    notify_emails = models.TextField(
        "Empfänger für neue Anfragen", blank=True, default="info@tiptophandyreparatur.de",
        help_text="Eine E-Mail-Adresse pro Zeile.",
    )
    summary_emails = models.TextField(
        "Empfänger der Tageszusammenfassung", blank=True, default="info@tiptophandyreparatur.de",
        help_text="Eine E-Mail-Adresse pro Zeile.",
    )

    sheets_enabled = models.BooleanField("Google Sheets aktiv", default=False)
    google_sheet_id = models.CharField(
        "Google-Sheet-ID", max_length=120, blank=True,
        help_text="Der lange Teil der Sheet-URL zwischen /d/ und /edit. Das Sheet muss für das Dienstkonto freigegeben sein.",
    )
    google_sheet_tab = models.CharField("Tabellenblatt", max_length=60, default="Anfragen")

    analytics_enabled = models.BooleanField(
        "Statistik (Matomo) aktiv", default=False,
        help_text="Erst einschalten, wenn Matomo läuft. Zeigt die Kategorie „Statistik“ im Cookie-Banner.",
    )
    matomo_url = models.URLField("Matomo-URL", blank=True)
    matomo_site_id = models.CharField("Matomo-Site-ID", max_length=10, blank=True)
    ads_enabled = models.BooleanField(
        "Werbe-Tracking aktiv", default=False,
        help_text="Nur einschalten, wenn Anzeigen geschaltet werden. Zeigt die Kategorie „Marketing“ im Cookie-Banner.",
    )
    google_ads_id = models.CharField("Google-Ads-ID", max_length=40, blank=True)
    meta_pixel_id = models.CharField("Meta-Pixel-ID", max_length=40, blank=True)
    consent_version = models.PositiveIntegerField(
        "Version des Cookie-Hinweises", default=1,
        help_text="Wird automatisch erhöht, wenn sich die Kategorien ändern. Danach fragt die Website alle Besucher erneut.",
    )

    prices_are_placeholders = models.BooleanField(
        "Preise sind Platzhalter", default=True,
        help_text="Zeigt einen Hinweis im Footer. Nach dem Import der echten Preisliste ausschalten.",
    )
    maintenance_mode = models.BooleanField("Wartungsmodus", default=False)
    maintenance_text_de = models.TextField(
        "Wartungstext (Deutsch)", blank=True,
        default="Wir arbeiten gerade an der Website. Ruf uns an oder schreib uns auf WhatsApp, wir sind wie gewohnt für dich da.",
    )
    maintenance_text_en = models.TextField(
        "Wartungstext (Englisch)", blank=True,
        default="We're working on the website right now. Call us or message us on WhatsApp, we're here for you as usual.",
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Einstellungen"
        verbose_name_plural = "Einstellungen"

    def __str__(self):
        return "Einstellungen"

    CACHE_KEY = "site-settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        if SiteSettings.objects.filter(pk=1).exists():
            old = SiteSettings.objects.get(pk=1)
            if (old.analytics_enabled, old.ads_enabled) != (self.analytics_enabled, self.ads_enabled):
                self.consent_version = old.consent_version + 1
        super().save(*args, **kwargs)
        cache.delete(self.CACHE_KEY)

    @classmethod
    def load(cls) -> "SiteSettings":
        obj = cache.get(cls.CACHE_KEY)
        if obj is None:
            obj, _ = cls.objects.get_or_create(pk=1)
            cache.set(cls.CACHE_KEY, obj, 300)
        return obj

    @staticmethod
    def _lines(value: str) -> list[str]:
        return [x.strip() for x in value.replace(",", "\n").splitlines() if x.strip()]

    @property
    def notify_list(self) -> list[str]:
        return self._lines(self.notify_emails)

    @property
    def summary_list(self) -> list[str]:
        return self._lines(self.summary_emails)

    @property
    def consent_categories(self) -> list[str]:
        cats = ["necessary"]
        if self.analytics_enabled:
            cats.append("stats")
        if self.ads_enabled:
            cats.append("marketing")
        return cats


class Redirect(models.Model):
    """A 301 redirect from an old (Shopify) address to a page on the new site."""

    old_path = models.CharField("Alte Adresse", max_length=300, unique=True, help_text="Pfad ohne Domain, z. B. /pages/kontakt")
    new_path = models.CharField("Neue Adresse", max_length=300, help_text="Pfad ohne Domain, z. B. /de/#shops")
    note = models.CharField("Notiz", max_length=200, blank=True)
    active = models.BooleanField("Aktiv", default=True)

    class Meta:
        verbose_name = "Weiterleitung"
        verbose_name_plural = "Weiterleitungen"
        ordering = ["old_path"]

    def __str__(self):
        return f"{self.old_path} → {self.new_path}"

    def save(self, *args, **kwargs):
        self.old_path = normalise_path(self.old_path)
        super().save(*args, **kwargs)
        cache.delete("redirect-map")


def normalise_path(p: str) -> str:
    p = (p or "").strip()
    if "://" in p:
        p = "/" + p.split("://", 1)[1].split("/", 1)[-1]
    p = p.split("?", 1)[0].split("#", 1)[0]
    if not p.startswith("/"):
        p = "/" + p
    return p.rstrip("/").lower() or "/"
