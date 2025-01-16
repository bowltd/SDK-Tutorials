# Install script for directory: /home/stuart/Projects/BOW/SDK-Tutorials/Tutorials/basics/Step_0_Dependencies/C++/Linux/opencv/modules/dnn

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "/home/stuart/Projects/BOW/SDK-Tutorials/Tutorials/basics/Step_0_Dependencies/install")
endif()
string(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
if(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  if(BUILD_TYPE)
    string(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  else()
    set(CMAKE_INSTALL_CONFIG_NAME "Release")
  endif()
  message(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
endif()

# Set the component getting installed.
if(NOT CMAKE_INSTALL_COMPONENT)
  if(COMPONENT)
    message(STATUS "Install component: \"${COMPONENT}\"")
    set(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  else()
    set(CMAKE_INSTALL_COMPONENT)
  endif()
endif()

# Install shared libraries without execute permission?
if(NOT DEFINED CMAKE_INSTALL_SO_NO_EXE)
  set(CMAKE_INSTALL_SO_NO_EXE "1")
endif()

# Is this installation the result of a crosscompile?
if(NOT DEFINED CMAKE_CROSSCOMPILING)
  set(CMAKE_CROSSCOMPILING "FALSE")
endif()

# Set default install directory permissions.
if(NOT DEFINED CMAKE_OBJDUMP)
  set(CMAKE_OBJDUMP "/usr/bin/objdump")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "libs" OR NOT CMAKE_INSTALL_COMPONENT)
  foreach(file
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libopencv_dnn.so.4.5.1"
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libopencv_dnn.so.4.5"
      )
    if(EXISTS "${file}" AND
       NOT IS_SYMLINK "${file}")
      file(RPATH_CHECK
           FILE "${file}"
           RPATH "/home/stuart/Projects/BOW/SDK-Tutorials/Tutorials/basics/Step_0_Dependencies/install/lib")
    endif()
  endforeach()
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE SHARED_LIBRARY OPTIONAL FILES
    "/home/stuart/Projects/BOW/SDK-Tutorials/Tutorials/basics/Step_0_Dependencies/C++/Linux/opencv/build/lib/libopencv_dnn.so.4.5.1"
    "/home/stuart/Projects/BOW/SDK-Tutorials/Tutorials/basics/Step_0_Dependencies/C++/Linux/opencv/build/lib/libopencv_dnn.so.4.5"
    )
  foreach(file
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libopencv_dnn.so.4.5.1"
      "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libopencv_dnn.so.4.5"
      )
    if(EXISTS "${file}" AND
       NOT IS_SYMLINK "${file}")
      file(RPATH_CHANGE
           FILE "${file}"
           OLD_RPATH "/home/stuart/Projects/BOW/SDK-Tutorials/Tutorials/basics/Step_0_Dependencies/C++/Linux/opencv/build/lib:"
           NEW_RPATH "/home/stuart/Projects/BOW/SDK-Tutorials/Tutorials/basics/Step_0_Dependencies/install/lib")
      if(CMAKE_INSTALL_DO_STRIP)
        execute_process(COMMAND "/usr/bin/strip" "${file}")
      endif()
    endif()
  endforeach()
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "dev" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE SHARED_LIBRARY FILES "/home/stuart/Projects/BOW/SDK-Tutorials/Tutorials/basics/Step_0_Dependencies/C++/Linux/opencv/build/lib/libopencv_dnn.so")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "dev" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/opencv4/opencv2" TYPE FILE OPTIONAL FILES "/home/stuart/Projects/BOW/SDK-Tutorials/Tutorials/basics/Step_0_Dependencies/C++/Linux/opencv/modules/dnn/include/opencv2/dnn.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "dev" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/opencv4/opencv2/dnn" TYPE FILE OPTIONAL FILES "/home/stuart/Projects/BOW/SDK-Tutorials/Tutorials/basics/Step_0_Dependencies/C++/Linux/opencv/modules/dnn/include/opencv2/dnn/all_layers.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "dev" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/opencv4/opencv2/dnn" TYPE FILE OPTIONAL FILES "/home/stuart/Projects/BOW/SDK-Tutorials/Tutorials/basics/Step_0_Dependencies/C++/Linux/opencv/modules/dnn/include/opencv2/dnn/dict.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "dev" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/opencv4/opencv2/dnn" TYPE FILE OPTIONAL FILES "/home/stuart/Projects/BOW/SDK-Tutorials/Tutorials/basics/Step_0_Dependencies/C++/Linux/opencv/modules/dnn/include/opencv2/dnn/dnn.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "dev" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/opencv4/opencv2/dnn" TYPE FILE OPTIONAL FILES "/home/stuart/Projects/BOW/SDK-Tutorials/Tutorials/basics/Step_0_Dependencies/C++/Linux/opencv/modules/dnn/include/opencv2/dnn/dnn.inl.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "dev" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/opencv4/opencv2/dnn" TYPE FILE OPTIONAL FILES "/home/stuart/Projects/BOW/SDK-Tutorials/Tutorials/basics/Step_0_Dependencies/C++/Linux/opencv/modules/dnn/include/opencv2/dnn/layer.details.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "dev" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/opencv4/opencv2/dnn" TYPE FILE OPTIONAL FILES "/home/stuart/Projects/BOW/SDK-Tutorials/Tutorials/basics/Step_0_Dependencies/C++/Linux/opencv/modules/dnn/include/opencv2/dnn/layer.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "dev" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/opencv4/opencv2/dnn" TYPE FILE OPTIONAL FILES "/home/stuart/Projects/BOW/SDK-Tutorials/Tutorials/basics/Step_0_Dependencies/C++/Linux/opencv/modules/dnn/include/opencv2/dnn/shape_utils.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "dev" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/opencv4/opencv2/dnn/utils" TYPE FILE OPTIONAL FILES "/home/stuart/Projects/BOW/SDK-Tutorials/Tutorials/basics/Step_0_Dependencies/C++/Linux/opencv/modules/dnn/include/opencv2/dnn/utils/inference_engine.hpp")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "dev" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/opencv4/opencv2/dnn" TYPE FILE OPTIONAL FILES "/home/stuart/Projects/BOW/SDK-Tutorials/Tutorials/basics/Step_0_Dependencies/C++/Linux/opencv/modules/dnn/include/opencv2/dnn/version.hpp")
endif()

