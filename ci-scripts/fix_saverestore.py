import pathlib, re
p = pathlib.Path('3rdparty/ReGameDLL_CS/regamedll/dlls/saverestore.cpp')
if p.exists():
    lines = p.read_text().splitlines()
    if len(lines) >= 429:
        idx = 428
        orig = lines[idx]
        new = orig.replace('(uint32)', '(uint32)(uintptr_t)')
        new = new.replace('reinterpret_cast<uint32>', 'reinterpret_cast<uint32>(reinterpret_cast<uintptr_t>')
        if new != orig:
            lines[idx] = new
            p.write_text(chr(10).join(lines) + chr(10))
root = pathlib.Path('3rdparty/ReGameDLL_CS')
if root.exists():
    pat = re.compile(r'[ \t]*__gcclibcxx_demangle_callback[ \t]*;?[ \t]*\r?\n')
    for f in root.rglob('*'):
        if not f.is_file(): continue
        try: s = f.read_text()
        except Exception: continue
        if '__gcclibcxx_demangle_callback' in s:
            s2 = pat.sub('', s)
            if s2 != s: f.write_text(s2)
