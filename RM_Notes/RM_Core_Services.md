# RM Core Services

What each of Refinish Metal's shared services does, how a module uses it, the rules it keeps, and the decisions and measurements behind them. Current to 2026-10-08, the v4.0.0 release (first written 2026-09-24; everything that still holds from earlier versions is carried here). The code is the source of truth: every signature below was read from the file named, and each file's header holds the full reasoning and history.

## Principles this work follows

- **No compatibility patches.** Compatibility is built into the design: systems anchor on measurement and evaluation so they keep working with vanilla and other mods, unmaintained, for years.
- **Shared systems and shared content, once, in RM core.** A module declares what it needs; RM provides it once for every module that asks, so players never carry two of the same thing (no five CRUSH_GRAVELs). RM holds only what passes the test: would a second module want it, and does it work without the first module's systems? Content whose meaning lives in one module's systems stays with that module (2026-09-25; this replaced the rule that every form is an RM item type).
- **Compartments.** RM never fails because a module failed. A bad entry costs that entry, a missing need shelves only what needed it, and every failure is named in the log. A claim that clashes with an earlier module's costs the later module that one claim, logged.
- **Mechanical calls are made and justified by the implementer.** Design and intent are design calls, recorded with their reasons.
- **Every per-poll path is measured in the profiler before and after a change.**
- **Comments are code** (RM_Comment_Rules.md).

## Loop cost, before and after (2026-09-24)

Profiler total went from 132.6 ms/s (13.3% of the time) to roughly 30 ms/s. The large items:

| Loop | Before | After | What changed |
|---|---|---|---|
| refinish-menu-icons | 72.7 ms/s | ~3 | Page snapshot compared each frame; full pass only on change. `construction.page` reads 1 with the menu closed, so the old gate never closed. |
| making_fuel_tool_tint | 23.2 | ~0 | reqscript hoisted to file scope; TOOL walk only on DF's new-colour signal and a slow backstop. (Now RM's refinish-sprite-tool-tint.) |
| making_fuel_fuel_access | 13.7 | ~0.5 | Jobs with no fuel slot decided once (skip memo); per-material class memo; no IN_PLAY walk for a key absent on purpose. |
| making-fuel-drain-key | 12.3 ms/call | ~0.3 | Keys counted by id (ledger); clone position remembered; engine held at file scope. |
| rot keys / cremate keys | 9.85 / 5.92 ms/call | 1.27 / 0.25 | Ledger; one rot or remains walk shared by every site. |
| stone-mat / tinder | 5.0 / 4.6 | ~0.3 / ~0 | Created event enabled by each file itself; sweep became a slow backstop. (Stone twins are now RM's refinish-material-aggregate.) |
| coal watcher | 6.2 | small | 100-frame backstop; one field read per bar. |
| hide watch | 3 to 4, then 5 to 10 by 2026-09-26 | not yet measured | Rebuilt 2026-09-26: no every-frame poll and no full sweep. Butchery runs on the item created event with a 100-frame tail backstop; the remainder look checks the watcher's own stacks every 30 frames instead of taking every reaction job from the dispatcher. |
| hide sprite trace | 2.6 | retired | Trace was a log only, off by default. `making-fuel-hide-sprite` was retired with the glob hides, 2026-09-26. |

## Loop cost, before and after (2026-10-02)

Measured with DFHack's own timers (`print_timers`) and refinish-section-probe on region4, sessions of three to six minutes. Load time went from 15.3 s to 4.68 s in the same work (the ledger's fingerprint, one script lookup per run, signatures once, the scan's minting loop, the permission evaluator's single civ list, the entity stage's handover).

| Loop | Before | After | What changed |
|---|---|---|---|
| coal watcher | 2,159 ms a session | 186 to 359 | New items read off the end of `items.all`, which is in id order; a waiting list for bars left alone; the bar backstop sliced, 2,000 bars a poll. |
| tinder watcher | 1,840 ms a session | 137 to 282 | The same three parts, 1,000 tools a sweep. |
| binder watcher | 0.82 ms a maker job, 7.86 ms/s | 0.02, 0.2 ms/s | `item_next_id` read at each poll marks where a job's output starts; no walk of the workshop's contents. |
| tool tint, the walk | 13.3 ms, 30 at worst, every 1,000 frames | slices of 0.6 to 0.7 ms, 5 at worst | New tools read every poll; the backstop sliced, kept in step by the last tool read; a colour found gone marked unmatched, so its leftover entry asks for no walk. The flat fields' one colour is the lowest in play. |
| stockpile windows, the full walk | 46 to 48 ms, 56 at worst, every 4,000 frames | slices of 3 to 3.4 ms, 8 at worst | The renewal pass (THE RENEWAL, A SLICE A TICK): every count reads the known list, and the backstop runs a slice a tick through the full walk's own per-item code. |
| save hook monitor | about 2.0 ms/s | about 1.7 | The focus string asked only while `options.open` is set (2,145 frames with the screen up, no disagreement), with a tripwire every 100 frames. |
| opening the options screen | 273 to 279 ms, 386 at worst | 4.0 ms, 7 at worst (the tool record 1.5, the ledger 1.2) | The tool record kept in memory, the ledger's sizes read first, the two scripts found once a data cycle. |

Bugs found and fixed along the way: access adopted the surviving menu key at start and then forgot its id, so the coal watcher could convert the key into a visible coal bar; a key absent on purpose triggered a full item walk every 5 frames; the old job polls read `job.id` after `removeJob`; the fuel bank was never saved (see banks).

## The module engine (refinish-module-engine and family)

Modules register a listener; at the token call the engine collects every module's payload (JSON files or Lua tables), validates it, and injects it.

- **Validation, entry by entry** (refinish-module-validate). Materials, tools and reactions are checked one at a time. A bad entry is left out and named; the module runs with the rest. A module is refused whole only for an identity fault (no prefix, a colliding prefix) or when nothing valid is left.
- **Knock-on omissions.** A reaction naming a left-out material or tool is dropped and named. A reaction whose reagent names a tool that is not injected is left out, never left as an open slot that accepts any tool (81 such slots were built on 2026-09-25 before this). A product that cannot resolve is skipped rather than shipped as the wrong thing (an unresolved builtin once shipped as index -1, magma); a reaction left with nothing to make is left out. Builtin materials resolve by their own name (water in FILL_WATER_BARREL).
- **STEP 1.5, the catalog.** A registration whose module block has `catalog = '<FORM>'` is a catalog form. It is kept only when some module lists that name in its module block's `requires`, and each form a module asks for joins that module's `depends_on`, so the form is injected first. A form missing or refused never shelves the module that asked; only its reactions naming the form are left out. The log's `Catalog:` line lists what was requested and kept. The four module blocks of a registration are walked by index: ipairs stopped at the first nil and hid every form until 2026-09-25.
- **STEP 2.5, the aggregate twins,** pushed after the catalog and before any module's materials.
- **Per-module injection** in dependency order, alphabetical where the graph does not care, each step under its own pcall: the sprite file root first, then tools (ahead of reactions, which resolve tool subtypes at build time), materials, reactions, buildings.
- **The tool record and restore** (refinish-tool-wash). See THE MATERIAL LEDGER AND THE TOOL RECORD below. Until 2026-09-25 each prefix replaced the record and the first restore consumed it, which turned every tool not owned by the first injected registration into a jug.
- **The lifecycle** (MODULE LIFECYCLE, 2026-09-30). A module may return `start` and `stop` in the table its listener returns. `start` runs at the end of `run_module_pipeline`, in injection order, only for accepted modules; `stop` runs first thing in `clear_module_assets`, in reverse order, only for started modules. Every unload path passes through there: the save hook's save & continue unload, the hotsave's clear, manual and hard shutdowns and the map unload failsafe. A rejected module that carries a start hook is named after its rejection: `Not started: rejected above, so none of its scripts run this session.` Until then Making Fuel started its scripts inside its own token call, before validation, and stopped them only at map unload: a rejected Making Fuel kept every watcher running and looked loaded, and every watcher polled on through each save with its data out of RAM. Making Fuel, Making Concrete and the advanced template use the hooks; a module without them works as before. Every Making Fuel stop was checked before the move: none writes or deletes stored data, and nearly every state it resets is one its own start already resets at each data cycle.
- **A registration's data folder** comes from its materials or buildings file, or a Lua registration names it as `data_dir`. FILE sprites resolve against it.
- **One module block per Lua response.** A module whose listener returns one table hands the engine one module block; anything declared in another file's block (Making Fuel's `requires` lives in its tools file) must be gathered into it by the listener.
- **Tools-only payloads** take their name and dependencies from their tools block.
- **Shutdown** stops every started module, then sweeps every module's assets and RM's own core assets (the REFINISH_CORE_ sweep, which also removes the aggregate twins).

## RM's core payload (refinish-core-payload)

RM's own assets, injected through the module engine like a module's. Registered at refinish_steel's load with no mod id, so they are broadcast in every world. The engine refuses any prefix stemming from `REFINISH_STEEL_`. Each registration is independent, so one failing takes nothing else down:

- **REFINISH_CORE_** (always): the dust tool, `REFINISH_CORE_DUST`, Making Fuel's DUST field for field, vanilla art.
- **Catalog forms** (only when requested), `REFINISH_<FORM>_TOOL`: GRAVEL (the gravel tool, 600 and stacking since 2026-10-07, a quarter boulder at 2500 until then; with REFINISH_GRAVEL_CRUSH and REFINISH_GRAVEL_CRUSH_COMMON at the mason's workshop, one boulder into twelve gravel and the rest as dust, measured: 14 from a boulder, declared whole; and the aggregate twins pushed while GRAVEL is carried), the byproducts SAWDUST, BARK, SCRAP, CULLET and HEAP, and CRUST. HEAP (2026-10-07) is the heap tool, 600 like gravel so a recipe can take either as an aggregate, and carries RM's slag, REFINISH_HEAP_SLAG; Making Fuel's manure and compost are heaps too. It replaced the WASTE form and its REFINISH_WASTE_SLAG, which are gone. CRUST has no tool since 2026-10-06 (gall is paid in RM's dust) and stays only to carry its material, REFINISH_CRUST_GALL. SCALE was deleted 2026-10-05, never injected and paid by nothing. The vessels SMALL_BOTTLE, LARGE_BOTTLE, SMALL_CASK, LARGE_CASK and VAT were removed 2026-10-07. Moved field for field from Making Fuel's tools JSON. Only shared content lives here: Making Fuel's fuels, feedstocks and keys came and went back on 2026-09-25, and BRIQUETTE and CINDER were dropped. A tool without no_default_job is forged by DF's own job: refinish-module-evaluate-permissions grants the fort's civ every tool whose id starts with a registration's prefix and lacks no_default_job. A form that borrows a vanilla tool's look declares `graphics.donor`, applied by refinish-sprite-engine at injection; refinish-tool-graphics.lua's DONOR_MAP, which did that from a core file, is empty since stage 4.
- **RM's own data folder,** `refinish_steel/data`, found at the token call with `scriptmanager.getModSourcePath('refinish_steel')` and handed to the engine as each registration's `data_dir`, so sheet art reads RM's images (refinish_byproducts.png and the rest, copied and renamed from Making Fuel's sheets). Unresolved: one WARNING, forms keep their base art.

A module that uses a core asset outside the catalog declares `depends_on = { 'REFINISH_CORE_' }`; a module that uses a catalog form lists it in `requires`.

## The loop dispatcher (refinish-loop-dispatch)

One loop that runs other loops. Loaded at refinish_steel's load, so modules can subscribe during the pipeline: `subscribe()` works while it is stopped. One of RM's services, which follow the data (below): started at the end of refinish-startup and of the hotsave restore, stopped before any clear and at map unload. `stop()` drops every subscription, and every service and module subscribes again in its own start, so a stop and start loses nothing (nine subscribers before and after every save in region4, 2026-09-30).

- `subscribe(name, spec)`: `spec.fn(jobs)` is called; `spec.every` (frames) or `spec.tier` (`frame` 1, `fast` 5, `steady` 10, `slow` 100); `spec.jobs` is `true` (every job) or a predicate on the reaction name and job type (only matching jobs); `spec.paused`. Returns false and a reason on a bad spec. `unsubscribe(name)`, `start()`, `stop()`. Published as `_G.refinish_dispatch_api`.
- One job walk per tick for every subscriber; only reaction jobs have their name read.
- Each subscriber is a profiler row `d:<name>`; the dispatcher's own share is `d:refinish-loop-dispatch`. The profiler's `P.self_timed` set keeps the tick from being counted twice. Since 2026-10-02 DFHack's own timers carry the same names (`dfhack.internal.recordRepeatRuntime`), and so do RM's loops of their own (refinish-save-hook-monitor, refinish-jit-watcher, refinish-calendar, refinish-menu-icons, refinish-furnace-render); until then three quarters of the Lua timer time in `print_timers` was unnamed.
- Subscribers: access, still, tank fast poll (5), rot and cremate (10; since 2026-09-26 they seal new jobs at posting through onJobInitiated, so nothing rides the every frame tier with a job walk), branch spawner, the adaptive engine (10), and RM's job units watch, every frame with no job walk, so it runs ahead of every slower subscriber (2026-10-09). Each keeps its own loop as the fallback when the dispatcher is absent.
- Making Concrete's mix watcher (10) rides it too, since 2.0; its 1.x sand watcher is gone.
- Still on their own loops: the hijacker memo (100, now only for its product guard), the tank slow poll, and the hide watcher (the item created event, a 100-frame tail backstop and a 30-frame look over its own stacks). It left the dispatcher on 2026-09-26: it only needs the jobs its stacks are in, which each stack's JOB ref names directly.
- A shared UI snapshot was assessed and dropped: the every-frame UI loops read different state, and only the hide sprite read focus strings (retired 2026-09-26).

## Work order units (refinish-job-units)

Every unit a work order's job finishes, reported on the tick it finishes to everything that waits for job completions. Since 2026-10-09.

- **Why:** a work order keeps one job per workshop and resets it in place after every unit, the way DF resets a repeating job, but flagged by_manager rather than repeat (measured 2026-10-09: jobs 7654 and 7655 kept their ids through three units each). DFHack's completion event reports a job still in the list only if it repeats (EventManager.cpp), so it reported a whole order as one completion, its last unit. Every completion listener saw an order as one job: work order bins and blocks paid no byproducts at all.
- **How:** a work order's job is noted at posting (onJobInitiated), by a backstop every 100 frames and by a scan at start, and found again through its own workshop every frame, paused included. A unit is done when the job's completion timer goes from 0 to -1 with the job still in its workshop: DFHack's own test for a repeating job's unit. Each subscriber's handler is then called with the live job, lowest order first.
- **First in the tick:** the watch rides the dispatcher's every frame tier, so a unit is reported before any slower poll on that tick can move an item number mark past its products (shown in a mock, 2026-10-09: with the slower polls first, a block unit read "nothing out, 5000 lost").
- **Subscribers:** byproducts (order 10, first, so it measures what DF made before anything is added to the workshop), reaction outputs, melt and bricks, and Making Fuel's hijacker, access, tank fuel, still, hide watcher and binder watcher. Each keeps its own onJobCompleted registration: ordinary and repeating jobs, and an order's last unit, are DFHack's to report, and without this service nothing changes.
- `subscribe(name, fn[, order])`, `unsubscribe(name)`, `start()`, `stop()`. Published as `_G.refinish_job_units_api`, at load, so modules subscribe in the pipeline; started and stopped right after the dispatcher. One DETAIL line per unit names the job and the new items in its workshop; `refinish-job-units status` lists the subscribers and the jobs watched.

## RM's services follow the data (refinish_steel)

The dispatcher and the services riding it (job units, byproducts, tool tint, the aggregate twins' runtime, the organic registrar, stockpile windows) run only while RM's data is in RAM. `start_services` and `stop_services` in refinish_steel.lua, published as `_G.refinish_services`, carry them: started at the end of refinish-startup (map load, the save hook's reload, a manual start) and last in the hotsave restore; stopped first thing in refinish-shutdown and at the hotsave's clear, before any clear, and at map unload. A second start or stop does nothing. Until 2026-09-30 they started at map load and stopped at map unload only, so they ran through every save: the tool tint walked binder items whose twin materials were out of RAM, and the aggregate read past the end of the shrunken inorganics.

What each stop does, checked before the change: the byproduct service drops module registrations and keeps core's (the modules register again as they start); the organic registrar wipes every claim (Making Fuel's start makes its claims again); the stockpile windows close an open window first, handing the twins' flags back while the twins still exist (`window closed after 325 frames (RM stopping); 2109 flag(s) put back`); the tool tint resets its caches; the aggregate unclaims its own window claim, which its start makes again.

## Job surgery (refinish-job-surgery)

The filter rules in one place: append at the end only; remove only what you own, by what it is; never under an attached item unless forced; walk downward so an erase never moves a slot still to visit.

- `holds_nothing(job)`, `count(job, owns)`, `append(job, proto)`, `erase(job, owns, { limit, keep_first, force })`.
- Access routes every fuel slot change through it; the adaptive vessels' `collapse_vessels` routes its filter erase through it.
- **What a vanilla job does with an appended item** (measured 2026-10-08, making-fuel-butcher-vessel-probe, two runs). A ButcherAnimal job given an empty vessel filter after the corpse's own fetched the vessel after the corpse, both held as role Reagent, and when the job ended the vessel was left in the shop as a building item, not consumed (a bucket, then an iron jug). A SlaughterAnimal job posts no item filters, only a UNIT_SLAUGHTEREE ref: a filter appended at index 0 was never fetched, because the job completes the moment the animal arrives and its parts appear in the shop. Furnace fuel slots are the other case: DF fetches and consumes them (making-fuel-access.lua). A vanilla job asking for something that does not exist is cancelled within a second, so an optional item may only be appended while one is free.

## The reaction key ledger (refinish-reaction-keys)

The standard form for "this reaction reads red when X is not here". A key is a hidden tool whose material carries the reaction's class, so the menu lights only where a key is.

- `ledger()` returns a ledger: `track(slot, id)`, `forget(id)`, `live(id)`, `at(slot)` (a job's key first, so trimming extras never takes the one a job is using), `scrap(it)` (forgotten only when the remove took), `strays(present, f)`, `pend(id)`, `settle(f)`, `reset()`.
- `sites(kind_fn)`: host buildings cached; rescanned when the building count moves or every 10 calls. Helpers: `busy(it)`, `at_pos(it, p)`, `scrap(it)`.
- Used by rot (census at session start, since its key material is JSON-declared), cremate and drain (purge at session start, since their key indices cannot be trusted across a cycle). Each watcher's key is its own Making Fuel tool: a watcher sweeps its key tool by subtype and removes keys it does not recognise, so keys never share a tool (they were RM catalog forms briefly on 2026-09-25, and came back).
- Its header carries the key lessons: a key is a tool (a boulder key landed in the building materials list), one key per menu light, none anywhere else, match by subtype for sweeps, collect first and remove after, `dfhack.items.remove` is deferred (the 96 repeated lines), no pcall inside an item loop.
- The rot reaction's reagent carries `nearby`, which is what makes a key light only its own building; keys are placed per building for that reason.

## Persistent banks (refinish-persist-banks)

A bank per name per fort, restored from site data on first open, every change written through. `open(name)` returns the bank; `_G.refinish_banks` holds them. The table handed out is a proxy (`__index`, `__newindex`, `__pairs`): `next` and `#` do not work on it, and nothing uses them on a bank. `making_fuel.lua` opens `MAKING_FUEL_BANK` before any script starts; `_G.refinish_fuel_bank` is the handle. Before this the bank lived only in Lua and was lost on every map unload or relaunch. A new fort opens its own, so nothing leaks between forts.

## The byproduct service (refinish-job-byproducts)

Measures what a covered job destroys and pays it back as forms, with or without any module.

- **How it measures:** a feedstock memo (the attached inputs and their total volume) on the dispatcher at 100 frames, with the mark, DF's next item number, read at every poll while the job holds its items. At completion, DFHack's or, for each unit of a work order, the job units service's (above), output is what the workshop holds numbered at or above the mark, minus anything this service made; loss is input minus output. Until 2026-10-09 the memo kept a snapshot of the workshop's contents instead and heard of a work order only at its last unit, so one memo stood for a whole order and anything carried in counted as output: a bin read 6000 and a mechanism 18000, and work order bins and blocks paid nothing.
- **RM's own payment, first:** dust at stone 0.40, gem 1.00, metal 0.60 of the measured loss; gravel 0.60 of stone loss when the GRAVEL form is carried; slag heaps for all of a smelt's measured ore loss when the HEAP form is carried (since 2026-10-07; Making Fuel paid slag until then). A stream whose unit is AGGREGATE is counted in the gravel tool's declared size, 600, so gravel and slag stay one size. Stone is the largest loss in the game (a 10000 boulder becomes four blocks); dressing makes coarse spalls and fine dust, so it splits two ways. Gem cutting is all fines.
- **The consistency rule:** per class, core recovery is applied to the full loss first; module recoveries share what is left, and if their sum is larger every module stream in that class is scaled down, logged once. Core is never reduced, so RM's output is identical with or without modules.
- `register(owner, spec)`: `spec.classes[class] = { mode, recovery, cap, streams = { { form, share, unit, vol, mat }, ... } }`, with `spec.value` and `spec.is_fuel` for pricing (VALUE mode keeps the module's valuation hook, which is how Making Fuel's fuel curve stays module policy). A form RM already pays in a class is refused to modules. `unregister(owner)`, `credit(mode, form, bid, amount)`, `start()`, `stop()`. Published as `_G.refinish_byproducts_api`.
- A stream with no `mat` inherits the feedstock: "a feather wood door gives feather wood bark and a microcline block gives microcline dust". Balances are banked per form per building.
- No silent returns: no memo, no class, nobody pays, each said once with the reason; no loss is said for every job, as every payout is, with the job's id, what went in and each kind of item counted as output (2026-10-09; said once a job type until then, so a second bin that measured the same left no line). The cap is a safety valve, not a governor.
- **Byproduct Rate** (2026-10-07): an RM setting, 100, 75, 50, 25 or 10 percent (`refinish_config_byproduct_rate` in site data), scales every stream's payment, core's and modules' alike, so players can turn output down. The Byproducts switch still decides which forms pay at all.
- **Building construction pays nothing** (decided 2026-10-05): it makes no sense for a building to shed byproducts.
- **The readout** (a bank provider, order 30) lists every stream a building's jobs can bank, at zero until it banks (2026-10-05). Which classes a building takes is fixed per workshop and held by DF's own enum names, resolved guarded (BUILDING_CLASSES): carpenter wood; mason stone; metalsmith and magma forge metal; jeweler gem and glass; craftsdwarf stone, wood and bone; bowyer wood; mechanic stone; siege workshop wood; leatherworks leather; clothier and loom cloth; glass furnaces glass; smelters ore. Only a class some registered stream pays makes a row; OFF shows no bank, NO DUST no dust row. Any other balance shows once it has paid there since the readout landed (its unit saved beside it): balances older than that put dust and scrap rows on buildings that bank neither (seen in play 2026-10-05). A dust row carries its class, "stone dust", "metal dust", "bone dust", while scrap, cullet and gravel stand alone (2026-10-06). Glass worked at the jeweler is glass work, so the jeweler banks cullet beside gem dust.

## Stone aggregate twins (refinish-material-aggregate)

One twin per stone, `REFINISH_CORE_AGG_<stone>` (MAKING_FUEL_AGG_<stone> while it was Making Fuel's), carrying the AGGREGATE class so recipes can take gravel by class. Pushed at engine STEP 2.5 in one fixed step, because an item stores a mat_index; removed LIFO by the REFINISH_CORE_ sweep. Gravel hops onto its stone's twin. Twins must never carry IS_STONE (refinish scan would count them).

## The organic stockpile registrar (refinish-stockpile-organic)

Registers injected inorganic materials into organic stockpile categories so they haul and store. Categories: Glob (fill any) and PlantPowder (fill all).

- `claim(owner, category, select, opts)` (`opts.may_be_empty` hides the entry when nothing is present), `unclaim(owner)`, `sync()`, `settle()`, `start()`, `stop()`. JSON materials can instead declare `organic_category`. Published as `_G.refinish_organic_api`.
- Measured rules kept in its header: settings vectors are grown to target and never shrunk; settings are numbers, not booleans (`vector<char>`); both directions of the index are required; the reverse index is rebuilt every sync; faults are said once; dyes must be plant materials (the inorganic path failed both ways).

## Tool tint (refinish-sprite-tool-tint)

Dresses a tool per material from a char map pattern, for tools DF's own tint fails on. A tool declares `"tint": "<pattern>"` in its JSON or its Lua registration; patterns live in refinish-sprite-art-forms (gravel, and sawdust, the heap that sawdust and Making Concrete's cement wear) with the rules for converting a sheet cell. A change in the module registry resets every cache. `pass()`, `start()`, `stop()`. The colour key is measured: a cache entry's color_index is the material's state_color.Solid plus one. Dressing runs every frame, because DF rebuilds entries with its own art (the stock powder pile these forms register as their base) and each rebuild shows until the next dressing; a REDRESS line counts how often. An art may register a blend profile, `register(name, charmap, profile)` in refinish-sprite-art, that lands each sprite at its material's own lightness instead of the shared knobs, which put back the art's luminance and so give every grey material one grey. How every art colours is one switch, the mode, set with `refinish-tint palette` or `refinish-tint blend` (`ramp=a|b` picks the palette ramp). Palette, the default, colours the way DF does: DF's item art is drawn in the key greys of palette row 0 (vanilla palettes.png), and DF swaps each for the same column of the material colour's own palette row, which every descriptor carries live as `palette.color` (18 colours: ramp A muted, ramp B richer). RM's RAMP is exactly ramp B's keys, so a char map's symbols are palette columns. Blend is the multiply with the material's lightness put back, the material's true colour, on the shared knobs or an art's profile (gravel and sawdust have one; profiles are blend numbers only). In palette mode an art can be shifted whole steps along each material's palette (`refinish-tint gravel shift=1`), for art drawn darker or lighter than DF's own (median mean level 3.12 over 469 vanilla item cells); gravel is drawn at 2.10 and sits one step up by default, which lands alunite gravel at 113:74:102 beside DF's alunite dust at 117:81:106. The report gives each art's level. The art module's `forget()` wipes its cache and moves `generation()` on, which the tool tint compares every poll, so any change lands on the next frame. refinish-palette-probe rewrites the palette rows themselves (test, custom, vanilla). In play (2026-09-25) many of DF's own sprites followed, so DF reads the rows live, though boulders and blocks did not; a global vanilla or custom switch is shelved, and RM's art uses the rows as DF loaded them.

## The adaptive reaction engine (refinish-reaction-adaptive, refinish-reaction-adaptive-vessels)

Runs reactions whose products and quantities depend on what went in: swapping, settling, the orphan sweep, and (in the vessels half) container sizing, liquid writing, drains and the null liquid reaper. Split from Making Fuel's ghost; Making Fuel's valuation is the only part that knows what its things are worth.

- Serves every registered module with its own provider, config, bank and prefixes; refuses only a prefix collision. Without the vessels file it refuses all registrations.
- `register(owner, spec)` with `spec.valuation` (the provider) and `spec.reactions` (the module's reaction table, from which the provider derives which reactions are adaptive). `unregister(owner)`, `register_alias(clone_code, base_code)`, `settle(id, s, force)`, `resweep_orphans()`, `stop()`. Published as `_G.refinish_adaptive_api`.
- The provider interface (Making Fuel's is making-fuel-adaptive-valuation): `config_for`, `streams`, `value_of`, `tars_in`, `fluids_of`, `write`, `traits`, `DEFAULT_PROFILE`, `bank`, `bank_key`, `REACTION_PREFIX`, `CURRENCY_MATERIAL_PREFIX`, `setting`, `dial`, `is_fuel_slot`, `start_banner`.
- Logs as REFINISH_METAL REACTION_ADAPTIVE.
- **Runtime clones must be adopted.** A reaction cloned at runtime (the drain key's per-retort drains, the tank's per-building fill, install and atomise clones) is invisible to the engine until its maker calls `register_alias(clone, base)`, re-asserted every poll because the engine rebuilds its tables each cycle. An unadopted clone mints product nobody paid for, which the vessels' reaper pulls back out (`REAPED unpaid`). Makers read `_G.refinish_adaptive_api` at the moment of each call, never holding it: a handle kept from a file's first load can be a copy that is no longer the live engine once a save load changes DFHack's script paths (DFHack's own warning under `reqscript` in Lua_API.txt). On 2026-09-30 both makers' held handles aliased into tables the live engine never read, for a whole session, while the same call from the console, reading the global fresh, adopted both bases.

## The reaction outputs service (refinish-reaction-outputs)

Makes a reaction's outputs out of what went in, and stacks them, for every custom reaction: RM's, a module's or the raws'. Since 2026-10-03.

- **Outputs follow inputs.** A product that takes its material from a reagent gets the material of the FIRST item DF collected for it, so a slot holding several materials made everything of the first (two trees' branches split into kindling all of one tree, in play). While a job runs, the items held for each such reagent are measured by volume and material; at completion, if the reagent held more than one material, the job's new items of that product are shared out by those volumes (largest remainder; a lone item to the largest share).
- **Stacks.** New items of a tool that declares `stack = true` are merged per material, one stack each.
- **Measured stacks.** A product marked `measure = true` (the crushers' dust), and RM's grinders by code, are sized from what the source measured, in the tool's own unit, with DF's count becoming how many stacks.
- **When:** DFHack walks event types in enum order, so every JOB_COMPLETED handler runs before any ITEM_CREATED handler of the same tick (EventManager.cpp, read 2026-10-03): the sharing and merging are done before anything that acts on a new item sees it. An output something else already changed is left alone, said once per reaction.
- **How it sees a job:** the dispatcher hands it custom reaction jobs every 10 frames; a memo keeps each job's workshop, the item number line and the measured inputs.
- **The readout** (a bank provider, order 40): every measured product a building makes is a row, one per material once a material holds a remainder, and one under the product's own name at zero while none does (2026-10-05). A product declared `whole = true` beside `measure = true` gets no zero row: its measure always comes out whole, as the crushers' dust does (25 from every boulder), so it never banks (2026-10-06). A remainder, if one were ever left, shows like any other.
- `start()`, `stop()`; an RM service. Measured in play (2026-10-03): branches split by tree type, gravel merged, crush dust sized by measure.

## The material class service (refinish-material-classes)

Gives existing materials a reaction class while RM's data is in RAM: the first piece of RM's runtime editor. Since 2026-10-03; words for requirement text since 2026-10-05.

- `_G.refinish_class_api.grant(owner, { class = 'POZZOLAN', inorganic_flags = { 'IGNEOUS_EXTRUSIVE' }, ids = { 'OBSIDIAN' } })`, from a module's start hook; returns how many materials it gave the class to. A material that already carries the class keeps its own and is not recorded, so taking grants back never removes a class the raws gave. RM's own materials are never given one. Inorganics only.
- **Taken back** by `stop()`, run first thing at every shutdown with RM's other services: before every save, at a data cycle and at map unload. One record and one sweep for every module.
- **Erased, not freed:** a class is a string allocated for it, and a material copied while it carried the class (a twin) may hold the same pointer, so the entry is erased and the string left allocated.
- A stone given a legitimate class is economic, as flux and gypsum are (accepted 2026-10-03). Measured in play: Making Concrete granted POZZOLAN to seven volcanic stones.
- **Words** (ALIASES, 2026-10-05): a reagent that declares `reads` asks for its words as its class (Requirement text, below), and every material carrying the old class must carry the words too. The reaction builder records each pair in `_G.refinish_class_aliases`; `start()` gives them once every material of the cycle is in RAM, twins included, searching the inorganics (RM's finishes, `REFINISH_STEEL_`, skipped: copies of base metals carrying no module class), every plant's materials and every creature's (FAT is on each creature's fat). A product gate turned into words (2026-10-06) is found through each material's reaction products. RM's own materials are searched, unlike a grant (the slag's classes, the gall's). The words are recorded with the grants, taken back at `stop()` the same way, and the table emptied for the next injection. A material made after start that carries an aliased class would miss its words; none is today. Measured: 36 sets of words on 1977 materials in 63 ms; 39 sets on 1980 in 94 ms.

## Requirement text (READS, refinish-module-react)

DF writes a task row's requirement lines, the hover and a red row's objection alike, from each reagent's own fields, so a reagent gated by a token prints the token: "4 FINE_COAL bars", "Tar-containing item", "SEED_MAT-producing". Measured 2026-10-05 with making-fuel-reads-probe: changing the class string changed both lines, and the row stayed white with the materials carrying the new class. Since 2026-10-05.

- **`reads`** on a reagent is the words DF prints for it; DF adds its own item word after them. A contained reagent takes the words as its code, and every product naming that code follows it. A reagent gated by a class takes the words as its class, given beside the old one on every material carrying it (the class service's words, above). A reagent gated by a product with no class (2026-10-06) has its gate turned into a class of words carried by every material with the product: "seed-bearing plant". A reagent with both keeps its product gate: a reagent holds one class.
- **One set of words stands for one class or product.** Words already standing for another are refused, ERROR, and that reagent keeps its own class and code. Without the class service a gated reagent keeps its token, one WARNING a session; a contained reagent's code still takes the words.
- **Validation:** refinish-module-validate.lua requires `reads` to be a non-empty string; preflight.py also checks that a lever prints it and that each set of words stands for one class or product across every file it checks.
- **Classes RM and the watchers write themselves are words too.** The metal grinder's class is "unfinished metal"; each finished-metal grinder's is "finished <base name>", the base's id after it where two bases share a name; refinish-clear-reaction.lua takes them back by the exact words (the finished ones published on `_G.refinish_grind_fin_words`), never by a prefix. Lowercase classes are RM's alone: raws tokens are uppercase, and a module's words are taken back before any clear runs. Making Fuel's drain clones ask for "number <building id> overfill drain" ("Requires number 5 overfill drain tool"); its rot and cremation keys take words through `reads`, and their abort seals ask the job's own reaction for its class.
- **Still a token:** a reagent gated by both a class and a product shows its product, if DF prints it (unmeasured); other mods' reactions asking builtin coal print DF's own "Refined coal".

## The finish mint (refinish-mint-finish, refinish-mint-finish-watch)

Mints RM's finishes once a fort can make them, instead of every finish at load. Since 2026-10-02.

- **Why:** with every finish at load (61,392 materials, 99,574 reactions, 81 bases), New work order built 4,922,677 templates and took 13 to 16 s to open, locking DF up with every base on; the material picker listed 62,606 inorganics, about 5 s; the forge's item categories held 61,442 rows each.
- **A pair of base metal and dust** is minted once the fort has had both, because a tool reagent gets no magnifying glass: there is one reaction per base and dust. refinish-scan still builds the whole blueprint as the catalog.
- **The roster** (site data, REFINISH_STEEL_FINISH_ROSTER): S B (a base metal's first bars), S D (a dust's first appearance) and M (a finish minted), in order, never removed. Step 4 mints the M lines in roster order, so the replay rebuilds the session's layout; where it cannot, the ledger moves objects by name. A line the blueprint cannot make this cycle is skipped, never dropped.
- **Reactions** are rebuilt each load from the S lines, grouped and sorted as the full set always was; a pair minted in play is appended, and saved jobs are pointed back at their reactions on the next load.
- **Who calls what:** Step 4 `load_materials()`; Step 5 `set_shell()`, `minted_reactions()`, `build_reaction()`, `folders()`, `build_placeholder()`, `finish_load()`; Step 6.5 and Step 7 `_G.refinish_mint_finish_on_demand`, a finish an object wears minted instead of the object parked; Step 6.7 `reconcile()`; in play, the watch calls `notice(kind, id)` and `dust_subtype()`.
- **The watch** sees a bar or dust the moment it exists: `eventful.onItemCreated`, plus a poll reading what was made since the last one off the end of `items.all` (which catches trader, migrant and invader goods); a bar still a caravan's waits until bought. No walk of every bar: one walk of 60,000 bars a poll cost 9.3 ms a second.
- **Placeholders:** a folder with no reaction kills the task panel, so each kind folder in the forge gets one placeholder reaction once a finish of that kind exists; the forge menu replaces its row, and the manager's list has them taken out.
- **Finished-metal grinders** (2026-10-03): one per base with finishes, at the quern and millstone, under "Grind finished metals", keyed by a class every finish of that base carries (`build_fin_grinder`), written as words, "finished <base name>" (2026-10-05). The metal grinder's class on every finish slowed the picker, which that class exists to keep short.
- **Defaults** (2026-10-03): with nothing saved, every base with a refinishing path is on (it was steel alone), and Protect Bases is off, since it prevents grinding metal entirely.

## The forge menu (refinish-menu-forge)

Files every RM finish in each of the forge's item categories into one folder: weapons and ammunition > refinished metals > steel > colour-based > amber steel > its job list (layout decided 2026-10-03). `start()`, `stop()`.

- The base and kind levels are always there, so the path is the same however many bases are selected.
- A kind folder's placeholder row is replaced by every finish of that kind of the base, taken from the blueprint, because DF's category list carries a material number in 16 bits and loses everything past 32,767 (measured 2026-10-02: 29,838 rows came out as rock).
- The folder token is cleared so a press opens the metal's jobs, and put back once the jobs are open, so Back returns to the folder. A job row that does not name the metal opened is taken out and logged.
- Every Back entry is built from DF's own: built with its fields zeroed, it read Cancel in play.
- **Ownership:** DF deletes what is in `button` when it rebuilds, so every button is deleted exactly once, by exactly one party, and no list is touched unless DF built it; `filtered_button` holds stale pointers while the panel is closed. The buttons a filed category list leaves behind are deleted over the frames after it opens.
- The probe's measurements of DF's task menu are in the script's header (WHAT THE PROBE RUNS MEASURED).

## The melt service (refinish-melt)

Measures every melt and keeps what is under a tenth. Since 2026-10-04.

- **DF's store:** `building_furnacest.melt_remainder` keeps part bars per inorganic, in tenths of a bar; DF makes a bar at 10. DF credits 3 tenths per point of material size (every RM form: 3 tenths a unit, measured on fourteen melts), and many vanilla items return more than they cost.
- **The measure:** nine tenths of what is in what was melted. RM's dust and scrap hold their volume; anything else the smaller of its cost to make and its own volume (a gold table: 1800 of cost, volume 3000). A type with no cost known is credited nine tenths of the lesser of its volume and DF's credit, said once per type. DF's credit is read only to undo what DF did.
- **The remainder:** what is under a tenth goes to REFINISH_MELT, per smelter and metal by name, and is added in at that smelter's next melt of the metal. A remainder whose smelter is gone is dropped at the next start.
- **The store covers the array:** before any melt, the smelter's store is grown to the inorganics array, since a store sized before a finish was minted ends short of it.
- Melts pay no byproducts. It provides the smelter's "melt bank" section to the bank readout (order 20). `start()`, `stop()`; an RM service.

## The bank readout (refinish-bank-readout)

A panel beside the building sheet showing what the open building holds back, so a job that completes and drops nothing explains itself. RM's since 2026-10-04 (it began as Making Fuel's fuel bank readout).

- **Providers:** `_G.refinish_bank_providers.<name> = { order = <number>, fn = <function> }`. `fn(bld)` returns nil or a section: `title` (the first heads the panel, a later one heads its own rows), `rows` (bar rows `{ key, label, value, full }` or text rows `{ key, text, pen }`; keys unique across every provider) and `footers` (42 columns at most). Sections draw lowest order first; each fn runs under pcall every frame the panel is up, so it must be cheap.
- A provider registers at its own load. Today: Making Fuel's fuel banks (making-fuel-bank-readout.lua, order 10), the smelters' part bars (refinish-melt.lua, order 20), the byproduct bank (refinish-job-byproducts.lua, order 30) and the output bank (refinish-reaction-outputs.lua, order 40).
- **Every bank shows always** (decided 2026-10-05): a building that banks shows its bank from the start, every row it can bank, zero included, never invisible until something has banked. Each provider keeps the law its own way (the byproduct service and the outputs service, above).
- The flash is kept per building: keyed by currency alone, opening one furnace after another flashed every row whose bank differed (found in a mock).

## The brick service (refinish-bricks)

Pays clay bricks by volume, for vanilla's make clay bricks and RM's REFINISH_BRICK_RXN_GROG. Since 2026-10-04.

- **The measure:** clay shrinks 8% linear, keeping about 78% of its volume ((1 - S)^3, ASTM C326); grog is stone already and keeps nine tenths; a brick costs an eighth of a boulder (1250) of what is left. So a clay boulder makes 6 bricks where vanilla made 1, and 8 with 13 dust of grog (25 while dust was 100). A brick is whole: what is left under one is part of the loss.
- **The block standard behind it** (decided 2026-10-04): a cut block costs a quarter boulder, four from a boulder with nothing but labour. A molded or fired block (bricks, concrete, asphalt) costs an eighth of a boulder of what is left after its process loss: the extra steps and the fuel buy the yield.
- **How:** the poll notes each brick job's clay volume, kiln and item number line, again whenever it holds a different number of items. The grog is what the reaction asks for, not what the job holds. Two ticks after completion it makes the rest of the bricks beside DF's, each a brick of its own, in the material DF gave them.
- `start()`, `stop()`; an RM service.

## The dye service (refinish-dyes)

A mineral dye for every colour dust comes in, at the dyer's shop: two dust of that colour, a glue granule and an empty bag. Since 2026-10-04.

- **Colours read live** at the token call, from every stone, gem and metal's colour (a pattern's first colour), so a mod's colours come in with nothing written for them; the test world had 152. A finish takes its colour from the dust that finished it.
- **The dyes** are plant materials, on hosts of their own (REFINISH_DYE_HOST, a second past 200 colours), claimed for Milled Plants. The organic registrar's `claim` takes a function that lists them, called when it settles: handed a list, it refuses the claim.
- **Which dust:** a reaction cannot ask for a colour, so every material with dust carries its colour's class, REFINISH_DYE_<colour>: stones, gems and metals through the class service at start, finishes from the finish mint.
- **All at load:** every dye reaction is permitted at load. Permitted only as the fort first had a colour's dust, none showed in any menu (the module engine, above).
- `payload()`, `colour_of()`, `start_dyes`, `stop_dyes`.
- **Known limit:** a module's materials inject after the token call, so a colour only a module's stone wears has no dye.

## The save paths (refinish-autosave, refinish-save-hook, the map unload failsafe)

A save written with RM's or a module's additions in the raws arrays is corrupt, so every save happens with them out of RAM, and every load puts them back. The records that let a load put objects back (the material ledger and the tool record, below) must reach site data before the game writes.

- **Hotsave** (refinish-autosave). Pauses for the whole cycle whatever Pause on Save says (the setting decides only whether the game stays paused afterwards). Writes the ledger snapshot, stops the services, clears (modules stop first, in `clear_module_assets`), quicksaves, and restores on the frame `plotinfo.main.autosave_request` clears: the save's measured end, before any tick. If the request is never seen, or never clears, it falls back to the next tick with a WARNING. Services start last. No completion prompt: a prompt is a modal screen and held the game paused over a resume; the figures are on the status panel and in a DETAIL line.
- **The game's save & continue** (refinish-save-hook). Unloads on the frame `options.do_manual_save` rises, holds the pause from the unload to the reload (reasserted every frame), and reloads on the frame DF closes the options screen, which is that save's end: 51 frames after the countdown, both times it was measured. Then hands back the pause the player had.
- **The game's save & quit.** Nothing is unloaded by the save hook. DF unloads the map before it writes, and the map unload failsafe clears RAM there. Backing out of the save and exit choices therefore costs nothing (it used to cost a 2 s unload and a 12 s reload in region4).
- **The records,** refreshed by the save hook each time the options screen opens, because DFHack writes its data on the frame a save is requested, before any script's per-frame handler runs.
- **The map unload failsafe** (refinish_steel.lua). Stops the services, clears entity permissions, reactions and materials (each gated on its loaded flag, which the index scripts set and map load re-derives from RAM) and every module's assets (modules stopped first). It writes no tool record: site data can no longer be written at the map unload.

## The material ledger and the tool record (refinish-ledger, refinish-tool-wash)

- **The ledger** records id to index for every owned inorganic, name to pair for every owned plant material (`PLANT_ID|MAT_ID`, mat_type 419 plus its position), and each finish's base metal. The remap at load moves every object (items, constructions, buildings, dye references, history) from the index its material held to the one it holds now, by name. A finish that is no longer generated (its base metal deselected) sends its objects to the base metal and parks them; reselecting the metal gives them their finish back (10,000 parked and 10,000 restored in play).
- **Storage** is plain lines through `saveSiteDataString` (`LEDGER 2`, tokens with whitespace or % escaped). `saveSiteData` JSON-encodes its value, so a JSON string handed to it was stored double-encoded, and `getSiteData` read it back through DFHack's character-by-character JSON reader: about 60 s at 8,956 materials, which hung region2 at load. Lines read in 29 ms there; region4's 61,801 records (7.2 MB) read in about 0.4 s. An old double-encoded ledger still reads.
- **`write({ if_changed = true })`** keeps the stored ledger when the arrays stand as the last write found them. Since 2026-10-02 it reads their sizes first (the site, the inorganics, the plants and every plant's materials): the same sizes as at the last layout read keep the ledger without reading an id, 0 ms in its own log line where reading every id cost 31 to 62 ms an opening. Other sizes fall through to the exact test: the site and every inorganic and plant material id in order, read without building anything. The sizes rest on a rule (THE ARRAYS' SIZES, ASKED FIRST, refinish-ledger.lua): during play a material is only ever appended, as the tinder and aggregate twins are; whatever renames or moves one in place does it inside a data cycle, which sets the layout afresh, or sets `last_sig` to nil. The save hook's refresh, the shutdown's snapshot and the hotsave's snapshot pass it; startup's write after a data cycle never does. Before if_changed, every menu opening rebuilt an identical 7.2 MB ledger, about a second of lag outside any save.
- **The tool record** stores item id to tool code for every owned tool item, in one shared record; no item is touched (RECORD, NOT REPOINT, since 2026-09-29). At load DF brings module tools back as cauldrons, its default, because their itemdefs do not exist yet; each module's items are repointed right after its tools inject, and `settle()` names what never came back and consumes the record. Written at every clear except the failsafe, and at the options screen refresh, which since 2026-10-02 works from a record kept in memory (THE RECORD, KEPT BETWEEN OPENINGS OF THE MENU, refinish-tool-wash.lua): built in the background in about a second after each load, topped up at each opening with only the items made since and the items a script changed, and written only when that changed it. The kept record rests on a rule: a script that changes which owned tool an existing item is lists the item in `_G.refinish_tool_wash_touched` (air-dry does; nothing else changes one outside a load). The one difference from a full wash is an entry for an item the build read and that was used up before the first write; restore counts it as no longer in the world. Confirmed in play 2026-10-02: a save & quit restored 9,973 items (37 gone) and a save & continue 10,048 (46 gone), every entry its record held, no WARNING, and the save's own full wash found no tool the kept record lacked. Stored as one layer of JSON through `saveSiteDataString` since 2026-09-30; an old record still reads.

## Decisions on record

- **Dust** (2026-10-03; 200 since 2026-10-07): one dust is 200, for every class, and two dust finish a bar. Dust of one class finishes no better than another; it only comes easier or harder, and each job's measured loss decides that. A boulder (10000) grinds to 50, a bar (600) to 3, three rough gems (750) to 3 and three quarters, the quarter banked; a block and an aggregate (600 each) are 3. The size doubled from 100 because finishing was too cheap: a boulder's 100 dust finished about fifty bars. A finish that one material alone makes adds per bar: stone value / 25, metal value x 2/3, gem value x 8/5; colour finishes and shared finishes are worth their base metal. Until 2026-10-03: one dust tool finished three bars, and one dust was one bar (600), three rough gems (750) or a quarter boulder (2500), by class.
- **Dust volumes,** measured 2026-09-24: bar 600, rough gem 250, cut gem 20, boulder 10000. Powder is no longer accepted as a reagent; leftover powder in old saves stays powder. The renamed powder names lived in raws and were never saved, so nothing needed converting.
- **Every melt is measured** (2026-10-04): nine tenths of what is in what was melted, nothing rounded away (the melt service).
- **Blocks** (2026-10-04): a cut block costs a quarter boulder, a molded or fired one an eighth of what is left after its process loss (the brick service).
- **Glue is RM's, solid, as granules** (2026-10-04); Making Fuel's liquid glue, its glue boils and its liquid glue presses are retired. A recipe never takes part of a unit: a liquid unit too large for one run gets a smaller form on a tool.
- **Mineral dyes are RM core's** (2026-10-04), one per colour, built from the materials' live colours, all permitted at load.
- **Mods never cut RM's material** (2026-10-04): when a mod cuts a vanilla category RM's reactions file under, RM makes its own rather than guessing among the mod's.
- **Grinder names are non-negotiable:** every grind job is named after the material it grabbed, from a few general reactions; the per-job clone that pins the material and the one that carries the name are the same clone. The grinders are at the quern and millstone. `refinish-evaluate-dust-making` stays: it picks the grinder's template reaction by evaluation, which is the point of every evaluator.
- **Gravel:** Making Fuel's model (a gravel tool in the stone's material, with aggregate twins carrying AGGREGATE) is the standard. Making Concrete's bagged gravel material retires in its overhaul. Since 2026-10-07 gravel is 600 and stacks (a quarter boulder until then), and slag is a heap of the same size, so ratio-based recipes take either by AGGREGATE.
- **Making Concrete overhaul,** once the core services exist: tools instead of bags, gravel and dust byproducts as the main aggregate route, sand one option rather than a requirement (vanilla sand stays vanilla), varieties of concrete by route, its sand watcher's ghost retired into the core adaptive engine.
- **Keys:** consistent and effective; no sweeping across saves except where a key's material cannot survive a data cycle.
- **The retort does not burn fuel.** It is a wood furnace with jugs. It belongs to Making Fuel, not RM (decided 2026-09-25).
- **Load at the true end of a save** (decided 2026-09-30): the hotsave restores on the request clearing, the save hook reloads when DF closes the options screen; no waiting for a tick, which left one tick with RM's data out.
- **Save & quit is not unloaded by the save hook** (decided 2026-09-30), on condition that everything still works and lag stays out of places it does not belong: lag only at an actual save. Confirmed in play the same day: 466 of 466 tools restored, no remap needed, no faults.
- **The module lifecycle lives in RM core** (decided 2026-09-30): modules hand RM a start and a stop, and RM runs them; RM's own services follow the data the same way.
- **Colours are patterns** (2026-09-30): a material's `state_color` holds a pattern index; every reader goes through the pattern to its first colour, and the injector stores a colour's own single colour pattern.
- **Requirement text reads in words** (2026-10-05): every reagent a player meets says what it needs in plain words, in the hover and on a red row, through one field on the reagent and one service, never a menu rewrite.
- **Banks always show every row** (2026-10-05); a dust row carries its class (2026-10-06); a measured product that always comes out whole lists no row (2026-10-06).
- **Building construction pays no byproducts** (2026-10-05).
- **The heap is RM's** (2026-10-07): a module set cannot carry two slags, and Making Concrete's slag concrete needs the slag Making Fuel's smelting made, so the heap and its slag moved into RM, and the WASTE form went, with nothing left to carry.
- **Vessels are not RM content** (2026-10-07): the five vessel forms were removed from the core payload.
- **Log Detail is Quiet, Info and Debug, Quiet by default** (2026-10-07). Info was named Normal.
- **Byproduct Rate** (2026-10-07): see the byproduct service.
- **Blood meal was cut** (2026-10-08): slaughter, the common way to butcher, cannot collect a vessel (Job surgery, above), and blood meal spawned straight off a corpse was not wanted.
- **Every unit of a work order is a completion** (2026-10-09): RM reports each one itself, since DFHack reports a work order once (the job units service).

## Still to build

In order, with the handoff (RM_Handoff.md) as the running plan:
- Consumers before release, since nothing may accumulate without one: gypsum crystals, leather and cloth scrap, bone dust and cullet have none, and coal ash, gravel and slag have thin sinks. Gall is dust and a fertilizer since 2026-10-06.
- Not planned: the fuel system into RM (wood and tinder twins, fuel classes, the coal watcher, access gating, the fuel curve, breeze and the coal host materials). It is Making Fuel's.
- An explicit `adaptive` block on a reaction instead of inference from zero product counts; the grinders' per-material naming as an option any generalised reaction can request.
- Derived materials (the tinder twins) returned in the payload instead of pushed by background scripts, as the stone twins now are at an engine step.
- One change-detecting poll for sprite reassertion.
- The logger factory: every file's log funnel becomes one line; the per-line cost in `_G.refinish_log_event` (a file open and close, and an insert at position 1 of a 15,000 entry table) goes with it.
- The rest of the job walkers onto the dispatcher: the hijacker memo, the tank slow poll, Concrete's sand watcher in its overhaul.
- Retire the engine's per-injection `copyall` step (refinish-tool-graphics), which copies nothing since forms stage 4.
- Flux dust: reactions that take a flux boulder asking for flux dust instead. Parked 2026-10-04; which the job consumes, the slot DF rewrote or the reaction's own reagent, is not measured.
- The lifecycle manifest is deferred on purpose (see the handoff).