#!/usr/bin/env python3
"""
guardar_datos.py — Recorder para experimento de transporte de carga.

Guarda en ~/Experimentos/:
  • Agente1_<sufijo>.mat  →  datos del quad 1
  • Agente2_<sufijo>.mat  →  datos del quad 2
  • Carga_<sufijo>.mat    →  pose VRPN real de la carga + trayectoria deseada

Estructura de cada fila guardada:
  Quad_i : [x, y, z, psi, u, tau_phi, tau_theta, tau_psi, phi, theta]
  Carga  : [x_real, y_real, z_real,
             x_des,  y_des,  z_des,
             ex,     ey,     ez]       ← error = real - deseado
"""
import os
import rospy
from geometry_msgs.msg import Twist, PoseStamped
from crazyflie.msg import Full
from scipy import io
import tf.transformations as t


class DataRecorder:
    def __init__(self):
        rospy.init_node('guardar_datos')

        # ── Tipo de controlador ───────────────────────────────────────
        self.ros_param1 = rospy.get_param('~n1', 1)
        self.ros_param2 = rospy.get_param('~n2', 1)

        _labels = {1:'PID', 2:'Mellinger', 3:'INDI',
                   4:'Brescanccini', 5:'Lee', 6:'JSAR'}
        suffix = _labels.get(self.ros_param1, 'PID')   # mismo sufijo para carga

        self.base_name_1 = f"Agente1_{_labels.get(self.ros_param1,'PID')}"
        self.base_name_2 = f"Agente2_{_labels.get(self.ros_param2,'PID')}"
        self.base_name_c = f"Carga_{suffix}"

        # ── Buffers ───────────────────────────────────────────────────
        self.Quad1  = []
        self.Quad2  = []
        self.Carga  = []

        self.is_saving_data = False

        # ── Estado interno (inicializar para evitar AttributeError) ───
        # Quad 1
        self.x1 = self.y1 = self.z1 = 0.0
        self.phi1 = self.theta1 = self.psi1 = 0.0
        self.tau_phi1 = self.tau_theta1 = self.tau_psi1 = self.u1 = 0.0
        # Quad 2
        self.x2 = self.y2 = self.z2 = 0.0
        self.phi2 = self.theta2 = self.psi2 = 0.0
        self.tau_phi2 = self.tau_theta2 = self.tau_psi2 = self.u2 = 0.0
        # Carga real
        self.xc = self.yc = self.zc = 0.0
        # Carga deseada
        self.xd = self.yd = self.zd = 0.0

        # ── Suscriptores ─────────────────────────────────────────────
        rospy.Subscriber('/crazyflie1/sc',
                         Twist, self.CMD_Signals1)
        rospy.Subscriber('/vrpn_client_node/crazyflie1/pose',
                         PoseStamped, self.VRPNPOSE1)

        rospy.Subscriber('/crazyflie2/sc',
                         Twist, self.CMD_Signals2)
        rospy.Subscriber('/vrpn_client_node/crazyflie2/pose',
                         PoseStamped, self.VRPNPOSE2)

        # Carga real (marcador OptiTrack en la carga)
        carga_vrpn = rospy.get_param(
            '~carga_vrpn_topic', '/vrpn_client_node/carga/pose')
        rospy.Subscriber(carga_vrpn, PoseStamped, self.VRPNPOSE_CARGA)

        # Trayectoria deseada de la carga (publicada por carga.py)
        rospy.Subscriber('/carga/desired_pose',
                         PoseStamped, self.DESIRED_CARGA)

        # Señal de inicio / parada del recorder
        rospy.Subscriber('/start', Twist, self.Start)

    # ── Quad 1 ────────────────────────────────────────────────────────
    def CMD_Signals1(self, msg):
        self.tau_phi1   = msg.linear.x
        self.tau_theta1 = msg.linear.y
        self.tau_psi1   = msg.linear.z
        self.u1         = msg.linear.z

    def VRPNPOSE1(self, msg):
        q   = msg.pose.orientation
        rpy = t.euler_from_quaternion([q.x, q.y, q.z, q.w])
        self.phi1   = rpy[0]
        self.theta1 = rpy[1]
        self.psi1   = rpy[2]
        self.x1 = msg.pose.position.x
        self.y1 = msg.pose.position.y
        self.z1 = msg.pose.position.z

    # ── Quad 2 ────────────────────────────────────────────────────────
    def CMD_Signals2(self, msg):
        self.tau_phi2   = msg.linear.x
        self.tau_theta2 = msg.linear.y
        self.tau_psi2   = msg.linear.z
        self.u2         = msg.linear.z

    def VRPNPOSE2(self, msg):
        q   = msg.pose.orientation
        rpy = t.euler_from_quaternion([q.x, q.y, q.z, q.w])
        self.phi2   = rpy[0]
        self.theta2 = rpy[1]
        self.psi2   = rpy[2]
        self.x2 = msg.pose.position.x
        self.y2 = msg.pose.position.y
        self.z2 = msg.pose.position.z

    # ── Carga ─────────────────────────────────────────────────────────
    def VRPNPOSE_CARGA(self, msg):
        self.xc = msg.pose.position.x
        self.yc = msg.pose.position.y
        self.zc = msg.pose.position.z

    def DESIRED_CARGA(self, msg):
        self.xd = msg.pose.position.x
        self.yd = msg.pose.position.y
        self.zd = msg.pose.position.z

    # ── Control de grabación ─────────────────────────────────────────
    def Start(self, msg):
        val = msg.angular.x
        if val == 10 and not self.is_saving_data:
            self.is_saving_data = True
            rospy.loginfo("[RECORDER] Grabando datos...")
        elif val == 0 and self.is_saving_data:
            self.is_saving_data = False
            rospy.loginfo("[RECORDER] Grabación detenida.")

        if self.is_saving_data:
            self.Quad1.append([
                self.x1, self.y1, self.z1,
                self.psi1, self.u1,
                self.tau_phi1, self.tau_theta1, self.tau_psi1,
                self.phi1, self.theta1
            ])
            self.Quad2.append([
                self.x2, self.y2, self.z2,
                self.psi2, self.u2,
                self.tau_phi2, self.tau_theta2, self.tau_psi2,
                self.phi2, self.theta2
            ])
            self.Carga.append([
                self.xc, self.yc, self.zc,          # pose real
                self.xd, self.yd, self.zd,          # pose deseada
                self.xc - self.xd,                  # ex
                self.yc - self.yd,                  # ey
                self.zc - self.zd,                  # ez
            ])

    # ── Guardado al cerrar ────────────────────────────────────────────
    def save_data(self):
        home_dir = os.path.expanduser("~/Experimentos")
        os.makedirs(home_dir, exist_ok=True)

        def _save(path, key, data):
            io.savemat(path, {key: data})
            rospy.loginfo(f"[RECORDER] Guardado: {path}  ({len(data)} muestras)")

        _save(os.path.join(home_dir, self.base_name_1 + ".mat"),
              'Quad1_data', self.Quad1)
        _save(os.path.join(home_dir, self.base_name_2 + ".mat"),
              'Quad2_data', self.Quad2)
        _save(os.path.join(home_dir, self.base_name_c + ".mat"),
              'Carga_data', self.Carga)


if __name__ == '__main__':
    recorder = DataRecorder()
    rospy.on_shutdown(recorder.save_data)
    rospy.spin()
