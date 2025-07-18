from functools import partial

from zoo.libs.pyqt.widgets import elements
from zoo.libs.pyqt.widgets.frameless import widgets as framelesswidgets
from zoo.libs.pyqt.widgets.frameless import window as framelesswindow
from zoo.libs.pyqt.models import (
    listmodel,
    datasources,
    modelutils,
    constants,
)
from zoo.libs.pyqt import utils as qtutils
from zoo.preferences.interfaces import coreinterfaces
from zoo.apps.toolpalette import layouts, run, qtmenu, utils
from zoovendor.Qt import QtCore, QtWidgets, QtGui

# todo: Add LMB,MMB,RMB support to toolpalette actions


WIDGET_INFO_KEYS = {
    constants.minValue: "minValue",
    constants.maxValue: "maxValue",
    constants.defaultValueRole: "defaultValue",
}
# window size without dpiScale applied when window is minimized
MINIMIZE_SIZE = 100


class ShelfWindow(elements.ZooWindow):
    windowSettingsPath = "zoo/qtshelf"

    def __init__(
        self,
        name="zooShelf",
        title="Zoo Shelf",
        shelfId="AnimShelf",
        iconSize=32,
        parent=None,
    ):
        self._previousCloseTitleBarState = False  # false hidden
        self._isDocked = False
        super(ShelfWindow, self).__init__(
            name,
            title,
            parent=parent,
            resizable=True,
            width=300,
            height=20,
            modal=False,
            alwaysShowAllTitle=False,
            minButton=False,
            maxButton=False,
            onTop=False,
            saveWindowPref=True,
            overlay=True,
            minimizeEnabled=True,
            initPos=None,
            titleBarVisible=True,
            showDockTabs=False,
        )
        self._iconSize = qtutils.dpiScale(iconSize)
        self._closeButtonTitleBar = framelesswidgets.TitleBar(
            parent=self,
            showTitle=False,
            alwaysShowAll=False,
            titleBarHeight=self.titleBar.titleBarHeight,
            showDockTabs=False,
            style=framelesswidgets.TitleBar.TitleStyle.Default,
        )
        self._closeButtonTitleBar.setMaximiseVisible(False)
        self._closeButtonTitleBar.setMinButtonVisible(False)
        self._closeButtonTitleBar.logoButton.hide()
        self._closeButtonTitleBar._mainLayout.insertWidget(
            0, self._closeButtonTitleBar.closeButton
        )
        self._framelessLayout.addWidget(self._closeButtonTitleBar)
        self.titleBarDirectionMaxSize = qtutils.sizeByDpi(QtCore.QSize(0, 200))

        layout = elements.vBoxLayout(spacing=0, margins=(2, 2, 2, 2))
        self.setMainLayout(layout)
        self.toolPalette = run.currentInstance()
        self.shelfView = ShelfWidget(
            self.toolPalette, shelfId, iconSize=self._iconSize, parent=self
        )
        layout.addWidget(self.shelfView)
        self.applyStyleSheet(default=False)
        self.setTitleBarDirection(QtWidgets.QBoxLayout.LeftToRight)
        self._previousTitleStyle = framelesswidgets.TitleBar.TitleStyle.VerticalThin
        rowCount = self.shelfView.shelfModel.rowCount()
        iconSize = self.shelfView.listview.iconSize()
        titleBarWidth = self._closeButtonTitleBar.width()

        self.parentContainer.resize(
            (rowCount * iconSize.width()) + (titleBarWidth * 2.0), iconSize.height()
        )

    def dockEvent(self, container):
        """Dock event

        :return:
        :rtype:
        """
        self._isDocked = True
        super(ShelfWindow, self).dockEvent(container)

        self.savedSize = self.size()
        self._previousCloseTitleBarState = self._closeButtonTitleBar.isVisible()
        self._closeButtonTitleBar.hide()

    def undockedEvent(self):
        """Undocked event

        :return:
        :rtype:
        """
        self._isDocked = False
        super(ShelfWindow, self).undockedEvent()
        qtutils.singleShotTimer(lambda: self.window().resize(self.savedSize))
        self._closeButtonTitleBar.setVisible(self._previousCloseTitleBarState)

    def setTitleBarDirection(self, direction):
        changed = super(ShelfWindow, self).setTitleBarDirection(direction)
        if not changed:
            return False
        self.titleBar.titleLabel.hide()
        if direction == QtWidgets.QBoxLayout.LeftToRight:
            self.titleBar.closeButton.hide()
            self.titleBar.setTitleStyle(
                framelesswidgets.TitleBar.TitleStyle.VerticalThin
            )
            if not self._isDocked:
                self._closeButtonTitleBar.setTitleStyle(
                    framelesswidgets.TitleBar.TitleStyle.VerticalThin
                )
                self._closeButtonTitleBar.show()
            return True
        self.titleBar.setTitleStyle(framelesswidgets.TitleBar.TitleStyle.Thin)
        self.titleBar.closeButton.show()
        self._closeButtonTitleBar.hide()
        return True

    def applyStyleSheet(self, default=True):
        """Try to set the default stylesheet, if not, just ignore it

        :return:
        """
        if default:
            self.setDefaultStyleSheet()
            return
        # transparent background
        coreInterface = coreinterfaces.coreInterface()
        themeName = coreInterface.currentTheme()
        themeDict = coreInterface.themeDict(themeName)
        backgroundColor = "rgba(60, 60, 60, 155)"
        themeDict["$MAIN_BACKGROUND_COLOR"] = backgroundColor
        themeDict["$FRAMELESS_WINDOW_CONTENTS"] = backgroundColor
        themeDict["$FRAMELESS_TITLEBAR_COLOR"] = backgroundColor
        # set to transparent to avoid blending
        themeDict["$VIEW_BACKGROUND_COLOR"] = "transparent"
        style = coreInterface.stylesheetFromData(themeDict)
        self.setStyleSheet(style.data)

    def resizeEvent(self, event):
        """

        :param event:
        :type event: :class:`QResizeEvent`
        :return:
        :rtype:
        """
        size = event.size()
        if (
            size.height() >= self.titleBarDirectionMaxSize.height()
            and size.width() >= self.titleBarDirectionMaxSize.width()
        ):
            self.setTitleBarDirection(QtWidgets.QBoxLayout.TopToBottom)
        else:
            self.setTitleBarDirection(QtWidgets.QBoxLayout.LeftToRight)
        super(ShelfWindow, self).resizeEvent(event)

    def titleDoubleClicked(self):
        """Title double-clicked"""
        op = super(ShelfWindow, self).titleDoubleClicked()
        if framelesswindow.NO_OP:
            return op
        if op == framelesswindow.MINIMIZED:
            self.savedSize = self.window().size()
            self._closeButtonTitleBar.hide()
            qtutils.singleShotTimer(
                lambda: self.window().resize(
                    qtutils.dpiScale(100), self.savedSize.height()
                )
            )
        elif op == framelesswindow.MAXIMIZED:
            qtutils.singleShotTimer(lambda: self.window().resize(self.savedSize))
            self.update()

        return op


class ShelfWidget(QtWidgets.QWidget):
    """Reusable shelf widget which displays a single zoo tools shelf"""

    def __init__(self, toolPalette, shelfId, iconSize=16, parent=None):
        super(ShelfWidget, self).__init__(parent=parent)
        self.shelfId = shelfId
        self.toolPalette = toolPalette
        self._coreInterface = coreinterfaces.coreInterface()
        self._themeDict = self._coreInterface.themeDict(
            self._coreInterface.currentTheme()
        )

        self.listview = QtWidgets.QListView(parent=self)
        self.listview.setSpacing(qtutils.dpiScale(2))
        self.listview.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.listview.setMouseTracking(True)
        self.listview.setViewMode(QtWidgets.QListView.IconMode)
        self.listview.setResizeMode(QtWidgets.QListView.Adjust)
        self.listview.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.listview.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.listview.setUniformItemSizes(False)

        self.listview.setDragEnabled(False)
        self.listview.setAcceptDrops(False)
        self.listview.setUpdatesEnabled(True)
        self.listview.setIconSize(QtCore.QSize(iconSize, iconSize))

        self.shelfModel = ShelfModel(self.toolPalette, parent=self)
        self.listview.setModel(self.shelfModel)
        self.rowDataSource = ShelfItemDataSource(
            self, [], self.listview.iconSize().width(), model=self.shelfModel
        )
        self.shelfModel.rowDataSource = self.rowDataSource

        layout = elements.vBoxLayout(spacing=0, margins=(0, 0, 0, 0))
        layout.addWidget(self.listview)
        self.setLayout(layout)

        self._uiConnections()
        self.refresh()

    def refresh(self):
        self.shelfModel.refresh(self.shelfId)

        for row in range(self.rowDataSource.rowCount()):
            item = self.rowDataSource.zooShelfItems[row]
            if item.isSlider():
                self.listview.setItemDelegateForRow(row, SliderDelegate(parent=self))
                self.listview.openPersistentEditor(
                    self.shelfModel.index(row, 0, QtCore.QModelIndex())
                )
            elif item.isSeparator():
                self.listview.setItemDelegateForRow(
                    row,
                    SeparatorDelegate(parent=self),
                )

    def _uiConnections(self):
        self.listview.pressed.connect(self.iconPressed)

    def iconPressed(self, index):
        # index is from the proxy model ie. handles search, so we remap to our model before
        # getting values.
        sourceIndex, sourceModel = modelutils.dataModelIndexFromIndex(index)
        shelfItem = sourceModel.data(
            sourceIndex, role=constants.userObject
        )  # type: layouts.ShelfButton
        if shelfItem is None or shelfItem.isSeparator() or shelfItem.isSlider():
            return
        if not len(shelfItem):
            self.toolPalette.executePluginById(shelfItem.id, **shelfItem.arguments)
            return

        self.showMenuForShelfItem(shelfItem)

    def showMenuForShelfItem(self, shelfItem):
        iconSize = self.listview.iconSize()
        rootMenu = QtWidgets.QMenu(parent=self)

        qtmenu.generateMenuTree(
            shelfItem,
            rootMenu,
            self.toolPalette.executePluginById,
            self.toolPalette.typeRegistry,
            iconSize=iconSize.width(),
        )
        if len(rootMenu.children()) != 0:
            rootMenu.exec_(QtGui.QCursor.pos())

    def executePlugin(self, shelfItem):
        args = dict(shelfItem.arguments)
        if shelfItem.isSlider():
            args["value"] = shelfItem.widgetInfo["value"]
        args["item"] = shelfItem
        self.toolPalette.executePluginById(shelfItem.id, **args)


class ShelfModel(listmodel.ListModel):
    def __init__(self, toolPalette, parent):
        """

        :param toolPalette:
        :type toolPalette: :class:``zoo.apps.toolpalette.palette.ToolPalette`
        :param parent:
        :type parent: :class:`ShelfWidget`
        """
        super(ShelfModel, self).__init__(parent=parent)
        self.toolPalette = toolPalette

    def refresh(self, shelfId):
        shelfItem = self.toolPalette.shelfManager.shelfById(shelfId)
        for childItem in shelfItem.children:
            typePlugin = self.toolPalette.typeRegistry.getPlugin(
                childItem.type
            )  # type: palette.PluginTypeBase
            if typePlugin is None:
                continue
            data = childItem.serialize(valid=True)
            uiData = typePlugin.pluginUiData(childItem.id, data)
            childItem.update(uiData)
        self.rowDataSource.setUserObjects(shelfItem.children)
        self.reload()


class ShelfItemDataSource(datasources.IconRowDataSource):
    """DataSource which describes the data to show in the shelf.
    Only one of these exist for a listview
    """

    def __init__(
        self, view, shelfItems, iconSize, headerText=None, model=None, parent=None
    ):
        """
        :param view:
        :type view: :class:`ShelfWidget`
        :param shelfItems:
        :type shelfItems:
        :param iconSize:
        :type iconSize:
        :param headerText:
        :type headerText:
        :param model:
        :type model:
        :param parent:
        :type parent:
        """
        super(ShelfItemDataSource, self).__init__(headerText, model, parent)
        self.zooShelfItems = shelfItems  # type: list[layouts.Item]
        self.iconCache = {}  # type: dict[int, QtGui.QIcon]
        self._iconSize = QtCore.QSize(iconSize, iconSize)
        self._view = view

    def setIconSize(self, size):
        self._iconSize = size

    def userObjects(self):
        return self.zooShelfItems

    def setUserObjects(self, objects):
        self.zooShelfItems = objects

    def rowCount(self):
        return len(self.zooShelfItems)

    def isEditable(self, index):
        return False

    def isSelectable(self, index):
        return False

    def toolTip(self, index):
        return self.zooShelfItems[index].tooltip

    def minimum(self, index):
        shelfItem = self.zooShelfItems[index]
        if shelfItem.isSlider():
            return shelfItem.widgetInfo.get("minValue", 0.0)
        return 0.0

    def maximum(self, index):
        shelfItem = self.zooShelfItems[index]
        if shelfItem.isSlider():
            return shelfItem.widgetInfo.get("maxValue", 1.0)
        return 1.0

    def data(self, index):
        shelfItem = self.zooShelfItems[index]
        if shelfItem.isSlider():
            return shelfItem.widgetInfo.get(
                "value", shelfItem.widgetInfo.get("defaultValue")
            )

    def setData(self, index, value):
        shelfItem = self.zooShelfItems[index]
        if shelfItem.isSlider():
            shelfItem.widgetInfo["value"] = value
            self._view.executePlugin(shelfItem)
            return True
        return False

    def icon(self, index):
        try:
            iconCacheInstance = self.iconCache[index]
        except KeyError:
            item = self.zooShelfItems[index]
            iconCacheInstance = utils.iconForItem(
                item, iconSize=self._iconSize.width(), ignoreSeparators=False
            )
            if item is not None:
                self.iconCache[index] = iconCacheInstance

        return iconCacheInstance

    def iconSize(self, index):
        return self._iconSize

    def dataByRole(self, index, role):
        shelfItem = self.zooShelfItems[index]
        if shelfItem.isSlider():
            return shelfItem.widgetInfo.get(WIDGET_INFO_KEYS.get(role, 0))

    def setDataByCustomRole(self, index, data, role):
        shelfItem = self.zooShelfItems[index]
        if shelfItem.isSlider():
            shelfItem.widgetInfo[WIDGET_INFO_KEYS[role]] = data
            return True
        return False

    def customRoles(self, index):
        if self.zooShelfItems[index].isSlider():
            return constants.minValue, constants.maxValue, constants.defaultValueRole
        return []


class SeparatorDelegate(QtWidgets.QStyledItemDelegate):
    separatorWidth = 2
    separatorColor = (155, 155, 155, 255)

    def __init__(self, parent=None):
        super(SeparatorDelegate, self).__init__(parent)

    def initStyleOption(self, option, index):
        super(SeparatorDelegate, self).initStyleOption(option, index)
        option.icon = QtGui.QIcon()
        option.features &= QtWidgets.QStyleOptionViewItem.HasDecoration
        option.state &= ~QtWidgets.QStyle.State_MouseOver

    def sizeHint(self, option, index):
        return _computeItemSizeHint(self, option.decorationSize.width())

    def paint(self, painter, option, index):
        self.initStyleOption(option, index)
        rct = option.rect
        painter.setPen(
            QtGui.QPen(QtGui.QColor(*self.separatorColor), self.separatorWidth)
        )
        if isVertical(self):

            centerLeft = rct.topLeft()
            centerLeft.setY(centerLeft.y() + (rct.height() * 0.5))
            centerRight = QtCore.QPoint(centerLeft.x() + rct.width(), centerLeft.y())

            painter.drawLine(centerLeft, centerRight)
        else:
            centerTop = rct.topLeft()
            centerTop.setX(centerTop.x() + (rct.width() * 0.5))
            centerBot = QtCore.QPoint(centerTop.x(), centerTop.y() + rct.height())

            painter.drawLine(centerTop, centerBot)


class SliderBtnWidget(QtWidgets.QWidget):
    """Specialized delegate widget to handle a slider with a button.
    Layout is changed depending on the orientation.
    """

    def __init__(self, model, index, parent=None):
        super(SliderBtnWidget, self).__init__(parent=parent)
        layout = elements.hBoxLayout(self)
        icon = model.data(index, QtCore.Qt.DecorationRole)
        defaultValue = model.data(index, constants.defaultValueRole)
        minValue = model.data(index, constants.minValue)
        maxValue = model.data(index, constants.maxValue)
        self.slider = elements.Slider(
            defaultValue=defaultValue, minValue=minValue, maxValue=maxValue, parent=self
        )
        self.button = elements.ExtendedButton(icon=icon, parent=self)
        layout.addWidget(self.button)
        layout.addWidget(self.slider)

    def setOrientation(self, orientation):
        if orientation == QtCore.Qt.Vertical:
            self.slider.setOrientation(QtCore.Qt.Vertical)
            self.layout().setDirection(QtWidgets.QBoxLayout.BottomToTop)
        else:
            self.slider.setOrientation(QtCore.Qt.Horizontal)
            self.layout().setDirection(QtWidgets.QBoxLayout.LeftToRight)


class SliderDelegate(QtWidgets.QStyledItemDelegate):

    def __init__(self, lengthBeforeFlipping=100, parent=None):
        """
        :param parent:
        :type parent: :class:`ShelfWidget`
        :param lengthBeforeFlipping: The length the item before switching between vertical and horizontal direction
        :type lengthBeforeFlipping: int
        """
        super(SliderDelegate, self).__init__(parent)
        self._lengthBeforeFlipping = lengthBeforeFlipping

    def initStyleOption(self, option, index):
        super(SliderDelegate, self).initStyleOption(option, index)
        option.icon = QtGui.QIcon()
        option.decorationSize = QtCore.QSize(-1, -1)
        option.features &= QtWidgets.QStyleOptionViewItem.HasDecoration
        option.state &= ~QtWidgets.QStyle.State_MouseOver

    def createEditor(self, parent, option, index):
        self.initStyleOption(option, index)
        model = index.model()
        editor = SliderBtnWidget(model, index, parent=parent)
        editor.slider.valueChanged.connect(partial(self._valueChanged, editor))
        editor.button.clicked.connect(
            partial(
                self._buttonClicked, editor, model.data(index, constants.userObject)
            )
        )
        return editor

    def _buttonClicked(self, editor, shelfItem):
        self.parent().showMenuForShelfItem(shelfItem)

    def _valueChanged(self, widget, *args, **kwargs):
        """

        :param widget:
        :type widget: :class:`elements.Slider`
        """

        self.commitData.emit(widget)

    def setModelData(self, editor, model, index):
        value = editor.slider.value()
        model.setData(index, value, QtCore.Qt.EditRole)

    def sizeHint(self, option, index):
        return _computeItemSizeHint(self, self._lengthBeforeFlipping)

    def setEditorData(self, widget, index):
        value = index.model().data(index, QtCore.Qt.EditRole)
        if value is not None:
            widget.blockSignals(True)
            widget.slider.setValue(value)
            widget.blockSignals(False)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

        if option.rect.height() == self._lengthBeforeFlipping:
            editor.setOrientation(QtCore.Qt.Vertical)
        else:
            editor.setOrientation(QtCore.Qt.Horizontal)


def isVertical(delegate):
    parent = delegate.parent()
    viewSize = parent.listview.size()
    iconSize = parent.listview.iconSize()
    return (viewSize.width() - iconSize.width() * 0.5) <= iconSize.width() * 2.0


def _computeItemSizeHint(delegate, defaultDistance=100):
    """

    :param delegate:
    :type delegate: :class:`QtWidgets.QStyledItemDelegate`
    :param defaultDistance:
    :type defaultDistance:
    :return:
    :rtype:
    """
    parent = delegate.parent()
    viewSize = parent.listview.size()
    iconSize = parent.listview.iconSize()
    if (viewSize.width() - iconSize.width() * 0.5) <= iconSize.width() * 2.0:
        return QtCore.QSize(iconSize.height(), defaultDistance)
    return QtCore.QSize(defaultDistance, iconSize.width())
