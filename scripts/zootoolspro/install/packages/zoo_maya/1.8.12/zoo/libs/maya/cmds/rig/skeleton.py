""""Module for skeleton discovery and manipulation

Supports name conventions for the following:

- Hive
- Skeleton Builder
- Accurig Character Creator
- HIK and varients
- UE5

example:

from zoo.libs.maya.cmds.rig import skeleton
skeleton.getTwistSpineCount("spine00")

from zoo.libs.maya.cmds.rig import skeleton
print(skeleton.IdentifySkeleton("god_M_godnode_jnt").skeletonFormat())


"""
import re

from maya import cmds

from zoo.libs.utils import output
from zoo.libs.maya.cmds.animation import batchconstraintconstants as bcc


def findListMatch(keyMatch, skeletonPreset):
    """Finds the matching index of a list of strings"""
    for jntDict in skeletonPreset:
        if keyMatch == next(iter(jntDict)):
            conventionStr = jntDict[keyMatch]["node"]
            # replace numbers with * for matching -------------------
            conventionStr = re.sub(r'\d', '?', conventionStr)
            conventionStr = re.sub(r'\*+', '?', conventionStr)
            findList = conventionStr.split("?")
            return list(filter(None, findList))  # remove empty strings
    return ""


def findStringsInOrder(mainString, findList):
    """Find if two strings are found anywhere in another string, must be in order of the two strings

    Searches only the first and last elements in a list.

    ['spine_M_', '', '_jnt']

    matches

    aNamespace:spine_M_01_jnt

    :param mainString: The main string to search in
    :type mainString: str
    :param findList: List of two strings to find in order
    :type findList: str
    :return: True if both strings are found in order, False otherwise
    :rtype: bool
    """
    if len(findList) == 1:
        if findList[0] in mainString:
            return True

    index1 = mainString.find(findList[0])
    if index1 == -1:
        return False

    index2 = mainString.find(findList[-1], index1 + len(findList[0]))
    if index2 == -1:
        return False
    return True


def jointHierarchy(baseJoint):
    allJoints = cmds.listRelatives(baseJoint, allDescendents=True, type="joint")
    if not allJoints:
        return list()
    allJoints.append(baseJoint)  # add the base joint to the list\
    return allJoints


def spineJoints(baseJoint, skeletonPreset=bcc.HIVE_BIPED_STRD_JOINTS_TWSTS):
    """Returns the spine joints from the base joint

    :param baseJoint: The parent joint to search down the chain
    :type baseJoint: str
    :param skeletonPreset: A skeleton preset list of dictionaries see bcc.HIVE_BIPED_STRD_JOINTS_TWSTS
    :type skeletonPreset: list(dict())
    :return: spineJnts
    :rtype: list(str)
    """
    spinejnts = list()

    # get all child joints -----------------------------------
    joints = jointHierarchy(baseJoint)
    if not joints:
        output.displayWarning("No joints found for {}".format(baseJoint))
        return

    spineFindList = findListMatch("spine00_M", skeletonPreset)
    for jnt in joints:
        if findStringsInOrder(jnt, spineFindList):  # "old:armUprTwst01_L" matches ["armUprTwst", "_L"]
            spinejnts.append(jnt)

    return spinejnts


def twistSpineJonts(baseJoint, skeletonPreset=bcc.HIVE_BIPED_STRD_JOINTS_TWSTS):
    """Returns joint lists for the arm twists, leg twists and spine components.

    :param baseJoint: The parent joint to search down the chain
    :type baseJoint: str
    :param skeletonPreset: A skeleton preset list of dictionaries see bcc.HIVE_BIPED_STRD_JOINTS_TWSTS
    :type skeletonPreset: list(dict())
    :return: uprArmTwist, lwrArmTwist, uprLegTwists, lwrLegTwists, spineJnts
    :rtype: tuple(list(str), list(str), list(str), list(str), list(str))
    """
    armUprTwists = list()
    armLwrTwists = list()
    legUprTwists = list()
    legLwrTwists = list()
    spinejnts = list()

    # get all child joints -----------------------------------
    joints = jointHierarchy(baseJoint)
    if not joints:
        output.displayWarning("No joints found for {}".format(baseJoint))
        return

    # Find lists are usually two strings in a list.  Representing two parts of joint name with a number in middle
    armUpprFindList = findListMatch("armUprTwst00_L", skeletonPreset)
    armLwrFindList = findListMatch("armLwrTwst00_L", skeletonPreset)
    legUprFindList = findListMatch("legUprTwst00_L", skeletonPreset)
    legLwrFindList = findListMatch("legLwrTwst00_L", skeletonPreset)
    spineFindList = findListMatch("spine00_M", skeletonPreset)

    for jnt in joints:
        if findStringsInOrder(jnt, armUpprFindList):  # "old:armUprTwst01_L" matches ["armUprTwst", "_L"]
            armUprTwists.append(jnt)
        if findStringsInOrder(jnt, armLwrFindList):
            armLwrTwists.append(jnt)
        if findStringsInOrder(jnt, legUprFindList):
            legUprTwists.append(jnt)
        if findStringsInOrder(jnt, legLwrFindList):
            legLwrTwists.append(jnt)
        if findStringsInOrder(jnt, spineFindList):
            spinejnts.append(jnt)

    return armUprTwists, armLwrTwists, legUprTwists, legLwrTwists, spinejnts


def getTwistSpineCount(baseJoint, skeletonPreset=bcc.HIVE_BIPED_STRD_JOINTS_TWSTS):
    """Returns the twist count for the arm, leg and spine components.

    :param baseJoint: The parent joint to search down the chain
    :type baseJoint: str
    :param skeletonPreset: A skeleton preset list of dictionaries see bcc.HIVE_BIPED_STRD_JOINTS_TWSTS
    :type skeletonPreset: list(dict())
    :return: uprArmTwistCount, lwrArmTwistCount, uprLegTwistCount, lwrLegTwistCount, spineCount
    :rtype: tuple(int, int, int, int, int)
    """
    armUprTwists, armLwrTwists, legUprTwists, legLwrTwists, spinejnts = twistSpineJonts(baseJoint, skeletonPreset)
    return len(armUprTwists), len(armLwrTwists), len(legUprTwists), len(legLwrTwists), len(spinejnts)


class IdentifySkeleton(object):
    """

    TODO handle namespaces

    """

    def __init__(self,
                 parentJoint
                 ):
        """Initialize variables for the class

        :param parentJoint: The source list of dictionaries
        :type parentJoint: dict(str)

        """
        super(IdentifySkeleton, self).__init__()
        self.parentJoint = parentJoint
        self.joints = list()
        self.skeletonType = ""

    def _validateSkeleton(self, jointDict):
        """Checks the joints match the name structure of the skeleton type.

        Checks to find biped joint naming in the jointList self.joints such as

        - spine
        - neck
        - head
        - shoulder_L
        - elbow_L
        - wrist_L
        - lowerLeg
        - foot
        - ball

        :param jointDict: The dictionary of joint names to match eg. bcc.HIVE_BIPED_STRD_JOINTS
        :type jointDict: dict(str)
        :return: True if valid, False otherwise
        :rtype: bool
        """
        spine = False
        neck = False
        head = False
        shoulder = False
        elbow = False
        wrist = False
        thigh = False
        knee = False
        ankle = False
        ball = False

        spineSearchList = findListMatch(bcc.SPINE01, jointDict)
        neckSearchList = findListMatch(bcc.NECK01, jointDict)
        headSearchList = findListMatch(bcc.HEAD, jointDict)
        shoulderSearchList = findListMatch(bcc.SHOULDER_L, jointDict)
        elbowSearchList = findListMatch(bcc.ELBOW_L, jointDict)
        wristSearchList = findListMatch(bcc.WRIST_L, jointDict)
        thighSearchList = findListMatch(bcc.THIGH_L, jointDict)
        kneeSearchList = findListMatch(bcc.KNEE_L, jointDict)
        ankleSearchList = findListMatch(bcc.ANKLE_L, jointDict)
        ballSearchList = findListMatch(bcc.BALL_L, jointDict)

        for jnt in self.joints:
            if findStringsInOrder(jnt, spineSearchList):  # "old:spine_M_00_jnt" matches ["spine_M_", "", "_M"]
                spine = True
            elif findStringsInOrder(jnt, neckSearchList):
                neck = True
            elif findStringsInOrder(jnt, headSearchList):
                head = True
            elif findStringsInOrder(jnt, shoulderSearchList):
                shoulder = True
            elif findStringsInOrder(jnt, elbowSearchList):
                elbow = True
            elif findStringsInOrder(jnt, wristSearchList):
                wrist = True
            elif findStringsInOrder(jnt, thighSearchList):
                thigh = True
            elif findStringsInOrder(jnt, kneeSearchList):
                knee = True
            elif findStringsInOrder(jnt, ankleSearchList):
                ankle = True
            elif findStringsInOrder(jnt, ballSearchList):
                ball = True

        if kneeSearchList == ['L_leg']:  # Skeleton Builder exception
            knee = True
            ankle = True

        if spine and neck and head and shoulder and elbow and wrist and thigh and knee and ankle and ball:
            return True

        return False

    def spineJoints(self):
        """Returns the spine joints from the base joint

        Requires skeletonFormat to be run first.
        """
        spineNameList = list()
        spineJoints = list()

        if not self.skeletonType or not self.jointDict:
            return list()

        for spineId in bcc.SPINE_IDS:
            for dict in self.jointDict:
                if next(iter(dict)) == spineId:
                    spineNameList.append(dict[spineId]["node"])
                    break

        if not spineNameList:
            return list()

        for spineName in spineNameList:
            for jnt in self.joints:
                if spineName in jnt:
                    spineJoints.append(jnt)
                    break
        return spineJoints

    def skeletonFormat(self):
        """Returns the type of skeleton based on the parent joint.

        See bcc.SKELETON_MAPPINGS for the list of skeleton types. Eg:

            "HIVE Biped Strd Jnts"
            "HIVE Biped Light Jnts"
            "Hive BIPED UE Jnts"
            "HIK Jnts"
            "UE5 Jnts"
            "AccuRig Jnts"
            "Skele Bldr Jnts"

        :return: The skeleton format of the current skeleton "HIVE Biped Strd Jnts", "" if unknown
        :rtype: str
        """
        # get all child joints -----------------------------------
        self.joints = jointHierarchy(self.parentJoint)
        if not self.joints:
            output.displayWarning("No joints found for {}".format(self.parentJoint))
            self.skeletonType = ""
            return ""
        for skeleDict in bcc.SKELETON_MAPPINGS:
            skeletonType = next(iter(skeleDict))
            self.jointDict = skeleDict[skeletonType]["nodes"]  # get the first key
            spineFindList = findListMatch(bcc.SPINE00, self.jointDict)
            if not spineFindList:
                continue
            for jnt in self.joints:
                if findStringsInOrder(jnt, spineFindList):  # "old:armUprTwst01_L" matches ["armUprTwst", "_L"]
                    if self._validateSkeleton(self.jointDict):  # always HIK
                        if (skeletonType == bcc.ROKOKO_JNTS_K or
                                skeletonType == bcc.UNITY_JNTS_K or
                                skeletonType == bcc.QUICK_RIG_JNTS_K or
                                skeletonType == bcc.MIXAMO_JNTS_K):
                            return bcc.HIK_JNTS_K
                        if (skeletonType == bcc.HIVE_BIPED_UE5_JNTS_K):  # always UE5
                            return bcc.UE5_JNTS_K
                        return skeletonType
                    break  # can't be this skele type
        self.skeletonType = ""
        return ""

