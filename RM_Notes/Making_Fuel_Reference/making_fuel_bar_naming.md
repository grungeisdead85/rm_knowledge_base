# Making Fuel: Suppressing the "bars" Suffix

Status: **diagnosed and proven, not yet built.** The mechanism is measured
end to end. What remains is the injection work.

Problem: module charcoal displays as "charcoal bars". Vanilla coal displays
as "charcoal". The goal is parity, per the no-seams principle.

---

## 1. Measured facts

Four probe builds, all run live via `refinish-name-probe`. Method throughout:
mutate one field, read the regenerated name, restore, compare. The simulation
is suspended for the whole script, so no frame passes between mutate and
restore. Names are not stored on items; DF regenerates them from the item's
material identity on demand, which is what makes this measurable at all.

### B1: the suffix is not flag controlled

88 material flags and 32 inorganic flags swept, each flipped and restored
individually.

- Material flags: **0 hits.**
- Inorganic flags: **1 hit, `WAFERS`**, which changed "charcoal bars" to
  "charcoal wafers".

`WAFERS` is adamantine's lever. It selects **which** word is appended, never
**whether** one is. There is no flag that suppresses the suffix.

The `WAFERS` hit matters beyond the letdown: it proves the sweep was sensitive
enough to find a real lever, so the zeros are trustworthy rather than a probe
defect.

### B2: the suffix is INORGANIC-branch behavior

The bar's `mat_type` / `mat_index` were swapped across material modes:

| identity | display |
|---|---|
| builtin COAL, idx 1 (t=7) | `charcoal` |
| INORGANIC:IRON (t=0) | `iron bars` |
| PLANT_MAT:WILLOW:WOOD (t=420) | `willow` |
| PLANT_MAT:WILLOW:STRUCTURAL (t=419) | `willow plant` |
| CREATURE_MAT:DOG:BONE (t=22) | `dog bone` |

Builtin coal names are minted inside the bar description code, keyed on
builtin COAL identity, with the suffix skipped in that same branch. Outside
that branch, only the **inorganic** path appends a type word. Plant and
creature mode bars display bare names.

Creature mode is suffix free but bakes in a creature name, so **plant mode is
the road.**

### B3 and B4: the prefix is a stored field, not a runtime composition

B3's surprise: renaming the willow **plant** to "charcoal" did not clear the
prefix on its STRUCTURAL material. It still read "willow charcoal". So the
prefix is not composed at display time.

B4 found the field. `material.prefix` is a string snapshotted at raw parse:

| material | prefix | state_name | displays |
|---|---|---|---|
| WILLOW:WOOD | `""` | `willow` | `willow` |
| WILLOW:STRUCTURAL | `willow` | `plant` | `willow plant` |
| PLUMP:DRINK | `""` | `frozen dwarven wine` | `frozen dwarven wine` |
| WHEAT:MILL | `""` | `single-grain wheat flour` | `single-grain wheat flour` |
| DOG:BONE | `dog` | `bone` | `dog bone` |

**Display = prefix + state_name when prefix is non-empty, state_name alone
when it is blank.** One mechanism, every observation, including the ones from
B2 that looked like different rules.

Confirmed live, not just inferred from the table:

- `R1` control: prefix set to `"xyzzy"`, state name `"charcoal"` gives
  **"xyzzy charcoal"**. The field is what the name builder reads, right now.
- `R2` final config: prefix `""`, state name `"charcoal"` gives **"charcoal"**.

`R2` is the target configuration, rehearsed on a live vanilla material and
undone. Plain plant material, no special flags, prefix blank.

Corroborated by the wheat path map: STRUCTURAL, LEAF and SEED carry
`prefix = "single-grain wheat"`; DRINK and MILL carry `""` via `[PREFIX:NONE]`
in the raws. Builtin COAL also carries `""`.

---

## 2. The BAR shape question is closed

Concern raised: the coals must be **bar shaped** or the smelter's fuel fix
stops accepting them.

They stay bars. Material mode and item type are independent fields on the
item. A BAR of a plant material is still `df.item_type.BAR`.

Confirmed against the fuel fix itself. `widen()` in
`making-fuel-fuel-access.lua` rewrites the job filter to:

```lua
e.item_type      = spec.item_type and df.item_type[spec.item_type] or -1
e.item_subtype   = -1
e.mat_type       = -1        -- wildcard: any material mode
e.mat_index      = -1        -- wildcard
e.reaction_class = spec.class or ''
e.vector_id      = df.job_item_vector_id[vec]
```

The smith tier's floor is `item_type = BAR` and its gate is
`reaction_class = FUEL_SMELTING`. **Material is wildcarded by construction.**
`scan_for_fuel` agrees: it reads classes through
`dfhack.matinfo.decode(it).material.reaction_class`, which is on
`material_common` and present in every mode.

The naming fix and the fuel fix do not touch.

---

## 3. Build plan

### 3.1 The pipeline as it actually runs

Worth stating because it narrows the work considerably:

1. A reaction mints a coal bar. Products are declared
   `{"type": "BAR_COAL", "mat_id": "CHARCOAL", "dimension": 150}`.
2. `BAR_COAL` in `refinish-module-types.lua` resolves to
   `item_type = 0, mat_type = df.builtin_mats.COAL` with `mat_subtypes`
   mapping the schema's `mat_id`. So the reaction mints a **builtin** coal bar.
3. `making-fuel-coal-watcher.lua` intercepts it on `onItemCreated` and
   replaces it with the module material carrying the fuel classes.

**The reaction JSON never names the module materials.** Only the watcher does.
So the reactions need no change at all; the swap happens downstream of them.

### 3.2 Edit sites

**A. Define the host plant and move three materials into it.**

`CHARCOAL`, `COKE` and `REFINED_COAL` currently live in the `materials` array
of `making_fuel_materials.json` as inorganics. They move to plant materials on
a module host plant, via the existing `inject_plants` path in
`refinish-module-inject-plant.lua`, which already clones a donor and
neutral-resets it (wipes all plant flags, biomes, spawn rates, growths and
anatomy strings, so the host never sprouts or reaches worldgen).

Per material: `state_name.Solid` set to the coal name, **`prefix` written
explicitly empty**, reaction classes attached as today
(`FUEL`, `FUEL_SMELTING`, `CHARCOAL`).

Writing `prefix` explicitly is not optional. A deep-copied donor brings its
materials' prefix strings along, so trusting the clone reintroduces the exact
bug being fixed.

**B. Point the watcher at the new address.** `making-fuel-coal-watcher.lua`:

- `REPLACEMENT_FOR` (lines 62 to 66) stops holding inorganic keys.
- `module_mat` (line 90) stops building `'INORGANIC:' .. mat_key`.
- The fallback at line 165.

One host can carry all three, since the prefix is per material and blank on
each. So the tokens become `PLANT_MAT:<HOST>:CHARCOAL` and siblings.

**C. Sprites: the engine reaches, the call site does not exist.**

Both coal materials declare
`"graphics": {"bar": {"donor": "BUILTIN:COAL", "offset": 0},
"texflag": "BUILTIN:COAL"}`.

`refinish-sprite-engine.lua` needs **no changes**. `apply_to_material(material,
spec, mat_key)` takes a material struct directly, and donor resolution runs
through `dfhack.matinfo.find(token).material`. Both are mode-agnostic, and
`bar_texpos` is a material-side slot present in every mode.

The gap is the caller. `apply_to_material` has exactly one call site:
`apply_graphics` in `refinish-module-inject.lua`, the inorganic injector.
`refinish-module-inject-plant.lua` contains no reference to sprites, graphics
or texpos. **The plant path needs a graphics call wired in**, reusing the
engine unchanged.

### 3.3 The blocker: the plant path is not wired

`inject_plants`, `clear_plants` and `plants_physically_clear` have **zero
callers** outside `refinish-module-inject-plant.lua`. Nothing in the injection
sequence invokes them and nothing in the shutdown pipeline clears them. The
file is written but not connected.

So this is RM core engine work, not Making Fuel module work. Before the naming
fix can be delivered at all:

1. **Wire plant injection into the guarded Step 2.5 injection.** Not
   `SC_MAP_LOADED`: injecting before the pause protocol makes the safety
   predicates misreport clean state.
2. **Wire `clear_plants` into shutdown** at the correct LIFO position, module
   assets after RM core assets.
3. **Wire a graphics call into the plant path**, per 3.2C.
4. **Confirm the materials JSON schema can express a plant host at all.**
   Unverified. If it cannot, the schema and its validator need the shape first,
   and `preflight.py` needs re-copying from the live RM install after.

### 3.4 Then verify in game

1. **`createItem` with a plant material.** The watcher calls
   `dfhack.items.createItem(u, BAR, -1, mi.type, mi.index)`. Plant mat_types
   are large (419 to 421 observed). Confirm a plant-material BAR mints, and
   that `stack_size` and `dimension` behave. This is the load-bearing
   assumption; a two minute console test, worth running before any of 3.3.
2. **Hotsave coverage.** Confirm the clear/restore cycle handles
   plant-injected materials the way it handles inorganics.

### 3.5 Known side effect: ghost classifier reclassification

`making-fuel-ghost.lua` Layer 3 branches on `mi.mode` (line 276), so module
coal moves from MINERAL to PLANT once it becomes a plant material.

Inert today: coal is a reaction output, not a char reagent, so no yield
changes. But the file's own comments treat a live MINERAL result as a bug
signal meaning a reagent needs a gate, and this reclassification is silent. If
module coal ever becomes a reagent to an adaptive reaction, its multiplier
changes with no warning. Documented here so it is not rediscovered as a bug.

### 3.4 Then eyeball in game

Normal recycle-and-look pass: bars stockpile listing, stocks screen grouping,
trade screen. These are display surfaces no probe reaches.

---

## 4. Probe

`refinish-name-probe` build B4 is the current build. It is non-destructive and
self-restoring; rerun it after the injection lands to confirm the real module
material displays bare. Requires an idle module coal bar in the fort.
