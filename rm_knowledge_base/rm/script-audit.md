# Which scripts the running system uses (2026-09-30)

- **Method:** every Lua file in the project, comments stripped, searched for code naming another file; a file is required when a chain of such references leads to it from an entry point: `refinish_steel.lua`, the modules' main scripts, and scripts DFHack loads itself (`OVERLAY_WIDGETS`). The full report with every chain is script-audit.md in the session outputs.
- **Result:** 113 files, 96 required (two of them overlays RM never names), 17 not loaded:
  - read only utilities: refinish-path, refinish-find, refinish-item-inspect, refinish-job-find, refinish-job-inspect, refinish-tool-plantmat;
  - tools that change or tune things: refinish-job-set (edits live jobs), refinish-tint (tint tuner), making-fuel-curve (named in a settings error message);
  - probes: making-fuel-fell-probe, making-fuel-hijack-probe, making-fuel-mat-probe, refinish-tool-inspect;
  - dead: refinish-ledger-tool (superseded by the tool record), refinish-module-dependencies (unused);
  - templates: rm-module-template, rm-module-template-advanced (runnable while in a scripts folder).
- **Open:** files in the mod folders that are not in the project (refinish-save-probe, for one) need a folder listing.
