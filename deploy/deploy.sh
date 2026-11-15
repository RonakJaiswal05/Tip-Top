#!/usr/bin/env bash
# Deploy the app to one environment. Run on the server as root (or with sudo), any number of times:
#
#   sudo REPO_URL=git@github.com:OWNER/tiptop.git bash deploy/deploy.sh staging [git-ref]
#   sudo bash deploy/deploy.sh production main
#
# Steps: fetch the code, install dependencies (uv, locked), check settings, migrate, collect static files, seed what
# is missing (first deploy), set up roles, restart Gunicorn/Celery, smoke test. Production refuses to start without a
# working email backend (withdrawal confirmations).
set -euo pipefail
ENVNAME="${1:?staging or production}"
REF="${2:-main}"
[[ "$ENVNAME" =~ ^(staging|production)$ ]] || { echo "staging or production" >&2; exit 1; }
BASE="/srv/tiptop/${ENVNAME}"
SRC="${BASE}/src"
APP="${BASE}/app"
UV=/srv/tiptop/.local/bin/uv
ENVFILE="/etc/tiptop/${ENVNAME}.env"
REPO_URL="${REPO_URL:-$(git -C "$SRC" remote get-url origin 2>/dev/null || true)}"
as_app() { sudo -u tiptop -H bash -c "set -a; . ${ENVFILE}; set +a; cd ${APP}; $*"; }

echo "==> code (${REF})"
if [ ! -d "$SRC/.git" ]; then
  [ -n "$REPO_URL" ] || { echo "Set REPO_URL for the first deploy." >&2; exit 1; }
  sudo -u tiptop -H git clone --quiet "$REPO_URL" "$SRC"
fi
sudo -u tiptop -H git -C "$SRC" fetch --quiet --tags origin
sudo -u tiptop -H git -C "$SRC" checkout --quiet --force "$REF"
sudo -u tiptop -H git -C "$SRC" reset --quiet --hard "origin/${REF}" 2>/dev/null || true
ln -sfn "$SRC/app" "$APP"
# the seed reads the prototype (images, texts, legal pages) from the repository root
sudo -u tiptop -H git -C "$SRC" log -1 --format='    %h %s (%ci)'

echo "==> dependencies"
as_app "${UV} sync --frozen --no-dev --quiet"

echo "==> checks"
as_app ".venv/bin/python manage.py check --deploy --fail-level ERROR"

echo "==> database"
FIRST=0
as_app ".venv/bin/python manage.py showmigrations catalog | grep -q '\[X\]'" || FIRST=1
as_app ".venv/bin/python manage.py migrate --noinput"

echo "==> static files"
as_app ".venv/bin/python manage.py collectstatic --noinput -v0"

if [ "$FIRST" = 1 ]; then
  echo "==> first deploy: seeding catalogue, shops, texts, media, legal pages, redirects"
  as_app ".venv/bin/python manage.py seed_site"
  as_app ".venv/bin/python manage.py seed_redirects"
fi
as_app ".venv/bin/python manage.py setup_roles"

echo "==> restart"
systemctl restart "tiptop-web@${ENVNAME}"
if [ "$ENVNAME" = production ]; then
  systemctl restart tiptop-worker@production tiptop-beat@production
fi

echo "==> smoke test"
sleep 2
SOCK="/run/tiptop-${ENVNAME}/gunicorn.sock"
HOST="$(sed -n 's/^DJANGO_ALLOWED_HOSTS=\([^,]*\).*/\1/p' "$ENVFILE")"
for path in /healthz /de/ /en/ /de/reparatur/apple-iphone-13/ /api/catalog.json /sitemap.xml; do
  code="$(curl -s -o /dev/null -w '%{http_code}' --unix-socket "$SOCK" -H "Host: ${HOST}" -H 'X-Forwarded-Proto: https' "http://localhost${path}")"
  printf '    %-36s %s\n' "$path" "$code"
  [ "$code" = 200 ] || { echo "Smoke test failed on ${path}" >&2; exit 1; }
done
echo "Deployed ${REF} to ${ENVNAME}."
