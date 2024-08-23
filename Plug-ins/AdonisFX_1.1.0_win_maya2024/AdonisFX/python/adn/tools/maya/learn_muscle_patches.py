import math
import copy

import maya.cmds as cmds

from adn.utils.constants import UiConstants
from adn.ui.widgets.dialogs import msg_box


def learn_muscle_patches(destination_file, mesh, targets, vertices, num_muscle_patches,
                         draw=False, max_iterations=0):
    """Calls AdnLearnMusclePatches command with the given arguments 
       to run the algorithm for the muscle patches calculation.

    Args:
        destination_file (str): full path for the output .amp file.
        mesh (str): name of the neutral mesh.
        targets (list): list of names of the target meshes.
        vertices (list): list of vertices to process in the training.
        num_muscle_patches (int): number of muscle patches to generate by the muscle patches 
                                  calculation algorithm.
        draw (bool, optional): flag to enable drawing of output muscle patches by coloring vertices 
                               of the neutral mesh. Defaults to False.
        max_iterations (int, optional): number of maximum iterations for the muscle 
                                        patches algorithm. Defaults to 0.
    """
    cmds.AdnLearnMusclePatches(outputPath=destination_file,
                               neutralMesh=mesh,
                               targetMeshes=targets,
                               verticesMask=vertices,
                               numMuscles=num_muscle_patches,
                               drawMuscles=draw,
                               maxIterations=max_iterations)
    if draw:
        selected = cmds.ls(mesh, long=True, dag=True, objectsOnly=True, shapes=True)
        if selected:
            selected = selected[0]
            cmds.sets(selected, edit=True, forceElement="initialShadingGroup")
            cmds.polyColorPerVertex(selected, colorDisplayOption=True)


def generate_targets_from_controllers(duplication_axis_x, duplication_axis_y, 
                                      axis_transform_offset_x, axis_transform_offset_y,
                                      ctrl_prefix="CTRL_*", group_targets=True):
    """
    Generate a target set from an imported controller scene. This set will have a 
    controller associated from which the targets will be calculated.

    Example of use: generate_targets_from_controllers("x", "z", 25, 40)
        - Generates a grid of targets with x spacing of 25 and y spacing of 40.

    Args:
        duplication_axis_x (str): The horizontal axis that will be used for duplication.
        duplication_axis_y (str): The vertical axis that will be used for duplication.
        axis_transform_offset_x (float): Horizontal offset between duplicated targets.
        axis_transform_offset_y (float): Vertical offset between duplicated targets.
        ctrl_prefix (str, optional): Prefix string for the rig controllers. Defaults to CTRL_*.
        group_targets (bool, optional): Group the generated targets. Defaults to True.

    Returns:
        list: List of the names of the generated targets.
    """
    # Get the selected mesh shape and the associated blendshape node.
    extraction_mesh, blendshape_node = _get_mesh_and_blendshape_selection()
    if not extraction_mesh or not blendshape_node:
        print("{0} Could not generate target meshes.".format(UiConstants.LOG_PREFIX))
        return
    # Extract the controllers from the scene.
    history = cmds.listHistory(blendshape_node)
    history_selection = cmds.ls(history, type="transform")
    ctrl = cmds.ls(ctrl_prefix, type="transform")
    controllers = [x for x in history_selection if x in ctrl]
    # Get the limit information of the controllers.
    controls = list()
    group_dict_default = {
        "name": None,
        "data": {
            "has_limit": {
                "x": [False, False],
                "y": [False, False]
            },
            "limit": {
                "x": [0.0, 0.0],
                "y": [0.0, 0.0]
            }
        }
    }
    for con in controllers:
        group_dict = copy.deepcopy(group_dict_default)
        has_x_limit = cmds.transformLimits(con, etx=True, query=True) or [False, False]
        has_y_limit = cmds.transformLimits(con, ety=True, query=True) or [False, False]
        x_limit = cmds.transformLimits(con, tx=True, query=True) or [0.0, 0.0]
        y_limit = cmds.transformLimits(con, ty=True, query=True) or [0.0, 0.0]
        group_dict["data"]["has_limit"]["x"] = has_x_limit
        group_dict["data"]["has_limit"]["y"] = has_y_limit
        group_dict["data"]["limit"]["x"] = x_limit
        group_dict["data"]["limit"]["y"] = y_limit
        group_dict["name"] = con
        controls.append(group_dict)
    # Check the amount of valid targets that can be generated with the controllers.
    num_targets = 0
    for ctrl in controls:
        if ctrl["data"]["has_limit"]["x"][0] and ctrl["data"]["limit"]["x"][0] < 0:
            num_targets += 1
        if ctrl["data"]["has_limit"]["x"][1] and ctrl["data"]["limit"]["x"][1] > 0:
            num_targets += 1
        if ctrl["data"]["has_limit"]["y"][0] and ctrl["data"]["limit"]["y"][0] < 0:
            num_targets += 1
        if ctrl["data"]["has_limit"]["y"][1] and ctrl["data"]["limit"]["y"][1] > 0:
            num_targets += 1
    current_controller = 0
    current_target = 0
    extracted_target_meshes = []
    # Loop over all controllers (for all axis and limits) and generate targets.
    for i in range(num_targets):
        # Stop iterating when the number of targets have been reached.
        if current_target >= num_targets:
            break
        # Loop over each axis of the controller to get the targets.
        for axis, trans in zip(["x", "y"], ["translateX", "translateY"]):
            for limit_type in ["lower", "upper"]:
                ctrl_name = controls[current_controller]["name"]
                attr = "{0}.{1}".format(ctrl_name, trans)
                # Continue if the attribute is locked.
                if cmds.getAttr(attr, lock=True):
                  continue
                has_lower_limit = controls[current_controller]["data"]["has_limit"][axis][0]
                lower_limit = controls[current_controller]["data"]["limit"][axis][0]
                has_upper_limit = controls[current_controller]["data"]["has_limit"][axis][1]
                upper_limit = controls[current_controller]["data"]["limit"][axis][1]
                # Set the transform of the controller to the desired limit.
                if limit_type == "lower" and has_lower_limit and lower_limit < 0:
                    cmds.setAttr(attr, lower_limit)
                elif limit_type == "upper" and has_upper_limit and upper_limit > 0:
                    cmds.setAttr(attr, upper_limit)
                else:
                    continue
                # Duplicate a new mesh with the the generated expression.
                new_name = "{0}_{1}_{2}".format(ctrl_name, axis, limit_type)
                dupe_mesh = cmds.duplicate(extraction_mesh, n=new_name)[0]
                cmds.delete(dupe_mesh, constructionHistory=True)
                extracted_target_meshes.append(dupe_mesh)
                # Reset the controller value.
                cmds.setAttr("{0}.{1}".format(ctrl_name, trans), 0)
                current_target += 1
        current_controller += 1
    # Group the generated targets if selected.
    if extracted_target_meshes and group_targets:
        cmds.group(extracted_target_meshes, 
                   name="{}_targets".format(extraction_mesh))
    # Get the translation axis for the target meshes.
    axis_attr_x, axis_attr_y = _get_grid_axis(duplication_axis_x, duplication_axis_y)
    # Reorganize the targets to form a square formation.
    _move_targets_into_grid(extracted_target_meshes, num_targets, axis_attr_x, axis_attr_y,
                            axis_transform_offset_x, axis_transform_offset_y)


def generate_targets_from_blendshapes(duplication_axis_x, duplication_axis_y, 
                                      axis_transform_offset_x, axis_transform_offset_y,
                                      group_targets=True):
    """
    Generate a generic target set from an mesh containing blendshapes. This set will not have a 
    controller associated from which the targets will be calculated.

    Example of use: generate_generic_targets("x", "z", 25, 40)
        - Generates a grid of targets with x spacing of 25 and y spacing of 40.

    Args:
        duplication_axis_x (str): The horizontal axis that will be used for duplication.
        duplication_axis_y (str): The vertical axis that will be used for duplication.
        axis_transform_offset_x (float): Horizontal offset between duplicated targets.
        axis_transform_offset_y (float): Vertical offset between duplicated targets.
        group_targets (bool, optional): Group the generated targets. Defaults to True.

    Returns:
        list: List of the names of the generated targets.
    """
    extraction_mesh, blendshape_node = _get_mesh_and_blendshape_selection()
    if not extraction_mesh or not blendshape_node:
        print("{0} Could not generate target meshes.".format(UiConstants.LOG_PREFIX))
        return
    target_data = cmds.aliasAttr(blendshape_node, query=True)
    target_names = target_data[::2]
    num_targets = len(target_names)
    current_target = 0
    extracted_target_meshes = []
    for current_target in range(num_targets):
        # Stop iterating when the number of targets have been reached.
        if current_target >= num_targets:
            break
        target_name = target_names[current_target]
        bs_attr = "{}.{}".format(blendshape_node, target_name)
        # Duplicate a new mesh with the the generated expression.
        cmds.setAttr(bs_attr, lock=False)
        cmds.setAttr(bs_attr, 1, lock=False)
        dupe_mesh = cmds.duplicate(extraction_mesh, n=target_name)[0]
        cmds.delete(dupe_mesh, constructionHistory=True)
        extracted_target_meshes.append(dupe_mesh)
        # Reset the blendshape value.
        cmds.setAttr(bs_attr, 0, lock=False)
    # Group the generated targets if selected.
    if extracted_target_meshes and group_targets:
        cmds.group(extracted_target_meshes, 
                   name="{}_targets".format(extraction_mesh))
    # Get the translation axis for the target meshes.
    axis_attr_x, axis_attr_y = _get_grid_axis(duplication_axis_x, duplication_axis_y)
    # Reorganize the targets to form a square formation.
    _move_targets_into_grid(extracted_target_meshes, num_targets, axis_attr_x, axis_attr_y,
                            axis_transform_offset_x, axis_transform_offset_y)


def _get_mesh_and_blendshape_selection(default_blendshape="head_lod0_mesh_blendShapes"):
    """Get the selected mesh and its associated blendshape node.

    Args:
        default_blendshape (str, optional): Default blendshape node. Defaults to 
                                            head_lod0_mesh_blendShapes.

    Returns:
        str: The selected mesh node and its associated blenshape node.
    """
    # Get the currently selected mesh.
    selection = cmds.ls(selection=True, noIntermediate=True,
                        dagObjects=True, type="mesh", long=True)
    if not selection:
        print("{0} Incorrect selection provided for target creation.".format(UiConstants.LOG_PREFIX))
        return None, None
    selection_mesh_history = cmds.listHistory(selection[0])
    # Get the associated blendshape to the selected mesh.
    blendshapes = cmds.ls(selection_mesh_history, type="blendShape", long=True)
    if not blendshapes:
        blendshapes = cmds.ls(default_blendshape, type="blendShape", long=True)
        if not blendshapes:
            print("{0} No blendshape data found for target creation.".format(UiConstants.LOG_PREFIX))
            return selection[0], None
    return selection[0], blendshapes[0]


def _get_grid_axis(duplication_axis_x, duplication_axis_y):
    """Get the translation axis for the final target grid layout.

    Args:
        duplication_axis_x (str): The horizontal axis that will be used for duplication.
        duplication_axis_y (str): The vertical axis that will be used for duplication.

    Returns:
        str: Attribute names for both horizontal an vertical axis.
    """
    if duplication_axis_x == "y" or duplication_axis_x == "Y":
        axis_attr_x = "translateY"
    elif duplication_axis_x == "z" or duplication_axis_x == "Z":
        axis_attr_x = "translateZ"
    else:
        axis_attr_x = "translateX"

    if duplication_axis_y == "x" or duplication_axis_y == "X":
        axis_attr_y = "translateX"
    elif duplication_axis_y == "z" or duplication_axis_y == "Z":
        axis_attr_y = "translateZ"
    else:
        axis_attr_y = "translateY"

    return axis_attr_x, axis_attr_y


def _move_targets_into_grid(extracted_target_meshes, num_targets, axis_attr_x, axis_attr_y,
                            axis_transform_offset_x, axis_transform_offset_y):
    """
    Reorganize the targets to form a grid layout.

    Args:
        extracted_target_meshes (list): List of the names from the generated targets.
        num_targets (int): _description_
        axis_attr_x (str): Attribute name for horizontal axis.
        axis_attr_y (str): Attribute name for vertical axis.
        axis_transform_offset_x (float): Horizontal offset between duplicated targets.
        axis_transform_offset_y (float): Vertical offset between duplicated targets.
    """
    # Reorganize the targets to form a square formation.
    target = 0
    x_axis_offset = axis_transform_offset_x
    y_axis_offset = axis_transform_offset_y
    num_targets_axis = math.ceil(math.sqrt(num_targets))
    for x_axis in range(num_targets_axis):
        for y_axis in range(num_targets_axis):
            if target >= len(extracted_target_meshes):
                return
            current_mesh = extracted_target_meshes[target]
            # Translate the newly generated mesh to generate a grid formation.
            trs_attr_x = "{0}.{1}".format(current_mesh, axis_attr_x)
            trs_attr_y = "{0}.{1}".format(current_mesh, axis_attr_y)
            cmds.setAttr(trs_attr_x, lock=False)
            cmds.setAttr(trs_attr_y, lock=False)
            cmds.setAttr(trs_attr_x, x_axis_offset, lock=False)
            cmds.setAttr(trs_attr_y, y_axis_offset, lock=False)
            y_axis_offset += axis_transform_offset_y
            target += 1
        y_axis_offset = axis_transform_offset_y
        x_axis_offset += axis_transform_offset_x
