"""Template helpers shared by all public pages: texts, icons, prices, responsive images."""
from django import template
from django.utils.html import escape, format_html
from django.utils.safestring import mark_safe

from catalog.services import fmt_eur
from content.texts import fill
from core.icons import icon

register = template.Library()


@register.simple_tag(takes_context=True)
def t(context, key, **kw):
    """Text in the current language; {placeholders} filled from keyword arguments. Escaped."""
    T = context.get("T") or {}
    s = T.get(key, key)
    if isinstance(s, str) and kw:
        s = fill(s, **kw)
    return s


@register.simple_tag
def ic(name, stroke=1.8):
    return icon(name, float(stroke))


@register.filter
def eur(value, lang="de"):
    return fmt_eur(value, lang)


@register.filter
def get(d, key):
    try:
        return d.get(key) if hasattr(d, "get") else d[key]
    except (KeyError, IndexError, TypeError):
        return None


SIZES = {
    "tile": "(max-width:599px) 44vw, (max-width:900px) 22vw, 200px",
    "rep": "(max-width:520px) 76vw, (max-width:900px) 46vw, 440px",
    "hero": "(max-width:599px) 92vw, (max-width:900px) 40vw, 600px",
    "lcard": "(max-width:599px) 84vw, (max-width:760px) 92vw, 700px",
    "cmp": "(max-width:1400px) 96vw, 1400px",
    "default": "(max-width:700px) 92vw, 640px",
}


# Where the hero film plays (same test as site.js HV_MQ, plus reduced motion). There the hero shows the film's first
# frame from the start instead of the repair photo, so nothing jumps when the film begins (Ronak, 27 Nov 2026).
FILM_MEDIA = "(min-width:901px) and (hover:hover) and (pointer:fine) and (prefers-reduced-motion:no-preference)"


def _srcset(img: dict, fmt: str) -> str:
    s, l = img["s"], img.get("l") or img["s"]
    if fmt not in s:
        return ""
    return f"{s[fmt]} {s['w']}w, {l[fmt]} {l['w']}w" if l is not s else f"{s[fmt]} {s['w']}w"


def picture_html(img: dict | None, sizes: str = "default", eager: bool = False, high: bool = False, alt: str = "", cls: str = "",
                 art: dict | None = None, art_media: str = "") -> str:
    """<picture> with AVIF, WebP and JPEG sources in a phone (760 px) and a desktop size, like the prototype's srcset.
    `art` is another image shown instead where `art_media` matches (art direction)."""
    if not img or "s" not in img:
        return ""
    sz = SIZES.get(sizes, sizes)
    s, l = img["s"], img.get("l") or img["s"]

    def srcset(fmt):
        return _srcset(img, fmt)

    art_sources = ""
    if art and "s" in art and art_media:
        for f in ("avif", "webp", "jpg"):
            if f in art["s"]:
                typ = f' type="image/{f}"' if f != "jpg" else ""
                art_sources += f'<source media="{art_media}"{typ} srcset="{_srcset(art, f)}" sizes="{sz}">'

    load = 'fetchpriority="high"' if high else ("" if eager else 'loading="lazy"')
    style = "" if (img.get("fx", 50), img.get("fy", 50)) == (50, 50) else f' style="object-position:{img["fx"]}% {img["fy"]}%"'
    w, h = img.get("w") or l["w"], img.get("h") or round(l["w"] * 1.5)
    return mark_safe(
        "<picture>" + art_sources
        + "".join(f'<source type="image/{f}" srcset="{srcset(f)}" sizes="{sz}">' for f in ("avif", "webp") if f in s)
        + f'<img src="{l["jpg"]}" srcset="{srcset("jpg")}" sizes="{sz}" width="{w}" height="{h}" alt="{escape(alt)}" '
        + f'decoding="async" {load}{style}{(" class=" + chr(34) + cls + chr(34)) if cls else ""}>'
        + "</picture>"
    )


@register.simple_tag(takes_context=True)
def ph(context, key, cls="", sizes="default", eager=False, high=False, alt=None, film=""):
    """The prototype's <figure class="ph"> image frame, rendered on the server with the image already in place.
    `film`: media key of the hero film's first frame, shown instead where the film plays (FILM_MEDIA)."""
    imgs = context.get("IMGS") or {}
    img = imgs.get(key)
    lang = context.get("lang", "de")
    a = (img or {}).get("alt", {}).get(lang, "") if alt is None else alt
    hidden = "" if a else ' aria-hidden="true"'
    art = imgs.get(film) if film else None
    inner = picture_html(img, sizes, eager, high, a, art=art, art_media=FILM_MEDIA) if img else ""
    loaded = " tried loaded" if inner else ""
    return format_html('<figure class="ph {}{}" data-img="{}"{}>{}</figure>', cls, loaded, key, mark_safe(hidden), inner)


@register.simple_tag(takes_context=True)
def stars(context, rating):
    from content.texts import fill as f

    T = context.get("T") or {}
    lang = context.get("lang", "de")
    r = float(rating)
    txt = f"{r:.1f}".replace(".", ",") if lang == "de" else f"{r:.1f}"
    star = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2.6l2.9 6 6.5.8-4.8 4.5 1.2 6.5L12 17.3l-5.8 3.1 1.2-6.5L2.6 9.4l6.5-.8z"/></svg>'
    label = f(T.get("gmb_aria", "Rated {r} out of 5"), r=txt)
    return mark_safe(
        f'<span class="stars" role="img" aria-label="{escape(label)}"><span class="s0">{star * 5}</span>'
        f'<span class="s1" style="width:{r / 5 * 100:.1f}%">{star * 5}</span></span>'
    )


@register.filter
def num1(value, lang="de"):
    if value is None:
        return ""
    s = f"{float(value):.1f}"
    return s.replace(".", ",") if lang == "de" else s


@register.filter
def thousands(value, lang="de"):
    try:
        n = int(value)
    except (TypeError, ValueError):
        return value
    s = f"{n:,}"
    return s.replace(",", ".") if lang == "de" else s


@register.simple_tag(takes_context=True)
def fine(context, key):
    """Short privacy note under a form, with links to the privacy policy and terms (the prototype's fine())."""
    T = context.get("T") or {}
    urls = context.get("urls") or {}
    s = escape(T.get(key, key))
    s = s.replace("{p}", f'<a href="{urls.get("datenschutz", "")}">{escape(T.get("lk_priv", ""))}</a>')
    s = s.replace("{a}", f'<a href="{urls.get("agb", "")}">{escape(T.get("lk_agb", ""))}</a>')
    return mark_safe(s)


@register.simple_tag
def walink(number, msg):
    from urllib.parse import quote

    return f"https://wa.me/{number}?text={quote(str(msg))}"
