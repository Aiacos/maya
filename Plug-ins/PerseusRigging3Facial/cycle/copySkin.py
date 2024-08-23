# Copy Skin Weights Created by Mohammad Jafarian contact@perseusrigging.com
# Copy Skin Weights from one mesh to another meshes or from some vertices to another vertices on the same mesh or different mesh
# Tested under MAYA 2016,2017


import pymel.core as pmel
import maya.cmds as cmds
import maya.mel as mel            
sourceVertexLs = []            
destinationVertexLs = []

def source_define():
    base=cmds.ls(sl=1)          
    mel.eval("PolySelectConvert 3;")
    SourceDestinationSel('source')
    print sourceVertexLs
    cmds.select(base)

def destination_define():
    base=cmds.ls(sl=1)
    mel.eval("PolySelectConvert 3;")
    SourceDestinationSel('destination')
    print destinationVertexLs
    cmds.select(base)
    
def SourceDestinationSel(sdType):
    global destinationVertexLs
    global sourceVertexLs
    selectionList = pmel.ls(sl=1, flatten = 1)
    if selectionList:
        if pmel.nodeType(selectionList[0]) == 'mesh':
            mel.eval("PolySelectConvert 3;")
            selectionList = pmel.ls(sl=1, flatten = 1)
            if sdType == 'destination' :
                destinationVertexLs = selectionList
            if sdType == 'source' :
                sourceVertexLs = selectionList
def copySkinGlobal( ):
    global sourceVertexLs
    global destinationVertexLs
    base=cmds.ls(sl=1)
    copySkinMain()
    sourceVertexLs = []
    destinationVertexLs = []
    cmds.select(base)    

def copySkinMain():
    global progSkin
    sourceVer = sourceVertexLs
    destinationVer = destinationVertexLs
    i=0.0
    if len(destinationVer)>0:
        for x_dis in destinationVer:
            x_disPos = x_dis.getPosition()
            length = 20000
            closest_src = None
            for x_src in sourceVer:
                newlength = (x_disPos-x_src.getPosition()).length()
                if newlength < length:
                    length = newlength
                    closest_src = x_src
            if closest_src:
                pmel.select(closest_src)
                mel.eval( 'artAttrSkinWeightCopy' )
                pmel.select(x_dis)
                mel.eval( 'artAttrSkinWeightPaste' )
                i+=10.0/len(destinationVer)
                pmel.progressBar(progSkin, edit=True, progress=i)

def main():
    global progSkin
    cmds.window(title='Copy Skin Weights',widthHeight=[400,100],s=0)
    cmds.rowColumnLayout(nr=2)
    cmds.button(label="Source mesh/vertices",height=50, width=200, c='source_define()')
    cmds.button(label="Destination meshes/vertices",height=50, width=200, c='destination_define()')
    cmds.button(label="Copy Skin Weights", width=200, c='copySkinGlobal()')
    progSkin=cmds.progressBar(maxValue=10, width=200)

main()
cmds.showWindow()
    

    

    