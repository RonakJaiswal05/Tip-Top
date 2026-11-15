"""Shared fixtures: the full catalogue, shops, texts and legal pages, seeded once per test class."""
import json
import re

from django.core.cache import cache
from django.test import Client, TestCase

from catalog.seed import seed_catalog
from content.seed import seed_faq, seed_texts
from legal.seed import seed_legal
from shops.seed import seed_holidays, seed_shops


class SeededTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cache.clear()
        seed_catalog(log=lambda *_: None)
        seed_shops()
        seed_holidays()
        seed_texts()
        seed_faq()
        seed_legal()
        from django.core.management import call_command

        call_command("setup_roles", stdout=open(__import__("os").devnull, "w"))

    def setUp(self):
        cache.clear()

    @staticmethod
    def page_data(html: str) -> dict:
        return json.loads(re.search(r'<script id="tt-data" type="application/json">(.*?)</script>', html, re.S).group(1))

    def fresh_client(self):
        c = Client(enforce_csrf_checks=True)
        r = c.get("/de/")
        return c, c.cookies["csrftoken"].value, self.page_data(r.content.decode())["ts"]
