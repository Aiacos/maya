"""Module for matching Hive guides to rigs or skeletons.

from zoo.libs.hive.library.matching import matchguides
guideNamesDict = matchguides.hiveGuideNames(hiveRig, namespace="", hiveIdDict=mc.HIVE_BIPED_IDS)

from zoo.libs.hive.library.matching import matchconstants as mc
from zoo.libs.hive.library.matching import matchguides
hiveRigName = "biped"
skeletonDict = mc.HIVE_BIPED_SKELETON
matchguides.matchGuidesBipedSkeleton(hiveRigName, skeletonDict, hiveIdDict=mc.HIVE_BIPED_IDS, leftIdentifier="_L",
                                    rightIdentifier="_R", mirrorSuffixPrefix="",
                                    keyOrder=mc.HIERARCHY_ORDER_SPLINESPINE)

from zoo.libs.hive.library.matching import matchguides
matchguides.alignFeetGuideControls(legComponent)

"""

from maya import cmds

from zoo.libs.maya import zapi

from zoo.libs.hive.library.matching import (
    matchconstants as mc,
)  # todo move into maya repo, should be pointing to hive
from zoo.libs.maya.cmds.objutils import namehandling, alignutils
from zoo.libs.maya.cmds.rig import skeleton
from zoo.libs.utils import output
from zoo.libs.hive.base import rig
from zoo.libs.hive import api


def alignFeetGuideControls(legComponent, quadFix=False, preAlignComponent=True, message=True):
    """Aligns the foot controls of a leg component which can be annoying after aligning the leg.

    - Aligns controls and guides to the ground
    - Orients the controls and pivots to match the ankle to the ball of the foot direction.

    :param legComponent: rigInstance.leg_L
    :type legComponent: :class:`api.Component`
    :param preAlignComponent: Align the component before doing the control/guide alignment (recommended)
    :type preAlignComponent: bool
    :param message: Report the message to the user?
    :type message: bool
    """
    legGuideLayer = legComponent.guideLayer()
    if preAlignComponent:
        api.commands.autoAlignGuides([legComponent])

    # Get controls and guides -----------------------------------
    subsystems = legComponent.subsystems()
    footSubsystem, twistSubsystem = subsystems.get("foot"), subsystems["twists"]
    footActive = footSubsystem.active()
    if not footActive and not twistSubsystem.active():
        return
    guideIds = ["end", twistSubsystem.segmentTwistOffsetIds[-1]]
    if footActive:
        guideIds += list(footSubsystem.guideIds)
    guides = legGuideLayer.findGuides(*guideIds)
    guidesMap = {i.id(): i for i in guides if i is not None}
    if footActive:
        footGuide = guidesMap["end"]
        footControl = footGuide.shapeNode().fullPathName()
        outerGuide = guidesMap["outer_piv"].fullPathName()
        outerControl = guidesMap["outer_piv"].shapeNode().fullPathName()
        innerGuide = guidesMap["inner_piv"].fullPathName()
        innerControl = guidesMap["inner_piv"].shapeNode().fullPathName()
        heelGuide = guidesMap["heel_piv"].fullPathName()
        heelControl = guidesMap["heel_piv"].shapeNode().fullPathName()
        ballGuide = guidesMap["ball"].fullPathName()
        ballControl = guidesMap["ball"].shapeNode().fullPathName()
        toeGuide = guidesMap["toe"].fullPathName()
        toeControl = guidesMap["toeTip_piv"].shapeNode().fullPathName()
        ballBackControl = guidesMap["ballroll_piv"].shapeNode().fullPathName()

        # Align the feet controls to the ground ------------------------
        cmds.matchTransform(footControl, ballGuide, position=True)
        alignutils.placeObjectOnGroundList(
            [footControl, outerGuide, innerGuide, heelGuide, toeGuide], forcePivot=True
        )

        # Align the feet control and toe guide in the direction of the ball ------------------------
        locator = cmds.spaceLocator(name="hiveFootAim_Temp_loc")[0]
        cmds.setAttr("{}.rotateOrder".format(locator), 2)  # ZXY
        cmds.matchTransform(locator, footGuide.fullPathName(), rotation=True, position=True)
        locRot = cmds.getAttr("{}.rotate".format(locator))[0]
        if quadFix:
            cmds.setAttr("{}.rotate".format(locator), 0, locRot[1] + 90, 0)
        else:
            cmds.setAttr("{}.rotate".format(locator), 0, locRot[1] - 90, 0)
        cmds.matchTransform(footControl, locator, rotation=True)

        # Align the ball control and pivots -----------
        cmds.setAttr("{}.rotateY".format(ballControl), 0.0)
        cmds.setAttr("{}.rotateX".format(ballControl), 0.0)
        cmds.setAttr("{}.translateZ".format(ballControl), 0.0)
        cmds.setAttr("{}.rotateY".format(innerControl), 0.0)
        cmds.setAttr("{}.translateZ".format(innerControl), 0.0)
        cmds.setAttr("{}.rotateY".format(outerControl), 0.0)
        cmds.setAttr("{}.translateZ".format(outerControl), 0.0)
        if quadFix:
            cmds.setAttr("{}.rotateY".format(heelControl), 180.0)
            cmds.setAttr("{}.rotateZ".format(heelControl), 180.0)
            cmds.setAttr("{}.translateX".format(heelControl), 0.0)
        else:
            cmds.setAttr("{}.rotateY".format(heelControl), 180.0)
            cmds.setAttr("{}.translateX".format(heelControl), 0.0)

        cmds.setAttr("{}.rotateY".format(toeControl), 90.0)
        cmds.setAttr("{}.rotateZ".format(toeControl), 0)
        cmds.setAttr("{}.translateZ".format(toeControl), 0.0)
        if quadFix:
            cmds.setAttr("{}.rotateY".format(ballBackControl), 0)
            cmds.setAttr("{}.rotateX".format(ballBackControl), 0)
            cmds.setAttr("{}.translateZ".format(ballBackControl), 0.0)
        else:
            cmds.setAttr("{}.rotateY".format(ballBackControl), 90.0)
            cmds.setAttr("{}.translateZ".format(ballBackControl), 0.0)
        cmds.delete(locator)
    if twistSubsystem.active():
        lwrTwistArrow = legGuideLayer.guide("lwrTwistOffset").shapeNode().fullPathName()
        cmds.setAttr("{}.rotateY".format(lwrTwistArrow), 0.0)
        cmds.setAttr("{}.translateX".format(lwrTwistArrow), 0.0)
        cmds.setAttr("{}.translateY".format(lwrTwistArrow), 0.0)

    if message:
        output.displayInfo("Feet controls aligned")


def alignWristControls(armComponent, preAlignComponent=True, message=True):
    """Aligns the wrist controls of an arm component which can be annoying after aligning the arm.

    :param armComponent: hive component instance.
    :type armComponent: :class:`api.Component`
    :param preAlignComponent: Align the component before doing the control/guide alignment (recommended)
    :type preAlignComponent: bool
    :param message: Report the message to the user?
    :type message: bool
    """
    armGuideLayer = armComponent.guideLayer()
    if preAlignComponent:
        api.commands.autoAlignGuides([armComponent])

    # Align Wrists Back To Guide -----------------------------------
    endGuide, lwrTwistOffsetGuide = armGuideLayer.findGuides("end", "lwrTwistOffset")
    wristControl = endGuide.shapeNode().fullPathName()
    cmds.setAttr("{}.rotate".format(wristControl), 0, 0, 90)
    if lwrTwistOffsetGuide is not None:
        lwrTwistArrowControl = lwrTwistOffsetGuide.shapeNode().fullPathName()
        cmds.setAttr("{}.rotate".format(lwrTwistArrowControl), 90, 0, 0)
        cmds.setAttr("{}.translateX".format(lwrTwistArrowControl), 0)
        cmds.setAttr("{}.translateZ".format(lwrTwistArrowControl), 0)

    if message:
        output.displayInfo("Wrist controls aligned")


def hiveComponentIdSide():
    """From a selected hive control return the first "component, id and side" as a string.

    Example:
        "leg ball L"

    :return: the first selected "component, id and side" as a string.
    :rtype: str
    """
    selNodes = list(zapi.selected(filterTypes=zapi.kTransform))
    for node in selNodes:
        components = api.componentsFromNodes([node])
        if not components:
            return ""
        component = list(components.keys())[0]
        hiveComponentIdSide = " ".join(
            [
                component.componentType,
                api.ControlNode(node.object()).id(),
                component.side(),
            ]
        )
        return hiveComponentIdSide


def rigInstanceSafe(hiveRigName, namespace=""):
    """Returns the rig instance given and string name and namespace, if it does not exist it returns None

    :param hiveRigName: The string name of a Hive rig ie "zoo_mannequin"
    :type hiveRigName: str
    :param namespace: The namespace of the rig if it exists, otherwise leave blank ""
    :type namespace: str
    :return: A hive rig instance
    :rtype: :class:`api.Rig`
    """
    if not api.rootByRigName(hiveRigName, namespace):  # Doesn't exist
        if namespace:
            output.displayWarning("Rig `{}{}` not found".format(namespace, hiveRigName))
        else:
            output.displayWarning("Rig `{}` not found".format(hiveRigName))
        return None
    rigInstance = rig.Rig()
    if namespace:
        rigInstance.startSession(hiveRigName, namespace=namespace)
    else:
        rigInstance.startSession(hiveRigName, namespace="")
    return rigInstance


def skeletonOrderedList(
    skeletonDict=mc.HIVE_BIPED_SKELETON, order=mc.HIERARCHY_ORDER_SPLINESPINE
):
    """Returns a list of skeleton joints in the order given."""
    skeletonList = []
    for key in order:
        skeletonList.append(skeletonDict[key])
    return skeletonList


def hiveIdsDictToStringList(
    hiveIdDict=mc.HIVE_BIPED_SPLINE_IDS, order=mc.HIERARCHY_ORDER_SPLINESPINE
):
    """Returns a list of hive ids as strings in the order given.

    hiveIdsList = ["god root M", "arm root L", "arm end L", "arm root R"]

    :param hiveIdDict: The hive id dictionary each key contains a list of [component, id, side]
    :type hiveIdDict: dict(list)
    :param order: The order of the hive ids
    :type order: list(str)
    :return hiveIdsList: List of hive ids as strings
    :rtype hiveIdsList: list(str)
    """
    hiveIdsList = []
    for key in order:
        idList = hiveIdDict[key]
        hiveIdsList.append("{} {} {}".format(idList[0], idList[1], idList[2]))
    return hiveIdsList


def hiveIdStringListToDict(hiveIdStrings, order=mc.HIERARCHY_ORDER_SPLINESPINE):
    """Returns a dictionary of hive ids as strings in the order given.

    hiveIdStrings = ["god root M", "arm root L", "arm end L", "arm root R"]

    hiveIdsDict = {"god": ["god", "root", "M"],
                   "armL": ["arm", "root", "L"],
                   "armEndL": ["arm", "end, "L"],
                   "armR": ["arm", "root", "R"]}

    :param hiveIdStrings: A list of hive ids as strings
    :type hiveIdStrings: list(str)
    :param order: The order of the hive ids
    :type order: list(str)
    :return hiveIdsDict: Dictionary of hive ids as strings
    :rtype hiveIdsDict: dict(str)
    """
    # Todo not used?
    hiveIdsDict = {}
    for i, key in enumerate(order):
        idList = hiveIdStrings[i].split(
            " "
        )  # convert a string separated by spaces to a list
        if len(idList) != 3:
            output.displayWarning(
                "Entry {} formatted correctly, should be 3 strings separated by spaces".format(
                    str(i)
                )
            )
            return {}
        hiveIdsDict[key] = idList
    return hiveIdsDict


def guideStrName(rigInstance, component, id, side):
    """Returns the component, id and side as a string ie. "leg ball L"

    :param rigInstance: The rig instance
    :type rigInstance: :class:`api.Rig`
    :param component: The component name
    :type component: str
    :param id: The id name of the guide
    :type id: str
    :param side: The side of the guide
    :type side: str
    :return: Returns the component, id and side as a string ie. "leg ball L"
    :rtype: str
    """
    compInstance = rigInstance.component(component, side=side)
    if not compInstance:
        output.displayWarning("No component found: {}".format(component))
        return ""
    if not compInstance.hasGuide():
        output.displayWarning("No guides found for component: {}".format(component))
        return ""
    try:
        guideStr = compInstance.guideLayer().guide(id).fullPathName()
    except AttributeError:  # likely another spine type or guide that does not exist.
        return ""
    return guideStr


def hiveRigExists(hiveRigName, namespace=""):
    """Checks if a Hive rig exists in the scene.

    :param hiveRigName: The name of the Hive rig ie. "biped"
    :type hiveRigName: str
    :param namespace: The namespace of the rig in the scene, if it exists, otherwise leave blank ""
    :type namespace: str
    :return: True if the rig instance was found, false if not
    :rtype: bool
    """
    if rigInstanceSafe(hiveRigName, namespace=namespace):
        return True
    return False


def hiveGuideNames(hiveRigName, namespace="", hiveIdDict=mc.HIVE_BIPED_SPLINE_IDS):
    """Returns a dict of the hive guide names with each value being a fullpath string name.

    :param hiveRigName:
    :type hiveRigName: str
    :param hiveIdDict: The hive id dictionary each key contains a list of [component, id, side]
    :type hiveIdDict: dict(list)
    :return guideNames: List of guide names now with full path string names of the guides
    :rtype guideNames: dict(str)
    """
    rigInstance = rigInstanceSafe(hiveRigName, namespace=namespace)
    if not rigInstance:  # error message reported
        output.displayWarning("No rig instance found for {}".format(hiveRigName))
        return dict(), rigInstance
    guideNames = {}
    for key, value in hiveIdDict.items():
        component, idVal, side = value
        guideNames[key] = guideStrName(rigInstance, component, idVal, side)
    return guideNames, rigInstance


def calculateHeight(bottomJoint, topJoint):
    botSpace = cmds.xform(bottomJoint, query=True, worldSpace=True, translation=True)
    topSpace = cmds.xform(topJoint, query=True, worldSpace=True, translation=True)
    return abs(botSpace[1] - topSpace[1])


def scaleGuides(
    rootGuide,
    headGuide,
    spineRoot,
    topSpineGuide,
    headJoint,
    toeJoint,
    topSpineJoint,
    bottomSpineJoint,
    rigInstance,
):
    """

    :param rigInstance:
    :type rigInstance: :class:`api.Rig`
    """
    # Scale all guides ------------------
    guideHeight = calculateHeight(rootGuide, headGuide)
    currentGuideScale = cmds.getAttr("{}.scaleY".format(rootGuide))
    skeletonHeight = calculateHeight(headJoint, toeJoint)
    scaleSkeleton = (
        skeletonHeight / guideHeight * 1.1
    )  # make it a bit bigger for easier control selection
    newScale = currentGuideScale * scaleSkeleton
    cmds.setAttr("{}.globalScale".format(rootGuide), newScale)

    # Pin guides parented to the spine component ------------------
    spineComponent = rigInstance.componentsByType("spineIk")
    # no spineik found so exit
    if not spineComponent:
        return
    children = list(spineComponent[0].children(depthLimit=1))
    for i in children:
        i.pin()

    # Scale the spine guides ------------------
    guideSpineHeight = calculateHeight(spineRoot, topSpineGuide)
    spineSkeleHeight = calculateHeight(topSpineJoint, bottomSpineJoint)
    currentSpineGuideScale = cmds.getAttr("{}.scaleY".format(spineRoot))
    scaleSpine = spineSkeleHeight / guideSpineHeight
    newSpineScale = currentSpineGuideScale * scaleSpine
    cmds.setAttr("{}.globalScale".format(spineRoot), newSpineScale)

    # Unpin guides parented to the spine component ------------------
    for i in children:
        i.unPin()


def addNamespace(name, namespace):
    """Adds a namespace to a name, if the name already has a namespace it will add another one

    :param name: The name to add the namespace to
    :type name: str
    :param namespace: The namespace to add
    :type namespace: str
    :return name: The name with the namespace added
    :rtype name: str
    """
    if not namespace:
        return name
    return "{}:{}".format(namespace, name)


def hiveIdDictToList(hiveGuideIdsDict, orderList):
    """Returns a list of hive ids as strings in the order given.

    hiveIdsList = ["god root M", "arm root L", "arm end L", "arm root R"]

    :return hiveIdsList: List of hive ids as strings
    :rtype hiveIdsList: list(str)
    """
    hiveIdsList = []
    for key in orderList:
        idList = hiveGuideIdsDict[key]
        hiveIdsList.append("{} {} {}".format(idList[0], idList[1], idList[2]))
    return hiveIdsList


def skeletonDictToList(skeletonDict, orderList):
    """Returns a list of skeleton joints in the order given."""
    skeletonList = []
    for key in orderList:
        skeletonList.append(skeletonDict[key])
    return skeletonList


class BuildMatchGuidesSkele(object):
    """ """

    def __init__(
        self,
        sourceJntsList,
        targetHiveIdsList,
        order,
        rigName="biped",
        sourceNamespace="",
        sourcePrefix="",
        sourceSuffix="",
        autoJointCount=True,
        armUpTwistCount=5,
        armLowTwistCount=5,
        legUpTwistCount=5,
        legLowTwistCount=5,
        spineCount=6,
        autoTopSpineJoint=True,
        matchOnly=False,
    ):
        """Initialize variables for the class

        :param sourceJntsList: The source list of dictionaries
        :type sourceJntsList: dict(str)
        :param targetHiveIdsList: The target list of dictionaries
        :type targetHiveIdsList: dict(str)
        :param order: The order of the Hive IDs to match the guides, ie mc.HIERARCHY_ORDER_SPLINESPINE
        :type order: list(str)
        :param sourceNamespace: The source obj namespace, eg "skeletonReferenceName".
        :type sourceNamespace: str
        :param sourcePrefix: The source prefix eg "characterName_".  Source sometimes have the char as prefix
        :type sourcePrefix: str
        :param sourceSuffix: The source prefix eg "characterName_".  Source sometimes have the char as suffix
        :type sourceSuffix: str
        :param autoJointCount: Automatically set the twist and spine count for the arm, leg and spine components
        :type autoJointCount: bool
        :param armUpTwistCount: The number of twist joints for the upper arm. If autoJointCount is True this is ignored
        :type armUpTwistCount: int
        :param armLowTwistCount: The number of twist joints for the lower arm. If autoJointCount is True this is ignored
        :type armLowTwistCount: int
        :param legUpTwistCount: The number of twist joints for the upper leg. If autoJointCount is True this is ignored
        :type legUpTwistCount: int
        :param legLowTwistCount: The number of twist joints for the lower leg. If autoJointCount is True this is ignored
        :type legLowTwistCount: int
        :param spineCount: The number of joints for the spine. If autoJointCount is True this is ignored
        :type spineCount: int
        :param autoTopSpineJoint: Automatically find the top spine joint, if False uses the topSpineGuide
        :type autoTopSpineJoint: bool
        :param matchOnly: Only match the guides, do not build the rig
        :type matchOnly: bool
        """
        super(BuildMatchGuidesSkele, self).__init__()
        self.sourceJntsList = sourceJntsList
        self.targetHiveIdsList = targetHiveIdsList
        self.order = order
        self.rigName = rigName
        self.sourceNamespace = sourceNamespace
        self.sourcePrefix = sourcePrefix
        self.sourceSuffix = sourceSuffix
        self.autoJointCount = autoJointCount
        self.armUpTwistCount = armUpTwistCount
        self.armLowTwistCount = armLowTwistCount
        self.legUpTwistCount = legUpTwistCount
        self.legLowTwistCount = legLowTwistCount
        self.spineCount = spineCount
        self.autoTopSpineJoint = autoTopSpineJoint
        self.matchOnly = matchOnly
        # Guides to be assigned later
        self.rootGuide = ""
        self.headGuide = ""
        self.spineRoot = ""
        self.topSpineGuide = ""
        # Joints to be assigned later
        self.headJoint = ""
        self.toeJoint = ""
        self.topSpineJoint = ""
        self.bottomSpineJoint = ""
        # rig instance to be assigned later
        self.rigInstance = None
        self.skeletonDict = dict()
        self.hiveGuideNameDict = dict()
        self.hiveGuideIdsDict = dict()
        self.leftComponents = list()
        self.allComponents = list()
        self.leftComponents = list()

    def _renameObj(self, name, namespace, prefix, suffix):
        """Renames an object with a namespace, prefix and suffix.  Does not perform a Maya rename.

        Returns the new name.

        :param name: obj string name
        :type name: str
        :param namespace: The obj namespace, eg "characterX". Note a semicolon will be added.
        :type namespace: str
        :param prefix: Adds a prefix to the object name eg "prefix_" for prefix_pCube1
        :type prefix: str
        :param suffix: Adds a suffix to the object name eg "_suffix" for pCube1_suffix
        :type suffix: str
        :return: obj string name now renamed
        :rtype: str
        """
        return namehandling.renameNamespaceSuffixPrefix(name, namespace, prefix, suffix)

    def _buildObjectLists(self):
        """Returns lists of source bound joints, and target joints."""
        self.sourceJntsRenamed = list()
        if (
            not self.sourceJntsList
        ):  # can't build the names, not needed till the transfer
            return self.sourceJntsRenamed

        for sourceJnt in self.sourceJntsList:
            # Add name prefix and namespaces -------------------------------------
            sourceJnt = self._renameObj(
                sourceJnt, self.sourceNamespace, self.sourcePrefix, self.sourceSuffix
            )
            self.sourceJntsRenamed.append(sourceJnt)

        for i, k in enumerate(self.order):
            self.skeletonDict[k] = self.sourceJntsRenamed[i]
            idStr = self.targetHiveIdsList[i]
            self.hiveGuideIdsDict[k] = idStr.split(" ")

        return self.sourceJntsRenamed

    def _someJointsExist(self):
        """Checks if any source joints exist in the scene"""
        someJointExists = False
        for jnt in self.sourceJntsRenamed:
            if cmds.objExists(jnt):
                someJointExists = True
        return someJointExists

    def _spineJointList(self):
        for jnt in self.sourceJntsRenamed:
            if "spine" in jnt:
                return jnt

    def _buildRig(self):
        if (
            not hiveRigExists(self.rigName, namespace="") and self.rigName
        ):  # Then build the rig
            path = api.Configuration().templateRegistry().templatePath(self.rigName)
            r, components = api.commands.loadTemplate(path)
            self.rigInstance = r

    def _guideStrFromId(self, idVal):
        """Returns a guide string name from a hive id

        :param id: The hive id as a tuple (component, id, side)
        :type id: tuple(str)
        :return guideStr: The full path string name of the guide
        :rtype guideStr: str
        """
        return guideStrName(self.rigInstance, idVal[0], idVal[1], idVal[2])

    def _jointsAndIds(self):
        """Retrieves and stores names for the guides rootGuide, headGuide, spineRoot, topSpineGuide
        and joints headJoint, toeJoint, topSpineJoint, bottomSpineJoint"""
        self.rootGuide = self.hiveGuideNameDict[mc.ROOT_KEY]
        self.headGuide = self.hiveGuideNameDict[mc.HEAD_KEY_M]
        self.spineRoot = self.hiveGuideNameDict[mc.HIP_KEY_M]
        self.topSpineGuide = self.hiveGuideNameDict[mc.CHEST_KEY_M]

        self.headJoint = self.skeletonDict[mc.HEAD_KEY_M]
        self.toeJoint = self.skeletonDict[mc.BALL_KEY_L]
        self.bottomSpineJoint = self.skeletonDict[mc.HIP_KEY_M]
        if self.autoTopSpineJoint:
            skeletonInstance = skeleton.IdentifySkeleton(self.bottomSpineJoint)
            skeletonInstance.skeletonFormat()
            spineJoints = skeletonInstance.spineJoints()
            if spineJoints:  # auto find the top spine joint
                self.topSpineJoint = spineJoints[-1]
                output.displayInfo(
                    "Auto found the top spine joint: {}".format(self.topSpineJoint)
                )
            else:
                output.displayWarning("Failed to auto find the top spine joint")
        if not self.topSpineJoint:  # if auto has failed or not run
            self.topSpineJoint = self.skeletonDict[mc.CHEST_KEY_M]

    def _pinGuides(self, pin=True):
        """Pins the guides parented to the spine component.  If pin is False unpins the guides."""
        if pin:
            self.rigInstance.component("leg", side="L").pin()
            self.rigInstance.component("leg", side="R").pin()
            self.rigInstance.component("clavicle", side="L").pin()
            self.rigInstance.component("clavicle", side="R").pin()
            self.rigInstance.component("head", side="M").pin()
        else:
            self.rigInstance.component("leg", side="L").unPin()
            self.rigInstance.component("leg", side="R").unPin()
            self.rigInstance.component("clavicle", side="L").unPin()
            self.rigInstance.component("clavicle", side="R").unPin()
            self.rigInstance.component("head", side="M").unPin()

    def _scaleGuides(self):
        # Scale all guides ------------------
        guideHeight = calculateHeight(self.rootGuide, self.headGuide)
        currentGuideScale = cmds.getAttr("{}.scaleY".format(self.rootGuide))
        skeletonHeight = calculateHeight(self.headJoint, self.toeJoint)
        scaleSkeleton = (
            skeletonHeight / guideHeight * 1.1
        )  # make it a bit bigger for easier control selection
        newScale = currentGuideScale * scaleSkeleton
        cmds.setAttr("{}.globalScale".format(self.rootGuide), newScale)  # global scale and no longer scale

        # Pin guides parented to the spine component ------------------
        self._pinGuides(pin=True)

        # Scale the spine guides ------------------
        guideSpineHeight = calculateHeight(self.spineRoot, self.topSpineGuide)
        spineSkeleHeight = calculateHeight(self.topSpineJoint, self.bottomSpineJoint)
        currentSpineGuideScale = cmds.getAttr("{}.scaleY".format(self.spineRoot))
        scaleSpine = spineSkeleHeight / guideSpineHeight
        newSpineScale = currentSpineGuideScale * scaleSpine
        cmds.setAttr("{}.globalScale".format(self.spineRoot), newSpineScale)

        # Unpin guides parented to the spine component ------------------
        self._pinGuides(pin=False)

    def _snapMatchGuides(self):
        for k in self.order:
            if k not in self.skeletonDict:
                continue
            rotMatch = False
            joint = self.skeletonDict[k]
            if k in mc.ROT_ALIGN_GUIDES:  # rot match fingers
                rotMatch = True
            if not joint or not self.hiveGuideNameDict[k]:
                output.displayWarning(
                    "Object not found `{}` or `{}`".format(
                        joint, self.hiveGuideNameDict[k]
                    )
                )
                output.displayWarning(
                    "No guide or skeleton joint found for {}".format(k)
                )
                continue
            if not cmds.objExists(joint):
                output.displayWarning("Joint does not exist: {}".format(joint))
                continue
            cmds.matchTransform(
                self.hiveGuideNameDict[k],
                joint,
                pos=True,
                rot=rotMatch,
                scl=False,
                piv=False,
            )

    def _components(self):
        """Generate all the left and all component lists"""
        for key in self.hiveGuideIdsDict:
            componentName = self.hiveGuideIdsDict[key][0]
            sideName = self.hiveGuideIdsDict[key][2]
            component = self.rigInstance.component(componentName, side=sideName)
            self.allComponents.append(component)
            if "_L" in key:
                self.leftComponents.append(component)
                # add right component to all components
                self.allComponents.append(
                    self.rigInstance.component(componentName, side="R")
                )
        self.leftComponents = list(set(self.leftComponents))  # remove duplicates
        self.allComponents = list(set(self.allComponents))  # remove duplicates

    def _applySymmetry(self):
        api.commands.applySymmetry(self.rigInstance, self.leftComponents)

    def _alignAllGuides(self):
        api.commands.autoAlignGuides(self.allComponents)

    def _setSpineCount(self):
        spineComponent = self.rigInstance.component("spine", side="M")
        components = list(spineComponent.children(depthLimit=1))
        with api.componentutils.disconnectComponentsContext(components):
            api.commands.updateGuideSettings(
                spineComponent, {"jointCount": self.spineCount}
            )
            guideId = spineComponent.jointIdForNumber(self.spineCount - 1)
            spineGuide = spineComponent.guideLayer().guide(guideId)
            # Need to update parenting
            for comp in components:
                if comp.componentType == "legcomponent":
                    continue
                comp.setParent(spineComponent, driver=spineGuide)

    def _twistSpineCount(self):
        """Sets the twist and spine count for the arm, leg and spine components."""
        if self.autoJointCount:
            (
                self.armUpTwistCount,
                self.armLowTwistCount,
                self.legUpTwistCount,
                self.legLowTwistCount,
                self.spineCount,
            ) = skeleton.getTwistSpineCount(self.bottomSpineJoint)

        if self.armUpTwistCount < 3:
            self.armUpTwistCount = 3
        if self.armLowTwistCount < 3:
            self.armLowTwistCount = 3
        if self.legUpTwistCount < 3:
            self.legUpTwistCount = 3
        if self.legLowTwistCount < 3:
            self.legLowTwistCount = 3
        if self.spineCount < 2:
            self.spineCount = 2

        for component in self.allComponents:
            componentType = component.componentType
            if componentType == "armcomponent":
                api.commands.updateGuideSettings(
                    component, {"uprSegmentCount": self.armUpTwistCount,
                                "lwrSegmentCount": self.armLowTwistCount}
                )
            if componentType == "legcomponent":
                api.commands.updateGuideSettings(
                    component, {"uprSegmentCount": self.legUpTwistCount,
                                "lwrSegmentCount": self.legLowTwistCount}
                )
            if componentType == "spineIk":
                # self._pinGuides(pin=True)
                # api.commands.updateGuideSettings(component, {"jointCount": self.spineCount})
                self._setSpineCount()
                # self._pinGuides(pin=False)
            if componentType == "spineFk":
                api.commands.updateGuideSettings(
                    component, {"jointCount": self.spineCount}
                )

    def _alignControls(self):
        """Snaps the foot ctrls to the floor. orients various controls including the wrist controls."""
        alignFeetGuideControls(
            self.rigInstance.leg_L, preAlignComponent=True, message=True
        )
        alignWristControls(self.rigInstance.arm_L, preAlignComponent=True, message=True)

    def stage1_basicChecks(self):
        if not self.sourceJntsList or not self.targetHiveIdsList:
            output.displayWarning("No matching Joints or Hive Ids in the table.")
            return False
        self._buildObjectLists()  # renames and creates self.skeletonDict and self.hiveGuideIdsDict
        # Check joints exist ---------------
        if not self._someJointsExist():
            output.displayWarning(
                "No joints have been found in the scene, check namespace and naming."
            )
            return False
        return True

    def stage2_BuildRig(self):
        if not self.matchOnly:
            self._buildRig()
        # Check joints are valid and that valid joints exist ---------------
        self.hiveGuideNameDict, self.rigInstance = hiveGuideNames(
            self.rigName, namespace="", hiveIdDict=self.hiveGuideIdsDict
        )
        if not self.hiveGuideNameDict:  # error message reported
            return False
        return self.rigInstance

    def stage3_MatchGuides(self):
        # Scale the guides ---------------------------------------------------
        self._jointsAndIds()
        self._scaleGuides()
        # Snap match the guides ---------------------------------------------------
        self._snapMatchGuides()
        # Generate all the left and all component lists -------------------
        self._components()
        # Align all guides ---------------------------------------------------
        self._alignAllGuides()  # TODO can skip right side

    def stage4_FinalAlignment(self):
        # Snap the foot ctrls to the ground, reset wrists ---------------------------------------
        self._alignControls()
        # Apply Symmetry left guides to right ---------------------------------------------------
        self._applySymmetry()

    def stage5_TwistSpineCount(self):
        # Add twist and spine count ---------------------------------------------------
        self._twistSpineCount()

    def buildAndMatch(self):
        """Matches Hive biped guides to a skeleton using hive ids to find guides.
        TODO Aim the spine bottom at the top spine, maybe not?

        """
        if not self.stage1_basicChecks():
            return False

        if not self.stage2_BuildRig():
            return False

        self.stage3_MatchGuides()

        self.stage4_FinalAlignment()

        self.stage5_TwistSpineCount()

        output.displayInfo("Success: Matched Hive guides to skeleton successfully.")
        return self.rigInstance
