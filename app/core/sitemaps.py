"""XML sitemap with hreflang alternates for German and English (SOW F13, section 10)."""
from django.contrib.sitemaps import Sitemap

from catalog.models import DeviceModel
from legal.models import LegalPage

from .routes import LEGAL_KEYS, model_url, page_url


class _I18n(Sitemap):
    i18n = True
    languages = ["de", "en"]
    alternates = True
    x_default = True
    protocol = "https"

    def get_domain(self, site=None):
        from django.conf import settings

        return settings.SITE_URL.split("://", 1)[-1]

    def get_protocol(self, protocol=None):
        from django.conf import settings

        return settings.SITE_URL.split("://", 1)[0] if "://" in settings.SITE_URL else "https"


class PagesSitemap(_I18n):
    changefreq = "weekly"

    def items(self):
        keys = ["home", "request", "models"]
        published = set(LegalPage.objects.values_list("key", flat=True))
        return keys + [k for k in LEGAL_KEYS if k in published]

    def location(self, key):
        return page_url(key)

    def priority(self, key):
        return {"home": 1.0, "models": 0.8, "request": 0.6}.get(key, 0.3)


class ModelsSitemap(_I18n):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return DeviceModel.objects.filter(active=True).order_by("category__order", "brand__order", "sort_order")

    def location(self, m):
        return model_url(m.slug)

    def lastmod(self, m):
        latest = m.prices.order_by("-updated_at").values_list("updated_at", flat=True).first()
        return max(filter(None, [m.updated_at, latest]))


SITEMAPS = {"pages": PagesSitemap, "models": ModelsSitemap}
