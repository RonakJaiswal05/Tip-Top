"""Page texts per language from the ContentBlock table, cached per site version."""
from core.cache import cached

from .models import ContentBlock


def texts(lang: str) -> dict:
    def build():
        return {b.key: b.value(lang) for b in ContentBlock.objects.all()}

    return cached(f"texts-{lang}", build)


def fill(text: str, /, **kw) -> str:
    """The prototype's t(k, v) placeholder rule: {x} -> value."""
    for k, v in kw.items():
        text = text.replace("{" + k + "}", str(v))
    return text
