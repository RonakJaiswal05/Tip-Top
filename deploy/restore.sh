#!/usr/bin/env bash
# Restore a backup into an environment (default: staging, so a restore can be tested without touching production).
#   sudo tiptop-restore /var/backups/tiptop/tiptop_production_2026-11-17_0315.dump [staging|production] [media.tar.gz]
set -euo pipefail
DUMP="${1:?path to a .dump file}"
ENVNAME="${2:-staging}"
MEDIA="${3:-}"
DB="tiptop_${ENVNAME}"
if [ "$ENVNAME" = production ]; then
  read -r -p "Restore into PRODUCTION and replace its data? Type 'production' to continue: " ok
  [ "$ok" = production ] || exit 1
fi
systemctl stop "tiptop-web@${ENVNAME}" "tiptop-worker@${ENVNAME}" "tiptop-beat@${ENVNAME}" 2>/dev/null || true
sudo -u postgres dropdb --if-exists "$DB"
sudo -u postgres createdb -O "$DB" -E UTF8 -T template0 --locale=C.UTF-8 "$DB"
sudo -u postgres pg_restore --no-owner --role="$DB" -d "$DB" "$DUMP"
if [ -n "$MEDIA" ]; then
  rm -rf "/srv/tiptop/${ENVNAME}/media.old" && mv "/srv/tiptop/${ENVNAME}/media" "/srv/tiptop/${ENVNAME}/media.old"
  tar -C "/srv/tiptop/${ENVNAME}" -xzf "$MEDIA"
  chown -R tiptop:tiptop "/srv/tiptop/${ENVNAME}/media"
fi
systemctl start "tiptop-web@${ENVNAME}"
[ "$ENVNAME" = production ] && systemctl start tiptop-worker@production tiptop-beat@production
echo "Restored ${DUMP} into ${ENVNAME}. Check the site and the admin."
