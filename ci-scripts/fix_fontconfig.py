import pathlib, sys
root = pathlib.Path('3rdparty/mainui_cpp')
if not root.exists():
    sys.exit(0)

h = root / 'font' / 'FreeTypeFont.h'
h.write_text('''#ifndef FREETYPE_FONT_H
#define FREETYPE_FONT_H
#include "BaseFontBackend.h"
class CFreeTypeFont : public CBaseFont
{
public:
    CFreeTypeFont() {}
    virtual ~CFreeTypeFont() {}
    virtual bool LoadFont(const char *name, int size, int flags) { return false; }
    virtual void GetStringSize(const char *text, int *w, int *h) { if(w)*w=0; if(h)*h=0; }
    virtual void DrawString(int x, int y, const char *text, int r, int g, int b, int a) {}
    static void *m_Library;
};
#endif
''')

cpp = root / 'font' / 'FreeTypeFont.cpp'
cpp.write_text('''#include "FreeTypeFont.h"
void *CFreeTypeFont::m_Library = nullptr;
''')

win = root / 'font' / 'WinAPIFont.cpp'
if win.exists():
    win.write_text("")

cm = root / 'CMakeLists.txt'
if cm.exists():
    s = cm.read_text()
    if 'CI_NO_FONTCONFIG_AND_FREETYPE' not in s:
        s += '\nif(ANDROID)\n    add_definitions(-DNO_FONTCONFIG -DNO_FREETYPE)\nendif()\n'
        cm.write_text(s)
