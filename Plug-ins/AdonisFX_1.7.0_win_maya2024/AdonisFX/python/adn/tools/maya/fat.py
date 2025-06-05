import maya.cmds as cmds

from adn.utils.constants import DeformerTypes
from adn.utils.maya.undo_stack import undo_chunk
from adn.utils.maya.checkers import plugin_check
from adn.tools.maya import locators
from adn.ui.widgets.dialogs import UiConstants
from adn.ui.utils import cursor


@undo_chunk
def apply_fat(custom_name=None, start_time=None, stiffness=1e3, iterations=5, gravity=0.0, damping=0.1):
    """ Create the fat deformer and configure the main attributes with the given argument values.

    Args:
        custom_name (str, optional): Custom name to give to the deformer. Defaults to None.
        start_time (float, optional): Frame number for initialization. Defaults to None.
        stiffness (float, optional): Material stiffness. Defaults to 1e3.
        iterations (int, optional): Number of solver iterations for a simulation step. Defaults to 5.
        gravity (float, optional): Magnitude of the gravity. Defaults to 0.0.
        damping (float, optional): Global damping value. Defaults to 0.1.

    Returns:
        str: Name of the created fat deformer if created correctly.
        bool: False if there was an error. True otherwise.
    """
    plugin_check()
    deformer = ""
    selection = cmds.ls(selection=True, dagObjects=True, type="mesh", noIntermediate=True)
    if len(selection) != 1 and len(selection) != 2:
        print("{0} Wrong number of meshes selected ({1}). "
              "Please, select in the following order: "
              "1) [optional] base mesh to guide the fat, "
              "2) mesh to apply the fat solver to."
              "".format(UiConstants.ERROR_PREFIX, len(selection)))
        return deformer, False

    # Check deformers applied to the selection
    applied_deformers = cmds.findDeformers(selection[-1]) or []
    short_name = cmds.ls(selection[-1], long=False)
    for applied_deformer in applied_deformers:
        if cmds.nodeType(applied_deformer) == DeformerTypes.FAT:
            print("{0} The selected mesh ({1}) has already an {2} deformer "
                  "node applied to. Aborting creation."
                  "".format(UiConstants.WARNING_PREFIX, short_name[0], DeformerTypes.FAT))
            return deformer, True

    connect_to_debugger_success = True
    with cursor.wait_cursor_context():
        node = selection[-1]
        base_node = selection[-2] if len(selection) == 2 else None
        if base_node:
            if not check_base_mesh(base_node, node):
                return deformer, False

        cmds.select(node)
        deformer = (cmds.deformer(type=DeformerTypes.FAT)[0] if not custom_name else
                    cmds.deformer(type=DeformerTypes.FAT, name=custom_name)[0])

        # Configure attributes
        cmds.setAttr("{0}.prerollStartTime".format(deformer), start_time or cmds.currentTime(query=True))
        cmds.setAttr("{0}.startTime".format(deformer), start_time or cmds.currentTime(query=True))
        cmds.setAttr("{0}.stiffness".format(deformer), stiffness)
        cmds.setAttr("{0}.gravity".format(deformer), gravity)
        cmds.setAttr("{0}.iterations".format(deformer), iterations)
        cmds.setAttr("{0}.globalDampingMultiplier".format(deformer), damping)

        # Main connections
        cmds.connectAttr("time1.outTime", "{0}.currentTime".format(deformer))

        if base_node:
            cmds.connectAttr("{0}.worldMatrix[0]".format(base_node), "{0}.baseMatrix".format(deformer))
            cmds.connectAttr("{0}.worldMesh[0]".format(base_node), "{0}.baseMesh".format(deformer))

        # Data node and Locator
        # This function may print an error message so we propagate whether
        # the function succeeded so that the error dialog is displayed.
        connect_to_debugger_success = locators.connect_to_debugger(deformer)
        # Restore selection
        cmds.select(selection)

    fat_deformer_short_name = cmds.ls(deformer, shortNames=True)[0]
    print("{0} \"{1}\" deformer has been created successfully."
          "".format(UiConstants.INFO_PREFIX, fat_deformer_short_name))

    return deformer, connect_to_debugger_success


def create_default_fat(mesh_name, node_name):
    """Create the most basic fat deformer. Only time attributes are
    configured for security reasons.

    Args:
        mesh_name (str): name of the geometry to create the deformer onto.
        node_name (str): tentative name for the node to create.

    Returns:
        str: resulting name of the created node.
        bool: False if there was an error. True otherwise.
    """
    connect_to_debugger_success = True
    with cursor.wait_cursor_context():
        # Deformer and connections
        deformer = cmds.deformer(mesh_name,
                                 type=DeformerTypes.FAT,
                                 name=node_name)[0]
        cmds.setAttr("{0}.prerollStartTime".format(deformer),
                     cmds.currentTime(query=True))
        cmds.setAttr("{0}.startTime".format(deformer),
                     cmds.currentTime(query=True))
        cmds.connectAttr("time1.outTime",
                         "{0}.currentTime".format(deformer))

        # Data node and Locator
        # This function may print an error message so we propagate whether
        # the function succeeded so that the error dialog is displayed.
        connect_to_debugger_success = locators.connect_to_debugger(deformer)

    return deformer, connect_to_debugger_success


@undo_chunk
def add_base_mesh(force=True):
    """Connects a mesh to the base mesh plug of the fat deformer.
    The source mesh and the destination fat deformer are retrieved
    from the current selection in that order.

    Args:
        force (bool, optional): If the mesh plug has to be overridden. Defaults to True.

    Returns:
        bool: False if there was an error. True otherwise.
    """
    plugin_check()
    selection = cmds.ls(selection=True, long=True)
    base_mesh, deformer = get_base_mesh_and_deformer(selection)
    if not base_mesh or not deformer:
        print("{0} No valid base mesh and deformer provided. Please retry adding "
              "the base mesh by selecting the elements in the following order: "
              "1) Base mesh, 2) Mesh with an {1} applied to."
              "".format(UiConstants.ERROR_PREFIX, DeformerTypes.FAT))
        return False

    # Number vertices check
    if not check_base_mesh(base_mesh, selection[-1]):
        return False

    try:
        cmds.connectAttr("{0}.worldMatrix[0]".format(base_mesh), "{0}.baseMatrix".format(deformer), force=force)
        cmds.connectAttr("{0}.worldMesh[0]".format(base_mesh), "{0}.baseMesh".format(deformer), force=force)
    except:
        print("{0} Could not add the base mesh because there is already a mesh connected."
              "".format(UiConstants.ERROR_PREFIX))
        return False

    base_mesh_short_name = cmds.ls(base_mesh, shortNames=True)[0]
    deformer_short_name = cmds.ls(deformer, shortNames=True)[0]
    print("{0} \"{1}\" connected successfully to the base mesh plug of \"{2}\"."
          "".format(UiConstants.INFO_PREFIX, base_mesh_short_name, deformer_short_name))
    return True


@undo_chunk
def remove_base_mesh():
    """Disconnects the base mesh from the base mesh plugs of simshape.
    The fat deformer is retrieved from the current selected object.

    Returns:
        bool: False if there was an error. True otherwise.
    """
    plugin_check()
    selection = cmds.ls(selection=True, long=True)
    if len(selection) < 1:
        print("{0} Invalid selection. Please, select the "
              "mesh with {1} applied to and try again."
              "".format(UiConstants.ERROR_PREFIX, DeformerTypes.FAT))
        return False

    _, deformer = get_base_mesh_and_deformer(selection)
    if not deformer:
        selection_short_name = cmds.ls(selection[-1], shortNames=True)[0]
        print("{0} Could not find a valid {1} deformer assigned to \"{2}\"."
              "".format(UiConstants.ERROR_PREFIX, DeformerTypes.FAT, selection_short_name))
        return False

    input_mesh = cmds.listConnections("{0}.baseMesh".format(deformer), plugs=True)
    input_matrix = cmds.listConnections("{0}.baseMatrix".format(deformer), plugs=True)

    if not input_mesh and not input_matrix:
        print("{0} Input connections to the base plug not found. "
              "Nothing to remove.".format(UiConstants.WARNING_PREFIX))
        return True

    if input_mesh:
        cmds.disconnectAttr("{0}".format(input_mesh[0]), "{0}.baseMesh".format(deformer))

    if input_matrix:
        cmds.disconnectAttr("{0}".format(input_matrix[0]), "{0}.baseMatrix".format(deformer))

    deformer_short_name = cmds.ls(deformer, shortNames=True)[0]
    print("{0} Base mesh has been disconnected successfully from \"{1}\"."
          "".format(UiConstants.INFO_PREFIX, deformer_short_name))
    return True


def check_base_mesh(base_mesh, sim_mesh):
    """Check if the provided base mesh is compatible with the mesh that
    has the fat deformer applied to.

    Args:
        base_mesh (str): Name of the mesh to be connected to the base mesh plugs.
        sim_mesh (str): Name of the mesh with the fat deformer applied to.

    Returns:
        bool: True if base_mesh is valid. False otherwise.
    """
    # Number vertices check
    num_vertices_base_mesh = cmds.polyEvaluate(base_mesh, vertex=True)
    num_vertices_sim_mesh = cmds.polyEvaluate(sim_mesh, vertex=True)
    if num_vertices_base_mesh != num_vertices_sim_mesh:
        print("{0} Selected meshes have different vertex count. Please, make sure "
              "to select two compatible meshes and try again."
              "".format(UiConstants.ERROR_PREFIX))
        return False
    return True


def get_base_mesh_and_deformer(selection):
    """Get the base mesh and the deformer from the selection.
    The expected selection order is supposed to be:
    1) Base mesh.
    2) Mesh with the deformer applied to.

    Args:
        selection (list): Current selection.

    Returns:
        base_mesh (str): Name of the base mesh.
        deformer (str): Name of the fat deformer.
    """
    base_mesh = None
    deformer = None

    if not selection:
        return base_mesh, deformer

    if len(selection) == 2:
        if not cmds.ls(selection[-2], type="mesh") and not cmds.listRelatives(selection[-2], type="mesh"):
            return base_mesh, deformer
        base_mesh = selection[-2]

    deformers_found = cmds.findDeformers(selection[-1]) or []
    deformer_nodes = [node for node in deformers_found if cmds.nodeType(node) == DeformerTypes.FAT]
    if not deformer_nodes:
        return base_mesh, deformer
    deformer = deformer_nodes[0]

    return base_mesh, deformer


def get_fat_mesh_input(selection):
    """Returns a list with the inputs connected to the base mesh and
    base matrix plug which belong to an AdnFat deformer.

    Args:
        selection (list): list containing the current selection.

    Return:
        inputs (list): List containing the input names.
    """
    base_mesh, deformer = get_base_mesh_and_deformer(selection)

    if not base_mesh or not deformer:
        return []

    input_mesh = cmds.listConnections("{0}.baseMesh".format(deformer), plugs=True) or []
    input_matrix = cmds.listConnections("{0}.baseMatrix".format(deformer), plugs=True) or []

    return input_mesh + input_matrix
