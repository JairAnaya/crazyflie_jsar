;; Auto-generated. Do not edit!


(when (boundp 'crazyflie::UpdateParams)
  (if (not (find-package "CRAZYFLIE"))
    (make-package "CRAZYFLIE"))
  (shadow 'UpdateParams (find-package "CRAZYFLIE")))
(unless (find-package "CRAZYFLIE::UPDATEPARAMS")
  (make-package "CRAZYFLIE::UPDATEPARAMS"))
(unless (find-package "CRAZYFLIE::UPDATEPARAMSREQUEST")
  (make-package "CRAZYFLIE::UPDATEPARAMSREQUEST"))
(unless (find-package "CRAZYFLIE::UPDATEPARAMSRESPONSE")
  (make-package "CRAZYFLIE::UPDATEPARAMSRESPONSE"))

(in-package "ROS")





(defclass crazyflie::UpdateParamsRequest
  :super ros::object
  :slots (_params ))

(defmethod crazyflie::UpdateParamsRequest
  (:init
   (&key
    ((:params __params) (let (r) (dotimes (i 0) (push "" r)) r))
    )
   (send-super :init)
   (setq _params __params)
   self)
  (:params
   (&optional __params)
   (if __params (setq _params __params)) _params)
  (:serialization-length
   ()
   (+
    ;; string[] _params
    (apply #'+ (mapcar #'(lambda (x) (+ 4 (length x))) _params)) 4
    ))
  (:serialize
   (&optional strm)
   (let ((s (if strm strm
              (make-string-output-stream (send self :serialization-length)))))
     ;; string[] _params
     (write-long (length _params) s)
     (dolist (elem _params)
       (write-long (length elem) s) (princ elem s)
       )
     ;;
     (if (null strm) (get-output-stream-string s))))
  (:deserialize
   (buf &optional (ptr- 0))
   ;; string[] _params
   (let (n)
     (setq n (sys::peek buf ptr- :integer)) (incf ptr- 4)
     (setq _params (make-list n))
     (dotimes (i n)
     (let (n) (setq n (sys::peek buf ptr- :integer)) (incf ptr- 4) (setf (elt _params i) (subseq buf ptr- (+ ptr- n))) (incf ptr- n))
     ))
   ;;
   self)
  )

(defclass crazyflie::UpdateParamsResponse
  :super ros::object
  :slots ())

(defmethod crazyflie::UpdateParamsResponse
  (:init
   (&key
    )
   (send-super :init)
   self)
  (:serialization-length
   ()
   (+
    0
    ))
  (:serialize
   (&optional strm)
   (let ((s (if strm strm
              (make-string-output-stream (send self :serialization-length)))))
     ;;
     (if (null strm) (get-output-stream-string s))))
  (:deserialize
   (buf &optional (ptr- 0))
   ;;
   self)
  )

(defclass crazyflie::UpdateParams
  :super ros::object
  :slots ())

(setf (get crazyflie::UpdateParams :md5sum-) "279e0627eb574ffe8968384218434f5f")
(setf (get crazyflie::UpdateParams :datatype-) "crazyflie/UpdateParams")
(setf (get crazyflie::UpdateParams :request) crazyflie::UpdateParamsRequest)
(setf (get crazyflie::UpdateParams :response) crazyflie::UpdateParamsResponse)

(defmethod crazyflie::UpdateParamsRequest
  (:response () (instance crazyflie::UpdateParamsResponse :init)))

(setf (get crazyflie::UpdateParamsRequest :md5sum-) "279e0627eb574ffe8968384218434f5f")
(setf (get crazyflie::UpdateParamsRequest :datatype-) "crazyflie/UpdateParamsRequest")
(setf (get crazyflie::UpdateParamsRequest :definition-)
      "string[] params
---

")

(setf (get crazyflie::UpdateParamsResponse :md5sum-) "279e0627eb574ffe8968384218434f5f")
(setf (get crazyflie::UpdateParamsResponse :datatype-) "crazyflie/UpdateParamsResponse")
(setf (get crazyflie::UpdateParamsResponse :definition-)
      "string[] params
---

")



(provide :crazyflie/UpdateParams "279e0627eb574ffe8968384218434f5f")


