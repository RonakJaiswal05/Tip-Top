from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from catalog.pricelist import import_rows, read_table


class Command(BaseCommand):
    help = (
        "Import the shop's price list from CSV or Excel (.xlsx). Wide layout (one row per model, one column per repair, "
        "as written by export_prices) or long layout (Kategorie, Marke, Modell, Reparatur, Teil, Preis). "
        "Use --dry-run first to see what would change."
    )

    def add_arguments(self, parser):
        parser.add_argument("file")
        parser.add_argument("--dry-run", action="store_true", help="Show what would change without saving.")
        parser.add_argument("--verbose-changes", action="store_true", help="List every changed price.")

    def handle(self, *args, **opts):
        path = Path(opts["file"])
        if not path.is_file():
            raise CommandError(f"File not found: {path}")
        rows = read_table(path.read_bytes(), path.name)
        try:
            rep = import_rows(rows, filename=path.name, dry_run=opts["dry_run"])
        except ValueError as e:
            raise CommandError(str(e))
        prefix = "DRY RUN, nothing saved. " if opts["dry_run"] else ""
        self.stdout.write(self.style.SUCCESS(prefix + rep.summary()))
        if opts["verbose_changes"]:
            for c in rep.changes:
                self.stdout.write("  " + c)
        for title, items in (("Unknown models", rep.unknown_models), ("Unknown columns", rep.unknown_columns),
                             ("Unreadable cells", rep.bad_cells), ("Repair not offered for this model", rep.not_offered)):
            if items:
                self.stdout.write(self.style.WARNING(f"{title} ({len(items)}):"))
                for x in items[:50]:
                    self.stdout.write("  " + x)
                if len(items) > 50:
                    self.stdout.write(f"  … and {len(items) - 50} more")
