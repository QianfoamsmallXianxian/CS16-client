import re, pathlib
sp = pathlib.Path('android/app/src/main/res/values/strings.xml')
if sp.exists():
    s = sp.read_text()
    if 'name="app_name"' in s:
        s = re.sub(r'<string name="app_name">[^<]*</string>', '<string name="app_name">Counter Strike 1.6</string>', s)
    else:
        s = s.replace('</resources>', '    <string name="app_name">Counter Strike 1.6</string>\n</resources>')
    sp.write_text(s)
mf = pathlib.Path('android/app/src/main/AndroidManifest.xml')
if mf.exists():
    s = mf.read_text()
    if 'android:label="@string/app_name"' not in s:
        s = re.sub(r'android:label="[^"]*"', 'android:label="Counter Strike 1.6"', s)
        mf.write_text(s)
