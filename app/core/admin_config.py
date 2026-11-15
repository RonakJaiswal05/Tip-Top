"""Makes the TipTop admin site (two-factor sign-in, dashboard) the default admin site."""
from django.contrib.admin.apps import AdminConfig


class TipTopAdminConfig(AdminConfig):
    default_site = "core.admin_site.TipTopAdminSite"
