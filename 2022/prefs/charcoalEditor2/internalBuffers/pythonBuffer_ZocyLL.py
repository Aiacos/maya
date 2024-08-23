import pymel.core as pm


side = node_name.split('_')[0]
# Def
def setDrivenKey(driver, driverValueList, driven, drivenValueList, cvType='linear'):
    """
    Set Driven Key utility
    :param driver: str, driver + driving attribute (ctrl.attr)
    :param driverValueList: list, value list
    :param driven: str, driven + driven attribute (ctrl.attr)
    :param drivenValueList: list, value list
    :param cvType: str, auto, clamped, fast, flat, linear, plateau, slow, spline, step, and stepnext
    :return:
    """
    for driverV, drivenV in zip(driverValueList, drivenValueList):
        pm.setDrivenKeyframe(driven, currentDriver=driver, driverValue=driverV, value=drivenV, inTangentType=cvType, outTangentType=cvType)
        
def create_float_math_node(in_attr, value, out_attr, name):
    float_math_node = pm.shadingNode('floatMath', asUtility=True, n=name + '_floatMath')
        
    float_math_node.operation.set(2)
    float_math_node.floatB.set(value)
    pm.connectAttr(in_attr, float_math_node.floatA, f=True)
    pm.connectAttr(float_math_node.outFloat, out_attr, f=True)
    
    return float_math_node
    

attr_ctrl = pm.ls(node_name + '_ik_tip_ctrl')[-1]

# Foot_Roll
setDrivenKey(attr_ctrl.foot_roll, [-60, -30, 0, 30, 60], node_name + '_ik_toes_ball_foot_roll.rotateX', [-45, -30, 0, 30, 45])
setDrivenKey(attr_ctrl.foot_roll, [-60, -30, 0, 30, 60], node_name + '_ik_toes_tip_foot_roll.rotateX', [-60, 0, 0, 0, 0])
setDrivenKey(attr_ctrl.foot_roll, [-60, -30, 0, 30, 60], node_name + '_ik_heel_foot_roll.rotateX', [0, 0, 0, 0, 60])

# Ankle_Roll
create_float_math_node(attr_ctrl.ankle_roll, -1, node_name + '_ik_toes_ball_roll.rotateX', 'Ankle_Roll')

# Toe_Roll
create_float_math_node(attr_ctrl.toe_roll, -1, node_name + '_ik_toes_tip_toe_heel_roll.rotateX', 'Toe_Roll')

# Heel_Roll
create_float_math_node(attr_ctrl.heel_roll, -1, node_name + '_ik_heel_toe_heel_roll.rotateX', 'Heel_Roll')

# Toe_Tap
finger_list = pm.ls(side + '_BackFinger_finger_?_1_toe_tap_grp')

for offset_grp in finger_list:
    create_float_math_node(attr_ctrl.toe_tap, -1, offset_grp.rotateZ, offset_grp.name())

# SideRoll
inner_offset_grp = pm.ls(node_name + '_ik_tip_secondary_inner_side_roll')[-1]
outer_offset_grp = pm.ls(node_name + '_ik_tip_secondary_outer_side_roll')[-1]

pm.matchTransform(inner_offset_grp, side + '_inner_roll_loc', piv=True)
pm.matchTransform(outer_offset_grp, side + '_outer_roll_loc', piv=True)

setDrivenKey(attr_ctrl.side_roll, [-90, 0, 90], inner_offset_grp.rotateZ, [0, 0, 90])
setDrivenKey(attr_ctrl.side_roll, [-90, 0, 90], outer_offset_grp.rotateZ, [-90, 0, 0])

# ToeTwist
create_float_math_node(attr_ctrl.toe_twist, -1, node_name + '_ik_toes_tip_toe_heel_roll.rotateZ', 'ToeTwist')

# HeelTwist
create_float_math_node(attr_ctrl.heel_twist, -1, node_name + '_ik_heel_toe_heel_roll.rotateZ', 'HeelTwist')

# Cleanup
pm.setAttr(side + "_BackLeg_ik_fk_switch_ctrl.bendy_bones_ctrls", keyable=False, channelBox=False)
pm.setAttr(side + "_BackLeg_ik_fk_switch_ctrl.show_ik_ctrls", keyable=False, channelBox=False)
pm.setAttr(side + "_BackLeg_ik_fk_switch_ctrl.show_fk_ctrls", keyable=False, channelBox=False)
pm.setAttr(side + "_BackLeg_ik_fk_switch_ctrl._______", keyable=False, channelBox=False)

pm.setAttr(node_name + "_ik_toes_ball_ctrl.meta_aim", 0)