# RM Module Schema Reference
## Proven Configurations & Patterns

This document records every material class, reagent type, product resolution mode,
building assignment, permission mode, and reaction pattern that has been tested and
confirmed working in the RM module system. Each entry includes the JSON schema
syntax and a reference to the test case that proved it.

All patterns below produce output indistinguishable from vanilla DF. No seams.

A reaction's code in the game is its module's prefix, RXN_, then its key
(refinish-module-react.lua): key GROG under prefix REFINISH_BRICK_ is
REFINISH_BRICK_RXN_GROG. A script that watches a reaction by code uses that
name; one written with the key alone never matches (seen 2026-10-04).

A category a reaction names is filed by id, and a reaction whose category the
world lacks is offered in no menu. MAKE_DYE is the one exception the engine
handles: when a mod has cut vanilla's Make dye, it files the reaction under a
Make dye of RM's own instead (seen and fixed 2026-10-04).

---

## MATERIAL CLASSES

Materials are defined in the materials JSON. Every material gets a `material_class`
that determines its flag preset (applied after the neutral reset blanks all flags).

### METAL
Produces bars. Full weapon/armor/anvil/furniture/building capability.
Flags set: IS_METAL, ITEMS_METAL, ITEMS_HARD, ITEMS_BARRED, ITEMS_SCALED,
ITEMS_WEAPON, ITEMS_WEAPON_RANGED, ITEMS_AMMO, ITEMS_DIGGER, ITEMS_ARMOR, ITEMS_ANVIL

```json
{
    "key": "ALLOY_ORICHALCUM",
    "name": "orichalcum",
    "material_class": "METAL",
    "color": "AMBER",
    "fallback_colors": ["DARK_GOLD", "ORANGE", "BRONZE"],
    "value": null,
    "solid_density": 8500, "liquid_density": 7600, "molar_mass": null,
    "heat": { "spec_heat": 395, "melting_point": 11900, ... },
    "strength": { "yield": {...}, "fracture": {...}, "strain_at_yield": null, "max_edge": 5500 },
    "gem_names": null, "reaction_classes": [], "reaction_products": [],
    "material_flags": {}, "inorganic_flags": {}
}
```
- `value: null` — auto-calculated from reaction reagents by making_metal.lua's weighted value system
- `reaction_classes: []` — explicitly empty, clears any donor classes
- `reaction_products: []` — explicitly empty, clears any donor products
- `material_flags: {}` — no overrides beyond the preset
- Test: All 13 alloys (shakudo through purple gold)

### STONE
Produces boulders. Buildable, makes furniture, quern stones.
Flags set: IS_STONE, ITEMS_HARD, ITEMS_QUERN

```json
{
    "key": "ITE_ITE",
    "name": "ite",
    "material_class": "STONE",
    "color": "TAUPE_DARK",
    "fallback_colors": ["BROWN", "DARK_BROWN"],
    "value": 2,
    ...
    "reaction_classes": [],
    "reaction_products": [
        { "id": "ITE_ite", "mat_id": "MAKING_METAL_CERAMIC_FIRED_ITE" }
    ],
    ...
}
```
- Stones with `reaction_products` can participate in `get_material_product` derivation
- The `id` field in reaction_products is the product code used by `has_material_reaction_product` on reagents
- `mat_id` must be the full prefixed ID of the target material
- `reaction_classes` can be set to enable reaction_class filtering on reagents (e.g., `["ITE_ITE"]`)
- Test: ITE_ITE (with FIRED_MAT linkage), ITE_ITE_ITE (calcined ite with reaction_class), ITE_SLAKED

### CERAMIC
Produced by firing/processing. Buildable, makes furniture. No weapon/armor capability.
Flags set: IS_CERAMIC, ITEMS_HARD

```json
{
    "key": "CERAMIC_FIRED_ITE",
    "name": "fired ite",
    "material_class": "CERAMIC",
    "color": "RUST",
    ...
}
```
- Ceramics are typically the product of a kiln reaction
- Test: CERAMIC_FIRED_ITE, ITE_CEMENT, ITE_RED_CEMENT, ITE_GREEN_CEMENT

### GEM
Produces rough gems. Can be cut at the jeweler's workshop via vanilla cut gem jobs.
Flags set: IS_GEM

```json
{
    "key": "ITE_GEM",
    "name": "ite crystal",
    "material_class": "GEM",
    "color": "CYAN",
    "fallback_colors": ["TEAL", "LIGHT_BLUE"],
    "value": 15,
    ...
    "gem_names": ["ite crystal", "ite crystals"],
    "reaction_classes": [], "reaction_products": [],
    "material_flags": {}, "inorganic_flags": {}
}
```
- `gem_names` is required: sets gem_name1 (singular) and gem_name2 (plural)
  for proper display in gem-related UI
- Produced rough gems appear and function in the jeweler's workshop —
  they can be processed via vanilla gem cutting jobs
- Test: ITE_GEM (boulder → rough ite crystals at jeweler)

### GLASS — Tested (with limitations)
Produces items marked as glass. Cuttable at jeweler. CANNOT make vanilla glass items.
Flags set: IS_GLASS, ITEMS_HARD

```json
{
    "key": "ITE_GLASS",
    "name": "ite glass",
    "material_class": "GLASS",
    "color": "LIGHT_BLUE",
    ...
}
```
- The GLASS class creates an inorganic material with IS_GLASS flag
- Clone donor fallback: CERAMIC (no vanilla IS_GLASS inorganics exist in
  unmodded worlds). The GLASS preset flips IS_CERAMIC→false, IS_GLASS→true.
- Module reactions CAN produce raw glass (ROUGH product) at the glass furnace
- Produced raw glass CAN be cut at the jeweler into finished glass gems
  (cabochons, etc.) — these function identically to vanilla cut gems
- **LIMITATION:** Vanilla glass crafting jobs (make window, goblet, blocks,
  etc.) are hardcoded to builtin mat_types 3/4/5 (GREEN/CLEAR/CRYSTAL glass).
  An IS_GLASS inorganic does NOT appear in these hardcoded job lists. There
  is no mechanism to extend this — see GLASS INVESTIGATION below.
- For seamless glass-as-gem (cutting rough glass at jeweler): fully functional
- For glass items (windows, goblets, crafts): not possible without seams
- Test: ITE_GLASS (calcined ite → rough glass at glass furnace → cut at jeweler)
- GLASS_FURNACE building confirmed working for custom module reactions

### RAW
No flags set or cleared. Clone's flags preserved as-is.
After neutral reset, ALL flags are false — modder must set everything via material_flags.
- Untested, available for full manual control scenarios

---

## REAGENT TYPES

Reagents are defined per-reaction in the reactions JSON.

### METAL_BAR — Specific metal bar
```json
{ "code": "copper_bars", "type": "METAL_BAR", "mat_id": "COPPER", "quantity": 450 }
```
- `mat_id` resolves to an inorganic index at build time
- Can reference vanilla metals or module-injected metals
- Test: All alloy reactions, DYE_CEMENT_RED (iron bar as pigment), FORGE_ITE_REINFORCEMENT

### ORE_OF — Any ore boulder that smelts to a specific metal
```json
{ "code": "zinc_ore", "type": "ORE_OF", "metal_id": "ZINC", "quantity": 1 }
```
- `metal_id` resolves to inorganic index, sets reagent.metal_ore
- DF matches any boulder whose metal_ore table contains that metal
- Test: FORGE_CALAMINE_BRASS (zinc ore input)

### COAL — Any coal bar (charcoal or coke)
```json
{ "code": "coal", "type": "COAL", "quantity": 150 }
```
- mat_type = 7 (COAL material class), mat_index = -1 (any)
- Test: FORGE_CRUCIBLE_STEEL

### BOULDER — Specific stone boulder
```json
{ "code": "ite_boulder", "type": "BOULDER", "mat_id": "MAKING_METAL_ITE_ITE", "quantity": 1 }
```
- Test: CUT_ITE_BLOCKS, FIRE_ITE_CERAMIC, GRIND_ITE_POWDER, CALCINE_ITE, RESMELT_ITE, FORGE_ITE_REINFORCEMENT

### BOULDER_ANY — Any inorganic boulder with magnifying glass selector
```json
{ "code": "any_stone", "type": "BOULDER_ANY", "quantity": 1, "flags": { "non_economic": true } }
```
- mat_type=0 (INORGANIC), mat_index=-1 (NONE) — this combination triggers the
  magnifying glass material selector, letting the player choose which boulder to use
- `flags.non_economic: true` accepts non-economic stones. See ECONOMIC STONE RULES below.
- Optional `reaction_class` override filters to specific material families:
```json
{ "code": "ite_stone", "type": "BOULDER_ANY", "quantity": 1, "reaction_class": "ITE_ITE", "flags": { "non_economic": true } }
```
- Optional `has_material_reaction_product` filter matches materials with a specific
  reaction_product entry (e.g., any clay with FIRED_MAT):
```json
{ "code": "clay", "type": "BOULDER_ANY", "quantity": 1, "has_material_reaction_product": "FIRED_MAT" }
```
- Magnifying glass confirmed working on filtered and unfiltered variants
- Test: TEST_GLASS_ANY_UNFILTERED, TEST_GLASS_ANY_FILTERED,
  CEMENT_CLINKER (clay via FIRED_MAT filter)

#### ECONOMIC STONE RULES
Materials with `reaction_product` entries (like FIRED_MAT on clay, or ore smelting
products) are considered ECONOMIC by DF. The `non_economic` reagent flag controls
which economic status is accepted:
- `non_economic: true` → accept ONLY non-economic stones (rejects clay, ores, flux)
- `non_economic: false` or omitted → accept economic stones (default after neutral reset)
- **CRITICAL:** Do NOT combine `non_economic: true` with `has_material_reaction_product`
  — they are contradictory. FIRED_MAT makes a stone economic, and non_economic rejects
  economic stones. The reaction will find no valid reagents.
- Vanilla inorganics with reaction_products: clays (FIRED_MAT), ores (metal smelting
  products), gypsum-family stones (ITE_ITE — plaster). These are all economic.

#### VANILLA MATERIAL IDENTITY NOTES
When referencing vanilla materials as reagents, match what exists in the player's
stockpile, not what a process chain could produce:
- GYPSUM (index 203) = the raw stone you mine. Grinder produces GYPSUM dust.
- PLASTER (index 26, displays as "gypsum plaster") = the product of MAKE_PLASTER_POWDER.
  These are DIFFERENT inorganics. GYPSUM dust ≠ PLASTER powder.
- QUICKLIME (index 32) = the product of MAKE_QUICKLIME. The source stones are
  LIMESTONE, MARBLE, etc. (have reaction_class CALCIUM_CARBONATE).

### FLUX — Any flux-bearing boulder
```json
{ "code": "flux", "type": "FLUX", "quantity": 1 }
```
- Matches boulders with reaction_class "FLUX" (limestone, marble, chalk, etc.)
- Available, not yet tested in a module reaction

### BLOCKS — Specific block item as reagent input
```json
{ "code": "cement_blocks", "type": "BLOCKS", "mat_id": "MAKING_METAL_ITE_CEMENT", "quantity": 1 }
```
- Blocks can be consumed as reagents, not just produced
- Test: DYE_CEMENT_RED, DYE_CEMENT_GREEN (cement blocks as input for coloring)

### POWDER — Powder/dust item, optionally specific material
```json
{ "code": "calcined_powder", "type": "POWDER", "mat_id": "MAKING_METAL_ITE_ITE_ITE", "quantity": 150, "flags": { "in_container": true } }
```
- With `mat_id`: resolves to specific inorganic powder
- Without `mat_id`: wildcard powder (any material)
- Must pair with `flags.in_container: true` and a BAG reagent with `contains` linkage
- Can reference vanilla materials by ID (e.g., "QUICKLIME")
- Test: MIX_ITE_CEMENT (both module and vanilla powder inputs), SLAKE_ITE

### BAG — Bag container for powders
```json
{ "code": "bag", "type": "BAG", "quantity": 1, "flags": { "preserve": true, "empty": true } }
```
- `flags.preserve: true` — bag is returned after reaction (PRESERVE_REAGENT)
- `flags.empty: true` — bag must be empty (flags1.empty). Required for powder OUTPUT.
- For powder INPUT, omit `empty` and add `contains` pointing to the powder reagent code:
```json
{ "code": "calcined_bag", "type": "BAG", "quantity": 1, "flags": { "preserve": true }, "contains": "calcined_powder" }
```
- Test: GRIND_ITE_POWDER (empty bag for output), MIX_ITE_CEMENT (contains bag for input)

### WATER — Water liquid
```json
{ "code": "water", "type": "WATER", "quantity": 150, "flags": { "in_container": true } }
```
- item_type 73 (LIQUID_MISC), mat_type 6 (builtin water), mat_index -1
- Must pair with `flags.in_container: true` and a BUCKET reagent with `contains` linkage
- Discovered via: `dfhack.matinfo.find('WATER')` → `<material 6:-1>`
- Test: SLAKE_ITE (quicklime + water → slaked ite)

### BUCKET — Bucket container for liquids
```json
{ "code": "water_bucket", "type": "BUCKET", "quantity": 1, "flags": { "preserve": true }, "contains": "water" }
```
- item_type 18 (df.item_type.BUCKET)
- PRESERVE_REAGENT returns the bucket after the liquid is consumed
- `contains` points to the liquid reagent code
- For producing liquid INTO a bucket, use `flags.empty: true` and `to_container` on the product
- Test: SLAKE_ITE (water input), DEBUG_MAKE_WATER (water output into bucket)
- NOTE: Do NOT use CONTAINER (item_type -1) — it's too generic and DF grabs bars/weapons

### BARREL — Barrel container for liquids. Tested.
```json
{ "code": "barrel", "type": "BARREL", "quantity": 1, "flags": { "preserve": true, "empty": true } }
```
- item_type 17 (df.item_type.BARREL)
- Works identically to BUCKET for liquid reactions
- Test: DEBUG_MAKE_WATER_BARREL (water produced into barrel)

### LIQUID — Generic liquid (non-water)
```json
{ "code": "lye", "type": "LIQUID", "quantity": 150, "flags": { "in_container": true } }
```
- item_type 73 (LIQUID_MISC), wildcard mat_type
- For specific liquids like lye (mat_type 11), mat_type would need explicit setting.
- Available, not yet tested.

### CONTAINER — Generic container (any item) — USE WITH CAUTION
- item_type -1 (any item)
- **WARNING:** Too generic. DF grabs metal bars, weapons, etc. Use BUCKET or BARREL instead.

### POWDER_ANY — Any inorganic powder (NO magnifying glass)
```json
{ "code": "dust", "type": "POWDER_ANY", "quantity": 150, "flags": { "in_container": true } }
```
- mat_type=0 (INORGANIC), mat_index=-1 (NONE)
- **MAGNIFYING GLASS DOES NOT WORK on POWDER_MISC.** Tested with both
  INORGANIC:NONE (mat_type=0, mat_index=-1) and NONE:NONE (mat_type=-1, mat_index=-1).
  Neither produces the material selector. This is a hard DF engine limitation that
  runtime injection cannot bypass. POWDER_MISC is not in DF's magnifying glass item
  type whitelist (only BAR, BLOCKS, BOULDER, ROUGH, SMALLGEM get it).
- The reaction functions correctly — the player just cannot select which powder.
  This is why RM's core finishing system uses per-material reactions and a category
  tree rather than a single reaction with a powder selector.
- Test: TEST_GLASS_POWDER (confirmed no magnifying glass with either mat_type)

### ROUGH — Rough gem as reagent input
- item_type 3, mat_type 0 (INORGANIC)
- Available, not yet tested as a reaction INPUT (tested as product output only)

### ROCK — Rock item as reagent input
- item_type 76
- Available, not yet tested as a reaction INPUT (tested as product output only)

---

## PRODUCT RESOLUTION MODES

Each product in a reaction must use exactly one material source.

### Mode 1: Direct mat_id
```json
{ "type": "BAR", "mat_id": "MAKING_METAL_ALLOY_ORICHALCUM", "count": 3, "dimension": 150 }
```
- Resolves mat_id to inorganic index at build time
- Can reference vanilla materials: `"mat_id": "IRON"` works
- For non-inorganic products (water), mat_id won't resolve in the inorganic
  lookup — mat_index defaults to -1, mat_type comes from the product type definition
- Test: All alloy products, RESMELT_ITE (vanilla IRON), DEBUG_MAKE_WATER (water)

### Mode 2: get_material_same — Inherit from reagent
```json
{ "type": "BLOCKS", "get_material_same": "ite_boulder", "count": 4, "dimension": 150 }
```
- Output material = input reagent's material
- The string value is the reagent code to inherit from
- Test: CUT_ITE_BLOCKS (blocks inherit ite), GRIND_ITE_POWDER (powder inherits ite)

### Mode 3: get_material_product — Derive from reagent's reaction_product
```json
{ "type": "BLOCKS", "get_material_product": { "reagent_code": "ite_boulder", "product_code": "ITE_ite" }, "count": 4, "dimension": 150 }
```
- Looks up the reagent's material, finds its reaction_product with matching product_code
- Uses THAT material for the output
- Requires the reagent to also have `has_material_reaction_product` set
- The material definition must have a matching reaction_products entry
- Test: FIRE_ITE_CERAMIC (ite boulder → fired ite blocks via ITE_ite product code)

### Product options
- `count` — number of items produced (default 1)
- `dimension` — item dimension (default 150)
- `probability` — percentage chance of production (default 100).
  Test: FORGE_CRUCIBLE_STEEL has probability:25 on ite boulder byproduct
- `to_container` — reagent code of the container to place product in.
  Works for both powders (→ bag) and liquids (→ bucket).
  Test: GRIND_ITE_POWDER (powder → bag), DEBUG_MAKE_WATER (water → bucket)
- `force_edge` — FORCE_EDGE flag. Produces edged/sharp items usable as cutting tools.
  Test: KNAP_ITE (ite boulder → sharp ite rocks with edges)

---

## PRODUCT TYPES

- `BAR` — Metal/inorganic bar (item_type 0, mat_type 0). **Tested.**
- `BAR_COAL` — Coal bar (item_type 0, mat_type 7). Untested as product.
- `BLOCKS` — Stone/ceramic blocks (item_type 2, mat_type 0). **Tested.**
- `ROUGH` — Rough gem / uncut glass (item_type 3, mat_type 0). **Tested.** (CUT_ITE_GEMS)
- `BOULDER` — Boulder (item_type 4, mat_type 0). **Tested.** (FORGE_CRUCIBLE_STEEL byproduct, SLAKE_ITE)
- `LIQUID_MISC` — Liquid (item_type 73, mat_type 6 for water). **Tested.** (DEBUG_MAKE_WATER)
- `POWDER_MISC` — Powder (item_type 70, mat_type 0). **Tested.** (GRIND_ITE_POWDER, CALCINE_ITE)
- `ROCK` — Rock item (item_type 76). **Tested with FORCE_EDGE.** (KNAP_ITE)

---

## BUILDINGS

### Furnaces (building_type 5) — normal + magma variants
- `SMELTER` — subtypes 1/4. Gate: StrangeMoodForge/StrangeMoodMagmaForge (mood). **Tested.**
- `GLASS_FURNACE` — subtypes 2/5. Gate: GLASSMAKER (permitted_job). **Tested.**
- `KILN` — subtypes 3/6. Gate: StrangeMoodMason (mood). **Tested.**

### Workshops (building_type 13) — single or normal+magma
- `MASON` — subtype 2. Gate: MASON (permitted_job). **Tested.**
- `CRAFTSMAN` — subtype 3 (NOT 0, which is Carpenter). Gate: STONECRAFTER/WOODCRAFTER/BONE_CARVER. **Tested.**
- `JEWELER` — subtype 4. Gate: JEWELER/GEM_CUTTER/GEM_SETTER. **Tested.**
- `FORGE` — subtypes 5/6. Gate: StrangeMoodForge/StrangeMoodMagmaForge (mood). **Tested.**
- `NONE` — no building (adventure mode). Untested.

### Building source reference
- Furnace subtypes: `df.furnace_type` enum
- Workshop subtypes: `df.workshop_type` enum

---

## SKILLS

Skills are assigned per-reaction via the `skill` field.
Values sourced from `df.job_skill` enum.

### Tested
- `SMELT` (24) — smelter reactions
- `POTTERY` (109) — kiln reactions
- `MASONRY` (4) — mason workshop reactions
- `STONECRAFT` (32) — craftsman workshop reactions
- `FORGE_FURNITURE` (28) — forge reactions (blacksmithing)
- `GEM_CUTTING` (29) — jeweler workshop reactions
- `KNAPPING` (105) — craftsman workshop reactions
- `GLASSMAKER` (34) — glass furnace reactions

### Available but untested
- `FORGE_WEAPON` (26), `FORGE_ARMOR` (27)
- `GEM_SETTING` (30)
- `METALCRAFT` (33), `WOODCRAFT` (31)
- `BONECARVE` (36), `LEATHERWORK` (35)
- `SOAP_MAKING` (65), `MILLING` (16)
- `CUT_STONE` (135), `CARVE_STONE` (136)
- `WEAVING` (13), `CLOTHESMAKING` (15), `STRAND_EXTRACT` (25)
- `CARPENTRY` (2)

---

## PERMISSION MODES

### AUTO — Evaluate all civilizations
```json
"permissions": { "mode": "AUTO" }
```
- Every civ that passes both gates (building capability + reagent metal knowledge) gets the permit
- Default if permissions block is omitted
- Test: All standard alloy reactions, all stone/ceramic reactions

### ENTITY_CODE — Target specific civilizations
```json
"permissions": { "mode": "ENTITY_CODE", "entities": ["MOUNTAIN"] }
```
- Only named entity_raw codes are evaluated
- Both gates still apply
- Works with any entity_raw.code — vanilla or modded
- Test: FORGE_ORICHALCUM (MOUNTAIN only), FORGE_GOBLIN_IRON (EVIL only)

### NONE — No permits to any civilization
```json
"permissions": { "mode": "NONE" }
```
- Reaction only accessible if fortress_mode is true
- Test: FORGE_PURPLE_GOLD
- A permit a script adds after load is not enough: the mineral dyes, injected
  with NONE and permitted to every civilisation in play, were in the
  civilisation's permitted list and still offered in no menu (2026-10-04).
  Permitted at load (AUTO), the same reactions were offered. Why is not
  measured; until it is, a reaction the player should see is permitted at load.

### Fortress mode flag
```json
"reaction_flags": { "fortress_mode": true }
```
- Makes reaction available to the player regardless of civ permits
- Default: false
- Test: FORGE_PURPLE_GOLD, FORGE_ITE_REINFORCEMENT

---

## PROVEN REACTION PATTERNS

### Simple alloy (smelter)
Input: metal bars → Output: alloy bars
Building: SMELTER, Skill: SMELT, Fuel: yes
Example: FORGE_SHAKUDO (copper + gold → shakudo)

### Alloy with ore input
Input: ore boulder + metal bars → Output: alloy bars
Uses ORE_OF reagent type with metal_id
Example: FORGE_CALAMINE_BRASS (zinc ore + copper → calamine brass)

### Multi-product with probability
Input: metal bars + coal → Output: primary bars + secondary boulder at X%
Example: FORGE_CRUCIBLE_STEEL (steel + nickel + coal → crucible steel bars + ite boulder@25%)

### Stone block cutting (mason)
Input: specific boulder → Output: blocks (material inherited from input)
Uses get_material_same product mode
Building: MASON, Skill: MASONRY, Fuel: no
Example: CUT_ITE_BLOCKS

### Ceramic firing via reaction_product derivation (kiln)
Input: boulder with reaction_product linkage → Output: derived material blocks
Uses get_material_product + has_material_reaction_product on reagent
Building: KILN, Skill: POTTERY, Fuel: yes
Example: FIRE_ITE_CERAMIC (ite boulder → fired ite blocks via ITE_ite code)

### Powder grinding into bag (mason)
Input: boulder + empty bag → Output: powder in bag (material inherited)
Uses get_material_same + to_container + empty bag flag
Building: MASON, Skill: MASONRY, Fuel: no
Example: GRIND_ITE_POWDER

### Kiln powder production (calcination)
Input: boulder + empty bag → Output: specific powder in bag
Uses direct mat_id on product + to_container
Building: KILN, Skill: POTTERY, Fuel: yes
Example: CALCINE_ITE (ite boulder → calcined ite powder)

### Slag re-smelting (stone to metal conversion)
Input: module stone boulders → Output: vanilla metal bars at probability
Reverse direction: stone input → metal output
Building: SMELTER, Skill: SMELT, Fuel: yes
Example: RESMELT_ITE (3 ite boulders → 1 iron bar@50%)

### Multi-powder cement mixing (complex reagent chain)
Input: two different powders in bags → Output: novel building material blocks
Uses POWDER reagent with IN_CONTAINER + BAG with contains linkage (×2)
References both module material AND vanilla material as powder reagents
Building: KILN, Skill: POTTERY, Fuel: no
Example: MIX_ITE_CEMENT (calcined ite powder + quicklime powder → cement blocks)

### Colored material finishing (craftsman)
Input: blocks + metal bar (as pigment) → Output: colored variant blocks
Uses BLOCKS as reagent input + METAL_BAR for color source
Building: CRAFTSMAN, Skill: STONECRAFT, Fuel: no
Example: DYE_CEMENT_RED (cement blocks + iron bar → red cement blocks)
Example: DYE_CEMENT_GREEN (cement blocks + copper bar → green cement blocks)

### Forge reinforcement (mixed material smithing)
Input: metal bars + stone boulder → Output: alloy bars
Metal + non-metal inputs combined at the forge
Building: FORGE, Skill: FORGE_FURNITURE, Fuel: yes
Example: FORGE_ITE_REINFORCEMENT (iron bars + ite boulder → goblin iron bars)

### Liquid reaction (slaking — water as reagent)
Input: powder in bag + water in bucket → Output: boulders
Uses WATER reagent (item_type 73, mat_type 6) with IN_CONTAINER flag
Paired with BUCKET reagent (item_type 18) with contains linkage
Container is preserved, liquid is consumed
Building: KILN, Skill: POTTERY, Fuel: no
Example: SLAKE_ITE (quicklime powder + water → slaked ite boulders)

### Liquid production (water into bucket)
Input: any reagent + empty bucket → Output: liquid routed into preserved bucket
Uses LIQUID_MISC product type (item_type 73, mat_type 6)
Product uses to_container pointing to a BUCKET reagent with empty flag
Building: KILN (debug), Skill: POTTERY, Fuel: no
Example: DEBUG_MAKE_WATER (ite boulder + empty bucket → water in bucket)

### Any-boulder processing with magnifying glass (mason)
Input: any inorganic boulder (player selects via magnifying glass) → Output: blocks
Uses BOULDER_ANY (mat_type=0, mat_index=-1) + get_material_same
Player clicks magnifying glass to choose which stone to process
Building: MASON, Skill: MASONRY, Fuel: no
Example: TEST_GLASS_ANY_UNFILTERED (any boulder → blocks, glass confirmed)

### Filtered boulder processing with magnifying glass (mason)
Input: any boulder matching a reaction_class → Output: blocks
Uses BOULDER_ANY + reaction_class override + non_economic flag
Magnifying glass shows ONLY materials with the matching reaction_class
Building: MASON, Skill: MASONRY, Fuel: no
Example: TEST_GLASS_ANY_FILTERED (ITE_ITE class only → blocks, glass confirmed)

### Gem cutting (jeweler)
Input: specific stone boulder → Output: rough gems
Uses ROUGH product type + GEM class material with gem_names
Produced gems function in vanilla jeweler cut/encrust jobs
Building: JEWELER, Skill: GEM_CUTTING, Fuel: no
Example: CUT_ITE_GEMS (ite boulder → 3 rough ite crystals)

### Knapping with edge (craftsman)
Input: specific stone boulder → Output: edged rock items (sharp rocks)
Uses ROCK product type + force_edge: true flag
Produces usable cutting implements, not crafts
Building: CRAFTSMAN, Skill: KNAPPING, Fuel: no
Example: KNAP_ITE (ite boulder → 2 sharp ite rocks)

### Glass production (glass furnace)
Input: powder in bag → Output: raw glass (ROUGH)
Uses ROUGH product type + GLASS class material (IS_GLASS + ITEMS_HARD)
Produced raw glass can be cut at the jeweler into finished glass gems
Building: GLASS_FURNACE, Skill: GLASSMAKER, Fuel: yes
Example: FUSE_ITE_GLASS (calcined ite powder → rough ite glass)
NOTE: Vanilla glass crafting jobs (windows, goblets) do NOT recognize
module-injected glass. See GLASS INVESTIGATION in technical notes.

### Liquid production into barrel
Input: any reagent + empty barrel → Output: liquid in barrel
Same pattern as bucket but with BARREL (item_type 17) instead
Building: KILN (debug), Skill: POTTERY, Fuel: no
Example: DEBUG_MAKE_WATER_BARREL (ite boulder + empty barrel → water in barrel)

### Stone → modded metal (full conversion)
Input: module stone boulders + coal → Output: module metal bars
Complete material class conversion: STONE input → METAL output
Building: SMELTER, Skill: SMELT, Fuel: yes
Example: REFINE_ITE_METAL (4 ite boulders + coal → refined ite bars)

### Powder magnifying glass test (FAILED — hard DF limitation)
Attempted: specific metal bar + any powder (POWDER_ANY) → alloy bars
Tested POWDER_MISC with both INORGANIC:NONE and NONE:NONE mat tokens
Neither configuration produces the magnifying glass material selector
This is a hard DF engine limitation — POWDER_MISC is not in the engine's
whitelist for the material selector UI. Runtime injection does not bypass this.
Building: SMELTER, Skill: SMELT, Fuel: yes
Example: TEST_GLASS_POWDER (confirmed: no magnifying glass on powder reagent)

### Full industrial chain: cement production (multi-stage)
A complete industrial prototype using vanilla and module materials across
multiple workshops. Each intermediate stage produces something independently
useful (buildable stone/ceramic), so the chain rewards the player at every step.

Stage 1 — SLAKING (Kiln): vanilla quicklime powder + water in bucket
  → slaked lime boulders. Buildable stone. Uses vanilla QUICKLIME reagent.
Stage 2 — CLINKERING (Kiln, fuel): slaked lime boulder + any clay boulder
  → clinker boulders. Superior building stone. Clay matched via
  has_material_reaction_product:"FIRED_MAT" filter (matches kaolinite,
  fire clay, and any FIRED_MAT-bearing material).
Stage 3 — GRINDING (Mason): clinker boulder + empty bag → clinker powder.
Stage 4 — DRY MIXING (Mason): clinker powder + vanilla gypsum powder
  + empty bag → raw cement powder. Three bags total (two in, one out).
  Uses vanilla GYPSUM (index 203) NOT PLASTER (index 26). Important
  distinction — see VANILLA MATERIAL IDENTITY NOTES above.
Stage 5a — SET BLOCKS (Mason): cement powder + water → portland cement blocks.
Stage 5b — CAST BOULDERS (Mason): cement powder + water → portland cement boulders.
Stage 6 — COLORING (Craftsman): portland blocks + metal bar pigment → colored blocks.

Key design principles demonstrated:
- Every intermediate is independently useful (not just a pass-through)
- Vanilla materials as reagents (QUICKLIME, GYPSUM, IRON, SILVER, clay)
- Multi-workshop chain (kiln → mason → craftsman)
- Branching at Stage 5 (blocks vs boulders from same input)
- Branching at Stage 6 (color variants via different pigments)
- Liquid reagents at multiple points (slaking, setting)

Color variant limitation: each color requires a separate material definition
in the JSON. There is no mechanism to dynamically recolor a material based on
reagent input — a material has one fixed color set at injection time. DF's dye
system only applies to cloth, not stone/ceramic. Color variants must be
pre-defined as distinct materials with distinct reactions.

---

## CURRENT TEST CONTENT SUMMARY

### Materials (29)
- 14 METAL alloys (13 original + refined ite)
- 3 STONE (ite, calcined ite, slaked ite) — ite prototype chain
- 4 CERAMIC (fired ite, ite cement, red ite cement, green ite cement) — ite prototype chain
- 1 GEM (ite crystal)
- 1 GLASS (ite glass)
- 3 STONE (slaked lime, clinker, raw cement) — cement industry chain
- 3 CERAMIC (portland cement, red portland, white portland) — cement industry chain

### Reactions (40)
- 13 smelter alloys (various permission modes: AUTO, ENTITY_CODE, NONE)
- 3 mason (cut blocks, grind powder, magnifying glass unfiltered test)
- 4 kiln processing (fire ceramic, calcine, slake, magnifying glass filtered test)
- 1 kiln mixing (ite cement — dual powder-in-bag inputs)
- 2 craftsman coloring (red/green ite cement blocks)
- 1 craftsman knapping (sharp ite rocks with FORCE_EDGE)
- 1 jeweler (gem cutting — ite crystals)
- 1 glass furnace (fuse ite glass)
- 1 forge (reinforcement — mixed metal+stone → alloy)
- 1 smelter re-smelting (slag → vanilla iron@50%)
- 1 smelter refining (slag → modded metal)
- 1 smelter test (powder magnifying glass — confirmed no glass)
- 2 debug (water into bucket, water into barrel — REMOVE before release)
- 8 cement industry (slake, clinker, grind, mix, set blocks, cast boulders, dye red, dye white)

### 10 Categories
ROOT, ALLOYS, STEEL, EXOTIC, STONE, MASONRY, CRAFTS, SMITHING, GLASS, CEMENT

### Full proven processing chains
- Crucible steel smelting → ite slag boulder (byproduct@25%)
  → calcine at kiln → calcined ite powder in bag
  + vanilla quicklime powder in bag → mix at kiln → ite cement blocks
  → craft at craftsman + iron/copper bar → colored cement blocks
- Ite boulder + water in bucket → slaked ite (liquid reagent chain)
- Ite boulder + water in barrel → same pattern, barrel confirmed
- 3 ite boulders → re-smelt at smelter → vanilla iron bar@50% (reverse conversion)
- 4 ite boulders + coal → refine at smelter → modded refined ite bars (class conversion)
- Ite boulder → cut at jeweler → rough ite crystals (gem production)
- Ite boulder → knap at craftsman → sharp edged ite rocks (tool production)
- Iron bars + ite boulder → forge → goblin iron bars (mixed material smithing)
- Calcined ite powder → fuse at glass furnace → rough ite glass → cut at jeweler
  → finished glass gems (glass-as-gem chain)
- CEMENT INDUSTRY: vanilla limestone → vanilla MAKE_QUICKLIME → quicklime powder
  + water → slaked lime boulders + clay → clinker boulders → grind to powder
  + gypsum powder → dry mix to cement powder + water → portland cement blocks/boulders
  → craft with pigment → colored cement blocks

---

## TECHNICAL NOTES

### Reagent/product neutral reset
After cloning reagents and products from the template via assign(), ALL semantic
flags are zeroed before rebuilding from the schema definition. This is the same
philosophy as the material neutral reset — clone for C++ structure, clear for
semantics, rebuild from schema.

Reagents: flags1.whole=0, flags2.whole=0, flags3.whole=0, flags4=0, flags5=0,
has_tool_use=-1, dye_color=-1. This prevents stale template constraints from
leaking through — e.g., a creature body part template would have flags2.body_part=true,
flags1.unrotten=true, making our boulder reagent reject everything except body parts.

Products: All 9 named flags set to false (GET_MATERIAL_SAME, GET_MATERIAL_PRODUCT,
FORCE_EDGE, PASTE, PRESSED, CRAFTS, USE_FULL_REACTION_PRODUCT_CLASS,
USE_REAGENT_ITEM, TRANSFER_ARTIFACT_STATUS). get_material linkage cleared.
product_to_container cleared. This prevents the CRAFTS flag from making the
reaction produce random crowns/earrings instead of our specified product type.

### Magnifying glass (material selector) rules
The magnifying glass icon appears next to a job in the workshop queue, allowing the
player to select which specific material to use for a reagent.

WORKS — these item types show the glass with INORGANIC:NONE (mat_type=0, mat_index=-1):
  BAR, BLOCKS, BOULDER, ROUGH, SMALLGEM
Confirmed via runtime injection: BOULDER_ANY with and without reaction_class filter.

DOES NOT WORK — POWDER_MISC (item_type 70):
  Tested with both INORGANIC:NONE (mat_type=0) and NONE:NONE (mat_type=-1).
  Neither configuration produces the selector. This is a hard DF engine limitation
  that runtime injection cannot bypass. POWDER_MISC is simply not in the engine's
  whitelist for the material selector UI.

This limitation is why RM's core finishing system uses per-material reactions and
a category tree rather than a single reaction with a powder selector. The magnifying
glass works for reactions where the player selects a BOULDER, BAR, or BLOCK input,
but not for powder/dust inputs.

Source: DF wiki material token table + empirical testing.

### vector<string*> requires pointer allocation
DF's C++ bindings reject raw Lua strings for vector<string*> fields.
Must use: `local s = df.new('string'); s.value = str; vec:insert('#', s)`
Affects: material.reaction_class, material.reaction_product.id

### Neutral reset
After cloning a donor via assign(), ALL semantic fields are reset to builtin
neutral values before schema overrides apply. This prevents donor-specific
state from leaking (hardens_with_water, NO_STONE_STOCKPILE, ITEMS_QUERN,
metal_ore, environment, economic_uses, syndromes, sphere, etc.)

### Display names cover all 6 states
Solid, Liquid, Gas, Powder, Paste, Pressed — all set to prevent donor name leaks.
RM's dust naming system handles " dust" suffix separately.

### Colors cover all 6 state_color entries
Same pattern — all 6 states set to prevent donor color leaks.

### Permission gate types
- Mood gates (SMELTER, KILN, FORGE): resolve via df.job_type enum → numeric index
- Permitted_job gates (MASON, CRAFTSMAN, JEWELER, GLASS_FURNACE): direct named field
  access on entity_raw.jobs.permitted_job struct
- These are two different access patterns — do not mix them.

### Template scoring
The reaction builder scores existing reactions to find a structural donor.
Non-smelter reactions may match to unusual templates (creature reactions, dye reactions)
because few vanilla reactions use mason/craftsman workshops with matching shapes.
The reagent/product neutral reset (see above) mitigates the primary danger here —
stale flags like body_part, unrotten, CRAFTS no longer leak through from the template
donor. The structural donor is still suboptimal in terms of raw_strings and other
cosmetic fields, but functionally the reaction works correctly regardless of which
template was selected. Consider adding explicit fallback_template values for
non-smelter building types if cosmetic purity is desired.

### CONTAINER (item_type -1) is too generic
Do NOT use the CONTAINER reagent type for new liquid reactions. With item_type = -1,
DF will grab any item (including metal bars, weapons) as a "container." The vanilla
soap reaction uses item_type -1 for its lye container, but that works because
the lye is already inside — DF matches on the contained item, not the container.
For new reactions needing an empty container, use BUCKET (18) or BARREL (17).

### Water material identity
Water is mat_type 6, mat_index -1. Not an inorganic — builtin material type.
Discovered via `dfhack.matinfo.find('WATER')` → `<material 6:-1>`.

### Vanilla quicklime exists
QUICKLIME is vanilla inorganic index 32. MAKE_QUICKLIME is vanilla reaction 116.
Don't duplicate — use vanilla quicklime as a reagent in module reactions.

### No vanilla lye/potash reactions or inorganics
Lye and potash have no detectable reaction definitions or inorganic entries.
Likely hardcoded engine-side or CREATURE_MAT/PLANT_MAT types.

### economic_uses not populated on injected materials
Uses sheet shows flag-derived uses but not reaction-derived uses.
Vanilla populates economic_uses at raws parse time; runtime injection skips that.
Cosmetic for metals, relevant for stones.

### Entity permissions don't persist across data cycles
Known outstanding issue. Reaction index shifting during data cycles causes
permission entries to point at wrong reactions.

---

## GLASS INVESTIGATION — DEFINITIVE FINDINGS

### Builtin material table structure
Vanilla glass types (GREEN_GLASS, CLEAR_GLASS, CRYSTAL_GLASS) are stored as
builtin material objects in `df.global.world.raws.mat_table.builtin`, NOT as
inorganic entries. They occupy mat_type indices 3, 4, 5 respectively.

The full builtin index order (from df.builtin_mats enum):
  0=INORGANIC, 1=AMBER, 2=CORAL, 3=GLASS_GREEN, 4=GLASS_CLEAR,
  5=GLASS_CRYSTAL, 6=WATER, 7=COAL, 8=POTASH, 9=ASH, 10=PEARLASH,
  11=LYE, 12=MUD, 13=VOMIT, 14=SALT, 15=FILTH_B, 16=FILTH_Y,
  17=UNKNOWN_SUBSTANCE, 18=GRIME, 19+=CREATURE/PLANT/HF entries (nil except one each),
  619+=UNUSED01-UNUSED40 (nil until vivified)

### Builtin slots are writable
Existing builtin material properties can be modified at runtime:
  `df.global.world.raws.mat_table.builtin.GLASS_GREEN.state_name.Solid = "test"`
This is confirmed working — names, flags, colors, heat, strength all writable.

### Nil builtin slots can be vivified
The 40 UNUSED slots (UNUSED01-UNUSED40) start as nil pointers. They can be
brought to life using DFHack's table assignment auto-vivification:
  `df.global.world.raws.mat_table.builtin.UNUSED01 = { new = true }`
This allocates a fresh material object at the nil pointer. The resulting
object is fully functional with all fields initialized to zero/empty.
Flags can then be set manually (assign() does not copy flags on builtins).

### Glass furnace jobs are hardcoded to indices 3/4/5
The vanilla glass crafting jobs (make window, goblet, blocks, crafts, etc.)
are NOT reaction objects — they are engine-internal hardcoded jobs with no
reaction entry in the reactions array. They check for mat_types 3, 4, 5
(GREEN_GLASS, CLEAR_GLASS, CRYSTAL_GLASS) specifically.

A vivified UNUSED01 at index 619 with IS_GLASS=true and ITEMS_HARD=true
does NOT appear in any glass furnace crafting job. The engine does not
iterate builtins looking for IS_GLASS — it checks exactly three indices.

No count, bounds, or range variable was found in mat_table that could
extend the glass type range. The glass indices are sandwiched between
CORAL (2) and WATER (6) with no gaps.

### IS_GLASS on inorganic materials
An inorganic material with IS_GLASS=true (as used by mods like cobalt glass)
behaves as a cuttable material at the jeweler's workshop but does NOT appear
in vanilla glass furnace crafting jobs. The inorganic IS_GLASS flag makes
the material visually and physically glass-like but does not register it
with the engine's hardcoded glass item production code.

### Approaches considered and rejected
1. **New builtin at UNUSED slot:** Vivified successfully but not recognized
   by glass furnace jobs (index too high).
2. **Adjacent slot to glass types:** Index 6 is WATER — cannot overwrite.
   No unused slots exist between indices 2-6.
3. **Overwriting existing glass type:** Technically possible (swap GREEN_GLASS
   properties with custom glass, restore on save). Rejected as it creates
   a visible seam — all existing green glass items temporarily change identity.
4. **Extending glass type range:** No mechanism found. No count variable,
   no bounds field, no configurable range.

### Conclusion
Glass items through vanilla crafting jobs are behind a compiled C++ wall.
The ceiling for seamless module glass is: IS_GLASS inorganic → ROUGH product
at glass furnace → cuttable at jeweler → finished glass gems. Real glass
items (windows, goblets, furniture, crafts) require vanilla mat_types 3/4/5
and cannot be extended through runtime injection.

### Builtin vivification — future potential
The ability to vivify nil builtin slots is a novel discovery with potential
applications beyond glass. The UNUSED slots could theoretically host new
builtin material types for other purposes — custom liquids, custom powders,
or other engine-recognized material categories. Whether DF's engine checks
other builtin ranges dynamically (unlike glass) is unknown and would require
per-category investigation.