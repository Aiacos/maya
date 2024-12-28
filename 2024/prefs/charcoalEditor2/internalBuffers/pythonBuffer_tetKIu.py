import pymel.core as pm
import mayaLib.rigLib.utils.skin as skin

#selection_list = pm.ls(sl=True)

for geo in selection_list:
    r_geo = pm.ls(str(geo.name()).replace('L_', 'R_'))[-1]
    print(geo, r_geo)
    geo_skincluster = skin.findRelatedSkinCluster(geo)
    r_geo_skincluster = skin.findRelatedSkinCluster(r_geo)
    
    pm.copySkinWeights( ss=geo_skincluster, ds=r_geo_skincluster, mirrorMode='YZ', mirrorInverse=True )