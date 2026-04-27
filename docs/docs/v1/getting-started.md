# Getting Started

This page is the fastest path to running the backend locally and validating the API shape that frontend clients will consume.

## Runtime stack

- Django application server
- PostgreSQL database
- Redis broker
- Celery workers
- Celery Beat scheduler
- Optional email and media providers in production

## Repository layout that matters for setup

The current project layout uses root-level container files:

- `docker-compose.yml` for development
- `docker-compose.prod.yml` for production
- `Dockerfile` for the shared application image
- `nginx/` for reverse-proxy and HTTPS configuration

## Development setup

### 1. Create a local environment file

Development currently expects `.env.local` in the project root.

At minimum, define:

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

### 2. Build the app image

```bash
docker build -t sellaris:latest -f Dockerfile .
```

### 3. Start the stack

```bash
docker compose --env-file .env.local -f docker-compose.yml up -d
```

The development stack starts:

- `web` on port `8000`
- `db` with PostgreSQL 17
- `redis`
- `celery_default`
- `celery_emails`
- `celery_beat`

### 4. Run migrations

```bash
docker compose --env-file .env.local -f docker-compose.yml exec web python3 manage.py migrate
```

### 5. Optional admin user

```bash
docker compose --env-file .env.local -f docker-compose.yml exec web python3 manage.py createsuperuser
```

## Production setup highlights

Production currently adds:

- Daphne / ASGI app serving
- secure Redis broker password
- Nginx reverse proxy
- Certbot renewal container
- HTTPS proxy headers and secure cookie settings
- `/health/` container health check

Production expects `.env` in the project root, not inside a `docker/` folder.

## Environment variables that matter most to integrations

The codebase is especially sensitive to these groups of settings:

- Django core: `SECRET_KEY`, `DEBUG`, `DATABASE_URL`
- frontend origin and callbacks: `FRONTEND_BASE_URL`, `VERIFY_EMAIL_PATH`, `PAYMENT_REDIRECT_PATH`
- payment providers: `FLW_SECRET_KEY`, `FLW_SECRET_HASH`, `FLW_BASE_URL`, `PST_SECRET_KEY`
- auth/cookie security: `CORS_ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS`
- email delivery: `EMAIL_PROVIDER`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL`
- OAuth providers: `GOOGLE_CLIENT_ID`, `FACEBOOK_APP_ID`, `FACEBOOK_APP_SECRET`, `APPLE_CLIENT_ID`
- production-only infra: `REDIS_PASSWORD`, `DOMAIN_NAME`, `DOMAIN_MAIL`, `AWS_*`, `CLOUDINARY_*`

## Request conventions

- Public API prefixes: `/api/v1` and `/v1`
- Router-generated resource paths use `trailing_slash=False`
- Endpoint examples in this documentation intentionally omit trailing slashes

Some grouped routes repeat a resource segment, for example:

- `/api/v1/products/products`
- `/api/v1/carts/cart-items`
- `/api/v1/wishlists/wishlists`

That is expected and reflects the current router structure.

## Client behavior requirements

Sellaris is built for session-aware clients:

- guests receive a session-backed cart and wishlist
- login and registration transfer guest-owned data into the authenticated account
- account, order, and payment reads depend on the active session cookie

For browser clients:

- send requests with credentials enabled
- include a CSRF token on unsafe requests that send cookies

The current source does not expose a dedicated CSRF bootstrap endpoint, so plan for standard Django CSRF handling in your frontend shell.

## Recommended smoke tests

After the local stack is running, validate these flows first:

1. `GET /api/v1/products/products`
2. `POST /api/v1/carts/cart-items`
3. `POST /api/v1/orders/checkout`
4. `POST /api/v1/payments/initialize`
5. `POST /api/v1/users/register`
6. `GET /health/`

## Scheduled behavior to be aware of

Celery Beat supports several lifecycle rules that affect integrations:

- guest carts older than 14 days are cleaned up daily
- guest wishlists older than 30 days are cleaned up daily
- stale pending order reservations are intended to be released every 5 minutes
- soft-deleted accounts are permanently deleted 30 days later

See [System workflow](./whole-workflow.md) for the detailed behavior and caveats.

## Next reads

- [API guide](./api.md)
- [Authentication and access control](./authentication.md)
- [System workflow](./whole-workflow.md)
- [OpenAPI specification](../../openapi/sellaris-v1.yaml)
