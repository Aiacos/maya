"""CA_Tentacle module creates a spline_IK from a ribbon giving the advantages of both worlds. """

from arise.data_types import node_data
from arise.utils import math_utils
from arise.utils.matrix_utils import matrix_constraint
from arise.utils.modules_utils import (
    world_rotation, secondary_ctrls_setup, expose_rotation_order, create_grps,
    create_bezier_ctrls, SECONDARY_COLOR, update_ctrls,
)

from arise.utils.subcomponents.tentacle_ribbon import TentacleRibbon

MAYA_VERSION = 2017  # the version of maya from which this module SHOULD supports.
AUTHOR = "Etay Herz"  # name of person who created this module.
RIG_CATEGORY = "Cartoon"  # either 'Basic', 'Cartoon', 'Vfx', 'Game' or 'All'. (used when filtering).
RIG_TYPE = "All"  # Biped, Car, Quadruped, All, ... (for filtering modules in lists).
TAGS = ["cartoon", "complex", "advance", "ribbon", "ik_spline", "wave", "sine", "path",]
TOOL_TIP = "Cartoon tentacle, a combination of a ribbon and a spline IK."

node_data.NodeData.update_ctrls = update_ctrls


class CA_Tentacle(node_data.NodeData):
    """CA_Tentacle module creates a spline_IK from a ribbon giving the advantages of both worlds. """
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

        ### ribbons settings.
        self.add_separator()
        self.add_collapsible_layout(title="Tentacle Settings", shown=True)

        self.ctrls_count_attr = self.add_integer_attribute(
            name="Ctrls Count",
            default_value=4,
            dynamic_attribute=False,
            writable=True,
            readable=True,
            promoted=False,
            annotation="Number of ctrls/guides to create; modifying this attribute requires a 're-template'.",
            min_value=3,
            max_value=15,
            add_slider=True,
        )
        self.ribbon_joints_attr = self.add_integer_attribute(
            name="Joints",
            default_value=8,
            dynamic_attribute=False,
            writable=True,
            readable=True,
            promoted=False,
            annotation="Number of skinning joints along the tentacle.",
            help_link="https://youtu.be/-1fpRw6oJME?t=198",
            min_value=3,
            max_value=60,
            add_slider=True,
        )

        self.ribbon_ctrls_attr = self.add_boolean_attribute(
            name="Micro Ctrls",
            default_value=False,
            annotation="Add a ctrl for every ribbon skinning joint.",
            help_link="https://youtu.be/-1fpRw6oJME?t=211",
        )

        self.sine_attr = self.add_boolean_attribute(
            name="Sine",
            default_value=True,
            annotation="Add wave-like control attributes to the first ctrl.",
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
            annotation="Position offset of Bezier ctrls from the ribbon.\nmultiplied by attribute 'Ctrls Scale'.",
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
        self.guides_list = []
        pos = [0, 0, 0]
        side_pin_guide = None
        parent = None
        for index in range(self.ctrls_count_attr.value):
            guide = self.add_aim_guide(
                name="tentacle_{0}".format(index),
                translation=pos,
                parent=parent,
                side_pin_rotation=(0, 0, 0),
                side_pin_guide=side_pin_guide if self.guides_up_shared_attr.value else None,
            )

            if side_pin_guide is None:
                side_pin_guide = guide

            pos = [pos[0], pos[1]+13, pos[2]]
            self.guides_list.append(guide)
            parent = guide

        # aim guides at each other.
        for index, guide in enumerate(self.guides_list[:-1]):
            guide.aim_at = self.guides_list[index+1]

        self.guides_list[-1].aim_at = self.guides_list[-2]
        self.guides_list[-1].aim_rotation_offset = [180, 0, 0]

    def joints_creation(self):
        """Create joints based on attributes values and guides. (without positioning as this point). """
        # driver joints.
        self.driver_joints_list = []
        for index in range(self.ctrls_count_attr.value):
            jnt = self.add_joint(
                name="tentacle_driver_{0}".format(index),
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
                name="tentacle_driven_{0}".format(index),
                skinning_jnt=True,
                tag_parent_jnt=parent_tag,
                radius=0.5,
            )
            parent_tag = jnt
            self.driven_joints_list.append(jnt)

        self.driver_joints_list[-1].parent_tag = parent_tag

    def ctrls_creation(self):
        """Create controls based on attributes values, guides and joints. (without positioning as this point). """
        scale_mult = self.ctrls_scale_attr.value * 2.0

        self.ctrls_list = []
        self.secondary_ctrls = []
        for index in range(self.ctrls_count_attr.value):
            ctrl = self.add_ctrl(
                name="tentacle_{0}".format(index),
                shape="square_with_arrow",
                size=(1.5 * scale_mult),
                up_orient="+Y",
            )
            self.ctrls_list.append(ctrl)

            if self.secondary_ctrl_attr.value is True:
                secondary_ctrl = self.add_ctrl(name="tentacle_{0}_secondary".format(index), size=(1.4*scale_mult))
                secondary_ctrl.color = SECONDARY_COLOR
                self.secondary_ctrls.append(secondary_ctrl)

        self.ctrls_list[0].shape = "box"

        for ctrl in self.ctrls_list:
            ctrl.add_locked_hidden_attr("scaleY")
            ctrl.add_locked_hidden_attr("scaleZ")

        for ctrl in self.secondary_ctrls:
            for attr in ["scaleX", "scaleY", "scaleZ"]:
                ctrl.add_locked_hidden_attr(attr)

        self.ribbon_ctrls = []
        if self.ribbon_ctrls_attr.value:
            for index in range(self.ribbon_joints_attr.value):
                ctrl = self.add_ctrl(
                    name="tentacle_micro_{0}".format(index), size=(1.05 * scale_mult), shape="octagon",
                )
                self.ribbon_ctrls.append(ctrl)

        self.bezier_ctrls_list = []
        if self.ribbon_bezier_attr.value is True:
            self.bezier_ctrls_list = create_bezier_ctrls(
                class_=self,
                scale_mult=scale_mult,
                name="tentacle_ribbon_bezier",
                driver_jnts_count=len(self.driver_joints_list),
            )

    def maya_attrs_creation(self):
        """Declare any Maya attributes that users should be able to modify. """
        if self.ribbon_ctrls_attr.value:
            self.ctrls_list[0].add_maya_attr(name="tentacle_micro_ctrls", attr_type="bool", default_value=False)

        if self.ribbon_bezier_attr.value:
            self.ctrls_list[0].add_maya_attr(name="bezier_ctrls", attr_type="bool", default_value=False)

        self.ctrls_list[0].add_maya_attr(name="stretch", attr_type="float", default_value=0.0, min=0.0, max=1.0)
        self.ctrls_list[0].add_maya_attr(name="length", attr_type="float", default_value=1.0, min=0.0, max=1.0)

        if self.sine_attr.value:
            self.ctrls_list[0].add_maya_attr(
                name="wavelength", attr_type="float", default_value=2, min=-10000, max=10000,
            )
            self.ctrls_list[0].add_maya_attr(
                name="start_from", attr_type="float", default_value=0.0, min=0.0, max=10000,
            )
            self.ctrls_list[0].add_maya_attr(
                name="rotate_sine", attr_type="float", default_value=0.0, min=-10000, max=10000,
            )

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
        self.driver_tip_attr.set_maya_object(output_tip_grp)
        self.driver_root_attr.set_maya_object(output_root_grp)

        self.ctrls_grp, self.jnts_grp = create_grps(self, ["ctrls_grp", "jnts_grp"])

        self.ctrls_grp.set_translation(self.guides_list[0].world_transformations["translate"])
        world_rotation(
            obj=self.ctrls_grp,
            aim_direction=self.world_orientation_attr.display_value,
            twist=self.world_twist_attr.value,
        )

        for ctrl in self.ctrls_list:
            ctrl.pointer.offset_grp.parent_relative(self.ctrls_grp)
            ctrl.pointer.scale_attrs_connect()

        # create ribbons setup.
        self.total_length = 0.0
        from_pos = self.guides_list[0].world_transformations["translate"]
        for guide in self.guides_list[1:]:
            self.total_length += math_utils.distance_between(from_pos, guide.world_transformations["translate"])
            from_pos = guide.world_transformations["translate"]

        tentacle = TentacleRibbon(
            driver_joints=[jnt.pointer for jnt in self.driver_joints_list],
            driven_joints=[jnt.pointer for jnt in self.driven_joints_list[1:-1]],
            rest_length=self.total_length,
            name_prefix="{0}_tentacle".format(self.name),
            parent_to=self.module_grp,
            is_mirrored=self.is_mirrored,
            driven_root=self.driven_joints_list[0].pointer,
            driven_tip=self.driven_joints_list[-1].pointer,
        )

        first_ctrl = self.ctrls_list[0].pointer
        first_ctrl.add_spacer_attr()
        secondary_ctrls_setup(self.ctrls_list, self.secondary_ctrls)

        ## ribbon features.
        if self.ribbon_ctrls_attr.value is True:
            ribbon_ctrls_vis_attr = first_ctrl.add_attr("tentacle_micro_ctrls", at="bool", k=True, dv=0)

        if self.ribbon_bezier_attr.value is True:
            bezier_attr = first_ctrl.add_attr("bezier_ctrls", at="bool", k=True, dv=0)

        tentacle.spline_ik_setup(
            ctrl=self.ctrls_list[0].pointer,
            module_scale_attr=input_root_grp.attr("scaleX"),
            ctrls=[ctrl.pointer for ctrl in self.ctrls_list],
        )

        if self.sine_attr.value is True:
            tentacle.sine_setup(ctrl=first_ctrl)

        # bezier setup.
        if self.ribbon_bezier_attr.value is True:
            bezier_ctrls_list = []
            for info_lists in self.bezier_ctrls_list:
                ctrls = []
                for info in info_lists:
                    ctrls.append(info.pointer)

                bezier_ctrls_list.append(ctrls)

            tentacle.bezier_setup(
                bezier_ctrls=bezier_ctrls_list,
                ctrls_offset=[value * ctrls_scale for value in self.bezier_offset_attr.value],
                vis_attr=bezier_attr,
            )

        tentacle.top_grp.set_matrix(self.guides_list[0].world_transformations["matrix"])

        self._connect_driver_jnts()
        self._position_ctrls()

        if self.ribbon_ctrls_attr.value:
            tentacle.micro_ctrls_setup(
                driven_ctrls=[ctrl.pointer for ctrl in self.ribbon_ctrls],
                parent_to=self.ctrls_grp,
                vis_attr=ribbon_ctrls_vis_attr,
            )

        tentacle.jnts_grp.parent(self.jnts_grp)
        tentacle.jnts_grp.set_attr("scale", [1, 1, 1])
        input_root_grp.match_transformation_to(self.ctrls_grp)
        matrix_constraint(driver=input_root_grp, driven=self.jnts_grp, maintain_offset=True)
        matrix_constraint(driver=input_root_grp, driven=self.ctrls_grp, maintain_offset=True)

        matrix_constraint(driver=self.driven_joints_list[-1].pointer, driven=output_tip_grp, maintain_offset=False)
        matrix_constraint(
            driver=self.driven_joints_list[0].pointer,
            driven=output_root_grp,
            maintain_offset=False,
        )

        if self.expose_rotation_order_attr.value:
            expose_rotation_order(self.ctrls_list + self.secondary_ctrls)

    def _connect_driver_jnts(self):
        """Have ctrls drive the position of driver jnts. """
        ribbon_length = 0.0
        from_pos = None
        for jnt, ctrl, guide in zip(self.driver_joints_list, self.ctrls_list, self.guides_list):
            ctrl = ctrl.pointer
            jnt = jnt.pointer

            if from_pos is not None:
                ribbon_length += math_utils.distance_between(from_pos, guide.world_transformations["translate"])
                ctrl.offset_grp.set_attr("translateY", ribbon_length)

            matrix_constraint(
                driver=ctrl.btm_ctrl,
                driven=jnt,
                maintain_offset=False,
                skip_attrs=(False, False, False, False, False, False, True, True, True),
                )

            from_pos = guide.world_transformations["translate"]

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
