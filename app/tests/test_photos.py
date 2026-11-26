"""Buyback offer with photos (client feedback of 17 Nov 2026): metadata stripped, stored privately, staff only,
deleted after 30 days unless a purchase contract follows."""
import io
from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django.utils import timezone
from django_otp.plugins.otp_static.models import StaticDevice
from django_otp.plugins.otp_totp.models import TOTPDevice
from PIL import Image

from leads.models import PurchaseContract, Request, RequestPhoto
from leads.photos import delete_expired

from .base import SeededTestCase


def jpeg_with_gps(size=(2400, 1800)) -> bytes:
    """A JPEG carrying EXIF with a GPS position and a camera name, like a phone photo."""
    im = Image.new("RGB", size, (200, 30, 30))
    exif = Image.Exif()
    exif[0x0110] = "Test Phone 15"  # camera model
    exif[0x0112] = 6  # orientation: rotate 90
    gps = {1: "N", 2: (52.0, 31.0, 40.0), 3: "E", 4: (13.0, 19.0, 50.0)}
    exif[0x8825] = gps
    buf = io.BytesIO()
    im.save(buf, "JPEG", exif=exif.tobytes())
    return buf.getvalue()


class PhotoTests(SeededTestCase):
    def send(self, c, token, ts, files, **extra):
        data = {"kind": "offer", "lang": "de", "ts": ts, "name": "Mia", "phone": "0176 5555555", "category": "phone",
                "device": "Handy iPhone 14 Pro", "condition": "Gut", "repairs_text": "Ankauf-Angebot, Zustand: Gut", **extra}
        data["photos"] = files
        with self.captureOnCommitCallbacks(execute=True):
            return c.post("/api/requests/", data, HTTP_X_CSRFTOKEN=token, HTTP_ACCEPT="application/json")

    def test_photos_are_cleaned_and_private(self):
        c, token, ts = self.fresh_client()
        raw = jpeg_with_gps()
        self.assertIn(b"Test Phone 15", raw)
        files = [SimpleUploadedFile(f"p{i}.jpg", raw, content_type="image/jpeg") for i in range(2)]
        r = self.send(c, token, ts, files)
        self.assertEqual(r.status_code, 200, r.content)
        req = Request.objects.get(name="Mia")
        self.assertEqual((req.kind, req.shop.key, req.condition), ("offer", "moabit", "Gut"))
        self.assertTrue(req.is_actionable)
        self.assertEqual(req.photos.count(), 2)
        p = req.photos.first()
        path = Path(p.image.path)
        # outside the public media folder, inside the private one
        self.assertTrue(str(path).startswith(str(settings.PRIVATE_ROOT)))
        self.assertFalse(str(path).startswith(str(settings.MEDIA_ROOT)))
        data = path.read_bytes()
        self.assertNotIn(b"Test Phone 15", data)
        im = Image.open(io.BytesIO(data))
        self.assertFalse(im.getexif())  # no EXIF at all, so no GPS
        self.assertEqual(max(im.size), 1600)
        self.assertEqual(im.size, (1200, 1600))  # turned upright from the orientation tag, then the tag dropped
        # staff email mentions the photos
        self.assertIn("Fotos: 2", mail.outbox[-1].body)

    def test_limits_and_bad_files(self):
        c, token, ts = self.fresh_client()
        self.assertEqual(self.send(c, token, ts, []).status_code, 400)
        many = [SimpleUploadedFile(f"p{i}.jpg", jpeg_with_gps((200, 200)), content_type="image/jpeg") for i in range(7)]
        self.assertEqual(self.send(c, token, ts, many).status_code, 400)
        bad = [SimpleUploadedFile("x.jpg", b"<?php echo 1; ?>", content_type="image/jpeg")]
        r = self.send(c, token, ts, bad)
        self.assertEqual((r.status_code, r.json()["error"]), (400, "photo"))
        self.assertFalse(Request.objects.filter(kind="offer").exists())  # nothing half-saved
        self.assertEqual(self.send(c, token, ts, [SimpleUploadedFile("a.jpg", jpeg_with_gps((300, 300)))], phone="12").status_code, 400)

    def test_only_staff_see_photos(self):
        c, token, ts = self.fresh_client()
        self.send(c, token, ts, [SimpleUploadedFile("a.jpg", jpeg_with_gps((400, 300)), content_type="image/jpeg")])
        p = RequestPhoto.objects.get()
        url = f"/admin/leads/request/{p.request_id}/photo/{p.pk}/"
        self.assertEqual(Client().get(url).status_code, 302)  # to the login page
        u = User.objects.create_user("desk", password="Sehr-sicheres-Passwort-1", is_staff=True)
        u.groups.add(Group.objects.get(name="Front desk"))
        TOTPDevice.objects.create(user=u, name="app", confirmed=True)
        StaticDevice.objects.create(user=u, name="codes", confirmed=True).token_set.create(token="code1234")
        staff = Client()
        staff.post("/admin/login/", {"username": "desk", "password": "Sehr-sicheres-Passwort-1", "otp_token": "code1234", "next": "/admin/"})
        r = staff.get(url)
        self.assertEqual((r.status_code, r["Content-Type"]), (200, "image/jpeg"))
        self.assertIn("no-store", r["Cache-Control"])
        self.assertIn("private", r["Cache-Control"])
        self.assertEqual(staff.get(url + "?thumb=1").status_code, 200)
        self.assertContains(staff.get(f"/admin/leads/request/{p.request_id}/change/"), url)

    def test_deleted_after_30_days_unless_bought(self):
        c, token, ts = self.fresh_client()
        for name in ("Alt", "Gekauft", "Neu"):
            self.send(c, token, ts, [SimpleUploadedFile("a.jpg", jpeg_with_gps((300, 300)), content_type="image/jpeg")], name=name)
        old = timezone.now() - timedelta(days=31)
        RequestPhoto.objects.filter(request__name__in=["Alt", "Gekauft"]).update(created_at=old)
        bought = Request.objects.get(name="Gekauft")
        PurchaseContract.objects.create(offer_request=bought, seller_first_name="G", seller_last_name="K", seller_street="x",
                                        seller_postal_code="10553", seller_city="Berlin", seller_birth_date="1990-01-01",
                                        id_number="L01X00T47", device="iPhone", imei="1", price=100)
        gone = Path(RequestPhoto.objects.get(request__name="Alt").image.path)
        self.assertTrue(gone.exists())
        self.assertEqual(delete_expired(), 1)
        self.assertFalse(gone.exists())  # the file goes too, not only the database row
        self.assertEqual(sorted(RequestPhoto.objects.values_list("request__name", flat=True)), ["Gekauft", "Neu"])
        self.assertTrue(Request.objects.filter(name="Alt").exists())  # the request itself stays (6-month rule)
