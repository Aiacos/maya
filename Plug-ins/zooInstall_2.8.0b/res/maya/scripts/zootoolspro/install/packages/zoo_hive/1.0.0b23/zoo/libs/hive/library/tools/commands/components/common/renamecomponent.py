from zoo.libs.maya.mayacommand import command


class RenameComponentCommand(command.ZooCommandMaya):
    """Rename's the component instance
    """
    id = "hive.component.rename"
    creator = "David Sparrow"
    isUndoable = True
    uiData = {"icon": "",
              "tooltip": __doc__,
              "label": "Rename Component",
              "color": "",
              "backgroundColor": ""
              }
    _component = None
    _oldName = ""

    def resolveArguments(self, arguments):
        component = arguments.get("component")
        name = arguments.get("name")
        if not name:
            self.displayWarning("Must specify a valid name parameter")
            return
        self._component = component
        self._oldName = component.name()
        return arguments

    def doIt(self, component=None, name=None):
        component.rename(name)

    def undoIt(self):
        if self._component is not None and self._oldName:
            self._component.rename(self._oldName)


class SetSideComponentCommand(command.ZooCommandMaya):
    """Renames the component instance
    """
    id = "hive.component.rename.side"
    creator = "David Sparrow"
    isUndoable = True
    uiData = {"icon": "",
              "tooltip": __doc__,
              "label": "Rename Component Side",
              "color": "",
              "backgroundColor": ""
              }
    _component = None
    _oldName = ""

    def resolveArguments(self, arguments):
        component = arguments.get("component")
        name = arguments.get("side")
        if not name:
            self.displayWarning("Must specify a valid name parameter")
            return
        self._component = component
        self._oldName = component.side()
        return arguments

    def doIt(self, component=None, side=None):
        component.setSide(side)

    def undoIt(self):
        if self._component is not None and self._oldName:
            self._component.setSide(self._oldName)
