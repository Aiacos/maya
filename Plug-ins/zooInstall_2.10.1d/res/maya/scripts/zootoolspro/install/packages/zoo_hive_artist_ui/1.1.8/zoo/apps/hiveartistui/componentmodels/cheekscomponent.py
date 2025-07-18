from zoovendor.Qt import QtCore
from zoo.libs.hive import api as hiveapi

from zoo.apps.hiveartistui import model
from zoo.apps.hiveartistui.views import componentsettings
from zoo.apps.hiveartistui.views import guideselectwidget
from zoo.libs.maya import zapi


class CheekComponentModel(model.ComponentModel):
    """Base Class for Vchain class and subclasses to support better UI
    organization.
    """

    componentType = "cheekcomponent"

    def createWidget(self, componentWidget, parentWidget):
        return CheekSettingsWidget(componentWidget, parentWidget, componentModel=self)


class CheekSettingsWidget(componentsettings.ComponentSettingsWidget):
    showSpaceSwitching = False

    def __init__(self, componentWidget, parent, componentModel):
        self.driverWidget = None  # type: DriverSelectWidget
        super(CheekSettingsWidget, self).__init__(
            componentWidget, parent, componentModel
        )

    def initUi(self):
        self.driverWidget = DriverSelectWidget(rigModel=self.rigModel,
                                               label="Driver Lip Guide",
                                               toolTip="Select the guide that will be used as the driver\n "
                                                       "Expected to be L/R of the mouth",
                                               buttonToolTip="Select the guide that will be used as the driver\n "
                                                             "Expected to be L/R of the mouth",
                                               componentModel=self.componentModel,
                                               parent=self)
        self.driverWidget.itemSelected.connect(self._onDriverSelected)
        layout = self.layout()
        layout.addWidget(self.driverWidget)

        if self.showSpaceSwitching:
            self.createSpaceLayout()
        self.createNamingConventionLayout()
        self.createDeformSettingsLayout()

    def updateUi(self):
        super(CheekSettingsWidget, self).updateUi()
        self.driverWidget.updateCombo()

    def _onDriverSelected(self, component, guide):

        idMapping = component.idMapping()
        componentToken = component.serializedTokenKey()
        validGuidesWithCtrls = idMapping[hiveapi.constants.RIG_LAYER_TYPE]

        definition = self.componentModel.component.definition
        existingDriver = None  # type: hiveapi.DriverDef or None
        for driver in definition.drivers:
            if driver.label == "lipCorner":
                existingDriver = driver
        if existingDriver:
            existingDriver.params = hiveapi.DriverDirectParams(
                driver=hiveapi.pathAsDefExpression((componentToken, "rigLayer", validGuidesWithCtrls[guide.id()])),
                driven="@{self.inputLayer}",
                driverAttribute="translate",
                drivenAttribute="lipCornerLocalTranslate"
            )
        else:
            definition.drivers.append(hiveapi.DriverDef("direct", "lipCorner",
                                                        params={
                                                            "driver": hiveapi.pathAsDefExpression(
                                                                (componentToken, "rigLayer",
                                                                 validGuidesWithCtrls[guide.id()])),
                                                            "driven": "@{self.inputLayer}",
                                                            "driverAttribute": "translate",
                                                            "drivenAttribute": "lipCornerLocalTranslate"
                                                        }))
        self.componentModel.component.saveDefinition(definition)
        self.driverWidget._itemComboBox.setTexts(self.driverWidget.itemName(component, guide))


class DriverSelectWidget(guideselectwidget.GuideSelectWidget):
    itemSelected = QtCore.Signal(object, object)  # component, guide, driverId

    def __init__(self, rigModel,
                 label,
                 toolTip,
                 buttonToolTip,
                 componentModel=None,
                 parent=None):
        super(DriverSelectWidget, self).__init__(rigModel,
                                                 label, toolTip, buttonToolTip,
                                                 componentModel, parent)
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
        currentDriverExpr = compDrivers[0] if compDrivers else hiveapi.DriverDef("", "",
                                                                                 hiveapi.DriverDirectParams("", "", "",
                                                                                                            ""))
        self.currentItem = None
        rig = self.rigModel.rig
        for comp in rig.iterComponents():
            if comp == self.componentModel.component:
                continue
            idMapping = comp.idMapping()
            componentToken = comp.serializedTokenKey()
            validGuidesWithCtrls = idMapping[hiveapi.constants.RIG_LAYER_TYPE]
            guideLayer = comp.guideLayer()
            if guideLayer is None:
                continue
            guides = {i.id(): i for i in guideLayer.iterGuides(includeRoot=False)}
            for guideId, controlId in validGuidesWithCtrls.items():
                guide = guides.get(guideId)
                if not guide:
                    continue
                self._itemComboBox.addItem(self.itemName(comp, guide))
                self.itemData.append([comp, guide])
                guideExpr = hiveapi.pathAsDefExpression((componentToken, "rigLayer", controlId))
                if self.isCurrentUISelected(comp, guide) and not comboSet:
                    comboSet = True
                    self._itemComboBox.setCurrentIndex(self._itemComboBox.count() - 1)
                if guideExpr == currentDriverExpr.params.driver and not comboSet:
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
            self.itemSelected.emit(component, guide)

        self._itemComboBox.blockSignals(False)

    def onValueChanged(self, event):
        """ on Value Changed

        :param event: Event with all the values related to the change.
        :type event: zoo.libs.pyqt.extended.combobox.ComboItemChangedEvent
        :return:
        :rtype:
        """
        data = self.itemData[self._itemComboBox.currentIndex()]
        self.itemSelected.emit(data[0], data[1])  # component, guide
        self.currentItem = data[0], data[1]
