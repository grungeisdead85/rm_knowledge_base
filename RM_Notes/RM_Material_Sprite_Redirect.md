# RM Material Sprite Redirect

How Refinish Metal gives an injected material its own sprite by re-aiming a
baked texpos pointer, and how it avoids dragging every other material on that
pointer along with it.

Everything below is measured in game unless explicitly marked as untested.
Where a claim rests on a single observation, the run that produced it is given
so a future contradiction can be traced to it.

**Status, 2026-09-26: the hide use is retired.** Making Fuel's skins are DF's
own skins now, carrying a count (`making-fuel-hide-watcher.lua`), and
`making-fuel-hide-sprite.lua` is deleted. The redirect worked as described
here. It was retired for a reason no gate could fix: every solid glob that is
not fat reads the same entry live, so tallow wore the hide in the same frame as
our skins. The measurements stand as the record of the technique for any
future use, and `RM_Hide_Wing_Lessons.md` holds the rest of what the hide wing
learned.

**Read sections 4 and 6 before reusing the technique.** Section 4 is the
physics. Section 6 is the rule that follows from it and the reason the gate was
shaped the way it was.

---

## 1. The problem this solves

An injected inorganic material has no art of its own, so every skin currency
glob came out wearing **the water sprite**, the flask, identical to a stack of
water.

It did not look like fat. Fat is a glob too and has its own distinct sprite,
because it is a creature material and matches creature bodypart art. Being a
glob has nothing to do with which tile you get. What matters is whether the
material has art of its own; ours does not, so it falls through.

What it falls through to is the generic liquid tile:

```
[TILE_GRAPHICS:ITEM_NATURE:0:1:ITEM_LIQUID]
```

Our globs and every liquid item whose material has no art of its own both
resolve through that single declaration, which is the entire source of the
difficulty.

## 2. Why the graphics raws cannot be used directly

The raws are an initializer, not the graphics system. By the time a world is
loaded, each page's cells have been baked into integer texpos values and the
raws are no longer consulted. The material struct has no field for a liquid or
glob sprite, so there is nothing to dress the way `bar_texpos` or
`boulder_texpos1` can be dressed.

The baked pointer, however, is writable.

## 3. The pointer

```
df.global.gps.texture_indices7[137]
```

It holds the texpos of `ITEM_NATURE:0:1`. Verified as the **only** holder of
that value anywhere in `df.global.gps`: a depth 100 dump of the whole struct
contains exactly one line carrying it.

Do not hardcode the number. texpos numbering is assigned per session and
differs between loads of the same save, including between a save and a reload
of that same save in the same DF process. Observed vanilla values across
sessions: 42249, 137997, 137998, 138007, 138059, 138271. Always resolve it
live off `df.global.texture.page` by token and cell.

Finding the slot is a value search: resolve the cell to a texpos, then walk
`gps.texture_indices1` through `texture_indices11` for a slot holding it.

### Who is on this pointer

- Injected inorganic materials drawn as `GLOB`. Ours.
- Every other glob that is not fat, creature materials included. MEASURED: a
  llama SKIN glob and a llama LEATHER glob drew the same tile as ours
  (refinish-hide-probe, 2026-09-12), and vanilla tallow globs wore the hide
  while the redirect stood (2026-09-26). This is what retired the hide use.
- `LIQUID_MISC` and `DRINK` items whose material has no art. Water, booze,
  lye, and the Refinish scanner's injected liquids.

### Who is not

Fat. `CREATURE:WOLF:FAT` is a glob with art of its own, BODYPART_FAT, and never
touches this slot; fat kept its own sprite through every test. Being a creature
material is not what does it: skin, leather and tallow are creature materials
and all fall through. What fat has that they lack is unmeasured (its
REACTION_CLASS:FAT, its RENDER_MAT product, or being the creature's fat
tissue). A skin glob wearing fat's whole flag word was spawned on 2026-09-12
and never looked at.

### Blast radius, measured

`refinish-draw-probe census` on a live fort:

```
12 glob item(s), 3 distinct material(s):
  10   CREATURE:LLAMA:FAT                    own art, off the pointer
  1    CREATURE:WOLF:FAT                     own art, off the pointer
  1    INORGANIC:MAKING_FUEL_HIDEPART_WOLF   ON THE POINTER
```

Ours is the only glob on it. Plant globs, paste and pressed cake off a screw
press, should also fall through since no material carries glob art, but this
fort has none, so that remains untested rather than a present problem. Run the
census again on a fort that has them.

---

## 4. What is measured

Stated as observations rather than as a theory, because the theory that was
here before was wrong three times and the observations were not.

**O1. A material with no art of its own falls through to the liquid tile.**
Neither `GLOB` nor `LIQUID_MISC` has a material art slot, and the material
struct has no glob or liquid texpos field at all, so there is nothing to dress.

**O2. Fat never touches the pointer. Other creature materials do.** Census on
a live fort: 12 globs across 3 materials, ten llama fat and one wolf fat both
off the pointer, one of ours on it. This was first written as "creature
materials never touch the pointer", which the census could not show: fat was
the only creature material in it. Corrected 2026-09-26: skin and leather globs
(2026-09-12) and tallow globs (2026-09-26) are on it.

**O3. A material in its SOLID state reads the pointer LIVE, every frame.**
A marble glob on the ground, a skin glob in a stockpile, and a water glob
while still ice all follow a write immediately and follow a restore back
again, both directions, any number of times.

**O4. A material in its LIQUID state resolves the pointer ONCE and keeps that
answer for the session.** Writing the pointer afterwards does not move it,
while solids elsewhere in the same fort move normally.

The resolution point is the material **entering its liquid state and being
drawn**, not the item's first appearance. An item that starts solid and melts
resolves at the melt. This corrected a long-standing misreading; see O13.

**O5. A melted glob is still a glob.** It does not spill, it does not become
spatter, it sits on the tile, and dwarves clean it like any other item. No
conversion to a liquid item takes place.

**O6. `item_globst` has no `lp_flags` field.** Verified by the error text, not
inferred. Cleanup protection for a glob comes only from the material's
`DO_NOT_CLEAN_GLOB` flag. `lp_flags.no_auto_clean` is a liquid and powder
lever.

**O7. Our currency can never reach its liquid state.** `making-fuel-hide-mats.lua`
inherits the whole heat block from the creature's own skin material, melting
and boiling both 60001. This was found the hard way in an earlier session: a
test glob built on a donor melting at 9896 and boiling at 10180 was liquid at
fort room temperature of 10040 and vanished the moment the game unpaused. Skin
globs are permanently solid, which by O3 is why they follow the pointer and
always will.

**O8. What the slot holds on the frame a liquid item FIRST DRAWS is what that
item wears for the rest of the session.** This is O4 stated as an operational
rule, and it is the fact the whole gate exists to serve. Proven by an A/B in
one log file, same save, same code, different answer:

```
[05:01:40] First write put 42249 = VANILLA on dwarfmode/Default
[05:01:40] f1       VANILLA | dwarfmode/Default
...
f178   HIDE -> VANILLA
f179   VANILLA | Stocks type=69 n=7      drinks list first exists, VANILLA
                                          standing. Ale liquid all session.
```

```
[05:06:15] First write put 111434 = HIDE on dwarfmode/Default
[05:06:15] f6256    HIDE    | dwarfmode/Default
...
f6401  HIDE    | Stocks type=69 n=7      drinks list first exists, HIDE
                                          standing. Ale hide all session.
f6401  HIDE -> VANILLA                    correction, same frame, too late
```

**O9. Re-exposure after resolution does nothing.** In the cold launch run
above, the drinks list was later displayed again at `f3618` with `n=7` and the
slot standing at HIDE, and the ale stayed liquid. It had already resolved at
`f179`. A session therefore has exactly one chance to get each liquid item
right, at its first draw, and no chance to fix it afterwards.

**O13. The water that took the hide began as a glob of ICE.** Recorded because
it sat as an unexplained contradiction of O4 for several sessions:

```
10:22:21  SLOT  42249 -> 68813
10:25:56  FIRST LIQUID_MISC WATER  slot held 68813
10:26:33  MARK  water displays HIDES 0:3
```

Ice is water's solid state, so while it was ice the item was a solid glob
reading the pointer live every frame per O3, exactly like our skins. It
resolved when it melted, against whatever the slot held at that moment. O4 was
never contradicted, only misread as "first draw of the item" rather than "entry
into the liquid state". The container it sat in was incidental.

Source: first hand account of the test item's history. Not independently
re-measured.

**O14. Loose liquid on the map is not an item and has no sprite.** It spills
and behaves like a powder spatter. The only thing that can show a liquid sprite
on a map tile is a SOLID wearing one, and solids read the pointer live, so a
map draw has nothing to resolve. This is why the map guard was removable; see
6a.

Source: player observation across normal play, not an instrumented run.

**O15. Our currency is structurally safe, not luckily safe.** O7 pins melting
and boiling at 60001, so a skin glob can never enter its liquid state, can
never reach a resolution point, and follows the pointer for the whole session
regardless of what the gate does. Everything the gate protects is somebody
else's material.

**O10. `stocks.current_type` is a `df.item_type`, and category crossings are
direct.** `DRINK = 69`, `LIQUID_MISC = 73`, `GLOB = 75`. At one frame sampling
no neutral state was ever observed between two categories: the trace goes
`type=39` straight to `type=75` straight to `type=69`. There is no safe
intermediate frame to lean on.

**O11. `dfhack.gui.getCurFocus` reports the TOPMOST viewscreen only.**
`Lua_API.txt:1101` defines it as `getFocusStrings(getCurViewscreen())`. A
DFHack screen is a viewscreen pushed on top of the DF screen and it renders
that screen beneath itself every frame, so with a DFHack screen open the focus
read names the DFHack screen and says nothing about the DF screen that is
still drawing. **Read `dfhack.gui.getDFViewscreen(true)` instead**, which
returns the topmost viewscreen not owned by DFHack.

**O12. DFHack keeps the Lua environment across a main menu reload and does not
re-execute an unchanged file body.** Any file local holding per-world state
therefore survives into the next world. See section 6a; this has now caused
two separate multi-day bugs in this one file.

### The asymmetry, which is the whole design principle

By O3 a solid reads the slot live, so a wrong value costs one frame of wrong
art and then corrects itself. By O4 and O8 a liquid reads it once, so a wrong
value at the wrong moment is permanent for the session.

**Being late on a solid is a flicker. Being late on a liquid is a bug that
survives until you quit DF.** Every branch in the gate resolves toward vanilla
when it is unsure, and the glob category is the only place the gate is allowed
to be optimistic, because globs are the only thing on the pointer that can
recover.

---

## 5. Where the latch is not

Five exhaustive negatives. None of these need repeating.

| Candidate | Result |
|---|---|
| `gps.texture_indices1..11` | 52390 slots snapshotted across a first draw of water. Nothing moved. |
| `df.global.texture` | Holds only `page`, `palette`, `layer_set_template`. No side table. |
| the material struct | `wood_texpos`, `boulder_texpos1/2`, `rough_texpos1/2`, `bar_texpos`, `cheese_texpos1/2`, `texflag`: all zero before and after a first draw. No liquid or glob field exists. |
| the item struct | Two depth 100 path maps of the same water item across one look differ only in `flags.weight_computed` and `weight`. Lazy weight, not art. |
| `view_sheets` | Only texpos field is `vermin_portrait_texpos`, sitting at zero. The sheet stores which item to draw, not the result. |

The resolved value lives in the renderer's own memory and is not exposed as a
DF structure. **It cannot be read and it cannot be written.** Only the value it
reads at resolution time can be controlled, which is what the gate does.

A consequence worth stating plainly so nobody goes looking again: **no amount
of logging can print what texpos an item actually drew with.** Everything that
decides it can be printed, and section 8 is about printing all of it. The
result itself is only ever observable on screen.

---

## 6. The gate

`making-fuel-hide-sprite.lua`.

The slot does not have to stand at the hide. It has to be **vanilla in any
frame where a liquid could resolve** and the hide everywhere else. Skins on the
map, in stockpiles, in workshop lists and in the stocks glob list all draw
live off whatever is standing at that moment.

### Cadence

| Loop | Period | Job |
|---|---|---|
| `frame_tick` | 1 frame | Category tripwire, then the state trace. |
| `apply` | 2 frames (`POLL_FRAMES`) | Read the slot, compute the verdict, write on a difference. |

The tripwire runs at one frame because the event it guards, a stocks category
crossing, builds and draws the new list on the frame it happens, and a two
frame poll cannot answer in time. The trace runs on the same tick because it is
free once the tick exists.

`apply` stays at two frames. Dropping `POLL_FRAMES` to 1 halves the gate's
latency everywhere at the cost of doubling how often the whole gate runs, and
the whole gate includes a stocks list walk. It is a one line knob if a
flicker ever justifies it.

### Resolution

`want_target(src, dst)` returns the vanilla texpos or the hide texpos:

1. **Focus whitelist.** Every string from
   `dfhack.gui.getFocusStrings(dfhack.gui.getDFViewscreen(true))` must match a
   safe prefix. Anything unrecognised yields vanilla. Per O11, this must not
   be `getCurFocus`.
2. **Per entry test.** An entry may carry a predicate for screens that can
   sometimes draw a liquid. The test returns true when vanilla is required.
3. **Sheet contents.** For view sheets, the item, its contained items one
   level down, the building's `contained_items`, and the unit's `inventory`
   are all checked for a liquid class item that is not ours.

Every unreadable case returns vanilla.

### The whitelist as it stands

| Prefix | Test | Why |
|---|---|---|
| `dwarfmode/Default` | gated on `MAP_GUARD`, currently off | The plain map. See 6a: the guard is switched off and the map is unconditionally safe. |
| `dwarfmode/ViewSheets` | none here | Falls through to the contents test in `want_target`. |
| `dwarfmode/Stockpile` | none | The stockpile config screen, all three variants. It lists material names, not item sprites, and the only thing drawing items while it is up is the map behind it. Without this entry the gate fell to vanilla and every skin in view washed to liquid art for as long as the menu was open. |
| `dwarfmode/Stocks` | `stocks_needs_vanilla` | Safe only on the glob category, see 6b. |

There is deliberately **no `dfhack/` entry**. Per O11 a DFHack screen is not a
screen in its own right for this purpose; it is a pane over a DF screen that
keeps drawing underneath. Reading the DF viewscreen makes a DFHack screen
inherit the verdict of whatever it covers, which is correct by construction and
needs no entry.

### 6a. The map guard and the per-world state rule

**The guard is off.** `MAP_GUARD` is false, so the plain map is unconditionally
safe and the slot stands at HIDE from the first write of a load. Run with it
off and no wrong resolution has been observed.

O14 is why: loose liquid on the map is not an item and has no sprite, so a map
draw has nothing to resolve. The guard was protecting against a case that does
not occur, and it cost a visible wrong sprite on every load until the player
opened a menu.

What the guard did, kept because `MAP_GUARD = true` restores it in one line.
The gate is reactive; it reads the focus and corrects the slot after the fact.
That is fine for every transition except the first of a load, where the slot
would otherwise be written to HIDE on the map before the player has done
anything. `_G.making_fuel_hide_sprite_seen` withheld the map until the player
had been on some screen the gate had already evaluated.

**It lives in `_G` and `start()` clears it, and both of those are load
bearing.** As a file local it survived a world unload and killed the guard on
every main menu reload, because of O12: the environment persists and an
unchanged body is not re-executed, so the flag stayed true from the previous
world. The new world came up with the map already treated as safe, the first
write of the load landed on HIDE, and the first liquid drawn anywhere latched.

The frame counter in the trace is what proved it. A cold launch logs the first
write at `f1` and puts VANILLA. A reload in the same process logs it at `f6256`
and puts HIDE. Same save, same code, same screen, opposite answer, and the only
difference is whether DF was restarted.

**This is the second time O12 has caused a multi-day bug in this file.** The
first was `running`, a file local that reset on body re-execution while the
state global beside it did not, so `start()` proceeded against a dead world's
slot record. The rule that follows:

> Any state in this file that is scoped to one world load belongs in `_G` and
> must be explicitly reset in `start()`. A file local is scoped to the body
> execution, and body executions and world loads are unrelated events.

### 6b. Stocks, and why only the glob category

Stocks was taken off the whitelist entirely at one point, which killed the
latch and cost skins their sprite on the one stocks list that shows them. It is
back, narrowly.

`stocks_needs_vanilla` returns false, meaning the hide is permitted, only when
`current_type` is `df.item_type.GLOB` and that list holds nothing liquid. Every
other category, an unreadable read, and the category list itself answer
vanilla.

The broad version, a predicate that scanned the category for liquids and
allowed the hide when it found none, was correct and could still never work.
The gate is reactive and O10 says crossings are direct, so the drinks list is
built and drawn on the frame the player crosses into it, before any poll has
run. The trace caught it exactly:

```
f6401  HIDE | Stocks type=69 n=7      list exists, HIDE standing
f6401  HIDE -> VANILLA                correction, same frame, too late
```

and in a cold launch the same two events landed the other way round, which is
why the ale changed answer between runs that were otherwise identical.

The glob category is safe where a liquid category is not, purely because of the
asymmetry in section 4: a skin drawn wrong for a frame corrects itself.

### 6c. The category tripwire

`category_tripwire` runs on the one frame tick, detects any change in
`stocks.current_type`, and immediately writes the gate's verdict rather than
waiting for `apply` to come round.

It is load bearing, not diagnostic, and runs even with the trace switched off.

It originally wrote a blanket vanilla, which was safe and slow: entering the
glob category cost a drop to vanilla plus up to two more frames before the hide
went back, and that gap was visible. It now writes `want_target`'s answer,
which is the same safety with none of the churn, because the gate's answer for
any category other than the glob list is vanilla anyway.

It logs only when it had to drop off a standing HIDE. That is the near miss
worth seeing every time; a raise to hide is cosmetic and the trace records it
anyway.

### What the gate costs

Skins draw as liquid art on any unrecognised screen, on every stocks category
except the glob list, and on the map until the player has opened something
after a load. That is the whole price, it is cosmetic, and each screen can be
given its own predicate later by the same shape.

---

## 7. Failure history

Recorded so none of it gets tried again. Roughly chronological.

- **"Any sheet open yields vanilla."** Wrong. `view_sheets.open` is true for
  unit and building sheets too, and a workshop's Items list is a building sheet
  whose `active_id` is a building id. Feeding that to `df.item.find` misses or
  lands on an unrelated item, and the gate sat on vanilla for the whole time a
  skin was being inspected in the butcher's.
- **"Only ITEM sheets yield vanilla."** Also wrong. A workshop's Items list
  draws contained liquids, so water latched to the hide there before the barrel
  was ever opened.
- **The `find_holder(dst)` fallback in `apply()`.** Removed twice. It searched
  for the target value, which always exists because the HIDES page registers
  its own cells in `texture_indices8`. It silently adopted a page registration
  slot as the redirect and `stop()` then wrote the ITEM_LIQUID texpos into it,
  corrupting the page's own registration for the session. `apply()` now only
  ever claims a slot that held the vanilla value.
- **A startup delay (`FIRST_TICKS`), in ticks and then in frames.** Timing is
  not the variable. Tried at 100 and 6000 ticks and at 1 frame; none of them
  moved the result, and reverting between them moved it in neither direction.
  The unit argument consumed a whole session and established nothing.
- **Blanket `dfhack/` in the whitelist.** Justified by a false claim about
  `getCurFocus` that was written into this document and then reasoned from for
  two sessions. Per O11 the gate was seeing `dfhack/lua/launcher` and answering
  HIDE while a liquid list drew underneath. Removed; the fix is to read the DF
  viewscreen, not to add an entry.
- **`stocks_shows_liquid` testing only the outer item.** It used
  `is_liquid_item` where the sheet path had always used `holds_liquid`. A
  barrel of ale is neither `LIQUID_MISC` nor `DRINK`, so every row answered
  false while the screen drew the contents. The trace caught the slot at HIDE
  for 97 straight frames on `dwarfmode/Stocks` because of it.
- **`stocks_shows_liquid` answering safe on an empty list.** Stocks is open for
  at least one frame before it has built `current_type_i_list`, so an empty
  read means not built yet, not no liquids here.
- **`seen_a_screen` as a file local.** The reload versus cold launch split.
  See 6a, and see O12 for the general form.
- **A predicate that permits the hide on any liquid free stocks category.**
  Cannot work at any poll rate. See 6b.

### Two process failures worth the same treatment

- **Theorising against a first hand result.** This document's own failure
  history said timing was not the variable. It was argued with, reverted to,
  and argued with again across two sessions, costing reload cycles and getting
  nowhere. The record was right the first time.
- **Stating an inference as a measurement.** "Your pairs are not applied" was
  asserted twice from a single log line, with no access to the file in
  question. It was wrong, and it cost trust and two exchanges. If the artefact
  in hand cannot settle a question, say which artefact would.

---

## 8. Instrumentation

The single largest cause of the time this took was that **the production
watcher logged decisions and not state, and the only instrument that logged
state had to be armed separately and dumped separately.** A session log could
truthfully show the first write landing at VANILLA and contain no record at all
of the slot standing at HIDE six minutes later with a barrel on screen.

What exists now, all of it in the watcher, all of it into the session log, on
by default:

| Line | When | Answers |
|---|---|---|
| `claimed (vanilla N, hide M). First write put X = ... on FOCUS` | Once per load | Which value the load started at, and on what screen. This one line separates a cold launch from a reload. |
| `fN  VANILLA -> HIDE on FOCUS  stocks type=T` | Every slot transition | When a HIDE window opens and closes, and what permitted it. |
| `fN  STATE \| FOCUS \| stocks type=T n=L \| sheet ...` | Every frame the state changes | The whole decision surface, ordered. Prints nothing while nothing changes. |
| `fN  stocks category -> T with HIDE standing; forced VANILLA` | Tripwire near miss | A crossing that would have exposed a liquid list to the hide. |
| `making-fuel-hide-sprite gate` | On demand | Both focus stacks, the sheet, the full stocks list with per row liquid verdicts, the gate's verdict, and what the slot actually holds. |

`making-fuel-hide-sprite trace off` if the volume ever gets in the way.

The frame number is the watcher's own counter, incremented on the one frame
tick. `world.frame_counter` is game time and does not advance while paused, and
sheets get opened while paused, which is precisely when this has to work. The
counter is also what distinguishes a cold launch from a reload at a glance:
`f1` versus `f6256`.

**The design rule this produced:** wall clock timestamps cannot answer an
ordering question. One second is sixty frames and the resolution happens in one
of them. Anything that logs a sprite event logs a frame number.

---

## 9. Unexplained

Recorded because it is real and nobody has accounted for it.

Every page in `df.global.texture.page` carries **two** texpos arrays, `texpos`
and its greyscale twin `texpos_gs`. All 566 pages have both. For
`ITEM_NATURE:0:1` these are 42249 and 42265 in one session.

The greyscale value has **zero holders anywhere in `gps`**. Since the
redirected art demonstrably tints from the material, and tinting is what a
greyscale sheet is for, something reads those values, but not through any slot
we have found.

Separately: glob sprites do not tint from `state_color`. Confirmed by a live
paint test. Colour was not pursued past that point.

---

## 10. Open and untested

- **Trade screen, work order material pickers, minecart contents.** All fall to
  vanilla by default. Untested.
- **A solid that melts while on screen.** O13 and O14 together say the only way
  to resolve a liquid wrongly is for a solid wearing the shared sprite to enter
  its liquid state while the slot stands at HIDE. Ice is the known case. Which
  other materials can do this in a normal fort has not been enumerated, and by
  O15 none of them are ours.
- **The magnifying glass.** Unknown whether liquids or globs get one at all.
- **Resolution key.** Whether it is keyed on material alone or on material plus
  item class. O9 says re-exposure does nothing, but nothing has distinguished
  "this item resolved" from "this material resolved".
- **Plant globs.** Paste and pressed cake off a screw press should be on the
  pointer by O1. No fort tested has had any. Run `census` on one that does.

---

## 11. Generalizing this

The technique is not specific to hides or to globs. The general recipe:

1. Find the vanilla cell that the target item class falls through to, in the
   graphics raws. It is a `TILE_GRAPHICS` token.
2. Resolve that cell to a live texpos from `df.global.texture.page`.
3. Search `gps.texture_indices1..11` for the slot holding it. Collect **all**
   holders, not the first.
4. Determine who else is on that slot, which is every material with no art of
   its own in every item class that falls through to the same tile.
5. If nothing else of consequence shares it, write it and stop. If something
   does, gate it as in section 6.

The axis is **materials without art of their own**, not item classes. Who
shares a slot is answered by asking which materials are art-less in every class
that falls through to that tile, which is what `census` does.

### Decide these before writing any gate

- **Is the target material solid at fort temperature?** Check the heat block
  first, always. By O3 and O7 a solid follows the pointer everywhere and needs
  no gate for itself. A material that can reach its liquid state escapes the
  pointer permanently the moment it does, and per O7 it may simply cease to
  exist.
- **Is anything on the shared slot a liquid?** If yes, the asymmetry in
  section 4 applies and the gate must resolve toward vanilla in every
  ambiguous case. If everything on the slot is solid, no gate is needed at
  all: everything reads live and nothing can be permanently wrong.
- **Is the shared set small and enumerable?** `ITEM_POWDER` is declared
  separately at `ITEM_CONSTRUCTION:2:3` and has its own slot, so powders are a
  different and probably smaller neighbourhood than liquids. Untested.

### Rules carried out of this one

1. **A reactive gate cannot win the frame it is reacting to.** Any screen or
   list that builds and draws on the frame it is entered is unreachable by
   polling. Either the thing being protected can recover, or that screen gets
   an unconditional vanilla.
2. **Per-world state goes in `_G` and is reset in `start()`.** O12. Body
   executions and world loads are unrelated events.
3. **Read `getDFViewscreen`, never `getCurFocus`.** O11.
4. **Log state, not just decisions, with frame numbers, in the production
   watcher.** Section 8. An instrument that has to be armed will not be armed
   when the bug happens.
5. **Measure before naming a mechanism.** Every mechanism named ahead of a
   measurement in this project has been wrong.

---

## 12. Tools

| File | Purpose |
|---|---|
| `making-fuel-hide-sprite.lua` | The production watcher, the gate, the tripwire, the frame trace, and `gate` diagnostics. |
| `refinish-sprite-recorder.lua` | Background flight recorder. Largely superseded by the in-watcher trace, which does not have to be armed. Its first sight ledger came back empty on every dump and was never fixed. |
| `refinish-sprite-probe.lua` | Lists every gps slot holding the vanilla or any target texpos, and writes chosen cells into individual slots so they can be told apart by eye. |
| `refinish-path.lua` | Depth bounded path map of any df object. The workhorse for every structural question here. Writes to a fixed filename, so rename between runs. |
| `refinish-latch-probe.lua` | Differential snapshot of item, container and material across a draw. Produced the negatives in section 5. |
| `refinish-needle-probe.lua` | Value search across an object tree with a flushed crash breadcrumb. Largely superseded by `refinish-path` plus grep. |
| `refinish-draw-probe.lua` | Spawns persistent loose items of any material in any of glob, liquid or powder, with an optional temperature pin so an item can be born in a chosen state. `census` lists every glob material in the fort with a verdict on whether it is on the pointer. Test procedures are in its header. |

---

## 13. A warning about blind tree walks

An early version of `refinish-needle-probe` walked
`df.global.game.main_interface` at depth 12 and took DF down. A blind walk
dereferences whatever the tree hands it, and a bad pointer inside the C++ layer
is not catchable by `pcall`: the process dies and nothing is learned.

If a walk is unavoidable, write the path to a file and flush it **before**
touching the object, so a crash names its own cause. Prefer `refinish-path` on
a narrow root.
