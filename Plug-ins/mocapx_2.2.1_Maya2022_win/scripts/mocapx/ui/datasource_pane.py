from maya.api import OpenMaya

from mocapx.commands import establish_connection, start_session, break_connection
from mocapx.lib import nodes
# pylint: disable=no-name-in-module
# noinspection PyUnresolvedReferences
from mocapx.vendor.Qt import QtWidgets, QtGui, QtCore
# pylint: enable=no-name-in-module
from mocapx.ui.widgets import ToolButton, FrameArea, LineEditStyled, ActionButtonsRTD, ActionButtonsClip
from mocapx.lib.utils import get_mobject, adapt_name, get_adapters_where_source_active, switch_data_source, \
    clipreader_load_clip
from mocapx.lib.uiutils import COLOR_GROUPS, scaled, set_color_palette_lighter, get_application_palette, \
    show_warning


# noinspection SpellCheckingInspection
class DataSourcePane(FrameArea):
    source_renamed = QtCore.Signal(str, str)
    source_selected = QtCore.Signal(str)

    drag_started = QtCore.Signal(object, QtCore.QPoint, float, float)
    drag_moved = QtCore.Signal(QtCore.QPoint, float)
    drag_finished = QtCore.Signal()

    def __init__(self, source_node, parent=None):
        super(DataSourcePane, self).__init__(parent)

        self.source_node = source_node

        if nodes.if_clipreader_node(self.source_node):
            self.source_node_type = 'clipreader'
        elif nodes.realtime_device_node(self.source_node):
            self.source_node_type = 'realtime'
        else:
            raise AttributeError('Unknown data source node {}.'.format(source_node))

        self.connected_plug = None
        self.connection_status = nodes.get_realtime_device_conn_status(self.source_node)
        self.is_live = nodes.get_realtime_device_live(self.source_node)

        # Indicator area
        self.indicator_area = FrameArea()
        self.indicator_area.setFixedWidth(scaled(7))

        # Data source name widget
        self.label = LineEditStyled(source_node, check_command=lambda: not nodes.is_node_read_only(self.source_node))

        # Source select button
        # TODO: Put generic MocapX icon by default
        if self.source_node_type == 'clipreader':
            source_select_button_icon = 'MCPXClipReader'
        elif self.source_node_type == 'realtime':
            source_select_button_icon = 'MCPXRealTimeDevice'
        else:
            source_select_button_icon = 'MCPXClipReader'

        self.source_select_button = ToolButton(
            size=(scaled(34), scaled(34)),
            icon_name=source_select_button_icon,
            icon_size=(scaled(32), scaled(32)),
            toggle=False
        )

        self.select_button = ToolButton(
            size=(scaled(18), scaled(18)),
            icon_name='MCPXSelect',
            alpha=True,
            icon_size=(scaled(16), scaled(16))
        )
        self.delete_button = ToolButton(
            size=(scaled(18), scaled(18)),
            icon_name='MCPXDelete',
            alpha=True,
            icon_size=(scaled(16), scaled(16))
        )

        # Optional buttons
        if self.source_node_type == 'realtime':
            self.optional_buttons = ActionButtonsRTD(self.connection_status, self.is_live)
            self.optional_buttons.connect_signal.connect(self.connect_handle)
            self.optional_buttons.disconnect_signal.connect(self.disconnect_handle)
            self.optional_buttons.start_session_signal.connect(self.start_session_handle)
            self.optional_buttons.pause_signal.connect(self.toggle_live_handle)
        else:
            self.file_dialog = QtWidgets.QFileDialog(
                parent=self,
                caption="Select MocapX clip",
                directory=nodes.get_project_directory(),
                filter="MocapX Clips (*{})".format(".mcpx"))
            self.file_dialog.setOptions(QtWidgets.QFileDialog.DontUseNativeDialog)
            self.file_dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptOpen)

            self.optional_buttons = ActionButtonsClip()
            self.optional_buttons.browse_signal.connect(self.browse_clip_handle)
            self.optional_buttons.reload_signal.connect(self.reload_clip_handle)
            self.set_state_clip_reload_button()

        # Event handlers
        self.indicator_area.mouse_pressed.connect(self.select_source_handler)
        self.source_select_button.clicked.connect(self.select_source_handler)
        self.mouse_pressed.connect(self.mouse_pressed_handle)
        self.mouse_moved.connect(self.mouse_moved_handle)
        self.mouse_released.connect(self.mouse_released_handle)
        self.label.mouse_pressed.connect(self.mouse_pressed_handle)
        self.label.mouse_moved.connect(self.mouse_moved_handle)
        self.label.mouse_released.connect(self.mouse_released_handle)
        self.label.editingFinished.connect(self.rename_pose_handle)
        self.label.edit_restricted.connect(self.rename_restricted_handle)
        self.select_button.clicked.connect(self.select_handler)
        self.delete_button.clicked.connect(self.delete_handler)

        # Maya callbacks
        self.node_renamed_cbid = None
        self.connection_state_changed_cbid = None
        self.attr_changed_cbid = None
        self.set_maya_callbacks()

        # layout
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(scaled(2), scaled(0), scaled(2), scaled(0))
        layout.setSpacing(scaled(4))
        layout.addWidget(self.source_select_button)
        layout.addWidget(self.label)
        layout.addWidget(self.optional_buttons)
        layout.addItem(QtWidgets.QSpacerItem(scaled(4), scaled(1)))
        layout.addWidget(self.select_button)
        layout.addWidget(self.delete_button)

        complete_layout = QtWidgets.QHBoxLayout()
        complete_layout.setContentsMargins(scaled(0), scaled(0), scaled(0), scaled(0))
        complete_layout.setSpacing(scaled(0))
        complete_layout.addWidget(self.indicator_area)
        complete_layout.addLayout(layout)

        self.setLayout(complete_layout)

        self.setPalette(get_application_palette())
        for c_group in COLOR_GROUPS:
            set_color_palette_lighter(self, c_role="Background", c_group=c_group, factor=107)

        self.set_active(False)

    def set_maya_callbacks(self):
        if self.source_node_type == "realtime":
            if not self.connection_state_changed_cbid:
                # noinspection PyCallByClass
                self.connection_state_changed_cbid = OpenMaya.MUserEventMessage.addUserEventCallback(
                    'MCPXRltDvceConnStatusChanged', self.status_changed_cb)

        node_mobject = get_mobject(self.source_node)
        if node_mobject:
            self.node_renamed_cbid = OpenMaya.MNodeMessage.addNameChangedCallback(
                node_mobject, self.maya_node_name_changed_cb)
            if not self.attr_changed_cbid:
                self.attr_changed_cbid = OpenMaya.MNodeMessage.addAttributeChangedCallback(
                    node_mobject, self.attr_changed_cb)

    def clean_callbacks(self):
        if self.node_renamed_cbid:
            OpenMaya.MMessage.removeCallback(self.node_renamed_cbid)
        if self.connection_state_changed_cbid:
            OpenMaya.MMessage.removeCallback(self.connection_state_changed_cbid)
        if self.attr_changed_cbid:
            OpenMaya.MMessage.removeCallback(self.attr_changed_cbid)

    # noinspection PyArgumentList,PyUnusedLocal
    def status_changed_cb(self, data):
        status = nodes.get_realtime_device_conn_status(self.source_node)
        if status != self.connection_status:
            self.optional_buttons.set_state(status)
            self.connection_status = status

    # noinspection PyPep8Naming,PyUnusedLocal
    def maya_node_name_changed_cb(self, node, prev_name, clientData):
        new_name = OpenMaya.MFnDependencyNode(node).name()
        new_name = adapt_name(new_name)
        self.source_node = new_name
        self.label.setText(new_name)
        self.source_renamed.emit(prev_name, new_name)

    # noinspection PyPep8Naming,PyUnusedLocal
    def attr_changed_cb(self, msg, plug, otherplug, clientData):
        attr_name = plug.partialName(includeNodeName=False)

        if self.source_node_type == "realtime":
            if attr_name in ("lv", "live"):
                if msg & OpenMaya.MNodeMessage.kAttributeSet:
                    self.is_live = nodes.get_realtime_device_live(self.source_node)
                    self.optional_buttons.set_pause_label(self.is_live)
        else:
            if attr_name == "clipFilepath":
                if msg & OpenMaya.MNodeMessage.kAttributeSet or \
                        msg & OpenMaya.MNodeMessage.kConnectionMade or \
                        msg & OpenMaya.MNodeMessage.kConnectionBroken:
                    self.set_state_clip_reload_button()

    def mouse_pressed_handle(self, event, widget):
        if not hasattr(widget, "edit_mode") or not widget.edit_mode:
            if event.buttons() == QtCore.Qt.LeftButton:
                self.raise_()
                self.drag_started.emit(self, event.pos(), self.geometry().y(), event.globalY())

    def mouse_moved_handle(self, event, widget):
        if not hasattr(widget, "edit_mode") or not widget.edit_mode:
            if event.buttons() == QtCore.Qt.LeftButton:
                self.drag_moved.emit(event.pos(), event.globalY())

    # noinspection PyUnusedLocal
    def mouse_released_handle(self, event, widget):
        if not hasattr(widget, "edit_mode") or not widget.edit_mode:
            self.drag_finished.emit()

    def rename_restricted_handle(self):
        show_warning("\"{}\" is locked or referenced and cannot be renamed.".format(self.source_node))

    def rename_pose_handle(self):
        try:
            nodes.rename_node(self.source_node, self.label.text())
        except:
            self.label.setText(self.source_node)

    def select_source_handler(self):
        self.source_selected.emit(self.source_node)

    def select_handler(self):
        nodes.select_node(self.source_node)

    def delete_handler(self):
        nodes.delete_node(self.source_node)

    def connect_handle(self):
        nodes.set_realtime_device_live(self.source_node, True)
        if establish_connection(self.source_node):
            for adapter in get_adapters_where_source_active(self.source_node):
                switch_data_source(self.source_node, adapter)

    def disconnect_handle(self):
        nodes.set_realtime_device_live(self.source_node, True)
        break_connection(self.source_node)

    def start_session_handle(self):
        start_session(self.source_node)

    def toggle_live_handle(self):
        if nodes.get_realtime_device_live(self.source_node):
            nodes.set_realtime_device_live(self.source_node, False)
        else:
            nodes.set_realtime_device_live(self.source_node, True)

    def browse_clip_handle(self):
        if self.file_dialog.exec_():
            filepath = self.file_dialog.selectedFiles()[0]
            nodes.set_clip_reader_path(self.source_node, filepath)
            self.reload_clip_handle()

    def reload_clip_handle(self):
        clipreader_load_clip(
            self.source_node,
            nodes.get_clip_reader_path(self.source_node))

    def set_state_clip_reload_button(self):
        state = bool(nodes.get_clip_reader_path(self.source_node))
        self.optional_buttons.reload_button.setVisible(state)

    def set_active(self, state):
        if state:
            color = (82, 133, 166)
        else:
            color = (37, 37, 37)
        self.indicator_area.setStyleSheet(
            "QFrame {{background-color: rgb{}}}".format(color))
        self.optional_buttons.setVisible(state)


# noinspection SpellCheckingInspection
class DataSourceAddPane(QtWidgets.QFrame):
    add_clipreader = QtCore.Signal()
    add_realtime_device = QtCore.Signal()

    def __init__(self, parent=None):
        super(DataSourceAddPane, self).__init__(parent)

        self.add_realtime_device_button = ToolButton(
            size=(scaled(160), scaled(26)),
            icon_name='MCPXRealTimeDevice',
            icon_size=(scaled(24), scaled(24)),
            label="+ RealTimeDevice"
        )
        self.add_realtime_device_button.clicked.connect(self.add_realtime_device_handler)

        self.add_clipreader_button = ToolButton(
            size=(scaled(160), scaled(26)),
            icon_name='MCPXClipReader',
            icon_size=(scaled(24), scaled(24)),
            label="+ ClipReader"
        )
        self.add_clipreader_button.clicked.connect(self.add_clipreader_handler)

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(scaled(6), scaled(6), scaled(6), scaled(6))
        layout.setSpacing(scaled(6))
        layout.addWidget(self.add_realtime_device_button)
        layout.addWidget(self.add_clipreader_button)
        self.setLayout(layout)

    def add_clipreader_handler(self):
        self.add_clipreader.emit()

    def add_realtime_device_handler(self):
        self.add_realtime_device.emit()
