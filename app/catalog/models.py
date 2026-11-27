"""Catalogue: categories, brands, device models, repair types and prices (A3 to A5)."""
import math
import re
import unicodedata
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from simple_history.models import HistoricalRecords


def slugify_de(value: str) -> str:
    """The prototype's slug() rule (strip accents, lower case, other characters become '-'), except that '+' becomes
    'plus': the prototype gave "Galaxy S26" and "Galaxy S26+" the same id."""
    s = unicodedata.normalize("NFD", value.lower().replace("+", " plus "))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


class Category(models.Model):
    key = models.SlugField("Schlüssel", max_length=20, unique=True)
    name_de = models.CharField("Name (Deutsch)", max_length=60)
    name_en = models.CharField("Name (Englisch)", max_length=60)
    subtitle_de = models.CharField("Untertitel (Deutsch)", max_length=120, blank=True)
    subtitle_en = models.CharField("Untertitel (Englisch)", max_length=120, blank=True)
    tip_de = models.CharField("Tipp zum Modell (Deutsch)", max_length=200, blank=True)
    tip_en = models.CharField("Tipp zum Modell (Englisch)", max_length=200, blank=True)
    order = models.PositiveSmallIntegerField("Reihenfolge", default=0)

    class Meta:
        verbose_name = "Kategorie"
        verbose_name_plural = "Kategorien"
        ordering = ["order"]

    def __str__(self):
        return self.name_de

    def name(self, lang="de"):
        return self.name_en if lang == "en" else self.name_de


def _logo_ext(f):
    FileExtensionValidator(["svg", "png", "webp"])(f)


class Brand(models.Model):
    name = models.CharField("Marke", max_length=60, unique=True)
    slug = models.SlugField(max_length=60, unique=True)
    logo = models.FileField(
        "Logo", upload_to="brands/", blank=True, validators=[_logo_ext],
        help_text="Offizielle Logodatei des Herstellers (SVG bevorzugt, sonst PNG). Bitte keine nachgezeichneten Logos. "
                  "Ohne Logo zeigt die Website den Namen.",
    )
    logo_is_wordmark = models.BooleanField(
        "Logo zeigt den Namen", default=False,
        help_text="Das Logo ist ein Schriftzug (z. B. SAMSUNG, SONY). Im Markenschrank steht der Name dann nicht noch einmal daneben.",
    )
    order = models.PositiveSmallIntegerField("Reihenfolge", default=0)
    active = models.BooleanField("Aktiv", default=True)

    class Meta:
        verbose_name = "Marke"
        verbose_name_plural = "Marken"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_de(self.name)
        super().save(*args, **kwargs)


class RepairType(models.Model):
    key = models.SlugField(
        "Schlüssel", max_length=30, unique=True, blank=True,
        help_text="Technischer Name. Wird beim Anlegen aus dem Namen gebildet, danach nicht mehr ändern.",
    )
    name_de = models.CharField("Name (Deutsch)", max_length=80)
    name_en = models.CharField("Name (Englisch)", max_length=80)
    desc_de = models.CharField("Kurzbeschreibung (Deutsch)", max_length=200, blank=True)
    desc_en = models.CharField("Kurzbeschreibung (Englisch)", max_length=200, blank=True)
    icon = models.CharField("Symbol", max_length=30, blank=True, help_text="Symbolname, z. B. display oder battery.")
    image = models.ForeignKey(
        "content.MediaAsset", verbose_name="Foto", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    duration_minutes = models.PositiveIntegerField("Übliche Dauer (Minuten)", null=True, blank=True)
    warranty_months = models.PositiveSmallIntegerField("Garantie (Monate)", null=True, blank=True)
    has_tiers = models.BooleanField(
        "Premium und Original", default=False,
        help_text="Zwei Preise: Premium-Teil und Original-Teil. Beim Ausschalten wird der Premium-Preis zum einzigen Preis, "
                  "beim Einschalten gelten bisherige Preise für beide Teile, bis Sie sie ändern.",
    )
    fixed_price = models.BooleanField(
        "Einheitspreis", default=False,
        help_text="Gleicher Preis für alle Modelle einer Kategorie (Grundpreis). Pro Modell überschreibbar.",
    )
    default_from = models.BooleanField("Standardmäßig „ab“-Preis", default=False)
    price_weight = models.DecimalField(
        "Gewicht für Startpreise", max_digits=4, decimal_places=2, default=Decimal("0.50"),
        help_text="Wie stark die Preisstufe eines neuen Modells diesen Preis beeinflusst (0 = gar nicht, 1 = voll).",
    )
    order = models.PositiveSmallIntegerField("Reihenfolge", default=0)

    class Meta:
        verbose_name = "Reparaturart"
        verbose_name_plural = "Reparaturarten"
        ordering = ["order", "key"]

    def __str__(self):
        return self.name_de

    def save(self, *args, **kwargs):
        if not self.key:
            base, n = slugify_de(self.name_de)[:26] or "reparatur", 2
            self.key = base
            while RepairType.objects.filter(key=self.key).exclude(pk=self.pk).exists():
                self.key, n = f"{base}-{n}", n + 1
        old = RepairType.objects.filter(pk=self.pk).values_list("has_tiers", flat=True).first() if self.pk else None
        super().save(*args, **kwargs)
        if old is not None and old != self.has_tiers:
            self.switch_tiers()

    def switch_tiers(self) -> int:
        """Bring the stored prices in line with has_tiers (admin wish, 27 Nov 2026: "battery with one price").
        Off: the Premium price (or, without one, the Original price) becomes the single price. On: the single price is
        copied to Premium and Original. Model prices and base prices; the price history records the change."""
        reason = "Premium/Original " + ("eingeschaltet" if self.has_tiers else "ausgeschaltet")
        changed = 0
        for Model, key in ((Price, "model_id"), (CategoryPrice, "category_id")):
            rows = Model.objects.filter(repair=self)
            groups = {}
            for p in rows:
                groups.setdefault(getattr(p, key), {})[p.tier] = p
            for owner, tiers in groups.items():
                if self.has_tiers and Tier.STANDARD in tiers:
                    std = tiers[Tier.STANDARD]
                    for t in (Tier.PREMIUM, Tier.ORIGINAL):
                        if t not in tiers:
                            new = Model(**{key: owner}, repair=self, tier=t, amount=std.amount,
                                        **({"is_from": std.is_from, "source": std.source} if Model is Price else {}))
                            new._change_reason = reason
                            new.save()
                    std._change_reason = reason
                    std.delete()
                    changed += 1
                elif not self.has_tiers and (Tier.PREMIUM in tiers or Tier.ORIGINAL in tiers):
                    keep = tiers.get(Tier.PREMIUM) or tiers.get(Tier.ORIGINAL)
                    std = tiers.get(Tier.STANDARD) or Model(**{key: owner}, repair=self, tier=Tier.STANDARD)
                    std.amount = keep.amount
                    if Model is Price:
                        std.is_from, std.source = keep.is_from, keep.source
                    std._change_reason = reason
                    std.save()
                    for t in (Tier.PREMIUM, Tier.ORIGINAL):
                        if t in tiers:
                            tiers[t]._change_reason = reason
                            tiers[t].delete()
                    changed += 1
        return changed


class RepairName(models.Model):
    """Per device type names, e.g. 'Ladebuchse / DC-Buchse' for laptops."""

    repair = models.ForeignKey(RepairType, on_delete=models.CASCADE, related_name="names")
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name_de = models.CharField("Name (Deutsch)", max_length=80)
    name_en = models.CharField("Name (Englisch)", max_length=80)

    class Meta:
        verbose_name = "Name je Kategorie"
        verbose_name_plural = "Namen je Kategorie"
        unique_together = [("repair", "category")]

    def __str__(self):
        return f"{self.repair.key} ({self.category.key})"


class ConsoleType(models.TextChoices):
    DISC = "B", "Konsole mit Laufwerk"
    DIGITAL = "b", "Konsole ohne Laufwerk"
    HANDHELD = "H", "Handheld"
    CONTROLLER = "P", "Controller"


class RepairOption(models.Model):
    """Which repairs a device can get, in calculator order. Consoles have one list per console type."""

    class Requires(models.TextChoices):
        NONE = "", "Immer"
        FACE_ID = "face_id", "Nur mit Face ID"
        TOUCH_ID = "touch_id", "Nur mit Touch ID"
        JACK = "jack", "Nur mit Kopfhörerbuchse"

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="options")
    console_type = models.CharField("Konsolentyp", max_length=1, blank=True, choices=ConsoleType.choices)
    repair = models.ForeignKey(RepairType, on_delete=models.CASCADE, related_name="options")
    order = models.PositiveSmallIntegerField("Reihenfolge", default=0)
    requires = models.CharField("Bedingung", max_length=10, blank=True, choices=Requires.choices)

    class Meta:
        verbose_name = "Reparatur in Liste"
        verbose_name_plural = "Reparaturlisten"
        ordering = ["category__order", "console_type", "order"]
        unique_together = [("category", "console_type", "repair")]

    def __str__(self):
        return f"{self.category.key}{('/' + self.console_type) if self.console_type else ''}: {self.repair.key}"


class FeaturedRepair(models.Model):
    """The large photo cards: first six in the calculator and, for phones, on the home page (F5)."""

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="featured")
    repair = models.ForeignKey(RepairType, on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField("Reihenfolge", default=0)

    class Meta:
        verbose_name = "Hervorgehobene Reparatur"
        verbose_name_plural = "Hervorgehobene Reparaturen"
        ordering = ["category__order", "order"]
        unique_together = [("category", "repair")]

    def __str__(self):
        return f"{self.category.key}: {self.repair.key}"


class PriceLevel(models.TextChoices):
    BUDGET = "budget", "Einsteiger"
    STANDARD = "standard", "Standard"
    PREMIUM = "premium", "Premium"
    FLAGSHIP = "flagship", "Flaggschiff"


LEVEL_FACTORS = {"budget": Decimal("0.6"), "standard": Decimal("1"), "premium": Decimal("1.6"), "flagship": Decimal("2.2")}


class DeviceModel(models.Model):
    category = models.ForeignKey(Category, verbose_name="Kategorie", on_delete=models.PROTECT, related_name="models")
    brand = models.ForeignKey(Brand, verbose_name="Marke", on_delete=models.PROTECT, related_name="models")
    name = models.CharField("Modellname", max_length=80, help_text="Ohne Marke, z. B. „iPhone 13“ oder „Galaxy S23“.")
    slug = models.SlugField("URL-Name", max_length=120, unique=True, help_text="Wird automatisch erzeugt, z. B. apple-iphone-13.")
    legacy_key = models.CharField(max_length=120, unique=True, null=True, blank=True, editable=False)
    release_year = models.PositiveSmallIntegerField("Erscheinungsjahr", null=True, blank=True)
    price_level = models.CharField("Preisstufe", max_length=10, choices=PriceLevel.choices, blank=True)
    price_factor = models.DecimalField(
        "Preisfaktor", max_digits=4, decimal_places=2, default=Decimal("1.00"),
        help_text="Für Startpreise neuer Modelle. Wird aus der Preisstufe gesetzt.",
    )
    popular = models.BooleanField("Beliebt", default=False, help_text="Erscheint im Rechner unter „Beliebt“.")
    has_face_id = models.BooleanField("Hat Face ID", default=False)
    has_touch_id = models.BooleanField("Hat Touch ID", default=False, help_text="Fingerabdrucksensor (Home-Taste oder Seitentaste).")
    has_headphone_jack = models.BooleanField("Hat Kopfhörerbuchse", default=False)
    console_type = models.CharField("Konsolentyp", max_length=1, blank=True, choices=ConsoleType.choices)
    excluded_repairs = models.ManyToManyField(
        RepairType, verbose_name="Nicht möglich", blank=True, related_name="+",
        help_text="Reparaturen, die es bei diesem Gerät nicht gibt (z. B. kein Lüfter, fest verlöteter Speicher, "
                  "Batterien statt Akku). Sie erscheinen weder im Rechner noch auf der Modellseite.",
    )
    extra_repairs = models.ManyToManyField(
        RepairType, verbose_name="Zusätzlich", blank=True, related_name="+",
        help_text="Reparaturen, die für diese Geräteart sonst nicht angeboten werden, bei diesem Gerät aber schon.",
    )
    photo = models.ImageField("Foto", upload_to="models/", blank=True)
    active = models.BooleanField(
        "Aktiv", default=True, help_text="Ausschalten, wenn das Modell nicht mehr repariert wird. Die Historie bleibt erhalten."
    )
    sort_order = models.IntegerField("Sortierung", default=0, help_text="Kleiner = weiter oben. Neue Modelle stehen oben.")
    merged_into = models.ForeignKey(
        "self", verbose_name="Zusammengeführt in", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Gerät"
        verbose_name_plural = "Geräte"
        ordering = ["category__order", "brand__order", "sort_order", "name"]
        unique_together = [("category", "brand", "name")]

    def __str__(self):
        return self.full_name("de")

    def clean(self):
        if self.category_id and self.category.key == "console" and not self.console_type:
            raise ValidationError({"console_type": "Bitte den Konsolentyp wählen."})
        if self.category_id and self.category.key != "console":
            self.console_type = ""

    def save(self, *args, **kwargs):
        keep_factor = kwargs.pop("keep_factor", False)
        if self.price_level in LEVEL_FACTORS and not keep_factor and self._state.adding:
            self.price_factor = LEVEL_FACTORS[self.price_level]
        if not self.slug:
            self.slug = self.make_slug()
        super().save(*args, **kwargs)

    def make_slug(self) -> str:
        base = self.name if self.name.lower().startswith(self.brand.name.lower()) else f"{self.brand.name} {self.name}"
        slug = slugify_de(base)
        if DeviceModel.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = slugify_de(f"{base} {self.category.key}")
        return slug

    def base_name(self, lang="de") -> str:
        """The model name without brand, localised like the prototype's locName()."""
        n = self.name
        if lang == "de":
            n = re.sub(r"\((\d+)(st|nd|rd|th) gen\)", r"(\1. Gen.)", n)
            n = re.sub(r" controller$", " Controller", n)
        return n

    def full_name(self, lang="de") -> str:
        n = self.name if self.name.lower().startswith(self.brand.name.lower()) else f"{self.brand.name} {self.name}"
        if lang == "de":
            n = re.sub(r"\((\d+)(st|nd|rd|th) gen\)", r"(\1. Gen.)", n)
            n = re.sub(r" controller$", " Controller", n)
        return n

    def flags(self) -> str:
        """Prototype flag string: F = Face ID, T = Touch ID, J = headphone jack, B/b/H/P console type, p = popular."""
        return ("F" if self.has_face_id else "") + ("T" if self.has_touch_id else "") + ("J" if self.has_headphone_jack else "") + (self.console_type or "") + (
            "p" if self.popular else ""
        )


class Tier(models.TextChoices):
    STANDARD = "standard", "Standard"
    PREMIUM = "premium", "Premium"
    ORIGINAL = "original", "Original"


class PriceSource(models.TextChoices):
    PLACEHOLDER = "placeholder", "Platzhalter (Prototyp)"
    WEBSITE = "website", "Preis von der bisherigen Website"
    LEVEL = "level", "Startpreis aus Preisstufe"
    IMPORT = "import", "Preisliste importiert"
    ADMIN = "admin", "Im Admin geändert"
    SCHEDULED = "scheduled", "Geplante Änderung"


def r9(x: float) -> int:
    """Round to the nearest ten minus one, at least 19 (the prototype's r9: Math.round(x / 10) * 10 - 1)."""
    return max(19, math.floor(x / 10 + 0.5) * 10 - 1)


def starting_price(base: float, factor: float, weight: float) -> int:
    """Starting price for a new model from its category's base price (the prototype's price formula)."""
    return r9(base * math.pow(factor, weight))


class CategoryPrice(models.Model):
    """Base price per category and repair (the prototype's BASE).

    For repairs with a single price for all models (diagnosis, water damage check, data recovery, software) this is
    the price itself; a model can override it with its own Price row. For all other repairs it is the starting point
    when a new model is added with a price level.
    """

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="base_prices")
    repair = models.ForeignKey(RepairType, on_delete=models.CASCADE)
    tier = models.CharField("Teil", max_length=10, choices=Tier.choices, default=Tier.STANDARD)
    amount = models.DecimalField("Preis (€)", max_digits=8, decimal_places=2)
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Grundpreis"
        verbose_name_plural = "Grundpreise"
        unique_together = [("category", "repair", "tier")]
        ordering = ["category__order", "repair__order", "tier"]

    def __str__(self):
        return f"{self.category.key} {self.repair.key} {self.tier}: {self.amount}"


class Price(models.Model):
    model = models.ForeignKey(DeviceModel, verbose_name="Gerät", on_delete=models.CASCADE, related_name="prices")
    repair = models.ForeignKey(RepairType, verbose_name="Reparatur", on_delete=models.CASCADE, related_name="prices")
    tier = models.CharField("Teil", max_length=10, choices=Tier.choices, default=Tier.STANDARD)
    amount = models.DecimalField("Preis (€)", max_digits=8, decimal_places=2)
    is_from = models.BooleanField("„ab“-Preis", default=False)
    source = models.CharField("Herkunft", max_length=12, choices=PriceSource.choices, default=PriceSource.ADMIN)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Preis"
        verbose_name_plural = "Preise"
        unique_together = [("model", "repair", "tier")]
        ordering = ["model", "repair__order", "tier"]
        indexes = [models.Index(fields=["repair", "tier"])]

    def __str__(self):
        return f"{self.model} · {self.repair.name_de} ({self.get_tier_display()}): {self.amount} €"


class ScheduledPriceChange(models.Model):
    """A price that takes effect at a future date and time (A3). Applied every minute by Celery beat."""

    model = models.ForeignKey(DeviceModel, verbose_name="Gerät", on_delete=models.CASCADE, related_name="scheduled_prices")
    repair = models.ForeignKey(RepairType, verbose_name="Reparatur", on_delete=models.CASCADE)
    tier = models.CharField("Teil", max_length=10, choices=Tier.choices, default=Tier.STANDARD)
    amount = models.DecimalField("Neuer Preis (€)", max_digits=8, decimal_places=2)
    is_from = models.BooleanField("„ab“-Preis", default=False)
    effective_at = models.DateTimeField("Gültig ab")
    applied_at = models.DateTimeField("Angewendet am", null=True, blank=True, editable=False)
    note = models.CharField("Notiz", max_length=200, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Geplante Preisänderung"
        verbose_name_plural = "Geplante Preisänderungen"
        ordering = ["applied_at", "effective_at"]

    def __str__(self):
        return f"{self.model} · {self.repair.name_de}: {self.amount} € ab {self.effective_at:%d.%m.%Y %H:%M}"


class BuybackPrice(models.Model):
    """Guide price range for buying a device (F9: offer ranges per model and condition)."""

    class Condition(models.IntegerChoices):
        LIKE_NEW = 0, "Wie neu"
        GOOD = 1, "Gut"
        WORN = 2, "Abgenutzt"
        BROKEN = 3, "Defekt"

    model = models.ForeignKey(DeviceModel, verbose_name="Gerät", on_delete=models.CASCADE, related_name="buyback")
    condition = models.PositiveSmallIntegerField("Zustand", choices=Condition.choices)
    low = models.DecimalField("Von (€)", max_digits=8, decimal_places=2)
    high = models.DecimalField("Bis (€)", max_digits=8, decimal_places=2)

    class Meta:
        verbose_name = "Ankaufpreis"
        verbose_name_plural = "Ankaufpreise"
        unique_together = [("model", "condition")]
        ordering = ["model", "condition"]

    def clean(self):
        if self.low is not None and self.high is not None and self.low > self.high:
            raise ValidationError("„Von“ darf nicht größer als „Bis“ sein.")

    def __str__(self):
        return f"{self.model} {self.get_condition_display()}: {self.low}–{self.high} €"


class CabinetDrawer(models.Model):
    """A drawer in the brand cabinet on the home page (F6). Opens the calculator on that brand's models."""

    class Group(models.TextChoices):
        PHONE = "phone", "Handys und Tablets"
        LAPTOP = "laptop", "Laptops"
        CONSOLE = "console", "Konsolen"

    group = models.CharField("Schrank", max_length=10, choices=Group.choices)
    label = models.CharField("Beschriftung", max_length=60, help_text="z. B. iPad, Galaxy Tab, PlayStation")
    category = models.ForeignKey(Category, verbose_name="Kategorie", on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, verbose_name="Marke", on_delete=models.CASCADE)
    logo = models.FileField(
        "Eigenes Logo", upload_to="brands/", blank=True, validators=[_logo_ext],
        help_text="Nur für Untermarken mit eigenem Logo (PlayStation, Xbox, Steam Deck). Sonst wird das Logo der Marke verwendet.",
    )
    use_brand_logo = models.BooleanField("Logo der Marke verwenden", default=True)
    order = models.PositiveSmallIntegerField("Reihenfolge", default=0)
    active = models.BooleanField("Sichtbar", default=True)

    class Meta:
        verbose_name = "Schublade (Markenschrank)"
        verbose_name_plural = "Markenschrank"
        ordering = ["group", "order"]

    def __str__(self):
        return self.label

    @property
    def logo_file(self):
        if self.logo:
            return self.logo
        if self.use_brand_logo and self.brand.logo:
            return self.brand.logo
        return None
