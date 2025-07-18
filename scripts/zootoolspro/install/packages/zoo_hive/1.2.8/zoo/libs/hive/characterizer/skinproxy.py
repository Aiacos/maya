"""
from zoo.libs.hive.characterizer import skinproxy
skinproxy.importSkinProxy()


"""

from maya import cmds

from zoo.libs.utils import output
from zoo.libs.hive.characterizer import skinproxy_constants as sc
from zoo.libs.maya.cmds.skin import bindskin

def skinProxyExists():
    return cmds.objExists("skinProxy:skinProxyBlends")


def importSkinProxy():
    """ Imports the skinProxy.mb file into the scene with a namespace "skinProxy:"
    """
    if cmds.objExists("skinProxy:god_M_godnode_jnt"):
        output.displayWarning("The skinProxy is already imported into the scene.  "
                              "To rebuild delete the existing skinProxy.")
        return
    if cmds.objExists(sc.DEFAULT_SKINPROXY_MESH):
        output.displayWarning("The skinProxy mesh is already imported into the scene. Delete before creating new mesh.")
        return
    namespace = "skinProxy"
    # if the namespace exists delete it
    if cmds.namespace(exists=namespace):
        # delete the namespace "skinProxy" and all nodes in it
        deleteSkinProxy()

    cmds.file(sc.SKIN_PROXY_MAYA_PATH,
              preserveReferences=True,
              ignoreVersion=True,
              namespace=namespace,
              i=True,
              type="mayaBinary",
              force=True,
              options="v=0;")

def importSkinProxyMesh():
    if cmds.objExists(sc.DEFAULT_SKINPROXY_MESH):
        output.displayWarning("The skinProxy mesh is already imported into the scene. Delete before creating new mesh.")
        return

    importSkinProxy()
    # remove skinning, and unparent
    bindskin.unbindSkinObjs([sc.DEFAULT_SKINPROXY_MESH])
    cmds.parent(sc.DEFAULT_SKINPROXY_MESH, world=True)
    # delete the skeleton
    cmds.delete([sc.DEFAULT_SKINPROXY_SKELETON_ROOT, sc.DEFAULT_SKINPROXY_BLEND])


def deleteSkinProxy():
    """Deletes the skinProxy namespace and all nodes within it
    """
    try:
        cmds.namespace(set=":")
        cmds.namespace(removeNamespace="skinProxy", deleteNamespaceContent=True)
        output.displayInfo("The skinProxy has been deleted from the scene.")
    except RuntimeError:
        output.displayWarning("The skinProxy is not in the scene.")


def bodyPartAdjust(bodyPart, value):
    """For UI sliders sets the body part to the correct slider value.

    :param bodyPart: The body part name "head", "chest", "hips", "legs", "arms", "hands"
    :type bodyPart: str
    :param value: A slider value of 0.0 - 1.0
    :type value: float
    """
    if not skinProxyExists():
        output.displayWarning("Please import the skinProxy.  Blendshape node not found.")
        return
    data = sc.ALL_DATA[bodyPart]
    defaultDict = data[0]["skeleton"]
    poseDict = data[1]["skeleton"]
    blendshapeAttr = data[1]["blendAttr"]
    # set the blendshape value ----------------------
    cmds.setAttr("skinProxy:skinProxyBlends.{}".format(blendshapeAttr), value)
    # Set the skeleton values rotate and translate ----------------------
    for jnt in defaultDict.keys():
        jntName = "skinProxy:{}".format(jnt)
        defaultTranslate = defaultDict[jnt][0][0]
        defaultRotate = defaultDict[jnt][1][0]
        targetTranslate = poseDict[jnt][0][0]
        targetRotate = poseDict[jnt][1][0]

        translate = [defaultTranslate[i] + (targetTranslate[i] - defaultTranslate[i]) * value for i in range(3)]
        rotate = [defaultRotate[i] + (targetRotate[i] - defaultRotate[i]) * value for i in range(3)]
        cmds.setAttr("{}.translate".format(jntName), *translate)
        cmds.setAttr("{}.rotate".format(jntName), *rotate)
