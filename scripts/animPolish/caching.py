'''

Copyright Frigging Awesome Studios
friggingawesomestudios@gmail.com
http://www.friggingawesome.com

Run with:

import animPolish.caching as caching
reload (caching)
caching.func ()

'''



from __future__ import absolute_import
from __future__ import print_function
try:
	from importlib import reload
except:
	pass

import maya.cmds as cmds
import maya.mel as mel
import sys
import os
import ast



def exp_cams (path, cams):

	#exec ('cams = {}'.format (cams))
	cams = ast.literal_eval (cams)

	check = os.path.isdir (path)
	if not check:
		os.mkdir (path)

	sel = cmds.ls (sl = 1)
	cmds.select (cams)
	cmd = 'file -force -options "v=0;" -typ "mayaAscii" -es "{}/cameras.ma";'.format (path)
	mel.eval (cmd)
	if sel:
		cmds.select (sel)
	else:
		cmds.select (cl = 1)

	sys.stdout.write ("Exported '{}/cameras.ma'.".format (path))



def exp_geos (path, geos):

	'''
	geos = geos.replace ('[','')
	geos = geos.replace (']','')
	geos = geos.replace ("'", "")
	geos = geos.split (', ')
	'''
	geos = ast.literal_eval (geos)

	check = os.path.isdir (path)
	if not check:
		os.mkdir (path)
	
	st = cmds.playbackOptions (q = 1, min = 1)
	end = cmds.playbackOptions (q = 1, max = 1)
	st2 = cmds.playbackOptions (q = 1, ast = 1)
	end2 = cmds.playbackOptions (q = 1, aet = 1)

	roots = ''
	for geo in geos:
		if not roots:
			roots = '-root {}'.format (geo)
		else:
			roots = '{} -root {}'.format (roots,geo)

		meshes = [geo]
		kids = cmds.listRelatives (geo, ad = 1, type = 'transform', f = 1)
		if kids:
			for k in kids:
				meshes.append (k)
		for mesh in meshes:
			shps = cmds.listRelatives (mesh, s = 1, f = 1)
			if shps:
				shp = shps[0]
				nt = cmds.nodeType (shp)
				if nt == 'mesh':
					if not cmds.objExists ('{}.polish_cache_origGeo'.format (mesh)):
						cmds.addAttr (mesh, ln = 'polish_cache_origGeo', dt = 'string')
						cmds.setAttr ('{}.polish_cache_origGeo'.format (mesh), mesh, type = 'string')

	cmd = 'AbcExport -j "-frameRange {} {} -attr polish_cache_origGeo -uvWrite -writeVisibility -worldSpace -dataFormat ogawa {} -file {}/geometry.abc";'.format (st2,end2,roots,path)
	mel.eval (cmd)
	
	# Sample
	#   AbcExport -j "-frameRange 1 10 -attr testAttr -uvWrite -writeVisibility -dataFormat ogawa -root |bonnie2_v1_1:bonnie2|bonnie2_v1_1:geo_GRP|bonnie2_v1_1:unPrx_GEO_GRP|bonnie2_v1_1:clothes_GEO_GRP|bonnie2_v1_1:shirts_GEO_GRP|bonnie2_v1_1:longSleeve_GEO_GRP|bonnie2_v1_1:longSleeve_GEO -root |bonnie2_v1_1:bonnie2|bonnie2_v1_1:geo_GRP|bonnie2_v1_1:unPrx_GEO_GRP|bonnie2_v1_1:clothes_GEO_GRP|bonnie2_v1_1:pants_GEO_GRP|bonnie2_v1_1:pantsLong_GEO_GRP|bonnie2_v1_1:pants_GEO -file C:/Users/joshs/OneDrive/Desktop/Projects/Rigs/bonnie_2.0/bonnie2_v1.1/cache/alembic/abcTest4.abc";
	
	sys.stdout.write ("Exported '{}/geometry.abc'\n".format (path))



def imp_cams (path):

	if os.path.isfile ('{}/cameras.ma'.format (path)):
		cmd = 'file -import -type "mayaAscii" -ignoreVersion -mergeNamespacesOnClash false -rpr "cameras" -options "v=0;" "{}/cameras.ma";'.format (path)
		mel.eval (cmd)



def imp_geos (path):

	cmds.select (ado = 1)
	ws_stuff = cmds.ls (sl = 1)
	#print(ws_stuff)

	version = path.split ('/')[-1]
	rangeq = cmds.checkBox ('jsap_impFrameRange_cb', q = 1, v = 1)
	if rangeq == 1:
		cmd = 'AbcImport -mode import -fitTimeRange -setToStartFrame "{}/geometry.abc";'.format (path)
	else:
		cmd = 'AbcImport -mode import -setToStartFrame "{}/geometry.abc";'.format (path)
	abc = mel.eval (cmd)

	cmds.select (ado = 1)
	ws_stuff2 = cmds.ls (sl = 1)
	#print(ws_stuff2)

	geos = []
	for i in ws_stuff2:
		if i not in ws_stuff:
			geos.append (i)

	if abc:
		name = '_{}_ABC'.format (version)
		name2 = '_{}_ABC_CTRL'.format (version)
		abc = cmds.rename (abc, str(name))

		grp = cmds.group (n = name2, w = 1, em = 1)
		cmds.connectAttr ('{}.nodeState'.format (grp), '{}.nodeState'.format (abc))
		for a in ['tx','ty','tz','rx','ry','rz','sx','sy','sz']:
			cmds.setAttr ('{}.{}'.format (grp,a), k = 0, l = 1)
		if not cmds.objExists ('polish_ABC_CTRL_GRP'):
			parGrp = cmds.group (n = 'polish_ABC_CTRL_GRP', w = 1, em = 1)
			for a in ['tx','ty','tz','rx','ry','rz','sx','sy','sz']:
				cmds.setAttr ('{}.{}'.format (parGrp,a), k = 0, l = 1)
		grp = cmds.parent (grp, 'polish_ABC_CTRL_GRP')

		'''
		cons = cmds.listConnections (abc)
		ws = []
		for c in cons:
			nt = cmds.nodeType (c)
			try:
				shps = cmds.listRelatives (c, s = 1, f = 1)
				if shps:
					nt = cmds.nodeType (shps[0])
					if nt == 'mesh': 
						par = cmds.listRelatives (c, p = 1, f = 1)
						if not par:
							ws.append (c)
						else:
							check = 0
							geo = c
							while check == 0:
								par = cmds.listRelatives (geo, p = 1, f = 1)
								if par:
									geo = par[0]
								else:
									check = 1
									ws.append (geo)
			except:
				pass
					
		if ws:
			cmds.parent (ws, grp)
		'''
		cmds.parent (geos, grp)
		cmds.select (grp)
		sys.stdout.write ("Imported '{}'".format (version))

	else:
		cmds.warning ("No animated alembic cache found. This tool will not function properly with this import.")

	# Sample
	#   AbcImport -mode import -fitTimeRange -setToStartFrame "C:/Users/joshs/OneDrive/Desktop/Temp/polish/006_polish/geometry.abc";



def swap (path):

	version = path.split ('/')[-1]
	sel = cmds.ls (sl = 1)
	if sel:
		if len(sel) == 1:
			ctrl = sel[0]
			if ctrl.endswith ('_ABC_CTRL'):
				abc = ctrl.replace ('_CTRL','')
				path1 = cmds.getAttr ('{}.abc_File'.format (abc))
				old = path1.split ('/')[-2]
				path2 = path1.replace (old,version)
				cmds.setAttr ('{}.abc_File'.format (abc), path2, type = 'string')
				cmds.rename (ctrl, '_{}_ABC_CTRL'.format (version))
				cmds.rename (abc, '_{}_ABC'.format (version))
				sys.stdout.write ("Replaced '{}' with '{}'. If you don't see any change, save and re-open your file.".format (old,version))
			else:
				cmds.warning ("Select an '_ABC_CTRL' object in the outliner.")
		else:
			cmds.warning ("Select an '_ABC_CTRL' object in the outliner.")
	else:
		cmds.warning ("Select an '_ABC_CTRL' object in the outliner.")

	# Sample
	#   AbcImport -mode replace "C:/Users/joshs/OneDrive/Desktop/Temp/polish/011_polish/geometry.abc";



def attach_sel ():

	sel = cmds.ls (sl = 1)
	if sel:
		if len(sel) == 2:
			if sel[0].endswith ('ABC_CTRL') and sel[1].endswith ('ABC_CTRL'):
				src = sel[0]
				dest = sel[1]
				cmds.setAttr ('{}.v'.format (src), 0)
				if not cmds.objExists ('{}.envelope'.format (src)):
					cmds.addAttr (src, ln = 'envelope', at = 'float', min = 0, max = 1, k = 1, dv = 1)
				kidsDest = cmds.listRelatives (dest, ad = 1, f = 1, type = 'transform')
				kidsSrc = cmds.listRelatives (src, ad = 1, f = 1, type = 'transform')
				for geo in kidsSrc:
					shps = cmds.listRelatives (geo, s = 1, f = 1)
					if shps:
						shp = shps[0]
						nt = cmds.nodeType (shp)
						if nt == 'mesh':
							idx = kidsSrc.index (geo)
							orig = kidsDest[idx]
							if '|' in orig:
								short = orig.split ('|')[-1]
							else:
								short = orig
							bsn = '{}_polished_1_BS'.format (short)
							if cmds.objExists (bsn):
								bss = cmds.ls ('{}_polished_*_BS'.format (short), type = 'blendShape')
								num = len(bss) + 1
								bsn = '{}_polished_{}_BS'.format (short,num)
							bs = cmds.blendShape (geo, orig, n = bsn, o = 'world', w = [0,1])[0]
							cmds.connectAttr ('{}.envelope'.format (src), '{}.envelope'.format (bs))
			else:
				cmds.warning ("Select 2 '_ABC_CTRL' nodes in the outliner.")
		else:
			cmds.warning ("Select 2 '_ABC_CTRL' nodes in the outliner.")
	else:
		cmds.warning ("Select 2 '_ABC_CTRL' nodes in the outliner.")


def attach ():

	sel = cmds.ls (sl = 1)
	chars = []
	if sel:
		for char in sel:
			if char.startswith ('_') and 'polish' in char:
				chars.append (char)
		if chars:
			attach2 (chars)
		else:
			cmds.warning ("Select at least 1 '_ABC_CTRL' node, or nothing to automatically run on all.")
	else:
		chars = cmds.listRelatives ('polish_ABC_CTRL_GRP', c = 1, f = 1, type = 'transform')
		if chars:
			attach2 (chars)
		else:
			cmds.warning ("Select at least 1 '_ABC_CTRL' node, or nothing to automatically run on all.")
	
def attach2 (chars):

	errored = []
	for char in chars:

		if not cmds.objExists ('{}.envelope'.format (char)):
			cmds.addAttr (char, ln = 'envelope', at = 'float', min = 0, max = 1, k = 1, dv = 1)

		kids = cmds.listRelatives (char, ad = 1, f = 1, type = 'transform')
		for geo in kids:
			shps = cmds.listRelatives (geo, s = 1, f = 1)
			if shps:
				shp = shps[0]
				nt = cmds.nodeType (shp)
				if nt == 'mesh':
					if cmds.objExists ('{}.polish_cache_origGeo'.format (geo)):
						orig = cmds.getAttr ('{}.polish_cache_origGeo'.format (geo))
						if '|' in geo:
							short = geo.split ('|')[-1]
						else:
							short = geo
						bsn = '{}_polished_1_BS'.format (short)
						if cmds.objExists (bsn):
							bss = cmds.ls ('{}_polished_*_BS'.format (short), type = 'blendShape')
							num = len(bss) + 1
							bsn = '{}_polished_{}_BS'.format (short,num)
						try:
							bs = cmds.blendShape (geo, orig, n = bsn, o = 'world', w = [0,1])[0]
							cmds.connectAttr ('{}.envelope'.format (char), '{}.envelope'.format (bs))
						except:
							errored.append (geo)
							print("\nERROR: Could not attach '{}'.".format (geo.split('|')[-1]))
		if '|' in char:
			char1 = char.split ('|')[-1]
		else:
			char1 = char
		cmds.setAttr ('{}.v'.format (char), 0)
		print("Attached '{}'.".format (char1))
	
	cmds.select (chars)
	if not errored:
		sys.stdout.write ("Created blendshapes successfully.")
	else:
		sys.stdout.write ("Created blendshapes, but some failed. Check script editor for details.")



def delete ():

	sel = cmds.ls (sl = 1)
	if sel:
		for c in sel:
			if c.endswith ('_ABC_CTRL'):
				kids = cmds.listRelatives (c, ad = 1, type = 'transform', f = 1)
				if kids:
					for k in kids:
						shps = cmds.listRelatives (k, s = 1, f = 1)
						if shps:
							for s in shps:
								outs = cmds.listConnections (s, s = 0)
								if outs:
									for out in outs:
										if '_polished_' in out and out.endswith ('_BS'):
											cmds.delete (out)
				cmds.delete (c.replace ('_CTRL',''))
				cmds.delete (c)
				sys.stdout.write ("Deleted caches and blendshapes for '{}'".format (c))

			else:
				cmds.warning ("No '_ABC_CTRL's selected.")
	else:
		cmds.warning ("No '_ABC_CTRL's selected.")