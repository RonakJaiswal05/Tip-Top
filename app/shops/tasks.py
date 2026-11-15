"""Google ratings (F1, F10): rating and userRatingCount from the Places API (New), once a day per shop.

If the API fails, the last stored values stay on the site and the error is shown in the admin.
"""
import logging
from decimal import Decimal

import requests
from celery import shared_task
from django.conf import settings
from django.utils import timezone

from .models import Shop

log = logging.getLogger(__name__)
PLACES_URL = "https://places.googleapis.com/v1/places/{pid}"
FIELDS = "rating,userRatingCount,location"


def fetch_rating(shop: Shop) -> tuple[bool, str]:
    key = settings.GOOGLE_PLACES_API_KEY
    if not key:
        return False, "Kein API-Schlüssel (GOOGLE_PLACES_API_KEY) gesetzt; die gespeicherten Werte bleiben."
    if not shop.google_place_id:
        return False, "Keine Place ID eingetragen."
    try:
        r = requests.get(
            PLACES_URL.format(pid=shop.google_place_id),
            headers={"X-Goog-Api-Key": key, "X-Goog-FieldMask": FIELDS},
            timeout=15,
        )
        if r.status_code != 200:
            raise RuntimeError(f"HTTP {r.status_code}: {r.text[:200]}")
        data = r.json()
        rating, count = data.get("rating"), data.get("userRatingCount")
        if rating is None or count is None:
            raise RuntimeError("Antwort ohne rating/userRatingCount")
        fields = {"rating": Decimal(str(round(float(rating), 1))), "rating_count": int(count), "rating_fetched_at": timezone.now(),
                  "rating_error": ""}
        loc = data.get("location") or {}
        if loc.get("latitude") is not None and loc.get("longitude") is not None:
            fields["latitude"] = Decimal(str(round(loc["latitude"], 6)))
            fields["longitude"] = Decimal(str(round(loc["longitude"], 6)))
        Shop.objects.filter(pk=shop.pk).update(**fields)
        from core.cache import bump

        bump()
        return True, f"{fields['rating']} aus {fields['rating_count']} Bewertungen"
    except Exception as e:  # keep the last good values
        msg = str(e)[:300]
        Shop.objects.filter(pk=shop.pk).update(rating_error=f"{timezone.localtime():%d.%m.%Y %H:%M}: {msg}")
        log.warning("Google rating for %s failed: %s", shop.key, msg)
        return False, f"Abruf fehlgeschlagen, alte Werte bleiben ({msg})"


@shared_task
def fetch_google_ratings() -> dict:
    return {s.key: fetch_rating(s) for s in Shop.objects.filter(active=True).exclude(google_place_id="")}
