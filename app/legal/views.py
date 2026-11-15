from django.core import signing
from django.http import Http404, HttpResponsePermanentRedirect
from django.shortcuts import render
from django.utils import timezone, translation

from core.page import base_context, date_long
from core.routes import LEGAL_KEYS, alternates, page_url
from leads.models import Withdrawal

from .models import LegalPage
from .render import render as render_body

WD_ERRORS = {"name": "wd_err_name", "email": "wd_err_mail", "reference": "wd_err_ref", "rate": "err_rate"}


def canonical_redirect(request, key: str, lang: str):
    """/de/privacy/ -> /de/datenschutz/: one address per page and language."""
    if request.path != page_url(key, lang):
        qs = request.META.get("QUERY_STRING")
        return HttpResponsePermanentRedirect(page_url(key, lang) + (f"?{qs}" if qs else ""))
    return None


def legal_page(request, key: str):
    lang = translation.get_language()
    redirect = canonical_redirect(request, key, lang)
    if redirect:
        return redirect
    page_key = "widerruf" if key == "withdraw" else key
    page = LegalPage.objects.filter(key=page_key).first()
    v = page.current(lang) if page else None
    if not v:
        raise Http404
    ctx = base_context(request, key, alt=alternates(key), title=v.title)
    T = ctx["T"]
    nav = []
    for k in LEGAL_KEYS:
        p = LegalPage.objects.filter(key=k).first()
        cv = p.current(lang) if p else None
        if cv:
            nav.append({"key": k, "url": page_url(k, lang), "nav": cv.nav_title})
    toc, body = render_body(v.body_html, T.get("lg_toc", ""))

    receipt = None
    if request.GET.get("receipt"):
        try:
            wid = signing.loads(request.GET["receipt"], salt="wd-receipt", max_age=24 * 3600)
            receipt = Withdrawal.objects.select_related("request").filter(pk=wid).first()
        except signing.BadSignature:
            receipt = None
    if receipt:
        at = timezone.localtime(receipt.received_at)
        ctx.update(receipt_date=date_long(at.date(), lang), receipt_time=at.strftime("%H:%M"))
    err = request.GET.get("error")
    ctx.update({
        "v": v, "key": page_key, "nav": nav, "toc": toc, "body": body, "receipt": receipt,
        "wd_open": key == "withdraw" or bool(err),
        "error_text": T.get(WD_ERRORS.get(err, "err_send"), "") if err else "",
        "page_description": v.intro[:160] if v.intro else "",
    })
    return render(request, "site/legal.html", ctx)
