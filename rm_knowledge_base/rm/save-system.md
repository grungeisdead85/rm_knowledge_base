# RM's save system

What happens to RM's data around every save, as of 2026-09-30, and the steps that led here.

## The rule: RAM clean when DF writes, records written before the request

- **Status:** measured (df/saves.md)
- Every save is written with RM's and the modules' additions out of RAM, and every load puts them back. The records that let a load put objects back, the material ledger and the tool record, must be in site data before the save request, because DFHack writes its data first.

## Load at the true end of a save, never on a tick

- **Status:** decided (Jay, 2026-09-30) and measured
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

- **Status:** decided (Jay, 2026-09-30, on condition that everything still works and lag stays out of places it does not belong) and measured
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
