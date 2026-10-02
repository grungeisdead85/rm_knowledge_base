# DFHack scripts, handles and entry points

## A handle captured at a script's first load can outlive the copy it belongs to

- **Status:** code (Lua_API.txt, reqscript: a retained reference "may lead to unintended behavior if the location of the script changes (e.g., if a save is loaded or unloaded)") and measured (2026-09-30)
- Loading a save changes DFHack's script paths, so a script can be loaded again as a new copy with new tables. A `_G` handle or a reqscript result held from an earlier load can point at the old copy.
- Measured: Making Fuel's drain key and tank fuel scripts held `_G.refinish_adaptive_api` from their first load. Every `register_alias` call went into tables the live engine never read, for a whole session: zero adoptions. The same call from the console, reading the global fresh, adopted both bases.
- **Rule:** read a stateful handle from `_G` at the moment of each call. A global lookup costs nothing; `reqscript` by name costs about 2 ms a call (measured), so resolve modules at file scope but read shared handles fresh. A stateless module kept from an earlier load still does its work.
- **Corrected in place (2026-10-02):** "about 2 ms a call" was measured on 2026-09-24. In region4 a lookup by name costs 6.5 to 7 ms: the cost follows how many script folders DFHack searches ahead of the script's own (FINDING A SCRIPT BY NAME, below). An environment found by name may be kept as long as no load intervenes: RM keeps one until the module registry is replaced, which every load and reload does.

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
- **The same cost elsewhere:**
  - the module engine made 221 lookups by name in one region4 load, 1,428 ms, 6.5 ms each, until each script was found once a run (ONE LOOKUP PER SCRIPT A RUN, 2026-10-01);
  - the save hook's options screen refresh made two at every opening, and its background build one every frame it ran: an opening cost 20.4 ms, 12.4 and 8.0 of it in the two parts that looked a script up. Found once a data cycle, an opening cost 4.0 ms (THE TWO SCRIPTS THE REFRESH CALLS, 2026-10-02).

## world.items.all is in id order, so the items made since a mark are its tail

- **Status:** code (DFHack finds an item by id with a binary search over `world.items.all`: df.item.xml, the item instance vector, keyed by id) and measured (2026-10-02: the coal watcher's and the tool tint's reads of new items check the order as they go, and neither warned in any session)
- **How RM uses it:** keep the next item id at a mark (`df.global.item_next_id`, below), find the first position holding an id at least that large with one binary search, and read on to the end.
- **Who reads new items this way:** the coal watcher (it catches traders', migrants' and invaders' goods, which the created event skips), the tinder watcher, the tool tint's new tools and the tool wash's record for the options screen.

## df.global.item_next_id is the id the next item will get

- **Status:** code (an archived probe, probe-corpsepiece.lua, numbers the items it creates from it) and measured (2026-10-02)
- **What it buys:** one read splits every item in the world into made before and made after.
- **Measured:** the binder watcher reads it at each poll to tell a job's output from the binders already in the workshop: the same yields as the walk of the workshop it replaced, at 0.02 ms a job instead of 0.82 (making-fuel/fuel.md).

## print_timers measures unpaused time, and names a Lua loop only when the loop reports itself

- **Status:** measured (2026-10-02, `:lua require('script-manager').print_timers()`), and code for the clock (Lua_API.txt: `dfhack.getTickCount()` returns the tick count in ms)
- **Unpaused only:** the report says so. A loop's cost while the game is paused, an options screen or a save, is not in it.
- **Names:** a loop on `dfhack.timeout` shows only in the timers' unnamed share (`framework`). A loop that calls `dfhack.internal.recordRepeatRuntime(name, start_ms)` after each run gets a row of its own. Once RM's dispatcher reported each subscriber as `d:<name>` and RM's own loops reported under their names, the unnamed share of Lua timer time fell from 75% to 11 to 14%.
- **Resolution:** `start_ms` comes from `dfhack.getTickCount()`, in whole milliseconds, so a short loop's runs read 0 or 1 ms each and its total is right only on average.

## A walk spread across ticks can pass an item over

- **Status:** code (a vector's later items move down when one is removed) and measured in mocks (2026-10-02)
- **What goes wrong:** a walk that reads a vector by position a slice at a time, across ticks, loses its place when an item below its position is removed: everything after it moves down one, and the next slice starts one item late.
- **The two cures RM uses:**
  - where the vector is in id order (`items.all`), walk by item id: each slice starts from a binary search for the next id (the tool wash's background build);
  - elsewhere, check that the last item read is still where it was left, look for it within a few places either way when it is not, and go on after it. A pass that cannot find it marks itself unsure and drops nothing at its end (the tool tint's backstop, the window service's renewal pass).
- **Measured in the mocks:** with an item removed every frame, every pass read each item present throughout exactly once. A block of 100 removed at once made the pass unsure, and it dropped nothing.
