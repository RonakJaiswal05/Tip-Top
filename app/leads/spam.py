"""Spam protection without reCAPTCHA (SOW F4): honeypot, minimum fill time and rate limits per IP.

Nothing here stores the IP address: the rate limit key is a salted hash that expires with the window.
"""
import hashlib
import time

from django.conf import settings
from django.core import signing
from django.core.cache import cache


def client_ip(request) -> str:
    # Nginx sets X-Real-IP to the connecting address; never trust a client-supplied X-Forwarded-For chain.
    return request.META.get("HTTP_X_REAL_IP") or request.META.get("REMOTE_ADDR", "")


def _key(request, bucket: str) -> str:
    raw = f"{settings.SECRET_KEY}:{client_ip(request)}".encode()
    return f"rl:{bucket}:{hashlib.sha256(raw).hexdigest()[:24]}"


def rate_limited(request, bucket: str, limit: int, window: int) -> bool:
    """True if this IP already used `limit` submissions in the last `window` seconds (fixed window)."""
    key = _key(request, bucket)
    if cache.add(key, 1, window):
        return False
    try:
        n = cache.incr(key)
    except ValueError:
        cache.set(key, 1, window)
        return False
    return n > limit


def honeypot_hit(data) -> bool:
    return bool(str(data.get("website", "") or "").strip())


def too_fast(data) -> bool:
    """The page hands out a signed timestamp; a real person needs a few seconds to fill a form."""
    raw = data.get("ts")
    if not raw:
        return True
    try:
        issued = signing.loads(str(raw), salt="form-ts", max_age=7 * 24 * 3600)
    except signing.BadSignature:
        return True
    return time.time() - int(issued) < settings.FORM_MIN_SECONDS
