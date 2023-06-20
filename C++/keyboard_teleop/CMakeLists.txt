cmake_minimum_required(VERSION 3.10)
project(bow_client)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_SOURCE_DIR}/cmake/")
set(CMAKE_CXX_STANDARD_LIBRARIES "${CMAKE_CXX_STANDARD_LIBRARIES} -lm -pthread")

# find the opencv package
find_package(OpenCV REQUIRED)

# find the QT5 package
find_package(Qt5 COMPONENTS Widgets REQUIRED)

set(BOW_INCLUDE_ROOT /usr/local/include/)
set(BOW_LIB_DIR /usr/local/lib/bow/)

# add libs you need
include_directories(${OpenCV_INCLUDE_DIRS} ${BOW_INCLUDE_ROOT}/bow_client ${BOW_INCLUDE_ROOT}/bow_protobuf )
set(OpenCV_LIBS opencv_core opencv_imgproc opencv_highgui opencv_imgcodecs)
set(BOW_LIBS ${BOW_LIB_DIR}/libprotobuf.a ${BOW_LIB_DIR}/libbow_client.so   ${BOW_LIB_DIR}/libanimus_client.so)

add_executable(bow_keyboard_control main.cpp)
target_include_directories(bow_keyboard_control PUBLIC)
target_link_libraries(bow_keyboard_control PUBLIC ${BOW_LIBS} ${OpenCV_LIBS} Qt5::Widgets)