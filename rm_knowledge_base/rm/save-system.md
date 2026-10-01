# RM's save system

What happens to RM's data around every save, as of 2026-10-01, and the steps that led here.

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

## The tool record (refinish-tool-wash)

- **Status:** code, measured
- Item id to tool code for every owned tool item, one shared record; no item is touched (RECORD, NOT REPOINT, since 2026-09-29; before that items were repointed to jugs). At load DF brings module tools back as cauldrons, its default, because their itemdefs do not exist yet; each module's items are repointed right after its tools inject, and `settle()` names what never came back and consumes the record.
- Stored as one layer of JSON through `saveSiteDataString` since 2026-09-30 (read back 398 old-form records, then 464 new, in play).

## History

- 2026-09-29: the legacy AUTOSAVE cycle (save, wash to base metals, restore) retired; hotsave for all; a one-time migration restores an old payload by name. The ESC menu data cycle replaced by pre-save hooks.
- 2026-09-30: hotsave restore on the request clearing; the cycle always paused; no completion prompt; the save hook's pause hold; save & quit left to the failsafe; the tool record and the ledger stored as single layers; the ledger kept when nothing has moved.
- 2026-10-01: the failsafe reports each failed step and counts what is left before it claims success; the unload's code kept in memory, with the sweep's lookups answered from it; RM's files checked every 5 s by known path, with an alarm; a save & continue held back while they are missing; prompts after an unload wait for a settled screen.

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
