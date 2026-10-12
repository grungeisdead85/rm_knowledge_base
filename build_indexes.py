#!/usr/bin/env python3
"""
build_indexes.py

Regenerates every repo index and the overview (REFERENCE_REPOS.md) by parsing
the clones, and checks the one index written by hand (rm_knowledge_base's
INDEX.md). Run it after adding files to any of the repos.

Usage:
    python3 build_indexes.py [REPOS_DIR] [OUT_DIR]

    REPOS_DIR  the folder holding the clones side by side. Default: the folder
               above the rm_knowledge_base clone this script sits in.
    OUT_DIR    where the results go. Default: index_output inside REPOS_DIR.

Writes, under OUT_DIR, one folder per destination:
    <repo>/<repo>_INDEX.md                 the root of that repo
    rm_knowledge_base/REFERENCE_REPOS.md   the root of rm_knowledge_base
    project/indexes/                       every index and the overview, under
                                           the names the project keeps them by

Nothing here reads the live game or the RM project. It only parses the clones,
and it never writes into them.
"""
import os
import sys

# The sibling modules are imported from this folder by path, so the script
# runs the same from any working directory, and under python -I, which leaves
# the script's own folder off the import path. No __pycache__ is written: this
# folder lives in a clone, and a cache folder there is one more thing that
# could be uploaded to the repo by mistake.
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True

import index_common as common      # noqa: E402
import index_data                  # noqa: E402
import index_raws                  # noqa: E402
import index_tools                 # noqa: E402
import index_ports                 # noqa: E402
import index_knowledge             # noqa: E402
import reference_repos             # noqa: E402

# Repo name -> the module that indexes it. A repo missing here has no index.
INDEXERS = {
    'df_data_reference': index_data,
    'vanilla_raws_reference': index_raws,
    'refinish_metal_tools': index_tools,
    'argmod_injection_all_ports': index_ports,
}


def save(path, text):
    """UTF-8, LF line endings, one final newline."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text.rstrip('\n') + '\n')


def main():
    repos_dir = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 \
        else os.path.dirname(os.path.dirname(HERE))
    out_dir = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 \
        else os.path.join(repos_dir, 'index_output')
    project = os.path.join(out_dir, 'project', 'indexes')
    print(f"repos:  {repos_dir}")
    print(f"output: {out_dir}\n")

    stats, problems, project_files = {}, [], []
    for r in common.REPOS:
        name = r['name']
        root = os.path.join(repos_dir, name)
        if not os.path.isdir(root):
            problems.append(f"{name}: no clone at {root}")
            print(f"{name:28s} MISSING: no clone at {root}")
            continue

        if name in INDEXERS:
            mod = INDEXERS[name]
            scanned = mod.scan(root)
            text = mod.write(scanned)
            stats[name] = mod.stats(scanned)
            for dest in (os.path.join(out_dir, name, r['index']), os.path.join(project, r['index'])):
                save(dest, text)
            project_files.append(r['index'])
            print(f"{name:28s} {stats[name]['files']:4d} files -> {name}/{r['index']}")

        elif name == index_knowledge.NAME:
            # ---- THE HAND-WRITTEN INDEX: CHECK, NEVER WRITE ----
            scanned = index_knowledge.scan(root)
            stats[name] = index_knowledge.stats(scanned)
            if not scanned['has_index']:
                problems.append(f"{name}: no {index_knowledge.INDEX}")
                print(f"{name:28s} NO {index_knowledge.INDEX}")
            elif scanned['unlisted'] or scanned['missing']:
                print(f"{name:28s} {stats[name]['files']:4d} files, {index_knowledge.INDEX} "
                      "is written by hand and needs these lines:")
                for rel in scanned['unlisted']:
                    print(f"    NOT LISTED:   {rel}")
                    problems.append(f"{name}: {rel} is not in {index_knowledge.INDEX}")
                for rel in scanned['missing']:
                    print(f"    NOT IN REPO:  {rel}")
                    problems.append(f"{name}: {index_knowledge.INDEX} names {rel}, which is not there")
            else:
                print(f"{name:28s} {stats[name]['files']:4d} files, {index_knowledge.INDEX} "
                      "is written by hand: lists every file")
            if scanned['has_index']:
                # The project keeps a copy too, under the same name.
                with open(os.path.join(root, index_knowledge.INDEX), encoding='utf-8') as f:
                    save(os.path.join(project, index_knowledge.INDEX), f.read())
                project_files.append(index_knowledge.INDEX)

        else:
            stats[name] = common.plain_stats(root)
            print(f"{name:28s} {stats[name]['files']:4d} files, no index (described in the overview)")

    # ---- THE OVERVIEW ----
    # Needs every indexed repo's figures. With a clone missing it is not
    # written at all, rather than written with a section quietly gone.
    needed = [r['name'] for r in common.REPOS if r['name'] != 'mods_backup_premigration']
    absent = [n for n in needed if n not in stats]
    if absent:
        print(f"\nREFERENCE_REPOS.md NOT written: no clone of {', '.join(absent)}")
    else:
        text = reference_repos.write(stats)
        for dest in (os.path.join(out_dir, common.HUB, 'REFERENCE_REPOS.md'),
                     os.path.join(project, 'REFERENCE_REPOS.md')):
            save(dest, text)
        project_files.append('REFERENCE_REPOS.md')
        print(f"\n{'REFERENCE_REPOS.md':28s}      -> {common.HUB}/REFERENCE_REPOS.md")
    print(f"{'project copies':28s} {len(project_files):4d} files -> project/indexes/")

    if problems:
        print(f"\n{len(problems)} thing(s) need attention:")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("\nAll indexes written, nothing needs attention.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
