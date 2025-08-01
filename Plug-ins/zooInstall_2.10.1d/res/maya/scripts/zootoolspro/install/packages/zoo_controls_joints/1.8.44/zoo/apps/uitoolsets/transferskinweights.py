""" ---------- Replace Joint Weights -------------
Transfers skinned joint weights from one joint list to another joint list.

Replaces the old tool "Replace Joint Weights".


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
from zoo.libs.maya.cmds.objutils import selection
from zoo.libs.maya.cmds.skin import skinreplacejoints
from zoo.libs.maya.cmds.animation import batchconstraintconstants, mocap

# Table imports -----------------
from zoo.libs.pyqt.extended import tableviewplus
from zoo.libs.pyqt.models import tablemodel, delegates
from zoo.libs.pyqt.models import datasources, constants

UI_MODE_COMPACT = 0
UI_MODE_ADVANCED = 1

SKELETON_MAPPINGS = batchconstraintconstants.SKELETON_TWIST_MAPPINGS

ITEMS_LIST_KEY = "itemsList"
OPTIONS_DICT_KEY = "optionsDict"


class TransferJointWeights(toolsetwidget.ToolsetWidget):
    id = "transferSkinWeights"
    info = "Transfers joint skin weights from one joint to another joint."
    uiData = {"label": "Transfer Joint Weights (beta)",
              "icon": "replaceJointWeights",
              "tooltip": "Transfers joint skin weights from one joint to another joint.",
              "defaultActionDoubleClick": False,
              "helpUrl": "https://create3dcharacters.com/maya-tool-replace-joint-weights/"}

    # ------------------
    # STARTUP
    # ------------------

    def preContentSetup(self):
        """First code to run, treat this as the __init__() method"""
        self.toolsetWidget = self  # needed for table resizer widget

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
        return super(TransferJointWeights, self).currentWidget()

    def widgets(self):
        """ Override base method for autocompletion

        :return:
        :rtype: list[GuiAdvanced or GuiCompact]
        """
        return super(TransferJointWeights, self).widgets()

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
        self.compactWidget.targetLeft.setEnabled(state)
        self.compactWidget.targetRight.setEnabled(state)
        self.compactWidget.targetLRAlwaysSuffix.setEnabled(state)
        self.compactWidget.targetLRAlwaysPrefix.setEnabled(state)
        self.compactWidget.targetLRSeparatorOnBorder.setEnabled(state)

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
        self.properties.targetNamespace.value = ""
        self.properties.targetLeft.value = "_L"
        self.properties.targetRight.value = "_R"
        self.properties.targetLRAlwaysPrefix.value = False
        self.properties.targetLRAlwaysSuffix.value = False
        self.properties.targetLRSeparatorOnBorder.value = False
        self.properties.targetPrefix.value = ""
        self.properties.targetSuffix.value = ""
        self.properties.autoLeftRightCheck.value = False
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
        optionsDict["namespace"] = self.properties.targetNamespace.value
        optionsDict["leftIdentifier"] = self.properties.targetLeft.value
        optionsDict["rightIdentifier"] = self.properties.targetRight.value
        optionsDict["leftRightUnderscore"] = self.properties.targetLRSeparatorOnBorder.value
        optionsDict["leftRightPrefix"] = self.properties.targetLRAlwaysPrefix.value
        optionsDict["leftRightSuffix"] = self.properties.targetLRAlwaysSuffix.value
        optionsDict["prefix"] = self.properties.targetPrefix.value
        optionsDict["suffix"] = self.properties.targetSuffix.value

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
        self.properties.targetNamespace.value = optionsDict["namespace"]
        self.properties.targetLeft.value = optionsDict["leftIdentifier"]
        self.properties.targetRight.value = optionsDict["rightIdentifier"]
        self.properties.targetLRSeparatorOnBorder.value = optionsDict["leftRightUnderscore"]
        self.properties.targetLRAlwaysPrefix.value = optionsDict["leftRightPrefix"]
        self.properties.targetLRAlwaysSuffix.value = optionsDict["leftRightSuffix"]
        self.properties.targetPrefix.value = optionsDict["prefix"]
        self.properties.targetSuffix.value = optionsDict["suffix"]
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
    # LOGIC
    # ------------------

    def applySourcesPreset(self):
        """Updates from the source preset combo box"""
        presetNames = self.compactWidget.tableControl.presetSourceNames
        options = self.compactWidget.tableControl.updateColumnsFromPreset(
            presetNames[self.properties.sourceCombo.value])
        if not options:
            return  # is a title divider
        self.properties.sourceLeft.value = options["leftIdentifier"]
        self.properties.sourceRight.value = options["rightIdentifier"]
        self.properties.sourceLRAlwaysPrefix.value = options["leftRightPrefix"]
        self.properties.sourceLRAlwaysSuffix.value = options["leftRightSuffix"]
        self.properties.sourceLRSeparatorOnBorder.value = options["leftRightUnderscore"]
        self.properties.autoLeftRightCheck.value = True
        self.updateFromProperties()

    def applyTargetsPreset(self):
        """Updates from the source preset combo box"""
        presetNames = self.compactWidget.tableControl.presetSourceNames
        options = self.compactWidget.tableControl.updateColumnsFromPreset(
            presetNames[self.properties.targetCombo.value],
            sources=False)
        if not options:
            return
        self.properties.autoLeftRightCheck.value = options["autoRightSide"]
        self.properties.targetLeft.value = options["leftIdentifier"]
        self.properties.targetRight.value = options["rightIdentifier"]
        self.properties.targetLRAlwaysPrefix.value = options["leftRightPrefix"]
        self.properties.targetLRAlwaysSuffix.value = options["leftRightSuffix"]
        self.properties.targetLRSeparatorOnBorder.value = options["leftRightUnderscore"]
        self.properties.autoLeftRightCheck.value = True
        self.leftRightCheckboxChanged()
        self.updateFromProperties()

    def _updateBuildInstance(self):
        """Use the transferInstance code to here if used multiple times"""
        pass

    def validateObjects(self):
        """Validates the objects in the table, returns a list of errors"""
        self._updateBuildInstance()
        self.batchBakeInstance.printValidateObjects()

    @toolsetwidget.ToolsetWidget.undoDecorator
    def transferSkinWeights(self):
        """Transfers the skin weights from the source to the target joints"""
        import time
        start_time = time.time()
        boundJoints, targetJoints = self.compactWidget.tableControl.allData()
        transferInstance = skinreplacejoints.ReplaceJointsWeights(
            boundJoints,
            targetJoints,
            moveWithJoints=self.properties.moveWithJointsCheck.value,
            unbindSource=self.properties.unbindSourceCheck.value,
            sourceNamespace=self.properties.sourceNamespace.value,
            targetNamespace=self.properties.targetNamespace.value,
            sourcePrefix=self.properties.sourcePrefix.value,
            targetPrefix=self.properties.targetPrefix.value,
            sourceSuffix=self.properties.sourceSuffix.value,
            targetSuffix=self.properties.targetSuffix.value,
            autoLeftToRight=self.properties.autoLeftRightCheck.value,
            sourceLeftIdentifier=self.properties.sourceLeft.value,
            sourceRightIdentifier=self.properties.sourceRight.value,
            sourceLRIsPrefix=self.properties.sourceLRAlwaysPrefix.value,
            sourceLRIsSuffix=self.properties.sourceLRAlwaysSuffix.value,
            sourceLRSeparatorOnBorder=self.properties.sourceLRSeparatorOnBorder.value,
            targetLeftIdentifier=self.properties.targetLeft.value,
            targetRightIdentifier=self.properties.targetRight.value,
            targetLRIsPrefix=self.properties.targetLRAlwaysPrefix.value,
            targetLRIsSuffix=self.properties.targetLRAlwaysSuffix.value,
            targetLRSeparatorOnBorder=self.properties.targetLRSeparatorOnBorder.value
        )
        transferInstance.replaceJointsWeights(message=True)
        print("--- %s seconds ---" % (time.time() - start_time))

    # ------------------
    # CONNECTIONS
    # ------------------

    def uiConnections(self):
        """Add all UI connections here, button clicks, on changed etc"""
        for widget in self.widgets():
            widget.transferSkinWeightsBtn.clicked.connect(self.transferSkinWeights)
            widget.sourceCombo.itemChanged.connect(self.applySourcesPreset)
            widget.targetCombo.itemChanged.connect(self.applyTargetsPreset)
            # Auto checkbox changed --------------
            widget.autoLeftRightCheck.stateChanged.connect(self.leftRightCheckboxChanged)
            # Connect Table Functions ------------------
            widget.addButton.clicked.connect(widget.tableControl.onAdd)
            widget.clearButton.clicked.connect(widget.tableControl.clear)
            widget.removeButton.clicked.connect(widget.tableControl.removeSelected)
            widget.swapButton.clicked.connect(widget.tableControl.swapSelected)
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
        # Auto Left Right Names Checkbox ---------------------------------------
        tooltip = "Will automatically try to also find the right side names of the given joints. \n" \
                  "See `Source/Target Rename Options` to set the left/right settings. \n" \
                  "Useful for transferring full skeleton setups."
        self.autoLeftRightCheck = elements.CheckBox(label="Auto Right Side",
                                                    checked=False,
                                                    toolTip=tooltip,
                                                    parent=parent)
        # Move With Joints Checkbox ---------------------------------------
        tooltip = ("Will move the skinned mesh to the target joints \n"
                   "after transferring the skin weights.\n\n"
                   "If off (default) the mesh will stay in place as \n"
                   "the weights are transferred.")
        self.moveWithJointsCheck = elements.CheckBox(label="Move With Joints",
                                                     checked=False,
                                                     toolTip=tooltip,
                                                     parent=parent)
        # Unbind Source Checkbox ---------------------------------------
        tooltip = ("Will remove the source bound joints from the skin cluster \n"
                   "after transferring the skin weights.")
        self.unbindSourceCheck = elements.CheckBox(label="Unbind Source Joints",
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

        # Target ---------------------------------------
        tooltip = "Specify the namespace to be added to all target names. \n\n" \
                  "  - Example: `characterX` will be added to the name eg `characterX:pCube1`"
        self.targetNamespace = elements.StringEdit(label="Namespace",
                                                   editPlaceholder="characterX:",
                                                   toolTip=tooltip,
                                                   parent=parent)
        self.targetLeft = elements.StringEdit(label="Left Right ID",
                                              editText="_L",
                                              toolTip=tooltipLR,
                                              parent=parent)
        self.targetRight = elements.StringEdit(label="",
                                               editText="_R",
                                               toolTip=tooltipLR,
                                               parent=parent)
        self.targetLRAlwaysPrefix = elements.CheckBox(label="L-R Is Prefix",
                                                      checked=False,
                                                      toolTip=tooltipForcePrefix,
                                                      parent=parent,
                                                      right=True)
        self.targetLRAlwaysSuffix = elements.CheckBox(label="L-R Is Suffix",
                                                      checked=False,
                                                      toolTip=tooltipForceSuffix,
                                                      parent=parent,
                                                      right=True)
        self.targetLRSeparatorOnBorder = elements.CheckBox(label="Separator On Border",
                                                           checked=False,
                                                           toolTip=tooltipBorder,
                                                           parent=parent,
                                                           right=True)
        tooltip = "Specify the prefix to be added to all target names. \n\n" \
                  "  - Example: `xxx_` will be added to the name eg `xxx_pCube1`"
        self.targetPrefix = elements.StringEdit(label="Prefix",
                                                editPlaceholder="xxx_",
                                                toolTip=tooltip,
                                                labelRatio=3,
                                                editRatio=6,
                                                parent=parent)
        tooltip = "Specify the suffix to be added to all target names. \n\n" \
                  "  - Example: `xxx_` will be added to the name eg `pCube1_xxx`"
        self.targetSuffix = elements.StringEdit(label="Suffix",
                                                editPlaceholder="_xxx",
                                                toolTip=tooltip,
                                                labelRatio=3,
                                                editRatio=6,
                                                parent=parent)
        # Constrain And Bake Btn ---------------------------------------
        tooltip = "Transfer the skin weights from the source column to the target column's joints. \n" \
                  "The source column is the bound joints and the target column is the joints to transfer to. \n" \
                  "For skeleton presets be sure to add namespaces where appropriate in the Rename Options."
        self.transferSkinWeightsBtn = elements.styledButton("Transfer & Replace Skin Weights",
                                                            icon="replaceJointWeights",
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
        # Select Button --------------------------------------
        tooltip = "Selects the source, target, or all objs. \n" \
                  "Left-click to activate the menu with options."
        self.selectBtn = elements.styledButton("",
                                               icon="cursorSelect",
                                               toolTip=tooltip,
                                               style=uic.BTN_DEFAULT,
                                               parent=parent)
        self.selectBtn.setVisible(False)
        # ---------------- COLLAPSABLES ------------------
        self.sourceCollapsable = elements.CollapsableFrameThin("Source Rename Options",
                                                               contentMargins=(uic.SREG, uic.SREG, uic.SREG, uic.SREG),
                                                               contentSpacing=uic.SLRG,
                                                               collapsed=True,
                                                               parent=parent)
        self.targetCollapsable = elements.CollapsableFrameThin("Target Rename Options",
                                                               contentMargins=(uic.SREG, uic.SREG, uic.SREG, uic.SREG),
                                                               contentSpacing=uic.SLRG,
                                                               collapsed=True,
                                                               parent=parent)

    def tableWidget(self, parent):
        # Build the table tree --------------------------------------------
        self.definitionTree = tableviewplus.TableViewPlus(manualReload=False, searchable=False, parent=parent)

        self.userModel = tablemodel.TableModel(parent=parent)
        self.tableControl = Controller(self.userModel, self.definitionTree, parent=parent)
        self.definitionTree.setModel(self.userModel)
        self.definitionTree.tableView.verticalHeader().hide()
        self.definitionTree.tableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.definitionTree.tableView.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.definitionTree.registerRowDataSource(SourceColumn(self.tableControl, headerText="Source Bound Joints"))
        self.definitionTree.registerColumnDataSources([TargetColumn(headerText="Target Joints")])

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
                  "Select joints already bound to the mesh and then joint targets to add to the table.\n" \
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
        checkboxLayout.addWidget(self.moveWithJointsCheck, 1)
        checkboxLayout.addWidget(self.unbindSourceCheck, 1)

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

        # Target ---------------------------------------
        targetNamespaceLayout = elements.hBoxLayout(self, margins=(0, 0, 0, 0), spacing=uic.SREG)
        targetNamespaceLayout.addWidget(self.targetNamespace, 15)
        targetNamespaceLayout.addWidget(self.targetLeft, 10)
        targetNamespaceLayout.addWidget(self.targetRight, 5)

        targetCheckboxLayout = elements.hBoxLayout(self, margins=(0, 0, 0, 0), spacing=uic.SREG)
        targetCheckboxLayout.addWidget(self.targetLRAlwaysPrefix, 1)
        targetCheckboxLayout.addWidget(self.targetLRAlwaysSuffix, 1)
        targetCheckboxLayout.addWidget(self.targetLRSeparatorOnBorder, 1)

        targetPrefixSufixLayout = elements.hBoxLayout(self, margins=(0, 0, 0, 0), spacing=uic.SREG)
        targetPrefixSufixLayout.addWidget(self.targetPrefix, 1)
        targetPrefixSufixLayout.addWidget(self.targetSuffix, 1)

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
        buttonLayout.addWidget(self.transferSkinWeightsBtn, 20)
        buttonLayout.addWidget(self.validateBtn, 1)
        buttonLayout.addWidget(self.selectBtn, 1)

        # Button vertical layout ---------------------------------------
        vertButtonLayout = elements.vBoxLayout(self, margins=(0, 0, 0, 0), spacing=uic.SPACING)
        vertButtonLayout.addLayout(buttonLayout)

        #  Flip Collapsable ---------------------------------------
        #  Pre post Collapsable ---------------------------------------
        self.sourceCollapsable.hiderLayout.addLayout(sourceNamespaceLayout)
        self.sourceCollapsable.hiderLayout.addLayout(sourceCheckboxLayout)
        self.sourceCollapsable.hiderLayout.addLayout(sourcePrefixSufixLayout)
        #  Options Collapsable ---------------------------------------
        self.targetCollapsable.hiderLayout.addLayout(targetNamespaceLayout)
        self.targetCollapsable.hiderLayout.addLayout(targetCheckboxLayout)
        self.targetCollapsable.hiderLayout.addLayout(targetPrefixSufixLayout)
        # Collapsable Connections -------------------------------------
        self.sourceCollapsable.toggled.connect(toolsetWidget.treeWidget.updateTree)
        self.targetCollapsable.toggled.connect(toolsetWidget.treeWidget.updateTree)

        # Add To Main Layout ---------------------------------------
        mainLayout.addLayout(checkboxLayout)
        mainLayout.addWidget(self.sourceCollapsable)
        mainLayout.addWidget(self.targetCollapsable)
        mainLayout.addLayout(combosLayout)
        mainLayout.addLayout(tableLayout)
        mainLayout.addLayout(tableButtonLayout)
        mainLayout.addWidget(self.resizerWidget)
        mainLayout.addLayout(vertButtonLayout)


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
        self.presetMappingList = SKELETON_MAPPINGS
        self.presetSourceNames = list()
        self.presetTargetNames = list()
        for preset in self.presetMappingList:
            self.presetSourceNames.append(list(preset.keys())[0])
        self.presetTargetNames = list(self.presetSourceNames)
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

        :param modelIndex:
        :type modelIndex: :class:`QtCore.QModelIndex`
        :return:
        :rtype:
        """
        sel = selection.selectedTransforms(type="joint")  # todo: change selection to new code
        if not sel:
            return False
        return self.userModel.setData(modelIndex, sel[0], QtCore.Qt.EditRole)

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
        sourceObjs, targetObjs = selection.selectionPairs(type="joint")
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

    def _nodesConstraintsList(self, presetDict):
        """From a preset dictionary returns the nodes and constraints as lists.

        :param presetDict: A single preset dictionary eg "Hive Biped Cntrls"
        :type presetDict: dict(dict(str))
        :return: a list of object names and constraint types as strings
        :rtype: tuple(list(str), list(str))
        """
        nodeList = list()
        constraintTypeList = list()
        valuesDict = list(presetDict.values())[0]
        if not valuesDict:  # Can be empty when a preset is a divider or title.
            return list(), list(), dict()
        optionsDict = valuesDict["options"]
        nodesConstraintsList = valuesDict["nodes"]  # is a list of dictionaries
        for dictDict in nodesConstraintsList:
            nodeConstraintDict = list(dictDict.values())[0]  # get contents of first key
            nodeList.append(nodeConstraintDict["node"])
            constraintTypeList.append(nodeConstraintDict["constraint"])
        return nodeList, constraintTypeList, optionsDict

    def updateColumnsFromPreset(self, presetKeyName, sources=True, message=False):
        """Updates the column from a preset name.

        If sources is True updates the sources column, if False updates the target.

        Adds rows if needed, other column will be blank or defaults.

        :param presetKeyName: The name of the dictionary with nodes and options eg "Hive Biped Cntrls"
        :type presetKeyName: str
        :param sources: If True updates the sources column, if False updates the targets column
        :type sources: bool
        :return: The Options Dict for the target preset intended for the UI to use, left right modifiers etc.
        :rtype: tuple(list(str), list(str))
        """
        presetDict = self._presetDictByName(presetKeyName)
        if not presetDict:
            if message:  # default is off as likely a divider or title
                output.displayWarning("Preset not found: {}".format(presetKeyName))
            return
        jointList, constraintTypeList, optionsDict = self._nodesConstraintsList(presetDict)
        if not jointList:  # Likely a divider or title so do nothing.
            return
        if sources:
            self._updateSourcesColumn(jointList)
        else:
            self._updateTargetsColumn(jointList)
        return optionsDict

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
        """Updates the targets and constrain column from two lists.
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
        return 2

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
        # replace this code with what you need to set the target for the index(row) on the userData object
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
