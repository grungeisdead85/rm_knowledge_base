- **Profiler:** the old butchery sweep cost 3 to 4 ms a second, a closure per
  item across 15,000 items, until it asked item type first. The stacked-skin
  watcher kept that sweep at first and reached 5 to 10 ms a second, top of the
  profiler, so on 2026-09-26 it moved to the item created event with a tail
  backstop and a look over its own stacks. The sprite trace cost 2.6 ms a
  second.# RM Hide Wing Lessons

What Making Fuel's glob hide wing learned, kept after the wing itself was
retired.

From 2026-09-11 to 2026-09-26 the hide currency was a GLOB of a per species
injected inorganic, run by five scripts (`making-fuel-hide-watcher`,
`-hide-mats`, `-hide-chain`, `-hide-rot`, `-hide-sprite`) and two reactions
(`COMBINE_PARTIAL_SKIN`, `PROCESS_SKIN`). On 2026-09-26 it was replaced by DF's
own skin carrying a count in `material_amount.Leather`, with the remainder
handed back whenever a job uses a stack. The replacement is one file,
`making-fuel-hide-watcher.lua`, and it worked on its first test.

Everything below was paid for in play. MEASURED means observed in game, with
the run or date where the source recorded one. Anything not measured says so.
The retired files hold the code behind each entry; they belong in
`refinish_metal_tools`, since the mirror copies go when the files are deleted.
`RM_Material_Sprite_Redirect.md` keeps the full record of the sprite redirect,
and `RM_Organic_Category_Registration.md` the stockpile registration.

---

## 1. Why the glob was retired

**One texture entry draws every glob that is not fat.** MEASURED. The redirect
pointed that entry at the hide art, and every solid glob on screen wore the
hide in the same frame as our skins. Tallow was the one seen. Paste, press
cake, wax cake, paper slurry and the module's own paper pulp globs are on the
same entry by the same mechanism, though none was seen. One entry holds one
value per frame, so no gate could separate them.
That is structural, not a bug in the gate.

**The requirements the hide wing was held to.** Skins must wear the
chosen sprite, gain a rotten prefix without rotten copies of every material,
stack or over-dimension, and have a selectable stockpile option. They must not
break other sprites, must not be taken by reactions seeking their item type,
and must not be revealed as fake (miasma was the one accepted compromise).

**What else was tried, and what failed it:**

| Route | Result |
|---|---|
| CHEESE of the hide material (2026-09-26) | Sprite, name, rotten prefix and stack all passed. Dwarves ate it by item type, and the first run with the material missing from CreatureCheese most likely crashed DF. |
| TOOL (2026-09-26) | Stacked ("dingo skin skins [5]"). DF prints no "rotten" on a tool with the flag set, and never rots tools. |
| BAR (2026-09-12) | No rot, no recognised rotten state, no miasma. |
| A glob of the creature's own SKIN (2026-09-12) | Drew the same shared tile. So did LEATHER. Only FAT drew its own. |
| A rawhide body part pointed at another material (2026-09-26) | The material moved, the name and rot did not, and the sprite went to a raw body part. See section 4. |

**What replaced it.** A skin is already a hide in every way DF knows: its own
art, rot, the rotten prefix, miasma and refuse pile settings. The only thing it
lacked was a count that pays, and handing the remainder back supplies that.

---

## 2. Globs as items

**DF cleans a glob that lacks DO_NOT_CLEAN_GLOB, as spatter.** MEASURED. Four
globs spawned together, then unpause: llama SKIN (ROTS, no clean flag) gone,
llama FAT (has the flag) survived, ours with ROTS gone, ours without ROTS gone.
Rot was never what removed them. Isolated afterwards on three materials:
DO_NOT_CLEAN_GLOB alone survived, STOCKPILE_GLOB alone did not. Still live:
Making Fuel's `MAKING_FUEL_PAPER_*` pulp materials declare no material flags,
so a pulp glob left unforbidden may be cleaned away (unverified on pulp).

**STOCKPILE_GLOB does not keep a glob alive.** It is what makes it a glob
stockpile item, hauled and stored rather than left where it was made.

**DF never rots a glob.** MEASURED on a vanilla llama fat glob, loose, in a
fort where corpses rotted normally: `rot_timer` climbed to 199 and reset to 0
(age 8138 to 8140), with nothing else on the item moving. It recycles at 200
and never sets `flags.rotten`. So a glob never takes the rotten prefix, never
gives miasma and is never removed on its own, whatever its material says.
`age` (ticks since creation, never reset) is the clock that works. Setting
`flags.rotten` by hand makes the name, the miasma and the rot watcher follow,
because all three are DF reacting to its own flag.

**A glob reagent's quantity is DIMENSION.** MEASURED on jobs 370 and 375: DF
took exactly 1 from each of two 36 dimension partials and left 35 in each, so
the next job claimed the same two items. For a dimensioned reagent DF checks
available dimension rather than distinct items, so one 7 dimension glob
satisfies two slots asking for 1 each and the reaction never goes red. DF
dispatches a hauler for every slot the moment a job posts, so sealing slot B
after slot A binds is already too late.

**A glob can be stacked AND dimensioned.** MEASURED, water buffalo fat, job 15:
the item read "[9]" at getVolume 540, and one run took it to "[8]" at 480. The
total held is stack times dimension, and a reagent of 150 took one unit.
(Recorded in `refinish-reaction-adaptive.lua`, which still relies on it.)

**Heat decides whether a glob exists.** MEASURED. A test glob on an RM
inorganic that melts at 9896 and boils at 10180 sat at fortress room
temperature, 10040: liquid at rest, and gone the moment the game unpaused.
Skin melts and boils at 60001, which is never. A glob material has to take the
whole heat block from a donor that stays solid, by `assign()`, since it is
seven values and one missed is a material that fails later.

**`butcher_special_type`.** Fat's material reads 75 (GLOB); an injected glob
material reads -1 unless it is set. It was the one structural field a material
diff against fat left standing, and the standing candidate for why our globs
hauled but were never barrelled while fat in the same pile was. Never
confirmed as the gate.

**`mat.absorption` does not exist on this build.** MEASURED: the write threw
for every material on every inject. Globs from a wet workshop read "laced with
water" and carry it through every later job.

**Which item classes carry what** (old watcher, 2026-09-11):
`item_globst` has `rot_timer` and `dimension` and no race; `item_meatst` has
`rot_timer`; `item_remainsst` has race, caste and `rot_timer` (and a race
cannot be created cleanly); `item_toolst` has neither. `item_globst` has no
`lp_flags` field (redirect doc O6).

**Glob sprites do not tint from `state_color`.** MEASURED by a live paint test.

**Still open:** whether two globs of the same material merge when stockpiled.

---

## 3. The texture entry and the redirect

The full record is `RM_Material_Sprite_Redirect.md`. The rules that outlive
the hide use:

- **The graphics raws are an initializer.** At load the parser bakes every
  TILE_GRAPHICS line into the `gps.texture_indices` tables, and the renderer
  reads the tables live. Rewriting an entry re-aimed the sprite on screen,
  including globs that already existed. MEASURED 22:41.
- **The shared entry is ITEM_LIQUID** (ITEM_NATURE:0:1), `texture_indices7[137]`
  on this build and the only holder of its value. Every glob but fat, and every
  LIQUID_MISC and DRINK without art of its own, draws from it. Fat draws
  BODYPART_FAT. Skin and leather globs were on it (2026-09-12, "every one is
  the same white water sprite as ours except for the fat"), and tallow was
  (2026-09-26). The redirect doc's O2 said creature materials never touch it;
  that is corrected there. What gives fat its own art is unmeasured.
- **Solids read the entry live every frame; liquids resolve it once and keep
  it for the session.** A liquid that first draws while the entry is redirected
  wears the wrong art until restart. Every latch on record happened on a screen
  listing contents: an item sheet on a barrel, a workshop's Items list, a unit's
  inventory, a stocks list.
- **A blacklist of screens failed twice.** Only a whitelist of screens known
  unable to draw a contained liquid held.
- **`getCurFocus` reports only the topmost viewscreen.** With the DFHack
  launcher open over a stocks list it answered `dfhack/lua/launcher` while the
  drink list kept drawing beneath (recorder, 19:08:49 to 19:08:56).
  `dfhack.gui.getDFViewscreen` returns the screen actually drawing.
- **Stocks builds and draws a category's list on the frame the player crosses
  into it.** A gate polling every two frames is late by construction; only a
  one frame tripwire on `stocks.current_type` (a `df.item_type`) closed it. An
  empty `current_type_i_list` means not built yet, not empty.
- **Time a first write in TICKS, not frames.** Ticks do not advance while
  paused, and a reloaded fort comes up paused. MEASURED twice, the second time
  by switching to frames: after autosave, exit and reload, dwarven ale took
  HIDES:0:3 and kept it.
- **The gps tables rebuild** on graphics reload, a resolution change or any
  renderer reinit, holding vanilla again, possibly at a different index. Verify
  every poll and re-find from scratch.
- **Never find the entry by searching for the target value.**
  `texture_indices8[43]` holds the HIDES page's own registration of the same
  texpos, and adopting it redirects the page instead of the pointer.
- **No per item render result is readable anywhere.** The item struct, the
  material struct, `view_sheets` and all eleven gps tables were searched. The
  texpos an item drew with lives in the renderer's own memory; judge art by eye.
- **`world.frame_counter` is game time** and stands still while paused, which
  is exactly when sheets get opened. UI timing needs its own counter.
- **Every page carries a greyscale twin, `texpos_gs`, with zero holders in
  gps.** Unexplained.
- **A hotsave never unloads the map.** A watcher whose `stop()` runs only on
  SC_MAP_UNLOADED keeps running through RM's clear, quicksave and rebuild, and
  the save is taken with its state live. `refinish-autosave.lua` had to stop
  the sprite watcher itself. Any module holding RAM state across a save needs
  the same.
- **Log every transition that can do damage, and trace state, not decisions.**
  A decision log cannot answer an ordering question; one second is sixty frames
  and a latch lives in one of them. A frame stamped state trace that prints
  only on change settled it, and cost 2.6 ms a second, so it stayed off unless
  asked for.

---

## 4. Corpse pieces and skins

**Butchery pays one skin per animal, any size, and writes nothing on it.**
MEASURED 2026-09-11. Butchery writes a resource flag and a count for bone, horn,
hoof and wool, and neither for skin.

**`material_amount.Leather` renders as a count on a skin.** MEASURED 2026-09-11:
"water buffalo cow skin [4]", the same way a bone with Bone(3)=16 reads "llama
bone [16]". Vanilla tanning ignores the count: it ate the whole [4] and
returned one leather. The current watcher is built on exactly this.

**RM's adaptive engine already treats that count as the pile.** It reads a
corpse piece's count from `material_amount`, raises its ghost reaction's
reagent to the whole pile, and credits all of it. DF consumes by the raws
reagent quantity; the job item quantity only governs seeking, and the engine
leaves it alone. So the current watcher reads the reaction's reagent to decide
what to hand back, and hands back nothing after this module's ash, char and
retort, which already paid for the whole stack.

**A corpse piece carries race and caste, and no material field.** Confirmed on
every piece of a 50 item dump. `item_corpsepiecest` has no `mat_type` or
`mat_index`; its material is `largest_tissue`. MEASURED by
`making-fuel-rawhide-probe` (2026-09-26): pointing `largest_tissue` at the
animal's LEATHER moved `getActualMaterial` (and so `dfhack.matinfo.decode`) to
LEATHER, while `getMaterial` read -1/-1 on both pieces. The name and the
rotting did not move; they come from the piece's layers. The sprite did move:
the piece drew as a raw body part instead of a hide. Whether job filters read
`getActualMaterial` on a body part was not tested.

**`createItem` alone cannot make a corpse piece.** It leaves race unset, and
`getDescription` then indexes `creatures.all[-1]`: two crashes on 2026-09-11
were put down to that. `modtools/create-item`'s `hackWish` is the route that
works. It writes race, normal_race, normal_caste, sex, largest_tissue,
largest_unrottable_tissue, bp_modifiers, body_part_relsize, body_part_status
and layer_status, and caste last. For a generic piece its `get_mat` returns
`ok, mattype, matindex, caste, bodypart, partlayer, generic`, and it reads the
partlayer as a position in the creature's own material list, found by name.
Read from its source, not measured: it makes MEAT for a layer name outside its
table, and cannot build a piece whose material no tissue uses.

**`hackWish` builds a skin as leather.** MEASURED side by side with a skin DF's
butchery made (2026-09-12):

|  | DF's skin | hackWish's |
|---|---|---|
| corpse_flags | rottable, use_blood_color | leather |
| material_amount | empty | Leather=1 |
| largest_unrottable_tissue | -1/-1 | the creature's own material |

Leather does not rot, so the timer stayed at zero a whole session, and the
token still decoded as SKIN, which hid it. Set all three to match DF's, or the
piece rots down and leaves something a real hide does not.

**CORPSEPIECE is a reagent type and not a product type.** No reaction can make
a body part; a watcher has to.

**`getVolume` returns 350 for every corpse** whatever the animal was. Size is
`caste.misc.adult_size`.

**A butchered skin usually sits inside the butcher's shop**, not on the tile
beneath it, and `getPosition` returns the tile either way. Ask
`getHolderBuilding`. `moveToBuilding` returns false rather than throwing.

**Refuse piles take skins natively.** DF sends a skin to a refuse pile and lets
it rot there, and the refuse settings carry their own `fresh_raw_hide` and
`rotten_raw_hide` switches (df-structures). DF also removes a rotten skin, which
it never does for a glob.

**Match a skin by its material token, never a flag.** DF sets no resource flag
on skin. The token stays `:SKIN` after a display rename, because id and
state_name are different fields.

**Anything that makes a raw skin must mark it before a butchery poll can see
it.** MEASURED 16:20:49: PROCESS_SKIN made #3390 "cow rawhide", and at
16:20:50 the watcher paid it back into currency. The mark goes in the same
synchronous call as the creation.

---

## 5. Materials, names and injection

**The creature name is a field on the material.** MEASURED:
`CREATURE:LLAMA:SKIN` has `prefix="llama"`, `state_name.Solid="skin"`. Writing
`prefix` on an injected inorganic works: a boulder of an RM material read
"llama frozen ammonia". A creature's display name comes from its own name
vector, not the lowercased token ("WATER_BUFFALO" is not "water buffalo").

**id and state_name are different fields.** Reagents, reactions and matinfo
match id; state_name is display only. MEASURED: renaming vanilla SKIN to
"rawhide" left matinfo resolving and tanning binding. A rename writes into a
string that already exists and allocates nothing, so it needs no save cycle,
and names come back from the raws on every world load. `ALL_SOLID` fills Solid,
Powder, Paste and Pressed.

**Restore a rename by reading the material, never by a remembered flag.** `_G`
outlives a world load and material names do not, so after a reload the skins
read "skin" while the flag still said renamed, and the rename refused. A table
keyed by race index is world specific. A name already reading the new word
must never be saved as the original, or the rename becomes permanent.

**Material class RAW has no clone donor.** Its CLONE_SIGNATURES entry is empty,
and the STONE fallback only runs inside a class evaluation, which happens only
for classes a module uses. A JIT material of an unwarmed class fails with "No
donor for class [RAW]". SOIL carries the same require_true as STONE and is
warmed.

**The clone preset brings flags the material should not have.** A hide came
with IS_STONE. `refinish-module-inject.lua` blanks every flag and rebuilds from
the preset, and flag overrides are applied last precisely so a preset can be
corrected.

**`assign()` copies a whole flag word.** Copying skin's flags wiped the four
glob flags the payload had chosen, which cost the glob its art, its stockpile,
its clean protection and its miasma. Put the chosen flags back after. Never
copy fat's word wholesale: REACTION_CLASS:FAT is what RENDER_FAT selects on,
and it hands the material to the kitchen.

**Reaction classes stay unprefixed.** DF prints the class at the workshop as
"Needs <CLASS> item".

**IMPLIES_ANIMAL_KILL belongs on an animal product.** Dwarves with the relevant
values object to owning it.

**A material injected mid session lands at the end of `inorganics.all`**, and
the next load injects it somewhere else. That is fine because RM records item
materials by token and rebinds them. But a material injected after startup is
absent from the ledger written at startup step 8: call `refinish-ledger`
`write()` after a JIT inject. It rescans the live array and refuses to
overwrite a good ledger with an empty one.

**A roster in site data survives the save; the materials do not.** The module
payload has to regenerate them from the roster on every load, or every item of
that species points at a material nobody injected. Fields the schema cannot
express are applied in `on_materials_injected`, after the engine injects.

**Roster rules.** An array of creature tokens in injection order, append only:
`pairs()` over a hash gives a different order every load. Tokens, not race
indices, which are world specific. And never cache a blank read taken before
site data is reachable: one early blank, re-added to and saved, wiped a fort's
roster of butchered species.

**Inject every tier or none.** A JIT inject that took only the whole tier left
every remainder homeless, and the log showed "1 missed" climbing by one per
creature.

---

## 6. Jobs, reagents and filters

**`onJobCompleted` fires after the reagents are consumed.** Snapshot what a job
holds while it runs.

**A hook on an event nobody enabled is never called, silently.** Nothing in
Making Fuel enabled JOB_INITIATED, and a file hooked on it printed its start
line and nothing else across a full run. Enable the event yourself.

**Reaction codes compose as `prefix .. "RXN_" .. key`**
(`refinish-module-react.lua`). Matching the wrong form is silent: the poll finds
none of its jobs. MEASURED twice.

**A reaction_class no material carries, written onto a filter, cancels a job
cleanly.** DF searches, fails and cancels it the way a furnace out of ore does.
A zeroed quantity instead leaves the job idling engaged forever, because DF
sees nothing missing.

**DF re-tests the live filter when a hauled item arrives**, so a filter sealed
to a chosen item has to still match it. `flags1.unrotten` survives a seal and
turns away an item that rotted in transit.

**An attached item in transit does not count toward the filter quantity.**
Left at 1, DF sends a second hauler for a second item. Zero it once the item is
attached.

**Reachability matters.** The first match in the world item list once sat
across a canyon, and a job sealed to an unwalkable item never completes.

**`items.remove` cancels any job attached to the item**, so disposal skips
`in_job` items and catches them next pass. Removing inside a walk of
`world.items.all` is safe: it marks for garbage collection and unlinks, and
does not splice the vector.

**Every walk gets a per item pcall.** One unreadable reference aborting a scan
once cost the module a whole feature.

---

## 7. DFHack script lifecycle

**`--@ module = true` does not stop the body running.** It only makes the file
reqscript-able. Without the CLI guard, every reqscript falls through to the
usage branch.

**The file body re-executes on reqscript; `_G` does not.** A file local
`running` flag reset for a new world while the `_G` state still held the old
world's texpos numbers, and restore acted on indices that now pointed at
something else: the two day sprite bug. A guard and the state it guards must
share one lifetime.

**DFHack keeps the Lua environment across a main menu reload and does not
re-execute an unchanged file body.** MEASURED by the frame counter: a cold
launch logged the first write at f1 and put VANILLA; a reload in the same
process logged it at f6256 and put HIDE. Same save, same code, opposite answer.
Reset per world state explicitly, in `start()` or on SC_WORLD_UNLOADED.

**Track body identity separately from running.** Otherwise repeat-util keeps
calling the previous body's closure while typed commands run the new code.

**Lua resolves globals at run time.** A missing `require` (for
`utils.listpairs`) compiles and throws on the first tick. A local is invisible
above its own definition: moving a function above what it calls compiles and
then fails with a call to nil.

Also learned while replacing the wing, from DFHack's source:
`repeatUtil.scheduleEvery` runs its callback once immediately; `cancel` from
inside the callback does stop it; and on a world unload repeat-util forgets
its registry without cancelling a pending frame timer, so a frame callback can
fire once after unload.

---

## 8. Stockpiles

**`raws.inorganics` is a struct holding several lists, not a vector.** The
vector is `.all`. Taking `#` of the container returns nothing, which produced
`inorganics=nil` while 767 was visible elsewhere in the same output.

**Acceptance and classification are separate gates.** Refuse piles with GLOB
enabled still never got a fresh hide glob: DF routed it to a food pile's Glob
category, exactly like fat. Registering a material in an enumeration makes it
addressable by a setting; it does not change what DF decides the item is.
Container type follows item type: registered hide globs hauled to a food pile
and were never put in a barrel. Full record in
`RM_Organic_Category_Registration.md`.

---

## 9. Numbers worth keeping

- **HIDE_ANCHOR 5000**, measured against the world's creatures: sheep 5000 is
  one skin, pig 6000 one, llama 18000 two, horse 50000 five, cow 60000 five,
  water buffalo 100000 seven. At 30000 every farm animal paid zero whole hides.
  Still in use.
- **Exponent 2/3** because hide is a surface and mass a volume. Not a dial.
  Sheep to giant sperm whale is 4000 times the size, and 4000^(2/3) is 252.
- **CAP_HIDES 10.** A giant splits into stacks of ten so several tanners can
  work it and whatever nobody reaches rots; every farm animal is one stack.
  One stack per animal was tried and reverted on 2026-09-26: only one job can
  hold an item, so a whale's 252 fell to one tanner, and with the rot timer
  resetting on every reaction run that tanner could keep all 252 fresh
  indefinitely. At ten the reset buys ten runs at most.
- **150 dimension is one glob unit**, the figure vanilla's RENDER_FAT asks for.
- **Fortress room temperature is 10040.**
- **21 days to spoil, 21 more to rot away**, the glob wing's own schedule. The
  reasoning: a tannery working the butchery queue clears a hide inside three
  weeks, and a hoarder loses them before the season turns. DF's native rot
  governs skins now.
- **`AGE_PER_DAY` is unverified**, and it is the same value
  `making-fuel-air-dry.lua` still uses. One calibration fixes both.
- **Profiler:** the old butchery sweep cost 3 to 4 ms a second, a closure per
  item across 15,000 items, until it asked item type first. The stacked-skin
  watcher kept that sweep at first and reached 5 to 10 ms a second, top of the
  profiler, so on 2026-09-26 it moved to the item created event with a tail
  backstop and a look over its own stacks. The sprite trace cost 2.6 ms a
  second.

---

## 10. Still open

- Whether two globs of the same material merge in a stockpile.
- What gives fat its own glob art: REACTION_CLASS:FAT, its RENDER_MAT product,
  or being the creature's fat tissue. A skin glob wearing fat's whole flag word
  was spawned on 2026-09-12 and never looked at.
- Whether a loose liquid item drawn on the plain map latches (the barrel test).
  It only matters if the redirect is ever reused.
- Whether `butcher_special_type` is what lets fat into barrels.
- Where DF keeps a skin's decay. A stack run through a reaction comes back
  with its rot timer at zero every time (2026-09-26), so `rot_timer` does not
  carry it: DF keeps the progress elsewhere, or resets the timer when the
  stack is handled. A recorder watching one skin until it rots would show
  which.
- Whether a material appended to a real creature needs clearing before a save.
  That was the preferred rawhide route, and it was not pursued once the name
  was shown not to follow `largest_tissue`.
