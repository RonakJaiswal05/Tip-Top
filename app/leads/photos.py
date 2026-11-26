"""Buyback photos (F9, client feedback of 17 Nov 2026).

The browser already shrinks each photo to 1600 px JPEG. The server never keeps the uploaded bytes: every photo is
decoded, turned upright, re-encoded as a fresh JPEG without any metadata (no EXIF, no GPS, no camera details) and
stored outside the public media folder. Staff see them in the admin only; they are deleted after
settings.OFFER_PHOTO_DAYS days unless a purchase contract follows.
"""
import io
import logging
from datetime import timedelta

from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone
from PIL import Image, ImageOps, UnidentifiedImageError

log = logging.getLogger(__name__)

MAX_SIDE = 1600
THUMB_SIDE = 320
Image.MAX_IMAGE_PIXELS = 40_000_000  # refuse decompression bombs


class PhotoError(ValueError):
    pass


def _encode(im: Image.Image, side: int, quality: int) -> tuple[bytes, int, int]:
    im = im.copy()
    im.thumbnail((side, side), Image.LANCZOS)
    buf = io.BytesIO()
    # a new image object carries no info dict, so nothing from the original file (EXIF, GPS, XMP, ICC) is written
    clean = Image.new("RGB", im.size)
    clean.paste(im)
    clean.save(buf, "JPEG", quality=quality, optimize=True, progressive=True)
    return buf.getvalue(), clean.width, clean.height


def clean_photo(f) -> tuple[bytes, bytes, int, int]:
    """Return (jpeg, thumbnail, width, height) for an uploaded file, or raise PhotoError."""
    if f.size > settings.OFFER_PHOTO_MAX_BYTES:
        raise PhotoError("size")
    try:
        im = Image.open(f)
        if im.format not in ("JPEG", "PNG", "WEBP", "MPO"):
            raise PhotoError("type")
        im = ImageOps.exif_transpose(im)  # keep the orientation, then drop the EXIF data itself
        im = im.convert("RGB")
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as e:
        raise PhotoError("type") from e
    big, w, h = _encode(im, MAX_SIDE, 85)
    small, _, _ = _encode(im, THUMB_SIDE, 75)
    return big, small, w, h


def save_photos(req, files) -> int:
    from .models import RequestPhoto

    n = 0
    for f in files[: settings.OFFER_PHOTO_MAX]:
        big, small, w, h = clean_photo(f)
        p = RequestPhoto(request=req, width=w, height=h)
        p.image.save("photo.jpg", ContentFile(big), save=False)
        p.thumb.save("thumb.jpg", ContentFile(small), save=False)
        p.save()
        n += 1
    return n


def delete_expired(now=None) -> int:
    """Delete buyback photos older than OFFER_PHOTO_DAYS whose request has no purchase contract."""
    from .models import RequestPhoto

    now = now or timezone.now()
    old = RequestPhoto.objects.filter(created_at__lt=now - timedelta(days=settings.OFFER_PHOTO_DAYS),
                                      request__contracts__isnull=True)
    n = 0
    for p in old:
        p.delete()  # the post_delete signal removes the files
        n += 1
    return n
