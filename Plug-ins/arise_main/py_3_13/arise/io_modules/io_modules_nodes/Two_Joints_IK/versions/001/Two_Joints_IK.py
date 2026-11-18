"""Two_Joints_IK module is one of the basic nodes that simply creates a 2 joints IK setup. """

import maya.cmds as mc

from arise.utils.io_nodes.io_transform import IoTransform
from arise.data_types import node_data
from arise.utils.matrix_utils import matrix_constraint
from arise.utils.math_utils import distance_between
from arise.utils.tagging_utils import tag_as_dont_tag
from arise.utils.modules_utils import (
    world_rotation, secondary_ctrls_setup, expose_rotation_order, create_grps, SECONDARY_COLOR, update_ctrls,
)

MAYA_VERSION = 2016  # the version of maya from which this module supports.
AUTHOR = "Etay Herz"  # name of person who created this module.
RIG_CATEGORY = "Basic"  # either 'Basic', 'Cartoon', 'Vfx', 'Game' or 'All'. (used when filtering).
RIG_TYPE = "All"  # Biped, Car, Quadruped, All, ... (for filtering modules in lists).
TAGS = ["basic", "simple", "ik", "2", "two", "two joints", "simple ik"]
TOOL_TIP = "Simple two joints IK setup."

node_data.NodeData.update_ctrls = update_ctrls


class Two_Joints_IK(node_data.NodeData):
    """Two_Joints_IK module is one of the basic nodes that simply creates a 2 joints IK setup. """
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
        self.jnt_length_attr = self.add_radio_attribute(
            name="Joint Length",
            items=["Fixed", "Expandable", "Shrinkable", "Both"],
            default_value=0,
            annotation="Can the joint length change size?",
        )

        self.volume_attr = self.add_boolean_attribute(
            name="Volume",
            default_value=True,
            annotation="Add a 'volume' attribute that enables squash/stretch when joint length expands/shrinks",
        )

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
        self.volume_attr.set_disabled(False if self.jnt_length_attr.value else True)

        node_data.NodeData.evaluate_creation_methods(self)

    def guides_creation(self):  # REIMPLEMENTED!
        """Create guides based on attributes values. """

        self.root_guide = self.add_aim_guide(
            name="root",
            translation=[0, 0, 0],
            parent=None,
            side_pin_rotation=(0, 0, 0),
            side_pin_guide=None,
        )

        self.tip_guide = self.add_aim_guide(
            name="tip",
            translation=[0, 15, 0],
            parent=self.root_guide,
            side_pin_rotation=(0, 0, 0),
            side_pin_guide=self.root_guide,
        )

        self.root_guide.aim_at = self.tip_guide
        self.tip_guide.aim_at = self.root_guide
        self.tip_guide.aim_rotation_offset = (180, 0, 0)

    def joints_creation(self):
        """Create joints based on attributes values and guides. (without positioning as this point). """
        self.root_joint = self.add_joint(name="root", skinning_jnt=True, tag_parent_jnt=None, radius=0.5)
        self.tip_joint = self.add_joint(name="tip", skinning_jnt=True, tag_parent_jnt=self.root_joint, radius=0.5)

    def ctrls_creation(self):
        """Create controls based on attributes values, guides and joints. (without positioning as this point). """
        ctrls_mult = self.ctrls_scale_attr.value * 3.5
        self.root_ctrl = self.add_ctrl(name="root", shape="circle", up_orient="+Y", size=1.0 * ctrls_mult)
        self.tip_ctrl = self.add_ctrl(name="tip", shape="circle", up_orient="+Y", size=1.0 * ctrls_mult)

        self.root_secondary = None
        self.tip_secondary = None
        if self.secondary_ctrls_attr.value:
            self.root_secondary = self.add_ctrl(name="root_secondary", size=0.85 * ctrls_mult)
            self.root_secondary.color = SECONDARY_COLOR
            self.root_secondary.add_locked_hidden_attr("scaleX")

            self.tip_secondary = self.add_ctrl(name="tip_secondary", size=0.85 * ctrls_mult)
            self.tip_secondary.color = SECONDARY_COLOR
            self.tip_secondary.add_locked_hidden_attr("scaleX")


        secondary_ctrls = [self.root_secondary, self.tip_secondary] if self.tip_secondary else []
        for ctrl in [self.root_ctrl, self.tip_ctrl] + secondary_ctrls:
            ctrl.add_locked_hidden_attr("scaleY")
            ctrl.add_locked_hidden_attr("scaleZ")

    def rig_creation(self):
        """Based on attributes value, guides (which now you can get global position from) joints and controls
        created in their methods you can build the rig.
        """
        if self.is_mirrored:
            self.module_grp.set_attr("scaleX", -1)

        grps = create_grps(self, ["input_root_grp", "input_tip_grp", "output_root_grp", "output_tip_grp"])
        input_root_grp, input_tip_grp, output_root_grp, output_tip_grp = grps

        self.driven_root_attr.set_maya_object(input_root_grp)
        self.driven_tip_attr.set_maya_object(input_tip_grp)
        self.driver_tip_attr.set_maya_object(output_root_grp)
        self.driver_root_attr.set_maya_object(output_tip_grp)

        jnts_grp, ctrls_grp, data_grp = create_grps(self, ["jnts_grp", "ctrls_grp", "data_grp"])

        data_grp.set_visibility(False)

        root_jnt = self.root_joint.pointer
        tip_jnt = self.tip_joint.pointer
        root_ctrl = self.root_ctrl.pointer
        tip_ctrl = self.tip_ctrl.pointer

        # position joints.
        root_jnt.offset_grp = root_jnt.add_group_above("{0}_offset_grp".format(root_jnt.short_name))
        root_jnt.driven_grp = root_jnt.add_group_above("{0}_driven_grp".format(root_jnt.short_name))
        root_jnt.freeze_transformations()
        root_jnt.add_joint_orient()

        root_jnt.offset_grp.parent_relative(jnts_grp)
        root_jnt.offset_grp.set_matrix(self.root_guide.world_transformations["matrix"], space="world")
        root_jnt.offset_grp.set_attr("scale", [1, 1, 1])

        tip_jnt.parent_relative(root_jnt)
        tip_jnt.set_matrix(self.tip_guide.world_transformations["matrix"], space="world")
        tip_jnt.freeze_transformations()
        tip_jnt.add_joint_orient()

        # position ctrls.
        secondary_ctrls_setup([self.root_ctrl, self.tip_ctrl], [self.root_secondary, self.tip_secondary])

        for ctrl in [self.root_ctrl, self.tip_ctrl, self.root_secondary, self.tip_secondary]:
            if ctrl:
                ctrl.pointer.scale_attrs_connect()

        root_ctrl.offset_grp.parent_relative(ctrls_grp)

        tip_ctrl_scale_offset = IoTransform("{0}_scale_offset_grp".format(tip_ctrl.short_name))
        tip_ctrl_scale_offset.parent_relative(root_ctrl.btm_ctrl)
        tip_ctrl.offset_grp.parent_relative(tip_ctrl_scale_offset)

        ctrls_grp.match_transformation_to(root_jnt.offset_grp)
        ctrls_grp.set_attr("rotate", [0, 0, 0])
        ctrls_grp.set_attr("scale", [1, 1, 1])

        world_rotation(
            obj=root_ctrl.offset_grp,
            aim_direction=self.world_orientation_attr.display_value,
            flip_x_direction=False,
            twist=self.world_twist_attr.value,
        )
        distance = distance_between(
            self.root_guide.world_transformations["translate"],
            self.tip_guide.world_transformations["translate"],
        )
        tip_ctrl.offset_grp.set_attr("translateY", distance)

        # input tip has to be constraint here so tip_ctrl can be zeroed if clean_transformed.
        input_tip_grp.match_transformation_to(tip_ctrl_scale_offset)
        matrix_constraint(
            input_tip_grp,
            tip_ctrl_scale_offset,
            maintain_offset=True,
            skip_attrs=(False, False, False, False, False, False, True, True, True),
        )

        if self.clean_transformations_attr.value:
            root_ctrl.offset_grp.match_transformation_to(root_jnt)
            tip_ctrl.offset_grp.match_transformation_to(tip_jnt)

        else:
            root_ctrl.match_transformation_to(root_jnt)
            tip_ctrl.match_transformation_to(tip_jnt)

        # ik handle.
        name = "{0}_ik_handle".format(self.name)
        ik_handle, _ = mc.ikHandle(sj=root_jnt, ee=tip_jnt, solver="ikRPsolver", n=name)
        mc.setAttr("{0}.poleVector".format(ik_handle), *[0, 0, 0], type="double3")
        tag_as_dont_tag(mc.ikHandle(ik_handle, q=True, solver=True))
        mc.hide(ik_handle)

        self.handle_offset = IoTransform("ik_handle_offset_grp")
        self.handle_offset.parent_relative(data_grp)
        self.handle_offset.match_transformation_to(tip_jnt)
        mc.parent(ik_handle, self.handle_offset)

        matrix_constraint(root_ctrl.btm_ctrl, root_jnt.driven_grp, maintain_offset=False)
        matrix_constraint(
            tip_ctrl.btm_ctrl,
            self.handle_offset,
            maintain_offset=False,
            skip_attrs=(False, False, False, False, False, False, True, True, True),
        )
        mc.scaleConstraint(root_ctrl.btm_ctrl, self.handle_offset)
        tip_jnt.connect_attr("scaleX", tip_ctrl.attr("scaleX"))
        tip_jnt.connect_attr("scaleY", tip_ctrl.attr("scaleX"))
        tip_jnt.connect_attr("scaleZ", tip_ctrl.attr("scaleX"))

        self._joints_length_setup()

        if self.expose_rotation_order_attr.value:
            expose_rotation_order([self.root_ctrl, self.tip_ctrl, self.root_secondary, self.tip_secondary])

        # input output grps constraints.
        matrix_constraint(tip_jnt, output_tip_grp, maintain_offset=False)
        matrix_constraint(root_jnt, output_root_grp, maintain_offset=False)

        input_root_grp.match_transformation_to(ctrls_grp)
        matrix_constraint(input_root_grp, ctrls_grp, maintain_offset=True)

    def _joints_length_setup(self):
        """Setup control over joints length based on jnt_length_attr value. """
        tip_jnt = self.tip_joint.pointer
        root_ctrl = self.root_ctrl.pointer

        if self.jnt_length_attr.value == 0:  # fixed.
            return

        distance_node = mc.createNode("distanceBetween", n="{0}_distance_between".format(self.name))
        mc.connectAttr("{0}.worldMatrix[0]".format(self.handle_offset), "{0}.inMatrix1".format(distance_node))
        mc.connectAttr("{0}.worldMatrix[0]".format(root_ctrl.btm_ctrl), "{0}.inMatrix2".format(distance_node))
        distance = mc.getAttr("{0}.distance".format(distance_node))

        divide_node = mc.createNode("multiplyDivide", n="{0}_scale_divide".format(self.name))
        mc.setAttr("{0}.operation".format(divide_node), 2)  # divide.
        mc.connectAttr("{0}.distance".format(distance_node), "{0}.input1X".format(divide_node))
        mc.connectAttr("{0}.scaleX".format(self.handle_offset), "{0}.input2X".format(divide_node))

        if self.jnt_length_attr.value == 3:  # both.
            mc.connectAttr("{0}.outputX".format(divide_node), "{0}.translateY".format(tip_jnt))
            self._volume_setup()
            return

        condition_node = mc.createNode("condition", n="{0}_condition".format(self.name))
        mc.setAttr("{0}.secondTerm".format(condition_node), distance)
        mc.setAttr("{0}.colorIfFalseR".format(condition_node), distance)
        mc.connectAttr("{0}.outputX".format(divide_node), "{0}.firstTerm".format(condition_node))
        mc.connectAttr("{0}.outputX".format(divide_node), "{0}.colorIfTrueR".format(condition_node))

        if self.jnt_length_attr.value == 1:  # expendable.
            mc.setAttr("{0}.operation".format(condition_node), 2)  # greater than.
        else:  # shrinkable.
            mc.setAttr("{0}.operation".format(condition_node), 4)  # less than.

        mc.connectAttr("{0}.outColorR".format(condition_node), "{0}.translateY".format(tip_jnt))
        self._volume_setup()

    def _volume_setup(self):
        """Setup volume when expanding or shrinking. """
        if not self.volume_attr.value:
            return

        root_jnt = self.root_joint.pointer
        tip_jnt = self.tip_joint.pointer
        root_ctrl = self.root_ctrl.pointer

        root_ctrl.add_spacer_attr()
        volume_attr = root_ctrl.add_attr("volume", dv=0, min=0, smx=1, keyable=True)

        volume_node = mc.createNode("multiplyDivide", n="{0}_volume_attr_multiplyDivide".format(self.name))
        mc.setAttr("{0}.operation".format(volume_node), 2)  # divide.
        mc.setAttr("{0}.input1X".format(volume_node), mc.getAttr("{0}.translateY".format(tip_jnt)))
        mc.connectAttr("{0}.translateY".format(tip_jnt), "{0}.input2X".format(volume_node))

        blend_node = mc.createNode("blendTwoAttr", n="{0}_volume_attr_blendTwoAttr".format(self.name))
        mc.connectAttr(volume_attr, "{0}.attributesBlender".format(blend_node))
        mc.setAttr("{0}.input[0]".format(blend_node), 1.0)
        mc.connectAttr("{0}.outputX".format(volume_node), "{0}.input[1]".format(blend_node))
        mc.connectAttr("{0}.output".format(blend_node), "{0}.scaleX".format(root_jnt))
        mc.connectAttr("{0}.output".format(blend_node), "{0}.scaleZ".format(root_jnt))
