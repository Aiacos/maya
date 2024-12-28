"""
from zoo.libs.maya.objutils.modeling import create
create.createPrimitiveAndMatch(primitive="cube")

"""

import maya.cmds as cmds
import maya.mel as mel

from zoo.libs.utils import output
from zoo.libs.maya.cmds.objutils import matching


def createPrimitiveAndMatch(primitive="cube"):
    """Creates an object and matches it to the currently selected object.

    Creates one object at a time. Objects are:

        "cube", "sphere", "cylinder", "plane", "nurbsCircle", "torus", "cone", "pyramid", "pipe", "helix", "gear",
        "soccerall", "svg", "superEllipsoid", "sphericalHarmonics", "ultraShape", "disk", "platonicSolid"

    :param primitive: the name of the primitive to build
    :type primitive: str

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
    else:
        output.displayWarning("Invalid object not supported: {}".format(primitive))
        return ""
    if selectedObjList:
        matching.matchToCenterObjsComponents(newObj, selectedObjList, setObjectMode=True, orientToComponents=True)
        output.displayInfo("`{}` created and matched.".format(newObj))
    else:
        output.displayInfo("Created `{}`".format(newObj))
    mel.eval('setToolTo ShowManips')
    return newObj


def createZBrushGridPlaneSize():
    """Creates a polygon plane the size of the ZBrush grid.   Used for sending objects to Zbrush
    """
    planeTransform, planeShapeNode = cmds.polyPlane(name="zbrush_gridScale_geo")
    cmds.setAttr("{}.height".format(planeShapeNode), 6.0)
    cmds.setAttr("{}.width".format(planeShapeNode), 6.0)
