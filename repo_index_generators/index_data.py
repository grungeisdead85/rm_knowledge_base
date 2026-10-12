"""
index_data.py

df_data_reference: path maps, object maps and dumps captured from a live game.
Reads each file's first lines to find what object it traces, sorts the files
into kinds, and writes df_data_reference_INDEX.md.
"""
import os
import re
import collections

from index_common import read, md5, walk, kb, size_label, header

NAME = 'df_data_reference'


# ==========================================
# SCAN
# ==========================================
# A path map opens with "PATH MAP FOR: <subject>" and "MAX DEPTH: <n>"; an
# object map opens with its subject as "df.global... = <...>". The first
# .code or .id string in the first 40 lines names the object (STEEL_MAKING,
# IRON). The family is the raws list the subject lives in (reactions,
# inorganics), or for world objects the list after world (buildings, jobs).
def scan(root):
    files = []
    for p, rel in walk(root):
        txt = read(p)
        subject = depth = code = None
        for l in txt.split('\n')[:40]:
            m = re.match(r'PATH MAP FOR:\s*(.+)', l)
            if m:
                subject = m.group(1).strip()
            m = re.match(r'MAX DEPTH:\s*(\d+)', l)
            if m:
                depth = m.group(1)
            if subject is None:
                m = re.match(r'\s*(df\.global\.[\w\.\[\]]+?)\s*=\s*<', l)
                if m:
                    subject = m.group(1)
            m = re.search(r'\.code\s*=\s*"([^"]+)"', l)
            if m and not code:
                code = m.group(1)
            m = re.search(r'\.id\s*=\s*"([^"]+)"', l)
            if m and not code:
                code = m.group(1)
        family = None
        if subject:
            m = re.match(r'df\.global\.world\.raws\.(\w+)', subject)
            family = m.group(1) if m else (subject.split('.')[3] if subject.count('.') > 3 else None)
        files.append(dict(rel=rel, dir=os.path.dirname(rel), name=os.path.basename(rel),
                          size=os.path.getsize(p), lines=txt.count('\n'), md5=md5(p),
                          subject=subject, depth=depth, code=code, family=family,
                          kind=classify(subject, txt[:600])))
    return files


# ---- KIND ----
# Read off the first 600 characters. A console dump starts with the "> :lua"
# it was typed as; a PowerShell listing carries LastWriteTime columns.
def classify(subject, head):
    if subject and 'PATH MAP FOR' in head:
        return 'path map'
    if subject:
        return 'object map'
    if head.lstrip().startswith('> :lua'):
        return 'console dump'
    if head.lstrip().startswith('FIELDS ON'):
        return 'struct field list'
    if 'LastWriteTime' in head:
        return 'stale dir listing'
    if re.match(r'\s*--', head):
        return 'notes'
    return 'dump'


# ==========================================
# FIGURES FOR THE OVERVIEW
# ==========================================
def stats(files):
    maps = [f for f in files if f['kind'] in ('path map', 'object map')]
    fam = collections.Counter(f['family'] or 'other' for f in maps)
    return dict(
        files=len(files),
        size=size_label(sum(f['size'] for f in files)),
        path_maps=sum(1 for f in files if f['kind'] == 'path map'),
        pm_dirs=sorted({f['dir'] for f in files if f['kind'] == 'path map'}),
        # Families count path maps and object maps together, the way the
        # overview has always counted them (inorganics 22 + 1).
        families=sorted(fam.items(), key=lambda kv: (-kv[1], kv[0])),
        dumps=sum(1 for f in files if f['kind'] not in ('path map', 'object map')),
    )


# ==========================================
# WRITE
# ==========================================
def write(files):
    pm = sorted([f for f in files if f['kind'] == 'path map'],
                key=lambda f: (f['family'] or 'zz', f['name']))
    om = sorted([f for f in files if f['kind'] == 'object map'], key=lambda f: f['name'])
    other = sorted([f for f in files if f['kind'] not in ('path map', 'object map')],
                   key=lambda f: f['name'])
    L = header(NAME)
    L.append("Path maps and structure dumps captured from a **live Dwarf Fortress game**. "
             "These are ground truth for where data actually lives in the DF object tree, "
             "as opposed to what documentation says about it.\n")
    L.append("## How to use this\n")
    L.append("Each path map is a flattened trace of one object, every field recursively "
             "expanded, in the form `df.global.world.raws.<family>.<list>[i].<field> = <value>`. "
             "To find where something lives, grep for the field or value name across the repo. "
             "The hit gives you the full access path verbatim.\n")
    L.append("```\ngrep -rn 'reaction_class' 'Object Path Maps/' 'Path Maps/'\n```\n")
    L.append(f"## Path maps ({len(pm)} files)\n")
    L.append("Grouped by object family. 'Subject' is the object the map was taken from.\n")
    fam = collections.defaultdict(list)
    for f in pm:
        fam[f['family'] or 'other'].append(f)
    for family in sorted(fam):
        L.append(f"### {family} ({len(fam[family])})\n")
        L.append("| File | Subject | Code | Size |")
        L.append("|---|---|---|---|")
        for f in sorted(fam[family], key=lambda a: a['name']):
            L.append(f"| `{f['name']}` | `{f['subject'] or ''}` | {f['code'] or ''} | {kb(f['size'])} |")
        L.append("")
    if om:
        L.append(f"## Object maps ({len(om)})\n")
        L.append("| File | Subject | Code | Size |")
        L.append("|---|---|---|---|")
        for f in om:
            L.append(f"| `{f['name']}` | `{f['subject'] or ''}` | {f['code'] or ''} | {kb(f['size'])} |")
        L.append("")
    L.append(f"## Dumps, enums and notes ({len(other)})\n")
    L.append("| File | Kind | Lines | Size |")
    L.append("|---|---|---|---|")
    for f in other:
        L.append(f"| `{f['name']}` | {f['kind']} | {f['lines']} | {kb(f['size'])} |")
    L.append("")

    # ---- NOTES, each written only while what it describes is true ----
    # These used to be fixed text. Worked out from the files instead, so a
    # note cannot outlive the file it warns about.
    notes = []
    for f in sorted(files, key=lambda a: a['rel']):
        if os.path.splitext(f['name'])[1]:
            continue
        twins = [t for t in files if t['dir'] == f['dir']
                 and os.path.splitext(t['name'])[0] == f['name'] and t is not f]
        line = (f"- `{f['name']}` has **no file extension**. Searches filtered on "
                f"`*.txt` will miss it.")
        for t in twins:
            ext = os.path.splitext(t['name'])[1]
            same = 'byte-identical' if t['md5'] == f['md5'] else 'not identical to it'
            line += f" Its `{ext}` twin is {same}."
        notes.append(line)
    for f in other:
        if f['kind'] == 'stale dir listing':
            notes.append(f"- `{f['name']}` is a stale PowerShell directory listing of an old "
                         "local folder, not an index. It carries timestamps but no descriptions, "
                         "and may name files no longer present. This INDEX supersedes it.")
    if notes:
        L.append("## Notes\n")
        L.extend(notes)
    return '\n'.join(L)
