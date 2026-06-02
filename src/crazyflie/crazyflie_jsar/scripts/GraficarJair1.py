#!/usr/bin/env python3
import rospy
import os
from geometry_msgs.msg import Twist, PoseStamped
from crazyflie.msg import Full
from std_msgs.msg import Bool
from scipy import io

import tf.transformations as t


class DataRecorder:
    def __init__(self):
        self.Quad1 = []
        self.is_saving_data = False
        rospy.init_node('guardar_datos')

        self.ros_param1 = rospy.get_param('~n1', 0)
        
        self.suffix1 = ''
        if self.ros_param1 == 1:
            self.suffix1 = 'PID'
        elif self.ros_param1 == 2:
            self.suffix1 = 'Mellinger'
        elif self.ros_param1 == 3:
            self.suffix1 = 'INDI'
        elif self.ros_param1 == 4:
            self.suffix1 = 'Brescancinni'
        elif self.ros_param1 == 5:
            self.suffix1 = 'Lee'
        elif self.ros_param1 == 6:
            self.suffix1 = 'JSAR'

        self.base_name_1 = "Agente1_" + self.suffix1

        self.contador = 0

        rospy.Subscriber('/crazyflie1/sc', Twist, self.CMD_Signals1)
        rospy.Subscriber('/vrpn_client_node/crazyflie1/pose', PoseStamped, self.VRPNPOSE1)
        rospy.Subscriber('/start', Twist, self.Start)

    def CMD_Signals1(self, msg):
        self.tau_phi1 = msg.linear.x
        self.tau_theta1 = msg.linear.y
        self.tau_psi1 = msg.linear.z
        self.u1 = msg.linear.z

    def VRPNPOSE1(self, msg):
        q = msg.pose.orientation
        rpy = t.euler_from_quaternion([q.x, q.y, q.z, q.w])
        self.psi1 = rpy[2]
        self.x1 = msg.pose.position.x
        self.y1 = msg.pose.position.y
        self.z1 = msg.pose.position.z


    def Start(self, msg):
        angular_x = msg.angular.x
        if angular_x == 10 and not self.is_saving_data:
            self.is_saving_data = True
            rospy.loginfo("Comenzando a guardar los datos...")
        elif angular_x == 0 and self.is_saving_data:
            self.is_saving_data = False
            rospy.loginfo("Dejando de guardar los datos...")

        if self.is_saving_data:
            self.Quad1.append([self.x1, self.y1, self.z1, self.psi1, self.u1, self.tau_phi1, self.tau_theta1, self.tau_psi1])


    def save_data(self):
        home_dir = os.path.expanduser("~/ExperimentosJSAR")

        if not os.path.exists(home_dir):
            os.makedirs(home_dir)
        mat_path_quad1 = os.path.join(home_dir, self.base_name_1 + ".mat")

        data_dict_quad1 = {'Quad1_data': self.Quad1}
        io.savemat(mat_path_quad1, data_dict_quad1)


if __name__ == '__main__':
    recorder = DataRecorder()
    rospy.on_shutdown(recorder.save_data)
    rospy.spin()
