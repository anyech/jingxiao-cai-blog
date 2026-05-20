# Jingxiao Cai's Blog — Eleventy migration branch

This branch stages the blog migration from hand-maintained static HTML to Eleventy.

## Current migration shape

- Legacy posts are imported as `src/posts/*.html` with YAML frontmatter, preserving existing body HTML without Markdown wrapping/escaping regressions.
- New posts can be authored as `src/posts/*.md` with the same frontmatter shape.
- Public post URLs remain top-level `*.html` files.
- `feed.xml`, `sitemap.xml`, `index.html`, `search.html`, `robots.txt`, and Pagefind assets are generated at build time.
- Pagefind remains static-only; no server component is required.

## Local commands

```bash
npm install
npm run build
npm run pagefind
npm run verify
```

Build output goes to `dist/` and is intentionally not committed.

## Deployment note

This branch does not change GitHub Pages settings or publish anything by itself. A later reviewed deployment step should switch Pages to a GitHub Actions artifact workflow only after parity checks are accepted.
