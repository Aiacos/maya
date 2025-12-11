"""Eyes module creates a basic 2 eyes setup. """

import maya.cmds as mc

from arise.data_types import node_data
from arise.utils.io_nodes.io_transform import IoTransform
from arise.utils.matrix_utils import matrix_constraint
from arise.utils.modules_utils import (
    secondary_ctrls_setup, expose_rotation_order, create_grps, SECONDARY_COLOR, update_ctrls,
)

MAYA_VERSION = 2016  # the version of maya from which this module supports.
AUTHOR = "Etay Herz"  # name of person who created this module.
RIG_CATEGORY = "Basic"  # either 'Basic', 'Cartoon', 'Vfx', 'Game' or 'All'.
RIG_TYPE = "All"  # Biped, Car, Quadruped, ..., All.
TAGS = ["basic", "simple", "eyes", "eye", "aim"]
TOOL_TIP = "Basic eye setup with aim."

node_data.NodeData.update_ctrls = update_ctrls


class Eye(node_data.NodeData):
    """Eyes module creates a basic eye setup with aim. """
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

        self.expose_rotation_order_attr = self.add_boolean_attribute(
            name="Expose RotateOrder",
            default_value=True,
            annotation="Exposes all the ctrls 'RotateOrder' attribute in the Channel Box.",
            help_link="https://youtu.be/-1fpRw6oJME?t=149",
        )

        self.secondary_ctrls_attr = self.add_boolean_attribute(
            name="Secondary Ctrls",
            default_value=False,
            annotation="Under each ctrl adds a secondary ctrl.",
            help_link="https://youtu.be/-1fpRw6oJME?t=157",
        )

        self.add_separator()
        self.enable_scale_attr = self.add_boolean_attribute(
            name="Enable Scale",
            default_value=False,
            annotation="Enable scaling of the eyeball."
        )

        self.add_separator(title="Connections")
        self.driven_root_attr = self.add_driven_attribute(name="Root Input", annotation="Input")
        self.driven_aim_attr = self.add_driven_attribute(name="Aim Ctrl Input", annotation="Input")
        self.driver_eye_attr = self.add_driver_attribute(name="Eye Output", annotation="Output")

        self.close_layout()

    def guides_creation(self):
        """Create guides based on attributes values. """
        self.eye_guide = self.add_guide(name="eye_center", translation=[8, 180, 5], rotation=[90, 0, 90])
        self.eye_guide.shape = "sphere_with_arrow"
        self.eye_guide.up_orient = "-X"

        self.eyes_aim_guide = self.add_guide(name="eye_aim_at", translation=[8, 180, 60])
        self.eyes_aim_guide.shape = "crystal"
        self.eyes_aim_guide.rotate_offset = [90, 0, 90]
        self.eyes_aim_guide.size = self.eyes_aim_guide.size * 1.5
        self.eyes_aim_guide.visual_parent = self.eye_guide

    def joints_creation(self):
        """Create joints based on attributes values and guides. (without positioning as this point). """
        self.joint = self.add_joint(name="eyeball", skinning_jnt=True, tag_parent_jnt=None, radius=0.5)

    def ctrls_creation(self):
        """Create controls based on attributes values, guides and joints. (without positioning as this point). """
        scale_mult = self.ctrls_scale_attr.value * 3.5

        self.eye_ctrl = self.add_ctrl(name="eyeball", shape="circle", up_orient="+Y", size=1.5 * scale_mult)
        self.eye_ctrl.translate_offset = [0, 5, 0]

        self.aim_at_ctrl = self.add_ctrl(name="eye_aim_at", shape="crystal", size=1.5 * scale_mult)
        self.aim_at_ctrl.rotate_offset = [90, 0, 90]
        self.aim_at_ctrl.line_width = 2

        self.aim_at_secondary, self.eye_secondary = None, None
        if self.secondary_ctrls_attr.value:
            self.eye_secondary = self.add_ctrl(name="eye_secondary", size=1.2 * scale_mult)
            self.eye_secondary.translate_offset = [0, 5, 0]
            self.eye_secondary.color = SECONDARY_COLOR

            self.aim_at_secondary = self.add_ctrl(name="eye_aim_at_secondary", shape="crystal")
            self.aim_at_secondary.size = 1.2 * scale_mult
            self.aim_at_secondary.rotate_offset = [90, 0, 90]
            self.aim_at_secondary.color = SECONDARY_COLOR

        for ctrl in [self.aim_at_ctrl, self.aim_at_secondary]:

            if not ctrl:
                continue

            for attr in ["scaleX", "scaleY", "scaleZ"]:
                ctrl.add_locked_hidden_attr(attr)

        attrs = ["translateX", "translateY", "translateZ"]
        if self.enable_scale_attr.value is False:
            attrs = ["translateX", "translateY", "translateZ", "scaleX", "scaleY", "scaleZ"]

        for ctrl in [self.eye_ctrl, self.eye_secondary]:

            if not ctrl:
                continue

            for attr in attrs:
                ctrl.add_locked_hidden_attr(attr)

    def rig_creation(self):
        """Based on attributes value, guides (which now you can get global position from) joints and controls
        created in their methods you can build the rig.
        """
        if self.is_mirrored:
            self.module_grp.set_attr("scaleX", -1)

        input_grp, output_grp, input_aim = create_grps(self, ["input_grp", "output_grp", "input_aim_grp"])

        self.driven_root_attr.set_maya_object(input_grp)
        self.driver_eye_attr.set_maya_object(output_grp)
        self.driven_aim_attr.set_maya_object(input_aim)

        jnts_grp, ctrls_grp, aim_grp = create_grps(self, ["jnts_grp", "ctrls_grp", "eye_aiming_grp"])
        jnt_offset_grp, aim_at_driven = create_grps(self, ["jnt_offset_grp", "aim_at_ctrl_driven_grp"])

        ctrls_grp.set_translation(self.eye_guide.world_transformations["translate"])
        jnts_grp.set_translation(self.eye_guide.world_transformations["translate"])

        jnt_offset_grp.parent_relative(jnts_grp)
        jnt_offset_grp.set_matrix(self.eye_guide.world_transformations["matrix"])
        jnt_offset_grp.set_attr("scale", [1, 1, 1])

        joint = self.joint.pointer
        joint.parent_relative(jnt_offset_grp)

        secondary_ctrls_setup([self.eye_ctrl, self.aim_at_ctrl], [self.eye_secondary, self.aim_at_secondary])

        if self.expose_rotation_order_attr.value:
            expose_rotation_order([self.eye_ctrl, self.aim_at_ctrl, self.eye_secondary, self.aim_at_secondary])

        eye_ctrl = self.eye_ctrl.pointer
        eye_ctrl.offset_grp.parent_relative(ctrls_grp)
        eye_ctrl.offset_grp.match_transformation_to(joint)
        matrix_constraint(eye_ctrl.btm_ctrl, joint, maintain_offset=False)

        aim_at_driven.parent_relative(ctrls_grp)
        aim_at_driven.set_matrix(self.eyes_aim_guide.world_transformations["matrix"])
        aim_at_driven.set_attr("scale", [1, 1, 1])

        aim_at = self.aim_at_ctrl.pointer
        aim_at.offset_grp.parent_relative(aim_at_driven)

        loc = IoTransform(mc.spaceLocator(name="{0}_aim_at_up_loc".format(self.name))[0], existing=True)
        loc.parent_relative(jnt_offset_grp)
        loc.set_attr("translateX", 20)
        loc.parent(jnt_offset_grp)
        loc.lock_and_hide_transformations(vis=False)
        loc.hide()

        aim_grp.parent_relative(eye_ctrl)
        aim_grp.parent(ctrls_grp)

        aim_grp.aim_constraint_to(
            aim_at.btm_ctrl,
            aimVector=(0, 1, 0),
            upVector=(1, 0, 0),
            worldUpType="object",
            worldUpObject=loc,
            maintainOffset=False,
        )

        eye_ctrl.offset_grp.parent(aim_grp)

        input_grp.match_transformation_to(ctrls_grp)
        matrix_constraint(input_grp, ctrls_grp, maintain_offset=False)
        matrix_constraint(input_grp, jnts_grp, maintain_offset=False)
        input_aim.match_transformation_to(aim_at_driven)
        matrix_constraint(input_aim, aim_at_driven, maintain_offset=False)
        matrix_constraint(joint, output_grp, maintain_offset=False)
