'''

Copyright Frigging Awesome Studios
friggingawesomestudios@gmail.com
http://www.friggingawesome.com

Run with:

import animPolish.wrap as wrap
from importlib import reload
reload (wrap)
wrap.func ()

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



####################
### Wrap To Mesh ###
####################



### Wrap To Mesh
  # Wraps a duplicate to another mesh and blends in

def wrapToMesh_sel (verts = [], smooth = 3, hideData = 1):

	# Check if selection is okay
	sel = cmds.ls (sl = 1)
	if sel:
		if len(sel) >= 2:
			drvr = sel[-1]
			for drvn in sel:
				if drvn != drvr:

					# Make vert list
					drvnVerts = []
					if verts:
						#exec ('verts = {}'.format (verts))
						verts = ast.literal_eval (verts)
						for v in verts:
							if v.startswith ('{}.vtx['.format (drvn)):
								drvnVerts.append (v)

					# Run
					wrapToMesh (drvn, drvr, verts = drvnVerts, smooth = smooth, hideData = hideData)

			# Finalize
			cmds.select (sel)
			cmds.select (drvr, tgl = 1)
			if len(sel) >= 3:
				sys.stdout.write ("Wrapped multiple meshes to '{}'.".format (drvr))

		else:
			cmds.warning ('Select some objects to wrap, followed by an object to wrap to.')
	else:
		cmds.warning ('Select some objects to wrap, followed by an object to wrap to.')

def wrapToMesh (drvn, drvr, verts = [], smooth = 3, hideData = 1):

	# Duplicate and wrap
	dup = duplicate (drvn, n = '{}_wrap_1'.format (drvn))
	cmds.select (dup, drvr)
	wrap = mel.eval ('doWrapArgList "7" { "1","0","1", "2", "0", "1", "0", "0" }')

	# Create blend shape
	bs = cmds.blendShape (dup, drvn, n = '{}_BS'.format (dup), o = 'world', w = [0,1])[0]

	# Add keyable attribute
	cf = int(cmds.currentTime (q = 1))
	attrs = cmds.listAttr (drvn, k = 1)
	cnt = 1
	for a in attrs:
		if a.startswith ('fr{}_'.format (cf)) and a.endswith ('_wrap'):
			cnt += 1
	cmds.addAttr (drvn, at = 'float', k = 1, min = 0, max = 1, dv = 1, ln = 'fr{}_{}_wrap'.format (cf,cnt), nn = 'Wrap | Fr{}_{}'.format (cf,cnt))
	cmds.connectAttr ('{}.fr{}_{}_wrap'.format (drvn,cf,cnt), '{}.envelope'.format (bs))

	# Hide data
	bases = cmds.ls ('{}Base*'.format (drvr))
	for b in bases:
		if hideData == 1:
			cmds.setAttr ('{}.hiddenInOutliner'.format (b), 1)
		if cmds.objExists ('{}.polish_cache_origGeo'.format (b)):
			cmds.deleteAttr ('{}.polish_cache_origGeo'.format (b))

	# Flood and smooth
	if verts:
		floodReplace (bs, verts)
		if smooth >= 1:
			floodSmooth (bs, drvn, smooth = smooth)

	# Finalize
	cmds.select (drvn)
	sys.stdout.write ("Wraped '{}' to '{}'.".format (drvn, drvr))



#####################
### Wrap To World ###
#####################



### Wrap To World
  # Blends in a duplicate frozen in space

def wrapToWorld_sel (verts = [], smooth = 3, hideData = 1):

	# Check if selection is okay
	sel = cmds.ls (sl = 1)
	if sel:
		for drvn in sel:

			# Make vert list
			drvnVerts = []
			if verts:
				#exec ('verts = {}'.format (verts))
				verts = ast.literal_eval (verts)
				for v in verts:
					if v.startswith ('{}.vtx['.format (drvn)):
						drvnVerts.append (v)

			# Run
			wrapToWorld (drvn, verts = drvnVerts, smooth = smooth, hideData = hideData)
			cmds.select (sel)

	else:
		cmds.warning ('Select some objects to wrap, followed by an object to wrap to.')

def wrapToWorld (drvn, verts = [], smooth = 3, hideData = 1):

	# Duplicate
	dup = duplicate (drvn, n = '{}_wrap_1'.format (drvn))

	# Create blend shape
	bs = cmds.blendShape (dup, drvn, n = '{}_BS'.format (dup), o = 'world', w = [0,1])[0]

	# Add keyable attribute
	cf = int(cmds.currentTime (q = 1))
	attrs = cmds.listAttr (drvn, k = 1)
	cnt = 1
	for a in attrs:
		if a.startswith ('fr{}_'.format (cf)) and a.endswith ('_wrap'):
			cnt += 1
	cmds.addAttr (drvn, at = 'float', k = 1, min = 0, max = 1, dv = 1, ln = 'fr{}_{}_wrap'.format (cf,cnt), nn = 'Wrap | Fr{}_{}'.format (cf,cnt))
	cmds.connectAttr ('{}.fr{}_{}_wrap'.format (drvn,cf,cnt), '{}.envelope'.format (bs))

	# Hide data
	#if hideData == 1:
		#cmds.setAttr ('{}.ihi'.format (bs), 0)

	# Flood and smooth
	if verts:
		floodReplace (bs, verts)
		if smooth >= 1:
			floodSmooth (bs, drvn, smooth = smooth)

	# Finalize
	cmds.select (drvn)
	sys.stdout.write ("Wraped '{}' to world.".format (drvn))



#####################
### Utility Funcs ###
#####################



### Duplicate Geo
  # Duplicate geo and parent to a wrap group

def duplicate (obj, n = '', grpPar = 1):

	# Duplicate
	dup = cmds.duplicate (obj, n = n)[0]
	for a in ['tx','ty','tz','rx','ry','rz','sx','sy','sz','v']:
		cmds.setAttr ('{}.{}'.format (dup,a), l = 0)
		try:
			mel.eval ('source channelBoxCommand;')
			mel.eval ('CBunlockAttr "{}.{}"'.format (dup,a))
		except:
			pass

	cmds.setAttr ('{}.v'.format (dup), 0)

	'''
	# Make group if it doesn't exist
	if grpPar == 1:
		grp = 'wrap_GRP'
		if not cmds.objExists (grp):
			cmds.group (n = grp, em = 1, w = 1)
			cmds.setAttr ('{}.v'.format (grp), 0)

		# Parent duplicate to group
		cmds.parent (dup, grp)
	'''

	return dup



### Flood Inverted Verts To Zero
  # Zeroes out the values on unselected verts

def floodReplace (bs, verts):

	obj = str(verts[0]).split ('.')[0]
	cmds.hilite (obj, replace = 1)
	cmds.select (verts)

	mel.eval ('ArtPaintBlendShapeWeightsTool')
	mel.eval ('artSetToolAndSelectAttr( "artAttrCtx", "blendShape.{}.baseWeights" );'.format (bs))
	mel.eval ('artAttrPaintOperation artAttrCtx Replace;')
	mel.eval ('artAttrCtx -e -opacity 1 `currentCtx`;')
	mel.eval ('artAttrCtx -e -value 0 `currentCtx`;')
	cmds.select (verts)
	mel.eval ('invertSelection;')
	mel.eval ('artAttrCtx -e -clear `currentCtx`;')

	cmds.select (obj)
	mel.eval ('SelectTool;')



### Flood Smooth
  # Flood smooths all verts

def floodSmooth (bs, obj, smooth = 3):

	cmds.hilite (obj, replace = 1)
	cmds.select ('{}.vtx[*]'.format (obj))

	mel.eval ('ArtPaintBlendShapeWeightsTool')
	mel.eval ('artSetToolAndSelectAttr( "artAttrCtx", "blendShape.{}.baseWeights" );'.format (bs))
	mel.eval ('artAttrPaintOperation artAttrCtx Smooth;')
	mel.eval ('artAttrCtx -e -opacity 1 `currentCtx`;')
	cmds.select ('{}.vtx[*]'.format (obj))
	for i in range (smooth):
		mel.eval ('artAttrCtx -e -clear `currentCtx`;')

	cmds.select (obj)
	mel.eval ('SelectTool;')



### Extract Animated Faces
  # Duplicates object, blend shapes into it, and deletes unselected faces

def extractFaces ():

	faces = cmds.ls (sl = 1, fl = 1)
	sel = cmds.ls (sl = 1, o = 1)
	if len(sel) == 1:
		if faces:
			if '.f[' in faces[0]:
				geo = faces[0].split ('.')[0]

				# Make group
				grp = 'extractFaces_GRP'
				if not cmds.objExists (grp):
					cmds.group (n = grp, em = 1, w = 1)

				# Duplicate and blend
				cnt = 1
				kids = cmds.listRelatives (grp, c = 1)
				if kids:
					for k in kids:
						if geo.split ('|')[-1] in k and k.endswith ('_extractFaces'):
							cnt += 1
				dup = duplicate (geo, n = '{}_{}_extractFaces'.format (geo.split ('|')[-1],cnt), grpPar = 0)
				cmds.parent (dup, grp)
				bs = cmds.blendShape (geo, dup, n = '{}_BS'.format (dup), o = 'world', w = [0,1])[0]

				# Delete faces
				invFaces = []
				allFaces = cmds.ls ('{}.f[*]'.format (dup), fl = 1)
				for f in allFaces:
					new = f.replace (dup,geo)
					if new not in faces:
						invFaces.append (f)
				cmds.delete (invFaces)

				# Finalize
				cmds.select (dup)
				sys.stdout.write ("Extracted faces from '{}'".format (geo))

			else:
				cmds.warning ('Select some faces.')
		else:
			cmds.warning ('Select some faces.')
	else:
		cmds.warning ('Select some faces on 1 object.')