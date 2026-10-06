# RM's requirement text: reagents that say what they need

DF writes a task row's requirement lines from each reagent's own fields (df/menus.md), so a reagent gated by a token prints the token. RM gives those fields words a player can read, in the hover and on a red row alike.

## A reagent may declare reads, the words it is printed as

- **Status:** decided (2026-10-05), code (refinish-module-react.lua, READS), measured in play
- `reads` on a JSON reagent is the words DF prints for it; DF adds its own item word after them ("bars", "binder", "item", "tool", "plant").
- **A contained reagent** takes the words as its code, and every product naming that code follows it: the material it takes, the container it fills, an improvement's target.
- **A reagent gated by a class** takes the words as its class, and every material carrying the old class is given the words beside it, so the reagent matches exactly what it matched.
- **A reagent gated by a material reaction product, with no class** (2026-10-06): the gate becomes a class of words, carried by every material that has the product, and the reagent asks for the words in place of the product. DF prints "seed-bearing plant" where it printed "SEED_MAT-producing".
- A reagent with a class and a product keeps its product gate, since a reagent holds one class.
- One set of words stands for one class or one product: words already standing for another are refused with an ERROR, and that reagent keeps its own class and code.
- Without RM's class service, a gated reagent keeps its token (one WARNING a session); a contained reagent's code still takes the words.
- preflight.py checks every `reads`: a non-empty string, a lever for DF to print it through, and one class or product per set of words across every file it checks.
- **Measured:** the hover and the objection read the words on every reagent given them; the briquette press job ran with them; they came back after a hotsave.

## The class service gives the words at start and takes them back before every save

- **Status:** code (refinish-material-classes.lua, ALIASES), measured
- The builder records each pair in `_G.refinish_class_aliases` as it builds. The class service's `start()` gives them once every material of the cycle is in RAM, twins included, searching the inorganics (RM's finishes, `REFINISH_STEEL_`, skipped), every plant's materials and every creature's; a product gate is found through each material's reaction products. The words are recorded with the service's other grants, and `stop()` erases them, never frees them, and empties the table for the next injection.
- **Cost, measured:** 36 sets of words on 1977 materials in 63 ms (2026-10-05); 39 sets on 1980 in 94 ms (2026-10-06).
- A material made after start that carries an aliased class misses its words. None is made that way today: finishes minted in play copy base metals, which carry no module class.

## Classes a watcher or RM writes itself are words too

- **Status:** decided and code (2026-10-05 and 06); measured in play for the keys and the drain
- **Rot and cremation keys** take their words through `reads`: "rotten", "dead citizen", "dead pet". Their abort seals ask for the class the job's own reaction asks for (`slot_class`), so a cancellation reads what the workshop reads; the raws token is the fallback, never an empty class, which would match any item.
- **The drain's** per-retort class is "number <building id> overfill drain", so an empty retort's drain reads "Requires number 5 overfill drain tool". The id keeps it unique, which is the binding: retort 8's clone asks for words only retort 8's key material carries. A drain job saved before the change asks for the old DRAIN_B<id> and cancels once.
- **The grinders:** the metal grinder's class is "unfinished metal", and each finished-metal grinder's is "finished <base name>", with the base's id after it where two bases share a name. refinish-clear-reaction.lua takes them back by the exact words (the finished ones are published on `_G.refinish_grind_fin_words` as they are made), never by a prefix.
- Lowercase classes are written by RM alone: raws tokens are uppercase, and a module's words are taken back before any clear runs.

## The words in use

- **Status:** decided (2026-10-05 and 06), in play
- Coal bars: cinder, charcoal, coke breeze, coke, coal, green coke, fine coal. Binders: clay or glue, bitumen or pitch. Boulders: bitumen, pitch, oil shale. Crystals: naphthalene, anthracene. Dust: flux, volcanic. Glob: fat. Straw. Asphalt's aggregate: gravel or slag; Making Concrete's gravel: stone; slag waste and slag cement: slag.
- Liquids, as their containers' lines: tar, coal tar, coal tar or crude oil, tar or oil, crude oil, vinegar, acid or vinegar, ammonia, aniline, benzene, methanol, creosote, turpentine, varnish; the tar sand bag: tar sand.
- Plants: seed-bearing, brewable, oil-bearing, paper-making. Clay boulders: clay.

## Still printing a token

- **Status:** code
- The two tar liquids at the kitchen, the pitch seal, creosote and varnish carry a class and a product: their product gate stays. Whether DF prints it is not measured.
- Other mods' reactions asking for builtin coal print DF's own "Refined coal" on a red row.
