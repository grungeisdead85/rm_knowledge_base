"""
index_knowledge.py

rm_knowledge_base: its INDEX.md is written by hand, because each line says in
words what a file covers, and that is not something to generate. So this
writes nothing. It checks the hand-written index against the repo: every
content file the index does not name, and every path it names that is not
there. A new entry or a moved folder cannot slip past unlisted that way, as
the whole of RM_Notes/ did when it was first uploaded.

The index names each file by its full path from the repo root, in backticks.
"""
import os
import re
import collections

from index_common import read, walk, size_label, BY_NAME

NAME = 'rm_knowledge_base'
INDEX = BY_NAME[NAME]['hand_index']

# A backticked path with a file extension: `RM_Notes/RM_Tool_Schema.md`.
NAMED = re.compile(r'`([^`\s]+\.[A-Za-z0-9]+)`')


def scan(root):
    files = [(rel, os.path.getsize(p)) for p, rel in walk(root)]
    rels = {rel for rel, size in files}
    idx = os.path.join(root, INDEX)
    named = set(NAMED.findall(read(idx))) if os.path.isfile(idx) else set()
    return dict(
        files=files,
        has_index=os.path.isfile(idx),
        # In the repo, not in the index.
        unlisted=sorted(rels - named),
        # In the index as a path, not in the repo. Bare file names are left
        # alone: the index may mention a project file such as
        # RM_Comment_Rules.md that was never meant to be here.
        missing=sorted(n for n in named if '/' in n and n not in rels),
    )


def stats(scanned):
    by_top = collections.Counter(rel.split('/')[0] for rel, size in scanned['files'] if '/' in rel)
    areas = sorted({rel.split('/')[1] for rel, size in scanned['files']
                    if rel.startswith(NAME + '/') and rel.count('/') >= 2})
    return dict(files=len(scanned['files']),
                size=size_label(sum(size for rel, size in scanned['files'])),
                entries=by_top[NAME], areas=areas, notes=by_top['RM_Notes'])
