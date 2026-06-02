#!/usr/bin/env python3
import numpy as np
import rospy
from std_msgs.msg import Header
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Joy
from crazyflie.msg import Full

IDLE = 0
FLYING = 1
LANDING = 2

class TrajectoryCircle:
    def __init__(self):
        # --- Configuración inicial ---
        self.state = IDLE
        self.start_time = None
        # Inicializamos en el valor del launch por seguridad
        self.xi = rospy.get_param("~xi", 0.0)
        self.yi = rospy.get_param("~yi", -0.2)
        self.zi = rospy.get_param("~zi", 0.0)
        self.altura_final = rospy.get_param("~h", 0.4)
        self.radio_final = rospy.get_param("~r", 0.3)

        # Guardamos la última posición conocida (iniciamos en el punto de despegue)
        self.last_x = self.xi
        self.last_y = self.yi
        self.last_z = self.zi
        self.last_yaw = 0.0

        self.rt = 50.0
        self.dt = 1.0 / self.rt

        self.pub = rospy.Publisher('cmd_full', Full, queue_size=1)
        self.start_pub = rospy.Publisher('/start', Twist, queue_size=1)
        self.takeoff_duration = 5.0
        self.trajectory_duration = 60.0

    def joy_callback(self, joy_msg):
        # Botón A (índice 2)
        if joy_msg.buttons[2] == 1 and self.state == IDLE:
            rospy.loginfo('LIDER: Iniciando vuelo.')
            self.state = FLYING
            self.start_time = rospy.Time.now()
        # Botón Start/Stop (índice 10 en algunos controles, verifica el tuyo)
        elif joy_msg.buttons[10] == 1 and self.state == FLYING:
            rospy.loginfo('LIDER: Cancelación manual. Aterrizando...')
            self.state = LANDING

    def trajectory_circle(self):
        rate = rospy.Rate(self.rt)

        while not rospy.is_shutdown():
            full_msg = Full()
            full_msg.header = Header()
            full_msg.header.stamp = rospy.Time.now()

            # --- CASO 1: VOLANDO ---
            if self.state == FLYING:
                current_time = rospy.Time.now()
                elapsed_time = (current_time - self.start_time).to_sec()

                # Fase de Despegue
                if elapsed_time < self.takeoff_duration:
                    frac = elapsed_time / self.takeoff_duration
                    x = self.xi
                    y = self.yi
                    z = self.zi + (self.altura_final * frac)
                    dx = dy = dz = 0.0
                    yaw = 0.0

                # Fase de Trayectoria Circular
                elif elapsed_time < (self.takeoff_duration + self.trajectory_duration):
                    t_traj = elapsed_time - self.takeoff_duration
                    w = np.pi / 6
                    p = 15
                    r_smooth = self.radio_final * (np.arctan(p) + np.arctan(t_traj - p)) / (np.arctan(p) + np.pi/2)
                    x = r_smooth * np.cos(w * t_traj) + self.xi
                    y = r_smooth * np.sin(w * t_traj) + self.yi
                    z = self.altura_final + self.zi
                    yaw = 0.0
                    # Derivadas (Velocidades)
                    dx = -r_smooth * w * np.sin(w * t_traj)
                    dy = r_smooth * w * np.cos(w * t_traj)
                    dz = 0.0
                else:
                    rospy.loginfo('Tiempo finalizado. Aterrizando...')
                    self.state = LANDING
                    x, y, z = self.last_x, self.last_y, self.last_z
                    dx, dy, dz = 0, 0, 0
                    yaw = self.last_yaw

                # Actualizamos last_x/y/z para saber dónde aterrizar si se cancela
                self.last_x, self.last_y, self.last_z, self.last_yaw = x, y, z, yaw
                full_msg.twist1.linear.x = x
                full_msg.twist1.linear.y = y
                full_msg.twist1.linear.z = z
                full_msg.twist1.angular.x = dx
                full_msg.twist1.angular.y = dy
                full_msg.twist1.angular.z = dz
                full_msg.twist2.angular.x = yaw
                self.pub.publish(full_msg)

            # --- CASO 2: ATERRIZAJE SUAVE ---
            elif self.state == LANDING:
                descend_speed = 0.2
                step = descend_speed * self.dt
                self.last_z -= step

                if self.last_z <= 0.05:
                    self.last_z = 0.0
                    rospy.loginfo_throttle(2, "LIDER: Motores Apagados (Safe Mode).")
                    self.state = IDLE
                    # --- CORRECCIÓN CHOQUE ---
                    # No mandamos Full() vacío porque eso es ir a 0,0,0.
                    # Mandamos quedarse en X,Y y Z=0
                    stop_msg = Full()
                    stop_msg.twist1.linear.x = self.last_x
                    stop_msg.twist1.linear.y = self.last_y
                    stop_msg.twist1.linear.z = 0.0
                    self.pub.publish(stop_msg)

                else:
                    full_msg.twist1.linear.x = self.last_x
                    full_msg.twist1.linear.y = self.last_y
                    full_msg.twist1.linear.z = self.last_z
                    full_msg.twist2.angular.x = self.last_yaw
                    self.pub.publish(full_msg)

            elif self.state == IDLE:
                pass
            rate.sleep()


if __name__ == '__main__':
    rospy.init_node('trajectory_circle', anonymous=True)
    traj_circle = TrajectoryCircle()
    # Aseguramos usar /joy global
    joy_sub = rospy.Subscriber('/joy', Joy, traj_circle.joy_callback)
    try:
        traj_circle.trajectory_circle()
    except rospy.ROSInterruptException:
        pass 