"""Everything the site stores on a visitor's device, per consent category (cookie settings dialog and cookie policy).

From the prototype's COOKIES table, updated for the live system: tt-lang is now a cookie (the server needs it to send
"/" to the remembered language), and the prototype-only entries (tt-reqs, tt-ovr, tt-added) are gone. Statistics and
marketing rows only appear while those services are switched on in the settings.
"""

COOKIES = {
    "de": {
        "necessary": [
            ["tt-consent", "TipTop (lokaler Speicher)", "Speichert deine Cookie-Auswahl, die Version dieses Hinweises, den Zeitpunkt und eine zufällige Kennung als Nachweis.", "12 Monate"],
            ["tt-lang", "TipTop (Cookie)", "Merkt sich, ob du die Seite auf Deutsch oder Englisch sehen möchtest.", "1 Jahr"],
            ["tt-mic-ok", "TipTop (lokaler Speicher)", "Merkt sich, dass du den Hinweis zur Spracheingabe bestätigt hast.", "bis du ihn löschst"],
            ["csrftoken", "TipTop (Cookie)", "Schützt Formulare davor, von fremden Seiten abgeschickt zu werden.", "1 Jahr"],
            ["sessionid", "TipTop (Cookie)", "Hält Mitarbeitende im Admin-Bereich angemeldet. Wird für Besucher nicht gesetzt.", "2 Wochen"],
        ],
        "stats": [
            ["_pk_id.*", "Matomo, eigener Server", "Unterscheidet Besuche, ohne dich zu identifizieren. IP-Adresse wird gekürzt.", "13 Monate"],
            ["_pk_ses.*", "Matomo, eigener Server", "Fasst Seitenaufrufe eines Besuchs zusammen.", "30 Minuten"],
        ],
        "marketing": [
            ["_gcl_au", "Google Ireland Limited", "Misst, ob eine Google-Anzeige zu einer Anfrage geführt hat.", "90 Tage"],
            ["_fbp", "Meta Platforms Ireland Limited", "Misst den Erfolg von Anzeigen auf Facebook und Instagram.", "90 Tage"],
        ],
    },
    "en": {
        "necessary": [
            ["tt-consent", "TipTop (local storage)", "Stores your cookie choice, the version of this notice, the time and a random ID as proof.", "12 months"],
            ["tt-lang", "TipTop (cookie)", "Remembers whether you want the site in German or English.", "1 year"],
            ["tt-mic-ok", "TipTop (local storage)", "Remembers that you confirmed the voice input notice.", "until you delete it"],
            ["csrftoken", "TipTop (cookie)", "Stops forms being submitted from other websites.", "1 year"],
            ["sessionid", "TipTop (cookie)", "Keeps staff signed in to the admin area. Never set for visitors.", "2 weeks"],
        ],
        "stats": [
            ["_pk_id.*", "Matomo, our own server", "Tells visits apart without identifying you. IP addresses are shortened.", "13 months"],
            ["_pk_ses.*", "Matomo, our own server", "Groups the pages viewed during one visit.", "30 minutes"],
        ],
        "marketing": [
            ["_gcl_au", "Google Ireland Limited", "Measures whether a Google ad led to a request.", "90 days"],
            ["_fbp", "Meta Platforms Ireland Limited", "Measures how ads on Facebook and Instagram perform.", "90 days"],
        ],
    },
}


def cookie_table(lang: str, cats: list[str]) -> dict:
    src = COOKIES["en" if lang == "en" else "de"]
    return {k: src[k] for k in cats if k in src}
