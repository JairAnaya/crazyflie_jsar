#!/usr/bin/env python3
"""
guardar_experimento.py — Grabador de datos para experimento de transporte de carga.

Graba automáticamente desde que se lanza hasta Ctrl+C.
Guarda en ~/Experimentos/Carga/experimento_YYYYMMDD_HHMMSS.mat

=== LOGS DEL FIRMWARE (ctrlJair) ===
El controlador publica UN SOLO log group: ctrlJair
El driver de ROS lo publica como un tópico por variable en:
  /crazyflie1/ctrlJair/<nombre_variable>   (tipo Float32)

Variables disponibles en el firmware (controller_jair.c):
  thrustSi, phi_star, theta_star
  rpy_x/y/z       — ángulos Euler reales [rad]
  rpyd_x/y/z      — ángulos deseados [rad]
  epos_x/y/z      — error de posición [m]
  evel_x/y/z      — error de velocidad [m/s]
  eatt_x/y/z      — error de actitud [rad]
  erate_x/y/z     — error de velocidad angular [rad/s]
  s_x/y/z         — superficie SMC [rad/s]
  v_x/y/z         — integrador SMC [N·m]
  tau_x/y/z       — torques de control [N·m]
  nu_x/y/z        — control virtual de posición [m/s²]
  xidd_x/y/z      — aceleración de referencia [m/s²]
  dxi_x/y/z       — perturbación lineal estimada [m/s²]
  deta_x/y/z      — perturbación angular estimada [N·m]
  vel_kx/ky/kz    — velocidad Kalman [m/s]   ← NUEVO (requiere patch)
  vel_ox/oy/oz    — velocidad observador [m/s] ← NUEVO (requiere patch)
  pos_kx/ky/kz    — posición Kalman [m]       ← NUEVO (requiere patch)
  pos_ox/oy/oz    — posición observador [m]   ← NUEVO (requiere patch)

=== ESTRUCTURA DEL .mat ===
  t_vrpn          (N,1)   tiempo [s]
  pos_cf1/2/3     (N,3)   posición OptiTrack [x,y,z] m
  rpy_cf1/2/3     (N,3)   ángulos Euler OptiTrack [rad]
  vel_vrpn_cf1/2/3 (N,3)  velocidad derivada de OptiTrack [m/s]
  pos_carga       (N,3)   posición real de la carga [m]
  traj_desired    (N,3)   trayectoria deseada ξ_d(t) [m]
  error_carga     (N,3)   error de seguimiento [m]

  t_log           (M,1)   tiempo log firmware [s]
  — Por cada quad (cf1, cf2, cf3):
  thrustSi_cf*    (M,1)   empuje [N]
  tau_cf*         (M,3)   torques [N·m]
  epos_cf*        (M,3)   error posición firmware [m]
  evel_cf*        (M,3)   error velocidad firmware [m/s]
  eatt_cf*        (M,3)   error actitud [rad]
  erate_cf*       (M,3)   error vel. angular [rad/s]
  s_cf*           (M,3)   superficie SMC [rad/s]
  nu_cf*          (M,3)   control virtual posición [m/s²]
  dxi_cf*         (M,3)   perturbación lineal estimada [m/s²]
  deta_cf*        (M,3)   perturbación angular estimada [N·m]
  vel_k_cf*       (M,3)   velocidad Kalman [m/s]
  vel_o_cf*       (M,3)   velocidad observador [m/s]
  pos_k_cf*       (M,3)   posición Kalman [m]
  pos_o_cf*       (M,3)   posición observador [m]
  rpy_fw_cf*      (M,3)   ángulos Euler firmware [rad]
"""
import os
import numpy as np
import rospy
from datetime import datetime
from geometry_msgs.msg import PoseStamped, TwistStamped
from std_msgs.msg import Float32
from scipy import io
import tf.transformations as tft


# ══════════════════════════════════════════════════════════════════════
# Buffer de un quad: VRPN + todos los logs del firmware ctrlJair
# ══════════════════════════════════════════════════════════════════════
class QuadBuffer:
    def __init__(self, name, alpha_vel=0.7):
        self.name  = name
        self.alpha = alpha_vel

        # ── VRPN ──────────────────────────────────────────────────
        self.pos      = []   # [x, y, z] m
        self.rpy      = []   # [roll, pitch, yaw] rad
        self.vel_vrpn = []   # velocidad derivada filtrada

        self._prev_pos = None
        self._prev_t   = None
        self._vel_filt = np.zeros(3)

        # ── Firmware logs (Float32 individuales) ─────────────────
        # Escalares
        self.thrustSi = []

        # Vectores 3D — se acumulan por componente y se unen al guardar
        self._fw = {
            'tau':    [[], [], []],   # tau_x/y/z  [N·m]
            'epos':   [[], [], []],   # epos_x/y/z [m]
            'evel':   [[], [], []],   # evel_x/y/z [m/s]
            'eatt':   [[], [], []],   # eatt_x/y/z [rad]
            'erate':  [[], [], []],   # erate_x/y/z [rad/s]
            's':      [[], [], []],   # s_x/y/z    [rad/s]
            'nu':     [[], [], []],   # nu_x/y/z   [m/s²]
            'dxi':    [[], [], []],   # dxi_x/y/z  [m/s²]
            'deta':   [[], [], []],   # deta_x/y/z [N·m]
            'vel_k':  [[], [], []],   # vel_kx/y/z [m/s]
            'vel_o':  [[], [], []],   # vel_ox/y/z [m/s]
            'pos_k':  [[], [], []],   # pos_kx/y/z [m]
            'pos_o':  [[], [], []],   # pos_ox/y/z [m]
            'rpy_fw': [[], [], []],   # rpy_x/y/z  [rad]
        }

        self.log_ok = False

    # ── Callback VRPN ──────────────────────────────────────────────
    def cb_vrpn(self, msg):
        pos = np.array([msg.pose.position.x,
                        msg.pose.position.y,
                        msg.pose.position.z])
        q   = msg.pose.orientation
        rpy = tft.euler_from_quaternion([q.x, q.y, q.z, q.w])

        now = rospy.Time.now().to_sec()
        if self._prev_pos is not None and self._prev_t is not None:
            dt = now - self._prev_t
            if dt > 1e-4:
                raw = (pos - self._prev_pos) / dt
                self._vel_filt = (self.alpha * self._vel_filt
                                  + (1 - self.alpha) * raw)
        self._prev_pos = pos
        self._prev_t   = now

        self.pos.append(pos.tolist())
        self.rpy.append(list(rpy))
        self.vel_vrpn.append(self._vel_filt.tolist())

    # ── Callbacks de log firmware (Float32 individuales) ──────────
    def cb_thrust(self, msg):
        if not self.log_ok:
            rospy.loginfo(f"[RECORDER] Log firmware recibido de {self.name} ✓")
            self.log_ok = True
        self.thrustSi.append(msg.data)

    def _cb_vec(self, key, axis, msg):
        """Callback genérico para variable escalar que forma parte de un vector."""
        self._fw[key][axis].append(msg.data)

    # ── Exportar al dict del .mat ───────────────────────────────────
    def to_dict(self, suffix, n_vrpn):
        def a_vrpn(lst):
            if not lst:
                return np.zeros((n_vrpn, 3))
            arr = np.array(lst, dtype=np.float64)
            return _trim_pad(arr, n_vrpn, 3)

        d = {
            f'pos_{suffix}':      a_vrpn(self.pos),
            f'rpy_{suffix}':      a_vrpn(self.rpy),
            f'vel_vrpn_{suffix}': a_vrpn(self.vel_vrpn),
        }

        if self.log_ok:
            n_log = len(self.thrustSi)
            if n_log == 0:
                return d

            d[f'thrustSi_{suffix}'] = np.array(
                self.thrustSi, dtype=np.float64).reshape(-1, 1)

            # Etiquetas de los vectores firmware → sufijo en el .mat
            fw_labels = {
                'tau':    f'tau_{suffix}',
                'epos':   f'epos_{suffix}',
                'evel':   f'evel_{suffix}',
                'eatt':   f'eatt_{suffix}',
                'erate':  f'erate_{suffix}',
                's':      f's_{suffix}',
                'nu':     f'nu_{suffix}',
                'dxi':    f'dxi_{suffix}',
                'deta':   f'deta_{suffix}',
                'vel_k':  f'vel_k_{suffix}',
                'vel_o':  f'vel_o_{suffix}',
                'pos_k':  f'pos_k_{suffix}',
                'pos_o':  f'pos_o_{suffix}',
                'rpy_fw': f'rpy_fw_{suffix}',
            }
            for key, mat_name in fw_labels.items():
                cols = self._fw[key]
                # Longitud mínima de las tres componentes grabadas
                n = min(len(c) for c in cols) if all(cols) else 0
                if n == 0:
                    d[mat_name] = np.zeros((n_log, 3))
                else:
                    arr = np.column_stack([
                        np.array(cols[0][:n]),
                        np.array(cols[1][:n]),
                        np.array(cols[2][:n]),
                    ]).astype(np.float64)
                    d[mat_name] = _trim_pad(arr, n_log, 3)
        return d


def _trim_pad(arr, n, cols):
    """Ajusta arr a exactamente n filas."""
    if len(arr) >= n:
        return arr[:n]
    pad = np.zeros((n - len(arr), cols))
    return np.vstack([arr, pad])


# ══════════════════════════════════════════════════════════════════════
# Nodo principal
# ══════════════════════════════════════════════════════════════════════
class ExperimentRecorder:
    def __init__(self):
        rospy.init_node('guardar_experimento', anonymous=True)

        out_dir = os.path.expanduser(
            rospy.get_param("~output_dir", "~/Experimentos/Carga"))
        os.makedirs(out_dir, exist_ok=True)

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.mat_path = os.path.join(out_dir, f"experimento_{ts}.mat")

        rospy.loginfo(f"[RECORDER] Guardará en: {self.mat_path}")
        rospy.loginfo("[RECORDER] Grabando... Ctrl+C para guardar y salir.")

        self.t0 = None

        # ── Buffers ───────────────────────────────────────────────
        self.cf = {
            'cf1': QuadBuffer('crazyflie1'),
            'cf2': QuadBuffer('crazyflie2'),
            'cf3': QuadBuffer('crazyflie3'),
        }

        self.t_vrpn       = []
        self.pos_carga    = []
        self.traj_desired = []
        self.error_carga  = []
        self.t_log        = []
        self._log_t0      = None

        # ── Suscriptores VRPN ─────────────────────────────────────
        for ns, buf in [('crazyflie1', self.cf['cf1']),
                        ('crazyflie2', self.cf['cf2']),
                        ('crazyflie3', self.cf['cf3'])]:
            rospy.Subscriber(
                f'/vrpn_client_node/{ns}/pose',
                PoseStamped,
                lambda m, b=buf: self._cb_vrpn(m, b))

        carga_topic = rospy.get_param(
            "~carga_vrpn_topic", "/vrpn_client_node/carga/pose")
        rospy.Subscriber(carga_topic,      PoseStamped,  self._cb_carga)
        rospy.Subscriber('/trayectoria/desired_pose', PoseStamped,  self._cb_traj)
        rospy.Subscriber('/carga/position_error',     TwistStamped, self._cb_error)

        # ── Suscriptores firmware (Float32 individuales) ──────────
        # Mapeo: nombre_firmware → (clave_interna, eje)
        # El driver publica /crazyflie1/ctrlJair/tau_x etc.
        fw_map = {
            'thrustSi': None,          # escalar especial
            'tau_x':    ('tau',   0),
            'tau_y':    ('tau',   1),
            'tau_z':    ('tau',   2),
            'epos_x':   ('epos',  0),
            'epos_y':   ('epos',  1),
            'epos_z':   ('epos',  2),
            'evel_x':   ('evel',  0),
            'evel_y':   ('evel',  1),
            'evel_z':   ('evel',  2),
            'eatt_x':   ('eatt',  0),
            'eatt_y':   ('eatt',  1),
            'eatt_z':   ('eatt',  2),
            'erate_x':  ('erate', 0),
            'erate_y':  ('erate', 1),
            'erate_z':  ('erate', 2),
            's_x':      ('s',     0),
            's_y':      ('s',     1),
            's_z':      ('s',     2),
            'nu_x':     ('nu',    0),
            'nu_y':     ('nu',    1),
            'nu_z':     ('nu',    2),
            'dxi_x':    ('dxi',   0),
            'dxi_y':    ('dxi',   1),
            'dxi_z':    ('dxi',   2),
            'deta_x':   ('deta',  0),
            'deta_y':   ('deta',  1),
            'deta_z':   ('deta',  2),
            'vel_kx':   ('vel_k', 0),
            'vel_ky':   ('vel_k', 1),
            'vel_kz':   ('vel_k', 2),
            'vel_ox':   ('vel_o', 0),
            'vel_oy':   ('vel_o', 1),
            'vel_oz':   ('vel_o', 2),
            'pos_kx':   ('pos_k', 0),
            'pos_ky':   ('pos_k', 1),
            'pos_kz':   ('pos_k', 2),
            'pos_ox':   ('pos_o', 0),
            'pos_oy':   ('pos_o', 1),
            'pos_oz':   ('pos_o', 2),
            'rpy_x':    ('rpy_fw',0),
            'rpy_y':    ('rpy_fw',1),
            'rpy_z':    ('rpy_fw',2),
        }

        for ns, suf in [('crazyflie1','cf1'),
                        ('crazyflie2','cf2'),
                        ('crazyflie3','cf3')]:
            buf = self.cf[suf]
            for var, mapping in fw_map.items():
                topic = f'/{ns}/ctrlJair/{var}'
                if mapping is None:
                    # thrustSi — escalar
                    rospy.Subscriber(topic, Float32,
                                     lambda m, b=buf: b.cb_thrust(m))
                else:
                    key, axis = mapping
                    rospy.Subscriber(
                        topic, Float32,
                        lambda m, b=buf, k=key, ax=axis: self._cb_fw(m, b, k, ax))

        n_topics = len(fw_map) * 3
        rospy.loginfo(f"[RECORDER] Suscrito a {n_topics} tópicos firmware "
                      f"(ctrlJair). Si no llegan datos, verificar "
                      f"enable_logging=True y logs configurados en el launch.")

    # ── Callbacks ──────────────────────────────────────────────────
    def _get_t(self):
        now = rospy.Time.now().to_sec()
        if self.t0 is None:
            self.t0 = now
        return now - self.t0

    def _cb_vrpn(self, msg, buf):
        t = self._get_t()
        buf.cb_vrpn(msg)
        if buf is self.cf['cf1']:
            self.t_vrpn.append(t)

    def _cb_carga(self, msg):
        self._get_t()
        self.pos_carga.append([msg.pose.position.x,
                               msg.pose.position.y,
                               msg.pose.position.z])

    def _cb_traj(self, msg):
        self._get_t()
        self.traj_desired.append([msg.pose.position.x,
                                   msg.pose.position.y,
                                   msg.pose.position.z])

    def _cb_error(self, msg):
        self._get_t()
        self.error_carga.append([msg.twist.linear.x,
                                  msg.twist.linear.y,
                                  msg.twist.linear.z])

    def _cb_fw(self, msg, buf, key, axis):
        now = rospy.Time.now().to_sec()
        if self._log_t0 is None:
            self._log_t0 = now
        # El eje de tiempo del log lo lleva thrustSi (cb_thrust)
        buf._fw[key][axis].append(msg.data)

    # ── Guardado ───────────────────────────────────────────────────
    def save(self):
        n_vrpn = len(self.t_vrpn)
        if n_vrpn == 0:
            rospy.logwarn("[RECORDER] Sin datos VRPN — no se guardó nada.")
            return

        rospy.loginfo(f"[RECORDER] Guardando {n_vrpn} muestras VRPN "
                      f"→ {self.mat_path}")

        def arr_common(lst):
            if not lst:
                return np.zeros((n_vrpn, 3))
            a = np.array(lst, dtype=np.float64)
            return _trim_pad(a, n_vrpn, 3)

        mat = {
            't_vrpn':       np.array(self.t_vrpn).reshape(-1, 1),
            'pos_carga':    arr_common(self.pos_carga),
            'traj_desired': arr_common(self.traj_desired),
            'error_carga':  arr_common(self.error_carga),
        }

        for suf, buf in self.cf.items():
            mat.update(buf.to_dict(suf, n_vrpn))
            if buf.log_ok:
                n_log = len(buf.thrustSi)
                rospy.loginfo(f"[RECORDER]   {suf}: {n_log} muestras firmware")

        io.savemat(self.mat_path, mat)

        dur = self.t_vrpn[-1] if self.t_vrpn else 0
        rospy.loginfo(f"[RECORDER] ✓ Guardado. Duración: {dur:.1f} s")

        any_fw = any(b.log_ok for b in self.cf.values())
        if any_fw:
            rospy.loginfo("[RECORDER] Variables firmware incluidas: "
                          "thrustSi, tau, epos, evel, eatt, erate, s, nu, "
                          "dxi, deta, vel_k, vel_o, pos_k, pos_o, rpy_fw")
        else:
            rospy.logwarn("[RECORDER] Sin datos firmware. Verificar:")
            rospy.logwarn("[RECORDER]   1. enable_logging: True en el launch")
            rospy.logwarn("[RECORDER]   2. Logs ctrlJair configurados "
                          "(ver crazyflie_add.launch)")
            rospy.logwarn("[RECORDER]   3. Patch aplicado en controller_jair.c "
                          "para vel_k/vel_o/pos_k/pos_o")


if __name__ == '__main__':
    rec = ExperimentRecorder()
    rospy.on_shutdown(rec.save)
    rospy.spin()