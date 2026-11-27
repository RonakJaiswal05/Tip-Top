# TipTop Service 24: new website

Context for Claude Code. Read this whole file before changing anything. Last updated 26 November 2026, evening (see "Client feedback of 17 November 2026", "Client voice note of 17 November 2026 (evening)", "Call with the owner, 25 November 2026", "Changes of 26 November 2026 (evening)" and "Working with the claude.ai chat" below).

## The job in one paragraph

Build and launch the production website for TipTop Service 24, a phone, tablet, laptop and console repair business in Berlin, by **Tuesday 17 November 2026**. The front end is already designed and working as a prototype (`prototype/index.html`). Your job is to turn it into a Django site with a real back end and admin, deploy it to a GoDaddy VPS in Europe and switch the domain over. The agreed scope is in `docs/` (English and German PDFs). Ronak builds and owns the project on the agency side; he is the person you are working with.

## The client

| | |
|---|---|
| Trading name | TipTop Service 24 |
| Business | **Sole trader (Einzelunternehmer, no GmbH, not in the commercial register): Mostafa Khodr** (K-H-O-D-R, confirmed 25 Nov 2026), trading as **TipTop Service 24 Handy Reparatur Berlin**. **TLAMO GmbH has nothing to do with the business any more** (client, 15 Nov 2026): it must not appear anywhere |
| The shop (only one) | Beusselstraße 18, 10553 Berlin-Moabit (master workshop in the same place). Phone 030 814 757 91 (+49 30 81475791). **The Spandau shop (Havelstraße 8) is gone from the site** |
| Business WhatsApp | **The shop landline 030 814 757 91** (owner, 25 Nov 2026: "nur 030 überall"). Link format: `https://wa.me/493081475791?text=...`. The mobile +49 176 72746296 must not appear anywhere. Test that the link opens the shop's WhatsApp Business chat before launch |
| Email | **tiptophandyreparatur@gmail.com** (25 Nov 2026; nobody has access to the old info@tiptophandyreparatur.de). Later: create info@ on the domain and forward it to the Gmail address, then switch the site to info@ |
| VAT ID | **DE357158413** (confirmed 25 Nov 2026) |
| Domain | tiptophandyreparatur.de (currently a Shopify store) |
| Instagram | instagram.com/tiptopservice24 |
| Facts used in copy | In Moabit since 2009, **more than 20,000 customers**, own board-level workshop (micro-soldering since 2013), **up to 12 months guarantee**, mail-in with free return. **No pickup service** (the free pickup within 5 km is removed everywhere) |

**Opening hours:** Mon to Sat 10:00 to 20:00, Sunday closed (site and Google profile agree).

**Google ratings** (Google Business Profile, checked 15 Nov 2026):
- 4.9 from 321 reviews, place_id `ChIJA6sIHRNRqEcRdYbk2bTKeB4`, listed as "Meisterwerkstatt TipTop Service 24 Handy Reparatur Berlin"

The hero and the shop card show this rating. (The Spandau profile is not used any more.)

## What already exists

- `prototype/index.html`: the complete front end as one page with hash routes. Open it in a browser. This is the design source of truth: markup, CSS, copy (DE and EN), interactions and motion. Port it, don't redesign it.
- `prototype/TipTop-Service-24-final.html`: the same thing as one self-contained file (images and fonts embedded), for sharing.
- `prototype/img/`: photos, each in a full size and a `-s` phone size (760 px wide). **Real photos from the client:** the four workshop pictures (`lab-solder`, `lab-ic`, `lab-water`, `lab-data`) and the shop front (`shop-moabit`, a night photo, low resolution until the retouched version arrives). The rest were generated in ChatGPT and get replaced as real photos arrive; the client wants **himself** in the repair pictures and will send a photo. Prompts and file names are in `prototype/src/imgs4.js`.
- `prototype/fonts/`: Archivo variable font (width and weight axes), self-hosted, Latin and Latin Extended subsets. Open Font License.
- `prototype/src/`: how the prototype is assembled (see "Prototype build" below).
- `docs/TipTop-Service-24-Scope-of-Work.pdf` (English) and `docs/TipTop-Service-24-Leistungsbeschreibung.pdf` (German, plain language). Features F1 to F16, admin modules A1 to A12, each with "Done when" criteria. Treat these as the acceptance criteria.
- A live preview of the prototype is published as a private Claude artifact (Ronak has the link).

### Prototype routes (hash based, become real URLs)

`#top` home, `#anfrage` repair request page, `#admin` admin preview (any login works), `#impressum`, `#datenschutz`, `#agb`, `#widerruf`, `#vertrag-widerrufen` (opens the withdrawal form), `#cookies`, `#barrierefreiheit`.

### What the prototype fakes (must become real)

- Requests, withdrawals and admin edits are stored in the visitor's `localStorage` (`tt-reqs`, `tt-ovr`, `tt-added`). Replace with server APIs and the database.
- The admin preview is client-side only. Replace with the Django admin plus the custom screens described in the SOW.
- Google ratings are a hard-coded snapshot (`prototype/src/gmb4.js`). Replace with a daily fetch from the Google Places API.
- The "Image prompts" button and drawer (`#imgBtn`, `#drawer`) is a design-time tool. Remove it from production.
- The footer link "Geschäftskunden" points to the old Shopify page `/pages/geschaftskunde-werden`, which disappears at launch. Ask Ronak whether to build a simple business-customer page or redirect it.

## Stack and architecture

- Python 3.13 (pin it with uv), **Django 5.2 LTS**, PostgreSQL (Ubuntu's packaged version is fine), Redis plus Celery with concurrency 1 for background jobs, Gunicorn behind Nginx, TLS from Let's Encrypt (certbot).
- Server-rendered Django templates. Keep the prototype's vanilla JavaScript; no front-end framework and no build step on the server.
- i18n with German as the default and English second: `/de/...` and `/en/...`, `hreflang` tags, language switch remembers the choice.
- Static files and media served by Nginx. Responsive images: generate a phone size and a desktop size on upload (WebP or AVIF plus JPEG fallback) and keep the prototype's `srcset`/`sizes` logic from `hydrate4.js`.

### Data model (suggested)

`Shop` (name, address, phone, WhatsApp, geo, Google place_id, cached rating and count, fetched_at), `OpeningHours` per shop and weekday, `SpecialHours` and Berlin holidays, `Category` (phone, tablet, laptop, console), `Brand` (name, slug, **logo upload**, order), `DeviceModel` (category, brand, name, release year, price level, flags: Face ID, headphone jack, console type, active, photo), `RepairType` (key, DE/EN names with per-category overrides, duration, warranty months, photo, order), `Price` (model, repair, tier: standard, premium or original, amount, is_from) with full history and rollback (django-simple-history), `Request` (kind: callback, form, withdrawal, sale; all fields from the forms; for sale requests up to 6 **photos** in a private `RequestPhoto` model; language; source; status pipeline New, Contacted, Booked, In repair, Ready for pickup, Collected, Lost with reason; shop; assignee; notes), `PurchaseContract` (Ankauf: seller ID details, IMEI, checklist, signed PDF), `Withdrawal`, `ConsentRecord` (proof id, version, choices, timestamp, no IP address), `FAQ`, `ContentBlock` (DE/EN texts), `LegalPage` with versions, `MediaAsset`, `SiteSettings` (WhatsApp number, emails, Google Sheet id, feature toggles), audit log.

Seed the catalogue from the prototype: `prototype/src/js/engine.js` holds the services (`SV`, `SV_CAT`), which repairs apply to which device (`LISTS`, `CON`) and the model list with price levels (`M`), 180 models across 18 brands and 30 repair types. Prices in the prototype are placeholders until the client's price list arrives; write an import command for their spreadsheet (CSV or Excel).

### Admin roles

Owner, Manager, Front desk, Technician. The permission matrix is in the SOW (section 7, A1). Two-factor sign-in (TOTP, django-otp) for Owner and Manager.

## Integrations

- **WhatsApp**: click-to-chat links with prefilled text (no API). Message templates are in the prototype copy (`wa_msg`, `wa_sell`, `wa_pick`, `wa_general`).
- **Google Sheets**: append every request to the shop's sheet with a service account (gspread). Retry on failure. Sheet id goes in SiteSettings.
- **Email**: transactional email through an EU-hosted provider (Brevo suggested). New-request alerts, daily summary, and the **withdrawal confirmation sent immediately** with content, date and time. Set up SPF, DKIM and DMARC for the domain without touching the existing MX records.
- **Google ratings**: Places API (New) Place Details, fields `rating` and `userRatingCount`, once a day per shop, cached in `Shop`. Show "Google" attribution and link to the profile. Do not copy review texts onto the site.
- **Matomo**: deferred while the server has 2 GB RAM (see Hosting). While it is not running, remove the "Statistik" category from the cookie banner and the Matomo sections from the privacy and cookie pages.
- **Google Ads / Meta Pixel**: only if the client runs ads, and only after marketing consent. Otherwise remove the "Marketing" category and its legal text too.

## Legal requirements (Germany)

All legal texts are drafted in German and English in `prototype/src/legal_de.js` and `legal_en.js`. Move them into `LegalPage` records. Yellow `<mark class="fill">` spots are placeholders the client must fill or confirm (owner's name spelling, commercial register entry only if he is a registered e. K., VAT ID, Handwerksrolle entry, GoDaddy contracting entity and data-centre country). Since 17 Nov 2026 the texts name the sole owner (`LG_OWNER`, `LG_FIRM` in `legal_h.js`) instead of TLAMO GmbH, have no "Geschäftsführer", no second shop, no pickup service, a 12-month guarantee, GoDaddy instead of Hetzner, and a paragraph on photos sent for buyback offers (deleted after 30 days if no purchase). **Everything must be reviewed by the client's lawyer before launch.** German is legally binding; the English pages say so.

- Impressum under § 5 DDG. The EU online dispute platform link is removed on purpose (the platform closed on 20 July 2025); keep the consumer arbitration sentence.
- Privacy policy (GDPR). The hosting section now names GoDaddy with placeholders for the contracting entity and the data-centre country; fill them in from GoDaddy's data processing agreement once the server is bought.
- Cookie consent under § 25 TDDDG and the DSK guidance: "Alle ablehnen" and "Alle akzeptieren" equal in size and colour on the first layer, settings by category, proof id stored, ask again after 12 months, no optional script before consent, delete optional cookies on withdrawal. Keep the prototype's behaviour (`legal4.js`) and POST each decision to `/api/consent` for the consent log.
- **Withdrawal button (§ 356a BGB, in force since 19 June 2026)**: "Vertrag widerrufen" in the footer of every page, two steps (form, then "Widerruf bestätigen"), immediate confirmation email with content and timestamp, entry in the admin.
- Terms (AGB) for repairs and device purchases, withdrawal policy with the model form, cookie policy, accessibility statement (BFSG; MLBF Magdeburg as authority; client may be exempt as a micro-enterprise).
- Voice input shows a one-time notice before using the browser's speech recognition.
- Short privacy notes under every form (already in the prototype).
- No request to any third party before consent: fonts and images self-hosted.

### Brand logos

The brand cabinet should show the real logos (Apple, Samsung, Google, Xiaomi, Huawei, OnePlus, Oppo, Sony, Motorola, Lenovo, HP, Dell, ASUS, Acer, Microsoft, MSI, PlayStation, Xbox, Nintendo, Steam). **Do not draw or generate logos.** Use the official files the client or Ronak provides (brand press or media pages). The prototype already has the slot: files go in `prototype/img/brands/<slug>.svg` (list in `img/brands/README.txt`) and the slug is added to `BRAND_LOGOS_READY` in `brands4.js`. In Django, use the `Brand.logo` upload; without a logo the drawer shows the name. Under the cabinet there is a note that the brands belong to their owners and TipTop is not an authorised service partner. **Ask the client whether they are an authorised partner of any brand**; if they are, change that note.

## Hosting

- **GoDaddy VPS, self-managed, Linux, Europe region, no control panel.** Recommended plan to start: 1 vCPU, 2 GB RAM, 40 GB NVMe (₹649 a month on a 3-year term on GoDaddy India, plus GST). GoDaddy allows upgrading later from the VPS dashboard (permanent, no downgrades, short downtime), so start small. Ronak is buying it; ask him for the IP address and SSH access. Ideally the account is in the client's name, since the owner signs the data processing agreement.
- Choose the latest Ubuntu LTS GoDaddy offers. GoDaddy picks the country inside Europe; note it for the privacy policy.
- Set up for 2 GB: 2 GB swap file, Gunicorn with 2 to 3 workers, Celery concurrency 1, Redis with `maxmemory 64mb`, PostgreSQL tuned small (for example `shared_buffers=256MB`). No Matomo until the upgrade.
- Security: SSH keys only, root login off, ufw (22, 80, 443), fail2ban, unattended security upgrades, security headers, rate limits on forms and admin login.
- Backups: nightly `pg_dump` plus media, copied off the server, 30 days kept. Test a restore before launch. GoDaddy snapshots are a second layer.
- Staging and production on the same VPS (separate databases and systemd services) is fine for now.
- Monitoring: uptime checks with alerts; error tracking in an EU region.
- The project's Git repository should belong to the client (or be transferable to them).

### Launch steps

Lower DNS TTL early. Find out where tiptophandyreparatur.de is registered (ask Ronak). At go-live, point the A/AAAA records to the VPS, issue TLS, add 301 redirects from the old Shopify URLs (at least `/policies/legal-notice` → `/de/impressum`, `/policies/privacy-policy` → `/de/datenschutz`, `/pages/*`, `/products/*` and `/collections/*` to the closest new pages; fetch the old sitemap first), submit the new sitemap in Google Search Console, and update the website link in both Google Business Profiles if it changes. Leave email (MX) records alone.

## Pages and features to build

Everything in the SOW. Short list: home (hero with Google rating, device picker, describe box with voice, repairs and prices, brand cabinet, before and after, workshop, sell your device, shops with live open status and ratings, FAQ, footer), the four-step price calculator (opens over any page and is deep-linkable), the `/anfrage` request page (plus a QR code PNG for print), **model pages** for every model in both languages (for example `/de/reparatur/apple-iphone-13/`) with all prices and LocalBusiness/Service structured data, the six legal pages, the withdrawal function, the cookie banner, and the admin (dashboard, prices with history and bulk tools and import/export, devices, repair types, request inbox with pipeline, purchase contracts, withdrawals and consent log, content, media, settings, audit log).

Targets: LCP under 2.5 s on a mid-range Android over 4G, INP under 200 ms, CLS under 0.1, Lighthouse mobile performance 90 or more, WCAG 2.1 AA, no sideways scrolling at any of the 14 test sizes (320×568 up to 2560×1440, listed in the SOW section 13).

## Design and copy rules

- Colours: ink `#12141C`, paper `#FFFFFF`, fog `#F1F3F6`, cobalt `#3048F0`, lemon `#FFE14D`; categories phone `#3D69E5`, tablet `#FC80B3`, laptop `#1FBB8A`, console `#FC691E`. Font: Archivo, headings at `font-stretch:112%` and weight 800+.
- German is the default language. Customer-facing copy uses "du". The official withdrawal model text stays in "Sie". Anything addressed to the client (SOW, admin help) uses "Sie".
- Plain, specific copy. Sentence case. No all-caps labels, no "→" in buttons, no filler claims. Never invent reviews, ratings, numbers or testimonials.
- Respect `prefers-reduced-motion`. Keep the prototype's focus handling (Escape closes dialogs, focus returns).

## Prototype build (only if the prototype itself needs changes)

```
cd prototype/src
python build4.py        # src3.html + modules + patches -> src4.html
python assemble.py      # splices js/*.js -> ../index.html and _check.js
node --check _check.js  # syntax check
python make_standalone.py   # optional: ../TipTop-Service-24-final.html (needs Pillow)
```

`build4.py` does exact-string replacements on `src3.html` and fails loudly if a target string is missing. Patches run in order: `patch_dev.py` (mobile menu, image hydration), `patch_legal.py` (legal pages, consent, withdrawal, fonts), `patch_gmb.py` (Google ratings, logo slots, WhatsApp number, per-shop phone), `patch_feedback.py` + `feedback.css` (client feedback of 17 Nov 2026), `patch_nov17.py` (device-specific repair pictures, image prompts 20 to 37, clean logo), `patch_nov26.py` + `nov26.css` (call with the owner, 25 Nov 2026), `patch_hero_video.py` (desktop hero film, call text "Ruf uns an", 26 Nov 2026 evening). `make_standalone.py` also embeds `img/hero-loop.mp4` in the single file.

## Client feedback of 17 November 2026

From the owner's voice notes and messages (15 and 16 Nov). The prototype already has all of it; the live site must match:

1. **TLAMO GmbH removed everywhere** (legal pages, footer ©, emails, PDFs, structured data, admin texts). Business: "TipTop Service 24 Handy Reparatur Berlin", owner Mostafa Khodr. Footer: "© 2026 TipTop Service 24 Handy Reparatur Berlin".
2. **One shop only: Beusselstraße 18, Berlin-Moabit.** Spandau removed from shops, hero text, meta description, footer, Google rating, request form options, legal texts, sitemap/structured data. Shops section heading "Unser Laden in Moabit" / "Our shop in Moabit", one wide card (photo left, details right).
3. **Guarantee up to 12 months** (was 24): hero facts, display tier text, price summary, FAQ, AGB § 10.
4. **No free pickup.** Removed from hero facts, "ways to repair" (now: walk in, ask on WhatsApp with a photo, send it in), request form ("Im Laden vorbeibringen" / "Einschicken"), AGB § 7 (now "Einsendung"), privacy policy, withdrawal texts, accessibility statement.
5. **More than 20,000 customers** (was 15,000) in the workshop note.
6. **New models:** iPhone 17e, iPhone 18 Pro, iPhone 18 Pro Max, iPhone Duo (the foldable; no Face ID repair listed, aliases "iphone fold"). Base iPhone 18 and 18e come in spring 2027, add them then.
7. **Controllers:** new repair "TMR-Sticks (driftfrei)" / "TMR sticks (no more drift)" for every controller (DualSense, DualShock 4, Xbox controller, Joy-Con), placeholder €79. Describe box understands "tmr", "hall effect", "PS5 Controller", "PS4 Controller". Controller repairs now show as big cards.
8. **Repairs step: pick several at once.** Tapping a repair toggles it (check badge, coloured ring), a bar at the bottom shows "2 ausgewählt · 518 €" and "Preis ansehen". "Weitere Reparatur hinzufügen" on the price step goes back with the choices kept.
9. **Language switch visible on phones**: a globe button with the other language ("EN"/"DE") next to "Preis berechnen" below 600 px; the logo text hides below 560 px so nothing overflows down to 320 px.
10. **Buyback (Ankauf) with photos:** "Foto aufnehmen" (camera, phones only) and "Fotos hinzufügen" (gallery), up to 6, thumbnails with remove buttons. With photos, name + phone appear and "Fotos senden und Angebot holen" sends the request; WhatsApp stays as the alternative. Photos are shrunk in the browser (1600 px JPEG). Live site: multipart upload, server re-encodes and **strips EXIF/GPS**, stores privately (not under public media), admin shows thumbnails with the request, deleted automatically after 30 days if no purchase contract follows.
11. **Real photos:** workshop cards and the shop front use the owner's photos (see "What already exists").
12. **WhatsApp** number also in the footer.
13. **Brand logos** supplied by Ronak: `prototype/img/brands/*.svg` (20 brands) in the brand cabinet, no white plates. Don't draw or download others; Honor, Nothing, Fairphone and Realme have no logo yet and stay out of the cabinet.

## Client voice note of 17 November 2026 (evening)

The owner was unhappy with the pace: models missing, phone photos on laptop and tablet repairs, and the logo cut out of the sign photo. All of this is now in the prototype (`patch_nov17.py`, `js/engine.js`, `js/parse.js`); the live site must match:

1. **Catalogue: 435 models, 22 brands** (was 184 and 18), each brand grouped by series, newest first. Added older and current Samsung (S10 to S25 FE, Note 10/20, Z Fold/Flip 3 to 7 FE, A05s to A56), Pixel 4a to 10 Pro Fold, Xiaomi/Redmi/Poco, Huawei P/Mate/Pura/Nova, OnePlus 8 to 15 and Nord, Oppo Find/Reno/A, Sony Xperia 1/5/10 IV to VII, Motorola Edge/razr/moto g/e, and new phone brands **Honor, Nothing, Fairphone, Realme**; older iPads (7th gen onward), Galaxy Tab S6 Lite to S10, more Lenovo/Xiaomi/Huawei tablets; laptop series per brand (ThinkBook, Spectre, Victus, Alienware, TUF, ROG, Predator, Katana, Stealth, Galaxy Book, MateBook and more); PS4 Slim, PS3, PlayStation Portal, DualSense Edge, Xbox One, Xbox 360, Xbox Elite controller, Switch Pro Controller, Joy-Con 2, ROG Ally / Ally X / Xbox Ally X, Legion Go / Go S, MSI Claw. The price factors of the new models are estimates until the client's price list arrives. Galaxy S22+/S23+, MacBook Pro 14/16 (M2 Pro) and MacBook Air 15 (M2) were added after testing. Re-run `node app/seed/extract_prototype.js` (prints `models: 435`) and re-seed.
2. **Model ids no longer collide.** `+` becomes "plus" in the id (`galaxy-s26-plus`). Before, tapping "Galaxy S26" opened the S26+ and showed its price. Use the same rule for Django slugs and model page URLs.
3. **Repair pictures match the device.** Phone repair photos (`rep-*`) show only for phones. Tablets, laptops and consoles get tiles in their device colour (pink, green, orange) with the repair icon, and the side panel shows the device photo (`cat-tablet`, `cat-laptop`, `cat-console`), never a phone. Their own photos are planned: `tab-*`, `lap-*`, `con-*` (18 files, prompts 20 to 37 in the image drawer, mapping in `REP_CAT`). The build lists the files it finds in `img/` in `IMG_HAVE`; in Django, show a photo when its static file exists, otherwise the tile.
4. **Logo.** The cut-out from the sign photo is gone. `img/logo-tiptop.svg` (wordmark with the crowned phone) and `img/logo-mark.svg` (square icon, used below 560 px; favicon `logo-mark-180.png`) are a clean vector redraw of the shop sign. It is an interim until the original file arrives from the sign maker, so keep the logo swappable (one template include). Remove the old `logo-tiptop.jpg` / `logo-mark.jpg` references.
5. Describe box understands the new names and short forms: "iPad 9", "iPad Air 4", "iPad mini 6", "razr 50", "moto g54", "Nothing Phone 3", "ROG Ally", "Legion Go", "MSI Claw", "PS4 Slim", "Xbox 360", "ip13", "S21 plus", "Note 20 Ultra", "Z Fold 5", "DualSense Edge".
6. **Fixes from the logic test run (17 Nov):**
   - Describe box: everyday words no longer count as model names ("book a repair" was a Surface Book, "one" was an Xbox One, "my phone 2 times" was a Nothing Phone (2), "power switch on my laptop" was a Nintendo Switch). "Ladebuchse" on a console means the controller/handheld charging port (`cport`), "Tasten" on a laptop means the keyboard; before, these repairs were silently dropped. "PS5 controller" no longer matches the DualSense Edge. Tablet words "Tab", "Pad", "MatePad" detect tablets.
   - Repairs a model can't have are removed (`NOSV` / `noSv` in `js/engine.js`): PlayStation Portal no fan/SSD, Switch models no SSD, Joy-Con no charging port, Xbox controller no battery (AA cells), Apple silicon MacBooks no SSD upgrade, MacBook Air (M1 onward) no fan. Use `servicesFor()`; the seed already does.
   - `cport` is now called "Charging port" / "Ladebuchse Reparatur" (it covers handhelds too, not only controllers).
   - Console repair cards: handheld screen first, then sticks, battery, port; home consoles keep HDMI, fan, drive, power supply.
   - Admin "Add device": a model that already exists is refused (`ad_dup`), and the new model is selected by its real id.
7. **Seed script gap:** `app/seed/extract_prototype.js` reads `T` only up to the builder click handler, so every `Object.assign(T.en / T.de, {...})` block further down is missing from `prototype.json` (Google rating, buyback photos, multi-select, `ad_dup` strings: 22 keys). Append those blocks to the vm code (collect each line starting with `Object.assign(T.en, {` or `Object.assign(T.de, {` up to its closing `});`). With that, `T.en` and `T.de` both have 277 keys and match.
8. **Tested on 17 Nov:** 435 models, 7,032 prices (no empty or broken price, original display dearer than premium, totals add up), 109 describe-box phrases in German and English, 78 full price-calculator runs across every brand on desktop and phone (model → several repairs → price → WhatsApp text → callback → admin request), brand cabinet (26 drawers), admin prices and add device, buyback photos, EN/DE texts, no sideways scrolling from 320 to 1920 px, the standalone file. Re-run these checks on the Django site.

## Call with the owner, 25 November 2026

Recorded call (Fathom, 93 min) plus Ronak's list of 26 Nov. All of this is in the prototype (`patch_nov26.py`, `nov26.css`, `legal_*.js`, `js/engine.js`); the live site must match:

1. **New logo.** The owner's crowned, thumbs-up phone mascot is kept exactly as it is (cut out of his gold logo), with classic upright gold lettering (Cinzel Black, gold gradient), no stars, no swoosh, no text underneath, transparent background. Files: `img/logo-tiptop.svg` (header, footer on dark), `img/logo-mark.webp` (mascot only, header below 560 px), `img/logo-mark-180.png` (favicon, apple-touch-icon). The "Service 24" text next to the logo is gone. Large transparent PNG and SVG for print/Google: `brand/`.
2. **Top of the page, in this order:** search bar (live model suggestions while typing, repair words ignored for matching, arrow keys and Enter, a click opens the price calculator with the model and any repair already picked), then two buttons: call `030 814 757 91` with "Ruf uns an" under the number (was "Bitte sofort anrufen", changed 26 Nov evening, see below), and WhatsApp `030 814 757 91`, then the Google rating, then the headline. On phones this block comes before the photo. The header shows the number with "Ruf uns an" under it from 1180 px up.
3. **One number everywhere:** phone and WhatsApp are both 030 814 757 91 (`WA_NUMBER = "493081475791"`). The mobile number is gone from footer, legal pages and links.
4. **Email** tiptophandyreparatur@gmail.com in footer, Impressum, privacy policy, withdrawal texts.
5. **Impressum:** owner Mostafa Khodr (Einzelunternehmer), VAT ID DE357158413, the commercial-register block removed (sole trader), image credits filled in (own photos; device pictures made with AI). He asked for "K. Mostafa"; the Impressum needs the full first and last name, so it shows "Mostafa Khodr". Still open: the Handwerksrolle entry and professional title.
6. **Opening hours one day per line** with "Sonntag geschlossen" (shop card and footer), today in bold. Address shown as "10553 Berlin-Moabit" (Bezirk Mitte, Ortsteil Moabit).
7. **Google rating links** open the reviews directly: `https://search.google.com/local/reviews?placeid=ChIJA6sIHRNRqEcRdYbk2bTKeB4`.
8. **Repair photos per device type:** iPhone photos (`rep-*`) only for Apple phones; Samsung, Xiaomi and all other phones use the Android set `and-display`, `and-battery`, `and-port`, `and-back`, `and-camera`, `and-water`. Tablets, laptops and consoles use `tab-*`, `lap-*`, `con-*`. **All these files exist since 26 Nov evening** (see below); the tile fallback stays for models whose photo is missing. The image drawer has the prompts (43 images): newest devices (iPhone 18 Pro / Pro Max, Galaxy S26 Ultra, PlayStation 5 Pro with DualSense), new before/after with an iPhone 18 Pro Max, new "sell your device" picture with iPhone, iPad, MacBook and controller.
9. **Consoles:** joystick drift and TMR joysticks are offered for home consoles and handhelds too (big cards on the PS5 / Xbox page). Names: "Joystick-Drift Reparatur", "TMR-Joysticks (driftfrei)".
10. **Hero video:** done 26 Nov evening, see "Changes of 26 November 2026 (evening)". Desktop and laptop only; phones and tablets keep the photo (the owner agreed: 90% of visitors are on phones).
11. **AI video with the owner's face** (cartoon character, not a real person) showing the repair journey: **done 26 Nov** (`video/`, see below). Still later: an AI chatbot that answers questions from the site content.
12. **Live repair status ("Live-Tracking")**: to research. Proposal: admin sets the status of a request (received, diagnosed + price, in repair, ready for pickup) and the customer gets a WhatsApp message for each step (WhatsApp Business API template messages), plus a status page `/status/<code>` linked from those messages.
13. **Admin pricing:** he wants to see and set all prices without searching model by model. Add a price-list screen per category (all models × main repairs in one editable table) and CSV import/export, so his price list can be loaded in one go.

## Changes of 26 November 2026 (evening)

Made in the claude.ai chat after the client's feedback on the first video ("not overview-friendly, longer, show the repair process, logo on the t-shirt, name?, remove 'Bitte anrufen', it feels harsh"). All of it is in `prototype/` now; the live site must match.

1. **The film.** Google Flow cartoon film, 65 s, German speech: Mostafa (navy t-shirt with the TipTop logo) and a customer walk through six numbered steps: Gerät abgeben, Diagnose und Festpreis, Reparatur, Test, Nachricht: fertig, Abholen. His name appears once ("Ich bin Mostafa" + name tag). End card with the client's exact gold logo, 030 814 757 91, "Anruf oder WhatsApp" (no "Bitte anrufen"), address and hours.
   - `video/TipTop-Film-vertical.mp4`: 1080×1920, for Instagram, TikTok and WhatsApp status.
   - `video/TipTop-Film-hero-4x5.mp4` = `prototype/img/hero-loop.mp4`: 720×900, 6.2 MB, with sound, overlays placed clear of the hero badges.
2. **Hero film on desktop and laptop only** (`patch_hero_video.py`, function `heroVideo()`):
   - Plays only when `(min-width:901px) and (hover:hover) and (pointer:fine)` matches, reduced motion is off and Save-Data is off. Phones and tablets (touch, also iPad landscape) keep the still photo; CSS hides the video below that too.
   - `<video>` muted, loop, playsinline, `preload="none"`; the src is set 400 ms after `window` load so the hero photo stays the LCP. The photo stays underneath and the video fades in on `playing`.
   - Sound button bottom right, "Ton an" / "Ton aus" (EN "Sound on" / "Sound off", keys `snd_on`, `snd_off`), `aria-pressed`. The "Jetzt geöffnet" tag stays bottom left.
   - Pauses when the hero is out of view (IntersectionObserver) and when the window becomes narrow; a load error removes the video and keeps the photo.
   - The "Displays ab" sticker moves to `top:26%` while the video is on, so it doesn't cover the step card.
   - The separate 16:9 film section (`#film`, `patch_film.py`) is **dropped**: don't port it.
3. **Call text:** `call_now` is now **"Ruf uns an"** / "Give us a call" (header number, hero call button, shop card, footer). The owner asked for "Bitte sofort anrufen" in the call, then said "Bitte anrufen" feels aggressive; du-form as everywhere else on the site.
4. **All repair photos exist** (generated in ChatGPT, same blue-mat daylight style): `and-display`, `and-battery`, `and-port`, `and-back`, `and-camera`, `and-water` (Galaxy S26 Ultra style), `tab-*` (6), `lap-display`, `lap-battery`, `lap-keyboard`, `lap-port`, `lap-fan`, `lap-water`, `con-hdmi`, `con-fan`, `con-drift` (also used for TMR), `con-display` (handheld), `con-drive`, `con-psu`. Also new: `rep-display`, `rep-battery`, `rep-port`, `rep-back` (iPhone 18 Pro), `before` / `after` (iPhone 18 Pro Max), `sell`, `cat-console` (PS5 Pro with DualSense). `rep-camera` and `rep-water` are still the older pictures. Tested: Galaxy, iPad, MacBook and PS5 Pro each show only their own photos.
5. Preview published (Claude artifact, same link) and `prototype/TipTop-Service-24-final.html` rebuilt (17 MB, film embedded).

## Working with the claude.ai chat

Two Claude sessions work on this project for Ronak. Keep them from stepping on each other:

- **The claude.ai chat** owns `prototype/`, `video/` and `brand/`: design, copy, images, videos, client feedback and the published preview. It edits the prototype sources in its own workspace, rebuilds, and copies the results into this folder (`prototype/index.html`, `prototype/TipTop-Service-24-final.html`, `prototype/img/`, `prototype/src/`). After every change it adds a dated section to this file, like the one above.
- **Claude Code** (this folder, branch `django-site`) owns `app/` and everything Django, hosting and go-live. Don't edit `prototype/` here: the next copy from the chat would overwrite it. If the port needs a prototype change, write it under "Requests for the chat" below and tell Ronak.
- **After a dated section appears here**, re-run `node app/seed/extract_prototype.js`, the CSS/template port and the checks, so the Django site matches the prototype again.
- Keep "Status from Claude Code" short and current (what's built, what's next, blockers), so the chat can read it before changing the prototype.

### Status from Claude Code

Updated 27 Nov 2026. Branch `django-site`, pushed to GitHub `RonakJaiswal05/Tip-Top` (public; `main` is still the 15 Nov starting point). Django site not deployed.

- **Vercel:** the GitHub repo is connected to Vercel as a design preview only. `vercel.json` makes it serve `prototype/` (with `X-Robots-Tag: noindex`), so every prototype copy from the chat that gets committed shows up there. The Django site can't run on Vercel (database, background jobs, uploaded photos); it goes to the GoDaddy server.

- **Matches the prototype of 26 Nov (evening):** 435 models / 22 brands / 31 repairs with the NOSV exclusions, TMR, multi-select with bottom bar, search bar with suggestions, call + WhatsApp buttons (030 814 757 91, "Ruf uns an"), rating above the headline, new logo and favicon, globe language button on phones, device-specific repair photos (all 24 sets imported), one shop card with hours per line, ways cards, desktop-only hero film with sound button, brand cabinet with wordmark logos, owner/VAT/Gmail everywhere, legal texts of 26 Nov (statistics and marketing still removed).
- **Built beyond the prototype:** buyback photos for real (multipart upload, EXIF/GPS stripped, private storage, staff-only view, deleted after 30 days unless bought); admin price list per category (all models × main repairs, change-only save) next to the single-model editor, bulk changes, copy, CSV/Excel import/export; per-model "Nicht möglich" repairs; business facts in Settings.
- **Checks:** 61 tests pass; all 6,657 calculator labels match in DE and EN; no sideways scrolling or clipped text from 320 to 2560 px; axe 0 violations. Details in `docs/TESTING.md`.
- **Next:** server setup and go-live once Ronak gives access and says go; live repair status and the AI chatbot need decisions first.
- **Blocked on:** price list, Handwerksrolle/title, original logo, domain/DNS, GBP access, GoDaddy DPA details, Brevo, Google service account. Full list in `docs/BLOCKED.md`.
- **How the port works:** `node app/seed/extract_prototype.js` (data and texts), `app/tools/build_css.py` (prototype CSS + `app/static/site/css/port-additions.css`), templates and `app/static/site/js/site.js` by hand. So keep text keys and CSS class names stable when you can; new keys and images come over automatically.

### Requests for the chat

- Shop card at 320–380 px in German: the rating line ("321 Google-Bewertungen") and "Donnerstag 10:00–20:00 Uhr" make `.shop-b`'s grid column wider than the card, so text is clipped. Fixed on the site with `.shop .shop-b{grid-template-columns:minmax(0,1fr)}` plus smaller gaps below 381 px (see `port-additions.css`); please do the same in the prototype.
- Footer hours (`#fHours`) sit in a 128 px column on phones and overflow; the site lets each line wrap (`.fgrid .hours li{flex-wrap:wrap}`).
- `patch_nov26.py` sets `T.closed` to "geschlossen" for the hours list, but `openStatus()` uses the same key for "Geschlossen, öffnet {d} um 10 Uhr". The site keeps `closed` for the status and uses a new key `closed_day` for the list; please split the key in the prototype too.

## Development still open

Everything the live site still needs, in one list (details in the SOW and the sections above):

- Django back end with the catalogue from the database (435 models, 22 brands, 31 repairs), import command for the client's real price list (current prices are placeholders).
- Model pages per model in DE and EN with clean URLs, hreflang, sitemap, canonical tags and structured data.
- Admin A1 to A12: roles and 2FA, dashboard, prices (plus the price-list screen per category with all models × repairs editable at once, bulk percentage changes, copy from a similar model, CSV/Excel import and export, history with rollback, scheduled changes), devices, repair types, request inbox with pipeline and notifications, Ankauf at the counter (checklist, ID, IMEI blocklist check, contract PDF signed on a tablet, based on the client's Ankaufvertrag template), withdrawals and consent log, content, media library, settings, audit log.
- Server APIs replacing `localStorage`: requests, callbacks, buyback photos (private storage, EXIF stripped, deleted after 30 days), withdrawals with immediate confirmation email, consent records.
- Live repair status: admin sets the status, customer gets a WhatsApp message per step (WhatsApp Business API templates) and a `/status/<code>` page. Research cost and setup first, then build.
- AI chatbot answering customer questions in DE and EN from the site's own data (prices, models, hours, address, guarantee, Ankauf), handing over to WhatsApp or the 030 number, never inventing prices. Needs an AI provider (add it to the privacy policy).
- Integrations: Google Sheets sync, transactional email (EU provider, SPF/DKIM/DMARC), daily Google rating fetch (Places API), Matomo deferred, ads tracking only if ads run.
- info@tiptophandyreparatur.de forwarding to the Gmail address, then switch the site to info@.
- Legal placeholders filled from confirmed facts (Handwerksrolle and title, shipping partner, flat fee, storage period, GoDaddy contracting entity and data-centre country, data protection officer, ads sections, BFSG exemption, AI provider), then the lawyer's review.
- Production clean-up: remove the image-prompt drawer, decide the "Geschäftskunden" footer link.
- Hosting: GoDaddy VPS in Europe, staging and production, TLS, backups with a tested restore, monitoring, error tracking, deploys from a client-owned Git repo, rate limits and security headers.
- Move off Shopify: access, 301 redirects for every old URL, DNS switch, Search Console and sitemap, Google Business Profile link.
- Tests: 14 screen sizes, five browsers, price accuracy against the approved list, describe-box phrases, the 17 Nov logic checks, accessibility (keyboard, VoiceOver, NVDA), Lighthouse 90+ mobile, consent network log, staff acceptance test. Then training and a short guide for adding models and photos.

## Open questions for the client

1. Handwerksrolle entry and professional title (Meister) for the Impressum; whether the trading name stays "TipTop Service 24 Handy Reparatur Berlin" (in the call: "Tiptop Handy Reparatur Service" was also mentioned).
2. Access to the domain's email (to create info@ with forwarding to the Gmail address).
3. Price list for all models and repairs (including iPhone 17e, 18 Pro, 18 Pro Max, Duo, TMR sticks and the 246 models added on 17 Nov), and which models he wants that are still missing.
4. **The original TipTop logo file** (vector: AI, EPS, PDF or SVG) from whoever made the shop sign, and whether TipTop is an authorised partner of any brand.
5. Good photos of himself and 2-3 example AI videos he likes (for the AI video).
6. Where the domain is registered, and DNS access.
7. Google Business Profile access (for the API key project and the website link).
8. Analytics and ads: yes or no.
9. 100 real customer phrases to test the describe box.
10. Whether "Ruf uns an" under the call button is fine (he asked for "Bitte sofort anrufen" in the call, then called "Bitte anrufen" harsh in the video feedback).
11. Which AI provider to use for the chatbot, and whether he wants to pay for WhatsApp Business API messages for live status.

## Ask before you

Buy anything, change DNS, send email to real customers, delete data, push to production, or change legal texts beyond filling in confirmed facts.
