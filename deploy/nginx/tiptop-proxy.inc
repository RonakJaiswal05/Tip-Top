# /etc/nginx/snippets/tiptop-proxy-@ENV@.inc
proxy_pass http://unix:/run/tiptop-@ENV@/gunicorn.sock;
proxy_http_version 1.1;
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $remote_addr;
proxy_set_header X-Forwarded-Proto $scheme;
proxy_set_header Connection "";
proxy_read_timeout 60s;
proxy_redirect off;
