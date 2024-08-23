import pymel.core as pm

clothShape = pm.ls('|nCloth1|nClothShape1')[-1]
conn = pm.listConnections(clothShape.inputMesh, p=True)[-1]
print(conn)


import pymel.core as pm


ctrl_list = pm.ls(node_name + '_fk_chain_?_ctrl')
for ctrl in ctrl_list:
    ctrl.parent_space_switch.set(1)