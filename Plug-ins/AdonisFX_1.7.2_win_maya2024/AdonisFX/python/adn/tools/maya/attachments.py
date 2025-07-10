import maya.cmds as cmds

from adn.utils.constants import DeformerTypes, ConstraintTypesNiceNames, UiConstants
from adn.utils.maya.checkers import check_playback
from adn.utils.maya.checkers import scene_parent_check
from adn.utils.maya.undo_stack import undo_chunk
from adn.utils.maya.checkers import plugin_check, deformer_being_painted


def get_anchors_and_deformer(selection):
    """Get the anchors and the deformer.
       The expected selection order is supposed to be:
       1) Anchors to connect (source).
       2) Deformer node to connect to (target).

    Args:
        selection (list): Current selection.
    
    Returns:
        str: the names of the anchors to connect to the deformer node.
        str: the name of the deformer node to connect the anchors to.
    """
    deformer = None
    anchors = list()
    supported_deformers = [DeformerTypes.MUSCLE, DeformerTypes.RIBBON]

    if not selection:
        return anchors, deformer
    
    # Multiple anchors can be selected
    if len(selection) > 1:
        anchors = selection[:-1]
    deformer_object = selection[-1]

    node_history = cmds.findDeformers(deformer_object) or []
    deformer_nodes = [x for x in node_history if cmds.nodeType(x) in supported_deformers]
    if not deformer_nodes:
        return anchors, deformer
    
    return anchors, deformer_nodes[0]


@undo_chunk
def add_attachment(deformer=None, attachments=None):
    """Connect transform attachments to the deformer node. If the parameters are
    not provided will gather deformer and attachments from the selection.

    Args:
        deformer (str, optional): name of the deformer node. Defaults to None.
        attachments (list, optional): list of attachments to add. Defaults None.

    Returns:
        list: list with all attachments that were successfully added.
        list: list with all the attachments that are duplicated and were not added.
    """
    successful_attached = list()
    duplicated_attachments  = list()
    attachments = attachments or list()

    if not deformer and not attachments:
        current_selection = cmds.ls(selection=True, long=True)
        attachments, deformer = get_anchors_and_deformer(current_selection)
        if not deformer:
            return successful_attached, duplicated_attachments

    # Get list of multi indices
    attr = "{}.attachmentConstraintsList".format(deformer)
    logical_indices = cmds.getAttr(attr, multiIndices=True) or []

    # Ensure that we connect the attachment after the last connected plug
    connected_indices = list()
    for index in logical_indices:
        full_attr = attr + "[{0}].attachmentMatrix".format(index)
        if not cmds.listConnections(full_attr, destination=True):
            continue
        connected_indices.append(index)

    # If no connected indices were provided assume that the attachment will be
    # added to the first entry in the array plug
    last_index = connected_indices[-1] if connected_indices else -1

    attachments_connected = list()
    if len(logical_indices) > 0:
        # Using "[*]" will take into consideration any correspondence found.
        attachments_connected = cmds.listConnections("{0}[*].attachmentMatrix".format(attr)) or []

    # Attach the attachment to the next free plug position
    new_index = last_index + 1
    for i in range(0, len(attachments)):
        attachment = attachments[i]
        short_name = cmds.ls(attachment, shortNames=True)[0]
        world_matrix = "{0}.worldMatrix[0]".format(attachment)
        # Check if the selected attachment has a world matrix attribute
        if not cmds.objExists(world_matrix):
            continue
        # Check previously existing attachments
        if short_name in attachments_connected:
            duplicated_attachments.append(short_name)
            continue
        # Connect the world matrix to the attachment matrix entry
        child_attr = attr + "[{0}].attachmentMatrix".format(new_index)
        cmds.connectAttr(world_matrix, child_attr)

        child_attr = "{0}[{1}].attachmentConstraints".format(attr, new_index)
        child_logical_indices = cmds.getAttr(child_attr, multiIndices=True) or []
        # Remove all entries to the multi weight attribute to maintain a clean state
        for idx in child_logical_indices:
            cmds.removeMultiInstance("{0}[{1}]".format(child_attr, idx), b=True)

        successful_attached.append(short_name)
        new_index += 1

    # Re-query the logical indices to gather the new addition
    logical_indices = cmds.getAttr(attr, multiIndices=True) or []

    # Cleanup the weights of any plug that has no input connections
    # This is to avoid adding an attachment on top of an entry with still populated weights
    for log_index in logical_indices:
        full_attr = "{0}[{1}].attachmentMatrix".format(attr, log_index)
        if cmds.listConnections(full_attr, destination=True):
            continue
        child_attr = "{0}[{1}].attachmentConstraints".format(attr, log_index)
        child_logical_indices = cmds.getAttr(child_attr, multiIndices=True) or []
        # Remove all entries to the multi weight attribute to maintain a clean state
        for idx in child_logical_indices:
            cmds.removeMultiInstance("{0}[{1}]".format(child_attr, idx), b=True)
    
    return successful_attached, duplicated_attachments


@undo_chunk
def remove_attachment(deformer=None, attachments=None):
    """Remove transform attachments to the deformer node. If the parameters are
    not provided will gather deformer and attachments from the selection.

    Args:
        deformer (str, optional): name of the deformer node. Defaults to None.
        attachments (list, optional): list of attachments to remove. If no attachments provided
            all attachments available will be removed. Defaults to None.

    Returns:
        list: list with all attachments that were successfully removed.
        list: list with all the attachments that were not removed.
    """
    successful_dettached = list()
    unsuccessful_dettached = list()
    attachments = attachments or list()

    if not deformer and not attachments:
        current_selection = cmds.ls(selection=True, long=True)
        attachments, deformer = get_anchors_and_deformer(current_selection)
        if not deformer:
            return successful_dettached, unsuccessful_dettached

    # Get list of multi indices
    attr = "{}.attachmentConstraintsList".format(deformer)
    logical_indices = cmds.getAttr(attr, multiIndices=True) or []

    # If no attachments are selected, remove all attachments from the deformer
    if not attachments and len(logical_indices) > 0:
        # Using "[*]" will take into consideration any correspondence found.
        attachments = cmds.listConnections("{0}[*].attachmentMatrix".format(attr))

    # If the deformer has no attachments
    if not attachments:
        return successful_dettached, unsuccessful_dettached

    for i in range(0, len(attachments)):
        attachment = attachments[i]
        short_name = attachment.split("|")[-1]
        world_matrix = "{0}.worldMatrix[0]".format(attachment)
        # Check if the selected attachment has a world matrix attribute
        if not cmds.objExists(world_matrix):
            unsuccessful_dettached.append(short_name)
            continue
        deformer_name = cmds.listConnections(world_matrix, destination=True) or []
        if not deformer_name and deformer not in deformer_name:
            unsuccessful_dettached.append(short_name)
            continue
        connections = cmds.listConnections(world_matrix, destination=True, plugs=True)
        if not connections:
            unsuccessful_dettached.append(short_name)
            continue
        
        attachment_attr = "attachmentConstraintsList"
        attachment_matrices_attr = "attachmentMatrix"
        
        valid_connection = False
        attachment_constraints_list = ""
        attachment_matrices = ""

        # Support logic for the case that the attachment has multiple connections for the world matrix.
        for connection in connections:
            separated = connection.split(".")
            object_name = separated[0]
            if object_name != deformer:
                continue
            # This insures that the compound attribute has the correct number of levels
            if len(separated) != 3:
                continue
            # Check that the deformer node we are checking is the deformer node we have selected
            if object_name != deformer:
                continue
            
            attachment_constraints_list = separated[1]
            separated_list = attachment_constraints_list.split("[")
            attachment_constraints_list_name = separated_list[0] if separated_list else ""
            attachment_matrices = separated[2]

            # Check that the queried attributes are correct
            if attachment_constraints_list_name != attachment_attr:
                continue
            if attachment_matrices != attachment_matrices_attr:
                continue
            valid_connection = True
            break

        if not valid_connection:
            unsuccessful_dettached.append(short_name)
            continue

        # Get the index to remove from the deformer (..[0])
        idx1 = attachment_constraints_list.index("[")
        idx2 = attachment_constraints_list.index("]")
        logical_index = attachment_constraints_list[idx1 + 1: idx2]

        # Get the name of the child attributes and create a valid plug identifier to search for connections
        children = cmds.attributeQuery("attachmentConstraintsList",
                                       node=deformer, listChildren=True) or []
        children = ["{0}[{1}].{2}".format(attr, logical_index, x) for x in children]

        # Disconnect all child attributes
        for node_plug in children:
            connections = cmds.listConnections(node_plug, plugs=True, source=True) or []
            for source_plug in connections:
                try:
                    cmds.disconnectAttr(source_plug, node_plug)
                except:
                    pass

        child_attr = "{0}[{1}].attachmentConstraints".format(attr, logical_index)
        child_logical_indices = cmds.getAttr(child_attr, multiIndices=True) or []
        # Remove all entries to the multi weight attribute to maintain a clean state
        for idx in child_logical_indices:
            cmds.removeMultiInstance("{0}[{1}]".format(child_attr, idx), b=True)

        successful_dettached.append(short_name)

    # Cleanup the weights of any plug that has no input connections
    # This is to avoid adding an attachment on top of an entry with still populated weights
    for log_index in logical_indices:
        full_attr = "{0}[{1}].attachmentMatrix".format(attr, log_index)
        if cmds.listConnections(full_attr, destination=True):
            continue
        child_attr = "{0}[{1}].attachmentConstraints".format(attr, log_index)
        child_logical_indices = cmds.getAttr(child_attr, multiIndices=True) or []
        # Remove all entries to the multi weight attribute to maintain a clean state
        for idx in child_logical_indices:
            cmds.removeMultiInstance("{0}[{1}]".format(child_attr, idx), b=True)

    return successful_dettached, unsuccessful_dettached


def avoid_cyclic_assignments(deformer, tentative_attachments):
    """This function detects if by connecting any of the geometries provided
    in as tentative assignments to the targets plug of the given deformer
    would produce a cycle in the node graph: one geometry has an AdonisFX
    deformer which has a geometry target assigned that is being deformed by
    the given deformer. If such dependency is found, a warning message is
    printed and the tentative geometry is added to the avoid_list to return.

    Args:
        deformer (str): name of the deformer that is being evaluated to receive
            the tentative attachments as input targets.
        tentative_attachments (list): list of geometries that are candidate to
            be assigned as targets to the input deformer.
    
    Returns:
        list: list of attachments that are discarded because if they would
            produce a cycle if they get assigned to the input deformer.
    """
    avoid_list = list()

    types_filter = [DeformerTypes.RIBBON, DeformerTypes.MUSCLE]
    for attach in tentative_attachments:
        attach_deformers = cmds.findDeformers(attach) or []
        for d in attach_deformers:
            if cmds.nodeType(d) not in types_filter:
                continue
            # Gather the inputs to the deformer d of this current attachment
            plug_to_evaluate = "{0}.targets".format(d)
            if not cmds.objExists(plug_to_evaluate):
                continue
            targets = list(set(cmds.listConnections("{0}.targets".format(d),
                                                    source=True,
                                                    destination=False) or []))
            for t in targets:
                # For each target to deformer d, check if it has non permitted
                # node types (e.g. AdonisFX muscles) in the history
                t_deformers = cmds.findDeformers(t) or []
                for t_deformer in t_deformers:
                    if t_deformer != deformer:
                        continue
                    # If we reach this code, then there will be a cycle if we
                    # assign this attachment as target to the deformer
                    avoid_list.append(attach)
                    short_name = cmds.ls(attach, shortNames=True)[0]
                    print("{0} Cannot assign '{1}' as target to '{2}' "
                          "deformer: making this assignment would produce a "
                          "cycle.".format(UiConstants.ERROR_PREFIX, short_name, deformer))
                    break

    return avoid_list


@undo_chunk
def add_geometry_target(deformer=None, attachments=None):
    """Connect geometry targets to the deformer node. If the parameters are
    not provided will gather deformer and targets from the selection.

    Args:
        deformer (str, optional): name of the deformer node. Defaults to None.
        attachments (list, optional): list of attachments to add. Defaults to None.

    Returns:
        list: list with all targets that were successfully added.
        list: list with all the targets that are duplicated or not allowed as targets.
    """
    successful_attached = list()
    unsuccessful_attached  = list()
    attachments = attachments or list()

    if not deformer and not attachments:
        current_selection = cmds.ls(selection=True, long=True)
        attachments, deformer = get_anchors_and_deformer(current_selection)
        if not deformer:
            return successful_attached, unsuccessful_attached

    # Get list of multi indices
    attr = "{}.targets".format(deformer)
    logical_indices = cmds.getAttr(attr, multiIndices=True) or []

    # Prevent from cycles: if an attachment is a muscle (ribbon or volumetric)
    # and the current deformer is already assigned as target to that muscle,
    # then we don't assign it here as it would produce a graph cycle.
    unsuccessful_attached = avoid_cyclic_assignments(deformer, attachments)
    attachments = list(set(attachments).difference(unsuccessful_attached))

    # Ensure that we connect the attachment after the last connected plug
    all_connected_indices = list()
    attachments_connected = list()
    for index in logical_indices:
        mat_attr = attr + "[{0}].targetWorldMatrix".format(index)
        mesh_attr = attr + "[{0}].targetWorldMesh".format(index)
        matrices = cmds.listConnections(mat_attr, destination=True)
        meshes = cmds.listConnections(mesh_attr, destination=True)
        if matrices or meshes:
            all_connected_indices.append(index)
        if not matrices or not meshes:
            continue
        attachments_connected.append(matrices[0])
        attachments_connected.append(meshes[0])

    # If no connected indices were provided assume that the attachment will be
    # added to the first entry in the array plug
    last_index = all_connected_indices[-1] if all_connected_indices else -1

    # Attach the attachment to the next free plug position
    new_index = last_index + 1
    for i in range(0, len(attachments)):
        attachment = attachments[i]
        short_name = cmds.ls(attachment, shortNames=True)[0]
        world_matrix = "{0}.worldMatrix[0]".format(attachment)
        world_mesh = "{0}.worldMesh[0]".format(attachment)
        # Check if the selected attachment has the attributes
        if not cmds.objExists(world_matrix) or not cmds.objExists(world_mesh):
            continue

        # Check previously existing attachments
        if short_name in attachments_connected:
            unsuccessful_attached.append(short_name)
            continue

        # Connect the world matrix to the attachment matrix entry
        child_attr = attr + "[{0}].targetWorldMatrix".format(new_index)
        cmds.connectAttr(world_matrix, child_attr)

        # Connect the world mesh to the attachment matrix entry
        child_attr = attr + "[{0}].targetWorldMesh".format(new_index)
        cmds.connectAttr(world_mesh, child_attr)

        child_attr = "{0}[{1}].attachmentToGeoConstraints".format(attr, new_index)
        child_logical_indices = cmds.getAttr(child_attr, multiIndices=True) or []
        # Remove all entries to the multi weight attribute to maintain a clean state
        for idx in child_logical_indices:
            cmds.removeMultiInstance("{0}[{1}]".format(child_attr, idx), b=True)

        child_attr = "{0}[{1}].slideOnGeometryConstraints".format(attr, new_index)
        child_logical_indices = cmds.getAttr(child_attr, multiIndices=True) or []
        # Remove all entries to the multi weight attribute to maintain a clean state
        for idx in child_logical_indices:
            cmds.removeMultiInstance("{0}[{1}]".format(child_attr, idx), b=True)

        successful_attached.append(short_name)
        new_index += 1

    # Re-query the logical indices to gather the new addition
    logical_indices = cmds.getAttr(attr, multiIndices=True) or []

    # Cleanup the weights of any plug that has no input connections
    # This is to avoid adding an attachment on top of an entry with still populated weights
    for log_index in logical_indices:
        mat_attr = attr + "[{0}].targetWorldMatrix".format(log_index)
        mesh_attr = attr + "[{0}].targetWorldMesh".format(log_index)
        if (cmds.listConnections(mat_attr, destination=True) or
            cmds.listConnections(mesh_attr, destination=True)):
            continue
        child_attr = "{0}[{1}].attachmentToGeoConstraints".format(attr, log_index)
        child_logical_indices = cmds.getAttr(child_attr, multiIndices=True) or []
        # Remove all entries to the multi weight attribute to maintain a clean state
        for idx in child_logical_indices:
            cmds.removeMultiInstance("{0}[{1}]".format(child_attr, idx), b=True)

        child_attr = "{0}[{1}].slideOnGeometryConstraints".format(attr, log_index)
        child_logical_indices = cmds.getAttr(child_attr, multiIndices=True) or []
        # Remove all entries to the multi weight attribute to maintain a clean state
        for idx in child_logical_indices:
            cmds.removeMultiInstance("{0}[{1}]".format(child_attr, idx), b=True)
    
    return successful_attached, unsuccessful_attached


@undo_chunk
def remove_geometry_target(deformer=None, attachments=None):
    """Remove transform attachments to the deformer node. If the parameters are
    not provided will gather deformer and targets from the selection.

    Args:
        deformer (str, optional): name of the deformer node. Defaults to None.
        attachments (list, optional): list of attachments to remove. If no attachments provided
            all attachments available will be removed. Defaults to None.

    Returns:
        list: list with all attachments that were successfully removed.
        list: list with all the attachments that were not removed.
    """
    successful_dettached = list()
    unsuccessful_dettached = list()
    connected_attachments = list()
    connected_indices = list()
    attachments = attachments or list()

    if not deformer and not attachments:
        current_selection = cmds.ls(selection=True, long=True)
        attachments, deformer = get_anchors_and_deformer(current_selection)
        if not deformer:
            return successful_dettached, unsuccessful_dettached

    # Get list of multi indices
    attr = "{}.targets".format(deformer)
    logical_indices = cmds.getAttr(attr, multiIndices=True) or []

    # Gather the connected attachments
    for index in logical_indices:
        full_attr_matrix = "{0}[{1}].targetWorldMatrix".format(attr, index)
        full_attr_mesh = "{0}[{1}].targetWorldMesh".format(attr, index)
        attach_matrix_connected = cmds.listConnections(full_attr_matrix, shapes=True) or []
        # NOTE: Only consider attachments disconnectable that have both
        # plugs connected
        if not attach_matrix_connected:
            continue
        attach_mesh_connected = cmds.listConnections(full_attr_mesh, shapes=True) or []
        if not attach_mesh_connected:
            continue
        connected_indices.append(index)
        connected_attachments.append((
            cmds.ls(attach_matrix_connected, long=True)[0],
            cmds.ls(attach_mesh_connected, long=True)[0]))

    # If the deformer has no attachments
    if not connected_indices:
        return successful_dettached, unsuccessful_dettached

    # Add the shapes to the possible attachments connections
    shapes = list()
    for attachment in attachments:
        attachments = cmds.ls(attachments, long=True)
        shape = cmds.listRelatives(attachment, allDescendents=True, type="mesh")
        if shape:
            shapes.extend(cmds.ls(shape, long=True))

    index_to_remove = list()
    discarded_nodes = list()
    for i in range(0, len(connected_indices)):
        if not attachments:
            index_to_remove.append(i)
            continue
        is_matrix_in_attachments = connected_attachments[i][0] in attachments
        is_matrix_in_shapes = connected_attachments[i][0] in shapes
        is_mesh_in_attachments = connected_attachments[i][1] in attachments
        is_mesh_in_shapes = connected_attachments[i][1] in shapes
        matrix_found = is_matrix_in_attachments or is_matrix_in_shapes
        mesh_found = is_mesh_in_attachments or is_mesh_in_shapes
        # Remove attachment only if both nodes are contained in the selection
        if matrix_found and mesh_found:
            index_to_remove.append(i)

    index_to_remove = list(set(index_to_remove))
    for i in index_to_remove:
        logical_index = connected_indices[i]

        # Get the name of the child attributes and create a valid plug identifier to search for connections
        children = cmds.attributeQuery("targets", node=deformer, listChildren=True) or []
        children = ["{0}[{1}].{2}".format(attr, logical_index, x) for x in children]

        # Disconnect all child attributes
        for node_plug in children:
            connections = cmds.listConnections(node_plug, plugs=True, source=True) or []
            for source_plug in connections:
                try:
                    cmds.disconnectAttr(source_plug, node_plug)
                except:
                    pass

        child_attr = "{0}[{1}].attachmentToGeoConstraints".format(attr, logical_index)
        child_logical_indices = cmds.getAttr(child_attr, multiIndices=True) or []
        # Remove all entries to the multi weight attribute to maintain a clean state
        for idx in child_logical_indices:
            cmds.removeMultiInstance("{0}[{1}]".format(child_attr, idx), b=True)

        child_attr = "{0}[{1}].slideOnGeometryConstraints".format(attr, logical_index)
        child_logical_indices = cmds.getAttr(child_attr, multiIndices=True) or []
        # Remove all entries to the multi weight attribute to maintain a clean state
        for idx in child_logical_indices:
            cmds.removeMultiInstance("{0}[{1}]".format(child_attr, idx), b=True)

        successful_dettached.append(connected_attachments[i][0])

    for t in attachments:
        attachment_not_dettached = t not in successful_dettached
        attachment_shape_not_dettached = False
        shapes_attachment = cmds.listRelatives(t, shapes=True)
        if shapes_attachment:
            shapes_attachment = cmds.ls(shapes_attachment, long=True)
            attachment_shape_not_dettached = [i for i in shapes_attachment if i in successful_dettached]
        if attachment_not_dettached and not attachment_shape_not_dettached:
            unsuccessful_dettached.append(t)

    # Cleanup the weights of any plug that has no input connections
    # This is to avoid adding an attachment on top of an entry with still populated weights
    for log_index in logical_indices:
        mat_attr = attr + "[{0}].targetWorldMatrix".format(log_index)
        mesh_attr = attr + "[{0}].targetWorldMesh".format(log_index)
        if (cmds.listConnections(mat_attr, destination=True) or
            cmds.listConnections(mesh_attr, destination=True)):
            continue
        child_attr = "{0}[{1}].attachmentToGeoConstraints".format(attr, log_index)
        child_logical_indices = cmds.getAttr(child_attr, multiIndices=True) or []
        # Remove all entries to the multi weight attribute to maintain a clean state
        for idx in child_logical_indices:
            cmds.removeMultiInstance("{0}[{1}]".format(child_attr, idx), b=True)

        child_attr = "{0}[{1}].slideOnGeometryConstraints".format(attr, log_index)
        child_logical_indices = cmds.getAttr(child_attr, multiIndices=True) or []
        # Remove all entries to the multi weight attribute to maintain a clean state
        for idx in child_logical_indices:
            cmds.removeMultiInstance("{0}[{1}]".format(child_attr, idx), b=True)

    return successful_dettached, unsuccessful_dettached


@undo_chunk
def add_targets():
    """Connect attachments to the deformer node. Depending on the type of the attachment.

    Selection order:
        1) Attachments to connect.
        2) Deformer node to connect the attachments to.

    Returns:
        bool: False if there was an error. True otherwise.
    """
    plugin_check()
    current_selection = cmds.ls(selection=True, long=True)

    attachments, deformer = get_anchors_and_deformer(current_selection)
    if not deformer or not attachments:
        print("{0} No valid attachments and deformer provided. Please, retry adding the attachments "
              "by selecting the elements in the following order: "
              "1) Attachments, "
              "2) Mesh with AdonisFX deformer applied to."
              "".format(UiConstants.ERROR_PREFIX))
        return False

    if not check_playback(deformer):
        return True
    
    unsuccessful_attached = list()
    successful_attached = list()

    # Check if we are adding geometries or transform attachments.
    geometries_to_attach = list()
    transforms_to_attach = list()
    for attachment in attachments:
        if cmds.ls(attachment, type="mesh") or cmds.listRelatives(attachment, type="mesh"):
            geometries_to_attach.append(attachment)
        else:
            transforms_to_attach.append(attachment)

    if geometries_to_attach:
        # Add geometries as attachments
        successful_attached, unsuccessful_attached = add_geometry_target(deformer, geometries_to_attach)

    if transforms_to_attach:
        # Add transforms as attachments
        transforms_attached = list()
        transforms_duplicated = list()
        transforms_attached, transforms_duplicated = add_attachment(deformer, transforms_to_attach)
        successful_attached.extend(transforms_attached)
        unsuccessful_attached.extend(transforms_duplicated)

    deformer_short_name = cmds.ls(deformer, shortNames=True)[0]
    if unsuccessful_attached and not successful_attached: # All attachments are skipped
        unsuccessful_attached = ["\"{0}\"".format(s) for s in unsuccessful_attached]
        attachment_names = ", ".join(unsuccessful_attached)
        print("{0} No new attachments connected to \"{1}\". "
              "None of the selected nodes could be connected or they are already "
              "connected to the deformer: {2}."
              "".format(UiConstants.ERROR_PREFIX, deformer_short_name, attachment_names))
        return False
    elif not successful_attached: # No connected attachments (no skipping)
        print("{0} No new attachments connected to \"{1}\". Please, retry."
              "".format(UiConstants.ERROR_PREFIX, deformer_short_name))
        return False
    elif unsuccessful_attached: # Some attachments skipped, some added
        successful_attached = ["\"{0}\"".format(s) for s in successful_attached]
        successful_attachment_names = ", ".join(successful_attached)
        unsuccessful_attached = ["\"{0}\"".format(s) for s in unsuccessful_attached]
        skip_attachment_names = ", ".join(unsuccessful_attached)
        print("{0} Attachments connected successfully to \"{1}\": {2}. "
              "The following attachments are already connected to the "
              "deformer or could not be successfully added: {3}."
              "".format(UiConstants.WARNING_PREFIX, deformer_short_name, successful_attachment_names, skip_attachment_names))
        return True
    else: # All added, no skipped
        successful_attached = ["\"{0}\"".format(s) for s in successful_attached]
        attachment_names = ", ".join(successful_attached)
        print("{0} Attachments connected successfully to \"{1}\": {2}."
              "".format(UiConstants.INFO_PREFIX, deformer_short_name, attachment_names))
        return True


@undo_chunk
def remove_targets():
    """Remove attachments from the deformer node. Depending on the type of the attachment.

    Selection order:
        1) Attachments to disconnect.
        2) Deformer node to disconnect the attachments from.

    Returns:
        bool: False if there was an error. True otherwise.
    """
    plugin_check()
    current_selection = cmds.ls(selection=True, long=True)

    attachments, deformer = get_anchors_and_deformer(current_selection)
    if not deformer:
        print("{0} Could not find a valid deformer from the provided selection. "
              "Please, make one of the following selections and try again: "
              "1) The attachments to remove plus the geometry with the AdonisFX deformer, "
              "2) Only the geometry with the AdonisFX deformer to remove all the attachments."
              "".format(UiConstants.ERROR_PREFIX))
        return False

    if not check_playback(deformer):
        return True

    deformer_short_name = cmds.ls(deformer, shortNames=True)[0]
    weights_type = cmds.AdnPaintDataCommand(query=True, weight=True)
    painting_deformer = deformer_being_painted(deformer_short_name)
    painting_deformer_error_message = "Removing targets while painting is not allowed. " \
                                      "Please, exit from the paint context and try again."

    successful_dettached = list()
    unsuccessful_dettached = list()
    transforms_dettached = list()
    transform_not_dettached = list()
    if not attachments:
        # Check if attachments are being painted
        if painting_deformer and (weights_type == ConstraintTypesNiceNames.ATTACHMENT or
                                  weights_type == ConstraintTypesNiceNames.ATTACHMENT_GEOMETRY or
                                  weights_type == ConstraintTypesNiceNames.SLIDE_GEOMETRY):
            print("{0} {1}".format(UiConstants.ERROR_PREFIX, painting_deformer_error_message))
            return False

        # Remove every attachment found
        successful_dettached, unsuccessful_dettached = remove_geometry_target(deformer)
        transforms_dettached, transform_not_dettached = remove_attachment(deformer)
        successful_dettached.extend(transforms_dettached)
        unsuccessful_dettached.extend(transform_not_dettached)
    else:
        geometries_to_detach = list()
        transforms_to_detach = list()
        for attachment in attachments:
            if cmds.ls(attachment, type="mesh") or cmds.listRelatives(attachment, type="mesh"):
                geometries_to_detach.append(attachment)
            else:
                transforms_to_detach.append(attachment)

        # Check if attachments are being painted before making any removal
        if geometries_to_detach:
            if painting_deformer and (weights_type == ConstraintTypesNiceNames.ATTACHMENT_GEOMETRY or
                                      weights_type == ConstraintTypesNiceNames.SLIDE_GEOMETRY):
                print("{0} {1}".format(UiConstants.ERROR_PREFIX, painting_deformer_error_message))
                return False
        if transforms_to_detach:
            if painting_deformer and weights_type == ConstraintTypesNiceNames.ATTACHMENT:
                print("{0} {1}".format(UiConstants.ERROR_PREFIX, painting_deformer_error_message))
                return False

        # Remove targets
        if geometries_to_detach:
            # Remove geometries as attachments
            successful_dettached, unsuccessful_dettached = remove_geometry_target(deformer, geometries_to_detach)

        if transforms_to_detach:
            # Remove transforms as attachments
            transforms_attached = list()
            transforms_duplicated = list()
            transforms_attached, transforms_duplicated = remove_attachment(deformer, transforms_to_detach)
            successful_dettached.extend(transforms_attached)
            unsuccessful_dettached.extend(transforms_duplicated)

    if not unsuccessful_dettached and not successful_dettached:
        # Attachments selected did not have any effect
        unsuccessful_dettached.extend(attachments)
        if not unsuccessful_dettached:
            print("{0} Selected deformer has no attachments to remove.".format(UiConstants.ERROR_PREFIX))
            return False

    if unsuccessful_dettached and successful_dettached:
        unsuccessful_dettached = ["\"{0}\"".format(s) for s in unsuccessful_dettached]
        successful_dettached = ["\"{0}\"".format(s) for s in successful_dettached]
        print("{0} The disconnect attachment action for \"{1}\" did not have any effect for: {2}. "
              "The following attachments disconnected successfully: {3}."
              "".format(UiConstants.WARNING_PREFIX, deformer_short_name, ", ".join(unsuccessful_dettached), ", ".join(successful_dettached)))
        return True
    elif unsuccessful_dettached:
        unsuccessful_dettached = ["\"{0}\"".format(s) for s in unsuccessful_dettached]
        attachment_names = ", ".join(unsuccessful_dettached)
        print("{0} The disconnect attachment action for \"{1}\" did not have any effect for: {2}."
              "".format(UiConstants.ERROR_PREFIX, deformer_short_name, attachment_names))
        return False
    elif successful_dettached:
        successful_dettached = ["\"{0}\"".format(s) for s in successful_dettached]
        attachment_names = ", ".join(successful_dettached)
        print("{0} Attachments disconnected successfully from \"{1}\": {2}."
              "".format(UiConstants.INFO_PREFIX, deformer_short_name, attachment_names))
        return True


@undo_chunk
def add_slide_segment_constraint():
    plugin_check()
    """Connect two given transform nodes to the deformer node to work as root
    and tip points of a segment that the geometry can slide on.
    Selection order:
    1) Transform nodes to connect (source).
    2) Deformer node to connect the transforms to (target).
    
    Returns:
        bool: False if there was an error. True otherwise.
    """
    current_selection = cmds.ls(selection=True, long=True)
    if not current_selection:
        print("{0} Selection is empty. Please, make sure that you select an "
              "AdonisFX deformer with slide on segment constraints and "
              "try again."
              "".format(UiConstants.ERROR_PREFIX))
        return False

    transforms, deformer = get_anchors_and_deformer(current_selection)
    if not deformer or not transforms:
        print("{0} No valid transform nodes and deformer provided. "
              "Please, select the elements in the following order "
              "and try again: "
              "1) Transform nodes defining segments to slide on, "
              "2) Mesh with AdonisFX deformer applied to."
              "".format(UiConstants.ERROR_PREFIX))
        return False

    if not check_playback(deformer):
        return True
    
    if len(transforms) < 2:
        print("{0} Please, select at least two transform nodes to define a segment. "
              "Then, the mesh with AdonisFX deformer applied to."
              "".format(UiConstants.ERROR_PREFIX))
        return False

    if not scene_parent_check(transforms):
        print("{0} The current provided selection does not satisfy this condition for slide on segment constraints. "
              "Please, select transform nodes defining a segment in a consistent order following the scene hierarchy. "
              "(Eg. parentN > ... > parent1 > leaf_node)."
              "".format(UiConstants.ERROR_PREFIX))
        return False

    # Get destination plugs
    attr = "{0}.slideOnSegmentConstraintsList".format(deformer)
    logical_indices = cmds.getAttr(attr, multiIndices=True) or []

    # Ensure that we connect the segment after the last connected plug
    # Valid plugs are the ones who have both root and tip matrices connected
    connected_indices = list()
    all_connected_indices = list()
    for index in logical_indices:
        full_attr_root = "{0}[{1}].slideOnSegmentRootMatrix".format(attr, index)
        full_attr_tip = "{0}[{1}].slideOnSegmentTipMatrix".format(attr, index)
        roots = cmds.listConnections(full_attr_root, destination=True) or []
        tips = cmds.listConnections(full_attr_tip, destination=True) or []
        if roots or tips:
            all_connected_indices.append(index)
        if not roots or not tips:
            continue
        connected_indices.append(index)

    # Get the transform names of the segments that are already connected
    segments_connected = list()
    for id in connected_indices:
        anchors_connected_root = cmds.listConnections(
            "{0}[{1}].slideOnSegmentRootMatrix".format(attr, id))
        if not anchors_connected_root:
            continue
        anchors_connected_tip = cmds.listConnections(
            "{0}[{1}].slideOnSegmentTipMatrix".format(attr, id))
        if not anchors_connected_tip:
            continue
        # Get the already connected segment pairs
        segments_connected.append((
            cmds.ls(anchors_connected_root[0], long=True)[0],
            cmds.ls(anchors_connected_tip[0], long=True)[0]))

    successful_attached = list()
    duplicated_segments  = list()
    # Attach the segments to the next free plug position
    # If no connected indices were provided assume that the segments will be
    # added to the first entry in the array plug
    last_index = all_connected_indices[-1] if all_connected_indices else -1
    new_index = last_index + 1
    for i in range(0, len(transforms) - 1):
        name_root = transforms[i]
        name_tip = transforms[i + 1]
        # NOTE: locator1 - locator2 is the same as locator2 - locator1
        tip_root = (name_root, name_tip)
        root_tip = (name_tip, name_root)
        if tip_root in segments_connected or root_tip in segments_connected:
            duplicated_segments.append(tip_root)
            continue
        world_matrix_root = "{0}.worldMatrix[0]".format(name_root)
        world_matrix_tip = "{0}.worldMatrix[0]".format(name_tip)
        if not cmds.objExists(world_matrix_root) or not cmds.objExists(world_matrix_tip):
            continue
        cmds.connectAttr(world_matrix_root, 
                         "{0}[{1}].slideOnSegmentRootMatrix".format(attr, new_index))
        cmds.connectAttr(world_matrix_tip, 
                         "{0}[{1}].slideOnSegmentTipMatrix".format(attr, new_index))

        child_attr = "{0}[{1}].slideOnSegmentConstraints".format(attr, new_index)
        child_logical_indices = cmds.getAttr(child_attr, multiIndices=True) or []
        # Remove all entries to the multi weight attribute to maintain a clean state
        for idx in child_logical_indices:
            cmds.removeMultiInstance("{0}[{1}]".format(child_attr, idx), b=True)

        successful_attached.append(tip_root)
        new_index += 1

    deformer_short_name = cmds.ls(deformer, shortNames=True)[0]
    if duplicated_segments and not successful_attached: # All anchors are skipped 
        duplicated_segments = ["\"{0} - {1}\"".format(cmds.ls(s[0], shortNames=True)[0],
                                                      cmds.ls(s[1], shortNames=True)[0]) for s in duplicated_segments]
        segments_names = ", ".join(duplicated_segments)
        print("{0} No new segments connected to \"{1}\". "
              "All segments are already connected to the deformer: {2}."
              "".format(UiConstants.WARNING_PREFIX, deformer_short_name, segments_names))
        return True
    elif not successful_attached: # No connected segments (no skipping) 
        print("{0} No new segments connected to \"{1}\". Please, retry."
              "".format(UiConstants.ERROR_PREFIX, deformer_short_name))
        return False
    elif duplicated_segments: # Some segments skipped, some added
        successful_attached = ["\"{0} - {1}\"".format(cmds.ls(s[0], shortNames=True)[0],
                                                      cmds.ls(s[1], shortNames=True)[0]) for s in successful_attached]
        successful_anchor_names = ", ".join(successful_attached)
        duplicated_segments = ["\"{0} - {1}\"".format(cmds.ls(s[0], shortNames=True)[0],
                                                      cmds.ls(s[1], shortNames=True)[0]) for s in duplicated_segments]
        skip_segments_names = " ,".join(duplicated_segments)
        print("{0} Segments connected successfully to \"{1}\": {2}. "
              "The following segments are already connected to the deformer: {3}."
              "".format(UiConstants.WARNING_PREFIX, deformer_short_name, successful_anchor_names, skip_segments_names))
    else: # All added, no skipped
        successful_attached = ["\"{0} - {1}\"".format(cmds.ls(s[0], shortNames=True)[0],
                                                      cmds.ls(s[1], shortNames=True)[0]) for s in successful_attached]
        segments_names = ", ".join(successful_attached)
        print("{0} Segments connected successfully to \"{1}\": {2}." 
              "".format(UiConstants.INFO_PREFIX, deformer_short_name, segments_names))
    
    # Re-query the logical indices to gather the new addition
    logical_indices = cmds.getAttr(attr, multiIndices=True) or []

    # Cleanup the weights of any plug that has no input connections
    # This is to avoid adding a segment on top of an entry with still populated weights
    for log_index in logical_indices:
        anchors_connected_root = cmds.listConnections(
            "{0}[{1}].slideOnSegmentRootMatrix".format(attr, log_index), destination=True)
        anchors_connected_tip = cmds.listConnections(
            "{0}[{1}].slideOnSegmentTipMatrix".format(attr, log_index), destination=True)
        if anchors_connected_root or anchors_connected_tip:
            continue
        child_attr = "{0}[{1}].slideOnSegmentConstraints".format(attr, log_index)
        child_logical_indices = cmds.getAttr(child_attr, multiIndices=True) or []
        # Remove all entries to the multi weight attribute to maintain a clean state
        for idx in child_logical_indices:
            cmds.removeMultiInstance("{0}[{1}]".format(child_attr, idx), b=True)

    return True


@undo_chunk
def remove_slide_segment_constraint():
    plugin_check()
    """Remove input connections of slide on segment constraints from the
    selected deformer node.
    - If we select both nodes of a segment: Remove that segment
    - If we select one node of the segment: Remove that segment if no node pair was selected
    for a different segment.
    - If we select no nodes of a segment: Remove all segments from the deformer.

    Returns:
        bool: False if there was an error. True otherwise.
    """
    current_selection = cmds.ls(selection=True, long=True)
    if not current_selection:
        print("{0} Selection is empty. Please, make sure that you select an "
              "AdonisFX deformer with slide on segment constraints and "
              "try again."
              "".format(UiConstants.ERROR_PREFIX))
        return False

    transforms, deformer = get_anchors_and_deformer(current_selection)
    if not deformer:
        print("{0} Could not find a valid deformer from the provided selection. "
              "Please, make sure that you select an AdonisFX deformer with "
              "slide on segment constraints and try again."
              "".format(UiConstants.ERROR_PREFIX))
        return False

    if not check_playback(deformer):
        return True

    deformer_short_name = cmds.ls(deformer, shortNames=True)[0]

    # Check if the deformer is being painted
    if deformer_being_painted(deformer_short_name):
        # Check if segments are being painted
        weights_type = cmds.AdnPaintDataCommand(query=True, weight=True)
        if weights_type == ConstraintTypesNiceNames.SLIDE_SEGMENT:
            print("{0} Removing slide on segments constraints is not allowed while painting. "
                  "Please, exit from the paint context and try again."
                  "".format(UiConstants.ERROR_PREFIX))
            return False

    # Get list of multi indices
    attr = "{0}.slideOnSegmentConstraintsList".format(deformer)
    logical_indices = cmds.getAttr(attr, multiIndices=True) or []

    # Ensure that we connect the segment after the last connected plug
    successful_dettached = list()
    successful_dettached_flat = list()
    connected_segments = list()
    connected_indices = list()

    # Gather the connected segments. Pair of root/tip names per segment
    for index in logical_indices:
        full_attr_root = "{0}[{1}].slideOnSegmentRootMatrix".format(attr, index)
        full_attr_tip = "{0}[{1}].slideOnSegmentTipMatrix".format(attr, index)
        anchors_connected_root = cmds.listConnections(full_attr_root) or []
        # NOTE: Only consider segments disconnectable that have both 
        # anchors connected
        if not anchors_connected_root:
            continue
        anchors_connected_tip = cmds.listConnections(full_attr_tip) or []
        if not anchors_connected_tip:
            continue
        connected_indices.append(index)
        connected_segments.append((
            cmds.ls(anchors_connected_root, long=True)[0],
            cmds.ls(anchors_connected_tip, long=True)[0]))
    
    # If the deformer has no segments
    if not connected_indices:
        print("{0} The selected deformer has no segments to remove."
              "".format(UiConstants.ERROR_PREFIX))
        return False
    
    index_to_remove = list()
    discarded_nodes = list()
    for i in range(0, len(connected_indices)):
        # Remove all indices if no transform nodes were provided
        if not transforms:
            index_to_remove.append(i)
        # Remove segment only if both nodes are contained in the selection
        elif (connected_segments[i][0] in transforms and 
              connected_segments[i][1] in transforms):
            index_to_remove.append(i)
            # Keep track of node pairs forming a segment to avoid removing
            # segments which contain just 1 of them. Eg. Selecting two nodes forming
            # a segment but removing 3 segmens containing that node
            discarded_nodes.append(connected_segments[i][0])
            discarded_nodes.append(connected_segments[i][1])

    # Remove segments with one single entry in the selection if they weren't found
    # as a valid node pair inside of any other segment
    if transforms:
        for i in range(0, len(connected_indices)):
            root = connected_segments[i][0]
            tip = connected_segments[i][1]
            if root not in transforms and tip not in transforms:
                continue
            if root in discarded_nodes or tip in discarded_nodes:
                continue
            index_to_remove.append(i)

    index_to_remove = list(set(index_to_remove))
    for i in index_to_remove:
        logical_index = connected_indices[i]
        segment = connected_segments[i]

        # Get the name of the child attributes and create a valid plug identifier to search for connections
        children = cmds.attributeQuery("slideOnSegmentConstraintsList",
                                       node=deformer, listChildren=True) or []
        children = ["{0}[{1}].{2}".format(attr, logical_index, x) for x in children]

        # Disconnect all child attributes
        for node_plug in children:
            connections = cmds.listConnections(node_plug, plugs=True, source=True) or []
            for source_plug in connections:
                try:
                    cmds.disconnectAttr(source_plug, node_plug)
                except:
                    pass

        child_attr = "{0}[{1}].slideOnSegmentConstraints".format(attr, logical_index)
        child_logical_indices = cmds.getAttr(child_attr, multiIndices=True) or []
        # Remove all entries to the multi weight attribute to maintain a clean state
        for idx in child_logical_indices:
            cmds.removeMultiInstance("{0}[{1}]".format(child_attr, idx), b=True)

        successful_dettached.append(segment)
        # Keep track of nodes that are removed to then print them
        successful_dettached_flat.append(connected_segments[i][0])
        successful_dettached_flat.append(connected_segments[i][1])

    # Fill the unsuccessful dettached node to then print them
    success_dettach_flat = list(set(successful_dettached_flat))    
    unsuccessful_dettached = [t for t in transforms if t not in success_dettach_flat]

    success = True
    if unsuccessful_dettached:
        unsuccessful_dettached = ["\"{0}\"".format(cmds.ls(s, shortNames=True)[0]) for s in unsuccessful_dettached]
        attachment_names = ", ".join(unsuccessful_dettached)
        print("{0} The disconnect segment action for \"{1}\" did not have any effect for: {2}." 
              "".format(UiConstants.ERROR_PREFIX, deformer_short_name, attachment_names))
        success = False
    if successful_dettached:
        successful_dettached = ["\"{0} - {1}\"".format(cmds.ls(s[0], shortNames=True)[0], 
                                                             cmds.ls(s[1], shortNames=True)[0]) for s in successful_dettached]
        attachment_names = ", ".join(successful_dettached)
        print("{0} Segments disconnected successfully from \"{1}\": {2}." 
              "".format(UiConstants.INFO_PREFIX, deformer_short_name, attachment_names))

    # Cleanup the weights of any plug that has no input connections
    # This is to avoid adding a segment on top of an entry with still populated weights
    for log_index in logical_indices:
        anchors_connected_root = cmds.listConnections(
            "{0}[{1}].slideOnSegmentRootMatrix".format(attr, log_index), destination=True)
        anchors_connected_tip = cmds.listConnections(
            "{0}[{1}].slideOnSegmentTipMatrix".format(attr, log_index), destination=True)
        if anchors_connected_root or anchors_connected_tip:
            continue
        child_attr = "{0}[{1}].slideOnSegmentConstraints".format(attr, log_index)
        child_logical_indices = cmds.getAttr(child_attr, multiIndices=True) or []
        # Remove all entries to the multi weight attribute to maintain a clean state
        for idx in child_logical_indices:
            cmds.removeMultiInstance("{0}[{1}]".format(child_attr, idx), b=True)

    return success
