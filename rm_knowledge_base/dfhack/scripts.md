# DFHack scripts, handles and entry points

## A handle captured at a script's first load can outlive the copy it belongs to

- **Status:** code (Lua_API.txt, reqscript: a retained reference "may lead to unintended behavior if the location of the script changes (e.g., if a save is loaded or unloaded)") and measured (2026-09-30)
- Loading a save changes DFHack's script paths, so a script can be loaded again as a new copy with new tables. A `_G` handle or a reqscript result held from an earlier load can point at the old copy.
- Measured: Making Fuel's drain key and tank fuel scripts held `_G.refinish_adaptive_api` from their first load. Every `register_alias` call went into tables the live engine never read, for a whole session: zero adoptions. The same call from the console, reading the global fresh, adopted both bases.
- **Rule:** read a stateful handle from `_G` at the moment of each call. A global lookup costs nothing; `reqscript` by name costs about 2 ms a call (measured), so resolve modules at file scope but read shared handles fresh. A stateless module kept from an earlier load still does its work.

## DFHack loads overlay scripts by itself

- **Status:** code (overlay-dev-guide.txt) and RM audit (2026-09-30)
- A script that declares `OVERLAY_WIDGETS` is loaded by DFHack's overlay framework; nothing else names it. In RM: `making-fuel-bank-readout` (the fuel bank readout beside furnace sheets) and `refinish-warning` (now the options screen's shortcut to RM's configuration). Any audit of what a mod uses must count these as entry points.

## The console splits lua's arguments; `:lua` does not

- **Status:** measured (2026-09-30)
- `lua <code>` tokenises the line as console arguments first: quotes and semicolons broke a one-liner (`<name> expected near <eof>`). `:lua <code>` hands the rest of the line to Lua as typed, as DFHack's own examples do.

## ipairs over a game vector starts at 0

- **Status:** code (DFHack Lua)
- DFHack's `ipairs` walks game vectors from index 0, which is what RM stores as material and reaction indices. Mocks of RM code must do the same.

## dfhack.filesystem.listdir reports every failure as code 1

- **Status:** code (DFHack Filesystem.cpp) and measured (2026-09-30)
- `strerror(1)` reads "Operation not permitted", which misled a probe into a permissions hunt; the folder did not exist (see df/saves.md, where saves live).

## A 'frames' timeout survives a map unload

- **Status:** code (RM loop dispatcher notes)
- DF does not cancel frame timers on an unload, so a loop's stop must cancel its own.
