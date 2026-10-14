#!/usr/bin/env python3
"""bitnode-site control tool. Python stdlib only; runs identically on Linux, WSL, macOS, Windows.

    python scripts/site.py fetch      restore vendor/ from deps.lock.json sources (hash-verified)
    python scripts/site.py check      verify every locked input against its sha256
    python scripts/site.py build      deterministic build -> dist/site, dist/*.tar.gz, SHA256SUMS
    python scripts/site.py validate   check + build + validate output
    python scripts/site.py verify     build twice in clean temp dirs, require identical digests
    python scripts/site.py release    validate + verify + clean tree + changelog entry -> git tag vX.Y.Z

Exit code 0 = pass, 1 = failure. Idempotent: every command can be rerun without side effects
beyond regenerating dist/.
"""
from __future__ import annotations

import gzip
import hashlib
import io
import json
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?$")


# ---------- helpers ----------
def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load(name: str) -> dict:
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def git(*args: str) -> str | None:
    try:
        return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True,
                              check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def version() -> str:
    v = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if not SEMVER.match(v):
        die(f"VERSION '{v}' is not SemVer")
    return v


def build_identity() -> tuple[str, int]:
    """Commit id and SOURCE_DATE_EPOCH. Both derive from git, never from the clock."""
    commit = git("rev-parse", "--short=12", "HEAD") or "nogit"
    epoch = int(git("log", "-1", "--format=%ct") or 0)
    if commit != "nogit" and git("status", "--porcelain", "--untracked-files=no"):
        commit += "-dirty"
    return commit, epoch


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def err(self, m: str) -> None:
        self.errors.append(m)

    def warn(self, m: str) -> None:
        self.warnings.append(m)

    def done(self, title: str) -> None:
        for w in self.warnings:
            print(f"  WARN  {w}")
        for e in self.errors:
            print(f"  FAIL  {e}")
        status = "FAIL" if self.errors else "PASS"
        print(f"[{status}] {title}: {len(self.errors)} error(s), {len(self.warnings)} warning(s)")
        if self.errors:
            sys.exit(1)


def die(msg: str) -> None:
    print(f"[FAIL] {msg}")
    sys.exit(1)


# ---------- fetch / check ----------
def cmd_check() -> None:
    r = Report()
    for i in load("deps.lock.json")["inputs"]:
        p = ROOT / i["path"]
        if not p.is_file():
            r.err(f"missing input {i['path']} (run: fetch)")
        elif sha256(p) != i["sha256"]:
            r.err(f"hash mismatch {i['path']}")
        lf = i.get("license_file")
        if lf and not (ROOT / lf).is_file():
            r.err(f"missing license file {lf}")
    r.done("inputs match deps.lock.json")


def cmd_fetch() -> None:
    for i in load("deps.lock.json")["inputs"]:
        p = ROOT / i["path"]
        if p.is_file() and sha256(p) == i["sha256"]:
            continue
        if not i["source"].startswith("https://"):
            die(f"{i['path']} has no fetchable source; restore it from the brand package")
        data = urllib.request.urlopen(i["source"], timeout=30).read()
        if hashlib.sha256(data).hexdigest() != i["sha256"]:
            die(f"upstream changed for {i['path']}; refusing to write")
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
        print(f"  fetched {i['path']}")
    print("[PASS] fetch")


# ---------- build ----------
def svg_min(text: str, recolor: dict | None, retitle: str | None) -> str:
    text = re.sub(r"<\?xml[^>]*\?>", "", text)
    text = re.sub(r">\s+<", "><", text).strip()
    for a, b in (recolor or {}).items():
        text = text.replace(a, b)
    if retitle:
        text = re.sub(r"<title>.*?</title>", f"<title>{retitle}</title>", text, count=1)
    return text + "\n"


def build(out_root: Path) -> dict:
    plan = load("build.json")
    v = version()
    commit, epoch = build_identity()
    site = out_root / "site"
    if out_root.exists():
        shutil.rmtree(out_root)
    site.mkdir(parents=True)

    for s in plan["steps"]:
        src, dst = ROOT / s["from"], site / s["to"]
        dst.parent.mkdir(parents=True, exist_ok=True)
        if s["op"] == "copy":
            dst.write_bytes(src.read_bytes())
        elif s["op"] == "template":
            t = src.read_text(encoding="utf-8").replace("{{VERSION}}", v).replace("{{COMMIT}}", commit)
            dst.write_bytes(t.encode("utf-8"))
        elif s["op"] == "copy_tree":
            excl = set(s.get("exclude", []))
            for f in sorted(x for x in src.rglob("*") if x.is_file()):
                rel = f.relative_to(src)
                if rel.as_posix() in excl:
                    continue
                t = (site / s["to"] / rel)
                if t.exists():
                    die(f"copy_tree collision: {t.relative_to(site)}")
                t.parent.mkdir(parents=True, exist_ok=True)
                t.write_bytes(f.read_bytes())
        elif s["op"] == "svg_min":
            dst.write_bytes(svg_min(src.read_text(encoding="utf-8"), s.get("recolor"),
                                    s.get("retitle")).encode("utf-8"))
        else:
            die(f"unknown op {s['op']}")

    files = sorted(p for p in site.rglob("*") if p.is_file())
    manifest = {p.relative_to(site).as_posix(): sha256(p) for p in files}
    tree = hashlib.sha256("".join(f"{h}  {n}\n" for n, h in manifest.items()).encode()).hexdigest()

    # deterministic tarball: sorted entries, fixed mtime/owner/mode, gzip header mtime fixed
    name = f"bitnode-site-{v}"
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w", format=tarfile.PAX_FORMAT) as tar:
        for p in files:
            ti = tarfile.TarInfo(f"{name}/{p.relative_to(site).as_posix()}")
            data = p.read_bytes()
            ti.size, ti.mtime, ti.mode = len(data), epoch, 0o644
            ti.uid = ti.gid = 0
            ti.uname = ti.gname = ""
            tar.addfile(ti, io.BytesIO(data))
    tgz = out_root / f"{name}.tar.gz"
    with open(tgz, "wb") as fh, gzip.GzipFile(filename="", mode="wb", fileobj=fh, mtime=epoch,
                                              compresslevel=9) as gz:
        gz.write(buf.getvalue())

    info = {"name": "bitnode-site", "version": v, "commit": commit, "source_date_epoch": epoch,
            "tree_sha256": tree, "artifact": tgz.name, "artifact_sha256": sha256(tgz),
            "files": manifest}
    (out_root / "build-info.json").write_text(json.dumps(info, indent=2, sort_keys=True) + "\n",
                                              encoding="utf-8")
    (out_root / "SHA256SUMS").write_text(
        "".join(f"{h}  site/{n}\n" for n, h in manifest.items()) + f"{info['artifact_sha256']}  {tgz.name}\n",
        encoding="utf-8")
    return info


def cmd_build() -> None:
    info = build(ROOT / "dist")
    print(f"[PASS] build {info['version']} ({info['commit']}) tree={info['tree_sha256'][:16]} "
          f"files={len(info['files'])}")


# ---------- validate ----------
class Refs(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.loads: list[str] = []   # fetched by the browser
        self.links: list[str] = []   # navigations
        self.i18n: set[str] = set()
        self.ids: set[str] = set()
        self.imgs_no_alt = 0
        self.script = ""
        self._in_script = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        if "data-i18n" in a:
            self.i18n.add(a["data-i18n"])
        if tag == "img" and "alt" not in a:
            self.imgs_no_alt += 1
        if tag in ("img", "script", "source") and a.get("src"):
            self.loads.append(a["src"])
        if tag == "link" and a.get("href") and a.get("rel") not in ("alternate", "canonical"):
            self.loads.append(a["href"])
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
        if tag == "use" and a.get("href", "").startswith("#"):
            self.links.append(a["href"])
        self._in_script = tag == "script"

    def handle_endtag(self, tag):
        if tag == "script":
            self._in_script = False

    def handle_data(self, data):
        if self._in_script:
            self.script += data


def luminance(hexc: str) -> float:
    c = [int(hexc.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contrast(a: str, b: str) -> float:
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def validate_output(out_root: Path) -> None:
    plan = load("build.json")
    site = out_root / "site"
    r = Report()

    # route ownership: LNbits/Worker paths must never be shipped by Pages
    for f in plan["forbidden_out_paths"]:
        if (site / f).exists():
            r.err(f"forbidden path in output: /{f} (owned by Cloudflare Worker -> LNbits)")

    # passthrough fallback content (LNURL names not in LNbits, NIP-05) must ship and parse
    pt = plan.get("passthrough", {})
    for f in pt.get("required_out_paths", []):
        if not (site / f).exists():
            r.err(f"required passthrough path missing: /{f}")
    for pat in pt.get("json_files", []):
        for f in sorted(site.glob(pat)):
            try:
                d = json.loads(f.read_text(encoding="utf-8"))
            except ValueError as e:
                r.err(f"invalid JSON /{f.relative_to(site).as_posix()}: {e}")
                continue
            rel = f.relative_to(site).as_posix()
            if "/lnurlp/" in rel and d.get("tag") != "payRequest":
                r.err(f"/{rel}: tag is not payRequest")
            if rel.endswith("nostr.json"):
                for n, k in d.get("names", {}).items():
                    if not re.fullmatch(r"[0-9a-f]{64}", k):
                        r.err(f"nostr.json: '{n}' is not a 64-hex pubkey")

    html = (site / "index.html").read_text(encoding="utf-8")
    if "{{" in html:
        r.err("unresolved template placeholder in index.html")
    p = Refs()
    p.feed(html)

    for u in p.loads:
        if re.match(r"^(https?:)?//", u):
            r.err(f"external runtime load (privacy/SoT): {u}")
        elif not (site / u.split("?")[0].split("#")[0]).is_file():
            r.err(f"missing local asset: {u}")
    css_urls = re.findall(r"url\(([^)#]+)\)", html)
    for u in css_urls:
        u = u.strip("'\"")
        if re.match(r"^(https?:)?//", u):
            r.err(f"external CSS url(): {u}")
        elif not (site / u).is_file():
            r.err(f"missing CSS asset: {u}")

    for h in p.links:
        if h.startswith("#") and h != "#" and h[1:] not in p.ids:
            r.err(f"dangling anchor {h}")
        m = re.match(r"^https?://([^/]+)", h)
        if m and m.group(1) not in plan["allowed_external_link_hosts"]:
            r.warn(f"external link to non-allowlisted host: {h}")
        if (h.startswith("mailto:") or h.startswith("lightning:")) and h not in plan.get("confirmed_contacts", []):
            r.warn(f"contact endpoint must be confirmed live before release: {h}")

    if p.imgs_no_alt:
        r.err(f"{p.imgs_no_alt} <img> without alt")

    m = re.search(r"const de=\{(.*?)\};", p.script, re.S)
    de_keys = set(re.findall(r"(\w+):\"", m.group(1))) if m else set()
    for k in sorted(p.i18n - de_keys):
        r.err(f"i18n key '{k}' has no DE translation")
    for k in sorted(de_keys - p.i18n):
        r.warn(f"DE key '{k}' unused")

    tok = load(plan["tokens_file"])
    def t(mode, key):
        return tok["palette"][key] if mode == "palette" else tok["modes"][mode][key]
    for c in plan["contrast_pairs"]:
        ratio = contrast(t(c["mode"], c["fg"]), t(c["mode"], c["bg"]))
        if ratio < c["min"]:
            r.err(f"contrast {c['name']} {ratio:.2f} < {c['min']}")

    # CSS custom properties must equal brand tokens (no drift between page and brand package)
    css = html.split("<style>", 1)[1].split("</style>", 1)[0]
    blocks = {"light": css.split(":root{", 1)[1].split("}", 1)[0],
              "dark": css.split(":root[data-theme=dark]{", 1)[1].split("}", 1)[0],
              "dark_auto": css.split(":root[data-theme=auto]{", 1)[1].split("}", 1)[0]}
    plan.setdefault("css_must_match_tokens", {})
    if "dark" in plan["css_must_match_tokens"]:
        plan["css_must_match_tokens"]["dark_auto"] = plan["css_must_match_tokens"]["dark"]
    for mode, mapping in plan.get("css_must_match_tokens", {}).items():
        for var, key in mapping.items():
            m2 = re.search(re.escape(var) + r":\s*(#[0-9A-Fa-f]{6})", blocks[mode])
            if not m2:
                r.err(f"CSS {mode} {var} not found")
            elif m2.group(1).upper() != t(mode.split("_")[0], key).upper():
                r.err(f"CSS {mode} {var}={m2.group(1)} != token {key}={t(mode.split('_')[0], key)}")

    og = re.search(r'property="og:image" content="https://bitnode\.one/([^"]+)"', html)
    if og and not (site / og.group(1)).is_file():
        r.err(f"og:image target missing: {og.group(1)}")

    v = version()
    cl = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    if f"## [{v}]" not in cl:
        r.err(f"CHANGELOG.md has no entry for {v}")
    if f"v{v}" not in html:
        r.err("built page does not expose its version")

    r.done("output validation")


def cmd_validate() -> None:
    cmd_check()
    info = build(ROOT / "dist")
    print(f"[PASS] build {info['version']} ({info['commit']})")
    validate_output(ROOT / "dist")


def cmd_verify() -> None:
    with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
        i1, i2 = build(Path(a) / "out"), build(Path(b) / "out")
    if (i1["tree_sha256"], i1["artifact_sha256"]) != (i2["tree_sha256"], i2["artifact_sha256"]):
        die("non-deterministic build: two builds differ")
    print(f"[PASS] deterministic: tree={i1['tree_sha256'][:16]} artifact={i1['artifact_sha256'][:16]}")


def cmd_release() -> None:
    if git("status", "--porcelain"):
        die("working tree not clean; commit first")
    v = version()
    if git("tag", "--list", f"v{v}"):
        die(f"tag v{v} exists; bump VERSION")
    cmd_validate()
    cmd_verify()
    subprocess.run(["git", "-C", str(ROOT), "tag", "-a", f"v{v}", "-m", f"bitnode-site {v}"], check=True)
    print(f"[PASS] tagged v{v}")


COMMANDS = {"fetch": cmd_fetch, "check": cmd_check, "build": cmd_build, "validate": cmd_validate,
            "verify": cmd_verify, "release": cmd_release}

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in COMMANDS:
        print(__doc__)
        sys.exit(1)
    COMMANDS[sys.argv[1]]()
