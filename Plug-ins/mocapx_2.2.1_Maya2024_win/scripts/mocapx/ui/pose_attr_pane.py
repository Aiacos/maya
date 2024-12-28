from maya.api import OpenMaya

from mocapx.commands import update_plugs_in_pose
from mocapx.lib import nodes
from mocapx.lib.control_watcher import get_scene_watcher
from mocapx.lib.utils import get_mobject
from mocapx.lib.uiutils import COLOR_GROUPS, scaled, set_color_palette_darker, generate_style_sheet, \
    get_indicator_color_from_plug
from mocapx.ui.widgets import ToolButton, BaseLineEdit, LineEditStyled, Container
# pylint: disable=no-name-in-module
# noinspection PyUnresolvedReferences
from mocapx.vendor.Qt import QtCore, QtWidgets, QtGui
# pylint: enable=no-name-in-module


class AttrViewHeader(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(AttrViewHeader, self).__init__(parent)

        style_setting = "font: {}px; color: rgb(116, 116, 116)".format(scaled(10))

        rest_label = LineEditStyled("rest", editable=False)
        rest_label.setMaximumWidth(scaled(60))
        rest_label.setStyleSheet(style_setting)
        pose_label = LineEditStyled("pose", editable=False)
        pose_label.setMaximumWidth(scaled(60))
        pose_label.setStyleSheet(style_setting)

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(scaled(4), scaled(0), scaled(10), scaled(0))
        layout.setSpacing(scaled(2))
        spacer = LineEditStyled(editable=False)
        spacer.setMinimumWidth(scaled(110))
        layout.addWidget(spacer)
        layout.addWidget(rest_label)
        layout.addWidget(pose_label)
        spacer = QtWidgets.QLabel()
        spacer.setFixedSize(scaled(42), scaled(1))
        layout.addWidget(spacer)
        self.setLayout(layout)
        self.setFixedHeight(scaled(12))


class SingleAttrViewPE(QtWidgets.QFrame):
    toggled = QtCore.Signal()
    mouse_pressed = QtCore.Signal(object, QtCore.QPoint)
    mouse_moved = QtCore.Signal(QtCore.QPoint)
    unselected = QtCore.Signal()
    unfocused = QtCore.Signal()
    update_pressed = QtCore.Signal(object)
    delete_pressed = QtCore.Signal(object)

    @staticmethod
    def plug_name_changed(wgt, new_name):
        if wgt.connected_plug:
            plug = wgt.connected_plug.partition('.')[2]
            real_attr = wgt.real_attr.partition('.')[2]
            wgt.connected_plug = '{}.{}'.format(new_name, plug)
            wgt.real_attr = '{}.{}'.format(new_name, real_attr)
            wgt.set_state_label()

    # noinspection PyUnusedLocal
    @staticmethod
    def plug_value_changed(wgt, clean):
        if wgt.connected_plug:
            wgt.rest_value = nodes.get_attr_value(wgt.rest_attr)
            wgt.set_state_rest_value()

    def __init__(self, root_attr, parent=None):
        super(SingleAttrViewPE, self).__init__(parent)
        self.class_name = self.metaObject().className()
        self.is_checked = False

        self.root_attr = root_attr
        self.root_only = root_attr.partition(".")[2]  # to remember selection status without node name dependency
        self.rest_attr = root_attr + ".rest"
        self.pose_attr = root_attr + ".pose"
        self.real_attr = None
        self.connected_plug = None
        self.attr_collection_plug = None

        self.is_rest_active = None

        # edit-fields show round values according to formatting
        # so, need to prevent set this round values after every editingFinished signal
        # for this we keep actual values to be able to check before setAttr
        self.rest_value = None
        self.pose_value = None

        # Get scene watcher
        self._scene_watcher = get_scene_watcher()
        self.plug_is_dirty = False

        self.attr_lbl = LineEditStyled(editable=False)
        self.attr_lbl.setMinimumWidth(scaled(110))
        self.attr_lbl.setFixedHeight(scaled(20))
        self.attr_lbl.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.attr_rest_edit = BaseLineEdit(select_all_by_DoubleClick=True)
        self.attr_rest_edit.setToolTip("Set Rest Value")
        self.attr_rest_edit.setMaximumWidth(scaled(60))
        self.attr_rest_edit.set_float_validator()
        self.attr_pose_edit = BaseLineEdit(select_all_by_DoubleClick=True)
        self.attr_pose_edit.setToolTip("Set Pose Value")
        self.attr_pose_edit.setMaximumWidth(scaled(60))
        self.attr_pose_edit.set_float_validator()

        self.refresh = ToolButton(
            size=(scaled(18), scaled(18)),
            icon_name='MCPXRefresh',
            alpha=True,
            icon_size=(scaled(16), scaled(16))
        )
        self.refresh.setToolTip("Update Pose Value")
        self.delete = ToolButton(
            size=(scaled(18), scaled(18)),
            icon_name='MCPXDelete',
            alpha=True,
            icon_size=(scaled(16), scaled(16))
        )
        self.delete.setToolTip("Remove from Pose")

        self.attr_lbl.mouse_pressed.connect(self.mouse_press_handle)
        self.attr_lbl.mouse_moved.connect(self.mouse_move_handle)
        self.attr_rest_edit.mouse_pressed.connect(lambda event: self.unselected.emit())
        self.attr_rest_edit.editingFinished.connect(self.set_rest_value_handle)
        self.attr_pose_edit.mouse_pressed.connect(lambda event: self.unselected.emit())
        self.attr_pose_edit.editingFinished.connect(self.set_pose_value_handle)
        self.refresh.clicked.connect(self.update_attr_handle)
        self.delete.clicked.connect(lambda: self.delete_pressed.emit(self))

        o_layout = QtWidgets.QHBoxLayout()
        o_layout.setContentsMargins(scaled(0), scaled(0), scaled(0), scaled(0))
        o_layout.setSpacing(scaled(2))
        o_layout.addWidget(self.attr_lbl)
        o_layout.addWidget(self.attr_rest_edit)
        o_layout.addWidget(self.attr_pose_edit)

        self.b_layout = QtWidgets.QHBoxLayout()
        self.b_layout.setContentsMargins(scaled(6), scaled(6), scaled(6), scaled(6))
        self.b_layout.setSpacing(scaled(2))
        self.b_layout.addWidget(self.refresh)
        self.b_layout.addWidget(self.delete)

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(scaled(0), scaled(0), scaled(6), scaled(0))
        layout.setSpacing(scaled(6))
        layout.addLayout(o_layout)
        layout.addLayout(self.b_layout)
        self.setLayout(layout)

        self.refresh_state()

    # noinspection PyMethodMayBeStatic
    def _format_preview(self, value):
        return "{:.3f}".format(value)

    def _set_state_value(self, edit_field, attr_name, value, update_style=True):
        edit_field.setText(self._format_preview(value))
        if update_style:
            edit_field.setStyleSheet(
                generate_style_sheet("QLineEdit", get_indicator_color_from_plug(attr_name))
            )

    def _set_value(self, edit_field, attr_name, current_value):
        text = edit_field.text()
        if self._format_preview(current_value) != text:
            try:
                new_value = float(text)
            except ValueError:
                pass
            else:
                try:
                    if nodes.set_attr_value(attr_name, new_value, force=False, verbose=True):
                        return True
                except RuntimeError:
                    pass
        return False

    # noinspection PyPep8Naming
    def mousePressEvent(self, event):
        self.unfocused.emit()
        super(SingleAttrViewPE, self).mousePressEvent(event)

    def refresh_connected_plug(self, old_connected_plug=None):
        if nodes.if_real_attr(self.rest_attr):
            self.connected_plug = nodes.get_real_attr(self.rest_attr, short=False)
        else:
            self.connected_plug = None
        self.real_attr = nodes.get_real_attr(self.rest_attr, short=True)

        if old_connected_plug and old_connected_plug != self.connected_plug:
            self._scene_watcher.remove_rename_callbacks(self)
            if self.attr_collection_plug:
                self._scene_watcher.remove_plug_callbacks(self, plugs=(self.attr_collection_plug,))
                self.attr_collection_plug = None

        if self.connected_plug:
            self._scene_watcher.add_ctrl_name_changed(
                self, self.connected_plug, SingleAttrViewPE.plug_name_changed)

            self.attr_collection_plug = nodes.get_rest_real_attr(self.rest_attr)
            self._scene_watcher.add_ctrl_value_changed(
                self, self.attr_collection_plug, SingleAttrViewPE.plug_value_changed, clean=False,
                propagate_to_parent=False)

    def refresh_state(self):
        self.rest_value = nodes.get_attr_value(self.rest_attr)
        self.pose_value = nodes.get_attr_value(self.pose_attr)

        self.is_rest_active = nodes.is_attr_settable(self.rest_attr)

        self.refresh_connected_plug()

        self.set_state_refresh()
        self.set_selection_state()
        self.set_state_label()
        self.set_state_rest_value()
        self.set_state_pose_value()

    def set_selection_state(self):
        if self.is_checked:
            self.setStyleSheet(self.class_name + " {background-color: rgb(82, 133, 166)}")
        else:
            self.setStyleSheet("")

        self.attr_lbl.setStyleSheet("color: rgb(255, 255, 255)" * self.is_checked)

    def set_state_refresh(self):
        left_margin = scaled(0)
        if self.plug_is_dirty:
            self.refresh.setVisible(True)
        else:
            self.refresh.setVisible(False)
            left_margin += self.refresh.width() + self.b_layout.spacing()
        self.b_layout.setContentsMargins(left_margin, scaled(0), scaled(0), scaled(0))

    def set_state_label(self):
        self.attr_lbl.setText(self.real_attr)

    # noinspection PyTypeChecker
    def set_state_rest_value(self):
        self._set_state_value(self.attr_rest_edit, self.rest_attr, self.rest_value, self.is_rest_active)
        self.attr_rest_edit.setEnabled(self.is_rest_active)

    # noinspection PyTypeChecker
    def set_state_pose_value(self):
        self._set_state_value(self.attr_pose_edit, self.pose_attr, self.pose_value)

    # noinspection PyTypeChecker
    def set_rest_value_handle(self):
        if not self._set_value(self.attr_rest_edit, self.rest_attr, self.rest_value):
            self.rest_value = nodes.get_attr_value(self.rest_attr)
            self.set_state_rest_value()

    # noinspection PyTypeChecker
    def set_pose_value_handle(self):
        if not self._set_value(self.attr_pose_edit, self.pose_attr, self.pose_value):
            self.pose_value = nodes.get_attr_value(self.pose_attr)
            self.set_state_pose_value()

    def update_attr_handle(self):
        self.update_pressed.emit(self)
        self.unfocused.emit()

    def delete_attr_handle(self):
        nodes.remove_multi_element(self.root_attr)

    def mouse_press_handle(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            self.mouse_pressed.emit(self, event.globalPos())

    def mouse_move_handle(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            self.mouse_moved.emit(event.globalPos())

    def set_checked(self, state):
        if self.is_checked != state:
            self.is_checked = state
            self.set_selection_state()
            self.toggled.emit()

    def clean_callbacks(self):
        self._scene_watcher.remove_rename_callbacks(self)
        self._scene_watcher.remove_plug_callbacks(self)


# noinspection SpellCheckingInspection
class AttrViewPane(QtWidgets.QFrame):
    selection_updated = QtCore.Signal(list)
    clicked = QtCore.Signal(object)

    # noinspection PyDefaultArgument
    def __init__(self, pose_node, stored_attr_roots=[], parent=None):
        super(AttrViewPane, self).__init__(parent)

        self.node = pose_node

        self.node_attr_changed_cbid = None

        self.attributes = list()
        self.attrs_pane = Container(
            entities=self.attributes,
            constructor=SingleAttrViewPE,
            spacing=scaled(1),
            margins=(scaled(4), scaled(2), scaled(4), scaled(4))
        )
        self.attributes = nodes.get_pose_attrs(self.node)

        self.stored_attr_roots = stored_attr_roots
        self.selected_items = list()

        self.refresh_locker = False

        top_separator = QtWidgets.QFrame()
        top_separator.setFixedHeight(scaled(1))

        for c_group in COLOR_GROUPS:
            set_color_palette_darker(top_separator, c_role="Background", c_group=c_group, factor=110)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(scaled(0), scaled(0), scaled(0), scaled(0))
        layout.setSpacing(scaled(0))
        layout.addWidget(top_separator)
        layout.addWidget(AttrViewHeader())
        layout.addWidget(self.attrs_pane)
        self.setLayout(layout)

        self.refresh_state()

    def set_attributes_state(self):
        self.refresh_selection_list()

        for single_attr_pane in self.attrs_pane.items:
            state = not self.selected_items or single_attr_pane in self.selected_items
            single_attr_pane.refresh.setEnabled(state)
            single_attr_pane.delete.setEnabled(state)

        # to keep only existing attributes (filter init list in refresh_state and update in other cases)
        self.stored_attr_roots = [x.root_only for x in self.selected_items]
        self.selection_updated.emit(self.stored_attr_roots)

    def refresh_dirty_vector(self, dirty_value, attr_index=None):
        if attr_index or attr_index == 0:
            wgts_list = [self.attrs_pane.items[attr_index]]
        else:
            wgts_list = self.attrs_pane.items

        for single_attr_wgt in wgts_list:
            if single_attr_wgt.connected_plug:
                single_attr_wgt.plug_is_dirty = dirty_value
                single_attr_wgt.set_state_refresh()

    def refresh_selection_list(self):
        self.selected_items = [x for x in self.attrs_pane.items if x.is_checked]

    def refresh_state(self):
        self.attrs_pane.replace_content(self.attributes)

        for single_attr in self.attrs_pane.items:
            single_attr.set_checked(single_attr.root_only in self.stored_attr_roots)

            single_attr.toggled.connect(self.set_attributes_state)
            single_attr.mouse_pressed.connect(self.click_selection_handle)
            single_attr.mouse_moved.connect(self.drag_selection_handle)
            single_attr.unselected.connect(self.clear_selection_state)
            single_attr.unfocused.connect(self.clear_focus_state)
            single_attr.update_pressed.connect(self.update_handle)
            single_attr.delete_pressed.connect(self.delete_handle)

        self.set_attributes_state()

        self.clean_callbacks()
        node_mobject = get_mobject(self.node)
        if node_mobject:
            self.node_attr_changed_cbid = OpenMaya.MNodeMessage.addAttributeChangedCallback(
                node_mobject, self.node_attr_changed_cb)

    # noinspection PyAttributeOutsideInit
    def click_selection_handle(self, widget, event_pos):
        self.add_selection_mode = True  # select or deselect with ctrl-drag

        modifiers = QtWidgets.QApplication.keyboardModifiers()

        if modifiers == QtCore.Qt.ShiftModifier:
            self.selected_items_before_drag = self.selected_items

            click_index = self.attrs_pane.items.index(widget)
            above_group = []
            above_check = False
            below_group = []
            below_check = False

            # find possible ways to already selected items
            for index, single_attr_pane in enumerate(self.attrs_pane.items):
                if index < click_index:
                    if single_attr_pane.is_checked:
                        above_group = [single_attr_pane]
                        above_check = True
                    elif above_check:
                        above_group.append(single_attr_pane)
                elif index > click_index:
                    below_group.append(single_attr_pane)
                    if single_attr_pane.is_checked:
                        below_check = True
                        break

            below_group *= below_check

            # get the closest selected widget or first one if no selection
            if above_check and below_check:
                if len(above_group) <= len(below_group):
                    starting_widget = above_group[0]
                else:
                    starting_widget = below_group[-1]
            elif above_group:
                starting_widget = above_group[0]
            elif below_group:
                starting_widget = below_group[-1]
            else:
                starting_widget = self.attrs_pane.items[0]

            # perform selection
            center_x = starting_widget.width() // 2
            center_y = starting_widget.height() // 2
            self.start_drag_position = starting_widget.mapToGlobal(
                QtCore.QPoint(center_x, center_y))
            self.drag_selection_handle(event_pos)

        elif modifiers == QtCore.Qt.ControlModifier:
            self.start_drag_position = event_pos

            state = not widget.is_checked
            self.add_selection_mode = state
            widget.set_checked(state)

            self.selected_items_before_drag = self.selected_items

        else:
            self.start_drag_position = event_pos
            self.selected_items_before_drag = list()
            for single_attr_pane in self.attrs_pane.items:
                single_attr_pane.set_checked(single_attr_pane == widget)

        self.clicked.emit(self)

    def drag_selection_handle(self, pos):
        top_left = QtCore.QPoint(min(pos.x(), self.start_drag_position.x()),
                                 min(pos.y(), self.start_drag_position.y()))
        size = QtCore.QSize(abs(self.start_drag_position.x() - pos.x()),
                            abs(self.start_drag_position.y() - pos.y()))
        selected_area = QtCore.QRect(top_left, size)

        # for each mouse movement self.selected_items_before_drag - starting point (constant selected elements)
        self.selected_items = self.selected_items_before_drag[:]

        for single_attr in self.attrs_pane.items:
            # if need to select - work only with widgets which can be selected (added to the list)
            # if need to deselect - work only with widgets which can be deselected (removed from the list)
            if (self.add_selection_mode and single_attr not in self.selected_items_before_drag) or \
                    (not self.add_selection_mode and single_attr in self.selected_items_before_drag):
                widget_area = QtCore.QRect(single_attr.mapToGlobal(QtCore.QPoint(0, 0)),
                                           single_attr.size())

                if selected_area.intersects(widget_area):
                    state = self.add_selection_mode
                else:
                    state = not self.add_selection_mode
                single_attr.set_checked(state)

        self.refresh_selection_list()

    def clear_selection_state(self):
        for single_attr_pane in self.attrs_pane.items:
            single_attr_pane.set_checked(False)

    def clear_focus_state(self):
        for single_attr_pane in self.attrs_pane.items:
            for child in single_attr_pane.children():
                if hasattr(child, "clearFocus"):
                    # noinspection PyCallingNonCallable
                    child.clearFocus()

    def delete_handle(self, single_attr_pane):
        if self.selected_items:
            self.refresh_locker = True
            for item in self.selected_items:
                item.delete_attr_handle()
            self.attributes = nodes.get_pose_attrs(self.node)
            self.refresh_state()
            self.refresh_locker = False
        else:
            single_attr_pane.delete_attr_handle()

    def update_handle(self, single_attr_pane):
        plugs = list()
        for item in self.selected_items or [single_attr_pane]:
            plugs.append(nodes.get_real_attr(item.rest_attr))
        update_plugs_in_pose(self.node, plug_list=plugs)

    # noinspection PyPep8Naming,PyUnusedLocal
    def node_attr_changed_cb(self, msg, plug, otherplug, clientData):
        attr_name = plug.partialName(includeNodeName=False)

        if attr_name.startswith("attrs["):
            if msg & OpenMaya.MNodeMessage.kAttributeArrayAdded or \
                    msg & OpenMaya.MNodeMessage.kAttributeArrayRemoved:
                if not self.refresh_locker:
                    self.attributes = nodes.get_pose_attrs(self.node)
                    self.refresh_state()
            elif msg & OpenMaya.MNodeMessage.kAttributeSet:
                root_attr = "{}.attrs[{}]".format(self.node, nodes.get_index(attr_name))
                if attr_name.endswith(".rest"):
                    item_widget = self.attrs_pane.items_dict[root_attr]
                    item_widget.rest_value = nodes.get_attr_value(item_widget.rest_attr)
                    item_widget.set_state_rest_value()
                elif attr_name.endswith(".pose"):
                    item_widget = self.attrs_pane.items_dict[root_attr]
                    item_widget.pose_value = nodes.get_attr_value(item_widget.pose_attr)
                    item_widget.set_state_pose_value()
            elif msg & OpenMaya.MNodeMessage.kConnectionMade or \
                    msg & OpenMaya.MNodeMessage.kConnectionBroken or msg & OpenMaya.MNodeMessage.kAttributeLocked or \
                    msg & OpenMaya.MNodeMessage.kAttributeUnlocked:
                root_attr = "{}.attrs[{}]".format(self.node, nodes.get_index(attr_name))
                if attr_name.endswith(".rest"):
                    item_widget = self.attrs_pane.items_dict[root_attr]
                    item_widget.is_rest_active = nodes.is_attr_settable(item_widget.rest_attr)
                    old_connected_plug = item_widget.connected_plug
                    item_widget.refresh_connected_plug(old_connected_plug)
                    item_widget.rest_value = nodes.get_attr_value(item_widget.rest_attr)
                    item_widget.set_state_rest_value()
                    item_widget.set_state_label()
                elif attr_name.endswith(".pose"):
                    item_widget = self.attrs_pane.items_dict[root_attr]
                    item_widget.pose_value = nodes.get_attr_value(item_widget.pose_attr)
                    item_widget.set_state_pose_value()

    def clean_callbacks(self):
        if self.node_attr_changed_cbid:
            OpenMaya.MMessage.removeCallback(self.node_attr_changed_cbid)
            self.node_attr_changed_cbid = None

    def clean_all_callbacks(self):
        # Remove all attrs panes
        self.attrs_pane.replace_content(list())
        # Remove callbacks on self
        self.clean_callbacks()
