#!/usr/bin/env python3
import rospy
import numpy as np
import tf # Necesario para leer la orientación (yaw)
from std_msgs.msg import Header
from geometry_msgs.msg import Twist, PoseStamped
from sensor_msgs.msg import Joy
from crazyflie.msg import Full

IDLE = 0
FLYING = 1
LANDING = 2

class FollowerDrone:
    def __init__(self):
        rospy.init_node('follower_node', anonymous=True)

        # --- Parámetros Propios ---
        self.xi = rospy.get_param("~xi", 0.14)
        self.yi = rospy.get_param("~yi", 0.14)
        self.zi = rospy.get_param("~zi", 0.0)
        # Nota: Ya no usamos 'h' ni 'z_correction' porque obedeceremos al líder.

        # --- Parámetros del Líder (Para calcular el Offset) ---
        self.leader_xi = rospy.get_param("~leader_xi", 0.0)
        self.leader_yi = rospy.get_param("~leader_yi", 0.0)
        self.leader_zi = rospy.get_param("~leader_zi", 0.0)
        
        # Calculamos el Offset constante (Delta)
        self.offset_x = self.xi - self.leader_xi
        self.offset_y = self.yi - self.leader_yi
        self.offset_z = self.zi - self.leader_zi # Por si quisieras que volara más arriba/abajo que el líder

        # --- Variables de Estado ---
        self.state = IDLE
        self.leader_pos = None 
        self.leader_yaw = 0.0 # Almacenará la orientación del líder
        
        # Posiciones de seguridad
        self.last_x = self.xi
        self.last_y = self.yi
        self.last_z = 0.0 
        self.last_yaw = 0.0

        # Timer para seguridad (para detectar aterrizaje)
        self.start_time = None
        self.min_flight_time = 5.0 

        self.rate = rospy.Rate(50) 
        self.dt = 1.0/50.0

        self.pub = rospy.Publisher('cmd_full', Full, queue_size=1)
        self.sub_joy = rospy.Subscriber('/joy', Joy, self.joy_callback)
        
        leader_topic = rospy.get_param("~leader_topic", "/vrpn_client_node/crazyflie1/pose")
        self.sub_leader = rospy.Subscriber(leader_topic, PoseStamped, self.leader_pose_callback)

    def joy_callback(self, joy_msg):
        if joy_msg.buttons[2] == 1 and self.state == IDLE:
            rospy.loginfo("SEGUIDOR: Iniciando seguimiento (Esperando movimiento del líder).")
            self.state = FLYING
            self.start_time = rospy.Time.now()
        elif joy_msg.buttons[10] == 1 and self.state == FLYING:
            rospy.loginfo("SEGUIDOR: Cancelación manual.")
            self.state = LANDING

    def leader_pose_callback(self, msg):
        # 1. Posición
        self.leader_pos = msg.pose.position

        # 2. Orientación (Conversión Cuaternión -> Euler)
        # Extraemos cuaternión
        q = (
            msg.pose.orientation.x,
            msg.pose.orientation.y,
            msg.pose.orientation.z,
            msg.pose.orientation.w
        )
        # Convertimos a Euler (roll, pitch, yaw)
        euler = tf.transformations.euler_from_quaternion(q)
        # euler[2] es el Yaw en radianes. 
        # Convertimos a grados si tu controlador JSAR usa grados, o radianes si usa radianes.
        # Por estándar en JSAR/Full msg suele ser GRADOS.
        self.leader_yaw = np.degrees(euler[2]) 

    def run(self):
        while not rospy.is_shutdown():
            full_msg = Full()
            full_msg.header = Header()
            full_msg.header.stamp = rospy.Time.now()

            # --- CASO 1: VOLANDO (Copiar al Líder) ---
            if self.state == FLYING:
                if self.leader_pos is None:
                    rospy.logwarn_throttle(2, "SEGUIDOR: Esperando VRPN del líder...")
                else:
                    elapsed = (rospy.Time.now() - self.start_time).to_sec()

                    # DETECCIÓN DE ATERRIZAJE AUTOMÁTICO
                    # Si el líder baja de 15cm después de haber volado un rato, asumimos que acabó.
                    if elapsed > self.min_flight_time and self.leader_pos.z < 0.15:
                        rospy.loginfo("SEGUIDOR: Líder en suelo detectado. Terminando vuelo.")
                        self.state = LANDING
                        self.last_x = self.leader_pos.x + self.offset_x
                        self.last_y = self.leader_pos.y + self.offset_y
                        self.last_z = self.leader_pos.z + self.offset_z
                        self.last_yaw = self.leader_yaw
                        continue

                    # --- LÓGICA DE SEGUIMIENTO PURO ---
                    # Calculamos objetivo basado 100% en el líder actual
                    target_x = self.leader_pos.x + self.offset_x
                    target_y = self.leader_pos.y + self.offset_y
                    target_z = self.leader_pos.z + self.offset_z # Ahora Z también copia al líder
                    target_yaw = self.leader_yaw # Copiamos el giro

                    # Enviamos mensaje
                    full_msg.twist1.linear.x = target_x
                    full_msg.twist1.linear.y = target_y
                    full_msg.twist1.linear.z = target_z
                    
                    # Velocidades (feedforward): Podríamos calcular (pos - last_pos)/dt 
                    # pero por ahora dejamos en 0 para que el PID interno haga el trabajo.
                    full_msg.twist1.angular.x = 0.0 
                    full_msg.twist1.angular.y = 0.0 
                    full_msg.twist1.angular.z = 0.0 
                    
                    # Orientación
                    full_msg.twist2.angular.x = target_yaw

                    # Actualizamos últimas posiciones conocidas
                    self.last_x, self.last_y, self.last_z, self.last_yaw = target_x, target_y, target_z, target_yaw

                    self.pub.publish(full_msg)

            # --- CASO 2: ATERRIZAJE ---
            elif self.state == LANDING:
                # Bajamos gradualmente desde donde nos hayamos quedado
                descend_speed = 0.2
                self.last_z -= (descend_speed * self.dt)

                if self.last_z <= 0.05:
                    self.last_z = 0.0
                    self.state = IDLE
                    
                    # Paro seguro
                    stop_msg = Full()
                    stop_msg.twist1.linear.x = self.last_x
                    stop_msg.twist1.linear.y = self.last_y
                    stop_msg.twist1.linear.z = 0.0 
                    self.pub.publish(stop_msg)
                else:
                    full_msg.twist1.linear.x = self.last_x
                    full_msg.twist1.linear.y = self.last_y
                    full_msg.twist1.linear.z = self.last_z
                    full_msg.twist2.angular.x = self.last_yaw # Mantenemos orientación al bajar
                    self.pub.publish(full_msg)

            elif self.state == IDLE:
                pass

            self.rate.sleep()

if __name__ == '__main__':
    try:
        follower = FollowerDrone()
        follower.run()
    except rospy.ROSInterruptException:
        pass