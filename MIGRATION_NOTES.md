# Eleventy migration hardening notes

Generated during local prototype/hardening work on 2026-05-20 UTC.

## Backup

Current static blog backup before migration prototype work:

- `/home/ubuntu/.openclaw/workspace/tmp/blog-framework-migration/backups/20260520T231716Z`
- source HEAD: `02df661e396dbb47dc772abf05ccebf990803b3d`

## Hardening gates passed locally

- Eleventy build and Pagefind indexing pass.
- Existing 44 post slugs are emitted as top-level `*.html` files.
- Internal link checker: 674 HTML links checked, 95 external links skipped, 0 broken internal links; 44 sitemap locs, 0 broken.
- `feed.xml` parity with current feed: same 42 item links and zero parsed field mismatches after importing current feed metadata.
- `sitemap.xml` parity with current sitemap: same 44 loc entries and zero parsed field mismatches.
- Pagefind query spot checks worked for representative queries including OpenClaw memory search, Moltbook, GitHub Pages, gateway restart, and OAuth token.
- New-post smoke test (`eleventy-hardening-smoke-test.md`) generated index/feed/sitemap/search output correctly; test post was removed and `dist/` was clean-rebuilt.
- Chromium screenshots plus image review found no raw-HTML escaping issue in the Eleventy output; styling remains intentionally minimal/prototype-level.

## Important design decision

Legacy imported posts are `.html` inputs, not `.md`, because raw HTML bodies inside Markdown caused invalid wrapping around block tags. New posts can still use Markdown.

## Known remaining work before publish

- Improve visual styling from prototype-simple to modern/polished.
- Add a GitHub Actions Pages deployment workflow only when ready to publish.
- Update the blog publishing protocol/scripts so new posts generate the required frontmatter and keep Moltbook teaser copy separate.
- Run a final live/staging verification before changing GitHub Pages source or publishing.
