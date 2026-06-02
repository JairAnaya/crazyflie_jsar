#!/usr/bin/env python3

import rospy
from crazyflie_driver.srv import UpdateParams

def update_parameters():
    rospy.init_node('update_params_node', anonymous=True)

    # 1. Obtener parámetros del .launch
    namespace = rospy.get_param('~frame', 'crazyflie1')
    controller_type = rospy.get_param('~n', 6)

    # Asegurar que el namespace tenga el formato correcto /nombre
    if not namespace.startswith('/'):
        namespace = '/' + namespace

    service_name = namespace + '/update_params'

    rospy.loginfo(f"Iniciando secuencia de actualización para {namespace}...")
    rospy.loginfo(f"Esperando a que el servicio {service_name} esté disponible (revisa la conexión de radio)...")

    try:
        rospy.wait_for_service(service_name, timeout=20)
        update_params = rospy.ServiceProxy(service_name, UpdateParams)

        rospy.set_param(namespace + "/stabilizer/estimator", 2) 
        rospy.set_param(namespace + "/stabilizer/controller", controller_type)
        
        rospy.set_param(namespace + "/locSrv/extPosStdDev", 1e-3)
        rospy.set_param(namespace + "/locSrv/extQuatStdDev", 0.05)

        rospy.loginfo(f"Enviando controlador índice {controller_type} al firmware...")
        update_params(["stabilizer/estimator", "stabilizer/controller", "locSrv/extPosStdDev"])
        
        rospy.sleep(0.5)

        rospy.set_param(namespace + "/kalman/resetEstimation", 1)
        update_params(["kalman/resetEstimation"])
        
        rospy.loginfo(f"{namespace} configurado con controlador {controller_type}.")

    except rospy.ROSException as e:
        rospy.logerr(f"Tiempo de espera agotado o error de ROS: {e}")
    except rospy.ServiceException as e:
        rospy.logerr(f"Fallo en la llamada al servicio: {e}")

if __name__ == '__main__':
    rospy.sleep(2)
    update_parameters()