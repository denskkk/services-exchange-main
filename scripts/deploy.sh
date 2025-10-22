#!/usr/bin/env bash
set -euo pipefail

# Simple one-shot deploy for the current directory (root of repo)
# Usage: bash scripts/deploy.sh

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is not installed. Install Docker Engine + Compose first." >&2
  exit 1
fi

# Build and start stack
docker compose up -d --build

# Run migrations and collectstatic
docker compose exec web python manage.py migrate --noinput
docker compose exec web python manage.py collectstatic --noinput

# Show status
docker compose ps

echo "\nDeploy finished. Open: http://<your-server-ip>/ (HTTP)."
echo "To create an admin user: docker compose exec web python manage.py createsuperuser"
echo "To enable HTTPS later: bash scripts/enable_ssl.sh yourdomain.com (after certbot)."
