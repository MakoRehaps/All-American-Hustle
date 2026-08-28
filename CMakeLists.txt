cmake_minimum_required(VERSION 3.15)
project(AllAmericanHustle NONE)

find_package(Python3 COMPONENTS Interpreter REQUIRED)

add_custom_target(prepare ALL
    COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/prepare_game.py"
    WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
    COMMENT "Validating All-American Hustle and enabling RPG level scripts"
    VERBATIM
)

install(PROGRAMS "${CMAKE_SOURCE_DIR}/All American Hustle.exe" DESTINATION .)
install(FILES
    "${CMAKE_SOURCE_DIR}/SDL.dll"
    "${CMAKE_SOURCE_DIR}/alleg42.dll"
    "${CMAKE_SOURCE_DIR}/freetype6.dll"
    "${CMAKE_SOURCE_DIR}/libpng13.dll"
    "${CMAKE_SOURCE_DIR}/libpng3.dll"
    DESTINATION .
)
install(DIRECTORY "${CMAKE_SOURCE_DIR}/data" DESTINATION .)
install(DIRECTORY "${CMAKE_SOURCE_DIR}/rpg_mechanics" DESTINATION .
        PATTERN "__pycache__" EXCLUDE
        PATTERN "*.pyc" EXCLUDE)
install(DIRECTORY "${CMAKE_SOURCE_DIR}/tools" DESTINATION .
        PATTERN "__pycache__" EXCLUDE
        PATTERN "*.pyc" EXCLUDE)
install(FILES "${CMAKE_SOURCE_DIR}/run_game.bat" DESTINATION .)
