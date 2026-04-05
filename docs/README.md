# Sellaris — Website Source

This is the static website for the Sellaris Django E-Commerce Engine.

## File Structure

```
sellaris/
├── index.html          ← Main HTML (markup only — no inline styles or scripts)
│
├── css/
│   ├── base.css        ← Design tokens, reset, typography, layout utilities, buttons
│   ├── nav-footer.css  ← Navigation bar + footer styles
│   ├── sections.css    ← All main section styles (hero, features, api, arch, etc.)
│   └── docs.css        ← Documentation section styles
│
├── js/
│   ├── main.js         ← Sitewide JS (nav, mobile menu, scroll, copy buttons)
│   └── docs.js         ← Docs section JS (markdown rendering, page switching)
│
├── assets/             ← (create this folder) Images, logo, favicon
│   ├── logo.svg            ← Your Sellaris logo (30×30px, works on white bg)
│   ├── logo-white.svg      ← Logo version for dark footer
│   ├── favicon.svg         ← Browser tab icon
│   └── favicon.png         ← Fallback favicon
│
└── README.md           ← This file
```

## Customisation Checklist

Before publishing, complete these TODOs (each is marked in the code with a `TODO:` comment):

1. **Logo** — Replace the `<span class="logo-mark">S</span>` placeholder with your SVG logo
   in `index.html` (nav logo and footer logo). Use 30×30px SVG.
   Tools: [Figma](https://figma.com) | [Vectr](https://vectr.com) | [Iconify](https://iconify.design)

2. **Favicon** — Create an `assets/` folder, add your favicon files, and uncomment the
   favicon `<link>` tags in the `<head>` of `index.html`.
   Generator: [favicon.io](https://favicon.io) or [realfavicongenerator.net](https://realfavicongenerator.net)

3. **Canonical URL** — Replace `https://sellaris.dev` with your real deployed URL in
   the `<link rel="canonical">` and `<meta property="og:url">` tags.

4. **Social URLs** — In the footer section of `index.html`, replace the `href="#"` on
   the Twitter and LinkedIn social icons with your actual profile URLs.

5. **GitHub raw docs (once repo is public)** — Open `js/docs.js`, uncomment the
   `GITHUB_RAW_BASE` block, and comment out the inline `DOCS` object. This makes
   the docs section fetch live markdown from your `/docs` GitHub folder.

## Deployment

This is a plain static site — no build step required.

**GitHub Pages (free):**
1. Push this folder to a GitHub repo
2. Settings → Pages → Deploy from branch → `main` / `root`

**Netlify (free):**
1. Drag the `sellaris/` folder onto [netlify.com/drop](https://netlify.com/drop)

**Vercel:**
```bash
npx vercel --prod
```

## Dependencies (loaded via CDN)

| Library        | Purpose                                      |
|----------------|----------------------------------------------|
| Feather Icons  | SVG icon set (nav, cards, footer, buttons)   |
| Marked.js      | Renders markdown strings to HTML in the docs |
| highlight.js   | Syntax highlighting in docs code blocks      |
| Google Fonts   | Syne (display) + DM Mono (code) + Inter (body) |

No npm, no build tool, no bundler needed.
