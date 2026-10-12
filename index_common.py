"""
index_common.py

Shared pieces for the repo index generators: the repo registry, reading and
walking a repo without its own index tooling, size and number formatting, and
the header every generated index opens with.

Nothing here reads the live game or the RM project. It only parses the clones.
"""
import os
import hashlib

GITHUB_USER = 'grungeisdead85'

# ==========================================
# THE REPO REGISTRY
# ==========================================
# Every repo the overview (REFERENCE_REPOS.md) covers, in the order it
# presents them.
#   name   the repo, and the folder its clone sits in
#   index  the file the generator writes at the repo's root. None when the
#          index is written by hand (rm_knowledge_base's INDEX.md, which the
#          generator only checks) or the repo has no index at all
#          (mods_backup_premigration, a snapshot described only in the
#          overview).
#   blurb  one line for the companion list in every index header
REPOS = [
    dict(name='df_data_reference', index='df_data_reference_INDEX.md',
         blurb='path maps and structure dumps from a live game'),
    dict(name='vanilla_raws_reference', index='vanilla_raws_reference_INDEX.md',
         blurb='complete vanilla DF raws and sprite sheets'),
    dict(name='refinish_metal_tools', index='refinish_metal_tools_INDEX.md',
         blurb='archived probe scripts, reference only'),
    dict(name='rm_knowledge_base', index=None, hand_index='INDEX.md',
         blurb="what RM's development has established, with its evidence, "
               "and RM's development notes"),
    dict(name='argmod_injection_all_ports', index='argmod_injection_all_ports_INDEX.md',
         blurb="the ArgMOD and Elemental Metals Library ports to RM's module engine"),
    dict(name='mods_backup_premigration', index=None,
         blurb='RM, Making Fuel and Making Concrete as they stood before the RM core migration'),
]
BY_NAME = {r['name']: r for r in REPOS}

# The repo that holds these generators and the overview.
HUB = 'rm_knowledge_base'


def repo_url(name):
    return 'https://github.com/%s/%s' % (GITHUB_USER, name)


# ==========================================
# INDEX TOOLING IS NOT REPO CONTENT
# ==========================================
# The generators, the indexes and the overview sit inside the repos they
# describe. Counted as content they inflated every figure (df_data_reference's
# 65 files read as 73) and listed themselves as dumps and tools, so every walk
# skips them. Only at a repo's root: a file of the same name deeper down is
# content like any other.
TOOLING_DIRS = {'repo_index_generators'}
TOOLING_FILES = ({'.gitattributes', 'INDEX.md', 'REFERENCE_REPOS.md'}
                 | {r['index'] for r in REPOS if r['index']})


def read(p):
    """A file as text with CRLF folded to LF, whatever its encoding."""
    with open(p, 'rb') as f:
        return f.read().decode('utf-8', errors='replace').replace('\r\n', '\n')


def md5(p):
    with open(p, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def walk(root):
    """Yield (path, rel) for every content file under root.

    rel always uses '/' so an index reads the same whichever OS ran it.
    Directories and files are visited in sorted order. os.walk's own order is
    whatever the filesystem lists, which differs between machines, and ties in
    the indexes (which sample rows show, which files a path row names) used to
    follow it, so two runs on two machines could disagree with nothing changed.
    """
    for dp, dn, fn in os.walk(root):
        rel_dir = os.path.relpath(dp, root)
        at_root = rel_dir == '.'
        dn[:] = sorted(d for d in dn
                       if d != '.git' and not (at_root and d in TOOLING_DIRS))
        for f in sorted(fn):
            if at_root and f in TOOLING_FILES:
                continue
            p = os.path.join(dp, f)
            yield p, os.path.relpath(p, root).replace(os.sep, '/')


def kb(n):
    """A file size as the indexes print it: 5K, or 565B under a kilobyte."""
    return f"{n/1024:.0f}K" if n >= 1024 else f"{n}B"


def size_label(n):
    """A repo's size: the bytes of its content files, no .git, no tooling."""
    return f"{n/1048576:.1f}M" if n >= 1048576 else f"{n/1024:.0f}K"


_WORDS = ['no', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight',
          'nine', 'ten', 'eleven', 'twelve']


def number_word(n, capital=False):
    """Small counts as words, the way the prose around them reads."""
    w = _WORDS[n] if 0 <= n < len(_WORDS) else str(n)
    return w[0].upper() + w[1:] if capital else w


# ==========================================
# THE HEADER EVERY GENERATED INDEX CARRIES
# ==========================================
# Where the repo is, how to clone it, its companions, and that the index is
# generated, so nobody hand-edits a file the next run overwrites. Before this
# was rebuilt the header was added by a step the archive never kept, and it
# still pointed at the old account name and named two companions.
def header(name):
    L = [f"# {name}\n"]
    L.append(f"> **Repository:** {repo_url(name)}")
    L.append(">")
    L.append("> ```")
    L.append(f"> git clone --depth 1 {repo_url(name)}.git")
    L.append("> ```")
    L.append(">")
    L.append("> **Companion repos:**")
    for r in REPOS:
        if r['name'] != name:
            L.append(f"> - [{r['name']}]({repo_url(r['name'])}): {r['blurb']}")
    L.append(">")
    L.append("> A copy of this index also lives in the Refinish Metal project, where it is")
    L.append("> readable without cloning. See `REFERENCE_REPOS.md` there for the overview, and")
    L.append("> note that DFHack documentation is **not** in any repo.")
    L.append(f"> Both copies are generated by `build_indexes.py`, in {HUB}'s")
    L.append("> `repo_index_generators/`; regenerate rather than hand-editing either.\n")
    return L


def plain_stats(root):
    """File count and size for a repo that has no index of its own."""
    sizes = [os.path.getsize(p) for p, rel in walk(root)]
    return dict(files=len(sizes), size=size_label(sum(sizes)))


def headings(txt, level):
    """The text of every markdown heading of exactly this level, in order."""
    mark = '#' * level + ' '
    return [l[len(mark):].strip() for l in txt.split('\n') if l.startswith(mark)]
