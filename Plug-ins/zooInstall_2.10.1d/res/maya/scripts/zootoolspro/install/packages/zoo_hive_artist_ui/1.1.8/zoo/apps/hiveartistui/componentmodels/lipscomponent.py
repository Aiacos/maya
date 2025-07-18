from functools import partial
from zoovendor.Qt import QtCore
from maya import cmds
from zoo.libs.hive import api as hiveapi
from zoo.libs.hive.library.subsystems import lipSystem
from zoo.apps.hiveartistui import model
from zoo.apps.hiveartistui.views import componentsettings
from zoo.apps.hiveartistui.views import guideselectwidget

from zoo.libs.maya import zapi
from zoo.libs.pyqt import uiconstants
from zoo.libs.pyqt.widgets import elements
from zoo.libs.maya.cmds.objutils import selection
from zoo.libs.utils import output


class MouthComponentModel(model.ComponentModel):
    """Base Class for Vchain class and subclasses to support better UI
    organization.
    """

    componentType = "mouthcomponent"

    def createWidget(self, componentWidget, parentWidget):
        return MouthSettingsWidget(componentWidget, parentWidget, componentModel=self)


class MouthSettingsWidget(componentsettings.ComponentSettingsWidget):
    showSpaceSwitching = False

    def __init__(self, componentWidget, parent, componentModel):
        self.ratioLayouts = {}
        self.ratioFrameLayouts = {}
        self.topLipDriverWidget = None
        self.botLipDriverWidget = None
        super(MouthSettingsWidget, self).__init__(
            componentWidget, parent, componentModel
        )

    def initUi(self):
        mainLayout = self.layout()
        innerLayout = elements.hBoxLayout()

        guideSettings = self.componentModel.component.definition.guideLayer.guideSettings(
            "lipJointCount", "lipCtrlCount"
        )
        subsystems = self.componentModel.component.subsystems()
        lipSubsystem = subsystems["lips"]
        self.topLipDriverWidget = DriverSelectWidget(rigModel=self.rigModel,
                                                     label="Top Lip Driver Guide",
                                                     toolTip="Select the guide that will be used as the driver\n "
                                                             "Expected to be the top lip of the Jaw",
                                                     buttonToolTip="Select the guide that will be used as the driver\n "
                                                                   "Expected to either be the top lip of the Jaw",
                                                     componentModel=self.componentModel,
                                                     parent=self,
                                                     driverId="upperLip")
        self.botLipDriverWidget = DriverSelectWidget(rigModel=self.rigModel,
                                                     componentModel=self.componentModel,
                                                     label="Bot Lip Driver Guide",
                                                     toolTip="Select the guide that will be used as the driver\n "
                                                             "Expected to be the bot lip of the Jaw",
                                                     buttonToolTip="Select the guide that will be used as the driver\n "
                                                                   "Expected to either be the bot lip of the Jaw",
                                                     parent=self,
                                                     driverId="lowerLip")
        toolTip = ("Set's the Selected nurbs surface as the surface mask.")
        surfaceMaskBtn = elements.styledButton(
            "Set Surface Mask",
            icon="sphere",
            parent=self,
            toolTip=toolTip,
            themeUpdates=False,
        )
        surfaceMaskBtn.clicked.connect(self._onSurfaceMaskSelected)
        self.topLipDriverWidget.itemSelected.connect(self._onDriverSelected)
        self.botLipDriverWidget.itemSelected.connect(self._onDriverSelected)
        mainLayout.addWidget(self.topLipDriverWidget)
        mainLayout.addWidget(self.botLipDriverWidget)
        mainLayout.addWidget(surfaceMaskBtn)
        self.lipSettingsLayout = elements.CollapsableFrameThin(
            "Lip Settings", parent=self, collapsed=True
        )

        self.lipSettingsLayout.toggled.connect(
            partial(self.componentWidget.tree.updateTreeWidget, delay=True)
        )

        mainLayout.addWidget(self.lipSettingsLayout)

        self._createLidUI(
            parentLayout=self.lipSettingsLayout,
            guideSettings=guideSettings,
            lipSubSystem=lipSubsystem,
        )

        mainLayout.addLayout(innerLayout)

        if self.showSpaceSwitching:
            self.createSpaceLayout()
        self.createNamingConventionLayout()
        self.createDeformSettingsLayout()

    def _createLidUI(self, parentLayout, guideSettings, lipSubSystem):

        componentsettings.createIntWidget(
            self,
            guideSettings["lipJointCount"],
            "Lip Joint Count(Per Lip)",
            parentLayout,
            partial(self._countChanged, lipSubSystem),
            toolTip="Sets the total per lip joint count, where the count needs to be an odd number ie. 11."
                    "where 5 would be created per side plus 1 for the center",
        )
        componentsettings.createIntWidget(
            self,
            guideSettings["lipCtrlCount"],
            "Lip Ctrl Count(Per Lip)",
            parentLayout,
            partial(self._countChanged, lipSubSystem),
            toolTip="Sets the total per lip ctrl count, where the count needs to be an odd number ie. 7."
                    "where 3 would be created per side plus 1 for the center",
        )
        self.createLipButton(
            label="Set Upr Lip Curve",
            curveId=lipSystem.UPR_LIP_CURVE_ID,
            parentLayout=parentLayout,
        )
        self.createLipButton(
            label="Set Lwr Lip Curve",
            curveId=lipSystem.LWR_LIP_CURVE_ID,
            parentLayout=parentLayout,
        )

    def createLipButton(self, label, curveId, parentLayout):
        layout = elements.hBoxLayout(spacing=uiconstants.SPACING)
        lidBtn = elements.styledButton(
            label,
            icon="3dManipulator",
            parent=self,
            toolTip="",
            themeUpdates=False,
        )
        lidDeleteBtn = elements.styledButton(
            "",
            icon="trash",
            parent=self,
            toolTip="",
            themeUpdates=False,
        )
        lidBtn.clicked.connect(partial(self._onCreateLipCurve, curveId))
        lidDeleteBtn.clicked.connect(partial(self._deleteLidCurve, curveId))
        layout.addWidget(lidBtn, 2)
        layout.addWidget(lidDeleteBtn)
        parentLayout.addLayout(layout)
        return layout, lidBtn, lidDeleteBtn

    def _countChanged(self, lipSubSystem, widget, setting):
        self.settingNumericChanged(widget, setting)
        self.componentWidget.tree.updateTreeWidget(delay=True)

    def _onDriverSelected(self, component, guide, drivenId):
        lipSystem = self.componentModel.component.subsystems()["lips"]
        lipSystem.setLipDriver(drivenId,
                               hiveapi.pathAsDefExpression((component.serializedTokenKey(), "outputLayer", guide.id())))

    def _deleteLidCurve(self, curveId):
        lipSubsys = self.componentModel.component.subsystems()[
            "lips"
        ]  # type: lipSystem.MouthSubsystem
        lipSubsys.deleteGuideCurve(curveId)
        edits = self.ratioLayouts.get(curveId, {})
        for ratioLayout in edits.values():
            ratioLayout.deleteLater()
        if edits:
            del self.ratioLayouts[curveId]

    def _onCreateLipCurve(self, curveId):
        sel = cmds.ls(orderedSelection=True, long=True)
        if not sel:
            output.displayError("No Edges selected")
            return
        subsystems = self.componentModel.component.subsystems()
        selType = selection.componentSelectionType(sel)
        if selType == "object":
            self.componentModel.component.serializeFromScene()
            subsystems["lips"].setGuideCurve(curveId, curve=zapi.nodeByName(sel[0]))
            return
        vertices = selection.convertSelection(type="vertices")
        if not vertices:
            output.displayError("No Edges selected")
            return

        meshObj, vertexIndices = None, []
        for i in vertices:
            meshName = i.partition(".")[0]
            meshObj = zapi.nodeByName(meshName)
            vertexRange = i[i.index("[") + 1: i.index("]")].split(":")
            if len(vertexRange) > 1:
                vertexIndices.extend(
                    list(range(int(vertexRange[0]), int(vertexRange[1]) + 1))
                )
            else:
                vertexIndices.append(int(vertexRange[0]))
        self.componentModel.component.serializeFromScene()
        createdCurve = subsystems["lips"].createGuideCurve(
            meshObj, vertexIndices, curveId
        )
        if not createdCurve:
            output.displayError(
                "At least 3 edges must be selected to create the lid curve"
            )
            return

    def _onSurfaceMaskSelected(self):
        surface = None
        for sel in zapi.selected(filterTypes=(zapi.kNodeTypes.kTransform,)):
            for shape in sel.iterShapes():
                apiType = shape.apiType()
                if apiType == zapi.kNodeTypes.kNurbsSurface:
                    surface = sel
                    break
        if not surface:
            output.displayError("No Nurbs Surface selected")
            return
        self.componentModel.component.serializeFromScene()
        subsystems = self.componentModel.component.subsystems()
        if subsystems["lips"].setSurfaceMask(surface):
            output.displayInfo("Surface mask successfully updated")

    def updateUi(self):
        super(MouthSettingsWidget, self).updateUi()
        self.topLipDriverWidget.updateCombo()
        self.botLipDriverWidget.updateCombo()


class DriverSelectWidget(guideselectwidget.GuideSelectWidget):
    itemSelected = QtCore.Signal(object, object, str)  # component, guide, driverId

    def __init__(self, rigModel,
                 label,
                 toolTip,
                 buttonToolTip,
                 componentModel=None,
                 parent=None,
                 driverId=None):
        super(DriverSelectWidget, self).__init__(rigModel,
                                                 label, toolTip, buttonToolTip,
                                                 componentModel, parent)
        self.driverId = driverId
        self._guideSelect.clicked.connect(self._onGuideSelected)

    def _hardRefresh(self):
        self._itemComboBox.blockSignals(True)
        self._itemComboBox.clear()
        self.itemData = [[None, None]]
        self._itemComboBox.addItem("")

        if not self.rigModel:
            self._itemComboBox.blockSignals(False)
            return
        comboSet = False
        compDrivers = self.componentModel.component.definition.drivers

        currentDriverExpr = hiveapi.DriverDef("", "", hiveapi.DriverMatrixConstParams([], "", False))
        for driver in compDrivers:
            if driver.label == self.driverId:
                currentDriverExpr = driver
        self.currentItem = None
        rig = self.rigModel.rig
        for comp in rig.iterComponents():
            if comp == self.componentModel.component:
                continue
            guideLayer = comp.guideLayer()
            if guideLayer is None:
                continue
            componentToken = comp.serializedTokenKey()
            idMapping = comp.idMapping()
            outputMap = idMapping[hiveapi.constants.OUTPUT_LAYER_TYPE]
            for guide in guideLayer.iterGuides(includeRoot=False):
                outputNode = outputMap.get(guide.id())
                if not outputNode:
                    continue
                self._itemComboBox.addItem(self.itemName(comp, guide))
                self.itemData.append([comp, guide])

                guideExpr = hiveapi.pathAsDefExpression((componentToken, "outputLayer", outputNode))
                if not comboSet:
                    if self.isCurrentUISelected(comp, guide):
                        comboSet = True
                        self._itemComboBox.setCurrentIndex(self._itemComboBox.count() - 1)
                        continue
                    for driverLabel, driverExpr in currentDriverExpr.params.drivers:
                        if guideExpr == driverExpr and not comboSet:
                            self._itemComboBox.setCurrentIndex(self._itemComboBox.count() - 1)

        self._itemComboBox.blockSignals(False)

    def _onGuideSelected(self):
        self._itemComboBox.blockSignals(True)
        for sel in zapi.selected():
            if not hiveapi.Guide.isGuide(sel):
                continue
            guide = hiveapi.Guide(sel.object())
            component = hiveapi.componentFromNode(guide)
            if not component or component == self.componentModel.component:
                continue
            outputId = component.idMapping()[hiveapi.constants.OUTPUT_LAYER_TYPE].get(guide.id())
            if not outputId:
                break
            lipSystem = self.componentModel.component.subsystems()["lips"]
            lipSystem.setLipDriver(self.driverId,
                                   hiveapi.pathAsDefExpression(
                                       (component.serializedTokenKey(), "outputLayer", outputId)))
            self._itemComboBox.setTexts(self.itemName(component, guide))
            break
        self._itemComboBox.blockSignals(False)

    def onValueChanged(self, event):
        """ on Value Changed

        :param event: Event with all the values related to the change.
        :type event: zoo.libs.pyqt.extended.combobox.ComboItemChangedEvent
        :return:
        :rtype:
        """
        data = self.itemData[self._itemComboBox.currentIndex()]
        self.itemSelected.emit(data[0], data[1], self.driverId)  # component, guide
        self.currentItem = data[0], data[1]
