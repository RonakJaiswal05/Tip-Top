from django.core.management.base import BaseCommand

from catalog.seed import seed_catalog


class Command(BaseCommand):
    help = (
        "Seed categories, brands, 180 models, 30 repair types and placeholder prices from the prototype "
        "(app/seed/prototype.json). Safe to run again; existing prices are kept unless --reset-prices."
    )

    def add_arguments(self, parser):
        parser.add_argument("--reset-prices", action="store_true", help="Delete all prices first and re-create the placeholders.")

    def handle(self, *args, **opts):
        seed_catalog(reset_prices=opts["reset_prices"], log=lambda m: self.stdout.write(self.style.SUCCESS(m)))
