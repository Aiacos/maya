import maya.cmds as cmds

from adn.utils.constants import DeformerTypes, DebugDataDescriptor, UiConstants
from adn.ui.utils import cursor
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
        bool: False if there was an error. True otherwise.
    """
    plugin_check()
    deformer = ""
    selection = cmds.ls(selection=True)
    if len(selection) < 1:
        print("{0} Wrong number of objects selected ({1}). Select at least a mesh to apply "
              "the muscle solver to.".format(UiConstants.ERROR_PREFIX, len(selection)))
        return deformer, False

    # Check that the last element of the selection is a valid mesh
    deformer_mesh = cmds.ls(selection[-1], dagObjects=True, type="mesh", noIntermediate=True)
    if not deformer_mesh:
        print("{0} The selected object to apply the deformer is not a deformable mesh. "
              "Aborting creation."
              "".format(UiConstants.ERROR_PREFIX))
        return deformer, False

    # Check deformers applied to the selection
    applied_deformers = cmds.findDeformers(selection[-1]) or []
    short_name = cmds.ls(selection[-1], long=False)
    for applied_deformer in applied_deformers:
        if cmds.nodeType(applied_deformer) == DeformerTypes.RIBBON:
            print("{0} The selected mesh ({1}) has already an AdnRibbonMuscle deformer node "
                  "applied to. Aborting creation.".format(UiConstants.WARNING_PREFIX, short_name[0]))
            return deformer, True

    unsuccessful_attachments = list()
    successful_attachments = list()
    connect_to_debugger_success = True
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
        # This function may print an error message so we propagate whether
        # the function succeeded so that the error dialog is displayed.
        connect_to_debugger_success = locators.connect_to_debugger(deformer)

        # Restore selection
        cmds.select(selection)

    # Creation dialog
    ribbon_deformer_short_name = cmds.ls(deformer, shortNames=True)[0]
    if unsuccessful_attachments:
        unsuccessful_attachments = ["\"{0}\"".format(s) for s in unsuccessful_attachments]
        attachment_names = ", ".join(unsuccessful_attachments)
        print("{0} \"{1}\" deformer has been created successfully. "
              "The following selected nodes were not eligible for attachments: {2}."
              "".format(UiConstants.WARNING_PREFIX, ribbon_deformer_short_name, attachment_names))
    else:
         print("{0} \"{1}\" deformer has been created successfully."
              "".format(UiConstants.INFO_PREFIX, ribbon_deformer_short_name))

    return deformer, connect_to_debugger_success


def create_default_ribbon_muscle(mesh_name, node_name):
    """Create the most basic ribbon muscle deformer. Only time attributes are
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
                                 type=DeformerTypes.RIBBON,
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
