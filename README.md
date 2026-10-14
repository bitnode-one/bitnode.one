# bitnode-site

One-pager for [bitnode.one](https://bitnode.one/). Brand system V1.3 "Open Signal". EN / DE, light / dark.

This folder is the single source of truth (SoT). Everything that ships is derived from files tracked here,
pinned by hash, built by one stdlib-only Python script. Same commit in, same bytes out.

## Quick start

```sh
python3 scripts/site.py validate   # check inputs, build, validate output
python3 scripts/site.py verify     # build twice, require identical digests
```

Windows: `py scripts\site.py validate`. No `make`, no Node, no Hugo, no pip install.

## Layout

| Path | Role | Edited by hand |
|---|---|---|
| `src/` | page source (`index.html` template, `favicon.svg`) | yes |
| `brand/v1.3.6/` | locked subset of brand package V1.3.6, unmodified | no, replace + relock |
| `static/` | byte-exact passthrough: `.well-known` (NIP-05, LNURL fallbacks), `media/` | yes, content |
| `vendor/fonts/` | self-hosted webfonts, hash-pinned | no, `fetch` |
| `licenses/` | third-party licenses (OFL) | no |
| `deps.lock.json` | every external input: path, sha256, source, license | on input change |
| `build.json` | declarative build plan, forbidden paths, contrast pairs | on pipeline change |
| `scripts/site.py` | fetch / check / build / validate / verify / release | rarely |
| `VERSION` | SemVer of the site | per release |
| `CHANGELOG.md` | what changed, per version | per change |
| `BACKLOG.md` | open work, prioritised | anytime |
| `docs/` | architecture, routing, decisions, `RELEASING.md`, brand PDF | on decision |
| `dist/` | build output, gitignored, disposable | never |

## Build output

```
dist/site/                         deployable static site
dist/bitnode-site-X.Y.Z.tar.gz     reproducible archive (sorted, fixed mtime/owner)
dist/SHA256SUMS                    per-file and archive hashes
dist/build-info.json               version, commit, SOURCE_DATE_EPOCH, tree hash
```

Timestamps come from the last commit (`git log -1 --format=%ct`), never the wall clock.
A dirty tree is marked `-dirty` in the commit id and `release` refuses it.

## Release

1. Change files. Add an entry under `## [Unreleased]` in `CHANGELOG.md`.
2. Bump `VERSION`, rename `[Unreleased]` to `[X.Y.Z] - YYYY-MM-DD`.
3. `git commit -am "release: vX.Y.Z"`
4. `python3 scripts/site.py release` → validates, verifies determinism, tags `vX.Y.Z`.
5. `git push --follow-tags`

## Hard rules

- `/lnurlp/*` belongs to the Cloudflare Worker → LNbits; the build fails if it appears in `dist/site`.
- `/.well-known/lnurlp/*` is Worker-first, Pages-fallback; `/.well-known/nostr.json` is Pages. Both live in
  `static/`, ship byte-identical and are JSON-validated. See `docs/ARCHITECTURE.md`.
- No runtime requests to third parties. Fonts and images are local. The validator fails on external loads.
- Brand files are never edited in place. New brand version = new `brand/vX.Y.Z/` + relock.
