# RM Module Design Philosophy

## What This Document Is

This is the governing document for all RM module content. Every design
decision, every material definition, every reaction, every class
assignment must be consistent with the principles laid out here. When
in doubt, check this document. If a proposed change conflicts with
these principles, the change is wrong.

---

## What RM Is

Refinish Metal is the engine. It is adaptive, procedural, and universal.
RM responds to the content it finds in a loaded world — it scans
existing metals, evaluates existing reactions, and dynamically injects
finishing variants based on what's actually present. RM does not impose
content. It enhances what already exists.

RM's core guarantees:
- Universal compatibility with any mod combination
- No modification of raws or world generation
- Clean injection and clean removal (hotsave protocol)
- Deterministic, reproducible behavior across save cycles

These guarantees are non-negotiable and extend to everything that
uses the RM engine, including modules.

---

## What Modules Are

Modules are content. They are imposed, designed, opinionated. A module
declares "this material exists, this reaction exists, these workshops
can do these things." Modules use RM's injection engine to place their
content into the game at runtime, but they are not RM. They are an
ecosystem of independent content packs built on top of RM's capabilities.

A module is a standalone mod with its own identity:
- Its own info.txt with a unique mod ID
- Its own Lua registration file (from the universal template)
- Its own JSON data files (materials, reactions, categories)
- Its own data/ folder within its mod directory

Modules register with RM's engine via the listener API. When RM starts
up, it broadcasts a token call, and each registered module responds
with its data. RM validates, injects, and manages the lifecycle of
that data. On shutdown, RM sweeps everything clean.

---

## The Cardinal Rules

### 1. Modules never break.

No module may break when another module is absent, present, updated,
or replaced. Any combination of installed modules must produce a
working game. This is absolute.

If a player prefers ArgMOD alloys over Making Metal alloys, they
uninstall Making Metal and install ArgMOD. Everything works. Nothing
that Making Fuel or Making Concrete does should depend on Making Metal
specifically existing. If interactions existed between those modules,
they happened through shared infrastructure (reaction classes) that
any replacement module can independently opt into.

### 2. No module references another module's materials by name.

Cross-module material references by mat_id are forbidden. If module A
writes `"mat_id": "MAKING_METAL_ITE_ITE"` in a reagent, it breaks when
Making Metal isn't installed — the mat_id silently fails to resolve,
defaulting to mat_index -1 (wildcard), and the reaction grabs any
matching item type. This is the exact failure mode that caused the
distillation bug in Making Fuel's first prototype.

The correct way to create cross-module interaction is through shared
reaction_classes and material_reaction_products. These are semantic
labels that any module can independently assign to its own materials.
The connection exists without either module knowing about the other.

### 3. Every module must function perfectly in isolation.

A module installed alone, with no other modules, must work completely.
Every reaction must be satisfiable using only materials the module
itself provides plus vanilla materials that are verified to exist.
No reaction may have a hidden dependency on another module's output.

If a reaction benefits from cross-module materials (through reaction
class filtering), that's a bonus — not a requirement. The reaction
must have a valid execution path using only its own materials and
vanilla.

### 4. Vanilla asset references must be verified.

When a module references a specific vanilla material or reaction by
name (QUICKLIME, IRON, FLUX stones, LIGNITE_TO_COKE as a template),
it assumes that asset exists in the loaded world. But other mods can
cut or replace vanilla content. If a critical vanilla asset is missing,
the module must not break.

The engine must verify that referenced vanilla assets are present
before building reactions. If a vital asset is missing, the engine
generates a fallback replacement. This is engine-level infrastructure,
not something individual modules handle — modules declare their
vanilla dependencies, the engine ensures they're met.

### 5. Use accurate, real-world names.

Materials should be named after what they actually are using correct
terminology. Slag is slag. Calcite is calcite. Peat is peat.
Appropriate names let users reference common knowledge to understand
what they're looking at. Players who know metallurgy or chemistry
will appreciate the respect to detail, and players who don't will
learn something real.

We are not making dragon steel or upgradium. Those are cheap
generalizations — "cool steel" and "bonus in bar form" — a veneer
over nothing. We don't sell cool. We make accurate, effective
products that solve real gameplay problems. The user decides what's
cool. Configurations and module UI (when introduced) will give them
that control. The content itself earns respect by being right, not
by being flashy.

This applies to reaction_class names as well. `RM_CALCIUM_ITE` is
opaque. `RM_CALCIUM_SOURCE` describes function. Class names should
tell you what the class means without needing to look it up.

### 6. Build foundational infrastructure once, never remake it.

The module template, the class taxonomy, the engine's injection
pipeline — these are foundations. They get built once, built right,
and everything else builds on top. If something fails, only the
building fails, not the foundation. This is RM's core architectural
philosophy and it extends to the module ecosystem.

---

## Cross-Module Interaction

### The Problem

Modules will naturally produce materials that other modules could use.
Making Metal produces slag that Making Fuel could burn. Making Fuel
produces tar that Making Concrete could use as a binder. These
interactions are desirable — they create a rich industrial ecosystem.
But they must not create dependencies.

### The Solution: Shared Reaction Classes

Reaction classes are semantic labels on materials. A material can carry
any number of them. They describe what the material *is* and what it's
*eligible for* — not where it came from.

A reaction filters on a class to say "I accept any material with this
label." The reaction doesn't know or care which module produced the
material. It only knows the material carries the right class.

This means:
- Making Fuel defines a reaction that accepts `RM_SLAG` class boulders
- Making Metal tags its slag with `RM_SLAG`
- If Making Metal is installed, its slag works in fuel reactions
- If Making Metal is not installed, Making Fuel's own materials
  (which also carry `RM_SLAG` if applicable) fill the role
- If a third-party module produces slag and tags it `RM_SLAG`, it
  works too — without anyone updating anything

### The Class Hierarchy

Classes should be layered from general to specific. A material carries
classes at every applicable level. A reaction picks the level of
specificity it actually needs.

Example hierarchy:
```
RM_ITE                  — broadest: any processed industrial material
  RM_SLAG               — industrial byproduct stone
    RM_SLAG_ITE_MET          — metallurgical slag specifically
  RM_CALCIUM_SOURCE     — calcium-bearing material
  RM_FUEL_FEEDSTOCK     — suitable for fuel processing
    RM_FUEL_CHAR        — carbonized fuel intermediate
    RM_FUEL_TAR         — tar/pitch byproduct
```

A reaction that needs "any slag" filters on `RM_SLAG`. A reaction
that needs specifically metallurgical slag filters on `RM_SLAG_FERROUS`.
A reaction that needs "anything suitable for fuel processing" filters
on `RM_FUEL_FEEDSTOCK`.

The exact taxonomy is defined in the Supply Chain Class Reference
document. This philosophy document defines the *rules* for the
taxonomy — the reference document defines the *vocabulary*.

### Material Reaction Products and Economic Status

Materials with reaction_product entries are classified as "economic"
by DF. This has a practical consequence: reagents with the
`non_economic` flag set to true will reject economic materials.

This is useful. Processed module materials (peat charcoal, wood tar,
slag) should generally be economic — they have value, they're the
result of a process, and they should not be grabbed by wildcard
reagents that are looking for cheap generic stone from the ground.

Giving a processed material a reaction_product entry serves two
purposes:
1. It makes the material economic, preventing wildcard capture
2. It defines a derivation chain — "this material can produce that
   material" — which enables get_material_product reactions

Both purposes are legitimate and should be used deliberately.
Don't add reaction_products just to control economic status — add
them when the derivation relationship is real. If a material is
processed and should be economic but has no natural derivation
target, evaluate whether it needs a downstream product or whether
a different filtering approach is more appropriate.

---

## Module Scope and Boundaries

### What belongs in a module

A module should represent a coherent industrial domain:
- Making Metal: alloy smelting and exotic metalworking
- Making Fuel: fuel production and processing
- Making Concrete: cement and concrete production
- (Future) Making Glass: advanced glassworking
- (Future) Making Pottery: ceramic and clay industries

Each module owns its complete supply chain from raw inputs to
finished outputs. It defines its own materials, its own reactions,
its own categories, and its own reaction classes.

### What doesn't belong in a module

- Anything that modifies RM core behavior
- Placeholder materials with temporary names
- Test reactions or debug utilities (keep these separate)

### Core function vs auxiliary function

Every module must define its core functions — the industry it
represents, the materials it produces, the reactions that produce
them. Core function must be fully self-contained. Every core
reaction must be satisfiable using only materials the module itself
provides plus verified vanilla materials. This is non-negotiable.

Auxiliary functions are bonuses built on top of a complete core.
These are features that become possible when complementary
industries are present — things that wouldn't make sense without
certain ingredients from another module's output. An auxiliary
reaction might accept `RM_SLAG` class boulders as input, and if
no module providing slag is installed, that reaction simply has no
valid reagents. It doesn't break. It doesn't diminish the module's
core industry. It just isn't available.

The purpose of auxiliary functions is to gently encourage use of
the full ecosystem — not by denying core function, but by making
new things possible when industries are coupled together. A fuel
module's core function is producing fuel. If a metallurgy module
is also installed and produces slag tagged as fuel feedstock, the
fuel module might offer an extra reaction that converts that slag
into fuel. That's auxiliary. The fuel module already produces fuel
through its own peat chain — the slag path is a bonus.

Auxiliary functions should not limit or cheapen internal module
development. They are accents on an already properly fleshed out
core module, not substitutes for building a complete industry.
A module where half the reactions require another module's output
is not a module — it's a dependency.

### When to split a module

If a group of materials and reactions forms a self-contained industry
with its own supply chain, its own workshops, and its own purpose,
it should be its own module. The cement chain in Making Metal is a
good example — it has its own materials, its own multi-stage
production chain, and its own workshop assignments. It should be
Making Concrete.

The test: if you could remove this group of content and everything
else still works, it's a candidate for its own module.

---

## Naming Conventions

### Material keys
UPPERCASE, no spaces. Descriptive of what the material is.
```
SLAG_IRON           — not ITE_ITE
CALCITE_ITE_POWDER       — not ITE_ITE_ITE
PEAT                — not FUEL_INPUT_1
PORTLAND_CEMENT      — not CEMENT_TYPE_A
```

### Reaction keys
UPPERCASE, verb-first, descriptive of the process.
```
FORGE_SHAKUDO       — forge (verb) + material name
FIRE_PEAT           — fire (verb) + input material
CALCINE_SLAG        — calcine (verb) + input material
SLAKE_QUICKLIME     — slake (verb) + input material
```

### Reaction class names
UPPERCASE, prefixed with `RM_` for module ecosystem classes.
Descriptive of function or role, not origin.
```
RM_SLAG             — any industrial slag
RM_FUEL_FEEDSTOCK   — suitable for fuel processing
RM_CALCIUM_SOURCE   — calcium-bearing material
FLUX                — vanilla class, no prefix needed
CALCIUM_CARBONATE   — vanilla class, no prefix needed
```

### Category keys
UPPERCASE, prefixed with module prefix + `CAT_`.
```
MAKING_METAL_CAT_ALLOYS
MAKING_FUEL_CAT_FUEL
MAKING_CONCRETE_CAT_CEMENT
```

---

## Design Process

When designing new module content:

1. **Name it accurately.** Appropriate, correct names allow people
   to reference common knowledge to understand what's being
   presented. People who know about metallurgy, chemistry, or
   industrial processes will appreciate the respect to detail.
   We're not selling cool. We don't need dragon steel or
   upgradium — those are cheap generalizations for "cool steel"
   and "bonus in bar form," which is a cheap veneer. We're not
   in the business of sensationalism. We make a quality product
   that solves a problem accurately and effectively. The user
   decides what's cool. If the product is worthwhile and desired,
   it will succeed on its merits.

2. **Check independence.** Does this work if every other module is
   absent? Does it break anything if it's absent itself?

3. **Assign classes.** What is this material? What is it for? What
   processes should accept it? Tag it at every applicable level
   of the hierarchy.

4. **Check vanilla dependencies.** Does this reference a specific
   vanilla asset? Is that asset guaranteed to exist? If not,
   what's the fallback?

5. **Check cross-module references.** Are there any direct mat_id
   references to another module's materials? If yes, replace them
   with class-based filtering.

6. **Test in isolation.** Install only this module. Does everything
   work? Then install alongside other modules. Does everything
   still work? Then remove this module. Does everything else
   still work?
