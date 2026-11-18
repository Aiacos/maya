"""A vehicle body/chassis node. """

from arise.utils import tagging_utils
from arise.data_types import node_data
from arise.utils.matrix_utils import matrix_constraint
from arise.utils.io_nodes.io_transform import IoTransform
from arise.utils.modules_utils import (
    secondary_ctrls_setup, expose_rotation_order, create_grps, SECONDARY_COLOR, update_ctrls, MULT_DL,
    MULT_DL_INPUT1, MULT_DL_INPUT2,
)

import maya.cmds as mc

MAYA_VERSION = 2016  # the version of maya from which this module supports.
AUTHOR = "Etay Herz"  # name of person who created this module.
RIG_CATEGORY = "Mechanical"  # either 'Basic', 'Cartoon', 'Vfx', 'Game' or 'All'. (used when filtering).
RIG_TYPE = "Vehicle"  # Biped, Vehicle, Quadruped, All, ... (for filtering modules in lists).
TAGS = ["chassis", "vehicle", "car", "truck", "steering", "mechanical", "Undercarriage"]
TOOL_TIP = "Vehicle body/chassis with steering ctrl, shake attributes, understeer, oversteer, and more."

LABELS_LIST = ["L_front", "R_front", "L_back", "R_back"]

node_data.NodeData.update_ctrls = update_ctrls


class Vehicle_Body(node_data.NodeData):
    """A vehicle body/chassis node. """
    sort_priority = 1000

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

        self.expose_rotation_order_attr = self.add_boolean_attribute(
            name="Expose RotateOrder",
            default_value=True,
            annotation="Exposes the ctrls 'RotateOrder' attribute in the Channel Box.",
            help_link="https://youtu.be/-1fpRw6oJME?t=149",
        )
        self.secondary_ctrls_attr = self.add_boolean_attribute(
            name="Secondary Ctrls",
            default_value=True,
            annotation="Secondary ctrl is added under the drive ctrl to help prevent gimbal lock.",
            help_link="https://youtu.be/-1fpRw6oJME?t=157",
        )

        self.add_separator()

        self.tilt_attr = self.add_boolean_attribute(
            name="Tilt",
            default_value=True,
            annotation="Add a tilt ctrl to tilt the whole vehicle from side to side.",
        )

        self.oversteer_attr = self.add_boolean_attribute(
            name="Handling",
            default_value=True,
            annotation="Add 'oversteer' and 'understeer' attributes to the driver ctrl.",
        )

        self.add_frame_layout("Shake")
        self.shake_attr = self.add_boolean_attribute(
            name="Shake",
            default_value=True,
            annotation="Add shake attributes to the driver ctrl.",
        )

        self.up_shake_attr = self.add_float_attribute(
            name="Shake Up Down Amount",
            default_value=0.2,
            annotation="In Maya units, provide a range of how much vertical shaking will the vehicle experience.",
            min_value=0.0,
        )

        self.rotate_shake_attr = self.add_float_attribute(
            name="Shake Rotate Amount",
            default_value=0.2,
            annotation="In degrees, how much will the vehicle shake for 'front_back' and 'left_right'.",
            min_value=0.0,
        )
        self.close_layout()

        self.add_frame_layout("Wheels Suspension")
        self.enable_wheels_attr = self.add_boolean_attribute(
            name="Add Four Wheels",
            default_value=False,
            annotation=(
                "Add four wheels to the vehicle. Each wheel will have its own suspension affecting the body.\n"
                "A re-template is required to position the wheels guides."
                ),
        )
        self.suspension_up_attr = self.add_float_attribute(
            name="Suspension Upper Limit",
            default_value=10.0,
            annotation="The limit each wheel can move up before affecting the vehicle body.",
            min_value=0.0,
        )

        self.suspension_low_attr = self.add_float_attribute(
            name="Suspension Lower Limit",
            default_value=-10.0,
            annotation="The limit each wheel can move down before affecting the vehicle body.",
            max_value=0.0,
        )
        self.close_layout()

        self.add_separator(title="Connections")
        self.driven_attr = self.add_driven_attribute(name="Input", annotation="Input")

        self.body_driver_attr = self.add_driver_attribute(name="Body Output", annotation="Output")
        self.front_wheels_driver_attr = self.add_driver_attribute(name="Front Wheels Output", annotation="Output")
        self.back_wheels_driver_attr = self.add_driver_attribute(name="Back Wheels Output",annotation="Output")

        self.close_layout()

    def evaluate_creation_methods(self):  # REIMPLEMENTED!
        """Reimplemented to enable/disable attrs. """
        self.up_shake_attr.set_disabled(False if self.shake_attr.value else True)
        self.rotate_shake_attr.set_disabled(False if self.shake_attr.value else True)
        self.suspension_up_attr.set_disabled(False if self.enable_wheels_attr.value else True)
        self.suspension_low_attr.set_disabled(False if self.enable_wheels_attr.value else True)

        node_data.NodeData.evaluate_creation_methods(self)

    def guides_creation(self):
        """Create guides based on attributes values. """
        self.center_guide = self.add_guide(name="center", translation=[0, 66, 0])
        self.center_guide.shape = "square"
        self.center_guide.size = 90
        self.center_guide.scale_offset = [1, 1, 1.8]

        self.left_guide = self.add_guide(name="left", parent=self.center_guide, translation=[90, 0, 0])
        self.left_guide.shape = "square"
        self.left_guide.size = 10
        self.left_guide.scale_offset = [1, 1, 3]

        self.right_guide = self.add_guide(name="right", parent=self.center_guide, translation=[-90, 0, 0])
        self.right_guide.shape = "square"
        self.right_guide.size = 10
        self.right_guide.scale_offset = [1, 1, 3]

        self.front_guide = self.add_guide(name="front", parent=self.center_guide, translation=[0, 0, 162])
        self.front_guide.shape = "square"
        self.front_guide.size = 10
        self.front_guide.scale_offset = [3, 1, 1]

        self.back_guide = self.add_guide(name="back", parent=self.center_guide, translation=[0, 0, -162])
        self.back_guide.shape = "square"
        self.back_guide.size = 10
        self.back_guide.scale_offset = [3, 1, 1]

        self.tilt_guide = self.add_guide(name="tilt_ctrl", parent=self.center_guide, translation=[0, 235, 0])
        self.tilt_guide.shape = "arrow_rotation_4_way"
        self.tilt_guide.size = 30

        self.wheels_guides = []
        if self.enable_wheels_attr.value:
            positions_list = [[90, 0, 86], [-90, 0, 86], [90, 0, -86], [-90, 0, -86]]
            for label, pos in zip(LABELS_LIST, positions_list):
                btm_guide = self.add_aim_guide(name="{0}_wheel_base".format(label), translation=pos)
                btm_guide.shape = "box"
                btm_guide.size = 5
                btm_guide.scale_offset = [1, 0.2, 1]
                btm_guide.translate_offset = [0.0, 0.5, 0.0]
                btm_guide.arrow_size = 4
                btm_guide.parent = self.center_guide

                center_guide = self.add_aim_guide(
                    name="{0}_wheel_center".format(label),
                    aim_at_guide=btm_guide,
                    parent=btm_guide,
                    translation=[pos[0], pos[1] + 19, pos[2]],
                    side_pin_guide=btm_guide,
                )
                center_guide.size = 3
                center_guide.side_pin_size = 0.5
                center_guide.aim_rotation_offset = (180, 0, 0)

                btm_guide.aim_at = center_guide
                self.wheels_guides.append([label, btm_guide, center_guide])

    def post_guides_creation(self):  # REIMPLEMENTED!
        """Create cylinders for visual representation of the wheels radius. """
        new_nodes = []

        if self.enable_wheels_attr.value:
            display_grp = IoTransform(name="{0}_cylinders_display_grp".format(self.name))
            display_grp.lock_and_hide_transformations()
            display_grp.parent_relative(self.guide_manager.io_guides_list[0].offset_grp)
            new_nodes.append(display_grp)

        for label, btm_guide, center_guide in self.wheels_guides:
            center_guide_side_null = center_guide.guide_ptr.side_null
            center_guide = center_guide.guide_ptr.transform
            btm_guide = btm_guide.guide_ptr.transform

            cylinder_shape = IoTransform("{0}_{1}_radius_cylinder".format(self.name, label), existing=False)
            cylinder_shape.create_shape(
                shape="cylinder",
                up_orient="+Y",
                size=[1, 0.25, 1],
                trans_offset=[0.125, 0, 0],
                rotate_offset=[0, 0, 90],
            )
            cylinder_shape.set_line_width(2)
            cylinder_shape.parent_relative(display_grp)
            new_nodes.append(cylinder_shape)

            point_constraint = cylinder_shape.point_constraint_to(center_guide, maintainOffset=False)
            new_nodes.append(IoTransform(point_constraint, existing=True))

            aim_constraint = cylinder_shape.aim_constraint_to(
                btm_guide,
                aimVector=[0, -1, 0],
                upVector=[1, 0, 0],
                worldUpType="object",
                worldUpObject=center_guide_side_null,
                maintainOffset=False,
            )
            new_nodes.append(IoTransform(aim_constraint, existing=True))

            loc_a = mc.spaceLocator(name="{0}_{1}_cylinder_scale_A_loc".format(self.name, label))[0]
            loc_a = IoTransform(loc_a, existing=True)
            loc_a.parent_relative(center_guide)
            loc_a.set_visibility(False)
            loc_a.lock_and_hide_transformations()
            new_nodes.append(loc_a)

            loc_b = mc.spaceLocator(name="{0}_{1}_cylinder_scale_B_loc".format(self.name, label))[0]
            loc_b = IoTransform(loc_b, existing=True)
            loc_b.set_visibility(False)
            loc_b.parent_relative(btm_guide)
            loc_b.lock_and_hide_transformations()
            new_nodes.append(loc_b)

            scale_node = mc.createNode("distanceBetween", name="{0}_{1}_cylinder_scale_distanceBetween".format(self.name, label))
            mc.connectAttr(loc_a.attr("worldMatrix[0]"), "{0}.inMatrix1".format(scale_node))
            mc.connectAttr(loc_b.attr("worldMatrix[0]"), "{0}.inMatrix2".format(scale_node))
            new_nodes.append(scale_node)

            scale_attr = "{0}.distance".format(scale_node)
            mc.connectAttr(scale_attr, cylinder_shape.attr("scaleX"))
            mc.connectAttr(scale_attr, cylinder_shape.attr("scaleY"))
            mc.connectAttr(scale_attr, cylinder_shape.attr("scaleZ"))

            cylinder_shape.set_templated(True)
            cylinder_shape.lock_and_hide_transformations()

        if new_nodes:
            tagging_utils.tag_nodes(new_nodes, tag=self.uuid.hex)

    def joints_creation(self):
        """Create joints based on attributes values and guides. Without positioning as this point. """
        self.joint = self.add_joint(name="center", skinning_jnt=True, tag_parent_jnt=None, radius=0.5)

        self.wheels_joints = []
        if self.enable_wheels_attr.value:
            for label in LABELS_LIST:
                wheel_joint = self.add_joint(
                    name="{0}_center".format(label),
                    skinning_jnt=True,
                    tag_parent_jnt=self.joint,
                    radius=0.5,
                )
                self.wheels_joints.append(wheel_joint)

    def ctrls_creation(self):
        """Create controls based on attributes values, guides and joints. Without positioning as this point. """
        ctrls_mult = self.ctrls_scale_attr.value

        size = [value * ctrls_mult for value in [90.0, 1.0, 162.0]]
        self.drive_ctrl = self.add_ctrl(name="drive", shape="square_with_arrow", up_orient="+Y", size=size)

        self.drive_ctrl.add_locked_hidden_attr("scaleY")
        self.drive_ctrl.add_locked_hidden_attr("scaleZ")

        self.drive_2ry_ctrl = None
        if self.secondary_ctrls_attr.value:
            size = [value * ctrls_mult for value in [85.0, 1.0, 157.0]]
            self.drive_2ry_ctrl = self.add_ctrl(name="drive_secondary", shape="square", size=size)
            self.drive_2ry_ctrl.color = SECONDARY_COLOR

            for attr in ["scaleX", "scaleY", "scaleZ"]:
                self.drive_2ry_ctrl.add_locked_hidden_attr(attr)

        self.front_steer_ctrl = self.add_ctrl(name="front_steer", shape="arrow_rotation_2_way", size=20*ctrls_mult)
        self.front_steer_ctrl.translate_offset = [0, 0, 50.0 * ctrls_mult]
        self.front_steer_ctrl.rotate_offset = [90, 0, 90]

        self.back_steer_ctrl = self.add_ctrl(name="back_steer", shape="arrow_rotation_2_way",size=20*ctrls_mult)
        self.back_steer_ctrl.translate_offset = [0, 0, -50.0 * ctrls_mult]
        self.back_steer_ctrl.rotate_offset = [-90, 0, 90]

        for attr in ["translateX", "translateY", "translateZ", "rotateX", "rotateZ", "scaleX", "scaleY", "scaleZ"]:
            for ctrl in [self.front_steer_ctrl, self.back_steer_ctrl]:
                ctrl.add_locked_hidden_attr(attr)

        self.tilt_ctrl = None
        if self.tilt_attr.value:
            self.tilt_ctrl = self.add_ctrl(name="tilt", shape="arrow_rotation_4_way", size=30 * ctrls_mult)

            for attr in ["translateX", "translateY", "translateZ", "rotateY", "scaleX", "scaleY", "scaleZ"]:
                self.tilt_ctrl.add_locked_hidden_attr(attr)

            for attr in ["rotateX", "rotateZ"]:
                self.tilt_ctrl.add_limit_attr(attr, min_active=True, min_value=-180, max_active=True, max_value=180)

        self.wheels_ctrls = []
        if self.enable_wheels_attr.value:
            for label in LABELS_LIST:
                self.wheels_ctrls.append(wheels_utils.create_wheel_ctrls(self, label, ctrls_mult))

            self.wheels_ctrls[1][1].translate_offset = [-10.0 * ctrls_mult, 0, 0]  # R_front ctrl is flipped.
            self.wheels_ctrls[1][3].translate_offset = [-10.0 * ctrls_mult, 0, 0]
            self.wheels_ctrls[3][1].translate_offset = [-10.0 * ctrls_mult, 0, 0]  # R_back ctrl is flipped.
            self.wheels_ctrls[3][3].translate_offset = [-10.0 * ctrls_mult, 0, 0]

    def maya_attrs_creation(self):
        """Declare any Maya attributes that users should be able to modify. """
        if self.oversteer_attr.value:
            self.drive_ctrl.add_maya_attr("oversteer_wheels_mult", attr_type="float", default_value=1, min=0, max=1)
            self.drive_ctrl.add_maya_attr("understeer_wheels_mult", attr_type="float", default_value=1, min=0, max=1)

        if self.shake_attr.value:
            self.drive_ctrl.add_maya_attr("shake_mult", attr_type="float", default_value=10, min=0, max=1000)
            self.drive_ctrl.add_maya_attr("up_down_amount", attr_type="float", default_value=1, min=0, max=1000)
            self.drive_ctrl.add_maya_attr("front_back_amount", attr_type="float", default_value=1, min=0, max=1000)
            self.drive_ctrl.add_maya_attr("left_right_amount", attr_type="float", default_value=1, min=0, max=1000)
            self.drive_ctrl.add_maya_attr("up_down_speed", attr_type="float", default_value=7, min=0, max=10)
            self.drive_ctrl.add_maya_attr("front_back_speed", attr_type="float", default_value=7, min=0, max=10)
            self.drive_ctrl.add_maya_attr("left_right_speed", attr_type="float", default_value=7, min=0, max=10)

        if self.enable_wheels_attr.value:
            for ctrls in self.wheels_ctrls:
                ctrls[0].add_maya_attr("suspension_up_limit", attr_type="float", default_value=10, min=0, max=1000)
                ctrls[0].add_maya_attr("suspension_down_limit", attr_type="float", default_value=-10, min=-1000, max=0)

    def rig_creation(self):
        """Using the attributes values, guides, joints, and ctrls, build the rig. """
        if self.is_mirrored:
            self.module_grp.set_attr("scaleX", -1)

        input_grp, body_output_grp = create_grps(self, ["input_grp", "body_output_grp"])
        ctrls_grp, jnts_grp = create_grps(self, ["ctrls_grp", "jnts_grp"])
        self.front_wheels_output_grp = create_grps(self, ["front_wheels_output_grp"])[0]
        self.back_wheels_output_grp = create_grps(self, ["back_wheels_output_grp"])[0]

        input_grp.add_attr("steer", dv=0, keyable=True)

        self.driven_attr.set_maya_object(input_grp)
        self.body_driver_attr.set_maya_object(body_output_grp)
        self.front_wheels_driver_attr.set_maya_object(self.front_wheels_output_grp)
        self.back_wheels_driver_attr.set_maya_object(self.back_wheels_output_grp)

        front_wheels_steer_attr = self.front_wheels_output_grp.add_attr("steer", dv=0, keyable=True)
        back_wheels_steer_attr = self.back_wheels_output_grp.add_attr("steer", dv=0, keyable=True)

        joint = self.joint.pointer
        driver_ctrl = self.drive_ctrl.pointer
        front_steer_ctrl = self.front_steer_ctrl.pointer
        back_steer_ctrl = self.back_steer_ctrl.pointer

        driver_ctrl.scale_attrs_connect()
        secondary_ctrls_setup([driver_ctrl], [self.drive_2ry_ctrl])

        if self.expose_rotation_order_attr.value:
            expose_rotation_order(
                [driver_ctrl, driver_ctrl.btm_ctrl, front_steer_ctrl, back_steer_ctrl, self.tilt_ctrl]
            )

        driver_ctrl.set_attr("rotateOrder", 1)  # YZX.
        driver_ctrl.btm_ctrl.set_attr("rotateOrder", 1)  # YZX.

        input_grp.set_matrix(self.center_guide.world_transformations["matrix"], space="world")
        input_grp.set_scale([1, 1, 1])

        driver_ctrl.offset_grp.parent_relative(ctrls_grp)
        ctrls_grp.match_transformation_to(input_grp)

        # front_steer_ctrl setup.
        short_name = front_steer_ctrl.short_name
        front_steer_ctrl.offset_grp.parent_relative(driver_ctrl.btm_ctrl)

        name = "{0}_position_grp".format(short_name)
        front_steer_ctrl.position_grp = front_steer_ctrl.offset_grp.add_group_above(name)
        front_steer_ctrl.position_grp.set_matrix(self.front_guide.world_transformations["matrix"], space="world")
        front_steer_ctrl.position_grp.set_scale([1, 1, 1])

        name = "{0}_driven_grp".format(short_name)
        front_steer_ctrl.driven_grp = front_steer_ctrl.offset_grp.add_group_above(name)
        front_steer_ctrl.driven_grp.connect_attr("rotateY", input_grp.attr("steer"))

        front_steer_ctrl.front_steer_pma = mc.createNode("plusMinusAverage", name="{0}_PMA".format(short_name))
        mc.setAttr("{0}.operation".format(front_steer_ctrl.front_steer_pma), 1)  # add.

        mc.connectAttr(
            "{0}.rotateY".format(front_steer_ctrl),
            "{0}.input1D[0]".format(front_steer_ctrl.front_steer_pma),
        )

        mc.connectAttr(
            "{0}.rotateY".format(front_steer_ctrl.driven_grp),
            "{0}.input1D[1]".format(front_steer_ctrl.front_steer_pma),
        )

        mc.connectAttr("{0}.output1D".format(front_steer_ctrl.front_steer_pma), front_wheels_steer_attr)

        # back_steer_ctrl setup.
        short_name = back_steer_ctrl.short_name
        back_steer_ctrl.offset_grp.parent_relative(driver_ctrl.btm_ctrl)

        name = "{0}_position_grp".format(short_name)
        back_steer_ctrl.position_grp = back_steer_ctrl.offset_grp.add_group_above(name)
        back_steer_ctrl.position_grp.set_matrix(self.back_guide.world_transformations["matrix"], space="world")
        back_steer_ctrl.position_grp.set_scale([1, 1, 1])

        name = "{0}_driven_grp".format(short_name)
        back_steer_ctrl.driven_grp = back_steer_ctrl.offset_grp.add_group_above(name)

        back_steer_ctrl.back_steer_pma = mc.createNode("plusMinusAverage", name="{0}_PMA".format(short_name))
        mc.setAttr("{0}.operation".format(back_steer_ctrl.back_steer_pma), 1)  # add.

        mc.connectAttr(
            "{0}.rotateY".format(back_steer_ctrl),
            "{0}.input1D[0]".format(back_steer_ctrl.back_steer_pma),
        )

        mc.connectAttr(
            "{0}.rotateY".format(back_steer_ctrl.driven_grp),
            "{0}.input1D[1]".format(back_steer_ctrl.back_steer_pma),
        )

        mc.connectAttr(
            "{0}.output1D".format(back_steer_ctrl.back_steer_pma),
            back_wheels_steer_attr,
        )

        if self.oversteer_attr.value:
            self.oversteer_understeer_setup(driver_ctrl, front_steer_ctrl)

        driver_ctrl.driver_grp = IoTransform("{0}_driver_grp".format(self.name), existing=False)
        driver_ctrl.driver_grp.parent_relative(driver_ctrl.btm_ctrl)

        if self.tilt_attr.value:
            self.tilt_setup(driver_ctrl)

        joint.offset_grp = joint.add_group_above("{0}_offset_grp".format(joint.short_name))
        joint.offset_grp.parent_relative(jnts_grp)

        matrix_constraint(driver_ctrl.driver_grp, self.front_wheels_output_grp, maintain_offset=False)
        matrix_constraint(driver_ctrl.driver_grp, self.back_wheels_output_grp, maintain_offset=False)
        matrix_constraint(input_grp, ctrls_grp, maintain_offset=False)
        matrix_constraint(joint, body_output_grp, maintain_offset=False)

        if self.shake_attr.value:
            self.shake_setup(driver_ctrl, joint)

        if self.enable_wheels_attr.value:
            self.wheels_top_grp = IoTransform("{0}_wheels_top_grp".format(self.name), existing=False)
            self.wheels_top_grp.parent_relative(self.module_grp)

            front_l_wheel = wheels_utils.create_wheel_setup(
                node=self,
                guides=self.wheels_guides[0],
                ctrls_list=self.wheels_ctrls[0],
                joint=self.wheels_joints[0],
                label=LABELS_LIST[0],
            )
            matrix_constraint(self.front_wheels_output_grp, front_l_wheel[0], maintain_offset=True)
            front_l_wheel[0].connect_attr("steer", self.front_wheels_output_grp.attr("steer"))

            front_r_wheel = wheels_utils.create_wheel_setup(
                node=self,
                guides=self.wheels_guides[1],
                ctrls_list=self.wheels_ctrls[1],
                joint=self.wheels_joints[1],
                label=LABELS_LIST[1],
            )
            matrix_constraint(self.front_wheels_output_grp, front_r_wheel[0], maintain_offset=True)
            front_r_wheel[0].connect_attr("steer", self.front_wheels_output_grp.attr("steer"))

            back_l_wheel = wheels_utils.create_wheel_setup(
                node=self,
                guides=self.wheels_guides[2],
                ctrls_list=self.wheels_ctrls[2],
                joint=self.wheels_joints[2],
                label=LABELS_LIST[2],
            )
            matrix_constraint(self.back_wheels_output_grp, back_l_wheel[0], maintain_offset=True)
            back_l_wheel[0].connect_attr("steer", self.back_wheels_output_grp.attr("steer"))

            back_r_wheel = wheels_utils.create_wheel_setup(
                node=self,
                guides=self.wheels_guides[3],
                ctrls_list=self.wheels_ctrls[3],
                joint=self.wheels_joints[3],
                label=LABELS_LIST[3],
            )
            matrix_constraint(self.back_wheels_output_grp, back_r_wheel[0], maintain_offset=True)
            back_r_wheel[0].connect_attr("steer", self.back_wheels_output_grp.attr("steer"))

            wheels_locs = [front_l_wheel[2], front_r_wheel[2], back_l_wheel[2], back_r_wheel[2]]
            self.suspension_loc = wheels_utils.suspension_loc_setup(node=self, locs=wheels_locs)

        if self.enable_wheels_attr.value:
            jnts_grp.match_transformation_to(driver_ctrl)
            matrix_constraint(
                self.suspension_loc,
                jnts_grp,
                maintain_offset=True,
                skip_attrs=(False, False, False, False, False, False, True, True, True),
            )
            mc.scaleConstraint(driver_ctrl.driver_grp, jnts_grp, mo=True)
            mc.scaleConstraint(driver_ctrl.driver_grp, self.wheels_top_grp, mo=True)

        else:
            matrix_constraint(driver_ctrl.driver_grp, jnts_grp, maintain_offset=False)

    def oversteer_understeer_setup(self, driver_ctrl, front_steer_ctrl):
        """ Create oversteer and understeer attributes and connect them to new groups above the driver ctrl.

        Args:
            driver_ctrl (IoCtrl): The driver ctrl.
            front_steer_ctrl (IoCtrl): The front steer ctrl.
        """
        short_name = driver_ctrl.short_name
        driver_ctrl.oversteer = driver_ctrl.offset_grp.add_group_above("{0}_oversteer_grp".format(short_name))
        driver_ctrl.understeer = driver_ctrl.offset_grp.add_group_above("{0}_understeer_grp".format(short_name))
        driver_ctrl.reposition = driver_ctrl.offset_grp.add_group_above("{0}_reposition_grp".format(short_name))

        ctrl_matrix = driver_ctrl.get_matrix(space="world")

        driver_ctrl.oversteer.set_matrix(self.front_guide.world_transformations["matrix"], space="world")
        driver_ctrl.oversteer.set_scale([1, 1, 1])

        driver_ctrl.understeer.set_matrix(self.back_guide.world_transformations["matrix"], space="world")
        driver_ctrl.understeer.set_scale([1, 1, 1])

        driver_ctrl.reposition.set_matrix(ctrl_matrix)
        driver_ctrl.reposition.set_scale([1, 1, 1])

        driver_ctrl.add_spacer_attr()
        oversteer_attr = driver_ctrl.add_attr("oversteer", dv=0, keyable=True)
        oversteer_mult_attr = driver_ctrl.add_attr("oversteer_wheels_mult", dv=1, min=0, max=1, k=True)
        understeer_attr = driver_ctrl.add_attr("understeer", dv=0, keyable=True)
        understeer_mult_attr = driver_ctrl.add_attr("understeer_wheels_mult", dv=1, min=0, max=1, k=True)
        driver_ctrl.add_spacer_attr()

        mc.connectAttr(oversteer_attr, "{0}.rotateY".format(driver_ctrl.oversteer))
        mc.connectAttr(understeer_attr, "{0}.rotateY".format(driver_ctrl.understeer))

        short_name = front_steer_ctrl.short_name
        name = "{0}_oversteer_grp".format(short_name)
        front_steer_ctrl.oversteer = front_steer_ctrl.offset_grp.add_group_above(name)

        name = "{0}_understeer_grp".format(short_name)
        front_steer_ctrl.understeer = front_steer_ctrl.offset_grp.add_group_above(name)

        oversteer_reverse = mc.createNode(MULT_DL, name="{0}_oversteer_reverse".format(short_name))
        oversteer_mult = mc.createNode(MULT_DL, name="{0}_oversteer_mult".format(short_name))

        mc.connectAttr(oversteer_attr, "{0}.{1}".format(oversteer_reverse, MULT_DL_INPUT1))
        mc.setAttr("{0}.{1}".format(oversteer_reverse, MULT_DL_INPUT2), -1)
        mc.connectAttr("{0}.output".format(oversteer_reverse), "{0}.{1}".format(oversteer_mult, MULT_DL_INPUT1))
        mc.connectAttr(oversteer_mult_attr, "{0}.{1}".format(oversteer_mult, MULT_DL_INPUT2))
        mc.connectAttr(
            "{0}.output".format(oversteer_mult),
            "{0}.rotateY".format(front_steer_ctrl.oversteer),
        )

        mc.connectAttr(
            "{0}.rotateY".format(front_steer_ctrl.oversteer),
            "{0}.input1D[2]".format(front_steer_ctrl.front_steer_pma),
        )

        understeer_reverse = mc.createNode(MULT_DL, name="{0}_understeer_reverse".format(short_name))
        understeer_mult = mc.createNode(MULT_DL, name="{0}_understeer_mult".format(short_name))

        mc.connectAttr(understeer_attr, "{0}.{1}".format(understeer_reverse, MULT_DL_INPUT1))
        mc.setAttr("{0}.{1}".format(understeer_reverse, MULT_DL_INPUT2), -1)
        mc.connectAttr("{0}.output".format(understeer_reverse), "{0}.{1}".format(understeer_mult, MULT_DL_INPUT1))
        mc.connectAttr(understeer_mult_attr, "{0}.{1}".format(understeer_mult, MULT_DL_INPUT2))
        mc.connectAttr(
            "{0}.output".format(understeer_mult),
            "{0}.rotateY".format(front_steer_ctrl.understeer),
        )
        mc.connectAttr(
            "{0}.rotateY".format(front_steer_ctrl.understeer),
            "{0}.input1D[3]".format(front_steer_ctrl.front_steer_pma),
        )

    def tilt_setup(self, driver_ctrl):
        """Setup the tilt ctrl.

        Args:
            driver_ctrl (IoCtrl): The driver ctrl.
        """
        short_name = driver_ctrl.short_name
        driver_ctrl.front_tilt = driver_ctrl.driver_grp.add_group_above("{0}_front_tilt_grp".format(short_name))
        driver_ctrl.back_tilt = driver_ctrl.driver_grp.add_group_above("{0}_back_tilt_grp".format(short_name))
        driver_ctrl.left_tilt = driver_ctrl.driver_grp.add_group_above("{0}_left_tilt_grp".format(short_name))
        driver_ctrl.right_tilt = driver_ctrl.driver_grp.add_group_above("{0}_right_tilt_grp".format(short_name))

        driver_ctrl.front_tilt.set_matrix(self.front_guide.world_transformations["matrix"], space="world")
        driver_ctrl.front_tilt.set_scale([1, 1, 1])

        driver_ctrl.back_tilt.set_matrix(self.back_guide.world_transformations["matrix"], space="world")
        driver_ctrl.back_tilt.set_scale([1, 1, 1])

        driver_ctrl.left_tilt.set_matrix(self.left_guide.world_transformations["matrix"], space="world")
        driver_ctrl.left_tilt.set_scale([1, 1, 1])

        driver_ctrl.right_tilt.set_matrix(self.right_guide.world_transformations["matrix"], space="world")
        driver_ctrl.right_tilt.set_scale([1, 1, 1])

        driver_ctrl.driver_grp.match_transformation_to(driver_ctrl)

        tilt_ctrl = self.tilt_ctrl.pointer
        tilt_ctrl.offset_grp.parent_relative(driver_ctrl.btm_ctrl)

        tilt_ctrl.offset_grp.set_matrix(self.tilt_guide.world_transformations["matrix"], space="world")
        tilt_ctrl.set_scale([1, 1, 1])

        tilt_ctrl.offset_grp.parent(driver_ctrl.btm_ctrl)

        x_tilt_mult = mc.createNode(MULT_DL, name="{0}_x_tilt_multDoubleLinear".format(self.name))
        z_tilt_mult = mc.createNode(MULT_DL, name="{0}_z_tilt_multDoubleLinear".format(self.name))

        mc.setAttr("{0}.{1}".format(x_tilt_mult, MULT_DL_INPUT2), 1.0)
        mc.setAttr("{0}.{1}".format(z_tilt_mult, MULT_DL_INPUT2), 1.0)

        mc.connectAttr("{0}.rotateX".format(tilt_ctrl), "{0}.{1}".format(x_tilt_mult, MULT_DL_INPUT1))
        mc.connectAttr("{0}.rotateZ".format(tilt_ctrl), "{0}.{1}".format(z_tilt_mult, MULT_DL_INPUT1))

        positive_clamp = mc.createNode("clamp", name="{0}_positive_clamp".format(self.name))
        negative_clamp = mc.createNode("clamp", name="{0}_negative_clamp".format(self.name))

        mc.setAttr("{0}.min".format(positive_clamp), 0, 0, 0)
        mc.setAttr("{0}.max".format(positive_clamp), 180, 180, 180)

        mc.setAttr("{0}.min".format(negative_clamp), -180, -180, -180)
        mc.setAttr("{0}.max".format(negative_clamp), 0, 0, 0)

        mc.connectAttr("{0}.output".format(x_tilt_mult), "{0}.inputR".format(positive_clamp))
        mc.connectAttr("{0}.output".format(x_tilt_mult), "{0}.inputR".format(negative_clamp))

        mc.connectAttr("{0}.output".format(z_tilt_mult), "{0}.inputB".format(positive_clamp))
        mc.connectAttr("{0}.output".format(z_tilt_mult), "{0}.inputB".format(negative_clamp))

        mc.connectAttr("{0}.outputR".format(positive_clamp), "{0}.rotateX".format(driver_ctrl.front_tilt))
        mc.connectAttr("{0}.outputR".format(negative_clamp), "{0}.rotateX".format(driver_ctrl.back_tilt))

        mc.connectAttr("{0}.outputB".format(negative_clamp), "{0}.rotateZ".format(driver_ctrl.left_tilt))
        mc.connectAttr("{0}.outputB".format(positive_clamp), "{0}.rotateZ".format(driver_ctrl.right_tilt))

    def shake_setup(self, driver_ctrl, joint):
        """ Create the shake attributes and connect them with animation nodes to a shake grp above the joint.

        Args:
            driver_ctrl (IoCtrl): The driver ctrl.
            joint (IoJoint): The joint.
        """

        driver_ctrl.add_spacer_attr()
        driver_ctrl.shake_mult = driver_ctrl.add_attr("shake_mult", dv=0, min=0,  keyable=True)
        driver_ctrl.up_down_amount = driver_ctrl.add_attr("up_down_amount", dv=1, min=0,  keyable=True)
        driver_ctrl.front_back_amount = driver_ctrl.add_attr("front_back_amount", dv=1, min=0,  keyable=True)
        driver_ctrl.left_right_amount = driver_ctrl.add_attr("left_right_amount", dv=1, min=0,  keyable=True)

        driver_ctrl.up_speed = driver_ctrl.add_attr(
            "up_down_speed",
            dv=7,
            min=0,
            hasSoftMaxValue=True,
            softMaxValue=10,
            keyable=True,
        )

        driver_ctrl.front_speed = driver_ctrl.add_attr(
            "front_back_speed",
            dv=7,
            min=0,
            hsx=True,
            softMaxValue=10,
            keyable=True,
        )

        driver_ctrl.left_speed = driver_ctrl.add_attr(
            "left_right_speed",
            dv=7,
            min=0,
            hsx=True,
            softMaxValue=10,
            keyable=True,
        )

        driver_ctrl.add_spacer_attr()

        joint.shake_grp = joint.offset_grp.add_group_above("{0}_shake_grp".format(joint.short_name))

        up_data = [driver_ctrl.up_speed, driver_ctrl.up_down_amount, "translateY", "up"]
        front_data = [driver_ctrl.front_speed, driver_ctrl.front_back_amount, "rotateX", "front"]
        left_data = [driver_ctrl.left_speed, driver_ctrl.left_right_amount, "rotateZ", "left"]

        animatable_nodes_list = []
        # create shake nodes for up_down, front_back and left_right.
        for speed_attr, amount_attr, attr, name in [up_data, front_data, left_data]:

            speed_mult = mc.createNode(MULT_DL, name="{0}_{1}_speed_multDoubleLinear".format(self.name, name))
            global_mult = mc.createNode(MULT_DL, name="{0}_{1}_global_multDoubleLinear".format(self.name, name))
            shake_mult = mc.createNode(MULT_DL, name="{0}_{1}_shake_multDoubleLinear".format(self.name, name))

            mc.connectAttr("time1.outTime", "{0}.{1}".format(speed_mult, MULT_DL_INPUT1))
            mc.connectAttr(speed_attr, "{0}.{1}".format(speed_mult, MULT_DL_INPUT2))

            mc.connectAttr(driver_ctrl.shake_mult, "{0}.{1}".format(global_mult, MULT_DL_INPUT1))
            mc.connectAttr(amount_attr, "{0}.{1}".format(global_mult, MULT_DL_INPUT2))

            mc.connectAttr("{0}.output".format(global_mult), "{0}.{1}".format(shake_mult, MULT_DL_INPUT2))

            anim_curve = mc.createNode("animCurveTA", name="{0}_{1}_animCurveTA".format(self.name, name))
            mc.setAttr("{0}.postInfinity".format(anim_curve), 5)  # oscillate.
            mc.setAttr("{0}.preInfinity".format(anim_curve), 5)  # oscillate.

            mc.connectAttr("{0}.output".format(speed_mult), "{0}.input".format(anim_curve))
            mc.connectAttr("{0}.output".format(anim_curve), "{0}.{1}".format(shake_mult, MULT_DL_INPUT1))
            mc.connectAttr("{0}.output".format(shake_mult), "{0}.{1}".format(joint.shake_grp, attr))
            animatable_nodes_list.append(shake_mult)

        # add keyframes to animation nodes with fake random.
        # up_down_amount.
        distance = self.up_shake_attr.value
        mc.setKeyframe(animatable_nodes_list[0], t=0, v=distance, attribute="input1")
        mc.setKeyframe(animatable_nodes_list[0], t=9, v=distance * -1.12, attribute="input1")
        mc.setKeyframe(animatable_nodes_list[0], t=16, v=distance * 0.85, attribute="input1")
        mc.setKeyframe(animatable_nodes_list[0], t=24, v=distance * -1.0, attribute="input1")
        mc.setKeyframe(animatable_nodes_list[0], t=32, v=distance * 1.1, attribute="input1")
        mc.setKeyframe(animatable_nodes_list[0], t=39, v=distance * -1.1, attribute="input1")

        # front_back_amount.
        rotation = self.rotate_shake_attr.value
        mc.setKeyframe(animatable_nodes_list[1], t=0, v=rotation, attribute="input1")
        mc.setKeyframe(animatable_nodes_list[1], t=8, v=rotation * -1.05, attribute="input1")
        mc.setKeyframe(animatable_nodes_list[1], t=15, v=rotation * 0.9, attribute="input1")
        mc.setKeyframe(animatable_nodes_list[1], t=22, v=rotation * -1.1, attribute="input1")
        mc.setKeyframe(animatable_nodes_list[1], t=29, v=rotation * 1.0, attribute="input1")
        mc.setKeyframe(animatable_nodes_list[1], t=35, v=rotation * -0.95, attribute="input1")
        mc.setKeyframe(animatable_nodes_list[1], t=42, v=rotation * 1.03, attribute="input1")

        # left_right_amount.
        mc.setKeyframe(animatable_nodes_list[2], t=0, v=rotation * 1.1, attribute="input1")
        mc.setKeyframe(animatable_nodes_list[2], t=10, v=rotation * -1.2, attribute="input1")
        mc.setKeyframe(animatable_nodes_list[2], t=19, v=rotation * 0.9, attribute="input1")
        mc.setKeyframe(animatable_nodes_list[2], t=26, v=rotation * -1.2, attribute="input1")
        mc.setKeyframe(animatable_nodes_list[2], t=35, v=rotation * 1.1, attribute="input1")
        mc.setKeyframe(animatable_nodes_list[2], t=43, v=rotation * -1.25, attribute="input1")
        mc.setKeyframe(animatable_nodes_list[2], t=50, v=rotation * 1.18, attribute="input1")
        mc.setKeyframe(animatable_nodes_list[2], t=58, v=rotation * -1.2, attribute="input1")
