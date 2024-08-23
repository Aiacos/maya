from zoo.libs.maya.mayacommand import command
from zoo.libs.hive.base import component as hComponent


class ShowRigCommand(command.ZooCommandMaya):
    """Shows the rig layer for this component
    """
    id = "hive.component.rig.show"
    description = __doc__
    creator = "David Sparrow"
    isUndoable = True
    uiData = {"icon": "",
              "tooltip": __doc__,
              "label": "Show Rig",
              "color": "",
              "backgroundColor": ""
              }
    _component = None

    def resolveArguments(self, arguments):
        component = arguments.get("component")

        if not component or not isinstance(component, hComponent.Component):
            self.displayWarning("Must supply component instance")
            return arguments
        if not component.hasRig():
            self.displayWarning("Must have the Rig built for this component:{}".format(str(component)))
            return arguments
        self._component = component
        return arguments

    def doIt(self, component=None):
        layer = component.rigLayer()
        layer.show()

    def undoIt(self):
        if self._component is not None:
            layer = self._component.rigLayer()
            layer.hide()


class HideRigCommand(command.ZooCommandMaya):
    """Hide the rig Layer for the component
    """
    id = "hive.component.rig.hide"
    description = __doc__
    isUndoable = True
    creator = "David Sparrow"
    uiData = {"icon": "",
              "tooltip": __doc__,
              "label": "Hide Rig",
              "color": "",
              "backgroundColor": ""
              }
    _component = None

    def resolveArguments(self, arguments):
        component = arguments.get("component")

        if not component or not isinstance(component, hComponent.Component):
            self.displayWarning("Must supply rig instance")
            return
        if not component.hasRig():
            self.displayWarning("Must have the rig built for this component:{}".format(str(component)))
            return
        self._component = component
        return arguments

    def doIt(self, component=None):
        layer = component.rigLayer()
        layer.hide()

    def undoIt(self):
        if self._component is not None:
            layer = self._component.rigLayer()
            layer.show()


class ToggleRigVisibilityCommand(command.ZooCommandMaya):
    """Toggles the rig visibility for this component
    """
    id = "hive.component.rig.toggleVisibility"
    description = __doc__
    creator = "David Sparrow"
    isUndoable = True
    uiData = {"icon": "",
              "tooltip": __doc__,
              "label": "Toggle Rig Visibility",
              "color": "",
              "backgroundColor": ""
              }
    _component = None

    def resolveArguments(self, arguments):
        component = arguments.get("component")

        if not component or not isinstance(component, hComponent.Component):
            self.displayWarning("Must supply rig instance")
            return
        elif not component.hasRig():
            self.displayWarning("Must have the Rig built for this component:{}".format(str(component)))
            return
        self._component = component
        return arguments

    def doIt(self, component=None):
        layer = component.rigLayer()
        self._toggleVis(layer)

    def undoIt(self):
        if self._component is not None:
            layer = self._component.rigLayer()
            self._toggleVis(layer)

    def _toggleVis(self, layer):
        if layer.isHidden():
            layer.show()
            return
        layer.hide()
