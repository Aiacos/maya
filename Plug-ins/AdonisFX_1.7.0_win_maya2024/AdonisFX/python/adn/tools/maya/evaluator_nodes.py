import maya.cmds as cmds

from adn.utils.maya.undo_stack import undo_chunk
from adn.utils.maya.checkers import plugin_check
from adn.utils.constants import UiConstants


@undo_chunk
def create_edge_evaluator():
    """Creates the edge evaluator based on selection and makes the
    connections. 
    
    The order of selection is the following:
      1) Deform mesh
      2) Rest mesh

    Returns:
        bool: False if there was an error. True otherwise.
    """
    plugin_check()
    # Get the selected meshes
    selection = cmds.ls(selection=True, dagObjects=True, type="mesh",
                        long=True, noIntermediate=True)
    if len(selection) != 2:
        print("{0} Wrong number of meshes selected ({1}). "
              "Please, select in the following order: "
              "1) Deform mesh, 2) Rest mesh."
              "".format(UiConstants.ERROR_PREFIX, len(selection)))
        return False
    deform_mesh = selection[0]
    rest_mesh = selection[1]

    num_vertices_deform_mesh = cmds.polyEvaluate(deform_mesh, vertex=True)
    num_vertices_rest_mesh = cmds.polyEvaluate(rest_mesh, vertex=True)
    if num_vertices_deform_mesh != num_vertices_rest_mesh:
        print("{0} The selected meshes have different vertex count. "
              "Please, select two meshes with matching vertex count "
              "and try again."
              "".format(UiConstants.ERROR_PREFIX))
        return False

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
    print("{0} Node \"{1}\" has been created successfully.".format(UiConstants.INFO_PREFIX, edge_eval_node))
    return True
