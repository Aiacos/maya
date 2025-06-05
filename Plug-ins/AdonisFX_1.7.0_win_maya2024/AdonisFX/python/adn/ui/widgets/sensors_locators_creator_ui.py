try:
    from PySide6 import QtCore, QtWidgets
except ImportError:
    from PySide2 import QtCore, QtWidgets

from adn.utils.checkers import is_identifier
from adn.ui.maya.window import main_window
from adn.ui.widgets.dialogs import msg_box


class SensorsLocatorsCreatorUI(QtWidgets.QMainWindow):
    """UI class to write a custom name when creating a sensor or a locator.

    Args:
        node_creation_method (module): Method to create the locator or sensor.
        node_type (str): Node type of locator or sensor.
        parent (:obj:`BaseWidget`): Parent class of the current UI class.
        *args: Argument list.
        **kwargs: Keyword argument list.
    """
    def __init__(self, node_creation_method, node_type, parent, *args, **kwargs):
        super(SensorsLocatorsCreatorUI, self).__init__(parent)

        self._node_creation_method = node_creation_method
        self._node_type = node_type if node_type else "AdnNode"
        self._parent = parent
        self._build_ui()

    def _build_ui(self):
        """Builds the UI for the locator and sensor creator"""
        # Base window setup
        self._title = "Create new {}".format(self._node_type)
        self.setWindowTitle(self._title)
        self.setObjectName(self._title + '_uniqueId')
        
        # Resize
        self.setFixedSize(350, 100)
        
        # Main layout
        self._main_widget = QtWidgets.QWidget()
        self.setCentralWidget(self._main_widget)
        self._main_layout = QtWidgets.QVBoxLayout(self._main_widget)

        # General parameters
        self._button_width = 100
        self._button_height = 30

        ###############################
        # BEGIN NAMING SECTION
        ###############################
        self._label = QtWidgets.QLabel("Custom name:")

        self._name_input = QtWidgets.QLineEdit(self)
        self._name_input.setText(self._node_type)
        # Red rounded border similar to focus border
        self._wrong_input_name_stylesheet = "border: 2px solid #ff3535; border-radius: 2.5px"

        self._horizontal_layout = QtWidgets.QHBoxLayout()
        self._horizontal_layout.addWidget(self._label)
        self._horizontal_layout.addWidget(self._name_input)
        
        self._main_layout.addLayout(self._horizontal_layout)

        ###############################
        # BEGIN BUTTONS SECTION
        ###############################
        self._cancel_button = QtWidgets.QPushButton("Cancel")
        self._cancel_button.resize(QtCore.QSize(self._button_width, self._button_height))
        self._cancel_button.clicked.connect(self.close)

        self._create_button = QtWidgets.QPushButton("Create")
        self._create_button.resize(QtCore.QSize(self._button_width, self._button_height))
        self._create_button.clicked.connect(self._create_on_clicked)

        self._buttons_horizontal_layout = QtWidgets.QHBoxLayout()
        self._buttons_horizontal_layout.addWidget(self._cancel_button)
        self._buttons_horizontal_layout.addWidget(self._create_button)

        self._main_layout.addLayout(self._buttons_horizontal_layout)

        # Connect signals
        self._name_input.textEdited.connect(self._validate_name)

    def _validate_name(self, custom_name):
        """Checks if the name provided is valid while editing the custom name.
        Will enable the creation button if the name is valid, will disable otherwise.

        Args:
            custom_name (str): Name that the user is providing.
        """
        if not custom_name or not is_identifier(custom_name):
            self._create_button.setEnabled(False)
            self._name_input.setStyleSheet(self._wrong_input_name_stylesheet)
            return

        self._create_button.setEnabled(True)
        self._name_input.setStyleSheet("")

    def keyPressEvent(self, qKeyEvent):
        """Overload the keyPressEvent to trigger the creation method if the
        user press Enter."""
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if (qKeyEvent.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter) and
                modifiers == QtCore.Qt.NoModifier):
            self._create_on_clicked()
        else:
            super(SensorsLocatorsCreatorUI, self).keyPressEvent(qKeyEvent)

    def _create_on_clicked(self):
        """Create the node with the name set in the input text field. If the
        creator method fails (it will return None or False), an error dialog
        is prompted to inform the user to check the console for more
        information."""
        custom_name = self._name_input.text()
        if not custom_name or not is_identifier(custom_name):
            # This code should never be reached. Only by the keyPressEvent.
            self._create_button.setEnabled(False)
            self._name_input.setStyleSheet(self._wrong_input_name_stylesheet)
            return

        result = self._node_creation_method(custom_name)
        if not result:
            msg_box(main_window(), "error",
                    "An error occurred when creating an {0}. Please, check "
                    "the console for more information.".format(self._node_type))
            return

        self.close()
