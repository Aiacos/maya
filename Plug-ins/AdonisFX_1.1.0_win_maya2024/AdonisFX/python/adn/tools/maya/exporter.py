import json
import copy

import maya.cmds as cmds
import maya.OpenMaya as OpenMaya

import adn.tools.maya.attribute_handlers as attr_handler
from adn.utils.constants import UiConstants
from adn.utils.constants import AssetDefinition
from adn.utils.maya.asset_definition_helpers import MayaAssetDefinition


def extract_relevant_nodes(obj):
    """Collects AdonisFX nodes info connected to the given object.

    Args:
        obj (str): name of the object to traverse the history of to search
            for relevant nodes connected.

    Returns:
        dict: dictionary to extend with relevant nodes found in
            the hierarchy of the given object.
    """
    relevant_nodes = dict()
    shape_nodes = cmds.listRelatives(obj,
                                     fullPath=True,
                                     allDescendents=True,
                                     type="mesh")
    if not shape_nodes:
        return

    for shape in shape_nodes:
        node_history = cmds.listHistory(shape)
        nodes = [x for x in node_history
                 if cmds.nodeType(x) in AssetDefinition.NODE_TYPES]
        if not nodes:
            continue
        for node in nodes:
            node_type = cmds.nodeType(node)
            if node_type not in relevant_nodes:
                relevant_nodes[node_type] = list()
            if node in relevant_nodes[node_type]:
                continue
            relevant_nodes[node_type].append(node)
    return relevant_nodes


def extract_map_attributes(node, node_type):
    """Returns all attributes of type considered maps which
    do not require special treatment from the given node and type.

    Args:
        node (str): name of the node for the extraction.
        node_type (str): type of the node for the extraction.

    Returns:
        list: list of names of map attributes.
    """
    paintable_attributes = list()
    methods_keys = MayaAssetDefinition.ATTR_GET_COMMANDS.keys()

    for attribute in cmds.listAttr(node):
        if attribute in MayaAssetDefinition.ATTR_IGNORE_LIST[node_type]:
            continue
        if not cmds.attributeQuery(attribute, node=node, exists=True, typeExact=node_type):
            continue
        # Attribute requires specific treatment, not based on its type
        if attribute in methods_keys:
            continue
        node_attribute = "{0}.{1}".format(node, attribute)
        if not cmds.objExists(node_attribute):
            continue
        if cmds.getAttr(node_attribute, type=True) != "TdataCompound":
            continue

        paintable_attributes.append(cmds.attributeName(node_attribute, nice=True))

    return paintable_attributes


def is_allowed_to_export(features_enabled_in_ui, node, attribute, attribute_type=None):
    """Checks if the provided attribute is allowed for the export process.
    The check is based in two conditions (A and B must be True):
        A) This attribute is supported by the exporter of this DCC in
        asset_definition_helpers.
        B) This attribute (or the feature type containing this attribute) is
        enabled by the user in the UI.

    Args:
        features_enabled_in_ui (dict): dictionary with features selected by
            the user to be exported, at node level.
        node (str): node of the attribute.
        attribute (str): potential attribute to be exported.
        attribute_type (str, optional): type of the candidate attribute to
            be exported. Defaults to None.

    Returns:
        bool: True if the attribute should be exported, False otherwise.
    """
    # Check if the attribute should be exported based on the attribute not the type
    if not attribute_type:
        key_export_features = MayaAssetDefinition.ATTR_EXPORT_FEATURES_REMAP.get(
            attribute, MayaAssetDefinition.ATTR_EXPORT_FEATURES_REMAP_DEFAULT)
        if key_export_features in features_enabled_in_ui:
            # Attribute found, see export status
            return features_enabled_in_ui[key_export_features]
    # Check if the attribute should be exported based on the attribute type
    else:
        key_export_features = MayaAssetDefinition.ATTR_EXPORT_FEATURES_REMAP.get(
            attribute_type, MayaAssetDefinition.ATTR_EXPORT_FEATURES_REMAP_DEFAULT)
        if key_export_features == "Maps":
            # If attribute type was "Map" see if that exact map should be exported
            node_attribute = "{0}.{1}".format(node, attribute)
            return features_enabled_in_ui[cmds.attributeName(node_attribute, nice=True)]
        if key_export_features in features_enabled_in_ui:
            # Attribute type found, see export status
            return features_enabled_in_ui[key_export_features]

    return False


def get_node_definition(features_enabled_in_ui, node_type, node, mesh_node):
    """Returns the Asset Definition of a node connected to a mesh.
    The returned dictionary will include mesh info and the node
    attributes configuration.

    Args:
        features_enabled_in_ui (dict): dictionary with features selected by
            the user in the ui to be exported.
        node_type: type of the node to export.
        node (str): name of the node to export.
        mesh_node (str): mesh node associated to the node to export.

    Returns:
        dict: dictionary with the AdonisFX Asset Definition associated to the
            node given as input.
    """
    if not node or not mesh_node:
        return dict()

    node_data = copy.deepcopy(AssetDefinition.DEFORMER_DATA_TEMPLATE)

    # Private DATA
    node_data["__type__"] = node_type
    node_data["__name__"] = node.split(":")[-1]
    node_data["__full_name__"] = node
    node_data["__mesh_name__"] = mesh_node
    selection_list = OpenMaya.MSelectionList()
    selection_list.add(mesh_node)
    node_dag_path = OpenMaya.MDagPath()
    selection_list.getDagPath(0, node_dag_path)
    mesh_fn = OpenMaya.MFnMesh(node_dag_path)

    node_data["__num_vertices__"] = mesh_fn.numVertices()
    node_data["__num_poly__"] = mesh_fn.numPolygons()

    # Node specific attributes
    methods_keys = MayaAssetDefinition.ATTR_GET_COMMANDS.keys()

    # Get all attributes in this node
    filtered_attributes = cmds.listAttr(node)
    # Remove all attributes not defined by this specific AdonisFX node
    # This is to remove inherited attributes
    filtered_attributes = [
        attr for attr in filtered_attributes
        if cmds.attributeQuery(attr, node=node, exists=True, typeExact=node_type)]
    # Remove all attributes marked to ignore
    filtered_attributes = [
        attr for attr in filtered_attributes
        if attr not in MayaAssetDefinition.ATTR_IGNORE_LIST[node_type]]
    # Add only the attributes from inheritance that are supported
    filtered_attributes.extend(MayaAssetDefinition.DEFORMER_NODE_ATTRIBUTES)

    # Iterate over all filtered attributes
    for attribute in filtered_attributes:
        node_attribute = "{0}.{1}".format(node, attribute)
        if not cmds.objExists(node_attribute):
            continue

        # Read attributes that requires specific treatment,
        # not based on its type but on a predefined getter method
        if attribute in methods_keys:
            if not is_allowed_to_export(features_enabled_in_ui, node, attribute):
                continue
            get_command = MayaAssetDefinition.ATTR_GET_COMMANDS.get(attribute)
            if not get_command:
                get_command = attr_handler.get_plain_attribute
            attribute_value = get_command(node_attribute)
            node_data["data"][attribute] = attribute_value
        # Read attributes based on its type
        else:
            attribute_type = cmds.getAttr(node_attribute, type=True)
            if not is_allowed_to_export(features_enabled_in_ui, node,
                                        attribute, attribute_type):
                continue
            get_command = MayaAssetDefinition.ATTR_GET_COMMANDS.get(attribute_type)
            if not get_command:
                get_command = attr_handler.get_plain_attribute
            attribute_value = get_command(node_attribute)
            node_data["data"][attribute] = attribute_value

    return node_data


def get_asset_definition(asset_data, features_enabled_in_ui):
    """Method to collect and extract all supported nodes to export
    from the list of objects provided. For each node, it will extract
    the attributes configuration.

    Args:
        asset_data (dict): output dictionary to store the Asset Definition data.
        features_enabled_in_ui (dict): dictionary with features selected by
            the user in the ui to be exported.
    """
    nodes_to_export = features_enabled_in_ui.keys()
    for node in nodes_to_export:
        if not features_enabled_in_ui[node]["node"]:
            # Not selected to export
            continue

        # Export is limited to deformers whose output is connected to one single shape.
        shapes = cmds.deformer(node, query=True, geometry=True) or []
        if len(shapes) != 1:
            print("{0} Failed to get definition of '{1}' node. Export of a "
                  "deformer connected to none or more than one shape is not "
                  "supported.".format(UiConstants.LOG_PREFIX, node))
            continue

        shape = cmds.ls(shapes[0], long=True)[0]
        node_type = cmds.nodeType(node)
        data = get_node_definition(features_enabled_in_ui[node],
                                   node_type,
                                   node,
                                   shape)
        if data:
            asset_data["data"].append(data)
        else:
            print("{0} Failed to get definition of '{1}' node."
                  "".format(UiConstants.LOG_PREFIX, node))


def is_attribute_invalid(attribute):
    """Checks recursively if the attribute is empty or None.

    Args:
        attribute: attribute from asset that is going to be exported.

    Returns:
        bool: True if the attribute had invalid data, False otherwise.
    """
    data_type = type(attribute)
    if data_type in [tuple, list, set, dict]:
        # Complex attributes
        return all(is_attribute_invalid(item) for item in attribute)
    elif attribute is None:
        # Simple data
        return True
    return False


def asset_data_is_empty(asset_data):
    """Checks if the asset sent has at least one feature with valid data.

    Args:
        asset_data (dict): Asset Definition data dictionary about to be exported to a file.

    Returns:
        bool: True if the asset has valid content, False if it is empty.
    """
    for mesh in asset_data:
        for data_element in mesh["data"]:
            attribute = mesh["data"][data_element]
            if not is_attribute_invalid(attribute):
                return False
    return True


def export_asset_definition(export_assets, destination_file):
    """Main export method. Given an asset to export, this method collects and
    exports the AdonisFX Asset Definition data into a json file at the given
    destination.

    Args:
        export_assets (dict): dictionary with all the assets, nodes and
            features to export.
        destination_file (str): full path to the output destination file.

    Returns:
        bool: True if Asset Definition exported successfully, False otherwise.
    """
    aad_data = copy.deepcopy(AssetDefinition.TEMPLATE)

    # Private data
    aad_data["__version__"] = cmds.pluginInfo(UiConstants.PLUGIN_NAME,
                                              query=True,
                                              version=True)
    aad_data["__dcc__"]["name"] = "maya"

    num_assets = len(export_assets.keys())
    aad_data["assets"] = [copy.deepcopy(AssetDefinition.ASSET_TEMPLATE)] * num_assets

    minimum_valid_data_to_export = False
    something_went_wrong = False
    for idx, asset_nice_name in enumerate(export_assets.keys()):
        export_data = export_assets[asset_nice_name]
        asset = cmds.ls(asset_nice_name, long=True)[0]
        # Private data
        aad_data["assets"][idx]["__asset__"] = asset_nice_name
        aad_data["assets"][idx]["__asset_path__"] = asset

        # Get all nodes configuration for this asset
        get_asset_definition(aad_data["assets"][idx], export_data)

        # If data is empty, something went wrong
        if not aad_data["assets"][idx]["data"]:
            print("{0} Failed to get AdonisFX Asset Definition for '{1}': "
                  "nothing found or selected to export."
                  "".format(UiConstants.LOG_PREFIX, asset_nice_name))
            something_went_wrong = True
            continue

        # Check if at least one feature is exported from the asset
        if asset_data_is_empty(aad_data["assets"][idx]["data"]):
            print("{0} Failed to get AdonisFX Asset Definition for '{1}': "
                  "data selected to export is not initialized or empty. "
                  "".format(UiConstants.LOG_PREFIX, asset_nice_name))
            something_went_wrong = True
            continue

        minimum_valid_data_to_export = True

    if not minimum_valid_data_to_export:
        return not something_went_wrong

    with open(destination_file, "w") as file_stream:
        json.dump(aad_data, file_stream)
        file_stream.close()

    return not something_went_wrong
