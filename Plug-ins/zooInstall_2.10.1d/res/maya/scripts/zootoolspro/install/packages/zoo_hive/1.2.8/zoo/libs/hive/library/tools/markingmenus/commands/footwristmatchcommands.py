from zoo.libs.maya.markingmenu import menu
from zoo.libs.hive.library.matching import matchguides


class FootAlignmentCommand(menu.MarkingMenuCommand):
    id = "hiveFootGuideAlign"
    creator = "Zootools"

    @staticmethod
    def uiData(arguments):
        uiData = {
            "icon": "starControl",
            "label": "Align Foot Controls",
            "bold": False,
            "italic": False,
            "optionBox": False,
        }
        return uiData

    def execute(self, arguments):
        componentTypes = ("legcomponent", "quadLeg")
        for comp, nodes in arguments.get("componentToNodes", {}).items():
            if comp.componentType not in componentTypes:
                continue
            if comp.componentType == "quadLeg":
                matchguides.alignFeetGuideControls(comp, quadFix=True)
            else:
                matchguides.alignFeetGuideControls(comp, quadFix=False)


class WristAlignmentCommand(menu.MarkingMenuCommand):
    id = "hiveWristGuideAlign"
    creator = "Zootools"

    @staticmethod
    def uiData(arguments):
        uiData = {
            "icon": "starControl",
            "label": "Align Wrist Controls",
            "bold": False,
            "italic": False,
            "optionBox": False,
        }
        return uiData

    def execute(self, arguments):
        componentTypes = ("armcomponent",)
        for comp, nodes in arguments.get("componentToNodes", {}).items():
            if comp.componentType not in componentTypes:
                continue
            matchguides.alignWristControls(comp)
