# Eleventy migration hardening notes

Generated during local prototype/hardening work on 2026-05-20 UTC.

## Backup

Current static blog backup before migration prototype work:

- `/home/ubuntu/.openclaw/workspace/tmp/blog-framework-migration/backups/20260520T231716Z`
- source HEAD: `02df661e396dbb47dc772abf05ccebf990803b3d`

## Hardening gates passed locally

- Eleventy build and Pagefind indexing pass.
- Existing 44 post slugs are emitted as top-level `*.html` files.
- Internal link checker: 905 HTML links checked after theme/nav/llms additions, 0 broken internal links; 44 sitemap locs, 0 broken.
- `feed.xml` parity with current feed: same 42 item links and zero parsed field mismatches after importing current feed metadata.
- `sitemap.xml` parity with current sitemap: same 44 loc entries and zero parsed field mismatches.
- Pagefind query spot checks worked for representative queries including OpenClaw memory search, Moltbook, GitHub Pages, gateway restart, and OAuth token.
- New-post smoke test (`eleventy-hardening-smoke-test.md`) generated index/feed/sitemap/search output correctly; test post was removed and `dist/` was clean-rebuilt.
- Chromium screenshots plus image review found no raw-HTML escaping issue in the Eleventy output.
- Modern theme pass added a responsive header, hero, post-card grid, article typography, and styled search page.
- Agent-friendly pass added `llms.txt`, RSS/sitemap links, semantic layout, stable `*.html` URLs, and server-rendered article content with Pagefind body scoping.
- The original Google site verification meta tag is preserved from `main:index.html`: `ldyJIS_0pM696yDpK1lNXgneHDhpHVJyXI4lBWb6ZP8`.
- Theme review panel follow-up added `404.html`, visible `:focus-visible` keyboard focus, `prefers-reduced-motion` guarded hover/smooth-scroll behavior, `-webkit-backdrop-filter` header fallback, and a no-JS fallback on the search page.

## Important design decision

Legacy imported posts are `.html` inputs, not `.md`, because raw HTML bodies inside Markdown caused invalid wrapping around block tags. New posts can still use Markdown.

## Known remaining work before publish

- Further tune visual design if the owner wants a different aesthetic direction.
- Add a GitHub Actions Pages deployment workflow only when ready to publish.
- Update the blog publishing protocol/scripts so new posts generate the required frontmatter and keep Moltbook teaser copy separate.
- Run a final live/staging verification before changing GitHub Pages source or publishing.
