# How to use the api?

The canonical machine-readable contract for this version is the [OpenAPI specification](../../openapi/sellaris-v1.yaml).

This page is the human-readable companion to that file. It explains how the API is organized, what is public, and which endpoints are staff-protected.

## Staff protected endpoints

Supported API prefixes:

- `/api/v1`
- `/v1`

Examples below use `/api/v1`.

## Authentication and ownership model

Sellaris uses Django session authentication.

- Public users can still create carts, wishlists, orders, and payment initializations
- Guests are tracked by `session_key`
- Logged-in users are tracked by `request.user`
- When a user registers or logs in, guest cart, wishlist, and pending order ownership is transferred to the user account

For browser clients:

- keep cookies enabled
- send CSRF tokens on unsafe requests
- do not treat this API as a stateless bearer-token API

See [Authentication and access control](./authentication.md) for the full session model and role behavior.

## Access matrix

| Access level | What it can do |
|---|---|
| Public | Read catalog, manage guest cart/wishlist, create checkout orders, initialize payments, register, verify email, log in, use OAuth |
| Authenticated user | View and update own account, soft-delete own account, view own orders, view own payment records |
| Staff (`is_staff=true`) | Create/update/delete categories, products, variants, specifications, product images, and inventory stock quantities |
| Staff audit | Read inventory logs through the endpoint that uses DRF `IsAdminUser` |

## Staff and admin protected endpoints

These are the endpoints that are not public:

### Staff write endpoints

- `POST|PUT|PATCH|DELETE /api/v1/products/categories`
- `POST|PUT|PATCH|DELETE /api/v1/products/categories/{categoryId}`
- `POST|PUT|PATCH|DELETE /api/v1/products/products`
- `POST|PUT|PATCH|DELETE /api/v1/products/products/{productId}`
- `POST|PUT|PATCH|DELETE /api/v1/products/product-variants`
- `POST|PUT|PATCH|DELETE /api/v1/products/product-variants/{variantId}`
- `POST|PUT|PATCH|DELETE /api/v1/products/specifications`
- `POST|PUT|PATCH|DELETE /api/v1/products/specifications/{specificationId}`
- `POST|PUT|PATCH|DELETE /api/v1/products/product-images`
- `POST|PUT|PATCH|DELETE /api/v1/products/product-images/{imageId}`
- `POST /api/v1/inventories/set-stock-quantity`
- `POST /api/v1/inventories/adjust-stock-quantity`
- `POST /api/v1/inventories/bulk-stock-quantity-update`

### Staff audit endpoint

- `GET /api/v1/inventories/inventory-log`

Important note:

- this endpoint is conceptually “admin audit”
- the current permission class is DRF `IsAdminUser`
- in DRF that effectively means any authenticated user with `is_staff=true`
- there is no stricter superuser-only API layer in the current codebase

## Endpoint groups

### Users

- `POST /api/v1/users/register`
- `POST /api/v1/users/login`
- `GET /api/v1/users/verify-email`
- `POST /api/v1/users/resend-email-verify`
- `GET /api/v1/users/account-info`
- `PATCH /api/v1/users/manage-account`
- `POST /api/v1/users/delete`
- `POST /api/v1/users/google`
- `POST /api/v1/users/facebook`
- `POST /api/v1/users/apple`

### Product catalog

- `GET /api/v1/products/categories`
- `GET /api/v1/products/categories/{categoryId}`
- `GET /api/v1/products/products`
- `GET /api/v1/products/products/{productId}`
- `GET /api/v1/products/product-variants`
- `GET /api/v1/products/product-variants/{variantId}`
- `GET /api/v1/products/specifications`
- `GET /api/v1/products/specifications/{specificationId}`
- `GET /api/v1/products/product-images`
- `GET /api/v1/products/product-images/{imageId}`

### Cart

- `GET /api/v1/carts/carts`
- `GET /api/v1/carts/carts/{cartId}`
- `DELETE /api/v1/carts/carts/{cartId}`
- `GET /api/v1/carts/cart-items`
- `POST /api/v1/carts/cart-items`
- `GET /api/v1/carts/cart-items/{cartItemId}`
- `PUT /api/v1/carts/cart-items/{cartItemId}`
- `PATCH /api/v1/carts/cart-items/{cartItemId}`
- `DELETE /api/v1/carts/cart-items/{cartItemId}`

Notes:

- `GET /carts/carts` returns the current cart for the active session or user
- `GET /carts/carts/{cartId}` does not expose arbitrary cart access; the view still returns the current caller’s cart
- direct cart creation and cart update methods are intentionally disabled

### Wishlists

- `GET /api/v1/wishlists/wishlists`
- `POST /api/v1/wishlists/wishlists`
- `GET /api/v1/wishlists/wishlists/{wishlistId}`
- `PUT /api/v1/wishlists/wishlists/{wishlistId}`
- `PATCH /api/v1/wishlists/wishlists/{wishlistId}`
- `DELETE /api/v1/wishlists/wishlists/{wishlistId}`
- `GET /api/v1/wishlists/wishlist-items`
- `POST /api/v1/wishlists/wishlist-items`
- `GET /api/v1/wishlists/wishlist-items/{wishlistItemId}`
- `DELETE /api/v1/wishlists/wishlist-items/{wishlistItemId}`

Notes:

- own private wishlists are returned by default
- `?from=others` switches list behavior to public wishlists owned by other users
- guests can own wishlists through the Django session

### Checkout and orders

- `GET /api/v1/orders/checkout`
- `POST /api/v1/orders/checkout`
- `GET /api/v1/orders/checkout/{orderId}`

The write path is called `checkout`, but it creates `Order` records.

### Payments

- `GET /api/v1/payments`
- `POST /api/v1/payments/initialize`

The payment list is ownership-scoped. Users only see payment records for their own orders or current guest session.

### Payment webhooks

Configured provider webhook views live outside the versioned prefix:

- intended Flutterwave webhook route: `/payments/webhook/flutterwave`
- intended Paystack webhook route: `/payments/webhook/paystack`

Because the root include in `config/urls.py` is registered without a trailing slash, verify the resolved deployed path before giving it to a provider.

## List behavior

Most list endpoints use the project’s default pagination:

- default page size: `10`
- optional query parameter: `page_size`
- maximum page size: `50`

Inventory logs use a separate pagination class:

- default page size: `50`
- maximum page size: `200`

Common list query parameters:

- `page`
- `page_size`
- `search`
- `ordering`
- resource-specific filters such as `status`, `provider`, `category`, `currency`, `is_public`

## Business rules that affect API consumers

- Cart item price is a snapshot of product variant price at add time
- Checkout revalidates price and stock before order creation
- Checkout can auto-adjust quantities downward if stock dropped
- Stock is reserved when an order is created, not when an item is added to cart
- Payment initialization is idempotent for an already-initialized order
- Successful payment confirmation moves stock from reserved to confirmed deduction
- The cart is not cleared automatically on checkout creation
- The codebase intends stale pending orders to expire after 40 minutes

## Why this OpenAPI file is useful for AI agents

Another AI system can use the [OpenAPI specification](../../openapi/sellaris-v1.yaml) to:

- infer exact request shapes
- generate form schemas
- generate typed clients
- identify resource ownership rules
- understand which endpoints need staff access
- scaffold admin dashboards separately from shopper UI

## Related documents

- [Overview](./intro.md)
- [Getting started](./getting-started.md)
- [Authentication and access control](./authentication.md)
- [System workflow](./whole-workflow.md)
- [FAQ](./faq.md)
