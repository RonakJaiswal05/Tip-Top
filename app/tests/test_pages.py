"""Every page in both languages, SEO tags, sitemap, redirects, security headers (F13, section 10)."""
import json
import re

from django.test import Client, override_settings

from core.routes import LEGAL_KEYS, page_url

from .base import SeededTestCase

PAGES = ["home", "request", "models"] + LEGAL_KEYS + ["withdraw"]


class PageTests(SeededTestCase):
    def test_all_pages_in_both_languages(self):
        c = Client()
        for lang in ("de", "en"):
            for key in PAGES:
                url = page_url(key, lang)
                r = c.get(url)
                self.assertEqual(r.status_code, 200, url)
                html = r.content.decode()
                self.assertIn(f'<html lang="{lang}">', html)
                self.assertIn(f'<link rel="canonical" href="http://testserver{url}">'.replace("http://testserver", ""), html.replace("http://localhost:8000", ""))
                self.assertIn('hreflang="de"', html)
                self.assertIn('hreflang="en"', html)
                self.assertNotRegex(html, r'data-t="', "texts are rendered on the server")
                data = self.page_data(html)
                self.assertEqual(data["lang"], lang)

    def test_no_untranslated_keys_leak(self):
        for lang in ("de", "en"):
            html = Client().get(page_url("home", lang)).content.decode()
            text = re.sub(r"<script.*?</script>|<[^>]+>", " ", html, flags=re.S)
            self.assertNotRegex(text, r"\b(?:nav|cat|cc|wd|lg|mp|lf)_[a-z_]+\b", lang)

    def test_root_and_language_choice(self):
        c = Client()
        self.assertEqual(c.get("/", HTTP_ACCEPT_LANGUAGE="en").headers["Location"], "/de/")
        c.cookies["tt-lang"] = "en"
        self.assertEqual(c.get("/").headers["Location"], "/en/")
        self.assertEqual(Client().get("/anfrage").headers["Location"], "/de/anfrage/")

    def test_wrong_language_slug_redirects(self):
        self.assertEqual(Client().get("/de/privacy/").headers["Location"], "/de/datenschutz/")
        self.assertEqual(Client().get("/en/reparatur/apple-iphone-13/").headers["Location"], "/en/repair/apple-iphone-13/")

    def test_model_pages_structured_data(self):
        html = Client().get("/de/reparatur/apple-iphone-13/").content.decode()
        ld = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S).group(1))
        types = [str(x["@type"]) for x in ld["@graph"]]
        self.assertEqual(sum("LocalBusiness" in t for t in types), 1)  # one shop since 17 Nov 2026
        biz = next(x for x in ld["@graph"] if "LocalBusiness" in str(x["@type"]))
        self.assertEqual((biz["vatID"], biz["founder"]["name"]), ("DE357158413", "Mostafa Khodr"))
        self.assertNotIn("TLAMO", html)
        self.assertGreater(types.count("Service"), 15)
        self.assertIn("BreadcrumbList", types)
        self.assertEqual(Client().get("/de/reparatur/does-not-exist/").status_code, 404)

    def test_sitemap(self):
        xml = Client().get("/sitemap.xml").content.decode()
        self.assertEqual(xml.count("<url>"), (3 + len(LEGAL_KEYS)) * 2 + 435 * 2)
        self.assertIn('hreflang="x-default"', xml)

    def test_robots(self):
        self.assertIn("Disallow: /", Client().get("/robots.txt").content.decode())
        with override_settings(ENVIRONMENT="production"):
            txt = Client().get("/robots.txt").content.decode()
            self.assertIn("Disallow: /admin/", txt)
            self.assertNotIn("Disallow: /\n", txt)

    def test_shopify_redirects(self):
        c = Client()
        self.assertEqual(c.get("/policies/legal-notice").headers["Location"], "/de/impressum/")
        self.assertEqual(c.get("/policies/privacy-policy").headers["Location"], "/de/datenschutz/")
        self.assertEqual(c.get("/products/iphone-13-reparatur-akku").headers["Location"], "/de/reparatur/apple-iphone-13/")
        self.assertEqual(c.get("/collections/macbook-air-13-anfang-2015").headers["Location"], "/de/reparatur/#laptop-apple")
        # the P30 lite is in the catalogue since 17 Nov 2026, so its old product page lands on its own model page
        self.assertEqual(c.get("/products/huawei-p30-lite-reparatur-akku").headers["Location"], "/de/reparatur/huawei-p30-lite/")
        self.assertEqual(c.get("/pages/kontakt").status_code, 301)

    def test_security_headers_and_no_third_party_requests(self):
        r = Client().get("/de/")
        csp = r.headers["Content-Security-Policy"]
        self.assertIn("default-src 'self'", csp)
        self.assertNotIn("unsafe-inline", csp.split("style-src")[0])  # scripts: no inline except the hashed one
        html = r.content.decode()
        for host in ("fonts.googleapis", "fonts.gstatic", "googletagmanager", "facebook", "google-analytics", "matomo"):
            self.assertNotIn(host, html)
        self.assertNotIn("sessionid", r.cookies, "visitors never get a session")

    def test_withdrawal_link_in_every_footer(self):
        for lang in ("de", "en"):
            for key in PAGES:
                html = Client().get(page_url(key, lang)).content.decode()
                self.assertIn(f'class="fwd" href="{page_url("withdraw", lang)}"', html)

    def test_maintenance_mode(self):
        from core.models import SiteSettings

        s = SiteSettings.load()
        s.maintenance_mode = True
        s.save()
        r = Client().get("/de/")
        self.assertEqual(r.status_code, 503)
        self.assertEqual(Client().get("/admin/login/").status_code, 200)
