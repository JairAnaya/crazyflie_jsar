// Auto-generated. Do not edit!

// (in-package crazyflie.msg)


"use strict";

const _serializer = _ros_msg_utils.Serialize;
const _arraySerializer = _serializer.Array;
const _deserializer = _ros_msg_utils.Deserialize;
const _arrayDeserializer = _deserializer.Array;
const _finder = _ros_msg_utils.Find;
const _getByteLength = _ros_msg_utils.getByteLength;
let geometry_msgs = _finder('geometry_msgs');
let std_msgs = _finder('std_msgs');

//-----------------------------------------------------------

class Full {
  constructor(initObj={}) {
    if (initObj === null) {
      // initObj === null is a special case for deserialization where we don't initialize fields
      this.header = null;
      this.twist1 = null;
      this.twist2 = null;
    }
    else {
      if (initObj.hasOwnProperty('header')) {
        this.header = initObj.header
      }
      else {
        this.header = new std_msgs.msg.Header();
      }
      if (initObj.hasOwnProperty('twist1')) {
        this.twist1 = initObj.twist1
      }
      else {
        this.twist1 = new geometry_msgs.msg.Twist();
      }
      if (initObj.hasOwnProperty('twist2')) {
        this.twist2 = initObj.twist2
      }
      else {
        this.twist2 = new geometry_msgs.msg.Twist();
      }
    }
  }

  static serialize(obj, buffer, bufferOffset) {
    // Serializes a message object of type Full
    // Serialize message field [header]
    bufferOffset = std_msgs.msg.Header.serialize(obj.header, buffer, bufferOffset);
    // Serialize message field [twist1]
    bufferOffset = geometry_msgs.msg.Twist.serialize(obj.twist1, buffer, bufferOffset);
    // Serialize message field [twist2]
    bufferOffset = geometry_msgs.msg.Twist.serialize(obj.twist2, buffer, bufferOffset);
    return bufferOffset;
  }

  static deserialize(buffer, bufferOffset=[0]) {
    //deserializes a message object of type Full
    let len;
    let data = new Full(null);
    // Deserialize message field [header]
    data.header = std_msgs.msg.Header.deserialize(buffer, bufferOffset);
    // Deserialize message field [twist1]
    data.twist1 = geometry_msgs.msg.Twist.deserialize(buffer, bufferOffset);
    // Deserialize message field [twist2]
    data.twist2 = geometry_msgs.msg.Twist.deserialize(buffer, bufferOffset);
    return data;
  }

  static getMessageSize(object) {
    let length = 0;
    length += std_msgs.msg.Header.getMessageSize(object.header);
    return length + 96;
  }

  static datatype() {
    // Returns string type for a message object
    return 'crazyflie/Full';
  }

  static md5sum() {
    //Returns md5sum for a message object
    return 'c6afbdb945f02d23afa7f796e1f4d470';
  }

  static messageDefinition() {
    // Returns full string definition for message
    return `
    Header header
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
    `;
  }

  static Resolve(msg) {
    // deep-construct a valid message object instance of whatever was passed in
    if (typeof msg !== 'object' || msg === null) {
      msg = {};
    }
    const resolved = new Full(null);
    if (msg.header !== undefined) {
      resolved.header = std_msgs.msg.Header.Resolve(msg.header)
    }
    else {
      resolved.header = new std_msgs.msg.Header()
    }

    if (msg.twist1 !== undefined) {
      resolved.twist1 = geometry_msgs.msg.Twist.Resolve(msg.twist1)
    }
    else {
      resolved.twist1 = new geometry_msgs.msg.Twist()
    }

    if (msg.twist2 !== undefined) {
      resolved.twist2 = geometry_msgs.msg.Twist.Resolve(msg.twist2)
    }
    else {
      resolved.twist2 = new geometry_msgs.msg.Twist()
    }

    return resolved;
    }
};

module.exports = Full;
