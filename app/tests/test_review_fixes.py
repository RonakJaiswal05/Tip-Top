"""Regression tests for the findings of the code review of 15 Nov 2026."""
import json

from django.contrib.auth.models import Group, User
from django.test import Client

from catalog.models import DeviceModel, Price
from catalog.pricelist import export_rows, import_rows
from core.cache import bump, site_version
from leads.models import Request

from .base import SeededTestCase


class ReviewFixTests(SeededTestCase):
    def test_no_open_redirect_through_back(self):
        c, token, ts = self.fresh_client()
        for back in ("//evil.example/de/anfrage/", "https://evil.example/", "/\\evil.example"):
            r = c.post("/api/requests/", {"kind": "form", "ts": ts, "name": "A", "phone": "030 1234567", "back": back,
                                          "csrfmiddlewaretoken": token})
            self.assertEqual(r["Location"], "/de/anfrage/?sent=1", back)

    def test_admin_survives_braces_in_repair_names(self):
        req = Request.objects.create(kind="callback", name="X", phone="1", repairs=[{"name": "{0} {x}", "price": 10}])
        u = User.objects.create_user("o", password="p-very-long-123", is_staff=True)
        u.groups.add(Group.objects.get(name="Front desk"))
        c = Client()
        c.force_login(u)
        r = c.get(f"/admin/leads/request/{req.pk}/change/")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "{0} {x}")

    def test_inbox_can_show_all_kinds(self):
        Request.objects.create(kind="whatsapp", device="WA-only")
        Request.objects.create(kind="callback", name="CB-only", phone="1")
        u = User.objects.create_user("f", password="p-very-long-123", is_staff=True)
        u.groups.add(Group.objects.get(name="Front desk"))
        c = Client()
        c.force_login(u)
        default = c.get("/admin/leads/request/")
        self.assertEqual(default.status_code, 200)  # no redirect
        self.assertContains(default, "CB-only")
        self.assertNotContains(default, "WA-only")
        self.assertContains(c.get("/admin/leads/request/?art=all"), "WA-only")

    def test_site_version_never_repeats(self):
        a = site_version()
        bump()
        b = site_version()
        self.assertGreater(b, a)
        self.assertGreater(b, 10**15)  # a timestamp, not a counter starting at 1

    def test_import_respects_face_id_and_export_round_trip_is_clean(self):
        rep = import_rows([["Kategorie", "Marke", "Modell", "Reparatur", "Teil", "Preis"],
                           ["Smartphone", "Apple", "iPhone SE (2022)", "Face ID", "", "199"]])
        self.assertEqual(rep.created, 0)
        self.assertEqual(len(rep.not_offered), 1)
        self.assertFalse(Price.objects.filter(model__name="iPhone SE (2022)", repair__key="faceid").exists())
        rep = import_rows(export_rows(), dry_run=True)
        self.assertEqual((rep.created, rep.updated, rep.removed, len(rep.not_offered)), (0, 0, 0, 0))

    def test_bare_shopify_paths_redirect(self):
        self.assertEqual(Client().get("/blogs").status_code, 301)
        self.assertEqual(Client().get("/collections").status_code, 301)

    def test_seed_bumps_the_version(self):
        from catalog.seed import seed_catalog

        before = site_version()
        with self.captureOnCommitCallbacks(execute=True):
            seed_catalog(log=lambda *_: None)
        self.assertNotEqual(site_version(), before)
        data = json.loads(Client().get("/api/catalog.json").content)
        m = DeviceModel.objects.get(slug="apple-iphone-13")
        self.assertIn("battery", data["prices"][str(m.pk)])
