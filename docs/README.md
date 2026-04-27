# Sellaris Docs Site

This folder contains the static documentation site for Sellaris.

## Source of truth

The docs UI now loads its content from the Markdown files under:

- `docs/docs/v1/`

The machine-readable API contract lives at:

- `docs/openapi/sellaris-v1.yaml`

That means the Markdown files and the OpenAPI file are the primary assets to update. The site simply renders them.

## File structure

```text
docs/
├── index.html
├── README.md
├── CNAME
├── css/
├── js/
├── openapi/
│   └── sellaris-v1.yaml
└── docs/
    └── v1/
        ├── intro.md
        ├── getting-started.md
        ├── authentication.md
        ├── api.md
        ├── whole-workflow.md
        └── faq.md
```

## How the docs UI works

- `index.html` defines the layout and sidebar
- `js/docs.js` fetches the Markdown files from `docs/docs/v1/`
- `marked.js` renders Markdown into HTML
- `highlight.js` styles code blocks

## Publishing notes

Before publishing publicly, make sure these are set correctly in `index.html`:

- canonical URL
- Open Graph URL
- social profile links
- favicon assets

## Deployment

This is a plain static site.

- GitHub Pages works well for it
- Netlify and Vercel will also serve it without a build step
