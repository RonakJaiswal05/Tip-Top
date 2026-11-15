from django.core.management import call_command
from django.core.management.base import BaseCommand

from content import seed as content_seed
from core.models import SiteSettings
from shops.seed import seed_holidays, seed_shops


class Command(BaseCommand):
    help = (
        "Seed everything a fresh site needs from the prototype: settings, catalogue, shops and holidays, page texts, "
        "FAQ, media library, workshop cards, before/after pair, legal pages and roles. Safe to run again."
    )

    def add_arguments(self, parser):
        parser.add_argument("--overwrite-texts", action="store_true", help="Reset page texts to the prototype's wording.")

    def handle(self, *args, **opts):
        ok = lambda m: self.stdout.write(self.style.SUCCESS(m))  # noqa: E731
        SiteSettings.load()
        call_command("seed_catalog", stdout=self.stdout)
        ok(f"shops created: {seed_shops()}, holidays added: {seed_holidays()}")
        ok(f"texts written: {content_seed.seed_texts(overwrite=opts['overwrite_texts'])}, FAQ: {content_seed.seed_faq()}")
        ok(f"images added: {content_seed.seed_media(log=self.stdout.write)}")
        ok(f"workshop cards: {content_seed.seed_workshop()}, before/after pairs: {content_seed.seed_before_after()}")
        for cmd in ("seed_legal", "setup_roles"):
            try:
                call_command(cmd, stdout=self.stdout)
            except Exception as e:  # commands added in later steps
                if "Unknown command" not in str(e):
                    raise
