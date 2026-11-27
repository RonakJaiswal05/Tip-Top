# TipTop Service 24: website, price calculator and admin

Django 5.2 site for TipTop Service 24 Handy Reparatur Berlin (owner Mostafa Khodr), one shop in Berlin-Moabit. The
approved design lives in `prototype/` (owned by the claude.ai chat, see CLAUDE.md); the live site in `app/` is a port
of it.

| Where | What |
|---|---|
| `app/` | Django project (uv, Python 3.13). Apps: `catalog` (models, repairs, prices), `shops` (hours, ratings), `leads` (requests, withdrawals, purchase contracts), `content` (texts, FAQ, media), `legal` (legal pages, consent log), `core` (settings, admin site, pages) |
| `app/static/site/` | The prototype's CSS, fonts and JavaScript (`site.js`) |
| `app/seed/` | Data extracted from the prototype (`extract_prototype.js` → `prototype.json`) and the Shopify redirect list |
| `deploy/` | Server setup, deploy, backup and restore scripts, Nginx and systemd configuration |
| `docs/RUNBOOK.md` | How to set up the server, deploy, go live and operate |
| `docs/BLOCKED.md` | What is waiting on the client or on Ronak |
| `docs/TESTING.md` | Test results |
| `vercel.json` | Vercel serves `prototype/` as a design preview (no indexing). The Django site itself runs on the server in `deploy/`, not on Vercel |

## Local development

```bash
cd app
uv sync
uv run python manage.py migrate
uv run python manage.py seed_site          # catalogue, shops, texts, photos, legal pages, roles
uv run python manage.py seed_redirects
uv run python manage.py create_staff me --role Owner
uv run python manage.py runserver
```

Without `DATABASE_URL` and `REDIS_URL` the dev settings use SQLite, an in-memory cache and run background jobs
inline; emails go to the console. Two-factor sign-in is off locally unless `OTP_ENFORCE=1`.

Tests: `uv run python manage.py test tests --settings=tiptop.settings.test`

After the chat updates `prototype/` (a new dated section in CLAUDE.md):

```bash
node app/seed/extract_prototype.js                  # texts, catalogue, legal texts -> app/seed/prototype.json
cd app && python tools/build_css.py                 # prototype CSS + port-additions.css -> static/site/css/site.css
uv run python manage.py migrate
uv run python manage.py seed_site --overwrite-texts --refresh-media   # dev only: resets texts, replaces changed photos/film
uv run python tests/browser/expected_labels.py      # then tests/browser/price_check.js in the browser
```

Useful commands: `import_prices FILE [--dry-run]`, `export_prices FILE.xlsx`, `fetch_ratings`, `setup_roles`,
`seed_legal`, `seed_catalog`.
