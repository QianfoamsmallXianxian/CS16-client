import pathlib, re
p = pathlib.Path('android/app/src/main/java/su/xash/engine/XashActivity.java')
if not p.exists():
    print('XashActivity.java not found')
    raise SystemExit(0)
s = p.read_text()
orig = s

if 'XashStartupTracker' not in s:
    s = s.replace(
        'import android.os.Bundle;',
        'import android.os.Bundle;\nimport su.xash.cs16client.XashStartupTracker;\nimport su.xash.cs16client.CS16CrashHandler;'
    ) if 'import android.os.Bundle;' in s else s

if 'markXashStarted' not in s:
    m = re.search(r'(protected\s+void\s+onCreate\s*\([^)]*\)\s*\{)', s)
    if m:
        insert = m.group(1) + '\n        XashStartupTracker.getInstance().markXashStarted();\n        try { CS16CrashHandler.install(this); } catch (Throwable x) {}'
        s = s[:m.start()] + insert + s[m.end():]

if s != orig:
    p.write_text(s)
    print('patched XashActivity')
else:
    print('XashActivity no change')
