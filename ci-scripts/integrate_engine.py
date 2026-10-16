import pathlib, re, glob, os, shutil

JAVA = pathlib.Path('android/app/src/main/java')
MANIFEST = pathlib.Path('android/app/src/main/AndroidManifest.xml')
RES = pathlib.Path('android/app/src/main/res')

def write(p, content):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)

mf = JAVA / 'su/xash/cs16client/MainActivity.java'
write(mf, '''package su.xash.cs16client;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;

public class MainActivity extends Activity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        Intent i = new Intent();
        i.setClassName(getPackageName(), "su.xash.engine.XashActivity");
        i.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
        i.putExtra("gamedir", "cstrike");
        i.putExtra("gamelibdir", getApplicationInfo().nativeLibraryDir);
        i.putExtra("argv", "-dev 2 -log -dll @yapb");
        i.putExtra("package", getPackageName());
        startActivity(i);
        finish();
    }
}
''')

cz = JAVA / 'su/xash/cs16client/CZeroActivity.java'
write(cz, '''package su.xash.cs16client;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;

public class CZeroActivity extends Activity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        Intent i = new Intent();
        i.setClassName(getPackageName(), "su.xash.engine.XashActivity");
        i.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
        i.putExtra("gamedir", "czero");
        i.putExtra("gamelibdir", getApplicationInfo().nativeLibraryDir);
        i.putExtra("argv", "-dev 2 -log -dll @yapb");
        i.putExtra("package", getPackageName());
        startActivity(i);
        finish();
    }
}
''')

patched_r = 0
for f in glob.glob(str(JAVA / 'su/xash/engine/**/*.java'), recursive=True):
    p = pathlib.Path(f)
    s = p.read_text()
    orig = s
    s = re.sub(r'import\s+su\.xash\.engine\.R\s*;', 'import su.xash.cs16client.R;', s)
    s = re.sub(r'\bsu\.xash\.engine\.R\.', 'su.xash.cs16client.R.', s)
    s = re.sub(r'(?<![\w.])R\.', 'su.xash.cs16client.R.', s)
    s = re.sub(r'import\s+su\.xash\.engine\.([A-Z]\w*)\s*;', r'import su.xash.cs16client.\1;', s)
    s = re.sub(r'"su\.xash\.engine"', 'getPackageName()', s)
    s = re.sub(r'BuildConfig\.APPLICATION_ID', 'getPackageName()', s)
    s = re.sub(r'import\s+su\.xash\.engine\.BuildConfig\s*;', '', s)
    if s != orig:
        p.write_text(s)
        patched_r += 1
print(f"patched java R refs: {patched_r}")

manifest_src = pathlib.Path('/tmp/xash/android/app/src/main/AndroidManifest.xml')
if manifest_src.exists() and MANIFEST.exists():
    src = manifest_src.read_text()
    dst = MANIFEST.read_text()
    for m in re.finditer(r'<uses-permission[^/]*/>', src):
        perm = m.group(0)
        name = re.search(r'android:name="([^"]+)"', perm)
        if name and name.group(1) not in dst:
            dst = dst.replace('<application', perm + chr(10) + '    <application', 1)
    for act_name in ['su.xash.engine.XashActivity', 'su.xash.engine.EngineActivity',
                     'su.xash.engine.EngineActivityAlias', 'org.libsdl.app.SDLActivity']:
        if act_name not in dst:
            block = chr(10) + '        <activity' + chr(10) + \
                    f'            android:name="{act_name}"' + chr(10) + \
                    '            android:configChanges="orientation|screenSize|keyboardHidden|screenLayout|smallestScreenSize|uiMode|density"' + chr(10) + \
                    '            android:exported="false"' + chr(10) + \
                    '            android:theme="@style/Theme.Xash3D" />'
            dst = dst.replace('    </application>', block + chr(10) + '    </application>')
    MANIFEST.write_text(dst)
    print("manifest merged")

RES_SRC = pathlib.Path('/tmp/xash/android/app/src/main/res')
if RES_SRC.exists() and RES.exists():
    protected = ('mipmap-anydpi-v26', 'mipmap-hdpi', 'mipmap-mdpi', 'mipmap-xhdpi',
                 'mipmap-xxhdpi', 'mipmap-xxxhdpi')
    for d in RES_SRC.iterdir():
        if not d.is_dir():
            continue
        name = d.name
        if name in protected:
            continue
        dst_d = RES / name
        dst_d.mkdir(parents=True, exist_ok=True)
        for f in d.iterdir():
            if f.is_file():
                shutil.copy2(f, dst_d / f.name)
        print(f"copied res/{name}")

for g in ['mipmap-anydpi-v26', 'mipmap-hdpi', 'mipmap-mdpi', 'mipmap-xhdpi', 'mipmap-xxhdpi', 'mipmap-xxxhdpi']:
    src_d = RES_SRC / g
    if not src_d.exists():
        continue
    dst_d = RES / g
    if dst_d.exists():
        for f in src_d.iterdir():
            if f.is_file() and not (dst_d / f.name).exists():
                shutil.copy2(f, dst_d / f.name)

strings = RES / 'values' / 'strings.xml'
if strings.exists():
    s = strings.read_text()
    if 'name="app_name"' not in s:
        s = s.replace('</resources>', '    <string name="app_name">Counter Strike 1.6</string>' + chr(10) + '</resources>')
        strings.write_text(s)
    print("app_name ensured")

print("done")
