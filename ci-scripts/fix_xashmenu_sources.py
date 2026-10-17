import pathlib, sys, re

cm = pathlib.Path('3rdparty/mainui_cpp/CMakeLists.txt')
if not cm.exists():
    sys.exit(0)

s = cm.read_text()

s = s.replace('set(MAINUI_LIBRARY xashmenu64)', 'set(MAINUI_LIBRARY menu)')
s = s.replace('set(MAINUI_LIBRARY xashmenu)', 'set(MAINUI_LIBRARY menu)')
s = s.replace('set(MAINUI_LIBRARY "xashmenu64")', 'set(MAINUI_LIBRARY "menu")')
s = s.replace('set(MAINUI_LIBRARY "xashmenu")', 'set(MAINUI_LIBRARY "menu")')
s = s.replace('xashmenu64', 'menu')
s = s.replace('xashmenu', 'menu')

s = re.sub(r'\nif\(ANDROID\)\n    list\(APPEND MAINUI_SOURCES.*?endif\(\)\n', '', s, flags=re.DOTALL)

target_line = 'add_library (${MAINUI_LIBRARY} SHARED ${MAINUI_SOURCES})'
if target_line in s:
    inject = '''if(ANDROID)
    file(GLOB ALL_MINIUTL_CPP "${CMAKE_CURRENT_SOURCE_DIR}/miniutl/*.cpp")
    foreach(_cpp ${ALL_MINIUTL_CPP})
        list(APPEND MAINUI_SOURCES ${_cpp})
    endforeach()
    list(REMOVE_DUPLICATES MAINUI_SOURCES)
endif()

'''
    s = s.replace(target_line, inject + target_line)
else:
    target_line2 = 'add_library(${MAINUI_LIBRARY} SHARED ${MAINUI_SOURCES})'
    if target_line2 in s:
        inject = '''if(ANDROID)
    file(GLOB ALL_MINIUTL_CPP "${CMAKE_CURRENT_SOURCE_DIR}/miniutl/*.cpp")
    foreach(_cpp ${ALL_MINIUTL_CPP})
        list(APPEND MAINUI_SOURCES ${_cpp})
    endforeach()
    list(REMOVE_DUPLICATES MAINUI_SOURCES)
endif()

'''
        s = s.replace(target_line2, inject + target_line2)

cm.write_text(s)
