"""
from zoo.libs.maya.cmds.modeling import create
create.createPrimitiveAndMatch(primitive="cube")

"""

import maya.cmds as cmds
import maya.mel as mel

from zoo.libs.maya import zapi
from zoo.libs.utils import output
from zoo.libs.maya.cmds.objutils import matching
from zoo.libs.maya.cmds.objutils import namehandling

def createPrimitiveAndMatch(primitive="cube", inheritName=False, suffix="", message=True):
    """Creates an object and matches it to the currently selected object.

    Creates one object at a time. Objects are:

        "cube", "sphere", "cylinder", "plane", "nurbsCircle", "torus", "cone", "pyramid", "pipe", "helix", "gear",
        "soccerall", "svg", "superEllipsoid", "sphericalHarmonics", "ultraShape", "disk", "platonicSolid"

    :param primitive: the name of the primitive to build
    :type primitive: str
    :param inheritName: Inherit the name of the selected object?
    :type inheritName: bool
    :param suffix: Add a suffix to the new object Eg. "_jnt". There is no underscore added automatically
    :type suffix: str

    :return newObj: The name of the new object created
    :rtype: str
    """
    selectedObjList = cmds.ls(sl=1, l=1)
    if primitive == "cube":
        newObj = cmds.polyCube()[0]
    elif primitive == "sphere":
        newObj = cmds.polySphere(subdivisionsAxis=12, subdivisionsHeight=8)[0]
    elif primitive == "cylinder":
        newObj = cmds.polyCylinder(subdivisionsAxis=12)[0]
    elif primitive == "plane":
        newObj = cmds.polyPlane(subdivisionsHeight=1, subdivisionsWidth=1)[0]
    elif primitive == "nurbsCircle":
        newObj = cmds.circle(normal=[0, 1, 0])[0]
    elif primitive == "torus":
        newObj = cmds.polyTorus()[0]
    elif primitive == "cone":
        newObj = cmds.polyCone()[0]
    elif primitive == "disk":
        newObj = mel.eval('polyDisc;')[0]
    elif primitive == "pyramid":
        newObj = cmds.polyPyramid()[0]
    elif primitive == "pipe":
        newObj = cmds.polyPipe()[0]
    elif primitive == "prism":
        newObj = cmds.polyPrism()[0]
    elif primitive == "helix":
        newObj = cmds.polyHelix()[0]
    elif primitive == "gear":
        newObj = mel.eval('polyGear')[0]
    elif primitive == "platonicSolid":
        newObj = mel.eval('polyPlatonic -primitive 4 -subdivisionMode 0 -subdivisions 0 -radius 1 '
                          '-sphericalInflation 1;')[0]
    elif primitive == "soccerBall":
        newObj = mel.eval('polyPrimitive -r 1 -l 0.4036 -ax 0 1 0 -pt 0  -cuv 4 -ch 1')[0]
    elif primitive == "superEllipsoid":
        newObj = mel.eval('polySuperShape -radius 1 -shape "SuperEllipse" -horizontalDivisions 16 '
                          '-verticalDivisions 16 -createUV 2 -mergeVertices 1 -horizontalRevolutions 1 '
                          '-verticalRevolutions 1 -verticalOffset 0 -internalRadius 0 -xOffset 0 -zOffset 0 '
                          '-ve 1 -he 1 -em 1 -vm1 0 -ve1 1 -vm2 0 -ve2 1 -hm1 0 -he1 1 -hm2 0 -he2 1 -u0 0 -u1 1 '
                          '-u2 1 -u3 0.5 -u4 0 -u5 1 -u6 1 -u7 1 -u8 0 -u9 1 -u10 1 -u11 0.5 '
                          '-u12 0 -u13 1 -u14 1 -u15 1 -um 0;')[0]
    elif primitive == "sphericalHarmonics":
        newObj = mel.eval('polySuperShape -radius 1 -shape "SphericalHarmonics" -horizontalDivisions 16 '
                          '-verticalDivisions 16 -createUV 2 -mergeVertices 1 -horizontalRevolutions 1 '
                          '-verticalRevolutions 1 -verticalOffset 0 -internalRadius 0 -xOffset 0 -zOffset 0 -ve 1 '
                          '-he 1 -em 1 -vm1 0 -ve1 1 -vm2 0 -ve2 1 -hm1 0 -he1 1 -hm2 0 -he2 1 -u0 0 -u1 1 -u2 1 '
                          '-u3 0.5 -u4 0 -u5 1 -u6 1 -u7 1 -u8 0 -u9 1 -u10 1 -u11 0.5 -u12 0 -u13 1 -u14 1 -u15 1 '
                          '-um 0;')[0]
    elif primitive == "ultraShape":
        newObj = mel.eval('polySuperShape -radius 1 -shape "UltraShape" -horizontalDivisions 16 -verticalDivisions 16 '
                          '-createUV 2 -mergeVertices 1 -horizontalRevolutions 1 -verticalRevolutions 1 '
                          '-verticalOffset 0 -internalRadius 0 -xOffset 0 -zOffset 0 -ve 1 -he 1 -em 1 -vm1 0 -ve1 1 '
                          '-vm2 0 -ve2 1 -hm1 0 -he1 1 -hm2 0 -he2 1 -u0 0 -u1 1 -u2 1 -u3 0.5 -u4 0 -u5 1 -u6 1 '
                          '-u7 1 -u8 0 -u9 1 -u10 1 -u11 0.5 -u12 0 -u13 1 -u14 1 -u15 1 -um 0;')[0]
    elif primitive == "joint":
        sel = cmds.ls(selection=True)
        cmds.select(deselect=True)
        newObj = cmds.joint()
        cmds.select(sel, replace=True)
    else:
        output.displayWarning("Invalid object not supported: {}".format(primitive))
        return ""

    # Match to selection -----------------------------
    if selectedObjList:
        matching.matchToCenterObjsComponents(newObj, selectedObjList, setObjectMode=True, orientToComponents=True)
        if message:
            output.displayInfo("`{}` created and matched.".format(newObj))
    else:
        if message:
            output.displayInfo("Created `{}`".format(newObj))
    mel.eval('setToolTo ShowManips')

    # Rename ----------------------------------------
    if inheritName:
        newShortName = cmds.ls(selection=True, long=False)[0]
    else:
        newShortName = newObj
    if inheritName or suffix:
        if suffix:
            newShortName = "{}{}".format(newShortName, suffix)
        newObj = namehandling.safeRename(newObj, newShortName, message=False)
    return newObj


def createPrimitiveAndMatchMulti(objs, primitive="cube", inheritName=False, suffix="", parent=False, message=True):
    """Creates objects and matches to every selected object.  Will create many objects if many are selected.

    Objects are:

        "cube", "sphere", "cylinder", "plane", "nurbsCircle", "torus", "cone", "pyramid", "pipe", "helix", "gear",
        "soccerall", "svg", "superEllipsoid", "sphericalHarmonics", "ultraShape", "disk", "platonicSolid", "joint"

    :param objs: A list of objects to match the new objects to
    :type objs: list(str)
    :param primitive: the name of the primitive to build
    :type primitive: str
    :param suffix: add a suffix to the name?
    :type suffix: str

    :return: A list of all the new objects created
    :rtype: list(str)
    """
    newObjs = list()
    if not objs:
        newObj = createPrimitiveAndMatch(primitive=primitive, inheritName=inheritName, suffix=suffix, message=message)  # create only one
        return [newObj]
    for obj in objs:
        cmds.select(obj, replace=True)
        newObj = createPrimitiveAndMatch(primitive=primitive, inheritName=inheritName, suffix=suffix, message=message)
        newObjs.append(newObj)
    cmds.select(newObjs, replace=True)
    if not parent or len(newObjs) < 2:
        return newObjs

    # parent to each other -------
    nodesZapi = list(zapi.nodesByNames(newObjs))
    for i, node in enumerate(nodesZapi):
        if node == nodesZapi[-1]:  # Last node is already parented
            break
        cmds.parent(nodesZapi[i + 1].fullPathName(), node.fullPathName())

    return zapi.fullNames(nodesZapi)  # return the full names of the nodes


def createPrimitiveAndMatchMultiSel(primitive="cube", parent=False, inheritName=False, suffix=""):
    """Creates objects and matches to every selected object.  Will create many objects if many are selected.

    Objects are:

        "cube", "sphere", "cylinder", "plane", "nurbsCircle", "torus", "cone", "pyramid", "pipe", "helix", "gear",
        "soccerall", "svg", "superEllipsoid", "sphericalHarmonics", "ultraShape", "disk", "platonicSolid", "joint"

    :param primitive: the name of the primitive to build
    :type primitive: str
    :param primitive: parent objects together?
    :type primitive: str

    :return: A list of all the new objects created
    :rtype: list(str)
    """
    selObjs = cmds.ls(selection=True, type="transform", long=True)
    createPrimitiveAndMatchMulti(selObjs, primitive=primitive, parent=parent, inheritName=inheritName, suffix=suffix)


def createZBrushGridPlaneSize():
    """Creates a polygon plane the size of the ZBrush grid.   Used for sending objects to Zbrush
    """
    planeTransform, planeShapeNode = cmds.polyPlane(name="zbrush_gridScale_geo")
    cmds.setAttr("{}.height".format(planeShapeNode), 6.0)
    cmds.setAttr("{}.width".format(planeShapeNode), 6.0)
