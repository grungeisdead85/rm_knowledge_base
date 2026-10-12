"""
index_dfhack.py

dfhack_docs, a folder of rm_knowledge_base: DFHack's own manual as DFHack
ships it in Dwarf Fortress's hack/docs/ folder, every page rendered as plain
text. Writes dfhack_docs_INDEX.md: the pages RM reads most and where the
DFHack names RM uses are documented, the full outline of those pages with the
line each section starts on, every other page with its sections, the
changelogs by version, and every tool with its tags, commands and summary.
"""
import os
import re
import collections

from index_common import read, walk, kb, size_label, sub_header

FOLDER = 'dfhack_docs'
INDEX = 'dfhack_docs_INDEX.md'

# ==========================================
# THE PAGES RM READS MOST
# ==========================================
# The first four were kept in the RM project under flat names, and the
# project's instructions, older notes and code comments cite them that way
# (Lua_API.txt for docs/dev/Lua API.txt, note the space). Each gets its full
# outline below. The last two are kept in the table for what they are not,
# so nobody goes looking in them for structure data.
#   (path in dfhack_docs/, the name older notes use, what RM reads it for,
#    full outline in the index)
KEY_PAGES = [
    ('docs/dev/Lua API.txt', 'Lua_API.txt',
     'dfhack.matinfo, textures.loadTileset, dfhack.timeout, createItem, reqscript, '
     'persistent data, the eventful API', True),
    ('docs/guides/modding-guide.txt', 'modding-guide.txt',
     'repeat-util and eventful in use', True),
    ('docs/dev/overlay-dev-guide.txt', 'overlay-dev-guide.txt', 'overlay and HUD work', True),
    ('docs/Core.txt', 'Core.txt', 'script loading, init files, environment', True),
    ('docs/dev/Structures-intro.txt', 'Structures-intro.txt',
     'only a pointer to the df-structures XML: no structure data', False),
    ('library/xml/SYNTAX.txt', 'SYNTAX.txt',
     'the df-structures XML authoring syntax, which RM never writes', False),
]

# ---- WHERE RM'S DFHACK NAMES ARE DOCUMENTED ----
# Searched in the four outlined pages at every run, so the table cannot drift
# from the pages. Each cell is the first line naming it and the section that
# line sits in.
NAMES = ['dfhack.matinfo', 'dfhack.items.createItem', 'loadTileset', 'dfhack.timeout',
         'reqscript', 'dfhack.persistent', 'repeat-util', 'eventful']

# ==========================================
# HEADINGS
# ==========================================
# The text rendering underlines every heading with one character per level,
# the same on every page: = is the page title, then - ~ ` + " * going down.
# Measured over all 491 pages on 2026-10-12: no page breaks that order. The
# two changelog fragments under docs/changelogs/ have no title, so each of
# their versions takes an =. ^ is not a level: it underlines the Contents
# boxes and a few rubrics (Tip, Typical Options), so it stays out of every
# outline. A title is underlined to its own length, which can be two
# characters (ls), so there is no minimum.
LEVEL = {'=': 1, '-': 2, '~': 3, '`': 4, '+': 5, '"': 6, '*': 7}
VERSION_RE = re.compile(r'^DFHack \d')


def headings(lines):
    """[(level, text, line number)] for one page, line numbers from 1."""
    out = []
    for i in range(len(lines) - 1):
        t, u = lines[i], lines[i + 1]
        if (t.strip() and not t[0].isspace() and len(u) == len(t)
                and len(set(u)) == 1 and u[0] in LEVEL):
            out.append((LEVEL[u[0]], t, i + 1))
    return out


def section_at(heads, line_no):
    """The deepest heading at or above a line: the section that line is in."""
    best = None
    for level, text, ln in heads:
        if ln <= line_no:
            best = text
        else:
            break
    return best


def contents_lines(lines, heads):
    """Line numbers inside the page's Contents box, from its ^ heading to the
    next real heading. The box repeats every section title, so a search that
    stops at the first mention would land in it."""
    out = set()
    for i in range(len(lines) - 1):
        t, u = lines[i], lines[i + 1]
        if t.endswith('Contents') and u and len(u) == len(t) and set(u) == {'^'}:
            end = next((ln for lv, tx, ln in heads if ln > i + 1), len(lines))
            out.update(range(i + 1, end))
    return out


def count_lines(lines):
    """Lines in a page split on newlines: a final newline adds no line."""
    return len(lines) - 1 if lines and lines[-1] == '' else len(lines)


# ==========================================
# TOOLS
# ==========================================
# Every page under docs/tools/ opens the same way: the tool's name as the
# title, a Tags line, then its commands and one indented summary. A plugin
# with several commands gives its own summary first and one per command
# after; a Lua-only plugin (eventful) has no Command line at all. The summary
# kept is the first indented paragraph after Tags, which is the page's own.
def scan_tool(lines):
    tags, summary = [], ''
    ti = next((i for i, l in enumerate(lines[:15]) if l.startswith('Tags:')), None)
    if ti is not None:
        tags = [x.strip() for x in lines[ti][5:].split('|') if x.strip()]
        for j in range(ti + 1, len(lines)):
            l = lines[j]
            if l.startswith('  ') and l.strip():
                para, k = [l.strip()], j + 1
                while k < len(lines) and lines[k].startswith('  ') and lines[k].strip():
                    para.append(lines[k].strip())
                    k += 1
                summary = ' '.join(para)
                break
            if l.strip() and not l.startswith(('Command:', 'Keybinding:')):
                break
    commands = re.findall(r'^Command: "([^"]+)"', '\n'.join(lines), re.M)
    return dict(title=lines[0] if lines else '', tags=tags, summary=summary, commands=commands)


# ==========================================
# SCAN
# ==========================================
def scan(root):
    pages, tools = [], []
    for p, rel in walk(root):
        size = os.path.getsize(p)
        if not rel.endswith('.txt'):
            pages.append(dict(rel=rel, size=size, lines=0, heads=[], title='', kind='other'))
            continue
        lines = read(p).split('\n')
        if rel.startswith('docs/tools/'):
            t = scan_tool(lines)
            t.update(rel=rel, dir=os.path.dirname(rel), name=rel[len('docs/tools/'):-4], size=size)
            tools.append(t)
            continue
        heads = headings(lines)
        versions = [h for h in heads if VERSION_RE.match(h[1])]
        title = next((h[1] for h in heads if h[0] == 1), lines[0] if lines else '')
        pages.append(dict(rel=rel, size=size, lines=count_lines(lines), heads=heads, title=title,
                          versions=versions, text=lines, contents=contents_lines(lines, heads),
                          kind='changelog' if len(versions) >= 5 else 'page'))
    return dict(pages=pages, tools=tools, root=root)


def newest_version(scanned):
    """The newest changelog entry, read off the changelog page itself."""
    for p in scanned['pages']:
        if p['rel'] == 'docs/NEWS.txt' and p.get('versions'):
            return p['versions'][0][1]
    for p in scanned['pages']:
        if p.get('versions'):
            return p['versions'][0][1]
    return None


def first_mention(pg, name):
    """(line, section) where a page documents a name, or None.

    A heading carrying the name is where the page documents it (eventful has
    its own section in the Lua API, far below its first mention). Otherwise it
    is the first line naming it outside the Contents box.
    """
    for level, text, ln in pg['heads']:
        if level >= 2 and name in text:
            return ln, text
    for i, l in enumerate(pg['text']):
        if name in l and (i + 1) not in pg['contents']:
            return i + 1, section_at(pg['heads'], i + 1)
    return None


def where_named(scanned):
    """For each name: {page path: (line, section)} over the outlined pages."""
    by_rel = {p['rel']: p for p in scanned['pages']}
    out = {}
    for name in NAMES:
        hits = {}
        for rel, old, use, outline in KEY_PAGES:
            pg = by_rel.get(rel)
            if outline and pg:
                hit = first_mention(pg, name)
                if hit:
                    hits[rel] = hit
        out[name] = hits
    return out


# ==========================================
# FIGURES FOR THE OVERVIEW
# ==========================================
def stats(scanned):
    by_rel = {p['rel'] for p in scanned['pages']}
    named = where_named(scanned)
    return dict(
        files=len(scanned['pages']) + len(scanned['tools']),
        size=size_label(sum(p['size'] for p in scanned['pages']) + sum(t['size'] for t in scanned['tools'])),
        pages=sum(1 for p in scanned['pages'] if p['kind'] != 'changelog'),
        changelogs=sum(1 for p in scanned['pages'] if p['kind'] == 'changelog'),
        tools=len(scanned['tools']),
        version=newest_version(scanned),
        key_pages=[(rel, old, use) for rel, old, use, outline in KEY_PAGES if rel in by_rel],
        missing_key_pages=[rel for rel, old, use, outline in KEY_PAGES if rel not in by_rel],
        # True only when the Lua API page is there and does not name it.
        repeat_util_not_in_lua_api=('docs/dev/Lua API.txt' in by_rel
                                    and 'docs/dev/Lua API.txt' not in named['repeat-util']),
    )


# ==========================================
# WRITE
# ==========================================
def cell(s):
    return s.replace('|', '/')


def write(scanned):
    pages, tools = scanned['pages'], scanned['tools']
    by_rel = {p['rel']: p for p in pages}
    version = newest_version(scanned)
    L = sub_header(FOLDER, INDEX)
    L.append("DFHack's own manual, as DFHack ships it in Dwarf Fortress's `hack/docs/` folder: every page "
             "rendered as plain text. It is the Lua API reference, the guides, the changelogs and one page "
             "per tool." + (f" The newest entry in its changelog is {version}." if version else '')
             + " It is DFHack's account of what DFHack does: the code is the source of truth, and what "
             "is measured in game outranks it.\n")
    L.append(f"{len(pages) + len(tools)} files: "
             f"{sum(1 for p in pages if p['kind'] != 'changelog')} pages, "
             f"{sum(1 for p in pages if p['kind'] == 'changelog')} changelogs and {len(tools)} tool pages.\n")

    # ---- HOW TO USE IT ----
    L.append("## How to use this\n")
    L.append("Paths below are inside `dfhack_docs/`. Every section is given with the line its heading "
             "is on, so a section can be read straight off the page. `Lua API.txt` has a space in its "
             "name, so quote the path:\n")
    # The example reads a real section, its lines taken from this run's scan.
    api = by_rel.get('docs/dev/Lua API.txt')
    span = None
    if api:
        hs = api['heads']
        for n, (lv, tx, ln) in enumerate(hs):
            if tx == 'Material info lookup':
                end = next((h[2] - 1 for h in hs[n + 1:] if h[0] <= lv), api['lines'])
                span = (ln, end)
    L.append("```\ngrep -n 'dfhack.matinfo' 'dfhack_docs/docs/dev/Lua API.txt'")
    if span:
        L.append(f"sed -n '{span[0]},{span[1]}p' 'dfhack_docs/docs/dev/Lua API.txt'   # Material info lookup")
    L.append("grep -rln 'reaction_class' dfhack_docs/docs/tools/\n```\n")

    # ---- THE PAGES RM READS MOST ----
    L.append("## The pages RM reads most\n")
    L.append("| Page | Older notes call it | Read it for | Lines |")
    L.append("|---|---|---|---|")
    for rel, old, use, outline in KEY_PAGES:
        pg = by_rel.get(rel)
        if pg:
            L.append(f"| `{rel}` | `{old}` | {use} | {pg['lines']:,} |")
        else:
            L.append(f"| `{rel}` | `{old}` | {use} | **not in the folder** |")
    L.append("")

    # ---- WHERE THE NAMES ARE ----
    outlined = [rel for rel, old, use, outline in KEY_PAGES if outline and rel in by_rel]
    named = where_named(scanned)
    L.append("## Where RM's DFHack names are documented\n")
    L.append("The first line in each page that names it, and the section that line is in. "
             "A dash means the page never names it.\n")
    L.append("| Name | " + ' | '.join(f"`{os.path.basename(r)}`" for r in outlined) + " |")
    L.append("|---|" + '---|' * len(outlined))
    for name in NAMES:
        cells = []
        for rel in outlined:
            hit = named[name].get(rel)
            cells.append(f"{hit[0]}, {cell(hit[1] or '')}" if hit else '-')
        L.append(f"| `{name}` | " + ' | '.join(cells) + " |")
    L.append("")

    # ---- FULL OUTLINES ----
    L.append("## Outlines of the pages RM reads most\n")
    for rel in outlined:
        pg = by_rel[rel]
        L.append(f"### `{rel}` ({pg['lines']:,} lines)\n")
        for level, text, ln in pg['heads']:
            if level >= 2:
                L.append('  ' * (level - 2) + f"- {text}, line {ln}")
        L.append("")

    # ---- EVERY OTHER PAGE ----
    others = sorted([p for p in pages if p['kind'] == 'page' and p['rel'] not in outlined],
                    key=lambda p: p['rel'])
    L.append(f"## Other pages ({len(others)})\n")
    L.append("Each page's top sections, with the line each starts on in brackets.\n")
    L.append("| Page | Title | Lines | Sections |")
    L.append("|---|---|---|---|")
    for p in others:
        top = [h for h in p['heads'] if h[0] == 2]
        secs = '; '.join(f"{cell(t)} ({ln})" for lv, t, ln in top[:12])
        if len(top) > 12:
            secs += f"; and {len(top) - 12} more"
        L.append(f"| `{p['rel']}` | {cell(p['title'])} | {p['lines']:,} | {secs or '-'} |")
    L.append("")

    # ---- CHANGELOGS ----
    logs = sorted([p for p in pages if p['kind'] == 'changelog'], key=lambda p: p['rel'])
    if logs:
        L.append(f"## Changelogs ({len(logs)})\n")
        L.append("Each version is a heading; the newest comes first. The two under `docs/changelogs/` "
                 "have no title of their own.\n")
        L.append("| Page | Title | Lines | Versions |")
        L.append("|---|---|---|---|")
        for p in logs:
            v = p['versions']
            title = p['title'] if not VERSION_RE.match(p['title']) else '(no title)'
            # Pages listing the very same versions, newest to oldest, are
            # named: the fragments repeat the changelog pages' entries.
            same = [o['rel'] for o in logs if o is not p
                    and [x[1] for x in o['versions']] == [x[1] for x in v]]
            note = f"; the same versions as `{same[0]}`" if same else ''
            L.append(f"| `{p['rel']}` | {cell(title)} | {p['lines']:,} | "
                     f"{len(v)}: {v[0][1]} back to {v[-1][1]}{note} |")
        L.append("")
    other_files = [p for p in pages if p['kind'] == 'other']
    if other_files:
        L.append("Not text, so not indexed: " + ', '.join(f"`{p['rel']}`" for p in other_files) + ".\n")

    # ---- TOOLS ----
    L.append(f"## Tools ({len(tools)} pages)\n")
    L.append("One page per tool under `docs/tools/`, each tool's name being its path there. "
             "Commands are listed where a page documents commands under other names.\n")
    tags_page = by_rel.get('docs/Tags.txt')
    if tags_page:
        groups, cur = [], None
        for l in tags_page['text']:
            m = re.match(r'^"(\w+)" tags$', l)
            if m:
                cur = [m.group(1), []]
                groups.append(cur)
            m = re.match(r'^\* (\w[\w-]*): ', l)
            if m and cur:
                cur[1].append(m.group(1))
        if groups:
            L.append("Tags, from `docs/Tags.txt`: " + '; '.join(f"{g}: {', '.join(ts)}" for g, ts in groups) + ".\n")
    bydir = collections.defaultdict(list)
    for t in tools:
        bydir[t['dir']].append(t)
    for d in sorted(bydir):
        ts = sorted(bydir[d], key=lambda t: t['name'].lower())
        L.append(f"### `{d}/` ({len(ts)})\n")
        L.append("| Tool | Tags | Summary |")
        L.append("|---|---|---|")
        for t in ts:
            summ = cell(t['summary']) or '_(no summary)_'
            other = [c for c in t['commands'] if c != t['name']]
            if other:
                summ += ' Commands: ' + ', '.join(f"`{c}`" for c in t['commands']) + '.'
            L.append(f"| `{t['name']}` | {', '.join(t['tags'])} | {summ} |")
        L.append("")
    return '\n'.join(L)
