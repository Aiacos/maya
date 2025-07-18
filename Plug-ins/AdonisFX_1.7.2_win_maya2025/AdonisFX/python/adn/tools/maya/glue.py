import maya.cmds as cmds

from adn.utils.constants import OtherNodeTypes
from adn.utils.maya.undo_stack import undo_chunk
from adn.utils.maya.checkers import plugin_check
from adn.utils.maya.constants import GluePaintableMaps
from adn.tools.maya import locators
from adn.ui.widgets.dialogs import UiConstants
from adn.ui.utils import cursor


@undo_chunk
def apply_glue(custom_name=None, preroll_start_time=None, stiffness=5e3, iterations=3):
    """ Create the glue node and configure the main attributes with the given argument values.

    Args:
        custom_name (str, optional): Custom name to give to the node. Defaults to None.
        preroll_start_time (float, optional): Frame number for initialization. Defaults to None.
        stiffness (float, optional): Material stiffness. Defaults to 5e3.
        iterations (int, optional): Number of solver iterations for a simulation step. Defaults to 3.

    Returns:
        str: Name of the created glue node if created correctly.
        bool: False if there was an error. True otherwise.
    """
    plugin_check()
    node = ""
    selection = cmds.ls(selection=True, dagObjects=True, type="mesh", noIntermediate=True)
    if len(selection) < 1:
        print("{0} Wrong number of meshes selected ({1}). Select at least one mesh to apply "
              "the glue solver to.".format(UiConstants.ERROR_PREFIX, len(selection)))
        return node, False

    connect_to_debugger_success = True
    with cursor.wait_cursor_context():
        node = (cmds.createNode(OtherNodeTypes.GLUE) if not custom_name else
                cmds.createNode(OtherNodeTypes.GLUE, name=custom_name))

        # Configure attributes
        cmds.setAttr("{0}.prerollStartTime".format(node), preroll_start_time or cmds.currentTime(query=True))
        cmds.setAttr("{0}.stiffness".format(node), stiffness)
        cmds.setAttr("{0}.iterations".format(node), iterations)

        # Main connections
        cmds.connectAttr("time1.outTime", "{0}.currentTime".format(node))

        # Connect inputs
        num_vertices = 0
        for i, geo in enumerate(selection):
            cmds.connectAttr("{0}.worldMatrix[0]".format(geo),
                             "{0}.inputs[{1}].inputMatrix".format(node, i))
            cmds.connectAttr("{0}.worldMesh[0]".format(geo),
                             "{0}.inputs[{1}].inputMesh".format(node, i))
            num_vertices += cmds.polyEvaluate(geo, vertex=True)

        # Connect AdnGlue output
        # Returns for example ['test_GEO', 'polyCube1']
        cube = cmds.polyCube(name="{0}_GEO".format(node))
        shape = cmds.listRelatives(cube)[0]
        # Delete polyCube node to connect the created node to the inMesh plug of the shape
        cmds.delete(cube[0], constructionHistory=True)
        cmds.connectAttr("{0}.outputMesh".format(node), "{0}.inMesh".format(shape))

        # Data node and Locator
        # This function may print an error message so we propagate whether
        # the function succeeded so that the error dialog is displayed.
        connect_to_debugger_success = locators.connect_to_debugger(node)
        # Restore selection
        cmds.select(selection)

        # Initialize paintable maps
        init_paintable_maps(node, num_vertices)

    glue_node_short_name = cmds.ls(node, shortNames=True)[0]
    print("{0} \"{1}\" node has been created successfully."
          "".format(UiConstants.INFO_PREFIX, glue_node_short_name))

    return node, connect_to_debugger_success


@undo_chunk
def add_inputs():
    """Connect inputs to the node. Depending on the results displays different
    information messages.

    Selection order:
        1) Inputs to connect.
        2) AdnGlue node to connect the inputs to.

    Returns:
        bool: False if there was an error. True otherwise.
    """
    plugin_check()
    selection = cmds.ls(selection=True, long=True)
    targets, node = get_targets_and_node(selection)

    error_msg = "Please, select the input meshes to be added plus the geometry with the {0} node applied." \
                "".format(OtherNodeTypes.GLUE)

    if not targets:
        print("{0} Invalid selection. {1}".format(UiConstants.ERROR_PREFIX, error_msg))
        return False

    if not node:
        short_name = cmds.ls(selection[-1])[0]
        print("{0} Could not find a valid {1} node applied to \"{2}\". {3}"
              "".format(UiConstants.ERROR_PREFIX, OtherNodeTypes.GLUE, short_name, error_msg))
        return False

    attr = "{0}.inputs".format(node)
    logical_indices = cmds.getAttr(attr, multiIndices=True) or []

    connected_indices = []
    targets_connected = []
    for index in logical_indices:
        mat_attr = "{0}[{1}].inputMatrix".format(attr, index)
        mesh_attr = "{0}[{1}].inputMesh".format(attr, index)
        matrices = cmds.listConnections(mat_attr, destination=True)
        meshes = cmds.listConnections(mesh_attr, destination=True)

        if matrices or meshes:
            connected_indices.append(index)

        if not matrices or not meshes:
            continue

        targets_connected.append(matrices[0])
        targets_connected.append(meshes[0])

    # The new input will be added to the next available index (sparse arrays are permitted)
    last_index = max(connected_indices) if connected_indices else -1
    new_index = last_index + 1
    unsuccessful_connected = []
    successful_connected = []
    for target in targets:
        short_name = cmds.ls(target, shortNames=True)[0]
        world_matrix = "{0}.worldMatrix[0]".format(target)
        world_mesh = "{0}.worldMesh[0]".format(target)
        # Check if the selected input has the attributes
        if not cmds.objExists(world_matrix) or not cmds.objExists(world_mesh):
            unsuccessful_connected.append(short_name)
            continue

        if short_name in targets_connected:
            unsuccessful_connected.append(short_name)
            continue
        shapes_input = cmds.ls(target, dagObjects=True, type="mesh", noIntermediate=True) or []
        if shapes_input and shapes_input[0] in targets_connected:
            unsuccessful_connected.append(short_name)
            continue

        # Connect the world matrix to the input matrix entry
        child_attr = "{0}[{1}].inputMatrix".format(attr, new_index)
        cmds.connectAttr(world_matrix, child_attr)

        # Connect the world mesh to the input mesh entry
        child_attr = "{0}[{1}].inputMesh".format(attr, new_index)
        cmds.connectAttr(world_mesh, child_attr)

        successful_connected.append(short_name)
        new_index += 1

    node_short_name = cmds.ls(node, shortNames=True)[0]
    if len(successful_connected) == len(targets): # All added
        print("{0} Inputs connected successfully to \"{1}\"."
              "".format(UiConstants.INFO_PREFIX, node_short_name))
        return True
    elif len(unsuccessful_connected) == len(targets): # All skipped
        unsuccessful_connected = ["\"{0}\"".format(s) for s in unsuccessful_connected]
        input_names = ", ".join(unsuccessful_connected)
        print("{0} No new inputs connected to \"{1}\". "
              "None of the selected inputs could be connected or they are already "
              "connected to the node: {2}."
              "".format(UiConstants.ERROR_PREFIX, node_short_name, input_names))
        return False
    else: # Some skipped, some added
        successful_connected = ["\"{0}\"".format(s) for s in successful_connected]
        input_names = ", ".join(successful_connected)
        unsuccessful_connected = ["\"{0}\"".format(s) for s in unsuccessful_connected]
        skipped_input_names = ", ".join(unsuccessful_connected)
        print("{0} The connection action for \"{1}\" had effect only in part of the selection. "
              "The following selected nodes were properly connected as inputs: {2}. "
              "The following selected nodes were not eligible as inputs, were added already or "
              "could not be added properly: {3}."
              "".format(UiConstants.WARNING_PREFIX, node_short_name, input_names, skipped_input_names))
        return True


@undo_chunk
def remove_inputs():
    """Remove inputs from the node. Depending on the results displays different
    information messages.

    Selection order:
        1) Inputs to disconnect.
        2) AdnGlue node to disconnect the inputs from.

    Returns:
        bool: False if there was an error. True otherwise.
    """
    plugin_check()
    selection = cmds.ls(selection=True, long=True)
    targets, node = get_targets_and_node(selection)

    error_msg = "Please, make one of the following selections and try again: " \
                "1) The inputs to remove plus the geometry with the {0} node applied, " \
                "2) Only the geometry with the {0} node applied to remove all the inputs." \
                "".format(OtherNodeTypes.GLUE)

    if not targets and not node:
        print("{0} Invalid selection. {1}".format(UiConstants.ERROR_PREFIX, error_msg))
        return False

    if not node:
        short_name = cmds.ls(selection[-1])[0]
        print("{0} Could not find a valid {1} node applied to \"{2}\". {3}"
              "".format(UiConstants.ERROR_PREFIX, OtherNodeTypes.GLUE, short_name, error_msg))
        return False

    # Allow to remove inputs only at preroll time
    play_status = cmds.play(query=True, state=True)
    preroll_time = cmds.getAttr("{0}.prerollStartTime".format(node))
    current_time = cmds.getAttr("{0}.currentTime".format(node))
    if play_status or preroll_time != current_time:
        print("{0} Please, stop playback, move to preroll start time and try again."
              "".format(UiConstants.ERROR_PREFIX))
        return False

    attr = "{0}.inputs".format(node)
    logical_indices = cmds.getAttr(attr, multiIndices=True) or []
    child_plugs = cmds.attributeQuery("inputs", node=node, listChildren=True) or []
    node_short_name = cmds.ls(node, shortNames=True)[0]

    # The value in success represent the result of the removal as follows:
    #   success = 0: # All inputs removed
    #   success = 1: # Some inputs skipped, some removed
    #   success = 2: # All inputs removal skipped
    success = 0
    successful_disconnected = []
    unsuccessful_disconnected = []
    if not targets:
        # If no targets provided remove all the connections
        removed = False
        for idx in logical_indices:
            for child in child_plugs:
                input_plug = "{0}[{1}].{2}".format(attr, idx, child)
                input_plug_connections = cmds.listConnections(input_plug, plugs=True, source=True, destination=False) or []
                for connection in input_plug_connections:
                    cmds.disconnectAttr(connection, input_plug)
                    removed = True

        if removed:
            success = 0
        else:
            success = 2

    else:
        # For each target find which index it corresponds to
        for target in targets:
            shape = None
            shapes = cmds.listRelatives(target, allDescendents=True, type="mesh")
            if shapes:
                shape = cmds.ls(shapes, long=True)[0]
            for idx in logical_indices:
                # For each index we iterate over its child plugs (mesh and matrix)
                for child in child_plugs:
                    input_plug = "{0}[{1}].{2}".format(attr, idx, child)
                    # Get the source plug connected to input_plug
                    input_plug_connections = cmds.listConnections(input_plug, plugs=True, source=True, destination=False) or []
                    # Get the shape connected to input_plug
                    input_plug_connections_shapes = cmds.listConnections(input_plug, shapes=True) or []

                    if input_plug_connections:
                        for connection, connected_shape in zip(input_plug_connections, input_plug_connections_shapes):
                            connected_shape = cmds.ls(connected_shape, long=True)[0]
                            # Check if the target we want to remove or its shape
                            # matches the shape connected to the current input_plug
                            if target == connected_shape or shape == connected_shape:
                                cmds.disconnectAttr(connection, input_plug)
                                successful_disconnected.append(target)


        successful_disconnected = list(set(successful_disconnected))
        unsuccessful_disconnected = [target for target in targets if target not in successful_disconnected]

        if len(successful_disconnected) == len(targets): # All removed
            success = 0
        elif len(unsuccessful_disconnected) == len(targets): # All skipped
            success = 2
        else: # Some skipped, some removed
            success = 1


    if success == 0: # All removed
        print("{0} Inputs disconnected successfully from \"{1}\"."
                "".format(UiConstants.INFO_PREFIX, node_short_name))
        return True
    elif success == 2: # All skipped
        print("{0} The disconnect input action for \"{1}\" did not have any effect."
                "".format(UiConstants.ERROR_PREFIX, node_short_name))
        return False
    else: # Some skipped, some removed
        successful_disconnected = ["\"{0}\"".format(s) for s in successful_disconnected]
        unsuccessful_disconnected = ["\"{0}\"".format(s) for s in unsuccessful_disconnected]
        input_names = ", ".join(successful_disconnected)
        skipped_input_names = ", ".join(unsuccessful_disconnected)
        print("{0} The disconnection action for \"{1}\" had effect only in part of the selection. "
              "The following selected nodes were properly disconnected: {2}. "
              "The following selected nodes were not eligible as inputs, were not found or "
              "could not be removed properly: {3}."
              "".format(UiConstants.WARNING_PREFIX, node_short_name, input_names, skipped_input_names))
        return True


def get_targets_and_node(selection):
    """Get the inputs and the node. The expected selection order is
    supposed to be:
    1) Inputs to connect or disconnect.
    2) AdnGlue node.

    Args:
        selection (list): Current selection.

    Returns:
        list: the names of the inputs to connect or disconnect.
        str: the name of the AdnGlue node.
    """
    node = None
    targets = []

    if not selection:
        return targets, node

    # Gather the inputs
    if len(selection) > 1:
        # Check if the selection contains meshes
        for target in selection[:-1]:
            if cmds.ls(target, type="mesh") or cmds.listRelatives(target, type="mesh"):
                targets.append(target)
        if not targets:
            return targets, node

    # Gather AdnGlue node
    upstream_chain = cmds.geometryAttrInfo("{0}.inMesh".format(selection[-1]), nodeChain=True) or []
    nodes = [x for x in upstream_chain if cmds.nodeType(x) in OtherNodeTypes.GLUE]
    if not nodes:
        return targets, node

    return targets, nodes[0]


@undo_chunk
def init_paintable_maps(node, num_elements):
    """Resize the AdnGlue paintable maps and set their default values.

    Args:
        node (str): Name of the AdnGlue node.
        num_elements (int): New size of the paintable maps. Represents the
            total number of vertices.
    """
    for map_name, default_value in GluePaintableMaps.DEFAULT_VALUES.items():
        attr_name = "{0}.{1}".format(node, map_name)
        cmds.setAttr(attr_name, [default_value] * num_elements, type="doubleArray")
