# RM Dye Integration (Making Fuel and RM core)

How the Making Fuel dyes were made indistinguishable from vanilla's: made in the
Make dye folder, taken by every dye job, listed by name and stockpiled the way
vanilla dyes are, and extended with a bark dye for every tree.

Everything below was measured on a live fort on 2026-09-23 (DF 53.16, DFHack
53.16-r1.1) unless it is marked otherwise. Since 2026-10-04 RM core makes dyes
of its own from dust (section 11), and makes its own Make dye when a mod cuts
vanilla's (section 12).

Related records: `RM_Organic_Category_Registration.md` (stockpile registration;
section 5b is the powder result), `refinish-ledger.lua` (the data cycle, header
and comments), `making_fuel_tree_dye_research.md` (bark colours and sources).

---

## 1. What DF's dye system reads

- **`material.powder_dye` is the dye colour.** It is a separate field from
  `state_color.Powder`, which is the material's colour PATTERN (DF's
  color_pattern), not a colour: powder_dye is a colour index, state_color a
  pattern index. RM's derived default dye colour is the first colour of the
  material's Powder pattern (refinish-module-inject, apply_dye_color,
  2026-09-30); read straight as a colour index it was right only for
  vanilla's first 136 colours.
  DF's dye system reads `powder_dye`: `item:isDyeColor()`, the colour filters
  on dye jobs, and the swatch in the Make dye menu all follow it. Vanilla sets
  both from the raws (`[POWDER_DYE:<colour>]` and `STATE_COLOR`) and keeps them
  apart on purpose: redroot dye looks brown and dyes red.
- **`IS_DYE` alone is a trap.** With `powder_dye` at -1, a plain Dye cloth job
  still takes the dye, completes, and dyes nothing (job 10370).
- **Existing dye items follow their material live.** Writing `powder_dye` on
  the material made existing items report a colour at once. No per-item repair
  is needed after a fix.
- **RM:** `apply_dye_color` (`refinish-module-inject.lua`) writes `powder_dye`
  from the material's powder colour, or from the definition's `dye_color` key
  when it is set. The inorganic and the plant injector both call it after the
  class preset. Validator and preflight check `dye_color` on both.

---

## 2. The Dyer's Shop menu

Measured with `making-fuel-dye-probe.lua`.

- **Top level:** four vanilla folders (Dye cloth, leather and thread a specific
  colour; Mix dye), the Make dye folder, the three plain dye jobs, then reaction
  rows.
- **Make dye is a reaction category,** `MAKE_DYE`, named once by vanilla's
  `ACACIA_BARK_DYE` for all 68 vanilla rows. A module reaction joins it with
  `"category": "MAKE_DYE"`; preflight warns (`external_category`) and RM injects
  it anyway. The row's swatch is the product material's `powder_dye`. When a
  mod has cut MAKE_DYE, the engine files these reactions under RM's own Make
  dye instead (section 12).
- **The colour lists cover all 136 descriptor colours,** not the dyes a fort
  owns. "Dye cloth a specific colour" holds 272 rows: 136 "tint cloth
  <colour>" folders first, then 136 direct "dye cloth <colour>" jobs. The
  direct row is how a single-colour dye is applied, and it sits below every
  tint folder.
- **A tint or mix submenu lists colour PAIRS** that mix to its colour (amber:
  13 mix pairs, 26 tint rows; crimson 25 with no crimson dye in the world). No
  pair mixes to black, so "Tint cloth black" and "Mix black dye" are empty in
  vanilla, sliver dye included. Adding black dyes cannot change that; "dye
  cloth black" is their route, confirmed with both module blacks. Decision:
  vanilla's empty menus are left to vanilla.
- **The menu is rebuilt every frame.** Read it only when the master list is
  populated and the drawn rows are its own pointers.
- **Manager work order templates** (33,175 dye entries) do not encode colour
  combinations.

Module dye reactions use vanilla's short names ("make alizarin dye"); the
tooltip names the reagents when they are available and the objection line when
they are not. Carbon black is made at the Dyer's Shop, without fuel.

---

## 3. Stockpiling, and why the dyes are plant materials

| The dye was | Listed by name | Hauled |
|---|---|---|
| Inorganic, no plant claim | nowhere | at once, its bag to Furniture as Bags, like vanilla gypsum plaster |
| Inorganic, with `POWDER_MISC`, `POWDER_MISC_PLANT` and a PlantPowder registration | under Milled Plants | never |
| A plant material on a module host plant, same registration | under Milled Plants | at once, to the pile set for it |

The middle row was diffed against a vanilla dye that hauled at once: material
flags identical, item flags identical, a PlantPowder back-reference on both.
The material TYPE was the only difference left, and moving the dyes onto a
plant host settled it. **DF files a powder by the type of its material.** No
stockpile category lists an inorganic powder by name and also hauls by that
listing, and an unlisted dye reads to a player as missing and broken, which
is ruled out. Hence plant hosts.

Measured on the way:

- **Stockpile settings are `vector<char>` at run time,** although df-structures
  declares them bool: DFHack's own error was "Cannot write field
  vector<char>.101: integer expected". Elements are numbers; append `1` or `0`
  with `insert('#', n)`. A Lua boolean is refused.
- **`building:canStoreItem` is not the stockpile check.** It answered false on
  every pile for a vanilla dye whose bag was being hauled at that moment.
- **`item.stockpile_countdown`** ticks down one per 50 frames, then DF checks
  whether the item needs moving; `stockpile_delay` is its reset value and
  varies at random (df-structures). It is not a count of failures.
- **Module scripts start after their materials exist** (since 2026-09-30).
  Until then `making_fuel.lua` started them inside RM's token call, a second
  before RM injected the module's materials, so the dye stock script polls
  every 10 frames until they appear (frames advance while paused; game days do
  not). RM now runs Making Fuel's start hook once its assets are injected and
  its stop hook before any clear (refinish-module-engine, MODULE LIFECYCLE),
  so a hotsave stops the scripts at its clear and starts them after the
  restore. The poll stays: harmless, and it covers anything that arrives
  later than the start.
- **New settings slots** start switched on only when the pile already takes
  every milled plant. The 48 tree dyes arrived switched off in a dye-only pile.

---

## 4. Where the dyes live

- **`DYE_HOST`** (`making_fuel_plants.json`): the eight authored dyes, class
  `DYE`. Tokens are `PLANT_MAT:MAKING_FUEL_DYE_HOST:<KEY>`.
- **`TREE_DYE_HOST`:** generated at the token call (section 5), on a host of
  its own so authored and generated dyes never renumber each other.
- **The DYE class preset** sets `IS_DYE`, `POWDER_MISC` and
  `POWDER_MISC_PLANT`, the flags every vanilla dye carries. The last two are
  the plant powder claim and are true only on a plant.
- **`making-fuel-dye-stock.lua`** registers every `IS_DYE` material on the
  module's host plants in PlantPowder: the list entry, the material's
  back-reference and the stockpile slots, following
  `RM_Organic_Category_Registration.md`. A module dye declared as an inorganic
  is reported and never registered, and preflight warns on one.

---

## 5. Tree bark dyes

Every plant with a WOOD material gets a bark dye: 70 trees in vanilla, since
abaca and banana have no wood.

- **22 trees with their own vanilla `BARK_DYE`** get a bark route making that
  dye. Vanilla already has their log route.
- **48 others** get a new dye on `TREE_DYE_HOST`, with a log route (vanilla's
  recipe: 1 log and an empty bag, Dyer's Shop, Plant Processing, Make dye) and
  a bark route (2 bark and a bag).
- **Colour:** five documented overrides (walnut dark brown, cashew black, mango
  yellow, candlenut russet, bayberry light brown); every other tree takes its
  live WOOD colour, so a tree added by another mod gets a dye in its own colour
  with nothing written for it.
- **Physical numbers** (heat, density, value) are copied from the first vanilla
  bark dye in the world.
- **Names:** vanilla's rows use the short tree name. The plant's NAME carries
  "tree" (`[NAME:apple tree]`) and its materials carry `PREFIX:NONE`, so the
  short name is the WOOD material's state name minus " wood" ("apple wood"
  gives "apple"); a wood named without it ("tower-cap") is used whole. A bark
  route over a vanilla dye takes that dye's own name, so both apple rows read
  "make apple bark dye" and differ only in the requirement line.
- **Bark is WOOD.** Bark items are `MAKING_FUEL_BARK` tools minted by the
  hijacker from a wood job's lost value, with the job's own feedstock material
  ("a feather wood door gives feather wood bark"). The tinder watcher moves only
  tinder and kindling onto the fuelwood twin. So the bark route names
  `PLANT_MAT:<tree>:WOOD`.
- **Built as data, not as a push.** `making-fuel-tree-dyes.lua` runs in
  `making_fuel.lua`'s listener and hands the host plant and the reactions to RM
  with the JSON, the way the hide materials are handed over. RM validates,
  injects and sweeps them with everything else, and they are in RAM before the
  first tick.
- **Guards:** keys are made unique against the whole module (one duplicate key
  rejects the entire module), a plant holds at most 200 materials, and an
  override colour must be a loaded descriptor.
- **Removed:** `GRIND_BARK` and `making-fuel-bark-dye.lua`, the push that put
  `BARK_DYE_MAT` on every tree's wood and twin for it.

---

## 6. RM core capability added: reagents name any material by token

`"mat_token": "PLANT_MAT:<plant>:<material>"` on a reagent, the form of
vanilla's `[REAGENT:log:1:WOOD:NONE:PLANT_MAT:ACACIA:WOOD]`. Products already
took it.

- Resolved at build time in `build_reagent` (`refinish-module-react.lua`),
  applied last, pinning type and index together.
- **A miss closes the slot.** The reagent is given reaction class
  `RM_UNRESOLVED_MAT_TOKEN`, which no material carries, so the row shows and
  cannot run, and an ERROR names the token. Falling back to "any material"
  would let one tree's log route take every log in the fort. (`mat_id` misses
  still fail open with a warning; not aligned yet.)
- The validator accepts `mat_token` as the material for types that need one;
  preflight checks it on reagents as well as products, including module-plant
  tokens against the plants file.

---

## 7. The data cycle

**Arrays against references.** Raws arrays (inorganics, reactions and the
like) must hold nothing of RM's or a module's when a save is written, or DF
treats the save as corrupt; keeping saves good is RM's job, which is why
everything a module adds goes through RM. Stale references in items are fine:
they fail gracefully, and they are what the ledger repairs on the next load.

**The ledger** (`refinish-ledger.lua`) moves, by name:

- inorganic indices on items, constructions and buildings, as before;
- **dye references:** thread and tanned-leather dye pairs, the thread and
  sewn-image improvements on built items, and every dye profile's source list;
- **world history:** the six event classes that store a material (three
  masterpiece types, item stolen, figure died, body abused). The walk runs back
  from the newest event to this site's founding: 6,987 events in 0 to 15 ms;
- **plant materials:** every owned plant material by name, `PLANT_ID|MAT_ID`,
  against the (type, index) pair `dfhack.matinfo.find` gives it. Owned means on
  a host plant with an owned prefix, or carrying an owned prefix itself (the
  `MAKING_FUEL_FUELWOOD` twin on every tree). 136 in this fort.

First large real move: removing the eight inorganic dyes shifted the module's
inorganics, and remap moved 359 objects by name and left 6 references to the
removed dyes untouched, by design. A ledger written before plant materials were
recorded skips plant pairs once; loading the same autosave twice shows that
message twice, because the save on disk still holds the older ledger. When a
half of the ledger comes back empty, `write()` keeps last session's record for
it.

**One sweep.** Prefixes exist so RM core and the module engine clear every
core and module asset in one pass. Scripts do not add their own cleanup to the
data cycle: every added cleanup slows it and multiplies the ways it can fail.
The dye stock script removes nothing when it stops; the PlantPowder list is
rebuilt from raws at load (109 before a hotsave, 101 after).

**Observed, not changed:** RM's AUTOSAVE shutdown clears core and module engine
assets and quicksaves, and module scripts stop only at map unload, after the
save. The fuelwood twins (70), the bark dye push (43, since removed) and the
hide material renames (780) were in RAM through that quicksave, and the reload
was clean.

---

## 8. DFHack facts

- Stockpile settings vectors are `vector<char>` on this build (section 3).
- `dfhack.items.getPosition(item)` returns x, y and z as three values, not a
  coordinate.
- DFHack exposes vtable classes in their exact type, so `obj._type` is the
  exact class (used to key the history event pass).
- df-structures on the develop branch can differ from the build in use. Read
  the structures at the DFHack tag's own revision, and trust a runtime error
  over the XML.

---

## 9. Mistakes made, so they are not repeated

- **The plant claim.** Copying vanilla plant dyes' powder flags onto inorganic
  dyes, and registering them under Milled Plants, is what stranded them in the
  dyer.
- **`bool` taken from the XML.** Concluded that insert could never work on
  settings vectors and that the hide script had never grown a pile. The build
  exposes `char`; the hide script was right all along.
- **A timer read as a verdict.** `stockpile_delay` 47 against 2 was read as
  repeated failures; df-structures documents it as a random reset value.
- **An assumption about bark.** Claimed the tinder watcher moves bark onto the
  fuelwood twin. Its hop list is tinder and kindling, and every bark route
  named the twin until corrected.
- **The plant NAME.** Rows named from it read "apple tree bark dye" beside
  vanilla's "apple bark dye".
- **A filename.** The new probe took the name of the older
  `making-fuel-stock-probe.lua` listed in `RM_Organic_Category_Registration.md`
  section 6.

---

## 10. Tools

| File | Purpose |
|---|---|
| `making-fuel-dye-probe.lua` | Watches the Dyer's Shop menu and every job at every dyer and logs each change; `dump` writes colours, dye materials, reactions, dye items, dyed goods and the bark wiring; `trial` sets `powder_dye` in RAM. |
| `making-fuel-dye-stock.lua` | The PlantPowder registration for module dyes. `status` lists each dye's slot and back-reference, each pile's categories and our slots in it, and every dye item with its container chain, tile and flags. |
| `making-fuel-stock-probe.lua` | Diffs one of our items and its material against a reference that hauls; `inorganic` is the RAM trial that stands our dyes as plaster does. Shares its name with the older probe (section 9). |
| `making-fuel-tree-dyes.lua` | The tree bark dye generator (section 5). |

---

## 11. RM core's mineral dyes (2026-10-04)

Dust of any stone, gem or metal makes a dye of its own colour at the Dyer's
Shop, under Make dye: "make <colour> mineral dye", two dust of that colour, a
granule of RM's glue and an empty bag, processing plants skill, no fuel. A
quarter of the dust is lost (`refinish-dyes.lua`).

- **One dye per colour dust comes in, read live.** At the token call every
  stone, gem and metal's colour is read (a pattern's first colour:
  `df/colours.md` in the knowledge base), so a mod's colours come in with nothing written for
  them. Vanilla has 77; a modded test world had 152. A finish takes its colour
  from the dust that finished it, so finishes add none.
- **Plant materials, as every dye must be** (section 3): class `DYE`, named
  "<colour> mineral dye", dye colour its own, on host plants of their own,
  `REFINISH_DYE_HOST` and, past 200 colours, `REFINISH_DYE_HOST_2` on. Tokens
  are `PLANT_MAT:REFINISH_DYE_HOST:<COLOUR>`.
- **Which dust.** A reaction cannot ask for a colour, so every material that
  has dust carries its colour's class, `REFINISH_DYE_<COLOUR>`: stones, gems
  and metals through RM's class service at start, finishes from the finish
  mint (`refinish-mint-finish.lua`), since the class service never touches
  RM's own materials. Taken back before every save.
- **Stockpiles.** Claimed for Milled Plants through
  `refinish-stockpile-organic`. The claim takes a FUNCTION that lists the dyes,
  called when the registrar settles; handed a list, it refused the claim
  ("select must be a function", in play).
- **All permitted at load** (AUTO). First they were injected with no permits
  and permitted to the civilisation as the fort had dust of each colour; nine
  were in the permitted list and none showed in any menu. Loaded all at once,
  every one is listed and works.
- **Known limit:** a module's materials inject after the token call, so a
  colour only a module's stone wears has no dye.

---

## 12. When a mod cuts Make dye (2026-10-04)

A mod replaced vanilla's dye reactions with categories of its own ("Concentrate
dye" among them, ordinary and bulk), so no `MAKE_DYE` category existed. A
reaction names its category by id and is offered in no menu when the world
lacks it, so every module dye, Making Fuel's and RM's, was gone from the
Dyer's Shop.

- When `MAKE_DYE` is missing, the module engine (`refinish-module-react.lua`,
  WHEN A MOD CUTS MAKE DYE) makes a Make dye of RM's own,
  `REFINISH_CORE_CAT_MAKE_DYE`, as vanilla's: its name, its description with
  minerals added, no hotkey. Every module reaction that asks for `MAKE_DYE` is
  filed there. It is swept with RM core's other assets before every save and
  made again at the next load; said once a session at INFO.
- It never guesses which of a mod's categories is the dye one: a mod can split
  its dyes across several. A mod's own categories are left as they are.
- Seen in that world: Making Fuel's tree dyes rebuilt a log route for every
  tree, so the mod's cut log reactions did not take those dyes away.

---

## 13. Open

- **Dye pile default:** a new module dye slot starts off unless the pile takes
  every milled plant. Whether a pile that takes every module dye should also
  take new ones is not decided.
- **`mat_id` against `mat_token`:** a `mat_id` miss still fails open, a
  `mat_token` miss fails closed.
- **`making_fuel_content_1_0.md`** still lists `DYE_BARK` and `GRIND_BARK`,
  both superseded by the tree bark dyes.
- **The older stock probe** (`organic`, `sizes`, `flags`) is in neither the
  project nor the tools archive.
- **Why a permit added after load was not enough** for the mineral dyes
  (section 11). A read of the Dyer's built menu with one reaction permitted
  after startup beside one permitted at load would settle it.
