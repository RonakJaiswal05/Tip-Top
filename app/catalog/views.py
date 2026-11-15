"""Model landing pages (one per model and language) and the model index (SOW section 10)."""
from django.http import Http404, HttpResponsePermanentRedirect
from django.shortcuts import render
from django.utils import translation

from content.texts import fill
from core.page import base_context
from core.routes import PAGES, alternates, model_url, page_url
from core.structured import dump, local_business
from core.views import shop_status, wa_link

from .services import fmt_eur, is_from, price, repair_name, services_for, snapshot

CAT_IMG = {"phone": "cat-phone", "tablet": "cat-tablet", "laptop": "cat-laptop", "console": "cat-console"}


def _rows(snap, m, lang, T):
    rows = []
    for key in services_for(snap, m) + ["diagnosis"]:
        r = snap["rep"][key]
        name = repair_name(snap, key, m["cat"], lang)
        tiers = [("p", T["tier_p"]), ("o", T["tier_o"])] if r["tiers"] else [("", "")]
        for code, label in tiers:
            v = price(snap, m, key, code or "p")
            frm = is_from(snap, m, key)
            rows.append({
                "key": key, "tier": code, "name": name, "tier_label": label, "amount": v,
                "label": T["on_request"] if v is None else (f"{T['from']} " if frm else "") + fmt_eur(v, lang),
                "from": frm, "dur": r.get("dur"), "war": r.get("war"),
            })
    return rows


def model_page(request, slug: str):
    lang = translation.get_language()
    snap = snapshot()
    m = next((x for x in snap["models"] if x["slug"] == slug), None)
    if not m:
        from .models import DeviceModel

        old = DeviceModel.objects.filter(slug=slug).select_related("merged_into").first()
        if old and old.merged_into_id and old.merged_into.active:
            return HttpResponsePermanentRedirect(model_url(old.merged_into.slug, lang))
        raise Http404
    if request.path != model_url(slug, lang):
        return HttpResponsePermanentRedirect(model_url(slug, lang))
    name = m[lang]
    ctx = base_context(request, "model", alt=alternates("model", slug=slug))
    T = ctx["T"]
    rows = _rows(snap, m, lang, T)
    priced = [r for r in rows if r["amount"] is not None and r["key"] != "diagnosis"]
    disp = [r["amount"] for r in rows if r["key"] == "display" and r["amount"] is not None]
    sticker = (T["stk_hero"], fmt_eur(min(disp), lang)) if disp else ((T["from"], fmt_eur(min(r["amount"] for r in priced), lang)) if priced else None)
    summary = ", ".join(f"{r['name']}{' ' + r['tier_label'] if r['tier_label'] else ''} {r['label']}" for r in priced[:4])
    others = [x for x in snap["models"] if x["brand"] == m["brand"] and x["cat"] == m["cat"] and x["id"] != m["id"]]
    from core.models import SiteSettings

    S = SiteSettings.load()
    shops = ctx["SHOPS"]
    biz = [local_business(sh, S, lang) for sh in shops]
    services = [{
        "@type": "Service",
        "name": f"{r['name']}{' (' + r['tier_label'] + ')' if r['tier_label'] else ''}: {name}",
        "serviceType": r["name"],
        "areaServed": {"@type": "City", "name": "Berlin"},
        "provider": [{"@id": b["@id"]} for b in biz],
        "offers": {"@type": "Offer", "price": f"{r['amount']:.2f}", "priceCurrency": "EUR", "url": f"{ctx.get('SITE_URL', '')}{model_url(slug, lang)}",
                   **({"priceSpecification": {"@type": "PriceSpecification", "minPrice": f"{r['amount']:.2f}", "priceCurrency": "EUR"}} if r["from"] else {})},
    } for r in rows if r["amount"] is not None]
    from django.conf import settings

    crumbs = [(T["mp_home"], page_url("home", lang)), (T["mp_models"], page_url("models", lang)), (name, model_url(slug, lang))]
    breadcrumb = {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": f"{settings.SITE_URL}{u}"} for i, (n, u) in enumerate(crumbs)
    ]}
    for s in services:
        s["offers"]["url"] = f"{settings.SITE_URL}{model_url(slug, lang)}"
    status = shop_status(T, lang)
    main = ctx["MAIN_SHOP"]
    ctx.update({
        "m": m, "name": name, "rows": rows, "sticker": sticker, "others": others, "crumbs": crumbs,
        "img": CAT_IMG.get(m["cat"], "hero"),
        "page_title": fill(T["mp_title"], m=name), "page_description": fill(T["mp_desc"], m=name, list=summary),
        "wa_url": wa_link(S.whatsapp_number, fill(T["mp_wa_msg"], m=name)), "status": status,
        "main_status": status.get(main["key"]) if main else (False, ""), "pick_wa": wa_link(S.whatsapp_number, T["wa_pick"]),
        "ld_json": dump(biz + services + [breadcrumb]), "hash": "rechner" if lang == "de" else "calculator",
    })
    return render(request, "site/model.html", ctx)


def model_index(request):
    lang = translation.get_language()
    if request.path != page_url("models", lang):
        return HttpResponsePermanentRedirect(page_url("models", lang))
    snap = snapshot()
    ctx = base_context(request, "models", alt=alternates("models"))
    T = ctx["T"]
    groups = []
    for cat in snap["cats"]:
        brands = {}
        for x in snap["models"]:
            if x["cat"] == cat:
                brands.setdefault(x["brand"], []).append(x)
        from catalog.models import slugify_de

        groups.append({"cat": cat, "name": T.get(f"cat_{cat}", cat), "brands": [
            {"name": b, "anchor": f"{cat}-{slugify_de(b)}", "models": [{"name": x[lang], "short": x["nde" if lang == "de" else "nen"], "url": model_url(x["slug"], lang)} for x in ms]}
            for b, ms in brands.items()
        ]})
    ctx.update({"groups": groups, "page_title": T["all_models"], "page_description": T["mi_p"]})
    return render(request, "site/models.html", ctx)
