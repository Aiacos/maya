import os

from PySide2 import QtWidgets, QtGui, QtCore

from adn.utils import path
from adn.utils.constants import UiConstants
from adn.ui.utils.launchers import open_url
from adn.ui.widgets.base import BaseDialog


class AboutDialog(QtWidgets.QDialog):
    """Generic dialog class.

    Class that handles the dialog creation for errors, warning, etc.

    Args:
        parent (:obj:`QDialog`): Parent class of the dialog class.
    """
    def __init__(self, parent):
        super(AboutDialog, self).__init__(parent)

        self.setWindowTitle("About AdonisFX")
        self._layout = QtWidgets.QVBoxLayout()
        self.setLayout(self._layout)
        
        # Layouts
        self._info_layout = QtWidgets.QHBoxLayout()
        self._extra_info_layout = QtWidgets.QVBoxLayout()
        self._terms_layout = QtWidgets.QVBoxLayout()
        self._button_layout = QtWidgets.QHBoxLayout()

        # Main info
        self._label = QtWidgets.QLabel(UiConstants.ABOUT_INFO)
        self._info_layout.addWidget(self._label)

        self._info_layout.addStretch(1)

        # AdonisFX logo
        self._adn_logo = QtWidgets.QLabel()
        pixmap = QtGui.QPixmap(path.get_icon_path("adn_logo.png"))
        pixmap = pixmap.scaled(50, 50, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self._adn_logo.setPixmap(pixmap)
        self._adn_logo.mousePressEvent = self.open_documentation_url
        self._adn_logo.setToolTip("Go to AdonisFX Documentation")
        self._adn_logo.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self._info_layout.addWidget(self._adn_logo)

        # Inbibo logo
        self._inbibo_logo = QtWidgets.QLabel()
        pixmap = QtGui.QPixmap(path.get_icon_path("inbibo_logo.png"))
        pixmap = pixmap.scaled(50, 50, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self._inbibo_logo.setPixmap(pixmap)
        self._inbibo_logo.mousePressEvent = self.open_inbibo_url
        self._inbibo_logo.setToolTip("Go to Inbibo Website")
        self._inbibo_logo.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self._info_layout.addWidget(self._inbibo_logo)

        # More info
        self._extra_info_label = QtWidgets.QLabel(UiConstants.ABOUT_EXTRA_INFO)
        self._extra_info_layout.addWidget(self._extra_info_label)

        # Confirm button
        self._button_layout.setAlignment(QtCore.Qt.AlignRight)
        self._close_button = QtWidgets.QPushButton("Close")
        self._close_button.clicked.connect(self.close)
        self._button_layout.addWidget(self._close_button)

        # Add all layout to main
        self._layout.addLayout(self._info_layout)
        self._layout.addLayout(self._extra_info_layout)
        self._layout.addLayout(self._button_layout)

    def open_inbibo_url(self, event):
        """Open link to the Inbibo website."""
        open_url("https://www.inbibo.co.uk")

    def open_documentation_url(self, event):
        """Open link to the technical documentation."""
        open_url("https://www.inbibo.co.uk/docs/adonisfx")


class AttributeWarningDialog(BaseDialog):
    """Custom dialog to warn the user of an attribute value. Gives 3 options:
     - "Yes": sets response to 0.
     - "Yes, don't ask again": sets response to 1.
     - "No, use defaults": sets response to 2.

    Args:
        text (str): Text to display in dialog.
        parent (:obj:`QtWidgets.QWindow`, optional): Parent window to the dialog.
            Defaults to None.
    """
    def __init__(self, text, parent=None):
        title = "Attribute Value Check"
        super(AttributeWarningDialog, self).__init__(
            title, parent, width=460, height=125,
            use_content=True, use_buttons=True, icon="question")

        # User response:
        # - Yes (0),
        # - Yes, don't ask again (1),
        # - No, use defaults (2)
        self.response = 0

        # Customize message
        self.message_label = QtWidgets.QLabel(self)
        self.message_label.setAlignment(QtCore.Qt.AlignLeft)
        self.message_label.setText(text)
        self.message_label.setWordWrap(True)
        self.message_label.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                                               QtWidgets.QSizePolicy.Fixed))
        self.message_layout.addWidget(self.message_label)
        self.message_layout.addStretch()

        # Configure buttons
        continue_button = QtWidgets.QPushButton("Yes")
        continue_button.clicked.connect(lambda: self.button_pressed(0))
        no_ask_again_button = QtWidgets.QPushButton("Yes, don't ask again")
        no_ask_again_button.clicked.connect(lambda: self.button_pressed(1))
        defaults_button = QtWidgets.QPushButton("No, use defaults")
        defaults_button.clicked.connect(lambda: self.button_pressed(2))
        self.buttons_layout.addStretch()
        self.buttons_layout.addWidget(continue_button)
        self.buttons_layout.addWidget(no_ask_again_button)
        self.buttons_layout.addWidget(defaults_button)
        self.buttons_layout.addStretch()

    def button_pressed(self, option_selected):
        """Callback when any button is pressed."""
        self.response = option_selected
        self.accept()

    def closeEvent(self, event):
        """Override close event to prevent the user to close it without a response."""
        event.ignore()


def msg_box(parent, msg_type, message, title=None, title_prefix=True, confirm_button=None,
            cancel_button=None):
    """Message file dialog creation.

    Function that generates the file dialogs for error,
    warning, information, about and question handling.

    Args:
        parent (class): Parent class to the file dialog.
        msg_type (str): Message type indicating the type of dialog to create.
        message (str): Message to be added to the dialog.
        title (str, optional): Title of the file dialog.
            Defaults to None.
        title_prefix (bool, optional): Indicates if the file dialog title should have a prefix.
            Defaults to True.
        confirm_button (:obj:`QPushButton`, optional): Confirm button to be added to the dialog.
            Defaults to None.
        cancel_button (:obj:`QPushButton`, optional): Cancel button to be added to the dialog.
            Defaults to None.

    Returns:
        bool: result of the execution.
    """
    msg_type = msg_type.lower()

    if not title:
        if msg_type in UiConstants.TAGS_INFO:
            title = "Info"
        elif msg_type in UiConstants.TAGS_WARNING:
            title = "Warning"
        elif msg_type in UiConstants.TAGS_ERROR:
            title = "Error"
        elif msg_type in UiConstants.TAGS_ABOUT:
            title = "About"
        elif msg_type in UiConstants.TAGS_QUESTION:
            title = "Question"

    if title_prefix:
        title = "{0} {1}".format(UiConstants.DIALOG_TITLE_PREFIX, title)

    if msg_type in UiConstants.TAGS_INFO:
        QtWidgets.QMessageBox.information(parent, title, message)
        return True

    if msg_type in UiConstants.TAGS_WARNING:
        QtWidgets.QMessageBox.warning(parent, title, message)
        return True

    if msg_type in UiConstants.TAGS_ERROR:
        QtWidgets.QMessageBox.critical(parent, title, message)
        return True

    if msg_type in UiConstants.TAGS_ABOUT:
        QtWidgets.QMessageBox.about(parent, title, message)
        return True

    if msg_type in UiConstants.TAGS_QUESTION:
        confirm_button = confirm_button or QtWidgets.QMessageBox.Yes
        cancel_button = cancel_button or QtWidgets.QMessageBox.No
        result = QtWidgets.QMessageBox.question(parent, title, message,
                                                confirm_button, cancel_button)
        return result == QtWidgets.QMessageBox.Yes
