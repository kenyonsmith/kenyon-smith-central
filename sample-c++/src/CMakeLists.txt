#################################################################################
# CMakeLists.txt file 
#
# Revision History
# May 17, 2019  K. Smith     / Initial Implementation
#################################################################################

cmake_minimum_required(VERSION 3.1)
set(BINARY_NAME sample-c++)

set(src_files sample.cpp
    sampleAppSettings.cpp)

include_directories(${PROJECT_SOURCE_DIR}/include)

set(EXECUTABLE_OUTPUT_PATH ${OUTPUT_DIR})
add_executable(${BINARY_NAME} ${src_files})
target_include_directories(${BINARY_NAME} PRIVATE ${COMMON_LIB_HEADER_DIR})
target_link_libraries(${BINARY_NAME} Threads::Threads ${LIBRARY_DIR}/libCommonLib.a)
