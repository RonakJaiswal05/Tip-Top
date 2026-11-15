from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import path

from django.contrib.sitemaps.views import sitemap as sitemap_view
from django.views.decorators.cache import cache_page

from catalog import views as catalog_views
from core import views as core_views
from core.sitemaps import SITEMAPS
from core.routes import LEGAL_KEYS, PAGES
from leads import api as leads_api
from leads import views as leads_views
from legal import api as legal_api
from legal import views as legal_views

from django.contrib.auth import views as auth_views

# Password reset by email for staff (A1). Templates: Django admin's registration templates.
_reset = dict(extra_context={"site_header": "TipTop Service 24 · Verwaltung"})
urlpatterns = [
    path("admin/password_reset/", auth_views.PasswordResetView.as_view(
        **_reset, email_template_name="registration/password_reset_email.html", subject_template_name="registration/password_reset_subject.txt",
    ), name="admin_password_reset"),
    path("admin/password_reset/done/", auth_views.PasswordResetDoneView.as_view(**_reset), name="password_reset_done"),
    path("admin/reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(**_reset), name="password_reset_confirm"),
    path("admin/reset/done/", auth_views.PasswordResetCompleteView.as_view(**_reset), name="password_reset_complete"),
    path("admin/", admin.site.urls),
    path("healthz", core_views.healthz),
    path("robots.txt", core_views.robots),
    path("api/catalog.json", core_views.catalog_json, name="catalog-json"),
    path("api/requests/", leads_api.submit, name="api-requests"),
    path("api/consent/", legal_api.consent, name="api-consent"),
    path("qr/anfrage.<str:fmt>", leads_views.qr, name="qr"),
    path("sitemap.xml", cache_page(3600)(sitemap_view), {"sitemaps": SITEMAPS}, name="django.contrib.sitemaps.views.sitemap"),
]

localized = [path("", core_views.home, name="home")]
# One canonical slug per language (core.routes.PAGES); the other language's slug redirects with a 301.
for lang in ("de", "en"):
    localized.append(path(f"{PAGES['request'][lang]}/", leads_views.request_page, name=f"request-{lang}"))
    localized.append(path(f"{PAGES['models'][lang]}/", catalog_views.model_index, name=f"models-{lang}"))
    localized.append(path(f"{PAGES['models'][lang]}/<slug:slug>/", catalog_views.model_page, name=f"model-{lang}"))
    for key in LEGAL_KEYS + ["withdraw"]:
        localized.append(path(f"{PAGES[key][lang]}/", legal_views.legal_page, {"key": key}, name=f"{key}-{lang}"))

urlpatterns += i18n_patterns(*localized, prefix_default_language=True)

if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
