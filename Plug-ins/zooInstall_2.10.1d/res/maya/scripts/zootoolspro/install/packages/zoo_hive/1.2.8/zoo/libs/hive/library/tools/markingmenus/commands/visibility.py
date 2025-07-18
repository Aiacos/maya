from zoo.libs.maya.markingmenu import menu
from zoo.libs.hive import api
from zoo.libs.utils import output
from zoo.core.util import zlogging
from maya import cmds

logger = zlogging.getLogger(__name__)


class DeformVisibilityGuides(menu.MarkingMenuCommand):
    id = "hiveToggleDeformVisibility"
    creator = "Zootools"

    @staticmethod
    def uiData(arguments):
        uiData = {"icon": "connectionSRT",
                  "label": "Show Joints",
                  "bold": False,
                  "italic": False,
                  "optionBox": False,
                  "checkBox": False
                  }
        rig = arguments.get("rig")
        if not rig:
            output.displayWarning("Unable to detect hive rig from current selection")
            return uiData
        deform = rig.deformLayer()
        if deform:
            hidden = not deform.rootTransform().isHidden()
            uiData["checkBox"] = hidden
            arguments["hiddenState"] = not hidden
        return uiData

    def execute(self, arguments):
        """The execute method is called when triggering the action item. use executeUI() for a optionBox.

        :type arguments: dict
        """
        rig = arguments.get("rig")
        if not rig:
            output.displayWarning("Unable to detect hive rig from current selection")
            return
        deformLayer = rig.deformLayer()
        if deformLayer:
            cmds.setAttr(".".join((deformLayer.rootTransform().fullPathName(), "visibility")),
                         arguments.get("hiddenState", False))
        output.displayInfo("Completed switching display of the skeleton")


class SoloComponent(menu.MarkingMenuCommand):
    id = "hiveSoloComponent"
    creator = "Zootools"

    @staticmethod
    def uiData(arguments):
        uiData = {"icon": "solo",
                  "label": "Solo Component",
                  "bold": False,
                  "italic": False
                  }
        rig = arguments.get("rig")
        if not rig:
            output.displayWarning("Unable to detect hive rig from current selection")
            return uiData

        for component in rig.iterComponents():
            if component.isHidden():
                uiData["checkBox"] = True
                uiData["label"] = "UnSolo Component"
                break
        else:
            uiData["checkBox"] = False
        arguments["checked"] = uiData["checkBox"]
        rig = arguments.get("rig")
        if not rig:
            output.displayWarning("Unable to detect hive rig from current selection")
            return uiData
        return uiData

    def execute(self, arguments):
        """The execute method is called when triggering the action item. use executeUI() for a optionBox.

        :type arguments: dict
        """
        rig = arguments.get("rig")
        if not rig:
            output.displayWarning("Unable to detect hive rig from current selection")
            return
        show = arguments["checked"]

        if show:
            componentsToShow = []
            for component in rig.iterComponents():
                if component.isHidden():
                    componentsToShow.append(component)
            if componentsToShow:
                api.commands.showComponents(componentsToShow)
            return

        # soloing hides everything else except for the selected components
        toHide = []
        requestedComponents = arguments["components"]
        for component in rig.iterComponents():
            if not component.isHidden() and component not in requestedComponents:
                toHide.append(component)
        api.commands.hideComponents(toHide)

        output.displayInfo("Completed switching display of the skeleton")