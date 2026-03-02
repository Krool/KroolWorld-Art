# KroolWorld Shared Asset Library

This folder is a shared game asset library. It contains 38 packs (~55,000 files) — art, UI, icons, sound effects, and more.
Do not modify the asset folders. Copy assets out to your project using the tools below.

---

## Find assets fast

**Search by keyword, tag, or pack:**
```bash
python _catalog/search.py sword
python _catalog/search.py --tag icon --tag weapon --ext png
python _catalog/search.py --pack swordsandshields
python _catalog/search.py --list-packs
python _catalog/search.py --list-tags
```

**Copy assets to your project:**
```bash
# Ad-hoc
python _catalog/export.py --tag sword --ext png --dest /your/project/assets

# Manifest-driven (recommended — keeps a record of what your project uses)
python _catalog/export.py --init-manifest /your/project   # run once to scaffold
python _catalog/export.py --manifest /your/project/assets.manifest.json
```

Add `--dry-run` to preview before copying. Source files (PSD, aseprite) are excluded by default; add `--include-source` to include them.

---

## Understand the collection

Read these files before recommending or selecting assets:

| File | Purpose |
|---|---|
| `_catalog/GUIDE.md` | Full pack listing — descriptions, usage, tags, file counts |
| `_catalog/style_rules.md` | **Critical** — style groups, compatibility rules, what NOT to mix |
| `_catalog/visual_notes.json` | Per-pack visual metadata: art style, scale, palette, perspective |
| `_catalog/packs.json` | Machine-readable pack data |
| `_catalog/assets.jsonl` | One record per file — pack, path, type, tags, size |

---

## Key facts for asset recommendations

- Packs fall into **5 visual style groups** plus style-independent packs (UI, audio) — see `_catalog/style_rules.md` before recommending
- Never mix cartoon/illustrated characters (Group D) with pixel art tilesets (Group A/B)
- The `rpgworlds*` packs are a cohesive family — use them together
- `tropicalislandgameassets` and `wintervillagegameassets` are siblings by the same creator
- `rpggame1700plusicons` is the most comprehensive pixel icon set (1700+ items) — check it first for pixel RPG UI icons
- `FantasyIconsMegaPack` has 2672+ hand-drawn icons — the largest icon pack for non-pixel projects
- `Universal Sound FX` contains 10,000+ WAV sound effects across 75+ categories — check it first for any sound need
- `Area730` is a complete game UI kit (buttons, bars, panels, dialogs)
- Source files (.psd, .aseprite, .scml) are excluded from exports by default
