import itertools

from zoo.apps.hiveartistui import model
from zoo.apps.hiveartistui.views import componentsettings
from zoo.libs.pyqt.widgets import elements
from zoo.core.util import strutils
from functools import partial
from zoo.libs.commands import hive
from zoo.libs.maya.utils import general


class HeadComponentModel(model.ComponentModel):
    componentType = "headcomponent"

    def createWidget(self, componentWidget, parentWidget):
        return HeadSettingsWidget(componentWidget, parentWidget, componentModel=self)


class HeadSettingsWidget(componentsettings.ComponentSettingsWidget):
    def __init__(self, componentWidget, parent, componentModel):
        super(HeadSettingsWidget, self).__init__(
            componentWidget, parent, componentModel
        )
        self.twistSegmentWidgets = []

    def initUi(self):
        self.advancedSettingsLayout = elements.CollapsableFrameThin(
            "Advanced Settings", parent=self, collapsed=True
        )
        self.twistSettingsLayout = elements.CollapsableFrameThin(
            "Twist Settings", parent=self.advancedSettingsLayout, collapsed=True
        )
        self.advancedSettingsLayout.addWidget(self.twistSettingsLayout)
        layout = self.layout()

        guideLayerDef = self.componentModel.component.definition.guideLayer
        primarySettings = guideLayerDef.guideSettings(
            "hasTwists", "neckSegmentCount", "distributionType", "hasTwistRotation"
        )

        hasTwists = primarySettings["hasTwists"]

        switchesLayout = elements.hBoxLayout()
        componentsettings.createBooleanWidget(
            self, primarySettings["hasTwistRotation"], "Build Twist Rotation", switchesLayout,
            self.settingCheckboxChanged
        )
        layout.addLayout(switchesLayout)

        componentsettings.createRadioWidget(
            self,
            [None, hasTwists],
            ["No Twists", "Twists"],
            layout,
            self.onTwistsBendyChanged,
        )

        layout.addWidget(self.advancedSettingsLayout)
        self.createSpaceLayout()

        self.advancedSettingsLayout.toggled.connect(
            partial(self.componentWidget.tree.updateTreeWidget, delay=True)
        )
        self.twistSettingsLayout.toggled.connect(
            partial(self.componentWidget.tree.updateTreeWidget, delay=True)
        )
        self.advancedSettingsLayout.setEnabled(hasTwists.value)
        self.twistSettingsLayout.setEnabled(hasTwists.value)

        if hasTwists.value:
            self._createTwistWidgets(
                guideLayerDef, primarySettings, self.twistSettingsLayout
            )

        self.createNamingConventionLayout()
        self.createDeformSettingsLayout()

    def onSwitchChanged(self, checkbox, guideSetting, state):
        self.settingCheckboxChanged(checkbox, guideSetting, state)

    def onTwistsBendyChanged(self, event):
        """

        :param event:
        :type event: :class:`zoo.libs.pyqt.widgets.joinedRadio.JoinedRadioButtonEvent`
        """
        hasTwists = False
        if event.index == 0:  # None
            self.advancedSettingsLayout.setEnabled(False)
            if not self.advancedSettingsLayout.collapsed:
                # Hack to hide the flickering on collapse. Updates are re-enabled on tree.updateTreeWidget
                self.componentWidget.tree.setUpdatesEnabled(False)
                self.advancedSettingsLayout.onCollapsed()
            self._clearTwistSettings()
        elif event.index == 1:  # hasTwists
            hasTwists = True
            self.advancedSettingsLayout.setEnabled(True)
            self.twistSettingsLayout.setEnabled(True)

        self.componentWidget.tree.updateTreeWidget(delay=True)
        hive.updateGuideSettings(
            self.componentModel.component, {"hasTwists": hasTwists}
        )
        if event.index == 1:
            guideLayerDef = self.componentModel.component.definition.guideLayer
            primarySettings = guideLayerDef.guideSettings(
                "hasTwists", "neckSegmentCount", "distributionType"
            )
            self._createTwistWidgets(
                guideLayerDef, primarySettings, self.twistSettingsLayout
            )

    def _createTwistWidgets(self, guideLayerDefinition, primarySettings, layout):
        """
        :param guideLayerDefinition: The current components guide layer definition instance
        :type guideLayerDefinition: :class:`zoo.libs.hive.api.GuideLayerDefinition`
        :param primarySettings: The list of guide settings for twists.
        :type primarySettings: dict[str, :class:`zoo.libs.hive.api.AttributeDefinition`]
        :param layout: The collapsableFrame Layout which is a widget but has layout methods.
        :type layout: :class:`elements.CollapsableFrame`
        """
        self._clearTwistSettings()
        uprSegment = primarySettings["neckSegmentCount"]
        distributionType = primarySettings["distributionType"]
        distWidget = componentsettings.createEnumWidget(
            self,
            distributionType,
            "Distribution Type",
            layout,
            None,
            self._onDistributionChanged,
        )
        self.neckTwistSegmentWidget = componentsettings.createIntWidget(
            self, uprSegment, "Neck Segment Count", layout, self._onSegmentValueChanged
        )

        minValue = 0 if distributionType.value == 0 else 3
        self.neckTwistSegmentWidget.setMinValue(minValue)

        self.twistSegmentWidgets.append(("", distWidget))
        self.twistSegmentWidgets.append(("", self.neckTwistSegmentWidget))
        # segment count change
        self._createSegmentWidgets(
            itertools.chain(*self.componentModel.component.twistIds()),
            guideLayerDefinition,
            layout,
        )

    def _onDistributionChanged(self, event, widget, setting):
        """Called when the twist distribution type has changed.

        :type event:  :class:`zoo.libs.pyqt.extended.combobox.ComboItemChangedEvent`
        :param widget: The combo box for the enum attribute.
        :type widget: :class:`elements.ComboBoxRegular`
        :param setting: The guide setting
        :type setting: :class:`zao.libs.hive.api.AttributeDefinition`
        """
        self.enumChanged(event, widget, setting)
        minValue = 0 if event.index == 0 else 3
        self.neckTwistSegmentWidget.setMinValue(minValue)
        self._updateTwistSettingWidgets()

    def _createSegmentWidgets(self, guideIds, guideLayerDefinition, layout):
        """Generates All widgets for a single twist Segment.

        Note you need to handle refresh the treewidget for size hinting . We don't
        handle this here for optimisation.

        :param guideIds: The list of guide ids for twists to display in the UI.
        :type guideIds: list[str]
        :param guideLayerDefinition: The current components guide layer definition instance
        :type guideLayerDefinition: :class:`zoo.libs.hive.api.GuideLayerDefinition`
        :param layout: The collapsableFrame Layout which is a widget but has layout methods.
        :type layout: :class:`elements.CollapsableFrame`
        """
        for twistSetting in sorted(
            guideLayerDefinition.guideSettings(*guideIds).values(), key=lambda x: x.name
        ):
            edit = componentsettings.createFloatWidget(
                self,
                twistSetting,
                strutils.titleCase(twistSetting.name),
                layout,
                supportsSlider=True,
                sliderFinishedFunc=self._twistSliderFinished,
                sliderStartSignalFunc=self._twistSliderStarted,
                sliderChangedFunc=self._twistSliderValueChanged,
                signalFunc=self._twistValueChanged,
            )
            self.twistSegmentWidgets.append((twistSetting.name, edit))

    def _updateTwistSettingWidgets(self):
        guideLayer = self.componentModel.component.definition.guideLayer
        for name, twistWidget in self.twistSegmentWidgets:
            guideSetting = guideLayer.guideSetting(name)
            if guideSetting is not None:
                twistWidget.setValue(guideSetting.value)

    def _setTwistValue(self, setting, value):
        existingSetting = (
            self.componentModel.component.definition.guideLayer.guideSetting(
                setting.name
            )
        )
        if existingSetting is not None:
            if existingSetting.value == value:
                return False
            hive.updateGuideSettings(
                self.componentModel.component, {setting.name: value}
            )
            return True
        return False

    def _twistSliderStarted(self, widget, setting, *args, **kwargs):
        """Called when the twist slider has started to be changed and opens a maya undo chunk, closed
        by _twistSliderFinished.
        """
        general.openUndoChunk("HiveTwistSlider_{}".format(setting.name))

    def _twistSliderValueChanged(self, widget, setting, value, **kwargs):
        existingSetting = (
            self.componentModel.component.definition.guideLayer.guideSetting(
                setting.name
            )
        )
        if existingSetting is None:
            return False
        ret = self._setTwistValue(setting, widget.edit.convertValue(value))
        return ret

    def _twistSliderFinished(self, widget, setting, *args, **kwargs):
        value = widget.edit.convertValue(widget.text())
        ret = self._setTwistValue(setting, value)
        general.closeUndoChunk("HiveTwistSlider_{}".format(setting.name))
        return ret

    def _twistValueChanged(self, widget, setting, *args, **kwargs):
        value = widget.edit.convertValue(widget.text())
        ret = self._setTwistValue(setting, value)
        return ret

    def _onSegmentValueChanged(self, widget, setting):
        """Called when the twist segment count has changed.

        Updates hive component which will handle scene state.
        Purges current twist widgets and rebuilds from new count and then lets the treewidget
        know to handle the size hint.

        :param widget: The zoo tools integer edit widget
        :type widget: :class:`elements.IntEdit`
        :param setting: The guide setting
        :type setting: :class:`zao.libs.hive.api.AttributeDefinition`
        """

        changed = self.settingNumericChanged(widget, setting)
        if not changed:
            return
        guideLayerDef = self.componentModel.component.definition.guideLayer
        for _, twistWidget in self.twistSegmentWidgets:
            twistWidget.deleteLater()
        primarySettings = guideLayerDef.guideSettings(
            "hasTwists", "neckSegmentCount", "distributionType"
        )
        self._createTwistWidgets(
            guideLayerDef, primarySettings, self.twistSettingsLayout
        )
        self.componentWidget.tree.updateTreeWidget()

    def _clearTwistSettings(self):
        for _, edit in self.twistSegmentWidgets:
            edit.deleteLater()
        self.twistSegmentWidgets = []
