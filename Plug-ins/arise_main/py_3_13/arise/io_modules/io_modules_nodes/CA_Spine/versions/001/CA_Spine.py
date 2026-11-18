"""Cartoon_A_Spine module creates a cartoon_complex spine module. """

import maya.cmds as mc

from arise.utils.io_nodes.io_transform import IoTransform
from arise.data_types import node_data
from arise.utils import math_utils
from arise.utils.matrix_utils import matrix_constraint
from arise.utils.modules_utils import (
    world_rotation, create_module_scale, secondary_ctrls_setup, expose_rotation_order, create_grps,
    movable_pivot_setup, create_bezier_ctrls, SECONDARY_COLOR, update_ctrls,
)
from arise.utils.subcomponents.complex_ribbon import ComplexRibbon

MAYA_VERSION = 2016  # the version of maya from which this module supports.
AUTHOR = "Etay Herz"  # name of person who created this module.
RIG_CATEGORY = "Cartoon"  # either 'Basic', 'Cartoon', 'Vfx', 'Game' or 'All'. (used when filtering).
RIG_TYPE = "Biped"  # Biped, Car, Quadruped, All, ... (for filtering modules in lists).
TAGS = ["cartoon", "complex", "advance", "ribbon", "bendy bones", "ik", "fk", "spine"]
TOOL_TIP = "Cartoon spine with IK/FK, bendy bones, bezier ctrls, manual/auto volume, moveable pivot, and more."

IK_FK_SWITCH_ATTR = "ik_fk_switch"

node_data.NodeData.update_ctrls = update_ctrls


class CA_Spine(node_data.NodeData):
    """Cartoon_A_Spine module creates a cartoon_complex spine module. """
    sort_priority = 100

    def __init__(self, parent, docs, icon, module_dict):
        node_data.NodeData.__init__(
            self,
            parent=parent,
            icon=icon,
            docs=docs,
            module_dict=module_dict,
        )

        self.body_part = "spine"

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
            default_value=items.index("+Y"),  # Spine points up.
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
        self.volume_attr = self.add_boolean_attribute(
            name="Volume",
            default_value=True,
            annotation="Adds 'Auto Volume' and 'Manual Volume' attributes.",
        )

        self.pivot_attr = self.add_boolean_attribute(
            name="Movable Pivots",
            default_value=True,
            annotation=(
                "Adds a movable pivot to 'cog_ctrl' and 'pelvis_ctrl'.\n"
                "similar to the attachment 'MovablePivot'."
            ),
        )

        self.ik_follow_attr = self.add_boolean_attribute(
            name="IK Ctrls Follow",
            default_value=True,
            annotation="IK ctrls will aim at their next ctrl and move with 'base_ctrl' and 'chest_ctrl'.",
        )

        self.ctrls_count_attr = self.add_integer_attribute(
            name="IK FK Ctrls Count",
            default_value=1,
            dynamic_attribute=False,
            writable=True,
            readable=True,
            promoted=False,
            annotation="The number of middle ctrls between 'base_ctrl' and 'chest_ctrl' for both IK and FK.",
            min_value=1,
            max_value=10,
            add_slider=True,
        )

        ### ribbons settings.
        self.add_collapsible_layout(title="Ribbon Settings", shown=True)
        self.ribbon_joints_attr = self.add_integer_attribute(
            name="Ribbon Joints",
            default_value=5,
            dynamic_attribute=False,
            writable=True,
            readable=True,
            promoted=False,
            annotation="The number of skinning joints the spine has besides the 'pelvis_jnt' and 'chest_jnt'",
            help_link="https://youtu.be/-1fpRw6oJME?t=198",
            min_value=3,
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
            default_value=True,
            annotation="Add ctrls that deform the ribbon like a Bezier curve.",
            help_link="https://youtu.be/-1fpRw6oJME?t=222",
        )
        self.bezier_offset_attr = self.add_xyz_attribute(
            name="Bezier Ctrls Offset",
            default_value=[0, 0, -22],
            dynamic_attribute=False,
            writable=True,
            readable=True,
            promoted=False,
            annotation="Position offset of bezier ctrls from the ribbon.\nmultiplied by attribute 'Ctrls Scale'.",
        )
        self.close_layout()

        ### connections.
        self.add_separator(title="Connections")
        self.driven_root_attr = self.add_driven_attribute(name="Root Input", annotation="Input")
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
        self.cog_guide = self.add_guide(
            name="COG",
            translation=(0, 99, 0),
        )
        self.cog_guide.size = self.cog_guide.size * 6.0
        self.cog_guide.shape = "square"

        self.spine_base_guide = self.add_aim_guide(
            name="spine_base",
            translation=(0, 103, 0),
            parent=self.cog_guide,
            side_pin_rotation=(0, 0, 0),
            side_pin_guide=None,
        )

        parent = self.spine_base_guide
        self.guides_list = []
        pos = [0, 114, 0]
        for index in range(self.ctrls_count_attr.value):
            guide = self.add_aim_guide(
                name="spine_{0}".format(index+1),
                translation=pos,
                parent=parent,
                side_pin_rotation=(0, 0, 0),
                side_pin_guide=self.spine_base_guide if self.guides_up_shared_attr.value else None,
            )

            pos = [pos[0], pos[1]+11.0, pos[2]]
            self.guides_list.append(guide)
            parent = guide

        self.chest_guide = self.add_guide(
            name="chest",
            translation=pos,
            parent=parent,
        )
        self.chest_guide.size = self.chest_guide.size * 5.5

        # aim guides at each other.
        self.spine_base_guide.aim_at = self.guides_list[0]

        for index, guide in enumerate(self.guides_list[:-1]):
            guide.aim_at = self.guides_list[index+1]

        self.guides_list[-1].aim_at = self.chest_guide

    def joints_creation(self):
        """Create joints based on attributes values and guides. (without positioning as this point). """
        self.pelvis_jnt = self.add_joint(name="pelvis", skinning_jnt=True, tag_parent_jnt=None, radius=0.95)

        # driven joints.
        self.driven_joints_list = []
        parent_tag = self.pelvis_jnt
        for index in range(self.ribbon_joints_attr.value):
            jnt = self.add_joint(
                name="ribbon_driven_{0}".format(index),
                skinning_jnt=True,
                tag_parent_jnt=parent_tag,
                radius=0.5,
            )
            parent_tag = jnt
            self.driven_joints_list.append(jnt)

        # driver joints.
        self.driver_joints_list = []
        for index in range(self.ctrls_count_attr.value + 2):
            jnt = self.add_joint(
                name="ribbon_driver_{0}".format(index),
                skinning_jnt=False,
                tag_parent_jnt=None,
                radius=0.75,
            )
            parent_tag = jnt
            self.driver_joints_list.append(jnt)

        # chest jnt.
        self.chest_jnt = self.add_joint(
            name="chest",
            skinning_jnt=True,
            tag_parent_jnt=self.driven_joints_list[-1],
            radius=0.95,
        )

        # humanIK definition.
        self.pelvis_jnt.human_ik = "Hips"
        human_ik_tags = ["Spine"] + ["Spine{0}".format(index) for index in range(1, 10)]
        for tag, jnt in zip(human_ik_tags, self.driven_joints_list + [self.chest_jnt]):
            jnt.human_ik = tag

        if not self.chest_jnt.human_ik:
            self.chest_jnt.human_ik = "Spine9"

    def ctrls_creation(self):
        """Create controls based on attributes values, guides and joints. (without positioning as this point). """
        scale_mult = self.ctrls_scale_attr.value * 3.5
        ctrl_size = 4.0 * scale_mult

        self.cog_ctrl = self.add_ctrl(name="cog", shape="pelvis", size=(7.0 * scale_mult))
        self.cog_ctrl.line_width = 3.0

        self.pelvis_ctrl = self.add_ctrl(name="pelvis", shape="octagon", size=(6.0 * scale_mult))
        self.spine_base_ctrl = self.add_ctrl(name="base", shape="square", size=ctrl_size)

        size = [ctrl_size, ctrl_size/1.5, ctrl_size/1.2]
        self.ik_chest_ctrl = self.add_ctrl(name="ik_chest", shape="box", size=size)
        self.ik_chest_ctrl.translate_offset = [0, ctrl_size/1.5, 0]

        self.fk_chest_ctrl = self.add_ctrl(name="fk_chest", shape="box", size=size)
        self.fk_chest_ctrl.translate_offset = [0, ctrl_size/1.5, 0]

        ctrls = [self.cog_ctrl, self.pelvis_ctrl, self.ik_chest_ctrl, self.fk_chest_ctrl, self.spine_base_ctrl]
        for ctrl in ctrls:
            for attr in ["scaleY", "scaleZ"]:
                ctrl.add_locked_hidden_attr(attr)

        self.spine_base_ctrl.add_locked_hidden_attr("scaleX")

        self.cog_secondary_ctrl = []
        self.pelvis_secondary_ctrl = []
        self.base_secondary_ctrl = []
        self.chest_secondary_ctrls = []
        if self.secondary_ctrl_attr.value:
            self.cog_secondary_ctrl = self.add_ctrl(name="cog_secondary", shape="pelvis", size=(6.7 * scale_mult))
            self.cog_secondary_ctrl.line_width = 3.0
            self.cog_secondary_ctrl.color = SECONDARY_COLOR

            self.pelvis_secondary_ctrl = self.add_ctrl(
                name="pelvis_secondary",
                shape="octagon",
                size=(5.7 * scale_mult),
            )
            self.pelvis_secondary_ctrl.color = SECONDARY_COLOR

            self.base_secondary_ctrl = self.add_ctrl(
                name="base_secondary",
                shape="square",
                size=(0.95 * ctrl_size),
            )
            self.base_secondary_ctrl.color = SECONDARY_COLOR

            ik_chest_secondary = self.add_ctrl(
                name="ik_chest_secondary",
                shape="square",
                size=(0.77 * ctrl_size),
            )
            ik_chest_secondary.color = SECONDARY_COLOR

            fk_chest_secondary = self.add_ctrl(
                name="fk_chest_secondary",
                shape="square",
                size=(0.77 * ctrl_size),
            )
            fk_chest_secondary.color = SECONDARY_COLOR
            self.chest_secondary_ctrls = [ik_chest_secondary, fk_chest_secondary]

            ctrls = [
                self.cog_secondary_ctrl, self.pelvis_secondary_ctrl, self.base_secondary_ctrl,
                ik_chest_secondary, fk_chest_secondary,
            ]
            for ctrl in ctrls:
                for attr in ["scaleX", "scaleY", "scaleZ"]:
                    ctrl.add_locked_hidden_attr(attr)

        # ik/fk ctrls.
        self.ik_ctrls_list = []
        self.fk_ctrls_list = []
        self.ik_secondary_ctrls = []
        self.fk_secondary_ctrls = []
        self.mid_ctrls_list = []
        for index in range(self.ctrls_count_attr.value):
            ik_ctrl = self.add_ctrl(name="ik_{0}".format(index), shape="square_with_arrow", size=ctrl_size)
            ik_ctrl.rotate_offset = [180, 0, 0]
            self.ik_ctrls_list.append(ik_ctrl)

            fk_ctrl = self.add_ctrl(name="fk_{0}".format(index), shape="circle", size=ctrl_size)
            self.fk_ctrls_list.append(fk_ctrl)

            if self.secondary_ctrl_attr.value:
                ik_secondary_ctrl = self.add_ctrl(
                    name="ik_{0}_secondary".format(index),
                    shape="square",
                    up_orient="+Y",
                    size=(0.90 * ctrl_size),
                )
                ik_secondary_ctrl.color = SECONDARY_COLOR
                self.ik_secondary_ctrls.append(ik_secondary_ctrl)

                fk_secondary_ctrl = self.add_ctrl(
                    name="fk_{0}_secondary".format(index),
                    shape="circle",
                    up_orient="+Y",
                    size=(0.90 * ctrl_size),
                )
                fk_secondary_ctrl.color = SECONDARY_COLOR
                self.fk_secondary_ctrls.append(fk_secondary_ctrl)

            mid_ctrl = self.add_ctrl(
                name="ribbon_mid_{0}".format(index),
                shape="box",
                size=[scale_mult*3, scale_mult/2, scale_mult*3],
            )
            mid_ctrl.line_width = 1.5
            self.mid_ctrls_list.append(mid_ctrl)

        all_secondary = self.ik_secondary_ctrls + self.fk_secondary_ctrls
        all_primary_ctrls = self.ik_ctrls_list + self.fk_ctrls_list + self.mid_ctrls_list
        for ctrl in all_primary_ctrls + all_secondary:
            for attr in ["scaleX", "scaleY", "scaleZ"]:
                ctrl.add_locked_hidden_attr(attr)

        self.ribbon_ctrls = []
        if self.ribbon_ctrls_attr.value:
            for index in range(self.ribbon_joints_attr.value):
                ctrl = self.add_ctrl(
                    name="ribbon_micro_{0}".format(index), size=(3.1 * scale_mult), shape="octagon",
                )
                self.ribbon_ctrls.append(ctrl)

        self.bezier_ctrls_list = []
        if self.ribbon_bezier_attr.value is True:
            self.bezier_ctrls_list = create_bezier_ctrls(
                class_=self,
                scale_mult=scale_mult,
                name="ribbon_bezier",
                driver_jnts_count=len(self.driver_joints_list),
            )

        # humanIK definition ctrls.
        self.cog_ctrl.human_ik = "Hips"
        self.ik_chest_ctrl.human_ik = "Chest"

        defintion_tags = ["Spine"] + ["Spine{0}".format(index) for index in range(1, 6)]
        for ik_ctrl, tag in zip(self.ik_ctrls_list, defintion_tags):
            ik_ctrl.human_ik = tag

    def maya_attrs_creation(self):
        """Declare any Maya attributes that users should be able to modify. """
        self.cog_ctrl.add_maya_attr(name="ik_fk_switch", attr_type="float", default_value=0, min=0, max=1)

        self.cog_ctrl.add_maya_attr(
            name="show_ik_ctrls", attr_type="enum", default_value=1, enum_names=["Off", "Auto", "On"],
        )
        self.cog_ctrl.add_maya_attr(
            name="show_fk_ctrls", attr_type="enum", default_value=1, enum_names=["Off", "Auto", "On"],
        )

        if self.pivot_attr.value:
            self.cog_ctrl.add_maya_attr(name="pivot", attr_type="bool", default_value=False)

        self.cog_ctrl.add_maya_attr(name="bendy_bones_ctrls", attr_type="bool", default_value=False)

        if self.ribbon_ctrls_attr.value:
            self.cog_ctrl.add_maya_attr(name="ribbon_micro_ctrls", attr_type="bool", default_value=False)

        if self.ribbon_bezier_attr.value:
            self.cog_ctrl.add_maya_attr(name="bezier_ctrls", attr_type="bool", default_value=False)

        if self.volume_attr.value:
            self.cog_ctrl.add_maya_attr(name="auto_volume", attr_type="float", default_value=0, min=0, max=1)
            self.cog_ctrl.add_maya_attr(name="gradual_volume", attr_type="float", default_value=1, min=0, max=1)
            self.cog_ctrl.add_maya_attr(name="gradual_intensity", attr_type="float", default_value=0, min=-10, max=10)
            self.cog_ctrl.add_maya_attr(name="gradual_spread", attr_type="float", default_value=0, min=-10, max=10)

        if self.pivot_attr.value:
            self.pelvis_ctrl.add_maya_attr(name="pivot", attr_type="bool", default_value=False)

    def rig_creation(self):
        """Based on attributes value, guides (which now you can get global position from) joints and controls
        created in their methods you can build the rig.
        """
        ctrls_scale = self.ctrls_scale_attr.value

        if self.is_mirrored:
            self.module_grp.set_attr("scaleX", -1)

        grps = create_grps(self, ["input_root_grp", "output_root_grp", "output_tip_grp"])
        input_root_grp, output_root_grp, output_tip_grp = grps

        self.driven_root_attr.set_maya_object(input_root_grp)
        self.driver_root_attr.set_maya_object(output_root_grp)
        self.driver_tip_attr.set_maya_object(output_tip_grp)

        self.ctrls_grp, self.jnts_grp = create_grps(self, ["ctrls_grp", "jnts_grp"])

        self.ctrls_grp.set_translation(self.cog_guide.world_transformations["translate"])

        self.chest_jnt.pointer.parent_relative(self.jnts_grp)
        self.pelvis_jnt.pointer.parent_relative(self.jnts_grp)

        cog_ctrl = self.cog_ctrl.pointer
        cog_ctrl.offset_grp.parent_relative(self.ctrls_grp)

        cog_ctrl.add_spacer_attr()
        ik_fk_switch_attr = cog_ctrl.add_attr(IK_FK_SWITCH_ATTR, min=0, max=1, dv=0, k=True)
        cog_ctrl.add_spacer_attr()
        ik_vis_attr = cog_ctrl.add_attr("show_ik_ctrls", keyable=False, at="enum", en="Off:Auto:On:", dv=1)
        mc.setAttr(ik_vis_attr, channelBox=True)
        fk_vis_attr = cog_ctrl.add_attr("show_fk_ctrls", keyable=False, at="enum", en="Off:Auto:On:", dv=1)
        mc.setAttr(fk_vis_attr, channelBox=True)

        ctrls = self.ik_ctrls_list + self.fk_ctrls_list + [self.cog_ctrl, self.pelvis_ctrl]
        ctrls += [self.spine_base_ctrl, self.ik_chest_ctrl, self.fk_chest_ctrl]
        secondary_ctrls = self.ik_secondary_ctrls + self.fk_secondary_ctrls + [self.cog_secondary_ctrl]
        secondary_ctrls += [self.pelvis_secondary_ctrl] + [self.base_secondary_ctrl] + self.chest_secondary_ctrls
        secondary_ctrls_setup(ctrls, secondary_ctrls)

        world_rotation(
            obj=self.ctrls_grp,
            aim_direction=self.world_orientation_attr.display_value,
            twist=self.world_twist_attr.value,
        )

        base_distance = math_utils.distance_between(
            self.cog_guide.world_transformations["translate"],
            self.spine_base_guide.world_transformations["translate"],
        )

        base_ctrl = self.spine_base_ctrl.pointer
        base_ctrl.offset_grp.parent_relative(cog_ctrl.btm_ctrl)
        base_ctrl.offset_grp.set_attr("translateY", base_distance)

        self.ik_ctrls_grp = IoTransform("ik_ctrls_grp")
        self.ik_ctrls_grp.parent_relative(cog_ctrl.btm_ctrl)

        self.fk_ctrls_grp = IoTransform("fk_ctrls_grp")
        self.fk_ctrls_grp.parent_relative(base_ctrl.btm_ctrl)

        self.mid_ctrls_grp = IoTransform("mid_ctrls_grp")
        self.mid_ctrls_grp.parent_relative(cog_ctrl.btm_ctrl)

        pelvis_ctrl = self.pelvis_ctrl.pointer
        pelvis_ctrl.offset_grp.parent_relative(base_ctrl.btm_ctrl)
        pelvis_ctrl.offset_grp.set_attr("translateY", base_distance * -1)

        fk_parent = self.fk_ctrls_grp
        from_pos = self.spine_base_guide.world_transformations["translate"]
        self.total_length = 0
        ctrls_list = [self.guides_list, self.ik_ctrls_list, self.fk_ctrls_list, self.mid_ctrls_list]
        for guide, ik_ctrl, fk_ctrl, mid_ctrl in zip(*ctrls_list):
            ik_ctrl = ik_ctrl.pointer
            fk_ctrl = fk_ctrl.pointer
            mid_ctrl = mid_ctrl.pointer

            length = math_utils.distance_between(from_pos, guide.world_transformations["translate"])
            self.total_length += length
            from_pos = guide.world_transformations["translate"]

            # mid.
            mid_ctrl.offset_grp.parent_relative(self.mid_ctrls_grp)
            mid_ctrl.offset_grp.set_attr("translateY", self.total_length + base_distance)

            # IK.
            ik_ctrl.offset_grp.parent_relative(self.ik_ctrls_grp)
            ik_ctrl.offset_grp.set_attr("translateY", self.total_length + base_distance)

            # FK.
            fk_ctrl.offset_grp.parent_relative(fk_parent)
            fk_ctrl.offset_grp.set_attr("translateY", length)
            fk_parent = fk_ctrl.btm_ctrl

        length = math_utils.distance_between(from_pos, self.chest_guide.world_transformations["translate"])
        self.total_length += length

        ik_chest_ctrl = self.ik_chest_ctrl.pointer
        ik_chest_ctrl.offset_grp.parent_relative(self.ik_ctrls_grp)
        ik_chest_ctrl.offset_grp.set_attr("translateY", base_distance + self.total_length)

        fk_chest_ctrl = self.fk_chest_ctrl.pointer
        fk_chest_ctrl.offset_grp.parent_relative(self.fk_ctrls_list[-1].pointer.btm_ctrl)
        fk_chest_ctrl.offset_grp.set_attr("translateY", length)

        if self.pivot_attr.value:
            if not self.cog_secondary_ctrl:
                cog_ctrl.add_spacer_attr()
                pelvis_ctrl.add_spacer_attr()

            movable_pivot_setup(cog_ctrl)
            movable_pivot_setup(pelvis_ctrl)

        if self.expose_rotation_order_attr.value:
            expose_rotation_order(ctrls + self.mid_ctrls_list + secondary_ctrls)

        # create ribbons setup.
        ribbon = ComplexRibbon(
            driver_joints=[jnt.pointer for jnt in self.driver_joints_list],
            driven_joints=[jnt.pointer for jnt in self.driven_joints_list],
            rest_length=self.total_length,
            name_prefix="{0}_ribbon".format(self.name),
            parent_to=self.module_grp,
            is_mirrored=self.is_mirrored,
        )

        ## ribbon features.
        cog_ctrl.add_spacer_attr()
        bendy_bones_attr = cog_ctrl.add_attr("bendy_bones_ctrls", attributeType="bool", k=True, dv=0)
        for ctrl in self.mid_ctrls_list:
            ctrl.pointer.offset_grp.connect_attr("visibility", bendy_bones_attr)

        if self.ribbon_ctrls_attr.value is True:
            ribbon_ctrls_vis_attr = cog_ctrl.add_attr("ribbon_micro_ctrls", attributeType="bool", k=True, dv=0)

        if self.ribbon_bezier_attr.value is True:
            bezier_attr = cog_ctrl.add_attr("bezier_ctrls", attributeType="bool", k=True, dv=0)

        # volume setup.
        if self.volume_attr.value:

            module_scale_attr = create_module_scale(
                parent_to=cog_ctrl.btm_ctrl,
                name_prefix=self.name,
            )

            vol_attrs = ribbon.auto_manual_volume_setup(
                attrs_node=cog_ctrl,
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
            ribbon.ctrls_grp.parent_relative(cog_ctrl)

        matrix_constraint(driver=pelvis_ctrl.btm_ctrl, driven=self.pelvis_jnt.pointer, maintain_offset=False)

        ribbon.top_grp.set_matrix(self.spine_base_guide.world_transformations["matrix"])
        ribbon.top_grp.set_scale([1, 1, 1])

        drivers = [base_ctrl.btm_ctrl] + [ctrl.pointer for ctrl in self.mid_ctrls_list]
        previous_jnt, previous_ctrl = None, None
        for jnt, driver in zip(self.driver_joints_list[0:-1], drivers):
            matrix_constraint(
                driver=driver,
                driven=jnt.pointer,
                maintain_offset=False,
                skip_attrs=(False, False, False, True, True, True, True, True, True),
            )

            if previous_jnt:
                previous_jnt.aim_constraint_to(
                    jnt.pointer,
                    aimVector=(0, 1, 0),
                    upVector=(1, 0, 0),
                    worldUpType="objectrotation",
                    worldUpVector=(1, 0, 0),
                    worldUpObject=previous_ctrl,
                    maintainOffset=False,
                )

            previous_jnt = jnt.pointer
            previous_ctrl = driver

        previous_jnt.aim_constraint_to(  # last jnt aims at chest jnt.
            self.driver_joints_list[-1].pointer,
            aimVector=(0, 1, 0),
            upVector=(1, 0, 0),
            worldUpType="objectrotation",
            worldUpVector=(1, 0, 0),
            worldUpObject=previous_ctrl,
            maintainOffset=False,
        )

        matrix_constraint(
            driver=self.chest_jnt.pointer,
            driven=self.driver_joints_list[-1].pointer,
            maintain_offset=False,
        )

        self._create_ik_fk_switch_connection(attrs=[ik_fk_switch_attr, ik_vis_attr, fk_vis_attr])

        if self.ik_follow_attr.value:
            self._ik_ctrls_follow()

        self._position_ctrls()

        if self.ribbon_ctrls_attr.value:
            ribbon.micro_ctrls_setup(
                driven_ctrls=[ctrl.pointer for ctrl in self.ribbon_ctrls],
                parent_to=cog_ctrl,
                vis_attr=ribbon_ctrls_vis_attr,
            )

        ribbon.update_default_arch_length()

        ribbon.jnts_grp.parent(self.jnts_grp)
        matrix_constraint(driver=cog_ctrl.btm_ctrl, driven=self.jnts_grp, maintain_offset=False)

        input_root_grp.match_transformation_to(self.ctrls_grp)
        matrix_constraint(driver=input_root_grp, driven=self.ctrls_grp, maintain_offset=True)
        matrix_constraint(driver=self.pelvis_jnt.pointer, driven=output_root_grp, maintain_offset=False)
        matrix_constraint(driver=self.chest_jnt.pointer, driven=output_tip_grp, maintain_offset=False)

        cog_ctrl.scale_attrs_connect()
        pelvis_ctrl.scale_attrs_connect()
        ik_chest_ctrl.scale_attrs_connect()
        fk_chest_ctrl.scale_attrs_connect()

    def _position_ctrls(self):
        """Position ctrls at guides positions. """
        cog_ctrl = self.cog_ctrl.pointer
        base_ctrl = self.spine_base_ctrl.pointer
        pelvis_ctrl = self.pelvis_ctrl.pointer
        ik_chest_ctrl = self.ik_chest_ctrl.pointer
        fk_chest_ctrl = self.fk_chest_ctrl.pointer

        if self.clean_transformations_attr.value:
            cog_ctrl.offset_grp.set_matrix(self.cog_guide.world_transformations["matrix"])
            cog_ctrl.offset_grp.set_scale([1, 1, 1])
            base_ctrl.offset_grp.set_matrix(self.spine_base_guide.world_transformations["matrix"])
            base_ctrl.offset_grp.set_scale([1, 1, 1])
            pelvis_ctrl.offset_grp.set_matrix(self.cog_guide.world_transformations["matrix"])
            pelvis_ctrl.offset_grp.set_scale([1, 1, 1])
            ik_chest_ctrl.offset_grp.set_matrix(self.chest_guide.world_transformations["matrix"])
            ik_chest_ctrl.offset_grp.set_scale([1, 1, 1])

        else:
            cog_ctrl.set_matrix(self.cog_guide.world_transformations["matrix"])
            cog_ctrl.set_scale([1, 1, 1])
            base_ctrl.set_matrix(self.spine_base_guide.world_transformations["matrix"])
            base_ctrl.set_scale([1, 1, 1])
            pelvis_ctrl.set_matrix(self.cog_guide.world_transformations["matrix"])
            pelvis_ctrl.set_scale([1, 1, 1])
            ik_chest_ctrl.set_matrix(self.chest_guide.world_transformations["matrix"])
            ik_chest_ctrl.set_scale([1, 1, 1])

        # FK ctrls.
        for fk_ctrl, guide in zip(self.fk_ctrls_list, self.guides_list):
            if self.clean_transformations_attr.value:
                fk_ctrl.pointer.offset_grp.set_matrix(guide.world_transformations["matrix"])
                fk_ctrl.pointer.offset_grp.set_scale([1, 1, 1])
            else:
                fk_ctrl.pointer.set_matrix(guide.world_transformations["matrix"])
                fk_ctrl.pointer.set_scale([1, 1, 1])

        # FK chest ctrl.
        if self.clean_transformations_attr.value:
            fk_chest_ctrl.offset_grp.set_matrix(self.chest_guide.world_transformations["matrix"])
            fk_chest_ctrl.offset_grp.set_scale([1, 1, 1])

        else:
            fk_chest_ctrl.set_matrix(self.chest_guide.world_transformations["matrix"])
            fk_chest_ctrl.set_scale([1, 1, 1])

        # IK ctrls.
        for ik_ctrl, guide in zip(reversed(self.ik_ctrls_list), reversed(self.guides_list)):
            if self.clean_transformations_attr.value:
                ik_ctrl.pointer.offset_grp.set_matrix(guide.world_transformations["matrix"])
                ik_ctrl.pointer.offset_grp.set_scale([1, 1, 1])
            else:
                ik_ctrl.pointer.set_matrix(guide.world_transformations["matrix"])
                ik_ctrl.pointer.set_scale([1, 1, 1])

    def _create_ik_fk_switch_connection(self, attrs):
        """Connect ik_fk_switch attr between ik and fk ctrls to drive mid_Ctrls.

        Arguments:
            attrs {list} -- of long path to attrs that will drive ik_fk_switch and vis
        """
        switch_attr, ik_vis_attr, fk_vis_attr = attrs
        reverse_node = mc.createNode("reverse", n="{0}_ik_fk_switch_reverse".format(self.name))
        mc.connectAttr(switch_attr, "{0}.inputX".format(reverse_node))
        reverse_attr = "{0}.outputX".format(reverse_node)

        # ctrls visibility connection.
        plus_minus = mc.createNode("plusMinusAverage", name="{0}_ik_fk_switch_PMA".format(self.name))
        remap_ik_vis = mc.createNode("remapValue", name="{0}_ik_fk_switch_ik_remapValue".format(self.name))
        remap_fk_vis = mc.createNode("remapValue", name="{0}_ik_fk_switch_fk_remapValue".format(self.name))

        mc.connectAttr(reverse_attr, "{0}.input3D[0].input3Dx".format(plus_minus))
        mc.connectAttr(switch_attr, "{0}.input3D[0].input3Dy".format(plus_minus))
        mc.setAttr("{0}.input3D[1].input3Dx".format(plus_minus), -1)
        mc.setAttr("{0}.input3D[1].input3Dy".format(plus_minus), -1)
        mc.connectAttr(ik_vis_attr, "{0}.input3D[2].input3Dx".format(plus_minus))
        mc.connectAttr(fk_vis_attr, "{0}.input3D[2].input3Dy".format(plus_minus))

        mc.setAttr("{0}.inputMin".format(remap_ik_vis), 1)
        mc.setAttr("{0}.inputMax".format(remap_ik_vis), 0)
        mc.setAttr("{0}.outputMin".format(remap_ik_vis), 5)
        mc.setAttr("{0}.outputMax".format(remap_ik_vis), 0)

        mc.setAttr("{0}.inputMin".format(remap_fk_vis), 0)
        mc.setAttr("{0}.inputMax".format(remap_fk_vis), 1)
        mc.setAttr("{0}.outputMin".format(remap_fk_vis), 0)
        mc.setAttr("{0}.outputMax".format(remap_fk_vis), 5)

        mc.connectAttr("{0}.output3Dx".format(plus_minus), "{0}.inputValue".format(remap_ik_vis))
        mc.connectAttr("{0}.outValue".format(remap_ik_vis), self.ik_ctrls_grp.attr("visibility"))

        mc.connectAttr("{0}.output3Dy".format(plus_minus), "{0}.inputValue".format(remap_fk_vis))
        mc.connectAttr("{0}.outValue".format(remap_fk_vis), self.fk_ctrls_grp.attr("visibility"))

        # constraints driven by switch attribute.
        for mid_ctrl, ik_ctrl, fk_ctrl in zip(self.mid_ctrls_list, self.ik_ctrls_list, self.fk_ctrls_list):
            drivers = [ik_ctrl.pointer.btm_ctrl, fk_ctrl.pointer.btm_ctrl]
            parent_constraint = mid_ctrl.pointer.offset_grp.parent_constraint_to(drivers, maintainOffset=False)
            ik_attr, fk_attr = mc.parentConstraint(parent_constraint, q=True, weightAliasList=True)
            mc.connectAttr(reverse_attr, "{0}.{1}".format(parent_constraint, ik_attr))
            mc.connectAttr(switch_attr, "{0}.{1}".format(parent_constraint, fk_attr))

        # chest ik and fk ctrls switch setup.
        parent_constraint = self.chest_jnt.pointer.parent_constraint_to(
            [self.ik_chest_ctrl.pointer.btm_ctrl, self.fk_chest_ctrl.pointer.btm_ctrl],
            maintainOffset=False,
        )
        ik_attr, fk_attr = mc.parentConstraint(parent_constraint, q=True, weightAliasList=True)
        mc.connectAttr(reverse_attr, "{0}.{1}".format(parent_constraint, ik_attr))
        mc.connectAttr(switch_attr, "{0}.{1}".format(parent_constraint, fk_attr))

        belnd_attrs_node = mc.createNode("blendTwoAttr", name="{0}_switch_chest_scale_blend".format(self.name))
        mc.connectAttr(self.ik_chest_ctrl.pointer.attr("scaleX"), "{0}.input[0]".format(belnd_attrs_node))
        mc.connectAttr(self.fk_chest_ctrl.pointer.attr("scaleX"), "{0}.input[1]".format(belnd_attrs_node))
        mc.connectAttr(switch_attr, "{0}.attributesBlender".format(belnd_attrs_node))

        for attr in ["scaleX", "scaleY", "scaleZ"]:
            mc.connectAttr("{0}.output".format(belnd_attrs_node), self.chest_jnt.pointer.attr(attr))

    def _ik_ctrls_follow(self):
        """IK ctrls, beside the first and last, parent constraint to first and last IK ctrls with weights
        based on their distance from them.
        """
        first_ik = self.spine_base_ctrl.pointer
        last_ik = self.ik_chest_ctrl.pointer

        all_ctrls = [self.spine_base_ctrl] + self.ik_ctrls_list + [self.ik_chest_ctrl]

        ctrls_pos_data = []
        last_pos = mc.xform(first_ik.offset_grp, q=True, ws=True, t=True)
        length = 0.0
        for ctrl_info in self.ik_ctrls_list:
            ctrl = ctrl_info.pointer
            follow_grp = ctrl.offset_grp.add_group_above("{0}_follow_grp".format(ctrl.short_name), False)
            ctrl_pos = mc.xform(ctrl.offset_grp, q=True, ws=True, t=True)
            length += math_utils.distance_between(last_pos, ctrl_pos)
            last_pos = ctrl_pos
            ctrls_pos_data.append([ctrl, ctrl.get_matrix(space="world")])

            # 2 constraints allow to maintain offset with different weights.
            offset = self.clean_transformations_attr.value
            last_ik_weight = length / self.total_length
            mc.pointConstraint(last_ik, follow_grp, maintainOffset=offset, w=last_ik_weight)
            mc.pointConstraint(first_ik, follow_grp, maintainOffset=offset, weight=(1.0-last_ik_weight))

            index = all_ctrls.index(ctrl_info)
            next_ctrl = all_ctrls[index+1].pointer
            mc.aimConstraint(
                next_ctrl.btm_ctrl,
                follow_grp,
                aimVector=(0, 1, 0),
                upVector=(0, 0, 1),
                worldUpVector=(0, 0, 1),
                worldUpType="objectrotation",
                worldUpObject=self.spine_base_ctrl.pointer,
                maintainOffset=self.clean_transformations_attr.value,
            )

        if self.clean_transformations_attr.value is False:
            for ctrl, pos in ctrls_pos_data:
                ctrl.set_matrix(pos, space="world")
