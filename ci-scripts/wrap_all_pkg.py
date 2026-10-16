import pathlib, re

targets = [
    '3rdparty/mainui_cpp/CMakeLists.txt',
    '3rdparty/mainui_cpp/controls/CMakeLists.txt',
    '3rdparty/mainui_cpp/menus/CMakeLists.txt',
    '3rdparty/mainui_cpp/font/CMakeLists.txt',
]

KEEP_PKGS = set()

for path in targets:
    p = pathlib.Path(path)
    if not p.exists():
        continue
    s = p.read_text()
    if 'CI_WRAP_START' in s:
        print(path + ': already wrapped')
        continue
    lines = s.splitlines()
    out = []
    wrapped = 0
    i = 0
    while i < len(lines):
        ln = lines[i]
        m = re.match(r'^(\s*)pkg_check_modules\s*\(\s*(\S+)\s+(?:REQUIRED\s+|QUIET\s+|NO_CMAKE_PATH\s+)*([\w.-]+)', ln)
        if m:
            indent = m.group(1)
            module = m.group(3).lower().split('>=')[0].split('<')[0].strip()
            if module in KEEP_PKGS or any(module.startswith(k) for k in KEEP_PKGS):
                out.append(ln)
                i += 1
                continue
            out.append(f'{indent}# CI_WRAP_START {module}')
            out.append(f'{indent}if(NOT ANDROID)')
            out.append(ln)
            out.append(f'{indent}endif()')
            out.append(f'{indent}# CI_WRAP_END {module}')
            wrapped += 1
            i += 1
            continue
        out.append(ln)
        i += 1
    if wrapped > 0:
        p.write_text(chr(10).join(out) + chr(10))
        print(f'{path}: wrapped {wrapped}')
    else:
        print(f'{path}: nothing')

for f in pathlib.Path('3rdparty/mainui_cpp').rglob('CMakeLists.txt'):
    if str(f) in targets:
        continue
    try:
        s = f.read_text()
    except Exception:
        continue
    if 'pkg_check_modules' not in s:
        continue
    if 'CI_WRAP_START' in s:
        print(f'{f}: already wrapped')
        continue
    lines = s.splitlines()
    out = []
    wrapped = 0
    for ln in lines:
        m = re.match(r'^(\s*)pkg_check_modules\s*\(\s*(\S+)\s+(?:REQUIRED\s+|QUIET\s+|NO_CMAKE_PATH\s+)*([\w.-]+)', ln)
        if m:
            indent = m.group(1)
            module = m.group(3).lower().split('>=')[0].split('<')[0].strip()
            if module in KEEP_PKGS or any(module.startswith(k) for k in KEEP_PKGS):
                out.append(ln)
                continue
            out.append(f'{indent}# CI_WRAP_START {module}')
            out.append(f'{indent}if(NOT ANDROID)')
            out.append(ln)
            out.append(f'{indent}endif()')
            out.append(f'{indent}# CI_WRAP_END {module}')
            wrapped += 1
            continue
        out.append(ln)
    if wrapped > 0:
        f.write_text(chr(10).join(out) + chr(10))
        print(f'{f}: wrapped {wrapped}')

print('done')
