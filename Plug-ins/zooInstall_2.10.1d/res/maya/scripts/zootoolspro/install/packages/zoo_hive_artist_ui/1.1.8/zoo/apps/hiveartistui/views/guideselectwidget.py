from zoovendor.Qt import QtCore, QtWidgets
from zoo.libs.pyqt.widgets import elements
from zoo.libs.pyqt import utils as qtutils


class GuideSelectWidget(QtWidgets.QWidget):

    def __init__(self, rigModel, label,
                 toolTip=None,
                 buttonToolTip=None,
                 componentModel=None, parent=None):
        """
        :param rigModel: The component model for this widget to operate on
        :type rigModel: :class:`zoo.apps.hiveartistui.model.RigModel`
        :param componentModel: The Hive UI component Data Model.
        :type componentModel: :class:`zoo.apps.hiveartistui.model.ComponentModel`
        :param parent:
        :type parent: :class:`QtWidgets.QWidget`
        """
        super(GuideSelectWidget, self).__init__(parent=parent)
        self.currentItem = (None, None)
        self.itemData = []
        self.componentModel = componentModel
        self.rigModel = rigModel

        layout = elements.hBoxLayout(parent=self)
        self._itemComboBox = elements.ComboEditWidget(label=label,
                                                      mainStretch=16, labelStretch=4,
                                                      parent=self,
                                                      inputMode="string",
                                                      supportMiddleMouseScroll=False
                                                      )
        self._itemComboBox.setToolTip(toolTip or "")
        self._itemComboBox.setFixedHeight(qtutils.dpiScale(21))
        self._itemComboBox.itemClickedOrReturned.connect(self.onValueChanged)

        self._guideSelect = elements.styledButton(
            "",
            icon="cursorSelect",
            parent=self,
            toolTip=buttonToolTip or "",
            themeUpdates=False,
        )
        layout.addWidget(self._itemComboBox)
        layout.addWidget(self._guideSelect)

    def initUi(self):
        self.updateCombo()

    def updateCombo(self):
        self._hardRefresh()

    def isCurrentUISelected(self, component, guide):
        """ Checks if the component + guide combination is the same as the current parent

        :param component:
        :type component: :class:`zoo.libs.hive.base.component.Component`
        :param guide:
        :type guide:
        :return:
        :rtype:
        """

        if self.currentItem and self.currentItem[0] is not None:
            return self.currentItem == (component, guide)

    def _hardRefresh(self):
        """ Do a hard refresh.
        Clear out the combobox and add it all based on the rigs and components

        :return:
        :rtype:
        """
        pass

    @classmethod
    def itemName(cls, component, guide):
        return '[{} {}] {}'.format(component.name(), component.side(), guide.name(includeNamespace=False))

    def onValueChanged(self, event):
        """ on Value Changed

        :param event: Event with all the values related to the change.
        :type event: zoo.libs.pyqt.extended.combobox.ComboItemChangedEvent
        :return:
        :rtype:
        """
        pass
