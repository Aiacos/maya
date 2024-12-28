import maya.cmds as cmds

#scene = cmds.file(q=True, sn=True)
scene = '/'.join(cmds.file(q=True, sn=True).split('/')[:-1]) + '/'

print(scene)