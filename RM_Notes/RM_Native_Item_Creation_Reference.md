# RM Native Item Creation Reference
## Creating Items with dfhack.items.createItem and Placing Them in Containers

This document records every technical detail discovered during the Making Concrete
sand multiplier development. It covers creating powder items at runtime, placing
them inside bag containers, and making DF's UI display them correctly. Every rule
here was determined empirically through extensive testing.

---

## 1. The Problem

Vanilla CollectSand produces exactly 1 unit of sand powder (dimension 150) per bag
per trip. This is hardcoded in the DF engine. The concrete production chain needs
4 units of sand per batch, making the labour cost prohibitive at 1 unit per trip.

The solution: hook `onJobCompleted`, detect CollectSand jobs, and create 3 additional
sand powder items inside the same bag. This makes every collect trip produce 4 units,
matching the output of the GRIND_SAND reaction.

---

## 2. dfhack.items.createItem

### Signature
```lua
local result = dfhack.items.createItem(unit, item_type, item_subtype, mat_type, mat_index)
```

### Return Value
Returns a **Lua table**, not a DF item object directly. The created item is at
index `[1]`:
```lua
local new_item = result[1]  -- this is the actual item_powder_miscst
```

Accessing the return value directly (without `[1]`) gives you a table pointer,
not an item. Calling methods or accessing fields on it will fail with cryptic
nil errors.

### Birth State
Every item created by `createItem` is born with:
- `flags.removed = true` — marked for deletion
- `flags.garbage_collect = true` — marked for deletion
- `pos = {-30000, -30000, -30000}` — not on the map
- `flags.on_ground = false`
- `flags.in_inventory = false`
- All thermal properties zeroed (spec_heat, boiling_point, etc. = 0)
- Weight zeroed (weight.whole = 0, weight.fraction = 0)
- `flags.temps_computed = false`
- `flags.weight_computed = false`

If `removed` and `garbage_collect` are not cleared, DF deletes the item on
the next frame.

If thermal properties are left zeroed, DF treats the item as having bizarre
physics and it **explodes** — a visible dust cloud appears as the item
undergoes catastrophic thermal failure.

---

## 3. moveToContainer Does Not Work

`dfhack.items.moveToContainer(item, container)` **silently fails** on items
created with `createItem`. It returns without error but does not build the
containment relationship. The bag's `getContainedItems` count does not increase.

This is likely because `moveToContainer` internally checks the `removed` flag
or some other birth-state condition and rejects the item, even if you clear
`removed` before calling it.

**Do not use moveToContainer for created items.** Build containment refs manually.

---

## 4. Manual Containment Refs

To place a created item inside a bag, build the relationship manually:

```lua
-- Clear death flags so DF doesn't delete the item
item.flags.removed = false
item.flags.garbage_collect = false
item.flags.on_ground = false

-- Set contained position sentinel
item.pos.x = -30000
item.pos.y = -30000
item.pos.z = -30000

-- Powder -> bag: "I am contained in this bag"
local ref_in = df.general_ref_contained_in_itemst:new()
ref_in.item_id = bag.id
item.general_refs:insert('#', ref_in)

-- Bag -> powder: "I contain this powder"
local ref_has = df.general_ref_contains_itemst:new()
ref_has.item_id = item.id
bag.general_refs:insert('#', ref_has)
```

Both refs are required. Without the `contained_in_itemst` on the powder, DF
doesn't know the item is inside something. Without the `contains_itemst` on the
bag, `getContainedItems` won't find it.

---

## 5. Critical Flag Rules

These were determined by comparing working items against broken items using
full field dumps across multiple sessions of testing.

### FLAGS TO SET:
| Flag | Value | Why |
|------|-------|-----|
| `removed` | `false` | Clear or DF deletes the item |
| `garbage_collect` | `false` | Clear or DF deletes the item |
| `on_ground` | `false` | Item is inside a container, not on the map |
| `in_inventory` | `true` | Required for DF's reaction system to see the item inside a bag |
| `temps_computed` | `true` | Tells DF thermal properties are valid |
| `weight_computed` | `true` | Tells DF weight values are valid |

### THE SAND BAG DISPLAY TRADEOFF

Sand bags in DF are categorized as **furniture** when they contain sand.
This creates a fundamental conflict between two behaviors:

- `in_inventory = true` → DF's reaction system can see the items inside
  the bag. Reactions that need sand-containing bags work correctly. **But**
  the bag view shows "Uses" (crafting recipes) instead of listing the sand
  contents. This is the same behavior as vanilla CollectSand bags.

- `in_inventory = false` → The bag view displays the sand contents (each
  unit listed individually with icons). **But** DF's reaction system cannot
  see the items — reactions report "needs sand-containing bag" even when
  the bag is right there.

**These two behaviors are mutually exclusive.** There is no known flag
combination that gives both bag content display AND reaction recognition
for sand bags. This is a DF engine limitation tied to the furniture
categorization of sand-containing bags.

**The multiplier uses `in_inventory = true` because reaction functionality
is more important than bag display.** The sand items are visible in the
stock screen (z -> Stocks), so the player can verify quantities there.
The bag not displaying sand contents is vanilla DF behavior — unmodified
CollectSand bags behave the same way.

### Why non-sand bags work differently:
Bags containing non-sand powders (cement, gravel, plaster) are NOT
categorized as furniture. They display contents AND work in reactions
with `in_inventory = true`. The furniture categorization is specific to
bags containing SOIL_SAND-flagged inorganic materials.

---

## 6. Thermal Property Copy

All seven thermal fields must be copied from the original item:

```lua
new_item.boiling_point  = original.boiling_point
new_item.colddam_point  = original.colddam_point
new_item.fixed_temp     = original.fixed_temp
new_item.heatdam_point  = original.heatdam_point
new_item.ignite_point   = original.ignite_point
new_item.melting_point  = original.melting_point
new_item.spec_heat      = original.spec_heat
```

Also copy the temperature state to prevent starting at absolute zero:

```lua
new_item.temperature.whole    = original.temperature.whole
new_item.temperature.fraction = original.temperature.fraction
new_item.temp_updated_frame   = original.temp_updated_frame
```

And copy weight values (even though `weight_computed` stays false, the values
should be populated for physics correctness):

```lua
new_item.weight.whole    = original.weight.whole
new_item.weight.fraction = original.weight.fraction
```

Copy dimension and age for consistency:

```lua
new_item.dimension = original.dimension
new_item.age       = original.age
```

**If thermal properties are left zeroed, the item explodes.** This manifests
as a visible dust cloud on the map — DF's temperature system processes the
item, finds impossible thermal values, and destroys it catastrophically.

---

## 7. The One-Frame Delay Rule

**Items created on the same frame as job completion are garbage collected.**

This was the final piece of the puzzle. Even with all flags correct and all
properties copied, items created during the `onJobCompleted` callback (or
on the same frame via `dfhack.timeout(0, ...)`) are swept by DF's item
cleanup pass that runs as part of job completion processing.

### What doesn't work:
- Creating items directly inside `onJobCompleted` — items are GC'd
- Using `dfhack.timeout(0, 'frames', ...)` — same frame, items are GC'd
- Using `dfhack.timeout(1, 'frames', ...)` — items are GC'd
  (timeout may execute before DF's cleanup finishes)
- Creating items in a `repeat-util` tick on the same frame — items are GC'd

### What works:
- Recording the bag ID in `onJobCompleted`
- Setting a 1-frame delay counter
- On the **next frame**, a `repeat-util` tick sees the counter has expired
  and creates all items in one batch

```lua
-- In the onJobCompleted callback:
pending_bag_id = bag.id
frame_delay = 1  -- skip one frame

-- In the repeat-util tick (runs every frame):
if not pending_bag_id then return end
if frame_delay > 0 then
    frame_delay = frame_delay - 1
    return  -- skip this frame, let DF's cleanup finish
end
-- NOW create items — they survive
```

All 3 items can be created in one batch on the delayed frame. They do not
need to be spread across multiple frames. The key is waiting for the
job-completion frame to fully process before creating anything.

### Why the console worked without delay:
When running commands from the DFHack console, the game is **paused** (or
at minimum, not mid-frame). There is no active job-completion cleanup pass
running. Items created from the console persist because they're created in
a clean frame context, not inside a callback that's part of DF's job pipeline.

---

## 8. Architecture: Two-Component Design

The multiplier uses two cooperating components:

### Component 1: eventful.onJobCompleted callback
- Fires for every completed job in the game
- Filters for `job_type == 24` (CollectSand)
- Finds the bag from `job.items[0].item`
- Records `bag.id` and sets `frame_delay = 1`
- Does NOT create items (they would be GC'd)

### Component 2: repeat-util tick (1 frame interval)
- Runs every frame
- Fast exit if `pending_bag_id` is nil (effectively free)
- Counts down `frame_delay`; skips frame if delay > 0
- When delay expires: looks up bag, finds original sand, creates 3 copies
- Clears `pending_bag_id` after processing

Both components are started/stopped together via `start()` and `stop()`.
Lifecycle is managed by `making_concrete.lua` — started during module boot,
stopped on `SC_MAP_UNLOADED`.

---

## 9. Cleanup Commands

### Remove all sand powder items:
```lua
:lua local count = 0; for i = #df.global.world.items.all - 1, 0, -1 do
  local item = df.global.world.items.all[i];
  if item:getType() == df.item_type.POWDER_MISC and item.mat_type == 0 then
    local mat = df.global.world.raws.inorganics.all[item.mat_index];
    if mat and mat.flags.SOIL_SAND then
      dfhack.items.remove(item); count = count + 1
    end
  end
end; print("Removed " .. count)
```

`dfhack.items.remove` handles ref cleanup on the bag automatically.

### Remove malformed powders (zero thermal properties):
```lua
:lua local count = 0; for i = #df.global.world.items.all - 1, 0, -1 do
  local item = df.global.world.items.all[i];
  if item:getType() == df.item_type.POWDER_MISC and item.spec_heat == 0 then
    dfhack.items.remove(item); count = count + 1
  end
end; print("Removed " .. count .. " malformed")
```

### Kill all sand multiplier callbacks:
```lua
:lua local eventful = require('plugins.eventful');
eventful.onJobCompleted['making_concrete_sand_multiply'] = nil;
require('repeat-util').cancel('making_concrete_sand_multiply_tick');
print("killed")
```

### Find all bags with sand:
```lua
:lua for _, item in ipairs(df.global.world.items.all) do
  if item:getType() == df.item_type.BAG then
    local contents = dfhack.items.getContainedItems(item);
    for _, c in ipairs(contents) do
      if c:getType() == df.item_type.POWDER_MISC and c.mat_type == 0 then
        local mat = df.global.world.raws.inorganics.all[c.mat_index];
        if mat and mat.flags.SOIL_SAND then
          print("bag", item.id, "has", #contents, "sand")
        end
      end
    end
  end
end
```

---

## 10. Item Tracking Registration (IN_PLAY)

`createItem` adds items to `world.items.all` but does **NOT** add them to
`world.items.other.IN_PLAY`. This is DF's master tracking list for all active
items in the fortress. Without registration in `IN_PLAY`:

- The stock screen (z -> Stocks) cannot see the item
- The item may not be findable by some DF subsystems

### The fix:
After creating and linking each item, insert it into `IN_PLAY`:

```lua
df.global.world.items.other.IN_PLAY:insert('#', new_item)
```

This must be done AFTER clearing the death flags (`removed`, `garbage_collect`)
and AFTER setting up the containment refs. The item must be in a valid state
before being registered.

### Other category lists:
`world.items.other` contains many category-specific lists (`POWDER_MISC`,
`BAG`, `BOULDER`, etc.). Testing showed that adding items to `IN_PLAY` alone
is sufficient for stock screen visibility. The category-specific lists
(`POWDER_MISC`) did NOT need to be updated — `IN_PLAY` is the master list
that the stock screen queries.

### Discovery process:
The stock screen only showed 1 sand (the original from CollectSand) despite
4 items being in the bag. Comparing `world.items.other.IN_PLAY` membership
revealed the original was in the list and the created items were not. Adding
them to `IN_PLAY` immediately made them visible in stock.

---

## 11. Known Limitations

- **Sand bag content display:** Sand bags do not display their contents
  in the bag view — they show "Uses" (crafting recipes) instead. This is
  vanilla DF behavior caused by sand bags being categorized as furniture.
  It affects ALL sand bags: vanilla CollectSand, GRIND_SAND output, and
  multiplier-created sand alike. The sand IS visible in the stock screen.
  Setting `in_inventory = false` makes the bag display contents but
  breaks reaction recognition — DO NOT DO THIS. See Section 5 for the
  full tradeoff analysis.

- **One bag at a time:** If two CollectSand/GRIND_SAND jobs complete on
  the same frame, only the last one's bag ID is recorded. The first is
  lost. This is unlikely in practice (dwarves don't complete two collect
  jobs simultaneously) but could be fixed with a queue if needed.

---

## 12. Testing Checklist

After any changes to the multiplier:

1. Full recycle (quit DF, clear mod cache, relaunch)
2. Load save
3. Collect sand at mason (button should be present from sand-button script)
4. Check stock screen (z -> Stocks) — should show 4 sand
5. Verify items survive unpausing and playing for several minutes
6. Verify no dust explosions (thermal properties are correct)
7. Queue MIX_CONCRETE — verify the reaction is selectable and can find
   the sand-containing bag
8. Run GRIND_SAND — verify it also produces a bag with 4 sand in stock
9. Verify MIX_CONCRETE accepts both CollectSand and GRIND_SAND bags
