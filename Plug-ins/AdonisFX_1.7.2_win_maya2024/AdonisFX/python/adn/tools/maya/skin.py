import maya.cmds as cmds

from adn.utils.constants import DeformerTypes
from adn.utils.constants import UiConstants
from adn.utils.maya.checkers import check_playback
from adn.ui.widgets.dialogs import UiConstants
from adn.ui.utils import cursor
from adn.tools.maya import locators
from adn.utils.maya.undo_stack import undo_chunk
from adn.utils.maya.checkers import plugin_check


@undo_chunk
def apply_skin(custom_name=None, start_time=None, stiffness=1e5, iterations=3, gravity=0.0, damping=0.75):
    """Create the skin deformer and configure the main attributes with the given argument values.

    Args:
        custom_name (str, optional): Custom name to give to the deformer. Defaults to None.
        start_time (float, optional): Frame number for initialization. Defaults to None.
        stiffness (float, optional): Material stiffness. Defaults to 1e5.
        iterations (int, optional): Number of solver iterations for a simulation step. Defaults to 3.
        gravity (float, optional): Magnitude of the gravity. Defaults to 0.0.
        damping (float, optional): Global damping value. Defaults to 0.75.

    Returns:
        str: Name of the created skin deformer if created correctly.
        bool: False if there was an error. True otherwise.
    """
    plugin_check()
    deformer = ""
    selection = cmds.ls(selection=True, dagObjects=True, type="mesh", noIntermediate=True)
    if len(selection) < 1:
        print("{0} Wrong number of meshes selected ({1}). Select at least a mesh to apply "
              "the skin solver to.".format(UiConstants.ERROR_PREFIX, len(selection)))
        return deformer, False

    # Check deformers applied to the selection
    applied_deformers = cmds.findDeformers(selection[-1]) or []
    short_name = cmds.ls(selection[-1], long=False)
    for applied_deformer in applied_deformers:
        if cmds.nodeType(applied_deformer) == DeformerTypes.SKIN:
            print("{0} The selected mesh ({1}) has already an AdnSkin deformer node "
                  "applied to. Aborting creation.".format(UiConstants.WARNING_PREFIX, short_name[0]))
            return deformer, True

    unsuccessful_targets = list()
    successful_targets = list()
    connect_to_debugger_success = True
    with cursor.wait_cursor_context():
        node = selection[-1]
        cmds.select(node)
        deformer = (cmds.deformer(type=DeformerTypes.SKIN)[0] if not custom_name else
                    cmds.deformer(type=DeformerTypes.SKIN, name=custom_name)[0])
        
        # Configure attributes
        cmds.setAttr("{0}.prerollStartTime".format(deformer), start_time or cmds.currentTime(query=True))
        cmds.setAttr("{0}.startTime".format(deformer), start_time or cmds.currentTime(query=True))
        cmds.setAttr("{0}.stiffness".format(deformer), stiffness)
        cmds.setAttr("{0}.gravity".format(deformer), gravity)
        cmds.setAttr("{0}.iterations".format(deformer), iterations)
        cmds.setAttr("{0}.globalDampingMultiplier".format(deformer), damping)
        cmds.setAttr("{0}.material".format(deformer), 7)

        # Main connections
        cmds.connectAttr("time1.outTime", "{0}.currentTime".format(deformer))

        # Targets
        if len(selection) > 1:
            targets = selection[:-1]
            successful_targets, unsuccessful_targets = add_skin_targets(deformer, targets)

        # Data node and Locator
        # This function may print an error message so we propagate whether
        # the function succeeded so that the error dialog is displayed.
        connect_to_debugger_success = locators.connect_to_debugger(deformer)

        # Restore selection
        cmds.select(selection)

    # Creation dialog
    skin_deformer_short_name = cmds.ls(deformer, shortNames=True)[0]
    if unsuccessful_targets:
        unsuccessful_targets = ["\n    \"{0}\"".format(s) for s in unsuccessful_targets]
        target_names = "".join(unsuccessful_targets)
        print("{0} \"{1}\" deformer has been created successfully "
              "but the following selected objects could not get assigned as targets: {2}."
              "".format(UiConstants.WARNING_PREFIX, skin_deformer_short_name, target_names))
    else:
        print("{0} \"{1}\" deformer has been created successfully."
              "".format(UiConstants.INFO_PREFIX ,skin_deformer_short_name))

    return deformer, connect_to_debugger_success


def create_default_skin(mesh_name, node_name):
    """Create the most basic skin deformer. Only time attributes are
    configured for security reasons.

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
                                 type=DeformerTypes.SKIN,
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


def check_dependencies_on_import(data):
    """Checks if, based on the imported data, the AdnSkin deformer might be
    created from scratch with all the minimum inputs required.
    The minimum requirements for the AdnSkin deformer are:
        - Providing the 'referenceMesh'.
        - Providing the 'referenceMatrix'.

    Args:
        data (dict): Dictionary that containts all the AdnSkin available
            data to import.

    Returns:
        bool: True if imported data has the minimum requirements to create the
            AdnSkin deformer from scratch. False otherwise.
        str: descriptive message about the missing requirement if any.
    """
    return True, ""


def get_targets_and_deformer(selection):
    """Get the targets and the deformer.
       The expected selection order is supposed to be:
       1) Targets to connect (source).
       2) Deformer node to connect to (target).

    Args:
        selection (list): Current selection.

    Returns:
        str: the names of the targets to connect to the deformer node.
        str: the name of the deformer node to connect the targets to.
    """
    deformer = None
    targets = list()

    if not selection:
        return targets, deformer

    # Gather the TARGETS
    if len(selection) > 1:
        targets = selection[:-1]
        mesh_targets = list()

        # Check selection contains meshes
        for target in targets:
            if cmds.ls(target, type="mesh") or cmds.listRelatives(target, type="mesh"):
                mesh_targets.append(target)
        if not mesh_targets:
            return targets, deformer
        targets = mesh_targets

    # Gather the ADNSKIN NODE
    deformer_object = selection[-1]
    node_history = cmds.findDeformers(deformer_object) or []
    deformer_nodes = [x for x in node_history if cmds.nodeType(x) in DeformerTypes.SKIN]
    if not deformer_nodes:
        return targets, deformer

    return targets, deformer_nodes[0]


@undo_chunk
def add_targets():
    """Connect targets to the deformer node. Depending on the results displays different
    information messages.

    Selection order:
        1) Targets to connect.
        2) Deformer node to connect the targets to.

    Returns:
        bool: False if there was an error. True otherwise.
    """
    plugin_check()
    warning_message = "No valid targets and deformer provided. Please retry adding the targets " \
                      "by selecting the elements in the following order: " \
                      "1) Targets, 2) Mesh with {0} deformer applied to." \
                      "".format(DeformerTypes.SKIN)

    current_selection = cmds.ls(selection=True, long=True)
    targets, deformer = get_targets_and_deformer(current_selection)
    if not targets or not deformer:
        print("{0} {1}".format(UiConstants.ERROR_PREFIX, warning_message))
        return False

    # Add geometries
    successful_referenced = list()
    unsuccessful_referenced = list()
    successful_referenced, unsuccessful_referenced = add_skin_targets(deformer, targets)

    deformer_short_name = cmds.ls(deformer, shortNames=True)[0]
    if unsuccessful_referenced and not successful_referenced: # All targets are skipped
        unsuccessful_referenced = ["\"{0}\"".format(s) for s in unsuccessful_referenced]
        target_names = ", ".join(unsuccessful_referenced)
        print("{0} No new targets connected to \"{1}\". "
              "The following selected nodes were not eligible as targets, were added already or "
              "could not be added properly: {2}."
              "".format(UiConstants.WARNING_PREFIX, deformer_short_name, target_names))
    elif not successful_referenced: # No connected targets (no skipping)
        print("{0} No new targets connected to \"{1}\". Please, retry."
              "".format(UiConstants.ERROR_PREFIX, deformer_short_name))
        return False
    elif unsuccessful_referenced: # Some targets skipped, some added
        successful_referenced = ["\"{0}\"".format(s) for s in successful_referenced]
        successful_target_names = ", ".join(successful_referenced)
        unsuccessful_referenced = ["\"{0}\"".format(s) for s in unsuccessful_referenced]
        skip_target_names = ", ".join(unsuccessful_referenced)
        print("{0} The connection action had effect only in part of the selection. "
              "The following selected nodes were properly connected as targets: {1}. "
              "The following selected nodes were not eligible as targets, were added already or "
              "could not be added properly: {2}."
              "".format(UiConstants.WARNING_PREFIX, successful_target_names, skip_target_names))
    else: # All added, no skipped
        print("{0} Targets connected successfully to \"{1}\""
              "".format(UiConstants.INFO_PREFIX, deformer_short_name))
    
    return True


@undo_chunk
def add_skin_targets(deformer=None, targets=None):
    """Connect geometry targets to the deformer node. If the parameters are
    not provided will gather deformer and targets from the selection.

    Args:
        deformer (str, optional): name of the deformer node. Defaults to None.
        targets (list, optional): list of targets to add. Defaults to None.

    Returns:
        list: list with all targets that were successfully added.
        list: list with all the targets that are duplicated or not allowed as targets.
    """
    plugin_check()
    successful_referenced = list()
    unsuccessful_referenced  = list()
    targets = targets or list()

    if not deformer or not targets:
        # Gather the elements from selection
        current_selection = cmds.ls(selection=True, long=True)
        targets, deformer = get_targets_and_deformer(current_selection)
        if not deformer or not targets:
            return successful_referenced, unsuccessful_referenced

    # Get list of multi indices
    attr = "{}.targets".format(deformer)
    logical_indices = cmds.getAttr(attr, multiIndices=True) or []

    # Ensure that we connect the target after the last connected plug
    all_connected_indices = list()
    targets_connected = list()
    for index in logical_indices:
        mat_attr = attr + "[{0}].targetWorldMatrix".format(index)
        mesh_attr = attr + "[{0}].targetWorldMesh".format(index)
        matrices = cmds.listConnections(mat_attr, destination=True)
        meshes = cmds.listConnections(mesh_attr, destination=True)
        if matrices or meshes:
            all_connected_indices.append(index)
        if not matrices or not meshes:
            continue
        targets_connected.append(matrices[0])
        targets_connected.append(meshes[0])

    single_attr_matrix = "{0}.referenceMatrix".format(deformer)
    single_attr_mesh = "{0}.referenceMesh".format(deformer)
    single_matrix_connected = cmds.listConnections(single_attr_matrix, shapes=True) or []
    single_mesh_connected = cmds.listConnections(single_attr_mesh, shapes=True) or []
    if single_matrix_connected:
        targets_connected.append(single_matrix_connected[0])
    if single_mesh_connected:
        targets_connected.append(single_mesh_connected[0])

    # If no connected indices were provided assume that the target will be
    # added to the first entry in the array plug
    last_index = all_connected_indices[-1] if all_connected_indices else -1

    # Attach the target to the next free plug position
    new_index = last_index + 1
    for i in range(0, len(targets)):
        target = targets[i]
        short_name = cmds.ls(target, shortNames=True)[0]
        world_matrix = "{0}.worldMatrix[0]".format(target)
        world_mesh = "{0}.worldMesh[0]".format(target)
        # Check if the selected target has the attributes
        if not cmds.objExists(world_matrix) or not cmds.objExists(world_mesh):
            continue

        # Check previously existing targets
        if short_name in targets_connected:
            unsuccessful_referenced.append(short_name)
            continue
        shapes_target = cmds.ls(target, dagObjects=True, type="mesh", noIntermediate=True) or []
        if shapes_target and shapes_target[0] in targets_connected:
            unsuccessful_referenced.append(short_name)
            continue

        # Connect the world matrix to the target matrix entry
        child_attr = attr + "[{0}].targetWorldMatrix".format(new_index)
        cmds.connectAttr(world_matrix, child_attr)

        # Connect the world mesh to the target mesh entry
        child_attr = attr + "[{0}].targetWorldMesh".format(new_index)
        cmds.connectAttr(world_mesh, child_attr)

        successful_referenced.append(short_name)
        new_index += 1

    return successful_referenced, unsuccessful_referenced


@undo_chunk
def remove_targets():
    """Remove targets from the deformer node. Depending on the results displays different
    information messages. Removing all targets available is not allowed due to AdnSkin
    requirements.

    Selection order:
        1) Targets to disconnect.
        2) Deformer node to disconnect the targets from.

    Returns:
        bool: False if there was an error. True otherwise.
    """
    plugin_check()
    warning_message = "No valid targets and deformer provided. Please retry removing the targets " \
                      "by making one of the following selections: " \
                      "1) The targets to remove plus the geometry with the AdonisFX deformer or " \
                      "2) Only the geometry with the AdonisFX deformer to remove all the targets."

    current_selection = cmds.ls(selection=True, long=True)
    targets, deformer = get_targets_and_deformer(current_selection)
    if not deformer:
        print("{0} {1}".format(UiConstants.ERROR_PREFIX, warning_message))
        return False

    if not check_playback(deformer):
        return True

    successful_dettached = list()
    unsuccessful_dettached = list()
    successful_dettached, unsuccessful_dettached = remove_skin_targets(deformer, targets)

    deformer_short_name = cmds.ls(deformer, shortNames=True)[0]
    if not unsuccessful_dettached and not successful_dettached:
        print("{0} The disconnect target action for \"{1}\" did not have any effect. "
              "Please, try again."
              "".format(UiConstants.ERROR_PREFIX, deformer_short_name))
        return False

    if unsuccessful_dettached and successful_dettached:
        unsuccessful_dettached = ["\"{0}\"".format(s) for s in unsuccessful_dettached]
        successful_dettached = ["\"{0}\"".format(s) for s in successful_dettached]
        print("{0} The disconnection action had effect only in part of the selection. "
              "The following selected nodes were properly disconnected: {1}. "
              "The following selected nodes were not eligible as targets, were not found or "
              "could not be removed properly: {2}."
              "".format(UiConstants.WARNING_PREFIX, ", ".join(successful_dettached), ", ".join(unsuccessful_dettached)))
    elif unsuccessful_dettached:
        print("{0} The disconnect target action for \"{1}\" did not have any effect."
              "".format(UiConstants.ERROR_PREFIX, deformer_short_name))
        return False
    elif successful_dettached:
        print("{0} Targets disconnected successfully from \"{1}\""
              "".format(UiConstants.INFO_PREFIX, deformer_short_name))

    return True


@undo_chunk
def remove_skin_targets(deformer=None, targets=None):
    """Remove targets from the deformer node. If the parameters are
    not provided will gather deformer and targets from the selection.

    Args:
        deformer (str, optional): name of the deformer node. Defaults to None.
        targets (list, optional): list of targets to remove. If no targets provided
            all targets available will be removed. Defaults to None.

    Returns:
        list: list with all targets that were successfully removed.
        list: list with all the targets that were not removed.
    """
    successful_dettached = list()
    unsuccessful_dettached = list()
    targets = targets or list()

    if not deformer and not targets:
        # Gather the elements from selection
        current_selection = cmds.ls(selection=True, long=True)
        targets, deformer = get_targets_and_deformer(current_selection)
        if not deformer:
            return successful_dettached, unsuccessful_dettached

    # Get list of multi indices
    attr = "{}.targets".format(deformer)
    logical_indices = cmds.getAttr(attr, multiIndices=True) or []

    # If no targets are selected, remove all targets from the deformer
    if not targets:
        if len(logical_indices) > 0:
            # Using "[*]" will take into consideration any correspondence found.
            targets = cmds.listConnections("{0}[*].targetWorldMatrix".format(attr)) or []

        single_plug_targets = cmds.listConnections("{0}.referenceMatrix".format(deformer)) or []
        if single_plug_targets:
            targets.extend(single_plug_targets)

    # Nothing to disconnect
    if not targets:
        return successful_dettached, unsuccessful_dettached

    children = cmds.attributeQuery("targets", node=deformer, listChildren=True) or []
    reference_attr_mesh = "{0}.referenceMesh".format(deformer)
    reference_attr_matrix = "{0}.referenceMatrix".format(deformer)
    for target in targets:
        target = cmds.ls(target, long=True)[0]
        # Evaluate also the shape
        shape = None
        shapes = cmds.listRelatives(target, allDescendents=True, type="mesh")
        if shapes:
            shape = cmds.ls(shapes, long=True)[0]

        # Check targets plug
        for index in logical_indices:
            full_attr_matrix = "{0}[{1}].targetWorldMatrix".format(attr, index)
            attach_matrix_connected = cmds.listConnections(full_attr_matrix, shapes=True) or []
            if attach_matrix_connected:
                attach_matrix_connected = cmds.ls(attach_matrix_connected, long=True)[0]
            full_attr_mesh = "{0}[{1}].targetWorldMesh".format(attr, index)
            attach_mesh_connected = cmds.listConnections(full_attr_mesh, shapes=True) or []
            if attach_mesh_connected:
                attach_mesh_connected = cmds.ls(attach_mesh_connected, long=True)[0]

            if not attach_matrix_connected and not attach_mesh_connected:
                # Nothing to disconnect for this index
                continue
            target_found = attach_matrix_connected == target or attach_mesh_connected == target
            shape_found = (attach_matrix_connected == shape or attach_mesh_connected == shape) and shape

            if target_found or shape_found:
                # Disconnect
                children_target = ["{0}[{1}].{2}".format(attr, index, x) for x in children]

                # Disconnect all child attributes
                for node_plug in children_target:
                    connections = cmds.listConnections(node_plug, plugs=True, source=True) or []
                    for source_plug in connections:
                        try:
                            cmds.disconnectAttr(source_plug, node_plug)
                            successful_dettached.append(target)
                        except:
                            pass

        # Check reference plug
        reference_matrix_connected = cmds.listConnections(reference_attr_matrix, shapes=True) or []
        if reference_matrix_connected:
            reference_matrix_connected = cmds.ls(reference_matrix_connected, long=True)[0]
        reference_mesh_connected = cmds.listConnections(reference_attr_mesh, shapes=True) or []
        if reference_mesh_connected:
            reference_mesh_connected = cmds.ls(reference_mesh_connected, long=True)[0]

        if not reference_matrix_connected and not reference_mesh_connected:
            # Nothing to disconnect for this plug
            continue
        target_found = reference_matrix_connected == target or reference_mesh_connected == target
        shape_found = (reference_matrix_connected == shape or reference_mesh_connected == shape) and shape

        if target_found or shape_found:
            # Disconnect matrix
            connections = cmds.listConnections(reference_attr_matrix, plugs=True, source=True) or []
            if connections:
                cmds.disconnectAttr(connections[0], reference_attr_matrix)
                successful_dettached.append(target)

            # Disconnect mesh
            connections = cmds.listConnections(reference_attr_mesh, plugs=True, source=True) or []
            if connections:
                cmds.disconnectAttr(connections[0], reference_attr_mesh)
                successful_dettached.append(target)

    # Fill unsuccessful_dettached list
    successful_dettached = list(set(successful_dettached))
    for t in targets:
        t = cmds.ls(t, long=True)[0]
        if not t in successful_dettached:
            unsuccessful_dettached.append(t)

    return successful_dettached, unsuccessful_dettached
