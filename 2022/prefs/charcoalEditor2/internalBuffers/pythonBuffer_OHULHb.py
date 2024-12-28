import pymel.core as pm


attr = node_name + "_ik_tip_ctrl.parent_space_switch"
enum_name = pm.addAttr(attr, q=True)
print(enum_name)
pm.addAttr(attr, edit=True, enumName='________')
pm.setAttr(attr, lock=True)



enum_list = pm.attributeQuery('parent_space_switch', node=node_name+'_ik_tip_ctrl', listEnum=True)[-1]
enum_list = enum_list.replace('local', 'world')
pm.addAttr(attr, edit=True, enumName=enum_list)