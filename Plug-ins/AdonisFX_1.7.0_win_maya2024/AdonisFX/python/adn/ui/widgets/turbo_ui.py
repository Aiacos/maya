try:
    from PySide6 import QtCore, QtWidgets
    from PySide6.QtGui import QRegularExpressionValidator
    from PySide6.QtCore import QRegularExpression
except ImportError:
    from PySide2 import QtCore, QtWidgets
    from PySide2.QtGui import QRegExpValidator as QRegularExpressionValidator
    from PySide2.QtCore import QRegExp as QRegularExpression

from adn.ui.widgets.base import BaseWidget
from adn.ui.widgets.dialogs import msg_box, display_report_data
from adn.utils.constants import TurboFeatures


class TurboUIErrorCode:
    """Class to define the error codes used in the TurboUI class.
    The error codes are used to identify the type of error that occurred in the UI."""
    kNone = 0           # The input is valid
    kWrongInput = 1     # The input does not satisfy its requirements
    kDuplicated = 2     # The input contains a geo that is used by another layer
    kWrongTopology = 3  # The fat geometry is not topologically identical to the fascia geometry


class TurboUI(BaseWidget):
    """User interface of the AdnTurbo tool to configure the inputs required to
    execute the process. The UI allows to set the geometries to be used for the
    simulation layers (i.e. mummy, muscles, fascia, fat and skin)
    as well as the space scale value.

    Args:
        dcc_tool (module): Tool that will be launching the AdnTurbo command.
        dcc_scene_commands (module): Module that will be used to interact with the scene.
        parent (:obj:`BaseWidget`): Parent class of the current UI class.
        *args: Argument list.
        **kwargs: Keyword argument list.
    """
    def __init__(self, dcc_tool, dcc_scene_commands, parent, *args, **kwargs):
        super(TurboUI, self).__init__("AdnTurbo", parent)
        self._parent = parent
        self._dcc_tool = dcc_tool
        self._dcc_scene_commands = dcc_scene_commands

        self._label_min_width = 75

        # Set the overall UI minimum width
        self.setMinimumWidth(400)

        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        """Builds the UI of the window based the following UI groups:
        - Global settings group: contains the mummy and space scale inputs.
        - Muscle layer group: contains the muscle input.
        - Locators layer group: contains the locators input and the option to create it if it does not exist.
        - Glue layer group: contains the glue input and the option to create it if it does not exist.
        - Fascia layer group: contains the fascia input.
        - Fat layer group: contains the fat input.
        - Skin layer group: contains the skin input.
        - Apply & Cancel buttons: centered in the bottom of the window.
        """
        layout = self._main_layout

        self._tooltips = {
            TurboFeatures.MUMMY:       "Skeletal mesh that will drive the muscle simulation layer. "
                                       "Provide the mesh or the group containing the mesh.",
            TurboFeatures.MUSCLES:     "Muscle meshes to which an AdnMuscle deformer will be applied. "
                                       "Provide the list of meshes or the group containing the meshes.",
            TurboFeatures.LOCATORS:    "Group in which locators and rivets will be created. ",
            TurboFeatures.GLUE:        "Group in which the AdnGlue mesh will be created.",
            TurboFeatures.FASCIA:      "Fascia mesh to which an AdnSkin deformer will be applied. "
                                       "Provide the mesh or the group containing the mesh.",
            TurboFeatures.FAT:         "Fat mesh to which an AdnFat deformer will be applied. "
                                       "Provide the mesh or the group containing the mesh.",
            TurboFeatures.SKIN:        "Skin mesh to which an AdnSkin deformer will be applied. "
                                       "Provide the mesh or the group containing the mesh.",
            TurboFeatures.SPACE_SCALE: "Space scale factor applied to all the deformers created.",
        }

        # Global settings group
        global_settings_group, mummy_line_edit, self._mummy_select_button, self._space_scale_spinbox = \
            self._create_global_settings_group()
        layout.addWidget(global_settings_group)

        # Muscle layer group
        (
            muscle_layer_group,
            muscle_line_edit,
            self._muscle_select_button
        ) = self._create_checkable_layer_group(
            title="Muscle Layer",
            label_text=TurboFeatures.MUSCLES,
            line_edit_attr="muscle_line_edit",
            button_text="Select"
        )
        layout.addWidget(muscle_layer_group)

        # Locators group
        (
            locators_layer_group,
            group_locators_checkbox,
            create_if_not_exist_locators_checkbox,
            self._locators_group_label,
            locators_group_line_edit,
            self._locators_group_select_button
        ) = self._create_grouping_group(
            feature=TurboFeatures.LOCATORS,
            title="Locators && Sensors"
        )
        layout.addWidget(locators_layer_group)

        # Glue layer group
        (
            glue_layer_group,
            group_glue_checkbox,
            create_if_not_exist_glue_checkbox,
            self._glue_group_label,
            glue_group_line_edit,
            self._glue_group_select_button
        ) = self._create_grouping_group(
            feature=TurboFeatures.GLUE,
            title="Glue Layer"
        )
        layout.addWidget(glue_layer_group)

        # Fascia layer group
        (
            fascia_layer_group,
            fascia_line_edit,
            self._fascia_select_button
        ) = self._create_checkable_layer_group(
            title="Fascia Layer",
            label_text=TurboFeatures.FASCIA,
            line_edit_attr="fascia_line_edit",
            button_text="Select"
        )
        layout.addWidget(fascia_layer_group)

        # Fat layer group
        (
            fat_layer_group,
            fat_line_edit,
            self._fat_select_button
        ) = self._create_checkable_layer_group(
            title="Fat Layer",
            label_text=TurboFeatures.FAT,
            line_edit_attr="fat_line_edit",
            button_text="Select"
        )
        layout.addWidget(fat_layer_group)

        # Skin layer group
        (
            skin_layer_group,
            skin_line_edit,
            self._skin_select_button
        ) = self._create_checkable_layer_group(
            title="Skin Layer",
            label_text=TurboFeatures.SKIN,
            line_edit_attr="skin_line_edit",
            button_text="Select"
        )
        layout.addWidget(skin_layer_group)

        # Apply & Cancel buttons centered
        button_row = QtWidgets.QHBoxLayout()
        self._apply_button = QtWidgets.QPushButton("Apply Turbo")
        self._cancel_button = QtWidgets.QPushButton("Cancel")
        self._apply_button.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Preferred
        )
        self._cancel_button.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Preferred
        )
        button_row.addWidget(self._apply_button, 1)
        button_row.addWidget(self._cancel_button, 1)
        layout.addLayout(button_row)

        self._line_edits = {
            TurboFeatures.MUMMY: mummy_line_edit,
            TurboFeatures.MUSCLES: muscle_line_edit,
            TurboFeatures.LOCATORS: locators_group_line_edit,
            TurboFeatures.GLUE: glue_group_line_edit,
            TurboFeatures.FASCIA: fascia_line_edit,
            TurboFeatures.FAT: fat_line_edit,
            TurboFeatures.SKIN: skin_line_edit
        }

        # Map to store if the input is valid or not and the latest error message.
        # This is used to keep track of the inputs to be able to restore the style
        # of the line edit. For example, if the fascia input is invalid we will
        # modify the style of the line edit to show the error, but if the fascia
        # group is disabled we will restore the line edit style to the default one.
        self._valid_input = {
            TurboFeatures.MUMMY: [True, "", TurboUIErrorCode.kNone],
            TurboFeatures.MUSCLES: [True, "", TurboUIErrorCode.kNone],
            TurboFeatures.LOCATORS: [True, "", TurboUIErrorCode.kNone],
            TurboFeatures.GLUE: [True, "", TurboUIErrorCode.kNone],
            TurboFeatures.FASCIA: [True, "", TurboUIErrorCode.kNone],
            TurboFeatures.FAT: [True, "", TurboUIErrorCode.kNone],
            TurboFeatures.SKIN: [True, "", TurboUIErrorCode.kNone]
        }

        self._groups = {
            TurboFeatures.MUMMY: global_settings_group,
            TurboFeatures.MUSCLES: muscle_layer_group,
            TurboFeatures.LOCATORS: locators_layer_group,
            TurboFeatures.GLUE: glue_layer_group,
            TurboFeatures.FASCIA: fascia_layer_group,
            TurboFeatures.FAT: fat_layer_group,
            TurboFeatures.SKIN: skin_layer_group
        }

        self._create_if_not_exist_checkbox = {
            TurboFeatures.GLUE: create_if_not_exist_glue_checkbox,
            TurboFeatures.LOCATORS: create_if_not_exist_locators_checkbox
        }

        self._group_checkbox = {
            TurboFeatures.GLUE: group_glue_checkbox,
            TurboFeatures.LOCATORS: group_locators_checkbox
        }

        self._group_features = [TurboFeatures.GLUE, TurboFeatures.LOCATORS]

        # Validate the inputs at the beginning to set the style of the line edits
        # as "error" because they are empty by default.
        self._validate_selection(TurboFeatures.MUMMY)
        self._validate_selection(TurboFeatures.MUSCLES)
        self._validate_selection(TurboFeatures.LOCATORS)
        self._validate_selection(TurboFeatures.GLUE)
        self._validate_selection(TurboFeatures.FASCIA)
        self._validate_selection(TurboFeatures.FAT)
        self._validate_selection(TurboFeatures.SKIN)

    def _connect_signals(self):
        """Connects the signals to the UI components.

        It connects the signals enable/disable the dependent layers in the cascade
        and to validate the inputs.

        It also connects the select buttons to the handlers to select the objects
        in the scene and set the line edit text to the selected objects.
        """
        # Enable/disable dependent layers in cascade
        self._groups[TurboFeatures.MUSCLES].toggled.connect(
            lambda state: self._propagate_enabled(state, [
                TurboFeatures.MUSCLES,
                TurboFeatures.LOCATORS,
                TurboFeatures.GLUE,
                TurboFeatures.FASCIA,
                TurboFeatures.FAT,
                TurboFeatures.SKIN
            ])
        )
        self._groups[TurboFeatures.LOCATORS].toggled.connect(
            lambda state: self._propagate_enabled(state, [
                TurboFeatures.LOCATORS
            ])
        )
        self._groups[TurboFeatures.GLUE].toggled.connect(
            lambda state: self._propagate_enabled(state, [
                TurboFeatures.GLUE,
                TurboFeatures.FASCIA,
                TurboFeatures.FAT,
                TurboFeatures.SKIN
            ])
        )
        self._groups[TurboFeatures.FASCIA].toggled.connect(
            lambda state: self._propagate_enabled(state, [
                TurboFeatures.FASCIA,
                TurboFeatures.FAT,
                TurboFeatures.SKIN
            ])
        )
        self._groups[TurboFeatures.FAT].toggled.connect(
            lambda state: self._propagate_enabled(state, [
                TurboFeatures.FAT,
                TurboFeatures.SKIN
            ])
        )
        self._groups[TurboFeatures.SKIN].toggled.connect(
            lambda state: self._propagate_enabled(state, [
                TurboFeatures.SKIN
            ])
        )

        # Glue layer interactions
        self._group_checkbox[TurboFeatures.GLUE].toggled.connect(self._create_if_not_exist_checkbox[TurboFeatures.GLUE].setEnabled)
        self._group_checkbox[TurboFeatures.GLUE].toggled.connect(self._glue_group_label.setEnabled)
        self._group_checkbox[TurboFeatures.GLUE].toggled.connect(self._line_edits[TurboFeatures.GLUE].setEnabled)
        self._group_checkbox[TurboFeatures.GLUE].toggled.connect(self._glue_group_select_button.setEnabled)
        self._group_checkbox[TurboFeatures.GLUE].toggled.connect(lambda: self._evaluate_grouping_group_state(TurboFeatures.GLUE))
        self._create_if_not_exist_checkbox[TurboFeatures.GLUE].toggled.connect(lambda: self._evaluate_grouping_group_state(TurboFeatures.GLUE))

        # Locators layer interactions
        self._group_checkbox[TurboFeatures.LOCATORS].toggled.connect(self._create_if_not_exist_checkbox[TurboFeatures.LOCATORS].setEnabled)
        self._group_checkbox[TurboFeatures.LOCATORS].toggled.connect(self._locators_group_label.setEnabled)
        self._group_checkbox[TurboFeatures.LOCATORS].toggled.connect(self._line_edits[TurboFeatures.LOCATORS].setEnabled)
        self._group_checkbox[TurboFeatures.LOCATORS].toggled.connect(self._locators_group_select_button.setEnabled)
        self._group_checkbox[TurboFeatures.LOCATORS].toggled.connect(lambda: self._evaluate_grouping_group_state(TurboFeatures.LOCATORS))
        self._create_if_not_exist_checkbox[TurboFeatures.LOCATORS].toggled.connect(lambda: self._evaluate_grouping_group_state(TurboFeatures.LOCATORS))

        # Connect select buttons to handlers
        self._mummy_select_button.clicked.connect(lambda: self._select_scene_objects(self._line_edits[TurboFeatures.MUMMY]))
        self._muscle_select_button.clicked.connect(lambda: self._select_scene_objects(self._line_edits[TurboFeatures.MUSCLES]))
        self._locators_group_select_button.clicked.connect(lambda: self._select_scene_objects(self._line_edits[TurboFeatures.LOCATORS]))
        self._glue_group_select_button.clicked.connect(lambda: self._select_scene_objects(self._line_edits[TurboFeatures.GLUE]))
        self._fascia_select_button.clicked.connect(lambda: self._select_scene_objects(self._line_edits[TurboFeatures.FASCIA]))
        self._fat_select_button.clicked.connect(lambda: self._select_scene_objects(self._line_edits[TurboFeatures.FAT]))
        self._skin_select_button.clicked.connect(lambda: self._select_scene_objects(self._line_edits[TurboFeatures.SKIN]))

        self._line_edits[TurboFeatures.MUMMY].textChanged.connect(lambda: self._validate_selection(TurboFeatures.MUMMY))
        self._line_edits[TurboFeatures.MUSCLES].textChanged.connect(lambda: self._validate_selection(TurboFeatures.MUSCLES))
        self._line_edits[TurboFeatures.LOCATORS].textChanged.connect(lambda: self._validate_selection(TurboFeatures.LOCATORS))
        self._line_edits[TurboFeatures.GLUE].textChanged.connect(lambda: self._validate_selection(TurboFeatures.GLUE))
        self._line_edits[TurboFeatures.FASCIA].textChanged.connect(lambda: self._validate_selection(TurboFeatures.FASCIA))
        self._line_edits[TurboFeatures.FAT].textChanged.connect(lambda: self._validate_selection(TurboFeatures.FAT))
        self._line_edits[TurboFeatures.SKIN].textChanged.connect(lambda: self._validate_selection(TurboFeatures.SKIN))

        self._line_edits[TurboFeatures.FAT].textChanged.connect(self._validate_fat_and_fascia_topology)
        self._line_edits[TurboFeatures.FASCIA].textChanged.connect(self._validate_fat_and_fascia_topology)

        self._line_edits[TurboFeatures.MUMMY].textChanged.connect(self._validate_selection_duplicates)
        self._line_edits[TurboFeatures.MUSCLES].textChanged.connect(self._validate_selection_duplicates)
        self._line_edits[TurboFeatures.FASCIA].textChanged.connect(self._validate_selection_duplicates)
        self._line_edits[TurboFeatures.FAT].textChanged.connect(self._validate_selection_duplicates)
        self._line_edits[TurboFeatures.SKIN].textChanged.connect(self._validate_selection_duplicates)

        # Connect main buttons
        self._apply_button.clicked.connect(self._apply)
        self._cancel_button.clicked.connect(self.close)

    def _create_global_settings_group(self):
        """Creates the global settings group containing the mummy and space scale inputs.

        Returns:
            tuple: Group box, mummy line edit, mummy select button and space scale spinbox.
        """
        group_box = QtWidgets.QGroupBox("Global settings")
        form_layout = QtWidgets.QFormLayout(group_box)
        form_layout.setLabelAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        # Mummy selection row
        mummy_label = QtWidgets.QLabel(TurboFeatures.MUMMY)
        mummy_label.setMinimumWidth(self._label_min_width)
        mummy_label.setToolTip(self._tooltips[TurboFeatures.MUMMY])
        mummy_line_edit = QtWidgets.QLineEdit()
        mummy_select_button = QtWidgets.QPushButton("Select")
        mummy_container = QtWidgets.QWidget()
        mummy_layout = QtWidgets.QHBoxLayout(mummy_container)
        mummy_layout.setContentsMargins(0, 0, 0, 0)
        mummy_layout.addWidget(mummy_line_edit)
        mummy_layout.addWidget(mummy_select_button)
        form_layout.addRow(mummy_label, mummy_container)

        # Space scale numeric input
        scale_label = QtWidgets.QLabel("Space Scale")
        scale_label.setMinimumWidth(self._label_min_width)
        scale_label.setToolTip(self._tooltips[TurboFeatures.SPACE_SCALE])
        space_scale_spinbox = QtWidgets.QDoubleSpinBox()
        space_scale_spinbox.setRange(0.001, 1000.0)
        space_scale_spinbox.setDecimals(3)
        space_scale_spinbox.setValue(1.0)
        form_layout.addRow(scale_label, space_scale_spinbox)

        return (group_box, mummy_line_edit, mummy_select_button, space_scale_spinbox)

    def _create_checkable_layer_group(self, title, label_text, line_edit_attr, button_text):
        """Creates a checkable group box with a label, a line edit and a select button.

        Args:
            title (str): Title of the group box.
            label_text (str): Text of the label.
            line_edit_attr (str): Name of the line edit attribute to be set.
            button_text (str): Text of the select button.

        Returns:
            tuple: Group box, line edit and select button.
        """
        group_box = QtWidgets.QGroupBox(title)
        group_box.setCheckable(True)
        group_box.setChecked(True)

        form_layout = QtWidgets.QFormLayout(group_box)
        form_layout.setLabelAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        # Layer row: label + input + select button
        layer_label = QtWidgets.QLabel(label_text)
        layer_label.setMinimumWidth(self._label_min_width)
        layer_label.setToolTip(self._tooltips[label_text])
        line_edit = QtWidgets.QLineEdit()
        setattr(self, line_edit_attr, line_edit)
        select_button = QtWidgets.QPushButton(button_text)
        row_container = QtWidgets.QWidget()
        row_layout = QtWidgets.QHBoxLayout(row_container)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.addWidget(line_edit)
        row_layout.addWidget(select_button)
        form_layout.addRow(layer_label, row_container)

        return (group_box, line_edit, select_button)

    def _create_grouping_group(self, feature, title):
        """Creates the grouping group containing the group input and two checkboxes for
        toggling the grouping and create if not exist.

        Args:
            feature (str): Feature to get the tooltip from the dictionary.
            title (str): Title of the group box.

        Returns:
            tuple: Group box, group checkbox, create if not exist checkbox,
                group label, group line edit and group select button.
        """
        group_box = QtWidgets.QGroupBox(title)
        group_box.setCheckable(True)
        group_box.setChecked(True)

        form_layout = QtWidgets.QFormLayout(group_box)
        form_layout.setLabelAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        # Option checkboxes row
        group_checkbox = QtWidgets.QCheckBox("Group")
        create_if_not_exist_checkbox = QtWidgets.QCheckBox("Create if not exist")
        create_if_not_exist_checkbox.setEnabled(False)
        create_if_not_exist_checkbox.setChecked(True)
        options_container = QtWidgets.QWidget()
        options_layout = QtWidgets.QHBoxLayout(options_container)
        options_layout.setContentsMargins(0, 0, 0, 0)
        options_layout.addWidget(group_checkbox)
        options_layout.addStretch()
        options_layout.addWidget(create_if_not_exist_checkbox)
        empty_label = QtWidgets.QLabel("")
        empty_label.setMinimumWidth(self._label_min_width)
        form_layout.addRow(empty_label, options_container)

        # Group input row
        group_label = QtWidgets.QLabel("Group Name")
        group_label.setMinimumWidth(self._label_min_width)
        group_label.setEnabled(False)
        group_label.setToolTip(self._tooltips[feature])
        group_line_edit = QtWidgets.QLineEdit()
        regex = QRegularExpression(self._dcc_tool.OBJECT_PATH_DCC_REGEX)
        validator = QRegularExpressionValidator(regex, self)
        group_line_edit.setValidator(validator)
        group_line_edit.setEnabled(False)
        group_select_button = QtWidgets.QPushButton("Select")
        group_select_button.setEnabled(False)
        input_container = QtWidgets.QWidget()
        input_layout = QtWidgets.QHBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.addWidget(group_line_edit)
        input_layout.addWidget(group_select_button)
        form_layout.addRow(group_label, input_container)

        return (group_box,
                group_checkbox,
                create_if_not_exist_checkbox,
                group_label,
                group_line_edit,
                group_select_button)

    def _propagate_enabled(self, state, turbo_features):
        """Enables/disables the groups of the turbo features in cascade.

        The first group is the one that is being toggled and the rest are the ones
        that are enabled/disabled based on the state of the first group.

        It also handles the style of the line edits to show if the input is valid or not
        for all the groups passed as argument.

        If it is called only for one group, it will only handle the style of the line edit
        of that group.

        At the end it evaluates if the apply button should be enabled or not based on the
        state of the groups and the validity of the inputs.

        Args:
            state (bool): State of the group that is being toggled.
            turbo_features (list): List of turbo features associated to the groups to
                be enabled/disabled.
        """
        if not turbo_features:
            return

        # For the self layer (i.e. layer that triggered the function) we only handle the
        # style of the line edit
        turbo_feature = turbo_features[0]
        enable = state
        # For the glue layer we need to take into account also the group glue checkbox
        # and the create if not exist checkbox
        if turbo_feature in self._group_features and enable:
            enable = enable and self._group_checkbox[turbo_feature].isChecked()
            if self._create_if_not_exist_checkbox[turbo_feature].isChecked():
                text = self._line_edits[turbo_feature].text()
                enable = enable and (text == "" or len(text.split(",")) > 1)

        if not enable:
            self._restore_line_edit(self._line_edits[turbo_feature])
        else:
            if not self._valid_input[turbo_feature][0]:
                self._error_line_edit(self._line_edits[turbo_feature],
                                      self._valid_input[turbo_feature][1])
        # For the rest of the layers we handle the style of the line edit
        # and enable/disable the group
        enable = state
        for turbo_feature in turbo_features[1:]:
            group = self._groups[turbo_feature]
            group.setEnabled(enable)

            tmp_enable = enable
            enable = enable and group.isChecked()
            final_enable = enable
            # For the glue layer we need to take into account also the group glue checkbox
            # and the create if not exist checkbox
            if turbo_feature in self._group_features and final_enable:
                final_enable = final_enable and self._group_checkbox[turbo_feature].isChecked()
                if self._create_if_not_exist_checkbox[turbo_feature].isChecked():
                    text = self._line_edits[turbo_feature].text()
                    final_enable = final_enable and (text == "" or len(text.split(",")) > 1)
            if not final_enable:
                self._restore_line_edit(self._line_edits[turbo_feature])
            else:
                if not self._valid_input[turbo_feature][0]:
                    self._error_line_edit(self._line_edits[turbo_feature],
                                          self._valid_input[turbo_feature][1])

            # The locators group checkbox state is not propagated as
            # it must not affect the next layer groups. That is why we
            # revert the effect of the line `enable = enable and group.isChecked()`
            # for the following iterations
            if turbo_feature == TurboFeatures.LOCATORS:
                enable = tmp_enable

        # Evaluate the apply button state
        self._evaluate_disable_apply()

    def _select_scene_objects(self, line_edit):
        """Selects the objects in the scene and sets the line edit text to the
        selected objects.

        Args:
            line_edit (:obj:`QLineEdit`): Line edit widget to set the selected objects.
        """
        if not line_edit:
            return

        selection = self._dcc_scene_commands.get_selection()
        if selection:
            line_edit.setText(", ".join(selection))
        else:
            line_edit.setText("")

    def _validate_selection(self, turbo_feature):
        """Validates the selection of the line edit and sets the error message if needed.

        Before returning it evaluates if the apply button should be enabled or not based on the
        state of the groups and the validity of the inputs.

        Args:
            turbo_feature (str): Turbo feature to be validated.
        """
        if turbo_feature not in self._line_edits:
            return
        line_edit = self._line_edits[turbo_feature]
        if not line_edit:
            return

        self._restore_line_edit(line_edit)

        text = line_edit.text()
        if text == "":
            msg = ("The {0} input for AdnTurbo must be provided.").format(turbo_feature)
            # For glue we don't want to show the error if the group glue checkbox is not checked
            if turbo_feature not in self._group_features or self._group_checkbox[turbo_feature].isChecked():
                self._error_line_edit(line_edit, msg)
            self._valid_input[turbo_feature][2] = TurboUIErrorCode.kWrongInput
            self._valid_input[turbo_feature][1] = msg
            self._valid_input[turbo_feature][0] = False
            self._evaluate_disable_apply()
            return

        if turbo_feature != TurboFeatures.MUSCLES:
            if len(text.split(",")) > 1:
                msg = ("The {0} input for AdnTurbo must be a single object.".format(turbo_feature))
                # For glue we don't want to show the error if the group glue checkbox is not checked
                if turbo_feature not in self._group_features or self._group_checkbox[turbo_feature].isChecked():
                    self._error_line_edit(line_edit, msg)
                self._valid_input[turbo_feature][2] = TurboUIErrorCode.kWrongInput
                self._valid_input[turbo_feature][1] = msg
                self._valid_input[turbo_feature][0] = False
                self._evaluate_disable_apply()
                return
            elif not self._dcc_scene_commands.exists(text):
                msg = ("The object \"{0}\" provided as {1} does not exist in the scene.".format(text, turbo_feature))
                # For glue we don't want to show the error if the group glue checkbox is not checked.
                # Additionally, in this case, we don't want to show the error if the create if not exist
                # checkbox is checked
                if turbo_feature not in self._group_features or (self._group_checkbox[turbo_feature].isChecked() \
                   and not self._create_if_not_exist_checkbox[turbo_feature].isChecked()):
                    self._error_line_edit(line_edit, msg)
                self._valid_input[turbo_feature][2] = TurboUIErrorCode.kWrongInput
                self._valid_input[turbo_feature][1] = msg
                self._valid_input[turbo_feature][0] = False
                self._evaluate_disable_apply()
                return
            elif turbo_feature not in self._group_features:
                mesh = self._dcc_scene_commands.get_mesh(text)
                if len(mesh) == 0:
                    msg = ("No valid mesh found in object \"{0}\" provided as {1}.".format(text, turbo_feature))
                    self._error_line_edit(line_edit, msg)
                    self._valid_input[turbo_feature][2] = TurboUIErrorCode.kWrongInput
                    self._valid_input[turbo_feature][1] = msg
                    self._valid_input[turbo_feature][0] = False
                    self._evaluate_disable_apply()
                    return
                elif len(mesh) > 1:
                    msg = ("More than one mesh found in object \"{0}\" provided as {1}. Only one mesh is allowed."
                           "").format(text, turbo_feature)
                    self._error_line_edit(line_edit, msg)
                    self._valid_input[turbo_feature][2] = TurboUIErrorCode.kWrongInput
                    self._valid_input[turbo_feature][1] = msg
                    self._valid_input[turbo_feature][0] = False
                    self._evaluate_disable_apply()
                    return
        else:
            muscles = text.split(",")
            no_exist_muscles = [m for m in muscles if not self._dcc_scene_commands.exists(m.strip())]
            if no_exist_muscles:
                msg = ("The following muscle(s) or group(s) do not exist in the scene: {0}"
                      "").format(", ".join('"{}"'.format(m) for m in no_exist_muscles))
                self._error_line_edit(line_edit, msg)
                self._valid_input[turbo_feature][2] = TurboUIErrorCode.kWrongInput
                self._valid_input[turbo_feature][1] = msg
                self._valid_input[turbo_feature][0] = False
                self._evaluate_disable_apply()
                return
            else:
                meshes = self._dcc_scene_commands.get_mesh(muscles)
                if len(meshes) == 0:
                    msg = ("No valid mesh found in the provided muscle(s) or group(s).")
                    self._error_line_edit(line_edit, msg)
                    self._valid_input[turbo_feature][2] = TurboUIErrorCode.kWrongInput
                    self._valid_input[turbo_feature][1] = msg
                    self._valid_input[turbo_feature][0] = False
                    self._evaluate_disable_apply()
                    return

        self._restore_line_edit(line_edit)
        self._valid_input[turbo_feature][2] = TurboUIErrorCode.kNone
        self._valid_input[turbo_feature][1] = ""
        self._valid_input[turbo_feature][0] = True
        self._evaluate_disable_apply()

    def _validate_fat_and_fascia_topology(self):
        """Validates the topology of the fat and fascia meshes. If the topology is not
        valid, it sets the error message and disables the apply button.
        """
        if self._valid_input[TurboFeatures.FAT][2] == TurboUIErrorCode.kWrongTopology:
            self._restore_line_edit(self._line_edits[TurboFeatures.FAT])
            self._valid_input[TurboFeatures.FAT][2] = TurboUIErrorCode.kNone
            self._valid_input[TurboFeatures.FAT][1] = ""
            self._valid_input[TurboFeatures.FAT][0] = True
        elif not self._valid_input[TurboFeatures.FAT][0]:
            # There is already another error more critical, we don't need to continue checking the topology
            return

        if not self._valid_input[TurboFeatures.FASCIA][0]:
            # There is already another error more critical, we don't need to continue checking the topology
            return

        # Get fascia mesh
        fascia_text = self._line_edits[TurboFeatures.FASCIA].text()
        fat_text = self._line_edits[TurboFeatures.FAT].text()
        if not fascia_text or not fat_text:
            return
        fascia_meshes = self._dcc_scene_commands.get_mesh(fascia_text)
        fat_meshes = self._dcc_scene_commands.get_mesh(fat_text)
        if not fascia_meshes or not fat_meshes:
            return
        fascia_num_verts = self._dcc_scene_commands.get_num_vertices(fascia_meshes[0])
        fat_num_verts = self._dcc_scene_commands.get_num_vertices(fat_meshes[0])
        if fascia_num_verts != fat_num_verts:
            msg = ("The fascia \"{0}\" and fat \"{1}\" geometries have mismatching vertex count. "
                "In order to create the fat solver it is required for the two geometries to "
                "be topologically identical (while different in shape)."
                "").format(fascia_text, fat_text)
            self._error_line_edit(self._line_edits[TurboFeatures.FAT], msg)
            self._valid_input[TurboFeatures.FAT][2] = TurboUIErrorCode.kWrongTopology
            self._valid_input[TurboFeatures.FAT][1] = msg
            self._valid_input[TurboFeatures.FAT][0] = False
            self._evaluate_disable_apply()
            return

        self._evaluate_disable_apply()

    def _validate_selection_duplicates(self):
        """Validates all the input texts to ensure that the same mesh is not assigned to more than
        one single layer.

        Before returning it evaluates if the apply button should be enabled or not based on the
        state of the groups and the validity of the inputs.
        """
        cross_dependency_list = [TurboFeatures.MUMMY, TurboFeatures.MUSCLES, TurboFeatures.FASCIA,
                                 TurboFeatures.FAT, TurboFeatures.SKIN]
        for i in range(len(cross_dependency_list)):
            turbo_feature = cross_dependency_list[i]
            line_edit = self._line_edits[turbo_feature]
            if not line_edit:
                continue

            # Clear existing error if it was kDuplicated as we are going to re-evaluate
            if self._valid_input[turbo_feature][2] == TurboUIErrorCode.kDuplicated:
                self._restore_line_edit(line_edit)
                self._valid_input[turbo_feature][2] = TurboUIErrorCode.kNone
                self._valid_input[turbo_feature][1] = ""
                self._valid_input[turbo_feature][0] = True
            elif not self._valid_input[turbo_feature][0]:
                # There is already another error more critical, we don't need to continue checking for duplicates
                continue

            text = line_edit.text()
            text_list = text.split(",")
            meshes = self._dcc_scene_commands.get_mesh(text_list)
            for j in range(len(cross_dependency_list)):
                if i == j:
                    continue
                other_feature = cross_dependency_list[j]
                if not self._valid_input[other_feature][0] and self._valid_input[other_feature][2] != TurboUIErrorCode.kDuplicated:
                    # There is already another error more critical, we don't need to continue checking for duplicates
                    continue
                other_line_edit = self._line_edits[other_feature]
                if not other_line_edit:
                    continue
                other_text = self._line_edits[other_feature].text()
                other_text_list = other_text.split(",")
                other_meshes = self._dcc_scene_commands.get_mesh(other_text_list)
                for m in meshes:
                    if m in other_meshes:
                        msg = ("The mesh {0} is provided twice in {1} and {2} which "
                              "is not allowed.").format(m, turbo_feature, other_feature)
                        self._error_line_edit(line_edit, msg)
                        self._valid_input[turbo_feature][2] = TurboUIErrorCode.kDuplicated
                        self._valid_input[turbo_feature][1] = msg
                        self._valid_input[turbo_feature][0] = False
                        # We update the other input as well only if it has no other error more critical
                        self._error_line_edit(other_line_edit, msg)
                        self._valid_input[other_feature][2] = TurboUIErrorCode.kDuplicated
                        self._valid_input[other_feature][1] = msg
                        self._valid_input[other_feature][0] = False
                        break

        self._evaluate_disable_apply()


    def _evaluate_grouping_group_state(self, turbo_feature):
        """Evaluates the style and error state of the group line edit based on the
        states of the group checkbox and the create if not exist checkbox.

        If the group checkbox is checked, the function checks the validity of the
        group input. When the create if not exist checkbox is unchecked, errors
        related to invalid or missing input are displayed. If the create if not exist
        checkbox is checked, some errors (e.g., empty input or multiple inputs) are
        still displayed, but others are suppressed to allow for group creation.

        Finally, the function evaluates whether the apply button should be enabled
        or disabled based on the current state of the inputs and checkboxes.
        """
        if turbo_feature not in self._group_features:
            return
        create_if_not_exist = self._create_if_not_exist_checkbox[turbo_feature].isChecked()

        self._restore_line_edit(self._line_edits[turbo_feature])

        if self._group_checkbox[turbo_feature].isChecked():
            if not self._valid_input[turbo_feature][0]:
                if not create_if_not_exist:
                    self._error_line_edit(self._line_edits[turbo_feature],
                                          self._valid_input[turbo_feature][1])
                else:
                    text = self._line_edits[turbo_feature].text()
                    if text == "" or len(text.split(",")) > 1:
                        self._error_line_edit(self._line_edits[turbo_feature],
                                              self._valid_input[turbo_feature][1])

        self._evaluate_disable_apply()

    def _evaluate_disable_apply(self):
        """Evaluates if the apply button should be enabled or not based on the
        state of the groups and the validity of the inputs.

        Example: If only the Fascia input is invalid, the apply button will be disabled.
        However, if the Fascia layer is disabled, we don't care about the validity of the
        input and the apply button will be enabled.
        """
        enable_apply = True
        # If the muscle layer is not checked, disable the apply button directly
        if not self._groups[TurboFeatures.MUSCLES].isChecked():
            enable_apply = False
        else:
            # Iterate the groups and skip them if they are not checked or not enabled
            for turbo_feature in self._groups:
                group = self._groups[turbo_feature]
                valid_input = self._valid_input[turbo_feature]
                # The group related to the mummy is always "enabled" and "checked",
                # however as we don't call setCheckable(True), it would return False
                # for isChecked() and isEnabled()
                if turbo_feature != TurboFeatures.MUMMY and (not group.isChecked() or not group.isEnabled()):
                    continue
                if turbo_feature in self._group_features:
                    # Skip the glue group when the group glue checkbox is not checked
                    if not self._group_checkbox[turbo_feature].isChecked():
                        continue
                    # Skip the glue group when the create if not exist checkbox is checked, the
                    # line edit is not empty and the text is a single object
                    if self._create_if_not_exist_checkbox[turbo_feature].isChecked():
                        text = self._line_edits[turbo_feature].text()
                        if text != "" and len(text.split(",")) == 1:
                            continue
                if not valid_input[0]:
                    enable_apply = False
                    break

        self._apply_button.setEnabled(enable_apply)

    def _restore_line_edit(self, line_edit):
        """Restores the line edit style to the default and removes the tooltip.

        Args:
            line_edit (:obj:`QLineEdit`): Line edit widget to restore the style.
        """
        line_edit.setStyleSheet("")
        line_edit.setToolTip("")

    def _error_line_edit(self, line_edit, error_msg):
        """Modifies the border style of the line edit to show an error and sets the tooltip.

        Args:
            line_edit (:obj:`QLineEdit`): Line edit widget to set the error message.
        """
        line_edit.setStyleSheet("QLineEdit {border: 2px solid #ff3535; border-radius: 2.5px}")
        line_edit.setToolTip(error_msg)

    def _apply(self):
        """Collects settings from the widgets and call the method to execute
        the AdnTurbo process.
        """
        # Space scale is always available
        space_scale = self._space_scale_spinbox.value()
        # Mummy is always enabled
        mummy = self._line_edits[TurboFeatures.MUMMY].text()

        muscles = None
        locators = False
        locators_group = None
        create_locators_if_not_exist = False
        glue = False
        glue_group = None
        create_glue_if_not_exist = False
        fascia = None
        fat = None
        skin = None

        # Layers: only if the group is both enabled and checked
        if self._groups[TurboFeatures.MUSCLES].isEnabled() and self._groups[TurboFeatures.MUSCLES].isChecked():
            muscles = self._line_edits[TurboFeatures.MUSCLES].text()
            if muscles and "," in muscles:
                muscles = [m.strip() for m in muscles.split(",")]

        if self._groups[TurboFeatures.LOCATORS].isEnabled() and self._groups[TurboFeatures.LOCATORS].isChecked():
            locators = True
            if self._group_checkbox[TurboFeatures.LOCATORS].isChecked():
                locators_group = self._line_edits[TurboFeatures.LOCATORS].text()
                if self._create_if_not_exist_checkbox[TurboFeatures.LOCATORS].isEnabled():
                    create_locators_if_not_exist = self._create_if_not_exist_checkbox[TurboFeatures.LOCATORS].isChecked()


        if self._groups[TurboFeatures.GLUE].isEnabled() and self._groups[TurboFeatures.GLUE].isChecked():
            glue = True
            if self._group_checkbox[TurboFeatures.GLUE].isChecked():
                glue_group = self._line_edits[TurboFeatures.GLUE].text()
                if self._create_if_not_exist_checkbox[TurboFeatures.GLUE].isEnabled():
                    create_glue_if_not_exist = self._create_if_not_exist_checkbox[TurboFeatures.GLUE].isChecked()

        if self._groups[TurboFeatures.FASCIA].isEnabled() and self._groups[TurboFeatures.FASCIA].isChecked():
            fascia = self._line_edits[TurboFeatures.FASCIA].text()

        if self._groups[TurboFeatures.FAT].isEnabled() and self._groups[TurboFeatures.FAT].isChecked():
            fat = self._line_edits[TurboFeatures.FAT].text()

        if self._groups[TurboFeatures.SKIN].isEnabled() and self._groups[TurboFeatures.SKIN].isChecked():
            skin = self._line_edits[TurboFeatures.SKIN].text()

        if bool(self._dcc_scene_commands.get_plugin_nodes_in_scene()):
            msg = ("AdonisFX nodes have been found in the scene. All the "
                   "AdonisFX nodes will be deleted before applying AdnTurbo. "
                   "Do you want to continue?")
            if not msg_box(self._parent, "question", msg,
                           title="Before AdnTurbo..."):
                return

        report_data = {"errors": [], "warnings": []}
        self._dcc_tool.apply_turbo(mummy, muscles, fascia=fascia, fat=fat, skin=skin, glue=glue,
                                   glue_group_name=glue_group, create_glue_group=create_glue_if_not_exist,
                                   locators=locators, locators_group_name=locators_group,
                                   create_locators_group=create_locators_if_not_exist,
                                   space_scale=space_scale, report_data=report_data, force=True)

        msg = ("The AdnTurbo process completed with errors. Please check the "
               "detailed error list below for further information.")
        title = "AdnTurbo Errors"
        display_report_data(report_data, msg, title)
