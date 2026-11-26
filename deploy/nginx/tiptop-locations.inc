# /etc/nginx/snippets/tiptop-@ENV@.inc: shared by the HTTP and HTTPS server blocks of the @ENV@ site.

access_log /var/log/nginx/tiptop-@ENV@.access.log tiptop;
error_log /var/log/nginx/tiptop-@ENV@.error.log warn;

add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;

location = /favicon.ico { alias /srv/tiptop/@ENV@/static/site/img/logo-mark-180.png; access_log off; expires 30d; }

# hashed file names (ManifestStaticFilesStorage): cache for a year
location /static/ {
    alias /srv/tiptop/@ENV@/static/;
    access_log off;
    expires 1y;
    add_header Cache-Control "public, immutable" always;
    add_header X-Content-Type-Options "nosniff" always;
    gzip_static on;
}

# signed purchase contracts are personal data: only the admin may hand them out
location ^~ /media/contracts/ { return 404; }
location /media/ {
    alias /srv/tiptop/@ENV@/media/;
    access_log off;
    expires 30d;
    add_header Cache-Control "public" always;
    add_header X-Content-Type-Options "nosniff" always;
    # uploaded files are never executed or rendered as HTML
    location ~* \.(html?|svg|js)$ { add_header Content-Security-Policy "default-src 'none'; style-src 'unsafe-inline'; sandbox" always; add_header X-Content-Type-Options "nosniff" always; }
}

location = /api/requests/ { limit_req zone=tt_forms burst=10 nodelay; include snippets/tiptop-proxy-@ENV@.inc; }
location = /api/consent/ { limit_req zone=tt_forms burst=20 nodelay; include snippets/tiptop-proxy-@ENV@.inc; }
location = /admin/login/ { limit_req zone=tt_login burst=5 nodelay; include snippets/tiptop-proxy-@ENV@.inc; }
location /admin/password_reset/ { limit_req zone=tt_login burst=3 nodelay; include snippets/tiptop-proxy-@ENV@.inc; }

location / {
    limit_req zone=tt_general burst=60 nodelay;
    include snippets/tiptop-proxy-@ENV@.inc;
}
