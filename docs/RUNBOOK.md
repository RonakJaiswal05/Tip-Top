# Runbook: TipTop Service 24 on a GoDaddy VPS

Production and staging run on one Ubuntu LTS server (1 vCPU, 2 GB RAM, 40 GB NVMe):
Nginx → Gunicorn (Django 5.2, Python 3.13 via uv) → PostgreSQL; Redis for cache and Celery (concurrency 1);
Let's Encrypt TLS; nightly backups copied off the server.

| | Production | Staging |
|---|---|---|
| URL | https://tiptophandyreparatur.de | https://staging.tiptophandyreparatur.de (password, noindex) |
| Code | /srv/tiptop/production/src (Git checkout), app → src/app | /srv/tiptop/staging/src |
| Settings | /etc/tiptop/production.env | /etc/tiptop/staging.env |
| Database | tiptop_production | tiptop_staging |
| Redis DB | 0 cache, 1 Celery | 2 cache (jobs run inline, no worker) |
| Services | tiptop-web@production, tiptop-worker@production, tiptop-beat@production | tiptop-web@staging |
| Logs | /var/log/tiptop/production.log, journalctl -u tiptop-web@production, /var/log/nginx/tiptop-production.*.log | same with staging |

Memory plan for 2 GB: PostgreSQL ~300 MB (shared_buffers 256 MB), Gunicorn production 3 workers × 2 threads
(~250 MB), staging 1 worker (~80 MB), Celery worker ~120 MB, beat ~60 MB, Redis 64 MB max, Nginx ~20 MB,
plus 2 GB swap. Matomo stays off until the server is upgraded.

## 0. Before the server exists (now)

1. Lower the TTL of the A/AAAA records of tiptophandyreparatur.de and www to 300 s at the current DNS host
   (ask the client where the domain is registered). Leave MX records alone.
2. Accounts the site needs (ideally in the client's name, since TLAMO GmbH signs the data processing agreements):
   - Brevo (EU) for email: API key; add the sender domain and set the SPF/DKIM/DMARC records Brevo shows
     (TXT records only, MX stays as it is).
   - Google Cloud project: Places API (New) key restricted to the Places API and the server IP; a service account
     for Sheets (download the JSON key; share the Sheet with the service account's email as Editor).
   - Sentry project in the EU region (de.sentry.io) for error tracking; an uptime monitor (e.g. Better Stack or
     UptimeRobot) on https://tiptophandyreparatur.de/healthz every minute, alerts to the shop.
   - Off-server backup space, e.g. a Hetzner Storage Box or an S3 bucket in the EU.
3. Put the code in a Git repository the client owns (GitHub/GitLab), push branch `main`.

## 1. Provision the server (once, about 10 minutes)

On GoDaddy: Ubuntu, latest LTS offered (24.04 or 26.04), Europe region. Note the country of the data centre for
the privacy policy (hosting section, see docs/BLOCKED.md). Then, from your machine:

```bash
ssh root@SERVER_IP
apt-get update && apt-get install -y git
git clone https://github.com/OWNER/tiptop.git /root/tiptop && cd /root/tiptop
sudo ADMIN_USER=ronak ADMIN_PUBKEY="$(cat ~/.ssh/id_ed25519.pub from your laptop)" \
     LE_EMAIL=info@tiptophandyreparatur.de REPO_URL=git@github.com:OWNER/tiptop.git SKIP_TLS=1 \
     bash deploy/setup.sh
```

- Keep this root session open and test `ssh ronak@SERVER_IP` in a second terminal before closing it: the script
  switches SSH to keys only and turns root login off.
- It prints a deploy key: add it to the repository as a read-only deploy key.
- It prints the staging password once (user `tiptop`).
- Fill in the secrets in /etc/tiptop/production.env and /etc/tiptop/staging.env (BREVO_API_KEY,
  GOOGLE_PLACES_API_KEY, SENTRY_DSN) and copy the service account JSON to /etc/tiptop/google-service-account.json
  (`chown root:tiptop`, `chmod 640`).
- Set BACKUP_TARGET in /etc/tiptop/backup.env and make sure root can reach it with its SSH key
  (`ssh-keygen -t ed25519` as root, add the public key at the storage box).

`setup.sh` can be run again at any time; it only changes what differs.

## 2. Deploy staging and test

```bash
sudo bash /root/tiptop/deploy/deploy.sh staging main
```

The first deploy seeds the catalogue (180 models, placeholder prices), shops, texts, photos, legal pages and the
2,086 Shopify redirects. Then create the staff accounts (Owner and Manager set up their authenticator app at
first sign-in):

```bash
sudo -u tiptop -H bash -c 'set -a; . /etc/tiptop/staging.env; set +a; cd /srv/tiptop/staging/app && .venv/bin/python manage.py create_staff NAME --role Owner --email NAME@example.com'
```

Point a DNS record `staging` (A/AAAA) at the server, run `setup.sh` again without `SKIP_TLS` to get the
certificates, and test on https://staging.tiptophandyreparatur.de (staff test on Monday 16 November):
calculator, callback, request form, withdrawal (check the confirmation email arrives), admin price change, sign-in
with 2FA, Google Sheet row.

## 3. Production

```bash
sudo bash /root/tiptop/deploy/deploy.sh production main
```

Create the production staff accounts the same way (with production.env). Import the client's price list:
Admin → Preise → Import (preview first), then Settings → switch off "Preise sind Platzhalter". Fill in the legal
placeholders and tick "Anwaltlich geprüft" on each version once the lawyer has approved it.

Go-live (only with the client's go):
1. Fetch the old sitemap one last time and compare with `app/seed/shopify_paths.txt`; load new paths with
   `manage.py seed_redirects --build new_paths.txt`.
2. Change the A/AAAA records of tiptophandyreparatur.de and www to the server. Do not touch MX/TXT for email.
3. Run `setup.sh` again (with LE_EMAIL, without SKIP_TLS) to issue the certificates and switch Nginx to HTTPS.
4. Check: https://tiptophandyreparatur.de, www → apex redirect, /policies/legal-notice → /de/impressum/,
   /sitemap.xml, /robots.txt (allows crawling in production), a test request reaches inbox, sheet and email.
5. Google Search Console: add the domain property, submit https://tiptophandyreparatur.de/sitemap.xml.
6. Update the website link in both Google Business Profiles if it changed.
7. Raise the DNS TTL again after a few days.

## Everyday operations

| Task | Command / place |
|---|---|
| Deploy a new version | `sudo bash /srv/tiptop/production/src/deploy/deploy.sh production main` (staging first) |
| Roll back | `sudo bash .../deploy.sh production <previous commit or tag>`; migrations that were added need a restore |
| Status | `systemctl status 'tiptop-*'`, `journalctl -u tiptop-web@production -n 100` |
| Django shell | `sudo -u tiptop -H bash -c 'set -a; . /etc/tiptop/production.env; set +a; cd /srv/tiptop/production/app && .venv/bin/python manage.py shell'` |
| Maintenance page | Admin → Einstellungen → Wartungsmodus (staff still see the site) |
| Google ratings now | Admin → Filialen → action "Google-Bewertung jetzt abrufen", or `manage.py fetch_ratings` |
| Price list | Admin → Preise → Import / Export, or `manage.py import_prices file.xlsx --dry-run` |
| Locked-out staff | Admin → Axes → Zugriffsversuche (delete the entry), or `manage.py axes_reset` |
| New phone for 2FA | Admin → Benutzer → action "Zwei-Faktor-Anmeldung zurücksetzen" |
| Certificates | renew automatically (certbot timer); `certbot renew --dry-run` to test |

## Backups

Nightly 03:15 (`/etc/cron.d/tiptop`): `pg_dump` of both databases, media archives and /etc/tiptop, kept 30 days in
/var/backups/tiptop and copied to BACKUP_TARGET. Log: /var/log/tiptop/backup.log. GoDaddy snapshots are a second layer.

Restore test (do this before launch and after any change to the backup):

```bash
sudo tiptop-backup
sudo tiptop-restore /var/backups/tiptop/tiptop_production_<stamp>.dump staging /var/backups/tiptop/media_production_<stamp>.tar.gz
```

Then open staging and check the newest requests and prices are there. Afterwards redeploy staging if needed.

## Security in place

SSH keys only, no root login; ufw allows 22/80/443 only; fail2ban for SSH and Nginx rate-limit offenders;
unattended security upgrades (no automatic reboot: reboot in a quiet hour when `/var/run/reboot-required`
exists); TLS 1.2/1.3 with HSTS; Content-Security-Policy without inline scripts; rate limits in Nginx and Django
for forms and sign-in; admin lockout after 5 failed attempts; Owner/Manager two-factor sign-in; purchase contract
PDFs are never served by Nginx (only through the admin); Gunicorn and Celery run as an unprivileged user with
systemd sandboxing.

## Upgrading the server later

GoDaddy lets you upgrade the plan from the VPS dashboard (short downtime, no downgrade). After an upgrade to 4 GB:
raise `GUNICORN_WORKERS`, `shared_buffers` (25 % of RAM) and Redis `maxmemory`, then Matomo can be added
(Settings → Statistik, which also brings back the cookie banner category; the privacy texts need the lawyer).
