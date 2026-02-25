"""
Asset Catalog Generator
Scans all art packs and produces:
  - assets.jsonl     (one record per file)
  - packs.json       (one record per pack, includes visual_notes.json data)
  - GUIDE.md         (human + LLM readable overview)

Visual metadata is read from visual_notes.json and merged into packs.json.
Edit visual_notes.json to update visual descriptions; re-run this script to apply.
"""

import json
import re
from pathlib import Path
from collections import defaultdict

ART_DIR = Path(__file__).parent.parent
CATALOG_DIR = Path(__file__).parent

SKIP_DIRS = {"_catalog"}
SKIP_EXTS = {".meta", ".db", ".DS_Store", ""}
TEXT_EXTS  = {".txt", ".md", ".csv"}

# ── Per-pack manually curated context ──────────────────────────────────────────
PACK_CONTEXT = {
    "2dcutecharacterspack": {
        "description": "Cute/chibi-style 2D character sprites with multiple animation states. Includes PSD source files.",
        "category": "characters",
        "style": "cute, chibi, cartoon",
        "usage": "Player characters, NPCs, overworld sprites",
        "tags": ["character", "sprite", "animated", "cute", "chibi", "top-down"],
    },
    "7soulsrpggraphics_cavetileset": {
        "description": "Cave and underground tileset for RPG games.",
        "category": "tileset",
        "style": "pixel art, rpg",
        "usage": "Underground levels, cave biomes, dungeon interiors",
        "tags": ["tileset", "cave", "underground", "rpg", "pixel"],
    },
    "7soulsrpggraphics_dungeontileset": {
        "description": "Dungeon tileset with animated tiles and autotile support.",
        "category": "tileset",
        "style": "pixel art, rpg",
        "usage": "Dungeon floors, walls, animated tiles for RPGMaker or custom engine",
        "tags": ["tileset", "dungeon", "animated", "autotile", "rpg", "pixel"],
    },
    "japantileset": {
        "description": "Japanese-themed environment tileset.",
        "category": "tileset",
        "style": "pixel art, japanese",
        "usage": "Japanese town/village environments",
        "tags": ["tileset", "japan", "japanese", "environment", "town"],
    },
    "medievalfantasycharacters": {
        "description": "Large pack of medieval fantasy character sprites with many classes and animation states.",
        "category": "characters",
        "style": "pixel art, medieval, fantasy",
        "usage": "RPG player characters, enemies, NPCs — medieval fantasy setting",
        "tags": ["character", "sprite", "animated", "medieval", "fantasy", "rpg", "pixel"],
    },
    "medievalrpgpack": {
        "description": "General medieval RPG asset pack — mix of tiles, props, and decorative elements.",
        "category": "mixed",
        "style": "pixel art, medieval",
        "usage": "Medieval RPG environments, general-purpose sprites",
        "tags": ["medieval", "rpg", "tileset", "prop", "pixel"],
    },
    "medievalskillandabilityicons": {
        "description": "Medieval skill and ability icons for RPG UI. Includes PSD source files.",
        "category": "icons",
        "style": "stylized, fantasy",
        "usage": "Skill trees, ability bars, inventory UI, spell icons",
        "tags": ["icon", "ui", "skill", "ability", "medieval", "fantasy", "rpg"],
    },
    "medievaltechnologyandskillicons": {
        "description": "Technology and crafting skill icons for RPG UI. Includes PSD source files.",
        "category": "icons",
        "style": "stylized, fantasy",
        "usage": "Tech trees, crafting menus, upgrade screens",
        "tags": ["icon", "ui", "technology", "crafting", "skill", "medieval"],
    },
    "outdoorandforesttileset": {
        "description": "Outdoor and forest environment tileset with animated elements. Includes Aseprite source files.",
        "category": "tileset",
        "style": "pixel art",
        "usage": "Forest biomes, outdoor overworld maps",
        "tags": ["tileset", "outdoor", "forest", "nature", "animated", "pixel"],
    },
    "pixelhouseandfurnies": {
        "description": "Pixel art house interiors and furniture sprites. Includes Aseprite source files.",
        "category": "props",
        "style": "pixel art",
        "usage": "Indoor scenes, house interiors, furniture decoration",
        "tags": ["prop", "interior", "furniture", "house", "pixel"],
    },
    "potionbottles": {
        "description": "Potion bottle item sprites. Includes PSD source files.",
        "category": "items",
        "style": "stylized, fantasy",
        "usage": "Inventory items, consumables, potion icons",
        "tags": ["item", "potion", "consumable", "inventory", "fantasy"],
    },
    "rpgbuildingshouses": {
        "description": "RPG building and house sprites. Includes PSD source files.",
        "category": "buildings",
        "style": "pixel art, rpg",
        "usage": "Overworld buildings, towns, villages",
        "tags": ["building", "house", "structure", "overworld", "rpg", "pixel"],
    },
    "rpgcharacterportraits": {
        "description": "Character portrait illustrations for RPG dialogue and character screens. Includes PSD source files.",
        "category": "portraits",
        "style": "illustrated, fantasy",
        "usage": "Dialogue boxes, character selection screens, party UI",
        "tags": ["portrait", "character", "ui", "dialogue", "fantasy", "rpg"],
    },
    "rpggame1700plusicons": {
        "description": "Massive icon pack with 1700+ RPG game icons across many categories: weapons, armor, consumables, materials, skills, accessories.",
        "category": "icons",
        "style": "pixel art, rpg",
        "usage": "Inventory items, equipment slots, loot, skill icons — comprehensive RPG UI icon set",
        "tags": ["icon", "ui", "weapon", "armor", "item", "skill", "consumable", "material", "rpg", "pixel"],
    },
    "rpginventoryiconsv1": {
        "description": "RPG inventory item icons version 1. Includes PSD source files.",
        "category": "icons",
        "style": "pixel art, rpg",
        "usage": "Inventory UI, item pickups, loot drops",
        "tags": ["icon", "inventory", "item", "ui", "rpg", "pixel"],
    },
    "rpgitemssetv3": {
        "description": "RPG items icon set version 3 — equipment, consumables, and misc items.",
        "category": "items",
        "style": "pixel art, rpg",
        "usage": "Item icons for inventory, shops, drops",
        "tags": ["item", "icon", "equipment", "consumable", "rpg", "pixel"],
    },
    "rpgpixelweapons": {
        "description": "Small pixel art weapons sprite sheet.",
        "category": "weapons",
        "style": "pixel art",
        "usage": "Weapon icons or equippable sprites",
        "tags": ["weapon", "icon", "pixel", "equipment"],
    },
    "rpgsurvivalcharacter": {
        "description": "Survival-themed RPG character with animation states. Includes Aseprite source files.",
        "category": "characters",
        "style": "pixel art, survival",
        "usage": "Survival game player character, post-apocalyptic or wilderness RPG",
        "tags": ["character", "sprite", "animated", "survival", "rpg", "pixel"],
    },
    "rpgweaponsv1": {
        "description": "RPG weapon illustrations version 1 — swords, axes, bows, etc. Includes PSD source files.",
        "category": "weapons",
        "style": "stylized, fantasy",
        "usage": "Weapon item icons, inventory, equipment screens",
        "tags": ["weapon", "icon", "sword", "axe", "bow", "fantasy", "rpg"],
    },
    "rpgworldsdecorativeprops": {
        "description": "Decorative prop sprites for RPG world environments. Includes PSD source files.",
        "category": "props",
        "style": "pixel art, rpg",
        "usage": "Environment decoration, map detailing",
        "tags": ["prop", "decoration", "environment", "rpg", "pixel"],
    },
    "rpgworldsgrassland": {
        "description": "Grassland biome tileset for RPG worlds. Includes PSD source files.",
        "category": "tileset",
        "style": "pixel art, rpg",
        "usage": "Overworld grassland maps, fields, plains",
        "tags": ["tileset", "grassland", "nature", "overworld", "rpg", "pixel"],
    },
    "rpgworldshousesandinteriors": {
        "description": "House and interior sprites for RPG worlds. Includes PSD source files.",
        "category": "buildings",
        "style": "pixel art, rpg",
        "usage": "Building interiors, house rooms, indoor environments",
        "tags": ["building", "interior", "house", "rpg", "pixel"],
    },
    "rpgworldsmarshland": {
        "description": "Marshland/swamp biome tileset for RPG worlds. Includes PSD source files.",
        "category": "tileset",
        "style": "pixel art, rpg",
        "usage": "Swamp biomes, marsh environments, wetlands",
        "tags": ["tileset", "marsh", "swamp", "wetland", "biome", "rpg", "pixel"],
    },
    "rpgworldssnowylands": {
        "description": "Snowy landscape tileset for RPG worlds. Includes PSD source files.",
        "category": "tileset",
        "style": "pixel art, rpg",
        "usage": "Winter biomes, snow environments, icy lands",
        "tags": ["tileset", "snow", "winter", "cold", "biome", "rpg", "pixel"],
    },
    "segel2dcharactersbundle": {
        "description": "Large bundle of 2D character sprites by Segel. Includes Spriter (SCML) animation files and PSD sources.",
        "category": "characters",
        "style": "pixel art, fantasy",
        "usage": "RPG characters with skeletal animation support (Spriter), player and NPC sprites",
        "tags": ["character", "sprite", "animated", "spriter", "scml", "rpg", "pixel", "fantasy"],
    },
    "snowforesttilesets": {
        "description": "Snow-covered forest tileset with animated elements. Includes Aseprite source files.",
        "category": "tileset",
        "style": "pixel art",
        "usage": "Winter forest biomes, snowy outdoor environments",
        "tags": ["tileset", "snow", "forest", "winter", "animated", "pixel"],
    },
    "swordsandshields": {
        "description": "Sword and shield weapon/equipment sprites. Includes PSD source files.",
        "category": "weapons",
        "style": "pixel art, fantasy",
        "usage": "Melee weapon and shield icons, equipment UI",
        "tags": ["weapon", "sword", "shield", "equipment", "icon", "fantasy", "pixel"],
    },
    "tropicalislandgameassets": {
        "description": "Comprehensive tropical island asset pack — tiles, animated shorelines, boats, dolphins, cliffs, doors, and more. Includes RPGMaker MV/MZ support and Aseprite sources.",
        "category": "tileset",
        "style": "pixel art, tropical",
        "usage": "Tropical island maps, ocean shores, water tiles, island structures, RPGMaker-compatible",
        "tags": ["tileset", "tropical", "island", "ocean", "water", "animated", "boat", "shore", "rpgmaker", "pixel"],
    },
    "wintervillagegameassets": {
        "description": "Winter village asset pack — tiles, doors, animated elements, cabin/shed structures. RPGMaker MV/MZ compatible.",
        "category": "tileset",
        "style": "pixel art, winter",
        "usage": "Winter village maps, snowy town environments, cabin interiors, RPGMaker-compatible",
        "tags": ["tileset", "winter", "village", "snow", "cabin", "door", "animated", "rpgmaker", "pixel"],
    },
}

# ── Tag inference from filename patterns ───────────────────────────────────────
ANIMATION_KEYWORDS = {
    "idle", "walk", "run", "attack", "jump", "death", "die", "hurt",
    "hit", "cast", "shoot", "swing", "block", "roll", "climb", "swim",
    "fall", "dash", "crouch", "sit", "stand", "wave", "talk", "open", "close",
}

def infer_tags_from_path(rel_path: str, pack_tags: list) -> list:
    parts = re.split(r"[\\/\-_. ]", rel_path.lower())
    tags = set(pack_tags)
    for part in parts:
        if part in ANIMATION_KEYWORDS:
            tags.add(part)
            tags.add("animated")
    return sorted(tags)


def get_asset_type(pack_category: str, ext: str, filename: str) -> str:
    fname = filename.lower()
    if ext in {".psd", ".aseprite"}:
        return "source_file"
    if ext in {".txt", ".md"}:
        return "documentation"
    if ext == ".scml":
        return "animation_data"
    if ext == ".gif":
        return "animation_preview"
    return pack_category


def load_visual_notes() -> dict:
    path = CATALOG_DIR / "visual_notes.json"
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def main():
    CATALOG_DIR.mkdir(exist_ok=True)

    visual_notes = load_visual_notes()
    if visual_notes:
        print(f"  Loaded visual_notes.json ({len(visual_notes)} entries)")

    packs = []
    all_assets = []

    pack_dirs = sorted([
        d for d in ART_DIR.iterdir()
        if d.is_dir() and d.name not in SKIP_DIRS and not d.name.startswith(".")
    ])

    for pack_dir in pack_dirs:
        pack_name = pack_dir.name
        ctx = PACK_CONTEXT.get(pack_name, {
            "description": f"{pack_name} asset pack",
            "category": "mixed",
            "style": "unknown",
            "usage": "General purpose",
            "tags": [pack_name],
        })

        files_by_ext = defaultdict(int)
        file_count = 0
        pack_assets = []

        for fpath in pack_dir.rglob("*"):
            if not fpath.is_file():
                continue
            ext = fpath.suffix.lower()
            if ext in SKIP_EXTS:
                continue

            files_by_ext[ext] += 1
            file_count += 1

            rel = fpath.relative_to(pack_dir).as_posix()
            tags = infer_tags_from_path(rel, ctx.get("tags", []))
            asset_type = get_asset_type(ctx.get("category", "mixed"), ext, fpath.name)

            record = {
                "pack": pack_name,
                "path": rel,
                "filename": fpath.name,
                "ext": ext,
                "type": asset_type,
                "tags": tags,
                "size_bytes": fpath.stat().st_size,
            }
            pack_assets.append(record)
            all_assets.append(record)

        pack_record = {
            "pack": pack_name,
            "description": ctx["description"],
            "category": ctx["category"],
            "style": ctx.get("style", ""),
            "usage": ctx.get("usage", ""),
            "tags": ctx.get("tags", []),
            "file_count": file_count,
            "file_types": dict(files_by_ext),
            "visual": visual_notes.get(pack_name, {}),
        }
        packs.append(pack_record)
        print(f"  {pack_name}: {file_count} files")

    # Write packs.json
    packs_path = CATALOG_DIR / "packs.json"
    with open(packs_path, "w", encoding="utf-8") as f:
        json.dump(packs, f, indent=2)
    print(f"\nWrote {packs_path} ({len(packs)} packs)")

    # Write assets.jsonl
    assets_path = CATALOG_DIR / "assets.jsonl"
    with open(assets_path, "w", encoding="utf-8") as f:
        for record in all_assets:
            f.write(json.dumps(record) + "\n")
    print(f"Wrote {assets_path} ({len(all_assets)} assets)")

    # Write GUIDE.md
    guide_path = CATALOG_DIR / "GUIDE.md"
    with open(guide_path, "w", encoding="utf-8") as f:
        f.write("# KroolWorld Art Asset Guide\n\n")
        f.write(f"**Total packs:** {len(packs)}  \n")
        f.write(f"**Total files:** {len(all_assets)}  \n\n")
        f.write("---\n\n")

        # Group by category
        by_cat = defaultdict(list)
        for p in packs:
            by_cat[p["category"]].append(p)

        for cat, cat_packs in sorted(by_cat.items()):
            f.write(f"## {cat.title()}\n\n")
            for p in cat_packs:
                v = p.get("visual", {})
                f.write(f"### `{p['pack']}/`\n")
                f.write(f"**{p['file_count']} files** | Style: {p['style']}  \n")
                f.write(f"{p['description']}  \n")
                f.write(f"**Usage:** {p['usage']}  \n")
                f.write(f"**Tags:** {', '.join(p['tags'])}  \n")
                ftypes = ", ".join(f"{ext}({n})" for ext, n in sorted(p["file_types"].items()))
                f.write(f"**File types:** {ftypes}  \n")
                if v:
                    f.write(f"**Art style:** {v.get('art_style', '')}  \n")
                    f.write(f"**Perspective:** {v.get('perspective', '')}  \n")
                    f.write(f"**Resolution:** {v.get('approx_resolution', '')}  \n")
                    f.write(f"**Palette:** {v.get('palette', '')}  \n")
                    if v.get('compatibility_group'):
                        f.write(f"**Compatibility group:** {v.get('compatibility_group')}  \n")
                    if v.get('notes'):
                        f.write(f"**Notes:** {v.get('notes')}  \n")
                f.write("\n")

    print(f"Wrote {guide_path}")


if __name__ == "__main__":
    print("Scanning packs...")
    main()
    print("\nDone.")
