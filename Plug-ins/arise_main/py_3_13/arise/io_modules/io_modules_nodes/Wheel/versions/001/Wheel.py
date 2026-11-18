"""Wheel node for vehicles. """

from arise.data_types import node_data
from arise.utils import tagging_utils
from arise.utils.math_utils import distance_between
from arise.utils.matrix_utils import matrix_constraint
from arise.utils.io_nodes.io_transform import IoTransform
from arise.utils.modules_utils import (
    secondary_ctrls_setup, expose_rotation_order, create_grps, SECONDARY_COLOR, create_module_scale, update_ctrls,
    MULT_DL, MULT_DL_INPUT1, MULT_DL_INPUT2
)
from arise.utils.tagging_utils import tag_as_delete_first

import maya.cmds as mc

MAYA_VERSION = 2016  # the version of maya from which this module supports.
AUTHOR = "Etay Herz"  # name of person who created this module.
RIG_CATEGORY = "Mechanical"  # either 'Basic', 'Cartoon', 'Vfx', 'Game' or 'All'. (used when filtering).
RIG_TYPE = "Vehicle"  # Biped, Vehicle, Quadruped, All, ... (for filtering modules in lists).
TAGS = ["basic", "wheel", "vehicle", "car", "truck", "tire", "steering", "mechanical"]
TOOL_TIP = "A vehicle wheel/tire."

node_data.NodeData.update_ctrls = update_ctrls


class Wheel(node_data.NodeData):
    """Wheel node for vehicles. """
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
            annotation="Secondary ctrl is added under the wheel ctrl to help prevent gimbal lock.",
            help_link="https://youtu.be/-1fpRw6oJME?t=157",
        )

        self.add_separator()

        self.auto_roll_attr = self.add_boolean_attribute(
            name="Auto Roll",
            default_value=True,
            annotation=(
                "Add an expression and nodes driven auto rotation mechanism for the wheel, enabling it to rotate\n"
                "automatically based on the distance traveled.\n"
                "It is important to note that in order to create accurate auto-rotation the entire time range\n"
                "should be played. Read more about this in the documentation."
            ),
        )

        self.add_separator(title="Connections")
        self.driven_attr = self.add_driven_attribute(name="Input", annotation="Input")
        self.driver_attr = self.add_driver_attribute(name="Output", annotation="Output")

        self.close_layout()

    def guides_creation(self):
        """Create guides based on attributes values. """
        self.btm_guide = self.add_aim_guide(name="wheel_bottom", translation=[75, 0, 0])
        self.btm_guide.shape = "box"
        self.btm_guide.size = 5
        self.btm_guide.scale_offset = [1, 0.2, 1]
        self.btm_guide.translate_offset = [0.0, 0.5, 0.0]
        self.btm_guide.arrow_size = 4

        self.center_guide = self.add_aim_guide(
            name="wheel_center",
            aim_at_guide=self.btm_guide,
            parent=self.btm_guide,
            translation=[75, 19, 0],
            side_pin_guide=self.btm_guide,
        )
        self.center_guide.size = 3
        self.center_guide.side_pin_size = 0.5
        self.center_guide.aim_rotation_offset = (180, 0, 0)

        self.btm_guide.aim_at = self.center_guide

    def post_guides_creation(self):  # REIMPLEMENTED!
        """Create a cylinder for visual representation of the wheel radius. """
        new_nodes = []
        center_guide = self.center_guide.guide_ptr.transform
        btm_guide = self.btm_guide.guide_ptr.transform
        center_guide_side_null = self.center_guide.guide_ptr.side_null

        display_grp = IoTransform(name="{0}_cylinder_shape_display_grp".format(self.name))
        display_grp.lock_and_hide_transformations()
        display_grp.parent_relative(self.guide_manager.io_guides_list[0].offset_grp)
        new_nodes.append(display_grp)

        self.cylinder_shape = IoTransform("{0}_radius_cylinder_display_shape".format(self.name), existing=False)
        self.cylinder_shape.create_shape(
            shape="cylinder",
            up_orient="+Y",
            size=[1, 0.25, 1],
            trans_offset=[0.125, 0, 0],
            rotate_offset=[0, 0, 90],
        )
        self.cylinder_shape.set_line_width(2)
        self.cylinder_shape.parent_relative(display_grp)
        new_nodes.append(self.cylinder_shape)

        point_constraint = self.cylinder_shape.point_constraint_to(center_guide, maintainOffset=False)
        new_nodes.append(IoTransform(point_constraint, existing=True))

        aim_constraint = self.cylinder_shape.aim_constraint_to(
            btm_guide,
            aimVector=[0, -1, 0],
            upVector=[1, 0, 0],
            worldUpType="object",
            worldUpObject=center_guide_side_null,
            maintainOffset=False,
        )
        new_nodes.append(IoTransform(aim_constraint, existing=True))

        loc_a = IoTransform(mc.spaceLocator(name="{0}_cylinder_scale_a_loc".format(self.name))[0], existing=True)
        loc_a.parent_relative(center_guide)
        loc_a.set_visibility(False)
        loc_a.lock_and_hide_transformations()
        new_nodes.append(loc_a)

        loc_b = IoTransform(mc.spaceLocator(name="{0}_cylinder_scale_b_loc".format(self.name))[0], existing=True)
        loc_b.set_visibility(False)
        loc_b.parent_relative(btm_guide)
        loc_b.lock_and_hide_transformations()
        new_nodes.append(loc_b)

        scale_node = mc.createNode("distanceBetween", name="{0}_cylinder_scale_distanceBetween".format(self.name))
        mc.connectAttr(loc_a.attr("worldMatrix[0]"), "{0}.inMatrix1".format(scale_node))
        mc.connectAttr(loc_b.attr("worldMatrix[0]"), "{0}.inMatrix2".format(scale_node))
        new_nodes.append(scale_node)

        scale_attr = "{0}.distance".format(scale_node)
        mc.connectAttr(scale_attr, self.cylinder_shape.attr("scaleX"))
        mc.connectAttr(scale_attr, self.cylinder_shape.attr("scaleY"))
        mc.connectAttr(scale_attr, self.cylinder_shape.attr("scaleZ"))

        self.cylinder_shape.set_templated(True)
        self.cylinder_shape.lock_and_hide_transformations()

        tagging_utils.tag_nodes(new_nodes, tag=self.uuid.hex)

    def joints_creation(self):
        """Create joints based on attributes values and guides. (without positioning as this point). """
        self.joint = self.add_joint(
            name="center",
            skinning_jnt=True,
            tag_parent_jnt=None,
            radius=0.5,
        )

    def ctrls_creation(self):
        """Create controls based on attributes values, guides and joints. (without positioning as this point). """
        ctrls_mult = self.ctrls_scale_attr.value

        self.btm_ctrl = self.add_ctrl(
            name="bottom",
            shape="box",
            up_orient="+Y",
            size=[value * ctrls_mult for value in [10.0, 1.0, 10.0]],
        )
        self.btm_ctrl.translate_offset = [0, ctrls_mult, 0]

        self.center_ctrl = self.add_ctrl(name="center", shape="rotate", up_orient="+X", size=10 * ctrls_mult)
        self.center_ctrl.translate_offset = [10.0 * ctrls_mult, 0, 0]

        for attr in ["rotateX", "scaleY", "scaleZ"]:
            self.btm_ctrl.add_locked_hidden_attr(attr)
            self.center_ctrl.add_locked_hidden_attr(attr)

        self.btm_2ry_ctrl = None
        self.center_2ry_ctrl = None
        if self.secondary_ctrls_attr.value:
            self.btm_2ry_ctrl = self.add_ctrl(name="bottom_secondary", shape="square", size=8.5 * ctrls_mult)
            self.btm_2ry_ctrl.color = SECONDARY_COLOR

            self.center_2ry_ctrl = self.add_ctrl(
                name="center_secondary",
                shape="circle",
                up_orient="+X",
                size=5.5 * ctrls_mult,
            )
            self.center_2ry_ctrl.translate_offset = [10.0 * ctrls_mult, 0, 0]
            self.center_2ry_ctrl.color = SECONDARY_COLOR

            for attr in ["rotateX", "scaleX", "scaleY", "scaleZ"]:
                self.btm_2ry_ctrl.add_locked_hidden_attr(attr)
                self.center_2ry_ctrl.add_locked_hidden_attr(attr)

    def rig_creation(self):
        """Using the attributes values, guides, joints, and ctrls, build the rig. """
        if self.is_mirrored:
            self.module_grp.set_attr("scaleX", -1)

        input_grp, output_grp, jnts_grp = create_grps(self, ["input_grp", "output_grp", "jnts_grp"])
        ctrls_grp = create_grps(self, ["ctrls_grp"])[0]

        self.driven_attr.set_maya_object(input_grp)
        self.driver_attr.set_maya_object(output_grp)

        input_grp.set_matrix(self.center_guide.world_transformations["matrix"], space="world")
        input_grp.set_scale([1, 1, 1])

        ctrls_grp.match_transformation_to(input_grp)

        btm_ctrl = self.btm_ctrl.pointer
        center_ctrl = self.center_ctrl.pointer
        joint = self.joint.pointer

        btm_ctrl.scale_attrs_connect()
        center_ctrl.scale_attrs_connect()

        secondary_ctrls_setup([btm_ctrl, center_ctrl], [self.btm_2ry_ctrl, self.center_2ry_ctrl])

        btm_ctrl.set_attr("rotateOrder", 2)  # ZXY.
        btm_ctrl.btm_ctrl.set_attr("rotateOrder", 2)  # ZXY.
        center_ctrl.set_attr("rotateOrder", 3)  # XZY.
        center_ctrl.btm_ctrl.set_attr("rotateOrder", 3)  # XZY.


        if self.expose_rotation_order_attr.value:
            expose_rotation_order([btm_ctrl, btm_ctrl.btm_ctrl, center_ctrl, center_ctrl.btm_ctrl])

        btm_ctrl.offset_grp.parent_relative(ctrls_grp)

        center_name = center_ctrl.short_name
        center_ctrl.pos_grp = center_ctrl.offset_grp.add_group_above("{0}_position_grp".format(center_name))
        btm_ctrl.steer_grp = btm_ctrl.offset_grp.add_group_above("{0}_steer_driver_grp".format(center_name))

        input_grp.add_attr("steer", dv=0, keyable=True)

        mult_node = mc.createNode("multiplyDivide", name="{0}_negative_steer_multiplyDivide".format(self.name))
        mc.connectAttr(input_grp.attr("steer"), "{0}.input1X".format(mult_node))
        mc.setAttr("{0}.input2X".format(mult_node), -1 if self.is_mirrored else 1)
        mc.connectAttr("{0}.outputX".format(mult_node), btm_ctrl.steer_grp.attr("rotateY"))

        center_ctrl.pos_grp.parent_relative(btm_ctrl.btm_ctrl)

        btm_ctrl.offset_grp.set_matrix(self.btm_guide.world_transformations["matrix"], space="world")
        btm_ctrl.offset_grp.set_scale([1, 1, 1])

        center_ctrl.pos_grp.set_matrix(self.center_guide.world_transformations["matrix"], space="world")
        center_ctrl.pos_grp.set_scale([1, 1, 1])

        driver_grp = IoTransform("{0}_jnt_driver_grp".format(self.name), existing=False)
        driver_grp.offset_grp = driver_grp.add_group_above("{0}_jnt_driver_offset_grp".format(self.name))
        driver_grp.offset_grp.parent_relative(center_ctrl.btm_ctrl)

        center_ctrl.add_spacer_attr()
        manual_spin_attr = center_ctrl.add_attr("manual_spin", dv=0, keyable=True)
        driver_grp.manual_spin_grp = driver_grp.add_group_above("{0}_manual_spin_grp".format(self.name))
        driver_grp.manual_spin_grp.connect_attr("rotateX", manual_spin_attr)

        joint.offset_grp = joint.add_group_above("{0}_offset_grp".format(joint.short_name))
        joint.offset_grp.parent_relative(jnts_grp)
        joint.offset_grp.set_attr("rotateZ", -90)

        radius = distance_between(
            self.center_guide.world_transformations["translate"],
            self.btm_guide.world_transformations["translate"],
        )

        if self.auto_roll_attr.value:
            self.setup_auto_roll(driver_grp, center_ctrl, radius)

        matrix_constraint(driver_grp, jnts_grp, maintain_offset=False)
        matrix_constraint(input_grp, ctrls_grp, maintain_offset=False)
        matrix_constraint(joint, output_grp, maintain_offset=False)

    def setup_auto_roll(self, driver_grp, ctrl, radius):
        """Setup auto roll using an expression.

        Arguments:
            driver_grp (str or IoTransform) -- the transform that drives the joint
            ctrl (IoCtrl) -- that will have 'auto_roll' attribute added to it
            radius (float) -- radius of the wheel
        """
        ctrl.add_spacer_attr()
        auto_roll_attr = ctrl.add_attr("auto_roll", dv=0, min=0, max=1, keyable=True)
        break_attr = ctrl.add_attr("break", at="bool", k=True, dv=False)
        reset_attr = ctrl.add_attr("reset", at="bool", k=False, dv=False)
        mc.setAttr(reset_attr, channelBox=True)
        ctrl.add_spacer_attr()

        frame_grp = driver_grp.add_group_above("{0}_frame_rotation".format(self.name))

        added_rotation_grp = driver_grp.add_group_above("{0}_added_rotation".format(self.name))
        added_rotation_grp.add_attr("last_frame", dv=0)

        direction_grp = IoTransform("{0}_wheel_direction_grp".format(self.name), existing=False)
        direction_grp.parent_relative(ctrl.btm_ctrl)
        direction_grp.set_attr("translateZ", 10.0)
        direction_grp.lock_and_hide_transformations()

        current_pos_grp = IoTransform("{0}_wheel_current_pos_grp".format(self.name), existing=False)
        current_pos_grp.parent_relative(self.module_grp)
        current_pos_grp.parent_constraint_to(ctrl.btm_ctrl, mo=False)
        current_pos_grp.lock_and_hide_transformations()

        old_pos_grp = IoTransform("{0}_wheel_old_pos_grp".format(self.name), existing=False)
        old_pos_grp.parent_relative(self.module_grp)
        old_pos_grp.match_transformation_to(current_pos_grp)

        node_scale_attr = create_module_scale(ctrl.btm_ctrl, self.name)

        name = "{0}_auto_roll_current_pose_decomposeMatrix".format(self.name)
        current_pos_decom = mc.createNode("decomposeMatrix", n=name)
        mc.connectAttr(current_pos_grp.attr("worldMatrix[0]"), "{0}.inputMatrix".format(current_pos_decom))

        name = "{0}_auto_roll_old_pose_decomposeMatrix".format(self.name)
        old_pos_decom = mc.createNode("decomposeMatrix", n=name)
        mc.connectAttr(old_pos_grp.attr("worldMatrix[0]"), "{0}.inputMatrix".format(old_pos_decom))

        name = "{0}_auto_roll_wheel_direction_decomposeMatrix".format(self.name)
        direction_decom = mc.createNode("decomposeMatrix", n=name)
        mc.connectAttr(direction_grp.attr("worldMatrix[0]"), "{0}.inputMatrix".format(direction_decom))

        name = "{0}_auto_roll_motion_vector_plusMinusAverage".format(self.name)
        motion_vector_node = mc.createNode("plusMinusAverage", n=name)
        mc.setAttr("{0}.operation".format(motion_vector_node), 2) # subtract.
        mc.connectAttr("{0}.outputTranslate".format(current_pos_decom), "{0}.input3D[0]".format(motion_vector_node))
        mc.connectAttr("{0}.outputTranslate".format(old_pos_decom), "{0}.input3D[1]".format(motion_vector_node))

        name = "{0}_auto_roll_wheel_vector_plusMinusAverage".format(self.name)
        wheel_vector_node = mc.createNode("plusMinusAverage", n=name)
        mc.setAttr("{0}.operation".format(wheel_vector_node), 2) # subtract.
        mc.connectAttr("{0}.outputTranslate".format(direction_decom), "{0}.input3D[0]".format(wheel_vector_node))
        mc.connectAttr("{0}.outputTranslate".format(current_pos_decom), "{0}.input3D[1]".format(wheel_vector_node))

        name = "{0}_auto_roll_motion_vector_combined_plusMinusAverage".format(self.name)
        motion_vector_add_node = mc.createNode("plusMinusAverage", n=name)
        mc.setAttr("{0}.operation".format(motion_vector_add_node), 1)  # add.
        mc.connectAttr("{0}.output3Dx".format(motion_vector_node), "{0}.input1D[0]".format(motion_vector_add_node))
        mc.connectAttr("{0}.output3Dy".format(motion_vector_node), "{0}.input1D[1]".format(motion_vector_add_node))
        mc.connectAttr("{0}.output3Dz".format(motion_vector_node), "{0}.input1D[2]".format(motion_vector_add_node))

        name = "{0}_auto_roll_motion_vector_combined_condition".format(self.name)
        comb_condition_node = mc.createNode("condition", n=name)
        mc.setAttr("{0}.operation".format(comb_condition_node), 0)  # equal.
        mc.setAttr("{0}.secondTerm".format(comb_condition_node), 0)
        mc.connectAttr("{0}.output1D".format(motion_vector_add_node), "{0}.firstTerm".format(comb_condition_node))
        mc.setAttr("{0}.colorIfTrue".format(comb_condition_node), 1, 1, 1)
        mc.connectAttr("{0}.output3D".format(motion_vector_node), "{0}.colorIfFalse".format(comb_condition_node))

        name = "{0}_auto_roll_wheel_vector_dot_product_vectorProduct".format(self.name)
        dot_product_node = mc.createNode("vectorProduct", n=name)
        mc.setAttr("{0}.operation".format(dot_product_node), 1)  # dot product.
        mc.setAttr("{0}.normalizeOutput".format(dot_product_node), 1)
        mc.connectAttr("{0}.outColor".format(comb_condition_node), "{0}.input1".format(dot_product_node))
        mc.connectAttr("{0}.output3D".format(wheel_vector_node), "{0}.input2".format(dot_product_node))

        name = "{0}_auto_roll_mult_by_dir_vector_multDoubleLinear".format(self.name)
        mult_dir_node = mc.createNode(MULT_DL, n=name)
        mc.connectAttr("{0}.outputX".format(dot_product_node), "{0}.{1}".format(mult_dir_node, MULT_DL_INPUT1))

        name = "{0}_auto_roll_motion_vector_power_2_multiplyDivide".format(self.name)
        power_node = mc.createNode("multiplyDivide", n=name)
        mc.setAttr("{0}.operation".format(power_node), 3)  # power.
        mc.setAttr("{0}.input2".format(power_node), 2, 2, 2)
        mc.connectAttr("{0}.output3D".format(motion_vector_node), "{0}.input1".format(power_node))

        name = "{0}_auto_roll_add_power_values_plusMinusAverage".format(self.name)
        add_power_node = mc.createNode("plusMinusAverage", n=name)
        mc.setAttr("{0}.operation".format(add_power_node), 1)  # add.
        mc.connectAttr("{0}.outputX".format(power_node), "{0}.input1D[0]".format(add_power_node))
        mc.connectAttr("{0}.outputY".format(power_node), "{0}.input1D[1]".format(add_power_node))
        mc.connectAttr("{0}.outputZ".format(power_node), "{0}.input1D[2]".format(add_power_node))

        name = "{0}_auto_roll_square_root_multiplyDivide".format(self.name)
        sqrt_node = mc.createNode("multiplyDivide", n=name)
        mc.setAttr("{0}.operation".format(sqrt_node), 3)  # power.
        mc.setAttr("{0}.input2X".format(sqrt_node), 0.5)
        mc.connectAttr("{0}.output1D".format(add_power_node), "{0}.input1X".format(sqrt_node))

        mc.connectAttr("{0}.outputX".format(sqrt_node), "{0}.{1}".format(mult_dir_node, MULT_DL_INPUT2))

        name = "{0}_auto_roll_mult_on_off_attr_multDoubleLinear".format(self.name)
        mult_auto_roll_node = mc.createNode(MULT_DL, n=name)
        mc.connectAttr(auto_roll_attr, "{0}.{1}".format(mult_auto_roll_node, MULT_DL_INPUT1))
        mc.connectAttr("{0}.output".format(mult_dir_node), "{0}.{1}".format(mult_auto_roll_node, MULT_DL_INPUT2))

        name = "{0}_auto_roll_break_reset_reverse".format(self.name)
        reverse_node = mc.createNode("reverse", n=name)
        mc.connectAttr(break_attr, "{0}.inputX".format(reverse_node))
        mc.connectAttr(reset_attr, "{0}.inputY".format(reverse_node))

        name = "{0}_auto_roll_mult_by_break_multDoubleLinear".format(self.name)
        mult_break_node = mc.createNode(MULT_DL, n=name)
        mc.connectAttr("{0}.outputX".format(reverse_node), "{0}.{1}".format(mult_break_node, MULT_DL_INPUT1))
        mc.connectAttr("{0}.output".format(mult_auto_roll_node), "{0}.{1}".format(mult_break_node, MULT_DL_INPUT2))

        name = "{0}_auto_roll_mult_by_reset_multDoubleLinear".format(self.name)
        mult_reset_node = mc.createNode(MULT_DL, n=name)
        mc.connectAttr("{0}.outputY".format(reverse_node), "{0}.{1}".format(mult_reset_node, MULT_DL_INPUT1))
        mc.connectAttr("{0}.output".format(mult_break_node), "{0}.{1}".format(mult_reset_node, MULT_DL_INPUT2))

        name = "{0}_auto_roll_auto_roll_circumference_multDoubleLinear".format(self.name)
        circumference_node = mc.createNode(MULT_DL, n=name)
        mc.connectAttr(node_scale_attr, "{0}.{1}".format(circumference_node, MULT_DL_INPUT1))
        mc.setAttr("{0}.{1}".format(circumference_node, MULT_DL_INPUT2), radius * 6.283)

        name = "{0}_auto_roll_circumference_divide_multiplyDivide".format(self.name)
        circumference_divide_node = mc.createNode("multiplyDivide", n=name)
        mc.setAttr("{0}.operation".format(circumference_divide_node), 2)  # divide.
        mc.connectAttr("{0}.output".format(mult_reset_node), "{0}.input1X".format(circumference_divide_node))
        mc.connectAttr("{0}.output".format(circumference_node), "{0}.input2X".format(circumference_divide_node))

        name = "{0}_auto_roll_convert_to_rotation_multDoubleLinear".format(self.name)
        convert_to_rotation_node = mc.createNode(MULT_DL, n=name)
        mc.connectAttr("{0}.outputX".format(circumference_divide_node), "{0}.{1}".format(convert_to_rotation_node, MULT_DL_INPUT1))
        mc.setAttr("{0}.{1}".format(convert_to_rotation_node, MULT_DL_INPUT2), 360)

        mc.connectAttr("{0}.output".format(convert_to_rotation_node), "{0}.rotateX".format(frame_grp))

        expression_node = mc.expression(
            name="{0}_auto_roll_expression".format(self.name),
            object=frame_grp,
            animated=0,  # Not Animated.
            string="""
                if (frame != {0}.last_frame) {{
                    float $frameRotateX = `getAttr {1}.rotateX`;
                    float $addRotateX = `getAttr {0}.rotateX`;
                    {0}.rotateX = $addRotateX + $frameRotateX;

                    {2}.translateX = `getAttr {3}.translateX`;
                    {2}.translateY = `getAttr {3}.translateY`;
                    {2}.translateZ = `getAttr {3}.translateZ`;

                    {0}.last_frame = frame;
                }}

                if ({4} == true) {{ {0}.rotateX = 0; }}
                """.format(
                added_rotation_grp,
                frame_grp,
                old_pos_grp,
                current_pos_grp,
                reset_attr,
            ),
        )

        del_first_nodes = mc.listConnections(expression_node, t="unitConversion", d=True, s=False, p=False) or []
        del_first_nodes.append(expression_node)
        tag_as_delete_first(del_first_nodes)

        mc.setAttr(auto_roll_attr, 1)  # set auto_roll on by default.
