'''

Copyright Frigging Awesome Studios
friggingawesomestudios@gmail.com
http://www.friggingawesome.com

Run with:

import animPolish.growShrink as growShrink
reload (growShrink)
growShrink.func()

'''



from __future__ import absolute_import
try:
	from importlib import reload
except:
	pass

import maya.cmds as cmds
import maya.mel as mel
import sys
try:
	from six.moves import range
except:
	pass
import ast



def run_sel (hideData = 1, smooth = 3):

	sel = cmds.ls (sl = 1, o = 1)
	dfrmverts1 = cmds.textField ('jsap_misc_dfrmVerts_tf', q = 1, tx = 1)
	if dfrmverts1:
		dfrmverts = dfrmverts1
	else:
		dfrmverts = str(cmds.ls ('{}.vtx[*]'.format (sel[0]), fl = 1))
	floodverts = cmds.textField ('jsap_misc_floodVerts_tf', q = 1, tx = 1)
	geos = []
	surfs = []
	worked = 0
	if sel:
		for i in sel:
			if cmds.nodeType (i) == 'transform':
				geos.append (i)
			elif cmds.nodeType (i) == 'mesh':
				surfs.append (i)

		for geo in geos:
			check = run (geo, dfrmverts = dfrmverts, floodverts = floodverts, smooth = smooth, hideData = hideData)
			if check == 1:
				worked += 1

		'''
		for surf in surfs:
			geo = cmds.listRelatives (surf, p = 1, f = 1)[0]
			geos.append (geo)
			check = run (geo, dfrmverts = dfrmverts, floodverts = floodverts, smooth = smooth, hideData = hideData)
			if check == 1:
				worked += 1
		'''

		cmds.select (geos)
		if worked >= 2:
			sys.stdout.write ("Created 'Grow/Shrink' on multiple objects.")
	else:
		cmds.warning ('Select some meshes!')



def run (geo, dfrmverts = [], floodverts = [], cb = '', hideData = 1, smooth = 3, its = 3):

	worked = 0

	dfrmverts = ast.literal_eval (dfrmverts)
	if floodverts:
		floodverts = ast.literal_eval (floodverts)

	# Check for existing
	attrs1 = cmds.listAttr (geo, k = 1)
	attrs = []
	for a in attrs1:
		if 'growShrink' in a:
			attrs.append (a)
	if attrs:
		num = len(attrs) + 1
	else:
		num = 1

	# Get isolated verts
	isoVerts = []
	if floodverts:
		for v in floodverts:
			#print(v)
			#print(geo)
			if (v.split ('|')[-1]).startswith (geo.split ('|')[-1]):
				isoVerts.append (v)

	# Duplicate and blend back
	dup = cmds.duplicate (geo, n = '{}_growShrink_{}_LIVE'.format (geo,num), ic = 1, rr = 1)[0]
	dfrmverts = str(dfrmverts).replace (geo,dup)
	dfrmverts = ast.literal_eval (dfrmverts)
	cmds.setAttr ('{}.v'.format (dup), 0)
	if hideData == 1:
		cmds.setAttr ('{}.hiddenInOutliner'.format (dup), 1)
	for a in ['tx','ty','tz','rx','ry','rz','sx','sy','sz']:
		cmds.setAttr ('{}.{}'.format (dup,a), l = 0)
		try:
			mel.eval ('source channelBoxCommand;')
			mel.eval ('CBunlockAttr "{}.{}"'.format (dup,a))
		except:
			pass
	'''
	par = cmds.listRelatives (dup, p = 1, f = 1)
	if par:
		cmds.parent (dup, w = 1)
	'''
	bs = cmds.blendShape (dup, geo, n = '{}_growShrink_{}_BS'.format (geo.split ('|')[-1],num), o = 'world', w = [0,1])[0]

	# Add attribute control
	ln = 'growShrink_{}'.format (num)
	nn = 'Grow/Shrink {}'.format (num)
	cmds.addAttr (geo, at = 'float', dv = .1, k = 1, ln = ln, nn = nn)

	# Create polyMoveVertex
	pmv = cmds.polyMoveVertex (dfrmverts)[0]
	cmds.connectAttr ('{}.growShrink_{}'.format (geo,num), '{}.ltz'.format (pmv))

	# Flood verts
	if isoVerts:
		flood (isoVerts, bs, smooth = smooth)

	# Finalize
	cmds.setAttr ('{}.v'.format (dup), 0)
	cmds.select (geo)
	sys.stdout.write ("Created 'Grow/Shrink' on '{}'.".format (geo.split ('|')[-1]))
	worked = 1

	return worked



def flood (verts, bs, smooth = 3):

	obj = str(verts[0]).split ('.')[0]
	cmds.hilite (obj, replace = 1)

	mel.eval ('ArtPaintBlendShapeWeightsTool')
	mel.eval ('artSetToolAndSelectAttr( "artAttrCtx", "blendShape.{}.baseWeights" );'.format (bs))
	cmds.select (verts)
	mel.eval ('artAttrPaintOperation artAttrCtx Replace;')
	mel.eval ('artAttrCtx -e -opacity 1 `currentCtx`;')
	mel.eval ('artAttrCtx -e -value 0 `currentCtx`;')
	cmds.select (verts)
	mel.eval ('invertSelection;')
	mel.eval ('artAttrCtx -e -clear `currentCtx`;')

	mel.eval ('artAttrPaintOperation artAttrCtx Smooth;')
	mel.eval ('artAttrCtx -e -opacity 1 `currentCtx`;')
	cmds.select ('{}.vtx[*]'.format (obj))
	for i in range (smooth):
		mel.eval ('artAttrCtx -e -clear `currentCtx`;')

	cmds.select (obj)
	mel.eval ('SelectTool;')