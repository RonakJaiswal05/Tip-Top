"""Admin roles (A1): Owner, Manager, Front desk, Technician.

Each ModelAdmin declares `role_perms = {"view": [...], "add": [...], "change": [...], "delete": [...]}`; the command
`manage.py setup_roles` turns these into Django group permissions, so the permission matrix lives next to the
screens it controls. Row-level rules (a technician sees only requests assigned to them) are in get_queryset.

Matrix from the scope of work (section 7, A1):
                                  Owner  Manager  Front desk  Technician
  Change prices and part tiers      x      x
  Add, edit or hide devices         x      x
  Work the request inbox            x      x        x         assigned only
  Purchase contracts                x      x        x
  Withdrawals and consent log       x      x        view
  Texts, FAQ, hours, legal pages    x      x
  Media library                     x      x
  Users, roles and settings         x
  Exports and reports               x      x
"""
ROLES = ["Owner", "Manager", "Front desk", "Technician"]
ROLE_LABELS = {"Owner": "Inhaber", "Manager": "Filialleitung", "Front desk": "Empfang", "Technician": "Technik"}

ALL = ROLES
OWNER_MANAGER = ["Owner", "Manager"]
OWNER = ["Owner"]


def user_in(user, *groups) -> bool:
    if not getattr(user, "is_authenticated", False):
        return False
    if user.is_superuser:
        return True
    cache = getattr(user, "_tt_groups", None)
    if cache is None:
        cache = set(user.groups.values_list("name", flat=True))
        user._tt_groups = cache
    return bool(cache & set(groups))


class RoleAdminMixin:
    """Marker for ModelAdmins that declare role_perms (read by setup_roles)."""

    role_perms: dict = {}
