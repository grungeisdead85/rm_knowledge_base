# Adaptive sprites in RM

How a sprite takes its colour from the material instead of carrying its
own. Two mechanisms, one of which is DF's and one of which is ours.

Everything here is measured off the vanilla art, read out of a live
struct dump, or confirmed in play. Where something is inference it says
so.

---

## 1. The rule, in one table

| carrier | field | who tints it |
|---|---|---|
| TOOL itemdef | `texpos_item`, `texpos_stone/_wood/_metal/_glass` | **DF**, automatically |
| MATERIAL, slot left at 0 | — | **DF**, via its own default item sprite |
| MATERIAL, slot written | `boulder_texpos1/2`, `bar_texpos`, `rough_texpos1/2`, `wood_texpos`, `cheese_texpos1/2` | **nobody**, until RM does it |

A tool's texpos lives on the itemdef, shared by every material the tool
can be made of, so DF has no choice but to tint it. A material's texpos
is already specific to one material, so DF draws it exactly as given.

**Confirmed by direct experiment.** Green coke and coke breeze were set
to RED and their sprites did not move at all. Not darker, not shifted,
identical. That is the signature of no tint being applied, not of a tint
with nothing to work on.

Supporting measurement, across the 22 materials dumped in
`df_data_reference`: `bar_texpos` is 0 in all 22, `texflag` is 0 in all
22, and `boulder_texpos1` is set on only 7, always shared between
lookalike pairs (FIRE_CLAY/KAOLINITE 42371, LIMESTONE/MARBLE 42365,
MAGNETITE/TETRAHEDRITE 42383, OBSIDIAN 42384). Vanilla only writes a
material texpos where the materials sharing it already look alike, which
is what you would expect if writing it costs you the tint. In play,
limestone and marble render the same sprite while the materials differ
in colour.

---

## 2. The ramps

Vanilla item art uses a small number of fixed ramps sharing one shadow
colour. Two cover almost everything.

**NEUTRAL**, off `ITEM_CONSTRUCTION 2:3` and `1:1`. Stone, metal, glass,
bone, cloth. **This is the ramp all tintable art belongs on.**

```
#FFFFFF  255      #6B7076  118
#C7C4B4  199      #5A5E65  101
#A5A6A5  166      #494C54   84
#8A9091  145      #3C3E46   70
                  #2F3038   56   also at alpha 128
```

**WOOD**, off `ITEM_CONSTRUCTION 0:2`, the log. Bark on `TREES 7:3` is
100% on this ramp, five of its nine steps with nothing outside it, so it
is a shared palette and not one cell's quirk.

```
#D7D3D2  215      #605852   96
#B3A59E  179      #564F49   86
#94877E  148      #4E4743   78
#746A63  116      #463E3D   70
                  #2F3038   56   also at alpha 128
```

**CHARCOAL**, off `ITEM_CONSTRUCTION 1:4`. Pure grey, zero saturation,
and much darker: 39, 48, 57, 67, 77, 96, 112, 127.

`#2F3038` is the bottom step of both NEUTRAL and WOOD. Outline and
shadow are shared across the whole item set; only the body tones carry
the material family.

## 3. The two numbers

**Saturation ceiling 22.** Nothing adaptive exceeds it and nothing sits
between 22 and 90. Powder pile 22, generic bar 19, log 22, bark 22, soap
bar 19. Above it are the fixed colour cells: potash 170, pearlash 102,
straw 133, the vanilla branch 94.

Saturation is not flat across a ramp. On WOOD it peaks at 21 and 22 in
the mid values and falls to 5 at the highlight and 9 at the shadow. The
colour lives in the middle of the value range and drains out of both
ends, which is what stops a red wood tinting to a crayon.

**Value floor 56, ceiling 199 or higher.** Generic bar 56-255, jug
56-255, log 56-215, powder 56-255. A tint has nothing to work on below
that. The two that sit under it, coke at 38-114 and charcoal at 39-127,
are both dedicated fixed-colour cells.

This one bit us: the coke sprites were drawn on the CHARCOAL ramp, which
was right when the art had to look like coal unaided and wrong the
moment a tint arrived. Multiplying already dark art by an already dark
descriptor gave a flat blob with no readable form, mean value 17. On
NEUTRAL the same shapes tint to mean 27 with the lumps still legible.
**Darkness is the descriptor's job, never the art's.**

## 4. Retoning an existing sprite

**Match by value** when the source already shares a value structure with
the target ramp. Map each step to the nearest target step by value and
the artwork is unchanged pixel for pixel. The vanilla branch went this
way: its six steps at 185, 158, 119, 96, 72, 56 land on WOOD's 179, 148,
116, 96, 70, 56.

**Stretch by rank** when the source sits outside the band. Rank the
distinct values darkest to lightest and map rank to rank. Charcoal's
eight steps spread across NEUTRAL's eight this way.

**Spread by rank proportionally** when the counts differ. Vanilla cells
carry between 7 and 18 distinct values; target index
`round(i * 8 / (n - 1))` keeps the relative shading whatever `n` is.
This is what the vanilla set in section 8 uses.

---

## 5. The TINT: system

Since DF will not tint a written material slot, RM does it: read the
material's colour, multiply the grey art in Lua, and hand DF a texture
that is already the right colour.

```json
"graphics": { "bar": { "source": "TINT:powder" } }
```

### The chain

```
material.state_color.Solid          index into descriptors.PATTERNS (DF's color_pattern)
patterns[p].colors[0]               the pattern's first colour: an index into descriptors.colors
colors[c].orig_rgb[0..2]            0-255 ints
dfhack.textures.createTileset(...)  pixels -> TexposHandle array
getTexposByHandle(h)                handle -> texpos
deleteHandle(h)                     teardown
```

### Packing is ABGR

```lua
(a << 24) | (b << 16) | (g << 8) | r
```

`Lua_API.txt` says "packed RBGA format (for example, #0022FF11)" and
that is its only mention anywhere. It describes the BYTE layout, not the
integer, so the obvious `0xRRGGBBAA` is wrong.

**Signature of getting it wrong:** sprites render as ghostly semi
transparent negatives, because alpha ends up tracking the red channel.
Dark dominant art goes INVISIBLE on the map while pale art survives
looking washed out.

**How to identify it in one look:** write a flat fill of 200,100,50 at
full alpha. Each candidate order renders it unmistakably differently.
Orange opaque is rgba, violet see-through is argb, red-pink see-through
is abgr, blue-teal opaque is bgra.

### The blend

```
DESAT    = 0       desaturate the DESCRIPTOR toward its own luminance
STRENGTH = 0.75    lerp from untinted art toward the full multiply
```

Tuned in play against vanilla boulders. `STRENGTH` exists because a dark
descriptor multiplied onto anything goes very dark: CHARCOAL is
54:69:79, roughly a quarter in every channel, so even art topping at 199
lands near 50 and loses its shading. `DESAT` exists for descriptors with
a zeroed channel and settled at 0 once the lift proved sufficient.

### Descriptor traps

**A zeroed channel wrecks a multiply.** MAROON is 128:0:0 and BLACK is
0:0:0. There is nothing left for the shading to carry, so the sprite
collapses onto the live channel or to a flat silhouette. `DESAT` is the
lever if it bites.

**Colour cannot separate materials that share a descriptor.** All five
coke family materials declare CHARCOAL. Tinting cannot tell them apart,
so the SHAPE has to, which is why green coke got coarse lumps and breeze
got dust.

### Reserved range, not dynamic

The dynamic range is periodically wiped and the handle exists so you can
re-resolve. **We cannot: a material slot holds a raw integer, not a
handle.** Once the vector is wiped that integer points at whatever now
occupies the index and the material silently wears somebody else's
sprite. Reserved is never wiped.

The catch: reserved is a fixed size buffer and DFHack falls back to
dynamic SILENTLY when it is full, with no way to ask which you got. A
measured datapoint, from one session log: RM already loads 97 reserved
cells before the tint system asks for anything, 96 of them `retort.png`.
The tint system wants one per art-and-colour pairing, so a handful. If
sprites ever start swapping themselves after a long session, a full
reserved buffer is the first suspect.

### Art must be Lua data, not a PNG

`loadTileset` returns TexposHandles, not pixels, and there is no way to
read a PNG's pixels back out of DF. Anything we intend to tint has to
exist as a char map. That splits the sprites permanently:

* **tool sprites** stay on the PNG sheet, because DF tints those
* **material sprites** are char maps, because we do

When the sheet and a char map disagree, the char map wins.

---

## 6. The failure that looks like success

**Read this before debugging anything in this system.**

When a `TINT:` source fails, nothing is written and the slot keeps what
it had. On a fresh load that is **0**, and 0 means "use DF's default item
sprite", which DF tints. So a total failure renders as a correctly
coloured default bar or boulder.

**Correct colour on a vanilla shape means this is failing, not working.**
The shapes are the test, not the colours.

Every failure path logs at level 0 as ERROR and says so in those terms.

## 7. Where it hooks in, and the trap in that

There are **two** material appliers in `refinish-sprite-engine.lua` and
both need the interception:

* `apply_edits`, the `MATERIAL:<token>#<slot>` target grammar. Tagged
  `SPRITE_EDITS` in the log. This is what `making-fuel-ash-sprite.lua`
  uses.
* `apply_to_material`, which walks a module's JSON `graphics` block.
  Tagged `GRAPHICS` in the log.

They call `resolve_source` from separate call sites. Patching only one
made peat work and the four JSON materials fail, which read as the
system being broken rather than half-wired.

Both intercept BEFORE `resolve_source`, because its signature is
`(src, default_slot)` with no access to the material, and a manufactured
texpos needs the material's colour. Threading a third argument through
would touch all seven call sites when only two need it.

`resolve_source`'s last fallback treats an unrecognised source as a
donor material token, so an unintercepted `TINT:` fails as
`material not found: TINT:green_coke`. Any malformed source fails that
way; `GLUE`'s long standing `TODO_COL:TODO_ROW:TODO_ROW` is the same
line.

**Registration must happen before the injects.** A `TINT:` source is
resolved during the inject, so the art module is reqscripted at
`making_fuel.lua` load time, not in `start_background_scripts`, which
runs after. Registering is pure data and touches nothing in DF, so load
time is safe.

One consequence: load-time logging predates `_G.refinish_log_event`, so
the registration line goes to the console rather than the session file.

## 8. The files

| file | holds |
|---|---|
| `refinish-sprite-art.lua` | core: ramp, packing, blend, build, registry, cache, `release_all` |
| `refinish-sprite-art-vanilla.lua` | core: the vanilla default for every material slot, retoned |
| `making-fuel-sprite-art.lua` | module: coal, green_coke, breeze, powder |
| `refinish-tint-probe.lua` | live probe, writes a slot with undo, no recycle |

The vanilla set, all retoned to 56-255 and prefixed `vanilla_` so module
art cannot collide:

| art | source | for |
|---|---|---|
| `vanilla_boulder` | `BOULDERS 0:1` | `boulder1/2` |
| `vanilla_rough_gem` | `BOULDERS 0:10` | `rough1/2` |
| `vanilla_bar` | `ITEM_CONSTRUCTION 0:1` | `bar` |
| `vanilla_block` | `ITEM_CONSTRUCTION 0:0` | blocks |
| `vanilla_log` | `ITEM_CONSTRUCTION 0:2` | `wood_texpos` |
| `vanilla_soap_bar` | `ITEM_CONSTRUCTION 1:1` | small bar |
| `vanilla_powder` | `ITEM_CONSTRUCTION 2:3` | powders |
| `vanilla_cheese` | `ITEM_FOOD 0:1` | `cheese1/2` |

Pointing a slot at `TINT:vanilla_bar` gets back exactly what leaving it
at 0 would have given, except RM now controls it.

## 9. Dead ends, recorded so they are not retried

* **Value range is not why material slots fail to adapt.** The red test
  rules it out: a too-dark sprite would still shift hue.
* **`texflag` is not a tint switch.** `PEAT_DRIED` carries none and does
  not adapt; clearing it on peat and the cokes changed nothing.
* **`texflag` is not required for a material texpos to render.** Sprites
  stayed visible with it cleared, contradicting the belief written into
  `making-fuel-ash-sprite.lua`.
* **There is no greyscale texpos variant on a material.** The complete
  field list off a live struct is `wood_texpos`, `rough_texpos1/2`,
  `cheese_texpos1/2`, `boulder_texpos1/2`, `bar_texpos`, `texflag`.
  Nothing else.
* **Inference, unresolved:** the tint is likely a property of the
  TEXTURE rather than the slot, since DF registers its own default item
  textures and knows those are tintable while anything from
  `createTileset` is just a texture. If there is a registration flag
  that says "tint this", it is not reachable from the Lua API. This is
  the shape that fits, not a finding.
