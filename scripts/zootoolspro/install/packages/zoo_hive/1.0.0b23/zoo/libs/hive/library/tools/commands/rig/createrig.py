from zoo.libs.maya.mayacommand import command
from zoo.libs.hive import api


class CreateRigCommand(command.ZooCommandMaya):
    id = "hive.rig.create"
    creator = "davidsp"
    isUndoable = False
    isEnabled = True
    _rig = None
    uiData = {"icon": "",
              "tooltip": "Creates a new instance of a rig or returns the existing one",
              "label": "Create rig",
              "color": "white",
              "backgroundColor": "black"
              }

    def resolveArguments(self, arguments):
        arguments["namespace"] = arguments.get("namespace", None)
        name = arguments.get("name")
        # guard against name being an empty string switch .get doesn't deal with
        if not name:
            name = "HiveRig"
        arguments["name"] = api.naming.uniqueNameForRig(api.iterSceneRigs(), name)
        return arguments

    def doIt(self, name=None, namespace=None):
        rig = api.Rig()
        self._rig = rig
        rig.startSession(name, namespace=namespace)
        return rig
