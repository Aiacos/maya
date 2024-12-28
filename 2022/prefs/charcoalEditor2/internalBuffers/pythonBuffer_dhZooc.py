import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm
import mayaLib.rigLib.utils as utils

#tendons = ['Phalanges_tendon_geo', 'Legement_patela_geo', 'Hand_fatpad_geo', 'Genital_geo', 'Nipples_areola_geo', 'External_intercostal_geo', 'Feet_fatpad_geo']
#secondary = ['Abductor_pollicis_brevis_geo', 'Flexor_pollicis_brevis_geo', 'Abductor_digiti_minimi_geo', 'Flexor_digiti_minimi_brevis_geo', 'Palmaris_intersosseous_geo', 'Dorsal_interosseous_geo', 'Phalange_extensor_geo', 'Adductor_pollicis_geo', 'Tendons_geo', 'Abductor_hallucis_strains_geo']
#face = ['Orbicularis_oculi_geo', 'Orbicularis_oris_geo', 'Depressor_anguli_oris_copy1_geo', 'Ears_geo', 'Geniohyoid_mylohyoid_stylohyoid_geo', 'Digastric_geo', 'Cricoid_cartilage_geo', 'Zygo_major_minor_geo', 'Levator_labii_superioris_geo', 'Transverse_nasalis_geo', 'Temporalis_geo', 'Procerus_geo', 'Parotid_gland_geo', 'Nasalis_geo', 'Mentalis_geo', 'Masseter_geo', 'Masseter_risorius_geo', 'Lavator_superioris_geo', 'Frontalis_geo', 'Epicranial_aponeurosis_geo', 'Depressor_labii_inferioris_geo', 'Depressor_anguli_oris_geo', 'Buccinator_geo']


def split_geo_muscle(geo):
    geo_name = geo

    # Separate mesh
    split_geo_list = cmds.polySeparate(geo, ch=0)


    for split_geo in split_geo_list:
        # Center Pivot
        cmds.select(split_geo)
        mel.eval('CenterPivot;')

        # Check pivot and Rename
        rx, ry, rz, sx, sy, sz = cmds.xform(split_geo, piv=True, q=True)
        if rx > 0:
            cmds.rename(split_geo, 'L_' + geo_name)
        else:
            cmds.rename(split_geo, 'R_' + geo_name)
            
    cmds.parent(cmds.ls('?_'+geo_name), 'human_anatomy_final_grp|muscle_grp')
    cmds.parent(geo, '|to_delete_grp')
    
    
for geo in cmds.ls(sl=True):
    try:
        print(geo)
        split_geo_muscle(geo)
    except:
        pass