import pymel.core as pm

ctrl_list = pm.ls('M_Tail' + '_tentacle?_ctrl')
ctrl_list.reverse()

print(ctrl_list)

for ctrl in ctrl_list:
    ctrl_parent = ctrl.getParent()
    index = ctrl_list.index(ctrl)

    if index < len(ctrl_list)-1:
        pm.parent(ctrl_parent, ctrl_list[index+1])