import logging

import maya.cmds as cmds

from adn.utils.constants import DeformerTypes, OtherNodeTypes
from adn.ui.utils import cursor
from adn.tools.maya import locators 
from adn.utils.maya.undo_stack import undo_chunk
from adn.utils.maya.checkers import plugin_check
from adn.utils.constants import DebugDataDescriptor, UiConstants
import adn.tools.maya.attachments as adn_attachments


@undo_chunk
def apply_muscle(custom_name=None, start_time=None, stiffness=1e5, iterations=10, gravity=0.0, damping=0.75):
    """Create a muscle deformer and configure the main attributes with the given argument values.

    Args:
        custom_name (str, optional): Custom name to give to the deformer. Defaults to None.
        start_time (float, optional): Frame number for initialization. Defaults to None.
        stiffness (float, optional): Material stiffness. Defaults to 1e5.
        iterations (int, optional): Number of solver iterations for a simulation step. Defaults to 10.
        gravity (float, optional): Magnitude of the gravity. Defaults to 0.0.
        damping (float, optional): Global damping value. Defaults to 0.75.

    Returns:
        str: Name of the created ribbon muscle deformer if created correctly.
        bool: False if there was an error. True otherwise
    """
    plugin_check()
    deformer = ""
    selection = cmds.ls(selection=True)
    if len(selection) < 1:
        print("{0} Wrong number of objects selected ({1}). Select at least a mesh to apply "
              "the muscle solver to.".format(UiConstants.ERROR_PREFIX, len(selection)))
        return deformer, False

    # Check that the last element of the selection is a valid mesh
    deformer_mesh = cmds.ls(selection[-1], dagObjects=True, type="mesh", noIntermediate=True)
    if not deformer_mesh:
        print("{0} The selected object to apply the deformer is not a deformable mesh. "
              "Aborting creation."
              "".format(UiConstants.ERROR_PREFIX))
        return deformer, False

    # Check deformers applied to the selection
    applied_deformers = cmds.findDeformers(selection[-1]) or []
    short_name = cmds.ls(selection[-1], long=False)
    for applied_deformer in applied_deformers:
        if cmds.nodeType(applied_deformer) == DeformerTypes.MUSCLE:
            print("{0} The selected mesh ({1}) has already an AdnMuscle deformer node "
                  "applied to. Aborting creation.".format(UiConstants.WARNING_PREFIX, short_name[0]))
            return deformer, True

    unsuccessful_attachments = list()
    successful_attachments = list()
    connect_to_debugger_success = True
    with cursor.wait_cursor_context():
        attachment_nodes, node = selection[:-1], selection[-1]
        cmds.select(node)
        deformer = (cmds.deformer(type=DeformerTypes.MUSCLE)[0] if not custom_name else
                    cmds.deformer(type=DeformerTypes.MUSCLE, name=custom_name)[0])

        # Configure attributes
        cmds.setAttr("{0}.prerollStartTime".format(deformer), start_time or cmds.currentTime(query=True))
        cmds.setAttr("{0}.startTime".format(deformer), start_time or cmds.currentTime(query=True))
        cmds.setAttr("{0}.stiffness".format(deformer), stiffness)
        cmds.setAttr("{0}.gravity".format(deformer), gravity)
        cmds.setAttr("{0}.iterations".format(deformer), iterations)
        cmds.setAttr("{0}.globalDampingMultiplier".format(deformer), damping)

        # Main connections
        cmds.connectAttr("time1.outTime", "{0}.currentTime".format(deformer))

        # Attachments
        geometries_to_attach = list()
        transforms_to_attach = list()
        for attachment in attachment_nodes:
            if cmds.ls(attachment, type="mesh") or cmds.listRelatives(attachment, type="mesh"):
                geometries_to_attach.append(attachment)
            else:
                transforms_to_attach.append(attachment)

        if geometries_to_attach:
            # Add geometries as attachments
            successful_attachments, unsuccessful_attachments = \
              adn_attachments.add_geometry_target(deformer, geometries_to_attach)

        if transforms_to_attach:
            # Add transforms as attachments
            transforms_duplicated = list()
            successful_attachments, transforms_duplicated = \
                adn_attachments.add_attachment(deformer, transforms_to_attach)
            unsuccessful_attachments.extend(transforms_duplicated)

        # Data node and Locator
        # This function may print an error message so we propagate whether
        # the function succeeded so that the error dialog is displayed.
        connect_to_debugger_success = locators.connect_to_debugger(deformer)

        # Restore selection
        cmds.select(selection)

    # Creation dialog
    muscle_deformer_short_name = cmds.ls(deformer, shortNames=True)[0]
    if unsuccessful_attachments:
        unsuccessful_attachments = ["\"{0}\"".format(s) for s in unsuccessful_attachments]
        attachment_names = ", ".join(unsuccessful_attachments)
        print("{0} \"{1}\" deformer has been created successfully. "
              "The following selected nodes were not eligible for attachments: {2}."
              "".format(UiConstants.WARNING_PREFIX, muscle_deformer_short_name, attachment_names))
    else:
        print("{0} \"{1}\" deformer has been created successfully."
              "".format(UiConstants.INFO_PREFIX, muscle_deformer_short_name))

    return deformer, connect_to_debugger_success


def create_default_muscle(mesh_name, node_name):
    """Create the most basic muscle deformer. Only time attributes
    are configured for security reasons.

    Args:
        mesh_name (str): name of the geometry to create the deformer onto.
        node_name (str): tentative name for the node to create.

    Returns:
        str: resulting name of the created node.
        bool: False if there was an error. True otherwise.
    """
    connect_to_debugger_success = True
    with cursor.wait_cursor_context():
        # Deformer and connections
        deformer = cmds.deformer(mesh_name,
                                 type=DeformerTypes.MUSCLE,
                                 name=node_name)[0]
        cmds.setAttr("{0}.prerollStartTime".format(deformer),
                     cmds.currentTime(query=True))
        cmds.setAttr("{0}.startTime".format(deformer),
                     cmds.currentTime(query=True))
        cmds.connectAttr("time1.outTime",
                         "{0}.currentTime".format(deformer))

        # Data node and Locator
        # This function may print an error message so we propagate whether
        # the function succeeded so that the error dialog is displayed.
        connect_to_debugger_success = locators.connect_to_debugger(deformer)

    return deformer, connect_to_debugger_success


@undo_chunk
def draw_fibers(display):
    """Shows or hides the fibers direction for all the muscle deformers in the scene.

    Args:
        display (bool): flag to show or hide the fibers.
    """
    all_muscles = cmds.ls(type=DeformerTypes.MUSCLE)
    for muscle in all_muscles:
        if display:
            # Reference number for fibers is defined in DebugDataDescriptor.kMuscleFibers
            cmds.setAttr("{0}.debugFeature".format(muscle), DebugDataDescriptor.kMuscleFibers)
        elif cmds.getAttr("{0}.debugFeature".format(muscle)) != DebugDataDescriptor.kMuscleFibers:
            # Don't hide if it's a feature other than fibers
            continue
        cmds.setAttr("{0}.debug".format(muscle), display)


def find_muscles(selection):
    """Returns the AdnMuscle or AdnRibbonMuscle deformers found in the current selection.

    Args:
        selection (list): Current selection.

    Return:
        muscle_deformers (list): Muscle deformers found in the selection.
        no_deformers (list): Meshes with no muscle deformer applied.
    """
    muscle_deformers = []
    no_deformers = []
    if not selection:
        return muscle_deformers, no_deformers

    # Gather the AdnMuscle or AdnRibbonMuscle deformers
    deformers = []
    for element in selection:
        deformers_found = cmds.findDeformers(element) or []
        if not deformers_found:
            no_deformers.append(element)
            continue
        deformers += deformers_found

    # Filter deformers by muscle deformers
    muscle_deformers = [deformer for deformer in deformers if cmds.nodeType(deformer) in [DeformerTypes.MUSCLE, DeformerTypes.RIBBON]]

    return muscle_deformers, no_deformers


def remove_activation_inputs(locators, nodes):
    """Remove the inputs connected to an AdnActivation node or to the activation list of AdnMuscle or AdnRibbonMuscle
    deformers. This method works in two ways depending on the current selection.

    Selection order:
        1) Locators to disconnect (optional).
        2) AdnActivation node to disconnect the inputs from or a list of geometries with a muscle deformer applied that
        is connected to an AdnActivation node.

    If no locators are found in the selection, then all the inputs will be removed from the AdnActivation nodes or 
    AdnMuscle/AdnRibbonMuscle deformers. If locators are provided, then only those ones connected to the AdnActivation
    nodes or AdnMuscle/AdnRibbonMuscle deformers will be removed.

    Args:
        locators (list): list of locators to disconnect. This list can be empty for a full disconnection.
        nodes (list): list of AdnActivation nodes or AdnMuscle/AdnRibbonMuscle deformers to disconnect the inputs from.

    Returns:
        bool: False if no inputs could be removed for one of the AdnActivation nodes or AdnMuscle/AdnRibbonMuscle 
            deformers. True otherwise.
    """
    all_succeed = True
    for node in nodes:
        is_activation_node = cmds.nodeType(node) == OtherNodeTypes.ACTIVATION
        parent_plug = "inputs" if is_activation_node else "activationList"
        child_plug = "value" if is_activation_node else "activationListValue"
        attr = "{0}.{1}".format(node, parent_plug)
        logical_indices = cmds.getAttr(attr, multiIndices=True) or []

        # The value in success represent the result of the removal as follows:
        #   success = 0: # All inputs removed
        #   success = 1: # Some inputs skipped, some removed
        #   success = 2: # All inputs removal skipped
        success = 0
        successful_disconnected = []
        unsuccessful_disconnected = []

        # If no locators provided, remove all the entries
        if not locators:
            removed = False
            for idx in logical_indices:
                plug = "{0}[{1}]".format(attr, idx)
                # Remove the entry entirely
                # b=True will break the connections before removing the entry, otherwise the command would fail
                cmds.removeMultiInstance(plug, b=True)
                removed = True
            success = 0 if removed else 2
        else:
            for locator in locators:
                for idx in logical_indices:
                    parent_dst_plug = "{0}[{1}]".format(attr, idx)
                    dst_plug = "{0}.{1}".format(parent_dst_plug, child_plug)
                    src_shapes = cmds.listConnections(dst_plug, shapes=True, destination=False) or []
                    src_shapes = [cmds.ls(shape, long=True)[0] for shape in src_shapes]
                    for src_shape in src_shapes:
                        if src_shape == locator or locator in cmds.listHistory(src_shape, fullNodeName=True):
                            # If the locator is found, remove the entry entirely
                            cmds.removeMultiInstance(parent_dst_plug, b=True)
                            successful_disconnected.append(locator)

            unsuccessful_disconnected = [locator for locator in locators if locator not in successful_disconnected]

            if len(successful_disconnected) == len(locators):
                success = 0
            elif len(unsuccessful_disconnected) == len(locators):
                success = 2
            else:
                success = 1

        node_short_name = cmds.ls(node, shortNames=True)[0]
        if success == 0:
            logging.info("Activation inputs disconnected successfully from \"{0}\"."
                         "".format(node_short_name))
        elif success == 2:
            logging.error("The disconnect input action for \"{0}\" did not have any effect. "
                          "Either this node had no inputs connected or none of the selected "
                          "locators were connected to the activation inputs."
                          "".format(node_short_name))
            all_succeed = False
        else:
            successful_disconnected = ["\"{0}\"".format(s) for s in successful_disconnected]
            unsuccessful_disconnected = ["\"{0}\"".format(s) for s in unsuccessful_disconnected]
            input_names = ", ".join(successful_disconnected)
            skipped_input_names = ", ".join(unsuccessful_disconnected)
            logging.info("The disconnection action for \"{0}\" had effect only in part of the selection. "
                         "The following selected nodes were properly disconnected: {1}. "
                         "The following selected nodes were not eligible as inputs, were not found or "
                         "could not be removed properly: {2}."
                         "".format(node_short_name, input_names, skipped_input_names))
    return all_succeed
