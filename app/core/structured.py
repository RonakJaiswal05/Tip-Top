"""schema.org data: LocalBusiness per shop (F10, section 10), FAQPage, and Service/Offer for model pages."""
import json

from django.conf import settings

DAY_URIS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def local_business(shop: dict, S, lang: str) -> dict:
    d = {
        "@type": ["ElectronicsStore", "LocalBusiness"],
        "@id": f"{settings.SITE_URL}/#shop-{shop['key']}",
        "name": f"TipTop Service 24 {shop['short']}",
        "url": f"{settings.SITE_URL}/{lang}/",
        "telephone": shop["tel"],
        "email": S.contact_email,
        "address": {"@type": "PostalAddress", "streetAddress": shop["street"], "postalCode": shop["postal_code"],
                    "addressLocality": shop["city"], "addressCountry": "DE"},
        "openingHoursSpecification": [
            {"@type": "OpeningHoursSpecification", "dayOfWeek": f"https://schema.org/{DAY_URIS[int(day)]}", "opens": o, "closes": c}
            for day, iv in shop["weekly"].items() for o, c in iv
        ],
        "priceRange": "€€",
        "parentOrganization": {"@type": "Organization", "name": "TLAMO GmbH", "vatID": "DE326279747"},
    }
    if shop.get("lat") is not None and shop.get("lng") is not None:
        d["geo"] = {"@type": "GeoCoordinates", "latitude": shop["lat"], "longitude": shop["lng"]}
    if shop.get("place_id"):
        d["hasMap"] = shop["maps"]
    if S.instagram_url:
        d["sameAs"] = [S.instagram_url]
    return d


def faq_page(faq: list[dict]) -> dict:
    return {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}} for f in faq
    ]}


def dump(items: list[dict]) -> str:
    # "<\/" keeps a "</script>" inside the data from ending the script element
    return json.dumps({"@context": "https://schema.org", "@graph": items}, ensure_ascii=False).replace("</", r"<\/")
