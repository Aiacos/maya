"""
from zoo.libs.maya.cmds.animation import batchconstraintconstants
batchconstraintconstants.ALL_MAPPINGS

"""


def appendTwistJoints(skeleListDicts, twistList, twistStartAtZero=True, twistCount=9):
    """Appends twist joints to a dictionary of joints.

    (('armUprTwstXX', 'leg_L_uprTwistXX_jnt')) with 9 joints becomes:

        [{'legUprTwst01': {'node': 'leg_L_uprTwist00_jnt', 'constraint': 'orient'}},
        {'legUprTwst02': {'node': 'leg_L_uprTwist01_jnt', 'constraint': 'orient'}},
        {'legUprTwst03': {'node': 'leg_L_uprTwist02_jnt', ' constraint': 'orient'}},
        {'legUprTwst04': {'node': 'leg_L_uprTwist03_jnt', 'constraint': 'orient'}},
        {'legUprTwst05': {'node': 'leg_L_uprTwist04_jnt', 'constraint': 'orient'}},
        {'legUprTwst06': {'node': 'leg_L_uprTwist05_jnt', 'constraint': 'orient'}},
        {'legUprTwst07': {'node': 'leg_L_uprTwist06_jnt', 'constraint': 'orient'}}]

    :param skeleDict: A dictionary of joints to append to.
    :type skeleDict: dict()
    :param twistList: The list that will generate the naming convention for the twist joints.
    :type twistList: tuple(tuple(str, str))
    :param twistCount: The number of twist joints to append.
    :type twistCount: int
    :return: The dictionary of joints with the twist joints appended.
    :rtype:
    """
    for pair in twistList:
        key = pair[0]
        jnt = pair[1]
        for i in range(0, twistCount):  # loop for the amount of twists
            pad = str(i).zfill(2)
            keyName = key.replace('XX', pad)
            if twistStartAtZero:
                pad = str(i).zfill(2)
            else:
                pad = str(i + 1).zfill(2)
            jntName = jnt.replace('XX', pad)
            skeleListDicts.append({keyName: {'node': jntName, 'constraint': 'orient'}})
    return skeleListDicts


def nodeDictToList(nodeDict):
    """Converts a dictionary of nodes HIVE_BIPED_STRD_CTRLS to a list of nodes ["spine_M_cog_anim", etc]

    :param nodeDict:
    :type nodeDict:
    :return:
    :rtype:
    """
    nodeList = list()
    for jntDict in nodeDict:
        key = next(iter(jntDict))
        nodeList.append(jntDict[key]["node"])
    return nodeList


# Rig Type Keys -------------------------------------------------------
HIVE_BIPED_K = "Hive Biped Standard"
HIVE_BIPED_LIGHT_K = "Hive Biped Lightweight"
HIVE_BIPED_UE_K = "Hive Biped UE"
SKELE_BUILDER_K = "Skele Blder Biped"

# Skeleton Type Keys ---------------------------------------------------
HIVE_BIPED_JNTS_K = "HIVE Biped Strd Jnts"
HIVE_BIPED_LIGHT_JNTS_K = "HIVE Biped Light Jnts"
HIVE_BIPED_UE5_JNTS_K = "Hive BIPED UE Jnts"
HIK_JNTS_K = "Human IK Jnts"
UNITY_JNTS_K = "Unity Jnts"
QUICK_RIG_JNTS_K = "Quick Rig Jnts"
MIXAMO_JNTS_K = "Mixamo Jnts"
ROKOKO_JNTS_K = "Rokoko Jnts"
ROKOKO_VAR_JNTS_K = "Rokoko Var1 Jnts"
UE5_JNTS_K = "UE5 Jnts"
ACCU_RIG_JNTS_K = "AccuRig Jnts"
SKELE_BUILDER_JNTS_K = "Skele Bldr Jnts"

HIVE_RIG_JOINT_KEYS = {HIVE_BIPED_K: HIVE_BIPED_JNTS_K,
                       HIVE_BIPED_LIGHT_K: HIVE_BIPED_LIGHT_JNTS_K,
                       HIVE_BIPED_UE_K: HIVE_BIPED_UE5_JNTS_K}


# Keys Body Parts -------------------------------------------------------
ROOT = "root"
SHOULDER_L = "shoulder_L"
ELBOW_L = "elbow_L"
WRIST_L = "wrist_L"
THIGH_L = "thigh_L"
KNEE_L = "knee_L"
ANKLE_L = "ankle_L"
BALL_L = "ball_L"
TOE_L = "toe_L"
CLAVICLE_L = "clavicle_L"
NECK01 = "neck01_M"
NECK02 = "neck02_M"
HEAD = "head_M"
HIP_KEY_M = "hip_M"  # Spine IK base
CHEST_KEY_M = "chest_M"  # Spine IK top
SPINE00 = "spine00_M"
SPINE01 = "spine01_M"
SPINE02 = "spine02_M"
SPINE03 = "spine03_M"
SPINE04 = "spine04_M"
SPINE05 = "spine05_M"
SPINE06 = "spine06_M"
SPINE07 = "spine07_M"
SPINE08 = "spine08_M"
SPINE09 = "spine09_M"
SPINE10 = "spine10_M"
THUMB01_L = "thumb01_L"
THUMB02_L = "thumb02_L"
THUMB03_L = "thumb03_L"
INDEXMETACARPAL_L = "indexMetacarpal_L"
INDEX01_L = "index01_L"
INDEX02_L = "index02_L"
INDEX03_L = "index03_L"
MIDDLEMETACARPAL_L = "middleMetacarpal_L"
MIDDLE01_L = "middle01_L"
MIDDLE02_L = "middle02_L"
MIDDLE03_L = "middle03_L"
RINGMETACARPAL_L = "ringMetacarpal_L"
RING01_L = "ring01_L"
RING02_L = "ring02_L"
RING03_L = "ring03_L"
PINKYMETACARPAL_L = "pinkyMetacarpal_L"
PINKY01_L = "pinky01_L"
PINKY02_L = "pinky02_L"
PINKY03_L = "pinky03_L"
ARMUPRTWST00_L = "armUprTwst00_L"
ARMLWRTWST00_L = "armLwrTwst00_L"
LEGUPRTWST00_L = "legUprTwst00_L"
LEGLWRTWST00_L = "legLwrTwst00_L"

SPINE_IDS = [SPINE00, SPINE01, SPINE02, SPINE03, SPINE04, SPINE05, SPINE06, SPINE07, SPINE08, SPINE09, SPINE10]

# Rig Constants -------------------------------------------------
HIVE_BIPED_STRD_OPTIONS = {"autoRightSide": True,
                           "leftIdentifier": "_L",
                           "rightIdentifier": "_R",
                           "maintainOffset": True,
                           "leftRightUnderscore": False,
                           "leftRightPrefix": False,
                           "leftRightSuffix": False}

HIVE_BIPED_STRD_CTRLS = [{ROOT: {'node': 'spine_M_cog_anim', 'constraint': 'parent'}},
                         {SHOULDER_L: {'node': 'arm_L_shldr_fk_anim', 'constraint': 'orient'}},
                         {ELBOW_L: {'node': 'arm_L_elbow_fk_anim', 'constraint': 'orient'}},
                         {WRIST_L: {'node': 'arm_L_wrist_fk_anim', 'constraint': 'orient'}},
                         {THIGH_L: {'node': 'leg_L_upr_fk_anim', 'constraint': 'orient'}},
                         {KNEE_L: {'node': 'leg_L_knee_fk_anim', 'constraint': 'orient'}},
                         {ANKLE_L: {'node': 'leg_L_foot_fk_anim', 'constraint': 'orient'}},
                         {BALL_L: {'node': 'leg_L_ball_fk_anim', 'constraint': 'orient'}},
                         {CLAVICLE_L: {'node': 'clavicle_L_00_anim', 'constraint': 'orient'}},
                         {NECK01: {'node': 'head_M_neck_anim', 'constraint': 'orient'}},
                         {NECK02: {'node': '', 'constraint': 'orient'}},
                         {HEAD: {'node': 'head_M_head_anim', 'constraint': 'orient'}},
                         {SPINE00: {'node': 'spine_M_ctrl00_anim', 'constraint': 'parent'}},
                         {SPINE01: {'node': 'spine_M_ctrl01_anim', 'constraint': 'parent'}},
                         {SPINE02: {'node': 'spine_M_ctrl02_anim', 'constraint': 'parent'}},
                         {SPINE03: {'node': 'spine_M_ctrl03_anim', 'constraint': 'parent'}},
                         {SPINE04: {'node': 'spine_M_ctrl04_anim', 'constraint': 'parent'}},
                         {SPINE05: {'node': 'spine_M_ctrl05_anim', 'constraint': 'parent'}},
                         {SPINE06: {'node': 'spine_M_ctrl06_anim', 'constraint': 'parent'}},
                         {SPINE07: {'node': 'spine_M_ctrl07_anim', 'constraint': 'parent'}},
                         {SPINE08: {'node': 'spine_M_ctrl08_anim', 'constraint': 'parent'}},
                         {SPINE09: {'node': 'spine_M_ctrl09_anim', 'constraint': 'parent'}},
                         {SPINE10: {'node': 'spine_M_ctrl10_anim', 'constraint': 'parent'}},
                         {THUMB01_L: {'node': 'finger_thumb_L_00_anim', 'constraint': 'orient'}},
                         {THUMB02_L: {'node': 'finger_thumb_L_01_anim', 'constraint': 'orient'}},
                         {THUMB03_L: {'node': 'finger_thumb_L_02_anim', 'constraint': 'orient'}},
                         {INDEXMETACARPAL_L: {'node': 'finger_pointer_L_00_anim', 'constraint': 'orient'}},
                         {INDEX01_L: {'node': 'finger_pointer_L_01_anim', 'constraint': 'orient'}},
                         {INDEX02_L: {'node': 'finger_pointer_L_02_anim', 'constraint': 'orient'}},
                         {INDEX03_L: {'node': 'finger_pointer_L_03_anim', 'constraint': 'orient'}},
                         {MIDDLEMETACARPAL_L: {'node': 'finger_middle_L_00_anim', 'constraint': 'orient'}},
                         {MIDDLE01_L: {'node': 'finger_middle_L_01_anim', 'constraint': 'orient'}},
                         {MIDDLE02_L: {'node': 'finger_middle_L_02_anim', 'constraint': 'orient'}},
                         {MIDDLE03_L: {'node': 'finger_middle_L_03_anim', 'constraint': 'orient'}},
                         {RINGMETACARPAL_L: {'node': 'finger_ring_L_00_anim', 'constraint': 'orient'}},
                         {RING01_L: {'node': 'finger_ring_L_01_anim', 'constraint': 'orient'}},
                         {RING02_L: {'node': 'finger_ring_L_02_anim', 'constraint': 'orient'}},
                         {RING03_L: {'node': 'finger_ring_L_03_anim', 'constraint': 'orient'}},
                         {PINKYMETACARPAL_L: {'node': 'finger_pinky_L_00_anim', 'constraint': 'orient'}},
                         {PINKY01_L: {'node': 'finger_pinky_L_01_anim', 'constraint': 'orient'}},
                         {PINKY02_L: {'node': 'finger_pinky_L_02_anim', 'constraint': 'orient'}},
                         {PINKY03_L: {'node': 'finger_pinky_L_03_anim', 'constraint': 'orient'}}
                         ]

HIVE_BIPED_LIGHT_CTRLS = list(HIVE_BIPED_STRD_CTRLS)  # Use STRD ctrls just change spine and root
HIVE_BIPED_LIGHT_CTRLS[0] = {ROOT: {'node': 'spine_M_cog_anim', 'constraint': 'parent'}}
HIVE_BIPED_LIGHT_CTRLS[12] = {SPINE00: {'node': 'spine_M_01_anim', 'constraint': 'orient'}}
HIVE_BIPED_LIGHT_CTRLS[13] = {SPINE01: {'node': '', 'constraint': 'orient'}}
HIVE_BIPED_LIGHT_CTRLS[14] = {SPINE02: {'node': 'spine_M_02_anim', 'constraint': 'orient'}}

HIVE_BIPED_UE_OPTIONS = {"autoRightSide": True,
                         "leftIdentifier": "_l_",
                         "rightIdentifier": "_r_",
                         "maintainOffset": True,
                         "leftRightUnderscore": False,
                         "leftRightPrefix": False,
                         "leftRightSuffix": False}

HIVE_BIPED_UE_CTRLS = [{ROOT: {'node': 'spine_m_hipsSwing_anim', 'constraint': 'parent'}},
                       {SHOULDER_L: {'node': 'arm_l_upperarm_fk_anim', 'constraint': 'orient'}},
                       {ELBOW_L: {'node': 'arm_l_lowerarm_fk_anim', 'constraint': 'orient'}},
                       {WRIST_L: {'node': 'arm_l_hand_fk_anim', 'constraint': 'orient'}},
                       {THIGH_L: {'node': 'leg_l_thigh_fk_anim', 'constraint': 'orient'}},
                       {KNEE_L: {'node': 'leg_l_calf_fk_anim', 'constraint': 'orient'}},
                       {ANKLE_L: {'node': 'leg_l_foot_fk_anim', 'constraint': 'orient'}},
                       {BALL_L: {'node': 'leg_l_ball_fk_anim', 'constraint': 'orient'}},
                       {CLAVICLE_L: {'node': 'clavicle_l_00_anim', 'constraint': 'orient'}},
                       {NECK01: {'node': 'head_m_neck_01_anim', 'constraint': 'orient'}},
                       {NECK02: {'node': '', 'constraint': 'orient'}},
                       {HEAD: {'node': 'head_m_head_anim', 'constraint': 'orient'}},
                       {SPINE00: {'node': 'spine_m_03_anim', 'constraint': 'parent'}},
                       {SPINE01: {'node': 'spine_m_04_anim', 'constraint': 'parent'}},
                       {SPINE02: {'node': 'spine_m_05_anim', 'constraint': 'parent'}},
                       {SPINE03: {'node': '', 'constraint': 'parent'}},
                       {SPINE04: {'node': '', 'constraint': 'parent'}},
                       {SPINE05: {'node': '', 'constraint': 'parent'}},
                       {SPINE06: {'node': '', 'constraint': 'parent'}},
                       {SPINE07: {'node': '', 'constraint': 'parent'}},
                       {SPINE08: {'node': '', 'constraint': 'parent'}},
                       {SPINE09: {'node': '', 'constraint': 'parent'}},
                       {SPINE10: {'node': '', 'constraint': 'parent'}},
                       {THUMB01_L: {'node': 'thumb_l_metacarpal_anim', 'constraint': 'orient'}},
                       {THUMB02_L: {'node': 'thumb_l_01_anim', 'constraint': 'orient'}},
                       {THUMB03_L: {'node': 'thumb_l_02_anim', 'constraint': 'orient'}},
                       {INDEXMETACARPAL_L: {'node': 'index_l_metacarpal_anim', 'constraint': 'orient'}},
                       {INDEX01_L: {'node': 'index_l_01_anim', 'constraint': 'orient'}},
                       {INDEX02_L: {'node': 'index_l_02_anim', 'constraint': 'orient'}},
                       {INDEX03_L: {'node': 'index_l_03_anim', 'constraint': 'orient'}},
                       {MIDDLEMETACARPAL_L: {'node': 'middle_l_metacarpal_anim', 'constraint': 'orient'}},
                       {MIDDLE01_L: {'node': 'middle_l_01_anim', 'constraint': 'orient'}},
                       {MIDDLE02_L: {'node': 'middle_l_02_anim', 'constraint': 'orient'}},
                       {MIDDLE03_L: {'node': 'middle_l_03_anim', 'constraint': 'orient'}},
                       {RINGMETACARPAL_L: {'node': 'ring_l_metacarpal_anim', 'constraint': 'orient'}},
                       {RING01_L: {'node': 'ring_l_01_anim', 'constraint': 'orient'}},
                       {RING02_L: {'node': 'ring_l_02_anim', 'constraint': 'orient'}},
                       {RING03_L: {'node': 'ring_l_03_anim', 'constraint': 'orient'}},
                       {PINKYMETACARPAL_L: {'node': 'pinky_l_metacarpal_anim', 'constraint': 'orient'}},
                       {PINKY01_L: {'node': 'pinky_l_01_anim', 'constraint': 'orient'}},
                       {PINKY02_L: {'node': 'pinky_l_02_anim', 'constraint': 'orient'}},
                       {PINKY03_L: {'node': 'pinky_l_03_anim', 'constraint': 'orient'}}
                       ]

SKELE_BUILDER_OPTIONS = {"autoRightSide": True,
                         "leftIdentifier": "L",
                         "rightIdentifier": "R",
                         "maintainOffset": True,
                         "leftRightUnderscore": True,
                         "leftRightPrefix": False,
                         "leftRightSuffix": False}

SKELE_BUILDER_CTRLS = [{ROOT: {'node': 'rootControl', 'constraint': 'parent'}},
                       {SHOULDER_L: {'node': 'fk_bicepControl_L', 'constraint': 'orient'}},
                       {ELBOW_L: {'node': 'fk_elbowControl_L', 'constraint': 'orient'}},
                       {WRIST_L: {'node': 'fk_wristControl_L', 'constraint': 'orient'}},
                       {THIGH_L: {'node': 'fk_thighControl_L', 'constraint': 'orient'}},
                       {KNEE_L: {'node': 'fk_kneeControl_L', 'constraint': 'orient'}},
                       {ANKLE_L: {'node': 'fk_ankleControl_L', 'constraint': 'orient'}},
                       {BALL_L: {'node': '', 'constraint': 'orient'}},
                       {CLAVICLE_L: {'node': 'clavicleControl_L', 'constraint': 'orient'}},
                       {NECK01: {'node': 'neckControl', 'constraint': 'orient'}},
                       {NECK02: {'node': '', 'constraint': 'orient'}},
                       {HEAD: {'node': 'headControl', 'constraint': 'orient'}},
                       {SPINE00: {'node': 'spine_0_fkControl', 'constraint': 'parent'}},
                       {SPINE01: {'node': 'spine_1_fkControl', 'constraint': 'parent'}},
                       {SPINE02: {'node': 'spine_3_fkControl', 'constraint': 'parent'}},
                       {SPINE03: {'node': '', 'constraint': 'parent'}},
                       {SPINE04: {'node': '', 'constraint': 'parent'}},
                       {SPINE05: {'node': '', 'constraint': 'parent'}},
                       {SPINE06: {'node': '', 'constraint': 'parent'}},
                       {SPINE07: {'node': '', 'constraint': 'parent'}},
                       {SPINE08: {'node': '', 'constraint': 'parent'}},
                       {SPINE09: {'node': '', 'constraint': 'parent'}},
                       {SPINE10: {'node': '', 'constraint': 'parent'}},
                       {THUMB01_L: {'node': 'ThumbControl_0_L', 'constraint': 'orient'}},
                       {THUMB02_L: {'node': 'ThumbControl_1_L', 'constraint': 'orient'}},
                       {THUMB03_L: {'node': 'ThumbControl_2_L', 'constraint': 'orient'}},
                       {INDEXMETACARPAL_L: {'node': 'IndexControl_0_L', 'constraint': 'orient'}},
                       {INDEX01_L: {'node': 'IndexControl_1_L', 'constraint': 'orient'}},
                       {INDEX02_L: {'node': 'IndexControl_2_L', 'constraint': 'orient'}},
                       {INDEX03_L: {'node': 'IndexControl_3_L', 'constraint': 'orient'}},
                       {MIDDLEMETACARPAL_L: {'node': 'MidControl_0_L', 'constraint': 'orient'}},
                       {MIDDLE01_L: {'node': 'MidControl_1_L', 'constraint': 'orient'}},
                       {MIDDLE02_L: {'node': 'MidControl_2_L', 'constraint': 'orient'}},
                       {MIDDLE03_L: {'node': 'MidControl_3_L', 'constraint': 'orient'}},
                       {RINGMETACARPAL_L: {'node': 'RingControl_0_L', 'constraint': 'orient'}},
                       {RING01_L: {'node': 'RingControl_1_L', 'constraint': 'orient'}},
                       {RING02_L: {'node': 'RingControl_2_L', 'constraint': 'orient'}},
                       {RING03_L: {'node': 'RingControl_3_L', 'constraint': 'orient'}},
                       {PINKYMETACARPAL_L: {'node': 'PinkyControl_0_L', 'constraint': 'orient'}},
                       {PINKY01_L: {'node': 'PinkyControl_1_L', 'constraint': 'orient'}},
                       {PINKY02_L: {'node': 'PinkyControl_2_L', 'constraint': 'orient'}},
                       {PINKY03_L: {'node': 'PinkyControl_3_L', 'constraint': 'orient'}}
                       ]

SKELE_BUILDER_JOINTS = [{ROOT: {'node': 'root', 'constraint': 'parent'}},
                        {SHOULDER_L: {'node': 'L_bicep', 'constraint': 'orient'}},
                        {ELBOW_L: {'node': 'L_elbow', 'constraint': 'orient'}},
                        {WRIST_L: {'node': 'L_wrist', 'constraint': 'orient'}},
                        {THIGH_L: {'node': 'L_leg01', 'constraint': 'orient'}},
                        {KNEE_L: {'node': 'L_leg02', 'constraint': 'orient'}},
                        {ANKLE_L: {'node': 'L_leg03', 'constraint': 'orient'}},
                        {BALL_L: {'node': 'L_toeBase', 'constraint': 'orient'}},
                        {CLAVICLE_L: {'node': 'L_clavicle', 'constraint': 'orient'}},
                        {NECK01: {'node': 'neck1', 'constraint': 'orient'}},
                        {NECK02: {'node': '', 'constraint': 'orient'}},
                        {HEAD: {'node': 'head', 'constraint': 'orient'}},
                        {SPINE00: {'node': 'spine2', 'constraint': 'parent'}},
                        {SPINE01: {'node': 'spine3', 'constraint': 'parent'}},
                        {SPINE02: {'node': 'spine5', 'constraint': 'parent'}},
                        {SPINE03: {'node': '', 'constraint': 'parent'}},
                        {SPINE04: {'node': '', 'constraint': 'parent'}},
                        {SPINE05: {'node': '', 'constraint': 'parent'}},
                        {SPINE06: {'node': '', 'constraint': 'parent'}},
                        {SPINE07: {'node': '', 'constraint': 'parent'}},
                        {SPINE08: {'node': '', 'constraint': 'parent'}},
                        {SPINE09: {'node': '', 'constraint': 'parent'}},
                        {SPINE10: {'node': '', 'constraint': 'parent'}},
                        {THUMB01_L: {'node': 'Thumb_0_L', 'constraint': 'orient'}},
                        {THUMB02_L: {'node': 'Thumb_1_L', 'constraint': 'orient'}},
                        {THUMB03_L: {'node': 'Thumb_2_L', 'constraint': 'orient'}},
                        {INDEXMETACARPAL_L: {'node': 'Index_0_L', 'constraint': 'orient'}},
                        {INDEX01_L: {'node': 'Index_1_L', 'constraint': 'orient'}},
                        {INDEX02_L: {'node': 'Index_2_L', 'constraint': 'orient'}},
                        {INDEX03_L: {'node': 'Index_3_L', 'constraint': 'orient'}},
                        {MIDDLEMETACARPAL_L: {'node': 'Mid_0_L', 'constraint': 'orient'}},
                        {MIDDLE01_L: {'node': 'Mid_1_L', 'constraint': 'orient'}},
                        {MIDDLE02_L: {'node': 'Mid_2_L', 'constraint': 'orient'}},
                        {MIDDLE03_L: {'node': 'Mid_3_L', 'constraint': 'orient'}},
                        {RINGMETACARPAL_L: {'node': 'Ring_0_L', 'constraint': 'orient'}},
                        {RING01_L: {'node': 'Ring_1_L', 'constraint': 'orient'}},
                        {RING02_L: {'node': 'Ring_2_L', 'constraint': 'orient'}},
                        {RING03_L: {'node': 'Ring_3_L', 'constraint': 'orient'}},
                        {PINKYMETACARPAL_L: {'node': 'Pinky_0_L', 'constraint': 'orient'}},
                        {PINKY01_L: {'node': 'Pinky_1_L', 'constraint': 'orient'}},
                        {PINKY02_L: {'node': 'Pinky_2_L', 'constraint': 'orient'}},
                        {PINKY03_L: {'node': 'Pinky_3_L', 'constraint': 'orient'}}
                        ]

HIK_OPTIONS = {"autoRightSide": True,
               "leftIdentifier": "Left",
               "rightIdentifier": "Right",
               "maintainOffset": True,
               "leftRightUnderscore": False,
               "leftRightPrefix": False,
               "leftRightSuffix": False}

HIK_JOINTS = [{ROOT: {'node': 'Hips', 'constraint': 'parent'}},
              {SHOULDER_L: {'node': 'LeftArm', 'constraint': 'orient'}},
              {ELBOW_L: {'node': 'LeftForeArm', 'constraint': 'orient'}},
              {WRIST_L: {'node': 'LeftHand', 'constraint': 'orient'}},
              {THIGH_L: {'node': 'LeftUpLeg', 'constraint': 'orient'}},
              {KNEE_L: {'node': 'LeftLeg', 'constraint': 'orient'}},
              {ANKLE_L: {'node': 'LeftFoot', 'constraint': 'orient'}},
              {BALL_L: {'node': 'LeftToeBase', 'constraint': 'orient'}},
              {CLAVICLE_L: {'node': 'LeftShoulder', 'constraint': 'orient'}},
              {NECK01: {'node': 'Neck', 'constraint': 'orient'}},
              {NECK02: {'node': '', 'constraint': 'orient'}},
              {HEAD: {'node': 'Head', 'constraint': 'orient'}},
              {SPINE00: {'node': 'Hips', 'constraint': 'orient'}},
              {SPINE01: {'node': 'Spine', 'constraint': 'orient'}},
              {SPINE02: {'node': 'Spine2', 'constraint': 'orient'}},
              {SPINE03: {'node': '', 'constraint': 'orient'}},
              {SPINE04: {'node': '', 'constraint': 'orient'}},
              {SPINE05: {'node': '', 'constraint': 'orient'}},
              {SPINE06: {'node': '', 'constraint': 'orient'}},
              {SPINE07: {'node': '', 'constraint': 'orient'}},
              {SPINE08: {'node': '', 'constraint': 'orient'}},
              {SPINE09: {'node': '', 'constraint': 'orient'}},
              {SPINE10: {'node': '', 'constraint': 'orient'}},
              {THUMB01_L: {'node': 'LeftHandThumb1', 'constraint': 'orient'}},
              {THUMB02_L: {'node': 'LeftHandThumb2', 'constraint': 'orient'}},
              {THUMB03_L: {'node': 'LeftHandThumb3', 'constraint': 'orient'}},
              {INDEXMETACARPAL_L: {'node': '', 'constraint': 'orient'}},
              {INDEX01_L: {'node': 'LeftHandIndex1', 'constraint': 'orient'}},
              {INDEX02_L: {'node': 'LeftHandIndex2', 'constraint': 'orient'}},
              {INDEX03_L: {'node': 'LeftHandIndex3', 'constraint': 'orient'}},
              {MIDDLEMETACARPAL_L: {'node': '', 'constraint': 'orient'}},
              {MIDDLE01_L: {'node': 'LeftHandMiddle1', 'constraint': 'orient'}},
              {MIDDLE02_L: {'node': 'LeftHandMiddle2', 'constraint': 'orient'}},
              {MIDDLE03_L: {'node': 'LeftHandMiddle3', 'constraint': 'orient'}},
              {RINGMETACARPAL_L: {'node': '', 'constraint': 'orient'}},
              {RING01_L: {'node': 'LeftHandRing1', 'constraint': 'orient'}},
              {RING02_L: {'node': 'LeftHandRing2', 'constraint': 'orient'}},
              {RING03_L: {'node': 'LeftHandRing3', 'constraint': 'orient'}},
              {PINKYMETACARPAL_L: {'node': '', 'constraint': 'orient'}},
              {PINKY01_L: {'node': 'LeftHandPinky1', 'constraint': 'orient'}},
              {PINKY02_L: {'node': 'LeftHandPinky2', 'constraint': 'orient'}},
              {PINKY03_L: {'node': 'LeftHandPinky3', 'constraint': 'orient'}}
              ]

ROKOKO_VAR1_JOINTS = list(HIK_JOINTS)
ROKOKO_VAR1_JOINTS[4] = {THIGH_L: {'node': 'LeftThigh', 'constraint': 'parent'}}
ROKOKO_VAR1_JOINTS[5] = {KNEE_L: {'node': 'LeftShin', 'constraint': 'orient'}}
ROKOKO_VAR1_JOINTS[6] = {ANKLE_L: {'node': 'LeftFoot', 'constraint': 'orient'}}
ROKOKO_VAR1_JOINTS[7] = {BALL_L: {'node': 'LeftToe', 'constraint': 'orient'}}
# TODO add the finger joint names see matchconstants.py

ACCU_RIG_OPTIONS = {"autoRightSide": True,
                    "leftIdentifier": "_L",
                    "rightIdentifier": "_R",
                    "maintainOffset": True,
                    "leftRightUnderscore": False,
                    "leftRightPrefix": False,
                    "leftRightSuffix": False}

ACCU_RIG_JOINTS = [{ROOT: {'node': 'CC_Base_Hip', 'constraint': 'parent'}},
                   {SHOULDER_L: {'node': 'CC_Base_L_Upperarm', 'constraint': 'orient'}},
                   {ELBOW_L: {'node': 'CC_Base_L_Forearm', 'constraint': 'orient'}},
                   {WRIST_L: {'node': 'CC_Base_L_Hand', 'constraint': 'orient'}},
                   {THIGH_L: {'node': 'CC_Base_L_Thigh', 'constraint': 'orient'}},
                   {KNEE_L: {'node': 'CC_Base_L_Calf', 'constraint': 'orient'}},
                   {ANKLE_L: {'node': 'CC_Base_L_Foot', 'constraint': 'orient'}},
                   {BALL_L: {'node': 'CC_Base_L_ToeBase', 'constraint': 'orient'}},
                   {CLAVICLE_L: {'node': 'CC_Base_L_Clavicle', 'constraint': 'orient'}},
                   {NECK01: {'node': 'CC_Base_NeckTwist01', 'constraint': 'orient'}},
                   {NECK02: {'node': 'CC_Base_NeckTwist02', 'constraint': 'orient'}},
                   {HEAD: {'node': 'CC_Base_Head', 'constraint': 'orient'}},
                   {SPINE00: {'node': 'CC_Base_Waist', 'constraint': 'orient'}},
                   {SPINE01: {'node': 'CC_Base_Spine01', 'constraint': 'orient'}},
                   {SPINE02: {'node': 'CC_Base_Spine02', 'constraint': 'orient'}},
                   {SPINE03: {'node': '', 'constraint': 'orient'}},
                   {SPINE04: {'node': '', 'constraint': 'orient'}},
                   {SPINE05: {'node': '', 'constraint': 'orient'}},
                   {SPINE06: {'node': '', 'constraint': 'orient'}},
                   {SPINE07: {'node': '', 'constraint': 'orient'}},
                   {SPINE08: {'node': '', 'constraint': 'orient'}},
                   {SPINE09: {'node': '', 'constraint': 'orient'}},
                   {SPINE10: {'node': '', 'constraint': 'orient'}},
                   {THUMB01_L: {'node': 'CC_Base_L_Thumb1', 'constraint': 'orient'}},
                   {THUMB02_L: {'node': 'CC_Base_L_Thumb2', 'constraint': 'orient'}},
                   {THUMB03_L: {'node': 'CC_Base_L_Thumb3', 'constraint': 'orient'}},
                   {INDEXMETACARPAL_L: {'node': '', 'constraint': 'orient'}},
                   {INDEX01_L: {'node': 'CC_Base_L_Index1', 'constraint': 'orient'}},
                   {INDEX02_L: {'node': 'CC_Base_L_Index2', 'constraint': 'orient'}},
                   {INDEX03_L: {'node': 'CC_Base_L_Index3', 'constraint': 'orient'}},
                   {MIDDLEMETACARPAL_L: {'node': '', 'constraint': 'orient'}},
                   {MIDDLE01_L: {'node': 'CC_Base_L_Mid1', 'constraint': 'orient'}},
                   {MIDDLE02_L: {'node': 'CC_Base_L_Mid2', 'constraint': 'orient'}},
                   {MIDDLE03_L: {'node': 'CC_Base_L_Mid3', 'constraint': 'orient'}},
                   {RINGMETACARPAL_L: {'node': '', 'constraint': 'orient'}},
                   {RING01_L: {'node': 'CC_Base_L_Ring1', 'constraint': 'orient'}},
                   {RING02_L: {'node': 'CC_Base_L_Ring2', 'constraint': 'orient'}},
                   {RING03_L: {'node': 'CC_Base_L_Ring3', 'constraint': 'orient'}},
                   {PINKYMETACARPAL_L: {'node': '', 'constraint': 'orient'}},
                   {PINKY01_L: {'node': 'CC_Base_L_Pinky1', 'constraint': 'orient'}},
                   {PINKY02_L: {'node': 'CC_Base_L_Pinky2', 'constraint': 'orient'}},
                   {PINKY03_L: {'node': 'CC_Base_L_Pinky3', 'constraint': 'orient'}}
                   ]

TWSTS = (('armUprTwstXX_L', 'CC_Base_L_UpperarmTwistXX'), ('armLwrTwstXX_L', 'CC_Base_L_ForearmTwistXX'),
         ('legUprTwstXX_L', 'CC_Base_L_ThighTwistXX'), ('legLwrTwstXX_L', 'CC_Base_L_CalfTwistXX'))
ACCU_RIG_TWST_JOINTS = list(ACCU_RIG_JOINTS)
ACCU_RIG_TWST_JOINTS = appendTwistJoints(ACCU_RIG_TWST_JOINTS, TWSTS, twistStartAtZero=False, twistCount=9)

UE5_JOINTS_OPTIONS = {"autoRightSide": True,
                      "leftIdentifier": "_l",
                      "rightIdentifier": "_r",
                      "maintainOffset": True,
                      "leftRightUnderscore": False,
                      "leftRightPrefix": False,
                      "leftRightSuffix": False}

UE5_JOINTS = [{ROOT: {'node': 'pelvis', 'constraint': 'parent'}},
              {SHOULDER_L: {'node': 'upperarm_l', 'constraint': 'orient'}},
              {ELBOW_L: {'node': 'lowerarm_l', 'constraint': 'orient'}},
              {WRIST_L: {'node': 'hand_l', 'constraint': 'orient'}},
              {THIGH_L: {'node': 'thigh_l', 'constraint': 'orient'}},
              {KNEE_L: {'node': 'calf_l', 'constraint': 'orient'}},
              {ANKLE_L: {'node': 'foot_l', 'constraint': 'orient'}},
              {BALL_L: {'node': 'ball_l', 'constraint': 'orient'}},
              {CLAVICLE_L: {'node': 'clavicle_l', 'constraint': 'orient'}},
              {NECK01: {'node': 'neck_01', 'constraint': 'orient'}},
              {NECK02: {'node': 'neck_02', 'constraint': 'orient'}},
              {HEAD: {'node': 'head', 'constraint': 'orient'}},
              {SPINE00: {'node': 'spine_03', 'constraint': 'orient'}},
              {SPINE01: {'node': 'spine_04', 'constraint': 'orient'}},
              {SPINE02: {'node': 'spine_05', 'constraint': 'orient'}},
              {SPINE03: {'node': '', 'constraint': 'orient'}},
              {SPINE04: {'node': '', 'constraint': 'orient'}},
              {SPINE05: {'node': '', 'constraint': 'orient'}},
              {SPINE06: {'node': '', 'constraint': 'orient'}},
              {SPINE07: {'node': '', 'constraint': 'orient'}},
              {SPINE08: {'node': '', 'constraint': 'orient'}},
              {SPINE09: {'node': '', 'constraint': 'orient'}},
              {SPINE10: {'node': '', 'constraint': 'orient'}},
              {THUMB01_L: {'node': 'thumb_01_l', 'constraint': 'orient'}},
              {THUMB02_L: {'node': 'thumb_02_l', 'constraint': 'orient'}},
              {THUMB03_L: {'node': 'thumb_03_l', 'constraint': 'orient'}},
              {INDEXMETACARPAL_L: {'node': 'index_metacarpal_l', 'constraint': 'orient'}},
              {INDEX01_L: {'node': 'index_01_l', 'constraint': 'orient'}},
              {INDEX02_L: {'node': 'index_02_l', 'constraint': 'orient'}},
              {INDEX03_L: {'node': 'index_03_l', 'constraint': 'orient'}},
              {MIDDLEMETACARPAL_L: {'node': 'middle_metacarpal_l', 'constraint': 'orient'}},
              {MIDDLE01_L: {'node': 'middle_01_l', 'constraint': 'orient'}},
              {MIDDLE02_L: {'node': 'middle_02_l', 'constraint': 'orient'}},
              {MIDDLE03_L: {'node': 'middle_03_l', 'constraint': 'orient'}},
              {RINGMETACARPAL_L: {'node': 'ring_metacarpal_l', 'constraint': 'orient'}},
              {RING01_L: {'node': 'ring_01_l', 'constraint': 'orient'}},
              {RING02_L: {'node': 'ring_02_l', 'constraint': 'orient'}},
              {RING03_L: {'node': 'ring_03_l', 'constraint': 'orient'}},
              {PINKYMETACARPAL_L: {'node': 'pinky_metacarpal_l', 'constraint': 'orient'}},
              {PINKY01_L: {'node': 'pinky_01_l', 'constraint': 'orient'}},
              {PINKY02_L: {'node': 'pinky_02_l', 'constraint': 'orient'}},
              {PINKY03_L: {'node': 'pinky_03_l', 'constraint': 'orient'}}
              ]

HIVE_BIPED_STRD_JOINTS_OPTIONS = {"autoRightSide": True,
                                  "leftIdentifier": "_L",
                                  "rightIdentifier": "_R",
                                  "maintainOffset": True,
                                  "leftRightUnderscore": False,
                                  "leftRightPrefix": False,
                                  "leftRightSuffix": False}

HIVE_BIPED_STRD_JOINTS = [{ROOT: {'node': 'spine_M_00_jnt', 'constraint': 'parent'}},
                          {SHOULDER_L: {'node': 'arm_L_shldr_jnt', 'constraint': 'orient'}},
                          {ELBOW_L: {'node': 'arm_L_elbow_jnt', 'constraint': 'orient'}},
                          {WRIST_L: {'node': 'arm_L_wrist_jnt', 'constraint': 'orient'}},
                          {THIGH_L: {'node': 'leg_L_upr_jnt', 'constraint': 'orient'}},
                          {KNEE_L: {'node': 'leg_L_knee_jnt', 'constraint': 'orient'}},
                          {ANKLE_L: {'node': 'leg_L_foot_jnt', 'constraint': 'orient'}},
                          {BALL_L: {'node': 'leg_L_ball_jnt', 'constraint': 'orient'}},
                          {CLAVICLE_L: {'node': 'clavicle_L_00_jnt', 'constraint': 'orient'}},
                          {NECK01: {'node': 'head_M_neck_jnt', 'constraint': 'orient'}},
                          {NECK02: {'node': '', 'constraint': 'orient'}},
                          {HEAD: {'node': 'head_M_head_jnt', 'constraint': 'orient'}},
                          {SPINE00: {'node': 'spine_M_01_jnt', 'constraint': 'orient'}},
                          {SPINE01: {'node': 'spine_M_02_jnt', 'constraint': 'orient'}},
                          {SPINE02: {'node': 'spine_M_03_jnt', 'constraint': 'orient'}},
                          {SPINE03: {'node': 'spine_M_04_jnt', 'constraint': 'orient'}},
                          {SPINE04: {'node': 'spine_M_05_jnt', 'constraint': 'orient'}},
                          {SPINE05: {'node': 'spine_M_06_jnt', 'constraint': 'orient'}},
                          {SPINE06: {'node': 'spine_M_07_jnt', 'constraint': 'orient'}},
                          {SPINE07: {'node': 'spine_M_08_jnt', 'constraint': 'orient'}},
                          {SPINE08: {'node': 'spine_M_09_jnt', 'constraint': 'orient'}},
                          {SPINE09: {'node': 'spine_M_10_jnt', 'constraint': 'orient'}},
                          {SPINE10: {'node': 'spine_M_11_jnt', 'constraint': 'orient'}},
                          {THUMB01_L: {'node': 'finger_thumb_L_00_jnt', 'constraint': 'orient'}},
                          {THUMB02_L: {'node': 'finger_thumb_L_01_jnt', 'constraint': 'orient'}},
                          {THUMB03_L: {'node': 'finger_thumb_L_02_jnt', 'constraint': 'orient'}},
                          {INDEXMETACARPAL_L: {'node': 'finger_pointer_L_00_jnt', 'constraint': 'orient'}},
                          {INDEX01_L: {'node': 'finger_pointer_L_01_jnt', 'constraint': 'orient'}},
                          {INDEX02_L: {'node': 'finger_pointer_L_02_jnt', 'constraint': 'orient'}},
                          {INDEX03_L: {'node': 'finger_pointer_L_03_jnt', 'constraint': 'orient'}},
                          {MIDDLEMETACARPAL_L: {'node': 'finger_middle_L_00_jnt', 'constraint': 'orient'}},
                          {MIDDLE01_L: {'node': 'finger_middle_L_01_jnt', 'constraint': 'orient'}},
                          {MIDDLE02_L: {'node': 'finger_middle_L_02_jnt', 'constraint': 'orient'}},
                          {MIDDLE03_L: {'node': 'finger_middle_L_03_jnt', 'constraint': 'orient'}},
                          {RINGMETACARPAL_L: {'node': 'finger_ring_L_00_jnt', 'constraint': 'orient'}},
                          {RING01_L: {'node': 'finger_ring_L_01_jnt', 'constraint': 'orient'}},
                          {RING02_L: {'node': 'finger_ring_L_02_jnt', 'constraint': 'orient'}},
                          {RING03_L: {'node': 'finger_ring_L_03_jnt', 'constraint': 'orient'}},
                          {PINKYMETACARPAL_L: {'node': 'finger_pinky_L_00_jnt', 'constraint': 'orient'}},
                          {PINKY01_L: {'node': 'finger_pinky_L_01_jnt', 'constraint': 'orient'}},
                          {PINKY02_L: {'node': 'finger_pinky_L_02_jnt', 'constraint': 'orient'}},
                          {PINKY03_L: {'node': 'finger_pinky_L_03_jnt', 'constraint': 'orient'}}
                          ]

TWSTS = (('armUprTwstXX_L', 'arm_L_uprTwistXX_jnt'), ('armLwrTwstXX_L', 'arm_L_lwrTwistXX_jnt'),
         ('legUprTwstXX_L', 'leg_L_uprTwistXX_jnt'), ('legLwrTwstXX_L', 'leg_L_lwrTwistXX_jnt'))

HIVE_BIPED_STRD_TWST_JOINTS = list(HIVE_BIPED_STRD_JOINTS)
HIVE_BIPED_STRD_JOINTS_TWSTS = appendTwistJoints(HIVE_BIPED_STRD_TWST_JOINTS, TWSTS, twistCount=9)

HIVE_BIPED_LIGHT_JOINTS = list(HIVE_BIPED_STRD_JOINTS)  # Use STRD joints just change spine and root
HIVE_BIPED_LIGHT_JOINTS[0] = {ROOT: {'node': 'spine_M_cog_jnt', 'constraint': 'parent'}}
HIVE_BIPED_LIGHT_JOINTS[12] = {SPINE00: {'node': 'spine_M_01_jnt', 'constraint': 'orient'}}
HIVE_BIPED_LIGHT_JOINTS[13] = {SPINE01: {'node': '', 'constraint': 'orient'}}
HIVE_BIPED_LIGHT_JOINTS[14] = {SPINE02: {'node': 'spine_M_02_jnt', 'constraint': 'orient'}}

HIVE_BIPED_UE5_JOINTS = list(UE5_JOINTS)  # use UE5 joints just change root
HIVE_BIPED_UE5_JOINTS[0] = {ROOT: {'node': 'hipsSwing', 'constraint': 'parent'}}
HIVE_BIPED_UE5_JOINTS_OPTIONS = dict(UE5_JOINTS_OPTIONS)

CONTROL_MAPPINGS = [{HIVE_BIPED_K: {"nodes": HIVE_BIPED_STRD_CTRLS, "options": HIVE_BIPED_STRD_OPTIONS}},
                    {HIVE_BIPED_LIGHT_K: {"nodes": HIVE_BIPED_LIGHT_CTRLS, "options": HIVE_BIPED_STRD_OPTIONS}},
                    {HIVE_BIPED_UE_K: {"nodes": HIVE_BIPED_UE_CTRLS, "options": HIVE_BIPED_UE_OPTIONS}},
                    {SKELE_BUILDER_K: {"nodes": SKELE_BUILDER_CTRLS, "options": SKELE_BUILDER_OPTIONS}}]

SKELETON_MAPPINGS = [
    {HIVE_BIPED_JNTS_K: {"nodes": HIVE_BIPED_STRD_JOINTS, "options": HIVE_BIPED_STRD_JOINTS_OPTIONS}},
    {HIVE_BIPED_LIGHT_JNTS_K: {"nodes": HIVE_BIPED_LIGHT_JOINTS, "options": HIVE_BIPED_STRD_JOINTS_OPTIONS}},
    {HIVE_BIPED_UE5_JNTS_K: {"nodes": HIVE_BIPED_UE5_JOINTS, "options": HIVE_BIPED_UE5_JOINTS_OPTIONS}},
    {HIK_JNTS_K: {"nodes": HIK_JOINTS, "options": HIK_OPTIONS}},
    {QUICK_RIG_JNTS_K: {"nodes": HIK_JOINTS, "options": HIK_OPTIONS}},
    {MIXAMO_JNTS_K: {"nodes": HIK_JOINTS, "options": HIK_OPTIONS}},
    {ROKOKO_JNTS_K: {"nodes": HIK_JOINTS, "options": HIK_OPTIONS}},
    {ROKOKO_VAR_JNTS_K: {"nodes": ROKOKO_VAR1_JOINTS, "options": HIK_OPTIONS}},
    {UE5_JNTS_K: {"nodes": UE5_JOINTS, "options": UE5_JOINTS_OPTIONS}},
    {ACCU_RIG_JNTS_K: {"nodes": ACCU_RIG_JOINTS, "options": ACCU_RIG_OPTIONS}},
    {SKELE_BUILDER_JNTS_K: {"nodes": SKELE_BUILDER_JOINTS, "options": SKELE_BUILDER_OPTIONS}}]

SKELETON_TWIST_MAPPINGS = [
    {HIVE_BIPED_JNTS_K: {"nodes": HIVE_BIPED_STRD_JOINTS_TWSTS, "options": HIVE_BIPED_STRD_JOINTS_OPTIONS}},
    {HIVE_BIPED_LIGHT_JNTS_K: {"nodes": HIVE_BIPED_LIGHT_JOINTS, "options": HIVE_BIPED_STRD_JOINTS_OPTIONS}},
    {HIVE_BIPED_UE5_JNTS_K: {"nodes": HIVE_BIPED_UE5_JOINTS, "options": HIVE_BIPED_UE5_JOINTS_OPTIONS}},
    {HIVE_BIPED_UE5_JNTS_K: {"nodes": HIK_JOINTS, "options": HIK_OPTIONS}},
    {QUICK_RIG_JNTS_K: {"nodes": HIK_JOINTS, "options": HIK_OPTIONS}},
    {MIXAMO_JNTS_K: {"nodes": HIK_JOINTS, "options": HIK_OPTIONS}},
    {ROKOKO_JNTS_K: {"nodes": HIK_JOINTS, "options": HIK_OPTIONS}},
    {ROKOKO_VAR_JNTS_K: {"nodes": ROKOKO_VAR1_JOINTS, "options": HIK_OPTIONS}},
    {UE5_JNTS_K: {"nodes": UE5_JOINTS, "options": UE5_JOINTS_OPTIONS}},
    {ACCU_RIG_JNTS_K: {"nodes": ACCU_RIG_TWST_JOINTS, "options": ACCU_RIG_OPTIONS}},
    {SKELE_BUILDER_JNTS_K: {"nodes": SKELE_BUILDER_JOINTS, "options": SKELE_BUILDER_OPTIONS}}]

ALL_MAPPINGS = CONTROL_MAPPINGS + [{"--- Joints ---": {}}] + SKELETON_MAPPINGS

ALL_MAPPINGS_TODO = [{HIVE_BIPED_K: {"nodes": HIVE_BIPED_STRD_CTRLS, "options": HIVE_BIPED_STRD_OPTIONS}},
                     {HIVE_BIPED_LIGHT_K: {"nodes": HIVE_BIPED_LIGHT_CTRLS, "options": HIVE_BIPED_STRD_OPTIONS}},
                     {HIVE_BIPED_UE_K: {"nodes": HIVE_BIPED_UE_CTRLS, "options": HIVE_BIPED_UE_OPTIONS}},
                     {SKELE_BUILDER_K: {"nodes": SKELE_BUILDER_CTRLS, "options": SKELE_BUILDER_OPTIONS}},
                     {"MGear Ctrls": {"nodes": ACCU_RIG_JOINTS, "options": ACCU_RIG_OPTIONS}},
                     {"Advanced Skele Ctrls": {"nodes": ACCU_RIG_JOINTS, "options": ACCU_RIG_OPTIONS}},
                     {"--- Joints ---": {}},
                     {HIVE_BIPED_JNTS_K: {"nodes": HIVE_BIPED_STRD_JOINTS,
                                          "options": HIVE_BIPED_STRD_JOINTS_OPTIONS}},
                     {HIVE_BIPED_LIGHT_JNTS_K: {"nodes": HIVE_BIPED_LIGHT_JOINTS,
                                                "options": HIVE_BIPED_STRD_JOINTS_OPTIONS}},
                     {HIVE_BIPED_UE5_JNTS_K: {"nodes": HIVE_BIPED_UE5_JOINTS,
                                              "options": HIVE_BIPED_UE5_JOINTS_OPTIONS}},
                     {HIVE_BIPED_UE5_JNTS_K: {"nodes": HIK_JOINTS, "options": HIK_OPTIONS}},
                     {QUICK_RIG_JNTS_K: {"nodes": HIK_JOINTS, "options": HIK_OPTIONS}},
                     {MIXAMO_JNTS_K: {"nodes": HIK_JOINTS, "options": HIK_OPTIONS}},
                     {ROKOKO_JNTS_K: {"nodes": HIK_JOINTS, "options": HIK_OPTIONS}},
                     {ROKOKO_VAR_JNTS_K: {"nodes": ROKOKO_VAR1_JOINTS, "options": HIK_OPTIONS}},
                     {UE5_JNTS_K: {"nodes": UE5_JOINTS, "options": UE5_JOINTS_OPTIONS}},
                     {ACCU_RIG_JNTS_K: {"nodes": ACCU_RIG_JOINTS, "options": ACCU_RIG_OPTIONS}},
                     {"Daz CC Jnts": {"nodes": ACCU_RIG_JOINTS, "options": ACCU_RIG_OPTIONS}},
                     {SKELE_BUILDER_JNTS_K: {"nodes": SKELE_BUILDER_JOINTS, "options": SKELE_BUILDER_OPTIONS}},
                     {"MGear Jnts": {"nodes": ACCU_RIG_JOINTS, "options": ACCU_RIG_OPTIONS}},
                     {"Advanced Skele Jnts": {"nodes": ACCU_RIG_JOINTS, "options": ACCU_RIG_OPTIONS}},
                     {"--- User Presets ---": {}}]
