# KroolWorld Shared Asset Library

This folder is a shared game asset library. It contains 67 packs (~88,500 files) — art, UI, icons, sound effects, music, and more.
Do not modify the asset folders. Copy assets out to your project using the tools below.

---

## CRITICAL — Do NOT scan or process asset folders directly

This library has **88,500+ files** across 67 packs. The catalog already indexes every file.

**NEVER do any of the following:**
- `find`, `ls -R`, `glob`, or `grep` inside the asset pack folders
- Read or open image files to "understand" the collection
- Attempt to split sprite sheets, rename, resize, or reorganize assets
- Scan directories to build your own file lists — `assets.jsonl` already has every file

**ALWAYS use the catalog and tools instead:**
1. Read `_catalog/GUIDE.md` for pack descriptions, tags, styles, and file counts
2. Read `_catalog/style_rules.md` for compatibility rules before recommending assets
3. Run `python _catalog/search.py` to find specific assets by keyword, tag, or pack
4. Run `python _catalog/export.py` to copy assets into your project
5. Read `_catalog/packs.json` for machine-readable pack metadata (includes visual notes)

The catalog files contain everything you need — descriptions, tags, file types, art style, resolution, palette, compatibility groups, and per-file records. There is no reason to touch the raw asset folders.

---

## Find assets fast

**Search by keyword, tag, or pack:**
```bash
python _catalog/search.py sword                    # keyword search (filename + tags)
python _catalog/search.py --tag icon --tag weapon --ext png  # multi-tag AND filter
python _catalog/search.py --pack swordsandshields  # browse a specific pack
python _catalog/search.py --type characters         # filter by category
python _catalog/search.py --list-packs             # list all 65 packs with descriptions
python _catalog/search.py --list-tags              # list all tags by frequency
python _catalog/search.py --limit 100 knight       # increase result limit (default 50)
python _catalog/search.py --full knight            # show full absolute paths
```

**Copy assets to your project:**
```bash
# Ad-hoc — copy matching assets directly
python _catalog/export.py --tag sword --ext png --dest /your/project/assets
python _catalog/export.py --pack swordsandshields --dest /your/project/assets
python _catalog/export.py --dest /your/project/assets knight  # keyword search

# Manifest-driven (recommended — keeps a record of what your project uses)
python _catalog/export.py --init-manifest /your/project   # run once to scaffold
python _catalog/export.py --manifest /your/project/assets.manifest.json

# Useful flags
#   --dry-run          Preview what would be copied without copying
#   --flat             Flatten all files into dest (no subfolders)
#   --overwrite        Overwrite existing files (default: skip)
#   --include-source   Include PSD/aseprite/SCML source files (excluded by default)
```

---

## Understand the collection

Read these files before recommending or selecting assets:

| File | Purpose |
|---|---|
| `_catalog/GUIDE.md` | Full pack listing — descriptions, usage, tags, file counts, visual metadata |
| `_catalog/style_rules.md` | **Critical** — style groups, compatibility rules, what NOT to mix |
| `_catalog/visual_notes.json` | Per-pack visual metadata: art style, scale, palette, perspective |
| `_catalog/packs.json` | Machine-readable pack data (includes visual_notes merged in) |
| `_catalog/assets.jsonl` | One record per file — pack, path, type, tags, size |

**Workflow for asset recommendations:**
1. Read `style_rules.md` to understand the 6 style groups and compatibility matrix
2. Read `GUIDE.md` to find packs matching the project's needs
3. Use `search.py` to find specific assets within those packs
4. Use `export.py` to copy selected assets into the target project

---

## Key facts for asset recommendations

- Packs fall into **6 visual style groups** (A–F) plus style-independent packs (UI, audio) — see `_catalog/style_rules.md` before recommending
- Never mix cartoon/illustrated characters (Group D) with pixel art tilesets (Group A/B)
- The `rpgworlds*` packs are a cohesive family — use them together
- `tropicalislandgameassets` and `wintervillagegameassets` are siblings by the same creator
- `rpggame1700plusicons` is the most comprehensive pixel icon set (1700+ items) — check it first for pixel RPG UI icons
- `FantasyIconsMegaPack` has 2672+ hand-drawn icons — the largest icon pack for non-pixel projects
- `Tiny RPG Character Asset Pack` has 20 side-view battle characters with full animations — good for combat scenes
- `10k Game Assets` has 10,000+ assets spanning pixel art AND HD graphics (two incompatible styles) plus audio, fonts, and 3D models — do NOT mix pixel and HD sections
- `Game Assets(2)` has 10,000+ pixel art fantasy RPG assets — tilesets, characters, monsters, spell VFX, platformer tiles, sound effects (RPG Maker compatible)
- `Universal Sound FX` contains 10,000+ WAV sound effects across 75+ categories — check it first for any sound need
- `Cute RPG Music Pack 1–5` has 25 lighthearted RPG music tracks (MP3/OGG/WAV, loopable) — use for cute/casual games
- `Epic Medieval I–V Music Pack` has 30 epic orchestral tracks — use for serious medieval/fantasy RPGs
- `Farming RPG Music Pack 1–5` has 26 pastoral/relaxing tracks — use for farming/life sim games
- `Area730` is a complete game UI kit (buttons, bars, panels, dialogs)
- `32rogues` is a complete 32x32 roguelike tileset (v0.5.0) — characters, monsters, items, tiles, autotiles in one pack
- `CHARACTER MEGAPACK` has 54 tiny pixel characters (heroes with LVL1-4 variants, enemies, NPCs) — from the same creator as SLIMES, RPG HEROES, and Orcs Goblins packs
- `CHARACTER MEGAPACK`, `SLIMES BLOBS TENTACLES`, `RPG HEROES ENEMIES`, and `Orcs Goblins V2` share identical art style — use them together
- `Tiny Swords (Free Pack)` has buildings, terrain, units (5 types × 5 faction colors), UI, and particle FX — cute RTS/strategy style
- `Tiny Swords (Enemy Pack)` has 17 enemy creature types + avatars — companion to Tiny Swords Free Pack, use together
- `OVERBURN AssetPack` has fire/flame VFX in 4 color variants — good for spell effects
- `ASTRONAUT AssetPack` has 15 color variants with 8-directional animations — ideal for multiplayer
- `OVERSTELLAR AssetPack` has animated planets, stars, galaxies, and space backgrounds — complete space environment kit
- Source files (.psd, .aseprite, .scml) are excluded from exports by default

---

## Adding new packs to the catalog

When a new asset folder is added to this directory:

1. Add a `PACK_CONTEXT` entry in `_catalog/generate_catalog.py` (description, category, style, usage, tags)
2. Add a visual metadata entry in `_catalog/visual_notes.json` (art style, perspective, resolution, palette, compatibility group)
3. Add the pack to the appropriate style group table in `_catalog/style_rules.md`
4. Run `python _catalog/generate_catalog.py` to regenerate `packs.json`, `assets.jsonl`, and `GUIDE.md`
5. Update the pack count in this file
