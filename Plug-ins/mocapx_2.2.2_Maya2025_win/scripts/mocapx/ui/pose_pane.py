from maya.api import OpenMaya
import maya.mel as mel

from mocapx.lib import nodes
from mocapx.commands import update_plugs_in_pose, update_controls_in_pose
from mocapx.lib.control_watcher import get_scene_watcher
from mocapx.lib.utils import get_mobject, get_selected_attrs, adapt_name
from mocapx.lib.uiutils import COLOR_GROUPS, scaled, generate_style_sheet, get_indicator_color_from_plug, \
    set_color_palette_lighter, set_color_palette_darker, \
    get_application_palette, show_warning
from mocapx.ui.attribute_outliner import AttributeOutlinerHolder
from mocapx.ui.pose_attr_pane import AttrViewPane
from mocapx.ui.widgets import ToolButton, DynamicSlider, BaseLineEdit, LineEditStyled, FrameArea, \
    ArrowRadioButton
# pylint: disable=no-name-in-module
# noinspection PyUnresolvedReferences
from mocapx.vendor.Qt import QtCore, QtWidgets, QtGui
# pylint: enable=no-name-in-module


# noinspection SpellCheckingInspection
class PosePane(FrameArea):
    change_pose_weight = QtCore.Signal(str, float)
    solo_pose = QtCore.Signal(str, bool)
    mute_pose = QtCore.Signal(str, bool)
    pose_renamed = QtCore.Signal(str, str)

    drag_started = QtCore.Signal(object, QtCore.QPoint, float, float)
    drag_moved = QtCore.Signal(QtCore.QPoint, float)
    drag_finished = QtCore.Signal()

    clicked = QtCore.Signal(object)

    @staticmethod
    def plug_name_changed(wgt, new_name):
        plug = wgt.connected_plug.partition('.')[2]
        wgt.connected_plug = '{}.{}'.format(new_name, plug)
        wgt.set_state_connected()

    @staticmethod
    def get_plug_value_changed(attr):
        def callback(wgt, clean=False):
            dirty = not clean
            attr_index = wgt.pose_attrs.index(attr)
            if attr_index < len(wgt.dirty_vector):
                wgt.dirty_vector[attr_index] = dirty

                if wgt.attr_view_pane:
                    wgt.attr_view_pane.refresh_dirty_vector(dirty, attr_index)

                if not any(wgt.dirty_vector):
                    wgt.pose_is_dirty = False
                else:
                    wgt.pose_is_dirty = True
                wgt.set_state_pose_update()

        return callback

    def __init__(self, pose_node, parent=None):
        super(PosePane, self).__init__(parent)

        # State
        self.node = pose_node
        self.connected_plug = nodes.get_pose_weight_connected_attr(self.node)
        self.pose_attrs = nodes.get_pose_attrs(self.node, include_node_name=False)
        self.weight_value = None
        self.weight_locked = None
        self.mute_value = None
        self.mute_locked = None
        self.pose_is_dirty = False
        self.dirty_vector = list()

        # to remember selected attributes inside attr pane when it is closed (deleted)
        self.stored_attr_roots = list()
        self.node_renamed_cbid = None
        self.node_attr_changed_cbid = None

        # Get scene watcher
        self._scene_watcher = get_scene_watcher()

        # Indicator area
        self.indicator_area = QtWidgets.QFrame()
        self.indicator_area.setFixedWidth(scaled(8))

        # Pose name widget
        self.label = LineEditStyled(pose_node, check_command=lambda: not nodes.is_node_read_only(self.node))
        self.label.setMinimumHeight(scaled(16))

        # switcher of attributes pane
        self.attr_switcher = ArrowRadioButton()
        self.attr_switcher.setCheckable(True)

        # Connected plug
        self.connected_plug_label = LineEditStyled(editable=False)
        self.connected_plug_disconnect_action = self.connected_plug_label.add_action("Break Connection")

        # Buttons
        self.add_button = ToolButton(
            size=(scaled(18), scaled(18)),
            icon_name='MCPXAddPlugs',
            alpha=True,
            icon_size=(scaled(16), scaled(16))
        )
        self.add_button.setToolTip("Add new Attributes and update existing Pose Values")
        self.update_button = ToolButton(
            size=(scaled(18), scaled(18)), icon_name='MCPXRefresh', alpha=True, icon_size=(scaled(16), scaled(16)))
        self.update_button.setToolTip("Update existing Pose Values")
        self.select_controls_button = ToolButton(
            size=(scaled(18), scaled(18)),
            icon_name='MCPXSelectControl',
            alpha=True,
            icon_size=(scaled(16), scaled(16))
        )
        self.select_controls_button.setToolTip("Select Controls")
        self.select_pose_button = ToolButton(
            size=(scaled(18), scaled(18)),
            icon_name='MCPXSelect',
            alpha=True,
            icon_size=(scaled(16), scaled(16))
        )
        self.select_pose_button.setToolTip("Select Pose Node")
        self.delete_button = ToolButton(
            size=(scaled(18), scaled(18)),
            icon_name='MCPXDelete',
            alpha=True,
            icon_size=(scaled(16), scaled(16))
        )
        self.delete_button.setToolTip("Delete Pose")

        self.attr_view_pane = None
        # Weight edit
        self.weight_edit = BaseLineEdit(select_all_by_DoubleClick=True)
        self.weight_edit.setToolTip("Set Pose Weight")
        self.weight_edit.setMinimumWidth(scaled(35))
        self.weight_edit.setMaximumWidth(scaled(60))
        self.weight_edit.set_float_validator()
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                            QtWidgets.QSizePolicy.Preferred)
        self.weight_edit.setSizePolicy(size_policy)
        self.weight_edit_lock_action = self.weight_edit.add_action("Lock Attribute")
        self.weight_edit_unlock_action = self.weight_edit.add_action("Unlock Attribute")

        # Weight slider
        self.weight_slider = DynamicSlider(QtCore.Qt.Horizontal)
        self.weight_slider.min_field.setToolTip("Set Minimum of Weight")
        self.weight_slider.max_field.setToolTip("Set Maximum of Weight")

        # Buttons
        self.connect_button = ToolButton(
            size=(scaled(18), scaled(18)),
            icon_size=(scaled(16), scaled(16)),
            alpha=True
        )
        self.disconnect_button = ToolButton(
            size=(scaled(18), scaled(18)),
            icon_name='MCPXDisconnect',
            icon_size=(scaled(16), scaled(16)),
            alpha=True
        )
        self.disconnect_button.setToolTip("Disconnect Pose Weight")

        self.select_connected = ToolButton(
            size=(scaled(18), scaled(18)),
            icon_name='MCPXSelectConnection',
            alpha=True,
            icon_size=(scaled(16), scaled(16))
        )
        self.select_connected.setToolTip("Select Connected Node")

        self.solo_button = ToolButton(
            size=(scaled(18), scaled(18)),
            icon_name='MCPXSolo',
            alpha=True,
            icon_size=(scaled(16), scaled(16)),
            toggle=True
        )
        self.solo_button.setToolTip("Solo Pose")

        self.mute_button = ToolButton(
            size=(scaled(18), scaled(18)),
            icon_name='MCPXMute',
            alpha=True,
            icon_size=(scaled(16), scaled(16)),
            toggle=True
        )
        self.mute_button.setToolTip("Mute Pose")

        # Event handlers
        self.mouse_pressed.connect(self.mouse_pressed_handle)
        self.mouse_moved.connect(self.mouse_moved_handle)
        self.mouse_released.connect(self.mouse_released_handle)
        self.label.mouse_pressed.connect(self.mouse_pressed_handle)
        self.label.mouse_moved.connect(self.mouse_moved_handle)
        self.label.mouse_released.connect(self.mouse_released_handle)
        self.connected_plug_label.mouse_pressed.connect(self.mouse_pressed_handle)
        self.connected_plug_label.mouse_moved.connect(self.mouse_moved_handle)
        self.connected_plug_label.mouse_released.connect(self.mouse_released_handle)
        self.label.editingFinished.connect(self.rename_pose_handle)
        self.label.edit_restricted.connect(self.rename_restricted_handle)
        self.attr_switcher.toggled.connect(self.set_state_attr_pane)
        self.connect_button.clicked.connect(self.connect_handle)
        self.disconnect_button.clicked.connect(self.disconnect_handle)
        self.connected_plug_disconnect_action.triggered.connect(self.disconnect_handle)
        self.select_connected.clicked.connect(self.select_connected_handle)
        self.delete_button.clicked.connect(self.delete_handle)
        self.add_button.clicked.connect(self.add_plugs_handle)
        self.update_button.clicked.connect(self.update_handle)
        self.select_controls_button.clicked.connect(self.select_controls_handle)
        self.select_pose_button.clicked.connect(self.select_pose_handle)
        self.solo_button.toggled.connect(self.solo_handle)
        self.mute_button.toggled.connect(self.mute_handle)
        self.weight_edit.editingFinished.connect(self.edit_change_handle)
        self.weight_edit.mouse_pressed.connect(self.elements_clicked_handle)
        self.weight_edit_lock_action.triggered.connect(self.lock_weight_handle)
        self.weight_edit_unlock_action.triggered.connect(self.unlock_weight_handle)
        self.weight_slider.valueChanged.connect(self.slider_change_handle)
        self.weight_slider.weight_min_set.connect(self.weight_min_change_handle)
        self.weight_slider.weight_max_set.connect(self.weight_max_change_handle)
        self.weight_slider.sliderPressed.connect(self.elements_clicked_handle)
        self.weight_slider.min_field.mouse_pressed.connect(self.elements_clicked_handle)
        self.weight_slider.max_field.mouse_pressed.connect(self.elements_clicked_handle)

        # Top part of Pose pane layout
        top_layout = QtWidgets.QHBoxLayout()
        top_layout.setContentsMargins(scaled(0), scaled(0), scaled(4), scaled(0))
        top_layout.setSpacing(scaled(2))
        top_layout.addWidget(self.label)
        top_layout.addWidget(self.add_button)
        top_layout.addWidget(self.update_button)
        top_layout.addWidget(self.select_controls_button)
        top_layout.addWidget(self.select_pose_button)
        top_layout.addWidget(self.delete_button)

        # Bottom part of Pose pane layout
        self.buttons_area = QtWidgets.QFrame()
        for c_group in COLOR_GROUPS:
            set_color_palette_darker(self.buttons_area, c_role="Window", c_group=c_group, factor=121)
        self.buttons_area.setFixedHeight(scaled(22))
        buttons_area_layout = QtWidgets.QHBoxLayout()
        buttons_area_layout.setContentsMargins(scaled(4), scaled(2), scaled(4), scaled(2))
        buttons_area_layout.setSpacing(scaled(2))
        buttons_area_layout.addWidget(self.solo_button)
        buttons_area_layout.addWidget(self.mute_button)
        self.buttons_area.setLayout(buttons_area_layout)

        bottom_layout = QtWidgets.QHBoxLayout()
        bottom_layout.setContentsMargins(scaled(0), scaled(0), scaled(0), scaled(0))
        bottom_layout.setSpacing(scaled(6))
        bottom_layout.addWidget(self.connect_button)
        bottom_layout.addWidget(self.disconnect_button)
        bottom_layout.addWidget(self.select_connected)
        bottom_layout.addWidget(self.connected_plug_label)
        bottom_layout.addWidget(self.weight_slider)
        bottom_layout.addWidget(self.weight_edit)
        bottom_layout.addWidget(self.buttons_area)

        # Pose pane layout
        pane_area_layout = QtWidgets.QVBoxLayout()
        pane_area_layout.setContentsMargins(scaled(4), scaled(2), scaled(2), scaled(5))
        pane_area_layout.setSpacing(scaled(4))
        pane_area_layout.addLayout(top_layout)
        pane_area_layout.addLayout(bottom_layout)

        self.pose_pane_layout = QtWidgets.QHBoxLayout()
        self.pose_pane_layout.setContentsMargins(scaled(6), scaled(6), scaled(6), scaled(6))
        self.pose_pane_layout.setSpacing(scaled(0))
        self.pose_pane_layout.addWidget(self.attr_switcher)
        self.pose_pane_layout.addLayout(pane_area_layout)

        self.expanded_pane_layout = QtWidgets.QVBoxLayout()
        self.expanded_pane_layout.setContentsMargins(scaled(0), scaled(0), scaled(0), scaled(0))
        self.expanded_pane_layout.setSpacing(scaled(0))
        self.expanded_pane_layout.addLayout(self.pose_pane_layout)

        # Complete layout
        separator = QtWidgets.QFrame()
        separator.setFixedWidth(scaled(2))
        for c_group in COLOR_GROUPS:
            set_color_palette_darker(separator, c_role="Window", c_group=c_group, factor=110)

        complete_layout = QtWidgets.QHBoxLayout()
        complete_layout.setContentsMargins(scaled(0), scaled(0), scaled(0), scaled(0))
        complete_layout.setSpacing(scaled(0))
        complete_layout.addWidget(self.indicator_area)
        complete_layout.addWidget(separator)
        complete_layout.addLayout(self.expanded_pane_layout)
        self.setLayout(complete_layout)

        self.setMouseTracking(True)

        self.setPalette(get_application_palette())
        for c_group in COLOR_GROUPS:
            set_color_palette_lighter(self, c_role="Window", c_group=c_group, factor=107)

        # Setup state according to the node
        # Setup maya callbacks
        self.refresh_state()

    # noinspection PyMethodMayBeStatic
    def _format_preview(self, value):
        return str(round(value, 4))

    def set_state_attr_switcher(self):
        left_margin = scaled(3)
        if self.pose_attrs:
            self.attr_switcher.show()
        else:
            left_margin += self.attr_switcher.width() + self.pose_pane_layout.spacing()
            self.attr_switcher.setChecked(False)
            self.attr_switcher.hide()
        self.pose_pane_layout.setContentsMargins(left_margin, scaled(0), scaled(3), scaled(0))

    def set_state_indicator_color(self):
        plug = self.node + ".weight"
        if self.mute_value:
            settings = {"background-color": "rgb(191, 161, 130)"}
        else:
            settings = get_indicator_color_from_plug(plug)
            if not settings:
                settings = {"background-color": "rgb(37, 37, 37)"}
        self.indicator_area.setStyleSheet(
            generate_style_sheet("QFrame", settings)
        )

    def set_state_connected(self):
        if self.connected_plug:
            self.weight_edit.hide()
            self.weight_slider.hide()
            self.connect_button.set_icon('MCPXPlibEditorConnected')
            self.connect_button.setToolTip("Reconnect Pose Weight")
            self.disconnect_button.show()
            self.connected_plug_label.setText(self.connected_plug)
            self.connected_plug_label.show()
            self.select_connected.show()
        else:
            # block tab reason for line-edit focusEvents to prevent text selection
            self.weight_edit.block_tab_focus(True)
            self.weight_slider.block_tab_focus(True)
            self.weight_edit.show()
            self.weight_slider.show()
            self.connect_button.set_icon('MCPXPlibEditorNotConnected')
            self.connect_button.setToolTip("Connect Pose Weight")
            self.disconnect_button.hide()
            self.connected_plug_label.setText("")
            self.connected_plug_label.hide()
            self.select_connected.hide()
            self.weight_edit.block_tab_focus(False)
            self.weight_slider.block_tab_focus(False)

    def set_state_weight_value(self):
        self.weight_slider.blockSignals(True)
        self.weight_edit.blockSignals(True)
        self.weight_slider.setValue(self.weight_value)
        self.weight_edit.setText(self._format_preview(self.weight_value))
        self.weight_slider.blockSignals(False)
        self.weight_edit.blockSignals(False)

    def set_state_weight_lock(self):
        if not self.weight_locked:
            self.connect_button.setEnabled(True)
            self.disconnect_button.setEnabled(True)
            self.weight_edit.setStyleSheet("")
            self.weight_edit.setReadOnly(False)
            self.weight_edit_lock_action.setVisible(True)
            self.weight_edit_unlock_action.setVisible(False)
            self.weight_slider.setEnabled(True)
            self.connected_plug_label.setEnabled(True)
        else:
            self.connect_button.setEnabled(False)
            self.disconnect_button.setEnabled(False)
            self.weight_edit.setStyleSheet(
                "QLineEdit {color: black; background-color: rgb(92, 104, 116)}")
            self.weight_edit.setReadOnly(True)
            self.weight_edit_unlock_action.setVisible(True)
            self.weight_edit_lock_action.setVisible(False)
            self.weight_slider.setEnabled(False)
            self.connected_plug_label.setEnabled(False)

    def set_state_mute_value(self):
        self.mute_button.setChecked(self.mute_value)

    def set_state_mute_lock(self):
        if not self.mute_locked:
            self.mute_button.setEnabled(True)
        else:
            self.mute_button.setEnabled(False)

    def set_state_pose_update(self):
        if self.pose_is_dirty:
            self.update_button.setVisible(True)
        else:
            self.update_button.setVisible(False)

    def refresh_pose_attrs(self, old_attrs=None):
        if old_attrs:
            if self.pose_attrs:
                attr_to_delete = set(old_attrs).difference(set(self.pose_attrs))
            else:
                attr_to_delete = old_attrs
            plugs_to_delete = list()
            for pose_attr in attr_to_delete:
                rest_subattr = '{}.{}.rest'.format(self.node, pose_attr)
                if nodes.if_real_attr(rest_subattr):
                    plugs_to_delete.append(nodes.get_real_attr(rest_subattr))
            self._scene_watcher.remove_plug_callbacks(self, plugs=plugs_to_delete)

        self.dirty_vector = list()
        if self.pose_attrs:
            for pose_attr in self.pose_attrs:
                rest_subattr = '{}.{}.rest'.format(self.node, pose_attr)
                if nodes.if_real_attr(rest_subattr):
                    connected_attr = nodes.get_real_attr(rest_subattr, short=False)
                    # temporary solution to avoid not proper behavior on Windows 7(?)
                    # (kAttributeEval sent always if mouse just moved inside viewport)
                    clean = not nodes.is_attr_manipulated(connected_attr)
                    self._scene_watcher.add_ctrl_value_changed(
                        self, connected_attr, PosePane.get_plug_value_changed(pose_attr), clean=clean)

                    animblend_node = nodes.get_anim_blend_node(connected_attr)
                    animblend_node_out = '{}.output'.format(animblend_node)
                    self._scene_watcher.add_ctrl_value_changed(
                        self, animblend_node_out,
                        PosePane.get_plug_value_changed(pose_attr),
                        dirty=False, propagate_to_parent=False)
                if nodes.if_attr_dirty(nodes.get_real_attr(rest_subattr, short=False)):
                    self.dirty_vector.append(True)
                else:
                    self.dirty_vector.append(False)

        if not any(self.dirty_vector):
            self.pose_is_dirty = False
        else:
            self.pose_is_dirty = True

    def refresh_connected_plug(self, old_connected_plug=None):
        if old_connected_plug and not self.connected_plug:
            self._scene_watcher.remove_rename_callbacks(self)
        elif self.connected_plug:
            self._scene_watcher.add_ctrl_name_changed(
                self, self.connected_plug, PosePane.plug_name_changed)

    def refresh_state(self):
        # Set callback for a node
        self.clean_callbacks()

        self.weight_value = nodes.get_pose_weight(self.node)
        self.weight_locked = nodes.pose_weight_locked(self.node)
        self.mute_value = nodes.get_mute_pose(self.node)
        self.mute_locked = nodes.if_pose_mute_locked(self.node)

        self.refresh_connected_plug()
        self.refresh_pose_attrs()

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
        self.set_state_mute_value()
        self.set_state_mute_lock()
        self.set_state_connected()
        self.set_state_indicator_color()
        self.set_state_attr_switcher()
        self.set_state_pose_update()
        self.set_state_attr_pane()

        self.weight_slider.setRange(
            nodes.get_pose_weight_min(self.node),
            nodes.get_pose_weight_max(self.node))

    # HANDLERS
    def elements_clicked_handle(self):
        return self.clicked.emit(self)

    def mouse_pressed_handle(self, event, widget):
        if not hasattr(widget, "edit_mode") or not widget.edit_mode:
            if event.buttons() == QtCore.Qt.LeftButton:
                self.raise_()
                self.drag_started.emit(self, event.pos(), self.geometry().y(), event.globalY())
        self.elements_clicked_handle()

    def mouse_moved_handle(self, event, widget):
        if not hasattr(widget, "edit_mode") or not widget.edit_mode:
            if event.buttons() == QtCore.Qt.LeftButton:
                self.drag_moved.emit(event.pos(), event.globalY())

    # noinspection PyUnusedLocal
    def mouse_released_handle(self, event, widget):
        if not hasattr(widget, "edit_mode") or not widget.edit_mode:
            self.drag_finished.emit()

    def rename_restricted_handle(self):
        show_warning("\"{}\" is locked or referenced and cannot be renamed.".format(self.node))

    def rename_pose_handle(self):
        try:
            nodes.rename_node(self.node, self.label.text())
        except:
            self.label.setText(self.node)

    def new_weight_expr_handle(self):
        mel.eval('expressionEditor EE "{}" "weight";'.format(self.node))

    def set_weight_key_handle(self):
        mel.eval('setKeyframe "{}.weight";'.format(self.node))

    def set_weight_driven_key_handle(self):
        mel.eval('setDrivenKeyWindow "{}" {};'.format(self.node, '{"weight"}'))

    def lock_weight_handle(self):
        nodes.lock_attribute(self.node + ".weight", True, verbose=True)

    def unlock_weight_handle(self):
        nodes.lock_attribute(self.node + ".weight", False, verbose=True)

    def connect_handle(self):
        AttributeOutlinerHolder.display_pane('{}.weight'.format(self.node))

    def disconnect_handle(self):
        connected_plug = nodes.get_pose_weight_connected_attr(self.node)
        if connected_plug:
            nodes.disconnect_attrs(connected_plug, '{}.weight'.format(self.node), verbose=True)
            self.set_state_weight_value()

    def slider_change_handle(self):
        if not nodes.pose_weight_has_connection(self.node) and not nodes.pose_weight_locked(self.node):
            value = float(self.weight_slider.value())
            nodes.change_pose_weight(self.node, value)
            self.change_pose_weight.emit(self.node, value)

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
                    return self.change_pose_weight.emit(self.node, value)
        self.set_state_weight_value()

    def select_controls_handle(self):
        nodes.select_nodes(nodes.get_pose_controls(self.node))

    def select_pose_handle(self):
        nodes.select_node(self.node)

    def select_connected_handle(self):
        if self.connected_plug and '.' in self.connected_plug:
            node = self.connected_plug.split('.')[0]
            nodes.select_node(node)

    def delete_handle(self):
        nodes.delete_node(self.node)

    def add_plugs_handle(self):
        selected_attrs = get_selected_attrs()
        if selected_attrs:
            update_plugs_in_pose(self.node, selected_plugs=True)
        else:
            update_controls_in_pose(self.node, selected_controls=True)

        # temporary, while no rename callbacks
        if self.attr_view_pane:
            for single_attr_pane in self.attr_view_pane.attrs_pane.items:
                single_attr_pane.connected_plug = nodes.get_real_attr(single_attr_pane.rest_attr)
                single_attr_pane.set_state_label()

    def update_handle(self):
        plugs = list()
        for root_attr in nodes.get_pose_attrs(self.node):
            plugs.append(nodes.get_real_attr(root_attr + ".rest"))
        update_plugs_in_pose(self.node, plug_list=plugs)

    def solo_handle(self, checked):
        self.solo_pose.emit(self.node, checked)

    def mute_handle(self, checked):
        nodes.set_mute_pose(self.node, checked, force=False, verbose=True)
        self.mute_pose.emit(self.node, checked)

    def update_selection_handle(self, stored_attr_roots):
        self.stored_attr_roots = stored_attr_roots

    def set_state_attr_pane(self):
        if self.attr_switcher.isChecked():
            if not self.attr_view_pane:
                self.attr_view_pane = AttrViewPane(self.node, self.stored_attr_roots)
                self.attr_view_pane.selection_updated.connect(self.update_selection_handle)
                self.attr_view_pane.clicked.connect(self.elements_clicked_handle)
                self.expanded_pane_layout.addWidget(self.attr_view_pane)

                for index in range(len(self.dirty_vector)):
                    if self.dirty_vector[index]:
                        self.attr_view_pane.refresh_dirty_vector(True, attr_index=index)
        else:
            if self.attr_view_pane:
                self.expanded_pane_layout.removeWidget(self.attr_view_pane)
                self.attr_view_pane.clean_all_callbacks()
                self.attr_view_pane.deleteLater()
                self.attr_view_pane = None

    # CALLBACKS
    # noinspection PyArgumentList,PyUnusedLocal,PyPep8Naming
    def maya_node_name_changed_cb(self, node, prev_name, clientData):
        new_name = OpenMaya.MFnDependencyNode(node).name()
        new_name = adapt_name(new_name)
        self.node = new_name
        self.label.setText(new_name)

        if self.attr_view_pane:
            self.attr_view_pane.node = new_name
            # TODO replace refresh state with something less dramatic
            self.attr_view_pane.refresh_state()

        self.pose_renamed.emit(prev_name, new_name)

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
                self.set_state_indicator_color()
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
                self.set_state_indicator_color()

        elif msg & OpenMaya.MNodeMessage.kAttributeLocked or msg & OpenMaya.MNodeMessage.kAttributeUnlocked:
            if attr_name == 'weight':
                self.weight_locked = nodes.pose_weight_locked(self.node)
                self.set_state_weight_lock()
                self.set_state_indicator_color()
            elif attr_name == 'mute':
                self.mute_locked = nodes.if_pose_mute_locked(self.node)
                self.set_state_mute_lock()
                self.set_state_indicator_color()

        elif msg & OpenMaya.MNodeMessage.kConnectionMade or msg & OpenMaya.MNodeMessage.kConnectionBroken:
            if attr_name == 'weight':
                self.weight_value = nodes.get_pose_weight(self.node)
                old_connected_plug = self.connected_plug
                if nodes.pose_weight_has_connection(self.node):
                    self.connected_plug = nodes.get_pose_weight_connected_attr(self.node)
                else:
                    self.connected_plug = None
                self.refresh_connected_plug(old_connected_plug)
                self.set_state_connected()
                self.set_state_indicator_color()
            elif attr_name.endswith(".rest"):
                old_attrs = self.pose_attrs
                self.pose_attrs = nodes.get_pose_attrs(self.node, include_node_name=False)
                self.refresh_pose_attrs(old_attrs)

        elif msg & OpenMaya.MNodeMessage.kAttributeArrayAdded or msg & OpenMaya.MNodeMessage.kAttributeArrayRemoved:
            if attr_name.startswith("attrs["):
                old_attrs = self.pose_attrs
                self.pose_attrs = nodes.get_pose_attrs(self.node, include_node_name=False)
                self.refresh_pose_attrs(old_attrs)
                self.set_state_attr_switcher()

    def clean_callbacks(self):
        self._scene_watcher.remove_rename_callbacks(self)
        self._scene_watcher.remove_plug_callbacks(self)

        if self.node_renamed_cbid:
            OpenMaya.MMessage.removeCallback(self.node_renamed_cbid)
        if self.node_attr_changed_cbid:
            OpenMaya.MMessage.removeCallback(self.node_attr_changed_cbid)

        if self.attr_view_pane:
            self.attr_view_pane.clean_all_callbacks()
