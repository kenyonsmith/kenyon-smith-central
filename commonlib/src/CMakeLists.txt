#################################################################################
# Prototype CMakeLists.txt file 
#
# Revision History
# May 17, 2019  K. Smith / Initial Implementation
#################################################################################

cmake_minimum_required(VERSION 3.1)
set(BINARY_NAME commonlib)

set(src_files 
  crc.cpp
  hexUtils.cpp
  logger.cpp
  version.cpp)

include_directories(${COMMON_LIB_HEADER_DIR})
add_library(${PROJECT_NAME} ${src_files})
target_include_directories(${PROJECT_NAME} BEFORE PUBLIC ${COMMON_LIB_HEADER_DIR})
target_link_libraries(CommonLib Threads::Threads)
