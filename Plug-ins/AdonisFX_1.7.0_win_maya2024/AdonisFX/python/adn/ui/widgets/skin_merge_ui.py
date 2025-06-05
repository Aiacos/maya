try:
    from PySide6 import QtCore, QtWidgets, QtGui
except ImportError:
    from PySide2 import QtCore, QtWidgets, QtGui

from adn.ui.widgets.base import BaseWidget
from adn.ui.widgets.dialogs import msg_box, report_error
from adn.ui.maya.window import main_window
from adn.utils.constants import UiConstants
from adn.utils.checkers import is_identifier
from adn.utils.constants import DeformerTypes


class SkinMergeUI(BaseWidget):
    """UI class for the AdnSkinMerge creation and edition.
    This tool allows to create and configure an AdnSkinMerge deformer easily.
    The UI consists in 3 group boxes to enter the destination mesh, the list of animated
    meshes and the list of simulated meshes.
    At the bottom, another section is presented for settings customization.
    This tool works in two modes: create and edit. "Create mode" allows to select all elements for the
    deformer (all meshes, custom name and initialization time) and create the deformer.
    "Edit mode" will only display the simulated and animation meshes lists, allowing to modify the
    meshes that are merged into the destination mesh.

    Args:
        dcc_tool (module): Tool that will be launching the command associated to the UI.
        dcc_scene_commands (module): Commands that will invoke scene functions.
        parent (:obj:`BaseWidget`): Parent class of the current UI class.
        edit (bool, optional): Flag to launch the UI in create or edit mode. Defaults to False.
        deformer (string, optional): Deformer name, used only in edit mode. Defaults to None.
        *args: Argument list.
        **kwargs: Keyword argument list.
    """
    def __init__(self, dcc_tool, dcc_scene_commands, parent, edit=False, deformer=None, *args, **kwargs):
        title = "Create Skin Merge" if not edit else "Edit Skin Merge"
        super(SkinMergeUI, self).__init__(title,
                                          parent,
                                          width=500,
                                          height=600)
        self._parent = parent

        self._dcc_tool = dcc_tool
        self._dcc_scene_commands = dcc_scene_commands

        # Class private attributes
        self._edit = edit
        self._final_mesh = None
        self._sim_meshes = None
        self._anim_meshes = None
        self._final_ok = False
        self._sim_ok = False
        self._anim_ok = False
        self._valid_name = True
        self._deformer_name = deformer
        self._data = None
        if self._edit:
            self._data = self._dcc_tool.get_skin_merge_data(self._deformer_name)

        self._build_ui()

    def _build_ui(self):
        """Builds the UI for the skin merge creation and edition."""
        # General parameters
        self._button_width = 200
        self._button_height = 60

        # Specific parameters
        self._mesh_text_height = 80

        ###############################
        # BEGIN FINAL MESH SECTION
        ###############################
        # Final mesh component definition
        self._final_text_edit = QtWidgets.QLineEdit()
        self._final_text_edit.setReadOnly(True)
        self._final_text_edit.setPlaceholderText("Select a final mesh")
        self._final_text_edit.setToolTip("Select the base final mesh over which simulation "
                                         "and animation meshes will be merged.")

        self._add_final_button = QtWidgets.QPushButton("Add Selected")
        self._add_final_button.resize(QtCore.QSize(self._button_width, self._button_height))
        self._add_final_button.clicked.connect(self._final_on_clicked)

        self._clear_final_button = QtWidgets.QPushButton("Clear")
        self._clear_final_button.resize(QtCore.QSize(self._button_width, self._button_height))
        self._clear_final_button.clicked.connect(self._final_on_cleared)

        # Final mesh section layout
        self._final_top_horizontal_layout = QtWidgets.QHBoxLayout()
        self._final_top_horizontal_layout.addWidget(self._final_text_edit)

        self._final_bottom_horizontal_layout = QtWidgets.QHBoxLayout()
        self._final_bottom_horizontal_layout.addWidget(self._add_final_button)
        self._final_bottom_horizontal_layout.addWidget(self._clear_final_button)

        self._final_global_vertical_layout = QtWidgets.QVBoxLayout()
        self._final_global_vertical_layout.addLayout(self._final_top_horizontal_layout)
        self._final_global_vertical_layout.addLayout(self._final_bottom_horizontal_layout)

        self._final_group = QtWidgets.QGroupBox()
        self._final_group.setTitle("Final Mesh")
        self._final_group.setLayout(self._final_global_vertical_layout)
        self._final_group.setHidden(self._edit)

        self._main_layout.addWidget(self._final_group)

        ###############################
        # BEGIN ANIMATION MESHES
        ###############################
        # Animation meshes component definition
        self._anim_list = QtWidgets.QListWidget()
        self._anim_list.setMinimumHeight(self._mesh_text_height)
        self._anim_list.setToolTip("Select the animation meshes to merge.")
        if self._edit and self._data:
            self._anim_meshes = self._data["animList"]
            self._anim_ok = True if self._anim_meshes else False
            for anim in self._anim_meshes:
                self._anim_list.addItem(anim)

        self._add_anim_button = QtWidgets.QPushButton("Add Selected")
        self._add_anim_button.resize(QtCore.QSize(self._button_width, self._button_height))
        self._add_anim_button.clicked.connect(self._anims_on_clicked)

        self._remove_anim_button = QtWidgets.QPushButton("Remove Selected")
        self._remove_anim_button.resize(QtCore.QSize(self._button_width, self._button_height))
        self._remove_anim_button.clicked.connect(self._anims_on_removed)

        self._clear_anim_button = QtWidgets.QPushButton("Clear")
        self._clear_anim_button.resize(QtCore.QSize(self._button_width, self._button_height))
        self._clear_anim_button.clicked.connect(self._anims_on_cleared)

        # Animation meshes section layout
        self._anim_top_horizontal_layout = QtWidgets.QHBoxLayout()
        self._anim_top_horizontal_layout.addWidget(self._anim_list)

        self._anim_bottom_horizontal_layout = QtWidgets.QHBoxLayout()
        self._anim_bottom_horizontal_layout.addWidget(self._add_anim_button)
        self._anim_bottom_horizontal_layout.addWidget(self._remove_anim_button)
        self._anim_bottom_horizontal_layout.addWidget(self._clear_anim_button)

        self._anim_global_vertical_layout = QtWidgets.QVBoxLayout()
        self._anim_global_vertical_layout.addLayout(self._anim_top_horizontal_layout)
        self._anim_global_vertical_layout.addLayout(self._anim_bottom_horizontal_layout)

        self._anim_group = QtWidgets.QGroupBox()
        self._anim_group.setTitle("Animation Meshes")
        self._anim_group.setLayout(self._anim_global_vertical_layout)

        self._main_layout.addWidget(self._anim_group)

        ###############################
        # BEGIN SIMULATION MESHES
        ###############################
        # Simulation meshes component definition
        self._sim_list = QtWidgets.QListWidget()
        self._sim_list.setMinimumHeight(self._mesh_text_height)
        self._sim_list.setToolTip("Select the simulation meshes to merge.")
        if self._edit and self._data:
            self._sim_meshes = self._data["simList"]
            self._sim_ok = True if self._sim_meshes else False
            for sim in self._sim_meshes:
                self._sim_list.addItem(sim)

        self._add_sim_button = QtWidgets.QPushButton("Add Selected")
        self._add_sim_button.resize(QtCore.QSize(self._button_width, self._button_height))
        self._add_sim_button.clicked.connect(self._sims_on_clicked)

        self._remove_sim_button = QtWidgets.QPushButton("Remove Selected")
        self._remove_sim_button.resize(QtCore.QSize(self._button_width, self._button_height))
        self._remove_sim_button.clicked.connect(self._sims_on_removed)

        self._clear_sim_button = QtWidgets.QPushButton("Clear")
        self._clear_sim_button.resize(QtCore.QSize(self._button_width, self._button_height))
        self._clear_sim_button.clicked.connect(self._sims_on_cleared)

        # Simulation meshes section layout
        self._sim_top_horizontal_layout = QtWidgets.QHBoxLayout()
        self._sim_top_horizontal_layout.addWidget(self._sim_list)

        self._sim_bottom_horizontal_layout = QtWidgets.QHBoxLayout()
        self._sim_bottom_horizontal_layout.addWidget(self._add_sim_button)
        self._sim_bottom_horizontal_layout.addWidget(self._remove_sim_button)
        self._sim_bottom_horizontal_layout.addWidget(self._clear_sim_button)

        self._sim_global_vertical_layout = QtWidgets.QVBoxLayout()
        self._sim_global_vertical_layout.addLayout(self._sim_top_horizontal_layout)
        self._sim_global_vertical_layout.addLayout(self._sim_bottom_horizontal_layout)

        self._sim_group = QtWidgets.QGroupBox()
        self._sim_group.setTitle("Simulation Meshes")
        self._sim_group.setLayout(self._sim_global_vertical_layout)

        self._main_layout.addWidget(self._sim_group)

        ###############################
        # BEGIN SETTINGS SECTION
        ###############################
        self._name_text = QtWidgets.QLabel("Custom Name:")

        # Get next AdnSkinMerge default name
        default_name = self._dcc_scene_commands.get_available_name(DeformerTypes.SKIN_MERGE)
        self._name_input = QtWidgets.QLineEdit(self)
        self._name_input.setText(default_name)
        self._name_input.textEdited.connect(self._validate_name)
        # Red rounded border similar to focus border
        self._wrong_input_name_stylesheet = "border: 2px solid #ff3535; border-radius: 2.5px"

        current_time = self._dcc_scene_commands.get_current_time()
        self._start_time_text = QtWidgets.QLabel("Initialization Time:")

        self._start_time_spin = QtWidgets.QSpinBox()
        self._start_time_spin.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self._start_time_spin.setRange(-1e6, 1e6)
        self._start_time_spin.setValue(current_time)
        self._start_time_spin.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self._start_time_spin.setToolTip("Set the initialization time for the deformer.")

        self._settings_layout = QtWidgets.QGridLayout()
        self._settings_layout.addWidget(self._name_text, 1, 1)
        self._settings_layout.addWidget(self._name_input, 1, 2)
        self._settings_layout.addWidget(self._start_time_text, 2, 1)
        self._settings_layout.addWidget(self._start_time_spin, 2, 2)

        self._settings_group = QtWidgets.QGroupBox()
        self._settings_group.setTitle("Settings")
        self._settings_group.setLayout(self._settings_layout)
        self._settings_group.setHidden(self._edit)

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
        self._clear_all_button.resize(QtCore.QSize(self._button_width, self._button_height))
        self._clear_all_button.clicked.connect(self._clear_all_on_clicked)

        self._create_button = QtWidgets.QPushButton("Create")
        self._create_button.resize(QtCore.QSize(self._button_width, self._button_height))
        self._create_button.clicked.connect(self._create_on_clicked)
        self._create_button.setEnabled(False)

        self._edit_button = QtWidgets.QPushButton("Apply Changes")
        self._edit_button.resize(QtCore.QSize(self._button_width, self._button_height))
        self._edit_button.clicked.connect(self._edit_on_clicked)
        self._edit_button.setEnabled(False)
        self._edit_button.setHidden(True)

        self._edit_button.setHidden(not self._edit)
        self._create_button.setHidden(self._edit)

        # Run section layout
        self._create_horizontal_layout = QtWidgets.QHBoxLayout()
        self._create_horizontal_layout.addWidget(self._clear_all_button)
        self._create_horizontal_layout.addWidget(self._create_button)
        self._create_horizontal_layout.addWidget(self._edit_button)

        self._main_layout.addLayout(self._create_horizontal_layout)

        if self._edit:
            self._check_all_go()

    def _validate_name(self, custom_name):
        """Checks if the name provided is valid while editing the custom name.
        Will enable the creation button if the name is valid, will disable otherwise.

        Args:
            custom_name (str): Name that the user is providing.
        """
        if not custom_name or not is_identifier(custom_name):
            self._name_input.setStyleSheet(self._wrong_input_name_stylesheet)
            self._valid_name = False
            return

        self._valid_name = True
        self._name_input.setStyleSheet("")

    def _check_all_go(self):
        """Checks if all input values have been correctly added"""
        self._create_button.setEnabled(self._final_ok and self._anim_ok
                                       and self._sim_ok and self._valid_name)
        self._edit_button.setEnabled(self._anim_ok and self._sim_ok
                                     and self._valid_name)

    def _final_on_clicked(self):
        """Get the selected final mesh. Sanity checks are launched when the
        select button in a final mesh context is launched.
        """
        tmp_final_mesh = self._dcc_scene_commands.get_selection()

        # No final mesh is selected.
        if not tmp_final_mesh:
            msg_box(self._parent, "error", "No final mesh selected.")
            return
        final_mesh_name = tmp_final_mesh[0]

        # More than one geometry selected, so get the first one.
        if len(tmp_final_mesh) > 1:
            print(("{0} More than one geometry selected. "
                   "Selecting the first geometry: {1}.").format(UiConstants.LOG_PREFIX, final_mesh_name))

        # Check if the final mesh is not a mesh object.
        if not self._dcc_scene_commands.is_mesh(final_mesh_name):
            msg_box(self._parent, "error",
                    "Final mesh selected object {0} is not a mesh.".format(final_mesh_name))
            return

        self._final_on_cleared()

        self._final_mesh = final_mesh_name
        self._final_ok = True
        self._final_text_edit.setText(self._final_mesh)
        self._check_all_go()

    def _final_on_cleared(self):
        """Clear the flag, input text and value for the final mesh when
        the clear button is pressed.
        """
        self._final_mesh = None
        self._final_ok = False
        self._final_text_edit.setText("")
        self._check_all_go()

    def _anims_on_clicked(self):
        """Get the selected animation meshes. Sanity checks are launched when the
        select button in a animation meshes context is launched.
        """
        tmp_anim_meshes = self._dcc_scene_commands.get_selection()

        # No anim meshes selected.
        if not tmp_anim_meshes:
            msg_box(self._parent, "error", "No animation meshes selected.")
            return
        tmp_anim_meshes = [targ for targ in tmp_anim_meshes if self._dcc_scene_commands.is_mesh(targ)]

        # The anim selection does not contain a mesh object.
        if not tmp_anim_meshes:
            msg_box(self._parent, "error",
                    "The anim selection does not contain any mesh objects.")
            return
        
        self._anims_on_cleared()

        # Ignore non mesh objects for the anims.
        not_mesh_list = [targ for targ in tmp_anim_meshes if targ not in tmp_anim_meshes]
        if not_mesh_list:
            print("{0} Ignored animation meshes: {1}.".format(UiConstants.LOG_PREFIX, not_mesh_list))

        self._anim_meshes = tmp_anim_meshes
        if self._anim_meshes:
            print("{0} Using {1} animation meshes: {2}.".format(UiConstants.LOG_PREFIX,
                                                                len(self._anim_meshes),
                                                                self._anim_meshes))
        self._anim_ok = True
        for anim in self._anim_meshes:
            self._anim_list.addItem(anim)
        self._anim_list.sortItems()
        self._check_all_go()

    def _anims_on_removed(self):
        """Remove a single element from the animation meshes list when the
        clear button is pressed
        """
        selected = self._anim_list.currentItem()
        if not selected:
            return
        self._anim_list.takeItem(self._anim_list.currentRow())
        self._anim_meshes.remove(selected.text())
        if not self._anim_meshes:
            self._anim_ok = False
        self._check_all_go()

    def _anims_on_cleared(self):
        """Clear the flag, input text and value for the animation meshes when
        the clear button is pressed.
        """
        self._anim_meshes = None
        self._anim_ok = False
        self._anim_list.clear()
        self._check_all_go()

    def _sims_on_clicked(self):
        """Get the selected simulation meshes. Sanity checks are launched when the
        select button in a simulation meshes context is launched.
        """
        tmp_sim_meshes = self._dcc_scene_commands.get_selection()

        # No simulation meshes selected.
        if not tmp_sim_meshes:
            msg_box(self._parent, "error", "No simulation meshes selected.")
            return
        tmp_sim_meshes = [targ for targ in tmp_sim_meshes if self._dcc_scene_commands.is_mesh(targ)]

        # The simulation selection does not contain a mesh object.
        if not tmp_sim_meshes:
            msg_box(self._parent, "error",
                    "The simulation selection does not contain any mesh objects.")
            return
        
        self._sims_on_cleared()
        
        # Ignore non mesh objects for the sims.
        not_mesh_list = [targ for targ in tmp_sim_meshes if targ not in tmp_sim_meshes]
        if not_mesh_list:
            print("{0} Ignored simulation meshes: {1}.".format(UiConstants.LOG_PREFIX, not_mesh_list))

        self._sim_meshes = tmp_sim_meshes
        if self._sim_meshes:
            print("{0} Using {1} simulation meshes: {2}.".format(UiConstants.LOG_PREFIX,
                                                                 len(self._sim_meshes),
                                                                 self._sim_meshes))
        self._sim_ok = True
        for sim in self._sim_meshes:
            self._sim_list.addItem(sim)
        self._sim_list.sortItems()
        self._check_all_go()

    def _sims_on_removed(self):
        """Remove a single element from the simulation meshes list when the
        clear button is pressed
        """
        selected = self._sim_list.currentItem()
        if not selected:
            return
        self._sim_list.takeItem(self._sim_list.currentRow())
        self._sim_meshes.remove(selected.text())
        if not self._sim_meshes:
            self._sim_ok = False
        self._check_all_go()

    def _sims_on_cleared(self):
        """Clear the flag, input text and value for the simulation meshes when
        the clear button is pressed.
        """
        self._sim_meshes = None
        self._sim_ok = False
        self._sim_list.clear()
        self._check_all_go()

    def _clear_all_on_clicked(self):
        """Clears and resets all inputs.
        """
        self._final_on_cleared()
        self._anims_on_cleared()
        self._sims_on_cleared()

    def _check_on_run(self):
        """Check if data provided in the UI is valid and can be
        used to create the Skin Merge deformer.

        Returns:
            bool: returns the outcome of the check before the execution.
        """
        final_check = self._dcc_scene_commands.exists(self._final_mesh) if not self._edit else True
        if not final_check:
            msg_box(self._parent, "error", "Final mesh not found in the scene.")
            return False
        anim_check = all([self._dcc_scene_commands.exists(anim) for anim in self._anim_meshes])
        if not anim_check:
            msg_box(self._parent, "error", "Animation meshes not found in the scene.")
            return False
        sim_check = all([self._dcc_scene_commands.exists(sim) for sim in self._sim_meshes])
        if not sim_check:
            msg_box(self._parent, "error", "Simulation meshes not found in the scene.")
            return False

        return True

    def _create_on_clicked(self):
        """Run the command when the create button is clicked.
        """
        if not self._check_on_run():
            return

        response = True
        if any(mesh in self._sim_meshes for mesh in self._anim_meshes):
            response = self._proceed_with_duplicates_question()
        # Abort the creation if the user denied the question
        if not response:
            return
        created, result = self._dcc_tool.create_skin_merge(self._name_input.text(),
                                                           self._final_mesh,
                                                           self._anim_meshes,
                                                           self._sim_meshes,
                                                           self._start_time_spin.value(),
                                                           force=response)
        report_error(result, "creating an {0} deformer".format(DeformerTypes.SKIN_MERGE))
        if created:
            self.close()

    def _edit_on_clicked(self):
        """Run the command when the edit button is clicked.
        """
        if not self._check_on_run():
            return

        response = True
        if any(mesh in self._sim_meshes for mesh in self._anim_meshes):
            response = self._proceed_with_duplicates_question()
        # Abort the edition if the user denied the question
        if not response:
            return
        edit_applied, result = self._dcc_tool.edit_skin_merge(self._deformer_name,
                                                              self._anim_meshes,
                                                              self._sim_meshes,
                                                              force=response)
        report_error(result, "editing an {0} deformer".format(DeformerTypes.SKIN_MERGE))
        if edit_applied:
            self.close()

    def _proceed_with_duplicates_question(self):
        """Displays a dialog asking the user to decide whether to proceed with the creation/editing
        of AdnSkinMerge when one or more meshes are present in both, anim and sim meshes.
        """
        return msg_box(main_window(), "question",
                       "One or more meshes are included in both the animation and simulated meshes "
                       "selections. This may cause the AdnSkinMerge not to work as expected. "
                       "Do you want to proceed with these settings?.")

    def keyPressEvent(self, qKeyEvent):
        """Overload the keyPressEvent to trigger the creation or the edit
        methods if the user press Enter."""
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if (qKeyEvent.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter) and
                modifiers == QtCore.Qt.NoModifier):
            if self._edit:
                self._edit_on_clicked()
            else:
                self._create_on_clicked()
        else:
            super(SkinMergeUI, self).keyPressEvent(qKeyEvent)
