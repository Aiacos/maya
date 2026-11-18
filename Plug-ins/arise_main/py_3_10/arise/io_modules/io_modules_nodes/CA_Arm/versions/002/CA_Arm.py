"""Cartoon_A_Arm module creates a cartoon_complex arm module. """

from arise.utils.subcomponents.limb_base import Limb

MAYA_VERSION = 2016  # the version of maya from which this module is supported.
AUTHOR = "Etay Herz"  # name of person who created this module.
RIG_CATEGORY = "Cartoon"  # either 'Basic', 'Cartoon', 'Vfx', 'Game' or 'All'. (used when filtering).
RIG_TYPE = "Biped"  # Biped, Car, Quadruped, All, ... (for filtering modules in lists).
TAGS = ["cartoon", "complex", "advance", "ribbon", "bendy bones", "ik", "fk", "arm"]
TOOL_TIP = "Cartoon arm without any fingers. Features include IK/FK, ribbons, twist, soft IK, stretch, etc."


class CA_Arm(Limb):
    """Cartoon_A_Arm module creates a cartoon_complex arm module. """
    BODY_PART = "arm"
    WORLD_ORIENT_DEFAULT = "+X"
    SWITCH_OFFSET_DEFAULT = [13, 0, 0]
    MIRROR_DEFAULT = True
    MIRROR_ANNOTATION = (
        "Only affects mirrored nodes.\n\n"
        "Unchecked - The IK ctrls of mirrored nodes will align with the world,\n"
        "meaning that both arms will move and rotate in the same direction (default for legs).\n\n"
        "Checked - The IK ctrls of mirrored nodes will mirror orientations,\n"
        "meaning that both arms will reflect each other behavior(default for arms)."
    )
    AUTO_CLAVICLE_DEFAULT = True
    AUTO_CLAVICLE_Z_LIMITS = (-180, 0)
    BEZIER_OFFSET_DEFAULT = [10, 0, 0]
    BEZIER_ANNOTATION = "Position offset of Bezier ctrls from the ribbons.\nmultiplied by attribute 'Ctrls Scale'."
    GUIDES = {
        "base": {"translation": [4.2, 137, 0], "rotation": [190, 0, 90]},
        "root": {"translation": [12.7, 140, 0]},
        "mid": {"translation": [40, 140, -10]},
        "tip": {"translation": [68, 140, 0], "rotation": [0, 180, -90]},
    }
    TIP_GUIDE_ROTATE_OFFSET = [0, 90, 0]
    BASE_SKINNING_JNT = True
    LIMB_JNT_RADIUS = 1
    BASE_HUMAN_IK = "*Shoulder"
    TIP_HUMAN_IK = "*Hand"
    UPPER_ROLL_TAGS = ("*Arm", "Leaf*ArmRoll{0}")
    LOWER_ROLL_TAGS = ("*ForeArm", "Leaf*ForeArmRoll{0}")
    BASE_CTRL = {"shape": "pin_sphere_2_way", "up_orient": "+Z", "size": 1.6}
    SECONDARY_CLEAN_ORIENT = "+X"
    BASE_HUMAN_IK_CTRL = "*Clavicle"
    TIP_HUMAN_IK_CTRL = "*Hand"
    PV_HUMAN_IK_CTRL = "*Elbow"
    WORLD_DIRECTION_FLIP_X = True
    BASE_CTRL_VIS_ATTR = False
    OUTPUT_TIP_GRP = "output_tip_grp"

    def _driver_attributes_creation(self):
        self.driver_tip_attr = self.add_driver_attribute(name="Tip Output", annotation="Output")

    def _set_driver_objects(self, output_tip_grp):
        self.driver_tip_attr.set_maya_object(output_tip_grp)
