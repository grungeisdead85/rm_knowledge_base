"""
index_tools.py

refinish_metal_tools: archived probe scripts, in folders that are clear-outs
of the live scripts folder. Reads each file's header comment, the df.global
paths and dfhack calls it reaches for and the functions it defines, tags it by
subsystem, marks the files whose comments speak of something broken, and
writes refinish_metal_tools_INDEX.md.
"""
import os
import re
import collections

from index_common import read, md5, walk, kb, size_label, header, number_word

NAME = 'refinish_metal_tools'

PATH_RE = re.compile(r'\bdf\.global\.[A-Za-z0-9_.\[\]]+')
API_RE = re.compile(r'\bdfhack\.[A-Za-z0-9_.]+')
DFTYPE_RE = re.compile(r'\bdf\.(?!global)([a-z_]+)\b')
FUNC_RE = re.compile(r'^\s*(?:local\s+)?function\s+([A-Za-z0-9_.:]+)\s*\(', re.M)

# ==========================================
# THE (!) MARK
# ==========================================
# A file is marked when its comments use any of this language. The step that
# set the mark was never archived with the other generators, so this pattern
# was rebuilt by fitting it to the published index: over the comment text it
# marks exactly the 40 files that index marked, and no other. Over whole files
# it marks 39 more, from words in code, prints and strings, so comments only.
# fail(s|ed) has no closing boundary, so "failsafe" counts: a "Failsafe:"
# comment is what marks refinish-verify-metals.lua. Its "THE FIX" comment,
# which records what an earlier version got wrong, matches nothing here.
CAVEAT_RE = re.compile(
    r'\b(broke|wrong|abandon|supersed|fail(s|ed)|not work|incorrect|retired|garbage)', re.I)


def comment_text(txt, ext):
    """Everything after a Lua '--' on each line, plus '#' comments in Python.

    '--' is matched anywhere on the line, strings included. Reading only true
    comments, outside quotes, marks the same 40 files today, so the simpler
    reading stays. Python files had no '#' comment matching the pattern when
    this was written, so reading them changes no mark today and keeps future
    ones honest.
    """
    out = [l[l.find('--') + 2:] for l in txt.split('\n') if '--' in l]
    if ext == '.py':
        out += [l.split('#', 1)[1] for l in txt.split('\n') if '#' in l]
    return '\n'.join(out)


# ---- PATHS ----
# Indexes are dropped and a trailing '.' or unclosed '[' trimmed, so
# reactions, reactions[i] and a sentence ending in "reactions." are one path.
# The published index kept reactions[] and reactions apart, then printed both
# without brackets: two rows that read the same with different counts.
def norm_path(p):
    return re.sub(r'\[[^\]]*\]', '', p).rstrip('.[')


# ---- SUBSYSTEM TOPICS ----
# A file joins a topic when any of its paths, API calls, df types or its name
# contains one of the topic's keys. A file can join several.
TOPIC = [
    ('reactions', ['raws.reactions']),
    ('inorganics/materials', ['raws.inorganics', 'matinfo', 'mat_table', 'material_templates']),
    ('items', ['world.items', 'item_type', 'items.createItem', 'items.getDescription']),
    ('jobs', ['world.jobs', 'job_type']),
    ('buildings/workshops', ['world.buildings', 'raws.buildings', 'workshop']),
    ('sprites/textures', ['texture', 'textures.', 'tile_page', 'getTexposByHandle']),
    ('units/creatures', ['world.units', 'raws.creatures', 'units.']),
    ('entities/civ', ['world.entities', 'raws.entities', 'plotinfo.civ']),
    ('plants', ['raws.plants']),
    ('gui/overlay', ['dfhack.gui', 'overlay', 'viewscreen']),
]


# ==========================================
# SCAN
# ==========================================
def scan(root):
    tools = []
    for p, rel in walk(root):
        ext = os.path.splitext(p)[1].lower()
        txt = read(p)
        # The leading comment block is the file's stated purpose.
        purpose = []
        for l in txt.split('\n')[:12]:
            s = l.strip()
            if s.startswith('--'):
                s = s.lstrip('-').strip()
                if s and not set(s) <= set('-=# '):
                    purpose.append(s)
            elif s:
                break
        paths = sorted({norm_path(x) for x in PATH_RE.findall(txt)})
        apis = sorted(set(API_RE.findall(txt)))
        types = sorted(set(DFTYPE_RE.findall(txt)))
        funcs = sorted(set(FUNC_RE.findall(txt)))
        blob = ' '.join(paths + apis + types + [os.path.basename(rel)])
        topics = [name for name, keys in TOPIC if any(k in blob for k in keys)] or ['misc']
        tools.append(dict(rel=rel, dir=rel.split('/')[0], name=os.path.basename(rel),
                          ext=ext, size=os.path.getsize(p), lines=txt.count('\n'), md5=md5(p),
                          purpose=' '.join(purpose)[:300], paths=paths, apis=apis,
                          types=types, funcs=funcs, topics=topics,
                          caveat=bool(CAVEAT_RE.search(comment_text(txt, ext)))))
    # ---- COPIES AND VERSIONS ----
    # A name found in more than one dump is a copy when the bytes match and a
    # version when they do not; only versions need telling apart.
    byname = collections.defaultdict(list)
    for t in tools:
        byname[t['name']].append(t)
    for t in tools:
        others = [o for o in byname[t['name']] if o is not t]
        t['variant'] = any(o['md5'] != t['md5'] for o in others)
    return tools


# ==========================================
# FIGURES FOR THE OVERVIEW
# ==========================================
def stats(t):
    topics = collections.Counter(tp for x in t for tp in x['topics'] if tp != 'misc')
    return dict(
        files=len(t), size=size_label(sum(x['size'] for x in t)),
        unique=len({x['md5'] for x in t}),
        lua=sum(1 for x in t if x['ext'] == '.lua'),
        py=sum(1 for x in t if x['ext'] == '.py'),
        dfglobal=sum(1 for x in t if x['paths']),
        topics=sorted(topics.items(), key=lambda kv: (-kv[1], kv[0]))[:6],
        caveat=sum(1 for x in t if x['caveat']),
        variants=sorted({x['name'] for x in t if x['variant']}),
        dirs=len({x['dir'] for x in t}),
    )


def short(p):
    return p.replace('df.global.', '')


# ==========================================
# WRITE
# ==========================================
def write(t):
    L = header(NAME)
    L.append("Archived probe scripts and utilities from Refinish Metal development. These are "
             "**periodic clear-outs of the live scripts folder**, taken whenever it got too full, "
             "too messy, or had scripts running that interfered with testing. The directory names "
             "are strata, not categories.\n")
    L.append("These tools are **not meant to be run again**. They are kept for reference: the "
             "paths they reference, the engine questions they record, and the functions worth "
             "harvesting into generalized RM tooling later. See the reliability warning below "
             "before trusting anything here.\n")
    L.append("## Reliability warning\n")
    L.append("**These probes are hit and miss. Many are failures, half-finished, or were "
             "superseded.** A script existing here is not evidence that its approach worked. "
             f"{sum(1 for x in t if x['caveat'])} of {len(t)} files contain comments about "
             "something being broken, wrong, abandoned or superseded, but that language covers "
             "three different cases that cannot be told apart mechanically: the script is broken, "
             "the script *found* that something else was wrong (the valuable case), or the script "
             "records what an earlier version got wrong. Files carrying any such comment are "
             "marked (!) below. Read the comment before trusting the code, and verify anything "
             "load-bearing against the live game.\n")
    L.append("## How to use this\n")
    L.append("The question this archive answers is *\"did we already work this out, and where?\"* "
             "Use the Topic index below to narrow, then grep the file.\n")
    L.append("```\ngrep -rn 'reaction_class' --include='*.lua' .\ngrep -rln 'getTexposByHandle' .\n```\n")
    L.append(f"**{len(t)} files** ({len({x['md5'] for x in t})} unique by content), "
             f"{sum(1 for x in t if x['ext'] == '.lua')} Lua, "
             f"{sum(1 for x in t if x['ext'] == '.py')} Python. "
             f"{sum(1 for x in t if x['paths'])} touch a `df.global` path.\n")

    # ---- COPIES AND VERSIONS ----
    counts = collections.Counter(x['name'] for x in t)
    multi = sorted(n for n, c in counts.items() if c > 1)
    var = sorted({x['name'] for x in t if x['variant']})
    L.append("## Versions that differ\n")
    if not multi:
        L.append("No tool name appears in more than one dump.\n")
    else:
        pairs = all(counts[n] == 2 for n in multi)
        where = 'two dumps' if pairs else 'more than one dump'
        lead = (f"{number_word(len(multi), capital=True)} tool "
                f"{'name appears' if len(multi) == 1 else 'names appear'} in {where}. ")
        if not var:
            L.append(lead + "All are byte-identical copies.\n")
        else:
            copies = 'the two copies' if pairs else 'the copies'
            L.append(lead + "All are byte-identical copies except these, where "
                     f"{copies} genuinely differ and you need to know which you are reading:\n")
            for v in var:
                L.append(f"- `{v}`")
                for c in sorted([x for x in t if x['name'] == v], key=lambda a: (-a['lines'], a['rel'])):
                    L.append(f"  - `{c['rel']}` ({c['lines']} lines, {kb(c['size'])})")
            L.append("")

    # ---- TOPIC INDEX ----
    L.append("## Topic index\n")
    L.append("Which files carry knowledge about which subsystem. A file can appear more than once.\n")
    bytopic = collections.defaultdict(list)
    for x in t:
        for tp in x['topics']:
            bytopic[tp].append(x)
    for tp in sorted(bytopic, key=lambda a: (-len(bytopic[a]), a)):
        files = sorted(bytopic[tp], key=lambda a: (a['name'], a['rel']))
        L.append(f"### {tp} ({len(files)})\n")
        L.append(', '.join(f"`{f['name']}`" for f in files))
        L.append("")

    # ---- PATH INDEX ----
    L.append("## Path index\n")
    L.append("The `df.global` paths this archive **references**, and where. These are attempts, not verified findings: "
             "A path appearing here means a script reached for it, not that it worked. Use this to find prior attempts, then read the file and verify against the live game.\n")
    pc = collections.Counter(p for x in t for p in x['paths'])
    L.append("| Path | Files | Where |")
    L.append("|---|---|---|")
    for p, c in sorted(pc.items(), key=lambda kv: (-kv[1], kv[0]))[:30]:
        who = [x['name'] for x in t if p in x['paths']][:3]
        more = f" +{c-3}" if c > 3 else ""
        L.append(f"| `{short(p)}` | {c} | {', '.join(who)}{more} |")
    L.append("")

    # ---- FILES BY DUMP ----
    L.append("## Files by dump\n")
    bydir = collections.defaultdict(list)
    for x in t:
        bydir[x['dir']].append(x)
    for dd in sorted(bydir, key=lambda a: (-len(bydir[a]), a)):
        files = sorted(bydir[dd], key=lambda a: a['name'])
        L.append(f"### `{dd}/` ({len(files)} files)\n")
        L.append("| File | Lines | ! | What it covers | Key paths / API | Functions |")
        L.append("|---|---|---|---|---|---|")
        for f in files:
            purpose = (f['purpose'][:95] + '...') if len(f['purpose']) > 95 else f['purpose']
            purpose = purpose.replace('|', '/') or '_(no header comment)_'
            keys = [short(p) for p in f['paths'][:2]] + [a for a in f['apis'][:2]]
            fn = ', '.join(f"`{x}`" for x in f['funcs'][:3]) + (f" +{len(f['funcs'])-3}" if len(f['funcs']) > 3 else "")
            L.append(f"| `{f['name']}` | {f['lines']} | {'!' if f['caveat'] else ''} | {purpose} | "
                     f"{', '.join('`'+k+'`' for k in keys)} | {fn or '-'} |")
        L.append("")
    return '\n'.join(L)
