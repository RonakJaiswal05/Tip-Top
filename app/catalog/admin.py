"""Catalogue admin (A3–A5). Full screens are added in step 5; this registers the models needed elsewhere."""
from django.contrib import admin

from .models import DeviceModel


@admin.register(DeviceModel)
class DeviceModelAdmin(admin.ModelAdmin):
    search_fields = ["name", "brand__name", "slug"]
    list_display = ["__str__", "category", "active"]
