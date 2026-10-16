cmake_minimum_required(VERSION 3.10)
project(cs16_crash_handler CXX)

add_library(cs16_crash_handler SHARED crash_handler.cpp)

find_library(log-lib log)
find_library(android-lib android)
find_library(dl-lib dl)

target_link_libraries(cs16_crash_handler
    ${log-lib}
    ${android-lib}
    ${dl-lib}
)
