import sys

import maya.cmds as cmds

from adn.utils.constants import DeformerTypes
from adn.ui.widgets.dialogs import msg_box
from adn.ui.utils import cursor
from adn.ui.maya.window import main_window
from adn.tools.maya import locators
from adn.utils.maya.undo_stack import undo_chunk
from adn.utils.maya.checkers import plugin_check


@undo_chunk
def apply_skin(custom_name=None, start_time=None, stiffness=1e5, iterations=3, gravity=0.0, damping=0.75):
    """Create the skin deformer and configure the main attributes with the given argument values.

    Args:
        custom_name (str, optional): Custom name to give to the deformer. Defaults to None.
        start_time (float, optional): Frame number for initialization. Defaults to None.
        stiffness (float, optional): Material stiffness. Defaults to 1e5.
        iterations (int, optional): Number of solver iterations for a simulation step. Defaults to 3.
        gravity (float, optional): Magnitude of the gravity. Defaults to 0.0.
        damping (float, optional): Global damping value. Defaults to 0.75.

    Returns:
        str: Name of the created skin deformer if created correctly.
    """
    plugin_check()
    deformer = ""
    selection = cmds.ls(selection=True, dagObjects=True, type="mesh", noIntermediate=True)
    if len(selection) != 2:
        msg_box(main_window(), "error",
                "Wrong number of meshes selected ({0}). Select one reference mesh to guide "
                "the skin, and the mesh to apply the skin solver to."
                "".format(len(selection)))
        return deformer

    # Check deformers applied to the selection
    applied_deformers = cmds.findDeformers(selection[1]) or []
    short_name = cmds.ls(selection[1], long=False)
    for applied_deformer in applied_deformers:
        if cmds.nodeType(applied_deformer) == DeformerTypes.SKIN:
            msg_box(main_window(), "warning",
                    "The selected mesh ({0}) has already an AdnSkin deformer node "
                    "applied to. Aborting creation.".format(short_name[0]))
            return deformer

    with cursor.wait_cursor_context():
        goal_node, node = selection
        cmds.select(node)
        deformer = (cmds.deformer(type=DeformerTypes.SKIN)[0] if not custom_name else
                    cmds.deformer(type=DeformerTypes.SKIN, name=custom_name)[0])
        
        # Configure attributes
        cmds.setAttr("{0}.prerollStartTime".format(deformer), start_time or cmds.currentTime(query=True))
        cmds.setAttr("{0}.startTime".format(deformer), start_time or cmds.currentTime(query=True))
        cmds.setAttr("{0}.stiffness".format(deformer), stiffness)
        cmds.setAttr("{0}.gravity".format(deformer), gravity)
        cmds.setAttr("{0}.iterations".format(deformer), iterations)
        cmds.setAttr("{0}.globalDampingMultiplier".format(deformer), damping)

        # Main connections
        cmds.connectAttr("{0}.worldMatrix[0]".format(goal_node), "{0}.referenceMatrix".format(deformer))
        cmds.connectAttr("{0}.worldMesh[0]".format(goal_node), "{0}.referenceMesh".format(deformer))
        cmds.connectAttr("time1.outTime", "{0}.currentTime".format(deformer))

        # Force a viewport refresh (needed for the wait_cursor_context to work)
        cmds.refresh(force=True)
        # Data node and Locator
        locators.connect_to_debugger(deformer)
        # Restore selection
        cmds.select(selection)

    # Creation dialog
    skin_deformer_short_name = cmds.ls(deformer, shortNames=True)[0]
    msg_box(main_window(), "info",
            "\"{0}\" deformer has been created successfully."
            "".format(skin_deformer_short_name))

    return deformer


def create_default_skin(mesh_name, node_name):
    """Create the most basic skin deformer. Only time attributes are
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
                                 type=DeformerTypes.SKIN,
                                 name=node_name)[0]
        cmds.setAttr("{0}.prerollStartTime".format(deformer),
                     cmds.currentTime(query=True))
        cmds.setAttr("{0}.startTime".format(deformer),
                     cmds.currentTime(query=True))
        cmds.connectAttr("time1.outTime",
                         "{0}.currentTime".format(deformer))

        # Data node and Locator
        locators.connect_to_debugger(deformer)

    return deformer


def check_dependencies_on_import(data):
    """Checks if, based on the imported data, the AdnSkin deformer might be
    created from scratch with all the minimum inputs required.
    The minimum requirements for the AdnSkin deformer are:
        - Providing the 'referenceMesh'.
        - Providing the 'referenceMatrix'.

    Args:
        data (dict): Dictionary that containts all the AdnSkin available
            data to import.

    Returns:
        bool: True if imported data has the minimum requirements to create the
            AdnSkin deformer from scratch. False otherwise.
        str: descriptive message about the missing requirement if any.
    """
    error_message = ""
    if "referenceMesh" not in data:
        error_message = "The target mesh was not found in the imported data."
        return False, error_message
    else:
        reference_mesh = data["referenceMesh"]
        if not cmds.objExists(reference_mesh):
            error_message = "The target mesh '{0}' was not found in the scene." \
                            "".format(reference_mesh)
            return False, error_message

    if "referenceMatrix" not in data:
        error_message = "The reference matrix was not found in the imported data."
        return False, error_message
    else:
        reference_matrix = data["referenceMatrix"]
        # String values from a json load in Python 2 return unicode
        if sys.version_info[0] < 3 and type(reference_matrix) is unicode:
            reference_matrix = str(reference_matrix)

        imported_value_type = type(reference_matrix)
        if imported_value_type == str:
            # Importing a connection
            if not cmds.objExists(reference_matrix):
                error_message = "The reference matrix '{0}' was not found in " \
                                "the scene.".format(reference_matrix)
                return False, error_message

    return True, error_message
