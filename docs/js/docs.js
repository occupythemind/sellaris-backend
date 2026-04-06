/* ============================================================
   docs.js — Documentation section JavaScript
   Handles: rendering markdown pages, sidebar navigation,
            GitHub fetch (commented out, ready for when repo is public).
============================================================ */

/* ----------------------------------------------------------
   DOC PAGES
   Each page is a markdown string keyed by its page ID.
   These match the IDs used in the sidebar nav items
   (data-doc attribute).

   TO LOAD FROM GITHUB instead:
   1. Make your repo public.
   2. Create a /docs/ folder in the repo with .md files.
   3. Uncomment the GITHUB_RAW_BASE block below and comment
      out the inline DOCS object.
   The fetch() version is already written — just swap.
---------------------------------------------------------- */
const DOCS = {

  overview: `
# Sellaris — Overview

Sellaris is a **Django REST Framework** e-commerce backend designed to serve as the
engine powering any commerce service. It is modular, API-first, and production-oriented.

## What is it?

Sellaris handles all the server-side complexity of an online store:

- Product catalogue management
- Shopping cart and wishlist logic
- Order lifecycle management
- Payment processing hooks
- User authentication and authorisation

It exposes a clean REST API so any frontend — React, Vue, mobile apps, or
third-party storefronts — can consume it without caring about the underlying Django code.

## Who is it for?

- Developers building e-commerce products who want a solid, extensible backend
- Teams who want to ship quickly without reinventing cart and order logic
- Engineers who need a Django backend they can deploy with one Docker command

## Tech Stack

| Layer             | Technology                     |
|-------------------|--------------------------------|
| Framework         | Django + Django REST Framework |
| Database          | PostgreSQL                     |
| Containerisation  | Docker + Docker Compose        |
| Async (planned)   | Celery + Redis                 |
| License           | MIT                            |

## Project Status

> 🚧 Actively under development. Core commerce modules are functional.
> Auth, payment integration, and async features are in progress.
  `,

  setup: `
# Setup & Installation

## Prerequisites

- [Docker](https://www.docker.com/get-started) installed
- [Docker Compose](https://docs.docker.com/compose/) (bundled with Docker Desktop)

No local Python environment needed.

## 1. Clone the repository

\`\`\`bash
git clone https://github.com/occupythemind/sellaris-backend.git
cd sellaris-backend
\`\`\`

## 2. Create your environment file

Create a \`.env\` file in the project root:

\`\`\`bash
DEBUG=True
SECRET_KEY=your-secret-key

# Docker database settings
DB_NAME=ecommerce_db
DB_USER=ecommerce_user
DB_PASSWORD=yourpassword
DB_HOST=db
DB_PORT=5432

# Django DATABASE_URL
DATABASE_URL=postgresql://DB_USER:DB_PASSWORD@DB_HOST:DB_PORT/DB_NAME
\`\`\`

## 3. Start the stack

\`\`\`bash
docker compose --env-file .env -f docker/docker-compose.yml up --build
\`\`\`

Django will be available at \`http://localhost:8000\`.

## 4. Verify

\`\`\`bash
curl http://localhost:8000/api/v1/products/
\`\`\`

You should receive a JSON response from the API.
  `,

  'api-ref': `
# API Reference

All endpoints are versioned under \`/api/v1/\` and return JSON.

## Authentication

Token-based authentication. Include the token in the request header:

\`\`\`
Authorization: Token <your-token>
\`\`\`

## Products

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | \`/api/v1/products/\`      | List all products |
| POST   | \`/api/v1/products/\`      | Create a product |
| GET    | \`/api/v1/products/{id}/\` | Retrieve a product |
| PUT    | \`/api/v1/products/{id}/\` | Update a product |
| DELETE | \`/api/v1/products/{id}/\` | Delete a product |

## Cart

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | \`/api/v1/carts/\`      | Get current cart |
| POST   | \`/api/v1/carts/\`      | Add item to cart |
| PUT    | \`/api/v1/carts/{id}/\` | Update cart item |
| DELETE | \`/api/v1/carts/{id}/\` | Remove cart item |

## Orders

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET  | \`/api/v1/orders/\`      | List user orders |
| POST | \`/api/v1/orders/\`      | Create an order |
| GET  | \`/api/v1/orders/{id}/\` | Get order details |

## Payments

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | \`/api/v1/payments/\` | Initiate a payment |

## Wishlists

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | \`/api/v1/wishlists/\`      | Get wishlist |
| POST   | \`/api/v1/wishlists/\`      | Add to wishlist |
| DELETE | \`/api/v1/wishlists/{id}/\` | Remove from wishlist |

> ⚠️ Actively in development. More endpoints coming.
  `,

  architecture: `
# Architecture

## Directory Structure

\`\`\`
sellaris-backend/
├── apps/
│   ├── users/
│   ├── products/
│   ├── cart/
│   ├── orders/
│   ├── payments/
│   └── notifications/
├── core/          ← Shared utilities
├── services/      ← Business logic layer
├── tasks/         ← Background jobs (Celery-ready)
├── config/        ← Django settings
└── docker/        ← Docker Compose config
\`\`\`

## Layer Responsibilities

### \`apps/\` — Domain Modules
Each app owns its models, serializers, views, and URL routes.
Apps are independent — removing one doesn't break others.

### \`services/\` — Business Logic
Business rules live here, not in views. This keeps API handlers thin
and logic reusable and testable in isolation.

### \`core/\` — Shared Utilities
Custom exceptions, base serializers, pagination classes, and shared
permissions — defined once, used everywhere.

### \`tasks/\` — Background Jobs
Celery-ready task definitions. Async processing (emails, notifications)
plugs in here with Redis as the message broker.

## Design Principles

- **API-first**: No server-side rendering. Pure REST + JSON.
- **Decoupled**: Frontend and backend are fully independent.
- **Modular**: Add or replace domains without system-wide impact.
- **Microservices-ready**: Decoupling today makes service extraction easier later.
  `,

  env: `
# Environment Variables

Create a \`.env\` file in the project root. Never commit this file to version control.

## Variables

| Variable       | Example           | Description |
|----------------|-------------------|-------------|
| \`DEBUG\`        | \`True\`            | Enable debug mode (\`False\` in production) |
| \`SECRET_KEY\`   | \`your-secret-key\` | Django secret key — use a strong random string |
| \`DB_NAME\`      | \`ecommerce_db\`    | PostgreSQL database name |
| \`DB_USER\`      | \`ecommerce_user\`  | PostgreSQL username |
| \`DB_PASSWORD\`  | \`yourpassword\`    | PostgreSQL password |
| \`DB_HOST\`      | \`db\`              | DB host (\`db\` in Docker, \`localhost\` outside) |
| \`DB_PORT\`      | \`5432\`            | PostgreSQL port |
| \`DATABASE_URL\` | See below          | Full connection string |

## DATABASE_URL Format

\`\`\`
DATABASE_URL=postgresql://DB_USER:DB_PASSWORD@DB_HOST:DB_PORT/DB_NAME
\`\`\`

## Generating a SECRET_KEY

\`\`\`bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
\`\`\`

## Production Notes

- Always set \`DEBUG=False\` in production
- Use a secrets manager (AWS Secrets Manager, Doppler, etc.) rather than a plain \`.env\`
- Rotate your \`SECRET_KEY\` if it's ever exposed
  `,

  contributing: `
# Contributing

Sellaris is open-source and welcomes contributions.

## How to Contribute

1. **Fork** the repository on GitHub
2. **Clone** your fork locally
3. **Create a branch**: \`git checkout -b feature/your-feature-name\`
4. **Make your changes** with clear, descriptive commits
5. **Push** to your fork: \`git push origin feature/your-feature-name\`
6. **Open a Pull Request** against the \`main\` branch

## What to Work On

- Check the [open issues](https://github.com/occupythemind/sellaris-backend/issues)
- Look for issues labelled \`good first issue\` or \`help wanted\`
- Or open a new issue to propose a feature or report a bug

## Code Style

- Follow PEP 8 for Python code
- Write tests for new features
- Keep commits atomic — one logical change per commit

## Feedback

Suggestions, bug reports, and ideas are all welcome.
Open an issue or start a discussion on GitHub.

> Maintainer: **David Akaluzia** — *"Building safer, secure & reliable systems."*
  `
};


/* ----------------------------------------------------------
   GITHUB RAW FETCH (uncomment when repo is public)
   Replace the DOCS object above with this block, and create
   matching .md files in your repo's /docs/ directory.

const GITHUB_RAW_BASE =
  'https://raw.githubusercontent.com/occupythemind/sellaris-backend/main/docs';

const DOC_FILES = {
  overview:     `${GITHUB_RAW_BASE}/overview.md`,
  setup:        `${GITHUB_RAW_BASE}/setup.md`,
  'api-ref':    `${GITHUB_RAW_BASE}/api-reference.md`,
  architecture: `${GITHUB_RAW_BASE}/architecture.md`,
  env:          `${GITHUB_RAW_BASE}/environment.md`,
  contributing: 'https://raw.githubusercontent.com/occupythemind/sellaris-backend/main/CONTRIBUTING.md',
};
---------------------------------------------------------- */


/* ----------------------------------------------------------
   loadDoc(pageId)
   Renders a documentation page by its ID.
   Called by clicking a .docs-nav-item.
---------------------------------------------------------- */
window.loadDoc = function (pageId, clickedEl) {
  const docsBody = document.getElementById('docsBody');
  if (!docsBody) return;

  // Update sidebar active state
  document.querySelectorAll('.docs-nav-item').forEach(el => {
    el.classList.remove('active');
  });
  if (clickedEl) clickedEl.classList.add('active');

  // Show loading spinner
  docsBody.innerHTML = `
    <div class="docs-loading">
      <div class="spinner"></div>
      Loading…
    </div>`;

  /* ---- INLINE VERSION ---- */
  const md = DOCS[pageId];
  if (md && typeof marked !== 'undefined') {
    // Short delay so the spinner is visible (feels less jarring)
    setTimeout(() => {
      docsBody.innerHTML = marked.parse(md);
      // Apply syntax highlighting to code blocks if hljs is loaded
      if (typeof hljs !== 'undefined') {
        docsBody.querySelectorAll('pre code').forEach(block => {
          hljs.highlightElement(block);
        });
      }
    }, 160);
  } else {
    docsBody.innerHTML = '<p style="color:var(--text-muted);padding:24px 0;">Page not found.</p>';
  }

  /*
  ---- GITHUB FETCH VERSION (uncomment when repo is public) ----
  const url = DOC_FILES[pageId];
  if (!url) return;
  fetch(url)
    .then(res => {
      if (!res.ok) throw new Error('Not found');
      return res.text();
    })
    .then(md => {
      docsBody.innerHTML = marked.parse(md);
      if (typeof hljs !== 'undefined') {
        docsBody.querySelectorAll('pre code').forEach(b => hljs.highlightElement(b));
      }
    })
    .catch(() => {
      docsBody.innerHTML =
        '<p style="color:var(--text-muted)">Could not load this page. Make sure the repo is public and the file exists.</p>';
    });
  */
};


/* ----------------------------------------------------------
   Render the default page (overview) on load.
---------------------------------------------------------- */
document.addEventListener('DOMContentLoaded', () => {
  const docsBody = document.getElementById('docsBody');
  if (!docsBody) return;

  if (typeof marked !== 'undefined') {
    docsBody.innerHTML = marked.parse(DOCS['overview']);
    if (typeof hljs !== 'undefined') {
      docsBody.querySelectorAll('pre code').forEach(b => hljs.highlightElement(b));
    }
  }

  // Mark the first sidebar item as active
  const firstItem = document.querySelector('.docs-nav-item');
  if (firstItem) firstItem.classList.add('active');
});
