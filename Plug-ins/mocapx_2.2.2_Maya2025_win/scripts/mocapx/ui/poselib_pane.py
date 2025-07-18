import maya.api.OpenMaya as OpenMaya
import mocapx
from mocapx.lib.nodes import get_pose_nodes, if_pose_node, get_mute_pose, set_mute_pose, get_order_list, \
    sort_nodes_by_order, set_order_list
from mocapx.ui.pose_pane import PosePane
from mocapx.ui.poselib_picker_pane import PoselibPicker
# pylint: disable=no-name-in-module
# noinspection PyUnresolvedReferences
from mocapx.vendor.Qt import QtWidgets, QtCore
# pylint: enable=no-name-in-module
from mocapx.ui.widgets import ScrolledContainerDrag
from mocapx.lib.utils import get_mobject
from mocapx.lib.uiutils import COLOR_GROUPS, scaled, set_color_palette_darker


# noinspection SpellCheckingInspection, PyPep8Naming
class PoselibPane(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(PoselibPane, self).__init__(parent)

        # State
        self.pose_nodes = list()
        self.pose_order = list()
        self.solo_node = None
        self.poselib_watcher_callback_id = None
        self.scene_before_save_cbid = None

        # Picker
        self.poselib_picker = PoselibPicker()
        self.poselib_node = self.poselib_picker.selected_item

        # Poses pane
        self.poses_pane = ScrolledContainerDrag(self.pose_nodes, PosePane)
        for c_group in COLOR_GROUPS:
            set_color_palette_darker(self.poses_pane, c_role="Window", c_group=c_group, factor=121)

        # Lay out
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(scaled(6), scaled(6), scaled(6), scaled(6))
        layout.setSpacing(scaled(6))
        layout.addWidget(self.poselib_picker)
        layout.addWidget(self.poses_pane)
        self.setLayout(layout)

        # Setup handlers
        self.poselib_picker.poselib_changed.connect(self.change_poselib_handle)

        # Setup state according to the node
        # Setup maya callbacks
        self.refresh_state()

    def mousePressEvent(self, event):
        self.clear_attr_selection()
        super(PoselibPane, self).mousePressEvent(event)

    def clear_attr_selection(self, source_pane=None):
        for pane in self.poses_pane.items:
            if source_pane is None or source_pane != pane:
                if pane.attr_view_pane:
                    pane.attr_view_pane.clear_selection_state()

    def connect_handlers(self, pose_pane):
        pose_pane.solo_pose.connect(self.solo_pose_handle)
        pose_pane.mute_pose.connect(self.mute_pose_handle)
        pose_pane.pose_renamed.connect(self.renamed_pose_handle)
        pose_pane.drag_finished.connect(self.refresh_order_state)
        pose_pane.clicked.connect(self.clear_attr_selection)

    def sort_poses_by_order(self):
        if not self.pose_nodes:
            return
        if not self.pose_order:
            self.pose_order = get_order_list(self.poselib_node)
        if self.pose_order:
            self.pose_nodes = sort_nodes_by_order(
                self.pose_nodes,
                self.pose_order,
                self.poselib_node.rpartition(":")[0])

    def set_order_attribute(self, *args, **kwargs):
        return set_order_list(self.poselib_node, self.pose_nodes, force=False)

    def refresh_order_state(self):
        # according to widgets order
        self.pose_nodes = list()
        inv_map = {v: k for k, v in self.poses_pane.items_dict.items()}
        for widget in self.poses_pane.items:
            self.pose_nodes.append(inv_map[widget])
        self.set_order_attribute()

    def refresh_buttons_state(self, removed_node=None):
        all_poses = get_pose_nodes()
        # after nodeRemoved callback called, removed node still returned by ls command
        if removed_node:
            all_poses = [node for node in all_poses if node != removed_node]

        unmuted = list(filter(lambda x: not get_mute_pose(x), all_poses))
        alone_pane = None

        if len(unmuted) == 1:
            pose_solo_node = unmuted[0]
            if pose_solo_node in self.poses_pane.items_dict:
                alone_pane = self.poses_pane.items_dict[pose_solo_node]
                solo_button = alone_pane.solo_button
                if not solo_button.isChecked():
                    solo_button.blockSignals(True)
                    solo_button.setChecked(True)
                    solo_button.blockSignals(False)

        else:
            # reset global solo state
            mocapx.pose_solo_mode = False

        for pose_pane in self.poses_pane.items:
            # reset solo states and show/hide add-button state
            if pose_pane == alone_pane:
                pose_pane.add_button.show()
            else:
                pose_pane.add_button.hide()
                if pose_pane.solo_button.isChecked():
                    pose_pane.solo_button.blockSignals(True)
                    pose_pane.solo_button.setChecked(False)
                    pose_pane.solo_button.blockSignals(False)

    def refresh_state(self):
        # set pose-nodes already connected to poselib
        self.pose_nodes = get_pose_nodes(self.poselib_node)
        self.sort_poses_by_order()

        self.poses_pane.replace_content(self.pose_nodes)

        for pose_pane in self.poses_pane.items:
            self.connect_handlers(pose_pane)

        self.refresh_buttons_state()

        # Set callback for a node
        self.clean_callbacks()
        if self.poselib_node:
            node_mobject = get_mobject(self.poselib_node)
            if node_mobject:
                self.poselib_watcher_callback_id = OpenMaya.MNodeMessage.addAttributeChangedCallback(
                    node_mobject, self.poselib_changed_callback)
            else:
                self.poselib_watcher_callback_id = None
        else:
            self.poselib_watcher_callback_id = None
        self.scene_before_save_cbid = OpenMaya.MSceneMessage.addCallback(
            OpenMaya.MSceneMessage.kBeforeSave, self.set_order_attribute)

    # HANDLERS
    def change_poselib_handle(self, poselib_node):
        self.set_order_attribute()
        self.poselib_node = poselib_node
        self.pose_order = get_order_list(self.poselib_node)
        self.refresh_state()

    def mute_pose_handle(self, mute_pose, mute_state):
        ctrl = QtWidgets.QApplication.keyboardModifiers() == QtCore.Qt.ControlModifier

        for pose_node in self.pose_nodes:
            if ctrl and mute_pose != pose_node:
                set_mute_pose(pose_node, mute_state, force=False, verbose=True)

    def solo_pose_handle(self, solo_pose, solo_state):
        solo_checked = False
        temp_unmutes = list()  # collect unmute states
        save_unmutes = solo_state  # remember if solo switched on and no previous solo

        for pose_node in get_pose_nodes():
            solo_button = mute_button = None
            if pose_node in self.poses_pane.items_dict:
                solo_button = self.poses_pane.items_dict[pose_node].solo_button
                mute_button = self.poses_pane.items_dict[pose_node].mute_button

            if pose_node != solo_pose:
                solo_value = False
                mute_value = solo_state or (pose_node not in mocapx.pose_unmutes_before_solo)

                if save_unmutes and mocapx.pose_solo_mode:
                    # if another solo was before this one - do not update stored mute states
                    save_unmutes = False

            else:
                solo_value = solo_state
                mute_value = False if solo_state else (pose_node not in mocapx.pose_unmutes_before_solo)

            # collect unmute to remember
            if save_unmutes and not get_mute_pose(pose_node):
                temp_unmutes.append(pose_node)

            if solo_button and mute_button:
                # update UI solo state
                solo_button.blockSignals(True)
                solo_button.setChecked(solo_value)
                solo_button.blockSignals(False)

                if solo_value:
                    solo_checked = True

                # update mute state
                mute_button.blockSignals(True)
                mute_button.setChecked(mute_value)
            try:
                set_mute_pose(pose_node, mute_value, force=False, verbose=True)
            except RuntimeError:
                pass
            finally:
                if mute_button:
                    mute_button.blockSignals(False)

        mocapx.pose_solo_mode = solo_checked
        if save_unmutes:
            mocapx.pose_unmutes_before_solo = temp_unmutes

    def renamed_pose_handle(self, old_name, new_name):
        self.pose_nodes[self.pose_nodes.index(old_name)] = new_name
        self.set_order_attribute()
        self.poses_pane.items_dict[new_name] = self.poses_pane.items_dict[old_name]
        del self.poses_pane.items_dict[old_name]

    # CALLBACKS
    # noinspection PyArgumentList, PyUnusedLocal, PyPep8Naming
    def poselib_changed_callback(self, msg, plug, otherplug, clientData):
        plug_name = str(plug.partialName(includeNodeName=True))
        plug_node, attr_name = plug_name.split('.', 1)
        otherplug_node = str(otherplug.partialName(includeNodeName=True)).split('.')[0]
        if msg & OpenMaya.MNodeMessage.kConnectionMade:
            if if_pose_node(otherplug_node):
                if otherplug_node not in self.pose_nodes:
                    self.pose_nodes.append(otherplug_node)
                    # while scene loading, read order-attribute and insert according to it
                    # in other case and/or if no current node in order-attribute - index is last
                    self.sort_poses_by_order()
                    index = self.pose_nodes.index(otherplug_node)
                    pose_pane = self.poses_pane.add_item(otherplug_node, index)
                    self.connect_handlers(pose_pane)
                    self.refresh_buttons_state()
        elif msg & OpenMaya.MNodeMessage.kConnectionBroken:
            if if_pose_node(otherplug_node):
                if otherplug_node in self.pose_nodes:
                    self.poses_pane.remove_item(otherplug_node)
                    self.pose_nodes.remove(otherplug_node)
                    self.refresh_buttons_state(removed_node=otherplug_node)
        elif msg & OpenMaya.MNodeMessage.kAttributeSet:
            if attr_name == "order":
                self.pose_order = get_order_list(self.poselib_node)

    def clean_callbacks(self):
        if self.poselib_watcher_callback_id:
            OpenMaya.MMessage.removeCallback(self.poselib_watcher_callback_id)
            self.poselib_watcher_callback_id = None
        if self.scene_before_save_cbid:
            OpenMaya.MMessage.removeCallback(self.scene_before_save_cbid)
            self.scene_before_save_cbid = None

    def clean_all_callbacks(self):
        # Remove all pose panes
        self.poses_pane.replace_content(list())
        # Remove callbacks on pose picker
        self.poselib_picker.clean_callbacks()
        # Remove callbacks on self
        self.clean_callbacks()
