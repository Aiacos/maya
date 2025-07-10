try:
    from PySide6 import QtCore, QtWidgets, QtGui
    from PySide6.QtGui import QAction
except ImportError:
    from PySide2 import QtCore, QtWidgets, QtGui
    from PySide2.QtWidgets import QAction

from adn.utils.constants import UiConstants


class BaseWidget(QtWidgets.QMainWindow):
    """Base widget from which all generated UI elements will be inherited.

    Args:
        title (str): Title of the base widget window.
        parent (:obj:`QtWidgets.QMainWindow`): Parent class of the base widget class.
        *args: Argument list.
        **kwargs: Keyword argument list.
    """
    def __init__(self, title, parent, *args, **kwargs):
        super(BaseWidget, self).__init__(parent)
        
        # Base window setup
        self.setWindowTitle(title)
        self.setObjectName(title + '_uniqueId')
        
        # Resize
        if "width" in kwargs and "height" in kwargs:
            width = kwargs.get("width")
            height = kwargs.get("height")
            self.resize(width, height)
        
        # Main layout
        self._main_widget = QtWidgets.QWidget()
        self.setCentralWidget(self._main_widget)
        self._main_layout = QtWidgets.QVBoxLayout(self._main_widget)
        
        # Menu bar
        menu_bar = self.menuBar()
        self._help_menu = QtWidgets.QMenu("&Help", self)
        self._docs_action = QAction("&Documentation", self, triggered=self.open_docs)
        self._about_action = QAction("&About", self, triggered=self.open_about)
        self._help_menu.addAction(self._docs_action)
        self._help_menu.addAction(self._about_action)
        menu_bar.addMenu(self._help_menu)

    @classmethod
    def open_docs(cls):
        """Open link to the technical documentation."""
        from adn.ui.utils.launchers import open_url
        open_url("https://www.inbibo.co.uk/docs/adonisfx")

    def open_about(self):
        """Open the about dialog."""
        from adn.ui.widgets.dialogs import AboutDialog
        dialog = AboutDialog(self)
        dialog.show()


class BaseDialog(QtWidgets.QDialog):
    """Base dialog from which custom dialogs can inherit.

    Args:
        title (str): Title of the base dialog.
        parent (:obj:`QtWidgets.QDialog`): Parent class of the base dialog.
        *args: Argument list.
        **kwargs: Keyword argument list.
    """
    def __init__(self, title, parent, *args, **kwargs):
        super(BaseDialog, self).__init__(parent)

        # Base window setup
        self.setWindowTitle("{0} {1}".format(UiConstants.LOG_PREFIX, title))
        self.setObjectName(title + '_uniqueId')
        flags = self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint
        self.setWindowFlags(flags)

        # Resize
        width = kwargs.get("width", 250)
        height = kwargs.get("height", 250)
        self.resize(width, height)
        self.setFocus()

        # Main layout
        self._main_widget = QtWidgets.QWidget()
        self._main_layout = QtWidgets.QVBoxLayout(self._main_widget)
        self.setLayout(self._main_layout)

        # Optional class members
        self.content_layout = None
        self.buttons_layout = None
        self.message_layout = None

        # Content layout
        use_content = kwargs.get("use_content", False)
        if use_content:
            self.content_layout = QtWidgets.QHBoxLayout()
            self.content_layout.setContentsMargins(10, 10, 10, 10)
            self._main_layout.addLayout(self.content_layout)

            # Add icon on the left if icon_tag is provided and valid (optional)
            icon_tag = kwargs.get("icon", None)
            if icon_tag:
                if icon_tag in UiConstants.TAGS_INFO:
                    icon = getattr(QtWidgets.QStyle, "SP_MessageBoxInformation")
                elif icon_tag in UiConstants.TAGS_WARNING:
                    icon = getattr(QtWidgets.QStyle, "SP_MessageBoxWarning")
                elif icon_tag in UiConstants.TAGS_ERROR:
                    icon = getattr(QtWidgets.QStyle, "SP_MessageBoxCritical")
                elif icon_tag in UiConstants.TAGS_QUESTION:
                    icon = getattr(QtWidgets.QStyle, "SP_MessageBoxQuestion")
                else:
                    icon = None

                if icon:
                    icon = self.style().standardIcon(icon)
                    icon_label = QtWidgets.QLabel()
                    icon_label.setFixedWidth(64)
                    pixmap = icon.pixmap(icon.actualSize(QtCore.QSize(64, 64)))
                    icon_label.setPixmap(pixmap)
                    self.content_layout.addWidget(icon_label)

            # Add a layout on the right to fill with content from a child dialog
            self.message_layout = QtWidgets.QVBoxLayout()
            self.content_layout.addLayout(self.message_layout)

        # Buttons layout
        use_buttons = kwargs.get("use_buttons", False)
        if use_buttons:
            self.buttons_layout = QtWidgets.QHBoxLayout()
            self.buttons_layout.setContentsMargins(2, 2, 2, 2)
            self._main_layout.addLayout(self.buttons_layout)
