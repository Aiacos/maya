import os

from zoo.apps.hiveartistui import uiinterface
from zoo.apps.toolsetsui.widgets import toolsetwidget

from zoo.libs.maya.cmds.filemanage import saveexportimport
from zoo.libs.hive import api as hiveapi

from zoo.libs.pyqt import uiconstants as uic
from zoo.libs.pyqt.widgets import elements
from zoo.libs.utils import output
from zoovendor.Qt import QtWidgets, QtCore

from zoo.libs.hive.library.exporters import fbxexporter
from zoo.libs.hive.library.exporters import maexporter


class HiveRigMaExportToolset(toolsetwidget.ToolsetWidget):
    id = "hiveMaRigExport"
    info = "Hive Ma rig export tool."
    uiData = {"label": "Hive Export MA",
              "icon": "maya",
              "tooltip": "Provides an MA exporter for hive rigs.",
              "defaultActionDoubleClick": False,
              "helpUrl": "https://create3dcharacters.com/maya-tool-hive-export-ma"}

    def contents(self):
        """The UI Modes to build, compact, medium and or advanced """
        return [self.initCompactWidget()]

    def initCompactWidget(self):
        """Builds the Compact GUI (self.compactWidget) """
        self.compactWidget = GuiCompact(parent=self, properties=self.properties, toolsetWidget=self)
        return self.compactWidget

    def postContentSetup(self):
        """Last of the initialize code"""
        self.uiFolderPath = ""
        # Update a rig list done in post because we have signals getting emitted by
        # hive UI which require a reload of the list as well.
        self._rigStateChanged()  # Updates the rig combo box
        self.uiConnections()

    @property
    def defaultBrowserPath(self):
        outputDirectory = os.path.expanduser("~")
        if not saveexportimport.isCurrentSceneUntitled():
            currentScenePath = saveexportimport.currentSceneFilePath()
            outputDirectory = os.path.dirname(currentScenePath)
        return outputDirectory

    def initializeProperties(self):
        """Used to store and update UI data

        For use in the GUI use:
            current value: self.properties.itemName.value
            default value (automatic): self.properties.itemName.default

        To connect Qt widgets to property methods use:
            self.toolsetWidget.linkProperty(self.widgetQtName, "itemName")

        :return properties: special dictionary used to save and update all GUI widgets
        :rtype properties: list(dict)
        """
        return [
            {"name": "filePathEdit", "value": ""},
        ]

    def widgets(self):
        """ Override base method for autocompletion

        :return:
        :rtype: list[GuiCompact]
        """
        return super(HiveRigMaExportToolset, self).widgets()

    # ------------------
    # ENTER
    # ------------------

    def enterEvent(self, event):
        """When the cursor enters the UI update it"""
        self._rigStateChanged()

    def _rigStateChanged(self):
        self._updateSceneRigs()
        for widget in self.widgets():
            widget.updateRigs(self.rigComboNames)

    def _updateSceneRigs(self):
        self.rigComboNames, self.rigInstances = fbxexporter.allRigsComboUI()

    def _currentRigChangedFromArtistUI(self, rigName):
        for widget in self.widgets():
            widget.setCurrentRig(rigName)

    def uiSettingsDict(self):
        uiSettingsDict = dict()
        self.updateUISettings()
        uiSettingsDict["rigCombo"] = self.rigCombo
        uiSettingsDict["outputFilePath"] = self.outputFilePath
        return uiSettingsDict

    def updateUISettings(self):
        """Updates all the class variables UI based on the current settings"""
        if not self.rigInstances:
            self.rigInstance = None
            self.rigName = ""
        else:
            self.rigInstance = self.rigInstances[self.properties.rigListCombo.value]
            self.rigName = self.rigComboNames[self.properties.rigListCombo.value]

        self.outputFilePath = self.compactWidget.filePathEdit.path()
        self.rigCombo = self.properties.rigListCombo.value

    def sceneRigs(self):
        """Returns a list of rig names in the scene

        :return: list of rig names in the scene
        :rtype: list(str), list[:class:`zoo.libs.hive.base.rig.Rig`]
        """
        return fbxexporter.allRigsComboUI()

    def _uiRigModel(self):
        """Query from Hive UI the rig model instance. This is so we can sync between the UIs
        """
        hiveUICore = uiinterface.instance().core()
        # todo: support running without the artist ui
        if hiveUICore is None:
            output.displayWarning("Hive Artist UI needs to be open")
            return
        container = hiveUICore.currentRigContainer
        if container is None:
            output.displayWarning("Hive Artist UI needs to have a active rig")
            return
        rigModel = container.rigModel
        if rigModel is None:
            output.displayError("Hive Artist UI needs a active rig")
            return
        return rigModel

    def progressCallback(self, progress, message):
        output.displayInfo("Progress: {}% : {}".format(progress, message))

    def exportMAButtonPressed(self):
        """Single file export
        self.updateUISettings() must be called before this method.
        """
        self.updateUISettings()  # updates all the UI settings to class variables for later use.

        if self.rigInstance is None:
            output.displayWarning("No valid Rig Selected in the UI")
            return

        if not self.outputFilePath:
            output.displayWarning("Invalid export path: {}".format(self.outputFilePath))
            return

        # todo: export rig here.
        exporter = hiveapi.Configuration().exportPluginForId("maExport")()
        exporter.onProgressCallbackFunc = self.progressCallback
        settings = exporter.exportSettings()  # type: maexporter.ExportSettings
        settings.outputPath = self.outputFilePath
        exporter.execute(self.rigInstance, settings)

    def uiConnections(self):
        """Add all UI connections here, button clicks, on changed etc"""
        hiveUICore = uiinterface.instance()
        for widget in self.widgets():
            widget.exportBtn.clicked.connect(self.exportMAButtonPressed)
        if hiveUICore is not None:
            hiveUICore = hiveUICore.core()
            hiveUICore.rigRenamed.connect(self._rigStateChanged)
            hiveUICore.rigsChanged.connect(self._rigStateChanged)
            hiveUICore.currentRigChanged.connect(self._currentRigChangedFromArtistUI)


class GuiWidgets(QtWidgets.QWidget):
    def __init__(self, parent=None, properties=None, toolsetWidget=None):
        """Builds the main widgets for all GUIs

        properties is the list(dictionaries) used to set logic and pass between the different UI layouts
        such as compact/adv etc

        :param parent: the parent of this widget
        :type parent: :class:`QtWidgets.QWidget`
        :param properties: the properties dictionary which tracks all the properties of each widget for UI modes
        :type properties: :class:`zoo.apps.toolsetsui.widgets.toolsetwidget.PropertiesDict`
        :type toolsetWidget: :class:`HiveRigExportToolset`
        """
        super(GuiWidgets, self).__init__(parent=parent)
        self.properties = properties

        # Select Hive Rig -----------------------------
        self.rigDivider = elements.LabelDivider(text="Select Hive Rig", parent=parent)
        # Rig Combo -----------------------------
        toolTip = "Select the Hive rig from the scene to export. \n" \
                  "No rigs will appear if there are no valid Hive rigs in the scene."
        self.rigListCombo = elements.ComboBoxRegular("",
                                                     items=[],
                                                     parent=parent,
                                                     labelRatio=1,
                                                     boxRatio=3,
                                                     toolTip=toolTip)

        # ----------------------------- FILE PATHS -----------------------------
        # File Path Divider -----------------------------
        self.filePathDivider = elements.LabelDivider(text="File Path (Single File)", parent=parent)
        # Path Widget -----------------------------
        toolTip = "Set the .MA path and file name that will be saved to disk. "
        self.filePathEdit = elements.PathWidget(parent=parent,
                                                path=self.properties.filePathEdit.value,
                                                toolTip=toolTip)
        self.filePathEdit.defaultBrowserPath = toolsetWidget.defaultBrowserPath
        self.filePathEdit.pathText.setPlaceHolderText("Set MA export file path...")
        self.filePathEdit.setSearchFilter("*.ma")

        # Export Button -----------------------------
        toolTip = "Hive Export MA saves a Hive rig to disk. Will save rig, mesh, and animation etc. \n" \
                  "Use this tool for `export selection` with a Hive rig to a new Maya scene. \n\n" \
                  "All geometry must be placed inside the Hive group `rigName_geo_hrc`. \n" \
                  "The single hierarchy skeleton must be inside the group `rigName_deformLayer_hrc`. \n" \
                  "Supports custom joints parented to the Hive skeleton. "
        self.exportBtn = elements.styledButton("Export Hive Rig As .MA",
                                               icon="maya",
                                               toolTip=toolTip,
                                               minWidth=uic.BTN_W_ICN_MED,
                                               parent=parent)

    def updateRigs(self, rigNames):
        oldPropertyValue = self.rigListCombo.currentText()
        self.rigListCombo.clear()
        self.rigListCombo.addItems(rigNames)
        self.rigListCombo.setToText(oldPropertyValue)

    def setCurrentRig(self, rigName):
        self.rigListCombo.setToText(rigName)


class GuiCompact(GuiWidgets):
    def __init__(self, parent=None, properties=None, toolsetWidget=None):
        """Adds the layout building the compact version of the GUI:

            default uiMode - 0 is advanced (UI_MODE_COMPACT)

        :param parent: the parent of this widget
        :type parent: QtWidgets.QWidget
        :param properties: the properties dictionary which tracks all the properties of each widget for UI modes
        :type properties: :class:`toolsetwidget.PropertiesDict`
        """
        super(GuiCompact, self).__init__(parent=parent, properties=properties,
                                         toolsetWidget=toolsetWidget)
        # Main Layout ---------------------------------------
        mainLayout = elements.vBoxLayout(self,
                                         margins=(uic.WINSIDEPAD, uic.WINBOTPAD, uic.WINSIDEPAD, uic.WINBOTPAD),
                                         spacing=uic.SLRG)
        saveDivider = elements.LabelDivider(text="Save", parent=parent)

        rigLayout = elements.hBoxLayout(spacing=uic.SLRG, margins=(uic.REGPAD, 0, uic.REGPAD, 0))
        rigLayout.addWidget(self.rigListCombo, 1)

        filePathLayout = elements.hBoxLayout(spacing=uic.SLRG, margins=(uic.REGPAD, 0, uic.REGPAD, 0))
        filePathLayout.addWidget(self.filePathEdit, 1)

        buttonLayout = elements.hBoxLayout(spacing=uic.SPACING, margins=(uic.SMLPAD, 0, uic.SMLPAD, 0))
        buttonLayout.addWidget(self.exportBtn, 10)

        mainLayout.addWidget(self.rigDivider)
        mainLayout.addLayout(rigLayout)

        mainLayout.addWidget(self.filePathDivider)
        mainLayout.addLayout(filePathLayout)

        mainLayout.addWidget(saveDivider)
        mainLayout.addLayout(buttonLayout)
