from django.core.management.base import BaseCommand

from catalog.seed import seed_catalog


class Command(BaseCommand):
    help = (
        "Seed categories, brands, models, repair types and placeholder prices from the prototype "
        "(app/seed/prototype.json). Safe to run again; existing prices are kept unless --reset-prices."
    )

    def add_arguments(self, parser):
        parser.add_argument("--reset-prices", action="store_true", help="Delete all prices first and re-create the placeholders.")
        parser.add_argument("--from-prototype", action="store_true",
                            help="Take over the prototype's repair names, lists and base prices again (overrides admin edits "
                                 "of the prototype's own repairs; repairs added in the admin stay).")

    def handle(self, *args, **opts):
        seed_catalog(reset_prices=opts["reset_prices"], from_prototype=opts["from_prototype"],
                     log=lambda m: self.stdout.write(self.style.SUCCESS(m)))
