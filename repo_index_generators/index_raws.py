"""
index_raws.py

vanilla_raws_reference: DF's vanilla raws and sprite sheets, laid out like
DF's own mod folders. Counts what each raws file defines, totals the sprite
sheets by folder, and writes vanilla_raws_reference_INDEX.md.
"""
import os
import re
import collections

from index_common import read, walk, kb, size_label, header

NAME = 'vanilla_raws_reference'

# A definition is a token at the start of a line whose name is the file's
# object type ([CREATURE:BIRD_CROW] in an [OBJECT:CREATURE] file). Three
# object types define under other names: items as ITEM_<kind>, graphics
# files as TILE_PAGE, colour descriptors as COLOR.
OBJ_TOKEN = re.compile(r'^\[([A-Z_]+):([^\]]+)\]', re.M)


# ==========================================
# SCAN
# ==========================================
def scan(root):
    raws, sprites, other = [], collections.defaultdict(lambda: dict(n=0, bytes=0)), []
    image_ext = collections.Counter()
    for p, rel in walk(root):
        ext = os.path.splitext(p)[1].lower()
        if ext in ('.png', '.bmp'):
            d = os.path.dirname(rel)
            sprites[d]['n'] += 1
            sprites[d]['bytes'] += os.path.getsize(p)
            image_ext[ext] += 1
            continue
        if ext not in ('.txt', '.lua'):
            other.append(dict(rel=rel, size=os.path.getsize(p)))
            continue
        txt = read(p)
        m = re.search(r'\[OBJECT:(\w+)\]', txt)
        otype = m.group(1) if m else None
        defs = []
        if otype:
            for tok, val in OBJ_TOKEN.findall(txt):
                if tok == otype or (otype == 'ITEM' and tok.startswith('ITEM_')) \
                   or (otype == 'GRAPHICS' and tok in ('TILE_PAGE',)) \
                   or (otype == 'DESCRIPTOR_COLOR' and tok == 'COLOR'):
                    defs.append(val.split(':')[0])
        raws.append(dict(rel=rel, dir=os.path.dirname(rel), name=os.path.basename(rel),
                         ext=ext, size=os.path.getsize(p), otype=otype, ndefs=len(defs),
                         sample=defs[:6]))
    return dict(raws=raws, sprites=dict(sprites), other=other, image_ext=image_ext)


# ==========================================
# FIGURES FOR THE OVERVIEW
# ==========================================
def stats(scanned):
    r, sp = scanned['raws'], scanned['sprites']
    lua = [f for f in r if f['ext'] == '.lua']
    # The folders the Lua files sit in, each named once at its shallowest.
    # The overview used to say they were in the example folders; they are
    # all under vanilla_procedural/scripts/.
    lua_dirs = sorted({f['dir'] for f in lua})
    tops = [d for d in lua_dirs if not any(d != o and d.startswith(o + '/') for o in lua_dirs)]
    sizes = sum(f['size'] for f in r) + sum(v['bytes'] for v in sp.values()) \
        + sum(f['size'] for f in scanned['other'])
    return dict(
        files=len(r) + sum(v['n'] for v in sp.values()) + len(scanned['other']),
        size=size_label(sizes),
        txt=sum(1 for f in r if f['ext'] == '.txt'),
        lua=len(lua), lua_dirs=tops,
        # PNG and BMP apart: the overview names PNG sheets. The two BMPs are
        # floors.bmp (the ALT_FLOORS page) and the interface's
        # black_background.bmp.
        png=scanned['image_ext']['.png'], bmp=scanned['image_ext']['.bmp'],
        images=sum(v['n'] for v in sp.values()), image_dirs=len(sp),
    )


# ==========================================
# WRITE
# ==========================================
def write(scanned):
    r, sp = scanned['raws'], scanned['sprites']
    L = header(NAME)
    L.append("Complete unmodified Dwarf Fortress vanilla raws, plus the vanilla sprite sheets. "
             "Mirrors DF's own mod folder layout, so the directory name tells you the object "
             "type before you open anything.\n")
    L.append("## How to use this\n")
    L.append("This is the authority for **what vanilla actually defines**: token spellings, "
             "existing material and reaction IDs, graphics tags, and name collisions to avoid "
             "when injecting new content.\n")
    L.append("```\ngrep -rln 'REACTION_CLASS:PITCH' vanilla_*/objects/\n```\n")
    bydir = collections.defaultdict(list)
    for f in r:
        bydir[f['dir'] or '(root)'].append(f)
    L.append(f"## Raws files ({len(r)} text files)\n")
    for dd in sorted(bydir):
        files = bydir[dd]
        types = collections.Counter(f['otype'] for f in files if f['otype'])
        tdesc = ', '.join(f"{k} x{v}" for k, v in types.most_common(4)) or 'no OBJECT token'
        tot = sum(f['ndefs'] for f in files)
        L.append(f"### `{dd}/`\n")
        L.append(f"{len(files)} files, {tdesc}" + (f", {tot} definitions total" if tot else "") + "\n")
        # The eight files that define the most; ties fall to name order.
        big = sorted(files, key=lambda a: (-a['ndefs'], a['name']))[:8]
        if any(f['ndefs'] for f in big):
            L.append("| File | Object | Defs | Examples |")
            L.append("|---|---|---|---|")
            for f in big:
                if not f['ndefs']:
                    continue
                L.append(f"| `{f['name']}` | {f['otype']} | {f['ndefs']} | {', '.join(f['sample'][:4])} |")
            if len(files) > 8:
                L.append(f"| _...{len(files)-8} more_ | | | |")
            L.append("")
    L.append(f"## Sprite sheets ({sum(v['n'] for v in sp.values())} images across {len(sp)} directories)\n")
    L.append("| Directory | Images | Size |")
    L.append("|---|---|---|")
    for dd in sorted(sp, key=lambda a: (-sp[a]['bytes'], a)):
        L.append(f"| `{dd}/` | {sp[dd]['n']} | {kb(sp[dd]['bytes'])} |")
    L.append("")
    if any(f['rel'] == 'readme.txt' for f in r):
        L.append("## Notes\n")
        L.append("- `readme.txt` at the root is **Bay 12's public-domain waiver** that shipped with "
                 "the raws, not a description of this repo. GitHub renders it as the landing page.")
        L.append("- Images remain under copyright per that notice; the text raws are public domain.")
    return '\n'.join(L)
