"""
Asset Export Tool
Copies assets from the KroolWorld shared library into a target project directory.

── Ad-hoc copy ──────────────────────────────────────────────────────────────────
  python export.py --dest /path/to/project/assets --tag sword
  python export.py --dest /path/to/project/assets --pack swordsandshields
  python export.py --dest /path/to/project/assets --tag icon --tag weapon --ext png
  python export.py --dest /path/to/project/assets sword          # keyword search

── Manifest-driven copy ─────────────────────────────────────────────────────────
  # 1. Create a manifest in your project (see --init-manifest)
  # 2. Run:
  python export.py --manifest /path/to/project/assets.manifest.json

  python export.py --init-manifest /path/to/project   # scaffold a blank manifest

── Options ──────────────────────────────────────────────────────────────────────
  --dest PATH        Destination directory to copy assets into
  --manifest PATH    Path to a project manifest JSON file
  --init-manifest D  Write a blank manifest template into directory D
  --flat             Flatten all files into dest (no subfolders)
  --dry-run          Print what would be copied without copying anything
  --overwrite        Overwrite existing files (default: skip)
  --tag TAG          Filter by tag (repeatable, AND logic)
  --pack PACK        Filter by pack name (partial match)
  --type TYPE        Filter by asset category
  --ext EXT          Filter by file extension (e.g. png)
  query              Positional keyword search
"""

import json
import shutil
import argparse
from pathlib import Path

CATALOG_DIR = Path(__file__).parent
ASSETS_FILE = CATALOG_DIR / "assets.jsonl"
ART_DIR     = CATALOG_DIR.parent

SKIP_TYPES = {"source_file", "documentation", "animation_data"}


def load_assets():
    with open(ASSETS_FILE, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def search_assets(assets, query=None, tags=None, pack=None, asset_type=None,
                  ext=None, exclude_source=True):
    query_lower = query.lower() if query else None
    tags_lower  = [t.lower() for t in tags] if tags else []
    pack_lower  = pack.lower() if pack else None
    type_lower  = asset_type.lower() if asset_type else None
    ext_lower   = ("." + ext.lstrip(".")).lower() if ext else None

    results = []
    for a in assets:
        if exclude_source and a.get("type") in SKIP_TYPES:
            continue
        if pack_lower and pack_lower not in a["pack"].lower():
            continue
        if type_lower and type_lower not in a["type"].lower():
            continue
        if ext_lower and a.get("ext", "").lower() != ext_lower:
            continue
        if tags_lower:
            asset_tags = [t.lower() for t in a.get("tags", [])]
            if not all(t in asset_tags for t in tags_lower):
                continue
        if query_lower:
            searchable = " ".join([
                a.get("filename", ""),
                a.get("path", ""),
                " ".join(a.get("tags", [])),
            ]).lower()
            if query_lower not in searchable:
                continue
        results.append(a)
    return results


def copy_assets(assets, dest: Path, flat=False, dry_run=False, overwrite=False):
    dest.mkdir(parents=True, exist_ok=True)
    copied = skipped = missing = 0

    for a in assets:
        src = ART_DIR / a["pack"] / a["path"]
        if not src.exists():
            print(f"  [missing]  {src}")
            missing += 1
            continue

        if flat:
            dst = dest / src.name
        else:
            dst = dest / a["pack"] / a["path"]

        if dst.exists() and not overwrite:
            skipped += 1
            continue

        if dry_run:
            print(f"  [dry-run]  {a['pack']}/{a['path']}  ->  {dst}")
            copied += 1
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            copied += 1

    label = "Would copy" if dry_run else "Copied"
    print(f"\n  {label}: {copied}  |  Skipped (exists): {skipped}  |  Missing: {missing}\n")
    return copied


def load_manifest(path: Path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def run_manifest(manifest: dict, assets, dest_override=None,
                 dry_run=False, overwrite=False, flat=False):
    dest = Path(dest_override) if dest_override else Path(manifest["dest"])
    total = 0

    for entry in manifest.get("assets", []):
        label = entry.get("label", "unnamed")
        print(f"\n── {label} ──")
        matched = search_assets(
            assets,
            query    = entry.get("query"),
            tags     = entry.get("tags"),
            pack     = entry.get("pack"),
            asset_type = entry.get("type"),
            ext      = entry.get("ext"),
            exclude_source = entry.get("exclude_source", True),
        )
        if not matched:
            print(f"  [warn] No assets matched for entry: {label}")
            continue
        total += copy_assets(matched, dest, flat=flat, dry_run=dry_run, overwrite=overwrite)

    print(f"Total exported: {total}")


MANIFEST_TEMPLATE = {
    "_comment": "KroolWorld asset manifest. Run: python /path/to/export.py --manifest this_file.json",
    "dest": "./assets",
    "assets": [
        {
            "label": "example — all sword icons (png only)",
            "tags": ["sword"],
            "ext": "png"
        },
        {
            "label": "example — entire pack",
            "pack": "swordsandshields"
        },
        {
            "label": "example — keyword search",
            "query": "idle",
            "pack": "medievalfantasycharacters"
        }
    ]
}


def init_manifest(directory: Path):
    directory.mkdir(parents=True, exist_ok=True)
    out = directory / "assets.manifest.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(MANIFEST_TEMPLATE, f, indent=2)
    print(f"Manifest written to: {out}")


def main():
    parser = argparse.ArgumentParser(description="Export assets from KroolWorld library")
    parser.add_argument("query", nargs="?", help="Keyword search")
    parser.add_argument("--dest",          help="Destination directory")
    parser.add_argument("--manifest",      help="Path to project manifest JSON")
    parser.add_argument("--init-manifest", metavar="DIR", help="Write blank manifest into DIR")
    parser.add_argument("--flat",          action="store_true", help="Flatten output (no subfolders)")
    parser.add_argument("--dry-run",       action="store_true", help="Preview without copying")
    parser.add_argument("--overwrite",     action="store_true", help="Overwrite existing files")
    parser.add_argument("--tag",   action="append", dest="tags", metavar="TAG")
    parser.add_argument("--pack",  help="Filter by pack name")
    parser.add_argument("--type",  help="Filter by asset type/category")
    parser.add_argument("--ext",   help="File extension filter (e.g. png)")
    parser.add_argument("--include-source", action="store_true",
                        help="Include PSD/aseprite/scml source files (excluded by default)")

    args = parser.parse_args()

    if args.init_manifest:
        init_manifest(Path(args.init_manifest))
        return

    assets = load_assets()

    if args.manifest:
        manifest = load_manifest(Path(args.manifest))
        run_manifest(manifest, assets, dest_override=args.dest,
                     dry_run=args.dry_run, overwrite=args.overwrite, flat=args.flat)
        return

    if not any([args.query, args.tags, args.pack, args.type, args.ext]):
        parser.print_help()
        return

    if not args.dest and not args.dry_run:
        parser.error("--dest is required unless using --dry-run")

    matched = search_assets(
        assets,
        query      = args.query,
        tags       = args.tags,
        pack       = args.pack,
        asset_type = args.type,
        ext        = args.ext,
        exclude_source = not args.include_source,
    )

    if not matched:
        print("\n  No assets matched.\n")
        return

    print(f"\n  Matched: {len(matched)} files")
    dest = Path(args.dest) if args.dest else Path(".")
    copy_assets(matched, dest, flat=args.flat, dry_run=args.dry_run, overwrite=args.overwrite)


if __name__ == "__main__":
    main()
