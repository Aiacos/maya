import os
import logging

try:
    from PySide6 import QtWidgets, QtGui
except ImportError:
    from PySide2 import QtWidgets, QtGui

from adn.ui.widgets.base import BaseWidget
from adn.ui.widgets.dialogs import main_window
from adn.ui.widgets.dialogs import msg_box
from adn.utils.maya.constants import IOFeaturesData


class InputOutputUI(BaseWidget):
    """Base widget from which the import and export user interfaces will be inherited.

    Args:
        dcc_tool (module): Tool that will be launching the command associated to the UI.
        dcc_scene_commands (module): Commands that will invoke scene functions.
        parent (:obj:`BaseWidget`): Parent class of the current UI class.
        title (str): Name of the window.
        *args: Argument list.
        **kwargs: Keyword argument list.
    """
    def __init__(self, title, dcc_tool, dcc_scene_commands, parent, *args, **kwargs):
        title = "InputOutputUI" if not title else title
        super(InputOutputUI, self).__init__(title, parent, width=400, height=300)

        self._parent = parent

        self._dcc_tool = dcc_tool
        self._dcc_scene_commands = dcc_scene_commands

        self._adonis_env = os.getenv("ADONISFX_RESOURCES", "")

        self._build_ui()
        self._connect_signals()

    def _connect_signals(self):
        """Connects the signals of the UI."""
        self._accept_button.clicked.connect(lambda: self._on_execute(close=True))
        self._exec_button.clicked.connect(self._on_execute)
        self._close_button.clicked.connect(self.close)
        self._file_button.clicked.connect(self._browse_dialog)

    def _build_ui(self):
        """Builds the widget UI."""
        # File Path Input
        self._file_layout = QtWidgets.QHBoxLayout()
        self._file_input = QtWidgets.QLineEdit(self)
        self._file_icon_path = "{0}/adn_file.png".format(self._adonis_env)
        self._file_icon = QtGui.QIcon(self._file_icon_path)
        self._file_button = QtWidgets.QPushButton()
        self._file_button.setIcon(self._file_icon)
        self._file_layout.addWidget(QtWidgets.QLabel("Filepath:"))
        self._file_layout.addWidget(self._file_input)
        self._file_layout.addWidget(self._file_button)
        self._main_layout.addLayout(self._file_layout)

        # Solvers Group
        self._solvers_group = self._create_group("Solvers",
                                                 ["Muscles", "Glue", "Fat", "Skin", "Simshape"],
                                                 [IOFeaturesData.MUSCLE, IOFeaturesData.GLUE,
                                                  IOFeaturesData.FAT, IOFeaturesData.SKIN,
                                                  IOFeaturesData.SIMSHAPE])
        self._main_layout.addWidget(self._solvers_group)

        # Deformers Group
        self._deformers_group = self._create_group("Deformers",
                                                   ["Skin Merge", "Relax"],
                                                   [IOFeaturesData.SKIN_MERGE,
                                                    IOFeaturesData.RELAX])
        self._main_layout.addWidget(self._deformers_group)

        # Utils Group
        self._utils_group = self._create_group("Utils",
                                               ["Sensors && Locators", "Activation", "Remap", "Edge Evaluator"],
                                               [IOFeaturesData.SENSOR,
                                                IOFeaturesData.ACTIVATION,
                                                IOFeaturesData.REMAP,
                                                IOFeaturesData.EDGE_EVALUATOR])
        self._main_layout.addWidget(self._utils_group)

        # Buttons Layout
        self._button_layout = QtWidgets.QHBoxLayout()
        self._accept_button = QtWidgets.QPushButton("Accept")
        self._exec_button = QtWidgets.QPushButton("Execute")
        self._close_button = QtWidgets.QPushButton("Close")
        
        self._button_layout.addWidget(self._accept_button)
        self._button_layout.addWidget(self._exec_button)
        self._button_layout.addWidget(self._close_button)

        self._main_layout.addLayout(self._button_layout)

        self.setLayout(self._main_layout)

    def _create_group(self, title, options_titles, options):
        """Creates a group of check boxes (`QGroupBox`) with the title and
        options specified as arguments.

        Args:
            title (str): Name of the group.
            options_titles (list): Titles of the check boxes in the group.
            options (list): Feature IDs of the check box in the group.

        Returns:
            group_box (:obj:`QtWidgets.QGroupBox`): Group of boxes created.
        """
        group_box = QtWidgets.QGroupBox(title)
        layout = QtWidgets.QVBoxLayout()
        if not options_titles or not options:
            return group_box
        if len(options_titles) != len(options):
            return group_box
        for option_title, option in zip(options_titles, options):
            checkbox = QtWidgets.QCheckBox(option_title)
            checkbox.setProperty("IOFeatureData", option)
            checkbox.setChecked(True)
            layout.addWidget(checkbox)
        group_box.setLayout(layout)
        return group_box

    def _on_execute(self, close=True):
        """Handles the execution process when a button is clicked."""
        raise NotImplementedError("This method should be overridden by subclasses")

    def _browse_dialog(self):
        """Opens a file dialog. This method will be overridden by subclasses."""
        raise NotImplementedError("This method should be overridden by subclasses")

    def _gather_enabled_features(self):
        """Gathers the enabled features from the checkboxes.

        Returns:
            enabled_features (dict): Dictionary with the enabled features.
        """
        enabled_features = {}
        for group in [self._solvers_group, self._deformers_group, self._utils_group]:
            for checkbox in group.findChildren(QtWidgets.QCheckBox):
                io_feature_data = checkbox.property("IOFeatureData")
                if not io_feature_data:
                    continue
                enabled_features[io_feature_data] = checkbox.isChecked()
        return enabled_features


class ExportUI(InputOutputUI):
    """Specialized widget from which to implement the UI for the exporter.

    Args:
        dcc_tool (module): Tool that will be launching the command associated to the UI.
        dcc_scene_commands (module): Commands that will invoke scene functions.
        parent (:obj:`BaseWidget`): Parent class of the current UI class.
        *args: Argument list.
        **kwargs: Keyword argument list.
    """
    def __init__(self, dcc_tool, dcc_scene_commands, parent, *args, **kwargs):
        super(ExportUI, self).__init__("Export", dcc_tool, dcc_scene_commands,
                                       parent, width=400, height=300)
        self._exec_button.setText("Export")

    def _on_execute(self, close=False):
        """Handles the export process when a button is clicked.

        This method collects the status of checkboxes to build the `enabled_features`
        dictionary, validates the file path, and calls the export function from the
        DCC tool. If the export is successful and the `close` parameter is True, it
        closes the UI.

        Args:
            close (bool, optional): If True, closes the UI after exporting. Defaults to False.
        """
        file_path = self._file_input.text()
        if not os.path.exists(os.path.dirname(file_path)):
            msg_box(main_window(), "error", "The directory provided does not exist.")
            return

        if not file_path.endswith(".json"):
            file_path = os.path.splitext(file_path)[0] + ".json"
            logging.warning("File extension overwritten to JSON. Resulting file path: {0}"
                            "".format(file_path))

        # Collect the status of checkboxes to build the enabled_features dictionary
        enabled_features = self._gather_enabled_features()

        if not self._dcc_tool.export_data(file_path, enabled_features):
            msg_box(main_window(), "error", "Failed to export the AdonisFX setup.")
            return

        if close:
            self.close()

    def _browse_dialog(self):
        """Opens a file dialog to select a path and provide the name of a file to be written."""
        file_name, _ = QtWidgets.QFileDialog.getSaveFileName(self,
                                                             caption="Select File",
                                                             filter="JSON Files (*.json)")
        if file_name:
            self._file_input.setText(file_name)


class ImportUI(InputOutputUI):
    """Specialized widget from which to implement the UI for the importer.

    Args:
        dcc_tool (module): Tool that will be launching the command associated to the UI.
        dcc_scene_commands (module): Commands that will invoke scene functions.
        parent (:obj:`BaseWidget`): Parent class of the current UI class.
        *args: Argument list.
        **kwargs: Keyword argument list.
    """
    def __init__(self, dcc_tool, dcc_scene_commands, parent, *args, **kwargs):
        super(ImportUI, self).__init__("Import", dcc_tool, dcc_scene_commands,
                                       parent, width=400, height=300)
        self._exec_button.setText("Import")

    def _on_execute(self, close=False):
        """Handles the import process when a button is clicked.

        This method collects the status of checkboxes to build the `enabled_features`
        dictionary, validates the file path, and calls the import function from the
        DCC tool. If the import is successful and the `close` parameter is True, it
        closes the UI.

        Args:
            close (bool, optional): If True, closes the UI after importing. Defaults to False.
        """
        file_path = self._file_input.text()
        if not os.path.exists(file_path):
            msg_box(main_window(), "error", "The file provided does not exist.")
            return

        if not file_path.endswith(".json"):
            msg_box(main_window(), "error", "The file provided is not a JSON file.")
            return

        # Collect the status of checkboxes to build the enabled_features dictionary
        enabled_features = self._gather_enabled_features()

        if not self._dcc_tool.import_data(file_path, enabled_features):
            msg_box(main_window(), "error", "Failed to import the AdonisFX setup.")
            return

        if close:
            self.close()

    def _browse_dialog(self):
        """Opens a file dialog to select a file to be read."""
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self,
                                                             caption="Select File",
                                                             filter="JSON Files (*.json)")
        if file_name:
            self._file_input.setText(file_name)
