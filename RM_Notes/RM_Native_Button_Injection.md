# Native Workshop Button Injection

## Discovery Date: April 8, 2026

## Summary

DF premium's workshop order list is populated from a vector of
`interface_button` objects stored at:

```
df.global.game.main_interface.building.filtered_button
```

This vector is rebuilt every time the player opens a workshop's order
panel. Each entry is a polymorphic `interface_button` subclass. By
creating a new instance of the correct subclass and inserting it into
this vector, we can add native-feeling order entries to any workshop —
entries that look and behave identically to DF's own built-in orders.

This was proven by injecting a "Collect Sand" button (normally only
available at the glass furnace) into the mason workshop's order list.
The button appeared as a native entry, and clicking it queued a real
CollectSand job that executed correctly.


## Button Types Observed

### interface_button_building_new_jobst
A button that creates a new job when clicked. Used for all concrete
workshop orders ("make rock blocks", "make rock door", etc.) and for
hardcoded jobs like "collect sand".

**Key fields:**
| Field                  | Type                    | Description                                          |
|------------------------|-------------------------|------------------------------------------------------|
| `bd`                   | `building*`             | Pointer to the building this button belongs to       |
| `filter_str`           | `string`                | Display text shown in the order list                 |
| `jobtype`              | `int32`                 | `df.job_type` enum value (e.g., 24 = CollectSand)    |
| `itemtype`             | `int32`                 | Item type for the job (e.g., 115 = TOOL for bags)    |
| `subtype`              | `int32`                 | Item subtype (-1 = any)                              |
| `material`             | `int32`                 | Material type (-1 = any)                             |
| `matgloss`             | `int32`                 | Material index (-1 = any)                            |
| `mstring`              | `string`                | Additional string data (empty for CollectSand)       |
| `specflag`             | `job_spec_flags`        | Special flags (default zeroed)                       |
| `specdata`             | `job_spec_data`         | Special data (default zeroed)                        |
| `job_item_flag`        | `job_material_category` | Material category filter (default zeroed)            |
| `add_building_location`| `bool`                  | Whether job uses building location (false)           |
| `show_help_instead`    | `bool`                  | Show help tooltip instead of executing (false)       |
| `art_specifier`        | `int32`                 | Art specifier (-1 = none)                            |
| `art_specifier_id1`    | `int32`                 | Art specifier ID 1 (-1 = none)                       |
| `art_specifier_id2`    | `int32`                 | Art specifier ID 2 (-1 = none)                       |
| `objection`            | `string`                | Objection text if job can't run (empty)              |
| `info`                 | `string`                | Info text (empty)                                    |

**Common (inherited) fields:**
| Field         | Type                   | Description                          |
|---------------|------------------------|--------------------------------------|
| `hotkey`      | `int32`                | Keyboard shortcut index (0 = none)   |
| `leave_button`| `bool`                 | Whether clicking leaves the menu     |
| `flag`        | `interface_button_flag`| Button state flags                   |
| `alpha_order` | `int32`                | Sort order (0 = default)             |

### interface_button_building_material_selectorst
Opens a material submenu. Used for "green glass (opens menu)" etc.
Has `material`, `matgloss`, `prepare_interface` fields.

### interface_button_building_category_selectorst
Opens a category submenu. Used for "engrave memorial slab (opens menu)".

### interface_button_building_custom_category_selectorst
Opens a custom reaction category submenu. Used for module reaction
categories like "cement production (opens menu)".
Has `custom_category_token` field matching the reaction category key.


## CollectSand Button Injection — Exact Code

```lua
-- Create a new job button pointing at the target workshop
local btn = df.interface_button_building_new_jobst:new()
btn.bd = workshop                -- the building_workshopst pointer
btn.filter_str = "collect sand"  -- display text in order list
btn.jobtype = 24                 -- df.job_type.CollectSand
btn.itemtype = 115               -- df.item_type.TOOL (bag)
btn.subtype = -1                 -- any subtype
btn.material = -1                -- any material
btn.matgloss = -1                -- any material index
btn.add_building_location = false
btn.show_help_instead = false
btn.art_specifier = -1
btn.art_specifier_id1 = -1
btn.art_specifier_id2 = -1

-- Insert in correct alphabetical position among new_jobst entries.
--
-- DF's order list is segregated: category/selector buttons appear
-- first as a group, then new_jobst entries appear below in
-- alphabetical order by filter_str. We must not insert into the
-- category group — only among the new_jobst entries.
--
-- Algorithm:
--   1. Walk the filtered_button vector
--   2. Skip all non-new_jobst entries (categories, material selectors)
--   3. Among new_jobst entries, find the first whose filter_str
--      sorts alphabetically after our label
--   4. Insert before that entry
--   5. If no such entry exists, insert at the end
local buttons = df.global.game.main_interface.building.filtered_button
local insert_idx = #buttons  -- default: end of list

for i = 0, #buttons - 1 do
    local existing = buttons[i]
    -- Only compare against other new_jobst entries (skip categories)
    if existing._type == df.interface_button_building_new_jobst then
        if existing.filter_str > btn.filter_str then
            insert_idx = i
            break
        end
    end
end

buttons:insert(insert_idx, btn)
```


## Ordering Rules

DF's workshop order list is type-segregated, then alphabetical:

1. `interface_button_building_category_selectorst` — vanilla category menus
   (e.g., "engrave memorial slab")
2. `interface_button_building_custom_category_selectorst` — module/mod
   reaction categories (e.g., "cement production", "concrete production")
3. `interface_button_building_material_selectorst` — material submenus
   (e.g., "green glass")
4. `interface_button_building_new_jobst` — concrete job entries, sorted
   alphabetically by `filter_str` (e.g., "collect sand", "grind any
   stone into dust", "make rock blocks")

Injected buttons must land in group 4. The insertion algorithm above
ensures this by only comparing `filter_str` against other `new_jobst`
entries. A button with `filter_str = "collect sand"` naturally sorts
before "grind any stone" and after any category selectors.

**Important:** Do NOT insert at a hardcoded index. The number of
categories varies depending on which modules are loaded. Always walk
the list and find the correct alphabetical position dynamically.


## Persistence — Solved

The `filtered_button` vector is rebuilt by DF every time the player
opens a workshop's order panel. Injected buttons vanish on close.

### The Problem

DF populates two vectors when a workshop panel opens:
- `button` — the master list of available orders
- `filtered_button` — a filtered copy (filtered by the search box)

Both are rebuilt from scratch each time. Injected buttons must be
re-added to both vectors every time the mason is opened.

### The Solution: 1-Frame Polling with Gate Checks

A `repeat-util` callback runs every frame. Five gate checks ensure
it only injects when the player is actively viewing a mason workshop
whose button list has been fully rebuilt by DF.

**Gate sequence:**
1. Are both `button` and `filtered_button` populated? (skip if empty)
2. Is `view_sheets.open` true? (skip if not viewing a building)
3. Is the viewed building a mason? (type 13, subtype 2)
4. Do the buttons belong to THIS mason? (see race condition below)
5. Is the collect sand button already present? (skip if duplicate)

### Critical: The Workshop Switch Race Condition

When the player switches from one workshop to another, there is a
window of 1+ frames where `view_sheets.viewing_bldid` has already
updated to the new building, but `filtered_button` still contains
the old building's entries. Without Gate 4, the injector sees:
- "The viewed building is a mason" (from `viewing_bldid`)
- "The button list has entries but no collect sand" (stale entries)
- Injects into the stale list → DF overwrites with the real list

Gate 4 catches this by checking `filtered_button[0].bd` — the first
button's building pointer. If it doesn't match the mason we're
targeting, the list hasn't been rebuilt yet. Skip that frame.

```lua
local ok, first_bd = pcall(function() return fb[0].bd end)
if not ok or first_bd ~= bld then return end
```

The `pcall` wrapper handles the edge case where `bd` is nil during
the transition (observed in debug logging).

### Injection Target

Must inject into BOTH vectors:
- `mi.building.button` — the master list
- `mi.building.filtered_button` — the display list

Injecting into only `filtered_button` works while the panel stays
open, but DF may re-derive `filtered_button` from `button` during
certain UI operations (e.g., typing in the search box). Injecting
into both ensures the button survives all UI interactions.

### Performance

At 1-frame polling, the callback fires every rendered frame. The
gate checks are extremely cheap — Gate 1 exits immediately on empty
vectors (which is the case whenever no workshop is open). The total
cost when not viewing a mason is one vector length check per frame.

### File Structure

- `making-concrete-sand-button.lua` — the injector script, lives in
  `scripts_modinstalled` under Making Concrete. Exports `start()`
  and `stop()`. Does not auto-start.
- `making_concrete.lua` — calls `start()` during the module listener
  callback (after sand resolution), registers `stop()` on
  `SC_MAP_UNLOADED` via `dfhack.onStateChange`.

### Lifecycle

```
Module boot (RM token call)
  → making_concrete.lua listener fires
    → JSON loading, value calc, sand resolution
    → start_sand_button()
      → reqscript('making-concrete-sand-button').start()
        → repeat-util schedules on_tick at 1 frame

Map unload (SC_MAP_UNLOADED)
  → dfhack.onStateChange.making_concrete_unload
    → stop_sand_button()
      → reqscript('making-concrete-sand-button').stop()
        → repeat-util cancels the callback
```


## Implications

This technique is not limited to CollectSand. Any `df.job_type` value
can be injected as a native button on any workshop. Potential uses:

- **CollectSand on mason** — proven working, fully integrated
- **Custom hardcoded jobs on workshops** — any job_type that DF's
  engine can execute but doesn't normally offer at a given building
- **Fill Water Barrel** — if a suitable job_type exists or can be
  spoofed, water collection could use the same pattern
- **Any future hardcoded job migration** — moving vanilla jobs
  between building types without raw modification

The key insight is that DF's engine validates jobs based on job_type
logic, not based on which building's UI created them. The UI is just
a list of buttons that create jobs. If the job is valid for the
engine to execute (as CollectSand proved to be on the mason), then
injecting the button makes it seamlessly available.

The secondary insight is that DF premium's UI re-reads the button
vectors live every render frame. Injecting into the vectors while
the panel is open causes the button to appear immediately — no
screen refresh or panel close/reopen needed.


## Data Sources

- Glass furnace filtered_button dump (entry 6): CollectSand reference
- Mason filtered_button dump (27 entries): injection target
- Building struct comparison: furnace vs workshop field differences
- Debug log: race condition identification and gate validation
- Path: `df.global.game.main_interface.building.filtered_button`
- Path: `df.global.game.main_interface.building.button`
- Button type: `df.interface_button_building_new_jobst`
