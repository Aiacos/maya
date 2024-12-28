import pymel.core as pm

node_name = 'L_Crest'
ribbon_vtx = pm.ls(node_name + '_ribbon_bezier_nurb_surface.cv[3:11][3]', node_name + '_ribbon_bezier_nurb_surface.cv[2][3]', node_name + '_ribbon_bezier_nurb_surface.cv[1][3]', node_name + '_ribbon_bezier_nurb_surface.cv[0][3]')

sine_deformer = pm.nonLinear(ribbon_vtx, type='sine', n=node_name+'_nurbs_sine')[-1]
pm.parent(sine_deformer, node_name + '_ribbon_shape_grp')
#sine_deformer.rotateY.set(90)

pm.connectAttr(node_name + '_ribbon_0_ctrl.amplitude', sine_deformer.amplitude, f=True)
pm.connectAttr(node_name + '_ribbon_0_ctrl.offset', sine_deformer.offset, f=True)
pm.connectAttr(node_name + '_ribbon_0_ctrl.wavelength', sine_deformer.wavelength, f=True)