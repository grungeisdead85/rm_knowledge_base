# Finishes, minted once the fort can make them

How RM loads its finished metals since 2026-10-02: not every finish it could make, only those a fort can. The forge's folders are in rm/forge-menu.md.

## Every finish at load made DF's own lists unusable

- **Status:** measured (2026-10-02)
- Until then every finish in the blueprint was injected at load: 61,392 materials and 99,574 reactions with all 81 base metals selected. DF builds several lists over every metal it knows, and they grew with the finishes (df/menus.md):
  - New work order: 4,922,677 templates, 13 to 16 seconds to open, and with every base on it locked DF up;
  - the material picker: all 62,606 inorganics, about 5 seconds;
  - the forge's item categories: 61,442 rows each.

## A pair of base metal and dust is minted once the fort has had both

- **Status:** decided (2026-10-02), measured in play
- A finish is made from bars of its base metal and one dust, in a reaction that names that dust. A tool reagent gets no magnifying glass, so the dust cannot be picked in the job, which is why there is one reaction per base metal and dust. So a pair is minted once the fort has had both the base metal's bars and the dust, and what is loaded grows with what the fort works, not with what RM could make.
- refinish-scan still builds the whole blueprint every data cycle, as the catalog every mint reads from.
- **In play (2026-10-02 and 10-03):** built and tested with every base on. The magnifying glasses opened promptly, the forge menus were fine, and RM's finishes appeared in the stockpile options and were hauled to their piles (amber steel bars to an amber steel bar pile).
- **Not yet measured:** how long New work order takes to open under the just-in-time finishes.

## The roster keeps the order, because an item stores a number

- **Status:** code (refinish-mint-finish.lua, THE ROSTER)
- An item stores a material number, and RM's materials are not in the save, so every load has to put them back where they were. The roster (site data, REFINISH_STEEL_FINISH_ROSTER) holds one line per event, in order, never removed: S B for a base metal's first bars, S D for a dust's first appearance, M for a finish minted.
- Step 4 mints the M lines in roster order, and every mint since was appended to both the array and the roster, so the replay rebuilds the session's layout and the ledger's fingerprint finds nothing to move. When it cannot, because another script appended a material between two mints, the ledger moves objects by name, as it does for everything else.
- A line the blueprint cannot make this cycle (its base not selected, Material Finishes off) is skipped, never dropped: the ledger parks the objects that wear it, and they get it back when it is minted again.

## Reactions are rebuilt each load from what the fort has had

- **Status:** code
- Reactions are not in the roster. Step 5 builds every pair the S lines allow, grouped by category and sorted as the full set always was, so a finishing menu reads the same. A pair minted in play is appended instead, and the repoint at the end of refinish-index-reaction.lua points saved jobs back at their reactions on the next load.

## A bar or dust is noticed the moment it exists

- **Status:** code, sources measured (2026-10-01)
- refinish-mint-finish-watch.lua mints in play. `eventful.onItemCreated` sees a grinder's dust, RM's byproduct dust and a smelter's bars the frame they exist, and skips trader, migrant and invader goods. A poll reads what was made since the last one off the end of `world.items.all` (dfhack/scripts.md), which catches what the event skips. A bar still a caravan's is waited on until it is bought or leaves.
- No walk of every bar: one walk of 60,000 bars every poll cost 9.3 ms a second (the coal watcher, 2026-10-01). What both miss is read at the next load, when Step 6.7 walks every bar and dust.

## A folder never opens empty

- **Status:** code and measured (2026-10-02)
- DF builds a folder's rows from the reactions filed under it, and an empty folder kills the task panel (df/menus.md). Each kind folder in the forge (colour-based, material-based) gets one placeholder reaction at the metalsmith's forge and the magma forge once a finish of that kind exists, which opens the base folder and refinished metals above it as well. refinish-menu-forge.lua replaces the row with the kind's finishes; without it, the row reads red and cannot be done.
- The manager's New work order list has the placeholders taken out.

## Every base metal is on by default, and Protect Bases is off

- **Status:** decided (2026-10-03), code
- With finishes minted just in time, a fort with nothing saved has every base metal with a refinishing path selected (refinish-bases.lua, THE DEFAULT SELECTION); it was steel alone. Protect Bases defaults to off, because protecting the bases prevents grinding metal entirely.
