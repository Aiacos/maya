from zoo.libs.maya.mayacommand import command
from zoo.libs.hive import api


class GuideSymmetryCommand(command.ZooCommandMaya):
    id = "hive.component.symmetry"

    isUndoable = True
    isEnabled = True
    disableQueue = True  # If true, disable the undo queue in doIt()

    _mirrorData = {}
    _mirrorUndoData = {}

    def _resolveComponentData(self, rig, components, mirrorMapping, mirrorUndoData):
        for component in components:  # type: api.Component
            key = component.serializedTokenKey()
            if key in mirrorMapping:
                continue
            mirrorData = component.mirrorData(translate=("x",), rotate = "yz")
            if not mirrorData:
                continue
            mirrorMapping[key] = {"data": mirrorData["mirrorData"],
                                  "oppositeComponent": mirrorData["opposite"]}
            if mirrorData.get("undo"):
                mirrorUndoData[key] = {"data": mirrorData["undo"],
                                       "component": mirrorData["opposite"]}
            self._resolveComponentData(rig, component.children(), mirrorMapping, mirrorUndoData)

    def resolveArguments(self, arguments):
        components = arguments.get("components")
        rig = arguments.get("rig")
        mirrorMapping = {}
        mirrorUndoData = {}
        self._resolveComponentData(rig, components, mirrorMapping, mirrorUndoData)
        self._mirrorData = mirrorMapping
        self._mirrorUndoData = mirrorUndoData

        super(GuideSymmetryCommand, self).resolveArguments(arguments)

    def doIt(self, rig=None, components=None):
        components = [mirrorInfo["oppositeComponent"] for mirrorInfo in self._mirrorData.values()]
        with api.componentutils.disconnectComponentsContext(components):
            for _, mirrorInfo in self._mirrorData.items():
                comp = mirrorInfo["oppositeComponent"]
                comp.preMirror()
                api.mirrorutils.setMirrorData(mirrorInfo["data"])
                comp.postMirror()

        api.alignGuides(rig, components)

    def undoIt(self):
        components = [mirrorInfo["component"] for mirrorInfo in self._mirrorUndoData.values()]
        with api.componentutils.disconnectComponentsContext(components):
            for _, mirrorInfo in self._mirrorUndoData.items():
                comp = mirrorInfo["component"]
                comp.preMirror()
                api.mirrorutils.setMirrorData(mirrorInfo["data"], mirrorCurve=False)
                comp.postMirror()
