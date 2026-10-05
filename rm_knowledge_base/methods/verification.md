# How claims are measured and changes verified

## Measure before naming a mechanism, and make the probe read the right place

- A probe that reads the wrong folder, field or screen reports "not settled" forever. Three save probe runs read nothing because `getSavePath` pointed at the install folder (df/saves.md).
- When a probe keeps failing, find where it failed from its own lines (every read, the path it used) before changing its logic again.

## Reproduce the failure in a mock before trusting the fix

- Load the real file (or lift the real functions verbatim) into a mock world that plays the measured sequence: for saves, DF's logic first (the screen closing, a tick if nothing halts it), then DFHack's update calling the script. Count the effect that matters (ticks with RM out, unloads and reloads, stores).
- The mock must first reproduce what was seen in play: the save hook mock showed the one slipped tick and the back-out lock before showing the fix. A mock that cannot reproduce the failure proves nothing about the fix.
- Mocks of RM code walk game vectors from 0 (DFHack's ipairs) and model DFHack's behaviour from its documentation, not assumption (for example saveSiteData JSON-encoding its value).

## Survey every reader before changing what a value means

- Changing state_color from colour to pattern needed every reader and writer found first (injector, dye default, finish names, sprite art, tree dyes, tool tint). The tool tint was misjudged as a harmless grouping key and surfaced in play as a colour mismatch.

## Pairs are verified by round trip

- Every FIND is checked to occur exactly once in the file the user is actually running (the project copy may lag); the pair document is then applied to fresh copies and the result compared byte for byte with the tested build.
- The applier recognises a file heading only as `## <file>`. A heading with anything after the name matched nothing, applied nothing, and still printed success until the applier was made to fail when FIND blocks sit outside a file heading (2026-09-30).
- A deletion pair loses its FIND's trailing blank lines in a document; anchor it on the next non-blank line with a non-empty REPLACE.

## Check that moved code still reads what it should

- `luac5.3 -l -l` lists a function's upvalues and every global it reads. After moving code into a closure, confirm a local it needs is read as an upvalue, never as a global (a mistake compiles cleanly and reads nil in play).

## Give the next session something to measure

- New code logs what it decided and how long it took (the ledger's write and keep lines carry milliseconds; a fill held to one vessel names its counts), so the next log settles the question rather than a new probe.

## Time the sections before changing a loop

- **The tool:** since 2026-09-30, RM's section probe (refinish-section-probe). Code places laps between the parts of a loop through `_G.refinish_section_clock` (`sc.now()`, `sc.lap(name, t0)`); the laps cost nothing while the probe is off.
- **The report:** `report` ranks every section by its cost per second, with the calls, the ms a call and the worst call.
- **The rule:** a loop whose internal cost is unknown gets laps first, and a fix second.
- **When a fix adds a read, check which lap it lands in.** The same-items skip of 2026-10-01 added an identity build that landed inside the stack rule's lap. Its cost showed up only as a smaller saving there, not as a line of its own, and the engine's total did not move.

## A probe never throws away what it measured

- **Adopted 2026-10-01:** the section probe lost a fifteen minute window to `off` typed in place of `report`.
- **The rule:** every command that ends or clears a window reports first: off, reset, and arming again. A map unload writes the report to the log.
- **The profiler follows the same rule** (REPORT FIRST in refinish-tool-profiler.lua).

## Compare runs per call, on the same save, interval by interval

- **Per call, not per second.** A cost per second scales with the game's speed. The engine polled 8.71 times a second in one run and 9.59 in the next, so its ms/sec fell 7.5% while its cost per poll fell 16% (2026-10-01).
- **The same save makes runs comparable.** Reloading it gives the same start: the census read 4,885 twin items, 1,509 of them in workshops, at both loads on 2026-10-01.
- **Read the drift between reports.** A report's figures are averages since `on`; differencing successive reports gives each interval's own cost.
  - The engine's poll rose from 1.25 to 1.58 ms through one 818 s run.
  - The window's known count rose from 12.9 to 19.4 ms as the workshop backlog grew.
  - So a short run reads lower than a long one, and a before and an after are compared at the same point of a run.

## Build an estimate on the measured distribution

- **What went wrong, 2026-10-01:** the stored-twin skip was estimated to bring the window's recount to a few ms. The estimate came from a mock with 60 of 5,000 twins in workshops. The fort's census, already in the log, had 1,509 there, all loose and all still read. The recount came to 16.9 ms.
- **The rule:** a mock that feeds an estimate takes its proportions from the census or the log, not from a guess. An estimate is reported as one until a run confirms it.

## Old and new side by side, and DFHack's errors modelled

- **Side by side:** a change that must give the same answers is checked by lifting both versions verbatim into one mock and running them on the same states, comparing every answer.
  - The window's known count was run this way through hauls, drops, a removed workshop, binned coal and a census.
  - A known gap is reproduced on purpose, to show where the two differ and when they agree again.
- **DFHack's errors modelled:** a mock item whose metatable raises on a missing field, as DFHack does (dfhack/scripts.md), counts the throws a change removes.

## Name before you probe

- **Adopted 2026-10-02:** DFHack's own timers (`print_timers`) showed three quarters of the Lua timer time as unnamed until RM's loops reported themselves (dfhack/scripts.md). Named, they showed two loops no probe had laps in, the binder watcher and the tool tint, among RM's five costliest.
- **The rule:** a loop that runs on its own timer reports its runtime under its name, so the first look at a session's cost needs no new probe.

## An engine fact a change rests on is probed before the change

- **Example, 2026-10-02:** gating the save hook's focus check on `options.open` was safe only if `open` is set whenever the options screen is up.
  - First a probe counted, every frame, the frames the two disagreed in each direction, warning at once on the dangerous one and changing nothing.
  - Four openings, one a save & continue, 2,145 frames up: no disagreement.
  - Only then was the gate written, with a tripwire left in (df/saves.md).

## A record is compared old against new by its content

- **The tool wash, 2026-10-02:** the old full wash and the new kept record ran in one mock world, opening the options screen five times while tools were made, used up and dried. Each opening's stored record was decoded and hashed: identical at every opening, with and without a leftover record from before.
- **A difference is classified, not waved through:** after a data cycle the two differed. Both were dumped and compared item by item: 17 entries, every one for an item gone, nothing missing, no tool different (rm/save-system.md).

## A pass spread over ticks is checked for what it read

- **The check:** in the mock, each item's reads are counted per pass against the items present throughout that pass. Missed must be 0 and read twice 0 with items removed every frame; a shift too large to follow must make the pass unsure, and an unsure pass must drop nothing (dfhack/scripts.md, a walk spread across ticks).

## A mock takes its names from the code that makes them

- Seen 2026-10-04: the brick service watched for its grog reaction as REFINISH_BRICK_GROG, and its mock passed, because the mock was handed the same name. The module engine names every reaction it builds prefix, RXN_, key, so in play the reaction ran and the service never saw it. A name, code or key a mock feeds in is read from the code that produces it in play, never written from what the author expects it to be.

## When a fix is in place and the thing still does not happen, read what DF built

- Seen 2026-10-04: the mineral dye permits were confirmed in the civilisation's list by a console read, and the dyes were still in no menu (df/jobs.md). Reasoning from the reaction's fields ruled out the flags, the building, the category and the permit evaluator, and found nothing. The next step is a read of what DF itself built, here the menu's buttons (game.main_interface.building), set beside a case that works, rather than another theory.
