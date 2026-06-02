#!/usr/bin/env python3
"""
Nodo de la CARGA (Líder virtual).
- Conoce la trayectoria deseada (círculo).
- Publica la trayectoria deseada en /carga/desired_pose para que los quads
  calculen su posición de formación: ξ_di = ξ_carga_deseada + Ci
- NO controla ningún quad directamente. Es un nodo de referencia.
- También suscribe a la pose real de la carga (VRPN) y publica el error
  de posición de la carga (para monitoreo/debug).

Basado en la Sección 6 del reporte de avances:
  ξ_di = ξ_c + Ci
  donde Ci son los vectores de formación geométrica con α = 45°.
"""
import numpy as np
import rospy
from std_msgs.msg import Header
from geometry_msgs.msg import PoseStamped, TwistStamped
from sensor_msgs.msg import Joy

IDLE    = 0
FLYING  = 1
LANDING = 2


class CargaLider:
    def __init__(self):
        rospy.init_node('carga_lider', anonymous=True)

        # --- Parámetros de la trayectoria ---
        self.xi = rospy.get_param("~xi", 0.0)
        self.yi = rospy.get_param("~yi", 0.0)
        self.zi = rospy.get_param("~zi", 0.0)
        self.h  = rospy.get_param("~h",  0.1)   # altura de vuelo de la carga
        self.r  = rospy.get_param("~r",  0.2)   # radio del círculo

        # --- Estado ---
        self.state      = IDLE
        self.start_time = None
        self.trajectory_duration = 60.0

        self.last_x   = self.xi
        self.last_y   = self.yi
        self.last_z   = self.zi

        # Pose real de la carga (desde VRPN / OptiTrack)
        # En el experimento real la carga es un marcador rígido.
        # Si no hay VRPN de la carga, este campo queda como None y
        # publicamos solo la referencia deseada.
        self.carga_real_pos = None

        self.rt = 30.0
        self.dt = 1.0 / self.rt

        # --- Publishers ---
        # Pose DESEADA de la carga → los quads la leen para calcular ξ_di = ξ_cd + Ci
        self.pub_desired = rospy.Publisher(
            '/carga/desired_pose', PoseStamped, queue_size=1)

        # Error de posición de la carga (para monitoreo)
        self.pub_error = rospy.Publisher(
            '/carga/position_error', TwistStamped, queue_size=1)

        # --- Subscribers ---
        rospy.Subscriber('/joy', Joy, self.joy_callback)

        carga_vrpn = rospy.get_param("~carga_vrpn_topic", "")
        if carga_vrpn:
            rospy.Subscriber(carga_vrpn, PoseStamped, self.carga_pose_callback)

    # ------------------------------------------------------------------
    def joy_callback(self, msg):
        if msg.buttons[2] == 1 and self.state == IDLE:
            rospy.loginfo("[CARGA] Iniciando trayectoria.")
            self.state      = FLYING
            self.start_time = rospy.Time.now()
        elif msg.buttons[10] == 1 and self.state == FLYING:
            rospy.loginfo("[CARGA] Cancelación manual. Aterrizando.")
            self.state = LANDING

    def carga_pose_callback(self, msg):
        self.carga_real_pos = msg.pose.position

    # ------------------------------------------------------------------
    def compute_trajectory(self, elapsed):
        """
        Trayectoria circular con despegue suave.

        Z usa tanh centrado en t=2.5 s, lo que produce un ascenso
        continuo y diferenciable desde zi hasta h+zi, sin fase de
        despegue separada. El radio XY crece también suavemente con
        arctan, arrancando desde 0 para no generar tirones laterales
        al inicio.
        """
        if elapsed >= self.trajectory_duration:
            # Tiempo cumplido → aterrizar
            self.state = LANDING
            return self.last_x, self.last_y, self.last_z, 0.0, 0.0, 0.0

        t = elapsed
        w = np.pi / 6      # velocidad angular [rad/s]
        p = 15.0           # factor de suavizado del radio

        # Radio creciente (arctan) — evita tirón lateral brusco al arrancar
        r_s = self.r * (np.arctan(p) + np.arctan(t - p))

        # Posición
        x = r_s * np.cos(w * t) + self.xi
        y = r_s * np.sin(w * t) + self.yi
        z = (self.h / 2) * (1 + np.tanh(t - 2.5)) + self.zi

        # Velocidades (primera derivada)
        dx = -r_s * w * np.sin(w * t)
        dy =  r_s * w * np.cos(w * t)
        dz =  (self.h / 2) * np.tanh(t - 2.5) * (1 - np.tanh(t - 2.5))

        return x, y, z, dx, dy, dz

    # ------------------------------------------------------------------
    def run(self):
        rate = rospy.Rate(self.rt)

        while not rospy.is_shutdown():
            now = rospy.Time.now()

            if self.state == FLYING:
                elapsed = (now - self.start_time).to_sec()
                x, y, z, dx, dy, dz = self.compute_trajectory(elapsed)
                self.last_x, self.last_y, self.last_z = x, y, z

            elif self.state == LANDING:
                # Descenso gradual de la referencia
                self.last_z -= 0.2 * self.dt
                if self.last_z <= 0.05:
                    self.last_z = 0.0
                    self.state  = IDLE
                    rospy.loginfo("[CARGA] Referencia en suelo. IDLE.")
                x, y, z     = self.last_x, self.last_y, self.last_z
                dx = dy = dz = 0.0

            else:  # IDLE
                x, y, z     = self.last_x, self.last_y, self.last_z
                dx = dy = dz = 0.0

            # --- Publicar pose deseada de la carga ---
            desired = PoseStamped()
            desired.header.stamp    = now
            desired.header.frame_id = "world"
            desired.pose.position.x = x
            desired.pose.position.y = y
            desired.pose.position.z = z
            # Velocidad deseada viaja en el campo de orientación (hack conveniente
            # para no crear un mensaje custom): angular.x=dx, .y=dy, .z=dz
            # Los quads leen esto para feedforward.
            # (alternativa: publicar un TwistStamped aparte)
            self.pub_desired.publish(desired)

            # --- Publicar error de posición de la carga (si hay VRPN) ---
            if self.carga_real_pos is not None:
                err = TwistStamped()
                err.header.stamp = now
                err.twist.linear.x = self.carga_real_pos.x - x
                err.twist.linear.y = self.carga_real_pos.y - y
                err.twist.linear.z = self.carga_real_pos.z - z
                self.pub_error.publish(err)

            rate.sleep()


if __name__ == '__main__':
    try:
        nodo = CargaLider()
        nodo.run()
    except rospy.ROSInterruptException:
        pass