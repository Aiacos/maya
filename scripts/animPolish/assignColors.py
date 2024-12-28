'''

Copyright Frigging Awesome Studios
friggingawesomestudios@gmail.com
http://www.friggingawesome.com

Run with:

import animPolish.assignColors as assignColors
reload (assignColors)
assignColors.func()

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



def createMats ():

	createMat ('red', [1.0, 0.215599998832, 0.215599998832])
	createMat ('orange', [1.0, 0.414999991655, 0.215599998832])
	createMat ('yellow', [1.0, 0.725199997425, 0.097999997437])
	createMat ('yellowGreen', [0.772899985313, 1.0, 0.215599998832])
	createMat ('green', [0.168899998069, 0.627399981022, 0.159899994731])
	createMat ('teal', [0.215599998832, 1.0, 0.551699995995])
	createMat ('lightBlue', [0.215599998832, 0.703299999237, 1.0])
	createMat ('blue', [0.137199997902, 0.352899998426, 1.0])
	createMat ('purple', [0.433899998665, 0.215599998832, 1.0])
	createMat ('lightPink', [0.996299982071, 0.588199973106, 1.0])
	createMat ('hotPink', [0.993099987507, 0.215599998832, 1.0])
	createMat ('gray', [.5, .5, .5])
	createMat ('black', [0.1, 0.1, 0.1])
	createMat ('white', [1.0, 1.0, 1.0])



def createMat (name, color):

	matB = 'jsap_{}_blinn_MAT'.format (name)
	matL = 'jsap_{}_lambert_MAT'.format (name)
	if not cmds.objExists (matB):
		cmds.shadingNode ('blinn', n = matB, asShader = 1)
		cmds.setAttr ('{}.color'.format (matB), color[0], color[1], color[2], type = 'double3')
		cmds.setAttr ('{}.specularColor'.format (matB), .254438, .254438, .254438, type = 'double3')
		cmds.setAttr ('{}.eccentricity'.format (matB), .556157)
	if not cmds.objExists (matL):
		cmds.shadingNode ('lambert', n = matL, asShader = 1)
		cmds.setAttr ('{}.color'.format (matL), color[0], color[1], color[2], type = 'double3')



def assign_sel (color, mode):

	sel = cmds.ls (sl = 1)
	if sel:
		for i in sel:
			try:
				assign (i, color, mode)
			except:
				pass
		cmds.select (sel)
	else:
		cmds.warning ('Select some meshes!')


def assign (obj, color, mode):

	createMats ()
	cmds.select (obj)
	cmds.hyperShade (assign = 'jsap_{}_{}_MAT'.format (color,mode))



def random_sel (mode):

	sel = cmds.ls (sl = 1)
	if sel:
		for i in sel:
			try:
				random (i, mode)
			except:
				pass
		cmds.select (sel)
	else:
		cmds.warning ('Select some meshes!')

def random (obj, mode):

	import random
	colors = ['red','orange','yellow','yellowGreen','green','teal','lightBlue','blue','purple','lightPink','hotPink']
	color = random.choice (colors)
	assign (obj, color, mode)



def printColor_sel ():

	sel = cmds.ls (sl = 1)
	if sel:
		printColor (sel[0])



def printColor (mat):

	get = cmds.getAttr ('{}.color'.format (mat))
	get = str(get).replace ('[', '')
	get = get.replace (']', '')
	exec ('getList = {}'.format (get))
	print('[{}, {}, {}]'.format (getList[0],getList[1],getList[2]))