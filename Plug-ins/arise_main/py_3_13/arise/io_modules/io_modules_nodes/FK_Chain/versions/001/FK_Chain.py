"""FK_Chain module creates a basic FK chain rig. """

import maya.cmds as mc

from arise.data_types import node_data
from arise.utils.matrix_utils import matrix_constraint
from arise.utils.math_utils import distance_between
from arise.utils.modules_utils import (
    world_rotation, secondary_ctrls_setup, expose_rotation_order, create_grps, SECONDARY_COLOR, update_ctrls,
)

MAYA_VERSION = 2016  # the version of maya from which this module supports.
AUTHOR = "Etay Herz"  # name of person who created this module.
RIG_CATEGORY = "Basic"  # either 'Basic', 'Cartoon', 'Vfx', 'Game' or 'All'.
RIG_TYPE = "All"  # Biped, Car, Quadruped, ..., All.
TAGS = ["basic", "fk", "chain"]
TOOL_TIP = "Simple FK chain."

node_data.NodeData.update_ctrls = update_ctrls


class FK_Chain(node_data.NodeData):
    """FK_Chain module creates a basic FK chain rig. """
    sort_priority = 500

    def __init__(self, parent, docs, icon, module_dict):
        node_data.NodeData.__init__(
            self,
            parent=parent,
            icon=icon,
            docs=docs,
            module_dict=module_dict
        )

    def attributes_creation(self):  # REIMPLEMENTED!
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
            annotation="Exposes all the ctrls 'RotateOrder' attribute in the Channel Box",
            help_link="https://youtu.be/-1fpRw6oJME?t=149",
        )

        self.secondary_ctrls_attr = self.add_boolean_attribute(
            name="Secondary Ctrls",
            default_value=False,
            annotation="Secondary ctrls are added under some ctrls to help prevent gimbal lock.",
            help_link="https://youtu.be/-1fpRw6oJME?t=157",
        )

        self.add_separator()
        self.joint_count_attr = self.add_integer_attribute(
            name="Joints",
            default_value=3,
            dynamic_attribute=False,
            writable=True,
            readable=True,
            promoted=False,
            annotation="The number of joints/guides; modifying this attribute requires a 're-template'.",
            min_value=2,
            max_value=200,
            add_slider=False,
        )
        self.translate_ctrls_attr = self.add_boolean_attribute(
            name="Ctrls Translate",
            default_value=False,
            annotation="If checked, animators will also be able to translate the FK ctrls.",
        )

        self.last_ctrl_attr = self.add_boolean_attribute(
            name="Create Last Joint Ctrl",
            default_value=True,
            annotation="Creates a ctrl for the last joint",
        )

        self.add_separator(title="Connections")
        self.driven_root_attr = self.add_driven_attribute(name="Root Input", annotation="Input")
        self.driver_root_attr = self.add_driver_attribute(name="Root Output", annotation="Output")
        self.driver_tip_attr = self.add_driver_attribute(name="Tip Output", annotation="Output")

        self.close_layout()

    def evaluate_creation_methods(self):  # REIMPLEMENTED!
        """Reimplemented to enable/disable attrs. """
        self.world_orientation_attr.set_disabled(True if self.clean_transformations_attr.value else False)
        self.world_twist_attr.set_disabled(True if self.clean_transformations_attr.value else False)

        node_data.NodeData.evaluate_creation_methods(self)

    def guides_creation(self):
        """Create guides based on attributes values. """
        offset = 15
        self.guides_list = []
        side_pin_guide = None
        parent = None
        for index in range(self.joint_count_attr.value):
            guide = self.add_aim_guide(
                name="{0}".format(str(index).zfill(4)),
                translation=[0, offset * index, 0],
                parent=parent,
                side_pin_rotation=(0, 0, 0),
                side_pin_guide=side_pin_guide if self.guides_up_shared_attr.value else None,
            )
            if side_pin_guide is None:
                side_pin_guide = guide

            self.guides_list.append(guide)
            parent = guide

        # aim guides at each other.
        for index, guide in enumerate(self.guides_list[:-1]):
            guide.aim_at = self.guides_list[index+1]

        self.guides_list[-1].aim_at = self.guides_list[-2]
        self.guides_list[-1].aim_rotation_offset = (180, 0, 0)

    def joints_creation(self):
        """Create joints based on attributes values and guides. (without positioning as this point). """
        self.joints_list = []
        parent = None
        for index in range(self.joint_count_attr.value):
            joint = self.add_joint(
                name="fk_chain_{0}".format(index),
                skinning_jnt=True,
                tag_parent_jnt=parent,
                radius=0.5,
            )
            parent = joint
            self.joints_list.append(joint)

    def ctrls_creation(self):
        """Create controls based on attributes values, guides and joints. (without positioning as this point). """
        scale_mult = self.ctrls_scale_attr.value * 3.5

        self.ctrls_list = []
        self.secondary_list = []
        count = len(self.joints_list) if self.last_ctrl_attr.value else len(self.joints_list)-1
        for index in range(count):
            # ctrls.
            ctrl = self.add_ctrl(
                name="fk_chain_{0}".format(index),
                shape="circle",
                up_orient="+Y",
                size=1.5 * scale_mult,
            )
            self.ctrls_list.append(ctrl)

            # secondary ctrls.
            if self.secondary_ctrls_attr.value:
                secondary = self.add_ctrl(
                    name="fk_chain_{0}_secondary".format(index),
                    shape="circle",
                    up_orient="+Y",
                    size=1.4 * scale_mult,
                )
                secondary.color = SECONDARY_COLOR
                self.secondary_list.append(secondary)

        # lock hide attrs on new ctrls.
        attrs = ["scaleY", "scaleZ"]
        if self.translate_ctrls_attr.value is False:
            attrs = ["translateX", "translateY", "translateZ", "scaleY", "scaleZ"]

        for ctrl in self.ctrls_list + self.secondary_list:
            for attr in attrs:
                ctrl.add_locked_hidden_attr(attr)

    def rig_creation(self):
        """Based on attributes value, guides (which now you can get global position from) joints and controls
        created in their methods you can build the rig.
        """
        if self.is_mirrored:
            self.module_grp.set_attr("scaleX", -1)

        grps = create_grps(self, ["input_root_grp", "output_root_grp", "output_tip_grp"])
        input_root_grp, output_root_grp, output_tip_grp = grps

        self.driven_root_attr.set_maya_object(input_root_grp)
        self.driver_root_attr.set_maya_object(output_root_grp)
        self.driver_tip_attr.set_maya_object(output_tip_grp)

        jnts_grp, ctrls_grp = create_grps(self, ["jnts_grp", "ctrls_grp"])

        ctrls_grp.set_translation(self.guides_list[0].world_transformations["translate"])
        world_rotation(ctrls_grp, self.world_orientation_attr.display_value, twist=self.world_twist_attr.value)

        jnts_grp.set_translation(self.guides_list[0].world_transformations["translate"])

        secondary_ctrls_setup(self.ctrls_list, self.secondary_list)

        # position and connect joints and ctrls.
        parent_jnt = self.joints_list[0].pointer
        parent_jnt.parent_relative(jnts_grp)
        parent_ctrl = self.ctrls_list[0].pointer
        parent_ctrl.offset_grp.parent_relative(ctrls_grp)
        parent_pos = self.guides_list[0].world_transformations["translate"]
        for ctrl, guide, jnt in zip(self.ctrls_list[1:], self.guides_list[1:], self.joints_list[1:]):
            ctrl = ctrl.pointer
            jnt = jnt.pointer

            jnt.parent_relative(parent_jnt)
            ctrl.offset_grp.parent_relative(parent_ctrl.btm_ctrl)
            distance = distance_between(parent_pos, guide.world_transformations["translate"])
            ctrl.offset_grp.set_attr("translateY", distance)

            # constrain joints to ctrls (cleaner code if I constrain parent joints and ctrls).
            if self.translate_ctrls_attr.value is True:
                mc.pointConstraint(parent_ctrl.btm_ctrl, parent_jnt, maintainOffset=False)
                mc.scaleConstraint(parent_ctrl.btm_ctrl, parent_jnt, maintainOffset=False)
                mc.aimConstraint(
                    ctrl.btm_ctrl,
                    parent_jnt,
                    aimVector=(0, 1, 0),
                    upVector=(1, 0, 0),
                    worldUpType="objectrotation",
                    worldUpVector=(1, 0, 0),
                    worldUpObject=parent_ctrl.btm_ctrl,
                    maintainOffset=False,
                )

            else:
                matrix_constraint(parent_ctrl.btm_ctrl, parent_jnt, maintain_offset=False)

            parent_pos = guide.world_transformations["translate"]
            parent_ctrl = ctrl
            parent_jnt = jnt

        # last joint is always matrix_constraint all axis.
        if self.last_ctrl_attr.value:
            matrix_constraint(
                self.ctrls_list[-1].pointer.btm_ctrl,
                self.joints_list[-1].pointer,
                maintain_offset=False,
            )

        else:
            matrix_constraint(
                self.ctrls_list[-1].pointer.btm_ctrl,
                self.joints_list[-2].pointer,
                maintain_offset=False,
            )

            self.joints_list[-1].pointer.parent_relative(parent_jnt)
            distance = distance_between(parent_pos, self.guides_list[-1].world_transformations["translate"])
            self.joints_list[-1].pointer.set_attr("translateY", distance)

        if self.clean_transformations_attr.value is True:
            for ctrl, guide in zip(self.ctrls_list, self.guides_list):
                ctrl.pointer.offset_grp.set_matrix(guide.world_transformations["matrix"])
                ctrl.pointer.offset_grp.set_scale([1, 1, 1])
        else:
            for ctrl, guide in zip(self.ctrls_list, self.guides_list):
                ctrl.pointer.set_matrix(guide.world_transformations["matrix"])
                ctrl.pointer.set_scale([1, 1, 1])

        for ctrl in self.ctrls_list + self.secondary_list:
            ctrl.pointer.scale_attrs_connect()

        # input output grps.
        input_root_grp.match_transformation_to(ctrls_grp)
        matrix_constraint(input_root_grp, ctrls_grp, maintain_offset=True)
        matrix_constraint(self.joints_list[-1], output_tip_grp, maintain_offset=False)
        matrix_constraint(self.joints_list[0], output_root_grp, maintain_offset=False)

        if self.expose_rotation_order_attr.value:
            expose_rotation_order(self.ctrls_list + self.secondary_list)
