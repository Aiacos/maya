import maya.cmds as cmds

from adn.utils.constants import DeformerTypes, DebugDataDescriptor
from adn.ui.widgets.dialogs import msg_box
from adn.ui.utils import cursor
from adn.ui.maya.window import main_window
from adn.tools.maya import locators 
from adn.utils.maya.undo_stack import undo_chunk
from adn.utils.maya.checkers import plugin_check
import adn.tools.maya.attachments as adn_attachments


@undo_chunk
def apply_ribbon_muscle(custom_name=None, start_time=None, stiffness=1e5, iterations=10, gravity=0.0, damping=0.75):
    """Create a ribbon muscle deformer and configure the main attributes with the given argument values.

    Args:
        custom_name (str, optional): Custom name to give to the deformer. Defaults to None.
        start_time (float, optional): Frame number for initialization. Defaults to None.
        stiffness (float, optional): Material stiffness. Defaults to 1e5.
        iterations (int, optional): Number of solver iterations for a simulation step. Defaults to 10.
        gravity (float, optional): Magnitude of the gravity. Defaults to 0.0.
        damping (float, optional): Global damping value. Defaults to 0.75.

    Returns:
        str: Name of the created ribbon muscle deformer if created correctly.
    """
    plugin_check()
    deformer = ""
    selection = cmds.ls(selection=True)
    if len(selection) < 1:
        msg_box(main_window(), "error",
                "Wrong number of objects selected ({0}). Select at least a mesh to apply "
                "the muscle solver to.".format(len(selection)))
        return deformer

    # Check that the last element of the selection is a valid mesh
    deformer_mesh = cmds.ls(selection[-1], dagObjects=True, type="mesh", noIntermediate=True)
    if not deformer_mesh:
        msg_box(main_window(), "error",
                "The selected object to apply the deformer is not a deformable mesh. "
                "Aborting creation.")
        return deformer

    # Check deformers applied to the selection
    applied_deformers = cmds.findDeformers(selection[-1]) or []
    short_name = cmds.ls(selection[-1], long=False)
    for applied_deformer in applied_deformers:
        if cmds.nodeType(applied_deformer) == DeformerTypes.RIBBON:
            msg_box(main_window(), "warning",
                    "The selected mesh ({0}) has already an AdnRibbonMuscle deformer node "
                    "applied to. Aborting creation.".format(short_name[0]))
            return deformer

    unsuccessful_attachments = list()
    successful_attachments = list()
    with cursor.wait_cursor_context():
        attachment_nodes, node = selection[:-1], selection[-1]
        cmds.select(node)
        deformer = (cmds.deformer(type=DeformerTypes.RIBBON)[0] if not custom_name else
                    cmds.deformer(type=DeformerTypes.RIBBON, name=custom_name)[0])

        # Configure attributes
        cmds.setAttr("{0}.prerollStartTime".format(deformer), start_time or cmds.currentTime(query=True))
        cmds.setAttr("{0}.startTime".format(deformer), start_time or cmds.currentTime(query=True))
        cmds.setAttr("{0}.stiffness".format(deformer), stiffness)
        cmds.setAttr("{0}.gravity".format(deformer), gravity)
        cmds.setAttr("{0}.iterations".format(deformer), iterations)
        cmds.setAttr("{0}.globalDampingMultiplier".format(deformer), damping)

        # Main connections
        cmds.connectAttr("time1.outTime", "{0}.currentTime".format(deformer))

        # Attachments
        geometries_to_attach = list()
        transforms_to_attach = list()
        geometries_to_attach = list()
        transforms_to_attach = list()
        for attachment in attachment_nodes:
            if cmds.ls(attachment, type="mesh") or cmds.listRelatives(attachment, type="mesh"):
                geometries_to_attach.append(attachment)
            else:
                transforms_to_attach.append(attachment)

        if geometries_to_attach:
            # Add geometries as attachments
            successful_attachments, unsuccessful_attachments = \
              adn_attachments.add_geometry_target(deformer, geometries_to_attach)

        if transforms_to_attach:
            # Add transforms as attachments
            transforms_duplicated = list()
            successful_attachments, transforms_duplicated = \
                adn_attachments.add_attachment(deformer, transforms_to_attach)
            unsuccessful_attachments.extend(transforms_duplicated)

        # Data node and Locator
        locators.connect_to_debugger(deformer)

        # Force a viewport refresh (needed for the wait_cursor_context to work)
        cmds.refresh(force=True)
        # Restore selection
        cmds.select(selection)

    # Creation dialog
    ribbon_deformer_short_name = cmds.ls(deformer, shortNames=True)[0]
    if unsuccessful_attachments:
        unsuccessful_attachments = ["\n    \"{0}\"".format(s) for s in unsuccessful_attachments]
        attachment_names = "".join(unsuccessful_attachments)
        msg_box(main_window(), "warning",
                "\"{0}\"deformer has been created successfully. "
                "\nThe following selected nodes were not eligible for attachments:"
                "{1}\nPlease, check the console for more information."
                "".format(ribbon_deformer_short_name, attachment_names))
    else:
        msg_box(main_window(), "info",
                "\"{0}\" deformer has been created successfully."
                "".format(ribbon_deformer_short_name))

    return deformer


def create_default_ribbon_muscle(mesh_name, node_name):
    """Create the most basic ribbon muscle deformer. Only time attributes are
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
                                 type=DeformerTypes.RIBBON,
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


@undo_chunk
def draw_fibers(display):
    """Shows or hides the fibers direction for all the ribbon deformers in
    the scene.

    Args:
        display (bool): flag to show or hide the fibers.
    """
    all_muscles = cmds.ls(type=DeformerTypes.RIBBON)
    for muscle in all_muscles:
        if display:
            # Reference number for fibers is defined in DebugDataDescriptor.kMuscleFibers
            cmds.setAttr("{0}.debugFeature".format(muscle), DebugDataDescriptor.kMuscleFibers)
        elif cmds.getAttr("{0}.debugFeature".format(muscle)) != DebugDataDescriptor.kMuscleFibers:
            # Don't hide if it's a feature other than fibers
            continue
        cmds.setAttr("{0}.debug".format(muscle), display)
