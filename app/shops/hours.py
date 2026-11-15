"""Opening hours as text ("Mo–Sa 10–20 Uhr") and as data for the live open status in the browser."""
from datetime import datetime, time

from core.cache import cached

from .models import BERLIN, Shop

DAYS_SHORT = {"de": ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"], "en": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]}
DAYS_LONG = {
    "de": ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"],
    "en": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
}


def t_fmt(t: time, lang: str) -> str:
    """German '10', '20:30'; English '10:00', '20:30' (the prototype's style)."""
    if lang == "de":
        return f"{t.hour}" if t.minute == 0 else f"{t.hour}:{t.minute:02d}"
    return f"{t.hour:02d}:{t.minute:02d}"


def _groups(weekly: dict[int, list]) -> list[tuple[int, int, list]]:
    """Consecutive weekdays with identical hours: [(first, last, intervals), ...], closed days left out."""
    out = []
    for d in range(7):
        iv = weekly.get(d, [])
        if out and out[-1][2] == iv and out[-1][1] == d - 1:
            out[-1] = (out[-1][0], d, iv)
        else:
            out.append((d, d, iv))
    return [g for g in out if g[2]]


def _span(a: int, b: int, lang: str, long: bool) -> str:
    names = DAYS_LONG[lang] if long else DAYS_SHORT[lang]
    if a == b:
        return names[a]
    if long:
        if b == a + 1:
            return f"{names[a]} {'und' if lang == 'de' else 'and'} {names[b]}"
        return f"{names[a]} {'bis' if lang == 'de' else 'to'} {names[b]}"
    return f"{names[a]}–{names[b]}"


def _intervals(iv, lang: str, long: bool) -> str:
    parts = []
    for o, c in iv:
        if long:
            parts.append(f"{t_fmt(o, lang)} {'bis' if lang == 'de' else 'to'} {t_fmt(c, lang)}")
        else:
            parts.append(f"{t_fmt(o, lang)}–{t_fmt(c, lang)}")
    s = (", " if long else ", ").join(parts)
    return s + (" Uhr" if lang == "de" else "")


def week_text(weekly: dict, lang: str, long: bool = False) -> str:
    """'Mo–Sa 10–20 Uhr' or 'Montag bis Samstag, 10 bis 20 Uhr'."""
    groups = _groups(weekly)
    sep = ", " if long else " "
    return "; ".join(f"{_span(a, b, lang, long)}{sep}{_intervals(iv, lang, long)}" for a, b, iv in groups)


def closed_days(weekly: dict) -> list[int]:
    return [d for d in range(7) if not weekly.get(d)]


def summary(shops: list[Shop], lang: str, long: bool = False) -> str:
    """One text for all shops if their hours match, else one per shop."""
    weeks = [s.weekly_hours() for s in shops]
    if not shops:
        return ""
    if all(w == weeks[0] for w in weeks):
        return week_text(weeks[0], lang, long)
    return "; ".join(f"{s.short} {week_text(w, lang, long)}" for s, w in zip(shops, weeks))


def footer_lines(shops: list[Shop], lang: str, sun_closed: str) -> list[str]:
    weeks = [s.weekly_hours() for s in shops]
    if not shops:
        return []

    def one(w):
        txt = week_text(w, lang)
        if 6 in closed_days(w):
            txt += f", {sun_closed}"
        return txt

    if all(w == weeks[0] for w in weeks):
        return [one(weeks[0])]
    return [f"{s.short}: {one(w)}" for s, w in zip(shops, weeks)]


def open_data() -> list[dict]:
    """Per shop: opening intervals for the next 15 days as epoch milliseconds (cached per site version and day)."""
    today = datetime.now(BERLIN).date()

    def build():
        out = []
        for s in Shop.objects.filter(active=True).prefetch_related("hours").order_by("order"):
            out.append({"key": s.key, "iv": [[int(a.timestamp() * 1000), int(b.timestamp() * 1000)] for a, b in s.schedule(today)]})
        return out

    return cached(f"open-data-{today.isoformat()}", build, timeout=6 * 3600)


def is_open_now(shop: Shop, now: datetime | None = None) -> tuple[bool, datetime | None]:
    now = now or datetime.now(BERLIN)
    for a, b in shop.schedule(now.date() - __import__("datetime").timedelta(days=1), days=16):
        if a <= now < b:
            return True, b
        if a > now:
            return False, a
    return False, None
