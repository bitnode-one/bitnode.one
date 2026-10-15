# bitnode.one

One-Pager für [bitnode.one](https://bitnode.one/), Brand System V1.3.6, EN/DE, Light/Dark.
Dieses Repo ist die einzige Quelle der Wahrheit (SoT): gleicher Commit, gleiche Bytes.

## Setup

Voraussetzungen: `git` und `python3` ≥ 3.10. Kein Node, kein Hugo, kein pip.

```sh
git clone git@github.com:bitnode-one/bitnode.one.git && cd bitnode.one
python3 scripts/site.py validate    # Inputs prüfen, bauen, Output prüfen
python3 scripts/site.py verify      # zweimal bauen, Hashes müssen gleich sein
```

Windows: `py scripts\site.py validate`. WSL: Repo unter `~/`, nicht unter `/mnt/c`.
Ausgabe: `dist/site/` (wird nicht committet).

## Wo was liegt

| Pfad | Inhalt |
|---|---|
| `src/index.html` | Seite und Texte EN/DE |
| `static/` | `.well-known` (NIP-05, LNURL-Fallbacks) und `media/`, wird byte-genau ausgeliefert |
| `brand/v1.3.6/` | Logos, Favicons, Tokens, nicht von Hand ändern |
| `VERSION`, `CHANGELOG.md`, `BACKLOG.md` | Version, Änderungen, offene Punkte |

## Release (regulär)

```sh
git switch main && git pull --ff-only
git switch -c feat/<thema>
# ändern, Zeile unter [Unreleased] in CHANGELOG.md ergänzen
python3 scripts/site.py validate
git commit -am "feat: <thema>" && git push -u origin feat/<thema>
```

1. PR öffnen → CI `pages / build` grün → Merge nach `main` → automatischer Deploy mit Smoke-Test.
2. Version setzen: `VERSION` erhöhen, in `CHANGELOG.md` `[Unreleased]` → `[X.Y.Z] - YYYY-MM-DD`.
3. Taggen:

```sh
git commit -am "release: vX.Y.Z" && git push
python3 scripts/site.py release && git push --follow-tags
```

## Quick-Fix

```sh
git switch main && git pull --ff-only
# Datei ändern
python3 scripts/site.py validate && git commit -am "fix: <was>" && git push
```

Auf `main` wird sofort deployt. CHANGELOG-Zeile im nächsten Release nachtragen.

## Rollback

Actions → `pages` → Run workflow → `ref` = letzter guter Tag, z. B. `v0.4.1`.

## Nach dem Deploy

Der Deploy-Job prüft die Live-Routen selbst und wird rot, wenn etwas fehlt. Manuell:

```sh
curl -s https://bitnode.one/ | grep -o 'bitnode-site [0-9.]* ([0-9a-f]*)'
curl -s https://bitnode.one/.well-known/lnurlp/albihub | grep -o payRequest
curl -s https://bitnode.one/.well-known/nostr.json | head -c 80
```

## Harte Regeln

- `/lnurlp/*` gehört dem Worker → LNbits und darf nie im Build landen.
- `/.well-known/*` kommt aus `static/`. `include-hidden-files: true` im Workflow nie entfernen.
- Keine externen Requests zur Laufzeit. Fonts und Bilder sind lokal.

Details: [docs/RELEASING.md](docs/RELEASING.md) · [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) · [docs/DECISIONS.md](docs/DECISIONS.md)
