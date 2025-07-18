import webbrowser

from zoo.apps.toolpalette import palette
from zoo.libs.pyqt.widgets.frameless import window
from zoo.core.util import zlogging
from zoo.apps.toolpalette import qtshelf
from zoo.core import engine
from zoovendor.Qt import QtGui

logger = zlogging.getLogger(__name__)


class HelpIconShelf(palette.ActionPlugin):
    id = "zoo.shelf.help"
    creator = "Andrew Silke"
    tags = ["shelf", "icon"]
    uiData = {"icon": "helpMenu_shlf", "label": "Help Menu"}
    _ADDRESSES = dict(
        create3dcharacters="https://create3dcharacters.com",
        latestNews="https://create3dcharacters.com/latest-news",
        zooToolsHelpContents="https://create3dcharacters.com/zoo2",
        zooToolsGettingStarted="https://create3dcharacters.com/zootools-getting-started",
        zooToolsInstallUpdate="https://create3dcharacters.com/maya-zoo-tools-pro-installer",
        zooToolsAssetsPresets="https://create3dcharacters.com/maya-zoo-tools-pro-installer",
        zooChangelog="https://create3dcharacters.com/maya-zoo-tools-pro-changelog",
        zooIssuesFixes="https://create3dcharacters.com/maya-zoo-tools-pro-known-issues",
        coursesByOrder="https://create3dcharacters.com/package-courses",
        coursesByPopularity="https://create3dcharacters.com/package-by-popularity",
        coursesByDateAdded="https://create3dcharacters.com/package-by-date-added",
        intermediateCourse="https://create3dcharacters.com/package-maya-generalist-intermediate",
        advancedCourse="https://create3dcharacters.com/package-maya-generalist-advanced",
        mayaHotkeyList="https://create3dcharacters.com/maya-hotkeys-zoo2",
        developerDocumentation="https://create3dcharacters.com/zoo-dev-documentation/index.html",
    )

    def execute(self, *args, **kwargs):
        name = kwargs["variant"]
        address = HelpIconShelf._ADDRESSES.get(name)
        if address:
            webbrowser.open(address)


class ZooShelfFloatingWindow(palette.ActionPlugin):
    id = "zoo.shelf.zooFloatingShelf"
    creator = "ZooTools"
    tags = ["shelf", "icon"]
    uiData = {
        "icon": "zooToolsZ",
        "tooltip": "Floating Shelf For Zoo Tools",
        "label": "Zoo Floating Shelf (shift+alt+Q)",
    }
    WINDOW_OFFSET_X = int(-(17 / 2 * 32))
    WINDOW_OFFSET_Y = -10

    def execute(self, *args, **kwargs):
        point = QtGui.QCursor.pos()
        point.setX(point.x() + ZooShelfFloatingWindow.WINDOW_OFFSET_X)
        point.setY(point.y() + ZooShelfFloatingWindow.WINDOW_OFFSET_Y)
        win = engine.currentEngine().showDialog(
            qtshelf.ShelfWindow, name="zooShelf", shelfId="ZooToolsPro", show=False
        )
        win.show(point)


class ResetAllWindowPosition(palette.ActionPlugin):
    id = "zoo.shelf.resetAllWindows"
    creator = "ZooTools"
    tags = ["shelf", "icon"]
    uiData = {
        "icon": "reloadWindows",
        "tooltip": "Resets all Zoo windows to be at the center of the host application",
        "label": "Reset All Zoo Windows",
    }

    def execute(self, *args, **kwargs):
        for i in window.getZooWindows():
            win = i.zooWindow
            if win is not None:
                win.centerToParent()


class ToggleZooLogging(palette.ActionPlugin):
    id = "zoo.logging"
    creator = "Zootools"
    tags = ["debug", "logging"]
    uiData = {
        "icon": "",
        "tooltip": "Sets Zoo tools logging to either DEBUG or INFO",
        "label": "Debug Logging",
        "isCheckable": True,
        "isChecked": zlogging.isGlobalDebug(),
    }

    def execute(self, *args, **kwargs):
        state = not zlogging.isGlobalDebug()
        if zlogging.isGlobalDebug():
            zlogging.setGlobalDebug(False)
        else:
            zlogging.setGlobalDebug(True)

        return state


class SliderTest(palette.SliderActionPlugin):
    id = "zoo.sliderTest"
    creator = "Zootools"

    @property
    def uiData(self):
        # example data for the plugin this is called for all child variants as well,
        # todo: provide variant id to uiData() maybe uiDataForVariant()?
        data = {
            "icon": "blender",
            "iconColor": (255.0, 153.0, 153.0),
            "tooltip": "Tween Machine Slider with Options",
            "widgetInfo": {
                "defaultValue": 0.5,
                "minValue": -0.25,
                "maxValue": 1.25,
                "value": 0.5,
                "someRandoKey": "something Weird",
            },
        }
        return data

    def execute(self, *args, **kwargs):
        print(self, args, kwargs)
        # means we're executing a menu action so we get the parent item
        if kwargs.get("variant", "") == "create3dcharacters":
            widgetInfo = kwargs["item"].parent.widgetInfo
            print(widgetInfo)
            print(widgetInfo["value"])
            print(widgetInfo["maxValue"])
            print(widgetInfo["minValue"])
