import re

import maya.cmds as cmds
import maya.mel as mel


def play_interactive():
    """Starts the playback in interactive."""
    mel.eval("InteractivePlayback")


def get_selection(flatten=False, long_path=True):
    """Gets the current selection from the scene.

    Args:
        flatten (bool, optional): flattens the output list so that each item
            is identified individually. Defaults to False.
        long_path (bool, optional): provides the long format of the name (full path).
            Defaults to True.

    Returns:
        list: list of selected objects.
    """
    return cmds.ls(selection=True, flatten=flatten, long=long_path)


def clear_selection():
    """Clears the selection in the scene."""
    cmds.select(clear=True)


def select(obj):
    """Select the given object(s) in the scene, replacing the active list.

    Args:
        obj (str or list): name of the object or objects.

    Returns:
        str or list: list of objects selected.
    """
    return cmds.select(obj)


def nice_name(obj):
    """Gets the shortest nice name of the given object(s) in the scene.

    Args:
        obj (str or list): name of the object or objects.

    Returns:
        str or list: name or names in nice format of the input object(s).
    """
    if type(obj) is list:
        return cmds.ls(obj, long=False)
    return cmds.ls(obj, long=False)[0]


def is_mesh(object_path, long_path=True):
    """Checks if the input object is a mesh.

    Args:
        object_path (str): input path to he object that will be checked to be a mesh.
        long_path (bool, optional): provides the long format of the name (full path).
            Defaults to True.

    Returns:
        bool: wether the object is a mesh or not.
    """
    if cmds.nodeType(object_path) == 'mesh':
        return True
    children = cmds.listRelatives(object_path, shapes=True, fullPath=long_path) or []
    if children:
        return cmds.nodeType(children[0]) == 'mesh'
    return False


def get_num_vertices(object_path, long_path=True):
    """Get the number of vertices from an object.

    Args:
        object_path (str): input to the object containing geometry information.
        long_path (bool, optional): Use the long format of the name.
            Defaults to True.

    Returns:
        int: the number of vertices of the object.
    """
    try:
        vertex_count = cmds.polyEvaluate(object_path).get('vertex')
        if vertex_count:
            return vertex_count
        children = cmds.listRelatives(object_path, shapes=True, fullPath=long_path) or []
        if children:
            return cmds.polyEvaluate(children[0])['vertex']
        return 0
    except:
        return 0


def exists(object_path):
    """Checks if the object is in the scene.

    Args:
        object_path (str): input path to the object to check if present in scene.

    Returns:
        bool: if the object is in the scene.
    """
    return cmds.objExists(object_path)


def get_available_name(name, ignore_list=None):
    """Get the next available name in the scene based on the addition of
    digits at the end to ensure that the resulting name is unique.

    Args:
        name (str): base name that can be already present in scene.
        ignore_list (list, optional): List of names that should be ignored.
            Defaults to an empty list.

    Returns:
        str: resulting unique name in the scene.
    """
    ignore_list = ignore_list if ignore_list is not None else list()
    base_name = name
    regular_expression = re.compile(".*[^0-9]").match(name)
    if regular_expression:
        base_name = regular_expression.group(0)

    numeric_suffix = 1
    unique_name = base_name + str(numeric_suffix)
    while cmds.objExists(unique_name) or unique_name in ignore_list:
        numeric_suffix += 1
        unique_name = base_name + str(numeric_suffix)

    return unique_name


def list_relatives(node, filter_type=None):
    """Retrieves all children in the descendant hierarchy of the given node.
    If a `filter_type` is provided, then only the children with that type
    will be returned.

    Args:
        node (str): long name of the parent node to the query.
        filter_type (str, optional): type identifier to filter the query.
            Defaults to None.

    Returns:
        list: list with long names of the children found.
        list: list with short names of the children found.
    """
    if filter_type and filter_type in cmds.ls(nodeTypes=True):
        long_names = cmds.listRelatives(node,
                                        fullPath=True,
                                        allDescendents=True,
                                        type=filter_type) or []
        short_names = cmds.listRelatives(node,
                                         fullPath=False,
                                         allDescendents=True,
                                         type=filter_type) or []
    else:
        long_names = cmds.listRelatives(node,
                                        fullPath=True,
                                        allDescendents=True) or []
        short_names = cmds.listRelatives(node,
                                         fullPath=False,
                                         allDescendents=True) or []

    return long_names, short_names


def get_current_time():
    """Returns the current time in a Maya scene.

    Returns:
        int: current time of current scene.
    """
    return cmds.currentTime(query=True)
