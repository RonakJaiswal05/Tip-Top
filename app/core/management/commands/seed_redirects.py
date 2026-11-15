import csv
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from core.models import Redirect, normalise_path
from core.redirects import _models, best_target

CSV = Path(settings.BASE_DIR) / "seed" / "shopify_redirects.csv"


class Command(BaseCommand):
    help = (
        "Load the 301 redirects from the old Shopify URLs (seed/shopify_redirects.csv) into the admin. "
        "--build PATHS_FILE recomputes the CSV from a list of old paths (one per line, e.g. from the old sitemap)."
    )

    def add_arguments(self, parser):
        parser.add_argument("--build", metavar="PATHS_FILE")

    def handle(self, *args, **opts):
        if opts.get("build"):
            models = _models()
            paths = [p.strip() for p in Path(opts["build"]).read_text(encoding="utf-8").splitlines() if p.strip()]
            rows = []
            for p in sorted(set(paths)):
                if p in ("/", "/agents.md"):
                    continue
                t = best_target(p, models)
                if t:
                    rows.append((normalise_path(p), t))
            with CSV.open("w", encoding="utf-8", newline="") as f:
                w = csv.writer(f)
                w.writerow(["old_path", "new_path"])
                w.writerows(rows)
            self.stdout.write(self.style.SUCCESS(f"{len(rows)} redirects written to {CSV}"))
        n = 0
        with CSV.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                _, created = Redirect.objects.get_or_create(old_path=normalise_path(row["old_path"]),
                                                            defaults={"new_path": row["new_path"], "note": "Shopify (Sitemap 15.11.2026)"})
                n += created
        self.stdout.write(self.style.SUCCESS(f"{n} new redirects loaded ({Redirect.objects.count()} in total)."))
