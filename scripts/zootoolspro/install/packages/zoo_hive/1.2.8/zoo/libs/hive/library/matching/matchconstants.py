"""
from zoo.libs.hive.library.matching import matchconstants
HIVE_IDS = matchconstants.HIVE_IDS  # list of tuples, name and hive id dictionary
SKELETONS = matchconstants.SKELETONS  # list of tuples, name and skeleton id dictionary
"""

from zoo.libs.maya.cmds.animation import batchconstraintconstants as bcc

ROOT_KEY = bcc.ROOT
SHOULDER_KEY_L = bcc.SHOULDER_L
ELBOW_KEY_L = bcc.ELBOW_L
WRIST_KEY_L = bcc.WRIST_L
THIGH_KEY_L = bcc.THIGH_L
KNEE_KEY_L = bcc.KNEE_L
ANKLE_KEY_L = bcc.ANKLE_L
BALL_KEY_L = bcc.BALL_L
TOE_KEY_L = bcc.TOE_L
CLAVICLE_KEY_L = bcc.CLAVICLE_L
HIP_KEY_M = bcc.HIP_KEY_M  # Spine IK base
CHEST_KEY_M = bcc.CHEST_KEY_M  # Spine IK top
NECK_KEY_M = bcc.NECK01
HEAD_KEY_M = bcc.HEAD
SPINE00_KEY_M = bcc.SPINE00
SPINE01_KEY_M = bcc.SPINE01
SPINE02_KEY_M = bcc.SPINE02
SPINE03_KEY_M = bcc.SPINE03
SPINE04_KEY_M = bcc.SPINE04
SPINE05_KEY_M = bcc.SPINE05
SPINE06_KEY_M = bcc.SPINE06
SPINE07_KEY_M = bcc.SPINE07
SPINE08_KEY_M = bcc.SPINE08
SPINE09_KEY_M = bcc.SPINE09
SPINE10_KEY_M = bcc.SPINE10
THUMB01_KEY_L = bcc.THUMB01_L
THUMB02_KEY_L = bcc.THUMB02_L
THUMB03_KEY_L = bcc.THUMB03_L
INDEXMETACARPAL_KEY_L = bcc.INDEXMETACARPAL_L
INDEX01_KEY_L = bcc.INDEX01_L
INDEX02_KEY_L = bcc.INDEX02_L
INDEX03_KEY_L = bcc.INDEX03_L
MIDDLEMETACARPAL_KEY_L = bcc.MIDDLEMETACARPAL_L
MIDDLE01_KEY_L = bcc.MIDDLE01_L
MIDDLE02_KEY_L = bcc.MIDDLE02_L
MIDDLE03_KEY_L = bcc.MIDDLE03_L
RINGMETACARPAL_KEY_L = bcc.RINGMETACARPAL_L
RING01_KEY_L = bcc.RING01_L
RING02_KEY_L = bcc.RING02_L
RING03_KEY_L = bcc.RING03_L
PINKYMETACARPAL_KEY_L = bcc.PINKYMETACARPAL_L
PINKY01_KEY_L = bcc.PINKY01_L
PINKY02_KEY_L = bcc.PINKY02_L
PINKY03_KEY_L = bcc.PINKY03_L

SPINESPINE_ORDER = [ROOT_KEY, HIP_KEY_M, CHEST_KEY_M]
FKSPINE_ORDER = [ROOT_KEY, SPINE00_KEY_M, SPINE01_KEY_M, SPINE02_KEY_M, SPINE03_KEY_M, SPINE04_KEY_M, SPINE05_KEY_M,
                 SPINE06_KEY_M, SPINE07_KEY_M, SPINE08_KEY_M, SPINE09_KEY_M, SPINE10_KEY_M]

HIERARCHY_ORDER_NO_SPINE = [NECK_KEY_M, HEAD_KEY_M, CLAVICLE_KEY_L, SHOULDER_KEY_L,
                            WRIST_KEY_L, ELBOW_KEY_L, THUMB01_KEY_L, THUMB02_KEY_L, THUMB03_KEY_L,
                            INDEXMETACARPAL_KEY_L, INDEX01_KEY_L, INDEX02_KEY_L, INDEX03_KEY_L,
                            MIDDLEMETACARPAL_KEY_L, MIDDLE01_KEY_L, MIDDLE02_KEY_L, MIDDLE03_KEY_L,
                            RINGMETACARPAL_KEY_L, RING01_KEY_L, RING02_KEY_L, RING03_KEY_L,
                            PINKYMETACARPAL_KEY_L, PINKY01_KEY_L, PINKY02_KEY_L, PINKY03_KEY_L,
                            THIGH_KEY_L, ANKLE_KEY_L, KNEE_KEY_L, BALL_KEY_L, TOE_KEY_L]

HIERARCHY_ORDER_SPLINESPINE = SPINESPINE_ORDER + HIERARCHY_ORDER_NO_SPINE
HIERARCHY_ORDER_FKSPINE = FKSPINE_ORDER + FKSPINE_ORDER

# Rotate align guides all finger joints need to rotate match align to skeleton fingers
ROT_ALIGN_GUIDES = [THUMB01_KEY_L, THUMB02_KEY_L, THUMB03_KEY_L,
                    INDEXMETACARPAL_KEY_L, INDEX01_KEY_L, INDEX02_KEY_L, INDEX03_KEY_L,
                    MIDDLEMETACARPAL_KEY_L, MIDDLE01_KEY_L, MIDDLE02_KEY_L, MIDDLE03_KEY_L,
                    RINGMETACARPAL_KEY_L, RING01_KEY_L, RING02_KEY_L, RING03_KEY_L,
                    PINKYMETACARPAL_KEY_L, PINKY01_KEY_L, PINKY02_KEY_L, PINKY03_KEY_L]

# Hive IDs -----------------------------------------------------------------------------------------------------------

HIVE_BIPED_SPLINE_IDS = {ROOT_KEY: ["god", "root", "M"],
                         SHOULDER_KEY_L: ["arm", "root", "L"],
                         ELBOW_KEY_L: ["arm", "mid", "L"],
                         WRIST_KEY_L: ["arm", "end", "L"],
                         THIGH_KEY_L: ["leg", "root", "L"],
                         KNEE_KEY_L: ["leg", "mid", "L"],
                         ANKLE_KEY_L: ["leg", "end", "L"],
                         BALL_KEY_L: ["leg", "ball", "L"],
                         TOE_KEY_L: ["leg", "toe", "L"],
                         CLAVICLE_KEY_L: ["clavicle", "root", "L"],
                         HIP_KEY_M: ["spine", "root", "M"],
                         CHEST_KEY_M: ["spine", "endCurvePiv", "M"],
                         NECK_KEY_M: ["head", "root", "M"],
                         HEAD_KEY_M: ["head", "head", "M"],
                         SPINE00_KEY_M: ["spine", "00", "M"],
                         SPINE01_KEY_M: ["spine", "01", "M"],
                         SPINE02_KEY_M: ["spine", "02", "M"],
                         SPINE03_KEY_M: ["spine", "03", "M"],
                         THUMB01_KEY_L: ["finger_thumb", "root", "L"],
                         THUMB02_KEY_L: ["finger_thumb", "fk01", "L"],
                         THUMB03_KEY_L: ["finger_thumb", "fk02", "L"],
                         INDEXMETACARPAL_KEY_L: ["finger_pointer", "root", "L"],
                         INDEX01_KEY_L: ["finger_pointer", "fk01", "L"],
                         INDEX02_KEY_L: ["finger_pointer", "fk02", "L"],
                         INDEX03_KEY_L: ["finger_pointer", "fk03", "L"],
                         MIDDLEMETACARPAL_KEY_L: ["finger_middle", "root", "L"],
                         MIDDLE01_KEY_L: ["finger_middle", "fk01", "L"],
                         MIDDLE02_KEY_L: ["finger_middle", "fk02", "L"],
                         MIDDLE03_KEY_L: ["finger_middle", "fk03", "L"],
                         RINGMETACARPAL_KEY_L: ["finger_ring", "root", "L"],
                         RING01_KEY_L: ["finger_ring", "fk01", "L"],
                         RING02_KEY_L: ["finger_ring", "fk02", "L"],
                         RING03_KEY_L: ["finger_ring", "fk03", "L"],
                         PINKYMETACARPAL_KEY_L: ["finger_pinky", "root", "L"],
                         PINKY01_KEY_L: ["finger_pinky", "fk01", "L"],
                         PINKY02_KEY_L: ["finger_pinky", "fk02", "L"],
                         PINKY03_KEY_L: ["finger_pinky", "fk03", "L"]
                         }

HIVE_BIPED_FK_IDS = {ROOT_KEY: ["god", "root", "M"],
                     SHOULDER_KEY_L: ["arm", "root", "L"],
                     ELBOW_KEY_L: ["arm", "mid", "L"],
                     WRIST_KEY_L: ["arm", "end", "L"],
                     THIGH_KEY_L: ["leg", "root", "L"],
                     KNEE_KEY_L: ["leg", "mid", "L"],
                     ANKLE_KEY_L: ["leg", "end", "L"],
                     BALL_KEY_L: ["leg", "ball", "L"],
                     TOE_KEY_L: ["leg", "toe", "L"],
                     CLAVICLE_KEY_L: ["clavicle", "root", "L"],
                     HIP_KEY_M: ["spine", "root", "M"],
                     CHEST_KEY_M: ["spine", "endCurvePiv", "M"],
                     NECK_KEY_M: ["head", "root", "M"],
                     HEAD_KEY_M: ["head", "head", "M"],
                     SPINE00_KEY_M: ["spineFk", "00", "M"],
                     SPINE01_KEY_M: ["spineFk", "01", "M"],
                     SPINE02_KEY_M: ["spineFk", "02", "M"],
                     SPINE03_KEY_M: ["spineFk", "03", "M"],
                     SPINE04_KEY_M: ["spineFk", "04", "M"],
                     SPINE05_KEY_M: ["spineFk", "05", "M"],
                     SPINE06_KEY_M: ["spineFk", "06", "M"],
                     SPINE07_KEY_M: ["spineFk", "07", "M"],
                     SPINE08_KEY_M: ["spineFk", "08", "M"],
                     SPINE09_KEY_M: ["spineFk", "09", "M"],
                     SPINE10_KEY_M: ["spineFk", "10", "M"],
                     THUMB01_KEY_L: ["finger_thumb", "root", "L"],
                     THUMB02_KEY_L: ["finger_thumb", "fk01", "L"],
                     THUMB03_KEY_L: ["finger_thumb", "fk02", "L"],
                     INDEXMETACARPAL_KEY_L: ["finger_pointer", "root", "L"],
                     INDEX01_KEY_L: ["finger_pointer", "fk01", "L"],
                     INDEX02_KEY_L: ["finger_pointer", "fk02", "L"],
                     INDEX03_KEY_L: ["finger_pointer", "fk03", "L"],
                     MIDDLEMETACARPAL_KEY_L: ["finger_middle", "root", "L"],
                     MIDDLE01_KEY_L: ["finger_middle", "fk01", "L"],
                     MIDDLE02_KEY_L: ["finger_middle", "fk02", "L"],
                     MIDDLE03_KEY_L: ["finger_middle", "fk03", "L"],
                     RINGMETACARPAL_KEY_L: ["finger_ring", "root", "L"],
                     RING01_KEY_L: ["finger_ring", "fk01", "L"],
                     RING02_KEY_L: ["finger_ring", "fk02", "L"],
                     RING03_KEY_L: ["finger_ring", "fk03", "L"],
                     PINKYMETACARPAL_KEY_L: ["finger_pinky", "root", "L"],
                     PINKY01_KEY_L: ["finger_pinky", "fk01", "L"],
                     PINKY02_KEY_L: ["finger_pinky", "fk02", "L"],
                     PINKY03_KEY_L: ["finger_pinky", "fk03", "L"]
                     }

HIVE_IDS = [(bcc.HIVE_BIPED_K, HIVE_BIPED_SPLINE_IDS, HIERARCHY_ORDER_SPLINESPINE),
            (bcc.HIVE_BIPED_LIGHT_K, HIVE_BIPED_FK_IDS, HIERARCHY_ORDER_FKSPINE),
            (bcc.HIVE_BIPED_UE_K, dict(), HIERARCHY_ORDER_FKSPINE),
            (bcc.SKELE_BUILDER_K, dict(), HIERARCHY_ORDER_FKSPINE)]

# Skeletons -----------------------------------------------------------------------------------------------------------


HIVE_BIPED_SKELETON = {ROOT_KEY: "god_M_godnode_jnt",
                       SHOULDER_KEY_L: "arm_L_shldr_jnt",
                       ELBOW_KEY_L: "arm_L_elbow_jnt",
                       WRIST_KEY_L: "arm_L_wrist_jnt",
                       THIGH_KEY_L: "leg_L_upr_jnt",
                       KNEE_KEY_L: "leg_L_knee_jnt",
                       ANKLE_KEY_L: "leg_L_foot_jnt",
                       BALL_KEY_L: "leg_L_ball_jnt",
                       TOE_KEY_L: "leg_L_toe_jnt",
                       CLAVICLE_KEY_L: "clavicle_L_00_jnt",
                       HIP_KEY_M: "spine_M_00_jnt",
                       CHEST_KEY_M: "spine_M_05_jnt",
                       NECK_KEY_M: "head_M_neck_jnt",
                       HEAD_KEY_M: "head_M_head_jnt",
                       SPINE00_KEY_M: "spine_M_00_jnt",
                       SPINE01_KEY_M: "spine_M_01_jnt",
                       SPINE02_KEY_M: "spine_M_02_jnt",
                       SPINE03_KEY_M: "spine_M_03_jnt",
                       SPINE04_KEY_M: "spine_M_04_jnt",
                       SPINE05_KEY_M: "spine_M_05_jnt",
                       SPINE06_KEY_M: "spine_M_06_jnt",
                       SPINE07_KEY_M: "spine_M_07_jnt",
                       SPINE08_KEY_M: "spine_M_08_jnt",
                       SPINE09_KEY_M: "spine_M_09_jnt",
                       SPINE10_KEY_M: "spine_M_10_jnt",
                       THUMB01_KEY_L: "finger_thumb_L_00_jnt",
                       THUMB02_KEY_L: "finger_thumb_L_01_jnt",
                       THUMB03_KEY_L: "finger_thumb_L_02_jnt",
                       INDEXMETACARPAL_KEY_L: "finger_pointer_L_00_jnt",
                       INDEX01_KEY_L: "finger_pointer_L_01_jnt",
                       INDEX02_KEY_L: "finger_pointer_L_02_jnt",
                       INDEX03_KEY_L: "finger_pointer_L_03_jnt",
                       MIDDLEMETACARPAL_KEY_L: "finger_middle_L_00_jnt",
                       MIDDLE01_KEY_L: "finger_middle_L_01_jnt",
                       MIDDLE02_KEY_L: "finger_middle_L_02_jnt",
                       MIDDLE03_KEY_L: "finger_middle_L_03_jnt",
                       RINGMETACARPAL_KEY_L: "finger_ring_L_00_jnt",
                       RING01_KEY_L: "finger_ring_L_01_jnt",
                       RING02_KEY_L: "finger_ring_L_02_jnt",
                       RING03_KEY_L: "finger_ring_L_03_jnt",
                       PINKYMETACARPAL_KEY_L: "finger_pinky_L_00_jnt",
                       PINKY01_KEY_L: "finger_pinky_L_01_jnt",
                       PINKY02_KEY_L: "finger_pinky_L_02_jnt",
                       PINKY03_KEY_L: "finger_pinky_L_03_jnt",
                       }

SKELEBUILDER_BIPED_SKELETON = {ROOT_KEY: "",
                               SHOULDER_KEY_L: "L_bicep",
                               ELBOW_KEY_L: "L_elbow",
                               WRIST_KEY_L: "L_wrist",
                               THIGH_KEY_L: "L_leg01",
                               KNEE_KEY_L: "L_leg02",
                               ANKLE_KEY_L: "L_leg03",
                               BALL_KEY_L: "L_toeBase",
                               TOE_KEY_L: "L_leg03_tip",
                               CLAVICLE_KEY_L: "L_clavicle",
                               HIP_KEY_M: "root",
                               CHEST_KEY_M: "spine5",
                               NECK_KEY_M: "neck1",
                               HEAD_KEY_M: "head",
                               SPINE00_KEY_M: "root",
                               SPINE01_KEY_M: "spine1",
                               SPINE02_KEY_M: "spine2",
                               SPINE03_KEY_M: "spine3",
                               SPINE04_KEY_M: "spine4",
                               SPINE05_KEY_M: "spine5",
                               SPINE06_KEY_M: "spine6",
                               SPINE07_KEY_M: "spine7",
                               SPINE08_KEY_M: "spine8",
                               SPINE09_KEY_M: "spine9",
                               SPINE10_KEY_M: "spine10",
                               THUMB01_KEY_L: "Thumb_0_L",
                               THUMB02_KEY_L: "Thumb_1_L",
                               THUMB03_KEY_L: "Thumb_2_L",
                               INDEXMETACARPAL_KEY_L: "Index_0_L",
                               INDEX01_KEY_L: "Index_1_L",
                               INDEX02_KEY_L: "Index_2_L",
                               INDEX03_KEY_L: "Index_3_L",
                               MIDDLEMETACARPAL_KEY_L: "Mid_0_L",
                               MIDDLE01_KEY_L: "Mid_1_L",
                               MIDDLE02_KEY_L: "Mid_2_L",
                               MIDDLE03_KEY_L: "Mid_3_L",
                               RINGMETACARPAL_KEY_L: "Ring_0_L",
                               RING01_KEY_L: "Ring_1_L",
                               RING02_KEY_L: "Ring_2_L",
                               RING03_KEY_L: "Ring_3_L",
                               PINKYMETACARPAL_KEY_L: "Pinky_0_L",
                               PINKY01_KEY_L: "Pinky_1_L",
                               PINKY02_KEY_L: "Pinky_2_L",
                               PINKY03_KEY_L: "Pinky_3_L",
                               }

HUMANIK_BIPED_SKELETON = {ROOT_KEY: "",
                          SHOULDER_KEY_L: "LeftArm",
                          ELBOW_KEY_L: "LeftForeArm",
                          WRIST_KEY_L: "LeftHand",
                          THIGH_KEY_L: "LeftUpLeg",
                          KNEE_KEY_L: "LeftLeg",
                          ANKLE_KEY_L: "LeftFoot",
                          BALL_KEY_L: "LeftToeBase",
                          TOE_KEY_L: "LeftToe_End",
                          CLAVICLE_KEY_L: "LeftShoulder",
                          HIP_KEY_M: "Hips",
                          CHEST_KEY_M: "Spine2",
                          NECK_KEY_M: "Neck",
                          HEAD_KEY_M: "Head",
                          SPINE00_KEY_M: "Hips",
                          SPINE01_KEY_M: "Spine",
                          SPINE02_KEY_M: "Spine1",
                          SPINE03_KEY_M: "Spine2",
                          SPINE04_KEY_M: "Spine3",
                          SPINE05_KEY_M: "Spine4",
                          SPINE06_KEY_M: "Spine5",
                          SPINE07_KEY_M: "Spine6",
                          SPINE08_KEY_M: "Spine7",
                          SPINE09_KEY_M: "Spine8",
                          SPINE10_KEY_M: "Spine9",
                          THUMB01_KEY_L: "LeftHandThumb1",
                          THUMB02_KEY_L: "LeftHandThumb2",
                          THUMB03_KEY_L: "LeftHandThumb3",
                          INDEXMETACARPAL_KEY_L: "",
                          INDEX01_KEY_L: "LeftHandIndex1",
                          INDEX02_KEY_L: "LeftHandIndex2",
                          INDEX03_KEY_L: "LeftHandIndex3",
                          MIDDLEMETACARPAL_KEY_L: "",
                          MIDDLE01_KEY_L: "LeftHandMiddle1",
                          MIDDLE02_KEY_L: "LeftHandMiddle2",
                          MIDDLE03_KEY_L: "LeftHandMiddle3",
                          RINGMETACARPAL_KEY_L: "",
                          RING01_KEY_L: "LeftHandRing1",
                          RING02_KEY_L: "LeftHandRing2",
                          RING03_KEY_L: "LeftHandRing3",
                          PINKYMETACARPAL_KEY_L: "",
                          PINKY01_KEY_L: "LeftHandPinky1",
                          PINKY02_KEY_L: "LeftHandPinky2",
                          PINKY03_KEY_L: "LeftHandPinky3",
                          }

MIXAMO_BIPED_SKELETON = HUMANIK_BIPED_SKELETON

UNITY_BIPED_SKELETON = HUMANIK_BIPED_SKELETON  # Not sure but seems Human IK is ok

ROKOKO_BIPED_SKELETON = HUMANIK_BIPED_SKELETON

ROKOKO_VAR1_SKELETON = dict(HUMANIK_BIPED_SKELETON)
ROKOKO_VAR1_SKELETON[THIGH_KEY_L] = "LeftThigh"
ROKOKO_VAR1_SKELETON[KNEE_KEY_L] = "LeftShin"
ROKOKO_VAR1_SKELETON[ANKLE_KEY_L] = "LeftFoot"
ROKOKO_VAR1_SKELETON[BALL_KEY_L] = "LeftToe"
ROKOKO_VAR1_SKELETON[TOE_KEY_L] = "LeftToe_End"
ROKOKO_VAR1_SKELETON[THUMB01_KEY_L] = "LeftFinger1Metacarpal"
ROKOKO_VAR1_SKELETON[THUMB02_KEY_L] = "LeftFinger1Proximal"
ROKOKO_VAR1_SKELETON[THUMB03_KEY_L] = "LeftFinger1Distal"
ROKOKO_VAR1_SKELETON[INDEXMETACARPAL_KEY_L] = "LeftFinger2Metacarpal"
ROKOKO_VAR1_SKELETON[INDEX01_KEY_L] = "LeftFinger2Proximal"
ROKOKO_VAR1_SKELETON[INDEX02_KEY_L] = "LeftFinger2Medial"
ROKOKO_VAR1_SKELETON[INDEX03_KEY_L] = "LeftFinger2Distal"
ROKOKO_VAR1_SKELETON[MIDDLEMETACARPAL_KEY_L] = "LeftFinger3Metacarpal"
ROKOKO_VAR1_SKELETON[MIDDLE01_KEY_L] = "LeftFinger3Proximal"
ROKOKO_VAR1_SKELETON[MIDDLE02_KEY_L] = "LeftFinger3Medial"
ROKOKO_VAR1_SKELETON[MIDDLE03_KEY_L] = "LeftFinger3Distal"
ROKOKO_VAR1_SKELETON[RINGMETACARPAL_KEY_L] = "LeftFinger4Metacarpal"
ROKOKO_VAR1_SKELETON[RING01_KEY_L] = "LeftFinger4Proximal"
ROKOKO_VAR1_SKELETON[RING02_KEY_L] = "LeftFinger4Medial"
ROKOKO_VAR1_SKELETON[RING03_KEY_L] = "LeftFinger4Distal"
ROKOKO_VAR1_SKELETON[PINKYMETACARPAL_KEY_L] = "LeftFinger5Metacarpal"
ROKOKO_VAR1_SKELETON[PINKY01_KEY_L] = "LeftFinger5Proximal"
ROKOKO_VAR1_SKELETON[PINKY02_KEY_L] = "LeftFinger5Medial"
ROKOKO_VAR1_SKELETON[PINKY03_KEY_L] = "LeftFinger5Distal"

ACCURIG_BIPED_SKELETON = {ROOT_KEY: "RL_BoneRoot",
                          SHOULDER_KEY_L: "CC_Base_L_Upperarm",
                          ELBOW_KEY_L: "CC_Base_L_Forearm",
                          WRIST_KEY_L: "CC_Base_L_Hand",
                          THIGH_KEY_L: "CC_Base_L_Thigh",
                          KNEE_KEY_L: "CC_Base_L_Calf",
                          ANKLE_KEY_L: "CC_Base_L_Foot",
                          BALL_KEY_L: "CC_Base_L_ToeBase",
                          TOE_KEY_L: "CC_Base_L_ToeBase",
                          CLAVICLE_KEY_L: "CC_Base_L_Clavicle",
                          HIP_KEY_M: "CC_Base_Hip",
                          CHEST_KEY_M: "CC_Base_Spine02",
                          NECK_KEY_M: "CC_Base_NeckTwist01",
                          HEAD_KEY_M: "CC_Base_Head",
                          SPINE00_KEY_M: "CC_Base_Pelvis",
                          SPINE01_KEY_M: "CC_Base_Waist",
                          SPINE02_KEY_M: "CC_Base_Spine01",
                          SPINE03_KEY_M: "CC_Base_Spine02",
                          SPINE04_KEY_M: "CC_Base_Spine03",
                          SPINE05_KEY_M: "CC_Base_Spine04",
                          SPINE06_KEY_M: "CC_Base_Spine05",
                          SPINE07_KEY_M: "CC_Base_Spine06",
                          SPINE08_KEY_M: "CC_Base_Spine07",
                          SPINE09_KEY_M: "CC_Base_Spine08",
                          SPINE10_KEY_M: "CC_Base_Spine09",
                          THUMB01_KEY_L: "CC_Base_L_Thumb1",
                          THUMB02_KEY_L: "CC_Base_L_Thumb2",
                          THUMB03_KEY_L: "CC_Base_L_Thumb3",
                          INDEXMETACARPAL_KEY_L: "",
                          INDEX01_KEY_L: "CC_Base_L_Index1",
                          INDEX02_KEY_L: "CC_Base_L_Index2",
                          INDEX03_KEY_L: "CC_Base_L_Index3",
                          MIDDLEMETACARPAL_KEY_L: "",
                          MIDDLE01_KEY_L: "CC_Base_L_Mid1",
                          MIDDLE02_KEY_L: "CC_Base_L_Mid2",
                          MIDDLE03_KEY_L: "CC_Base_L_Mid3",
                          RINGMETACARPAL_KEY_L: "",
                          RING01_KEY_L: "CC_Base_L_Ring1",
                          RING02_KEY_L: "CC_Base_L_Ring2",
                          RING03_KEY_L: "CC_Base_L_Ring3",
                          PINKYMETACARPAL_KEY_L: "",
                          PINKY01_KEY_L: "CC_Base_L_Pinky1",
                          PINKY02_KEY_L: "CC_Base_L_Pinky2",
                          PINKY03_KEY_L: "CC_Base_L_Pinky3",
                          }

UE5_BIPED_SKELETON = {ROOT_KEY: "root",
                      SHOULDER_KEY_L: "upperarm_l",
                      ELBOW_KEY_L: "lowerarm_l",
                      WRIST_KEY_L: "hand_l",
                      THIGH_KEY_L: "thigh_l",
                      KNEE_KEY_L: "calf_l",
                      ANKLE_KEY_L: "foot_l",
                      BALL_KEY_L: "ball_l",
                      TOE_KEY_L: "toe_l",
                      CLAVICLE_KEY_L: "clavicle_l",
                      HIP_KEY_M: "hipsSwing",
                      CHEST_KEY_M: "spine_06",
                      NECK_KEY_M: "neck_01",
                      HEAD_KEY_M: "head",
                      SPINE00_KEY_M: "hipsSwing",
                      SPINE01_KEY_M: "spine_01",
                      SPINE02_KEY_M: "spine_02",
                      SPINE03_KEY_M: "spine_03",
                      SPINE04_KEY_M: "spine_04",
                      SPINE05_KEY_M: "spine_05",
                      SPINE06_KEY_M: "spine_06",
                      SPINE07_KEY_M: "spine_07",
                      SPINE08_KEY_M: "spine_08",
                      SPINE09_KEY_M: "spine_09",
                      SPINE10_KEY_M: "spine_10",
                      THUMB01_KEY_L: "thumb_01_l",
                      THUMB02_KEY_L: "thumb_02_l",
                      THUMB03_KEY_L: "thumb_03_l",
                      INDEXMETACARPAL_KEY_L: "index_metacarpal_l",
                      INDEX01_KEY_L: "index_01_l",
                      INDEX02_KEY_L: "index_02_l",
                      INDEX03_KEY_L: "index_03_l",
                      MIDDLEMETACARPAL_KEY_L: "middle_metacarpal_l",
                      MIDDLE01_KEY_L: "middle_01_l",
                      MIDDLE02_KEY_L: "middle_02_l",
                      MIDDLE03_KEY_L: "middle_03_l",
                      RINGMETACARPAL_KEY_L: "ring_metacarpal_l",
                      RING01_KEY_L: "ring_01_l",
                      RING02_KEY_L: "ring_02_l",
                      RING03_KEY_L: "ring_03_l",
                      PINKYMETACARPAL_KEY_L: "pinky_metacarpal_l",
                      PINKY01_KEY_L: "pinky_01_l",
                      PINKY02_KEY_L: "pinky_02_l",
                      PINKY03_KEY_L: "pinky_03_l",
                      }

SKELETONS = [(bcc.HIVE_BIPED_JNTS_K, HIVE_BIPED_SKELETON),
             (bcc.HIVE_BIPED_LIGHT_JNTS_K, HIVE_BIPED_FK_IDS),
             (bcc.MIXAMO_JNTS_K, MIXAMO_BIPED_SKELETON),
             (bcc.ROKOKO_JNTS_K, ROKOKO_BIPED_SKELETON),
             (bcc.ROKOKO_VAR_JNTS_K, ROKOKO_VAR1_SKELETON),
             (bcc.HIK_JNTS_K, HUMANIK_BIPED_SKELETON),
             (bcc.UNITY_JNTS_K, UNITY_BIPED_SKELETON),
             (bcc.ACCU_RIG_JNTS_K, ACCURIG_BIPED_SKELETON),
             (bcc.UE5_JNTS_K, UE5_BIPED_SKELETON),
             (bcc.SKELE_BUILDER_K, SKELEBUILDER_BIPED_SKELETON)]
