# rm_knowledge_base: INDEX

> **Repository:** https://github.com/grungeisdead85/rm_knowledge_base
>
> ```
> git clone --depth 1 https://github.com/grungeisdead85/rm_knowledge_base.git
> ```
>
> A copy of this index also lives in the Refinish Metal project, where it is
> readable without cloning. It is written by hand: `build_indexes.py`, in this
> repo's `repo_index_generators/`, checks it for any file it does not name, so
> name every file by its full path from the repo root, in backticks. The one
> exception is `dfhack_docs/`, too big to list by hand: the generator writes its
> index, `dfhack_docs_INDEX.md`, and this one names that file instead.

What Refinish Metal's development has established about Dwarf Fortress, DFHack and RM itself, with the evidence for each claim, RM's development notes, and DFHack's own documentation. The companion repos hold raw material (structure dumps, vanilla raws, archived probes); this one holds conclusions, plus the DFHack manual they are checked against. It also holds the index generators for every repo and `REFERENCE_REPOS.md`, the overview of all of them.

## How entries are written

Every entry in `rm_knowledge_base/` states one claim, then:

- **Status:** `measured` (a probe, a log or a live test showed it), `code` (read from the source: DF structures, DFHack, RM), `decided` (a design decision, with its reason), or `inference` (reasoned, not yet measured: say what would confirm it).
- **Evidence:** the log lines, probe runs, file and line, or test that shows it.
- **Date** it was established, and what in RM depends on it.

A claim is corrected in place, keeping the old claim and the date it fell, never silently rewritten.

## Knowledge base entries

| File | Covers |
|---|---|
| `rm_knowledge_base/df/saves.md` | How DF saves: the quicksave request and saver, save & continue, save & quit, the options screen, ticks, where saves live on disk, holding a save request down, what makes a write long, whether options.open tracks the screen |
| `rm_knowledge_base/df/colours.md` | Material colours are patterns; colour, pattern, dye and tool cache indices; palette mods |
| `rm_knowledge_base/df/jobs.md` | Reagent slots and stacks, fuel slots that collect by quantity and burn whole, a job's items arriving one at a time, tools named by number, a missing category, permits after startup, a table's volume, builtin coal held against a bar's dimension, the reagent a red row names |
| `rm_knowledge_base/df/menus.md` | The task menu's lists and rebuilds, folders and their reactions, the folder token, Back, the 16-bit material number, stale pointers, New work order's size, the material picker, pile lists as saved, a reagent's requirement line written from its own fields |
| `rm_knowledge_base/df/melting.md` | A furnace's part bars in tenths, DF's credit per material size, what items cost to forge, a melt destroying its item |
| `rm_knowledge_base/dfhack/scripts.md` | reqscript copies and stale handles, overlay entry points, the console, vectors, timers, filesystem, a missing field's throw, closures per read, bitfields, finding scripts by name, items.all's order and the next item number, what print_timers measures and names, a walk spread across ticks, isCitizen on the dead |
| `rm_knowledge_base/rm/save-system.md` | RM's save design as it stands and how it got there: hotsave, the save hook, the failsafe, the ledger, the tool record, the files check and kept copies, held-back saves, the options screen's kept tool record and the ledger's size check, tools in saved jobs and work orders, smelters' part bars, pile settings following their materials |
| `rm_knowledge_base/rm/module-lifecycle.md` | Module start and stop hooks, rejected modules, RM's services following the data, the dispatcher's subscription rules |
| `rm_knowledge_base/rm/performance.md` | Measured costs and the fixes that cut them, the region4 passes of 2026-09-30 to 2026-10-02 (runtime and load), drift, what is left |
| `rm_knowledge_base/rm/finishes.md` | Finishes minted just in time: why, base and dust pairs, the roster, reactions rebuilt each load, noticing bars and dust in play, placeholder folders, the default selection |
| `rm_knowledge_base/rm/forge-menu.md` | The forge's refinished metals folder: why, the layout and how it was reached, each view, button ownership, in play |
| `rm_knowledge_base/rm/melting.md` | Every melt measured, the remainder bank, no byproducts on melts, a smelter's store covering the array, the melt bank on the building sheet |
| `rm_knowledge_base/rm/dust.md` | The dust unit, the byproduct switch, stacked payouts, mixed inputs shared by volume, runtime classes, grinders for finished metals, clay bricks and grog, the block standard, glue as granules, mineral dyes, RM's own Make dye, flux parked, banks listing every row, balances shown once paid, dust rows by class, products that always come out whole, the scale form gone |
| `rm_knowledge_base/rm/requirement-text.md` | Reagents that say what they need: reads, the class service's words, product gates, the words watchers and RM write, the words in use, what still prints a token |
| `rm_knowledge_base/rm/stockpile-windows.md` | How the window service counts twins: the known list, the renewal pass, the stored and workshop shortcuts and what each can miss, classify, the pile list, the opening, the retry wait |
| `rm_knowledge_base/making-fuel/fuel.md` | Runtime clones and the ghost engine, drains and tank fills, fill batching, binder twins for any clay, fuel access's kept fuel and decided slots, the engine's per poll records, the binder's output mark, air-dry's report to the tool wash, fuel stacking decided and shelved, liquid glue retired, the kept menu key and its size, dead citizens at the pyre, the retort's building material |
| `rm_knowledge_base/methods/verification.md` | How claims are measured and changes verified: probes, the section probe, reporting first, comparing runs, estimates, mock harnesses side by side, pair round trips, bytecode checks, naming before probing, an engine fact probed first, records compared by content, a pass checked for what it read, a mock's names from the code, reading what DF built |
| `rm_knowledge_base/rm/script-audit.md` | Which scripts the running system loads, and which are utilities, probes or dead |

## Development notes

RM's development notes, kept here rather than in the project because of their size. Each follows its own format and dates itself, and several mark themselves historical or say that a design has since moved on. They record their systems as they stood when written; the live code in the project is the source of truth.

| File | Covers |
|---|---|
| `RM_Notes/RM_Core_Services.md` | What each of RM core's shared services does, how a module uses it, the rules it keeps and the decisions and measurements behind them, current to the v4.0.0 release (2026-10-08): the principles, loop costs before and after (2026-09-24 and 2026-10-02), the module engine, core payload, loop dispatcher, work order units, services following the data, job surgery, reaction keys, persistent banks, byproducts, stone aggregate twins, the organic stockpile registrar, tool tint, the adaptive reaction engine, reaction outputs, material classes, requirement text, the finish mint, the forge menu, melting, the bank readout, bricks, dyes, the save paths, the ledger and tool record, decisions on record, still to build |
| `RM_Notes/RM_Module_Design_Philosophy.md` | The governing document for module content: what RM is, what modules are, the cardinal rules, cross-module interaction, module scope and boundaries, naming conventions, the design process |
| `RM_Notes/RM_Module_Schema_Reference.md` | Every module JSON configuration tested and confirmed in play, with its syntax and the test that proved it: material classes, reagent types, product resolution modes, product types, buildings, skills, permission modes, proven reaction patterns, the test content, technical notes, the glass investigation |
| `RM_Notes/RM_Schema_Reference_Additions.md` | Findings from the Making Fuel sessions, written to be merged into the schema reference: builtin material subtypes (`mat_subtypes`), the reagent flag vocabulary, a reagent quantity's two meanings, organic material encoding, the material picker's empirical table, the complete `df.item_type` map, silent material resolution failure, category nesting, reagent types not in `REAGENT_TYPES`, a reagent's reads, a product's measure and whole |
| `RM_Notes/RM_Module_Supply_Chain_Classes.md` | The reaction class vocabulary modules share, version 0.4, which retires the 0.3 vocabulary in full: what DF gives us, the four mechanisms, reaction classes, reaction products, economic stone, the Making Fuel, Making Concrete and Making Metal classes, the change log from 0.3, extending the vocabulary |
| `RM_Notes/RM_Tool_Schema.md` | Historical, by its own note: the design that brought tools into the module engine (a module's tools JSON, the tool object, the four containers, integration points, confirming the field map first). Its examples are vessel tools removed from RM's catalog on 2026-10-07, and it names `RM_MODULE_ENGINE_README.md`, section 7, as the current reference for tool fields |
| `RM_Notes/RM_Stacked_Tools.md` | How DF fills a reaction slot from stacked tool items and what it takes away, measured 2026-10-03 and 2026-10-04 with the stack and fuel stack probes: what it means, the rules that follow, what was decided and what is in force, mixed inputs, fuel slots, running the probe again |
| `RM_Notes/RM_Adaptive_Reactions.md` | The adaptive reaction mechanism (ghost reactions, the two-sided rule, adding input slots, adapting output, what extra slots do not do), the yield model (units, the curve, why sub-linear, slot arithmetic, sizing versus scoring), corpse item quirks, failure modes seen in development, what is owed. Its status line dates from the Making Fuel prototype, when the mechanism was not yet in the engine |
| `RM_Notes/RM_Adaptive_Sprites.md` | How a sprite takes its colour from its material, by DF's mechanism and by RM's: the rule in one table, the ramps, the two numbers, retoning a sprite, the TINT: system (ABGR packing, the blend, descriptor traps, the reserved range, art as Lua data), the failure that looks like success, where it hooks in, the files, dead ends recorded so they are not retried |
| `RM_Notes/RM_Sprite_System_Reference.md` | What the sprite engine accepts, written against the shipped `refinish-sprite-engine.lua`: the idea underneath, SOURCE grammar, material tokens and which prefixes are real, TARGET, what is proven, deciding what a new thing needs, the two minute test for a new item type |
| `RM_Notes/RM_Material_Sprite_Redirect.md` | Giving an injected material its own sprite by re-aiming a baked texpos pointer without dragging the rest of that pointer along: the pointer and its blast radius, what is measured, the gate (cadence, resolution, whitelist, map guard, stocks, category tripwire), failure history, instrumentation, the unexplained, generalizing it, a warning about blind tree walks. Its hide use was retired 2026-09-26; the measurements stand as the record of the technique |
| `RM_Notes/RM_Hide_Wing_Lessons.md` | What Making Fuel's glob hide wing (2026-09-11 to 2026-09-26) learned, kept after the wing was replaced by DF's own skins: why the glob was retired, globs as items, the texture entry and redirect, corpse pieces and skins, materials, names and injection, jobs, reagents and filters, script lifecycle, stockpiles, numbers worth keeping, still open |
| `RM_Notes/RM_Organic_Category_Registration.md` | How DF decides where an item is stored, and how to give an injected material a real stockpile identity in one of DF's organic categories: the problem, what is measured, barrels (unresolved), the recipe, which categories it opens, failure history, where the hide wing and the dyes landed, tools |
| `RM_Notes/RM_Stockpile_Mechanics.md` | How DF files items into piles, read from source and measured 2026-09-26 to 2026-09-28: sources, how DF addresses an item, group by group, the filing rule, DF's hauling jobs captured live, routes 2 and 3 tested for damage, the stockpile window service, DF's storage timer, stone twins refused and the piles' mirror, the menu label, hiding twins in the menus, coal and the soap switch, editing rows out of the settings screen |
| `RM_Notes/RM_Dye_Integration.md` | How Making Fuel's dyes were made indistinguishable from vanilla's, measured 2026-09-23: what DF's dye system reads, the Dyer's shop menu, stockpiling and why the dyes are plant materials, where they live, tree bark dyes, reagents naming any material by token, the data cycle, DFHack facts, mistakes made, tools; RM core's mineral dyes, and its own Make dye when a mod cuts vanilla's (2026-10-04) |
| `RM_Notes/RM_Native_Button_Injection.md` | Injecting a native button into a workshop's order list, discovered April 8, 2026: the button types observed, the CollectSand injection code, ordering rules, persistence, implications, data sources |
| `RM_Notes/RM_Native_Item_Creation_Reference.md` | Creating items with `dfhack.items.createItem` and placing them in containers, from the Making Concrete sand multiplier work: why moveToContainer does not work, manual containment refs, flag rules, thermal property copy, the one-frame delay, the two-component design, cleanup commands, IN_PLAY tracking registration, limitations, a testing checklist |

### Making Fuel

| File | Covers |
|---|---|
| `RM_Notes/Making_Fuel_Reference/RETORT_DEFECT_REGISTER.md` | Every defect found in the retort chain, what proved it and where it stands, 2026-09-07 to 2026-10-06: priority, the liquid packaging law, the design rule, the audits, open and closed defects, engine facts learned, verified working, known and not worth fixing, retractions, slot surgery, mirror sync, the per retort drain, offered and not built |
| `RM_Notes/Making_Fuel_Reference/making_fuel_bar_naming.md` | Suppressing the "bars" suffix on module charcoal: the measured facts, the BAR shape question closed, a build plan, the probe. Its status line reads diagnosed and proven, not yet built |
| `RM_Notes/Making_Fuel_Reference/making_fuel_tree_dye_research.md` | The research pass of 2026-09-23 behind the tree dye generator: the rules, the method for a documented colour, how vanilla chose its 22 bark dye colours, overrides for documented bark dyes, all 50 trees without a vanilla bark dye, gaps, source links |

### Making Concrete

| File | Covers |
|---|---|
| `RM_Notes/Making_Concrete_Reference/making-concrete-2.md` | The Making Concrete 2.0 delivery record, kept as written: what it is, the comment audit, checks after the recycle, the diffs of `making_concrete.lua` and the mix watcher. Its figures predate 2026-10-07; its opening note records the recipes after that change |

## DFHack documentation

`dfhack_docs/` is DFHack's own manual as DFHack ships it in Dwarf Fortress's `hack/docs/` folder: every page rendered as plain text, from the Lua API reference and the guides to the changelogs and one page per tool. Its index, `dfhack_docs_INDEX.md`, is generated: it names the DFHack version, lists every page and tool, gives the full outline of the pages RM reads most with the line each section starts on, and shows where each DFHack name RM uses is documented.

The manual is DFHack's account of DFHack. It says where to look, not how DF or DFHack behaves: the code and what is measured in game decide that.

## Sources

Knowledge base entries were established in the Refinish Metal sessions of 2026-09-29 to 2026-10-06 unless an entry says otherwise. The development notes date themselves. Session transcripts, logs and probe scripts are the underlying record. `dfhack_docs/` is DFHack's text, under the licenses in `dfhack_docs/LICENSE.txt`.
