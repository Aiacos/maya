"""Utilities functions to help create the wheels setup with suspension."""

from arise.utils.math_utils import distance_between
from arise.utils.matrix_utils import matrix_constraint
from arise.utils.tagging_utils import tag_as_delete_first
from arise.utils.io_nodes.io_transform import IoTransform
from arise.utils.modules_utils import (
    secondary_ctrls_setup, expose_rotation_order, create_grps, SECONDARY_COLOR, create_module_scale, MULT_DL,
    MULT_DL_INPUT1, MULT_DL_INPUT2,
)

import maya.cmds as mc

def create_wheel_ctrls(node, label, ctrls_mult):
    """Create wheel ctrls for the provided node and label to quickly create 4 wheels ctrls.

    Arguments:
        node (IoNode) -- the node module
        label (str) -- the label to use for the ctrls
        ctrls_mult (float) -- the multiplier to use for the ctrls size

    Returns:
        tuple -- the bottom ctrl, center ctrl, bottom secondary ctrl, center secondary ctrl
    """
    btm_ctrl = node.add_ctrl(
        name="{0}_wheel_bottom".format(label),
        shape="box",
        up_orient="+Y",
        size=[value * ctrls_mult for value in [10.0, 1.0, 10.0]],
    )
    btm_ctrl.translate_offset = [0, ctrls_mult, 0]

    center_ctrl = node.add_ctrl(
        name="{0}_wheel_center".format(label),
        shape="rotate",
        up_orient="+X",
        size=10 * ctrls_mult,
    )
    center_ctrl.translate_offset = [10.0 * ctrls_mult, 0, 0]

    for attr in ["rotateX", "scaleY", "scaleZ"]:
        btm_ctrl.add_locked_hidden_attr(attr)
        center_ctrl.add_locked_hidden_attr(attr)

    btm_2ry_ctrl = node.add_ctrl(
        name="{0}_bottom_secondary".format(label), shape="square", size=8.5 * ctrls_mult)
    btm_2ry_ctrl.color = SECONDARY_COLOR

    center_2ry_ctrl = node.add_ctrl(
        name="{0}_center_secondary".format(label),
        shape="circle",
        up_orient="+X",
        size=5.5 * ctrls_mult,
    )
    center_2ry_ctrl.translate_offset = [10.0 * ctrls_mult, 0, 0]
    center_2ry_ctrl.color = SECONDARY_COLOR

    for attr in ["rotateX", "scaleX", "scaleY", "scaleZ"]:
        btm_2ry_ctrl.add_locked_hidden_attr(attr)
        center_2ry_ctrl.add_locked_hidden_attr(attr)

    return btm_ctrl, center_ctrl, btm_2ry_ctrl, center_2ry_ctrl

def create_wheel_setup(node, guides, ctrls_list, joint, label):
    """Create wheel rig setup including suspension loc, roll, and input/output grps.

    Arguments:
        node (IoNode) -- the node module
        guides (list) -- the list of guides (x2) to use for the wheel setup
        ctrls_list (list) -- the list of ctrls (x4) to use for the wheel setup
        joint (IoJoint) -- the joint to use for the wheel setup
        label (str) -- the label to use for the wheel setup

    Returns:
        tuple -- the input grp, output grp, and the loc

    """
    btm_guide, center_guide = guides[1], guides[2]
    btm_ctrl = ctrls_list[0].pointer
    center_ctrl = ctrls_list[1].pointer
    btm_2ry_ctrl = ctrls_list[2].pointer
    center_2ry_ctrl = ctrls_list[3].pointer
    joint = joint.pointer

    input_grp, output_grp = create_grps(node, ["{0}_input_grp".format(label), "{0}_output_grp".format(label)])
    ctrls_grp, jnts_grp = create_grps(node, ["{0}_ctrls_grp".format(label), "{0}_jnts_grp".format(label)])
    wheel_grp = create_grps(node, ["{0}_wheel_grp".format(label)])[0]

    input_grp.set_matrix(center_guide.world_transformations["matrix"], space="world")
    input_grp.set_scale([1, 1, 1])

    wheel_grp.parent_relative(node.wheels_top_grp)
    input_grp.parent_relative(wheel_grp)
    output_grp.parent_relative(wheel_grp)
    ctrls_grp.parent_relative(wheel_grp)
    jnts_grp.parent_relative(wheel_grp)

    ctrls_grp.match_transformation_to(input_grp)

    btm_ctrl.scale_attrs_connect()
    center_ctrl.scale_attrs_connect()

    secondary_ctrls_setup([btm_ctrl, center_ctrl], [btm_2ry_ctrl, center_2ry_ctrl])

    btm_ctrl.set_attr("rotateOrder", 2)  # ZXY.
    btm_ctrl.btm_ctrl.set_attr("rotateOrder", 2)  # ZXY.
    center_ctrl.set_attr("rotateOrder", 3)  # XZY.
    center_ctrl.btm_ctrl.set_attr("rotateOrder", 3)  # XZY.

    if node.expose_rotation_order_attr.value:
        expose_rotation_order([btm_ctrl, btm_ctrl.btm_ctrl, center_ctrl, center_ctrl.btm_ctrl])

    btm_ctrl.offset_grp.parent_relative(ctrls_grp)

    center_name = center_ctrl.short_name
    center_ctrl.pos_grp = center_ctrl.offset_grp.add_group_above("{0}_position_grp".format(center_name))
    btm_ctrl.steer_grp = btm_ctrl.offset_grp.add_group_above("{0}_steer_driver_grp".format(center_name))

    input_grp.add_attr("steer", dv=0, keyable=True)

    mult_node = mc.createNode("multiplyDivide", name="{0}_{1}_negative_steer_multiplyDivide".format(node.name, label))
    mc.connectAttr(input_grp.attr("steer"), "{0}.input1X".format(mult_node))
    mc.setAttr("{0}.input2X".format(mult_node), -1 if node.is_mirrored else 1)
    mc.connectAttr("{0}.outputX".format(mult_node), btm_ctrl.steer_grp.attr("rotateY"))

    center_ctrl.pos_grp.parent_relative(btm_ctrl.btm_ctrl)

    btm_ctrl.offset_grp.set_matrix(btm_guide.world_transformations["matrix"], space="world")
    btm_ctrl.offset_grp.set_scale([1, 1, 1])

    center_ctrl.pos_grp.set_matrix(center_guide.world_transformations["matrix"], space="world")
    center_ctrl.pos_grp.set_scale([1, 1, 1])

    driver_grp = IoTransform("{0}_{1}_jnt_driver_grp".format(node.name, label), existing=False)
    driver_grp.offset_grp = driver_grp.add_group_above("{0}_{1}_jnt_driver_offset_grp".format(node.name, label))
    driver_grp.offset_grp.parent_relative(center_ctrl.btm_ctrl)

    center_ctrl.add_spacer_attr()
    manual_spin_attr = center_ctrl.add_attr("manual_spin", dv=0, keyable=True)
    driver_grp.manual_spin_grp = driver_grp.add_group_above("{0}_{1}_manual_spin_grp".format(node.name, label))
    driver_grp.manual_spin_grp.connect_attr("rotateX", manual_spin_attr)

    joint.offset_grp = joint.add_group_above("{0}_offset_grp".format(joint.short_name))
    joint.offset_grp.parent_relative(jnts_grp)
    joint.offset_grp.set_attr("rotateZ", -90)

    radius = distance_between(
        center_guide.world_transformations["translate"],
        btm_guide.world_transformations["translate"],
    )
    prefix = "{0}_{1}".format(node.name, label)
    setup_auto_roll(prefix, node, driver_grp, center_ctrl, radius)

    matrix_constraint(driver_grp, jnts_grp, maintain_offset=False)
    matrix_constraint(input_grp, ctrls_grp, maintain_offset=False)
    matrix_constraint(joint, output_grp, maintain_offset=False)

    loc = mc.spaceLocator(name="{0}_{1}_loc".format(node.name, label))[0]
    loc = IoTransform(loc, existing=True)
    loc.offset_grp = loc.add_group_above("{0}_offset_grp".format(loc.short_name))
    loc.suspension_grp = loc.add_group_above("{0}_suspension_grp".format(loc.short_name))
    loc.offset_grp.parent_relative(btm_2ry_ctrl)
    loc.match_transformation_to(center_ctrl)

    btm_ctrl.add_spacer_attr()
    btm_ctrl.add_attr("suspension_up_limit", dv=0, min=0, keyable=True)
    btm_ctrl.set_attr("suspension_up_limit", node.suspension_up_attr.value)
    btm_ctrl.add_attr("suspension_down_limit", dv=0, max=0, keyable=True)
    btm_ctrl.set_attr("suspension_down_limit", node.suspension_low_attr.value)

    up_mult = mc.createNode(MULT_DL, name="{0}_{1}_up_suspension_multDoubleLinear".format(node.name, label))
    down_mult = mc.createNode(MULT_DL, name="{0}_{1}_suspension_down_multDoubleLinear".format(node.name, label))
    remap = mc.createNode("remapValue", name="{0}_{1}_suspension_remapValue".format(node.name, label))

    mc.connectAttr(btm_ctrl.attr("suspension_up_limit"), "{0}.{1}".format(up_mult, MULT_DL_INPUT1))
    mc.setAttr("{0}.{1}".format(up_mult, MULT_DL_INPUT2), -1)

    mc.connectAttr(btm_ctrl.attr("suspension_down_limit"), "{0}.{1}".format(down_mult, MULT_DL_INPUT1))
    mc.setAttr("{0}.{1}".format(down_mult, MULT_DL_INPUT2), -1)

    mc.connectAttr(btm_ctrl.attr("translateY"), "{0}.inputValue".format(remap))
    mc.connectAttr("{0}.output".format(up_mult), "{0}.outputMax".format(remap))
    mc.connectAttr("{0}.output".format(down_mult), "{0}.outputMin".format(remap))
    mc.connectAttr(btm_ctrl.attr("suspension_up_limit"), "{0}.inputMax".format(remap))
    mc.connectAttr(btm_ctrl.attr("suspension_down_limit"), "{0}.inputMin".format(remap))
    mc.connectAttr("{0}.outValue".format(remap), loc.suspension_grp.attr("translateY"))

    return input_grp, output_grp, loc

def suspension_loc_setup(node, locs):
    """Using the 4 wheels locs, create 3 more locs that will be the suspension locs.

    Arguments:
        node (IoNode) -- the node module
        locs (list) -- the list of locs to use for the suspension setup

    Returns:
        IoTransform -- the center loc
    """
    center_loc = IoTransform(mc.spaceLocator(name="{0}_suspension_center_loc".format(node.name))[0], existing=True)
    mid_front_loc = IoTransform(mc.spaceLocator(name="{0}_suspension_mid_front_loc".format(node.name))[0], existing=True)
    mid_side_loc = IoTransform(mc.spaceLocator(name="{0}_suspension_mid_side_loc".format(node.name))[0], existing=True)

    center_loc.offset_grp = center_loc.add_group_above("{0}_offset_grp".format(center_loc.short_name))
    mid_front_loc.offset_grp = mid_front_loc.add_group_above("{0}_offset_grp".format(mid_front_loc.short_name))
    mid_side_loc.offset_grp = mid_side_loc.add_group_above("{0}_offset_grp".format(mid_side_loc.short_name))

    susp_locs_grp = create_grps(node, ["{0}_suspension_locs_grp".format(node.name)])[0]
    susp_locs_grp.parent_relative(node.wheels_top_grp)

    center_loc.offset_grp.parent_relative(susp_locs_grp)
    mid_front_loc.offset_grp.parent_relative(susp_locs_grp)
    mid_side_loc.offset_grp.parent_relative(susp_locs_grp)

    center_loc.offset_grp.point_constraint_to(locs, maintainOffset=False)
    mid_front_loc.offset_grp.point_constraint_to([locs[0], locs[1]], maintainOffset=False)
    mid_side_loc.offset_grp.point_constraint_to([locs[0], locs[2]], maintainOffset=False)

    center_loc.aim_constraint_to(
        mid_front_loc,
        aimVector=(0, 0, 1),
        upVector=(1, 0, 0),
        worldUpType="object",
        worldUpObject=mid_side_loc,
        maintainOffset=False,
    )

    for loc in locs + [center_loc, mid_front_loc, mid_side_loc]:
        loc.hide()

    return center_loc

def setup_auto_roll(prefix, node, driver_grp, ctrl, radius):
        """Setup auto roll using an expression.

        Arguments:
            prefix (str) -- prefix to use for naming the nodes
            node (IoNode) -- the node module
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

        frame_grp = driver_grp.add_group_above("{0}_frame_rotation".format(prefix))

        added_rotation_grp = driver_grp.add_group_above("{0}_added_rotation".format(prefix))
        added_rotation_grp.add_attr("last_frame", dv=0)

        direction_grp = IoTransform("{0}_wheel_direction_grp".format(prefix), existing=False)
        direction_grp.parent_relative(ctrl.btm_ctrl)
        direction_grp.set_attr("translateZ", 10.0)
        direction_grp.lock_and_hide_transformations()

        current_pos_grp = IoTransform("{0}_wheel_current_pos_grp".format(prefix), existing=False)
        current_pos_grp.parent_relative(node.wheels_top_grp)
        current_pos_grp.parent_constraint_to(ctrl.btm_ctrl, maintainOffset=False)
        current_pos_grp.lock_and_hide_transformations()

        old_pos_grp = IoTransform("{0}_wheel_old_pos_grp".format(prefix), existing=False)
        old_pos_grp.parent_relative(node.wheels_top_grp)
        old_pos_grp.match_transformation_to(current_pos_grp)

        node_scale_attr = create_module_scale(ctrl.btm_ctrl, prefix)

        name = "{0}_auto_roll_current_pose_decomposeMatrix".format(prefix)
        current_pos_decom = mc.createNode("decomposeMatrix", n=name)
        mc.connectAttr(current_pos_grp.attr("worldMatrix[0]"), "{0}.inputMatrix".format(current_pos_decom))

        name = "{0}_auto_roll_old_pose_decomposeMatrix".format(prefix)
        old_pos_decom = mc.createNode("decomposeMatrix", n=name)
        mc.connectAttr(old_pos_grp.attr("worldMatrix[0]"), "{0}.inputMatrix".format(old_pos_decom))

        name = "{0}_auto_roll_wheel_direction_decomposeMatrix".format(prefix)
        direction_decom = mc.createNode("decomposeMatrix", n=name)
        mc.connectAttr(direction_grp.attr("worldMatrix[0]"), "{0}.inputMatrix".format(direction_decom))

        name = "{0}_auto_roll_motion_vector_plusMinusAverage".format(prefix)
        motion_vector_node = mc.createNode("plusMinusAverage", n=name)
        mc.setAttr("{0}.operation".format(motion_vector_node), 2) # subtract.
        mc.connectAttr("{0}.outputTranslate".format(current_pos_decom), "{0}.input3D[0]".format(motion_vector_node))
        mc.connectAttr("{0}.outputTranslate".format(old_pos_decom), "{0}.input3D[1]".format(motion_vector_node))

        name = "{0}_auto_roll_wheel_vector_plusMinusAverage".format(prefix)
        wheel_vector_node = mc.createNode("plusMinusAverage", n=name)
        mc.setAttr("{0}.operation".format(wheel_vector_node), 2) # subtract.
        mc.connectAttr("{0}.outputTranslate".format(direction_decom), "{0}.input3D[0]".format(wheel_vector_node))
        mc.connectAttr("{0}.outputTranslate".format(current_pos_decom), "{0}.input3D[1]".format(wheel_vector_node))

        name = "{0}_auto_roll_motion_vector_combined_plusMinusAverage".format(prefix)
        motion_vector_add_node = mc.createNode("plusMinusAverage", n=name)
        mc.setAttr("{0}.operation".format(motion_vector_add_node), 1)  # add.
        mc.connectAttr("{0}.output3Dx".format(motion_vector_node), "{0}.input1D[0]".format(motion_vector_add_node))
        mc.connectAttr("{0}.output3Dy".format(motion_vector_node), "{0}.input1D[1]".format(motion_vector_add_node))
        mc.connectAttr("{0}.output3Dz".format(motion_vector_node), "{0}.input1D[2]".format(motion_vector_add_node))

        name = "{0}_auto_roll_motion_vector_combined_condition".format(prefix)
        comb_condition_node = mc.createNode("condition", n=name)
        mc.setAttr("{0}.operation".format(comb_condition_node), 0)  # equal.
        mc.setAttr("{0}.secondTerm".format(comb_condition_node), 0)
        mc.connectAttr("{0}.output1D".format(motion_vector_add_node), "{0}.firstTerm".format(comb_condition_node))
        mc.setAttr("{0}.colorIfTrue".format(comb_condition_node), 1, 1, 1)
        mc.connectAttr("{0}.output3D".format(motion_vector_node), "{0}.colorIfFalse".format(comb_condition_node))

        name = "{0}_auto_roll_wheel_vector_dot_product_vectorProduct".format(prefix)
        dot_product_node = mc.createNode("vectorProduct", n=name)
        mc.setAttr("{0}.operation".format(dot_product_node), 1)  # dot product.
        mc.setAttr("{0}.normalizeOutput".format(dot_product_node), 1)
        mc.connectAttr("{0}.outColor".format(comb_condition_node), "{0}.input1".format(dot_product_node))
        mc.connectAttr("{0}.output3D".format(wheel_vector_node), "{0}.input2".format(dot_product_node))

        name = "{0}_auto_roll_mult_by_dir_vector_multDoubleLinear".format(prefix)
        mult_dir_node = mc.createNode(MULT_DL, n=name)
        mc.connectAttr("{0}.outputX".format(dot_product_node), "{0}.{1}".format(mult_dir_node, MULT_DL_INPUT1))

        name = "{0}_auto_roll_motion_vector_power_2_multiplyDivide".format(prefix)
        power_node = mc.createNode("multiplyDivide", n=name)
        mc.setAttr("{0}.operation".format(power_node), 3)  # power.
        mc.setAttr("{0}.input2".format(power_node), 2, 2, 2)
        mc.connectAttr("{0}.output3D".format(motion_vector_node), "{0}.input1".format(power_node))

        name = "{0}_auto_roll_add_power_values_plusMinusAverage".format(prefix)
        add_power_node = mc.createNode("plusMinusAverage", n=name)
        mc.setAttr("{0}.operation".format(add_power_node), 1)  # add.
        mc.connectAttr("{0}.outputX".format(power_node), "{0}.input1D[0]".format(add_power_node))
        mc.connectAttr("{0}.outputY".format(power_node), "{0}.input1D[1]".format(add_power_node))
        mc.connectAttr("{0}.outputZ".format(power_node), "{0}.input1D[2]".format(add_power_node))

        name = "{0}_auto_roll_square_root_multiplyDivide".format(prefix)
        sqrt_node = mc.createNode("multiplyDivide", n=name)
        mc.setAttr("{0}.operation".format(sqrt_node), 3)  # power.
        mc.setAttr("{0}.input2X".format(sqrt_node), 0.5)
        mc.connectAttr("{0}.output1D".format(add_power_node), "{0}.input1X".format(sqrt_node))

        mc.connectAttr("{0}.outputX".format(sqrt_node), "{0}.{1}".format(mult_dir_node, MULT_DL_INPUT2))

        name = "{0}_auto_roll_mult_on_off_attr_multDoubleLinear".format(prefix)
        mult_auto_roll_node = mc.createNode(MULT_DL, n=name)
        mc.connectAttr(auto_roll_attr, "{0}.{1}".format(mult_auto_roll_node, MULT_DL_INPUT1))
        mc.connectAttr("{0}.output".format(mult_dir_node), "{0}.{1}".format(mult_auto_roll_node, MULT_DL_INPUT2))

        name = "{0}_auto_roll_break_reset_reverse".format(prefix)
        reverse_node = mc.createNode("reverse", n=name)
        mc.connectAttr(break_attr, "{0}.inputX".format(reverse_node))
        mc.connectAttr(reset_attr, "{0}.inputY".format(reverse_node))

        name = "{0}_auto_roll_mult_by_break_multDoubleLinear".format(prefix)
        mult_break_node = mc.createNode(MULT_DL, n=name)
        mc.connectAttr("{0}.outputX".format(reverse_node), "{0}.{1}".format(mult_break_node, MULT_DL_INPUT1))
        mc.connectAttr("{0}.output".format(mult_auto_roll_node), "{0}.{1}".format(mult_break_node, MULT_DL_INPUT2))

        name = "{0}_auto_roll_mult_by_reset_multDoubleLinear".format(prefix)
        mult_reset_node = mc.createNode(MULT_DL, n=name)
        mc.connectAttr("{0}.outputY".format(reverse_node), "{0}.{1}".format(mult_reset_node, MULT_DL_INPUT1))
        mc.connectAttr("{0}.output".format(mult_break_node), "{0}.{1}".format(mult_reset_node, MULT_DL_INPUT2))

        name = "{0}_auto_roll_auto_roll_circumference_multDoubleLinear".format(prefix)
        circumference_node = mc.createNode(MULT_DL, n=name)
        mc.connectAttr(node_scale_attr, "{0}.{1}".format(circumference_node, MULT_DL_INPUT1))
        mc.setAttr("{0}.{1}".format(circumference_node, MULT_DL_INPUT2), radius * 6.283)

        name = "{0}_auto_roll_circumference_divide_multiplyDivide".format(prefix)
        circumference_divide_node = mc.createNode("multiplyDivide", n=name)
        mc.setAttr("{0}.operation".format(circumference_divide_node), 2)  # divide.
        mc.connectAttr("{0}.output".format(mult_reset_node), "{0}.input1X".format(circumference_divide_node))
        mc.connectAttr("{0}.output".format(circumference_node), "{0}.input2X".format(circumference_divide_node))

        name = "{0}_auto_roll_convert_to_rotation_multDoubleLinear".format(prefix)
        convert_to_rotation_node = mc.createNode(MULT_DL, n=name)
        mc.connectAttr("{0}.outputX".format(circumference_divide_node), "{0}.{1}".format(convert_to_rotation_node, MULT_DL_INPUT1))
        mc.setAttr("{0}.{1}".format(convert_to_rotation_node, MULT_DL_INPUT2), 360)

        mc.connectAttr("{0}.output".format(convert_to_rotation_node), "{0}.rotateX".format(frame_grp))

        expression_node = mc.expression(
            name="{0}_auto_roll_expression".format(prefix),
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
