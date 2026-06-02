#!/bin/bash
# Graba los logs del controlador durante el vuelo de hover.
# Ejecutar en una terminal separada MIENTRAS corre el launch.
#
# Uso:
#   chmod +x record_hover.sh
#   ./record_hover.sh
#
# Después del vuelo, analizar con:
#   python3 plot_hover.py hover_FECHA.bag

BAGFILE="hover_$(date +%Y%m%d_%H%M%S).bag"

echo "Grabando en $BAGFILE ..."
echo "Ctrl+C para detener la grabación"

rosbag record \
  /crazyflie1/log/ctrlJair \
  /vrpn_client_node/crazyflie1/pose \
  -O "$BAGFILE"