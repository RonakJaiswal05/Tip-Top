from pathlib import Path

from django.core.management.base import BaseCommand

from catalog.pricelist import export_rows, to_csv, to_xlsx


class Command(BaseCommand):
    help = "Export all prices as Excel (.xlsx) or CSV in the layout import_prices reads."

    def add_arguments(self, parser):
        parser.add_argument("file", help="Output file, .xlsx or .csv")
        parser.add_argument("--category", choices=["phone", "tablet", "laptop", "console"])

    def handle(self, *args, **opts):
        path = Path(opts["file"])
        rows = export_rows(opts.get("category"))
        path.write_bytes(to_xlsx(rows) if path.suffix.lower() == ".xlsx" else to_csv(rows))
        self.stdout.write(self.style.SUCCESS(f"{len(rows) - 1} models written to {path}"))
