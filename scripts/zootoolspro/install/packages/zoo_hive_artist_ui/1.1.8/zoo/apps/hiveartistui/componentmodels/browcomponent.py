from functools import partial

from maya import cmds

from zoo.core.util import strutils
from zoo.libs.hive.library.subsystems import browsubsystem
from zoo.libs.commands import hive
from zoo.apps.hiveartistui import model
from zoo.apps.hiveartistui.views import componentsettings
from zoo.libs.maya import zapi
from zoo.libs.maya.cmds.objutils import selection
from zoo.libs.pyqt.widgets import elements
from zoo.libs.pyqt import uiconstants
from zoo.libs.utils import output


class BrowComponentModel(model.ComponentModel):
    """Base Class for Vchain class and subclasses to support better UI
    organization.
    """

    componentType = "browcomponent"

    def createWidget(self, componentWidget, parentWidget):
        return BrowSettingsWidget(componentWidget, parentWidget, componentModel=self)


class BrowSettingsWidget(componentsettings.ComponentSettingsWidget):
    showSpaceSwitching = False

    def __init__(self, componentWidget, parent, componentModel):
        super(BrowSettingsWidget, self).__init__(
            componentWidget, parent, componentModel
        )
        self.jointPosLayouts = {}
        self.advancedFrameLayout = None
        self.outerJointWidget = None
        self.jointCountWidget = None

    def initUi(self):
        guideSettings = (
            self.componentModel.component.definition.guideLayer.guideSettings(
                "jointCount",
                "outerJointCount",
                "separateJointCounts",
                "jointRotationFollowsCurve"
            )
        )
        mainLayout = self.layout()
        self._createUI(
            parentLayout=mainLayout,
            guideSettings=guideSettings
        )

        if self.showSpaceSwitching:
            self.createSpaceLayout()
        self.createNamingConventionLayout()
        self.createDeformSettingsLayout()

    def _createUI(self, parentLayout, guideSettings):
        componentsettings.createRadioWidget(self, [None, None],
                                            ["All", "Separate Joint Counts"], parentLayout,
                                            self.onJointCountModeChanged, toolTips=None)
        countLayout = elements.hBoxLayout(spacing=uiconstants.SPACING)
        boolLayout = elements.hBoxLayout(spacing=uiconstants.SPACING)
        self.jointCountWidget = componentsettings.createIntWidget(
            self,
            guideSettings["jointCount"],
            "Joint Count",
            countLayout,
            self._jointCountChanged,
            toolTip=None,
        )
        self.outerJointWidget = componentsettings.createIntWidget(
            self,
            guideSettings["outerJointCount"],
            "Outer Joint Count",
            countLayout,
            self._jointCountChanged,
            toolTip=None,
        )
        self.outerJointWidget.setEnabled(guideSettings["separateJointCounts"].value)
        componentsettings.createBooleanWidget(
            self,
            guideSettings["jointRotationFollowsCurve"],
            "Joint Rotation Follow Curve",
            boolLayout,
            self.settingCheckboxChanged,
            toolTip=None,
        )

        parentLayout.addLayout(countLayout)
        parentLayout.addLayout(boolLayout)

        layout = elements.hBoxLayout(spacing=uiconstants.SPACING)
        lidBtn = elements.styledButton(
            "Set Brow Curve",
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
        layout.addWidget(lidBtn, 2)
        layout.addWidget(lidDeleteBtn)
        parentLayout.addLayout(layout)
        lidBtn.clicked.connect(self._onCreateCurve)
        lidDeleteBtn.clicked.connect(self._deleteCurve)

        self.advancedFrameLayout = elements.CollapsableFrameThin(
            "Advanced", parent=self, collapsed=True
        )
        self.createJointCountParams(self.advancedFrameLayout)
        parentLayout.addWidget(self.advancedFrameLayout)
        self.advancedFrameLayout.toggled.connect(
            partial(self.componentWidget.tree.updateTreeWidget, delay=True)
        )

    def onJointCountModeChanged(self, event):
        self.outerJointWidget.setEnabled(event.index == 1)
        guideLayerDef = self.componentModel.component.definition.guideLayer
        settings = guideLayerDef.guideSettings("jointCount", "outerJointCount")
        jointCount, outerJointCount = settings["jointCount"].value, settings["outerJointCount"].value

        if event.index == 0:  # not separate so join the counts together
            outJointCount = jointCount + outerJointCount
        else:
            twoThirdsValue = (jointCount * 2) // 3
            outJointCount = twoThirdsValue
            outerJointCount = jointCount - twoThirdsValue
        hive.updateGuideSettings(
            self.componentModel.component, {"separateJointCounts": bool(event.index),
                                            "jointCount": outJointCount, "outerJointCount": outerJointCount}
        )
        self.jointCountWidget.setValue(outJointCount, updateText=True)
        self.outerJointWidget.setValue(outerJointCount, updateText=True)

    def _jointCountChanged(self, widget, setting):
        oldValue, newValue = setting.value, widget.value()
        self.settingNumericChanged(widget, setting)
        self.createJointCountParams(self.advancedFrameLayout, oldValue, newValue)

        self.componentWidget.tree.updateTreeWidget(delay=True)

    def createJointCountParams(self, parent, oldValue=0, newValue=0):
        subsystem = self.componentModel.component.subsystems()["brow"]  # type: browsubsystem.BrowSubsystem
        paramNames = subsystem.guideJntParams()

        if newValue < oldValue:
            ratioWidgets = self.jointPosLayouts
            for paramName in paramNames[newValue:]:
                wid = ratioWidgets.get(paramName)
                if wid is not None:
                    wid.deleteLater()
        else:
            guideLayerDef = self.componentModel.component.definition.guideLayer
            for paramName in paramNames:
                param = guideLayerDef.guideSetting(paramName)
                existingParamWidget = self.jointPosLayouts.get(paramName)
                if existingParamWidget is not None and param is None:
                    existingParamWidget.deleteLater()
                    del self.jointPosLayouts[paramName]
                    continue
                if param is None:
                    continue

                if existingParamWidget is not None:
                    existingParamWidget.setValue(param.value)
                else:
                    settingWidget = componentsettings.createFloatWidget(
                        self,
                        param,
                        strutils.titleCase(param.name),
                        parent,
                        self.settingNumericChanged,
                        toolTip=None,
                    )
                    self.jointPosLayouts[param.name] = settingWidget

    def _deleteCurve(self):
        subsystem = self.componentModel.component.subsystems()[
            "brow"
        ]  # type: browsubsystem.BrowSubsystem
        subsystem.deleteGuideCurve()

    def _onCreateCurve(self):
        sel = cmds.ls(orderedSelection=True, long=True)
        if not sel:
            output.displayError("No Edges selected")
            return
        selType = selection.componentSelectionType(sel)
        if selType == "object":
            output.displayError("No Edges selected")
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

        subsystems = self.componentModel.component.subsystems()
        createdCurve = subsystems["brow"].createGuideCurve(meshObj, vertexIndices)
        if not createdCurve:
            output.displayError("At least 3 edges must be selected to create the lid curve")
            return
        self.componentWidget.tree.updateTreeWidget(delay=False)
