# Sellaris API v1 Overview

Sellaris is a Django and Django REST Framework e-commerce backend organized around a set of domain modules:

- `users` for registration, login, verification, OAuth, and account lifecycle
- `products` for catalog, variants, specifications, and product media
- `cart` for guest and authenticated carts
- `wishlists` for private and shareable saved lists
- `orders` for checkout and order snapshots
- `payments` for payment initialization and webhook confirmation
- `inventory` for stock mutation and stock audit logging

## What this API supports

- Public catalog browsing
- Guest carts, guest wishlists, and guest checkout
- Session-to-user ownership transfer after login or registration
- Order creation with stock reservation
- Payment initialization for `flutterwave` and `paystack`
- Email verification and social OAuth login
- Staff-protected catalog and inventory write operations

## Base paths

The backend exposes the same API under two versioned prefixes:

- `/api/v1`
- `/v1`

All examples in this documentation use `/api/v1` for consistency.

## Authentication model

Sellaris uses Django session authentication, not bearer tokens.

- Guests are identified through Django session state
- Logged-in users receive a session cookie after `POST /api/v1/users/login`
- Ownership for carts, wishlists, orders, and payment records is derived from either `request.user` or `request.session.session_key`

This has practical implications for clients:

- browser-based clients should preserve cookies across requests
- unsafe requests should include a valid CSRF token
- machine clients that do not maintain cookies cannot use session-owned shopper flows correctly

See [Authentication and access control](./authentication.md) for integration details.

## Access model

There are three practical access levels in the current codebase:

| Access level | Description |
|---|---|
| Public | Catalog reads, guest cart and wishlist flows, checkout, payment initialization, registration, login, and OAuth entrypoints |
| Authenticated user | Own account management, own orders, and own payment history |
| Staff | Product writes, inventory writes, and inventory audit access |

The inventory log endpoint uses DRF `IsAdminUser`, which in practice means authenticated users with `is_staff=True`.

## Documentation map

Use the pages below as the primary v1 documentation set:

- [Getting started](./getting-started.md) for local setup, request conventions, and first validation calls
- [Authentication and access control](./authentication.md) for sessions, CSRF, role boundaries, and guest transfer behavior
- [API guide](./api.md) for the endpoint map, access matrix, and integration-facing behavior
- [System workflow](./whole-workflow.md) for end-to-end commerce flows and timing rules
- [FAQ](./faq.md) for common implementation and integration questions
- [OpenAPI specification](../../openapi/sellaris-v1.yaml) for the machine-readable contract

## Recommended starting points

If you are integrating a frontend or generating clients from the API, start with:

1. [OpenAPI specification](../../openapi/sellaris-v1.yaml)
2. [API guide](./api.md)
3. [Authentication and access control](./authentication.md)
4. [System workflow](./whole-workflow.md)
