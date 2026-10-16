import re, pathlib
p = pathlib.Path('3rdparty/mainui_cpp/CMakeLists.txt')
if not p.exists():
    raise SystemExit(0)
lines = p.read_text().splitlines()
out = []
targets = ('fontconfig','freetype','freetype2','x11','wayland','glib','pango','xkbcommon','xi','xcursor','xinerama','xrandr','xss','xext','alsa','pulse','pulseaudio','dbus','libusb','udev')
for ln in lines:
    m = re.match(r'^(\s*)pkg_check_modules\s*\(\s*(\S+)\s+(?:REQUIRED\s+|QUIET\s+|NO_CMAKE_PATH\s+)*([\w.-]+)', ln)
    if m:
        indent = m.group(1)
        module = m.group(3).lower().split('>=')[0].split('<')[0].strip()
        if module in targets or any(module.startswith(t) for t in targets):
            out.append(f'{indent}if(NOT ANDROID)')
            out.append(ln)
            out.append(f'{indent}endif()')
            continue
    out.append(ln)
p.write_text(chr(10).join(out) + chr(10))
