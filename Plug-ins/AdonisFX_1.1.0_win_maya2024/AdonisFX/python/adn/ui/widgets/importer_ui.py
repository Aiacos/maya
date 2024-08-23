import os
import re
import copy

from PySide2 import QtCore, QtGui, QtWidgets

from adn.ui.widgets.base import BaseWidget
from adn.ui.widgets.dialogs import msg_box
from adn.ui.utils import cursor
from adn.utils.constants import AssetDefinition, AssetDefinitionImportStatusCode
import adn.utils.asset_definition as asset_definition_utils


class AssetDefinitionImporterUi(BaseWidget):
    """UI class for the AdonisFX Asset Definition importer

    Class used to generate AdonisFX Asset Definition file based on selection.

    Args:
        dcc_tool (module): Tool that will be launching the command associated to the UI.
        dcc_scene_commands (module): Commands that will invoke scene functions.
        parent (:obj:`BaseWidget`): Parent class of the current UI class.
        *args: Argument list.
        **kwargs: Keyword argument list.
    """

    def __init__(self, dcc_tool, dcc_scene_commands, parent, *args, **kwargs):
        super(AssetDefinitionImporterUi, self).__init__(
            "AdonisFX Asset Definition Importer",
            parent,
            width=900,
            height=550)
        self._parent = parent
        self._dcc_tool = dcc_tool
        self._dcc_scene_commands = dcc_scene_commands

        # Class private attributes
        self._input_file = None
        self._asset_ok = False
        self._file_ok = False

        # Store raw data from the selected file
        self._raw_file_data = copy.deepcopy(AssetDefinition.TEMPLATE)
        # Store import assignments data file-to-scene
        self._import_assignment_data = copy.deepcopy(AssetDefinition.TEMPLATE)

        # Required to browse icons
        self._adonis_env = os.getenv("ADONISFX_RESOURCES", "")

        # Main method to build the interface
        self._build_ui()

        # Fill the mesh list on the right with the initial selection (if any)
        self._add_asset_from_selection(show_error=False)

    def _build_ui(self):
        """Builds the UI for the AAD importer."""
        self._file_icon_path = "{0}/adn_file.png".format(self._adonis_env)
        self._file_icon = QtGui.QIcon(self._file_icon_path)
        self._import_icon_path = "{0}/adn_importer.png".format(self._adonis_env)
        self._import_icon = QtGui.QIcon(self._import_icon_path)
        self._trash_icon_path = "{0}/adn_bin.png".format(self._adonis_env)
        self._trash_icon = QtGui.QIcon(self._trash_icon_path)

        # Reusable parameters
        self._button_width = 200
        self._button_height = 60

        ###############################
        # File path section
        ###############################
        # File selection component definition
        self._file_text_edit = QtWidgets.QLineEdit()
        self._file_text_edit.setReadOnly(True)
        self._file_text_edit.setMaximumHeight(75)
        self._file_text_edit.setPlaceholderText(
            "Input JSON file path")
        self._file_text_edit.setToolTip(
            "Select the file path to the input AdonisFX Asset Definition.")

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
        self._file_group.setTitle("Input File Path")
        self._file_group.setLayout(self._file_global_horizontal_layout)

        self._main_layout.addWidget(self._file_group)

        ###############################
        # File content section
        ###############################
        self._vertical_header_nodes_table = QtWidgets.QHeaderView(
            QtCore.Qt.Vertical)
        self._vertical_header_nodes_table.hide()
        self._nodes_table = QtWidgets.QTableWidget(0, 2)
        self._nodes_table.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectRows)
        self._nodes_table.setMinimumWidth(400)
        self._nodes_table.setVerticalHeader(
            self._vertical_header_nodes_table)
        self._nodes_table.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch)
        self._nodes_table.setHorizontalHeaderLabels(
            ["Node Name", "Node Type"])
        self._nodes_table.setSortingEnabled(True)

        self._assign_button = QtWidgets.QPushButton("Assign")
        self._assign_button.resize(
            QtCore.QSize(self._button_width, self._button_height))
        self._assign_button.setToolTip(
            "Assigns node selected to mesh(es) selected")
        self._assign_button.clicked.connect(self._make_assignment)

        self._delete_button = QtWidgets.QPushButton("Delete")
        self._delete_button.resize(
            QtCore.QSize(self._button_width, self._button_height))
        self._delete_button.setToolTip(
            "Removes candidate node for the mesh(es) selected")
        self._delete_button.clicked.connect(self._remove_assignment)

        # Neutral asset component definition
        self._vertical_header_mesh_table = QtWidgets.QHeaderView(
            QtCore.Qt.Vertical)
        self._vertical_header_mesh_table.hide()
        self._mesh_table = QtWidgets.QTableWidget(0, 3)
        self._mesh_table.setMinimumWidth(400)
        self._mesh_table.setVerticalHeader(self._vertical_header_mesh_table)
        self._mesh_table.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch)
        self._mesh_table.setHorizontalHeaderLabels(
            ["Mesh", "Candidate Node", "Asset"])
        self._mesh_table.setColumnHidden(2, True)
        self._mesh_table.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection)
        self._mesh_table.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectRows)
        self._mesh_table.setSortingEnabled(True)
        self._mesh_table.itemSelectionChanged.connect(self._mesh_item_selected)

        self._add_asset_button = QtWidgets.QPushButton("Add Selected")
        self._add_asset_button.resize(
            QtCore.QSize(self._button_width, self._button_height))
        self._add_asset_button.clicked.connect(self._add_asset_from_selection)

        self._clear_asset_button = QtWidgets.QPushButton("Clear")
        self._clear_asset_button.resize(
            QtCore.QSize(self._button_width, self._button_height))
        self._clear_asset_button.clicked.connect(self._clear_asset)

        # Neutral mesh section layout
        self._asset_vertical_buttons_layout = QtWidgets.QVBoxLayout()
        self._asset_vertical_buttons_layout.setAlignment(
            QtCore.Qt.AlignVCenter)
        self._asset_vertical_buttons_layout.addWidget(self._assign_button)
        self._asset_vertical_buttons_layout.addWidget(self._delete_button)

        self._asset_top_horizontal_layout = QtWidgets.QHBoxLayout()
        self._asset_top_horizontal_layout.addWidget(self._mesh_table)

        self._asset_bottom_horizontal_layout = QtWidgets.QHBoxLayout()
        self._asset_bottom_horizontal_layout.addWidget(self._add_asset_button)
        self._asset_bottom_horizontal_layout.addWidget(
            self._clear_asset_button)

        self._asset_vertical_layout = QtWidgets.QVBoxLayout()
        self._asset_vertical_layout.addLayout(
            self._asset_top_horizontal_layout)
        self._asset_vertical_layout.addLayout(
            self._asset_bottom_horizontal_layout)

        self._asset_parent_horizontal_layout = QtWidgets.QHBoxLayout()
        self._asset_parent_horizontal_layout.addWidget(self._nodes_table)
        self._asset_parent_horizontal_layout.addLayout(
            self._asset_vertical_buttons_layout)
        self._asset_parent_horizontal_layout.addLayout(
            self._asset_vertical_layout)

        self._asset_group = QtWidgets.QGroupBox()
        self._asset_group.setMinimumHeight(200)
        self._asset_group.setTitle("Import Configuration")
        self._asset_group.setLayout(self._asset_parent_horizontal_layout)

        self._main_layout.addWidget(self._asset_group)

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

        self._import_button = QtWidgets.QPushButton("Import")
        self._import_button.setIcon(self._import_icon)
        self._import_button.setIconSize(QtCore.QSize(18, 18))
        self._import_button.resize(
            QtCore.QSize(self._button_width, self._button_height))
        self._import_button.clicked.connect(self._import)
        self._import_button.setEnabled(False)

        # Run section layout
        self._import_horizontal_layout = QtWidgets.QHBoxLayout()
        self._import_horizontal_layout.addWidget(self._clear_all_button)
        self._import_horizontal_layout.addWidget(self._import_button)

        self._main_layout.addLayout(self._import_horizontal_layout)

    def _update_import_button_status(self):
        """Checks if all input values have been correctly added"""
        self._import_button.setEnabled(self._asset_ok and self._file_ok)

    def _mesh_item_selected(self):
        """Called when an element of the mesh tree is selected. It will select
        the item in the scene.
        """
        # Get item selected column
        mesh_items_selected = self._mesh_table.selectedItems()
        if not mesh_items_selected:
            return

        mesh_long_names = [item.toolTip() for item in mesh_items_selected
                           if item.column() == 0]
        self._dcc_scene_commands.select(mesh_long_names)

    def _make_assignment(self):
        """Will assign the node selected on the node list to all the meshes
        selected on the mesh tree. In addition, will populate a tree widget with
        the features of the node.
        """
        node_selected = self._nodes_table.currentItem()
        if not node_selected:
            msg_box(self, "error", "No selected nodes to assign. "
                    "Please, select a node from the list on the left, a "
                    "destination mesh from the list on the right and try again.")
            return

        node_selected = self._nodes_table.item(node_selected.row(), 0)
        node_name = node_selected.text()
        node_full_name = node_selected.toolTip()

        mesh_items_selected = self._mesh_table.selectedItems()
        mesh_items_selected = [item for item in mesh_items_selected
                               if item.column() == 0]
        if not mesh_items_selected:
            msg_box(self, "error", "No selected meshes to assign the selected node. "
                    "Please, select a node from the liston the left, a destination "
                    "mesh from the list on the right and try again.")
            return

        # Stop sorting, needed when manipulating elements of sorted tree
        self._mesh_table.setSortingEnabled(False)

        # Iterate over the meshes selected
        for idx in range(len(mesh_items_selected)):
            row = mesh_items_selected[idx].row()
            candidate_node_widget = self._mesh_table.item(row, 1)
            candidate_node_widget.setText(node_name)
            candidate_node_widget.setToolTip(node_full_name)

            mesh = mesh_items_selected[idx].toolTip()
            asset_name = self._mesh_table.item(row, 2).text()
            # Remove old candidate assignment from `_import_assignment_data`
            self._clear_assignment_data(asset_name, mesh)
            # Add this candidate assignment to `_import_assignment_data`
            self._fill_assignment_data(asset_name, mesh, node_full_name)

        # Enable sorting again
        self._mesh_table.setSortingEnabled(True)

    def _remove_assignment(self):
        """Remove the node assigned to the meshes selected. It will also remove
        the tree with the features of the node.
        """
        # Stop sorting, needed when manipulating elements of sorted tree
        self._mesh_table.setSortingEnabled(False)

        mesh_items_selected = self._mesh_table.selectedItems()
        mesh_items_selected = [item for item in mesh_items_selected
                               if item.column() == 0]
        for idx in range(len(mesh_items_selected)):
            # Remove assignment from the widget
            row = mesh_items_selected[idx].row()
            candidate_node_widget = self._mesh_table.item(row, 1)
            candidate_node_widget.setText("")
            candidate_node_widget.setToolTip("")

            mesh = mesh_items_selected[idx].toolTip()
            asset_name = self._mesh_table.item(row, 2).text()
            # Remove old candidate assignment from `_import_assignment_data`
            self._clear_assignment_data(asset_name, mesh)

        # Enable sorting again
        self._mesh_table.setSortingEnabled(True)

    def _add_asset_from_selection(self, show_error=True):
        """Get the selected asset. Sanity checks are launched when the
        select button in a neutral mesh context is launched.

        Args:
            show_error (bool, optional): flag to determine if a message box
                has to be prompted in case of error. Defaults to True.
        """
        selection_short_names = self._dcc_scene_commands.get_selection(
            long_path=False)
        selection_long_names = self._dcc_scene_commands.get_selection(
            long_path=True)

        if not selection_short_names or not selection_long_names:
            if show_error:
                msg_box(self, "error", "Empty selection is not valid.")
            return

        # Clear data
        self._clear_asset()
        self._mesh_table.setSortingEnabled(False)

        # Iterate overt the selection
        for parent in selection_short_names:
            all_meshes = self._dcc_scene_commands.list_relatives(parent, "mesh")
            meshes, meshes_short_names = all_meshes
            if not meshes:
                continue

            num_meshes = len(meshes)
            row_offset = self._mesh_table.rowCount()
            self._asset_ok = True if num_meshes > 0 else self._asset_ok
            self._mesh_table.setRowCount(num_meshes + row_offset)

            # Iterate over the shapes in hierarchy of the selected object
            for idx in range(num_meshes):
                # Column 0
                mesh_widget = QtWidgets.QTableWidgetItem(
                    meshes_short_names[idx])
                mesh_widget.setFlags(
                    mesh_widget.flags() & ~QtCore.Qt.ItemIsEditable)
                mesh_widget.setToolTip(meshes[idx])
                self._mesh_table.setItem(idx + row_offset, 0, mesh_widget)

                # Column 1
                candidate_widget = QtWidgets.QTableWidgetItem()
                candidate_widget.setFlags(
                    candidate_widget.flags() & ~QtCore.Qt.ItemIsEditable)
                self._mesh_table.setItem(idx + row_offset, 1, candidate_widget)

                # Column 2
                asset_widget = QtWidgets.QTableWidgetItem(parent)
                self._mesh_table.setItem(idx + row_offset, 2, asset_widget)

                # Search for a valid candidate node to assign to this mesh
                candidate, candidate_short_name = self._dcc_tool.search_for_matching_node(
                    self._raw_file_data, meshes[idx])
                if not candidate:
                    continue

                # Candidate node found, make automatic assignment
                candidate_widget.setText(candidate_short_name)
                candidate_widget.setToolTip(candidate)

                # Add this candidate assignment to `_import_assignment_data`
                self._fill_assignment_data(parent, meshes[idx], candidate)

        self._mesh_table.setSortingEnabled(True)
        self._update_import_button_status()

        # Restore original selection
        self._dcc_scene_commands.select(selection_long_names)

    def _clear_asset(self):
        """Clear the flag, mesh tree and selection. Also, disables the
        import button.
        """
        del self._import_assignment_data["assets"][:]
        self._asset_ok = False
        self._mesh_table.setRowCount(0)
        self._update_import_button_status()

    def _browse_file(self):
        """Open a file selection dialog when clicked. Sanity checks are
        launched when the select button in a file selection context is
        launched. Trees will be updated accordingly the data of the file.
        """
        tmp_destination_file = QtWidgets.QFileDialog.getOpenFileName(
            self,
            caption="Open AdonisFX Asset Definition",
            filter="AdonisFX Asset Definition File (*.JSON)")[0]

        # If open dialog was closed or cancelled, do nothing
        if not tmp_destination_file:
            return

        # If provided file does not exist, prompt an error and exit
        if not os.path.exists(tmp_destination_file):
            msg_box(self, "error", "Provided file path does not exist.")
            return

        # Read file
        is_valid, data_dict = asset_definition_utils.\
            load_asset_definition_file(tmp_destination_file)
        if not is_valid:
            msg_box(self, "error",
                    "Provided file is not a valid AdonisFX Asset Definition.")
            return

        # Clear data
        self._clear_file()
        # Cache data
        self._raw_file_data = data_dict
        self._input_file = tmp_destination_file
        self._file_text_edit.setText(self._input_file)
        self._file_ok = True
        self._update_import_button_status()
        # For completeness (not critical)
        self._import_assignment_data["__dcc__"] = self._raw_file_data["__dcc__"]
        self._import_assignment_data["__version__"] = self._raw_file_data["__version__"]

        # Update table widgets
        # nodes_info is a list of tuples with 4 string each:
        # 0: node name
        # 1: node full name
        # 2: node type
        # 3: mesh assigned to that node
        nodes_info = asset_definition_utils.\
            get_nodes_info_from_asset_definition(self._raw_file_data)
        num_nodes = len(nodes_info)

        self._mesh_table.setSortingEnabled(False)
        self._nodes_table.setSortingEnabled(False)
        self._nodes_table.clearSelection()
        self._nodes_table.setRowCount(num_nodes)
        for idx in range(num_nodes):
            name, full_name, node_type, mesh_assigned = nodes_info[idx]

            # Add node to the nodes_table
            node_widget = QtWidgets.QTableWidgetItem(name)
            node_widget.setToolTip(full_name)
            node_widget.setFlags(
                node_widget.flags() & ~QtCore.Qt.ItemIsEditable)
            type_widget = QtWidgets.QTableWidgetItem(node_type)
            type_widget.setFlags(
                type_widget.flags() & ~QtCore.Qt.ItemIsEditable)
            self._nodes_table.setItem(idx, 0, node_widget)
            self._nodes_table.setItem(idx, 1, type_widget)

            # Search for meshes in mesh_table fitting for this node
            for row_idx in range(self._mesh_table.rowCount()):
                mesh_table_widget = self._mesh_table.item(row_idx, 0)
                if mesh_assigned != mesh_table_widget.toolTip():
                    continue
                candidate_widget = QtWidgets.QTableWidgetItem(name)
                candidate_widget.setToolTip(full_name)
                candidate_widget.setFlags(
                    candidate_widget.flags() & ~QtCore.Qt.ItemIsEditable)
                self._mesh_table.setItem(row_idx, 1, candidate_widget)

                # Add this candidate assignment to `_import_assignment_data`
                asset_widget = self._mesh_table.item(row_idx, 2)
                self._fill_assignment_data(asset_widget.text(),
                                           mesh_table_widget.toolTip(),
                                           full_name)

        # Enable sorting
        self._nodes_table.setSortingEnabled(True)
        self._mesh_table.setSortingEnabled(True)

    def _clear_file(self):
        """Clear the flag, destination file and text and the node tree.
        Also, disables the "import" button
        """
        self._input_file = None
        self._file_ok = False
        self._file_text_edit.setText("")
        self._nodes_table.setRowCount(0)
        self._raw_file_data = copy.deepcopy(AssetDefinition.TEMPLATE)
        self._import_assignment_data = copy.deepcopy(AssetDefinition.TEMPLATE)

        # Clear assignations on mesh table
        # Stop sorting, needed when manipulating elements of sorted table
        self._mesh_table.setSortingEnabled(False)
        self._mesh_table.clearSelection()

        for asset_idx in range(self._mesh_table.rowCount()):
            candidate_item = self._mesh_table.item(asset_idx, 1)
            candidate_item.setText("")

        self._mesh_table.setSortingEnabled(True)
        self._update_import_button_status()

    def _clear_all(self):
        """Clears and resets all inputs.
        """
        self._clear_asset()
        self._clear_file()

    def _is_ready_to_import(self):
        """Check if data provided in the UI is valid and can be
        used to launch the AdonisFX Asset Definition importer

        Returns:
            bool: returns the outcome of the check before the execution.
        """
        is_ready, error_message = self._dcc_tool.is_ready_to_import(
            self._import_assignment_data)
        if not is_ready and error_message:
            msg_box(self, "error", error_message)
            return False

        return True

    def _import(self):
        """Execute the import. This method also prompts message dialogs to
        inform the user about the result of the execution."""
        if not self._is_ready_to_import():
            return

        with cursor.wait_cursor_context():
            response = self._dcc_tool.import_asset_definition(
                self._import_assignment_data)

        # Check result from the export and prompt dialog to inform the user
        if response == AssetDefinitionImportStatusCode.SUCCESS:
            msg_box(self, "Information",
                    "AdonisFX Asset Definition data imported successfully!")
        elif response == AssetDefinitionImportStatusCode.WARNING:
            msg_box(self, "Warning",
                    "AdonisFX Asset Definition data imported partially: "
                    "some of the import assignments could not complete with "
                    "success. Please, check the console for more information.")
        else:
            msg_box(self, "Error",
                    "AdonisFX Asset Definition data not imported. "
                    "Please, check the console for more information.")

    def _fill_assignment_data(self, asset_name, mesh, node):
        """Populate information about the pair between the mesh and node that
        are going to be imported. If there is already data about that mesh,
        will be replaced.

        Args:
            asset_name (str): Asset name. Corresponds to the element selected
                (parent object) of the mesh to receive the node assignment.
            mesh (str): Mesh name to receive the node assignment.
            node (str): Node name to assign to the mesh.
        """
        # Find node_data in file content to assign
        node_data_block = None
        for asset in self._raw_file_data["assets"]:
            for data_block in asset["data"]:
                if data_block["__full_name__"] == node:
                    node_data_block = data_block
                    break
            if node_data_block:
                break
        if not node_data_block:
            return

        # Check if asset_name already added to _import_assignment_data
        asset_dictionary = None
        for asset in self._import_assignment_data["assets"]:
            if asset["__asset_path__"] == asset_name:
                asset_dictionary = asset
                break
        # If not added (assignment not made yet), then create empty assignment
        if not asset_dictionary:
            # First time we add a mesh from this asset
            nice_name = self._dcc_scene_commands.nice_name(asset_name)
            asset_dictionary = copy.deepcopy(AssetDefinition.ASSET_TEMPLATE)
            asset_dictionary["__asset_path__"] = asset_name
            asset_dictionary["__asset__"] = nice_name
            self._import_assignment_data["assets"].append(asset_dictionary)

        # Populate mesh data block
        import_data_block = dict()
        node_name = self._dcc_tool.get_name_based_on_hierarchy(node, mesh)
        import_data_block["__type__"] = node_data_block["__type__"]
        import_data_block["__name__"] = node_name
        import_data_block["__full_name__"] = node_name
        import_data_block["__mesh_name__"] = mesh
        import_data_block["__num_vertices__"] = node_data_block["__num_vertices__"]
        import_data_block["__num_poly__"] = node_data_block["__num_poly__"]
        import_data_block["data"] = node_data_block["data"]

        # Assign data to asset_dictionary object which is a reference to an
        # entry in _import_assignment_data
        asset_dictionary["data"].append(copy.deepcopy(import_data_block))

    def _clear_assignment_data(self, asset_name, mesh):
        """Remove information about the mesh sent.

        Args:
            asset_name (str): Asset name. Corresponds to the element selected
                (parent object) of the mesh to receive the node assignment.
            mesh (str): Mesh name to receive the node assignment.
        """
        # Remove from import data structure
        for asset in self._import_assignment_data["assets"]:
            if asset["__asset_path__"] != asset_name:
                continue
            for data_block_idx in range(len(asset["data"])):
                if asset["data"][data_block_idx]["__mesh_name__"] == mesh:
                    asset["data"].pop(data_block_idx)
                    return

        return
