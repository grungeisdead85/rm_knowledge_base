# The forge's task menu: RM's finishes in one folder

How RM files its finished metals in the forge's task menu (refinish-menu-forge.lua). What DF does underneath is in df/menus.md.

## Why: the vanilla metals could not be found

- **Status:** measured (2026-09-30 and 2026-10-02)
- The forge lists every metal inside every item category. With every base on, one category held 61,442 rows, nearly all RM finishes, and the vanilla metals could not be found, even by searching. The forge menu and the material picker were the two things standing in the way of every base being on, and the forge menu came first.

## The layout: refinished metals, base, kind, finish

- **Status:** decided (2026-10-03), measured in play
- Each item category gets one folder for every finish:
  - weapons and ammunition > refinished metals > steel > colour-based > amber steel > its job list
- The base and kind levels are always there, so the path is the same however many bases are selected. The kinds split a base's finishes as the smelter's folders do.
- **On the way there:**
  - 2026-10-02: two layouts were tried in play, and nesting a folder per base metal read better. Every RM metal went in one main folder beside the vanilla metals: refinished metals > base > metals. A finish type between the base and its metals was the other acceptable path; the base straight to its metals, the only acceptable shortcut. As few levels as possible, because a wrong turn means going all the way out and back in.
  - 2026-10-03: a base folder had listed all its finishes together, sorted by name, with nothing to show which kind each was; the colour-based and material-based level went in.
- The smelter's categories are left as they are.

## What the service does in each view

- **Status:** code
- **Top level:** DF lists "refinished metals" here too, since its category has reactions at the forge. It is taken out, because a metal opened from the top has no item category.
- **A category list:** every RM finish whose base has a folder leaves the list, and so does every row DF could not number; the refinished metals folder goes on top.
- **Refinished metals:** DF builds a folder per base metal. Bases with no finish in this category go, and a Back entry that returns to the category list is put last.
- **A base folder:** DF builds a folder per kind the base has, from the placeholders; Back returns to refinished metals.
- **A kind folder:** DF's placeholder row is replaced by every finish of that kind of the base, taken from the blueprint rather than from DF's list, which loses the high numbers (df/menus.md). The folder token is cleared, so a press opens the metal's jobs, and Back returns to the base folder.
- **A job list:** opened from a kind folder, the kind's token is put back, so Back returns to it. A job row that does not name the metal opened is taken out and logged, so a broken number can never become a job.
- **New work order:** the placeholders are taken out of the manager's list.

## Every button is deleted exactly once, by exactly one party

- **Status:** code and measured (2026-10-02)
- DF deletes what is in `button` when it rebuilds. A button taken out of the vectors is deleted by the service, after it is out of all three; a button made by the service and left in `button` is DF's to delete. Since `filtered_button` holds stale pointers while the panel is closed (df/menus.md), no list is touched unless DF built it: `button` not empty, and belonging to the forge in view.
- The buttons a filed category list leaves behind are deleted over the frames after it opens (DEFERRED DELETION), out of every vector the whole time.
- Every Back entry is built from DF's own: built with its fields zeroed, the first entries read Cancel in play (2026-10-02).

## Reported in play

- **Status:** measured in play
- 2026-10-02: the forge menu much better, with every base on; the material picker was then the last major thing standing in the way of every base on by default.
- 2026-10-03, under the just-in-time finishes with every base on: the forge menus with the colour and material layer were fine, and the magnifying glasses opened promptly.
