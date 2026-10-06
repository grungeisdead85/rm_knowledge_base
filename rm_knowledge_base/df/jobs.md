# Jobs, their slots, and what reaches a workshop's menu

What DF does with a job's item slots and its fuel, how a job names the tools it wants, and what decides whether a reaction is offered in a workshop's task menu.

## A reagent slot fills from any number of stacks and draws exactly its quantity

- **Status:** measured (2026-10-03, refinish-stack-probe)
- A reaction's reagent slot asking for N units of a stacked tool takes whole stacks until it holds at least N. At completion DF draws exactly N, and the stack it held keeps the rest: a job holding a stack of 12 for a reagent asking 5 left the same item holding 7, released in the workshop.
- Two slots of the same tool and material need items of their own: one stack cannot fill both.
- **Evidence:** RM_Stacked_Tools.md.
- **Depends on it:** every recipe that takes stacked dust, gravel, binder or glue. The brick service counts a reaction's grog by what the reaction asks, never by what the job holds (refinish-bricks.lua).

## A fuel slot collects by quantity, then burns every item it holds whole

- **Status:** measured (2026-10-04, refinish-fuel-stack-probe)
- A fuel slot asking for 1, fed a stack of 10 kindling, held the whole stack and destroyed all 10.
- A fuel slot asking for 4 held a stack of 10 and destroyed all 10. Fed stacks of 2 and 3 instead, it gathered both into the one slot (5 units) and destroyed both.
- On the bulk surcharge's four slots of one, each slot took a whole stack, and every stack was destroyed.
- So with stacks, DF honours a fuel slot's quantity when it collects and ignores it when it burns. The fuel access layer's note that DF pays no attention to a fuel slot's quantity was measured with single items (making-fuel-access.lua, THE BULK SURCHARGE).
- **Evidence:** the probe's REPORT lines (FUEL_PROBE), for instance a job that "held 2 item(s). Destroyed: #54322 x1, #54194 x10", and the run whose slot 1 held #54293 x3 and #54292 x2.
- **Depends on it:** fuel stacking, decided and shelved (making-fuel/fuel.md).

## A job holds an item from the moment it is claimed, and gathers its items one at a time

- **Status:** code (making-fuel-access.lua) and measured (2026-10-04)
- A job's item list holds a reference from the moment an item is claimed, before it arrives, and a job that needs several stacks has them brought one at a time, so what it holds changes while it waits.
- **Evidence:** a byproduct memo taken once, at the first item, measured a gold table, three bars, as "ConstructTable: gold bars went in at 600".
- **Depends on it:** the byproduct service retakes its memo whenever a job holds a different number of items (refinish-job-byproducts.lua, THE MEMO FOLLOWS THE JOB).

## A job names a tool by number; an item points at the tool itself

- **Status:** measured (2026-10-04) and code
- An item points at its tool's definition, which RM's tool wash carries across saves (refinish-tool-wash.lua). A job's item slot, a job that makes a tool, a work order and an order's item conditions hold the tool's subtype NUMBER, and nothing carried it until 2026-10-04.
- RM's and the modules' tools are numbered in the order they are injected, so a tool added ahead of others moves every one after it, and a saved job then asks for whichever tool took its number.
- **Evidence:** RM's glue granules were injected between cullet and gravel (TOOL_INJECT lines, 2026-10-04). Two saved branch jobs, 17845 at a retort and 2352 at a charcoal reaction, then fetched clay binders and were stopped by the adaptive engine's INERT check, which blamed a missing material gate that the reagent did not lack.
- **Depends on it:** the ledger's tool record (rm/save-system.md).

## A reaction whose category does not exist is in no menu

- **Status:** measured (2026-10-04)
- A reaction names its category by id, and DF files it under the category of that id, or under none.
- **Evidence:** a mod replaced vanilla's dye reactions under categories of its own ("Concentrate dye" among them), so no MAKE_DYE category existed, and every module dye that named it, Making Fuel's and RM's, was gone from the dyer.
- **Depends on it:** RM's own Make dye (rm/dust.md).

## A module reaction permitted after startup did not reach the dyer's menu

- **Status:** measured (2026-10-04); the cause is not known
- Mineral dye reactions injected with no permits, then permitted to every civilisation in play, were in the civilisation's permitted list and still offered in no menu. Module dyes permitted at load, in the same category, were offered. Permitted at load instead, all 152 mineral dyes were offered.
- **Evidence:** a console read of the civilisation's permitted reactions listed nine mineral dye codes while the dyer showed none; the next load, with the dyes permitted at load, listed all of them.
- **Open:** what DF builds the menu from. A read of the built menu (game.main_interface.building) with one reaction permitted after startup next to one permitted at load would settle it. The finishing reactions RM permits in play were not part of this comparison.
- **Depends on it:** the mineral dyes are permitted at load (rm/dust.md).

## A table is 3000 in volume, whatever it is made of

- **Status:** measured (2026-10-04)
- A gold table and a wooden table both measure 3000: an item's volume is set by its type, not by what went into it. A metal table takes three bars, 1800, and a log is 5000.
- **Evidence:** the melt line for a gold table, "holds 1800 of the 1800 it cost, volume 3000"; both tables read 3000 in play.
- **Depends on it:** a melt credits the smaller of an item's cost and its volume (rm/melting.md).

## A builtin coal reagent is held against a bar's dimension, and a red row names its last unmet reagent

- **Status:** measured (2026-10-05, making-fuel-objection-probe, two runs at a smelter)
- With Making Fuel's menu key at one bar (dimension 150) and 16 free module coal bars in the fort, every steelmaking row asking 300 or more read "Requires Refined coal", and the rows asking 150 did not. With the key's dimension set to 2400, the fort's free coal, those rows no longer named coal on the next press. A reagent's quantity is held against the bar's dimension, not counted in bars.
- A red row names one reagent: the last one, in reagent order, that the fort cannot meet. With coal met, "make steel bars (5)" named "Cast iron bars".
- **Depends on it:** making-fuel-access.lua sizes the menu key to the fort's free coal (making-fuel/fuel.md).
