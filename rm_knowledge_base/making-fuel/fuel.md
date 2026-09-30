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
