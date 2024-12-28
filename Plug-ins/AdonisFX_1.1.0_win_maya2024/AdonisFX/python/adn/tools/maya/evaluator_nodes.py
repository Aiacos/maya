import maya.cmds as cmds

from adn.ui.maya.window import main_window
from adn.ui.widgets.dialogs import msg_box
from adn.utils.maya.undo_stack import undo_chunk
from adn.utils.maya.checkers import plugin_check


@undo_chunk
def create_edge_evaluator():
    """Creates the edge evaluator based on selection and makes the
    connections. 
    
    The order of selection is the following:
      1) Deform mesh
      2) Rest mesh
    """
    plugin_check()
    # Get the selected meshes
    selection = cmds.ls(selection=True, dagObjects=True, type="mesh",
                        long=True, noIntermediate=True)
    if len(selection) != 2:
        msg_box(main_window(), "error",
                "Wrong number of meshes selected ({0}). "
                "Please, select in the following order:"
                "\n1) Deform mesh"
                "\n2) Rest mesh".format(len(selection)))
        return
    deform_mesh = selection[0]
    rest_mesh = selection[1]

    num_vertices_deform_mesh = cmds.polyEvaluate(deform_mesh, vertex=True)
    num_vertices_rest_mesh = cmds.polyEvaluate(rest_mesh, vertex=True)
    if num_vertices_deform_mesh != num_vertices_rest_mesh:
        msg_box(main_window(), "error",
                "The selected meshes have different vertex count. "
                "Please, select two meshes with matching vertex count "
                "and try again.")
        return

    # Create the node
    edge_eval_node = cmds.createNode("AdnEdgeEvaluator")

    # Make the connections
    cmds.setAttr("{0}.initializationTime".format(edge_eval_node), 
                 cmds.currentTime(query=True))
    cmds.connectAttr("{0}.outMesh".format(deform_mesh), 
                     "{0}.deformMesh".format(edge_eval_node))
    cmds.connectAttr("{0}.outMesh".format(rest_mesh), 
                     "{0}.restMesh".format(edge_eval_node))

    cmds.select(edge_eval_node)
    msg_box(main_window(), "info",
            "Node \"{0}\" has been created successfully.".format(edge_eval_node))
