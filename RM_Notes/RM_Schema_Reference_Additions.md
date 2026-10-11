# RM Schema Reference Additions

Findings verified against live game data during the Making Fuel session.
Written to be merged into `RM_Module_Schema_Reference.md`. Every claim here
was confirmed by console dump or in-game observation, not inferred.

---

## 1. Builtin material subtypes: `mat_subtypes`

### The mechanism

Some builtin materials carry a subtype index that selects *which form* of the
material an item is. `COAL` is the only one currently known.

The builtin COAL material is a **single object**. Its `state_name.Solid` is
just `"coal"`, and coke and charcoal are not separate materials anywhere in
the raws. `mat_index` is a pure discriminator that DF's item naming and
stockpile code reads:

| mat_index | Item name | Notes |
|---|---|---|
| `0` | coke | What vanilla `LIGNITE_TO_COKE` writes |
| `1` | charcoal | What the wood furnace's built-in job writes |
| `-1` | refined coal | No discriminator, DF's generic label |
| `2`, `3` | refined coal | Collapse to the generic. There is no fourth name. |

All three names are fully functional vanilla fuel. `-1` is not a broken state;
it is a legitimate third product.

### Verification

```
vanilla LIGNITE_TO_COKE  products[0].mat_type = 7, mat_index = 0
dfhack.matinfo.find('COAL:COKE')      -> 7 / 0
dfhack.matinfo.find('COAL:CHARCOAL')  -> 7 / 1
```

Note that `matinfo:toString()` returns `"coal"` for every index including 0
and 1. The material layer does not distinguish them; the **item naming layer**
does. Do not use `toString()` to verify this.

### Schema

`PRODUCT_TYPES` entries may carry `mat_subtypes`, a table mapping the schema's
`mat_id` string onto the index:

```lua
BAR_COAL = { item_type = 0, mat_type = df.builtin_mats.COAL,
             mat_subtypes = { COKE = 0, CHARCOAL = 1, COAL = -1 } },
```

`build_product` consults `mat_subtypes` **before** the inorganic lookup. An
unmapped `mat_id` is a hard failure that logs and skips the product, because
the previous behaviour was to miss the inorganic lookup, fall through to `-1`,
and produce a plausible-looking item that was silently wrong.

### Appearance cannot be split

`mat_table.builtin.COAL` carries `tile = 219` and `state_color.Solid = 8` on
the single shared object. There is no per-index appearance data. Changing the
tile or colour changes coke, charcoal and refined coal together.

To get a distinct-looking coal item, make a custom material as `BLOCKS` or
`BOULDER` (as `MAKING_FUEL_CARBON_BRICK` does) and convert it to a coal bar in
a second reaction. The fuel itself must stay vanilla, because DF's furnace fuel
check is hardcoded to the COAL builtin. No custom material can be fuel.

---

## 2. Reagent flag vocabulary

DF's reaction reagents share the **general job item filter** bitfields, which
are far wider than the reaction raw token set. RM can therefore express filters
that no raw file can, because the raw parser has no token for them.

**Confirmed live.** A reagent carrying `furniture`, `plant`, `non_artifact`,
`wood` and `not_bin` produced the in-game tooltip:

> Requires: Furniture plant non-artifact wooden item that isn't a bin

Three of those five bits have no reaction raw token. DF composed them into a
grammatical description, which proves the engine reads them rather than merely
tolerating them.

### Full bit map

Dumped from `df.reaction_reagent_itemst` in a live world.

**flags1**: item state, origin, processing history, and item categories

```
 0 improvable              16 extract_bearing_vermin
 1 butcherable             17 processable_to_vial
 2 millable                19 processable_to_barrel
 3 allow_buryable          20 solid
 4 unrotten                21 tameable_vermin
 5 undisturbed             22 nearby
 6 collected               23 sand_bearing
 7 sharpenable             24 glass
 8 murdered                25 milk
10 empty                   26 milkable
11 processable             27 finished_goods
13 cookable                28 ammo
14 extract_bearing_plant   29 furniture
15 extract_bearing_fish    30 not_bin
                           31 lye_bearing
```

**flags2**: material families, decoration state, designations

```
 0 dye                     19 totemable
 1 dyeable                 20 horn
 2 dyed                    21 pearl
 3 sewn_imageless          22 plaster_containing
 4 glass_making            24 soap
 5 screw                   25 body_part
 6 building_material       26 ivory_tooth
 7 fire_safe               27 lye_milk_free
 8 magma_safe              28 blunt
 9 deep_material           29 unengraved
10 melt_designated         30 hair_wool
11 non_economic            31 yarn
12 allow_melt_dump
13 allow_artifact
14 plant
15 silk
16 leather
17 bone
18 shell
```

**flags3**: material classes and item circumstance

```
 0 unimproved              12 edged
 1 any_raw_material        13 on_ground
 2 non_absorbent           14 divine
 3 non_pressed             15 crafted_artifact
 4 allow_liquid_powder     16 wood
 5 any_craft               17 stone
 6 hard                    18 non_artifact
 7 food_storage            19 woven
 8 metal                   20 gem
 9 sand                    21 empty_or_water
10 can_use_location_reserved   22 grown_not_crafted
11 written_on
```

Bits 9, 12 and 18 of flags1 and bit 23 of flags2 are `UNUSED` and are
deliberately omitted from the schema.

### Implementation

`build_reagent` maps a subset explicitly, because those carry an alias
(`glass_material` writes `flags1.glass`), read from outside the flags block
(`sand_bearing` reads the reagent root), or needed a comment. The remainder
live in `REAGENT_FLAG_MAP` at module scope in `refinish-module-react.lua`,
applied by a single loop. Schema names match struct field names there.

`preflight.py` validates flag names against `KNOWN_REAGENT_FLAGS`, which must
be kept in sync with both.

### Flags with non-obvious behaviour

**`unrotten` is a positive requirement only.** Setting it `false` does not mean
"must be rotten"; it means no rot requirement, which is the default. **DF has
no filter for requiring rot.** A pair of rotten/unrotten reactions cannot be
distinguished and should be a single reaction.

**`body_part` is sufficient on its own.** Verified live: a reagent carrying
only `body_part` took raw hides and left coal bars and pitch buckets alone.
It also spans both `CORPSE` and `CORPSEPIECE`. The narrowing flags (`bone`,
`shell`, `horn`, `totemable`) are optional refinements.

**`not_bin` excludes bins, not barrels.** `item_binst` and `item_barrelst` are
separate item classes. There is no `not_barrel` bit anywhere in the three
bitfields. Excluding barrels requires pinning item types instead.

**`totemable` is the skull filter.** Unworked skulls are not matched by `bone`.
They carry `totemable`, which is the flag DF uses to decide what a totem can be
carved from.

**`allow_artifact` and `crafted_artifact` are the two dangerous flags.**
`crafted_artifact` *requires* an artifact rather than permitting one, so a
reagent carrying it will seek out exactly the items that must never be
consumed. `preflight.py` warns on both under `artifact_risk`.

**Untested in a reaction context:** most of the long-tail flags have no raw
token, so no vanilla reaction exercises them. `furniture` and `not_bin` are
confirmed working. The rest are exposed on the principle that an inert flag
costs a table row and the only way to learn which ones bite is to set them.
`nearby`, `on_ground` and `murdered` are the most promising unexplored ones.

---

## 3. Reagent `quantity` has two meanings

This is a silent-failure trap.

**Countable items** (boulders, plants, corpse pieces, hides, remains):
`quantity` is an item count.

**Dimensioned items** (bars, liquids, powders, thread, cloth, globs):
`quantity` is measured in **dimension units**, not items.

Confirmed dimensions:

| Item type | Full dimension |
|---|---|
| BAR (incl. coal) | 150 |
| LIQUID / GLOB | 150 |
| THREAD | 15000 |
| CLOTH | 10000 |
| SKIN_TANNED | 1 |

A wildcard reagent (`item_type -1`) spans both kinds, so **no value of
`quantity` is correct for it**. This produced a real bug: a reagent with
`quantity: 4` matched a coal bar and consumed 4 of its 150 units, leaving a
bar displayed as 2% spent.

---

## 4. Organic material encoding

Organic `mat_type` is computed per species from a base plus the material's
**own local index within that species**:

```
plant material    mat_type = 419 + local material index
                  mat_index = plant raw index

creature material mat_type = 19 + local material index
                  mat_index = creature raw index
```

Observed examples:

```
419/173  plump helmet plant     (local 0, STRUCTURAL)
420/62   peanut plant leaf
422/174  pig tail               (THREAD item)
423/85   cranberry vine fruit
37/616   cave spider silk       (creature)
19/615   giant cave spider silk (creature)
```

### Local indices are NOT stable across species

Scanned all 225 plants:

- Local material `0` is `STRUCTURAL` for **225 of 225**. Base 419 is universal.
- Local material `1` is `WOOD` for **224 of 225**. `OLIVE` is the exception.

```
OLIVE material list:
  0 STRUCTURAL   plant
  1 OIL          frozen olive oil
  2 SOAP         olive oil soap
  3 WOOD         olive wood
  ...
```

A reagent pinned to `mat_type = 420` asks every plant for its local material 1,
which on olive is **frozen olive oil**. A "char wood" reaction would silently
accept oil.

**Rule: never pin `mat_type` on an organic reagent.** Use `mat_type = -1` and
filter with flags. This is what vanilla does. The gukil strings reagent is
`THREAD` at `mat -1/-1` carrying nothing but `ANY_PLANT_MATERIAL`, and the soap
tallow reagent is `GLOB` at `mat -1/-1` with a reaction class.

---

## 5. Magnifying glass (material picker): empirical table only

**There is no working theory.** Five were proposed and falsified against data
during this session. What follows is measurement, not explanation.

The picker selects a **material**, never an item. It cannot express "burn my
tables but not my beds"; that distinction is item type and no reagent-level UI
in DF exposes it.

| Picker appears | Picker absent |
|---|---|
| BAR, SMALLGEM, BLOCKS, ROUGH, BOULDER | PLANT *(garbage menu)* |
| WOOD | PLANT_GROWTH *(garbage menu)* |
| CORPSEPIECE *(creature list)* | SEEDS, TOTEM, BRANCH |
| SKIN_TANNED *(creature list)* | CLOTH, GLOB |
| THREAD **with `flags2.plant`** | ANY_ITEM, POWDER_MISC |

"Garbage menu" means the picker appears but every entry renders as
**"unknown frozen plant substance"**. That is DF's fallback for a plant material
it cannot resolve, and it is worse than no picker at all.

### Theories tested and falsified

1. **`mat_type = 0` required**: killed by gukil strings, which is `-1/-1` and works.
2. **Resolved `mat_type` with wildcard `mat_index`**: killed by the same.
3. **Item-type whitelist**: killed by `CHAR_BONE`, which is `item_type -1` and works.
4. **Material-domain enumerability**: killed by `PLANT` failing with the same flags THREAD succeeds with.
5. **Pinning the item type fixes the garbage menu**: it does not.

### Known dependency

`flags2.plant` is load-bearing for THREAD. The same reagent without it shows no
picker. This matches vanilla's gukil reagent carrying `ANY_PLANT_MATERIAL`.

**Open test:** add `"plant": true` to a `CLOTH` reagent. Cloth is the same
material domain as thread and currently shows nothing.

---

## 6. `df.item_type` complete map

93 entries, 0 to 92. This list is the complete set of what a reagent can pin,
and it is what the in-game stockpile category list displays.

```
 0 BAR              23 CORPSE           46 CORPSEPIECE      69 DRINK
 1 SMALLGEM         24 WEAPON           47 REMAINS          70 POWDER_MISC
 2 BLOCKS           25 ARMOR            48 MEAT             71 CHEESE
 3 ROUGH            26 SHOES            49 FISH             72 FOOD
 4 BOULDER          27 SHIELD           50 FISH_RAW         73 LIQUID_MISC
 5 WOOD             28 HELM             51 VERMIN           74 COIN
 6 DOOR             29 GLOVES           52 PET              75 GLOB
 7 FLOODGATE        30 BOX              53 SEEDS            76 ROCK
 8 BED              31 BAG              54 PLANT            77 PIPE_SECTION
 9 CHAIR            32 BIN              55 SKIN_TANNED      78 HATCH_COVER
10 CHAIN            33 ARMORSTAND       56 PLANT_GROWTH     79 GRATE
11 FLASK            34 WEAPONRACK       57 THREAD           80 QUERN
12 GOBLET           35 CABINET          58 CLOTH            81 MILLSTONE
13 INSTRUMENT       36 FIGURINE         59 TOTEM            82 SPLINT
14 TOY              37 AMULET           60 PANTS            83 CRUTCH
15 WINDOW           38 SCEPTER          61 BACKPACK         84 TRACTION_BENCH
16 CAGE             39 AMMO             62 QUIVER           85 ORTHOPEDIC_CAST
17 BARREL           40 CROWN            63 CATAPULTPARTS    86 TOOL
18 BUCKET           41 RING             64 BALLISTAPARTS    87 SLAB
19 ANIMALTRAP       42 EARRING          65 SIEGEAMMO        88 EGG
20 TABLE            43 BRACELET         66 BALLISTAARROWHEAD 89 BOOK
21 COFFIN           44 GEM              67 TRAPPARTS        90 SHEET
22 STATUE           45 ANVIL            68 TRAPCOMP         91 BRANCH
                                                            92 BOLT_THROWER_PARTS
```

### Item type notes

- `ROCK` (76) is the small rock / knapping item. It is **not** `BOULDER` (4)
  and it is not a degradation fallback.
- `CORPSE` (23), `CORPSEPIECE` (46) and `REMAINS` (47) are three distinct types.
  Bird and pest bodies filed under Remains in the stockpile are
  `item_remainsst`, so no `CORPSE` reagent will ever match them.
- **Organs are `MEAT`, not `CORPSEPIECE`.** A heart cannot be reached by any
  `body_part` reagent. Arms, heads, bones and skulls are `CORPSEPIECE`.
  The split follows the stockpile: organs are food, limbs are corpses.
- `BRANCH` (91) is what tree felling leaves behind. Nothing in vanilla
  consumes it.
- `THREAD` (57) covers plant fibre and all creature silks under one item type.

---

## 7. Material resolution failure is silent

DF does not error on an unresolvable material. It renders a fallback:

- Unresolvable plant material in a picker: `"unknown frozen plant substance"`
- Inorganic `mat_type 0 / mat_index -1`: `"rock"`
- Out-of-range `mat_index`: also renders as rock

**`0 / -1` decodes to `rock`, verified.** This is why a fort keeps playing
normally after RM shuts down and its materials are pulled from RAM. Walls,
buildings and items made from removed materials simply become rock. Nothing is
damaged by being rock.

This benign failure mode is the reason the material index problem never
manifested as crashes, and it is why `-1` is the correct wash target for a
module material whose identity cannot be recovered.

---

## 8. Category nesting

`parent` names the parent category's key **unprefixed**:

```json
{ "key": "FUEL",     "name": "make fuel",     "parent": "" },
{ "key": "CHARCOAL", "name": "make charcoal", "parent": "FUEL" }
```

An empty string means top level. Reactions reference the prefixed form
(`MAKING_FUEL_CAT_CHARCOAL`).

---

## 9. Reagent types not found in `REAGENT_TYPES`

A reagent type defined in `refinish-module-types.lua` but placed **outside** the
`REAGENT_TYPES` table produces this validation error:

```
reactions[N].reagents[M].type 'X' is not a recognized reagent type
```

This reads like a typo in the JSON and sends you looking in the wrong place.
The file parses cleanly, `reqscript` succeeds, and other reagent types resolve
normally. Check table membership before checking spelling:

```lua
local types = reqscript('refinish-module-types')
print(types.REAGENT_TYPES['X'] ~= nil, types.PRODUCT_TYPES['X'] ~= nil)
```

---

## 10. Reagent `reads`: the words DF prints for a reagent

DF writes a reagent's requirement line, in the hover and in a red row's
objection alike, from the reagent's own fields, and adds its own item word
after them. A reagent gated by a token prints the token. `reads` gives it
words instead. Verified in play 2026-10-05 and 06.

```json
{ "code": "fine_coals", "type": "BAR_ANY", "quantity": 600,
  "reaction_class": "FINE_COAL", "reads": "fine coal" }
```

The hover read "4 FINE_COAL bars" before and "4 fine coal bars" after; a
red row reads "Requires fine coal bars".

| The reagent | `reads` becomes | DF prints |
|---|---|---|
| contained (another reagent's `contains` names it) | its code; every product naming the code follows | "Coal tar-containing item" |
| gated by `reaction_class`, or by its type's own class | its class; every material carrying the old class carries the words beside it | "fine coal bars" |
| gated by `has_material_reaction_product`, with no class | a class of words carried by every material that has the product; the product gate is cleared | "seed-bearing plant" |
| gated by both a class and a product | its class; the product gate stays (a reagent holds one class) | |
| naming a material or a tool alone | nothing: DF already prints the name | "Sponge iron bars" |

- The words are the part before DF's item word: "clay or glue" on a binder
  tool reads "Clay or glue binder".
- A non-empty string. One set of words stands for one class or one product
  across every module: words already standing for another are refused with
  an ERROR, and that reagent keeps its own class and code.
- Leave `reads` off a reagent a script finds by its class or code at run
  time: Making Fuel's tank fill and its drain base are two.
- The class service gives the words at start and takes them back before
  every save (RM_Core_Services.md, the material class service).

## 11. Products: `measure` and `whole`

- `"measure": true` on a TOOL product: the product is sized from what its
  source measured, in the tool's own unit, and DF's count becomes how many
  stacks (refinish-reaction-outputs.lua, MEASURED STACKS). What is left
  below one unit banks per building, tool and material, and shows in the
  building's output bank.
- `"whole": true` beside it: the measure always comes out whole, so the
  output bank lists no zero row for it. The crushers' dust is one: a
  boulder less twelve gravel is 14 dust exactly.