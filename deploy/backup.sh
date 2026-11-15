#!/usr/bin/env bash
# Nightly backup (cron 03:15): database dump and media for production and staging, kept 30 days on the server
# and copied off the server. Installed as /usr/local/bin/tiptop-backup by setup.sh.
#
# Off-server copy: set BACKUP_TARGET in /etc/tiptop/backup.env to an rsync target reachable with root's SSH key,
# e.g. u123456@u123456.your-storagebox.de:tiptop (port in ~/.ssh/config), or "rclone:remote:bucket/tiptop" for an
# S3-compatible bucket in the EU (needs rclone configured for root).
set -euo pipefail
. /etc/tiptop/backup.env
KEEP="${BACKUP_KEEP_DAYS:-30}"
DIR=/var/backups/tiptop
STAMP="$(date +%Y-%m-%d_%H%M)"
mkdir -p "$DIR"
chmod 700 "$DIR"

for ENVNAME in production staging; do
  DB="tiptop_${ENVNAME}"
  if sudo -u postgres psql -qtAc "SELECT 1 FROM pg_database WHERE datname='${DB}'" | grep -q 1; then
    sudo -u postgres pg_dump -Fc --no-owner "$DB" > "$DIR/${DB}_${STAMP}.dump"
  fi
  if [ -d "/srv/tiptop/${ENVNAME}/media" ]; then
    tar -C "/srv/tiptop/${ENVNAME}" -czf "$DIR/media_${ENVNAME}_${STAMP}.tar.gz" media
  fi
done
# the env files hold the secret key and database passwords: needed to restore, so they are backed up too
tar -C /etc -czf "$DIR/etc-tiptop_${STAMP}.tar.gz" tiptop
chmod 600 "$DIR"/*"${STAMP}"*

find "$DIR" -type f -mtime +"$KEEP" -delete

if [ -n "${BACKUP_TARGET:-}" ]; then
  if [[ "$BACKUP_TARGET" == rclone:* ]]; then
    rclone copy "$DIR" "${BACKUP_TARGET#rclone:}" --max-age 48h
    rclone delete "${BACKUP_TARGET#rclone:}" --min-age "${KEEP}d"
  else
    rsync -a --delete "$DIR/" "$BACKUP_TARGET/"
  fi
  echo "$(date -Is) backup ${STAMP} copied to ${BACKUP_TARGET}"
else
  echo "$(date -Is) backup ${STAMP} done, NOT copied off the server (BACKUP_TARGET empty)" >&2
fi
