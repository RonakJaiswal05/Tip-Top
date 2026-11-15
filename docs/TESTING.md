# Test results (15 November 2026, local build)

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
