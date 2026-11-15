"""Legal pages from the prototype (prototype/src/legal_de.js and legal_en.js, as built into index.html).

Changes made for the live site, all following the build instructions and kept to the minimum:
* internal links point to the real pages (/de/datenschutz/ instead of #datenschutz),
* statistics (Matomo) and marketing (Google Ads, Meta Pixel) are not used, so their sections, cookie tables and the
  sentences announcing them are removed (privacy policy and cookie policy),
* the cookie table lists what the live site stores (tt-lang is a cookie; prototype-only entries removed).
Nothing else is reworded. Yellow <mark class="fill"> placeholders stay for the client to fill; every page shows the
"template, have it checked by a lawyer" note until a version is marked as lawyer-approved in the admin.
"""
import re

from django.db import transaction

from catalog.seed import load
from core.routes import LEGAL_KEYS, page_url

from .cookies import COOKIES
from .models import LegalPage, LegalPageVersion

STAND = {"de": "15. November 2026", "en": "15 November 2026"}
STAND_UNCHANGED = {"de": "14. November 2026", "en": "14 November 2026"}

DROP_SECTIONS = {
    "de": {"datenschutz": {"Statistik mit Matomo (nur mit Einwilligung)", "Marketing (nur mit Einwilligung)"},
           "cookies": {"Statistik", "Marketing"}},
    "en": {"datenschutz": {"Statistics with Matomo (consent only)", "Marketing (consent only)"},
           "cookies": {"Statistics", "Marketing"}},
}
REPLACE = {
    "de": [
        ("<li>Statistik- und Marketing-Dienste laden nur, wenn du ihnen in den Cookie-Einstellungen zustimmst.</li>",
         "<li>Wir setzen keine Statistik- oder Marketing-Dienste ein.</li>"),
        (" Statistik und Marketing setzen wir nur mit deiner Einwilligung ein (§ 25 Abs. 1 TDDDG, Art. 6 Abs. 1 lit. a DSGVO).", ""),
    ],
    "en": [
        ("<li>Statistics and marketing services only load if you agree to them in the cookie settings.</li>",
         "<li>We don't use any statistics or marketing services.</li>"),
        (" We only use statistics and marketing with your consent (§ 25(1) TDDDG, Art. 6(1)(a) GDPR).", ""),
    ],
}


def _cookie_table(lang: str) -> str:
    h = ["Name", "Anbieter", "Zweck", "Dauer"] if lang == "de" else ["Name", "Provider", "Purpose", "Duration"]
    rows = "".join(f"<tr><td><code>{r[0]}</code></td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td></tr>" for r in COOKIES[lang]["necessary"])
    head = "".join(f'<th scope="col">{x}</th>' for x in h)
    return f'<div class="lg-tw"><table class="lg-tbl"><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>'


def build(lang: str, key: str, d: dict) -> tuple[dict, bool]:
    src = (d["LEGAL_DE"] if lang == "de" else d["LEGAL_EN"])[key]
    parts, changed = [], False
    for s in src["sec"]:
        title = s[0]
        if title.startswith("@"):
            parts.append(f'<p class="lg-part">{title[1:]}</p>')
            continue
        if title in DROP_SECTIONS[lang].get(key, set()):
            changed = True
            continue
        body = s[1]
        if key == "cookies" and re.search(r'<table class="lg-tbl">', body) and title in ("Notwendig", "Necessary"):
            body = re.sub(r'<div class="lg-tw">.*?</div>', _cookie_table(lang), body, flags=re.S)
            changed = True
        parts.append(f"<h2>{title}</h2>{body}")
    html = "".join(parts)
    for old, new in REPLACE[lang]:
        if old in html:
            html = html.replace(old, new)
            changed = True
    # internal links: #datenschutz -> /de/datenschutz/
    for k in LEGAL_KEYS + ["withdraw"]:
        anchor = "vertrag-widerrufen" if k == "withdraw" else k
        html = html.replace(f'href="#{anchor}"', f'href="{page_url(k, lang)}"')
    html = html.replace('href="#top"', f'href="{page_url("home", lang)}"').replace('href="#anfrage"', f'href="{page_url("request", lang)}"')
    return {"title": src["h"], "nav_title": src["nav"], "intro": src.get("intro", ""), "body_html": html}, changed


@transaction.atomic
def seed_legal(force: bool = False) -> int:
    d = load()
    n = 0
    for i, key in enumerate(LEGAL_KEYS):
        page, _ = LegalPage.objects.get_or_create(key=key, defaults={"order": i})
        for lang in ("de", "en"):
            if page.versions.filter(language=lang).exists() and not force:
                continue
            data, changed = build(lang, key, d)
            LegalPageVersion.objects.create(
                page=page, language=lang, status=LegalPageVersion.Status.PUBLISHED,
                stand=(STAND if changed else STAND_UNCHANGED)[lang],
                change_note="Aus dem Prototyp übernommen" + ("; Statistik und Marketing entfernt, Cookie-Tabelle an das Live-System angepasst" if changed else ""),
                **data,
            )
            n += 1
    return n
