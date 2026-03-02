# KroolWorld Asset Library

Shared game asset library for KroolWorld projects. Contains 38 packs (~55,000 files) — art, UI, icons, sound effects, and more — with a catalog, search tool, and export tool for pulling assets into other projects.

The art files themselves are local-only. This repo tracks the catalog metadata and tooling.

---

## What's in here

| Pack category | Packs |
|---|---|
| Characters | Cute chibi, medieval fantasy, survival, Segel bundle, Hero Editor (customizable) |
| Tilesets | Cave, dungeon, japan, forest, grassland, marsh, snow, tropical island, winter village |
| Icons | 1700+ RPG pixel icons, 2672+ hand-drawn fantasy icons, inventory icons, skill icons, tech icons |
| UI | Game UI kit (Area730), RPG unit frames, skill icon pack |
| Weapons | Pixel weapons, painted weapons, swords & shields |
| Items | Potion bottles, RPG item sets |
| Buildings | Houses, interiors, decorative props |
| Portraits | Character portrait paintings |
| Backgrounds | Fantasy painted backgrounds (arctic, desert, forest, volcano, etc.) |
| Effects | Hit/impact VFX (Casual Hit) |
| Audio | 10,000+ universal sound effects (75+ categories) |

Full pack listing: [`_catalog/GUIDE.md`](_catalog/GUIDE.md)
Style compatibility rules: [`_catalog/style_rules.md`](_catalog/style_rules.md)

---

## Setup

Clone the repo into the same machine where the art packs live:

```bash
git clone https://github.com/Krool/KroolWorld-Art.git
cd KroolWorld-Art
```

The art pack folders sit alongside `_catalog/` in the same directory. If you're setting up on a new machine, copy the art packs there after cloning.

---

## Search

```bash
# Keyword search
python _catalog/search.py sword

# Filter by tag
python _catalog/search.py --tag icon --tag weapon --ext png

# Filter by pack
python _catalog/search.py --pack swordsandshields

# Browse everything
python _catalog/search.py --list-packs
python _catalog/search.py --list-tags
```

---

## Export assets to a project

**Ad-hoc:**
```bash
python _catalog/export.py --tag sword --ext png --dest /your/project/assets
python _catalog/export.py --pack wintervillagegameassets --dest /your/project/assets
```

Add `--dry-run` to preview before copying. Add `--flat` to copy all files into a single folder. Source files (PSD, aseprite, SCML) are excluded by default — add `--include-source` to include them.

**Manifest-driven (recommended):**

Keeps a permanent record in your project of exactly which assets it uses.

```bash
# Run once in your project to scaffold the manifest
python _catalog/export.py --init-manifest /your/project

# Edit assets.manifest.json to declare what your project needs, then sync:
python _catalog/export.py --manifest /your/project/assets.manifest.json
```

Example manifest:
```json
{
  "dest": "./assets",
  "assets": [
    { "label": "swords and shields", "pack": "swordsandshields" },
    { "label": "weapon icons", "tags": ["weapon", "icon"], "ext": "png" },
    { "label": "winter tiles", "pack": "wintervillagegameassets", "ext": "png" }
  ]
}
```

---

## Adding new packs

1. Drop the new pack folder into the Art directory
2. Add its metadata to `PACK_CONTEXT` in `_catalog/generate_catalog.py`
3. Re-run the generator:
   ```bash
   python _catalog/generate_catalog.py
   ```
4. Commit and push the updated catalog files

---

## Catalog files

| File | Description |
|---|---|
| `_catalog/GUIDE.md` | Human-readable overview of all packs |
| `_catalog/style_rules.md` | Style groups and compatibility rules |
| `_catalog/visual_notes.json` | Visual metadata per pack (style, scale, palette) |
| `_catalog/packs.json` | Machine-readable pack data |
| `_catalog/assets.jsonl` | One record per file (54k+ entries) |
| `_catalog/search.py` | Search CLI |
| `_catalog/export.py` | Export/copy CLI |
| `_catalog/generate_catalog.py` | Regenerates all catalog files |
