from maya.api import OpenMaya

import mocapx
from mocapx.lib.nodes import delete_node, select_node, scene_selection, list_attrs, find_pose_nodes, connect_attrs, \
    pose_weight_locked, get_pose_weight_connected_attr, list_poselib_nodes
from mocapx.lib.uiutils import scaled, confirm_dialog, show_warning
from mocapx.lib.utils import is_attr_type_valid, get_mobject, adapt_name
from mocapx.ui.widgets import ToolButton
# pylint: disable=no-name-in-module
# noinspection PyUnresolvedReferences
from mocapx.vendor.Qt import QtCore, QtWidgets
# pylint: enable=no-name-in-module


# noinspection SpellCheckingInspection,PyPep8Naming
class PoselibPicker(QtWidgets.QFrame):
    poselib_changed = QtCore.Signal(str)

    def __init__(self, parent=None):
        super(PoselibPicker, self).__init__(parent)

        # State
        self.poselib_nodes = list()
        self.node_added_cbid = None
        self.node_removed_cbid = None
        self.node_rename_cbids = dict()

        # label
        self.label = QtWidgets.QLabel('Poselib:')

        # Dropdown list of poselibs
        self.dropdown = QtWidgets.QComboBox()
        self.dropdown.setInsertPolicy(QtWidgets.QComboBox.InsertAtCurrent)
        size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        self.dropdown.setSizePolicy(size_policy)

        # Auto connect button
        self.auto_connect_button = ToolButton(
            size=(scaled(18), scaled(18)),
            icon_name='MCPXAutoConnect',
            alpha=True,
            icon_size=(scaled(16), scaled(16))
        )
        self.auto_connect_button.setToolTip("Connect Poses to the same named Attributes of selected Node")

        # Select poselib button
        self.select_button = ToolButton(
            size=(scaled(18), scaled(18)),
            icon_name='MCPXSelect',
            alpha=True,
            icon_size=(scaled(16), scaled(16))
        )
        self.select_button.setToolTip("Select Poselib Node")

        # Delete poselib button
        self.delete_button = ToolButton(
            size=(scaled(18), scaled(18)),
            icon_name='MCPXDelete',
            alpha=True,
            icon_size=(scaled(16), scaled(16))
        )
        self.delete_button.setToolTip("Delete Poselib and its Poses")

        # Event handlers
        self.dropdown.currentIndexChanged.connect(self.node_change_handle)
        self.auto_connect_button.clicked.connect(self.auto_connect_handle)
        self.select_button.clicked.connect(self.select_click_handle)
        self.delete_button.clicked.connect(self.delete_click_handle)

        # Layout
        p_layout = QtWidgets.QHBoxLayout()
        p_layout.setContentsMargins(scaled(6), scaled(6), scaled(6), scaled(6))
        p_layout.setSpacing(scaled(6))
        p_layout.addWidget(self.label)
        p_layout.addWidget(self.dropdown)

        b_layout = QtWidgets.QHBoxLayout()
        b_layout.setContentsMargins(scaled(6), scaled(6), scaled(6), scaled(6))
        b_layout.setSpacing(scaled(2))
        b_layout.addWidget(self.auto_connect_button)
        b_layout.addWidget(self.select_button)
        b_layout.addWidget(self.delete_button)

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(scaled(0), scaled(0), scaled(11), scaled(0))
        layout.setSpacing(scaled(6))
        layout.addLayout(p_layout)
        layout.addLayout(b_layout)

        self.setLayout(layout)

        # Setup state according to the node
        # Setup maya callbacks
        self.refresh_state()

    @property
    def selected_item(self):
        return self.dropdown.currentText()

    def add_item(self, item):
        self.dropdown.addItem(item)
        self.poselib_nodes.append(item)

    def rename_item(self, old_name, new_name):
        # since node referenced - in picker it added as node without namespace yet
        # so, it can be named as another one node
        # rename callback has to rename correct item
        # as new item always appended - we search correct item from the end
        index = len(self.poselib_nodes) - self.poselib_nodes[::-1].index(old_name) - 1
        self.dropdown.setItemText(index, new_name)
        self.poselib_nodes[index] = new_name

    def remove_item(self, node_name):
        index = self.poselib_nodes.index(node_name)
        self.dropdown.removeItem(index)
        self.poselib_nodes.remove(node_name)

    def refresh_state(self):
        self.poselib_nodes = list_poselib_nodes()
        # Populate dropdown with poselibs
        self.dropdown.clear()
        if self.poselib_nodes:
            self.dropdown.addItems(self.poselib_nodes)

        # Set callback for a node
        self.clean_callbacks()
        self.node_added_cbid = OpenMaya.MDGMessage.addNodeAddedCallback(
            self.maya_node_created_cb, 'MCPXPoselib')
        self.node_removed_cbid = OpenMaya.MDGMessage.addNodeRemovedCallback(
            self.maya_node_removed_cb, 'MCPXPoselib')
        for node in self.poselib_nodes:
            node_mobject = get_mobject(node)
            if node_mobject:
                rename_cbid = OpenMaya.MNodeMessage.addNameChangedCallback(
                    node_mobject, self.maya_node_name_changed_cb)
                self.node_rename_cbids[node] = rename_cbid

    # HANDLERS
    # noinspection PyMethodMayBeStatic
    def auto_connect_handle(self):
        selection = scene_selection()
        poselib_namespace = self.selected_item.rpartition(':')[0]
        if selection:
            options = ("Reconnect", "Skip")

            selected_node = selection[-1]
            for attr_name in list_attrs(selected_node, connectable=True):
                found = find_pose_nodes(attr_name)
                if found:
                    if poselib_namespace:
                        found = list(filter((lambda el: poselib_namespace in el), found))
                    else:
                        found = list(filter((lambda el: ':' not in el), found))
                    pose_node = found[0]
                    possible_source = selected_node + "." + attr_name

                    if is_attr_type_valid(possible_source):
                        if not pose_weight_locked(pose_node):
                            current_source = get_pose_weight_connected_attr(pose_node)

                            if not current_source:
                                confirm = options[0]
                            else:
                                if possible_source != current_source:
                                    confirm = confirm_dialog(
                                        title="Destination connected",
                                        icon="warning",
                                        message="\"{}\" already driven by \"{}\".".format(
                                            pose_node, current_source),
                                        button=options,
                                        defaultButton=options[0],
                                        cancelButton=options[-1])
                                else:
                                    continue

                            if confirm == options[0]:
                                connect_attrs(possible_source, pose_node + ".weight", verbose=True)
                        else:
                            show_warning(
                                "Connection for locked weight of \"{}\" skipped.".format(pose_node))
                    else:
                        show_warning(
                            "Source attribute \"{}\" has unsupported type. Connection skipped.".format(
                                possible_source))
        else:
            show_warning("Nothing selected.")

    def select_click_handle(self):
        select_node(self.dropdown.currentText())

    def delete_click_handle(self):
        delete_node(self.dropdown.currentText())

    def node_change_handle(self):
        self.poselib_changed.emit(self.selected_item)

    # CALLBACKS
    # noinspection PyArgumentList,PyUnusedLocal
    def maya_node_created_cb(self, node, clientData):
        if not mocapx.suppress_on_scene_loading:
            node_name = OpenMaya.MFnDependencyNode(node).name()
            rename_cbid = OpenMaya.MNodeMessage.addNameChangedCallback(
                node, self.maya_node_name_changed_cb)
            self.node_rename_cbids[node_name] = rename_cbid
            self.add_item(node_name)

    # noinspection PyArgumentList,PyUnusedLocal
    def maya_node_removed_cb(self, node, clientData):
        if not mocapx.suppress_on_scene_loading:
            node_name = OpenMaya.MFnDependencyNode(node).name()
            self.remove_item(node_name)
            OpenMaya.MMessage.removeCallback(self.node_rename_cbids[node_name])
            del self.node_rename_cbids[node_name]

    # noinspection PyArgumentList,PyUnusedLocal
    def maya_node_name_changed_cb(self, node, prev_name, clientData):
        if not mocapx.suppress_on_scene_loading:
            new_name = OpenMaya.MFnDependencyNode(node).name()
            new_name = adapt_name(new_name)
            self.rename_item(prev_name, new_name)
            self.node_rename_cbids[new_name] = self.node_rename_cbids.pop(prev_name)

    # noinspection PyArgumentList
    def clean_callbacks(self):
        if self.node_added_cbid:
            OpenMaya.MMessage.removeCallback(self.node_added_cbid)
            self.node_added_cbid = None
        if self.node_removed_cbid:
            OpenMaya.MMessage.removeCallback(self.node_removed_cbid)
            self.node_removed_cbid = None
        if self.node_rename_cbids:
            for cbid in list(self.node_rename_cbids.values()):
                OpenMaya.MMessage.removeCallback(cbid)
            self.node_rename_cbids = dict()
