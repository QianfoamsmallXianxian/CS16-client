import pathlib, re, glob, shutil, sys

JAVA = pathlib.Path('android/app/src/main/java')
MANIFEST = pathlib.Path('android/app/src/main/AndroidManifest.xml')
RES = pathlib.Path('android/app/src/main/res')
ASSETS = pathlib.Path('android/app/src/main/assets')
XASH = pathlib.Path('/tmp/xash/android/app/src/main')

def write(p, content):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)

def read_xml_keys(path, tag):
    if not path.exists():
        return {}
    s = path.read_text()
    result = {}
    for m in re.finditer(r'<' + tag + r'\s+name="([^"]+)"[^>]*>.*?</' + tag + r'>', s, re.DOTALL):
        result[m.group(1)] = m.group(0)
    for m in re.finditer(r'<' + tag + r'\s+name="([^"]+)"[^/]*/>', s):
        result[m.group(1)] = m.group(0)
    return result

def merge_values_into(target_xml, source_xml, tag):
    if not source_xml.exists():
        return 0
    src = read_xml_keys(source_xml, tag)
    if not src:
        return 0
    if target_xml.exists():
        tgt = target_xml.read_text()
    else:
        tgt = '<?xml version="1.0" encoding="utf-8"?>' + chr(10) + '<resources>' + chr(10) + '</resources>'
    existing = read_xml_keys(target_xml, tag) if target_xml.exists() else {}
    added = 0
    for k, block in src.items():
        if k in existing:
            continue
        tgt = tgt.replace('</resources>', '    ' + block + chr(10) + '</resources>')
        added += 1
    if added:
        target_xml.parent.mkdir(parents=True, exist_ok=True)
        target_xml.write_text(tgt)
    return added

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
print("MainActivity/CZeroActivity written")

patched_java = 0
for f in glob.glob(str(JAVA / 'su/xash/engine/**/*.java'), recursive=True):
    p = pathlib.Path(f)
    s = p.read_text()
    orig = s
    s = re.sub(r'import\s+su\.xash\.engine\.R\s*;', 'import su.xash.cs16client.R;', s)
    s = re.sub(r'\bsu\.xash\.engine\.R\.', 'su.xash.cs16client.R.', s)
    s = re.sub(r'(?<![\w.])R\.', 'su.xash.cs16client.R.', s)
    s = re.sub(r'"su\.xash\.engine"', 'getPackageName()', s)
    s = re.sub(r'BuildConfig\.APPLICATION_ID', 'getPackageName()', s)
    s = re.sub(r'import\s+su\.xash\.engine\.BuildConfig\s*;', '', s)
    s = re.sub(r'import\s+su\.xash\.engine\.(?!R\b)([A-Z]\w*)\s*;', r'import su.xash.cs16client.\1;', s)
    if s != orig:
        p.write_text(s)
        patched_java += 1
print("patched java R refs: " + str(patched_java))

xash_java = XASH / 'java'
if xash_java.exists():
    for pkg_dir in xash_java.rglob('*.java'):
        rel = pkg_dir.relative_to(xash_java)
        if str(rel).startswith('su/xash/engine/'):
            continue
        dst = JAVA / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(pkg_dir, dst)
        print("copied java: " + str(rel))

strings_target = RES / 'values' / 'strings.xml'
strings_source = XASH / 'res' / 'values' / 'strings.xml'
n = merge_values_into(strings_target, strings_source, 'string')
print("strings added: " + str(n))

for tag, fname in [
    ('color', 'colors.xml'),
    ('dimen', 'dimens.xml'),
    ('style', 'styles.xml'),
    ('bool', 'bools.xml'),
    ('integer', 'integers.xml'),
    ('array', 'arrays.xml'),
    ('attr', 'attrs.xml'),
    ('string-array', 'string_arrays.xml'),
]:
    src = XASH / 'res' / 'values' / fname
    if not src.exists():
        continue
    dst = RES / 'values' / fname
    n = merge_values_into(dst, src, tag)
    print(f"{fname}: +{n}")

for x in XASH.glob('res/values-*'):
    if not x.is_dir():
        continue
    suffix = x.name.replace('values-', '')
    if suffix in ('v21', 'v24', 'v26', 'v31'):
        continue
    for f in x.iterdir():
        if not f.is_file():
            continue
        dst_dir = RES / ('values-' + suffix)
        dst_dir.mkdir(parents=True, exist_ok=True)
        dst = dst_dir / f.name
        if dst.exists():
            continue
        shutil.copy2(f, dst)
        print("copied lang: " + str(dst))

strings_target_x = RES / 'values' / 'strings.xml'
if strings_target_x.exists():
    s = strings_target_x.read_text()
    if 'name="app_name"' not in s:
        s = s.replace('</resources>', '    <string name="app_name">Counter Strike 1.6</string>' + chr(10) + '</resources>')
        strings_target_x.write_text(s)
    print("app_name ensured")

COPY_DIRS = ['layout', 'menu', 'navigation', 'xml', 'anim', 'animator',
             'interpolator', 'font', 'raw', 'transition', 'color', 'drawable']
PROTECT_PREFIX = ('mipmap',)

for d in COPY_DIRS:
    src_d = XASH / 'res' / d
    if not src_d.exists():
        continue
    dst_d = RES / d
    dst_d.mkdir(parents=True, exist_ok=True)
    for f in src_d.rglob('*'):
        if not f.is_file():
            continue
        rel = f.relative_to(src_d)
        dst = dst_d / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, dst)
    print("copied res/" + d)

for x in XASH.glob('res/drawable*'):
    if not x.is_dir():
        continue
    dst_d = RES / x.name
    dst_d.mkdir(parents=True, exist_ok=True)
    for f in x.iterdir():
        if not f.is_file():
            continue
        dst = dst_d / f.name
        if dst.exists():
            continue
        shutil.copy2(f, dst)
    print("copied " + x.name)

for x in XASH.glob('res/*'):
    if not x.is_dir():
        continue
    name = x.name
    if name in COPY_DIRS or name.startswith('drawable') or name.startswith('mipmap') or name.startswith('values'):
        continue
    if name in ('layout', 'menu', 'navigation', 'xml', 'anim', 'animator',
                'interpolator', 'font', 'raw', 'transition', 'color'):
        continue
    dst_d = RES / name
    dst_d.mkdir(parents=True, exist_ok=True)
    for f in x.rglob('*'):
        if not f.is_file():
            continue
        rel = f.relative_to(x)
        dst = dst_d / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not dst.exists():
            shutil.copy2(f, dst)
    print("copied res/" + name)

for g in ['mipmap-anydpi-v26', 'mipmap-hdpi', 'mipmap-mdpi', 'mipmap-xhdpi',
          'mipmap-xxhdpi', 'mipmap-xxxhdpi']:
    src_d = XASH / 'res' / g
    if not src_d.exists():
        continue
    dst_d = RES / g
    dst_d.mkdir(parents=True, exist_ok=True)
    for f in src_d.iterdir():
        if not f.is_file():
            continue
        dst = dst_d / f.name
        if dst.exists():
            continue
        shutil.copy2(f, dst)
    print("copied " + g)

if MANIFEST.exists():
    dst = MANIFEST.read_text()
    src_mf = XASH / 'AndroidManifest.xml'
    if src_mf.exists():
        src = src_mf.read_text()
        for m in re.finditer(r'<uses-permission[^>]*/>', src):
            perm = m.group(0)
            name_m = re.search(r'android:name="([^"]+)"', perm)
            if name_m and name_m.group(1) not in dst:
                dst = dst.replace('    <application', '    ' + perm + chr(10) + '    <application', 1)
        for m in re.finditer(r'<uses-feature[^>]*/>', src):
            feat = m.group(0)
            name_m = re.search(r'android:name="([^"]+)"', feat)
            if name_m and name_m.group(1) not in dst:
                dst = dst.replace('    <application', '    ' + feat + chr(10) + '    <application', 1)
        print("permissions merged")

    activities = re.findall(
        r'<activity\b[^>]*?android:name="([^"]+)"[^>]*?(?:/>|>.*?</activity>)',
        src, re.DOTALL) if src_mf.exists() else []

    for act_name in activities:
        if act_name in dst:
            continue
        block = chr(10) + '        <activity' + chr(10) + \
                '            android:name="' + act_name + '"' + chr(10) + \
                '            android:configChanges="orientation|screenSize|keyboardHidden|screenLayout|smallestScreenSize|uiMode|density"' + chr(10) + \
                '            android:exported="false"' + chr(10) + \
                '            android:theme="@android:style/Theme.Black.NoTitleBar.Fullscreen" />'
        dst = dst.replace('    </application>', block + chr(10) + '    </application>')

    for svc_name in re.findall(r'<service\b[^>]*?android:name="([^"]+)"', dst):
        pass

    MANIFEST.write_text(dst)
    print("manifest merged")

if (XASH / 'assets').exists():
    ASSETS.mkdir(parents=True, exist_ok=True)
    for f in (XASH / 'assets').rglob('*'):
        if not f.is_file():
            continue
        rel = f.relative_to(XASH / 'assets')
        dst = ASSETS / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not dst.exists():
            shutil.copy2(f, dst)
    print("assets copied")

styles = RES / 'values' / 'styles.xml'
if styles.exists():
    s = styles.read_text()
    s = s.replace('@style/Theme.Xash3D', '@android:style/Theme.Black.NoTitleBar.Fullscreen')
    styles.write_text(s)

for f in RES.rglob('*.xml'):
    try:
        s = f.read_text()
    except Exception:
        continue
    if 'Theme.Xash3D' in s:
        s2 = s.replace('@style/Theme.Xash3D', '@android:style/Theme.Black.NoTitleBar.Fullscreen')
        f.write_text(s2)

print("done")
