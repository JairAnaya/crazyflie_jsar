#!/usr/bin/env python3
import rospy
from geometry_msgs.msg import Twist, PoseStamped
from std_srvs.srv import Empty, EmptyResponse
from crazyflie.srv import *
from crazyflie.msg import *
import numpy as np
import time, sys
from threading import Thread

# Librerías de Bitcraze
import cflib
import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig

class CrazyflieROS:
    Disconnected = 0
    Connecting = 1
    Connected = 2

    def __init__(self, link_uri, tf_prefix, roll_trim, pitch_trim, enable_logging):
        self.link_uri = link_uri
        self.tf_prefix = tf_prefix
        self._cf = Crazyflie()

        self._cf.connected.add_callback(self._connected)
        self._cf.disconnected.add_callback(self._disconnected)
        self._cf.connection_failed.add_callback(self._connection_failed)

        self._subCmdFull = rospy.Subscriber(tf_prefix + "/cmd_full", Full, self._cmdsetpointChanged)
        self._subCmdExtPose = rospy.Subscriber(tf_prefix + "/external_pose", PoseStamped, self._poseMeasurementChanged)
        
        self._state = CrazyflieROS.Disconnected
        rospy.Service(tf_prefix + "/update_params", UpdateParams, self._update_params)
        rospy.Service(tf_prefix + "/emergency", Empty, self._emergency)

        self._isEmergency = False
        Thread(target=self._update).start()

    def _try_to_connect(self):
        rospy.loginfo("Connecting to %s" % self.link_uri)
        self._state = CrazyflieROS.Connecting
        self._cf.open_link(self.link_uri)

    def _connected(self, link_uri):
        rospy.loginfo("Connected to %s" % link_uri)
        self._state = CrazyflieROS.Connected

        # Se eliminó el bloque de señales log (signals_n) porque causaba error en el TOC
        # Si agregas variables personalizadas al firmware, puedes reactivarlo aquí.

        #p_toc = self._cf.param.toc.toc
        #for group in p_toc.keys():
        #    for name in p_toc[group].keys():
        #        ros_param = "/{}/{}/{}".format(self.tf_prefix, group, name)
        #        cf_param = "{}.{}".format(group, name)
        #        if rospy.has_param(ros_param):
        #            self._cf.param.set_value(cf_param, str(rospy.get_param(ros_param)))

    def _cmdsetpointChanged(self, msg):
        """
        Ajuste para recibir posición y velocidad (Feed-forward)
        """
        # Posición deseada
        x = msg.twist1.linear.x
        y = msg.twist1.linear.y
        z = msg.twist1.linear.z
        
        # Velocidad deseada (extraída de angular de twist1 según tu setpoint.py)
        #vx = msg.twist1.angular.x
        #vy = msg.twist1.angular.y
        #vz = msg.twist1.angular.z
        
        # Yaw
        yaw = msg.twist2.angular.x

        # Usamos send_full_state_setpoint para inyectar la velocidad al controlador
        # Esto reduce drásticamente el error de seguimiento en círculos
        self._cf.commander.send_position_setpoint(
            x, y, z,    # Aceleración (opcional, en 0 por ahora)
            yaw      # Yaw y YawRate
        )

    def _poseMeasurementChanged(self, msg):
        # Envío de posición externa al filtro de Kalman
        x, y, z = msg.pose.position.x, msg.pose.position.y, msg.pose.position.z
        qx, qy, qz, qw = msg.pose.orientation.x, msg.pose.orientation.y, msg.pose.orientation.z, msg.pose.orientation.w
        self._cf.extpos.send_extpose(x, y, z, qx, qy, qz, qw)

    def _update_params(self, req):
        rospy.loginfo("Actualizando parámetros en el firmware...")
        for param in req.params:
            ros_param = "/{}/{}".format(self.tf_prefix, param)
            cf_param = param.replace("/", ".")
            if rospy.has_param(ros_param):
                try:
                    # Intentamos setear el valor
                    self._cf.param.set_value(cf_param, str(rospy.get_param(ros_param)))
                    rospy.sleep(0.05) # Pequeña pausa entre parámetros para no saturar la radio
                except Exception as e:
                    rospy.logwarn(f"No se pudo setear {cf_param}: {str(e)}")
        return UpdateParamsResponse()

    def _emergency(self, req):
        rospy.logfatal("Emergency requested!")
        self._isEmergency = True
        self._cf.loc.send_emergency_stop()
        return EmptyResponse()

    def _connection_failed(self, link_uri, msg):
        rospy.logfatal("Connection failed: %s" % msg)
        self._state = CrazyflieROS.Disconnected

    def _disconnected(self, link_uri):
        self._state = CrazyflieROS.Disconnected

    def _update(self):
        while not rospy.is_shutdown():
            if self._isEmergency: break
            if self._state == CrazyflieROS.Disconnected:
                self._try_to_connect()
            rospy.sleep(0.1)
        self._cf.close_link()

def add_crazyflie(req):
    CrazyflieROS(req.uri, req.tf_prefix, req.roll_trim, req.pitch_trim, req.enable_logging)
    return AddCrazyflieResponse()

if __name__ == '__main__':
    rospy.init_node('crazyflie_server')
    cflib.crtp.init_drivers()
    rospy.Service("add_crazyflie", AddCrazyflie, add_crazyflie)
    rospy.spin()