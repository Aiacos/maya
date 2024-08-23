'''

Copyright Frigging Awesome Studios
friggingawesomestudios@gmail.com
http://www.friggingawesome.com

Select 1 vertex and run with:

import animPolish.copyPasteAttrs as copyPasteAttrs
reload (copyPasteAttrs)
copyPasteAttrs.func ()

'''



from __future__ import absolute_import
try:
	from importlib import reload
except:
	pass

import maya.cmds as cmds
import maya.mel as mel
import sys
import animPolish as jsap
reload (jsap)



def copy (path = '', k = 0):

	sel = cmds.ls (sl = 1, l = 1)
	if sel:
		if len(sel) == 1:

			if path:
				if not path.endswith ('/'):
					root = '{}/'.format (path)
			else:
				root = jsap.__file__
				root = root.replace ('__init__.py', '')
			path = '{}user_copyPasteAttrs.py'.format (root)
			i = sel[0]
			
			f = open (path, 'w')
			f.write ("import maya.cmds as cmds\n\n")

			f.write ("sel = cmds.ls (sl = 1)\n")
			f.write ("if sel:\n")
			f.write ("    for i in sel:\n\n")
			if k == 1:
				attrs = cmds.listAttr (i, k = 1)
			elif k == 0:
				attrs = cmds.listAttr (i)
			for a in attrs:
				try:
					val = cmds.getAttr ('{}.{}'.format (i,a))
					f.write ("        try:\n")
					f.write ("            cmds.setAttr ('{}.{}'.format (i), {})\n".format ('{}',a,val))
					f.write ("        except:\n")
					f.write ("            pass\n\n")
				except:
					pass

			f.close ()
			sys.stdout.write ("Copied attributes to '{}'".format (path))

		else:
			cmds.warning ("Select 1 object!")
	else:
		cmds.warning ("Select 1 object!")



def paste (path = ''):
	
	sel = cmds.ls (sl = 1, l = 1)
	if sel:
		if path:
			if not path.endswith ('/'):
				root = '{}/'.format (path)
		else:
			root = jsap.__file__
			root = root.replace ('__init__.py', '')
		path = '{}user_copyPasteAttrs.py'.format (root)
		try:
			exec(compile(open(path, "rb").read(), path, 'exec'))
		except:
			cmds.warning ("Couldn't find file...")
		sys.stdout.write ("Pasted attributes from '{}'".format (path))
	else:
		cmds.warning ("Select some objects!")