# Getting Started

This page is the quickest path to running the backend locally and validating the core API flows.

## Runtime stack

- Django application server
- PostgreSQL database
- Redis broker
- Celery workers
- Celery Beat scheduler
- Optional email and storage providers in production

## Start the local environment

The repository is already configured for Docker Compose development:

```bash
docker compose --env-file .env -f docker/docker-compose.yml up --build
```

The local stack starts:

- `web` on port `8000`
- `db` with PostgreSQL 17
- `redis`
- `celery_default`
- `celery_emails`
- `celery_beat`

## Environment configuration

At minimum, the application expects configuration in these categories:

- Django core: `SECRET_KEY`, `DEBUG`, `DATABASE_URL`
- frontend and backend URLs: `FRONTEND_BASE_URL`, `BACKEND_BASE_URL`
- payment redirects and verification paths: `PAYMENT_REDIRECT_PATH`, `VERIFY_EMAIL_PATH`
- payment providers: `FLW_SECRET_KEY`, `FLW_SECRET_HASH`, `FLW_BASE_URL`, `PST_SECRET_KEY`
- email delivery: `EMAIL_PROVIDER`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL`
- OAuth providers: `GOOGLE_CLIENT_ID`, `FACEBOOK_APP_ID`, `FACEBOOK_APP_SECRET`, `APPLE_CLIENT_ID`

Production deployments also expect:

- `ALLOWED_HOSTS`
- `CORS_ALLOWED_ORIGINS`
- `AWS_*` storage variables for static and media files
- Cloudinary credentials for image processing

## Request conventions

- Public API prefixes: `/api/v1` and `/v1`
- Router-generated resource paths use `trailing_slash=False`
- Endpoint examples in this documentation intentionally omit trailing slashes

Some grouped routes repeat a resource segment, for example `/api/v1/products/products`. That is expected and reflects the current router structure.

## Client behavior requirements

Sellaris is built for session-aware clients:

- guests receive a session-backed cart and wishlist
- login and registration transfer guest-owned data into the authenticated account
- account, order, and payment reads depend on the active session cookie

For browser clients:

- send requests with credentials enabled
- include CSRF protection on unsafe requests

See [Authentication and access control](./authentication.md) for the full session model.

## Recommended smoke tests

After the local stack is running, validate these flows first:

1. `GET /api/v1/products/products`
2. `POST /api/v1/carts/cart-items`
3. `POST /api/v1/orders/checkout`
4. `POST /api/v1/payments/initialize`
5. `POST /api/v1/users/register`

## Scheduled behavior to be aware of

Celery Beat supports several lifecycle rules that affect integrations:

- guest carts older than 14 days are cleaned up daily
- guest wishlists older than 30 days are cleaned up daily
- stale pending order reservations are intended to be released every 5 minutes
- soft-deleted accounts are permanently deleted 30 days later

See [System workflow](./whole-workflow.md) for the detailed behavior and current caveats.

## Next reads

- [API guide](./api.md)
- [Authentication and access control](./authentication.md)
- [System workflow](./whole-workflow.md)
- [OpenAPI specification](../../openapi/sellaris-v1.yaml)
