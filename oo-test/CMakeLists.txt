cmake_minimum_required(VERSION 3.10)
project(oo_test LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)


include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)
add_library(ootest
    src/entity.cpp
    src/component.cpp
    src/renderer.cpp
    src/resource.cpp
    src/entity_manager.cpp
)


add_executable(ootest_app src/main.cpp)
target_link_libraries(ootest_app PRIVATE ootest)
