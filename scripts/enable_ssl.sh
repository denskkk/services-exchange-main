#!/usr/bin/env bash
set -euo pipefail

# Enable HTTPS for the Nginx container after certificates are issued on the host.
# Usage: bash scripts/enable_ssl.sh yourdomain.com

DOMAIN=${1:-}
if [[ -z "${DOMAIN}" ]]; then
  echo "Usage: bash scripts/enable_ssl.sh yourdomain.com" >&2
  exit 1
fi

FULLCHAIN="/etc/letsencrypt/live/${DOMAIN}/fullchain.pem"
PRIVKEY="/etc/letsencrypt/live/${DOMAIN}/privkey.pem"

if [[ ! -f "$FULLCHAIN" || ! -f "$PRIVKEY" ]]; then
  echo "Certificates not found at: $FULLCHAIN and $PRIVKEY" >&2
  echo "Issue them first, e.g.: certbot certonly --standalone -d ${DOMAIN} -d www.${DOMAIN}" >&2
  exit 1
fi

# Stop nginx so we can swap config safely (not strictly required, but clean)
docker compose stop nginx || true

# Create a local override with the given DOMAIN
TMP_OVERRIDE="docker-compose.ssl.override.local.yml"
sed "s/YOUR_DOMAIN_HERE/${DOMAIN}/g" docker-compose.ssl.override.yml > "$TMP_OVERRIDE"

# Bring up nginx with 443 and cert mounts
docker compose -f docker-compose.yml -f "$TMP_OVERRIDE" up -d nginx

# Copy SSL config into container and restart nginx
docker compose cp docker/nginx/default.ssl.conf.sample nginx:/etc/nginx/conf.d/default.conf

docker compose restart nginx

echo "HTTPS enabled at: https://${DOMAIN}"