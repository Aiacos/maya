"""
from zoo.libs.hive.library.matching import buildskinfromskele
buildInstance = buildskinfromskele.BuildAndSkinFromSkeleton()
buildInstance.buildAndSkinSel(skinTransfer=True, buildRig=True, skinJointTransfer=True)

"""

from maya import cmds

from zoo.libs.utils import output

from zoo.libs.hive.library.matching import matchguides
from zoo.libs.hive import api
from zoo.libs.maya.cmds.skin import skinreplacejoints, bindskin
from zoo.libs.maya.cmds.rig import skeleton
from zoo.libs.maya.cmds.objutils import namehandling, filtertypes, attributes
from zoo.libs.maya.cmds.animation import batchconstraintconstants as bcc
from zoo.libs.hive.library.matching import matchconstants as mc
from zoo.libs.maya.cmds.shaders import shadermulti
from zoo.libs.maya.cmds.shaders.shadertypes import mayastandardsurface
from zoo.libs.utils import color


PROXY_MESH_HIVE = "proxyHiveMesh_geo"
SKIN_PROXY_GEO = "skinProxy_geo"


def autoGetSkinProxyGeoAndBaseJoint():
    """Automatically finds the skin proxy geometry and the base joint of the skin proxy skeleton.

    :return: baseJoint, proxyMesh
    :rtype: tuple(str,str)
    """
    sel = cmds.ls(selection=True)
    baseJoint, proxyMesh = skinProxyBaseJoint(message=False)
    cmds.select(sel, replace=True)
    return baseJoint, proxyMesh


def skinProxyBaseJoint(message=True):
    """Returns the base joint of the skin proxy skeleton and automatically tries to find the skin proxy mesh.

    If nothing is selected it will try to find both the skin proxy mesh and base joint automatically.

    :return: The base joint of the skin proxy skeleton and the skin proxy mesh
    :rtype: tuple(str, str)
    """
    godJoints = ""
    selJoints = cmds.ls(selection=True, type="joint")
    if not selJoints:
        godJoints = cmds.ls("*god_M_godnode_jnt*", type="joint")
        if not godJoints:  # try namespaces
            godJoints = cmds.ls("*:god_M_godnode_jnt*", type="joint")
        if not godJoints:
            if message:
                output.displayWarning("Please select the root joint of the skeleton, or import a known skin proxy rig.")
            return "", ""
        if len(godJoints) > 1:
            if message:
                output.displayWarning("Please select the root joint of the skeleton, more than one root joint found.")
            return "", ""
    if godJoints:
        selJoints = godJoints
    if len(selJoints) == 1:
        childJoints = cmds.listRelatives(selJoints[0], children=True, type="joint")
        if childJoints:
            skinClusters = bindskin.getSkinClusterFromJoint(childJoints[0])
            if len(skinClusters) == 1:
                geo = bindskin.geoFromSkinCluster(skinClusters[0])
                if len(geo) == 1:
                    meshUniqueName = namehandling.getUniqueShortName(geo[0])
                    return selJoints[0], meshUniqueName
    return selJoints[0], ""


def skinProxySkinnedGeo():
    """Returns the skin proxy mesh and then automatically finds the root joint of the skeleton.

    If nothing is selected it will try to find the skin proxy mesh and root joint automatically.

    :return: The skin proxy mesh and the root joint of the skeleton
    :rtype: tuple(str, str)
    """
    proxyMeshes = ""
    selGeo = cmds.ls(selection=True, type="transform")
    if not selGeo:
        proxyMeshes = cmds.ls("*skinProxy_geo*", type="transform")
        if not proxyMeshes:
            output.displayWarning("Please select the skin proxy mesh, this mesh should be skinned.")
            return "", ""
        if len(proxyMeshes) > 1:
            output.displayWarning("Please select the skin proxy mesh, more than one skin proxy mesh found.")
            return "", ""
    if proxyMeshes:
        selGeo = proxyMeshes
    if not bindskin.filterSkinnedMeshes(selGeo):
        output.displayWarning("Mesh {} is not skinned".format(selGeo[0]))
        return "", ""
    mesh = selGeo[0]
    skinCluster = bindskin.getSkinCluster(mesh)
    if not skinCluster:
        return mesh, ""
    joints = bindskin.jointsFromSkinCluster(skinCluster)
    for jnt in joints:
        parentJoint = cmds.listRelatives(jnt, parent=True, type="joint")
        if parentJoint:
            if "god_M_godnode_jnt" in parentJoint[0]:
                return mesh, parentJoint[0]
    return mesh, ""


def targetGeoObjectsAsString():
    """Returns the target geometry objects as a string for the UI, will check that the geo is not skinned

    :return: The target geo as a singgle string "geo1, geo2, geo3"
    :rtype: str
    """
    selGeo = cmds.ls(selection=True, type="transform", long=True)
    if not selGeo:
        output.displayWarning("Please select geometry that will be automatically skinned to the Hive rig.")
        return ""
    geo = filtertypes.filterGeoOnly(selGeo, fullpath=True)
    if not geo:
        output.displayWarning("Objects must be able to be skinned")
        return ""
    geo = list(set(cmds.listRelatives(geo, parent=True, fullPath=True)))  # get the transforms
    skinnedGeo = bindskin.filterSkinnedMeshes(geo)
    if skinnedGeo:
        output.displayWarning("Mesh already skinned {}".format(skinnedGeo))
        return ""
    if len(geo) == 1:
        return geo[0]
    return ", ".join(geo)


def allRigsInScene():
    """Returns a list of rig instances, names and namespaces from the scene's Hive rigs.

    :return: A list of rig instances, names and namespaces
    :rtype: tuple(list(:class:`api.Rig`), list(str), list(str))
    """
    rigNames = list()
    rigNamespaces = list()
    rigInstances = list(api.iterSceneRigs())
    if not rigInstances:
        return list(), list(), list()
    for rigInstance in rigInstances:
        rigNames.append(rigInstance.name())
        rigNamespaces.append(rigInstance.meta.namespace())
    return rigInstances, rigNames, rigNamespaces


class BuildAndSkinFromSkeleton(object):
    """
    """

    def __init__(self,
                 hiveRigType=bcc.HIVE_BIPED_K,
                 rigName="biped",
                 polishRig=True,
                 sourceNamespace="",
                 sourcePrefix="",
                 sourceSuffix="",
                 sourceLeftIdentifier="_L",
                 sourceRightIdentifier="_R",
                 sourceLRIsPrefix=False,
                 sourceLRIsSuffix=False,
                 sourceLRSeparatorOnBorder=False,
                 autoDiscover=True,
                 autoJointCount=True,
                 armUpTwistCount=5,
                 armLowTwistCount=5,
                 legUpTwistCount=5,
                 legLowTwistCount=5,
                 spineCount=6,
                 skinProxyGeo="",
                 skinTargetGeoList=list(),
                 unbindProxyGeo=True
                 ):
        """Initialize variables for the class

        :param hiveRigType: The type of Hive rig to build, eg bcc.HIVE_BIPED_K
        :type hiveRigType: str
        :param sourceNamespace: The source obj namespace, eg "skeletonReferenceName". Note a semicolon will be added.
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
        :param skinProxyGeo: The skin proxy geometry to transfer the skin weights from
        :type skinProxyGeo: str
        :param skinTargetGeoList: The list of target geometry to transfer the skin weights to
        :type skinTargetGeoList: list(str)
        :param unbindProxyGeo: Unbind the proxy geometry after transferring the skin weights
        :type unbindProxyGeo: bool
        """
        super(BuildAndSkinFromSkeleton, self).__init__()
        self.hiveRigType = hiveRigType
        self.rigName = rigName
        self.polishRig = polishRig
        self.sourceNamespace = sourceNamespace
        self.sourcePrefix = sourcePrefix
        self.sourceSuffix = sourceSuffix
        self.sourceLeftIdentifier = sourceLeftIdentifier
        self.sourceRightIdentifier = sourceRightIdentifier
        self.sourceLRIsSuffix = sourceLRIsSuffix
        self.sourceLRIsPrefix = sourceLRIsPrefix
        self.sourceLRSeparatorOnBorder = sourceLRSeparatorOnBorder
        self.autoDiscover = autoDiscover
        self.autoJointCount = autoJointCount
        self.armUpTwistCount = armUpTwistCount
        self.armLowTwistCount = armLowTwistCount
        self.legUpTwistCount = legUpTwistCount
        self.legLowTwistCount = legLowTwistCount
        self.spineCount = spineCount
        self.skinProxyGeo = skinProxyGeo
        self.skinTargetGeoList = skinTargetGeoList
        self.unbindProxyGeo = unbindProxyGeo
        # Class Generated Variables -----------------------------------
        self.proxyMeshHive = ""  # The duplicate of the proxy mesh for the hive rig
        self.skeletonType = ""  # Type of skeleton, eg "HIVE Biped Strd Jnts", dict key eg bcc.HIVE_BIPED_JNTS_K
        self.sourceMatchJntsList = list()  # List of matching source joints for building the rig
        self.hiveTargetJoints = list()  # List of matching hive target joints for transfer after building the rig
        self.targetHiveIdsList = list()  # List of matching hive IDs for the rig build
        self.hierarchyOrder = list()  # The hierarchy order of the hive rig
        self.rigInstance = None  # the hive rig instance after building
        self.oldNamespace = "skinProxy"  # The namespace of the source joints be renamed if they have no namespace

    def transferSkinMeshWeights(self, sourceMesh, targetMeshes):
        """Transfer the skin weights from the proxy mesh to the target meshes
        """
        for targetMesh in targetMeshes:
            bindskin.transferSkinning(sourceMesh, targetMesh)

    def hiveTargetJoints(self):
        return self.hiveTargetJoints

    def transferJointWeights(self):
        """Transfer the joint weights from the source skeleton to the new rig
        """
        proxyMeshSkinClusters = list()
        if self.skinProxyGeo:
            proxyMeshSkinClusters = bindskin.getSkinCluster(self.skinProxyGeo)
        transferInstance = skinreplacejoints.ReplaceJointsWeights(
            self.sourceJntsAll,
            self.hiveTargetJoints,
            skipSkinClusters=proxyMeshSkinClusters,
            moveWithJoints=False,
            unbindSource=self.unbindProxyGeo,
            sourceNamespace=self.sourceNamespace,
            sourcePrefix=self.sourcePrefix,
            sourceSuffix=self.sourceSuffix,
            autoLeftToRight=True,
            sourceLeftIdentifier=self.sourceLeftIdentifier,
            sourceRightIdentifier=self.sourceRightIdentifier,
            sourceLRIsPrefix=self.sourceLRIsPrefix,
            sourceLRIsSuffix=self.sourceLRIsSuffix,
            sourceLRSeparatorOnBorder=self.sourceLRSeparatorOnBorder,
        )
        transferInstance.replaceJointsWeights(message=True)

    def _sourceJntsList(self, skeletonType):
        """Gets the skeleton dict from match constants

        :param skeletonType: The type of Hive skeleton to build, eg bcc.HIVE_BIPED_JNTS_K
        :type skeletonType: str
        :return: list of source joints
        :rtype: list(str)
        """
        for skeleTuple in mc.SKELETONS:
            if skeletonType == skeleTuple[0]:
                skeletonList = matchguides.skeletonDictToList(skeleTuple[1], self.hierarchyOrder)
                return skeletonList
        return list()

    def _targetHiveIdsList(self, hiveRigType):
        """Gets the hive dict and hierarchy order from match constants

        :param hiveRigType: The type of Hive rig to build, eg bcc.HIVE_BIPED_K
        :type hiveRigType: str
        :return:
        :rtype:
        """
        for hiveTuple in mc.HIVE_IDS:
            if hiveRigType == hiveTuple[0]:
                orderList = hiveTuple[2]
                hiveIdList = matchguides.hiveIdDictToList(hiveTuple[1], orderList)
                return hiveIdList, orderList
        return list(), list()

    def _jointListFromKey(self, rigSkeleKey=bcc.HIVE_BIPED_K, convertRigToSkele=True):
        """From a dictionary key such as bcc.HIVE_BIPED_K or bcc.HIVE_BIPED_JNTS_K will return a list of joint names.

        :param rigSkeleKey:  eg a rig key bcc.HIVE_BIPED_K or bcc.HIVE_BIPED_JNTS_K if a skeleton, auto converts
        :type rigSkeleKey: str
        :param convertRigToSkele: If True will convert the rig key to a skeleton key
        :type convertRigToSkele: bool
        :return: The list of joints that match the rig type
        :rtype: list(str)
        """
        if convertRigToSkele:
            skeletonKey = bcc.HIVE_RIG_JOINT_KEYS[rigSkeleKey]
        else:
            skeletonKey = rigSkeleKey
        hiveTargetJoints = list()
        for nodeOptionDict in bcc.SKELETON_TWIST_MAPPINGS:
            # get the first key in the nodeOptionDict
            if skeletonKey == next(iter(nodeOptionDict)):
                nodeDict = nodeOptionDict[skeletonKey]["nodes"]
                hiveTargetJoints = bcc.nodeDictToList(nodeDict)
                break
        if hiveTargetJoints:
            return hiveTargetJoints
        output.displayWarning("Could not find joints that match the hive rig type")
        return hiveTargetJoints

    def _skeleAndRigTypes(self):
        """Sets all the skeleton and hive lists/dicts for use in the build and skin transfers.

        :return: Success if True, False if not.
        :rtype: bool
        """
        self.hiveTargetJoints = self._jointListFromKey(self.hiveRigType, convertRigToSkele=True)
        self.sourceJntsAll = self._jointListFromKey(self.skeletonType, convertRigToSkele=False)
        self.targetHiveIdsList, self.hierarchyOrder = self._targetHiveIdsList(self.hiveRigType)
        self.sourceMatchJntsList = self._sourceJntsList(self.skeletonType)
        if not self.sourceMatchJntsList:
            output.displayWarning("Could not find the skeleton type `{}` "
                                  "in the match constants".format(self.skeletonType))
            return False
        if not self.hiveTargetJoints:
            output.displayWarning("Could not find the hive skeleton for ``".format(self.hiveRigType))
            return False
        return True

    def _namespaceProxyJoints(self, baseJoint):
        """Will namespace all skin proxy joints if they don't have a namespace.

        This is to avoid clashes with the Hive skeleton as the transfer is name based as per the Joint transfer UI.

        :param baseJoint: The base joint of the skin proxy skeleton
        :type baseJoint: str
        """
        jnts = skeleton.jointHierarchy(baseJoint)
        if ":" in baseJoint:
            return  # self.sourceNamespace should be set correctly
        renameList = list()
        for i, jnt in enumerate(jnts):
            if cmds.objExists(jnt):
                renameList.append(jnt)
        if renameList:
            namehandling.createAssignNamespaceList(renameList, self.oldNamespace)
        self.sourceNamespace = self.oldNamespace

    def _uiObjsExist(self, baseJoint):
        """Checks if the expected objects exist in the current scene.

        :param baseJoint: The base joint of the skin proxy skeleton
        :type baseJoint: str
        :return: Success if True, False if not.
        :rtype: bool
        """
        if not cmds.objExists(baseJoint):
            output.displayWarning("Base joint does not exist")
            return False
        if not namehandling.stringNameIsUnique(baseJoint):
            output.displayWarning("The Base Joint name is not unique, please rename.")
            return False
        if self.skinProxyGeo and not cmds.objExists(self.skinProxyGeo):
            output.displayWarning("Skin proxy geometry does not exist")
            return False
        if not namehandling.stringNameIsUnique(self.skinProxyGeo):
            output.displayWarning("The Skin Proxy Geo name is not unique, please rename.")
            return False
        if self.skinTargetGeoList:
            for geo in self.skinTargetGeoList:
                if not cmds.objExists(geo):
                    output.displayWarning("Skin target geometry does not exist")
                    return False
        return True

    def _shaderDuplicate(self, offsetColors):
        """Duplicates the skin proxy shaders assigns to the Hive proxy mesh geo.
         Offset hue on the shader colors on the proxy mesh to show has finished.

        :param offsetColors: Do you want to offset the colors and duplicate the shaders?
        :type offsetColors: bool
        """
        newShadInsts = list()
        hiveMeshList = list()
        if not offsetColors and not SKIN_PROXY_GEO in self.skinProxyGeo:
            return
        shaderInsts = shadermulti.shaderInstancesFromNodes([self.proxyMeshHive])
        for shaderInst in shaderInsts:
            assignedGeo = shaderInst.assignedGeo()
            shadName = shaderInst.shaderName().split(":")[-1]
            shaderValueDict = shaderInst.shaderValues()
            newShadInst = mayastandardsurface.StandardSurface(shadName,
                                                              create=True,
                                                              genAttrDict=shaderValueDict)  # creates a new shader
            newShadInsts.append(newShadInst)
            for geo in assignedGeo:
                if "skinProxy:" in geo:
                    continue
                hiveMeshList.append(geo)
            newShadInst.assign(hiveMeshList)
            hiveMeshList = list()

        for shaderInst in newShadInsts:
            hsv = color.convertRgbToHsv(shaderInst.diffuse())
            hsv = color.offsetHueColor(hsv, 15.0)
            shaderInst.setDiffuse(color.convertHsvToRgb(hsv))

    def stage1_basicChecks(self, baseJoint):
        """Runs the basic check for the scene and creates all the variables and skeletons, checks if the objects exist.

        :param baseJoint: The base joint of the skin proxy skeleton
        :type baseJoint: str
        :return: Success if True, False if not.
        :rtype: bool
        """

        # check that if there is any target geo that it is unique
        if self.skinTargetGeoList:
            for obj in self.skinTargetGeoList:
                if not cmds.objExists(obj):
                    output.displayWarning("`{}` does not exist. Please remove or rename in the UI".format(obj))
                    return False
                if not namehandling.stringNameIsUnique(obj):
                    output.displayWarning("`{}` is not unique. The target geometry must have unique names.  "
                                          "Please rename.".format(obj))
                    return False
        # check the rig isn't built.
        rigInstances, names, namespaces = allRigsInScene()
        if rigInstances:
            output.displayWarning("A Hive rig already exists in the scene.  "
                                  "Please remove the rig before building a new one.")
            return False
        if not self._uiObjsExist(baseJoint):
            return False  # Message reported
        # Check namespace on the skeleton
        self.sourceNamespace = namehandling.nameSpace(baseJoint, multi=True)
        # Discover the skeleton and set type
        skeletonInst = skeleton.IdentifySkeleton(baseJoint)
        self.skeletonType = skeletonInst.skeletonFormat()
        if not self.skeletonType:
            output.displayWarning(
                "Could not identify the skeleton type.  Please select the root joint of a known skeleton.")
            return False
        if not self._skeleAndRigTypes():  # Message reported
            return False
        return True

    def stage2_duplicateSkinProxyMesh(self):
        self.proxyMeshHive = cmds.duplicate(self.skinProxyGeo,
                                            name=namehandling.generateUniqueName(PROXY_MESH_HIVE))[0]
        bindskin.cleanDeadOrigShapes([self.proxyMeshHive], displayMessage=False)  # Delete shape orig node
        attributes.unlockSRTV(self.proxyMeshHive,
                              translate=True,
                              rotate=True,
                              scale=True,
                              visibility=False,
                              lock=False,
                              keyable=True)
        self.transferSkinMeshWeights(sourceMesh=self.skinProxyGeo, targetMeshes=[self.proxyMeshHive])

    def stage3_buildRig(self, baseJoint, buildRig):
        """Builds the Hive rig and renames the proxy joints if they have no namespace.

        :param baseJoint: The base joint of the skin proxy skeleton
        :type baseJoint: str
        :param buildRig: True if you'd like to build the rig
        :type buildRig: bool
        :return: True if successful, False if not.
        :rtype: bool
        """
        # Add namespace to the source joints if there is none, as may clash with the rig joints
        self._namespaceProxyJoints(baseJoint)

        # Build the rig
        self.buildMatchInstance = matchguides.BuildMatchGuidesSkele(self.sourceMatchJntsList,
                                                                    self.targetHiveIdsList,
                                                                    order=self.hierarchyOrder,
                                                                    rigName=self.rigName,
                                                                    sourceNamespace=self.sourceNamespace,
                                                                    sourcePrefix=self.sourcePrefix,
                                                                    sourceSuffix=self.sourceSuffix)
        if not self.buildMatchInstance.stage1_basicChecks():
            return False
        self.rigInstance = self.buildMatchInstance.stage2_BuildRig()
        if not self.rigInstance:
            return False
        return True

    def stage4_matchGuides(self):
        """Matches the guides to the skeleton

        :return: True if successful, False if not.
        :rtype: bool
        """
        self.buildMatchInstance.stage3_MatchGuides()

    def stage5_FinalAlignment(self):
        """Does the final controls alignment on the rig, applies symmetry

        :return: True if successful, False if not.
        :rtype: bool
        """
        self.buildMatchInstance.stage4_FinalAlignment()
        output.displayInfo("Success: Matched Hive guides to skeleton successfully.")

    def stage6_twistingSpineCount(self):
        """Sets the twist and spine count for the rig"""
        self.buildMatchInstance.stage5_TwistSpineCount()

    def stage7_buildHiveSkeleton(self):
        api.commands.buildDeform(self.rigInstance)  # build the deform skeleton

    def stage8_transferJointWeights(self, skinJointTransfer):
        """Transfers the skin weights to the Hive skeleton.

        :param skinJointTransfer: True if you'd like to transfer the joint weights to the Hive skeleton.
        :type skinJointTransfer: bool
        """
        # Transfer joint weights to the new skeleton, proxy mesh to the hive proxy mesh
        self.transferJointWeights()
        # Transfer joint weights from the hive proxy mesh to the target meshes if there are any
        if self.skinTargetGeoList and skinJointTransfer:
            self.transferSkinMeshWeights(sourceMesh=self.proxyMeshHive, targetMeshes=self.skinTargetGeoList)

    def stage9_polishRig(self, baseJoint, hideProxySkeleton, hideProxyGeo, hideHiveProxyGeo, offsetColors=True):
        """Polishes the rig if self.polishRig is True, otherwise goes to guides.

        Optionally hides the proxy skeleton and geometry.

        :param baseJoint: The base joint of the skin proxy skeleton
        :type baseJoint: str
        :param hideProxySkeleton: Hides the proxy skeleton if True
        :type hideProxySkeleton: bool
        :param hideProxyGeo: Hides the proxy geometry if True
        :type hideProxyGeo: bool
        :param hideHiveProxyGeo: Hides the hive proxy geometry if True
        :type hideHiveProxyGeo: bool
        :param offsetColors: Offsets the shader colors on the proxy mesh to show has finished
        :type offsetColors: bool
        """
        # Polish the rig
        if self.polishRig:
            self.rigInstance.polish()
        else:
            api.commands.buildGuides(self.rigInstance)  # guides mode

        # Hide the proxy mesh and skeleton --------------------------
        if ":" not in baseJoint:  # if the original joint has no namespace, add it now
            baseJoint = ":".join([self.sourceNamespace, baseJoint])
        if hideProxySkeleton:
            cmds.setAttr("{}.visibility".format(baseJoint), False)
        if hideProxyGeo:
            if self.skinProxyGeo:
                cmds.setAttr("{}.visibility".format(self.skinProxyGeo), False)
        if self.skinTargetGeoList and hideHiveProxyGeo:
            cmds.setAttr("{}.visibility".format(self.proxyMeshHive), False)
        if self.skinTargetGeoList:
            for geo in self.skinTargetGeoList:
                try:
                    cmds.setAttr("{}.visibility".format(geo), True)
                except:  # locked/connected attr
                    pass

        # Auto name skin clusters.
        if self.proxyMeshHive:
            skinnedMeshes = [self.proxyMeshHive] + self.skinTargetGeoList
            bindskin.renameSkinClusters(skinnedMeshes, message=False)
        if self.proxyMeshHive:
            cmds.parent(self.proxyMeshHive, "biped_geo_hrc")  # parent to the rig geo folder
            self._shaderDuplicate(offsetColors)
        if self.skinTargetGeoList:
            for geo in self.skinTargetGeoList:
                cmds.parent(geo, "biped_geo_hrc")
        cmds.select(deselect=True)  # select nothing

    def buildAndSkin(self, baseJoint, skinTransfer=True, buildRig=True, skinJointTransfer=True, hideProxySkeleton=True,
                     hideProxyGeo=True, hideHiveProxyGeo=True):
        """Build and skin the rig and transfer joint weights to the new rig.

        :param baseJoint: The base joint of the skin proxy skeleton
        :type baseJoint: str
        :param skinTransfer: True if the skin weights should be transferred
        :type skinTransfer: bool
        :param buildRig: True if you'd like to build the rig
        :type buildRig: bool
        :param skinJointTransfer: True if you'd like to transfer the joint weights to the Hive skeleton.
        :type skinJointTransfer: bool
        :param hideProxySkeleton: Hides the proxy skeleton if True
        :type hideProxySkeleton: bool
        :param hideProxyGeo: Hides the proxy geometry if True
        :type hideProxyGeo: bool
        :return: The hive rig instance
        :rtype: object
        """
        # TODO: Auto detect skin proxy geo

        # TODO: feet pivots can be joints
        # TODO: Optional Constrain rather than reskin
        # TODO: Support no twist joints
        if not self.stage1_basicChecks(baseJoint):
            return None

        self.stage2_duplicateSkinProxyMesh()  # creates self.proxyMeshHive and skins it

        if not self.stage3_buildRig(baseJoint, buildRig):
            return None

        if not self.stage4_matchGuides():
            return None

        if not self.stage5_FinalAlignment():
            return None

        self.stage6_twistingSpineCount()

        if not self.stage7_buildHiveSkeleton():
            return None

        self.stage8_transferJointWeights(skinJointTransfer)

        self.stage9_polishRig(baseJoint, hideProxySkeleton, hideProxyGeo)
        return self.rigInstance

    def buildAndSkinSel(self, skinTransfer=True, buildRig=True, skinJointTransfer=True, hideProxySkeleton=True,
                        hideProxyGeo=True):
        """Build and skin the rig and transfer joint weights to the new rig.

        Uses the selection as the base joint.

        :param skinTransfer:
        :type skinTransfer:
        :param buildRig: True if you'd like to build the rig
        :type buildRig: bool
        :param skinJointTransfer: True if you'd like to transfer the joint weights to the Hive skeleton.
        :type skinJointTransfer: bool
        :param hideProxySkeleton: Hides the proxy skeleton if True
        :type hideProxySkeleton: bool
        :param hideProxyGeo: Hides the proxy geometry if True
        :type hideProxyGeo: bool
        :return: The hive rig instance object
        :rtype: object
        """
        selJoints = cmds.ls(selection=True, type="joint")
        if not selJoints:
            output.displayWarning("Please select the root joint of the skeleton")
            return
        self.buildAndSkin(selJoints[0], skinTransfer=skinTransfer, buildRig=buildRig,
                          skinJointTransfer=skinJointTransfer, hideProxySkeleton=hideProxySkeleton,
                          hideProxyGeo=hideProxyGeo)
