# Releasing and publishing

Pipeline: push → `pages.yml` builds with `scripts/site.py`, validates, verifies determinism.
Only `main` (or a manual dispatch) deploys `dist/site` to GitHub Pages.

## One-time setup (first switch from Hugo)

1. GitHub → repo Settings → Pages → Source: **GitHub Actions** (already the case for the Hugo workflow).
2. Custom domain `bitnode.one` stays as set; tick **Enforce HTTPS** (see B-013 for `www`).
3. Merge the integration branch (below). The old `deploy.yml` is removed in the same commit, so two workflows never race.

## Regular release (Git)

```sh
git switch main && git pull --ff-only
git switch -c feat/<topic>
# edit src/ or static/; add a line under [Unreleased] in CHANGELOG.md
python3 scripts/site.py validate
git commit -am "feat: <topic>"
git push -u origin feat/<topic>          # CI validates, does not deploy
# open PR → CI green → merge to main     # CI deploys
# then cut the version:
git switch main && git pull --ff-only
# VERSION = X.Y.Z, CHANGELOG [Unreleased] -> [X.Y.Z] - YYYY-MM-DD
git commit -am "release: vX.Y.Z"
python3 scripts/site.py release           # validate + verify + tag vX.Y.Z
git push --follow-tags
```

## Quick fix (hotfix straight to main)

For a broken link, typo or a `.well-known` entry that must go live now.

```sh
git switch main && git pull --ff-only
# edit the file
python3 scripts/site.py validate          # never skip: it guards nostr.json and lnurlp JSON
git commit -am "fix: <what>"
git push                                  # deploys in ~1 min
```

Add the CHANGELOG line in the next regular release.

## Rollback

GitHub → Actions → `pages` → Run workflow → `ref` = last good tag, e.g. `v0.3.0`.
No revert commit needed to restore the site; fix forward afterwards.

## Verify after deploy

```sh
curl -sI https://bitnode.one/ | grep -i x-github-request-id
curl -s  https://bitnode.one/ | grep -o 'bitnode-site [0-9.]* ([0-9a-f]*)'
curl -s  "https://bitnode.one/.well-known/nostr.json?name=bitmax" | head -c 120
curl -s  https://bitnode.one/.well-known/lnurlp/bitmax   | grep -o lnbits.bitnode.one
curl -s  https://bitnode.one/.well-known/lnurlp/albihub  | grep -o getalby.com
```

The commit id in the page must equal `git rev-parse --short=12 HEAD` of the deployed ref.
