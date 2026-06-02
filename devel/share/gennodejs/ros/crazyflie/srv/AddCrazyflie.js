// Auto-generated. Do not edit!

// (in-package crazyflie.srv)


"use strict";

const _serializer = _ros_msg_utils.Serialize;
const _arraySerializer = _serializer.Array;
const _deserializer = _ros_msg_utils.Deserialize;
const _arrayDeserializer = _deserializer.Array;
const _finder = _ros_msg_utils.Find;
const _getByteLength = _ros_msg_utils.getByteLength;

//-----------------------------------------------------------


//-----------------------------------------------------------

class AddCrazyflieRequest {
  constructor(initObj={}) {
    if (initObj === null) {
      // initObj === null is a special case for deserialization where we don't initialize fields
      this.uri = null;
      this.tf_prefix = null;
      this.roll_trim = null;
      this.pitch_trim = null;
      this.enable_logging = null;
    }
    else {
      if (initObj.hasOwnProperty('uri')) {
        this.uri = initObj.uri
      }
      else {
        this.uri = '';
      }
      if (initObj.hasOwnProperty('tf_prefix')) {
        this.tf_prefix = initObj.tf_prefix
      }
      else {
        this.tf_prefix = '';
      }
      if (initObj.hasOwnProperty('roll_trim')) {
        this.roll_trim = initObj.roll_trim
      }
      else {
        this.roll_trim = 0.0;
      }
      if (initObj.hasOwnProperty('pitch_trim')) {
        this.pitch_trim = initObj.pitch_trim
      }
      else {
        this.pitch_trim = 0.0;
      }
      if (initObj.hasOwnProperty('enable_logging')) {
        this.enable_logging = initObj.enable_logging
      }
      else {
        this.enable_logging = false;
      }
    }
  }

  static serialize(obj, buffer, bufferOffset) {
    // Serializes a message object of type AddCrazyflieRequest
    // Serialize message field [uri]
    bufferOffset = _serializer.string(obj.uri, buffer, bufferOffset);
    // Serialize message field [tf_prefix]
    bufferOffset = _serializer.string(obj.tf_prefix, buffer, bufferOffset);
    // Serialize message field [roll_trim]
    bufferOffset = _serializer.float32(obj.roll_trim, buffer, bufferOffset);
    // Serialize message field [pitch_trim]
    bufferOffset = _serializer.float32(obj.pitch_trim, buffer, bufferOffset);
    // Serialize message field [enable_logging]
    bufferOffset = _serializer.bool(obj.enable_logging, buffer, bufferOffset);
    return bufferOffset;
  }

  static deserialize(buffer, bufferOffset=[0]) {
    //deserializes a message object of type AddCrazyflieRequest
    let len;
    let data = new AddCrazyflieRequest(null);
    // Deserialize message field [uri]
    data.uri = _deserializer.string(buffer, bufferOffset);
    // Deserialize message field [tf_prefix]
    data.tf_prefix = _deserializer.string(buffer, bufferOffset);
    // Deserialize message field [roll_trim]
    data.roll_trim = _deserializer.float32(buffer, bufferOffset);
    // Deserialize message field [pitch_trim]
    data.pitch_trim = _deserializer.float32(buffer, bufferOffset);
    // Deserialize message field [enable_logging]
    data.enable_logging = _deserializer.bool(buffer, bufferOffset);
    return data;
  }

  static getMessageSize(object) {
    let length = 0;
    length += _getByteLength(object.uri);
    length += _getByteLength(object.tf_prefix);
    return length + 17;
  }

  static datatype() {
    // Returns string type for a service object
    return 'crazyflie/AddCrazyflieRequest';
  }

  static md5sum() {
    //Returns md5sum for a message object
    return '5b59a3ab8b313e5f8ea146f7129a4bf5';
  }

  static messageDefinition() {
    // Returns full string definition for message
    return `
    string uri
    string tf_prefix
    float32 roll_trim
    float32 pitch_trim
    bool enable_logging
    
    `;
  }

  static Resolve(msg) {
    // deep-construct a valid message object instance of whatever was passed in
    if (typeof msg !== 'object' || msg === null) {
      msg = {};
    }
    const resolved = new AddCrazyflieRequest(null);
    if (msg.uri !== undefined) {
      resolved.uri = msg.uri;
    }
    else {
      resolved.uri = ''
    }

    if (msg.tf_prefix !== undefined) {
      resolved.tf_prefix = msg.tf_prefix;
    }
    else {
      resolved.tf_prefix = ''
    }

    if (msg.roll_trim !== undefined) {
      resolved.roll_trim = msg.roll_trim;
    }
    else {
      resolved.roll_trim = 0.0
    }

    if (msg.pitch_trim !== undefined) {
      resolved.pitch_trim = msg.pitch_trim;
    }
    else {
      resolved.pitch_trim = 0.0
    }

    if (msg.enable_logging !== undefined) {
      resolved.enable_logging = msg.enable_logging;
    }
    else {
      resolved.enable_logging = false
    }

    return resolved;
    }
};

class AddCrazyflieResponse {
  constructor(initObj={}) {
    if (initObj === null) {
      // initObj === null is a special case for deserialization where we don't initialize fields
    }
    else {
    }
  }

  static serialize(obj, buffer, bufferOffset) {
    // Serializes a message object of type AddCrazyflieResponse
    return bufferOffset;
  }

  static deserialize(buffer, bufferOffset=[0]) {
    //deserializes a message object of type AddCrazyflieResponse
    let len;
    let data = new AddCrazyflieResponse(null);
    return data;
  }

  static getMessageSize(object) {
    return 0;
  }

  static datatype() {
    // Returns string type for a service object
    return 'crazyflie/AddCrazyflieResponse';
  }

  static md5sum() {
    //Returns md5sum for a message object
    return 'd41d8cd98f00b204e9800998ecf8427e';
  }

  static messageDefinition() {
    // Returns full string definition for message
    return `
    
    
    `;
  }

  static Resolve(msg) {
    // deep-construct a valid message object instance of whatever was passed in
    if (typeof msg !== 'object' || msg === null) {
      msg = {};
    }
    const resolved = new AddCrazyflieResponse(null);
    return resolved;
    }
};

module.exports = {
  Request: AddCrazyflieRequest,
  Response: AddCrazyflieResponse,
  md5sum() { return '5b59a3ab8b313e5f8ea146f7129a4bf5'; },
  datatype() { return 'crazyflie/AddCrazyflie'; }
};
