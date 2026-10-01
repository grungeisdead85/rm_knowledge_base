# The stockpile window service: how it counts twins

The window service (refinish-stockpile-windows.lua) lends each twin its source material's flags while twin items are loose, so DF's own haulers file them. The mechanism and its probes are in RM_Stockpile_Mechanics.md.

While a window is open, the service recounts the loose twins every RECOUNT (250) frames. That count drives:

- the stall clock;
- the coal switch;
- the mirror of pile entries;
- the decision to close.

These entries cover how the count is kept affordable in a big fort, and what each shortcut can miss. The measured costs are in rm/performance.md.

## The loop counts the twins it knows; a full walk is the backstop

- **Status:** code and measured (2026-10-01)
- **Before:** each recount walked every item of every claimed type to find the twins among them. That was 548 twin items among tens of thousands of bars: 41.2 ms a recount, 15.2 ms/sec, nine tenths of the service (486 s, window open throughout).
- **Now:**
  - the full walk records every twin item it passes (`known`);
  - the item created hook adds each new twin item on the next tick (`absorb`);
  - a count reads the known items alone (`count_known`).
- **The backstop:** a full walk runs at least every FULL_FRAMES (4000), and whenever the claims change (`claims_sig`).
- **The gap, measured rather than assumed:** the created event does not fire for traders, migrants or invaders, nor for the coal watcher's sweep turning an existing bar into a coal twin. The full walk logs any twin item the list lacked (`STOCKPILE_WINDOWS KNOWN`).

## Stored twins are skipped until the next full walk

- **Status:** code and measured (2026-10-01)
- **The problem:** 147 recounts ran at 23.6 ms (45 at worst), 7.94 ms/sec (437 s). Each read every known twin, around 5,000, most of them stored.
- **The skip:** a count records a twin it finds stored (`settled`), and a count without detail skips it after that: no find, no material read, no classify. Stored means one of:
  - on a pile;
  - in a container;
  - built into a construction or a building;
  - held by another building.
- **Renewal:** detail counts (the census, a STUCK diagnosis) read every item and renew the record. Every full walk builds it afresh.
- **The gap:** a stored twin made loose again with no new item is unseen until the next full walk or detail count. That happens when a pile's settings change or a bin is emptied. A window never closes on it, because closing on nothing loose takes a fresh full walk first.
- **Measured in region4 (818 s):** the recount came to 16.9 ms, not the few ms estimated. The census held 1,509 twins in workshops (3,333 in containers, 21 on piles), and a twin in a workshop is loose, so all of them were still read.

## A twin in a workshop whose flags word has not changed is still there

- **Status:** code (2026-10-01), measured (2026-10-01), its gap inferred
- **The shortcut:** a count that finds a twin in a workshop keeps its item flags word (`in_shop`). A count without detail that reads the same word again counts the twin loose in a workshop through `tally_loose`, without classify. Any other word gets the full classify, and so does every item of a count with detail.
- **Why it holds:** every way a twin leaves a workshop changes a flag classify reads:
  - a haul or a reaction takes it into a job (`in_job`);
  - a removed workshop drops it (`on_ground`);
  - forbidding, dumping or destroying it marks it.
- **What still runs:** the find and the material read stay, so an item that is gone, or no longer a twin, still leaves the list.
- **The gap (inferred):** a twin moved from a workshop into another building with its flags word unchanged, by a script or by a haul no count saw in progress. It stays counted until the next full walk, which counts such twins and logs them (`KNOWN`, "kept as in a workshop, flags unchanged, were elsewhere").
- **Measured (443.7 s, the same save as the 818 s run):**
  - the known count took 11.4 ms a call, against 15.3 at the same point of the 818 s run;
  - the window service took 6.76 ms/sec, against 7.77;
  - no gap line appeared in 11 full walks.
- **Not yet measured:** the shortcut's hit rate. About 5 µs a loose twin remains, by inference: (11.4 ms less 1.9 of setup) over about 1,750 loose. Every loose twin is still found and read at each recount.

## classify asks the holder, reads the flags once, and stops early when only loose matters

- **Status:** code and measured (2026-10-01)
- **Nothing off the ground is judged by its flags:** whatever holds the item is asked (LOOSE, AND NEVER STRANDED).
- **ITEM FLAGS AS ONE NUMBER:** `it.flags.whole` is read once and its bits are tested in Lua. Before, up to seven separate reads cost 25.8 ms a count, about 4 µs an item, with 4,285 twins.
- **LOOSE ONLY:** an item no building holds is never loose. A count without detail answers 'held elsewhere' without the unit and container reads, which only name the place for the census. Before: 24.8 ms a count with 3,206 of 3,773 twins in containers.
- **ONE READ OF A BUILDING'S CONTENTS PER COUNT:** the role check scanned a workshop's `contained_items` from the start for each item, so a count grew with the square of what a workshop holds. That cost 63.9 ms a count with 690 to 732 twins in workshops, against 41 ms with 106. Now each building's list is read once per count into a role map.

## A count's pile list

- **Status:** code and measured (2026-10-01)
- **A PILE'S BOUNDS, READ ONCE PER LIST:** a pile's z and corners are read once and kept as numbers, and an item's position once per test. Before: 4.5 ms of a 14.4 ms count.
- **THE ROOM, SUMMED ONLY FOR PILES ASKED ABOUT:** bins are only placed on their piles at setup, and a pile's free bin volume is summed the first time an item on it asks. Before: 7.6 ms with 19 twins on piles.
- **Now:** a pile list lives for one count or one tick, and its setup costs 1.9 ms a count.

## A window's opening

- **Status:** code and measured (2026-10-01)
- **NO CLOSURE PER FLAG:** `flags_on` took 35 ms to lend 2,099 flags over 459 twins, now 22 to 23 ms.
- **THE KNOWN TWINS, WHEN THE LIST IS GOOD:** setting the storage timers took 24 ms and the coal check 34 ms, both walks of every claimed item. Now 17 to 18 ms and 21 ms.
- **THE CENSUS ASKS ONLY FOR PLACES:** the opening scan read every loose twin's description, which only a STUCK report uses: 105 ms with 559 loose. Now 104 to 114 ms with 1,527 loose.
- **Left to cut:** the opening tick still takes one frame of 167 to 180 ms.

## The retry wait gives way only to a change that could unstick

- **Status:** code and measured (2026-09-27, 2026-10-01)
- **The rule, 2026-09-27:** after a STUCK the window waits, doubling from 2000 to 32000 frames. A 32,000 frame wait missed a removed mason dropping its gravel to the floor, so any change in the census ended the wait.
- **What went wrong, 2026-10-01:** in a busy fort that rule left no wait at all. A STUCK listing 554 twins, 540 of them in workshops, reopened 14 s later, ran 15,750 frames, logged a STUCK for 580, and reopened 10 s after that.
- **Now the wait ends early only for:**
  - a loose twin of a material, in a place, that the STUCK did not have loose there;
  - a pile made or removed;
  - a pile's categories, bin, barrel or wheelbarrow allowance, links-only flag or links changed;
  - the mirror setting twin entries.
- More twins of the stuck kinds, in the stuck places, wait out the backoff. A window that closes with nothing loose puts the backoff back to its minimum.

## A full hauling queue holds a window open

- **Status:** measured (2026-10-01, region4) and code (`queue_full`: DF's hauling jobs against its haulers, `world.stockpile.num_jobs` and `num_haulers`)
- **What was measured:** with 1,509 twins waiting in workshops, the queue sat full (12 of 12, then 11 to 13). The window stayed open for the whole of both runs (818 s and 443.7 s) while hauls continued.
- **What follows:** in a fort with a backlog, the open window's recount is paid continuously. The queue's cap follows the number of haulers.
