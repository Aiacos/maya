""" Simple UI for converting a skeleton into a skin proxy scalable mesh with live mirorring on the left and right joints.

"""

from zoovendor.Qt import QtWidgets

from zoo.apps.toolsetsui.widgets import toolsetwidget
from zoo.libs.pyqt import uiconstants as uic
from zoo.libs.pyqt.widgets import elements

from zoo.apps.toolsetsui import toolsetui, toolsetcallbacks
from zoo.libs.hive.characterizer import skinproxy
from zoo.libs.maya.cmds.rig import skelemirror

import zoo.libs.maya.cmds.hotkeys.definedhotkeys as hk

UI_MODE_COMPACT = 0
UI_MODE_ADVANCED = 1


class HiveCharacterizer(toolsetwidget.ToolsetWidget):
    id = "hiveCharacterizer"
    info = "Creates new characters from the skin proxy skeleton."
    uiData = {"label": "Hive Characterizer (alpha)",
              "icon": "settingSliders",
              "tooltip": "Creates new characters from the skin proxy skeleton.",
              "defaultActionDoubleClick": False,
              "helpUrl": "https://create3dcharacters.com/maya-tool-hive-characterizer/"}
    # TODO: Duplicate shaders when the rig builds so its not in the skinProxy namespace

    # ------------------
    # STARTUP
    # ------------------

    def preContentSetup(self):
        """First code to run, treat this as the __init__() method"""
        self.toolsetWidget = self  # needed for UI change sizes

    def contents(self):
        """The UI Modes to build, compact, medium and or advanced """
        return [self.initCompactWidget()]  # self.initAdvancedWidget()

    def initCompactWidget(self):
        """Builds the Compact GUI (self.compactWidget) """
        self.compactWidget = GuiCompact(parent=self, properties=self.properties, toolsetWidget=self)
        return self.compactWidget

    def initAdvancedWidget(self):
        """Builds the Advanced GUI (self.advancedWidget) """
        self.advancedWidget = GuiAdvanced(parent=self, properties=self.properties, toolsetWidget=self)
        return self.advancedWidget

    def postContentSetup(self):
        """Last of the initialize code"""
        self.uiConnections()
        self.disableEnableSliders()

    def defaultAction(self):
        """Double Click
        Double clicking the tools toolset icon will run this method
        Be sure "defaultActionDoubleClick": True is set inside self.uiData (meta data of this class)"""
        pass

    def currentWidget(self):
        """ Currently active widget

        :return:
        :rtype: GuiAdvanced or GuiCompact
        """
        return super(HiveCharacterizer, self).currentWidget()

    def widgets(self):
        """ Override base method for autocompletion

        :return:
        :rtype: list[GuiAdvanced or GuiCompact]
        """
        return super(HiveCharacterizer, self).widgets()

    # ------------------
    # SEND/RECEIVE
    # ------------------

    def global_sendProxyImported(self, proxyImported=False):
        """Updates all GUIs with the copied shader"""
        toolsets = toolsetui.toolsetsByAttr(attr="global_receiveProxyImported")
        for tool in toolsets:
            tool.global_receiveProxyImported(proxyImported=proxyImported)

    def global_receiveProxyImported(self, proxyImported=False):
        """Receives the copied proxy import/delete from other GUIs"""
        self.disableEnableSliders()

    # ------------------
    # UI
    # ------------------

    def enterEvent(self, event):
        """When the cursor enters the UI update it"""
        self.disableEnableSliders()

    def disableEnableSliders(self):
        """Disables or enables the sliders based on the skin proxy being in the scene"""
        if skinproxy.skinProxyExists():
            for widget in self.widgets():
                for slider in widget.allSliders:
                    slider.setEnabled(True)
        else:
            for widget in self.widgets():
                for slider in widget.allSliders:
                    slider.setEnabled(False)

    # ------------------
    # LOGIC
    # ------------------

    @toolsetwidget.ToolsetWidget.undoDecorator
    def headSlider(self):
        """Head Slider"""
        skinproxy.bodyPartAdjust("head",
                                 self.properties.headSlider.value)

    @toolsetwidget.ToolsetWidget.undoDecorator
    def chestSlider(self):
        """Chest Slider"""
        skinproxy.bodyPartAdjust("chest",
                                 self.properties.chestSlider.value)

    @toolsetwidget.ToolsetWidget.undoDecorator
    def hipsSlider(self):
        """Hips Slider"""
        skinproxy.bodyPartAdjust("hips",
                                 self.properties.hipsSlider.value)

    @toolsetwidget.ToolsetWidget.undoDecorator
    def armsSlider(self):
        """Arms Slider"""
        skinproxy.bodyPartAdjust("arms",
                                 self.properties.armsSlider.value)

    @toolsetwidget.ToolsetWidget.undoDecorator
    def handsSlider(self):
        """Hands Slider"""
        skinproxy.bodyPartAdjust("hands",
                                 self.properties.handsSlider.value)

    @toolsetwidget.ToolsetWidget.undoDecorator
    def legsSlider(self):
        """Legs Slider"""
        skinproxy.bodyPartAdjust("legs",
                                 self.properties.legsSlider.value)

    def allBodyParts(self):
        """All Body Parts Slider"""
        value = self.properties.allSlider.value
        for bodyPart in ["head", "chest", "hips", "legs", "arms", "hands"]:
            skinproxy.bodyPartAdjust(bodyPart, value)
        self.properties.headSlider.value = value
        self.properties.chestSlider.value = value
        self.properties.hipsSlider.value = value
        self.properties.armsSlider.value = value
        self.properties.handsSlider.value = value
        self.properties.legsSlider.value = value
        self.updateFromProperties()

    @toolsetwidget.ToolsetWidget.undoDecorator
    def selectHierarchy(self):
        """Selects the hierarchy of the skeleton"""
        skelemirror.selectHierarchy()

    @toolsetwidget.ToolsetWidget.undoDecorator
    def importSkinProxy(self):
        skinproxy.importSkinProxy()
        self.disableEnableSliders()
        self.global_sendProxyImported(proxyImported=True)

    @toolsetwidget.ToolsetWidget.undoDecorator
    def deleteSkinProxy(self):
        skinproxy.deleteSkinProxy()
        self.disableEnableSliders()
        self.global_sendProxyImported(proxyImported=False)

    def createHiveRig(self):
        hk.open_skinProxyToRig()

    # ------------------
    # CONNECTIONS
    # ------------------

    def uiConnections(self):
        """Add all UI connections here, button clicks, on changed etc"""
        for widget in self.widgets():
            for slider in widget.allSliders:
                slider.sliderPressed.connect(self.openUndoChunk)
                slider.sliderReleased.connect(self.closeUndoChunk)
            widget.allSlider.numSliderChanged.connect(self.allBodyParts)
            widget.headSlider.numSliderChanged.connect(self.headSlider)
            widget.chestSlider.numSliderChanged.connect(self.chestSlider)
            widget.hipsSlider.numSliderChanged.connect(self.hipsSlider)
            widget.armsSlider.numSliderChanged.connect(self.armsSlider)
            widget.handsSlider.numSliderChanged.connect(self.handsSlider)
            widget.legsSlider.numSliderChanged.connect(self.legsSlider)
            # buttons ---------------------------------------
            widget.importSkinProxyBtn.clicked.connect(self.importSkinProxy)
            widget.deleteSkinProxyBtn.clicked.connect(self.deleteSkinProxy)
            widget.createHiveRig.clicked.connect(self.createHiveRig)
            widget.selectHierarchyBtn.clicked.connect(self.selectHierarchy)



class GuiWidgets(QtWidgets.QWidget):
    def __init__(self, parent=None, properties=None, uiMode=None, toolsetWidget=None):
        """Builds the main widgets for all GUIs

        properties is the list(dictionaries) used to set logic and pass between the different UI layouts
        such as compact/adv etc

        :param parent: the parent of this widget
        :type parent: QtWidgets.QWidget
        :param properties: the properties dictionary which tracks all the properties of each widget for UI modes
        :type properties: zoo.apps.toolsetsui.widgets.toolsetwidget.PropertiesDict
        :param uiMode: 0 is compact ui mode, 1 is advanced ui mode
        :type uiMode: int
        """
        super(GuiWidgets, self).__init__(parent=parent)
        self.properties = properties
        # Head Slider ---------------------------------------
        toolTip = ""
        self.headSlider = elements.FloatSlider(label="Head",
                                               defaultValue=0.0,
                                               sliderMax=1.0,
                                               sliderMin=0.0,
                                               toolTip=toolTip,
                                               dynamicMax=True)
        # Chest Slider ---------------------------------------
        toolTip = ""
        self.chestSlider = elements.FloatSlider(label="Chest",
                                                defaultValue=0.0,
                                                sliderMax=1.0,
                                                sliderMin=0.0,
                                                toolTip=toolTip,
                                                dynamicMax=True)
        # Hips Slider ---------------------------------------
        toolTip = ""
        self.hipsSlider = elements.FloatSlider(label="Hips",
                                               defaultValue=0.0,
                                               sliderMax=1.0,
                                               sliderMin=0.0,
                                               toolTip=toolTip,
                                               dynamicMax=True)
        # Arms Slider ---------------------------------------
        toolTip = ""
        self.armsSlider = elements.FloatSlider(label="Arms",
                                               defaultValue=0.0,
                                               sliderMax=1.0,
                                               sliderMin=0.0,
                                               toolTip=toolTip,
                                               dynamicMax=True)
        # Hands Slider ---------------------------------------
        toolTip = ""
        self.handsSlider = elements.FloatSlider(label="Hands",
                                                defaultValue=0.0,
                                                sliderMax=1.0,
                                                sliderMin=0.0,
                                                toolTip=toolTip,
                                                dynamicMax=True)
        # Legs Slider ---------------------------------------
        toolTip = ""
        self.legsSlider = elements.FloatSlider(label="Legs",
                                               defaultValue=0.0,
                                               sliderMax=1.0,
                                               sliderMin=0.0,
                                               toolTip=toolTip,
                                               dynamicMax=True)
        # Legs Slider ---------------------------------------
        toolTip = ""
        self.allSlider = elements.FloatSlider(label="All",
                                               defaultValue=0.0,
                                               sliderMax=1.0,
                                               sliderMin=0.0,
                                               toolTip=toolTip,
                                               dynamicMax=True)
        self.allSliders = [self.headSlider, self.chestSlider, self.hipsSlider, self.armsSlider, self.handsSlider,
                           self.legsSlider, self.allSlider]
        # Import Skin Proxy ---------------------------------------
        tooltip = "Import the skin proxy rig that can be characterized."
        self.importSkinProxyBtn = elements.styledButton("Import Skin Proxy",
                                                       parent=parent,
                                                       icon="importArrow",
                                                       toolTip=tooltip,
                                                       style=uic.BTN_DEFAULT)
        # Delete Skin Proxy Button --------------------------------------
        tooltip = "Delete the Skin Proxy from the scene. "
        self.deleteSkinProxyBtn = elements.styledButton("",
                                                        icon="trash",
                                                        toolTip=tooltip,
                                                        style=uic.BTN_DEFAULT,
                                                        parent=parent)
        # Create Hive Rig ---------------------------------------
        tooltip = "Open the Skin Proxy To Rig UI.  \n" \
                  "This will create a new rig from the skin proxy."
        self.createHiveRig = elements.styledButton("Create Hive Rig UI",
                                                   parent=parent,
                                                   icon="superhero",
                                                   toolTip=tooltip,
                                                   style=uic.BTN_DEFAULT)

        # Select Hierarchy Button --------------------------------------
        tooltip = "Select the hierarchy of a selected joint/control. "
        self.selectHierarchyBtn = elements.styledButton("",
                                                        icon="cursorSelect",
                                                        toolTip=tooltip,
                                                        style=uic.BTN_DEFAULT,
                                                        parent=parent)


class GuiCompact(GuiWidgets):
    def __init__(self, parent=None, properties=None, uiMode=UI_MODE_COMPACT, toolsetWidget=None):
        """Adds the layout building the compact version of the GUI:

            default uiMode - 0 is advanced (UI_MODE_COMPACT)

        :param parent: the parent of this widget
        :type parent: QtWidgets.QWidget
        :param properties: the properties dictionary which tracks all the properties of each widget for UI modes
        :type properties: zoo.apps.toolsetsui.widgets.toolsetwidget.PropertiesDict
        """
        super(GuiCompact, self).__init__(parent=parent, properties=properties, uiMode=uiMode,
                                         toolsetWidget=toolsetWidget)
        # Main Layout ---------------------------------------
        mainLayout = elements.vBoxLayout(self, margins=(uic.WINSIDEPAD, uic.WINBOTPAD, uic.WINSIDEPAD, uic.WINBOTPAD),
                                         spacing=uic.SREG)
        # Buttons Layout ---------------------------------------
        btnLayout = elements.hBoxLayout(margins=(0, 0, 0, 0), spacing=uic.SPACING)
        btnLayout.addWidget(self.importSkinProxyBtn, 20)
        btnLayout.addWidget(self.deleteSkinProxyBtn, 1)
        btnLayout.addWidget(self.createHiveRig, 20)
        btnLayout.addWidget(self.selectHierarchyBtn, 1)

        # Add To Main Layout ---------------------------------------
        mainLayout.addWidget(self.allSlider)
        mainLayout.addWidget(elements.LabelDivider("Body Parts"))
        mainLayout.addWidget(self.headSlider)
        mainLayout.addWidget(self.chestSlider)
        mainLayout.addWidget(self.hipsSlider)
        mainLayout.addWidget(self.legsSlider)
        mainLayout.addWidget(self.armsSlider)
        mainLayout.addWidget(self.handsSlider)
        mainLayout.addLayout(btnLayout)


class GuiAdvanced(GuiWidgets):
    def __init__(self, parent=None, properties=None, uiMode=UI_MODE_ADVANCED, toolsetWidget=None):
        """Adds the layout building the advanced version of the GUI:

            default uiMode - 1 is advanced (UI_MODE_ADVANCED)

        :param parent: the parent of this widget
        :type parent: QtWidgets.QWidget
        :param properties: the properties dictionary which tracks all the properties of each widget for UI modes
        :type properties: zoo.apps.toolsetsui.widgets.toolsetwidget.PropertiesDict
        """
        super(GuiAdvanced, self).__init__(parent=parent, properties=properties, uiMode=uiMode,
                                          toolsetWidget=toolsetWidget)
        # Main Layout ---------------------------------------
        mainLayout = elements.vBoxLayout(self, margins=(uic.WINSIDEPAD, uic.WINBOTPAD, uic.WINSIDEPAD, uic.WINBOTPAD),
                                         spacing=uic.SREG)
        # Add To Main Layout ---------------------------------------
