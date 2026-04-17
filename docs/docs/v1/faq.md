# FAQ

## Is Sellaris a public storefront backend or an admin backend?

Both. The same backend serves shopper flows and staff operations, but they are not all equally exposed.

- shopper flows are mostly public or session-based
- catalog write operations are staff-only
- inventory mutation is staff-only
- inventory audit is staff/staff-admin only

## Does the API use JWT or bearer tokens?

No. The current implementation uses Django sessions.

If you are building a frontend:

- keep cookies enabled
- keep the guest session alive until login or registration completes
- handle CSRF on unsafe requests

## Can guests shop before creating an account?

Yes.

Guests can:

- browse products
- maintain a cart
- maintain wishlists
- create an order
- initialize payment

Later, login or registration transfers guest ownership to the user account.

## What happens when a guest logs in after shopping?

The backend transfers:

- wishlists
- cart ownership, with cart merge logic if the user already has a cart
- pending orders

This is implemented in `apps/users/services/transfer_ownership.py`.

## When is stock actually reserved?

At checkout, not at cart add time.

That means:

- the cart is not a stock guarantee
- checkout revalidates stock in real time
- stock can be adjusted before order creation if availability changed

## When is stock finally deducted?

After payment success is confirmed by a verified webhook flow.

Before that, the stock sits in `reserved_stock`.

## How long does an order last before it expires?

The intended business rule in the code is:

- a pending order reservation should expire after 40 minutes

That release job is scheduled every 5 minutes.

Important caveat:

- the current cleanup query uses uppercase `"PENDING"` while the model stores lowercase `pending`
- verify or fix that before relying on automated reservation release in production

## How long are guest artifacts retained?

Current scheduled cleanup rules:

- guest carts: 14 days
- guest wishlists: 30 days
- guest pending orders: intended 48 hours

Again, confirm the pending-order filter because of the status-case mismatch noted above.

## How long does email verification last?

24 hours, based on the configured `PASSWORD_RESET_TIMEOUT`.

## How long before a deleted account is removed permanently?

30 days after soft deletion, unless the user logs back in before the deletion task executes.

## Are orders cleared from the cart automatically?

Not today.

- the order creation flow explicitly does not clear the cart
- the current code also does not clear it later on payment success

Frontend teams should decide how to present this state to users.

## Which endpoints should never be exposed in a shopper UI?

- all product create/update/delete endpoints
- all inventory stock mutation endpoints
- inventory log audit endpoint

Those belong in an admin or staff interface.

## What is the best input for another AI agent to generate a frontend?

Use:

1. `docs/openapi/sellaris-v1.yaml`
2. `docs/docs/v1/api.md`
3. `docs/docs/v1/authentication.md`
4. `docs/docs/v1/whole-workflow.md`

That combination gives the agent:

- exact schemas
- endpoint URLs
- access rules
- ownership rules
- business logic constraints

## Are the route names in the docs exact?

Yes, the docs follow the current URL registration structure, including repeated segments such as:

- `/api/v1/products/products`
- `/api/v1/carts/cart-items`
- `/api/v1/wishlists/wishlists`

Those are intentional in this documentation because they reflect the current router setup, not a prettier hypothetical API.
