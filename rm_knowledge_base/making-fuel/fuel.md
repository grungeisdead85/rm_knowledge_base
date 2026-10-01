# Making Fuel findings

## A reaction cloned at runtime must be adopted by the ghost engine, through the live handle

- **Status:** measured (2026-09-29, 2026-09-30)
- The engine only knows reactions a module declared. A clone (the drain key's per-retort drains, the tank's per-building fill, install and atomise clones) is invisible to it until the maker calls `register_alias(clone, base)`, re-asserted every poll. An unadopted drain mints liquid nobody paid for, which the vessels' reaper pulls back out (`REAPED unpaid ... jug freed`), so fills look broken.
- The makers must read `_G.refinish_adaptive_api` at each call (dfhack/scripts.md): with the handle held from file load, adoption failed all session; reading it fresh fixed both drains and fills in play (`Adopted runtime clone MAKING_FUEL_RXN_RETORT_DRAIN_B10`).

## Fills gather in batches, holding two vessels in reserve

- **Status:** measured (2026-09-29 kiln, 2026-09-30 smelter)
- A fill job opens extra vessel slots only while free fuel vessels exceed those open at other fills plus a reserve of two (`FILL_RESERVE`), up to the fill limit. With 9, 6 and 4 free it opened 2 slots and took 32 and 17 units from 2 jugs; with 3 free it took one. Since 2026-09-30 a fill held to one vessel says why: `one vessel only; N free fuel vessel(s), M open at other fills, 2 kept in reserve`.

## Any clay is a binder source, modded ones included

- **Status:** measured (2026-09-30)
- A binder source is any inorganic with a `FIRED_MAT` reaction product, which every clay has. Seven clays from other people's mods failed their twins only because the twin copied its colour by reading state_color as a colour index (df/colours.md). Through the pattern, all seven twins exist, and a modded clay makes binder.

## The fuel a walk found is tested first

- **Status:** code and measured (2026-09-30, 2026-10-01; region4)
- **Before:** the honest menu scan walked IN_PLAY (24,000 items) every 200 polls and whenever the building in view changed. count_bulk walked it again for each job expanding its fuel. Together: 2.71 ms/sec.
- **Now:** the items a walk found are kept (`found_fuel`, by class and item type, as ids) and tested first, with `usable_fuel` itself. A kept item that passes is one the walk would accept. The walk runs only when the kept items no longer answer, and its finds replace the list.
- **Measured after:** the scan costs 0.007 ms a call; in an 818 s run it walked once. The list is emptied every session (`start()`).

## A fuel slot already reclassed is decided for the session

- **Status:** code and measured (2026-10-01, 187 s)
- **Before:** 16,135 of 29,043 `widen_job` calls ended at one line, five jobs a poll at 54 µs each: 97% of its cost. Each was a job holding a fuel slot that `expand_fuel` had already reclassed (FUEL_BULK, or FUEL_SMELTING as its fallback), asked the whole question again every poll. No later poll can give such a slot back the shape that was matched.
- **Now:** the job is marked decided and its slot left as it is. `widen_job` went from 5.0 to 0.2 ms/sec (SHAPED BEFORE, DECIDED NOW).

## The ghost engine reads a job's held items once a poll

- **Status:** code and measured (2026-10-01; region4, about 5.3 ghosted jobs a poll)
- **The records:** `handle_ghosted` runs every poll for every ghosted job. Two records keyed by job id spare its work when nothing has moved:
  - `valued` (THE HELD ITEMS, PRICED ONCE) keeps the valuation's results;
  - `steady` (THE SAME ITEMS AS THE LAST POLL) skips the stack rule, the identity tables and the item descriptions.
- **The identity they key on** is each held item's id, stack, material, slot and dimension, built once a poll (ONE IDENTITY A POLL). Its dimension is read without a throw (A DIMENSION, READ WITHOUT A THROW; dfhack/scripts.md).
- **What is left out:**
  - profiles that carry tars, from both records: their feedstock is inside the jugs;
  - drains, from the same-items record: their witness is what the vessels hold.
- **Housekeeping:** both records are emptied by `reset_engine` and pruned by `audit_sweep`.
- **Why skipping is safe:** the stack rule is the only writer of a ghost reagent's quantity, and it writes only when the count differs, so skipping it on unchanged items skips nothing.
- **Measured** (rm/performance.md):
  - valuation: 91 µs a call, 4.71 ms/sec (612 s), down to 2 µs on unchanged items (443.7 s);
  - `handle_ghosted`: about 210 µs a job a poll (437 s), down to about 160 (443.7 s);
  - the whole engine: 1.40 ms a poll, down to 1.18.
