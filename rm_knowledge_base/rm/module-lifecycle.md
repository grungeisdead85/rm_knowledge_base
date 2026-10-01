# The module lifecycle and RM's services

## Modules hand RM a start and a stop; RM runs them

- **Status:** decided (2026-09-30) and measured in play
- A module's listener may return `start` and `stop` with its data. RM's engine runs `start` at the end of `run_module_pipeline`, in injection order, only for accepted modules; it runs `stop` first thing in `clear_module_assets`, in reverse order, only for started modules. Every unload path passes through there. Modules without the hooks work as before.
- **Why:** Making Fuel started its scripts inside its own token call, before RM validated anything, and stopped them only at map unload. A rejected Making Fuel kept every watcher running, which made it look loaded many times over, and every watcher polled on through each save with its data out of RAM.
- A rejected module carrying a start hook is named once: `Not started: rejected above, so none of its scripts run this session.`
- Measured in play: `Started 2 module(s)` after each pipeline, `Stopped 2 module(s)` at each clear, nothing of either module logged inside the unloaded windows.

## Moving a module's start after injection changed nothing it needed

- **Status:** code (2026-09-30)
- Nothing in Making Fuel's payload building reads what its start routine does, and no reaction names its tinder twins. Every stop was checked: none writes or deletes stored data, and nearly every state a stop resets is one its own start already resets at each data cycle.
- The fuelwood twins (plant materials Making Fuel appends to every tree) now leave RAM at every save and return at restore, the same position each time; the ledger tracks them by name. Before, they stayed in RAM through saves.

## RM's services follow the data

- **Status:** decided and measured in play (2026-09-30)
- The dispatcher and the services riding it (byproducts, tool tint, the aggregate twins' runtime, the organic registrar, stockpile windows) start at the end of refinish-startup and of the hotsave restore, and stop first in refinish-shutdown, at the hotsave's clear and at map unload. Before, they ran through every save: the tool tint walked binder items whose materials were out of RAM.
- What each stop does: byproducts drops module registrations and keeps core's; the organic registrar wipes every claim; the stockpile windows close an open window first, handing the twins' flags back while the twins exist; the tool tint resets caches; the aggregate unclaims its own claim. Each start makes again what its stop dropped.

## The dispatcher's subscription rules

- **Status:** code (refinish-loop-dispatch)
- `subscribe()` works while the dispatcher is stopped, which is how modules subscribe in the pipeline before it starts. `start()` keeps existing subscriptions. `stop()` drops them all. `unsubscribe()` of a missing name does nothing.
- Every subscriber, in RM and both modules, subscribes inside its own `start()` (the adaptive engine in `start_loop()`), so stopping at every save loses nothing: nine subscribers before and after each save in region4.
