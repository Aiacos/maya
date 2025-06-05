try:
    from PySide6 import QtCore, QtWidgets
except ImportError:
    from PySide2 import QtCore, QtWidgets

import maya.cmds as cmds

from adn.ui.widgets.base import BaseWidget
from adn.ui.widgets.dialogs import msg_box, report_error
from adn.ui.maya.window import main_window


class SensorsConnectionEditorUI(BaseWidget):
    """UI class to make the connections between AdonisFX Sensors with nodes.

    Args:
        dcc_tool (module): Tool that will be launching the command associated to the UI.
        parent (:obj:`BaseWidget`): Parent class of the current UI class.
        *args: Argument list.
        **kwargs: Keyword argument list.
    """
    def __init__(self, dcc_tool, parent, *args, **kwargs):
        super(SensorsConnectionEditorUI, self).__init__("AdonisFX Sensors Connection Editor",
                                                        parent,
                                                        width=600,
                                                        height=300)
        self._dcc_tool = dcc_tool

        self._build_ui()

    def _build_ui(self):
        """Builds the UI for the connection editor"""
        # General parameters
        self._button_width = 200
        self._button_height = 60

        ###############################
        # BEGIN RELOAD SECTION
        ###############################
        self._reload_left_button = QtWidgets.QPushButton("Reload Left")
        self._reload_left_button.resize(QtCore.QSize(self._button_width, self._button_height))
        self._reload_left_button.clicked.connect(self._reload_left_on_clicked)

        self._reload_right_button = QtWidgets.QPushButton("Reload Right")
        self._reload_right_button.resize(QtCore.QSize(self._button_width, self._button_height))
        self._reload_right_button.clicked.connect(self._reload_right_on_clicked)

        self._reload_buttons_horizontal_layout = QtWidgets.QHBoxLayout()
        self._reload_buttons_horizontal_layout.addWidget(self._reload_left_button)
        self._reload_buttons_horizontal_layout.addWidget(self._reload_right_button)

        self._main_layout.addLayout(self._reload_buttons_horizontal_layout)

        ###############################
        # BEGIN TREE SECTION
        ###############################
        self._sources_tree = QtWidgets.QTreeWidget()
        self._sources_tree.setHeaderLabels(["Source"])
        self._sources_tree.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self._sources_tree.setSortingEnabled(True)
        self._sources_tree.sortByColumn(0, QtCore.Qt.AscendingOrder)

        self._destination_tree = QtWidgets.QTreeWidget()
        self._destination_tree.setHeaderLabels(["Destination"])
        self._destination_tree.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self._destination_tree.setSortingEnabled(True)
        self._destination_tree.sortByColumn(0, QtCore.Qt.AscendingOrder)

        self._tree_horizontal_layout = QtWidgets.QHBoxLayout()
        self._tree_horizontal_layout.addWidget(self._sources_tree)
        self._tree_horizontal_layout.addWidget(self._destination_tree)

        self._main_layout.addLayout(self._tree_horizontal_layout)

        ###############################
        # BEGIN CONNECT SECTION
        ###############################
        self._clear_button = QtWidgets.QPushButton("Clear All")
        self._clear_button.resize(QtCore.QSize(self._button_width, self._button_height))
        self._clear_button.clicked.connect(self._clear_all_on_clicked)

        self._make_connection_button = QtWidgets.QPushButton("Make Connection")
        self._make_connection_button.clicked.connect(self._connect_on_clicked)
        self._make_connection_button.setEnabled(False)

        self._button_horizontal_layout = QtWidgets.QHBoxLayout()
        self._button_horizontal_layout.addWidget(self._clear_button)
        self._button_horizontal_layout.addWidget(self._make_connection_button)

        self._main_layout.addLayout(self._button_horizontal_layout)

    def _toogle_make_connection_button(self):
        """Toggles if the "Make Connection" button should be enabled or not"""
        self._make_connection_button.setEnabled(len(self._sources_tree.selectedItems()) and
                                                len(self._destination_tree.selectedItems()))

    def _clear_sources_column(self):
        """Clears the source column and tree. Clearing the tree and toggling button."""
        self._sources_tree.clear()
        self._toogle_make_connection_button()

    def _clear_destination_column(self):
        """Clears the destination column and tree. Clearing the tree and toggling button."""
        self._destination_tree.clear()
        self._toogle_make_connection_button()

    def _clear_all_on_clicked(self):
        """Clears both tree widgets. Will disabled the "Make Connections" button"""
        self._clear_sources_column()
        self._clear_destination_column()

    def _reload_left_on_clicked(self):
        """Reloads the source tree based on selection."""
        success, source_nodes, short_source_names = self._dcc_tool.collect_connection_info_source_nodes()
        report_error(success, "collecting source nodes")
        if source_nodes:
            self._clear_sources_column()
            self._populate_sources_tree(source_nodes, short_source_names)

    def _reload_right_on_clicked(self):
        """Reloads the destination tree based on selection."""
        success, nodes, short_destination_nodes = self._dcc_tool.collect_destination_nodes_plugs()
        report_error(success, "collecting destination nodes")
        if nodes:
            self._clear_destination_column()
            self._populate_destination_tree(nodes, short_destination_nodes)

    def _check_on_run(self):
        """Check if there is a valid selection for the attribute connection.

        Returns:
            bool: returns the outcome of the check before the execution.
        """
        sensor_check = True
        source_attr_selected = self._sources_tree.selectedItems()
        if not len(source_attr_selected):
            sensor_check = False

        node_check = True
        node_attr_selected = self._destination_tree.selectedItems()
        if not len(node_attr_selected):
            node_check = False

        return sensor_check and node_check

    def _connect_on_clicked(self):
        """Run the command when the "Make Connection" button is clicked. Will try to make a
        connection between the selected attributes on the trees.
        """
        if not self._check_on_run():
            msg_box(self, "error", "Wrong selection. Please, select one attribute from the Source "
                                   "and one attribute from the Destination and try again.")
            return

        # First and only source node attribute selected
        source_selected = self._sources_tree.selectedItems()
        source_selected = (source_selected[0].parent().toolTip(0) +
                           "." + source_selected[0].text(0))

        # First and only node attribute selected
        attribute_node_selected = self._destination_tree.selectedItems()
        attribute_node_selected = (attribute_node_selected[0].parent().toolTip(0) +
                                   "." + attribute_node_selected[0].text(0))

        # Connect attribute
        response = self._override_connection(attribute_node_selected)
        # Abort the connection if the user does not want to override it
        if not response:
            return
        result = self._dcc_tool.connect_sensor_output(source_selected, attribute_node_selected, force=response)
        report_error(result, "connecting the source and destination plugs")

    def _populate_sources_tree(self, source_nodes, short_source_names):
        """Populates, based on the source data, the left tree.

        Args:
            source_nodes (dict): Dictionary with key:sensor/locator and value:list of atributes to
                                 use as source plugs.
            short_source_names (dict): Dictionary with key:node and value:short name for that
                                       locator/sensor.
        """
        self._sources_tree.clear()
        source_tree = self._sources_tree.invisibleRootItem()
        for sensor in source_nodes.keys():
            self._add_tree(source_tree, sensor, short_source_names[sensor], source_nodes[sensor])
        self._sources_tree.itemClicked.connect(self._toogle_make_connection_button)

    def _populate_destination_tree(self, nodes, short_destination_names):
        """Populates, based on the node data, the left tree. If an attribute "activation" is found
        will select it.

        Args:
            nodes (dict): Dictionary with key:node and value:list of float plugs.
            short_destination_names (dict): Dictionary with key:node and value:short name for that
                                            node.
        """
        self._destination_tree.clear()
        destination_tree = self._destination_tree.invisibleRootItem()
        for node in nodes.keys():
            self._add_tree(destination_tree, node, short_destination_names[node], nodes[node])
        self._destination_tree.itemClicked.connect(self._toogle_make_connection_button)

        # Search for an "Activation" plug. If found, select it. 
        activation_item = self._destination_tree.findItems(
            "activation", QtCore.Qt.MatchExactly | QtCore.Qt.MatchRecursive, 0)
        if activation_item:
            self._destination_tree.setCurrentItem(activation_item[0])
            self._toogle_make_connection_button()

    def _add_tree(self, node_item, node_name, short_node_name, attributes):
        """ Creates QTreeWidgetItems for one node and adds it to the parent item.

        Args:
            node_item (:obj:`QTreeWidgetItem`): Tree item to hang new elements. Parent item.
            node_name (str): full path name of the node with the attributes.
            short_node_name (str): short path name of the node with the attributes.
            attributes (list): list of attributes from that node.
        """
        node_element = QtWidgets.QTreeWidgetItem([short_node_name])
        node_element.setToolTip(0, node_name)
        # Remove the ability to select items at node level (sensors, locators, nodes...)
        node_element.setFlags(node_element.flags() & ~QtCore.Qt.ItemIsSelectable)

        for attribute in attributes:
            attribute_element = QtWidgets.QTreeWidgetItem([attribute])
            attribute_element.setFlags(attribute_element.flags()
                                       | QtCore.Qt.ItemIsSelectable)
            node_element.addChild(attribute_element)

        node_item.addChild(node_element)

    def _override_connection(self, node_plug):
        """ Checks if there is a plug already connected to node_plug,
            if that is the case a question dialog is displayed asking
            the user whether to override the connection or not

        Args:
            node_plug (str): Name of the attribute to make the connection,
                             will be the destination of the connection.

        Returns:
            true: If the source plug has to be connected with node_plug.
            false: If the user do not want to override the connection.
        """
        if not cmds.objExists(node_plug):
            return True

        if cmds.connectionInfo(node_plug, isExactDestination=True):
            return msg_box(main_window(), "question",
                           "The destination plug is already connected. "
                           "Do you want to override the connection?")
        return True
