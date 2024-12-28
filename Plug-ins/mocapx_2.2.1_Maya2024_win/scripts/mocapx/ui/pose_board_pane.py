# pylint: disable=no-name-in-module
# noinspection PyUnresolvedReferences
from mocapx.vendor.Qt import QtCore, QtWidgets, QtGui
# pylint: enable=no-name-in-module
from maya.api import OpenMaya

from mocapx.ui.widgets import ScrolledContainer
from mocapx.ui.pose_board_preview_pane import PoseBoardPreviewPane
from mocapx.lib.utils import adapt_name
from mocapx.lib.uiutils import COLOR_GROUPS, scaled, set_color_palette_darker


class PoseBoard(QtWidgets.QWidget):
    # noinspection SpellCheckingInspection
    def __init__(self, parent=None):
        super(PoseBoard, self).__init__(parent)
        self.node_added_cbid = None
        self.node_removed_cbid = None
        self.node_renamed_cbid = None

        self.poses_pane = ScrolledContainer(
            (
                "browDown_L",
                "browDown_R",
                "browInnerUp",
                "browOuterUp_L",
                "browOuterUp_R",
                "cheekPuff",
                "cheekSquint_L",
                "cheekSquint_R",
                "eyeBlink_L",
                "eyeBlink_R",
                "eyeLookDown_L",
                "eyeLookDown_R",
                "eyeLookIn_L",
                "eyeLookIn_R",
                "eyeLookOut_L",
                "eyeLookOut_R",
                "eyeLookUp_L",
                "eyeLookUp_R",
                "eyeSquint_L",
                "eyeSquint_R",
                "eyeWide_L",
                "eyeWide_R",
                "jawForward",
                "jawLeft",
                "jawOpen",
                "jawRight",
                "mouthClose",
                "mouthDimple_L",
                "mouthDimple_R",
                "mouthFrown_L",
                "mouthFrown_R",
                "mouthFunnel",
                "mouthLeft",
                "mouthLowerDown_L",
                "mouthLowerDown_R",
                "mouthPress_L",
                "mouthPress_R",
                "mouthPucker",
                "mouthRight",
                "mouthRollLower",
                "mouthRollUpper",
                "mouthShrugLower",
                "mouthShrugUpper",
                "mouthSmile_L",
                "mouthSmile_R",
                "mouthStretch_L",
                "mouthStretch_R",
                "mouthUpperUp_L",
                "mouthUpperUp_R",
                "noseSneer_L",
                "noseSneer_R"
            ),
            PoseBoardPreviewPane
        )
        for c_group in COLOR_GROUPS:
            set_color_palette_darker(self.poses_pane, c_role="Background", c_group=c_group, factor=121)

        # layout
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(scaled(6), scaled(6), scaled(6), scaled(6))
        layout.setSpacing(scaled(6))
        layout.setAlignment(QtCore.Qt.AlignTop)
        layout.addWidget(self.poses_pane)
        self.setLayout(layout)

        # Setup maya callbacks
        self.node_added_cbid = OpenMaya.MDGMessage.addNodeAddedCallback(
            self.maya_node_created_cb, "MCPXPose")
        self.node_removed_cbid = OpenMaya.MDGMessage.addNodeRemovedCallback(
            self.maya_node_removed_cb, 'MCPXPose')
        self.node_renamed_cbid = OpenMaya.MNodeMessage.addNameChangedCallback(
            OpenMaya.MObject.kNullObj, self.maya_node_name_changed_cb)

    def update_state(self, pose_node, state):
        if pose_node:
            check_name = adapt_name(pose_node).rpartition(":")[2]
            for pane in self.poses_pane.items:
                if pane.pose_name == check_name:
                    pane.set_as_used(state)
                    break

    # CALLBACKS
    # noinspection PyArgumentList,PyUnusedLocal,PyPep8Naming
    def maya_node_created_cb(self, node, clientData):
        self.update_state(OpenMaya.MFnDependencyNode(node).name(), True)

    # noinspection PyArgumentList,PyUnusedLocal,PyPep8Naming
    def maya_node_removed_cb(self, node, clientData):
        self.update_state(OpenMaya.MFnDependencyNode(node).name(), False)

    # noinspection PyArgumentList,PyUnusedLocal,PyPep8Naming
    def maya_node_name_changed_cb(self, node, prev_name, clientData):
        node = OpenMaya.MFnDependencyNode(node)
        if node.typeName == 'MCPXPose':
            self.update_state(prev_name, False)
            self.update_state(node.name(), True)

    # noinspection PyArgumentList,SpellCheckingInspection
    def clean_callbacks(self):
        if self.node_added_cbid:
            OpenMaya.MMessage.removeCallback(self.node_added_cbid)
            self.node_added_cbid = None
        if self.node_removed_cbid:
            OpenMaya.MMessage.removeCallback(self.node_removed_cbid)
            self.node_removed_cbid = None
        if self.node_renamed_cbid:
            OpenMaya.MMessage.removeCallback(self.node_renamed_cbid)
            self.node_renamed_cbid = None

    def clean_all_callbacks(self):
        self.poses_pane.replace_content(list())
        self.clean_callbacks()
