#!/usr/bin/env python3
"""Append a note to site/content/notes.json.

notes.html reads this file, and the Decap CMS at /admin edits the same file,
so you can use whichever is closer to hand.

Examples
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

NOTES_PATH = Path(__file__).resolve().parent.parent / "content" / "notes.json"
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
    return parser.parse_args(argv)


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
        entry["source"] = args.source.strip()
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
