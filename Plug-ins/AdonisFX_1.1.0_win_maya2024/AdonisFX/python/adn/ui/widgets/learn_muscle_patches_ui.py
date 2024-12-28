import os

from PySide2 import QtCore, QtGui, QtWidgets

from adn.ui.widgets.base import BaseWidget
from adn.ui.widgets.dialogs import msg_box
from adn.ui.utils import cursor
from adn.utils.constants import UiConstants


class LearnMusclePatchesUI(BaseWidget):
    """UI class for the muscle patches calculation.

    Class used to generate muscle patches on an input mesh.

    Args:
        dcc_tool (module): Tool that will be launching the command associated to the UI.
        dcc_scene_commands (module): Commands that will invoke scene functions.
        parent (:obj:`BaseWidget`): Parent class of the current UI class.
        *args: Argument list.
        **kwargs: Keyword argument list.
    """
    def __init__(self, dcc_tool, dcc_scene_commands, parent, *args, **kwargs):
        super(LearnMusclePatchesUI, self).__init__("Learn Muscle Patches",
                                                   parent,
                                                   width=500,
                                                   height=800)

        self._parent = parent

        self._dcc_tool = dcc_tool
        self._dcc_scene_commands = dcc_scene_commands

        # Class private attributes
        self._neutral_mesh = None
        self._target_meshes = None
        self._vertices_mask = None
        self._destination_file = ""
        self._neutral_ok = False
        self._targets_ok = False
        self._mask_ok = False
        self._file_ok = False

        self._adonis_env = os.getenv("ADONISFX_RESOURCES", "")

        self._build_ui()

    def _build_ui(self):
        """Builds the UI for the muscle patches calculation."""
        self._file_icon_path = "{0}/adn_file.png".format(self._adonis_env)
        self._file_icon = QtGui.QIcon(self._file_icon_path)
        self._execute_icon_path = "{0}/adn_execute.png".format(self._adonis_env)
        self._execute_icon = QtGui.QIcon(self._execute_icon_path)
        self._trash_icon_path = "{0}/adn_bin.png".format(self._adonis_env)
        self._trash_icon = QtGui.QIcon(self._trash_icon_path)

        # General parameters
        self._button_width = 200
        self._button_height = 60

        # Specific parameters
        self._target_text_height = 80

        ###############################
        # BEGIN NEUTRAL MESH SECTION
        ###############################
        # Neutral mesh component definition
        self._neutral_text_edit = QtWidgets.QLineEdit()
        self._neutral_text_edit.setReadOnly(True)
        self._neutral_text_edit.setPlaceholderText("Select a neutral mesh")
        self._neutral_text_edit.setToolTip("Select the base mesh on which to calculate the muscle patches.")

        self._add_neutral_button = QtWidgets.QPushButton("Add Selected")
        self._add_neutral_button.resize(QtCore.QSize(self._button_width, self._button_height))
        self._add_neutral_button.clicked.connect(self._neutral_on_clicked)

        self._clear_neutral_button = QtWidgets.QPushButton("Clear")
        self._clear_neutral_button.resize(QtCore.QSize(self._button_width, self._button_height))
        self._clear_neutral_button.clicked.connect(self._neutral_on_cleared)

        # Neutral mesh section layout
        self._neutral_top_horizontal_layout = QtWidgets.QHBoxLayout()
        self._neutral_top_horizontal_layout.addWidget(self._neutral_text_edit)

        self._neutral_bottom_horizontal_layout = QtWidgets.QHBoxLayout()
        self._neutral_bottom_horizontal_layout.addWidget(self._add_neutral_button)
        self._neutral_bottom_horizontal_layout.addWidget(self._clear_neutral_button)

        self._neutral_global_vertical_layout = QtWidgets.QVBoxLayout()
        self._neutral_global_vertical_layout.addLayout(self._neutral_top_horizontal_layout)
        self._neutral_global_vertical_layout.addLayout(self._neutral_bottom_horizontal_layout)

        self._neutral_group = QtWidgets.QGroupBox()
        self._neutral_group.setTitle("Neutral Mesh")
        self._neutral_group.setLayout(self._neutral_global_vertical_layout)

        self._main_layout.addWidget(self._neutral_group)

        ###############################
        # BEGIN TARGET MESHES
        ###############################
        # Target meshes component definition
        self._target_list = QtWidgets.QListWidget()
        self._target_list.setMinimumHeight(self._target_text_height)
        self._target_list.setToolTip("Select the target meshes from which muscle patches will be calculated.")

        self._add_target_button = QtWidgets.QPushButton("Add Selected")
        self._add_target_button.resize(QtCore.QSize(self._button_width, self._button_height))
        self._add_target_button.clicked.connect(self._targets_on_clicked)

        self._clear_target_button = QtWidgets.QPushButton("Clear")
        self._clear_target_button.resize(QtCore.QSize(self._button_width, self._button_height))
        self._clear_target_button.clicked.connect(self._targets_on_cleared)

        # Target meshes section layout
        self._target_top_horizontal_layout = QtWidgets.QHBoxLayout()
        self._target_top_horizontal_layout.addWidget(self._target_list)

        self._target_bottom_horizontal_layout = QtWidgets.QHBoxLayout()
        self._target_bottom_horizontal_layout.addWidget(self._add_target_button)
        self._target_bottom_horizontal_layout.addWidget(self._clear_target_button)

        self._target_global_vertical_layout = QtWidgets.QVBoxLayout()
        self._target_global_vertical_layout.addLayout(self._target_top_horizontal_layout)
        self._target_global_vertical_layout.addLayout(self._target_bottom_horizontal_layout)

        self._target_group = QtWidgets.QGroupBox()
        self._target_group.setTitle("Target Meshes")
        self._target_group.setLayout(self._target_global_vertical_layout)

        self._main_layout.addWidget(self._target_group)

        ###############################
        # BEGIN VERTICES MASK SECTION
        ###############################
        # Vertices mask component definition
        self._mask_text_edit = QtWidgets.QLineEdit()
        self._mask_text_edit.setReadOnly(True)
        self._mask_text_edit.setPlaceholderText("Select the vertices mask")
        self._mask_text_edit.setToolTip("Select the vertices mask to set the area of the muscle patches calculation.")

        self._add_mask_button = QtWidgets.QPushButton("Add Selected")
        self._add_mask_button.resize(QtCore.QSize(self._button_width, self._button_height))
        self._add_mask_button.clicked.connect(self._mask_on_clicked)

        self._clear_mask_button = QtWidgets.QPushButton("Clear")
        self._clear_mask_button.resize(QtCore.QSize(self._button_width, self._button_height))
        self._clear_mask_button.clicked.connect(self._mask_on_cleared)

        # Vertices mask section layout
        self._mask_top_horizontal_layout = QtWidgets.QHBoxLayout()
        self._mask_top_horizontal_layout.addWidget(self._mask_text_edit)

        self._mask_bottom_horizontal_layout = QtWidgets.QHBoxLayout()
        self._mask_bottom_horizontal_layout.addWidget(self._add_mask_button)
        self._mask_bottom_horizontal_layout.addWidget(self._clear_mask_button)

        self._mask_global_vertical_layout = QtWidgets.QVBoxLayout()
        self._mask_global_vertical_layout.addLayout(self._mask_top_horizontal_layout)
        self._mask_global_vertical_layout.addLayout(self._mask_bottom_horizontal_layout)

        self._mask_group = QtWidgets.QGroupBox()
        self._mask_group.setTitle("Vertices Mask")
        self._mask_group.setLayout(self._mask_global_vertical_layout)

        self._main_layout.addWidget(self._mask_group)

        ###############################
        # BEGIN FILE SELECTION SECTION
        ###############################
        # File selection component definition
        self._file_text_edit = QtWidgets.QLineEdit()
        self._file_text_edit.setReadOnly(True)
        self._file_text_edit.setPlaceholderText("Select output file path")
        self._file_text_edit.setToolTip("Select a file path to save the generated muscle patches data.")

        self._add_file_button = QtWidgets.QPushButton()
        self._add_file_button.setIcon(self._file_icon)
        self._add_file_button.setIconSize(QtCore.QSize(16, 16))
        self._add_file_button.resize(QtCore.QSize(self._button_width, self._button_height))
        self._add_file_button.clicked.connect(self._file_on_clicked)

        # File selection section layout
        self._file_left_horizontal_layout = QtWidgets.QHBoxLayout()
        self._file_left_horizontal_layout.addWidget(self._file_text_edit)

        self._file_right_vertical_layout = QtWidgets.QVBoxLayout()
        self._file_right_vertical_layout.addWidget(self._add_file_button)

        self._file_global_horizontal_layout = QtWidgets.QHBoxLayout()
        self._file_global_horizontal_layout.addLayout(self._file_left_horizontal_layout)
        self._file_global_horizontal_layout.addLayout(self._file_right_vertical_layout)

        self._file_group = QtWidgets.QGroupBox()
        self._file_group.setTitle("Output File Path")
        self._file_group.setLayout(self._file_global_horizontal_layout)

        self._main_layout.addWidget(self._file_group)

        ###############################
        # BEGIN SETTINGS SECTION
        ###############################
        # Settings component definition
        self._limit_checkbox = QtWidgets.QCheckBox()
        self._limit_checkbox.stateChanged.connect(self._handle_limit_mode)
        self._limit_checkbox.setChecked(False)
        self._limit_checkbox.setToolTip("Toggle the limit of iterations for the muscle patches calculation.")

        self._limit_text = QtWidgets.QLabel("Limit iterations:")

        self._limit_text_edit = QtWidgets.QSpinBox()
        self._limit_text_edit.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self._limit_text_edit.setValue(20)
        self._limit_text_edit.setRange(1, 1e6)
        self._limit_text_edit.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self._limit_text_edit.setEnabled(False)
        self._limit_text_edit.setToolTip("Set the limit of iterations for the muscle patches calculation.")

        self._num_muscle_patches_text = QtWidgets.QLabel("Number of muscle patches:")

        self._num_muscle_patches_text_edit = QtWidgets.QSpinBox()
        self._num_muscle_patches_text_edit.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self._num_muscle_patches_text_edit.setValue(79)
        self._num_muscle_patches_text_edit.setRange(1, 1e6)
        self._num_muscle_patches_text_edit.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self._num_muscle_patches_text_edit.setToolTip("Set the number of muscle patches that should be calculated.")

        self._draw_text = QtWidgets.QLabel("Draw muscle patches:")

        self._draw_checkbox = QtWidgets.QCheckBox()
        self._draw_checkbox.setChecked(False)
        self._draw_checkbox.setToolTip("Draw the muscle patches using the paint tool option.")

        # Settings section layout
        self._right_settings_layout = QtWidgets.QHBoxLayout()
        self._right_settings_layout.addWidget(self._limit_checkbox)
        self._right_settings_layout.addWidget(self._limit_text_edit)

        self._settings_layout = QtWidgets.QGridLayout()
        self._settings_layout.addWidget(self._limit_text, 1, 1)
        self._settings_layout.addLayout(self._right_settings_layout, 1, 2)
        self._settings_layout.addWidget(self._num_muscle_patches_text, 2, 1)
        self._settings_layout.addWidget(self._num_muscle_patches_text_edit, 2, 2)
        self._settings_layout.addWidget(self._draw_text, 3, 1)
        self._settings_layout.addWidget(self._draw_checkbox, 3, 2)

        self._settings_group = QtWidgets.QGroupBox()
        self._settings_group.setTitle("Settings")
        self._settings_group.setLayout(self._settings_layout)

        self._main_layout.addWidget(self._settings_group)

        self._spacer = QtWidgets.QSpacerItem(0, 10, QtWidgets.QSizePolicy.Expanding)
        self._main_layout.addSpacerItem(self._spacer)

        self._line = QtWidgets.QFrame()
        self._line.setFrameShape(QtWidgets.QFrame.HLine)
        self._line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self._main_layout.addWidget(self._line)

        ###############################
        # BEGIN RUN SECTION
        ###############################
        # Run component definition
        self._clear_all_button = QtWidgets.QPushButton("Clear All")
        self._clear_all_button.setIcon(self._trash_icon)
        self._clear_all_button.setIconSize(QtCore.QSize(18, 18))
        self._clear_all_button.resize(QtCore.QSize(self._button_width, self._button_height))
        self._clear_all_button.clicked.connect(self._clear_all_on_clicked)

        self._run_button = QtWidgets.QPushButton("Execute")
        self._run_button.setIcon(self._execute_icon)
        self._run_button.setIconSize(QtCore.QSize(18, 18))
        self._run_button.resize(QtCore.QSize(self._button_width, self._button_height))
        self._run_button.clicked.connect(self._execute_on_clicked)
        self._run_button.setEnabled(False)

        # Run section layout
        self._run_horizontal_layout = QtWidgets.QHBoxLayout()
        self._run_horizontal_layout.addWidget(self._clear_all_button)
        self._run_horizontal_layout.addWidget(self._run_button)

        self._main_layout.addLayout(self._run_horizontal_layout)

    def _check_all_go(self):
        """Checks if all input values have been correctly added"""
        self._run_button.setEnabled(self._neutral_ok and self._targets_ok
                                    and self._mask_ok and self._file_ok)

    def _handle_limit_mode(self):
        """Activate or deactivate the iteration limit textbox depending
        on the value of the checkbox.
        """
        self._limit_text_edit.setEnabled(self._limit_checkbox.isChecked())

    def _neutral_on_clicked(self):
        """Get the selected neutral mesh. Sanity checks are launched when the
        select button in a neutral mesh context is launched.
        """
        self._neutral_on_cleared()
        tmp_neutral_mesh = self._dcc_scene_commands.get_selection()

        # No neutral mesh is selected.
        if not tmp_neutral_mesh:
            msg_box(self._parent, "error", "No neutral mesh selected.")
            return
        neutral_mesh_name = tmp_neutral_mesh[0]

        # More than one geometry selected, so get the first one.
        if len(tmp_neutral_mesh) > 1:
            print(("{0} More than one geometry selected. "
                   "Selecting the first geometry: {1}.").format(UiConstants.LOG_PREFIX, neutral_mesh_name))

        # Check if the neutral mesh is not a mesh object.
        if not self._dcc_scene_commands.is_mesh(neutral_mesh_name):
            msg_box(self._parent, "error",
                    "Neutral mesh selected object {0} is not a mesh.".format(neutral_mesh_name))
            return

        if neutral_mesh_name:
            print("{0} Neutral mesh {1} selected.".format(UiConstants.LOG_PREFIX, neutral_mesh_name))

        self._neutral_mesh = neutral_mesh_name
        self._neutral_ok = True
        self._neutral_text_edit.setText(self._neutral_mesh)
        self._check_all_go()

    def _neutral_on_cleared(self):
        """Clear the flag, input text and value for the neutral mesh when
        the clear button is pressed.
        """
        self._neutral_mesh = None
        self._neutral_ok = False
        self._neutral_text_edit.setText("")
        self._check_all_go()

    def _targets_on_clicked(self):
        """Get the selected target meshes. Sanity checks are launched when the
        select button in a target meshes context is launched.
        """
        self._targets_on_cleared()

        # No neutral mesh was selected before selecting the target meshes.
        if not self._neutral_mesh:
            msg_box(self._parent, "error", "Select a neutral mesh before selecting the targets.")
            return
        neutral_vertex_count = self._dcc_scene_commands.get_num_vertices(self._neutral_mesh)
        tmp_target_meshes = self._dcc_scene_commands.get_selection()

        # No target meshes selected.
        if not tmp_target_meshes:
            msg_box(self._parent, "error", "No target meshes selected.")
            return
        tmp_target_meshes = [targ for targ in tmp_target_meshes if self._dcc_scene_commands.is_mesh(targ)]

        # The target selection does not contain a mesh object.
        if not tmp_target_meshes:
            msg_box(self._parent, "error",
                    "The target selection does not contain any mesh objects.")
            return
        not_mesh_list = [targ for targ in tmp_target_meshes if targ not in tmp_target_meshes]

        # Ignore non mesh objects for the targets.
        if not_mesh_list:
            print("{0} Ignored targets: {1}.".format(UiConstants.LOG_PREFIX, not_mesh_list))
        vertex_count = [self._dcc_scene_commands.get_num_vertices(targ) for targ in tmp_target_meshes]

        # Make sure that the vertex count of neutral and all target meshes match.
        if not vertex_count.count(neutral_vertex_count) == len(vertex_count):
            msg_box(self._parent, "error",
                    "Make sure that the vertex count of neutral and all target meshes match.")
            return
        self._target_meshes = tmp_target_meshes
        if self._target_meshes:
            print("{0} Using {1} mesh targets: {2}.".format(UiConstants.LOG_PREFIX,
                                                            len(self._target_meshes),
                                                            self._target_meshes))
        self._targets_ok = True
        for target in self._target_meshes:
            self._target_list.addItem(target)
        self._target_list.sortItems()
        self._check_all_go()

    def _targets_on_cleared(self):
        """Clear the flag, input text and value for the target meshes when
        the clear button is pressed.
        """
        self._target_meshes = None
        self._targets_ok = False
        self._target_list.clear()
        self._check_all_go()

    def _mask_on_clicked(self):
        """Get the selected vertices when clicked. Sanity checks are launched when the
        select button in a vertices mask context is launched.
        """
        self._mask_on_cleared()

        # Make sure that a neutral mesh is selected before selecting the vertices mask.
        if not self._neutral_ok:
            msg_box(self._parent,
                    "error", "Select the neutral mesh first before selecting vertices.")
            return
        selection = self._dcc_scene_commands.get_selection(flatten=True)
        selection_not_flatten = self._dcc_scene_commands.get_selection()
        tmp_vertices_mask = []

        # Check if what is being parsed are integer vertex indices.
        try:
            tmp_vertices_mask = [int(x.partition("[")[2].partition("]")[0]) for x in selection]
        except:
            msg_box(self._parent, "error", "No valid vertex mask selection provided.")
            return
        num_vertices = self._dcc_scene_commands.get_num_vertices(self._neutral_mesh)

        # Check if the number of vertices in the mask is greater
        # than the neutral mesh vertices count.
        if tmp_vertices_mask and len(tmp_vertices_mask) > num_vertices:
            msg_box(self._parent, "error",
                    "The amount of selected vertices is greater than the neutral mesh vertex count.")
            return
        self._vertices_mask = tmp_vertices_mask
        if not self._vertices_mask:
            msg_box(self._parent, "Information",
                    "No vertices provided. All vertices of the neutral mesh are used.")
        else:
            print(("{0} Selected vertices provided "
                   "for the vertex mask: {1}.").format(UiConstants.LOG_PREFIX, len(self._vertices_mask)))
            mask_vertices = [x.partition("[")[2].partition("]")[0] for x in selection_not_flatten]
            self._mask_text_edit.setText(",".join(str(e) for e in mask_vertices))
        self._mask_ok = True
        self._check_all_go()

    def _mask_on_cleared(self):
        """Clear the flag, input text and value for the vertices mask when
        the clear button is pressed.
        """
        self._vertices_mask = None
        self._mask_ok = False
        self._mask_text_edit.setText("")
        self._check_all_go()

    def _file_on_clicked(self):
        """Open a file selection dialog when clicked. Sanity checks
        are launched when the select button in a file selection context is launched.
        """
        self._file_on_cleared()

        tmp_destination_file = QtWidgets.QFileDialog.getSaveFileName(
            self,
            caption="Save AdonisFX Muscle Patches",
            filter="AdonisFX Muscle Patches (*.amp)")[0]

        # Check if the destination file path was set correctly.
        if not tmp_destination_file:
            msg_box(self._parent, "error", ".amp file path is empty.")
            return
        self._destination_file = tmp_destination_file
        self._file_ok = True
        self._file_text_edit.setText(self._destination_file)
        self._check_all_go()

    def _file_on_cleared(self):
        """Clear the flag, input text and value for the output
        file path when the clear button is pressed.
        """
        self._destination_file = None
        self._file_ok = False
        self._file_text_edit.setText("")
        self._check_all_go()

    def _clear_all_on_clicked(self):
        """Clears and resets all inputs.
        """
        self._neutral_on_cleared()
        self._targets_on_cleared()
        self._mask_on_cleared()
        self._file_on_cleared()

    def _check_on_run(self):
        """Check if data provided in the UI is valid and can be
        used to launch the muscle patch calculation algorithm.

        Returns:
            bool: returns the outcome of the check before the execution.
        """
        num_vertices = self._dcc_scene_commands.get_num_vertices(self._neutral_mesh)
        neutral_check = self._dcc_scene_commands.exists(self._neutral_mesh)
        if not neutral_check:
            msg_box(self._parent, "error", "Neutral mesh not found in the scene.")
        target_check = all([self._dcc_scene_commands.exists(target) for target in self._target_meshes])
        if not target_check:
            msg_box(self._parent, "error", "Target meshes not found in the scene.")
        else:
            vertex_count = [self._dcc_scene_commands.get_num_vertices(targ) for targ in self._target_meshes]
            # Make sure that the vertex count of neutral and all target meshes match.
            if not vertex_count.count(num_vertices) == len(vertex_count):
                msg_box(self._parent, "error",
                        "Make sure that the vertex count of neutral and all target meshes match.")
                target_check = False
        file_check = os.path.isabs(self._destination_file)
        if not file_check:
            msg_box(self._parent, "error", "File path invalid.")
        muscle_patches_check = bool(self._num_muscle_patches_text_edit.text())
        if not muscle_patches_check:
            msg_box(self._parent, "error", "Empty number of muscle patches.")
        limit_check = bool(self._limit_text_edit.text())
        if self._limit_checkbox.isChecked() and not limit_check:
            msg_box(self._parent, "error", "Empty limit of iterations.")
        else:
            limit_check = True
        vertex_check = True
        if self._vertices_mask and (len(self._vertices_mask) > num_vertices or
                                    max(self._vertices_mask) >= num_vertices):
            msg_box(self._parent, "error",
                    "The amount of selected vertices is greater than the neutral mesh vertex count or "
                    "the vertex mask contains vertices not found in the neutral mesh.")
            vertex_check = False

        return neutral_check and target_check and file_check and muscle_patches_check and limit_check and vertex_check

    @cursor.wait_cursor_decorator_self
    def _execute_on_clicked(self):
        """Run the command when the run button is clicked.
        """
        if not self._check_on_run():
            return
        execute = True
        if self._draw_checkbox.isChecked():
            short_name = self._neutral_mesh.split("|")[-1] or self._neutral_mesh
            execute = msg_box(self._parent, "question", ("The draw muscle patches option is checked. "
                                                         "Drawing the muscle patches will replace the " 
                                                         "currently assigned material to \"{}\" with a "
                                                         "default lambert material.\n"
                                                         "Do you want to continue?").format(short_name))
        if execute:
            limit = int(self._limit_text_edit.text()) if self._limit_checkbox.isChecked() else 0
            self._dcc_tool.learn_muscle_patches(self._destination_file,
                                                self._neutral_mesh,
                                                self._target_meshes,
                                                self._vertices_mask,
                                                int(self._num_muscle_patches_text_edit.text()),
                                                self._draw_checkbox.isChecked(),
                                                limit)
