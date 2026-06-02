#!/usr/bin/env python3
"""
cargalider.py — Nodo de la CARGA (sensor pasivo).

La carga NO controla nada. Solo:
  1. Lee la pose real de la carga desde OptiTrack (VRPN).
  2. Lee la trayectoria deseada publicada por los quads (/trayectoria/desired_pose).
  3. Calcula y publica el error de seguimiento de la carga:
       e_carga = pos_carga_real - pos_deseada
  4. Publica la pose real de la carga para grabación y graficado.

Tópicos publicados:
  /carga/pose_real       (PoseStamped) — pose real de la carga (OptiTrack)
  /carga/position_error  (TwistStamped) — error de seguimiento de la carga
"""
import rospy
from geometry_msgs.msg import PoseStamped, TwistStamped


class CargaLider:
    def __init__(self):
        rospy.init_node('carga_lider', anonymous=True)

        # Pose real de la carga (OptiTrack)
        self.carga_pos = None

        # Trayectoria deseada (publicada por transportador_seguidor.py)
        self.desired_pos = None

        self.rt = 50.0

        # --- Publishers ---
        self.pub_real  = rospy.Publisher(
            '/carga/pose_real', PoseStamped, queue_size=1)
        self.pub_error = rospy.Publisher(
            '/carga/position_error', TwistStamped, queue_size=1)

        # --- Subscribers ---
        carga_vrpn = rospy.get_param(
            "~carga_vrpn_topic", "/vrpn_client_node/carga/pose")
        rospy.Subscriber(carga_vrpn, PoseStamped, self.carga_pose_callback)
        rospy.Subscriber('/trayectoria/desired_pose', PoseStamped,
                         self.desired_callback)

        rospy.loginfo(f"[CARGA] Escuchando VRPN en: {carga_vrpn}")

    def carga_pose_callback(self, msg):
        self.carga_pos = msg

    def desired_callback(self, msg):
        self.desired_pos = msg

    def run(self):
        rate = rospy.Rate(self.rt)
        while not rospy.is_shutdown():
            now = rospy.Time.now()

            # Publicar pose real
            if self.carga_pos is not None:
                self.pub_real.publish(self.carga_pos)

            # Publicar error de seguimiento
            if self.carga_pos is not None and self.desired_pos is not None:
                xc = self.carga_pos.pose.position.x
                yc = self.carga_pos.pose.position.y
                zc = self.carga_pos.pose.position.z

                xd = self.desired_pos.pose.position.x
                yd = self.desired_pos.pose.position.y
                zd = self.desired_pos.pose.position.z

                err = TwistStamped()
                err.header.stamp    = now
                err.header.frame_id = "world"
                err.twist.linear.x  = xc - xd
                err.twist.linear.y  = yc - yd
                err.twist.linear.z  = zc - zd
                self.pub_error.publish(err)

            rate.sleep()


if __name__ == '__main__':
    try:
        nodo = CargaLider()
        nodo.run()
    except rospy.ROSInterruptException:
        pass
