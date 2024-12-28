'''

Copyright Frigging Awesome Studios
friggingawesomestudios@gmail.com
http://www.friggingawesome.com

Run with:

import animPolish.smoothPreview as smoothPreview
from importlib import reload
reload (smoothPreview)
smoothPreview.run ()

'''



from __future__ import absolute_import
try:
	from importlib import reload
except:
	pass

import maya.cmds as cmds
import maya.mel as mel
import sys



def run (div = 2):

	sel = cmds.ls (sl = 1)
	if sel:

		# Check top levels
		meshes = []
		for top in sel:
			shps = cmds.listRelatives (top, s = 1, f = 1)
			if shps:
				nt = cmds.nodeType (shps[0])
				if nt == 'mesh' and 'Orig' not in shps[0]:
					meshes.append (shps[0])

			# Get descendants
			kids = cmds.listRelatives (top, ad = 1, type = 'transform', f = 1)
			if kids:
				for i in kids:
					shps = cmds.listRelatives (i, s = 1, f = 1)
					if shps:
						for shp in shps:
							nt = cmds.nodeType (shp)
							if nt == 'mesh' and 'Orig' not in shps:
								meshes.append (shp)

		# Smooth
		for i in meshes:
			try:
				cmds.setAttr ('{}.displaySmoothMesh'.format (i), 2)
				#cmds.setAttr ('{}.useGlobalSmoothDrawType'.format (i), 0)
				#cmds.setAttr ('{}.smoothDrawType'.format (i), 0)
				cmds.setAttr ('{}.smoothLevel'.format (i), div)
			except:
				pass