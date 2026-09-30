# How claims are measured and changes verified

## Measure before naming a mechanism, and make the probe read the right place

- A probe that reads the wrong folder, field or screen reports "not settled" forever. Three save probe runs read nothing because `getSavePath` pointed at the install folder (df/saves.md).
- When a probe keeps failing, find where it failed from its own lines (every read, the path it used) before changing its logic again.

## Reproduce the failure in a mock before trusting the fix

- Load the real file (or lift the real functions verbatim) into a mock world that plays the measured sequence: for saves, DF's logic first (the screen closing, a tick if nothing halts it), then DFHack's update calling the script. Count the effect that matters (ticks with RM out, unloads and reloads, stores).
- The mock must first reproduce what was seen in play: the save hook mock showed the one slipped tick and the back-out lock before showing the fix. A mock that cannot reproduce the failure proves nothing about the fix.
- Mocks of RM code walk game vectors from 0 (DFHack's ipairs) and model DFHack's behaviour from its documentation, not assumption (for example saveSiteData JSON-encoding its value).

## Survey every reader before changing what a value means

- Changing state_color from colour to pattern needed every reader and writer found first (injector, dye default, finish names, sprite art, tree dyes, tool tint). The tool tint was misjudged as a harmless grouping key and surfaced in play as a colour mismatch.

## Pairs are verified by round trip

- Every FIND is checked to occur exactly once in the file the user is actually running (the project copy may lag); the pair document is then applied to fresh copies and the result compared byte for byte with the tested build.
- The applier recognises a file heading only as `## <file>`. A heading with anything after the name matched nothing, applied nothing, and still printed success until the applier was made to fail when FIND blocks sit outside a file heading (2026-09-30).
- A deletion pair loses its FIND's trailing blank lines in a document; anchor it on the next non-blank line with a non-empty REPLACE.

## Check that moved code still reads what it should

- `luac5.3 -l -l` lists a function's upvalues and every global it reads. After moving code into a closure, confirm a local it needs is read as an upvalue, never as a global (a mistake compiles cleanly and reads nil in play).

## Give the next session something to measure

- New code logs what it decided and how long it took (the ledger's write and keep lines carry milliseconds; a fill held to one vessel names its counts), so the next log settles the question rather than a new probe.
