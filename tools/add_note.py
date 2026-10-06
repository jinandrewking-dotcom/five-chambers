#!/usr/bin/env python3
"""Append a note to site/content/notes.json.

notes.html reads this file, and the Decap CMS at /admin edits the same file,
so you can use whichever is closer to hand. This script lives outside site/
on purpose: Netlify publishes everything under site/, and a tool has no
business being downloadable from the website.

A note with the same source URL, or the same title on the same date, as an
existing entry is refused; pass --force to add it anyway.

Examples (run from the repo root)
--------
    python tools/add_note.py ^
        --title "Optogenetics takes the Nobel" ^
        --summary "Three laureates, one causal switch for behavioural science." ^
        --tags neuroscience,methods ^
        --source https://www.nobelprize.org/prizes/medicine/2026/press-release/ ^
        --source-label "Nobel Prize press release, 5 Oct 2026"

    # a specific date, a Chinese subtitle, and a preview instead of a write
    python tools/add_note.py --date 2026-10-05 ^
        --title "New data from old bones" --title-zh "旧骨头，新数据" ^
        --kind Archaeology --summary "..." --dry-run
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

NOTES_PATH = Path(__file__).resolve().parent.parent / "site" / "content" / "notes.json"
DATE_FMT = "%Y-%m-%d"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Append one entry to the Notes reading log (content/notes.json)."
    )
    parser.add_argument("--title", required=True, help="English title (required)")
    parser.add_argument("--summary", required=True, help="Two or three sentences (required)")
    parser.add_argument("--date", default=date.today().strftime(DATE_FMT),
                        help="YYYY-MM-DD (default: today)")
    parser.add_argument("--kind", default="Note",
                        help="Label shown beside the date, e.g. 'Journal scan'")
    parser.add_argument("--title-zh", dest="title_zh", default="",
                        help="Optional Chinese subtitle")
    parser.add_argument("--tags", default="",
                        help="Comma-separated, e.g. neuroscience,methods")
    parser.add_argument("--source", default="", help="Source URL")
    parser.add_argument("--source-label", dest="source_label", default="",
                        help="Human-readable source, e.g. 'Nature, 2 Oct 2026'")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print the entry without writing anything")
    parser.add_argument("--force", action="store_true",
                        help="Add the note even if it looks like a duplicate")
    return parser.parse_args(argv)


def _norm(text: str) -> str:
    return " ".join(str(text).split()).casefold()


def find_duplicate(entries: list, entry: dict) -> dict | None:
    """Return an existing entry with the same source URL, or the same title on the same date."""
    src = entry.get("source", "").rstrip("/").casefold()
    for old in entries:
        if not isinstance(old, dict):
            continue
        if src and str(old.get("source", "")).rstrip("/").casefold() == src:
            return old
        if (old.get("date") == entry["date"]
                and _norm(old.get("title", "")) == _norm(entry["title"])):
            return old
    return None


def load(path: Path) -> dict:
    """Read the notes file, or return an empty scaffold if it does not exist yet."""
    if not path.exists():
        return {"entries": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"! {path} is not valid JSON ({exc}). Fix it before adding a note.")
    if not isinstance(data, dict):
        raise SystemExit(f"! {path} should hold a JSON object with an 'entries' key.")
    data.setdefault("entries", [])
    if not isinstance(data["entries"], list):
        raise SystemExit(f"! 'entries' in {path} should be a list.")
    return data


def validate_date(value: str) -> str:
    try:
        date.fromisoformat(value)
    except ValueError:
        raise SystemExit(f"! --date must look like 2026-10-06 (got {value!r})")
    return value


def build_entry(args: argparse.Namespace) -> dict:
    entry: dict = {
        "date": validate_date(args.date),
        "kind": args.kind.strip() or "Note",
        "title": args.title.strip(),
        "summary": args.summary.strip(),
    }
    if args.title_zh.strip():
        entry["titleZh"] = args.title_zh.strip()
    tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    if tags:
        entry["tags"] = tags
    if args.source.strip():
        source = args.source.strip()
        if not source.lower().startswith(("http://", "https://")):
            raise SystemExit(f"! --source must start with http:// or https:// (got {source!r})")
        entry["source"] = source
    if args.source_label.strip():
        entry["sourceLabel"] = args.source_label.strip()
    return entry


def save(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        data = load(NOTES_PATH)
        entry = build_entry(args)

        dup = find_duplicate(data["entries"], entry)
        if dup and not args.force:
            print(f"! Looks like a duplicate of the note dated {dup.get('date')}: "
                  f"{dup.get('title')!r}. Nothing written (use --force to add it anyway).",
                  file=sys.stderr)
            return 2

        if args.dry_run:
            print("Dry run -- nothing written. The entry would be:")
            print(json.dumps(entry, ensure_ascii=False, indent=2))
            return 0

        data["entries"].insert(0, entry)      # newest first
        save(NOTES_PATH, data)
    except SystemExit:
        raise
    except OSError as exc:
        print(f"! Could not write {NOTES_PATH}: {exc}", file=sys.stderr)
        return 1

    print(f"Added note for {entry['date']}: {entry['title']}")
    print(f"  {NOTES_PATH} now holds {len(data['entries'])} entries")
    print('Next:  git add -A && git commit -m "note: ..." && git push')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
