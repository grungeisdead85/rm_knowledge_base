# Measured costs and what cut them

Costs come from RM's section probe unless a row says otherwise: per call, and per second of wall clock. A per second figure moves with the game's speed, so runs are compared per call (methods/verification.md). Each fix's full measurement sits in the code note named in capitals, beside the code it governs.

| What | Before | After | How |
|---|---|---|---|
| Ledger read at load (8,956 materials) | about 60 s (hung region2) | 29 ms | plain lines through the string site data calls instead of double-encoded JSON (rm/save-system.md) |
| Ledger rewrite at each options screen opening (region4) | a full write every time: 594 ms, 7.2 MB (measured 2026-09-30) | kept in 31 to 47 ms when nothing has moved (five openings and a save & continue's snapshot, measured 2026-09-30) | exact layout comparison, `if_changed` |
| Ledger check at each options screen opening (region4) | 31 to 62 ms, every id read (2026-10-02) | 0 ms in its own log line (2026-10-02) | the arrays' sizes read first (THE ARRAYS' SIZES, ASKED FIRST; rm/save-system.md) |
| Back-out of save & quit (region4) | 2 s unload + 12 s reload | nothing | no early unload |
| Grind watcher per call (all metals on, 81 bases) | 2.46 ms | 0.04 ms | base selection read as raw text and rebuilt only when the text changes; ghost reaction slots remembered and verified on use |
| Making Fuel menu shaper at the forge (100,138 reactions) | 54.8 ms per call, 85% of CPU | 0.14 ms per frame (mock, 20,000 buttons) | stamp the list (length, first button, folder token) and cache the verdict until the list is rebuilt |
| Branch spawner fall vector per tree | 3.2 to 3.3 s as branches piled up | 0.9 ms (mock, 2,540 items) | walk each map block once instead of once per tile of the 25x25 search |

## The 2026-09-30 to 2026-10-01 pass in region4 (the big fort)

- **Status:** measured. Section probe runs in region4 on 2026-09-30 and 2026-10-01. Before figures come from each code note; after figures come from the 2026-10-01 runs of 818 s and 443.7 s, unless a row says otherwise.
- region4 is the stress case:
  - 82 active mods;
  - about 24,000 items in play;
  - 4,885 twin items at load (the window census);
  - a backlog of 1,500 to 2,000 twins in workshops, with DF's hauling queue full.

### The ghost engine (refinish-reaction-adaptive.lua and its vessels file)

| What | Before | After | How (code note) |
|---|---|---|---|
| Vessel plan and product writes | 1.24 ms a call, 29.3 ms/sec; count_free_vessels 6.07 ms a call of it (2026-09-30, 606 s) | 56 µs a call (443.7 s) | liquid container capacity read once per tool subtype, no closure per tool (THE POOL TEST, ONE TOOL, SHARED BY BOTH WALKS), and the two rows below |
| Pool minimum walk | 2.10 ms, on 1,336 of 4,726 polls, 5.2 ms/sec (2026-09-30, 539 s) | held 10 polls | the estimate only sizes how many extra containers a collecting job asks for (HELD FOR POOL_HOLD_POLLS) |
| Pool walk over every tool | 8.1 ms a walk, 3.35 ms/sec, rising with the twin count over three runs: 2.1, 5.5, 8.1 ms (2026-10-01, 700 s; gravel and kindling are tools) | 0.67 to 0.79 ms a call; the backstop walk 8.5 to 8.8 ms, 15 to 27 times a run | a list of the liquid containers, tested fresh on each use, the walk kept as a backstop (THE KNOWN CONTAINERS) |
| Valuing the held items | 91 µs a call, 4.71 ms/sec (2026-10-01, 612 s) | 2 µs a call on unchanged items (443.7 s) | kept per job beside the identity of what it priced (THE HELD ITEMS, PRICED ONCE) |
| Rebuilding what the last poll built | handle_ghosted about 210 µs a job a poll: stack rule 41, identity tables 24, descriptions most of 21 (2026-10-01, 437 s) | about 160 µs a job a poll: stack rule 20, identity 4, snapshot 13, untouched test 11 (443.7 s) | THE SAME ITEMS AS THE LAST POLL, ONE IDENTITY A POLL, A DIMENSION, READ WITHOUT A THROW (making-fuel/fuel.md) |
| Whole engine | 17.3 ms/sec before the valuation memo, 12.2 after it (session report, 2026-10-01); 1.40 ms a poll, 12.20 ms/sec at 8.71 polls a second (818 s) | 1.18 ms a poll, 11.28 ms/sec at 9.59 polls a second (443.7 s) | the rows above |

- **Corrected in place:** the same-items batch was estimated to take about a third off the engine (2026-10-01). It took nothing: 12.2 ms/sec before and after (818 s).
  - Its identity was built twice a poll and read each item's `dimension` under pcall, which raises on most item classes (dfhack/scripts.md).
  - As a result, `yield: held items, priced before` went from 10 µs to 20 to 30.
  - Built once and read without a throw, the batch came to 1.18 ms a poll (443.7 s).

### Fuel access (making-fuel-access.lua)

| What | Before | After | How (code note) |
|---|---|---|---|
| Honest menu scan | 2.71 ms/sec, a walk of IN_PLAY (24,000 items) every 200 polls and at every change of building in view (2026-09-30, 267 s) | 0.007 ms a call, 0.12 to 0.14 ms/sec; one walk (23 ms) in 818 s | the fuel a walk found is tested first (THE FUEL LAST FOUND, TESTED FIRST; making-fuel/fuel.md) |
| widen_job | 16,135 of 29,043 calls ended at one line, 54 µs each, 97% of its cost (2026-10-01, 187 s); 5.0 ms/sec (session report) | 0.21 ms/sec | a slot already reclassed is decided for the session (SHAPED BEFORE, DECIDED NOW) |
| Whole poll | 8.4 ms/sec (session report, 2026-10-01) | 0.25 ms a call, 4.5 to 4.8 ms/sec | the rows above |

### Build menu icons (refinish-menu-icons.lua)

| What | Before | After | How (code note) |
|---|---|---|---|
| Pages check with the menu closed | 19,733 runs in mode NONE, 2.60 ms/sec plus 1.02 for the targets, never a change (2026-09-30, 267 s) | runs only in the build menu's modes, about 0.01 ms/sec each (818 s) | ONLY WHILE THE BUILD MENU CAN SHOW |

### The stockpile window service (refinish-stockpile-windows.lua)

The design behind each row, and what each shortcut can miss, is in rm/stockpile-windows.md.

| What | Before | After | How (code note) |
|---|---|---|---|
| The open window's recount | 41.2 ms a call, 92 at worst, 15.2 ms/sec, nine tenths of the service (2026-10-01, 486 s, 548 twin items among tens of thousands of bars) | reads the known twins | THE KNOWN TWINS |
| A workshop's contents read per item | 63.9 ms a count, 110 at worst, with 690 to 732 twins in workshops; 41 ms with 106 (2026-10-01, 189 s) | one read per building per count | ONE READ OF A BUILDING'S CONTENTS PER COUNT |
| Pile bounds and bin room | 4.5 ms of a 14.4 ms count (2026-10-01, 267 s); 7.6 ms with 19 twins on piles (365 s) | 1.9 ms a count | A PILE'S BOUNDS, READ ONCE PER LIST; THE ROOM, SUMMED ONLY FOR PILES ASKED ABOUT |
| Item flags read one by one | 25.8 ms a count, about 4 µs an item (2026-10-01, 365 s, 4,285 twins) | one read | ITEM FLAGS AS ONE NUMBER |
| Unit and container reads | 24.8 ms a count, 10.8 ms/sec, 3,206 of 3,773 twins in containers (2026-10-01, 367 s) | stop at the holder when only loose matters | LOOSE ONLY |
| Stored twins read every recount | 147 recounts at 23.6 ms, 45 at worst, 7.94 ms/sec (2026-10-01, 437 s) | 16.9 ms a call (818 s) | A STORED TWIN, LEFT STORED |
| Twins in workshops read every recount | 16.9 ms a call; 15.3 at the same point of the run (818 s) | 11.4 ms a call (443.7 s) | A TWIN IN A WORKSHOP, STILL THERE |
| Lending the flags at an opening | 35 ms for 2,099 flags over 459 twins | 22 to 23 ms | NO CLOSURE PER FLAG |
| Timers and the coal check at an opening | 24 ms and 34 ms, walks of every claimed item | 17 to 18 ms and 21 ms | THE KNOWN TWINS, WHEN THE LIST IS GOOD |
| The scan that opens a window | 105 ms with 559 loose, every loose twin's description read | 104 to 114 ms with 1,527 loose | THE CENSUS ASKS ONLY FOR PLACES |
| Whole service, window open | 16.9 ms/sec (2026-10-01, from the 15.2 ms/sec recount at nine tenths) | 2.23 ms a call, 7.77 ms/sec (818 s); 1.76 ms a call, 6.76 ms/sec (443.7 s) | the rows above |

- **Corrected in place:** the stored-twin skip was estimated to bring the recount to a few ms (2026-10-01). It came to 16.9 ms. The estimate rested on a mock with 60 twins in workshops; the fort's census had 1,509 there, all loose and all read (methods/verification.md).

### RM's script check (refinish_steel.lua)

| What | Before | After | How (code note) |
|---|---|---|---|
| Checking RM's files every 5 s | 12 lookups by name, 86 ms a run, 110 at worst, plus 49 ms refreshing the kept copies: about 15 ms/sec; 180 ms at a save request (2026-10-01, 115 s, 24 script folders) | 0.6 ms a call, 0.12 to 0.13 ms/sec; about 1 ms at a save request (session report) | each file found once, then its known path asked with one mtime call (KNOWN PATHS, CHECKED WITHOUT A SEARCH; dfhack/scripts.md) |

## The 2026-10-02 runtime pass in region4

- **Status:** measured. DFHack's own timers (`print_timers`, sessions of three to six minutes) and RM's section probe, 2026-10-02. DFHack's timers count unpaused time only (dfhack/scripts.md).

| What | Before | After | How (code note) |
|---|---|---|---|
| Coal watcher | 2,159 ms a session, the costliest named Lua timer | 186 to 359 ms a session | new items read off the end of `items.all`; a waiting list for bars left alone; the BAR backstop sliced, 2,000 bars a poll; one opening sweep a session (making-fuel-coal-watcher.lua) |
| Tinder watcher | 1,840 ms a session | 137 to 282 ms a session | the same three parts, 1,000 tools a sweep |
| Binder watcher, a maker job each poll | 0.82 ms a call, 7.86 ms/sec | 0.013 to 0.023 ms a call | `item_next_id` marks where a job's output starts (making-fuel/fuel.md) |
| Tool tint's walk of every tool | 13.3 ms a walk, 30 at worst, 33 walks in 342 s | backstop slices of 0.51 to 0.73 ms, 2 to 5 at worst; a whole walk only at a load and on DF's signal (one in a session, 17 ms) | THE NEW TOOLS; THE BACKSTOP, A SLICE A POLL; A COLOUR THAT LEFT PLAY |
| Window service's full walk | 46 to 48 ms, 56 at worst, every 4,000 frames | slices of 3.05 to 3.38 ms, 7 to 8 at worst | the renewal pass (rm/stockpile-windows.md) |
| Save hook monitor | about 2.0 ms/sec | about 1.7 ms/sec | the focus asked only while `options.open` is set (rm/save-system.md) |
| Opening the options screen | 273 to 279 ms a call, 386 at worst | 4.0 ms, 7 at worst | the tool record kept in memory; the ledger's sizes read first; the two scripts kept once a data cycle (rm/save-system.md) |
| The HUD's Status values | computed at every render of the list | once a second (mock, 61 frames: site data reads 183 to 6, version calls 122 to 4) | each value cached for the second (refinish-panel-status.lua); the HUD's drawing itself did not move |
| Lua timer time no loop was named for | 75% | 11 to 14% | every RM loop reports itself (dfhack/scripts.md) |

- **What spreading costs:** the window service's backstop came to about 1.4 ms/sec in slices against about 1.1 for the full walk it replaced. The tool tint's average per frame did not move (0.082 against 0.083 ms): both passes did the same work, without the stall.

## The 2026-10-01 to 2026-10-02 load pass in region4

- **Status:** measured (the load clock, refinish-startup.lua, region4, every base metal on: 61,392 materials, 99,574 reactions, 9,849 restored items)
- **The whole load:** 15.3 s, then 10.34, 7.87, 5.18 and 4.68 s, as the batches landed.

| What | Before | After | How (code note) |
|---|---|---|---|
| Script lookups by name | 221 in a load, 1,428 ms, 6.5 ms each | each script found once a run | ONE LOOKUP PER SCRIPT A RUN (refinish-module-engine.lua); a run-scoped require (refinish-startup.lua) |
| Material injection | 2.30 s (its loop 1,781 ms) | 0.98 s (628) | each struct read once into a local, about half the crossings; only the writes that change something, read once per base metal (refinish-index.lua) |
| Reaction injection | 2.49 s (loop and sort 2,281 ms) | 1.45 s | sorted without a Lua comparator, grouped by category (SORTED WITHOUT A LUA COMPARATOR); writes of values the template already holds skipped (refinish-index-reaction.lua) |
| Entity injection | 0.74 s | 0.29 s | a civilization raw marked done compared as an object, since DFHack makes a new userdata on every read, so the old key never matched; positions handed over from the reaction stage |
| Module permission evaluation | 379 ms | 33 ms | the civilizations listed once, before the loop over reactions |
| The ledger on an unchanged load | about 1.3 s, a remap and a write | 172 to 328 ms, a check | the fingerprint: an MD5 of the records, made in one walk; no write when it matches (rm/save-system.md) |

## A per poll cost drifts upward through a session

- **Status:** measured (2026-10-01, 818 s run, its five reports differenced)
- The engine's whole poll ran 1.25 ms over the first 169 s, then 1.35, 1.43, 1.58 and 1.37 ms in the intervals after.
- The vessel plan rose from 45 to 60 µs a call, and the window's known count from 12.9 to 19.4 ms as the workshop backlog grew.
- Jobs per poll held at about 5.3. The engine's growth has no known cause yet.
- A short run reads lower than a long one.

## Still to cut

As measured 2026-10-02 (region4):

- **The ghost engine, about 10 ms/sec, the largest RM loop.** Its largest part, the vessel plan and product writes, was split on 2026-10-02: a liquid stream written 45 to 68 µs, a solid stream 10 to 12, the pre-pass 12 to 15, at about 5 ghosted jobs a poll. Held: skipping a write whose inputs have not changed is possible, since each job has its own ghost, but it needs every writer of ghost products audited, for 1 to 2 ms/sec at most.
- **The window service's known count,** 9 to 11 ms a recount, 3.1 to 3.5 ms/sec: the floor for an exact count with 1,509 twins in workshops.
- **The tool tint's dressing,** about 0.06 ms a frame, 5.4 to 6.4 ms/sec: every frame by design, so DF's own art never shows for more than one frame.
- **The HUD, while open:** the left pane 0.69 to 0.80 ms and the right 0.57 to 0.68 ms a drawn frame, drawing DF needs every frame.
- **The save hook monitor, about 1.7 ms/sec over a 329 s run** (a 52 s run since read about 0.7): the status panel's clock string formatted every frame and the walk to the options struct. Parked.
- **The window service's opening tick,** 166 to 252 ms, once at each load.
- **About ten loops of 1 to 2.6 ms/sec each:** the aggregate, the menu shaper, the window menu watch, the rot and cremate keys, the organic registrar, the coal watcher, the JIT watcher and the dispatcher's own share.
- **For scale:** DFHack's own overlays cost more than any RM loop, 7.9 to 22.4 s a session, about half of it DFHack's overlay framework.

As measured 2026-10-01 (443.7 s, region4):

- **The engine:**
  - vessel plan and product writes, 56 µs a job a poll, 2.83 ms/sec (the largest section left, and it grows through a session);
  - reap and vessel tick, 184 µs a poll, 1.76 ms/sec;
  - repair_filters, 26 µs a job a poll, 1.31 ms/sec.
- **Fuel access:** `tank_step`, 13 µs a call, 2.11 ms/sec.
- **The window service:**
  - the known count, 11.4 ms a call, 4.13 ms/sec: every loose twin is still found and read at each recount, about 5 µs a twin by inference;
  - the full walk, 49 ms at least every 4000 frames, 1.22 ms/sec (cut 2026-10-02: the renewal pass);
  - an opening's single frame of 167 to 180 ms.
- **Rare spikes:** organic stockpile registration and the branch spawner (session report, not timed since).

As listed 2026-09-30, with what has happened since:

- **Stockpile windows, 2 to 4 ms per call in a big world:** in region4 with a window open, the tick cost 2.23 ms a call and its recount alone 23.6 to 41.2 ms (2026-10-01). Cut as above.
- **Rot and cremate watchers, 22 and 11 ms per second:** not timed since; they carry no section laps.
  - Named in DFHack's timers since 2026-10-02: the rot keys 514 to 796 ms and the cremate keys 250 to 562 ms in sessions of three to six minutes. What cut them from the 2026-09-30 figures is not in these notes.
- **The tool record at each options screen opening walks every tool item (cheap at 466 tools):** not timed since.
  - Timed 2026-10-02: 273 to 279 ms an opening at 9,914 tools. Cut to 1.5 ms (rm/save-system.md).

## A data cycle's cost in region4

- **Status:** measured (2026-09-30)
- Startup pipeline about 12 s: modules 4.3, scan 0.5, materials 2.2, reactions 2.4, module permissions 0.35, entities 0.8. With every base metal on, RM held 61,392 materials and 99,578 reactions; the default went back to steel only, with the base metal selection as the control over how much is loaded.
- 2026-10-01 runs: the pipeline took 14.3 to 14.5 s (modules 6.1 to 6.3, scan 0.5, materials 2.2 to 2.3, reactions 2.5, module permissions 0.37 to 0.46, entities 0.75 to 0.82).
- 2026-10-02: a load takes 4.68 s (the load pass above).
