import pymel.core as pm

cloth_node_list = pm.ls('*_proxy_nCloth1')
for cloth in cloth_node_list:
    cloth_shape = cloth.getShape()
    cloth_out_shape_plug = pm.listConnections(cloth_shape.outputMesh, p=True, d=True)[-1]
    cloth_in_shape_plug = pm.listConnections(cloth_shape.inputMesh, p=True, s=True)
    
    
    print(cloth_in_shape_plug)