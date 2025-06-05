import sys 

import maya.cmds as cmds
import maya.OpenMayaUI as OpenMayaUI
import maya.OpenMaya as OpenMaya
import maya.mel as mel

import adn.tools.maya.attribute_handlers as attr_handler

from adn.utils.constants import UiConstants, DeformerTypes, DebugDataDescriptor, UiConstants
from adn.utils.maya.undo_stack import undo_chunk, undo_disabled


class PaintToolBrush:
    """Paint brush style. Represents all the brushes the paint tool
    will handle.
    """
    GAUSS = "gaussian"
    POLY = "poly"
    SOLID = "solid"
    SQUARE = "square"


class PaintToolMode:
    """Weigh painting mode. Represents all paint operation modes the
    tool has.
    """
    ABSOLUTE = "absolute"
    ADDITIVE = "additive"
    SCALE = "scale"
    SMOOTH = "smooth"

    paint_mode = {
        ABSOLUTE: 0,
        ADDITIVE: 1,
        SCALE: 2,
        SMOOTH: 3
    }


class PaintToolReflectionAxis:
    """Reflection axis. The three axis the reflection can be."""
    X = "x"
    Y = "y"
    Z = "z"


class PaintToolSettings:
    """ Contains constants/settings used at the painting tool.
    """
    # Presets for the paint tool parameters with default parameters.
    DEFAULT_PRESET = {
        "intensity": 1.0,
        "lower_radius": 0.001,
        "upper_radius": 1.0,
        "opacity": 1.0,
        "screen_proj": False,
        "reflection": False,
        "reflection_origin": False,
        "stamp_spacing": 0.1,
        "paint_mode": PaintToolMode.ABSOLUTE,
        "brush_shape": PaintToolBrush.POLY,
        "reflection_axis": PaintToolReflectionAxis.X
    }


@undo_chunk
def create_weights_display_node(deformer_node=None):
    """Auxiliary function to create dynamically on demand the
    AdnWeightsDisplayNode and connect it to the current selection which should
    have an AdonisFX deformer previously assigned.

    Args:
        deformer_node (str, optional): Name of the deformer to connect the
            weights display node created to. It is an optional argument to
            ensure backward compatibility. Defaults to None.

    Returns:
        str: Name of the display node if created. None if not created.
    """
    raise DeprecationWarning("Function 'create_weights_display_node' is deprecated")


@undo_chunk
def remove_all_weights_display_nodes():
    """Auxiliary function to remove all AdnWeightsDisplayNode from the scene.

    Returns:
        bool: True if all AdnWeightsDisplayNode were removed successfully.
            False otherwise.
    """
    display_nodes = cmds.ls(type="AdnWeightsDisplayNode")
    if not display_nodes:
        return True

    # Check playback status to make safe deletes
    play_status = cmds.play(query=True, state=True)
    if play_status:
        cmds.play(state=False)

    node_types = cmds.AdnPaintDataCommand(query=True, deformerType=True) or []
    for display_node in display_nodes:
        if cmds.referenceQuery(display_node, isNodeReferenced=True):
            # Do not remove the node if it is referenced
            continue

        node_history = cmds.listHistory(display_node)
        deformer_nodes = [x for x in node_history if
                          cmds.nodeType(x) in node_types]
        if not deformer_nodes:
            # No Adn deformer, we can just remove the display node and continue
            cmds.delete(display_node)
            continue

        deformer_node = deformer_nodes[0]
        # Disconnect any possible connection
        display_in_mesh = "{0}.inMesh".format(display_node)
        current_influence = "{0}.currentInfluence".format(display_node)

        attr_handler.disconnect_attribute_from_source(display_in_mesh)
        attr_handler.disconnect_attribute_from_source(current_influence)

        # Remake the connections and delete node
        destination_connections = cmds.listConnections(
            "{0}.outMesh".format(display_node),
            destination=True, plugs=True)
        for dst_conn in destination_connections:
            cmds.connectAttr("{0}.outputGeometry[0]".format(deformer_node),
                             dst_conn, force=True)

        cmds.delete(display_node)
        print("{0} Deprecated '{1}' removed successfully."
              "".format(UiConstants.INFO_PREFIX, display_node))

    # Restore playback status
    if play_status:
        cmds.play(state=True)

    display_nodes = cmds.ls(type="AdnWeightsDisplayNode")
    if display_nodes:
        print("{0} Could not remove deprecated AdnWeightsDisplayNodes: {1}."
              "".format(UiConstants.INFO_PREFIX, display_nodes))
        return False

    return True


def assign_default_material(mesh_node):
    """Switch to a default material in case the mesh element sent was not using the default
    "initialShadingGroup". The original shading group from the object will be returned.

    Args:
        mesh_node (str): Mesh node name.

    Returns:
        str: Node UUID of the original shading group node if possible,
            None otherwise.
    """
    shading_group_uuid = None

    if not mesh_node:
        return None

    painted_obj = cmds.ls(mesh_node, long=True, dag=True, objectsOnly=True, shapes=True)
    if not painted_obj:
        return None
    painted_obj = painted_obj[0]
    shading_group = list(set(cmds.listConnections(painted_obj, type="shadingEngine") or []))

    if not shading_group:
        return None

    shading_group = shading_group[0]
    shading_group_uuid = cmds.ls(shading_group, uuid=True)
    shading_group_uuid = shading_group_uuid[0] if shading_group_uuid else None
    init_shading_group_uuid = cmds.ls("initialShadingGroup", uuid=True)
    init_shading_group_uuid = init_shading_group_uuid[0] if init_shading_group_uuid else None

    # Check if current material is different from default one.
    if not shading_group_uuid or shading_group_uuid == init_shading_group_uuid:
        return None

    # noWarning flag added since elements of the rig might not totally accept
    # the set change but allow it
    cmds.sets(painted_obj, edit=True, forceElement="initialShadingGroup", noWarnings=True)
    return shading_group_uuid


def restore_material(mesh_node, shading_group_uuid):
    """Attempts to restore the given shading group to the given mesh. This assignment is applied
    only if the current shading group of that mesh is the default one.

    Args:
        mesh_node (str): Mesh node to change the material from.
        shading_group_uuid (str): UUID of the original shading node.

    Returns:
        bool: False if there was an error. True otherwise.
    """
    if not shading_group_uuid or not mesh_node:
        return True
    mesh_node_long_name = cmds.ls(mesh_node, long=True, dag=True, objectsOnly=True, shapes=True)
    if not mesh_node_long_name:
        return True
    mesh_node_long_name = mesh_node_long_name[0]

    current_shading_group = cmds.listConnections(mesh_node_long_name, type="shadingEngine")
    if not current_shading_group:
        return True
    current_shading_group_uuid = cmds.ls(current_shading_group, uuid=True)
    current_shading_group_uuid = current_shading_group_uuid[0] if current_shading_group_uuid else None
    init_shading_group_uuid = cmds.ls("initialShadingGroup", uuid=True)
    init_shading_group_uuid = init_shading_group_uuid[0] if init_shading_group_uuid else None
    data_check = current_shading_group_uuid and shading_group_uuid
    if not data_check or current_shading_group_uuid != init_shading_group_uuid:
        return True

    original_shading_group = cmds.ls(shading_group_uuid, long=True)
    if not original_shading_group:
        print("{0} Failed to restore the original shading group. The shading group provided could not "
              "be found."
              "".format(UiConstants.ERROR_PREFIX))
        return False
    original_shading_group = original_shading_group[0]

    # noWarning flag added since elements of the rig might not totally accept
    # the set change but allow it.
    cmds.sets(mesh_node_long_name, edit=True, forceElement=original_shading_group, noWarnings=True)
    return True


@undo_disabled
def display_paint(mesh_node, enable, current_shading_group_uuid, poly_option):
    """Toggles on or off the display colors of the mesh sent. At the same time, switch the
    materials if needed.

    Args:
        mesh_node (str): Mesh node to change colors.
        enable (bool): Flag that represents if colors has to be displayed or not.
        current_shading_group_uuid (str): Cached node UUID of the original shading node.
        poly_option  (str): Current stored colorMaterialChannel poly option. 
            Can be: none, ambient, ambientDiffuse, diffuse, specular, emission.

    Returns:
        str: UUID of the original shading node if the material has been
            switched, None otherwise.
        str: Previous polyOption colorMaterialChannel state before
            switching to colorMaterialChannel "none". Defaults to "none".
        bool: False if there was an error. True otherwise.
    """
    success = True
    if not mesh_node:
        return None, None, success
    
    found = cmds.ls(mesh_node)
    if not found:
        return None, None, success
    
    shading_group_uuid = None
    previous_poly_option = "none"

    if enable:
        if not current_shading_group_uuid:
            # Switch material
            shading_group_uuid = assign_default_material(mesh_node)
        else:
            # Material already switched
            shading_group_uuid = current_shading_group_uuid
        # Get the colorMaterialChannel of the painted mesh
        previous_poly_option = cmds.polyOptions(mesh_node,
                                                colorMaterialChannel=True,
                                                query=True)[-1]
        cmds.polyOptions(mesh_node, colorMaterialChannel="none")
    else:
        # Restore material
        success = restore_material(mesh_node, current_shading_group_uuid)
        cmds.polyOptions(mesh_node, colorMaterialChannel=poly_option)

    # Toggle display colors
    selection_list = OpenMaya.MSelectionList()
    selection_list.add(mesh_node)
    node_dag_path = OpenMaya.MDagPath()
    selection_list.getDagPath(0, node_dag_path)
    mesh_fn = OpenMaya.MFnMesh(node_dag_path)

    mesh_fn.setDisplayColors(enable)

    return shading_group_uuid, previous_poly_option, success


def collect_paint_tool_nodes(selection):
    """Collects the nodes needed for the paint tool based on 
    the selection.

    Args: 
        selection (`MObject`): Selected mesh that we are going to paint.

    Returns:
        str: Name of the deformer node.
        str: Type of the deformer node.
        str: Name of the selected mesh node.
        dict: Dictionary with the message to be displayed if errors ocurred and
              the level of the error. Returns None if no errors happened.
    """
    # REMINDER: Add paintable nodes
    paint_tool_paintable_nodes = [DeformerTypes.MUSCLE,
                                  DeformerTypes.RIBBON,
                                  DeformerTypes.SKIN]
    deformer_node = None
    node_type = None
    mesh_node = None
    error_dict = dict()
    error_dict["error_level"] = "error"
    error_dict["error_msg"] = "Please, select a geometry with an AdonisFX " \
                              "paintable deformer and try again. Make sure that " \
                              "the deformer to paint is enabled."
    node_history = list()

    if not selection:
        return deformer_node, node_type, mesh_node, error_dict

    # For collecting the paint tool nodes, we evaluate the last item in the
    # selection to make sure that we construct the paintable context
    # based on the right geometry. This is especially needed for when
    # there are influences included in the selection, where those influences
    # are added to the beginning of the selection list, and the desired
    # paintable surface is at the end of the list
    selection = selection[-1]

    # Get the shapes
    shape_nodes = cmds.listRelatives(selection, shapes=True, fullPath=True)
    if not shape_nodes:
        return deformer_node, node_type, mesh_node, error_dict

    # Get the deformer node
    adn_node_types = cmds.AdnPaintDataCommand(query=True, deformerType=True) or []
    for shape_node in shape_nodes:
        node_history = cmds.deformableShape(shape_node, nodeChain=True) or []
        # Filter by Adonis nodes
        adn_nodes_in_history = [x for x in node_history if cmds.objExists(x) and cmds.nodeType(x) in adn_node_types]
        if adn_nodes_in_history:
            # Filter by Adonis nodes that are paintable by our paint tool
            paintable_nodes = [x for x in adn_nodes_in_history if cmds.nodeType(x) in paint_tool_paintable_nodes]
            if not paintable_nodes:
                deformer_node = adn_nodes_in_history[0]
                node_type = cmds.nodeType(deformer_node)
                error_dict["error_msg"] = "The selected deformer does not " \
                                          "require the AdonisFX Paint Tool. " \
                                          "You may use the standard Maya " \
                                          "Paint Context."
                error_dict["error_level"] = "warning"
                return deformer_node, node_type, mesh_node, error_dict

            deformer_node = paintable_nodes[0]
            node_type = cmds.nodeType(deformer_node)
            # Deformer found and paintable. Edit paint command.
            cmds.AdnPaintDataCommand(edit=True, deformerType=node_type)
            break

    # Check if we found the deformer
    if not deformer_node:
        return deformer_node, node_type, mesh_node, error_dict

    # Check if deformer is initialized
    if not cmds.AdnPaintDataCommand(deformer_node, query=True, initializedDeformer=True):
        return deformer_node, node_type, mesh_node, error_dict

    # Get the mesh
    mesh_nodes = [x for x in node_history if cmds.nodeType(x) == "mesh"]
    if mesh_nodes:
        mesh_node = mesh_nodes[-1]
    else:
        return deformer_node, node_type, mesh_node, error_dict

    return deformer_node, node_type, mesh_node, None


def setup_paint_tool(parent):
    """Gathers the nodes and makes the connections to make the 
    AdonisFX deformer paintable based on the selected mesh.

    Args: 
        parent (:obj:`QtWidgets.QWindow`): Widget to parent dialogs to.

    Returns:
        bool: All sanity checks passed.
        str: Name of the deformer node.
        str: Node type name.
        list: List of paintable attributes.
        list: List of multi influence paintable attributes.
        str: Mesh node of the selection.
    """
    current_selection = cmds.ls(selection=True, long=True)

    # At least one object selected
    if not current_selection:
        print("{0} Selection is empty. Please, select "
              "the transform node of a mesh with an AdonisFX "
              "deformer assigned to and try again."
              "".format(UiConstants.ERROR_PREFIX))
        return False, None, None, None, None, None

    # node_type is not used now, but might be needed when we support more deformers
    deformer_node, node_type, mesh_node, error_dict = \
        collect_paint_tool_nodes(current_selection)

    if error_dict:
        print("{0} {1}"
              "".format(UiConstants.ERROR_PREFIX, error_dict["error_msg"]))
        return False, None, None, None, None, None

    # Get a list of the attributes used in this deformer and check if it is an unsupported deformer.
    paintable_attr = cmds.AdnPaintDataCommand(query=True, attributes=True) or []
    # Get a list of the multi influence attributes used in this deformer.
    multi_infl_attr = cmds.AdnPaintDataCommand(query=True, multiInflAttributes=True) or []

    cmds.select(current_selection)

    return True, deformer_node, node_type, paintable_attr, multi_infl_attr, mesh_node
    
    
def create_mel_procedure(python_method, args=[], return_type=""):
    """Create a MEL procedure which calls a custom Python function. This method will be necessary to
    not create additional commands that can be handle and do not affect that much the performance
    using python.

    Args:
        python_method (Python method reference): Reference to the python method.
        args (list, optional): List of the types of arguments the python method has. Defaults to [].
        return_type (str, optional): Type of the return of the method. Defaults to "".

    Returns:
        str: Mel procedure name.
    """
    proc_name = "adnMelProcedure{0}{1}".format(id(python_method), python_method.__name__)
    sys.modules["__main__"].__dict__[proc_name] = python_method
    mel_args = ",".join(map(lambda a:"{0} ${1}".format(a[0], a[1]), args))
    python_args = ",".join(map(lambda a:'\'"+ ${0}+"\''.format(a[1]), args))
    return_stmt = "return" if return_type != "" else return_type
    melCode = ("global proc {0} {1}({2}) "
                "{{ {3} python(\"{4}({5})\"); }}").format(return_type, proc_name,
                                                          mel_args, return_stmt,
                                                          proc_name, python_args)
    mel.eval(melCode)
    return proc_name


def get_closest_index_dragger_context(dragger_context, deformer, mesh):
    """Return the closest vertex index based on the dragger context.
    Steps:
        - Get point selected on screen
        - Get points on mesh
        - Get the closest vertex on the mesh

    Args:
        dragger_context (str): Name of the dragger context.
        deformer (str): Name of the deformer node being painted.
        mesh (str): Name of the mesh node that is selected and being painted.

    Returns:
        int: closest vertex index selected. It returns -1 if the method aborts.
    """
    # Get point on screen
    press_position = cmds.draggerContext(dragger_context, query=True, anchorPoint=True)
    if len(press_position) < 2:
        print("{0} Failed to get anchor point where the dragger was pressed."
              "".format(UiConstants.LOG_PREFIX))
        return -1
    x = int(press_position[0])
    y = int(press_position[1])

    # Create rays
    ray_source = OpenMaya.MPoint()
    ray_direction = OpenMaya.MVector()
    active_view = OpenMayaUI.M3dView.active3dView()
    active_view.viewToWorld(x, y, ray_source, ray_direction)
    OpenMaya.MGlobal.selectFromScreen(x, y, OpenMaya.MGlobal.kReplaceList)
    selection_list = OpenMaya.MSelectionList()
    OpenMaya.MGlobal.getActiveSelectionList(selection_list)

    # Check selection
    current_selection = cmds.ls(selection=True, long=True)
    deformer_node, node_type, mesh_selected, _ = collect_paint_tool_nodes(current_selection)
    if selection_list.length() == 0 or deformer_node != deformer or mesh_selected != mesh:
        # Wrong selection
        print("{0} Invalid selection from screen: nothing selected or the selected node is not "
              "a mesh with paintable maps.".format(UiConstants.LOG_PREFIX))
        return -1

    # Get closest vertex on mesh
    mesh_dag = OpenMaya.MDagPath()
    selection_list.getDagPath(0, mesh_dag)
    mesh_fn = OpenMaya.MFnMesh(mesh_dag)
    hit_float_point = OpenMaya.MFloatPoint()
    ray_source_float = OpenMaya.MFloatPoint(ray_source.x, ray_source.y, ray_source.z)
    ray_direction_float = OpenMaya.MFloatVector(ray_direction.x, ray_direction.y, ray_direction.z)
    face_idx_util = OpenMaya.MScriptUtil()
    face_idx_util.createFromInt(-1)
    face_int_ptr = face_idx_util.asIntPtr()

    mesh_intersected = mesh_fn.closestIntersection(
        ray_source_float,         # raySource
        ray_direction_float,      # rayDirection
        None,                     # faceIds
        None,                     # triIds
        False,                    # idsSorted
        OpenMaya.MSpace().kWorld, # space
        9999,                     # maxParam
        False,                    # testBothDirections
        None,                     # accelParams
        hit_float_point,          # hitPoint
        None,                     # hitRayParam
        face_int_ptr,             # hitFace
        None,                     # hitTriangle
        None,                     # hitBary1
        None,                     # hitBary2
        0.000001)                 # tolerance

    if not mesh_intersected:
        print("{0} Could not find a valid closest intersection from the ray "
              "source.".format(UiConstants.LOG_PREFIX))
        return -1

    # Get closest vertex index
    face_idx = face_idx_util.getInt(face_int_ptr)
    if face_idx > mesh_fn.numPolygons() or face_idx < 0:
        print("{0} Invalid face found from the closest intersection "
              "operation.".format(UiConstants.LOG_PREFIX))
        return -1

    vertices_selected = OpenMaya.MIntArray()
    mesh_fn.getPolygonVertices(face_idx, vertices_selected)
    if len(vertices_selected) == 0:
        print("{0} Invalid list of vertices found from the closest "
              "intersection operation.".format(UiConstants.LOG_PREFIX))
        return -1

    hit_point = OpenMaya.MPoint(hit_float_point)
    current_point = OpenMaya.MPoint()
    closest_vertex = -1
    closest_length = float("inf")
    for idx in range(0, vertices_selected.length()):
        mesh_fn.getPoint(vertices_selected[idx], current_point)
        current_length = hit_point.distanceTo(current_point)
        if current_length < closest_length:
            closest_vertex = vertices_selected[idx]
            closest_length = current_length

    return closest_vertex


def debug_fibers_on_painting(deformer):
    """Enable fiber debugging as the user is using the paint tool to
    comb fibers. At the same time, gathers and returns the debug values
    in order to restore them after the combing.

    Args:
        deformer (str): name of the deformer node that we are going to
            tweak its attributes

    Returns:
        bool: previous state of the 'debug' flag of the deformer.
            Defaults to False.
        int: numeric value for the feature that was set to debug.
            Defaults to -1.
    """
    # Get the previous flags and update the values
    debug_flag = False
    debug_attribute = "{0}.debug".format(deformer)
    if cmds.objExists(debug_attribute):
        debug_flag = cmds.getAttr(debug_attribute)
        cmds.setAttr(debug_attribute, True)

    debug_feature = -1
    debug_feature_attribute = "{0}.debugFeature".format(deformer)
    if cmds.objExists(debug_feature_attribute):
        debug_feature = cmds.getAttr(debug_feature_attribute)
        # Reference number for fibers is defined in DebugDataDescriptor.kMuscleFibers
        cmds.setAttr(debug_feature_attribute, DebugDataDescriptor.kMuscleFibers)

    return debug_flag, debug_feature


def restore_debug_attributes(deformer, prev_debug_flag, prev_debug_feature):
    """Restore the debug attributes from the deformer sent as the user is
    no longer combing fibers. If the user, during the fiber combing, tweaked
    any debug parameter the restore process will be aborted.

    Args:
        deformer (str): name of the deformer node that we are going to
            restore its attributes
        prev_debug_flag (bool): previous state of the debug variable.
        prev_debug_feature (int): previous value of the debug feature variable.
    """
    if prev_debug_feature == -1:
        # Nothing to restore. User was not combing fibers.
        return

    debug_attribute = "{0}.debug".format(deformer)
    debug_feature_attribute = "{0}.debugFeature".format(deformer)
    attributes_available = (cmds.objExists(debug_attribute) and
                            cmds.objExists(debug_feature_attribute))

    if (not attributes_available or
            not cmds.getAttr(debug_attribute) or
            cmds.getAttr(debug_feature_attribute) != DebugDataDescriptor.kMuscleFibers):
        # Reference number for fibers is defined in DebugDataDescriptor.kMuscleFibers
        # Attribute not available or user tweaked one debug attribute
        # so restore operation is aborted
        return

    # NOTE: Debug features might be out of range if we added new entries.
    # Make sure to avoid restoring any previous state if the feature is not available.
    try:
        cmds.setAttr(debug_attribute, prev_debug_flag)
        cmds.setAttr(debug_feature_attribute, prev_debug_feature)
    except:
        pass


@undo_disabled
def select_multi_influence_obj(selected_item):
    """Selects an multi-influence object while making this selection not undoable.

    Args:
        selected_item (str): Name of the multi-influence object to select.
    """
    # Support slide on segment anchors selection
    selected_item = selected_item.split(" - ")
    sel = cmds.ls(selection=True)
    if len(sel) == 1:
        cmds.select(selected_item, addFirst=True)
    elif len(sel) > 1:
        cmds.select(selected_item + [sel[-1]], replace=True)


@undo_disabled
def select_debug_locator():
    """Adds all the AdnDebugLocator nodes found in the scene to the selection."""
    debug_locators = cmds.ls(type="AdnDebugLocator")
    if not debug_locators:
        return
    # Add all AdnDebugLocator nodes to the selection
    cmds.select(debug_locators, addFirst=True)


def toggle_display_weight(node_name, value):
    """Enables or disabled the displayWeights attribute of the given node.
    This method ensures that the paintable node is ready to color the
    vertices while using the paint tool.

    Args:
        node_name (str): name of the paintable node to modify.
        value (bool): new status to set to the displayWeights attribute.
    """
    attribute = "{0}.displayWeights".format(node_name)
    if cmds.objExists(attribute):
        cmds.setAttr(attribute, value)


def get_on_low_init_only_paintable_attributes():
    """Return the paintable attributes only valid at the lowest init time.
    The lowest init time is the lowest of preroll start time and start time.

    Returns:
        list: paintable attributes only at the lowest initialization time.
    """
    return cmds.AdnPaintDataCommand(query=True, lowInitOnlyAttributes=True) or []
