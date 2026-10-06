# rm_knowledge_base: INDEX

What Refinish Metal's development has established about Dwarf Fortress, DFHack and RM itself, with the evidence for each claim. The companion repos hold raw material (structure dumps, vanilla raws, archived probes); this one holds conclusions.

## How entries are written

Every entry states one claim, then:

- **Status:** `measured` (a probe, a log or a live test showed it), `code` (read from the source: DF structures, DFHack, RM), `decided` (a design decision, with its reason), or `inference` (reasoned, not yet measured: say what would confirm it).
- **Evidence:** the log lines, probe runs, file and line, or test that shows it.
- **Date** it was established, and what in RM depends on it.

A claim is corrected in place, keeping the old claim and the date it fell, never silently rewritten.

## Files

| File | Covers |
|---|---|
| `df/saves.md` | How DF saves: the quicksave request and saver, save & continue, save & quit, the options screen, ticks, where saves live on disk, holding a save request down, what makes a write long, whether options.open tracks the screen |
| `df/colours.md` | Material colours are patterns; colour, pattern, dye and tool cache indices; palette mods |
| `df/jobs.md` | Reagent slots and stacks, fuel slots that collect by quantity and burn whole, a job's items arriving one at a time, tools named by number, a missing category, permits after startup, a table's volume, builtin coal held against a bar's dimension, the reagent a red row names |
| `df/menus.md` | The task menu's lists and rebuilds, folders and their reactions, the folder token, Back, the 16-bit material number, stale pointers, New work order's size, the material picker, pile lists as saved, a reagent's requirement line written from its own fields |
| `df/melting.md` | A furnace's part bars in tenths, DF's credit per material size, what items cost to forge, a melt destroying its item |
| `dfhack/scripts.md` | reqscript copies and stale handles, overlay entry points, the console, vectors, timers, filesystem, a missing field's throw, closures per read, bitfields, finding scripts by name, items.all's order and the next item number, what print_timers measures and names, a walk spread across ticks, isCitizen on the dead |
| `rm/save-system.md` | RM's save design as it stands and how it got there: hotsave, the save hook, the failsafe, the ledger, the tool record, the files check and kept copies, held-back saves, the options screen's kept tool record and the ledger's size check, tools in saved jobs and work orders, smelters' part bars, pile settings following their materials |
| `rm/module-lifecycle.md` | Module start and stop hooks, rejected modules, RM's services following the data, the dispatcher's subscription rules |
| `rm/performance.md` | Measured costs and the fixes that cut them, the region4 passes of 2026-09-30 to 2026-10-02 (runtime and load), drift, what is left |
| `rm/finishes.md` | Finishes minted just in time: why, base and dust pairs, the roster, reactions rebuilt each load, noticing bars and dust in play, placeholder folders, the default selection |
| `rm/forge-menu.md` | The forge's refinished metals folder: why, the layout and how it was reached, each view, button ownership, in play |
| `rm/melting.md` | Every melt measured, the remainder bank, no byproducts on melts, a smelter's store covering the array, the melt bank on the building sheet |
| `rm/dust.md` | The dust unit, the byproduct switch, stacked payouts, mixed inputs shared by volume, runtime classes, grinders for finished metals, clay bricks and grog, the block standard, glue as granules, mineral dyes, RM's own Make dye, flux parked, banks listing every row, balances shown once paid, dust rows by class, products that always come out whole, the scale form gone |
| `rm/requirement-text.md` | Reagents that say what they need: reads, the class service's words, product gates, the words watchers and RM write, the words in use, what still prints a token |
| `rm/stockpile-windows.md` | How the window service counts twins: the known list, the renewal pass, the stored and workshop shortcuts and what each can miss, classify, the pile list, the opening, the retry wait |
| `making-fuel/fuel.md` | Runtime clones and the ghost engine, drains and tank fills, fill batching, binder twins for any clay, fuel access's kept fuel and decided slots, the engine's per poll records, the binder's output mark, air-dry's report to the tool wash, fuel stacking decided and shelved, liquid glue retired, the kept menu key and its size, dead citizens at the pyre, the retort's building material |
| `methods/verification.md` | How claims are measured and changes verified: probes, the section probe, reporting first, comparing runs, estimates, mock harnesses side by side, pair round trips, bytecode checks, naming before probing, an engine fact probed first, records compared by content, a pass checked for what it read, a mock's names from the code, reading what DF built |
| `rm/script-audit.md` | Which scripts the running system loads, and which are utilities, probes or dead |

## Sources

Established in the Refinish Metal sessions of 2026-09-29 to 2026-10-06 unless an entry says otherwise. Session transcripts, logs and probe scripts are the underlying record.
