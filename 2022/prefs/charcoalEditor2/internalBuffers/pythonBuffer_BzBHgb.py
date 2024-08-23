import pymel.core as pm


pm.delete('C_Head_neck_mid_offset_grp_pointConstraint1', 'C_Head_neck_mid_offset_grp_aimConstraint1')
pm.parentConstraint(['C_Head_head_secondary_ctrl', 'C_Head_neck_root_secondary_ctrl'],'C_Head_neck_mid_offset_grp', mo=True, skipRotate=['x', 'y', 'z'])