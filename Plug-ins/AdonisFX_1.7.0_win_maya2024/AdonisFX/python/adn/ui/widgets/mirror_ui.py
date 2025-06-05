import logging

try:
    from PySide6 import QtCore, QtWidgets
except ImportError:
    from PySide2 import QtCore, QtWidgets

from adn.ui.widgets.base import BaseWidget
from adn.ui.widgets.dialogs import msg_box, main_window, display_report_data


class MirrorUI(BaseWidget):
    """User interface of the mirror tool to configure the settings required to
    execute the mirroring. The UI allows to set the naming convention rule
    (i.e. by prefix or by suffix) as well as the left and right labels.

    Args:
        dcc_tool (module): Tool that will be launching the mirror command.
        parent (:obj:`BaseWidget`): Parent class of the current UI class.
        *args: Argument list.
        **kwargs: Keyword argument list.
    """
    def __init__(self, dcc_tool, parent, *args, **kwargs):
        super(MirrorUI, self).__init__("Mirror", parent)
        self._parent = parent
        self._dcc_tool = dcc_tool
        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        """Builds the UI of the window based on: settings vertical layout and
        buttons horizontal layout. The settings layout consists in two
        horizontal layouts that integrate a combo box and the left/right
        input line edits respectively. The buttons layout has three buttons:
        accept, apply and cancel."""
        # Main layout
        self._main_widget = QtWidgets.QWidget()
        self.setCentralWidget(self._main_widget)
        self._main_layout = QtWidgets.QVBoxLayout(self._main_widget)

        # General parameters
        self._button_width = 100
        self._button_height = 30

        # Settings section
        self._mirror_by_label = QtWidgets.QLabel("Mirror by:")
        self._mirror_by_label.setMaximumWidth(90)
        self._mirror_by_combo = QtWidgets.QComboBox()
        self._mirror_by_combo.addItems(["Prefix", "Suffix"])
        self._combo_layout = QtWidgets.QHBoxLayout()
        self._combo_layout.addWidget(self._mirror_by_label)
        self._combo_layout.addWidget(self._mirror_by_combo)

        self._left_label = QtWidgets.QLabel("Left:")
        self._left_input = QtWidgets.QLineEdit()
        self._left_input.setText("L_")
        self._right_label = QtWidgets.QLabel("Right:")
        self._right_input = QtWidgets.QLineEdit()
        self._right_input.setText("R_")
        self._side_convention_layout = QtWidgets.QHBoxLayout()
        self._side_convention_layout.addWidget(self._left_label)
        self._side_convention_layout.addWidget(self._left_input)
        self._side_convention_layout.addWidget(self._right_label)
        self._side_convention_layout.addWidget(self._right_input)

        self._settings_layout = QtWidgets.QVBoxLayout()
        self._settings_layout.setContentsMargins(10, 10, 10, 10)
        self._settings_layout.addLayout(self._combo_layout)
        self._settings_layout.addLayout(self._side_convention_layout)
        self._main_layout.addLayout(self._settings_layout)

        # Buttons section
        self._accept_button = QtWidgets.QPushButton("Accept")
        self._accept_button.resize(QtCore.QSize(self._button_width,
                                                self._button_height))
        self._apply_button = QtWidgets.QPushButton("Apply")
        self._apply_button.resize(QtCore.QSize(self._button_width,
                                               self._button_height))
        self._cancel_button = QtWidgets.QPushButton("Cancel")
        self._cancel_button.resize(QtCore.QSize(self._button_width,
                                                self._button_height))

        self._button_horizontal_layout = QtWidgets.QHBoxLayout()
        self._button_horizontal_layout.setContentsMargins(10, 10, 10, 10)
        self._button_horizontal_layout.addWidget(self._accept_button)
        self._button_horizontal_layout.addWidget(self._apply_button)
        self._button_horizontal_layout.addWidget(self._cancel_button)
        self._main_layout.addLayout(self._button_horizontal_layout)
        self._main_layout.addStretch()

    def _connect_signals(self):
        """Connect signals to all of the components of the UI."""
        self._accept_button.clicked.connect(lambda: self._apply(close=True))
        self._apply_button.clicked.connect(self._apply)
        self._cancel_button.clicked.connect(self.close)

    def _apply(self, close=False):
        """Collects settings from the widgets and call the method to execute
        the mirroring.

        Args:
            close (bool, optional): Flag to close the window after apply.
                Defaults to False.
        """
        left_convention = self._left_input.text()
        right_convention = self._right_input.text()
        mirror_mode = self._mirror_by_combo.currentIndex()

        # Mirror by prefix
        if mirror_mode == 0:
            left_convention = "{0}*".format(left_convention)
            right_convention = "{0}*".format(right_convention)
        # Mirror by suffix
        else:
            left_convention = "*{0}".format(left_convention)
            right_convention = "*{0}".format(right_convention)

        # Check for selected locators and muscles
        selected_locators = self._dcc_tool.get_selected_locators()
        selected_muscles = self._dcc_tool.get_selected_muscles()
        no_locators = False if selected_locators else True
        no_muscles = False if selected_muscles else True

        # If the selection is empty inform the user and return
        if no_locators and no_muscles:
            msg = "Please select one or more locators or muscles to be mirrored."
            msg_box(main_window(), "info", msg, title="Before Mirroring...")
            return

        # If there are no locators in the selection and there are locators in the scene
        # inform the user and ask for confirmation to continue
        all_locators = self._dcc_tool.get_locators_in_scene()
        if no_locators and all_locators:
            question = ("There are no locators selected, only muscles will be mirrored. "
                        "Do you want to continue?")
            confirmation = msg_box(main_window(), "question", question,
                                   title="Before Mirroring...")

            if not confirmation:
                return

        # If there are no muscles in the selection and there are muscles in the scene
        # inform the user and ask for confirmation to continue
        all_muscles = self._dcc_tool.get_muscles_in_scene()
        if no_muscles and all_muscles:
            question = ("There are no muscles selected, only locators will be mirrored. "
                        "Do you want to continue?")
            confirmation = msg_box(main_window(), "question", question,
                                   title="Before Mirroring...")

            if not confirmation:
                return

        question = ("This mirroring process is undoable, but it is "
                    "advisable to have a saved version of this scene. Do you "
                    "want to continue with mirroring?")
        confirmation = msg_box(main_window(), "question", question,
                               title="Before Mirroring...")
        if not confirmation:
            return

        # Execute
        report_data = {"errors": [], "warnings": []}
        result = self._dcc_tool.apply_mirror(left_convention, right_convention, report_data=report_data)

        msg = "The mirror process completed with errors. Please check the detailed error list below for further information."
        title = "Mirroring Errors"
        display_report_data(report_data, msg, title)


        if result and close:
            self.close()
