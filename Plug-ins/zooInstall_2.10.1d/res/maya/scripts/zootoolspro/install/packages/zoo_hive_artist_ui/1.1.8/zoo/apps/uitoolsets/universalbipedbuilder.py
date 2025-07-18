""" ---------- Universal Mesh To Hive -------------
Takes a universal mesh and builds a Hive guides/rig

"""
import ast, os
from functools import partial

from zoovendor.Qt import QtWidgets

from zoo.apps.toolsetsui.widgets import toolsetwidget
from zoo.libs.pyqt import uiconstants as uic
from zoo.libs.pyqt.widgets import elements
from zoo.libs.utils import output, filesystem
from zoo.libs.maya.cmds.workspace import mayaworkspace
from zoo.libs.maya.cmds.filemanage import saveexportimport

from zoo.libs.hive.universalmesh import universalmesh, umeshconstants
from zoo.libs.hive.characterizer import skinproxy

UI_MODE_COMPACT = 0
UI_MODE_ADVANCED = 1

HIVE_MODES = ["Hive - Guides Mode", "Hive - Controls Mode", "Hive - Skeleton Mode", "Hive Pre Rig Mode",
              "Hive - Polish Rig Mode"]
BIPED_PIV_ORDER_UI = umeshconstants.BIPED_PIV_ORDER_UI
SECTIONS_UI = umeshconstants.SECTIONS_UI
ZOO_SKIN_PROXY_DICT = umeshconstants.ZOO_SKIN_PROXY_DICT
SECTIONS_UI = umeshconstants.SECTIONS_UI


def stringToVertList(vertString):
    """Converts a string of vertices to a list of vertices
    """
    # Add outer parentheses to make it a tuple of tuples
    s_with_outer_parentheses = "({})".format(vertString)

    # Safely evaluate the string to convert it into a tuple of tuples
    vertList = ast.literal_eval(s_with_outer_parentheses)
    if type(vertList) is not tuple:  # Can be an int if a single value so convert to tuple
        return tuple([vertList])
    return ast.literal_eval(s_with_outer_parentheses)


class UniversalMeshToHive(toolsetwidget.ToolsetWidget):
    id = "universalBipedBuilder"
    info = "Takes a universal mesh and builds a Hive guides/rig."
    uiData = {"label": "Universal Biped Builder (beta)",
              "icon": "saturn",
              "tooltip": "Takes a universal mesh and builds a Hive guides/rig.",
              "defaultActionDoubleClick": False,
              "helpUrl": "https://create3dcharacters.com/maya-tool-universal-biped-builder/"}

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
        self.uiFolderPath = ""  # used for the save directory
        self.universalMeshPressed()

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
        return super(UniversalMeshToHive, self).currentWidget()

    def widgets(self):
        """ Override base method for autocompletion

        :return:
        :rtype: list[GuiAdvanced or GuiCompact]
        """
        return super(UniversalMeshToHive, self).widgets()

    # ------------------
    # UI
    # ------------------

    def _autoAddMeshUI(self):
        """Auto adds the mesh name to the UI"""
        self.properties.meshNameTxt.value = skinproxy.sc.DEFAULT_SKINPROXY_MESH
        self.updateFromProperties()

    def inputProxyGeo(self):
        """Sets the skin proxy geometry"""
        self.properties.meshNameTxt.value = universalmesh.universalMeshUI()
        self.updateFromProperties()

    def _uiToVertDict(self):
        """Converts the UI text boxes to a dictionary of vertices"""
        vertDict = dict()
        count = 0
        for i, sectionPivotOrder in enumerate(BIPED_PIV_ORDER_UI):
            for pivot in sectionPivotOrder:
                vertDict[pivot] = stringToVertList(self.currentWidget().vertPosTxtList[count].text())
                count += 1
        return vertDict

    # ------------------
    # DATA
    # ------------------
    @property
    def defaultBrowserPath(self):
        """Sets the default browser path to /zoo_preferences/assets/hive/universalmeshes"""
        from zoo.preferences.interfaces import hiveinterfaces
        return hiveinterfaces.hiveInterface().defaultUniversalMeshPivotPath()

    def saveJsonToDisk(self):
        """Saves the universal mesh dictionary to disk as a JSON file
        """
        vertDict = self._uiToVertDict()
        if not self.uiFolderPath:
            self.uiFolderPath = self.defaultBrowserPath
        filePath, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save the universal vertex information to disk.",
                                                            self.defaultBrowserPath, "*.json")
        if not filePath:  # cancel
            return
        self.uiFolderPath = os.path.dirname(filePath)  # update the default browser path
        filesystem.saveJson(vertDict, filePath, indent=4, separators=(",", ":"))
        output.displayInfo("File Saved To: {}".format(filePath))

    def _importJsonFromDisk(self, source=True):
        """Imports a JSON file from disk and returns the dictionary"""

        if not self.uiFolderPath:
            self.uiFolderPath = self.defaultBrowserPath

        filePath, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open Universal Vertex From Disk",
                                                            dir=self.uiFolderPath,
                                                            filter="*.json")
        if not filePath:  # cancel
            return {}
        return filesystem.loadJson(filePath)

    def importJsonUI(self):
        """Imports the JSON file from disk and sets the UI text boxes"""
        vertDict = self._importJsonFromDisk()
        if not vertDict:
            return  # import was cancelled
        count = 0
        for i, sectionPivotOrder in enumerate(BIPED_PIV_ORDER_UI):
            for pivot in sectionPivotOrder:
                vertString = str(vertDict.get(pivot, ""))
                vertString = vertString.replace("[", "")
                vertString = vertString.replace("]", "")
                self.currentWidget().vertPosTxtList[count].setText(vertString)
                count += 1

    # ------------------
    # LOGIC
    # ------------------

    def openHiveWindow(self):
        """Opens the Hive window"""
        import zoo.libs.maya.cmds.hotkeys.definedhotkeys as hk
        hk.open_hiveArtistUI()

    def openJointTool(self):
        """Opens the Joint Tool window"""
        import zoo.libs.maya.cmds.hotkeys.definedhotkeys as hk
        hk.open_jointTool()

    @toolsetwidget.ToolsetWidget.undoDecorator
    def buildLocators(self):
        vertDict = self._uiToVertDict()
        # iterate through the dict and check if the values are all ints
        for key, value in vertDict.items():
            if not all(isinstance(x, int) for x in value):
                output.displayWarning("`{}` value is not a number with no decimals, please check.".format(key))

        buildBipedInstc = universalmesh.BuildBipedFromUniversalMesh(meshName=self.properties.meshNameTxt.value)

        meshName = buildBipedInstc.validateMesh()
        self.properties.meshNameTxt.value = meshName  # updates the mesh name to valid mesh
        self.updateFromProperties()
        buildBipedInstc.setVertDict(vertDict)
        buildBipedInstc.setMeshName(self.properties.meshNameTxt.value, message=False)
        buildBipedInstc.buildPivots()

    @toolsetwidget.ToolsetWidget.undoDecorator
    def buildJoints(self):
        buildBipedInstc = universalmesh.BuildBipedFromUniversalMesh(meshName=self.properties.meshNameTxt.value)

        meshName = buildBipedInstc.validateMesh()
        self.properties.meshNameTxt.value = meshName  # updates the mesh name to valid mesh
        self.updateFromProperties()

        buildBipedInstc.setMeshName(self.properties.meshNameTxt.value, message=False)
        buildBipedInstc.buildSkeleton()

    @toolsetwidget.ToolsetWidget.undoDecorator
    def hiveFromJoints(self):
        buildBipedInstc = universalmesh.BuildBipedFromUniversalMesh(meshName=self.properties.meshNameTxt.value)

        meshName = buildBipedInstc.validateMesh()
        self.properties.meshNameTxt.value = meshName  # updates the mesh name to valid mesh
        self.updateFromProperties()

        buildBipedInstc.buildGuides()

    @toolsetwidget.ToolsetWidget.undoDecorator
    def deleteLocators(self):
        buildBipedInstc = universalmesh.BuildBipedFromUniversalMesh(meshName=self.properties.meshNameTxt.value)
        buildBipedInstc.deleteLocators()
        buildBipedInstc.deleteSkeleton()

    def importSkinProxy(self):
        skinproxy.importSkinProxyMesh()
        self._autoAddMeshUI()

    # ------------------
    # CONNECTIONS
    # ------------------

    def universalMeshPressed(self):
        """Add all UI connections here, button clicks, on changed etc"""
        for widget in self.widgets():
            widget.addMeshBtn.clicked.connect(self.inputProxyGeo)
            widget.hiveBtn.clicked.connect(self.openHiveWindow)
            widget.jointToolBtn.clicked.connect(self.openJointTool)
            widget.buildLocatorsBtn.clicked.connect(self.buildLocators)
            widget.buildJointsBtn.clicked.connect(self.buildJoints)
            widget.trashBtn.clicked.connect(self.deleteLocators)
            widget.importSkinProxyBtn.clicked.connect(self.importSkinProxy)
            widget.buildRigBtn.clicked.connect(self.hiveFromJoints)
            widget.saveBtn.clicked.connect(self.saveJsonToDisk)
            widget.importBtn.clicked.connect(self.importJsonUI)


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
        # Mesh Name ---------------------------------------
        tooltip = ("Add a Hive Skin Proxy Mesh or custom Universal Mesh to build from. \n"
                   "This mesh will be used to automatically build pivots. \n"
                   "Use the Import button to import a new Skin Proxy Mesh. \n\n"
                   "If no mesh is added pivots will be created as per the default biped.\n\n"
                   "Customize and save/import your own universal mesh settings in the dropdown section below.")
        self.meshNameTxt = elements.StringEdit(label="Skin Proxy Mesh",
                                               editPlaceholder="skinProxy_geo (optional)",
                                               toolTip=tooltip)
        # Add Mesh Button ---------------------------------------
        tooltip = ("Add the currently selected mesh to the UI \n"
                   "This mesh must be a supported Universal Mesh. \n"
                   "Use the Import button to import a new Skin Proxy Universal Mesh. \n\n"
                   "Customize and save/import your own universal mesh settings in the dropdown section below.")
        self.addMeshBtn = elements.styledButton("",
                                                "arrowLeft",
                                                parent=parent,
                                                toolTip=tooltip,
                                                style=uic.BTN_TRANSPARENT_BG,
                                                minWidth=15)
        # Sub Button Modes ---------------------------------------
        tooltip = ("Build Biped Locator Pivots\n"
                   "Automatically builds pivots from a Universal Mesh, if none exists uses default biped proportions.\n"
                   "Place and adjust the locator pivots before building the Proxy Joints.")
        self.buildLocatorsBtn = elements.AlignedButton("1. Proxy Pivots",
                                                       icon="locator",
                                                       toolTip=tooltip)
        tooltip = ("Builds the Skin Proxy Joints from the Locator Pivots or the Universal Mesh. \n"
                   "If locators or the mesh don't exist the default biped skeleton proportions will be created.\n\n"
                   "The Proxy Joints can be oriented (hands and neck) before building the Hive Rig.")
        self.buildJointsBtn = elements.AlignedButton("2. Proxy Joints",
                                                     icon="hiveJointsToGuides",
                                                     toolTip=tooltip)
        tooltip = "Builds a Hive Guides Rig from existing Skeleton Proxy Joints."
        self.buildRigBtn = elements.AlignedButton("3. Hive Rig",
                                                  icon="man",
                                                  toolTip=tooltip)
        # Hive Button --------------------------------------
        tooltip = "Open The Hive UI"
        self.hiveBtn = elements.styledButton("",
                                             icon="hive",
                                             toolTip=tooltip,
                                             style=uic.BTN_DEFAULT,
                                             parent=parent)
        # Joint Tool Button --------------------------------------
        tooltip = "Open The Joint Tool UI, for orienting joints."
        self.jointToolBtn = elements.styledButton("",
                                                  icon="skeleton",
                                                  toolTip=tooltip,
                                                  style=uic.BTN_DEFAULT,
                                                  parent=parent)
        # Trash Button --------------------------------------
        tooltip = "Deletes the Locator Pivots and Proxy Joints"
        self.trashBtn = elements.styledButton("",
                                              icon="trash",
                                              toolTip=tooltip,
                                              style=uic.BTN_DEFAULT,
                                              parent=parent)
        # Import Skin Proxy ---------------------------------------
        tooltip = "Import a skin proxy mesh into the scene."
        self.importSkinProxyBtn = elements.styledButton("",
                                                        parent=parent,
                                                        icon="importArrow",
                                                        toolTip=tooltip,
                                                        style=uic.BTN_DEFAULT)
        # Save ---------------------------------------
        tooltip = "Save the Universal Mesh vertex pivot information to disk."
        self.saveBtn = elements.AlignedButton("Save Universal Pivots",
                                              icon="save",
                                              toolTip=tooltip)
        # import ---------------------------------------
        tooltip = "Import the Universal Mesh vertex pivot information from disk."
        self.importBtn = elements.AlignedButton("Import Universal Pivots",
                                                icon="importArrow",
                                                toolTip=tooltip)

        # BUILD MESH TEXTBOXES ---------------------------------------
        self.vertPosTxtList = list()
        self.addVertBtns = list()
        # Import Skin Proxy ---------------------------------------
        pivotTooltip = "Select vertices/edges/faces on the mesh to set the pivot position of"
        textTooltip = "Vertices numbers that mark the center pivot position of the"
        for sectionPivotOrder in BIPED_PIV_ORDER_UI:
            for pivot in sectionPivotOrder:
                verts = ZOO_SKIN_PROXY_DICT[pivot]
                vertString = str(verts).replace("[", "")
                vertString = vertString.replace("]", "")
                txt = elements.StringEdit(label="", editText=vertString,
                                          toolTip="{} {}.".format(textTooltip, pivot))
                self.vertPosTxtList.append(txt)
                btn = elements.styledButton("",
                                            "arrowLeft",
                                            parent=parent,
                                            toolTip="{} {}.".format(pivotTooltip, pivot),
                                            style=uic.BTN_TRANSPARENT_BG,
                                            minWidth=15)
                self.addVertBtns.append(btn)
                btn.clicked.connect(partial(self.addVertClicked, txt))

    def addVertClicked(self, stringEdit):
        """Connection: Adds the vertex selection to the stringEdit text box"""
        vertexSel = universalmesh.vertextSelection()
        vertString = str(vertexSel).replace("[", "")
        vertString = vertString.replace("]", "")
        stringEdit.setText(vertString)


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
        # Universal Mesh Text Layout ---------------------------------------
        universalMeshLayout = elements.hBoxLayout(self, margins=(0, 0, 0, 0), spacing=uic.SPACING)
        universalMeshLayout.addWidget(self.meshNameTxt, 10)
        universalMeshLayout.addWidget(self.addMeshBtn, 1)
        universalMeshLayout.addWidget(self.hiveBtn, 1)
        universalMeshLayout.addWidget(self.jointToolBtn, 1)
        universalMeshLayout.addWidget(self.trashBtn, 1)
        universalMeshLayout.addWidget(self.importSkinProxyBtn, 1)

        # Text Boxes Layout ---------------------------------------
        vertPivotLayout = elements.vBoxLayout(self, margins=(uic.SMLPAD, 0, uic.SMLPAD, 0), spacing=uic.SPACING)
        count = 0
        for i, sectionPivotOrder in enumerate(BIPED_PIV_ORDER_UI):
            collapsable = elements.CollapsableFrameThin(SECTIONS_UI[i], collapsed=True, parent=parent)
            collapsable.toggled.connect(toolsetWidget.treeWidget.updateTree)  # toggle connection behaviour
            collapsable.toggled.connect(toolsetWidget.treeWidget.updateTree)  # two refreshes as nested collapsable
            vertPivotLayout.addWidget(collapsable)
            for pivot in sectionPivotOrder:
                textLayout = elements.hBoxLayout(self, margins=(uic.REGPAD, 0, uic.REGPAD, 0), spacing=uic.SPACING)
                textTooltip = "Vertices numbers that mark the center pivot position of the"
                textLayout.addWidget(elements.Label(text=pivot,
                                                    toolTip="{} {}.".format(textTooltip, pivot)), 10)
                textLayout.addWidget(self.vertPosTxtList[count], 20)
                textLayout.addWidget(self.addVertBtns[count], 1)
                collapsable.hiderLayout.addLayout(textLayout)
                count += 1

        # save layout ---------------------------------------
        saveLayout = elements.hBoxLayout(self, margins=(uic.SMLPAD, uic.SMLPAD, uic.SMLPAD, uic.SMLPAD),
                                         spacing=uic.SPACING)
        saveLayout.addWidget(self.saveBtn, 1)
        saveLayout.addWidget(self.importBtn, 1)

        # Button Layout ---------------------------------------
        btnLayout = elements.hBoxLayout(self, margins=(0, uic.SMLPAD, 0, 0), spacing=uic.SPACING)
        btnLayout.addWidget(self.buildLocatorsBtn, 1)
        btnLayout.addWidget(self.buildJointsBtn, 1)
        btnLayout.addWidget(self.buildRigBtn, 1)

        # Main pivot collapsable ---------------------------------------
        pivotCollapsable = elements.CollapsableFrameThin("UNIVERSAL MESH PIVOTS (optional)",
                                                         collapsed=True,
                                                         parent=parent)
        pivotCollapsable.toggled.connect(toolsetWidget.treeWidget.updateTree)  # toggle connection behaviour
        pivotCollapsable.hiderLayout.addLayout(saveLayout)
        pivotCollapsable.hiderLayout.addLayout(vertPivotLayout)

        # Add To Main Layout ---------------------------------------
        mainLayout.addLayout(universalMeshLayout)
        mainLayout.addWidget(pivotCollapsable)
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
        mainLayout.addWidget(self.meshNameTxt)
        mainLayout.addWidget(self.universalMeshToGuidesBtn)
