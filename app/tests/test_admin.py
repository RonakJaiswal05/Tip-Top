"""Admin roles, two-factor sign-in, price tools, devices (A1, A3, A4, A12)."""
from decimal import Decimal

from django.contrib.auth.models import Group, User
from django.test import Client
from django_otp.plugins.otp_static.models import StaticDevice
from django_otp.plugins.otp_totp.models import TOTPDevice

from catalog.models import Brand, Category, DeviceModel, Price
from leads.models import Request

from .base import SeededTestCase

PW = "Sehr-sicheres-Passwort-1"


class AdminTests(SeededTestCase):
    def user(self, role, otp=False):
        u = User.objects.create_user(role.replace(" ", "").lower(), password=PW, is_staff=True)
        u.groups.add(Group.objects.get(name=role))
        if otp:
            TOTPDevice.objects.create(user=u, name="app", confirmed=True)
            StaticDevice.objects.create(user=u, name="codes", confirmed=True).token_set.create(token="code1234")
        return u

    def login(self, role, otp=False):
        u = self.user(role, otp)
        c = Client()
        data = {"username": u.username, "password": PW, "next": "/admin/"}
        if otp:
            data["otp_token"] = "code1234"
        r = c.post("/admin/login/", data)
        return c, r

    def test_owner_needs_second_factor(self):
        c, r = self.login("Owner")
        self.assertEqual(r.headers["Location"], "/admin/otp/setup/")  # no device yet -> set it up first
        self.assertEqual(c.get("/admin/").status_code, 302)
        c2 = Client()
        r = c2.post("/admin/login/", {"username": "owner", "password": PW, "next": "/admin/"})
        TOTPDevice.objects.create(user=User.objects.get(username="owner"), confirmed=True)
        r = Client().post("/admin/login/", {"username": "owner", "password": PW, "next": "/admin/"})
        self.assertEqual(r.status_code, 200)  # code missing
        self.assertContains(r, "Authenticator")

    def test_role_matrix(self):
        paths = {
            "prices": "/admin/catalog/price/editor/", "devices": "/admin/catalog/devicemodel/add/", "inbox": "/admin/leads/request/?art=actionable",
            "contracts": "/admin/leads/purchasecontract/", "withdrawals": "/admin/leads/withdrawal/", "consent": "/admin/legal/consentrecord/",
            "texts": "/admin/content/contentblock/", "media": "/admin/content/mediaasset/", "hours": "/admin/shops/shop/",
            "legal": "/admin/legal/legalpageversion/", "settings": "/admin/core/sitesettings/1/change/", "users": "/admin/auth/user/",
        }
        allowed = {
            "Owner": set(paths),
            "Manager": set(paths) - {"settings", "users"},
            "Front desk": {"inbox", "contracts", "withdrawals", "consent"},
            "Technician": {"inbox"},
        }
        from core.models import SiteSettings

        SiteSettings.load()
        for role, ok in allowed.items():
            c, _ = self.login(role, otp=role in ("Owner", "Manager"))
            for name, path in paths.items():
                code = c.get(path).status_code
                self.assertEqual(code == 200, name in ok, f"{role} {name} -> {code}")

    def test_technician_sees_only_assigned_requests(self):
        tech = self.user("Technician")
        Request.objects.create(kind="callback", name="Mine", phone="1", assignee=tech)
        Request.objects.create(kind="callback", name="Other", phone="2")
        c = Client()
        c.post("/admin/login/", {"username": tech.username, "password": PW, "next": "/admin/"})
        html = c.get("/admin/leads/request/?art=actionable").content.decode()
        self.assertIn("Mine", html)
        self.assertNotIn("Other", html)

    def test_price_editor_history_and_bulk(self):
        c, _ = self.login("Manager", otp=True)
        m = DeviceModel.objects.get(slug="apple-iphone-13")
        p = Price.objects.get(model=m, repair__key="battery")
        data = {f"p_{p.repair_id}_standard": "105"}
        r = c.post(f"/admin/catalog/price/editor/?model={m.pk}", data)
        self.assertEqual(r.status_code, 302)
        p.refresh_from_db()
        self.assertEqual(p.amount, Decimal("105"))
        h = p.history.first()
        self.assertEqual((h.history_user.username, h.history_change_reason), ("manager", "Preisübersicht"))
        # bulk: +10 % on Apple batteries, rounded to ...9
        apple = Brand.objects.get(name="Apple")
        phone = Category.objects.get(key="phone")
        battery = p.repair
        r = c.post("/admin/catalog/price/bulk/", {"category": phone.pk, "brand": apple.pk, "repair": battery.pk, "tier": "", "mode": "pct",
                                                  "value": "10", "rounding": "9", "apply": "1"})
        self.assertEqual(r.status_code, 302)
        p.refresh_from_db()
        self.assertEqual(p.amount, Decimal("119"))  # 105 * 1.1 = 115.5 -> 119

    def test_new_device_gets_starting_prices_and_page(self):
        c, _ = self.login("Owner", otp=True)
        r = c.post("/admin/catalog/devicemodel/add/", {
            "category": Category.objects.get(key="phone").pk, "brand": Brand.objects.get(name="Apple").pk, "name": "iPhone 18 Pro",
            "price_level": "flagship", "has_face_id": "on", "popular": "on", "active": "on", "sort_order": "-10",
        })
        self.assertEqual(r.status_code, 302, r.content[:2000])
        m = DeviceModel.objects.get(name="iPhone 18 Pro")
        self.assertGreater(m.prices.count(), 15)
        self.assertEqual(Client().get("/de/reparatur/apple-iphone-18-pro/").status_code, 200)
        self.assertTrue(m.prices.filter(repair__key="faceid").exists())

    def test_audit_log_records_changes(self):
        from auditlog.models import LogEntry

        c, _ = self.login("Owner", otp=True)
        from content.models import ContentBlock

        b = ContentBlock.objects.get(key="h1a")
        c.post(f"/admin/content/contentblock/{b.pk}/change/", {"group": b.group, "text_de": "Handy hin?", "text_en": b.text_en, "note": ""})
        e = LogEntry.objects.get_for_object(b).first()
        self.assertEqual(e.actor.username, "owner")
        self.assertIn("text_de", e.changes_dict)
        self.assertIn("Handy hin?", Client().get("/de/").content.decode())
