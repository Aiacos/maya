import maya.cmds as cmds
from adn.utils.constants import UiConstants, DeformerTypes
from adn.utils.maya.undo_stack import undo_chunk


@undo_chunk
def configure_attributes(node, attribute_dict):
    """Set the values of all attributes from a dictionary to the given node.

    Args:
        node (str): name of the node to configure.
        attribute_dict (dict): dictionary with all attribute names and their
            respective values to set.
    """
    for attr_name, value in attribute_dict.items():
        node_attribute = "{0}.{1}".format(node, attr_name)
        if not cmds.objExists(node_attribute):
            print("{0} No attribute matches name {1}."
                  "".format(UiConstants.LOG_PREFIX, node_attribute))
            continue

        if type(value) is list and len(value) == 3:
            cmds.setAttr(node_attribute,
                         value[0], value[1], value[2],
                         type="float3")
        else:
            cmds.setAttr(node_attribute, value)


def disconnect_attribute_from_source(attribute):
    """Checks if an attribute has a source connection and disconnects it
    in case it has one.

    Args:
        attribute (str): name of the attribute to disconnect.
    """
    if not cmds.connectionInfo(attribute, isDestination=True):
        return
    source = cmds.connectionInfo(attribute, sourceFromDestination=True)
    if not source:
        return
    cmds.disconnectAttr(source, attribute)


def disconnect_nodes(nodes):
    """Disconnects all connections from a list of nodes.

    This function iterates through a list of nodes and disconnects all their
    incoming and outgoing connections. If the node is a deformer, it bypasses
    the connections between the input and output geometries by connecting the
    input geometry directly to the output geometry.

    Args:
        nodes (list): List of node names to disconnect.
    """
    if not nodes:
        return

    bypass_deformer_geometry_plugs(nodes)

    for node in nodes:
        node_connections = cmds.listConnections(node, connections=True, plugs=True) or []
        for connection_index in range(len(node_connections) // 2):
            connection_a = node_connections[connection_index * 2]
            connection_b = node_connections[connection_index * 2 + 1]
            try:
                cmds.disconnectAttr(connection_a, connection_b)
            except:
                cmds.disconnectAttr(connection_b, connection_a)


def bypass_deformer_geometry_plugs(nodes):
    """Bypasses the connections between input and output geometries for deformers.

    This function iterates through a list of nodes and, if the node is a deformer,
    it connects the input geometry directly to the output geometry, effectively
    bypassing the deformer. This is useful for cleaning up the scene or preparing
    it for import.

    Args:
        nodes (list): List of nodes to process.
    """
    for node in nodes:
        if cmds.nodeType(node, apiType=True) != "kPluginDeformerNode":
            continue
        in_plug = "{0}.input[0].inputGeometry".format(node)
        out_plug = "{0}.outputGeometry[0]".format(node)
        if not cmds.objExists(in_plug) or not cmds.objExists(out_plug):
            continue
        left_plug = cmds.listConnections(in_plug, source=True, destination=False, plugs=True) or []
        right_plug = cmds.listConnections(out_plug, source=False, destination=True, plugs=True) or []
        if left_plug and right_plug:
            cmds.connectAttr(left_plug[0], right_plug[0], force=True)
