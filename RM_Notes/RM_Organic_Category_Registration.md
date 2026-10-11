# RM Stockpiles and Organic Category Registration

How DF decides where an item is stored, and how to give a runtime-injected
material a real stockpile identity in one of DF's organic storage categories so
it can be hauled, filtered and switched on and off by the player like any
vanilla material.

Everything below is measured on a live fort. Where a claim rests on one
observation, the run that produced it is given.

This is an engine-level capability, not content. It belongs beside
`RM_MODULE_ENGINE_README.md`, and `making-fuel-hide-stock.lua` is currently
its only implementation.

---

## 1. The problem

An injected material that is stored in an **inorganic-indexed** category works
with no help at all. Every RM metal, every Making Concrete stone, every bar and
block hauls correctly and always has, because those settings vectors are sized
off `world.raws.inorganics.all`, which RM grows at injection time.

Measured on one fort, stockpile 220:

```
stone.mats             len=767
bars_blocks.bars_mats  len=767
coins.mats             len=767
gems.cut_mats          len=767
armor.mats             len=767
```

with the hide material at inorganic index 765. Already covered.

The **organic** categories are indexed differently, and that is the whole
problem. Food, leather, bone, wood, cloth and the rest are indexed by position
in a per-category enumeration built from the raws at world load. A material
injected into RAM afterwards has no position in it.

```
Glob   len=2416   ours=ABSENT   fat=372
```

Vanilla llama fat sits at position 372. Our material is absent from all forty
categories. There is therefore no position for a stockpile setting to switch
on, which is why `STOCKPILE_GLOB` on the material does nothing.

**The flag is not the lever.** `STOCKPILE_GLOB` was present on our material the
whole time, identical to fat's. So was every other candidate: clearing
`IS_STONE` changed nothing, and after that the two materials' flag words were
identical except `IMPLIES_ANIMAL_KILL`.

---

## 2. What is measured

**O1. Inorganic-indexed categories need nothing.** They are sized off the live
inorganic list. Everything RM has ever injected into one has hauled.

**O2. Organic categories are indexed by enumeration position, not by material
index.** `settings.food.glob` has length 2416 on a fort whose inorganic list is
767 long and whose creature list is 1318 long. It matches nothing except the
Glob enumeration.

**O3. The enumeration lives in `world.raws.mat_table`,** as two parallel
vectors per category: `organic_types[cat]` holding mat_type and
`organic_indexes[cat]` holding mat_index.

**O4. There is a reverse index on the material,** `material.food_mat_index[cat]`,
and it holds the same position. Confirmed on both sides:

```
fat  food_mat_index[Glob] = 372      and fat is at position 372 in the list
ours food_mat_index[Glob] = 2416     after registration, and hauling started
```

**O5. Both directions are required.** Registered in the enumeration with an
enabled settings slot and no reverse index, nothing hauls. That state was held
for fifteen minutes of fort time and observed doing nothing. Adding the reverse
index alone started hauling within a job cycle.

**O6. `food_mat_index` is the only candidate field.** A field-name scan of the
material for anything containing `index`, `food` or `mat_` returns
`[food_mat_index, mat_rgb]` on both our material and fat's.

**O7. `raws.inorganics` is a struct, not a vector.** The vector is `.all`
inside it. Taking `#` of the container returns nothing, silently, which cost
two rounds here and produced a probe line reading `inorganics=nil` while 767
was visible in a dozen other rows of the same output.

**O8. Acceptance and classification are separate gates, and registration only
buys the first.** A refuse stockpile accepts item types through
`settings.refuse.type`, which is indexed by item type rather than by material.
On the test fort every type was already enabled on both refuse piles, `GLOB`
included, before anything was registered:

```
stockpile 222: refuse.type len=113
   [GLOB=75] = 1
   enabled: BAR(0) SMALLGEM(1) ... GLOB(75) ... BOLT_THROWER_PARTS(92)
```

The indexing is proven rather than assumed: indices 0 to 92 each decode to a
real item type in order, and 93 to 112 are padding. Yet DF still routed a fresh
hide glob to a food pile, exactly as it routes vanilla llama fat. So refuse
acceptance was never closed; DF simply does not classify a fresh glob as
refuse.

The lesson generalises past this case. Registering a material in an enumeration
makes it **addressable** by a stockpile setting. It does not change what DF
decides the item **is**. Both the Glob registration and the refuse toggle were
necessary-and-not-sufficient in exactly the same way, one round apart.

**O9. Container type follows item type, not stockpile category.** Food class
items ask for barrels; bars, blocks, gems, finished goods, cloth and leather
ask for bins. Registering a glob into a bin-using category would change which
pile accepts it and not which vessel it asks for, so a `GLOB` will not bin.

Source: reasoning from observed behaviour plus the vessel split DF presents in
its own stockpile screens. Not independently measured, and it was never tested
because the design question it answered was dropped.

**O10. A registered material appears by name in the stockpile settings UI.**
After registration the hide materials are individually listed and togglable
under Food, in the fats section, alongside vanilla fat. The UI list is built
from the same enumeration, so registration is what makes a material visible to
the player rather than only to the hauling code.

---

## 2a. Barrels, unresolved

Registered hide globs haul to a food pile and are never put in a barrel, while
vanilla fat in the same pile is barrelled. Every surface was compared and the
material one is exhausted: a full field diff against fat leaves only
differences we set deliberately, and `butcher_special_type` was matched to
fat's `75` with no effect.

An item level diff leaves two numeric candidates and no flag:

```
dimension     ours=1050   fat=150
stack_size    ours=1      fat=13
```

A hide is seven units where a fat glob is one. If barrel capacity is checked
against dimension, a 1050 glob may not fit. **Untested.** It is the only
numeric explanation anything produced, and it was not pursued because the
design landed on uncontainered storage.

`flags` differ too, but that row is the outcome rather than the cause: fat
reads `in_inventory` precisely because it is already inside the barrel.

---

## 3. The recipe

For each material, per category:

1. Resolve the category: `df.organic_mat_category.<Name>`.
2. Append to the forward enumeration:
   ```lua
   types:insert('#', mat_type)     -- 0 for an inorganic
   idxs:insert('#', mat_index)
   ```
3. Write the reverse index, using the position the append landed at:
   ```lua
   mat.food_mat_index[cat] = pos
   ```
4. Grow every existing stockpile's settings vector for that category to the new
   enumeration length. The elements are numbers on this build: DFHack exposes
   `settings.food.*` as `vector<char>` (its own error, "Cannot write field
   vector<char>.101: integer expected"), although df-structures declares them
   bool. Append `1` or `0` with `insert('#', n)`; a Lua boolean is refused.

Steps 1 to 3 touch raws, which are rebuilt from the mod files on every load, so
they must be redone every load. Step 4 touches saved fort data and must be
idempotent.

### What is safe and what is not

| Write | Persists? | Risk |
|---|---|---|
| `organic_types` / `organic_indexes` | No, raws | None. Rebuilt each load, re-appended each load. |
| `material.food_mat_index` | No, raws | None, same reason. |
| `settings.<group>.<vector>` | **Yes, saved** | The only write into data we do not own. |

Rules that follow, and none of them are optional:

- **Grow to a target, never by a delta.** Compute the enumeration length and
  fill up to it. A delta creeps across sessions and corrupts the alignment.
- **Never shrink a settings vector.** Cutting one shifts every position after
  the cut and silently re-points the player's existing choices at other
  materials. `stop()` must unwind nothing.
- **Rewrite the reverse index for every material every sync,** not only newly
  appended ones. Positions can land differently across loads, and a stale
  reverse index pointing at another material is worse than an absent one.
- **Skip stockpiles whose vector for that group is zero length.** That means
  the pile carries no settings for that group at all; growing it hands it a
  category it never had.

### Default for new slots

A new slot inherits the pile's existing intent: enabled if anything else in the
same vector is already enabled, disabled otherwise. A player who switched globs
on for a pile meant globs, and a new one appearing switched off reads as the
feature not working.

### Uninstall

If the mod is removed, a stockpile carries a short tail DF's own enumeration
does not reach. DF indexes by position and stops at its own list length, so the
tail should be ignored. **UNTESTED.** It is the one consequence of this
technique that has not been measured.

---

## 4. Which categories this opens

Forty, from one fort's enumeration. Nothing about the technique is glob
specific.

```
Meat  Fish  UnpreparedFish  Eggs  Plants  PlantDrink  CreatureDrink
PlantCheese  CreatureCheese  Seed  PlantGrowth  PlantPowder  CreaturePowder
Glob  PlantLiquid  CreatureLiquid  MiscLiquid  Leather  Silk  PlantFiber
Bone  Shell  Wood  Horn  Pearl  Tooth  EdibleCheese  AnyDrink  EdiblePlant
CookableLiquid  CookablePowder  CookableSeed  CookablePlantGrowth
Paste  Pressed  Yarn  MetalThread  Paper  Parchment
```

Several are cooking categories rather than storage ones, so registering into
`EdiblePlant` or `CookableLiquid` would expose a material to the kitchen rather
than to a stockpile. Untested, and worth knowing before reaching for one.

---

## 5. Failure history

- **Assuming the material flag was the lever.** `STOCKPILE_GLOB` was present
  the entire time. So was everything else; clearing `IS_STONE` changed nothing
  and the flag words ended up identical to fat's except for
  `IMPLIES_ANIMAL_KILL`.
- **Comparing a raw `mat_index` against a settings vector length.** The probe
  printed "OUR INDEX 765 IS PAST THE END" as a verdict. Meaningless: the vector
  is indexed by enumeration position, and ours and fat do not even share an
  index space, mat_type 0 against mat_type 20.
- **Suspecting an engine-wide hole.** Reasoning from "our globs do not haul" to
  "maybe nothing RM injects hauls" ignored evidence already in hand: the
  inorganic-indexed vectors in the same dump all read 767, and every metal in
  the mod hauls in normal play. The narrow explanation was available and was
  not taken.
- **Registering forward only.** Enumeration slot present, settings slot
  enabled, nothing hauled. See O5.
- **`#` on `raws.inorganics`.** See O7. Two rounds.
- **Reissuing a whole file over an applied pair.** The `.all` fix was delivered
  as a pair, applied, and then overwritten by a whole-file reissue built from
  the pre-pair copy. Diagnosed from the log: working at 10:07, failing again at
  10:17. Deliver pairs against the reconstructed live file, or deliver a whole
  file only when every outstanding pair is already folded into it.
- **Reading a length as a verdict.** The probe printed "OUR INDEX 765 IS PAST
  THE END" against `glob_paste` and `glob_pressed` because their vectors are
  short. Meaningless, and it pointed at the wrong thing for a round.
- **Treating acceptance as classification.** Twice, one round apart. See O8.
- **A stale scheduled closure.** `repeatUtil` holds the function from the body
  execution that scheduled it. Reloading the script makes a new body, but the
  `running` global is still true, so `start()` returns early and never
  reschedules. The poll keeps running old code while manual commands run new
  code. `off` then `on` rebinds it. This is the third time in this project that
  the gap between a body execution and a lifecycle event has caused a bug; see
  also `running` and `seen_a_screen` in `RM_Material_Sprite_Redirect.md`.

---

## 5a. Where the hide wing landed, and why

**Superseded 2026-09-26.** Hides are no longer globs. The currency is DF's own
skin carrying a count, which DF files in a refuse pile under its own fresh raw
hide and rotten raw hide settings, so the hide claim and everything below are
gone. The section stays as the record of why the glob went where it did;
`RM_Hide_Wing_Lessons.md` has the rest.

Recorded because the reasoning is the reusable part, not the outcome.

Hide globs live in the **Glob category of a food stockpile**, uncontainered,
and rot there on schedule.

DF sends a rawhide to a refuse pile and lets it rot. A rawhide is a
`CORPSEPIECE`, and corpsepieces are refuse by item type, which is a route our
material cannot take without giving up the glob-based currency design. DF sends
a glob, including vanilla fat, to the Glob category of a food pile. So the
module treats a hide the way DF treats every other glob, and the pressure to
process promptly is preserved by letting it rot where it sits rather than by
choosing the pile.

Storage does not preserve. `PRESERVE_IN_STORAGE` in `making-fuel-hide-rot.lua`
is false, and the machinery for the other answer is intact behind it. A hide
that keeps indefinitely once stored removes the only thing making the player
tan it.

Confirmed in play: registered hides haul, appear by name in the stockpile
settings under Food, age in the pile, take the rotten prefix, and are destroyed
on schedule. Both hide reactions refuse rotten input, before and during the
job.

---

## 5b. Powders, and where the dyes landed

Measured 2026-09-23 on the Making Fuel dyes. The recipe above makes a material
addressable. For a powder, DF also files the item by the TYPE of its material,
and no flag or registration changes that.

| The dye was | Listed by name | Hauled |
|---|---|---|
| Inorganic, no plant claim | nowhere | at once, its bag to Furniture as Bags, "as though empty", like vanilla gypsum plaster |
| Inorganic, with `POWDER_MISC` and `POWDER_MISC_PLANT` and a PlantPowder registration | under Milled Plants | never |
| A plant material on the module's `DYE_HOST` plant, same registration | under Milled Plants | at once, to the pile set for it |

The middle row was diffed against a vanilla dye that hauled at once: material
flags identical, item flags identical, a PlantPowder back-reference on both.
The material type was the one difference left, and moving the dyes onto a plant
host settled it.

So no stockpile category lists an inorganic powder by name and also hauls by
that listing. Dyes are declared on a plant host, and preflight warns when one
is declared as an inorganic. `making-fuel-dye-stock.lua` registers them: the
recipe above, with the plant material's own (type, index) pair.

Also measured: `building:canStoreItem` is not the stockpile check. It answered
false on every pile for a vanilla dye whose bag was being hauled at that moment.

---

## 6. Tools

| File | Purpose |
|---|---|
| `making-fuel-hide-stock.lua` | The implementation. `sync` registers and resizes, `status` reports slot presence per material and vector length per stockpile, `reverse` prints the reverse index for ours beside vanilla fat. |
| `making-fuel-stock-probe.lua` | Read only. `organic` dumps all forty enumerations with the position of ours and of a control material. `sizes` dumps every settings vector on every stockpile against the reference counts. `flags` diffs the two material flag words. |

The control material matters more than any single reading. Pick something
vanilla that is stored the way the injected material wants to be stored, and
every number becomes a comparison instead of a guess. Llama fat did all the
work here.
