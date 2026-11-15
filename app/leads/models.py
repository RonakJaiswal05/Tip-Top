"""Requests from the website (A6), withdrawals (A8) and device purchase contracts (A7)."""
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Request(models.Model):
    class Kind(models.TextChoices):
        CALLBACK = "callback", "Rückruf"
        FORM = "form", "Anfrageformular"
        WHATSAPP = "whatsapp", "WhatsApp gestartet"
        SALE = "sale", "Ankauf-Angebot"
        WALKIN = "walkin", "Laufkundschaft"
        WITHDRAWAL = "withdrawal", "Widerruf"

    ACTIONABLE = [Kind.CALLBACK, Kind.FORM, Kind.WALKIN, Kind.WITHDRAWAL]

    class Status(models.TextChoices):
        NEW = "new", "Neu"
        CONTACTED = "contacted", "Kontaktiert"
        BOOKED = "booked", "Gebucht"
        IN_REPAIR = "in_repair", "In Reparatur"
        READY = "ready", "Abholbereit"
        COLLECTED = "collected", "Abgeholt"
        LOST = "lost", "Verloren"

    class LostReason(models.TextChoices):
        PRICE = "price", "Zu teuer"
        NO_ANSWER = "no_answer", "Nicht erreicht"
        ELSEWHERE = "elsewhere", "Woanders repariert"
        NOT_REPAIRABLE = "not_repairable", "Nicht reparierbar"
        CANCELLED = "cancelled", "Abgesagt"
        SPAM = "spam", "Spam / Test"
        OTHER = "other", "Sonstiges"

    class Method(models.TextChoices):
        MOABIT = "moabit", "Vorbeikommen in Moabit"
        SPANDAU = "spandau", "Vorbeikommen in Spandau"
        PICKUP = "pickup", "Kostenlose Abholung (5 km)"
        MAILIN = "mailin", "Einschicken"

    class Via(models.TextChoices):
        WHATSAPP = "whatsapp", "WhatsApp"
        PHONE = "phone", "Anruf"
        EMAIL = "email", "E-Mail"

    kind = models.CharField("Art", max_length=12, choices=Kind.choices)
    status = models.CharField("Status", max_length=12, choices=Status.choices, default=Status.NEW)
    lost_reason = models.CharField("Grund (verloren)", max_length=20, choices=LostReason.choices, blank=True)

    name = models.CharField("Name", max_length=120, blank=True)
    phone = models.CharField("Telefon", max_length=40, blank=True)
    email = models.EmailField("E-Mail", blank=True)

    category = models.CharField("Kategorie", max_length=20, blank=True)
    device_model = models.ForeignKey(
        "catalog.DeviceModel", verbose_name="Gerät (Katalog)", null=True, blank=True, on_delete=models.SET_NULL, related_name="requests"
    )
    device = models.CharField("Gerät", max_length=160, blank=True)
    repairs = models.JSONField("Reparaturen (Daten)", default=list, blank=True)
    repairs_text = models.CharField("Reparatur", max_length=400, blank=True)
    total_text = models.CharField("Angezeigter Preis", max_length=80, blank=True)
    total_amount = models.DecimalField("Summe (€)", max_digits=8, decimal_places=2, null=True, blank=True)
    problem = models.TextField("Beschreibung", blank=True)
    method = models.CharField("Reparaturweg", max_length=10, choices=Method.choices, blank=True)
    contact_via = models.CharField("Kontakt über", max_length=10, choices=Via.choices, blank=True)
    condition = models.CharField("Zustand (Ankauf)", max_length=40, blank=True)

    language = models.CharField("Sprache", max_length=2, default="de")
    source = models.CharField("Quelle", max_length=200, blank=True, help_text="Seite, von der die Anfrage kam.")
    shop = models.ForeignKey("shops.Shop", verbose_name="Filiale", null=True, blank=True, on_delete=models.SET_NULL)
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name="Zuständig", null=True, blank=True, on_delete=models.SET_NULL, related_name="requests"
    )
    notes = models.TextField("Interne Notizen", blank=True)

    created_at = models.DateTimeField("Eingegangen", default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    first_contact_at = models.DateTimeField("Erster Kontakt", null=True, blank=True)
    status_changed_at = models.DateTimeField("Status geändert", null=True, blank=True)
    notified_at = models.DateTimeField("Team benachrichtigt", null=True, blank=True, editable=False)
    sheet_synced_at = models.DateTimeField("Im Google Sheet", null=True, blank=True, editable=False)
    sheet_attempts = models.PositiveSmallIntegerField(default=0, editable=False)
    sheet_error = models.CharField(max_length=300, blank=True, editable=False)

    class Meta:
        verbose_name = "Anfrage"
        verbose_name_plural = "Anfragen"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["kind", "status"]), models.Index(fields=["status", "created_at"])]

    def __str__(self):
        who = self.name or self.get_kind_display()
        return f"#{self.pk} {who} · {self.device or '–'}"

    def clean(self):
        if self.status == self.Status.LOST and not self.lost_reason:
            raise ValidationError({"lost_reason": "Bitte einen Grund angeben."})

    def save(self, *args, **kwargs):
        if self.pk:
            old = Request.objects.filter(pk=self.pk).values_list("status", flat=True).first()
            if old is not None and old != self.status:
                self.status_changed_at = timezone.now()
                if old == self.Status.NEW and not self.first_contact_at:
                    self.first_contact_at = timezone.now()
        if self.shop_id is None and self.method in ("moabit", "spandau"):
            from shops.models import Shop

            self.shop = Shop.objects.filter(key=self.method).first()
        super().save(*args, **kwargs)

    @property
    def is_actionable(self) -> bool:
        return self.kind in self.ACTIONABLE

    @property
    def phone_digits(self) -> str:
        d = "".join(c for c in self.phone if c.isdigit())
        if d.startswith("00"):
            d = d[2:]
        elif d.startswith("0"):
            d = "49" + d[1:]
        return d


class Withdrawal(models.Model):
    """An electronic withdrawal under § 356a BGB, with the confirmation email on record (A8)."""

    class Refund(models.TextChoices):
        OPEN = "open", "Offen"
        REFUNDED = "refunded", "Erstattet"
        NOTHING = "nothing", "Nichts zu erstatten"
        REJECTED = "rejected", "Abgelehnt (mit Begründung in den Notizen)"

    request = models.OneToOneField(Request, on_delete=models.CASCADE, related_name="withdrawal")
    reference = models.CharField("Auftragsnummer oder Datum", max_length=120)
    device = models.CharField("Gerät", max_length=160, blank=True)
    message = models.TextField("Nachricht", blank=True)
    received_at = models.DateTimeField("Eingegangen am", default=timezone.now)
    confirmation_to = models.EmailField("Bestätigung an")
    confirmation_subject = models.CharField("Betreff der Bestätigung", max_length=200, blank=True)
    confirmation_body = models.TextField("Text der Bestätigung", blank=True)
    confirmation_sent_at = models.DateTimeField("Bestätigung gesendet", null=True, blank=True)
    confirmation_error = models.CharField("Fehler beim Senden", max_length=300, blank=True)
    refund_status = models.CharField("Erstattung", max_length=10, choices=Refund.choices, default=Refund.OPEN)
    refunded_at = models.DateTimeField("Erstattet am", null=True, blank=True)

    class Meta:
        verbose_name = "Widerruf"
        verbose_name_plural = "Widerrufe"
        ordering = ["-received_at"]

    def __str__(self):
        return f"Widerruf {self.request.name} ({self.received_at:%d.%m.%Y %H:%M})"


def contract_upload(instance, filename):
    return f"contracts/{timezone.now():%Y/%m}/{instance.number or 'entwurf'}.pdf"


class PurchaseContract(models.Model):
    """Ankaufvertrag: guided purchase of a used device at the counter (A7)."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Entwurf"
        COMPLETED = "completed", "Abgeschlossen"
        CANCELLED = "cancelled", "Storniert"

    class IdType(models.TextChoices):
        ID_CARD = "id_card", "Personalausweis"
        PASSPORT = "passport", "Reisepass"
        RESIDENCE = "residence", "Aufenthaltstitel"
        OTHER = "other", "Anderer amtlicher Lichtbildausweis"

    class Payment(models.TextChoices):
        CASH = "cash", "Bar"
        TRANSFER = "transfer", "Überweisung"

    class Water(models.TextChoices):
        OK = "ok", "Nicht ausgelöst"
        TRIGGERED = "triggered", "Ausgelöst"
        UNKNOWN = "unknown", "Nicht prüfbar"

    number = models.CharField("Vertragsnummer", max_length=20, unique=True, blank=True)
    status = models.CharField("Status", max_length=10, choices=Status.choices, default=Status.DRAFT)
    shop = models.ForeignKey("shops.Shop", verbose_name="Filiale", null=True, on_delete=models.PROTECT)
    staff = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="Mitarbeiter", null=True, blank=True, on_delete=models.SET_NULL)
    offer_request = models.ForeignKey(
        Request, verbose_name="Angebotsanfrage", null=True, blank=True, on_delete=models.SET_NULL,
        limit_choices_to={"kind": "sale"}, related_name="contracts",
    )

    seller_first_name = models.CharField("Vorname", max_length=80)
    seller_last_name = models.CharField("Nachname", max_length=80)
    seller_street = models.CharField("Straße und Hausnummer", max_length=120)
    seller_postal_code = models.CharField("PLZ", max_length=10)
    seller_city = models.CharField("Ort", max_length=80)
    seller_birth_date = models.DateField("Geburtsdatum")
    id_type = models.CharField("Ausweisart", max_length=10, choices=IdType.choices, default=IdType.ID_CARD)
    id_number = models.CharField("Ausweisnummer", max_length=40)

    category = models.CharField("Kategorie", max_length=20, blank=True)
    device = models.CharField("Gerät (Marke und Modell)", max_length=160)
    imei = models.CharField("IMEI oder Seriennummer", max_length=40, db_index=True)
    storage_colour = models.CharField("Speicher / Farbe", max_length=80, blank=True)
    accessories = models.CharField("Zubehör", max_length=200, blank=True)

    check_screen = models.BooleanField("Display geprüft, Touch funktioniert", default=False)
    check_battery_health = models.PositiveSmallIntegerField("Akkuzustand (%)", null=True, blank=True)
    check_activation_lock_off = models.BooleanField(
        "Aktivierungssperre aus („Wo ist?“ / Google-Konto)", default=False,
        help_text="Ohne aufgehobene Aktivierungssperre kann der Ankauf nicht abgeschlossen werden.",
    )
    check_water = models.CharField("Feuchtigkeitsindikator", max_length=10, choices=Water.choices, default=Water.UNKNOWN)
    check_notes = models.TextField("Prüfnotizen / Mängel", blank=True)
    blocklist_checked = models.BooleanField("IMEI gegen Sperrlisten geprüft", default=False)
    blocklist_reference = models.CharField("Prüfnachweis (Dienst, Ergebnis)", max_length=200, blank=True)
    blocklist_clear = models.BooleanField("Nicht gesperrt gemeldet", default=False)

    price = models.DecimalField("Kaufpreis (€)", max_digits=8, decimal_places=2)
    payment = models.CharField("Zahlung", max_length=10, choices=Payment.choices, default=Payment.CASH)
    iban = models.CharField("IBAN (bei Überweisung)", max_length=40, blank=True)

    data_erased = models.BooleanField("Daten auf dem Gerät gelöscht", default=False)
    data_erased_at = models.DateTimeField("Gelöscht am", null=True, blank=True)

    signature = models.TextField("Unterschrift (Bild)", blank=True, editable=False)
    signed_at = models.DateTimeField("Unterschrieben am", null=True, blank=True, editable=False)
    pdf = models.FileField("Vertrag (PDF)", upload_to=contract_upload, blank=True, editable=False)
    created_at = models.DateTimeField("Angelegt", auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Ankaufvertrag"
        verbose_name_plural = "Ankaufverträge"
        ordering = ["-created_at"]
        permissions = [("complete_purchasecontract", "Ankaufvertrag abschließen und unterschreiben lassen")]

    def __str__(self):
        return f"{self.number or 'Entwurf'} · {self.seller_first_name} {self.seller_last_name} · {self.device}"

    @property
    def seller_name(self):
        return f"{self.seller_first_name} {self.seller_last_name}"

    def completion_errors(self) -> list[str]:
        errs = []
        if not self.check_activation_lock_off:
            errs.append("Die Aktivierungssperre ist nicht aufgehoben. Ohne aufgehobene Sperre kein Ankauf (AGB § 14).")
        if not (self.blocklist_checked and self.blocklist_clear):
            errs.append("Die IMEI bzw. Seriennummer muss gegen Sperrlisten geprüft und als nicht gesperrt bestätigt sein.")
        if self.seller_birth_date:
            today = timezone.localdate()
            age = today.year - self.seller_birth_date.year - (
                (today.month, today.day) < (self.seller_birth_date.month, self.seller_birth_date.day)
            )
            if age < 18:
                errs.append("Der Verkäufer muss mindestens 18 Jahre alt sein (AGB § 14).")
        if self.payment == self.Payment.TRANSFER and not self.iban:
            errs.append("Für eine Überweisung fehlt die IBAN.")
        if not self.id_number:
            errs.append("Die Ausweisnummer fehlt.")
        return errs

    def save(self, *args, **kwargs):
        if not self.number:
            year = timezone.localdate().year
            last = PurchaseContract.objects.filter(number__startswith=f"AK-{year}-").order_by("-number").values_list("number", flat=True).first()
            n = int(last.rsplit("-", 1)[1]) + 1 if last else 1
            self.number = f"AK-{year}-{n:04d}"
        if self.data_erased and not self.data_erased_at:
            self.data_erased_at = timezone.now()
        super().save(*args, **kwargs)
