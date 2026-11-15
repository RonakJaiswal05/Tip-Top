"""Forms in both languages, spam protection, emails, Google Sheets and the consent log (F4, F12, F16, A6, A8)."""
import json
from unittest import mock

from django.core import mail
from django.test import Client, override_settings

from core.models import SiteSettings
from leads.models import Request, Withdrawal
from legal.models import ConsentRecord

from .base import SeededTestCase


class FormTests(SeededTestCase):
    def post(self, c, token, body):
        # run the after-commit jobs (staff email, Sheets) like in production
        with self.captureOnCommitCallbacks(execute=True):
            return c.post("/api/requests/", json.dumps(body), content_type="application/json", HTTP_X_CSRFTOKEN=token)

    def test_callback_in_both_languages(self):
        for lang in ("de", "en"):
            c, token, ts = self.fresh_client()
            r = self.post(c, token, {"kind": "callback", "lang": lang, "ts": ts, "name": f"Test {lang}", "phone": "+49 30 1234567",
                                     "device": "Apple iPhone 13", "repairs_text": "Display", "total": "149 €", "total_amount": 149,
                                     "repairs": [{"key": "display", "tier": "p", "name": "Display", "price": 149}]})
            self.assertEqual(r.status_code, 200, r.content)
            req = Request.objects.get(name=f"Test {lang}")
            self.assertEqual((req.kind, req.language, req.status), ("callback", lang, "new"))
            self.assertEqual(req.repairs[0]["price"], 149.0)
        self.assertEqual(len(mail.outbox), 2)  # staff notification for each
        self.assertIn("Rückruf", mail.outbox[0].subject)

    def test_request_form_with_and_without_javascript(self):
        c, token, ts = self.fresh_client()
        r = self.post(c, token, {"kind": "form", "lang": "en", "ts": ts, "name": "Ann", "phone": "0176 1234567", "category": "tablet",
                                 "device": "iPad Air 11 (M2)", "problem": "Cracked", "method": "spandau", "contact_via": "phone"})
        self.assertEqual(r.status_code, 200)
        req = Request.objects.get(name="Ann")
        self.assertEqual((req.method, req.contact_via, req.shop.key), ("spandau", "phone", "spandau"))
        # plain HTML form post
        r = c.post("/api/requests/", {"kind": "form", "lang": "de", "ts": ts, "name": "Ohne JS", "phone": "030 1234567",
                                      "method_i": "2", "via_i": "0", "back": "/de/anfrage/", "csrfmiddlewaretoken": token})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r["Location"], "/de/anfrage/?sent=1")
        self.assertEqual(Request.objects.get(name="Ohne JS").method, "pickup")
        self.assertIn("Danke", Client().get("/de/anfrage/?sent=1").content.decode())

    def test_validation(self):
        c, token, ts = self.fresh_client()
        self.assertEqual(self.post(c, token, {"kind": "callback", "ts": ts, "name": "", "phone": "0301234567"}).json()["field"], "name")
        self.assertEqual(self.post(c, token, {"kind": "callback", "ts": ts, "name": "A", "phone": "12"}).json()["field"], "phone")
        self.assertEqual(self.post(c, token, {"kind": "nope", "ts": ts}).status_code, 400)

    def test_spam_protection(self):
        c, token, ts = self.fresh_client()
        # honeypot: looks like success, nothing stored
        r = self.post(c, token, {"kind": "callback", "ts": ts, "name": "Bot", "phone": "030 1234567", "website": "http://spam"})
        self.assertEqual(r.json(), {"ok": True})
        self.assertFalse(Request.objects.filter(name="Bot").exists())
        # missing or forged timestamp
        with override_settings(FORM_MIN_SECONDS=2.5):
            self.assertEqual(self.post(c, token, {"kind": "callback", "ts": "forged", "name": "A", "phone": "030 1234567"}).json()["error"], "timing")
        # CSRF
        self.assertEqual(Client(enforce_csrf_checks=True).post("/api/requests/", "{}", content_type="application/json").status_code, 403)

    @override_settings(FORM_RATE_LIMIT=3)
    def test_rate_limit(self):
        c, token, ts = self.fresh_client()
        codes = [self.post(c, token, {"kind": "callback", "ts": ts, "name": f"R{i}", "phone": "030 1234567"}).status_code for i in range(5)]
        self.assertEqual(codes, [200, 200, 200, 429, 429])

    def test_withdrawal_confirmation_is_sent_immediately(self):
        for lang, word in (("de", "Eingangsbestätigung"), ("en", "Confirmation of receipt")):
            mail.outbox.clear()
            c, token, ts = self.fresh_client()
            r = self.post(c, token, {"kind": "withdrawal", "lang": lang, "ts": ts, "name": "Erika", "email": "erika@example.com",
                                     "reference": "A-10482", "device": "iPhone 13", "message": "Bitte stornieren"})
            body = r.json()
            self.assertTrue(body["mail_ok"])
            w = Withdrawal.objects.filter(request__language=lang).latest("received_at")
            self.assertIsNotNone(w.confirmation_sent_at)
            confirmation = next(m for m in mail.outbox if m.to == ["erika@example.com"])
            self.assertIn(word, confirmation.subject)
            self.assertIn("A-10482", confirmation.body)
            self.assertIn("Bitte stornieren", confirmation.body)
            self.assertRegex(confirmation.body, r"\d{1,2}:\d{2}")  # time of receipt
            self.assertEqual(w.confirmation_body, confirmation.body)  # on record in the admin

    def test_withdrawal_without_javascript_shows_receipt(self):
        c, token, ts = self.fresh_client()
        r = c.post("/api/requests/", {"kind": "withdrawal", "lang": "de", "ts": ts, "name": "Max", "email": "max@example.com",
                                      "reference": "12.11.2026", "back": "/de/vertrag-widerrufen/", "csrfmiddlewaretoken": token})
        self.assertEqual(r.status_code, 302)
        html = Client().get(r["Location"]).content.decode()
        self.assertIn("Dein Widerruf ist eingegangen", html)
        self.assertIn("12.11.2026", html)

    def test_withdrawal_mail_failure_is_retried_not_lost(self):
        c, token, ts = self.fresh_client()
        with mock.patch("leads.tasks.EmailMessage.send", side_effect=OSError("smtp down")), \
                mock.patch("leads.tasks.retry_withdrawal_confirmation.apply_async") as retry:
            r = self.post(c, token, {"kind": "withdrawal", "ts": ts, "name": "Eva", "email": "eva@example.com", "reference": "X"})
        self.assertFalse(r.json()["mail_ok"])
        self.assertTrue(retry.called)
        w = Withdrawal.objects.get(request__name="Eva")
        self.assertIn("smtp down", w.confirmation_error)

    def test_beacons_are_stored_but_not_actionable(self):
        c, token, ts = self.fresh_client()
        self.post(c, token, {"kind": "whatsapp", "ts": ts, "device": "Apple iPhone 13", "total": "149 €"})
        self.post(c, token, {"kind": "sale", "ts": ts, "device": "iPhone 14 Pro", "condition": "Gut"})
        self.assertEqual(Request.objects.filter(kind__in=["whatsapp", "sale"]).count(), 2)
        self.assertEqual(len(mail.outbox), 0)  # informational only: no staff email, no sheet row

    def test_google_sheet_row(self):
        s = SiteSettings.load()
        s.sheets_enabled, s.google_sheet_id = True, "sheet123"
        s.save()
        c, token, ts = self.fresh_client()
        with mock.patch("leads.tasks._append") as append:
            self.post(c, token, {"kind": "callback", "ts": ts, "name": "=HYPERLINK(1)", "phone": "030 1234567"})
        append.assert_called_once()
        sheet_id, tab, row = append.call_args.args
        self.assertEqual((sheet_id, tab), ("sheet123", "Anfragen"))
        self.assertIn("=HYPERLINK(1)", row)
        self.assertIsNotNone(Request.objects.get(name="=HYPERLINK(1)").sheet_synced_at)

    def test_google_sheet_failure_keeps_request_and_retries(self):
        s = SiteSettings.load()
        s.sheets_enabled, s.google_sheet_id = True, "sheet123"
        s.save()
        c, token, ts = self.fresh_client()
        with mock.patch("leads.tasks._append", side_effect=OSError("quota")):
            self.post(c, token, {"kind": "callback", "ts": ts, "name": "Sheetless", "phone": "030 1234567"})
        req = Request.objects.get(name="Sheetless")
        self.assertIsNone(req.sheet_synced_at)
        self.assertGreaterEqual(req.sheet_attempts, 1)
        with mock.patch("leads.tasks._append") as append:
            from leads.tasks import retry_unsynced

            retry_unsynced()
        self.assertTrue(append.called)

    def test_consent_log_without_ip(self):
        c, token, _ = self.fresh_client()
        r = c.post("/api/consent/", json.dumps({"id": "ab12cd34", "v": 1, "ts": "2026-11-15T10:00:00Z", "action": "accept", "lang": "en",
                                                 "choices": {"stats": True, "marketing": True}}), content_type="application/json",
                   HTTP_X_CSRFTOKEN=token, REMOTE_ADDR="203.0.113.9")
        self.assertEqual(r.status_code, 200)
        rec = ConsentRecord.objects.get(proof_id="ab12cd34")
        # statistics/marketing are switched off, so they can't be consented to
        self.assertEqual((rec.action, rec.stats, rec.marketing, rec.language), ("accept", False, False, "en"))
        self.assertNotIn("203.0.113.9", json.dumps(list(ConsentRecord.objects.values()), default=str), "no IP address stored")
        self.assertEqual(c.post("/api/consent/", json.dumps({"id": "<script>"}), content_type="application/json",
                                HTTP_X_CSRFTOKEN=token).status_code, 400)
