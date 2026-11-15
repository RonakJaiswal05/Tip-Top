"""Seed page texts, FAQ, media, workshop cards and the before/after pair from the prototype (see catalog.seed)."""
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.db import transaction

from catalog.models import RepairType
from catalog.seed import load

from .models import FAQ, BeforeAfter, ContentBlock, MediaAsset, WorkshopCard

IMG_DIR = Path(settings.REPO_DIR) / "prototype" / "img"

# Texts only the prototype needed (admin preview, image prompt tool, "saved in this browser" notes)
DROP = {
    "ad_title", "ad_sign", "ad_user", "ad_pass", "ad_demo", "ad_tabs", "ad_out", "ad_site", "ad_search", "ad_save",
    "ad_reset", "ad_saved", "ad_resetd", "ad_rep", "ad_price", "ad_pick", "ad_cat", "ad_brand", "ad_name", "ad_level",
    "levels", "ad_faceid", "ad_kind", "kinds", "ad_add", "ad_added", "ad_err", "ad_none", "ad_cols", "ad_reqs_note",
    "via_cb", "via_form", "via_wd", "q_p", "q_o", "img_btn", "img_h", "img_p", "copy", "copied_p", "attach", "real",
    "file", "proto", "proto_foot", "f_hours", "faq", "lab",
}

# Texts that change for the live site. Opening hours now come from the admin ({hours}, {t}); prototype-only wording goes.
CHANGES = {
    "de": {
        "open": "Jetzt geöffnet, bis {t} Uhr",
        "closed": "Geschlossen, öffnet {d} um {t} Uhr",
        "shops_p": "Zwei Filialen, ohne Termin. {hours}.",
        "wi_s": "Ohne Termin, {hours}",
        "lf_p": "Sag uns, was kaputt ist. Wir melden uns während der Öffnungszeiten, {hours}.",
        "ai_blocked": "Das Mikrofon ist gesperrt. Erlaube den Zugriff in deinem Browser oder tipp es einfach ein.",
    },
    "en": {
        "open": "Open now, until {t}",
        "closed": "Closed, opens {d} at {t}",
        "shops_p": "Two shops, no appointment needed. {hours}.",
        "wi_s": "No appointment, {hours}",
        "lf_p": "Tell us what's broken. We reply during opening hours, {hours}.",
        "ai_blocked": "The microphone is blocked. Allow access in your browser or just type it instead.",
    },
}

# New texts for the live site
NEW = {
    "price_note": ("Die Preise sind Platzhalter, bis die Preisliste des Shops eingespielt ist.",
                   "Prices are placeholders until the shop's price list is loaded."),
    "closed_now": ("Geschlossen", "Closed"),
    "cc_p_min": ("Wir nutzen nur notwendige Speichereinträge, damit die Seite funktioniert, etwa für deine Sprachwahl, "
                 "deine Auswahl hier und den Schutz unserer Formulare. Statistik- oder Werbedienste setzen wir nicht ein. "
                 "Du kannst deine Wahl jederzeit unter „Cookie-Einstellungen“ ändern.",
                 "We only use necessary storage so the site works, for example for your language, your choice here and to "
                 "protect our forms. We don't use any statistics or advertising services. You can change your choice any "
                 "time under “Cookie settings”."),
    "cc_p_stats": ("Wir nutzen notwendige Speichereinträge, damit die Seite funktioniert. Mit deiner Einwilligung nutzen wir außerdem "
                   "Statistik (Matomo, eigener Server). Ablehnen hat keine Nachteile, und du kannst deine Wahl jederzeit unter "
                   "„Cookie-Einstellungen“ ändern.",
                   "We use necessary storage so the site works. With your consent we also use statistics (Matomo, on our own "
                   "server). Rejecting costs you nothing, and you can change your choice any time under “Cookie settings”."),
    "cc_p_ads": ("Wir nutzen notwendige Speichereinträge, damit die Seite funktioniert. Mit deiner Einwilligung nutzen wir außerdem "
                 "Marketing (Google Ads, Meta-Pixel), wobei Daten in die USA übermittelt werden können. Ablehnen hat keine Nachteile, "
                 "und du kannst deine Wahl jederzeit unter „Cookie-Einstellungen“ ändern.",
                 "We use necessary storage so the site works. With your consent we also use marketing (Google Ads, Meta Pixel), "
                 "which can send data to the USA. Rejecting costs you nothing, and you can change your choice any time under "
                 "“Cookie settings”."),
    "err_send": ("Das hat nicht geklappt. Bitte versuch es noch einmal oder ruf uns an.",
                 "That didn't work. Please try again or give us a call."),
    "err_rate": ("Gerade kommen zu viele Anfragen von deinem Anschluss. Bitte versuch es in ein paar Minuten noch einmal oder ruf uns an.",
                 "Too many requests from your connection right now. Please try again in a few minutes or give us a call."),
    "sending": ("Wird gesendet …", "Sending…"),
    "lab_count": ("15000", "15000"),
    "all_models": ("Alle Modelle und Preise", "All models and prices"),
    "f_hours_sun": ("So geschlossen", "Sun closed"),
    "lab_go": ("Preis berechnen", "Get a price"),
    "guide": ("Richtwert für {m}: {p}", "Guide price for {m}: {p}"),
    "skip": ("Zum Inhalt springen", "Skip to content"),
    "lang_l": ("Sprache", "Language"),
    "menu": ("Menü", "Menu"),
    "nav_main": ("Hauptnavigation", "Main"),
    "bld_l": ("Reparaturpreis", "Repair price"),
    "wd_mail_err": ("Die Bestätigung konnte nicht sofort verschickt werden. Wir senden sie, sobald es geht, und melden uns.",
                    "We couldn't send the confirmation straight away. We'll send it as soon as possible and get in touch."),
}

GROUPS = [
    ("nav_", "Navigation"), ("cta", "Navigation"), ("h1", "Startseite: Kopf"), ("hero", "Startseite: Kopf"), ("stk_", "Startseite: Kopf"),
    ("pick", "Startseite: Kopf"), ("ask", "Startseite: Beschreiben"), ("mic", "Startseite: Beschreiben"), ("ai_", "Startseite: Beschreiben"),
    ("facts", "Startseite: Kopf"), ("glass", "Startseite: Kopf"), ("cat_", "Kategorien"), ("tip_", "Preisrechner"),
    ("pop_", "Startseite: Reparaturen"), ("br_", "Startseite: Marken"), ("cmp_", "Startseite: Vorher/nachher"),
    ("before", "Startseite: Vorher/nachher"), ("after", "Startseite: Vorher/nachher"), ("lab", "Startseite: Werkstatt"),
    ("sell", "Startseite: Ankauf"), ("conds", "Startseite: Ankauf"), ("wa_", "WhatsApp-Nachrichten"), ("shops", "Startseite: Filialen"),
    ("open", "Öffnungszeiten"), ("closed", "Öffnungszeiten"), ("today", "Öffnungszeiten"), ("tomorrow", "Öffnungszeiten"),
    ("days", "Öffnungszeiten"), ("ways", "Startseite: Filialen"), ("faq", "Startseite: FAQ"), ("f_", "Footer"),
    ("lf_", "Anfrageformular"), ("wheres", "Anfrageformular"), ("vias", "Anfrageformular"), ("cc_", "Cookie-Banner"),
    ("mic_", "Spracheingabe"), ("wd_", "Widerruf"), ("lg_", "Rechtstexte"), ("fine_", "Datenschutz-Hinweise"), ("lk_", "Datenschutz-Hinweise"),
    ("gmb_", "Google-Bewertungen"), ("err_", "Formulare"), ("cb_", "Preisrechner"), ("name_l", "Formulare"), ("phone_l", "Formulare"),
]

ALT = {
    "hero": ("Hände in blauen Handschuhen heben das gesprungene Display eines geöffneten Smartphones mit einem Saugnapf an",
             "Gloved hands lifting the cracked screen off an opened smartphone with a suction cup"),
    "cat-phone": ("Smartphone mit gesprungenem Display auf blauem Papier", "Smartphone with a cracked screen on blue paper"),
    "cat-tablet": ("Tablet mit gesprungenem Display auf rosa Papier", "Tablet with a cracked screen on pink paper"),
    "cat-laptop": ("Aufgeklappter Laptop mit gesprungenem Bildschirm auf grünem Papier", "Opened laptop with a cracked screen on green paper"),
    "cat-console": ("Spielkonsole und Controller auf orangem Papier", "Games console and controller on orange paper"),
    "rep-display": ("Smartphone mit zersplittertem Display neben einem neuen Ersatzdisplay", "Smartphone with a shattered screen next to a new replacement screen"),
    "rep-battery": ("Geöffnetes Smartphone, der alte Akku wird herausgenommen", "Opened smartphone with the old battery being lifted out"),
    "rep-port": ("Die Ladebuchse eines Smartphones wird mit einem Pinsel gereinigt", "A smartphone's charging port being cleaned with a brush"),
    "rep-back": ("Smartphone mit stark gesprungener Glasrückseite", "Smartphone with a badly cracked glass back"),
    "rep-camera": ("Kameramodul eines Smartphones in einer Pinzette", "A smartphone camera module held in tweezers"),
    "rep-water": ("Nasses, geöffnetes Smartphone, die Platine liegt im Ultraschallreiniger", "Wet opened smartphone with its board in an ultrasonic cleaner"),
    "before": ("Vorher: Smartphone mit zersplittertem Display", "Before: smartphone with a shattered screen"),
    "after": ("Nachher: dasselbe Smartphone mit neuem, unbeschädigtem Display", "After: the same smartphone with a new, undamaged screen"),
    "lab-solder": ("Techniker lötet unter dem Mikroskop an einer Platine", "Technician micro-soldering a board under the microscope"),
    "lab-ic": ("Heißluftdüse über einer Smartphone-Platine, eine Pinzette hebt einen Chip an", "Hot-air nozzle over a phone board while tweezers lift a chip"),
    "lab-water": ("Korrodierte Platine wird mit Pinsel und Isopropanol gereinigt", "Corroded board being cleaned with a brush and isopropyl alcohol"),
    "lab-data": ("Speicherchip auf einem Programmieradapter zur Datenrettung", "Memory chip on a programmer adapter for data recovery"),
    "sell": ("Gebrauchte Smartphones, Tablet und Controller auf farbigem Papier", "Used phones, a tablet and a controller on coloured paper"),
}
DECORATIVE = {"hero", "cat-phone", "cat-tablet", "cat-laptop", "cat-console", "rep-display", "rep-battery", "rep-port",
              "rep-back", "rep-camera", "rep-water", "sell", "lab-solder", "lab-ic", "lab-water", "lab-data"}
REP_IMG = {"display": "rep-display", "battery": "rep-battery", "port": "rep-port", "back": "rep-back", "camera": "rep-camera",
           "water": "rep-water", "cport": "rep-port"}
LAB = [("lab-solder", "mainboard"), ("lab-ic", "mainboard"), ("lab-water", "water"), ("lab-data", "data")]


def group_of(key: str) -> str:
    for prefix, g in GROUPS:
        if key.startswith(prefix):
            return g
    return "Preisrechner"


def texts_from_prototype() -> dict[str, tuple]:
    d = load()
    T = d["T"]
    out = {}
    for key in T["de"]:
        if key in DROP:
            continue
        de, en = CHANGES["de"].get(key, T["de"][key]), CHANGES["en"].get(key, T["en"][key])
        out[key] = (de, en)
    for key, (de, en) in NEW.items():
        out[key] = (de, en)
    return out


@transaction.atomic
def seed_texts(overwrite: bool = False) -> int:
    n = 0
    for key, (de, en) in texts_from_prototype().items():
        fmt, raw_de = ContentBlock.serialise(de)
        _, raw_en = ContentBlock.serialise(en)
        obj = ContentBlock.objects.filter(key=key).first()
        if obj and not overwrite:
            continue
        ContentBlock.objects.update_or_create(key=key, defaults=dict(format=fmt, text_de=raw_de, text_en=raw_en, group=group_of(key)))
        n += 1
    return n


def seed_faq() -> int:
    if FAQ.objects.exists():
        return 0
    T = load()["T"]
    for i, ((qd, ad), (qe, ae)) in enumerate(zip(T["de"]["faq"], T["en"]["faq"])):
        FAQ.objects.create(question_de=qd, answer_de=ad, question_en=qe, answer_en=ae, order=i)
    return len(T["de"]["faq"])


def seed_media(log=print) -> int:
    n = 0
    for m in load()["IMGS"]:
        key = m["id"]
        src = IMG_DIR / f"{key}.jpg"
        if not src.is_file() or MediaAsset.objects.filter(key=key).exists():
            continue
        alt_de, alt_en = ALT.get(key, ("", ""))
        asset = MediaAsset(key=key, title=m["name"], alt_de=alt_de, alt_en=alt_en, decorative=key in DECORATIVE,
                           generated=True, published=bool(alt_de and alt_en))
        with src.open("rb") as fh:
            asset.image.save(f"{key}.jpg", File(fh), save=False)
        asset.save()
        n += 1
        log(f"  image {key}: {asset.variants.get('w')}×{asset.variants.get('h')}")
    for rkey, mkey in REP_IMG.items():
        RepairType.objects.filter(key=rkey, image__isnull=True).update(image=MediaAsset.objects.filter(key=mkey).first())
    return n


def seed_workshop() -> int:
    if WorkshopCard.objects.exists():
        return 0
    T = load()["T"]
    for i, ((td, xd), (te, xe)) in enumerate(zip(T["de"]["lab"], T["en"]["lab"])):
        img, rep = LAB[i]
        WorkshopCard.objects.create(image=MediaAsset.objects.get(key=img), title_de=td, text_de=xd, title_en=te, text_en=xe,
                                    repair=RepairType.objects.filter(key=rep).first(), order=i)
    return 4


def seed_before_after() -> int:
    if BeforeAfter.objects.exists():
        return 0
    b, a = MediaAsset.objects.filter(key="before").first(), MediaAsset.objects.filter(key="after").first()
    if b and a:
        BeforeAfter.objects.create(before=b, after=a)
        return 1
    return 0
