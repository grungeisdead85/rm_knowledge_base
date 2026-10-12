"""
index_ports.py

argmod_injection_all_ports: other modders' mods ported to Refinish Metal's
module engine. Every folder holding an info.txt is one DF mod. For each it
reads the mod's identity and load order from info.txt, counts what its data/
JSON injects, lists what its raws still define, select or cut, and names its
graphics, script and other files. Notes and files outside the mod folders
are listed with their sections. Writes argmod_injection_all_ports_INDEX.md.
"""
import ast
import collections
import json
import os
import re

from index_common import read, walk, kb, size_label, header, headings

NAME = 'argmod_injection_all_ports'

INFO_TOKEN = re.compile(r'\[([A-Z_]+):([^\]]*)\]')
# Raw tokens at the start of a line, leading whitespace allowed.
RAW_TOKEN = re.compile(r'^\s*\[([A-Z_]+):([^\]]+)\]', re.M)

# ---- WHAT COUNTS AS A DEFINITION ----
# The token that starts a new object, by the file's [OBJECT:] type. Taken
# literally, not as a prefix: a reagent's [REACTION_CLASS:] is not a reaction
# and a building's tile [COLOR:] is not a colour.
DEF_TOKENS = {
    'BUILDING': {'BUILDING_WORKSHOP', 'BUILDING_FURNACE'},
    'DESCRIPTOR_COLOR': {'COLOR'},
    'GRAPHICS': {'TILE_PAGE'},
}

# The arrays RM's module templates define: materials, reactions with their
# categories beside them, tools, plants and buildings. Whichever a file holds
# is counted.
DATA_ARRAYS = ('materials', 'reactions', 'categories', 'tools', 'plants', 'buildings')


# ==========================================
# SCAN
# ==========================================
def scan(root):
    files = list(walk(root))
    mod_dirs = sorted({os.path.dirname(rel) for p, rel in files
                       if os.path.basename(rel) == 'info.txt'})

    # A mod folder's files are everything under it. '' is a mod at the
    # repo's root, which holds every file.
    def under(rel, d):
        return rel.startswith(d + '/') if d else True

    mods = [scan_mod(root, d, [(p, rel) for p, rel in files if under(rel, d)])
            for d in mod_dirs]
    loose = [(p, rel) for p, rel in files
             if not any(under(rel, d) for d in mod_dirs)]
    extras = [describe_loose(p, rel, files) for p, rel in loose]
    return dict(mods=mods, extras=extras,
                files=len(files), size=sum(os.path.getsize(p) for p, rel in files))


def scan_mod(root, d, files):
    info = collections.defaultdict(list)
    for tok, val in INFO_TOKEN.findall(read(os.path.join(root, d, 'info.txt'))):
        info[tok].append(val)
    mod = dict(dir=d, label=f"{d}/" if d else '(repo root)', info=info,
               data=[], raws=[], graphics=[], images=[], scripts=[], other=[])
    for p, rel in files:
        sub = rel[len(d) + 1:] if d else rel
        top = sub.split('/')[0] if '/' in sub else ''
        ext = os.path.splitext(p)[1].lower()
        if sub == 'info.txt':
            continue
        if top == 'data' and ext == '.json':
            mod['data'].append(scan_data(p, sub))
        elif top == 'objects' and ext == '.txt':
            mod['raws'].append(scan_raw(p, sub))
        elif top == 'graphics' and ext in ('.png', '.bmp'):
            mod['images'].append(dict(rel=sub, size=os.path.getsize(p)))
        elif top == 'graphics':
            mod['graphics'].append(dict(rel=sub, size=os.path.getsize(p)))
        elif top.startswith('scripts_') and ext == '.lua':
            txt = read(p)
            mod['scripts'].append(dict(rel=sub, lines=txt.count('\n'), purpose=lua_purpose(txt)))
        else:
            mod['other'].append(dict(rel=sub, size=os.path.getsize(p)))
    return mod


# ---- MODULE DATA ----
# A module data file is a JSON object with a module block (prefix, name,
# version, depends_on) and one or more arrays. Anything else is listed as a
# plain file rather than guessed at.
def scan_data(p, sub):
    out = dict(rel=sub, module=None, counts={}, classes=None, buildings=None)
    try:
        # utf-8-sig: a file saved with a byte order mark still parses.
        with open(p, encoding='utf-8-sig') as f:
            d = json.load(f)
    except (ValueError, UnicodeDecodeError) as e:
        out['error'] = str(e)
        return out
    if not isinstance(d, dict) or not isinstance(d.get('module'), dict):
        return out
    out['module'] = d['module']
    for k in DATA_ARRAYS:
        if isinstance(d.get(k), list):
            out['counts'][k] = len(d[k])
    if isinstance(d.get('materials'), list):
        out['classes'] = collections.Counter(m.get('material_class') for m in d['materials']
                                             if isinstance(m, dict))
    if isinstance(d.get('reactions'), list):
        out['buildings'] = collections.Counter(r.get('building') for r in d['reactions']
                                               if isinstance(r, dict) and isinstance(r.get('building'), str))
    return out


# ---- RAWS THE MOD STILL LOADS ----
# Split three ways: what a file defines, what it selects (edits to an object
# defined elsewhere, [SELECT_INORGANIC:CLAY]) and what it cuts
# ([CUT_REACTION:BRASS_MAKING]). A port's raws are mostly the second and
# third kind, so a definition count alone would read as nearly empty.
def scan_raw(p, sub):
    txt = read(p)
    m = re.search(r'\[OBJECT:(\w+)\]', txt)
    otype = m.group(1) if m else None
    want = DEF_TOKENS.get(otype, {otype})
    defs, sel, cut = [], [], []
    for tok, val in RAW_TOKEN.findall(txt):
        ident = val.split(':')[0].strip()
        if tok.startswith('SELECT_'):
            sel.append(ident)
        elif tok.startswith('CUT_'):
            cut.append(ident)
        elif tok in want or (otype == 'ITEM' and tok.startswith('ITEM_')):
            defs.append(ident)
    return dict(rel=sub, otype=otype, defs=defs, sel=sel, cut=cut, size=os.path.getsize(p))


def lua_purpose(txt):
    """The header comment, read as the tools index reads it (the first 12
    lines), less the '@ module = true' line every module script opens with."""
    purpose = []
    for l in txt.split('\n')[:12]:
        s = l.strip()
        if s.startswith('--'):
            s = s.lstrip('-').strip()
            if s and not set(s) <= set('-=# ') and not s.startswith('@ module'):
                purpose.append(s)
        elif s:
            break
    return ' '.join(purpose)


# ---- FILES OUTSIDE THE MOD FOLDERS ----
# Markdown by its title and sections; an HTML page as a rendering of the
# markdown beside it only when their headings line up; Python by its
# docstring.
def describe_loose(p, rel, files):
    ext = os.path.splitext(p)[1].lower()
    out = dict(rel=rel, size=os.path.getsize(p), what='', sections=[])
    if ext == '.md':
        txt = read(p)
        titles = headings(txt, 1)
        out['what'] = titles[0] if titles else ''
        out['sections'] = headings(txt, 2)
    elif ext in ('.html', '.htm'):
        html = read(p)
        stem = os.path.splitext(rel)[0]
        md = [q for q, r in files if r == stem + '.md']
        t = re.search(r'<title>(.*?)</title>', html, re.S)
        title = ' '.join(t.group(1).split()) if t else ''
        if md and len(re.findall(r'<h2[\s>]', html)) == len(headings(read(md[0]), 2)):
            out['what'] = f"HTML rendering of `{os.path.basename(stem)}.md`" + (f" ({title})" if title else '')
        else:
            out['what'] = f"HTML page: {title}" if title else 'HTML page'
    elif ext == '.py':
        try:
            doc = ast.get_docstring(ast.parse(read(p))) or ''
        except SyntaxError:
            doc = ''
        out['what'] = doc.strip().split('\n\n')[0].replace('\n', ' ')
    return out


# ==========================================
# FIGURES FOR THE OVERVIEW
# ==========================================
def mod_totals(mod):
    tot = collections.Counter()
    prefix = None
    for d in mod['data']:
        tot.update(d['counts'])
        if d['module'] and not prefix:
            prefix = d['module'].get('prefix')
    return tot, prefix


def stats(scanned):
    rows = []
    for m in scanned['mods']:
        tot, prefix = mod_totals(m)
        rows.append(dict(name=(m['info'].get('NAME') or [m['label']])[0], prefix=prefix,
                         materials=tot['materials'], reactions=tot['reactions'],
                         categories=tot['categories']))
    return dict(files=scanned['files'], size=size_label(scanned['size']), mods=rows)


# ==========================================
# WRITE
# ==========================================
def counter_text(c):
    return ', '.join(f"{k} {v}" for k, v in sorted(c.items(), key=lambda kv: (-kv[1], str(kv[0]))))


def ids(xs, n=4):
    more = f" +{len(xs) - n}" if len(xs) > n else ''
    return ', '.join(xs[:n]) + more


def write(scanned):
    mods, extras = scanned['mods'], scanned['extras']
    L = header(NAME)
    L.append("Other modders' mods ported to Refinish Metal's module engine. Each mod folder "
             "below is a complete DF mod: its `data/` JSON is what RM's module engine injects "
             "at runtime, and its `objects/` and `graphics/` are ordinary raws that DF loads as "
             "usual. Injected content is not part of worldgen, so anything worldgen or another "
             "raw file needs stays in raws, and the port notes say what stayed and why.\n")
    L.append("## How to use this\n")
    L.append("Start with a port's notes: they record what moved, what stayed in raws and why, "
             "and the bugs found in the source mod. The JSON is RM's module schema at scale, so "
             "it is also where to find a worked example of a reagent, product or permission "
             "form. Search it by key:\n")
    L.append("```\ngrep -rn '\"key\": \"IRIDIUM\"' --include='*.json' .\n```\n")

    # ---- THE PORTS AT A GLANCE ----
    L.append(f"## Ports ({len(mods)} mods)\n")
    L.append("| Mod folder | Name | Prefix | Materials | Reactions | Categories |")
    L.append("|---|---|---|---|---|---|")
    for m in mods:
        tot, prefix = mod_totals(m)
        name = (m['info'].get('NAME') or [''])[0]
        L.append(f"| `{m['label']}` | {name} | `{prefix or ''}` | {tot['materials']} | "
                 f"{tot['reactions']} | {tot['categories']} |")
    L.append("")

    # ---- EACH PORT ----
    for m in mods:
        info = m['info']
        L.append(f"### `{m['label']}`\n")
        who = []
        if info.get('AUTHOR'):
            who.append(f"by {info['AUTHOR'][0]}")
        if info.get('DISPLAYED_VERSION'):
            who.append(f"version {info['DISPLAYED_VERSION'][0]}")
        ident = f" (`{info['ID'][0]}`)" if info.get('ID') else ''
        by = f", {', '.join(who)}" if who else ''
        L.append(f"**{(info.get('NAME') or [m['label']])[0]}**{ident}{by}.\n")
        if info.get('DESCRIPTION'):
            L.append(f"> {info['DESCRIPTION'][0]}\n")
        order = []
        if info.get('REQUIRES_ID'):
            order.append("requires " + ', '.join(f"`{x}`" for x in info['REQUIRES_ID']))
        if info.get('REQUIRES_ID_BEFORE_ME'):
            order.append("loads after " + ', '.join(f"`{x}`" for x in info['REQUIRES_ID_BEFORE_ME']))
        if info.get('REQUIRES_ID_AFTER_ME'):
            order.append("loads before " + ', '.join(f"`{x}`" for x in info['REQUIRES_ID_AFTER_ME']))
        if info.get('CONFLICTS_WITH_ID'):
            order.append("conflicts with " + ', '.join(f"`{x}`" for x in info['CONFLICTS_WITH_ID']))
        if order:
            L.append(f"- **Load order:** {'; '.join(order)}.")
        for d in m['data']:
            if d.get('error'):
                L.append(f"- **`{d['rel']}`:** not readable as JSON ({d['error']}).")
                continue
            if not d['module']:
                L.append(f"- **`{d['rel']}`:** JSON without a module block.")
                continue
            mod = d['module']
            dep = mod.get('depends_on') or []
            parts = []
            for k in DATA_ARRAYS:
                if k in d['counts']:
                    part = f"{d['counts'][k]} {k}"
                    if k == 'materials' and d['classes']:
                        part += f" ({counter_text(d['classes'])})"
                    if k == 'reactions' and d['buildings']:
                        part += f" ({counter_text(d['buildings'])})"
                    parts.append(part)
            dep_text = f", depends on {', '.join(f'`{x}`' for x in dep)}" if dep else ''
            L.append(f"- **Injects** (`{d['rel']}`, prefix `{mod.get('prefix', '')}`{dep_text}): "
                     f"{'; '.join(parts) or 'no arrays'}.")
        if m['raws']:
            L.append("- **Still in raws:**")
            for r in sorted(m['raws'], key=lambda a: a['rel']):
                bits = []
                if r['defs']:
                    bits.append(f"defines {len(r['defs'])} ({ids(r['defs'])})")
                if r['sel']:
                    bits.append(f"selects {len(r['sel'])} ({ids(r['sel'])})")
                if r['cut']:
                    bits.append(f"cuts {len(r['cut'])} ({ids(r['cut'])})")
                L.append(f"  - `{r['rel']}`: {r['otype'] or 'no OBJECT token'}, "
                         f"{'; '.join(bits) or 'nothing defined, selected or cut'}")
        if m['graphics'] or m['images']:
            g = ', '.join(f"`{os.path.basename(x['rel'])}`" for x in m['graphics']) or 'none'
            im = ', '.join(f"`{os.path.basename(x['rel'])}`" for x in m['images']) or 'none'
            L.append(f"- **Graphics:** raws {g}; images {im}.")
        for s in m['scripts']:
            purpose = (s['purpose'][:160] + '...') if len(s['purpose']) > 160 else s['purpose']
            L.append(f"- **Script:** `{s['rel']}` ({s['lines']} lines): {purpose or '_(no header comment)_'}")
        if m['other']:
            L.append("- **Other files:** " + ', '.join(f"`{x['rel']}` ({kb(x['size'])})" for x in m['other']) + ".")
        L.append("")

    # ---- NOTES AND FILES OUTSIDE THE MOD FOLDERS ----
    if extras:
        L.append("## Notes and other files\n")
        L.append("| File | What it is | Sections | Size |")
        L.append("|---|---|---|---|")
        for x in extras:
            secs = '; '.join(x['sections']).replace('|', '/')
            L.append(f"| `{x['rel']}` | {x['what'].replace('|', '/')} | {secs} | {kb(x['size'])} |")
        L.append("")
    return '\n'.join(L)
