from maya.api import OpenMaya

from mocapx.lib import nodes
from mocapx.lib.utils import get_mobject, adapt_name
from mocapx.lib.uiutils import scaled, get_widget, generate_style_sheet, get_indicator_color_from_plug
from mocapx.ui.attribute_outliner import AttributeOutlinerHolder
from mocapx.ui.widgets import ToolButton, DynamicSlider, BaseLineEdit, FrameArea
# pylint: disable=no-name-in-module
# noinspection PyUnresolvedReferences
from mocapx.vendor.Qt import QtCore, QtWidgets, QtGui


# noinspection SpellCheckingInspection
class PoseWeightPane(FrameArea):
    def __init__(self, pose_node, parent=None):
        super(PoseWeightPane, self).__init__(parent)

        # State
        self.node = pose_node
        self.connected_plug = None
        self.weight_value = None
        self.weight_locked = None
        self.mute_value = None
        self.mute_locked = None

        self.node_renamed_cbid = None
        self.node_attr_changed_cbid = None

        # Weight edit
        self.weight_edit = BaseLineEdit(select_all_by_DoubleClick=True)
        self.weight_edit.setTextMargins(scaled(3), scaled(0), scaled(0), scaled(0))
        self.weight_edit.setToolTip("Set Pose Weight")
        self.weight_edit.setFixedSize(scaled(58), scaled(18))
        self.weight_edit.set_float_validator()
        self.weight_edit_select_connection_action = self.weight_edit.add_action()
        self.weight_edit_connect_action = self.weight_edit.add_action("Set Connection...")
        self.weight_edit_disconnect_action = self.weight_edit.add_action("Break Connection")
        self.weight_edit_lock_action = self.weight_edit.add_action("Lock Attribute")
        self.weight_edit_unlock_action = self.weight_edit.add_action("Unlock Attribute")

        # Weight slider
        self.weight_slider = DynamicSlider(QtCore.Qt.Horizontal)

        self.mute_button = ToolButton(
            size=(scaled(18), scaled(18)),
            icon_name='MCPXMute',
            alpha=True,
            icon_size=(scaled(16), scaled(16)),
            toggle=True
        )
        self.mute_button.setToolTip("Mute Pose")
        self.mute_button_lock_action = self.mute_button.add_action("Lock Attribute")
        self.mute_button_unlock_action = self.mute_button.add_action("Unlock Attribute")

        # Event handlers
        self.mute_button.toggled.connect(self.mute_handle)
        self.weight_edit.editingFinished.connect(self.edit_change_handle)
        self.weight_edit_select_connection_action.triggered.connect(self.select_connected_handle)
        self.weight_edit_connect_action.triggered.connect(self.connect_handle)
        self.weight_edit_disconnect_action.triggered.connect(self.disconnect_handle)
        self.weight_edit_lock_action.triggered.connect(self.lock_weight_handle)
        self.weight_edit_unlock_action.triggered.connect(self.unlock_weight_handle)
        self.weight_slider.valueChanged.connect(self.slider_change_handle)
        self.weight_slider.weight_min_set.connect(self.weight_min_change_handle)
        self.weight_slider.weight_max_set.connect(self.weight_max_change_handle)
        self.mute_button_lock_action.triggered.connect(self.lock_mute_handle)
        self.mute_button_unlock_action.triggered.connect(self.unlock_mute_handle)

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(scaled(16), scaled(10), scaled(0), scaled(10))
        layout.setSpacing(scaled(6))
        layout.addWidget(self.weight_slider)
        layout.addWidget(self.weight_edit)
        layout.addWidget(self.mute_button)
        self.setLayout(layout)

        self.setFixedWidth(scaled(382))

        # Setup state according to the node
        # Setup maya callbacks
        self.refresh_state()

    # noinspection PyMethodMayBeStatic
    def _format_preview(self, value):
        return "{:.4f}".format(value)

    def set_state_weight_color(self):
        settings = get_indicator_color_from_plug(self.node + ".weight")
        settings.update({"border": "none", "border-radius": "{}px".format(scaled(2))})
        self.weight_edit.setStyleSheet(
            generate_style_sheet("QLineEdit", settings)
        )

    def set_state_weight_actions(self):
        state_1 = state_2 = False
        if not self.weight_locked:
            if self.connected_plug:
                self.weight_edit_select_connection_action.setText(self.connected_plug + "...")
                state_1 = True
            else:
                self.weight_edit_select_connection_action.setText("")
                state_2 = True
        self.weight_edit_select_connection_action.setVisible(state_1)
        self.weight_edit_connect_action.setVisible(state_2)
        self.weight_edit_disconnect_action.setVisible(state_1)

    def set_state_connected(self):
        if self.connected_plug:
            self.weight_slider.set_blocked(True)
        else:
            self.weight_slider.set_blocked(False)

    def set_state_weight_value(self):
        self.weight_slider.blockSignals(True)
        self.weight_edit.blockSignals(True)
        self.weight_slider.setValue(self.weight_value)
        self.weight_edit.setText(self._format_preview(self.weight_value))
        self.weight_slider.blockSignals(False)
        self.weight_edit.blockSignals(False)

    def set_state_weight_lock(self):
        if not self.weight_locked:
            self.weight_edit.setReadOnly(False)
            self.weight_edit_lock_action.setVisible(True)
            self.weight_edit_unlock_action.setVisible(False)
            self.weight_slider.setEnabled(True)
        else:
            self.weight_edit.setReadOnly(True)
            self.weight_edit_unlock_action.setVisible(True)
            self.weight_edit_lock_action.setVisible(False)
            self.weight_slider.setEnabled(False)

    def set_state_mute_value(self):
        self.mute_button.setChecked(self.mute_value)

    def set_state_mute_lock(self):
        if not self.mute_locked:
            self.mute_button.setEnabled(True)
            self.mute_button_lock_action.setVisible(True)
            self.mute_button_unlock_action.setVisible(False)
        else:
            self.mute_button.setEnabled(False)
            self.mute_button_lock_action.setVisible(False)
            self.mute_button_unlock_action.setVisible(True)

    def refresh_connected_plug(self):
        if nodes.pose_weight_has_connection(self.node):
            self.connected_plug = nodes.get_pose_weight_connected_attr(self.node)
        else:
            self.connected_plug = None

    def refresh_state(self):
        # Set callback for a node
        self.clean_callbacks()

        self.weight_value = nodes.get_pose_weight(self.node)
        self.weight_locked = nodes.pose_weight_locked(self.node)
        self.mute_value = nodes.get_mute_pose(self.node)
        self.mute_locked = nodes.if_pose_mute_locked(self.node)
        self.refresh_connected_plug()

        # this pose node callbacks
        node_mobject = get_mobject(self.node)
        if node_mobject:
            self.node_renamed_cbid = OpenMaya.MNodeMessage.addNameChangedCallback(
                node_mobject, self.maya_node_name_changed_cb)
            self.node_attr_changed_cbid = OpenMaya.MNodeMessage.addAttributeChangedCallback(
                node_mobject, self.node_attr_changed_cb)

        # Set UI state
        self.set_state_weight_value()
        self.set_state_weight_lock()
        self.set_state_connected()
        self.set_state_weight_color()
        self.set_state_weight_actions()
        self.set_state_mute_value()
        self.set_state_mute_lock()

        self.weight_slider.setRange(
            nodes.get_pose_weight_min(self.node),
            nodes.get_pose_weight_max(self.node))

    # HANDLERS
    def connect_handle(self):
        AttributeOutlinerHolder.display_pane('{}.weight'.format(self.node))

    def disconnect_handle(self):
        connected_plug = nodes.get_pose_weight_connected_attr(self.node)
        if connected_plug:
            nodes.disconnect_attrs(connected_plug, '{}.weight'.format(self.node), verbose=True)
            self.set_state_weight_value()

    def lock_weight_handle(self):
        nodes.lock_attribute(self.node + ".weight", True, verbose=True)

    def unlock_weight_handle(self):
        nodes.lock_attribute(self.node + ".weight", False, verbose=True)

    def lock_mute_handle(self):
        nodes.lock_attribute(self.node + ".mute", True, verbose=True)

    def unlock_mute_handle(self):
        nodes.lock_attribute(self.node + ".mute", False, verbose=True)

    def slider_change_handle(self):
        if not nodes.pose_weight_has_connection(self.node) and not nodes.pose_weight_locked(self.node):
            value = float(self.weight_slider.value())
            nodes.change_pose_weight(self.node, value)

    def weight_min_change_handle(self, value):
        if not nodes.set_pose_weight_min(self.node, value, force=False):
            self.weight_slider.setMinimum(value)

    def weight_max_change_handle(self, value):
        if not nodes.set_pose_weight_max(self.node, value, force=False):
            self.weight_slider.setMaximum(value)

    def edit_change_handle(self):
        text = self.weight_edit.text()
        if self._format_preview(self.weight_value) != text:
            try:
                value = float(text)
            except ValueError:
                pass
            else:
                if nodes.change_pose_weight(self.node, value, force=False, verbose=True):
                    return
        self.set_state_weight_value()

    def select_connected_handle(self):
        if self.connected_plug and '.' in self.connected_plug:
            node = self.connected_plug.split('.')[0]
            nodes.select_node(node)

    def mute_handle(self, checked):
        nodes.set_mute_pose(self.node, checked, force=False, verbose=True)

    # CALLBACKS
    # noinspection PyArgumentList,PyUnusedLocal,PyPep8Naming
    def maya_node_name_changed_cb(self, node, prev_name, clientData):
        new_name = OpenMaya.MFnDependencyNode(node).name()
        new_name = adapt_name(new_name)
        self.node = new_name

    # noinspection PyArgumentList,PyUnusedLocal,PyPep8Naming
    def node_attr_changed_cb(self, msg, plug, otherplug, clientData):
        attr_name = plug.partialName(includeNodeName=False)
        if msg & OpenMaya.MNodeMessage.kAttributeSet:
            if attr_name == 'weight':
                self.weight_value = nodes.get_pose_weight(self.node)
                if self.weight_value > nodes.get_pose_weight_max(self.node):
                    nodes.set_pose_weight_max(self.node, self.weight_value)
                elif self.weight_value < nodes.get_pose_weight_min(self.node):
                    nodes.set_pose_weight_min(self.node, self.weight_value)
                self.set_state_weight_value()
            elif attr_name == 'weight_min':
                _min = nodes.get_pose_weight_min(self.node)
                self.weight_slider.setMinimum(_min)
                _max = nodes.get_pose_weight_max(self.node)
                if _max <= _min:
                    nodes.set_pose_weight_max(self.node, _max + 0.01)
            elif attr_name == 'weight_max':
                _max = nodes.get_pose_weight_max(self.node)
                self.weight_slider.setMaximum(_max)
                _min = nodes.get_pose_weight_min(self.node)
                if _min >= _max:
                    nodes.set_pose_weight_min(self.node, _max - 0.01)
            elif attr_name == 'mute':
                self.mute_value = nodes.get_mute_pose(self.node)
                self.set_state_mute_value()
        elif msg & OpenMaya.MNodeMessage.kConnectionMade or msg & OpenMaya.MNodeMessage.kConnectionBroken:
            if attr_name == "weight":
                self.refresh_connected_plug()
                self.set_state_connected()
                self.set_state_weight_actions()
                self.set_state_weight_color()
        elif msg & OpenMaya.MNodeMessage.kAttributeLocked or msg & OpenMaya.MNodeMessage.kAttributeUnlocked:
            if attr_name == 'weight':
                self.weight_locked = nodes.pose_weight_locked(self.node)
                self.set_state_weight_lock()
                self.set_state_weight_color()
                self.set_state_weight_actions()
            elif attr_name == 'mute':
                self.mute_locked = nodes.if_pose_mute_locked(self.node)
                self.set_state_mute_lock()

    def clean_callbacks(self):
        if self.node_renamed_cbid:
            OpenMaya.MMessage.removeCallback(self.node_renamed_cbid)
        if self.node_attr_changed_cbid:
            OpenMaya.MMessage.removeCallback(self.node_attr_changed_cbid)


# noinspection PyUnusedLocal
def pose_create_view(parent, weight, weight_min, weight_max):
    node = weight.split('.')[0]
    ae_widget = get_widget(parent)
    ae_layout = ae_widget.layout()
    pose_pane = PoseWeightPane(node)
    ae_layout.addWidget(pose_pane)


# noinspection PyUnusedLocal
def pose_update_view(parent, weight, weight_min, weight_max, prev_uuid):
    ae_widget = get_widget(parent)
    ae_layout = ae_widget.layout()
    pose_pane_widget = None
    for c in range(ae_layout.count()):
        pose_pane_widget = ae_layout.itemAt(c).widget()
        if isinstance(pose_pane_widget, PoseWeightPane):
            break
    node = weight.split('.')[0]
    if pose_pane_widget:
        if nodes.get_node_uuid(node) != prev_uuid or \
                node != pose_pane_widget.node or \
                nodes.get_pose_weight(node) != pose_pane_widget.weight_value or \
                bool(nodes.get_pose_weight_connected_attr(node)) != bool(pose_pane_widget.connected_plug) or \
                nodes.pose_weight_locked(node) != pose_pane_widget.weight_locked or \
                nodes.get_pose_weight_min(node) != pose_pane_widget.weight_slider.minimum() or \
                nodes.get_pose_weight_max(node) != pose_pane_widget.weight_slider.maximum() or \
                nodes.get_mute_pose(node) != pose_pane_widget.mute_value or \
                nodes.if_pose_mute_locked(node) != pose_pane_widget.mute_locked:
            pose_pane_widget.node = node
            pose_pane_widget.refresh_state()
