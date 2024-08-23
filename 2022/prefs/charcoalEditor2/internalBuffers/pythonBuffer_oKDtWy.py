import pymel.core as pm


def rename_enum(ctrl, enum_list):
    for attr_name in enum_list:
        attr = ctrl.name() + '.' + attr_name
        
        pm.addAttr(attr, edit=True, enumName='________')
        pm.setAttr(attr, lock=True)

def cleanup_attributes(ctrl, hide_attr_list):
    attr_list = pm.listAttr(ctrl, ud=True, v=True, s=True)
    for attr in attr_list:
        if attr in hide_attr_list:
            try:
                pm.setAttr(ctrl.name() + '.' + attr, lock=True, k=False, cb=False)
            except:
                pass
                
            
            
ctrl_list = pm.ls('*_ctrl')

hide_attr_list = ['secondary_ctrl', 'show_ik_ctrls', 'show_fk_ctrls', 'rotateOrder', '_______', 'Sine', 'amplitude', 'offset', 'wavelength', 'neck_mid_ctrl', 'auto_twist', 'ribbon_micro_ctrls', 'bezier_ctrls']
for ctrl in ctrl_list:
    cleanup_attributes(ctrl, hide_attr_list)
    
pm.setAttr('Base_main_secondary_offset_grp.visibility', 0)


vis_ctrl_list = pm.ls('Body_Visibility_01_ctrl', 'Face_Visibility_01_ctrl')
attr_list = ['Module_Wing', 'Module_Tail', 'Module_Toes', 'Module_Fly', 'Module_Neck', 'GEOMETRY', 'Module_Face', 'Module_Head']
for ctrl in vis_ctrl_list:
    for attr in attr_list:
        try:
            enum_list = pm.attributeQuery(attr, node=ctrl, listEnum=True)[-1]
            enum_list = enum_list.split(':')[0]
            pm.addAttr(ctrl.name() + '.' + attr, edit=True, enumName=enum_list)
            #pm.setAttr(ctrl.name() + '.' + attr, l=True)
        except:
            pass
            
pm.renameAttr('Body_Visibility_01_ctrl.' + attr_list[0], '____') # 4
pm.renameAttr('Body_Visibility_01_ctrl.' + attr_list[1], '_____') # 5
pm.renameAttr('Body_Visibility_01_ctrl.' + attr_list[2], '______') # 6
pm.renameAttr('Body_Visibility_01_ctrl.' + attr_list[3], '_______') # 7
pm.renameAttr('Body_Visibility_01_ctrl.' + attr_list[4], '________') # 8
pm.renameAttr('Body_Visibility_01_ctrl.' + attr_list[5], '_________') # 9
pm.renameAttr('Face_Visibility_01_ctrl.' + attr_list[6], '____') # 4
pm.renameAttr('Face_Visibility_01_ctrl.' + attr_list[7], '_____') # 5

pm.setAttr('Body_Visibility_01_ctrl.____', l=True) # 4
pm.setAttr('Body_Visibility_01_ctrl._____', l=True) # 5
pm.setAttr('Body_Visibility_01_ctrl.______', l=True) # 6
pm.setAttr('Body_Visibility_01_ctrl._______', l=True) # 7
pm.setAttr('Body_Visibility_01_ctrl.________', l=True) # 8
pm.setAttr('Body_Visibility_01_ctrl._________', l=True) # 9
pm.setAttr('Face_Visibility_01_ctrl.____', l=True) # 4
pm.setAttr('Face_Visibility_01_ctrl._____', l=True) # 5
