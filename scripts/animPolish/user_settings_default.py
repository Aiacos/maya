from __future__ import absolute_import
try:
	from importlib import reload
except:
	pass

import maya.cmds as cmds

def run ():

	# Sculpt Pose
	try:
		cmds.frameLayout ('jsap_sculptPose_fl', e = 1, cl = False)
		cmds.checkBox ('jsap_scuVis_cb', e = 1, v = True)
		cmds.checkBox ('jsap_scuReshade_cb', e = 1, v = True)
		cmds.checkBox ('jsap_scuData_cb', e = 1, v = True)
		cmds.intField ('jsap_scuLevel_if', e = 1, v = 1)
		cmds.optionMenu ('jsap_sfz_om', e = 1, sl = 1)
	except:
		pass

	# Wrap ++
	try:
		cmds.frameLayout ('jsap_wrap_fl', e = 1, cl = False)
		cmds.intField ('jsap_wrap_autoSmooth_if', e = 1, v = 3)
	except:
		pass
		
	# Subdue
	try:
		cmds.frameLayout ('jsap_subdue_fl', e = 1, cl = False)
		cmds.intField ('jsap_subdue_resample_if', e = 1, v = 4)
		cmds.intField ('jsap_subdue_autoSmooth_if', e = 1, v = 3)
	except:
		pass
		
	# Misc. Deformation
	try:
		cmds.frameLayout ('jsap_miscDeformation_fl', e = 1, cl = True)
		cmds.intField ('jsap_misc_autoSmooth_if', e = 1, v = 3)
		cmds.checkBox ('jsap_misc_data_cb', e = 1, v = True)
	except:
		pass
		
	# Native Maya
	try:
		cmds.frameLayout ('jsap_nativeMaya_fl', e = 1, cl = True)
	except:
		pass
		
	# Assign Colors
	try:
		cmds.frameLayout ('jsap_assignColors_fl', e = 1, cl = True)
		cmds.radioCollection ('jsap_colorMode_rc', e = 1, sl = 'jsap_colorMode_blinn_rb')
	except:
		pass
		
	# Utilities
	try:
		cmds.frameLayout ('jsap_utilities_fl', e = 1, cl = True)
	except:
		pass
		
	# Caching
	try:
		cmds.frameLayout ('jsap_caching_fl', e = 1, cl = True)
	except:
		pass