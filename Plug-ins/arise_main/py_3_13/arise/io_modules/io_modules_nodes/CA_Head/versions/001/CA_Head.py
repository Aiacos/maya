"""Cartoon_A_Head module creates a cartoon_complex head and neck module. """

import maya.cmds as mc

from arise.utils.io_nodes.io_transform import IoTransform
from arise.data_types import node_data
from arise.utils import math_utils
from arise.utils.subcomponents.complex_ribbon import ComplexRibbon
from arise.utils.modules_utils import (
    world_rotation, create_module_scale, secondary_ctrls_setup, expose_rotation_order, create_grps,
    create_bezier_ctrls, SECONDARY_COLOR, update_ctrls, MULT_DL, MULT_DL_INPUT1, MULT_DL_INPUT2
)
from arise.utils.matrix_utils import matrix_constraint


MAYA_VERSION = 2016  # the version of maya from which this module supports.
AUTHOR = "Etay Herz"  # name of person who created this module.
RIG_CATEGORY = "Cartoon"  # either 'Basic', 'Cartoon', 'Vfx', 'Game' or 'All'. (used when filtering).
RIG_TYPE = "Biped"  # Biped, Car, Quadruped, All, ... (for filtering modules in lists).
TAGS = ["cartoon", "complex", "advance", "ribbon", "neck", "head",]
TOOL_TIP = "Cartoon neck and head with manual/auto volume, auto twist, Bezier ctrls, and more."

node_data.NodeData.update_ctrls = update_ctrls


class CA_Head(node_data.NodeData):
    """Cartoon_A_Head module creates a cartoon_complex arm module. """
    sort_priority = 100

    def __init__(self, parent, docs, icon, module_dict):
        node_data.NodeData.__init__(
            self,
            parent=parent,
            icon=icon,
            docs=docs,
            module_dict=module_dict
        )

        self.body_part = "head"

    def attributes_creation(self):
        """Here you add the module attributes. """
        self.add_collapsible_layout(title="Guides", shown=False)
        self.guides_up_shared_attr = self.add_boolean_attribute(
            name="Single Side Guide",
            default_value=True,
            annotation=(
                "For some Aim Guides, the 'side_vector' (twist) is locked and driven by a single 'side_vector', "
                "which keeps the orientation consistent.\n"
                "Uncheck this attribute to unlock them if you need more control over the twist.\n"
                "Re-template is required when changes are made."
            ),
            help_link="https://youtu.be/-1fpRw6oJME?t=233",
        )
        self.close_layout()

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
            default_value=True,
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
            default_value=items.index("+Y"),  # head points up ("+Y")
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
        self.secondary_ctrls_attr = self.add_boolean_attribute(
            name="Secondary Ctrls",
            default_value=True,
            annotation="Add secondary ctrls under 'neck_root_ctrl' and 'head_ctrl' to help prevent gimbal lock.",
            help_link="https://youtu.be/-1fpRw6oJME?t=157",
        )

        self.add_separator()
        self.volume_attr = self.add_boolean_attribute(
            name="Volume",
            default_value=True,
            annotation="Add 'Auto Volume' and 'Manual Volume' attributes to 'neck_root_ctrl'.",
        )

        self.translate_ctrl_attr = self.add_boolean_attribute(
            name="Ctrls Translate",
            default_value=True,
            annotation="If checked, will enable translation attributes on 'neck_root_ctrl' and 'head_ctrl'.",
        )
        self.pin_ctrl_attr = self.add_boolean_attribute(
            name="Pin Ctrl",
            default_value=False,
            annotation=(
                "Add a 'pin_ctrl' that constrains 'neck_mid_ctrl' when activated.\n"
                "Use a 'SpaceSwitch' attachment for 'pin_ctrl' to properly use this feature."
            ),
        )

        ### ribbons settings.
        self.add_separator("Ribbon Settings")
        self.ribbon_joints_attr = self.add_integer_attribute(
            name="Ribbon Joints",
            default_value=4,
            dynamic_attribute=False,
            writable=True,
            readable=True,
            promoted=False,
            annotation="The number of skinning joints the head has besides 'neck_root_jnt' and 'head_jnt'.",
            help_link="https://youtu.be/-1fpRw6oJME?t=198",
            min_value=2,
            max_value=20,
            add_slider=True,
        )

        self.ribbon_ctrls_attr = self.add_boolean_attribute(
            name="Ribbon Micro Ctrls",
            default_value=False,
            annotation="Create a ctrl for every ribbon skinning joint.",
            help_link="https://youtu.be/-1fpRw6oJME?t=211",
        )

        self.ribbon_bezier_attr = self.add_boolean_attribute(
            name="Bezier Ctrls",
            default_value=False,
            annotation="Add ctrls that deform the ribbon like a Bezier curve.",
            help_link="https://youtu.be/-1fpRw6oJME?t=222",
        )
        self.bezier_offset_attr = self.add_xyz_attribute(
            name="Bezier Ctrls Offset",
            default_value=[0, 0, -8],
            dynamic_attribute=False,
            writable=True,
            readable=True,
            promoted=False,
            annotation="Position offset of bezier ctrls from the ribbon.\nmultiplied by attribute 'Ctrls Scale'.",
        )

        ### connections.
        self.add_separator(title="Connections")
        self.driven_attr = self.add_driven_attribute(name="Root Input", annotation="Input")
        self.driver_root_attr = self.add_driver_attribute(name="Root Output", annotation="Output")
        self.driver_tip_attr = self.add_driver_attribute(name="Tip Output", annotation="Output")

        self.close_layout()

    def evaluate_creation_methods(self):  # REIMPLEMENTED!
        """Reimplemented to enable/disable attrs. """
        self.world_orientation_attr.set_disabled(True if self.clean_transformations_attr.value else False)
        self.world_twist_attr.set_disabled(True if self.clean_transformations_attr.value else False)
        self.bezier_offset_attr.set_disabled(False if self.ribbon_bezier_attr.value else True)

        node_data.NodeData.evaluate_creation_methods(self)

    def guides_creation(self):
        """Create guides based on attributes values. """
        self.neck_root_guide = self.add_aim_guide(
            name="neck_root",
            translation=(0, 145, 0),
            parent=None,
            # side_pin_rotation=(0, 180, 0),
            side_pin_guide=None,
        )
        self.neck_root_guide.size = self.neck_root_guide.size * 0.65

        self.neck_mid_guide = self.add_aim_guide(
            name="neck_mid",
            translation=(0, 153, 0),
            parent=self.neck_root_guide,
            side_pin_rotation=(0, 0, 0),
            side_pin_guide=self.neck_root_guide if self.guides_up_shared_attr.value else None,
        )
        self.neck_mid_guide.size = self.neck_mid_guide.size * 0.65

        self.head_guide = self.add_guide(
            name="head",
            translation=(0, 161, 0),
            parent=self.neck_mid_guide,
        )
        self.head_guide.shape = "circle_with_arrow"
        self.head_guide.rotate_offset = [-90, 0, 0]
        self.head_guide.size = self.head_guide.size * 3.3
        self.head_guide.translate_offset = [0, self.head_guide.size / 2, 0]

        # aim guides at each other.
        self.neck_root_guide.aim_at = self.neck_mid_guide
        self.neck_mid_guide.aim_at = self.head_guide
        self.head_guide.aim_at = self.neck_mid_guide
        self.head_guide.aim_rotation_offset = [180, 0, 0]

    def joints_creation(self):
        """Create joints based on attributes values and guides. (without positioning as this point). """
        self.neck_root_jnt = self.add_joint(name="neck_root", skinning_jnt=True, tag_parent_jnt=None, radius=0.7)

        # ribbon driver joints.
        self.ribbon_driver_jnts = [
            self.add_joint(name="ribbon_driver_01", skinning_jnt=False, tag_parent_jnt=None, radius=0.5),
            self.add_joint(name="ribbon_driver_02", skinning_jnt=False, tag_parent_jnt=None, radius=0.5),
            self.add_joint(name="ribbon_driver_03", skinning_jnt=False, tag_parent_jnt=None, radius=0.5),
        ]

        # ribbon driven joints.
        self.ribbon_driven_jnts = []
        parent = self.neck_root_jnt
        for index in range(self.ribbon_joints_attr.value):
            name = "ribbon_driven_{0}".format(index)
            ribbon_jnt = self.add_joint(name=name, skinning_jnt=True, tag_parent_jnt=parent, radius=0.25)
            parent = ribbon_jnt
            self.ribbon_driven_jnts.append(ribbon_jnt)

        self.head_jnt = self.add_joint(name="head", skinning_jnt=True, tag_parent_jnt=parent, radius=0.7)

        # humanIK definition.
        self.neck_root_jnt.human_ik = "Neck"
        self.head_jnt.human_ik = "Head"

        neck_tags = ["Neck{0}".format(index) for index in range(1, 10)]
        for jnt, tag in zip(self.ribbon_driven_jnts, neck_tags):
            jnt.human_ik = tag

    def ctrls_creation(self):
        """Create controls based on attributes values, guides and joints. (without positioning as this point). """
        scale_mult = self.ctrls_scale_attr.value * 3.5

        self.neck_root_ctrl = self.add_ctrl(name="neck_root", shape="circle", size=(2.5 * scale_mult))

        self.neck_mid_ctrl = self.add_ctrl(name="neck_mid", shape="circle", size=(1.5 * scale_mult))
        self.neck_mid_ctrl.line_width = 1.5

        for attr in ["scaleX", "scaleY", "scaleZ"]:
            self.neck_mid_ctrl.add_locked_hidden_attr(attr)

        head_scale = 3.2 * scale_mult
        self.head_ctrl = self.add_ctrl(name="head", shape="circle", up_orient="-Z", size=head_scale)
        self.head_ctrl.translate_offset = [0, head_scale / 2, 0]

        attrs = ["scaleY", "scaleZ"]
        if self.translate_ctrl_attr.value is False:
            attrs = ["translateX", "translateY", "translateZ", "scaleY", "scaleZ"]

        for attr in attrs:
            self.neck_root_ctrl.add_locked_hidden_attr(attr)
            self.head_ctrl.add_locked_hidden_attr(attr)

        self.neck_root_secondary_ctrl = None
        self.head_secondary_ctrl = None
        if self.secondary_ctrls_attr.value:
            self.neck_root_secondary_ctrl = self.add_ctrl(name="neck_root_secondary", size=(2.2 * scale_mult))
            self.neck_root_secondary_ctrl.color = SECONDARY_COLOR

            head_sec_scale = 2.8 * scale_mult
            self.head_secondary_ctrl = self.add_ctrl(name="head_secondary", up_orient="-Z", size=head_sec_scale)
            self.head_secondary_ctrl.translate_offset = [0, head_sec_scale / 2, 0]
            self.head_secondary_ctrl.color = SECONDARY_COLOR

            attrs = ["scaleX", "scaleY", "scaleZ"]
            if self.translate_ctrl_attr.value is False:
                attrs = ["translateX", "translateY", "translateZ", "scaleX", "scaleY", "scaleZ"]

            for attr in attrs:
                self.neck_root_secondary_ctrl.add_locked_hidden_attr(attr)
                self.head_secondary_ctrl.add_locked_hidden_attr(attr)

        # pin ctrl.
        self.pin_ctrl = None
        if self.pin_ctrl_attr.value:
            self.pin_ctrl = self.add_ctrl(name="pin", shape="box", size=(1.25 * scale_mult))
            self.pin_ctrl.line_width = 2

            for attr in ["scaleX", "scaleY", "scaleZ"]:
                self.pin_ctrl.add_locked_hidden_attr(attr)

        self.ribbon_ctrls = []
        if self.ribbon_ctrls_attr.value:
            for index in range(self.ribbon_joints_attr.value):
                ctrl = self.add_ctrl(
                    name="ribbon_micro_{0}".format(index), size=(1.05 * scale_mult), shape="octagon",
                )
                self.ribbon_ctrls.append(ctrl)

        self.bezier_ctrls_list = []
        if self.ribbon_bezier_attr.value is True:
            self.bezier_ctrls_list = create_bezier_ctrls(
                class_=self,
                scale_mult=scale_mult,
                name="head_ribbon_bezier",
                driver_jnts_count=len(self.ribbon_driver_jnts),
            )

        # humanIK definition ctrls.
        self.neck_root_ctrl.human_ik = "Neck"
        self.neck_mid_ctrl.human_ik = "Neck1"
        self.head_ctrl.human_ik = "Head"

    def maya_attrs_creation(self):
        """Declare any Maya attributes that users should be able to modify. """
        neck_ctrl = self.neck_root_ctrl

        neck_ctrl.add_maya_attr(name="neck_mid_ctrl", attr_type="bool", default_value=False)

        if self.ribbon_ctrls_attr.value:
            neck_ctrl.add_maya_attr(name="ribbon_micro_ctrls", attr_type="bool", default_value=False)

        if self.ribbon_bezier_attr.value:
            neck_ctrl.add_maya_attr(name="bezier_ctrls", attr_type="bool", default_value=False)

        self.neck_root_ctrl.add_maya_attr(name="auto_twist", attr_type="float", default_value=1, min=0, max=1)

        if self.volume_attr.value:
            neck_ctrl.add_maya_attr(name="auto_volume", attr_type="float", default_value=0, min=0, max=1)
            neck_ctrl.add_maya_attr(name="gradual_volume", attr_type="float", default_value=1, min=0, max=1)
            neck_ctrl.add_maya_attr(name="gradual_intensity", attr_type="float", default_value=0, min=-10, max=10)
            neck_ctrl.add_maya_attr(name="gradual_spread", attr_type="float", default_value=0, min=-10, max=10)

    def rig_creation(self):
        """Based on attributes value, guides (which now you can get global position from) joints and controls
        created in their methods you can build the rig.
        """
        ctrls_scale = self.ctrls_scale_attr.value

        if self.is_mirrored:
            self.module_grp.set_attr("scaleX", -1)

        grps = create_grps(self, ["input_root_grp", "output_root_grp", "output_tip_grp"])
        input_root_grp, output_root_grp, output_tip_grp = grps

        self.driven_attr.set_maya_object(input_root_grp)
        self.driver_root_attr.set_maya_object(output_root_grp)
        self.driver_tip_attr.set_maya_object(output_tip_grp)

        self.ctrls_grp, self.jnts_grp = create_grps(self, ["ctrls_grp", "jnts_grp"])

        neck_root_jnt = self.neck_root_jnt.pointer
        head_jnt = self.head_jnt.pointer

        neck_root_ctrl = self.neck_root_ctrl.pointer
        neck_mid_ctrl = self.neck_mid_ctrl.pointer
        head_ctrl = self.head_ctrl.pointer
        head_ctrl.set_attr("rotateOrder", 1)  # YZX has less gimble lock for head.

        ### position joints offset grps.
        head_jnt.set_attr("rotateOrder", 1)
        neck_root_jnt.parent_relative(self.jnts_grp)
        head_jnt.parent_relative(self.jnts_grp)

        neck_root_jnt.set_matrix(self.neck_root_guide.world_transformations["matrix"], space="world")
        neck_root_jnt.freeze_transformations()
        neck_root_jnt.offset_grp = neck_root_jnt.add_group_above(
            "{0}_offset_grp".format(neck_root_jnt.short_name),
            False,
        )
        neck_root_jnt.add_joint_orient()

        head_jnt.set_matrix(self.head_guide.world_transformations["matrix"], space="world")
        head_jnt.freeze_transformations()
        head_jnt.offset_grp = head_jnt.add_group_above("{0}_offset_grp".format(head_jnt.short_name), False)
        head_jnt.add_joint_orient()

        neck_root_ctrl.add_spacer_attr()

        # setup secondary ctrls.
        ctrls = [self.neck_root_ctrl, self.head_ctrl]
        secondery_ctrls = [self.neck_root_secondary_ctrl, self.head_secondary_ctrl]
        secondary_ctrls_setup(ctrls, secondery_ctrls)

        if self.expose_rotation_order_attr.value:
            expose_rotation_order(ctrls + secondery_ctrls + [self.neck_mid_ctrl, self.pin_ctrl])

        neck_root_ctrl.offset_grp.parent_relative(self.ctrls_grp)
        neck_mid_ctrl.offset_grp.parent_relative(neck_root_ctrl.btm_ctrl)
        head_ctrl.offset_grp.parent_relative(neck_root_ctrl.btm_ctrl)

        # create ribbons setup.
        length_a = math_utils.distance_between(
            self.neck_root_guide.world_transformations["translate"],
            self.neck_mid_guide.world_transformations["translate"],
        )
        length_b = math_utils.distance_between(
            self.neck_mid_guide.world_transformations["translate"],
            self.head_guide.world_transformations["translate"],
        )

        ribbon = ComplexRibbon(
            driver_joints=[jnt.pointer for jnt in self.ribbon_driver_jnts],
            driven_joints=[jnt.pointer for jnt in self.ribbon_driven_jnts],
            rest_length=length_a + length_b,
            name_prefix="{0}_neck_ribbon".format(self.name),
            parent_to=self.module_grp,
            is_mirrored=self.is_mirrored,
        )

        ## ribbon features.
        neck_mid_vis_attr = neck_root_ctrl.add_attr("neck_mid_ctrl", at="bool", k=True, dv=0)

        if self.ribbon_ctrls_attr.value is True:
            ribbon_ctrls_vis_attr = neck_root_ctrl.add_attr("ribbon_micro_ctrls", at="bool", k=True, dv=0)

        if self.ribbon_bezier_attr.value is True:
            bezier_attr = neck_root_ctrl.add_attr("bezier_ctrls", at="bool", k=True, dv=0)

        neck_root_ctrl.add_spacer_attr()
        auto_twist_attr = neck_root_ctrl.add_attr("auto_twist", min=0, max=1, dv=1, k=True)

        # volume setup.
        if self.volume_attr.value:
            module_scale_attr = create_module_scale(
                parent_to=neck_root_ctrl.btm_ctrl,
                name_prefix=self.name,
            )

            vol_attrs = ribbon.auto_manual_volume_setup(
                attrs_node=neck_root_ctrl,
                module_scale_attr=module_scale_attr,
                count=len(ribbon.driven_joints),
            )

            length = len(ribbon.driven_joints)
            first_half_size = (length // 2) + (length % 2)
            first_half = ribbon.driven_joints[:first_half_size]
            second_half = ribbon.driven_joints[first_half_size:]
            for joints in [first_half, second_half[::-1]]:
                for vol_attr, jnt in zip(vol_attrs, joints):
                    jnt.volume_grp = jnt.add_group_above(name="{0}_volume_grp".format(jnt.short_name))
                    jnt.volume_grp.connect_attr("scaleX", vol_attr)
                    jnt.volume_grp.connect_attr("scaleZ", vol_attr)

        if self.ribbon_ctrls_attr.value:
            ribbon.micro_ctrls_setup(
                driven_ctrls=[ctrl.pointer for ctrl in self.ribbon_ctrls],
                parent_to=neck_root_ctrl,
                vis_attr=ribbon_ctrls_vis_attr,
            )

        # bezier setup.
        if self.ribbon_bezier_attr.value is True:
            bezier_ctrls = []
            for info_lists in self.bezier_ctrls_list:
                ctrls = []
                for info in info_lists:
                    ctrls.append(info.pointer)

                bezier_ctrls.append(ctrls)

            ribbon.bezier_setup(
                bezier_ctrls=bezier_ctrls,
                ctrls_offset=[value * ctrls_scale for value in self.bezier_offset_attr.value],
                vis_attr=bezier_attr,
            )
            ribbon.ctrls_grp.parent_relative(neck_root_ctrl)

        ## ribbon ends driver joints to aim at middle driver joint.
        ribbon.aim_root_driver_jnts(object_orient=neck_root_jnt)
        aim_constraint = ribbon.aim_tip_driver_jnts(object_orient=neck_root_jnt)

        add_matrix_node = mc.createNode("wtAddMatrix", name="{0}_aim_switch_wtAddMatrix".format(self.name))
        mc.connectAttr(
            "{0}.worldMatrix[0]".format(neck_root_jnt),
            "{0}.wtMatrix[0].matrixIn".format(add_matrix_node),
        )
        mc.connectAttr(
            "{0}.worldMatrix[0]".format(head_jnt),
            "{0}.wtMatrix[1].matrixIn".format(add_matrix_node),
        )

        reverse_node = mc.createNode("reverse", name="{0}_auto_twist_reverse".format(self.name))
        mc.connectAttr(auto_twist_attr, "{0}.inputX".format(reverse_node))

        mc.connectAttr(auto_twist_attr, "{0}.wtMatrix[0].weightIn".format(add_matrix_node))
        mc.connectAttr("{0}.outputX".format(reverse_node), "{0}.wtMatrix[1].weightIn".format(add_matrix_node))

        mc.connectAttr("{0}.matrixSum".format(add_matrix_node), "{0}.worldUpMatrix".format(aim_constraint), f=True)

        ### position ctrls.
        ribbon.top_grp.match_transformation_to(neck_root_jnt)
        self.ctrls_grp.match_translation_to(neck_root_jnt)
        world_rotation(
            obj=self.ctrls_grp,
            aim_direction=self.world_orientation_attr.display_value,
            twist=self.world_twist_attr.value,
        )

        neck_mid_ctrl.offset_grp.set_attr("translateY", length_a)
        head_ctrl.offset_grp.set_attr("translateY", length_a + length_b)
        neck_root_jnt_pos = neck_root_jnt.get_matrix()
        head_jnt_pos = head_jnt.get_matrix()

        # position and connect ribbon.
        matrix_constraint(
            driver=neck_root_ctrl.btm_ctrl,
            driven=self.ribbon_driver_jnts[0].pointer.offset_grp,
            maintain_offset=False,
            skip_attrs=(False, False, False, False, False, False, True, True, True),
        )
        neck_root_jnt.parent_constraint_to(neck_root_ctrl.btm_ctrl, maintainOffset=False)

        matrix_constraint(
            driver=head_ctrl.btm_ctrl,
            driven=self.ribbon_driver_jnts[2].pointer.offset_grp,
            maintain_offset=False,
            skip_attrs=(False, False, False, False, False, False, True, True, True),
        )
        head_jnt.parent_constraint_to(head_ctrl.btm_ctrl, maintainOffset=False)
        head_jnt.scale_constraint_to(head_ctrl.btm_ctrl, maintainOffset=False)

        if self.clean_transformations_attr.value is True:
            neck_root_ctrl.offset_grp.set_matrix(neck_root_jnt_pos)
            head_ctrl.offset_grp.set_matrix(head_jnt_pos)
            neck_mid_ctrl.offset_grp.set_matrix(self.neck_mid_guide.world_transformations["matrix"])
            self.connect_mid_driver_ctrl(vis_attr=neck_mid_vis_attr, total_distance=length_a + length_b)

            if self.pin_ctrl:
                self.pin_ctrl_setup()

        else:
            if self.pin_ctrl:
                self.pin_ctrl_setup()

            self.connect_mid_driver_ctrl(vis_attr=neck_mid_vis_attr, total_distance=length_a + length_b)
            neck_root_ctrl.set_matrix(neck_root_jnt_pos)
            head_ctrl.set_matrix(head_jnt_pos)
            neck_mid_ctrl.set_matrix(self.neck_mid_guide.world_transformations["matrix"])

            if self.pin_ctrl:
                self.pin_ctrl.pointer.match_transformation_to(neck_mid_ctrl.offset_grp)

        neck_root_ctrl.scale_attrs_connect()
        head_ctrl.scale_attrs_connect()

        self.stable_twist_setup(ribbon, attr=auto_twist_attr)
        ribbon.update_default_arch_length()

        ribbon.jnts_grp.parent(self.jnts_grp)
        self.jnts_grp.scale_constraint_to(neck_root_ctrl.btm_ctrl, maintainOffset=False)

        input_root_grp.match_transformation_to(self.ctrls_grp)
        matrix_constraint(driver=input_root_grp, driven=self.ctrls_grp, maintain_offset=True)

        matrix_constraint(driver=neck_root_jnt, driven=output_root_grp, maintain_offset=False)
        matrix_constraint(driver=head_jnt, driven=output_tip_grp, maintain_offset=False)

    def pin_ctrl_setup(self):
        """Create attr on neck_mid_ctrl that can switch it to be driven by a pin_ctrl. """
        neck_mid_ctrl = self.neck_mid_ctrl.pointer
        pin_ctrl = self.pin_ctrl.pointer

        pin_ctrl.offset_grp.parent_relative(self.ctrls_grp)
        pin_ctrl.offset_grp.match_translation_to(neck_mid_ctrl.offset_grp)

        switch_grp = neck_mid_ctrl.add_group_above("{0}_pin_space_switch_grp".format(self.name))
        pin_space_offset_grp = IoTransform("{0}_pin_space_offset_grp".format(neck_mid_ctrl.short_name))
        pin_space_offset_grp.parent_relative(pin_ctrl)
        pin_space_offset_grp.match_transformation_to(switch_grp)

        pin_space_grp = IoTransform("{0}_pin_space_grp".format(neck_mid_ctrl.short_name))
        pin_space_grp.parent_relative(pin_space_offset_grp)

        neck_mid_ctrl.add_spacer_attr()
        pin_attr = neck_mid_ctrl.add_attr("pin", keyable=True, min=0, max=1, dv=0)
        reverse_node = mc.createNode("reverse", name="{0}_pin_attr_reverse".format(self.name))
        mc.connectAttr(pin_attr, "{0}.inputX".format(reverse_node))
        pin_attr_reverse = "{0}.outputX".format(reverse_node)

        constraint = mc.parentConstraint(
            [neck_mid_ctrl.offset_grp, pin_space_grp],
            switch_grp,
            maintainOffset=False,
        )[0]

        parent_space_attr, pin_space_attr = mc.parentConstraint(constraint, q=True, weightAliasList=True)
        mc.connectAttr(pin_attr_reverse, "{0}.{1}".format(constraint, parent_space_attr))
        mc.connectAttr(pin_attr, "{0}.{1}".format(constraint, pin_space_attr))
        pin_ctrl.offset_grp.connect_attr("visibility", pin_attr)

    def connect_mid_driver_ctrl(self, vis_attr, total_distance):
        """Constrain neck_mid_ctrl to drive mid driver_jnt position aim at end driver joint.
        copied from 'ComplexRibbon' to add support for maintaining offset.

        Arguments:
            vis_attr {str} -- long path to attr that will drive the vis of the ctrl
            total_distance {float} -- ribbon total length
        """
        neck_mid_ctrl = self.neck_mid_ctrl.pointer
        maintain_offset = self.clean_transformations_attr.value

        matrix_constraint(
            driver=neck_mid_ctrl,
            driven=self.ribbon_driver_jnts[1].pointer.offset_grp,
            maintain_offset=False,
        )

        follow_a = self.ribbon_driver_jnts[0].pointer.offset_grp
        follow_b = self.ribbon_driver_jnts[-1].pointer.offset_grp
        follow_a_pos = mc.xform(follow_a, q=True, ws=True, t=True)
        ctrl_pos = mc.xform(neck_mid_ctrl, q=True, ws=True, t=True)

        mc.pointConstraint([follow_a, follow_b], neck_mid_ctrl.offset_grp, maintainOffset=maintain_offset)

        if maintain_offset is False:
            follow_b_weight = math_utils.distance_between(follow_a_pos, ctrl_pos) / total_distance
            mc.pointConstraint(follow_b, neck_mid_ctrl.offset_grp, e=True, w=follow_b_weight)
            mc.pointConstraint(follow_a, neck_mid_ctrl.offset_grp, e=True, w=(1.0-follow_b_weight))

        mc.aimConstraint(
            self.ribbon_driver_jnts[-1].pointer.offset_grp,
            neck_mid_ctrl.offset_grp,
            aimVector=(0, 1, 0),
            upVector=(0, 0, 1),
            worldUpType="objectrotation",
            worldUpVector=(0, 0, 1),
            worldUpObject=self.neck_root_ctrl.pointer.btm_ctrl,
            maintainOffset=maintain_offset,
        )
        neck_mid_ctrl.offset_grp.connect_attr("visibility", vis_attr)

    def stable_twist_setup(self, ribbon, attr):
        """Create a stable twist setup using matrix nodes to get the correct twist of the joints.

        Args:
            ribbon (ComplexRibbon): the ribbon that it's driven jnts will twist
            attr (str): long path to attr to drive twist
        """
        neck_root_jnt = self.neck_root_jnt.pointer
        head_jnt = self.head_jnt.pointer

        twist_tip_attr = ribbon.add_twist_from_tip()

        twist_base_loc = IoTransform(mc.spaceLocator(n="{0}_twist_base_loc".format(self.name))[0], existing=True)
        twist_tip_loc = IoTransform(mc.spaceLocator(n="{0}_twist_tip_loc".format(self.name))[0], existing=True)

        twist_base_loc.parent_relative(neck_root_jnt)
        twist_tip_loc.parent_relative(head_jnt)

        twist_base_loc.set_attr("rotateZ", 90)
        twist_tip_loc.set_attr("rotateZ", 90)

        mult_matrix = mc.createNode("multMatrix", name="{0}_twist_base_multMatrix".format(self.name))
        mc.connectAttr(twist_tip_loc.attr("worldMatrix[0]"), "{0}.matrixIn[0]".format(mult_matrix))
        mc.connectAttr(twist_base_loc.attr("worldInverseMatrix[0]"), "{0}.matrixIn[1]".format(mult_matrix))

        decomp_matrix = mc.createNode("decomposeMatrix",name="{0}_twist_base_decomposeMatrix".format(self.name))
        mc.connectAttr("{0}.matrixSum".format(mult_matrix), "{0}.inputMatrix".format(decomp_matrix))

        quat_to_euler = mc.createNode("quatToEuler", name="{0}_twist_base_quatToEuler".format(self.name))
        mc.connectAttr("{0}.outputQuatX".format(decomp_matrix), "{0}.inputQuatX".format(quat_to_euler))
        mc.connectAttr("{0}.outputQuatW".format(decomp_matrix), "{0}.inputQuatW".format(quat_to_euler))

         # create mult node and connect to attr.
        enable_mult_node = mc.createNode(MULT_DL, name="{0}_twist_enable_mult".format(self.name))
        mc.connectAttr("{0}.outputRotateX".format(quat_to_euler), "{0}.{1}".format(enable_mult_node, MULT_DL_INPUT1))
        mc.connectAttr(attr, "{0}.{1}".format(enable_mult_node, MULT_DL_INPUT2))

        mult_node = mc.createNode(MULT_DL, name="{0}_twist_base_mult".format(self.name))
        mc.connectAttr("{0}.output".format(enable_mult_node), "{0}.{1}".format(mult_node, MULT_DL_INPUT1))
        mc.connectAttr("{0}.output".format(mult_node), twist_tip_attr)

        if ribbon.is_mirrored:
            mc.setAttr("{0}.{1}".format(mult_node, MULT_DL_INPUT2), -1)

        else:
            mc.setAttr("{0}.{1}".format(mult_node, MULT_DL_INPUT2), 1)

        twist_base_loc.hide()
        twist_tip_loc.hide()
