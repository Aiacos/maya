import os
import copy
import json

from adn.utils.constants import AssetDefinition


def load_asset_definition_file(input_file):
    """Attempts to load an AdonisFX Asset Definition as dictionary from the
    provided input file.

    Args:
        input_file (str): full path to JSON file.

    Returns:
        bool: True if the given path is a valid json file with AdonisFX Asset
            Definition, False otherwise.
        dict: data dictionary with an AdonisFX Asset Definition. None if the
            file is not valid.
    """
    if not input_file or not os.path.exists(input_file):
        return False, None

    file_obj = open(input_file)
    try:
        asset_definition_dict = json.load(file_obj)
    except:
        return False, None

    if not check_asset_definition_dict(asset_definition_dict):
        return False, None

    return True, asset_definition_dict


def check_asset_definition_dict(asset_definition_dict):
    """Check if the content of the input dictionary matches the structure of
    AdonisFX Asset Definition template. The matching criteria is based only on
    the dictionary keys at the first level.

    Args:
    asset_definition_dict (dict): dictionary to compare with the AdonisFX
        Asset Definition template.

    Structure of `AssetDefinition.TEMPLATE`:
        {
            "__version__"   : None,
            "__dcc__"       : {"name": None},
            "assets"        : list()
        }

    Returns:
        bool: True if the input dictionary is a valid Asset Definition, False
            otherwise.
    """
    template = copy.deepcopy(AssetDefinition.TEMPLATE)
    for key in template.keys():
        if key not in asset_definition_dict.keys():
            return False
    return True


def get_nodes_info_from_asset_definition(asset_definition):
    """Retrieves relevant information from all nodes existing in the input
    AdonisFX Asset Definition. The information is constructed as a list of nodes
    info where each item contains the nice name of the node, the full name of
    the node, the node type and the mesh that the node was assigned to (in
    that order).

    Args:
        asset_definition (dict): data dict with an AdonisFX Asset Definition.

    Returns:
        list: list of tuples with node names, full names, types and mesh assigned.
    """
    nodes_info = list()
    for asset_data in asset_definition["assets"]:
        for node_data in asset_data["data"]:
            node_type = node_data["__type__"]
            if node_type not in AssetDefinition.NODE_TYPES:
                continue
            node_info = (
                node_data["__name__"],
                node_data["__full_name__"],
                node_data["__type__"],
                node_data["__mesh_name__"]
            )
            nodes_info.append(node_info)
    return nodes_info
