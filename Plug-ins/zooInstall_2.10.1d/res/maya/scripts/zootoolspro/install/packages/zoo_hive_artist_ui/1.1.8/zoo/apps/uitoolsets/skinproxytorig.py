""" Simple UI for converting a skeleton into a skin proxy scalable mesh with live mirorring on the left and right joints.

"""

from zoovendor.Qt import QtWidgets, QtCore

from zoo.libs.utils import output
from zoo.apps.toolsetsui.widgets import toolsetwidget
from zoo.libs.pyqt import uiconstants as uic
from zoo.libs.pyqt.widgets import elements

from zoo.apps.toolsetsui import toolsetui, toolsetcallbacks
from zoo.libs.hive.library.matching import buildskinfromskele
from zoo.libs.maya.cmds.rig import skelemirror

import zoo.libs.maya.cmds.hotkeys.definedhotkeys as hk
from zoo.libs.hive.characterizer import skinproxy

UI_MODE_COMPACT = 0
UI_MODE_ADVANCED = 1


class SkinProxyToRig(toolsetwidget.ToolsetWidget):
    id = "skinProxyToRig"
    info = "Turns a skin proxy skeleton into a Hive Rig."
    uiData = {"label": "Skin Proxy To Rig (beta)",
              "icon": "superhero",
              "tooltip": "Turns a skin proxy skeleton into a Hive Rig.",
              "defaultActionDoubleClick": False,
              "helpUrl": "https://create3dcharacters.com/maya-tool-skin-proxy-to-hive-rig/"}

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
        self.autoAddMeshAndJoint()

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
        return super(SkinProxyToRig, self).currentWidget()

    def widgets(self):
        """ Override base method for autocompletion

        :return:
        :rtype: list[GuiAdvanced or GuiCompact]
        """
        return super(SkinProxyToRig, self).widgets()

    # ------------------
    # SEND RECEIVE
    # ------------------

    def global_sendProxyImported(self, proxyImported=False):
        """Updates all GUIs with the copied shader"""
        toolsets = toolsetui.toolsetsByAttr(attr="global_receiveProxyImported")
        for tool in toolsets:
            tool.global_receiveProxyImported(proxyImported=proxyImported)

    def global_receiveProxyImported(self, proxyImported=False):
        """Receives the copied proxy import/delete from other GUIs"""
        if proxyImported:
            self.autoAddMeshAndJoint()
        else:
            self.properties.baseJointStr.value = ""
            self.properties.skinProxyGeoStr.value = ""
            self.updateFromProperties()

    # ------------------
    # LOGIC
    # ------------------

    def autoAddMeshAndJoint(self):
        """On the open of the UI automatically adds base joint and skin proxy geometry if they exist in the scene."""
        baseJnt, proxyMesh = buildskinfromskele.autoGetSkinProxyGeoAndBaseJoint()
        self.properties.baseJointStr.value = baseJnt
        self.properties.skinProxyGeoStr.value = proxyMesh
        self.updateFromProperties()

    def inputBaseJoint(self):
        """Sets the base joint for the skin proxy skeleton"""
        self.properties.baseJointStr.value, skinValue = buildskinfromskele.skinProxyBaseJoint()
        if skinValue:
            self.properties.skinProxyGeoStr.value = skinValue
        self.updateFromProperties()

    def inputProxyGeo(self):
        """Sets the skin proxy geometry"""
        self.properties.skinProxyGeoStr.value, rootJoint = buildskinfromskele.skinProxySkinnedGeo()
        if rootJoint:
            self.properties.baseJointStr.value = rootJoint
        self.updateFromProperties()

    def inputTargetSkin(self):
        """Sets the target skin objects"""
        self.compactWidget.targetSkinObjectsStr.setText(buildskinfromskele.targetGeoObjectsAsString())
        self.updateFromProperties()

    def update_progress(self, progress, message):
        """Update the progress bar

        :param progress: The progress value 0-6
        :type progress: int
        :param message: The message to display
        :type message: str
        """
        if message:
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
            if message:
                output.displayInfo(message)  # Rig completed, or failed if no message
            self.toolsetWidget.treeWidget.updateTree()
            return
        elif progress == 0:
            self.compactWidget.progressDivider.setVisible(True)
            self.compactWidget.progressBarWidget.setVisible(True)
            self.compactWidget.progressMessageLabel.setVisible(True)
            self.toolsetWidget.treeWidget.updateTree()

    @toolsetwidget.ToolsetWidget.undoDecorator
    def skinProxyToRig(self):
        """Creates custom rig groups from the selected Hive joints
        """
        skinTransfer = True
        buildRig = True
        skinJointTransfer = True
        hideProxySkeleton = True
        hideProxyGeo = True
        hideHiveProxyGeo = True

        if not self.properties.baseJointStr.value:
            output.displayWarning("Please add the `Skin Proxy Base Joint` to the UI.")
            self.update_progress(100, "")
            return
        skinTargetList = list()
        skinTargetsStr = self.compactWidget.targetSkinObjectsStr.toPlainText()

        if skinTargetsStr:
            skinTargetList = skinTargetsStr.split(",")
        buildInstance = buildskinfromskele.BuildAndSkinFromSkeleton(skinProxyGeo=self.properties.skinProxyGeoStr.value,
                                                                    skinTargetGeoList=skinTargetList)

        self.update_progress(0, "Status: Checking Scene")
        if not buildInstance.stage1_basicChecks(self.properties.baseJointStr.value):
            self.update_progress(100, "")
            return

        self.update_progress(5, "Status: Transfer Skin Proxy Weights To Hive Proxy Mesh")
        buildInstance.stage2_duplicateSkinProxyMesh()

        self.update_progress(10, "Status: Building New Hive Template (Please Wait)")
        if not buildInstance.stage3_buildRig(self.properties.baseJointStr.value, buildRig):
            self.update_progress(100, "")
            return

        self.update_progress(15, "Status: Matching Hive Guides To The Skin Proxy Skeleton")
        buildInstance.stage4_matchGuides()

        self.update_progress(30, "Status: Aligning Controls and Hive Symmetry")
        buildInstance.stage5_FinalAlignment()

        self.update_progress(45, "Status: Matching joint counts on the Hive template, and symmetry")
        buildInstance.stage6_twistingSpineCount()

        self.update_progress(60, "Status: Creating the Hive Deformation Skeleton")
        buildInstance.stage7_buildHiveSkeleton()

        self.update_progress(65, "Status: Transferring Weights To Hive Skeleton (Please Wait)")
        buildInstance.stage8_transferJointWeights(skinJointTransfer)

        self.update_progress(90, "Status: Polishing The Hive Rig")
        buildInstance.stage9_polishRig(self.properties.baseJointStr.value,
                                       hideProxySkeleton,
                                       hideProxyGeo,
                                       hideHiveProxyGeo)
        self.update_progress(100, "Status: Rig Completed")

    def openHiveWindow(self):
        """Opens the Hive window"""
        import zoo.libs.maya.cmds.hotkeys.definedhotkeys as hk
        hk.open_hiveArtistUI()

    @toolsetwidget.ToolsetWidget.undoDecorator
    def selectHierarchy(self):
        """Selects the hierarchy of the skeleton"""
        skelemirror.selectHierarchy()

    @toolsetwidget.ToolsetWidget.undoDecorator
    def importSkinProxy(self):
        skinproxy.importSkinProxy()
        self.autoAddMeshAndJoint()
        self.global_sendProxyImported(proxyImported=True)

    @toolsetwidget.ToolsetWidget.undoDecorator
    def deleteSkinProxy(self):
        skinproxy.deleteSkinProxy()
        self.properties.baseJointStr.value = ""
        self.properties.skinProxyGeoStr.value = ""
        self.updateFromProperties()
        self.global_sendProxyImported(proxyImported=False)

    def openCharacterizer(self):
        hk.open_hiveCharacterizer()

    # ------------------
    # CONNECTIONS
    # ------------------

    def uiConnections(self):
        """Add all UI connections here, button clicks, on changed etc"""
        for widget in self.widgets():
            widget.skinProxyToRigBtn.clicked.connect(self.skinProxyToRig)
            widget.inputBaseJointBtn.clicked.connect(self.inputBaseJoint)
            widget.inputProxyGeoBtn.clicked.connect(self.inputProxyGeo)
            widget.inputTargetSkinBtn.clicked.connect(self.inputTargetSkin)
            widget.importSkinProxyBtn.clicked.connect(self.importSkinProxy)
            widget.openCharacterizerBtn.clicked.connect(self.openCharacterizer)
            widget.deleteSkinProxyBtn.clicked.connect(self.deleteSkinProxy)
            widget.selectHierarchyBtn.clicked.connect(self.selectHierarchy)
            widget.hiveBtn.clicked.connect(self.openHiveWindow)


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
        # Base Joint Text Edit ----------------------------------------------
        toolTip = "Automatically tries to add the base joint/ctrl in the scene and its proxy mesh. \n" \
                  "You may also select then add the base joint/ctrl if many are in the scene. \n" \
                  "The base joint is the first joint in the Skin Proxy hierarchy and may also be a control."
        self.baseJointStr = elements.StringEdit(label="Skin Proxy Base Joint",
                                                parent=parent,
                                                editPlaceholder="god_M_god_jnt",
                                                toolTip=toolTip,
                                                editRatio=13,
                                                labelRatio=10)
        self.inputBaseJointBtn = elements.styledButton("",
                                                       "arrowLeft",
                                                       parent=parent,
                                                       toolTip=toolTip,
                                                       style=uic.BTN_TRANSPARENT_BG,
                                                       minWidth=15)
        # Base Joint Text Edit ----------------------------------------------
        toolTip = "Automatically tries to add the skin proxy geometry in the scene and its base joint. \n" \
                  "You may also select then add the geometry of a single skin proxy mesh if many are in the scene. \n" \
                  "Skin Proxies geometry is optional, without it the rig will be built without the skin transfer."
        self.skinProxyGeoStr = elements.StringEdit(label="Skin Proxy Skinned Geo",
                                                   parent=parent,
                                                   editPlaceholder="skinProxy_geo (optional)",
                                                   toolTip=toolTip,
                                                   editRatio=13,
                                                   labelRatio=10)
        self.inputProxyGeoBtn = elements.styledButton("",
                                                      "arrowLeft",
                                                      parent=parent,
                                                      toolTip=toolTip,
                                                      style=uic.BTN_TRANSPARENT_BG,
                                                      minWidth=15)
        # Target Skin Objects Text Edit ----------------------------------------------
        toolTip = "Select and add the target objects, these objects will be automatically skinned. \n" \
                  "Usually the final geometry of the character. \n" \
                  "These meshes should not be skinned and are optional."
        self.targetSkinObjectsStr = elements.TextEdit(placeholderText="Add geometry to be skinned. Eg. \n"
                                                                      "bodyHires_geo, hair_geo, shirt_geo \n"
                                                                      "(optional)",
                                                      parent=parent,
                                                      toolTip=toolTip,
                                                      minimumHeight=60,
                                                      maximumHeight=60)
        self.inputTargetSkinBtn = elements.styledButton("",
                                                        "arrowLeft",
                                                        parent=parent,
                                                        toolTip=toolTip,
                                                        style=uic.BTN_TRANSPARENT_BG,
                                                        minWidth=15)
        # Skele To Skin Proxy ---------------------------------------
        tooltip = "Convert a Skin Proxy Hive Skeleton into a Hive Rig.\n" \
                  "Skin Proxies can be scaled to match a new character's proportions. \n" \
                  "The Proxy skinning can be optionally transferred to target meshes. \n\n" \
                  "Complete the UI and press to convert the Skin Proxy to a Hive Rig."
        self.skinProxyToRigBtn = elements.styledButton("Skin Proxy Skeleton To Hive Rig",
                                                       parent=parent,
                                                       icon="superhero",
                                                       toolTip=tooltip,
                                                       style=uic.BTN_DEFAULT)
        # Open The Characterizer ---------------------------------------
        tooltip = "Open the characterizer UI to change proportions."
        self.openCharacterizerBtn = elements.styledButton("",
                                                          parent=parent,
                                                          icon="settingSliders",
                                                          toolTip=tooltip,
                                                          style=uic.BTN_DEFAULT)
        # Import Skin Proxy ---------------------------------------
        tooltip = "Import a skin proxy rig into the scene."
        self.importSkinProxyBtn = elements.styledButton("",
                                                        parent=parent,
                                                        icon="importArrow",
                                                        toolTip=tooltip,
                                                        style=uic.BTN_DEFAULT)
        # Hive Button --------------------------------------
        tooltip = "Open The Hive UI"
        self.hiveBtn = elements.styledButton("",
                                             icon="hive",
                                             toolTip=tooltip,
                                             style=uic.BTN_DEFAULT,
                                             parent=parent)
        # Select Hierarchy Button --------------------------------------
        tooltip = "Select the hierarchy of a selected joint/control. "
        self.selectHierarchyBtn = elements.styledButton("",
                                                        icon="cursorSelect",
                                                        toolTip=tooltip,
                                                        style=uic.BTN_DEFAULT,
                                                        parent=parent)
        # Delete Skin Proxy Button --------------------------------------
        tooltip = "Delete the Skin Proxy from the scene. "
        self.deleteSkinProxyBtn = elements.styledButton("",
                                                        icon="trash",
                                                        toolTip=tooltip,
                                                        style=uic.BTN_DEFAULT,
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
        # Base Jnt Layout ---------------------------------------
        baseJointLayout = elements.hBoxLayout(margins=(0, 0, 0, 0), spacing=uic.SREG)
        baseJointLayout.addWidget(self.baseJointStr, 10)
        baseJointLayout.addWidget(self.inputBaseJointBtn, 1)
        # Skin Proxy Geo Layout ---------------------------------------
        skinProxyGeoLayout = elements.hBoxLayout(margins=(0, 0, 0, 0), spacing=uic.SREG)
        skinProxyGeoLayout.addWidget(self.skinProxyGeoStr, 10)
        skinProxyGeoLayout.addWidget(self.inputProxyGeoBtn, 1)
        # Base Jnt Layout ---------------------------------------
        targetGeoLayout = elements.hBoxLayout(margins=(0, 0, 0, 0), spacing=uic.SREG)
        targetGeoLayout.addWidget(self.targetSkinObjectsStr, 10)
        targetGeoLayout.addWidget(self.inputTargetSkinBtn, 1, QtCore.Qt.AlignTop)
        # Button Layout ---------------------------------------
        btnLayout = elements.hBoxLayout(margins=(0, 0, 0, 0), spacing=uic.SPACING)
        btnLayout.addWidget(self.skinProxyToRigBtn, 20)
        btnLayout.addWidget(self.openCharacterizerBtn, 1)
        btnLayout.addWidget(self.importSkinProxyBtn, 1)
        btnLayout.addWidget(self.selectHierarchyBtn, 1)
        btnLayout.addWidget(self.hiveBtn, 1)
        btnLayout.addWidget(self.deleteSkinProxyBtn, 1)

        # Add To Main Layout ---------------------------------------
        mainLayout.addLayout(baseJointLayout)
        mainLayout.addLayout(skinProxyGeoLayout)
        mainLayout.addLayout(targetGeoLayout)
        mainLayout.addLayout(btnLayout)
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
        # Add To Main Layout ---------------------------------------
