# Backlog

Priority: P0 blocks go-live, P1 before or right after go-live, P2 later.
Status: open / doing / blocked / done. Done items move to `CHANGELOG.md` with the release that ships them.

| ID | P | Status | Item | Done when |
|---|---|---|---|---|
| B-001 | P0 | done (0.3.0) | Integrate into `bitnode-one/bitnode.one` as plain static Pages (D-004 → A) | `pages.yml` deploys `dist/site` |
| B-002 | P0 | done (0.3.0) | Contacts confirmed from live site | no contact warnings |
| B-003 | P0 | done (0.3.0) | Brand package V1.3.6 assets | locked in `brand/v1.3.6/` |
| B-004 | P1 | done (0.3.0) | Favicon set + manifest | icons resolve |
| B-005 | P1 | open | Open Graph 1200×630 light/dark — not in package V1.3.6 | `og:image` is 1200×630 |
| B-006 | P1 | open | Persist theme choice (`localStorage`, preference only) | toggle survives reload |
| B-007 | P1 | open | Visual QA dark mode in a real browser | screenshot in `docs/qa/` |
| B-008 | P1 | open | `/de/` and `/en/` static paths for SEO instead of `?lang=` | hreflang → real URLs |
| B-013 | P1 | open | `https://www.bitnode.one/` HTTPS timed out on 2026-10-14 (HTTP 301 works). Check Pages custom-domain cert / "Enforce HTTPS" | `curl -I https://www.bitnode.one/` → 301 to apex |
| B-014 | P1 | open | Pages serves `/.well-known/lnurlp/*` as `application/octet-stream`; Worker could set `application/json` on fallback | header is JSON |
| B-015 | P1 | open | LNbits `bitmax` metadata says `text/identifier` = `bitmax@bitcash.one` while address is `@bitnode.one`; strict wallets may reject | identifier matches address |
| B-016 | P2 | open | Old live site had `tel:+18884623453` shown as `+1 (307) 453-2121` — mismatch, phone dropped from redesign | decide: add verified number or not |
| B-009 | P2 | open | Keyboard / screen reader pass | findings fixed |
| B-010 | P2 | open | Hero SVG 516 KB: compare AVIF/PNG fallback | decision in `DECISIONS.md` |
| B-011 | P2 | open | Branch protection on `main`: require `pages / build` check | setting on |
| B-012 | P2 | open | Record upstream font git tags in lock | lock has both |
| B-017 | P2 | open | Delete stale `gh-pages` branch after first successful Actions deploy | branch gone |
| B-018 | P2 | open | Fonts: optionally switch to package static woff2 (needs Mono Medium, missing in V1.3.6) | decision |
