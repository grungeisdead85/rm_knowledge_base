# RM Module Supply Chain Class Reference
## Version 0.4

Supersedes 0.3. The 0.3 vocabulary (the REFINISH_ prefix, the
processing state layer, the functional role layer) is retired in full.
The change log at the end records what happened to each group and why.

---

## Purpose

This document defines the two vocabularies an RM module puts on a
material so that reactions can find it without naming it:

- `reaction_class` says what a material IS.
- `reaction_product` says what a material BECOMES.

A reaction that names a material by id is locked to the module that
defined it. A reaction that asks for a class or a product code accepts
anything that carries it, from any module, including modules not yet
written. That is the whole point of the system, and it is the only
channel through which modules interact.

---

## What DF gives us

Three facts, all probe-verified, that shape every rule below.

1. **A reagent reads one class.** `reaction_reagent_itemst.reaction_class`
   is a single string. A reagent can ask "is it PITCH", never "is it
   PITCH and BINDER". A material can carry any number of classes, so
   the vocabulary is sized by the questions reactions ask, not by the
   materials that exist.

2. **A reagent can also read one product code**
   (`has_material_reaction_product`), and a product can take its
   material from that code on the reagent that satisfied it
   (`GET_MATERIAL_PRODUCT`). This is how one vanilla "tan a hide"
   reaction serves every creature: each hide names its own leather
   under `TAN_MAT`.

3. **Vanilla itself barely uses classes.** `FLUX`, `CALCIUM_CARBONATE`
   and `CAN_GLAZE` are the lot. Everything that looks like a role
   (`FIRED_MAT`, `GLAZE_MAT`, `SOAP_MAT`, `RENDER_MAT`, `TAN_MAT`,
   `PRESS_LIQUID_MAT`, `SEED_MAT`, `DRINK_MAT`) is a product code,
   because a role is defined by what it produces.

So: classes for identity and kind, product codes for derivation. Most
of what 0.3 got wrong was trying to say "becomes" with a class, which
a class cannot carry into a product.

---

## The four mechanisms

Whenever two reactions differ only by their input, they belong in
exactly one of these bins. Sort before writing.

| The question | Mechanism | Example |
|---|---|---|
| Exactly this module's material | identity class on the reagent (or `mat_id`, see below) | FRACTIONATE wants coal tar |
| Several qualify, same product regardless | family class | any TAR burns to carbon black |
| Several qualify, product follows the input | product code on the input; `has_material_reaction_product` plus `get_material_product` on the reaction | any tar boils to its own pitch |
| Only the count follows the input | adaptive yield (the ghost) | charcoal from corpses |

Two notes on the last row. Adaptive yield is for open sets: any
corpse, any furniture, anything the module has never heard of. For a
closed set of two or three known inputs with different counts, write
two or three fixed reactions on identity. It is simpler, and it is
what the raws can express on their own.

`mat_id` and the identity class are interchangeable inside a module.
Prefer the class on reagents, because the reaction is then already
cross-module at no cost. `mat_id` remains correct for vanilla
materials (lignite, bituminous coal, jet, clay, graphite, iron), which
cannot carry module classes from JSON.

---

## Reaction classes

Two layers. Nothing else.

### Identity

Every module material carries its own key as a class, verbatim,
without the module prefix. `MAKING_FUEL_TAR_COAL` carries `TAR_COAL`.
Raws minerals carry their inorganic id: `PEAT` carries `PEAT`.

This requires no decision, and it is the cross-module `mat_id`: it is
how another module makes coal tar and this module's reactions take it.
Code may read identity too; the ghost classifier keys on `PEAT`.

### Family

A family class exists only when at least one reaction asks for the
family instead of a member, and would produce the same thing whichever
member arrived. It is named as the noun the members ARE, never as the
role an asker wants: `PITCH`, not `BITUMINOUS_BINDER`; `TAR`, not
`TAR_SOURCE`.

A family with no asker is not added, however plausible. The day a
reaction asks for it, it is added with its members and its asker in
the same edit. Until then it is a word nothing reads, and unread words
rot: the 0.3 raws comment said bitumen was in the binder economy while
its tags said otherwise, and nothing noticed because nothing read them.

### The surprise test

A family is a claim that its members are interchangeable FOR THE
QUESTIONS ITS ASKERS ASK, and nothing more. It is not a claim that
they are the same substance.

Before a material joins a family, walk every asker: would a player
who knows the real material be surprised to see it accepted there?
One surprise means either the material stays out of the family, or
that asker leaves the family and goes to identity. Realism is enforced
per asker, at the reaction, because with one class per reagent that is
the only place it can be enforced.

Worked example. `PITCH` = {wood pitch, coal pitch, bitumen}. Askers:
the four briquette presses. Any of the three binds fines; no surprise.
`COKE_PITCH` was also an asker, and wood pitch does not coke. So
`COKE_PITCH` leaves the family and asks `PITCH_COAL` by identity. The
family survives, the accurate reaction survives, and no new word was
needed.

An abstraction is acceptable when accurate modelling would add no
distinct player decision. Accepted abstractions are recorded in the
module's section below, so "we fudged this" is a written fact rather
than a worry.

### Naming

- Bare names, no prefix. Vanilla's classes are bare, and two mods
  meeting on a word like `COKE` is the feature.
- Complete words. `CALCIUM_SOURCE`, never `CALC_SRC`.
- Keys are `THING_QUALIFIER`: `TAR_COAL`, `PITCH_WOOD`, `DUST_COAL`,
  `BREEZE_COKE`. Keep it, and a family is always the first word of its
  members' identities. `FINE_COKE` beside `COAL_FINE` is what breaking
  it looks like.

### What a class never encodes

- **Form.** Item type carries it. Coal dust is fine because it is a
  powder item, not because it carries `FINE`.
- **Destination.** That is a product code.
- **Heat.** That is the fuel tier ladder, owned by the Making Fuel
  taxonomy document. The tier classes are families in this vocabulary
  (their askers are the furnaces) but the ladder is designed there.
- **Process history and hazard.** `THERMALLY_PROCESSED`, `FLAMMABLE`,
  `TOXIC`: true, and asked by nothing.

---

## Reaction products

A `reaction_product` entry on a material is a labelled pointer to
another material: "under this code, I become that." A reagent asks for
the code; a product reads the pointer off whichever reagent qualified.

### Rules

- **Vanilla codes take precedence.** If vanilla has a code for the
  concept, use it, and the module's material becomes usable in
  vanilla's own jobs. If the concept differs from vanilla's, use a
  module code, so the module's material does NOT leak into vanilla
  jobs. Sealing a jug with pitch is not glazing: a pitch carrying
  `GLAZE_MAT` appears in vanilla's glaze menu, which is a seam.
- **A code is added when a reaction asks for it**, same as a family.
- **Targets must be inorganic.** The engine resolves `mat_id` against
  the inorganic table and writes `mat_type 0`. The plant-hosted coals
  cannot be product targets today.
- **Cross-module targets work.** Unresolved targets are deferred to a
  final pass after every module has injected; a target still missing
  then is logged as a dangling reference.

### Shapes

Material side (materials JSON). `item_type` and `item_subtype` are
ignored by the engine and should be omitted:

```json
"reaction_products": [
    { "id": "PITCH_MAT", "mat_id": "MAKING_FUEL_PITCH_WOOD" }
]
```

Raws side, for worldgen minerals:

```
[MATERIAL_REACTION_PRODUCT:SEAL_MAT:INORGANIC:BITUMEN]
```

Reagent side (reactions JSON). The class filter is omitted when the
code alone selects correctly, as vanilla does:

```json
{ "code": "tar", "type": "LIQUID_INORGANIC_ANY", "quantity": 150,
  "has_material_reaction_product": "PITCH_MAT",
  "flags": { "in_container": true } }
```

Product side, item or improvement:

```json
{ "type": "BOULDER", "count": 1, "dimension": 150,
  "get_material_product": { "reagent_code": "tar", "product_code": "PITCH_MAT" } }
```

Improvement products support only `get_material_product` in the
engine today. An improvement whose material is the reagent itself (a
pitch seal is made of pitch) therefore needs a self-referencing code
on the material. Engine support for `get_material_same` on
improvements would remove that need; until then, the self-reference is
the pattern.

### Codes in use

| Code | Origin | Meaning | Carried by |
|---|---|---|---|
| `FIRED_MAT` | vanilla | what a clay fires into | vanilla clays |
| `SEED_MAT`, `DRINK_MAT`, `PRESS_LIQUID_MAT`, `PRESS_PAPER_MAT` | vanilla | plant processing outputs | vanilla plants |
| `GLAZE_MAT` | vanilla | what a material glazes with | vanilla ash and tin; no module material |
| `PITCH_MAT` | module | what a tar boils down to | TAR_WOOD, TAR_COAL |
| `SEAL_MAT` | module | what a material seals or coats with (itself) | PITCH_WOOD, PITCH_COAL, BITUMEN, WAX_PARAFFIN, CREOSOTE |

---

## Economic stone

DF calls a stone economic if it carries ANY reaction class or ANY
reaction product. A `BOULDER_ANY` reagent with `non_economic: true`
means "accept ONLY non-economic stone." Since every module material
carries at least its identity class, every module material is economic
and invisible to that wildcard. This is intended, and it is the second
reason identity is mandatory: a module boulder with no class would be
grabbed by any "any cheap stone" reagent in any mod.

---

## Making Fuel

### Families

| Family | Members | Asked by |
|---|---|---|
| `FUEL` | every dried and carbonized fuel | fuel access: the primary class, every furnace not listed in `FUEL_TIERS` |
| `FUEL_SMELTING` | charcoal, coke, refined coal; coal dust and coke breeze at Round D | fuel access: `FUEL_TIERS` for Smelter, GlassFurnace, MetalsmithsForge |
| `TAR` | TAR_WOOD, TAR_COAL, OIL_BONE | BURN_CARBON_BLACK |
| `PITCH` | PITCH_WOOD, PITCH_COAL, BITUMEN | PRESS_DUST_BRIQUETTES, PRESS_BRIQUETTES, PRESS_CHARCOAL_BRIQUETTES, PRESS_BREEZE_BRIQUETTES |
| `ACID` | VINEGAR_WOOD | MAKE_ANILINE, DYE_MAGENTA |
| `ALKALI` | AMMONIA | DYE_MAUVE, DYE_INDIGO, DYE_ALIZARIN |
| `POZZOLAN` | ASH_COAL; VOLCANIC_SAND (Making Concrete) | FIRE_CALCIUM_SILICATE_ASH |

The tier ladder (`FUEL_CRUCIBLE` and `FUEL_INDUSTRIAL` reserved) is
owned by `making_fuel_taxonomy.md`.

### Identity

Every material, its key. Three materials currently miss theirs and
carry synonyms instead: OIL_BONE (has TAR_BONE), VINEGAR_WOOD (has
WOOD_VINEGAR, VINEGAR, PYROLIGNEOUS_ACID), WAX_PARAFFIN (has WAX,
PARAFFIN_WAX). The plant-hosted coals and the raws minerals already
conform.

### Reactions that change under 0.4

| Reaction | Change |
|---|---|
| BOIL_PITCH_WOOD, BOIL_PITCH_COAL | one reaction, BOIL_PITCH: reagent asks `PITCH_MAT`, product reads it |
| BOIL_SHALE_PITCH | folds into BOIL_PITCH once shale oil exists as a material and carries `PITCH_MAT` |
| REFINE_WOOD_TAR, REFINE_COAL_TAR | one reaction, REFINE_TAR, same pattern; creosote stays a fixed second product |
| COKE_PITCH | asks `PITCH_COAL` by identity (wood pitch does not coke); optional COKE_BITUMEN on identity at lower yield |
| GLAZE_JUG_PITCH | asks `SEAL_MAT`, no class filter; rename SEAL_JUG_PITCH |
| TREAT_WOOD_CREOSOTE | asks `SEAL_MAT`; dead today, because creosote carries no product code at all |
| WASH_TAR_SAND | asks `SAND_TAR` (currently `WASH_FEED`, which nothing carries) |
| the four PRESS_*_BRIQUETTES | `BITUMINOUS_BINDER` becomes `PITCH` |
| SLAKE_CARBIDE_TAR | `CARBIDE` becomes `CALCIUM_CARBIDE` |
| BURN_CARBON_BLACK_OIL | `OIL_HEAVY` becomes `CREOSOTE`; creosote is a tar fraction, not a tar, and stays out of `TAR` |
| COKE_COAL_DUST, PRESS_DUST_BRIQUETTES, PRESS_CLAY_BRIQUETTES | `COAL_FINE` becomes `DUST_COAL` |
| PRESS_BREEZE_BRIQUETTES | `FINE_COKE` becomes `BREEZE_COKE` |
| FRACTIONATE_TAR_COAL | unchanged; correctly asks `TAR_COAL` |

Material-side corrections in the same pass: NAPHTHALENE and
WAX_PARAFFIN carry `GLAZE_MAT` pointing at PITCH_WOOD. Naphthalene
seals nothing and loses the entry; wax seals and gets `SEAL_MAT`
pointing at itself. PITCH_WOOD and PITCH_COAL swap `GLAZE_MAT` for
`SEAL_MAT`.

### Abstractions on record

| Abstraction | Status |
|---|---|
| CREOSOTE is one material for wood creosote and coal tar creosote | accepted; no reaction distinguishes them |
| Wood vinegar stands in for a mineral acid in aniline and magenta synthesis | accepted until a mineral acid exists; brimstone from the fluxed coke line is the natural source if one is ever wanted |
| Ammonia stands in for an alkali in the dye syntheses | accepted, same reason |
| Wood pitch binds briquettes | accepted; the press does not care which pitch |
| Shale oil boils to coal pitch | candidate for correction: petroleum residue is bitumen, and BITUMEN exists; decide with the shale line |
| Retorted corpses yield charcoal | accepted until BONE_CHAR exists (taxonomy Round C) |

### Cross-module hooks

The identity classes are the hooks. A module that makes coal tar tags
it `TAR_COAL` and every Making Fuel tar reaction accepts it. A module
that wants "any acid" asks `ACID`. Families are added on request when
a real reaction outside this module asks for one.

---

## Making Concrete

Carries the 0.3 property vocabulary (`RAW`, `MECHANICALLY_PROCESSED`,
`THERMALLY_PROCESSED`, `CHEMICALLY_PROCESSED`, `BINDER`, `AGGREGATE`,
`CALCIUM_SILICATE`, `POZZOLAN`). None of Concrete's own reactions
filter on any of them. Pending a 0.4 pass: identity on every material,
`POZZOLAN` kept (it has an asker in Making Fuel), the rest retired
unless a reaction asks. Not urgent; nothing is broken by the extra
words, only decorated.

## Making Metal

Its materials file is not in the project. Pending the same pass when
it is next touched.

---

## Change log: 0.3 to 0.4

Retired from Making Fuel, by group:

- **Property and hazard words**, no asker: SOLVENT, FLAMMABLE,
  FLAMMABLE_EXTREME, TOXIC, ANTISEPTIC, PRESERVATIVE, FUMIGANT,
  REFRACTORY, CARBON_REFRACTORY.
- **Role words**, no asker: MORDANT, SCOURING_AGENT, DYE_PRECURSOR,
  SYNTHETIC_DYE, ANILINE_DYE, PIGMENT, PIGMENT_BLACK, PIGMENT_RED,
  PIGMENT_BLUE, PIGMENT_PURPLE. Not wrong, early. They return with
  members and an asker when a reaction wants them.
- **Form words**: COAL_FINE, FINE_COKE, CARBON_FINE, FINE_CARBON,
  FUEL_FINE, FINE_FUEL. Form is item type.
- **Synonym identities**: TAR_BONE, WOOD_VINEGAR, VINEGAR,
  PYROLIGNEOUS_ACID, WAX, PARAFFIN_WAX, ASH_MINERAL, CARBIDE,
  ALCOHOL_WOOD, ALCOHOL_ALIPHATIC, FUEL_LIQUID, and STRAW on
  STRAW_DRIED. One identity per material, and it is the key.
- **Destination words**: the ten SOURCE_ classes on the raws minerals.
  "What it becomes" is a product code, and the retort reactions ask by
  identity or mat_id.
- **Private words**: WASH_FEED, BITUMINOUS_BINDER.
- **Dead filters** fixed: TAR_SHALE, WASH_FEED.

Retired RM-wide: the `REFINISH_` prefix, and the processing state
layer (RAW, THERMALLY_PROCESSED, CHEMICALLY_PROCESSED,
MECHANICALLY_PROCESSED, BYPRODUCT), which no reaction in any module
ever asked for.

Kept from 0.3: vanilla precedence, complete words, build only what a
reaction asks for, economic stone behaviour.

---

## Extending the vocabulary

Adding a class or a code:

1. Name the reaction that asks for it. No asker, no entry.
2. Is it identity? Then it is the key, and this document does not
   change.
3. Is the product the same whichever member arrives? Family class.
   Does the product follow the input? Product code.
4. Vanilla first: adopt a vanilla code if the concept matches; use a
   module code if it does not, so module materials stay out of
   vanilla jobs.
5. Run the surprise test across every asker.
6. Add it to the tables above with its members and its askers, in the
   same edit as the reaction.
