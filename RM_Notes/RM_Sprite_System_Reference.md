# RM Sprite System: Reference

What the sprite engine accepts, where each thing is allowed to
appear, and how to find the values you need. Written against the
shipped `refinish-sprite-engine.lua`, so every form listed here is
one the code actually parses.


## 1. The one idea underneath everything

DF renders a sprite by looking up an integer called a **texpos**.
It is an index into the game's texture atlas, assembled fresh each
load from the tileset PNGs.

A texpos is universal. The number that draws a dung pile draws a
dung pile no matter which item's field it is written into. So the
whole system is only ever doing two things:

1. **Find** a texpos that already exists somewhere live.
2. **Write** it into a field the renderer reads for your object.

Everything below is either a way of finding (SOURCE grammar) or a
way of writing (TARGET grammar).

Texpos values change between sessions if the tileset changes, so
they are never stored in JSON. Sources are always *descriptions of
where to look*, resolved live at inject time.


## 2. SOURCE grammar: where a sprite comes from

These strings appear on the right hand side, wherever a sprite
value is wanted. All six forms are implemented.

### `PAGE:<TOKEN>:<x>:<y>`
A cell on a loaded graphics page, the same coordinates the raws
use. `PAGE:BOULDERS:1:15` is the dung pile.

This is the closest thing to a real address, and the most useful:
it reaches any cell of any loaded tileset, vanilla or mod, whether
or not anything in the game currently points at it.

**Finding the coordinates:** open vanilla's graphics raws and read
them off existing lines. Any `[TOOL_GRAPHICS:BOULDERS:1:15:...]`
or similar tells you the page token and the cell. The token is the
page name, then x, then y.

### `TOOL:<ITEMDEF_CODE>#<field>`
One sprite field off a tool itemdef, live.
`TOOL:ITEM_TOOL_LARGE_POT#texpos_item`.

Use when something in the game already looks the way you want and
you would rather copy it than locate its cell.

### `<material token>#<slot>`
A sprite slot off a material.
`BUILTIN:COAL#bar`, `INORGANIC:MAGNETITE#boulder1`.

Slot names: `bar`, `wood`, `boulder1`, `boulder2`, `rough1`,
`rough2`, `cheese1`, `cheese2`, `texflag`. A raw field name also
works if you know one the friendly list lacks.

### `<material token>` with no `#`
Legal **only** as the source for a material target, where it means
"the same slot on the donor." `"bar": "BUILTIN:COAL"` means the
donor's bar slot. This is why the original coal schema reads the
way it does.

### `INFO:<surface>:<index>`
The texpos held by an entry in one of the graphics_info vectors.
`INFO:anvil:0`. Reading these is safe and useful; see section 5
about writing to them.

### `TEXPOS:<number>`
A literal. Debugging only. Values shift between sessions, so a
literal in JSON is a future bug.


## 3. Material tokens, and which prefixes are real

This is the distinction that was never explained, and it matters.

**Real, from DF's own raws grammar**, understood by DFHack's
`matinfo.find`:
- `INORGANIC:MAGNETITE`
- `PLANT:OAK:WOOD`
- `CREATURE_MAT:COW:LEATHER`

**Invented by this engine**, because DFHack has no name-based way
to reach builtin materials:
- `BUILTIN:COAL`, `BUILTIN:ASH`, `BUILTIN:POTASH`, and any other
  name in the `df.builtin_mats` enum.

Likewise `PAGE:`, `TOOL:`, `INFO:`, `TEXPOS:`, `MATERIAL:` and
`STATUE_TOP:` are all engine grammar. They exist because the code
in `resolve_source` and `apply_edits` explicitly parses them.

**The rule of thumb:** if a prefix is not in the list in this
document, the engine does not understand it, and adding it means
adding a branch to `resolve_source`. That is a small edit, roughly
fifteen lines, but it is an edit, not a configuration change.


## 4. TARGET: where a sprite goes

### 4a. On a material definition, in the materials JSON

```json
"graphics": {
  "bar": "BUILTIN:COAL",
  "boulder": { "source": "PAGE:BOULDERS:1:15" },
  "texflag": "BUILTIN:COAL"
}
```

Allowed keys, and only these: `bar`, `wood`, `boulder`, `rough`,
`cheese`, `texflag`. Note these are the **paired** names: one
`boulder` entry fills both `boulder_texpos1` and `boulder_texpos2`.

Long form on any value: `{ "source": "...", "offset": n }`.
`offset` shifts the resolved number by whole cells. `donor` is
accepted as an alias of `source`.

### 4b. On a tool definition, in the tools JSON

```json
"graphics": {
  "donor": "TOOL:ITEM_TOOL_LARGE_POT",
  "fields": {
    "texpos_item":  "PAGE:BOULDERS:1:15",
    "texpos_stone": { "source": "PAGE:BOULDERS:1:15", "fill": 7 }
  }
}
```

`donor` copies every sprite shaped field off another tool itemdef.
`fields` writes named fields, and runs after `donor`, so you can
wear a whole look and then override one part.

`fill` is only for a field that is a genuinely empty vector; the
common `texpos_stone` style fields are fixed arrays of 7 and
ignore it.

**Finding field names:** `refinish-sprite-engine fields <CODE>`
prints every sprite field on any tool itemdef with its current
values. Point it at a vanilla tool to see what a real binding
looks like.

### 4c. Anywhere, via `apply_edits`

For targets with no schema of their own. Called from Lua:

```lua
reqscript('refinish-sprite-engine').apply_edits({
  { target = 'MATERIAL:INORGANIC:MY_STONE#bar',
    source = 'PAGE:ITEM_CONSTRUCTION:0:4' },
  { target = 'TOOL:MAKING_FUEL_DUNG#texpos_item',
    source = 'PAGE:BOULDERS:1:15' },
}, 'my_module')
```

Target forms: `MATERIAL:<token>#<slot>`, `TOOL:<CODE>#<field>`,
`INFO:<surface>:<index>` or `:+` to append, `STATUE_TOP:<n>`,
`STATUE_BOTTOM:<n>`.


## 5. What is proven, and what is not

Stated honestly, because the registry lists far more addresses
than have been tested.

**Proven working, seen on screen:**
- Material `bar` slot. Module charcoal, coke and refined coal wear
  vanilla coal's art.
- Tool `fields` and `donor`. Eight module tools dressed with no
  raws involvement at all.
- `PAGE:` source. Proven equal to what the raws parser produces.
- `BUILTIN:` source, `TOOL:` source.

**Untested, expected to work:** the other material slots
(`boulder`, `wood`, `rough`, `cheese`). Same struct, same
mechanism as `bar`, but nothing has needed one yet.

**Tested and FAILED: writing to `INFO:` surfaces.** Appending
entries to `block_graphics_info` with correct color indices
changed nothing, across eight attempts. The working theory is that
these tables are built by the raws parser and consulted by the
renderer in a way that runtime appends do not reach.

So the registry's practical value today is as a **source of
values to read**, not a place to write.

**Known ceiling:** blocks and powders have no per-material sprite
field. They render the generic item sprite tinted by the
material's color, and that tint is the only control available.
Anything that must look distinctive ships as a tool instead.


## 6. Deciding what you need, for a new thing

**"I want my new material's bars to look like X."**
Material slot. Find X's cell in the graphics raws, then
`"graphics": { "bar": "PAGE:<TOKEN>:<x>:<y>" }`. No code.

**"I want my new tool to look like X."**
Tool fields. Same lookup, then a `fields` block with
`texpos_item` plus the four material class arrays at `fill: 7`,
copying the dung pattern. No code.

**"I want my new tool to look exactly like some existing tool."**
`"graphics": { "donor": "TOOL:<THAT_CODE>" }`. No code.

**"I want to change something that is not a material slot or a
tool."**
First establish whether it is writable at all, using the two
minute test in section 7. If it is, an `apply_edits` target may
already cover it, or a new target branch is a small engine edit.
If it is not writable, no amount of schema helps.


## 7. The two minute test, for any new item type

This is the method that produced every result in this system, and
it needs no help from anyone:

1. Find a field that could hold the sprite. Console tools:
   `refinish-sprite-engine fields <CODE>` for itemdefs,
   `refinish-sprite-engine mat <TOKEN>` for materials,
   `refinish-sprite-engine info <surface> <n>` for info entries.
2. Write an obviously wrong value into it from the console.
   Something recognisable, like the dung pile.
3. Look at the item.

Changed means the field is live and the renderer reads it per
object: it is yours, and the only question left is grammar.
Unchanged means the value was resolved at parse time and a runtime
write cannot reach it: no schema will fix that, and the answer is
a different surface or a different item type.

**Prediction, flagged as prediction:** item types that have
itemdefs (weapons, armor, ammo, instruments, toys, trapcomps)
should behave like tools, since they are the same shape. Item
types without itemdefs came back color-only in every case tested.
