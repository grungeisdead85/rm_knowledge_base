# Making Concrete 2.0

> The 2.0 delivery record, kept as written. Its figures are from before 2026-10-07, when gravel became 600, dust 200, and slag a heap in RM's HEAP form (REFINISH_HEAP_SLAG, which replaced the WASTE form). The recipes now (making_concrete_reactions.json): 3 flux and 1 clay burn into 42 clinker at the kiln; 17 clinker, or 17 slag heaps, grind into 4 cement at a quern or millstone; 1 cement, 25 dust and 12 gravel make 10 concrete blocks at the mason's workshop, dwarven concrete with volcanic dust and slag concrete with slag cement.

Concrete from what a fort already throws away. Every file is whole: the module is rewritten, each Lua file from its original.

**Replace:** making_concrete.lua, making_concrete_materials.json, making_concrete_reactions.json (all LF).
**Add:** making_concrete_tools.json, making-concrete-mix-watcher.lua.
**Delete** from Making Concrete and the project: making-concrete-sand-watcher.lua (the mix watcher is it, rewritten) and making-concrete-sand-button.lua (its technique stays in the premigration backup).
**Document, whole:** RM_Handoff.md.

Both Lua files pass `luac5.3 -p` with no new global reads; preflight passes the three data files (its two warnings are the ghosts, which only the watcher wakes, as before).

## What it is

| Step | Where | In | Out |
|---|---|---|---|
| Burn clinker | kiln, fuel | 3 flux stone, 1 clay | 10 clinker nodules (RM's gravel form, clinker material) |
| Grind clinker | quern or millstone | 4 clinker | 4 clinker cement |
| Grind slag | quern or millstone | 4 slag waste (RM's) | 4 slag cement |
| Mix concrete | mason's workshop | 1 cement, 2 stone dust, 3 gravel | 6 blocks |

The mix makes **concrete**, **dwarven concrete** when every dust is volcanic (obsidian, or any stone the raws mark extrusive igneous, modded ones included) or **slag concrete** when the cement is slag cement. The mix watcher decides once all six ingredients are attached, so the result never depends on which item arrived first, and the job's name changes to what it is making. Gravel and dust arrive from ordinary masonry through RM's byproduct service; cement is the one thing made on purpose.

**Showcase details:** no containers anywhere; one mix entry, several concretes, chosen by what went in; RM's shared gravel and dust (a load order never carries two gravels); slag from any module that pays it becomes a binder; volcanic stone of any mod counts, by its raws; the cement form takes RM's cinders tint pattern, so clinker cement and slag cement each wear their own colour; the watcher rides RM's loop dispatcher instead of walking the job list itself.

## Comment audit

- making_concrete.lua: the header's description, architecture and Collect Sand button notes were descriptions of 1.x and are rewritten. The knowledge in the removed sand code (the wildcard POWDER reagent, the sentinel over a key list, two filters for one fact, why sand needs bags and the multiplier) moves to WHAT SAND TAUGHT in the header, with a pointer to the button's technique in the premigration backup. Clinker's protection from grinding moves to CLINKER IS GRAVEL.
- making-concrete-mix-watcher.lua: the sand watcher's technique, dormant ghost, cache, retry, orphan sweep and use-after-free lessons are carried verbatim. The swap rules' pozzolanic reactivity order and the obsidian and flag rules are kept, adapted to the mix; the yield tier text about bags and ratios of sand went with sand. The protection's reasoning moves to NOTHING TO PROTECT. The linked list lesson (collect, then remove after the walk) stays in serve().

## Checks after the recycle

- Making Concrete injects 4 materials, 1 tool and 6 reactions; no rejected entries.
- The mix watcher logs `Started on RM's dispatcher` and, once injection finishes, its two ghosts present and dormant.
- No SAND_MULTIPLY error, no sand or bag reactions anywhere.
- A mix with ordinary stone dust makes concrete blocks; with volcanic dust, dwarven concrete; with slag cement, slag concrete (needs a module paying slag, such as Making Fuel).

## making_concrete.lua: diff

```diff
--- old/making_concrete.lua
+++ new/making_concrete.lua
@@ -4,24 +4,90 @@
 -- MAKING CONCRETE: RM MODULE
 -- ==========================================
--- Adds cement and concrete production to the game. A complete
--- industrial chain from raw limestone through quicklime, clinker,
--- and ground cement to finished portland cement blocks and boulders,
--- with colored variants via metal oxide pigments.
+-- Concrete from what a fort already throws away (2.0, 2026-09-25).
+-- A simple material module with hooks to and from other industries:
+-- walls, floors and buildings in concrete, from waste that would
+-- otherwise be useless, without changing how people play. It grows by
+-- variety (a new recipe when a good idea comes along), not by
+-- complexity.
+--
+-- ---- THE RECIPE ----
+-- Concrete is binder, fine aggregate and coarse aggregate in roughly
+-- real proportions, 1 : 2 : 3, and every ingredient is a loose item:
+-- no bags, no barrels, no sand.
+--   coarse   RM's gravel (REFINISH_GRAVEL_TOOL) on its stone's
+--            aggregate twin, which carries AGGREGATE
+--   fine     RM's dust (REFINISH_CORE_DUST) of any stone. Crushed rock
+--            fines are a standard sand in real concrete (manufactured
+--            sand, which replaces river sand outright), and quarry dust
+--            is what crushing boulders into coarse aggregate leaves.
+--   binder   this module's cement form in the material it was ground
+--            from: clinker cement from the kiln's clinker, or slag
+--            cement from RM's slag (blast furnace slag is a real clinker
+--            substitute)
+-- Gravel and dust pile up on their own from masonry through RM's
+-- byproduct service, so cement is the only ingredient a player makes on
+-- purpose. Every input is a quarter boulder's worth and six of them make
+-- six blocks: vanilla makes four blocks from a boulder, so the mix
+-- conserves what went in, with no minimum batch and no bulk reaction.
+--
+-- ---- VARIETY FROM INPUTS, NOT STEPS ----
+-- One mix in the menu. The mix watcher points each job at what its
+-- inputs make: every fine aggregate volcanic (pozzolana, the Roman
+-- recipe's volcanic ash) makes dwarven concrete, slag cement makes slag
+-- concrete, anything else is concrete. A new concrete is a new input
+-- and a ghost reaction, never a new step.
+--
+-- ---- CLINKER IS GRAVEL ----
+-- The kiln burns three flux stones and one clay into ten clinker
+-- nodules, RM's gravel form in the clinker material: four boulders in,
+-- two and a half out, roughly the mass limestone loses as it calcines.
+-- In 1.x clinker was a boulder, which a BOULDER_ANY reagent would take
+-- (the sand grinder had to refuse it). As gravel it is inert, the mix
+-- cannot take it for aggregate because clinker carries no AGGREGATE
+-- class, and only GRIND_CLINKER asks for it.
+--
+-- ---- WHAT RM PROVIDES, AND THIS MODULE ASKS FOR ----
+-- GRAVEL and WASTE (slag, with its material) from RM's catalog, named in
+-- the materials file's module block ("requires"), and RM's dust
+-- (depends_on REFINISH_CORE_). RM injects each once for every module
+-- that asks, so a load order never carries two gravels.
+--
+-- ---- WHAT SAND TAUGHT (1.x, retired 2026-09-25) ----
+-- Sand is why this module was hard, and why 2.0 has none. Real sand is
+-- a powder, and a powder in DF lives in a bag: collection yields one
+-- unit per bag run, and the bag is a furniture item rather than a real
+-- container, so a bag boosted to several units shows no count, and a
+-- bag with its count shown stops working as a reagent. 1.x carried
+-- eight sand bags, a cement bag, two gravel bags and a water barrel into
+-- every mix, multiplied collected sand from one unit to four per bag so
+-- bags matched (making-concrete-sand-multiply, which was missing from
+-- the mod, so that multiplier never ran and logged an ERROR every
+-- session), and injected a native Collect Sand button into the mason's
+-- workshop. The lessons that outlive it:
+--   - A wildcard POWDER reagent (no mat_id) matches any powder in a
+--     bag; beside a specific cement slot DF cannot tell the slots
+--     apart and matching goes non deterministic. Resolve every
+--     material.
+--   - Match a sentinel, not a list of reaction keys: a renamed key
+--     drops out of a list silently (CRUSH_AGGREGATE became CRUSH_GRAVEL
+--     and its sand patch quietly stopped).
+--   - Two filters for one fact (a material AND the SOIL_SAND flag) are
+--     one more way to reject a valid item.
+-- The Collect Sand button's technique, native button injection into a
+-- workshop's order list with its gates and its category leak guard,
+-- lives on in the premigration backup:
+-- making_concrete/scripts_modinstalled/making-concrete-sand-button.lua.
 --
 -- ARCHITECTURE:
---   Content lives in two JSON files:
---     making_concrete_materials.json: Cement material definitions
---     making_concrete_reactions.json: Cement reaction definitions
---
---   This Lua file loads JSONs, runs value calculation if needed,
---   and registers with RM's module engine via the listener API.
---
--- SAND BUTTON:
---   Also manages the "Collect Sand" native button injector for
---   mason workshops. The injector (making-concrete-sand-button.lua)
---   is started during module boot and stopped on map unload.
---   See RM_Native_Button_Injection.md for the technique reference.
--- ==========================================
-
+--   Content lives in three JSON files:
+--     making_concrete_materials.json: clinker and the three concretes,
+--                                     and the module block's requests
+--     making_concrete_tools.json:     the cement form
+--     making_concrete_reactions.json: the cement and concrete reactions
+--                                     and the mix's two ghosts
+--   This Lua file loads them, runs value calculation if needed,
+--   starts the mix watcher (making-concrete-mix-watcher.lua), and
+--   registers with RM's module engine via the listener API.
+-- ==========================================
 local json = require('json')
 local scriptmanager = require('script-manager')
@@ -55,5 +121,5 @@
 --
 -- SUBJECT is the correlation slot: the part of the module a line is
--- about (DATA, SAND, SAND_BUTTON, SAND_MULTIPLY, SAND_WATCHER).
+-- about (DATA, MIX_WATCHER).
 --
 -- Every line reaches the log on disk. Filtering is the panel's job
@@ -93,4 +159,5 @@
 local MATERIALS_FILE = "making_concrete_materials.json"
 local REACTIONS_FILE = "making_concrete_reactions.json"
+local TOOLS_FILE = "making_concrete_tools.json"
 
 
@@ -165,268 +232,36 @@
 
 -- ==========================================
--- SAND MATERIAL RESOLVER
--- ==========================================
--- Scans the live inorganic array for a suitable sand material.
--- Vanilla DF has multiple sand types (SAND_TAN, SAND_WHITE,
--- SAND_BLACK, SAND_RED, SAND_YELLOW), all flagged SOIL_SAND.
--- Modded worlds may add more or remove some.
---
--- Preference order:
---   1. SAND_TAN (most common vanilla sand, always present
---      in unmodded worlds)
---   2. First inorganic with the SOIL_SAND flag
---
--- Returns: the inorganic ID string (e.g. "SAND_TAN"), or nil
--- if the world has no sand materials at all.
--- ==========================================
-local function resolve_sand_id()
-    local raws = df.global.world.raws.inorganics.all
-    local fallback = nil
-
-    for _, mat in ipairs(raws) do
-        if mat.flags.SOIL_SAND then
-            -- Preferred: vanilla SAND_TAN, so return immediately
-            if mat.id == "SAND_TAN" then
-                return "SAND_TAN"
-            end
-            -- Otherwise remember the first sand we find
-            if not fallback then
-                fallback = mat.id
-            end
-        end
-    end
-
-    return fallback  -- nil if no sand exists in this world
-end
-
-
--- ==========================================
--- SAND PATCHER
--- ==========================================
--- Resolves null mat_id fields on sand-related reactions to the
--- best available sand inorganic in this world.
---
--- Patches three places:
---   1. GRIND_SAND products: what the grinder outputs
---   2. Any other null POWDER_MISC product (CRUSH_GRAVEL
---      byproducts, volcanic sand ghost remainders)
---   3. MIX_CONCRETE sand reagents: what the mixer accepts
---
--- All three use mat_id = null (JSON null → Lua nil) as a sentinel
--- meaning "resolve to the best sand at boot time."
---
--- If no sand material exists in the world, GRIND_SAND is removed
--- entirely. Everything else keeps its real output but loses
--- sand byproducts and their bag reagents. MIX_CONCRETE's sand
--- reagents stay nil (engine can't resolve them = no concrete).
---
--- This runs AFTER JSON loading but BEFORE the data is returned
--- to the module engine, so the engine never sees a nil mat_id.
--- ==========================================
-local function patch_sand(rxn_data)
-    if not rxn_data or not rxn_data.reactions then return end
-
-    local sand_id = resolve_sand_id()
-
-    if sand_id then
-        local reagents_patched = 0
-
-        for _, rxn in ipairs(rxn_data.reactions) do
-
-            -- Any POWDER_MISC product carrying the null sentinel is
-            -- ordinary sand, whatever reaction it belongs to.
-            --
-            -- This used to name reactions: GRIND_SAND and
-            -- CRUSH_AGGREGATE. CRUSH_AGGREGATE was renamed to
-            -- CRUSH_GRAVEL and the branch quietly stopped matching
-            -- anything, which is exactly the failure a key list
-            -- invites. The volcanic sand ghosts then added four more
-            -- reactions that would each have needed adding here.
-            --
-            -- Matching on the sentinel instead means a new reaction
-            -- opts in simply by writing "mat_id": null, and nothing
-            -- else in this module writes that. Products with a real
-            -- material (volcanic sand, gravel) are untouched.
-            for _, prod in ipairs(rxn.products or {}) do
-                if prod.type == "POWDER_MISC" and prod.mat_id == nil then
-                    prod.mat_id = sand_id
-                end
-            end
-
-            -- MIX_CONCRETE and any other sand consumer: patch null
-            -- reagent mat_id. This is item 3 in the header above. It was
-            -- documented but never implemented, so the mixer's sand slots
-            -- stayed wildcard in RAM (mat_type -1 / mat_index -1) while
-            -- only the GRIND_SAND output ever got a real material.
-            --
-            -- A wildcard POWDER reagent matches ANY powder sitting in a
-            -- bag. With four wildcard sand slots next to a specific
-            -- cement slot, DF has nothing to tell them apart and reagent
-            -- matching goes non deterministic. Resolving the material
-            -- here makes every sand slot specific, exactly like cement.
-            --
-            -- Predicate: type POWDER, no mat_id, code starting "sand".
-            --   sand_bag_N  is type BAG      -> skipped, bags are
-            --                                   deliberately material free
-            --   sandstone   is type BOULDER  -> skipped, and it already
-            --                                   carries mat_id SANDSTONE
-            for _, rgt in ipairs(rxn.reagents or {}) do
-                if rgt.type == "POWDER"
-                        and rgt.mat_id == nil
-                        and string.find(rgt.code, "^sand") then
-
-                    rgt.mat_id = sand_id
-                    reagents_patched = reagents_patched + 1
-
-                    -- Drop sand_bearing once the material is known. It
-                    -- was introduced as a stand in for this resolution
-                    -- while the reagent was wildcard. Leaving both means
-                    -- an item must satisfy the material AND the
-                    -- SOIL_SAND flag: redundant, and one more filter
-                    -- that can silently reject a valid bag.
-                    rgt.sand_bearing = nil
-                end
-            end
-
-        end
-        log('DETAIL', 'Sand resolved to ' .. sand_id .. ' ('
-            .. reagents_patched .. ' sand reagents patched).', 'SAND')
-    else
-        -- No sand in this world, so remove GRIND_SAND entirely (it only
-        -- makes sand, so it's useless). Strip sand byproducts from
-        -- every other reaction but keep it (its real output, gravel
-        -- or volcanic sand, does not depend on world sand).
-        local removed, products_stripped = 0, 0
-
-        for i = #rxn_data.reactions, 1, -1 do
-            local rxn = rxn_data.reactions[i]
-            if rxn.key == "GRIND_SAND" then
-                table.remove(rxn_data.reactions, i)
-                removed = removed + 1
-            else
-                -- Every other reaction keeps its real products and
-                -- loses only its sand ones. That covers CRUSH_GRAVEL's
-                -- byproducts and the volcanic ghosts, which still make
-                -- volcanic sand from their own material and simply
-                -- fill fewer bags.
-                local stripped = false
-                for pi = #(rxn.products or {}), 1, -1 do
-                    local prod = rxn.products[pi]
-                    if prod.type == "POWDER_MISC" and prod.mat_id == nil then
-                        table.remove(rxn.products, pi)
-                        stripped = true
-                    end
-                end
-                if stripped then products_stripped = products_stripped + 1 end
-            end
-        end
-
-        log('WARNING', 'No sand material in this world. GRIND_SAND removed, '
-            .. products_stripped .. ' reaction(s) lost their sand products.',
-            'SAND')
-    end
-end
-
-
--- ==========================================
--- COLLECT SAND BUTTON MANAGEMENT
--- ==========================================
--- Starts and stops the mason workshop button injector. The
--- injector adds a native "Collect Sand" order to every mason
--- workshop, identical to the glass furnace's built-in button.
---
--- The injector script (making-concrete-sand-button.lua) manages
--- its own polling via repeat-util. We just call start/stop.
--- ==========================================
-
-local function start_sand_button()
-    local ok, sand_btn = pcall(reqscript, 'making-concrete-sand-button')
-    if ok and sand_btn and sand_btn.start then
-        sand_btn.start()
-        log('DETAIL', 'Collect Sand button injector started.', 'SAND_BUTTON')
-    else
-        -- ERROR: mason workshops get no Collect Sand button.
-        log('ERROR', 'Could not start the sand button injector.', 'SAND_BUTTON')
-    end
-end
-
-local function stop_sand_button()
-    local ok, sand_btn = pcall(reqscript, 'making-concrete-sand-button')
-    if ok and sand_btn and sand_btn.stop then
-        sand_btn.stop()
-    end
-end
-
-
--- ==========================================
--- COLLECT SAND MULTIPLIER MANAGEMENT
--- ==========================================
--- Starts and stops the onJobCompleted hook that multiplies
--- collect sand output from 1 unit to 4 units per bag. This
--- makes collected sand bags uniform with GRIND_SAND output
--- (4 units each), preventing mixed-size bag problems in
--- reaction matching and cutting sand haul counts by 75%.
---
--- The multiplier script (making-concrete-sand-multiply.lua)
--- registers an eventful callback. We just call start/stop.
--- ==========================================
-
-local function start_sand_multiplier()
-    local ok, sand_mul = pcall(reqscript, 'making-concrete-sand-multiply')
-    if ok and sand_mul and sand_mul.start then
-        sand_mul.start()
-        log('DETAIL', 'Collect Sand multiplier started.', 'SAND_MULTIPLY')
-    else
-        -- ERROR: collected sand stays at one unit per bag.
-        log('ERROR', 'Could not start the sand multiplier.', 'SAND_MULTIPLY')
-    end
-end
-
-local function stop_sand_multiplier()
-    local ok, sand_mul = pcall(reqscript, 'making-concrete-sand-multiply')
-    if ok and sand_mul and sand_mul.stop then
-        sand_mul.stop()
-    end
-end
-
-
--- ==========================================
--- GHOST SWAP WATCHER MANAGEMENT
--- ==========================================
--- Starts and stops the watcher that redirects generic grind
--- jobs to material specific ghost reactions.
---
--- What it does: the player orders one "grind stone into sand"
--- job. Before it completes, the watcher reads the stone the
--- dwarf actually carried in. Volcanic stone gets the job
--- pointed at GRIND_VOLCANIC_SAND instead, so the same menu
--- entry yields volcanic sand from obsidian and ordinary sand
--- from everything else.
---
--- The ghost is declared dormant in the JSON (permissions NONE,
--- fortress_mode false) so it never appears in a workshop menu.
--- The watcher wakes it only while a job needs it.
---
--- It also refuses to grind this module's own materials, the
--- way RM refuses to grind finished bars.
---
--- The watcher script (making-concrete-sand-watcher.lua) manages
--- its own polling via repeat-util. We just call start/stop.
--- ==========================================
-
-local function start_sand_watcher()
-    local ok, watcher = pcall(reqscript, 'making-concrete-sand-watcher')
+-- MIX WATCHER MANAGEMENT
+-- ==========================================
+-- Starts and stops the watcher that points each concrete mix job at
+-- the ghost reaction for what its inputs make.
+--
+-- What it does: the player orders one "mix concrete" job. Once every
+-- ingredient is attached, the watcher reads what the dwarf actually
+-- carried in. Volcanic dust points the job at MIX_CONCRETE_DWARVEN,
+-- slag cement at MIX_CONCRETE_SLAG; anything else stays concrete.
+--
+-- The ghosts are declared dormant in the JSON (permissions NONE,
+-- fortress_mode false, building NONE) so they never appear in a
+-- workshop menu. The watcher wakes one only while a job needs it.
+--
+-- It rides RM's loop dispatcher, with its own loop as the fallback.
+-- We just call start/stop. (In 1.x this was the sand watcher, beside
+-- the Collect Sand button injector and the sand multiplier.)
+-- ==========================================
+local function start_mix_watcher()
+    local ok, watcher = pcall(reqscript, 'making-concrete-mix-watcher')
     if ok and watcher and watcher.start then
         watcher.start()
-        log('DETAIL', 'Ghost swap watcher started.', 'SAND_WATCHER')
+        log('DETAIL', 'Mix watcher started.', 'MIX_WATCHER')
     else
-        -- ERROR: no volcanic sand swaps, and nothing stops this module's
-        -- own materials being ground.
-        log('ERROR', 'Could not start the ghost swap watcher.', 'SAND_WATCHER')
-    end
-end
-
-local function stop_sand_watcher()
-    local ok, watcher = pcall(reqscript, 'making-concrete-sand-watcher')
+        -- ERROR: every mix makes plain concrete, whatever went in.
+        log('ERROR', 'Could not start the mix watcher; every mix makes plain'
+            .. ' concrete.', 'MIX_WATCHER')
+    end
+end
+
+local function stop_mix_watcher()
+    local ok, watcher = pcall(reqscript, 'making-concrete-mix-watcher')
     if ok and watcher and watcher.stop then
         watcher.stop()
@@ -434,5 +269,4 @@
 end
 
-
 -- ==========================================
 -- REGISTRATION
@@ -440,7 +274,7 @@
 -- Connects to RM's module engine and registers a listener
 -- that fires when RM broadcasts its startup token call.
--- The listener loads JSONs, runs value calculation if needed,
--- resolves sand materials, starts the sand button injector,
--- and returns pre-built data tables to the engine.
+-- The listener loads the JSONs, runs value calculation if needed,
+-- starts the mix watcher, and returns pre-built data tables to the
+-- engine.
 -- ==========================================
 local function register_with_rm()
@@ -484,4 +318,15 @@
         end
 
+        -- The cement form. Every mix and grind names it, so without it
+        -- the module's reactions are left out by the engine; say so here
+        -- first, where the cause is plain.
+        local tool_data = nil
+        if TOOLS_FILE then
+            tool_data = load_json(data_path .. TOOLS_FILE)
+            if not tool_data then
+                log('ERROR', 'Failed to load ' .. TOOLS_FILE .. '.', 'DATA')
+                return nil
+            end
+        end
         if not mat_data and not rxn_data then
             log('ERROR', 'No data files loaded, so there is nothing to inject.',
@@ -524,34 +369,11 @@
         end
 
-        -- ---- SAND MATERIAL RESOLUTION ----
-        -- Resolve null mat_id on GRIND_SAND product to the best
-        -- available sand inorganic in this world. Must run before
-        -- the engine processes reaction data, since the engine
-        -- expects all mat_id values to be resolvable strings.
-        if rxn_data then
-            patch_sand(rxn_data)
-        end
-
-        -- ---- COLLECT SAND BUTTON ----
-        -- Start the mason workshop button injector. Adds a native
-        -- "Collect Sand" order to every mason workshop, identical
-        -- to the glass furnace's built-in button. Runs after sand
-        -- resolution since it depends on the world having sand.
-        start_sand_button()
-
-        -- ---- COLLECT SAND MULTIPLIER ----
-        -- Start the onJobCompleted hook that multiplies collect
-        -- sand output from 1 to 4 units per bag. This makes
-        -- collected sand uniform with GRIND_SAND output and cuts
-        -- sand haul counts by 75%.
-        start_sand_multiplier()
-
-        -- ---- GHOST SWAP WATCHER ----
-        -- Started last. It sweeps orphaned ghost names off any
-        -- jobs that survived a save, which needs the reactions
-        -- to be present, and the engine injects those from the
-        -- data returned just below. The first poll is a frame
-        -- away, so the sweep lands after injection either way.
-        start_sand_watcher()
+        -- ---- MIX WATCHER ----
+        -- Started last. It sweeps orphaned ghost names off any jobs
+        -- that survived a save, which needs the reactions to be
+        -- present, and the engine injects those from the data returned
+        -- just below. The first poll is a frame away, so the sweep lands
+        -- after injection either way.
+        start_mix_watcher()
 
         -- ---- RETURN TO ENGINE ----
@@ -560,4 +382,5 @@
             reactions  = rxn_data and rxn_data.reactions or nil,
             categories = rxn_data and rxn_data.categories or nil,
+            tools      = tool_data and tool_data.tools or nil,
             module     = mat_data and mat_data.module or
                          rxn_data and rxn_data.module or nil,
@@ -570,17 +393,14 @@
 -- SHUTDOWN HOOK
 -- ==========================================
--- Stops the button injector, sand multiplier and ghost swap
--- watcher when the map
--- unloads. This prevents callbacks from running after the
--- world data they reference has been freed.
+-- Stops the mix watcher when the map unloads. This prevents
+-- callbacks from running after the world data they reference has
+-- been freed. (1.x stopped the sand button injector and the sand
+-- multiplier here too.)
 -- ==========================================
 dfhack.onStateChange.making_concrete_unload = function(code)
     if code == SC_MAP_UNLOADED then
-        stop_sand_button()
-        stop_sand_multiplier()
-        stop_sand_watcher()
-    end
-end
-
+        stop_mix_watcher()
+    end
+end
 
 -- ==========================================
```

## making-concrete-mix-watcher.lua: diff against making-concrete-sand-watcher.lua

```diff
--- old/making-concrete-sand-watcher.lua
+++ new/making-concrete-mix-watcher.lua
@@ -1,10 +1,15 @@
 --@ module = true
--- making-concrete-sand-watcher.lua
+-- making-concrete-mix-watcher.lua
 -- ==========================================
 -- MAKING CONCRETE: GHOST REACTION SWAP WATCHER
 -- ==========================================
--- Watches generic grind jobs and redirects them to a material
--- specific ghost reaction based on what the dwarf actually
--- picked up.
+-- Watches concrete mix jobs and points each at the ghost reaction
+-- for the concrete its inputs make, judged on what the dwarf actually
+-- brought: volcanic dust makes dwarven concrete, slag cement makes
+-- slag concrete, and anything else stays plain concrete.
+--
+-- This was the sand watcher (making-concrete-sand-watcher.lua), which
+-- did the same for the sand grinder until sand left the module with
+-- 2.0, 2026-09-25. The technique and its lessons are unchanged.
 --
 -- THE PROBLEM:
@@ -35,6 +40,6 @@
 --   renames the job.
 --
---   Ours does real work. Volcanic sand is not the input material,
---   so GET_MATERIAL_SAME cannot reach it and the ghost carries an
+--   Ours does real work. Dwarven and slag concrete are not the input
+--   material, so GET_MATERIAL_SAME cannot reach them and the ghost carries an
 --   explicit material. A missed swap gives the wrong material
 --   rather than an ugly name, so the structural rules below are
@@ -58,5 +63,5 @@
 local utils      = require('utils')
 
-local REPEAT_KEY = 'making_concrete_sand_watcher'
+local REPEAT_KEY = 'making_concrete_mix_watcher'
 -- ---- LOG IDENTITY, DECLARED HERE ----
 -- RM core does not know this module exists and must never have to.
@@ -69,5 +74,5 @@
 -- falls back to the same grammar, unsanitised, and the script still
 -- loads.
-local LOG_SYS, LOG_SUB = 'MAKING_CONCRETE', 'SAND_WATCHER'
+local LOG_SYS, LOG_SUB = 'MAKING_CONCRETE', 'MIX_WATCHER'
 local rlog = nil
 pcall(function() rlog = reqscript('refinish-log') end)
@@ -94,5 +99,5 @@
 --
 -- SUBJECT is the correlation slot: the part of the watcher a line is
--- about (POLL, JOB, SWAP, GHOST, REFUSED, ORPHANS, START, STOP).
+-- about (POLL, JOB, SWAP, GHOST, ORPHANS, START, STOP).
 --
 -- Every line reaches the log on disk. Filtering is the panel's job
@@ -132,13 +137,8 @@
 
 -- Frames between polls. RM's watcher runs at 10 on its FAST
--- setting. Grinding is not instant, so this has room, but it must
+-- setting. Mixing is not instant, so this has room, but it must
 -- stay well under the shortest job duration or a swap can miss.
 local POLL_FRAMES = 10
 
--- Any material whose ID starts with this is something this module
--- produced. Grinding it back down is always a mistake, so the
--- watcher cancels the job rather than letting it run. Prefix based
--- so it covers materials added later without another edit here.
-local PROTECT_PREFIX = 'MAKING_CONCRETE_'
 
 
@@ -147,16 +147,23 @@
 -- ==========================================
 -- Keyed by the BASE reaction code (full prefixed ID). Each rule
--- names the reagent slot carrying the material to inspect, and an
--- ordered list of matches. First match wins; no match leaves the
+-- lists its matches in order. First match wins; no match leaves the
 -- job alone and the base reaction's own product stands.
 --
--- A match may test either:
+-- A match names the TOOL whose attached items carry the material to
+-- inspect (every input to the mix is a tool, so the item type alone
+-- cannot tell them apart the way it told the sand grinder's stone from
+-- its bag; the tool's itemdef id can), and tests that material by
+-- either:
 --   mat_id  an exact inorganic ID
 --   flag    an inorganic_raw.flags name, which catches modded
 --           stones of the same kind without naming them
---
--- Adding a rock-coloured sand set later means adding entries here
--- and declaring the matching ghosts in the JSON. Nothing in the
--- loop below needs to change.
+-- all = true asks every attached item of that tool to pass, not one.
+--
+-- A rule is judged once every reagent is attached (items), never
+-- earlier, so the outcome cannot depend on which item a dwarf happened
+-- to carry in first.
+--
+-- Adding a concrete later means adding a match here and declaring the
+-- matching ghost in the JSON. Nothing in the loop below needs to change.
 -- ==========================================
 -- Reaction codes are built by the engine as
@@ -172,185 +179,94 @@
 end
 
+local DUST_TOOL   = 'REFINISH_CORE_DUST'      -- RM's dust: the fine aggregate
+local CEMENT_TOOL = MODULE_PREFIX .. 'CEMENT'  -- this module's cement form
+local SLAG_MAT    = 'REFINISH_WASTE_SLAG'      -- RM's slag, carried by its WASTE form
+
 local SWAP_RULES = {
-    ["GRIND_SAND"] = {
-        -- Which item type carries the material we inspect. This is
-        -- how RM's own watcher picks the input out of job.items
-        -- (JIT_CONFIG.itype), and it is enough to tell the stone
-        -- apart from the bag without needing a reagent index.
-        item_type = df.item_type.BOULDER,
-
-        -- YIELD TIERS. First match wins, so order is significant:
-        -- specific materials first, the flag catch-all last.
-        --
-        -- Every tier fills all four bags. Only the RATIO of volcanic
-        -- sand to ordinary sand changes, so nothing is wasted and no
-        -- tier leaves a partial bag the mixer cannot use.
-        --
-        -- The ordering is pozzolanic reactivity, which tracks
-        -- amorphous silica content, which in turn tracks how felsic
-        -- and how glassy the rock is. That is why obsidian sits at
-        -- the top: it is volcanic glass, effectively pure amorphous
-        -- silica.
-        --
-        -- Anything not listed and not extrusive never reaches a ghost
-        -- at all. It stays on the base reaction and yields four
-        -- ordinary sand.
+    ["MIX_CONCRETE"] = {
+        -- One cement, two dust, three gravel: the mix's reagent count,
+        -- which every ghost shares (see the header).
+        items = 6,
         matches = {
-            -- 4 volcanic. Volcanic glass. Named explicitly so it
-            -- still wins if a mod clears its igneous flag.
-            { mat_id = "OBSIDIAN",
-              ghost  = "GRIND_VOLCANIC_SAND" },
-
-            -- 3 volcanic, 1 sand. Felsic extrusives: high silica,
-            -- commonly glassy.
-            { mat_id = "RHYOLITE",
-              ghost  = "GRIND_VOLCANIC_SAND_FELSIC" },
-
-            -- 2 volcanic, 2 sand. Intermediate extrusive.
-            { mat_id = "ANDESITE",
-              ghost  = "GRIND_VOLCANIC_SAND_INTERMEDIATE" },
-            { mat_id = "DACITE",
-              ghost  = "GRIND_VOLCANIC_SAND_INTERMEDIATE" },
-
-            -- 1 volcanic, 3 sand. The floor for volcanic rock:
-            -- basalt in vanilla, plus any modded extrusive stone
-            -- this table has never heard of. Mafic and largely
-            -- crystalline, so weak pozzolanic activity, and the
-            -- right conservative default for an unknown.
+            -- DWARVEN CONCRETE. Every fine aggregate is volcanic dust:
+            -- pozzolana, the Roman recipe's volcanic ash. It wins over
+            -- slag cement, since the pozzolan is what makes it.
             --
-            -- Anything that should beat this ratio gets named above.
-            { flag  = "IGNEOUS_EXTRUSIVE",
-              ghost = "GRIND_VOLCANIC_SAND_MAFIC" },
-        },
-    },
-    ["GRIND_COMMON_SAND"] = {
-        -- Which item type carries the material we inspect. This is
-        -- how RM's own watcher picks the input out of job.items
-        -- (JIT_CONFIG.itype), and it is enough to tell the stone
-        -- apart from the bag without needing a reagent index.
-        item_type = df.item_type.BOULDER,
-
-        -- YIELD TIERS. First match wins, so order is significant:
-        -- specific materials first, the flag catch-all last.
-        --
-        -- Every tier fills all four bags. Only the RATIO of volcanic
-        -- sand to ordinary sand changes, so nothing is wasted and no
-        -- tier leaves a partial bag the mixer cannot use.
-        --
-        -- The ordering is pozzolanic reactivity, which tracks
-        -- amorphous silica content, which in turn tracks how felsic
-        -- and how glassy the rock is. That is why obsidian sits at
-        -- the top: it is volcanic glass, effectively pure amorphous
-        -- silica.
-        --
-        -- Anything not listed and not extrusive never reaches a ghost
-        -- at all. It stays on the base reaction and yields four
-        -- ordinary sand.
-        matches = {
-            -- 4 volcanic. Volcanic glass. Named explicitly so it
-            -- still wins if a mod clears its igneous flag.
-            { mat_id = "OBSIDIAN",
-              ghost  = "GRIND_VOLCANIC_SAND" },
-
-            -- 3 volcanic, 1 sand. Felsic extrusives: high silica,
-            -- commonly glassy.
-            { mat_id = "RHYOLITE",
-              ghost  = "GRIND_VOLCANIC_SAND_FELSIC" },
-
-            -- 2 volcanic, 2 sand. Intermediate extrusive.
-            { mat_id = "ANDESITE",
-              ghost  = "GRIND_VOLCANIC_SAND_INTERMEDIATE" },
-            { mat_id = "DACITE",
-              ghost  = "GRIND_VOLCANIC_SAND_INTERMEDIATE" },
-
-            -- 1 volcanic, 3 sand. The floor for volcanic rock:
-            -- basalt in vanilla, plus any modded extrusive stone
-            -- this table has never heard of. Mafic and largely
-            -- crystalline, so weak pozzolanic activity, and the
-            -- right conservative default for an unknown.
+            -- The sand grinder graded volcanic stone by pozzolanic
+            -- reactivity, which tracks amorphous silica content, which in
+            -- turn tracks how felsic and how glassy the rock is: obsidian
+            -- (volcanic glass, effectively pure amorphous silica), then
+            -- felsic rhyolite, then intermediate andesite and dacite,
+            -- then mafic basalt, the floor, largely crystalline and
+            -- weakly pozzolanic. Every grade makes dwarven concrete now;
+            -- the order is kept here in case grades return.
             --
-            -- Anything that should beat this ratio gets named above.
-            { flag  = "IGNEOUS_EXTRUSIVE",
-              ghost = "GRIND_VOLCANIC_SAND_MAFIC" },
+            -- Obsidian is named so it still counts if a mod clears its
+            -- igneous flag; the flag catches every extrusive stone,
+            -- modded ones this table has never heard of included.
+            { tool = DUST_TOOL, all = true,
+              tests = { { mat_id = "OBSIDIAN" },
+                        { flag = "IGNEOUS_EXTRUSIVE" } },
+              ghost = "MIX_CONCRETE_DWARVEN" },
+            -- SLAG CONCRETE. The cement was ground from slag: the
+            -- byproduct route to a binder, blast furnace slag standing
+            -- in for clinker as it does in real cement.
+            { tool = CEMENT_TOOL,
+              tests = { { mat_id = SLAG_MAT } },
+              ghost = "MIX_CONCRETE_SLAG" },
         },
     },
 }
 
-
--- ==========================================
--- READ THE ATTACHED MATERIAL
--- ==========================================
--- Returns the inorganic ID string and its raw object for the first
--- attached item of the given type, or nil if nothing is attached
--- yet. An early poll will legitimately return nil: the dwarf has
--- taken the job but has not carried the stone in.
---
--- Item type selects the slot, exactly as RM's watcher does with
--- JIT_CONFIG.itype. The bag is a different item type from the
--- stone, so no reagent index is needed.
+-- ==========================================
+-- READ THE ATTACHED MATERIALS
+-- ==========================================
+-- Returns { id, raw } for every attached item that is the given tool,
+-- in attachment order. An empty list is normal early in a job's life:
+-- the dwarf has taken the order but has not carried the item in.
+--
+-- The tool is recognised by its itemdef's id: item_toolst.subtype is
+-- a pointer to the itemdef, and the id is the only stable identity
+-- (refinish-tool-wash.lua).
 --
 -- matinfo.decode is the documented API and the one RM already uses
 -- here. mat_info.inorganic is the inorganic_raw, so the caller can
--- read .id and .flags straight off it.
--- ==========================================
-local function read_input_material(job, want_type)
+-- read .id and .flags straight off it. A non inorganic material has
+-- nothing to match on and comes back with no id.
+-- ==========================================
+local function read_tool_materials(job, want_tool)
+    local out = {}
     for _, iref in ipairs(job.items) do
         local item = iref.item
         if item then
-            local ok, itype = pcall(function() return tonumber(item:getType()) end)
-            if ok and itype == want_type then
+            local tid = nil
+            pcall(function()
+                if item:getType() == df.item_type.TOOL then tid = item.subtype.id end
+            end)
+            if tid == want_tool then
                 local mat_info = dfhack.matinfo.decode(item)
                 if mat_info and mat_info.inorganic then
-                    return mat_info.inorganic.id, mat_info.inorganic
+                    out[#out + 1] = { id = mat_info.inorganic.id, raw = mat_info.inorganic }
+                else
+                    out[#out + 1] = { id = nil, raw = nil }
                 end
-                -- Right slot, non inorganic material. Nothing to
-                -- match on, so leave the job alone.
-                return nil
-            end
-        end
-    end
-    return nil
-end
-
-
--- ==========================================
--- PROTECT THIS MODULE'S OWN MATERIALS
--- ==========================================
--- Mirrors RM's trap door, which refuses to let a dwarf grind a
--- finished bar or a protected base metal.
---
--- Only CLINKER is currently exposed (it is the module's one BOULDER
--- product, and a BOULDER_ANY reagent will happily take it), but the
--- check is on the prefix rather than a material list so anything
--- added later is covered without touching this file.
--- ==========================================
-local function is_protected(mat_id)
-    return string.sub(mat_id, 1, #PROTECT_PREFIX) == PROTECT_PREFIX
-end
-
--- Cancels the job and tells the player why. Uses RM's theme colour
--- when it is reachable so the announcement matches the rest of the
--- mod, and falls back to a plain warning colour if it is not.
-local function cancel_protected(job, mat_id, mat_raw)
-    local nice = mat_id
-    pcall(function()
-        local n = mat_raw.material.state_name[0]
-        if n and n ~= '' then nice = n end
-    end)
-
-    local msg = 'A dwarf realized they were about to grind ' .. nice
-                .. ' back into sand and canceled the job.'
-
-    local color = COLOR_YELLOW
-    pcall(function()
-        color = reqscript('refinish-theme').get_current_theme().RISK_L
-    end)
-
-    pcall(function() dfhack.gui.showAnnouncement(msg, color, true) end)
-    -- WARNING, matching the yellow announcement above.
-    log('WARNING', 'Canceled job. Refused to grind protected material '
-        .. mat_id .. '.', 'REFUSED')
-end
-
+            end
+        end
+    end
+    return out
+end
+
+-- ==========================================
+-- NOTHING TO PROTECT
+-- ==========================================
+-- The sand watcher cancelled any grind of this module's own materials
+-- (anything prefixed MAKING_CONCRETE_: grinding it back down was always
+-- a mistake), mirroring RM's trap door, which refuses to let a dwarf
+-- grind a finished bar or a protected base metal. Clinker was the one
+-- exposed material: a boulder, which a BOULDER_ANY reagent would happily
+-- take. In 2.0 the module has no grinder of its own and clinker is RM's
+-- gravel form, which nothing but GRIND_CLINKER asks for, so the refusal
+-- went with the sand grinder.
+-- ==========================================
 
 -- ==========================================
@@ -360,12 +276,32 @@
 -- the first one that fits, or nil.
 -- ==========================================
-local function resolve_ghost(rule, mat_id, mat_raw)
+local function passes(tests, mat)
+    if not mat.id then return false end
+    for _, t in ipairs(tests) do
+        if t.mat_id and t.mat_id == mat.id then return true end
+        if t.flag then
+            local ok, val = pcall(function() return mat.raw.flags[t.flag] end)
+            if ok and val then return true end
+        end
+    end
+    return false
+end
+
+local function resolve_ghost(rule, job)
     for _, m in ipairs(rule.matches) do
-        if m.mat_id and m.mat_id == mat_id then
-            return m.ghost_code
-        end
-        if m.flag then
-            local ok, val = pcall(function() return mat_raw.flags[m.flag] end)
-            if ok and val then return m.ghost_code end
+        local mats = read_tool_materials(job, m.tool)
+        if #mats > 0 then
+            local hit = m.all == true
+            for _, mat in ipairs(mats) do
+                local ok = passes(m.tests, mat)
+                if m.all and not ok then
+                    hit = false
+                    break
+                elseif not m.all and ok then
+                    hit = true
+                    break
+                end
+            end
+            if hit then return m.ghost_code end
         end
     end
@@ -373,10 +309,9 @@
 end
 
-
 -- ==========================================
 -- DORMANT GHOSTS
 -- ==========================================
 -- A ghost must not be orderable. If it were, the workshop would
--- carry a second sand entry permanently, which is the exact menu
+-- carry a second concrete entry permanently, which is the exact menu
 -- clutter this whole approach exists to avoid.
 --
@@ -393,4 +328,9 @@
 -- moment it points a job at the ghost, and back to false once no
 -- job references it. Enabled exactly as long as it is needed.
+--
+-- Measured since, in Making Fuel: a reaction's visibility is its
+-- building field alone, and FORTRESS_MODE_ENABLED is not a visibility
+-- lever. So these ghosts also declare building NONE, which keeps them
+-- out of every menu by itself. The flag handling here is unchanged.
 -- ==========================================
 
@@ -407,4 +347,11 @@
         GHOST_CODES[m.ghost_code] = true
     end
+end
+
+-- The jobs this watcher serves: a base mix, or a mix already swapped
+-- to a ghost (it keeps its ghost awake, and the orphan sweep needs it).
+-- Handed to RM's dispatcher, which walks the job list once for everyone.
+local function is_mix_name(name)
+    return BASE_CODES[name] ~= nil or GHOST_CODES[name] ~= nil
 end
 
@@ -457,5 +404,7 @@
 -- THE POLL
 -- ==========================================
--- One pass over the job list. Everything is wrapped in pcall so a
+-- One pass over the mix jobs, handed in by RM's dispatcher, or by this
+-- file's own loop (poll, below) where there is none. Everything is
+-- wrapped in pcall so a
 -- malformed job cannot take the module down, and errors are
 -- reported once rather than every frame.
@@ -479,5 +428,5 @@
 local SWEEP_RETRIES = 40
 
-local function poll()
+local function serve(jobs)
     if not dfhack.isMapLoaded() then return end
 
@@ -554,9 +503,8 @@
     end
 
-    -- Jobs to cancel are collected here and removed AFTER the walk
-    -- finishes. RM removes in place and breaks, which works, but
-    -- mutating a linked list while iterating it is a hazard worth
-    -- not taking when deferring costs nothing.
-    local doomed = {}
+    -- The sand watcher collected jobs to cancel here and removed them
+    -- AFTER the walk: RM removes in place and breaks, which works, but
+    -- mutating a linked list while iterating it is a hazard worth not
+    -- taking when deferring costs nothing. Nothing is cancelled now.
 
     -- Ghost codes some job is currently pointing at. Anything not in
@@ -565,5 +513,5 @@
 
     local ok, err = pcall(function()
-        for _, job in utils.listpairs(df.global.world.jobs.list) do
+        for _, job in ipairs(jobs) do
             if job.job_type == df.job_type.CustomReaction then
                 local rname = tostring(job.reaction_name)
@@ -575,5 +523,4 @@
 
                 local rule = BASE_CODES[rname]
-
                 -- Only base reactions match. Once swapped, the job
                 -- holds the ghost name and falls through here, so
@@ -583,62 +530,31 @@
                              'Observing base reaction job: ' .. rname .. '.',
                              'JOB')
-
-                    local mat_id, mat_raw = read_input_material(job, rule.item_type)
-
-                    if not mat_id then
-                        -- Normal early in a job's life: the dwarf has
-                        -- taken the order but not carried the stone in.
-                        -- Logged once so a job that NEVER gets an item
-                        -- is distinguishable from one that just has not
-                        -- yet.
-                        log_once('noitem:' .. rname, 'DETAIL',
-                                 'Job ' .. rname .. ' has no item of the '
-                                 .. 'expected type attached yet.', 'JOB')
-                    end
-
-                    if mat_id then
-                        log_once('mat:' .. mat_id, 'DETAIL',
-                                 'Job ' .. rname .. ' carrying ' .. mat_id .. '.',
-                                 'JOB')
-
-                        if is_protected(mat_id) then
-                            -- This module made it. Do not grind it.
-                            table.insert(doomed, { job = job,
-                                                   mat_id = mat_id,
-                                                   mat_raw = mat_raw })
-                        else
-                            local ghost = resolve_ghost(rule, mat_id, mat_raw)
-
-                            if not ghost then
-                                log_once('norule:' .. mat_id, 'DETAIL',
-                                         mat_id .. ' matches no swap rule. '
-                                         .. 'Leaving the job on its base reaction.',
-                                         'SWAP')
-                            end
-
-                            local rxn = ghost and find_ghost(ghost)
-
-                            if ghost and not rxn then
-                                -- WARNING: the missing ghost itself is the
-                                -- ERROR above; this is one job it cost.
-                                log_once('noghost:' .. ghost, 'WARNING',
-                                         'Rule matched ' .. mat_id .. ' but ghost '
-                                         .. ghost .. ' is not in the reactions '
-                                         .. 'array. No swap performed.', 'SWAP')
-                            end
-
-                            if rxn then
-                                -- Wake the ghost first, then point the
-                                -- job at it. Never the other way round:
-                                -- a job aimed at a dormant reaction is
-                                -- a job nobody is permitted to finish.
-                                set_ghost_enabled(rxn, true)
-                                job.reaction_name = ghost
-                                referenced[ghost] = true
-                                log('DETAIL', 'Ghost swap: ' .. mat_id .. ' -> '
-                                    .. ghost .. '.', 'SWAP')
-                            end
+                    -- Judged only once every reagent is attached, so
+                    -- the outcome never depends on which item a dwarf
+                    -- carried in first. Until then the job is left alone.
+                    local n = 0
+                    pcall(function() n = #job.items end)
+                    if n >= rule.items then
+                        local ghost = resolve_ghost(rule, job)
+                        local rxn = ghost and find_ghost(ghost)
+                        if ghost and not rxn then
+                            -- WARNING: the missing ghost itself is the
+                            -- ERROR above; this is one job it cost.
+                            log_once('noghost:' .. ghost, 'WARNING',
+                                     'Rule matched but ghost ' .. ghost .. ' is not'
+                                     .. ' in the reactions array. No swap performed.',
+                                     'SWAP')
                         end
-
+                        if rxn then
+                            -- Wake the ghost first, then point the
+                            -- job at it. Never the other way round:
+                            -- a job aimed at a dormant reaction is
+                            -- a job nobody is permitted to finish.
+                            set_ghost_enabled(rxn, true)
+                            job.reaction_name = ghost
+                            referenced[ghost] = true
+                            log('DETAIL', 'Ghost swap: job ' .. tostring(job.id)
+                                .. ' -> ' .. ghost .. '.', 'SWAP')
+                        end
                     end
                 end
@@ -666,8 +582,4 @@
     end)
 
-    for _, d in ipairs(doomed) do
-        cancel_protected(d.job, d.mat_id, d.mat_raw)
-        pcall(function() dfhack.job.removeJob(d.job) end)
-    end
 
     if not ok then
@@ -684,4 +596,20 @@
 end
 
+
+
+-- This file's own loop, for an RM without the dispatcher: one pass over
+-- the job list, handing serve() exactly the jobs the dispatcher would.
+local function poll()
+    local jobs = {}
+    pcall(function()
+        for _, job in utils.listpairs(df.global.world.jobs.list) do
+            if job.job_type == df.job_type.CustomReaction
+               and is_mix_name(tostring(job.reaction_name)) then
+                jobs[#jobs + 1] = job
+            end
+        end
+    end)
+    serve(jobs)
+end
 
 -- ==========================================
@@ -741,16 +669,21 @@
 -- LIFECYCLE
 -- ==========================================
+-- ---- THE JOB WALK RIDES THE DISPATCHER ----
+-- RM's dispatcher walks the job list once per tick for every
+-- subscriber and hands this file only the mix jobs. With no dispatcher
+-- (an RM without refinish-loop-dispatch), or a subscription it refuses,
+-- this file's own loop runs instead. Whichever runs, the other is
+-- cleared, so a start after a start never leaves both serving the same
+-- jobs. paused = true because the sand watcher's loop ran while paused
+-- as well, so nothing about when it runs changes.
 function start()
     err_reported = false
     seen = {}
-
     local rule_count, ghost_count = 0, 0
     for _ in pairs(BASE_CODES)  do rule_count  = rule_count  + 1 end
     for _ in pairs(GHOST_CODES) do ghost_count = ghost_count + 1 end
-
     -- The reactions array is rebuilt every data cycle, so last
     -- session's reaction pointers are stale.
     ghost_cache = {}
-
     -- Do NOT sweep here. start() is called from the module listener,
     -- which RM runs before injection, so nothing this module declares
@@ -758,8 +691,14 @@
     needs_sweep = true
     sweep_tries = 0
-
-    repeatUtil.scheduleEvery(REPEAT_KEY, POLL_FRAMES, 'frames', poll)
-
-    log('DETAIL', 'Started. Polling every ' .. POLL_FRAMES .. ' frames.'
+    local via = 'its own loop'
+    local api = _G.refinish_dispatch_api
+    if api and api.subscribe and api.subscribe(REPEAT_KEY,
+            { every = POLL_FRAMES, jobs = is_mix_name, fn = serve, paused = true }) then
+        repeatUtil.cancel(REPEAT_KEY)
+        via = "RM's dispatcher"
+    else
+        repeatUtil.scheduleEvery(REPEAT_KEY, POLL_FRAMES, 'frames', poll)
+    end
+    log('DETAIL', 'Started on ' .. via .. ', every ' .. POLL_FRAMES .. ' frames.'
         .. ' Watching ' .. rule_count .. ' base reaction(s), ' .. ghost_count
         .. ' ghost(s).', 'START')
@@ -768,4 +707,8 @@
 function stop()
     repeatUtil.cancel(REPEAT_KEY)
+    -- Out of the dispatcher as well as repeat-util: whichever start()
+    -- chose, stop() clears both.
+    local api = _G.refinish_dispatch_api
+    if api and api.unsubscribe then api.unsubscribe(REPEAT_KEY) end
     log('DETAIL', 'Stopped.', 'STOP')
-end+end
```
