# KroolWorld Asset Style Guide

This document describes the visual styles present in the collection, which packs are
compatible with each other, and provides a template for defining the visual direction
of a specific project. Give this file to an LLM alongside GUIDE.md when making asset
decisions.

---

## Style Groups

The visual art packs fall into **5 distinct visual styles**. Mixing across groups will create
visual inconsistency. Within a group, packs are safe to combine.
Some packs are **style-independent** (UI kits, audio, VFX) and can be used with any group — see the end of this document.

---

### Group A — Pixel Art · Small Scale (16–32px)
*Classic 8-bit/16-bit RPG feel. Top-down. RPGMaker-compatible scale.*

| Pack | Notes |
|---|---|
| `medievalfantasycharacters` | Many character classes, full animation |
| `medievalrpgpack` | Quirky bird/creature characters |
| `rpggame1700plusicons` | 1700+ item/skill icons, RPGMaker sheet format |
| `rpginventoryiconsv1` | Inventory item icons |
| `rpgpixelweapons` | Dense weapon sprite sheet |
| `rpgsurvivalcharacter` | Survival character, full animations |
| `outdoorandforesttileset` | Forest tiles + animated chest |
| `pixelhouseandfurnies` | Interior furniture, animated fireplace |
| `snowforesttilesets` | Snow/ice tiles, animated chest |
| `HeroEditor` | Customizable fantasy/undead characters, equipment, animations |
| `Tiny RPG Character Asset Pack v1.03b -Full 20 Characters` | 20 tiny side-view battle characters (heroes + enemies), full animations |

**Palette:** Varied but generally muted/earthy or classic bright RPG colors
**Resolution:** 16–32px per tile/sprite
**Perspective:** Top-down, 4 or 8-directional; side-view for battle characters

---

### Group B — Pixel Art · Medium Scale (32–64px)
*More detailed pixel art. Top-down RPG overworld/interior.*

| Pack | Notes |
|---|---|
| `rpgbuildingshouses` | Buildings and furniture |
| `rpgworldsdecorativeprops` | Animated flags, decorative props |
| `rpgworldsgrassland` | Animated autumn trees, ground tiles |
| `rpgworldshousesandinteriors` | Interior props (crates, wells, shields) |
| `rpgworldsmarshland` | Dark swamp tiles, animated bubbles |
| `rpgworldssnowylands` | Snowy rocks, pine trees |
| `7soulsrpggraphics_cavetileset` | Dark cave tiles |
| `7soulsrpggraphics_dungeontileset` | Dungeon tiles, autotile support |
| `japantileset` | Soft pastel Japanese town tiles |

**Palette:** Muted/dark medieval for rpgworlds; pastel for japantileset
**Resolution:** 32–48px per tile
**Perspective:** Top-down orthographic
**Note:** The `rpgworlds*` packs are a cohesive family — use them together.

---

### Group C — Pixel Art · Large / Polished (48–64px+)
*Clean, modern pixel art with smooth curves. RPGMaker autotile format.*

| Pack | Notes |
|---|---|
| `tropicalislandgameassets` | Tropical ocean/island tiles, animated shore |
| `wintervillagegameassets` | Winter village buildings, animated doors |

**Palette:** Tropical: sandy tan + ocean blue. Winter: blue-grey + white
**Resolution:** 48–64px per tile
**Perspective:** Top-down, RPGMaker MV/MZ autotile format
**Note:** Both packs by the same creator (GDM). They share visual language but use different biomes.

---

### Group D — Stylized Cartoon / Illustrated
*Smooth vector-like art with thick outlines. Not pixel art.*

| Pack | Notes |
|---|---|
| `segel2dcharactersbundle` | Chibi characters, side-scroll, Spriter animation |
| `2dcutecharacterspack` | Chibi character parts (accessory, body, etc.) |
| `potionbottles` | Cartoon-style potion items |
| `swordsandshields` | Bold flat-shaded weapons |

**Palette:** Clean, saturated, bold
**Resolution:** 128–512px per asset
**Perspective:** Side-scrolling (characters) / flat icon (items)
**Note:** `segel2d` and `2dcutecharacters` share similar chibi aesthetics.
`potionbottles` and `swordsandshields` share bold outline / flat shading.

---

### Group E — Painted / Realistic
*High-detail digital painting. Best for UI — inventory, skill trees, dialogue.*

| Pack | Notes |
|---|---|
| `medievalskillandabilityicons` | Glowing icons on dark BG |
| `medievaltechnologyandskillicons` | Same style, crafting/tech focus |
| `rpgitemssetv3` | Painted armor/items with decorative border |
| `rpgweaponsv1` | Realistic weapon paintings, transparent BG |
| `rpgcharacterportraits` | Realistic portrait paintings, dark moody |

**Palette:** Dark backgrounds, metallic tones, dramatic lighting
**Resolution:** 128–512px per asset
**Perspective:** Flat icon or portrait bust
**Note:** All suit a "premium UI" look. `medievalskill` + `medievaltechnology` are a matched pair.
`rpgweaponsv1` is the odd one out (transparent BG, no dark frame) but still fits the painted aesthetic.
`FantasyBackgrounds` provides painted scene backgrounds (arctic, desert, forest, volcano, etc.).

---

### Group F — Hand-Drawn / Illustrated Icons
*High-detail hand-drawn icons. Not pixel art, not painted-realism. Distinct illustrated style.*

| Pack | Notes |
|---|---|
| `FantasyIconsMegaPack` | 2672+ icons across 13 categories, multiple color variants, 256px |
| `FantasyInventoryIcons` | 2300+ equipment slot icons with themed variants (Knights, Samurai, Vikings) |
| `Skill_Icon_Pack` | 250+ skill icons organized by color theme |

**Palette:** Varied — each pack has its own palette; color variants available
**Resolution:** 256px per icon (FantasyIcons), varied others
**Perspective:** Flat icon, front-facing
**Note:** These icon packs work as UI overlays with any style group, similar to Group E.
`FantasyIconsMegaPack` and `FantasyInventoryIcons` complement each other well (items vs. equipment slots).

---

### Style-Independent Packs
*These packs are not visual-style-specific and can be used alongside any style group.*

| Pack | Type | Notes |
|---|---|---|
| `Universal Sound FX` | Audio | 10,000+ WAV sound effects, 75+ categories |
| `Area730` | UI Kit | Sliced PNG components — buttons, bars, dialogs, menus, panels |
| `RPG Unitframe #1` | UI Kit | Unit frame components — health/mana bars, portrait frames |
| `Casual_Hit` | VFX | Hit/impact effect prefabs (Unity) with textures |

---

## Compatibility Quick Reference

```
COMPATIBLE COMBINATIONS
─────────────────────────────────────────────────────
Group A + Group B     Pixel RPG world (small chars, medium tiles)
Group B + Group C     Pixel RPG world (medium chars, polished tiles)
Group C only          Modern RPGMaker project
Group D only          Side-scroll adventure or chibi action game
Group E only          Premium UI layer (skill trees, inventory, portraits)
Group A/B + Group E   Pixel game world + premium UI layer (common combo)
Group A/B + Group F   Pixel game world + illustrated icon UI layer
Any + Style-Indep.    UI kits, audio, and VFX work with everything

AVOID MIXING
─────────────────────────────────────────────────────
Group A + Group C     Scale mismatch (16px chars on 64px tiles)
Group D + Group A/B   Pixel art world with cartoon characters (style clash)
Group E + Group D     Painted realism with thick-outline cartoon (style clash)
Group C + Group D     Polished pixel tiles with cartoon characters (scale/style clash)
Group E + Group F     Two different illustrated icon styles side-by-side (jarring)
```

---

## Project Visual Direction (Fill In)

Use this section to define the visual target for your specific game. An LLM can use
these decisions to recommend the right packs and flag incompatible assets.

```yaml
project:
  name: ""
  genre: ""           # e.g. RPG, platformer, adventure, survival

visual_target:
  style_group: ""     # A, B, C, D, E, or a specific combination
  perspective: ""     # top-down, side-scroll, isometric
  pixel_art: true     # or false
  tile_size: ""       # e.g. 32px, 48px

primary_packs:        # packs that define the visual identity
  - ""

supporting_packs:     # packs used for UI, items, supplemental content
  - ""

excluded_packs:       # packs confirmed NOT to be used
  - ""

palette_direction: "" # e.g. "dark and moody", "pastel and cute", "warm earthy"
tone: ""              # e.g. "serious medieval fantasy", "lighthearted adventure"
notes: ""
```

---

## Notes for LLMs

When recommending assets from this collection:

1. **Check the style group first** — never mix Group D (cartoon) characters with Group A/B (pixel) tilesets
2. **Check scale** — a 16px character on a 64px tile will look wrong
3. **The rpgworlds* packs are a family** — use them together, not individually mixed with unrelated tilesets
4. **tropicalislandgameassets + wintervillagegameassets** are sibling packs by the same creator — they share format and quality
5. **Group E packs are UI layers** — they overlay a game world, they don't define it
6. **segel2dcharactersbundle** uses Spriter skeletal animation (SCML files) — not frame-by-frame sprite sheets
7. **rpggame1700plusicons** is the most complete pixel icon set — use it first for pixel RPG inventory/UI
8. **FantasyIconsMegaPack** is the largest non-pixel icon set (2672+ items) — use it for illustrated/hand-drawn UI
9. **Universal Sound FX** has 10,000+ sound effects — check it first for any audio need
10. **Area730** and **RPG Unitframe #1** are UI kits — style-independent, usable with any visual group
11. **Casual_Hit** contains Unity prefabs — only useful in Unity projects
