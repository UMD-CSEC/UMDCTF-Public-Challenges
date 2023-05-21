cmake_minimum_required (VERSION 3.0)
cmake_policy(VERSION 3.0)

project(machokes-flex)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS ON)

IF(NOT CMAKE_BUILD_TYPE)
  SET(CMAKE_BUILD_TYPE Debug CACHE STRING "Choose the type of build (Debug or Release)" FORCE)
ENDIF(NOT CMAKE_BUILD_TYPE)

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_SOURCE_DIR}/cmake/modules/")

link_directories(${CMAKE_SOURCE_DIR}/lib)

find_package(GLM REQUIRED)
message(STATUS "GLM included at ${GLM_INCLUDE_DIR}")
find_package(GLFW3 REQUIRED)
message(STATUS "Found GLFW3 in ${GLFW3_INCLUDE_DIR}")
find_package(ASSIMP REQUIRED)
message(STATUS "Found ASSIMP in ${ASSIMP_INCLUDE_DIR}")

set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -Wall")
find_package(OpenGL REQUIRED)
add_definitions(${OPENGL_DEFINITIONS})
find_package(X11 REQUIRED)
set(LIBS ${GLFW3_LIBRARY} X11 Xrandr Xinerama Xi Xxf86vm Xcursor GL dl pthread freetype ${ASSIMP_LIBRARY})
set (CMAKE_CXX_LINK_EXECUTABLE "${CMAKE_CXX_LINK_EXECUTABLE} -ldl")

configure_file(configuration/root_directory.h.in configuration/root_directory.h)
include_directories(${CMAKE_BINARY_DIR}/configuration)

add_library(STB_IMAGE "src/lib/stb_image.cpp")
set(LIBS ${LIBS} STB_IMAGE)

add_library(GLAD "src/lib/glad.c")
set(LIBS ${LIBS} GLAD)

macro(makeLink src dest target)
  add_custom_command(TARGET ${target} POST_BUILD COMMAND ${CMAKE_COMMAND} -E create_symlink ${src} ${dest}  DEPENDS  ${dest} COMMENT "mklink ${src} -> ${dest}")
endmacro()

file(GLOB SOURCE
          "src/*.h"
          "src/*.cpp"
)
set(NAME "machokes-flex")
add_executable(${NAME} ${SOURCE})
target_link_libraries(${NAME} ${LIBS})
set_target_properties(${NAME} PROPERTIES RUNTIME_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}/bin")

include_directories(${CMAKE_SOURCE_DIR}/includes)
