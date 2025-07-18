from zoo.apps.hiveartistui import model
from zoo.apps.hiveartistui.views import componentsettings


class JawComponentModel(model.ComponentModel):
    """Base Class for Vchain class and subclasses to support better UI
    organization.
    """
    componentType = "jaw"

    def createWidget(self, componentWidget, parentWidget):
        return JawSettingsWidget(componentWidget,
                                     parentWidget,
                                     componentModel=self)


class JawSettingsWidget(componentsettings.ComponentSettingsWidget):
    showSpaceSwitching = True

    def __init__(self, componentWidget, parent, componentModel):
        super(JawSettingsWidget, self).__init__(componentWidget, parent, componentModel)

    def initUi(self):
        layout = self.layout()

        guideLayerDef = self.componentModel.component.definition.guideLayer
        primarySettings = guideLayerDef.guideSettings(
            "createBSDifferentiator",
        )

        toolTip = ""
        componentsettings.createBooleanWidget(
            self, primarySettings["createBSDifferentiator"], "Create BlendShape Differentiator",
            layout, self.settingCheckboxChanged,toolTip
        )
        self.createSpaceLayout()
        self.createNamingConventionLayout()
        self.createDeformSettingsLayout()
