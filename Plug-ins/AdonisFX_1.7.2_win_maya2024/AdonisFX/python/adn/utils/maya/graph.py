import maya.cmds as cmds

from adn.tools.maya import remap


def upgrade_remap_nodes(delete=True):
    """Upgrades the whole scene graph by replacing all maya remapValue
    nodes by AdnRemap nodes. The process preserves the settings
    (input value, ramp and ranges) and also the input and output
    connections.

    Args:
        delete (bool, optional): Flag to remove every maya remapValue node
            once the AdnRemap node is created. Defaults to True.
    """
    maya_remap_nodes = cmds.ls(type="remapValue")
    for maya_node in maya_remap_nodes:
        remap_data = remap.get_remap_value_node_setup(maya_node)
        if remap_data is None:
            continue
        remap.create_remap(remap_data)
        if delete:
            cmds.delete(maya_node)
