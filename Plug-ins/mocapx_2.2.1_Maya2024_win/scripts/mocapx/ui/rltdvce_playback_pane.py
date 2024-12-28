import re

from maya.api import OpenMaya

import mocapx
from mocapx.commands import establish_connection, start_session, break_connection
from mocapx.lib import nodes
from mocapx.lib.utils import get_mobject, get_adapters_where_source_active, switch_data_source
from mocapx.lib.uiutils import RegExValidator, scaled
from mocapx.ui.widgets import ActionButtonsRTD, BaseLineEdit, ToggledSwitcher
# noinspection PyUnresolvedReferences
# pylint: disable=no-name-in-module
from mocapx.vendor.Qt import QtCore, QtWidgets, QtGui


# pylint: enable=no-name-in-module


# noinspection SpellCheckingInspection
class MCPXRealTimeDevicePlaybackPane(QtWidgets.QWidget):
    def __init__(self, node, parent=None):
        super(MCPXRealTimeDevicePlaybackPane, self).__init__(parent)

        # State
        self.node = node
        self.connection_type = nodes.get_realtime_device_conn_type(self.node)
        self.port_value = nodes.get_realtime_device_port(self.node)
        self.ip_value = nodes.get_realtime_device_ip(self.node)
        self.connection_status = nodes.get_realtime_device_conn_status(self.node)
        self.is_live = nodes.get_realtime_device_live(self.node)
        self.save_video_state = nodes.get_realtime_device_save_video(self.node)

        self.attrs_changed_cbid = None
        self.connection_state_changed_cbid = None

        # WiFi - USB Switcher
        self.conn_type_switcher = ToggledSwitcher(
            bold_font=False,
            size=(scaled(60), scaled(40), scaled(20)),
            angle_factor=0.15
        )

        # IP widget
        self.ip_label = QtWidgets.QLabel('IP:')
        self.ip_label.setMinimumWidth(scaled(16))
        self.ip_label.setFixedHeight(scaled(20))
        self.ip_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        self.ip_label.setSizePolicy(size_policy)

        self.ip_field = BaseLineEdit()
        self.ip_field.setMinimumWidth(scaled(90))
        self.ip_field.setAlignment(QtCore.Qt.AlignRight)
        ip_range = r'(?:[0-1]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])'
        self.ip_regex = r'^{}\.{}\.{}\.{}$'.format(ip_range, ip_range, ip_range, ip_range)
        self.ip_field.setValidator(RegExValidator(QtCore.QRegExp(self.ip_regex)))

        # Port widget
        port_label = QtWidgets.QLabel('port:')
        port_label.setMinimumWidth(scaled(30))
        port_label.setFixedHeight(scaled(20))
        port_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        port_label.setSizePolicy(size_policy)

        self.port_field = BaseLineEdit()
        self.port_field.setMinimumWidth(scaled(35))
        self.port_field.setMaximumWidth(scaled(55))

        port_range = r'([0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])'
        self.port_regex = "^" + port_range + "$"
        self.port_field.setValidator(RegExValidator(QtCore.QRegExp(self.port_regex)))

        # Action button
        self.action_buttons = ActionButtonsRTD(pause_state=self.is_live, frame=False)

        # Settings
        self.save_video_check = QtWidgets.QCheckBox("Save Video")

        # Setup handlers
        self.destroyed.connect(self.clean_callbacks)
        self.conn_type_switcher.toggled.connect(self.conn_type_switch_handle)
        self.ip_field.editingFinished.connect(self.ip_changed_handle)
        self.port_field.editingFinished.connect(self.port_changed_handle)
        self.action_buttons.connect_signal.connect(self.connect_handle)
        self.action_buttons.disconnect_signal.connect(self.disconnect_handle)
        self.action_buttons.start_session_signal.connect(self.start_session_handle)
        self.action_buttons.pause_signal.connect(self.toggle_live_handle)
        self.save_video_check.stateChanged.connect(self.save_video_handle)

        # layout widgets
        top_layout = QtWidgets.QHBoxLayout()
        top_layout.setContentsMargins(scaled(6), scaled(6), scaled(6), scaled(6))
        top_layout.setSpacing(scaled(3))
        if mocapx.platform != "Linux":
            top_layout.addWidget(self.conn_type_switcher)
        top_layout.addWidget(self.ip_label)
        top_layout.addWidget(self.ip_field)
        top_layout.addWidget(port_label)
        top_layout.addWidget(self.port_field)
        top_layout.addWidget(self.action_buttons)
        bottom_layout = QtWidgets.QHBoxLayout()
        bottom_layout.setContentsMargins(scaled(148), scaled(0), scaled(0), scaled(0))
        bottom_layout.setSpacing(scaled(6))
        # bottom_layout.addWidget(self.save_video_check)
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(scaled(0), scaled(0), scaled(0), scaled(0))
        layout.setSpacing(scaled(6))
        top_frame = QtWidgets.QFrame()
        top_frame.setLayout(top_layout)
        bottom_frame = QtWidgets.QFrame()
        bottom_frame.setLayout(bottom_layout)
        layout.addWidget(top_frame)
        layout.addWidget(bottom_frame)
        self.setLayout(layout)

        # Setup state according to the node
        # Setup maya callbacks
        self.refresh_state()

    def set_state_for_conn_type(self):
        self.ip_field.setDisabled(self.connection_type)
        self.ip_label.setDisabled(self.connection_type)

        if mocapx.platform != "Linux":
            self.conn_type_switcher.blockSignals(True)
            self.conn_type_switcher.setValue(self.connection_type)
            self.conn_type_switcher.blockSignals(False)

    def set_state_ip(self):
        self.ip_field.setText(str(self.ip_value))

    def set_state_port(self):
        self.port_field.setText(str(self.port_value))

    def set_state_for_pause_button(self):
        self.action_buttons.set_pause_label(self.is_live)

    def set_state_for_conn_status(self):
        self.action_buttons.set_state(self.connection_status)

    def set_state_save_video(self):
        if self.connection_status in (0, 1):
            self.save_video_check.setEnabled(True)
            self.save_video_check.setChecked(self.save_video_state)
        elif self.connection_status in (2, 3):
            self.save_video_check.setEnabled(False)

    def refresh_state(self):
        # Setup pane state
        self.ip_value = nodes.get_realtime_device_ip(self.node)
        self.port_value = nodes.get_realtime_device_port(self.node)
        self.connection_type = nodes.get_realtime_device_conn_type(self.node)
        self.connection_status = nodes.get_realtime_device_conn_status(self.node)
        self.is_live = nodes.get_realtime_device_live(self.node)
        self.save_video_state = nodes.get_realtime_device_save_video(self.node)
        self.set_state_for_conn_status()
        self.set_state_for_pause_button()
        self.set_state_for_conn_type()
        self.set_state_port()
        self.set_state_ip()
        self.set_state_save_video()

        # Set callback for a new node
        self.clean_callbacks()
        node_mobject = get_mobject(self.node)
        if node_mobject:
            self.attrs_changed_cbid = OpenMaya.MNodeMessage.addAttributeChangedCallback(
                node_mobject, self.attrs_changed_cb)

        # Set callback for disconnection from the device
        # It is needs to be set once for specific instance of the pane
        if not self.connection_state_changed_cbid:
            # noinspection PyCallByClass
            self.connection_state_changed_cbid = OpenMaya.MUserEventMessage.addUserEventCallback(
                'MCPXRltDvceConnStatusChanged', self.status_changed_cb)

    # HANDLERS
    def connect_handle(self):
        nodes.set_realtime_device_live(self.node, True)
        if establish_connection(self.node):
            for adapter in get_adapters_where_source_active(self.node):
                switch_data_source(self.node, adapter)

    def disconnect_handle(self):
        nodes.set_realtime_device_live(self.node, True)
        break_connection(self.node)

    def start_session_handle(self):
        start_session(self.node)

    def toggle_live_handle(self):
        if nodes.get_realtime_device_live(self.node):
            nodes.set_realtime_device_live(self.node, False)
        else:
            nodes.set_realtime_device_live(self.node, True)

    def conn_type_switch_handle(self):
        nodes.set_realtime_device_conn_type(self.node, self.conn_type_switcher.value)

    def ip_changed_handle(self):
        new_val = self.ip_field.text()
        if re.match(self.ip_regex, new_val):
            nodes.set_realtime_device_ip(self.node, new_val)
        else:
            self.set_state_ip()

    def port_changed_handle(self):
        new_val = self.port_field.text()
        if re.match(self.port_regex, new_val):
            nodes.set_realtime_device_port(self.node, int(new_val))
        else:
            self.set_state_port()

    def save_video_handle(self):
        nodes.set_realtime_device_save_video(self.node, self.save_video_check.isChecked())

    # CALLBACKS
    # noinspection PyUnusedLocal,PyPep8Naming
    def attrs_changed_cb(self, msg, plug, otherplug, clientData):
        attr_name = plug.partialName(includeNodeName=False)
        if msg & OpenMaya.MNodeMessage.kAttributeSet and attr_name == 'ipAddress':
            self.ip_value = nodes.get_realtime_device_ip(self.node)
            self.set_state_ip()
        elif msg & OpenMaya.MNodeMessage.kAttributeSet and attr_name in ('wifiPort', 'usbPort'):
            port_value = nodes.get_realtime_device_port(self.node)
            if port_value != self.port_value:
                self.port_value = port_value
                self.set_state_port()
        elif msg & OpenMaya.MNodeMessage.kAttributeSet and attr_name == 'connectionType':
            conn_type = nodes.get_realtime_device_conn_type(self.node)
            if conn_type != self.connection_type:
                self.connection_type = conn_type
                self.set_state_for_conn_type()
                self.port_value = nodes.get_realtime_device_port(self.node)
                self.set_state_port()
        elif msg & OpenMaya.MNodeMessage.kAttributeSet and attr_name in ("rv", "recordVideo"):
            save_video_state = nodes.get_realtime_device_save_video(self.node)
            if save_video_state != self.save_video_state:
                self.save_video_state = save_video_state
                self.set_state_save_video()
        elif msg & OpenMaya.MNodeMessage.kAttributeSet and attr_name in ("lv", "live"):
            self.is_live = nodes.get_realtime_device_live(self.node)
            self.set_state_for_pause_button()

    # noinspection PyUnusedLocal
    def status_changed_cb(self, data):
        status = nodes.get_realtime_device_conn_status(self.node)
        if status != self.connection_status:
            self.connection_status = status
            self.set_state_for_conn_status()
            self.set_state_save_video()
            if status == 1:
                start_session(self.node)

    def clean_callbacks(self):
        if self.attrs_changed_cbid:
            OpenMaya.MMessage.removeCallback(self.attrs_changed_cbid)
