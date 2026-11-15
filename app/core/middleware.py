import time

from django.conf import settings
from django.contrib.auth import logout
from django.http import HttpResponsePermanentRedirect
from django.middleware.locale import LocaleMiddleware as DjangoLocaleMiddleware
from django.shortcuts import render


class LocaleMiddleware(DjangoLocaleMiddleware):
    """Django's LocaleMiddleware, but German unless the visitor chose English.

    The language comes from the URL (/de/, /en/). For an address without a prefix, such as "/" or "/anfrage",
    the remembered choice (cookie tt-lang, set by the language switch) decides; the browser's Accept-Language
    header is ignored on purpose, German is the default.
    """

    def process_request(self, request):
        request.META.pop("HTTP_ACCEPT_LANGUAGE", None)
        return super().process_request(request)


def _csp(request) -> str:
    from .models import SiteSettings

    if request.path.startswith("/admin/"):
        return ("default-src 'self'; img-src 'self' data: blob:; style-src 'self' 'unsafe-inline'; "
                "script-src 'self' 'unsafe-inline'; frame-ancestors 'none'; form-action 'self'; base-uri 'self'")
    from .page import HEAD_JS_HASH

    s = SiteSettings.load()
    script, connect, img = ["'self'", f"'{HEAD_JS_HASH}'"], ["'self'"], ["'self'", "data:"]
    # Optional services only ever load after consent (core.js checks the consent first); CSP just allows their hosts.
    if s.analytics_enabled and s.matomo_url:
        host = s.matomo_url.rstrip("/")
        script.append(host); connect.append(host); img.append(host)
    if s.ads_enabled:
        script += ["https://www.googletagmanager.com", "https://connect.facebook.net"]
        connect += ["https://www.google-analytics.com", "https://www.facebook.com"]
        img += ["https://www.facebook.com", "https://googleads.g.doubleclick.net"]
    return (f"default-src 'self'; script-src {' '.join(script)}; style-src 'self' 'unsafe-inline'; "
            f"img-src {' '.join(img)}; connect-src {' '.join(connect)}; font-src 'self'; frame-ancestors 'none'; "
            "form-action 'self'; base-uri 'self'; object-src 'none'")


class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response.headers.setdefault("Content-Security-Policy", _csp(request))
        response.headers.setdefault(
            "Permissions-Policy", "microphone=(self), camera=(), geolocation=(), payment=(), usb=(), interest-cohort=()"
        )
        response.headers.setdefault("Cross-Origin-Opener-Policy", "same-origin")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        return response


class StaffSessionMiddleware:
    """Signs staff out after STAFF_IDLE_TIMEOUT seconds without activity (A1)."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        if user is not None and user.is_authenticated:
            now = int(time.time())
            last = request.session.get("last_seen", now)
            if now - last > settings.STAFF_IDLE_TIMEOUT:
                logout(request)
            else:
                if now - last > 60:  # write at most once a minute
                    request.session["last_seen"] = now
                request.session.setdefault("last_seen", now)
        return self.get_response(request)


EXEMPT_PREFIXES = ("/admin/", "/static/", "/media/", "/api/consent", "/robots.txt", "/sitemap.xml", "/healthz")


class MaintenanceMiddleware:
    """Friendly page for visitors while maintenance mode is on in the settings (A11). Staff see the site."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        from .models import SiteSettings

        if not request.path.startswith(EXEMPT_PREFIXES):
            s = SiteSettings.load()
            if s.maintenance_mode and not (request.user.is_authenticated and request.user.is_staff):
                lang = "en" if request.path.startswith("/en/") else "de"
                text = s.maintenance_text_en if lang == "en" else s.maintenance_text_de
                resp = render(request, "maintenance.html", {"text": text, "lang": lang, "s": s}, status=503)
                resp["Retry-After"] = "1800"
                return resp
        return self.get_response(request)


SHOPIFY_PREFIXES = ("/pages/", "/products/", "/collections/", "/policies/", "/blogs/", "/cart", "/account", "/search")


class LegacyRedirectMiddleware:
    """301 redirects from the old Shopify URLs (rules are managed in the admin, see core.Redirect)."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        if path.startswith(SHOPIFY_PREFIXES) or path.rstrip("/").endswith(".html"):
            from .redirects import resolve_legacy

            target = resolve_legacy(path)
            if target:
                return HttpResponsePermanentRedirect(target)
        return self.get_response(request)
