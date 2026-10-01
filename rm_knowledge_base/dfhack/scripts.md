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

## Reading a field an object's class lacks raises an error

- **Status:** code and measured (2026-10-01)
  - Code: DFHack LuaTypes.cpp `lookup_field` calls LuaWrapper.cpp `field_error`, a `luaL_error` with the message `Cannot read field <class>.<name>: not found.`
  - Measured: in the ghost engine, region4.
- **What happens:** a struct reference answers only the fields its class declares. Any other name raises; it never answers nil.
- **Where RM meets it:** RM's reads on items meet every class. A job's items include corpses, which carry no `mat_type` (refinish-stockpile-windows.lua, ONE READ PER ITEM). So a read that can meet a class without the field sits under a pcall.
- **What the throw costs:** the held-item identity read every item's `dimension` under pcall, once per item, twice a poll. `yield: held items, priced before` went from 10 µs a call to 20 to 30 µs. Once the answer was learned per item type it took 2 µs (443.7 s run).
- **Which classes have `dimension`** (df-structures df.item.xml):
  - with it: bars, liquids and powders (`item_liquipowder`), globs, thread, cloth and sheets;
  - without it: logs, tools (gravel, kindling, branches), boulders, plants and corpse pieces.
- **Rule:** each item_type names exactly one class (the item_type enum's `classname` attribute, df.d_basics.xml: 93 types, no class used twice), and a class's fields are fixed. So whether a type has a field can be learned once, with one guarded read, and kept for the life of the process. See `dimension_of` in refinish-reaction-adaptive.lua.

## A closure and a pcall per read cost about as much as the read

- **Status:** measured (2026-09-30, 2026-10-01)
- **Measured:**
  - a walk of 20,190 bars cost 16.7 ms reading each field through `try()`, which is two closures and two pcalls an item, and 9.6 ms reading them directly (walk probe, 2026-09-30);
  - `flags_on` took 35 ms to lend 2,099 flags over 459 twins, with a closure and a pcall per flag read (2026-10-01).
- **Rule:** in a loop over items, guard a read with one pcall on a named function, such as `pcall(mat_of, it)`, which builds no closure.

## A bitfield's whole is one read

- **Status:** code (Lua_API: a bitfield's `whole` is its value as an integer) and measured (2026-10-01)
- **Before:** the window service's classify read up to seven item flags one by one, each a read through DFHack. A count of 4,285 twins cost 25.8 ms, about 4 µs an item.
- **Now:** `it.flags.whole` reads them all at once, and the bits are tested in Lua. The bit positions come from `df.item_flags` by name, so no number is hard coded.

## Finding a script by name searches every script folder, in order

- **Status:** measured (2026-10-01, region4: 24 script folders, RM's the 18th)
- **What it cost:** a lookup by name (`dfhack.findScript`) walks DFHack's script folders in order. RM's script check made 12 lookups every 5 s: 86 ms a run, 110 at worst. With the kept copies refreshed, that came to about 15 ms/sec, plus 180 ms at a save request.
- **Now:** each file is found by name once. After that only its known path is asked about, with one `dfhack.filesystem.mtime` call, which answers -1 when the file is gone and a new value when it changed. The check costs about 0.6 ms a call.
- **When the paths are forgotten:** at each map load, since DFHack builds its script folders afresh for each world.
