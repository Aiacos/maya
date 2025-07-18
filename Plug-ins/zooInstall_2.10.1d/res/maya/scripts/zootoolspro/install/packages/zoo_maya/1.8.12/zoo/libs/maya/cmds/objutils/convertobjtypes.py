"""
from zoo.libs.maya.cmds.objutils import convertobjtypes
convertobjtypes.convertSelectedGroupsToLocators()

from zoo.libs.maya.cmds.objutils import convertobjtypes
convertobjtypes.convertAllGroupsToLocators()

from zoo.libs.maya.cmds.objutils import convertobjtypes
convertobjtypes.convertSelHiGroupsToLocators()

"""

import maya.cmds as cmds


def convertGroupToLocator(groupName):
    """Convert the specified group into a locator by parenting a locator shape
    under it and preserving the group's transform.

    :param groupName: The name of the group to convert.
    :type groupName: str
    :return: The name of the newly created locator shape node.
    :rtype: str
    """
    tempLoc = cmds.spaceLocator(name='tempLocator')[0]
    tempLocShape = cmds.listRelatives(tempLoc, shapes=True)[0]  # long name??

    # get the local pivot value of the group as it may have been moved and set the offset on the locator
    pivOffset = cmds.getAttr("{}.rotatePivot".format(groupName))[0]
    cmds.setAttr("{}.localPosition".format(tempLocShape), pivOffset[0], pivOffset[1], pivOffset[2], type="double3")

    # Parent the locator shape to the group.
    cmds.parent(tempLocShape, groupName, r=True, s=True)

    # Delete the original locator transform node and rename the shape node
    cmds.delete(tempLoc)
    newShapeName = cmds.rename('|'.join([groupName, tempLocShape]), "{}Shape".format(groupName))
    return newShapeName


def convertSelectedGroupsToLocators():
    """
    Loops through all selected transforms that have no shape nodes (i.e., empty groups)
    and converts each one into a locator.

    :return: The newly created locator shape nodes.
    :rtype: list(str)
    """
    newShapeNodes = []
    # Get all selected transforms
    selectedTransforms = cmds.ls(sl=True, type='transform') or []

    if not selectedTransforms:
        return

    # Filter only those that have no shape (empty groups)
    emptyGroups = [x for x in selectedTransforms if not cmds.listRelatives(x, shapes=True)]

    if not emptyGroups:
        return

    # Convert each group into a locator
    for grp in emptyGroups:
        shapeNode = convertGroupToLocator(grp)
        newShapeNodes.append(shapeNode)
    return newShapeNodes


def find_all_groups():
    """Returns a list of transform nodes that have no shape children.
    In Maya, these are often used as 'group' nodes.

    :return: A list of group nodes.
    """
    groups = []
    all_transforms = cmds.ls(type='transform')
    if not all_transforms:
        return []
    for node in all_transforms:
        shapes = cmds.listRelatives(node, shapes=True, path=True)
        if not shapes:
            groups.append(node)
    return groups


def convertAllGroupsToLocators():
    """
    Convert all groups in the scene to locators.
    :return: A tuple containing the original group nodes and the newly created locator shape nodes.
    :rtype: tuple(list(str), list(str))
    """
    newShapeNodes = []
    allGrps = find_all_groups()
    if not allGrps:
        return [], []
    for grp in allGrps:
        shapeNode = convertGroupToLocator(grp)
        newShapeNodes.append(shapeNode)
    return allGrps, newShapeNodes


def find_groups_under_selection():
    """
    Find all transform nodes that have no shape children (i.e., 'groups'),
    within the hierarchy of the currently selected objects.

    Returns a list of the full path names of those group nodes.

    :return: A list of group nodes under the selection.
    :rtype: list(str)
    """
    selected_transforms = cmds.ls(sl=True, type='transform', l=True) or []

    if not selected_transforms:
        return []

    descendants = cmds.listRelatives(selected_transforms, ad=True, type='transform', f=True) or []

    # Combine the selected transforms + their descendants, ensuring no duplicates
    all_in_hierarchy = list(set(selected_transforms + descendants))

    # Now check each transform for whether it has shape children
    groups = []
    for node in all_in_hierarchy:
        # List shape children under the transform
        shapes = cmds.listRelatives(node, shapes=True, f=True)

        # If there are no shapes, this transform acts as a "group"
        if not shapes:
            groups.append(node)

    return groups


def convertSelHiGroupsToLocators():
    """
    Convert all groups under the selected hierarchy to locators.
    :return: A tuple containing the original group nodes and the newly created locator shape nodes.
    :rtype: tuple(list(str), list(str))
    """
    newShapeNodes = []
    allGrps = find_groups_under_selection()
    if not allGrps:
        return [], []

    for grp in allGrps:
        shapeNode = convertGroupToLocator(grp)
        newShapeNodes.append(shapeNode)

    return allGrps, newShapeNodes
