import os
from collections import OrderedDict

from zoo.apps.hiveartistui import uiinterface
from zoo.apps.toolsetsui.widgets import toolsetwidget
from zoo.libs.hive import api as hiveapi
from zoo.libs.maya.api import anim
from zoo.libs.maya.cmds.filemanage import saveexportimport
from zoo.libs.maya.utils import fbx as fbxutils
from zoo.libs.maya.utils import general
from zoo.libs.pyqt import uiconstants as uic
from zoo.libs.pyqt.widgets import elements
from zoo.libs.utils import output
from zoovendor.Qt import QtWidgets

from zoo.libs.utils import general as libgeneral

if libgeneral.TYPE_CHECKING:
    from zoo.libs.hive.library.exporters import fbxexporter

UI_MODE_COMPACT = 0
UI_MODE_ADVANCED = 1

WORLD_UP_LIST = ["Y", "Z"]

FBX_WORLD_UP_KEY = "worldUp"
FBX_VERSION_KEY = "fbxVersion"
PRESET_DICT = OrderedDict()

PRESET_DICT['Custom Preset - None'] = {}
PRESET_DICT['3dsMax 2018'] = {FBX_WORLD_UP_KEY: "Z",
                              FBX_VERSION_KEY: "FBX 2018"}
PRESET_DICT['3dsMax 2019'] = {FBX_WORLD_UP_KEY: "Z",
                              FBX_VERSION_KEY: "FBX 2019"}
PRESET_DICT['3dsMax 2020'] = {FBX_WORLD_UP_KEY: "Z",
                              FBX_VERSION_KEY: "FBX 2020"}
PRESET_DICT['Houdini 17'] = {FBX_WORLD_UP_KEY: "Y",
                             FBX_VERSION_KEY: "FBX 2018"}
PRESET_DICT['Unity 2021'] = {FBX_WORLD_UP_KEY: "Y",
                             FBX_VERSION_KEY: "FBX 2018"}
PRESET_DICT['Unreal 4'] = {FBX_WORLD_UP_KEY: "Y",
                           FBX_VERSION_KEY: "FBX 2018"}
PRESET_DICT['Unreal 5'] = {FBX_WORLD_UP_KEY: "Y",
                           FBX_VERSION_KEY: "FBX 2018"}

SAVE_SCENE_MSG = "Zoo needs to close and reload this Maya scene file after the FBX export completes.\n" \
                 "Save the current file to avoid losing changes?"


class HiveRigExportToolset(toolsetwidget.ToolsetWidget):
    id = "hiveFbxRigExport"
    info = "Hive Fbx rig export tool."
    uiData = {"label": "Hive Export FBX",
              "icon": "hiveExportFbx",
              "tooltip": "Provides an Fbx exporter for hive rigs.",
              "defaultActionDoubleClick": False,
              "helpUrl": "https://create3dcharacters.com/maya-tool-hive-export-fbx"}

    def preContentSetup(self):
        general.loadPlugin("fbxmaya")
        # force to 2018 since anything below this isn't support by games
        self._fbxVersions = list(fbxutils.availableFbxVersions(ignoreBeforeVersion="2018"))

    def contents(self):
        """The UI Modes to build, compact, medium and or advanced """
        return [self.initCompactWidget()]

    def initCompactWidget(self):
        """Builds the Compact GUI (self.compactWidget) """
        self.compactWidget = GuiCompact(parent=self, properties=self.properties, toolsetWidget=self)
        return self.compactWidget

    def postContentSetup(self):
        """Last of the initialize code"""
        self.uiConnections()
        # Update a rig list done in post because we have signals getting emitted by
        # hive UI which require a reload of the list as well.
        self._rigStateChanged()

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
        general.loadPlugin("fbxmaya")
        # temporary so we grab 2018 by default, later we'll have presets.
        total = len(list(fbxutils.availableFbxVersions(ignoreBeforeVersion="2018")))
        timeInfo = anim.currentTimeInfo()
        return [
            {"name": "triangulateCheckBox", "value": 1},
            {"name": "blendshapeCheckBox", "value": 1},
            {"name": "fbxFormatCombo", "value": 0},
            {"name": "worldAxisCombo", "value": 0},
            {"name": "rigListCombo", "value": 0},
            {"name": "fbxVersionCombo", "value": total - 1},
            {"name": "animationCheckBox", "value": 1},
            {"name": "meshCheckBox", "value": 1},
            {"name": "startEndFrameAnim", "value": [timeInfo["start"].value, timeInfo["end"].value]},
            {"name": "filePathEdit", "value": ""},
            {"name": "meshCheckBox", "value": 1},
            {"name": "skinningCheckBox", "value": 1}
        ]

    def widgets(self):
        """ Override base method for autocompletion

        :return:
        :rtype: list[GuiAdvanced or GuiCompact]
        """
        return super(HiveRigExportToolset, self).widgets()

    # ------------------
    # ENTER
    # ------------------

    def enterEvent(self, event):
        """When the cursor enters the UI update it"""
        self._rigStateChanged()

    # -------------------
    # HIVE CORE SIGNALS
    # -------------------

    def _rigStateChanged(self):
        sceneRigs = self.sceneRigs()
        for widget in self.widgets():
            widget.updateRigs(sceneRigs)

    def _currentRigChangedFromArtistUI(self, rigName):
        for widget in self.widgets():
            widget.setCurrentRig(rigName)

    def fbxVersionLabels(self):
        return [i for _, i in self._fbxVersions]

    # ------------------
    # LOGIC
    # ------------------
    def progressCallback(self, progress, message):
        output.displayInfo("Progress: {}% : {}".format(progress, message))

    def applyPreset(self):
        """Creates light and UI/Viewport settings from a dict preset

        """
        dict = list(PRESET_DICT.items())[self.properties.presetsCombo.value][1]
        if not dict:  # is "Custom Preset - None"
            return
        # Set Version --------------------------
        versionList = self.fbxVersionLabels()
        if dict[FBX_VERSION_KEY] in versionList:  # FBX version may not exist
            self.properties.fbxVersionCombo.value = versionList.index(dict[FBX_VERSION_KEY])
        else:
            self.properties.fbxVersionCombo.value = 0
        # Set WORLD UP --------------------------
        self.properties.worldAxisCombo.value = WORLD_UP_LIST.index(dict[FBX_WORLD_UP_KEY])
        # Update UI ---------------------------
        self.updateFromProperties()

    def sceneRigs(self):
        """

        :return:
        :rtype: list[:class:`zoo.libs.hive.base.rig.Rig`]
        """

        return list(hiveapi.iterSceneRigs())

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

    def _ensureFileSaved(self):
        """Checks if the file has already been saved. Return True or False so we know if we should
        continue exporting

        If not saved opens "save", or "cancel" window.  Returns the button pressed if "cancel"

        If "save" is clicked it will try to save the current file, if cancelled will return False

        :return buttonClicked: Whether or not to continue exporting
        :rtype buttonClicked: str
        """
        # TODO move this into elements under maya cmds
        sceneModified = saveexportimport.fileModified()

        if not sceneModified:  # Has been saved already so continue
            return True
        # Open dialog window with Save/Discard/Cancel buttons
        buttonPressed = elements.MessageBox.showSave(title="Save File", parent=self, message=SAVE_SCENE_MSG,
                                                     showDiscard=True)
        if buttonPressed == "save":
            if saveexportimport.saveAsDialogMaMb():  # file saved
                return True
            return False
        elif buttonPressed == "discard":
            return True
        return False

    def onExport(self):
        currentWidget = self.currentWidget()
        rigInstance = None
        for rig in self.sceneRigs():
            if rig.name() == currentWidget.rigListCombo.currentText():
                rigInstance = rig
                break
        if rigInstance is None:
            output.displayError("No valid Rig Selected in the UI")
            return
        compatWidget = self.widgets()[0]
        outputPath = compatWidget.filePathEdit.path()
        if not outputPath:
            output.displayError("Invalid export path: {}".format(outputPath))
            return
        if not self._ensureFileSaved():
            return
        exporter = hiveapi.Configuration().exportPluginForId("fbxExport")()
        exporter.onProgressCallbackFunc = self.progressCallback
        settings = exporter.exportSettings()  # type: fbxexporter.ExportSettings
        settings.outputPath = outputPath
        meshes = self.properties.meshCheckBox.value
        # the actual FBX not the display label
        settings.version = self._fbxVersions[self.properties.fbxVersionCombo.value][0]
        settings.shapes = self.properties.blendshapeCheckBox.value and meshes
        settings.axis = {0: "y", 1: "z"}.get(self.properties.worldAxisCombo.value)
        settings.triangulate = self.properties.triangulateCheckBox.value and meshes
        settings.ascii = self.properties.fbxFormatCombo.value  # 1 is ascii
        settings.animation = self.properties.animationCheckBox.value
        settings.startEndFrame = self.properties.startEndFrameAnim.value
        settings.meshes = meshes
        settings.skins = self.properties.skinningCheckBox.value and meshes
        settings.interactive = True

        exporter.execute(rigInstance, settings)

    def uiConnections(self):
        """Add all UI connections here, button clicks, on changed etc"""

        hiveUICore = uiinterface.instance()
        for widget in self.widgets():
            widget.exportBtn.clicked.connect(self.onExport)

            # widget.rigListCombo.currentIndexChanged.connect(self._currentRigChanged)
        if hiveUICore is not None:
            hiveUICore = hiveUICore.core()
            hiveUICore.rigRenamed.connect(self._rigStateChanged)
            hiveUICore.rigsChanged.connect(self._rigStateChanged)
            hiveUICore.currentRigChanged.connect(self._currentRigChangedFromArtistUI)
        self.compactWidget.presetsCombo.itemChanged.connect(self.applyPreset)


class GuiWidgets(QtWidgets.QWidget):
    def __init__(self, parent=None, properties=None, uiMode=None, toolsetWidget=None):
        """Builds the main widgets for all GUIs

        properties is the list(dictionaries) used to set logic and pass between the different UI layouts
        such as compact/adv etc

        :param parent: the parent of this widget
        :type parent: :class:`QtWidgets.QWidget`
        :param properties: the properties dictionary which tracks all the properties of each widget for UI modes
        :type properties: :class:`zoo.apps.toolsetsui.widgets.toolsetwidget.PropertiesDict`
        :param uiMode: 0 is compact ui mode, 1 is advanced ui mode
        :type uiMode: int
        :type toolsetWidget: :class:`HiveRigExportToolset`
        """
        super(GuiWidgets, self).__init__(parent=parent)
        self.properties = properties
        # Rig Combo -----------------------------
        toolTip = "Select the Hive rig from the scene to export. "
        self.rigListCombo = elements.ComboBoxRegular("",
                                                     items=[],
                                                     parent=self,
                                                     labelRatio=1,
                                                     boxRatio=3,
                                                     toolTip=toolTip)
        # Path Widget -----------------------------
        toolTip = "Set the FBX file path that will be saved to disk. "
        self.filePathEdit = elements.PathWidget(parent=self,
                                                path=self.properties.filePathEdit.value,
                                                toolTip=toolTip)
        self.filePathEdit.defaultBrowserPath = toolsetWidget.defaultBrowserPath
        self.filePathEdit.pathText.setPlaceHolderText("Set FBX export file path...")
        self.filePathEdit.setSearchFilter("*.fbx")
        # Mesh Checkbox -----------------------------
        toolTip = "Exports the geometry inside the group `HiveDeformLayer_hrc` on export. "
        self.meshCheckBox = elements.CheckBox("Meshes", enableMenu=False, toolTip=toolTip,
                                              checked=self.properties.meshCheckBox.value,
                                              parent=self)
        # Triangulate Checkbox -----------------------------
        toolTip = "Triangulate all geometry inside the group `HiveDeformLayer_hrc` on export. \n" \
                  "Game engines may require this setting checked on. "
        self.triangulateCheckBox = elements.CheckBox("Triangulate", enableMenu=False, toolTip=toolTip,
                                                     checked=self.properties.triangulateCheckBox.value,
                                                     parent=self)
        # Blendshape Checkbox -----------------------------
        toolTip = "Exports blendshape information related to geometry inside the group `HiveDeformLayer_hrc` "
        self.blendshapeCheckBox = elements.CheckBox("Blendshapes", enableMenu=False, toolTip=toolTip,
                                                    checked=self.properties.blendshapeCheckBox.value,
                                                    parent=self)
        # Blendshape Checkbox -----------------------------
        toolTip = "Exports skinning information related to geometry inside the group `HiveDeformLayer_hrc` "
        self.skinningCheckBox = elements.CheckBox("Skinning", enableMenu=False, toolTip=toolTip,
                                                  checked=self.properties.skinningCheckBox.value,
                                                  parent=self)
        # Animation Checkbox -----------------------------
        toolTip = "Exports FBX compatible animation within the frame range."
        self.animationCheckBox = elements.CheckBox("Animation", enableMenu=False, toolTip=toolTip,
                                                   checked=self.properties.animationCheckBox.value,
                                                   parent=self)
        # Start End Vector -----------------------------
        self.startEndFrameAnim = elements.VectorLineEdit(label="Start/End",
                                                         value=self.properties.startEndFrameAnim.value,
                                                         axis=("start", "end"),
                                                         toolTip=toolTip,
                                                         editRatio=2,
                                                         labelRatio=1,
                                                         parent=self)
        # Presets Combo -----------------------------
        toolTip = "Select a preset to determine the `World Up` and `FBX Version` supported. "
        self.presetsCombo = elements.ComboBoxRegular("",
                                                     items=list(PRESET_DICT.keys()),
                                                     parent=self,
                                                     labelRatio=1,
                                                     boxRatio=3,
                                                     toolTip=toolTip)
        # World Up Combo -----------------------------
        toolTip = "Export world up of the FBX. \n" \
                  "Some engines/programs support both Y or Z and you can \n" \
                  "use the settings in the receiving program to accept either."
        self.worldAxisCombo = elements.ComboBoxRegular("World Up",
                                                       items=["Y", "Z"],
                                                       setIndex=self.properties.worldAxisCombo.value,
                                                       parent=self,
                                                       toolTip=toolTip)
        # Format Combo -----------------------------
        toolTip = "Export as a binary file or ascii? \n" \
                  " - Binary:  File is compressed as binary code and is unreadable. \n" \
                  " - Ascii: File is exported as text, and can be edited. "
        self.fbxFormatCombo = elements.ComboBoxRegular("Format",
                                                       items=["binary", "ascii"],
                                                       setIndex=self.properties.fbxFormatCombo.value,
                                                       parent=self,
                                                       toolTip=toolTip)
        # Version Combo -----------------------------
        toolTip = "The version of FBX to export.  \n" \
                  "Many programs support older versions of FBX. "
        self.fbxVersionCombo = elements.ComboBoxRegular("Version",
                                                        items=toolsetWidget.fbxVersionLabels(),
                                                        setIndex=self.properties.fbxVersionCombo.value,
                                                        parent=self,
                                                        toolTip=toolTip)
        # Export Button -----------------------------
        toolTip = "FBX Exports the Hive skeleton and geometry inside the group `HiveDeformLayer_hrc` to disk. "
        self.exportBtn = elements.styledButton("Export Hive Rig As FBX",
                                               icon="hiveExportFbx",
                                               toolTip=toolTip,
                                               minWidth=uic.BTN_W_ICN_MED,
                                               parent=self)

        self.onAnimationCheckChanged(properties.animationCheckBox.value)
        self.onMeshCheckChanged(properties.meshCheckBox.value)
        # View only connections
        self.animationCheckBox.stateChanged.connect(self.onAnimationCheckChanged)
        self.meshCheckBox.stateChanged.connect(self.onMeshCheckChanged)

    def onAnimationCheckChanged(self, state):
        self.startEndFrameAnim.setEnabled(state)

    def onMeshCheckChanged(self, state):
        self.triangulateCheckBox.setEnabled(state)
        self.skinningCheckBox.setEnabled(state)
        self.blendshapeCheckBox.setEnabled(state)

    def updateRigs(self, rigs):
        oldPropertyValue = self.rigListCombo.currentText()
        self.rigListCombo.clear()
        self.rigListCombo.addItems([i.name() for i in rigs])
        self.rigListCombo.setToText(oldPropertyValue)

    def setCurrentRig(self, rigName):
        self.rigListCombo.setToText(rigName)


class GuiCompact(GuiWidgets):
    def __init__(self, parent=None, properties=None, uiMode=UI_MODE_COMPACT, toolsetWidget=None):
        """Adds the layout building the compact version of the GUI:

            default uiMode - 0 is advanced (UI_MODE_COMPACT)

        :param parent: the parent of this widget
        :type parent: QtWidgets.QWidget
        :param properties: the properties dictionary which tracks all the properties of each widget for UI modes
        :type properties: :class:`toolsetwidget.PropertiesDict`
        """
        super(GuiCompact, self).__init__(parent=parent, properties=properties, uiMode=uiMode,
                                         toolsetWidget=toolsetWidget)
        # Main Layout ---------------------------------------
        mainLayout = elements.vBoxLayout(self,
                                         margins=(uic.WINSIDEPAD, uic.WINBOTPAD, uic.WINSIDEPAD, uic.WINBOTPAD),
                                         spacing=uic.SLRG)
        rigDivider = elements.LabelDivider(text="Select Hive Rig", parent=self)
        filePathDivider = elements.LabelDivider(text="File Path", parent=self)
        geoDivider = elements.LabelDivider(text="Geometry", parent=self)
        animDivider = elements.LabelDivider(text="Animation", parent=self)
        fbxDivider = elements.LabelDivider(text="FBX Settings", parent=self)
        saveDivider = elements.LabelDivider(text="Save", parent=self)
        # Rig Layout -----------------------
        rigLayout = elements.hBoxLayout(spacing=uic.SLRG, margins=(uic.REGPAD, 0, uic.REGPAD, 0))
        rigLayout.addWidget(self.rigListCombo, 1)
        # File Path Layout -----------------------
        filePathLayout = elements.hBoxLayout(spacing=uic.SLRG, margins=(uic.REGPAD, 0, uic.REGPAD, 0))
        filePathLayout.addWidget(self.filePathEdit, 1)
        # Geometry Layout -----------------------
        geometryLayout = elements.hBoxLayout(spacing=uic.SLRG, margins=(uic.REGPAD, 0, uic.REGPAD, 0))
        geometryLayout.addWidget(self.meshCheckBox, 1)
        geometryLayout.addWidget(self.triangulateCheckBox, 1)
        geometryLayout2 = elements.hBoxLayout(spacing=uic.SLRG, margins=(uic.REGPAD, 0, uic.REGPAD, 0))
        geometryLayout2.addWidget(self.skinningCheckBox, 1)
        geometryLayout2.addWidget(self.blendshapeCheckBox, 1)
        # Anim Layout -----------------------
        animLayout = elements.hBoxLayout(spacing=uic.SLRG, margins=(uic.REGPAD, 0, uic.REGPAD, 0))
        animLayout.addWidget(self.animationCheckBox, 1)
        animLayout.addWidget(self.startEndFrameAnim, 1)
        # Presets Layout -----------------------
        presetLayout = elements.hBoxLayout(spacing=uic.SLRG, margins=(uic.REGPAD, 0, uic.REGPAD, 0))
        presetLayout.addWidget(self.presetsCombo, 1)
        # Other Settings Layout -----------------------
        fbxLayout = elements.hBoxLayout(spacing=uic.SVLRG, margins=(uic.REGPAD, 0, uic.REGPAD, 0))
        fbxLayout.addWidget(self.worldAxisCombo, 1)
        fbxLayout.addWidget(self.fbxFormatCombo, 1)
        fbxLayout.addWidget(self.fbxVersionCombo, 1)
        # Button Layout -----------------------
        buttonLayout = elements.hBoxLayout(spacing=uic.SLRG, margins=(uic.SMLPAD, 0, uic.SMLPAD, 0))
        buttonLayout.addWidget(self.exportBtn, 1)
        # Main Layout ---------------------------------------
        mainLayout.addWidget(rigDivider)
        mainLayout.addLayout(rigLayout)
        mainLayout.addWidget(filePathDivider)
        mainLayout.addLayout(filePathLayout)
        mainLayout.addWidget(geoDivider)
        mainLayout.addLayout(geometryLayout)
        mainLayout.addLayout(geometryLayout2)
        mainLayout.addWidget(animDivider)
        mainLayout.addLayout(animLayout)
        mainLayout.addWidget(fbxDivider)
        mainLayout.addLayout(presetLayout)
        mainLayout.addLayout(fbxLayout)
        mainLayout.addWidget(saveDivider)
        mainLayout.addLayout(buttonLayout)
