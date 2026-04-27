# Sellaris API v1 Overview

Sellaris is a Django and Django REST Framework e-commerce backend organized around domain-focused modules:

- `users` for registration, login, verification, OAuth, and account lifecycle
- `products` for catalog, variants, specifications, and product media
- `cart` for guest and authenticated carts
- `wishlists` for private and shareable saved lists
- `orders` for checkout and order snapshots
- `payments` for payment initialization and provider webhook confirmation
- `inventory` for stock mutation and stock audit logging

## What this API supports today

- Public catalog browsing
- Guest carts, guest wishlists, and guest checkout
- Session-to-user ownership transfer after login or registration
- Order creation with stock reservation
- Payment initialization for `flutterwave` and `paystack`
- Email verification and social OAuth entrypoints
- Staff-protected catalog and inventory write operations

## Base paths

The backend exposes the same versioned API under:

- `/api/v1`
- `/v1`

All examples in this documentation use `/api/v1` for consistency.

## Authentication model

Sellaris currently uses Django session authentication, not bearer tokens.

- Guests are identified through Django session state
- Logged-in users receive a session cookie after `POST /api/v1/users/login`
- Ownership for carts, wishlists, orders, and payment records is derived from either `request.user` or `request.session.session_key`

Practical client implications:

- browser-based clients should preserve cookies across requests
- unsafe requests should include a CSRF token when cookies are being sent
- machine clients that do not maintain cookies cannot use shopper flows correctly

See [Authentication and access control](./authentication.md) for the integration details.

## Access model

There are three practical access levels in the current codebase:

| Access level | Description |
|---|---|
| Public | Catalog reads, guest cart and wishlist flows, checkout, payment initialization, registration, login, and OAuth entrypoints |
| Authenticated user | Own account management, own orders, and own payment history |
| Staff | Product writes, inventory writes, and inventory audit access |

The inventory log endpoint uses DRF `IsAdminUser`, which in practice means authenticated users with `is_staff=True`.

## Current platform notes

While reviewing the codebase, these recent platform-level changes are reflected in the docs:

- development and production Compose files now live at the repository root
- production deploys through Nginx with Certbot-managed TLS
- `/health/` exists for container health checks
- CSRF, SameSite, secure-cookie, and trusted-origin settings are explicitly configured
- dynamic frontend URLs are now built from request context plus `VERIFY_EMAIL_PATH` and `PAYMENT_REDIRECT_PATH`

## Documentation map

Use the pages below as the primary v1 documentation set:

- [Getting started](./getting-started.md) for local setup, environment variables, and first validation calls
- [Authentication and access control](./authentication.md) for sessions, CSRF, role boundaries, and guest transfer behavior
- [API guide](./api.md) for endpoint groups, examples, and protected-route summaries
- [System workflow](./whole-workflow.md) for end-to-end commerce flows and timing rules
- [FAQ](./faq.md) for common implementation and integration questions
- [OpenAPI specification](../../openapi/sellaris-v1.yaml) for the machine-readable contract

## Recommended starting points

If you are integrating a frontend or generating clients from the API, start with:

1. [OpenAPI specification](../../openapi/sellaris-v1.yaml)
2. [API guide](./api.md)
3. [Authentication and access control](./authentication.md)
4. [System workflow](./whole-workflow.md)
