#!/usr/bin/env python3
"""
Graficar.py — Visualización de experimento de transporte de carga cooperativa.

Lee los archivos .mat generados por guardar_datos.py y produce:
  1. Trayectoria 3D  — carga deseada, carga real, quad 1, quad 2
  2. Posiciones X/Y/Z vs tiempo — carga deseada vs real, quad 1, quad 2
  3. Errores de formación  e_xi = pos_quad_i - pos_carga_real - Ci
  4. Ángulos de orientación phi y theta de cada quad

Uso:
  python3 Graficar.py                        # busca archivos en ~/Experimentos/
  python3 Graficar.py --dir /ruta/a/datos    # directorio personalizado
  python3 Graficar.py --sufijo PID           # sufijo del controlador (default: PID)

Estructura esperada de los .mat:
  Agente1_<sufijo>.mat  →  clave 'Quad1_data'
       columnas: x, y, z, psi, u, tau_phi, tau_theta, tau_psi, phi, theta
  Agente2_<sufijo>.mat  →  clave 'Quad2_data'   (mismas columnas)
  Carga_<sufijo>.mat    →  clave 'Carga_data'
       columnas: xc, yc, zc, xd, yd, zd, ex, ey, ez
"""

import argparse
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from mpl_toolkits.mplot3d import Axes3D          # noqa: F401
from scipy import io

# ══════════════════════════════════════════════════════════════════════
# Vectores de formación Ci (deben coincidir con los usados en el experimento)
# Para formación con 2 quads (triangular simplificada), l = 0.5 m, α = 45°:
#   L  = l·cos(45°) ≈ 0.3536 m
#   Zi = l·sin(45°) ≈ 0.3536 m
# Cambia estos valores si usaste una longitud de cable diferente.
# ══════════════════════════════════════════════════════════════════════
L  = 0.5 * np.cos(np.radians(45))   # ≈ 0.3536 m
Zi = 0.5 * np.sin(np.radians(45))   # ≈ 0.3536 m

C1 = np.array([-L,  0.0, Zi])
C2 = np.array([ L,  0.0, Zi])

# ══════════════════════════════════════════════════════════════════════
# Estilo global
# ══════════════════════════════════════════════════════════════════════
plt.rcParams.update({
    'font.size':        11,
    'axes.grid':        True,
    'grid.alpha':       0.35,
    'lines.linewidth':  1.5,
    'figure.dpi':       120,
})

COLOR_DES  = 'k'          # trayectoria deseada
COLOR_REAL = 'tab:green'  # carga real
COLOR_Q1   = 'tab:blue'   # quad 1
COLOR_Q2   = 'tab:red'    # quad 2


# ══════════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════════
def load_mat(path, key):
    """Carga un .mat y devuelve el array bajo 'key'. Aborta si no existe."""
    if not os.path.isfile(path):
        print(f"[ERROR] No se encontró: {path}")
        sys.exit(1)
    raw = io.loadmat(path)[key]
    return np.array(raw, dtype=float)


def make_time(n, dt=0.02):
    """Eje de tiempo en segundos (dt ≈ 50 Hz por defecto)."""
    return np.arange(n) * dt


# ══════════════════════════════════════════════════════════════════════
# Figura 1 — Trayectoria 3D
# ══════════════════════════════════════════════════════════════════════
def plot_3d(q1, q2, carga):
    fig = plt.figure(figsize=(9, 7))
    ax  = fig.add_subplot(111, projection='3d')

    xd, yd, zd = carga[:, 3], carga[:, 4], carga[:, 5]   # deseada
    xc, yc, zc = carga[:, 0], carga[:, 1], carga[:, 2]   # real

    # Trayectoria deseada de la carga (línea gruesa negra discontinua)
    ax.plot(xd, yd, zd, color=COLOR_DES, lw=2.0, ls='--',
            label='Carga deseada', zorder=5)

    # Trayectoria real de la carga
    ax.plot(xc, yc, zc, color=COLOR_REAL, lw=1.8,
            label='Carga real', zorder=4)

    # Quad 1
    ax.plot(q1[:, 0], q1[:, 1], q1[:, 2], color=COLOR_Q1,
            lw=1.4, ls='-', label='Quad 1', zorder=3)

    # Quad 2
    ax.plot(q2[:, 0], q2[:, 1], q2[:, 2], color=COLOR_Q2,
            lw=1.4, ls='-', label='Quad 2', zorder=3)

    # Puntos de inicio
    for pos, col, mk in [
        ([xd[0], yd[0], zd[0]], COLOR_DES,  'D'),
        ([xc[0], yc[0], zc[0]], COLOR_REAL, 'o'),
        (q1[0, :3],             COLOR_Q1,   's'),
        (q2[0, :3],             COLOR_Q2,   '^'),
    ]:
        ax.scatter(*pos, color=col, marker=mk, s=60, zorder=6)

    ax.set_xlabel('X [m]')
    ax.set_ylabel('Y [m]')
    ax.set_zlabel('Z [m]')
    ax.set_title('Trayectoria 3D — Transporte cooperativo de carga')
    ax.legend(loc='upper left', fontsize=9)
    fig.tight_layout()
    return fig


# ══════════════════════════════════════════════════════════════════════
# Figura 2 — Posiciones X, Y, Z vs tiempo
# ══════════════════════════════════════════════════════════════════════
def plot_positions(q1, q2, carga):
    n   = min(len(q1), len(q2), len(carga))
    t   = make_time(n)
    q1  = q1[:n];  q2 = q2[:n];  carga = carga[:n]

    fig, axes = plt.subplots(3, 1, figsize=(11, 8), sharex=True)
    labels = ['X [m]', 'Y [m]', 'Z [m]']

    for i, (ax, lbl) in enumerate(zip(axes, labels)):
        # Deseada (carga)
        ax.plot(t, carga[:, 3+i], color=COLOR_DES,  ls='--', lw=2.0,
                label='Carga deseada')
        # Real (carga)
        ax.plot(t, carga[:,   i], color=COLOR_REAL, lw=1.8,
                label='Carga real')
        # Quad 1 posición real
        ax.plot(t, q1[:, i],      color=COLOR_Q1,   lw=1.4,
                label='Quad 1')
        # Quad 2 posición real
        ax.plot(t, q2[:, i],      color=COLOR_Q2,   lw=1.4,
                label='Quad 2')

        ax.set_ylabel(lbl)
        if i == 0:
            ax.legend(loc='upper right', fontsize=9, ncol=2)

    axes[-1].set_xlabel('Tiempo [s]')
    axes[0].set_title('Posiciones — Carga deseada vs real vs Quads')
    fig.tight_layout()
    return fig


# ══════════════════════════════════════════════════════════════════════
# Figura 3 — Errores de formación e_ξi = pos_quad_i − pos_carga_real − Ci
# ══════════════════════════════════════════════════════════════════════
def plot_formation_errors(q1, q2, carga):
    n  = min(len(q1), len(q2), len(carga))
    t  = make_time(n)
    q1 = q1[:n];  q2 = q2[:n];  carga = carga[:n]

    # pos_carga_real
    xc, yc, zc = carga[:, 0], carga[:, 1], carga[:, 2]

    # Error de formación para cada quad
    e1 = np.column_stack([
        q1[:, 0] - xc - C1[0],   # ex1
        q1[:, 1] - yc - C1[1],   # ey1
        q1[:, 2] - zc - C1[2],   # ez1
    ])
    e2 = np.column_stack([
        q2[:, 0] - xc - C2[0],
        q2[:, 1] - yc - C2[1],
        q2[:, 2] - zc - C2[2],
    ])

    # Error de la carga respecto a la trayectoria deseada
    ec = carga[:, 6:9]   # ex, ey, ez  (guardados en recorder)

    fig, axes = plt.subplots(3, 1, figsize=(11, 8), sharex=True)
    ylabels = [r'$e_x$ [m]', r'$e_y$ [m]', r'$e_z$ [m]']

    for i, (ax, lbl) in enumerate(zip(axes, ylabels)):
        ax.plot(t, ec[:, i],   color=COLOR_REAL, lw=1.8, ls='-.',
                label='Error carga (real − deseada)')
        ax.plot(t, e1[:, i],   color=COLOR_Q1,   lw=1.4,
                label=r'$e_{\xi 1}$ (quad 1 − carga − $C_1$)')
        ax.plot(t, e2[:, i],   color=COLOR_Q2,   lw=1.4,
                label=r'$e_{\xi 2}$ (quad 2 − carga − $C_2$)')
        ax.axhline(0, color='grey', lw=0.8, ls=':')
        ax.set_ylabel(lbl)
        if i == 0:
            ax.legend(loc='upper right', fontsize=9)

    axes[-1].set_xlabel('Tiempo [s]')
    axes[0].set_title('Errores de formación')
    fig.tight_layout()
    return fig


# ══════════════════════════════════════════════════════════════════════
# Figura 4 — Ángulos de orientación phi y theta (ambos quads)
# ══════════════════════════════════════════════════════════════════════
def plot_angles(q1, q2):
    n  = min(len(q1), len(q2))
    t  = make_time(n)
    q1 = q1[:n];  q2 = q2[:n]

    # Convertir rad → grados
    # columnas: 8=phi, 9=theta, 3=psi
    phi1   = np.degrees(q1[:, 8])
    theta1 = np.degrees(q1[:, 9])
    psi1   = np.degrees(q1[:, 3])

    phi2   = np.degrees(q2[:, 8])
    theta2 = np.degrees(q2[:, 9])
    psi2   = np.degrees(q2[:, 3])

    fig, axes = plt.subplots(3, 2, figsize=(13, 9), sharex=True)
    angle_data = [
        (phi1,   phi2,   r'$\phi$ [°]',   'Alabeo'),
        (theta1, theta2, r'$\theta$ [°]', 'Cabeceo'),
        (psi1,   psi2,   r'$\psi$ [°]',   'Guiñada'),
    ]

    for row, (a1, a2, ylabel, title) in enumerate(angle_data):
        for col, (data, color, label) in enumerate([
            (a1, COLOR_Q1, 'Quad 1'),
            (a2, COLOR_Q2, 'Quad 2'),
        ]):
            ax = axes[row, col]
            ax.plot(t, data, color=color, lw=1.4)
            ax.axhline(0, color='grey', lw=0.8, ls=':')
            ax.set_ylabel(ylabel)
            if row == 0:
                ax.set_title(label)
            if row == 2:
                ax.set_xlabel('Tiempo [s]')

    axes[0, 0].annotate('Alabeo',   xy=(0.02, 0.88),
                        xycoords='axes fraction', fontsize=10)
    axes[1, 0].annotate('Cabeceo',  xy=(0.02, 0.88),
                        xycoords='axes fraction', fontsize=10)
    axes[2, 0].annotate('Guiñada',  xy=(0.02, 0.88),
                        xycoords='axes fraction', fontsize=10)

    fig.suptitle('Ángulos de orientación — Quads transportadores', fontsize=12)
    fig.tight_layout()
    return fig


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════
def main():
    parser = argparse.ArgumentParser(
        description='Graficar experimento de transporte de carga cooperativa.')
    parser.add_argument('--dir',    default=os.path.expanduser('~/Experimentos'),
                        help='Directorio con los archivos .mat')
    parser.add_argument('--sufijo', default='PID',
                        help='Sufijo del controlador (PID, Mellinger, JSAR, ...)')
    args = parser.parse_args()

    d = args.dir
    s = args.sufijo

    print(f"[GRAFICAR] Cargando datos desde: {d}  (sufijo: {s})")

    q1    = load_mat(os.path.join(d, f'Agente1_{s}.mat'), 'Quad1_data')
    q2    = load_mat(os.path.join(d, f'Agente2_{s}.mat'), 'Quad2_data')
    carga = load_mat(os.path.join(d, f'Carga_{s}.mat'),   'Carga_data')

    print(f"  Quad 1 : {q1.shape[0]} muestras")
    print(f"  Quad 2 : {q2.shape[0]} muestras")
    print(f"  Carga  : {carga.shape[0]} muestras")

    fig1 = plot_3d(q1, q2, carga)
    fig2 = plot_positions(q1, q2, carga)
    fig3 = plot_formation_errors(q1, q2, carga)
    fig4 = plot_angles(q1, q2)

    # Guardar figuras en el mismo directorio
    for fig, name in [
        (fig1, f'Trayectoria3D_{s}.png'),
        (fig2, f'Posiciones_{s}.png'),
        (fig3, f'Errores_{s}.png'),
        (fig4, f'Angulos_{s}.png'),
    ]:
        path = os.path.join(d, name)
        fig.savefig(path, bbox_inches='tight')
        print(f"  Guardada: {path}")

    plt.show()


if __name__ == '__main__':
    main()
