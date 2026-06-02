; Auto-generated. Do not edit!


(cl:in-package crazyflie-msg)


;//! \htmlinclude Full.msg.html

(cl:defclass <Full> (roslisp-msg-protocol:ros-message)
  ((header
    :reader header
    :initarg :header
    :type std_msgs-msg:Header
    :initform (cl:make-instance 'std_msgs-msg:Header))
   (twist1
    :reader twist1
    :initarg :twist1
    :type geometry_msgs-msg:Twist
    :initform (cl:make-instance 'geometry_msgs-msg:Twist))
   (twist2
    :reader twist2
    :initarg :twist2
    :type geometry_msgs-msg:Twist
    :initform (cl:make-instance 'geometry_msgs-msg:Twist)))
)

(cl:defclass Full (<Full>)
  ())

(cl:defmethod cl:initialize-instance :after ((m <Full>) cl:&rest args)
  (cl:declare (cl:ignorable args))
  (cl:unless (cl:typep m 'Full)
    (roslisp-msg-protocol:msg-deprecation-warning "using old message class name crazyflie-msg:<Full> is deprecated: use crazyflie-msg:Full instead.")))

(cl:ensure-generic-function 'header-val :lambda-list '(m))
(cl:defmethod header-val ((m <Full>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader crazyflie-msg:header-val is deprecated.  Use crazyflie-msg:header instead.")
  (header m))

(cl:ensure-generic-function 'twist1-val :lambda-list '(m))
(cl:defmethod twist1-val ((m <Full>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader crazyflie-msg:twist1-val is deprecated.  Use crazyflie-msg:twist1 instead.")
  (twist1 m))

(cl:ensure-generic-function 'twist2-val :lambda-list '(m))
(cl:defmethod twist2-val ((m <Full>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader crazyflie-msg:twist2-val is deprecated.  Use crazyflie-msg:twist2 instead.")
  (twist2 m))
(cl:defmethod roslisp-msg-protocol:serialize ((msg <Full>) ostream)
  "Serializes a message object of type '<Full>"
  (roslisp-msg-protocol:serialize (cl:slot-value msg 'header) ostream)
  (roslisp-msg-protocol:serialize (cl:slot-value msg 'twist1) ostream)
  (roslisp-msg-protocol:serialize (cl:slot-value msg 'twist2) ostream)
)
(cl:defmethod roslisp-msg-protocol:deserialize ((msg <Full>) istream)
  "Deserializes a message object of type '<Full>"
  (roslisp-msg-protocol:deserialize (cl:slot-value msg 'header) istream)
  (roslisp-msg-protocol:deserialize (cl:slot-value msg 'twist1) istream)
  (roslisp-msg-protocol:deserialize (cl:slot-value msg 'twist2) istream)
  msg
)
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql '<Full>)))
  "Returns string type for a message object of type '<Full>"
  "crazyflie/Full")
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql 'Full)))
  "Returns string type for a message object of type 'Full"
  "crazyflie/Full")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql '<Full>)))
  "Returns md5sum for a message object of type '<Full>"
  "c6afbdb945f02d23afa7f796e1f4d470")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql 'Full)))
  "Returns md5sum for a message object of type 'Full"
  "c6afbdb945f02d23afa7f796e1f4d470")
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql '<Full>)))
  "Returns full string definition for message of type '<Full>"
  (cl:format cl:nil "Header header~%geometry_msgs/Twist twist1~%geometry_msgs/Twist twist2~%~%================================================================================~%MSG: std_msgs/Header~%# Standard metadata for higher-level stamped data types.~%# This is generally used to communicate timestamped data ~%# in a particular coordinate frame.~%# ~%# sequence ID: consecutively increasing ID ~%uint32 seq~%#Two-integer timestamp that is expressed as:~%# * stamp.sec: seconds (stamp_secs) since epoch (in Python the variable is called 'secs')~%# * stamp.nsec: nanoseconds since stamp_secs (in Python the variable is called 'nsecs')~%# time-handling sugar is provided by the client library~%time stamp~%#Frame this data is associated with~%string frame_id~%~%================================================================================~%MSG: geometry_msgs/Twist~%# This expresses velocity in free space broken into its linear and angular parts.~%Vector3  linear~%Vector3  angular~%~%================================================================================~%MSG: geometry_msgs/Vector3~%# This represents a vector in free space. ~%# It is only meant to represent a direction. Therefore, it does not~%# make sense to apply a translation to it (e.g., when applying a ~%# generic rigid transformation to a Vector3, tf2 will only apply the~%# rotation). If you want your data to be translatable too, use the~%# geometry_msgs/Point message instead.~%~%float64 x~%float64 y~%float64 z~%~%"))
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql 'Full)))
  "Returns full string definition for message of type 'Full"
  (cl:format cl:nil "Header header~%geometry_msgs/Twist twist1~%geometry_msgs/Twist twist2~%~%================================================================================~%MSG: std_msgs/Header~%# Standard metadata for higher-level stamped data types.~%# This is generally used to communicate timestamped data ~%# in a particular coordinate frame.~%# ~%# sequence ID: consecutively increasing ID ~%uint32 seq~%#Two-integer timestamp that is expressed as:~%# * stamp.sec: seconds (stamp_secs) since epoch (in Python the variable is called 'secs')~%# * stamp.nsec: nanoseconds since stamp_secs (in Python the variable is called 'nsecs')~%# time-handling sugar is provided by the client library~%time stamp~%#Frame this data is associated with~%string frame_id~%~%================================================================================~%MSG: geometry_msgs/Twist~%# This expresses velocity in free space broken into its linear and angular parts.~%Vector3  linear~%Vector3  angular~%~%================================================================================~%MSG: geometry_msgs/Vector3~%# This represents a vector in free space. ~%# It is only meant to represent a direction. Therefore, it does not~%# make sense to apply a translation to it (e.g., when applying a ~%# generic rigid transformation to a Vector3, tf2 will only apply the~%# rotation). If you want your data to be translatable too, use the~%# geometry_msgs/Point message instead.~%~%float64 x~%float64 y~%float64 z~%~%"))
(cl:defmethod roslisp-msg-protocol:serialization-length ((msg <Full>))
  (cl:+ 0
     (roslisp-msg-protocol:serialization-length (cl:slot-value msg 'header))
     (roslisp-msg-protocol:serialization-length (cl:slot-value msg 'twist1))
     (roslisp-msg-protocol:serialization-length (cl:slot-value msg 'twist2))
))
(cl:defmethod roslisp-msg-protocol:ros-message-to-list ((msg <Full>))
  "Converts a ROS message object to a list"
  (cl:list 'Full
    (cl:cons ':header (header msg))
    (cl:cons ':twist1 (twist1 msg))
    (cl:cons ':twist2 (twist2 msg))
))
