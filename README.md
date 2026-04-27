# 🛒 Sellaris — Django E-Commerce Engine


Sellaris is a Django and Django REST Framework e-commerce backend engine built for session-aware shopper flows, staff-managed catalog operations, and payment-driven checkout.

## What it supports

- Public product catalog browsing
- Guest carts, guest wishlists, and guest checkout
- Account registration, login, email verification, and OAuth entrypoints
- Order creation with stock reservation
- Payment initialization for Flutterwave and Paystack
- Staff-protected catalog and inventory management
- Docker-based development and production deployments

## API surface

Versioned API prefixes:

- `/api/v1`
- `/v1`

Operational endpoint:

- `/health/`

The frontend-facing routes intentionally include repeated resource segments in some groups, for example:

- `/api/v1/products/products`
- `/api/v1/carts/cart-items`
- `/api/v1/wishlists/wishlists`

That reflects the current router structure.

## Documentation

Primary docs:

- [Overview](docs/docs/v1/intro.md)
- [Getting started](docs/docs/v1/getting-started.md)
- [Authentication and access control](docs/docs/v1/authentication.md)
- [API guide](docs/docs/v1/api.md)
- [System workflow](docs/docs/v1/whole-workflow.md)
- [FAQ](docs/docs/v1/faq.md)
- [OpenAPI specification](docs/openapi/sellaris-v1.yaml)

If you want to build a frontend quickly, start with the OpenAPI file and then read the authentication and workflow docs.

## Local development

### 1. Create `.env.local`

Development uses the root-level `docker-compose.yml` file and expects `.env.local` in the repository root.

Example minimum shape:

```env
DEBUG=True
SECRET_KEY=change-me

DB_NAME=ecommerce_db
DB_USER=ecommerce_user
DB_PASSWORD=yourpassword
DB_HOST=db
DB_PORT=5432
DATABASE_URL=postgresql://ecommerce_user:yourpassword@db:5432/ecommerce_db

FRONTEND_BASE_URL=http://localhost:3000
VERIFY_EMAIL_PATH=/verify-email
PAYMENT_REDIRECT_PATH=/payment-return

FLW_SECRET_KEY=...
FLW_SECRET_HASH=...
FLW_BASE_URL=https://api.flutterwave.com/v3
PST_SECRET_KEY=...

EMAIL_HOST=...
EMAIL_PORT=587
EMAIL_HOST_USER=...
EMAIL_HOST_PASSWORD=...
DEFAULT_FROM_EMAIL=...

GOOGLE_CLIENT_ID=...
FACEBOOK_APP_ID=...
FACEBOOK_APP_SECRET=...
APPLE_CLIENT_ID=...
```

### 2. Build the application image

```bash
docker build -t sellaris:latest -f Dockerfile .
```

### 3. Start the stack

```bash
docker compose --env-file .env.local -f docker-compose.yml up -d
```

### 4. Run migrations

```bash
docker compose --env-file .env.local -f docker-compose.yml exec web python3 manage.py migrate
```

### 5. Optional admin user

```bash
docker compose --env-file .env.local -f docker-compose.yml exec web python3 manage.py createsuperuser
```

### 6. Smoke test the API

```bash
curl http://localhost:8000/api/v1/products/products
curl http://localhost:8000/health/
```

## 🔒 Enabling HTTPS and Starting the Production Stack

This project uses dynamic Nginx configuration. You **do not** need to manually edit Nginx config files!

Production uses:

- `docker-compose.prod.yml`
- Daphne for the Django app
- Nginx reverse proxy
- Certbot for TLS renewal
- Redis with password protection
- secure cookie and proxy settings
- `/health/` for container health checks

Common production variables include:

- `ALLOWED_HOSTS`
- `CORS_ALLOWED_ORIGINS`
- `CSRF_TRUSTED_ORIGINS`
- `REDIS_PASSWORD`
- `DOMAIN_NAME`
- `DOMAIN_MAIL`
- `AWS_*`
- `CLOUDINARY_*`


### 1. Update your `.env` file
Add your domain details to your production `.env` file:
```env
DOMAIN_NAME=yourdomain.com
INCLUDE_WWW=true  # Optional: Set to true if you want to also support www.yourdomain.com
```

### 2. Get your SSL Certificate
Before running this, make sure:
- Your domain points to your server's IP address.
- Ports `80` and `443` are open on your server firewall.

Run pre-written script to fetch the certificate:
```sh
sh init-letsencrypt.sh
```

### 3. Run the docker compose
```sh
# Recommended for Redis performance in production
echo "vm.overcommit_memory = 1" | sudo tee -a /etc/sysctl.conf

# Start the containers in the background
docker compose --env-file .env -f docker-compose.prod.yml up -d

# Run database migrations
docker compose --env-file .env -f docker-compose.prod.yml exec web python3 manage.py migrate

# Collect static files
docker compose --env-file .env -f docker-compose.prod.yml exec web python3 manage.py collectstatic --no-input
```
The API will be served via Nginx at `http://localhost/` (or your configured domain).

## Current integration notes

These are worth knowing before a frontend team builds on top of the backend:

- auth is session-based, not token-based
- the code expects `VERIFY_EMAIL_PATH` and `PAYMENT_REDIRECT_PATH`
- payment and verification URLs are built dynamically from request context plus frontend config
- webhook routes should be verified carefully because of the current mount structure
- inventory audit responses are still stabilizing

## License

This project is available under the MIT License.
