# How Sellaris Works

This document explains the actual business flow implemented in the codebase, including the timing rules that matter for production integration.

## 1. Product and inventory model

The catalog is split into layers:

- `Category`
- `Product`
- `ProductVariant`
- `Specification`
- `ProductImage`

Important implementation details:

- product slugs are auto-generated if not supplied
- variant SKU codes are auto-generated if not supplied
- product images are processed asynchronously after the DB transaction commits
- variants track both `stock_quantity` and `reserved_stock`

That split matters because orders and carts are built against product variants, not base products.

## 2. Session-first commerce flow

Sellaris is designed so a guest can start shopping immediately.

Guests can:

- receive a Django session automatically
- create a cart
- add cart items
- create wishlists
- create orders
- initialize payments

Later, when the guest registers or logs in, ownership is transferred to the new or existing user account.

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

This is one of the key production behaviors in Sellaris:

- stale cart prices do not survive checkout unchanged
- stale quantities can be corrected instead of hard-failing the entire order

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

## 8. Payment confirmation

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

## 9. When stock is finally deducted

Reserved stock is only converted into actual deduction after successful payment verification.

`confirm_stock()` does this by:

- decreasing `stock_quantity`
- decreasing `reserved_stock`
- writing an inventory log entry

This design separates:

- shopping intent
- order reservation
- confirmed payment

## 10. Expiry and cleanup rules

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

## 11. Current implementation caveats worth knowing

These are important if you are documenting or integrating the current code exactly as it exists.

### Pending-order expiry filters

The scheduled cleanup tasks filter expired orders using `"PENDING"` while the order model stores lowercase `pending`.

Intended business rule:

- release stale pending orders after 40 minutes
- delete stale guest pending orders after 48 hours

Current code caveat:

- those scheduled filters should be verified or corrected before relying on them in production

### Cart clearing after checkout or payment

The cart is intentionally not cleared during order creation.

Also note:

- the current codebase does not include a later success hook that clears the cart after payment confirmation

Frontend teams should not assume cart cleanup happens automatically.

### Inventory log read endpoint

The inventory log model contains rich audit fields, but the current response serializer is only a placeholder.

Treat that endpoint as internal/still maturing until the serializer is aligned with the model.

### Currency consistency

The codebase is multi-currency in the product and payment models, but currency propagation is not yet fully normalized end to end.

Before multi-currency production rollout, verify:

- order currency assignment
- payment currency assignment
- frontend display rules for mixed or default currencies

### Webhook URL registration

The payment webhook include is mounted without a trailing slash in the root URL config.

Before giving webhook URLs to payment providers, confirm the resolved deployed routes explicitly.

## 12. Why frontend teams care about this flow

A frontend or AI-generated UI needs this workflow detail to avoid wrong assumptions:

- cart totals can change at checkout
- stock reservation starts at order creation, not cart addition
- payment initialization can be reused
- ownership is session-based until login
- order and payment history are private to the current owner
- staff inventory APIs should never be exposed in shopper UIs
