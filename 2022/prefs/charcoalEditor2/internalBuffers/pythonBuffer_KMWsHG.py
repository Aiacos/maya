import pymel.core as pm

for geo in pm.ls(sl=True):
    pm.polyRetopo(geo, tfc=250, phe=True)