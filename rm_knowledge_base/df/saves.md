# How Dwarf Fortress saves

## The quicksave raises a request, runs its saver while paused, and clears the request at the end

- **Status:** measured (refinish-save-probe, hotsave mode, three runs, 2026-09-29/30)
- `plotinfo.main.autosave_request` rises with `autosave_timer` counting down one per frame. The saver, `plotinfo.main.save_progress`, then steps `stage/substage` 1/1 to 50/50, one stage per frame, with the game paused and DF's main loop blocking for seconds inside some stages. On the frame the saver reaches 51/51 the request clears. The saver stays at 51/51 afterwards; it never returns to 0/0.
- No tick runs during any of it. In the measured run the first tick came 1,956 frames later, when the player unpaused.
- **RM depends on it:** the hotsave restores on the frame the request clears (rm/save-system.md).

## A quicksave's files are on disk before its request clears

- **Status:** measured (refinish-save-probe run 4, 2026-09-30)
- The probe snapshotted the save directory's files (mtime and size) at the request's rise, its clear, and 1,500 frames after. The save went into `autosave 1`: `world.sav` and DFHack's `.dat` files were all written before the clear, and nothing in the 1,824 watched files changed after it.

## Save & continue: a flag, a five-frame countdown, and the options screen closing at the end

- **Status:** measured (2026-09-29, and region4 2026-09-30)
- `options.do_manual_save` rises with `manual_save_timer` at 5, counting down one per frame. The quicksave's saver (`save_progress`) does not move: it read 0/0 throughout.
- The flag stays true after the save, until the options screen next opens, so it cannot mark the save's end.
- DF closes the options screen by itself when the save is done: 51 frames after the countdown ended, both times measured (13 s in one world, 33 s in region4). That close is the only end-of-save signal on this path.

## The options screen halts the simulation without touching pause_state, and a tick runs on the frame it closes

- **Status:** measured (refinish-save-probe, menu mode, game running, 2026-09-30)
- `pause_state` read false the whole time the screen was open, yet the tick stayed at +310 from the screen opening to the save's end.
- The first read after DF closed the screen showed +311, in the same DFHack update in which RM's save hook saw the close and reloaded. Nothing simulates between two callbacks in one update, so that tick ran before the reload.
- **RM depends on it:** the save hook holds the pause itself from its unload to its reload (rm/save-system.md).

## Save & quit: no field marks the final click, and the map unloads before DF writes

- **Status:** measured (2026-09-29, 2026-09-30); the write order comes from early save tests in play, and was confirmed by a save & quit taken with RM loaded that loaded cleanly (2026-09-29)
- The options context becomes `MAIN_DWARF_SAVE_AND_EXIT_CHOICES` when the player opens the save and exit choices; in the measured run nothing else changed until the map unloaded 87 frames later.
- DF leaves the fort first: `SC_MAP_UNLOADED` fires, and DF writes the save on its saving screen afterwards. DFHack writes its persistent data when that save screen appears.

## The options screen's fields outlive the screen and the map

- **Status:** measured (2026-09-29 region2; 2026-09-30 back-out lock)
- region2 loaded with the context still on the save and exit choices from the quit that wrote it. A back-out that closed the screen straight from the choices left the context reading them with no screen shown; a typing flag can do the same. Anything reading these fields must check the screen is actually shown, from the live focus (`dfhack.gui.getCurFocus()` starting `dwarfmode/Options`).

## DFHack writes its persistent data before any script sees a save request

- **Status:** code (DFHack Core.cpp, read 2026-09-29) and measured (test2, 2026-09-29)
- Core's update writes persistent data (site data included, into `save/current`) on the frame `do_manual_save` or `autosave_request` rises, or the save screen appears, and only then runs per-frame handlers. Anything a script writes to site data on the request frame misses that save: test2 carried a census written 24 s before its request, but not a tool record written at the request, and all 288 tools came back as cauldrons.
- **RM depends on it:** the records a save needs are written when the options screen opens.

## Saves live under getBaseDir, not under getSavePath's folder

- **Status:** code (DFHack dfhack.lua, Filesystem.cpp, Core.cpp) and measured (2026-09-30)
- `dfhack.getSavePath()` is one line of Lua: `dfhack.getDFPath() .. '/save/' .. save_dir`, the install folder. DFHack's own core keeps saves under `Filesystem::getBaseDir()`, which outside portable mode is DF's user data folder (`DFSDL_GetPrefPath`, on Windows `%APPDATA%/Bay 12 Games/Dwarf Fortress`). A probe that watched getSavePath's folder read nothing three runs running; `dfhack.filesystem.getBaseDir() .. '/save'` worked at once.

## A save written with RM's additions in the raws arrays is corrupt; stale item references are not

- **Status:** measured (save tests in play)
- The raws arrays (inorganics, reactions and the like) must hold none of RM's or a module's additions when a save is written. Items that reference injected indices fail gracefully and recover once the indices exist again.

## A cleared save request comes back until it is held down every frame

- **Status:** measured (2026-10-01, refinish-save-cancel-probe, RM shut down, on a copy of the fort)
- **Clearing once does not hold:** clearing `options.do_manual_save` once, on the frame it rose, failed. The flag came back, the countdown ran out and the save was written (seen in play; the probe's own file check read nothing).
- **Holding it down every frame does:**
  - across 3,000 frames the flag was raised again 18 times, each time with `manual_save_timer` still at 5, and was cleared each time;
  - the timer never moved and the menu stayed open;
  - no save happened until the hold ended, and the next press then saved at once.
- **What the player sees:** the save name screen simply does not take the save.

## A save written while RM's scripts were missing carried RM's data

- **Status:** measured (2026-10-01)
- This bears out the claim above about RM's additions in the raws arrays.
- With RM's files deleted mid game, a save & quit wrote REFINISH_CORE_AGG_PLASTER into the save, and it would not load.
- A second test left 29 tool defs in RAM, and that save would not load either (rm/save-system.md).

## DF's write time follows the fort, not RM's loops

- **Status:** measured (2026-09-30, 2026-10-01; region4) and one inference
- **DF's own write of region4** (the hotsave's Engine figure):
  - 21 s, then 26.1 s, on 2026-09-30;
  - 47.7 s the next morning, before any change of that day;
  - 49 to 50 s through 2026-10-01.
- **RM's checks are not the cause:** cutting RM's script check from 135 ms to 1 ms every 5 s left the write at 50 s.
- **Fort size is:** a regular fort (vanilla, RM and its modules) saves quickly (in play, 2026-10-01). What grew is the fort and its mods.
- **Inference:** during one 80 s save window the script check ran 6 times, not 16, and about 50 s of it was DF writing. That fits DF running no script loops while it writes.
