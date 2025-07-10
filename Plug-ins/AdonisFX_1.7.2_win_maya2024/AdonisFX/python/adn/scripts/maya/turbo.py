import logging
import re

import maya.cmds as cmds

from adn.scripts.maya.adnio import clear_scene
from adn.utils.maya.checkers import plugin_check
from adn.utils.maya.undo_stack import undo_chunk
from adn.tools.maya.muscle import apply_muscle
from adn.tools.maya.glue import apply_glue
from adn.tools.maya.skin import apply_skin
from adn.tools.maya.fat import apply_fat
from adn.tools.maya.relax import apply_relax
from adn.tools.maya.sensors import create_sensor_distance
from adn.commands.maya.scene import get_plugin_nodes_in_scene, get_mesh, create_group_hierarchy
from adn.utils.math import compute_main_axis
from adn.utils.geometry import find_extremal_vertices
from adn.utils.maya.geometry import get_closest_point_and_uv, get_points_py_list, get_bounding_box_diagonal
from adn.utils.maya.constants import OBJECT_PATH_DCC_REGEX
from adn.utils.constants import DeformerTypes, OtherNodeTypes
from adn.utils.constants import TurboFeatures


def check_duplicated_usage(feature, features_to_check, meshes, matches, report_data=None):
    """Checks if the mesh associated to the provided feature was already configured for another
    feature. If so, it will add an error message to the report data and return False.

    Args:
        feature (str): The feature to check for duplicates.
        features_to_check (list): A list of features to check against.
        meshes (dict): A dictionary containing the meshes associated with each feature.
        matches (dict): A dictionary containing the matches for each feature.
        report_data (dict, optional): A dictionary to store error and warning messages. Defaults to None.
    Returns:
        bool: True if no duplicates were found, False otherwise.
    """
    feature_labels = {
        TurboFeatures.MUMMY: "mummy",
        TurboFeatures.MUSCLES: "muscles",
        TurboFeatures.FASCIA: "fascia",
        TurboFeatures.FAT: "fat",
        TurboFeatures.SKIN: "skin"
    }
    for other_feature in features_to_check:
        if other_feature not in matches[feature]:
            continue
        duplicated_mesh = meshes[feature][0] if feature != TurboFeatures.MUSCLES else meshes[other_feature][0]
        msg = ("Could not configure {0} because the {0} geometry \"{1}\" was already "
                "provided and configured as {2}. AdnTurbo can't proceed with the downstream "
                "layers.").format(feature_labels[feature], duplicated_mesh, feature_labels[other_feature])
        add_to_report(report_data, "errors", msg)
        return False
    return True


def get_layer_meshes(objects, feature):
    """Retrieves the meshes from the provided objects performing the same checks as
    the turbo functions (i.e. turbo_muscles, turbo_fascia, turbo_fat, turbo_skin).

    Args:
        objects (str or list): The name of the object(s) to be checked.
        feature (str): The feature for which the meshes are being retrieved.

    Returns:
        list: A list of meshes found in the provided objects.
    """
    if not objects:
        return []
    if isinstance(objects, str):
        objects = [objects]

    meshes = []
    for object in objects:
        # We perform the following checks because if any of them is fulfilled,
        # then the dedicated function to configure each layer would already
        # skip and prompt the error.
        if not object:
            continue
        if not cmds.objExists(object):
            continue
        long_name = cmds.ls(object, long=True)
        if len(long_name) > 1:
            continue
        tmp_meshes = get_mesh(object)
        if len(tmp_meshes) == 0:
            continue
        # If we find more than one mesh, we don't add it. The reason is that
        # we will ignore duplicated meshes because the dedicated function to
        # configure each layer will prompt an error when multiple meshes are found.
        if feature != TurboFeatures.MUSCLES and len(tmp_meshes) > 1:
            continue
        meshes.extend(tmp_meshes)

    return meshes

def group_objects(objects, group, create_group, objects_name, report_data=None):
    """Groups the provided objects under the specified group. If the group does not exist,
    it will be created if the create_group flag is set to True.

    This function is meant to be used to group objects created by the AdnTurbo process (i.e. rivets,
    locators and glue geometry).

    Args:
        objects (str or list): The name of the object(s) to be grouped.
        group (str): The name of the group under which the objects will be grouped.
        create_group (bool): If True, a new group will be created if the specified group does not exist.
        objects_name (str): Label that identifies the objects being grouped.
        report_data (dict, optional): A dictionary to store error and warning messages. Defaults to None.
    """
    if not group and create_group:
        msg = ("No group name was provided for {0}. "
               "The {0} will be created at the scene root."
               "").format(objects_name)
        add_to_report(report_data, "warnings", msg)
        return

    if group is None:
        return
    
    if re.fullmatch(OBJECT_PATH_DCC_REGEX, group) is None:
        msg = ("Could not create the group \"{1}\" for {0} because the name provided "
               "is not a valid path. The {0} will be created at the scene root. "
               "A valid path is an alpha numeric string starting by a letter or a pipe; "
               "numbers are not allowed after a pipe; and special characters other than "
               "underscores are not allowed.").format(objects_name, group)
        add_to_report(report_data, "warnings", msg)
        return

    if not cmds.objExists(group):
        if create_group:
            new_group = create_group_hierarchy(group)
            if not new_group:
                msg = ("Could not create the group \"{1}\" for {0} because the path provided "
                       "contains non-transform nodes. The {0} will be created at the scene root."
                        "").format(objects_name, group)
                add_to_report(report_data, "warnings", msg)
                return
            group = new_group
        else:
            msg = ("The object \"{0}\" provided as {1} group does not exist, "
                    "the {1} will be created at the scene root."
                    "").format(group, objects_name)
            add_to_report(report_data, "warnings", msg)
            return
    else:
        if cmds.nodeType(group) != "transform":
            msg = ("The object \"{0}\" provided as {1} group is not a transform node, "
                    "the {1} will be created at the scene root."
                    "").format(group, objects_name)
            add_to_report(report_data, "warnings", msg)
            return

    # Check if there are nodes in the group
    group_children = cmds.listRelatives(group, children=True, fullPath=True) or []
    if group_children:
        group_children_str = ", ".join(['"{0}"'.format(name) for name in group_children])
        msg = ("The object \"{0}\" provided as {1} group already contained objects "
                "({2}). It may be advisable to remove them if they are not used."
                "").format(group, objects_name, group_children_str)
        add_to_report(report_data, "warnings", msg)

    cmds.parent(objects, group)


def get_name_from_geo(geo_name, object_name):
    """Generates a name for the object based on the geometry name and the object type.
    If the geometry name ends with "GEO" or "geo", it is removed before concatenation.

    Args:
        geo_name (str): The name of the geometry.
        object_name (str): The name of the object type.

    Returns:
        str: The generated name for the object.
    """
    if not object_name:
        return ""
    if not geo_name:
        return object_name

    if geo_name.upper().endswith("GEO"):
        geo_name = geo_name[:-3]

    return "{0}{1}".format(geo_name, object_name)


def get_scaled_max_sliding_distance(input_sliding_distance, space_scale, target_mesh):
    """Calculates the maximum sliding distance based on the input sliding distance,
    space scale, and the bounding box diagonal of the target mesh.
    The maximum sliding distance is capped to the 10% of the bounding box diagonal
    of the target mesh.

    Args:
        input_sliding_distance (float): The input sliding distance.
        space_scale (float): The space scale factor.
        target_mesh (str): The name of the target mesh.

    Returns:
        float: The scaled maximum sliding distance.
    """
    # Diagonal length of the bounding box of the target mesh
    diagonal_length = get_bounding_box_diagonal(target_mesh)
    # Desired distance: 10% of the diagonal length minus a tolerance of 1e-3
    max_sliding_distance = (diagonal_length * 0.1) - 1e-3
    if space_scale < 1e-6:
        return max_sliding_distance
    # Tentative sliding distance based on the space scale
    scaled_sliding_distance = input_sliding_distance / space_scale
    # Make sure the scaled sliding distance is not greater than the maximum
    return min(scaled_sliding_distance, max_sliding_distance)


def add_to_report(report_data, key, msg):
    """Adds a message to the report data dictionary under the specified key.
    If the key does not exist, the message will not be added.

    Args:
        report_data (dict): The dictionary to store messages.
        key (str): The key under which to store the message.
        msg (str): The message to be added.
    """
    if report_data is None:
        return
    if key not in report_data.keys():
        return
    report_data[key].append(msg)


def create_rivet_at_point(mesh, target_point, rivet_base_name, space_scale=1.0):
    """Creates a rivet-based rivet on the given mesh at the point closest
    to target_point. The rivet is positioned based on UV coordinates computed
    via maya.OpenMaya, so the resulting locator will follow the mesh as it deforms.

    Args:
        mesh (str): The name of the mesh (e.g., "mummy_geo").
        target_point (tuple): A 3-tuple (x, y, z) representing the target point.
        rivet_base_name (str): Base name for the created nodes.
        space_scale (float, optional): The scale factor for the space scale parameter of
            the nodes. Defaults to 1.0.

    Returns:
        str: The name of the uvPin node created.
        str: The name of the uvOutput node created.
    """
    # Use the API to compute the closest point and its UV in world space.
    closest_point, (u, v) = get_closest_point_and_uv(mesh, target_point)
    
    # Get the shape node for the mesh.
    if cmds.nodeType(mesh) != "mesh":
        shapes = cmds.listRelatives(mesh, shapes=True)
        if not shapes:
            return None, None

    if rivet_base_name is None:
        rivet_base_name = ""
    
    # Create a rivet node.
    cmds.select("{0}.f[0]".format(mesh))
    rivet_name = "{0}_rivet".format(rivet_base_name)
    rivet_locator_name = "{0}_rivet_loc".format(rivet_base_name)
    cmds.Rivet()
    uv_pin, pin_output = cmds.ls(selection=True)
    rivet_name = cmds.rename(uv_pin, rivet_name)
    rivet_locator_name = cmds.rename(pin_output, rivet_locator_name)
    
    # Set the rivet's UV parameters based on the computed UV.
    cmds.setAttr("{0}.coordinate[0].coordinateU".format(rivet_name), u)
    cmds.setAttr("{0}.coordinate[0].coordinateV".format(rivet_name), v)

    # Set local scale based on the space scale for better visualization
    if space_scale > 1e-6:
        local_scale = 1.0 / space_scale
        cmds.setAttr("{0}.localScaleX".format(rivet_locator_name), local_scale)
        cmds.setAttr("{0}.localScaleY".format(rivet_locator_name), local_scale)
        cmds.setAttr("{0}.localScaleZ".format(rivet_locator_name), local_scale)

    return rivet_name, rivet_locator_name


def turbo_muscles(mummy_geo, muscles, glue=True, glue_group_name=None,
                  create_glue_group=False, locators=True, locators_group_name=None,
                  create_locators_group=False, space_scale=1.0, report_data=None):
    """Applies the AdnTurbo process to the given muscles group by creating AdnMuscle
    nodes to each muscle geometry. Additionally, it creates a glue node with all the
    AdnMuscle nodes created as inputs.

    Args:
        mummy_geo (str): The name of the geometry representing the bones to which the
            muscles are attached.
        muscles (str or list): The muscle geometries. It can be a mesh, a group containing the mesh,
            or a list of meshes.
        glue (bool, optional): If True, an AdnGlue node with the muscles as inputs will be created.
            Defaults to True.
        glue_group_name (str, optional): The name of the group to which the glue node will be added.
            Defaults to None.
        create_glue_group (bool, optional): If True and glue_group_name is provided, a new group will be
            created in which the glue geometry will be created. Defaults to False.
        locators (bool, optional): If True, rivets, sensors and locators will be created for each muscle.
            Defaults to True.
        locators_group_name (str, optional): The name of the group to which the locators, sensors and
            rivets will be added. Defaults to None.
        create_locators_group (bool, optional): If True and locators_group_name is provided, a new group
            will be created in which the locators, sensors and rivets will be created. Defaults to False.
        space_scale (float, optional): The scale factor for the space scale parameter of
            the nodes. Defaults to 1.0.
        report_data (dict, optional): A dictionary to store error and warning messages.
            Defaults to None.

    Returns:
        str: The name of the glue node created. If the process fails, returns None.
        bool: True if any muscle was created, False otherwise.
    """
    from adn.api import adnx
    if not muscles:
        msg = ("Could not configure muscles because a muscle, a muscle list or parent group "
               "containing all muscle geometries is required but not provided. AdnTurbo can't "
               "proceed with the downstream layers.")
        add_to_report(report_data, "errors", msg)
        return None, False

    if isinstance(muscles, str):
        muscle_list = [muscles]
    else:
        muscle_list = muscles

    muscle_geos = []
    # Iterate muscle list to evaluate every object individually for better error/warning handling
    for obj in muscle_list:
        # Each object in the list can be a shape (e.g. pPlane1Shape), the transform (e.g. pPlane1)
        # or a transform used as a group (e.g. pPlane1_grp).
        if obj is None or not cmds.objExists(obj):
            msg = ("Could not configure muscle(s) for \"{0}\" because it does not exist. "
                   "This object is skipped.").format(obj)
            add_to_report(report_data, "warnings", msg)
            continue
        # If this call returns more than one object, it means that there are multiple
        # objects with the same name in the scene and the user provided the short name.
        long_name = cmds.ls(obj, long=True)
        if len(long_name) > 1:
            long_name_str = ", ".join(['"{0}"'.format(name) for name in long_name])
            msg = ("Could not configure muscle(s) for \"{0}\" because more than one object "
                   "with the same name was found: {1}. This object is skipped."
                   "").format(obj, long_name_str)
            add_to_report(report_data, "warnings", msg)
            continue
        tmp_muscles = get_mesh(obj)
        if len(tmp_muscles) == 0:
            msg = ("Could not configure muscle(s) on the object \"{0}\" provided because "
                   "it does not contain any valid meshes. This object is skipped.").format(obj)
            add_to_report(report_data, "warnings", msg)
            continue
        muscle_geos.extend(tmp_muscles)

    if len(muscle_geos) == 0:
        msg = ("Could not configure muscles because no valid meshes were found in the objects "
               "provided. AdnTurbo can't proceed with the downstream layers.").format(muscles)
        add_to_report(report_data, "errors", msg)
        return None, False

    # Filter out duplicated meshes
    tmp_muscle_geos = []
    visited = set()
    for geo in muscle_geos:
        if geo in visited:
            msg = ("The muscle mesh \"{0}\" is duplicated in the input list. Only one "
                   "AdnMuscle deformer will be applied to this mesh.").format(geo)
            add_to_report(report_data, "warnings", msg)
        else:
            tmp_muscle_geos.append(geo)
            visited.add(geo)
    muscle_geos = tmp_muscle_geos

    # Calculate a valid max sliding distance
    scaled_sliding_distance = get_scaled_max_sliding_distance(1.0, space_scale, mummy_geo)

    successful_muscle_geos = []
    auxiliary_nodes = []
    for geo in muscle_geos:
        geo_short_name = cmds.ls(geo, shortNames=True)
        # This should not happen as previously we checked if the object is a mesh
        if not geo_short_name:
            msg = ("Could not configure a muscle solver for \"{0}\" because its short name "
                   "could not be resolved. This object is skipped.").format(geo)
            add_to_report(report_data, "warnings", msg)
            continue
        geo_short_name = geo_short_name[0]
        # Even if we retrieve the short name, we can still get a long name if there are
        # multiple meshes with the same name in the scene (e.g. group1|pPlane1|pPlane1Shape, group2|pPlane1|pPlane1Shape).
        # For this reason if the name contains "|", we take the last part of the name.
        if "|" in geo_short_name:
            geo_short_name = geo_short_name.split("|")[-1]
        solver_name = get_name_from_geo(geo_short_name, DeformerTypes.MUSCLE)
        cmds.select([mummy_geo, geo])
        solver_name, success = apply_muscle(custom_name=solver_name)
        # If apply_muscle fails, skip this muscle
        if not success and not solver_name:
            msg = ("The AdnTurbo process failed to create {0} for the muscle \"{1}\", "
                   "it will be skipped.").format(DeformerTypes.MUSCLE, geo)
            add_to_report(report_data, "warnings", msg)
            continue
        successful_muscle_geos.append(geo)
        adn_rig = adnx.AdnRig(adnx.AdnHost.kMaya)
        adn_solver = adnx.AdnMuscle(adn_rig)
        adn_solver.fromNode(solver_name)
        
        vertex_count = cmds.polyEvaluate(geo, vertex=True)
        attachment_map = [0.1] * vertex_count
        sliding_map = [0.5] * vertex_count
        tendons_map = [0.0] * vertex_count
        shape_preservation_map = [1.0] * vertex_count
        
        adn_solver.setParameter("geometryAttachmentsMap", [attachment_map])
        adn_solver.setParameter("geometrySlidingMap", [sliding_map])
        adn_solver.setParameter("shapePreservationMap", shape_preservation_map)
        adn_solver.setParameter("pointMassMode", 0)
        adn_solver.setParameter("globalMassMultiplier", 0.1)
        adn_solver.setParameter("triangulateMesh", True)
        adn_solver.setParameter("hardAttachments", False)
        adn_solver.setParameter("maxSlidingDistance", scaled_sliding_distance)
        adn_solver.setParameter("slidingConstraintsMode", 1)
        adn_solver.setParameter("spaceScale", space_scale)
        adn_solver.setParameter("spaceScaleMode", 2)
        adn_solver.setParameter("gravity", 9.8)

        vertices = get_points_py_list(geo)
        main_axis_info = compute_main_axis(vertices)
        fibers_centroid = main_axis_info[0]
        fibers_dir = main_axis_info[1]
        # If compute_muscle_fibers or find_extremal_vertices fails, skip the creation
        # of the sensor and locator and report the warning.
        msg_1 = "Could not configure sensor nor locator for muscle \"{0}\".".format(geo)
        msg_2 = "Could not configure tendons nor fiber directions for muscle \"{0}\".".format(geo)
        if fibers_centroid is None or fibers_dir is None:
            add_to_report(report_data, "warnings", msg_1)
            add_to_report(report_data, "warnings", msg_2)
            continue
        extremal_vertices_data = find_extremal_vertices(vertices, fibers_centroid, fibers_dir)
        if not extremal_vertices_data:
            add_to_report(report_data, "warnings", msg_1)
            add_to_report(report_data, "warnings", msg_2)
            continue
        start_index = extremal_vertices_data["start_index"]
        end_index = extremal_vertices_data["end_index"]
        start_point = extremal_vertices_data["start_point"]
        end_point = extremal_vertices_data["end_point"]
        tendons_map[start_index] = 1.0
        tendons_map[end_index] = 1.0
        adn_solver.setParameter("tendonsMap", tendons_map)
        adn_solver.update()
        if not locators:
            continue
        rivet_start_name = get_name_from_geo(geo_short_name, "SensorStart")
        rivet_end_name = get_name_from_geo(geo_short_name, "SensorEnd")
        rivet_start, locator_start = create_rivet_at_point(mummy_geo, start_point, rivet_start_name, space_scale)
        rivet_end, locator_end = create_rivet_at_point(mummy_geo, end_point, rivet_end_name, space_scale)
        if not locator_start or not locator_end:
            add_to_report(report_data, "warnings", msg_1)
            continue
        cmds.select([locator_start, locator_end])
        create_sensor_distance()
        sensor_name = get_name_from_geo(geo_short_name, "Sensor")
        locator_name = get_name_from_geo(geo_short_name, "Locator")
        sensor_name = cmds.rename("adnSensorDistance1", sensor_name)
        locator_name = cmds.rename("adnLocatorDistance1", locator_name)
        distance_min = cmds.getAttr("{0}.inputMinDistance".format(sensor_name))
        cmds.setAttr("{0}.inputMaxDistance".format(sensor_name), distance_min * 0.666)
        cmds.connectAttr("{0}.activationDistance".format(locator_name), "{0}.activation".format(solver_name))
        auxiliary_nodes += [locator_start, locator_end, locator_name]

        if space_scale > 1e-6:
            locator_shape_name = "{0}Shape".format(locator_name)
            cmds.setAttr("{0}.scale".format(locator_shape_name), 1.0 / space_scale)

    # If none of the objects provided as muscles were valid,
    # abort the process and report the error
    if not successful_muscle_geos:
        msg = ("Could not configure any muscle provided. AdnTurbo "
               "can't proceed with the downstream layers.")
        add_to_report(report_data, "errors", msg)
        return None, False

    if auxiliary_nodes:
        group_objects(auxiliary_nodes, locators_group_name, create_locators_group,
                      "locators", report_data=report_data)

    if not glue:
        return None, True

    cmds.select(successful_muscle_geos)
    solver_name, success = apply_glue()
    # If apply_glue fails, abort the process and report the error
    if not success and not solver_name:
        msg = ("Could not create {0} solver. AdnTurbo can't proceed with the "
               "downstream layers.").format(OtherNodeTypes.GLUE)
        add_to_report(report_data, "errors", msg)
        return None, True
    adn_rig = adnx.AdnRig(adnx.AdnHost.kMaya)
    adn_solver = adnx.AdnGlue(adn_rig)
    adn_solver.fromNode(solver_name)
    adn_solver.setParameter("iterations", 10)
    adn_solver.setParameter("pointMassMode", 0)
    adn_solver.setParameter("globalMassMultiplier", 0.1)
    adn_solver.setParameter("maxGlueDistance", 2.0)
    adn_solver.setParameter("spaceScale", space_scale)
    adn_solver.update()

    glue_geo = cmds.listConnections("{0}.outputMesh".format(solver_name)) or []
    if not glue_geo:
        # This code should never be reached. Once muscles are built,
        # we always should be able to build AdnGlue and retrieve the mesh.
        msg = ("Could not retrieve the output mesh from the {0} \"{1}\". AdnTurbo "
               "can't proceed with the downstream layers.").format(OtherNodeTypes.GLUE, solver_name)
        add_to_report(report_data, "errors", msg)
        return None, True
    glue_geo = glue_geo[0]

    vertex_count = cmds.polyEvaluate(glue_geo, vertex=True)
    shape_preservation_map = [1.0] * vertex_count
    adn_solver.setParameter("shapePreservationMap", shape_preservation_map)
    adn_solver.update()

    group_objects(glue_geo, glue_group_name, create_glue_group,
                  "glue geometry", report_data=report_data)

    return glue_geo, True


def turbo_fascia(mummy_geo, glue_geo, fascia, space_scale=1.0, report_data=None):
    """Applies the AdnTurbo process to the given fascia geometry by creating AdnSkin and
    AdnRelax nodes. The process requires the mummy geometry and the glue geometry to be provided.

    Args:
        mummy_geo (str): The name of the geometry representing the bones that will
            be a fascia target.
        glue_geo (str): The name of the glue geometry created from the muscles that
            will be a fascia target.
        fascia_geo (str): The name of the fascia to be processed. It can be a mesh or
            a group containing the mesh.
        space_scale (float, optional): The scale factor for the space scale parameter
            of the AdnSkin node. Defaults to 1.0.
        report_data (dict, optional): A dictionary to store error and warning messages.
            Defaults to None.

    Returns:
        str: The name of the fascia geometry created. If the process fails, returns None.
    """
    from adn.api import adnx
    if not fascia:
        msg = ("Could not configure fascia because the fascia geometry was not provided. "
               "AdnTurbo can't proceed with the downstream layers.")
        add_to_report(report_data, "errors", msg)
        return None

    if not cmds.objExists(fascia):
        msg = ("Could not configure fascia because the object \"{0}\" provided does not exist. "
               "AdnTurbo can't proceed with the downstream layers.").format(fascia)
        add_to_report(report_data, "errors", msg)
        return None

    # If this call returns more than one object, it means that there are multiple
    # objects with the same name in the scene and the user provided the short name.
    long_name = cmds.ls(fascia, long=True)
    if len(long_name) > 1:
        long_name_str = ", ".join(['"{0}"'.format(name) for name in long_name])
        msg = ("Could not configure fascia for \"{0}\" because more than one object "
               "with the same name was found: {1}. AdnTurbo can't proceed with the "
               "downstream layers.").format(fascia, long_name_str)
        add_to_report(report_data, "errors", msg)
        return None

    fascia_geo = get_mesh(fascia)
    if len(fascia_geo) == 0:
        msg = ("Could not configure fascia because no valid mesh was found in the object "
               "\"{0}\" provided. AdnTurbo can't proceed with the downstream layers.").format(fascia)
        add_to_report(report_data, "errors", msg)
        return None
    if len(fascia_geo) > 1:
        msg = ("Could not configure fascia because more than one mesh was found in the object "
               "\"{0}\" provided and only one is allowed. AdnTurbo can't proceed with the "
               "downstream layers.").format(fascia)
        add_to_report(report_data, "errors", msg)
        return None
    fascia_geo = fascia_geo[0]

    cmds.select([mummy_geo, glue_geo, fascia_geo])
    solver_name, success = apply_skin(custom_name="fascia_{0}1".format(DeformerTypes.SKIN))
    # If apply_skin fails, abort the process and report the error
    if not success and not solver_name:
        msg = ("Could not configure fascia because something failed when creating the {0} "
               "solver. AdnTurbo can't proceed with the downstream layers.").format(DeformerTypes.SKIN)
        add_to_report(report_data, "errors", msg)
        return None
    
    # Calculate a valid max sliding distance
    scaled_sliding_distance_on_mummy = get_scaled_max_sliding_distance(3.0, space_scale, mummy_geo)
    scaled_sliding_distance_on_glue = get_scaled_max_sliding_distance(3.0, space_scale, glue_geo)
    scaled_sliding_distance = max(scaled_sliding_distance_on_mummy, scaled_sliding_distance_on_glue)

    adn_rig = adnx.AdnRig(adnx.AdnHost.kMaya)
    adn_solver = adnx.AdnSkin(adn_rig)
    adn_solver.fromNode(solver_name)
    adn_solver.setParameter("iterations", 10)
    adn_solver.setParameter("material", 7)
    adn_solver.setParameter("gravity", 9.8)
    adn_solver.setParameter("pointMassMode", 0)
    adn_solver.setParameter("globalMassMultiplier", 0.1)
    adn_solver.setParameter("triangulateMesh", True)
    adn_solver.setParameter("maxSlidingDistance", scaled_sliding_distance)
    adn_solver.setParameter("slidingConstraintsMode", 1)
    adn_solver.setParameter("spaceScale", space_scale)
    vertex_count = cmds.polyEvaluate(fascia_geo, vertex=True)
    hard_map = [0.1] * vertex_count
    soft_map = [0.6] * vertex_count
    slide_map = [0.3] * vertex_count
    shape_preservation_map = [1.0] * vertex_count
    adn_solver.setParameter("hardConstraintsMap", hard_map)
    adn_solver.setParameter("softConstraintsMap", soft_map)
    adn_solver.setParameter("slideConstraintsMap", slide_map)
    adn_solver.setParameter("shapePreservationMap", shape_preservation_map)
    adn_solver.update()

    cmds.select(fascia_geo)
    solver_name, success = apply_relax()
    # If apply_relax fails, abort the process and report the error
    if not success and not solver_name:
        msg = ("Could not configure an {0} node on the fascia. AdnTurbo skips this step "
               "to continue with the downstream layers.").format(DeformerTypes.RELAX)
        add_to_report(report_data, "warnings", msg)
        return fascia_geo
    solver_name = cmds.rename(solver_name, "fascia_{0}1".format(DeformerTypes.RELAX))
    adn_rig = adnx.AdnRig(adnx.AdnHost.kMaya)
    adn_deformer = adnx.AdnRelax(adn_rig)
    adn_deformer.fromNode(solver_name)
    adn_deformer.setParameter("iterations", 10)
    adn_deformer.setParameter("pushOutRatio", 1)
    adn_deformer.setParameter("pushOutThreshold", 0.15)
    adn_deformer.update()

    return fascia_geo


def turbo_fat(fascia_geo, fat, space_scale=1.0, report_data=None):
    """Applies the AdnTurbo process to the given fat geometry by creating AdnFat and
    AdnRelax nodes. The process requires the fascia geometry to be provided.

    Args:
        fascia_geo (str): The name of the fascia geometry that acts as base mesh of the fat.
        fat (str): The name of the fat to be processed. It can be a mesh or a group
            containing the mesh.
        space_scale (float, optional): The scale factor for the space scale parameter of the
            AdnFat node. Defaults to 1.0.
        report_data (dict, optional): A dictionary to store error and warning messages.
            Defaults to None.

    Returns:
        str: The name of the fat geometry created. If the process fails, returns None.
    """
    from adn.api import adnx
    if not fat:
        msg = ("Could not configure fat because the fat geometry was not provided. "
               "AdnTurbo can't proceed with the downstream layers.")
        add_to_report(report_data, "errors", msg)
        return False

    if not cmds.objExists(fat):
        msg = ("Could not configure fat because the object \"{0}\" provided does not exist. "
               "AdnTurbo can't proceed with the downstream layers.").format(fat)
        add_to_report(report_data, "errors", msg)
        return None

    # If this call returns more than one object, it means that there are multiple
    # objects with the same name in the scene and the user provided the short name.
    long_name = cmds.ls(fat, long=True)
    if len(long_name) > 1:
        long_name_str = ", ".join(['"{0}"'.format(name) for name in long_name])
        msg = ("Could not configure fat for \"{0}\" because more than one object "
               "with the same name was found: {1}. AdnTurbo can't proceed with the "
               "downstream layers.").format(fat, long_name_str)
        add_to_report(report_data, "errors", msg)
        return None

    fat_geo = get_mesh(fat)
    if len(fat_geo) == 0:
        msg = ("Could not configure fat because no valid mesh was found in the object "
               "\"{0}\" provided. AdnTurbo can't proceed with the downstream layers.").format(fat)
        add_to_report(report_data, "errors", msg)
        return None
    if len(fat_geo) > 1:
        msg = ("Could not configure fat because more than one mesh was found in the object "
               "\"{0}\" provided and only one is allowed. AdnTurbo can't proceed with the "
               "downstream layers.").format(fat)
        add_to_report(report_data, "errors", msg)
        return None
    fat_geo = fat_geo[0]

    if cmds.polyEvaluate(fat_geo, vertex=True) != cmds.polyEvaluate(fascia_geo, vertex=True):
        msg = ("Could not configure fat because the fascia \"{0}\" and fat \"{1}\" geometries "
               "have mismatching vertex count. In order to create the fat solver it is "
               "required for the two geometries to be topologically identical (while "
               "different in shape). AdnTurbo can't proceed with the downstream "
               "layers.").format(fascia_geo, fat_geo)
        add_to_report(report_data, "errors", msg)
        return None

    cmds.select([fascia_geo, fat_geo])
    solver_name, success = apply_fat(custom_name="fat_{0}1".format(DeformerTypes.FAT))
    # If apply_fat fails, abort the process and report the error
    if not success and not solver_name:
        msg = ("Could not configure fat because something failed when creating the {0} "
               "solver. AdnTurbo can't proceed with the downstream layers.").format(DeformerTypes.FAT)
        add_to_report(report_data, "errors", msg)
        return None
    
    vertex_count = cmds.polyEvaluate(fat_geo, vertex=True)
    shape_preservation_map = [1.0] * vertex_count

    adn_rig = adnx.AdnRig(adnx.AdnHost.kMaya)
    adn_solver = adnx.AdnFat(adn_rig)
    adn_solver.fromNode(solver_name)
    adn_solver.setParameter("gravity", 9.8)
    adn_solver.setParameter("pointMassMode", 0)
    adn_solver.setParameter("globalMassMultiplier", 0.1)
    adn_solver.setParameter("spaceScale", space_scale)
    adn_solver.setParameter("shapePreservationMap", shape_preservation_map)
    adn_solver.update()

    cmds.select(fat_geo)
    solver_name, success = apply_relax()
    # If apply_relax fails, abort the process and report the error
    if not success and not solver_name:
        msg = ("Could not configure an {0} node on the fat. AdnTurbo skips this step "
               "to continue with the downstream layers.").format(DeformerTypes.RELAX)
        add_to_report(report_data, "warnings", msg)
        return fat_geo
    solver_name = cmds.rename(solver_name, "fat_{0}1".format(DeformerTypes.RELAX))
    adn_rig = adnx.AdnRig(adnx.AdnHost.kMaya)
    adn_deformer = adnx.AdnRelax(adn_rig)
    adn_deformer.fromNode(solver_name)
    adn_deformer.setParameter("iterations", 10)
    adn_deformer.setParameter("pushOutRatio", 1)
    adn_deformer.setParameter("pushOutThreshold", 0.15)
    adn_deformer.update()

    return fat_geo


def turbo_skin(fat_geo, skin, space_scale=1.0, report_data=None):
    """Applies the AdnTurbo process to the given skin geometry by creating AdnSkin nodes.
    The process requires the fat geometry to be provided.

    Args:
        fat_geo (str): The name of the fat geometry that will be the skin target.
        skin_geo (str): The name of the skin to be processed. It can be a mesh or a group
            containing the mesh.
        space_scale (float, optional): The scale factor for the space scale parameter
            of the AdnSkin node. Defaults to 1.0.
        report_data (dict, optional): A dictionary to store error and warning messages.
            Defaults to None.

    Returns:
        str: The name of the skin geometry created. If the process fails, returns None.
    """
    from adn.api import adnx
    if not skin:
        msg = "Could not configure skin because the skin geometry was not provided."
        add_to_report(report_data, "errors", msg)
        return None

    if not cmds.objExists(skin):
        msg = ("Could not configure skin because the object \"{0}\" provided does not exist. "
               "").format(skin)
        add_to_report(report_data, "errors", msg)
        return None

    # If this call returns more than one object, it means that there are multiple
    # objects with the same name in the scene and the user provided the short name.
    long_name = cmds.ls(skin, long=True)
    if len(long_name) > 1:
        long_name_str = ", ".join(['"{0}"'.format(name) for name in long_name])
        msg = ("Could not configure skin for \"{0}\" because more than one object "
               "with the same name was found: {1}. AdnTurbo can't proceed with the "
               "downstream layers.").format(skin, long_name_str)
        add_to_report(report_data, "errors", msg)
        return None

    skin_geo = get_mesh(skin)
    if len(skin_geo) == 0:
        msg = ("Could not configure skin because no valid mesh was found in the object "
               "\"{0}\" provided. AdnTurbo can't proceed with the downstream layers.").format(skin)
        add_to_report(report_data, "errors", msg)
        return None
    if len(skin_geo) > 1:
        msg = ("Could not configure skin because more than one mesh was found in the object "
               "\"{0}\" provided and only one is allowed. AdnTurbo can't proceed with the "
               "downstream layers.").format(skin)
        add_to_report(report_data, "errors", msg)
        return None
    skin_geo = skin_geo[0]

    cmds.select([fat_geo, skin_geo])
    solver_name, success = apply_skin(custom_name="skin_{0}1".format(DeformerTypes.SKIN))
    # If apply_skin fails, abort the process and report the error
    if not success and not solver_name:
        msg = ("Could not configure skin because something failed when creating the {0} "
               "solver.").format(DeformerTypes.SKIN)
        add_to_report(report_data, "errors", msg)
        return None
    
    # Calculate a valid max sliding distance
    scaled_sliding_distance = get_scaled_max_sliding_distance(3.0, space_scale, fat_geo)

    adn_rig = adnx.AdnRig(adnx.AdnHost.kMaya)
    adn_solver = adnx.AdnSkin(adn_rig)
    adn_solver.fromNode(solver_name)
    adn_solver.setParameter("iterations", 10)
    adn_solver.setParameter("material", 7)
    adn_solver.setParameter("gravity", 9.8)
    adn_solver.setParameter("pointMassMode", 0)
    adn_solver.setParameter("globalMassMultiplier", 0.1)
    adn_solver.setParameter("triangulateMesh", True)
    adn_solver.setParameter("maxSlidingDistance", scaled_sliding_distance)
    adn_solver.setParameter("compressionMultiplier", 0.5)
    adn_solver.setParameter("slidingConstraintsMode", 1)
    adn_solver.setParameter("spaceScale", space_scale)
    vertex_count = cmds.polyEvaluate(skin_geo, vertex=True)
    hard_map = [0.0] * vertex_count
    soft_map = [0.6] * vertex_count
    slide_map = [0.3] * vertex_count
    shape_preservation_map = [1.0] * vertex_count
    adn_solver.setParameter("hardConstraintsMap", hard_map)
    adn_solver.setParameter("softConstraintsMap", soft_map)
    adn_solver.setParameter("slideConstraintsMap", slide_map)
    adn_solver.setParameter("shapePreservationMap", shape_preservation_map)
    adn_solver.update()

    return skin_geo


@undo_chunk
def apply_turbo(mummy, muscles, fascia=None, fat=None, skin=None, glue=True,
                glue_group_name=None, create_glue_group=False, locators=True,
                locators_group_name=None, create_locators_group=False, space_scale=1.0,
                force=False, report_data=None):
    """Apply the AdnTurbo process to the given geometries, creating the AdonisFX
    nodes and setting up the simulation.

    Args:
        mummy (str): The name of the mummy. It can be a mesh or a group containing the mesh.
        muscles (str or list): The muscle geometries. It can be a mesh, a group containing the mesh,
                or a list of meshes.
        fascia (str, optional): The name of the fascia. It can be a mesh or a group
            containing the mesh. Defaults to None.
        fat (str, optional): The name of the fat. It can be a mesh or a group containing the mesh.
            Defaults to None.
        skin (str, optional): The name of the skin. It can be a mesh or a group containing the mesh.
            Defaults to None.
        glue (bool, optional): If True, creates an AdnGlue node with the muscles as inputs.
            Defaults to True.
        glue_group_name (str, optional): The name of the group to which the glue node will be added.
            Defaults to None.
        create_glue_group (bool, optional): If True and glue_group_name is provided, creates a new
            group in which the glue geometry will be created. Defaults to False.
        locators (bool, optional): If True, creates rivets, sensors and locators for each muscle.
            Defaults to True.
        locators_group_name (str, optional): The name of the group to which the locators, sensors and
            rivets will be added. Defaults to None.
        create_locators_group (bool, optional): If True and locators_group_name is provided, creates a new
            group in which the locators, sensors and rivets will be created. Defaults to False.
        space_scale (float, optional): The space scale for the simulation. Defaults to 1.0.
        force (bool, optional): If True, forces the process even if there are AdonisFX
            nodes in the scene. Defaults to False.
        report_data (dict, optional): A dictionary to store error and warning messages.
            Defaults to None.

    Raises:
        TypeError: If the type of the mummy, muscles, fascia, fat, skin, glue_group_name or 
            locators_group_name arguments is not valid.
        ValueError: If the `space_scale` argument is close to 0.0 or negative.
    """
    plugin_check()

    # Type check for the mummy, muscles, fascia, fat, skin, glue_group_name and locators_group_name arguments
    if mummy is not None and not isinstance(mummy, str):
        raise TypeError("Type of argument \"mummy\" is not valid, expected string, got {0}.".format(type(mummy).__name__))
    if muscles is not None and not isinstance(muscles, (str, list)):
        raise TypeError("Type of argument \"muscles\" is not valid, expected string or list, got {0}.".format(type(muscles).__name__))
    if fascia is not None and not isinstance(fascia, str):
        raise TypeError("Type of argument \"fascia\" is not valid, expected string, got {0}.".format(type(fascia).__name__))
    if fat is not None and not isinstance(fat, str):
        raise TypeError("Type of argument \"fat\" is not valid, expected string, got {0}.".format(type(fat).__name__))
    if skin is not None and not isinstance(skin, str):
        raise TypeError("Type of argument \"skin\" is not valid, expected string, got {0}.".format(type(skin).__name__))
    if glue_group_name is not None and not isinstance(glue_group_name, str):
        raise TypeError("Type of argument \"glue_group_name\" is not valid, expected string, got {0}.".format(type(glue_group_name).__name__))
    if locators_group_name is not None and not isinstance(locators_group_name, str):
        raise TypeError("Type of argument \"locators_group_name\" is not valid, expected string, got {0}.".format(type(locators_group_name).__name__))
    if space_scale <= 1e-6:
        raise ValueError("Space scale zero or negative is not allowed.")

    meshes = {
        TurboFeatures.MUMMY: get_layer_meshes(mummy, TurboFeatures.MUMMY),
        TurboFeatures.MUSCLES: get_layer_meshes(muscles, TurboFeatures.MUSCLES),
        TurboFeatures.FASCIA: get_layer_meshes(fascia, TurboFeatures.FASCIA),
        TurboFeatures.FAT: get_layer_meshes(fat, TurboFeatures.FAT),
        TurboFeatures.SKIN: get_layer_meshes(skin, TurboFeatures.SKIN)
    }

    matches = {
        TurboFeatures.MUMMY: set(),
        TurboFeatures.MUSCLES: set(),
        TurboFeatures.FASCIA: set(),
        TurboFeatures.FAT: set(),
        TurboFeatures.SKIN: set()
    }

    for feature, feat_meshes in meshes.items():
        if not feat_meshes:
            continue
        for other_feature, other_feat_meshes in meshes.items():
            if feature == other_feature or not other_feat_meshes:
                continue
            for mesh in feat_meshes:
                if mesh in other_feat_meshes:
                    matches[feature].add(other_feature)
                    matches[other_feature].add(feature)

    # Store the selection to restore it before returning
    selection = cmds.ls(selection=True, long=True) or []

    if report_data is not None:
        if not isinstance(report_data, dict):
            report_data = None
            logging.warning("The AdnTurbo process will not report possible errors "
                            "or warnings because `report_data` argument is not valid.")
        else:
            report_data.clear()
            report_data["errors"] = []
            report_data["warnings"] = []

    if bool(get_plugin_nodes_in_scene()):
        if force:
            clear_scene()
        else:
            msg = ("The AdnTurbo process cannot be executed because there are AdonisFX nodes "
                   "in the scene. Please clear the scene (go to AdonisFX menu > Utils > Clear) "
                   "before running this process or enable the `force` flag and try again. "
                   "Any intermediate node will not be deleted.")
            add_to_report(report_data, "errors", msg)
            cmds.select(selection)
            return

    if not mummy:
        msg = ("Could not execute AdnTurbo because a skeletal mesh (i.e. mummy geometry) is "
               "required but was not provided. AdnTurbo skipped.")
        add_to_report(report_data, "errors", msg)
        cmds.select(selection)
        return

    if not cmds.objExists(mummy):
        msg = ("Could not execute AdnTurbo because the object \"{0}\" provided as skeletal "
               "mesh (i.e. mummy geometry) does not exist. AdnTurbo skipped.").format(mummy)
        add_to_report(report_data, "errors", msg)
        cmds.select(selection)
        return

    # If this call returns more than one object, it means that there are multiple
    # objects with the same name in the scene and the user provided the short name.
    long_name = cmds.ls(mummy, long=True)
    if len(long_name) > 1:
        long_name_str = ", ".join(['"{0}"'.format(name) for name in long_name])
        msg = ("Could not execute AdnTurbo because more than one skeletal mesh (i.e. mummy "
               "geometry) was found in \"{0}\": {1}. AdnTurbo skipped.").format(mummy, long_name_str)
        add_to_report(report_data, "errors", msg)
        return None

    mummy_geo = get_mesh(mummy)
    if len(mummy_geo) == 0:
        msg = ("Could not find a valid mesh in the object \"{0}\" provided as skeletal mesh "
               "(i.e. mummy geometry). AdnTurbo skipped.").format(mummy)
        add_to_report(report_data, "errors", msg)
        cmds.select(selection)
        return
    if len(mummy_geo) > 1:
        msg = ("More than one mesh was found in the object \"{0}\" provided as skeletal mesh "
               "(i.e. mummy geometry), but only one is allowed. AdnTurbo skipped.").format(mummy)
        add_to_report(report_data, "errors", msg)
        cmds.select(selection)
        return
    mummy_geo = mummy_geo[0]

    # Check duplicated usage
    features_to_check = [TurboFeatures.MUMMY]
    if not check_duplicated_usage(TurboFeatures.MUSCLES, features_to_check,
                                  meshes, matches, report_data=report_data):
        return

    glue_geo, muscles_created = turbo_muscles(mummy_geo, muscles, glue=glue,
                                              glue_group_name=glue_group_name,
                                              create_glue_group=create_glue_group,
                                              locators=locators,
                                              locators_group_name=locators_group_name,
                                              create_locators_group=create_locators_group,
                                              space_scale=space_scale,
                                              report_data=report_data)

    # If the muscles were not created, there was an error that was already reported, just return.
    # If muscles were created, the glue flag was set to True but the glue geometry
    # was not created, there was an error that was already reported, just return.
    if not muscles_created or (muscles_created and glue and not glue_geo):
        cmds.select(selection)
        return

    # If the geometries for the next layers are not provided, just return
    if not fascia and not fat and not skin:
        cmds.select(selection)
        return

    if not glue:
        msg = ("Could not configure fascia because the glue flag was set to False. "
               "AdnTurbo can't proceed with the downstream layers.")
        add_to_report(report_data, "errors", msg)
        cmds.select(selection)
        return

    # Check duplicated usage
    features_to_check = [TurboFeatures.MUMMY, TurboFeatures.MUSCLES]
    if not check_duplicated_usage(TurboFeatures.FASCIA, features_to_check,
                                  meshes, matches, report_data=report_data):
        return

    fascia_geo = turbo_fascia(mummy_geo, glue_geo, fascia,
                              space_scale=space_scale,
                              report_data=report_data)
    if not fascia_geo:
        cmds.select(selection)
        return

    # If the geometries for the next layers are not provided, just return
    if not fat and not skin:
        cmds.select(selection)
        return

    # Check duplicated usage
    features_to_check = [TurboFeatures.MUMMY, TurboFeatures.MUSCLES, TurboFeatures.FASCIA]
    if not check_duplicated_usage(TurboFeatures.FAT, features_to_check,
                                  meshes, matches, report_data=report_data):
        return

    fat_geo = turbo_fat(fascia_geo, fat,
                        space_scale=space_scale,
                        report_data=report_data)
    if not fat_geo:
        cmds.select(selection)
        return

    # If the geometry for the next layer is not provided, just return
    if not skin:
        cmds.select(selection)
        return

    # Check duplicated usage
    features_to_check = [TurboFeatures.MUMMY, TurboFeatures.MUSCLES,
                         TurboFeatures.FASCIA, TurboFeatures.FAT]
    if not check_duplicated_usage(TurboFeatures.SKIN, features_to_check,
                                  meshes, matches, report_data=report_data):
        return

    skin_geo = turbo_skin(fat_geo, skin,
                          space_scale=space_scale,
                          report_data=report_data)
    if not skin_geo:
        cmds.select(selection)
        return

    cmds.select(selection)
