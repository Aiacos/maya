from zoo.apps.hiveartistui import model
from zoo.apps.hiveartistui.views import componentsettings
from zoo.libs.pyqt.widgets import elements


class GodNodeComponentModel(model.ComponentModel):
    """Base Class for Vchain class and subclasses to support better UI
    organization.
    """
    componentType = "godnodecomponent"

    def createWidget(self, componentWidget, parentWidget):
        return GodNodeSettingsWidget(componentWidget,
                                     parentWidget,
                                     componentModel=self)


class GodNodeSettingsWidget(componentsettings.ComponentSettingsWidget):
    showSpaceSwitching = False

    def __init__(self, componentWidget, parent, componentModel):
        super(GodNodeSettingsWidget, self).__init__(componentWidget, parent, componentModel)

    def initUi(self):
        layout = self.layout()

        guideLayerDef = self.componentModel.component.definition.guideLayer
        primarySettings = guideLayerDef.guideSettings(
            "godNodeVis",
            "offsetVis",
            "rootMotionVis",
            "rootJoint",
            "supportsNonUniformScale"
        )

        toolTip = ""
        componentsettings.createBooleanWidget(
            self, primarySettings["rootJoint"], "Root Joint", layout, self.settingCheckboxChanged,toolTip
        )
        if "supportsNonUniformScale" in primarySettings:
            componentsettings.createBooleanWidget(
                self,
                primarySettings["supportsNonUniformScale"],
                "Support Non-Uniform Scale",
                layout,
                self.settingCheckboxChanged,
                toolTip,
            )
        visLayout = elements.hBoxLayout()
        componentsettings.createBooleanWidget(
            self, primarySettings["godNodeVis"], "God Node Visibility", visLayout, self.settingCheckboxChanged, toolTip
        )
        componentsettings.createBooleanWidget(
            self, primarySettings["offsetVis"], "Offset Visibility", visLayout, self.settingCheckboxChanged, toolTip
        )
        componentsettings.createBooleanWidget(
            self, primarySettings["rootMotionVis"], "Root Motion Visibility", visLayout, self.settingCheckboxChanged, toolTip
        )

        layout.addLayout(visLayout)
        self.createSpaceLayout()
        self.createNamingConventionLayout()
        self.createDeformSettingsLayout()
