# generated from genmsg/cmake/pkg-genmsg.cmake.em

message(STATUS "crazyflie: 2 messages, 2 services")

set(MSG_I_FLAGS "-Icrazyflie:/home/lrm/crazyflie_jsar/src/crazyflie/crazyflie/msg;-Istd_msgs:/opt/ros/noetic/share/std_msgs/cmake/../msg;-Igeometry_msgs:/opt/ros/noetic/share/geometry_msgs/cmake/../msg")

# Find all generators
find_package(gencpp REQUIRED)
find_package(geneus REQUIRED)
find_package(genlisp REQUIRED)
find_package(gennodejs REQUIRED)
find_package(genpy REQUIRED)

add_custom_target(crazyflie_generate_messages ALL)

# verify that message/service dependencies have not changed since configure



get_filename_component(_filename "/home/lrm/crazyflie_jsar/src/crazyflie/crazyflie/msg/Full.msg" NAME_WE)
add_custom_target(_crazyflie_generate_messages_check_deps_${_filename}
  COMMAND ${CATKIN_ENV} ${PYTHON_EXECUTABLE} ${GENMSG_CHECK_DEPS_SCRIPT} "crazyflie" "/home/lrm/crazyflie_jsar/src/crazyflie/crazyflie/msg/Full.msg" "geometry_msgs/Vector3:std_msgs/Header:geometry_msgs/Twist"
)

get_filename_component(_filename "/home/lrm/crazyflie_jsar/src/crazyflie/crazyflie/msg/Position.msg" NAME_WE)
add_custom_target(_crazyflie_generate_messages_check_deps_${_filename}
  COMMAND ${CATKIN_ENV} ${PYTHON_EXECUTABLE} ${GENMSG_CHECK_DEPS_SCRIPT} "crazyflie" "/home/lrm/crazyflie_jsar/src/crazyflie/crazyflie/msg/Position.msg" "std_msgs/Header"
)

get_filename_component(_filename "/home/lrm/crazyflie_jsar/src/crazyflie/crazyflie/srv/AddCrazyflie.srv" NAME_WE)
add_custom_target(_crazyflie_generate_messages_check_deps_${_filename}
  COMMAND ${CATKIN_ENV} ${PYTHON_EXECUTABLE} ${GENMSG_CHECK_DEPS_SCRIPT} "crazyflie" "/home/lrm/crazyflie_jsar/src/crazyflie/crazyflie/srv/AddCrazyflie.srv" ""
)

get_filename_component(_filename "/home/lrm/crazyflie_jsar/src/crazyflie/crazyflie/srv/UpdateParams.srv" NAME_WE)
add_custom_target(_crazyflie_generate_messages_check_deps_${_filename}
  COMMAND ${CATKIN_ENV} ${PYTHON_EXECUTABLE} ${GENMSG_CHECK_DEPS_SCRIPT} "crazyflie" "/home/lrm/crazyflie_jsar/src/crazyflie/crazyflie/srv/UpdateParams.srv" ""
)

#
#  langs = gencpp;geneus;genlisp;gennodejs;genpy
#

### Section generating for lang: gencpp
### Generating Messages
_generate_msg_cpp(crazyflie
  "/home/lrm/crazyflie_jsar/src/crazyflie/crazyflie/msg/Full.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Vector3.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Twist.msg"
  ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/crazyflie
)
_generate_msg_cpp(crazyflie
  "/home/lrm/crazyflie_jsar/src/crazyflie/crazyflie/msg/Position.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg"
  ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/crazyflie
)

### Generating Services
_generate_srv_cpp(crazyflie
  "/home/lrm/crazyflie_jsar/src/crazyflie/crazyflie/srv/AddCrazyflie.srv"
  "${MSG_I_FLAGS}"
  ""
  ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/crazyflie
)
_generate_srv_cpp(crazyflie
  "/home/lrm/crazyflie_jsar/src/crazyflie/crazyflie/srv/UpdateParams.srv"
  "${MSG_I_FLAGS}"
  ""
  ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/crazyflie
)

### Generating Module File
_generate_module_cpp(crazyflie
  ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/crazyflie
  "${ALL_GEN_OUTPUT_FILES_cpp}"
)

add_custom_target(crazyflie_generate_messages_cpp
  DEPENDS ${ALL_GEN_OUTPUT_FILES_cpp}
)
add_dependencies(crazyflie_generate_messages crazyflie_generate_messages_cpp)

# add dependencies to all check dependencies targets
get_filename_component(_filename "/home/lrm/crazyflie_jsar/src/crazyflie/crazyflie/msg/Full.msg" NAME_WE)
add_dependencies(crazyflie_generate_messages_cpp _crazyflie_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/lrm/crazyflie_jsar/src/crazyflie/crazyflie/msg/Position.msg" NAME_WE)
add_dependencies(crazyflie_generate_messages_cpp _crazyflie_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/lrm/crazyflie_jsar/src/crazyflie/crazyflie/srv/AddCrazyflie.srv" NAME_WE)
add_dependencies(crazyflie_generate_messages_cpp _crazyflie_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/lrm/crazyflie_jsar/src/crazyflie/crazyflie/srv/UpdateParams.srv" NAME_WE)
add_dependencies(crazyflie_generate_messages_cpp _crazyflie_generate_messages_check_deps_${_filename})

# target for backward compatibility
add_custom_target(crazyflie_gencpp)
add_dependencies(crazyflie_gencpp crazyflie_generate_messages_cpp)

# register target for catkin_package(EXPORTED_TARGETS)
list(APPEND ${PROJECT_NAME}_EXPORTED_TARGETS crazyflie_generate_messages_cpp)

### Section generating for lang: geneus
### Generating Messages
_generate_msg_eus(crazyflie
  "/home/lrm/crazyflie_jsar/src/crazyflie/crazyflie/msg/Full.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Vector3.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Twist.msg"
  ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/crazyflie
)
_generate_msg_eus(crazyflie
  "/home/lrm/crazyflie_jsar/src/crazyflie/crazyflie/msg/Position.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg"
  ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/crazyflie
)

### Generating Services
_generate_srv_eus(crazyflie
  "/home/lrm/crazyflie_jsar/src/crazyflie/crazyflie/srv/AddCrazyflie.srv"
  "${MSG_I_FLAGS}"
  ""
  ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/crazyflie
)
_generate_srv_eus(crazyflie
  "/home/lrm/crazyflie_jsar/src/crazyflie/crazyflie/srv/UpdateParams.srv"
  "${MSG_I_FLAGS}"
  ""
  ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/crazyflie
)

### Generating Module File
_generate_module_eus(crazyflie
  ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/crazyflie
  "${ALL_GEN_OUTPUT_FILES_eus}"
)

add_custom_target(crazyflie_generate_messages_eus
  DEPENDS ${ALL_GEN_OUTPUT_FILES_eus}
)
add_dependencies(crazyflie_generate_messages crazyflie_generate_messages_eus)

# add dependencies to all check dependencies targets
get_filename_component(_filename "/home/lrm/crazyflie_jsar/src/crazyflie/crazyflie/msg/Full.msg" NAME_WE)
add_dependencies(crazyflie_generate_messages_eus _crazyflie_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/lrm/crazyflie_jsar/src/crazyflie/crazyflie/msg/Position.msg" NAME_WE)
add_dependencies(crazyflie_generate_messages_eus _crazyflie_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/lrm/crazyflie_jsar/src/crazyflie/crazyflie/srv/AddCrazyflie.srv" NAME_WE)
add_dependencies(crazyflie_generate_messages_eus _crazyflie_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/lrm/crazyflie_jsar/src/crazyflie/crazyflie/srv/UpdateParams.srv" NAME_WE)
add_dependencies(crazyflie_generate_messages_eus _crazyflie_generate_messages_check_deps_${_filename})

# target for backward compatibility
add_custom_target(crazyflie_geneus)
add_dependencies(crazyflie_geneus crazyflie_generate_messages_eus)

# register target for catkin_package(EXPORTED_TARGETS)
list(APPEND ${PROJECT_NAME}_EXPORTED_TARGETS crazyflie_generate_messages_eus)

### Section generating for lang: genlisp
### Generating Messages
_generate_msg_lisp(crazyflie
  "/home/lrm/crazyflie_jsar/src/crazyflie/crazyflie/msg/Full.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Vector3.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Twist.msg"
  ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/crazyflie
)
_generate_msg_lisp(crazyflie
  "/home/lrm/crazyflie_jsar/src/crazyflie/crazyflie/msg/Position.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg"
  ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/crazyflie
)

### Generating Services
_generate_srv_lisp(crazyflie
  "/home/lrm/crazyflie_jsar/src/crazyflie/crazyflie/srv/AddCrazyflie.srv"
  "${MSG_I_FLAGS}"
  ""
  ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/crazyflie
)
_generate_srv_lisp(crazyflie
  "/home/lrm/crazyflie_jsar/src/crazyflie/crazyflie/srv/UpdateParams.srv"
  "${MSG_I_FLAGS}"
  ""
  ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/crazyflie
)

### Generating Module File
_generate_module_lisp(crazyflie
  ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/crazyflie
  "${ALL_GEN_OUTPUT_FILES_lisp}"
)

add_custom_target(crazyflie_generate_messages_lisp
  DEPENDS ${ALL_GEN_OUTPUT_FILES_lisp}
)
add_dependencies(crazyflie_generate_messages crazyflie_generate_messages_lisp)

# add dependencies to all check dependencies targets
get_filename_component(_filename "/home/lrm/crazyflie_jsar/src/crazyflie/crazyflie/msg/Full.msg" NAME_WE)
add_dependencies(crazyflie_generate_messages_lisp _crazyflie_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/lrm/crazyflie_jsar/src/crazyflie/crazyflie/msg/Position.msg" NAME_WE)
add_dependencies(crazyflie_generate_messages_lisp _crazyflie_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/lrm/crazyflie_jsar/src/crazyflie/crazyflie/srv/AddCrazyflie.srv" NAME_WE)
add_dependencies(crazyflie_generate_messages_lisp _crazyflie_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/lrm/crazyflie_jsar/src/crazyflie/crazyflie/srv/UpdateParams.srv" NAME_WE)
add_dependencies(crazyflie_generate_messages_lisp _crazyflie_generate_messages_check_deps_${_filename})

# target for backward compatibility
add_custom_target(crazyflie_genlisp)
add_dependencies(crazyflie_genlisp crazyflie_generate_messages_lisp)

# register target for catkin_package(EXPORTED_TARGETS)
list(APPEND ${PROJECT_NAME}_EXPORTED_TARGETS crazyflie_generate_messages_lisp)

### Section generating for lang: gennodejs
### Generating Messages
_generate_msg_nodejs(crazyflie
  "/home/lrm/crazyflie_jsar/src/crazyflie/crazyflie/msg/Full.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Vector3.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Twist.msg"
  ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/crazyflie
)
_generate_msg_nodejs(crazyflie
  "/home/lrm/crazyflie_jsar/src/crazyflie/crazyflie/msg/Position.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg"
  ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/crazyflie
)

### Generating Services
_generate_srv_nodejs(crazyflie
  "/home/lrm/crazyflie_jsar/src/crazyflie/crazyflie/srv/AddCrazyflie.srv"
  "${MSG_I_FLAGS}"
  ""
  ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/crazyflie
)
_generate_srv_nodejs(crazyflie
  "/home/lrm/crazyflie_jsar/src/crazyflie/crazyflie/srv/UpdateParams.srv"
  "${MSG_I_FLAGS}"
  ""
  ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/crazyflie
)

### Generating Module File
_generate_module_nodejs(crazyflie
  ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/crazyflie
  "${ALL_GEN_OUTPUT_FILES_nodejs}"
)

add_custom_target(crazyflie_generate_messages_nodejs
  DEPENDS ${ALL_GEN_OUTPUT_FILES_nodejs}
)
add_dependencies(crazyflie_generate_messages crazyflie_generate_messages_nodejs)

# add dependencies to all check dependencies targets
get_filename_component(_filename "/home/lrm/crazyflie_jsar/src/crazyflie/crazyflie/msg/Full.msg" NAME_WE)
add_dependencies(crazyflie_generate_messages_nodejs _crazyflie_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/lrm/crazyflie_jsar/src/crazyflie/crazyflie/msg/Position.msg" NAME_WE)
add_dependencies(crazyflie_generate_messages_nodejs _crazyflie_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/lrm/crazyflie_jsar/src/crazyflie/crazyflie/srv/AddCrazyflie.srv" NAME_WE)
add_dependencies(crazyflie_generate_messages_nodejs _crazyflie_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/lrm/crazyflie_jsar/src/crazyflie/crazyflie/srv/UpdateParams.srv" NAME_WE)
add_dependencies(crazyflie_generate_messages_nodejs _crazyflie_generate_messages_check_deps_${_filename})

# target for backward compatibility
add_custom_target(crazyflie_gennodejs)
add_dependencies(crazyflie_gennodejs crazyflie_generate_messages_nodejs)

# register target for catkin_package(EXPORTED_TARGETS)
list(APPEND ${PROJECT_NAME}_EXPORTED_TARGETS crazyflie_generate_messages_nodejs)

### Section generating for lang: genpy
### Generating Messages
_generate_msg_py(crazyflie
  "/home/lrm/crazyflie_jsar/src/crazyflie/crazyflie/msg/Full.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Vector3.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Twist.msg"
  ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/crazyflie
)
_generate_msg_py(crazyflie
  "/home/lrm/crazyflie_jsar/src/crazyflie/crazyflie/msg/Position.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg"
  ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/crazyflie
)

### Generating Services
_generate_srv_py(crazyflie
  "/home/lrm/crazyflie_jsar/src/crazyflie/crazyflie/srv/AddCrazyflie.srv"
  "${MSG_I_FLAGS}"
  ""
  ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/crazyflie
)
_generate_srv_py(crazyflie
  "/home/lrm/crazyflie_jsar/src/crazyflie/crazyflie/srv/UpdateParams.srv"
  "${MSG_I_FLAGS}"
  ""
  ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/crazyflie
)

### Generating Module File
_generate_module_py(crazyflie
  ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/crazyflie
  "${ALL_GEN_OUTPUT_FILES_py}"
)

add_custom_target(crazyflie_generate_messages_py
  DEPENDS ${ALL_GEN_OUTPUT_FILES_py}
)
add_dependencies(crazyflie_generate_messages crazyflie_generate_messages_py)

# add dependencies to all check dependencies targets
get_filename_component(_filename "/home/lrm/crazyflie_jsar/src/crazyflie/crazyflie/msg/Full.msg" NAME_WE)
add_dependencies(crazyflie_generate_messages_py _crazyflie_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/lrm/crazyflie_jsar/src/crazyflie/crazyflie/msg/Position.msg" NAME_WE)
add_dependencies(crazyflie_generate_messages_py _crazyflie_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/lrm/crazyflie_jsar/src/crazyflie/crazyflie/srv/AddCrazyflie.srv" NAME_WE)
add_dependencies(crazyflie_generate_messages_py _crazyflie_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/lrm/crazyflie_jsar/src/crazyflie/crazyflie/srv/UpdateParams.srv" NAME_WE)
add_dependencies(crazyflie_generate_messages_py _crazyflie_generate_messages_check_deps_${_filename})

# target for backward compatibility
add_custom_target(crazyflie_genpy)
add_dependencies(crazyflie_genpy crazyflie_generate_messages_py)

# register target for catkin_package(EXPORTED_TARGETS)
list(APPEND ${PROJECT_NAME}_EXPORTED_TARGETS crazyflie_generate_messages_py)



if(gencpp_INSTALL_DIR AND EXISTS ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/crazyflie)
  # install generated code
  install(
    DIRECTORY ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/crazyflie
    DESTINATION ${gencpp_INSTALL_DIR}
  )
endif()
if(TARGET std_msgs_generate_messages_cpp)
  add_dependencies(crazyflie_generate_messages_cpp std_msgs_generate_messages_cpp)
endif()
if(TARGET geometry_msgs_generate_messages_cpp)
  add_dependencies(crazyflie_generate_messages_cpp geometry_msgs_generate_messages_cpp)
endif()

if(geneus_INSTALL_DIR AND EXISTS ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/crazyflie)
  # install generated code
  install(
    DIRECTORY ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/crazyflie
    DESTINATION ${geneus_INSTALL_DIR}
  )
endif()
if(TARGET std_msgs_generate_messages_eus)
  add_dependencies(crazyflie_generate_messages_eus std_msgs_generate_messages_eus)
endif()
if(TARGET geometry_msgs_generate_messages_eus)
  add_dependencies(crazyflie_generate_messages_eus geometry_msgs_generate_messages_eus)
endif()

if(genlisp_INSTALL_DIR AND EXISTS ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/crazyflie)
  # install generated code
  install(
    DIRECTORY ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/crazyflie
    DESTINATION ${genlisp_INSTALL_DIR}
  )
endif()
if(TARGET std_msgs_generate_messages_lisp)
  add_dependencies(crazyflie_generate_messages_lisp std_msgs_generate_messages_lisp)
endif()
if(TARGET geometry_msgs_generate_messages_lisp)
  add_dependencies(crazyflie_generate_messages_lisp geometry_msgs_generate_messages_lisp)
endif()

if(gennodejs_INSTALL_DIR AND EXISTS ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/crazyflie)
  # install generated code
  install(
    DIRECTORY ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/crazyflie
    DESTINATION ${gennodejs_INSTALL_DIR}
  )
endif()
if(TARGET std_msgs_generate_messages_nodejs)
  add_dependencies(crazyflie_generate_messages_nodejs std_msgs_generate_messages_nodejs)
endif()
if(TARGET geometry_msgs_generate_messages_nodejs)
  add_dependencies(crazyflie_generate_messages_nodejs geometry_msgs_generate_messages_nodejs)
endif()

if(genpy_INSTALL_DIR AND EXISTS ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/crazyflie)
  install(CODE "execute_process(COMMAND \"/usr/bin/python3\" -m compileall \"${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/crazyflie\")")
  # install generated code
  install(
    DIRECTORY ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/crazyflie
    DESTINATION ${genpy_INSTALL_DIR}
  )
endif()
if(TARGET std_msgs_generate_messages_py)
  add_dependencies(crazyflie_generate_messages_py std_msgs_generate_messages_py)
endif()
if(TARGET geometry_msgs_generate_messages_py)
  add_dependencies(crazyflie_generate_messages_py geometry_msgs_generate_messages_py)
endif()
