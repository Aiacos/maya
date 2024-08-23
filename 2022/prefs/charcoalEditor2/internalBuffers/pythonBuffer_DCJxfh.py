import pymel.core as pm

n = Arise.API.selected_nodes

for node in n:
    name = str(node).split(' ')[0]
    grp = name + '_grp'
    
    print(grp)