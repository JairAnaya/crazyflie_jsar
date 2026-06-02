#!/usr/bin/env python3
"""
transportadorseguidor.py — Quad transportador con trayectoria propia.

Cada quad sigue: ξ_di(t) = ξ_d(t) + Ci

SECUENCIA DE VUELO:
  ASCENT    → Todos los quads suben simultáneamente al presionar
              botón A. X,Y fijos a la posición real de OptiTrack
              congelada en ese instante. Sin corrección lateral.
              Termina cuando z_real >= z_safe - 0.04 m.

  STABILIZE → Regulador P con rampa de ganancia (0→Kp en
              stab_ramp_time s). Solo proporcional, sin derivativo.
              Termina cuando err_xy < xy_stable_thr Y tiempo > ramp.

  GOTO_INIT → Se mueve al punto inicial de su trayectoria ξ_d(0)+Ci.
              Termina cuando error 3D < formation_thr.

  FOLLOWING → Sigue ξ_d(t)+Ci en tiempo real.
"""
import numpy as np
import rospy
from geometry_msgs.msg import PoseStamped
from sensor_msgs.msg import Joy
from crazyflie.msg import Full

IDLE      = 0
ASCENT    = 1
STABILIZE = 2
GOTO_INIT = 3
FOLLOWING = 4
LANDING   = 5


class TransportadorSeguidor:
    def __init__(self):
        rospy.init_node('transportador_node', anonymous=True)

        # ── Posición inicial nominal ───────────────────────────────
        self.xi = rospy.get_param("~xi", 0.0)
        self.yi = rospy.get_param("~yi", 0.0)
        self.zi = rospy.get_param("~zi", 0.0)

        # ── Parámetros de trayectoria ─────────────────────────────
        self.xc = rospy.get_param("~xc", 0.0)
        self.yc = rospy.get_param("~yc", 0.0)
        self.zc = rospy.get_param("~zc", 0.0)
        self.h  = rospy.get_param("~h",  0.1)
        self.r  = rospy.get_param("~r",  0.2)
        self.trajectory_duration = rospy.get_param("~trajectory_duration", 60.0)

        # ── Vector de formación Ci ────────────────────────────────
        self.Ci = np.array([
            rospy.get_param("~ci_x", 0.0),
            rospy.get_param("~ci_y", 0.0),
            rospy.get_param("~ci_z", 0.189),
        ])
        rospy.loginfo(f"[TRANSPORTADOR] Ci = {self.Ci}")

        self.publica_trayectoria = rospy.get_param("~publica_trayectoria", False)

        # ── Parámetros de despegue ────────────────────────────────
        # z_safe: altura objetivo del despegue.
        # Con carga suspendida el quad llega a ~0.28-0.30 m con z_safe=0.35.
        # Bajar z_safe a lo que realmente alcanza el quad con el cable puesto.
        self.z_safe        = rospy.get_param("~z_safe",        0.28)
        self.takeoff_rate  = rospy.get_param("~takeoff_rate",  0.15)

        # ── Estabilización ────────────────────────────────────────
        self.Kp_xy          = rospy.get_param("~Kp_xy",          0.8)
        self.stab_ramp_time = rospy.get_param("~stab_ramp_time", 3.0)
        self.xy_stable_thr  = rospy.get_param("~xy_stable_thr",  0.04)

        # ── Formación ─────────────────────────────────────────────
        self.formation_thr = rospy.get_param("~formation_thr", 0.05)

        # ── Estado interno ────────────────────────────────────────
        self.state           = IDLE
        self.start_time      = None
        self.stabilize_start = None
        self.traj_start      = None

        # Posición congelada al presionar botón A
        self.takeoff_x  = self.xi
        self.takeoff_y  = self.yi
        self.takeoff_zi = self.zi

        # Posición real (OptiTrack)
        self.my_x = self.xi
        self.my_y = self.yi
        self.my_z = self.zi
        self.optitrack_ready = False

        # Último setpoint (para aterrizaje suave)
        self.last_x   = self.xi
        self.last_y   = self.yi
        self.last_z   = 0.0
        self.last_yaw = 0.0

        # Punto inicial de la trayectoria
        self.init_x = 0.0
        self.init_y = 0.0
        self.init_z = 0.0

        self.rt = 50.0
        self.dt = 1.0 / self.rt

        # ── Publishers / Subscribers ──────────────────────────────
        self.pub      = rospy.Publisher('cmd_full', Full, queue_size=1)
        self.pub_traj = rospy.Publisher(
            '/trayectoria/desired_pose', PoseStamped, queue_size=1)

        rospy.Subscriber('/joy', Joy, self.joy_callback)

        my_vrpn = rospy.get_param("~my_vrpn_topic", "")
        if my_vrpn:
            rospy.Subscriber(my_vrpn, PoseStamped, self.my_pose_callback)
        else:
            rospy.logwarn("[TRANSPORTADOR] my_vrpn_topic no configurado.")
            self.optitrack_ready = True

    # ── Callbacks ──────────────────────────────────────────────────
    def joy_callback(self, msg):
        if msg.buttons[2] == 1 and self.state == IDLE:
            if not self.optitrack_ready:
                rospy.logwarn("[TRANSPORTADOR] OptiTrack no listo.")
                return
            # Congelar posición real en el instante del botón A
            self.takeoff_x  = self.my_x
            self.takeoff_y  = self.my_y
            self.takeoff_zi = self.my_z
            rospy.loginfo(
                f"[TRANSPORTADOR] Ascenso desde "
                f"({self.takeoff_x:.3f}, {self.takeoff_y:.3f}, "
                f"{self.takeoff_zi:.3f})  z_safe={self.z_safe} m")
            self.state      = ASCENT
            self.start_time = rospy.Time.now()

        elif msg.buttons[10] == 1 and self.state != IDLE:
            rospy.loginfo("[TRANSPORTADOR] Cancelacion manual -> aterrizando.")
            self.state = LANDING

    def my_pose_callback(self, msg):
        self.my_x = msg.pose.position.x
        self.my_y = msg.pose.position.y
        self.my_z = msg.pose.position.z
        self.optitrack_ready = True

    # ── Trayectoria ξ_d(t) ─────────────────────────────────────────
    def compute_trajectory(self, t):
        w   = np.pi / 6
        p   = 15.0
        r_s = self.r * (np.arctan(p) + np.arctan(t - p))
        x   = r_s * np.cos(w * t) + self.xc
        y   = r_s * np.sin(w * t) + self.yc
        z   = (self.h / 2) * (1 + np.tanh(t - 2.5)) + self.zc
        return x, y, z

    # ── Lógica principal ───────────────────────────────────────────
    def run(self):
        rate = rospy.Rate(self.rt)

        while not rospy.is_shutdown():
            full_msg = Full()
            full_msg.header.stamp = rospy.Time.now()
            now = rospy.Time.now()

            # ══════════════════════════════════════════════════════
            # ASCENT — subida simultánea, X,Y fijos
            # ══════════════════════════════════════════════════════
            if self.state == ASCENT:
                elapsed = (now - self.start_time).to_sec()
                z_cmd   = self.z_safe * (1.0 - np.exp(-self.takeoff_rate * elapsed)) \
                          + self.takeoff_zi

                rospy.loginfo_throttle(
                    2.0, f"[ASCENT] z_real={self.my_z:.3f}  z_cmd={z_cmd:.3f}  "
                         f"ex={self.takeoff_x - self.my_x:.3f}  "
                         f"ey={self.takeoff_y - self.my_y:.3f}")

                # Transición: z_real cerca de z_safe
                # Tolerancia amplia (0.04) para que no dependa de
                # alcanzar exactamente z_safe con la carga puesta.
                z_obj = self.z_safe + self.takeoff_zi
                if self.my_z >= (z_obj - 0.04) and elapsed > 5.0:
                    rospy.loginfo(
                        f"[TRANSPORTADOR] Altura alcanzada "
                        f"(z={self.my_z:.3f} m). Estabilizando X,Y...")
                    self.stabilize_start = now
                    self.state = STABILIZE

                self._send(full_msg, self.takeoff_x, self.takeoff_y, z_cmd)

            # ══════════════════════════════════════════════════════
            # STABILIZE — regulador P con rampa
            # ══════════════════════════════════════════════════════
            elif self.state == STABILIZE:
                z_obj  = self.z_safe + self.takeoff_zi
                t_stab = (now - self.stabilize_start).to_sec()
                kp     = self.Kp_xy * min(t_stab / self.stab_ramp_time, 1.0)

                ex = self.takeoff_x - self.my_x
                ey = self.takeoff_y - self.my_y

                x_cmd = np.clip(self.takeoff_x + kp * ex,
                                self.takeoff_x - 0.15,
                                self.takeoff_x + 0.15)
                y_cmd = np.clip(self.takeoff_y + kp * ey,
                                self.takeoff_y - 0.15,
                                self.takeoff_y + 0.15)

                err_xy = np.sqrt(ex**2 + ey**2)
                rospy.loginfo_throttle(
                    1.0, f"[STABILIZE] kp={kp:.2f}  "
                         f"ex={ex:.3f}  ey={ey:.3f}  err_xy={err_xy:.3f}")

                if err_xy < self.xy_stable_thr and t_stab > self.stab_ramp_time:
                    xd0, yd0, zd0 = self.compute_trajectory(0.0)
                    self.init_x = xd0 + self.Ci[0]
                    self.init_y = yd0 + self.Ci[1]
                    self.init_z = zd0 + self.Ci[2]
                    rospy.loginfo(
                        f"[TRANSPORTADOR] X,Y estabilizados. "
                        f"Fase 2: yendo a "
                        f"({self.init_x:.3f},{self.init_y:.3f},{self.init_z:.3f})")
                    self.state = GOTO_INIT

                self._send(full_msg, x_cmd, y_cmd, z_obj)

            # ══════════════════════════════════════════════════════
            # GOTO_INIT — ir al punto inicial de la trayectoria
            # ══════════════════════════════════════════════════════
            elif self.state == GOTO_INIT:
                err = np.sqrt((self.my_x - self.init_x)**2 +
                              (self.my_y - self.init_y)**2 +
                              (self.my_z - self.init_z)**2)

                rospy.loginfo_throttle(
                    2.0, f"[GOTO_INIT] err={err:.3f} m  "
                         f"target=({self.init_x:.3f},{self.init_y:.3f},{self.init_z:.3f})")

                if err < self.formation_thr:
                    rospy.loginfo(
                        f"[TRANSPORTADOR] En posicion inicial "
                        f"(err={err:.3f} m). Fase 3: siguiendo trayectoria.")
                    self.traj_start = now
                    self.state = FOLLOWING

                self._send(full_msg, self.init_x, self.init_y, self.init_z)

            # ══════════════════════════════════════════════════════
            # FOLLOWING — seguimiento de trayectoria
            # ══════════════════════════════════════════════════════
            elif self.state == FOLLOWING:
                t = (now - self.traj_start).to_sec()

                if t >= self.trajectory_duration:
                    rospy.loginfo("[TRANSPORTADOR] Trayectoria finalizada. Aterrizando.")
                    self.state = LANDING
                    rate.sleep()
                    continue

                xd, yd, zd = self.compute_trajectory(t)
                target_x = xd + self.Ci[0]
                target_y = yd + self.Ci[1]
                target_z = zd + self.Ci[2]

                if self.publica_trayectoria:
                    desired = PoseStamped()
                    desired.header.stamp    = now
                    desired.header.frame_id = "world"
                    desired.pose.position.x = xd
                    desired.pose.position.y = yd
                    desired.pose.position.z = zd
                    self.pub_traj.publish(desired)

                self._send(full_msg, target_x, target_y, target_z)

            # ══════════════════════════════════════════════════════
            # LANDING — descenso suave
            # ══════════════════════════════════════════════════════
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
                    self._send(full_msg, self.last_x, self.last_y, self.last_z)

            elif self.state == IDLE:
                pass

            rate.sleep()

    # ── Helper ─────────────────────────────────────────────────────
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
        nodo = TransportadorSeguidor()
        nodo.run()
    except rospy.ROSInterruptException:
        pass