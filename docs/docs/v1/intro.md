# Sellaris Backend Overview

Sellaris is a Django + Django REST Framework e-commerce backend engine built around modular domain apps:

- `users` for registration, login, verification, OAuth, and account lifecycle
- `products` for catalog, variants, specifications, and product media
- `cart` for guest and authenticated carts
- `wishlists` for private and shareable saved lists
- `orders` for checkout and order snapshots
- `payments` for payment initialization and webhook confirmation
- `inventory` for stock mutation and stock audit logging

## What the backend already supports

- Public product catalog browsing
- Guest carts, guest wishlists, and guest checkout
- Session-to-user ownership transfer after login or registration
- Order creation with stock reservation
- Payment initialization for `flutterwave` and `paystack`
- Email verification and social OAuth login
- Staff-protected catalog and inventory write operations

## Base URLs

The backend exposes the same API under two versioned prefixes:

- `/api/v1`
- `/v1`

All endpoint paths in the documentation use the `/api/v1` form for clarity.

## Authentication model

Sellaris currently uses Django session authentication, not bearer tokens.

- Guests are identified by Django session state
- Logged-in users receive a session cookie after `POST /users/login`
- Ownership for carts, wishlists, orders, and payment records is derived from either:
  - `request.user`, or
  - `request.session.session_key`

This matters for frontend clients and AI agents:

- a browser UI should preserve cookies across requests
- unsafe browser requests should also send the CSRF token
- machine clients that do not keep cookies cannot use the ownership-based flows correctly

## Role model

There are three practical access levels in the current codebase:

- Public: catalog reads, guest cart/wishlist flows, checkout, payment initialization, registration, login
- Authenticated user: own account management, own orders, own payment history
- Staff: product/catalog writes and inventory mutation endpoints

There is no separate superuser-only API surface at the moment. The endpoint documented as admin audit uses DRF `IsAdminUser`, which in practice means `is_staff=True`.

## Primary deliverables in this docs set

- `docs/openapi/sellaris-v1.yaml`: machine-readable OpenAPI spec
- `docs/docs/v1/api.md`: readable API guide and access matrix
- `docs/docs/v1/authentication.md`: session auth, CSRF, role access, guest transfer behavior
- `docs/docs/v1/whole-workflow.md`: how the system works end to end
- `docs/docs/v1/faq.md`: developer and integration FAQ

## For frontend and AI-driven UI generation

If you want a clean generated UI, the OpenAPI file is the source of truth to start from. It is the best entrypoint for:

- generating API clients
- generating request/response types
- scaffolding forms and tables
- mapping auth requirements and role gating
- understanding which resources are session-scoped versus globally readable
