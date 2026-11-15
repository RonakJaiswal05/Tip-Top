from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import path

from core import views as core_views
from core.routes import LEGAL_KEYS, PAGES
from leads import api as leads_api
from leads import views as leads_views
from legal import api as legal_api
from legal import views as legal_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("healthz", core_views.healthz),
    path("robots.txt", core_views.robots),
    path("api/catalog.json", core_views.catalog_json, name="catalog-json"),
    path("api/requests/", leads_api.submit, name="api-requests"),
    path("api/consent/", legal_api.consent, name="api-consent"),
    path("qr/anfrage.<str:fmt>", leads_views.qr, name="qr"),
]

localized = [path("", core_views.home, name="home")]
# One canonical slug per language (core.routes.PAGES); the other language's slug redirects (core.views.page_router).
for lang in ("de", "en"):
    localized.append(path(f"{PAGES['request'][lang]}/", leads_views.request_page, name=f"request-{lang}"))
    for key in LEGAL_KEYS + ["withdraw"]:
        localized.append(path(f"{PAGES[key][lang]}/", legal_views.legal_page, {"key": key}, name=f"{key}-{lang}"))

urlpatterns += i18n_patterns(*localized, prefix_default_language=True)

if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
