#!/usr/bin/env python3
import rospy
from geometry_msgs.msg import PoseStamped

class PublishExternalPosition:
    def __init__(self):
        rospy.init_node('publish_external_position_vrpn', anonymous=True)
        ns = rospy.get_namespace()
        self.topic = rospy.get_param("~topic", f"/vrpn_client_node{ns}pose")
        self.pub = rospy.Publisher("external_pose", PoseStamped, queue_size=1)
        self.msg = PoseStamped()

        rospy.loginfo(f"Publicando posición externa desde: {self.topic}")
        rospy.Subscriber(self.topic, PoseStamped, self.on_new_transform)

    def on_new_transform(self, pose):
        self.msg.header = pose.header
        self.msg.pose = pose.pose
        self.pub.publish(self.msg)

    def run(self):
        rospy.spin()

if __name__ == '__main__':
    rospy.sleep(2)
    try:
        external_position = PublishExternalPosition()
        external_position.run()
    except rospy.ROSInterruptException:
        pass