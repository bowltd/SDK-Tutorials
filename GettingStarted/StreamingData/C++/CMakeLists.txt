# Minimum CMake required
cmake_minimum_required(VERSION 3.5...3.27)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

project(StreamingData)

# Ensure BOW_API environment variable is set
if(BOW_API)
    set(BOW_API_FINAL ${BOW_API})
    message(STATUS "Using BOW_API from CMake variable: ${BOW_API_FINAL}")
elseif(DEFINED ENV{BOW_API})
    set(BOW_API_FINAL $ENV{BOW_API})
    message(STATUS "Using BOW_API from environment variable: ${BOW_API_FINAL}")
else()
    message(FATAL_ERROR "BOW_API is not set. Please set it as a CMake variable or as an environment variable.")
endif()

# Add BOW_SDK location to CMAKE_PREFIX_PATH
list(APPEND CMAKE_PREFIX_PATH "${BOW_API_FINAL}")
message(STATUS "CMAKE_PREFIX_PATH: ${CMAKE_PREFIX_PATH}")

# Find the BOW_SDK package
find_package(BOW_SDK REQUIRED)
find_package(OpenCV REQUIRED )

# Collect application source files
file(GLOB_RECURSE APP_SRC "${CMAKE_SOURCE_DIR}/src/*.cpp")

# Include directories
include_directories(
    ${CMAKE_SOURCE_DIR}/include
    ${BOW_SDK_INCLUDE_DIRS}
    ${OpenCV_INCLUDE_DIRS}
)

if(MSVC)
    foreach(flag_var CMAKE_CXX_FLAGS CMAKE_CXX_FLAGS_DEBUG CMAKE_CXX_FLAGS_RELEASE
            CMAKE_CXX_FLAGS_MINSIZEREL CMAKE_CXX_FLAGS_RELWITHDEBINFO)
        # Replace dynamic release `/MD` with debug `/MDd` for Debug builds
        if(CMAKE_BUILD_TYPE STREQUAL "Debug")
            string(REGEX REPLACE "/MD" "/MDd" ${flag_var} "${${flag_var}}")
        else()
            # Ensure release configurations use `/MD`
            string(REGEX REPLACE "/MDd" "/MD" ${flag_var} "${${flag_var}}")
        endif()
    endforeach()
endif()


# Define the application executable
add_executable(${PROJECT_NAME} ${APP_SRC} ${BOW_SDK_SRC})

if(CMAKE_CXX_COMPILER_ID STREQUAL "MSVC")
    target_link_options(${PROJECT_NAME} PRIVATE "/IGNORE:4098") # Ignore the runtime mismatch warning
endif()

# Link SDK libraries
target_link_libraries(${PROJECT_NAME} PRIVATE ${BOW_SDK_LIBRARIES} ${OpenCV_LIBS})

# Ensure libanimus_client.dll is copied post-build
copy_animus_dll(${PROJECT_NAME})

# Install the application executable and the DLL
install(TARGETS ${PROJECT_NAME} DESTINATION bin)
install(FILES ${BOW_SDK_DLL_PATH} DESTINATION bin)
