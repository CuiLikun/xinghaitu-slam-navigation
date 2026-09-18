# Copyright(c) 2019 livoxtech limited. Original driver: ../LICENSE.txt.
# Restored build entry; explicit SDK discovery and optional messages-only build.
cmake_minimum_required(VERSION 3.0.2)
include(cmake/version.cmake)
project(livox_ros_driver VERSION ${LIVOX_ROS_DRIVER_VERSION} LANGUAGES CXX)
find_package(catkin REQUIRED COMPONENTS roscpp rospy sensor_msgs std_msgs message_generation rosbag pcl_ros)
add_message_files(FILES CustomPoint.msg CustomMsg.msg)
generate_messages(DEPENDENCIES std_msgs)
catkin_package(CATKIN_DEPENDS roscpp rospy sensor_msgs std_msgs message_runtime rosbag pcl_ros)
option(LIVOX_BUILD_DRIVER "Build Livox hardware/recording node (requires Livox-SDK v1)" ON)
if(LIVOX_BUILD_DRIVER)
  find_package(Boost REQUIRED COMPONENTS system thread chrono)
  find_package(PCL REQUIRED)
  find_package(PkgConfig REQUIRED)
  pkg_check_modules(APR REQUIRED apr-1)
  find_path(LIVOX_SDK_INCLUDE_DIR livox_sdk.h PATH_SUFFIXES livox_sdk)
  find_library(LIVOX_SDK_LIBRARY NAMES livox_sdk_static)
  if(NOT LIVOX_SDK_INCLUDE_DIR OR NOT LIVOX_SDK_LIBRARY)
    message(FATAL_ERROR "Install Livox-SDK v1 first, or use -DLIVOX_BUILD_DRIVER=OFF for bag replay/external drivers. See docs/installation.md.")
  endif()
  set(CMAKE_CXX_STANDARD 11)
  set(CMAKE_CXX_STANDARD_REQUIRED ON)
  add_definitions(${PCL_DEFINITIONS})
  add_executable(livox_ros_driver_node
    livox_ros_driver/lvx_file.cpp livox_ros_driver/ldq.cpp
    livox_ros_driver/lds.cpp livox_ros_driver/lds_lvx.cpp
    livox_ros_driver/lds_lidar.cpp livox_ros_driver/lds_hub.cpp
    livox_ros_driver/lddc.cpp livox_ros_driver/livox_ros_driver.cpp
    timesync/timesync.cpp timesync/user_uart/user_uart.cpp
    common/comm/comm_protocol.cpp common/comm/sdk_protocol.cpp common/comm/gps_protocol.cpp)
  add_dependencies(livox_ros_driver_node ${${PROJECT_NAME}_EXPORTED_TARGETS} ${catkin_EXPORTED_TARGETS})
  target_include_directories(livox_ros_driver_node PRIVATE
    ${catkin_INCLUDE_DIRS} ${PCL_INCLUDE_DIRS} ${Boost_INCLUDE_DIRS}
    ${APR_INCLUDE_DIRS} ${LIVOX_SDK_INCLUDE_DIR}
    common common/rapidjson common/rapidxml common/comm timesync timesync/user_uart livox_ros_driver)
  target_link_libraries(livox_ros_driver_node ${LIVOX_SDK_LIBRARY} ${Boost_LIBRARIES}
    ${catkin_LIBRARIES} ${PCL_LIBRARIES} ${APR_LIBRARIES})
  install(TARGETS livox_ros_driver_node RUNTIME DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION})
endif()
install(DIRECTORY launch config DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION})
