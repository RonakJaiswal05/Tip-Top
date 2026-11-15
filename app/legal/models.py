"""Legal pages with version history (A9) and the cookie consent log (A8)."""
from django.conf import settings
from django.db import models
from django.utils import timezone


class LegalPage(models.Model):
    key = models.SlugField("Schlüssel", max_length=30, unique=True)
    order = models.PositiveSmallIntegerField("Reihenfolge", default=0)

    class Meta:
        verbose_name = "Rechtstext"
        verbose_name_plural = "Rechtstexte"
        ordering = ["order"]

    def __str__(self):
        v = self.current("de")
        return v.title if v else self.key

    def current(self, lang: str):
        return self.versions.filter(language=lang, status=LegalPageVersion.Status.PUBLISHED).order_by("-version").first()


class LegalPageVersion(models.Model):
    """One version of a legal page in one language. The newest published version is live; older ones stay on record."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Entwurf"
        PUBLISHED = "published", "Veröffentlicht"
        ARCHIVED = "archived", "Archiviert"

    page = models.ForeignKey(LegalPage, on_delete=models.CASCADE, related_name="versions")
    language = models.CharField("Sprache", max_length=2, choices=[("de", "Deutsch"), ("en", "Englisch")])
    version = models.PositiveIntegerField("Version", editable=False)
    status = models.CharField("Status", max_length=10, choices=Status.choices, default=Status.DRAFT)
    title = models.CharField("Überschrift", max_length=120)
    nav_title = models.CharField("Name im Menü", max_length=60)
    intro = models.TextField("Einleitung", blank=True)
    body_html = models.TextField(
        "Text (HTML)",
        help_text="Abschnitte beginnen mit <h2>. Teil-Überschriften als <p class=\"lg-part\">. "
                  "Gelb markierte Platzhalter: <mark class=\"fill\">…</mark>.",
    )
    stand = models.CharField("Stand (Datum im Text)", max_length=40, help_text="z. B. 14. November 2026")
    lawyer_approved = models.BooleanField(
        "Anwaltlich geprüft", default=False, help_text="Erst ankreuzen, wenn diese Fassung vom Anwalt freigegeben ist."
    )
    approval_note = models.CharField("Freigabe-Notiz", max_length=200, blank=True, help_text="z. B. Kanzlei, Datum der Freigabe")
    change_note = models.CharField("Was wurde geändert?", max_length=200, blank=True)
    published_at = models.DateTimeField("Veröffentlicht am", null=True, blank=True, editable=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, editable=False)
    created_at = models.DateTimeField("Angelegt", auto_now_add=True)

    class Meta:
        verbose_name = "Fassung"
        verbose_name_plural = "Fassungen"
        ordering = ["page", "language", "-version"]
        unique_together = [("page", "language", "version")]

    def __str__(self):
        return f"{self.page.key} {self.language} v{self.version} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        if not self.version:
            last = LegalPageVersion.objects.filter(page=self.page, language=self.language).aggregate(m=models.Max("version"))["m"]
            self.version = (last or 0) + 1
        if self.status == self.Status.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)
        if self.status == self.Status.PUBLISHED:
            LegalPageVersion.objects.filter(page=self.page, language=self.language, status=self.Status.PUBLISHED).exclude(
                pk=self.pk
            ).update(status=self.Status.ARCHIVED)


class ConsentRecord(models.Model):
    """Proof of a cookie decision: proof ID, notice version, choices and time. No IP address is stored."""

    class Action(models.TextChoices):
        ACCEPT = "accept", "Alle akzeptiert"
        REJECT = "reject", "Alle abgelehnt"
        SAVE = "save", "Auswahl gespeichert"

    proof_id = models.CharField("Nachweis-ID", max_length=40, db_index=True)
    version = models.PositiveIntegerField("Version des Hinweises")
    action = models.CharField("Aktion", max_length=10, choices=Action.choices)
    necessary = models.BooleanField("Notwendig", default=True)
    stats = models.BooleanField("Statistik", default=False)
    marketing = models.BooleanField("Marketing", default=False)
    language = models.CharField("Sprache", max_length=2, default="de")
    decided_at = models.DateTimeField("Zeitpunkt laut Browser", null=True, blank=True)
    created_at = models.DateTimeField("Gespeichert", auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "Einwilligung"
        verbose_name_plural = "Einwilligungsprotokoll"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.proof_id} v{self.version} {self.get_action_display()}"
