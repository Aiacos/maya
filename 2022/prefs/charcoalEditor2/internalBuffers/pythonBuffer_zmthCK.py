import pymel.core as pm


neck_rot_ctrl_list = pm.ls('M_NeckRot_?_01_ctrl')
neck_ctrl_list = pm.ls('C_Head_ribbon_micro_*_ctrl')


neck_cnst_list = []
for ctrl in neck_ctrl_list:
    #print(ctrl)
    cnst = pm.parentConstraint(neck_rot_ctrl_list, ctrl.getParent(), mo=True)
    neck_cnst_list.append(cnst)
    
    
#cnst_query = pm.ls('C_Head_ribbon_micro_*_offset_grp_parentConstraint1')
#for cnst in cnst_query:
#    print('cnst: ', cnst)
#    print(cnst.M_NeckRot_0_01_ctrlW0.get())
#    print(cnst.M_NeckRot_1_01_ctrlW1.get())
#    print(cnst.M_NeckRot_2_01_ctrlW2.get())
    

pm.setAttr(neck_cnst_list[0].M_NeckRot_0_01_ctrlW0, 0.0)
pm.setAttr(neck_cnst_list[0].M_NeckRot_1_01_ctrlW1, 0.0)
pm.setAttr(neck_cnst_list[0].M_NeckRot_2_01_ctrlW2, 0.0)

pm.setAttr(neck_cnst_list[1].M_NeckRot_0_01_ctrlW0, 0.0)
pm.setAttr(neck_cnst_list[1].M_NeckRot_1_01_ctrlW1, 0.0)
pm.setAttr(neck_cnst_list[1].M_NeckRot_2_01_ctrlW2, 0.25)

pm.setAttr(neck_cnst_list[2].M_NeckRot_0_01_ctrlW0, 0.0)
pm.setAttr(neck_cnst_list[2].M_NeckRot_1_01_ctrlW1, 0.0)
pm.setAttr(neck_cnst_list[2].M_NeckRot_2_01_ctrlW2, 0.75)

pm.setAttr(neck_cnst_list[3].M_NeckRot_0_01_ctrlW0, 0.0)
pm.setAttr(neck_cnst_list[3].M_NeckRot_1_01_ctrlW1, 0.0)
pm.setAttr(neck_cnst_list[3].M_NeckRot_2_01_ctrlW2, 1.0)

pm.setAttr(neck_cnst_list[4].M_NeckRot_0_01_ctrlW0, 0.0)
pm.setAttr(neck_cnst_list[4].M_NeckRot_1_01_ctrlW1, 0.25)
pm.setAttr(neck_cnst_list[4].M_NeckRot_2_01_ctrlW2, 0.75)

pm.setAttr(neck_cnst_list[5].M_NeckRot_0_01_ctrlW0, 0.0)
pm.setAttr(neck_cnst_list[5].M_NeckRot_1_01_ctrlW1, 0.5)
pm.setAttr(neck_cnst_list[5].M_NeckRot_2_01_ctrlW2, 0.5)

pm.setAttr(neck_cnst_list[6].M_NeckRot_0_01_ctrlW0, 0.0)
pm.setAttr(neck_cnst_list[6].M_NeckRot_1_01_ctrlW1, 0.75)
pm.setAttr(neck_cnst_list[6].M_NeckRot_2_01_ctrlW2, 0.25)

pm.setAttr(neck_cnst_list[7].M_NeckRot_0_01_ctrlW0, 0.0)
pm.setAttr(neck_cnst_list[7].M_NeckRot_1_01_ctrlW1, 1.0)
pm.setAttr(neck_cnst_list[7].M_NeckRot_2_01_ctrlW2, 0.0)

pm.setAttr(neck_cnst_list[8].M_NeckRot_0_01_ctrlW0, 0.25)
pm.setAttr(neck_cnst_list[8].M_NeckRot_1_01_ctrlW1, 0.75)
pm.setAttr(neck_cnst_list[8].M_NeckRot_2_01_ctrlW2, 0.0)

pm.setAttr(neck_cnst_list[9].M_NeckRot_0_01_ctrlW0, 0.5)
pm.setAttr(neck_cnst_list[9].M_NeckRot_1_01_ctrlW1, 0.5)
pm.setAttr(neck_cnst_list[9].M_NeckRot_2_01_ctrlW2, 0.0)

pm.setAttr(neck_cnst_list[10].M_NeckRot_0_01_ctrlW0, 0.75)
pm.setAttr(neck_cnst_list[10].M_NeckRot_1_01_ctrlW1, 0.25)
pm.setAttr(neck_cnst_list[10].M_NeckRot_2_01_ctrlW2, 0.0)

pm.setAttr(neck_cnst_list[11].M_NeckRot_0_01_ctrlW0, 1.0)
pm.setAttr(neck_cnst_list[11].M_NeckRot_1_01_ctrlW1, 0.0)
pm.setAttr(neck_cnst_list[11].M_NeckRot_2_01_ctrlW2, 0.0)

pm.setAttr(neck_cnst_list[12].M_NeckRot_0_01_ctrlW0, 0.75)
pm.setAttr(neck_cnst_list[12].M_NeckRot_1_01_ctrlW1, 0.0)
pm.setAttr(neck_cnst_list[12].M_NeckRot_2_01_ctrlW2, 0.0)

pm.setAttr(neck_cnst_list[13].M_NeckRot_0_01_ctrlW0, 0.5)
pm.setAttr(neck_cnst_list[13].M_NeckRot_1_01_ctrlW1, 0.0)
pm.setAttr(neck_cnst_list[13].M_NeckRot_2_01_ctrlW2, 0.0)

pm.setAttr(neck_cnst_list[14].M_NeckRot_0_01_ctrlW0, 0.25)
pm.setAttr(neck_cnst_list[14].M_NeckRot_1_01_ctrlW1, 0.0)
pm.setAttr(neck_cnst_list[14].M_NeckRot_2_01_ctrlW2, 0.0)

pm.setAttr(neck_cnst_list[15].M_NeckRot_0_01_ctrlW0, 0.0)
pm.setAttr(neck_cnst_list[15].M_NeckRot_1_01_ctrlW1, 0.0)
pm.setAttr(neck_cnst_list[15].M_NeckRot_2_01_ctrlW2, 0.0)
