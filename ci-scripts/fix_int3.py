import pathlib, re
roots = ['3rdparty/ReGameDLL_CS', '3rdparty/mainui_cpp', 'dlls', 'cl_dll', 'engine', 'common']
pats = [
    (re.compile(r'#\s*define\s+DebuggerBreak\s*\(\s*\)\s*[^\n]*'), '#define DebuggerBreak() ((void)0)'),
    (re.compile(r'#\s*define\s+DebuggerBreakIfDebugging\s*\(\s*\)\s*[^\n]*'), '#define DebuggerBreakIfDebugging() ((void)0)'),
    (re.compile(r'#\s*define\s+DebugBreak\s*\(\s*\)\s*[^\n]*'), '#define DebugBreak() ((void)0)'),
    (re.compile(r'__asm__\s+__volatile__\s*\(\s*"int3;?"\s*\)'), '((void)0)'),
    (re.compile(r'__asm__\s+volatile\s*\(\s*"int3;?"\s*\)'), '((void)0)'),
    (re.compile(r'asm\s+volatile\s*\(\s*"int3;?"\s*\)'), '((void)0)'),
    (re.compile(r'asm\s*\(\s*"int3;?"\s*\)'), '((void)0)'),
    (re.compile(r'__asm\s+int\s+3\s*;?'), '((void)0)'),
    (re.compile(r'__debugbreak\s*\(\s*\)'), '((void)0)'),
]
for root in roots:
    r = pathlib.Path(root)
    if not r.exists(): continue
    for f in r.rglob('*'):
        if not f.is_file(): continue
        if f.suffix not in ('.cpp','.cc','.cxx','.c','.h','.hpp','.hxx','.inl'): continue
        try: s = f.read_text()
        except Exception: continue
        s2 = s
        for pat, rep in pats: s2 = pat.sub(rep, s2)
        if s2 != s: f.write_text(s2)
