"""Cartoon_A_Leg module creates a cartoon_complex leg module. """

import maya.cmds as mc

from arise.data_types import node_data
from arise.utils import math_utils
from arise.utils import matrix_utils
from arise.utils.modules_utils import (
    create_grps, movable_pivot_setup, create_bezier_ctrls, SECONDARY_COLOR, update_ctrls, ADD_DL, MULT_DL,
    MULT_DL_INPUT1, MULT_DL_INPUT2,
)
from arise.utils.io_nodes.io_transform import IoTransform
from arise.utils.subcomponents.complex_ribbon import ComplexRibbon
from arise.utils.subcomponents.ik_chain_three_joints import IkChainThreeJoints
from arise.utils.subcomponents.fk_chain_three_joints import FkChainThreeJoints
from arise.utils.subcomponents.ik_fk_switch import IkFkSwitch

MAYA_VERSION = 2016  # the version of Maya from which this module supports.
AUTHOR = "Etay Herz"  # name of person who created this module.
RIG_CATEGORY = "Cartoon"  # either 'Basic', 'Cartoon', 'Vfx', 'Game' or 'All'. (used when filtering).
RIG_TYPE = "Biped"  # Biped, Car, Quadruped, All, ... (for filtering modules in lists).
TAGS = ["cartoon", "complex", "advance", "ribbon", "bendy bones", "ik", "fk", "leg"]
TOOL_TIP = "Cartoon leg and foot. Features include IK/FK, soft IK, stretch, foot roll, tilt, etc."

SWITCH_ATTR_OPTIONS = ["switch_ctrl", "proxy attrs"]

node_data.NodeData.update_ctrls = update_ctrls


class CA_Leg(node_data.NodeData):
    """Cartoon_A_Leg module creates a cartoon_complex leg module. """
    sort_priority = 100

    def __init__(self, parent, docs, icon, module_dict):
        node_data.NodeData.__init__(
            self,
            parent=parent,
            icon=icon,
            docs=docs,
            module_dict=module_dict
        )

        self.body_part = "leg"

    def attributes_creation(self):
        """Here you add the module attributes. """
        self.add_collapsible_layout(title="Settings", shown=True)
        self.ctrls_scale_attr = self.add_float_attribute(
            name="Ctrls Scale",
            default_value=1.0,
            annotation=(
                "Scale all the node's ctrls.\n"
                "Note that the attachments 'CtrlsSettings' and 'CtrlsShape' will override this."
            ),
            min_value=0.01,
            max_value=100,
            button=[
                self.update_ctrls,
                "Update",
                "resources/icons/sync_icon.png",
                "If the ctrls exist in the Maya scene, their shapes will update without requiring a rebuild.",
            ],
            help_link="https://youtu.be/-1fpRw6oJME?t=31",
        )

        self.clean_transformations_attr = self.add_boolean_attribute(
            name="Clean Transformations",
            default_value=False,
            annotation=(
                "If checked, the zeroed pose will be the same as the bind pose;\n"
                "if unchecked, when zeroing the ctrls, they will align with a world axis "
                "specified in the following two attributes."
            ),
            help_link="https://youtu.be/-1fpRw6oJME?t=61",
        )

        self.add_collapsible_layout(title="World Orientation", shown=False)
        items = ["+X", "+Y", "+Z", "-X", "-Y", "-Z"]
        self.world_orientation_attr = self.add_radio_attribute(
            name="World Orientation",
            items=items,
            default_value=items.index("-Y"),  # Leg points down.
            annotation=(
                "The world axis the ctrls will align with when zeroed.\n"
                "Usually, this attribute's default value is the correct value."
            ),
            help_link="https://youtu.be/-1fpRw6oJME?t=61",
        )
        self.world_twist_attr = self.add_float_attribute(
            name="World Orient Twist",
            min_value=-360,
            max_value=360,
            annotation=(
                "Along with 'world Orientation', defines the ctrls zeroed pose.\n"
                "Usually, the default value of 0 is the correct value."
            ),
            help_link="https://youtu.be/-1fpRw6oJME?t=61",
        )
        self.close_layout()

        self.expose_rotation_order_attr = self.add_boolean_attribute(
            name="Expose RotateOrder",
            default_value=True,
            annotation="Exposes all the ctrls 'RotateOrder' attribute in the Channel Box.",
            help_link="https://youtu.be/-1fpRw6oJME?t=149",
        )
        self.secondary_ctrl_attr = self.add_boolean_attribute(
            name="Secondary Ctrls",
            default_value=True,
            annotation="Secondary ctrls are added under some ctrls to help prevent gimbal lock.",
            help_link="https://youtu.be/-1fpRw6oJME?t=157",
        )

        self.add_separator()
        self.switch_ctrl_attr = self.add_radio_attribute(
            name="Ik Fk Switch",
            items=SWITCH_ATTR_OPTIONS,
            default_value=0,
            annotation=(
                "Select where the 'Ik Fk Switch' attribute and other shared attributes are placed:\n"
                "'switch_ctrl' - Places them on a ctrl that follows the leg tip (default).\n"
                "'proxy_attrs' - places them as shared attributes (proxy attributes), "
                "on both the IK tip ctrl and the FK tip ctrl."
            ),
            help_link="https://youtu.be/-1fpRw6oJME?t=171",
        )

        self.switch_offset_attr = self.add_xyz_attribute(
            name="Switch Ctrl Offset",
            default_value=[-13, 0, 0],
            dynamic_attribute=False,
            writable=True,
            readable=True,
            promoted=False,
            annotation="Position offset of 'switch_ctrl' from 'tip_jnt'.\nmultiplied by attribute 'Ctrls Scale'.",
        )

        self.volume_attr = self.add_boolean_attribute(
            name="Volume",
            default_value=True,
            annotation="Add 'Auto Volume' and 'Manual Volume' attributes.",
        )

        self.pin_ctrl_attr = self.add_boolean_attribute(
            name="Pin Ctrl",
            default_value=False,
            annotation=(
                "Add a 'pin_ctrl' that constrains 'mid_ctrl' when activated.\n"
                "To activate this ctrl use the 'Pin' attribute on 'mid_ctrl'.\n"
                "Use a 'SpaceSwitch' attachment for 'pin_ctrl' to properly use this feature."
            ),
        )

        ### IK chain settings.
        self.add_collapsible_layout(title="IK Chain Settings", shown=True)
        self.mirror_behaviour_attr = self.add_boolean_attribute(
            name="Mirror Behaviour",
            default_value=False,
            annotation=(
                "Only affects mirrored nodes.\n\n"
                "Unchecked - The IK ctrls of mirrored nodes will align with the world,\n"
                "meaning that both legs will move and rotate in the same direction (default for legs).\n\n"
                "Checked - The IK ctrls of mirrored nodes will mirror orientations,\n"
                "meaning that both legs will reflect each other (default for arms)."
            ),
        )

        self.add_twist_attr = self.add_boolean_attribute(
            name="IK Twist",
            default_value=True,
            annotation="Add attribute 'Twist' to 'ik_tip_ctrl', giving another control over the IK chain twist.",
        )
        self.add_stretch_attr = self.add_boolean_attribute(
            name="Stretch",
            default_value=True,
            annotation="Add attributes 'Auto Stretch' and 'Manual Stretch' to 'ik_tip_ctrl'.",
        )
        self.add_toggle_pv_attr = self.add_boolean_attribute(
            name="Toggle Pole Vector",
            default_value=True,
            annotation="Add attribute 'Toggle Pole Vector' to 'ik_tip_ctrl' for turning off PV constraint.",
        )
        self.add_soft_ik_attr = self.add_boolean_attribute(
            name="Soft IK",
            default_value=True,
            annotation="Add attr 'Soft Ik' which helps fix 'pop' in animation when IK chain is fully extended.",
        )
        self.auto_clavicle_attr = self.add_boolean_attribute(
            name="Auto Clavicle",
            default_value=False,
            annotation=(
                "Enables automatic rotation of 'base_jnt' based on 'ik_tip_ctrl' movement.\n"
                "Add attributes 'Auto Clavicle X Mult' and 'Auto Clavicle Z Mult' to the 'ik_tip_ctrl'.\n"
                "Turned off by default for legs."
            )
        )
        self.close_layout()

        ### FK chain settings.
        self.add_collapsible_layout(title="FK Chain Settings", shown=True)
        self.fk_translate_ctrls_attr = self.add_boolean_attribute(
            name="Ctrls Translate",
            default_value=False,
            annotation="If checked, animators will also be able to translate the FK ctrls.",
        )
        self.close_layout()

        ### ribbons settings.
        self.add_collapsible_layout(title="Ribbons Settings", shown=True)
        self.ribbon_joints_attr = self.add_integer_attribute(
            name="Ribbon Joints",
            default_value=5,
            dynamic_attribute=False,
            writable=True,
            readable=True,
            promoted=False,
            annotation="How many skinning joints each ribbon will have (total x2; upper ribbon and lower ribbon).",
            help_link="https://youtu.be/-1fpRw6oJME?t=198",
            min_value=2,
            max_value=20,
            add_slider=True,
        )

        self.ribbon_twist_attr = self.add_boolean_attribute(
            name="Ribbon Twist",
            default_value=True,
            annotation=(
                "Allows the ribbon joints to twist.\n"
                "Turn this off for creatures with external skeletons, such as spiders, "
                "or for characters wearing rigid armor."
            ),
        )

        self.ribbon_ctrls_attr = self.add_boolean_attribute(
            name="Ribbon Micro Ctrls",
            default_value=False,
            annotation="Add a ctrl for every ribbon skinning joint.",
            help_link="https://youtu.be/-1fpRw6oJME?t=211",
        )

        self.ribbon_bezier_attr = self.add_boolean_attribute(
            name="Bezier Ctrls",
            default_value=True,
            annotation="Add ctrls that deform the ribbons like a Bezier curve.",
            help_link="https://youtu.be/-1fpRw6oJME?t=222",
        )

        self.bezier_offset_attr = self.add_xyz_attribute(
            name="Bezier Ctrls Offset",
            default_value=[-10, 0, 0],
            dynamic_attribute=False,
            writable=True,
            readable=True,
            promoted=False,
            annotation="Position offset of bezier ctrls from the ribbons.\nmultiplied by attribute 'Ctrls Scale'.",
        )

        self.roundness_attr = self.add_boolean_attribute(
            name="Roundness",
            default_value=False,
            annotation=(
                "A cartoon feature of rounding the limb shape.\n"
                "Attribute 'Roundness' is added to the 'switch_ctrl'."
            ),
        )
        self.close_layout()

        ### connections.
        self.add_separator(title="Connections")
        self.driven_roots_attr = self.add_driven_attribute(name="Root Input", annotation="Input")
        self.driven_ik_tip_attr = self.add_driven_attribute(name="IK Tip Input", annotation="Input")
        self.driver_root_attr = self.add_driver_attribute(name="Root Output", annotation="Output")
        self.driver_ankle_attr = self.add_driver_attribute(name="Ankle Output", annotation="Output")
        self.driver_toes_start_attr = self.add_driver_attribute(name="Toes Start Output", annotation="Output")
        self.driver_toes_tip_attr = self.add_driver_attribute(name="Toes Tip Output", annotation="Output")

        self.close_layout()

    def evaluate_creation_methods(self):  # REIMPLEMENTED!
        """Reimplemented to enable/disable attrs. """
        self.world_orientation_attr.set_disabled(True if self.clean_transformations_attr.value else False)
        self.world_twist_attr.set_disabled(True if self.clean_transformations_attr.value else False)
        self.switch_offset_attr.set_disabled(True if self.switch_ctrl_attr.value != 0 else False)
        self.bezier_offset_attr.set_disabled(False if self.ribbon_bezier_attr.value else True)

        node_data.NodeData.evaluate_creation_methods(self)

    def guides_creation(self):
        """Create guides based on attributes values. """
        self.base_guide = self.add_guide(name="base", translation=[9.5, 108.5, 1], rotation=[0, 0, 180])
        self.base_guide.size = self.base_guide.size * 1.5
        self.base_guide.shape = "pin_sphere_2_way"
        self.base_guide.up_orient = "+Z"

        self.root_guide = self.add_aim_guide(name="root", translation=[12.0, 99, 0.5], parent=self.base_guide)
        self.mid_guide = self.add_aim_guide(name="mid", translation=[12.0, 55, 8.7], parent=self.base_guide)
        self.mid_guide.visual_parent = self.root_guide

        self.tip_guide = self.add_guide(
            name="tip",
            translation=[12.0, 13, -3.0],
            rotation=[0, 0, 180],
            parent=self.base_guide,
        )
        self.tip_guide.shape = ["square_with_arrow", "arrow"]
        self.tip_guide.scale_offset = (1.5, 0.8, 1.5)
        self.tip_guide.visual_parent = self.mid_guide

        self.guides_list = [self.base_guide, self.root_guide, self.mid_guide, self.tip_guide]

        # aim guides at each other.
        for index, guide in enumerate(self.guides_list[:-1]):
            guide.aim_at = self.guides_list[index+1]

        # pole vector.
        self.ik_pv_guide = self.add_pole_vector_guide(
            name="pole_vector",
            guide_start=self.root_guide,
            guide_mid=self.mid_guide,
            guide_end=self.tip_guide,
            offset=(-2.5, 25),
        )

        self.mid_guide.aim_side_pin = [self.tip_guide, self.ik_pv_guide]
        self.root_guide.aim_side_pin = [self.tip_guide, self.ik_pv_guide]

        # foot guides.
        self.heel_guide = self.add_guide(
            name="heel",
            translation=[12, 0, -8.3],
            rotation=[90, 0, 180],
            parent=self.tip_guide,
        )
        self.heel_guide.shape = "sphere"
        self.heel_guide.size = self.heel_guide.size / 2.0

        self.toes_guide = self.add_guide(
            name="toes_root",
            translation=[12, 2.8, 6],
            rotation=[90, 0, 180],
            parent=self.tip_guide,
        )

        self.toes_tip_guide = self.add_guide(
            name="toes_tip",
            translation=[12, 2.8, 13],
            rotation=[90, 0, 180],
            parent=self.toes_guide,
        )
        self.toes_tip_guide.shape = "sphere"
        self.toes_tip_guide.size = self.toes_tip_guide.size / 2.0

        self.outer_tilt_guide = self.add_guide(
            name="outer_tilt",
            translation=[18, 0, 0],
            rotation=[90, 0, 180],
            parent=self.tip_guide,
        )
        self.outer_tilt_guide.shape = "sphere"
        self.outer_tilt_guide.size = self.outer_tilt_guide.size / 2.0

        self.inner_tilt_guide = self.add_guide(
            name="inner_tilt",
            translation=[6, 0, 0],
            rotation=[90, 0, 180],
            parent=self.tip_guide,
        )
        self.inner_tilt_guide.shape = "sphere"
        self.inner_tilt_guide.size = self.inner_tilt_guide.size / 2.0

    def joints_creation(self):
        """Create joints based on attributes values and guides. (without positioning as this point). """
        # driven joints.
        self.base_jnt = self.add_joint(name="base", skinning_jnt=False, tag_parent_jnt=None, radius=1)
        self.root_jnt = self.add_joint(name="root", skinning_jnt=False, tag_parent_jnt=self.base_jnt, radius=0.5)
        self.mid_jnt = self.add_joint(name="mid", skinning_jnt=False, radius=0.5)

        # IK joints.
        self.ik_root_jnt = self.add_joint(name="ik_root", skinning_jnt=False, radius=0.7)
        self.ik_mid_jnt = self.add_joint(name="ik_mid", skinning_jnt=False, radius=0.7)
        self.ik_tip_jnt = self.add_joint(name="ik_tip", skinning_jnt=False, radius=0.7)

        # FK joints.
        self.fk_root_jnt = self.add_joint(name="fk_root", skinning_jnt=False, radius=0.75)
        self.fk_mid_jnt = self.add_joint(name="fk_mid", skinning_jnt=False, radius=0.75)
        self.fk_tip_jnt = self.add_joint(name="fk_tip", skinning_jnt=False, radius=0.75)

        # ribbons driver joints.
        self.ribbon_upper_driver_jnts = [
            self.add_joint(name="upper_ribbon_driver_01", skinning_jnt=False, tag_parent_jnt=None, radius=0.5),
            self.add_joint(name="upper_ribbon_driver_02", skinning_jnt=False, tag_parent_jnt=None, radius=0.5),
            self.add_joint(name="upper_ribbon_driver_03", skinning_jnt=False, tag_parent_jnt=None, radius=0.5),
        ]

        self.ribbon_lower_driver_jnts = [
            self.add_joint(name="lower_ribbon_driver_01", skinning_jnt=False, tag_parent_jnt=None, radius=0.5),
            self.add_joint(name="lower_ribbon_driver_02", skinning_jnt=False, tag_parent_jnt=None, radius=0.5),
            self.add_joint(name="lower_ribbon_driver_03", skinning_jnt=False, tag_parent_jnt=None, radius=0.5),
        ]

        # upper ribbon driven jnts.
        parent_upper = self.base_jnt
        self.ribbon_upper_driven_jnts = []
        for index in range(self.ribbon_joints_attr.value):
            name = "upper_ribbon_driven_{0}".format(index)
            up_ribbon_jnt = self.add_joint(name=name, skinning_jnt=True, tag_parent_jnt=parent_upper, radius=0.25)
            parent_upper = up_ribbon_jnt
            self.ribbon_upper_driven_jnts.append(up_ribbon_jnt)

        # lower ribbon driven jnts.
        parent_lower = self.ribbon_upper_driven_jnts[-1]
        self.ribbon_lower_driven_jnts = []
        for index in range(self.ribbon_joints_attr.value):
            name = "lower_ribbon_driven_{0}".format(index)
            low_ribbon_jnt = self.add_joint(name=name, skinning_jnt=True, tag_parent_jnt=parent_lower, radius=0.25)
            parent_lower = low_ribbon_jnt
            self.ribbon_lower_driven_jnts.append(low_ribbon_jnt)

        self.tip_jnt = self.add_joint(name="tip", skinning_jnt=True, radius=0.5)
        self.tip_jnt.parent_tag = self.ribbon_lower_driven_jnts[-1]

        self.toes_jnt = self.add_joint(
            name="toes_root", skinning_jnt=True, tag_parent_jnt=self.tip_jnt, radius=0.5
        )
        self.toes_tip_jnt = self.add_joint(
            name="toes_tip", skinning_jnt=False, tag_parent_jnt=self.toes_jnt, radius=0.25,
        )

        # humanIK definition.
        self.tip_jnt.human_ik = "*Foot"
        self.toes_jnt.human_ik = "*ToeBase"

        arm_roll_tags = ["*UpLeg"] + ["Leaf*UpLegRoll{0}".format(index) for index in range(1, 6)]
        for jnt, tag in zip(self.ribbon_upper_driven_jnts, arm_roll_tags):
            jnt.human_ik = tag

        forearm_roll_tags = ["*Leg"] + ["Leaf*LegRoll{0}".format(index) for index in range(1, 6)]
        for jnt, tag in zip(self.ribbon_lower_driven_jnts, forearm_roll_tags):
            jnt.human_ik = tag

    def ctrls_creation(self):
        """Create controls based on attributes values, guides and joints. (without positioning as this point). """
        scale_mult = self.ctrls_scale_attr.value * 3.5

        self.base_ctrl = self.add_ctrl(
            name="base", shape="pin_sphere", up_orient="-X", size=(0.95 * scale_mult),
        )
        self.base_ctrl.add_locked_hidden_attr("scaleY")
        self.base_ctrl.add_locked_hidden_attr("scaleZ")

        ## ik_fk_switch ctrls.
        self.switch_ctrl = None  # proxy_attrs.
        if self.switch_ctrl_attr.display_value == SWITCH_ATTR_OPTIONS[0]:  # switch_ctrl.
            self.switch_ctrl = self.add_ctrl(
                name="ik_fk_switch", shape="cross", up_orient="-Z", size=(0.8 * scale_mult))

            for attr in ["translate", "rotate", "scale"]:
                for axis in "XYZ":
                    self.switch_ctrl.add_hidden_attr("{0}{1}".format(attr, axis))

        ## IK ctrls.
        self.ik_tip_ctrl = self.add_ctrl(name="ik_tip", shape="box", up_orient="+Y", size=(1.6 * scale_mult))
        self.ik_tip_ctrl.add_locked_hidden_attr("scaleY")
        self.ik_tip_ctrl.add_locked_hidden_attr("scaleZ")

        self.ik_pv_ctrl = self.add_ctrl(name="ik_pv", shape="locator", up_orient="+Y", size=(1.2 * scale_mult))
        self.ik_pv_ctrl.line_width = 1.5

        ## FK ctrls.
        self.fk_three_ctrls = [
            self.add_ctrl(name="fk_root", shape="square", up_orient="+Y", size=(1.5 * scale_mult)),
            self.add_ctrl(name="fk_mid", shape="square", up_orient="+Y", size=(1.5 * scale_mult)),
            self.add_ctrl(name="fk_tip", shape="square", up_orient="+Y", size=(1.5 * scale_mult)),
        ]

        attrs = ["scaleY", "scaleZ"]
        if self.fk_translate_ctrls_attr.value is False:
            attrs = ["translateX", "translateY", "translateZ", "scaleY", "scaleZ"]

        for fk_ctrl in self.fk_three_ctrls:
            for attr in attrs:
                fk_ctrl.add_locked_hidden_attr(attr)

        ## secondary ctrls.
        self.ik_secondary_ctrl = None
        self.fk_secondary_ctrls = None
        if self.secondary_ctrl_attr.value:

            orient = "-Y" if self.clean_transformations_attr.value else self.world_orientation_attr.display_value
            self.ik_secondary_ctrl = self.add_ctrl(
                name="ik_tip_secondary",
                up_orient=orient,
                size=1.6 * scale_mult,
            )
            self.ik_secondary_ctrl.color = SECONDARY_COLOR

            for attr in ["scaleX", "scaleY", "scaleZ"]:
                self.ik_secondary_ctrl.add_locked_hidden_attr(attr)

            self.fk_secondary_ctrls = [
                self.add_ctrl(name="fk_root_secondary", shape="circle", size=(1.4 * scale_mult)),
                self.add_ctrl(name="fk_mid_secondary", shape="circle", size=(1.4 * scale_mult)),
                self.add_ctrl(name="fk_tip_secondary", shape="circle", size=(1.4 * scale_mult)),
            ]

            for fk_secondary_ctrl in self.fk_secondary_ctrls:
                fk_secondary_ctrl.color = SECONDARY_COLOR

                for attr in ["scaleX", "scaleY", "scaleZ"]:
                    fk_secondary_ctrl.add_locked_hidden_attr(attr)

        # pin ctrl.
        self.pin_ctrl = None
        if self.pin_ctrl_attr.value:
            self.pin_ctrl = self.add_ctrl(name="pin", shape="box", size=(1.35 * scale_mult))
            self.pin_ctrl.line_width = 2

            for attr in ["scaleX", "scaleY", "scaleZ"]:
                self.pin_ctrl.add_locked_hidden_attr(attr)

        ## ribbon ctrls.
        self.ribbons_mid_ctrl = self.add_ctrl(name="mid", shape="circle_with_arrow", size=(2.2 * scale_mult))
        self.ribbons_mid_ctrl.line_width = 1.5

        self.ribbon_upper_mid_ctrl = self.add_ctrl(name="upper_ribbon_mid", up_orient="+Y", size=(1.4*scale_mult))
        self.ribbon_upper_mid_ctrl.shape = "circle_crosshair"
        self.ribbon_upper_mid_ctrl.line_width = 1.5

        self.ribbon_lower_mid_ctrl = self.add_ctrl(name="lower_ribbon_mid", up_orient="+Y", size=(1.4*scale_mult))
        self.ribbon_lower_mid_ctrl.shape = "circle_crosshair"
        self.ribbon_lower_mid_ctrl.line_width = 1.5

        for mid_ctrl in [self.ribbon_upper_mid_ctrl, self.ribbon_lower_mid_ctrl]:
            mid_ctrl.add_locked_hidden_attr("scaleY")
            mid_ctrl.add_locked_hidden_attr("scaleZ")

        # foot ctrls.
        self.toes_ctrl = self.add_ctrl(name="toes", shape="circle", size=(1.3 * scale_mult))
        for attr in ["translateX", "translateY", "translateZ", "scaleY", "scaleZ"]:
            self.toes_ctrl.add_locked_hidden_attr(attr)

        self.master_ctrl = self.add_ctrl(name="ik_master", up_orient="+Z", size=(0.5 * scale_mult))
        self.master_ctrl.shape = "arrow_rotation_4_way"
        self.master_ctrl.translate_offset = (0, 0, 1.5 * scale_mult)


        for attr in ["translateX", "translateY", "translateZ", "rotateZ", "scaleX", "scaleY", "scaleZ"]:
            self.master_ctrl.add_locked_hidden_attr(attr)

        self.ik_toes_ball_ctrl = self.add_ctrl(
            name="ik_toes_ball",
            up_orient="+Z",
            shape="strap",
            size=1.0 * scale_mult,
        )
        self.ik_toes_ball_ctrl.translate_offset = (0, 0, 1.0 * scale_mult)

        self.ik_heel_ctrl = self.add_ctrl(name="ik_heel", up_orient="+Y", shape="box", size=(0.3 * scale_mult))
        self.ik_toes_tip_ctrl = self.add_ctrl(name="ik_toes_tip", shape="box", size=(0.3 * scale_mult))

        for ctrl in [self.ik_toes_ball_ctrl, self.ik_heel_ctrl, self.ik_toes_tip_ctrl]:
            for attr in ["translateX", "translateY", "translateZ", "scaleX", "scaleY", "scaleZ"]:
                ctrl.add_locked_hidden_attr(attr)

        self.upper_ribbon_ctrls = []
        self.lower_ribbon_ctrls = []
        if self.ribbon_ctrls_attr.value:
            for index in range(self.ribbon_joints_attr.value):
                ctrl = self.add_ctrl(
                    name="upper_ribbon_micro_{0}".format(index), size=(1.05 * scale_mult), shape="octagon",
                )
                self.upper_ribbon_ctrls.append(ctrl)

            for index in range(self.ribbon_joints_attr.value):  # different loop to keep ctrls order organized.
                ctrl = self.add_ctrl(
                    name="lower_ribbon_micro_{0}".format(index), size=(1.05 * scale_mult), shape="octagon",
                )
                self.lower_ribbon_ctrls.append(ctrl)

        self.upper_bezier_ctrls = []
        self.lower_bezier_ctrls = []
        if self.ribbon_bezier_attr.value is True:
            self.upper_bezier_ctrls = create_bezier_ctrls(
                class_=self,
                scale_mult=scale_mult,
                name="upper_ribbon_bezier",
                driver_jnts_count=len(self.ribbon_upper_driver_jnts),
            )

            self.lower_bezier_ctrls = create_bezier_ctrls(
                class_=self,
                scale_mult=scale_mult,
                name="lower_ribbon_bezier",
                driver_jnts_count=len(self.ribbon_lower_driver_jnts),
            )

        # HumanIK definition ctrls.
        self.ik_tip_ctrl.human_ik = "*Ankle"
        self.ik_pv_ctrl.human_ik = "*Knee"

    def maya_attrs_creation(self):
        """Declare any Maya attributes that users should be able to modify. """
        parent = self.switch_ctrl if self.switch_ctrl else self.ik_tip_ctrl
        parent.add_maya_attr(name="ik_fk_switch", attr_type="float", default_value=0, min=0, max=1)

        if self.switch_ctrl:
            self.switch_ctrl.add_maya_attr(
                name="show_ik_ctrls", attr_type="enum", default_value=1, enum_names=["Off", "Auto", "On"],
            )
            self.switch_ctrl.add_maya_attr(
                name="show_fk_ctrls", attr_type="enum", default_value=1, enum_names=["Off", "Auto", "On"],
            )

        parent.add_maya_attr(name="base_ctrl", attr_type="bool", default_value=False)
        parent.add_maya_attr(name="mid_ctrl", attr_type="bool", default_value=False)
        parent.add_maya_attr(name="bendy_bones_ctrls", attr_type="bool", default_value=False)

        if self.ribbon_ctrls_attr.value:
            parent.add_maya_attr(name="ribbon_micro_ctrls", attr_type="bool", default_value=False)

        if self.ribbon_bezier_attr.value:
            parent.add_maya_attr(name="bezier_ctrls", attr_type="bool", default_value=False)

        if self.volume_attr.value:
            parent.add_maya_attr(name="auto_volume", attr_type="float", default_value=0, min=0, max=1)
            parent.add_maya_attr(name="gradual_volume", attr_type="float", default_value=1, min=0, max=1)
            parent.add_maya_attr(name="gradual_intensity", attr_type="float", default_value=0, min=-10, max=10)
            parent.add_maya_attr(name="gradual_spread", attr_type="float", default_value=0, min=-10, max=10)

        if self.roundness_attr.value:
            parent.add_maya_attr(name="roundness", attr_type="float", default_value=0, min=0, max=1)

        if self.add_stretch_attr.value:
            self.ik_tip_ctrl.add_maya_attr(name="auto_stretch", attr_type="float", default_value=0, min=0, max=1)

        if self.add_toggle_pv_attr.value:
            self.ik_tip_ctrl.add_maya_attr(name="toggle_pole_vector", attr_type="bool", default_value=True)

        if self.auto_clavicle_attr.value:
            self.ik_tip_ctrl.add_maya_attr(
                name="auto_clavicle_x_mult", attr_type="float", default_value=0, min=0, max=1,
            )
            self.ik_tip_ctrl.add_maya_attr(
                name="auto_clavicle_z_mult", attr_type="float", default_value=0, min=0, max=1,
            )

        self.master_ctrl.add_maya_attr(name="foot_roll_angle", attr_type="float", default_value=30, min=0, max=180)
        self.master_ctrl.add_maya_attr(name="tilt_pivots", attr_type="bool", default_value=False)

    def rig_creation(self):
        """Based on attributes value, guides (which now you can get global position from) joints and controls
        created in their methods you can build the rig.
        """
        ctrls_scale = self.ctrls_scale_attr.value

        if self.is_mirrored:
            self.module_grp.set_attr("scaleX", -1)

        grps = create_grps(self, ["input_root_grp", "input_ik_tip_grp", "output_root_grp", "output_ankle_grp"])
        input_root_grp, input_ik_tip_grp, output_root_grp, output_ankle_grp = grps
        toes_start_output, toes_tip_output = create_grps(self, ["output_toes_start_grp", "output_toes_tip_grp"])

        self.driven_roots_attr.set_maya_object(input_root_grp)
        self.driven_ik_tip_attr.set_maya_object(input_ik_tip_grp)
        self.driver_root_attr.set_maya_object(output_root_grp)
        self.driver_ankle_attr.set_maya_object(output_ankle_grp)
        self.driver_toes_start_attr.set_maya_object(toes_start_output)
        self.driver_toes_tip_attr.set_maya_object(toes_tip_output)

        ### position main/IK/FK chains.
        self.base_jnt.pointer.set_matrix(self.base_guide.world_transformations["matrix"], space="world")
        self.base_jnt.pointer.freeze_transformations()
        self.base_jnt.pointer.add_joint_orient()

        for jnt_info in [self.root_jnt, self.ik_root_jnt, self.fk_root_jnt]:
            jnt_info.pointer.set_matrix(self.root_guide.world_transformations["matrix"], space="world")
            jnt_info.pointer.freeze_transformations()
            jnt_info.pointer.add_joint_orient()

        for jnt_info in [self.mid_jnt, self.ik_mid_jnt, self.fk_mid_jnt]:
            jnt_info.pointer.set_matrix(self.mid_guide.world_transformations["matrix"], space="world")
            jnt_info.pointer.freeze_transformations()
            jnt_info.pointer.add_joint_orient()

        for jnt_info in [self.tip_jnt, self.ik_tip_jnt, self.fk_tip_jnt]:
            jnt_info.pointer.set_matrix(self.tip_guide.world_transformations["matrix"], space="world")
            jnt_info.pointer.freeze_transformations()
            jnt_info.pointer.add_joint_orient()

        self.ik_pv_ctrl.pointer.offset_grp.set_translation(self.ik_pv_guide.world_transformations["translate"])

        ### create IK chain setup.
        ik_chain_obj = IkChainThreeJoints(
            parent_to=self.module_grp,
            three_joints=[self.ik_root_jnt.pointer, self.ik_mid_jnt.pointer, self.ik_tip_jnt.pointer],
            ik_tip_ctrl=self.ik_tip_ctrl.pointer,
            mirror_behaviour=self.mirror_behaviour_attr.value,
            pole_vector_ctrl=self.ik_pv_ctrl.pointer,
            name_prefix="{0}_ik".format(self.name),
            world_direction=self.world_orientation_attr.display_value,
            world_twist=self.world_twist_attr.value,
            world_direction_flip_x=False,
            clean_transformations=self.clean_transformations_attr.value,
            secondary_tip_ctrl=self.ik_secondary_ctrl.pointer if self.ik_secondary_ctrl else None,
            rotation_order=0,  # xyz.
        )

        ## IK features.
        if self.add_twist_attr.value:
            ik_chain_obj.twist_setup()

        if self.add_stretch_attr.value:
            ik_chain_obj.auto_and_manual_stretch_setup()

        if self.add_soft_ik_attr.value:
            ik_chain_obj.soft_ik_setup()

        if self.add_toggle_pv_attr.value:
            ik_chain_obj.pole_vector_toggle_setup()

        # create FK chain setup.
        secondary_ctrls = [ctrl.pointer for ctrl in self.fk_secondary_ctrls] if self.fk_secondary_ctrls else None
        fk_chain_obj = FkChainThreeJoints(
            parent_to=self.module_grp,
            three_joints=[self.fk_root_jnt.pointer, self.fk_mid_jnt.pointer, self.fk_tip_jnt.pointer],
            three_ctrls=[ctrl.pointer for ctrl in self.fk_three_ctrls],
            name_prefix="{0}_fk".format(self.name),
            world_direction=self.world_orientation_attr.display_value,
            world_twist=self.world_twist_attr.value,
            world_direction_flip_x=False,
            clean_transformations=self.clean_transformations_attr.value,
            three_secondary_ctrls=secondary_ctrls,
            rotation_order=0,  # xyz.
        )
        ## FK features.
        if self.fk_translate_ctrls_attr.value:
            fk_chain_obj.aim_jnts_at_next_ctrl()

        ### create a IK FK switch setup that connects the 2 chains.
        ik_fk_switch_obj = IkFkSwitch(
            parent_to=self.module_grp,
            three_joints=[self.root_jnt.pointer, self.mid_jnt.pointer, self.tip_jnt.pointer],
            base_jnt=self.base_jnt.pointer,
            base_ctrl=self.base_ctrl.pointer,
            ik_subcomponent_ptr=ik_chain_obj,
            fk_sbcomponent_ptr=fk_chain_obj,
            input_root_grp=input_root_grp,
            input_ik_tip_grp=input_ik_tip_grp,
            output_root_grp=output_root_grp,
            output_tip_grp=output_ankle_grp,
            name_prefix="{0}_ik_fk_switch".format(self.name),
            switch_ctrl=self.switch_ctrl.pointer if self.switch_ctrl else None,
            switch_offset=[value * ctrls_scale for value in self.switch_offset_attr.value],
            rotation_order=0,  # xyz.
        )

        # create ribbons setup.
        upper_ribbon_length = math_utils.distance_between(
            self.guides_list[1].world_transformations["translate"],
            self.guides_list[2].world_transformations["translate"],
        )
        upper_ribbon = ComplexRibbon(
            driver_joints=[jnt.pointer for jnt in self.ribbon_upper_driver_jnts],
            driven_joints=[jnt.pointer for jnt in self.ribbon_upper_driven_jnts[1:]],
            rest_length=upper_ribbon_length,
            name_prefix="{0}_upper_ribbon".format(self.name),
            parent_to=self.module_grp,
            is_mirrored=self.is_mirrored,
            driven_root=self.ribbon_upper_driven_jnts[0].pointer,
        )

        lower_ribbon_length = math_utils.distance_between(
            self.guides_list[2].world_transformations["translate"],
            self.guides_list[3].world_transformations["translate"],
        )
        lower_ribbon = ComplexRibbon(
            driver_joints=[jnt.pointer for jnt in self.ribbon_lower_driver_jnts],
            driven_joints=[jnt.pointer for jnt in self.ribbon_lower_driven_jnts[1:]],
            rest_length=lower_ribbon_length,
            name_prefix="{0}_lower_ribbon".format(self.name),
            parent_to=self.module_grp,
            is_mirrored=self.is_mirrored,
            driven_root=self.ribbon_lower_driven_jnts[0].pointer,
        )

        ## ribbon features.
        # create attrs on switch ctrl/s.
        ik_fk_switch_obj.create_spacer_on_switch()
        base_vis_attr = ik_fk_switch_obj.create_attr_on_switch("base_ctrl", at="bool", k=True, dv=0)
        mid_vis_attr = ik_fk_switch_obj.create_attr_on_switch("mid_ctrl", at="bool", k=True, dv=0)
        bendy_bones_attr = ik_fk_switch_obj.create_attr_on_switch("bendy_bones_ctrls", at="bool", k=True, dv=0)

        for shape in self.base_ctrl.pointer.get_shapes():
            mc.connectAttr(base_vis_attr, "{0}.visibility".format(shape))

        if self.ribbon_ctrls_attr.value is True:
            attr_name = "ribbon_micro_ctrls"
            ribbon_ctrls_vis_attr = ik_fk_switch_obj.create_attr_on_switch(attr_name, at="bool", k=True, dv=0)

        if self.ribbon_bezier_attr.value is True:
            bezier_attr = ik_fk_switch_obj.create_attr_on_switch("bezier_ctrls", at="bool", k=True, dv=0)

        # volume setup.
        if self.volume_attr.value:
            vol_attrs = upper_ribbon.auto_manual_volume_setup(
                attrs_node=ik_fk_switch_obj,
                module_scale_attr=ik_fk_switch_obj.module_scale_attr,
                count=len(upper_ribbon.driven_joints) + 1,  # +1 for the root jnt.
            )

            upper_joints = [upper_ribbon.driven_root] + upper_ribbon.driven_joints
            lower_joints = [lower_ribbon.driven_root] + lower_ribbon.driven_joints
            for joints in [upper_joints, lower_joints[::-1]]:
                for vol_attr, jnt in zip(vol_attrs, joints):
                    jnt.volume_grp = jnt.add_group_above(name="{0}_volume_grp".format(jnt.short_name))
                    jnt.volume_grp.connect_attr("scaleX", vol_attr)
                    jnt.volume_grp.connect_attr("scaleZ", vol_attr)

        # bezier setup.
        if self.ribbon_bezier_attr.value is True:
            bezier_ctrls = [self.upper_bezier_ctrls, self.lower_bezier_ctrls]
            for ribbon, bezier in zip([upper_ribbon, lower_ribbon], bezier_ctrls):
                bezier_ctrls_list = []
                for info_lists in bezier:
                    ctrls = []
                    for info in info_lists:
                        ctrls.append(info.pointer)

                    bezier_ctrls_list.append(ctrls)

                ribbon.bezier_setup(
                    bezier_ctrls=bezier_ctrls_list,
                    ctrls_offset=[value * ctrls_scale for value in self.bezier_offset_attr.value],
                    vis_attr=bezier_attr,
                )

        ## connect ribbons to ik_fk_setup.
        ik_fk_switch_obj.connect_ribbons(
            upper_ribbon=upper_ribbon,
            lower_ribbon=lower_ribbon,
            mid_ctrl=self.ribbons_mid_ctrl.pointer,
            mid_ctrl_vis_attr=mid_vis_attr,
            pin_ctrl=self.pin_ctrl.pointer if self.pin_ctrl else None,
        )

        if self.ribbon_twist_attr.value is True:
            ik_fk_switch_obj.stable_twist_setup()

        ## more ribbon features.
        upper_ribbon.aim_root_driver_jnts(object_orient=ik_fk_switch_obj.root_jnt)
        upper_ribbon.aim_tip_driver_jnts(object_orient=ik_fk_switch_obj.root_jnt)
        lower_ribbon.aim_root_driver_jnts(object_orient=ik_fk_switch_obj.mid_jnt)
        lower_ribbon.aim_tip_driver_jnts(object_orient=ik_fk_switch_obj.mid_jnt)

        upper_ribbon.connect_mid_driver_ctrl(
            driver_jnt=self.ribbon_upper_driver_jnts[1].pointer,
            ctrl=self.ribbon_upper_mid_ctrl.pointer,
            object_orient=ik_fk_switch_obj.root_jnt,
            vis_attr=bendy_bones_attr,
        )
        self.ribbon_upper_mid_ctrl.pointer.scale_attrs_connect()

        lower_ribbon.connect_mid_driver_ctrl(
            driver_jnt=self.ribbon_lower_driver_jnts[1].pointer,
            ctrl=self.ribbon_lower_mid_ctrl.pointer,
            object_orient=ik_fk_switch_obj.mid_jnt,
            vis_attr=bendy_bones_attr,
        )
        self.ribbon_lower_mid_ctrl.pointer.scale_attrs_connect()

        if self.expose_rotation_order_attr.value:
            for obj in [fk_chain_obj, ik_chain_obj, ik_fk_switch_obj, upper_ribbon, lower_ribbon]:
                obj.expose_rotation_order()

        if self.ribbon_ctrls_attr.value:
            upper_ribbon.micro_ctrls_setup(
                driven_ctrls=[ctrl.pointer for ctrl in self.upper_ribbon_ctrls],
                parent_to=ik_fk_switch_obj.base_ctrl,
                vis_attr=ribbon_ctrls_vis_attr,
            )

            lower_ribbon.micro_ctrls_setup(
                driven_ctrls=[ctrl.pointer for ctrl in self.lower_ribbon_ctrls],
                parent_to=ik_fk_switch_obj.base_ctrl,
                vis_attr=ribbon_ctrls_vis_attr,
            )

        # ### foot setup.
        heel_pos_grp = IoTransform("{0}_heel_pos_grp".format(self.name))
        heel_pos_grp.offset_grp = heel_pos_grp.add_group_above("{0}_heel_pos_offset_grp".format(self.name))
        heel_pos_grp.offset_grp.parent_relative(ik_fk_switch_obj.tip_jnt)
        heel_pos_grp.offset_grp.set_matrix(self.heel_guide.world_transformations["matrix"])
        heel_pos_grp.offset_grp.set_scale([1, 1, 1])

        toes_jnt = self.toes_jnt.pointer
        toes_jnt.parent_relative(ik_fk_switch_obj.tip_jnt)
        toes_jnt.set_matrix(self.toes_guide.world_transformations["matrix"])
        toes_jnt.freeze_transformations()
        toes_jnt.add_joint_orient()

        toes_tip_jnt = self.toes_tip_jnt.pointer
        toes_tip_jnt.parent_relative(toes_jnt)
        toes_tip_jnt.set_matrix(self.toes_tip_guide.world_transformations["matrix"])
        toes_tip_jnt.freeze_transformations()
        toes_tip_jnt.add_joint_orient()

        loc_grp = ik_chain_obj.tip_ctrl.btm_ctrl.loc_grp
        loc_grp.add_group_above("{0}b_grp".format(loc_grp.short_name[:-3]), maintain_local_values=False)
        tilt_outer_grp = loc_grp.add_group_above("{0}_tilt_outer_grp".format(self.name))
        tilt_outer_grp.offset_grp = tilt_outer_grp.add_group_above("{0}_tilt_outer_offset_grp".format(self.name))
        tilt_inner_grp = loc_grp.add_group_above("{0}_tilt_inner_grp".format(self.name))
        tilt_inner_grp.offset_grp = tilt_inner_grp.add_group_above("{0}_tilt_inner_offset_grp".format(self.name))
        loc_grp.parent(self.module_grp)

        outer_tilt_pos = self.outer_tilt_guide.world_transformations["translate"]
        inner_tilt_pos = self.inner_tilt_guide.world_transformations["translate"]
        mc.xform(tilt_outer_grp.offset_grp, ws=True, translation=outer_tilt_pos)
        mc.xform(tilt_inner_grp.offset_grp, ws=True, translation=inner_tilt_pos)
        loc_grp.parent(tilt_inner_grp)

        ik_toes_tip_ctrl = self.ik_toes_tip_ctrl.pointer
        self._parent_ctrl_above(loc_grp, ik_toes_tip_ctrl, toes_tip_jnt.get_matrix())
        tip_driven_grp = ik_toes_tip_ctrl.add_group_above("{0}_driven_grp".format(ik_toes_tip_ctrl.short_name))
        ik_toes_ball_ctrl = self.ik_toes_ball_ctrl.pointer
        self._parent_ctrl_above(loc_grp, ik_toes_ball_ctrl, toes_jnt.get_matrix())
        toes_driven_grp = ik_toes_ball_ctrl.add_group_above("{0}_driven_grp".format(ik_toes_ball_ctrl.short_name))
        ik_heel_ctrl = self.ik_heel_ctrl.pointer
        self._parent_ctrl_above(loc_grp, ik_heel_ctrl, heel_pos_grp.get_matrix())
        heel_driven_grp = ik_heel_ctrl.add_group_above("{0}_driven_grp".format(ik_heel_ctrl.short_name))

        ik_toes_tip_ctrl.add_spacer_attr()
        movable_pivot_setup(ik_toes_tip_ctrl, scale_pivot=False, attr=None)
        tip_driven_grp.connect_attr("rotatePivot", ik_toes_tip_ctrl.attr("rotatePivot"))

        ik_heel_ctrl.add_spacer_attr()
        movable_pivot_setup(ik_heel_ctrl, scale_pivot=False, attr=None)
        heel_driven_grp.connect_attr("rotatePivot", ik_heel_ctrl.attr("rotatePivot"))

        # toes_ctrl and it's compensate.
        toes_ctrl = self.toes_ctrl.pointer
        comp_a_grp = toes_ctrl.offset_grp.add_group_above("{0}_comp_a_grp".format(toes_ctrl.short_name))
        comp_b_grp = toes_ctrl.offset_grp.add_group_above("{0}_comp_b_grp".format(toes_ctrl.short_name))
        comp_c_grp = toes_ctrl.offset_grp.add_group_above("{0}_comp_c_grp".format(toes_ctrl.short_name))

        comp_a_grp.parent_relative(ik_fk_switch_obj.ctrls_grp)
        comp_a_grp.set_matrix(ik_fk_switch_obj.tip_jnt.get_matrix())
        comp_b_grp.set_matrix(toes_jnt.get_matrix())
        toes_ctrl.scale_attrs_connect()
        matrix_utils.matrix_constraint(driver=toes_ctrl, driven=toes_jnt, maintain_offset=False)
        matrix_utils.matrix_constraint(driver=ik_fk_switch_obj.tip_jnt, driven=comp_a_grp, maintain_offset=False)

        rotate_mult_node = mc.createNode("multiplyDivide", n="{0}_rotate_comp".format(comp_c_grp.short_name))
        switch_node = mc.createNode("multiplyDivide", n="{0}_switch_comp".format(comp_c_grp.short_name))
        add_node = mc.createNode(ADD_DL, n="{0}_add_driven".format(tip_driven_grp.short_name))

        mc.connectAttr(ik_toes_ball_ctrl.attr("rotateX"), "{0}.input1".format(add_node))
        mc.connectAttr("{0}.rotateX".format(toes_driven_grp), "{0}.input2".format(add_node))
        mc.connectAttr("{0}.output".format(add_node), "{0}.input1X".format(rotate_mult_node))
        mc.connectAttr(ik_toes_ball_ctrl.attr("rotateY"), "{0}.input1Y".format(rotate_mult_node))
        mc.connectAttr(ik_toes_ball_ctrl.attr("rotateZ"), "{0}.input1Z".format(rotate_mult_node))

        for attr in ["input2X", "input2Y", "input2Z"]:
            mc.setAttr("{0}.{1}".format(rotate_mult_node, attr), -1)

        mc.connectAttr("{0}.outputX".format(rotate_mult_node), "{0}.input1X".format(switch_node))
        mc.connectAttr("{0}.outputY".format(rotate_mult_node), "{0}.input1Y".format(switch_node))
        mc.connectAttr("{0}.outputZ".format(rotate_mult_node), "{0}.input1Z".format(switch_node))

        mc.connectAttr("{0}.outputX".format(ik_fk_switch_obj.reverse_node), "{0}.input2X".format(switch_node))
        mc.connectAttr("{0}.outputX".format(ik_fk_switch_obj.reverse_node), "{0}.input2Y".format(switch_node))
        mc.connectAttr("{0}.outputX".format(ik_fk_switch_obj.reverse_node), "{0}.input2Z".format(switch_node))

        mc.connectAttr("{0}.outputX".format(switch_node), comp_c_grp.attr("rotateX"))
        mc.connectAttr("{0}.outputY".format(switch_node), comp_c_grp.attr("rotateY"))
        mc.connectAttr("{0}.outputZ".format(switch_node), comp_c_grp.attr("rotateZ"))

        minus_node = mc.createNode("plusMinusAverage", n="{0}_rotation_order_minus".format(comp_c_grp.short_name))
        mc.setAttr("{0}.operation".format(minus_node), 2)
        mc.setAttr("{0}.input3D[0].input3Dx".format(minus_node), 5)
        mc.connectAttr(ik_toes_ball_ctrl.attr("rotateOrder"), "{0}.input3D[1].input3Dx".format(minus_node))
        mc.connectAttr("{0}.output3Dx".format(minus_node), comp_c_grp.attr("rotateOrder"))

        master_ctrl = self.master_ctrl.pointer
        master_ctrl.offset_grp.parent_relative(ik_chain_obj.tip_ctrl.btm_ctrl)
        master_ctrl.offset_grp.set_matrix(toes_tip_jnt.get_matrix())

        master_ctrl.add_spacer_attr()
        foot_roll_attr = master_ctrl.add_attr("foot_roll_angle", dv=30, min=0, max=180, keyable=True)
        tilt_vis_attr = master_ctrl.add_attr("tilt_pivots", attributeType="bool", keyable=True, dv=0)
        movable_pivot_setup(tilt_outer_grp, scale_pivot=False, attr=tilt_vis_attr)
        movable_pivot_setup(tilt_inner_grp, scale_pivot=False, attr=tilt_vis_attr)

        # tilt.
        clamp = mc.createNode("clamp", n="{0}_tilt_clamp".format(master_ctrl.short_name))
        mc.connectAttr(master_ctrl.attr("rotateY"), "{0}.inputR".format(clamp))
        mc.connectAttr(master_ctrl.attr("rotateY"), "{0}.inputG".format(clamp))
        mc.setAttr("{0}.maxR".format(clamp), 360)
        mc.setAttr("{0}.minG".format(clamp), -360)
        mc.connectAttr("{0}.outputR".format(clamp), tilt_inner_grp.attr("rotateZ"))
        mc.connectAttr("{0}.outputG".format(clamp), tilt_outer_grp.attr("rotateZ"))

        # foot_roll and heel pivot.
        clamp = mc.createNode("clamp", n="{0}_foot_roll_clamp".format(master_ctrl.short_name))
        multi_a = mc.createNode(MULT_DL, n="{0}_foot_roll_inverse".format(master_ctrl.short_name))
        multi_b = mc.createNode(MULT_DL, n="{0}_toes_inverse".format(master_ctrl.short_name))
        remap = mc.createNode("remapValue", n="{0}_remap_foot_roll".format(master_ctrl.short_name))

        mc.connectAttr(master_ctrl.attr("rotateX"), "{0}.{1}".format(multi_a, MULT_DL_INPUT1))
        mc.setAttr("{0}.{1}".format(multi_a, MULT_DL_INPUT2), -1)

        mc.connectAttr("{0}.output".format(multi_a), "{0}.inputValue".format(remap))
        mc.connectAttr(foot_roll_attr, "{0}.inputMin".format(remap))
        mc.setAttr("{0}.inputMax".format(remap), 10000)
        mc.setAttr("{0}.outputMin".format(remap), 0)
        mc.setAttr("{0}.outputMax".format(remap), -10000)
        mc.connectAttr("{0}.outValue".format(remap), tip_driven_grp.attr("rotateX"))

        mc.connectAttr(master_ctrl.attr("rotateX"), "{0}.inputR".format(clamp))
        mc.connectAttr("{0}.output".format(multi_a), "{0}.inputG".format(clamp))
        mc.setAttr("{0}.minR".format(clamp), 0)
        mc.setAttr("{0}.maxR".format(clamp), 180)
        mc.setAttr("{0}.minG".format(clamp), 0)
        mc.connectAttr(foot_roll_attr, "{0}.maxG".format(clamp))
        mc.connectAttr("{0}.outputR".format(clamp), heel_driven_grp.attr("rotateX"))
        mc.connectAttr("{0}.outputG".format(clamp), "{0}.{1}".format(multi_b, MULT_DL_INPUT1))

        mc.setAttr("{0}.{1}".format(multi_b, MULT_DL_INPUT2), -1)
        mc.connectAttr("{0}.output".format(multi_b), toes_driven_grp.attr("rotateX"))

        matrix_utils.matrix_constraint(driver=toes_tip_jnt, driven=toes_tip_output, maintain_offset=False)
        matrix_utils.matrix_constraint(driver=toes_jnt, driven=toes_start_output, maintain_offset=False)

        if self.auto_clavicle_attr.value:
            ik_fk_switch_obj.auto_base_setup(x_limits=(-180, 180), z_limits=(-180, 180))

        if self.roundness_attr.value:
            ik_fk_switch_obj.roundness_setup()

        ik_chain_obj.pole_vector_rest_update()  # update PV rest pos at setup end fixes a bug.

    @staticmethod
    def _parent_ctrl_above(child, new_parent_ctrl, matrix):
        """Parent new_parent_ctrl above child and below child current parent.

        Args:
            child (IoTransform): the child to add the new parent above
            new_parent_ctrl (IoTransform): the new parent ctrl to add above
            matrix (list): of matrix to position and orient new_parent_ctrl
        """
        grandparent = mc.listRelatives(child, parent=True, fullPath=True)[0]
        new_parent_ctrl.offset_grp.parent(grandparent)
        new_parent_ctrl.offset_grp.set_matrix(matrix)
        child.parent(new_parent_ctrl)
