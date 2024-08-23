import pymel.core as pm

shapeDeformed_node_list = pm.ls('*ShapeDeformed')

for shape in shapeDeformed_node_list:
    shape_old_name = str(shape.name())
    new_name = shape_old_name.replace('Deformed', '')
    pm.rename(shape, new_name)