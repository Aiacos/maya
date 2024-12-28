'''

Copyright Frigging Awesome Studios
friggingawesomestudios@gmail.com
http://www.friggingawesome.com

Run with:

import animPolish.ui as ui
try:
	from importlib import reload
except:
	pass
reload (ui)
ui.ui (dock = 1)

Or if you get display issues such as double buttons, or just want to launch undocked:

import animPolish.ui as ui
try:
	from importlib import reload
except:
	pass
reload (ui)
ui.ui (dock = 0)


'''



from __future__ import absolute_import
try:
	from importlib import reload
except:
	pass

import maya.cmds as cmds
import maya.mel as mel
import sys
import os
import imp
import animPolish.sculptPose as sculptPose
import animPolish.wrap as wrap
import animPolish.assignColors as assignColors
import animPolish.growShrink as growShrink
import animPolish.iron as iron
import animPolish.subdue as subdue
import animPolish.caching as caching
import animPolish.rivetStuff as rivetStuff
import animPolish as jsap
try:
	from six.moves import range
except:
	pass
reload (rivetStuff)
reload (sculptPose)
reload (wrap)
reload (assignColors)
reload (growShrink)
reload (iron)
reload (subdue)
reload (caching)
reload (jsap)



#############################
### Custom Data Directory ###
#############################

'''

If multiple users run AnimPolish from a shared directory, you might want to fill in the
custom "user_data_directory" variable. I'd recommend writing some custom code above it
to query the current user and concatenate a final path. If you don't, the "Save/Load
Settings" and "Copy/Paste Attrs" tools will end up overwriting eachother between users.

'''

user_data_directory = ''



##########
### UI ###
##########



def ui (dock = 1):

	# Define
	win = 'animPolish'
	dockUI = 'animPolish_dock'
	width = 275
	height = 875
	bWidth = width - 37
	bHeight = 35
	bHeight2 = bHeight * .6
	bColor_green = [0.670,0.736,0.602]
	bColor_blue = [0.571,0.676,0.778]
	bColor_purple = [0.691,0.604,0.756]
	bColor_red = [0.765,0.525,0.549]
	bColor_brown = [0.804,0.732,0.646]
	if (cmds.window (win, exists = 1)):
		cmds.deleteUI (win)
	if (cmds.dockControl (dockUI, exists = 1)):
		cmds.deleteUI (dockUI)
	cmds.window (win, rtf = 1, t = 'AnimPolish', s = 1, w = width+20, menuBar = 1)

	# File menu
	cmds.menu (l = 'General', tearOff = 1)
	cmds.menuItem (l = 'Toggle DG/Parallel', c = 'import animPolish.ui as ui ; reload(ui) ; ui.toggleAnimEval ()', ann = "Some of these tools function more predictably in the 'DG' animation evaluation mode.")
	cmds.menuItem (l = 'Save Settings', c = 'import animPolish.ui as ui ; reload(ui) ; ui.saveSettings ()', ann = "Saves current AnimPolish UI settings so that they remain the same when you re-open it later.")
	cmds.menuItem (l = 'Default Settings', c = 'import animPolish.ui as ui ; reload(ui) ; ui.defaultSettings ()', ann = 'Resets default UI settings.')
	cmds.menu (l = 'Help', tearOff = 1)
	cmds.menuItem (l = 'Documentation', c = "import webbrowser ; webbrowser.open('https://docs.google.com/document/d/1wZ9YK99o3FRZpzjEoPXzcpPmpGOSfbl__VPGC60qM4Y/edit?usp=sharing')", ann = 'Detailed instructions for each tool.')
	cmds.menuItem (l = 'Contact', c = "import webbrowser ; webbrowser.open('https://www.friggingawesome.com/support')", ann = 'Email about bugs and such.')
	cmds.menu (l = 'Extra', tearOff = 1)
	cmds.menuItem (l = 'Download Sticky Mod', c = "import webbrowser ; webbrowser.open('https://gum.co/sticky-mod')", ann = 'Ride-along soft mod for quick deformation adjustments.')
	cmds.columnLayout (adj = 1, rs = 3, w = width)
	cmds.separator (h = 7, style = 'none', w = width+20)
	cmds.text (l = "AnimPolish v1.23", font = 'boldLabelFont')
	cmds.setParent ('..')

	try:
		cmds.scrollLayout ('jsap_scroll', vsb = 1, w = width+20)
	except:
		cmds.scrollLayout ('jsap_scroll')

	'''
	cmds.frameLayout ('jsap_general_fl', l = 'General', cll = 1, cl = 1, mh = 8, mw = 15, w = width)
	cmds.columnLayout (adj = 1, rs = 3)
	cmds.iconTextButton (l = '                Toggle DG/Parallel', i = 'bufferSwap.png', bgc = bColor_green, st = 'iconAndTextHorizontal', ann = "Some of these tools function more predictably in the 'DG' animation evaluation mode.", h = bHeight2, c = "import animPolish.ui as ui ; reload(ui) ; ui.toggleAnimEval ()")
	cmds.iconTextButton (l = '                     Save Settings', i = 'fileSave.png', bgc = bColor_blue, st = 'iconAndTextHorizontal', ann = "Saves current AnimPolish UI settings so that they remain the same when you re-open it later.", h = bHeight2, c = "import animPolish.ui as ui ; reload(ui) ; ui.saveSettings ()")
	cmds.iconTextButton (l = '                   Default Settings', i = 'undo_s.png', bgc = bColor_blue, st = 'iconAndTextHorizontal', ann = "Resets default UI settings.", h = bHeight2, c = "import animPolish.ui as ui ; reload(ui) ; ui.defaultSettings ()")
	cmds.separator (h = 6, style = 'double')
	cmds.iconTextButton (l = '             Download Sticky Mod', i = 'moveLayerDown.png', bgc = bColor_brown, ann = 'Ride-along soft mod for quick deformation adjustments.', st = 'iconAndTextHorizontal', h = bHeight2, c = "import webbrowser ; webbrowser.open('https://gum.co/sticky-mod')")
	cmds.iconTextButton (l = '                   Documentation', i = 'help.png', bgc = bColor_brown, ann = 'Detailed instructions for each tool.', st = 'iconAndTextHorizontal', h = bHeight2, c = "import webbrowser ; webbrowser.open('https://friggingawesome.plexie.com/app/#/public/project/d732c559-ae3a-4271-aeb4-0e941628b9ff')")
	cmds.iconTextButton (l = '                         Contact', i = 'fileTextureEdit.png', bgc = bColor_brown, ann = 'Email about bugs and such.', st = 'iconAndTextHorizontal', h = bHeight2, c = "import webbrowser ; webbrowser.open('https://www.friggingawesome.com/support')")
	cmds.separator (h = 6, st = 'none')
	cmds.setParent ('..')
	cmds.setParent ('..')
	cmds.setParent ('..')
	'''

	# Sculpt
	cmds.frameLayout ('jsap_sculptPose_fl', l = 'Sculpt', cll = 1, cl = 0, mh = 8, mw = 15, w = width, ann = "Animate custom geo sculpts over time.")
	cmds.columnLayout (adj = 1, rs = 3)
	cmds.iconTextButton (l = '                      Sculpt', i = 'putty.png', bgc = bColor_green, ann = 'Duplicate selected geo for sculpting.', st = 'iconAndTextHorizontal', w = bWidth, h = bHeight, c = 'import animPolish.ui as ui ; reload(ui) ; ui.scu_sculpt ()')
	cmds.button (l = 'Sculpt From Zero', bgc = bColor_green, ann = 'Duplicate selected geo for sculpting, with all existing sculpt deformation removed.', w = bWidth, h = bHeight2, c = 'import animPolish.ui as ui ; reload (ui) ; ui.scu_sculptFromZero ()')
	cmds.button (l = 'Abort Sculpt', bgc = bColor_red, ann = 'Delete selected WIP sculpts.', w = bWidth, h = bHeight2, c = 'import animPolish.ui as ui ; reload (ui) ; ui.scu_abortSculpt ()')
	cmds.separator (h = 6, style = 'double')
	cmds.iconTextButton (l = '               Apply Standard', bgc = bColor_blue, i = 'nurbsToPolygons.png', st = 'iconAndTextHorizontal', ann = 'Apply selected sculpt as a standard shape.', h = bHeight, c = 'import animPolish.ui as ui ; reload(ui) ; ui.scu_apply ()')
	cmds.button (l = 'Apply Standard 1-Frame', bgc = bColor_blue, ann = 'Apply selected sculpt mesh as a standard sculpt keyed 0-1-0 around current frame.', h = bHeight2, c = 'import animPolish.ui as ui ; reload(ui) ; ui.scu_apply_1f ()')
	cmds.separator (h = 6, style = 'double')
	cmds.iconTextButton (l = '           Apply Pose-To-Pose', bgc = bColor_purple, i = 'setKeyOnAnim.png', st = 'iconAndTextHorizontal', ann = 'Apply selected sculpt mesh as a Pose-To-Pose sculpt, automatically keying in and out of existing P2P shapes.', h = bHeight, c = 'import animPolish.ui as ui ; reload(ui) ; ui.scu_apply_p2p ()')
	cmds.button (l = 'Create P2P Zero', bgc = bColor_purple, ann = 'Skipping the sculpt step, create a P2P sculpt with no sculpt deformation.', w = (bWidth/2), h = bHeight2, c = 'import animPolish.ui as ui ; reload(ui) ; ui.scu_createP2PZero ()')
	cmds.button (l = 'Create P2P Hold', bgc = bColor_purple, ann = 'Skipping the sculpt step, create a P2P sculpt with the deformation of the previous P2P sculpt.', w = (bWidth/2), h = bHeight2, c = 'import animPolish.ui as ui ; reload(ui) ; ui.scu_createP2PHold ()')
	cmds.separator (h = 6, style = 'double')
	cmds.rowColumnLayout (nc = 2, rs = [2,3], cs = [2,3])
	cmds.button (l = 'Delete CB Sel', bgc = bColor_red, ann = 'Deletes shapes and releated nodes based on channel box selection.', w = (bWidth/2), h = bHeight2, c = 'import animPolish.ui as ui ; reload(ui) ; ui.scu_delete (allP2P = 0)')
	cmds.button (l = 'Delete All P2P', bgc = bColor_red, ann = 'Deletes entire Pose-To-Pose System.', w = (bWidth/2), h = bHeight2, c = "import animPolish.ui as ui ; reload(ui) ; ui.scu_delete (allP2P = 1)")
	cmds.setParent ('..')
	cmds.separator (h = 6, style = 'double')
	cmds.rowColumnLayout (nc = 2, rs = [2,3], cs = [2,3])
	cmds.button (l = 'Edit Sculpt', bgc = bColor_brown, ann = 'Start sculpting a sculpt that will be automatically driven by the selected sculpt in the channel box.', w = bWidth/2, h = bHeight2, c = 'import animPolish.ui as ui ; reload(ui) ; ui.scu_editSculpt ()')
	cmds.button (l = 'Apply Edit', bgc = bColor_brown, ann = 'Apply the edited sculpt mesh.', w = bWidth/2, h = bHeight2, c = 'import animPolish.ui as ui ; reload(ui) ; ui.scu_applyEdit ()')
	cmds.setParent ('..')
	cmds.button (l = 'Select Active Sculpts', bgc = bColor_brown, h = bHeight2, ann = "Selects all objects that end in '_scu'", c = "import animPolish.sculptPose as sculptPose ; reload (sculptPose) ; sculptPose.selectSculpts ()")
	cmds.button (l = 'Sort Channel Box', bgc = bColor_brown, h = bHeight2, ann = "If you used undo after hitting one of the delete buttons, you may need to sort the channel box with this button.", c = "import animPolish.sculptPose as sculptPose ; reload (sculptPose) ; sculptPose.sortCB ()")
	cmds.separator (h = 6, style = 'double')
	cmds.rowColumnLayout (nc = 3, rs = [3,5], cs = [3,3])
	cmds.checkBox ('jsap_scuVis_cb', l = 'Vis Toggle  ', v = 1, ann = 'Automatically toggles visibility between original geo and duplicated sculpts.')
	cmds.checkBox ('jsap_scuReshade_cb', l = 'Re-Shade ', v = 1, ann = 'Applies a shiny blue shader to duplicated sculpt geo so they are easily recognized.')
	cmds.checkBox ('jsap_scuData_cb', l = 'Hide Data', v = 1, ann = 'Prevents data nodes from cluttering up the outliner, channel box, and attribute editor. You can still find them through the node editor.')
	cmds.setParent ('..')
	cmds.separator (h = 1, style = 'none')
	cmds.rowColumnLayout (nc = 3, rs = [3,3], cs = [3,3])
	cmds.text (l = 'P2P Level: ', ann = 'When creating P2P sculpts, the automatic keyframing process will only be affected by P2P sculpts of the same level.')
	cmds.intField ('jsap_scuLevel_if', v = 1, min = 1, w = 40, ann = 'When creating P2P sculpts, the automatic keyframing process will only be affected by P2P sculpts of the same level.')
	cmds.optionMenu ('jsap_sfz_om', l = '   SFZ:', w = 145, ann = 'Choose which sculpts get zeroed out when using Sculpt From Zero.')
	cmds.menuItem ('jsap_sfz1_mi', l = 'All Sculpts')
	cmds.menuItem ('jsap_sfz2_mi', l = 'Standard')
	cmds.menuItem ('jsap_sfz3_mi', l = 'P2P')
	cmds.menuItem ('jsap_sfz4_mi', l = 'Current P2P Level')
	cmds.setParent ('..')
	cmds.rowColumnLayout (nc = 2, rs = [4,3], cs = [4,3])
	cmds.text (l = 'Prefix:  ')
	cmds.textField ('jsap_scu_prefix_tf', w = 205, h = 24, ann = "If this field is filled, 'Sculpt' will be replaced by this in attribute names for standard sculpts. Channel box names must be set to 'Nice' to see this.", tx = 'Sculpt')
	cmds.setParent ('..')
	cmds.separator (h = 6, st = 'none')
	cmds.setParent ('..')
	cmds.setParent ('..')

	# Wrap
	cmds.frameLayout ('jsap_wrap_fl', l = 'Wrap', cll = 1, cl = 0, mh = 8, mw = 15, w = width, ann = "Wrap geo to other meshes, or lock them in space.")
	cmds.columnLayout (adj = 1, rs = 3)
	cmds.iconTextButton (l = '                Wrap To Mesh', i = 'wrap.png', bgc = bColor_green, ann = 'Utilizing paintable blend shapes, wraps duplicates of meshes in selection to the last mesh in selection.', st = 'iconAndTextHorizontal', h = bHeight, c = 'import animPolish.ui as ui ; reload(ui) ; ui.wrap_wrapToMesh ()')
	cmds.iconTextButton (l = '               Wrap To World', i = 'duplicateCurve.png', bgc = bColor_green, ann = 'Blends duplicates of selected objects frozen in space back to their respective originals.', st = 'iconAndTextHorizontal', h = bHeight, c = 'import animPolish.ui as ui ; reload(ui) ; ui.wrap_wrapToWorld ()')
	cmds.iconTextButton (l = '         Extract Animated Faces', i = 'polyChipOff.png', bgc = bColor_brown, ann = "Duplicates selected faces with animation in-tact. Useful for creating simple surfaces to wrap geo to with the 'Wrap' tool.", st = 'iconAndTextHorizontal', w = bWidth, h = bHeight, c = 'import animPolish.wrap as wrap ; reload (wrap) ; wrap.extractFaces ()')
	cmds.separator (h = 6, style = 'double')
	cmds.rowColumnLayout (nc = 6, rs = [4,3], cs = [4,3])
	cmds.text (l = 'Flood Verts:  ')
	cmds.textField ('jsap_wrap_autoFlood_tf', w = 95, ann = "If this field is filled, any non-loaded verts will be flooded to zero.")
	cmds.text (l = '', w = 1)
	cmds.button (l = 'Load', ann = "Loads selected verts. If the field is filled, any non-loaded verts will be flooded to zero.", c = 'import animPolish.ui as ui ; reload(ui) ; ui.wrap_loadVerts ()')
	cmds.text (l = '', w = 3)
	cmds.button (l = 'Clear', ann = "Clears loaded verts.", c = 'import animPolish.ui as ui ; reload(ui) ; ui.wrap_clearVerts ()')
	cmds.setParent ('..')
	cmds.separator (h = 1, style = 'none')
	cmds.rowColumnLayout (nc = 4, rs = [2,3], cs = [2,3])
	cmds.text (l = '                       Smooth Map: ', ann = "If flooding verts, the map will be smoothed this number of times.")
	cmds.intField ('jsap_wrap_autoSmooth_if', v = 3, min = 0, w = 35, ann = "If flooding verts, the map will be smoothed this number of times.")
	cmds.text (l = '    ')
	#cmds.checkBox ('jsap_wrap_data_cb', l = 'Hide Data', v = 1, ann = 'Prevents data nodes from cluttering up the outliner, channel box, and attribute editor. You can still find them through the node editor.')
	cmds.setParent ('..')
	cmds.separator (h = 6, st = 'none')
	cmds.setParent ('..')
	cmds.setParent ('..')

	# Subdue
	cmds.frameLayout ('jsap_subdue_fl', l = 'Subdue', cll = 1, cl = 0, mh = 8, mw = 15, w = width, ann = "Softens vertex motion over time.")
	cmds.columnLayout (adj = 1, rs = 3)
	cmds.iconTextButton (l = '                    Subdue *', i = 'modifySmooth.png', bgc = bColor_green, ann = "Softens motion over time. Takes a few seconds to apply.\nIf you see a quick error flash, ignore it. If prompted with a pop-up, click 'Auto-Rename'.\nRecommended to save first in case this large calculation crashes your file.\nUndoing is not recommended.", st = 'iconAndTextHorizontal', w = bWidth, h = bHeight, c = 'import animPolish.ui as ui ; reload(ui) ; ui.subdue_run ()')
	cmds.separator (h = 6, style = 'double')
	cmds.rowColumnLayout (nc = 4, rs = [4,3], cs = [4,3])
	cmds.text (l = 'Resample Rate:  ', ann = 'When rebuilding vertex animation curves, a key will be set after skipping this many frames. In other words, setting it to 2 means you are re-building animation on twos, 3 is on threes...')
	cmds.intField ('jsap_subdue_resample_if', v = 4, w = 35, ann = "When rebuilding vertex animation curves, a key will be set after skipping this many frames. In other words, setting it to 2 means you are re-building animation on twos, 3 is on threes...")
	cmds.text (l = '   Smooth Map: ', ann = "If running on selected verts, the map will be inversely flooded to zero and smoothed this number of times.")
	cmds.intField ('jsap_subdue_autoSmooth_if', v = 3, w = 35, ann = "If running on selected verts, the map will be inversely flooded to zero and smoothed this number of times.")
	cmds.setParent ('..')
	cmds.separator (h = 6, st = 'none')
	cmds.setParent ('..')
	cmds.setParent ('..')

	# Grow/Shrink/Iron
	cmds.frameLayout ('jsap_miscDeformation_fl', l = 'Grow/Shrink/Iron', cll = 1, cl = 1, mh = 8, mw = 15, w = width, ann = "Simple deformation tools for growing/shrinking and smoothing.")
	cmds.columnLayout (adj = 1, rs = 3)
	cmds.iconTextButton (l = '                  Grow/Shrink', i = 'Bulge.png', bgc = bColor_green, ann = "Utilizing a duplicated geo with shared input connections, creates a paintable pseudo-deformer that grows/shrinks verts along their normals. * Can cause performance slowdown -- use sparingly. ", st = 'iconAndTextHorizontal', w = bWidth, h = bHeight, c = 'import animPolish.ui as ui ; reload(ui) ; ui.growShrink_run ()')
	cmds.iconTextButton (l = '                         Iron', i = 'Smooth.png', bgc = bColor_green, ann = "Utilizing a duplicated geo with shared input connections, creates a paintable pseudo-deformer that averages vertices. * Can cause performance slowdown -- use sparingly.", st = 'iconAndTextHorizontal', w = bWidth, h = bHeight, c = 'import animPolish.ui as ui ; reload(ui) ; ui.iron_run ()')
	cmds.separator (h = 6, style = 'double')
	cmds.rowColumnLayout (nc = 6, rs = [4,3], cs = [4,3])
	cmds.text (l = 'Flood Verts:  ')
	cmds.textField ('jsap_misc_floodVerts_tf', w = 95, ann = "If this field is filled, only loaded vertices will be deformed. This is unrelated to the selected verts that get flooded to 1 on the paintable map, or smoothed.")
	cmds.text (l = '', w = 1)
	cmds.button (l = 'Load', ann = "Loads selected verts. If the field is filled, any non-loaded verts will be flooded to zero.", c = 'import animPolish.ui as ui ; reload(ui) ; ui.misc_loadFloodVerts ()')
	cmds.text (l = '', w = 3)
	cmds.button (l = 'Clear', ann = "Clears loaded verts.", c = 'import animPolish.ui as ui ; reload(ui) ; ui.misc_clearFloodVerts ()')
	cmds.setParent ('..')
	cmds.rowColumnLayout (nc = 6, rs = [4,3], cs = [4,3])
	cmds.text (l = 'Dfrm Verts:  ')
	cmds.textField ('jsap_misc_dfrmVerts_tf', w = 100, ann = "If this field is filled, only loaded vertices will be deformed. This is unrelated to the selected verts that get flooded to 1 on the paintable map, or smoothed.")
	cmds.text (l = '', w = 1)
	cmds.button (l = 'Load', ann = "Loads selected verts. If the field is filled, any non-loaded verts will be flooded to zero.", c = 'import animPolish.ui as ui ; reload(ui) ; ui.misc_loadDfrmVerts ()')
	cmds.text (l = '', w = 3)
	cmds.button (l = 'Clear', ann = "Clears loaded verts.", c = 'import animPolish.ui as ui ; reload(ui) ; ui.misc_clearDfrmVerts ()')
	cmds.setParent ('..')
	cmds.rowColumnLayout (nc = 4, rs = [4,3], cs = [4,3])
	cmds.text (l = '       Smooth Map:  ', ann = "If running on selected verts, the map will be inversely flooded to zero and smoothed this number of times.")
	cmds.intField ('jsap_misc_autoSmooth_if', v = 3, w = 35, ann = "If running on selected verts, the map will be inversely flooded to zero and smoothed this number of times.")
	cmds.text (l = '    ')
	cmds.checkBox ('jsap_misc_data_cb', l = 'Hide Data', v = 1, ann = 'Prevents data nodes from cluttering up the outliner, channel box, and attribute editor. You can still find them through the node editor.')
	cmds.setParent ('..')
	cmds.separator (h = 6, st = 'none')
	cmds.setParent ('..')
	cmds.setParent ('..')

	# Native Maya
	cmds.frameLayout ('jsap_nativeMaya_fl', l = 'Native Maya', cll = 1, cl = 1, mh = 8, mw = 15, w = width, ann = "Built-in Maya deformers useful for tech anim.")
	cmds.columnLayout (adj = 1, rs = 3)
	cmds.iconTextButton (l = '                  Delta Mush', i = 'Smooth.png', bgc = bColor_blue, ann = "Similar to 'Smooth Geo', but instead of a general smooth, the mesh will always try to return to the vert-to-vert relationship it remembers from the pose the 'Delta Mush' was created in. Recommended to create while in t-pose.", st = 'iconAndTextHorizontal', w = bWidth, h = bHeight, c = 'import animPolish.ui as ui ; reload(ui) ; ui.deltaMush ()')
	cmds.iconTextButton (l = '                   Sine Wave', i = 'waveNLD.png', bgc = bColor_blue, ann = "System to send sine waves through a mesh. Useful for water, wind, and general noise.", st = 'iconAndTextHorizontal', w = bWidth, h = bHeight, c = 'import animPolish.ui as ui ; reload(ui) ; ui.sine ()')
	cmds.iconTextButton (l = '                  Radial Wave', i = 'sineNLD.png', bgc = bColor_blue, ann = "System to send sine waves through a mesh. Useful for water, wind, and general noise.", st = 'iconAndTextHorizontal', w = bWidth, h = bHeight, c = 'import animPolish.ui as ui ; reload(ui) ; ui.wave ()')
	cmds.iconTextButton (l = '                      Cluster', i = 'cluster.png', bgc = bColor_blue, ann = "Basic paintable transform-based deformer.", st = 'iconAndTextHorizontal', w = bWidth, h = bHeight, c = 'import animPolish.ui as ui ; reload(ui) ; ui.cluster ()')
	cmds.separator (h = 6, st = 'none')
	cmds.setParent ('..')
	cmds.setParent ('..')

	# Assign Colors
	cmds.frameLayout ('jsap_assignColors_fl', l = 'Assign Colors', cll = 1, cl = 1, mh = 8, mw = 15, w = width, ann = "Assign lambert and blinn materials of common colors to objects for easy spotting of inter-penetrations, either manually or randomly.")
	cmds.columnLayout (adj = 1, rs = 3)
	cmds.rowColumnLayout (nc = 3, rs = [3,4], cs = ([2,4], [3,4]))
	cmds.button (bgc = [.467,.467,.467], l = '/', w = bWidth/3, h = bHeight2, c = "import animPolish.ui as ui ; reload(ui) ; ui.ac_lambert1 ()")
	cmds.button (bgc = [1.0, 0.215599998832, 0.215599998832], l = 'Red', w = bWidth/3, c = "import animPolish.ui as ui ; reload(ui) ; ui.assignColor ('red')")
	cmds.button (bgc = [1.0, 0.414999991655, 0.215599998832], l = 'Orange', w = bWidth/3, c = "import animPolish.ui as ui ; reload(ui) ; ui.assignColor ('orange')")
	cmds.button (bgc = [1.0, 0.725199997425, 0.097999997437], l = 'Yellow', c = "import animPolish.ui as ui ; reload(ui) ; ui.assignColor ('yellow')")
	cmds.button (bgc = [0.772899985313, 1.0, 0.215599998832], l = 'Yellow-Green', c = "import animPolish.ui as ui ; reload(ui) ; ui.assignColor ('yellowGreen')")
	cmds.button (bgc = [0.168899998069, 0.627399981022, 0.159899994731], l = 'Green', c = "import animPolish.ui as ui ; reload(ui) ; ui.assignColor ('green')")
	cmds.button (bgc = [0.106100000441, 0.90189999342, 0.555499970913], l = 'Teal', c = "import animPolish.ui as ui ; reload(ui) ; ui.assignColor ('teal')")
	cmds.button (bgc = [0.215599998832, 0.703299999237, 1.0], l = 'Light Blue', c = "import animPolish.ui as ui ; reload(ui) ; ui.assignColor ('lightBlue')")
	cmds.button (bgc = [0.137199997902, 0.352899998426, 1.0], l = 'Blue', c = "import animPolish.ui as ui ; reload(ui) ; ui.assignColor ('blue')")
	cmds.button (bgc = [0.433899998665, 0.215599998832, 1.0], l = 'Purple', c = "import animPolish.ui as ui ; reload(ui) ; ui.assignColor ('purple')")
	cmds.button (bgc = [0.996299982071, 0.588199973106, 1.0], l = 'Light Pink', c = "import animPolish.ui as ui ; reload(ui) ; ui.assignColor ('lightPink')")
	cmds.button (bgc = [0.993099987507, 0.215599998832, 1.0], l = 'Hot Pink', c = "import animPolish.ui as ui ; reload(ui) ; ui.assignColor ('hotPink')")
	cmds.button (bgc = [.5,.5,.5], l = 'Gray', c = "import animPolish.ui as ui ; reload(ui) ; ui.assignColor ('gray')")
	cmds.button (bgc = [0.0, 0.0, 0.0], l = 'Black', c = "import animPolish.ui as ui ; reload(ui) ; ui.assignColor ('black')")
	cmds.button (bgc = [1.0, 1.0, 1.0], l = 'White', c = "import animPolish.ui as ui ; reload(ui) ; ui.assignColor ('white')")
	cmds.setParent ('..')
	cmds.separator (h = 1, st = 'none')
	cmds.separator (h = 6, style = 'double')
	cmds.rowColumnLayout (nc = 3)
	cmds.text (l = '                 ')
	cmds.radioCollection ('jsap_colorMode_rc')
	cmds.radioButton ('jsap_colorMode_lambert_rb', l = 'Lambert       ')
	cmds.radioButton ('jsap_colorMode_blinn_rb', l = 'Blinn')
	cmds.radioCollection ('jsap_colorMode_rc', e = 1, sl = 'jsap_colorMode_blinn_rb')
	cmds.setParent ('..')
	cmds.separator (h = 1, st = 'none')
	cmds.iconTextButton (l = '                Random Colors', i = 'render_remapColor.png', bgc = bColor_brown, ann = 'Assigns random color shaders to selected objects.', st = 'iconAndTextHorizontal', w = bWidth, h = bHeight, c = "import animPolish.ui as ui ; reload(ui) ; ui.randomColors ()")
	cmds.separator (h = 6, st = 'none')
	cmds.setParent ('..')
	cmds.setParent ('..')

	# Caching
	cmds.frameLayout ('jsap_caching_fl', l = 'Caching', cll = 1, cl = 1, mh = 8, mw = 15, w = width, ann = "Export alembic caches into their own lightweight scenes for a fast workflow.")
	cmds.columnLayout (adj = 1, rs = 3)
	cmds.button (l = 'Refresh Data', ann = "Refresh tool with latest data from current scene and polish versions.", h = bHeight2, bgc = bColor_brown, c = 'import animPolish.ui as ui ; reload (ui) ; ui.cache_refresh (create = 0)')
	cmds.separator (h = 12, st = 'double')
	cmds.rowColumnLayout (nc = 2, cs = [2,3])
	cmds.text (l = 'Directory: ')
	cmds.textField ('jsap_cache_dir_tf', w = 187, h = 24, ann = "The directory that a will be filled with polish caches.", cc = 'import animPolish.ui as ui ; reload (ui) ; ui.cache_fieldWrite ()')
	cmds.setParent ('..')
	cmds.rowColumnLayout (nc = 2, cs = [2,3])
	cmds.button (l = 'Reset', ann = "Reset to a polish directory in the current file's location.", w = bWidth/2, h = bHeight2, bgc = bColor_blue, c = 'import animPolish.ui as ui ; reload (ui) ; ui.cache_resetDir ()')
	cmds.button (l = 'Browse', ann = "Choose a directory to work in. If it is not named 'polish' and does not contain a directory named 'polish', one will be created and set.", w = bWidth/2, h = bHeight2, bgc = bColor_blue, c = 'import animPolish.ui as ui ; reload (ui) ; ui.cache_browseDir ()')
	cmds.setParent ('..')
	cmds.separator (h = 12, st = 'double')
	cmds.rowColumnLayout (nc = 4, rs = [4,3], cs = [4,3])
	cmds.text (l = 'Cameras:  ', w = 53)
	cmds.textField ('jsap_cache_cams_tf', w = 148, ann = "The cameras or parent group/s that will be cached..", cc = 'import animPolish.ui as ui ; reload (ui) ; ui.cache_fieldWrite ()')
	cmds.text (l = '', w = 1)
	cmds.button (l = 'Load', ann = "Load cameras or parent group/s into field.", c = 'import animPolish.ui as ui ; reload (ui) ; ui.cache_loadCams ()')
	cmds.setParent ('..')
	cmds.iconTextButton (l = '               Export Cameras', i = 'cameraAim.png', bgc = bColor_green, ann = "Exports loaded cameras.\nCan be ran in an anim or polish scene.", st = 'iconAndTextHorizontal', w = bWidth, h = bHeight, c = 'import animPolish.ui as ui ; reload (ui) ; ui.cache_exportCams ()')
	cmds.iconTextButton (l = '               Import Cameras', i = 'cameraAimUp.png', bgc = bColor_green, ann = "Imports cameras.", st = 'iconAndTextHorizontal', w = bWidth, h = bHeight, c = 'import animPolish.ui as ui ; reload (ui) ; ui.cache_importCams ()')
	cmds.separator (h = 1, st = 'none')
	cmds.separator (h = 7, st = 'double')
	cmds.rowColumnLayout (nc = 2, rs = [4,3], cs = ([2,3]))
	cmds.text (l = 'Suffix:   ')
	cmds.textField ('jsap_cache_suff_tf', w = 198, h = 24, ann = "When creating a new polish version, you can give it a custom descriper prefix.", cc = 'import animPolish.ui as ui ; reload (ui) ; ui.cache_fieldWrite ()')
	cmds.setParent ('..')
	cmds.rowColumnLayout (nc = 4, cs = [4,3])
	cmds.text (l = 'Geo/Grp:  ')
	cmds.textField ('jsap_cache_geos_tf', w = 148, ann = "Geometry or parent group/s that will be cached.", cc = 'import animPolish.ui as ui ; reload (ui) ; ui.cache_fieldWrite ()')
	cmds.text (l = '', w = 1)
	cmds.button (l = 'Load', ann = "Load geometry or parent group/s into field.", c = 'import animPolish.ui as ui ; reload (ui) ; ui.cache_loadGeo ()')
	cmds.setParent ('..')
	cmds.separator (h = 1, st = 'none')
	cmds.textScrollList ('jsap_cache_lvs_tsl', a = 'New Version', si = 'New Version', ann = "Choose which version to run commands on.")
	#cmds.separator (h = 7, st = 'double')
	cmds.iconTextButton (l = '                   Export Geo', i = 'exportCache.png', bgc = bColor_green, ann = "Exports alembic caches of loaded geo into chosen polish version.\nCan be ran in an anim or polish scene.", st = 'iconAndTextHorizontal', w = bWidth, h = bHeight, c = 'import animPolish.ui as ui ; reload (ui) ; ui.cache_exportGeo ()')
	cmds.iconTextButton (l = '                  Import Geo', i = 'importCache.png', bgc = bColor_green, ann = "Imports cached geo from chosen polish directory.", st = 'iconAndTextHorizontal', w = bWidth, h = bHeight, c = 'import animPolish.ui as ui ; reload (ui) ; ui.cache_importGeo ()')
	cmds.separator (h = 4, st = 'none')
	cmds.rowColumnLayout (nc = 2, rs = [3,5], cs = [3,3])
	cmds.text ('           ')
	cmds.checkBox ('jsap_impFrameRange_cb', l = 'Adjust Frame Range On Import', v = 1, ann = 'Adjusts frame range to match ABC cache when importing.')
	cmds.setParent ('..')
	cmds.separator (h = 12, st = 'double')
	cmds.iconTextButton (l = '               Attach To Anim', i = 'blendShapePlus.png', bgc = bColor_green, ann = "For selected '_ABC_CTRL' nodes or all if nothing is selected, imports cache from chosen polish directory and creates override blendShapes to original geo.", st = 'iconAndTextHorizontal', w = bWidth, h = bHeight, c = 'import animPolish.ui as ui ; reload (ui) ; ui.cache_attach ()')
	cmds.button (l = 'Attach To Imported', bgc = bColor_blue, ann = "Based on a selection of 2 '_ABC_CTRL' nodes in the outliner, creates override blendShapes from first selection to second", w = bWidth/2, h = bHeight2, c = 'import animPolish.ui as ui ; reload (ui) ; ui.cache_attach_sel ()')
	#cmds.button (l = 'Swap Version', bgc = bColor_blue, ann = "Based on selection of an '_ABC_CTRL' nodes in the outliner, swaps the cache with that of the selected version.\nUseful for updating polish scenes with new animation without\nlosing work, and updating imported polish caches in anim scenes.\nDepending on your Maya version, you might have to save and re-open your scene to see changes.", w = bWidth/2, h = bHeight2, c = 'import animPolish.ui as ui ; reload (ui) ; ui.cache_swap ()')
	cmds.button (l = 'Delete From Scene', bgc = bColor_red, ann = "Deleted all relevant nodes from scene for selected '_ABC_CTRL'.", w = bWidth/2, h = bHeight2, c = 'import animPolish.ui as ui ; reload (ui) ; ui.cache_delete ()')
	cmds.separator (h = 20, st = 'none')
	cmds.setParent ('..')
	cmds.setParent ('..')

	# Utilities
	cmds.frameLayout ('jsap_utilities_fl', l = 'Utilities', cll = 1, cl = 1, mh = 8, mw = 15, w = width, ann = "Random helpers for various tasks.")
	cmds.columnLayout (adj = 1, rs = 3)
	cmds.iconTextButton (l = '               Cycle Cameras', i = 'cameraAim.png', bgc = bColor_brown, ann = 'Cycle view between all cameras in your scene.', st = 'iconAndTextHorizontal', w = bWidth, h = bHeight, c = 'import animPolish.cycleCam as cycleCam ; reload (cycleCam) ; cycleCam.run (skipOrtho = 0)')
	cmds.iconTextButton (l = '    Cycle Cameras (Skip Ortho)', i = 'cameraAim.png', bgc = bColor_brown, ann = 'Cycle view between all cameras in your scene, except for orthographic ones.', st = 'iconAndTextHorizontal', w = bWidth, h = bHeight, c = 'import animPolish.cycleCam as cycleCam ; reload (cycleCam) ; cycleCam.run (skipOrtho = 1)')
	cmds.iconTextButton (l = '                       Rivet', i = 'locator.png', bgc = bColor_brown, ann = 'Creates a locator from selected vertex or curve point that perfectly follows the position and rotation of the surface underneath it.', st = 'iconAndTextHorizontal', w = bWidth, h = bHeight, c = 'import animPolish.rivetStuff as rivetStuff ; reload (rivetStuff) ; rivetStuff.rivet_sel (loc = 1)')
	cmds.iconTextButton (l = '          Quick-Bake Selected', i = 'bakeAnimation.png', bgc = bColor_brown, ann = 'Disables the viewport and bakes keys on selected objects. If interrupted, use "Fix Viewport" to allow viewport refresh.', st = 'iconAndTextHorizontal', w = bWidth, h = bHeight, c = 'import animPolish.quickBake as quickBake ; reload (quickBake) ; quickBake.run_sel ()')
	cmds.iconTextButton (l = '           Rivet + Quick-Bake', i = 'bakeAnimation.png', bgc = bColor_brown, ann = 'Disables the viewport and bakes keys on a rivet created on selected vertices. If interrupted, use "Fix Viewport" to allow viewport refresh.', st = 'iconAndTextHorizontal', w = bWidth, h = bHeight, c = 'import animPolish.quickBake as quickBake ; reload (quickBake) ; quickBake.rivet_sel ()')
	cmds.iconTextButton (l = '    Riveted Plane + Quick-Bake', i = 'bakeAnimation.png', bgc = bColor_brown, ann = 'Disables the viewport and bakes keys on a rivet created on selected vertices, with a 1x1 polyPlane parented to it. If interrupted, use "Fix Viewport" to allow viewport refresh.', st = 'iconAndTextHorizontal', w = bWidth, h = bHeight, c = 'import animPolish.quickBake as quickBake ; reload (quickBake) ; quickBake.plane_sel ()')
	cmds.iconTextButton (l = '                Fix Viewport', i = 'cameraAimUp.png', bgc = bColor_brown, ann = 'If viewport refresh is locked after an interrupted quick-bake, this will fix the problem.', st = 'iconAndTextHorizontal', w = bWidth, h = bHeight, c = 'import animPolish.ui as ui ; reload(ui) ; ui.fixViewport ()')
	cmds.iconTextButton (l = '       Smooth Preview + (1-Div)', i = 'polySmooth.png', bgc = bColor_brown, ann = 'Enables smooth preview with 1-division on selected objects, as well as switches the smoothing algorithm to one that prevents fake geo clipping.', st = 'iconAndTextHorizontal', w = bWidth, h = bHeight, c = 'import animPolish.smoothPreview as smoothPreview ; reload (smoothPreview) ; smoothPreview.run (div = 1)')
	cmds.iconTextButton (l = '       Smooth Preview + (2-Div)', i = 'polySmooth.png', bgc = bColor_brown, ann = 'Enables smooth preview with 2-divisions on selected objects, as well as switches the smoothing algorithm to one that prevents fake geo clipping.', st = 'iconAndTextHorizontal', w = bWidth, h = bHeight, c = 'import animPolish.smoothPreview as smoothPreview ; reload (smoothPreview) ; smoothPreview.run (div = 2)')
	if user_data_directory:
		cmds.iconTextButton (l = '                   Copy Attrs', i = 'copySkinWeight.png', bgc = bColor_brown, ann = 'Writes a python file in maya/scripts that stores current attributes of selected object, to later be run with "Paste Attrs" to transfer the attributes to any other objects. Works between Maya sessions.', st = 'iconAndTextHorizontal', w = bWidth, h = bHeight, c = 'import animPolish.copyPasteAttrs as copyPasteAttrs ; reload (copyPasteAttrs) ; copyPasteAttrs.copy (path = "{}")'.format (user_data_directory))
		cmds.iconTextButton (l = '           Copy Attrs (Keyable)', i = 'copySkinWeight.png', bgc = bColor_brown, ann = 'Writes a python file in maya/scripts that stores current keyable attributes of selected object, to later be run with "Paste Attrs" to transfer the attributes to any other objects. Works between Maya sessions.', st = 'iconAndTextHorizontal', w = bWidth, h = bHeight, c = 'import animPolish.copyPasteAttrs as copyPasteAttrs ; reload (copyPasteAttrs) ; copyPasteAttrs.copy (path = "{}", k = 1)'.format (user_data_directory))
		cmds.iconTextButton (l = '                   Paste Attrs', i = 'copySkinWeight.png', bgc = bColor_brown, ann = 'Runs the Python file created in "Copy Attrs" on selected objects, transferring the stored atributes.', st = 'iconAndTextHorizontal', w = bWidth, h = bHeight, c = 'import animPolish.copyPasteAttrs as copyPasteAttrs ; reload (copyPasteAttrs) ; copyPasteAttrs.paste (path = "{}")'.format (user_data_directory))
	else:
		cmds.iconTextButton (l = '                   Copy Attrs', i = 'copySkinWeight.png', bgc = bColor_brown, ann = 'Writes a python file in maya/scripts that stores current attributes of selected object, to later be run with "Paste Attrs" to transfer the attributes to any other objects. Works between Maya sessions.', st = 'iconAndTextHorizontal', w = bWidth, h = bHeight, c = 'import animPolish.copyPasteAttrs as copyPasteAttrs ; reload (copyPasteAttrs) ; copyPasteAttrs.copy ()')
		cmds.iconTextButton (l = '           Copy Attrs (Keyable)', i = 'copySkinWeight.png', bgc = bColor_brown, ann = 'Writes a python file in maya/scripts that stores current keyable attributes of selected object, to later be run with "Paste Attrs" to transfer the attributes to any other objects. Works between Maya sessions.', st = 'iconAndTextHorizontal', w = bWidth, h = bHeight, c = 'import animPolish.copyPasteAttrs as copyPasteAttrs ; reload (copyPasteAttrs) ; copyPasteAttrs.copy (k = 1)')
		cmds.iconTextButton (l = '                   Paste Attrs', i = 'copySkinWeight.png', bgc = bColor_brown, ann = 'Runs the Python file created in "Copy Attrs" on selected objects, transferring the stored atributes.', st = 'iconAndTextHorizontal', w = bWidth, h = bHeight, c = 'import animPolish.copyPasteAttrs as copyPasteAttrs ; reload (copyPasteAttrs) ; copyPasteAttrs.paste ()')
	cmds.iconTextButton (l = '             Flood Smooth x10', i = 'art3dPaint.png', bgc = bColor_brown, ann = "When using Maya's Artisan painting suite to adjust any deformer maps, this will flood the smooth function 10 times.", st = 'iconAndTextHorizontal', w = bWidth, h = bHeight, c = 'import animPolish.ui as ui ; reload(ui) ; ui.floodSmooth (10)')
	cmds.iconTextButton (l = '     Parent Cluster Inverse Matrix', i = 'cluster.png', bgc = bColor_brown, ann = "Make it so that a cluster does not deform when its parents move around -- it will only deform when its own values change.", st = 'iconAndTextHorizontal', w = bWidth, h = bHeight, c = 'import animPolish.ui as ui ; reload (ui) ; ui.pim ()')
	cmds.separator (h = 30, st = 'none')
	cmds.setParent ('..')

	# Launch

	# Dock
	if dock == 1:
		cmds.dockControl (dockUI, l = 'AnimPolish', area = 'right', content = win, allowedArea = ['right', 'left'])
		cmds.refresh ()
		cmds.dockControl (dockUI, e = 1, r = 1, w = width+20)
	else:
		cmds.showWindow (win)
		cmds.window (win, e = 1, w = width+20, h = height)

	# Refresh fields
	cache_launch ()
	loadSettings ()



#########################
### Sculpt Pose Funcs ###
#########################



def scu_sculpt ():

	vis = cmds.checkBox ('jsap_scuVis_cb', q = 1, v = 1)
	shade = cmds.checkBox ('jsap_scuReshade_cb', q = 1, v = 1)
	sculptPose.sculpt_sel (vis = vis, shade = shade)

def scu_sculptFromZero ():

	mode = cmds.optionMenu ('jsap_sfz_om', q = 1, sl = 1)
	vis = cmds.checkBox ('jsap_scuVis_cb', q = 1, v = 1)
	shade = cmds.checkBox ('jsap_scuReshade_cb', q = 1, v = 1)
	lv = cmds.intField ('jsap_scuLevel_if', q = 1, v = 1)
	sculptPose.sculptFromZero_sel (vis = vis, shade = shade, lv = lv, mode = mode)

def scu_abortSculpt ():

	sculptPose.abortSculpt ()

def scu_apply ():

	ihi = cmds.checkBox ('jsap_scuData_cb', q = 1, v = 1)
	lv = cmds.intField ('jsap_scuLevel_if', q = 1, v = 1)
	sculptPose.apply_sel ('standard', lv = lv, ihi = ihi)

def scu_apply_1f ():

	sculptPose.apply_1f_sel ()

def scu_apply_p2p ():

	lv = cmds.intField ('jsap_scuLevel_if', q = 1, v = 1)
	ihi = cmds.checkBox ('jsap_scuData_cb', q = 1, v = 1)
	sculptPose.apply_p2p_sel (lv = lv, ihi = ihi)

def scu_createP2PZero ():

	lv = cmds.intField ('jsap_scuLevel_if', q = 1, v = 1)
	sculptPose.createP2PZero_sel (lv)

def scu_createP2PHold ():

	lv = cmds.intField ('jsap_scuLevel_if', q = 1, v = 1)
	ihi = cmds.checkBox ('jsap_scuData_cb', q = 1, v = 1)
	sculptPose.createP2PHold_sel (lv = lv, ihi = ihi)

def scu_delete (allP2P = 0):

	lv = cmds.intField ('jsap_scuLevel_if', q = 1, v = 1)
	sculptPose.delete_sel (lv, allP2P = allP2P)

def scu_editSculpt ():

	vis = cmds.checkBox ('jsap_scuVis_cb', q = 1, v = 1)
	shade = cmds.checkBox ('jsap_scuReshade_cb', q = 1, v = 1)
	sculptPose.editSculpt_sel (vis = 1, shade = 1)

def scu_applyEdit ():

	vis = cmds.checkBox ('jsap_scuVis_cb', q = 1, v = 1)
	shade = cmds.checkBox ('jsap_scuReshade_cb', q = 1, v = 1)
	lv = cmds.intField ('jsap_scuLevel_if', q = 1, v = 1)
	ihi = cmds.checkBox ('jsap_scuData_cb', q = 1, v = 1)
	sculptPose.applyEdit_sel (lv = lv, ihi = ihi)



#####################
### Wrap ++ Funcs ###
#####################



def wrap_loadVerts ():

	sel = cmds.ls (sl = 1, fl = 1)
	verts = []
	for i in sel:
		verts.append (str(i))
	cmds.textField ('jsap_wrap_autoFlood_tf', e = 1, tx = str(verts))

def wrap_clearVerts ():

	cmds.textField ('jsap_wrap_autoFlood_tf', e = 1, tx = '')

def wrap_wrapToMesh ():

	verts = cmds.textField ('jsap_wrap_autoFlood_tf', q = 1, tx = 1)
	smooth = cmds.intField ('jsap_wrap_autoSmooth_if', q = 1, v = 1)
	#hideData = cmds.checkBox ('jsap_wrap_data_cb', q = 1, v = 1)
	#wrap.wrapToMesh_sel (verts = verts, smooth = smooth, hideData = hideData)
	wrap.wrapToMesh_sel (verts = verts, smooth = smooth)

def wrap_wrapToWorld ():

	verts = cmds.textField ('jsap_wrap_autoFlood_tf', q = 1, tx = 1)
	smooth = cmds.intField ('jsap_wrap_autoSmooth_if', q = 1, v = 1)
	#hideData = cmds.checkBox ('jsap_wrap_data_cb', q = 1, v = 1)
	#wrap.wrapToWorld_sel (verts = verts, smooth = smooth, hideData = hideData)
	wrap.wrapToWorld_sel (verts = verts, smooth = smooth)



##############
### Subdue ###
##############



def subdue_run ():

	smooth = cmds.intField ('jsap_subdue_autoSmooth_if', q = 1, v = 1)
	rate = cmds.intField ('jsap_subdue_resample_if', q = 1, v = 1)
	subdue.run (rate = rate, smooth = smooth)




#########################
### Misc. Deformation ###
#########################



def growShrink_run ():

	smooth = cmds.intField ('jsap_misc_autoSmooth_if', q = 1, v = 1)
	hideData = cmds.checkBox ('jsap_misc_data_cb', q = 1, v = 1)
	growShrink.run_sel (smooth = smooth, hideData = hideData)

def iron_run ():

	smooth = cmds.intField ('jsap_misc_autoSmooth_if', q = 1, v = 1)
	hideData = cmds.checkBox ('jsap_misc_data_cb', q = 1, v = 1)
	iron.run_sel (smooth = smooth, hideData = hideData)

def misc_loadDfrmVerts ():

	sel = cmds.ls (sl = 1, fl = 1)
	verts = []
	for i in sel:
		verts.append (str(i))
	cmds.textField ('jsap_misc_dfrmVerts_tf', e = 1, tx = str(verts))

def misc_clearDfrmVerts ():

	cmds.textField ('jsap_misc_dfrmVerts_tf', e = 1, tx = '')

def misc_loadFloodVerts ():

	sel = cmds.ls (sl = 1, fl = 1)
	verts = []
	for i in sel:
		verts.append (str(i))
	cmds.textField ('jsap_misc_floodVerts_tf', e = 1, tx = str(verts))

def misc_clearFloodVerts ():

	cmds.textField ('jsap_misc_floodVerts_tf', e = 1, tx = '')



###################
### Native Maya ###
###################



def deltaMush ():

	cmds.deltaMush ()

def sine ():

	cmds.nonLinear (type = 'sine', amplitude = .1)

def wave ():

	cmds.nonLinear (type = 'wave', amplitude = .1)

def cluster ():

	cmds.cluster ()



#####################
### Assign Colors ###
#####################



def ac_lambert1 ():

	sel = cmds.ls (sl = 1)
	if sel:
		for i in sel:
			cmds.select (i)
			cmds.hyperShade (assign = 'lambert1')
		cmds.select (sel)
	else:
		cmds.warning ('Select some meshes!')

def assignColor (color):

	mode_q = cmds.radioCollection ('jsap_colorMode_rc', q = 1, sl = 1)
	if mode_q == 'jsap_colorMode_blinn_rb':
		mode = 'blinn'
	if mode_q == 'jsap_colorMode_lambert_rb':
		mode = 'lambert'
	assignColors.assign_sel (color, mode)

def randomColors ():

	mode_q = cmds.radioCollection ('jsap_colorMode_rc', q = 1, sl = 1)
	if mode_q == 'jsap_colorMode_blinn_rb':
		mode = 'blinn'
	if mode_q == 'jsap_colorMode_lambert_rb':
		mode = 'lambert'
	assignColors.random_sel (mode)



#################
### Utilities ###
#################



def saveSettings_run (typ, name, flag, f):

	exec ("val = cmds.{} ('{}', q = 1, {} = 1)".format (typ,name,flag))
	if typ == 'radioCollection':
		cmd = "        cmds.{} ('{}', e = 1, {} = '{}')\n".format (typ,name,flag,val)
	else:
		cmd = "        cmds.{} ('{}', e = 1, {} = {})\n".format (typ,name,flag,val)
	f.write (cmd)

def saveSettings ():

	# Get path
	if user_data_directory:
		root = user_data_directory
		if not root.endswith ('/'):
			root = '{}/'.format (root)
	else:
		root = jsap.__file__
		root = root.replace ('__init__.py', '')
	path = '{}user_settings.py'.format (root)
	f = open (path, 'w')
	f.write ("import maya.cmds as cmds\n\n")
	f.write ("def run ():\n\n")

	# Sculpt Pose
	f.write ('    # Sculpt Pose\n')
	f.write ('    try:\n')
	saveSettings_run ('frameLayout', 'jsap_sculptPose_fl', 'cl', f)
	saveSettings_run ('checkBox', 'jsap_scuVis_cb', 'v', f)
	saveSettings_run ('checkBox', 'jsap_scuReshade_cb', 'v', f)
	saveSettings_run ('checkBox', 'jsap_scuData_cb', 'v', f)
	saveSettings_run ('intField', 'jsap_scuLevel_if', 'v', f)
	saveSettings_run ('optionMenu', 'jsap_sfz_om', 'sl', f)
	f.write ('    except:\n')
	f.write ('        pass\n')
	f.write ('\n')

	# Wrap ++
	f.write ('    # Wrap ++\n')
	f.write ('    try:\n')
	saveSettings_run ('frameLayout', 'jsap_wrap_fl', 'cl', f)
	saveSettings_run ('intField', 'jsap_wrap_autoSmooth_if', 'v', f)
	f.write ('    except:\n')
	f.write ('        pass\n')
	f.write ('\n')

	# Subdue
	f.write ('    # Subdue\n')
	f.write ('    try:\n')
	saveSettings_run ('frameLayout', 'jsap_subdue_fl', 'cl', f)
	saveSettings_run ('intField', 'jsap_subdue_resample_if', 'v', f)
	saveSettings_run ('intField', 'jsap_subdue_autoSmooth_if', 'v', f)
	f.write ('    except:\n')
	f.write ('        pass\n')
	f.write ('\n')

	# Misc. Deformation
	f.write ('    # Misc. Deformation\n')
	f.write ('    try:\n')
	saveSettings_run ('frameLayout', 'jsap_miscDeformation_fl', 'cl', f)
	saveSettings_run ('intField', 'jsap_misc_autoSmooth_if', 'v', f)
	saveSettings_run ('checkBox', 'jsap_misc_data_cb', 'v', f)
	f.write ('    except:\n')
	f.write ('        pass\n')
	f.write ('\n')

	# Native Maya
	f.write ('    # Native Maya\n')
	f.write ('    try:\n')
	saveSettings_run ('frameLayout', 'jsap_nativeMaya_fl', 'cl', f)
	f.write ('    except:\n')
	f.write ('        pass\n')
	f.write ('\n')

	# Assign Colors
	f.write ('    # Assign Colors\n')
	f.write ('    try:\n')
	saveSettings_run ('frameLayout', 'jsap_assignColors_fl', 'cl', f)
	saveSettings_run ('radioCollection', 'jsap_colorMode_rc', 'sl', f)
	f.write ('    except:\n')
	f.write ('        pass\n')
	f.write ('\n')

	# Utilities
	f.write ('    # Utilities\n')
	f.write ('    try:\n')
	saveSettings_run ('frameLayout', 'jsap_utilities_fl', 'cl', f)
	f.write ('    except:\n')
	f.write ('        pass\n')
	f.write ('\n')

	# Caching
	f.write ('    # Caching\n')
	f.write ('    try:\n')
	saveSettings_run ('frameLayout', 'jsap_caching_fl', 'cl', f)
	f.write ('    except:\n')
	f.write ('        pass\n')
	f.write ('\n')

	# Close
	f.close ()

def loadSettings ():

	# Custom
	if user_data_directory:
		try:
			root = user_data_directory
			if not root.endswith ('/'):
				root = '{}/'.format (root)
			path = '{}/user_settings.py'.format (root)
			settings_file = imp.load_source ('user_settings.py', path)
			settings_file.run ()
		except:
			try:
				import animPolish.user_settings_default as user_settings_default
				reload (user_settings_default)
				user_settings_default.run ()
			except:
				sys.stdout.write ("Failed to load custom settings. Using defaults.")
	else:

		# Standard
		try:
			import animPolish.user_settings as user_settings
			reload (user_settings)
			user_settings.run ()
		except:
			try:
				import animPolish.user_settings_default as user_settings_default
				reload (user_settings_default)
				user_settings_default.run ()
			except:
				sys.stdout.write ("Failed to load custom settings. Using defaults.")

def defaultSettings ():

	if user_data_directory:
		root = user_data_directory
		if not root.endswith ('/'):
			root = '{}/'.format (root)
	else:
		root = jsap.__file__
		root = root.replace ('__init__.py', '')
	path = '{}user_settings.py'.format (root)
	try:
		os.remove (path)
	except:
		pass
	loadSettings ()

def toggleAnimEval ():

	rslt = toggleAnimEval_2 ()
	cmds.refresh ()
	sys.stdout.write ("Switched animation evaluation mode to '{}'.".format (rslt))
	cmds.refresh ()

def toggleAnimEval_2 ():

	mode = cmds.evaluationManager (q = 1, mode = 1)[0]
	if mode == 'off':
		cmds.evaluationManager (e = 1, mode = 'parallel')
		rslt = 'Parallel'
	elif mode == 'parallel' or mode == 'serial':
		cmds.evaluationManager (e = 1, mode = 'off')
		rslt = 'DG'
	return rslt

def fixViewport ():

	cmds.refresh (su = 0)

def floodSmooth (cnt):

	try:
		mel.eval ('artAttrPaintOperation artAttrCtx Smooth;')
		mel.eval ('artAttrCtx -e -opacity 1 `currentCtx`;')
		for i in range (cnt):
			mel.eval ('artAttrCtx -e -clear `currentCtx`;')
	except:
		cmds.warning ("Couldn't find any live paint deformer tools.")

def pim ():

	sel = cmds.ls (sl  = 1)
	for i in sel:
		try:
			out = cmds.listConnections (i, d = 1)[0]
			cmds.connectAttr ('{}.pim'.format (i), '{}.pm'.format (out), f = 1)
			cmds.setAttr ('{}.relative'.format (out), 0)
			sys.stdout.write ("Ran PIM on '{}'".format (i))
		except:
			cmds.warning ("Could not run on '{}'".format (i))



###############
### Caching ###
###############



def cache_launch ():

	cache_refresh (create = 0)

def cache_createMeta ():

	data = 'animPolish_cache_DATA'
	if not cmds.objExists (data):
		cmds.group (n = data, w = 1, em = 1)
		cmds.addAttr (data, dt = 'string', ln = 'cache_dir')
		cmds.addAttr (data, dt = 'string', ln = 'cache_geos')
		cmds.addAttr (data, dt = 'string', ln = 'cache_cams')
		cmds.addAttr (data, dt = 'string', ln = 'cache_suff')

def cache_refresh (create = 1):

	if create == 1:
		cache_createMeta ()

	data = 'animPolish_cache_DATA'
	if cmds.objExists (data):
		
		dir_q = cmds.getAttr ('{}.cache_dir'.format (data))
		geos_q = cmds.getAttr ('{}.cache_geos'.format (data))
		cams_q = cmds.getAttr ('{}.cache_cams'.format (data))
		suff_q = cmds.getAttr ('{}.cache_suff'.format (data))

		if dir_q:
			cmds.textField ('jsap_cache_dir_tf', e = 1, tx = dir_q)
		if geos_q:
			cmds.textField ('jsap_cache_geos_tf', e = 1, tx = geos_q)
		if cams_q:
			cmds.textField ('jsap_cache_cams_tf', e = 1, tx = cams_q)
		if suff_q:
			cmds.textField ('jsap_cache_suff_tf', e = 1, tx = suff_q)

	cache_refreshList ()

def cache_refreshList ():

	si = cmds.textScrollList ('jsap_cache_lvs_tsl', q = 1, si = 1)
	path = cmds.textField ('jsap_cache_dir_tf', q = 1, tx = 1)
	cmds.textScrollList ('jsap_cache_lvs_tsl', e = 1, ra = 1)
	if path:
		check = os.path.isdir (path)
		if not check:
			os.mkdir (path)
		contents = os.listdir (path)
		contents = sorted (contents)
		for i in contents:
			if '_polish' in i and '.' not in i:
				cmds.textScrollList ('jsap_cache_lvs_tsl', e = 1, a = i)
		cmds.textScrollList ('jsap_cache_lvs_tsl', e = 1, a = 'New Version', si = 'New Version')
	else:
		cmds.textScrollList ('jsap_cache_lvs_tsl', e = 1, a = 'New Version', si = 'New Version')
	if si:
		cmds.textScrollList ('jsap_cache_lvs_tsl', e = 1, si = si[0])

def cache_fieldWrite ():

	cache_createMeta ()

	tf = 'jsap_cache_dir_tf'
	attr = 'cache_dir'
	tx = cmds.textField (tf, q = 1, tx = 1)
	cmds.setAttr ('animPolish_cache_DATA.{}'.format (attr), tx, type = 'string')

	tf = 'jsap_cache_geos_tf'
	attr = 'cache_geos'
	tx = cmds.textField (tf, q = 1, tx = 1)
	cmds.setAttr ('animPolish_cache_DATA.{}'.format (attr), tx, type = 'string')

	tf = 'jsap_cache_cams_tf'
	attr = 'cache_cams'
	tx = cmds.textField (tf, q = 1, tx = 1)
	cmds.setAttr ('animPolish_cache_DATA.{}'.format (attr), tx, type = 'string')

	tf = 'jsap_cache_suff_tf'
	attr = 'cache_suff'
	tx = cmds.textField (tf, q = 1, tx = 1)
	cmds.setAttr ('animPolish_cache_DATA.{}'.format (attr), tx, type = 'string')

def cache_resetDir ():

	fullPath = cmds.file (q = 1, sn = 1)
	if fullPath:
		if ' ' not in fullPath:
			file = fullPath.split ('/')[-1]
			path = fullPath.replace ('/{}'.format (file),'')
			cmds.textField ('jsap_cache_dir_tf', e = 1, tx = '{}/polish'.format (path))
			cache_fieldWrite ()
			cache_refresh (create = 0)
		else:
			cmds.warning ('Directory path cannot contain spaces.')

def cache_browseDir ():

	path1 = cmds.fileDialog2 (ds = 2, fm = 2, okc = 'Set')
	if path1:
		if ' ' not in path1:
			path = path1[0]
			contents = os.listdir (path)
			if path.endswith ('/polish'):
				cmds.textField ('jsap_cache_dir_tf', e = 1, tx = path)
			else:
				cmds.textField ('jsap_cache_dir_tf', e = 1, tx = '{}/polish'.format (path))
			cache_fieldWrite ()
			cache_refresh (create = 0)
		else:
			cmds.warning ('Directory path cannot contain spaces.')

def cache_exportGeo ():

	path1 = cmds.textField ('jsap_cache_dir_tf', q = 1, tx = 1)
	geos = cmds.textField ('jsap_cache_geos_tf', q = 1, tx = 1)
	suff = cmds.textField ('jsap_cache_suff_tf', q = 1, tx = 1)
	if path1:
		version1 = cmds.textScrollList ('jsap_cache_lvs_tsl', q = 1, si = 1)
		if geos:
			if version1:
				version = version1[0]
				if version != 'New Version':
					path = '{}/{}'.format (path1,version)
					versionFinal = version
					confirm = cmds.confirmDialog (title = 'WARNING!', message = 'You are about to overwrite the selected version. Continue?', button = ['Yes','No'], defaultButton = 'Yes', cancelButton = 'No', dismissString = 'No')
					if confirm == 'Yes':
						caching.exp_geos (path, geos)
				else:
					contents1 = os.listdir (path1)
					contents = []
					for c in contents1:
						if '.' not in c:
							contents.append (c)
					if contents:
						contents.sort ()
						num = int(contents[-1].split ('_')[0]) + 1
						num = '{0:0=3d}'.format (num)
						if suff:
							path = '{}/{}_polish_{}'.format (path1,num,suff)
							versionFinal = '{}_polish_{}'.format (num,suff)
						else:
							path = '{}/{}_polish'.format (path1,num)
							versionFinal = '{}_polish'.format (num)
						cache_refreshList ()
					else:
						if suff:
							path = '{}/001_polish_{}'.format (path1,suff)
							versionFinal = '001_polish_{}'.format (suff)
						else:
							path = '{}/001_polish'.format (path1)
							versionFinal = '001_polish'
					caching.exp_geos (path, geos)
				cache_refreshList ()
				cmds.textScrollList ('jsap_cache_lvs_tsl', e = 1, si = versionFinal)
			else:
				cmds.warning ('No version selected.')
		else:
			cmds.warning ('No geometry loaded.')
	else:
		cmds.warning ('No directory chosen.')

def cache_exportCams ():

	path = cmds.textField ('jsap_cache_dir_tf', q = 1, tx = 1)
	cams = cmds.textField ('jsap_cache_cams_tf', q = 1, tx = 1)

	if path and cams:
	
		if os.path.isfile ('{}/cameras.ma'.format (path)):
			confirm = cmds.confirmDialog (title = 'WARNING!', message = "You are about to overwrite 'cameras.ma'. Continue?", button = ['Yes','No'], defaultButton = 'Yes', cancelButton = 'No', dismissString = 'No')
			if confirm == 'Yes':
				caching.exp_cams (path, cams)
		else:
			caching.exp_cams (path, cams)

	else:
		cmds.warning ("Directory and Cameras must be filled.")

def cache_loadGeo ():

	sel1 = cmds.ls (sl = 1, l = 1)
	sel = []
	for i in sel1:
		sel.append (str(i))
	cmds.textField ('jsap_cache_geos_tf', e = 1, tx = str(sel))
	cache_fieldWrite ()

def cache_loadCams ():

	sel1 = cmds.ls (sl = 1)
	sel = []
	for i in sel1:
		sel.append (str(i))
	cmds.textField ('jsap_cache_cams_tf', e = 1, tx = str(sel))
	cache_fieldWrite ()

def cache_importGeo ():

	version1 = cmds.textScrollList ('jsap_cache_lvs_tsl', q = 1, si = 1)
	path1 = cmds.textField ('jsap_cache_dir_tf', q = 1, tx = 1)
	cache_fieldWrite ()
	if path1:
		if version1:
			version = version1[0]
			if version != 'New Version':
				if not cmds.objExists ('|polish_ABC_CTRL_GRP|_{}_ABC_CTRL'.format (version)):
					path = '{}/{}'.format (path1,version)
					caching.imp_geos (path)
					if cmds.objExists ('polish_ABC_CTRL_GRP'):
						ctrls = []
						ctrls1 = cmds.listRelatives ('polish_ABC_CTRL_GRP', c = 1, type = 'transform', f = 1)
						for c in ctrls1:
							ctrls.append (str(c))
						cmds.textField ('jsap_cache_geos_tf', e = 1, tx = str(ctrls))
				else:
					cmds.warning ("'{}' already exists in this file.".format (version))
			else:
				cmds.warning ("Can only import from existing version.")
		else:
			cmds.warning ('No version selected.')
	else:
		cmds.warning ('No directory set.')

def cache_importCams ():

	path = cmds.textField ('jsap_cache_dir_tf', q = 1, tx = 1)
	cache_fieldWrite ()
	if path:
		caching.imp_cams (path)
		sys.stdout.write ("Built polish scene.")
	else:
		cmds.warning ('No directory set.')

def cache_attach ():

	caching.attach ()

def cache_attach_sel ():

	caching.attach_sel ()

def cache_swap ():

	version1 = cmds.textScrollList ('jsap_cache_lvs_tsl', q = 1, si = 1)
	path1 = cmds.textField ('jsap_cache_dir_tf', q = 1, tx = 1)
	if path1:
		if version1:
			version = version1[0]
			if version != 'New Version':
				if not cmds.objExists ('|polish_ABC_CTRL_GRP|_{}_ABC_CTRL'.format (version)):
					path = '{}/{}'.format (path1,version)
					caching.swap (path)
				else:
					cmds.warning ("'{}' already exists in this file.".format (version))
			else:
				cmds.warning ("Can only swap from existing version.")
		else:
			cmds.warning ('No version selected.')

def cache_delete ():

	caching.delete ()