import maya.cmds as cmds

from adn.ui.widgets.dialogs import msg_box
from adn.ui.maya.window import main_window
from adn.utils.maya.licensing import check_license


def check_playback(deformer):
    """Check the playback status of the scene.

    Args:
        deformer (str): deformer node name.

    Returns:
        bool: check if we can interact with the deformer in the case we are
              at the start or prerroll frame and we are not in playback mode.
    """
    play_status = cmds.play(query=True, state=True)
    preroll_time = cmds.getAttr("{0}.prerollStartTime".format(deformer))
    start_time = cmds.getAttr("{0}.startTime".format(deformer))
    current_time = cmds.getAttr("{0}.currentTime".format(deformer))
    if play_status or preroll_time != current_time and start_time != current_time:
        msg_box(main_window(), "error",
                "Please, stop playback, move to preroll or start frame and try again.")
        return False
    return True


def scene_hierarchy_check(selection):
    """Check that all elements in the selection follow the scene hierarchy.
       The expected selection should be parentN > parent1 > leaf_node.
       It is not required that nodes have a direct parent to child relationship.

    Args:
        selection (list): Current selection in the scene hierarchy with long/fullpath names.
    
    Returns:
        bool: True if the selection follows the scene hierarchy. False otherwise.
    """
    if len(selection) <= 1:
        return False
    # Invert the selection to go from leaf to parent
    selection = selection[::-1]
    for i in range(0, len(selection) - 1):
        node = selection[i]
        parent = selection[i + 1]
        # Get a list of parent nodes from their names
        parents = cmds.ls(node, long=True)[0].split("|")[1:-1]
        parents_long_named = ["|".join(parents[:j]) for j in range(1, 1 + len(parents))][::-1]
        # If the selected parent node is not in the parent list mark the selection as invalid
        if parent[1:] not in parents_long_named:
            return False
    return True


def scene_parent_check(selection):
    """Check that all elements in the selection follow a parent to child relationship
    within the selection.

    Args:
        selection (list): Current selection in the scene hierarchy with long/fullpath names.
    
    Returns:
        bool: True if the selection follows the scene parent to child hierarchy. False otherwise.
    """
    if len(selection) <= 1:
        return False
    # Invert the selection to go from leaf to parent
    selection = selection[::-1]
    for i in range(0, len(selection) - 1):
        node = selection[i]
        parent = selection[i + 1]
        # Get a list of parents nodes from their names
        parents = cmds.listRelatives(node, parent=True, fullPath=True) or []
        if not parents:
            return False
        if cmds.ls(parents, long=True)[0] != parent:
            return False
    return True


def plugin_check():
    """Evaluate the status of the AdonisFX plugin to check if its nodes and
    features can be used. If this evaluation fails, RuntimeErrors are raised.

    Raises:
        RuntimeError: If AdonisFX Plugin is not loaded.
        RuntimeError: If AdonisFX license could not be verified.
    """
    if not cmds.pluginInfo("AdonisFX", query=True, loaded=True):
        raise RuntimeError("AdonisFX not loaded, "
                           "please load the plugin and try again.")
    if not check_license():
        raise RuntimeError("AdonisFX license not validated, "
                           "please activate your license and try again.")


def world_matrix_plug_check(nodes):
    """Check if a list of nodes or single node have a worldMatrix plug.

    Args:
        nodes (str or list): node name or list of node names to check.
    
    Returns:
        bool: True if all nodes provided have a `worldMatrix` plug. False otherwise.
    """
    nodes = [nodes] if type(nodes) == str else nodes
    return all([cmds.objExists("{0}.worldMatrix".format(node)) for node in nodes])


def deformer_being_painted(deformer):
    """Check if the given deformer is currently being painted.

    Args:
        deformer (str): deformer node name.
    
    Returns:
        bool: True if the deformer is currently being painted. False otherwise.
    """
    if cmds.currentCtx() != "AdnPaintToolContext":
        return False
    painted_deformer = cmds.AdnPaintDataCommand(query=True, deformer=True)
    return painted_deformer == deformer
