# Decisions

Short ADR log. New decisions append; superseded ones stay, marked.

## D-001 — Folder is SoT, build is a pure function (2026-10-07)
Output depends only on tracked files, `VERSION`, commit id and commit time. Verified by `site.py verify`.
Reason: rebuild any tag years later, byte-identical. Don't trust, verify.

## D-002 — Python stdlib as the only build tool (2026-10-07)
Runs on Linux, WSL, macOS and Windows without install steps. No Node, no Hugo, no pip in the build path.
Rejected: Hugo (extra toolchain for a one-pager), Node (lockfile churn, supply chain surface).

## D-003 — Brand masters are immutable inputs (2026-10-07)
`brand/v1.3/` holds the package files unmodified. Derivatives (minify, dark recolor) are build steps.
Reason: the master stays auditable against the brand package; dark variant cannot drift.

## D-004 — Hosting integration open (2026-10-07)
Option A: plain static Pages, push `dist/site` via Actions. Option B: keep Hugo, place `dist/site/index.html`
as `layouts/index.html`. A is leaner and keeps D-002. Decide in B-001.

## D-005 — No third-party runtime loads (2026-10-07)
Fonts self-hosted, no CDN, no analytics. Enforced by the validator.

## D-006 — Language via `?lang=`, not separate paths, for now (2026-10-01)
Single file, no duplication. Revisit for SEO in B-008.

## D-004a — Hosting: plain static Pages via Actions (2026-10-14, resolves D-004)
Hugo, Tailwind CDN and Node are removed from the deploy path. `pages.yml` builds with `site.py` and deploys
`dist/site`. Reason: one toolchain, deterministic output, no third-party runtime script.

## D-007 — `static/` is a byte-exact passthrough (2026-10-14)
Lightning-address fallbacks and NIP-05 live in `static/` and are served by Pages behind the Worker.
They are content, not code: never minified, never normalized (`.gitattributes -text`), JSON-validated on build.
Supersedes the 0.2.0 rule that forbade `/.well-known/lnurlp` in the output — that rule would have broken
every address not hosted in LNbits.

## D-008 — Brand package is consumed as a locked subset (2026-10-14)
Only files the site ships are committed (`brand/v1.3.6/`), each hash-locked; the package zip hash is recorded
for provenance. Excalidraw, email and print assets stay in the brand package, not in the site repo.
