# VPS deployment (Docker Compose)

This guide shows how to deploy the Django app with Postgres, Redis, Celery worker and Nginx on a VPS (Ubuntu/Debian).

## What you get
- Nginx (port 80) reverse-proxying to Gunicorn (port 8000)
- Postgres with persistent data
- Redis for Celery broker
- Celery worker
- Media files persisted and served by Nginx (`/uploads/`)
- Static files served by WhiteNoise from the `web` container

## Prerequisites
- A fresh VPS (Ubuntu 22.04/24.04 recommended)
- A non-root user with sudo
- Docker Engine and Docker Compose plugin installed

## 1) Install Docker
```
# As root or via sudo
apt-get update
apt-get install -y ca-certificates curl gnupg
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo $VERSION_CODENAME) stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
usermod -aG docker $USER
```
Re-login to enable docker group.

## 2) Clone the repo
```
cd ~
git clone https://github.com/denskkk/services-exchange-main.git
cd services-exchange-main
```

## 3) Create production env file
Copy and edit:
```
cp .env.prod.example .env.prod
# Edit values (SECRET_KEY, passwords, domain)
```

Key variables:
- `SECRET_KEY`: generate a long random string
- `ALLOWED_HOSTS`: set to your domain or server IP
- `CSRF_TRUSTED_ORIGINS`: include https://yourdomain.com (and http:// during initial tests)
- `DB_*` and `POSTGRES_*`: same credentials

## 4) Start the stack
```
docker compose up -d --build
```

Check containers:
```
docker compose ps
```

## 5) Initialize the app
```
# Run DB migrations
docker compose exec web python manage.py migrate

# Collect static files (WhiteNoise serves them)
docker compose exec web python manage.py collectstatic --noinput

# Create admin user
docker compose exec web python manage.py createsuperuser
```

Open http://<server-ip>/ in your browser.

## 6) Logs and troubleshooting
```
docker compose logs -f nginx
docker compose logs -f web
```

## 7) Optional: enable HTTPS
1. Obtain Let’s Encrypt certs on the host (outside Docker), e.g. using certbot:
```
apt-get install -y certbot
certbot certonly --standalone -d yourdomain.com
```
Certs will be in `/etc/letsencrypt/live/yourdomain.com/`.
2. Mount the certs directory into the nginx container by adding a new volume:
```
# docker-compose.yml, nginx service -> volumes
# - /etc/letsencrypt/live/yourdomain.com/:/certs:ro
```
3. Replace `docker/nginx/default.conf` with `docker/nginx/default.ssl.conf.sample` (copy and edit server_name and certificate file names), then restart Nginx:
```
docker compose cp docker/nginx/default.ssl.conf.sample nginx:/etc/nginx/conf.d/default.conf
# or edit the repo file and
docker compose restart nginx
```

## 8) Updates / deploys
```
# From repo dir
git pull
docker compose build
docker compose up -d
# Migrations if needed
docker compose exec web python manage.py migrate
```

## Notes
- Media files persist in `src/uploads/` on the host and are served by Nginx.
- Postgres data persists in `docker/postgres/`.
- If you need Celery Beat, add a `beat` service similar to `worker`.
