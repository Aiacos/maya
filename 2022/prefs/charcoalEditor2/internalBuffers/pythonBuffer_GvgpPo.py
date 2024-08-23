import maya.cmds as cmds
import maya.mel as mel

selection = cmds.ls(sl=True)

for geo in selection:
    cmds.select(geo)
    mel.eval('polyRetopo -constructionHistory 1 -replaceOriginal 1 -preserveHardEdges 0 -topologyRegularity 0.5 -faceUniformity 0 -anisotropy 0.75 -targetFaceCount 1000 -targetFaceCountTolerance 10;')