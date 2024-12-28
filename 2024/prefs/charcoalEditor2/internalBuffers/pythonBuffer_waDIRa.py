import maya.cmds as cmds
import maya.mel as mel

selection = cmds.ls(sl=True)

for geo in selection:
    cmds.select(geo)
    mel.eval('polyRemesh -caching 1 -constructionHistory 1 -maxEdgeLength 1 -useRelativeValues 1 -collapseThreshold 20 -smoothStrength 0 -tessellateBorders 1 -interpolationType 2;')
    cmds.select(geo)
    mel.eval('polyRetopo -constructionHistory 1 -replaceOriginal 1 -preserveHardEdges 0 -topologyRegularity 0.5 -faceUniformity 0 -anisotropy 0.75 -targetFaceCount 1000 -targetFaceCountTolerance 10;')