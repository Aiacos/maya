"""Cartoon_A_Quadruped_Front module creates a cartoon_complex quadruped front leg module. """

from arise.utils.subcomponents.quadruped_leg import QuadrupedLeg

MAYA_VERSION = 2016  # the version of Maya from which this module supports.
AUTHOR = "Etay Herz"  # name of person who created this module.
RIG_CATEGORY = "Cartoon"  # either 'Basic', 'Cartoon', 'Vfx', 'Game' or 'All'. (used when filtering).
RIG_TYPE = "Quadruped"  # Biped, Car, Quadruped, All, ... (for filtering modules in lists).
TAGS = ["cartoon", "complex", "advance", "ribbon", "bendy bones", "ik", "fk", "leg", "quadruped"]
TOOL_TIP = "Cartoon quadruped front leg with IK/FK, ribbons, twist, soft IK, stretch, pin ctrl and more."


class CA_Quadruped_Front_Leg(QuadrupedLeg):
    """Create a cartoon_complex quadruped front leg module. """
    AUTO_CLAVICLE_DEFAULT = True
    GUIDES_POSITIONS = {
        "base": [8.3, 125.1, 34.5],
        "root": [13.9, 97.4, 57.9],
        "mid": [13.5, 81.5, 43.1],
        "tip": [12.5, 42.9, 45.5],
        "toes_root": [12.5, 15.4, 45.7],
        "heel": [12.5, 0, 46.2],
        "toes_tip": [12.5, 0, 59.5],
        "outer_tilt": [17.0, 0, 52.85],
        "inner_tilt": [8.0, 0, 52.85],
    }
    PV_GUIDE_OFFSET = (10, 31)
    AIM_ROTATION_OFFSET = [0, 180, 0]
    BASE_SKINNING_JNT = True
    JNTS_HUMAN_IK = {"base_jnt": "*Shoulder", "tip_jnt": "*Hand"}
    UPPER_ROLL_TAGS = ("*Arm", "Leaf*ArmRoll{0}")
    LOWER_ROLL_TAGS = ("*ForeArm", "Leaf*ForeArmRoll{0}")
    CTRLS_HUMAN_IK = {"base_ctrl": "*Clavicle", "ik_tip_ctrl": "*Hand", "ik_pv_ctrl": "*Elbow"}
    WORLD_DIRECTION_FLIP_X = True
    BASE_CTRL_VIS_DEFAULT = 1
    AIM_UP_VECTOR = (0, 0, -1)
