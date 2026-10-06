#!/usr/bin/env python3
"""Self-host the site's web fonts in site/fonts/ (no requests to Google at page load).

Why: fonts.googleapis.com / fonts.gstatic.com are blocked in mainland China,
so visitors there fell back to system fonts. Serving the files from the site
itself works everywhere.

What it builds
  site/fonts/fraunces-*.woff2, instrument-sans-*.woff2
      Latin + Latin-Extended variable fonts (weights 400–700), downloaded once.
  site/fonts/noto-serif-sc-600.woff2
      The Chinese display font, SUBSET to only the CJK characters that appear in
      site/**/*.html and site/content/*.json. The full font is several MB; the
      subset is a few tens of KB. Characters you add later (e.g. a Chinese note
      title in the CMS) are picked up the next time this runs. Until then they
      simply render in the visitor's system serif.
  site/fonts/fonts.css
      The @font-face rules every page links to.

The CJK subset is only re-downloaded when the set of characters changes
(tracked in site/fonts/noto-serif-sc.chars.txt), so running it repeatedly is
cheap and produces no diff. .github/workflows/build-fonts.yml runs it on every
push that changes page text.

Usage (from the repo root):
    python tools/build_fonts.py            # build / update
    python tools/build_fonts.py --force    # re-download everything
"""
from __future__ import annotations

import argparse
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
FONTS = SITE / "fonts"
CHARS_FILE = FONTS / "noto-serif-sc.chars.txt"
CJK_FILE = "noto-serif-sc-600.woff2"

# A modern browser UA makes Google return woff2 with unicode-range subsets.
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0 Safari/537.36")
LATIN_CSS = ("https://fonts.googleapis.com/css2?"
             "family=Fraunces:ital,opsz,wght@0,9..144,400..700;1,9..144,400..700"
             "&family=Instrument+Sans:wght@400..700&display=swap")
KEEP_SUBSETS = {"latin", "latin-ext"}

# Chinese characters, CJK punctuation and full-width forms
CJK_RE = re.compile(r"[　-〿㐀-䶿一-鿿豈-﫿＀-￯]")


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def build_latin(force: bool) -> list[str]:
    """Download the Latin font files; return their @font-face rules."""
    css = fetch(LATIN_CSS).decode("utf-8")
    rules = []
    for subset, body in re.findall(r"/\*\s*([\w-]+)\s*\*/\s*@font-face\s*{(.*?)}", css, re.S):
        if subset not in KEEP_SUBSETS:
            continue
        family = re.search(r"font-family:\s*'([^']+)'", body).group(1)
        style = re.search(r"font-style:\s*(\w+)", body).group(1)
        weight = re.search(r"font-weight:\s*([\d ]+);", body).group(1).strip()
        url = re.search(r"url\((https://[^)]+\.woff2)\)", body).group(1)
        urange = re.search(r"unicode-range:\s*([^;]+);", body).group(1).strip()
        name = f"{slug(family)}-{style}-{subset}.woff2"
        dest = FONTS / name
        if force or not dest.exists():
            dest.write_bytes(fetch(url))
            print(f"  downloaded {name} ({dest.stat().st_size // 1024} KB)")
        rules.append(
            f"/* {family} {style}, {subset} */\n"
            f"@font-face{{font-family:'{family}';font-style:{style};font-weight:{weight};"
            f"font-display:swap;src:url({name}) format('woff2');unicode-range:{urange};}}"
        )
    if not rules:
        raise SystemExit("! Google Fonts returned no latin @font-face rules — has the API changed?")
    return rules


def site_cjk_chars() -> str:
    chars: set[str] = set()
    for path in list(SITE.rglob("*.html")) + list((SITE / "content").glob("*.json")):
        if "admin" in path.parts:
            continue
        chars.update(CJK_RE.findall(path.read_text(encoding="utf-8")))
    return "".join(sorted(chars))


def build_cjk(force: bool) -> str:
    """Download a Noto Serif SC 600 subset covering the site's CJK text; return its rule."""
    chars = site_cjk_chars()
    old = CHARS_FILE.read_text(encoding="utf-8").strip() if CHARS_FILE.exists() else ""
    dest = FONTS / CJK_FILE
    if force or chars != old or not dest.exists():
        css = fetch("https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@600&text="
                    + urllib.parse.quote(chars)).decode("utf-8")
        url = re.search(r"url\((https://[^)]+)\)", css).group(1)
        dest.write_bytes(fetch(url))
        CHARS_FILE.write_text(chars + "\n", encoding="utf-8")
        print(f"  downloaded {CJK_FILE}: {len(chars)} characters ({dest.stat().st_size // 1024} KB)")
    else:
        print(f"  {CJK_FILE} already covers all {len(chars)} characters")
    return ("/* Noto Serif SC 600, subset to the characters used on the site\n"
            "   (rebuilt by tools/build_fonts.py; unlisted characters fall back to system serif) */\n"
            f"@font-face{{font-family:'Noto Serif SC';font-style:normal;font-weight:600;"
            f"font-display:swap;src:url({CJK_FILE}) format('woff2');}}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--force", action="store_true", help="re-download every font file")
    args = parser.parse_args(argv)

    FONTS.mkdir(parents=True, exist_ok=True)
    try:
        rules = build_latin(args.force) + [build_cjk(args.force)]
    except OSError as exc:  # network problems
        print(f"! Could not download fonts: {exc}", file=sys.stderr)
        return 1

    css = ("/* Self-hosted web fonts — generated by tools/build_fonts.py, do not edit by hand. */\n\n"
           + "\n\n".join(rules) + "\n")
    out = FONTS / "fonts.css"
    if not out.exists() or out.read_text(encoding="utf-8") != css:
        out.write_text(css, encoding="utf-8")
        print("  wrote fonts/fonts.css")
    total = sum(p.stat().st_size for p in FONTS.glob("*.woff2"))
    print(f"Done: {len(list(FONTS.glob('*.woff2')))} font files, {total // 1024} KB total")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
