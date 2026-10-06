# DF's menus: the task menu, work orders, the material picker, pile lists

How DF builds the lists a player works through, measured while RM's finishes filled them. RM's forge menu service is in rm/forge-menu.md, the finishes in rm/finishes.md.

## A workshop's task menu is rebuilt on a press, into one place

- **Status:** measured (2026-10-02, refinish-forge-menu-probe)
- `df.global.game.main_interface.building` holds the open task menu: `button` (every row, plus DF's Back), `filtered_button` (the rows a search leaves) and `press_button` (every row, not narrowed by a search), with the view's category, material and `current_custom_category_token`.
- DF rebuilds the list when something is pressed, never on its own and never while a search is typed: a search only narrows `filtered_button`.
- Queueing a job closes the panel and resets the menu to the top.
- **Depends on it:** refinish-menu-forge.lua; making-fuel-menu-shaper.lua (furnace menus).

## A folder's rows are the reactions filed under its category

- **Status:** measured (2026-10-02, refinish-forge-menu-probe)
- A folder, a custom category selector, draws its caption from its reaction category, and DF builds its rows from the reactions at that building filed under the category. A folder with no such reaction dumps the task panel, and Add new task stays dead until the workshop is reopened.
- **Depends on it:** every folder RM opens has a placeholder reaction (rm/finishes.md).

## DF checks the folder token before the metal

- **Status:** measured (2026-10-02)
- A metal pressed while a folder token is set rebuilds the folder. With the token cleared, the same press opens the metal's own job list, row for row the same as its base metal's, and the jobs queued from it were right in play. Putting the folder's token back once a job list is open makes DF's Back from the jobs return to the folder.

## Back presses the last entry that is not a row

- **Status:** measured (2026-10-02)
- DF's Back presses the last entry of `button` that is not a row. A category list's is a category button for NONE; a metal's job list's is a material button with no material; a reaction folder gets none, and there Back reads Cancel and shuts the panel.
- An entry a script puts there is pressed the same way, but only one carrying the fields of DF's own (leave_button, flag and search text) reads Back. Entries built with those fields zeroed read Cancel in play.

## A category list cannot number a material above 32,767

- **Status:** measured (2026-10-02, 61,392 finishes, 62,606 inorganics)
- DF's category list carries a material number in 16 bits. Rows for inorganics past 32,767 come out as "rock", the long rock list seen before RM filed anything, so only 31,424 finishes reached Weapons, and steel's 635 material finishes, numbered after the colours and the bases before it, never reached its folder.
- **Evidence:** the unnumbered rows carried -32,768 to -2,931: inorganics 32,768 to the last, wrapped through 16 bits, 29,838 rows. With the 31,554 filed, every one of the 61,392 finishes is accounted for.

## filtered_button keeps stale pointers while the panel is closed

- **Status:** measured (2026-10-02)
- With `button` empty, `filtered_button` still held 61,500 pointers. DF deletes what is in `button` when it rebuilds, so a script touches no list unless DF built it, and deletes only a button it took out of all three vectors.

## New work order lists every builtin job for every metal

- **Status:** measured (2026-10-02, refinish-orders-probe)
- With every finish injected at load (81 base metals, 61,392 finishes) and no finishing reaction permitted, the manager's New work order built 4,922,677 templates, 4,919,214 of them builtin jobs, about 80 a metal, and took 13 to 16 seconds to open, before RM's own passes over it. With every base on, opening it locked DF up entirely, reproduced with no probe running.
- **Depends on it:** finishes are minted just in time (rm/finishes.md).

## The material picker lists every inorganic for a bar, block, gem, powder or liquid

- **Status:** measured (2026-10-02, refinish-picker-probe)
- Behind the magnifying glass, a bar, block, rough gem, powder or liquid slot lists all 62,606 inorganics, about 5 seconds to open with every finish injected at load.
- A reaction class carried by every finish slowed the picker as well, even with few finishes loaded (seen in play, 2026-10-03), which is why finished metals got grinders of their own instead of the metal grinder's class (rm/dust.md).

## A pile's material lists come back as long as they were saved

- **Status:** measured (2026-10-02)
- A stockpile keeps its choices in lists indexed by inorganic position. On a save written before the finish roster, the piles' bars lists came back 62,606 long, the old layout's length, not the array's: DF restores them as saved, so a choice stays at its position whatever material is there now.
- **Depends on it:** the ledger moves pile entries by name (rm/save-system.md).

## A reagent's requirement line is its own fields, in the hover and on a red row

- **Status:** measured (2026-10-05, making-fuel-reads-probe; in play through 2026-10-06)
- A task row's requirement lines, in the hover and in a red row's objection alike, are written from each reagent's own fields, with DF's item word after them and the line's first letter capitalised. The hover gives a count ("4 fine coal bars"); the objection does not ("Requires BREEZE_COKE bars").
  - A reagent gated by a reaction class prints the class string: "4 FINE_COAL bars", "BINDER binder".
  - The container of a contained reagent prints that reagent's code: "Tar-containing item".
  - A reagent gated by a material reaction product prints the product id: "SEED_MAT-producing" on a plant.
  - A reagent flagged nearby is printed with "Nearby": "Requires Nearby dead citizen item".
  - A reagent naming a material prints the material's name: "Sponge iron bars".
- Changing a live reagent's class string or code changes both lines at once. A row stays white when the materials that should match carry the new class: the briquette press with "fine coal" and "clay or glue" read white with cinders and a binder in the fort, and its job ran.
- DF writes a new objection only on a press: a folder closed and reopened shows the change.
- **Depends on it:** reads, the words a reagent is printed as (rm/requirement-text.md).
