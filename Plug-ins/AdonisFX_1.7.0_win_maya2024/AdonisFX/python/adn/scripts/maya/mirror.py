import logging

import maya.cmds as cmds

from adn.ui.utils import cursor
from adn.utils.constants import DeformerTypes, LocatorTypes, SensorTypes, OtherNodeTypes
from adn.utils.maya.undo_stack import undo_chunk


def get_selected_muscles():
    """From the geometries in the current selection, returns a list with all the
    AdnMuscle or AdnRibbonMuscle deformers found in their history.

    Returns:
        list: List of all the AdnMuscle or AdnRibbonMuscle deformers found in the
            history of the selected geometries.
    """
    selection = cmds.ls(selection=True, dag=True, type="mesh")
    solvers = []
    for node in selection:
        node_muscles = get_muscle_deformer(node)
        if node_muscles:
            solvers += node_muscles
    return solvers


def get_muscles_in_scene():
    """Get all the AdnMuscle and AdnRibbonMuscle deformers in the scene.

    Returns:
        list: List of all the muscles in the scene.
    """
    return cmds.ls(type=[DeformerTypes.MUSCLE,
                         DeformerTypes.RIBBON])


def get_selected_locators():
    """Get the selected AdonisFX locators in the scene.

    Returns:
        list: List of the selected locators.
    """
    selection = cmds.ls(selection=True, dag=True, type=["locator"])
    selection = [x for x in selection if
                 cmds.nodeType(x) in [LocatorTypes.DISTANCE,
                                      LocatorTypes.ROTATION,
                                      LocatorTypes.POSITION]]
    return selection


def get_locators_in_scene():
    """Get all the AdonisFX locators in the scene.

    Returns:
        list: List of all the locators in the scene.
    """
    return cmds.ls(type=[LocatorTypes.DISTANCE,
                         LocatorTypes.ROTATION,
                         LocatorTypes.POSITION])


def report_naming_convention_error(name, left_convention, right_convention, report_data):
    """This function generates an error message if report_data is not None. It is
    meant to be used if get_mirror_name() returns None before creating a new node
    (e.g. it will be called when a sensor, locator, muscle to be created
    does not fulfill the naming convention).

    Args:
        name (str): The name of the node on the source side that does not
            fulfill the naming convention.
        left_convention (str): String parameter defining the naming convention.
        right_convention (str): String parameter defining the naming convention.
        report_data (dict): Dictionary to store the errors and warnings.
    """
    if report_data is None:
        return
    msg = ("Node \"{0}\" does not fulfill the naming convention. Please, "
           "make sure the name follows the convention \"{1}\" for left "
           "and \"{2}\" for right.".format(name, left_convention,
                                           right_convention))
    report_data["errors"].append(msg)


def report_mirror_connection_error(entity, source_node, attr, mirrored_node, report_data):
    """This function generates an error message if report_data is not None. It is
    meant to be used if get_mirror_name() returns something that does not exist
    before mirroring a connection (e.g. it will be called when the mirrored locator
    to be connected to the activation plug of a muscle does not exist).

    Args:
        entity (str): The name of the missing entity for which the connection
            could be mirrored
        source_node (str): The name of the node on the source side for which the
            connection is to be mirrored.
        attr (str): The name of the attribute referring to the connection to be
            mirrored.
        mirrored_node (str): The name of the node for which the connection could
            not be mirrored
        report_data (dict): Dictionary to store the errors and warnings.
    """
    if report_data is None:
        return
    msg = ("The connection \"{0}.{1}\" was not mirrored for \"{2}\" because the node "
           "or plug \"{3}\" does not exist or it was not mirrored."
           "").format(source_node, attr, mirrored_node, entity)
    report_data["errors"].append(msg)


def report_mirror_connection_warning(failed_to_mirror, mirrored_destination, attr, report_data):
    """This function generates a warning message if report_data is not None. It is
    meant to be used if get_mirror_name() returns None before mirroring a connection
    (e.g. it will be called for the muscle activation connection the source locator
    does not follow the naming convention).

    Args:
        failed_to_mirror (str): The name of the node on the source side that does not
            fulfill the naming convention.
        mirrored_destination (str): The name of the node for which the connection could
            not be mirrored.
        attr (str): The name of the attribute referring to the connection to be
            mirrored.
        report_data (dict): Dictionary to store the errors and warnings.
    """
    if report_data is None:
        return
    plug = "{0}.{1}".format(mirrored_destination, attr)
    msg  = ("\"{0}\" could not be mirrored because it does not follow the "
            "naming convention. \"{0}\" will be connected to \"{1}\".").format(failed_to_mirror, plug)
    report_data["warnings"].append(msg)


def get_mirror_name(node_name, left_convention, right_convention):
    """This function generates the mirror name of the provided node name.
    The method uses the provided conventions for left and right sides to
    generate the new name.

    Args:
        node_name (str): The name of the original node for which a new mirrored
            name is to be created.
        left_convention (str): String parameter defining the naming convention
            for left-side objects. The convention includes a '*' wildcard to
            define prefixes ('abc_*') or suffixes ('*_abc').
        right_convention (str): String parameter defining the naming convention
            for right-side objects. The convention includes a '*' wildcard to
            define prefixes ('abc_*') or suffixes ('*_abc').

    Returns:
        str: The mirrored node name.
    """
    mirror_name = None
    if left_convention[-1] == "*" and right_convention[-1] == "*":
        left = left_convention[:-1]
        right = right_convention[:-1]
        if node_name.startswith(left):
            mirror_name = "{0}{1}".format(right, node_name[len(left):])
        if node_name.startswith(right):
            mirror_name = "{0}{1}".format(left, node_name[len(right):])
    if left_convention[0] == "*" and right_convention[0] == "*":
        left = left_convention[1:]
        right = right_convention[1:]
        if node_name.endswith(left):
            mirror_name = "{0}{1}".format(node_name[:-len(left)], right)
        if node_name.endswith(right):
            mirror_name = "{0}{1}".format(node_name[:-len(right)], left)
    return mirror_name


def clear_connections(node, attribute, sub_attributes):
    """Clears all connections existing for a given node, attribute and children
    attributes. This is achieved by disconnecting any found connections.

    Args:
        node (str): The name of the node to have its connections cleared.
        attribute (str): The name of the attribute which connections have to
            be cleared.
        sub_attributes (list): List of names of children attributes to be
            cleared.
    """
    logical_indices = cmds.getAttr("{0}.{1}".format(node, attribute),
                                   multiIndices=True) or []
    for index in logical_indices:
        for sub_connection_name in sub_attributes:
            sub_connection_attribute = "{0}.{1}[{2}].{3}".format(node,
                                                                 attribute,
                                                                 index,
                                                                 sub_connection_name)
            sub_connections = cmds.listConnections(sub_connection_attribute,
                                                   plugs=True)
            if not sub_connections:
                continue
            for connection in sub_connections:
                cmds.disconnectAttr(connection, sub_connection_attribute)


def get_remap_node(data, new_sensor, remap_key, attr):
    """This function retrieves the remap node for the provided sensor if
    it exists. If it does not exist, a new one is created. The remap node
    is created with the name provided in the data dictionary.

    Note: this function is not used anymore. Please refer to get_remap_data
    and create_remap.

    Args:
        data (dict): Dictionary containing the remapValue node name.
        new_sensor (str): The name of the sensor to which the remap node is
            connected.
        remap_key (str): The key in the data dictionary for the remap node.
        attr (str): The name of the attribute to which the remap node is
            connected.

    Returns:
        str: The name of the remap node.
    """
    connections = cmds.listConnections("{0}.{1}".format(new_sensor, attr))
    if connections and cmds.nodeType(connections[0]) == "remapValue":
        remap_node = connections[0]
    else:
        remap_node = cmds.createNode("remapValue",
                                     name=data[remap_key]["name"])

    return remap_node


def get_muscle_deformer(node):
    """Retrieves the Adonis muscle deformer assigned to the provided node.
    Both AdnMuscle and AdnRibbonMuscle types are supported.

    Args:
        node (str): The name of the node with an Adonis muscle.

    Returns:
        list: The list of Adonis muscle deformers assigned to the input node.
    """
    node_history = cmds.listHistory(node)
    if not node_history:
        return []
    node_muscles = [x for x in node_history if cmds.nodeType(x) in
                    [DeformerTypes.MUSCLE, DeformerTypes.RIBBON]]
    return node_muscles


def connect_position_input(locator, attribute, source):
    """Connects the provided locator's position attribute to the indicated
    input for such position. To retrieve the positional information, a matrix
    decomposition node is created between the source position input and the
    receiving locator.

    Args:
        locator (str): The name of the locator to receive the connection.
        attribute (str): The name of the position attribute to connect to.
        source (str): The name of the transformation node to use as source
            of the connection.
    """
    connections = cmds.listConnections("{0}.{1}".format(locator, attribute))
    if connections and cmds.nodeType(connections[0]) == "decomposeMatrix":
        decompose_node = connections[0]
    else:
        decompose_node = cmds.createNode("decomposeMatrix")
    cmds.connectAttr("{0}.worldMatrix[0]".format(source),
                     "{0}.inputMatrix".format(decompose_node),
                     force=True)
    cmds.connectAttr("{0}.outputTranslate".format(decompose_node),
                     "{0}.{1}".format(locator, attribute),
                     force=True)


def connect_remap(remap_node, source_plug=None, destination_plug=None):
    """Makes the input and output values connection of a remap node. This
    function works both for Maya remapValue and AdnRemap nodes.

    Args:
        remap_node (str): name of the remap node existing in the scene.
        source_plug (str, optional): full attribute name (node.attr) to
            connect to the input value of the remap node. Defaults to None.
        destination_plug (str, optional): full attribute name (node.attr) to
            connect to the output value of the remap node. Defaults to None.
    """
    remap_node_type = cmds.nodeType(remap_node)
    # Maya remapValue node
    if remap_node_type == "remapValue":
        remap_input = "inputValue"
        remap_output = "outValue"
    # AdnRemap node
    elif remap_node_type == OtherNodeTypes.REMAP:
        remap_input = "input"
        remap_output = "output"
    else:
        return

    remap_destination = "{0}.{1}".format(remap_node, remap_input)
    remap_source = "{0}.{1}".format(remap_node, remap_output)

    # Connect source to the remap input plug
    if source_plug and cmds.objExists(source_plug):
        cmds.connectAttr(source_plug, remap_destination, force=True)
    # Connect remap output plug to the destination
    if destination_plug and cmds.objExists(destination_plug):
        cmds.connectAttr(remap_source, destination_plug, force=True)


def create_activation(data):
    """This function creates an AdnActivation node using the data provided
    in a dictionary.

    Args:
        data (dict): Dictionary containing all the relevant information to
            create the mirrored activation node.

    Returns:
        str: The name of the newly created activation node.
    """
    new_activation = None
    if data["type"] != OtherNodeTypes.ACTIVATION:
        return new_activation

    if cmds.objExists(data["name"]):
        new_activation = data["name"]
    else:
        new_activation = cmds.createNode(OtherNodeTypes.ACTIVATION, name=data["name"])

    cmds.setAttr("{0}.minOutValue".format(new_activation), data["minOutValue"])
    cmds.setAttr("{0}.maxOutValue".format(new_activation), data["maxOutValue"])

    for item in data["inputs"]:
        inputs_plug = "{0}.inputs[{1}]".format(new_activation, item["index"])
        cmds.setAttr("{0}.bypassOperator".format(inputs_plug), item["bypassOperator"])
        cmds.setAttr("{0}.operator".format(inputs_plug), item["operator"])
        if isinstance(item["value"], str):
            cmds.connectAttr(item["value"],
                             "{0}.value".format(inputs_plug),
                             force=True)
        else:
            cmds.setAttr("{0}.value".format(inputs_plug), item["value"])

    return new_activation


def create_locator(data):
    """This function creates an Adonis locator using the data provided in a
    dictionary.

    Args:
        data (dict): Dictionary containing all the relevant information to
            create the mirrored locator.

    Returns:
        str: The name of the newly created locator.
    """
    new_locator = None
    if data["type"] not in [LocatorTypes.DISTANCE, LocatorTypes.ROTATION,
                            LocatorTypes.POSITION]:
        return new_locator

    if cmds.objExists(data["name"]):
        new_locator = data["name"]
    else:
        new_locator = cmds.createNode(data["type"], name=data["name"])

    if not new_locator:
        return new_locator
    cmds.setAttr("{0}.scale".format(new_locator), data["scale"])
    cmds.setAttr("{0}.drawOutput".format(new_locator), data["drawOutput"])
    if data["type"] in [LocatorTypes.DISTANCE, LocatorTypes.ROTATION]:
        if "startPositionConnection" in data and data["startPositionConnection"]:
            connect_position_input(new_locator, "startPosition",
                                   data["startPositionConnection"])
        else:
            cmds.setAttr("{0}.startPositionX".format(new_locator),
                         data["startPosition"][0])
            cmds.setAttr("{0}.startPositionY".format(new_locator),
                         data["startPosition"][1])
            cmds.setAttr("{0}.startPositionZ".format(new_locator),
                         data["startPosition"][2])
        if "endPositionConnection" in data and data["endPositionConnection"]:
            connect_position_input(new_locator, "endPosition",
                                   data["endPositionConnection"])
        else:
            cmds.setAttr("{0}.endPositionX".format(new_locator),
                         data["endPosition"][0])
            cmds.setAttr("{0}.endPositionY".format(new_locator),
                         data["endPosition"][1])
            cmds.setAttr("{0}.endPositionZ".format(new_locator),
                         data["endPosition"][2])
        if "startMatrix" in data and data["startMatrix"]:
            cmds.connectAttr(data["startMatrix"], "{0}.startMatrix".format(new_locator),
                             force=True)
        if "endMatrix" in data and data["endMatrix"]:
            cmds.connectAttr(data["endMatrix"], "{0}.endMatrix".format(new_locator),
                             force=True)
    if data["type"] == LocatorTypes.ROTATION:
        if "midPositionConnection" in data and data["midPositionConnection"]:
            connect_position_input(new_locator, "midPosition",
                                   data["midPositionConnection"])
        else:
            cmds.setAttr("{0}.midPositionX".format(new_locator),
                         data["midPosition"][0])
            cmds.setAttr("{0}.midPositionY".format(new_locator),
                         data["midPosition"][1])
            cmds.setAttr("{0}.midPositionZ".format(new_locator),
                         data["midPosition"][2])
        if "midMatrix" in data and data["midMatrix"]:
            cmds.connectAttr(data["midMatrix"], "{0}.midMatrix".format(new_locator),
                             force=True)
    if data["type"] == LocatorTypes.POSITION:
        if "positionConnection" in data and data["positionConnection"]:
            connect_position_input(new_locator, "position",
                                   data["positionConnection"])
        else:
            cmds.setAttr("{0}.positionX".format(new_locator),
                         data["position"][0])
            cmds.setAttr("{0}.positionY".format(new_locator),
                         data["position"][1])
            cmds.setAttr("{0}.positionZ".format(new_locator),
                         data["position"][2])
        if "positionMatrix" in data and data["positionMatrix"]:
            cmds.connectAttr(data["positionMatrix"], "{0}.positionMatrix".format(new_locator),
                             force=True)
    return new_locator


def create_sensor(data, locator):
    """This function creates an Adonis sensor graph (includes sensors and
    remapping nodes) using the data provided in a dictionary. The activation
    values from the sensor graph are connected to indicated locator.

    Args:
        data (dict): Dictionary containing all the relevant information to
            create the mirrored sensor and its graph.
        locator (str): The name of the locator receiving the sensor data.

    Returns:
        str: The name of the newly created sensor.
    """
    if not data:
        return None

    sensor = data["sensor"]
    if not sensor:
        return None

    if sensor["type"] not in [SensorTypes.DISTANCE, SensorTypes.ROTATION,
                              SensorTypes.POSITION]:
        return None

    if cmds.objExists(sensor["name"]):
        new_sensor = sensor["name"]
    else:
        # Create new sensor
        new_sensor = cmds.createNode(sensor["type"], name=sensor["name"])

    # Set generic sensor attributes and connect the sensors to input drivers
    cmds.setAttr("{0}.timeScale".format(new_sensor), sensor["timeScale"])
    cmds.setAttr("{0}.startTime".format(new_sensor), sensor["startTime"])
    cmds.connectAttr("time1.outTime", "{0}.currentTime".format(new_sensor), force=True)
    set_sensor_remap_data(new_sensor, sensor, "Velocity")
    set_sensor_remap_data(new_sensor, sensor, "Acceleration")
    if sensor["type"] in [SensorTypes.DISTANCE, SensorTypes.ROTATION]:
        if "startPositionConnection" in sensor and sensor["startPositionConnection"]:
            connect_position_input(new_sensor, "startPosition",
                                   sensor["startPositionConnection"])
        if "endPositionConnection" in sensor and sensor["endPositionConnection"]:
            connect_position_input(new_sensor, "endPosition",
                                   sensor["endPositionConnection"])
        if "startMatrix" in sensor and sensor["startMatrix"]:
            cmds.connectAttr(sensor["startMatrix"], "{0}.startMatrix".format(new_sensor),
                             force=True)
        if "endMatrix" in sensor and sensor["endMatrix"]:
            cmds.connectAttr(sensor["endMatrix"], "{0}.endMatrix".format(new_sensor),
                             force=True)
        if sensor["type"] == SensorTypes.ROTATION:
            if "midPositionConnection" in sensor and sensor["midPositionConnection"]:
                connect_position_input(new_sensor, "midPosition",
                                       sensor["midPositionConnection"])
            if "midMatrix" in sensor and sensor["midMatrix"]:
                cmds.connectAttr(sensor["midMatrix"], "{0}.midMatrix".format(new_sensor),
                                 force=True)
            set_sensor_remap_data(new_sensor, sensor, "Angle")
        if sensor["type"] == SensorTypes.DISTANCE:
            set_sensor_remap_data(new_sensor, sensor, "Distance")
    if sensor["type"] == SensorTypes.POSITION:
        if "positionConnection" in sensor and sensor["positionConnection"]:
            connect_position_input(new_sensor, "position",
                                   sensor["positionConnection"])
        if "positionMatrix" in sensor and sensor["positionMatrix"]:
            cmds.connectAttr(sensor["positionMatrix"], "{0}.positionMatrix".format(new_sensor),
                             force=True)
    if sensor["type"] in [SensorTypes.DISTANCE, SensorTypes.POSITION]:
        cmds.setAttr("{0}.spaceScale".format(new_sensor),
                     sensor["spaceScale"])

    # Connect value remap outputs to locator
    if data["valueSensor"]:
        if sensor["type"] == SensorTypes.DISTANCE:
            cmds.connectAttr("{0}.outDistanceRemap".format(new_sensor),
                             "{0}.activationDistance".format(locator),
                             force=True)
        elif sensor["type"] == SensorTypes.ROTATION:
            cmds.connectAttr("{0}.outAngleRemap".format(new_sensor),
                             "{0}.activationAngle".format(locator),
                             force=True)

    # Connect velocity remap outputs to locator
    if data["velSensor"]:
        cmds.connectAttr("{0}.outVelocityRemap".format(new_sensor),
                         "{0}.activationVelocity".format(locator),
                         force=True)

    # Connect acceleration remap outputs to locator
    if data["accelSensor"]:
        cmds.connectAttr("{0}.outAccelerationRemap".format(new_sensor),
                         "{0}.activationAcceleration".format(locator),
                         force=True)

    # Create value remap nodes between the sensor and the locator
    # Value (e.g. distance, angle)
    if data["valueRemap"]:
        if sensor["type"] == SensorTypes.DISTANCE:
            sensor_output = "outDistance"
            locator_input = "activationDistance"
        else:
            sensor_output = "outAngle"
            locator_input = "activationAngle"
        remap_node = create_remap(data["valueRemap"])
        source_plug = "{0}.{1}".format(new_sensor, sensor_output)
        destination_plug = "{0}.{1}".format(locator, locator_input)
        connect_remap(remap_node, source_plug, destination_plug)
    # Velocity
    if data["velRemap"]:
        remap_node = create_remap(data["velRemap"])
        sensor_output = "outVelocity"
        locator_input = "activationVelocity"
        source_plug = "{0}.{1}".format(new_sensor, sensor_output)
        destination_plug = "{0}.{1}".format(locator, locator_input)
        connect_remap(remap_node, source_plug, destination_plug)
    # Acceleration
    if data["accelRemap"]:
        remap_node = create_remap(data["accelRemap"])
        sensor_output = "outAcceleration"
        locator_input = "activationAcceleration"
        source_plug = "{0}.{1}".format(new_sensor, sensor_output)
        destination_plug = "{0}.{1}".format(locator, locator_input)
        connect_remap(remap_node, source_plug, destination_plug)

    return new_sensor


def create_remap(data):
    """Creates a new remap node and configures the scalar values and the ramp
    attribute with the information provided in the input dictionary. This
    function works for both Maya remapValue and AdnRemap nodes.

    Args:
        data (dict): dictionary containing all the info required to create
            and configure the remap node.

    Returns:
        str: name of the created remap node.
    """
    # Filter by type: remapValue or AdnRemap
    remap_node_type = data["type"]
    ramp_attribute = "value" if remap_node_type == "remapValue" else "remap"
    input_attribute = "inputValue" if remap_node_type == "remapValue" else "input"

    # Create
    remap_node = data["name"]
    remap_node = cmds.createNode(remap_node_type, name=remap_node)

    # Configure input value
    cmds.setAttr("{0}.{1}".format(remap_node, input_attribute), data["input"])

    # Configure in/out min/max ranges
    cmds.setAttr("{0}.inputMin".format(remap_node), data["inputMin"])
    cmds.setAttr("{0}.inputMax".format(remap_node), data["inputMax"])
    cmds.setAttr("{0}.outputMin".format(remap_node), data["outputMin"])
    cmds.setAttr("{0}.outputMax".format(remap_node), data["outputMax"])

    # Configure ramp
    set_ramp_data(remap_node, ramp_attribute, data["ramp"])

    return remap_node


def get_sensor(locator, left_convention, right_convention, report_data=None):
    """This function retrieves the mirroring data for the sensor associated
    to the provided locator. All the relevant data for the sensor is retrieved
    and stored in a dictionary. Any mirrorable entity will get their name
    mirrored.

    Args:
        locator (str): The name of the locator receiving the sensor data.
        left_convention (str): String parameter defining the naming convention
            for left-side objects. The convention includes a '*' wildcard to
            define prefixes ('abc_*') or suffixes ('*_abc').
        right_convention (str): String parameter defining the naming convention
            for right-side objects. The convention includes a '*' wildcard to
            define prefixes ('abc_*') or suffixes ('*_abc').
        report_data (dict, optional): Dictionary to store the errors and warnings.
            Defaults to None.

    Returns:
        dict: A dictionary containing the data for the mirroring of the sensor.
    """
    sensor_nodes_set = set()
    sensor_data = {
        "valueRemap": None,
        "velRemap": None,
        "accelRemap": None,
        "valueSensor": None,
        "velSensor": None,
        "accelSensor": None,
        "sensor": {
            "type": None,
            "name": None,
            "timeScale": None,
            "startTime": None,
        }
    }

    # Value: get input node connected to the activation value (e.g. distance, angle)
    value_input_node = None
    if cmds.nodeType(locator) == LocatorTypes.DISTANCE:
        value_input_node = cmds.listConnections("{0}.activationDistance".format(locator), destination=False)
    elif cmds.nodeType(locator) == LocatorTypes.ROTATION:
        value_input_node = cmds.listConnections("{0}.activationAngle".format(locator), destination=False)
    if value_input_node:
        value_input_node = value_input_node[0]
        node_type = cmds.nodeType(value_input_node)
        if node_type in [SensorTypes.DISTANCE, SensorTypes.ROTATION]:
            # Locator and sensor directly connected to each other
            sensor_nodes_set.add(value_input_node)
            sensor_data["valueSensor"] = value_input_node
        else:
            # Intermediate remap node between locator and sensor
            sensor_data["valueRemap"] = get_remap_data(value_input_node, node_type,
                                                       left_convention, right_convention)
            if sensor_data["valueRemap"]:
                sensor = get_remap_input(value_input_node, node_type)
                if sensor:
                    sensor_nodes_set.add(sensor)

    # Velocity: get input node connected to the velocity value
    vel_input_node = cmds.listConnections("{0}.activationVelocity".format(locator), destination=False)
    if vel_input_node:
        vel_input_node = vel_input_node[0]
        node_type = cmds.nodeType(vel_input_node)
        if node_type in [SensorTypes.DISTANCE, SensorTypes.ROTATION, SensorTypes.POSITION]:
            # Locator and sensor directly connected to each other
            sensor_nodes_set.add(vel_input_node)
            sensor_data["velSensor"] = vel_input_node
        else:
            # Intermediate remap node between locator and sensor
            sensor_data["velRemap"] = get_remap_data(vel_input_node, node_type,
                                                     left_convention, right_convention)
            if sensor_data["velRemap"]:
                sensor = get_remap_input(vel_input_node, node_type)
                if sensor:
                    sensor_nodes_set.add(sensor)

    # Acceleration: get input node connected to the acceleration value
    accel_input_node = cmds.listConnections("{0}.activationAcceleration".format(locator), destination=False)
    if accel_input_node:
        accel_input_node = accel_input_node[0]
        node_type = cmds.nodeType(accel_input_node)
        if node_type in [SensorTypes.DISTANCE, SensorTypes.ROTATION, SensorTypes.POSITION]:
            # Locator and sensor directly connected to each other
            sensor_nodes_set.add(accel_input_node)
            sensor_data["accelSensor"] = accel_input_node
        else:
            # Intermediate remap node between locator and sensor
            sensor_data["accelRemap"] = get_remap_data(accel_input_node, node_type,
                                                       left_convention, right_convention)
            if sensor_data["accelRemap"]:
                sensor = get_remap_input(accel_input_node, node_type)
                if sensor:
                    sensor_nodes_set.add(sensor)

    # Abort if 0 or more than 1 sensors were found in the mirroring chain
    if len(sensor_nodes_set) != 1:
        return None

    sensor = list(sensor_nodes_set)[0]        

    node_type = cmds.nodeType(sensor)
    if node_type not in [SensorTypes.DISTANCE, SensorTypes.ROTATION,
                         SensorTypes.POSITION]:
        return None

    sensor_data["sensor"]["name"] = get_mirror_name(sensor, left_convention,
                                                    right_convention)

    if sensor_data["sensor"]["name"] is None:
        report_naming_convention_error(sensor, left_convention,
                                       right_convention, report_data)
        return None

    sensor_data["sensor"]["type"] = node_type
    sensor_data["sensor"]["timeScale"] = cmds.getAttr(
        "{0}.timeScale".format(sensor))
    sensor_data["sensor"]["startTime"] = cmds.getAttr(
        "{0}.startTime".format(sensor))
    
    get_sensor_remap_data(sensor, "Velocity", sensor_data["sensor"])
    get_sensor_remap_data(sensor, "Acceleration", sensor_data["sensor"])

    if node_type in [SensorTypes.DISTANCE,
                     SensorTypes.ROTATION]:
        if node_type == SensorTypes.DISTANCE:
            get_sensor_remap_data(sensor, "Distance", sensor_data["sensor"])
        if node_type == SensorTypes.ROTATION:
            get_sensor_remap_data(sensor, "Angle", sensor_data["sensor"])
            get_sensor_decompose_matrix_data(sensor, sensor_data["sensor"], "midPosition",
                                             left_convention, right_convention, report_data=report_data)
            get_input_matrix_data(sensor, sensor_data["sensor"], "midMatrix",
                                  left_convention, right_convention, report_data=report_data)
        
        get_sensor_decompose_matrix_data(sensor, sensor_data["sensor"], "startPosition",
                                         left_convention, right_convention, report_data=report_data)
        get_sensor_decompose_matrix_data(sensor, sensor_data["sensor"], "endPosition",
                                         left_convention, right_convention, report_data=report_data)
        get_input_matrix_data(sensor, sensor_data["sensor"], "startMatrix",
                              left_convention, right_convention, report_data=report_data)
        get_input_matrix_data(sensor, sensor_data["sensor"], "endMatrix",
                              left_convention, right_convention, report_data=report_data)
    
    if node_type in [SensorTypes.DISTANCE,
                     SensorTypes.POSITION]:
        sensor_data["sensor"]["spaceScale"] = cmds.getAttr(
            "{0}.spaceScale".format(sensor))
        if node_type == SensorTypes.POSITION:
            get_sensor_decompose_matrix_data(sensor, sensor_data["sensor"], "position", 
                                             left_convention, right_convention, report_data=report_data)
            get_input_matrix_data(sensor, sensor_data["sensor"], "positionMatrix",
                                  left_convention, right_convention, report_data=report_data)
    return sensor_data


def get_remap_data(remap_node, node_type, left_convention, right_convention):
    """Extracts remap node data (e.g., input/output ranges and ramp attributes).

    Args:
        remap_node (str): Name of the remap node to extract data from.
        node_type (str): Type of the remap node (e.g., remapValue, AdnRemap).
        left_convention (str): String parameter defining the naming convention
            for left-side objects. The convention includes a '*' wildcard to
            define prefixes ('abc_*') or suffixes ('*_abc').
        right_convention (str): String parameter defining the naming convention
            for right-side objects. The convention includes a '*' wildcard to
            define prefixes ('abc_*') or suffixes ('*_abc').
    """
    # Find sensor from the remap node's inputs
    if node_type == "remapValue":
        remap_attr = "value"
        input_attr = "inputValue"
    elif node_type == OtherNodeTypes.REMAP:
        remap_attr = "remap"
        input_attr = "input"
    else:
        return None

    remap_node_name = get_mirror_name(remap_node, left_convention, right_convention)

    # Write remap settings into the output dictionary
    return {
        "name": remap_node_name or remap_node,
        "type": node_type,
        "input": cmds.getAttr("{0}.{1}".format(remap_node, input_attr)),
        "inputMin": cmds.getAttr("{0}.inputMin".format(remap_node)),
        "inputMax": cmds.getAttr("{0}.inputMax".format(remap_node)),
        "outputMin": cmds.getAttr("{0}.outputMin".format(remap_node)),
        "outputMax": cmds.getAttr("{0}.outputMax".format(remap_node)),
        "ramp": get_ramp_data(remap_node, remap_attr)
    }


def get_remap_input(remap_node, node_type, plugs=False):
    """Auxiliary function to obtain the input connections to the input value
    of a remap node. It can return the node name only or also the full
    attribute name including the plug name.

    Args:
        remap_node (str): name of the remap node to get input connections from.
        node_type (str): type of the remap node (i.e. remapValue or AdnRemap).
        plugs (bool, optional): flag to determine if the function has to return
            the node name (False) or the full attribute name (True). Defaults
            to False.

    Returns:
        str: name of the node or the full attribute connected to the remap
            node. None if there is no input connection or the input node
            type is not valid.
    """
    if node_type == "remapValue":
        remap_input_plug = "{0}.inputValue".format(remap_node)
    elif node_type == OtherNodeTypes.REMAP:
        remap_input_plug = "{0}.input".format(remap_node)
    else:
        return None
    input_node = cmds.listConnections(remap_input_plug,
                                      source=True,
                                      destination=False,
                                      plugs=plugs) or []
    return input_node[0] if input_node else None


def apply_mirror_input_remap_connection(mirror_solver,
                                        attribute_name, attribute_connection,
                                        left_convention, right_convention,
                                        report_data=None):
    """Mirrors a remap node connected to a solver. This function is in charge
    of creating the intermediate remap node, configuring it, and making the
    input and output connections also mirrored.

    Args:
        mirror_solver (str): name of the destination solver in the mirrored side.
        attribute_name (str): name of the attribute of the solver that the
            remap node has to be connected to.
        attribute_connection (str): name of the input connection to the
            solver in the source side. It has the format "node.attr".
        left_convention (str): String parameter defining the naming convention
            for left-side objects. The convention includes a '*' wildcard to
            define prefixes ('abc_*') or suffixes ('*_abc').
        right_convention (str): String parameter defining the naming convention
            for right-side objects. The convention includes a '*' wildcard to
            define prefixes ('abc_*') or suffixes ('*_abc').
        report_data (dict, optional): Dictionary to store the errors and warnings.
            Defaults to None.
    """
    attr_source = attribute_connection.partition(".")[0]
    node_source_type = cmds.nodeType(attr_source)
    if node_source_type not in ["remapValue", "AdnRemap"]:
        return

    # Get remap settings
    remap_data = get_remap_data(attr_source, node_source_type,
                                left_convention,
                                right_convention)
    if not remap_data:
        return

    # Create remap and connect output to the solver attr
    mirror_remap = create_remap(remap_data)
    destination_plug = "{0}.{1}".format(mirror_solver,
                                        attribute_name)
    connect_remap(mirror_remap,
                  destination_plug=destination_plug)
    # Check for input connections to the remap node
    remap_input = get_remap_input(attr_source, node_source_type, plugs=True)
    if not remap_input:
        return
    remap_source = remap_input.partition(".")[0]
    remap_plug = remap_input.partition(".")[-1]
    mirror_source = get_mirror_name(remap_source,
                                    left_convention,
                                    right_convention)
    if mirror_source is None:
        report_mirror_connection_warning(remap_source, mirror_remap,
                                         "input", report_data)
        mirror_source = remap_source
    if not cmds.objExists(mirror_source):
        report_mirror_connection_error(mirror_source,
                                       remap_source,
                                       remap_plug,
                                       mirror_remap,
                                       report_data)
        return
    # Mirror input connection to the remap node
    source_plug = "{0}.{1}".format(mirror_source, remap_plug)
    connect_remap(mirror_remap, source_plug=source_plug)


def apply_mirror_muscle_deformer(node, solver, left_convention, right_convention, report_data=None):
    """This function mirrors an Adonis muscle deformer given the provided
    solver data and assigns it to the object that is the mirrored version of
    the provided node.

    Args:
        node (str): The name of the original geometry which mirrored entity
            the mirrored solver is to be assigned to.
        solver (str): The name of the original node for which a new mirrored
            name is to be created.
        left_convention (str): String parameter defining the naming convention
            for left-side objects. The convention includes a '*' wildcard to
            define prefixes ('abc_*') or suffixes ('*_abc').
        right_convention (str): String parameter defining the naming convention
            for right-side objects. The convention includes a '*' wildcard to
            define prefixes ('abc_*') or suffixes ('*_abc').
        report_data (dict, optional): Dictionary to store the errors and warnings.
            Defaults to None.

    Returns:
        str, str: Tuple with the mirrored geometry node and the mirrored
            muscle deformer if the execution completes successfully.
        bool: False if the expected mirrored node is None or not found
            so that the parameters can't be mirrored.
    """
    mirror_node = get_mirror_name(node, left_convention, right_convention)
    if mirror_node is None:
        report_naming_convention_error(node, left_convention,
                                       right_convention, report_data)
        return False
    if not cmds.objExists(mirror_node):
        if report_data is not None:
            report_data["errors"].append("Node \"{0}\" does not exist.".format(mirror_node))
        return False

    # Get deformer type (muscle or ribbon) from the solver node
    solver_type = cmds.nodeType(solver)
    if solver_type not in [DeformerTypes.MUSCLE, DeformerTypes.RIBBON]:
        if report_data is not None:
            msg_err = ("Node type of \"{0}\" can't be mirrored. "
                       "Expected {1} or {2}, got {3}"
                       "".format(mirror_node, DeformerTypes.MUSCLE,
                                 DeformerTypes.RIBBON, cmds.nodeType(solver)))
            report_data["errors"].append(msg_err)
        return False

    mirror_muscle_solvers = get_muscle_deformer(mirror_node)
    mirror_solver_name = None
    if solver.startswith(solver_type):
        if solver[len(solver_type):].isnumeric():
            mirror_solver_name = solver
    else:
        mirror_solver_name = get_mirror_name(solver, left_convention,
                                             right_convention)
        if mirror_solver_name is None:
            report_naming_convention_error(solver, left_convention,
                                           right_convention, report_data)
            return False

    if len(mirror_muscle_solvers) == 0:
        mirror_solver = cmds.deformer(mirror_node, type=solver_type,
                                      name=mirror_solver_name)[-1]
    else:
        if mirror_solver_name != mirror_muscle_solvers[0]:
            mirror_solver = mirror_muscle_solvers[0]
        else:
            mirror_solver = mirror_solver_name

    vertices_count = cmds.polyEvaluate(node, vertex=True)
    if not cmds.isConnected("time1.outTime",
                            "{0}.currentTime".format(mirror_solver)):
        cmds.connectAttr("time1.outTime",
                         "{0}.currentTime".format(mirror_solver))
    if mirror_solver not in cmds.listConnections("AdnDataNode1.inputs"):
        debug_connections = cmds.getAttr("AdnDataNode1.inputs",
                                         multiIndices=True) or []
        next_index = max(debug_connections) + 1 if debug_connections else 0
        cmds.connectAttr("{0}.message".format(mirror_solver),
                         "AdnDataNode1.inputs[{0}]".format(next_index))

    connections = {
        "targets": ["targetWorldMesh",
                    "targetWorldMatrix"],
        "slideOnSegmentConstraintsList": ["slideOnSegmentRootMatrix",
                                          "slideOnSegmentTipMatrix"],
        "attachmentConstraintsList": ["attachmentMatrix"]
    }

    for connection_name in connections.keys():
        clear_connections(mirror_solver, connection_name,
                          connections[connection_name])
        logical_indices = cmds.getAttr(
            "{0}.{1}".format(solver, connection_name),
            multiIndices=True) or []
        for connection_index in logical_indices:
            if not connections[connection_name]:
                continue
            for sub_connection_name in connections[connection_name]:
                sub_connections = cmds.listConnections(
                    "{0}.{1}[{2}].{3}".format(solver, connection_name,
                                              connection_index,
                                              sub_connection_name),
                    plugs=True)
                if not sub_connections:
                    continue
                for connection in sub_connections:
                    connection_source = connection.partition(".")[0]
                    connection_plug = connection.partition(".")[-1]
                    mirrored_connection = get_mirror_name(
                        connection_source, left_convention,
                        right_convention)
                    if mirrored_connection:
                        mirrored_connection = "{0}.{1}".format(mirrored_connection,  connection_plug)
                    else:
                        # We add this check to avoid reporting the warning for targets for two reasons:
                        # 1. We already check that the muscle geometries provided in the selection
                        # follow the naming convention.
                        # 2. If we don't exclude the targets, we would warn for each muscle attached to the
                        # skeletal geometry while this is a valid setup.
                        if connection_name != "targets":
                            report_mirror_connection_warning(connection, mirror_solver,
                                                             "{0}[{1}].{2}".format(connection_name,
                                                             connection_index, sub_connection_name),
                                                             report_data)
                        mirrored_connection = connection

                    if not cmds.objExists(mirrored_connection):
                        report_mirror_connection_error(mirrored_connection, solver,
                                                       "{0}[{1}].{2}".format(connection_name,
                                                       connection_index, sub_connection_name),
                                                       mirror_solver, report_data)
                        continue
                    cmds.connectAttr(mirrored_connection,
                                    "{0}.{1}[{2}].{3}".format(
                                        mirror_solver,
                                        connection_name,
                                        connection_index,
                                        sub_connection_name))

    # Attributes shared by muscle and ribbon types
    attributes = {
        "enable": "bool",
        "iterations": "int",
        "material": "enum",
        "stiffnessMultiplier": "float",
        "activation": "float",
        "restActivation": "float",
        "prerollStartTime": "float",
        "startTime": "float",
        "timeScale": "float",
        "spaceScale": "float",
        "spaceScaleMode": "enum",
        "gravity": "float",
        "gravityDirection": "vector",
        "initFibersLengthsAtStartTime": "bool",
        "initShapePreservationAtStartTime": "bool",
        "initExternalConstraintsAtStartTime": "bool",
        "useCustomStiffness": "bool",
        "stiffness": "float",
        "attachmentToGeometryStiffnessOverride": "float",
        "attachmentToTransformStiffnessOverride": "float",
        "fiberStiffnessOverride": "float",
        "shapeStiffnessOverride": "float",
        "slideOnGeometryStiffnessOverride": "float",
        "slideOnSegmentStiffnessOverride": "float",
        "pointMassMode": "enum",
        "density": "float",
        "globalMassMultiplier": "float",
        "triangulateMesh": "bool",
        "globalDampingMultiplier": "float",
        "inertiaDamper": "float",
        "restLengthMultiplier": "float",
        "maxSlidingDistance": "float",
        "compressionMultiplier": "float",
        "stretchingMultiplier": "float",
        "attenuationVelocityFactor": "float",
        "hardAttachments": "bool",
        "slidingConstraintsMode": "enum",
        "envelope": "float"}
    # Attributes own by muscle type only
    if solver_type == DeformerTypes.MUSCLE:
        attributes.update({
            "volumePreservation": "float",
            "volumeRatio": "float",
            "volumeStiffnessOverride": "float"
        })

    for attribute_name in attributes.keys():
        if not cmds.attributeQuery(attribute_name,
                                   node=mirror_solver,
                                   exists=True):
            continue
        attribute_type = attributes[attribute_name]
        attribute_lock = cmds.getAttr(
            "{0}.{1}".format(solver, attribute_name), lock=True)
        attribute_connections = cmds.listConnections(
            "{0}.{1}".format(solver, attribute_name),
            plugs=True, source=True, destination=False) or []

        # Check for input connections
        if attribute_connections:
            attr_source = attribute_connections[0].partition(".")[0]
            attr_plug = attribute_connections[0].partition(".")[-1]
            node_source_type = cmds.nodeType(attr_source)
            # Input connections to remap nodes (remapValue and AdnRemap)
            if node_source_type in ["remapValue", "AdnRemap"]:
                apply_mirror_input_remap_connection(mirror_solver,
                                                    attribute_name,
                                                    attribute_connections[0],
                                                    left_convention,
                                                    right_convention,
                                                    report_data)
            # Input connections to any other node type
            else:
                mirror_source = get_mirror_name(attr_source,
                                                left_convention,
                                                right_convention)
                if mirror_source is None:
                    mirror_source = attr_source
                new_connections_source = "{0}.{1}".format(mirror_source, attr_plug)
                new_connections_dest = "{0}.{1}".format(mirror_solver, attribute_name)
                if cmds.objExists(new_connections_source) and cmds.objExists(new_connections_dest):
                    cmds.connectAttr("{0}.{1}".format(mirror_source, attr_plug),
                                     "{0}.{1}".format(mirror_solver, attribute_name),
                                     force=True)

        if attribute_lock or attribute_connections:
            continue
            
        # Set attr value 
        if attribute_type in ["bool", "int", "float", "enum"]:
            attribute_value = cmds.getAttr(
                "{0}.{1}".format(solver, attribute_name))
            cmds.setAttr(
                "{0}.{1}".format(mirror_solver, attribute_name),
                attribute_value)
        elif attribute_type == "vector":
            axis = ["X", "Y", "Z"]
            for coordinate in axis:
                attribute_value = cmds.getAttr(
                    "{0}.{1}{2}".format(solver, attribute_name,
                                        coordinate))
                cmds.setAttr(
                    "{0}.{1}{2}".format(mirror_solver, attribute_name,
                                        coordinate), attribute_value)
                    
    # Mirror activation list
    # First clear compound array attribute to avoid inconsistencies
    activation_list_full_name = "{0}.activationList".format(mirror_solver)
    num_elements = cmds.getAttr(activation_list_full_name, size=True)
    for elem in reversed(range(num_elements)):
        elem_full_name = "{0}[{1}]".format(activation_list_full_name, elem)
        if cmds.objExists(elem_full_name):
            cmds.removeMultiInstance(elem_full_name, b=True)
    # Then mirror activation list from scratch
    activation_list_indices = cmds.getAttr("{0}.activationList".format(solver), multiIndices=True) or []
    for i, logical_index in enumerate(activation_list_indices):
        child_plug_name = "{0}.activationList[{1}]".format(solver, logical_index)
        mirror_child_plug_name = "{0}.activationList[{1}]".format(mirror_solver, logical_index)
        # Bypass
        bypass = cmds.getAttr("{0}.activationListBypassOperator".format(child_plug_name))
        cmds.setAttr("{0}.activationListBypassOperator".format(mirror_child_plug_name), bypass)
        # Operator
        operator = cmds.getAttr("{0}.activationListOperator".format(child_plug_name))
        cmds.setAttr("{0}.activationListOperator".format(mirror_child_plug_name), operator)
        # Value
        value = cmds.getAttr("{0}.activationListValue".format(child_plug_name))
        cmds.setAttr("{0}.activationListValue".format(mirror_child_plug_name), value)
        # Check for possible input connections to the value
        value_source = cmds.listConnections("{0}.activationListValue".format(child_plug_name), plugs=True) or []
        if value_source:
            attr_source = value_source[0].partition(".")[0]
            if cmds.nodeType(attr_source) in ["remapValue", "AdnRemap"]:
                apply_mirror_input_remap_connection(mirror_solver,
                                                    "activationList[{0}].activationListValue".format(logical_index),
                                                    value_source[0],
                                                    left_convention,
                                                    right_convention,
                                                    report_data)
            else:
                attr_plug = value_source[0].partition(".")[-1]
                mirror_source = get_mirror_name(attr_source, left_convention, right_convention)
                if mirror_source is None:
                    mirror_source = attr_source
                mirrored_connection = "{0}.{1}".format(mirror_source, attr_plug)
                if cmds.objExists(mirrored_connection):
                    cmds.connectAttr(mirrored_connection, "{0}.activationListValue".format(mirror_child_plug_name))
                else:
                    report_mirror_connection_error(mirrored_connection, solver,
                                                   "activationList[{0}].activationListValue".format(logical_index),
                                                   mirror_solver, report_data)

    # Copy maps
    # Transform Attachments
    logical_indices = cmds.getAttr("{0}.attachmentConstraintsList".format(solver),
                                   multiIndices=True) or []
    for attachment_index in logical_indices:
        for vertex_index in range(vertices_count):
            map_value = cmds.getAttr(
                "{0}.attachmentConstraintsList[{1}].attachmentConstraints[{2}]".format(
                    solver, attachment_index, vertex_index))
            cmds.setAttr(
                "{0}.attachmentConstraintsList[{1}].attachmentConstraints[{2}]".format(
                    mirror_solver, attachment_index, vertex_index),
                map_value)
    # Geometry Attachments
    logical_indices = cmds.getAttr("{0}.targets".format(solver),
                                   multiIndices=True) or []
    for attachment_index in logical_indices:
        for vertex_index in range(vertices_count):
            map_value = cmds.getAttr(
                "{0}.targets[{1}].attachmentToGeoConstraints[{2}]".format(
                    solver, attachment_index, vertex_index))
            cmds.setAttr(
                "{0}.targets[{1}].attachmentToGeoConstraints[{2}]".format(
                    mirror_solver, attachment_index, vertex_index),
                map_value)
    # Geometry Sliding
    logical_indices = cmds.getAttr("{0}.targets".format(solver),
                                   multiIndices=True) or []
    for attachment_index in logical_indices:
        for vertex_index in range(vertices_count):
            map_value = cmds.getAttr(
                "{0}.targets[{1}].slideOnGeometryConstraints[{2}]".format(
                    solver, attachment_index, vertex_index))
            cmds.setAttr(
                "{0}.targets[{1}].slideOnGeometryConstraints[{2}]".format(
                    mirror_solver, attachment_index, vertex_index),
                map_value)
    # Segment Sliding
    logical_indices = cmds.getAttr("{0}.slideOnSegmentConstraintsList".format(solver),
                                   multiIndices=True) or []
    for attachment_index in logical_indices:
        for vertex_index in range(vertices_count):
            map_value = cmds.getAttr(
                "{0}.slideOnSegmentConstraintsList[{1}].slideOnSegmentConstraints[{2}]".format(
                    solver, attachment_index, vertex_index))
            cmds.setAttr(
                "{0}.slideOnSegmentConstraintsList[{1}].slideOnSegmentConstraints[{2}]".format(
                    mirror_solver, attachment_index, vertex_index),
                map_value)
    # Tendons
    for vertex_index in range(vertices_count):
        map_value = cmds.getAttr(
            "{0}.tendonsList[0].tendons[{1}]".format(solver, vertex_index))
        cmds.setAttr(
            "{0}.tendonsList[0].tendons[{1}]".format(mirror_solver,
                                                     vertex_index),
            map_value)
    # Compression Resistance
    for vertex_index in range(vertices_count):
        map_value = cmds.getAttr(
            "{0}.compressionResistanceList[0].compressionResistance[{1}]".format(
                solver, vertex_index))
        cmds.setAttr(
            "{0}.compressionResistanceList[0].compressionResistance[{1}]".format(
                mirror_solver, vertex_index), map_value)
    # Global Damping
    for vertex_index in range(vertices_count):
        map_value = cmds.getAttr(
            "{0}.globalDampingList[0].globalDamping[{1}]".format(solver,
                                                                 vertex_index))
        cmds.setAttr("{0}.globalDampingList[0].globalDamping[{1}]".format(
            mirror_solver, vertex_index), map_value)
    # Masses
    for vertex_index in range(vertices_count):
        map_value = cmds.getAttr(
            "{0}.massList[0].mass[{1}]".format(solver, vertex_index))
        map_value = max(map_value, 0.000001)
        cmds.setAttr("{0}.massList[0].mass[{1}]".format(mirror_solver,
                                                        vertex_index),
                     map_value)
    # Shape Preservation
    for vertex_index in range(vertices_count):
        map_value = cmds.getAttr(
            "{0}.shapePreservationList[0].shapePreservation[{1}]".format(
                solver, vertex_index))
        cmds.setAttr(
            "{0}.shapePreservationList[0].shapePreservation[{1}]".format(
                mirror_solver, vertex_index), map_value)
    # Sliding Distance Multiplier
    for vertex_index in range(vertices_count):
        map_value = cmds.getAttr(
            "{0}.maxSlidingDistanceMultiplierList[0].maxSlidingDistanceMultiplier[{1}]".format(
                solver, vertex_index))
        cmds.setAttr(
            "{0}.maxSlidingDistanceMultiplierList[0].maxSlidingDistanceMultiplier[{1}]".format(
                mirror_solver, vertex_index), map_value)
    # Stretching Resistance
    for vertex_index in range(vertices_count):
        map_value = cmds.getAttr(
            "{0}.stretchingResistanceList[0].stretchingResistance[{1}]".format(
                solver, vertex_index))
        cmds.setAttr(
            "{0}.stretchingResistanceList[0].stretchingResistance[{1}]".format(
                mirror_solver, vertex_index), map_value)
    # Fibers
    for vertex_index in range(vertices_count):
        map_value = cmds.getAttr(
            "{0}.fibersList[0].fibers[{1}].fibersX".format(solver,
                                                           vertex_index))
        cmds.setAttr(
            "{0}.fibersList[0].fibers[{1}].fibersX".format(mirror_solver,
                                                           vertex_index),
            -map_value)
        map_value = cmds.getAttr(
            "{0}.fibersList[0].fibers[{1}].fibersY".format(solver,
                                                           vertex_index))
        cmds.setAttr(
            "{0}.fibersList[0].fibers[{1}].fibersY".format(mirror_solver,
                                                           vertex_index),
            map_value)
        map_value = cmds.getAttr(
            "{0}.fibersList[0].fibers[{1}].fibersZ".format(solver,
                                                           vertex_index))
        cmds.setAttr(
            "{0}.fibersList[0].fibers[{1}].fibersZ".format(mirror_solver,
                                                           vertex_index),
            map_value)
    # Fibers multiplier
    for vertex_index in range(vertices_count):
        map_value = cmds.getAttr(
            "{0}.fibersMultiplierList[0].fibersMultiplier[{1}]".format(
                solver, vertex_index))
        cmds.setAttr(
            "{0}.fibersMultiplierList[0].fibersMultiplier[{1}]".format(
                mirror_solver, vertex_index),
            map_value)
    return mirror_node, mirror_solver


def apply_mirror_muscles(left_convention, right_convention, report_data=None):
    """This function mirrors the Adonis muscles setup for the selected
    geometries. Given the selected muscle geometry, the associated Adonis
    muscle is retrieved and then mirrored.

    Args:
        left_convention (str): String parameter defining the naming convention
            for left-side objects. The convention includes a '*' wildcard to
            define prefixes ('abc_*') or suffixes ('*_abc').
        right_convention (str): String parameter defining the naming convention
            for right-side objects. The convention includes a '*' wildcard to
            define prefixes ('abc_*') or suffixes ('*_abc').
        report_data (dict, optional): Dictionary to store the errors and warnings.
            Defaults to None.
    """
    selection = cmds.ls(selection=True, dag=True, type="mesh")
    nodes_solvers = {}
    untangled_dependencies = []
    for node in selection:
        node_muscles = get_muscle_deformer(node)
        if node_muscles:
            untangled_dependencies.append(node)
            if node not in nodes_solvers.keys():
                nodes_solvers[node] = node_muscles
    for node in nodes_solvers.keys():
        required_solvers = nodes_solvers[node]
        dependencies = []
        for other_node in nodes_solvers.keys():
            if other_node != node:
                match = nodes_solvers[other_node][0] in required_solvers[1:]
                if match:
                    dependencies.append(other_node)
        if dependencies:
            last_dependency = -1
            for dependency_node in dependencies:
                dependency_index = untangled_dependencies.index(dependency_node)
                if dependency_index > last_dependency:
                    last_dependency = dependency_index
            if last_dependency > -1:
                untangled_dependencies.remove(node)
                untangled_dependencies.insert(last_dependency + 1, node)
        else:
            untangled_dependencies.remove(node)
            untangled_dependencies.insert(0, node)
    if not untangled_dependencies:
        if report_data is not None:
            report_data["warnings"].append("Muscles not mirrored because not "
                                           "found in the selection.")
        return
    for node in untangled_dependencies:
        node_muscles = get_muscle_deformer(node)[:1]
        if node_muscles:
            for solver in node_muscles:
                apply_mirror_muscle_deformer(node, solver,
                                             left_convention,
                                             right_convention,
                                             report_data=report_data)


def apply_mirror_activation(left_convention, right_convention, report_data=None):
    """This function performs the mirroring of the AdnActivation nodes connected
    to the activation plug of the muscles selected. All the relevant data for each of
    the activation nodes is retrieved and stored in a dictionary. Any mirrorable
    entity will get their name mirrored.

    Args:
        left_convention (str): String parameter defining the naming convention
            for left-side objects. The convention includes a '*' wildcard to
            define prefixes ('abc_*') or suffixes ('*_abc').
        right_convention (str): String parameter defining the naming convention
            for right-side objects. The convention includes a '*' wildcard to
            define prefixes ('abc_*') or suffixes ('*_abc').
        report_data (dict, optional): Dictionary to store the errors and warnings.
            Defaults to None.
    """
    selection = cmds.ls(selection=True, dag=True, type="mesh")
    activation_nodes = {}
    for node in selection:
        node_muscles = get_muscle_deformer(node)
        # Skip if there are no muscles
        if not node_muscles:
            continue
        muscle = node_muscles[0]
        connections = cmds.listConnections("{0}.activation".format(muscle)) or []
        # Skip if there is no connection to the activation plug
        if not connections:
            continue
        activation_node = connections[0]
        # Skip if there is no activation node connected to the activation plug
        if cmds.nodeType(activation_node) != OtherNodeTypes.ACTIVATION:
            continue
        # Skip if the activation node was already stored
        if activation_node in activation_nodes.keys():
            continue
        mirror_node_name = get_mirror_name(activation_node,
                                           left_convention,
                                           right_convention)
        if mirror_node_name is None:
            report_naming_convention_error(activation_node, left_convention,
                                           right_convention, report_data)
            continue

        activation_node_info = {
            "name" : mirror_node_name,
            "type" : OtherNodeTypes.ACTIVATION,
            "minOutValue" : cmds.getAttr("{0}.minOutValue".format(activation_node)),
            "maxOutValue" : cmds.getAttr("{0}.maxOutValue".format(activation_node)),
            "inputs" : []
        }
        logical_indices = cmds.getAttr("{0}.inputs".format(activation_node), multiIndices=True) or []
        for i in logical_indices:
            value_plug_name = "{0}.inputs[{1}].value".format(activation_node, i)
            value_connections = cmds.listConnections(value_plug_name, shapes=True, plugs=True) or []
            value = None
            # If there is no connection just store the value
            if not value_connections:
                value = cmds.getAttr(value_plug_name)
            # If there is a connection store the plug name
            else:
                value_source_obj = value_connections[0].partition(".")[0]
                value_source_plug = value_connections[0].partition(".")[-1]
                mirror_source = get_mirror_name(value_source_obj,
                                                left_convention,
                                                right_convention)

                if mirror_source is None:
                    report_mirror_connection_warning(value_connections[0], mirror_node_name,
                                                     "inputs[{0}].value".format(i), report_data)
                    mirror_source = value_source_obj

                if not cmds.objExists(mirror_source):
                    report_mirror_connection_error(mirror_source, activation_node,
                                                   "inputs[{0}].value".format(i),
                                                   mirror_node_name, report_data)
                    value = cmds.getAttr(value_plug_name)
                else:
                    value = "{0}.{1}".format(mirror_source, value_source_plug)

            input_data = {
                "index" : i,
                "bypassOperator" : cmds.getAttr("{0}.inputs[{1}].bypassOperator".format(activation_node, i)),
                "value" : value,
                "operator" : cmds.getAttr("{0}.inputs[{1}].operator".format(activation_node, i))
            }

            activation_node_info["inputs"].append(input_data)

        activation_nodes[mirror_node_name] = activation_node_info

    for key in activation_nodes:
        create_activation(activation_nodes[key])

    return activation_nodes


def apply_mirror_locators(left_convention, right_convention, report_data=None):
    """This function performs the mirroring of any selected Adonis locators
    and their associated sensor nodes, including value remapping nodes.
    All the relevant data for each of the locators is retrieved and stored in
    a dictionary. Any mirrorable entity will get their name mirrored.
    Positional parameters will be flipped in the X axis.

    Args:
        left_convention (str): String parameter defining the naming convention
            for left-side objects. The convention includes a '*' wildcard to
            define prefixes ('abc_*') or suffixes ('*_abc').
        right_convention (str): String parameter defining the naming convention
            for right-side objects. The convention includes a '*' wildcard to
            define prefixes ('abc_*') or suffixes ('*_abc').
        report_data (dict, optional): Dictionary to store the errors and warnings.
            Defaults to None.
    """
    selection = get_selected_locators()

    if not selection:
        if report_data is not None:
            report_data["warnings"].append("Locators not mirrored because not "
                                           "found in the selection.")
        return
    for locator in selection:
        locator_data = None
        if cmds.nodeType(locator) in [LocatorTypes.DISTANCE,
                                      LocatorTypes.ROTATION,
                                      LocatorTypes.POSITION]:
            locator_data = {
                "type": cmds.nodeType(locator),
                "name": None,
                "scale": cmds.getAttr("{0}.scale".format(locator)),
                "drawOutput": cmds.getAttr(
                    "{0}.drawOutput".format(locator))}

            mirror_name = get_mirror_name(locator, left_convention,
                                          right_convention)
            if mirror_name is None:
                report_naming_convention_error(locator, left_convention,
                                               right_convention, report_data)
                continue

            locator_data["name"] = mirror_name
        if cmds.nodeType(locator) in [LocatorTypes.DISTANCE,
                                      LocatorTypes.ROTATION]:
            locator_data["startPosition"] = [
                - cmds.getAttr("{0}.startPositionX".format(locator)),
                cmds.getAttr("{0}.startPositionY".format(locator)),
                cmds.getAttr("{0}.startPositionZ".format(locator))]
            locator_data["endPosition"] = [
                - cmds.getAttr("{0}.endPositionX".format(locator)),
                cmds.getAttr("{0}.endPositionY".format(locator)),
                cmds.getAttr("{0}.endPositionZ".format(locator))]

            # Start Position
            start_connections = cmds.listConnections(
                "{0}.startPosition".format(locator))
            if start_connections and len(start_connections) == 1:
                if cmds.nodeType(
                        start_connections[0]) == "decomposeMatrix":
                    matrix_input = cmds.listConnections(
                        "{0}.inputMatrix".format(start_connections[0]))
                    if matrix_input:
                        mirror_input = get_mirror_name(matrix_input[0],
                                                       left_convention,
                                                       right_convention)
                        if mirror_input is None:
                            report_mirror_connection_warning(matrix_input[0], mirror_name,
                                                             "startPosition", report_data)
                            mirror_input = matrix_input[0]

                        if not cmds.objExists(mirror_input):
                            report_mirror_connection_error(mirror_input, locator,
                                                           "startPosition", mirror_name,
                                                           report_data)
                        else:
                            locator_data["startPositionConnection"] = mirror_input
            # Start Matrix
            get_input_matrix_data(locator, locator_data, "startMatrix",
                                  left_convention, right_convention, report_data=report_data)
            # End Position
            end_connections = cmds.listConnections(
                "{0}.endPosition".format(locator))
            if end_connections and len(end_connections) == 1:
                if cmds.nodeType(end_connections[0]) == "decomposeMatrix":
                    matrix_input = cmds.listConnections(
                        "{0}.inputMatrix".format(end_connections[0]))
                    if matrix_input:
                        mirror_input = get_mirror_name(matrix_input[0],
                                                       left_convention,
                                                       right_convention)
                        if mirror_input is None:
                            report_mirror_connection_warning(matrix_input[0], mirror_name,
                                                             "endPosition", report_data)
                            mirror_input = matrix_input[0]

                        if not cmds.objExists(mirror_input):
                            report_mirror_connection_error(mirror_input, locator,
                                                           "endPosition", mirror_name,
                                                           report_data)
                        else:
                            locator_data["endPositionConnection"] = mirror_input
            # End Matrix
            get_input_matrix_data(locator, locator_data, "endMatrix",
                                  left_convention, right_convention, report_data=report_data)
        if cmds.nodeType(locator) == LocatorTypes.ROTATION:
            # Mid Position
            mid_connections = cmds.listConnections(
                "{0}.midPosition".format(locator))
            if mid_connections and len(mid_connections) == 1:
                if cmds.nodeType(mid_connections[0]) == "decomposeMatrix":
                    matrix_input = cmds.listConnections(
                        "{0}.inputMatrix".format(mid_connections[0]))
                    if matrix_input:
                        mirror_input = get_mirror_name(matrix_input[0],
                                                       left_convention,
                                                       right_convention)
                        if mirror_input is None:
                            report_mirror_connection_warning(matrix_input[0], mirror_name,
                                                             "midPosition", report_data)
                            mirror_input = matrix_input[0]

                        if not cmds.objExists(mirror_input):
                            report_mirror_connection_error(mirror_input, locator,
                                                           "midPosition", mirror_name,
                                                           report_data)
                        else:
                            locator_data["midPositionConnection"] = mirror_input
            locator_data["midPosition"] = [
                - cmds.getAttr("{0}.midPositionX".format(locator)),
                cmds.getAttr("{0}.midPositionY".format(locator)),
                cmds.getAttr("{0}.midPositionZ".format(locator))]
            # Mid Matrix
            get_input_matrix_data(locator, locator_data, "midMatrix",
                                  left_convention, right_convention, report_data=report_data)
        if cmds.nodeType(locator) == LocatorTypes.POSITION:
            # Position
            locator_data["position"] = [
                - cmds.getAttr("{0}.positionX".format(locator)),
                cmds.getAttr("{0}.positionY".format(locator)),
                cmds.getAttr("{0}.positionZ".format(locator))]
            position_connections = cmds.listConnections(
                "{0}.position".format(locator))
            if position_connections and len(position_connections) == 1:
                if cmds.nodeType(
                        position_connections[0]) == "decomposeMatrix":
                    matrix_input = cmds.listConnections(
                        "{0}.inputMatrix".format(position_connections[0]))
                    if matrix_input:
                        mirror_input = get_mirror_name(matrix_input[0],
                                                       left_convention,
                                                       right_convention)
                        if mirror_input is None:
                            report_mirror_connection_warning(matrix_input[0], mirror_name,
                                                             "position", report_data)
                            mirror_input = matrix_input[0]

                        if not cmds.objExists(mirror_input):
                            report_mirror_connection_error(mirror_input, locator,
                                                           "position", mirror_name,
                                                           report_data)
                        else:
                            locator_data["positionConnection"] = mirror_input
            # Matrix
            get_input_matrix_data(locator, locator_data, "positionMatrix",
                                  left_convention, right_convention, report_data=report_data)
        if locator_data:
            new_locator = create_locator(locator_data)
            sensor_data = get_sensor(locator, left_convention,
                                     right_convention, report_data=report_data)
            create_sensor(sensor_data, new_locator)


def get_sensor_remap_data(sensor, type_suffix, sensor_data):
    """Get the sensor remap data and ingest the data into the sensor_data dictionary.
    The information to be gathered from the sensor are: min and max for the input and output
    and the ramp attributes.

    Args:
        sensor (str): Name of the sensor from which to extract the implicit remap data from.
        type_suffix (str): Suffix naming convention for obtaining the right attribute names
            for the remap data. Eg. Distance, Angle, Acceleration, Velocity.
        sensor_data (dict): Dictionary to which to fill the remap data to. This dictionary will
            contain all the relevant data to mirror a sensor.
            The modification of this data is implicit.
    """
    if not type_suffix or not sensor or not sensor_data:
        return
    attr = "inputMin{0}".format(type_suffix)
    sensor_data[attr] = cmds.getAttr(
        "{0}.{1}".format(sensor, attr))
    attr = "inputMax{0}".format(type_suffix)
    sensor_data[attr] = cmds.getAttr(
        "{0}.{1}".format(sensor, attr))
    attr = "outputMin{0}".format(type_suffix)
    sensor_data[attr] = cmds.getAttr(
        "{0}.{1}".format(sensor, attr))
    attr = "outputMax{0}".format(type_suffix)
    sensor_data[attr] = cmds.getAttr(
        "{0}.{1}".format(sensor, attr))

    remap_attr = ""
    if type_suffix == "Distance":
        remap_attr = "distanceRemap"
    elif type_suffix == "Angle":
        remap_attr = "angleRemap"
    elif type_suffix == "Velocity":
        remap_attr = "velocityRemap"
    elif type_suffix == "Acceleration":
        remap_attr = "accelerationRemap"
    if remap_attr:
        sensor_data[remap_attr] = get_ramp_data(sensor, remap_attr)


def get_sensor_decompose_matrix_data(sensor, sensor_data, attr, 
                                     left_convention, right_convention,
                                     report_data=None):
    """Get the decompose matrix data and ingest the data into the sensor_data dictionary.

    Args:
        sensor (str): Name of the sensor from which to extract the implicit decompose matrix data from.
        sensor_data (dict): Dictionary to which to fill the decompose matrix data to. This dictionary will
            contain all the relevant data to mirror a sensor.
            The modification of this data is implicit.
        attr (str): Input attribute name from which to check the input connection
            for the decompose matrix node.
        left_convention (str): String parameter defining the naming convention
            for left-side objects. The convention includes a '*' wildcard to
            define prefixes ('abc_*') or suffixes ('*_abc').
        right_convention (str): String parameter defining the naming convention
            for right-side objects. The convention includes a '*' wildcard to
            define prefixes ('abc_*') or suffixes ('*_abc').
        report_data (dict, optional): Dictionary to store the errors and warnings.
            Defaults to None.
    """
    if not sensor or not sensor_data or not attr:
        return
    if not left_convention or not right_convention:
        return
    start_connections = cmds.listConnections(
        "{0}.{1}".format(sensor, attr)) or []
    if not start_connections:
        return
    if not len(start_connections) == 1:
        return
    if cmds.nodeType(start_connections[0]) != "decomposeMatrix":
        return
    matrix_input = cmds.listConnections(
        "{0}.inputMatrix".format(start_connections[0]))
    if not matrix_input:
        return
    mirror_input = get_mirror_name(matrix_input[0],
                                   left_convention,
                                   right_convention)

    if not mirror_input:
        report_mirror_connection_warning("{0}.worldMatrix".format(matrix_input[0]), sensor_data["name"],
                                         attr, report_data)
        mirror_input = matrix_input[0]

    if not cmds.objExists(mirror_input):
        report_mirror_connection_error(mirror_input, sensor, attr,
                                       sensor_data["name"], report_data)
        return
    sensor_data["{0}Connection".format(attr)] = mirror_input


def get_input_matrix_data(node, node_data, attr, left_convention, right_convention, report_data=None):
    """Retrieve the mirrored input matrix connection for a node attribute.

    This function examines the specified attribute on the given node to find an
    incoming connection that supplies a matrix (via its plug). If such a connection
    exists, the function uses the provided left and right naming conventions to generate
    a mirrored name. The resulting mirrored matrix identifier is stored in the node_data
    dictionary under the key defined by the attr parameter.

    Args:
        node (str): The name of the node from which to retrieve the matrix connection.
        node_data (dict): A dictionary to store node-related data; this function updates it
            by adding the mirrored matrix connection identified by attr.
        attr (str): The attribute name on the node to query for input matrix connections.
        left_convention (str): The naming convention string for left-side objects, typically
            including a wildcard (e.g., 'L_*').
        right_convention (str): The naming convention string for right-side objects, typically
            including a wildcard (e.g., 'R_*').
        report_data (dict, optional): Dictionary to store errors and warnings. Defaults to None.
    """
    if not node or not node_data or not attr:
        return
    if not left_convention or not right_convention:
        return
    matrix_input = cmds.listConnections("{0}.{1}".format(node, attr),
                                        source=True, destination=False, plugs=True) or []
    if not matrix_input:
        return

    connection_source = matrix_input[0].partition(".")[0]
    connection_plug = matrix_input[0].partition(".")[-1]
    mirror_input = get_mirror_name(connection_source,
                                   left_convention,
                                   right_convention)

    if mirror_input:
        mirror_input = "{0}.{1}".format(mirror_input, connection_plug)
    else:
        report_mirror_connection_warning(matrix_input[0], node_data["name"],
                                         attr, report_data)
        mirror_input = matrix_input[0]

    if not cmds.objExists(mirror_input):
        report_mirror_connection_error(mirror_input, node, attr,
                                       node_data["name"], report_data)
        return
    node_data[attr] = mirror_input


def set_sensor_remap_data(sensor, sensor_data, type_suffix):
    """Set the sensor remap data to the sensor from sensor_data dictionary.
    The information to set to the sensor are: min and max for the input and output
    and the ramp attributes.

    Args:
        sensor (str): Name of the sensor to which to apply the sensor remap data.
        sensor_data (dict): Dictionary from which to extract the remap data.
            This dictionary will contain all the relevant data of the mirrored sensor.
        type_suffix (str): Suffix naming convention for setting the right attribute names
            for the remap data. Eg. Distance, Angle, Acceleration, Velocity.
    """
    if not sensor or not sensor_data or not type_suffix:
        return
    if not cmds.objExists(sensor):
        return
    attr = "inputMin{0}".format(type_suffix)
    cmds.setAttr("{0}.{1}".format(sensor, attr),
                 sensor_data[attr])
    attr = "inputMax{0}".format(type_suffix)
    cmds.setAttr("{0}.{1}".format(sensor, attr),
                 sensor_data[attr])
    attr = "outputMin{0}".format(type_suffix)
    cmds.setAttr("{0}.{1}".format(sensor, attr),
                 sensor_data[attr])
    attr = "outputMax{0}".format(type_suffix)
    cmds.setAttr("{0}.{1}".format(sensor, attr),
                 sensor_data[attr])
    
    remap_attr = ""
    if type_suffix == "Distance":
        remap_attr = "distanceRemap"
    elif type_suffix == "Angle":
        remap_attr = "angleRemap"
    elif type_suffix == "Velocity":
        remap_attr = "velocityRemap"
    elif type_suffix == "Acceleration":
        remap_attr = "accelerationRemap"

    set_ramp_data(sensor, remap_attr, sensor_data[remap_attr])


def get_ramp_data(node, attribute):
    """This function gathers all the relevant data out of a ramp attribute.
    That would include the index, the position, the value and the 
    interpolation type (None, Linear, Smooth, Spline).

    Args:
        node (str): String parameter defining the name of the node to query the attribute from.
        attribute (str): Remap attribute name to gather data from.

    Returns:
        list: A list of dictionaries including for each ramp index entry the 
            Index, Position, FloatValue and Interp.
    """
    remap_data = []
    full_attr = "{0}.{1}".format(node, attribute)
    remap_indices = cmds.getAttr(full_attr, multiIndices=True) or []
    if len(remap_indices) == 0:
        return remap_data
    for idx in remap_indices:
        attr_prefix = "{0}[{1}].{2}".format(full_attr, idx, attribute)
        pos = cmds.getAttr("{0}_Position".format(attr_prefix))
        val = cmds.getAttr("{0}_FloatValue".format(attr_prefix))
        interp = cmds.getAttr("{0}_Interp".format(attr_prefix))
        remap_data.append({
            "Index": idx,
            "Position": pos,
            "FloatValue": val,
            "Interp": interp,
        })
    return remap_data


def set_ramp_data(node, attribute, remap_data):
    """This function sets the relevant data to a ramp attribute.
    Data to be set is the Position, FloatValue and Interp values. 

    Args:
        node (str): String parameter defining the name of the node to query the attribute from.
        attribute (str): Remap attribute name to gather data from.
        remap_data (list): A list of dictionaries including for each ramp index entry the 
            Index, Position, FloatValue and Interp.
    """
    if not remap_data:
        return
    full_attr = "{0}.{1}".format(node, attribute)
    for idx, entry in enumerate(remap_data):
        attr_prefix = "{0}[{1}].{2}".format(full_attr, entry["Index"], attribute)
        cmds.setAttr("{0}_Position".format(attr_prefix), entry["Position"])
        cmds.setAttr("{0}_FloatValue".format(attr_prefix), entry["FloatValue"])
        cmds.setAttr("{0}_Interp".format(attr_prefix), entry["Interp"])


@undo_chunk
def apply_mirror(left_convention, right_convention, report_data=None):
    """This function takes care of mirroring any selected locators first and
    then mirror any selected geometries with assigned muscle deformers.
    If no locators or muscle geometries are selected, the user will be informed
    that the mirroring process cannot take place.
    Before mirroring is triggered, the user is asked if a safe copy of the scene
    was saved before proceeding.

    Args:
        left_convention (str): String parameter defining the naming convention
            for left-side objects. The convention includes a '*' wildcard to
            define prefixes ('abc_*') or suffixes ('*_abc').
        right_convention (str): String parameter defining the naming convention
            for right-side objects. The convention includes a '*' wildcard to
            define prefixes ('abc_*') or suffixes ('*_abc').
        report_data (dict, optional): Dictionary to store errors and warnings.
            Defaults to None.

    Returns:
        bool: False if the mirroring of the muscles did not complete
            successfully or if the selection is empty or the user aborts the
            execution. True otherwise.
    """
    if report_data is not None:
        if not isinstance(report_data, dict):
            report_data = None
            logging.warning("The mirroring process will not report possible errors "
                            "or warnings because `report_data` argument is not valid.")
        else:
            report_data.clear()
            report_data["errors"] = []
            report_data["warnings"] = []
    selection = cmds.ls(selection=True, dag=True,
                        type=["mesh", LocatorTypes.DISTANCE,
                              LocatorTypes.ROTATION, LocatorTypes.POSITION])
    if len(selection) == 0:
        msg_err = ("Nothing mirrored because there were no muscles nor locators found in the selection.")
        if report_data is not None:
            report_data["errors"].append(msg_err)
        return False

    with cursor.wait_cursor_context():
        apply_mirror_locators(left_convention, right_convention, report_data)
        cmds.select(selection)
        apply_mirror_activation(left_convention, right_convention, report_data)
        cmds.select(selection)
        apply_mirror_muscles(left_convention, right_convention, report_data)

    return True
