# Retort defect register

Every defect found in the retort chain, what proved it, and where it
stands. Status is one of:

- **PROVEN** measured in game, evidence recorded here
- **SUSPECTED** consistent with evidence, not yet measured
- **FIXED** change applied and verified in game
- **PATCH WRITTEN** change exists but is NOT verified, do not trust it

Nothing moves to FIXED without a log line or probe output proving it.

## Priority

**CHAR, ASH and RETORT are the core of the mod and come first.** They
are the foundation and nothing else matters if they are not flawless.

**Processing is a tail**: coke, dyes, glue, methanol, verdigris. Mostly
unvetted ideas, the bark dye chain being the most intricate, and some
of it may migrate to a separate mod later. If a tail is wrong we fix
it so it works, but it never outranks a core defect and it never gets
to hold up core work.

Register items are ordered by that rule, not by when they were found.

## Liquid packaging law, not negotiable

**One package size per currency, across a whole interacting chain.**

A reaction takes the FIRST item in the list that meets its
requirements, always that first item. So if it asks for 450 and the
first match holds 300, that reaction is broken for as long as the
conflict exists. Any cross pollination of incompatible package sizes
anywhere in a production stream causes the partial bug. This is why
the strict packaging structure exists.

**Never allow the partial bug.** The only viable way to move more
liquid is MORE CONTAINERS, never variable contents.

**Amended 2026-09-08, and now a live plan rather than a parked one.**
Multi-unit vessels are viable under exactly one invariant: every
reaction requires **no more than one unit of 150 dimension per
container**. Consumption stays at one unit per slot, so a reaction
needing several units hauls a unique container for each. The ruling:
that is a lesser burden than hauling fifty containers to bottle a
whale. Under that invariant a barrel is a payout-side optimisation
only and cannot cause the partial bug. See "Barrels" below.

## Design rule

**A stack burns whole.** Nobody should sit through forty runs for one
output. Consistency is the point: "whole stacks burn and I get the
right output" is one rule a player can predict, rather than several
systems to learn. Any exception has to be justified here, in writing,
against that rule.

**Extended 2026-09-08 to dimensioned feeds.** If we can burn a whole,
we burn the whole, whether the amount lives in `stack_size`,
`material_amount` or `dimension`. Nobody scoops a spoonful out of a
glob forty times.

Every Lua file delivered is now syntax checked with a real `luac5.4 -p`
pass before it goes out, rather than by reading the block structure.

---

## Audit, fourth revision of 2026-09-09

Everything after the cache validation round. The retort ran a full
hostile sequence clean, the schema was audited end to end, and four of
the entries below are my own claims withdrawn.

| item | was | now |
|---|---|---|
| tar collapse | proposed | **APPLIED.** Three organic tars are one `TAR`, 80 product mat_ids, 430 to 430 reactions |
| `RETORT_DRAIN` | named `decant held liquids`, in a category | renamed `drain retort`, category dropped, and **nothing needed changing**: every reference is to the reaction KEY |
| R25 | new | the meat overfetch. TWO writes, both the ghost's. **FIXED** |
| R26 | new | the rot key was a boulder, so it sat in the building materials list. **FIXED**, and it exposed two older bugs |
| R27 | new | `RETORT_ROT` did not exist. **ADDED** |
| R28 | new | the bank readout sized to its skeleton, not its content. **FIXED**, third scrollbar |
| R29 | new | two silent fallbacks to a WILDCARD in `build_reagent`. **FIXED** |
| `vector_id` | not expressible | **ADDED**, 136 vectors, validated offline |
| flag audit | assumed incomplete | **83 of 83 already expressible.** Nothing was missing |
| L16 to L20 | new | engine facts, including two that only a live probe could give |
| X11 to X14 | new | four more of my own calls retracted, all from the same root |
| mirror sync | 2026-09-09 | still 2026-09-09, and it lagged on every single round |

## Audit, third revision of 2026-09-09

The retort ran the full hostile sequence clean: a corpse job expanded
to five slots, a data cycle pulled mid collection, the job completing
and settling, then two drains. 457 log lines, no crash, every bank
reconciling to six decimals.

| item | was | now |
|---|---|---|
| barrel probe | **Next, item 1** | **RUN.** See L11. Barrels have no itemdef and were not adopted; the sizing answer changed the design instead |
| RETORT_DRAIN | **Next, item 3**, blocked on the ledger | **BUILT and verified**, per retort. See the drain section below |
| R18 | new | runtime cloned reactions are invisible to the adaptive engine. **FIXED** |
| R19 | new | `base_cache` holds reaction pointers across a data cycle. **FIXED** |
| R20 | new | an unreadable slot was treated as feed. **FIXED**, and it was CTD 1 |
| R21 | new | the INERT refusal re-asserted every poll. **FIXED** |
| R22 | new | an expanded job reverted onto a smaller base cannot complete. **FIXED**, and it was CTD 2 |
| R23 | new | the drain key stutters between completion and settle. **FIXED** |
| `expand_state` leak | housekeeping, open | **FIXED**, `start()` clears it at 4412 |
| ghost accumulation | "unbounded over a long fort" | **NOT UNBOUNDED.** The engine sweeps by prefix every data cycle, several times an hour |
| L7 to L13 | new | engine facts, including two that cost a crash each |
| X6, X7, X8 | new | three of my own calls retracted |
| crumb trail | live | **SILENCED**, call sites kept. It found none of the three crashes |
| mirror sync state | 2026-09-08 | replaced, 2026-09-09 |

## Audit, second revision of 2026-09-08

| item | was | now |
|---|---|---|
| R9 | OPEN, new lead | **FIXED**, `corpse_flags.unbutchered` is the discriminator |
| fire_safe gate | candidate | **DEAD**, killed by a live test |
| X4 | new | my wrong call: DF job item flags are not positive-only |
| X5 | new | my wrong call: `isTemperatureSafe` misused, verdict void |
| K3 | new | fireproof creatures burn as flesh, known and accepted |
| L5, L6 | new | `corpse_flags` vocabulary; relsize shares overlap |
| slot disagreement announcement | proposed | **SHIPPED**, correctly silent |
| standing note | scattered | **N4**, the non-discriminating test, now three times |

## Audit, first revision of 2026-09-08

| item | was | now |
|---|---|---|
| R1 | RESOLVED BY FIX 2, pending application | **FIXED**, applied and verified |
| R2 | RESOLVED BY FIX 2, pending application | **FIXED** for the seen cases, open as a class |
| R5 | RESOLVED BY FIX 2, pending application | **FIXED**, applied and verified |
| R14 | RESOLVED BY FIX 2, pending application | **FIXED**, applied and verified |
| R12 | PROVEN, blocking | **FIXED**, verified 3 of 3 settles |
| R13 | PROVEN, blocking | **FIXED**, `live_jobs` written every poll |
| R7 | PROVEN, severity raised | **FIXED**, both halves |
| R9 | SUSPECTED, spec_heat hypothesis | **hypothesis DISPROVEN**, still open, new lead |
| R15 | new | **FIXED**, vessel expansion after collection closes |
| R16 | new | **FIXED**, fat never classified as FAT |
| R17 | new | **FIXED**, a glob carries a count AND a size |
| N2 | new | AFTERMATH growth check is a false positive |
| N3 | new | mirror `preflight.py` cannot see the split reaction set |
| L1 to L4 | new | engine facts learned, recorded so they are not re-derived |
| Slot surgery | PROVEN VIABLE | **narrowed**, proven only at 1 item attached |
| Multi package payout | "still untested: the payoff" | **VERIFIED**, whale bottled in one job |
| Mirror sync state | 2026-09-07 13:23 | replaced, 2026-09-08 |

---

## Open, blocking

**Nothing.** Every blocking core defect in this register is closed and
verified in play, including the three crashes of 2026-09-09.

Still open and none of them blocking: R10 stale comments, R11 the coke
family, B1 the tar and vinegar ratio, and the four items in
"Observed 2026-09-09, not yet investigated" below.

---

## Closed core defects

### R1. settle cannot see a corpsepiece being consumed
**Status: FIXED, applied and verified**

A pile consumed whole VANISHES, and settle already detects that.
Proven in game: job 13, 14 bone buffalo stack, `the whole item is
gone`, ledger `BURNED`, every bank carried. The burn test needed no
change at all. Confirmed again 2026-09-08: `STACK: job 19 takes all 14
of #1558 in one run`.

**Was: PROVEN**

`settle` decides "did this job burn" from three questions: did the
reagent vanish, did its `stack_size` shrink, did its `dimension` drop.
A corpsepiece answers no to all three. Its count lives in
`material_amount`, and DF can even RAISE that mid job by merging loose
bones in.

Evidence: bone probe, `CHANGED #1110 mat_amount: [3]=1 -> [3]=11,
parts_present 12 -> 11`, while `stack_size` stayed 1 throughout. Every
RETORT_BONE job in three sessions logged `NOT CONSUMED`.

### R2. Free payout once a bank is primed
**Status: FIXED for every case seen, open as a class**

With the burn detected the payout is debited: job 13 logged `costing
oil_bone 1.000000` and `bank oil_bone 0.142396 carried`. The hazard
remains anywhere else settle cannot see a burn, so this closes for the
known feeds and stays open as a shape to watch for.

**Was: PROVEN**

Because of R1, a job writes a payout and then never pays for it.

Evidence: jobs 20 and 22. `bank oil_bone 0.950000 held + 0.206037 in =
1.156037`, `out ... 1 oil_bone (costing oil_bone 1.000000)`,
`MINT #1162 OIL_BONE stack=1`, then `bank oil_bone unchanged at
0.950000, nothing was consumed`. Two real jugs minted, bank never
moved.

### R3. DF mints to_container liquid products at count 0
**Status: FIXED by the null reaper, confirmed in play**

The engine behaviour is unchanged and always will be; DF still mints
the null. The reaper removes it on the next poll.

**Confirmed at scale 2026-09-08.** Job 14 in the vessel gate session
was cancelled holding 47 filters and DF minted **46 nulls**, one per
`to_container` slot, of which only 2 had jugs because only 2 slots
were ever filled. The reaper took all 46 on that poll and freed both
jugs. The failure was total and the accounting survived it intact.

**Was: PROVEN**

The ghost writes count 0 to a liquid slot, correctly, and DF creates
the item anyway at `stack_size = 0`, dimension as authored.

Evidence: mint probe, ten mints across five RETORT_BONE jobs, every
one `count=0` in the slot and `stack=0` on the item. The paired
control is decisive: job 22 held `[3] OIL_BONE count=1` and
`[4] AMMONIA count=0` in the same poll, and produced
`#1162 OIL_BONE stack=1` and `#1163 AMMONIA stack=0`.

**stack_size mirrors count exactly.** That correspondence is the only
safe discriminator between a real payout and a null, and it must never
be inverted: stamping a null to stack 1 mints fluid from nothing. That
bug has already shipped once in this file.

### R4. Nulls occupy jugs, two per job
**Status: FIXED by the null reaper, confirmed in play**

Jugs return to circulation instead of two fresh ones being pulled per
run.

**Was: PROVEN, and it had bitten in play**

A null sits in the jug, the jug is no longer empty, and the vessel
reagents require `empty: true`, so the next job pulls two more.

Evidence: jug ids across five bone jobs, strictly descending, zero
reuse: 979/978, 977/976, 975/974, 973/972, 971/970. Burning one
buffalo's 14 bone stack consumed roughly 28 jugs and the fort ran out
mid run.

### R5. Corpsepiece valuation reads body part relsize, not the count
**Status: FIXED, and the valuation was never wrong**

Crediting the whole pile was only incorrect because DF consumed one
bone from it. Consume the pile and the existing arithmetic is right as
written; no denominator was needed. Verified independently against job
13, all eight figures matching to six decimals, and additive: the
bones pay 45 percent of what the whole buffalo would, matching their
45.4 percent relsize share.

**The same fault recurred on a different item type and is now closed
there too, see R17.** The stack fraction is `min(1, q / sz)`. Any item
whose amount does not live in `stack_size` clamps that to 1 and gets
credited whole while a fraction of it burns. Corpsepieces were the
first instance, measured at 8.7x. Globs were the second, measured at
9x on a `[9]` fat stack. **If a third item type turns up whose amount
lives somewhere else again, this is the fault to look for first.**

**Was: PROVEN**

Evidence: measured 8.7x over five runs. Also inverted: one bone reads
relsize 3000 of 8972 (33.4 percent of a dwarf), the six bone item
reads 960 of 8972 (10.7 percent), so one bone prices at 3.12x six
bones.

**Basis confirmed stable.** Six consecutive consumptions on #1110:
`material_amount` fell by 1 each time, `parts_present` fell by 1 each
time, `relsize_present` fell by 400, 500, 500, 80, 80, 200. Not one
increase in any field.

**Narrower than first written.** Single unit corpsepieces are fine:
#1140, a troglodyte right foot at amount 1, went `stack_size 1 -> 0`
and was then destroyed, which settle's existing test catches. Only
MULTI unit stacks are invisible.

### R6. BOIL_PITCH and REFINE_TAR produce no pitch
**Status: FIXED by the null reaper, confirmed in play**

Root cause was R3 as suspected: the boil was being handed stack 0 null
tar, which DF's consume path will not drain. With nulls reaped the
boil is fed real tar and works. This was the complaint that opened the
session.

### R12. Cycles are lost silently, no ledger line at all
**Status: FIXED, verified in play**

The item set emptying IS DF's own cycle boundary, and the poll now
settles there instead of relying on the audit sweep firing through a
dead guard. Verified 2026-09-08, three jobs left the list and three
reached the correct verdict:

| job | verdict | banks |
|---|---|---|
| 10, whale, cancelled by hand | NOT CONSUMED | unchanged, correctly |
| 13, whale, expansion refused | BURNED | carried 35.151247 oil, 11.717082 ammonia |
| 15, aardvark | BURNED | drained the backlog to 0.713747 |

Not a statistical proof. The symptom was intermittent, and three
correct settles plus one clean repeat boundary from the previous
session is a strong signal rather than a guarantee. The thing that
would raise it further is a session of several repeat cycles back to
back.

One log line looks alarming and is not: `empty ledger set, so
untouched() can never return false and this cycle can never settle`.
It fires on a job's first sighting, before any item has attached, and
`audit_sweep` cleans those up.

**Was: PROVEN, upstream of R1 and R2**

Job 47, one repeat bone job, chewing a multi bone stack:

```
08:06:21  #1110 9->8   settled
08:06:44  #1110 8->7   NO LEDGER LINE
08:06:58  #1110 7->6   settled
08:07:12  #1110 6->5   NO LEDGER LINE
08:07:26  #1110 5->4   settled
08:07:40  #1110 4->3   settled
```

Six bones consumed, four ledger blocks. Two cycles produced no verdict
of any kind and their deposits vanished without a trace.

### R13. `live_jobs` is dead code, so the audit sweep settles live jobs
**Status: FIXED, verified in play**

`live_jobs` is cleared and refilled on every poll. This is the load
bearing half of R12: `audit_sweep` settles by comparing against
`live_jobs`, and with it empty the sweep could not tell a finished job
from a running one.

**Was: PROVEN, this is the mechanism behind R12**

```
1509:  local live_jobs = {}
2071:  if live_jobs[id] then
```

Declared, read once, never written to. Its own comment states exactly
the bug it was added to prevent: "A snapshot can only be called
cancelled if its job is NOT here."

**How it produced R12.** Between repeat cycles DF detaches every item,
so `job.items` reaches zero:

```
08:38:06  id_key "1027"   bone attached, idx=0, reagent=0
08:38:21  id_key ""       job.items EMPTY, no rows at all
08:38:22  id_key "1027"   bone back, plus jug #977 idx=1 PRESERVED
```

The poll only called `handle_ghosted` when `#job.items > 0`, so during
that empty window the snapshot went stale and `audit_sweep` settled
it, always reading NOT CONSUMED because the reagent was still present.

**The warning attached to this entry was correct and was followed.**
Populating `live_jobs` alone would have stopped the only thing then
ending a cycle. The empty item set was adopted as the real boundary in
the same change.

### R14. Free payouts at scale, measured
**Status: FIXED, applied and verified**

Closes with R2. One pile is now one job, detected, debited.

**Was: PROVEN, consequence of R1, R5 and R13 together**

One buffalo bone stack, 14 bones: six settle blocks paid `1 oil_bone`
at `costing oil_bone 1.000000`, and exactly one `carried in
BANK_OIL_BONE` line in the entire run. Six jugs of bone oil minted and
nothing ever debited.

### R15. Slots appended after collection closes are never hauled for
**Status: FIXED, verified in play**

DF closes a job's collection phase once its own reagents are all
covered. Slots appended after that point are never hauled for, and the
job then waits forever on a filter nothing will fill.

Proven by two whale corpse runs in one session that differ in exactly
one thing:

| | job 10, worked | job 14, failed |
|---|---|---|
| base filters covered at expand time | 1 of 3 | 3 of 3 |
| containers free in the fort | 94 | 52 |
| extras appended | 44 | 44 |
| extras DF actually hauled | 44 | **0** |
| outcome | `attached=47 filters=47`, BURNED | 44 filters unfilled, NOT CONSUMED |

Availability was never the difference. Timing was. `AFTERMATH` on the
failing run read `52 free, 0 forbidden, 46 holding, 2 claimed`.

**Why it needs a cancel to reproduce.** A cancelled job leaves its feed
and its jugs standing at the workshop, so the next job fills every base
filter inside a single frame and is already closed when the swap fires.
Job 13 went from zero items to all three between two consecutive
polls; there was no partial state for a faster poll to catch.

**Not a poll rate problem, measured.** Job 13 and job 15 were both
caught one second after first sighting. Job 13 held 3 of 3 items, job
15 held 1 of 3. Identical latency, different attachment order. A per
frame hook would buy nothing on this path.

**The fix is a gate, not a vacate.** `collection_open` tests whether
every base filter index has an item pointing at it, and zeroes the
expansion pile when it does not. Vacating a filter to reopen
collection is ruled out, on the grounds it would likely cancel the job
the way forbidding an item does.

**Measured by FILTER COVERAGE, not by item count.** K1 attaches spare
items to satisfied filters and DF sometimes attaches at
`job_item_idx` -1. Either inflates `#job.items` and would refuse a job
that genuinely still had a slot open.

**The deferral costs nothing.** `projected = banked + credit`, so the
bank is inside `packages_wanted`. Verified: job 13 banked 35.151247
oil and 11.717082 ammonia, and job 15, an **aardvark corpse worth
0.250000**, paid out 35 oil and 11 ammonia in one run and drained the
backlog to under a package.

### R16. Fat has never once classified as FAT
**Status: FIXED, verified in play**

`FAT_TEMPLATE` carries `SPEC_HEAT:4181`. So does `TALLOW_TEMPLATE`. So
does `MUSCLE_TEMPLATE`. Confirmed in `material_template_default.txt`
at lines 219, 1902 and 270. DF uses water's specific heat to mark
anything mostly water, and fat qualifies.

The classifier tests `sp >= 4000` at L1 and returns FLESH before ever
reaching L2, so **`BY_ID`'s `FAT`, `TALLOW` and `SOAP` rows were dead
code from the day they were written.**

Consequence, measured on water buffalo fat:

```
. water buffalo fat [9]  size=540  FLESH  d=900  [item:L1 wet tissue]  = 0.123238
  oil_tallow bank 0.000000 + 0.000000 = 0.000000
  oil_bone   bank 0.000000 + 0.277285 = 0.277285
  ammonia    bank 0.000000 + 0.092428 = 0.092428
REAPED unpaid INORGANIC:MAKING_FUEL_OIL_TALLOW #1580, jug #1468 freed
```

A reaction named "render tallow oil from fats" produced no tallow,
banked two currencies it has no slot for, and minted a null into its
own declared slot on every single run.

Fixed by testing fat before the flag rather than by loosening the 4000
threshold. 4181 is genuinely correct for fat, it is just not the whole
story about it. Only the ordering was wrong. The test reads `BY_ID`
so one place still decides what a fat is.

After:

```
. water buffalo fat [9]  size=540  FAT  d=900  [item:L1 id FAT]  = 0.591540
out  0 charcoal, 0 boulder, 1 cinder, 0 ash, 1 oil_tallow
bank oil_tallow 0.478851 carried in BANK_OIL_TALLOW@5
```

Three streams instead of five, no null, every figure reconciling.

**Checked and cleared for every other creature template.** Only SINEW
also carries 4181, and FLESH is correct for collagen, so nothing else
is being swallowed:

| template | spec heat | |
|---|---|---|
| BONE, TOOTH, SHELL, PEARL | 1000 | clears the gate |
| HORN, HOOF, LEATHER, HAIR, SCALE, CHITIN, CARTILAGE, FEATHER | 420 | clears |
| SINEW | 4181 | returns FLESH, and that is correct |

### R17. A glob carries a count AND a size
**Status: FIXED, verified in play**

Measured on water buffalo fat, job 15:

```
water buffalo fat [9]  size=540   ->  one run  ->  water buffalo fat [8]  size=480
reagent asked q150, exactly one unit went
```

540 over 9 is 60 volume a unit, and 150 removed exactly one of nine.
So on a glob `stack_size` holds **how many** and `dimension` holds
**how big each one is**. The total held is their product.

This caught out two successive attempts and both are worth recording,
because the item disproved each in turn:

1. Reading `stack_size` alone would write a stack count into a
   dimension quantity: `RETORT_GLOB` asks 150, a glob reading
   `stack_size 2` would rewrite that to 2 and collapse the demand.
2. Reading `dimension` alone gives 150, which already equals what the
   reaction asks for, so the guard writes nothing, says nothing, and
   the stack burns one unit per run. **This is what shipped first and
   it was silent**, which is why the logging rule below was added.

The guard now reads `stack_size * dimension`. Verified: `STACK: #1550
is a dimensioned feed, stack 9 at dimension 150, so 1350 unit(s) held
in total.` followed by `STACK: job 14 takes all 1350 of #1550 in one
run`, and the job reached BURNED.

**It also closed a 9x over credit**, the R5 fault on a new item type.
The stack fraction `min(1, q / sz)` was `min(1, 150/9)`, clamping to
1, so the valuation credited the entire nine unit stack while burning
one unit of it.

**LOG RULE, added because of this.** The old line only spoke when the
quantity actually moved, which is exactly why a fat reading 150
against an authored 150 was invisible. Every dimensioned item now
reports itself whether or not anything is done about it. In unexplored
territory, silence on the no-change path is how a defect hides.

### R7. RETORT_GLOB was a broken hybrid
**Status: FIXED, both halves, verified in play**

```
[0] count=1  BAR_COAL               CHARCOAL
[1] count=0  LIQUID_MISC_INORGANIC  MAKING_FUEL_OIL_TALLOW  to=vessel_1
```

Any nonzero count fails `derive_config`'s all-zero gate, so the whole
reaction sat outside the adaptive engine. Slot 1 was never written, so
it never produced a drop of tallow, and charcoal paid a flat 1 whether
the fat came off a rat or a whale. It was the only broken reaction
among the 103 adaptive retorts in that file.

Regenerated to the standard shape: `BAR_COAL`, `BOULDER` char, `BAR`
cinder, `BAR_ASH`, then the tallow slot, all at count 0. Positions
verified against `RETORT_MEAT` programmatically, since `SECONDARY_SLOT`
pins ash at position 3 and getting it wrong is silent.

Vessel count stays at one, which is correct: `FLUID_SPLIT.FAT` is
`{ OIL_TALLOW = 1 }`, one liquid, one container. Chemically fat renders
tallow and carries no nitrogen worth bottling, so no ammonia slot.

**R16 and R17 were both hiding behind this one** and only surfaced once
GLOB entered the adaptive engine and started valuing its input.

Predicted yield against the curve was 0.150 charcoal and 0.500 tallow
per single glob, both under a package. Actual on a `[9]` stack under
the corrected class: 0.443655 charcoal, 0.110914 ash, 1.478851 tallow,
paying one cinder and one jug and carrying the remainder.

---

### R18. A runtime cloned reaction is invisible to the adaptive engine
**Status: FIXED, verified in play**

`JIT_CONFIG` is keyed on the reaction key the module DECLARED:

```lua
JIT_CONFIG[MODULE_PREFIX .. r.key] = cfg
```

The per retort drains are cut at runtime as
`MAKING_FUEL_RXN_RETORT_DRAIN_B5`, which is not a declared key. The
lookup missed, `swap_to_ghost` was never called, no products were
written, no snapshot was taken and nothing settled. DF completed the
job on the authored slots and minted liquid that nothing paid for.

**Every symptom was downstream and none of them named the cause.** The
only trace was two reaper lines:

```
REAPED unpaid INORGANIC:MAKING_FUEL_OIL_BONE #1564, jug #1468 freed
```

with the key correctly consumed and IN LEDGER, the jugs correctly
PRESERVED, and no `Ghost Swap` line anywhere for that job.

**Fix.** `register_alias(clone_code, base_code)` points the clone at
the SAME cfg table as the base, so the two cannot drift. The clone's
maker declares what it is; the engine does not guess from the name,
because a name test would make the engine know a watcher's private
naming scheme and would break the day a declared key looked like one.
Re-asserted every poll, because the ghost rebuilds `JIT_CONFIG` in its
own `start()`.

Two things came out of it that are worth more than the fix. An
unadopted module reaction is now NAMED at level 0 instead of silently
completing on its authored counts. And `resweep_orphans()` exists,
because `sweep_orphans` runs inside `start()` before any alias can
exist, so a job left mid drain across a cycle was passed over.

---

### R19. `base_cache` holds reaction pointers across a data cycle
**Status: FIXED, verified in play**

Second whale after an ESC menu, cancelled instantly with "needs
corpse". The probe caught the filters being rewritten after the swap:

```
[0] r0 type=CORPSE mat=0/8     <- inorganic gated
[1] r1 type=TOOL   mat=0/83    <- inorganic gated
[2] r2 type=TOOL   mat=-1/-1   <- untouched
```

`mat_type 0` is INORGANIC and a corpse is 22, so slot 0 could never be
satisfied.

`repair_filters` is the only thing that writes a material onto a live
job filter, and it copies from `base.reagents[ri]`. `base_reaction`
cached raw `df.reaction` POINTERS in `base_cache`, and that table was
**never cleared anywhere**. `CLEAR RXN: Excised 594 injected reactions
from RAM` freed them all.

**The third filter surviving is the proof.** `repair_filters` only
writes where `ri < #base.reagents`, so the object it read had exactly
two reagents. `RETORT_CORPSE` has three.

The file already stated the rule it broke, eight lines above the block
that misses it: *"Ghosts must not be held across a RAM transition.
They become dangling the moment clear_module_assets() runs."* That
block clears `ghost_cache`, `audit_state` and `seen`. `base_cache` was
never added to it.

**Fix.** The cache validates itself on read: a cached object whose own
`code` no longer matches the one asked for is dropped and the array
rescanned. Clearing depends on someone calling a hook; a comparison
cannot be forgotten. Cleared in `start()` as well, deterministically.

`base_reaction` also stopped caching MISSES. The old `false` sentinel
was safe while every reaction existed at boot; it is not now that the
drain key watcher mints clones during play.

`drain_mat_cache` was given the same treatment, unmeasured and on
purpose. It holds inorganic INDICES, which survive a cycle only while
the material count does not change. Install or remove a module and the
drain would pour the wrong liquid into a jug.

---

### R20. An unreadable slot was treated as feed. CTD 1
**Status: FIXED, verified in play**

`slot_preserved` read `rxn.reagents[ri].flags.PRESERVE_REAGENT` inside
a pcall and returned `false` whenever the read failed, which puts the
item in the consumable pile. **That default is backwards: not knowing
what a slot is must never mean burn it.**

A corpse job expanded to five vessel slots. A data cycle deleted its
ghost, and `sweep_orphans` reverted the job onto `RETORT_CORPSE`,
which declares three reagents. Reagent indices 3 and 4 did not exist,
the read threw, and both of those jugs were valued as feed:

```
. aluminum jug  size=30  INERT  d=2700  = 0.000000
. aluminum jug  size=30  INERT  d=2700  = 0.000000
INERT REFUSED: job 19 holds aluminum jug, which does not burn.
```

**Exactly two, which is five items minus three reagents.** That count
is the fingerprint.

**Fix.** Three outcomes now differ honestly: no owner recorded stays
not preserved, a successful read is obeyed, and a failed read is
treated as PRESERVED and named once per item.

---

### R21. The INERT refusal was re-asserted every poll. CTD 1
**Status: FIXED, verified in play**

A refusal is a terminal verdict. It was written and logged on every
poll, roughly six times a second, for sixteen seconds: writing to a
live job's flags and re-reading an item list DF was concurrently
releasing. Then a CTD in "Advancing unit moves".

**Fix.** The suspend write is skipped once the job already carries it,
so nothing touches a job DF has already parked, and the report is
keyed on the job so it is said exactly once.

Shipped in the same round: `repair_filters` never shrinks past an
occupied filter. With R20 fixed the job survives to the shrink block,
which would compute a target of 3 against 5 filters and erase slots
with items standing in them. Fixing one defect created that hazard, so
both went in together.

---

### R22. An expanded job cannot complete against a smaller base. CTD 2
**Status: FIXED, verified in play**

With R20 and R21 in, the loop was gone and the crash moved to the end
of the job, which is where it belongs. See L7.

```
FILTER REPAIR: job 10 has 5 filters against 3 reagent(s), but 5 of
               them are occupied. NOT shrinking; ...
SLOT DESYNC: job 10 filters=5 expected=3 (reagents=3, 0 folded).
```

for eleven seconds, then a crash as the job finished.

**Fix.** `reconcile_reagents` grows the reaction to match the job. The
job is the ground truth: DF has already fetched the items, the filters
are already written, and a dwarf is standing at the furnace.

**Growing rather than re-pointing, deliberately.** Pointing the
surplus filters at an existing vessel reagent is a smaller write, but
it produces a shape DF has never been asked to complete, two filters
claiming one reagent. Growing produces 5 reagents against 5 filters,
which is exactly what a normal expansion produces and what this fort
completes every day. After three crashes the right choice is the one
that reproduces a proven shape.

**Reagent AND product together, registered with `expand_state`.**
`collapse_vessels` erases a TRIPLE off the end, `st.n` times. Growing
reagents alone would leave it removing a product expansion never
added, and `slots_for_liquid` would find no claim on the rebuilt slots
and grow the reaction again next cycle. The rebuilt products carry
count 0, so the surplus jugs are held, released empty, and their
liquid banks. The allocation those slots once had died with the ghost
and is not recoverable; inventing one would be worse than banking.

Verified in play:

```
VESSEL: job 10 kept 5 filter(s) across a data cycle but its rebuilt
        reaction declares 3. Rebuilt 2 vessel slot(s) so the job can
        finish
RETORT_CORPSE  job 10  BURNED
```

---

### R23. The drain key stutters between completion and settle
**Status: FIXED, verified in play**

Cosmetic, and recorded because the timing is instructive. The key is
consumed when the drain job COMPLETES, not when it starts (L9). The
bank is not debited until the job leaves the list and the ghost
settles it. In that gap the watcher saw no key and a bank still
reading full, minted a replacement, and withdrew it a poll later:

```
DRAIN KEY: retort 5 holds a package of OIL_BONE; key minted.
FUEL GHOST: RETORT_DRAIN_B5  job 13  BURNED
  bank oil_bone 0.575624 carried in BANK_OIL_BONE@5
DRAIN KEY: retort 5 has nothing left to drain; key withdrawn.
```

Same second for the first three.

**Fix.** A key that was there and is gone now, with the bank still
reading full, is a key a job just took. That retort sits out exactly
one poll. The previous state is written from a RE-COUNT at the end of
the poll rather than inferred from the held count, because a key the
watcher withdrew itself must not look like one a job consumed.

---

### R24. Five coal-family reagents name materials that do not exist
**Status: FIXED, applied, not yet run in play**

`MODULE REACT` logged `mat_id [BITUMINOUS_COAL] did not resolve` twice
and `[COKE]` three times, each shipping the reagent **UNGATED**.

Measured, not assumed: on a mat_id miss the react builder writes
`mat_index = -1` and leaves `mat_type` at whatever the type table set.
`REAGENT_TYPES.BAR` is `mat_type = 0`, INORGANIC. So the live filter is
`item_type BAR, mat_type 0, mat_index -1`: **any inorganic bar**, steel
included.

**The two coal reagents are a plain typo.** `BITUMINOUS_COAL` does not
exist; the vanilla id is `COAL_BITUMINOUS`, words reversed. Proven by
its own sibling: `RETORT_BITUMINOUS` uses the correct form and has
never warned.

**The three coke reagents used the wrong mechanism.** `type: BAR` with
`mat_id: COKE` resolves against inorganics, and this module's coke is a
plant material (L14). They become `type: BAR_ANY` with
`reaction_class: COKE`, the shape three sibling reactions already use.

**Why NOT a coal-typed reagent, which is the tempting fix.** See L15.
`BAR_COKE` would be caught by the fuel widener and dissolved into the
building's tier class, so a coke requirement would become "any smelting
fuel". On `SMELT_CALCIUM_CARBIDE`, which is `fuel: true` at a Smelter,
the reagent and the job's own fuel slot would become the same filter.
Charcoal would make calcium carbide.

---

### L14. Coke is a PLANT material, and both directions are intercepted
The module's coke, charcoal and coal live on `MAKING_FUEL_COAL_HOST`,
not in the inorganics. The reason: a plant bar disguises as vanilla
coke perfectly, where an inorganic renders an awkward name.

Reactions still MINT the vanilla builtin, `BAR_COAL` with
`mat_id: COKE`, resolving through `mat_subtypes` to
`mat_type 7, mat_index 0`. That is not a contradiction, because
**builtin coal is intercepted in BOTH directions**:

- **Outputs.** `making-fuel-coal-watcher.lua` holds the invariant that
  no builtin coal bar exists in the fort's world, ever, except the
  fuel-access menu key. Charcoal (1), coke (0) and refined coal (-1)
  are replaced the frame they appear:
  `REPLACEMENT_FOR = { [1] = 'CHARCOAL', [0] = 'COKE', ... }`.
- **Inputs.** `making-fuel-fuel-access.lua` widens any job filter
  asking for builtin coal, at job posting, to the building's tier
  class. See L15.

So a reagent written against builtin coal is not broken. It is fixed
automatically. That is the design.

The watcher's comment explains why the classes cannot simply live on
builtin COAL: tagging it made the fuel-access menu key legal fuel and
a dwarf burned it, measured repeatedly at cost.

**For anyone auditing materials:** a sweep of
`making_fuel_materials.json` sees the inorganics only. The plant hosted
materials in `making_fuel_plants.json` are a second, equally real
namespace, and any "this material does not exist" check that reads one
file is wrong. See X9.

---

### L15. The fuel widener matches on SHAPE, so coal-typed means fuel
`is_fuel_filter` fires on `item_type == BAR and mat_type ==
df.builtin_mats.COAL`, whatever the mat_index, and `widen` then
rewrites that filter in place: `mat_type -1`, `mat_index -1`,
`reaction_class` set to the building's tier class, `item_type` to the
tier floor. `FUEL_TIERS` gives Smelter, GlassFurnace and
MetalsmithsForge `FUEL_SMELTING` with a BAR floor; everything else
gets `FUEL_CLASS`, which is `FUEL`.

**The widener could not tell a fuel slot from a material slot.** It
had only the shape to go on, so any reagent typed to builtin coal was
widened as fuel. Superseded 2026-09-22 by the owner test, below.
Module reactions should still never type a reagent as builtin coal;
name the coal by identity class (`COKE`, `CHARCOAL`, `COAL`).

`BAR_ANY` with a `reaction_class` is invisible to it on both branches:
`mat_type` is -1 rather than COAL, and the class is `COKE` rather than
the tier's. That is what lets a coke requirement survive while the same
job's real fuel slot is widened normally.

**The OWNER decides (2026-09-22).** On a reaction job, a builtin coal
filter that names a reagent is a COAL REAGENT; vanilla PIG_IRON_MAKING
and STEEL_MAKING type their carbon this way. `widen_coal_reagents`
swaps it for the module's coals FIRST, at every building, tanked or
not: coke (mat_index 0) takes `COKE`, charcoal (1) takes `CHARCOAL`,
and no variety (-1, what vanilla writes) takes `FUEL_SMELTING`, which
only the three module coals and their briquettes carry, always with the
BAR floor. The building's tier class is never used for a reagent:
outside the smith tier it is `FUEL` with no floor, and would take dung.
A builtin coal filter that names no reagent is the FUEL SLOT: the tiers
widen it and the tank erases it, and every other fuel slot operation
(counting, the bulk copies, the stop and start sweeps, the tank's
erase, keep and restore, and the ghost's filter repair) asks
`is_fuel_slot` in tuning. See L21.

A second reason a module reaction must never type a reagent as builtin
coal: on a ghosted reaction, `repair_filters` restores the authored
material every poll, so the widened carbon slot goes back to builtin
COAL, which the coal watcher guarantees does not exist, and the job
waits forever.

---

### R25. A burn fetched a second stack it never consumed
**Status: FIXED, verified in play**

Long standing, seen on meat and on corpses, and it was TWO writes in
the ghost fighting one watcher.

**Write one, the demand.** The stack rule set the job item quantity
alongside the reagent:

```lua
ghost.reagents[ri].quantity          = n
job.job_items.elements[idx].quantity = n   -- this one
```

This file had already measured the second unnecessary, at 2508:
*"consumption per completion is the RAWS reagent quantity (measured:
one unit per cycle even with the job item zeroed) ... the job item
quantity only governs SEEKING."* And it does not count what is
attached: a stack in transit contributes nothing, so a stack of twenty
raised the demand to twenty, counted the stack as zero, and sent
someone for more. Removed.

**Write two, the seal.** `repair_filters` cleared the material off
EVERY filter every poll, including one the rot watcher had
deliberately sealed. MEASURED on job 25:

```
r0 q0  type=MEAT mat=21/296   <- rot watcher, sealed to rotten wolf meat
r0 q20 type=MEAT mat=-1/-1    <- one poll after the ghost swap
```

So the demand came back on a filter that now read "any meat", and DF
filled it with a chopped naked mole dog liver.

`repair_filters` now skips OCCUPIED slots. Its own comment says it
exists for the RE-POST case, where DF rebuilds job_items from the
clone and inherits a race lock that stalls the job, and a re-post
starts with nothing attached. An occupied slot is not seeking and
cannot stall.

**That is also what R19 was.** The corpse crash was this same loop
stamping `0/8` onto an occupied slot from a stale base pointer. Both
faults are one loop writing a material onto a slot whose item had
already arrived.

**And the thrash.** Two items in one slot meant each visit rewrote the
reagent to its own size, so the quantity flipped between 20 and 5
forever while the rot watcher pushed back from the other side, over a
hundred log lines in one run. A slot now decides once, from the first
item, which is the one that was actually sought.

A slot the stack rule raises should hold exactly one item. Two now
says so at level 0, once per job and slot.

---

### R26. The rot key was a boulder, so it sat in the build menu
**Status: FIXED, applied**

The key was minted as `df.item_type.BOULDER`. A boulder is a
construction material, so it appeared in the stone list every time the
player placed a building: the module's own plumbing hanging out of a
menu.

It is a TOOL now, with no `tool_use` and `no_default_job`, which is
inert: nothing builds with it, nothing hauls it to a stockpile job,
and it still carries the `ROTTEN` class that lights the menu. The
material drops to `"rot"` so the item reads **"rot key"**, the same
split the drain key uses.

**Its own itemdef, not the drain key's.** The drain key watcher sweeps
every `DRAIN_KEY` tool it does not recognise as one of its retorts, so
sharing would have that watcher delete this one on its next poll.

**Existing saves migrate.** `is_key` matches on MATERIAL, so an old
boulder key still answers to it, which is the only way it gets found.
Wrong item type, scrapped, tool minted in its place, said once.

**Two older bugs it exposed**, both present before this change:

The watcher placed ONE key, at the first wood furnace in the world
list. The rot reagent carries `nearby`, so a second wood furnace across
the fort already read red. Keys are per building now, one at each site
that can host a rot job, with the honest menu rule applied per site.

And `fill(job, b)` was handed that same furnace regardless of where the
job was queued, while `find_rot` tests reachability from the building
it is given. So a job could draw rot only its neighbour could reach.
Now `dfhack.job.getHolder(job)`.

The harness caught two more before delivery: an early return when no
sites existed skipped the stray sweep, leaving keys lying about
carrying a live reaction class, and the sweep removed items while
walking `world.items.all`, which skips the next entry. Two strays in,
one out.

---

### R27. RETORT_ROT did not exist
**Status: ADDED, verified in play**

`CHAR_ROT` and `ASH_ROT` existed; the retort had no rot reaction. The
refuse reagent is byte identical to `CHAR_ROT`'s and the product types
match `RETORT_HAS_PROTECT_FOLDED_SHEETS` in order. Liquid slots are
`OIL_BONE` and `AMMONIA` like `RETORT_CORPSE`, because rot is flesh.

Verified banking bone oil and ammonia in play.

---

### R28. The bank readout was sized to its skeleton, not its content
**Status: FIXED, verified in play. Third scrollbar.**

The slot count was a formula, `3 + liquids + purses + footers`, which
added the wood furnace's THREE solid rows to the retort's FULL liquid
block. No furnace has both. One surplus row is a blank line at the
bottom of the retort and one row the frame had no room for.

**Sizing the frame alone does not shorten the panel.** `token.line` is
documented as reserved for internal use and is assigned when the token
list is PARSED. A text callback can change what a row SAYS but never
how many rows there are, so a shorter frame scrolls the same lines. I
built that twice before establishing it.

Resizing to content therefore needs `setText`, which this file swore
off after it shipped blank. It is done from `overlay_onupdate`, off the
render path, and only when the ROW COUNT changes, which is once per
kind of furnace opened. `set_rows` is pcall wrapped and only records
the new count on success, so a throw leaves the last good list and
frame in place.

`overlay_onupdate_max_freq_seconds` defaults to **five seconds**, which
would have read as a bug rather than a throttle. Set to 0.

Wood furnace 8, smelter 7, retort 17, from 20 for all three.

---

### R29. Two silent fallbacks to a WILDCARD in build_reagent
**Status: FIXED, applied**

Both resolved a name and fell to a value that means "no constraint",
so a typo did not narrow the filter, it OPENED it, and nothing said so.

```lua
r.has_tool_use = df.tool_uses[rgt_def.has_tool_use] or -1
r.metal_ore    = mat_lookup[rgt_def.metal_id] or -1
```

`-1` on `has_tool_use` is any tool use. `-1` on `metal_ore` is no ore
requirement at all, so an `ORE_OF` reagent with a mistyped `metal_id`
accepted any boulder the rest of its filter allowed.

Same disease the `mat_id` path was cured of. Both now name the reagent
and the bad string; `has_tool_use` falls to the TYPE default where
there is one rather than straight to the wildcard. Neither can do
better than -1 in the end, so the log line IS the fix.

`has_tool_use` also gained an offline vocabulary, `TOOL_USES`, 27
values. `metal_id` cannot have one: it resolves against the inorganic
table, which preflight cannot see without the raws.

---

## Open, not blocking

### R30. The fuel sweeps erased under attached items and took coal reagents' fuel
**Status: FIXED 2026-09-22, verified in play for the bulk surcharge.
Two checks outstanding, below.**

`strip_extras` in making-fuel-access.lua runs at every stop and start
and assumed DF posts exactly one fuel filter. Two faults, both seen on
one HOTSAVE:

- It erased bulk copies with fuel attached. Job 10111 completed on 2
  dried dung of the 4 owed (L22).
- It counted a coal REAGENT as a second fuel slot. The sweep's count of
  4 was job 10111's 3 copies plus, by count, pig iron job 10109's fuel
  slot, so that pig iron cycle most likely burned no fuel.

By the code, the same shape only test also let a tanked smelter's
erase take pig iron's and steel's carbon reagent along with the fuel
slot. The owner test alone moved that fault rather than closing it:
the tank branch of `widen_job` never widens, so the carbon reagent was
then left as raw builtin coal, which the coal watcher makes sure never
exists, and the job would be cancelled. Closed by
`widen_coal_reagents`, which swaps coal reagents for the module's
coals before the tier or the tank sees the job (L15).

**Fix.** The owner test everywhere past the widener (L21). The sweeps
never erase under an attached item; a busy job's copies are adopted
into the surcharge memo and come off at its cycle boundary. Both
removal paths take fuel slots by what they are, never by position.

**Verified in play, 2026-09-22.** A boil collected 4 after a HOTSAVE,
and again from the save after a full recycle.

**Still to check.**

- A HARDCODED fuel job (smelt ore, melt, smithing, raw glass): the
  probe must show its fuel slot at owner -1. The owner test was proven
  on reaction jobs only (L21). If a hardcoded job's fuel slot carries an
  index, it fails `is_fuel_slot`, and on a TANKED furnace `widen_job`
  marks the job handled without widening it, so it waits on raw builtin
  coal and is cancelled.
- Pig iron keeping its fuel slot through a HOTSAVE: PARTLY DONE
  2026-09-22. After a hotsave the access layer restarted, resolved the
  smelter tier, and logged neither a sweep nor an adoption, so nothing
  was stripped from any job, and the pig iron job completed normally. No
  probe listing was taken across the save, so the filter count itself is
  still unread.
- A steel or pig iron job at a tanked smelter (probe: the carbon reagent
  at owner 2 as FUEL_SMELTING BAR and no fuel slot; the job completes on
  module coal with the tank paying).

### R31. Jug expansion and the fuel copies share the job's tail
**Status: FIX DELIVERED 2026-09-22, not yet verified in play. The
standing rule holds until it is: no fuel on any ghosted reaction that
makes liquids (the retort reactions and the distils).**

Both append to the END of `job_items`, so taking the last N could erase
fuel filters while deleting the reagents the jug filters name, which is
the R22 crash.

**Fix.** Neither side reads position now. The fuel side removes its own
copies, which own no reagent. `collapse_vessels` removes the filters
owned by the reagents it appended, at or past the base reagent count,
which covers both `append_vessel_triple` and the slots R22's reconcile
rebuilds. `ghost.reagents` and `ghost.products` are the ghost's alone,
so those still come off the end by count, and they come off whether or
not their filters were still there. The VESSEL line now reports both
counts. `append_vessel_triple`'s fallback prototype is chosen by owner
as well: taking the last filter outright could clone a bulk fuel copy
into a jug slot.

**Verify.** It has to be an ADAPTIVE distil, because only a ghosted
reaction expands jugs: DISTIL_TAR, DISTIL_TAR_COAL or DISTIL_OIL. A
fixed count one proves nothing here. MEASURED 2026-09-22:
DISTIL_METHANOL ran at a still with fuel on and burned it, but its
products carry counts, so the ghost never touched the job and no jug
was ever appended. Turn fuel on for one of the three, run a cycle that
actually expands jugs, and read the VESSEL line: as many filters
released as jug slots, and the job's DETAIL line keeping its fuel
count. Only then does the standing rule lift.

### R32. Builtin coal in item types other than bars
**Status: FIX DELIVERED 2026-09-22, not yet verified in play**

The coal watcher converted bars only, so builtin coal in any other item
type sat in the fort as dead fuel, and nothing widened a requirement
for one either. Vanilla never makes one, and whether a raws-only mod
can is untested, but `dfhack.items.createItem` takes any material with
any item type, so a script, create-item, or anyone writing an RM module
can (L23).

**Fix.** The watcher rewrites a non-bar's material in place, per
variety, on the item created event and in one opening sweep of all
items at start. An item a job holds is deferred and retried by the
poll, because the job matched it on the material being rewritten. Bars
keep the replacement path, which is proven. `widen_coal_reagents` in
the fuel access layer takes a coal reagent of any item type and keeps
the type it asked for, swapping only the material (L15).

**Not covered.** There is no repeating sweep of every item. Everything
minted fires the created event, and only trade, migrants and invaders
arrive without one, none of which carries builtin coal today. If one
ever does, a slow full sweep is the answer.

### R9. Bones classify FLESH, not BONE

**Status: FIXED, verified in play**

**Both recorded causes were wrong.** This entry first blamed
`spec_heat >= 4000`, and `BONE_TEMPLATE` is 1000, so bone clears that
gate comfortably. It then blamed the material handed to the classifier.
The real cause is neither: `item_value` computes `classify(mi)` at the
top for every item and the CORPSE and CORPSEPIECE branches **throw the
answer away**, returning the literal string:

```lua
return whole * frac, size * frac, 'FLESH', nil, 'piece', nil, size, frac
```

Every bone, skull, hide and severed limb was priced as wet tissue by
construction. The `d=-` on every bone line is the same branch: it
returns nil density deliberately.

**The discriminator is `corpse_flags.unbutchered`**, and it partitioned
30 pieces in one fort exactly along the line that matters, without
being told which was which:

| | n | what they are |
|---|---|---|
| without the flag | 12 | two buffalo butchered in game: `bone [14]`, `horn [2]`, `hoof [4]`, skull, skin, nervous tissue |
| with the flag | 18 | 8 dwarf and 10 dragon parts, all whole create-item pieces |

That matters because a piece is two different items wearing one type. A
butchery product is one tissue by construction. A severed part is
several tissues wearing whichever one covers it, which is why a dwarf
arm reads `DWARF:SKIN` and a dwarf head reads `DWARF:HAIR`. Neither is
made of that.

**DF confirms the classifier independently on the butchered set.**
`corpse_flags` carried `bone` on the bone stacks, `horn` on horns AND
hooves, `skull` on skulls, `rottable` on skin and nerve. Every one
agrees with what `classify()` returns from the material.

Fixed by classifying butchered pieces only. Held safe three ways: an
unbutchered piece keeps FLESH, a class outside the tissue whitelist
(FLESH, BONE, LEATHER, HAIR, FAT) keeps FLESH and logs, and an
unreadable flag reads as unbutchered so nothing moves.

Verified in play:

```
STACK: job 23 takes all 14 of #1598 in one run
. water buffalo cow bone [14]  size=45413  BONE  d=-  [piece:BONE]  = 1.421648
  ammonia  bank 0.000000 + 1.015463
  oil_bone bank 0.000000 + 1.015463
```

Whole stack, `piece:BONE`, and the two currencies **dead equal**, which
is `FLUID_SPLIT.BONE` at half and half arriving. The ammonia vessel had
been starved since it was written.

**The balance shift, measured rather than assumed.** One butchered
buffalo, by relsize share:

| pieces | share | class |
|---|---|---|
| bone 0.4541, horn 0.0204, hoof 0.0489, skull 0.0204 | 0.5438 | BONE |
| skin 0.6384, nervous tissue 0.0407 | 0.6791 | FLESH |
| sum | **1.2229** | |

**That sum was already over 1.0 before any change**, see L6. Butchering
has always beaten charring whole by 22 percent. With BONE at 2.80x the
butchered route goes to 2.2017x, a 1.80x move rather than a departure
from a clean 1.0. The ruling: charring a whole corpse wastes more
than carefully tending the pieces, and the module already simulates
gain through reduced loss in kindling. The lever if it ever wants
shrinking is `CLASS.BONE`, currently 0.350 against FLESH 0.125.

### R10. Stale coupled constant comment
**Status: PROVEN, cosmetic**

The COUPLED CONSTANT note above `LIQUID_STANDARD` says
`TAR_UNITS_PER_PITCH` must equal pairs times package size "(currently
2 x 1)", while the constant is 3 and the canonical boil is a single
pair of one unit. The mechanism is coherent, the comment is not.
BOIL zone is locked, so this waits for its own pass.

**A second stale comment found 2026-09-08.** Line 2294 of
`making-fuel-ghost.lua` says filters are unlocked again in
`normalize_slots`. There is no `normalize_slots` in the file.

### R11. The coke family is static by design and not yet converted
**Status: NOT A DEFECT, scoped work, and a tail**

```
RETORT_LIGNITE             1 lignite   -> 5 coke + tar_coal + ammonia + ash_coal
RETORT_BITUMINOUS          1 bituminous-> 9 coke + tar_coal + ammonia + ash_coal
RETORT_LIGNITE_FLUXED      + flux      -> 5 coke + tar_coal + ammonia + gypsum + brimstone
RETORT_BITUMINOUS_FLUXED   + flux      -> 9 coke + tar_coal + ammonia + gypsum + brimstone
RETORT_SHALE_OIL           1 shale oil -> 2 coke + oil_crude + ammonia + ash_coal
BOIL_HIDE_GLUE             1 hide      -> 1 glue
BOIL_BONE_GLUE             1 body part -> 1 glue
```

Every product carries a nonzero count, both vessels are paid, and
there is not a single zero count slot among them. They are clean
static recipes. They mint real stack 1 liquids, suffer none of R1
through R5, and clog no jugs. Nothing here is broken.

They live in `making_fuel_reactions_processing.json`, which makes them
a tail by the priority rule.

Two prerequisites before conversion, both measured:

1. **`FLUID_CLASS.MINERAL = 0.000`.** These bottle TAR_COAL, OIL_CRUDE
   and AMMONIA, and mineral coal classifies MINERAL. Going adaptive
   today would give every one a dead liquid limb while the vessels
   still hauled. Identical bug shape to `FLUID_CLASS.PEAT = 0.000`.
   `CLASS.MINERAL` is already 1.000, so the solid side is ready.
2. **The classifier treats MINERAL as a fault signal.** Adaptive coke
   makes mineral fuel legitimate feedstock, which retires that
   invariant. The detector has to be re-aimed or it will cry wolf on
   every coke job.

### B1. Tar outruns vinegar four to one
**Status: NOT A DEFECT, balance question, a design call, still open**

| | per log | one jug every | over 12 logs |
|---|---|---|---|
| TAR_WOOD | 0.7867 | 1.27 logs | 9 jugs |
| VINEGAR_WOOD | 0.1967 | 5.1 logs | 2 jugs |

That is `FLUID_SPLIT.WOOD = { TAR_WOOD = 4/5, VINEGAR_WOOD = 1/5 }`
working exactly as written.

**The vinegar heavy figure is a real number.** Raw pyroligneous acid is nearer
35 percent of a log against tar's 10, so the raw distillate genuinely
IS vinegar heavy. The file models CONDENSED usable vinegar at 2.5
percent because raw acid is roughly 90 percent water, and that choice
flips the ratio.

**The demand side cuts the other way.** Vinegar has five consuming
reactions and one takes two packages: `MAKE_ANILINE`, `DYE_MAGENTA`,
`DISTIL_METHANOL` (2), `MAKE_VERDIGRIS`, `MAKE_IRON_BLACK`.

**The ceiling limits the obvious fix.** Raising `FLUID_ANCHOR_UNITS`
lifts both, but tar already accrues 0.79 against a 1.0 package. The
lever that does not fight the ceiling is the split ratio: moving WOOD
to 3/5 and 2/5 gives one vinegar per 2.5 logs and one tar per 1.7, at
the cost of slowing pitch.

Not changing anything without a decision.

### Housekeeping, found while fixing the above
**Status: PROVEN, all minor, none blocking**

| item | detail |
|---|---|
| ~~`expand_state` leak~~ | **CLOSED 2026-09-09.** `start()` clears it, along with `live_jobs`, `vessel_poll` and `pool_room_cache`. |
| ~~ghost accumulation~~ | **CLOSED 2026-09-09, and the premise was wrong.** Ghosts carry the module prefix and the engine sweeps by prefix on every data cycle, which is every ESC press and every save. Proven in the log: `Cleared [MAKING_FUEL_]: 436 reactions` against 430 declared, the extra six being ghosts and drain clones. Not unbounded, and never was. |
| slotless streams are silent | see L3. A currency earned with no slot on this reaction logs identically to one that has a slot. This is what let R16 hide. |

---

## Engine facts learned, so they are not re-derived

### L1. A glob carries both a count and a size
`stack_size` is how many, `dimension` is how big each one is, and the
total is the product. **DF accepts a reagent quantity of
`stack_size * dimension` and consumes the whole item**, verified at
1350 on a `[9]` fat stack. Quantity on a dimensioned reagent is
counted in dimension units, which is why 150 removed exactly one unit
of nine.

### L2. Fat shares muscle's specific heat
`FAT_TEMPLATE` and `TALLOW_TEMPLATE` both carry `SPEC_HEAT:4181`,
identical to `MUSCLE_TEMPLATE`. Any classifier that tests specific
heat before material id will call every fat a flesh. See R16.

### L3. `streams_for` mints slotless streams on purpose
**Announcement SHIPPED 2026-09-08 and correctly silent.**
`handle_ghosted` now reports both directions once per reaction and
currency: a currency earned with no container (legitimate, it banks for
a sibling reaction at the same furnace), and a declared container the
feed never funds (a fault, it pays zero and DF mints a null every run).
Gated so it does not cry wolf: the dead slot message needs the job to
have earned some liquid AND the bank to be empty, because a zero
earning slot is deliberately kept alive so a stranded balance can drain
through it. Ran clean on the corrected RETORT_GLOB with no output,
which is the right answer once slots and split agree.


Liquid streams come from the union of the reaction's declared slots
and whatever the feed actually earned, not from the products alone:

```lua
for cur, at in pairs(cfg.liquid_slots) do ... end     -- declared
for cur, v in pairs(fluids or {}) do
    if not seen_cur[cur] and v > 0 then
        table.insert(s, { currency = cur, at = nil, ... })  -- slotless
    end
end
```

A currency with no slot banks 100 percent of its earnings. That is
coherent, because banks key on currency and building
(`BANK_OIL_BONE@5`), so a sibling reaction at the same furnace pays it
out. Nothing is lost.

**But it is indistinguishable in the log from a stream that has a
slot**, and that is precisely how a fat banked bone oil for as long as
the code existed. The reciprocal tell is the one to watch: a declared
slot the class never names earns 0.000000 and mints a null every run.

### L5. `corpse_flags` is a rich, reliable vocabulary
Read off 30 pieces in one fort. `unbutchered` separates butchery
products from severed parts. `bone`, `horn` (which covers hooves),
`skull`, `leather` and `rottable` describe what a piece is, and every
one agreed with what `classify()` returned from the material. So DF
will tell us what a piece is made of, twice, and the two answers match.

`df.item_corpsepiecest._fields` also enumerates cleanly, so any future
question about these items can be answered by reading the struct rather
than by another round of guessing at field names.

### L6. Piece relsize shares OVERLAP and do not sum to the creature
One butchered buffalo sums to 1.2229 of itself. Each piece reports the
relsize it still holds, and skin covers the same parts the bones sit
inside, so the shares are not a partition. **Additivity against the
intact corpse was never exact for butchered stock.** Any future
argument that starts "but pieces must sum to the whole" is starting
from something that has never been true.

### L4. DF closes collection once the base filters are covered
See R15. Appended slots are honoured while a job is still collecting
and ignored once it is not. The previously recorded finding "slots
added mid collection are honoured" was true but narrower than it read.

### L7. DF cannot complete a job with more filters than the reaction has reagents
Every `job_item` carries a `reagent_index`, and completion looks each
one up on the reaction to decide consume or preserve. An index past
the end is an out of bounds read inside DF.

This is a FILTER naming a reagent the reaction does not have. An ITEM
left pointing past the end of `job_items` is a different mismatch and
did not crash: see L22. Do not read one into the other.

**Nothing reads them while the job is merely working**, which is why
job 10 survived eleven seconds of `SLOT DESYNC` and died on the last
frame. See R22. Any future "the job runs fine and then crashes" starts
here.

### L8. A freed reaction's address is reused by a LIVE reaction
Not corrupted memory. After a wash frees 594 reactions and injects new
ones, a pointer cached beforehand resolves to a real, well formed,
WRONG reaction. In R19 it landed on one of RM's alloy variants, which
carry `mat_type = 0` with a specific inorganic `mat_index`
(`refinish-index-reaction.lua:309` and `:316`) and have two reagents.
Every number in that probe output follows from that.

The consequence for diagnosis: the values look plausible, so "these
numbers are garbage" is the wrong instinct. Ask what object they
belong to.

### L9. The drain key is consumed at COMPLETION, not at job start
It sits attached and preserved for the whole run. Proven: `#1546` is
`IN LEDGER drain key` on job 13 from 00:33:43 through an eighteen
second run. See R23 and X7.

### L10. Visibility is the `building` field. Fort mode is permissions
A reaction's building is four parallel vectors, `type`, `subtype`,
`custom` and `hotkey`, written together in
`refinish-module-react.lua:1469`. All four empty and it appears in no
menu anywhere; `BUILDING_TYPES.NONE` is exactly that.

`FORTRESS_MODE_ENABLED` bypasses permissions entirely. It is not a
visibility lever. `build_ghost_jit` proves both at once: it sets fort
mode true AND empties the four vectors, and its ghosts appear in no
menu. Set it once, never flip it.

`score_template` treats building as 40 points of scoring rather than a
gate, so a reaction declared `building: NONE` still finds a structural
donor.

### L11. Container sizing, measured
- DF divides raws `SIZE` and `CONTAINER_CAPACITY` by 10 on load.
- One liquid package costs **60 volume**. A jug at capacity 1000 holds
  **16**, not the 6.7 a naive capacity-over-dimension division gives.
  Dimension and volume are different currencies.
- `count` does NOT stack for `LIQUID_MISC`. A count of 50 minted a
  stack 0 null. The amount goes in `product_dimension`, and the item
  reads as a percentage of 150: 1600 percent is 16 packages.
- DF does NOT enforce `container_capacity` on a reaction product.
  Dimension 2550, which is 1020 volume in a 1000 jug, succeeded. The
  limit is ours.
- **DF re-reads a product's material at COMPLETION**, not at job
  creation. A slot authored `OIL_BONE` and rewritten mid job minted
  ammonia. This is what makes the drain's runtime material assignment
  legal.
- A barrel has no itemdef, so `SIZE` and `CONTAINER_CAPACITY` do not
  exist for it, and its volume EXCLUDES its contents. Barrels were not
  adopted; the sizing answer removed the need by making every vessel
  fill to its own capacity instead.

### L12. The module engine sweeps by PREFIX, not by manifest
`refinish-module-engine.lua:1203` for reactions, `:1239` for
materials, LIFO. Anything carrying `MAKING_FUEL_RXN_` or
`MAKING_FUEL_` is collected by the same loop that collects the
declared set, with no registration call.

That is what makes runtime minted ghosts safe, and it is why
`making-fuel-drain-key.lua` deliberately has no cleanup: a `stop()`
that popped them would be a double free. Contrast
`making-fuel-tinder-mat.lua`, whose twins hang off vanilla plants
where no sweep reaches, which is exactly why THAT file needs its own
pop.

### L13. Watchers start before injection, and after `ledger.write()`
`start_background_scripts()` is called from inside the module
listener, which RM broadcasts at Step 2 BEFORE injecting anything, and
startup runs synchronously through Step 8. So the first POLL lands
after `ledger.write()`.

Two consequences. A lookup at watcher start always misses, so a miss
must never be cached. And a material minted from a poll is recorded
after the snapshot every session without exception, so the ledger can
never remap an item made of it. The drain key is not defended against
that; it is purged and re-minted at session start instead.

### L16. `dead_dwarf` means "not butcherable", not "dwarf"
Measured on four real corpses in one fort:

| corpse | civ | isCitizen | isPet | dead_dwarf |
|---|---|---|---|---|
| amphibian man, sapient INVADER | 163 | false | false | **true** |
| giant cave toad, wild ANIMAL | -1 | false | false | **false** |
| a dead CITIZEN dwarf | 276 | **true** | false | **true** |
| a PET sheep | 276 | false | **true** | **true** |

True for citizen, pet AND invader; false only for the wild animal. It
is the exact inverse of `butcherable`, which matches what a butcher
will take: animals and nothing else.

`dfhack.units.isCitizen(unit, true)` **answers on the dead**, contrary
to the API docs describing it as "non-dead". That is the only thing
separating a citizen from an invader, and it lives on the UNIT.

`corpse_flags` on a real corpse are `bone, rottable, unbutchered,
use_blood_color`. The field is `unbutchered`, meaning not yet
butchered, NOT `unbutcherable`. It is not a discriminator.

### L17. DF keeps 136 job item vectors, and they do not mean their names
`ANY_DEAD_DWARF` holds citizens, pets AND sapient invaders, which is
the `dead_dwarf` flag by another route. `ANY_BUTCHERABLE` holds **all
nine** corpses in the fort including the citizen and the pet, so it is
not "what a butcher would take" either.

Neither vector can separate a citizen from a goblin. Reading a vector's
CONTENTS is the only way to know what it holds; the name is not
evidence.

### L18. DFHack types and instances enumerate differently
`pairs()` on a TYPE returns its metatable: `_first_item`, `_last_item`,
`attrs`, `is_instance`, `sizeof`. Not its contents.

- Enums: walk by index from `_first_item` to `_last_item`.
- Bitfields and structs: `pairs()` on an INSTANCE, or `_fields` on the
  type.

This cost a whole probe round. One build reported no `df` identifier
containing "dwarf" while the section three lines below it was reading
`item.flags.dead_dwarf` successfully, and reported eleven vector ids
named `_complex` and `sizeof` where there are 136.

### L19. What a reagent can express, audited end to end
- **83 of 83** named `job_item` flag bits are reachable. Two look
  missing and are not: `glass` is reached as `glass_material`, an alias
  at `refinish-module-react.lua:305`, and `sand_bearing` lives at the
  reagent ROOT with preflight erroring if it is put inside `flags`.
- `flags4` and `flags5` are plain integers the engine zeroes, not
  bitfields with named bits.
- Every authorable `job_item` field is written. The six that are not
  are `reagent_index` and `reaction_id`, which are engine managed, and
  the four `job_details_*`, which are the job details UI.
- Five fields resolve a NAME: `mat_id`, `tool_id`, `metal_id`,
  `has_tool_use`, `vector_id`. All five now report a miss.
- Offline vocabularies exist for `vector_id` (136) and `has_tool_use`
  (27). `mat_id`, `tool_id` and `metal_id` cannot have one for vanilla
  names, but `check_cross_references` already validates the module
  prefixed half of `mat_id` and `metal_id`, and
  `check_asset_references` does the same for `tool_id`.

### L20. `df.tool_uses` has 27 values, `NONE` included
`NONE` is legal and means the item must have no tool use at all. The
list is in `TOOL_USES` in the types file, enumerated from a live game.

### L21. The fuel slot is the filter that serves no reagent
DF writes the fuel requirement as one extra `job_item` with
`reagent_index` -1, first measured by the ghost on a live
MAKE_CLAY_JUG. Every reagent filter names its reagent. MEASURED,
making-fuel-filter-probe build F1: pig iron job 10109 carried its
carbon reagent at owner 2 and the fuel slot beside it at owner -1, both
BAR and both FUEL_SMELTING once widened; boil job 10111 carried its
four bulk fuel slots at -1 and its container at 1. Shape and class
cannot separate the two; the owner always does. `is_fuel_slot` in
tuning is the one definition, and the fuel access layer and the ghost
both call it.

### L22. An item stranded past the end of `job_items` did not crash completion
MEASURED, job 10111, BOIL_TAR at the kitchen: a HOTSAVE's start sweep
erased three bulk fuel copies while dried dung sat in one, leaving 3
attached items against 2 filters. The ghost logged the item as held in
a slot the job does not have and treated it as preserved. DF completed
the job normally and burned only what it held, 2 dried dung of the 4
owed. Measured once, so "did not crash" is a record, not a guarantee;
the cost that is certain is the underpaid cycle. Contrast L7.

### L23. Builtin coal is legal in every item type tried, and a plant material replaces it in place
MEASURED, making-fuel-coal-form-probe build C1, one fort.
`dfhack.items.createItem` accepted builtin coal in BAR, POWDER_MISC,
GLOB, BLOCKS, FIGURINE, BOULDER, ROUGH and SMALLGEM, the last three
being types DF itself only makes of stone or glass. Each rendered,
stockpiled and was hauled normally, and each sat inert as fuel while it
was builtin coal, which is the whole problem: builtin COAL carries no
reaction class.

Writing our charcoal, a PLANT material, straight into `mat_type` and
`mat_index` worked on every one of them. The descriptions came out
right ("rough charcoal", "charcoal blocks", "charcoal figurine of kea
men"), the values were unchanged, each then carried FUEL and
FUEL_SMELTING, and a kiln burned every one of them as fuel. Nothing
crashed.

A POWDER_MISC vanished the moment it hit the ground and a GLOB vanished
from its stockpile: DF cleans both as mess. That is DF's housekeeping,
not a limit on the rewrite.

---

## Verified working, do not re-litigate

### V1. The corpse piece fluid limb is additive
Verified against the live log to six decimals: whole 6000, share
0.334373, solid 0.091572, oil_bone 0.206037, ammonia 0.068679.

### V2. The one package ceiling and the bank arithmetic
Deposits, splits and thresholds all compute correctly. Every ledger
figure in every session reproduces from the tuning constants. The
accounting was never the problem.

### V3. TOOL feed `tool_id`
Recorded as a defect in an older session. Already present in the
mirror on `RETORT_KINDLING` and the rest of the TOOL feed family.

### V4. The multi package payout, which had never run
**VERIFIED 2026-09-08.** The slot surgery entry below used to end
"still untested: the payoff". It has now run at full scale. A giant
sperm whale, 47 filters, `PHASE: job 10 working (attached=47
filters=47)`, bottling 35 oil and 11 ammonia in a single job and
leaving 0.575624 and 0.858541 banked, both under a package and exactly
the predicted remainder.

`VESSEL_MAX_FILTERS` at 47 is now the binding constraint on a whale,
not the jug supply. Job 10 had 96 containers free and still reported
`stopped at 47 filters` and `earned 36 oil_bone but can only bottle
34`. That is working as designed and it says so to the player.

---

### N1. gui/create-item bones are malformed, butchered bones are not
**Status: PROVEN, affects test setup only**

| | created peasant bone | butchered buffalo bone |
|---|---|---|
| material_amount | 1 | 14 |
| body parts present | 12 | 16 |
| relsize present | 3000 of 8972 | 4460 of 9821 |

A created single carries a whole skeleton's part list against a count
of one. **Balance testing must use butchered stock.** Mechanism
testing is still valid on created bones.

### N2. The AFTERMATH probe's growth check is a false positive
**Status: PROVEN**

It flagged four base reactions and concluded "A GROWN BASE IS THE
FAULT". Every one matches its authored JSON exactly:

| reaction | probe read | authored |
|---|---|---|
| RETORT_LIGNITE_FLUXED | 4 reagents, 5 products, 2 vessels | identical |
| RETORT_BITUMINOUS_FLUXED | 4 reagents, 5 products, 2 vessels | identical |
| RETORT_PEAT_DRIED | 4 reagents, 7 products, 3 vessels | identical |
| RETORT_PEAT | 4 reagents, 7 products, 3 vessels | identical |

No base grew, and RETORT_CORPSE was not even in the list. The check
compares against a fixed threshold instead of the authored shape, so
it accuses reactions for having three vessels. **Same signature this
register already warns about: a discriminating test that never
discriminates.** It cost the better part of a session.

### N4. The test that never discriminates, THREE TIMES NOW
**Status: STANDING NOTE, read this before writing any probe**

Three separate times a column has read the same for every row and been
believed anyway:

| | what read flat | cost |
|---|---|---|
| `canWalkBetween` | every jug reported the same reachability, including ones standing at the workshop | two sealed jugs counted as available |
| AFTERMATH growth check | four reactions accused of growing when they matched their authored shape | most of a session chasing a base mutation that did not exist |
| `isTemperatureSafe` | every material read false, including one that cannot burn | a wrong verdict on the fire_safe gate, X5 |

The register already carried the first as a lesson and it did not stop
the second or the third.

**So it is a rule now.** Every probe that reports a column must also
state, in words, whether that column actually separated anything, and
must refuse to draw a conclusion when it did not. Two of the three
above were caught only because a reader noticed the flat column by eye.
A cross-check costs a few lines: `isDamagedByHeat` returning true for a
material with no heat damage point is a contradiction the probe could
have caught itself.

### N3. The mirror's `preflight.py` cannot see the split reaction set
**Status: PROVEN, tooling**

It auto-discovers a single `*_reactions.json` and the module has five
family files. Validation currently requires merging them by hand
first. If a multi-file version exists on the live install it needs
re-copying into the project.

---

## Known, not worth fixing

### K1. A corpse unforbidden mid job is swept onto the feed filter
**Status: KNOWN, do not re-investigate**

Unforbid a corpse while a retort is gathering containers and the job
takes it onto filter 0, which already holds its feed. It is NEVER
consumed and it is released when the job ends.

**Everything about our code is cleared, measured:**

| checked | result |
|---|---|
| feed filter quantity | `q1` on every run, nothing raised it |
| the stack rule | zero STACK lines, never fired |
| container filter specs | all 27 appended read `type=TOOL use=LIQUID_CONTAINER` |
| container routing | every jug on its own index, no corpse on a vessel filter |

**This entry is load bearing for R15.** It is the proof that
`#job.items` can exceed the number of satisfied filters, which is why
`collection_open` counts coverage rather than items.

### K3. Fireproof creatures burn as flesh
**Status: KNOWN AND ACCEPTED, deferred to the components system**

A dragon piece carries `unbutchered`, so R9's gate leaves it at FLESH
and it burns like meat. `CREATURE:DRAGON:SCALE` reads ignite 60001 and
heatdam 60001, DF's never sentinel, against 10508 and 10250 for every
ordinary tissue.

**This predates everything.** A whole dragon CORPSE has burned as FLESH
since the corpse branch was written. R9 neither introduced nor widened
it.

Every cheap fix was examined and none survives:

| option | why not |
|---|---|
| `fire_safe` reagent gate | DEAD. Proven in play: a dragon leg does not wake a `fire_safe: true` reaction, so `fire_safe: false` cannot exclude one |
| let INERT through, yield 0 | the piece burns and produces nothing, destroying it silently. Worse than today |
| copy the input back out | the components system with the serial numbers filed off, and a CORPSEPIECE product is probably not expressible |
| ghost forbids the piece | works, but forbidding is global: it would hide the scale from crafting and from the player with no explanation |

The framing that holds: the outer fireproof layer armours the
creature until it is processed, and processing removes the scales so
the burnable parts burn. That is the **non-burning components system**,
which is planned and not built. It needs to read what a reaction's
inputs are made of and return the parts that do not burn.

The set of fireproof creatures a fort actually butchers is close to
empty, so the cost of leaving this is small. Do not build a special
case for it.

### K2. Containers are shared first come between a job's own currencies
**Status: FIXED and verified in play**

Proportional allocation applied, plus a container margin:

| containers | allotted | bottled | result |
|---|---|---|---|
| 20 | 11 oil + 3 ammonia | 12 + 4 | BURNED |
| 50 | 34 oil + 10 ammonia | **35 + 11** | BURNED |
| a handful | none | 1 + 1 | BURNED, rest banked |

**The hauling throttle was removed.** Pipelining appends against
arrivals issued filters one a second. Issuing them together lets DF
dispatch haulers in parallel.

**A container margin was added.** `VESSEL_RESERVE = 4`. 48 free with 46
asked completed; 18 free with 20 asked was cancelled inside one second
announcing "Needs corpse". Not a filter count problem, 47 filters
worked and 21 did not. Erring low costs a package that waits in the
bank; over asking costs the whole burn.

---

## Retracted, and why

### X1. "Stack 0 is a malformation, stamp it to 1"
Shipped, then reverted. Stack 0 is not a malformation, it is how DF
marks a product that did not fire (R3). Stamping nulls to 1 turned
every unpaid liquid into real consumable fluid.

The lesson is recorded because the mistake is attractive: the sweep
made the symptom disappear, and "it works" was taken as proof of
correctness without asking why an item existed on a job that paid
zero.

### X2. "The stack 0 tar was a leftover from before the injector fix"
Wrong. A clean save with nothing ever produced still minted stack 0
liquids, because R3 mints them on every unpaid slot.

### X3. "Read the amount off `dimension` for dimensioned feeds"
Mine, 2026-09-08. Shipped and was wrong: a glob's dimension is its
per-unit size, not its amount, so the value already matched the
authored quantity and the guard silently did nothing. See R17.

The lesson is the same shape as X1. The change compiled, passed every
offline case I had thought to write, and produced no error in play. It
took a live run and a stack going `[9]` to `[8]` to disprove it. **The
offline harness can only test the model of the engine I already hold.**

---

### X4. "DF job item flags are positive requirements only"
Mine, 2026-09-08. I read `if flags.bone ~= nil then r.flags2.bone =
flags.bone end` and concluded a false flag writes a zero bit meaning
"no constraint", so `bone: false` on `RETORT_CORPSEPIECE` was
decorative and a `fire_safe` exclusion could never work.

Wrong, and the game in play showed it. `RETORT_CORPSEPIECE`
carries `bone: false`, shows white with bones available, collects, and
then DF cancels it: **"Needs 14 body parts"**. The stack was there and
the filter refused it. Negative flags exclude.

The lesson is not about flags. It is that I reasoned about engine
semantics from a field-write line while the person I was talking to
could simply look.

### X5. The FIRE_SAFE verdict from `isTemperatureSafe`
Mine, 2026-09-08, and void. The probe called
`item:isTemperatureSafe(n)` across four arities and reported `false`
for every material at every category, including one that cannot burn,
and printed NOT DISCRIMINATING as a verdict.

**The output contained its own refutation.** `isDamagedByHeat` returned
**true** for `CREATURE:DRAGON:SCALE`, whose heatdam point is the never
sentinel. That is an internal contradiction, so the method was being
called wrong, most likely raw integers where DFHack wants a
`temperature_type` enum, and it answered a question nobody asked
instead of erroring.

The probe should have refused to print a verdict off a column that
contradicts the raw data beside it. See N4.

The raw material data still discriminates cleanly and is not in doubt:
ignite and heatdam separate scale from all 14 ordinary tissues, while
melting point is 60001 for every one of them.

### X6. "Freed memory reads differently every time"
Mine, 2026-09-09. I diagnosed R19 correctly and then explained it
wrongly, saying the stale pointer read corrupted bytes and using that
to explain why the fault was intermittent. It does not. The address
holds a live reaction (L8), so the failure is deterministic for a
given allocation layout. The intermittency story was invented to cover
a gap and it survived a whole round before it was
questioned.

The lesson is narrow and worth having: a diagnosis and its explanation
are separate claims, and getting the first right does not license
guessing at the second.

### X7. "The drain key is consumed when the job starts"
Mine, 2026-09-09. Written into a comment in the shipped file. The log
had the refutation in it the whole time: the key is attached and
preserved for the entire run and goes at completion (L9). The fix
behaved correctly either way, which is exactly why it survived review
until the comment itself was read.

### X9. "Three coke reactions can never be satisfied"
Mine, 2026-09-09, and the worst call in this register.

Auditing R24 I swept every reagent `mat_id` against the vanilla
inorganic raws plus `making_fuel_materials.json`, then swept reagent
reaction classes against the same list, and found three reagents gated
on a `COKE` class that "nothing anywhere carries". I wrote that those
three reactions were dead and proposed changing them.

**They were correct and working.** The class is carried by the coke
material on `MAKING_FUEL_COAL_HOST`, in `making_fuel_plants.json`, a
file I never opened.

Reading one of two material files was careless. **Concluding that
working code was dead from a partial sweep, when three sibling
reactions used the same gate and had never once warned in any log, and
when I had already printed those siblings on screen, was not.** When a
check says working code is broken, the check is the suspect.

### X10. "A reagent gated on builtin coal can never be satisfied"
Mine, 2026-09-09, the same day, correcting my own correction.

Having found the coal watcher, I over-read it: I wrote that because no
builtin coal bar survives in the world, a reagent asking for one is
gated on something that can never exist.

**Wrong, and it misses half the system.** `making-fuel-fuel-access.lua`
widens any builtin-coal filter at job posting (L15). Writing a reagent
against builtin coal is a supported, intended pattern.

The real objection to a coal-typed coke reagent is the opposite of the
one I gave: it does not fail, it succeeds too broadly. The widener
dissolves it into the tier's fuel class, and on a `fuel: true` reaction
it becomes indistinguishable from the job's own fuel slot.

Both X9 and X10 are the same mistake twice in one day: reading one file
of a two-file mechanism and reasoning confidently from half of it.

### X11. "dead_dwarf means sapient remains"
Mine, 2026-09-09. I had three corpses and concluded from them that the
flag marked sapients, so it could not include pets and the feature was
dead. The fourth corpse, a pet sheep, carries it. See L16.

Three data points that all agreed still did not span the space. The
sheep was the row that mattered and I reasoned before it existed.

### X12. "The schema exposes 14 reagent flags against forty bits"
Mine, 2026-09-09, twice in two messages. The real numbers are 82 in the
engine and 82 accepted by preflight, in exact agreement, and 83 of 83
DF bits reachable.

The 14 came from a regex written `flags\.(\w+) ~= nil` with a single
space, and the file aligns those assignments with padding, so it
matched only the fourteen that happened to have one.

### X13. "No silent fallback to a wildcard is left in build_reagent"
Mine, 2026-09-09, said in the same message that fixed one of the two.
`metal_id` still was one. Asking whether these fields were already
accessible is what found it. See R29.

### X14. "mat_id has no module-half cross-check"
Mine, 2026-09-09, offered as the last loose end. It has had one all
along: `check_cross_references` validates every prefixed `mat_id` AND
`metal_id` against the module's own materials, which is exactly why the
sweep I ran to justify the work came back with zero violations. I read
the zero as "nothing broken yet" instead of "already guarded".

**These four share one root and it is worth naming once.** Every one
came from reasoning about a system from a partial reading of it: three
corpses instead of four, one regex instead of the file, one message's
fix instead of the function, one sweep instead of the validator that
made it come back clean. The measurement was always available and
cheap. See also X9 and X10, same day, same root.

### X8. "Clearing on the RAM transition covers it"
Mine, 2026-09-09. I proposed adding the R19 cache clear to the RAM
transition block in `poll()` alongside the `start()` clear, and
presented the two as equal coverage. `poll()` returns early while the
game is paused and the whole silent cycle completes inside the ESC
handler in about a second: there is exactly ONE `FUEL GHOST` line in
that window. The transition block is not reliably reached, and
`ghost_cache` survives on the strength of `start()` rather than that
block. The clear went into `start()` only.

### X15. "isCitizen answers on a corpse when asked with the second parameter"
Recorded in making-fuel-cremate-watcher.lua's header as measured, and the
premise of cremating citizens. Fell 2026-10-06: making-fuel-cremate-probe
read an exterminated citizen's unit as isCitizen false with the parameter
and without, isOwnGroup true, and the corpse lay on the pyre and was never
keyed. The API's own line says "non-dead". Whether the old reading held
under another DFHack, or for another kind of death, is not known. The
watcher now asks a dead unit is_dead_citizen (isOwnGroup, and none of the
flags isCitizen itself refuses), and cremation worked in play the same day.

The same root as X11: a claim about the dead, read off too few deaths.

## Vessel expansion is a MEGAFAUNA feature, not a fix

How many packages a whole bone stack earns in one job, against the
buffalo's own bone share of 0.454 by relsize:

| creature | packages | jugs |
|---|---|---|
| rat, cat, dog, dwarf | 0.02 to 0.28 | 1 |
| cow | 0.88 | 1 |
| water buffalo | 1.14 | 2 |
| elephant | 2.55 | 3 |
| dragon | 5.71 | 6 |

Everything up to a cow fits in one jug. So whole stack consumption
alone closes the bone problem for practically every creature a fort
processes, and multi vessel output only matters for elephants,
dragons, whales and dense plant stacks.

## Slot surgery: PROVEN VIABLE, NARROWER THAN FIRST WRITTEN

Two clean round trips on RETORT_WOOD, repeat, all four phases PASS:

| phase | result |
|---|---|
| 1 ADD | reagents 3 to 4, filters 3 to 4, both grew by one |
| 2 FILLED | peak attached 4 against a baseline of 3, extra jug collected |
| 3 REMOVE | reagents 4 to 3, filters 4 to 3, back to baseline |
| 4 RESTORED | ran another cycle at baseline shape and completed |

**Safe pattern, established here and not to be departed from:**
append at the END and erase only from the END, so no existing
`job_item_idx` or `reagent_index` shifts; and remove only while
`job.items` is empty AND the cycle has actually held items.

**NARROWED 2026-09-08.** This entry said "slots added mid collection
are honoured", and its own evidence line gives the limit of the claim:
*the baseline at add time was 1 item attached*. Both round trips were
run at one item attached. Nobody tested an append against a satisfied
item set. R15 is that test and it fails. The correct statement is that
slots added **while DF is still collecting** are honoured.

---

## Mirror sync state, 2026-09-09

Verified by direct scan, not assumed. Note that the project mirror
lags the live install by up to a round; anchors must be checked
against what is actually running, not against the mirror alone.

**This bit twice on 2026-09-09.** Once the mirror was missing
`making_fuel_reactions_retort.json` and `making_fuel_materials.json`
entirely, and once it lacked a round that had already been applied
and tested. Both times the anchors had to be validated against the
reconstructed live file rather than the mirror. Check the mirror
against the last delivery before writing a pair, every time.

| 2026-09-09 additions | |
|---|---|
| reaction count | **430** across five files, was 428 |
| adoption of runtime clones | APPLIED and verified, R18 |
| `base_cache` and `drain_mat_cache` self validation | APPLIED and verified, R19 |
| `slot_preserved` fails safe | APPLIED and verified, R20 |
| INERT refusal once per job | APPLIED and verified, R21 |
| shrink never passes an occupied filter | APPLIED and verified, R21 |
| `reconcile_reagents` | APPLIED and verified, R22. **Live but NOT in the mirror**, see below |
| drain key stutter | APPLIED and verified, R23 |
| per retort drain, whole feature | APPLIED and verified |
| crumb trail | SILENCED, `CRUMBS_ON = false`, 14 call sites kept. **Live but NOT in the mirror** |

**The mirror is one round behind as of this entry, and the LOG is the
better witness.** `reconcile_reagents` and `CRUMBS_ON` are absent from
the mirror copy of `making-fuel-ghost.lua`, and both are provably
running: the 457 line log contains `Rebuilt 2 vessel slot(s)` and zero
`CRUMB` lines. When the two disagree, believe the log. It records what
executed; the mirror records what was last copied.
| TOOL feed `tool_id` | rechecked: 44 gated, 0 bare. V3 stands |

| | |
|---|---|
| retort feed quantities | all balance pass edits present |
| orphan liquid slots | zero remaining, R8 fixed |
| `FLUID_CLASS.FLESH` / `.PEAT` | `3 / 4` and `1.000`, applied |
| whole stack consumption, fix 2 | APPLIED and verified |
| null reaper | APPLIED and verified |
| `live_jobs` | written every poll, R13 fixed |
| cycle boundary | settles on the empty item set, R12 fixed |
| proportional allocation, `VESSEL_RESERVE` | APPLIED, K2 fixed |
| vessel expansion, multi package payout | APPLIED and verified, V4 |
| `collection_open` gate | APPLIED and verified, R15 |
| dimensioned feed handling | APPLIED and verified, R17 |
| fat classifier ordering | APPLIED and verified, R16 |
| `RETORT_GLOB` shape | APPLIED and verified, R7 |
| slot and class disagreement announcement | APPLIED, silent as expected, L3 |
| butchered piece classification | APPLIED and verified, R9 |
| nonzero product counts in the retort file | none, and WASH_TAR_SAND in processing which is correct |
| preflight across all five reaction files | PASSED, 50 materials, 428 reactions, 36 known warnings |

---

## R8. Orphan TAR_PLANT liquid slots
**Status: FIXED, verified**

A scan of the live retort JSON finds zero LIQUID_MISC_INORGANIC
products without a `to_container`. Both stray slots are gone.

RETORT_STRAW_DRIED and RETORT_PEAT each carried a TAR_PLANT product
with no `to_container` and no `dimension`. On PEAT the slot could
never be paid at all, since the PEAT split funds TAR_PEAT,
VINEGAR_PLANT and AMMONIA.

---

## Mirror sync, and a delivery rule learned the hard way

**The mirror lagged on EVERY round of 2026-09-09.** Not once was it
current. Anchors must be checked against the reconstructed live file,
which means applying the previously delivered pairs to the mirror and
verifying the result parses before cutting the next set. Twice a pair
set had to be rebased after its predecessor had already been applied.

**LINE ENDINGS. Whole file deliveries destroyed them.** The project is
mixed: `making_fuel_reactions_*.json`, `making_fuel_tools.json` and
`making-fuel-bank-readout.lua` are CRLF, while `making_fuel_materials
.json`, `making-fuel-ghost.lua`, `making-fuel-tuning.lua` and
`making-fuel-rot-watcher.lua` are LF. Python reads text with universal
newlines, which strips `\r`, and writing back without it rewrote every
line in the file. The diff then showed 9816 changed lines for a one
reaction addition.

Three rules from that, and they are not optional:

1. **Pairs by default.** A whole file only when the change is genuinely
   too large to apply by hand, and then with an audit table.
2. **Read and write in binary**, or with `newline=''`, so endings
   survive.
3. **Anchors stay small.** A 40 line FIND to append one reaction is a
   failure of anchor choice, not a necessity. `RETORT_ROT` went in on a
   4 line anchor once it was noticed that its sibling was the last
   reaction in the file.

---

## Observed 2026-09-09, not yet investigated

Four things visible in a clean log. None blocks, none is understood,
and all four were seen rather than inferred.

| item | evidence | note |
|---|---|---|
| ~~Building grants differ across a data cycle~~ | | **CLOSED 2026-09-09, NOT A DEFECT.** See below |
| ~~Ungated reagents every boot~~ | | **Promoted to R24 and FIXED.** Five reagents, and the diagnosis went badly wrong first. See X9 |
| **Rebuilt vessel slots mint a null** | 2 of the 4 `REAPED unpaid AMMONIA` lines came from R22's rebuilt slots | The rebuilt slot clones an ammonia bound product and pays 0, so DF mints a stack 0 null and the reaper clears it. Benign per R3, but a jug transiently receives one. Avoidable by binding rebuilt slots to nothing |
| **Bark dye push reports a bug that may not be one** | `Bark Dye push wrote NOTHING with 22 dye trees present. That is a bug, report it.` after a cycle | Almost certainly the twins persisting on vanilla plants, which no sweep reaches, so the second push is correctly a no-op. The message is wrong, not the code |

### Building grants, 6 then 0: NOT A DEFECT
**Closed 2026-09-09 by reading the function I had flagged three times.**

`bld_injected` counts only NEW grants. The loop builds a `have` set
from each entity's existing `permitted_building_id` and skips anything
already there. Building permissions deliberately have no clear pass,
and the evaluator says why in its own comment: they hold building def
IDS rather than vector positions, injected ids are pinned per code by
the reservation ledger, and `entity_raw` is rebuilt from the raws on
load in any case.

Boot: no civ has the retort, 6 civs times 1 building is 6. After a
cycle: all 6 still have it, nothing to grant, 0 is correct.

Checked rather than taken: `BUILDING INJECT: [MAKING_FUEL_RETORT]
injected as id 2 (FURNACE)` on **both** cycles, so a persisting grant
re-resolves to the same building.

Same shape one line above: `0 slot(s) erased` on boot, `1` after. The
first pass has nothing to erase, DF creates the wsgi slot during play,
the second erases it. Idempotent.

**I flagged this three times across three sessions on two numbers
differing, without opening the function that prints them.** A
difference is not a defect until the code that produced it has been
read.

---

Also standing, and unchanged: the concrete module's
`PRODUCT mat_id [WATER] did not resolve; product ships as builtin
fallback. This is the magma bug.`, and GLUE graphics still carrying
`TODO_COL/TODO_ROW` placeholders.

---

## Next, in order

1. **CREMATE.** A reagent CANNOT target citizens: `dead_dwarf` and
   `ANY_DEAD_DWARF` both carry sapient invaders, and nothing on the
   ITEM separates a citizen from a goblin (L16, L17). A watcher can,
   exactly, and `isCitizen(unit, true)` is measured working on a
   corpse. Two reactions rather than one is free at that point, since
   `isPet` reads off the same unit. The rule stands: if it cannot
   target citizens specifically, it does not ship, and the reagent
   route is closed.
2. **Wood vinegar cannot reach four of its six consumers.** It carries
   `VINEGAR_WOOD, ACID` and is missing `VINEGAR`, so 60 reactions worth
   of output cannot feed `DISTIL_METHANOL`, `MAKE_VERDIGRIS` or
   `MAKE_IRON_BLACK`. Methanol is the one that stings: wood vinegar IS
   pyroligneous acid and distilling it is where methanol came from.
   One line fixes it. **The vinegar COLLAPSE is declined**, a design call.
3. **R11, the coke family.** Unchanged, and the inorganic push is the
   next big step after the retort.
4. **B1**, the tar and vinegar ratio, which needs rereading now that
   four of the five consumers it counted were unreachable from the
   dominant source.

## Coal pitch, scoped and deferred

Chemistry, so it is not re-argued: coal tar and bitumen have different
parents. Coal tar comes off coal during coking and distils to creosote
and **coal tar pitch**, a real product. Bitumen is the heavy residue of
crude oil and occurs in tar sands. Coal tar pitch BINDS and COKES;
wood pitch waterproofs and makes varnish; bitumen does roads.

The module already encodes most of this correctly. `DISTIL_TAR` gives
turpentine, creosote and pitch. `DISTIL_TAR_COAL` gives benzol,
naphthalene and anthracene. `MAKE_ANILINE` reducing benzol with acid
and iron is the Bechamp reduction, which is how the dye industry
started, out of coal tar.

The tell is `COKE_PITCH`, named "make coke from coal pitch" and fed
`BITUMEN`. And the four briquette reactions bind with wood `PITCH`
when coal tar pitch is the historical briquette and electrode binder.
So the USES are right and two of the materials are swapped.

Deferred because step five of the fix edits `inorganic_making_fuel
.txt`, a WORLDGEN raw, to remove `[REACTION_CLASS:PITCH]` from
`BITUMEN` so it stops standing in for pitch. That is a different
deployment story from injected JSON and belongs with the inorganic
push.

**Barrels are withdrawn, not deferred.** The probe was run and the
answer removed the need: a barrel has no itemdef and its volume
excludes its contents, and once `write_liquid` filled every vessel to
its own capacity a jug turned out to hold 16 packages rather than the
6.7 the old arithmetic claimed. See L11. Reopen only if hauling
becomes the complaint again.

## The per retort drain, built 2026-09-09

Not a defect. Recorded because the design took several wrong turns
that should not be walked again.

**What it is.** `RETORT_DRAIN` pours a furnace's banked liquid into
vessels without a burn. Banks are per furnace, so the reaction has to
be per furnace too. For each standing retort, three transient things,
all minted on demand and all swept by prefix:

| | id | carries |
|---|---|---|
| material | `MAKING_FUEL_DRAIN_KEY_B<id>` | classes `DRAIN_KEY` and `DRAIN_B<id>` |
| reaction | `MAKING_FUEL_RXN_RETORT_DRAIN_B<id>` | key reagent gated on `DRAIN_B<id>` |
| key | a `DRAIN_KEY` tool of that material | minted inside the retort when its banks hold a package |

Fort mode true at mint and never touched again. Visibility is the
`building` field only (L10): the open retort's clone gets the furnace,
every other clone gets nothing. The key decides red or white.

**`nearby: true` was tried and MEASURED TO FAIL.** One key, minted
once, genuinely inside retort 5, no floor fallback line, and the
adjacent retort still read the drain as available. Position is not
tight enough. Do not put it back.

**The key is consumed rather than preserved,** because a reaction with
nothing consumed leaves an empty ledger and the cycle can never be
recognised as having fired, which would pay liquid out and never debit
the bank.

**Keyed on building id, not a count**, so a key minted for retort 7
cannot drift onto another furnace when a different retort is
demolished.

**Wrong turns, recorded so they are not repeated.** A fixed material
pool with a ceiling, then headroom to patch a gap the pool created,
both invented to work around an assumption that materials could only
be injected at boot. They are injected several times an hour; the
whole pipeline tears down and rebuilds on every ESC press and every
save. And `fortress_mode` was reached for twice as a visibility lever
after the building field had already been named as the one.

**What it does not do.** A drain fills one jug per run and banks the
rest: `collection_open` refuses to append once every base filter is
covered, and a drain fills all of its filters the moment they arrive.
19.5 units took two drains. That sidesteps R15 rather than fighting
it, and it is the current ceiling.

---

## Offered, not built

- **A log line for unbutchered INERT pieces.** One `log_once` when an
  unbutchered piece classifies INERT, no yield effect at all. It would
  build the list of fireproof materials K3's components system needs,
  for free, out of ordinary play. Currently the fallback only speaks
  for butchered pieces, so dragons are silent.
- **A throwaway `fire_safe` test reaction**, to settle which field DF
  reads. Not needed for anything: K3 is deferred and the gate is
  already known not to select a dragon leg. Recorded only so the
  question is not re-opened from scratch.
