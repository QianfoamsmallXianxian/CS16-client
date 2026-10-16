import pathlib, re
root = pathlib.Path('3rdparty/mainui_cpp').resolve()
if root.exists():
    pat = re.compile(r'(?<![A-Za-z0-9_./-])([A-Za-z0-9_./-]+\.(?:cpp|cc|cxx|c))(?![A-Za-z0-9_])')
    for cm in list(root.rglob('CMakeLists.txt')) + list(root.rglob('*.cmake')):
        try:
            text = cm.read_text()
        except Exception:
            continue
        base = cm.parent
        new = text
        for m in pat.finditer(text):
            rel = m.group(1)
            if (base / rel).resolve().exists():
                continue
            name = pathlib.Path(rel).name
            hits = [x for x in base.rglob('*') if x.is_file() and x.name.lower() == name.lower()]
            if hits:
                nr = str(hits[0].relative_to(base)).replace(chr(92), '/')
                new = new.replace(rel, nr)
                continue
            new = re.sub(r'(?m)^[ \t]*' + re.escape(rel) + r'[ \t]*\n', '', new)
            new = re.sub(r'\s+' + re.escape(rel) + r'(?=\s)', ' ', new)
        if new != text:
            cm.write_text(new)

GUARD = 'XASH_INT64_TYPES_DEFINED'
for path, olds in [
    ('3rdparty/mainui_cpp/miniutl/miniutl.h', [
        ('typedef int64_t int64;', '#ifndef ' + GUARD + chr(10) + 'typedef int64_t int64;'),
        ('typedef uint64_t uint64;', 'typedef uint64_t uint64;' + chr(10) + '#endif'),
    ]),
    ('engine/archtypes.h', [
        ('typedef long long int64;', '#ifndef ' + GUARD + chr(10) + '#define ' + GUARD + ' 1' + chr(10) + 'typedef long long int64;'),
        ('typedef unsigned long long uint64;', 'typedef unsigned long long uint64;' + chr(10) + '#endif'),
    ]),
]:
    p2 = pathlib.Path(path)
    if not p2.exists():
        continue
    s2 = p2.read_text()
    if GUARD in s2:
        continue
    for old, new in olds:
        s2 = s2.replace(old, new)
    p2.write_text(s2)

pats = [
    re.compile(r'^[ \t]*#[ \t]*define[ \t]+uint64[ \t]+uint64_bruh[ \t]*\r?\n', re.M),
    re.compile(r'^[ \t]*#[ \t]*define[ \t]+int64[ \t]+int64_bruh[ \t]*\r?\n', re.M),
    re.compile(r'^[ \t]*#undef[ \t]+uint64[ \t]*\r?\n', re.M),
    re.compile(r'^[ \t]*#undef[ \t]+int64[ \t]*\r?\n', re.M),
]
for root2 in ['cl_dll','dlls','common','public','3rdparty/mainui_cpp']:
    r = pathlib.Path(root2)
    if not r.exists():
        continue
    for f in r.rglob('*'):
        if not f.is_file():
            continue
        if f.suffix not in ('.cpp','.cc','.cxx','.c','.h','.hpp','.hxx'):
            continue
        try:
            s3 = f.read_text()
        except Exception:
            continue
        s4 = s3
        for pp in pats:
            s4 = pp.sub('', s4)
        if s4 != s3:
            f.write_text(s4)
