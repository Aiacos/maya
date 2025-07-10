import logging

import maya.cmds as cmds

from adn.utils.maya.undo_stack import undo_chunk
from adn.utils.maya.checkers import plugin_check
from adn.utils.constants import UiConstants, DeformerTypes, OtherNodeTypes, LocatorTypes
from adn.tools.maya.muscle import find_muscles, remove_activation_inputs


@undo_chunk
def create_activation_node(single_instance=True, force=True):
    """Creates one or more AdnActivation nodes and connects them to the activation plugs
    of the selected muscle deformers. If no selection is provided, it creates a single
    AdnActivation node without connections.

    This function handles both single-instance and per-deformer node creation, depending
    on the `single_instance` flag. It also checks the `force` flag to overwrite or not
    existing connections.

    Args:
        single_instance (bool, optional): If True, one single AdnActivation node
            will be created and connected to all muscle deformers in the selection.
            If False, one dedicated AdnActivation node will be created and connected
            for each muscle deformer in the selection. Defaults to True.
        force (bool, optional): If the muscle deformer activation plug(s) have to be
            overwritten. Defaults to True.

    Returns:
        bool: False if there was an error. True otherwise.
    """
    plugin_check()

    selection = cmds.ls(selection=True, dagObjects=True, type="mesh", noIntermediate=True)

    # If the selection is empty, we simply create the AdnActivation node
    if not selection:
        node = cmds.createNode(OtherNodeTypes.ACTIVATION)
        print("{0} Node \"{1}\" has been created successfully.".format(UiConstants.INFO_PREFIX, node))
        return True

    muscle_deformers, skip_objects = find_muscles(selection)

    # Return if the selection does not contain any muscle deformer
    if not muscle_deformers:
        print("{0} {1} creation aborted. The selection does not contain any mesh with an {2} or {3} deformer applied."
              "".format(UiConstants.ERROR_PREFIX, OtherNodeTypes.ACTIVATION, DeformerTypes.MUSCLE, DeformerTypes.RIBBON))
        return False

    # If force is False (only possible from script) and all muscles are connected, abort the creation
    if not force and all_muscles_connected(muscle_deformers):
        print("{0} {1} creation aborted. All the {2} or {3} provided already have a connection to the activation plug."
              "".format(UiConstants.ERROR_PREFIX, OtherNodeTypes.ACTIVATION, DeformerTypes.MUSCLE, DeformerTypes.RIBBON))
        return False

    activation_nodes_created = []
    already_connected = []
    # Create one AdnActivation node and connect it to the muscle deformers in the selection
    if single_instance:
        node = cmds.createNode(OtherNodeTypes.ACTIVATION)
        activation_nodes_created.append(node)
        src_plug = "{0}.outValue".format(node)
        for muscle in muscle_deformers:
            dst_plug = "{0}.activation".format(muscle)
            try:
                cmds.connectAttr(src_plug, dst_plug, force=force)
            except:
                already_connected.append(muscle)

    # Create one AdnActivation node for each muscle deformer in the selection
    else:
        for muscle in muscle_deformers:
            # Avoid the creation of activation nodes for muscles
            # with connections when force is False
            activation_plug = "{0}.activation".format(muscle)
            has_inputs = bool(cmds.listConnections(activation_plug, destination=False) or [])
            if not force and has_inputs:
                already_connected.append(muscle)
                continue

            node = cmds.createNode(OtherNodeTypes.ACTIVATION)
            activation_nodes_created.append(node)
            src_plug = "{0}.outValue".format(node)
            dst_plug = "{0}.activation".format(muscle)
            # Here we don't need the try-except block because we are
            # previously avoiding the creation of an activation node
            # when a muscle has connections and force is False
            cmds.connectAttr(src_plug, dst_plug, force=force)

    # All good
    if not skip_objects and not already_connected:
        node_names = ["\"{0}\"".format(n) for n in activation_nodes_created]
        node_names = ", ".join(node_names)
        muscle_names = ["\"{0}\"".format(m) for m in muscle_deformers]
        muscle_names = ", ".join(muscle_names)
        print("{0} Node(s) {1} have been created successfully. "
                "The outValue plug(s) have been successfully connected to "
                "the activation plug of all the muscle deformers provided "
                "respectively: {2}."
                "".format(UiConstants.INFO_PREFIX, node_names, muscle_names))

        # Restore the selection
        cmds.select(selection)
        return True

    # Some muscles already have a connection and/or some meshes in the selection have no muscle applied
    already_connected_msg = ""
    skip_objects_msg = ""
    if already_connected:
        muscle_names = ["\"{0}\"".format(m) for m in already_connected]
        muscle_names = ", ".join(muscle_names)
        already_connected_msg = (" The outValue plug could not be connected to the following "
                                 "muscles because they already have a connection to the activation plug: {1}."
                                 "").format(src_plug, muscle_names)

    if skip_objects:
        mesh_names = ["\"{0}\"".format(m) for m in skip_objects]
        mesh_names = ", ".join(mesh_names)
        skip_objects_msg = (" The following elements in the selection have been ignored because "
                            "they had no {0} or {1} deformer applied: {2}."
                            "").format(DeformerTypes.MUSCLE, DeformerTypes.RIBBON, mesh_names)

    node_names = ["\"{0}\"".format(n) for n in activation_nodes_created]
    node_names = ", ".join(node_names)
    successful_muscle_names = ["\"{0}\"".format(m) for m in muscle_deformers if m not in already_connected]
    successful_muscle_names = ", ".join(successful_muscle_names)
    print("{0} Node(s) {1} have been created successfully. "
            "The outValue plug(s) have been successfully connected to "
            "the activation plug of the following provided muscle deformers "
            "respectively: {2}."
            "{3}{4}"
            "".format(UiConstants.WARNING_PREFIX, node_names, successful_muscle_names, already_connected_msg, skip_objects_msg))

    # Restore the selection
    cmds.select(selection)
    return True


def get_activation_inputs_from_muscles(muscle_deformers):
    """Returns the inputs connected to the activation plugs of all the
    muscles provided as argument.

    Args:
        muscle_deformers (list): List containing the muscle deformers.

    Return:
        input (list): List containing the input names.
    """
    inputs = []
    if not muscle_deformers:
        return inputs

    for muscle in muscle_deformers:
        activation_plug = "{0}.activation".format(muscle)
        inputs += cmds.listConnections(activation_plug, plugs=True, destination=False) or []

    return inputs


def all_muscles_connected(muscle_deformers):
    """Returns if all the muscles provided have a connection to their activation plug.

    Args:
        muscle_deformers (list): List containing the muscle deformers in the selection.

    Return:
        bool: True if all muscles have a connection. False otherwise.
    """
    if not muscle_deformers:
        return False

    for muscle in muscle_deformers:
        activation_plug = "{0}.activation".format(muscle)
        inputs = cmds.listConnections(activation_plug, destination=False) or []
        if not inputs:
            return False
    return True


@undo_chunk
def remove_inputs():
    """Remove the inputs connected to an AdnActivation node or to the activation list of AdnMuscle or AdnRibbonMuscle
    deformers. This method works in two ways depending on the current selection.

    Selection order:
        1) Locators to disconnect (optional).
        2) AdnActivation node to disconnect the inputs from or a list of geometries with a muscle deformer applied that
        is connected to an AdnActivation node.

    If no locators are found in the selection, then all the inputs will be removed from the AdnActivation nodes or 
    AdnMuscle/AdnRibbonMuscle deformers. If locators are provided, then only those ones connected to the AdnActivation
    nodes or AdnMuscle/AdnRibbonMuscle deformers will be removed.

    Returns:
        bool: False if no inputs could be removed for one of the AdnActivation nodes or AdnMuscle/AdnRibbonMuscle 
            deformers. True otherwise.
    """
    plugin_check()
    selection = cmds.ls(selection=True, long=True)

    error_msg = "Please, make one of the following selections and try again: " \
                "1) The input locators to remove plus an {0} node and/or a list of geometries with an {1} or {2} applied, " \
                "2) Only an {0} node and/or a list of geometries with an {1} or {2} applied to remove all the inputs." \
                "".format(OtherNodeTypes.ACTIVATION, DeformerTypes.MUSCLE, DeformerTypes.RIBBON)
    if not selection:
        logging.error("Invalid selection. {0}".format(error_msg))
        return False

    # Locators to disconnect
    locators = []
    locator_types = [LocatorTypes.POSITION, LocatorTypes.DISTANCE, LocatorTypes.ROTATION]
    for node in selection:
        if cmds.nodeType(node) in locator_types:
            locators.append(node)
        else:
            relatives = cmds.listRelatives(node, shapes=True, fullPath=True, type=locator_types) or []
            for relative in relatives:
                if cmds.nodeType(relative) in locator_types and relative not in locators:
                    locators.append(relative)

    # Destination nodes: AdnActivation or AdnMuscle/AdnRibbonMuscle deformers
    activation_nodes = [node for node in selection if cmds.nodeType(node) == OtherNodeTypes.ACTIVATION]
    muscle_deformers, _ = find_muscles(selection)
    for muscle in muscle_deformers:
        input_connections = cmds.listConnections(muscle, source=True, destination=False) or []
        activation_nodes += [node for node in input_connections if cmds.nodeType(node) == OtherNodeTypes.ACTIVATION]
    activation_nodes = list(set(activation_nodes))
    all_destination_nodes = activation_nodes + muscle_deformers

    if not all_destination_nodes:
        logging.error("Invalid selection. {0}".format(error_msg))
        return False
  
    return remove_activation_inputs(locators, all_destination_nodes)


def get_locators_and_activation_node(selection):
    """Get the locators and the activation node from the selection. The expected
    selection order is supposed to be:
    1) Locators to disconnect.
    2) AdnActivation node to disconnect the inputs from or a geometry with a muscle
    deformer applied that is connected to an AdnActivation node.

    If an AdnActivation node is provided, it can be at any position in the selection. If
    a geometry with a muscle deformer is provided, it must be the last element in the selection.

    Args:
        selection (list): Current selection

    Returns:
        list: The names of the locators.
        str: The name of the AdnActivation node.
    """

    activation_node = None
    locators = []
    if not selection:
        return locators, activation_node

    selection_copy = selection.copy()

    # Find AdnActivation node in the selection
    filtered_nodes = [node for node in selection_copy if cmds.nodeType(node) == OtherNodeTypes.ACTIVATION]
    if filtered_nodes:
        activation_node = filtered_nodes[0]
        for node in filtered_nodes:
            selection_copy.remove(node)
        num_activation_nodes = len(filtered_nodes)
        if num_activation_nodes > 1:
            print("{0} More than one {1} node found in the selection ({2}). "
                  "The first one will be used: \"{3}\". Others will be ignored."
                  "".format(UiConstants.WARNING_PREFIX, OtherNodeTypes.ACTIVATION, num_activation_nodes, activation_node))
    # If AdnActivation node not found, check if the last element in the selection
    # has a muscle applied and connected to an AdnActivation node
    else:
        deformers = cmds.findDeformers(selection_copy[-1]) or []
        muscle_deformers = [deformer for deformer in deformers if cmds.nodeType(deformer) in [DeformerTypes.MUSCLE, DeformerTypes.RIBBON]]
        if not muscle_deformers:
            return locators, activation_node
        connections = cmds.listConnections("{0}.activation".format(muscle_deformers[0]), destination=False) or []
        if not connections:
            return locators, activation_node
        history = cmds.listHistory(connections[0]) or []
        nodes = [node for node in history if cmds.nodeType(node) == OtherNodeTypes.ACTIVATION]
        if not nodes:
            return locators, activation_node
        activation_node = nodes[0]
        selection_copy.remove(selection_copy[-1])

    if not activation_node or len(selection) <= 1:
        return locators, activation_node

    # Gather the locators
    locator_types = [LocatorTypes.POSITION, LocatorTypes.DISTANCE, LocatorTypes.ROTATION]
    for node in selection_copy:
        if cmds.nodeType(node) in locator_types:
            locators.append(node)
        else:
            relatives = cmds.listRelatives(node, shapes=True, fullPath=True, type=locator_types) or []
            locators += relatives

    return locators, activation_node
