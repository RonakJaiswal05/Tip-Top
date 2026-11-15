"""Price management screens (A3): editor, bulk changes, copy from a similar model, import and export."""
import secrets
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

from django import forms
from django.contrib import messages
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone

from . import pricelist
from .services import model_repairs
from .models import (
    Brand, Category, CategoryPrice, DeviceModel, Price, PriceSource, RepairType, ScheduledPriceChange, Tier,
)


def _need(request, perm="change"):
    if not request.user.has_perm(f"catalog.{perm}_price"):
        raise PermissionDenied


def _ctx(request, title, **kw):
    from django.contrib import admin

    return {**admin.site.each_context(request), "title": title, "opts": Price._meta, **kw}


services = model_repairs  # one rule for editor, import and starting prices


def _dec(raw):
    raw = (raw or "").strip().replace(",", ".").replace("€", "").strip()
    if raw == "":
        return None
    try:
        v = Decimal(raw).quantize(Decimal("0.01"))
    except InvalidOperation:
        raise ValueError(raw)
    if v < 0 or v > 100000:
        raise ValueError(raw)
    return v


def price_editor(request):
    _need(request, "view")
    cats = list(Category.objects.order_by("order"))
    cat = request.GET.get("cat") or "phone"
    model = None
    if request.GET.get("model"):
        model = DeviceModel.objects.filter(pk=request.GET["model"]).select_related("category", "brand").first()
        if model:
            cat = model.category.key
    brand = request.GET.get("brand", "")
    q = request.GET.get("q", "").strip()
    models = DeviceModel.objects.filter(category__key=cat).select_related("brand").order_by("brand__order", "sort_order", "name")
    if brand:
        models = models.filter(brand__slug=brand)
    if q:
        for w in q.split():
            models = models.filter(Q(name__icontains=w) | Q(brand__name__icontains=w))
    brands = Brand.objects.filter(models__category__key=cat).distinct().order_by("order", "name")

    rows = []
    if model:
        if request.method == "POST":
            _need(request, "change")
            changed, errors = save_model_prices(request, model)
            if errors:
                messages.error(request, "Nicht gespeichert, bitte prüfen: " + ", ".join(errors))
            else:
                messages.success(request, f"{changed} Preise gespeichert. Die Website zeigt sie jetzt." if changed else "Keine Änderungen.")
                return redirect(f"{reverse('admin:catalog_price_editor')}?model={model.pk}")
        current = {(p.repair_id, p.tier): p for p in model.prices.all()}
        base = {(b.repair_id, b.tier): b.amount for b in CategoryPrice.objects.filter(category=model.category)}
        for r in services(model):
            tiers = [Tier.PREMIUM, Tier.ORIGINAL] if r.has_tiers else [Tier.STANDARD]
            for tier in tiers:
                p = current.get((r.id, tier))
                rows.append({
                    "repair": r, "tier": tier, "tier_label": "" if tier == Tier.STANDARD else Tier(tier).label, "p": p,
                    "field": f"p_{r.id}_{tier}", "from_field": f"f_{r.id}_{tier}",
                    "placeholder": base.get((r.id, tier)) if r.fixed_price else "", "fixed": r.fixed_price,
                })
    return render(request, "admin/catalog/price_editor.html", _ctx(
        request, "Preise", cats=cats, cat=cat, brands=brands, brand=brand, q=q, models=models, model=model, rows=rows,
        scheduled=model.scheduled_prices.filter(applied_at__isnull=True).select_related("repair") if model else [],
    ))


@transaction.atomic
def save_model_prices(request, model: DeviceModel) -> tuple[int, list[str]]:
    current = {(p.repair_id, p.tier): p for p in model.prices.select_for_update()}
    base = {(b.repair_id, b.tier): b.amount for b in CategoryPrice.objects.filter(category=model.category)}
    changed, errors = 0, []
    reason = "Preisübersicht"
    for r in services(model):
        for tier in ([Tier.PREMIUM, Tier.ORIGINAL] if r.has_tiers else [Tier.STANDARD]):
            field = f"p_{r.id}_{tier}"
            if field not in request.POST:
                continue
            try:
                amount = _dec(request.POST.get(field))
            except ValueError as e:
                errors.append(f"{r.name_de}: „{e}“")
                continue
            is_from = bool(request.POST.get(f"f_{r.id}_{tier}"))
            p = current.get((r.id, tier))
            if amount is None or (r.fixed_price and amount == base.get((r.id, tier)) and not is_from):
                if p:
                    p._change_reason = reason
                    p.delete()
                    changed += 1
                continue
            if p and p.amount == amount and p.is_from == is_from:
                continue
            if not p:
                p = Price(model=model, repair=r, tier=tier)
            p.amount, p.is_from, p.source = amount, is_from, PriceSource.ADMIN
            p._change_reason = reason
            p.save()
            changed += 1
    if errors:
        transaction.set_rollback(True)
        return 0, errors
    return changed, []


class BulkForm(forms.Form):
    category = forms.ModelChoiceField(Category.objects.order_by("order"), label="Kategorie")
    brand = forms.ModelChoiceField(Brand.objects.order_by("name"), label="Marke", required=False, empty_label="Alle Marken")
    repair = forms.ModelChoiceField(RepairType.objects.filter(fixed_price=False).order_by("order"), label="Reparatur", required=False,
                                    empty_label="Alle Reparaturen")
    tier = forms.ChoiceField(label="Teil", choices=[("", "Alle")] + list(Tier.choices), required=False)
    mode = forms.ChoiceField(label="Änderung", choices=[("pct", "Prozent"), ("eur", "Euro")], initial="pct")
    value = forms.DecimalField(label="Wert", help_text="z. B. 10 für +10 % oder -5 für 5 € günstiger", max_digits=7, decimal_places=2)
    rounding = forms.ChoiceField(label="Runden", choices=[("9", "Auf …9 (wie bisher: 149, 219)"), ("1", "Auf ganze Euro"), ("0", "Nicht runden")], initial="9")
    effective_at = forms.DateTimeField(label="Gültig ab (optional)", required=False, help_text="Leer = sofort. Sonst als geplante Änderung.",
                                       widget=forms.DateTimeInput(attrs={"type": "datetime-local"}))


def _new_amount(old: Decimal, mode: str, value: Decimal, rounding: str) -> Decimal:
    v = old * (1 + value / 100) if mode == "pct" else old + value
    v = max(v, Decimal("0"))
    if rounding == "9":
        v = Decimal(max(19, int((v / 10).quantize(Decimal("1"), rounding=ROUND_HALF_UP)) * 10 - 1))
    elif rounding == "1":
        v = v.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return v.quantize(Decimal("0.01"))


def bulk_change(request):
    """Raise all battery prices for a brand by a percentage, and similar (A3 bulk tools)."""
    _need(request)
    form = BulkForm(request.POST or None)
    preview, total = [], 0
    if request.method == "POST" and form.is_valid():
        d = form.cleaned_data
        qs = Price.objects.filter(model__category=d["category"], model__active=True).select_related("model__brand", "repair")
        if d["brand"]:
            qs = qs.filter(model__brand=d["brand"])
        if d["repair"]:
            qs = qs.filter(repair=d["repair"])
        if d["tier"]:
            qs = qs.filter(tier=d["tier"])
        items = [(p, _new_amount(p.amount, d["mode"], d["value"], d["rounding"])) for p in qs]
        items = [(p, n) for p, n in items if n != p.amount]
        total = len(items)
        if "apply" in request.POST:
            desc = f"Massenänderung {d['value']:+} {'%' if d['mode'] == 'pct' else '€'}"
            with transaction.atomic():
                if d["effective_at"] and d["effective_at"] > timezone.now():
                    ScheduledPriceChange.objects.bulk_create([
                        ScheduledPriceChange(model=p.model, repair=p.repair, tier=p.tier, amount=n, is_from=p.is_from,
                                             effective_at=d["effective_at"], note=desc, created_by=request.user)
                        for p, n in items
                    ])
                    messages.success(request, f"{total} Preisänderungen für {timezone.localtime(d['effective_at']):%d.%m.%Y %H:%M} geplant.")
                else:
                    for p, n in items:
                        p.amount, p.source = n, PriceSource.ADMIN
                        p._change_reason = desc
                        p.save()
                    messages.success(request, f"{total} Preise geändert. Die Website zeigt sie jetzt.")
            return redirect("admin:catalog_price_bulk")
        preview = items[:300]
    return render(request, "admin/catalog/bulk.html", _ctx(request, "Preise gesammelt ändern", form=form, preview=preview, total=total))


class CopyForm(forms.Form):
    source = forms.ModelChoiceField(DeviceModel.objects.select_related("brand").order_by("category__order", "brand__name", "name"), label="Von Modell")
    target = forms.ModelChoiceField(DeviceModel.objects.select_related("brand").order_by("category__order", "brand__name", "name"), label="Auf Modell")
    overwrite = forms.BooleanField(label="Vorhandene Preise des Ziels überschreiben", required=False)


def copy_prices(request):
    """Copy prices from a similar model (A3)."""
    _need(request)
    form = CopyForm(request.POST or None, initial={"target": request.GET.get("target")})
    if request.method == "POST" and form.is_valid():
        src, dst = form.cleaned_data["source"], form.cleaned_data["target"]
        if src.category_id != dst.category_id:
            form.add_error("target", "Beide Modelle müssen in derselben Kategorie sein.")
        elif src == dst:
            form.add_error("target", "Bitte zwei verschiedene Modelle wählen.")
        else:
            allowed = {r.id for r in services(dst)}
            n = 0
            with transaction.atomic():
                for p in src.prices.all():
                    if p.repair_id not in allowed:
                        continue
                    cur = Price.objects.filter(model=dst, repair_id=p.repair_id, tier=p.tier).first()
                    if cur and not form.cleaned_data["overwrite"]:
                        continue
                    cur = cur or Price(model=dst, repair_id=p.repair_id, tier=p.tier)
                    cur.amount, cur.is_from, cur.source = p.amount, p.is_from, PriceSource.ADMIN
                    cur._change_reason = f"Kopiert von {src}"
                    cur.save()
                    n += 1
            messages.success(request, f"{n} Preise von {src} auf {dst} übernommen.")
            return redirect(f"{reverse('admin:catalog_price_editor')}?model={dst.pk}")
    return render(request, "admin/catalog/copy.html", _ctx(request, "Preise von einem ähnlichen Modell übernehmen", form=form))


class ImportForm(forms.Form):
    file = forms.FileField(label="Preisliste (Excel .xlsx oder CSV)")


def import_view(request):
    """Upload, preview (dry run), then apply (A3)."""
    _need(request)
    report, token, name = None, request.POST.get("token"), ""
    form = ImportForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and token:
        stored = cache.get(f"price-import:{request.user.pk}:{token}")
        if not stored:
            messages.error(request, "Die Vorschau ist abgelaufen. Bitte die Datei erneut hochladen.")
            return redirect("admin:catalog_price_import")
        name, data = stored
        rows = pricelist.read_table(data, name)
        report = pricelist.import_rows(rows, filename=name, dry_run=False, user=request.user)
        cache.delete(f"price-import:{request.user.pk}:{token}")
        messages.success(request, f"Import abgeschlossen: {report.summary()}.")
        return redirect("admin:catalog_price_editor")
    if request.method == "POST" and form.is_valid():
        f = form.cleaned_data["file"]
        name = f.name
        if f.size > 5 * 1024 * 1024:
            form.add_error("file", "Die Datei ist größer als 5 MB.")
        else:
            data = f.read()
            try:
                rows = pricelist.read_table(data, name)
                report = pricelist.import_rows(rows, filename=name, dry_run=True)
                token = secrets.token_urlsafe(16)
                cache.set(f"price-import:{request.user.pk}:{token}", (name, data), 1800)
            except Exception as e:  # unreadable file
                form.add_error("file", f"Die Datei konnte nicht gelesen werden: {e}")
                report = None
    return render(request, "admin/catalog/import.html", _ctx(request, "Preisliste importieren", form=form, report=report, token=token, name=name))


def export_view(request):
    _need(request, "view")
    from core.roles import user_in

    if not user_in(request.user, "Owner", "Manager"):
        raise PermissionDenied
    cat = request.GET.get("cat") or None
    rows = pricelist.export_rows(cat)
    stamp = timezone.localdate().isoformat()
    if request.GET.get("fmt") == "csv":
        resp = HttpResponse(pricelist.to_csv(rows), content_type="text/csv; charset=utf-8")
        resp["Content-Disposition"] = f'attachment; filename="tiptop-preise-{stamp}.csv"'
    else:
        resp = HttpResponse(pricelist.to_xlsx(rows), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        resp["Content-Disposition"] = f'attachment; filename="tiptop-preise-{stamp}.xlsx"'
    return resp
