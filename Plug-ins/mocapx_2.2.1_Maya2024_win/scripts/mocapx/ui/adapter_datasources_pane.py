from maya.api import OpenMaya

import mocapx.commands as mcpx_cmds
from mocapx.lib import nodes
from mocapx.lib.utils import get_mobject
# pylint: enable=no-name-in-module
# noinspection PyUnresolvedReferences
from mocapx.vendor.Qt import QtWidgets
# pylint: disable=no-name-in-module
from mocapx.ui.datasource_pane import DataSourcePane, DataSourceAddPane
from mocapx.ui.widgets import ContainerDrag
from mocapx.lib.uiutils import COLOR_GROUPS, scaled, set_color_palette_darker


# noinspection SpellCheckingInspection
class MCPXAdapterDataSourcesPane(QtWidgets.QWidget):
    def __init__(self, node, parent=None):
        super(MCPXAdapterDataSourcesPane, self).__init__(parent)

        # Watching if new data sources is connected or changing of active data source
        self.data_source_watcher_callback_id = None

        self.node = node
        self.sources = list()
        self.active_data_source = None

        self.sources_pane = ContainerDrag(self.sources, DataSourcePane)
        for c_group in COLOR_GROUPS:
            set_color_palette_darker(self.sources_pane, c_role="Background", c_group=c_group, factor=121)

        self.sources_addPane = DataSourceAddPane()

        self.sources_addPane.add_clipreader.connect(self.add_clipreader_command)
        self.sources_addPane.add_realtime_device.connect(self.add_realtime_device_command)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(scaled(6), scaled(6), scaled(6), scaled(6))
        layout.setSpacing(scaled(6))
        layout.addWidget(self.sources_pane)
        layout.addWidget(self.sources_addPane)
        self.setLayout(layout)

        self.refresh_state()

    def add_clipreader_command(self):
        mcpx_cmds.create_clipreader(adapter_name=self.node)

    def add_realtime_device_command(self):
        mcpx_cmds.create_realtime_device(adapter_name=self.node)

    def clean_callbacks(self):
        if self.data_source_watcher_callback_id:
            OpenMaya.MMessage.removeCallback(self.data_source_watcher_callback_id)
            self.data_source_watcher_callback_id = None

    def set_maya_callbacks(self):
        self.clean_callbacks()
        if self.node:
            node_mobject = get_mobject(self.node)
            if node_mobject:
                self.data_source_watcher_callback_id = OpenMaya.MNodeMessage.addAttributeChangedCallback(
                    node_mobject, self.datasources_changed_callback)
        else:
            self.data_source_watcher_callback_id = None

    def renamed_source_handle(self, old_name, new_name):
        self.sources[self.sources.index(old_name)] = new_name
        self.set_order_attribute()
        self.sources_pane.items_dict[new_name] = self.sources_pane.items_dict[old_name]
        del self.sources_pane.items_dict[old_name]

        if old_name == self.active_data_source:
            self.active_data_source = new_name

    def set_active_source_change_handle(self, data_source_node):
        if self.active_data_source != data_source_node:
            nodes.set_active_source(self.node, data_source_node)

    # noinspection PyUnusedLocal
    def set_order_attribute(self, *args, **kwargs):
        return nodes.set_order_list(self.node, self.sources, force=False)

    def refresh_order_state(self):
        # according to widgets order
        self.sources = list()
        inv_map = {v: k for k, v in self.sources_pane.items_dict.items()}
        for widget in self.sources_pane.items:
            self.sources.append(inv_map[widget])
        self.set_order_attribute()

    def refresh_state(self):
        self.sources = nodes.sort_nodes_by_order(
            nodes.get_adapter_sources(self.node),
            nodes.get_order_list(self.node),
            self.node.rpartition(":")[0])
        self.set_order_attribute()

        self.sources_pane.replace_content(self.sources)

        # Connect handlers
        for source_pane in self.sources_pane.items:
            source_pane.source_renamed.connect(self.renamed_source_handle)
            source_pane.source_selected.connect(self.set_active_source_change_handle)
            source_pane.drag_finished.connect(self.refresh_order_state)

        self.active_data_source = nodes.get_active_data_source(self.node)
        if self.active_data_source:
            if self.active_data_source in self.sources_pane.items_dict:
                self.sources_pane.items_dict[self.active_data_source].set_active(True)

        self.set_maya_callbacks()

    # noinspection PyUnusedLocal,PyPep8Naming
    def datasources_changed_callback(self, msg, plug, otherplug, clientData):
        otherplug_node = str(otherplug.partialName(includeNodeName=True)).split('.')[0]
        plug_name = str(plug.partialName(includeNodeName=True, useLongNames=True)).split('.')[1]
        if msg & OpenMaya.MNodeMessage.kConnectionMade:
            if plug_name == 'activeSource':
                old_active = self.active_data_source
                self.active_data_source = otherplug_node
                if old_active:
                    self.sources_pane.items_dict[old_active].set_active(False)
                self.sources_pane.items_dict[self.active_data_source].set_active(True)
            elif plug_name == 'dnSetMembers':
                if nodes.if_data_source(otherplug_node):
                    if otherplug_node not in self.sources:
                        source_pane = self.sources_pane.add_item(otherplug_node)
                        source_pane.source_renamed.connect(self.renamed_source_handle)
                        source_pane.source_selected.connect(self.set_active_source_change_handle)
                        source_pane.drag_finished.connect(self.refresh_order_state)
                        self.sources.append(otherplug_node)
                        self.set_order_attribute()
        elif msg & OpenMaya.MNodeMessage.kConnectionBroken:
            if plug_name == 'dnSetMembers':
                if nodes.if_data_source(otherplug_node):
                    if otherplug_node in self.sources:
                        self.sources_pane.remove_item(otherplug_node)
                        self.sources.remove(otherplug_node)
                        self.set_order_attribute()
                    if otherplug_node == self.active_data_source:
                        self.active_data_source = None
