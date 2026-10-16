import pathlib
p = pathlib.Path('android/app/build.gradle')
if not p.exists():
    raise SystemExit(0)
s = p.read_text()
deps = [
    'com.google.android.material:material:1.11.0',
    'androidx.appcompat:appcompat:1.6.1',
    'androidx.constraintlayout:constraintlayout:2.1.4',
    'androidx.preference:preference:1.2.1',
    'androidx.core:core:1.12.0',
    'androidx.activity:activity:1.8.2',
    'androidx.navigation:navigation-fragment:2.7.7',
    'androidx.navigation:navigation-ui:2.7.7',
    'androidx.recyclerview:recyclerview:1.3.2',
    'androidx.fragment:fragment:1.6.2',
    'androidx.lifecycle:lifecycle-runtime:2.7.0',
    'androidx.lifecycle:lifecycle-viewmodel:2.7.0',
    'androidx.lifecycle:lifecycle-livedata:2.7.0',
    'androidx.lifecycle:lifecycle-common-java8:2.7.0',
    'androidx.webkit:webkit:1.10.0',
    'androidx.documentfile:documentfile:1.0.1',
    'androidx.viewpager2:viewpager2:1.1.0',
    'androidx.swiperefreshlayout:swiperefreshlayout:1.1.0',
    'androidx.cardview:cardview:1.0.0',
    'androidx.vectordrawable:vectordrawable:1.1.0',
    'androidx.media:media:1.7.0',
    'androidx.legacy:legacy-support-v4:1.0.0',
    'androidx.annotation:annotation:1.7.1',
]
seen = set()
uniq = []
for d in deps:
    if d in seen:
        continue
    seen.add(d)
    uniq.append(d)
to_add = [d for d in uniq if d not in s]
if not to_add:
    print('all present')
    raise SystemExit(0)
block = chr(10).join('    implementation "' + d + '"' for d in to_add)
if 'dependencies {' in s:
    s = s.replace('dependencies {', 'dependencies {' + chr(10) + block, 1)
else:
    s += chr(10) + 'dependencies {' + chr(10) + block + chr(10) + '}' + chr(10)
p.write_text(s)
print('added ' + str(len(to_add)) + ' deps')
