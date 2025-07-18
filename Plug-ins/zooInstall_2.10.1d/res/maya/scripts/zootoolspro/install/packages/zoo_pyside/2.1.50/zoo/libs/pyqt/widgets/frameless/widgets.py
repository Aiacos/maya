import webbrowser
from zoo.libs.utils import output
from zoovendor.Qt import QtCore, QtWidgets, QtGui
from zoo.libs.pyqt import utils, uiconstants
from zoo.libs.pyqt.extended.clippedlabel import ClippedLabel
from zoo.libs.pyqt.widgets import layouts, buttons, overlay
from zoo.libs.pyqt.widgets.frameless.containerwidgets import SpawnerIcon
from zoo.preferences.interfaces import coreinterfaces
from zoo.core.util import zlogging

logger = zlogging.getLogger(__name__)
MODIFIER = QtCore.Qt.AltModifier


class ResizeDirection:
    """Flag attributes to tell what position the resizer is"""

    Left = 1
    Top = 2
    Right = 4
    Bottom = 8


class TitleBar(QtWidgets.QFrame):
    doubleClicked = QtCore.Signal()
    moving = QtCore.Signal(object, object)

    class TitleStyle:
        Default = "DEFAULT"
        Thin = "THIN"
        VerticalThin = "VERTICAL_THIN"

    def __init__(
        self,
        parent=None,
        showTitle=True,
        alwaysShowAll=False,
        titleBarHeight=40,
        showDockTabs=True,
        style=TitleStyle.Default,
    ):
        """Title bar of the frameless window.

        Click drag this widget to move the window widget

        :param parent:
        :type parent: zoo.libs.pyqt.widgets.window.ZooWindow
        """
        super(TitleBar, self).__init__(parent=parent)

        self.titleBarHeight = titleBarHeight
        self.pressedAt = None
        self.leftContents = QtWidgets.QFrame(self)
        self.rightContents = QtWidgets.QWidget(self)

        self._mainLayout = None
        self._mainRightLayout = None
        self.contentsLayout = None
        self.cornerContentsLayout = None
        self.titleLayout = None
        self.windowButtonsLayout = None
        self._splitLayout = None
        self._initLayouts()
        self._titleStyle = style
        self._previousTitleStyle = style

        self.zooWindow = parent
        self.mousePos = None  # type: QtCore.QPoint
        self.widgetMousePos = None  # type: QtCore.QPoint
        self.themePref = coreinterfaces.coreInterface()

        # Title bar buttons
        self.logoButton = SpawnerIcon(
            zooWindow=parent, showDockTabs=showDockTabs, parent=self
        )

        self.toggle = True

        self.iconSize = 13  # note: iconSize gets dpiScaled in internally
        self.closeButton = buttons.ExtendedButton(parent=self, themeUpdates=False)
        self.minimizeButton = buttons.ExtendedButton(parent=self, themeUpdates=False)
        self.maxButton = buttons.ExtendedButton(parent=self, themeUpdates=False)
        self.helpButton = buttons.ExtendedButton(parent=self, themeUpdates=False)
        self.titleLabel = TitleLabel(parent=self, alwaysShowAll=alwaysShowAll)

        self._moveEnabled = True

        if not showTitle:
            self.titleLabel.hide()

        self.initUi()
        self._connections()

    def setDirection(self, direction):
        self._mainLayout.setDirection(direction)
        self._mainRightLayout.setDirection(direction)
        self.contentsLayout.setDirection(direction)
        self.cornerContentsLayout.setDirection(direction)
        self.titleLayout.setDirection(direction)
        self.windowButtonsLayout.setDirection(direction)
        self._splitLayout.setDirection(direction)

    def setDebugColors(self, debug):
        if debug:
            self.leftContents.setStyleSheet("background-color: green")
            self.titleLabel.setStyleSheet("background-color: red")
            self.rightContents.setStyleSheet("background-color: blue")
        else:
            self.leftContents.setStyleSheet("")
            self.titleLabel.setStyleSheet("")
            self.rightContents.setStyleSheet("")

    def _initLayouts(self):
        self._mainLayout = layouts.hBoxLayout(self)
        self._mainRightLayout = layouts.hBoxLayout()
        self.contentsLayout = layouts.hBoxLayout()
        self.cornerContentsLayout = layouts.hBoxLayout()
        self.titleLayout = layouts.hBoxLayout()
        self.windowButtonsLayout = layouts.hBoxLayout()
        self._splitLayout = layouts.hBoxLayout()

    def initUi(self):
        """Init UI"""

        self.setFixedHeight(utils.dpiScale(self.titleBarHeight))

        col = self.themePref.FRAMELESS_TITLELABEL_COLOR
        self.closeButton.setIconByName(
            "xMark", colors=col, size=self.iconSize, colorOffset=80
        )
        self.minimizeButton.setIconByName(
            "minus", colors=col, size=self.iconSize, colorOffset=80
        )
        self.maxButton.setIconByName(
            "checkbox", colors=col, size=self.iconSize, colorOffset=80
        )
        toolTip = "Open the help URL for this window."
        if self.zooWindow.helpUrl:
            toolTip = "{} \n{}  ".format(toolTip, self.zooWindow.helpUrl)
        self.helpButton.setIconByName(
            "help", colors=col, size=self.iconSize, colorOffset=80
        )
        self.helpButton.setToolTip(toolTip)

        # _mainLayout: The whole titlebar main layout

        # Button Settings
        btns = [self.helpButton, self.closeButton, self.minimizeButton, self.maxButton]
        for b in btns:
            b.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            b.setDoubleClickEnabled(False)

        """ The widget layout is laid out into the following:
        
        _mainLayout
            logoButton
            _mainRightLayout
                _splitLayout
                    leftContents
                    titleLayoutWgt -> titleLayout
                    rightContents   
                
                windowButtonsLayout
                    helpButton
                    minimizeButton
                    maxButton
                    closeButton
        """

        # Layout setup
        self._mainRightLayout.setContentsMargins(*utils.marginsDpiScale(0, 5, 6, 0))
        self.contentsLayout.setContentsMargins(0, 0, 0, 0)
        self.cornerContentsLayout.setContentsMargins(*utils.marginsDpiScale(0, 0, 0, 0))
        self.rightContents.setLayout(self.cornerContentsLayout)

        # Window buttons (Min, Max, Close button)
        self.windowButtonsLayout.setContentsMargins(*utils.marginsDpiScale(0, 0, 0, 0))
        self.windowButtonsLayout.addWidget(self.helpButton)
        self.windowButtonsLayout.addWidget(self.minimizeButton)
        self.windowButtonsLayout.addWidget(self.maxButton)
        self.windowButtonsLayout.addWidget(self.closeButton)

        # Split Layout
        self._splitLayout.addWidget(self.leftContents)
        self._splitLayout.addLayout(self.titleLayout, 1)
        self._splitLayout.addWidget(self.rightContents)

        # Title Layout
        self.leftContents.setLayout(self.contentsLayout)
        self.contentsLayout.setSpacing(0)
        self.titleLayout.addWidget(self.titleLabel)
        self.titleLayout.setSpacing(0)
        self.titleLayout.setContentsMargins(*utils.marginsDpiScale(0, 8, 0, 7))
        self.titleLabel.setSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
        )
        self.titleLabel.setMinimumWidth(1)

        # The main title layout (Logo | Main Right Layout)
        self._mainLayout.setContentsMargins(*utils.marginsDpiScale(4, 0, 0, 0))
        self._mainLayout.setSpacing(0)
        self.spacingItem = QtWidgets.QSpacerItem(8, 8)
        self.spacingItem2 = QtWidgets.QSpacerItem(6, 6)

        self._mainLayout.addWidget(self.logoButton)
        self._mainLayout.addSpacerItem(self.spacingItem2)
        self._mainLayout.addLayout(self._mainRightLayout)
        self._mainLayout.setAlignment(self.logoButton, QtCore.Qt.AlignLeft)

        # The Main right layout (Title, Window buttons)
        self._mainRightLayout.addLayout(self._splitLayout)
        # self._mainRightLayout.addWidget(self.rightContents)
        self._mainRightLayout.addLayout(self.windowButtonsLayout)
        self._mainRightLayout.setAlignment(QtCore.Qt.AlignVCenter)
        self.windowButtonsLayout.setAlignment(QtCore.Qt.AlignVCenter)

        # Left right margins have to be zero otherwise the title toolbar will flicker (eg toolsets)
        self._mainRightLayout.setStretch(0, 1)
        QtCore.QTimer.singleShot(0, self.refreshTitleBar)
        self.setTitleSpacing(False)

        if not self.zooWindow.helpUrl:
            self.helpButton.hide()

    def setTitleSpacing(self, spacing):
        """

        :param spacing:
        :return:
        """
        if spacing:
            self.spacingItem2.changeSize(6, 6)
        else:
            self.spacingItem2.changeSize(0, 0)
            self._splitLayout.setSpacing(0)

    def setTitleAlign(self, align):
        """Set Title Align

        :param align:
        :type align:
        """
        if align == QtCore.Qt.AlignCenter:
            self._splitLayout.setStretch(1, 0)
        else:
            self._splitLayout.setStretch(1, 1)

    def setDockable(self, dockable):
        if dockable:
            pass

    def setMoveEnabled(self, enabled):
        """Window moving enabled

        :param enabled:
        :type enabled:
        :return:
        :rtype:
        """
        self._moveEnabled = enabled

    def setTitleStyle(self, style):
        """Set the title style

        :param style:
        :type style: TitleStyle
        :return: TitleStyle.Default or TitleStyle.Thin
        :rtype:
        """
        self._previousTitleStyle = self._titleStyle
        self._titleStyle = style
        if style == self.TitleStyle.Default:
            self.setDirection(QtWidgets.QBoxLayout.LeftToRight)
            utils.setStylesheetObjectName(self.titleLabel, "")
            self.setFixedHeight(utils.dpiScale(self.titleBarHeight))
            self.setMaximumWidth(uiconstants.QWIDGETSIZE_MAX)  # unlock the width
            self.titleLayout.setContentsMargins(*utils.marginsDpiScale(0, 5, 0, 7))
            self._mainRightLayout.setContentsMargins(*utils.marginsDpiScale(0, 5, 6, 0))
            self.logoButton.setIconSize(QtCore.QSize(24, 24))
            self.logoButton.setFixedSize(QtCore.QSize(30, 24))
            self.minimizeButton.setFixedSize(QtCore.QSize(28, 24))
            self.maxButton.setFixedSize(QtCore.QSize(28, 24))
            self.maxButton.setIconSize(QtCore.QSize(24, 24))
            self.closeButton.setFixedSize(QtCore.QSize(28, 24))
            self.closeButton.setIconSize(QtCore.QSize(16, 16))
            if self.zooWindow.helpUrl:
                self.helpButton.show()

            self.windowButtonsLayout.setSpacing(utils.dpiScale(6))
            self._mainRightLayout.setContentsMargins(*utils.marginsDpiScale(0, 5, 6, 0))
            self.contentsLayout.setContentsMargins(0, 0, 0, 0)
            self.cornerContentsLayout.setContentsMargins(
                *utils.marginsDpiScale(0, 0, 0, 0)
            )
            self.windowButtonsLayout.setContentsMargins(
                *utils.marginsDpiScale(0, 0, 0, 0)
            )
            self.titleLayout.setContentsMargins(*utils.marginsDpiScale(0, 8, 0, 7))
            self._mainLayout.setContentsMargins(*utils.marginsDpiScale(4, 0, 0, 0))

        elif style == self.TitleStyle.Thin:
            self.setDirection(QtWidgets.QBoxLayout.LeftToRight)
            self.setMaximumWidth(uiconstants.QWIDGETSIZE_MAX)  # unlock the width
            self.logoButton.setIconSize(QtCore.QSize(12, 12))
            self.logoButton.setFixedSize(QtCore.QSize(10, 12))
            self.minimizeButton.setFixedSize(QtCore.QSize(10, 18))
            self.maxButton.setFixedSize(QtCore.QSize(10, 18))
            self.maxButton.setIconSize(QtCore.QSize(12, 12))
            self.closeButton.setFixedSize(QtCore.QSize(10, 18))
            self.closeButton.setIconSize(QtCore.QSize(12, 12))
            self.setFixedHeight(utils.dpiScale(int(self.titleBarHeight * 0.5)))
            self.titleLabel.setFixedHeight(utils.dpiScale(20))
            self.windowButtonsLayout.setSpacing(utils.dpiScale(6))
            self.helpButton.hide()

            utils.setStylesheetObjectName(self.titleLabel, "Minimized")
            self.titleLayout.setContentsMargins(*utils.marginsDpiScale(0, 3, 15, 7))
            self._mainRightLayout.setContentsMargins(*utils.marginsDpiScale(0, 0, 6, 0))
            self._mainLayout.setContentsMargins(*utils.marginsDpiScale(4, 0, 0, 0))
            self.contentsLayout.setContentsMargins(0, 0, 0, 0)
            self.cornerContentsLayout.setContentsMargins(
                *utils.marginsDpiScale(0, 0, 0, 0)
            )
            self.windowButtonsLayout.setContentsMargins(
                *utils.marginsDpiScale(0, 0, 0, 0)
            )

        elif style == self.TitleStyle.VerticalThin:
            self.setDirection(QtWidgets.QBoxLayout.TopToBottom)
            self.logoButton.setIconSize(QtCore.QSize(12, 12))
            self.logoButton.setFixedSize(QtCore.QSize(10, 12))
            self.minimizeButton.setFixedSize(QtCore.QSize(10, 18))
            self.maxButton.setFixedSize(QtCore.QSize(10, 18))
            self.maxButton.setIconSize(QtCore.QSize(12, 12))
            self.closeButton.setFixedSize(QtCore.QSize(10, 18))
            self.closeButton.setIconSize(QtCore.QSize(12, 12))
            self.setFixedWidth(int(self.titleBarHeight * 0.5))
            utils.setStylesheetObjectName(self.titleLabel, "Minimized")
            self.setMaximumHeight(uiconstants.QWIDGETSIZE_MAX)  # unlock the height
            self._mainLayout.setContentsMargins(*utils.marginsDpiScale(3, 3, 3, 3))
            self._mainRightLayout.setContentsMargins(*utils.marginsDpiScale(3, 3, 3, 3))
            self.contentsLayout.setContentsMargins(*utils.marginsDpiScale(3, 3, 3, 3))
            self.cornerContentsLayout.setContentsMargins(
                *utils.marginsDpiScale(3, 3, 3, 3)
            )
            self.titleLayout.setContentsMargins(*utils.marginsDpiScale(3, 3, 3, 3))
            self.windowButtonsLayout.setContentsMargins(
                *utils.marginsDpiScale(3, 3, 3, 3)
            )
            self._splitLayout.setContentsMargins(*utils.marginsDpiScale(3, 3, 3, 3))
        else:
            output.displayError(
                "'{}' style doesn't exist for {}.".format(
                    style, self.zooWindow.__class__.__name__
                )
            )

    def moveEnabled(self):
        """If the titlebar can drive movement.

        :return:
        :rtype:
        """
        return self._moveEnabled

    def setMaxButtonVisible(self, vis):
        """Set max button visible

        :param vis:
        :type vis:
        :return:
        :rtype:
        """
        self.maxButton.setVisible(vis)

    def setMinButtonVisible(self, vis):
        """Set Minimize button visible

        :param vis:
        :type vis:
        :return:
        :rtype:
        """
        self.minimizeButton.setVisible(vis)

    def titleStyle(self):
        """Return the title style

        :return:
        :rtype:
        """
        return self._titleStyle

    def previousTitleStyle(self):
        return self._previousTitleStyle

    def mouseDoubleClickEvent(self, event):
        """Mouse double clicked event

        :param event:
        :type event: :class:`QtGui.QMouseEvent`
        :return:
        :rtype:
        """
        # note: we don't call super to avoid mousePressEvent being called a second time
        self.doubleClicked.emit()

    def setLogoHighlight(self, highlight):
        """Set logo highlight.

        Highlight the logo

        :param highlight:
        :type highlight:
        :return:
        :rtype:
        """
        self.logoButton.setLogoHighlight(highlight)

    def refreshTitleBar(self):
        """Workaround for mainLayout not showing

        :return:
        """
        QtWidgets.QApplication.processEvents()
        self.updateGeometry()
        self.update()

    def setTitleText(self, value=""):
        """The text of the title bar in the window

        :param value:
        :type value:
        :return:
        :rtype:
        """
        self.titleLabel.setText(value.upper())

    def _connections(self):
        """

        :return:
        """
        self.closeButton.leftClicked.connect(self.zooWindow.close)
        self.minimizeButton.leftClicked.connect(self._onMinimizeButtonClicked)
        self.maxButton.leftClicked.connect(self._onMaximizeButtonClicked)
        self.helpButton.leftClicked.connect(self.openHelp)

    def openHelp(self):
        """Open help url

        :return:
        """
        webbrowser.open(self.zooWindow.helpUrl)

    def setWindowIconSize(self, size):
        """
        Sets the icon size of the titlebar icons
        :param size:
        :return:
        """
        self.iconSize = size

    def setMaximiseVisible(self, show=True):
        """Set Maximise button visible

        :param show:
        """
        if show:
            self.maxButton.show()
        else:
            self.maxButton.hide()

    def setMinimiseVisible(self, show=True):
        """Set minimize button visibility

        :param show:
        """
        if show:
            self.minimizeButton.show()
        else:
            self.minimizeButton.hide()

    def toggleContents(self):
        """Show or hide the additional contents in the titlebar"""
        if self.contentsLayout.count() > 0:
            for i in range(1, self.contentsLayout.count()):
                widget = self.contentsLayout.itemAt(i).widget()
                if widget.isHidden():
                    widget.show()
                else:
                    widget.hide()

    def mousePressEvent(self, event):
        """Mouse click event to start the moving of the window

        :type event: :class:`QtGui.QMouseEvent`
        """
        if event.buttons() & QtCore.Qt.LeftButton:
            self.startMove()

        event.ignore()

    def mouseReleaseEvent(self, event):
        """Mouse release for title bar

        :type event: :class:`QtGui.QMouseEvent`
        """
        self.endMove()

    def startMove(self):
        if self._moveEnabled:
            self.widgetMousePos = self.zooWindow.mapFromGlobal(QtGui.QCursor.pos())

    def endMove(self):
        if self._moveEnabled:
            self.widgetMousePos = None

    def mouseMoveEvent(self, event):
        """Move the window based on if the titlebar has been clicked or not

        :type event: :class:`QtGui.QMouseEvent`
        """
        if self.widgetMousePos is None or not self._moveEnabled:
            return

        pos = QtGui.QCursor.pos() - self.widgetMousePos

        delta = pos - self.window().pos()
        self.moving.emit(pos, delta)

        self.window().move(pos)

    def _onMinimizeButtonClicked(self):
        self.zooWindow.minimize()

    def _onMaximizeButtonClicked(self):
        self.zooWindow.maximize()


class FramelessOverlay(overlay.OverlayWidget):
    MOVEBUTTON = QtCore.Qt.MiddleButton
    RESIZEBUTTON = QtCore.Qt.RightButton

    def __init__(self, parent, titleBar, resizable=True):
        """Handles linux like window movement.

        Eg Alt-Middle click to move entire window
        Alt Left Click corner to resize

        """
        super(FramelessOverlay, self).__init__(parent=parent)
        self.resizable = resizable

        self.titleBar = titleBar
        self.pressedAt = QtCore.QPoint()  # for detect change between press/release

        # note 2 different positions used here, resizePos for resize left/top
        # and previousMovePos for resize right, bottom
        self._resizePos = QtCore.QPoint()
        self.resizeDir = 0

    def mousePressEvent(self, event):
        """Alt-Middle click to move window

        :param event:
        :return:
        """
        self.pressedAt = QtGui.QCursor.pos()

        if not self.isEnabled():
            event.ignore()
            super(FramelessOverlay, self).mousePressEvent(event)
            return

        if self.isModifier() and event.buttons() & self.MOVEBUTTON:
            self.titleBar.startMove()
            self.setCursor(QtCore.Qt.CursorShape.ClosedHandCursor)

        if self.isModifier() and event.buttons() & self.RESIZEBUTTON and self.resizable:
            self.resizeDir = self.quadrant()
            self._resizePos = QtGui.QCursor.pos()
            if self.resizeDir == ResizeDirection.Top | ResizeDirection.Right:
                self.setCursor(QtCore.Qt.CursorShape.SizeBDiagCursor)
            elif self.resizeDir == ResizeDirection.Top | ResizeDirection.Left:
                self.setCursor(QtCore.Qt.CursorShape.SizeFDiagCursor)
            elif self.resizeDir == ResizeDirection.Bottom | ResizeDirection.Left:
                self.setCursor(QtCore.Qt.CursorShape.SizeBDiagCursor)
            elif self.resizeDir == ResizeDirection.Bottom | ResizeDirection.Right:
                self.setCursor(QtCore.Qt.CursorShape.SizeFDiagCursor)

        if (not self.isModifier() and event.buttons() & self.MOVEBUTTON) or (
            not self.isModifier() and event.buttons() & self.RESIZEBUTTON
        ):
            self.hide()

        event.ignore()
        return super(FramelessOverlay, self).mousePressEvent(event)

    @classmethod
    def isModifier(cls):
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        # return modifiers == QtCore.Qt.ControlModifier | QtCore.Qt.AltModifier
        return modifiers == MODIFIER

    def mouseReleaseEvent(self, event):

        if not self.isEnabled():
            event.ignore()
            super(FramelessOverlay, self).mouseReleaseEvent(event)
            return

        self.titleBar.endMove()
        self.resizeDir = 0
        event.ignore()

        # If there is no difference in position at all, let the mouse click through
        if self.pressedAt - QtGui.QCursor.pos() == QtCore.QPoint(0, 0):
            utils.clickUnder(QtGui.QCursor.pos(), 1, modifier=MODIFIER)
        self._resizePos = QtCore.QPoint()
        super(FramelessOverlay, self).mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        """

        :param event:
        :type event:
        """
        if not self.isEnabled():
            event.ignore()
            super(FramelessOverlay, self).mouseMoveEvent(event)
            return

        if not self.isModifier():
            self.hide()
            return

        self.titleBar.mouseMoveEvent(event)

        if self.resizeDir != 0:
            self._handleResize()
            self._resizePos = QtGui.QCursor.pos()

        event.ignore()

        super(FramelessOverlay, self).mouseMoveEvent(event)

    def _handleResize(self):
        pos = QtGui.QCursor.pos()
        window = self.window()
        width, height = window.width(), window.height()
        minSize = self.window().minimumSize()
        geom = window.frameGeometry()
        # Minimum Size
        delta = pos - self._resizePos
        # Check to see if the ResizeDirection flag is in self.direction
        if self.resizeDir & ResizeDirection.Left == ResizeDirection.Left:
            width = max(window.minimumWidth(), width - delta.x())
            geom.setLeft(geom.right() - width)
        if self.resizeDir & ResizeDirection.Top == ResizeDirection.Top:
            height = max(window.minimumHeight(), height - delta.y())
            geom.setTop(geom.bottom() - height)
        if self.resizeDir & ResizeDirection.Right == ResizeDirection.Right:
            width = max(minSize.width(), width + delta.x())
            geom.setWidth(width)
        if self.resizeDir & ResizeDirection.Bottom == ResizeDirection.Bottom:
            height = max(minSize.height(), height + delta.y())
            geom.setHeight(height)
        window.setGeometry(geom)

    def quadrant(self):
        """Get the quadrant of where the mouse is pointed, and return the direction

        :return: The direction ResizeDirection
        :rtype: ResizeDirection
        """
        midX = self.geometry().width() * 0.5
        midY = self.geometry().height() * 0.5
        ret = 0

        pos = self.mapFromGlobal(QtGui.QCursor.pos())

        if pos.x() < midX:
            ret = ret | ResizeDirection.Left
        elif pos.x() > midX:
            ret = ret | ResizeDirection.Right

        if pos.y() < midY:
            ret = ret | ResizeDirection.Top
        elif pos.y() > midY:
            ret = ret | ResizeDirection.Bottom

        return ret

    def show(self):
        self.updateStyleSheet()
        if self.isEnabled():
            super(FramelessOverlay, self).show()
        else:
            logger.warning("FramelessOverlay.show() was called when it is disabled")

    def setEnabled(self, enabled):
        self.setDebugMode(not enabled)
        self.setVisible(enabled)
        super(FramelessOverlay, self).setEnabled(enabled)

    def updateStyleSheet(self):
        """Set style sheet

        :return:
        """
        self.setDebugMode(self._debug)


class WindowContents(QtWidgets.QFrame):
    """For CSS purposes"""


class TitleLabel(ClippedLabel):
    """For CSS purposes"""

    def __init__(self, *args, **kwargs):
        super(TitleLabel, self).__init__(*args, **kwargs)
        self.setAlignment(QtCore.Qt.AlignRight)
