# Measured costs and what cut them

| What | Before | After | How |
|---|---|---|---|
| Ledger read at load (8,956 materials) | about 60 s (hung region2) | 29 ms | plain lines through the string site data calls instead of double-encoded JSON (rm/save-system.md) |
| Ledger rewrite at each options screen opening (region4) | about 1 s, 7.2 MB, every time | kept in about 1/17 of the time when nothing moved (mock) | exact layout comparison, `if_changed` |
| Back-out of save & quit (region4) | 2 s unload + 12 s reload | nothing | no early unload |
| Grind watcher per call (all metals on, 81 bases) | 2.46 ms | 0.04 ms | base selection read as raw text and rebuilt only when the text changes; ghost reaction slots remembered and verified on use |
| Making Fuel menu shaper at the forge (100,138 reactions) | 54.8 ms per call, 85% of CPU | 0.14 ms per frame (mock, 20,000 buttons) | stamp the list (length, first button, folder token) and cache the verdict until the list is rebuilt |
| Branch spawner fall vector per tree | 3.2 to 3.3 s as branches piled up | 0.9 ms (mock, 2,540 items) | walk each map block once instead of once per tile of the 25x25 search |

## Still to cut (measured, 2026-09-30)

- Stockpile windows: 2 to 4 ms per call in a big world.
- Rot and cremate watchers: 22 and 11 ms per second.
- The tool record at each options screen opening walks every tool item (cheap at 466 tools).

## A data cycle's cost in region4

- **Status:** measured (2026-09-30)
- Startup pipeline about 12 s: modules 4.3, scan 0.5, materials 2.2, reactions 2.4, module permissions 0.35, entities 0.8. With every base metal on, RM held 61,392 materials and 99,578 reactions; the default went back to steel only, with the base metal selection as the control over how much is loaded.
