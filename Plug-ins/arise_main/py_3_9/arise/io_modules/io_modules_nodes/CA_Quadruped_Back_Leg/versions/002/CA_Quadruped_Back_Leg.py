"""Cartoon_A_Quadruped_Back module creates a cartoon_complex quadruped back leg module. """

from arise.utils.subcomponents.quadruped_leg import QuadrupedLeg

MAYA_VERSION = 2016  # the version of Maya from which this module supports.
AUTHOR = "Etay Herz"  # name of person who created this module.
RIG_CATEGORY = "Cartoon"  # either 'Basic', 'Cartoon', 'Vfx', 'Game' or 'All'. (used when filtering).
RIG_TYPE = "Quadruped"  # Biped, Car, Quadruped, All, ... (for filtering modules in lists).
TAGS = ["cartoon", "complex", "advance", "ribbon", "bendy bones", "ik", "fk", "leg", "quadruped"]
TOOL_TIP = "Cartoon quadruped back leg with IK/FK, ribbons, twist, soft IK, stretch, pin ctrl and more."


class CA_Quadruped_Back_Leg(QuadrupedLeg):
    """Create a cartoon_complex quadruped back leg module. """
    AUTO_CLAVICLE_DEFAULT = False
    AUTO_CLAVICLE_NOTE = "Turned off by default for hind legs."
    GUIDES_POSITIONS = {
        "base": [5.52, 126, -35.6],
        "root": [14.5, 116, -51],
        "mid": [16.5, 75.9, -47],
        "tip": [13.6, 47.5, -64.2],
        "toes_root": [13.6, 14.0, -62.9],
        "heel": [13.6, 0, -64.7],
        "toes_tip": [13.6, 0, -51.2],
        "outer_tilt": [18.1, 0, -57.95],
        "inner_tilt": [9.1, 0, -57.95],
    }
    PV_GUIDE_OFFSET = (-2.5, 45)
    BASE_SKINNING_JNT = False
    JNTS_HUMAN_IK = {"tip_jnt": "*Foot", "toes_jnt": "*ToeBase"}
    UPPER_ROLL_TAGS = ("*UpLeg", "Leaf*UpLegRoll{0}")
    LOWER_ROLL_TAGS = ("*Leg", "Leaf*LegRoll{0}")
    CTRLS_HUMAN_IK = {"ik_tip_ctrl": "*Ankle", "ik_pv_ctrl": "*Knee"}
    WORLD_DIRECTION_FLIP_X = False
    BASE_CTRL_VIS_DEFAULT = 0
    AIM_UP_VECTOR = (0, 0, 1)
