from django.utils import translation

from django.conf import settings

from .models import SiteSettings
from .page import HEAD_JS
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
        "head_js": HEAD_JS,
        "SITE_URL": settings.SITE_URL,
        "hp": "" if getattr(request, "is_home", False) else page_url("home", lang),
    }
