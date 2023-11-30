cmake_minimum_required(VERSION 3.10)
project(bow_client)

set(CMAKE_CXX_STANDARD 17)


# Depending on the platform, different libraries will be needed
if(WIN32)
    message(STATUS "Compiling for Windows")
    set(CMAKE_CXX_STANDARD_LIBRARIES "${CMAKE_CXX_STANDARD_LIBRARIES} -lm -pthread -lws2_32 -lbcrypt -lole32 -lstrmiids -lmfuuid -lmfplat -lmf")
    set(BOW_INCLUDE_DIR "C:/Program Files (x86)/BOW/include")
    set(BOW_LIB_DIR "C:/Program Files (x86)/BOW/lib")

    file(GLOB ABSL "${BOW_LIB_DIR}/libabsl*")
    set(BOW_LIBS
            "${BOW_LIB_DIR}/libbow_client.dll"
            "${BOW_LIB_DIR}/animus_client.dll"
            "${BOW_LIB_DIR}/libprotobuf.dll"
            "${BOW_LIB_DIR}/libwinpthread-1.dll"
            ${ABSL}
    )

elseif(UNIX AND NOT APPLE)
    message(STATUS "Compiling for Linux")
    set(CMAKE_CXX_STANDARD_LIBRARIES "${CMAKE_CXX_STANDARD_LIBRARIES} -lm -pthread")
    set(BOW_INCLUDE_DIR /usr/local/include/bow_client)
    set(BOW_LIB_DIR /usr/local/lib/bow)

    file(GLOB ABSL "${BOW_LIB_DIR}/libabsl*")
    set(BOW_LIBS
            "${BOW_LIB_DIR}/libbow_client.so"
            "${BOW_LIB_DIR}/libanimus_client.so"
            "${BOW_LIB_DIR}/libprotobuf.so"
            ${ABSL}
    )

elseif(APPLE)
    message(STATUS "Compiling for Apple")
    set(CMAKE_CXX_STANDARD_LIBRARIES "${CMAKE_CXX_STANDARD_LIBRARIES} -lm -pthread")
    set(BOW_INCLUDE_DIR /usr/local/include)
    set(BOW_LIB_DIR /usr/local/lib/bow)

    file(GLOB ABSL "${BOW_LIB_DIR}/libabsl*")
    set(BOW_LIBS
            "${BOW_LIB_DIR}/libbow_client.so"
            "${BOW_LIB_DIR}/libanimus_client.so"
            "${BOW_LIB_DIR}/libprotobuf.so"
            ${ABSL}
    )
endif()

# find the opencv package
find_package(OpenCV REQUIRED)

# SFML
set(SFML_STATIC_LIBRARIES TRUE)
find_package(SFML COMPONENTS window system)
set(CMAKE_BUILD_TYPE Debug)

add_executable(bow_keyboard_control main.cpp)
target_include_directories(bow_keyboard_control PUBLIC ${BOW_INCLUDE_DIR})
target_link_libraries(bow_keyboard_control PUBLIC ${BOW_LIBS} ${OpenCV_LIBS} sfml-window sfml-system)