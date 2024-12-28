import sys

import maya.cmds as cmds
from adn.utils.constants import UiConstants
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


def get_map_attribute(attribute):
    """Retrieves the values and the associated indices of a map attribute.
    This getter is usually used to retrieve data from paintable attributes.

    Note:
        The current implementation does return the current numeric values for
        each item, meaning that if any item has an input connection, then the
        source of the connection is not retrieved nor returned.

    Args:
        attribute (str): name of the attribute to retrieve.

    Returns:
        list: list with sparse values in the map.
        list: list with the sparse indices associated to the values in the map.
    """
    attribute_tokens = attribute.split(".")
    if len(attribute_tokens) < 2:
        return list(), list()

    child_attribute = cmds.attributeQuery(attribute_tokens[1],
                                          node=attribute_tokens[0],
                                          listChildren=True)
    if not child_attribute:
        return list(), list()

    child_attribute = attribute + "[0].{0}".format(child_attribute[0])
    ids = cmds.getAttr(child_attribute, multiIndices=True) or []
    values = [None] * len(ids)
    for index, i in enumerate(ids):
        # Use getAttr per index to make sure that compound attributes
        # like fibers will also work
        values[index] = cmds.getAttr(child_attribute + "[{0}]".format(i))

    return values, ids


def get_ramp_attribute(attribute):
    """Retrieves the values and the associated indices of a ramp attribute.

    Args:
        attribute (str): name of the attribute to retrieve.

    Returns:
        list: list with values in the ramp.
        list: list with the positions associated to the values in the ramp.
        list: list with the identifier of the curve interpolation at each value.
    """
    short_name = attribute.split(".")[-1]
    ids = cmds.getAttr(attribute, multiIndices=True) or []
    values = [None] * len(ids)
    positions = [None] * len(ids)
    interpolations = [None] * len(ids)
    for index, i in enumerate(ids):
        base_attribute = "{0}[{1}]".format(attribute, i)
        value_attribute = "{0}.{1}_FloatValue".format(base_attribute, short_name)
        pos_attribute = "{0}.{1}_Position".format(base_attribute, short_name)
        interp_attribute = "{0}.{1}_Interp".format(base_attribute, short_name)
        values[index] = cmds.getAttr(value_attribute)
        positions[index] = cmds.getAttr(pos_attribute)
        interpolations[index] = cmds.getAttr(interp_attribute)

    return values, positions, interpolations


def get_plain_attribute(attribute):
    """Retrieves the value of a standard attribute.
    
    Args:
        attribute (str): name of the attribute to retrieve.
        
    Returns:
        float, int, bool or str: if the attribute has no input connections,
            then the raw value of the attribute is returned. In case that it
            is connected, then the name of the source attribute is returned.
    """
    if cmds.connectionInfo(attribute, isDestination=True):
        return cmds.connectionInfo(attribute, sourceFromDestination=True)
    else:
        return cmds.getAttr(attribute, silent=True)


def get_attachments_attribute(attribute):
    """Retrieves all data from an attachment attribute.

    Args:
        attribute (str): name of the attachments attribute to retrieve.

    Returns:
        list of dict: attachments data including matrix, weights and ids.
    """
    ids = cmds.getAttr(attribute, multiIndices=True) or []
    attachments = list()

    for i, idx in enumerate(ids):
        attachments.append({})
        # Matrix
        matrix_attribute = "{0}[{1}].attachmentMatrix".format(attribute, idx)
        attachments[i]["matrix"] = get_plain_attribute(matrix_attribute)

        # Attachment weights
        weights_attribute = "{0}[{1}].attachmentConstraints".format(
            attribute, idx)
        attachments[i]["attachment_weights"] = cmds.getAttr(
            weights_attribute)[0]
        attachments[i]["attachment_weights_ids"] = cmds.getAttr(
            weights_attribute, multiIndices=True) or []

    return attachments


def get_targets_attribute(attribute):
    """Retrieves all data from a targets attribute.

    Args:
        attribute (str): name of the targets attribute to retrieve.

    Returns:
        list of dict: targets data including matrix, mesh, attachment weights + ids
        and slide weights + ids.
    """
    ids = cmds.getAttr(attribute, multiIndices=True) or []
    targets = list()

    for i, idx in enumerate(ids):
        targets.append({})
        # Matrix
        matrix_attribute = "{0}[{1}].targetWorldMatrix".format(attribute, idx)
        targets[i]["matrix"] = get_plain_attribute(matrix_attribute)

        # Mesh
        mesh_attribute = "{0}[{1}].targetWorldMesh".format(attribute, idx)
        targets[i]["mesh"] = get_plain_attribute(mesh_attribute)

        # Attachment weights
        attach_weights_attribute = "{0}[{1}].attachmentToGeoConstraints".format(
            attribute, idx)
        targets[i]["attachment_to_geo_weights"] = cmds.getAttr(
            attach_weights_attribute)[0]
        targets[i]["attachment_to_geo_weights_ids"] = cmds.getAttr(
            attach_weights_attribute, multiIndices=True) or []

        # Slide weights
        slide_weights_attribute = "{0}[{1}].slideOnGeometryConstraints".format(
            attribute, idx)
        targets[i]["slide_on_geo_weights"] = cmds.getAttr(
            slide_weights_attribute)[0]
        targets[i]["slide_on_geo_weights_ids"] = cmds.getAttr(
            slide_weights_attribute, multiIndices=True) or []

    return targets


def get_slide_segments_attribute(attribute):
    """Retrieves all data from a slide on segment attribute.

    Args:
        attribute (str): name of the slide on segment attribute to retrieve.

    Returns:
        list of dict: slide on segment data including root matrix, tip matrix, weights and ids.
    """
    ids = cmds.getAttr(attribute, multiIndices=True) or []
    slide_segments = list()

    for i, idx in enumerate(ids):
        slide_segments.append({})
        # Matrices
        root_matrix_attribute = "{0}[{1}].slideOnSegmentRootMatrix".format(attribute, idx)
        tip_matrix_attribute = "{0}[{1}].slideOnSegmentTipMatrix".format(attribute, idx)

        slide_segments[i]["root_matrix"] = get_plain_attribute(root_matrix_attribute)
        slide_segments[i]["tip_matrix"] = get_plain_attribute(tip_matrix_attribute)

        # Slide on segments weights
        weights_attribute = "{0}[{1}].slideOnSegmentConstraints".format(
            attribute, idx)
        slide_segments[i]["slide_segment_weights"] = cmds.getAttr(
            weights_attribute)[0]
        slide_segments[i]["slide_segment_weights_ids"] = cmds.getAttr(
            weights_attribute, multiIndices=True) or []

    return slide_segments


def get_sim_mesh_list_attribute(attribute):
    """Retrieves all data from an simulation mesh list attribute.

    Args:
        attribute (str): name of the simulation mesh list attribute to retrieve.

    Returns:
        list of dict: simulation mesh list data including meshes and matrices.
    """
    ids = cmds.getAttr(attribute, multiIndices=True) or []
    mesh_list = list()

    for i, idx in enumerate(ids):
        mesh_list.append({})
        # Matrix
        matrix_attribute = "{0}[{1}].simWorldMatrix".format(attribute, idx)
        mesh_list[i]["matrix"] = get_plain_attribute(matrix_attribute)

        # Mesh
        mesh_attribute = "{0}[{1}].simWorldMesh".format(attribute, idx)
        mesh_list[i]["mesh"] = get_plain_attribute(mesh_attribute)

    return mesh_list


def get_anim_mesh_list_attribute(attribute):
    """Retrieves all data from an animation mesh list attribute.

    Args:
        attribute (str): name of the animation mesh list attribute to retrieve.

    Returns:
        list of dict: animation mesh list data including meshes and matrices.
    """
    ids = cmds.getAttr(attribute, multiIndices=True) or []
    mesh_list = list()

    for i, idx in enumerate(ids):
        mesh_list.append({})
        # Matrix
        matrix_attribute = "{0}[{1}].animWorldMatrix".format(attribute, idx)
        mesh_list[i]["matrix"] = get_plain_attribute(matrix_attribute)

        # Mesh
        mesh_attribute = "{0}[{1}].animWorldMesh".format(attribute, idx)
        mesh_list[i]["mesh"] = get_plain_attribute(mesh_attribute)

    return mesh_list


def set_plain_attribute(attribute, value, attribute_type):
    """Sets the value to a standard attribute.

    Args:
        attribute (str): full name of the attribute to set with format
            "node_name.attribute_name".
        value (str, int, float, list, bool): attribute value to set.
        attribute_type (str): descriptor of the attribute type.

    Returns:
        bool: True if the attribute was properly set. False otherwise.
        str: additional information only in case of error.
    """
    # Check it attribute was already connected, disconnect if it is
    disconnect_attribute_from_source(attribute)

    # String values from a json load in Python 2 return unicode
    if sys.version_info[0] < 3 and type(value) is unicode:
        value = str(value)

    if type(value) is str:
      if cmds.objExists(value):
          # Recognized as connectable object
          cmds.connectAttr(value, attribute, force=True)
      elif attribute_type == "string":
          # Recognized as a string plug.
          # NOTE: Connected string plugs not found in scene will instead of
          # making the connection it will set the string value directly.
          cmds.setAttr(attribute, value, type="string")
      else:
          # Mismatch between value type and plug type
          return False, ("Attribute {0} not configured: could not assign "
                         "the given value {1}".format(attribute, value))
    elif attribute_type == "matrix":
        # Attempt to set attribute value with type specification
        cmds.setAttr(attribute, value, type="matrix")
    else:
        # Attempt to set attribute without specifier
        try:
            cmds.setAttr(attribute, value)
        except:
            return False, ("Attribute {0} not configured: could not assign "
                           "the given value {1}".format(attribute, value))
    return True, None


def set_numeric_compound_attribute(attribute, value, attribute_type):
    """Sets the value to a numeric compound attribute (i.e. gravity direction).

    Args:
        attribute (str): full name of the attribute to set with format
            "node_name.attribute_name".
        value (list): attribute value to set.
        attribute_type (str): descriptor of the attribute type.

    Example of input `value`:
        [
            [0.0, -1.0, 0.0]
        ]

    Returns:
        bool: True if the attribute was properly set. False otherwise.
        str: additional information only in case of error.
    """
    # Check size and type of the parent compound attribute
    size = len(value)
    if size != 1:
        return False, ("Attribute {0} not configured: inconsistent size, "
                       "expected 1, got {1}"
                       "".format(attribute, size))
    value = value[0]
    if not value:
        return False, ("Attribute {0} not configured: value of a compound "
                       "attribute is empty"
                       "".format(attribute))
    if type(value) not in (list, tuple):
        return False, ("Attribute {0} not configured: unexpected type of a "
                       "compound attribute, expected list or tuple, got {1}"
                       "".format(attribute, type(value)))

    # Check it attribute was already connected, disconnect if it is
    disconnect_attribute_from_source(attribute)

    # Prepare to set
    raw_type = type(value[0])
    if raw_type not in [int, float]:
        return False, ("Attribute {0} not configured: type of a compound "
                       "attribute not supported ({1}). Type must be int or float"
                       "".format(attribute, raw_type))
    size = len(value)
    nice_type = "float" if raw_type is float else "long"
    nice_type += "{0}".format(size)
    # Set value
    try:
        cmds.setAttr(attribute, *value, type=nice_type)
    except:
        return False, ("Attribute {0} not configured: failed to set compound "
                       "attribute ({1}) with type {2}"
                       "".format(attribute, value, nice_type))
    return True, None


def set_numeric_compound_map_attribute(attribute, value, attribute_type):
    """Sets the values to a numeric compound map attribute (i.e. fibers).

    Args:
        attribute (str): full name of the attribute to set with format
            "node_name.attribute_name".
        value (list): attribute value to set. As map, the content
            is split into 2 lists: the first one contains the values, and the
            second one contains the indices associated to each value.
        attribute_type (str): descriptor of the attribute type. Not used in
            this implementation, required to keep consistency in 
            `importer.set_attribute_definition`.

    Example of input `value`:
        [
            [
                [1.0, 0.0, 0.0],
                ...
            ],
            [0, 1, 2, ...]
        ]

    Returns:
        bool: True if the attribute was properly set. False otherwise.
        str: additional information only in case of error.
    """
    values, indices = value
    if not values or not indices:
        return True, None

    tokens = attribute.split(".")
    if len(tokens) != 2:
        return False, ("Attribute compound map {0} not configured: could not "
                       "retrieve the node name"
                       "".format(attribute))

    node, attribute_name = tokens
    children = cmds.attributeQuery(attribute_name, node=node,
                                   listChildren=True)
    if not children:
        return False, ("Attribute compound map {0} not configured: could not "
                       "get the list of children attributes"
                       "".format(attribute))

    child_name = "{0}[0].{1}".format(attribute, children[0])
    for idx in range(len(indices)):
        try:
            # values is a list of lists of one vector3
            # i.e.: [ [[1,0,0]], [[1,0,0]], ... ]
            value = values[idx][0]
            child = "{0}[{1}]".format(child_name, indices[idx])
            cmds.setAttr(child, *value, size=3)
        except:
            return False, ("Attribute compound map {0} not configured: could "
                           "not set values at index {1}"
                           "".format(attribute, idx))

    return True, None


def set_map_attribute(attribute, value, attribute_type):
    """Sets the values to a numeric map attribute (i.e. compression weights).

    Args:
        attribute (str): full name of the attribute to set with format
            "node_name.attribute_name".
        value (list): attribute value to set. As map, the content
            is split into 2 lists: the first one contains the values, and the
            second one contains the indices associated to each value.
        attribute_type (str): descriptor of the attribute type. Not used in
            this implementation, required to keep consistency in 
            `importer.set_attribute_definition`.

    Example of input `value`:
        [
            [1.0, 1.0, 1.0, ...],
            [0, 1, 2, ...]
        ]

    Returns:
        bool: True if the attribute was properly set. False otherwise.
        str: additional information only in case of error.
    """
    values, indices = value
    if not values or not indices:
        return True, None

    tokens = attribute.split(".")
    if len(tokens) != 2:
        return False, ("Attribute map {0} not configured: could not retrieve "
                       "the node name or the attribute name"
                       "".format(attribute))

    node, attribute_name = tokens
    children = cmds.attributeQuery(attribute_name, node=node, listChildren=True)
    if not children:
        return False, ("Attribute map {0} not configured: could not get the "
                       "list of children attributes"
                       "".format(attribute))
    if len(values) != len(indices):
        return False, ("Could not set value to attribute map {0}: number of values "
                       "({1}) does not match number of indices ({2})"
                       "".format(attribute, len(values), len(indices)))

    child = "{0}[0].{1}".format(attribute, children[0])
    for idx in range(len(indices)):
        cmds.setAttr("{0}[{1}]".format(child, indices[idx]), values[idx])

    return True, None


def set_ramp_attribute(attribute, value, attribute_type):
    """Sets the values to a ramp attribute (i.e. activationRemap).

    Args:
        attribute (str): full name of the attribute to set with format
            "node_name.attribute_name".
        value (list): attribute value to set. As map, the content
            is split into 3 lists: the first one contains the values in the
            Y-axis of the ramp, the second one contains the positions in the
            X-axis of the ramp, and the third one contains the identifiers
            of the interpolation type at each position.
        attribute_type (str): descriptor of the attribute type. Not used in
            this implementation, required to keep consistency in
            `importer.set_attribute_definition`.
            
    Example of input `value`:
        [
            [0.0, 1.0, 0.2, 0.1],
            [0.0, 1.0, 0.5, 0.0],
            [1, 3, 2, 0]
        ]

    Returns:
        bool: True if the attribute was properly set. False otherwise.
        str: additional information only in case of error.
    """
    values, positions, interpolations = value
    if not values or not positions or not interpolations:
        return True, None

    if len(values) != len(positions) != len(interpolations):
        return False, ("Attribute remap {0} not configured: inconsistent "
                       "sizes for values, positions and interpolations attributes"
                       "".format(attribute))

    short_name = attribute.split(".")[-1]
    for i in range(len(values)):
        base_attribute = "{0}[{1}]".format(attribute, i)
        value_attribute = "{0}.{1}_FloatValue".format(base_attribute, short_name)
        pos_attribute = "{0}.{1}_Position".format(base_attribute, short_name)
        interp_attribute = "{0}.{1}_Interp".format(base_attribute, short_name)
        cmds.setAttr(value_attribute, values[i])
        cmds.setAttr(pos_attribute, positions[i])
        cmds.setAttr(interp_attribute, interpolations[i])

    return True, None


def set_attachment_attributes(attribute, value, attribute_type):
    """Sets the values to attachment attributes including the input connection
    to the matrix plug, and the values associated to the painted weights.

    Args:
        attribute (str): full name of the attribute to set with format
            "node_name.attribute_name".
        value (list): attribute value to set. Each item in the list is a
            dictionary with 3 entries: matrix (name of the input matrix
            object to connect or matrix values), list of weights (the actual
            values) and list of indices (the indices in sparse array associated
            to each value.
        attribute_type (str): descriptor of the attribute type. Not used in
            this implementation, required to keep consistency in
            `importer.set_attribute_definition`.
            
    Example of input `value`:
    [
        {
            "matrix": "referenceObject.worldMatrix[0]",
            "attachment_weights": [0.0, ...},
            "attachment_weights_ids": [0, ...]
        }
        ...
    ]

    Returns:
        bool: True if the attribute was properly set. False otherwise.
        str: additional information only in case of error.
    """
    attachments_not_attached = list()
    idx = 0
    for attachment in value:
        # Matrix
        matrix = attachment["matrix"]
        matrix_attribute = "{0}[{1}].attachmentMatrix".format(attribute, idx)
        # String values from a json load in Python 2 return unicode
        if sys.version_info[0] < 3 and type(matrix) is unicode:
            matrix = str(matrix)

        # The value is the name of a node
        if type(matrix) is str and cmds.objExists(matrix):
            # Connect matrix
            disconnect_attribute_from_source(matrix_attribute)
            cmds.connectAttr(matrix, matrix_attribute, force=True)
        # The value is a matrix
        elif type(matrix) is not str:
            cmds.setAttr(matrix_attribute, matrix, type="matrix")
        # Unrecognized value
        else:
            attachments_not_attached.append(idx)

        # Attachment weights
        weights_indices = attachment["attachment_weights_ids"]
        if not weights_indices:
            idx += 1
            continue
        weights_attribute = "{0}[{1}].attachmentConstraints".format(attribute, idx)
        weights = attachment["attachment_weights"]
        for w_idx in range(len(weights_indices)):
            cmds.setAttr("{0}[{1}]".format(weights_attribute, weights_indices[w_idx]),
                         weights[w_idx])

        # Next slot
        idx += 1

    if attachments_not_attached:
        info = ",".join([str(i) for i in attachments_not_attached])
        return False, ("Could not configure attachments ({0}) to attribute "
                       "{1}: either the target transformation was not found "
                       "or the input value is not a valid matrix"
                       ".".format(info, attribute))

    return True, list()


def set_targets_attribute(attribute, value, attribute_type):
    """Sets the values to target attributes including the input connection
    to the matrix plug, and the values associated to the painted weights.

    Args:
        attribute (str): full name of the attribute to set with format
            "node_name.attribute_name".
        value (list): attribute value to set. Each item in the list is a
            dictionary with 6 entries: matrix (name of the input matrix
            object to connect or matrix values), mesh (name of the input
            mesh object to connect), list of attachment weights (the actual
            values), list of attachment indices (the indices in sparse array
            associated to each value, list of slide weights (the actual
            values), list of slide indices (the indices in sparse array
            associated to each value.
        attribute_type (str): descriptor of the attribute type. Not used in
            this implementation, required to keep consistency in
            `importer.set_attribute_definition`.
            
    Example of input `value`:
    [
        {
            "matrix": "referenceObject.worldMatrix[0]",
            "mesh": "referenceObject.worldMesh[0]",
            "attachment_to_geo_weights": [0.0, ...},
            "attachment_to_geo_weights_ids": [0, ...],
            "slide_on_geo_weights": [0.0, ...},
            "slide_on_geo_weights_ids": [0, ...]
        }
        ...
    ]

    Returns:
        bool: True if the attribute was properly set. False otherwise.
        str: additional information only in case of error.
    """
    targets_not_attached = list()
    idx = 0
    for target in value:
        # Matrix and mesh
        matrix = target["matrix"]
        mesh = target["mesh"]
        matrix_attached = True
        mesh_attached = True

        matrix_attribute = "{0}[{1}].targetWorldMatrix".format(attribute, idx)
        mesh_attribute = "{0}[{1}].targetWorldMesh".format(attribute, idx)
        # String values from a json load in Python 2 return unicode
        if sys.version_info[0] < 3 and type(matrix) is unicode:
            matrix = str(matrix)
        # String values from a json load in Python 2 return unicode
        if sys.version_info[0] < 3 and type(mesh) is unicode:
            mesh = str(mesh)

        # The matrix value is the name of a node
        if type(matrix) is str and cmds.objExists(matrix):
            # Connect matrix
            disconnect_attribute_from_source(matrix_attribute)
            cmds.connectAttr(matrix, matrix_attribute, force=True)
        # The matrix value is a matrix
        elif type(matrix) is not str:
            cmds.setAttr(matrix_attribute, matrix, type="matrix")
        # Unrecognized value
        else:
            matrix_attached = False
        
        # The mesh value is the name of a node
        if type(mesh) is str and cmds.objExists(mesh):
            # Connect mesh
            disconnect_attribute_from_source(mesh_attribute)
            cmds.connectAttr(mesh, mesh_attribute, force=True)
        # Unrecognized value
        else:
            mesh_attached = False

        if not matrix_attached or not mesh_attached:
            targets_not_attached.append(idx)

        # Attachment to geo weights
        attach_weights_indices = target["attachment_to_geo_weights_ids"]
        if attach_weights_indices:
            attach_weights_attribute = "{0}[{1}].attachmentToGeoConstraints".format(attribute, idx)
            attach_weights = target["attachment_to_geo_weights"]
            for attach_idx in range(len(attach_weights_indices)):
                cmds.setAttr("{0}[{1}]".format(attach_weights_attribute, attach_weights_indices[attach_idx]),
                            attach_weights[attach_idx])

        # Slide on geo weights
        slide_weights_indices = target["slide_on_geo_weights_ids"]
        if slide_weights_indices:
            slide_weights_attribute = "{0}[{1}].slideOnGeometryConstraints".format(attribute, idx)
            slide_weights = target["slide_on_geo_weights"]
            for slide_idx in range(len(slide_weights_indices)):
                cmds.setAttr("{0}[{1}]".format(slide_weights_attribute, slide_weights_indices[slide_idx]),
                            slide_weights[slide_idx])

        # Next slot
        idx += 1

    if targets_not_attached:
        info = ",".join([str(i) for i in targets_not_attached])
        return False, ("Could not configure targets ({0}) to attribute {1}: "
                       "either the target mesh was not found or the input matrix is not valid."
                       ".".format(info, attribute))

    return True, list()


def set_slide_segments_attributes(attribute, value, attribute_type):
    """Sets the values to slide on segments attributes including the input connection
    to the matrices plugs, and the values associated to the painted weights.

    Args:
        attribute (str): full name of the attribute to set with format
            "node_name.attribute_name".
        value (list): attribute value to set. Each item in the list is a
            dictionary with 4 entries: root_matrix (name of the root input matrix
            object to connect or matrix values), tip_matrix (name of the tip input matrix
            object to connect or matrix values), list of weights (the actual
            values) and list of indices (the indices in sparse array associated
            to each value.
        attribute_type (str): descriptor of the attribute type. Not used in
            this implementation, required to keep consistency in
            `importer.set_attribute_definition`.

    Example of input `value`:
    [
        {
            "root_matrix": "referenceObject0.worldMatrix[0]",
            "tip_matrix": "referenceObject1.worldMatrix[0]",
            "slide_segment_weights": [0.0, ...},
            "slide_segment_weights_ids": [0, ...]
        }
        ...
    ]

    Returns:
        bool: True if the attribute was properly set. False otherwise.
        str: additional information only in case of error.
    """
    segments_not_attached = list()
    idx = 0
    for segment in value:
        # Matrices
        root_matrix = segment["root_matrix"]
        tip_matrix = segment["tip_matrix"]

        root_matrix_attribute = "{0}[{1}].slideOnSegmentRootMatrix".format(attribute, idx)
        tip_matrix_attribute = "{0}[{1}].slideOnSegmentTipMatrix".format(attribute, idx)
        # String values from a json load in Python 2 return unicode
        if sys.version_info[0] < 3 and type(root_matrix) is unicode:
            root_matrix = str(root_matrix)
        # String values from a json load in Python 2 return unicode
        if sys.version_info[0] < 3 and type(tip_matrix) is unicode:
            tip_matrix = str(tip_matrix)

        # The value is the name of a node
        if (type(root_matrix) is str and cmds.objExists(root_matrix) and
                type(tip_matrix) is str and cmds.objExists(tip_matrix)):
            # Connect matrix
            disconnect_attribute_from_source(root_matrix_attribute)
            disconnect_attribute_from_source(tip_matrix_attribute)
            cmds.connectAttr(root_matrix, root_matrix_attribute, force=True)
            cmds.connectAttr(tip_matrix, tip_matrix_attribute, force=True)

        # The value is a matrix
        elif type(root_matrix) is not str and type(tip_matrix) is not str:
            cmds.setAttr(root_matrix_attribute, root_matrix, type="matrix")
            cmds.setAttr(tip_matrix_attribute, tip_matrix, type="matrix")
        # Unrecognized value
        else:
            segments_not_attached.append(idx)

        # Slide segment weights
        weights_indices = segment["slide_segment_weights_ids"]
        if not weights_indices:
            idx += 1
            continue
        weights_attribute = "{0}[{1}].slideOnSegmentConstraints".format(attribute, idx)
        weights = segment["slide_segment_weights"]
        for w_idx in range(len(weights_indices)):
            cmds.setAttr("{0}[{1}]".format(weights_attribute, weights_indices[w_idx]),
                         weights[w_idx])

        # Next slot
        idx += 1

    if segments_not_attached:
        info = ",".join([str(i) for i in segments_not_attached])
        return False, ("Could not configure slide on segments ({0}) to attribute "
                       "{1}: either the target transformations (root, tip) were not found "
                       "or the input values are not valid matrices"
                       ".".format(info, attribute))

    return True, list()


def set_sim_mesh_list_attribute(attribute, value, attribute_type):
    """Sets the values to sim mesh list attributes including the input connection
    to the matrix plug, and the input connection to the mesh plug.

    Args:
        attribute (str): full name of the attribute to set with format
            "node_name.attribute_name".
        value (list): attribute value to set. Each item in the list is a
            dictionary with 2 entries: matrix (name of the input matrix
            object to connect or matrix values) and mesh (name of the input
            mesh object to connect).
        attribute_type (str): descriptor of the attribute type. Not used in
            this implementation, required to keep consistency in
            `importer.set_attribute_definition`.
            
    Example of input `value`:
    [
        {
            "matrix": "referenceObject.simWorldMatrix[0]",
            "mesh": "referenceObject.simWorldMesh[0]",
        }
        ...
    ]

    Returns:
        bool: True if the attribute was properly set. False otherwise.
        str: additional information only in case of error.
    """
    meshes_not_attached = list()
    idx = 0
    for attachment in value:
        # Matrix and mesh
        matrix = attachment["matrix"]
        mesh = attachment["mesh"]
        matrix_attached = True
        mesh_attached = True

        matrix_attribute = "{0}[{1}].simWorldMatrix".format(attribute, idx)
        mesh_attribute = "{0}[{1}].simWorldMesh".format(attribute, idx)
        # String values from a json load in Python 2 return unicode
        if sys.version_info[0] < 3 and type(matrix) is unicode:
            matrix = str(matrix)
        # String values from a json load in Python 2 return unicode
        if sys.version_info[0] < 3 and type(mesh) is unicode:
            mesh = str(mesh)

        # The matrix value is the name of a node
        if type(matrix) is str and cmds.objExists(matrix):
            # Connect matrix
            disconnect_attribute_from_source(matrix_attribute)
            cmds.connectAttr(matrix, matrix_attribute, force=True)
        # The matrix value is a matrix
        elif type(matrix) is not str:
            cmds.setAttr(matrix_attribute, matrix, type="matrix")
        # Unrecognized value
        else:
            matrix_attached = False
        
        # The mesh value is the name of a node
        if type(mesh) is str and cmds.objExists(mesh):
            # Connect mesh
            disconnect_attribute_from_source(mesh_attribute)
            cmds.connectAttr(mesh, mesh_attribute, force=True)
        # Unrecognized value
        else:
            mesh_attached = False

        if not matrix_attached or not mesh_attached:
            meshes_not_attached.append(idx)

        # Next slot
        idx += 1

    if meshes_not_attached:
        info = ",".join([str(i) for i in meshes_not_attached])
        return False, ("Could not configure simulation mesh list ({0}) to attribute {1}: "
                       "either the target mesh was not found or the input matrix is not valid."
                       ".".format(info, attribute))

    return True, list()


def set_anim_mesh_list_attribute(attribute, value, attribute_type):
    """Sets the values to anim mesh list attributes including the input connection
    to the matrix plug, and the input connection to the mesh plug.

    Args:
        attribute (str): full name of the attribute to set with format
            "node_name.attribute_name".
        value (list): attribute value to set. Each item in the list is a
            dictionary with 2 entries: matrix (name of the input matrix
            object to connect or matrix values) and mesh (name of the input
            mesh object to connect).
        attribute_type (str): descriptor of the attribute type. Not used in
            this implementation, required to keep consistency in
            `importer.set_attribute_definition`.
            
    Example of input `value`:
    [
        {
            "matrix": "referenceObject.animWorldMatrix[0]",
            "mesh": "referenceObject.animWorldMesh[0]",
        }
        ...
    ]

    Returns:
        bool: True if the attribute was properly set. False otherwise.
        str: additional information only in case of error.
    """
    meshes_not_attached = list()
    idx = 0
    for attachment in value:
        # Matrix and mesh
        matrix = attachment["matrix"]
        mesh = attachment["mesh"]
        matrix_attached = True
        mesh_attached = True

        matrix_attribute = "{0}[{1}].animWorldMatrix".format(attribute, idx)
        mesh_attribute = "{0}[{1}].animWorldMesh".format(attribute, idx)
        # String values from a json load in Python 2 return unicode
        if sys.version_info[0] < 3 and type(matrix) is unicode:
            matrix = str(matrix)
        # String values from a json load in Python 2 return unicode
        if sys.version_info[0] < 3 and type(mesh) is unicode:
            mesh = str(mesh)

        # The matrix value is the name of a node
        if type(matrix) is str and cmds.objExists(matrix):
            # Connect matrix
            disconnect_attribute_from_source(matrix_attribute)
            cmds.connectAttr(matrix, matrix_attribute, force=True)
        # The matrix value is a matrix
        elif type(matrix) is not str:
            cmds.setAttr(matrix_attribute, matrix, type="matrix")
        # Unrecognized value
        else:
            matrix_attached = False
        
        # The mesh value is the name of a node
        if type(mesh) is str and cmds.objExists(mesh):
            # Connect mesh
            disconnect_attribute_from_source(mesh_attribute)
            cmds.connectAttr(mesh, mesh_attribute, force=True)
        # Unrecognized value
        else:
            mesh_attached = False

        if not matrix_attached or not mesh_attached:
            meshes_not_attached.append(idx)

        # Next slot
        idx += 1

    if meshes_not_attached:
        info = ",".join([str(i) for i in meshes_not_attached])
        return False, ("Could not configure animation mesh list ({0}) to attribute {1}: "
                       "either the target mesh was not found or the input matrix is not valid."
                       ".".format(info, attribute))

    return True, list()


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
