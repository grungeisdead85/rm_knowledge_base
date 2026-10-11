# RM Stacked Tools

How DF fills a reaction slot from stacked tool items and what it takes away,
measured in play on 2026-10-03 with `refinish-stack-probe.lua`, what a fuel slot
does with stacks, measured on 2026-10-04 with `refinish-fuel-stack-probe.lua`,
and the rules RM's byproducts and their consumers follow from them.

Related records: `RM_Hide_Wing_Lessons.md` (a tool item can carry a stack; only
one job can hold an item; DF consumes by the reagent quantity) and
`making-fuel-binder-watcher.lua` (binder made in stacks; a press took 1 binder
off a stack of 10 and left 9).

---

## 1. The test

The probe armed RM's finishing reactions in RAM (the dust slot's quantity, and
a second dust slot for E and F), laid stacks of RM's dust tool on the ground,
and followed every test job and every stack every 5 frames. Each scenario used
a stone of its own, so no job could reach another scenario's dust. Base metal
steel, jobs queued at a forge.

| | Laid | The reaction asked for | What happened |
|---|---|---|---|
| A | stacks 3 + 2 | one slot, 5 | Both stacks went into the one slot, whole, and the job used all 5. |
| B | stack 12 | one slot, 5 | The job held the whole stack, carried it to the forge, and DF drew 5 at completion: the same item was left holding 7. No split, no new item. |
| C | stack 3 | one slot, 5 | The reaction read red in the task menu, "requires limestone dust", and could not be queued. |
| D | stacks 4 + 4 | one slot, 5 | Both stacks went into the slot whole; at completion one was used up and the other drawn down to 3. |
| E | stack 2 | two slots, 1 each | The stack went into the first slot, the second slot found nothing, and the job ended without completing. |
| F | stack 1 | two slots, 1 each | As E: the job ended without completing. |

---

## 2. What it means

- **One slot fills from any number of stacks** (A, D), and DF takes exactly the
  reagent quantity at completion (B, D). Stacks merging at intake is what lets
  a consumer ask for any quantity.
- **A job holds whole stacks** (B, D), never a split piece. A stack therefore
  serves one job at a time, since only one job can hold an item.
- **Availability counts units** (C). A reaction asking for more than the fort
  holds reads red and cannot be queued, as for any missing item.
- **One item fills one slot** (E). Two slots of the same tool and material each
  need items of their own: one stack cannot be shared between them, and a
  single unit cannot fill two (F). The glob wing's partial slot bug (one glob
  filling two slots, `RM_Hide_Wing_Lessons.md`, section 2) does not happen with
  stacked tools.

---

## 3. Rules that follow

For a consumer:
- Ask for the whole quantity in one slot.
- Never write two slots of the same tool and material into one reaction.

For a producer:
- Byproducts, and anything a job makes in bulk, come out as stacks: one per
  form, material and job, never one item per unit.
- A large output is split into a few stacks, so several jobs can draw from it
  at once (binder: four stacks of ten per boulder).

---

## 4. Decided

- 2026-10-03: stacks are the standard way RM manages byproduct output and
  intake. Sawdust, gravel and the like are produced in stacks, not as
  individual items.

---

## 5. In force

Since the delivery of 2026-10-03:

- `refinish-job-byproducts.lua` pays every byproduct as one stack per form,
  material and job (`make`): dust, gravel, sawdust, bark, scrap, cullet
  and heaps, RM's streams and every module's (the waste form went on
  2026-10-07; crust has had no tool since 2026-10-06).
- `refinish-reaction-adaptive.lua` prices a slot's stacks together: the
  quantity a cycle takes is spread over every unit the slot holds. Priced one
  stack at a time, stacks of 3 and 2 in a slot asking for 4 were each valued
  whole, 5 units for 4 used.
- `making-concrete-mix-watcher.lua` judges a mix once every slot holds what it
  asks for, counting stack units, where it used to wait for six items.
- `refinish-reaction-outputs.lua` merges a reaction's new items of a stacked
  tool per material, one stack each: crushing a boulder gives its gravel as
  one stack of 12. RM's forms declare `stack = true` in
  `refinish-core-payload.lua`. RM's grinders are left out until the dust unit.

- The dust unit is 200 for every class (100 from 2026-10-03, 200 since
  2026-10-07): the dust tool's size,
  which the byproduct service divides each loss by. RM's grinders and the
  crushers' dust are measured stacks (`refinish-reaction-outputs.lua`,
  MEASURED STACKS): sized from what their source measured, in that unit, with
  DF's count as the number of stacks. A boulder grinds into 50 dust in four
  stacks, three rough gems into 3 (the three quarters banked), a bar into 3,
  and a crushed boulder leaves 14 dust beside its twelve gravel. What falls below one
  unit is banked per building, tool and material (REFINISH_OUTPUTS), so no
  material pays for another.
- 2026-10-04: RM's glue granules (REFINISH_GLUE_GRANULES, 25 a unit) stack, so
  a recipe takes one granule off a stack. The brick service counts a
  reaction's grog by what the reaction asks, never by what the job holds,
  since a slot holds whole stacks (`refinish-bricks.lua`).

---

## 6. Mixed inputs

A product that takes its material from a reagent (GET_MATERIAL_SAME, or the
reagent material's own product) gets the material of the first item DF
collected for that reagent: two branches of different trees split into
kindling all of the first tree. One slot fills from any number of stacks, so
a slot can hold several materials, and the rest vanished into the first.

`refinish-reaction-outputs.lua` measures, while the job runs, the volume of
each material held for such a reagent. At completion, if there was more than
one, it shares the job's new items of that product out over those materials
by volume: largest remainder, so every item lands on one, and a lone item
goes to the largest share (ties to the first collected). Each takes the
material the product gives an input of that material. A product of a fixed
material (concrete, a finish, a coal) is untouched, since nothing in it was
read off an input.

It acts on JOB_COMPLETED, which DFHack runs before any ITEM_CREATED of the
same tick (read from DFHack's EventManager.cpp: event types are walked in
enum order, JOB_COMPLETED 3, ITEM_CREATED 6), so whatever acts on a new item
(the fuel wood hop, the gravel hop, the finish minter) sees the final
materials. An output something else changed first is left alone and logged.
Seen in play later on 2026-10-03: branches split by tree type, gravel merged,
and the crushers' dust sized by measure.

---

## 7. Fuel slots

Measured 2026-10-04 with `refinish-fuel-stack-probe.lua`, on Making Fuel's
kindling, wanting to know whether fuels could stack:

- A fuel slot asking for 1, fed a stack of 10, held the whole stack and
  destroyed all 10.
- A fuel slot asking for 4 held a stack of 10 and destroyed all 10. Fed
  stacks of 2 and 3 instead, it gathered both into the one slot and destroyed
  both.
- On the bulk surcharge's four slots of one, each slot took a whole stack, and
  every stack was destroyed.

So a fuel slot collects by quantity, as a reagent slot does, and then burns
every item it holds whole, unlike a reagent slot, which DF draws its quantity
from. Making Fuel's note that DF pays no attention to a fuel slot's quantity
was measured with single items (`making-fuel-access.lua`).

Decided the same day: every current fuel should stack, and paying fuel from
stacks would collect the stacks a job needs, burn them, count what was there
and hand back the total less the cost. Shelved, as not worth it yet; fuels
stay unstacked and the four-slot surcharge stands. The fuel probe is a
development probe, not shipped.

---

## 8. Running the probe again

`refinish-stack-probe.lua` in the scripts folder. Hover the mouse over open
floor near a forge and run `refinish-stack-probe`; it picks the base metal with
the most free bars and six stones with no dust in the fort, lays the stacks,
mints and arms their finishing reactions, and prints the six reactions to queue
as plain jobs (18 bars of the base metal, and fuel). Running it again prints the
report; `refinish-stack-probe off` reports, cancels any open test job and
disarms. Traces are DETAIL and verdicts INFO, under REFINISH_METAL STACK_PROBE.
A development probe, not shipped with RM.
