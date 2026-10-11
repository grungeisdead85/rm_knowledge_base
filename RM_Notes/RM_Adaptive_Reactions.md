# RM Adaptive Reactions

Status: mechanism proven, prototype running in Making Fuel, not yet in the engine.
Established by in-game testing on August 13. Every claim marked CONFIRMED below was
observed directly. Claims marked UNTESTED are open.

---

## 1. What this is

A normal DF reaction is fixed at worldgen. It takes N of a thing and makes M of another
thing, and both numbers are written in the raws.

An adaptive reaction decides those numbers at job time, by reading what the player
actually put in front of it.

This matters because DF has no other way to express "it depends." A corpse reagent
cannot distinguish a rat from a dragon, so any hand-written charcoal reaction has to
pick one number and be wrong for every creature that is not that size. The size range
in vanilla is roughly 3,300 to 1 between an adult dwarf and a giant sperm whale.

Adaptive reactions solve this in two directions:

- **Output adapts.** One dragon corpse produces 20 charcoal. One dwarf corpse produces 1.
- **Input adapts.** A rat is worth 0.07 charcoal, so the reaction demands 15 rats.

Neither requires touching the raws, and both work on modded content the module has
never heard of.

---

## 2. The mechanism

### 2.1 Ghost reactions

RM already had this. A ghost is a runtime clone of a base reaction, injected into
`world.raws.reactions.reactions` with a unique code, kept out of workshop menus, and
swapped onto a live job by writing `job.reaction_name`.

Precedent is `build_ghost_grinder_jit` in `refinish_steel.lua`. That one builds its
reagents from scratch off a vanilla template rather than cloning, which is why it never
encountered the trap in 2.3 below.

**CONFIRMED:** the ghost owns everything about the job except the items already
attached when the swap happened. Name, products and reagents all come from the ghost.

Ghosts are disposable. They are wiped on data cycle like any other RM asset, they carry
the module prefix so the shutdown sweep collects them, and RM's existing ghost protocols
already handle reactions that were live when a shutdown occurred.

### 2.2 The two-sided rule

This is the core insight and everything else follows from it.

**`job.job_items.elements` drives collection. The reaction's reagents drive completion.**

`job_items` is a `vector<job_item*>` materialised from the base reaction at job creation.
It is never re-derived. It is what DF reads when deciding what to go and fetch.

The reaction's reagent list is what DF reads at completion, to check the job is
satisfiable and to consume the inputs.

Change one without the other and the job breaks in a way that looks like a different
problem than it is:

| Changed | Symptom |
|---|---|
| Reagents only | One item hauled, job aborts with no output |
| Filters only | Right number of items hauled, job aborts with no output |
| Both, mislinked | Right number hauled, job aborts with no output |
| Both, linked | Works |

All three failure modes look identical from the game. Only a log dump of both sides
distinguishes them. Budget for that when debugging.

### 2.3 Adding input slots

To make a ghost consume more than its base reaction, **all four** of the following are
required. None is sufficient alone.

**1. Clone extra reagents onto the ghost, each with a unique `.code`.**
DF keys reagents by that string. Duplicated codes collapse into one slot. Cloning the
already-material-locked reagent is correct; the lock does not prevent hauling.

**2. Clone matching entries into `job.job_items.elements`.**
Clone from `elements[0]` using `proto._type:new()` then `:assign(proto)`.

**3. Set `.reagent_index` on each cloned filter to its own slot index.**

```lua
local proto = els[0]
for _ = 1, extra_slots do
    local ji = proto._type:new()
    ji:assign(proto)
    ji.reagent_index = #els   -- BEFORE the insert
    els:insert('#', ji)
end
```

`assign()` copies the prototype's `reagent_index`, so every clone claims reagent 0
unless corrected. **This was the eight-round bug.** Symptom: the right number of items
get hauled and the job then aborts silently.

**4. Do NOT raise `.quantity` on an existing reagent.**
CONFIRMED to deadlock the job. The dwarf hauls what `job_items` asked for, completion
demands more, and the job abandons. Slots are the only handle on input count.

### 2.4 Adapting output

**CONFIRMED:** `products[0].count` can be rewritten on a live ghost while hauling is
still in progress, and completion honours the latest value.

This is what lets output track the real haul rather than the first item. Write it at
swap time and again on every poll as items arrive.

**CONFIRMED:** `count = 0` is safe. Jobs pass through zero on the way up without
erroring or aborting.

### 2.5 What extra slots do not do

**CONFIRMED:** cloned filters carry `mat_type = -1, mat_index = -1` while the reagents
carry the material lock. Hauling reads the filters, so **extra slots accept any item of
the right type, not the creature that opened the job.**

A rat job will happily accept aardvarks. This is why output must be re-evaluated from
what actually arrived rather than computed once from the first item.

**UNTESTED:** whether writing `mat_type` and `mat_index` onto the filters would
constrain hauling. Worth knowing, but the live re-evaluation makes it optional rather
than necessary.

---

## 3. The yield model

### 3.1 Units

**CONFIRMED:** every size DFHack reports is one tenth of the figure the wiki publishes.
This holds on both the item side and the creature side.

| thing | wiki | DFHack |
|---|---|---|
| wood log | 50,000 | 5,000 |
| metal bar | 6,000 | 600 |
| boulder | 100,000 | 10,000 |
| adult dwarf | 60,000 | 6,000 |
| giant sperm whale | 200,000,000 | 20,000,000 |

**Work in internal units and never convert.** The wiki's own note that custom sizes
round to the nearest multiple of ten is the same fact seen from the other side.

### 3.2 The curve

```
yield = ( size * material_factor / ANCHOR ) ^ EXPONENT
```

| constant | value | meaning |
|---|---|---|
| `ANCHOR` | 5000 | one log, one charcoal. The vanilla convention, read as the unit |
| `material_factor` | 5/6 for flesh | puts an adult dwarf corpse on exactly 1 |
| `EXPONENT` | 0.5 | compresses the 3,300x creature range into something playable |

`5/6` must be written as a fraction. The decimal `0.833` puts a dwarf on 0.99980, which
is under 1, and `math.ceil` then turns a 0.02 percent shortfall into a whole extra
corpse. See 5.2.

### 3.3 Why sub-linear

Linear at the dwarf anchor gives a giant sperm whale 3,333 charcoal. That is item spam,
an FPS event, and the permanent end of fuel scarcity.

Square root gives a usable spread with no cap needed:

| creature | adult_size | yield | slots | result |
|---|---|---|---|---|
| damselfly | 1 | 0.013 | 77 | beyond cap |
| rat | 30 | 0.071 | 15 | 15 rats : 1 charcoal |
| cat | 500 | 0.289 | 4 | 4 cats : 1 charcoal |
| dog | 3,000 | 0.707 | 2 | 2 dogs : 1 charcoal |
| dwarf | 6,000 | 1.000 | 1 | 1 : 1 |
| water buffalo | 100,000 | 4.08 | 1 | 1 : 4 |
| elephant | 500,000 | 9.13 | 1 | 1 : 9 |
| dragon | 2,500,000 | 20.41 | 1 | 1 : 20 |
| giant sperm whale | 20,000,000 | 57.74 | 1 | 1 : 58 |

Verified in game: dwarf 1:1, cat 4:1, rat 15:1, dragon 1:20, whale 1:58.

**Known property: a sub-linear curve is not additive.** N pieces of size S/N yield
`sqrt(N)` times what the whole yields. This is arithmetic, not a tuning problem, and
it applies to any exponent below 1. It means butchering before charring would be
profitable if pieces were curved independently.

Mitigation for corpsepieces, when they are implemented: compute the whole creature's
yield and divide the **finished yield** by a piece divisor. Dividing the input size
instead reintroduces the exploit.

### 3.4 Slot arithmetic

```lua
if y >= 1 - EPSILON then return 0 end
local needed = math.ceil((1 / y) - EPSILON)
if needed > MAX_REAGENT_SLOTS then needed = MAX_REAGENT_SLOTS end
return needed - 1                  -- EXTRA slots, base already has one
```

`EPSILON` of 0.01 guards against float shortfalls turning into a whole extra corpse.
It is a guard, not a substitute for exact arithmetic: fix the constants first.

**Nothing is rounded until the final output count.** The running sum stays a float so
fifteen rats at 0.070711 each accumulate honestly rather than being flattened fifteen
times.

`MAX_REAGENT_SLOTS` is currently 16. Tested to 15 without trouble. **UNTESTED:** DF's
real ceiling, and what a large slot count does to pathing.

### 3.5 Sizing versus scoring

Two different reads, deliberately:

- **The first item sizes the job.** It is all we have when the ghost is built.
  Computed once and cached per job id. Recomputing as items arrive causes the builder
  and the filter cloner to disagree. See 5.1.
- **The full haul scores the output.** Recomputed every poll from everything attached.

This is what makes mixed hauls fair. A rat opens 15 slots; if aardvarks fill them, the
output reflects aardvarks.

---

## 4. Corpse item quirks

Corpses are hostile to every obvious accessor. All CONFIRMED by probe.

| accessor | on CORPSE / CORPSEPIECE | use instead |
|---|---|---|
| `getWeight()` | does not exist as a vmethod on any item class | `getVolume()` |
| `getVolume()` | returns 350 for everything, rabbit to sperm whale | `caste.misc.adult_size` |
| `getMaterial()` | returns -1 | `dfhack.matinfo.decode(item)` |
| `getMaterialIndex()` | returns -1 | as above |

Size path:

```lua
df.global.world.raws.creatures.all[item.race].caste[item.caste].misc.adult_size
```

`item.race` and `item.caste` read cleanly off corpses, corpsepieces and remains.

**`caste.body_size_1/2/3` do not exist** under those names. The BODY_SIZE growth curve
is not reachable that way, so **individual size is not available**. A dwarf child and a
dwarf adult both read 6,000. Per-race and per-caste differentiation works; per-individual
does not. Caste matters: giant peregrine falcon reads 20,770 female against 11,329 male.

**Ghost cache keys must include race and caste, not just material.** A corpse's
`mat_index` is the creature but its `mat_type` is whichever tissue dominates, so the
same dwarf appears as BONE on one corpse and SKIN on another. Observed: giant
rattlesnake came through as tissue 21 while dwarf, cat and rat came through as 22.

**REMAINS behave differently.** Fixed `getVolume()` of 200 regardless of creature, and
`getMaterial()` returns the race directly rather than -1. Damselflies are REMAINS, not
CORPSE.

---

## 5. Failure modes seen during development

Recorded so they are not rediscovered.

### 5.1 Recomputing the slot count

`extra_slots_for()` reads `job.items`, which grows as corpses arrive. Called fresh on
every poll, the ghost builder and the filter cloner saw different hauls and disagreed
on the count. A dwarf job sized at zero extra slots silently grew one the moment a
second corpse appeared.

**Compute once on the first poll that sees the job. Cache by job id.**

### 5.2 Rounded constants meeting ceil

`0.833` instead of `5/6` put a dwarf on 0.99980. `math.ceil(1 / 0.99980)` is 2, so the
reaction demanded a second corpse. Displayed as `raw=1.000` because the log format was
three decimal places.

**Log floats to six decimals during development.** A displayed 1.000 can be anything
from 0.9995 up.

### 5.3 Silent pcall swallowing a rename

A variable rename hit the declaration and missed three uses inside a `pcall`. Every
clone threw, the counter stayed at 0, and it logged as "added 0" rather than as an
error. The filters still cloned, so the job hauled two corpses and consumed one.

**A pcall that reports success or failure but not the error message will hide a typo
as a plausible-looking zero.**

### 5.4 Guards inherited from removed code

The live re-evaluation was gated on `#job.items > 1`, inherited from a debug dump where
a single item was not worth printing. Effect: one-item jobs never re-evaluated, so
dwarves and dragons completed on whatever the builder had left behind.

### 5.5 Phase gates as supersets

A test phase gated at `>= 2` fired during a `>= 3` test and invalidated it. **Use exact
equality for mutually exclusive test modes.**

---

## 6. What is owed

| item | status |
|---|---|
| Stall handling when not enough items arrive | not started |
| Char as the stall output and fractional remainder | designed, not built |
| Large output ergonomics (58 bars is hard to read in the stock list) | open |
| Corpsepieces, remains, and other creature-derived classes | not started |
| Strip the test scaffolding | pending |
| Move from module watcher into the engine | planned |

**Char.** A reaction that cannot gather enough input does not fail, it produces char.
X char converts to one charcoal. This turns the not-enough-input case from an error
into part of the industry, and gives the fractional remainder somewhere to go so
nothing is silently rounded away. Kindling is the precedent: a conversion currency
that adds a step rather than papering over a gap.

**Engine migration.** This is general. Any module wanting input count or output count to
respond to what the player actually supplies needs exactly this mechanism. The intended
shape is a declarative block in the reactions JSON naming a yield policy, with the engine
owning the polling, the ghost lifecycle and the arithmetic. Modules should not each carry
their own watcher; that is load on every save for work the engine could do once.
