from django.core.management.base import BaseCommand

from legal.seed import seed_legal


class Command(BaseCommand):
    help = "Create the six legal pages (German and English) from the prototype as published, not yet lawyer-approved versions."

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true", help="Add a new version even if the page already has one.")

    def handle(self, *args, **opts):
        n = seed_legal(force=opts["force"])
        self.stdout.write(self.style.SUCCESS(f"{n} legal page versions created."))
