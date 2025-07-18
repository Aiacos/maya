"""Animator Hive Tools Misc

from zoo.libs.hive.anim import animatortools
animatortools.toggleControlPanelNodes()

animatortools.setTpose()

"""

from maya import cmds

from zoo.libs.utils import output

from zoo.libs.hive import api
from zoo.libs.hive.base import rig
from zoo.libs.hive.anim import mirroranim
from zoo.libs.maya.meta import base
from zoo.libs.maya import zapi

from zoo.libs.maya.cmds.objutils import locators

# -------------------------------------------------------------------------------------------------------------
# Get Rig Selected
# -------------------------------------------------------------------------------------------------------------

def rigNeedsNamespace(rigName):
    """If there are duplicated Hive rig names in the scene return True

    :param rigName: The name of a hive rig eg "zoo_mannequin"
    :type rigName: str
    :return: If Duplicated rigs return True
    :rtype: bool
    """
    try:
        api.rootByRigName(rigName, "")
        return False
    except:
        return True


def rigsFromNodes(nodes):
    """Returns a list of rig instances, names and namespaces from the given zapi nodes.  Usually a selection.

    :param nodes: A list of zapi node names
    :type nodes: list(:class:`zapi.DagNode`)
    :return: rigInstances, rigNames, rigNamespaces
    :rtype: tuple(list(:class:`api.Rig`), list(str), list(str)
    """
    rigInstances = list()
    rigNames = list()
    rigNamespaces = list()
    for node in nodes:  # get the current selection
        try:
            rigInstance = api.rigFromNode(node)
        except api.MissingMetaNode:
            continue
        if rigInstance.buildState() < api.constants.CONTROL_VIS_STATE:
            output.displayWarning("Rig `{}` must be in at least skeleton mode".format(rigInstance.name()))
            continue
        if rigInstance not in rigInstances:
            rigInstances.append(rigInstance)
            rigNames.append(rigInstance.name())
            rigNamespaces.append(rigInstance.meta.namespace())
    return rigInstances, rigNames, rigNamespaces


def rigsFromNodesSel():
    """Returns a list of rig instances, names and namespaces from the current selection

    :return: A list of Hive rig instances
    :rtype: list(:class:`api.Rig`)
    """
    return rigsFromNodes(list(zapi.selected()))


def rigNamesToString(rigNames, namespaces):
    """Converts a list of rig names and namespaces to a string for display in the UI

        "m1:zoo_mannequin, m2:zoo_mannequin, m3:zoo_mannequin"

    will remove the namespace of the name if it doesn't clash in the scene.

        "zoo_mannequin, robot"

    :param rigNames: A list of Hive rig names Eg. ["zoo_mannequin", "zoo_mannequin", "zoo_mannequin"]
    :type rigNames: list(str)
    :param namespaces: A list of Hive rig names Eg. ["m1", "m2", "m3"]
    :type namespaces: list(str)
    :return: A string for a UI text edit field, comma separated. Eg. "m1:zoo_mannequin, m2:zoo_mannequin"
    :rtype: str
    """
    rigNamesStr = ""
    for i, name in enumerate(rigNames):
        if namespaces[i] and rigNeedsNamespace(name):
            if namespaces[i].endswith(":"):
                namespaces[i] = namespaces[i][:-1]  # remove the trailing colon
            if namespaces[i].startswith(":"):
                namespaces[i] = namespaces[i][1:]  # remove the start colon
            if rigNamesStr:
                rigNamesStr += ",  "
            rigNamesStr += "{}:{}".format(namespaces[i], name)
        else:
            rigNamesStr += "{}".format(name)
    return rigNamesStr


def rigsFromNodesSelStr():
    """Returns list of rig names and matching namespaces from the current selection of Hive rigs.
    If no rigs are selected returns list(), list() .

    :return: A list of rig names and namespaces Eg. (["natalie"], [n1"])
    :rtype: tuple(list(str), list(str))
    """
    rigInstances, rigNames, namespaces = rigsFromNodesSel()
    if not rigNames:
        output.displayWarning("No Hive Rigs selected")
        return list(), list()
    return rigNames, namespaces


# -------------------------------------------------------------------------------------------------------------
# Control Panel Nodes
# -------------------------------------------------------------------------------------------------------------


def selectControlPanelNodes(add=True):
    """Adds related control panel nodes to the selection, from the Hive rig current selection.
    """
    controlPanelNodes = list()
    for sel in zapi.selected():
        if not sel.hasAttribute(api.constants.ID_ATTR):
            continue
        for m in base.getConnectedMetaNodes(sel):
            if m.mClassType() != api.constants.RIG_LAYER_TYPE:
                continue
            controlPanelNodes.append(str(m.controlPanel()))
    if controlPanelNodes:
        if add:
            cmds.select(controlPanelNodes, add=True)
        else:
            cmds.select(controlPanelNodes, deselect=True)
        return True
    return False


def toggleControlPanelNodesSel():
    """Toggles the selection of the control panel nodes, if they are selected it will deselect them, if they are not
    """
    if not cmds.ls(selection=True):
        return
    controlPanelFound = False
    networkNodes = cmds.ls(selection=True, type="network")
    for node in networkNodes:
        if cmds.attributeQuery(api.constants.ID_ATTR, node=node, exists=True):
            if cmds.getAttr(".".join([node, api.constants.ID_ATTR])) == api.constants.CONTROL_PANEL_TYPE:
                controlPanelFound = True
    if controlPanelFound:
        selectControlPanelNodes(add=False)
    else:
        selectControlPanelNodes(add=True)


# -------------------------------------------------------------------------------------------------------------
# TPose
# -------------------------------------------------------------------------------------------------------------

def setTPose(rigName="natalie", namespaceName=""):
    """Sets a biped  rig to a T-Pose, this is useful for setting up the rig for animation.

    Currently only supports the Biped and Biped Light, ie not UE5.

    :param rigName: The name identifier of the Hive rig, ie Natalie
    :type rigName: str
    :param namespaceName: If referenced or has a namespace, specify the namespace.  If not leave as "".
    :type namespaceName: str
    """
    bipedType = "standard"  # "standard" or "UE

    pointer01CtrlL = ""
    pointer02CtrlL = ""
    pointer03CtrlL = ""
    middle01CtrlL = ""
    middle02CtrlL = ""
    middle03CtrlL = ""
    ring01CtrlL = ""
    ring02CtrlL = ""
    ring03CtrlL = ""
    pinky01CtrlL = ""
    pinky02CtrlL = ""
    pinky03CtrlL = ""

    r = rig.Rig()
    r.startSession(rigName, namespace=namespaceName)  # Your rig name is found at the top left of the Hive UI.

    try:  # try the standard biped or lightweight biped rigs
        shoulderCtrlL = r.arm_L.rigLayer().control("uprfk").fullPathName()
        elbowCtrlL = r.arm_L.rigLayer().control("midfk").fullPathName()
        wristCtrlL = r.arm_L.rigLayer().control("endfk").fullPathName()
        legUpprCtrlL = r.leg_L.rigLayer().control("uprfk").fullPathName()
        kneeCtrlL = r.leg_L.rigLayer().control("midfk").fullPathName()
        footCtrlL = r.leg_L.rigLayer().control("endfk").fullPathName()
        armLControlPanel = r.arm_L.rigLayer().controlPanel().fullPathName()
        legLControlPanel = r.leg_L.rigLayer().controlPanel().fullPathName()
        try:  # could be missing fingers etc
            pointer01CtrlL = r.finger_pointer_L.rigLayer().control("fk01").fullPathName()
            pointer02CtrlL = r.finger_pointer_L.rigLayer().control("fk02").fullPathName()
            pointer03CtrlL = r.finger_pointer_L.rigLayer().control("fk03").fullPathName()
            middle01CtrlL = r.finger_middle_L.rigLayer().control("fk01").fullPathName()
            middle02CtrlL = r.finger_middle_L.rigLayer().control("fk02").fullPathName()
            middle03CtrlL = r.finger_middle_L.rigLayer().control("fk03").fullPathName()
            ring01CtrlL = r.finger_ring_L.rigLayer().control("fk01").fullPathName()
            ring02CtrlL = r.finger_ring_L.rigLayer().control("fk02").fullPathName()
            ring03CtrlL = r.finger_ring_L.rigLayer().control("fk03").fullPathName()
            pinky01CtrlL = r.finger_pinky_L.rigLayer().control("fk01").fullPathName()
            pinky02CtrlL = r.finger_pinky_L.rigLayer().control("fk02").fullPathName()
            pinky03CtrlL = r.finger_pinky_L.rigLayer().control("fk03").fullPathName()
        except AttributeError:
            pass
    except AttributeError:  # try UE rig type
        try:
            shoulderCtrlL = r.arm_l.rigLayer().control("uprfk").fullPathName()
            elbowCtrlL = r.arm_l.rigLayer().control("midfk").fullPathName()
            wristCtrlL = r.arm_l.rigLayer().control("endfk").fullPathName()
            legUpprCtrlL = r.leg_l.rigLayer().control("uprfk").fullPathName()
            kneeCtrlL = r.leg_l.rigLayer().control("midfk").fullPathName()
            footCtrlL = r.leg_l.rigLayer().control("endfk").fullPathName()
            armLControlPanel = r.arm_l.rigLayer().controlPanel().fullPathName()
            legLControlPanel = r.leg_l.rigLayer().controlPanel().fullPathName()
            bipedType = "UE"
            try:  # could be missing fingers etc
                pointer01CtrlL = r.index_l.rigLayer().control("fk01").fullPathName()
                pointer02CtrlL = r.index_l.rigLayer().control("fk02").fullPathName()
                pointer03CtrlL = r.index_l.rigLayer().control("fk03").fullPathName()
                middle01CtrlL = r.middle_l.rigLayer().control("fk01").fullPathName()
                middle02CtrlL = r.middle_l.rigLayer().control("fk02").fullPathName()
                middle03CtrlL = r.middle_l.rigLayer().control("fk03").fullPathName()
                ring01CtrlL = r.ring_l.rigLayer().control("fk01").fullPathName()
                ring02CtrlL = r.ring_l.rigLayer().control("fk02").fullPathName()
                ring03CtrlL = r.ring_l.rigLayer().control("fk03").fullPathName()
                pinky01CtrlL = r.pinky_l.rigLayer().control("fk01").fullPathName()
                pinky02CtrlL = r.pinky_l.rigLayer().control("fk02").fullPathName()
                pinky03CtrlL = r.pinky_l.rigLayer().control("fk03").fullPathName()
            except AttributeError:
                pass
        except AttributeError:  # failed to find the correct biped rig
            output.displayWarning("The rig is not of type `biped standard`, `biped lightweight`, or `biped UE`")
            return

    armControls = [shoulderCtrlL, elbowCtrlL, wristCtrlL, pointer01CtrlL, pointer02CtrlL, pointer03CtrlL, middle01CtrlL,
                   middle02CtrlL, middle03CtrlL, ring01CtrlL, ring02CtrlL, ring03CtrlL, pinky01CtrlL, pinky02CtrlL,
                   pinky03CtrlL]

    legControls = [legUpprCtrlL, kneeCtrlL]

    # Set to FK for arms and legs -------------------------------------
    cmds.setAttr("{}.ikfk".format(armLControlPanel), 1)
    cmds.setAttr("{}.ikfk".format(legLControlPanel), 1)

    # Do the T-Pose -------------------------------------
    rememberSel = cmds.ls(selection=True)
    cmds.select(shoulderCtrlL, replace=True)
    armLocator = locators.createLocatorAndMatch(name="zoo_tPoseArmMatch", handle=True, locatorSize=1.0)
    cmds.select(legUpprCtrlL, replace=True)
    legLocator = locators.createLocatorAndMatch(name="zoo_tPoseLegMatch", handle=True, locatorSize=1.0)

    if bipedType == "UE":  # Then the biped type is UE
        cmds.setAttr("{}.rotate".format(armLocator), 180, 0, 0)
        cmds.setAttr("{}.rotate".format(legLocator), -90, 0, 90)
    else:  # Standard
        cmds.setAttr("{}.rotate".format(armLocator), 0, 0, 0)
        cmds.setAttr("{}.rotate".format(legLocator), 180.0, 0, -90.0)

    for cntrl in armControls:
        cmds.matchTransform(cntrl, armLocator, rotation=True)

    for cntrl in legControls:
        cmds.matchTransform(cntrl, legLocator, rotation=True)

    cmds.setAttr("{}.rotate".format(footCtrlL), 0, 0, 0)

    # Mirror to the oppposite side -------------------------------------
    cmds.select(armControls + legControls + [footCtrlL], replace=True)
    mirroranim.flipPoseCtrlsSelected(flip=False, animation=False)

    # Return to original selection -------------------------------------
    cmds.select(rememberSel, replace=True)

    cmds.delete([armLocator, legLocator])


def setTPoseSel():
    """Sets the selected Hive Biped rigs to a T-Pose for the arms and legs.
    """
    if not cmds.ls(selection=True):
        output.displayWarning("Please select a control on a Hive Biped rig to set the T-Pose")
        return
    rigNames, namespaces = rigsFromNodesSelStr()
    if not rigNames:  # error message already displayed
        return
    for i, rigName in enumerate(rigNames):
        setTPose(rigName, namespaces[i])
