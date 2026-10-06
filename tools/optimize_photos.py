#!/usr/bin/env python3
"""Shrink site photos and strip their metadata.

Phone photos carry EXIF metadata — including the GPS coordinates of where each
shot was taken — and are usually 3–6 MB. This script, for every image under
site/photos/:

  * applies the EXIF rotation to the pixels, then drops ALL metadata
    (GPS, camera model, timestamps);
  * scales the long edge down to MAX_EDGE pixels;
  * re-saves JPEGs as progressive, quality JPEG_QUALITY.

File names are kept, so content/*.json references keep working.
It is idempotent: files that are already small and metadata-free are skipped,
so it is safe to run on every push (see .github/workflows/optimize-photos.yml).

Usage (from the repo root):
    python tools/optimize_photos.py            # optimise in place
    python tools/optimize_photos.py --check    # report only; exit 1 if any file needs work
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError

PHOTOS_DIR = Path(__file__).resolve().parent.parent / "site" / "photos"
MAX_EDGE = 1600
JPEG_QUALITY = 82
EXTENSIONS = {".jpg", ".jpeg", ".png"}


def needs_work(img: Image.Image) -> list[str]:
    reasons = []
    if max(img.size) > MAX_EDGE:
        reasons.append(f"{img.size[0]}x{img.size[1]}")
    exif = img.getexif()
    if exif.get_ifd(0x8825):  # GPS IFD
        reasons.append("GPS")
    elif len(exif):
        reasons.append("EXIF")
    if img.info.get("xmp") or img.info.get("XML:com.adobe.xmp"):
        reasons.append("XMP")
    return reasons


def optimise(path: Path) -> int:
    """Rewrite one image; return bytes saved."""
    before = path.stat().st_size
    with Image.open(path) as src:
        img = ImageOps.exif_transpose(src)  # bake rotation into the pixels
        img.thumbnail((MAX_EDGE, MAX_EDGE), Image.LANCZOS)
        icc = src.info.get("icc_profile")  # keep colour profile, nothing else
        fmt = (src.format or "").upper()
        if fmt == "PNG":
            img.save(path, "PNG", optimize=True, icc_profile=icc)
        else:
            if img.mode not in ("RGB", "L"):
                img = img.convert("RGB")
            img.save(path, "JPEG", quality=JPEG_QUALITY, optimize=True,
                     progressive=True, icc_profile=icc)
    return before - path.stat().st_size


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true",
                        help="only report; exit 1 if any photo needs optimising")
    args = parser.parse_args(argv)

    if not PHOTOS_DIR.is_dir():
        print(f"! {PHOTOS_DIR} not found", file=sys.stderr)
        return 1

    todo, saved = 0, 0
    for path in sorted(PHOTOS_DIR.rglob("*")):
        if path.suffix.lower() not in EXTENSIONS or not path.is_file():
            continue
        rel = path.relative_to(PHOTOS_DIR.parent)
        try:
            with Image.open(path) as img:
                reasons = needs_work(img)
        except (UnidentifiedImageError, OSError):
            print(f"  skip (not a readable image): {rel}")
            continue
        if not reasons:
            continue
        todo += 1
        if args.check:
            print(f"  needs work: {rel} ({', '.join(reasons)})")
            continue
        delta = optimise(path)
        saved += delta
        print(f"  optimised:  {rel} ({', '.join(reasons)}) -{delta / 1e6:.1f} MB")

    if args.check:
        print(f"{todo} photo(s) need optimising")
        return 1 if todo else 0
    print(f"Done: {todo} photo(s) optimised, {saved / 1e6:.1f} MB saved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
