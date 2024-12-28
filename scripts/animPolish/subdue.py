'''

Copyright Frigging Awesome Studios
friggingawesomestudios@gmail.com
http://www.friggingawesome.com

Run with:

import animPolish.subdue as subdue
from importlib import reload
reload (subdue)
subdue.run()

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



def run (rate = 4, smooth = 3):

	mode = cmds.evaluationManager (q = 1, mode = 1)[0]
	if mode == 'parallel' or mode == 'serial':
		cmds.warning ("'Subdue' is unstable when animation evaluation is set to 'Parallel'. Use the 'Toggle DG/Parallel' button at the top of the AnimPolish UI to switch to 'DG'.")
	else:

		sel = cmds.ls (sl = 1, fl = 1, l = 1)
		if sel:

			cf = cmds.currentTime (q = 1)

			# Get lists of geo
			shps = cmds.ls (sl = 1, o = 1, l = 1)
			geos = []
			verts = []
			for s in shps:
				nt = cmds.nodeType (s)
				if nt == 'mesh':
					par = cmds.listRelatives (s, p = 1, f = 1)
					if par:
						if par[0] not in geos:
							geos.append (par[0])

			# Get lists of verts and remaining geo
			for i in sel:
				if '.vtx[' in i:
					if i not in verts:
						verts.append (i)
				elif cmds.nodeType (i) != 'mesh':
					if i not in geos:
						geos.append (i)
					verts1 = cmds.ls ('{}.vtx[*]'.format (i), fl = 1, l = 1)
					for v in verts1:
						if v not in verts:
							verts.append (v)

			# Dup and blend
			dups = []
			blends = []
			tweaks = []
			for i in geos:
				sbds = cmds.ls ('{}_*_SBD'.format (i.split ('|')[-1]))
				if sbds:
					cnt = len(sbds) + 1
				else:
					cnt = 1
				dup = cmds.duplicate (i, n = '{}_{}_SBD'.format (i.split ('|')[-1],cnt))[0]
				cmds.setAttr ('{}.hiddenInOutliner'.format (dup), 1)
				cmds.setAttr ('{}.v'.format (dup), 0)
				cmds.addAttr (dup, dt = 'string', ln = 'origGeo')
				cmds.setAttr ('{}.origGeo'.format (dup), i, type = 'string')
				for a in ['tx','ty','tz','rx','ry','rz','sx','sy','sz']:
					cmds.setAttr ('{}.{}'.format (dup,a), l = 0)
					try:
						mel.eval ('source channelBoxCommand;')
						mel.eval ('CBunlockAttr "{}.{}"'.format (dup,a))
					except:
						pass
				par = cmds.listRelatives (dup, p = 1, f = 1)
				if par:
					cmds.parent (dup, w = 1)
				bs = cmds.blendShape (i, dup, o = 'world', w = [0,1])[0]
				hists = cmds.listHistory (dup)
				for h in hists:
					if h.startswith ('tweak'):
						tweaks.append (h)
				dups.append (dup)
				blends.append (bs)
			
			# Get dup verts
			dupVerts = []
			for v in verts:
				new = v.replace (v.split ('.')[0], '{}_{}_SBD'.format (v.split ('.')[0],cnt))
				dupVerts.append (new)

			# Bake
			cmds.select (cl = 1)
			for i in dups:
				cmds.select ('{}.vtx[*]'.format (i), add = 1)
			bakeVerts = cmds.ls (sl = 1, fl = 1)
			cmds.refresh (su = 1)
			st = cmds.playbackOptions (q = 1, min = 1)
			end = cmds.playbackOptions (q = 1, max = 1)
			cmds.refresh ()
			sys.stdout.write ("Baking verts to animation curves...ignore any error flashes.")
			cmds.bakeResults (sm = 1, t = (st,end), s = 0, cp = 1)
			cmds.refresh (su = 0)

			# Rebuild curves
			crvs = []
			for d in dups:
				if ':' in d:
					d2 = d.split (':')[1]
				else:
					d2 = d
				crvs1 = cmds.ls ('{}*'.format (d2), type = 'animCurveTL')
				for c in crvs1:
					crvs.append (c)
			cmds.filterCurve (crvs, f = 'resample', ker = 'gaussian2', per = rate)
			cmds.keyTangent (crvs, e = 1, itt = 'auto', ott = 'auto')

			# Geocache
			cmds.select (dups)
			cmds.refresh (su = 1)
			sys.stdout.write ("Geocaching and simplifying curves...Click 'Auto-Rename' if prompted.")
			mel.eval ('doCreateGeometryCache 6 { "2", "1", "10", "OneFile", "1", "","0","","0", "add", "0", "1", "1","0","1","mcx","0" } ;')
			cmds.refresh (su = 0)

			# Delete animation data
			cmds.delete (crvs)
			for t in tweaks:
				if ':' in t:
					t2 = t.split (':')[1]
				else:
					t2 = t
				crvs = cmds.ls ('{}*'.format (t2), type = 'animCurveTL')
				if crvs:
					cmds.delete (crvs)

			# Blend back
			for d in dups:
				orig = cmds.getAttr ('{}.origGeo'.format (d))
				sbds = cmds.ls ('{}_*_SBD'.format (orig.split ('|')[-1]))
				if sbds:
					cnt = len(sbds)
				else:
					cnt = 1
				bs = cmds.blendShape (d, orig, o = 'world', w = [0,1], n = '{}_BS'.format (d))[0]
				cmds.addAttr (orig, at = 'float', min = 0, max = 1, ln = 'subdue{}'.format (cnt), k = 1, dv = 1)
				cmds.connectAttr ('{}.subdue{}'.format (orig,cnt), '{}.envelope'.format (bs))
				newVerts = []
				for v in verts:
					if (cmds.getAttr ('{}.origGeo'.format (d))).split ('|')[-1] in v:
						newVerts.append (v)
				if newVerts:
					flood (newVerts, bs, smooth = smooth)

			cmds.select (geos)
			cmds.currentTime (cf)
			if len(geos) == 1:
				sys.stdout.write ("Subdued '{}'".format (geos[0].split ('|')[-1]))
			else:
				sys.stdout.write ("Subdued multiple meshes.")

		else:
			cmds.warning ('Select some meshes and/or verts!')



def flood (verts, bs, smooth = 3):

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

	mel.eval ('artAttrPaintOperation artAttrCtx Smooth;')
	mel.eval ('artAttrCtx -e -opacity 1 `currentCtx`;')
	cmds.select ('{}.vtx[*]'.format (obj))
	for i in range (smooth):
		mel.eval ('artAttrCtx -e -clear `currentCtx`;')

	cmds.select (obj)
	mel.eval ('SelectTool;')