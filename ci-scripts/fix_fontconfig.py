import pathlib, re, sys

root = pathlib.Path('3rdparty/mainui_cpp')
if not root.exists():
    sys.exit(0)

patched = 0

h = root / 'font' / 'FreeTypeFont.h'
if h.exists():
    s = h.read_text()
    if '#include <fontconfig/fontconfig.h>' in s and '#if defined(USE_FONTCONFIG)' not in s:
        s = s.replace('#include <fontconfig/fontconfig.h>', 
                      '#if defined(USE_FONTCONFIG)\n#include <fontconfig/fontconfig.h>\n#endif')
        h.write_text(s)
        patched += 1

for cpp in [root / 'font' / 'FreeTypeFont.cpp', root / 'font' / 'FontManager.cpp']:
    if not cpp.exists():
        continue
    s = cpp.read_text()
    if '#include <fontconfig/fontconfig.h>' in s and '#if defined(USE_FONTCONFIG)' not in s:
        s = s.replace('#include <fontconfig/fontconfig.h>', 
                      '#if defined(USE_FONTCONFIG)\n#include <fontconfig/fontconfig.h>\n#endif')
    
    if 'FcInitLoadConfigAndFonts' in s and 'NO_FONTCONFIG' not in s:
        s = '#define NO_FONTCONFIG\n' + s
        s = re.sub(r'FcInitLoadConfigAndFonts\(\)', 'nullptr', s)
        s = re.sub(r'FcConfigGetFonts\([^)]*\)', 'nullptr', s)
        s = re.sub(r'FcFontSetDestroy\([^)]*\)', '((void)0)', s)
        s = re.sub(r'FcPatternDestroy\([^)]*\)', '((void)0)', s)
        s = re.sub(r'FcConfigDestroy\([^)]*\)', '((void)0)', s)
        s = re.sub(r'FcPatternCreate\(\)', 'nullptr', s)
        s = re.sub(r'FcConfigSubstitute\([^)]*\)', '((void)0)', s)
        s = re.sub(r'FcDefaultSubstitute\([^)]*\)', '((void)0)', s)
        s = re.sub(r'FcFontMatch\([^)]*\)', 'nullptr', s)
        cpp.write_text(s)
        patched += 1

cm = root / 'CMakeLists.txt'
if cm.exists():
    s = cm.read_text()
    if 'CI_NO_FONTCONFIG' not in s:
        s += '\n# CI_NO_FONTCONFIG\nif(ANDROID)\n    add_definitions(-DNO_FONTCONFIG)\nendif()\n'
        cm.write_text(s)
