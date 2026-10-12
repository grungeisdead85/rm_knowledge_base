# Index generators

Rebuild every repo index and the overview, `REFERENCE_REPOS.md`, by parsing the
repos themselves. Run them after adding files to any repo, so no index goes
stale.

## Running

Clone the repos side by side in one folder, then run the one script:

```bash
git clone --depth 1 https://github.com/grungeisdead85/df_data_reference.git
git clone --depth 1 https://github.com/grungeisdead85/vanilla_raws_reference.git
git clone --depth 1 https://github.com/grungeisdead85/refinish_metal_tools.git
git clone --depth 1 https://github.com/grungeisdead85/rm_knowledge_base.git
git clone --depth 1 https://github.com/grungeisdead85/argmod_injection_all_ports.git
git clone --depth 1 https://github.com/grungeisdead85/mods_backup_premigration.git
python3 rm_knowledge_base/repo_index_generators/build_indexes.py
```

With no arguments it reads the clones beside `rm_knowledge_base` and writes to
`index_output/` in the same folder. Both can be given:
`build_indexes.py REPOS_DIR OUT_DIR`. It never writes into the clones, and
nothing here reads the live game or the RM project.

It prints one line per repo, then anything that needs attention, and exits 1
when something does.

## What comes out

`index_output/` holds one folder per destination:

| File | Goes to |
|---|---|
| `df_data_reference/df_data_reference_INDEX.md` | the root of df_data_reference |
| `vanilla_raws_reference/vanilla_raws_reference_INDEX.md` | the root of vanilla_raws_reference |
| `refinish_metal_tools/refinish_metal_tools_INDEX.md` | the root of refinish_metal_tools |
| `argmod_injection_all_ports/argmod_injection_all_ports_INDEX.md` | the root of argmod_injection_all_ports |
| `rm_knowledge_base/REFERENCE_REPOS.md` | the root of rm_knowledge_base |
| `project/indexes/` | the project's `indexes/` folder: all of the above, plus rm_knowledge_base's `INDEX.md` |

## The one index written by hand

rm_knowledge_base's `INDEX.md` says in words what each file covers, so it is
written by hand and the generator never writes it. It checks it instead: every
file in the repo the index does not name, and every path the index names that
is not there, are printed as needing attention. Name each file by its full
path from the repo root, in backticks (`` `RM_Notes/RM_Tool_Schema.md` ``), and
the check can see it.

`mods_backup_premigration` has no index; the overview describes it.

## The files

| File | Does |
|---|---|
| `build_indexes.py` | The one to run. Finds the clones, runs each indexer, writes the results, checks the hand-written index |
| `index_common.py` | The repo registry, the walk that skips index tooling, the header every index carries |
| `index_data.py` | df_data_reference: path maps, object maps, dumps |
| `index_raws.py` | vanilla_raws_reference: definitions per raws file, sprite sheets per folder |
| `index_tools.py` | refinish_metal_tools: topics, paths, functions, the (!) marks |
| `index_ports.py` | argmod_injection_all_ports: each mod's load order, injected JSON, remaining raws, notes |
| `index_knowledge.py` | rm_knowledge_base: the check on the hand-written index |
| `reference_repos.py` | `REFERENCE_REPOS.md`: its wording lives here, its figures come from the scans |

A new repo gets a line in `REPOS` in `index_common.py`, an indexer if it should
have an index, and a section in `reference_repos.py`.

## History worth keeping

These replace four scripts (`analyze.py`, `classify.py`, `genindex.py`,
`gentools.py`) that were kept as identical copies in df_data_reference,
vanilla_raws_reference and refinish_metal_tools and had stopped running:

- `gentools.py` needed a `caveat` field that nothing set. The step that marked
  files with (!) was never archived. Its pattern is rebuilt in `index_tools.py`
  and marks exactly the 40 files the published index marked.
- The header on each index and `REFERENCE_REPOS.md` itself came from steps that
  were never archived either. Those copies still pointed at the account's old
  name, and the project's copy of the overview had been edited by hand past
  the repo copies.
- Once the scripts and the overview were uploaded into the repos, the scripts
  counted themselves, the indexes and the overview as repo content.
- Rows that tie (equal counts) followed the filesystem's listing order, which
  differs between machines. Everything is sorted now, so two runs over the same
  repos write the same files.
