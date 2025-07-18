"""

from zoo.libs.maya.cmds.skin import skinreplacejoints
skinreplacejoints.replaceJointsMatrixSuffix(boundText="oldJnt", replaceText="newJnt", prefix=False, message=True)


"""
import re

import maya.cmds as cmds

from zoo.libs.utils import output
from zoo.libs.maya.cmds.objutils import namehandling, connections
from zoo.libs.maya.cmds.skin import bindskin

REPLACE_SKIN_ATTRS = ["worldMatrix", "objectColorRGB", "lockInfluenceWeights", "bindPose", "message"]
SKIN_DEST_TYPES = ["skinCluster", "dagPose"]


def replaceSkinMatrixJoint(boundJoint, replaceJoint):
    """Swaps the binding of a joint and replaces the bind to another joint.

    Useful while swapping the skinning from one skeleton to another.

    The skinning is swapped based on the matrix positions, so if the joint is in new locations the mesh may move.

    Bound joint must be verified as existing and being part of a skin cluster.

    :param boundJoint: The joint with the skinning, to be replaced
    :type boundJoint: str
    :param replaceJoint: The new joint that will receive the skinning
    :type replaceJoint: str
    """
    if not cmds.attributeQuery('lockInfluenceWeights', node=boundJoint, exists=True):
        return
    if not cmds.attributeQuery('lockInfluenceWeights', node=replaceJoint, exists=True):
        cmds.addAttr(replaceJoint, longName='lockInfluenceWeights', attributeType='bool')  # New joints need this attr
    for attr in REPLACE_SKIN_ATTRS:  # "worldMatrix", "objectColorRGB" etc
        connections.swapDriverConnectionAttr(boundJoint, replaceJoint, attr, checkDestNodeTypes=SKIN_DEST_TYPES)
        # TODO perhaps does not need to be swapped as per unbindSource parameter


def replaceSkinJoint(boundJoint, replaceJoint, unbindSource=True, skipSkinClusters=()):
    """Swap/replace the binding of a joint and replaces the bind to another joint.

    Uses the lock weights method for doing the swap and is faster than the replaceSkinJointSlow method.

    :param boundJoint: The joint with the skinning, to be replaced
    :type boundJoint: str
    :param replaceJoint: The new joint that will receive the skinning
    :type replaceJoint: str
    :param unbindSource: Unbind the source joint from the skin cluster
    :type unbindSource: bool
    :param skipSkinClusters: A list of skin clusters to skip
    :type skipSkinClusters: list(str)
    """
    skinClusterList = bindskin.getSkinClusterFromJoint(boundJoint)
    originalSelection = cmds.ls(selection=True)

    for sCluster in skinClusterList:
        if sCluster in skipSkinClusters:
            continue
        allJntInfl = cmds.ls(cmds.skinCluster(sCluster, query=True, influence=True))
        cmds.select(allJntInfl)
        for jnt in allJntInfl:  # Lock all weights
            cmds.skinCluster(sCluster, edit=True, influence=jnt, lockWeights=True)
        cmds.skinCluster(sCluster, edit=True, lockWeights=True, weightedInfluence=0, addInfluence=replaceJoint)
        cmds.skinCluster(sCluster, edit=True, influence=replaceJoint, lockWeights=False)
        cmds.skinCluster(sCluster, edit=True, influence=boundJoint, lockWeights=False)
        cmds.skinCluster(sCluster, edit=True, selectInfluenceVerts=boundJoint)
        cmds.skinPercent(sCluster, transformValue=[(boundJoint, 0), (replaceJoint, 1)])  # Transfer the weights
        for jnt in allJntInfl:  # Unlock all weights
            cmds.skinCluster(sCluster, edit=True, influence=jnt, lockWeights=False)
        if unbindSource:
            if not cmds.referenceQuery(boundJoint, isNodeReferenced=True):  # If not referenced
                bindskin.removeInfluence([boundJoint], sCluster)

    cmds.select(originalSelection, replace=True)  # Return to selection.


def replaceSkinJointSlow(boundJoint, replaceJoint, unbindSource=True):
    """Swaps the binding of a joint and replaces the bind to another joint.

    Bound joint must be verified as existing and being part of a skin cluster.

    :param boundJoint: The joint with the skinning, to be replaced
    :type boundJoint: str
    :param replaceJoint: The new joint that will receive the skinning
    :type replaceJoint: str
    :param unbindSource: Unbind the source joint from the skin cluster
    :type unbindSource: bool
    :return: Success if the transfer was successful
    :rtype: bool
    """
    skinClusterList = bindskin.getSkinClusterFromJoint(boundJoint)
    originalSelection = cmds.ls(selection=True)
    for skinCluster in skinClusterList:
        geoList = bindskin.geoFromSkinCluster(skinCluster, transforms=True)
        if not geoList:
            continue
        for geo in geoList:
            bindskin.addJointsToSkinned([replaceJoint], [skinCluster])  # Must be skinned first
            cmds.select("{}.vtx[*]".format(geo), replace=True)  # Select all vertexes from the mesh
            cmds.skinPercent(skinCluster, transformMoveWeights=[boundJoint, replaceJoint])  # TODO slow!!!
        if unbindSource:
            if not cmds.referenceQuery(boundJoint, isNodeReferenced=True):  # If not referenced
                bindskin.removeInfluence([boundJoint], skinCluster)
    cmds.select(originalSelection, replace=True)  # Return to selection.
    return True


def replaceSkinJointList(boundJoints, replaceJoints, moveWithJoints=False, unbindSource=True, skipSkinClusters=(),
                         message=False):
    """Swaps the binding of a list of joints and replaces the bind to another list of joints.

    Bound joints must be verified as existing and being part of a skin cluster.

    Useful while swapping the skinning from one skeleton to another.

    The skinning is swapped based on the matrix positions, so if joints are in new locations the mesh may move.

    :param boundJoints: A list of joints bound to a skin cluster
    :type boundJoints: list(str)
    :param replaceJoints: A list of joints to be switched to connect to the skin cluster
    :type replaceJoints: list(str)
    :param moveWithJoints: If True will move the joints to the new joint positions
    :type moveWithJoints: bool
    :param unbindSource: Unbind the source joints from the skin cluster
    :type unbindSource: bool
    :param skipSkinClusters: A list of skin clusters to skip
    :type skipSkinClusters: list(str)
    :param message: Report the message to the user
    :type message: bool
    """
    for i, boundJnt in enumerate(boundJoints):
        if moveWithJoints:
            replaceSkinMatrixJoint(boundJnt, replaceJoints[i])
        else:
            replaceSkinJoint(boundJnt, replaceJoints[i], unbindSource=unbindSource, skipSkinClusters=skipSkinClusters)
    if message:
        shortNames = namehandling.getShortNameList(replaceJoints)
        output.displayInfo("Success: Skinning transferred.".format(shortNames))


def replaceJointsMatrixSuffix(boundText="oldJnt", replaceText="newJnt", prefix=False, message=True):
    """Swaps the binding of a list of joints and replaces the bind to another list of joints from scene suffix/prefix.

    :param boundText: The suffix/prefix of the existing joints
    :type boundText: str
    :param replaceText: The suffix/prefix of the new joints
    :type replaceText: str
    :param prefix: If True will be the prefix otherwise suffix
    :type prefix: bool
    :param message: Report a message to the user?
    :type message: bool

    :return success: True if the transfer was successful
    :rtype success: bool
    """
    if prefix:
        bndText = str("{}_*".format(boundText))
        rplText = str("{}_*".format(replaceText))
    else:
        bndText = str("*_{}".format(boundText))
        rplText = str("*_{}".format(replaceText))
    boundJoints = sorted(cmds.ls(bndText, type="joint"))
    replaceJoints = sorted(cmds.ls(rplText, type="joint"))

    if not boundJoints or not replaceJoints:  # bail
        insertTxt = "suffix"
        if prefix:
            insertTxt = "prefix"
        if not boundJoints:
            if message:
                output.displayWarning("Skin Transfer Failed: No bind joints found with {}: {}.".format(insertTxt,
                                                                                                       boundText))
            return False
        if not replaceText:
            if message:
                output.displayWarning("Skin Transfer Failed: No replace joints found with {}: {}.".format(insertTxt,
                                                                                                          replaceText))
            return False

    if message:
        for i, jnt in enumerate(boundJoints):
            try:
                output.displayInfo("Skin Transfer: {} >> {}".format(jnt, replaceJoints[i]))
            except:
                pass

    if len(boundJoints) != len(replaceJoints):  # bail
        if message:
            output.displayWarning("Skin Transfer Failed: Uneven joint count in lists, see script editor.")
        return False

    replaceSkinJointList(boundJoints, replaceJoints, message=message)

    if message:
        output.displayInfo("Skin Transfer Succeeded: See script editor for matches.")
    return False


def replaceJointsMatrixSel(message=True):
    """Swaps the binding of the first half of selected joints and replaces them with the binding of the second half.

    :param message: Report a message to the user?
    :type message: bool
    """
    selJnts = cmds.ls(selection=True, type="joint")

    if not selJnts:
        output.displayWarning("No joints were selected")
        return False

    if (len(selJnts) % 2) != 0:  # not even
        output.displayWarning("There is an odd number of joints selected, must be even")
        return False

    boundJoints = selJnts[:len(selJnts) // 2]
    replaceJoints = selJnts[len(selJnts) // 2:]

    if message:
        for i, jnt in enumerate(boundJoints):
            try:
                output.displayInfo("Skin Transfer: {} >> {}".format(jnt, replaceJoints[i]))
            except:
                pass

    replaceSkinJointList(boundJoints, replaceJoints, message=message)


class ReplaceJointsWeights(object):
    """Class for transfer/replace the skin weights multiple joints to another joint list.

    This class is designed to be used by a UI with rename options.

    Naming Options:
        namespace: The obj namespace, eg "characterX". Colon is handled if included.
        prefix: Adds a prefix to the object name eg "prefix\_" for prefix_joint1
        suffix: Adds a suffix to the object name eg "_suffix" for joint1_suffix

    The class can automatically generate the right side names based on the left side names:
        autoLeftToRight: If True will automatically generate the right side names based on the left side names.
        leftIdentifier: The left side identifier
        rightIdentifier: The right side identifier
        LRIsPrefix: The identifier is always at the start of the name.
        LRIsSuffix: The identifier is always at the end of the name.
        LRSeparatorOnBorder: Underscores are on either side of the identifier eg "L" will be "_L" or "L\_"
    """

    def __init__(self,
                 sourceBoundJnts,
                 targetJnts,
                 skipSkinClusters=(),
                 moveWithJoints=False,
                 unbindSource=True,
                 sourceNamespace="",
                 targetNamespace="",
                 sourcePrefix="",
                 targetPrefix="",
                 sourceSuffix="",
                 targetSuffix="",
                 autoLeftToRight=True,
                 sourceLeftIdentifier="_L",
                 sourceRightIdentifier="_R",
                 sourceLRIsPrefix=False,
                 sourceLRIsSuffix=False,
                 sourceLRSeparatorOnBorder=False,
                 targetLeftIdentifier="_L",
                 targetRightIdentifier="_R",
                 targetLRIsPrefix=False,
                 targetLRIsSuffix=False,
                 targetLRSeparatorOnBorder=False
                 ):
        """Initialize variables for the class

        :param sourceBoundJnts: The source list of joints that have skinning.
        :type sourceBoundJnts: list(str)
        :param targetJnts: The target list of joints to transfer the skinning to.
        :type targetJnts: list(str)
        :param skipSkinClusters: A list of joints to skip in the transfer
        :type skipSkinClusters: list(str)
        :param moveWithJoints: If True will move the joints to the new joint positions
        :type moveWithJoints: bool
        :param unbindSource: Unbind the source joints from the skin cluster
        :type unbindSource: bool
        :param sourceNamespace: The source jnt namespace, eg "skeletonReferenceName". Colon is handled if included.
        :type sourceNamespace: str
        :param targetNamespace: The target jnt namespace, eg "skeletonReferenceName". Colon is handled if included.
        :type targetNamespace: str
        :param sourcePrefix: The source prefix eg "characterName_".  Source sometimes have the char as prefix
        :type sourcePrefix: str
        :param targetPrefix: The target prefix eg "characterName_".  Target sometimes have the char as prefix
        :type targetPrefix: str
        :param sourceSuffix: The source prefix eg "characterName_".  Source sometimes have the char as suffix
        :type sourceSuffix: str
        :param targetSuffix: The target prefix eg "characterName_".  Target sometimes have the char as suffix
        :type targetSuffix: str
        :param sourceLeftIdentifier: The source left side identifier
        :type sourceLeftIdentifier: str
        :param sourceRightIdentifier: The source right side identifier
        :type sourceRightIdentifier: str
        :param sourceLRIsPrefix: The identifier is always at the start of the name.
        :type sourceLRIsPrefix: bool
        :param sourceLRIsSuffix: The identifier is always at the end of the name.
        :type sourceLRIsSuffix: bool
        :param sourceLRSeparatorOnBorder: Underscores are on either side of the identifier eg "L" will be "_L" or "L_"
        :type sourceLRSeparatorOnBorder: bool
        :param targetLeftIdentifier: The target left side identifier
        :type targetLeftIdentifier: str
        :param targetRightIdentifier: The target right side identifier
        :type targetRightIdentifier: str
        :param targetLRIsPrefix: The identifier is always at the start of the name.
        :type targetLRIsPrefix: bool
        :param targetLRIsSuffix: The identifier is always at the end of the name.
        :type targetLRIsSuffix: bool
        :param targetLRSeparatorOnBorder: Underscores are on either side of the identifier eg "L" will be "_L" or "L_"
        :type targetLRSeparatorOnBorder: bool
        """
        super(ReplaceJointsWeights, self).__init__()
        self.sourceBoundJnts = sourceBoundJnts
        self.targetJoints = targetJnts
        self.skipSkinClusters = skipSkinClusters
        self.moveWithJoints = moveWithJoints
        self.unbindSource = unbindSource
        self.sourceJntsRenamed = list()
        self.targetJntsRenamed = list()
        self.checkKeyMatches = targetJnts
        self.targetNamespace = targetNamespace
        self.sourceNamespace = sourceNamespace
        self.sourcePrefix = sourcePrefix
        self.targetPrefix = targetPrefix
        self.sourceSuffix = sourceSuffix
        self.targetSuffix = targetSuffix
        self.autoLeftToRight = autoLeftToRight
        self.sourceLeftIdentifier = sourceLeftIdentifier
        self.sourceRightIdentifier = sourceRightIdentifier
        self.sourceLRIsPrefix = sourceLRIsPrefix
        self.sourceLRIsSuffix = sourceLRIsSuffix
        self.sourceLRSeparatorOnBorder = sourceLRSeparatorOnBorder
        self.targetLeftIdentifier = targetLeftIdentifier
        self.targetRightIdentifier = targetRightIdentifier
        self.targetLRIsPrefix = targetLRIsPrefix
        self.targetLRIsSuffix = targetLRIsSuffix
        self.targetLRSeparatorOnBorder = targetLRSeparatorOnBorder

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

    def _rightSideName(self, name, leftId, rightId, LRIsPrefix, LRIsSuffix, LRSeparatorOnBorder):
        """Finds the right side name of an object, with many options. If it can't be built the name will be empty.

        Name can be long with namespaces. "x|x:name"

        :param name: The name of the left side
        :type name: str
        :param leftId: The left identifier eg "L"
        :type leftId: str
        :param rightId: The left identifier eg "R"
        :type rightId: str
        :param LRIsPrefix: The identifier is always at the start of the name.
        :type LRIsPrefix: bool
        :param LRIsSuffix: The identifier is always at the end of the name.
        :type LRIsSuffix: bool
        :param LRSeparatorOnBorder: Underscores are on either side of the identifier eg "L" will be "_L" or "L_"
        :type LRSeparatorOnBorder: bool
        :return: The name of the right side, if not found returns an empty string
        :rtype: str
        """
        return namehandling.rightNameFromLeft(name, leftId, rightId, LRIsPrefix, LRIsSuffix, LRSeparatorOnBorder)

    def _buildObjectLists(self):
        """Returns lists of source bound joints, and target joints.
        """
        self.sourceJntsRenamed = list()
        self.targetJntsRenamed = list()
        if not self.sourceBoundJnts or not self.targetJoints:  # can't build the names, not needed till the transfer
            return self.sourceJntsRenamed, self.targetJntsRenamed

        for i, sourceJnt in enumerate(self.sourceBoundJnts):
            # Add name prefix and namespaces -------------------------------------
            sourceJnt = self._renameObj(sourceJnt,
                                        self.sourceNamespace,
                                        self.sourcePrefix,
                                        self.sourceSuffix)
            targetObj = self._renameObj(self.targetJoints[i],
                                        self.targetNamespace,
                                        self.targetPrefix,
                                        self.targetSuffix)
            self.sourceJntsRenamed.append(sourceJnt)
            self.targetJntsRenamed.append(targetObj)

            # Right side if passes checks --------------
            if not self.autoLeftToRight:
                continue
            if self.targetLeftIdentifier not in targetObj:
                continue

            rightSource = self._rightSideName(sourceJnt,
                                              self.sourceLeftIdentifier,
                                              self.sourceRightIdentifier,
                                              self.sourceLRIsPrefix,
                                              self.sourceLRIsSuffix,
                                              self.sourceLRSeparatorOnBorder)
            rightTarget = self._rightSideName(targetObj,
                                              self.targetLeftIdentifier,
                                              self.targetRightIdentifier,
                                              self.targetLRIsPrefix,
                                              self.targetLRIsSuffix,
                                              self.targetLRSeparatorOnBorder)
            self.sourceJntsRenamed.append(rightSource)
            self.targetJntsRenamed.append(rightTarget)

        return self.sourceJntsRenamed, self.targetJntsRenamed

    def _verifyJoints(self, message=True):
        """Names and verifies the bound joints and replace joints exist and are part of a skin cluster.

        :param message: Report a message to the user?
        :type message: bool

        :return: The verified bound joints, boundJointsVerified and replace joints, replaceJointsVerified
        :rtype: tuple(list(str), list(str))
        """
        boundJointsVerified = list()
        replaceJointsVerified = list()
        self._buildObjectLists()  # Name the joints correctly as per UI settings

        # remove pairs where the bind joint is not skinned or if doesn't exist -------------------------------------
        for i, boundJnt in enumerate(self.sourceJntsRenamed):
            if not cmds.objExists(boundJnt):
                if message:
                    output.displayWarning("The joint replace `{} >> {}` was skipped "
                                          "as source does not exist.".format(boundJnt,
                                                                             self.targetJntsRenamed[i]))
                continue
            if not cmds.objExists(self.targetJntsRenamed[i]):
                if message:
                    output.displayWarning("The joint replace `{} >> {}` was skipped "
                                          "as target does not exist.".format(boundJnt,
                                                                             self.targetJntsRenamed[i]))
                continue
            if not bindskin.getSkinClusterFromJoint(boundJnt):
                if message:
                    output.displayWarning("The joint replace `{} >> {}` was skipped "
                                          "as it is not bound to geometry.".format(boundJnt,
                                                                                   self.targetJntsRenamed[i]))
                continue
            if self.unbindSource:
                if cmds.referenceQuery(boundJnt, isNodeReferenced=True):  # If not referenced
                    if message:
                        output.displayWarning(
                            "The joint `{} >> {}` was skipped as the source joint is referenced"
                            " and cannot be unbound.".format(boundJnt, self.targetJntsRenamed[i]))
                    continue
            boundJointsVerified.append(boundJnt)
            replaceJointsVerified.append(self.targetJntsRenamed[i])
        return boundJointsVerified, replaceJointsVerified

    def replaceJointsWeights(self, message=False):
        """Replaces the joints weights from the source joints to the target joints.

        :param message: Report a message to the user?
        :type message: bool
        """
        boundJointsVerified, replaceJointsVerified = self._verifyJoints(message=message)
        replaceSkinJointList(boundJointsVerified,
                             replaceJointsVerified,
                             moveWithJoints=self.moveWithJoints,
                             unbindSource=self.unbindSource,
                             skipSkinClusters=self.skipSkinClusters,
                             message=message)
