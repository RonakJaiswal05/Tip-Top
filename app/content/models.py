"""Page texts, FAQ, media library, before-and-after pairs and workshop cards (A9, A10)."""
import hashlib
import io
import json

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import models
from PIL import Image, ImageOps


class ContentBlock(models.Model):
    """One text of the website in German and English. The key is what the templates and scripts look up."""

    class Format(models.TextChoices):
        TEXT = "text", "Text"
        LINES = "lines", "Liste (eine Zeile pro Eintrag)"
        ROWS = "rows", "Tabelle (eine Zeile pro Eintrag, Spalten mit | trennen)"
        JSON = "json", "Strukturiert (JSON)"

    key = models.CharField("Schlüssel", max_length=40, unique=True)
    group = models.CharField("Bereich", max_length=40, blank=True)
    format = models.CharField("Format", max_length=6, choices=Format.choices, default=Format.TEXT)
    text_de = models.TextField("Deutsch")
    text_en = models.TextField("Englisch")
    note = models.CharField("Wo erscheint der Text?", max_length=200, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Seitentext"
        verbose_name_plural = "Seitentexte"
        ordering = ["group", "key"]

    def __str__(self):
        return self.key

    def clean(self):
        for lang in ("de", "en"):
            try:
                self.parse(getattr(self, f"text_{lang}"))
            except ValueError as e:
                raise ValidationError({f"text_{lang}": str(e)})

    def parse(self, raw: str):
        if self.format == self.Format.LINES:
            return [x.strip() for x in raw.splitlines() if x.strip()]
        if self.format == self.Format.ROWS:
            return [[c.strip() for c in x.split("|")] for x in raw.splitlines() if x.strip()]
        if self.format == self.Format.JSON:
            try:
                return json.loads(raw)
            except json.JSONDecodeError as e:
                raise ValueError(f"Kein gültiges JSON: {e}")
        return raw

    def value(self, lang: str):
        return self.parse(self.text_en if lang == "en" else self.text_de)

    @staticmethod
    def serialise(value) -> tuple[str, str]:
        """(format, raw text) for a value from the prototype's dictionary."""
        if isinstance(value, str):
            return ContentBlock.Format.TEXT, value
        if isinstance(value, list) and all(isinstance(x, str) for x in value):
            return ContentBlock.Format.LINES, "\n".join(value)
        if isinstance(value, list) and all(isinstance(x, list) and all(isinstance(c, str) for c in x) for x in value):
            return ContentBlock.Format.ROWS, "\n".join(" | ".join(x) for x in value)
        return ContentBlock.Format.JSON, json.dumps(value, ensure_ascii=False, indent=1)


class FAQ(models.Model):
    question_de = models.CharField("Frage (Deutsch)", max_length=200)
    answer_de = models.TextField("Antwort (Deutsch)")
    question_en = models.CharField("Frage (Englisch)", max_length=200)
    answer_en = models.TextField("Antwort (Englisch)")
    order = models.PositiveSmallIntegerField("Reihenfolge", default=0)
    active = models.BooleanField("Sichtbar", default=True)

    class Meta:
        verbose_name = "Frage (FAQ)"
        verbose_name_plural = "Häufige Fragen"
        ordering = ["order", "id"]

    def __str__(self):
        return self.question_de

    def q(self, lang):
        return self.question_en if lang == "en" else self.question_de

    def a(self, lang):
        return self.answer_en if lang == "en" else self.answer_de


SIZES = {"s": 760, "l": 1600}
QUALITY = {"jpg": 82, "webp": 80, "avif": 55}


class MediaAsset(models.Model):
    """A photo uploaded once; phone and desktop sizes in AVIF, WebP and JPEG are made automatically (A10)."""

    key = models.SlugField(
        "Schlüssel", max_length=60, unique=True,
        help_text="Wo das Bild verwendet wird, z. B. hero, cat-phone, rep-display. Für neue Bilder frei wählbar.",
    )
    title = models.CharField("Titel", max_length=120, blank=True)
    image = models.ImageField("Bild (Original)", upload_to="uploads/", width_field="width", height_field="height")
    width = models.PositiveIntegerField(editable=False, null=True)
    height = models.PositiveIntegerField(editable=False, null=True)
    alt_de = models.CharField("Alternativtext (Deutsch)", max_length=200, blank=True)
    alt_en = models.CharField("Alternativtext (Englisch)", max_length=200, blank=True)
    focus_x = models.PositiveSmallIntegerField("Fokus horizontal (%)", default=50, help_text="0 = links, 100 = rechts")
    focus_y = models.PositiveSmallIntegerField("Fokus vertikal (%)", default=50, help_text="0 = oben, 100 = unten")
    published = models.BooleanField(
        "Veröffentlicht", default=True, help_text="Nur mit Alternativtext auf Deutsch und Englisch möglich."
    )
    decorative = models.BooleanField(
        "Rein dekorativ", default=False,
        help_text="Für Screenreader ausgeblendet (z. B. Hintergrundbilder neben einem Text, der dasselbe sagt).",
    )
    generated = models.BooleanField("KI-generiert", default=False, help_text="Platzhalterbild, durch echte Fotos ersetzen.")
    variants = models.JSONField(default=dict, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Bild"
        verbose_name_plural = "Mediathek"
        ordering = ["key"]

    def __str__(self):
        return self.title or self.key

    def clean(self):
        if self.published and not (self.alt_de.strip() and self.alt_en.strip()):
            raise ValidationError("Vor dem Veröffentlichen bitte den Alternativtext auf Deutsch und Englisch eintragen.")
        for f in ("focus_x", "focus_y"):
            if getattr(self, f) > 100:
                raise ValidationError({f: "Bitte einen Wert zwischen 0 und 100 eintragen."})

    def alt(self, lang):
        return "" if self.decorative else (self.alt_en if lang == "en" else self.alt_de)

    def save(self, *args, **kwargs):
        regenerate = kwargs.pop("regenerate", False)
        changed = regenerate or not self.variants
        if self.pk and not changed:
            old = MediaAsset.objects.filter(pk=self.pk).values_list("image", flat=True).first()
            changed = old != self.image.name
        super().save(*args, **kwargs)
        if changed and self.image:
            self.make_variants()
            MediaAsset.objects.filter(pk=self.pk).update(variants=self.variants)

    def make_variants(self):
        self.image.open("rb")
        data = self.image.read()
        digest = hashlib.sha1(data).hexdigest()[:8]
        src = ImageOps.exif_transpose(Image.open(io.BytesIO(data)))
        if src.mode not in ("RGB", "L"):
            bg = Image.new("RGB", src.size, (255, 255, 255))
            bg.paste(src, mask=src.convert("RGBA").split()[-1])
            src = bg
        src = src.convert("RGB")
        out = {"w": src.width, "h": src.height}
        for size, max_w in SIZES.items():
            w = min(max_w, src.width)
            h = round(src.height * w / src.width)
            im = src if w == src.width else src.resize((w, h), Image.LANCZOS)
            entry = {"w": w, "h": h}
            for fmt in ("avif", "webp", "jpg"):
                buf = io.BytesIO()
                if fmt == "jpg":
                    im.save(buf, "JPEG", quality=QUALITY[fmt], optimize=True, progressive=True)
                elif fmt == "webp":
                    im.save(buf, "WEBP", quality=QUALITY[fmt], method=5)
                else:
                    im.save(buf, "AVIF", quality=QUALITY[fmt], speed=8)
                name = f"img/{self.key}.{digest}-{size}.{fmt}"
                if default_storage.exists(name):
                    default_storage.delete(name)
                entry[fmt] = default_storage.save(name, ContentFile(buf.getvalue()))
            out[size] = entry
        self.variants = out

    def urls(self) -> dict:
        """Public URLs per size and format, for templates and the page data."""
        v = self.variants or {}
        res = {"w": v.get("w"), "h": v.get("h"), "fx": self.focus_x, "fy": self.focus_y}
        for size in SIZES:
            if size in v:
                res[size] = {"w": v[size]["w"], **{f: default_storage.url(v[size][f]) for f in ("avif", "webp", "jpg") if f in v[size]}}
        return res


class BeforeAfter(models.Model):
    before = models.ForeignKey(MediaAsset, verbose_name="Vorher", on_delete=models.PROTECT, related_name="+")
    after = models.ForeignKey(MediaAsset, verbose_name="Nachher", on_delete=models.PROTECT, related_name="+")
    order = models.PositiveSmallIntegerField("Reihenfolge", default=0)
    active = models.BooleanField("Sichtbar", default=True)

    class Meta:
        verbose_name = "Vorher-nachher-Paar"
        verbose_name_plural = "Vorher-nachher-Paare"
        ordering = ["order"]

    def __str__(self):
        return f"{self.before.key} / {self.after.key}"


class WorkshopCard(models.Model):
    image = models.ForeignKey(MediaAsset, verbose_name="Foto", on_delete=models.PROTECT, related_name="+")
    title_de = models.CharField("Titel (Deutsch)", max_length=80)
    title_en = models.CharField("Titel (Englisch)", max_length=80)
    text_de = models.CharField("Text (Deutsch)", max_length=200)
    text_en = models.CharField("Text (Englisch)", max_length=200)
    repair = models.ForeignKey(
        "catalog.RepairType", verbose_name="Öffnet im Rechner", null=True, blank=True, on_delete=models.SET_NULL,
        help_text="Diese Reparatur ist im Preisrechner vorausgewählt, wenn man auf die Karte tippt.",
    )
    order = models.PositiveSmallIntegerField("Reihenfolge", default=0)
    active = models.BooleanField("Sichtbar", default=True)

    class Meta:
        verbose_name = "Werkstatt-Karte"
        verbose_name_plural = "Werkstatt-Karten"
        ordering = ["order"]

    def __str__(self):
        return self.title_de

    def title(self, lang):
        return self.title_en if lang == "en" else self.title_de

    def text(self, lang):
        return self.text_en if lang == "en" else self.text_de
