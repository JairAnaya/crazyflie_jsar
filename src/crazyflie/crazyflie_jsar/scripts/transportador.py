#!/usr/bin/env python3
"""
Nodo del QUAD TRANSPORTADOR (Seguidor).

Secuencia de vuelo:
──────────────────────────────────────────────────────────────────────
  FASE 1a — ASCENSO LIBRE (ASCENT)
    Sube en Z con perfil exponencial suave.
    X,Y se mandan fijos al valor inicial SIN ningún regulador activo.

  FASE 1b — ESTABILIZACIÓN EN X,Y (STABILIZE)
    Ya en z_safe, un regulador P proporcional corrige la deriva XY.
    - Solo término proporcional (sin derivativo) para evitar
      oscilaciones por el salto inicial del error.
    - Ganancia con rampa: sube de 0 a Kp_xy en stab_ramp_time segundos,
      para que la corrección entre suavemente en lugar de en un escalón.
    Termina cuando err_xy < xy_stable_thr.

  FASE 2 — IR A FORMACIÓN (GOTO_FORM)
    Se mueve hacia ξ_c_actual + Ci.
    Termina cuando error 3D < formation_thr.

  FASE 3 — SEGUIMIENTO (FOLLOWING)
    ξ_di = ξ_c_deseada + Ci en cada instante.
──────────────────────────────────────────────────────────────────────
"""
import numpy as np
import rospy
from geometry_msgs.msg import PoseStamped
from sensor_msgs.msg import Joy
from crazyflie.msg import Full

IDLE      = 0
ASCENT    = 1
STABILIZE = 2
GOTO_FORM = 3
FOLLOWING = 4
LANDING   = 5


class TransportadorDrone:
    def __init__(self):
        rospy.init_node('transportador_node', anonymous=True)

        # ── Posición inicial ──────────────────────────────────────────
        self.xi = rospy.get_param("~xi", 0.0)
        self.yi = rospy.get_param("~yi", 0.0)
        self.zi = rospy.get_param("~zi", 0.0)

        # ── Parámetros de despegue ────────────────────────────────────
        self.z_safe       = rospy.get_param("~z_safe", 0.25)
        # t_95% = 3/takeoff_rate  →  0.15: ~20s | 0.2: ~15s | 0.3: ~10s
        self.takeoff_rate = rospy.get_param("~takeoff_rate", 0.15)

        # ── Regulador P para estabilización (Fase 1b) ─────────────────
        # Solo proporcional — sin derivativo para evitar oscilaciones.
        # Ganancia con rampa de 0 → Kp_xy en stab_ramp_time segundos.
        self.Kp_xy         = rospy.get_param("~Kp_xy", 0.8)
        self.stab_ramp_time = rospy.get_param("~stab_ramp_time", 3.0)  # s

        # Umbral de error XY para pasar de Fase 1b → Fase 2
        self.xy_stable_thr = rospy.get_param("~xy_stable_thr", 0.04)

        # ── Umbral de formación (Fase 2 → 3) ─────────────────────────
        self.formation_thr = rospy.get_param("~formation_thr", 0.05)

        # ── Vector de formación Ci ────────────────────────────────────
        self.Ci = np.array([
            rospy.get_param("~ci_x", -0.2),
            rospy.get_param("~ci_y",  0.0),
            rospy.get_param("~ci_z",  0.2),
        ])
        rospy.loginfo(f"[TRANSPORTADOR] Ci = {self.Ci}")

        # ── Estado interno ────────────────────────────────────────────
        self.state           = IDLE
        self.start_time      = None
        self.stabilize_start = None   # marca cuando empieza Fase 1b

        # Posición congelada al presionar botón A
        self.takeoff_x  = self.xi
        self.takeoff_y  = self.yi
        self.takeoff_zi = self.zi

        # Posición real del quad (OptiTrack)
        self.my_x = self.xi
        self.my_y = self.yi
        self.my_z = self.zi
        self.optitrack_ready = False

        # Último setpoint enviado (para aterrizaje suave)
        self.last_x   = self.xi
        self.last_y   = self.yi
        self.last_z   = 0.0
        self.last_yaw = 0.0

        self.carga_desired = None

        self.rt = 50.0
        self.dt = 1.0 / self.rt

        # ── Publishers / Subscribers ──────────────────────────────────
        self.pub = rospy.Publisher('cmd_full', Full, queue_size=1)
        rospy.Subscriber('/joy', Joy, self.joy_callback)
        rospy.Subscriber('/carga/desired_pose', PoseStamped,
                         self.carga_desired_callback)

        my_vrpn = rospy.get_param("~my_vrpn_topic", "")
        if my_vrpn:
            rospy.Subscriber(my_vrpn, PoseStamped, self.my_pose_callback)
        else:
            rospy.logwarn("[TRANSPORTADOR] my_vrpn_topic no configurado.")
            self.optitrack_ready = True

    # ── Callbacks ─────────────────────────────────────────────────────
    def joy_callback(self, msg):
        if msg.buttons[2] == 1 and self.state == IDLE:
            if not self.optitrack_ready:
                rospy.logwarn("[TRANSPORTADOR] OptiTrack no listo.")
                return
            self.takeoff_x  = self.my_x
            self.takeoff_y  = self.my_y
            self.takeoff_zi = self.my_z
            rospy.loginfo(
                f"[TRANSPORTADOR] Ascenso desde "
                f"({self.takeoff_x:.3f}, {self.takeoff_y:.3f}, "
                f"{self.takeoff_zi:.3f}) z_safe={self.z_safe} m")
            self.state      = ASCENT
            self.start_time = rospy.Time.now()

        elif msg.buttons[10] == 1 and self.state != IDLE:
            rospy.loginfo("[TRANSPORTADOR] Cancelacion manual -> aterrizando.")
            self.state = LANDING

    def carga_desired_callback(self, msg):
        self.carga_desired = msg

    def my_pose_callback(self, msg):
        self.my_x = msg.pose.position.x
        self.my_y = msg.pose.position.y
        self.my_z = msg.pose.position.z
        self.optitrack_ready = True

    # ── Lógica principal ──────────────────────────────────────────────
    def run(self):
        rate = rospy.Rate(self.rt)

        while not rospy.is_shutdown():
            full_msg = Full()
            full_msg.header.stamp = rospy.Time.now()

            # ══════════════════════════════════════════════════════════
            # FASE 1a — ASCENSO LIBRE EN Z
            # Sin ninguna corrección en X,Y.
            # ══════════════════════════════════════════════════════════
            if self.state == ASCENT:
                elapsed = (rospy.Time.now() - self.start_time).to_sec()

                z_cmd = self.z_safe * (1.0 - np.exp(-self.takeoff_rate * elapsed)) \
                        + self.takeoff_zi

                rospy.loginfo_throttle(
                    2.0, f"[ASCENT] z_real={self.my_z:.3f}  z_cmd={z_cmd:.3f}")

                # Transición cuando z_real se acerca a z_safe
                z_obj = self.z_safe + self.takeoff_zi
                if self.my_z >= (z_obj - 0.03):
                    rospy.loginfo(
                        f"[TRANSPORTADOR] Altura alcanzada "
                        f"(z={self.my_z:.3f} m). "
                        "Fase 1b: estabilizando X,Y suavemente...")
                    self.stabilize_start = rospy.Time.now()
                    self.state = STABILIZE

                # X,Y: setpoint fijo, sin corrección
                self._send(full_msg, self.takeoff_x, self.takeoff_y, z_cmd)

            # ══════════════════════════════════════════════════════════
            # FASE 1b — ESTABILIZACIÓN SUAVE EN X,Y
            # Solo regulador P con ganancia en rampa (0 → Kp en ramp_time).
            # Esto evita el escalón de corrección que causaba oscilaciones.
            # ══════════════════════════════════════════════════════════
            elif self.state == STABILIZE:
                z_obj   = self.z_safe + self.takeoff_zi
                t_stab  = (rospy.Time.now() - self.stabilize_start).to_sec()

                # Ganancia que crece linealmente de 0 a Kp_xy
                # en stab_ramp_time segundos
                kp_actual = self.Kp_xy * min(t_stab / self.stab_ramp_time, 1.0)

                ex = self.takeoff_x - self.my_x
                ey = self.takeoff_y - self.my_y

                # Solo término proporcional — sin derivativo
                x_cmd = self.takeoff_x + kp_actual * ex
                y_cmd = self.takeoff_y + kp_actual * ey

                # Saturar: máx 15 cm del punto inicial
                x_cmd = np.clip(x_cmd,
                                self.takeoff_x - 0.15,
                                self.takeoff_x + 0.15)
                y_cmd = np.clip(y_cmd,
                                self.takeoff_y - 0.15,
                                self.takeoff_y + 0.15)

                err_xy = np.sqrt(ex**2 + ey**2)
                rospy.loginfo_throttle(
                    1.0, f"[STABILIZE] kp={kp_actual:.2f}  "
                         f"ex={ex:.3f}  ey={ey:.3f}  err_xy={err_xy:.3f}")

                # Transición a Fase 2 cuando X,Y estabilizados
                # y la rampa ya llegó a ganancia completa (t > ramp_time)
                if err_xy < self.xy_stable_thr and t_stab > self.stab_ramp_time:
                    rospy.loginfo(
                        f"[TRANSPORTADOR] X,Y estabilizados "
                        f"(err_xy={err_xy:.3f} m). "
                        "Fase 2: yendo a posicion de formacion.")
                    self.state = GOTO_FORM

                self._send(full_msg, x_cmd, y_cmd, z_obj)

            # ══════════════════════════════════════════════════════════
            # FASE 2 — IR A POSICIÓN DE FORMACIÓN
            # ══════════════════════════════════════════════════════════
            elif self.state == GOTO_FORM:
                if self.carga_desired is None:
                    rospy.logwarn_throttle(
                        2, "[TRANSPORTADOR] Esperando /carga/desired_pose...")
                    rate.sleep()
                    continue

                xc = self.carga_desired.pose.position.x
                yc = self.carga_desired.pose.position.y
                zc = self.carga_desired.pose.position.z

                target_x = xc + self.Ci[0]
                target_y = yc + self.Ci[1]
                target_z = zc + self.Ci[2]

                err = np.sqrt((self.my_x - target_x)**2 +
                              (self.my_y - target_y)**2 +
                              (self.my_z - target_z)**2)

                rospy.loginfo_throttle(
                    2.0, f"[GOTO_FORM] err={err:.3f} m  "
                         f"target=({target_x:.3f},{target_y:.3f},{target_z:.3f})")

                if err < self.formation_thr:
                    rospy.loginfo(
                        f"[TRANSPORTADOR] Formacion alcanzada "
                        f"(err={err:.3f} m). Fase 3: siguiendo carga.")
                    self.state = FOLLOWING

                self._send(full_msg, target_x, target_y, target_z)

            # ══════════════════════════════════════════════════════════
            # FASE 3 — SEGUIMIENTO DE TRAYECTORIA
            # ══════════════════════════════════════════════════════════
            elif self.state == FOLLOWING:
                if self.carga_desired is None:
                    rospy.logwarn_throttle(
                        2, "[TRANSPORTADOR] Perdi /carga/desired_pose...")
                    rate.sleep()
                    continue

                xc = self.carga_desired.pose.position.x
                yc = self.carga_desired.pose.position.y
                zc = self.carga_desired.pose.position.z

                target_x = xc + self.Ci[0]
                target_y = yc + self.Ci[1]
                target_z = zc + self.Ci[2]

                if zc < 0.08:
                    rospy.loginfo(
                        "[TRANSPORTADOR] Carga en suelo. Aterrizando.")
                    self.state  = LANDING
                    self.last_x = target_x
                    self.last_y = target_y
                    self.last_z = target_z
                    rate.sleep()
                    continue

                self._send(full_msg, target_x, target_y, target_z)

            # ══════════════════════════════════════════════════════════
            # ATERRIZAJE SUAVE
            # ══════════════════════════════════════════════════════════
            elif self.state == LANDING:
                self.last_z -= 0.2 * self.dt

                if self.last_z <= 0.05:
                    self.last_z = 0.0
                    self.state  = IDLE
                    rospy.loginfo("[TRANSPORTADOR] En suelo. IDLE.")
                    stop = Full()
                    stop.twist1.linear.x = self.last_x
                    stop.twist1.linear.y = self.last_y
                    stop.twist1.linear.z = 0.0
                    self.pub.publish(stop)
                else:
                    self._send(full_msg,
                               self.last_x, self.last_y, self.last_z)

            elif self.state == IDLE:
                pass

            rate.sleep()

    # ── Helper ────────────────────────────────────────────────────────
    def _send(self, full_msg, x, y, z, yaw=0.0):
        full_msg.twist1.linear.x  = x
        full_msg.twist1.linear.y  = y
        full_msg.twist1.linear.z  = z
        full_msg.twist1.angular.x = 0.0
        full_msg.twist1.angular.y = 0.0
        full_msg.twist1.angular.z = 0.0
        full_msg.twist2.angular.x = yaw
        self.last_x, self.last_y   = x, y
        self.last_z, self.last_yaw = z, yaw
        self.pub.publish(full_msg)


if __name__ == '__main__':
    try:
        nodo = TransportadorDrone()
        nodo.run()
    except rospy.ROSInterruptException:
        pass