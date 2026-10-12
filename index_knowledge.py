"""
index_knowledge.py

rm_knowledge_base: its INDEX.md is written by hand, because each line says in
words what a file covers, and that is not something to generate. So this
writes nothing. It checks the hand-written index against the repo: every
content file the index does not name, and every path it names that is not
there. A new entry or a moved folder cannot slip past unlisted that way, as
the whole of RM_Notes/ did when it was first uploaded.

A folder with a generated index of its own (sub_indexes in index_common, the
DFHack manual in dfhack_docs/) is left to that index: INDEX.md names the
generated file instead of the folder's files, and the check makes sure it
does.

The index names each file by its full path from the repo root, in backticks.
"""
import os
import re
import collections

from index_common import read, walk, size_label, BY_NAME, TOOLING_DIRS

NAME = 'rm_knowledge_base'
INDEX = BY_NAME[NAME]['hand_index']
SUB_INDEXES = BY_NAME[NAME].get('sub_indexes', [])

# A backticked path with a file extension: `RM_Notes/RM_Tool_Schema.md`.
NAMED = re.compile(r'`([^`\s]+\.[A-Za-z0-9]+)`')

# ---- THE GENERATORS' OWN FILES ----
# GitHub's upload page drops a folder when its files are picked instead of
# the folder being dragged, and on 2026-10-12 that landed every generator at
# this repo's root. They are named here so a stray copy at the root is
# reported as what it is. README.md counts only when it is the generators'
# own, so this repo can still have a README of its own one day.
GENERATOR_FILES = {'build_indexes.py', 'index_common.py', 'index_data.py', 'index_raws.py',
                   'index_tools.py', 'index_ports.py', 'index_knowledge.py', 'index_dfhack.py',
                   'reference_repos.py'}
GENERATOR_README_TITLE = '# Index generators'


def scan(root):
    content = [(rel, os.path.getsize(p)) for p, rel in walk(root)]
    rels = {rel for rel, size in content}
    # Every file there, index tooling included, for checking that a path the
    # index names exists: the index names the generators by their folder.
    existing = set()
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d != '.git']
        for f in fn:
            existing.add(os.path.relpath(os.path.join(dp, f), root).replace(os.sep, '/'))
    idx = os.path.join(root, INDEX)
    text = read(idx) if os.path.isfile(idx) else ''
    named = set(NAMED.findall(text))

    sub_folders = [s['folder'] + '/' for s in SUB_INDEXES]

    def in_sub(rel):
        return any(rel.startswith(f) for f in sub_folders)

    # ---- AT THE ROOT BY MISTAKE ----
    stray = []
    for rel in sorted(rels):
        if '/' in rel:
            continue
        if rel in GENERATOR_FILES:
            stray.append((rel, f"a generator: it belongs in {sorted(TOOLING_DIRS)[0]}/"))
        elif rel == 'README.md' and read(os.path.join(root, rel)).startswith(GENERATOR_README_TITLE):
            stray.append((rel, f"the generators' README: it belongs in {sorted(TOOLING_DIRS)[0]}/"))
    stray_names = {rel for rel, why in stray}

    # ---- NOT IN THE INDEX ----
    # A file named like one the index lists in another folder is most likely
    # an upload that landed in the wrong folder, so it says which.
    listed_by_name = collections.defaultdict(list)
    for rel in rels:
        if rel in named:
            listed_by_name[os.path.basename(rel)].append(rel)
    unlisted = []
    for rel in sorted(rels - named):
        if in_sub(rel) or rel in stray_names:
            continue
        twins = [t for t in listed_by_name.get(os.path.basename(rel), []) if t != rel]
        unlisted.append((rel, f"same name as {twins[0]}: uploaded to the wrong folder?" if twins else ''))

    return dict(
        files=content,
        has_index=os.path.isfile(idx),
        stray=stray,
        unlisted=unlisted,
        # In the index as a path, not in the repo. Bare file names are left
        # alone: the index may mention a project file such as
        # RM_Comment_Rules.md that was never meant to be here.
        missing=sorted(n for n in named if '/' in n and n not in existing),
        # A generated folder index the hand-written one forgets to name.
        sub_not_named=[s['index'] for s in SUB_INDEXES if s['index'] not in named],
    )


def stats(scanned):
    by_top = collections.Counter(rel.split('/')[0] for rel, size in scanned['files'] if '/' in rel)
    areas = sorted({rel.split('/')[1] for rel, size in scanned['files']
                    if rel.startswith(NAME + '/') and rel.count('/') >= 2})
    return dict(files=len(scanned['files']),
                size=size_label(sum(size for rel, size in scanned['files'])),
                entries=by_top[NAME], areas=areas, notes=by_top['RM_Notes'],
                docs=sum(by_top[s['folder']] for s in SUB_INDEXES))
