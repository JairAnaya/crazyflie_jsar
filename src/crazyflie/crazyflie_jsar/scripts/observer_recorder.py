#!/usr/bin/env python3
"""
Nodo ROS para grabar datos del observador SM-FTO vs filtro Kalman.

Funciona en dos modos:
  MODO A (con LogBlocks): suscribe a /crazyflie1/log/ctrlJair_vel/pos/att
                          y graba vel_k, vel_o, dxi, tau, etc.
  MODO B (sin LogBlocks): calcula velocidad derivando VRPN con filtro IIR.
                          Siempre activo como respaldo.

El .mat resultante contiene siempre:
  t, pos_vrpn, vel_vrpn (derivada VRPN), rpy_vrpn
Y si los LogBlocks funcionaron también:
  vel_k, vel_o, pos_k, pos_o, dxi, epos, tau, s_smc, thrustSi

Uso:
  rosrun crazyflie_jsar observer_recorder.py _cf_name:=crazyflie1
  (o incluir en el launch — se guarda automáticamente al hacer Ctrl+C)
"""
import rospy
import os
import numpy as np
from datetime import datetime
from geometry_msgs.msg import PoseStamped
from scipy import io
import tf.transformations as tft


class ObserverRecorder:
    def __init__(self):
        rospy.init_node("observer_recorder", anonymous=True)

        self.cf_name = rospy.get_param("~cf_name", "crazyflie1")
        out_dir = rospy.get_param(
            "~output_dir",
            os.path.expanduser("~/Experimentos_Observer"))

        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.mat_path = os.path.join(out_dir, f"ObserverData_{ts}.mat")

        self.t0 = None

        # ── Buffers VRPN (siempre disponibles) ───────────────────
        self.t_vrpn    = []
        self.pos_vrpn  = []   # [x,y,z] m
        self.vel_vrpn  = []   # derivada filtrada [vx,vy,vz] m/s
        self.rpy_vrpn  = []   # [roll,pitch,yaw] rad

        # Estado del filtro de velocidad (IIR de primer orden)
        self._prev_pos  = None
        self._prev_t    = None
        self._vel_filt  = np.zeros(3)
        self._alpha_vel = 0.7   # suavizado: 0=sin filtro, 1=freezed

        # ── Buffers LogBlock (disponibles solo si el driver los publica) ─
        self.t_log     = []
        self.vel_k     = []
        self.vel_o     = []
        self.pos_k     = []
        self.pos_o     = []
        self.dxi       = []
        self.deta      = []
        self.epos      = []
        self.rpy_k     = []
        self.tau       = []
        self.s_smc     = []
        self.thrustSi  = []
        self._log_received = False

        # ── Suscriptores ──────────────────────────────────────────
        vrpn = f"/vrpn_client_node/{self.cf_name}/pose"
        rospy.Subscriber(vrpn, PoseStamped, self.cb_vrpn)

        # LogBlocks (opcionales — no fallan si no existen)
        try:
            from crazyflie_driver.msg import GenericLogData as GLD
            rospy.Subscriber(f"/{self.cf_name}/log/ctrlJair_vel",
                             GLD, self.cb_vel)
            rospy.Subscriber(f"/{self.cf_name}/log/ctrlJair_pos",
                             GLD, self.cb_pos)
            rospy.Subscriber(f"/{self.cf_name}/log/ctrlJair_att",
                             GLD, self.cb_att)
            rospy.loginfo("[OBS_REC] crazyflie_driver encontrado — "
                          "esperando LogBlocks del firmware")
        except ImportError:
            rospy.logwarn("[OBS_REC] crazyflie_driver no disponible — "
                          "solo se grabará VRPN derivado")

        rospy.loginfo(f"[OBS_REC] VRPN:    {vrpn}")
        rospy.loginfo(f"[OBS_REC] LOG vel: /{self.cf_name}/log/ctrlJair_vel")
        rospy.loginfo(f"[OBS_REC] Guardará en: {self.mat_path}")
        rospy.loginfo("[OBS_REC] Ctrl+C para guardar y salir.")

    # ── Callback VRPN ─────────────────────────────────────────────
    def cb_vrpn(self, msg):
        now = rospy.Time.now().to_sec()
        if self.t0 is None:
            self.t0 = now

        pos = np.array([msg.pose.position.x,
                        msg.pose.position.y,
                        msg.pose.position.z])
        q   = msg.pose.orientation
        rpy = tft.euler_from_quaternion([q.x, q.y, q.z, q.w])

        # Velocidad por diferencia finita + filtro IIR
        if self._prev_pos is not None and self._prev_t is not None:
            dt = now - self._prev_t
            if dt > 1e-4:
                vel_raw = (pos - self._prev_pos) / dt
                self._vel_filt = (self._alpha_vel * self._vel_filt
                                  + (1 - self._alpha_vel) * vel_raw)
        self._prev_pos = pos
        self._prev_t   = now

        self.t_vrpn.append(now - self.t0)
        self.pos_vrpn.append(pos.tolist())
        self.vel_vrpn.append(self._vel_filt.tolist())
        self.rpy_vrpn.append(list(rpy))

    # ── Callbacks LogBlocks ───────────────────────────────────────
    def cb_vel(self, msg):
        """ctrlJair_vel: [vel_kx,vel_ky,vel_kz, vel_ox,vel_oy,vel_oz, dxi_x,dxi_y,dxi_z]"""
        v = msg.values
        if len(v) < 9:
            return
        now = rospy.Time.now().to_sec()
        if self.t0 is None:
            self.t0 = now
        if not self._log_received:
            rospy.loginfo("[OBS_REC] LogBlock ctrlJair_vel recibido ✓")
            self._log_received = True
        self.t_log.append(now - self.t0)
        self.vel_k.append([v[0], v[1], v[2]])
        self.vel_o.append([v[3], v[4], v[5]])
        self.dxi.append(  [v[6], v[7], v[8]])

    def cb_pos(self, msg):
        """ctrlJair_pos: [pos_kx/y/z, pos_ox/y/z, epos_x/y/z, thrustSi]"""
        v = msg.values
        if len(v) < 10:
            return
        self.pos_k.append(    [v[0], v[1], v[2]])
        self.pos_o.append(    [v[3], v[4], v[5]])
        self.epos.append(     [v[6], v[7], v[8]])
        self.thrustSi.append( v[9])

    def cb_att(self, msg):
        """ctrlJair_att: [rpy_x/y/z, tau_x/y/z, s_x/y/z]"""
        v = msg.values
        if len(v) < 9:
            return
        self.rpy_k.append(  [v[0], v[1], v[2]])
        self.tau.append(    [v[3], v[4], v[5]])
        self.s_smc.append(  [v[6], v[7], v[8]])
        self.deta.append(   [0.0,  0.0,  0.0])

    # ── Guardado ──────────────────────────────────────────────────
    def save(self):
        n_vrpn = len(self.t_vrpn)
        n_log  = len(self.t_log)

        if n_vrpn == 0:
            rospy.logwarn("[OBS_REC] Sin datos VRPN — no se guardó nada.")
            return

        def arr(lst, default_cols=3):
            if not lst:
                return np.zeros((n_vrpn, default_cols))
            return np.array(lst, dtype=np.float64)

        rospy.loginfo(f"[OBS_REC] Guardando {n_vrpn} muestras VRPN, "
                      f"{n_log} muestras log → {self.mat_path}")

        # Siempre presentes
        mat = {
            "t_vrpn":   np.array(self.t_vrpn, dtype=np.float64).reshape(-1, 1),
            "pos_vrpn": arr(self.pos_vrpn),
            "vel_vrpn": arr(self.vel_vrpn),   # velocidad derivada de VRPN
            "rpy_vrpn": arr(self.rpy_vrpn),
        }

        # Del LogBlock (si se recibieron)
        if n_log > 0:
            mat["t_log"]    = np.array(self.t_log).reshape(-1, 1)
            mat["vel_k"]    = arr(self.vel_k)
            mat["vel_o"]    = arr(self.vel_o)
            mat["dxi"]      = arr(self.dxi)
            mat["pos_k"]    = arr(self.pos_k)    if self.pos_k    else np.zeros((n_log, 3))
            mat["pos_o"]    = arr(self.pos_o)    if self.pos_o    else np.zeros((n_log, 3))
            mat["epos"]     = arr(self.epos)     if self.epos     else np.zeros((n_log, 3))
            mat["thrustSi"] = np.array(self.thrustSi).reshape(-1, 1) if self.thrustSi else np.zeros((n_log, 1))
            mat["rpy_k"]    = arr(self.rpy_k)   if self.rpy_k    else np.zeros((n_log, 3))
            mat["tau"]      = arr(self.tau)      if self.tau      else np.zeros((n_log, 3))
            mat["s_smc"]    = arr(self.s_smc)   if self.s_smc    else np.zeros((n_log, 3))
            rospy.loginfo("[OBS_REC] ✓ Datos del firmware incluidos (vel_k, vel_o, dxi...)")
        else:
            rospy.logwarn("[OBS_REC] Sin datos de LogBlock — "
                          "solo se guardó VRPN (pos_vrpn, vel_vrpn).")
            rospy.logwarn("[OBS_REC] Para obtener vel_k/vel_o, verificar que:")
            rospy.logwarn("[OBS_REC]   1. enable_logging=True en el launch")
            rospy.logwarn("[OBS_REC]   2. El parámetro /crazyflie1/logs está definido")
            rospy.logwarn("[OBS_REC]   3. Las variables ctrlJair.vel_kx etc. existen en el firmware")

        io.savemat(self.mat_path, mat)
        rospy.loginfo(f"[OBS_REC] ✓ Guardado: {self.mat_path}")
        rospy.loginfo(f"[OBS_REC]   Duración: {self.t_vrpn[-1]:.1f}s")


if __name__ == "__main__":
    recorder = ObserverRecorder()
    rospy.on_shutdown(recorder.save)
    rospy.spin()