#!/usr/bin/env python3

import rospy
from geometry_msgs.msg import PoseStamped
from crazyflie_driver.srv import UpdateParams

def smart_reset():
    rospy.init_node('smart_reset_node', anonymous=True)

    # Parámetros
    namespace = rospy.get_param('~frame', 'crazyflie1')
    controller_type = rospy.get_param('~n', 6)
    pose_topic = rospy.get_param('~pose_topic', '/vrpn_client_node/crazyflie1/pose')

    if not namespace.startswith('/'):
        namespace = '/' + namespace

    service_name = namespace + '/update_params'
    
    rospy.loginfo(f"[{namespace}] Esperando conexión con el servicio de parámetros...")
    rospy.wait_for_service(service_name)
    update_params = rospy.ServiceProxy(service_name, UpdateParams)

    # 1. Configurar Kalman y Controlador
    rospy.loginfo(f"[{namespace}] Configurando EKF (2) y Controlador ({controller_type})...")
    rospy.set_param(namespace + "/stabilizer/estimator", 2) 
    rospy.set_param(namespace + "/stabilizer/controller", controller_type)
    update_params(["stabilizer/estimator", "stabilizer/controller"])

    # 2. ESPERAR A OPTITRACK (La parte clave)
    rospy.loginfo(f"[{namespace}] Esperando datos válidos de Optitrack en: {pose_topic} ...")
    
    try:
        # Esperamos un mensaje (timeout de 10s para no bloquear eternamente)
        msg = rospy.wait_for_message(pose_topic, PoseStamped, timeout=10.0)
        
        pos = msg.pose.position
        rospy.loginfo(f"[{namespace}] Optitrack detectado.")
        rospy.loginfo(f"[{namespace}] INICIALIZANDO EN: X={pos.x:.3f}, Y={pos.y:.3f}, Z={pos.z:.3f}")

        # Opcional: Si tu firmware soporta 'kalman.initialX', se pueden setear aquí.
        # Pero el resetEstimation con datos llegando suele ser suficiente.

        # 3. Reiniciar el Filtro Kalman ahora que sabemos que hay datos
        rospy.sleep(0.2)
        rospy.set_param(namespace + "/kalman/resetEstimation", 1)
        update_params(["kalman/resetEstimation"])
        
        rospy.sleep(0.1)
        rospy.set_param(namespace + "/kalman/resetEstimation", 0) # Lo regresamos a 0
        update_params(["kalman/resetEstimation"])

        rospy.loginfo(f"[{namespace}] Filtro Kalman REINICIALIZADO y LISTO.")

    except rospy.ROSException:
        rospy.logerr(f"[{namespace}] ERROR: No se recibieron datos de Optitrack en 10 segundos.")
        rospy.logerr(f"[{namespace}] El drone volará a ciegas o con error de altura.")

if __name__ == '__main__':
    smart_reset()