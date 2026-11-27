# Blocked and open items

Running list kept during the build. "Client" items are the open questions from CLAUDE.md; "Ronak" items are
decisions or access only Ronak can give. Last updated: 27 Nov 2026 (late evening), after porting the call with the
owner of 27 Nov and the story film.

## Needs the client

| # | What | Why it blocks | Current state on the site |
|---|------|---------------|---------------------------|
| 1 | Handwerksrolle entry and professional title (Meister) | Impressum cannot go live with placeholders | Yellow placeholders in the Impressum; owner, sole trader and VAT ID DE357158413 are filled in (Settings → Inhaber, USt-IdNr.) |
| 2 | Trading name: "TipTop Service 24 Handy Reparatur Berlin" or "Tiptop Handy Reparatur Service" | Footer ©, emails, contract PDF, structured data | "TipTop Service 24 Handy Reparatur Berlin" (Settings → Name des Geschäfts, one field) |
| 3 | Access to the domain's email (info@ forwarding to Gmail) | Contact address | tiptophandyreparatur@gmail.com everywhere (Settings → Kontakt-E-Mail). Emails are still *sent from* an address on the domain, which needs SPF/DKIM (Ronak 3); replies go to Gmail |
| 4 | Price list for all models and repairs (incl. iPhone 17e, 18 Pro/Pro Max, Duo, TMR sticks and the models added on 17 Nov) | Every price is a placeholder except iPhone 13 and 15 | Footer says prices are placeholders. Load with Admin → Preise → Import (CSV/Excel) or type them into Admin → Preise → Preisliste (all models of a device type in one table), then switch off "Preise sind Platzhalter" |
| 5 | Original logo file from the sign maker; authorised partner of any brand? | Logo is the interim redraw/cut-out (`app/templates/site/_logo.html`, one include); trademark note says "not an authorised service partner" | Interim logo files from the chat |
| 6 | Where the domain is registered, DNS access | Go-live, SPF/DKIM/DMARC | – |
| 7 | Google Business Profile access / Places API key | Daily rating update | 15 Nov 2026 snapshot (4.9 / 321); the badge opens the reviews |
| 8 | Analytics and ads: yes or no | Cookie banner categories | Statistics and marketing off, their categories and legal sections hidden |
| 9 | 100 real customer phrases | Acceptance test for the search/describe box (SOW F2) | – |
| 10 | Is "Ruf uns an" under the call buttons fine? | Copy in header, hero, shop card, footer | "Ruf uns an" (text `call_now`, editable in Admin → Texte) |
| 11 | AI provider for the chatbot (and its privacy text) | Chatbot can't be built without it | Not built. Live status via the WhatsApp Business API is dropped (owner, 27 Nov); the inbox has one-tap WhatsApp status buttons instead |
| 13 | The client's own Ankaufvertrag template | The SOW says the counter contract follows it | The admin's purchase contract PDF uses our own draft until the template arrives |
| 14 | Lawyer's review of the new privacy section "Karte von Google Maps (erst nach Klick)" | Part of the legal review before launch | Live on the site as drafted by the chat |
| 12 | Legal placeholders: shipping partner, mail-in flat fee, storage period and fee, data protection officer, BFSG exemption | Privacy policy, AGB, accessibility statement | Yellow placeholders; every legal page shows the "have it checked by a lawyer" note |

## Needs Ronak

| # | What | Current state |
|---|------|---------------|
| 1 | "Geschäftskunden" footer link: build a page or redirect? | Link hidden; old URL `/pages/geschaftskunde-werden` redirects to the home page |
| 2 | GoDaddy VPS: IP, SSH access, contracting entity and data-centre country from the DPA | Privacy policy names GoDaddy with placeholders for entity and country |
| 3 | Brevo account (API key) and sender domain | Emails go to the console in dev; withdrawal confirmation needs a working sender before launch |
| 4 | Google service account JSON and the Sheet ID(s) | Sheets sync off in Settings until set |
| 5 | Sentry (EU region) DSN, uptime monitor | – |
| 6 | Cookie banner with no optional category: keep it or drop it? | Kept: "Alle ablehnen" / "Alle akzeptieren" with the necessary-only text; decisions are logged |
| 7 | Google Maps Platform attribution: "Google" or "Google Maps" next to the rating | "Google" (one word in `templates/site/_gmb_badge.html`) |

## Decisions taken during the build (tell me if any is wrong)

- English pages use English slugs: `/en/legal-notice/`, `/en/privacy/`, `/en/terms/`, `/en/withdrawal/`,
  `/en/withdraw-contract/`, `/en/cookies/`, `/en/accessibility/`, `/en/request/`, `/en/repair/<model>/`.
- `tt-lang` is a cookie so "/" can send returning visitors to their language; the cookie table says so.
- Model URLs use `-plus` for "+" (`/de/reparatur/samsung-galaxy-s26-plus/`), the same rule as the prototype since 17 Nov.
- One shop since 17 Nov: the Spandau shop is switched off in the database, not deleted (older requests point to it).
  Request form: "Im Laden vorbeibringen" or "Einschicken"; old values (Spandau, pickup) stay readable on old requests.
- Business facts (trading name, owner, VAT ID, email, WhatsApp number, hero film) live in Settings, so the footer,
  emails, contract PDF and structured data change in one place.
- Repairs a device can't have (no fan, soldered SSD, AA batteries, no charging port) are a per-model field
  ("Nicht möglich") seeded from the prototype; the calculator, model pages, starting prices and the price list follow it.
- Repair photos per device type come from the media library by key (`rep-*` iPhone, `and-*` other phones, `tab-*`,
  `lap-*`, `con-*`); replacing a photo in Admin → Mediathek under the same key changes it everywhere.
- Buyback photos: re-encoded on the server (no EXIF/GPS), stored in `PRIVATE_ROOT` (not under `/media/`, never served
  by Nginx), shown only to staff in the request, deleted after 30 days unless a purchase contract is linked. They are
  **not** in the nightly backup, so a backup never keeps them longer than the 30 days the privacy policy promises.
- Two prototype layout issues fixed in `app/static/site/css/port-additions.css` (also listed for the chat in
  CLAUDE.md): at 320–380 px the German shop card clipped the rating and hours lines, and the footer hours overflowed
  their column.
- The prototype overwrote the text key `closed` with "geschlossen" (hours list), which breaks the live status
  ("Geschlossen, öffnet morgen um 10 Uhr"). The site keeps `closed` for the status and uses `closed_day` for the list.
- Legal texts: taken from the prototype of 26 Nov (Stand 26. November 2026), with statistics/Matomo and marketing
  removed as before. The seed adds a new version only on top of a version it wrote itself; anything edited or
  approved in the admin stays.
- Shopify redirects: products for models now in the catalogue (e.g. Huawei P30 lite) go to the model page.

## Not done yet

- Run `deploy/setup.sh` and `deploy/deploy.sh` on the server, DNS, certificates, Search Console (waiting for
  access and your go). Restore test of the backups.
- AI chatbot: waits for the provider decision (client 11).
- The two training sessions (SOW deliverable). A short German admin guide is in `docs/Admin-Kurzanleitung.md`.
- Buyback guide prices (F9) work, but no ranges are entered yet (Admin → Ankaufpreise).
- The remaining SOW screen sizes, five browsers, real phones with VoiceOver/NVDA, voice input on HTTPS, Lighthouse
  on the live server, the 100 customer phrases (docs/TESTING.md).
