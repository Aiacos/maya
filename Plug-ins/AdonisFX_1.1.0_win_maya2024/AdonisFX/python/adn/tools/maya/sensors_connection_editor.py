import maya.cmds as cmds

from adn.ui.widgets.dialogs import msg_box
from adn.ui.maya.window import main_window
from adn.utils.maya.constants import AdnMayaNodeNames as MAYA_CONST
from adn.utils.maya.undo_stack import undo_chunk


def collect_connection_info_source_nodes():
    """Collect all the float attributes in the nodes selected.

    Returns:
        source_nodes (dict): Dictionary with key:node and value:list of float attributes to
                             use as source plugs.
        source_nodes_nice_names (dict): Dictionary with key:node and value:short name for that
                                        locator/sensor.
    """
    source_nodes = dict()
    source_nodes_nice_names = dict()

    selection = cmds.ls(selection=True, long=True)
    if not selection:
        # Empty selection
        msg_box(main_window(), "error",
                "Selection is empty. Please, select one or more nodes and "
                "try again")
        return source_nodes, source_nodes_nice_names

    for node in selection:
        node_type = cmds.nodeType(node)
        float_attributes = list()

        # Find the float attributes in the node selected
        for attribute in cmds.listAttr(node):
            if not cmds.attributeQuery(attribute, node=node, connectable=True,
                                       exists=True, typeExact=node_type):
                continue
            node_attribute = "{0}.{1}".format(node, attribute)
            if cmds.getAttr(node_attribute, type=True) == "float":
                float_attributes.append(attribute)

        if float_attributes:
            source_nodes_nice_names[node] = cmds.ls(node, shortNames=True)[0]
            source_nodes[node] = float_attributes
        else:
            # If there is no float attributes in the node selected
            # try to find them in the relatives to the node
            relatives = cmds.listRelatives(node, fullPath=True)
            if not relatives:
                continue

            for relative in relatives:
                relative_type = cmds.nodeType(relative)
                float_attributes = list()

                # Find the float attributes in the relative node
                for attribute in cmds.listAttr(relative):
                    if not cmds.attributeQuery(attribute, node=relative, connectable=True,
                                               exists=True, typeExact=relative_type):
                        continue
                    node_attribute = "{0}.{1}".format(relative, attribute)
                    if cmds.getAttr(node_attribute, type=True) == "float":
                        float_attributes.append(attribute)

                if float_attributes:
                    source_nodes_nice_names[relative] = cmds.ls(relative, shortNames=True)[0]
                    source_nodes[relative] = float_attributes

    if not source_nodes:
        # No float attributes in the nodes selected
        msg_box(main_window(), "error",
                "Wrong selection. Please, select one or more nodes that have at least one float attribute and try again.")

    return source_nodes, source_nodes_nice_names


def collect_destination_nodes_plugs():
    """Collect, based on the selected elements, all the nodes found.

    Returns:
        nodes (dict): Dictionary with key:node and value:list of float plugs.
        nodes_short_names (dict): Dictionary with key:node and value:short name for that node.
    """
    nodes_dict = dict()
    nodes_short_names = dict()

    selection = cmds.ls(selection=True, long=True)
    if not selection:
        msg_box(main_window(), "error",
                "Empty selection. Please, select one or more nodes that will be used as the "
                "destination of the connections and try again.")
        return nodes_dict, nodes_short_names

    # Try to find AdonisFX Deformers
    nodes = list()
    for node in selection:
        shape_nodes = cmds.listRelatives(node, shapes=True, fullPath=True) or []
        if not shape_nodes:
            # Not a mesh
            nodes.append(node)
            continue

        for shape in shape_nodes:
            # Mesh. Add the deformers found.
            node_history = cmds.listHistory(shape)
            deformers = [x for x in node_history
                         if cmds.nodeType(x) in MAYA_CONST.ADN_DEFORMERS] or []
            if deformers:
                nodes.extend(deformers)
            else:
                nodes.append(shape)

    nodes = list(set(nodes))
    for node in nodes:
        node_type = cmds.nodeType(node)
        float_attributes = list()

        for attribute in cmds.listAttr(node):
            if not cmds.attributeQuery(attribute, node=node, connectable=True,
                                       exists=True, typeExact=node_type):
                continue
            node_attribute = "{0}.{1}".format(node, attribute)
            if cmds.getAttr(node_attribute, type=True) == "float":
                float_attributes.append(attribute)

        nodes_dict[node] = float_attributes
        nodes_short_names[node] = cmds.ls(node, shortNames=True)[0]

    return nodes_dict, nodes_short_names


@undo_chunk
def connect_sensor_output(source_plug, node_plug):
    """Connects the plugs provided.

    Args:
        source_plug (str): Name of the attribute to make the connection, will
                           be the source of the connection.
        node_plug (str): Name of the attribute to make the connection, will
                         be the destination of the connection.

    Returns:
        true: connection succeeded
        false: connection did not succeed.
    """
    # Check if plugs exist
    if not cmds.objExists(source_plug) or not cmds.objExists(node_plug):
        msg_box(main_window(), "error",
                "Could not make the connection. Please, make sure that source and destination "
                "are valid and try again.")
        return False

    # Check if source and destination plugs are the same
    if source_plug == node_plug:
        msg_box(main_window(), "error",
                "Cannot connect attribute {0} to itself.".format(source_plug))
        return False

    # Check if connection is already made. If it is ask the user to override it or not.
    if cmds.connectionInfo(node_plug, isExactDestination=True):
        if msg_box(main_window(), "question",
                   "The destination plug is already connected. "
                   "Do you want to override the connection?"):
            cmds.connectAttr(source_plug, node_plug, force=True)
        else:
            return True
    else:
        # Not connected. Connect.
        cmds.connectAttr(source_plug, node_plug)

    print("[AdonisFX] Connected {0} to {1}".format(source_plug, node_plug))
    return True
