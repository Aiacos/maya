from maya import cmds
from zoo.libs.maya.zapi import base

def findNonDeformerHistory(geometry):
    """Returns any geometry which contains non deformer history.

    :param geometry: The geometry to check, typically the parent transform of a mesh.
    :type geometry: list[:class:`base.DagNode`]
    :return: Meshes which contain non deformer history.
    :rtype: list[:class:`base.DagNode`]
    """
    # bakePartialHistory returns None when nothing found otherwise a list hence the if check
    out = set()
    for geo in geometry:
        history = cmds.bakePartialHistory(geo.fullPathName(), query=True,  preDeformers=True,
                                          prePostDeformers=True,
                                          preCache=True)
        if not history:
            continue
        for n in history:
            node = base.nodeByName(n)
            if node.apiType() in (base.kNodeTypes.kTransform, base.kNodeTypes.kMesh):
                continue
            out.add(geo)

    return list(out)
