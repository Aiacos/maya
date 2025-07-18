try:
    from PySide6 import QtCore, QtWidgets
except ImportError:
    from PySide2 import QtCore, QtWidgets

from adn.ui.widgets.base import BaseWidget
from adn.ui.maya.window import main_window
from adn.ui.widgets.dialogs import msg_box
from adn.utils.checkers import is_identifier
from adn.utils.constants import DeformerTypes


class DeformersCreatorUI(BaseWidget):
    """UI class to create a deformer with a custom name and custom base parameters.

    Args:
        node_creation_method (module): Method to create the locator or sensor.
        node_type (str): Node type of locator or sensor.
        dcc_tool (module): Tool that will be launching the command associated to the UI.
        dcc_scene_commands (module): Commands that will invoke scene functions.
        parent (:obj:`BaseWidget`): Parent class of the current UI class.
        *args: Argument list.
        **kwargs: Keyword argument list.
    """    
    def __init__(self, node_creation_method, node_type, dcc_tool, dcc_scene_commands,
                 parent, *args, **kwargs):
        super(DeformersCreatorUI, self).__init__("Create deformer",
                                                 parent,
                                                 width=360,
                                                 height=525)
        self._parent = parent
        self._node_creation_method = node_creation_method
        self._node_type = node_type if node_type else "AdnNode"
        self._dcc_tool = dcc_tool
        self._dcc_scene_commands = dcc_scene_commands
        self._materials_list = ["Fat", "Muscle", "Rubber", "Tendon",
                                "Leather", "Wood", "Concrete", "Skin"]
        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        """Builds the UI for the deformer creator"""
        # Base window setup
        self._title = "Create new {}".format(self._node_type)
        self.setWindowTitle(self._title)
                
        # Main layout
        self._main_widget = QtWidgets.QWidget()
        self.setCentralWidget(self._main_widget)
        self._main_layout = QtWidgets.QVBoxLayout(self._main_widget)

        # General parameters
        self._button_width = 100
        self._button_height = 30

        ###############################
        # BEGIN PARAMETERS SECTION
        ###############################
        self._parameters_vertical_layout = QtWidgets.QVBoxLayout()
        self._label = QtWidgets.QLabel("Custom Name:")

        self._name_input = QtWidgets.QLineEdit(self)
        self._name_input.setText(self._node_type)
        # Red rounded border similar to focus border
        self._wrong_input_name_stylesheet = "border: 2px solid #ff3535; border-radius: 2.5px"

        self._horizontal_layout = QtWidgets.QHBoxLayout()
        self._horizontal_layout.addWidget(self._label)
        self._horizontal_layout.addWidget(self._name_input)
        
        self._main_layout.addLayout(self._horizontal_layout)

        # Solver attributes
        solver_group = QtWidgets.QGroupBox("Solver Attributes")
        form_layout = QtWidgets.QFormLayout()
        solver_group.setLayout(form_layout)
        self._main_layout.addWidget(solver_group)

        # Iterations
        label = QtWidgets.QLabel("Iterations:")
        horizontal_layout = QtWidgets.QHBoxLayout()
        self.iterations_spin = QtWidgets.QDoubleSpinBox()
        self.iterations_spin.setDecimals(0)
        self.iterations_spin.setMinimum(1)
        self.iterations_spin.setMaximum(5000)
        self.iterations_spin.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.iterations_spin.setMaximumWidth(65)
        self.iterations_spin.setMinimumWidth(65)
        self.iterations_slider = QtWidgets.QSlider()
        self.iterations_slider.setOrientation(QtCore.Qt.Horizontal)
        self.iterations_slider.setSingleStep(1)
        self.iterations_slider.setMinimum(1)
        self.iterations_slider.setMaximum(10)
        self.iterations_slider.setMaximumWidth(150)
        self.iterations_slider.setMinimumWidth(150)

        horizontal_layout.addWidget(self.iterations_spin)
        horizontal_layout.addWidget(self.iterations_slider)
        form_layout.addRow(label, horizontal_layout)

        # Material Selection Dropdown
        label = QtWidgets.QLabel("Material:")
        self.material_combo = QtWidgets.QComboBox()
        self.material_combo.setMinimumWidth(250)
        self.material_combo.addItems(self._materials_list)
        self.material_combo.setCurrentIndex(0)
        self.material_combo.setMaximumWidth(150)

        form_layout.addRow(label, self.material_combo)

        # Stiffness multiplier
        label = QtWidgets.QLabel("Stiffness Multiplier:")
        horizontal_layout = QtWidgets.QHBoxLayout()
        self.stiffness_spin = QtWidgets.QDoubleSpinBox()
        self.stiffness_spin.setDecimals(3)
        self.stiffness_spin.setMinimum(0)
        self.stiffness_spin.setMaximum(5000)
        self.stiffness_spin.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.stiffness_spin.setMaximumWidth(65)
        self.stiffness_spin.setMinimumWidth(65)
        self.stiffness_spin.setValue(1)
        self.stiffness_slider = QtWidgets.QSlider()
        self.stiffness_slider.setOrientation(QtCore.Qt.Horizontal)
        self.stiffness_slider.setSingleStep(1)
        self.stiffness_slider.setMinimum(0)
        self.stiffness_slider.setMaximum(2000)
        self.stiffness_slider.setMaximumWidth(150)
        self.stiffness_slider.setMinimumWidth(150)
        self.stiffness_slider.setValue(1000)

        horizontal_layout.addWidget(self.stiffness_spin)
        horizontal_layout.addWidget(self.stiffness_slider)
        form_layout.addRow(label, horizontal_layout)

        # Time attributes
        time_group = QtWidgets.QGroupBox("Time Attributes")
        form_layout = QtWidgets.QFormLayout()
        time_group.setLayout(form_layout)
        self._main_layout.addWidget(time_group)
        current_time = self._dcc_scene_commands.get_current_time()

        # Preroll start time
        label = QtWidgets.QLabel("Preroll Start Time:")
        horizontal_layout = QtWidgets.QHBoxLayout()
        self.preroll_start_spin = QtWidgets.QDoubleSpinBox()
        self.preroll_start_spin.setDecimals(0)
        self.preroll_start_spin.setMinimum(current_time - 5000)
        self.preroll_start_spin.setMaximum(current_time + 5000)
        self.preroll_start_spin.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.preroll_start_spin.setMaximumWidth(65)
        self.preroll_start_spin.setMinimumWidth(65)
        self.preroll_start_spin.setValue(current_time)

        horizontal_layout.addWidget(self.preroll_start_spin)
        form_layout.addRow(label, horizontal_layout)

        # Start time
        label = QtWidgets.QLabel("Start Time:")
        horizontal_layout = QtWidgets.QHBoxLayout()
        self.start_spin = QtWidgets.QDoubleSpinBox()
        self.start_spin.setDecimals(0)
        self.start_spin.setMinimum(current_time - 5000)
        self.start_spin.setMaximum(current_time + 5000)
        self.start_spin.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.start_spin.setMaximumWidth(65)
        self.start_spin.setMinimumWidth(65)
        self.start_spin.setValue(current_time)

        horizontal_layout.addWidget(self.start_spin)
        form_layout.addRow(label, horizontal_layout)

        # Scale attributes
        scale_group = QtWidgets.QGroupBox("Scale Attributes")
        form_layout = QtWidgets.QFormLayout()
        scale_group.setLayout(form_layout)
        self._main_layout.addWidget(scale_group)

        # Time scale
        label = QtWidgets.QLabel("Time Scale:")
        horizontal_layout = QtWidgets.QHBoxLayout()
        self.time_scale_spin = QtWidgets.QDoubleSpinBox()
        self.time_scale_spin.setDecimals(3)
        self.time_scale_spin.setMinimum(0.001)
        self.time_scale_spin.setMaximum(5000)
        self.time_scale_spin.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.time_scale_spin.setMaximumWidth(65)
        self.time_scale_spin.setMinimumWidth(65)
        self.time_scale_spin.setValue(1)
        self.time_scale_slider = QtWidgets.QSlider()
        self.time_scale_slider.setOrientation(QtCore.Qt.Horizontal)
        self.time_scale_slider.setSingleStep(1)
        self.time_scale_slider.setMinimum(1)
        self.time_scale_slider.setMaximum(10000)
        self.time_scale_slider.setMaximumWidth(150)
        self.time_scale_slider.setMinimumWidth(150)
        self.time_scale_slider.setValue(1000)

        horizontal_layout.addWidget(self.time_scale_spin)
        horizontal_layout.addWidget(self.time_scale_slider)
        form_layout.addRow(label, horizontal_layout)

        # Space scale
        label = QtWidgets.QLabel("Space Scale:")
        horizontal_layout = QtWidgets.QHBoxLayout()
        self.space_scale_spin = QtWidgets.QDoubleSpinBox()
        self.space_scale_spin.setDecimals(3)
        self.space_scale_spin.setMinimum(0.001)
        self.space_scale_spin.setMaximum(5000)
        self.space_scale_spin.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.space_scale_spin.setMaximumWidth(65)
        self.space_scale_spin.setMinimumWidth(65)
        self.space_scale_spin.setValue(1)
        self.space_scale_slider = QtWidgets.QSlider()
        self.space_scale_slider.setOrientation(QtCore.Qt.Horizontal)
        self.space_scale_slider.setSingleStep(1)
        self.space_scale_slider.setMinimum(1)
        self.space_scale_slider.setMaximum(100000)
        self.space_scale_slider.setMaximumWidth(150)
        self.space_scale_slider.setMinimumWidth(150)
        self.space_scale_slider.setValue(1000)

        horizontal_layout.addWidget(self.space_scale_spin)
        horizontal_layout.addWidget(self.space_scale_slider)
        form_layout.addRow(label, horizontal_layout)

        # Dynamic properties
        dynamic_group = QtWidgets.QGroupBox("Dynamic Properties")
        form_layout = QtWidgets.QFormLayout()
        dynamic_group.setLayout(form_layout)
        self._main_layout.addWidget(dynamic_group)

        # Gravity
        label = QtWidgets.QLabel("Gravity:")
        horizontal_layout = QtWidgets.QHBoxLayout()
        self.gravity_spin = QtWidgets.QDoubleSpinBox()
        self.gravity_spin.setDecimals(3)
        self.gravity_spin.setMinimum(0)
        self.gravity_spin.setMaximum(5000)
        self.gravity_spin.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.gravity_spin.setMaximumWidth(65)
        self.gravity_spin.setMinimumWidth(65)
        self.gravity_spin.setValue(0)
        self.gravity_slider = QtWidgets.QSlider()
        self.gravity_slider.setOrientation(QtCore.Qt.Horizontal)
        self.gravity_slider.setSingleStep(1)
        self.gravity_slider.setMinimum(0)
        self.gravity_slider.setMaximum(100000)
        self.gravity_slider.setMaximumWidth(150)
        self.gravity_slider.setMinimumWidth(150)
        self.gravity_slider.setValue(0)

        horizontal_layout.addWidget(self.gravity_spin)
        horizontal_layout.addWidget(self.gravity_slider)
        form_layout.addRow(label, horizontal_layout)

        # Gravity direction
        label = QtWidgets.QLabel("Gravity Direction:")
        horizontal_layout = QtWidgets.QHBoxLayout()
        self.gravity_dir_x_spin = QtWidgets.QDoubleSpinBox()
        self.gravity_dir_x_spin.setDecimals(3)
        self.gravity_dir_x_spin.setMinimum(-5000)
        self.gravity_dir_x_spin.setMaximum(5000)
        self.gravity_dir_x_spin.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.gravity_dir_x_spin.setMaximumWidth(65)
        self.gravity_dir_x_spin.setMinimumWidth(65)
        self.gravity_dir_x_spin.setValue(0)
        self.gravity_dir_y_spin = QtWidgets.QDoubleSpinBox()
        self.gravity_dir_y_spin.setDecimals(3)
        self.gravity_dir_y_spin.setMinimum(-5000)
        self.gravity_dir_y_spin.setMaximum(5000)
        self.gravity_dir_y_spin.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.gravity_dir_y_spin.setMaximumWidth(65)
        self.gravity_dir_y_spin.setMinimumWidth(65)
        self.gravity_dir_y_spin.setValue(-1)
        self.gravity_dir_z_spin = QtWidgets.QDoubleSpinBox()
        self.gravity_dir_z_spin.setDecimals(3)
        self.gravity_dir_z_spin.setMinimum(-5000)
        self.gravity_dir_z_spin.setMaximum(5000)
        self.gravity_dir_z_spin.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.gravity_dir_z_spin.setMaximumWidth(65)
        self.gravity_dir_z_spin.setMinimumWidth(65)
        self.gravity_dir_z_spin.setValue(0)

        horizontal_layout.addWidget(self.gravity_dir_x_spin)
        horizontal_layout.addWidget(self.gravity_dir_y_spin)
        horizontal_layout.addWidget(self.gravity_dir_z_spin)
        form_layout.addRow(label, horizontal_layout)

        # Global damping multiplier
        label = QtWidgets.QLabel("Global Damp. Multiplier:")
        horizontal_layout = QtWidgets.QHBoxLayout()
        self.global_damp_spin = QtWidgets.QDoubleSpinBox()
        self.global_damp_spin.setDecimals(3)
        self.global_damp_spin.setMinimum(0)
        self.global_damp_spin.setMaximum(1)
        self.global_damp_spin.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.global_damp_spin.setMaximumWidth(65)
        self.global_damp_spin.setMinimumWidth(65)
        self.global_damp_spin.setValue(0.75)
        self.global_damp_slider = QtWidgets.QSlider()
        self.global_damp_slider.setOrientation(QtCore.Qt.Horizontal)
        self.global_damp_slider.setSingleStep(1)
        self.global_damp_slider.setMinimum(0)
        self.global_damp_slider.setMaximum(1000)
        self.global_damp_slider.setMaximumWidth(150)
        self.global_damp_slider.setMinimumWidth(150)
        self.global_damp_slider.setValue(750)

        horizontal_layout.addWidget(self.global_damp_spin)
        horizontal_layout.addWidget(self.global_damp_slider)
        form_layout.addRow(label, horizontal_layout)

        # Inertia damper
        label = QtWidgets.QLabel("Inertia Damper:")
        horizontal_layout = QtWidgets.QHBoxLayout()
        self.inertia_spin = QtWidgets.QDoubleSpinBox()
        self.inertia_spin.setDecimals(3)
        self.inertia_spin.setMinimum(0)
        self.inertia_spin.setMaximum(1)
        self.inertia_spin.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.inertia_spin.setMaximumWidth(65)
        self.inertia_spin.setMinimumWidth(65)
        self.inertia_slider = QtWidgets.QSlider()
        self.inertia_slider.setOrientation(QtCore.Qt.Horizontal)
        self.inertia_slider.setSingleStep(1)
        self.inertia_slider.setMinimum(0)
        self.inertia_slider.setMaximum(1000)
        self.inertia_slider.setMaximumWidth(150)
        self.inertia_slider.setMinimumWidth(150)

        horizontal_layout.addWidget(self.inertia_spin)
        horizontal_layout.addWidget(self.inertia_slider)
        form_layout.addRow(label, horizontal_layout)

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

        # Different default material and iteration values depending on the deformer type
        if self._node_type in [DeformerTypes.MUSCLE, DeformerTypes.RIBBON]:
            self.iterations_spin.setValue(10)
            self.iterations_slider.setValue(10)
            self.material_combo.setCurrentIndex(1)
        elif self._node_type in [DeformerTypes.FAT]:
            self.iterations_spin.setValue(5)
            self.iterations_slider.setValue(5)
            self.material_combo.setCurrentIndex(0)
            self.global_damp_spin.setValue(0.1)
            self.global_damp_slider.setValue(0.1)
        else:
            self.iterations_spin.setValue(3)
            self.iterations_slider.setValue(3)
            self.material_combo.setCurrentIndex(7)

    def _connect_signals(self):
        """Connect signals to all of the components of the UI."""
        # Connect signals
        self._name_input.textEdited.connect(self._validate_name)
        self.iterations_spin.valueChanged.connect(
            lambda: self._widget_changed(self.iterations_spin, self.iterations_slider, 1))
        self.iterations_slider.valueChanged.connect(
            lambda: self._widget_changed(self.iterations_slider, self.iterations_spin, 1))
        self.stiffness_spin.valueChanged.connect(
            lambda: self._widget_changed(self.stiffness_spin, self.stiffness_slider, 1000))
        self.stiffness_slider.valueChanged.connect(
            lambda: self._widget_changed(self.stiffness_slider, self.stiffness_spin, 0.001))
        self.time_scale_spin.valueChanged.connect(
            lambda: self._widget_changed(self.time_scale_spin, self.time_scale_slider, 1000))
        self.time_scale_slider.valueChanged.connect(
            lambda: self._widget_changed(self.time_scale_slider, self.time_scale_spin, 0.001))
        self.space_scale_spin.valueChanged.connect(
            lambda: self._widget_changed(self.space_scale_spin, self.space_scale_slider, 1000))
        self.space_scale_slider.valueChanged.connect(
            lambda: self._widget_changed(self.space_scale_slider, self.space_scale_spin, 0.001))
        self.gravity_spin.valueChanged.connect(
            lambda: self._widget_changed(self.gravity_spin, self.gravity_slider, 1000))
        self.gravity_slider.valueChanged.connect(
            lambda: self._widget_changed(self.gravity_slider, self.gravity_spin, 0.001))
        self.global_damp_spin.valueChanged.connect(
            lambda: self._widget_changed(self.global_damp_spin, self.global_damp_slider, 1000))
        self.global_damp_slider.valueChanged.connect(
            lambda: self._widget_changed(self.global_damp_slider, self.global_damp_spin, 0.001))
        self.inertia_spin.valueChanged.connect(
            lambda: self._widget_changed(self.inertia_spin, self.inertia_slider, 1000))
        self.inertia_slider.valueChanged.connect(
            lambda: self._widget_changed(self.inertia_slider, self.inertia_spin, 0.001))

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

    def _widget_changed(self, widget_changed, widget_to_update, multiplier):
        """Modify an UI element based on the value of another one and a multiplier.
        
        Args:
            widget_changed (:obj:`QtWidget`): UI component to read value. Altered by the user.
            widget_to_update (:obj:`QtWidget`): UI component to apply an updated value.
            multiplier (float): multiplier to scale one UI value to the other.
        """
        value = widget_changed.value() * multiplier
        widget_to_update.blockSignals(True)
        if value > widget_to_update.maximum():
            widget_to_update.setMaximum(2 * value)
        widget_to_update.setValue(value)
        widget_to_update.blockSignals(False)

    def keyPressEvent(self, qKeyEvent):
        """Overload the keyPressEvent to trigger the creation method if the
        user press Enter."""
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if (qKeyEvent.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter) and
                modifiers == QtCore.Qt.NoModifier):
            self._create_on_clicked()
        else:
            super(DeformersCreatorUI, self).keyPressEvent(qKeyEvent)

    def _create_on_clicked(self):
        """Create deformer and set it up with the selected settings"""
        custom_name = self._name_input.text()
        if not custom_name or not is_identifier(custom_name):
            # This code should never be reached
            self._create_button.setEnabled(False)
            self._name_input.setStyleSheet(self._wrong_input_name_stylesheet)
            return

        deformer_name, result = self._node_creation_method(custom_name)
        if not result:
            msg_box(main_window(), "error",
                    "An error occurred when creating an {0}. Please, check "
                    "the console for more information.".format(self._node_type))
            return
        if not deformer_name:
            msg_box(main_window(), "warning",
                    "{0} not created. Please, check "
                    "the console for more information.".format(self._node_type))
            return
        
        gravity_dir = [self.gravity_dir_x_spin.value(),
                       self.gravity_dir_y_spin.value(),
                       self.gravity_dir_z_spin.value()]
        
        attribute_dict = {
            "iterations": self.iterations_spin.value(),
            "stiffnessMultiplier": self.stiffness_spin.value(),
            "material": self.material_combo.currentIndex(),
            "prerollStartTime": self.preroll_start_spin.value(),
            "startTime": self.start_spin.value(),
            "timeScale": self.time_scale_spin.value(),
            "spaceScale": self.space_scale_spin.value(),
            "gravity": self.gravity_spin.value(),
            "gravityDirection": gravity_dir,
            "globalDampingMultiplier": self.global_damp_spin.value(),
            "inertiaDamper": self.inertia_spin.value()
        }
        self._dcc_tool.configure_attributes(deformer_name, attribute_dict)

        self.close()
