""" ---------- Build Biped From Skeleton -------------
Builds a Hive biped guide-rig from a skeleton.


"""
import os

from zoovendor.Qt import QtWidgets, QtCore

from zoo.libs.utils import output, filesystem
from zoo.libs.maya.cmds.filemanage import saveexportimport
from zoo.apps.toolsetsui.widgets import toolsetwidget
from zoo.libs.pyqt import utils, uiconstants as uic
from zoo.libs.pyqt.widgets import elements
from zoo.libs import iconlib
from zoo.libs.maya.cmds.workspace import mayaworkspace
from zoo.apps.toolsetsui.widgets.toolsetresizer import ToolsetResizer
from zoo.libs.maya.cmds.animation import mocap
from zoo.libs.maya.cmds.objutils import selection

from zoo.libs.hive.library.matching import matchconstants as mc
from zoo.libs.hive.library.matching import matchguides

HIVE_IDS = [mc.HIVE_IDS[0]]  # list of tuples, name and hive id dictionary, NOTE only Hive Standard for now
SKELETONS = mc.SKELETONS  # list of tuples, name and skeleton id dictionary

# Table imports -----------------
from zoo.libs.pyqt.extended import tableviewplus
from zoo.libs.pyqt.models import tablemodel, delegates
from zoo.libs.pyqt.models import datasources, constants

UI_MODE_COMPACT = 0
UI_MODE_ADVANCED = 1

# TODO change


ALL_MAPPINGS = [{"Hive Biped Controls": {"nodes": [], "options": []}},
                {"Hive Biped Light Ctrls": {"nodes": [], "options": []}}]

TIME_RANGE_COMBO_LIST = ["Playback Range", "Full Animation Range", "Custom Frame Range"]
ITEMS_LIST_KEY = "itemsList"
OPTIONS_DICT_KEY = "optionsDict"


class BuildBipedFromSkeleton(toolsetwidget.ToolsetWidget):
    id = "buildRigFromSkeleton"
    info = "Builds a Hive guide-rig from a skeleton."
    uiData = {"label": "Build Rig From Skeleton (beta)",
              "icon": "man",
              "tooltip": "Builds a Hive biped guide-rig from a skeleton.",
              "defaultActionDoubleClick": False,
              "helpUrl": "https://create3dcharacters.com/maya-tool-build-rig-from-skeleton/"}

    # ------------------
    # STARTUP
    # ------------------

    def preContentSetup(self):
        """First code to run, treat this as the __init__() method"""
        self.toolsetWidget = self  # needed for table resizer widget
        self.progress = 0  # progress bar value

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
        self.uiFolderPath = ""  # used for saving and loading UI settings
        # self.importSceneDataToUI()  # imports the scene data to the UI if it exists

        self.leftRightCheckboxChanged()  # disable the l/r UI elements when the Auto Right Side checkbox is checked off
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
        return super(BuildBipedFromSkeleton, self).currentWidget()

    def widgets(self):
        """ Override base method for autocompletion

        :return:
        :rtype: list[GuiAdvanced or GuiCompact]
        """
        return super(BuildBipedFromSkeleton, self).widgets()

    # ------------------
    # UI
    # ------------------

    def enterEvent(self, event):
        """Update selection on enter event
        """
        self.updateFromProperties()

    def leftRightCheckboxChanged(self):
        """Disable the left and right UI elements when the Auto Right Side checkbox is checked off"""
        state = self.properties.autoLeftRightCheck.value
        self.compactWidget.sourceLeft.setEnabled(state)
        self.compactWidget.sourceRight.setEnabled(state)
        self.compactWidget.sourceLRAlwaysSuffix.setEnabled(state)
        self.compactWidget.sourceLRAlwaysPrefix.setEnabled(state)
        self.compactWidget.sourceLRSeparatorOnBorder.setEnabled(state)

    def resetUiDefaults(self):
        """Resets the UI to the default settings"""
        self.properties.sourceNamespace.value = ""
        self.properties.sourceLeft.value = "_L"
        self.properties.sourceRight.value = "_R"
        self.properties.sourceLRAlwaysPrefix.value = False
        self.properties.sourceLRAlwaysSuffix.value = False
        self.properties.sourceLRSeparatorOnBorder.value = False
        self.properties.sourcePrefix.value = ""
        self.properties.sourceSuffix.value = ""
        self.properties.autoLeftRightCheck.value = False
        self.properties.maintainOffsetCheck.value = True
        self.properties.includeScaleCheck.value = False
        self.properties.sourceCombo.value = 0
        self.properties.targetCombo.value = 0
        # todo time range
        # Clear Table
        self.compactWidget.tableControl.clear()
        # Update enable disable states
        self.leftRightCheckboxChanged()
        # Update all data
        self.updateFromProperties()

    # ------------------
    # JSON IMPORT EXPORT
    # ------------------
    @property
    def defaultBrowserPath(self):
        """Sets the default browser path to the Maya project data directory or the current scene directory"""

        outputDirectory = os.path.expanduser("~")
        # find the current Maya project data directory if it exists
        if mayaworkspace.getCurrentMayaWorkspace():
            dataDir = mayaworkspace.getProjSubDirectory("data")
            if dataDir:
                outputDirectory = dataDir
        else:
            if not saveexportimport.isCurrentSceneUntitled():
                currentScenePath = saveexportimport.currentSceneFilePath()
                outputDirectory = os.path.dirname(currentScenePath)
        return outputDirectory

    def _globalOptionsDict(self):
        optionsDict = dict()
        optionsDict["autoRightSide"] = self.properties.autoLeftRightCheck.value
        optionsDict["maintainOffset"] = self.properties.maintainOffsetCheck.value
        optionsDict["scaleConstrain"] = self.properties.includeScaleCheck.value
        return optionsDict

    def _sourceDict(self):
        sourceItemsList = self.compactWidget.tableControl.allData()[0]

        optionsDict = self._globalOptionsDict()
        optionsDict["namespace"] = self.properties.sourceNamespace.value
        optionsDict["leftIdentifier"] = self.properties.sourceLeft.value
        optionsDict["rightIdentifier"] = self.properties.sourceRight.value
        optionsDict["leftRightUnderscore"] = self.properties.sourceLRSeparatorOnBorder.value
        optionsDict["leftRightPrefix"] = self.properties.sourceLRAlwaysPrefix.value
        optionsDict["leftRightSuffix"] = self.properties.sourceLRAlwaysSuffix.value
        optionsDict["prefix"] = self.properties.sourcePrefix.value
        optionsDict["suffix"] = self.properties.sourceSuffix.value

        exportDict = {ITEMS_LIST_KEY: sourceItemsList, OPTIONS_DICT_KEY: optionsDict}
        return exportDict

    def _targetDict(self):
        targetItemsList = self.compactWidget.tableControl.allData()[1]

        optionsDict = self._globalOptionsDict()

        exportDict = {ITEMS_LIST_KEY: targetItemsList, OPTIONS_DICT_KEY: optionsDict}
        return exportDict

    def _setSourceOptionsDictToUI(self, optionsDict):
        self.properties.sourceNamespace.value = optionsDict["namespace"]
        self.properties.sourceLeft.value = optionsDict["leftIdentifier"]
        self.properties.sourceRight.value = optionsDict["rightIdentifier"]
        self.properties.sourceLRSeparatorOnBorder.value = optionsDict["leftRightUnderscore"]
        self.properties.sourceLRAlwaysPrefix.value = optionsDict["leftRightPrefix"]
        self.properties.sourceLRAlwaysSuffix.value = optionsDict["leftRightSuffix"]
        self.properties.sourcePrefix.value = optionsDict["prefix"]
        self.properties.sourceSuffix.value = optionsDict["suffix"]
        self.updateFromProperties()

    def _setTargetOptionsDictToUI(self, optionsDict):
        self.properties.autoLeftRightCheck.value = optionsDict["autoRightSide"]
        self.updateFromProperties()

    def exportColumns(self):
        """Exports the source column to a file on disk."""
        sourceDict = self._sourceDict()
        if not sourceDict[ITEMS_LIST_KEY]:
            output.displayWarning("No Source Objects Found in the Table.  Please Add Some Objects.")
            return
        self._saveJsonToDisk(sourceDict, source=True)

    def _saveJsonToDisk(self, aDict, source=True):
        """Save a dictionary to disk as a JSON file

        :param aDict: A python dictionary to save to disk, will be the source or target dictionary
        :type aDict: dict
        """
        txt = "Target Column"
        if source:
            txt = "Source Column"
        if not self.uiFolderPath:
            self.uiFolderPath = self.defaultBrowserPath
        filePath, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save the {} To Disk".format(txt),
                                                            self.defaultBrowserPath, "*.json")
        if not filePath:  # cancel
            return
        self.uiFolderPath = os.path.dirname(filePath)  # update the default browser path
        filesystem.saveJson(aDict, filePath, indent=4, separators=(",", ":"))
        output.displayInfo("{} File Saved To: {}".format(txt, filePath))

    def importColumns(self):
        """Imports the source column from a file on disk."""
        sourceDict = self._importJsonFromDisk(self.defaultBrowserPath)
        if not sourceDict:
            return
        # set the source column to the UI
        self.compactWidget.tableControl.updateSourcesFromDictList(sourceDict[ITEMS_LIST_KEY])
        self._setSourceOptionsDictToUI(sourceDict[OPTIONS_DICT_KEY])
        self.leftRightCheckboxChanged()  # disable the l/r UI elements when the Auto Right Side checkbox is checked off

    def _importJsonFromDisk(self, source=True):
        """Imports a JSON file from disk and returns the dictionary"""
        txt = "Target Column"
        if source:
            txt = "Source Column"

        if not self.uiFolderPath:
            self.uiFolderPath = self.defaultBrowserPath

        filePath, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open {} Data From Disk".format(txt),
                                                            dir=self.uiFolderPath,
                                                            filter="*.json")
        if not filePath:  # cancel
            return {}
        return filesystem.loadJson(filePath)

    def saveUItoScene(self):
        """Saves the UI settings to the scene as a network node with string attributes"""
        sourceDict = self._sourceDict()
        targetDict = self._targetDict()
        # mocap.setMatchAndBakeToScene(sourceDict, targetDict)

    def deleteBuildSceneNode(self):
        """Deletes the info network node from the scene.  This is the node that remembers the UI settings"""
        pass

    def importSceneDataToUI(self):
        """Imports the scene data to the UI from the info network node, if it doesn't exist do nothing."""
        pass
        return
        sourceDict, targetDict = mocap.matchAndBakeDataFromScene()
        if not sourceDict or not targetDict:
            return  # nothing found
        self.compactWidget.tableControl.updateSourcesFromDictList(sourceDict[ITEMS_LIST_KEY])
        self.compactWidget.tableControl.updateTargetsFromDictList(targetDict[ITEMS_LIST_KEY])
        self._setSourceOptionsDictToUI(sourceDict[OPTIONS_DICT_KEY])
        self._setTargetOptionsDictToUI(targetDict[OPTIONS_DICT_KEY])

        self.leftRightCheckboxChanged()  # disable the l/r UI elements when the Auto Right Side checkbox is checked off

        self.updateFromProperties()

    # ------------------
    # UI
    # ------------------

    def update_progress(self, progress, message):
        """Update the progress bar

        :param progress: The progress value 0-6
        :type progress: int
        :param message: The message to display
        :type message: str
        """
        output.displayInfo("-------------------")
        output.displayInfo(message)
        output.displayInfo("-------------------")
        # Update Message ---------------------------------------
        self.compactWidget.progressMessageLabel.setText(message)
        self.updateFromProperties()
        # Progress Bar ---------------------------------------
        self.compactWidget.progressBarWidget.setValue(progress)
        if progress == 100:
            self.compactWidget.progressDivider.setVisible(False)
            self.compactWidget.progressBarWidget.setVisible(False)
            self.compactWidget.progressMessageLabel.setVisible(False)
            output.displayInfo(message)  # Rig completed
            self.toolsetWidget.treeWidget.updateTree()
            self.toolsetWidget.treeWidget.updateTree()  # needed twice to update the tree
            return
        elif progress == 0:
            self.compactWidget.progressDivider.setVisible(True)
            self.compactWidget.progressBarWidget.setVisible(True)
            self.compactWidget.progressMessageLabel.setVisible(True)
            self.toolsetWidget.treeWidget.updateTree()
            self.toolsetWidget.treeWidget.updateTree()  # needed twice to update the tree

    # ------------------
    # LOGIC
    # ------------------

    def presetNames(self):
        sourceNames = self.compactWidget.tableControl.presetSourceNames
        targetNames = self.compactWidget.tableControl.presetTargetNames
        sourcePreset = sourceNames[self.properties.sourceCombo.value]
        targetPreset = targetNames[self.properties.targetCombo.value]
        return sourcePreset, targetPreset

    def applySourcesPreset(self):
        """Updates from the source preset combo box"""
        sourcePreset, targetPreset = self.presetNames()
        self.compactWidget.tableControl.updateSourcesFromPreset(sourcePreset, targetPreset)

    def applyTargetsPreset(self):
        """Updates from the source preset combo box"""
        sourcePreset, targetPreset = self.presetNames()
        self.compactWidget.tableControl.updateTargetsFromPreset(sourcePreset, targetPreset)

    def _updateBuildInstance(self):
        """Updates the batch bake instance with the latest settings"""
        sourceJointsList, targetHiveIdsList = self.compactWidget.tableControl.allData()
        # self.batchBakeInstance = buildHiveFromSkeleton.BuildHiveFromSkeleton()

    def validateObjects(self):
        """Validates the objects in the table, returns a list of errors"""
        self._updateBuildInstance()
        return
        self.batchBakeInstance.printValidateObjects()

    def openHiveWindow(self):
        """Opens the Hive window"""
        import zoo.libs.maya.cmds.hotkeys.definedhotkeys as hk
        hk.open_hiveArtistUI()

    def buildRigFromSkeleton(self):
        """Builds the rig from the skeleton"""
        self._updateBuildInstance()
        rigName = "biped"
        sourceJointsList, targetHiveIdsList = self.compactWidget.tableControl.allData()
        buildMatchInstance = matchguides.BuildMatchGuidesSkele(sourceJointsList,
                                                               targetHiveIdsList,
                                                               order=self.compactWidget.tableControl.hiveOrder,
                                                               rigName=rigName,
                                                               sourceNamespace=self.properties.sourceNamespace.value,
                                                               sourcePrefix=self.properties.sourcePrefix.value,
                                                               sourceSuffix=self.properties.sourceSuffix.value)

        self.update_progress(0, "Status: Running Basic Checks.")
        buildMatchInstance.stage1_basicChecks()

        self.update_progress(10, "Status: Building the Hive Guide Template.")
        buildMatchInstance.stage2_BuildRig()

        self.update_progress(25, "Status: Matching Guides To The Skeleton.")
        buildMatchInstance.stage3_MatchGuides()

        self.update_progress(40, "Status: Aligning The Controls and Symmetry.")
        buildMatchInstance.stage4_FinalAlignment()

        self.update_progress(70, "Status: Matching Hive Skeleton Twist and Spine Counts.")
        buildMatchInstance.stage5_TwistSpineCount()

        self.update_progress(100, "Status: Matched Hive guides to skeleton successfully.")
        output.displayInfo("Success: Matched Hive guides to skeleton successfully.")

    # ------------------
    # CONNECTIONS
    # ------------------

    def uiConnections(self):
        """Add all UI connections here, button clicks, on changed etc"""
        for widget in self.widgets():
            widget.buildFromSkeleBtn.clicked.connect(self.buildRigFromSkeleton)
            widget.sourceCombo.itemChanged.connect(self.applySourcesPreset)
            widget.targetCombo.itemChanged.connect(self.applyTargetsPreset)
            # Auto checkbox changed --------------
            widget.autoLeftRightCheck.stateChanged.connect(self.leftRightCheckboxChanged)
            # Connect Table Functions ------------------
            widget.addButton.clicked.connect(widget.tableControl.onAdd)
            widget.clearButton.clicked.connect(widget.tableControl.clear)
            widget.removeButton.clicked.connect(widget.tableControl.removeSelected)
            widget.swapButton.clicked.connect(widget.tableControl.swapSelected)
            widget.hiveBtn.clicked.connect(self.openHiveWindow)
            # Connect Table Functions ------------------
            widget.validateBtn.addAction("Validate Names In Script Editor",
                                         mouseMenu=QtCore.Qt.LeftButton,
                                         icon=iconlib.icon("list"),
                                         connect=self.validateObjects)
            widget.dotsMenuButton.addAction("UI - Save Data To Scene (Remember)",
                                            mouseMenu=QtCore.Qt.LeftButton,
                                            icon=iconlib.icon("save"),
                                            connect=self.saveUItoScene)
            widget.dotsMenuButton.addAction("UI - Delete Data From Scene (Forget)",
                                            mouseMenu=QtCore.Qt.LeftButton,
                                            icon=iconlib.icon("trash"),
                                            connect=self.deleteBuildSceneNode)
            widget.dotsMenuButton.addAction("UI - Import Data From Scene",
                                            mouseMenu=QtCore.Qt.LeftButton,
                                            icon=iconlib.icon("lightPush"),
                                            connect=self.importSceneDataToUI)
            widget.dotsMenuButton.addAction("UI - Reset To Defaults",
                                            mouseMenu=QtCore.Qt.LeftButton,
                                            icon=iconlib.icon("reloadWindows"),
                                            connect=self.resetUiDefaults)
            widget.dotsMenuButton.addAction("Export - Columns To Disk (JSON)",
                                            mouseMenu=QtCore.Qt.LeftButton,
                                            icon=iconlib.icon("save"),
                                            connect=self.exportColumns)
            widget.dotsMenuButton.addAction("Import - Columns From Disk (JSON)",
                                            mouseMenu=QtCore.Qt.LeftButton,
                                            icon=iconlib.icon("openFolder01"),
                                            connect=self.importColumns)


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
        self.parentVar = parent
        self.toolsetWidget = toolsetWidget
        self.properties = properties
        tooltip = "Will automatically try to also find the right side of the given objects. \n" \
                  "See `Source/Target Rename Options` to set the left/right settings. \n" \
                  "Useful for matching full rig setups."
        self.autoLeftRightCheck = elements.CheckBox(label="Auto Right Side",
                                                    checked=True,
                                                    toolTip=tooltip,
                                                    parent=parent)
        # Source ---------------------------------------
        tooltip = "Specify the namespace to be added to all source names. \n\n" \
                  "  - Example: `characterX` will be added to the name eg `characterX:pCube1`"
        self.sourceNamespace = elements.StringEdit(label="Namespace",
                                                   editPlaceholder="characterX:",
                                                   toolTip=tooltip,
                                                   parent=parent)
        tooltipLR = "Specify the left and right identifiers. `Auto Right Side` must be on.\n\n" \
                    "  - Example: `_L`, `_R` \n" \
                    "  - `pCube1_L_geo` finds `pCube1_R_geo`"
        self.sourceLeft = elements.StringEdit(label="Left Right ID",
                                              editText="_L",
                                              toolTip=tooltipLR,
                                              parent=parent)
        self.sourceRight = elements.StringEdit(label="",
                                               editText="_R",
                                               toolTip=tooltipLR,
                                               parent=parent)
        tooltipForcePrefix = "Forces the left right identifier to always prefix the name. \n" \
                             "`Auto Right Side` must be on. \n\n" \
                             "  - Example: `l`, `r` \n" \
                             "  - `lpSphere1` finds `rpSphere1`"
        self.sourceLRAlwaysPrefix = elements.CheckBox(label="L-R Is Prefix",
                                                      checked=False,
                                                      toolTip=tooltipForcePrefix,
                                                      parent=parent,
                                                      right=True)
        tooltipForceSuffix = "Forces the left right identifier to always suffix the name. \n" \
                             "`Auto Right Side` must be on.\n\n" \
                             "  - Example: `l`, `r` \n" \
                             "  - `pSphere1l` finds `rpSpherer`"
        self.sourceLRAlwaysSuffix = elements.CheckBox(label="L-R Is Suffix",
                                                      checked=False,
                                                      toolTip=tooltipForceSuffix,
                                                      parent=parent,
                                                      right=True)
        tooltipBorder = "While finding the right side an underscore must be on the left or right side of the name. \n" \
                        "`Auto Right Side` must be on.\n\n" \
                        "  - Example: `l`, `r` \n" \
                        "  - `pCube1_l` finds `pCube1_r` \n" \
                        "  or \n" \
                        "  - `l_pCube1` finds `r_pCube1`"
        self.sourceLRSeparatorOnBorder = elements.CheckBox(label="Separator On Border",
                                                           checked=False,
                                                           toolTip=tooltipBorder,
                                                           parent=parent,
                                                           right=True)

        tooltip = "Specify the prefix to be added to all source names. \n\n" \
                  "  - Example: `xxx_` will be added to the name eg `xxx_pCube1`"
        self.sourcePrefix = elements.StringEdit(label="Prefix",
                                                editPlaceholder="xxx_",
                                                toolTip=tooltip,
                                                labelRatio=3,
                                                editRatio=6,
                                                parent=parent)
        tooltip = "Specify the suffix to be added to all source names. \n\n" \
                  "  - Example: `xxx_` will be added to the name eg `pCube1_xxx`"
        self.sourceSuffix = elements.StringEdit(label="Suffix",
                                                editPlaceholder="_xxx",
                                                toolTip=tooltip,
                                                labelRatio=3,
                                                editRatio=6,
                                                parent=parent)
        # Constrain And Bake Btn ---------------------------------------
        tooltip = "Builds a Hive rig from a given skeleton type in the scene. \n" \
                  "The source joints are matched to the target Hive guides IDs. \n\n" \
                  "Use the Name Options to add namespaces, prefixes and left/right identifiers."
        self.buildFromSkeleBtn = elements.styledButton("Build Hive Guide-Rig From Skeleton",
                                                       icon="man",
                                                       toolTip=tooltip,
                                                       style=uic.BTN_DEFAULT,
                                                       parent=parent)

        # Swap Table --------------------------------------
        self.tableWidget(parent)  # creates the table widget

        # Resizer widget ----------------------------------
        self.resizerWidget = ToolsetResizer(parent=self,
                                            toolsetWidget=self.toolsetWidget,
                                            target=self.definitionTree,
                                            margins=(0, 3, 0, 10))

        # Combo Presets --------------------------------------
        # Must build after the table
        self.sourceCombo = elements.ComboBoxSearchable(text="",
                                                       items=self.tableControl.presetSourceNames,
                                                       toolTip=tooltip,
                                                       parent=parent)
        self.targetCombo = elements.ComboBoxSearchable(text="",
                                                       items=self.tableControl.presetTargetNames,
                                                       toolTip=tooltip,
                                                       parent=parent)
        # Validate Button --------------------------------------
        tooltip = "Check object names by printing to the script editor. \n" \
                  "Names will get validated if they exist in the scene."
        self.validateBtn = elements.styledButton("",
                                                 icon="list",
                                                 toolTip=tooltip,
                                                 style=uic.BTN_DEFAULT,
                                                 parent=parent)
        self.validateBtn.setVisible(False)
        # Hive Button --------------------------------------
        tooltip = "Open The Hive UI"
        self.hiveBtn = elements.styledButton("",
                                             icon="hive",
                                             toolTip=tooltip,
                                             style=uic.BTN_DEFAULT,
                                             parent=parent)
        # ---------------- COLLAPSABLES ------------------
        self.sourceCollapsable = elements.CollapsableFrameThin("Source Joints - Name Options",
                                                               contentMargins=(uic.SREG, uic.SREG, uic.SREG, uic.SREG),
                                                               contentSpacing=uic.SLRG,
                                                               collapsed=True,
                                                               parent=parent)
        # Progress Bar ---------------------------------------
        self.progressDivider = elements.Divider(parent=parent)
        self.progressBarWidget = QtWidgets.QProgressBar(parent=parent)
        self.progressBarWidget.setMinimum(0)
        self.progressBarWidget.setMaximum(100)
        self.progressBarWidget.setStyleSheet("""
                            QProgressBar {
                                border: 2px #474747;
                                border-radius: 5px;
                                text-align: center;
                                background-color: #656565;
                                color: black; /* Set the text color to black */
                            }
                            QProgressBar::chunk {
                                background-color: #73bbd3; /* Hex color */
                                width: 20px;
                                border: 2px #474747;
                            }
                        """)
        self.progressMessageLabel = elements.Label("Status: Waiting For User Input",
                                                   parent=parent)
        self.progressMessageLabel.setAlignment(QtCore.Qt.AlignCenter)
        # Set the progress bar to invisible -------------------------
        self.progressDivider.setVisible(False)
        self.progressBarWidget.setVisible(False)
        self.progressMessageLabel.setVisible(False)

    def tableWidget(self, parent):
        # Build the table tree --------------------------------------------
        self.definitionTree = tableviewplus.TableViewPlus(manualReload=False, searchable=False, parent=parent)

        self.userModel = tablemodel.TableModel(parent=parent)
        self.tableControl = Controller(self.userModel, self.definitionTree, parent=parent)
        self.definitionTree.setModel(self.userModel)
        self.definitionTree.tableView.verticalHeader().hide()
        self.definitionTree.tableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.definitionTree.tableView.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.definitionTree.registerRowDataSource(SourceColumn(self.tableControl, headerText="Source Joints"))
        self.definitionTree.registerColumnDataSources([TargetColumn(headerText="Matching Hive Guides")])

        self.tableControl.clear()  # refresh updates the table
        self.definitionTree.tableView.horizontalHeader().resizeSection(0, utils.dpiScale(180))
        self.definitionTree.tableView.horizontalHeader().resizeSection(1, utils.dpiScale(180))
        # Dots menu button, export, import. --------------------------------------
        tooltip = ("Misc Settings: \n"
                   " - Save and import settings to the scene: Saves data to a node named `zooSkeleToRig_networkNode`.\n"
                   " - Delete the settings from the scene. Deletes the `zooSkeleToRig_networkNode`.\n"
                   " - Reset the UI to Defaults \n"
                   " - Import and Export column data to disk (JSON).")
        self.dotsMenuButton = elements.styledButton("",
                                                    icon="menudots",
                                                    toolTip=tooltip,
                                                    style=uic.BTN_TRANSPARENT_BG,
                                                    parent=parent)
        self.dotsMenuButton.setVisible(False)
        # Clear/Add/Remove/Swap Row Buttons --------------------------------------
        tooltip = "Clears all the rows in the table."
        self.clearButton = elements.styledButton("",
                                                 icon="checkListDel",
                                                 toolTip=tooltip,
                                                 style=uic.BTN_TRANSPARENT_BG,
                                                 parent=parent)
        tooltip = "Adds new row. \n" \
                  "Select objects sources and then targets to add to the table.\n" \
                  "Can select multiple sources and then multiple targets."
        self.addButton = elements.styledButton("",
                                               icon="plus",
                                               toolTip=tooltip,
                                               style=uic.BTN_TRANSPARENT_BG,
                                               parent=parent)
        tooltip = "Removes the selected row/s. from the table"
        self.removeButton = elements.styledButton("",
                                                  icon="minusSolid",
                                                  toolTip=tooltip,
                                                  style=uic.BTN_TRANSPARENT_BG,
                                                  parent=parent)
        tooltip = "Swaps the selected row/s so the source becomes the target and vice versa."
        self.swapButton = elements.styledButton("",
                                                icon="reverseCurves",
                                                toolTip=tooltip,
                                                style=uic.BTN_TRANSPARENT_BG,
                                                parent=parent)
        self.swapButton.setVisible(False)
        tooltip = "Shuffle the selected rows up."
        self.shuffleUpButton = elements.styledButton("",
                                                     icon="arrowSingleUp",
                                                     toolTip=tooltip,
                                                     style=uic.BTN_TRANSPARENT_BG,
                                                     parent=parent)
        self.shuffleUpButton.setVisible(False)
        tooltip = "Shuffle the selected rows down."
        self.shuffleDownButton = elements.styledButton("",
                                                       icon="arrowSingleDown",
                                                       toolTip=tooltip,
                                                       style=uic.BTN_TRANSPARENT_BG,
                                                       parent=parent)
        self.shuffleDownButton.setVisible(False)


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
        # Checkbox Layout ---------------------------------------
        checkboxLayout = elements.hBoxLayout(self, margins=(uic.SREG, uic.SREG, uic.SREG, uic.SREG), spacing=uic.SREG)
        checkboxLayout.addWidget(self.autoLeftRightCheck, 1)

        # Source ---------------------------------------
        sourceNamespaceLayout = elements.hBoxLayout(self, margins=(0, 0, 0, 0), spacing=uic.SREG)
        sourceNamespaceLayout.addWidget(self.sourceNamespace, 15)
        sourceNamespaceLayout.addWidget(self.sourceLeft, 10)
        sourceNamespaceLayout.addWidget(self.sourceRight, 5)

        sourceCheckboxLayout = elements.hBoxLayout(self, margins=(0, 0, 0, 0), spacing=uic.SREG)
        sourceCheckboxLayout.addWidget(self.sourceLRAlwaysPrefix, 1)
        sourceCheckboxLayout.addWidget(self.sourceLRAlwaysSuffix, 1)
        sourceCheckboxLayout.addWidget(self.sourceLRSeparatorOnBorder, 1)

        sourcePrefixSufixLayout = elements.hBoxLayout(self, margins=(0, 0, 0, 0), spacing=uic.SREG)
        sourcePrefixSufixLayout.addWidget(self.sourcePrefix, 1)
        sourcePrefixSufixLayout.addWidget(self.sourceSuffix, 1)

        # Combos ---------------------------------------
        combosLayout = elements.hBoxLayout(self, margins=(0, 0, 0, 0), spacing=uic.SREG)
        combosLayout.addWidget(self.sourceCombo, 1)
        combosLayout.addWidget(self.targetCombo, 1)

        # Table and add/remove/swap buttons ---------------------------------------
        tableLayout = elements.vBoxLayout()
        tableLayout.addWidget(self.definitionTree)

        # Table button layout ---------------------------------------
        tableButtonLayout = elements.hBoxLayout(self, margins=(0, 0, 0, 0), spacing=uic.SSML)
        buttonSpacer = QtWidgets.QSpacerItem(1000, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        tableButtonLayout.addWidget(self.dotsMenuButton, 1)
        tableButtonLayout.addWidget(self.addButton, 1)
        tableButtonLayout.addWidget(self.removeButton, 1)
        tableButtonLayout.addWidget(self.clearButton, 1)
        tableButtonLayout.addWidget(self.swapButton, 1)
        tableButtonLayout.addWidget(self.shuffleUpButton, 1)
        tableButtonLayout.addWidget(self.shuffleDownButton, 1)
        tableButtonLayout.addItem(buttonSpacer)

        # Buttons ---------------------------------------
        buttonLayout = elements.hBoxLayout(self, margins=(0, 0, 0, 0), spacing=uic.SPACING)
        buttonLayout.addWidget(self.buildFromSkeleBtn, 20)
        buttonLayout.addWidget(self.validateBtn, 1)
        buttonLayout.addWidget(self.hiveBtn, 1)

        # Button vertical layout ---------------------------------------
        vertButtonLayout = elements.vBoxLayout(self, margins=(0, 0, 0, 0), spacing=uic.SPACING)
        vertButtonLayout.addLayout(buttonLayout)

        #  Flip Collapsable ---------------------------------------
        #  Target Collapsable ---------------------------------------
        self.sourceCollapsable.hiderLayout.addLayout(sourceNamespaceLayout)
        self.sourceCollapsable.hiderLayout.addLayout(sourceCheckboxLayout)
        self.sourceCollapsable.hiderLayout.addLayout(sourcePrefixSufixLayout)
        # Collapsable Connections -------------------------------------
        self.sourceCollapsable.toggled.connect(toolsetWidget.treeWidget.updateTree)

        # Add To Main Layout ---------------------------------------
        mainLayout.addLayout(checkboxLayout)
        mainLayout.addWidget(self.sourceCollapsable)
        mainLayout.addLayout(combosLayout)
        mainLayout.addLayout(tableLayout)
        mainLayout.addLayout(tableButtonLayout)
        mainLayout.addWidget(self.resizerWidget)
        mainLayout.addLayout(vertButtonLayout)
        mainLayout.addWidget(self.progressDivider)
        mainLayout.addWidget(self.progressBarWidget)
        mainLayout.addWidget(self.progressMessageLabel, QtCore.Qt.AlignCenter)


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


# Table data --------------------------------------------------------------------------
# note always use constants.userRoleCount +  your custom role number
TYPE_ROLE = constants.userRoleCount + 1


class ItemData(object):
    def __init__(self, source, target):
        self.source = source
        self.target = target

    def __repr__(self):
        return "ItemData(source={}, target={})".format(self.source, self.target)


class Controller(QtCore.QObject):
    """Main class that controls the table

    - Adding Rows
    - Removing Rows
    - Swapping Source/Target
    - Clearing the table

    """

    def __init__(self, userModel, definitionTree, parent):
        """
        :param parent: The parent widget
        :type parent: object
        """
        super(Controller, self).__init__(parent)
        self.definitionTree = definitionTree
        # Could use a custom subclass
        self.userModel = userModel
        # Initialize Presets --------------------------------------
        self.sourceMappingList = SKELETONS
        self.targetMappingList = HIVE_IDS
        self.presetSourceNames = list()
        self.presetTargetNames = list()
        self.hiveOrderList = list()  # list of hiveOrders list(list(str))
        self.hiveOrder = list()  # list(str)
        for i, preset in enumerate(self.sourceMappingList):
            self.presetSourceNames.append(self.sourceMappingList[i][0])
        for i, preset in enumerate(self.targetMappingList):
            self.presetTargetNames.append(self.targetMappingList[i][0])
            self.hiveOrderList.append(self.targetMappingList[i][2])
        self.presetSourceNames.insert(0, "--- Select Skeleton ---")
        self.presetTargetNames.insert(0, "--- Select Hive Biped ---")

    # ------------------
    # MISC
    # ------------------

    def clear(self):
        """Clears the table."""
        # Clears out our data on the root item aka the tree
        self.userModel.rowDataSource.setUserObjects([])
        # internal code to the model to clear QT stuff
        self.userModel.reload()
        # auto discover + insert from template here aka insertRow

    def onAdd(self):
        """Adds a row to the table."""
        self.addItemFromSelection()

    def swapSelected(self):
        """Swaps source and target values in the selected rows of the table.
        """
        visited = set()
        for modelIndex in self.definitionTree.selectedQIndices():
            if modelIndex.row() in visited:
                continue
            visited.add(modelIndex.row())
            # grab our internal item data aka a dict
            item = self.userModel.rowDataSource.userObject(modelIndex.row())
            source = item.source
            target = item.target
            # swap data via the model so that the view gets notified of change.
            self.userModel.setData(self.userModel.index(modelIndex.row(), 0),
                                   target)
            self.userModel.setData(self.userModel.index(modelIndex.row(), 1),
                                   source)

    def columnButtonClicked(self, modelIndex):
        """Called by the source/target column button clicked in the dataSource classes

        Adds objects to the row/column.

        :param modelIndex: The model index of the button clicked
        :type modelIndex: :class:`QtCore.QModelIndex`
        :return:
        :rtype:
        """
        sel = selection.selectedTransforms()

        if modelIndex.column() == 0:  # source column
            if not sel:
                output.displayWarning("Please select a joint to match a guide to.")
                return False
            return self.userModel.setData(modelIndex, sel[0], QtCore.Qt.EditRole)

        # Else is a target column ------------------------------
        if not sel:
            output.displayWarning("Please select a Hive Guide to match to a joint.")
            return False
        componentIdSideStr = matchguides.hiveComponentIdSide()
        if not componentIdSideStr:
            output.displayWarning("Current selection is not a Hive control object.  "
                                  "Please select a Hive control object.")
            return False
        return self.userModel.setData(modelIndex, componentIdSideStr, QtCore.Qt.EditRole)

    # ------------------
    # GET DATA
    # ------------------

    def allData(self):
        """Returns all data

        :return: The Source Item List and Target Item List
        :rtype: tuple(list(), list())
        """
        sourceList = list()
        targetList = list()
        rowCount = self.userModel.rowCount()
        # loop through all rows
        for i, row in enumerate(range(rowCount)):
            item = self.userModel.rowDataSource.userObject(i)
            sourceList.append(item.source)
            targetList.append(item.target)
        return sourceList, targetList

    def _allItems(self):
        """Returns all the data as a list of class ItemData() instances.

            Class ItemData() instances stores the data for each row.
            "ItemData(source={}, target={})"

        :return: List of class ItemData() instances
        :rtype: list(:class:`ItemData`)
        """
        items = list()
        rowCount = self.userModel.rowCount()
        # loop through all rows
        for i, row in enumerate(range(rowCount)):
            item = self.userModel.rowDataSource.userObject(i)
            items.append(item)
        return items

    # ------------------
    # ADD ROWS
    # ------------------

    def addItemFromSelection(self):
        """Adds rows to the table.

        Gets selection pairs, ie first four objects in the selection as source objs and last four as targets.

        Creates the new item as a dictionary and adds it to the model.

        After added to item data:
            ItemData(sourceObj, targetObjs[i])
        Becomes:
            "ItemData(source={}, target={})"

        """
        sourceObjs, targetObjs = ["item1"], ["item2"]
        if not sourceObjs:
            sourceObjs = [""]
            targetObjs = [""]
        elif len(sourceObjs) != len(targetObjs):  # lists are odd numbers so last entry will be empty
            targetObjs.append("")
        # Batch adds all items to the model from selection
        items = []
        for i, sourceObj in enumerate(sourceObjs):
            newItem = ItemData(sourceObj, targetObjs[i])
            items.append(newItem)

        # get the last selected row if not return to the end of the list -----
        indices = self.definitionTree.selectedRowsIndices()
        insertIndex = self.userModel.rowCount()
        if indices:
            insertIndex = indices[-1].row() + 1
        self._updateTreeFromModelItems(items, clearExisting=False, insertIndex=insertIndex)

    def _autoAddRows(self, rowList):
        """Auto add rows to the table if not enough rows for the length of the rowList

        :param rowList: List of class ItemData() instances
        :type rowList: list(:class:`ItemData`)
        """
        newCount = len(rowList)
        items = self._allItems()
        rowCount = len(items)
        if newCount > rowCount:
            newRows = newCount - rowCount
            for i in range(newRows):  # loop for the number of new rows
                blankItem = ItemData("", "")
                items.append(blankItem)  # add a new item
        return items

    # ------------------
    # UPDATE TABLE
    # ------------------

    def _updateTreeFromModelItems(self, items, clearExisting=True, insertIndex=None):
        """From the ItemData list, update the table tree with the current items:

            Class ItemData() instances stores the data for each row.
            "ItemData(source={}, target={})"

        :param items: Class storing the row data "ItemData(source={}, target={})"
        :type items: list(:class:`ItemData`)
        :param clearExisting: If True clears the table before adding the new items
        :type clearExisting: bool
        :param insertIndex: The index to insert the new rows at, if None will append to the end of the table
        :type insertIndex: int
        """
        if clearExisting:
            self.clear()  # clears the table
        # must call the model to insert because this automatically informs the ui it's got something new to render
        # without this your new items won't display until the UI is refresh at some point i.e mouseEnter
        if insertIndex is None:  # None so insert at the end of the table
            insertIndex = self.userModel.rowCount()
        self.userModel.insertRows(insertIndex,
                                  count=len(items),
                                  items=items
                                  )
        tableModel = self.definitionTree.model()  # this is the proxy model
        # we force columns 0 and 1 for all rows to be persistent in other words always render
        # our custom widget in each cell
        for row in range(tableModel.rowCount()):
            firstColumnIndex = tableModel.index(row, 0)
            secondColumnIndex = tableModel.index(row, 1)
            if tableModel.flags(firstColumnIndex) & QtCore.Qt.ItemIsEditable:
                self.definitionTree.openPersistentEditor(firstColumnIndex)
            if tableModel.flags(secondColumnIndex) & QtCore.Qt.ItemIsEditable:
                self.definitionTree.openPersistentEditor(secondColumnIndex)

    # ------------------
    # REMOVE ROWS
    # ------------------

    def removeSelected(self):
        selected = self.definitionTree.selectedRowsIndices()
        if not selected:
            return
        for rowIndex in reversed(selected):
            self.userModel.removeRow(rowIndex.row())

    # ------------------
    # UPDATE FROM PRESETS
    # ------------------

    def _presetDictByName(self, presetKeyName):
        """Returns a preset dict from its preset name.

        Loops over all the preset dicts (self.presetMappingList) and returns the first match.

        :param name: The name of the key of the preset dict eg "Hive Biped Cntrls"
        :type name: str
        :return: The preset dictionary with nodes and options.
        :rtype: dict(dict(str))
        """
        for presetDict in self.presetMappingList:
            if presetKeyName in presetDict.keys():
                return presetDict
        else:
            return None

    def _updateLists(self, sourceKeyName, targetKeyName):
        for i, preset in enumerate(self.targetMappingList):
            if targetKeyName == preset[0]:
                self.hiveIds = preset[1]
                self.hiveOrder = self.hiveOrderList[i]
                break
            else:
                self.hiveOrder = self.hiveOrderList[0]  # Default to the Hive Biped order
        for preset in self.sourceMappingList:
            if sourceKeyName == preset[0]:
                self.jointList = preset[1]
                break
            else:
                self.jointList = list()

    def updateSourcesFromPreset(self, sourceKeyName, targetKeyName, updateLists=True, message=False):
        """Updates the sources column from a preset name.
        Adds rows if needed, other column will be blank or defaults.

        :param sourceKeyName: The name of the source preset
        :type sourceKeyName: str
        :param targetKeyName: The name of the target preset
        :type targetKeyName: str
        :param updateLists: If True will update the lists, if False will use the current lists
        :type updateLists: bool
        :param message: If True will print a message if the preset is not found
        :type message: bool
        :return: The Options Dict for the target preset intended for the UI to use, left right modifiers etc.
        :rtype: tuple(list(str), list(str))
        """
        if updateLists:
            self._updateLists(sourceKeyName, targetKeyName)  # updates self.hiveIds, self.hiveOrder, self.jointList

        if not self.jointList:
            return

        jointList = matchguides.skeletonOrderedList(skeletonDict=self.jointList,
                                                    order=self.hiveOrder)

        if not jointList:
            if message:  # default is off as likely a divider or title
                output.displayWarning("Preset not found: {}".format(sourceKeyName))
            return
        self._updateSourcesColumn(jointList)

    def updateTargetsFromPreset(self, sourceKeyName, targetKeyName, message=False):
        """Updates the targets column from a preset name.
        Adds rows if needed, other column will be blank or defaults.

        :param sourceKeyName: The name of the source preset
        :type sourceKeyName: str
        :param targetKeyName: The name of the target preset
        :type targetKeyName: str
        :return: The Options Dict for the target preset intended for the UI to use, left right modifiers etc.
        :rtype: tuple(list(str), list(str))
        """
        self._updateLists(sourceKeyName, targetKeyName)  # updates self.hiveIds, self.hiveOrder, self.jointList

        if not self.hiveIds:
            return

        hiveIdList = matchguides.hiveIdsDictToStringList(hiveIdDict=self.hiveIds,
                                                         order=self.hiveOrder)
        if not hiveIdList:
            if message:  # default is off as likely a divider or title
                output.displayWarning("Preset not found: {}".format(targetKeyName))
            return

        self.clear()  # will repopulate both columns

        self._updateTargetsColumn(hiveIdList)
        # Must update the sources as the order may have changed.
        self.updateSourcesFromPreset(sourceKeyName, targetKeyName, updateLists=False)  # lists are up to date so skip

    def updateSourcesFromDictList(self, presetList):
        """From an item dict, updated the sources column.

        [{'root': {'node': 'spine_M_cog_anim'}},
         {'shoulder_L': {'node': 'arm_L_shldr_fk_anim'}}]

        :param presetList:
        :type presetList:
        :return:
        :rtype:
        """
        if not presetList:
            return
        nodeList = list()
        for itemDict in presetList:
            nodeList.append(itemDict[list(itemDict.keys())[0]]["node"])
        self._updateSourcesColumn(nodeList)

    def updateTargetsFromDictList(self, presetList):
        if not presetList:
            return
        nodeList = list()
        for itemDict in presetList:
            nodeList.append(itemDict[list(itemDict.keys())[0]]["node"])
        self._updateTargetsColumn(nodeList)

    def _updateSourcesColumn(self, nodes):
        """Updates the sources column from a list.
        Adds rows if needed, other column will be blank or defaults.

        :param nodes: List of names of source maya objects
        :type nodes: list(str)
        """
        items = self._autoAddRows(nodes)  # be sure there are enough items in the list
        # Update the sources column -------------
        for i, item in enumerate(items):
            item.source = nodes[i]
        self._updateTreeFromModelItems(items, clearExisting=True)

    def _updateTargetsColumn(self, nodes):
        """Updates the targets column from list.
        Adds rows if needed, other column will be blank or defaults.

        :param nodes: List of names of source maya objects
        :type nodes: list(str)
        """
        items = self._autoAddRows(nodes)  # be sure there are enough items in the list
        # Update the sources column -------------
        for i, item in enumerate(items):
            item.target = nodes[i]
        self._updateTreeFromModelItems(items, clearExisting=True)


class SourceColumn(datasources.BaseDataSource):
    """Data in the first "Source" column
    """

    def __init__(self, controller, headerText=None, model=None, parent=None):
        super(SourceColumn, self).__init__(headerText, model, parent)
        self.controller = controller

    def delegate(self, parent):
        return delegates.LineEditButtonDelegate(parent)

    def columnCount(self):
        # specify how many columns that the item has, note: this is not the same as the number of columns in the view
        # which is can be changed on the view code.
        return 3

    def insertChildren(self, index, children):
        self._children[index:index] = children
        return True

    def insertRowDataSources(self, index, count, items):
        return self.insertChildren(index, items)

    def customRoles(self, index):
        """When you have custom roles i.e in this case TYPE_ROLE is here for search. it allows you
        to retrieve item data via dataByRole method.
        """
        return [TYPE_ROLE, constants.buttonClickedRole]

    def dataByRole(self, index, role):
        if TYPE_ROLE == role:
            return self._baseType
        elif role == constants.buttonClickedRole:
            return self.controller.columnButtonClicked(self.model.index(index, 0))

    def data(self, index):
        userData = self.userObject(index)
        if userData:
            return userData.source
        return ""

    def setData(self, index, value):
        userData = self.userObject(index)
        # you should replace this code with what you need to set the source for the index(row) on the userData object
        if userData:
            userData.source = value
            return True
        return False


class TargetColumn(datasources.ColumnDataSource):
    """Data in the second "Source" column
    """

    def __init__(self, headerText=None, model=None, parent=None):
        super(TargetColumn, self).__init__(headerText, model, parent)

    def delegate(self, parent):
        return delegates.LineEditButtonDelegate(parent)

    def data(self, rowDataSource, index):
        userData = rowDataSource.userObject(index)
        if userData and userData.target:
            return userData.target
        return ""

    def setData(self, rowDataSource, index, value):
        userData = rowDataSource.userObject(index)
        # you should replace this code with what you need to set the target for the index(row) on the userData object
        if userData:
            userData.target = value
            return True
        return False

    def customRoles(self, rowDataSource, index):
        """When you have custom roles i.e in this case TYPE_ROLE is here for search. it allows you
        to retrieve item data via dataByRole method.
        """
        return [TYPE_ROLE, constants.buttonClickedRole]

    def dataByRole(self, rowDataSource, index, role):
        if TYPE_ROLE == role:
            return self._baseType
        elif role == constants.buttonClickedRole:
            return rowDataSource.controller.columnButtonClicked(self.model.index(index, 1))
