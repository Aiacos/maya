import re

import maya.cmds as cmds
from adn.ui.maya.window import main_window
from adn.ui.widgets.dialogs import msg_box
from adn.utils.maya.undo_stack import undo_chunk, undo_disabled
from adn.utils.maya.checkers import plugin_check, world_matrix_plug_check
from adn.utils.maya.constants import AdnMayaNodeNames as MAYA_CONST


@undo_chunk
def create_locator_logo():
    """Create a cool logo locator that represents AdonisFX from Inbibo."""
    plugin_check()
    base_name = "adnLocator"
    transform_name = "{0}1".format(base_name)
    transform = cmds.createNode("transform", name=transform_name)
    index = transform[len(base_name):]
    locator_name = "{0}Shape{1}".format(base_name, index)
    cmds.createNode("AdnLocator", name=locator_name, parent=transform)
    cmds.select(transform)
    msg_box(None, "info",
            "\"{0}\" locator has been created successfully."
            "".format(transform))


def get_custom_base_name(custom_name):
    """Obtain a custom name's base name in case it has an index.
    Args:
        custom_name (str): Custom name to separate.

    Returns:
        str: Returns the base name with no index.
    """
    # iterate through custom_name in reverse order
    for i in range(len(custom_name) - 1, -1, -1):
        # check character at index (from right to left)
        if not custom_name[i].isdigit():
            return custom_name[:i + 1]


@undo_chunk
def create_locator_distance(custom_name=None, creation_dialog=True):
    """Create a distance locator between two selected objects.
    Args:
        custom_name (str, optional): Custom name to give to the locator. Defaults to None.
        creation_dialog (bool, optional): Flag to control if the creation dialog should
            be displayed. Defaults to True.

    Returns:
        str: Returns the name of the AdnLocatorDistance shape generated.
    """
    plugin_check()
    selection = cmds.ls(sl=True)
    if not world_matrix_plug_check(selection):
        msg_box(None, "error",
                "Wrong selection. Please select only transform nodes to create a locator.")
        return

    base_name = "adnLocatorDistance" if not custom_name else get_custom_base_name(custom_name)
    transform_name = "adnLocatorDistance1" if not custom_name else custom_name
    transform = cmds.createNode("transform", name=transform_name)
    index = transform[len(base_name):]
    locator_name = "{0}Shape{1}".format(base_name, index)
    locator = cmds.createNode("AdnLocatorDistance", name=locator_name, parent=transform)
    if len(selection) > 0:
        start_node = selection[0]
        start_decompose = None
        start_connections = cmds.listConnections(start_node, type="decomposeMatrix")
        if start_connections:
            start_decompose = start_connections[0]
        else:
            start_decompose = cmds.createNode("decomposeMatrix")
            cmds.connectAttr("{0}.worldMatrix[0]".format(start_node),
                             "{0}.inputMatrix".format(start_decompose))
        cmds.connectAttr("{0}.outputTranslate".format(start_decompose),
                         "{0}.startPosition".format(locator))
    if len(selection) > 1:
        end_node = selection[1]
        end_decompose = None
        end_connections = cmds.listConnections(end_node, type="decomposeMatrix")
        if end_connections:
            end_decompose = end_connections[0]
        else:
            end_decompose = cmds.createNode("decomposeMatrix")
            cmds.connectAttr("{0}.worldMatrix[0]".format(end_node),
                             "{0}.inputMatrix".format(end_decompose))
        cmds.connectAttr("{0}.outputTranslate".format(end_decompose),
                         "{0}.endPosition".format(locator))
    cmds.select(transform)
    if creation_dialog:
        msg_box(None, "info",
                "\"{0}\" locator has been created successfully."
                "".format(transform))
    return locator


@undo_chunk
def create_locator_position(custom_name=None, creation_dialog=True):
    """Create a position locator and make the connections with the first selected 
       object.
    Args:
        custom_name (str, optional): Custom name to give to the locator. Defaults to None.
        creation_dialog (bool, optional): Flag to control if the creation dialog should
            be displayed. Defaults to True.

    Returns:
        str: Returns the name of the AdnLocatorPosition shape generated.
    """
    plugin_check()
    selection = cmds.ls(selection=True, long=True)
    if not world_matrix_plug_check(selection):
        msg_box(None, "error",
                "Wrong selection. Please select only transform nodes to create a locator.")
        return

    base_name = "adnLocatorPosition" if not custom_name else get_custom_base_name(custom_name)
    transform_name = "adnLocatorPosition1" if not custom_name else custom_name
    transform = cmds.createNode("transform", name=transform_name)
    index = transform[len(base_name):]
    locator_name = "{0}Shape{1}".format(base_name, index)
    locator = cmds.createNode("AdnLocatorPosition", name=locator_name, parent=transform)

    if len(selection) > 0:
        position_node = selection[0]
        position_decompose = None
        pos_connections = cmds.listConnections(position_node, type="decomposeMatrix")
        if pos_connections:
            position_decompose = pos_connections[0]
        else:
            position_decompose = cmds.createNode("decomposeMatrix")
            cmds.connectAttr("{0}.worldMatrix[0]".format(position_node),
                             "{0}.inputMatrix".format(position_decompose))
        cmds.connectAttr("{0}.outputTranslate".format(position_decompose),
                         "{0}.position".format(locator))
    cmds.select(transform)
    if creation_dialog:
        msg_box(None, "info",
                "\"{0}\" locator has been created successfully."
                "".format(transform))
    return locator


@undo_chunk
def create_locator_rotation(custom_name=None, creation_dialog=True):
    """Create a rotation locator with it's connections based on the number of selected 
       objects.
    Args:
        custom_name (str, optional): Custom name to give to the locator. Defaults to None.
        creation_dialog (bool, optional): Flag to control if the creation dialog should
            be displayed. Defaults to True.

    Returns:
        str: Returns the name of the AdnLocatorRotation shape generated.
    """
    plugin_check()
    selection = cmds.ls(selection=True, long=True)
    if not world_matrix_plug_check(selection):
        msg_box(None, "error",
                "Wrong selection. Please select only transform nodes to create a locator.")
        return

    base_name = "adnLocatorRotation" if not custom_name else get_custom_base_name(custom_name)
    transform_name = "adnLocatorRotation1" if not custom_name else custom_name
    transform = cmds.createNode("transform", name=transform_name)
    index = transform[len(base_name):]
    locator_name = "{0}Shape{1}".format(base_name, index)
    locator = cmds.createNode("AdnLocatorRotation", name=locator_name, parent=transform)
    if len(selection) > 0:
        start_node = selection[0]
        start_decompose = None
        start_connections = cmds.listConnections(start_node, type="decomposeMatrix")
        if start_connections:
            start_decompose = start_connections[0]
        else:
            start_decompose = cmds.createNode("decomposeMatrix")
            cmds.connectAttr("{0}.worldMatrix[0]".format(start_node),
                             "{0}.inputMatrix".format(start_decompose))
        cmds.connectAttr("{0}.outputTranslate".format(start_decompose),
                         "{0}.startPosition".format(locator))
    if len(selection) > 1:
        mid_node = selection[1]
        mid_decompose = None
        mid_connections = cmds.listConnections(mid_node, type="decomposeMatrix")
        if mid_connections:
            mid_decompose = mid_connections[0]
        else:
            mid_decompose = cmds.createNode("decomposeMatrix")
            cmds.connectAttr("{0}.worldMatrix[0]".format(mid_node),
                             "{0}.inputMatrix".format(mid_decompose))
        cmds.connectAttr("{0}.outputTranslate".format(mid_decompose),
                         "{0}.midPosition".format(locator))
    if len(selection) > 2:
        end_node = selection[2]
        end_decompose = None
        end_connections = cmds.listConnections(end_node, type="decomposeMatrix")
        if end_connections:
            end_decompose = end_connections[0]
        else:
            end_decompose = cmds.createNode("decomposeMatrix")
            cmds.connectAttr("{0}.worldMatrix[0]".format(end_node),
                             "{0}.inputMatrix".format(end_decompose))
        cmds.connectAttr("{0}.outputTranslate".format(end_decompose),
                         "{0}.endPosition".format(locator))
    cmds.select(transform)
    if creation_dialog:
        msg_box(None, "info",
                "\"{0}\" locator has been created successfully."
                "".format(transform))
    return locator


def get_debugger_nodes():
    """Create or retrieve an AdnDebugLocator node and the data node connected.

    Returns:
        str: string name of the AdnDebugLocator node created.
        str: string name of the AdnDataNode node created.
        int: Next index available in the AdnDataNode.inputs plug
    """
    selection = cmds.ls(selection=True, long=True)

    # Locator
    adn_debug_locators = cmds.ls(type="AdnDebugLocator")
    debug_locator_found = False
    locator = None
    if adn_debug_locators:
        # Locator found
        locator = adn_debug_locators[0]
        debug_locator_found = True
    else:
        # Locator creation
        base_name = "adnDebug"
        transform_name = "{0}1".format(base_name)
        transform = cmds.createNode("transform", name=transform_name)
        index = transform[len(base_name):]
        locator_name = "{0}Shape{1}".format(base_name, index)
        locator = cmds.createNode("AdnDebugLocator", name=locator_name, parent=transform)

    # Data node
    adn_data_nodes = cmds.ls(type="AdnDataNode")
    data_node = None
    if adn_data_nodes:
        # Data node found
        data_node = adn_data_nodes[0]
    else:
        # Data node creation
        data_node = cmds.createNode("AdnDataNode")

    if not data_node or not locator:
        # This should never happen
        msg_box(main_window(), "error",
                "Failed to configure the debugger. Either AdnDataNode or AdnDebugLocator "
                "could not be retrieved.")
        return data_node, locator, None

    # Make connection
    locator_attr = "{0}.data".format(locator)
    data_node_attr = "{0}.message".format(data_node)
    is_connected = cmds.connectionInfo(locator_attr, isDestination=True)
    if not debug_locator_found or not is_connected:
        # Locator from scratch or not connected to anything
        cmds.connectAttr(data_node_attr, locator_attr)
    elif is_connected:
        # Connections found
        source = cmds.connectionInfo(locator_attr, sourceFromDestination=True)
        if source != data_node_attr:
            # Debug locator is being used by the user. Create a new one.
            base_name = "adnDebug"
            transform_name = "{0}1".format(base_name)
            transform = cmds.createNode("transform", name=transform_name)
            index = transform[len(base_name):]
            locator_name = "{0}Shape{1}".format(base_name, index)
            locator = cmds.createNode("AdnDebugLocator", name=locator_name, parent=transform)
            locator_attr = "{0}.data".format(locator)
            cmds.connectAttr(data_node_attr, locator_attr)

    # Next index available
    attr = "{0}.inputs".format(data_node)
    connections = cmds.listConnections(attr, connections=True) or []
    indices = [i.replace(attr, "") for i in connections if data_node in i]
    indices = [int(re.findall(r'\d+', i)[0]) for i in indices]
    next_index = max(indices) + 1 if indices else 0

    # Reset selection after creating new nodes
    cmds.select(selection)

    return locator, data_node, next_index

@undo_chunk
def connect_to_debugger(node):
    """Checks if the given node is connected by message to the AdnDataNode.
    In case it is not connected, then it makes the connection to ensure that
    the node is added to the debugger system.

    Args:
         node (str): name of the node to be connected to the debugger.
    """
    locator_node, data_node, next_index = get_debugger_nodes()
    connections = cmds.listConnections("{0}.inputs".format(data_node)) or []
    if node in connections:
        return
    if next_index is not None:
        cmds.connectAttr("{0}.message".format(node),
                         "{0}.inputs[{1}]".format(data_node, next_index))


@undo_chunk
def refresh_debug_graph():
    """Refreshes Maya AdonisFX debug graph. Creating missing "AdnDataNode" and
    "AdnDebugLocator" nodes. At the same time creates required connections
    between debug and deformer nodes.
    """
    plugin_check()

    deformer_nodes_scene = cmds.ls(type=MAYA_CONST.ADN_DEFORMERS)
    for deformer_node in deformer_nodes_scene:
        connect_to_debugger(deformer_node)
