import pathlib, re, glob, sys

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
patched_pkg = 0
for f in glob.glob(str(JAVA / 'su/xash/engine/**/*.java'), recursive=True):
    p = pathlib.Path(f)
    s = p.read_text()
    orig = s
    s = re.sub(r'import\s+su\.xash\.engine\.R\s*;', 'import su.xash.cs16client.R;', s)
    s = re.sub(r'\bsu\.xash\.engine\.R\.', 'su.xash.cs16client.R.', s)
    s = re.sub(r'(?<![\w.])R\.', 'su.xash.cs16client.R.', s)
    s = re.sub(r'import\s+su\.xash\.engine\.([A-Z]\w*)\s*;', r'import su.xash.cs16client.\1;', s)
    s = re.sub(r'"su\.xash\.engine"', 'getPackageName()', s)
    s = re.sub(r'su\.xash\.engine\.XashActivity', 'su.xash.engine.XashActivity', s)
    s = re.sub(r'BuildConfig\.APPLICATION_ID', 'getPackageName()', s)
    s = re.sub(r'import\s+su\.xash\.engine\.BuildConfig\s*;', '', s)
    if s != orig:
        p.write_text(s)
        patched_r += 1
print(f"patched java: {patched_r}")

if MANIFEST.exists():
    s = MANIFEST.read_text()
    if 'su.xash.engine.XashActivity' not in s:
        block = '''
        <activity
            android:name="su.xash.engine.XashActivity"
            android:configChanges="orientation|screenSize|keyboardHidden|screenLayout|smallestScreenSize|uiMode|density"
            android:exported="false"
            android:launchMode="singleTask"
            android:screenOrientation="sensorLandscape"
            android:theme="@android:style/Theme.Black.NoTitleBar.Fullscreen" />
        <activity
            android:name="su.xash.engine.EngineActivity"
            android:configChanges="orientation|screenSize|keyboardHidden|screenLayout|smallestScreenSize|uiMode|density"
            android:exported="false"
            android:launchMode="singleTask"
            android:theme="@android:style/Theme.Black.NoTitleBar.Fullscreen" />
        <activity
            android:name="org.libsdl.app.SDLActivity"
            android:configChanges="orientation|screenSize|keyboardHidden|screenLayout|smallestScreenSize|uiMode|density"
            android:exported="false"
            android:theme="@android:style/Theme.Black.NoTitleBar.Fullscreen" />
'''
        s = s.replace('    </application>', block + '    </application>')
        MANIFEST.write_text(s)
        print("manifest updated")

strings = RES / 'values' / 'strings.xml'
if strings.exists():
    s = strings.read_text()
    for key, val in [
        ('xash_loading', 'Loading...'),
        ('xash_error', 'Error'),
        ('xash_ok', 'OK'),
        ('xash_cancel', 'Cancel'),
    ]:
        if f'name="{key}"' not in s:
            s = s.replace('</resources>', f'    <string name="{key}">{val}</string>' + chr(10) + '</resources>')
    strings.write_text(s)
    print("strings patched")

ids = RES / 'values' / 'ids.xml'
if not ids.exists():
    ids.write_text('<?xml version="1.0" encoding="utf-8"?>' + chr(10) + '<resources></resources>')
print("done")
