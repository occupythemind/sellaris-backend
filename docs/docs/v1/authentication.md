# Authentication, Sessions, and Access Control

## Current auth style

Sellaris currently authenticates users with Django sessions.

What that means in practice:

- `POST /api/v1/users/login` calls Django `login(request, user)`
- the backend sets a session cookie
- authenticated requests depend on that cookie
- guest flows still work because carts, wishlists, orders, and payment records can be session-owned

This is not a JWT or bearer-token API at the moment.

For the broader endpoint map, see the [API guide](./api.md).

## Browser client requirements

If you are building a SPA or server-rendered frontend:

- preserve cookies on requests
- include CSRF protection on unsafe requests that send cookies
- do not discard the guest session before registration or login if you want cart transfer to work

The settings now explicitly configure:

- `CORS_ALLOW_CREDENTIALS = True`
- readable CSRF cookie behavior in development
- secure cross-site cookie settings in production

## CSRF note

The project enables Django `CsrfViewMiddleware`, but the current source does not expose a dedicated CSRF bootstrap endpoint.

That means frontend clients should plan around standard Django CSRF behavior:

- send `credentials: 'include'`
- capture the CSRF cookie when available
- send it back as `X-CSRFToken` on unsafe requests that use cookies

## Registration and verification flow

1. `POST /api/v1/users/register`
2. the backend creates the user
3. the backend queues `send_verification_email_task`
4. guest-owned data is transferred to the new account
5. the user verifies email through `GET /api/v1/users/verify-email?uid=...&token=...`

Important business rule:

- the verification token uses Django `PasswordResetTokenGenerator`
- `PASSWORD_RESET_TIMEOUT` is configured to 24 hours
- verification links should therefore be treated as expiring after 24 hours

## Dynamic verification URL behavior

Recent code now builds verification links dynamically:

- `FRONTEND_BASE_URL` is used if present
- otherwise the request scheme and validated host are used
- `VERIFY_EMAIL_PATH` is appended to produce the final frontend verification route

This is useful for staging and production environments that sit behind different domains or proxies.

## Login flow

`POST /api/v1/users/login`

Login behavior:

- rejects invalid credentials with `401`
- rejects unverified accounts with `403`
- reactivates a soft-deleted account if it logs in again before final deletion
- transfers guest cart, wishlist, and pending orders to the authenticated account

The response body is simple:

- `{"message": "Login successful"}`

The actual auth state is established by the session cookie.

## OAuth flows

Supported providers:

- Google
- Facebook
- Apple

All three endpoints:

- accept a provider token in the request body
- validate the provider token
- create or link a user
- create a Django session
- transfer guest-owned data into the user account

Apple-specific nuance:

- Apple may omit email on later logins
- the backend falls back to an existing `UserAuthProvider` link if the provider user ID is already known

## Authenticated user endpoints

These require a valid logged-in session:

- `GET /api/v1/users/account-info`
- `PATCH /api/v1/users/manage-account`
- `POST /api/v1/users/delete`

## Soft deletion behavior

Account deletion is not immediate.

`POST /api/v1/users/delete`:

- validates the submitted password
- sets `is_active=False`
- logs the user out
- schedules final deletion 30 days later with Celery

If the same user logs back in before the 30-day task executes:

- the account is reactivated
- `deletion_scheduled_at` is cleared in the login view logic

## Public vs protected API surface

### Public endpoints

- all catalog read endpoints
- cart and wishlist flows
- checkout
- payment initialization
- register, login, verify email, resend verification
- OAuth login endpoints

### Session-authenticated endpoints

- account info and account management
- own order reads
- own payment record reads

### Staff-only endpoints

- all catalog writes
- all inventory write endpoints

### Staff audit endpoint

- inventory log reads

## Permission classes used in code

- `IsStaffOrReadOnly`: public reads, staff-only writes
- `IsStaffUser`: staff-only access
- `IsAdminUser`: used on inventory log, but effectively still `is_staff=True`

## Ownership model for shopper data

The backend never exposes arbitrary carts, wishlists, orders, or payments.

Ownership is enforced by:

- authenticated user match, or
- active session key match

That applies to:

- carts
- cart items
- wishlists
- wishlist items
- orders
- payment record list

## Guest data transfer on login or registration

When a guest becomes an authenticated user, the backend:

- transfers wishlists from `session_id` to `user`
- merges the guest cart into the user cart, combining quantities for matching variants
- transfers pending guest orders to the user

This is one of the project’s most valuable UX features and should be preserved in any future auth redesign.

## Related documents

- [Overview](./intro.md)
- [Getting started](./getting-started.md)
- [API guide](./api.md)
- [System workflow](./whole-workflow.md)
