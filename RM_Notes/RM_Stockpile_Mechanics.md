# RM Stockpile Mechanics

Status, 2026-09-27: the settings layout is read from source. The filing rule
is measured (section 6): DF files by material class, and a slot alone does
nothing. Section 8 has the shape of DF's own hauling jobs, captured live.

---

## 1. Sources

- **df-structures**: `df.building.xml` (`stockpile_settings` and every
  `stockpile_parameter_*` struct), `df.d_basics.xml` (`organic_mat_category`,
  `material_flags` and their `type` attributes).
- **DFHack `plugins/stockpiles`** (commit 85d2a5f, 2026-09-26):
  `StockpileSerializer.cpp` says what indexes every settings vector and which
  materials DFHack lists in each; `OrganicMatLookup.cpp` says how an organic
  position maps to a material.
- **DFHack `library/modules/Materials.cpp`**, `MaterialInfo::getCraftClass`:
  the material flag to material class map.
- **RM measurements**: `RM_Organic_Category_Registration.md` (the two-way
  registration), the aggregate twin note in `refinish-material-aggregate.lua`
  (IS_STONE lost in the copy), the coal name probe runs of 2026-09-26 and
  2026-09-27, and observations in play on 2026-09-27.

DF's own acceptance code is in neither source. DFHack mirrors the settings UI,
so which fields DF's check actually reads is inferred from that mirror and
from play.

---

## 2. How DF addresses an item

An item goes to a pile when the pile has the group for the item's **type**
switched on, and the entry for the item's **material** in that group switched
on. Every group addresses a material in one of five ways.

| Address | Indexed by | Who is in it |
|---|---|---|
| Inorganic list | inorganic index | Any inorganic in `world.raws.inorganics.all` when the vectors are sized. DFHack lists only those with the group's flag (section 3). |
| Organic list | position in `mat_table.organic_types` / `organic_indexes` for one category | The enumeration DF builds from the raws at load. A material made at run time is only in it through RM's two-way registration plus vector growth (measured). |
| Fixed entries | a fixed list | Builtin materials, or a material flag class (below). |
| Plant list | plant index | TREE plants (logs). |
| Creature list | creature index | One entry per creature. |

**The flag classes.** DFHack's `getCraftClass` takes the first set flag that
has a class: WOOD is Wood, THREAD_PLANT is Cloth (the "plant cloth" entry),
SILK and YARN are Cloth, BONE is Bone, TOOTH is Ivory, HORN, PEARL, SHELL and
LEATHER are themselves, IS_METAL is Metal, IS_GEM is Gem, IS_GLASS is Glass,
IS_STONE is Stone.

The fixed lists line up with those classes. Finished goods' list is WOOD,
PLANT_CLOTH, BONE, TOOTH, HORN, PEARL, SHELL, LEATHER, SILK, AMBER, CORAL,
GREEN_GLASS, CLEAR_GLASS, CRYSTAL_GLASS, YARN, WAX. Amber, coral and the three
glasses are builtin materials.

---

## 3. Group by group

| Group | What it takes | Material address | Listed by DFHack |
|---|---|---|---|
| Animals | creatures | creature list | |
| Food | by subcategory | organic: Meat, Fish, UnpreparedFish, Eggs, Plants, PlantDrink, CreatureDrink, PlantCheese, CreatureCheese, Seed, PlantGrowth (leaves), PlantPowder, CreaturePowder, Glob, PlantLiquid, CreatureLiquid, MiscLiquid, Paste, Pressed | every position |
| Furniture | furniture types | inorganic + fixed (finished goods' list less WAX) | IS_METAL or IS_STONE |
| Corpses | corpses | creature list | |
| Refuse | every item type except BAR, SMALLGEM, BLOCKS, ROUGH, BOULDER, CORPSE, CORPSEPIECE, ROCK, ORTHOPEDIC_CAST; body parts by creature | creature lists | |
| Stone | boulders and the like | inorganic | inorganic SOIL (not AQUIFER), or IS_STONE without NO_STONE_STOCKPILE |
| Ammo | ammo itemdefs | inorganic + fixed | IS_METAL |
| Coins | coins | inorganic | any |
| Bars | bars | inorganic + fixed COAL, POTASH, ASH, PEARLASH, SOAP | IS_METAL |
| Blocks | blocks | inorganic + fixed GREEN_GLASS, CLEAR_GLASS, CRYSTAL_GLASS, WOOD | IS_METAL or IS_STONE |
| Gems | rough and cut | inorganic + glass | rough IS_GEM; cut IS_GEM or IS_STONE |
| Finished goods | CHAIN, FLASK, GOBLET, INSTRUMENT, TOY, ARMOR, SHOES, HELM, GLOVES, FIGURINE, AMULET, SCEPTER, CROWN, RING, EARRING, BRACELET, GEM, TOTEM, PANTS, BACKPACK, QUIVER, SPLINT, CRUTCH, TOOL, BOOK | inorganic + fixed (the 16 above) | IS_GEM, IS_METAL or IS_STONE |
| Leather | leather | organic Leather | |
| Cloth | thread and cloth | organic Silk, PlantFiber, Yarn, MetalThread | |
| Wood | logs | plant list | TREE plants |
| Weapons | weapon itemdefs | inorganic + fixed (10) | IS_METAL or IS_STONE |
| Armor | armor itemdefs | inorganic + fixed (10) | IS_METAL |
| Sheet | paper and parchment | organic Paper, Parchment | |

**Finished Goods checks every setting, not just type and material
(2026-09-27).** A pile hauls an item only if its dyed or undyed setting, its
colour and its core and total quality are all allowed as well. Vanilla's
stockpiling has more quirks of this kind, and they are not consistent from
one group to another, so RM's own hauling has to match each group's full set
of settings, not a simplified one.

**Settings vectors are numbers.** df-structures declares them as bool, but
DFHack hands them over as `vector<char>`: 0 or 1 (measured in
`refinish-stockpile-organic`). Read as a Lua boolean, a 0 counts as on.

---

## 4. What RM has measured

| Material | Item | Address it has | Result |
|---|---|---|---|
| Dye host materials (plant) | POWDER_MISC | PlantPowder, registered by `refinish-stockpile-organic` | stored |
| Hide material (inorganic, retired) | GLOB | Glob, registered | stored |
| Vanilla tree WOOD | TOOL | Wood class | stored, in a bin (2026-09-27) |
| Vanilla flax THREAD | TOOL | plant cloth class | stored, in a bin (2026-09-27) |
| Vanilla wheat STRUCTURAL | TOOL | none | never taken (2026-09-27) |
| Coal host CHARCOAL (plant) | TOOL | none | never taken (2026-09-27) |
| Coal host materials (plant) | BAR | none: bars have no plant list, and SOAP is the only flag entry | never stockpiled |
| Fuelwood twin (plant, copied with `assign`) | TOOL (kindling) | presumably none, see section 5 | never stockpiled (2026-09-27) |
| Aggregate stone twins (inorganic, copied with `assign`) | TOOL (gravel) | none: IS_STONE reads false on the twin (measured) | never stockpiled (2026-09-27) |
| Module inorganics (dung, straw, mash, the keys) | TOOL | inorganic list, flags from their definitions | stored |

---

## 5. The rule that fits every result

**A material made at run time stockpiles only when it carries the address its
item's group files by, and nothing gives it one automatically.**

- **`assign` does not bring flag arrays across.** Measured on the stone
  twins: granite reads IS_STONE true, its twin reads false. The fuelwood twin
  is made with the same call. Its own comment says the copy carries flags; the
  stone measurement says otherwise, and a comment is not evidence. A twin
  without WOOD has no class, which fits kindling never stockpiling.
- **The coal host materials were never given a class.** As tools they sit
  where vanilla wheat's structural material sits. As bars they have no
  address at all.
- **The dye was registered.** That is the whole reason it works.

---

## 6. Measured, 2026-09-27

**The constraint.** The twins must stay hidden. Giving them their flags
back puts duplicate names in every settings list and makes RM's refinish scan
take each stone twin as a second reagent for every stone, which breaks every
feature built on a hidden twin.

**SPECIAL does not help.** Per the wiki it keeps AI civilisations, caravans and
generated creatures off the material; the player uses it as normal. It hides
nothing from the player's lists.

**The copy leaves nothing behind.** `refinish-stockpile-probe`: plaster carries
IS_STONE, NO_STONE_STOCKPILE and 4 flags in all; its twin carries 0.

**A slot alone files nothing.** The twin's finished goods slot was already on
in three of the four piles before the probe touched them, and gravel on the
twins has sat unstored all along. In the probe, haulers binned the plaster
control and the iron bar within a minute and never touched the twin's gravel
or bar. DF's hauling only picks up an item whose material has a class.

**Hidden does not stop hauling.** `refinish-haul-capture` caught a
StoreItemInBin job carrying 14 rot and pet keys, all dressed hidden and
unforbidden, into a Finished Goods bin.

**RM's SOIL class preset sets IS_STONE.** So every SOIL-class module tool
(dung, straw, mash, every key) is filed under Finished Goods. That is why those
tools store, and why the keys get binned: 527 rot keys were minted in one
session, 50 to 60 a minute while unpaused, each replacing one a hauler took.

**The fuel wood twin map empties on a data cycle.** `making-fuel-tinder-mat`
fills `_G.making_fuel_fuelwood_twin` only for twins it makes in that push; a
start that finds them already present leaves the map empty. Kindling split
before the first cycle wears its twin; the first split after one will log
"no twin for plant" and stay on real wood.

---

## 7. What this means for RM's materials (for decision)

**No flag route keeps a twin hidden.** A material is filed only with a class,
and a class is what lists it. So a twin that must stay hidden cannot be filed
by DF's hauling at all.

**The building level route: RM hauls its own items.** Membership is position:
DFHack's StockpileIterator counts an item as in a pile when it is on one of
the pile's tiles, or in a container there, with no acceptance check. So RM can
map each of its items onto a menu entry the player already controls (coal to
a bar pile's Coal entry, gravel to finished goods tools with its source stone
on, kindling to tools with Wood on), find a free tile or bin in a matching
pile, and post the hauling job itself. DF's filing never has to accept the
item, and nothing gains a flag. Section 8 has the job shapes; still unknown is
whether DF runs and completes a hauling job it did not create, and whether the
item stays put afterwards.

**Anything that must never be hauled should have no class.** The keys must
stay at their furnaces, unforbidden and unclaimed, so their materials should
carry no class flag: the property the twins have by accident, used on purpose.

**Organic items** (food, cloth, leather, sheet, globs, powders) register
through `refinish-stockpile-organic`, as the dyes do.

**Coal** under RM's own hauling could stay a plant bar: bare name, stacking,
stored wherever the player switches Coal on. Decision pending.

---

## 8. DF's hauling jobs, captured live

| Job | pos | Refs | Items and roles | Flags |
|---|---|---|---|---|
| StoreItemInStockpile | the destination tile in the pile | BUILDING_HOLDER, building_id = the pile (DFHack reports the pile as the job's holder) | the item, Hauled | none; item_subtype 1, meaning unknown |
| StoreItemInBin | the bin's tile | UNIT_WORKER only | the bin, TargetContainer; then every item to store, QueuedContainer (one job carried 14) | store_item |
| StoreItemInBarrel | the barrel's destination | UNIT_WORKER only | the barrel, Hauled; the item, QueuedContainer | store_item, do_now |

**Posting RM's own StoreItemInStockpile job** (`refinish-haul-post` v1, three
runs, nine jobs): DF assigns it (a dwarf took one within 75 frames), and DF
keeps its own hauling jobs in their pile's job list (23 of 23, then 15 of 15),
so RM's go there too. But every job ended within about three seconds of being
taken, with the item never moved. v1 had no control; v2 posts the identical
job for a tool DF itself files, and logs DF's cancellation reports, to tell
"DF refuses the item when the job runs" from "the job lacks something".

v2 (one run): DF reports nothing when these jobs end; they end silently. DF
set a hauled tool's stockpile assignment on some of its own jobs and not
others (1 of 2, then 0 of 1). The control's job ended within seven seconds of
being taken, and DF's own StoreItemInBin job took the control over at once:
DF files that item, so its own hauling picked it up and binned it. That
decides nothing about the posted job. Both target piles kept bins, where DF
stores tools with StoreItemInBin and never floor stores them, so a pile with
no bins is the next test (v3 prefers one).

v3 (four runs, twelve jobs for items DF cannot file): an ALL pile keeps every
list full, not empty (type 113/113, mats 832/832, colours 136/136, quality
7/7), and takes every group but corpses and refuse. Every job for gravel,
kindling or coal was taken and then ended silently when the dwarf reached the
item, which never moved; once the walk took over a minute and the job still
died at the item. Every control job ended the same way and DF's own
StoreItemInBin took the control and binned it. All three piles kept bins (92,
30, 24), so a bin-free pile is still untested. The pattern so far: the job
dies at pickup, which is where DF checks whether the item belongs in the
pile; an item it files is re-routed into a bin, an item it cannot file is
simply dropped from the job.

v4 (bin-free piles, pickup tracked every 5 frames): every posted job, the
control's included, ended within one look of a dwarf taking it, and none was
ever picked up. DF's own StoreItemInStockpile job then took the control and
had it on the floor of the same bin-free pile two seconds later. Same job
type, same pile, same item: DF's finished and ours died the moment it was
started, so the fault is in the posted job. Against DF's own job (captured),
four fields differ: DF's carries mat_type -1, item_type -1, specdata -1 and
aux_id -1, and none of them has a default of -1 in df-structures, so a new job
leaves them 0: item type BAR (0) of material INORGANIC (0). v5 writes the four
as DF does, and records both jobs field by field so any further difference is
on the page.

v5 (two runs): with the four fields as DF has them, nothing changed. The
field by field record found ONE difference between our job when taken and
DF's own job for the same control: expire_timer, 1 against 0, which only
counts how long a job waited for a worker. The jobs are the same. The tiles
were not: every posted job targeted the first free tiles of the pile's top
row, and DF's own job for the same item chose another tile. v6 requires the
target tile to be walkable and in the item's walkable group, and records the
item and both target tiles field by field.

v6 (two runs): with reachable tiles (the item and our target in the same
walkable group), nothing changed. The item record settles it. When DF's own
job took the control over, the control was already in the dwarf's hands
(in_inventory true, a UNIT_HOLDER ref, weight computed): the dwarf took our
job, walked to the item and picked it up, and at that moment DF discarded our
job and gave the item its own job to its own tile (115,102 in all four
runs). The switch happens in the tick of the pickup, which is why a
five-frame watch never saw the item in hand under our job. The job record
differed only in expire_timer and maxdur (DF sets maxdur once its job is
under way). Taking a hauling job also sets the item's storage counters
(stockpile_delay 13, stockpile_countdown counting down from 13).

**Conclusion: DF re-decides every haul at pickup.** A posted
StoreItemInStockpile job brings a dwarf to the item, and then DF's own filing
takes over: an item it files goes where DF chooses, an item it cannot file is
put straight back down. A posted hauling job cannot store an item DF will not
file.

Where things ended: a bin or barrel carries its own pile assignment
(`item.stockpile`: the pile's building id and tile); the items inside it carry
none, and belong to the pile through the container. The captured
StoreItemInStockpile did not finish storing (its lignite left in another
job), so a completed floor store has not been seen yet.

---

## 9. Routes 2 and 3: testing them for damage (2026-09-27)

Decision: test both routes that give the twins their flags, for damage
before anything else.

- **Route 3, permanent flags.** The fear is not only duplicate names in
  menus, but players making stone things that carry AGGREGATE or wooden
  things that carry the fuel classes.
- **Route 2, flag windows.** The flags go on only long enough for DF's own
  dwarves to haul the twin items. The open questions: whether items can still
  be taken out of piles and bins with the flags off, and what else breaks
  that nobody sees until much later.

**Static audit (vanilla_raws_reference).** No vanilla reaction takes a tool
by stone or wood class. The wooden reactions take logs, and the only
material-class reagent on a NONE item type is ANY_BONE_MATERIAL, limited to
body parts. Whatever could take a flagged twin is therefore in DF's hardcoded
jobs or in other mods' reactions, which only play can show.

**The probe, `refinish-twin-exposure`.** It copies each twin's source flags
onto it (what the assign copy left behind) and watches while armed:

- every job that takes a twin item, marked MODULE for Making Fuel's, Making
  Concrete's and RM's own reactions and OTHER for anything else;
- every hauling job that takes one, and where the item ends up;
- every item created already in a twin material, meaning something used a
  twin as a reagent;
- which stockpile settings lists now include the stone twins, by DFHack's
  listing rules.

`on` tests route 3. `window [frames]` tests route 2: flags on until no twin
item is loose or being hauled, then off, with the watch carrying on so that
retrieval from piles and bins with the flags off shows up. `status` counts
twin items by where they are; `off` restores the flags exactly.

**Route 2, measured (2026-09-27, one window).** Flags on: 93 stone twins took
281 material and 108 inorganic flags from their stones, 70 fuel wood twins
took 490 flags from their WOOD, and by DFHack's rules the stone twins joined
six stockpile settings lists (stone 87, finished goods, blocks, furniture,
weapons and cut gems 93 each). DF then filed all 25 loose twin items (24
gravel, 1 kindling) into pile 2 within about 70 seconds of play; each haul
shows the pickup re-decision (claimed loose, then claimed again by DF's own
job while carried), this time in the twins' favour. The window closed itself
at 5750 frames and 879 flags went back. With the flags off, Making Fuel's
char kindling reaction took the kindling out of the pile, and nothing moved a
stored twin item out. No OTHER consumer and no item made in a twin material
appeared. In play, the fuel wood twin does not appear in the material picker
with its flags on, which fits the wood lists being per plant, not per material.

---

## 10. The stockpile window service (built 2026-09-27)

Decision: every twin goes on windows (route 2), kindling included,
provided a window is triggered so no item is ever left stranded. Built as an
RM core service, `refinish-stockpile-windows.lua`, shaped like the organic
registrar: owners claim their twins through `_G.refinish_window_api.claim(
owner, select, opts)`, where `select()` returns each twin with its source.
The aggregate claims the stone twins, Making Fuel's tinder push the fuel wood
twins.

- **Loose** means on the ground and on no stockpile tile, a workshop's
  products included. Not loose: in a job, carried, in a container, part
  of a building, forbidden or marked for dumping.
- **Opens** when a new twin item is made (checked on the next tick, after the
  hops) or the backstop scan (every 1000 frames) finds a loose one.
- **Never closes during a haul**, since DF re-decides at pickup. Closes when
  nothing is loose or hauled, after a fresh count.
- **Stuck items**: if nothing is hauled for 3000 frames with items loose, it
  closes, logs the stuck items once as a pile settings or space problem, and
  retries after a growing wait (2000 frames, doubling to 32000).
- **Waits out** stockpile settings, work orders and building sheets, the
  screens that would show the stone twins' names, unless a haul is in flight.
- **Flags** are the sources' own, recorded by material address and id and
  written back only to the same material.

**First play test (2026-09-27).** Two faults, both fixed in the service:

- **Products in workshops were never counted.** The first build counted
  only items on the ground. Gravel and kindling moved only when the
  workshops were removed and they fell to the floor, as predicted.
- **Windows closed for building sheets.** Building sheets counted as a
  screen to wait for, and an open window closed whenever one opened: eight
  closes across two sessions of work on workshops, nothing hauled.
  Now only stockpile settings and work orders delay an opening, and an open
  window closes only by the two rules above.

Also seen: 21 gravel on the floor (15 granite, 3 jet, 3 lignite) sat through
several windows with nothing hauled. The STUCK report said only "no pile
takes them, or none has room", so it now says pile by pile why: finished
goods, tools and these materials' slots, links only, free tiles, bins,
whether the items can walk to it, and the items' own storage timers.

**Second play test (2026-09-27).** No window opened at all. Three new gravel
from a char boulder were hauled, but they are not twins: the aggregate logs
that MAKING_FUEL_CHAR gravel keeps its own material by design, so DF files it
unaided. The six gravel in the mason (granite and jet twins, per the tool
tint's colour list) and the new kindling in the furnace were never seen.

The second build had taken the item flag comment for in_inventory ("in a
creature, workshop or container inventory") as the mark of a workshop's
product, and looked for in_inventory or in_building before asking the holder.
DFHack's own code says otherwise. detachItem and moveToBuilding
(library/modules/Items.cpp, reverse-engineered from DF) treat a
BUILDING_HOLDER reference without in_building as building clutter: the item
is off the ground, sits in contained_items with the TEMP role, and gets
neither in_building nor in_inventory. Only PERM, the building's own material,
sets in_building.

Fixed: nothing off the ground is judged by its flags. The service asks what
holds it: a workshop or furnace holding it as anything but PERM means loose.
The backstop scan now logs a CENSUS of every twin item by place whenever it
changes, with the flags of the first item held by nothing it could find; the
loop's errors are logged instead of swallowed; and `status` writes to the
session log.

**Third play test (2026-09-27).** The service subscribed (the dispatcher logged
it every 25 frames) and started, and then logged nothing for five minutes of
play: no census, no window, no error. The census logs on the first scan
whatever it finds, so no scan ever ran, and the log cannot say where the loop
stopped. The rule here: stop guessing and check. No behaviour changed; the service
gained `refinish-stockpile-windows check`, which writes facts only: how many
times the loop ran and how each run ended, the dispatcher's entry for it,
both pause readings, the screen's focus strings, and every twin item's flags,
references, holder building and role, with what each holding building lists.

**Fourth play test (2026-09-27, two loads).** The first build in which windows
open for items in workshops: every census found all twin items there (23
gravel, then kindling). Facts from the log:

- Kindling sitting in a workshop is hauled while a window is open: the census
  after the second load's middle window shows 5 kindling on a pile.
- The 23 gravel in the mason (17 granite, 3 jet, 3 lignite) were not hauled in
  any of four windows, nor were 3 granite gravel made during the last one. The
  settings read reported both piles taking all three twin materials; that read
  was wrong (section 14): it counted entries of 0 as on.
- What was seen hauled after the first load's last window opened cannot be
  checked: the world was unloaded before the next census.
- The storage timers in every STUCK report were cut off by the log's 400
  character limit, and `check` was not run.

Changed, reporting only: the STUCK report and `check` now write one fact group
per line, under the limit; both name each holding building's stockpile links
(a workshop that gives to linked piles sends its products only there, which
no report had read); and `check` reads the items' storage timers again 500
unpaused frames later.

**Fifth play test (2026-09-27).** Everything was filed. The first window opened
on the 23 twin items sitting in workshops at load, stayed open 8350 frames
while the hauls went on, and closed with nothing loose: the census then read
28 twin items, all on a pile. Two later windows, for 5 new items each, closed
after 875 and 1225 frames. At the end of the log all 41 twin items were on
piles, and no STUCK was logged.

The same pre-existing gravel sat in the mason through four windows (about
14,000 open frames) on the previous load and was hauled at once on this one,
so being present at load does not by itself keep an item stuck. What differed
between the two loads is not in either log: the facts that could show it
(storage timers, the mason's links, the items' own state) were never captured
on a failing load.

Gravel was also seen sitting at the mechanic's workshop, and dust. The census
counts only twins, and it read none off a pile at the end, so that gravel is
either not a twin (char gravel keeps its own material) or appeared after the
log ends. Dust is not a twin: DF files it unaided.

Changed, reporting only: a STUCK now writes its first five stuck items in full
(flags, references, holder and role, storage timers) and reads the timers of
every sampled item again 500 frames later, so a failure is recorded when it
happens. `check WORD` lists every tool item whose id holds WORD and is off a
pile, twin or not, with its material and place.

---

## 11. DF's storage timer (measured 2026-09-27)

Sixth play test. The fort loaded, the stockpiles were made, and the haulers
worked through other tools before the gravel; on the previous load, where
everything was filed, most of those tools had been forbidden first. The 23 gravel in the
mason (building 6) and a second workshop (building 17) went unhauled through
two windows. Neither workshop has stockpile links; the settings read said both
piles took the gravel, which was a misread (section 14). For the first time the
STUCK reports carried each item's
storage timers, with a second reading 500 frames later.

- **How the timer works.** `stockpile_countdown` falls by 1 every 50 frames
  (measured: 9 to 11 in 500 frames). At 0 DF looks at the item; if it does not
  store it, it resets the countdown to `stockpile_delay` and raises the delay
  (measured steps of 1, 11 and 14). The 20 sampled delays went from 24-49 to
  47-76 in about a minute.
- **DF looked at every stuck gravel with the flags lent.** Every sampled
  delay was under 60, the number of countdown steps in a 3000-frame window,
  so each item's countdown had reset at least once during the window: DF
  looked at each and stored none.
- **Why that makes old items lose.** Each look that stores nothing stretches
  the wait before the next, and most of an old item's looks fall while the
  flags are off, so its looks drift out of step with the windows; a new item
  on a short timer is looked at within the next window. That matches what was
  seen: new gravel and kindling hauled, gravel from an earlier load not, and
  neither every time.

**Change.** When a window opens, every loose twin item's timer is set short
(countdown 1 to 10, delay 13, the value a fresh item carried in the haul
probe's capture), so DF looks at each within about 500 frames while the flags
are on, and again about 650 frames later.

**Still unknown: why DF stored nothing at a look with the flags on.** DF keeps
storage job and hauler counts per hauler type (`world.stockpile.num_jobs`,
`num_haulers`). The forbidding test fits a hauler limit, but that is not
measured; every STUCK report and the check now record those counts.

---

## 12. Stone twins refused with free haulers (seventh load, 2026-09-27)

The two piles were made while paused, before any window, then the haulers
worked through a few hundred other tools. Facts from the log:

- **The first window met a full hauling queue.** DF's storage counts read Any
  12/12 and Bin 12/12: all 12 haulers busy.
- **Later windows met free haulers** (storage jobs 0 or 1 of 12), and every
  window set the stuck gravel's timers short. DF looked at each stuck gravel
  several times per window (delays grew from 13 to 17-31 in the first alone)
  and stored none.
- **In the same window, with free haulers, DF stored new kindling (a wood
  twin, from the wood furnace) and dust (not a twin, from the mason)**, and
  refused old gravel and three granite gravel crushed in the mason during that
  window. On the fifth load all
  23 gravel were stored. So DF refuses stone twin gravel on some loads, and
  whether the refusal belongs to the workshop, the pile or the material is not
  known.
- **The last window closed with a 32000 frame retry wait**, and the log ends
  five seconds later, so if the mason was removed after that, its gravel had
  no window to follow.

**in_building.** Gravel read as in_building false while every gravel
sat in a workshop. That is what DF stores: in_building marks an item that is
part of a building (df-structures: construction materials, mechanisms, bodies
in coffins). An item sitting in a workshop is held by it, with a
BUILDING_HOLDER reference and the TEMP role in the building's list, which is
what the check read (refs BUILDING_HOLDER 6, role 0). DFHack's detachItem and
moveToBuilding treat such items the same way.

**Changes.**

- **The retry wait gives way to a change.** A STUCK keeps its census; during
  the wait the backstop scan still counts, and if the census no longer matches
  (items made, dropped or moved), a window opens at once.
- **`refinish-stockpile-windows test [frames]`** splits the question in one
  run. It holds a window (default 6000 unpaused frames), moves up to three
  gravel twins out of their workshop onto the floor beside it, and asks each
  pile through DF's own `canStoreItem` whether it would take a moved gravel, a
  gravel still in a workshop, and a loose non-twin control. It also notes any
  pile made during the test, then reports where each tracked item ended up.

---

## 13. The refusal belongs to the pile (eighth load, 2026-09-27)

Piles 1 and 2 were made while paused, before any window, the hauling rush
finished, and `refinish-stockpile-windows test` ran. During the held window
a new pile was made. **All the gravel went to the new pile as soon as it was
made**, from the floor and from the workshops alike. Through four windows
before the test, and the test itself, piles 1 and 2 took none.

- By the settings as read, piles 1 and 2 took tools and all three twin
  materials. That read was wrong (section 14): the difference is in the
  settings, and the read counted entries of 0 as on.
- Wood twins (kindling) went to piles made without the flags all along; stone
  twins did not. This fits a difference in the per-inorganic parts of a pile.
- `canStoreItem`, asked during the test with the flags lent, answered no for
  piles 1 and 2 on both gravel twins, and no for the non-twin control (a green
  steel dust whose own material may not be stockpiled either). The new pile was
  not yet there to be asked, so whether it is a true acceptance test is not
  settled.
- The test's end report is not in the log: it was uploaded before the held
  window ran out.

This fits the loads before it: every load where the gravel went nowhere had
its piles made before any window opened; on the fifth load, where all 23
went, the first window opened eight seconds after the start. It does not
explain the route 2 exposure test, where DF filed 24 floor gravel into an
older pile, so creation time alone may not be the whole rule.

**Next measurement: `refinish-stockpile-windows piles`.** Every pile's own
`canStoreItem` answer for a stone twin and a wood twin, asked with the flags
lent and with them off in the same tick. Then every pile's settings, storage
and flags compared field by field against the newest pile, grouped by field,
with the differing index ranges and how many of them are stone twin indices.

---

## 14. The piles' twin entries: found, and the mirror (ninth load, 2026-09-27)

The observation going in: everything that was stored involved something
that did not exist in the save. A pile made during the load, or kindling made
for the first time, went through; gravel from the save did not.

**Measured by `refinish-stockpile-windows piles`** (piles 1 and 2 made while
paused before any window, pile 3 made during the test's window):

- **Pile 2 against pile 3:** the only settings difference is 93 entries of
  `settings.finished_goods.mats`, exactly the 93 stone twin indices
  (323-415): **0 in pile 2, 1 in pile 3**. The only other difference is
  `max_bins`.
- **Pile 1 against pile 3:** the same 93 twin entries differ, along with other
  finished goods materials and the Wood entry of `other_mats`, so pile 1 was
  set up differently to begin with.

**What that means.** A stone twin is filed only where the pile's own entry for
that twin is on. DF's pile presets turn on only the materials DF lists at the
time, and it lists a stone twin only while the twin has its stone's flags. So
a pile made while the flags are off leaves every twin entry off, and a pile
made during a window turns them on.

This accounts for the earlier loads:

- **Kindling** files under the single Wood entry of `other_mats`, not per
  material, which is why it went to piles made either way.
- **The fifth load** filed everything because its piles were made after the
  first window opened.
- **The route 2 exposure test** filed gravel into an older pile because the
  earlier slot probe had forced the twin entries on in it. That probe also
  showed the entry alone is not enough: with no flags, nothing moved.

"New things work" was what the timing of these made visible: new piles
were made during windows, and new kindling never needed a per-material entry.

**The read that hid it.** These settings vectors read as 0 and 1 in play, and
0 is true in Lua. The STUCK report tested the entries by truth alone, so it
printed "these materials 3/3" for piles whose twin entries were all 0. Every
settings entry in the service is now read through `truth()`. Any earlier count
of settings entries taken by truth alone, including the stockpile probe's, is
suspect.

**canStoreItem is not a pile's acceptance.** It answered no for pile 3 while
pile 3 was taking the gravel. It is no longer asked.

**The fix: the mirror.** RM keeps each stone twin's finished goods entry equal
to its stone's entry, in every pile. The player's choice for granite in a pile
is the choice for granite gravel, and the twin never has to appear in the
settings menus. It runs at every backstop scan, when a window opens, and at
every recount while one is open, so piles made or edited at any time follow.
Windows are still needed: the entry is one half, the flags lent while DF looks
are the other.

---

## 15. Working, with the mirror (tenth load, 2026-09-27)

Gravel and kindling now stockpile, alongside DF's regular hauling. From the
log:

- **The first scan set all 93 twin entries in pile 2** to match their stones.
  Pile 1 has granite, jet and lignite off, and so has their twins off.
- **The mirror followed edits in play.** With granite turned off in pile 2, the
  next STUCK read twin entries on 2/3 against their stones' 2/3. With granite
  turned back on, the mirror set that one entry back.
- **Everything ended up on piles.** 23 twin items, then 28 once kindling was
  made.
- **Both stalls came while DF's hauling queue was busy** (storage jobs 13 of
  12, then 10 of 12), not from a refusal. The next windows finished the job.
- **Two gravel landed on the floor** right after granite was turned off (the
  census read 2 on the floor). The dwarves carrying them lost their
  destination and DF set them down. Both were hauled once granite was back on.

**Duplicate names in the settings.** While a window is open, the twins have
their stones' flags, so DF lists them in the stockpile settings: two granites
showed, and both were turned off. With the window closed, only one granite shows.
With the mirror, the real entry governs: turning the twin's entry off alone
is undone at the next recount. So the duplicate is harmless, but it is
confusing.

**Decision: label them.** The twin's row reads "granite (aggregate)",
with the tag in the menu only, never on the material or an item. See section 16.

---

## 16. The menu label (2026-09-27)

**What the screen holds.** Each row of the stockpile settings screen is DF's
own UI record: `game.main_interface.custom_stockpile.spec_item[i]`, a
`custom_stockpile_itemst` in df-structures. It carries the label strings
`name` and `simple_name`, and `set_pointer`, the address of the one settings
entry the row toggles.

**How the label works.** A row whose `set_pointer` lands on a stone twin's
entry, in any of the pile's inorganic lists, gets " (aggregate)" appended to
both strings. The service finds the entry by address against the base of
each list: `stone`, `ammo`, `coins`, bars and blocks, rough and cut gems,
`finished_goods`, `weapons`, `armor` and `furniture`. The tag comes from the
claim's new `menu_tag` option, which the aggregate sets to 'aggregate'. Only
the screen's row strings are written: the material's and items' names come
from the material, and DF rebuilds the rows from it.

**Paused, per DFHack.** DFHack's `World::ReadPauseState` counts the game as
paused while `custom_stockpile.open`, so the window's own loop does not run
there. Whether the game itself stops is another matter: the same list includes
`job_details.open`, and in play the game kept running in the material selection
menu (section 17). The label runs from a second dispatcher
subscription with `paused = true`, every 2 frames. It does nothing unless the
screen is open and a window is lending the flags; with no window, no twin is
listed.

**The mirror still governs.** A labelled row follows its stone. Toggling the
labelled row alone is set back at the next recount.

**Checking it.** With a pile's settings open, `refinish-stockpile-windows menu`
dumps each row's label strings, the entry it toggles, and whether that entry
is a stone twin's. If no row is labelled, that dump shows whether the
addresses matched.

---

## 17. Hiding the twins in the menus (2026-09-27)

**Decision: hide them, and keep the label as the fallback.** A twin is a
tool made of its stone, which is how vanilla sorts it: piles separate tools only
by item type and material. So no menu needs the twin as an entry of its own. A
gravel-only pile would need one, but it would be an outlier among tools, which
cannot be sorted that way either.

While a window lends the flags, the twins show in two menus. They are hidden
differently, because **the game does not pause in the material selection menu**
(seen in play), whatever DFHack's pause reading lists.

- **The material selection menu** (`game.main_interface.job_details`).
  - Its rows have no label strings. They are parallel value vectors:
    `material` (mat_type), `matgloss` (mat_index) and `material_count`, plus
    the unfiltered `_master` copies. DF draws each name from the material, so
    the label cannot reach it.
  - The flags are never touched there, and hauling goes on.
  - Instead, twin rows are **erased** from both sets of vectors, kept in step,
    on the frame after DF builds or rebuilds the list. A twin shows for one
    frame at most, and a stone twin and a fuel wood twin are handled alike.
- **The stockpile settings screen** (`custom_stockpile`).
  - Its rows are pointers to structs DF allocated, with separate size counters
    (`cur_spec_item_sz`), so erasing them could make DF read past the end.
    They are not erased.
  - Instead, while the screen is open **and the game has actually stopped**
    (`df.global.cur_year_tick` unchanged for two frames, measured), the
    window's flags are taken back, so any list DF builds then carries no twins.
  - The flags are lent again on the frame the tick moves or the screen closes.
    If the game keeps running there, nothing is touched.
  - Rows DF built before the flags came off keep the "(aggregate)" label until
    DF rebuilds the list.

The window record now keeps each flag's lent value as well as its old one, so
taking the flags back and lending them again costs one write per recorded flag,
with one material lookup per twin.

**Checking it.** `refinish-stockpile-windows menu` now also reports the
material selection menu when it is open: its row counts, how many rows are
twins, and the first rows' material addresses. The MENU lines in the log say
when twin rows were removed, and when the flags were taken back and lent again.

**No fuel wood tag.** The fuel wood twin does not appear in the stockpile
settings (wood is one entry there), and the material menu cannot be labelled,
so a fuel wood tag would have nowhere to show.

---

## 18. Verified in play (2026-09-27)

In play: everything hides correctly in both menus, kindling included, with no
hauling conflicts despite deliberate attempts to cause them. From the log:

- **The mirror set 93 twin entries at the first scan**, and a window opened on
  the 23 twin items sitting in workshops.
- **The stockpile settings screen stops the game.** Measured, not taken from a
  pause list: the flags were taken back five times while the screen was open
  and the tick stood still, and lent again each time within a few seconds of
  the screen closing.
- **174 twin rows were removed from the material selection menu** each of the
  three times it was opened.
- **The one STUCK came with DF's hauling queue full** (storage jobs 12 of 12),
  after a window that had hauled steadily for 19,700 frames. The window
  reopened 20 seconds later for the remaining 9.
- No errors.

**Refinement, built after this load.** A stall that happens because DF's
queue is full no longer closes the window or grows the retry wait: while storage
jobs on the Any row are at or above the haulers, the stall clock stands still.
When the queue frees, the loose twins' storage timers are set short again,
since every look DF took while it was full raised their delays. A fort with no
haulers at all never counts as full.

**Probes now retired, for refinish_metal_tools:** refinish-twin-exposure.lua,
refinish-haul-post.lua, refinish-haul-capture.lua and
refinish-stockpile-probe.lua. The service keeps its own diagnostic commands
(status, check, test, piles, menu).

**The full-queue hold, in play (2026-09-27).** One window stayed open 30,075
frames through a busy queue and closed with nothing loose: the census then
read all 84 twin items on piles. The queue flips between full and one short
every few seconds while DF hauls, so the release line fired about 80 times in
that window. It is now logged once per window, and the window's closing line
reports the count.

---

## 19. Coal (2026-09-27)

Making Fuel's coals are BARs of plant materials on the coal host
(`PLANT_MAT:MAKING_FUEL_COAL_HOST:<KEY>`, ten materials), because a bar of an
inorganic displays "charcoal bars" while a plant-mode bar displays a bare
"charcoal" (making_fuel_bar_naming.md). A suffix there is a seam at the
centre of the module and to be avoided if at all possible, though not at the
cost of function. Since the move, no coal stockpiles.

**Why, from df-structures.** A bars pile takes a bar through one of two
lists:

- `bars_blocks.bars_mats`, one entry per inorganic material. Plant coal has no
  entry here.
- `bars_blocks.bars_other_mats`, five named entries: Coal, Potash, Ash,
  Pearlash and Soap.

**The vanilla precedent.** Coal, Potash, Ash and Pearlash are DF's builtin
materials. Soap is not: vanilla soap is a plant or creature material
(`PLANT_SOAP_TEMPLATE` and `SOAP_TEMPLATE` in
vanilla_raws_reference, both carrying `[SOAP][SOAP_LEVEL:2]` and
`[REACTION_CLASS:SOAP]`), made into a BAR at the soap maker, and it displays
bare, as in "linseed oil soap". So vanilla already stockpiles one kind of
plant-mode bar, under Soap. Whether the SOAP flag is what files it is an
inference, not yet measured.

**The probe: `making-fuel-coal-probe`.** `soap [frames]` sets the SOAP flag on
every coal host material for the given unpaused frames, and sets loose coal
bars' storage timers short. It then logs every job that takes a coal bar
(storage jobs with the pile they are bound for, and any other job as OTHER)
and where each bar ended. Setup: one bars pile with only Soap on, one with
only Coal on, and a hospital if the fort has one.

**What the answer decides:**

- **If coal files under Soap:** a window route keeps the bare names. The
  settings seam (coal following the Soap entry, not Coal) and anything that
  takes coal as soap while the flag is lent (OTHER lines) are then the design
  work.
- **If not:** every remaining route carries a seam:
  - inorganic coal: the "bars" suffix, which no flag suppresses;
  - builtin coal in transit: names change mid-haul, and DF's own fuel filters
    and the coal exterminator see builtin coal;
  - RM moving coal itself: no dwarf carries it;
  - another item type: rewrites the fuel system.

**Measured (probe, 2026-09-27).** With SOAP set on all ten coal host
materials, 138 storage jobs took coal, every one bound for the pile whose only
named bar entry was Soap, none for the Coal-only pile, and 58 bars were stored
within 6000 frames. So the SOAP flag is what files a plant-mode bar under Soap.

- **One CleanPatient job took a coal ash bar** out of a workshop to wash with,
  41 seconds in. From earlier finishing tests: any bar whose material
  carries SOAP, even a metal bar, is used up bit by bit like soap.
- **Stragglers.** When the probe put the flags back on its fixed timer, 10
  coal bars were mid-haul (5 carried, 5 reserved), and DF set them down
  unfiled. The window service never closes mid-haul.
- **Unexplained.** One coke breeze was found marked for dumping. The probe
  never touches that flag; in RM, only the coal watcher sets it, copying it
  from the builtin bar it replaces.

---

## 20. Coal: the soap switch (built 2026-09-27)

The requirement: coal follows a pile's Coal entry and takes priority over
loose soap (dwarves drop soap a lot), provided every seam can be made
invisible.

**The claim.** `making-fuel-coal-watcher.lua` claims every coal host material
with `file_as = 'coal'` and item type BAR. The window service treats loose
coal like any claimed item: windows, timers, the census, never closing
mid-haul, and the full-queue hold.

**What the switch does.** While a window has coal engaged:

- **Coal is soap.** Its materials carry SOAP.
- **Soap is not.** Every real soap material present on a bar loses SOAP,
  newly seen ones at each recount, so real soap is neither filed nor used
  while coal is hauled. Soap already stored has no category meanwhile, so DF
  has nowhere to move it.
- **The Coal entry rules.** Each pile's Soap entry is set to its own Coal
  entry. The player's own Soap entries are kept and put back at the window's
  close, and while a pile's settings are open with the game stopped, so the
  screen always shows the player's own Soap entry. A Coal edit made there is
  followed when the flags are lent again.
- **Nothing washes with coal.** Any job that takes coal as soap is cancelled
  on sight: CleanPatient, CleanSelf, StoreItemInLocation, or any job whose
  filter for the coal carries the soap bit (`job_item` `flags2.soap` or
  `flags3.soap`, "check for material flag SOAP"). Storage jobs and fuel use
  go through. The first stop in a window is logged, and the close line gives
  the count.
- **Soap in hand is left alone.** Coal is engaged only when coal is loose and
  no job holds a real soap bar. Until then the window runs without coal, and
  engages it at a later recount.
- **Menus.** Coal rows are pruned from the material selection menu only while
  coal is engaged. Outside a window, coal is a real material that menus may
  list on its own.

**Saves.** The switch writes pile settings, which saves carry. RM stops every
service before a save is written (the save integrity rule), and stop() closes
the window, so a save never holds a switched entry.

**In play (2026-09-27): it works.** Two seams were found, both closed since.

- **Soap lost its look.** DF draws a soap bar with its own tile only while the
  material carries SOAP (vanilla `graphics_items.txt`:
  `[TILE_GRAPHICS:ITEM_CONSTRUCTION:1:1:ITEM_BARS_SOAP]`, beside the plain
  `ITEM_BARS` at 0:1), so set-aside soap drew as a plain bar. Now, while a real
  soap material is set aside, its `bar_texpos` slot holds that tile. The tile
  is resolved through the live page registry (`df.global.texture.page`), the
  way the sprite engine resolves `PAGE:<token>:<x>:<y>`, and the slot goes
  back with the flag. A material bar slot outranks the SOAP choice: the coals
  carry art in theirs and kept it while they carried SOAP. A soap material with
  art of its own in that slot is left alone.
  - **Tinted.** DF never tints a texpos handed to a material slot, so the raw
    tile drew in its sheet's grey (seen in play). The slot now takes RM's own
    tint of the same picture: `vanilla_soap_bar` (refinish-sprite-art-vanilla.lua,
    the ITEM_BARS_SOAP cell retoned onto the neutral ramp), made in each
    soap's own colour by `refinish-sprite-art`'s `texpos_for`. The raw tile is
    the fallback.
- **Bins added later.** DF bins what a pile holds when bins arrive, but only
  what it can file. So coal stored before the bins came lay unbinned until new
  coal opened a window, while real soap was binned at once. Now a claimed item
  lying unbinned on a pile counts as loose when the pile allows bins and one
  of its bins has room for it. Room is the bin's capacity less the volume of
  what it holds, against the item's own volume. The census names these "on a
  pile, to bin". This covers the twins as well as coal.

**Measured: soap use is shut out while coal is engaged.** With a hospital in
the fort, one window of about two minutes stopped 5 jobs that took coal as
soap (CleanPatient among them). A fort making coal constantly would keep soap
from being used almost entirely. The question was whether circumstances
could be detected that should give soap priority instead. Two signals are readable:

- **A hospital asking for soap.** A hospital location
  (`abstract_building_hospitalst`) carries `contents.need_more.soap`
  (`NEED_SOAP` in `location_info_flag`) and `contents.desired_soap`.
- **A soap job stopped.** The switch already counts every job it cancels for
  taking coal as soap.

**Built, then made loop-free (2026-09-28): soap gets its turn.**

- **The rule.** One job stopped for taking coal as soap means soap is wanted,
  and coal hands soap back at once: only coal's share of the record is
  written back and dropped (`release_coal`), and the window stays open for the
  twins.
- **Soap's turn.** For at least 2000 frames coal is not engaged, and it also
  waits while any job holds real soap, so a soap job keeps its turn for as long
  as it takes. The reposted job finds real soap, or with none in the fort goes
  ahead without it, as vanilla would.
- **Why no guaranteed coal turn, and no waiting for coal in flight.** A
  loop of cancelled jobs would be a big issue, and a few hundred frames is not
  long for a job to finish. The first build gave coal a 2000 frame turn in
  which stops were only counted, and waited up to 500 frames for coal in
  flight before releasing. In both, DF could repost a soap job, meet coal
  again, and have it cancelled again. Now at most one job is cancelled per
  coal turn, and a coal turn begins only after soap's.
- **The cost.** Coal being carried at the moment soap is wanted is set down,
  lies loose, and goes on coal's next turn.
- **Loops, checked case by case.**
  - **Cancellations.** The only place the service cancels a job is a job
    taking coal as soap. The first such cancel releases coal in the same tick,
    so no second job can meet coal: never a tight loop. A new coal turn needs
    at least 2000 frames and no real soap in use.
  - **Everything else that repeats is bounded.**
    - Stalls back off, doubling to 32000 frames.
    - Menu hiding happens only with the game stopped, so no job decides
      anything meanwhile.
    - Settings writes are the player's own or restore the player's own.
    - Timer resets only prompt DF's own storage looks.
  - **The one slow repeat left.** A demand real soap cannot meet: a hospital
    wanting soap in a fort with none, or a modded reaction that consumes soap
    (no vanilla, RM or Making Fuel reaction does). Soap's turn cannot serve it,
    so each coal turn meets it once: one cancelled job per coal turn. A
    cancelled repeat job is gone for good, which matters only for such a
    modded reaction set to repeat. Three soap-wanted releases running with no
    real soap anywhere log a WARNING, once per session.

In play, without a hospital, on the first build (2026-09-27): when bins were
added, most of the coal was binned, then the soap had its turn, then the rest
of the coal. In the harness, on this build: one stop cancelled one job
and released coal at once; the reposted job took real soap and nothing more
was cancelled; coal waited while that soap was in use.

**In play with a hospital (2026-09-28, this build).** One window, 7200 frames
(100 frames a second):

- Coal engaged when the window opened, with 1 real soap material set aside.
- 14 seconds in, a CleanPatient took coal as soap. It was stopped, and coal was
  released in the same tick. No other job was cancelled before the log ended.
- In those 14 seconds 21 coal bars were filed, and 5 being carried were set
  down on the floor.
- Coal next engaged 88 seconds after the release: soap's 2000 frames, then a
  job held real soap at every check after them (each recount, and the reopened
  window), which is the only thing that keeps coal off past soap's turn.
- No unmet-soap WARNING, correctly: the fort had real soap.

**The seam it showed, and the fix: soap's turn holds the stall clock.** With
coal waiting and nothing else fileable (the test piles take no finished goods,
so the 23 gravel could not file), no haul came for STALL_FRAMES. The window
closed as stuck, its STUCK report listed 61 coal items (56 cinders, 3 coal ash,
1 coke breeze, 1 green coke) as "could not be stockpiled" when they were only
waiting their turn, and the retry wait doubled. Now, while loose coal waits out
soap's turn, the stall clock stands still, as it does for a full hauling queue
(section 18): the window stays open, coal engages at the first recount after
soap's turn, and a STUCK report lists only items that had their chance. The
hold is logged once per window. Coal already waited for as long as a job held
real soap, so the hold adds no wait of its own.

**The hospital flag was considered and left out: the overlooked trap.** While
coal is engaged, the hospital's own stored soap is set aside too, so DF could
read the hospital as short because of the switch itself, and cut every coal
window short in a loop. A stopped job is something the switch cannot cause.

**Known costs.**

- Coal being carried when soap is wanted is set down, and goes on coal's next
  turn (5 bars in the hospital run).
- With a hospital, a coal turn lasts until the first soap job meets coal (14
  seconds in the hospital run), and soap's turn lasts at least 2000 frames and
  for as long as real soap is in a job.

The first build's costs and harness results (a guaranteed coal turn that only
counted stops, each side getting about half the time, and a release that waited
up to 500 frames for a haul in flight) went with it: see "Why no guaranteed
coal turn, and no waiting for coal in flight" above.

**The coal bin picture (2026-09-28).** A bin holding module coal draws
plain bars on the bin, while a bin holding the menu key (builtin coal) draws
the coal picture. On the ground, module coal draws its own art from its
material's `bar_texpos` slot, so the bin picture comes from elsewhere.

- **What vanilla's graphics offer.** Bars have one plain tile, `ITEM_BARS`,
  and four named ones keyed by builtin material: POTASH, PEARLASH,
  COAL:COKE and COAL:CHARCOAL (`BARS_GRAPHICS`). A bin has one tile,
  `ITEM_BIN`, and `item_binst` carries no picture of its contents.
- **The first lever tested, and ruled out (probe, 2026-09-28).** `item_barst`
  has a `subtype` field whose df-structures comment reads "originally used for
  coal". `making-fuel-bin-probe read` showed the menu key (#1785, builtin COAL)
  carrying subtype -1, like every module coal bar, so the field is not the
  lever.
- **Also seen.** The bin holding the key among 70-odd module coal bars is the
  one that draws coal. The picture seems chosen by whether builtin coal is
  inside.
- **Parked (may not be worth fretting over).** The probe is retired, for
  refinish_metal_tools.

**Open points, to watch in play:**

- Real soap that is loose, not in a job, when coal engages waits until the
  window closes.
- Whether the stocks screen shows coal under soap while a window is open.
- All ten host materials follow the Coal entry, coal ash and cinders
  included. Coal ash could follow Ash only through separate windows, since the
  Soap entry is one switch per pile.
- The coke breeze marked for dumping (section 19).

---

## 21. Editing rows out of the settings screen (2026-09-28)

**The hole.** The flag take-back of section 17 cannot reach every list. Coins
holds every inorganic, flags or not (839 of 839 rows in play, evil clouds and
frozen liquids included), so every aggregate twin showed there, labelled. And
a listed binder twin (stone clay) is stone for good, so it showed in the stone
pile's Other stone beside the real clay under Clay.

**What the screen does, measured** (refinish-menu-probe: read only, then one
write test):

- `custom_stockpile.spec_item` is a pool with one row per inorganic. DF never
  allocates or frees a row while the screen is open. A list switch reorders
  the pool so the list's rows come first and sets `cur_spec_item_sz` to how
  many belong to it (Coins 839, Stone ores 16, Other stone 87, Goods
  Stone/clay 121).
- The search filter moves nothing. It sets each live row's `on` flag (the name
  matches; not the pile's setting) and sets `counted_cur_spec_item_sz` to how
  many are left on.
- Rows turned off from outside, with that count lowered to match, stayed off
  for hundreds of frames with no keystroke and vanished from Coins: no blank or
  repeated rows, no doubled clays, toggling a neighbour unaffected. A keystroke
  brings them back, since the filter recomputes both.

**The edit.** The window service does what the filter does, every frame the
screen is open: each live row that is on and toggles a twin's entry, or a
hidden material's outside its keep lists, is turned off, and the count is
lowered by as many. Nothing is moved, freed or erased. A coal claim's rows are
left, coal being a real material the screen may list. A row edited out carries its
tag, so it reads what it is if it ever shows; a row that stays listed never
does, and a tag it picked up in another list comes off. The material
selection menu erases hidden materials' rows with the twins'. The flag
take-back stays, for the Soap entries.

**Hidden materials.** A call beside `claim`: `hide(owner, select, opts)`, for
materials that are not windowed twins; `keep_in` names the settings lists
where their rows may stay. In use: the stone clay twins, kept in
`finished_goods.mats` only, unlabelled, since there they are the real
entries; and Making Fuel's key
materials (the drain keys, the rot key, the cremation keys), kept nowhere,
which also carry SPECIAL in their raws. The module's own stone class
materials (char, dung, the soaps and papers, concrete, slag) are listed in the
stone lists as well, and are left there by decision.

**Goods Stone/clay is IS_STONE.** It held 121 rows: the 93 stones on disk plus
28 RM stone materials. Vanilla's ceramics carry IS_STONE, which is why they are
listed there and have aggregate twins; a material marked ceramic alone would
not be.

