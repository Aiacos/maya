'''

Copyright Frigging Awesome Studios
friggingawesomestudios@gmail.com
http://www.friggingawesome.com

Run with:

import animPolish.cycleCam as cycleCam
reload (cycleCam)
cycleCam.run()

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

def run (skipOrtho = 0):

	# Get camera shapes in scene
	camShps1 = cmds.ls (type = 'camera')
	camShps = []
	if skipOrtho == 1:
		for c in camShps1:
			if not c.startswith ('top') and not c.startswith ('front') and not c.startswith ('side') and not c.startswith ('bottom') and not c.startswith ('left') and not c.startswith ('right'):
				camShps.append (c)
	else:
		camShps = camShps1

	# Get camera transforms
	cams = []
	for c in camShps:
		par = cmds.listRelatives (c, p = 1, f = 1)[0]
		cams.append (par)

	# Check current panel and run
	panel = cmds.getPanel (wf = 1)
	if 'modelPanel' in panel:
		cur = cmds.modelPanel (panel, q = 1, cam = 1)
		cur = cmds.ls (cur, l = 1)[0]
		print(cur)
		print(cams)
		try:
			curIdx = cams.index (cur)
			print(curIdx)
		except:
			curIdx = 0
		if cur == cams[-1]:
			cmds.lookThru (camShps[0])
			sys.stdout.write ("Looking through '{}'\n".format (cams[0]))
		else:
			try:
				cmds.lookThru (camShps[curIdx+1])
				sys.stdout.write ("Looking through '{}'\n".format (cams[curIdx+1]))
			except:
				cmds.lookThru (camShps[0])
				sys.stdout.write ("Looking through '{}'\n".format (cams[0]))
	
	else:
		cmds.warning ('No active viewport found. Click the gray area above it to make it active.')