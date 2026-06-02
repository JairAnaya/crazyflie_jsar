;; Auto-generated. Do not edit!


(when (boundp 'crazyflie::Full)
  (if (not (find-package "CRAZYFLIE"))
    (make-package "CRAZYFLIE"))
  (shadow 'Full (find-package "CRAZYFLIE")))
(unless (find-package "CRAZYFLIE::FULL")
  (make-package "CRAZYFLIE::FULL"))

(in-package "ROS")
;;//! \htmlinclude Full.msg.html
(if (not (find-package "GEOMETRY_MSGS"))
  (ros::roseus-add-msgs "geometry_msgs"))
(if (not (find-package "STD_MSGS"))
  (ros::roseus-add-msgs "std_msgs"))


(defclass crazyflie::Full
  :super ros::object
  :slots (_header _twist1 _twist2 ))

(defmethod crazyflie::Full
  (:init
   (&key
    ((:header __header) (instance std_msgs::Header :init))
    ((:twist1 __twist1) (instance geometry_msgs::Twist :init))
    ((:twist2 __twist2) (instance geometry_msgs::Twist :init))
    )
   (send-super :init)
   (setq _header __header)
   (setq _twist1 __twist1)
   (setq _twist2 __twist2)
   self)
  (:header
   (&rest __header)
   (if (keywordp (car __header))
       (send* _header __header)
     (progn
       (if __header (setq _header (car __header)))
       _header)))
  (:twist1
   (&rest __twist1)
   (if (keywordp (car __twist1))
       (send* _twist1 __twist1)
     (progn
       (if __twist1 (setq _twist1 (car __twist1)))
       _twist1)))
  (:twist2
   (&rest __twist2)
   (if (keywordp (car __twist2))
       (send* _twist2 __twist2)
     (progn
       (if __twist2 (setq _twist2 (car __twist2)))
       _twist2)))
  (:serialization-length
   ()
   (+
    ;; std_msgs/Header _header
    (send _header :serialization-length)
    ;; geometry_msgs/Twist _twist1
    (send _twist1 :serialization-length)
    ;; geometry_msgs/Twist _twist2
    (send _twist2 :serialization-length)
    ))
  (:serialize
   (&optional strm)
   (let ((s (if strm strm
              (make-string-output-stream (send self :serialization-length)))))
     ;; std_msgs/Header _header
       (send _header :serialize s)
     ;; geometry_msgs/Twist _twist1
       (send _twist1 :serialize s)
     ;; geometry_msgs/Twist _twist2
       (send _twist2 :serialize s)
     ;;
     (if (null strm) (get-output-stream-string s))))
  (:deserialize
   (buf &optional (ptr- 0))
   ;; std_msgs/Header _header
     (send _header :deserialize buf ptr-) (incf ptr- (send _header :serialization-length))
   ;; geometry_msgs/Twist _twist1
     (send _twist1 :deserialize buf ptr-) (incf ptr- (send _twist1 :serialization-length))
   ;; geometry_msgs/Twist _twist2
     (send _twist2 :deserialize buf ptr-) (incf ptr- (send _twist2 :serialization-length))
   ;;
   self)
  )

(setf (get crazyflie::Full :md5sum-) "c6afbdb945f02d23afa7f796e1f4d470")
(setf (get crazyflie::Full :datatype-) "crazyflie/Full")
(setf (get crazyflie::Full :definition-)
      "Header header
geometry_msgs/Twist twist1
geometry_msgs/Twist twist2

================================================================================
MSG: std_msgs/Header
# Standard metadata for higher-level stamped data types.
# This is generally used to communicate timestamped data 
# in a particular coordinate frame.
# 
# sequence ID: consecutively increasing ID 
uint32 seq
#Two-integer timestamp that is expressed as:
# * stamp.sec: seconds (stamp_secs) since epoch (in Python the variable is called 'secs')
# * stamp.nsec: nanoseconds since stamp_secs (in Python the variable is called 'nsecs')
# time-handling sugar is provided by the client library
time stamp
#Frame this data is associated with
string frame_id

================================================================================
MSG: geometry_msgs/Twist
# This expresses velocity in free space broken into its linear and angular parts.
Vector3  linear
Vector3  angular

================================================================================
MSG: geometry_msgs/Vector3
# This represents a vector in free space. 
# It is only meant to represent a direction. Therefore, it does not
# make sense to apply a translation to it (e.g., when applying a 
# generic rigid transformation to a Vector3, tf2 will only apply the
# rotation). If you want your data to be translatable too, use the
# geometry_msgs/Point message instead.

float64 x
float64 y
float64 z
")



(provide :crazyflie/Full "c6afbdb945f02d23afa7f796e1f4d470")


