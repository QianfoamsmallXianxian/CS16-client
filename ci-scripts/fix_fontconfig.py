import pathlib, re, sys
root = pathlib.Path('3rdparty/mainui_cpp')
if not root.exists():
    sys.exit(0)

h = root / 'font' / 'FreeTypeFont.h'
h.write_text("")

cpp = root / 'font' / 'FreeTypeFont.cpp'
cpp.write_text("")

win = root / 'font' / 'WinAPIFont.cpp'
if win.exists():
    win.write_text("")

fm = root / 'font' / 'FontManager.cpp'
if fm.exists():
    s = fm.read_text()
    s = re.sub(r'^\s*#include\s+["<].*FreeType.*[">]\s*', '', s, flags=re.M)
    lines = s.splitlines()
    out = []
    for ln in lines:
        if 'CFreeTypeFont' in ln or 'FT_Init_FreeType' in ln or 'FT_Done_FreeType' in ln:
            if 'font = new' in ln:
                out.append(re.sub(r'new\s+CFreeTypeFont\(\)', 'nullptr', ln))
            else:
                out.append('// ' + ln)
            continue
        out.append(ln)
    fm.write_text('\n'.join(out) + '\n')

cm = root / 'CMakeLists.txt'
if cm.exists():
    s = cm.read_text()
    if 'CI_NO_FONTCONFIG_AND_FREETYPE' not in s:
        s += '\nif(ANDROID)\n    add_definitions(-DNO_FONTCONFIG -DNO_FREETYPE)\nendif()\n'
        cm.write_text(s)
