import pathlib, sys, re

cm = pathlib.Path('3rdparty/mainui_cpp/CMakeLists.txt')
if not cm.exists():
    sys.exit(0)

s = cm.read_text()

s = re.sub(r'\n# CI_FORCE_MINIUTL\nif\(ANDROID\).*?endif\(\)\n', '', s, flags=re.DOTALL)

target_line = 'add_library (${MAINUI_LIBRARY} SHARED ${MAINUI_SOURCES})'
if target_line in s:
    if 'CI_FORCE_MINIUTL' not in s:
        inject = '''if(ANDROID)
    list(APPEND MAINUI_SOURCES "${CMAKE_CURRENT_SOURCE_DIR}/miniutl/bitstring.cpp")
    list(APPEND MAINUI_SOURCES "${CMAKE_CURRENT_SOURCE_DIR}/miniutl/generichash.cpp")
endif()

'''
        s = s.replace(target_line, inject + target_line)
        cm.write_text(s)
else:
    target_line2 = 'add_library(${MAINUI_LIBRARY} SHARED ${MAINUI_SOURCES})'
    if target_line2 in s:
        inject = '''if(ANDROID)
    list(APPEND MAINUI_SOURCES "${CMAKE_CURRENT_SOURCE_DIR}/miniutl/bitstring.cpp")
    list(APPEND MAINUI_SOURCES "${CMAKE_CURRENT_SOURCE_DIR}/miniutl/generichash.cpp")
endif()

'''
        s = s.replace(target_line2, inject + target_line2)
        cm.write_text(s)
