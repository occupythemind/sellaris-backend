# Getting Started

## Runtime stack

- Python / Django backend
- PostgreSQL database
- Redis broker
- Celery workers
- Celery Beat scheduler
- Optional storage and email providers in production

## Local development

The repository is already wired for Docker Compose development.

```bash
docker compose --env-file .env -f docker/docker-compose.yml up --build
```

The development stack starts:

- `web` on port `8000`
- `db` with PostgreSQL 17
- `redis`
- `celery_default`
- `celery_emails`
- `celery_beat`

## Required environment categories

The settings require more than just a secret key and database URL. At minimum, configure values for:

- Django core: `SECRET_KEY`, `DEBUG`, `DATABASE_URL`
- frontend/backend URLs: `FRONTEND_BASE_URL`, `BACKEND_BASE_URL`
- payment redirect and verification paths: `PAYMENT_REDIRECT_PATH`, `VERIFY_EMAIL_PATH`
- payment providers: `FLW_SECRET_KEY`, `FLW_SECRET_HASH`, `FLW_BASE_URL`, `PST_SECRET_KEY`
- email: `EMAIL_PROVIDER`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL`
- OAuth: `GOOGLE_CLIENT_ID`, `FACEBOOK_APP_ID`, `FACEBOOK_APP_SECRET`, `APPLE_CLIENT_ID`

Production also expects:

- `ALLOWED_HOSTS`
- `CORS_ALLOWED_ORIGINS`
- `AWS_*` storage variables for media/static files
- Cloudinary credentials for image processing

## Versioning and path conventions

- Public API prefixes: `/api/v1` and `/v1`
- Router-generated resource paths use `trailing_slash=False`
- In practice, documented endpoints should be called without a trailing slash

One thing to watch carefully:

- some grouped URLs have repeated path segments such as `/api/v1/products/products`
- this is not a documentation typo; it comes from the current include structure

## Session-based clients

Sellaris is designed to work well with browser clients:

- guests get a session-backed cart and wishlist
- login upgrades guest-owned data into the authenticated account
- subsequent account/order/payment requests rely on the session cookie

If you are building a SPA, configure:

- `credentials: 'include'` on fetch/XHR
- CSRF handling for unsafe requests

## Useful first tests

After booting the stack, validate these flows first:

1. `GET /api/v1/products/products`
2. `POST /api/v1/carts/cart-items`
3. `POST /api/v1/orders/checkout`
4. `POST /api/v1/payments/initialize`
5. `POST /api/v1/users/register`

## Core scheduled behaviors

Celery Beat is important to the business workflow:

- guest carts older than 14 days are cleaned up daily
- guest wishlists older than 30 days are cleaned up daily
- reserved stock is intended to be released for stale pending orders every 5 minutes
- soft-deleted accounts are permanently deleted 30 days later

Those lifecycle rules are explained in detail in `whole-workflow.md`.
