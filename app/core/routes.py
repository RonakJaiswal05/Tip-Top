"""Public URLs per language. German is the default; English pages have English slugs.

page_url("impressum", "en") -> "/en/legal-notice/". Views and templates use this instead of reverse() so a page
keeps one canonical address per language.
"""
from django.utils import translation

LANGS = ("de", "en")

PAGES = {
    "home": {"de": "", "en": ""},
    "request": {"de": "anfrage", "en": "request"},
    "models": {"de": "reparatur", "en": "repair"},
    "impressum": {"de": "impressum", "en": "legal-notice"},
    "datenschutz": {"de": "datenschutz", "en": "privacy"},
    "agb": {"de": "agb", "en": "terms"},
    "widerruf": {"de": "widerruf", "en": "withdrawal"},
    "vertrag-widerrufen": {"de": "vertrag-widerrufen", "en": "withdraw-contract"},
    "cookies": {"de": "cookies", "en": "cookies"},
    "barrierefreiheit": {"de": "barrierefreiheit", "en": "accessibility"},
}
LEGAL_KEYS = ["impressum", "datenschutz", "agb", "widerruf", "cookies", "barrierefreiheit"]


def lang_or_current(lang: str | None) -> str:
    lang = lang or translation.get_language() or "de"
    return lang if lang in LANGS else "de"


def page_url(key: str, lang: str | None = None) -> str:
    lang = lang_or_current(lang)
    slug = PAGES[key][lang]
    return f"/{lang}/{slug}/" if slug else f"/{lang}/"


def model_url(slug: str, lang: str | None = None) -> str:
    lang = lang_or_current(lang)
    return f"/{lang}/{PAGES['models'][lang]}/{slug}/"


def alternates(key: str, **kw) -> dict[str, str]:
    if key == "model":
        return {lg: model_url(kw["slug"], lg) for lg in LANGS}
    return {lg: page_url(key, lg) for lg in LANGS}


def key_for_slug(slug: str) -> tuple[str | None, str | None]:
    """Return (page key, language the slug belongs to) for a slug in either language."""
    for key, slugs in PAGES.items():
        for lg, s in slugs.items():
            if s and s == slug:
                return key, lg
    return None, None
