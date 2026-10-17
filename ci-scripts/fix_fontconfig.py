import pathlib, re, sys

root = pathlib.Path('3rdparty/mainui_cpp')
if not root.exists():
    sys.exit(0)

cpp = root / 'font' / 'FreeTypeFont.cpp'
if cpp.exists():
    cpp.write_text("// CI_DISABLED_FREETYPE\n")

win = root / 'font' / 'WinAPIFont.cpp'
if win.exists():
    win.write_text("// CI_DISABLED_WINAPI\n")

h = root / 'font' / 'FreeTypeFont.h'
if h.exists():
    s = h.read_text()
    if 'CI_DISABLED_FREETYPE' not in s:
        s = '#if 0 // CI_DISABLED_FREETYPE\n' + s + '\n#endif\n'
        h.write_text(s)

fm = root / 'font' / 'FontManager.cpp'
if fm.exists():
    s = fm.read_text()
    orig = s
    s = re.sub(r'^\s*#include\s+["<]FreeTypeFont\.h[">]\s*', '', s, flags=re.M)
    s = re.sub(r'^(\s*.*CFreeTypeFontBackend.*)$', r'// \1', s, flags=re.M)
    s = re.sub(r'^(\s*.*CWinAPIFontBackend.*)$', r'// \1', s, flags=re.M)
    if s != orig:
        fm.write_text(s)

cm = root / 'CMakeLists.txt'
if cm.exists():
    s = cm.read_text()
    if 'CI_NO_FONTCONFIG_AND_FREETYPE' not in s:
        s += '\n# CI_NO_FONTCONFIG_AND_FREETYPE\nif(ANDROID)\n    add_definitions(-DNO_FONTCONFIG -DNO_FREETYPE)\nendif()\n'
        cm.write_text(s)
