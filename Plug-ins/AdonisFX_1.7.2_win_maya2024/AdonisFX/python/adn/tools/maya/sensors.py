import math
import maya.cmds as cmds

import adn.tools.maya.locators as adn_locators
from adn.utils.maya.undo_stack import undo_chunk
from adn.utils.maya.checkers import plugin_check, world_matrix_plug_check
from adn.utils.constants import UiConstants


def get_sensor_locator_driver_node(node, matrix_plug, position_plug):
    """Get the driver node from a locator or sensor depending on the connection
    that had been made using the matrix or the position plug.
        - If the matrix plug has a connection return the node directly associated (joint, locator, etc).
        - If the position plug has a connection return the node associated to the
          'decomposeMatrix' that was attached to the plug (joint, locator, etc).

    Args:
        node (str): The locator or sensor node from which to extract the
            driver node from.
        matrix_plug (str): Matrix plug of the locator or sensor. Eg. 'endMatrix'.
        position_plug (str): Position plug of the locator or sensor. Eg. 'endPosition'.

    Returns:
        str: Returns the name of the driver node (joint, locator, etc).
            None if not found.
    """
    conn = cmds.listConnections("{0}.{1}".format(node, matrix_plug))
    if conn:
        return conn[0]

    matrix = cmds.listConnections("{0}.{1}".format(node, position_plug),
                                  type="decomposeMatrix")
    if not matrix:
        return None
    conn = cmds.listConnections("{0}.inputMatrix".format(matrix[0]))
    if not conn:
        return None

    return conn[0]


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
    cmds.connectAttr("{0}.outputTranslate".format(decompose_matrix), "{0}.{1}".format(sensor, attribute), force=True)


@undo_chunk
def create_sensor_distance(custom_name=None):
    """Create a distance sensor that measures the distance between two specified points.
    Visually updates the AdnLocatorDistance locator selected.

    Args:
        custom_name (str, optional): Custom name to give to the sensor. Defaults to None.

    Returns:
        bool: False if there was an error. True otherwise.
    """
    plugin_check()
    # Check selection
    selection = cmds.ls(sl=True)
    num_nodes_selected = len(selection)
    wrong_selection_message = ("Wrong selection. Please, choose one of the following options and try again: "
                               "1) Select the AdnLocatorDistance node associated, "
                               "2) Select start and end point transform nodes or "
                               "3) Select start and end transform nodes plus the AdnLocatorDistance node "
                               "previously created.")
    if not selection or num_nodes_selected > 3 or not world_matrix_plug_check(selection):
        print("{0} {1}".format(UiConstants.ERROR_PREFIX, wrong_selection_message))
        return False

    # Gather nodes
    locator_node = None
    start_node = None
    end_node = None
    # Only AdnLocatorDistance locator node selected
    if num_nodes_selected == 1:
        locator_node = selection[0]
        locator_shape = cmds.listRelatives(locator_node, shapes=True, fullPath=True)
        if not locator_shape or cmds.nodeType(locator_shape[0]) != "AdnLocatorDistance":
            print("{0} {1}".format(UiConstants.ERROR_PREFIX, wrong_selection_message))
            return False
        locator_node = locator_shape[0]

        # Get Start and End nodes
        start_node = get_sensor_locator_driver_node(locator_node, "startMatrix", "startPosition")
        end_node = get_sensor_locator_driver_node(locator_node, "endMatrix", "endPosition")

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
            print("{0} {1}".format(UiConstants.ERROR_PREFIX, wrong_selection_message))
            return False
        locator_node = locator_shape[0]

    # Create sensor and make connections
    sensor_name = "adnSensorDistance1" if not custom_name else custom_name
    sensor = cmds.createNode("AdnSensorDistance", name=sensor_name)

    if start_node:
        # Start node found, use matrix connections
        cmds.connectAttr("{0}.worldMatrix[0]".format(start_node),
                         "{0}.startMatrix".format(sensor))
    else:
        # Start node not found, use locator connections
        copy_locator_connections_to_sensor(locator_node, 
                                           sensor, 
                                           ["startMatrix"])

    if end_node:
        # End node found, use matrix connections
        cmds.connectAttr("{0}.worldMatrix[0]".format(end_node),
                         "{0}.endMatrix".format(sensor))
    else:
        # End node not found, use locator connections
        copy_locator_connections_to_sensor(locator_node, 
                                           sensor, 
                                           ["endMatrix"])

    # Connect time attributes
    cmds.setAttr("{0}.startTime".format(sensor), cmds.currentTime(query=True))
    cmds.connectAttr("time1.outTime", "{0}.currentTime".format(sensor))

    # Connect remapped distance to the locator
    cmds.connectAttr("{0}.outDistanceRemap".format(sensor),
                     "{0}.activationDistance".format(locator_node), force=True)
    # Inputs from initial distance to 0.0
    cmds.setAttr("{0}.inputMinDistance".format(sensor), cmds.getAttr("{0}.outDistance".format(sensor)))
    cmds.setAttr("{0}.inputMaxDistance".format(sensor), 0.0)
    # Outputs remapped to [0, 1]
    cmds.setAttr("{0}.outputMinDistance".format(sensor), 0.0)
    cmds.setAttr("{0}.outputMaxDistance".format(sensor), 1.0)

    # Connect remapped velocity to the locator
    cmds.connectAttr("{0}.outVelocityRemap".format(sensor),
                     "{0}.activationVelocity".format(locator_node), force=True)
    # Inputs in range [-10, 10] (this vel can be negative, expandable)
    cmds.setAttr("{0}.inputMinVelocity".format(sensor), -10.0)
    cmds.setAttr("{0}.inputMaxVelocity".format(sensor), 10.0)
    # Outputs remapped to [0, 1]
    cmds.setAttr("{0}.outputMinVelocity".format(sensor), 0.0)
    cmds.setAttr("{0}.outputMaxVelocity".format(sensor), 1.0)

    # Connect remapped acceleration to the locator
    cmds.connectAttr("{0}.outAccelerationRemap".format(sensor),
                     "{0}.activationAcceleration".format(locator_node), force=True)
    # Inputs in range [-10, 10] (accel can be negative, expandable)
    cmds.setAttr("{0}.inputMinAcceleration".format(sensor), -10.0)
    cmds.setAttr("{0}.inputMaxAcceleration".format(sensor), 10.0)
    # Outputs remapped to [0, 1]
    cmds.setAttr("{0}.outputMinAcceleration".format(sensor), 0.0)
    cmds.setAttr("{0}.outputMaxAcceleration".format(sensor), 1.0)

    # Select the sensor just created
    cmds.select(sensor)
    print("{0} \"{1}\" sensor has been created successfully."
          "".format(UiConstants.INFO_PREFIX, sensor))
    return True


@undo_chunk
def create_sensor_position(custom_name=None):
    """Create a position sensor that measures the position change of the locator.
    Visually updates the AdnLocatorPosition locator selected.

    Args:
        custom_name (str, optional): Custom name to give to the sensor. Defaults to None.

    Returns:
        bool: False if there was an error. True otherwise.
    """
    plugin_check()
    # Check selection
    selection = cmds.ls(sl=True)
    num_nodes_selected = len(selection)
    wrong_selection_message = ("Wrong selection. Please, choose one of the following options and try again: "
                               "1) Select the AdnLocatorPosition node associated, "
                               "2) Select the position transform node or "
                               "3) Select the position transform node plus the AdnLocatorPosition node "
                               "previously created.")
    if not selection or num_nodes_selected > 2 or not world_matrix_plug_check(selection):
        print("{0} {1}".format(UiConstants.ERROR_PREFIX, wrong_selection_message))
        return False

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

        # Get position node
        position_node = get_sensor_locator_driver_node(locator_node, "positionMatrix", "position")

    # Position node and locator provided
    elif num_nodes_selected == 2:
        position_node = selection[0]
        locator_node = selection[1]

        locator_shape = cmds.listRelatives(locator_node, shapes=True, fullPath=True)
        if not locator_shape or cmds.nodeType(locator_shape[0]) != "AdnLocatorPosition":
            print("{0} {1}".format(UiConstants.ERROR_PREFIX, wrong_selection_message))
            return False

        locator_node = locator_shape[0]

    # Create sensor and make connections
    sensor_name = "adnSensorPosition1" if not custom_name else custom_name
    sensor = cmds.createNode("AdnSensorPosition", name=sensor_name)

    if position_node:
        # Position node found, use matrix connections
        cmds.connectAttr("{0}.worldMatrix[0]".format(position_node), 
                         "{0}.positionMatrix".format(sensor))
    else:
        # Position node not found, use locator connections
        copy_locator_connections_to_sensor(locator_node, 
                                           sensor, 
                                           ["positionMatrix"])

    # Connect time attributes
    cmds.setAttr("{0}.startTime".format(sensor), cmds.currentTime(query=True))
    cmds.connectAttr("time1.outTime", "{0}.currentTime".format(sensor))

    # Connect remapped velocity to the locator
    cmds.connectAttr("{0}.outVelocityRemap".format(sensor),
                     "{0}.activationVelocity".format(locator_node), force=True)
    # Inputs in range [0, 10] (this vel can't be negative, expandable)
    cmds.setAttr("{0}.inputMinVelocity".format(sensor), 0.0)
    cmds.setAttr("{0}.inputMaxVelocity".format(sensor), 10.0)
    # Outputs remapped to [0, 1]
    cmds.setAttr("{0}.outputMinVelocity".format(sensor), 0.0)
    cmds.setAttr("{0}.outputMaxVelocity".format(sensor), 1.0)

    # Connect remapped acceleration to the locator
    cmds.connectAttr("{0}.outAccelerationRemap".format(sensor),
                     "{0}.activationAcceleration".format(locator_node), force=True)
    # Inputs in range [-10, 10] (accel can be negative, expandable)
    cmds.setAttr("{0}.inputMinAcceleration".format(sensor), -10.0)
    cmds.setAttr("{0}.inputMaxAcceleration".format(sensor), 10.0)
    # Outputs remapped to [0, 1]
    cmds.setAttr("{0}.outputMinAcceleration".format(sensor), 0.0)
    cmds.setAttr("{0}.outputMaxAcceleration".format(sensor), 1.0)

    # Select the sensor just created
    cmds.select(sensor)
    print("{0} \"{1}\" sensor has been created successfully."
          "".format(UiConstants.INFO_PREFIX, sensor))
    return True


@undo_chunk
def create_sensor_rotation(custom_name=None):
    """Create a rotation sensor that measures the angle change of three points.
    Visually updates the AdnLocatorRotation locator selected.

    Args:
        custom_name (str, optional): Custom name to give to the sensor. Defaults to None.

    Returns:
        bool: False if there was an error. True otherwise.
    """
    plugin_check()
    # Check selection
    selection = cmds.ls(sl=True)
    num_nodes_selected = len(selection)
    wrong_selection_message = ("Wrong selection. Please, choose one of the following options and try again: "
                               "1) Select the AdnLocatorRotation node associated, "
                               "2) Select the three transform nodes in order or"
                               "3) Select the three transform nodes in order plus the AdnLocatorRotation node "
                               "previously created.")
    if not selection or num_nodes_selected > 4 or num_nodes_selected == 2 or not world_matrix_plug_check(selection):
        print("{0} {1}".format(UiConstants.ERROR_PREFIX, wrong_selection_message))
        return False

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
            print("{0} {1}".format(UiConstants.ERROR_PREFIX, wrong_selection_message))
            return False
        locator_node = locator_shape[0]

        # Get Start, Mid, End nodes
        start_node = get_sensor_locator_driver_node(locator_node, "startMatrix", "startPosition")
        mid_node = get_sensor_locator_driver_node(locator_node, "midMatrix", "midPosition")
        end_node = get_sensor_locator_driver_node(locator_node, "endMatrix", "endPosition")

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
            print("{0} {1}".format(UiConstants.ERROR_PREFIX, wrong_selection_message))
            return False
        locator_node = locator_shape[0]

    # Create sensor and make connections
    sensor_name = "adnSensorRotation1" if not custom_name else custom_name
    sensor = cmds.createNode("AdnSensorRotation", name=sensor_name)

    if start_node:
        # Start node found, use matrix connections
        cmds.connectAttr("{0}.worldMatrix[0]".format(start_node), 
                         "{0}.startMatrix".format(sensor))
    else:
        # Start node not found, use locator connections
        copy_locator_connections_to_sensor(locator_node, 
                                           sensor, 
                                           ["startMatrix"])

    if mid_node:
        # Mid node found, use matrix connections
        cmds.connectAttr("{0}.worldMatrix[0]".format(mid_node), 
                         "{0}.midMatrix".format(sensor))
    else:
        # Mid node not found, use locator connections
        copy_locator_connections_to_sensor(locator_node, 
                                           sensor, 
                                           ["midMatrix"])

    if end_node:
        # End node found, use matrix connections
        cmds.connectAttr("{0}.worldMatrix[0]".format(end_node), 
                         "{0}.endMatrix".format(sensor))
    else:
        # End node not found, use locator connections
        copy_locator_connections_to_sensor(locator_node, 
                                           sensor, 
                                           ["endMatrix"])

    # Connect time attributes
    cmds.setAttr("{0}.startTime".format(sensor), cmds.currentTime(query=True))
    cmds.connectAttr("time1.outTime", "{0}.currentTime".format(sensor))

    # Connect remapped angle to the locator
    cmds.connectAttr("{0}.outAngleRemap".format(sensor),
                     "{0}.activationAngle".format(locator_node), force=True)
    # Inputs in range [PI, 0] (angle can't be negative)
    # The smaller the angle is, the greater the output value is
    cmds.setAttr("{0}.inputMinAngle".format(sensor), math.pi)
    cmds.setAttr("{0}.inputMaxAngle".format(sensor), 0.0)
    # Outputs remapped to [0, 1]
    cmds.setAttr("{0}.outputMinAngle".format(sensor), 0.0)
    cmds.setAttr("{0}.outputMaxAngle".format(sensor), 1.0)

    # Connect remapped velocity to the locator
    cmds.connectAttr("{0}.outVelocityRemap".format(sensor),
                     "{0}.activationVelocity".format(locator_node), force=True)
    # Inputs in range [10, -10] (vel can be negative, expandable)
    # Negative if the angle is increasing, positive if the angle is decreasing
    cmds.setAttr("{0}.inputMinVelocity".format(sensor), 10.0)
    cmds.setAttr("{0}.inputMaxVelocity".format(sensor), -10.0)
    # Outputs remapped to [0, 1]
    cmds.setAttr("{0}.outputMinVelocity".format(sensor), 0.0)
    cmds.setAttr("{0}.outputMaxVelocity".format(sensor), 1.0)

    # Connect remapped acceleration to the locator
    cmds.connectAttr("{0}.outAccelerationRemap".format(sensor),
                     "{0}.activationAcceleration".format(locator_node), force=True)
    # Inputs in range [10, -10] (accel can be negative, expandable)
    cmds.setAttr("{0}.inputMinAcceleration".format(sensor), 10.0)
    cmds.setAttr("{0}.inputMaxAcceleration".format(sensor), -10.0)
    # Outputs remapped to [0, 1]
    cmds.setAttr("{0}.outputMinAcceleration".format(sensor), 0.0)
    cmds.setAttr("{0}.outputMaxAcceleration".format(sensor), 1.0)

    # Select the sensor just created
    cmds.select(sensor)
    print("{0} \"{1}\" sensor has been created successfully."
          "".format(UiConstants.INFO_PREFIX, sensor))
    return True
