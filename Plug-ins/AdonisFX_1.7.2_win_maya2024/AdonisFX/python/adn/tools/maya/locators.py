import re

import maya.cmds as cmds
from adn.utils.maya.undo_stack import undo_chunk
from adn.utils.maya.checkers import plugin_check, world_matrix_plug_check
from adn.utils.maya.constants import AdnMayaNodeNames as MAYA_CONST
from adn.utils.constants import UiConstants, OtherNodeTypes
from adn.commands.maya.scene import get_namespace


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
    print("{0} \"{1}\" locator has been created successfully."
          "".format(UiConstants.INFO_PREFIX, transform))


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
        print("{0} Wrong selection. Please select only transform nodes to create a locator."
              "".format(UiConstants.ERROR_PREFIX))
        return None

    base_name = "adnLocatorDistance" if not custom_name else get_custom_base_name(custom_name)
    transform_name = "adnLocatorDistance1" if not custom_name else custom_name
    transform = cmds.createNode("transform", name=transform_name)
    index = transform[len(base_name):]
    locator_name = "{0}Shape{1}".format(base_name, index)
    locator = cmds.createNode("AdnLocatorDistance", name=locator_name, parent=transform)
    if len(selection) > 0:
        start_node = selection[0]
        cmds.connectAttr("{0}.worldMatrix[0]".format(start_node),
                         "{0}.startMatrix".format(locator))
    if len(selection) > 1:
        end_node = selection[1]
        cmds.connectAttr("{0}.worldMatrix[0]".format(end_node),
                         "{0}.endMatrix".format(locator))
    cmds.select(transform)
    if creation_dialog:
        print("{0} \"{1}\" locator has been created successfully."
              "".format(UiConstants.INFO_PREFIX, transform))
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
        print("{0} Wrong selection. Please select only transform nodes to create a locator."
              "".format(UiConstants.ERROR_PREFIX))
        return None

    base_name = "adnLocatorPosition" if not custom_name else get_custom_base_name(custom_name)
    transform_name = "adnLocatorPosition1" if not custom_name else custom_name
    transform = cmds.createNode("transform", name=transform_name)
    index = transform[len(base_name):]
    locator_name = "{0}Shape{1}".format(base_name, index)
    locator = cmds.createNode("AdnLocatorPosition", name=locator_name, parent=transform)

    if len(selection) > 0:
        position_node = selection[0]
        cmds.connectAttr("{0}.worldMatrix[0]".format(position_node),
                         "{0}.positionMatrix".format(locator))
    cmds.select(transform)
    if creation_dialog:
        print("{0} \"{1}\" locator has been created successfully."
              "".format(UiConstants.INFO_PREFIX, transform))
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
        print("{0} Wrong selection. Please select only transform nodes to create a locator."
              "".format(UiConstants.ERROR_PREFIX))
        return None

    base_name = "adnLocatorRotation" if not custom_name else get_custom_base_name(custom_name)
    transform_name = "adnLocatorRotation1" if not custom_name else custom_name
    transform = cmds.createNode("transform", name=transform_name)
    index = transform[len(base_name):]
    locator_name = "{0}Shape{1}".format(base_name, index)
    locator = cmds.createNode("AdnLocatorRotation", name=locator_name, parent=transform)
    if len(selection) > 0:
        start_node = selection[0]
        cmds.connectAttr("{0}.worldMatrix[0]".format(start_node),
                         "{0}.startMatrix".format(locator))
    if len(selection) > 1:
        mid_node = selection[1]
        cmds.connectAttr("{0}.worldMatrix[0]".format(mid_node),
                         "{0}.midMatrix".format(locator))
    if len(selection) > 2:
        end_node = selection[2]
        cmds.connectAttr("{0}.worldMatrix[0]".format(end_node),
                         "{0}.endMatrix".format(locator))
    cmds.select(transform)
    if creation_dialog:
        print("{0} \"{1}\" locator has been created successfully."
                "".format(UiConstants.INFO_PREFIX, transform))
    return locator


def get_debugger_nodes(namespace=None):
    """Create or retrieve an AdnDebugLocator node and the data node connected.
    This method allows to search and create the required nodes within a
    certain namespace. This is useful when a rig is referenced and the
    nodes that are supposed to be connected to the debugger are added to
    a namespace. In this situation, we have to make sure that the debuggable
    nodes are connected to the debugger nodes of the same namespace.

    Args:
        namespace (str, optional): The namespace which we want to retrieve
            debugger nodes from. Defaults to None.

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
    for loc in adn_debug_locators:
        loc_namespace = get_namespace(loc)
        if loc_namespace == namespace:
            locator = loc
            debug_locator_found = True
            break
    if locator is None:
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
    # Data node found
    for dat in adn_data_nodes:
        dat_namespace = get_namespace(dat)
        if dat_namespace == namespace:
            data_node = dat
            break
    if data_node is None:
        # Data node creation
        data_node = cmds.createNode("AdnDataNode")

    if not data_node or not locator:
        # This should never happen
        print("{0} Failed to configure the debugger. Either AdnDataNode or AdnDebugLocator "
              "could not be retrieved."
              "".format(UiConstants.ERROR_PREFIX))
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

    Returns:
        bool: False if there was an error. True otherwise.
    """
    namespace = get_namespace(node)
    locator_node, data_node, next_index = get_debugger_nodes(namespace=namespace)
    connections = cmds.listConnections("{0}.inputs".format(data_node)) or []
    if node in connections:
        return True
    if next_index is not None:
        cmds.connectAttr("{0}.message".format(node),
                         "{0}.inputs[{1}]".format(data_node, next_index))
        return True
    return False


@undo_chunk
def refresh_debug_graph():
    """Refreshes Maya AdonisFX debug graph. Creating missing "AdnDataNode" and
    "AdnDebugLocator" nodes. At the same time creates required connections
    between debug and deformer nodes.

    Returns:
        bool: True if all the calls to connect_to_debugger returned True. False otherwise.
    """
    plugin_check()

    success = True
    deformer_nodes_scene = cmds.ls(type=MAYA_CONST.ADN_DEFORMERS + [OtherNodeTypes.GLUE])
    for deformer_node in deformer_nodes_scene:
        success = connect_to_debugger(deformer_node) and success
    return success
