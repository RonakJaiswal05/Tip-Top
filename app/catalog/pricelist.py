"""Import and export the price list as CSV or Excel (A3).

Two layouts are understood:

* Wide (what export writes, one row per model): columns Kategorie, Marke, Modell, then one column per repair, e.g.
  "Akku Austausch [battery]" or "Display Reparatur – Premium [display:premium]". Without the [key] part the column is
  matched by the repair's German or English name; "Premium"/"Original" in the header picks the part for displays.
* Long (one row per price): columns Kategorie, Marke, Modell, Reparatur, Teil, Preis (English headers work too).

Cells: "149", "149,00", "149 €" set the price; "ab 149" sets a "from" price; "auf Anfrage", "on request" or "-" removes
the price (shown as price on request); an empty cell leaves the price unchanged.
"""
import csv
import io
import re
import unicodedata
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation

from django.db import transaction

from .models import Category, CategoryPrice, DeviceModel, Price, PriceSource, RepairType, Tier


GENERIC = re.compile(r"\b(reparatur|repair|austausch|replacement|tausch|wechsel|preis|price|eur)\b")


def core(s: str) -> str:
    return re.sub(r"\s+", " ", GENERIC.sub(" ", norm(s))).strip()


def norm(s) -> str:
    s = unicodedata.normalize("NFD", str(s or "").lower())
    s = "".join(c for c in s if not unicodedata.combining(c)).replace("ß", "ss")
    return re.sub(r"[^a-z0-9+]+", " ", s).strip()


CAT_ALIASES = {
    "phone": ["phone", "smartphone", "handy", "handys", "smartphones", "telefon"],
    "tablet": ["tablet", "tablets", "ipad"],
    "laptop": ["laptop", "laptops", "notebook", "macbook"],
    "console": ["console", "konsole", "konsolen", "consoles", "spielkonsole"],
}
TIER_WORDS = {"premium": Tier.PREMIUM, "original": Tier.ORIGINAL, "orig": Tier.ORIGINAL, "standard": Tier.STANDARD}
ON_REQUEST = {"auf anfrage", "on request", "anfrage", "-", "–", "n a", "na", "x"}
HEAD = {
    "category": ["kategorie", "category", "geraet", "geratetyp", "typ", "type"],
    "brand": ["marke", "brand", "hersteller", "manufacturer"],
    "model": ["modell", "model", "geraet modell", "device"],
    "slug": ["url name", "slug", "url"],
    "repair": ["reparatur", "repair", "service", "leistung"],
    "tier": ["teil", "tier", "qualitat", "qualitaet", "quality", "part"],
    "price": ["preis", "price", "betrag", "amount", "eur"],
}


@dataclass
class Report:
    updated: int = 0
    created: int = 0
    removed: int = 0
    unchanged: int = 0
    rows: int = 0
    unknown_models: list = field(default_factory=list)
    unknown_columns: list = field(default_factory=list)
    bad_cells: list = field(default_factory=list)
    not_offered: list = field(default_factory=list)
    changes: list = field(default_factory=list)

    def summary(self) -> str:
        parts = [f"{self.rows} Zeilen gelesen", f"{self.created} neu", f"{self.updated} geändert",
                 f"{self.removed} auf Anfrage gesetzt", f"{self.unchanged} unverändert"]
        if self.unknown_models:
            parts.append(f"{len(self.unknown_models)} unbekannte Modelle")
        if self.unknown_columns:
            parts.append(f"{len(self.unknown_columns)} unbekannte Spalten")
        if self.bad_cells:
            parts.append(f"{len(self.bad_cells)} unlesbare Zellen")
        return ", ".join(parts)


def read_table(data: bytes, filename: str) -> list[list[str]]:
    name = filename.lower()
    if name.endswith((".xlsx", ".xlsm")):
        from openpyxl import load_workbook

        wb = load_workbook(io.BytesIO(data), read_only=True, data_only=True)
        ws = wb.worksheets[0]
        return [["" if c is None else str(c) for c in row] for row in ws.iter_rows(values_only=True)]
    text = None
    for enc in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            text = data.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    sample = text[:4096]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=";,\t")
    except csv.Error:
        class dialect(csv.excel):  # noqa: N801
            delimiter = ";" if sample.count(";") > sample.count(",") else ","
    return [row for row in csv.reader(io.StringIO(text), dialect)]


def parse_cell(raw: str):
    """-> ('skip'|'clear'|'set', amount, is_from) or raises ValueError."""
    s = str(raw or "").strip()
    if not s:
        return "skip", None, False
    low = norm(s)
    if low in ON_REQUEST or s in ON_REQUEST:
        return "clear", None, False
    is_from = bool(re.match(r"^\s*(ab|from)\b", s, re.I))
    num = re.sub(r"(?i)\b(ab|from|eur|euro)\b|€", "", s).strip().replace(" ", "")
    if re.fullmatch(r"\d{1,3}(\.\d{3})+(,\d+)?", num):
        num = num.replace(".", "").replace(",", ".")
    else:
        num = num.replace(",", ".")
    try:
        amount = Decimal(num)
    except InvalidOperation:
        raise ValueError(s)
    if amount < 0 or amount > 100000:
        raise ValueError(s)
    return "set", amount.quantize(Decimal("0.01")), is_from


class Matcher:
    def __init__(self):
        self.cats = {c.key: c for c in Category.objects.all()}
        self.cat_alias = {}
        for key, words in CAT_ALIASES.items():
            for w in words:
                self.cat_alias[w] = key
        for c in self.cats.values():
            self.cat_alias[norm(c.name_de)] = c.key
            self.cat_alias[norm(c.name_en)] = c.key
        self.models = list(DeviceModel.objects.select_related("brand", "category"))
        self.by_slug = {m.slug: m for m in self.models}
        self.by_name = {}
        for m in self.models:
            for n in {m.name, m.full_name("de"), m.full_name("en"), f"{m.brand.name} {m.name}"}:
                self.by_name.setdefault((m.category.key, norm(n)), m)
                self.by_name.setdefault((None, norm(n)), m)
        self.reps = {r.key: r for r in RepairType.objects.all()}
        self.rep_names = {}
        for r in self.reps.values():
            for n in (r.key, r.name_de, r.name_en):
                self.rep_names[norm(n)] = r.key
                self.rep_names.setdefault(core(n), r.key)
            for rn in r.names.all():
                self.rep_names.setdefault(norm(rn.name_de), r.key)
                self.rep_names.setdefault(norm(rn.name_en), r.key)
                self.rep_names.setdefault(core(rn.name_de), r.key)
                self.rep_names.setdefault(core(rn.name_en), r.key)

    def category(self, raw) -> str | None:
        return self.cat_alias.get(norm(raw))

    def model(self, cat, brand, name, slug="") -> DeviceModel | None:
        if slug and slug.strip() in self.by_slug:
            return self.by_slug[slug.strip()]
        for cand in (f"{brand} {name}", name):
            m = self.by_name.get((cat, norm(cand))) or (None if cat else self.by_name.get((None, norm(cand))))
            if m:
                return m
        return None

    def repair_column(self, header: str):
        """-> (repair key, tier) or None."""
        h = str(header or "")
        m = re.search(r"\[([a-z]+)(?::([a-z]+))?\]", h)
        if m and m.group(1) in self.reps:
            key = m.group(1)
            tier = TIER_WORDS.get(m.group(2) or "", None) or (Tier.PREMIUM if self.reps[key].has_tiers else Tier.STANDARD)
            return key, tier
        words = norm(h)
        tier = None
        for w, t in TIER_WORDS.items():
            if re.search(rf"\b{w}\b", words):
                tier = t
                words = re.sub(rf"\b{w}\b", " ", words).strip()
        words = re.sub(r"\s+", " ", words)
        key = self.rep_names.get(words) or self.rep_names.get(core(words))
        if not key:
            # a longer known name inside the header ("iPhone Akku Austausch Preis"), else the header as the start
            # of a known name ("Wasserschaden" for "Wasserschaden Diagnose")
            for n, k in sorted(self.rep_names.items(), key=lambda x: -len(x[0])):
                if n and len(n) > 3 and re.search(rf"(^| ){re.escape(n)}( |$)", words):
                    key = k
                    break
        if not key and len(words) > 3:
            for n, k in sorted(self.rep_names.items(), key=lambda x: len(x[0])):
                if n.startswith(words + " ") or n.endswith(" " + words):
                    key = k
                    break
        if not key:
            return None
        if self.reps[key].has_tiers:
            tier = tier or Tier.PREMIUM
        else:
            tier = Tier.STANDARD
        return key, tier


def _col(headers, names):
    for i, h in enumerate(headers):
        if norm(h) in names:
            return i
    return None


def offered(model: DeviceModel, key: str, _cache: dict | None = None) -> bool:
    """Same rule as the calculator (services.model_repairs), looked up once per model."""
    from .services import model_repairs

    cache = _cache if _cache is not None else {}
    if model.id not in cache:
        cache[model.id] = {r.key for r in model_repairs(model)}
    return key in cache[model.id]


@transaction.atomic
def import_rows(rows: list[list[str]], filename: str = "Preisliste", dry_run: bool = False, user=None) -> Report:
    rep = Report()
    rows = [r for r in rows if any(str(c).strip() for c in r)]
    if not rows:
        return rep
    headers = [str(h).strip() for h in rows[0]]
    mt = Matcher()
    ci = {k: _col(headers, v) for k, v in HEAD.items()}
    long_format = ci["repair"] is not None and ci["price"] is not None
    if ci["model"] is None and ci["slug"] is None:
        raise ValueError("Keine Spalte „Modell“ gefunden.")

    targets = []  # (model, key, tier, action, amount, is_from, where)
    if long_format:
        for n, row in enumerate(rows[1:], start=2):
            rep.rows += 1
            g = lambda k: row[ci[k]] if ci[k] is not None and ci[k] < len(row) else ""  # noqa: E731
            cat = mt.category(g("category"))
            m = mt.model(cat, g("brand"), g("model"), g("slug"))
            if not m:
                rep.unknown_models.append(f"Zeile {n}: {g('brand')} {g('model')}".strip())
                continue
            col = mt.repair_column(f"{g('repair')} {g('tier')}")
            if not col:
                rep.unknown_columns.append(f"Zeile {n}: {g('repair')}")
                continue
            try:
                action, amount, is_from = parse_cell(g("price"))
            except ValueError as e:
                rep.bad_cells.append(f"Zeile {n}: „{e}“")
                continue
            targets.append((m, col[0], col[1], action, amount, is_from, f"Zeile {n}"))
    else:
        fixed_cols = {i for i in (ci["category"], ci["brand"], ci["model"], ci["slug"]) if i is not None}
        cols = {}
        for i, h in enumerate(headers):
            if i in fixed_cols or not h:
                continue
            c = mt.repair_column(h)
            if c:
                cols[i] = c
            else:
                rep.unknown_columns.append(h)
        for n, row in enumerate(rows[1:], start=2):
            rep.rows += 1
            g = lambda i: row[i] if i is not None and i < len(row) else ""  # noqa: E731
            cat = mt.category(g(ci["category"]))
            m = mt.model(cat, g(ci["brand"]), g(ci["model"]), g(ci["slug"]))
            if not m:
                rep.unknown_models.append(f"Zeile {n}: {g(ci['brand'])} {g(ci['model'])}".strip())
                continue
            for i, (key, tier) in cols.items():
                try:
                    action, amount, is_from = parse_cell(g(i))
                except ValueError as e:
                    rep.bad_cells.append(f"Zeile {n}, {headers[i]}: „{e}“")
                    continue
                targets.append((m, key, tier, action, amount, is_from, f"Zeile {n}"))

    reps = mt.reps
    base = {(cp.category_id, cp.repair.key, cp.tier): cp.amount for cp in CategoryPrice.objects.select_related("repair")}
    existing = {(p.model_id, p.repair.key, p.tier): p for p in Price.objects.select_related("repair")}
    reason = f"Import {filename}"
    offered_cache: dict = {}
    for m, key, tier, action, amount, is_from, where in targets:
        if action == "skip":
            continue
        if not offered(m, key, offered_cache):
            rep.not_offered.append(f"{where}: {m.full_name()} · {reps[key].name_de}")
            continue
        cur = existing.get((m.id, key, tier))
        r = reps[key]
        if action == "clear":
            if cur:
                rep.removed += 1
                rep.changes.append(f"{m.full_name()} · {r.name_de}: {cur.amount} € → auf Anfrage")
                if not dry_run:
                    cur._change_reason = reason
                    cur.delete()
            else:
                rep.unchanged += 1
            continue
        if r.fixed_price and base.get((m.category_id, key, tier)) == amount and not is_from:
            # same as the single price for all models: no model-specific override needed
            if cur and not dry_run:
                cur._change_reason = reason
                cur.delete()
            rep.unchanged += 1
            continue
        if cur:
            if cur.amount == amount and cur.is_from == is_from:
                rep.unchanged += 1
                if cur.source == PriceSource.PLACEHOLDER and not dry_run:
                    cur.source = PriceSource.IMPORT
                    cur._change_reason = reason
                    cur.save(update_fields=["source", "updated_at"])
                continue
            rep.updated += 1
            rep.changes.append(f"{m.full_name()} · {r.name_de} {'' if tier == Tier.STANDARD else tier}: {cur.amount} € → {amount} €")
            if not dry_run:
                cur.amount, cur.is_from, cur.source = amount, is_from, PriceSource.IMPORT
                cur._change_reason = reason
                cur.save()
        else:
            rep.created += 1
            rep.changes.append(f"{m.full_name()} · {r.name_de}: neu {amount} €")
            if not dry_run:
                p = Price(model=m, repair=r, tier=tier, amount=amount, is_from=is_from, source=PriceSource.IMPORT)
                p._change_reason = reason
                p.save()
                existing[(m.id, key, tier)] = p
    if dry_run:
        transaction.set_rollback(True)
    return rep


def export_rows(category: str | None = None) -> list[list]:
    """Wide layout, one row per model, the same layout import_rows reads."""
    reps = list(RepairType.objects.order_by("order"))
    cols = []
    for r in reps:
        if r.has_tiers:
            cols += [(r, Tier.PREMIUM, f"{r.name_de} – Premium [{r.key}:premium]"), (r, Tier.ORIGINAL, f"{r.name_de} – Original [{r.key}:original]")]
        else:
            cols.append((r, Tier.STANDARD, f"{r.name_de} [{r.key}]"))
    header = ["Kategorie", "Marke", "Modell", "URL-Name"] + [c[2] for c in cols]
    out = [header]
    prices = {}
    for p in Price.objects.select_related("repair"):
        prices[(p.model_id, p.repair.key, p.tier)] = p
    base = {(cp.category_id, cp.repair.key, cp.tier): cp.amount for cp in CategoryPrice.objects.select_related("repair")}
    qs = DeviceModel.objects.select_related("brand", "category").order_by("category__order", "brand__order", "sort_order")
    if category:
        qs = qs.filter(category__key=category)
    offered_cache: dict = {}
    for m in qs:
        offered(m, "diagnosis", offered_cache)
        keys = offered_cache[m.id]
        row = [m.category.name_de, m.brand.name, m.name, m.slug]
        for r, tier, _ in cols:
            if r.key not in keys:
                row.append("")
                continue
            p = prices.get((m.id, r.key, tier))
            amount = p.amount if p else (base.get((m.category_id, r.key, tier)) if r.fixed_price else None)
            if amount is None:
                row.append("auf Anfrage")
            else:
                v = int(amount) if amount == amount.to_integral_value() else float(amount)
                row.append(f"ab {v}" if (p and p.is_from) else v)
        out.append(row)
    return out


def to_xlsx(rows: list[list]) -> bytes:
    from openpyxl import Workbook
    from openpyxl.styles import Font

    wb = Workbook()
    ws = wb.active
    ws.title = "Preise"
    for r in rows:
        ws.append(r)
    for c in ws[1]:
        c.font = Font(bold=True)
    ws.freeze_panes = "E2"
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def to_csv(rows: list[list]) -> bytes:
    buf = io.StringIO()
    w = csv.writer(buf, delimiter=";")
    for r in rows:
        w.writerow(r)
    return buf.getvalue().encode("utf-8-sig")
