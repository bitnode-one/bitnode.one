# bitnode.one

One-pager for [bitnode.one](https://bitnode.one/), brand system V1.3.6, EN/DE, light/dark.
This repo is the single source of truth (SoT): same commit in, same bytes out.

## Setup

Requirements: `git` and `python3` ≥ 3.10. No Node, no Hugo, no pip.

```sh
git clone git@github.com:bitnode-one/bitnode.one.git && cd bitnode.one
python3 scripts/site.py validate    # check inputs, build, check output
python3 scripts/site.py verify      # build twice, hashes must match
```

Windows: `py scripts\site.py validate`. WSL: keep the repo under `~/`, not `/mnt/c`.
Output: `dist/site/` (not committed).

## Where things live

| Path | Content |
|---|---|
| `src/index.html` | page and EN/DE copy |
| `static/` | `.well-known` (NIP-05, LNURL fallbacks) and `media/`, shipped byte-identical |
| `brand/v1.3.6/` | logos, favicons, tokens; do not edit by hand |
| `VERSION`, `CHANGELOG.md`, `BACKLOG.md` | version, changes, open items |

## Release (regular)

```sh
git switch main && git pull --ff-only
git switch -c feat/<topic>
# edit, add a line under [Unreleased] in CHANGELOG.md
python3 scripts/site.py validate
git commit -am "feat: <topic>" && git push -u origin feat/<topic>
```

1. Open a PR → CI `pages / build` green → merge to `main` → automatic deploy with smoke test.
2. Set the version: bump `VERSION`, rename `[Unreleased]` → `[X.Y.Z] - YYYY-MM-DD` in `CHANGELOG.md`.
3. Tag:

```sh
git commit -am "release: vX.Y.Z" && git push
python3 scripts/site.py release && git push --follow-tags
```

## Quick fix

```sh
git switch main && git pull --ff-only
# edit the file
python3 scripts/site.py validate && git commit -am "fix: <what>" && git push
```

Pushing to `main` deploys immediately. Add the CHANGELOG line in the next release.

## Rollback

Actions → `pages` → Run workflow → `ref` = last good tag, e.g. `v0.4.1`.

## After deploy

The deploy job checks the live routes itself and fails if anything is missing. Manually:

```sh
curl -s https://bitnode.one/ | grep -o 'bitnode-site [0-9.]* ([0-9a-f]*)'
curl -s https://bitnode.one/.well-known/lnurlp/albihub | grep -o payRequest
curl -s https://bitnode.one/.well-known/nostr.json | head -c 80
```

## Hard rules

- `/lnurlp/*` belongs to the Worker → LNbits and must never appear in the build.
- `/.well-known/*` comes from `static/`. Never remove `include-hidden-files: true` from the workflow.
- No external requests at runtime. Fonts and images are local.

Details: [docs/RELEASING.md](docs/RELEASING.md) · [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) · [docs/DECISIONS.md](docs/DECISIONS.md)
