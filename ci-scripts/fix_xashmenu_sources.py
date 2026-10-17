import pathlib, sys

cm = pathlib.Path('3rdparty/mainui_cpp/CMakeLists.txt')
if not cm.exists():
    sys.exit(0)

s = cm.read_text()

if 'CI_FORCE_MINIUTL' not in s:
    s += '''
if(ANDROID)
    set(CI_MINIUTL_FILES
        "${CMAKE_CURRENT_SOURCE_DIR}/miniutl/bitstring.cpp"
        "${CMAKE_CURRENT_SOURCE_DIR}/miniutl/generichash.cpp"
    )
    foreach(_tgt ${MAINUI_LIBRARY} xashmenu xashmenu64)
        if(TARGET ${_tgt})
            target_sources(${_tgt} PRIVATE ${CI_MINIUTL_FILES})
        endif()
    endforeach()
endif()
'''
    cm.write_text(s)
