import pathlib, re
p = pathlib.Path('3rdparty/mainui_cpp/CMakeLists.txt')
if not p.exists():
    raise SystemExit(0)
s = p.read_text()
for old, new in [
    (r'set\s*\(\s*XASH_SDK\s+"\.\./"\s*\)', 'set(XASH_SDK "../../")'),
    (r'set\s*\(\s*XASH_SDK\s+\.\./\s*\)', 'set(XASH_SDK "../../")'),
]:
    s, _ = re.subn(old, new, s)
p.write_text(s)
