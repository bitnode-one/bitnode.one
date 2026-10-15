# Changelog

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versioning: [SemVer](https://semver.org/).
MAJOR = route/structure break, MINOR = visible content or design, PATCH = fixes without visible change.

## [Unreleased]

## [0.4.2] - 2026-10-15

### Changed
- Contact e-mail `mail@bitnode.one` → `hello@bitnode.one` (MX: SimpleLogin).
- Lightning address `bitmax@bitnode.one` → `bitnode@bitcash.one` (verified: payRequest, identifier matches).
- Section `02 / family` → `02 / agentic hub`; claim "One hub. One agentic constellation." /
  DE "Ein Hub. Eine agentische Konstellation."
- README rewritten as a short setup and release guide.

### Fixed
- Smoke test read `VERSION` in the deploy job (no checkout) and failed after a successful deploy; now matches the deployed commit id. Skipped on rollback dispatch.

## [0.4.1] - 2026-10-14

### Fixed
- Deploy dropped all dot-paths: `actions/upload-pages-artifact` excludes hidden files by default, so
  `/.well-known/nostr.json` and Pages-hosted `/.well-known/lnurlp/*` returned 404 after 0.3.0
  (2026-10-14 19:16–~19:45 UTC). Set `include-hidden-files: true`.
- Deploy job now runs a live smoke test (version, nostr.json, LNURL fallback and LNbits route) and fails loudly.

## [0.4.0] - 2026-10-14

### Changed
- bitcash.one status `planned` → `live`; logo, CTA "Open bitcash.one →" and footer entry link to https://bitcash.one/
  (verified HTTP 200, title "bitcash.one - Lightning Community Node").
- bitcash.one description EN/DE updated from "planned offering" to live community node.
- `bitcash.one` added to allowed external link hosts.

## [0.3.0] - 2026-10-14

### Added
- Brand package V1.3.6 subset in `brand/v1.3.6/` (logos, favicons, tokens), hash-locked; package zip hash recorded.
- Horizontal lockups for bitnode.one / bitcash.one / bitchat.one, light and dark, swapped by theme.
- Favicon set: `favicon.ico` (16–256), SVG, Apple Touch 180, Android 192/512, maskable 512, `site.webmanifest`.
- `static/` passthrough from the live Hugo repo, byte-identical: `/.well-known/nostr.json`,
  `/.well-known/lnurlp/*` (Pages fallback behind the Worker), `/media/*` voucher templates.
- Validator: passthrough presence + JSON shape (payRequest, 64-hex pubkeys), CSS colors must equal brand tokens,
  contrast computed from `design-tokens.json`, `og:image` target exists, confirmed-contacts allowlist.
- GitHub Pages workflow `pages.yml`: validate on every push/PR, deploy only from `main`, rollback via dispatch `ref`.
- `CNAME`, `.nojekyll` shipped.

### Changed
- Signal marks now from package V1.3.6 (light and dark masters); build-time recolor removed.
- Background raster is the V1.3.6 dot grid (`dot` token) instead of a line grid; `line` token aligned.
- Contacts from the live site: `mail@bitnode.one`, X `@bitnode_one`; Lightning `bitmax@bitnode.one` verified live.
- `theme-color` follows the manual theme toggle.
- Route rule corrected: `/.well-known/lnurlp/*` is Worker-first with Pages fallback, not Worker-only.
  Only `/lnurlp/*` stays forbidden in the build.
- Style guide PDF moved to `docs/brand/` (documentation, not a build input).

### Removed
- Hugo, Tailwind CDN, Node toolchain and committed `node_modules` from the deploy path.
- `brand/v1.3/` (superseded by v1.3.6), hand-made `src/favicon.svg`.

## [0.2.0] - 2026-10-07

### Added
- SoT control layer: `VERSION`, `deps.lock.json`, `build.json`, `scripts/site.py`, `Makefile`,
  `BACKLOG.md`, `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`, CI workflow (validate only).
- Deterministic build: sorted reproducible tarball, `SHA256SUMS`, `build-info.json`, `SOURCE_DATE_EPOCH` from git.
- Validation: input hashes, forbidden LNbits paths, external runtime loads, missing assets, dangling anchors,
  `alt` attributes, EN/DE key parity, WCAG contrast of V1.3 tokens, version/changelog consistency.
- Version visible in footer and `<meta name="generator">`.
- OFL license files for Space Grotesk and JetBrains Mono, shipped next to the fonts.

### Changed
- Hero uses the approved brand master `bitnode-mark-signal-light.svg` (Variante B) instead of the
  generated pixel scatter. Dark variant is derived at build time (`#171717` → `#F8F7F4`).
- b Core symbol and favicon use the exact master geometry.
- Acid band shows `b-signal-on-acid` and it is the provisional `og:image`.
- Repository layout: `src/` (hand-edited), `brand/` (masters), `vendor/` (pinned deps), `dist/` (output).

### Removed
- Client-side pixel generator script.

## [0.1.0] - 2026-10-01

### Added
- First one-pager per brand system V1.3: hero, vision/mission, three principles, brand family
  (bitnode.one / bitcash.one / bitchat.one), acid band, contact, footer.
- EN/DE switch (browser language default, `?lang=` override), light/dark (system default, manual toggle).
- Self-hosted Space Grotesk and JetBrains Mono. Tokens from V1.3 page 7.
- Pre-git reference state; not tagged.
