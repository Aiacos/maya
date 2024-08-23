import math
import maya.cmds as cmds

from adn.ui.widgets.dialogs import msg_box
import adn.tools.maya.locators as adn_locators
from adn.utils.maya.undo_stack import undo_chunk
from adn.utils.maya.checkers import plugin_check, world_matrix_plug_check


def copy_locator_connections_to_sensor(locator, sensor, plugs):
    """Copies all the connections the locator has on the sensor based on the plugs sent.

    Args:
        locator (str): Name of the locator from where source connections will be retrieved.
        sensor (str): Sensor that will recieve new connections.
        plugs (list): List of plugs to populate from locator to sensor.
    """
    for plug in plugs:
        str_plug = "{0}.{1}".format(locator, plug)
        connected_plug = cmds.connectionInfo(str_plug, isDestination=True)
        if not connected_plug:
            continue
        source = cmds.connectionInfo(str_plug, sourceFromDestination=True)
        cmds.connectAttr(source, "{0}.{1}".format(sensor, plug))

def connect_decompose_matrix(node, sensor, attribute):
    """Connect the decompose matrix connected to the node to the sensor sent. If decompose
    matrix not found will create one.

    Args:
        node (str): Node that should have connected a decompose matrix.
        sensor (str): Sensor that will be connected to a decompose matrix.
        attribute (str): Exact attribute to connect the matrix.
    """
    decompose_matrix = None
    node_connections = cmds.listConnections(node, type="decomposeMatrix")
    if node_connections:
        decompose_matrix = node_connections[0]
    else:
        decompose_matrix = cmds.createNode("decomposeMatrix")
        cmds.connectAttr("{0}.worldMatrix[0]".format(node), "{0}.inputMatrix".format(decompose_matrix))
    cmds.connectAttr("{0}.outputTranslate".format(decompose_matrix), "{0}.{1}".format(sensor, attribute))


@undo_chunk
def create_sensor_distance(custom_name=None):
    """Create a distance sensor that measures the distance between two specified points.
    Visually updates the AdnLocatorDistance locator selected.

    Args:
        custom_name (str, optional): Custom name to give to the sensor. Defaults to None.
    """
    plugin_check()
    # Check selection
    selection = cmds.ls(sl=True)
    num_nodes_selected = len(selection)
    wrong_selection_message = ("Wrong selection. Please, choose one of the following options and try again:"
                               "\n 1) Select the AdnLocatorDistance node associated. "
                               "\n 2) Select start and end point transform nodes."
                               "\n 3) Select start and end transform nodes plus the AdnLocatorDistance node "
                               "previously created.")
    if not selection or num_nodes_selected > 3 or not world_matrix_plug_check(selection):
        msg_box(None, "error", wrong_selection_message)
        return

    # Gather nodes
    locator_node = None
    start_node = None
    end_node = None
    # Only AdnLocatorDistance locator node selected
    if num_nodes_selected == 1:
        locator_node = selection[0]
        locator_shape = cmds.listRelatives(locator_node, shapes=True, fullPath=True)
        if not locator_shape or cmds.nodeType(locator_shape[0]) != "AdnLocatorDistance":
            msg_box(None, "error", wrong_selection_message)
            return
        locator_node = locator_shape[0]

        # Get Start and End nodes
        matrix_start = cmds.listConnections("{0}.startPosition".format(locator_node),
                                            type="decomposeMatrix")
        if matrix_start:
            start_node = cmds.listConnections("{0}.inputMatrix".format(matrix_start[0]))[0]

        matrix_end = cmds.listConnections("{0}.endPosition".format(locator_node),
                                          type="decomposeMatrix")
        if matrix_end:
            end_node = cmds.listConnections("{0}.inputMatrix".format(matrix_end[0]))[0]

    # Start and end points provided, locator and sensor will be created.
    elif num_nodes_selected == 2:
        locator_name = None if not custom_name else "{}Locator".format(custom_name)
        locator_node = adn_locators.create_locator_distance(locator_name, False)
        start_node = selection[0]
        end_node = selection[1]

    # All nodes provided
    elif num_nodes_selected == 3:
        start_node, end_node, locator_node = selection

        locator_shape = cmds.listRelatives(locator_node, shapes=True, fullPath=True)
        if not locator_shape or cmds.nodeType(locator_shape[0]) != "AdnLocatorDistance":
            msg_box(None, "error", wrong_selection_message)
            return
        locator_node = locator_shape[0]

    # Create sensor and make connections
    sensor_name = "adnSensorDistance1" if not custom_name else custom_name
    sensor = cmds.createNode("AdnSensorDistance", name=sensor_name)

    if start_node:
        # Start node found, use decompose matrix.
        connect_decompose_matrix(start_node, sensor, "startPosition")
    else:
        # Start node not found, use locator connections
        start_plugs = ["startPosition", "startPositionX", "startPositionY", "startPositionZ"]
        copy_locator_connections_to_sensor(locator_node, sensor, start_plugs)

    if end_node:
        # End node found, use decompose matrix.
        connect_decompose_matrix(end_node, sensor, "endPosition")
    else:
        # End node not found, use locator connections
        end_plugs = ["endPosition", "endPositionX", "endPositionY", "endPositionZ"]
        copy_locator_connections_to_sensor(locator_node, sensor, end_plugs)

    # Connect time attributes
    cmds.setAttr("{0}.startTime".format(sensor), cmds.currentTime(query=True))
    cmds.connectAttr("time1.outTime", "{0}.currentTime".format(sensor))

    # Remap nodes
    # Distance remap
    distance_remap = cmds.shadingNode("remapValue", asUtility=True, name="remapDistance")
    cmds.connectAttr("{0}.outDistance".format(sensor),
                     "{0}.inputValue".format(distance_remap))
    cmds.connectAttr("{0}.outValue".format(distance_remap),
                     "{0}.activationDistance".format(locator_node), force=True)
    # Inputs from initial distance to 0.0
    cmds.setAttr("{0}.inputMin".format(distance_remap),
                 cmds.getAttr("{0}.outDistance".format(sensor)))
    cmds.setAttr("{0}.inputMax".format(distance_remap), 0.0)
    # Outputs remapped to [0, 1]
    cmds.setAttr("{0}.outputMin".format(distance_remap), 0.0)
    cmds.setAttr("{0}.outputMax".format(distance_remap), 1.0)

    # Velocity remap
    distance_vel_remap = cmds.shadingNode("remapValue", asUtility=True, name="remapDistanceVel")
    cmds.connectAttr("{0}.outVelocity".format(sensor),
                     "{0}.inputValue".format(distance_vel_remap))
    cmds.connectAttr("{0}.outValue".format(distance_vel_remap),
                     "{0}.activationVelocity".format(locator_node), force=True)
    # Inputs in range [-10, 10] (this vel can be negative, expandable)
    cmds.setAttr("{0}.inputMin".format(distance_vel_remap), -10.0)
    cmds.setAttr("{0}.inputMax".format(distance_vel_remap), 10.0)
    # Outputs remapped to [0, 1]
    cmds.setAttr("{0}.outputMin".format(distance_vel_remap), 0.0)
    cmds.setAttr("{0}.outputMax".format(distance_vel_remap), 1.0)

    # Acceleration remap
    distance_accel_remap = cmds.shadingNode("remapValue", asUtility=True, name="remapDistanceAcc")
    cmds.connectAttr("{0}.outAcceleration".format(sensor),
                     "{0}.inputValue".format(distance_accel_remap))
    cmds.connectAttr("{0}.outValue".format(distance_accel_remap),
                     "{0}.activationAcceleration".format(locator_node), force=True)
    # Inputs in range [-10, 10] (accel can be negative, expandable)
    cmds.setAttr("{0}.inputMin".format(distance_accel_remap), -10.0)
    cmds.setAttr("{0}.inputMax".format(distance_accel_remap), 10.0)
    # Outputs remapped to [0, 1]
    cmds.setAttr("{0}.outputMin".format(distance_accel_remap), 0.0)
    cmds.setAttr("{0}.outputMax".format(distance_accel_remap), 1.0)

    # Select the sensor just created
    cmds.select(sensor)
    msg_box(None, "info",
            "\"{0}\" sensor has been created successfully."
            "".format(sensor))


@undo_chunk
def create_sensor_position(custom_name=None):
    """Create a position sensor that measures the position change of the locator.
    Visually updates the AdnLocatorPosition locator selected.

    Args:
        custom_name (str, optional): Custom name to give to the sensor. Defaults to None.
    """
    plugin_check()
    # Check selection
    selection = cmds.ls(sl=True)
    num_nodes_selected = len(selection)
    wrong_selection_message = ("Wrong selection. Please, choose one of the following options and try again:"
                               "\n 1) Select the AdnLocatorPosition node associated. "
                               "\n 2) Select the position transform node."
                               "\n 3) Select the position transform node plus the AdnLocatorPosition node "
                               "previously created")
    if not selection or num_nodes_selected > 2 or not world_matrix_plug_check(selection):
        msg_box(None, "error", wrong_selection_message)
        return

    # Gather nodes
    locator_node = None
    position_node = None
    # Only AdnLocatorPosition locator or only node selected
    if num_nodes_selected == 1:
        locator_node = selection[0]
        locator_shape = cmds.listRelatives(locator_node, shapes=True, fullPath=True)
        if not locator_shape or cmds.nodeType(locator_shape[0]) != "AdnLocatorPosition":
            # Locator not found, create it
            locator_name = None if not custom_name else "{}Locator".format(custom_name)
            locator_node = adn_locators.create_locator_position(locator_name, False)
        else:
            # Locator found
            locator_node = locator_shape[0]

        # Get position node nodes
        matrix_node = cmds.listConnections("{0}.position".format(locator_node),
                                           type="decomposeMatrix")
        if matrix_node:
            position_node = cmds.listConnections("{0}.inputMatrix".format(matrix_node[0]))[0]

    # Position node and locator provided
    elif num_nodes_selected == 2:
        position_node = selection[0]
        locator_node = selection[1]

        locator_shape = cmds.listRelatives(locator_node, shapes=True, fullPath=True)
        if not locator_shape or cmds.nodeType(locator_shape[0]) != "AdnLocatorPosition":
            msg_box(None, "error", wrong_selection_message)
            return

        locator_node = locator_shape[0]

    # Create sensor and make connections
    sensor_name = "adnSensorPosition1" if not custom_name else custom_name
    sensor = cmds.createNode("AdnSensorPosition", name=sensor_name)

    if position_node:
        # Position node found, use decompose matrix
        connect_decompose_matrix(position_node, sensor, "position")
    else:
        # Position node not found, use locator connections
        position_plugs = ["position", "positionX", "positionY", "positionZ"]
        copy_locator_connections_to_sensor(locator_node, sensor, position_plugs)

    # Connect time attributes
    cmds.setAttr("{0}.startTime".format(sensor), cmds.currentTime(query=True))
    cmds.connectAttr("time1.outTime", "{0}.currentTime".format(sensor))

    # Remap nodes
    # Velocity remap
    pos_vel_remap = cmds.shadingNode("remapValue", asUtility=True, name="remapPositionVel")
    cmds.connectAttr("{0}.outVelocity".format(sensor),
                     "{0}.inputValue".format(pos_vel_remap))
    cmds.connectAttr("{0}.outValue".format(pos_vel_remap),
                     "{0}.activationVelocity".format(locator_node), force=True)
    # Inputs in range [0, 10] (this vel can't be negative, expandable)
    cmds.setAttr("{0}.inputMin".format(pos_vel_remap), 0.0)
    cmds.setAttr("{0}.inputMax".format(pos_vel_remap), 10.0)
    # Outputs remapped to [0, 1]
    cmds.setAttr("{0}.outputMin".format(pos_vel_remap), 0.0)
    cmds.setAttr("{0}.outputMax".format(pos_vel_remap), 1.0)

    # Acceleration remap
    pos_accel_remap = cmds.shadingNode("remapValue", asUtility=True, name="remapPositionAcc")
    cmds.connectAttr("{0}.outAcceleration".format(sensor),
                     "{0}.inputValue".format(pos_accel_remap))
    cmds.connectAttr("{0}.outValue".format(pos_accel_remap),
                     "{0}.activationAcceleration".format(locator_node), force=True)
    # Inputs in range [-10, 10] (accel can be negative, expandable)
    cmds.setAttr("{0}.inputMin".format(pos_accel_remap), -10.0)
    cmds.setAttr("{0}.inputMax".format(pos_accel_remap), 10.0)
    # Outputs remapped to [0, 1]
    cmds.setAttr("{0}.outputMin".format(pos_accel_remap), 0.0)
    cmds.setAttr("{0}.outputMax".format(pos_accel_remap), 1.0)

    # Select the sensor just created
    cmds.select(sensor)
    msg_box(None, "info",
            "\"{0}\" sensor has been created successfully."
            "".format(sensor))


@undo_chunk
def create_sensor_rotation(custom_name=None):
    """Create a rotation sensor that measures the angle change of three points.
    Visually updates the AdnLocatorRotation locator selected.

    Args:
        custom_name (str, optional): Custom name to give to the sensor. Defaults to None.
    """
    plugin_check()
    # Check selection
    selection = cmds.ls(sl=True)
    num_nodes_selected = len(selection)
    wrong_selection_message = ("Wrong selection. Please, choose one of the following options and try again:"
                               "\n 1) Select the AdnLocatorRotation node associated. "
                               "\n 2) Select the three transform nodes in order."
                               "\n 3) Select the three transform nodes in order plus the AdnLocatorRotation node "
                               "previously created")
    if not selection or num_nodes_selected > 4 or num_nodes_selected == 2 or not world_matrix_plug_check(selection):
        msg_box(None, "error", wrong_selection_message)
        return

    # Gather nodes
    locator_node = None
    start_node = None
    mid_node = None
    end_node = None

    # Only AdnLocatorDistance locator node selected
    if num_nodes_selected == 1:
        locator_node = selection[0]
        locator_shape = cmds.listRelatives(locator_node, shapes=True, fullPath=True)
        if not locator_shape or cmds.nodeType(locator_shape[0]) != "AdnLocatorRotation":
            msg_box(None, "error", wrong_selection_message)
            return
        locator_node = locator_shape[0]

        # Get Start, Mid and End nodes
        matrix_start = cmds.listConnections("{0}.startPosition".format(locator_node),
                                            type="decomposeMatrix")
        if matrix_start:
            start_node = cmds.listConnections("{0}.inputMatrix".format(matrix_start[0]))[0]

        matrix_mid = cmds.listConnections("{0}.midPosition".format(locator_node),
                                          type="decomposeMatrix")
        if matrix_mid:
            mid_node = cmds.listConnections("{0}.inputMatrix".format(matrix_mid[0]))[0]

        matrix_end = cmds.listConnections("{0}.endPosition".format(locator_node),
                                          type="decomposeMatrix")
        if matrix_end:
            end_node = cmds.listConnections("{0}.inputMatrix".format(matrix_end[0]))[0]

    # Start, mid and end points provided, locator and sensor will be created.
    elif num_nodes_selected == 3:
        locator_name = None if not custom_name else "{}Locator".format(custom_name)
        locator_node = adn_locators.create_locator_rotation(locator_name, False)
        start_node = selection[0]
        mid_node = selection[1]
        end_node = selection[2]

    # All nodes provided
    elif num_nodes_selected == 4:
        start_node, mid_node, end_node, locator_node = selection

        locator_shape = cmds.listRelatives(locator_node, shapes=True, fullPath=True) 
        if not locator_shape or cmds.nodeType(locator_shape[0]) != "AdnLocatorRotation":
            msg_box(None, "error", wrong_selection_message)
            return
        locator_node = locator_shape[0]

    # Create sensor and make connections
    sensor_name = "adnSensorRotation1" if not custom_name else custom_name
    sensor = cmds.createNode("AdnSensorRotation", name=sensor_name)

    if start_node:
        # Start node found, use decompose matrix.
        connect_decompose_matrix(start_node, sensor, "startPosition")
    else:
        # Start node not found, use locator connections
        start_plugs = ["startPosition", "startPositionX", "startPositionY", "startPositionZ"]
        copy_locator_connections_to_sensor(locator_node, sensor, start_plugs)

    if mid_node:
        # Mid node found, use decompose matrix.
        connect_decompose_matrix(mid_node, sensor, "midPosition")
    else:
        # Mid node not found, use locator connections
        mid_plugs = ["midPosition", "midPositionX", "midPositionY", "midPositionZ"]
        copy_locator_connections_to_sensor(locator_node, sensor, mid_plugs)

    if end_node:
        # End node found, use decompose matrix.
        connect_decompose_matrix(end_node, sensor, "endPosition")
    else:
        # End node not found, use locator connections
        end_plugs = ["endPosition", "endPositionX", "endPositionY", "endPositionZ"]
        copy_locator_connections_to_sensor(locator_node, sensor, end_plugs)

    # Connect time attributes
    cmds.setAttr("{0}.startTime".format(sensor), cmds.currentTime(query=True))
    cmds.connectAttr("time1.outTime", "{0}.currentTime".format(sensor))

    # Remap nodes
    # Angle remap
    angle_remap = cmds.shadingNode("remapValue", asUtility=True,
                                    name="remapAngle")
    cmds.connectAttr("{0}.outAngle".format(sensor),
                     "{0}.inputValue".format(angle_remap))
    cmds.connectAttr("{0}.outValue".format(angle_remap),
                     "{0}.activationAngle".format(locator_node), force=True)
    cmds.setAttr("{0}.inputMin".format(angle_remap),
                  cmds.getAttr("{0}.outAngle".format(sensor)))
    cmds.setAttr("{0}.inputMax".format(angle_remap), 0.0)
    # Inputs in range [PI, 0] (angle can't be negative)
    # The smaller the angle is, the greater the output value is
    cmds.setAttr("{0}.inputMin".format(angle_remap), math.pi)
    cmds.setAttr("{0}.inputMax".format(angle_remap), 0.0)
    # Outputs remapped to [0, 1]
    cmds.setAttr("{0}.outputMin".format(angle_remap), 0.0)
    cmds.setAttr("{0}.outputMax".format(angle_remap), 1.0)

    # Velocity remap
    angle_vel_remap = cmds.shadingNode("remapValue", asUtility=True,
                                        name="remapAngleVel")
    cmds.connectAttr("{0}.outVelocity".format(sensor),
                     "{0}.inputValue".format(angle_vel_remap))
    cmds.connectAttr("{0}.outValue".format(angle_vel_remap),
                     "{0}.activationVelocity".format(locator_node), force=True)
    # Inputs in range [10, -10] (vel can be negative, expandable)
    # Negative if the angle is increasing
    # Positive if the angle is decreasing
    cmds.setAttr("{0}.inputMin".format(angle_vel_remap), 10.0)
    cmds.setAttr("{0}.inputMax".format(angle_vel_remap), -10.0)
    # Outputs remapped to [0, 1]
    cmds.setAttr("{0}.outputMin".format(angle_vel_remap), 0.0)
    cmds.setAttr("{0}.outputMax".format(angle_vel_remap), 1.0)

    angle_accel_remap = cmds.shadingNode("remapValue", asUtility=True,
                                         name="remapAngleAcc")
    cmds.connectAttr("{0}.outAcceleration".format(sensor),
                     "{0}.inputValue".format(angle_accel_remap))
    cmds.connectAttr("{0}.outValue".format(angle_accel_remap),
                     "{0}.activationAcceleration".format(locator_node), force=True)
    # Inputs in range [10, -10] (accel can be negative, expandable)
    cmds.setAttr("{0}.inputMin".format(angle_accel_remap), 10.0)
    cmds.setAttr("{0}.inputMax".format(angle_accel_remap), -10.0)
    # Outputs remapped to [0, 1]
    cmds.setAttr("{0}.outputMin".format(angle_accel_remap), 0.0)
    cmds.setAttr("{0}.outputMax".format(angle_accel_remap), 1.0)

    # Select the sensor just created
    cmds.select(sensor)
    msg_box(None, "info",
            "\"{0}\" sensor has been created successfully."
            "".format(sensor))
