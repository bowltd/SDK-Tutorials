# CMake generated Testfile for 
# Source directory: /home/stuart/Projects/BOW/SDK-Tutorials/Tutorials/basics/Step_0_Dependencies/C++/Linux/opencv/modules/flann
# Build directory: /home/stuart/Projects/BOW/SDK-Tutorials/Tutorials/basics/Step_0_Dependencies/C++/Linux/opencv/build/modules/flann
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
add_test(opencv_test_flann "/home/stuart/Projects/BOW/SDK-Tutorials/Tutorials/basics/Step_0_Dependencies/C++/Linux/opencv/build/bin/opencv_test_flann" "--gtest_output=xml:opencv_test_flann.xml")
set_tests_properties(opencv_test_flann PROPERTIES  LABELS "Main;opencv_flann;Accuracy" WORKING_DIRECTORY "/home/stuart/Projects/BOW/SDK-Tutorials/Tutorials/basics/Step_0_Dependencies/C++/Linux/opencv/build/test-reports/accuracy" _BACKTRACE_TRIPLES "/home/stuart/Projects/BOW/SDK-Tutorials/Tutorials/basics/Step_0_Dependencies/C++/Linux/opencv/cmake/OpenCVUtils.cmake;1677;add_test;/home/stuart/Projects/BOW/SDK-Tutorials/Tutorials/basics/Step_0_Dependencies/C++/Linux/opencv/cmake/OpenCVModule.cmake;1311;ocv_add_test_from_target;/home/stuart/Projects/BOW/SDK-Tutorials/Tutorials/basics/Step_0_Dependencies/C++/Linux/opencv/cmake/OpenCVModule.cmake;1075;ocv_add_accuracy_tests;/home/stuart/Projects/BOW/SDK-Tutorials/Tutorials/basics/Step_0_Dependencies/C++/Linux/opencv/modules/flann/CMakeLists.txt;2;ocv_define_module;/home/stuart/Projects/BOW/SDK-Tutorials/Tutorials/basics/Step_0_Dependencies/C++/Linux/opencv/modules/flann/CMakeLists.txt;0;")
