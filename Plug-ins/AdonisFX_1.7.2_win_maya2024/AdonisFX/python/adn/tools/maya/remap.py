import logging

import maya.cmds as cmds

from adn.utils.constants import OtherNodeTypes


def get_remap_value_node_setup(node):
    """Gathers the setup of a maya remapValue node and returns it in a
    dictionary format.

    Args:
        node (str): name of an existing maya remapValue node to extract
            setup from.
    Returns:
        dict: all settings of the queried node. None if the node is not
            found or it is not a remapValue node.
    """
    if not node:
        return None
    if not cmds.objExists(node):
        return None
    if cmds.nodeType(node) != "remapValue":
        return None
    # Name
    name = cmds.ls(node, shortNames=True)[0]
    # Input value and ranges
    input_value = cmds.getAttr("{0}.inputValue".format(node))
    input_range = [
        cmds.getAttr("{0}.inputMin".format(node)),
        cmds.getAttr("{0}.inputMax".format(node))
    ]
    output_range = [
        cmds.getAttr("{0}.outputMin".format(node)),
        cmds.getAttr("{0}.outputMax".format(node))
    ]
    # Ramp attribute
    ramp = []
    indices = cmds.getAttr("{0}.value".format(node), multiIndices=True) or []
    for i in indices:
        child_plug = "{0}.value[{1}]".format(node, i)
        value = cmds.getAttr("{0}.value_FloatValue".format(child_plug))
        position = cmds.getAttr("{0}.value_Position".format(child_plug))
        interp = cmds.getAttr("{0}.value_Interp".format(child_plug))
        ramp.append({
            "value": value,
            "position": position,
            "interpolation": interp
        })
    # Connections
    in_conn = cmds.listConnections(node, source=True, destination=False,
                                   plugs=True, connections=True) or []
    out_conn = cmds.listConnections(node, source=False, destination=True,
                                    plugs=True, connections=True) or []
    return {
        "name": name,
        "input_value": input_value,
        "input_range": input_range,
        "output_range": output_range,
        "ramp": ramp,
        "in_conn": in_conn,
        "out_conn": out_conn
    }


def create_remap(data):
    """Creates an AdnRemap node and configures the settings and connections
    with the information provided in the input dictionary.

    Args:
         data (dict): all settings to configure the new node.

    """
    name = "{0}_AdnRemap".format(data["name"]) if "name" in data else OtherNodeTypes.REMAP
    if cmds.ls(name) and cmds.nodeType(name) == OtherNodeTypes.REMAP:
        logging.warning("The '{0}' node to create already exists. "
                        "Skipping creation and setup".format(name))
        return
    # Create
    node = cmds.createNode(OtherNodeTypes.REMAP, name=name)
    # Input value and ranges
    if "input_value" in data:
        input_value = data["input_value"]
        cmds.setAttr("{0}.input".format(node), input_value)
    if "input_range" in data:
        input_range = data["input_range"]
        cmds.setAttr("{0}.inputMin".format(node), input_range[0])
        cmds.setAttr("{0}.inputMax".format(node), input_range[1])
    if "output_range" in data:
        output_range = data["output_range"]
        cmds.setAttr("{0}.outputMin".format(node), output_range[0])
        cmds.setAttr("{0}.outputMax".format(node), output_range[1])
    # Ramp
    if "ramp" in data:
        ramp = data["ramp"]
        for i, entry in enumerate(ramp):
            cmds.setAttr("{0}.remap[{1}].remap_FloatValue".format(node, i),
                         entry["value"])
            cmds.setAttr("{0}.remap[{1}].remap_Position".format(node, i),
                         entry["position"])
            cmds.setAttr("{0}.remap[{1}].remap_Interp".format(node, i),
                         entry["interpolation"])
    # Connections
    if "in_conn" in data:
        in_conn = data["in_conn"]
        for c in range(0, len(in_conn), 2):
            destination = in_conn[c].split(".")[-1]
            if destination == "inputValue":
                destination = "input"
            destination = "{0}.{1}".format(node, destination)
            if cmds.objExists(in_conn[c + 1]) and cmds.objExists(destination):
                cmds.connectAttr(in_conn[c + 1], destination, force=True)
    if "out_conn" in data:
        out_conn = data["out_conn"]
        for c in range(0, len(out_conn), 2):
            source = out_conn[c].split(".")[-1]
            if source == "outValue":
                source = "output"
            source = "{0}.{1}".format(node, source)
            if cmds.objExists(source) and cmds.objExists(out_conn[c + 1]):
                cmds.connectAttr(source, out_conn[c + 1], force=True)
