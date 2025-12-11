"""Cartoon_A_Ribbon module creates a cartoon_complex ribbon module. this is not a biped or quadruped module but
a generic module the user can choose to use
"""

from arise.utils.io_nodes.io_transform import IoTransform
from arise.data_types import node_data
from arise.utils import math_utils
from arise.utils.matrix_utils import matrix_constraint
from arise.utils.modules_utils import (
    world_rotation, create_module_scale, secondary_ctrls_setup, expose_rotation_order, create_grps,
    create_bezier_ctrls, SECONDARY_COLOR, update_ctrls
)
from arise.utils.subcomponents.complex_ribbon import ComplexRibbon

MAYA_VERSION = 2017  # the version of maya from which this module SHOULD supports.
AUTHOR = "Etay Herz"  # name of person who created this module.
RIG_CATEGORY = "Cartoon"  # either 'Basic', 'Cartoon', 'Vfx', 'Game' or 'All'. (used when filtering).
RIG_TYPE = "All"  # Biped, Car, Quadruped, All, ... (for filtering modules in lists).
TAGS = ["cartoon", "complex", "advance", "ribbon", ]
TOOL_TIP = "Cartoon ribbon with manual/auto volume, ribbon micro ctrls, bezier ctrls, and more."

node_data.NodeData.update_ctrls = update_ctrls


class CA_Ribbon(node_data.NodeData):
    """Cartoon_A_Ribbon module creates a cartoon_complex ribbon module. this is not a biped or quadruped module but
    a generic module the user can choose to use
    """
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
            default_value=items.index("+Y"),
            annotation="The world axis the ctrls will align with when zeroed.",
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
            default_value=False,
            annotation="Secondary ctrls are added to all ctrls to help prevent gimbal lock.",
            help_link="https://youtu.be/-1fpRw6oJME?t=157",
        )

        self.add_separator()
        self.volume_attr = self.add_boolean_attribute(
            name="Volume",
            default_value=True,
            annotation="Add 'Auto Volume' and 'Manual Volume' attributes.",
        )

        self.mid_jnts_aim_attr = self.add_boolean_attribute(
            name="Mid Joints Aim",
            default_value=False,
            annotation=(
                "Mid driver joints will aim at each other.\n"
                "This means the mid ctrls (all ctrls except first and last)\n"
                "will only influence twist for rotation (less control)\n"
                "but posing the ribbon to flow will be easier."
            ),
        )

        self.ctrls_count_attr = self.add_integer_attribute(
            name="Ctrls Count",
            default_value=3,
            dynamic_attribute=False,
            writable=True,
            readable=True,
            promoted=False,
            annotation="Number of ctrls/guides; modifying this attribute requires a 're-template'.",
            min_value=3,
            max_value=15,
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
            annotation="Number of skinning joints along the ribbon.",
            help_link="https://youtu.be/-1fpRw6oJME?t=198",
            min_value=3,
            max_value=50,
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
            annotation="Add ctrls that deform the ribbon like a Bezier curve.",
            help_link="https://youtu.be/-1fpRw6oJME?t=222",
        )
        self.bezier_offset_attr = self.add_xyz_attribute(
            name="Bezier Ctrls Offset",
            default_value=[-6, 0, 0],
            dynamic_attribute=False,
            writable=True,
            readable=True,
            promoted=False,
            annotation="Position offset of Bezier ctrls from joint chain.\nmultiplied by attribute 'Ctrls Scale'.",
        )
        self.close_layout()

        ### connections.
        self.add_separator(title="Connections")
        self.driven_root_attr = self.add_driven_attribute(name="Root Input", annotation="Input")
        self.driven_tip_attr = self.add_driven_attribute(name="Tip Input", annotation="Input")
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
        self.guides_list = []
        parent = None
        for index in range(self.ctrls_count_attr.value):
            guide = self.add_guide(
                name="ribbon_{0}".format(index),
                translation=[0, 13 * index, 0],
                parent=parent,
            )

            guide.shape = ["box", "arrow"]
            parent = guide
            self.guides_list.append(guide)

    def joints_creation(self):
        """Create joints based on attributes values and guides. (without positioning as this point). """
        # driver joints.
        self.driver_joints_list = []
        self.driver_joints_list.append(self.add_joint(name="ribbon_root", skinning_jnt=True, radius=0.75))

        for index in range(self.ctrls_count_attr.value - 2):
            jnt = self.add_joint(
                name="ribbon_driver_{0}".format(index),
                skinning_jnt=False,
                tag_parent_jnt=None,
                radius=0.75,
            )
            self.driver_joints_list.append(jnt)

        # driven joints.
        self.driven_joints_list = []
        parent_tag = self.driver_joints_list[0]
        for index in range(self.ribbon_joints_attr.value):
            jnt = self.add_joint(
                name="ribbon_driven_{0}".format(index),
                skinning_jnt=True,
                tag_parent_jnt=parent_tag,
                radius=0.5,
            )
            parent_tag = jnt
            self.driven_joints_list.append(jnt)

        self.driver_joints_list.append(self.add_joint(name="ribbon_tip", skinning_jnt=True, radius=0.75))
        self.driver_joints_list[-1].parent_tag = self.driven_joints_list[-1]

    def ctrls_creation(self):
        """Create controls based on attributes values, guides and joints. (without positioning as this point). """
        scale_mult = self.ctrls_scale_attr.value * 2.0

        self.ctrls_list = []
        self.secondary_ctrls = []
        for index in range(self.ctrls_count_attr.value):
            ctrl = self.add_ctrl(
                name="ribbon_{0}".format(index),
                shape="square_with_arrow",
                size=(1.5 * scale_mult),
                up_orient="+Y",
            )
            self.ctrls_list.append(ctrl)

            if self.secondary_ctrl_attr.value is True:
                secondary_ctrl = self.add_ctrl(name="ribbon_secondary_{0}".format(index), size=(1.4 * scale_mult))
                secondary_ctrl.color = SECONDARY_COLOR
                self.secondary_ctrls.append(secondary_ctrl)

        self.ctrls_list[0].shape = "box"
        self.ctrls_list[-1].shape = "box"

        for ctrl in self.ctrls_list + self.secondary_ctrls:
            for attr in ["scaleX", "scaleY", "scaleZ"]:
                ctrl.add_locked_hidden_attr(attr)

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
                name="ribbon_ribbon_bezier",
                driver_jnts_count=len(self.driver_joints_list),
            )

    def maya_attrs_creation(self):
        """Declare any Maya attributes that users should be able to modify. """
        first_ctrl = self.ctrls_list[0]

        if self.ribbon_ctrls_attr.value:
            first_ctrl.add_maya_attr(name="ribbon_micro_ctrls", attr_type="bool", default_value=False)

        if self.ribbon_bezier_attr.value:
            first_ctrl.add_maya_attr(name="bezier_ctrls", attr_type="bool", default_value=False)

        if self.volume_attr.value:
            first_ctrl.add_maya_attr(name="auto_volume", attr_type="float", default_value=0, min=0, max=1)
            first_ctrl.add_maya_attr(name="gradual_volume", attr_type="float", default_value=1, min=0, max=1)
            first_ctrl.add_maya_attr(name="gradual_intensity", attr_type="float", default_value=0, min=-10, max=10)
            first_ctrl.add_maya_attr(name="gradual_spread", attr_type="float", default_value=0, min=-10, max=10)

    def rig_creation(self):
        """Based on attributes value, guides (which now you can get global position from) joints and controls
        created in their methods you can build the rig.
        """
        ctrls_scale = self.ctrls_scale_attr.value

        if self.is_mirrored:
            self.module_grp.set_attr("scaleX", -1)

        grps = create_grps(self, ["input_root_grp", "input_tip_grp", "output_root_grp", "output_tip_grp"])
        input_root_grp, input_tip_grp, output_root_grp, output_tip_grp = grps

        self.driven_root_attr.set_maya_object(input_root_grp)
        self.driven_tip_attr.set_maya_object(input_tip_grp)
        self.driver_root_attr.set_maya_object(output_root_grp)
        self.driver_tip_attr.set_maya_object(output_tip_grp)

        self.ctrls_grp, self.jnts_grp = create_grps(self, ["ctrls_grp", "jnts_grp"])

        self.ctrls_grp.set_translation(self.guides_list[0].world_transformations["translate"])
        world_rotation(
            obj=self.ctrls_grp,
            aim_direction=self.world_orientation_attr.display_value,
            twist=self.world_twist_attr.value,
        )

        for ctrl in self.ctrls_list:
            ctrl.pointer.offset_grp.parent_relative(self.ctrls_grp)

        first_ctrl = self.ctrls_list[0].pointer
        last_ctrl = self.ctrls_list[-1].pointer

        # create ribbons setup.
        self.total_length = 0.0
        from_pos = self.guides_list[0].world_transformations["translate"]
        for guide in self.guides_list[1:]:
            self.total_length += math_utils.distance_between(from_pos, guide.world_transformations["translate"])
            from_pos = guide.world_transformations["translate"]

        ribbon = ComplexRibbon(
            driver_joints=[jnt.pointer for jnt in self.driver_joints_list],
            driven_joints=[jnt.pointer for jnt in self.driven_joints_list],
            rest_length=self.total_length,
            name_prefix="{0}_ribbon".format(self.name),
            parent_to=self.module_grp,
            is_mirrored=self.is_mirrored,
        )

        # show first and last driver jnts since they are skinning jnts.
        ribbon.driver_joints[0].offset_grp.set_attr("visibility", True)
        ribbon.driver_joints[-1].offset_grp.set_attr("visibility", True)

        first_ctrl.add_spacer_attr()
        secondary_ctrls_setup(self.ctrls_list, self.secondary_ctrls)

        ## ribbon features.
        if self.ribbon_ctrls_attr.value is True:
            ribbon_ctrls_vis_attr = first_ctrl.add_attr("ribbon_micro_ctrls", at="bool", k=True, dv=0)

        if self.ribbon_bezier_attr.value is True:
            bezier_attr = first_ctrl.add_attr("bezier_ctrls", at="bool", k=True, dv=0)

        # volume setup.
        if self.volume_attr.value:
            module_scale_attr = create_module_scale(parent_to=first_ctrl.btm_ctrl, name_prefix=self.name)

            vol_attrs = ribbon.auto_manual_volume_setup(
                attrs_node=first_ctrl,
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
            bezier_ctrls_list = []
            for info_lists in self.bezier_ctrls_list:
                ctrls = []
                for info in info_lists:
                    ctrls.append(info.pointer)

                bezier_ctrls_list.append(ctrls)

            ribbon.bezier_setup(
                bezier_ctrls=bezier_ctrls_list,
                ctrls_offset=[value * ctrls_scale for value in self.bezier_offset_attr.value],
                vis_attr=bezier_attr,
            )

        ribbon.top_grp.set_matrix(self.guides_list[0].world_transformations["matrix"])

        self._connect_driver_jnts()
        self._position_ctrls()

        if self.ribbon_ctrls_attr.value:
            ribbon.micro_ctrls_setup(
                driven_ctrls=[ctrl.pointer for ctrl in self.ribbon_ctrls],
                parent_to=self.ctrls_grp,
                vis_attr=ribbon_ctrls_vis_attr,
            )

        last_ctrl_scale_offset_grp = IoTransform("{0}_scale_offset_grp".format(last_ctrl.short_name))
        last_ctrl_scale_offset_grp.parent_relative(first_ctrl.btm_ctrl)
        last_ctrl.offset_grp.parent(last_ctrl_scale_offset_grp)

        ribbon.jnts_grp.parent(self.jnts_grp)
        ribbon.jnts_grp.set_attr("scale", [1, 1, 1])
        input_root_grp.match_transformation_to(self.ctrls_grp)
        matrix_constraint(driver=input_root_grp, driven=self.jnts_grp, maintain_offset=True)
        matrix_constraint(driver=input_root_grp, driven=self.ctrls_grp, maintain_offset=True)

        if self.volume_attr.value:  # resetting volume default length to bindPose length.
            ribbon.update_default_arch_length()

        input_tip_grp.match_transformation_to(last_ctrl_scale_offset_grp)
        matrix_constraint(
            driver=input_tip_grp,
            driven=last_ctrl_scale_offset_grp,
            maintain_offset=True,
            skip_attrs=(False, False, False, False, False, False, True, True, True),
            )

        matrix_constraint(driver=self.driver_joints_list[0].pointer, driven=output_root_grp, maintain_offset=False)
        matrix_constraint(driver=self.driver_joints_list[-1].pointer, driven=output_tip_grp, maintain_offset=False)

        if self.expose_rotation_order_attr.value:
            expose_rotation_order(self.ctrls_list + self.secondary_ctrls)

    def _connect_driver_jnts(self):
        """Have ctrls drive driver jnts. """
        edges_ctrls = [self.ctrls_list[0].pointer, self.ctrls_list[-1].pointer]

        ribbon_length = 0.0
        from_pos = None
        for jnt, ctrl, guide in zip(self.driver_joints_list, self.ctrls_list, self.guides_list):
            ctrl = ctrl.pointer
            jnt = jnt.pointer

            if from_pos is not None:
                ribbon_length += math_utils.distance_between(from_pos, guide.world_transformations["translate"])
                ctrl.offset_grp.set_attr("translateY", ribbon_length)

            skip_list = (False, False, False, False, False, False, True, True, True)
            if self.mid_jnts_aim_attr.value and ctrl not in edges_ctrls:
                skip_list = (False, False, False, True, True, True, True, True, True)

            matrix_constraint(
                driver=ctrl.btm_ctrl,
                driven=jnt,
                maintain_offset=False,
                skip_attrs=skip_list,
                )
            from_pos = guide.world_transformations["translate"]

        if self.mid_jnts_aim_attr.value:
            self._aim_driver_jnts()

    def _aim_driver_jnts(self):
        """Have driver jnts aim at each other except first and last. """
        aim_at_jnt = self.driver_joints_list[0].pointer
        for jnt, ctrl in zip(self.driver_joints_list[1:-1], self.ctrls_list[1:-1]):
            jnt, ctrl = jnt.pointer, ctrl.pointer
            jnt.aim_constraint_to(
                aim_at_jnt,
                aimVector=(0, -1, 0),
                upVector=(1, 0, 0),
                worldUpType="objectrotation",
                worldUpVector=(1, 0, 0),
                worldUpObject=ctrl.btm_ctrl,
                maintainOffset=False,
            )

            aim_at_jnt = jnt

    def _position_ctrls(self):
        """Position ctrls at guides position. """
        ordered_guides = [self.guides_list[0], self.guides_list[-1]] + self.guides_list[1:-1]
        ordered_ctrls = [self.ctrls_list[0], self.ctrls_list[-1]] + self.ctrls_list[1:-1]

        if self.clean_transformations_attr.value is True:
            for guide, ctrl in zip(ordered_guides, ordered_ctrls):
                ctrl.pointer.offset_grp.set_matrix(guide.world_transformations["matrix"])
        else:
            for guide, ctrl in zip(ordered_guides, ordered_ctrls):
                ctrl.pointer.set_matrix(guide.world_transformations["matrix"])
