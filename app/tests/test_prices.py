"""Price accuracy (SOW F3, section 13): every model and repair against the price list."""
import json
import re
from decimal import Decimal

from django.test import Client

from catalog.models import DeviceModel, Price, PriceSource, RepairType, starting_price
from catalog.seed import load
from catalog.services import fmt_eur, is_from, min_price, price, services_for, snapshot

from .base import SeededTestCase


class PriceAccuracyTests(SeededTestCase):
    def test_catalogue_counts(self):
        snap = snapshot()
        self.assertEqual(len(snap["models"]), 435)  # client voice note of 17 Nov 2026
        self.assertEqual(len(snap["rep"]), 31)  # TMR sticks added
        self.assertEqual(len({m["brand"] for m in snap["models"]}), 22)
        self.assertEqual(len({m["slug"] for m in snap["models"]}), 435)  # "+" becomes "plus": no two models share a URL

    def test_every_price_matches_the_prototype(self):
        """All 435 models x every repair x both parts, as the prototype computed them."""
        snap = snapshot()
        expected = load()["PRICES"]
        by_key = {(m["cat"], m["brand"], m["name"]): m for m in snap["models"]}
        checked = 0
        for e in expected:
            m = by_key[(e["cat"], e["brand"], e["name"])]
            self.assertEqual(services_for(snap, m), e["services"], m["slug"])
            for key, v in e["prices"].items():
                if isinstance(v, list):
                    self.assertEqual(price(snap, m, key, "p"), v[0], f"{m['slug']} {key} premium")
                    self.assertEqual(price(snap, m, key, "o"), v[1], f"{m['slug']} {key} original")
                    checked += 2
                else:
                    self.assertEqual(price(snap, m, key), v, f"{m['slug']} {key}")
                    checked += 1
        self.assertGreater(checked, 3000)

    def test_from_flags(self):
        snap = snapshot()
        m = next(x for x in snap["models"] if x["slug"] == "apple-iphone-13")
        self.assertTrue(is_from(snap, m, "mainboard"))
        self.assertFalse(is_from(snap, m, "battery"))

    def test_json_endpoint_carries_the_same_prices(self):
        data = json.loads(Client().get("/api/catalog.json").content)
        for p in Price.objects.select_related("repair", "model")[:400]:
            v = data["prices"][str(p.model_id)][p.repair.key]
            got = v[{"premium": "p", "original": "o"}[p.tier]] if isinstance(v, dict) else v
            self.assertEqual(Decimal(str(got)), p.amount)

    def test_model_pages_show_every_price(self):
        snap = snapshot()
        for m in snap["models"][::9]:  # 20 models across all categories, both languages
            for lang, prefix in (("de", "/de/reparatur/"), ("en", "/en/repair/")):
                html = Client().get(f"{prefix}{m['slug']}/").content.decode()
                for key in services_for(snap, m):
                    tiers = ("p", "o") if snap["rep"][key]["tiers"] else ("p",)
                    for t in tiers:
                        v = price(snap, m, key, t)
                        if v is not None:
                            self.assertIn(fmt_eur(v, lang).replace(" ", "&nbsp;") if False else fmt_eur(v, lang), html,
                                          f"{lang} {m['slug']} {key} {t}")

    def test_home_stickers_use_lowest_prices(self):
        snap = snapshot()
        html = Client().get("/de/").content.decode()
        self.assertIn(fmt_eur(min_price(snap, "phone", "display"), "de"), html)
        for key in snap["top"]["phone"]:
            self.assertIn(fmt_eur(min_price(snap, "phone", key), "de"), html)

    def test_price_change_is_live_immediately(self):
        m = DeviceModel.objects.get(slug="apple-iphone-13")
        p = Price.objects.get(model=m, repair__key="battery")
        p.amount = Decimal("111")
        p.save()
        data = json.loads(Client().get("/api/catalog.json").content)
        self.assertEqual(data["prices"][str(m.pk)]["battery"], 111)
        self.assertIn("111", Client().get("/de/reparatur/apple-iphone-13/").content.decode())
        self.assertEqual(p.history.count(), 2)

    def test_starting_prices_follow_the_prototype_formula(self):
        # iPhone 14 (factor 1.1): battery base 99, weight .35 -> r9(99 * 1.1^.35)
        self.assertEqual(starting_price(99, 1.1, 0.35), 99)
        self.assertEqual(starting_price(219, 1.9, 1), 419)

    def test_faceid_and_jack_only_where_fitted(self):
        snap = snapshot()
        se = next(x for x in snap["models"] if x["name"] == "iPhone SE (2022)")
        a16 = next(x for x in snap["models"] if x["name"] == "Galaxy A16")
        self.assertNotIn("faceid", services_for(snap, se))
        self.assertIn("jack", services_for(snap, a16))
        self.assertNotIn("jack", services_for(snap, se))

    def test_console_lists_by_type(self):
        snap = snapshot()
        pad = next(x for x in snap["models"] if x["name"] == "DualSense controller")
        self.assertEqual(services_for(snap, pad), ["drift", "tmr", "cport", "battery", "buttons", "water"])
        ps5 = next(x for x in snap["models"] if x["name"] == "PlayStation 5")
        self.assertIn("tmr", services_for(snap, ps5))  # owner, 25 Nov 2026: sticks on the console page too

    def test_repairs_a_model_cannot_have(self):
        """The prototype's NOSV list: no fan or SSD where there is none, no battery in an AA-powered controller."""
        snap = snapshot()
        by = {(m["brand"], m["name"]): m for m in snap["models"]}
        cases = {("Sony", "PlayStation Portal"): ["fan", "ssd"], ("Nintendo", "Switch 2"): ["ssd"], ("Nintendo", "Joy-Con"): ["cport"],
                 ("Microsoft", "Xbox controller"): ["battery"], ("Apple", "MacBook Air 13 (M4)"): ["fan", "ssd"],
                 ("Apple", "MacBook Pro 14 (M4)"): ["ssd"]}
        for key, gone in cases.items():
            have = services_for(snap, by[key])
            for k in gone:
                self.assertNotIn(k, have, key)
        self.assertIn("fan", services_for(snap, by[("Apple", "MacBook Pro 14 (M4)")]))

    def test_repair_photos_follow_the_device(self):
        """iPhone photos only for Apple phones; other phones, tablets, laptops and consoles never get a phone photo."""
        from catalog.services import repair_photo

        snap = dict(snapshot())
        snap["rimg"] = {"phone_apple": {"display": "rep-display"}, "phone": {"display": "and-display"},
                        "tablet": {"display": "tab-display"}, "laptop": {}, "console": {"hdmi": "con-hdmi"}}
        self.assertEqual(repair_photo(snap, "phone", "Apple", "display"), "rep-display")
        self.assertEqual(repair_photo(snap, "phone", "Samsung", "display"), "and-display")
        self.assertEqual(repair_photo(snap, "tablet", "Apple", "display"), "tab-display")
        self.assertIsNone(repair_photo(snap, "laptop", "Apple", "display"))


class ImportTests(SeededTestCase):
    def test_round_trip_export_import_changes_nothing(self):
        from catalog.pricelist import export_rows, import_rows

        rep = import_rows(export_rows(), dry_run=True)
        self.assertEqual((rep.created, rep.updated, rep.removed), (0, 0, 0))
        self.assertFalse(rep.unknown_models or rep.unknown_columns or rep.bad_cells)

    def test_long_layout_and_cell_formats(self):
        from catalog.pricelist import import_rows

        rows = [["Kategorie", "Marke", "Modell", "Reparatur", "Teil", "Preis"],
                ["Smartphone", "Apple", "iPhone 13", "Display", "Original", "229,00 €"],
                ["Handy", "Samsung", "Galaxy S23", "Akku", "", "ab 89"],
                ["Konsole", "Sony", "PlayStation 5", "HDMI", "", "auf Anfrage"],
                ["Smartphone", "Apple", "iPhone 99", "Akku", "", "99"]]
        rep = import_rows(rows)
        self.assertEqual(rep.updated, 2)
        self.assertEqual(rep.removed, 1)
        self.assertEqual(len(rep.unknown_models), 1)
        p = Price.objects.get(model__slug="samsung-galaxy-s23", repair__key="battery")
        self.assertEqual((p.amount, p.is_from, p.source), (Decimal("89.00"), True, PriceSource.IMPORT))
        self.assertFalse(Price.objects.filter(model__slug="sony-playstation-5", repair__key="hdmi").exists())
