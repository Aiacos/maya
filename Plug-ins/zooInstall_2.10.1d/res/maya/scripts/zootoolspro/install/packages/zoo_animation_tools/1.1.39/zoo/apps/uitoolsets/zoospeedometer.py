""" ---------- Toolset Boiler Plate (Multiple UI Modes) -------------
The following code is a template (boiler plate) for building Zoo Toolset GUIs that multiple UI modes.

Multiple UI modes include compact and medium or advanced modes.

This UI will use Compact and Advanced Modes.

The code gets more complicated while dealing with UI Modes.

"""

from zoovendor.Qt import QtWidgets

from zoo.apps.toolsetsui.widgets import toolsetwidget
from zoo.libs.pyqt import uiconstants as uic
from zoo.libs.pyqt.widgets import elements

from zoo.libs.maya.cmds.animation import speed

UI_MODE_COMPACT = 0
UI_MODE_ADVANCED = 1


class ZooSpeedometer(toolsetwidget.ToolsetWidget):
    id = "zooSpeedometer"
    info = "Measures the speed of a selected object and displays it in the HUD"
    uiData = {"label": "Zoo Speedometer",
              "icon": "time",
              "tooltip": "Measures the speed of a selected object and displays it in the HUD",
              "defaultActionDoubleClick": False,
              "helpUrl": "https://create3dcharacters.com/maya-tool-zoo-speedometer/"}

    # ------------------
    # STARTUP
    # ------------------

    def preContentSetup(self):
        """First code to run, treat this as the __init__() method"""
        pass

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
        return super(ZooSpeedometer, self).currentWidget()

    def widgets(self):
        """ Override base method for autocompletion

        :return:
        :rtype: list[GuiAdvanced or GuiCompact]
        """
        return super(ZooSpeedometer, self).widgets()

    # ------------------
    # LOGIC
    # ------------------

    def createSpeedometer(self):
        displayUnits = speed.MEASUREMENT_UNITS[self.properties.unitsCombo.value]
        speed.createSpeedometer(displayUnits=displayUnits)

    def deleteSpeedometer(self):
        speed.deleteSpeedometer()

    # ------------------
    # CONNECTIONS
    # ------------------

    def uiConnections(self):
        """Add all UI connections here, button clicks, on changed etc"""
        for widget in self.widgets():
            widget.createSpeedometerBtn.clicked.connect(self.createSpeedometer)
            widget.deleteSpeedometerBtn.clicked.connect(self.deleteSpeedometer)


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
        # Display Units Combobox ---------------------------------------
        tooltip = "The units to display the speed in per hour. Default is km/hr."
        self.unitsCombo = elements.ComboBoxRegular(label="Units Per Hour",
                                                   items=speed.MEASUREMENT_UNITS,
                                                   setIndex=0,
                                                   parent=self,
                                                   toolTip=tooltip)
        # Buttons ---------------------------------------
        tooltip = ("Creates a speedometer from the first selected object. \n"
                   "The resulting HUD display the speed in km/hr and miles/hr.")
        self.createSpeedometerBtn = elements.styledButton("Create Speedometer",
                                                          icon="time",
                                                          toolTip=tooltip,
                                                          style=uic.BTN_DEFAULT)
        tooltip = "Removes the speedometer HUD"
        self.deleteSpeedometerBtn = elements.styledButton("",
                                                          icon="trash",
                                                          toolTip=tooltip,
                                                          style=uic.BTN_DEFAULT)


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
        # Button Layout ---------------------------------------
        btnLayout = elements.hBoxLayout(margins=(0, 0, 0, 0), spacing=uic.SPACING)
        btnLayout.addWidget(self.unitsCombo, 20)
        btnLayout.addWidget(self.createSpeedometerBtn, 20)
        btnLayout.addWidget(self.deleteSpeedometerBtn, 1)

        # Add To Main Layout ---------------------------------------
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
        # Button Layout ---------------------------------------
        btnLayout = elements.hBoxLayout(margins=(0, 0, 0, 0), spacing=uic.SPACING)
        btnLayout.addWidget(self.createSpeedometerBtn)
        btnLayout.addWidget(self.createSpeedometerBtn)
        btnLayout.addWidget(self.deleteSpeedometerBtn)

        # Add To Main Layout ---------------------------------------
        mainLayout.addWidget(self.unitsCombo)
        mainLayout.addLayout(btnLayout)
