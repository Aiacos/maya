import copy

import maya.cmds as cmds
import maya.OpenMaya as OpenMaya

import adn.tools.maya.attribute_handlers as attr_handler
from adn.commands.maya import scene
from adn.utils.constants import UiConstants, AssetDefinition
from adn.utils.constants import AssetDefinitionImportStatusCode as STATUS
from adn.utils.maya.asset_definition_helpers import MayaAssetDefinition


def search_for_matching_node(asset_definition, mesh):
    """Processes the content of AdonisFX Asset Definition searching for nodes
    that are assigned to the provided mesh. If a node in the definition was
    assigned to the given mesh, then the long and short names of that node
    are returned.

    Args:
        asset_definition (dict): data dict with an AdonisFX Asset Definition.
        mesh (str): name of the mesh to drive the search.

    Returns:
        str: long name of the matching node. If not found, None.
        str: short name of the matching node. If not found, None.
    """
    matching = None
    matching_long_name = None

    # Iterate over the assets in the definition
    for asset_data in asset_definition["assets"]:
        # Iterate over the nodes in the current asset
        for node_data in asset_data["data"]:
            node_type = node_data["__type__"]
            if node_type not in AssetDefinition.NODE_TYPES:
                continue
            if mesh not in node_data["__mesh_name__"]:
                continue
            # Matching node found
            matching = node_data["__name__"]
            matching_long_name = node_data["__full_name__"]
            # No need to iterate further: there is only one possible matching
            break
        if matching:
            # No need to iterate further: there is only one possible matching
            break
    return matching, matching_long_name


def get_name_based_on_hierarchy(name, mesh, ignore_name_list=None):
    """Returns a suitable node name for the mesh and node name sent.

    Args:
        name (str): Node name proposed by the user.
        mesh (str): The final node will belong to this mesh hierarchy.
        ignore_name_list (list, optional): List of names that should
            be ignored. Defaults to an empty list.

    Returns:
      str: In case the node name is not found, will return that name.
      str: If the node name exists, checks if it belongs to the mesh hierarchy.
           If it does returns that name.
      str: If the node name exists, checks if it belongs to the mesh hierarchy.
           If it does not, generates a new node name.
    """
    if not cmds.objExists(name):
        # Node not found in scene.
        return name

    node_history = list(cmds.listHistory(mesh))
    nodes = [x for x in node_history if cmds.objExists(x) and
             cmds.nodeType(x) in AssetDefinition.NODE_TYPES]

    if name in nodes:
        # Node found in hierarchy will update that node.
        return name
    else:
        # Node not found in hierarchy will generate a new name.
        return scene.get_available_name(name, ignore_name_list)


def is_ready_to_import(asset_definition):
    """Checks if the Asset Definition provided is valid to complete an import
    process. The validation checks that every mesh added as destination to
    a node does exist in the scene.

    Args:
        asset_definition (dict): data dict with an AdonisFX Asset Definition.

    Returns:
        bool: result of validation (True if success, False otherwise).
        str: message describing the error found (if any, else it is None).
    """
    if len(asset_definition["assets"]) == 0:
        return False, "Mesh list is emtpy. Nothing to import."

    # Check destination meshes do exist in the scene
    for asset_data in asset_definition["assets"]:
        if len(asset_data["data"]) == 0:
            return False, "There are no candidate nodes assigned. Nothing to import."
        for node_to_import in asset_data["data"]:
            mesh = node_to_import["__mesh_name__"]
            if not scene.exists(mesh):
                return False, "Mesh not found in the scene: {0}".format(mesh)

    return True, None


def set_attribute_definition(node, node_type, attribute, value):
    """Configures the value(s) input attribute in the input node. It is a
    generic method that retrieves the proper setter command from
    `MayaAssetDefinition` class based on the name and type of the given
    attribute.

    Args:
        node (str): name of the node that owns the attribute.
        node_type (str): name of the node type.
        attribute (str): name of the attribute to set.
        value (object): value to set. It can be a list, bool, integer, float,
            etc. depending on the type of the attribute

    Returns:
        :obj:`AssetDefinitionImportStatusCode`: return code to determine the
            success of the import process, where 0 is success, 1 is partial
            success with warnings, and 2 is error).
        str: extra information if an error occurred.
    """
    if attribute in MayaAssetDefinition.ATTR_IGNORE_LIST[node_type]:
        return STATUS.SUCCESS, ""

    attribute_full_name = "{0}.{1}".format(node, attribute)
    if not cmds.objExists(attribute_full_name):
        log = ("Could not find attribute {0} in node "
               "{1} ({2})".format(attribute, node, node_type))
        return STATUS.WARNING, log

    attribute_type = cmds.getAttr(attribute_full_name, type=True)

    # Find a valid set command to this attribute
    # First search command by attr name, if not found then by attr type
    # and if not found then try with the default one
    set_command = MayaAssetDefinition.ATTR_SET_COMMANDS.get(attribute)
    if not set_command:
        set_command = MayaAssetDefinition.ATTR_SET_COMMANDS.get(attribute_type)
    if not set_command:
        set_command = attr_handler.set_plain_attribute

    # Attempt to set attribute
    success, log = set_command(attribute_full_name, value, attribute_type)
    return_code = STATUS.SUCCESS if success else STATUS.WARNING
    return return_code, log


def set_node_definition(node_definition):
    """Attempts to apply the node definition provided. This method searches
    for the destination mesh in the scene and attempts to configure a node
    with the input definition. If the mesh has already a node assigned with
    the same type of the input node, then this method attempts to modify the
    configuration (does not create a duplicate).

    Args:
        node_definition (dict): data dict with the definition of an AdonisFX node.

    Returns:
        :obj:`AssetDefinitionImportStatusCode`: return code to determine the
            success of the import process, where 0 is success, 1 is partial
            success with warnings, and 2 is error).
        list: list of messages with information of the import result.
    """
    return_code = STATUS.SUCCESS
    log = list()

    node_name = node_definition["__full_name__"]
    node_type = node_definition["__type__"]
    mesh_name = node_definition["__mesh_name__"]
    mesh_vertices = node_definition["__num_vertices__"]
    mesh_polygons = node_definition["__num_poly__"]

    # Mesh not found
    if not cmds.objExists(mesh_name):
        log.append("Could not import node {0} onto the mesh {1}: mesh "
                   "not found".format(node_name, mesh_name))
        return STATUS.CRITICAL, log
    # Multiple meshes in the scene with that name (should not happen as we
    # use full paths on export)
    if len(cmds.ls(mesh_name)) > 1:
        log.append("Could not import node {0} onto the mesh {1}: more than "
                   "one mesh occurrence found".format(node_name, mesh_name))
        return STATUS.CRITICAL, log

    selection_list = OpenMaya.MSelectionList()
    selection_list.add(mesh_name)
    node_dag_path = OpenMaya.MDagPath()
    selection_list.getDagPath(0, node_dag_path)
    mesh_fn = OpenMaya.MFnMesh(node_dag_path)
    # Unexpected num vertices
    if mesh_fn.numVertices() != mesh_vertices:
        log.append(
            "Could not import node {0} onto the mesh {1}: mesh has {2} "
            "vertices, expected {3}".format(
                node_name, mesh_name,
                mesh_fn.numVertices(), mesh_vertices))
        return STATUS.CRITICAL, log
    # Unexpected number of polygons
    if mesh_fn.numPolygons() != mesh_polygons:
        log.append(
            "Could not import node {0} onto the mesh {1}: mesh has {2} "
            "polygons, expected {3}".format(
                node_name, mesh_name,
                mesh_fn.numPolygons(), mesh_polygons))
        return STATUS.CRITICAL, log

    # Find node or create a new one
    node_history = list(cmds.listHistory(mesh_name))
    existing_nodes = [x for x in node_history
                      if cmds.nodeType(x) == node_type] or None
    if not existing_nodes:
        # Check if the minimum requirements are provided
        check_succeeded, error_message = \
            MayaAssetDefinition.NODE_CREATOR_CHECK[node_type](node_definition["data"])
        if not check_succeeded:
            log.append(
                "Could not import '{0}' ({1}): {2}" \
                "".format(node_name, node_type, error_message))
            return STATUS.CRITICAL, log

        # Node not found create a new node
        node = MayaAssetDefinition.NODE_CREATOR[node_type](
            mesh_name,
            node_name)
    else:
        node = existing_nodes[0]

    for attribute, value in node_definition["data"].items():
        if value is None:
            # Null values don't need to be imported
            # This is the case when optional input objects were not
            # configured (i.e. restMesh in AdnSimshape)
            continue
        attr_result, attr_log = set_attribute_definition(node,
                                                         node_type,
                                                         attribute,
                                                         value)
        if attr_log or attr_result != STATUS.SUCCESS:
            return_code = max([return_code, attr_result])
            log.append(attr_log)

    return return_code, log


def import_asset_definition(asset_definition):
    """Main import method. Given an Asset Definition to import, this method
    iterates over the list of node assignments of each asset and attempts to
    create and configure the nodes in the current scene.

    Args:
        asset_definition (dict): data dict with an AdonisFX Asset Definition.

    Returns:
        :obj:`AssetDefinitionImportStatusCode`: return code to determine the
            success of the import process, where 0 is success, 1 is partial
            success with warnings, and 2 is error).
        list: list of messages with information of the import result.
    """
    full_log = list()
    full_return_code = list()
    for asset_data in asset_definition["assets"]:
        for node_data in asset_data["data"]:
            node_type = node_data["__type__"]
            if node_type not in AssetDefinition.NODE_TYPES:
                continue

            result, log = set_node_definition(node_data)
            full_return_code.append(result)
            full_log.extend(log)

    for log in full_log:
        print("{0}: {1}".format(UiConstants.LOG_PREFIX, log))

    return max(full_return_code)
