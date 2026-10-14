# Architecture

## Route ownership on bitnode.one

Cloudflare proxies `bitnode.one`. A Worker sits in front; everything it does not answer falls through to GitHub Pages.

| URL | First responder | Fallback | Source of truth |
|---|---|---|---|
| `/` , `www.` | GitHub Pages | — | this repo, `dist/site` |
| `/.well-known/lnurlp/<name>` (name in LNbits) | Worker → Pangolin → LNbits | — | LNbits |
| `/.well-known/lnurlp/<name>` (name not in LNbits) | Worker passes through | GitHub Pages static file | this repo, `static/.well-known/lnurlp/` |
| `/.well-known/nostr.json` | GitHub Pages | — | this repo, `static/.well-known/nostr.json` |
| `/lnurlp/*` | Worker → LNbits | — | LNbits; forbidden in build |
| `/media/*` | GitHub Pages | — | this repo, `static/media/` |

Observed 2026-10-14: `bitmax` → LNbits callback; `albihub` → static file (getalby callback, served by GitHub);
`nostr.json` → GitHub. The build therefore ships `static/` byte-identical and validates it; only `/lnurlp` is forbidden.

To move a name to LNbits: create it in LNbits, verify the Worker answers, then delete the static file in a release.

## Build pipeline

```
src/index.html ──template(VERSION, COMMIT)──┐
src/favicon.svg ──copy──────────────────────┤
vendor/fonts/* ──copy (hash-locked)─────────┤
licenses/OFL-* ──copy───────────────────────┼──> dist/site ──> tar.gz + SHA256SUMS + build-info.json
brand/v1.3.6/** ──copy_tree (hash-locked)──┤
static/** ──copy_tree (byte-identical)───┘
```

Inputs: files in git + `VERSION` + commit id + commit time. No network, no clock, no environment variables.
`fetch` is the only command that touches the network, and it refuses bytes that do not match the lock.

## Dependencies

| Dependency | Kind | Pin |
|---|---|---|
| Python ≥ 3.10 | build tool | stdlib only |
| git | identity, epoch, tags | any ≥ 2.30 |
| Space Grotesk | webfont, OFL-1.1 | sha256 in `deps.lock.json` |
| JetBrains Mono | webfont, OFL-1.1 | sha256 in `deps.lock.json` |
| Brand package V1.3.6 subset | logos, favicons, tokens | sha256 per file + package zip hash |
| actions/checkout, upload-pages-artifact, deploy-pages | CI only | commit SHA in workflow |

The runtime page has zero third-party requests and zero JS dependencies.
