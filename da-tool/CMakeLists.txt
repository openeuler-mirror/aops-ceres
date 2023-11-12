cmake_minimum_required(VERSION 3.15)
project(da-tool-analysis)

set(CMAKE_CXX_STANDARD 11)

option(WITH_DEBUG "debug mode" OFF)

if (WITH_DEBUG)
    message("-- Note:da-tool debug mode")
    add_compile_options(-O3 -g -DWITH_DEBUG)
else()
    message("-- Note:da-tool not debug mode")
    add_compile_options(-O3)
endif()

include_directories(da_tool_analysis_srcs PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/analysis
)

set(da_tool_analysis_srcs
    analysis/trace_resolve.cpp
    analysis/time_pair.cpp
    analysis/config.cpp
    analysis/function_stack.cpp
    analysis/sched_analysis.cpp
    main.cpp
)

add_executable(da-tool-analysis ${da_tool_analysis_srcs})
