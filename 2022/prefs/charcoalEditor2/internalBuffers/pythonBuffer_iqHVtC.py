import pymel.core as pm


head_sec_ctrl = pm.ls('C_Head_head_secondary_ctrl')[-1]
neck_sec_ctrl = pm.ls('C_Head_neck_root_secondary_ctrl')[-1]
neck_mid_follow_grp = pm.ls('C_Head_neck_mid_ctrl')[-1]

if pm.objExists('neck_orient_loc'):
    neck_orient_loc = pm.ls('neck_orient_loc')[-1]
else:
    neck_orient_loc = pm.spaceLocator(n='neck_orient_loc')
    pm.parent(neck_orient_loc, 'rig_grp')
    
pm.pointConstraint([neck_sec_ctrl, head_sec_ctrl], neck_orient_loc)
pm.aimConstraint(neck_sec_ctrl, neck_orient_loc, mo=True, aimVector=[0, 0, -1], upVector=[0, 1, 0], worldUpType="vector", worldUpVector=[0, 1, 0])


if pm.objExists('neck_orient_floatMath'):
    float_math_node = pm.ls('neck_orient_floatMath')[-1]
else:
    float_math_node = pm.shadingNode('floatMath', asUtility=True, n='neck_orient_floatMath')

float_math_node.operation.set(2)
float_math_node.floatB.set(1.5)
pm.connectAttr(neck_orient_loc.rotateX, float_math_node.floatA, f=True)
pm.connectAttr(float_math_node.outFloat, neck_mid_follow_grp.rotateX, f=True)
