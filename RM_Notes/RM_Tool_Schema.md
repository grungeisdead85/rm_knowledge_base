# RM Tool Schema

> Historical: the design that brought tools into the module engine. Its examples are Making Fuel's vessel tools, which moved to RM's catalog and were removed from it on 2026-10-07. The current reference for tool fields is RM_MODULE_ENGINE_README.md, section 7.

A module may now carry a third data file alongside materials and
reactions: `<module>_tools.json`. Same shape as the other two, a
`module` block and a `tools` array.

Tools are core infrastructure, not module property. Any module can
reference any injected tool by its full code string, because
`refinish-module-react.lua` resolves itemdef codes to numeric subtypes
by lookup rather than by position. Cross module tool use needs no class
mechanism the way materials do, because the code string is stable while
the index is not.

---

## Tool object

| Key | Type | Notes |
|---|---|---|
| `key` | string | Prefixed at injection. `SMALL_BOTTLE` becomes `MAKING_FUEL_SMALL_BOTTLE`. |
| `name` | string | Singular display name. |
| `name_plural` | string | Plural display name. |
| `adjective` | string | Optional. Vanilla uses it for `[ADJECTIVE:large]` on the large pot. |
| `value` | int | Base value, before material. |
| `tile` | int | CP437 code point. |
| `size` | int | The item's own bulk, not what it holds. |
| `material_size` | int | How much material one costs to make. |
| `capacity` | int | `CONTAINER_CAPACITY`. Divide by 40 for dimension. |
| `tool_use` | array of strings | `TOOL_USE` tokens, resolved through `df.tool_uses`. |
| `flags` | object | Token flags, all optional, see below. |

### Flags

Omitted flags keep the constructed default rather than being forced
false. There is no class preset for tools the way there is for
materials, so nothing restores a sane baseline after a blanket clear.

`furniture`, `inverted_tile`, `no_default_job`, `incomplete_item`,
`unimprovable`, `no_default_improvements`, `hard_mat`, `metal_mat`,
`soft_mat`, `stone_mat`, `wood_mat`, `sheet_mat`, `metal_weapon_mat`

### Capacity and the partial container limit

Dimension is capacity divided by 40. A bucket is 6000, which is 150,
which is one unit of liquid.

A contained reagent draws from **exactly one container per quantity
slot**. DF will not gather three small bottles to satisfy a 150 slot.
So every container capacity must be a size that some reagent slot is
written at exactly, and moving between sizes has to be an explicit
decant reaction. Divisibility alone buys nothing.

Vanilla is inconsistent here: a bucket is 150 and the hardcoded vial is
45, and 45 does not divide 150, so one liquid offered in both sizes can
never satisfy a slot written for the other. The container set below
fixes that by putting everything on a strict times three ladder.

---

## The four containers

| Tool | capacity | dim | in buckets | decants from |
|---|---|---|---|---|
| small bottle | 2000 | 50 | 1/3 | |
| large bottle | 6000 | 150 | 1 | 3 small bottles |
| small cask | 18000 | 450 | 3 | 3 large bottles |
| large cask | 54000 | 1350 | 9 | 3 small casks |

`no_default_job` is set on all four. Without it DF offers a default
make job at the craftsdwarf's workshop, gated on a civ level tool
permission that the engine does not yet inject, so that route would
silently produce nothing. They are made by module reactions instead.
Drop the flag once entity tool permissions exist.

```json
{
    "module": {
        "id": "MAKING_FUEL",
        "prefix": "MAKING_FUEL_"
    },
    "tools": [
        {
            "key": "SMALL_BOTTLE",
            "name": "small bottle",
            "name_plural": "small bottles",
            "value": 10,
            "tile": 155,
            "size": 100,
            "material_size": 1,
            "capacity": 2000,
            "tool_use": [ "LIQUID_CONTAINER" ],
            "flags": {
                "hard_mat": true,
                "no_default_job": true
            }
        },
        {
            "key": "LARGE_BOTTLE",
            "name": "large bottle",
            "name_plural": "large bottles",
            "value": 10,
            "tile": 156,
            "size": 300,
            "material_size": 1,
            "capacity": 6000,
            "tool_use": [ "LIQUID_CONTAINER" ],
            "flags": {
                "hard_mat": true,
                "no_default_job": true
            }
        },
        {
            "key": "SMALL_CASK",
            "name": "small cask",
            "name_plural": "small casks",
            "value": 20,
            "tile": 233,
            "size": 1500,
            "material_size": 2,
            "capacity": 18000,
            "tool_use": [ "LIQUID_CONTAINER" ],
            "flags": {
                "hard_mat": true,
                "no_default_job": true
            }
        },
        {
            "key": "LARGE_CASK",
            "name": "large cask",
            "name_plural": "large casks",
            "value": 30,
            "tile": 234,
            "size": 4500,
            "material_size": 3,
            "capacity": 54000,
            "tool_use": [ "LIQUID_CONTAINER" ],
            "flags": {
                "hard_mat": true,
                "no_default_job": true
            }
        }
    ]
}
```

---

## Integration points

Four edits to existing files, each its own round. Listed in dependency
order.

### 1. `refinish-module-types.lua`

**`PRODUCT_TYPES` needs a `TOOL` entry.** There are fourteen product
types and none is a tool, so the engine can consume a container today
but can never make one. Nothing else works until this exists.

**`REAGENT_TYPES` needs a generic `TOOL` entry.** `JUG` and `LARGE_POT`
are currently hardcoded with a literal `item_subtype` string. A generic
entry lets a reagent name any tool:

```json
{ "code": "vessel", "type": "TOOL", "tool_id": "MAKING_FUEL_SMALL_CASK", "quantity": 1 }
```

That is better than adding four more hardcoded entries, and it is what
makes tools generally useful in reactions rather than just containers.

### 2. `refinish-module-react.lua`

Expose `invalidate_itemdef_cache()` and have `resolve_item_subtype`
check `_G.refinish_itemdef_cache_dirty` before trusting `itemdef_cache`.

The cache at line 202 is built once per session and never invalidated.
Harmless while every itemdef comes from raws, because raws never move.
The moment tools are injected and cleared across save cycles it hands
out positions for tools that no longer exist, silently, because the
miss branch only fires when a code is absent from the cache and not
when the cached number is stale. Same shape as the ghost_cache use
after free.

### 3. `refinish-module-engine.lua`

Load `<module>_tools.json`, call `inject_tools()` in the pipeline before
reactions are built, and call `clear_tools()` from `clear_module_assets()`.

Ordering is not negotiable: a reagent naming an injected tool needs
that tool in the array first.

### 4. Save safety

`is_memory_physically_clear()` and the autosave baseline check both need
to call `tools_physically_clear()`. A save taken with owned tools live
in the arrays is the same class of corruption as one taken with module
materials live.

The part I cannot write without seeing `refinish-ledger.lua`: a tool's
subtype is its array index, and every item stack in a fort stores that
number. That is the material index shift problem in a second array. If
`remap()` is written against inorganics specifically it needs
generalising; if it already walks arrays generically it may only need
the tools vector added to its list.

---

## Confirm the field map first

`refinish-module-inject-tool.lua` carries a `FIELD_MAP` and a
`FLAG_MAP` at the top. Those are the only place in the tool system that
knows `itemdef_toolst` layout, and they are written from the raw token
names rather than from the struct, because nothing in the project
documents it.

Run `refinish-tool-inspect` once, read `refinish_tool_inspect.txt`,
correct anything that differs. Steps 3 and 4 of the output give the
candidate names against the real ones, step 5 gives the tool use enum,
step 6 gives the flag members.

Every write in the injector is `pcall` guarded, so a map that is wrong
in one place still produces a usable tool for every other field and
logs exactly which name failed.
