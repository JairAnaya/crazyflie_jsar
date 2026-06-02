#!/usr/bin/env python3
"""
Analiza un bag de hover y grafica las variables clave del controlador.

Uso:
    python3 plot_hover.py hover_20240101_120000.bag
"""
import sys
import numpy as np
import matplotlib.pyplot as plt

try:
    import rosbag
except ImportError:
    print("Instala rosbag: pip install rosbag")
    sys.exit(1)

if len(sys.argv) < 2:
    print(f"Uso: python3 {sys.argv[0]} archivo.bag")
    sys.exit(1)

bag_file = sys.argv[1]
print(f"Leyendo {bag_file} ...")

data = {
    't': [],
    'epos_x': [], 'epos_y': [], 'epos_z': [],
    'nu_x': [],   'nu_y': [],   'nu_z': [],
    'phi_star': [], 'theta_star': [],
    'eatt_x': [],  'eatt_y': [],
    'tau_x': [],   'tau_y': [],  'tau_z': [],
    's_x': [],     's_y': [],    's_z': [],
    'thrustSi': [],
    'pos_x': [], 'pos_y': [], 'pos_z': [],  # OptiTrack real
}

t0 = None
with rosbag.Bag(bag_file) as bag:
    for topic, msg, t in bag.read_messages():
        ts = t.to_sec()
        if t0 is None:
            t0 = ts
        ts -= t0

        if 'ctrlJair' in topic:
            # El log de cfclient viene como variables separadas
            for key in data:
                if key == 't' or key.startswith('pos_'):
                    continue
                try:
                    val = getattr(msg, key, None)
                    if val is not None:
                        data[key].append(val)
                        if len(data['t']) < len(data[key]):
                            data['t'].append(ts)
                except:
                    pass

        elif 'vrpn' in topic and 'crazyflie1' in topic:
            data['pos_x'].append(msg.pose.position.x)
            data['pos_y'].append(msg.pose.position.y)
            data['pos_z'].append(msg.pose.position.z)

# Convertir a arrays
for k in data:
    data[k] = np.array(data[k])

t = data['t']
if len(t) == 0:
    print("No se encontraron datos de ctrlJair en el bag.")
    print("Tópicos disponibles:")
    with rosbag.Bag(bag_file) as bag:
        for t_name, _, _ in bag.read_messages():
            print(f"  {t_name}")
    sys.exit(1)

print(f"Datos cargados: {len(t)} muestras, {t[-1]:.1f} segundos")

fig, axes = plt.subplots(3, 2, figsize=(14, 10))
fig.suptitle(f'Diagnóstico de Hover — {bag_file}', fontsize=12)

# Fila 1: Error de posición
ax = axes[0, 0]
if len(data['epos_x']) > 0:
    ax.plot(t[:len(data['epos_x'])], data['epos_x'], label='epos_x', color='r')
    ax.plot(t[:len(data['epos_y'])], data['epos_y'], label='epos_y', color='b')
ax.axhline(0, color='k', linestyle='--', linewidth=0.5)
ax.set_ylabel('Error posición [m]')
ax.set_title('Error XY')
ax.legend()
ax.grid(True)

ax = axes[0, 1]
if len(data['epos_z']) > 0:
    ax.plot(t[:len(data['epos_z'])], data['epos_z'], label='epos_z', color='g')
ax.axhline(0, color='k', linestyle='--', linewidth=0.5)
ax.set_ylabel('Error Z [m]')
ax.set_title('Error Z')
ax.legend()
ax.grid(True)

# Fila 2: Control virtual y referencias angulares
ax = axes[1, 0]
if len(data['nu_x']) > 0:
    ax.plot(t[:len(data['nu_x'])], data['nu_x'], label='nu_x [m/s²]', color='r')
    ax.plot(t[:len(data['nu_y'])], data['nu_y'], label='nu_y [m/s²]', color='b')
ax.axhline(0, color='k', linestyle='--', linewidth=0.5)
ax.set_ylabel('[m/s²]')
ax.set_title('Control virtual nu_x, nu_y')
ax.legend()
ax.grid(True)

ax = axes[1, 1]
if len(data['phi_star']) > 0:
    ax.plot(t[:len(data['phi_star'])],
            np.degrees(data['phi_star']), label='phi* [deg]', color='r')
    ax.plot(t[:len(data['theta_star'])],
            np.degrees(data['theta_star']), label='theta* [deg]', color='b')
    ax.plot(t[:len(data['eatt_x'])],
            np.degrees(data['eatt_x']), label='eatt_x [deg]', color='r',
            linestyle='--', alpha=0.5)
    ax.plot(t[:len(data['eatt_y'])],
            np.degrees(data['eatt_y']), label='eatt_y [deg]', color='b',
            linestyle='--', alpha=0.5)
ax.axhline(0, color='k', linestyle='--', linewidth=0.5)
ax.set_ylabel('[deg]')
ax.set_title('Referencias angulares vs error de actitud')
ax.legend(fontsize=7)
ax.grid(True)

# Fila 3: Superficie STSMC y torques
ax = axes[2, 0]
if len(data['s_x']) > 0:
    ax.plot(t[:len(data['s_x'])], data['s_x'], label='s_phi', color='r')
    ax.plot(t[:len(data['s_y'])], data['s_y'], label='s_theta', color='b')
    ax.axhline( 0.20, color='gray', linestyle=':', label='±delta_s')
    ax.axhline(-0.20, color='gray', linestyle=':')
ax.axhline(0, color='k', linestyle='--', linewidth=0.5)
ax.set_ylabel('[rad/s]')
ax.set_xlabel('Tiempo [s]')
ax.set_title('Superficie STSMC (|s|<delta_s = dentro de capa)')
ax.legend(fontsize=7)
ax.grid(True)

ax = axes[2, 1]
if len(data['tau_x']) > 0:
    ax.plot(t[:len(data['tau_x'])], np.array(data['tau_x'])*1000,
            label='tau_phi [mN·m]', color='r')
    ax.plot(t[:len(data['tau_y'])], np.array(data['tau_y'])*1000,
            label='tau_theta [mN·m]', color='b')
    ax.plot(t[:len(data['tau_z'])], np.array(data['tau_z'])*1000,
            label='tau_psi [mN·m]', color='g')
    ax.axhline( 7.9, color='gray', linestyle=':', label='±tau_max roll')
    ax.axhline(-7.9, color='gray', linestyle=':')
ax.axhline(0, color='k', linestyle='--', linewidth=0.5)
ax.set_ylabel('[mN·m]')
ax.set_xlabel('Tiempo [s]')
ax.set_title('Torques de control')
ax.legend(fontsize=7)
ax.grid(True)

plt.tight_layout()
outfile = bag_file.replace('.bag', '_diagnostico.png')
plt.savefig(outfile, dpi=150)
print(f"Gráfica guardada: {outfile}")
plt.show()