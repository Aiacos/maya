'''

Copyright Frigging Awesome Studios
friggingawesomestudios@gmail.com
http://www.friggingawesome.com

Run dedicated UI:

import animPolish.sculptPose as sculptPose
from importlib import reload
reload (sculptPose)
sculptPose.ui ()

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
import re



###########
### Run ###
###########



### Run
  # Basic function when applying sculpts in any mode

def run_sel (lv = 1, ihi = 1):

	sel = cmds.ls (sl = 1)
	if len(sel) == 2:
		run (sel[0], sel[1], 'standard', lv = lv, ihi = ihi)
	else:
		cmds.warning ('Select sculpted mesh, then original mesh.')

def run (scu, geo, mode, lv = 1, ihi = 1):

	cmds.refresh ()
	sys.stdout.write ("Calculating...")
	cmds.refresh ()

	txt = cmds.textField ('jsap_scu_prefix_tf', q = 1, tx = 1)
	if txt:
		pre = txt
	else:
		pre = 'Sculpt'

	# Get frame and name
	fr = int(cmds.currentTime (q = 1))
	attrs = cmds.listAttr (geo, k = 1)
	nums_s = []
	nums_p = []
	for a in attrs:
		if a.startswith ('fr{}_'.format (fr)) and a.endswith ('_scu'):
			num = a.split ('_')[1]
			num = int(num.split ('_')[0])
			nums_s.append (num)
		elif a.startswith ('lv{}_fr{}'.format (lv,fr)):
			num = a.split ('_')[2]
			num = int(num.split ('_')[0])
			nums_p.append (num)
	nums_s.sort ()
	nums_p.sort ()
	
	if mode == 'standard':
		if len(nums_s) >= 1:
			cnt = nums_s[-1] + 1
			name = 'fr{}_{}_scu'.format (fr,cnt)
			nn = '{} | Fr{}_{}'.format (pre,fr,cnt)
		else:
			name = 'fr{}_1_scu'.format (fr)
			nn = '{} | Fr{}_1'.format (pre,fr)
	elif mode == 'p2p':
		if len(nums_p) >= 1:
			cnt = nums_p[-1] + 1
			name = 'lv{}_fr{}_{}_p2p'.format (lv,fr,cnt)
			nn = 'P2P Sculpt | Lv{} | Fr{}_{}'.format (lv,fr,cnt)
		else:
			name = 'lv{}_fr{}_1_p2p'.format (lv,fr)
			nn = 'P2P Sculpt | Lv{} | Fr{}_1'.format (lv,fr)

	# Get vtx
	vtxs = cmds.ls ('{}.vtx[*:*]'.format (geo), fl = 1)
	vtxOffs = []
	vtxOffIds = []
	geoPoss = []
	scuPoss = []

	# Get coordinates and add to lists
	for i in vtxs:
		vtxId = i.split ('[')[1]
		vtxId = vtxId.split (']')[0]
		geoPos1 = cmds.pointPosition ('{}.vtx[{}]'.format (geo,vtxId))
		scuPos1 = cmds.pointPosition ('{}.vtx[{}]'.format (scu,vtxId))
		geoPos = [round (geoPos1[0], 4), round (geoPos1[1], 4), round (geoPos1[2], 4)]
		scuPos = [round (scuPos1[0], 4), round (scuPos1[1], 4), round (scuPos1[2], 4)]
		if not geoPos == scuPos:
			vtxOffs.append ('{}.vtx[{}]'.format (geo,vtxId))
			vtxOffIds.append (vtxId)
			geoPoss.append (geoPos)
			scuPoss.append (scuPos)

	# Get existing deformer count
	if '|' in geo:
		geoShort = geo.split ('|')[-1]
	else:
		geoShort = geo
	geoShort = geoShort.replace (':','__')
	'''
	dfrms = cmds.ls ('{}_*_scuX_CLUS*'.format (geoShort))
	if dfrms:
		clusX_name = '{}_{}_scuX_CLUS'.format (geoShort,len(dfrms)+1)
		clusY_name = '{}_{}_scuY_CLUS'.format (geoShort,len(dfrms)+1)
		clusZ_name = '{}_{}_scuZ_CLUS'.format (geoShort,len(dfrms)+1)
	else:
		clusX_name = '{}_1_scuX_CLUS'.format (geoShort)
		clusY_name = '{}_1_scuY_CLUS'.format (geoShort)
		clusZ_name = '{}_1_scuZ_CLUS'.format (geoShort)
	'''
	clusX_name = '{}__{}__scuX_CLUS'.format (geoShort,name)
	clusY_name = '{}__{}__scuY_CLUS'.format (geoShort,name)
	clusZ_name = '{}__{}__scuZ_CLUS'.format (geoShort,name)

	# Create cluster for x
	cmds.select (vtxOffs)
	clusX = cmds.cluster (n = clusX_name)
	cmds.setAttr ('{}.io'.format (clusX[1]), 1)
	if ihi == 1:
		cmds.setAttr ('{}.ihi'.format (clusX[0]), 0)
	cmds.setAttr ('{}.tx'.format (clusX[1]), 1)

	# Create cluster for y
	cmds.select (vtxOffs)
	clusY = cmds.cluster (n = clusY_name)
	cmds.setAttr ('{}.io'.format (clusY[1]), 1)
	if ihi == 1:
		cmds.setAttr ('{}.ihi'.format (clusY[0]), 0)
	cmds.setAttr ('{}.ty'.format (clusY[1]), 1)

	# Create cluster for z
	cmds.select (vtxOffs)
	clusZ = cmds.cluster (n = clusZ_name)
	cmds.setAttr ('{}.io'.format (clusZ[1]), 1)
	if ihi == 1:
		cmds.setAttr ('{}.ihi'.format (clusZ[0]), 0)
	cmds.setAttr ('{}.tz'.format (clusZ[1]), 1)

	# Set deformer values
	for i in vtxOffIds:
		ind = vtxOffIds.index (i)
		cmds.setAttr ('{}.nodeState'.format (clusX[0]), 1)
		cmds.setAttr ('{}.nodeState'.format (clusY[0]), 1)
		cmds.setAttr ('{}.nodeState'.format (clusZ[0]), 1)
		#cmds.percent (clusX[0], '{}.vtx[{}]'.format (geo,i), v = scuPoss[ind][0] - geoPoss[ind][0])
		#cmds.percent (clusY[0], '{}.vtx[{}]'.format (geo,i), v = scuPoss[ind][1] - geoPoss[ind][1])
		#cmds.percent (clusZ[0], '{}.vtx[{}]'.format (geo,i), v = scuPoss[ind][2] - geoPoss[ind][2])
		cmds.setAttr ('{}.wl[0].w[{}]'.format (clusX[0],i), scuPoss[ind][0] - geoPoss[ind][0])
		cmds.setAttr ('{}.wl[0].w[{}]'.format (clusY[0],i), scuPoss[ind][1] - geoPoss[ind][1])
		cmds.setAttr ('{}.wl[0].w[{}]'.format (clusZ[0],i), scuPoss[ind][2] - geoPoss[ind][2])
		cmds.setAttr ('{}.nodeState'.format (clusX[0]), 0)
		cmds.setAttr ('{}.nodeState'.format (clusY[0]), 0)
		cmds.setAttr ('{}.nodeState'.format (clusZ[0]), 0)

	# Add keyable attr
	cmds.addAttr (geo, ln = name, nn = nn, at = 'float', min = 0, max = 1, dv = 1, k = 1)
	if mode == 'standard':
		cmds.connectAttr('{}.{}'.format (geo,name), '{}.envelope'.format (clusX[0]))
		cmds.connectAttr('{}.{}'.format (geo,name), '{}.envelope'.format (clusY[0]))
		cmds.connectAttr('{}.{}'.format (geo,name), '{}.envelope'.format (clusZ[0]))
	elif mode == 'p2p':
		if not cmds.objExists ('{}.p2pLv{}Envelope'.format (geo,lv)):
			cmds.addAttr (geo, ln = 'p2pLv{}Envelope'.format (lv), nn = 'P2P Envelope | Lv{}'.format (lv), at = 'float', min = 0, max = 1, dv = 1, k = 1)
		mult = cmds.createNode ('multiplyDivide', n = '{}_{}_MULT'.format (geo,name))
		if ihi == 1:
			cmds.setAttr ('{}.ihi'.format (mult), 1)
		cmds.connectAttr ('{}.{}'.format (geo,name), '{}.input1X'.format (mult))
		cmds.connectAttr ('{}.p2pLv{}Envelope'.format (geo,lv), '{}.input2X'.format (mult))
		cmds.connectAttr ('{}.outputX'.format (mult), '{}.envelope'.format (clusX[0]))
		cmds.connectAttr ('{}.{}'.format (geo,name), '{}.input1Y'.format (mult))
		cmds.connectAttr ('{}.p2pLv{}Envelope'.format (geo,lv), '{}.input2Y'.format (mult))
		cmds.connectAttr ('{}.outputY'.format (mult), '{}.envelope'.format (clusY[0]))
		cmds.connectAttr ('{}.{}'.format (geo,name), '{}.input1Z'.format (mult))
		cmds.connectAttr ('{}.p2pLv{}Envelope'.format (geo,lv), '{}.input2Z'.format (mult))
		cmds.connectAttr ('{}.outputZ'.format (mult), '{}.envelope'.format (clusZ[0]))

	# Finalize
	cmds.delete (scu)
	cmds.select(geo)
	sortCB()

	return name



##############
### Sculpt ###
##############



### Sculpt
  # Duplicates geo, stores metadata, and applies custom shader

def sculpt_sel (vis = 1, shade = 1, editMode = 0):

	sel = cmds.ls (sl = 1)
	if len(sel) == 0:
		cmds.warning ('Select some meshes!')
	elif len(sel) >= 1:
		bads = []
		for g in sel:
			if g.endswith ('_scu'):
				bads.append (g)
		if not bads:
			scus = []
			for geo in sel:
				scu = sculpt (geo, vis = vis, shade = shade, editMode = editMode)
				scus.append (scu)
			cmds.select (scus)
			if len(scus) >= 2:
				sys.stdout.write ("Sculpting multiple meshes.")
		else:
			cmds.warning ("Can't sculpt a sculpt!")

def sculpt (geo, vis = 1, shade = 1, editMode = 0):

	if editMode == 1:
		drv = cmds.channelBox ('mainChannelBox', q = 1, sma = 1)[0]

	# Establish short name
	name = geo.split ('|')[-1]
	if ':' in name:
		name = name.split (':')[-1]
	exists = cmds.ls ('{}_*_scu'.format (name))
	if exists:
		num = len(exists) + 1
		name = '{}_{}_scu'.format (name,num)
	else:
		name = '{}_1_scu'.format (name)

	# Duplicate and memorize geo name
	scu = cmds.duplicate (geo, n = name)[0]
	if cmds.objExists ('{}.polish_cache_origGeo'.format (scu)):
		cmds.deleteAttr ('{}.polish_cache_origGeo'.format (scu))
	cmds.addAttr (scu, dt = 'string', ln = 'origGeo')
	cmds.setAttr ('{}.origGeo'.format (scu), geo, type = 'string')
	if editMode == 1:
		cmds.addAttr (scu, dt = 'string', ln = 'editDriver')
		cmds.setAttr ('{}.editDriver'.format (scu), drv, type = 'string')

	if shade == 1:
		# Assign new shader
		if not cmds.objExists ('sculptimate_SHD'):
			shd = cmds.shadingNode ('blinn', n = 'sculptimate_SHD', asShader = 1)
			cmds.setAttr ('sculptimate_SHD.color', .2549, .8348, 1, type = 'double3')
			cmds.setAttr ('sculptimate_SHD.specularColor', .254438, .254438, .254438, type = 'double3')
			cmds.setAttr ('sculptimate_SHD.eccentricity', .556157)
		else:
			shd = 'sculptimate_SHD'
		cmds.select (scu)
		cmds.hyperShade (assign = shd)

	if vis == 1:
		# Hide original geo
		shps = cmds.listRelatives (geo, s = 1, f = 1)
		for s in shps:
			try:
				cmds.setAttr ('{}.v'.format (s), 0)
			except:
				pass

	# Remove sculpt attrs on sculpt
	attrs = cmds.listAttr (scu, k = 1)
	for a in attrs:
		if a.endswith ('_p2p') or a.endswith ('_scu') or (a.startswith ('p2pLv') and a.endswith ('Envelope')):
			cmds.setAttr ('{}.{}'.format (scu, a), l = 0)
			cmds.deleteAttr ('{}.{}'.format (scu, a))

	sys.stdout.write ("Sculpting '{}'.".format (scu))
	
	return scu



def abortSculpt ():

	sel = cmds.ls (sl = 1)
	for scu in sel:
		if scu.endswith ('_scu'):
			exists = cmds.objExists ('{}.origGeo'.format (scu))
			if exists:
				orig = cmds.getAttr ('{}.origGeo'.format (scu))
				cmds.delete (scu)
				shps = cmds.listRelatives (orig, s = 1, f = 1)
				if shps:
					for s in shps:
						try:
							cmds.setAttr ('{}.v'.format (s), 1)
						except:
							pass




### Sculpt From Zero
  # After negating existing sculpt deformation...duplicates geo, stores metadata, and applies custom shader

def sculptFromZero_sel (vis = 1, shade = 1, lv = 1, mode = 1):

	sel = cmds.ls (sl = 1)
	if len(sel) == 0:
		cmds.warning ('Select some meshes!')
	elif len(sel) >= 1:
		bads = []
		for g in sel:
			if g.endswith ('_scu'):
				bads.append (g)
		if not bads:
			scus = []
			for geo in sel:
				scu = sculptFromZero (geo, vis = vis, shade = shade, lv = lv, mode = mode)
				scus.append (scu)
			cmds.select (scus)
			if len(scus) >= 2:
				sys.stdout.write ("Sculpting multiple meshes.")
		else:
			cmds.warning ("Can't sculpt a sculpt!")

def sculptFromZero (geo, vis = 1, shade = 1, lv = 1, mode = 1):

	# Turn off deformation
	attrs1 = getAttrs (geo)
	attrs = []
	for a in attrs1:
		if mode == 1:
			if a.endswith ('_p2p') or a.endswith ('_scu'):
				attrs.append (a)
		elif mode == 2:
			if a.endswith ('_scu'):
				attrs.append (a)
		elif mode == 3:
			if a.endswith ('_p2p'):
				attrs.append (a)
		elif mode == 4:
			if a.startswith ('lv{}_'.format (lv)):
				attrs.append (a)
	for a in attrs:
		cons = cmds.listConnections ('{}.{}'.format (geo,a))
		if cons:
			for c in cons:
				if '_p2p_MULT' in c:
					cons1 = cmds.listConnections (c)
					for c1 in cons1:
						if '_scuX' in c1 or '_scuY' in c1 or '_scuZ' in c1:
							cmds.setAttr ('{}.nodeState'.format (c1), 1)
				if '_scuX' in c or '_scuY' in c or '_scuZ' in c:
					cmds.setAttr ('{}.nodeState'.format (c), 1)

	# Start sculpting
	scu = sculpt (geo, vis = vis, shade = shade)

	# Turn on deformation
	for a in attrs:
		cons = cmds.listConnections ('{}.{}'.format (geo,a))
		if cons:
			for c in cons:
				if '_p2p_MULT' in c:
					cons1 = cmds.listConnections (c)
					for c1 in cons1:
						if '_scuX' in c1 or '_scuY' in c1 or '_scuZ' in c1:
							cmds.setAttr ('{}.nodeState'.format (c1), 0)
				if '_scuX' in c or '_scuY' in c or '_scuZ' in c:
					cmds.setAttr ('{}.nodeState'.format (c), 0)

	return scu



######################
### Apply Standard ###
######################



### Apply Standard
  # Applies the run func in standard mode and tidies up

def apply_sel (mode, lv = 1, ihi = 1):

	sel = cmds.ls (sl = 1)
	if len(sel) == 0:
		cmds.warning ('Select some sculpt geo!')
	else:
		bads = []
		geos = []
		for g in sel:
			if not g.endswith ('_scu'):
				bads.append (g)
			elif cmds.objExists ('{}.editDriver'.format (g)):
				bads.append (g)
		if not bads:
			for scu in sel:
				num = 1
				geo = cmds.getAttr ('{}.origGeo'.format (scu))
				apply (scu, mode, lv = lv, ihi = ihi)
				geos.append (geo)
			cmds.select (geos)
			if len(geos) >= 2:
				sys.stdout.write ("Applied multiple sculpts as keyable attributes.")
		else:
			cmds.warning ("You can only apply sculpts!")

def apply (scu, mode, lv = 1, ihi = 1):

	# Get original geo and apply
	geo = cmds.getAttr ('{}.origGeo'.format (scu))
	shps = cmds.listRelatives (geo, s = 1, f = 1)
	smooth = 0
	for s in shps:
		smoo = cmds.getAttr ('{}.displaySmoothMesh'.format (geo))
		if smoo == 2:
			smooth = 2
	if mode == 'standard':
		attr = run (scu, geo, 'standard', lv = lv, ihi = ihi)
	elif mode == 'p2p':
		attr = run (scu, geo, 'p2p', lv = lv, ihi = ihi)

	# Show original geo
	shps = cmds.listRelatives (geo, s = 1, f = 1)
	for s in shps:
		try:
			cmds.setAttr ('{}.v'.format (s), 1)
			if smooth == 2:
				cmds.setAttr ('{}.displaySmoothMesh'.format (s), 2)
		except:
			pass
	
	cmds.keyTangent (geo, at = attr, itt = 'linear', ott = 'linear')
	if mode == 'standard':
		sys.stdout.write ("Applied '{}' as a keyable attribute.".format (scu))

	return attr



### Apply Standard 1-Frame
  # Applies the run func in standard mode, tidies up, and keys 0-1-0 around current frame

def apply_1f_sel ():

	sel = cmds.ls (sl = 1)
	if len(sel) == 0:
		cmds.warning ('Select some sculpt geo!')
	else:
		bads = []
		geos = []
		for g in sel:
			if not g.endswith ('_scu'):
				bads.append (g)
		if not bads:
			for scu in sel:
				geo = cmds.getAttr ('{}.origGeo'.format (scu))
				apply_1f (scu)
				geos.append (geo)
			cmds.select (geos)
			if len(geos) >= 2:
				sys.stdout.write ("Applied multiple sculpts as keyable attributes and keyed 0-1-0 around current frame.")
		else:
			cmds.warning ("You can only apply sculpts!")

def apply_1f (scu, lv = 1, ihi = 1):

	# Apply
	geo = cmds.getAttr ('{}.origGeo'.format (scu))
	attr = apply (scu, 'standard', lv = lv, ihi = ihi)

	# Key
	cf = cmds.currentTime (q = 1)
	cmds.setKeyframe (geo, at = attr, time = cf, itt = 'linear', ott = 'linear', v = 1)
	cmds.setKeyframe (geo, at = attr, time = cf-1, itt = 'linear', ott = 'linear', v = 0)
	cmds.setKeyframe (geo, at = attr, time = cf+1, itt = 'linear', ott = 'linear', v = 0)
	cmds.keyTangent (geo, at = attr, itt = 'linear', ott = 'linear')

	sys.stdout.write ("Applied '{}' as a keyable attribute and keyed 0-1-0 around current frame".format (scu))

	return attr



##########################
### Apply Pose-To-Pose ###
##########################



### Apply Pose-To-Pose
  # Applies the run func in P2P mode, tidies up, and keys in and out of each sculpt

def apply_p2p_sel (lv = 1, ihi = 1):

	sel = cmds.ls (sl = 1)
	if len(sel) == 0:
		cmds.warning ('Select some sculpt geo!')
	elif len(sel) >= 1:
		bads = []
		geos = []
		for g in sel:
			if not g.endswith ('_scu'):
				bads.append (g)
		if not bads:
			for scu in sel:
				geo = cmds.getAttr ('{}.origGeo'.format (scu))
				apply_p2p (scu, lv = lv, ihi = ihi)
				geos.append (geo)
			cmds.select (geos)
			if len(geos) >= 2:
				sys.stdout.write ("Applied multiple sculpts as P2P attributes and re-keyed to interpolate between existing P2P shapes")
		else:
			cmds.warning ("You can only apply sculpts!")

def apply_p2p (scu, lv = 1, ihi = 1):

	# Apply
	geo = cmds.getAttr ('{}.origGeo'.format (scu))
	p2pPre (geo, lv)
	attr = apply (scu, 'p2p', lv = lv, ihi = ihi)

	# Get existing poses
	attrs1 = getAttrs (geo)
	attrs = []
	for a in attrs1:
		if a.startswith ('lv{}_'.format (lv)):
			attrs.append (a)
	
	# Get frames with sculpts
	frames = []
	for a in attrs:
		fr = a.split ('_')[1]
		fr = int(fr.split ('fr')[1])
		frames.append (fr)
	frames = list(set(frames))
	frames.sort()

	# Key
	for fr in frames:
		for a in attrs:
			fr1 = a.split ('_')[1]
			fr1 = int(fr1.split ('fr')[1])
			if fr1 == fr:
				cmds.setKeyframe (geo, at = a, time = [fr,fr], itt = 'linear', ott = 'linear', v = 1)
			else:
				cmds.setKeyframe (geo, at = a, time = [fr,fr], itt = 'linear', ott = 'linear', v = 0)
			cmds.keyframe (geo, at = a, e = 1, tds = 1)
			cmds.keyTangent (geo, at = a, itt = 'linear', ott = 'linear')
	
	cf = cmds.currentTime (q = 1)
	cmds.currentTime (cf-1, u = 0)
	cmds.currentTime (cf, u = 0)
	sys.stdout.write ("Applied '{}' as a P2P sculpt and re-keyed to interpolate between existing P2P shapes.".format (scu))



### Apply Pose-To-Pose Zero
  # For a non-sculpt, applies a blank P2P pose and keys in and out of it, as if it were applying an empty sculpt

def createP2PZero_sel (lv):

	sel = cmds.ls (sl = 1)
	if len(sel) == 0:
		cmds.warning ('Select some sculpt geo!')
	elif len(sel) >= 1:
		bads = []
		geos = []
		for g in sel:
			if g.endswith ('_scu'):
				bads.append (g)
		if not bads:
			for geo in sel:
				if not cmds.objExists ('{}.p2pLv{}Envelope'.format (geo, lv)):
					cmds.warning ("Can't find any P2P sculpts on this level.")
				else:
					createP2PZero (geo, lv)
			if len(sel) >= 2:
				sys.stdout.write ("Created zeroed P2P attributes for multiple meshes.")
		else:
			cmds.warning ("You can't apply this to a sculpt!")

def createP2PZero (geo, lv):

	# Get current frame
	cf = int(cmds.currentTime (q = 1))

	# Get frame and name
	fr = int(cmds.currentTime (q = 1))
	attrs = cmds.listAttr (geo, k = 1)
	nums_s = []
	nums_p = []
	for a in attrs:
		if a.startswith ('fr{}_'.format (fr)) and a.endswith ('_scu'):
			num = a.split ('_')[1]
			num = int(num.split ('_')[0])
			nums_s.append (num)
		elif a.startswith ('lv{}_fr{}'.format (lv,fr)):
			num = a.split ('_')[2]
			num = int(num.split ('_')[0])
			nums_p.append (num)
	nums_s.sort ()
	nums_p.sort ()
	
	if len(nums_p) >= 1:
		cnt = nums_p[-1] + 1
		name = 'lv{}_fr{}_{}_p2p'.format (lv,fr,cnt)
		nn = 'P2P Sculpt | Lv{} | Fr{}_{}'.format (lv,fr,cnt)
	else:
		name = 'lv{}_fr{}_1_p2p'.format (lv,fr)
		nn = 'P2P Sculpt | Lv{} | Fr{}_1'.format (lv,fr)

	# Get existing poses
	attrs1 = getAttrs (geo)
	attrs = []
	for a in attrs1:
		if a.startswith ('lv{}_'.format (lv)):
			attrs.append (a)
	attrs.append (name)

	# Get frames with sculpts
	frames = []
	for a in attrs:
		fr = a.split ('_')[1]
		fr = int(fr.split ('fr')[1])
		frames.append (fr)
	if cf not in frames:
		frames.append (cf)
	frames = list(set(frames))
	frames.sort()

	# Add dummy attr
	cmds.addAttr (geo, ln = name, nn = nn, at = 'float', min = 0, max = 1, dv = 1, k = 1)

	# Key
	for fr in frames:
		for a in attrs:
			fr1 = a.split ('_')[1]
			fr1 = int(fr1.split ('fr')[1])
			if fr1 == fr:
				cmds.setKeyframe (geo, at = a, time = [fr,fr], itt = 'linear', ott = 'linear', v = 1)
			else:
				cmds.setKeyframe (geo, at = a, time = [fr,fr], itt = 'linear', ott = 'linear', v = 0)
			cmds.keyframe (geo, at = a, e = 1, tds = 1)
			cmds.keyTangent (geo, at = a, itt = 'linear', ott = 'linear')

	sortCB ()

	sys.stdout.write ("Created a zeroed P2P attribute for '{}'.".format (geo))



### Apply Pose-To-Pose Hold
  # Applies the run func in P2P mode, tidies up, and keys in and out of each sculpt

def createP2PHold_sel (lv = 1, ihi = 1):

	sel = cmds.ls (sl = 1)
	if len(sel) == 0:
		cmds.warning ('Select some sculpt geo!')
	elif len(sel) >= 1:
		bads = []
		geos = []
		for g in sel:
			if g.endswith ('_scu'):
				bads.append (g)
		if not bads:
			for geo in sel:
				nope = 0
				if not cmds.objExists ('{}.p2pLv{}Envelope'.format (geo, lv)):
					nope = 1
					cmds.warning ("Can't find any P2P sculpts on this level.")
				else:
					createP2PHold (geo, lv = lv, ihi = ihi)
					geos.append (geo)
			if nope == 0:
				cmds.select (geos)
				if len(geos) >= 2:
					sys.stdout.write ("Held the previous P2P pose of multiple meshes until the current frame.")
		else:
			cmds.warning ("You can't apply this to a sculpt!")

def createP2PHold (geo, lv = 1, ihi = 1):

	# Get selection and current frame
	cf = int(cmds.currentTime (q = 1))

	# Get existing poses
	attrs1 = getAttrs (geo)
	attrs = []
	for a in attrs1:
		if a.startswith ('lv{}_'.format (lv)):
			attrs.append (a)

	# Get frames with sculpts
	frames = []
	for a in attrs:
		fr = a.split ('_')[1]
		fr = int(fr.split ('fr')[1])
		frames.append (fr)
	if cf not in frames:
		frames.append (cf)
	frames = list(set(frames))
	frames.sort()

	# Get previous P2P frame
	curInd = frames.index (cf)
	prevInd = (frames.index (cf))-1
	prev = frames[prevInd]

	# Set previous pose to 1, and others to 0
	for a in attrs:
		fr = a.split ('_')[1]
		fr = int(fr.split ('fr')[1])
		if fr != prev:
			cmds.setAttr ('{}.{}'.format (geo,a), 0)
		else:
			cmds.setAttr ('{}.{}'.format (geo,a), 1)
	cmds.currentTime (cf-1, u = 0)
	cmds.currentTime (cf, u = 0)

	# Duplicate and apply
	scu = sculpt (geo, vis = 0, shade = 1)
	p2pPre (geo, lv)
	apply_p2p (scu, lv = lv, ihi = ihi)
	sortCB ()

	sys.stdout.write ("Held the previous P2P pose of '{}' until the current frame.".format (geo))



#####################
### Utility Funcs ###
#####################



### P2P Pre-Run
  # Pre-emptively keys existing P2P sculpts

def p2pPre (geo, lv):

	# Get current frame
	cf = int(cmds.currentTime (q = 1))

	# Get frame and name
	fr = cf
	attrs = cmds.listAttr (geo, k = 1)
	cnt = 1
	for a in attrs:
		if a.startswith('fr{}_'.format (fr)) and a.endswith ('_scu'):
			cnt += 1
		elif a.startswith ('lv{}_fr{}_'.format (lv,fr)):
			cnt += 1
	if cnt > 1:
		name = 'lv{}_fr{}_{}_p2p'.format (lv,fr,cnt)
	else:
		name = 'lv{}_fr{}_1_p2p'.format (lv,fr)

	# Get existing poses
	attrs1 = getAttrs (geo)
	attrs = []
	for a in attrs1:
		if a.startswith ('lv{}_'.format (lv)):
			attrs.append (a)
	attrs.append (name)

	# Get frames with sculpts
	frames = []
	for a in attrs:
		fr = a.split ('_')[1]
		fr = int(fr.split ('fr')[1])
		frames.append (fr)
	if cf not in frames:
		frames.append (cf)
	frames = list(set(frames))
	frames.sort()

	# Add dummy attr
	cmds.addAttr (geo, ln = name, nn = name, at = 'float', min = 0, max = 1, dv = 1, k = 1)

	# Key
	for fr in frames:
		for a in attrs:
			fr1 = a.split ('_')[1]
			fr1 = int(fr1.split ('fr')[1])
			if fr1 == fr:
				cmds.setKeyframe (geo, at = a, time = [fr,fr], itt = 'linear', ott = 'linear', v = 1)
			else:
				cmds.setKeyframe (geo, at = a, time = [fr,fr], itt = 'linear', ott = 'linear', v = 0)
			cmds.keyframe (geo, at = a, e = 1, tds = 1)
			cmds.keyTangent (geo, at = a, itt = 'linear', ott = 'linear')

	# Delete dummy attr
	cmds.deleteAttr ('{}.{}'.format (geo,name))



### Get Attributes
  # Returns a list of existing sculpt poses

def getAttrs(geo):

	attrs1 = cmds.listAttr (geo, k = 1)
	attrs = []
	for a in attrs1:
		if a.endswith ('_scu') or a.endswith ('_p2p'):
			attrs.append (a)
	return attrs



### Sort Channel Box
  # Sorts channel box using the deleteAttr/undo trick

def sortCB():

	sel = cmds.ls (sl = 1)
	for geo in sel:
		attrs1 = cmds.listAttr (geo, k = 1)
		p2ps1 = []
		p2ps = []
		envs = []
		scus = []
		for a in attrs1:
			if a.endswith ('_scu'):
				scus.append (a)
			if a.endswith ('_p2p'):
				p2ps1.append (a)
			if a.endswith ('Envelope'):
				envs.append (a)

		scus.sort (key = sortKey)

		if p2ps1:

			p2ps1.sort (key = sortKey)
			envs.sort (key = sortKey)

			lv = 1
			if envs:
				p2ps = [envs[0]]
				for i in p2ps1:
					if 'lv{}_'.format (lv) not in i:
						lv += 1
						p2ps.append (envs[lv-1])
					p2ps.append (i)
		if scus:
			#for a in scus:
			#	cmds.setAttr ('{}.{}'.format (geo,a), l = 0)
			for a in scus:
				cmds.deleteAttr (geo, at = a)
				mel.eval ('Undo;')
				nn = cmds.attributeName ('{}.{}'.format (geo,a), nice = 1)
				#if '(EDIT^)' in nn:
				#	cmds.setAttr ('{}.{}'.format (geo,a), l = 1)

		if p2ps1:
			#for a in p2ps:
			#	cmds.setAttr ('{}.{}'.format (geo,a), l = 0)
			for a in p2ps:
				cmds.deleteAttr (geo, at = a)
				mel.eval ('Undo;')
				nn = cmds.attributeName ('{}.{}'.format (geo,a), nice = 1)
				#if '(EDIT^)' in nn:
				#	cmds.setAttr ('{}.{}'.format (geo,a), l = 1)

	sys.stdout.write ('Sorted channel box using the deleteAttr/undo trick.')



### Sort
  # General info for sorting

def sortKey(text):
	
	return [atoi(c) for c in re.split (r'(\d+)', text)]

def atoi(text):

	return int(text) if text.isdigit() else text



### Delete Sculpt
  # Deletes sculpt attributes and related nodes

def delete_sel (lv = 1, allP2P = 0):

	sel = cmds.ls (sl = 1)
	if sel:
		if len (sel) == 1:
			geo = sel[-1]
			attrs = []
			if allP2P == 0:
				attrs = cmds.channelBox ('mainChannelBox', q = 1, sma = 1)
			elif allP2P == 1:
				attrs1 = cmds.listAttr (geo, k = 1)
				attrs = []
				for a in attrs1:
					if a.startswith ('lv{}_'.format (lv)):
						attrs.append (a)
			if attrs:
				errors = []
				for a in attrs:
					if '_p2p' not in a and '_scu' not in a:
						errors.append (a)
					if errors:
						cmds.warning ('Select some sculpts in the channel box while 1 object is selected.')
					else:
						delete (geo, a, lv = lv, allP2P = allP2P)

			else:
				if allP2P == 0:
					cmds.warning ('Select some sculpts in the channel box while 1 object is selected.')
				elif allP2P == 1:
					cmds.warning ("Couldn't find any P2P sculpts on this level to delete.")
		else:
			cmds.warning ('Select 1 geo.')
	else:
		cmds.warning ('Select 1 geo.')

def delete (geo, a, lv = 1, allP2P = 0):

	cons = cmds.listConnections ('{}.{}'.format (geo,a), s = 0)
	toDel = []
	p2ps = []
	if cons:
		for c in cons:
			if '_p2p_MULT' in c:
				if c not in toDel:
					toDel.append (c)
				cons2 = cmds.listConnections (c, s = 0)
				for c2 in cons2:
					if '_CLUS' in c2:
						if c2 not in toDel:
							toDel.append (c2)
			if ('_CLUS' in c):
				if c not in toDel:
					toDel.append (c)
	if toDel:
		cmds.delete (toDel)

	#cmds.setAttr ('{}.{}'.format (geo,a), l = 0)
	cmds.deleteAttr ('{}.{}'.format (geo,a))
	if allP2P == 1:
		if cmds.objExists ('{}.p2pLv{}Envelope'.format (geo,lv)):
			cmds.deleteAttr ('{}.p2pLv{}Envelope'.format (geo,lv))

	else:

		# Delete existing keys
		keys = cmds.ls ('{}_{}*'.format (geo,a), '{}_lv{}_fr*_p2p*'.format (geo,lv), type = 'animCurve')
		if keys:
			cmds.delete (keys)
		if ':' in geo:
			keyname = geo.split (':')[1]
			keys = cmds.ls ('{}_{}*'.format (keyname,a), '{}_lv{}_fr*_p2p*'.format (keyname,lv), type = 'animCurve')
			cmds.delete (keys)

		if a.startswith ('lv{}_'.format (lv)):

			# Get existing poses
			attrs1 = getAttrs (geo)
			attrs = []
			for attr in attrs1:
				if attr.startswith ('lv{}_'.format (lv)):
					attrs.append (attr)
			
			# Get frames with sculpts
			frames = []
			for attr in attrs:
				fr = attr.split ('_')[1]
				fr = int(fr.split ('fr')[1])
				frames.append (fr)
			frames = list(set(frames))
			frames.sort()

			# Key
			for fr in frames:
				for attr in attrs:
					fr1 = attr.split ('_')[1]
					fr1 = int(fr1.split ('fr')[1])
					if fr1 == fr:
						cmds.setKeyframe (geo, at = attr, time = [fr,fr], itt = 'linear', ott = 'linear', v = 1)
					else:
						cmds.setKeyframe (geo, at = attr, time = [fr,fr], itt = 'linear', ott = 'linear', v = 0)
					cmds.keyframe (geo, at = attr, e = 1, tds = 1)
					cmds.keyTangent (geo, at = attr, itt = 'linear', ott = 'linear')

			cf = cmds.currentTime (q = 1)
			cmds.currentTime (cf-1, u = 0)
			cmds.currentTime (cf, u = 0)



### Edit Sculpt
  # Starts a sculpt while saving data that ensures it will be driven by an existing pose attr when applied

def editSculpt_sel (vis = 1, shade = 1):

	sel = cmds.ls (sl = 1)
	if len(sel) == 0:
		cmds.warning ('Select some meshes!')
	elif len(sel) >= 1:
		bads = []
		for g in sel:
			if g.endswith ('_scu'):
				bads.append (g)
		if not bads:
			scus = []
			attrs = cmds.channelBox ('mainChannelBox', q = 1, sma = 1)
			if attrs:
				attr = attrs[0]
				if len(attrs) != 1:
					cmds.warning ('Select a sculpt in the channel box.')
				elif not attr.endswith ('_scu'):
					cmds.warning ('Select a standard sculpt in the channel box. P2P poses are not supported since they are automatically driven and editing would provide the same result as just adding a new P2P sculpt on the same frame.')
				else:
					for geo in sel:
						scu = editSculpt (geo, vis = 1, shade = 1)
						scus.append (scu)
					cmds.select (scus)
				if len(scus) >= 2:
					sys.stdout.write ("Sculpting multiple meshes.")
			else:
				cmds.warning ("Select an sculpt in the channel box!")
		else:
			cmds.warning ("Can't sculpt a sculpt!")

def editSculpt (geo, vis = 1, shade = 1):

	attrs = cmds.channelBox ('mainChannelBox', q = 1, sma = 1)
	if attrs:
		attr = attrs[0]
		if len(attrs) != 1:
			cmds.warning ('Select a sculpt in the channel box.')
		elif not attr.endswith ('_scu') and not attr.endswith ('_p2p'):
			cmds.warning ('Select a sculpt in the channel box.')
		else:
			frame = attr.split ('fr')[1]
			frame = frame.split ('_')[0]
			cmds.currentTime (frame)
			scu = sculpt (geo, vis = 1, shade = 1, editMode = 1)
			return scu
	else:
		cmds.warning ('Select a sculpt in the channel box.')

def applyEdit_sel (lv = 1, ihi = 1):

	sel = cmds.ls (sl = 1)
	if len(sel) == 0:
		cmds.warning ('Select some edit sculpt geo!')
	elif len(sel) >= 1:
		bads = []
		for g in sel:
			if not g.endswith ('_scu'):
				bads.append (g)
			elif not cmds.objExists ('{}.editDriver'.format (g)):
				bads.append (g)
		if not bads:
			geos = []
			for scu in sel:
				drv = cmds.getAttr ('{}.editDriver'.format (scu))
				geo = cmds.getAttr ('{}.origGeo'.format (scu))
				geos.append (geo)
				applyEdit (geo, scu, drv, lv = lv, ihi = ihi)
			cmds.select (geos)
			if len(geos) >= 2:
				sys.stdout.write ("Applied multiple meshes as edited sculpts.")
		else:
			cmds.warning ("You can only apply edit sculpts!")
	else:
		cmds.warning ("You can only apply edit sculpts!")

def applyEdit (geo, scu, drv, lv = 1, ihi = 1):

	if cmds.objExists ('{}.{}'.format (geo,drv)):

		drvn = apply (scu, 'standard', lv = lv, ihi = ihi)
		if 'p2p' not in drv:
			cmds.connectAttr ('{}.{}'.format (geo,drv), '{}.{}'.format (geo,drvn))
		else:
			level = drv.split ('lv')[1]
			level = level.split ('_')[0]
			env = 'p2pLv{}Envelope'.format (level)
			cons = cmds.listConnections ('{}.{}'.format (geo,env))
			for c in cons:
				if c.endswith ('mult'):
					mult = c
					break
			cmds.connectAttr ('{}.outputX'.format (mult), '{}.{}'.format (geo,drvn))
		nn = cmds.attributeName ('{}.{}'.format (geo,drvn), nice = 1)
		cmds.addAttr ('{}.{}'.format (geo,drvn), e = 1, nn = '(EDIT^)  {}'.format (nn))
		#cmds.setAttr ('{}.{}'.format (geo,drvn), k = 0)

	else:
		cmds.warning ("You can only apply edit sculpts!")



#############################
### Optional Dedicated UI ###
#############################



def ui ():

	# Define
	win = 'sculptPose'
	width = 250
	height = 10
	bWidth = width
	bHeight = 35
	bHeight2 = bHeight * .6
	bColor_green = [0.670,0.736,0.602]
	bColor_blue = [0.571,0.676,0.778]
	bColor_purple = [0.691,0.604,0.756]
	bColor_red = [0.765,0.525,0.549]
	bColor_brown = [0.804,0.732,0.646]
	if (cmds.window (win, exists = 1)):
		cmds.deleteUI (win)
	cmds.window (win, rtf = 1, t = 'Sculpt Pose', s = 1, w = width)

	# Buttons
	cmds.columnLayout (adj = 1, rs = 3)
	cmds.separator (h = 1, style = 'none')
	cmds.iconTextButton (l = '                        Sculpt', i = 'putty.png', bgc = bColor_green, ann = 'Duplicate selected geo for sculpting.', st = 'iconAndTextHorizontal', w = bWidth, h = bHeight, c = 'import sculptPose ; reload(sculptPose) ; sculptPose.ui_sculpt ()')
	cmds.button (l = 'Sculpt From Zero', bgc = bColor_green, ann = 'Duplicate selected geo for sculpting, with all existing sculpt deformation removed.', w = bWidth, h = bHeight2, c = 'import sculptPose ; reload (sculptPose) ; sculptPose.ui_sculptFromZero ()')
	cmds.separator (h = 6, style = 'double')
	cmds.iconTextButton (l = '                 Apply Standard', bgc = bColor_blue, i = 'nurbsToPolygons.png', st = 'iconAndTextHorizontal', ann = 'Apply selected sculpt as a standard shape.', h = bHeight, c = 'import sculptPose ; reload(sculptPose) ; sculptPose.ui_apply ()')
	cmds.button (l = 'Apply Standard 1-Frame', bgc = bColor_blue, ann = 'Apply selected sculpt as a standard shape keyed 0-1-0 around current frame.', h = bHeight2, c = 'import sculptPose ; reload(sculptPose) ; sculptPose.ui_apply_1f ()')
	cmds.separator (h = 6, style = 'double')
	cmds.iconTextButton (l = '             Apply Pose-To-Pose', bgc = bColor_purple, i = 'setKeyOnAnim.png', st = 'iconAndTextHorizontal', ann = 'Apply selected sculpt as a Pose-To-Pose shape, automatically keying in and out of existing P2P shapes.', h = bHeight, c = 'import sculptPose ; reload(sculptPose) ; sculptPose.ui_apply_p2p ()')
	cmds.button (l = 'Create P2P Zero', bgc = bColor_purple, ann = 'Skipping the sculpt step, create a P2P shape with no sculpt deformation.', w = (bWidth/2), h = bHeight2, c = 'import sculptPose ; reload(sculptPose) ; sculptPose.ui_createP2PZero ()')
	cmds.button (l = 'Create P2P Hold', bgc = bColor_purple, ann = 'Skipping the sculpt step, create a P2P shape with the deformation of the previous P2P sculpt.', w = (bWidth/2), h = bHeight2, c = 'import sculptPose ; reload(sculptPose) ; sculptPose.ui_createP2PHold ()')
	cmds.separator (h = 6, style = 'double')
	cmds.rowColumnLayout (nc = 2, rs = [2,3], cs = [2,3])
	cmds.button (l = 'Delete CB Sel', bgc = bColor_red, ann = 'Deletes shapes and releated nodes based on channel box selection.', w = (bWidth/2), h = bHeight2, c = 'import sculptPose ; reload(sculptPose) ; sculptPose.ui_delete (allP2P = 0)')
	cmds.button (l = 'Delete All P2P', bgc = bColor_red, ann = 'Deletes entire Pose-To-Pose System.', w = (bWidth/2), h = bHeight2, c = "import sculptPose ; reload(sculptPose) ; sculptPose.ui_delete (allP2P = 1)")
	cmds.setParent ('..')
	cmds.separator (h = 6, style = 'double')
	cmds.rowColumnLayout (nc = 2, rs = [2,3], cs = [2,3])
	cmds.button (l = 'Edit Sculpt', bgc = bColor_brown, ann = 'Start a sculpt that will be automatically driven by the selected sculpt in the channel box.', w = bWidth/2, h = bHeight2, c = 'import sculptPose ; reload(sculptPose) ; sculptPose.ui_editSculpt ()')
	cmds.button (l = 'Apply Edit', bgc = bColor_brown, ann = 'Apply the edited sculpt.', w = bWidth/2, h = bHeight2, c = 'import sculptPose ; reload(sculptPose) ; sculptPose.ui_applyEdit ()')
	cmds.setParent ('..')
	cmds.button (l = 'Sort Channel Box', bgc = bColor_brown, h = bHeight2, ann = "If you used undo after hitting one of the delete buttons, you may need to sort the channel box with this button.", c = "import sculptPose ; reload (sculptPose) ; sculptPose.sortCB ()")
	cmds.separator (h = 6, style = 'double')

	# Options
	cmds.rowColumnLayout (nc = 4, rs = [4,5], cs = [4,3])
	cmds.text (l = '', w = 5)
	cmds.checkBox ('jssp_scuVis_cb', l = 'Vis Toggle  ', v = 1, ann = 'Automatically toggles visibility between original geo and duplicated sculpts.')
	cmds.checkBox ('jssp_scuReshade_cb', l = 'Re-Shade ', v = 1, ann = 'Applies a shiny blue shader to duplicated sculpt geo so they are easily recognized.')
	cmds.checkBox ('jssp_scuData_cb', l = 'Hide Data', v = 1, ann = 'Prevents data nodes from cluttering up the outliner, channel box, and attribute editor. You can still find them through the node editor.')
	cmds.setParent ('..')
	cmds.separator (h = 1, style = 'none')
	cmds.rowColumnLayout (nc = 3, rs = [3,3], cs = [3,3])
	cmds.text (l = '  P2P Level: ', ann = 'When creating P2P sculpts, the automatic keyframing process will only be affected by P2P sculpts of the same level.')
	cmds.intField ('jssp_scuLevel_if', v = 1, min = 1, w = 40, ann = 'When creating P2P sculpts, the automatic keyframing process will only be affected by P2P sculpts of the same level.')
	cmds.optionMenu ('jssp_sfz_om', l = '   SFZ:', w = 145, ann = 'Choose which sculpts get zeroed out when using Sculpt From Zero.')
	cmds.menuItem ('jssp_sfz1_mi', l = 'All Sculpts')
	cmds.menuItem ('jssp_sfz2_mi', l = 'Standard')
	cmds.menuItem ('jssp_sfz3_mi', l = 'P2P')
	cmds.menuItem ('jssp_sfz4_mi', l = 'Current P2P Level')
	cmds.setParent ('..')
	cmds.separator (h = 1, style = 'none')

	# Launch
	cmds.showWindow (win)
	cmds.window (win, e = 1, w = width, h = height)



def ui_sculpt ():

	vis = cmds.checkBox ('jssp_scuVis_cb', q = 1, v = 1)
	shade = cmds.checkBox ('jssp_scuReshade_cb', q = 1, v = 1)
	sculpt_sel (vis = vis, shade = shade)



def ui_sculptFromZero ():

	mode = cmds.optionMenu ('jssp_sfz_om', q = 1, sl = 1)
	vis = cmds.checkBox ('jssp_scuVis_cb', q = 1, v = 1)
	shade = cmds.checkBox ('jssp_scuReshade_cb', q = 1, v = 1)
	lv = cmds.intField ('jssp_scuLevel_if', q = 1, v = 1)
	sculptFromZero_sel (vis = vis, shade = shade, lv = lv, mode = mode)



def ui_apply ():

	ihi = cmds.checkBox ('jssp_scuData_cb', q = 1, v = 1)
	lv = cmds.intField ('jssp_scuLevel_if', q = 1, v = 1)
	apply_sel ('standard', lv = lv, ihi = ihi)



def ui_apply_1f ():

	apply_1f_sel ()



def ui_apply_p2p ():

	lv = cmds.intField ('jssp_scuLevel_if', q = 1, v = 1)
	ihi = cmds.checkBox ('jssp_scuData_cb', q = 1, v = 1)
	apply_p2p_sel (lv = lv, ihi = lv)



def ui_createP2PZero ():

	lv = cmds.intField ('jssp_scuLevel_if', q = 1, v = 1)
	createP2PZero_sel (lv)



def ui_createP2PHold ():

	lv = cmds.intField ('jssp_scuLevel_if', q = 1, v = 1)
	ihi = cmds.checkBox ('jssp_scuData_cb', q = 1, v = 1)
	createP2PHold_sel (lv = lv, ihi = ihi)



def ui_delete (allP2P = 0):

	lv = cmds.intField ('jssp_scuLevel_if', q = 1, v = 1)
	delete_sel (lv, allP2P = allP2P)



def ui_editSculpt ():

	vis = cmds.checkBox ('jssp_scuVis_cb', q = 1, v = 1)
	shade = cmds.checkBox ('jssp_scuReshade_cb', q = 1, v = 1)
	editSculpt_sel (vis = 1, shade = 1)



def ui_applyEdit ():

	vis = cmds.checkBox ('jssp_scuVis_cb', q = 1, v = 1)
	shade = cmds.checkBox ('jssp_scuReshade_cb', q = 1, v = 1)
	ihi = cmds.checkBox ('jssp_scuData_cb', q = 1, v = 1)
	lv = cmds.intField ('jssp_scuLevel_if', q = 1, v = 1)
	applyEdit_sel (lv = lv, ihi = ihi)



def selectSculpts ():

	cmds.select ('*_scu')