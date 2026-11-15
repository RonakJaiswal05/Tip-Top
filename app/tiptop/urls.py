from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import path

from core import views as core_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("healthz", core_views.healthz),
    path("robots.txt", core_views.robots),
    path("api/catalog.json", core_views.catalog_json, name="catalog-json"),
]

urlpatterns += i18n_patterns(
    path("", core_views.home, name="home"),
    prefix_default_language=True,
)

if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
