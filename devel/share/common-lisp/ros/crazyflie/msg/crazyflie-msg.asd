
(cl:in-package :asdf)

(defsystem "crazyflie-msg"
  :depends-on (:roslisp-msg-protocol :roslisp-utils :geometry_msgs-msg
               :std_msgs-msg
)
  :components ((:file "_package")
    (:file "Full" :depends-on ("_package_Full"))
    (:file "_package_Full" :depends-on ("_package"))
    (:file "Position" :depends-on ("_package_Position"))
    (:file "_package_Position" :depends-on ("_package"))
  ))