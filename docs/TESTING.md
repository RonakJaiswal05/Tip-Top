# Test results

## 26 November 2026 (evening): client feedback of 17 Nov, call of 25 Nov, chat changes of 26 Nov

How to run: `cd app && uv run python manage.py test tests --settings=tiptop.settings.test` (61 tests, about 60 s).

| Area | What was checked | Result |
|------|------------------|--------|
| Catalogue | 435 models, 22 brands, 31 repairs, unique slugs ("+" → "plus"); every price and repair list equals the prototype's price() and servicesFor(), including the NOSV exclusions (PlayStation Portal, Switch, Joy-Con, Xbox controller, Apple silicon MacBooks) and TMR on consoles | Pass |
| Calculator in the browser | All 435 models opened via deep link, every label of the repair step compared with the server, no extra repairs shown | 6,657 / 6,657 labels match in German and in English |
| Repair photos | iPhone 17 Pro → `rep-*`, Galaxy S26 Ultra → `and-*`, iPad Air → `tab-*`, MacBook Air → `lap-*` (no fan card), PS5 Pro / Switch 2 / DualSense → `con-*` or a tile; side panel never shows a phone for other devices | Pass |
| Multi-select (17 Nov #8) | Tapping toggles, bottom bar "2 ausgewählt · 318 €", "Preis ansehen", "Weitere Reparatur hinzufügen" keeps the choices, deep link carries all repairs | Pass |
| Search bar (25 Nov #2) | Live suggestions with price, repair words ignored ("s24 akku" → Galaxy S24 family with battery prices), arrow keys + Enter open the calculator at the price step | Pass |
| Buyback with photos (17 Nov #10) | Browser: 2 photos shrunk to 1600 px, name + phone, sent as multipart, request in the inbox. Tests: EXIF/GPS and camera name gone, turned upright, stored under PRIVATE_ROOT (not /media/), max 6, non-images refused with nothing saved, staff-only view (no-store), deleted after 30 days unless a purchase contract is linked, file removed from disk | Pass |
| One shop, facts | No "Spandau", "Havelstraße", "TLAMO" or mobile number on the pages; structured data with owner and VAT ID; hours one per line with today bold and "Sonntag geschlossen"; request form "Im Laden vorbeibringen" / "Einschicken" | Pass |
| Price list per category (25 Nov #13) | Owner/Manager edit all models × main repairs in one table, only changed cells saved, history reason "Preisliste (Tabelle)", impossible repairs shown as "–" and ignored if posted, bad input saves nothing; Front desk and Technician get 403 | Pass |
| No sideways scrolling | 320, 390, 768, 1024, 1440, 2560 px: home (DE, EN), request page, model page, legal pages, calculator; also no clipped text (the German shop card and footer hours needed two CSS fixes at 320–380 px) | Pass |
| Accessibility (axe-core 4.10) | Home with the suggestion list open, calculator repair step with the bottom bar, buyback form with a photo | 0 violations |
| Hero film | Plays on desktop with mouse only, muted with "Ton an", photo stays underneath; phones keep the photo | Pass |

Not re-run this time: Lighthouse (the new logo SVG and the desktop film should be measured on the server).

## 15 November 2026, first build

How to run: `cd app && uv run python manage.py test tests --settings=tiptop.settings.test` (45 tests, about 20 s).
Browser checks: see `app/tests/browser/README.md`.

| Area | What was checked | Result |
|------|------------------|--------|
| Price accuracy (F3) | All 180 models × every repair × Premium/Original against the prototype's own price() (3,000+ prices); JSON endpoint and model pages show the same numbers; a saved price is live on the next request | Pass |
| Calculator in the browser | The real calculator (site.js) opened for all 180 models via deep link, every label of the repair step compared with the server's price list | 2,692 / 2,692 labels match in German and in English |
| Price import | Export → import round trip changes nothing; long layout with "ab", "auf Anfrage", unknown model | Pass |
| Forms (F4, F12) | Callback and request form in German and English, without JavaScript, validation, staff email, Google Sheets row (and retry on failure), WhatsApp/sale beacons | Pass |
| Spam protection | Honeypot (silent), signed timestamp, rate limit (429), CSRF | Pass |
| Withdrawal (F16, § 356a BGB) | Two steps, confirmation email sent inside the request with content, date and time (German and English), receipt page without JavaScript, mail failure is retried and visible in the admin | Pass |
| Consent log (A8) | Decision stored with proof ID, version, choices; no IP address; optional categories cannot be consented to while switched off | Pass |
| Opening hours (F1, F10) | Every hour of the week 21–27 Dec 2026 incl. two Berlin holidays; next opening skips Sunday and holidays; special hours win; different hours per shop show in all texts | Pass |
| Roles (A1) | Owner/Manager need the second factor; access matrix for all four roles; technicians only see assigned requests | Pass |
| Admin price tools (A3, A4, A12) | Price editor with history (user, reason), bulk +10 % with …9 rounding, new device gets starting prices and a model page, audit log entry | Pass |
| Pages and SEO (F13, section 10) | Every page 200 in both languages, html lang, canonical, hreflang, no untranslated keys, sitemap (378 URLs), robots, model page JSON-LD (2 × LocalBusiness, Service + Offer, BreadcrumbList), Shopify redirects, maintenance mode | Pass |
| Security | CSP without inline scripts (one hashed), no third-party hosts in the HTML, no session cookie for visitors | Pass |
| No sideways scrolling (F15) | 320, 390, 768, 1024, 1440, 2560 px: home, calculator open with callback form, model pages, model index, privacy, cookies, terms, request page, withdrawal | Pass on every page and width |
| Keyboard | Calculator opens from the header button, focus moves into the dialog and stays there, Enter picks a tile, model search gets focus, Escape closes and focus returns, scroll unlocked | Pass |
| Accessibility (axe-core 4.10, WCAG 2.1 AA + best practice) | Home, model page, request page, withdrawal page, open calculator | 0 violations (after moving the footer headings to h3 and the WhatsApp button into the footer) |
| Lighthouse 13.6, mobile, production-like local server (gzip, hashed static, no CDN) | Home `/de/` | Performance 96, Accessibility 100, Best practices 100; LCP 1.4 s, CLS 0, TBT 220 ms |
| | Model page `/de/reparatur/apple-iphone-13/` | Performance 93, Accessibility 100, Best practices 100; LCP 1.2 s, CLS 0.001, TBT 320 ms |

SEO scores locally (69/66) are low only because `robots.txt` blocks all crawlers outside production on purpose;
everything else in the SEO category passes.

Not tested yet (needs the server, the client or real devices):
- Lighthouse and WebPageTest on the live server over 4G; real Android and iPhone (VoiceOver, NVDA).
- Voice input in Chrome, Edge and Safari (needs HTTPS and a microphone).
- Real Google Sheets, Brevo and Places API calls (all mocked here; keys missing).
- The 100 real customer phrases for the describe box (client has not sent them yet).
- The remaining 8 of the 14 SOW screen sizes (360×800, 430×932, landscape phones, 820, 1024×1366, 1280, 1920).
