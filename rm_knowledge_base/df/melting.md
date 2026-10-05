# Melting in DF

How DF credits a melted object, where it keeps what is under a whole bar, and what an item costs to forge, which is what a melt is measured against. RM's handling is in rm/melting.md.

## A furnace keeps part bars per metal, in tenths of a bar

- **Status:** measured (2026-10-03 and 2026-10-04)
- `building_furnacest.melt_remainder` holds one entry per inorganic. A melt adds its credit to the metal's entry, and when an entry reaches 10, DF makes a bar of that metal and keeps the rest. DF shows the store nowhere.
- **Evidence:** a test smelter read 9 for amber steel, nine tenths of a bar. RM's melt service then checked DF's credit, bars made plus the store's gain, against this unit on every melt of an RM form, fourteen in all, and on every one it agreed.
- **Sizing:** DFHack's own furnace constructor sizes the store to the inorganics array (library/modules/Buildings.cpp). That a furnace DF builds in play is sized the same way, at the moment it is built, is an inference that every store read since agrees with. Every vector read after RM's finishes were minted just in time was longer than the array (seven were cut at one load, 2026-10-04).
- **Depends on it:** refinish-melt.lua, refinish-ledger.lua (fit_stores), refinish-bank-readout.lua.

## DF credits 3 tenths of a bar per point of material size

- **Status:** measured for RM's forms; the DF wiki for vanilla items
- Every RM form has material size 1, and DF credited exactly 3 tenths per unit on every melt measured. For other items the DF wiki's melt table (Melt item, v53.16) gives 0.3 bars per point of material size, or 1 bar for most furniture; a melted gold table returned exactly 1 bar in play.
- Many items return more than they cost to make: leggings, giant axe blades and two-handed swords 150%; shields, picks and battle axes 120%; a single bolt 250%; a single coin 5000%; a stack of 500 coins 110%.
- **Depends on it:** RM's measure replaces DF's credit (rm/melting.md).

## What an item costs to forge

- **Status:** the DF wiki (Melt item, v53.16; Metalsmith's forge)
- An item with a material size costs a third of a bar per point, in whole bars, at least one: max(1, floor(size / 3)). Gauntlets and boots are made in pairs and share it.
- Without a material size: ammo is made 25 a bar, coins 500, flasks and goblets 3; crafts 1 to 3 a bar; blocks, mechanisms, chains, buckets, animal traps, instruments and toys a bar each; furniture, cages, splints, crutches, and ballista arrows and arrowheads three bars.
- **Depends on it:** refinish-melt.lua (WHAT AN ITEM COSTS TO MAKE). Its crafts are costed at the least one can hold, a third of a bar, so a craft is never credited more than went in.

## A melt destroys its item whole, and completes once a cycle

- **Status:** measured (2026-10-03)
- DF destroys a melted item whole. A melted item stays in the item list for a few ticks afterwards, flagged for removal. A repeating melt job fires the completion event once for every cycle.
- **Depends on it:** refinish-melt.lua settles a melt two ticks after its completion.
