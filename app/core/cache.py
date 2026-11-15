"""One version number for everything the public pages show.

Any save in the catalogue, shops or content bumps it, so cached catalogue data and page fragments are rebuilt on
the next request. This is how a price change shows on the site within seconds (target: 60 s).
"""
from django.core.cache import cache

KEY = "site-version"


def site_version() -> int:
    v = cache.get(KEY)
    if v is None:
        v = 1
        cache.add(KEY, v, None)
    return v


def bump(*_args, **_kwargs) -> None:
    try:
        cache.incr(KEY)
    except ValueError:
        cache.set(KEY, 2, None)


def cached(name: str, builder, timeout: int = 3600):
    """Cache builder() under name for the current site version."""
    key = f"{name}:v{site_version()}"
    value = cache.get(key)
    if value is None:
        value = builder()
        cache.set(key, value, timeout)
    return value
