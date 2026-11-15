#!/usr/bin/env bash
# TipTop Service 24: provision a fresh Ubuntu LTS VPS (2 GB RAM) for production and staging.
#
# Idempotent: run it again after changing anything below; it only adds or updates what is missing or different.
# Run as root (or with sudo) on the server, from a checkout of this repository:
#
#   sudo ADMIN_USER=ronak ADMIN_PUBKEY="ssh-ed25519 AAAA... ronak" \
#        LE_EMAIL=info@tiptophandyreparatur.de \
#        REPO_URL=git@github.com:OWNER/tiptop.git \
#        bash deploy/setup.sh
#
# Optional: DOMAIN (default tiptophandyreparatur.de), STAGING_DOMAIN (default staging.<DOMAIN>),
#           STAGING_PASSWORD (basic auth for staging; generated if empty), SKIP_TLS=1 (before DNS points here),
#           BACKUP_TARGET (rsync target user@host:path for off-server copies), SWAP_GB (default 2).
#
# What it does: packages, 2 GB swap, admin user with SSH key, SSH hardening (keys only, no root login),
# ufw (22, 80, 443), fail2ban, unattended security upgrades, PostgreSQL (tuned small, one database per
# environment), Redis (64 MB, volatile-lru), app user and directories, env files with generated secrets,
# Nginx (both sites, rate limits, caching, staging password), systemd units for Gunicorn/Celery/beat,
# Let's Encrypt certificates, nightly backups. It does NOT change DNS.
set -euo pipefail

DOMAIN="${DOMAIN:-tiptophandyreparatur.de}"
STAGING_DOMAIN="${STAGING_DOMAIN:-staging.${DOMAIN}}"
ADMIN_USER="${ADMIN_USER:-}"
ADMIN_PUBKEY="${ADMIN_PUBKEY:-}"
LE_EMAIL="${LE_EMAIL:-}"
REPO_URL="${REPO_URL:-}"
SWAP_GB="${SWAP_GB:-2}"
APP_USER=tiptop
BASE=/srv/tiptop
ETC=/etc/tiptop
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

log() { printf '\n\033[1;34m==> %s\033[0m\n' "$*"; }
need_root() { [ "$(id -u)" = 0 ] || { echo "Run as root (sudo)." >&2; exit 1; }; }
need_root
. /etc/os-release
[ "${ID}" = "ubuntu" ] || { echo "This script is written for Ubuntu LTS." >&2; exit 1; }
log "Ubuntu ${VERSION_ID} (${VERSION_CODENAME})"

# ---------------------------------------------------------------- packages
log "Packages"
export DEBIAN_FRONTEND=noninteractive
apt-get update -q
apt-get install -y -q --no-install-recommends \
  nginx postgresql postgresql-contrib redis-server certbot python3-certbot-nginx \
  ufw fail2ban python3-systemd unattended-upgrades apt-listchanges git curl ca-certificates rsync pipx \
  build-essential libpq-dev gettext apache2-utils logrotate jq

# ---------------------------------------------------------------- swap
if ! swapon --show | grep -q '/swapfile'; then
  log "Swap ${SWAP_GB} GB"
  fallocate -l "${SWAP_GB}G" /swapfile
  chmod 600 /swapfile
  mkswap /swapfile
  swapon /swapfile
  grep -q '^/swapfile ' /etc/fstab || echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi
install -m 644 /dev/stdin /etc/sysctl.d/90-tiptop.conf <<'EOF'
vm.swappiness=10
vm.vfs_cache_pressure=50
vm.overcommit_memory=1
EOF
sysctl -q --system

# ---------------------------------------------------------------- admin user and SSH
if [ -n "${ADMIN_USER}" ]; then
  log "Admin user ${ADMIN_USER}"
  id "${ADMIN_USER}" >/dev/null 2>&1 || adduser --disabled-password --gecos "" "${ADMIN_USER}"
  usermod -aG sudo "${ADMIN_USER}"
  install -d -m 700 -o "${ADMIN_USER}" -g "${ADMIN_USER}" "/home/${ADMIN_USER}/.ssh"
  if [ -n "${ADMIN_PUBKEY}" ]; then
    touch "/home/${ADMIN_USER}/.ssh/authorized_keys"
    grep -qxF "${ADMIN_PUBKEY}" "/home/${ADMIN_USER}/.ssh/authorized_keys" || echo "${ADMIN_PUBKEY}" >> "/home/${ADMIN_USER}/.ssh/authorized_keys"
    chown "${ADMIN_USER}:${ADMIN_USER}" "/home/${ADMIN_USER}/.ssh/authorized_keys"
    chmod 600 "/home/${ADMIN_USER}/.ssh/authorized_keys"
  fi
  echo "${ADMIN_USER} ALL=(ALL) NOPASSWD:ALL" > "/etc/sudoers.d/90-${ADMIN_USER}"
  chmod 440 "/etc/sudoers.d/90-${ADMIN_USER}"
fi
# Keys only and no root login, but never lock the door before a key is in place.
if [ -n "${ADMIN_USER}" ] && [ -s "/home/${ADMIN_USER}/.ssh/authorized_keys" ]; then
  log "SSH: keys only, no root login"
  install -m 644 /dev/stdin /etc/ssh/sshd_config.d/90-tiptop.conf <<'EOF'
PermitRootLogin no
PasswordAuthentication no
KbdInteractiveAuthentication no
PubkeyAuthentication yes
MaxAuthTries 4
X11Forwarding no
EOF
  sshd -t && systemctl reload ssh || systemctl reload sshd || true
else
  echo "!! SSH hardening skipped: give ADMIN_USER and ADMIN_PUBKEY so you can't be locked out." >&2
fi

# ---------------------------------------------------------------- firewall, fail2ban, updates
log "Firewall (22, 80, 443)"
ufw default deny incoming >/dev/null
ufw default allow outgoing >/dev/null
ufw allow OpenSSH >/dev/null
ufw allow 'Nginx Full' >/dev/null
ufw --force enable >/dev/null

log "fail2ban"
install -m 644 "${HERE}/fail2ban/tiptop.local" /etc/fail2ban/jail.d/tiptop.local
systemctl enable --now fail2ban >/dev/null
systemctl restart fail2ban

log "Unattended security upgrades"
install -m 644 /dev/stdin /etc/apt/apt.conf.d/20auto-upgrades <<'EOF'
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
APT::Periodic::AutocleanInterval "7";
EOF
install -m 644 /dev/stdin /etc/apt/apt.conf.d/52tiptop-unattended <<'EOF'
Unattended-Upgrade::Automatic-Reboot "false";
Unattended-Upgrade::Remove-Unused-Dependencies "true";
EOF

# ---------------------------------------------------------------- PostgreSQL
log "PostgreSQL"
PGVER="$(ls /etc/postgresql | sort -V | tail -1)"
install -m 644 /dev/stdin "/etc/postgresql/${PGVER}/main/conf.d/90-tiptop.conf" <<'EOF'
# small server: 2 GB RAM shared with Nginx, Gunicorn, Celery and Redis
shared_buffers = 256MB
effective_cache_size = 768MB
work_mem = 4MB
maintenance_work_mem = 64MB
max_connections = 40
wal_buffers = 8MB
random_page_cost = 1.1
listen_addresses = 'localhost'
EOF
systemctl restart postgresql

# ---------------------------------------------------------------- Redis
log "Redis (64 MB)"
REDIS_CONF=/etc/redis/redis.conf
set_redis() { if grep -qE "^#?\s*$1 " "$REDIS_CONF"; then sed -i -E "s|^#?\s*$1 .*|$1 $2|" "$REDIS_CONF"; else echo "$1 $2" >> "$REDIS_CONF"; fi; }
set_redis bind "127.0.0.1 -::1"
set_redis maxmemory 64mb
# only keys with a timeout (cache entries) may be evicted, never Celery's queued tasks
set_redis maxmemory-policy volatile-lru
set_redis supervised systemd
systemctl enable --now redis-server >/dev/null
systemctl restart redis-server

# ---------------------------------------------------------------- app user, directories, uv
log "App user and directories"
id "${APP_USER}" >/dev/null 2>&1 || adduser --system --group --home "${BASE}" --shell /bin/bash "${APP_USER}"
usermod -aG "${APP_USER}" www-data   # Nginx reaches the Gunicorn sockets (mode 770)
install -d -m 755 -o "${APP_USER}" -g "${APP_USER}" "${BASE}" /var/log/tiptop /var/lib/tiptop
install -d -m 750 -o root -g "${APP_USER}" "${ETC}"
sudo -u "${APP_USER}" -H pipx install uv >/dev/null 2>&1 || sudo -u "${APP_USER}" -H pipx upgrade uv >/dev/null 2>&1 || true
UV="${BASE}/.local/bin/uv"
[ -x "${UV}" ] || { echo "uv not installed for ${APP_USER}" >&2; exit 1; }

if [ -n "${REPO_URL}" ] && [ ! -f "${BASE}/.ssh/id_ed25519" ]; then
  install -d -m 700 -o "${APP_USER}" -g "${APP_USER}" "${BASE}/.ssh"
  sudo -u "${APP_USER}" -H ssh-keygen -q -t ed25519 -N "" -C "tiptop-deploy@$(hostname)" -f "${BASE}/.ssh/id_ed25519"
  echo "!! Add this deploy key (read-only) to the Git repository, then run deploy/deploy.sh:"
  cat "${BASE}/.ssh/id_ed25519.pub"
fi

gen() { python3 -c "import secrets; print(secrets.token_urlsafe($1))"; }

for ENVNAME in production staging; do
  log "Environment ${ENVNAME}"
  install -d -m 755 -o "${APP_USER}" -g "${APP_USER}" "${BASE}/${ENVNAME}" "${BASE}/${ENVNAME}/media" "${BASE}/${ENVNAME}/static" \
    "/var/lib/tiptop/${ENVNAME}"
  DB="tiptop_${ENVNAME}"
  ENVFILE="${ETC}/${ENVNAME}.env"
  if [ ! -f "${ENVFILE}" ]; then
    DBPASS="$(gen 24)"
    if [ "${ENVNAME}" = production ]; then HOSTS="${DOMAIN},www.${DOMAIN}"; URL="https://${DOMAIN}"; RDB=0; WORKERS=3; EAGER=0;
    else HOSTS="${STAGING_DOMAIN}"; URL="https://${STAGING_DOMAIN}"; RDB=2; WORKERS=1; EAGER=1; fi
    sed -e "s|@ENVIRONMENT@|${ENVNAME}|g" -e "s|@SECRET@|$(gen 50)|g" -e "s|@DB@|${DB}|g" -e "s|@DBPASS@|${DBPASS}|g" \
        -e "s|@HOSTS@|${HOSTS}|g" -e "s|@URL@|${URL}|g" -e "s|@RDB@|${RDB}|g" -e "s|@RDB1@|$((RDB + 1))|g" \
        -e "s|@WORKERS@|${WORKERS}|g" -e "s|@EAGER@|${EAGER}|g" -e "s|@BASE@|${BASE}/${ENVNAME}|g" \
        "${HERE}/env.template" > "${ENVFILE}"
    chown root:"${APP_USER}" "${ENVFILE}"
    chmod 640 "${ENVFILE}"
  fi
  DBPASS="$(sed -n 's|^DATABASE_URL=postgres://[^:]*:\([^@]*\)@.*|\1|p' "${ENVFILE}")"
  sudo -u postgres psql -qtAc "SELECT 1 FROM pg_roles WHERE rolname='${DB}'" | grep -q 1 \
    || sudo -u postgres psql -qc "CREATE ROLE ${DB} LOGIN PASSWORD '${DBPASS}'"
  sudo -u postgres psql -qtAc "SELECT 1 FROM pg_database WHERE datname='${DB}'" | grep -q 1 \
    || sudo -u postgres createdb -O "${DB}" -E UTF8 -T template0 --locale=C.UTF-8 "${DB}"
done

# ---------------------------------------------------------------- systemd
log "systemd units"
for u in tiptop-web@.service tiptop-worker@.service tiptop-beat@.service; do
  install -m 644 "${HERE}/systemd/${u}" "/etc/systemd/system/${u}"
done
systemctl daemon-reload
systemctl enable tiptop-web@production tiptop-worker@production tiptop-beat@production tiptop-web@staging >/dev/null

# ---------------------------------------------------------------- Nginx
log "Nginx"
if [ ! -f "${ETC}/staging.htpasswd" ]; then
  STAGING_PASSWORD="${STAGING_PASSWORD:-$(gen 12)}"
  htpasswd -bc "${ETC}/staging.htpasswd" tiptop "${STAGING_PASSWORD}" >/dev/null
  chown root:www-data "${ETC}/staging.htpasswd"; chmod 640 "${ETC}/staging.htpasswd"
  echo "Staging sign-in: user tiptop, password ${STAGING_PASSWORD} (stored only as a hash in ${ETC}/staging.htpasswd)"
fi
install -m 644 "${HERE}/nginx/tiptop-common.conf" /etc/nginx/conf.d/tiptop-common.conf
install -m 644 "${HERE}/nginx/tiptop-ssl.inc" /etc/nginx/snippets/tiptop-ssl.inc
for ENVNAME in production staging; do
  sed -e "s|@ENV@|${ENVNAME}|g" "${HERE}/nginx/tiptop-locations.inc" > "/etc/nginx/snippets/tiptop-${ENVNAME}.inc"
  sed -e "s|@ENV@|${ENVNAME}|g" "${HERE}/nginx/tiptop-proxy.inc" > "/etc/nginx/snippets/tiptop-proxy-${ENVNAME}.inc"
done
install -d -m 755 /var/www/letsencrypt
CERT_PROD="/etc/letsencrypt/live/${DOMAIN}/fullchain.pem"
CERT_STAGE="/etc/letsencrypt/live/${STAGING_DOMAIN}/fullchain.pem"
if [ -f "${CERT_PROD}" ] && [ -f "${CERT_STAGE}" ]; then TEMPLATE=tiptop.conf; else TEMPLATE=tiptop-http.conf; fi
sed -e "s|@DOMAIN@|${DOMAIN}|g" -e "s|@STAGING_DOMAIN@|${STAGING_DOMAIN}|g" "${HERE}/nginx/${TEMPLATE}" > /etc/nginx/sites-available/tiptop.conf
ln -sf /etc/nginx/sites-available/tiptop.conf /etc/nginx/sites-enabled/tiptop.conf
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl reload nginx

# ---------------------------------------------------------------- TLS
if [ "${SKIP_TLS:-0}" != 1 ] && [ "${TEMPLATE}" = tiptop-http.conf ]; then
  if [ -z "${LE_EMAIL}" ]; then
    echo "!! LE_EMAIL not set: certificates skipped. Run again with LE_EMAIL once DNS points here." >&2
  else
    log "Let's Encrypt certificates"
    certbot certonly --webroot -w /var/www/letsencrypt --non-interactive --agree-tos -m "${LE_EMAIL}" \
      -d "${DOMAIN}" -d "www.${DOMAIN}" --keep-until-expiring
    certbot certonly --webroot -w /var/www/letsencrypt --non-interactive --agree-tos -m "${LE_EMAIL}" \
      -d "${STAGING_DOMAIN}" --keep-until-expiring
    sed -e "s|@DOMAIN@|${DOMAIN}|g" -e "s|@STAGING_DOMAIN@|${STAGING_DOMAIN}|g" "${HERE}/nginx/tiptop.conf" > /etc/nginx/sites-available/tiptop.conf
    nginx -t && systemctl reload nginx
  fi
fi
if [ -d /etc/letsencrypt/renewal-hooks/deploy ]; then
  printf '#!/bin/sh
systemctl reload nginx
' > /etc/letsencrypt/renewal-hooks/deploy/reload-nginx.sh
  chmod 755 /etc/letsencrypt/renewal-hooks/deploy/reload-nginx.sh
fi

# ---------------------------------------------------------------- backups and logs
log "Backups (nightly 03:15, 30 days) and log rotation"
install -m 755 "${HERE}/backup.sh" /usr/local/bin/tiptop-backup
install -m 755 "${HERE}/restore.sh" /usr/local/bin/tiptop-restore
install -d -m 700 /var/backups/tiptop
[ -f "${ETC}/backup.env" ] || printf 'BACKUP_TARGET=%s\nBACKUP_KEEP_DAYS=30\n' "${BACKUP_TARGET:-}" > "${ETC}/backup.env"
chmod 600 "${ETC}/backup.env"
install -m 644 /dev/stdin /etc/cron.d/tiptop <<'EOF'
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
15 3 * * * root /usr/local/bin/tiptop-backup >> /var/log/tiptop/backup.log 2>&1
EOF
install -m 644 /dev/stdin /etc/logrotate.d/tiptop <<'EOF'
/var/log/tiptop/*.log {
    weekly
    rotate 8
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
}
EOF

log "Done. Next: deploy the code with deploy/deploy.sh staging, test, then deploy/deploy.sh production."
