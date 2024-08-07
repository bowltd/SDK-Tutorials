cmake_minimum_required(VERSION 3.10)
project(bow_tutorial_1)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_PREFIX_PATH ${CMAKE_CURRENT_SOURCE_DIR}/../../Step_0_Dependencies/install/lib/cmake/opencv4/)
# Depending on the platform, different libraries will be needed
if(WIN32)
    set(BOW_INCLUDE_ROOT /usr/local/include/bow_client)
    set(BOW_LIB_DIR /usr/local/lib/bow/)

    set(CMAKE_CXX_STANDARD_LIBRARIES "${CMAKE_CXX_STANDARD_LIBRARIES} -lm -pthread -lws2_32 -lbcrypt -lole32 -lstrmiids -lmfuuid -lmfplat -lmf")
    file(GLOB ABSL "${BOW_LIB_DIR}/lib_win/libabsl*")
    set(BOW_LIBS
            "${BOW_LIB_DIR}/libbow_client.dll"
            "${BOW_LIB_DIR}/animus_client.dll"
            "${BOW_LIB_DIR}/libprotobuf.dll"
            "${BOW_LIB_DIR}/libwinpthread-1.dll"
            ${ABSL}
    )
elseif(UNIX AND NOT APPLE)
    set(BOW_INCLUDE_ROOT /usr/local/include/bow_client)
    set(BOW_LIB_DIR /usr/local/lib/bow/)

    set(CMAKE_CXX_STANDARD_LIBRARIES "${CMAKE_CXX_STANDARD_LIBRARIES} -lm -pthread")
    file(GLOB ABSL "${BOW_LIB_DIR}/lib*")
    set(BOW_LIBS
            "${BOW_LIB_DIR}/libbow_client.so"
            "${BOW_LIB_DIR}/libanimus_client.so"
            "${BOW_LIB_DIR}/libprotobuf.so"
            ${ABSL}
    )
elseif(APPLE)
    set(BOW_INCLUDE_ROOT /usr/local/include/bow_client)
    set(BOW_LIB_DIR /usr/local/lib/bow/)

    set(CMAKE_CXX_STANDARD_LIBRARIES "${CMAKE_CXX_STANDARD_LIBRARIES} -lm -pthread")
    file(GLOB ABSL "${BOW_LIB_DIR}/lib*")
    set(BOW_LIBS
            "${BOW_LIB_DIR}/libbow_client.so"
            "${BOW_LIB_DIR}/libanimus_client.so"
            "${BOW_LIB_DIR}/libprotobuf.so"
            ${ABSL}
    )
endif()

find_package(OpenCV REQUIRED)

# Where to find CMake modules and OpenCV
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_SOURCE_DIR}/cmake/")
set(BOW_PROTO_DIR ${BOW_INCLUDE_ROOT})
set(PROTO_HEADERS
        "${BOW_PROTO_DIR}/bow_client.pb.h"
        "${BOW_PROTO_DIR}/bow_client_sdk.pb.h"
        "${BOW_PROTO_DIR}/bow_common.pb.h"
        "${BOW_PROTO_DIR}/bow_data.pb.h"
        "${BOW_PROTO_DIR}/bow_data_audio.pb.h"
        "${BOW_PROTO_DIR}/bow_data_common.pb.h"
        "${BOW_PROTO_DIR}/bow_data_exteroception.pb.h"
        "${BOW_PROTO_DIR}/bow_data_interoception.pb.h"
        "${BOW_PROTO_DIR}/bow_data_motor.pb.h"
        "${BOW_PROTO_DIR}/bow_data_octree.pb.h"
        "${BOW_PROTO_DIR}/bow_data_tactile.pb.h"
        "${BOW_PROTO_DIR}/bow_data_vision.pb.h"
        "${BOW_PROTO_DIR}/bow_structs.pb.h"
        "${BOW_PROTO_DIR}/bow_robot.pb.h"
)
file(GLOB BOW_HEADERS ${CMAKE_CURRENT_SOURCE_DIR}/include/*)

set(OpenCV_LIBS opencv_core opencv_imgproc opencv_highgui opencv_imgcodecs)

# add libs you need
include_directories(${OpenCV_INCLUDE_DIRS} ${CMAKE_CURRENT_SOURCE_DIR}/include)

add_executable(bow_tutorial_1
        main.cpp
        ${PROTO_HEADERS}
        ${BOW_HEADERS}
        ${BOW_LIBS}
)
target_include_directories(bow_tutorial_1 PUBLIC ${OpenCV_INCLUDE_DIRS} ${CMAKE_CURRENT_SOURCE_DIR}/include ${BOW_PROTO_DIR})
target_link_libraries(bow_tutorial_1 PUBLIC ${BOW_LIBS} ${OpenCV_LIBS})