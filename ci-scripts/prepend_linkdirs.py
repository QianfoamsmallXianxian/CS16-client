import os, pathlib
sys_dir = os.environ['SYS']
mf = pathlib.Path('3rdparty/mainui_cpp/CMakeLists.txt')
s = mf.read_text()
if 'CI_LINKDIRS' in s:
    raise SystemExit(0)
header = 'link_directories("' + sys_dir + '/lib")\n' \
       + 'include_directories("' + sys_dir + '/include" "' + sys_dir + '/include/freetype2")\n' \
       + '# CI_LINKDIRS\n'
mf.write_text(header + s)
print('prepended link_directories to mainui CMakeLists')
