import os

from PySide2 import QtCore, QtGui, QtWidgets

from adn.ui.widgets.base import BaseWidget
from adn.ui.widgets.dialogs import msg_box
from adn.ui.utils import cursor
from adn.utils.constants import AssetDefinition


class AssetDefinitionExporterUi(BaseWidget):
    """User interface of AdonisFX Asset Definition exporter.
    This widget allows the user to export a json file with the configuration
    of AdonisFX nodes in the scene. It allows to determine which features
    and attributes will be exported and also the full path of the destination
    file.

    Args:
        dcc_tool (module): python module with DCC dependent tool methods
            to execute.
        dcc_scene_commands (module): python module with DCC dependent scene
            commands to execute.
        parent (:obj:`BaseWidget`): parent class of the current UI class.
        *args: argument list.
        **kwargs: keyword argument list.
    """
    def __init__(self, dcc_tool, dcc_scene_commands, parent, *args, **kwargs):
        super(AssetDefinitionExporterUi, self).__init__(
            "AdonisFX Asset Definition Exporter",
            parent,
            width=700,
            height=500)
        self._parent = parent
        self._dcc_tool = dcc_tool
        self._dcc_scene_commands = dcc_scene_commands

        # Class private attributes
        self._asset = None
        self._destination_file = ""
        self._asset_ok = False
        self._file_ok = False

        # Required to browse icons
        self._adonis_env = os.getenv("ADONISFX_RESOURCES", "")

        # Main method to build the interface
        self._build_ui()

        # Check initial selection and populate the content in the tree widget
        self._add_asset_from_selection(show_error=False)

    def _build_ui(self):
        """Builds the UI for the AdonisFX Asset Definition exporter.
        The interface is constructed in 3 sections: a tree widget to expose
        the asset data to export; a file browser to define the destination
        path; a buttons section to run the export or clear the contents of
        the tree widget.
        """
        self._file_icon_path = "{0}/adn_file.png".format(self._adonis_env)
        self._file_icon = QtGui.QIcon(self._file_icon_path)
        self._execute_icon_path = "{0}/adn_exporter.png".format(self._adonis_env)
        self._execute_icon = QtGui.QIcon(self._execute_icon_path)
        self._trash_icon_path = "{0}/adn_bin.png".format(self._adonis_env)
        self._trash_icon = QtGui.QIcon(self._trash_icon_path)

        # Reusable parameters
        self._button_width = 200
        self._button_height = 60

        ###############################
        # Asset Section
        ###############################
        # Tree widget
        self._tree_widget = QtWidgets.QTreeWidget()
        self._tree_widget.setColumnCount(2)
        self._tree_widget.setHeaderLabels(["Select Export Data", "Node Type"])
        self._tree_widget.header().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeToContents)
        self._tree_widget.header().setSectionResizeMode(
            0, QtWidgets.QHeaderView.Stretch)
        self._tree_widget.header().setStretchLastSection(False)
        self._tree_widget.setSortingEnabled(True)
        self._tree_widget.setAlternatingRowColors(True)
        self._tree_horizontal_layout = QtWidgets.QHBoxLayout()
        self._tree_horizontal_layout.addWidget(self._tree_widget)

        # Buttons: select and clear
        self._add_asset_button = QtWidgets.QPushButton("Add Selected")
        self._add_asset_button.resize(
            QtCore.QSize(self._button_width, self._button_height))
        self._add_asset_button.clicked.connect(self._add_asset_from_selection)
        self._clear_asset_button = QtWidgets.QPushButton("Clear")
        self._clear_asset_button.resize(
            QtCore.QSize(self._button_width, self._button_height))
        self._clear_asset_button.clicked.connect(self._clear_asset)
        self._asset_bottom_horizontal_layout = QtWidgets.QHBoxLayout()
        self._asset_bottom_horizontal_layout.addWidget(self._add_asset_button)
        self._asset_bottom_horizontal_layout.addWidget(self._clear_asset_button)

        # Global layout for the first section
        self._asset_global_vertical_layout = QtWidgets.QVBoxLayout()
        self._asset_global_vertical_layout.addLayout(
            self._tree_horizontal_layout)
        self._asset_global_vertical_layout.addLayout(
            self._asset_bottom_horizontal_layout)
        self._asset_group = QtWidgets.QGroupBox()
        self._asset_group.setTitle("Asset Definition")
        self._asset_group.setLayout(self._asset_global_vertical_layout)
        self._main_layout.addWidget(self._asset_group)

        ###############################
        # File Section
        ###############################
        # File selection component definition
        self._file_text_edit = QtWidgets.QLineEdit()
        self._file_text_edit.setReadOnly(True)
        self._file_text_edit.setPlaceholderText(
            "Output JSON file path")
        self._file_text_edit.setToolTip(
            "Select the destination file path to the AdonisFX Asset Definition.")

        self._add_file_button = QtWidgets.QPushButton()
        self._add_file_button.setIcon(self._file_icon)
        self._add_file_button.setIconSize(QtCore.QSize(16, 16))
        self._add_file_button.resize(
            QtCore.QSize(self._button_width, self._button_height))
        self._add_file_button.clicked.connect(self._browse_file)

        # File selection section layout
        self._file_left_horizontal_layout = QtWidgets.QHBoxLayout()
        self._file_left_horizontal_layout.addWidget(self._file_text_edit)

        self._file_right_vertical_layout = QtWidgets.QVBoxLayout()
        self._file_right_vertical_layout.addWidget(self._add_file_button)

        self._file_global_horizontal_layout = QtWidgets.QHBoxLayout()
        self._file_global_horizontal_layout.addLayout(
            self._file_left_horizontal_layout)
        self._file_global_horizontal_layout.addLayout(
            self._file_right_vertical_layout)

        self._file_group = QtWidgets.QGroupBox()
        self._file_group.setTitle("Output File Path")
        self._file_group.setLayout(self._file_global_horizontal_layout)

        self._main_layout.addWidget(self._file_group)

        ###############################
        # Executable buttons section
        ###############################
        # Run component definition
        self._clear_all_button = QtWidgets.QPushButton("Clear All")
        self._clear_all_button.setIcon(self._trash_icon)
        self._clear_all_button.setIconSize(QtCore.QSize(18, 18))
        self._clear_all_button.resize(
            QtCore.QSize(self._button_width, self._button_height))
        self._clear_all_button.clicked.connect(self._clear_all)

        self._export_button = QtWidgets.QPushButton("Export")
        self._export_button.setIcon(self._execute_icon)
        self._export_button.setIconSize(QtCore.QSize(18, 18))
        self._export_button.resize(
            QtCore.QSize(self._button_width, self._button_height))
        self._export_button.clicked.connect(self._export)
        self._export_button.setEnabled(False)

        # Run section layout
        self._export_horizontal_layout = QtWidgets.QHBoxLayout()
        self._export_horizontal_layout.addWidget(self._clear_all_button)
        self._export_horizontal_layout.addWidget(self._export_button)

        self._main_layout.addLayout(self._export_horizontal_layout)

    def _update_export_button_status(self):
        """Checks if all input values have been correctly added."""
        self._export_button.setEnabled(self._asset_ok and self._file_ok)

    def _add_asset_from_selection(self, show_error=True):
        """Collects AdonisFX nodes connected to the current selection. If valid
        nodes are found, the tree widget gets populated with the relevant
        information to export.

        Args:
            show_error (bool, optional): flag to determine if a message box
                has to be prompted in case of error. Defaults to True.
        """
        self._clear_asset()

        # Get selection and search for AdonisFX nodes to export
        tmp_asset_name = self._dcc_scene_commands.get_selection(long_path=False)
        relevant_nodes = self._dcc_tool.extract_relevant_nodes(tmp_asset_name)

        # Invalid selection
        if not relevant_nodes:
            if show_error:
                msg_box(self, "error",
                        "Invalid selection. Please, select an "
                        "object with AdonisFX nodes and try again.")
            return

        self._asset_ok = True
        self._update_export_button_status()
        self._update_tree_widget(tmp_asset_name[0], relevant_nodes)

    def _clear_asset(self):
        """Clears the content of the tree widget."""
        self._asset_ok = False
        self._tree_widget.clear()
        self._update_export_button_status()

    def _browse_file(self):
        """Opens a file selection dialog filtering by JSON type to allow the
        user to pick a destination file path.
        """
        tmp_destination_file = QtWidgets.QFileDialog.getSaveFileName(
            self,
            caption="Save AdonisFX Asset Definition",
            filter="AdonisFX Asset Definition File (*.JSON)")[0]

        # Check if the destination file path was set correctly.
        if not tmp_destination_file:
            msg_box(self, "error", "Invalid file path provided.")
            return

        self._clear_file()
        self._destination_file = tmp_destination_file
        self._file_ok = True
        self._file_text_edit.setText(self._destination_file)
        self._update_export_button_status()

    def _clear_file(self):
        """Clears path to the destination file."""
        self._destination_file = None
        self._file_ok = False
        self._file_text_edit.setText("")
        self._update_export_button_status()

    def _clear_all(self):
        """Clears both the tree widget and the destination file path."""
        self._clear_asset()
        self._clear_file()

    def _is_ready_to_export(self, asset):
        """Checks if data in the UI is valid and ready to export.
        
        Args:
            asset (str): asset that is about to be exported.
            
        Returns:
            bool: True if data is valid to export, False otherwise.
        """
        asset_check = self._dcc_scene_commands.exists(asset)
        if not asset_check:
            msg_box(self, "error", "Asset not found in the scene.")
        file_check = os.path.isabs(self._destination_file)
        format_check = self._destination_file[-5:].upper() == ".JSON"
        if not file_check or not format_check:
            msg_box(self, "error", "Invalid file path.")

        return asset_check and file_check

    def _update_tree_widget(self, asset_name, relevant_nodes):
        """ Updates the content of the tree widget based on asset selection.

        Args:
            asset_name (str): asset that has been selected.
                Will be populated at the tree widget with its features.
            relevant_nodes (dict): dictionary with relevant nodes found in
                the hierarchy of the input asset object.
        """
        self._tree_widget.clear()
        asset_item = QtWidgets.QTreeWidgetItem([asset_name])
        asset_item.setFlags(asset_item.flags()
                            | QtCore.Qt.ItemIsUserCheckable
                            | QtCore.Qt.ItemIsSelectable
                            | QtCore.Qt.ItemIsAutoTristate)
        asset_item.setCheckState(0, QtCore.Qt.CheckState.Checked)

        # Populate nodes data
        for node_type in relevant_nodes.keys():
            for node in relevant_nodes[node_type]:
                self._add_tree(asset_item, node, node_type)

        self._tree_widget.addTopLevelItem(asset_item)

    def _add_tree(self, parent, node, node_type):
        """Creates and adds a QTreeWidgetItem with data to export associated
        to the given node.

        Args:
            parent (:obj:`QTreeWidgetItem`): item in tree widget to parent.
            node (str): name of the node that is going to be populated on the tree.
            node_type (str): node type used to get features from node.
        """
        # Node
        node_item = QtWidgets.QTreeWidgetItem([node, node_type])
        node_item.setFlags(node_item.flags()
                           | QtCore.Qt.ItemIsUserCheckable
                           | QtCore.Qt.ItemIsSelectable
                           | QtCore.Qt.ItemIsAutoTristate)
        node_item.setCheckState(0, QtCore.Qt.CheckState.Checked)

        # Features
        for feature in AssetDefinition.NODE_FEATURES[node_type]:
            element = QtWidgets.QTreeWidgetItem([feature, ""])
            element.setFlags(element.flags()
                             | QtCore.Qt.ItemIsUserCheckable
                             | QtCore.Qt.ItemIsSelectable
                             | QtCore.Qt.ItemIsAutoTristate)
            element.setCheckState(0, QtCore.Qt.CheckState.Checked)

            if feature == "Maps":
                for map_item in self._dcc_tool.extract_map_attributes(node, node_type):
                    sub_element = QtWidgets.QTreeWidgetItem([map_item, ""])
                    sub_element.setFlags(sub_element.flags()
                                         | QtCore.Qt.ItemIsUserCheckable
                                         | QtCore.Qt.ItemIsSelectable)
                    sub_element.setCheckState(0, QtCore.Qt.CheckState.Checked)
                    element.addChild(sub_element)
            node_item.addChild(element)

        parent.addChild(node_item)

    def _export(self):
        """Main method to execute the export."""
        root = self._tree_widget.invisibleRootItem()
        if root.childCount() == 0:
            return
        # First row, first column: ensures that pick the parent node/group
        asset = root.child(0).text(0)

        if not self._is_ready_to_export(asset):
            return

        # Prepare data to export
        export_assets = dict()

        # Iterate over the objects inside the root
        for asset_idx in range(root.childCount()):
            # Assets
            asset_item = root.child(asset_idx)
            asset_name = asset_item.text(0)
            export_assets[asset_name] = dict()

            # Iterate over the nodes inside each node
            for idx in range(asset_item.childCount()):
                node_item = asset_item.child(idx)
                node_name = node_item.text(0)
                checked = node_item.checkState(0) != QtCore.Qt.CheckState.Unchecked
                export_assets[asset_name][node_name] = dict()
                export_assets[asset_name][node_name]["node"] = checked

                # Iterate over the features inside a node
                for feature_idx in range(node_item.childCount()):
                    # Features to export
                    feature_node_item = node_item.child(feature_idx)
                    feature_name = feature_node_item.text(0)
                    checked = feature_node_item.checkState(0) != QtCore.Qt.CheckState.Unchecked
                    export_assets[asset_name][node_name][feature_name] = checked

                    # Iterate over the elements inside a feature
                    for element_feature_idx in range(feature_node_item.childCount()):
                        # Components of feature
                        element_feature_item = feature_node_item.child(element_feature_idx)
                        sub_feature_name = element_feature_item.text(0)
                        checked = element_feature_item.checkState(0) != QtCore.Qt.CheckState.Unchecked
                        export_assets[asset_name][node_name][sub_feature_name] = checked

        # Do export
        with cursor.wait_cursor_context():
            response = self._dcc_tool.export_asset_definition(
                export_assets,
                self._destination_file)

        # Check result from the export and prompt dialog to inform the user
        if response:
            msg_box(self,
                    "Information",
                    "AdonisFX Asset Definition data exported!")
        else:
            msg_box(self,
                    "error",
                    "Failed to export AdonisFX Asset Definition. Please, check "
                    "the console for more information.")
