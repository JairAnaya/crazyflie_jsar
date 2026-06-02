#!/usr/bin/env python3
import numpy as np
import rospy
import tf
from std_msgs.msg import Header
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Joy
from crazyflie.msg import Full

# Definimos estados para facilitar el control
IDLE = 0      # Motores apagados / Esperando
FLYING = 1    # Volando la trayectoria
LANDING = 2   # Aterrizando suavemente

class TrajectoryCircle:
    def __init__(self):
        # --- Configuración inicial ---
        self.state = IDLE
        self.start_time = None
        
        # Guardamos la última posición conocida para poder aterrizar en ese lugar
        self.last_x = 0.0
        self.last_y = 0.0
        self.last_z = 0.0
        self.last_yaw = 0.0

        self.rt = 50.0  # 50 Hz
        self.dt = 1.0 / self.rt

        self.pub = rospy.Publisher('cmd_full', Full, queue_size=1)
        self.start_pub = rospy.Publisher('/start', Twist, queue_size=1)

        # Parámetros desde el launch
        self.xi = rospy.get_param("~xi", 0.0)
        self.yi = rospy.get_param("~yi", 0.0)
        self.zi = rospy.get_param("~zi", 0.0)
        self.altura_final = rospy.get_param("~h", 0.4)
        self.radio_final = rospy.get_param("~r", 0.3)
        
        self.takeoff_duration = 5.0 
        self.trajectory_duration = 60.0 # Duración de la parte circular

    def joy_callback(self, joy_msg):
        # Botón A (índice 2, verifica si es 0, 1, 2 en tu control) para iniciar
        if joy_msg.buttons[2] == 1 and self.state == IDLE:
            rospy.loginfo('Iniciando secuencia: Despegue -> Trayectoria')
            self.state = FLYING
            self.start_time = rospy.Time.now()

        # Botón para detener/reiniciar (índice 10)
        # En lugar de matar motores, cambiamos al estado LANDING
        elif joy_msg.buttons[10] == 1 and self.state == FLYING:
            rospy.loginfo('Cancelación manual: Iniciando aterrizaje suave...')
            self.state = LANDING

    def trajectory_circle(self):
        rate = rospy.Rate(self.rt)

        while not rospy.is_shutdown():
            full_msg = Full()
            full_msg.header = Header()
            full_msg.header.stamp = rospy.Time.now()

            # --- CASO 1: VOLANDO (Despegue + Círculo) ---
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
                    
                    # Trayectoria suave
                    r_smooth = self.radio_final * (np.arctan(p) + np.arctan(t_traj - p)) / (np.arctan(p) + np.pi/2)
                    
                    x = r_smooth * np.cos(w * t_traj) + self.xi
                    y = r_smooth * np.sin(w * t_traj) + self.yi
                    z = self.altura_final + self.zi
                    yaw = 0.0

                    # Velocidades
                    dx = -r_smooth * w * np.sin(w * t_traj)
                    dy = r_smooth * w * np.cos(w * t_traj)
                    dz = 0.0
                
                # Tiempo agotado -> Cambiar a Aterrizaje
                else:
                    rospy.loginfo('Trayectoria finalizada por tiempo. Aterrizando...')
                    self.state = LANDING
                    # Mantenemos los valores actuales para la primera iteración de landing
                    x, y, z = self.last_x, self.last_y, self.last_z
                    dx, dy, dz = 0, 0, 0
                    yaw = self.last_yaw

                # Actualizamos variables de estado y mensaje
                self.last_x, self.last_y, self.last_z, self.last_yaw = x, y, z, yaw
                
                full_msg.twist1.linear.x = x
                full_msg.twist1.linear.y = y
                full_msg.twist1.linear.z = z
                full_msg.twist1.angular.x = dx
                full_msg.twist1.angular.y = dy
                full_msg.twist1.angular.z = dz
                full_msg.twist2.angular.x = yaw
                
                self.pub.publish(full_msg)

                if int(elapsed_time * 10) % 50 == 0:
                     rospy.loginfo(f"Vuelo | Z: {z:.2f}")

            # --- CASO 2: ATERRIZAJE SUAVE (LANDING) ---
            elif self.state == LANDING:
                # Mantenemos X e Y donde estaban, bajamos Z gradualmente
                descend_speed = 0.2 # m/s (velocidad de bajada)
                step = descend_speed * self.dt
                
                self.last_z -= step

                # Si ya llegamos a 5cm (0.05m) o menos
                if self.last_z <= 0.05:
                    self.last_z = 0.05
                    rospy.loginfo("Aterrizaje completado. Apagando motores.")
                    self.state = IDLE # Pasamos a modo espera (motores off)
                    
                    # Enviamos un último mensaje de "Stop" (todo en ceros)
                    self.pub.publish(Full()) 
                else:
                    # Publicamos la posición descendente
                    full_msg.twist1.linear.x = self.last_x
                    full_msg.twist1.linear.y = self.last_y
                    full_msg.twist1.linear.z = self.last_z
                    full_msg.twist2.angular.x = self.last_yaw # Mantener orientación
                    
                    self.pub.publish(full_msg)

            # --- CASO 3: IDLE (Esperando) ---
            elif self.state == IDLE:
                # Opcional: Publicar ceros periódicamente para asegurar que no se arme solo
                # self.pub.publish(Full()) 
                pass

            rate.sleep()

if __name__ == '__main__':
    rospy.init_node('trajectory_circle', anonymous=True)
    traj_circle = TrajectoryCircle()
    joy_sub = rospy.Subscriber('joy', Joy, traj_circle.joy_callback)
    try:
        traj_circle.trajectory_circle()
    except rospy.ROSInterruptException:
        pass