import maya.cmds as cmds

from adn.utils.constants import DeformerTypes, UiConstants
from adn.utils.maya.undo_stack import undo_chunk
from adn.utils.maya.checkers import plugin_check
from adn.ui.utils import cursor


@undo_chunk
def apply_relax():
    """Apply an AdnRelax deformer to the selected mesh. The deformer will not be
    created if there is no selection or if there is a deformer already applied
    to the selected mesh.
    
    Returns:
        str: Name of the relax deformer if created correctly.
        bool: False if there was an error. True otherwise.
    """
    plugin_check()

    deformer = ""
    selection = cmds.ls(selection=True, dagObjects=True, type="mesh", noIntermediate=True)

    if not selection:
        print("{0} {1} could not be created because the selection does not contain a mesh."
              "".format(UiConstants.ERROR_PREFIX, DeformerTypes.RELAX))
        return deformer, False

    mesh = selection[0]
    # Check deformers applied to the selection
    applied_deformers = cmds.findDeformers(mesh) or []
    short_name = cmds.ls(mesh, long=False)[0]
    for applied_deformer in applied_deformers:
        if cmds.nodeType(applied_deformer) == DeformerTypes.RELAX:
            print("{0} The selected mesh ({1}) has already an {2} deformer node "
                  "applied to. Aborting creation."
                  "".format(UiConstants.WARNING_PREFIX, short_name, DeformerTypes.RELAX))
            return deformer, True

    with cursor.wait_cursor_context():
        deformer = cmds.deformer(type=DeformerTypes.RELAX)[0]
        # Restore selection
        cmds.select(mesh)

    print("{0} \"{1}\" deformer has been created successfully."
          "".format(UiConstants.INFO_PREFIX, deformer))
    return deformer, True
