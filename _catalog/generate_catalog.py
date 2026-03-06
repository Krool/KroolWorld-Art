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

SKIP_DIRS = {"_catalog", "Settings", "TutorialInfo"}
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
    "Area730": {
        "description": "Comprehensive game UI kit — sliced PNG components for buttons, bars, dialog boxes, icons, loading screens, menus, notifications, panels, progress bars, and sliders. Includes AI source files.",
        "category": "ui",
        "style": "stylized, modern",
        "usage": "Game UI — menus, HUD, dialog boxes, buttons, progress bars, notifications",
        "tags": ["ui", "button", "panel", "dialog", "menu", "hud", "bar", "slider", "icon", "notification"],
    },
    "Casual_Hit": {
        "description": "Casual hit/impact visual effect prefabs with textures. 4 hit variations in 4 color variants (blue, red, yellow, normal). Unity prefabs with materials and shaders.",
        "category": "effects",
        "style": "casual, cartoon",
        "usage": "Hit/impact particle effects, damage feedback, combat VFX",
        "tags": ["effect", "particle", "hit", "impact", "vfx", "casual", "unity"],
    },
    "FantasyBackgrounds": {
        "description": "6 painted fantasy background illustrations — Arctic, Dead Sea, Desert, Forest, Volcano, Wood. Includes PSD source file.",
        "category": "backgrounds",
        "style": "painted, fantasy",
        "usage": "Scene backgrounds, title screens, menu backgrounds, battle arenas",
        "tags": ["background", "painted", "fantasy", "environment", "scene"],
    },
    "FantasyIconsMegaPack": {
        "description": "Massive hand-drawn fantasy icon set with 2672+ icons across 13 categories: armor, weapons, potions, gems, food, herbs, loot, magic items, engineering/craft, and resources. Multiple color variants per icon. 256×256px with transparent backgrounds.",
        "category": "icons",
        "style": "hand-drawn, fantasy",
        "usage": "Inventory icons, loot, crafting menus, shops, item tooltips — comprehensive RPG icon coverage",
        "tags": ["icon", "ui", "weapon", "armor", "potion", "gem", "food", "crafting", "loot", "magic", "resource", "fantasy", "inventory"],
    },
    "FantasyInventoryIcons": {
        "description": "2300+ fantasy inventory item icons organized by equipment slot (armor, boots, belts, bows, capes, gloves, helmets, masks, shields, weapons, etc.) with themed variants (Knights, Samurai, Vikings, SandLords, SwampLords, Christmas). Includes sprite atlases, background plates, and UI frame components.",
        "category": "icons",
        "style": "stylized, fantasy",
        "usage": "Inventory system UI, equipment slots, item management, character loadout screens",
        "tags": ["icon", "inventory", "equipment", "armor", "weapon", "shield", "helmet", "ui", "fantasy", "rpg"],
    },
    "HeroEditor": {
        "description": "Comprehensive character customization system — Fantasy and Undead hero variants with body part customization (hair, eyes, ears, scars, facial hair), equipment icons across multiple themed sets, 39 animations (walk, run, jump, crouch, climb, combat), ranged weapon assets, and 54+ WAV sound effects. Includes C# inventory/shop system scripts.",
        "category": "characters",
        "style": "pixel art, fantasy",
        "usage": "Character creation/customization, RPG equipment systems, animated player/NPC sprites",
        "tags": ["character", "sprite", "animated", "customization", "equipment", "armor", "weapon", "fantasy", "undead", "rpg", "pixel", "sound"],
    },
    "RPG Unitframe #1": {
        "description": "RPG unit frame UI components — health/mana/energy bars, character portrait frames in 3 tiers (simple, half-elite, elite), level indicators, and frame masks. Includes PSD source.",
        "category": "ui",
        "style": "stylized, fantasy",
        "usage": "Player/NPC unit frames, health bars, portrait displays, party UI",
        "tags": ["ui", "unitframe", "healthbar", "portrait", "hud", "bar", "rpg", "fantasy"],
    },
    "Skill_Icon_Pack": {
        "description": "250+ skill/ability icons organized by color theme — blue, red, green, yellow, gray, emerald, violet — plus addon/modifier icons. Each color may represent a skill school or element.",
        "category": "icons",
        "style": "stylized, fantasy",
        "usage": "Skill trees, ability bars, spell icons, talent systems",
        "tags": ["icon", "skill", "ability", "spell", "ui", "fantasy", "rpg"],
    },
    "Universal Sound FX": {
        "description": "Massive professional sound effects library with 10,000+ mono WAV files across 75+ categories including: 8-bit retro, actions, ambiences, animals, battles, buttons, cartoon, construction, doors, electricity, explosions, foley, glass, gore, impacts, industrial, magic, mechanical, monsters, music stingers, nature, notifications, sci-fi, UI, vehicles, voices, water, weather, and more.",
        "category": "audio",
        "style": "professional, universal",
        "usage": "Game sound effects — UI, combat, environment, creatures, foley, ambient, everything",
        "tags": ["audio", "sfx", "sound", "wav", "ui", "combat", "ambient", "foley", "explosion", "impact", "creature", "environment"],
    },
    "Tiny RPG Character Asset Pack v1.03b -Full 20 Characters": {
        "description": "20 tiny pixel art RPG characters with full animation sets (idle, walk, attack, death, hurt, block, heal). Includes heroes (Knight, Archer, Wizard, Priest, Soldier, Swordsman, Lancer), enemies (Orc, Skeleton, Slime, Werebear, Werewolf), and variants. Provides shadow sprites, split VFX overlays, and projectile assets (arrows, magic). Includes Aseprite source files.",
        "category": "characters",
        "style": "pixel art, fantasy",
        "usage": "Side-view RPG battle characters, combat sprites, player and enemy characters",
        "tags": ["character", "sprite", "animated", "pixel", "fantasy", "rpg", "combat", "knight", "wizard", "orc", "skeleton", "side-view"],
    },
    "10k Game Assets": {
        "description": "Massive multi-category game asset pack by Chequered Ink — 10,000+ assets across pixel art (8-bit adventure, RPG characters/tilesets, inventory icons, retro monsters, control prompts), HD graphics (platformer, UI, 3D cars, dice, icons, puzzles, cards, board games, planets, particles), audio (792 WAV SFX across retro, arcade, RPG, and modern categories), fonts, and 3D vehicle models.",
        "category": "mixed",
        "style": "mixed — pixel art + HD illustrated",
        "usage": "General-purpose game assets — prototyping, game jams, full projects. Pixel art for retro/RPG games, HD graphics for modern/casual games, audio for any project",
        "tags": ["pixel", "hd", "character", "sprite", "tileset", "icon", "ui", "audio", "sfx", "platformer", "rpg", "retro", "font", "3d", "mixed"],
    },
    "Game Assets(2)": {
        "description": "Large pixel art fantasy RPG asset collection — Fantasy Dreamland tilesets/characters (16x16 tiles, 48x48 characters across 35 themed packs: grasslands, forest, desert, caves, castle, city, dungeon, village, interior, etc.), Pixel Battlers RPG monster sprites (12 monster packs with multiple animation states), Pixel VFX spell animations (fire, ice, light, buff/debuff), Platformer World tilesets (15 themed 16x16 platformer environments), and sound effects (footsteps, game SFX, sci-fi UI — MP3/OGG/WAV). RPG Maker MV/MZ compatible formats included.",
        "category": "mixed",
        "style": "pixel art, fantasy",
        "usage": "Fantasy RPG tilesets, character sprites, monster battlers, spell VFX, platformer tiles, sound effects",
        "tags": ["pixel", "rpg", "tileset", "character", "monster", "vfx", "platformer", "fantasy", "rpgmaker", "audio", "sfx"],
    },
    "Cute RPG Music Pack 1(1)": {
        "description": "5 cute/lighthearted RPG music tracks in MP3, OGG, and WAV formats. Loopable and non-loopable variants. Tracks: Adorable Adventures, Dreamy Dandelion, Sunny Symphony, Treasure Island, Waddlin' Away.",
        "category": "audio",
        "style": "cute, lighthearted",
        "usage": "Background music for cute/casual RPGs, overworld themes, town music, menus",
        "tags": ["audio", "music", "soundtrack", "rpg", "cute", "lighthearted", "loop", "mp3", "ogg", "wav"],
    },
    "Cute RPG Music Pack 2": {
        "description": "5 cute RPG music tracks in MP3, OGG, and WAV formats. Loopable and non-loopable variants. Tracks: City Stroll, Dreamy Days, Fluffy Cloudtops, Magical Forest, Seaside Lunch.",
        "category": "audio",
        "style": "cute, lighthearted",
        "usage": "Background music for cute/casual RPGs, town and exploration themes",
        "tags": ["audio", "music", "soundtrack", "rpg", "cute", "lighthearted", "loop", "mp3", "ogg", "wav"],
    },
    "Cute RPG Music Pack 3": {
        "description": "5 cute RPG music tracks in MP3, OGG, and WAV formats. Loopable and non-loopable variants. Tracks: Candy Bazaar, Cool Summer, Fantasy Prelude, Jazzberry Jam, Windowsill Cat.",
        "category": "audio",
        "style": "cute, lighthearted",
        "usage": "Background music for cute/casual RPGs, shop themes, exploration",
        "tags": ["audio", "music", "soundtrack", "rpg", "cute", "lighthearted", "loop", "mp3", "ogg", "wav"],
    },
    "Cute RPG Music Pack 4": {
        "description": "5 cute RPG music tracks in MP3, OGG, and WAV formats. Loopable and non-loopable variants. Tracks: Dazzling Bubbles, Otto's Shell Collection, Paw-some Stars, Sunny's Adventure, The Bear Boogie.",
        "category": "audio",
        "style": "cute, lighthearted",
        "usage": "Background music for cute/casual RPGs, adventure and overworld themes",
        "tags": ["audio", "music", "soundtrack", "rpg", "cute", "lighthearted", "loop", "mp3", "ogg", "wav"],
    },
    "Cute RPG Music Pack 5": {
        "description": "5 cute RPG music tracks in MP3, OGG, and WAV formats. Loopable and non-loopable variants. Tracks: Butterfly Hunt, Fireflies, In the Clouds, Spring Time, Way Back.",
        "category": "audio",
        "style": "cute, lighthearted",
        "usage": "Background music for cute/casual RPGs, nature and seasonal themes",
        "tags": ["audio", "music", "soundtrack", "rpg", "cute", "lighthearted", "loop", "mp3", "ogg", "wav"],
    },
    "Epic Medieval I Music Pack": {
        "description": "6 epic medieval/fantasy orchestral music tracks in MP3, OGG, and WAV formats. Tracks: Clear Waters, End of the Road, Fortified, Sewage, Theme, War.",
        "category": "audio",
        "style": "epic, orchestral, medieval",
        "usage": "Background music for medieval/fantasy RPGs — battle themes, exploration, menus",
        "tags": ["audio", "music", "soundtrack", "rpg", "medieval", "fantasy", "epic", "orchestral", "mp3", "ogg", "wav"],
    },
    "Epic Medieval II Music Pack": {
        "description": "5 epic medieval/fantasy orchestral music tracks in MP3, OGG, and WAV formats. Tracks: Endless Mountains, Fairy Forest, Memories, Valley Tribes, Warrior of the West.",
        "category": "audio",
        "style": "epic, orchestral, medieval",
        "usage": "Background music for medieval/fantasy RPGs — exploration, dramatic scenes",
        "tags": ["audio", "music", "soundtrack", "rpg", "medieval", "fantasy", "epic", "orchestral", "mp3", "ogg", "wav"],
    },
    "Epic Medieval III Music Pack(1)": {
        "description": "6 epic medieval/fantasy orchestral music tracks in MP3, OGG, and WAV formats. Includes vocal variants. Tracks: Awakening, Business As Usual, Frigg, Swords On Demand, Training Grounds, Frigg (No Vocals).",
        "category": "audio",
        "style": "epic, orchestral, medieval",
        "usage": "Background music for medieval/fantasy RPGs — battle, training, dramatic scenes",
        "tags": ["audio", "music", "soundtrack", "rpg", "medieval", "fantasy", "epic", "orchestral", "vocal", "mp3", "ogg", "wav"],
    },
    "Epic Medieval IV Music Pack": {
        "description": "6 epic medieval/fantasy orchestral music tracks in MP3, OGG, and WAV formats. Includes vocal variants. Tracks: Endless Peace, Fields Of War, Grand Palace, Grasslands (Vocals), The Horde, Grasslands (No Vocals).",
        "category": "audio",
        "style": "epic, orchestral, medieval",
        "usage": "Background music for medieval/fantasy RPGs — palace, war, peaceful exploration",
        "tags": ["audio", "music", "soundtrack", "rpg", "medieval", "fantasy", "epic", "orchestral", "vocal", "mp3", "ogg", "wav"],
    },
    "Epic Medieval V Music Pack": {
        "description": "7 epic medieval/fantasy orchestral music tracks in MP3, OGG, and WAV formats. Includes loopable variants. Tracks: A Forgotten Tale, Battlefield, Follow The Light, Hearth Fire, Reigentanz.",
        "category": "audio",
        "style": "epic, orchestral, medieval",
        "usage": "Background music for medieval/fantasy RPGs — battle, tavern, exploration",
        "tags": ["audio", "music", "soundtrack", "rpg", "medieval", "fantasy", "epic", "orchestral", "loop", "mp3", "ogg", "wav"],
    },
    "Farming RPG Music Pack 1": {
        "description": "6 pastoral/relaxing RPG music tracks in MP3, OGG, and WAV formats. Includes loopable variants. Tracks: Dragonfly, Fate, Good Morning, Seaside Promenade, Village.",
        "category": "audio",
        "style": "pastoral, relaxing",
        "usage": "Background music for farming/life sim games — village, morning, seaside themes",
        "tags": ["audio", "music", "soundtrack", "rpg", "farming", "pastoral", "relaxing", "loop", "mp3", "ogg", "wav"],
    },
    "Farming RPG Music Pack 2": {
        "description": "5 pastoral/relaxing RPG music tracks in MP3, OGG, and WAV formats. Loopable and non-loopable variants. Tracks: Cosy Island, Dusk Has Fallen, Falling Leaves, Stargazing, Up At Dawn.",
        "category": "audio",
        "style": "pastoral, relaxing",
        "usage": "Background music for farming/life sim games — evening, seasonal, nature themes",
        "tags": ["audio", "music", "soundtrack", "rpg", "farming", "pastoral", "relaxing", "loop", "mp3", "ogg", "wav"],
    },
    "Farming RPG Music Pack 3": {
        "description": "5 pastoral/relaxing RPG music tracks in MP3, OGG, and WAV formats. Loopable and non-loopable variants. Tracks: Nature's Serenity, Picnic Memories, Resting In The Hay, The Fruits Of Labour, Water Lily.",
        "category": "audio",
        "style": "pastoral, relaxing",
        "usage": "Background music for farming/life sim games — nature, harvest, peaceful themes",
        "tags": ["audio", "music", "soundtrack", "rpg", "farming", "pastoral", "relaxing", "loop", "mp3", "ogg", "wav"],
    },
    "Farming RPG Music Pack 4": {
        "description": "5 pastoral/relaxing RPG music tracks in MP3, OGG, and WAV formats. Loopable and non-loopable variants. Tracks: Fields of Tranquility, Harvest Festival, Homestead Harmony, Rise and Shine, Sunlit Meadows.",
        "category": "audio",
        "style": "pastoral, relaxing",
        "usage": "Background music for farming/life sim games — harvest, homestead, morning themes",
        "tags": ["audio", "music", "soundtrack", "rpg", "farming", "pastoral", "relaxing", "loop", "mp3", "ogg", "wav"],
    },
    "Farming RPG Music Pack 5": {
        "description": "5 pastoral/relaxing RPG music tracks in MP3, OGG, and WAV formats. Tracks: Dreams and Memories, Gramp's Still Got It, Lazy Afternoon, Moonlit Cruise, Woodland Melody.",
        "category": "audio",
        "style": "pastoral, relaxing",
        "usage": "Background music for farming/life sim games — evening, nostalgia, woodland themes",
        "tags": ["audio", "music", "soundtrack", "rpg", "farming", "pastoral", "relaxing", "mp3", "ogg", "wav"],
    },
    "32rogues": {
        "description": "32x32 pixel art roguelike tileset (v0.5.0) — 35 character classes, 28 monsters, 100+ items, animals, environment tiles, autotiles, animated tiles, and palette swap variants. Sprite sheets with individual frame documentation.",
        "category": "mixed",
        "style": "pixel art, roguelike",
        "usage": "Roguelike/dungeon crawler characters, monsters, items, environment tiles",
        "tags": ["character", "monster", "item", "tileset", "pixel", "roguelike", "sprite", "animated", "autotile", "32x32"],
    },
    "32rogues-0.4.0": {
        "description": "32x32 pixel art roguelike tileset (v0.4.0, older version) — characters, monsters, items, animals, environment tiles. Superseded by 32rogues v0.5.0 which adds autotiles, animated tiles, and palette swaps.",
        "category": "mixed",
        "style": "pixel art, roguelike",
        "usage": "Roguelike/dungeon crawler — use v0.5.0 instead unless you need the older version",
        "tags": ["character", "monster", "item", "tileset", "pixel", "roguelike", "sprite", "32x32"],
    },
    "CHARACTER MEGAPACK": {
        "description": "54 tiny pixel art RPG characters with full animation sets (ATK, Idle, Move, Dash, DashEnd). Includes heroes (Knight, Dwarfette, Wizard, Ranger, Ninja — 4 level variants each), enemies (Cyclops, Ent, Goblin, Mimic, Frog, Orc, Skeleton, Slime, Spider, Troll, Mushroom, Mummy, Scarecrow), and NPCs (GameMaster, Dummy). Individual frames + sprite sheet strips per animation.",
        "category": "characters",
        "style": "pixel art, fantasy, tiny",
        "usage": "Top-down RPG player characters, enemies, NPCs — extensive character variety with level progression variants",
        "tags": ["character", "sprite", "animated", "pixel", "fantasy", "rpg", "knight", "wizard", "goblin", "skeleton", "slime", "orc", "top-down"],
    },
    "SLIMES BLOBS TENTACLES": {
        "description": "Slime, blob, and tentacle enemy sprites in 12 color variants (green, cyan, blue, purple, pink, brown, red, dark green, yellow, orange, turquoise, weird purple). Each color has multiple slime levels with 4-directional attack, hit, idle, and move animations. Individual frames + sprite sheet strips.",
        "category": "characters",
        "style": "pixel art, fantasy, tiny",
        "usage": "RPG enemy sprites — slimes and blob creatures with color-coded variants for difficulty levels",
        "tags": ["character", "sprite", "animated", "pixel", "fantasy", "rpg", "monster", "slime", "enemy", "top-down"],
    },
    "RPG HEROES ENEMIES": {
        "description": "RPG hero and enemy character sprites organized by race — Humans, Orcs, Trolls, Demons, Weird Creatures — plus a bonus pseudo-Gameboy style set. Each character has ATK, Idle, Move, Hit, Dead animations. Individual frames + sprite sheet strips.",
        "category": "characters",
        "style": "pixel art, fantasy, tiny",
        "usage": "Top-down RPG heroes and enemies — multiple races and character types",
        "tags": ["character", "sprite", "animated", "pixel", "fantasy", "rpg", "human", "orc", "troll", "demon", "enemy", "hero", "top-down"],
    },
    "Orcs Goblins V2": {
        "description": "Orc and goblin character sprites V2 in 3 skin color variants (green, blue, red). Includes barrel goblins, regular goblins, orc warriors, and orc riders with full animation sets (ATK, Idle, Move, Hit, Dead). Individual frames + sprite sheet strips. Includes older V1 versions.",
        "category": "characters",
        "style": "pixel art, fantasy, tiny",
        "usage": "Top-down RPG orc and goblin enemies with color-coded variants",
        "tags": ["character", "sprite", "animated", "pixel", "fantasy", "rpg", "orc", "goblin", "enemy", "top-down"],
    },
    "OVERBURN AssetPack": {
        "description": "Fire and flame VFX sprite sheets in 4 color variants (yellow-orange, blue, green, purple). Includes flame animations, fireballs, orbs (top-down and isometric), shockwaves, flamethrower effects, realistic fire, and circle/square shaped flames at multiple sizes (32px, 48px, 64px, 96px). Bonus characters (Mage, Flamethrower). Includes PSD source files and preview GIFs.",
        "category": "effects",
        "style": "pixel art, VFX",
        "usage": "Fire spell effects, flame VFX, elemental abilities, torch/campfire animations",
        "tags": ["effect", "vfx", "fire", "flame", "spell", "pixel", "animated", "fireball", "particle"],
    },
    "ASTRONAUT AssetPack": {
        "description": "Pixel art astronaut character with 15 color variants (bicolor regular/variant, red, turquoise, green, yellow, orange, white, grey, pink, blue, purple, brown, salmon, black) plus bonus content. Full 8-directional animations: idle, run, jump, fall, dive, roll, land, turn. Both FullBody and DeadBody states. Sprite sheet format with direction/frame grids.",
        "category": "characters",
        "style": "pixel art, sci-fi",
        "usage": "Space game player characters, Among Us-style characters, sci-fi RPG, multiplayer color variants",
        "tags": ["character", "sprite", "animated", "pixel", "sci-fi", "space", "astronaut", "8-directional"],
    },
    "OVERSTELLAR AssetPack": {
        "description": "Space-themed VFX and environment sprite sheets — animated rotating planets (40+ including solar system replicas), animated suns/stars, asteroids, scrolling star backgrounds, black holes, celestial bodies (comets, nebulae), eclipses, galaxies, meteorites, shooting stars, glowing stars, and scrolling space backgrounds. Pre-rendered 3D-style on sprite sheet grids.",
        "category": "effects",
        "style": "pixel art, sci-fi, space",
        "usage": "Space game backgrounds, planet animations, celestial VFX, sci-fi environments, star fields",
        "tags": ["effect", "vfx", "space", "planet", "star", "galaxy", "asteroid", "background", "animated", "sci-fi", "pixel"],
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
