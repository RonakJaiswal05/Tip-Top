"""One version value for everything the public pages show.

Any save in the catalogue, shops or content bumps it, so cached catalogue data and page fragments are rebuilt on
the next request. This is how a price change shows on the site within seconds (target: 60 s).

The value is also the cache-busting key of /api/catalog.json, which browsers keep for a year. It must therefore
never repeat: it is a nanosecond timestamp, not a counter that could restart at 1 after Redis loses its data.
"""
import time

from django.core.cache import cache

KEY = "site-version"


def site_version() -> int:
    v = cache.get(KEY)
    if v is None:
        cache.add(KEY, time.time_ns(), None)
        v = cache.get(KEY)
    return v


def bump(*_args, **_kwargs) -> None:
    cache.set(KEY, time.time_ns(), None)


def cached(name: str, builder, timeout: int = 3600):
    """Cache builder() under name for the current site version."""
    key = f"{name}:v{site_version()}"
    value = cache.get(key)
    if value is None:
        value = builder()
        cache.set(key, value, timeout)
    return value
