cmake_minimum_required(VERSION 3.12)

include(pico_sdk_import.cmake)

project(PicoTasksProject)

pico_sdk_init()

add_subdirectory(tasks/dumy_test)
# Add other tasks as you create them
# add_subdirectory(tasks/task2)
# add_subdirectory(tasks/task3)
