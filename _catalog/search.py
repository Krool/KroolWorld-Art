"""
Asset Search CLI
Usage:
  python search.py sword                    # search filenames + tags
  python search.py --tag icon --tag weapon  # assets matching ALL tags
  python search.py --pack rpggame1700plusicons
  python search.py --type characters
  python search.py --tag snow --ext png
  python search.py --list-packs
  python search.py --list-tags

Options:
  -q / positional  Keyword search (filename + path + tags)
  --tag            Filter by tag (repeatable, AND logic)
  --pack           Filter by pack name (partial match)
  --type           Filter by category/type
  --ext            Filter by file extension (e.g. png, gif)
  --limit N        Max results (default 50)
  --full           Show full paths instead of short display
  --list-packs     List all packs with descriptions
  --list-tags      List all tags sorted by frequency
"""

import json
import sys
import argparse
from pathlib import Path

CATALOG_DIR = Path(__file__).parent
ASSETS_FILE = CATALOG_DIR / "assets.jsonl"
PACKS_FILE  = CATALOG_DIR / "packs.json"
ART_DIR     = CATALOG_DIR.parent


def load_assets():
    with open(ASSETS_FILE, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def load_packs():
    with open(PACKS_FILE, encoding="utf-8") as f:
        return json.load(f)


def list_packs(packs):
    print(f"\n{'Pack':<40} {'Category':<14} {'Files':>6}  Description")
    print("-" * 100)
    for p in sorted(packs, key=lambda x: x["category"]):
        desc = p["description"][:55] + "…" if len(p["description"]) > 55 else p["description"]
        print(f"  {p['pack']:<38} {p['category']:<14} {p['file_count']:>6}  {desc}")
    print()


def list_tags(assets):
    from collections import Counter
    counter = Counter()
    for a in assets:
        for t in a.get("tags", []):
            counter[t] += 1
    print("\nTag frequencies:\n")
    for tag, count in counter.most_common():
        print(f"  {tag:<30} {count}")
    print()


def search(assets, query=None, tags=None, pack=None, asset_type=None, ext=None, limit=50):
    results = []
    query_lower = query.lower() if query else None
    tags_lower  = [t.lower() for t in tags] if tags else []
    pack_lower  = pack.lower() if pack else None
    type_lower  = asset_type.lower() if asset_type else None
    ext_lower   = ("." + ext.lstrip(".")).lower() if ext else None

    for a in assets:
        # Pack filter
        if pack_lower and pack_lower not in a["pack"].lower():
            continue
        # Type filter
        if type_lower and type_lower not in a["type"].lower():
            continue
        # Extension filter
        if ext_lower and a.get("ext", "").lower() != ext_lower:
            continue
        # Tag filter (AND — must match all specified tags)
        if tags_lower:
            asset_tags = [t.lower() for t in a.get("tags", [])]
            if not all(t in asset_tags for t in tags_lower):
                continue
        # Keyword search
        if query_lower:
            searchable = " ".join([
                a.get("filename", ""),
                a.get("path", ""),
                " ".join(a.get("tags", [])),
            ]).lower()
            if query_lower not in searchable:
                continue

        results.append(a)
        if len(results) >= limit:
            break

    return results


def display(results, full=False):
    if not results:
        print("\n  No results found.\n")
        return

    print(f"\n  {len(results)} result(s):\n")
    for a in results:
        if full:
            path = ART_DIR / a["pack"] / a["path"]
            print(f"  {path}")
        else:
            tags = ", ".join(a["tags"][:5])
            print(f"  [{a['pack']}]  {a['path']}  ({tags})")
    print()


def main():
    parser = argparse.ArgumentParser(description="Search KroolWorld art assets")
    parser.add_argument("query", nargs="?", help="Keyword to search (filename/path/tags)")
    parser.add_argument("--tag",   action="append", dest="tags", metavar="TAG", help="Filter by tag (repeatable)")
    parser.add_argument("--pack",  help="Filter by pack name (partial match)")
    parser.add_argument("--type",  help="Filter by asset category/type")
    parser.add_argument("--ext",   help="Filter by file extension (e.g. png, gif)")
    parser.add_argument("--limit", type=int, default=50, help="Max results (default 50)")
    parser.add_argument("--full",  action="store_true", help="Show full absolute paths")
    parser.add_argument("--list-packs", action="store_true", help="List all packs")
    parser.add_argument("--list-tags",  action="store_true", help="List all tags by frequency")

    args = parser.parse_args()

    if args.list_packs:
        list_packs(load_packs())
        return

    assets = load_assets()

    if args.list_tags:
        list_tags(assets)
        return

    if not any([args.query, args.tags, args.pack, args.type, args.ext]):
        parser.print_help()
        return

    results = search(
        assets,
        query=args.query,
        tags=args.tags,
        pack=args.pack,
        asset_type=args.type,
        ext=args.ext,
        limit=args.limit,
    )
    display(results, full=args.full)


if __name__ == "__main__":
    main()
