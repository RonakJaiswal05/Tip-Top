"""Call with the owner, 27 Nov 2026: one joystick repair, WhatsApp status buttons, admin wishes (repair types with
combos, tiers on/off, repairs per device, delete models, password reset), the click-to-load map and the phone film."""
from decimal import Decimal
from urllib.parse import unquote

from django.contrib.auth.models import User
from django.core import mail
from django.core.cache import cache
from django.core.files.base import ContentFile
from django.test import Client

from catalog.models import Category, CategoryPrice, DeviceModel, Price, RepairOption, RepairType, Tier
from catalog.services import model_repairs, services_for, snapshot
from core.models import SiteSettings
from leads.models import Request

from .base import SeededTestCase
from .test_admin import AdminTests

PW = "Sehr-sicheres-Passwort-1"


def inline_mgmt(prefix: str, total: int = 0, initial: int = 0) -> dict:
    return {f"{prefix}-TOTAL_FORMS": str(total), f"{prefix}-INITIAL_FORMS": str(initial),
            f"{prefix}-MIN_NUM_FORMS": "0", f"{prefix}-MAX_NUM_FORMS": "1000"}


class JoystickTests(SeededTestCase):
    def test_one_joystick_repair(self):
        snap = snapshot()
        self.assertNotIn("drift", snap["rep"])
        self.assertEqual(snap["rep"]["tmr"]["de"], "TMR-Joystick-Reparatur (driftfrei)")
        by = {(m["brand"], m["name"]): m for m in snap["models"]}
        for key in (("Sony", "PlayStation 5"), ("Sony", "DualSense controller"), ("Nintendo", "Switch 2")):
            have = services_for(snap, by[key])
            self.assertIn("tmr", have, key)
            self.assertNotIn("drift", have, key)
        self.assertNotIn("drift", snap["top"]["console"])


class InboxWhatsAppTests(AdminTests.__base__):
    user = AdminTests.user
    login = AdminTests.login

    def test_status_buttons_in_the_customers_language(self):
        de = Request.objects.create(kind="callback", name="Lena", phone="0176 1234567", device="iPhone 13", language="de")
        en = Request.objects.create(kind="callback", name="Sam", phone="+44 7700 900123", device="Pixel 8", language="en")
        c, _ = self.login("Front desk")
        html = c.get("/admin/leads/request/?art=all").content.decode()
        self.assertIn("https://wa.me/491761234567?text=", html)
        self.assertIn("Dein%20Ger%C3%A4t%20ist%20in%20Bearbeitung.", html)
        self.assertIn("Dein%20Ger%C3%A4t%20ist%20fertig%20und%20kann%20abgeholt%20werden.", html)
        self.assertIn("Your%20device%20is%20ready%20for%20pickup.", html)
        page = c.get(f"/admin/leads/request/{de.pk}/change/").content.decode()
        self.assertIn("WhatsApp: In Bearbeitung", page)
        self.assertIn("WhatsApp: Abholbereit", page)
        self.assertTrue(en.pk)


class RepairTypeAdminTests(AdminTests.__base__):
    user = AdminTests.user
    login = AdminTests.login

    def test_owner_adds_a_combo_repair_with_starting_prices(self):
        c, _ = self.login("Owner", otp=True)
        phone = Category.objects.get(key="phone")
        data = {
            "key": "", "name_de": "Backcover + Display", "name_en": "Back cover + screen", "desc_de": "", "desc_en": "",
            "icon": "display", "order": "40", "duration_minutes": "", "warranty_months": "12",
            "price_weight": "0.8", "default_from": "",
            **inline_mgmt("options", 1), "options-0-category": phone.pk, "options-0-console_type": "", "options-0-requires": "",
            "options-0-order": "30",
            **inline_mgmt("categoryprice_set", 1), "categoryprice_set-0-category": phone.pk,
            "categoryprice_set-0-tier": "standard", "categoryprice_set-0-amount": "299",
            **inline_mgmt("names"),
        }
        r = c.post("/admin/catalog/repairtype/add/", data)
        self.assertEqual(r.status_code, 302, r.content[:3000])
        combo = RepairType.objects.get(name_de="Backcover + Display")
        self.assertEqual(combo.key, "backcover-plus-display")  # "+" becomes "plus", as in model URLs
        ip13 = DeviceModel.objects.get(brand__name="Apple", name="iPhone 13")
        self.assertIn(combo, model_repairs(ip13))
        self.assertTrue(Price.objects.filter(model=ip13, repair=combo).exists())  # starting price from 299 € and the level
        cache.clear()
        snap = snapshot()
        m = next(x for x in snap["models"] if x["id"] == ip13.pk)
        self.assertIn("backcover-plus-display", services_for(snap, m))
        self.assertEqual(Client().get("/de/reparatur/apple-iphone-13/").status_code, 200)

    def test_delete_repair_types_including_the_diagnosis(self):
        c, _ = self.login("Owner", otp=True)
        diag = RepairType.objects.get(key="diagnosis")
        r = c.post(f"/admin/catalog/repairtype/{diag.pk}/delete/", {"post": "yes"})
        self.assertEqual(r.status_code, 302)
        self.assertFalse(RepairType.objects.filter(key="diagnosis").exists())
        cache.clear()
        self.assertNotIn("diagnosis", snapshot()["rep"])
        for url in ("/de/", "/de/reparatur/apple-iphone-13/", "/api/catalog.json"):
            self.assertEqual(Client().get(url).status_code, 200, url)

    def test_tiers_on_and_off_keep_the_prices(self):
        battery = RepairType.objects.get(key="battery")
        ip13 = DeviceModel.objects.get(brand__name="Apple", name="iPhone 13")
        before = Price.objects.get(model=ip13, repair=battery, tier=Tier.STANDARD).amount
        battery.has_tiers = True
        battery.save()
        tiers = dict(Price.objects.filter(model=ip13, repair=battery).values_list("tier", "amount"))
        self.assertEqual(tiers, {Tier.PREMIUM: before, Tier.ORIGINAL: before})
        self.assertTrue(CategoryPrice.objects.filter(repair=battery, tier=Tier.PREMIUM).exists())
        Price.objects.filter(model=ip13, repair=battery, tier=Tier.PREMIUM).update(amount=Decimal("89"))
        battery.has_tiers = False
        battery.save()
        tiers = dict(Price.objects.filter(model=ip13, repair=battery).values_list("tier", "amount"))
        self.assertEqual(tiers, {Tier.STANDARD: Decimal("89")})  # the Premium price becomes the single price
        display = RepairType.objects.get(key="display")
        display.has_tiers = False
        display.save()
        cache.clear()
        snap = snapshot()
        m = next(x for x in snap["models"] if x["id"] == ip13.pk)
        self.assertFalse(snap["rep"]["display"]["tiers"])
        self.assertIsInstance(snap["prices"][str(ip13.pk)]["display"], (int, float))
        self.assertEqual(Client().get("/de/reparatur/apple-iphone-13/").status_code, 200)
        self.assertTrue(m)


class DeviceAdminTests(AdminTests.__base__):
    user = AdminTests.user
    login = AdminTests.login

    def device_form(self, m, **extra):
        data = {"category": m.category_id, "brand": m.brand_id, "name": m.name, "release_year": "", "price_level": m.price_level,
                "console_type": m.console_type, "popular": "on" if m.popular else "", "active": "on", "sort_order": m.sort_order}
        for f in ("has_face_id", "has_touch_id", "has_headphone_jack"):
            if getattr(m, f):
                data[f] = "on"
        data.update(extra)
        return {k: v for k, v in data.items() if v not in ("", None)}

    def test_choose_repairs_and_features_per_device(self):
        c, _ = self.login("Owner", otp=True)
        ip13 = DeviceModel.objects.get(brand__name="Apple", name="iPhone 13")
        keys = ["display", "battery", "keyboard"]  # keyboard is a laptop repair: an extra for this phone
        ids = list(RepairType.objects.filter(key__in=keys).values_list("id", flat=True))
        r = c.post(f"/admin/catalog/devicemodel/{ip13.pk}/change/", self.device_form(ip13, repairs=ids, has_touch_id="on"))
        self.assertEqual(r.status_code, 302, r.content[:3000])
        ip13.refresh_from_db()
        self.assertTrue(ip13.has_touch_id)
        self.assertEqual({x.key for x in model_repairs(ip13, with_diagnosis=False)}, set(keys))
        self.assertEqual(list(ip13.extra_repairs.values_list("key", flat=True)), ["keyboard"])
        cache.clear()
        snap = snapshot()
        m = next(x for x in snap["models"] if x["id"] == ip13.pk)
        self.assertEqual(set(services_for(snap, m)), set(keys))
        self.assertIn("T", m["fl"])

    def test_touch_id_repair_only_on_touch_id_devices(self):
        c, _ = self.login("Owner", otp=True)
        phone = Category.objects.get(key="phone")
        tid = RepairType.objects.create(name_de="Touch ID Reparatur", name_en="Touch ID repair", order=50)
        RepairOption.objects.create(category=phone, repair=tid, requires="touch_id", order=50)
        se = DeviceModel.objects.get(brand__name="Apple", name="iPhone 13")
        self.assertNotIn(tid, model_repairs(se))
        se.has_touch_id = True
        se.save()
        self.assertIn(tid, model_repairs(se))
        self.assertTrue(c)

    def test_owner_deletes_a_model(self):
        c, _ = self.login("Owner", otp=True)
        m = DeviceModel.objects.get(brand__name="Apple", name="iPhone 13")
        r = c.post(f"/admin/catalog/devicemodel/{m.pk}/delete/", {"post": "yes"})
        self.assertEqual(r.status_code, 302)
        self.assertFalse(DeviceModel.objects.filter(pk=m.pk).exists())
        cache.clear()
        self.assertEqual(Client().get("/de/reparatur/apple-iphone-13/").status_code, 404)


class PasswordResetTests(SeededTestCase):
    def test_reset_by_email_and_rate_limit(self):
        u = User.objects.create_user("mostafa", email="owner@example.com", password=PW, is_staff=True)
        c = Client()
        self.assertContains(c.get("/admin/login/"), "/admin/password_reset/")
        r = c.post("/admin/password_reset/", {"email": "owner@example.com"})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        link = next(w for w in mail.outbox[0].body.split() if "/admin/reset/" in w)
        path = "/" + link.split("://", 1)[1].split("/", 1)[1]
        r = c.get(path, follow=True)
        r = c.post(r.redirect_chain[-1][0], {"new_password1": "Neues-Passwort-2026!", "new_password2": "Neues-Passwort-2026!"})
        self.assertEqual(r.status_code, 302)
        u.refresh_from_db()
        self.assertTrue(u.check_password("Neues-Passwort-2026!"))
        for _ in range(8):
            c.post("/admin/password_reset/", {"email": "owner@example.com"})
        self.assertLessEqual(len(mail.outbox), 1 + 4)  # 5 per hour and address of the sender, then silence
        self.assertTrue(unquote(path))


class MapAndFilmTests(SeededTestCase):
    def test_map_loads_only_after_a_click(self):
        r = Client().get("/de/")
        html = r.content.decode()
        self.assertIn('id="shopMap"', html)
        self.assertIn("Karte laden", html)
        self.assertNotIn("<iframe", html)  # nothing from Google before the click
        self.assertIn("output=embed", html)  # the address the script loads after the click
        self.assertIn("frame-src https://www.google.com", r.headers["Content-Security-Policy"])
        self.assertIn("Schreib uns dein Problem", html)

    def test_phone_film_button_data(self):
        S = SiteSettings.load()
        S.hero_video.save("hero.mp4", ContentFile(b"\x00" * 10), save=False)
        S.hero_video_mobile.save("film-m.mp4", ContentFile(b"\x00" * 10), save=False)
        S.save()
        cache.clear()
        html = Client().get("/de/").content.decode()
        self.assertIn('data-film-m="', html)
        self.assertIn('data-video="', html)
