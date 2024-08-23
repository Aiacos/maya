from zoo.libs.maya.mayacommand import command
from zoo.libs.hive.base import rig as hiverig


class DeleteRigCommand(command.ZooCommandMaya):
    id = "hive.rig.delete"
    creator = "davidsp"
    isUndoable = True
    isEnabled = True
    _rig = None
    uiData = {"icon": "",
              "tooltip": "Deletes the rig instance from hive",
              "label": "Delete rig",
              "color": "white",
              "backgroundColor": "black"
              }
    _template = {}

    def doIt(self, rig=None):
        self._template = rig.serializeFromScene()
        rig.delete()
        return True

    def undoIt(self):
        if self._template:
            hiverig.loadFromTemplate(self._template)
