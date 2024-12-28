'''

Copyright Frigging Awesome Studios
friggingawesomestudios@gmail.com
http://www.friggingawesome.com

Run with:

import animPolish.quickBake as quickBake
from importlib import reload
reload (quickBake)
quickBake.run ()

'''



from __future__ import absolute_import
try:
	from importlib import reload
except:
	pass

import maya.cmds as cmds
import maya.mel as mel
import sys
import animPolish.rivetStuff as rivetStuff
reload (rivetStuff)



def run_sel ():

	sel = cmds.ls (sl = 1)
	if sel:
		nt = cmds.nodeType (sel[0])
		if nt == 'transform':
			run (sel)
		else:
			cmds.warning ('Select some meshes!')
	else:
		cmds.warning ('Select some meshes!')



def run (objs):

	cmds.refresh (su = 1)
	st = cmds.playbackOptions (q = 1, min = 1)
	end = cmds.playbackOptions (q = 1, max = 1)
	cmds.bakeResults (objs, sm = 1, t = (st,end))
	cmds.refresh (su = 0)
	sys.stdout.write ("Baked geo!")



def rivet_sel ():

	sel = cmds.ls (sl = 1)
	if sel:
		if len(sel) == 1:
			vtx = sel[0]
			if '.vtx[' in vtx:
				rivet ()
			else:
				cmds.warning ('Select 1 vertex.')
		else:
			cmds.warning ('Select 1 vertex.')
	else:
		cmds.warning ('Select 1 vertex.')



def rivet ():

	riv = rivetStuff.rivet_sel (loc = 1)
	loc = cmds.spaceLocator ()[0]
	cnst = cmds.parentConstraint (riv, loc)
	run (loc)
	cmds.delete (cnst)
	cmds.delete (riv)
	ren = cmds.rename (loc, riv)
	sys.stdout.write ("Baked rivet!")
	return ren



def plane_sel ():

	sel = cmds.ls (sl = 1)
	if sel:
		if len(sel) == 1:
			vtx = sel[0]
			if '.vtx[' in vtx:
				plane ()
			else:
				cmds.warning ('Select 1 vertex.')
		else:
			cmds.warning ('Select 1 vertex.')
	else:
		cmds.warning ('Select 1 vertex.')



def plane ():

	riv = rivetStuff.rivet_sel (loc = 1)
	plane = cmds.polyPlane (sx = 1, sy = 1, ch = 0)[0]
	cnst = cmds.parentConstraint (riv, plane)
	run (plane)
	cmds.delete (cnst)
	cmds.delete (riv)
	ren = cmds.rename (plane, riv.replace ('_RIV','_POL'))
	return ren
	sys.stdout.write ("Baked plane!")