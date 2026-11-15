# Blocked and open items

Running list kept during the build. "Client" items are the open questions from CLAUDE.md; "Ronak" items are
decisions or access only Ronak can give. Last updated: 15 Nov 2026.

## Needs the client

| # | What | Why it blocks | Current state on the site |
|---|------|---------------|---------------------------|
| 1 | Official email: info@tiptophandyreparatur.de or tiptop-service24@gmx.de | Footer, legal pages, sender and reply-to of all emails | info@ used everywhere (Settings → Kontakt-E-Mail) |
| 2 | Spandau phone number and opening hours for both shops | Shop cards, footer, structured data, live open status | Spandau phone from its Google profile (030 896 171 38). Both shops Mon–Sat 10–20 as on the current website; Google shows Spandau Mon–Thu 10–20:30, Fri–Sat 10–21. Change in Admin → Filialen once confirmed; all texts follow automatically |
| 3 | Managing director, HRB number, Handwerksrolle entry, person responsible under § 18 MStV | Impressum and privacy policy cannot go live with placeholders | Yellow `<mark class="fill">` placeholders, template note shown on every legal page |
| 4 | Price list for all models and repairs | Every price on the site is a placeholder except iPhone 13 and 15 (taken from the current website) | Footer says prices are placeholders. Import with `manage.py import_prices <file>` or Admin → Preise → Import, then switch off "Preise sind Platzhalter" in Settings |
| 5 | Brand logo files, and whether TipTop is an authorised partner of any brand | Brand cabinet shows names only; trademark note says "not an authorised service partner" | Upload in Admin → Marken (logo) and Admin → Markenschrank (PlayStation, Xbox, Steam Deck) |
| 6 | Real photos of the shops and team | Shop cards show the street sign without a photo; all other photos are AI-generated placeholders | Replace in Admin → Mediathek (same key, e.g. `hero`, `shop-moabit`) |
| 7 | Where the domain is registered, DNS access | Go-live, SPF/DKIM/DMARC for email | – |
| 8 | Google Business Profile access / Places API key | Daily rating update | Ratings show the 15 Nov 2026 snapshot (4.9 / 321 Moabit, 4.0 / 44 Spandau) until a key is set |
| 9 | Analytics and ads: yes or no | Cookie banner categories | Statistics and marketing switched off (Settings), their categories and texts hidden |
| 10 | 100 real customer phrases | Acceptance test for the describe box (SOW F2) | – |
| 11 | Server country in GoDaddy's Europe region | Several privacy-policy sentences say "Server in Deutschland" | Unchanged until the server is bought (see Ronak 2) |

## Needs Ronak

| # | What | Current state |
|---|------|---------------|
| 1 | "Geschäftskunden" footer link: build a page or redirect? | Link hidden (Settings → Link „Geschäftskunden“ empty); old URL `/pages/geschaftskunde-werden` redirects to the home page |
| 2 | GoDaddy VPS: IP, SSH access, contracting entity and address from the DPA | Privacy policy still names Hetzner (hosting section) |
| 3 | Brevo account (API key) and sender domain | Emails go to the console in dev; withdrawal confirmation needs a working sender before launch |
| 4 | Google service account JSON and the Sheet ID(s) | Sheets sync switched off in Settings until set |
| 5 | Sentry (EU region) DSN for error tracking, uptime monitor | – |
| 7 | Google Maps Platform attribution: the Places API terms ask for the "Google Maps" logo or the text "Google Maps" next to Places data. CLAUDE.md says "Google"; the badge currently says "Google" | One word in `templates/site/_gmb_badge.html` if you want "Google Maps" |
| 6 | Cookie banner with no optional category: keep it (as instructed) or drop it? Legally a banner is only needed for optional storage | Kept: "Alle ablehnen" / "Alle akzeptieren" with the necessary-only text; decisions are logged |

## Decisions taken during the build (tell me if any is wrong)

- English pages use English slugs: `/en/legal-notice/`, `/en/privacy/`, `/en/terms/`, `/en/withdrawal/`,
  `/en/withdraw-contract/`, `/en/cookies/`, `/en/accessibility/`, `/en/request/`, `/en/repair/<model>/`.
- The language cookie `tt-lang` is now a cookie (was local storage) so "/" can send returning visitors to their
  language. The cookie table on the cookie policy says so; the prototype-only rows (tt-reqs, tt-ovr, tt-added) are gone.
- Prototype bug fixed: Galaxy S24/S25/S26 and S24+/S25+/S26+ shared one id, so picking "Galaxy S26" priced the S26+.
  Model URLs now use `-plus` (e.g. `/de/reparatur/samsung-galaxy-s26-plus/`).
- Workshop cards open the calculator on the matching repair (SOW F8): micro-soldering and IC repair → mainboard,
  water damage → water damage check, data recovery → data recovery.
- The hero's open status shows the main shop (Moabit); each shop card shows its own status.
- Legal texts changed only where the instructions required it: statistics/Matomo and marketing removed from the
  privacy and cookie policies ("Wir setzen keine Statistik- oder Marketing-Dienste ein."), cookie table updated to
  the live site, internal links made real. These pages carry "Stand: 15. November 2026"; the others keep 14 November.
  All still need the lawyer.
- Price list: rows from the prototype are marked "Platzhalter"; the dashboard counts them until the import.
- Old Shopify URLs (2,086 from the sitemap of 15 Nov 2026): 72 go to the exact model page, products for models
  no longer listed (HTC, LG, Nokia, older Samsung/Huawei/Sony) go to their brand's section of /de/reparatur/.
- Staging runs background jobs inline (no Celery worker) to save memory on the 2 GB server.

## Not done yet (from the SOW, after this build)

- Run `deploy/setup.sh` and `deploy/deploy.sh` on the server, DNS, certificates, Search Console (waiting for
  access and your go). Restore test of the backups.
- German admin handbook and the two training sessions (SOW deliverables).
- Buyback guide prices (F9) work, but no ranges are entered yet (Admin → Ankaufpreise).
- The remaining 8 of the 14 SOW screen sizes, real phones with VoiceOver/NVDA, voice input on HTTPS, Lighthouse
  on the live server, the 100 customer phrases (docs/TESTING.md).
- Matomo and ad tracking: switched off, can be turned on in Settings once decided (the legal texts need the lawyer).
