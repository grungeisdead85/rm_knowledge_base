# Dust and its outlets

RM's dust: how much one is, how it is paid, and where it goes besides finishing. Melting is in rm/melting.md.

## One dust is 100, for every class

- **Status:** decided (2026-10-03)
- The dust tool's size is 100, and every class pays in it: dust of one class finishes no better than another, it only comes easier or harder, and each job's measured loss decides that. 100 makes a boulder (10000), a bar and a block (600 each) and the aggregate quarter (2500) whole numbers of dust. Two dust finish a bar.
- **Before this:** size 400, and one dust was a quarter boulder, three rough gems or one bar, by class.

## The byproduct switch

- **Status:** decided (2026-10-03)
- One row in RM's config, per fort: ON, NO_DUST, OFF. NO_DUST stops dust whoever declared it; every other stream pays as usual. It is read at every job, so a change applies to the next job with no data cycle. A share switched off is not handed to another stream, and banked balances stay banked.

## Byproducts are paid one stack per form, material and job

- **Status:** decided (2026-10-03)
- The byproduct service pays each form as one stack instead of one item per unit.

## A job's mixed inputs share its products by volume

- **Status:** code, measured in play (2026-10-03)
- The reaction outputs service (refinish-reaction-outputs.lua) runs on every custom reaction. When a reagent holds several materials, the products are shared among them by volume. New items of a tool that declares a stack are merged per material, and a product marked `measure` is sized from what its source measured.
- **Measured in play:** branches split by tree type, gravel merged, crush dust sized by measure.

## Classes are granted at runtime and taken back before every save

- **Status:** code, measured in play (2026-10-03)
- RM's class service (refinish-material-classes.lua) gives inorganics a reaction class from a start hook, by flags or ids, and takes every grant back at shutdown. It never touches RM's own materials.
- **Measured in play:** Making Concrete granted POZZOLAN to seven volcanic stones.

## Finished metals get a grinder per base, just in time

- **Status:** decided (2026-10-03), measured in play
- A finish does not carry its metal's grinder class, because that slowed the material picker. Each base metal with finishes gets its own grinder at the quern and millstone, in a "Grind finished metals" folder, keyed by a class every finish of that base carries. They are built at load and when the first finish of a new base appears in play.

## Clay bricks are paid by volume; dust is their grog

- **Status:** decided and measured in play (2026-10-04)
- Vanilla's make clay bricks pays one brick for a 10000 clay boulder. RM's brick service (refinish-bricks.lua) pays by volume, and RM's own reaction, make clay bricks with grog, fires 25 stone dust into a clay boulder. The clay is the binder, so bricks need no module; they are vanilla's own bricks of the clay's fired material.
- **The measure:**
  - Clay shrinks 8% linear in drying and firing, the low end of brick clays (a brickworks' clay measured 5 to 6.4% in drying alone). Linear shrinkage S keeps (1 - S)^3 of the volume (ASTM C326), about 78%.
  - Grog is stone already; it keeps the nine tenths every process allows.
  - A brick costs an eighth of a boulder (1250) of what is left (BLOCKS, below).
  - So a clay boulder alone makes 6 bricks, and with grog 8.
- **A fault found in play:** the service first watched for the reaction as REFINISH_BRICK_GROG, but the module engine names every reaction it builds prefix, RXN_, key (refinish-module-react.lua), so the grog reaction paid DF's one brick until the name was REFINISH_BRICK_RXN_GROG.

## Blocks: a cut block is a quarter boulder, a molded or fired one an eighth

- **Status:** decided (2026-10-04)
- A mason cuts four blocks from a boulder with nothing but labour, and the rest is cut away and paid back as dust and gravel: a cut block costs a quarter boulder. A molded or fired block takes more steps and burns fuel, and loses less of itself: it costs half that, an eighth of a boulder of what is left after its process loss.
- Concrete: one cement, 50 dust and three gravel make 10 blocks (making_concrete_reactions.json). Asphalt: five aggregate and seven binders make 10 (making_fuel_reactions_other.json, MIX_ASPHALT). Bricks as above.
- **On the way there:** by DF's own block volume (600) bricks came to 12 and 16 a boulder, four times cheaper than any other block; at a quarter boulder they were no better than stone (3 and 4). A process that takes fuel and more steps needs an advantage over cut stone, but not 12 to 16.

## Glue is RM's, as granules

- **Status:** decided (2026-10-04)
- Animal glue moved from Making Fuel into RM core, so the dyes need no module. It is solid, as real hide and bone glue is at room temperature. A bone or a tanned hide boils into six granules of 25 at the kitchen, the 150 one boil made before. A recipe takes a granule, never part of a unit: a liquid unit too large for one run gets a smaller form on a tool.
- Making Fuel's liquid glue, its glue boils and its liquid glue briquette presses are retired (making-fuel/fuel.md).

## A mineral dye for every colour dust comes in

- **Status:** decided and measured in play (2026-10-04)
- Dust of any stone, gem or metal makes a dye of its own colour at the dyer's shop: two dust of that colour, a glue granule and an empty bag. A quarter of the dust is lost (refinish-dyes.lua).
- **Colours read live.** At the token call RM reads every stone, gem and metal's colour, a pattern's first colour (df/colours.md), so a mod's colours come in with nothing written for them. A finish takes its colour from the dust that finished it, so the finishes add none. The test world had 152 colours.
- **Where they live.** Plant materials on a host plant of their own (two hosts past 200), claimed for Milled Plants; the stockpile claim takes a function that lists them, not a list.
- **Which dust.** A reaction cannot ask for a colour, so every material with dust carries its colour's class: stones, gems and metals from the class service, finishes from the finish mint.
- **All at load.** One dye per colour is a short list, so every reaction is permitted at load. Permitted only as the fort first had dust of a colour, none of them showed in any menu (df/jobs.md).
- **Known limit:** a module's materials are injected after the token call, so a colour only a module's stone wears has no dye.

## When a mod cuts Make dye, RM makes its own

- **Status:** decided and measured in play (2026-10-04)
- A reaction naming a category the world lacks is offered in no menu (df/jobs.md). When vanilla's MAKE_DYE is missing, the module engine files the module dyes under a Make dye of RM's own (REFINISH_CORE_CAT_MAKE_DYE), with vanilla's name and no hotkey, swept before every save like RM core's other assets.
- RM does not guess which of a mod's categories is the dye one: a mod can split its dyes across several, ordinary and bulk.

## Flux dust is parked

- **Status:** decided (2026-10-04)
- The flux hijack (reactions that take a flux boulder asking for flux dust instead) is set aside. Which reaction a job is consumed by, the job's slot or the reaction's own reagent, has not been measured.

## Every bank lists every row it keeps, zero included

- **Status:** decided (2026-10-05), code (refinish-job-byproducts.lua and refinish-reaction-outputs.lua, ALWAYS VISIBLE)
- The byproduct bank lists every stream a building's jobs can bank, at zero until it banks. Which classes a building takes is fixed per workshop, held by DF's own enum names (BUILDING_CLASSES): carpenter wood; mason stone; metalsmith and magma forge metal; jeweler gem and glass; craftsdwarf stone, wood and bone; bowyer wood; mechanic stone; siege workshop wood; leatherworks leather; clothier and loom cloth; glass furnaces glass; smelters ore. Only a class some registered stream pays makes a row, and the byproduct switch is honoured.
- The output bank lists each measured product a building makes, under the product's own name at zero, and one row per material once a material holds a remainder.
- Glass worked at the jeweler (a rough or cut gem of a glass material) is glass work, so the jeweler banks cullet beside gem dust.
- Making Fuel's banks follow the same law: straw at the mills and the farmer's workshop, mash at the still.

## A balance shows only once it has paid since the readout landed

- **Status:** measured symptom, inference on its cause (2026-10-05)
- Metal dust and scrap rows appeared on every building, with no byproduct paid in either log. A balance with no unit saved beside it is no longer shown: pay began saving the unit when the readout landed, so a balance without one has not paid since.
- **Inference:** building construction paid byproducts until 2026-10-05, leaving balances under buildings whose jobs can never fill them. The readout cannot tell what paid an old balance.

## Dust rows carry their class

- **Status:** decided (2026-10-06)
- A dust row reads "stone dust", "metal dust", "bone dust"; scrap, cullet and gravel stand alone. Bare "dust" was tried on 2026-10-05 and dropped the next day: dust of several classes shares buildings, and a building's banks share one screen.

## A measured product that always comes out whole lists no row

- **Status:** decided (2026-10-06), code (refinish-reaction-outputs.lua, declared_set and measured_tools)
- A product declared `whole = true` beside `measure = true` gets no zero row in the output bank. The mason's crush dust is a boulder less three gravel, 25 dust exactly, so it never banks, and a row that is always empty is not a bank. A remainder, if one were ever left, shows like any other.

## The scale form is gone

- **Status:** decided (2026-10-05)
- SCALE was never injected (dropped at the catalog step, as the log showed) and nothing paid it. It is deleted from refinish-core-payload.lua, making-fuel-hijacker.lua and making-fuel-tuning.lua.
