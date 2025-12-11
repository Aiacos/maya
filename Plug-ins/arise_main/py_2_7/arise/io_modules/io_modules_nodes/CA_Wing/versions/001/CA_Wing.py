"""CA_Wing module creates a cartoon_complex wing module. """

import maya.cmds as mc

from arise.data_types import node_data
from arise.utils import math_utils
from arise.utils.modules_utils import create_grps, create_bezier_ctrls, SECONDARY_COLOR, update_ctrls
from arise.utils.matrix_utils import matrix_constraint
from arise.utils.io_nodes.io_transform import IoTransform

from arise.utils.subcomponents.complex_ribbon import ComplexRibbon
from arise.utils.subcomponents.ik_chain_three_joints import IkChainThreeJoints
from arise.utils.subcomponents.fk_chain_three_joints import FkChainThreeJoints
from arise.utils.subcomponents.ik_fk_switch import IkFkSwitch

MAYA_VERSION = 2016  # the version of maya from which this module is supported.
AUTHOR = "Etay Herz"  # creator of module.
RIG_CATEGORY = "Cartoon"  # either 'Basic', 'Cartoon', 'Vfx', 'Game' or 'All'.
RIG_TYPE = "Bird"  # Biped, Car, Quadruped, All, ...
TAGS = ["cartoon", "complex", "advance", "ribbon", "feathers", "flight", "arm", "air"]
TOOL_TIP = "Cartoon wing. Everything an arm has plus control over feathers."

SWITCH_ATTR_OPTIONS = ["switch_ctrl", "proxy attrs"]

ROOT_POS = [9.826, 7.0, 0.0]
MID_POS = [18.826, 7.0, -3.51]
TIP_POS = [28.626, 7.0, 0.0]
META_POS = [38.076, 7, -1.76]

SCAP_ROTATION = [-68.694, 0, 90]
SEC_ROTATION = [-109.706, 0, 90]
PRIM_ROTATION = [-79.450, 0, 90]

node_data.NodeData.update_ctrls = update_ctrls


class CA_Wing(node_data.NodeData):
    """CA_Wing module creates a cartoon_complex wing module. """
    sort_priority = 100

    def __init__(self, parent, docs, icon, module_dict):
        node_data.NodeData.__init__(
            self,
            parent=parent,
            icon=icon,
            docs=docs,
            module_dict=module_dict
        )

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
            default_value=items.index("+X"),  # Arm points to side (+X).
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
        self.scap_feathers_attr = self.add_integer_attribute(
            name="Scapula Feathers",
            default_value=5,
            dynamic_attribute=False,
            writable=True,
            readable=True,
            promoted=False,
            annotation=(
                "Number of feathers to create.\n"
                "The wing has 3 feathers sections:\n"
                "Scapula feathers are the feathers closest to the wing root\n"
                "Secondary feathers are the middle section (forearm)\n"
                "Primary feathers are the at the tip section (palm)\n"
                "When changed, a 're-template' is required"
            ),
            min_value=3,
            max_value=50,
        )

        self.sec_feathers_attr = self.add_integer_attribute(
            name="Secondary Feathers",
            default_value=5,
            dynamic_attribute=False,
            writable=True,
            readable=True,
            promoted=False,
            annotation=(
                "Number of feathers to create.\n"
                "The wing has 3 feathers sections:\n"
                "Scapula feathers are the feathers closest to the wing root\n"
                "Secondary feathers are the middle section (forearm)\n"
                "Primary feathers are the at the tip section (palm)\n"
                "When changed, a 're-template' is required"
            ),
            min_value=3,
            max_value=50,
        )

        self.prim_feathers_attr = self.add_integer_attribute(
            name="Primary Feathers",
            default_value=5,
            dynamic_attribute=False,
            writable=True,
            readable=True,
            promoted=False,
            annotation=(
                "Number of feathers to create.\n"
                "The wing has 3 feathers sections:\n"
                "Scapula feathers are the feathers closest to the wing root\n"
                "Secondary feathers are the middle section (forearm)\n"
                "Primary feathers are the at the tip section (palm)\n"
                "When changed, a 're-template' is required"
            ),
            min_value=3,
            max_value=50,
        )

        self.auto_orient_attr = self.add_boolean_attribute(
            name="Auto Orient",
            default_value=True,
            annotation="feather_aim_b_ctrl will auto orient.",
        )

        self.add_separator()
        self.switch_ctrl_attr = self.add_radio_attribute(
            name="Ik Fk Switch",
            items=SWITCH_ATTR_OPTIONS,
            default_value=0,
            annotation=(
                "Select where the 'Ik Fk Switch' attribute and other shared attributes are placed:\n"
                "'switch_ctrl' - Places them on a ctrl that follows the wing tip (default).\n"
                "'proxy_attrs' - places them as shared attributes (proxy attributes), "
                "on both the IK tip ctrl and the FK tip ctrl."
            ),
            help_link="https://youtu.be/-1fpRw6oJME?t=171",
        )

        self.switch_offset_attr = self.add_xyz_attribute(
            name="Switch Ctrl Offset",
            default_value=[3, 0, 0],
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
            default_value=True,
            annotation=(
                "Only affects mirrored nodes.\n\n"
                "Unchecked - The IK ctrls of mirrored nodes will align with the world,\n"
                "meaning that both wings will move and rotate in the same direction (default for legs).\n\n"
                "Checked - The IK ctrls of mirrored nodes will mirror orientations,\n"
                "meaning that both wings will reflect each other behavior (default for arms)."
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
            default_value=[5, 0, 0],
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
        self.driver_tip_attr = self.add_driver_attribute(name="Tip Output", annotation="Output")

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
        self.base_guide = self.add_guide(name="base", translation=[5.35, 7, 0], rotation=[180, 0, 90])
        self.root_guide = self.add_aim_guide(name="root", translation=ROOT_POS, parent=self.base_guide)
        self.mid_guide = self.add_aim_guide(name="mid", translation=MID_POS, parent=self.base_guide)

        self.tip_guide = self.add_guide(
            name="tip",
            translation=TIP_POS,
            rotation=[190.55, 0.0, 90.0],
            parent=self.base_guide,
        )
        self.tip_guide.shape = ["square_with_arrow", "arrow"]
        self.tip_guide.rotate_offset = [0, 90, 0]
        self.tip_guide.scale_offset = (1.5, 0.8, 1.5)

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
            offset=(-0.5, 17),
        )

        self.mid_guide.aim_side_pin = [self.tip_guide, self.ik_pv_guide]
        self.root_guide.aim_side_pin = [self.tip_guide, self.ik_pv_guide]

        self.carp_guide = self.add_aim_guide(
            name="metacarpal",
            translation=META_POS,
            parent=self.tip_guide,
            aim_at_guide=self.tip_guide,
        )
        self.carp_guide.aim_rotation_offset = (180, 0, 0)

        self.aim_a_guide = self.add_direction_guide(name="feathers_aim_a", position_guide=self.root_guide)
        self.aim_a_guide.rotation = [-68.694, 0, 90]

        self.aim_b_guide = self.add_direction_guide(name="feathers_aim_b", position_guide=self.mid_guide)
        self.aim_b_guide.rotation = [-90, 0, 90]

        self.aim_c_guide = self.add_direction_guide(name="feathers_aim_c", position_guide=self.tip_guide)
        self.aim_c_guide.rotation = [-109.562, 0, 90]

        self.aim_d_guide = self.add_direction_guide(name="feathers_aim_d", position_guide=self.carp_guide)
        self.aim_d_guide.rotation = [-154.983, 0, 90]

        self.aim_guides = [self.aim_a_guide, self.aim_b_guide, self.aim_c_guide, self.aim_d_guide]

        for guide in [self.root_guide, self.mid_guide, self.tip_guide, self.ik_pv_guide, self.carp_guide]:
            guide.size = 1.2

        for guide in self.aim_guides:
            guide.scale_offset = [2, 6, 2]

        self.scap_guides = self._feather_guides_creation(
            feather_count=self.scap_feathers_attr.value,
            start_pos=ROOT_POS,
            end_pos=MID_POS,
            parents=[self.root_guide, self.mid_guide],
            ori_parent=self.root_guide,
            name="scapula_feather",
            rotation=SCAP_ROTATION,
        )
        self.mid_guide.visual_parent = self.scap_guides[-1]

        self.sec_guides = self._feather_guides_creation(
            feather_count=self.sec_feathers_attr.value,
            start_pos=MID_POS,
            end_pos=TIP_POS,
            parents=[self.mid_guide, self.tip_guide],
            ori_parent=self.mid_guide,
            name="secondary_feather",
            rotation=SEC_ROTATION,
        )
        self.tip_guide.visual_parent = self.sec_guides[-1]

        self.prim_guides = self._feather_guides_creation(
            feather_count=self.prim_feathers_attr.value,
            start_pos=TIP_POS,
            end_pos=META_POS,
            parents=[self.tip_guide, self.carp_guide],
            ori_parent=self.carp_guide,
            name="primary_feather",
            rotation=PRIM_ROTATION,
        )
        self.prim_guides
        self.carp_guide.visual_parent = self.prim_guides[-1]

    def _feather_guides_creation(self, feather_count, start_pos, end_pos, parents, ori_parent, name, rotation):
        """Create feathers guides for section.

        Args:
            feather_count (int): number of guides to create
            start_pos (list): of 3 floats representing start of line to create guides along
            end_pos (list): of 3 floats representing end of line to create guides along
            parents (list): of 2 parent guides to help drive its position and orientation
            ori_parent (str): name of guide to orient constraint to
            name (str): prefix name of new guides
            rotation (list): of 3 floats representing rotation of guides

        Returns:
            list: of lists of new guides (each list is a feather)
        """
        feathers_guides = []
        for index in range(1, feather_count+1):
            pos = [
                ((end_pos[0] - start_pos[0]) * (index/(feather_count+1.0))) + start_pos[0],
                ((end_pos[1] - start_pos[1]) * (index/(feather_count+1.0))) + start_pos[1],
                ((end_pos[2] - start_pos[2]) * (index
                /(feather_count+1.0))) + start_pos[2],
            ]
            weight = index / float(feather_count+1)
            guide = self.add_multi_parents_guide(
                name="{0}_{1}".format(name, index),
                translation=pos,
                rotation=rotation,
            )
            guide.point_weights = [(parents[0], 1.0-weight), (parents[1], weight)]
            guide.orient_weights = [(ori_parent, 1.0)]
            guide.scale_weights = [(parents[0], 1.0)]
            guide.size = 0.4
            guide.visual_parent = feathers_guides[-1] if feathers_guides else None
            feathers_guides.append(guide)

        return feathers_guides

    def joints_creation(self):
        """Create joints based on attributes values and guides. (without positioning as this point). """
        # driven joints.
        self.base_jnt = self.add_joint(name="base", skinning_jnt=True, tag_parent_jnt=None, radius=1)
        self.root_jnt = self.add_joint(name="root", skinning_jnt=False, tag_parent_jnt=self.base_jnt, radius=1)
        self.mid_jnt = self.add_joint(name="mid", skinning_jnt=False, radius=1)

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
            self.add_joint(name="upper_ribbon_driver_1", skinning_jnt=False, tag_parent_jnt=None, radius=0.5),
            self.add_joint(name="upper_ribbon_driver_2", skinning_jnt=False, tag_parent_jnt=None, radius=0.5),
            self.add_joint(name="upper_ribbon_driver_3", skinning_jnt=False, tag_parent_jnt=None, radius=0.5),
        ]

        self.ribbon_lower_driver_jnts = [
            self.add_joint(name="lower_ribbon_driver_1", skinning_jnt=False, tag_parent_jnt=None, radius=0.5),
            self.add_joint(name="lower_ribbon_driver_2", skinning_jnt=False, tag_parent_jnt=None, radius=0.5),
            self.add_joint(name="lower_ribbon_driver_3", skinning_jnt=False, tag_parent_jnt=None, radius=0.5),
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

        self.tip_jnt = self.add_joint(name="tip", skinning_jnt=True, radius=1)
        self.tip_jnt.parent_tag = self.ribbon_lower_driven_jnts[-1]

        self.meta_jnt = self.add_joint(name="metacarpals", skinning_jnt=False, radius=1)

        self.scap_feathers_jnts = []
        for feather_index in range(1, self.scap_feathers_attr.value+1):
            jnt = self.add_joint(
                name="scapula_feather_{0}".format(feather_index),
                skinning_jnt=True,
                tag_parent_jnt=self.ribbon_upper_driven_jnts[0],
                radius=0.25,
            )
            self.scap_feathers_jnts.append(jnt)

        self.sec_feathers_jnts = []
        for feather_index in range(1, self.sec_feathers_attr.value+1):
            jnt = self.add_joint(
                name="secondary_feather_{0}".format(feather_index),
                skinning_jnt=True,
                tag_parent_jnt=self.ribbon_lower_driven_jnts[0],
                radius=0.25,
            )
            self.sec_feathers_jnts.append(jnt)

        self.prim_feathers_jnts = []
        for feather_index in range(1, self.prim_feathers_attr.value+1):
            jnt = self.add_joint(
                name="primary_feather_{0}".format(feather_index),
                skinning_jnt=True,
                tag_parent_jnt=self.tip_jnt,
                radius=0.25,
            )
            self.prim_feathers_jnts.append(jnt)

        # humanIK definition.
        self.base_jnt.human_ik = "*Shoulder"
        self.tip_jnt.human_ik = "*Hand"

        arm_roll_tags = ["*Arm"] + ["Leaf*ArmRoll{0}".format(index) for index in range(1, 6)]
        for jnt, tag in zip(self.ribbon_upper_driven_jnts, arm_roll_tags):
            jnt.human_ik = tag

        forearm_roll_tags = ["*ForeArm"] + ["Leaf*ForeArmRoll{0}".format(index) for index in range(1, 6)]
        for jnt, tag in zip(self.ribbon_lower_driven_jnts, forearm_roll_tags):
            jnt.human_ik = tag

    def ctrls_creation(self):
        """Create controls based on attributes values, guides and joints. (without positioning as this point). """
        scale_mult = self.ctrls_scale_attr.value

        self.base_ctrl = self.add_ctrl(
            name="base", shape="pin_sphere_2_way", up_orient="+Z", size=(1.6 * scale_mult),
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

        # secondary ctrls.
        self.ik_secondary_ctrl = None
        self.fk_secondary_ctrls = None
        if self.secondary_ctrl_attr.value:

            orient = "+X" if self.clean_transformations_attr.value else self.world_orientation_attr.display_value
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

        size = [0.5*scale_mult, 5.0*scale_mult, 0.5*scale_mult]
        self.aim_ctrls = []
        for letter in ["a", "b", "c", "d"]:
            ctrl = self.add_ctrl(name="feather_aim_{0}".format(letter), shape="box", size=size)
            ctrl.translate_offset = [0, ctrl.size[1], 0]
            self.aim_ctrls.append(ctrl)

            for attr in ["translateX", "translateY", "translateZ", "scaleX", "scaleY", "scaleZ"]:
                ctrl.add_locked_hidden_attr(attr)

        self.scap_feathers_ctrls = []
        for feather_index in range(1, self.scap_feathers_attr.value+1):
            ctrl = self.add_ctrl(name="scapula_feather_{0}".format(feather_index), size=0.7 * scale_mult)
            self.scap_feathers_ctrls.append(ctrl)

        self.sec_feathers_ctrls = []
        for feather_index in range(1, self.sec_feathers_attr.value+1):
            ctrl = self.add_ctrl(name="secondary_feather_{0}".format(feather_index), size=0.7 * scale_mult)
            self.sec_feathers_ctrls.append(ctrl)

        self.prim_feathers_ctrls = []
        for feather_index in range(1, self.prim_feathers_attr.value+1):
            ctrl = self.add_ctrl(name="primary_feather_{0}".format(feather_index), size=0.7 * scale_mult)
            self.prim_feathers_ctrls.append(ctrl)

        # HumanIK definition ctrls.
        self.base_ctrl.human_ik = "*Clavicle"
        self.ik_tip_ctrl.human_ik = "*Hand"
        self.ik_pv_ctrl.human_ik = "*Elbow"

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

        if self.auto_orient_attr.value:
            self.aim_ctrls[1].add_maya_attr(name="auto_orient", attr_type="float", default_value=1, min=0, max=1)

    def rig_creation(self):
        """Based on attributes value, guides (which now you can get global position from) joints and controls
        created in their methods you can build the rig.
        """
        ctrls_scale = self.ctrls_scale_attr.value

        if self.is_mirrored:
            self.module_grp.set_attr("scaleX", -1)

        grps = create_grps(self, ["input_root_grp", "input_ik_tip_grp", "output_root_grp", "output_tip_grp"])
        input_root_grp, input_ik_tip_grp, output_root_grp, output_tip_grp = grps

        self.driven_roots_attr.set_maya_object(input_root_grp)
        self.driven_ik_tip_attr.set_maya_object(input_ik_tip_grp)
        self.driver_root_attr.set_maya_object(output_root_grp)
        self.driver_tip_attr.set_maya_object(output_tip_grp)

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
            world_direction_flip_x=True,
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
            world_direction_flip_x=True,
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
            output_tip_grp=output_tip_grp,
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
        mid_vis_attr = ik_fk_switch_obj.create_attr_on_switch("mid_ctrl", at="bool", k=True, dv=0)
        bendy_bones_attr = ik_fk_switch_obj.create_attr_on_switch("bendy_bones_ctrls", at="bool", k=True, dv=0)

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

        meta_jnt = self.meta_jnt.pointer
        meta_jnt.parent_relative(self.tip_jnt.pointer)
        meta_jnt.set_matrix(self.carp_guide.world_transformations["matrix"])
        meta_jnt.set_attr("scale", [1, 1, 1])

        self._setup_feathers(ribbons=[upper_ribbon, lower_ribbon])

        if self.auto_orient_attr.value:
            self.orient_aim_setup()

        if self.roundness_attr.value:
            ik_fk_switch_obj.roundness_setup()

        ik_chain_obj.pole_vector_rest_update()  # update PV rest pos at setup end fixes a bug.

    def _setup_feathers(self, ribbons):
        """Setup the feathers ctrls and aim setup.

        Args:
            ribbons (list): upper and lower ribbons
        """
        ctrls_grp, jnts_grp = create_grps(self, ["feathers_ctrls_grp", "feathers_jnts_grp"])
        aim_ctrls = [ctrl.pointer for ctrl in self.aim_ctrls]
        const_jnts = [self.root_jnt.pointer, self.mid_jnt.pointer, self.tip_jnt.pointer, self.meta_jnt.pointer]
        orient_jnts = []
        for aim_ctrl, guide, const_jnt in zip(aim_ctrls, self.aim_guides, const_jnts):
            aim_ctrl.top_grp = aim_ctrl.offset_grp.add_group_above("{0}_pos_grp".format(aim_ctrl.short_name))
            aim_ctrl.top_grp_pos = aim_ctrl.top_grp.add_group_above("{0}_section_grp".format(aim_ctrl.short_name))
            aim_ctrl.top_grp_pos.parent_relative(ctrls_grp)
            matrix_constraint(const_jnt, aim_ctrl.top_grp_pos, maintain_offset=False)
            aim_ctrl.top_grp.set_matrix(guide.world_transformations["matrix"])
            aim_ctrl.top_grp.set_attr("scale", [1, 1, 1])

            jnt_index = const_jnts.index(const_jnt)
            if jnt_index != 0 and jnt_index != 3:
                orient_jnts.append(self._orient_jnts(aim_ctrl=aim_ctrl, parent_jnt=const_jnts[jnt_index-1]))

            orient_jnts.append(self._orient_jnts(aim_ctrl=aim_ctrl, parent_jnt=const_jnt))

        scap_ctrls = [ctrl.pointer for ctrl in self.scap_feathers_ctrls]
        scap_jnts = [jnt.pointer for jnt in self.scap_feathers_jnts]
        for index, (feather_ctrl, guide, jnt) in enumerate(zip(scap_ctrls, self.scap_guides, scap_jnts)):
            jnt.parent_relative(jnts_grp)
            matrix_constraint(feather_ctrl, jnt, maintain_offset=False)
            offset_grp = feather_ctrl.offset_grp
            feather_ctrl.pos_grp = offset_grp.add_group_above("{0}_pos_grp".format(feather_ctrl.short_name))
            feather_ctrl.ori_grp = offset_grp.add_group_above("{0}_orient_grp".format(feather_ctrl.short_name))
            feather_ctrl.pos_grp.parent_relative(aim_ctrls[0].top_grp)
            feather_ctrl.pos_grp.set_matrix(guide.world_transformations["matrix"])
            feather_ctrl.pos_grp.set_attr("scale", [1, 1, 1])

            default_value = 1.0 - (index+1.0) / (len(scap_ctrls)+1)
            self._create_blend_color(orient_jnts[0], orient_jnts[1], feather_ctrl, default_value)
            u_pos = self._closest_u_pos(position=guide.world_transformations["translate"], ribbon=ribbons[0])
            self._follow_ribbon_pos(ctrl=feather_ctrl, u_pos=u_pos, ribbon=ribbons[0], parent=aim_ctrls[0].top_grp)

        sec_ctrls = [ctrl.pointer for ctrl in self.sec_feathers_ctrls]
        sec_jnts = [jnt.pointer for jnt in self.sec_feathers_jnts]
        for index, (feather_ctrl, guide, jnt) in enumerate(zip(sec_ctrls, self.sec_guides, sec_jnts)):
            jnt.parent_relative(jnts_grp)
            matrix_constraint(feather_ctrl, jnt, maintain_offset=False)
            offset_grp = feather_ctrl.offset_grp
            feather_ctrl.pos_grp = offset_grp.add_group_above("{0}_pos_grp".format(feather_ctrl.short_name))
            feather_ctrl.ori_grp = offset_grp.add_group_above("{0}_orient_grp".format(feather_ctrl.short_name))
            feather_ctrl.pos_grp.parent_relative(aim_ctrls[1].top_grp)
            feather_ctrl.pos_grp.set_matrix(guide.world_transformations["matrix"])
            feather_ctrl.pos_grp.set_attr("scale", [1, 1, 1])

            default_value = 1.0 - (index+1.0) / (len(sec_ctrls)+1)
            self._create_blend_color(orient_jnts[2], orient_jnts[3], feather_ctrl, default_value)
            u_pos = self._closest_u_pos(position=guide.world_transformations["translate"], ribbon=ribbons[1])
            self._follow_ribbon_pos(ctrl=feather_ctrl, u_pos=u_pos, ribbon=ribbons[1], parent=aim_ctrls[1].top_grp)

        prim_ctrls = [ctrl.pointer for ctrl in self.prim_feathers_ctrls]
        prim_jnts = [jnt.pointer for jnt in self.prim_feathers_jnts]
        for index, (feather_ctrl, guide, jnt) in enumerate(zip(prim_ctrls, self.prim_guides, prim_jnts)):
            jnt.parent_relative(jnts_grp)
            matrix_constraint(feather_ctrl, jnt, maintain_offset=False)
            offset_grp = feather_ctrl.offset_grp
            feather_ctrl.pos_grp = offset_grp.add_group_above("{0}_pos_grp".format(feather_ctrl.short_name))
            feather_ctrl.ori_grp = offset_grp.add_group_above("{0}_orient_grp".format(feather_ctrl.short_name))
            feather_ctrl.pos_grp.parent_relative(aim_ctrls[2].top_grp)
            feather_ctrl.pos_grp.set_matrix(guide.world_transformations["matrix"])
            feather_ctrl.pos_grp.set_attr("scale", [1, 1, 1])

            default_value = 1.0 - (index+1.0) / (len(prim_ctrls)+1)
            self._create_blend_color(orient_jnts[4], orient_jnts[5], feather_ctrl, default_value)

    @staticmethod
    def _orient_jnts(aim_ctrl, parent_jnt):
        """Create 2 jnts IK to get clean rotations.

        Args:
            aim_ctrl (IoCtrl): ctrl ik will follow
            parent_jnt (IoJoint): joint to parent under. so rotation values will be relative to

        Returns:
            IoTransform: of first joint in IK
        """
        mc.select(clear=True)
        name = "{0}_{1}".format(aim_ctrl.short_name, parent_jnt.short_name)
        joint_base = IoTransform(mc.joint(name="{0}_orient_base".format(name)), existing=True)
        mc.select(clear=True)
        joint_tip = IoTransform(mc.joint(name="{0}_orient_tip".format(name)), existing=True)
        pos_grp = joint_base.add_group_above("{0}_orient_pos_grp".format(name))
        pos_grp.point_constraint_to(aim_ctrl, mo=False)
        pos_grp.hide()

        joint_tip.parent_relative(joint_base)
        joint_base.set_attr("jointOrient", [0, 0, 0])
        joint_tip.set_attr("jointOrient", [0, 0, 0])
        joint_tip.set_attr("translateY", 4)

        pos_grp.parent_relative(parent_jnt)
        pos_grp.match_transformation_to(aim_ctrl)

        orient_ik_handle, _ = mc.ikHandle(
            name="{0}_orient_ikHandle".format(name),
            solver="ikRPsolver",
            startJoint=joint_base,
            endEffector=joint_tip,
        )

        mc.parent(orient_ik_handle, aim_ctrl)
        mc.hide(orient_ik_handle)
        mc.setAttr("{0}.poleVector".format(orient_ik_handle), *[0, 0, 0])

        return joint_base

    @staticmethod
    def _create_blend_color(orient_grp_root, orient_grp_end, ctrl, blend_value):
        """Connect ctrl to orient follow orient_jnts.

        Args:
            orient_grp_root (IoTransform): root grp to orient follow
            orient_grp_end (IoTransform): end grp to orient follow
            ctrl (IoCtrl): ctrl that will follow
            blend_value (float): between 0-1 of which ctrl to follow
        """
        blend_node = mc.createNode("blendColors", n="{0}_blendColors".format(ctrl.short_name))
        mc.connectAttr("{0}.rotateX".format(orient_grp_root), "{0}.color1R".format(blend_node))
        mc.connectAttr("{0}.rotateY".format(orient_grp_root), "{0}.color1G".format(blend_node))
        mc.connectAttr("{0}.rotateZ".format(orient_grp_root), "{0}.color1B".format(blend_node))

        mc.connectAttr("{0}.rotateX".format(orient_grp_end), "{0}.color2R".format(blend_node))
        mc.connectAttr("{0}.rotateY".format(orient_grp_end), "{0}.color2G".format(blend_node))
        mc.connectAttr("{0}.rotateZ".format(orient_grp_end), "{0}.color2B".format(blend_node))

        ctrl.add_spacer_attr()
        blend_attr = ctrl.add_attr("blend_to_root", min=0, max=1, dv=blend_value, keyable=True)
        mc.connectAttr(blend_attr, "{0}.blender".format(blend_node))

        mc.connectAttr("{0}.outputR".format(blend_node), "{0}.rotateX".format(ctrl.ori_grp))
        mc.connectAttr("{0}.outputG".format(blend_node), "{0}.rotateY".format(ctrl.ori_grp))
        mc.connectAttr("{0}.outputB".format(blend_node), "{0}.rotateZ".format(ctrl.ori_grp))

    @staticmethod
    def _closest_u_pos(position, ribbon):
        """Return U pos on surface of ribbon. """
        closest_point = mc.createNode("closestPointOnSurface")
        mc.setAttr("{0}.inPosition".format(closest_point), *position)
        mc.connectAttr(
            "{0}.worldSpace[0]".format(ribbon.nurb_surface_shape),
            "{0}.inputSurface".format(closest_point),
        )
        u_value = mc.getAttr("{0}.parameterU".format(closest_point))
        mc.delete(closest_point)

        return u_value

    def _follow_ribbon_pos(self, ctrl, u_pos, ribbon, parent):
        """Have ctrl follow ribbon (position only) at U_pos on ribbon. """
        surface_info = mc.createNode("pointOnSurfaceInfo", name="{0}_surface_info".format(ctrl.short_name))
        mc.connectAttr(
            "{0}.worldSpace[0]".format(ribbon.nurb_surface_shape),
            "{0}.inputSurface".format(surface_info),
        )
        mc.setAttr("{0}.parameterU".format(surface_info), u_pos)
        mc.setAttr("{0}.parameterV".format(surface_info), 0.5)

        loc_offset_grp = IoTransform("{0}_follow_loc_grp".format(ctrl.short_name))
        loc_offset_grp.parent_relative(parent)
        loc_offset_grp.set_attr("inheritsTransform", 0)
        loc_offset_grp.hide()

        driver_loc = mc.spaceLocator(name="{0}_follow_loc".format(ctrl.short_name))
        driver_loc = IoTransform(driver_loc, existing=True)
        driver_loc.parent_relative(loc_offset_grp)

        mc.connectAttr("{0}.position".format(surface_info), driver_loc.attr("translate"))

        ctrl.pos_grp.point_constraint_to(driver_loc, mo=True)

    def orient_aim_setup(self):
        """Give option for 'feather_aim_b_ctrl' to auto orient based on aim_a and aim_b rotations. """
        aim_a, aim_b, aim_c = self.aim_ctrls[0].pointer, self.aim_ctrls[1].pointer, self.aim_ctrls[2].pointer
        aim_b.orient_offset_grp = aim_b.add_group_above("{0}_orient_offset_grp".format(aim_b.short_name))
        aim_b.orient_grp = aim_b.add_group_above("{0}_orient_grp".format(aim_b.short_name))

        aim_b.add_spacer_attr()
        auto_orient_attr = aim_b.add_attr("auto_orient", min=0, max=1, dv=1, keyable=True)

        aim_a.orient_driver = IoTransform("{0}_orient_driver_grp".format(aim_a.short_name), existing=False)
        aim_a.orient_driver.parent_relative(aim_b)
        aim_a.orient_driver.parent(aim_a)
        aim_a.orient_driver.set_attr("translate", [0, 0, 0])

        aim_c.orient_driver = IoTransform("{0}_orient_driver_grp".format(aim_c.short_name), existing=False)
        aim_c.orient_driver.parent_relative(aim_b)
        aim_c.orient_driver.parent(aim_c)
        aim_c.orient_driver.set_attr("translate", [0, 0, 0])

        ori_constraint = aim_b.orient_grp.orient_constraint_to(
            (aim_b.orient_offset_grp, aim_a.orient_driver, aim_c.orient_driver),
            mo=False,
        )
        aliases = mc.orientConstraint(ori_constraint, q=True, weightAliasList=True)

        mc.connectAttr(auto_orient_attr, "{0}.{1}".format(ori_constraint, aliases[1]))
        mc.connectAttr(auto_orient_attr, "{0}.{1}".format(ori_constraint, aliases[2]))

        reverse_node = mc.createNode("reverse", n="{0}_orient_reverse".format(aim_a.short_name))
        mc.connectAttr(auto_orient_attr, "{0}.inputX".format(reverse_node))
        mc.connectAttr("{0}.outputX".format(reverse_node), "{0}.{1}".format(ori_constraint, aliases[0]))
