# Colours, patterns and dyes

## A material's state_color is a pattern index, not a colour index

- **Status:** code (df-structures df.material.xml: `state_color` has `original-name='color_pattern'`) and measured (2026-09-30)
- It indexes `world.raws.descriptors.patterns`. A pattern lists its colours (`descriptor_pattern.colors`, indices into `descriptors.colors`); the colour a material shows is its pattern's first colour. The token string form, `state_color_str`, exists only on material templates, not on a live material.
- **RM depends on it:** every RM reader of state_color goes through the pattern, and RM's injector stores a colour's own pattern (2026-09-30).

## Every colour has a single colour pattern named after it; vanilla's come first, in colour order

- **Status:** measured (console, region4, 2026-09-30)
- region4 had 165 colours (vanilla's 136 and Argmod's 29) and 450 patterns. CLAY is on pattern 10, BRASS, which is also colour 10: vanilla's single colour patterns sit at the start in colour order, so for vanilla colours the pattern and colour indices coincide. Argmod's colours, loaded later, have their patterns appended after every pattern file: ARSENIC_BRONZE 429, ANTIMONY_BRONZE 430, MONEL 431, COBALTITE 435, NICORIL 436, UMASTEEL 438, EMENRIL 445 (Argmod's own order, from 421).
- Why reading state_color as a colour index went unnoticed: it is right for every vanilla colour. For a mod's colour it runs past the colour list (seven modded clays failed their binder twins at every load) or lands on an unrelated colour.

## powder_dye is a colour index

- **Status:** code (df-structures: `powder_dye`, "color token index")
- A dye's colour is a colour index while its state_color is a pattern index; vanilla sets them apart on purpose (redroot looks brown and dyes red). A derived dye colour must come from the pattern's first colour.

## A tool's cache entry carries its material's colour index plus one

- **Status:** measured (2026-09-25 vanilla; 2026-09-30 mod colour)
- `itemdef_toolst.graphics_info` entries carry `flags.color_index`: clinker 49 against 50, limestone 96 against 97, cinnabar 87 against 88, and a cobaltous clay binder 151 against COBALTITE's colour 150 while its pattern is 435. The vanilla readings could not tell colour from pattern; the mod colour settled it on the colour.
- While an entry exists DF draws its `texpos` and never reads the itemdef's flat texpos fields.

## Palette mods add palette rows by colour token

- **Status:** measured (files, 2026-09-30)
- Caldfir's Metallic maps `METALLIC_*` tokens to rows 137 to 190 of its image; Argmod maps its colours to rows 191 to 219 of its own. Both declare `[PALETTE:DEFAULT]`. A colour's palette row is `descriptor_color.palette.color` (18 entries of RGB). COBALTITE's row 205 is blue throughout.
