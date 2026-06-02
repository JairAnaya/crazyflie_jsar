#!/usr/bin/env python3
"""
Nodo de hover con activación automática del observador SM-FTO.

El observador se activa automáticamente después de hover_stable_time
segundos de hover estable (error XY < hover_stable_thr).

El observador se puede también activar/desactivar manualmente
desde cfclient en Parameters → ctrlJair.obs_en.
"""
import numpy as np
import rospy
from geometry_msgs.msg import PoseStamped
from sensor_msgs.msg import Joy
from crazyflie.msg import Full
from crazyflie_driver.srv import UpdateParams

IDLE    = 0
FLYING  = 1
LANDING = 2


class HoverNode:
    def __init__(self):
        rospy.init_node('hover_node', anonymous=True)

        self.h            = rospy.get_param("~h",  0.4)
        self.takeoff_rate = rospy.get_param("~takeoff_rate", 0.3)

        # Parámetros del observador
        # Tiempo de hover estable antes de activar el observador [s]
        self.obs_activate_delay = rospy.get_param("~obs_activate_delay", 10.0)
        # Umbral de error XY para considerar "hover estable" [m]
        self.obs_stable_thr     = rospy.get_param("~obs_stable_thr", 0.08)
        # Namespace del crazyflie para el servicio de parámetros
        self.cf_ns = rospy.get_param("~cf_namespace", "/crazyflie1")

        # Estado
        self.my_x = 0.0
        self.my_y = 0.0
        self.my_z = 0.0
        self.optitrack_ready = False

        self.hover_x  = 0.0
        self.hover_y  = 0.0
        self.hover_zi = 0.0

        self.last_z = 0.0
        self.state      = IDLE
        self.start_time = None

        # Para activación del observador
        self.obs_active       = False
        self.hover_start_time = None  # cuando llegó a hover estable

        self.rt = 50.0
        self.dt = 1.0 / self.rt

        self.pub = rospy.Publisher('cmd_full', Full, queue_size=1)

        vrpn_topic = rospy.get_param(
            "~vrpn_topic", "/vrpn_client_node/crazyflie1/pose")
        rospy.Subscriber(vrpn_topic, PoseStamped, self.pose_cb)
        rospy.Subscriber('joy', Joy, self.joy_cb)

        # Servicio de parámetros del firmware
        svc_name = self.cf_ns + '/update_params'
        rospy.loginfo(f"[HOVER] Esperando servicio {svc_name}...")
        try:
            rospy.wait_for_service(svc_name, timeout=5.0)
            self.update_params = rospy.ServiceProxy(svc_name, UpdateParams)
            self.has_param_svc = True
            rospy.loginfo("[HOVER] Servicio de parámetros disponible")
        except rospy.ROSException:
            rospy.logwarn("[HOVER] Servicio de parámetros no disponible — obs no se activará automáticamente")
            self.has_param_svc = False

        rospy.loginfo(f"[HOVER] Listo. A=despegar, 10=aterrizar")
        rospy.loginfo(f"[HOVER] Obs se activará tras {self.obs_activate_delay}s de hover estable")

    def _set_obs_enabled(self, value):
        """Activa o desactiva el observador via servicio ROS."""
        if not self.has_param_svc:
            return
        param_name = self.cf_ns + "/ctrlJair/obs_en"
        try:
            rospy.set_param(param_name, int(value))
            self.update_params(["ctrlJair/obs_en"])
            self.obs_active = bool(value)
            rospy.loginfo(f"[HOVER] Observador {'ACTIVADO' if value else 'DESACTIVADO'}")
        except Exception as e:
            rospy.logerr(f"[HOVER] Error al cambiar obs_en: {e}")

    def pose_cb(self, msg):
        self.my_x = msg.pose.position.x
        self.my_y = msg.pose.position.y
        self.my_z = msg.pose.position.z
        if not self.optitrack_ready:
            self.optitrack_ready = True
            rospy.loginfo(f"[HOVER] OptiTrack: ({self.my_x:.3f}, {self.my_y:.3f}, {self.my_z:.3f})")

    def joy_cb(self, msg):
        if msg.buttons[2] == 1 and self.state == IDLE:
            if not self.optitrack_ready:
                rospy.logwarn("[HOVER] OptiTrack no listo")
                return
            self.hover_x  = self.my_x
            self.hover_y  = self.my_y
            self.hover_zi = self.my_z
            self.obs_active = False
            self.hover_start_time = None
            # Asegurar que el observador empieza desactivado
            self._set_obs_enabled(False)
            self.state      = FLYING
            self.start_time = rospy.Time.now()
            rospy.loginfo(
                f"[HOVER] Despegando desde "
                f"({self.hover_x:.3f}, {self.hover_y:.3f}, {self.hover_zi:.3f})"
                f" → z={self.hover_zi + self.h:.3f}m")

        elif msg.buttons[10] == 1 and self.state != IDLE:
            rospy.loginfo("[HOVER] Aterrizando...")
            if self.obs_active:
                self._set_obs_enabled(False)
            self.state = LANDING

    def _check_obs_activation(self):
        """
        Activa el observador automáticamente cuando el hover es estable.
        Condición: error XY < obs_stable_thr durante obs_activate_delay segundos.
        """
        if self.obs_active or not self.has_param_svc:
            return

        err_xy = np.sqrt((self.hover_x - self.my_x)**2 +
                         (self.hover_y - self.my_y)**2)
        now = rospy.Time.now()

        if err_xy < self.obs_stable_thr:
            if self.hover_start_time is None:
                self.hover_start_time = now
                rospy.loginfo(f"[HOVER] Hover estable detectado (err_xy={err_xy:.3f}m). "
                              f"Observador se activará en {self.obs_activate_delay:.0f}s...")
            else:
                elapsed = (now - self.hover_start_time).to_sec()
                if elapsed >= self.obs_activate_delay:
                    rospy.loginfo(f"[HOVER] Activando observador SM-FTO "
                                  f"(hover estable por {elapsed:.1f}s)")
                    self._set_obs_enabled(True)
        else:
            # Si pierde estabilidad, resetear el contador
            if self.hover_start_time is not None:
                rospy.loginfo_throttle(5.0,
                    f"[HOVER] Hover inestable (err_xy={err_xy:.3f}m), "
                    f"contador reiniciado")
            self.hover_start_time = None

    def run(self):
        rate = rospy.Rate(self.rt)

        while not rospy.is_shutdown():
            msg = Full()
            msg.header.stamp = rospy.Time.now()

            if self.state == FLYING:
                elapsed = (rospy.Time.now() - self.start_time).to_sec()
                z = self.hover_zi + self.h * (1.0 - np.exp(-self.takeoff_rate * elapsed))
                self.last_z = z

                # Verificar activación del observador cuando ya llegó a hover
                if z >= self.hover_zi + self.h * 0.95:
                    self._check_obs_activation()

                err_xy = np.sqrt((self.hover_x - self.my_x)**2 +
                                 (self.hover_y - self.my_y)**2)
                rospy.loginfo_throttle(
                    2.0,
                    f"[HOVER] z_sp={z:.3f}  z_real={self.my_z:.3f}  "
                    f"ex={self.hover_x - self.my_x:.3f}  "
                    f"ey={self.hover_y - self.my_y:.3f}  "
                    f"obs={'ON' if self.obs_active else 'OFF'}")

                msg.twist1.linear.x = self.hover_x
                msg.twist1.linear.y = self.hover_y
                msg.twist1.linear.z = z
                msg.twist2.angular.x = 0.0
                self.pub.publish(msg)

            elif self.state == LANDING:
                self.last_z -= 0.2 * self.dt
                if self.last_z <= 0.05:
                    self.last_z = 0.0
                    self.state  = IDLE
                    rospy.loginfo("[HOVER] En suelo. IDLE.")
                    self.pub.publish(Full())
                else:
                    msg.twist1.linear.x = self.hover_x
                    msg.twist1.linear.y = self.hover_y
                    msg.twist1.linear.z = self.last_z
                    self.pub.publish(msg)

            elif self.state == IDLE:
                pass

            rate.sleep()


if __name__ == '__main__':
    try:
        node = HoverNode()
        node.run()
    except rospy.ROSInterruptException:
        pass
