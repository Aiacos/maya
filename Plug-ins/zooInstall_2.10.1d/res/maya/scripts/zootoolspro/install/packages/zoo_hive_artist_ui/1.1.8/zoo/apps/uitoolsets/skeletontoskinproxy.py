""" Simple UI for converting a skeleton into a skin proxy scalable mesh with live mirorring on the left and right joints.

"""

from zoovendor.Qt import QtWidgets

from zoo.apps.toolsetsui.widgets import toolsetwidget
from zoo.libs.pyqt import uiconstants as uic
from zoo.libs.pyqt.widgets import elements

from zoo.libs.maya.cmds.rig import skelemirror

UI_MODE_COMPACT = 0
UI_MODE_ADVANCED = 1


class SkeletonToSkinProxy(toolsetwidget.ToolsetWidget):
    id = "skeletonToSkinProxy"
    info = "Turn a Hive skeleton into a mirrored skin proxy skeleton."
    uiData = {"label": "Skeleton To Skin Proxy (beta)",
              "icon": "jointKnee",
              "tooltip": "Turn a Hive skeleton into a mirrored skin proxy skeleton.",
              "defaultActionDoubleClick": False,
              "helpUrl": "https://create3dcharacters.com/maya-tool-skeleton-to-skin-proxy/"}

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
        return super(SkeletonToSkinProxy, self).currentWidget()

    def widgets(self):
        """ Override base method for autocompletion

        :return:
        :rtype: list[GuiAdvanced or GuiCompact]
        """
        return super(SkeletonToSkinProxy, self).widgets()

    # ------------------
    # LOGIC
    # ------------------

    @toolsetwidget.ToolsetWidget.undoDecorator
    def skeletonToSkinProxy(self):
        """Creates custom rig groups from the selected Hive joints
        """
        skelemirror.buildSkeleMirrorSel(nameConvention=(self.properties.leftTxt.value,
                                                        self.properties.rightTxt.value),
                                        segmentScale=self.properties.segmentScaleCheckBox.value,
                                        hierarchy=self.properties.selHierarchyRadioWidget.value,
                                        mirror=self.properties.liveMirrorCheckBox.value)

    @toolsetwidget.ToolsetWidget.undoDecorator
    def selectHierarchy(self):
        """Selects the hierarchy of the skeleton"""
        skelemirror.selectHierarchy()

    # ------------------
    # CONNECTIONS
    # ------------------

    def uiConnections(self):
        """Add all UI connections here, button clicks, on changed etc"""
        for widget in self.widgets():
            widget.skeleToSkinProxyBtn.clicked.connect(self.skeletonToSkinProxy)
            widget.selHierarchyBtn.clicked.connect(self.selectHierarchy)


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
        # Selected Hierarchy Radio Buttons ------------------------------------
        radioNameList = ["Selected", "Hierarchy"]
        radioToolTipList = ["Affects only the selected joints.",
                            "Affects the selected joints and all of it's child joints."]
        self.selHierarchyRadioWidget = elements.RadioButtonGroup(radioList=radioNameList,
                                                                 toolTipList=radioToolTipList,
                                                                 default=1,
                                                                 parent=parent,
                                                                 margins=(uic.SVLRG2, 0, uic.SVLRG2, 0),
                                                                 spacing=uic.SXLRG)
        # Left and Right Text Edits ----------------------------------------------
        toolTip = "Search and replace text for left and right sides in the joint names."
        self.leftTxt = elements.StringEdit(label="Left Text",
                                           editText="_L_",
                                           parent=parent,
                                           toolTip=toolTip,
                                           editRatio=1,
                                           labelRatio=1)
        self.rightTxt = elements.StringEdit(label="Replace Right",
                                            editText="_R_",
                                            parent=parent,
                                            toolTip=toolTip,
                                            editRatio=1,
                                            labelRatio=1)
        # Checkbox layout ---------------------------------------
        toolTip = "Set the Segment Scale Compensate attribute on for all joints (recommended). \n" \
                  "This allows joints to scale individually without affecting children."
        self.segmentScaleCheckBox = elements.CheckBox(label="Segment Scale Compensate",
                                                      checked=True,
                                                      parent=parent,
                                                      toolTip=toolTip)
        toolTip = "Sets up a live-mirror so the right hand side joints automatically mirror the left. "
        self.liveMirrorCheckBox = elements.CheckBox(label="LiveMirror",
                                                    checked=True,
                                                    parent=parent,
                                                    toolTip=toolTip)
        # Select Hierarchy Button ---------------------------------------
        tooltip = "After completing the setup use this button to select the \n" \
                  "section below the selected joints to scale. \n\n" \
                  "Select Hierarchy Zoo Hotkey: ctrl shift alt Z"
        self.selHierarchyBtn = elements.styledButton("Select Hierarchy",
                                                     icon="cursorSelect",
                                                     toolTip=tooltip,
                                                     style=uic.BTN_DEFAULT)
        # Skele To Skin Proxy ---------------------------------------
        tooltip = "Sets up a scalable skin proxy skeleton, usually from a Hive FBX skeleton. \n" \
                  "This skeleton can be used to match to new meshes for skin transfers. And build new Hive rigs. \n\n" \
                  "Select joints or the skeleton root to create a live mirrored skin proxy setup and run. \n\n" \
                  " - Mirror links left joints to drive the right joints.  \n" \
                  " - Turns on Segment Scale Compensate for all joints.\n\n" \
                  "See the help page for full workflow instructions. (question mark icon)"
        self.skeleToSkinProxyBtn = elements.styledButton("Skeleton To Skin Proxy Skeleton",
                                                         icon="jointKnee",
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
        # Radio Layout ---------------------------------------
        radioLayout = elements.hBoxLayout(margins=(0, uic.SSML, 0, 0), spacing=uic.SPACING)
        radioLayout.addWidget(self.selHierarchyRadioWidget, 1)
        # Left Right Layout ---------------------------------------
        leftRightLayout = elements.hBoxLayout(margins=(uic.SLRG, uic.SSML, uic.SLRG, 0), spacing=uic.SREG)
        leftRightLayout.addWidget(self.leftTxt, 1)
        leftRightLayout.addWidget(self.rightTxt, 1)
        # Checkbox Layout ---------------------------------------
        checkBoxLayout = elements.hBoxLayout(margins=(uic.SLRG * 2, uic.SSML, uic.SLRG * 2, uic.SSML), spacing=uic.SREG)
        checkBoxLayout.addWidget(self.segmentScaleCheckBox, 1)
        checkBoxLayout.addWidget(self.liveMirrorCheckBox, 1)
        # Button Layout ---------------------------------------
        btnLayout = elements.hBoxLayout(margins=(0, 0, 0, 0), spacing=uic.SPACING)
        btnLayout.addWidget(self.skeleToSkinProxyBtn, 2)
        btnLayout.addWidget(self.selHierarchyBtn, 1)

        # Add To Main Layout ---------------------------------------
        mainLayout.addLayout(radioLayout)
        mainLayout.addLayout(leftRightLayout)
        mainLayout.addLayout(checkBoxLayout)
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
