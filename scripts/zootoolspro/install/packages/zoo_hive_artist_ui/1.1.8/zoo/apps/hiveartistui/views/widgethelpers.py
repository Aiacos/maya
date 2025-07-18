from zoo.libs.hive import api as hiveapi
from zoo.libs.maya import zapi
from zoo.libs.pyqt.widgets import elements
from zoovendor.Qt import QtWidgets, QtCore
from zoo.apps.hiveartistui.views import guideselectwidget


class SideNameWidget(QtWidgets.QWidget):
    renamed = QtCore.Signal(str)

    def __init__(self, model, parent=None, showLabel=True, showArrow=True):
        """
        :param model: The component model for this widget to operate on
        :type model: :class:`zoo.apps.hiveartistui.model.ComponentModel`
        :param parent:
        :type parent: :class:`QtWidgets.QWidget`
        """
        super(SideNameWidget, self).__init__(parent=parent)
        self.showLabel = showLabel
        self.model = model
        self._initUi()
        styleSheet = """
        QComboBox {
            background-color: #30000000;
        }
        QComboBox:hover {
            background-color: #88111111;
        }
        QComboBox::drop-down {
            background-color: transparent;
            border-left: 0px solid #33FF1111;
        }
        QComboBox::drop-down:pressed {
            background-color: #8871a0d0;
        }
        
        QComboBox:pressed {
            background-color: #8871a0d0;
        }


        """

        hideArrow = """
        QComboBox::down-arrow {
            image: none;
        }
        
        """
        # used when the displayed in the component widget titlebar
        if not showArrow:
            styleSheet += hideArrow
            self.setStyleSheet(styleSheet)

    def _initUi(self):

        layout = elements.hBoxLayout(parent=self)
        self._sideComboBox = elements.ComboBoxRegular("Side",
                                                      [],
                                                      labelRatio=4,
                                                      boxRatio=16,
                                                      sortAlphabetically=True,
                                                      parent=self,
                                                      supportMiddleMouseScroll=False)
        self._sideComboBox.itemChanged.connect(self.onValueChanged)
        self._sideComboBox.box.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.updateCombo()
        layout.addWidget(self._sideComboBox)
        if not self.showLabel:
            self._sideComboBox.label.hide()

    def updateCombo(self):
        self._sideComboBox.blockSignals(True)
        namingObj = self.model.component.namingConfiguration()
        sideField = namingObj.field("side")
        sides = sorted(list([i.name for i in sideField.keyValues()]))
        side = sideField.valueForKey(self.model.side)
        self._sideComboBox.clear()
        self._sideComboBox.addItems(sides)
        self._sideComboBox.setToText(side, QtCore.Qt.MatchFixedString | QtCore.Qt.MatchCaseSensitive)
        self._sideComboBox.blockSignals(False)

    def onValueChanged(self, event=None):
        """

        :param event: Event with all the values related to the change.
        :type event: zoo.libs.pyqt.extended.combobox.ComboItemChangedEvent
        :return:
        :rtype:
        """
        side = str(self.model.component.namingConfiguration().field("side").valueForKey(event.text))
        self.renamed.emit(side)


class ParentWidget(guideselectwidget.GuideSelectWidget):
    parentChanged = QtCore.Signal(object, object)  # component, guide

    def __init__(self, rigModel=None, componentModel=None, parent=None):
        """
        :param rigModel: The component model for this widget to operate on
        :type rigModel: :class:`zoo.apps.hiveartistui.model.RigModel`
        :param componentModel: The Hive UI component Data Model.
        :type componentModel: :class:`zoo.apps.hiveartistui.model.ComponentModel`
        :param parent:
        :type parent: :class:`QtWidgets.QWidget`
        """
        toolTip = "Sets the components parent guide"
        btnToolTip = "Sets the components parent guide to the selected guide from the scene"
        super(ParentWidget, self).__init__(
            rigModel, "Parent", toolTip, btnToolTip, componentModel, parent
        )
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
        self.currentItem = self.componentModel.component.componentParentGuide()
        for i, comp in enumerate(self.rigModel.rig.components()):
            if comp == self.componentModel.component:
                continue
            guideLayer = comp.guideLayer()
            if not guideLayer:
                continue

            idMapping = comp.idMapping()
            jointIds = idMapping[hiveapi.constants.DEFORM_LAYER_TYPE]
            guideMap = {i.id(): i for i in comp.guideLayer().findGuides(*tuple(jointIds.keys())) if i is not None}
            for guideId, jntId in jointIds.items():
                jntGuide = guideMap.get(guideId)
                if not jntGuide:
                    continue
                self._itemComboBox.addItem(self.itemName(comp, jntGuide))
                self.itemData.append([comp, jntGuide])
                if not comboSet:
                    if self.isCurrentUISelected(comp, jntGuide):
                        comboSet = True
                        self._itemComboBox.setCurrentIndex(
                            self._itemComboBox.count() - 1
                        )
                        continue
        self._itemComboBox.blockSignals(False)

    @classmethod
    def itemName(cls, component, guide):
        return '[{} {}] {}'.format(component.name(), component.side(), guide.name(includeNamespace=False))

    def _onGuideSelected(self):
        self._itemComboBox.blockSignals(True)
        for sel in zapi.selected():
            if not hiveapi.Guide.isGuide(sel):
                continue
            guide = hiveapi.Guide(sel.object())
            component = hiveapi.componentFromNode(guide)
            if not component or component == self.componentModel.component:
                continue
            jntId = component.idMapping()[hiveapi.constants.DEFORM_LAYER_TYPE].get(
                guide.id()
            )
            if not jntId:
                break

            self._itemComboBox.setTexts(self.itemName(component, guide), setItem=True)
            self.parentChanged.emit(component, guide)  # component, guide
            self.currentItem = component, guide
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
        self.parentChanged.emit(data[0], data[1])  # component, guide
        self.currentItem = data[0], data[1]
