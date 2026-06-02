;; Auto-generated. Do not edit!


(when (boundp 'crazyflie::AddCrazyflie)
  (if (not (find-package "CRAZYFLIE"))
    (make-package "CRAZYFLIE"))
  (shadow 'AddCrazyflie (find-package "CRAZYFLIE")))
(unless (find-package "CRAZYFLIE::ADDCRAZYFLIE")
  (make-package "CRAZYFLIE::ADDCRAZYFLIE"))
(unless (find-package "CRAZYFLIE::ADDCRAZYFLIEREQUEST")
  (make-package "CRAZYFLIE::ADDCRAZYFLIEREQUEST"))
(unless (find-package "CRAZYFLIE::ADDCRAZYFLIERESPONSE")
  (make-package "CRAZYFLIE::ADDCRAZYFLIERESPONSE"))

(in-package "ROS")





(defclass crazyflie::AddCrazyflieRequest
  :super ros::object
  :slots (_uri _tf_prefix _roll_trim _pitch_trim _enable_logging ))

(defmethod crazyflie::AddCrazyflieRequest
  (:init
   (&key
    ((:uri __uri) "")
    ((:tf_prefix __tf_prefix) "")
    ((:roll_trim __roll_trim) 0.0)
    ((:pitch_trim __pitch_trim) 0.0)
    ((:enable_logging __enable_logging) nil)
    )
   (send-super :init)
   (setq _uri (string __uri))
   (setq _tf_prefix (string __tf_prefix))
   (setq _roll_trim (float __roll_trim))
   (setq _pitch_trim (float __pitch_trim))
   (setq _enable_logging __enable_logging)
   self)
  (:uri
   (&optional __uri)
   (if __uri (setq _uri __uri)) _uri)
  (:tf_prefix
   (&optional __tf_prefix)
   (if __tf_prefix (setq _tf_prefix __tf_prefix)) _tf_prefix)
  (:roll_trim
   (&optional __roll_trim)
   (if __roll_trim (setq _roll_trim __roll_trim)) _roll_trim)
  (:pitch_trim
   (&optional __pitch_trim)
   (if __pitch_trim (setq _pitch_trim __pitch_trim)) _pitch_trim)
  (:enable_logging
   (&optional (__enable_logging :null))
   (if (not (eq __enable_logging :null)) (setq _enable_logging __enable_logging)) _enable_logging)
  (:serialization-length
   ()
   (+
    ;; string _uri
    4 (length _uri)
    ;; string _tf_prefix
    4 (length _tf_prefix)
    ;; float32 _roll_trim
    4
    ;; float32 _pitch_trim
    4
    ;; bool _enable_logging
    1
    ))
  (:serialize
   (&optional strm)
   (let ((s (if strm strm
              (make-string-output-stream (send self :serialization-length)))))
     ;; string _uri
       (write-long (length _uri) s) (princ _uri s)
     ;; string _tf_prefix
       (write-long (length _tf_prefix) s) (princ _tf_prefix s)
     ;; float32 _roll_trim
       (sys::poke _roll_trim (send s :buffer) (send s :count) :float) (incf (stream-count s) 4)
     ;; float32 _pitch_trim
       (sys::poke _pitch_trim (send s :buffer) (send s :count) :float) (incf (stream-count s) 4)
     ;; bool _enable_logging
       (if _enable_logging (write-byte -1 s) (write-byte 0 s))
     ;;
     (if (null strm) (get-output-stream-string s))))
  (:deserialize
   (buf &optional (ptr- 0))
   ;; string _uri
     (let (n) (setq n (sys::peek buf ptr- :integer)) (incf ptr- 4) (setq _uri (subseq buf ptr- (+ ptr- n))) (incf ptr- n))
   ;; string _tf_prefix
     (let (n) (setq n (sys::peek buf ptr- :integer)) (incf ptr- 4) (setq _tf_prefix (subseq buf ptr- (+ ptr- n))) (incf ptr- n))
   ;; float32 _roll_trim
     (setq _roll_trim (sys::peek buf ptr- :float)) (incf ptr- 4)
   ;; float32 _pitch_trim
     (setq _pitch_trim (sys::peek buf ptr- :float)) (incf ptr- 4)
   ;; bool _enable_logging
     (setq _enable_logging (not (= 0 (sys::peek buf ptr- :char)))) (incf ptr- 1)
   ;;
   self)
  )

(defclass crazyflie::AddCrazyflieResponse
  :super ros::object
  :slots ())

(defmethod crazyflie::AddCrazyflieResponse
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

(defclass crazyflie::AddCrazyflie
  :super ros::object
  :slots ())

(setf (get crazyflie::AddCrazyflie :md5sum-) "5b59a3ab8b313e5f8ea146f7129a4bf5")
(setf (get crazyflie::AddCrazyflie :datatype-) "crazyflie/AddCrazyflie")
(setf (get crazyflie::AddCrazyflie :request) crazyflie::AddCrazyflieRequest)
(setf (get crazyflie::AddCrazyflie :response) crazyflie::AddCrazyflieResponse)

(defmethod crazyflie::AddCrazyflieRequest
  (:response () (instance crazyflie::AddCrazyflieResponse :init)))

(setf (get crazyflie::AddCrazyflieRequest :md5sum-) "5b59a3ab8b313e5f8ea146f7129a4bf5")
(setf (get crazyflie::AddCrazyflieRequest :datatype-) "crazyflie/AddCrazyflieRequest")
(setf (get crazyflie::AddCrazyflieRequest :definition-)
      "string uri
string tf_prefix
float32 roll_trim
float32 pitch_trim
bool enable_logging
---

")

(setf (get crazyflie::AddCrazyflieResponse :md5sum-) "5b59a3ab8b313e5f8ea146f7129a4bf5")
(setf (get crazyflie::AddCrazyflieResponse :datatype-) "crazyflie/AddCrazyflieResponse")
(setf (get crazyflie::AddCrazyflieResponse :definition-)
      "string uri
string tf_prefix
float32 roll_trim
float32 pitch_trim
bool enable_logging
---

")



(provide :crazyflie/AddCrazyflie "5b59a3ab8b313e5f8ea146f7129a4bf5")


