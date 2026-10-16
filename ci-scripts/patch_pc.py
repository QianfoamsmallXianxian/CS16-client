import os, pathlib, re
sys_dir = os.environ['SYS']
libdir = sys_dir + '/lib'
mapping = {'fontconfig': 'fontconfig', 'freetype2': 'freetype', 'expat': 'expat'}
for name, lib in mapping.items():
    pc = pathlib.Path(libdir) / 'pkgconfig' / (name + '.pc')
    if not pc.exists(): continue
    s = pc.read_text()
    s = re.sub(r'-L\S+', '', s)
    s = re.sub(r'-lfontconfig', libdir + '/libfontconfig.a', s)
    s = re.sub(r'-lfreetype', libdir + '/libfreetype.a', s)
    s = re.sub(r'-lexpat', libdir + '/libexpat.a', s)
    pc.write_text(s)
