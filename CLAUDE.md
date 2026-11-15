# TipTop Service 24: new website

Context for Claude Code. Read this whole file before changing anything. Last updated 15 November 2026.

## The job in one paragraph

Build and launch the production website for TipTop Service 24, a phone, tablet, laptop and console repair business in Berlin, by **Tuesday 17 November 2026**. The front end is already designed and working as a prototype (`prototype/index.html`). Your job is to turn it into a Django site with a real back end and admin, deploy it to a GoDaddy VPS in Europe and switch the domain over. The agreed scope is in `docs/` (English and German PDFs). Ronak builds and owns the project on the agency side; he is the person you are working with.

## The client

| | |
|---|---|
| Trading name | TipTop Service 24 |
| Legal entity | TLAMO GmbH |
| Main shop (Moabit, master workshop) | Beusselstraße 18, 10553 Berlin. Phone 030 814 757 91 (+49 30 81475791) |
| Second shop (Spandau) | Havelstraße 8, 13597 Berlin. Phone +49 30 89617138 (from its Google profile, ask the client to confirm) |
| Business WhatsApp | **+49 176 72746296** (confirmed by the client on 15 Nov 2026). Link format: `https://wa.me/4917672746296?text=...` |
| Email | info@tiptophandyreparatur.de (the old Impressum uses tiptop-service24@gmx.de; ask which one is official) |
| VAT ID | DE326279747 |
| Domain | tiptophandyreparatur.de (currently a Shopify store) |
| Instagram | instagram.com/tiptopservice24 |
| Facts used in copy | In Moabit since 2009, more than 15,000 customers, own board-level workshop (micro-soldering since 2013), up to 24 months guarantee, free pickup within 5 km, mail-in with free return |

**Opening hours conflict, ask the client.** The site currently says Mon to Sat 10:00 to 20:00 for both shops. The Google profiles say Moabit Mon to Sat 10:00 to 20:00, Spandau Mon to Thu 10:00 to 20:30 and Fri to Sat 10:00 to 21:00. The live site must support different hours per shop (it does not in the prototype).

**Google ratings** (Google Business Profile, checked 15 Nov 2026):
- Moabit: 4.9 from 321 reviews, place_id `ChIJA6sIHRNRqEcRdYbk2bTKeB4`, listed as "Meisterwerkstatt TipTop Service 24 Handy Reparatur Berlin"
- Spandau: 4.0 from 44 reviews, place_id `ChIJk4noUUFWqEcR8pf5IuXJ-7U`, listed as "Tip Top Reparatur Service"

The hero shows the Moabit rating (clearly labelled as Moabit); each shop card shows its own rating. Ronak may decide to show Spandau in the hero too.

## What already exists

- `prototype/index.html`: the complete front end as one page with hash routes. Open it in a browser. This is the design source of truth: markup, CSS, copy (DE and EN), interactions and motion. Port it, don't redesign it.
- `prototype/TipTop-Service-24-final.html`: the same thing as one self-contained file (images and fonts embedded), for sharing.
- `prototype/img/`: 18 photos, each in a full size and a `-s` phone size (760 px wide). They were generated in ChatGPT in a daylight documentary style; replace with real shop photos where the client provides them. Prompts and file names are in `prototype/src/imgs4.js`.
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

`Shop` (name, address, phone, WhatsApp, geo, Google place_id, cached rating and count, fetched_at), `OpeningHours` per shop and weekday, `SpecialHours` and Berlin holidays, `Category` (phone, tablet, laptop, console), `Brand` (name, slug, **logo upload**, order), `DeviceModel` (category, brand, name, release year, price level, flags: Face ID, headphone jack, console type, active, photo), `RepairType` (key, DE/EN names with per-category overrides, duration, warranty months, photo, order), `Price` (model, repair, tier: standard, premium or original, amount, is_from) with full history and rollback (django-simple-history), `Request` (kind: callback, form, withdrawal, sale; all fields from the forms; language; source; status pipeline New, Contacted, Booked, In repair, Ready for pickup, Collected, Lost with reason; shop; assignee; notes), `PurchaseContract` (Ankauf: seller ID details, IMEI, checklist, signed PDF), `Withdrawal`, `ConsentRecord` (proof id, version, choices, timestamp, no IP address), `FAQ`, `ContentBlock` (DE/EN texts), `LegalPage` with versions, `MediaAsset`, `SiteSettings` (WhatsApp number, emails, Google Sheet id, feature toggles), audit log.

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

All legal texts are drafted in German and English in `prototype/src/legal_de.js` and `legal_en.js`. Move them into `LegalPage` records. Yellow `<mark class="fill">` spots are placeholders the client must fill (managing director, register number HRB at Amtsgericht Charlottenburg, Handwerksrolle entry, person responsible under § 18 MStV). **Everything must be reviewed by the client's lawyer before launch.** German is legally binding; the English pages say so.

- Impressum under § 5 DDG. The EU online dispute platform link is removed on purpose (the platform closed on 20 July 2025); keep the consumer arbitration sentence.
- Privacy policy (GDPR). **The hosting section still names Hetzner; change it to GoDaddy** (exact contracting entity and address from GoDaddy's data processing agreement) once the server is bought.
- Cookie consent under § 25 TDDDG and the DSK guidance: "Alle ablehnen" and "Alle akzeptieren" equal in size and colour on the first layer, settings by category, proof id stored, ask again after 12 months, no optional script before consent, delete optional cookies on withdrawal. Keep the prototype's behaviour (`legal4.js`) and POST each decision to `/api/consent` for the consent log.
- **Withdrawal button (§ 356a BGB, in force since 19 June 2026)**: "Vertrag widerrufen" in the footer of every page, two steps (form, then "Widerruf bestätigen"), immediate confirmation email with content and timestamp, entry in the admin.
- Terms (AGB) for repairs and device purchases, withdrawal policy with the model form, cookie policy, accessibility statement (BFSG; MLBF Magdeburg as authority; client may be exempt as a micro-enterprise).
- Voice input shows a one-time notice before using the browser's speech recognition.
- Short privacy notes under every form (already in the prototype).
- No request to any third party before consent: fonts and images self-hosted.

### Brand logos

The brand cabinet should show the real logos (Apple, Samsung, Google, Xiaomi, Huawei, OnePlus, Oppo, Sony, Motorola, Lenovo, HP, Dell, ASUS, Acer, Microsoft, MSI, PlayStation, Xbox, Nintendo, Steam). **Do not draw or generate logos.** Use the official files the client or Ronak provides (brand press or media pages). The prototype already has the slot: files go in `prototype/img/brands/<slug>.svg` (list in `img/brands/README.txt`) and the slug is added to `BRAND_LOGOS_READY` in `brands4.js`. In Django, use the `Brand.logo` upload; without a logo the drawer shows the name. Under the cabinet there is a note that the brands belong to their owners and TipTop is not an authorised service partner. **Ask the client whether they are an authorised partner of any brand**; if they are, change that note.

## Hosting

- **GoDaddy VPS, self-managed, Linux, Europe region, no control panel.** Recommended plan to start: 1 vCPU, 2 GB RAM, 40 GB NVMe (₹649 a month on a 3-year term on GoDaddy India, plus GST). GoDaddy allows upgrading later from the VPS dashboard (permanent, no downgrades, short downtime), so start small. Ronak is buying it; ask him for the IP address and SSH access. Ideally the account is in the client's name, since TLAMO GmbH signs the data processing agreement.
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

`build4.py` does exact-string replacements on `src3.html` and fails loudly if a target string is missing. Patches run in order: `patch_dev.py` (mobile menu, image hydration), `patch_legal.py` (legal pages, consent, withdrawal, fonts), `patch_gmb.py` (Google ratings, logo slots, WhatsApp number, per-shop phone).

## Open questions for the client

1. Official email address (info@ or gmx).
2. Spandau phone number and opening hours for both shops.
3. Managing director, HRB number, Handwerksrolle entry, person responsible for content.
4. Price list for all models and repairs.
5. Brand logo files, and whether TipTop is an authorised partner of any brand.
6. Real photos of the shops and team.
7. Where the domain is registered, and DNS access.
8. Google Business Profile access (for the API key project and the website link).
9. Analytics and ads: yes or no.
10. 100 real customer phrases to test the describe box.

## Ask before you

Buy anything, change DNS, send email to real customers, delete data, push to production, or change legal texts beyond filling in confirmed facts.
