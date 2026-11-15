from django.utils import translation

from .models import SiteSettings
from .routes import LANGS, PAGES, alternates, page_url


def site(request):
    lang = translation.get_language() or "de"
    if lang not in LANGS:
        lang = "de"
    alt = getattr(request, "alternates", None) or alternates("home")
    return {
        "S": SiteSettings.load(),
        "lang": lang,
        "other_lang": "en" if lang == "de" else "de",
        "alternates": alt,
        "canonical": alt.get(lang),
        "urls": {k: page_url(k, lang) for k in PAGES},
    }
