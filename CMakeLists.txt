cmake_minimum_required(VERSION 2.8.3)
project(robot_joy_control)
find_package(catkin REQUIRED)
catkin_package()

install(PROGRAMS
  scripts/joy_head_nextage.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

install(DIRECTORY launch/
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/launch
)
