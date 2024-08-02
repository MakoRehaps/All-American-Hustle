cmake_minimum_required(VERSION 3.0)
project(AllAmericanHustle)

# Specify the C++ standard
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# Add the source files
file(GLOB SOURCES "src/*.cpp")

# Add the executable
add_executable(AllAmericanHustle ${SOURCES})

# TODO: Add any necessary libraries or dependencies
