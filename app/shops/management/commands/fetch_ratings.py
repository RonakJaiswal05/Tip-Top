from django.core.management.base import BaseCommand

from shops.models import Shop
from shops.tasks import fetch_rating


class Command(BaseCommand):
    help = "Fetch rating and userRatingCount for every shop from the Google Places API (New). Runs daily via Celery beat."

    def handle(self, *args, **opts):
        for s in Shop.objects.filter(active=True).exclude(google_place_id=""):
            ok, msg = fetch_rating(s)
            self.stdout.write((self.style.SUCCESS if ok else self.style.WARNING)(f"{s.short}: {msg}"))
