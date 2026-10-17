import pathlib, shutil, sys, os

root = pathlib.Path('.')
dest = root / 'android/app/src/main/jniLibs/arm64-v8a'
engine = root / 'engine-libs'
ndk_home = os.environ.get('ANDROID_NDK_HOME', '')

if not dest.exists():
    sys.exit(1)

for f in ['libandroid.so', 'libdl.so', 'liblog.so', 'libc.so', 'libm.so', 'libstdc++.so']:
    p = dest / f
    if p.exists(): p.unlink()

required = [
    'libxash.so', 'libfilesystem_stdio.so', 'libSDL2.so', 
    'libyapb_android_arm64.so', 'libserver.so', 'libref_gl4es.so', 
    'libref_gles1.so', 'libref_gles3compat.so'
]
for r in required:
    src = engine / r
    if src.exists() and not (dest / r).exists(): 
        shutil.copy(src, dest / r)

xashmenu64 = dest / 'libxashmenu64.so'
menu = dest / 'libmenu.so'
if xashmenu64.exists():
    shutil.copy(xashmenu64, menu)
    xashmenu64.unlink()

if ndk_home:
    cpp_shared = pathlib.Path(ndk_home) / 'toolchains/llvm/prebuilt/linux-x86_64/sysroot/usr/lib/aarch64-linux-android/libc++_shared.so'
    if cpp_shared.exists():
        shutil.copy(cpp_shared, dest / 'libc++_shared.so')
