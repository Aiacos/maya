import maya.cmds as cmds

from adn.ui.widgets.dialogs import msg_box
from adn.ui.maya.window import main_window
from adn.ui.utils import cursor
from adn.utils.maya.undo_stack import undo_chunk
from adn.utils.constants import DeformerTypes
from adn.utils.maya.checkers import plugin_check


def check_duplicates(anim_mesh_list, sim_mesh_list):
    """Check sim_mesh_list so that no mesh is also in anim_mesh_list.

    Args:
        anim_mesh_list (list): List of animation meshes.
        sim_mesh_list (list): List of simulation meshes.

    Returns:
        bool: True if there are no duplicates or if the user has decided to proceed with them.
              False if there are duplicates and the user has decided to abort the operation.
    """
    proceed = True
    # Check for duplicates in anim meshes
    if len(set(anim_mesh_list)) < len(anim_mesh_list):
        msg_box(main_window(), "error",
                "One or more meshes are duplicate in the animation meshes "
                "selection. Please make sure no elements are duplicate and try again.")
        return False
    # Check for duplicates in sim meshes
    if len(set(sim_mesh_list)) < len(sim_mesh_list):
        msg_box(main_window(), "error",
                "One or more meshes are duplicate in the simulations meshes "
                "selection. Please make sure no elements are duplicate and try again.")
        return False
    # Check for duplicates between meshes lists
    if any(mesh in sim_mesh_list for mesh in anim_mesh_list):
        proceed = msg_box(main_window(), "question",
                          "One or more meshes are included in both the animation and simulated meshes "
                          "selections. This may cause the AdnSkinMerge not to work as expected. "
                          "Do you want to proceed with these settings?.")
    return proceed


@undo_chunk
def create_skin_merge(name, final_mesh, anim_mesh_list, sim_mesh_list, start_time):
    """Create the AdnSkinMerge deformer and generate all necessary connections
    between nodes.

    Args:
        name (str): Name of the deformer.
        final_mesh (str): Name of final mesh.
        anim_mesh_list (list): List of animation meshes to merge.
        sim_mesh_list (list): List of simulation meshes to merge.
        start_time (int): Deformer start time.

    Returns:
        bool: True if the deformer has been created, false otherwise.
    """
    if not check_duplicates(anim_mesh_list, sim_mesh_list):
        return False

    with cursor.wait_cursor_context():
        cmds.select(final_mesh)
        deformer = cmds.deformer(type=DeformerTypes.SKIN_MERGE, name=name)[0]
        cmds.setAttr("{0}.initializationTime".format(deformer), start_time)
        # Set anim meshes
        for i, anim in enumerate(anim_mesh_list):
            cmds.connectAttr("{0}.worldMatrix[0]".format(anim),
                            "{0}.animList[{1}].animWorldMatrix".format(deformer, i))
            cmds.connectAttr("{0}.worldMesh[0]".format(anim),
                            "{0}.animList[{1}].animWorldMesh".format(deformer, i))
        # Set sim meshes
        for i, sim in enumerate(sim_mesh_list):
            cmds.connectAttr("{0}.worldMatrix[0]".format(sim),
                            "{0}.simList[{1}].simWorldMatrix".format(deformer, i))
            cmds.connectAttr("{0}.worldMesh[0]".format(sim),
                            "{0}.simList[{1}].simWorldMesh".format(deformer, i))

    # Creation dialog
    skin_merge_short_name = cmds.ls(deformer, shortNames=True)[0]
    msg_box(main_window(), "info",
            "\"{0}\" has been created successfully."
            "".format(skin_merge_short_name))

    return True


def create_default_skin_merge(mesh_name, node_name):
    """Create the most basic adnSkinMerge deformer. Only time attributes are
    configured for security reasons.

    Args:
        mesh_name (str): name of the geometry to create the deformer onto.
        node_name (str): tentative name for the node to create.

    Returns:
        str: resulting name of the created node.
    """
    with cursor.wait_cursor_context():
        # Deformer and connections
        deformer = cmds.deformer(mesh_name,
                                 type=DeformerTypes.SKIN_MERGE,
                                 name=node_name)[0]
        cmds.setAttr("{0}.initializationTime".format(deformer),
                     cmds.currentTime(query=True))

    return deformer


@undo_chunk
def edit_skin_merge(deformer, anim_mesh_list, sim_mesh_list):
    """Edit a AdnSkinMerge deformer and generate all necessary connections
    between nodes.

    Args:
        deformer (str): Name of the AdnSkinMerge deformer.
        anim_mesh_list (list): List of animation meshes to merge.
        sim_mesh_list (list): List of simulation meshes to merge.
        sim_mesh_list (int): Deformer start time.

    Returns:
        bool: True if the deformer has been edited, false otherwise.
    """
    if not check_duplicates(anim_mesh_list, sim_mesh_list):
        return False

    with cursor.wait_cursor_context():
        # Disconnect previous sim and anim meshes 
        for inputType in ["sim", "anim"]:
            mesh_attr = "{0}.{1}List".format(deformer, inputType)
            logical_indices = cmds.getAttr(mesh_attr, multiIndices=True) or []
            for index in logical_indices:
                full_attr_mesh = "{0}[{1}].{2}WorldMesh".format(mesh_attr, index, inputType)
                full_attr_matrix = "{0}[{1}].{2}WorldMatrix".format(mesh_attr, index, inputType)
                mesh_plugs = cmds.listConnections(full_attr_mesh, source=True, plugs=True) or []
                matrix_plugs = cmds.listConnections(full_attr_matrix, source=True, plugs=True) or []
                    
                for plug in mesh_plugs:
                    cmds.disconnectAttr(plug, full_attr_mesh)
                for plug in matrix_plugs:
                    cmds.disconnectAttr(plug, full_attr_matrix)

        # Set new anim meshes
        for i, anim in enumerate(anim_mesh_list):
            cmds.connectAttr("{0}.worldMatrix[0]".format(anim),
                            "{0}.animList[{1}].animWorldMatrix".format(deformer, i))
            cmds.connectAttr("{0}.worldMesh[0]".format(anim),
                            "{0}.animList[{1}].animWorldMesh".format(deformer, i))
        # Set new sim meshes
        for i, sim in enumerate(sim_mesh_list):
            cmds.connectAttr("{0}.worldMatrix[0]".format(sim),
                            "{0}.simList[{1}].simWorldMatrix".format(deformer, i))
            cmds.connectAttr("{0}.worldMesh[0]".format(sim),
                            "{0}.simList[{1}].simWorldMesh".format(deformer, i))
    
    # Edit complete dialog
    skin_merge_short_name = cmds.ls(deformer, shortNames=True)[0]
    msg_box(main_window(), "info",
            "Changes to \"{0}\" have been applied successfully."
            "".format(skin_merge_short_name))

    return True


def get_skin_merge_deformer():
    """Get the AdnSkinMerge deformer node from the selection.

    Returns:
        str: Name of AdnSkinMerge deformer from selection.
    """
    selection = cmds.ls(selection=True, long=True)
    message = "Please select a mesh with an AdnSkinMerge deformer applied to edit it."
    if not selection:
        msg_box(main_window(), "error", message)
        return None
    deformer_object = selection[-1]

    deformer_shape = cmds.listRelatives(deformer_object, shapes=True, fullPath=True) or []
    if not deformer_shape:
        msg_box(main_window(), "error", message)
        return None
    deformer_history = cmds.listHistory(deformer_shape[0])
    deformer_nodes = [x for x in deformer_history if cmds.nodeType(x) == DeformerTypes.SKIN_MERGE]
    if not deformer_nodes:
        msg_box(main_window(), "error", message)
        return None
    
    return deformer_nodes[0]


def get_skin_merge_data(deformer):
    """Get the AdnSkinMerge Data required.

    Args:
        deformer (str): Name of the AdnSkinMerge deformer.

    Returns:
        dict: Dictionary with 2 entries with the lists of anim meshes and sim meshes.
    """
    anim_mesh_attr = "{0}.animList".format(deformer)
    sim_mesh_attr = "{0}.simList".format(deformer)
    anim_mesh_connections = cmds.listConnections(anim_mesh_attr, destination=True) or []
    sim_mesh_connections = cmds.listConnections(sim_mesh_attr, destination=True) or []
    data = dict()
    data["animList"] = cmds.ls(set(anim_mesh_connections), long=True)
    data["simList"] = cmds.ls(set(sim_mesh_connections), long=True)

    return data