from django.contrib import admin
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from core.roles import ROLES

# Permissions for models whose admin we don't own (audit log, lockouts, 2FA devices) and custom ones
EXTRA = {
    ("auditlog", "logentry"): {"view": ["Owner", "Manager"]},
    ("axes", "accessattempt"): {"view": ["Owner"], "delete": ["Owner"]},
    ("axes", "accessfailurelog"): {"view": ["Owner"]},
    ("axes", "accesslog"): {"view": ["Owner"]},
    ("otp_totp", "totpdevice"): {"view": ["Owner"], "delete": ["Owner"]},
    ("otp_static", "staticdevice"): {"view": ["Owner"], "delete": ["Owner"]},
}
CUSTOM = {("leads", "complete_purchasecontract"): ["Owner", "Manager", "Front desk"]}


class Command(BaseCommand):
    help = "Create the four roles (Owner, Manager, Front desk, Technician) with the permission matrix from the scope of work."

    def handle(self, *args, **opts):
        groups = {name: Group.objects.get_or_create(name=name)[0] for name in ROLES}
        grant = {name: set() for name in ROLES}

        def add(app_label, model_name, action, roles):
            try:
                ct = ContentType.objects.get(app_label=app_label, model=model_name)
                perm = Permission.objects.get(content_type=ct, codename=f"{action}_{model_name}")
            except (ContentType.DoesNotExist, Permission.DoesNotExist):
                return
            for r in roles:
                grant[r].add(perm.pk)

        for model, model_admin in admin.site._registry.items():
            perms = getattr(model_admin, "role_perms", None) or {}
            for action, roles in perms.items():
                add(model._meta.app_label, model._meta.model_name, action, roles)
                if action in ("add", "change", "delete") and roles:
                    add(model._meta.app_label, model._meta.model_name, "view", roles)
            # simple-history: history views follow the model's view permission
        for (app_label, model_name), perms in EXTRA.items():
            for action, roles in perms.items():
                add(app_label, model_name, action, roles)
        for (app_label, codename), roles in CUSTOM.items():
            perm = Permission.objects.filter(content_type__app_label=app_label, codename=codename).first()
            if perm:
                for r in roles:
                    grant[r].add(perm.pk)
        # Technicians edit requests and need to look up devices in that form
        add("catalog", "devicemodel", "view", ["Technician"])

        for name, g in groups.items():
            g.permissions.set(grant[name])
            self.stdout.write(self.style.SUCCESS(f"{name}: {len(grant[name])} permissions"))
