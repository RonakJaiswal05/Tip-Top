from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management import call_command
from django.core.management.base import BaseCommand

from content import seed as content_seed
from core.models import SiteSettings
from shops.seed import seed_holidays, seed_shops


def _same(f, path: Path) -> bool:
    try:
        return f.size == path.stat().st_size and f.open("rb").read() == path.read_bytes()
    except (OSError, ValueError):
        return False
    finally:
        f.close()


class Command(BaseCommand):
    help = (
        "Seed everything a fresh site needs from the prototype: settings, catalogue, shops and holidays, page texts, "
        "FAQ, media library, workshop cards, before/after pair, legal pages and roles. Safe to run again."
    )

    def add_arguments(self, parser):
        parser.add_argument("--overwrite-texts", action="store_true",
                            help="Reset page texts, FAQ, workshop cards and the prototype's repair lists and names "
                                 "to the prototype (dev; overrides admin edits of those).")
        parser.add_argument("--refresh-media", action="store_true",
                            help="Replace photos whose file in prototype/img has changed (new photos from the client).")

    def handle(self, *args, **opts):
        ok = lambda m: self.stdout.write(self.style.SUCCESS(m))  # noqa: E731
        S = SiteSettings.load()
        # The films (story film of 27 Nov 2026): 4:5 muted in the desktop hero, 9:16 with sound behind "Film ansehen" on
        # phones. With --refresh-media a new cut from the chat replaces the old one under a new file name, so browsers
        # don't keep the old film.
        img = Path(settings.REPO_DIR) / "prototype" / "img"
        for field, name in (("hero_video", "hero-loop.mp4"), ("hero_video_mobile", "tiptop-film-m.mp4")):
            film, f = img / name, getattr(S, field)
            if film.is_file() and (not f or (opts["refresh_media"] and not _same(f, film))):
                old = f.name if f else ""
                with film.open("rb") as fh:
                    f.save(name, File(fh), save=True)
                if old and old != f.name:
                    f.storage.delete(old)
                ok(f"{field} attached: {f.name}")
        call_command("seed_catalog", stdout=self.stdout, from_prototype=opts["overwrite_texts"])
        ok(f"shops created: {seed_shops()}, holidays added: {seed_holidays()}")
        ok(f"texts written: {content_seed.seed_texts(overwrite=opts['overwrite_texts'])}, FAQ: {content_seed.seed_faq(opts['overwrite_texts'])}")
        ok(f"images added: {content_seed.seed_media(log=self.stdout.write, refresh=opts['refresh_media'])}")
        ok(f"workshop cards: {content_seed.seed_workshop(opts['overwrite_texts'])}, before/after pairs: {content_seed.seed_before_after()}")
        for cmd in ("seed_legal", "setup_roles"):
            try:
                call_command(cmd, stdout=self.stdout)
            except Exception as e:  # commands added in later steps
                if "Unknown command" not in str(e):
                    raise
