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
