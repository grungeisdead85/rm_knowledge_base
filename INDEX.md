# rm_knowledge_base: INDEX

What Refinish Metal's development has established about Dwarf Fortress, DFHack and RM itself, with the evidence for each claim. The companion repos hold raw material (structure dumps, vanilla raws, archived probes); this one holds conclusions.

## How entries are written

Every entry states one claim, then:

- **Status:** `measured` (a probe, a log or a live test showed it), `code` (read from the source: DF structures, DFHack, RM), `decided` (Jay's design decision, with its reason), or `inference` (reasoned, not yet measured: say what would confirm it).
- **Evidence:** the log lines, probe runs, file and line, or test that shows it.
- **Date** it was established, and what in RM depends on it.

A claim is corrected in place, keeping the old claim and the date it fell, never silently rewritten.

## Files

| File | Covers |
|---|---|
| `df/saves.md` | How DF saves: the quicksave request and saver, save & continue, save & quit, the options screen, ticks, where saves live on disk |
| `df/colours.md` | Material colours are patterns; colour, pattern, dye and tool cache indices; palette mods |
| `dfhack/scripts.md` | reqscript copies and stale handles, overlay entry points, the console, vectors, timers, filesystem |
| `rm/save-system.md` | RM's save design as it stands and how it got there: hotsave, the save hook, the failsafe, the ledger, the tool record |
| `rm/module-lifecycle.md` | Module start and stop hooks, rejected modules, RM's services following the data, the dispatcher's subscription rules |
| `rm/performance.md` | Measured costs and the fixes that cut them |
| `making-fuel/fuel.md` | Runtime clones and the ghost engine, drains and tank fills, fill batching, binder twins for any clay |
| `methods/verification.md` | How claims are measured and changes verified: probes, mock harnesses, pair round trips, bytecode checks |
| `rm/script-audit.md` | Which scripts the running system loads, and which are utilities, probes or dead |

## Sources

Established in the Refinish Metal sessions of 2026-09-29 and 2026-09-30 unless an entry says otherwise. Session transcripts, logs and probe scripts are the underlying record.
