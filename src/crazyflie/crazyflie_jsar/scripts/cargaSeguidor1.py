#!/usr/bin/env python3
import rospy
from crazyflie.msg import Full

class Seguidor:
    def __init__(self):
        rospy.init_node('seguidor_node', anonymous=True)
        self.ci_x = rospy.get_param("~xi", 0.0)
        self.ci_y = rospy.get_param("~yi", 0.0)
        self.ci_z = rospy.get_param("~zi", 0.2828)
        self.start_time = None
        self.pub = rospy.Publisher('cmd_full', Full, queue_size=1)
        rospy.Subscriber("/control_carga/posicion_deseada_formacion", Full, self.leader_cb)

    def leader_cb(self, msg):
        if self.start_time is None: self.start_time = rospy.Time.now()
        t = (rospy.Time.now() - self.start_time).to_sec()
        frac = min(t / 5.0, 1.0)
        target = Full()
        target.twist1.linear.x = msg.twist1.linear.x + (self.ci_x * frac)
        target.twist1.linear.y = msg.twist1.linear.y + (self.ci_y * frac)
        target.twist1.linear.z = msg.twist1.linear.z + (self.ci_z * frac)
        self.pub.publish(target)

if __name__ == '__main__':
    Seguidor()
    rospy.spin()