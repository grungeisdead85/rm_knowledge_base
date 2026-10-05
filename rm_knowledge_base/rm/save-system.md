# RM's save system

What happens to RM's data around every save, as of 2026-10-02, and the steps that led here.

## The rule: RAM clean when DF writes, records written before the request

- **Status:** measured (df/saves.md)
- Every save is written with RM's and the modules' additions out of RAM, and every load puts them back. The records that let a load put objects back, the material ledger and the tool record, must be in site data before the save request, because DFHack writes its data first.

## Load at the true end of a save, never on a tick

- **Status:** decided (2026-09-30) and measured
- Restoring while a save is still being written corrupts it (an early version did). For years no end-of-save hook was known, so the hotsave restored on the first tick after its request, and that tick simulated with every module material out of the array: a liquid of a module material resolves to magma (misted once in play, 2026-09-29).
- Now: the hotsave restores on the frame `autosave_request` clears; the save hook reloads a save & continue on the frame DF closes the options screen.

## The hotsave cycle (refinish-autosave)

- **Status:** code, measured in play 2026-09-30
- Pauses for the whole cycle whatever Pause on Save says; the setting decides only whether the game stays paused after. Writes the ledger snapshot (`if_changed`), stops RM's services, clears (modules stop first), quicksaves, then a save watcher restores on the request clearing; if the request is never seen or never clears it falls back to the next tick with a WARNING. RM's services start last.
- No completion prompt since 2026-09-30: a prompt is a modal screen, which held the game paused over the resume. The figures are on the status panel and in a DETAIL line.
- Measured in region4: Clear 1.4 s, Engine (the save) 21 s, Restore 12 s.

## The game's save & continue (refinish-save-hook)

- **Status:** code, measured in play 2026-09-30
- Unloads on the frame `do_manual_save` rises; takes and holds the pause, reasserting it every frame; reloads on the frame the options screen closes; hands back what the player had. Measured before the hold: one tick ran with RM out on the close frame. In a mock of the measured frame order the hold brings that to zero, and it stays zero with an unpause from the HUD mid-save.
- **The watch, since 2026-10-02:** the hook runs every frame, and asks DF for the focus string only while `options.open` is set (df/saves.md), with a tripwire that asks anyway every 100 frames. The monitor went from about 2.0 to about 1.7 ms/sec (DFHack's timers). The rest of its frame is the status panel's clock string and the walk to the options struct, parked.

## The game's save & quit: no unload by the save hook

- **Status:** decided (2026-09-30, on condition that everything still works and lag stays out of places it does not belong) and measured
- Until 2026-09-30 the hook unloaded on the frame the save and exit choices opened, since no field marks the final click, and reloaded if the player backed out. That put a full data cycle into a back-out (about 2 s to unload and 12 s to reload in region4) for a save that never happened. Its back-out test read options fields that outlive the screen, which once left RM unloaded and, with the pause hold, locked the game paused; before the hold the same back-out silently left RM unloaded while play went on.
- Now nothing unloads there. The records are refreshed when the options screen opens; DF unloads the map before it writes; the map unload failsafe clears RAM. Confirmed in play: 466 of 466 tools restored, no remap needed, no faults.

## The map unload failsafe (refinish_steel)

- **Status:** code, measured in play 2026-09-30
- Stops RM's services, clears entity permissions, reactions and materials (each gated on a loaded flag the index scripts set and map load re-derives from RAM) and every module's assets, modules stopped first. Measured clear at a save & quit: 220,003 permissions, 99,578 reactions, 61,392 materials, 107 fuelwood twins, every module tool.
- It writes no tool record: site data can no longer be written at the map unload. A 2026-09-29 save & quit with RM loaded came back clean for RM, but with every module tool a jug: the failsafe's old wash repointed them and could keep no record. The failsafe no longer washes, and the record is written before save & quit can be chosen.

## The material ledger (refinish-ledger)

- **Status:** code, measured
- Records id to index for every owned inorganic, name to pair for every owned plant material (`PLANT_ID|MAT_ID`: mat_type 419 plus the material's position, mat_index the plant's), and each finish's base metal. The remap at load moves every object (items, constructions, buildings, dye references, history events) from the index its material held to the one it holds now, by name.
- **Parking:** a finish that is no longer generated (its base metal deselected) sends its objects to the base metal and parks them in site data; reselecting the metal gives them their finish back (10,000 parked and restored in play, 2026-09-30).
- **Storage** (2026-09-30): plain lines through `saveSiteDataString` (`LEDGER 2`; tokens with whitespace or % escaped, since DF ids can hold spaces: gem materials, `REFINISH_CORE_AGG_LAPIS LAZULI`). `saveSiteData` JSON-encodes its value, so a JSON string was stored double-encoded and `getSiteData` read it back through DFHack's character-by-character JSON reader: about 60 s at 8,956 materials, which hung region2 at load. Lines read in 29 ms there; region4's 61,801 records, 7.2 MB, read in about 0.4 s. The old form still reads (`unwrap_old`).
- **Kept when nothing has moved** (2026-09-30): `write({ if_changed = true })` compares the arrays' exact order (the site and every inorganic and plant material id in place) with the last write's and keeps the stored ledger when they match. Callers: the save hook's menu refresh, the shutdown's snapshot, the hotsave's snapshot. Startup's write after a data cycle is always full. Before, one session wrote three identical 7.2 MB ledgers, one at each menu opening. Measured in play: a full write takes 594 ms in region4, a kept one 31 to 47 ms (2026-09-30).
- **Corrected in place (2026-10-02):** the comparison above read every id at every call, 31 to 62 ms an options screen opening in region4. Now the arrays' sizes are read first: the site, the inorganics, the plants and every plant's materials. The same sizes as at the last layout read keep the ledger without reading an id, 0 ms in its own log line; other sizes fall through to the exact comparison.
  - **The rule the sizes rest on** (THE ARRAYS' SIZES, ASKED FIRST): during play a material is only ever appended, as the tinder and aggregate twins are; anything that renames or moves one in place does it inside a data cycle, which sets the layout afresh, or must clear `last_sig`.
  - **Measured in a mock:** an appended twin, inorganic or plant material, is caught as before; a rename in place is not, as the rule says.

## The tool record (refinish-tool-wash)

- **Status:** code, measured
- Item id to tool code for every owned tool item, one shared record; no item is touched (RECORD, NOT REPOINT, since 2026-09-29; before that items were repointed to jugs). At load DF brings module tools back as cauldrons, its default, because their itemdefs do not exist yet; each module's items are repointed right after its tools inject, and `settle()` names what never came back and consumes the record.
- Stored as one layer of JSON through `saveSiteDataString` since 2026-09-30 (read back 398 old-form records, then 464 new, in play).
- **The options screen's copy, kept in memory (2026-10-02):**
  - **Before:** every opening washed in full: a walk of every item in the fort for its owned tools (9,914 in region4), a decode of the stored record and an encode of the whole record. 273 to 279 ms an opening, 386 at worst.
  - **Now:** the record is kept in memory (THE RECORD, KEPT BETWEEN OPENINGS OF THE MENU). It is built in the background in about a second after each load, by the full wash's own walk and merge, read by item id so a removal cannot make it pass one over (dfhack/scripts.md). Each opening tops it up with only the items made since and the items a script changed, and writes it only when that changed it, joined from one string per item. 1.5 ms an opening.
  - **The rule it rests on:** a script that changes which owned tool an existing item is lists the item in `_G.refinish_tool_wash_touched`. Air-dry does (wet to dry); restore changes tools only during a load, before the record is kept.
  - **The one difference from a full wash:** an owned tool the build read and that was used up before the record's first write keeps an entry, which restore counts as no longer in the world. In the mock: 17 such entries after a data cycle, every one an item gone, nothing missing, no tool different. With no data cycle between, the records were identical at every opening.
  - **Confirmed in play (2026-10-02):** a save & quit restored 9,973 items with 37 gone, the 10,010 entries its last opening wrote; a save & continue restored 10,048 with 46 gone, the 10,094 its opening wrote. No WARNING, and the save's own full wash found no tool the kept record lacked.

## History

- 2026-09-29: the legacy AUTOSAVE cycle (save, wash to base metals, restore) retired; hotsave for all; a one-time migration restores an old payload by name. The ESC menu data cycle replaced by pre-save hooks.
- 2026-09-30: hotsave restore on the request clearing; the cycle always paused; no completion prompt; the save hook's pause hold; save & quit left to the failsafe; the tool record and the ledger stored as single layers; the ledger kept when nothing has moved.
- 2026-10-01: the failsafe reports each failed step and counts what is left before it claims success; the unload's code kept in memory, with the sweep's lookups answered from it; RM's files checked every 5 s by known path, with an alarm; a save & continue held back while they are missing; prompts after an unload wait for a settled screen.
- 2026-10-02: the save hook asks for the focus only while `options.open` is set; the options screen's tool record kept in memory and topped up; the ledger's sizes read first; the refresh's two scripts kept once a data cycle, and RM's files checked at every opening. An opening of the options screen went from 273 to 279 ms (386 at worst) to 4.0 ms (7 at worst).

## RM's own files are checked while the game runs

- **Status:** code and measured (2026-10-01)
- **What was measured:** RM's script files were deleted while the game ran, and a save & quit then wrote a save that would not load, carrying REFINISH_CORE_AGG_PLASTER.
  - Two seconds earlier the options screen's refresh had failed with "Could not find script refinish-tool-wash" and "... refinish-ledger".
  - The map unload failsafe ran every scrubber inside a pcall that dropped its error. Nothing was cleared, and it still logged "Memory successfully terminated." before DF wrote the save.
- **The failsafe now:**
  - keeps and logs each step's failure;
  - then counts what of RM's is still in the raws, using the autosave's own test, written into refinish_steel because no other RM script may be reachable at that moment;
  - writes its success line only when nothing is left.
  - The count includes the plants and building defs the module sweep removes; in a second test, a count without them reported only the tools (WHAT THE UNLOAD LEFT IN RAM).
- **The alarm:** the twelve scripts every save path calls by name are checked every 5 s by known path (dfhack/scripts.md), except during a save. While any is missing, an alarm says so in Danger colours, and again in Caution colours once they are back (RM'S OWN FILES, STILL THERE).
- **At every options screen opening (2026-10-02):** the refresh's two scripts are now kept once a data cycle (dfhack/scripts.md), so a deleted file no longer makes the refresh fail, which is what used to bring the check forward there. The opening now runs the check itself, every time, about 0.5 ms by known path.

## The unload's code is kept in memory

- **Status:** code and measured (2026-10-01)
- **What is kept:** at each map load, and whenever the check finds a file changed, refinish_steel keeps the text of the three clear scripts and the environments of the module engine and its three injectors.
- **How it is used:** the failsafe runs each step from its file first, and from the kept copy only when the file cannot be reached. While the sweep runs, a lookup by name whose file is gone is answered from the kept environments.
- **Measured, a save & quit with the files deleted:**
  - the clear scripts ran from their copies: 61,392 materials, 99,579 reactions, 892 categories and 220,003 permissions cleared;
  - before the lookup fallback, every tool, building and plant clear in the sweep failed, because the sweep finds its injectors by name. 29 tool defs stayed in RAM and that save would not load (THE UNLOAD, KEPT IN MEMORY);
  - with the fallback, save & quit came out clean (session report, 2026-10-01).

## A save & continue RM cannot unload for is held back

- **Status:** code and measured (2026-10-01, refinish-save-cancel-probe on a copy of the fort, RM shut down)
- **When RM's files are missing, nothing is unloaded:** `options.do_manual_save` is cleared on the frame it rises, and every frame it rises again while the options screen is up. The player is told why in Danger colours, at most once every REFUSE_NOTICE_MS. A save goes through again once the files are back.
- **A save & quit is not held:** the map unload clears RAM from the kept copies.
- **DF's behaviour behind it:** df/saves.md (A SAVE RM CANNOT UNLOAD FOR IS HELD BACK, refinish-save-hook.lua).

## A prompt after an unload waits for a settled screen

- **Status:** code and measured (2026-10-01)
- **What went wrong:** waiting only for the world to be gone was not enough. Prompts were drawn over DF's save screen during a save & quit, stacked and garbled.
- **Now:** a prompt after a map unload waits for either the title screen with the world gone, or a fort with a map loaded again. After SETTLE_MAX_FRAMES it is shown regardless.

## The ledger carries tools in saved jobs and work orders

- **Status:** code, tested in a mock of the real remap (2026-10-04)
- A job and a work order name a tool by number, and RM's and the modules' tools are numbered in injection order (df/jobs.md). Every write records each owned tool by name with its number (T lines). The record is in the fingerprint, so a change to the tools alone takes the full remap.
- At load the jobs and work orders pass moves every tool number by name, the way it moves materials: an item slot, a job or order that makes a tool, an order's items and its item conditions. Only a number an owned tool held last session is touched; vanilla's never move. A tool no longer injected keeps its number, with a WARNING.
- **Mock:** with glue injected ahead of gravel and Making Fuel's tools, a saved branch job moved 5 to 6, a job making a binder 6 to 7, and an order's gravel condition 4 to 5; a vanilla tool slot and a bar slot were untouched, and the next write recorded the new layout.
- **Limit:** a ledger written before 2026-10-04 holds no tools, so jobs saved under it cannot be moved.

## The ledger carries smelters' part bars

- **Status:** code (2026-10-04)
- A smelter's store is indexed by inorganic (df/melting.md), so a finish that moves between loads would leave its part bars under another metal. At every load the ledger first fits every furnace's store to the array, then moves each store's entries by name alongside every other object. Part bars of a finish no longer generated go to its base metal's entry, as its items do. The fitting runs even when nothing moved, since a store sized before finishes were minted ends short of them.
- **Measured at load:** seven furnaces' stores were fitted to the 1,256-entry array (STORES DETAIL).

## Pile settings follow their materials

- **Status:** code and measured (2026-10-02 and 2026-10-03)
- A stockpile keeps its choices in lists indexed by inorganic position (eleven lists, refinish-stockpile-windows.lua, INORG_LISTS), and DF restores them as saved (df/menus.md). A material whose position changed left its pile choices behind on whatever took its place, and nothing moved them until 2026-10-03.
- The ledger's remap_piles moves them by name, as remap() moves objects: for every owned material in the previous layout that sits elsewhere now, its entry is read from the old position and written at the new one, in every list of every pile. A list longer than the array is then cut to the array's length, since past the end it holds only the previous layout's entries, and a finish minted later in play would land on one and take a choice no one made for it. An empty list stays empty.
- All of a list's entries are read before any is written, because one material's new position can be another's old one, and each is written back as the type it was read as.
- It runs after Steps 6.7 and 7, so the finishes a load mints from the fort's bars and dusts keep their choices too. A finish first minted later in play lies past the end of an old pile's lists, as it does for a pile made the same session.
- **Measured:** the first version moved entries but cut nothing, and piles 29 and 30 kept bars lists 62,606 long with no finish in that day's array switched on (region4, 2026-10-03).
- **The finish order itself** is kept by the roster (rm/finishes.md), so most loads move nothing.
