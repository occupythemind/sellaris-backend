# System Workflow

This document explains the business flow implemented in the current codebase, including the timing rules and caveats that matter for production integration.

## 1. Product and inventory model

The catalog is split into:

- `Category`
- `Product`
- `ProductVariant`
- `Specification`
- `ProductImage`

Important implementation details:

- product slugs are auto-generated if not supplied
- variant SKU codes are auto-generated if not supplied
- product images are processed asynchronously after the database transaction commits
- variants track both `stock_quantity` and `reserved_stock`

Orders, carts, and wishlists are built around product variants, not base products.

## 2. Session-first commerce flow

Sellaris is designed so a guest can start shopping immediately.

Guests can:

- receive a Django session automatically
- create a cart
- add cart items
- create wishlists
- create orders
- initialize payments

Later, when the guest registers or logs in, ownership is transferred to the user account.

## 3. Cart behavior

Cart ownership rules:

- authenticated users have one active cart per user
- guests have one active cart per session

Cart item behavior:

- adding an item snapshots the current variant price into `CartItem.price`
- if the same variant is added again, quantity is incremented instead of duplicating the row
- quantity cannot exceed the variant’s current `stock_quantity`
- updating an item to another variant can merge into an existing item for that variant

Important:

- adding to cart does not reserve inventory
- cart presence is not a stock guarantee

## 4. Wishlist behavior

Wishlists support:

- authenticated ownership
- guest ownership through session
- private lists
- public lists for sharing
- multiple named wishlists per owner

The endpoint has two list modes:

- default: your own wishlists
- `?from=others`: public wishlists that do not belong to you

## 5. Checkout and order creation

Checkout is implemented through `POST /api/v1/orders/checkout`.

At order creation time, the backend:

1. resolves the current cart from the authenticated user or session
2. rejects checkout if the cart is empty
3. re-checks every line item against the current product variant price
4. re-checks every line item against available stock
5. automatically adjusts cart quantities downward if stock has dropped
6. reserves stock for valid items
7. creates the `Order`
8. creates snapshot `OrderItem` rows

This is one of the most important production behaviors in Sellaris:

- stale cart prices do not survive checkout unchanged
- stale quantities can be corrected instead of hard-failing the whole order

If every item becomes unavailable:

- checkout fails with `OUT_OF_STOCK`

If only some items changed:

- the response includes `changes.price_changes`
- the response includes `changes.stock_changes`

## 6. When stock is reserved

Stock is reserved at order creation time, not cart time.

Why that matters:

- it prevents abandoned carts from locking inventory
- it reduces false scarcity
- it still protects against overselling at the moment that matters

Reservation flow:

- available stock is computed as `stock_quantity - reserved_stock`
- `reserve_stock()` locks the variant row with `select_for_update()`
- `reserved_stock` increases
- an inventory log entry is created

## 7. Payment initialization

Payment initialization is handled by `POST /api/v1/payments/initialize`.

The endpoint:

1. requires `order_id`
2. requires `provider`
3. verifies the caller owns the order
4. rejects already paid orders
5. rejects orders not in pending state
6. reuses an existing initialized payment if one exists
7. otherwise creates a `Payment` row
8. calls the provider service and returns the provider payment URL

Supported providers:

- `flutterwave`
- `paystack`

This gives the frontend an idempotent payment-init experience for retrying checkout.

## 8. Dynamic redirect and verification URLs

The current codebase now builds some frontend-facing URLs dynamically.

### Payment redirect

When a payment is initialized:

- the backend uses `generate_dynamic_url()`
- `PAYMENT_REDIRECT_PATH` is appended
- `FRONTEND_BASE_URL` is preferred if present

### Email verification link

When a verification email is sent:

- the backend uses `generate_dynamic_url()`
- `VERIFY_EMAIL_PATH` is appended
- `FRONTEND_BASE_URL` is preferred if present

This makes staging and production deployments less dependent on hard-coded callback hosts.

## 9. Payment confirmation

Provider webhooks queue Celery tasks for actual confirmation work.

### Flutterwave flow

- verify request hash header
- log webhook payload
- queue async processor
- verify transaction against Flutterwave API
- mark payment success or failure
- confirm stock deduction
- mark order as paid

### Paystack flow

- verify HMAC signature
- log webhook payload
- queue async processor
- verify transaction against Paystack API
- mark payment success or failure
- confirm stock deduction
- mark order as paid

## 10. When stock is finally deducted

Reserved stock is only converted into actual deduction after successful payment verification.

`confirm_stock()` is intended to:

- decrease `stock_quantity`
- decrease `reserved_stock`
- write an inventory log entry

This design separates:

- shopping intent
- order reservation
- confirmed payment

## 11. Expiry and cleanup rules

The project contains several timed lifecycle rules:

### Guest cart retention

- guest carts older than 14 days are cleaned up daily

### Guest wishlist retention

- guest wishlists older than 30 days are cleaned up daily

### Guest order cleanup

- guest pending orders older than 48 hours are intended to be cleaned up daily

### Order reservation expiry

- pending orders older than 40 minutes are intended to have reserved stock released
- the task runs every 5 minutes

### Account deletion

- soft-deleted accounts are permanently deleted after 30 days

### Email verification

- verification token lifetime is effectively 24 hours

## 12. Current implementation caveats worth knowing

These are important if you are documenting or integrating the current code exactly as it exists.

### Pending-order expiry filters

The scheduled cleanup tasks filter expired orders using `"PENDING"` while the order model stores lowercase `pending`.

Intended business rule:

- release stale pending orders after 40 minutes
- delete stale guest pending orders after 48 hours

Current code caveat:

- those scheduled filters should be verified or corrected before relying on them in production

### Dynamic URL settings

The user and payment views now expect:

- `VERIFY_EMAIL_PATH`
- `PAYMENT_REDIRECT_PATH`

Make sure these are actually exposed through settings and environment configuration in every deployed environment.

### Unverified-login error branch

`LoginAPIView` still references `settings.EMAIL_VERIFY_URL` when returning the unverified-account error message.

Treat that branch as something to verify in staging after the move toward dynamic URL generation.

### OAuth new-user creation path

The OAuth service creates new users through a `full_name` field, while the current user model stores `first_name` and `last_name`.

Treat the provider flows as implemented routes that still deserve staging verification before depending on them for a production frontend.

### Inventory log read endpoint

The inventory log model contains rich audit fields, but the current response serializer is only a placeholder.

Treat that endpoint as internal or still stabilizing until the serializer is aligned with the model.

### Payment webhook route mount

The payment webhook include is mounted from `path('payments/webhook', include(...))` without a trailing slash.

Before giving webhook URLs to payment providers, confirm the final deployed routes explicitly.

## 13. Why frontend teams care about this workflow

A frontend or AI-generated UI needs this workflow detail to avoid wrong assumptions:

- cart totals can change at checkout
- stock reservation starts at order creation, not cart addition
- payment initialization can be reused
- ownership is session-based until login
- order and payment history are private to the current owner
- staff inventory APIs should never be exposed in shopper UIs
