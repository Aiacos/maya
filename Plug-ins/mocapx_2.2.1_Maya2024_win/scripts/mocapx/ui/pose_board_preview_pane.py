from mocapx.lib.utils import get_selected_attrs
from mocapx.lib.uiutils import COLOR_GROUPS, scaled, set_color_palette_lighter, get_application_palette, \
    set_color_palette, get_color_from_maya_palette
from mocapx.ui.widgets import ToolButton, ArrowRadioButton
# pylint: disable=no-name-in-module
# noinspection PyUnresolvedReferences
from mocapx.vendor.Qt import QtGui, QtWidgets, QtCore
# noinspection SpellCheckingInspection
import mocapx.commands as mcpx_cmds
from mocapx.lib.nodes import get_poselib_node, node_exists, scene_selection, select_nodes, find_pose_nodes, \
    list_poselib_nodes
import mocapx
# pylint: enable=no-name-in-module
from mocapx.ui.widgets import BaseLabel


class PoseBoardPreviewPane(QtWidgets.QFrame):
    def __init__(self, pose_node, parent=None):
        super(PoseBoardPreviewPane, self).__init__(parent)

        # State
        self.pose_name = pose_node
        self.previewOpened = False

        self.normal_color = get_color_from_maya_palette(c_role="Foreground", palette=get_application_palette())
        self.used_color = self.normal_color.darker(150)
        # Buttons
        self.pose_button = ToolButton(
            size=(scaled(18), scaled(18)),
            icon_name="MCPXAddPlugs",
            alpha=True,
            icon_size=(scaled(16), scaled(16))
        )
        self.pose_button.setToolTip("Create this Pose")

        self.preview_switcher = ArrowRadioButton()
        self.preview_switcher.setCheckable(True)

        self.select_pose_button = ToolButton(
            size=(scaled(18), scaled(18)),
            icon_name='MCPXSelect',
            alpha=True,
            icon_size=(scaled(16), scaled(16))
        )
        self.select_pose_button.setToolTip("Select Pose Node")

        self.label = BaseLabel(self.pose_name)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setFont(QtGui.QFont(self.label.font().family(), scaled(9)))
        self.label.clicked.connect(self.process_label_click)
        self.label.mouseEntered.connect(self.process_label_mouse_enter)
        self.label.mouseLeft.connect(self.process_label_mouse_leave)

        top_layout = QtWidgets.QHBoxLayout()
        top_layout.setContentsMargins(scaled(0), scaled(0), scaled(0), scaled(0))
        top_layout.setSpacing(scaled(0))
        top_layout.addWidget(self.preview_switcher)
        top_layout.addWidget(self.label)

        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        size_policy.setRetainSizeWhenHidden(True)
        self.select_pose_button.setSizePolicy(size_policy)
        tool_layout = QtWidgets.QHBoxLayout()
        tool_layout.setContentsMargins(scaled(0), scaled(0), scaled(0), scaled(0))
        tool_layout.setSpacing(scaled(2))
        tool_layout.addWidget(self.select_pose_button)
        tool_layout.addWidget(self.pose_button)

        # Pose pane layout
        pane_area_layout = QtWidgets.QHBoxLayout()
        pane_area_layout.setContentsMargins(scaled(4), scaled(2), scaled(2), scaled(2))
        pane_area_layout.setSpacing(scaled(4))
        pane_area_layout.addLayout(top_layout)
        pane_area_layout.addLayout(tool_layout)

        self.expanded_pane_layout = QtWidgets.QVBoxLayout()
        self.expanded_pane_layout.setContentsMargins(scaled(0), scaled(0), scaled(0), scaled(0))
        self.expanded_pane_layout.setSpacing(scaled(0))
        self.expanded_pane_layout.addLayout(pane_area_layout)

        # Complete layout
        complete_layout = QtWidgets.QHBoxLayout()
        complete_layout.setContentsMargins(scaled(0), scaled(0), scaled(0), scaled(0))
        complete_layout.setSpacing(scaled(0))
        complete_layout.addLayout(self.expanded_pane_layout)
        self.setLayout(complete_layout)

        for c_group in COLOR_GROUPS:
            set_color_palette_lighter(self, c_role="Background", c_group=c_group, factor=107)

        # Event handlers
        self.pose_button.clicked.connect(self.create_pose_handle)
        self.preview_switcher.toggled.connect(self.show_preview_handle)
        self.select_pose_button.clicked.connect(self.select_pose_handle)

        # set initial state
        if find_pose_nodes(self.pose_name + "*", recursive=True):
            self.set_as_used(True)
        else:
            self.select_pose_button.setVisible(False)

        self.setMouseTracking(True)

    # noinspection PyPep8Naming,PyMethodMayBeStatic
    def clearLayout(self, layout):
        while layout.count() > 0:
            item = layout.takeAt(0)
            if not item:
                continue
            w = item.widget()
            if w:
                w.deleteLater()

    def set_as_used(self, used):
        color = self.used_color if used else self.normal_color
        for c_group in COLOR_GROUPS:
            set_color_palette(self.label, c_role="Foreground", c_group=c_group, q_color=color)
        self.select_pose_button.setVisible(used)

    # HANDLERS
    def process_label_click(self):
        self.preview_switcher.setChecked(not self.preview_switcher.isChecked())

    def process_label_mouse_enter(self):
        pass

    def process_label_mouse_leave(self):
        pass

    # noinspection PyMethodMayBeStatic
    def get_image(self, name):
        # noinspection SpellCheckingInspection
        return "{}/icons/poses/MCPX{}.png".format(mocapx.plugin_distr_root, name[0].upper() + name[1:])

    # noinspection PyAttributeOutsideInit
    def show_preview_handle(self):
        if self.previewOpened is False:
            self.previewOpened = True
            self.image_layout = QtWidgets.QHBoxLayout()
            self.image_layout.setContentsMargins(scaled(6), scaled(6), scaled(6), scaled(6))
            self.image_layout.setSpacing(scaled(6))
            self.default_label = QtWidgets.QLabel()
            self.default_image = QtGui.QPixmap(self.get_image("default"))
            self.default_image = self.default_image.scaledToWidth(scaled(624 / 3))
            self.default_label.setPixmap(self.default_image)
            self.default_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

            self.pose_label = QtWidgets.QLabel()
            self.pose_image = QtGui.QPixmap(self.get_image(self.pose_name))
            self.pose_image = self.pose_image.scaledToWidth(scaled(624 / 3))
            self.pose_label.setPixmap(self.pose_image)

            self.image_layout.addWidget(self.default_label)
            self.image_layout.addWidget(self.pose_label)
            self.image_layout.setAlignment(QtCore.Qt.AlignCenter)
            self.expanded_pane_layout.addLayout(self.image_layout)
        else:
            self.clearLayout(self.image_layout)
            self.expanded_pane_layout.removeItem(self.image_layout)
            self.previewOpened = False

    # noinspection SpellCheckingInspection
    def create_pose(self, poselib):
        pose_name = self.pose_name
        index = 1
        while node_exists(pose_name):
            pose_name = self.pose_name + str(index)
            index += 1

        selected_attrs = get_selected_attrs()
        pose = mcpx_cmds.create_empty_pose(pose_name=pose_name)

        if selected_attrs:
            # add plugs to empty pose
            mcpx_cmds.update_plugs_in_pose(pose, selected_plugs=True)
        else:
            # add controls to empty pose
            mcpx_cmds.update_controls_in_pose(pose, selected_controls=True)
        mcpx_cmds.add_pose_to_poselib(poselib, [pose])

    # noinspection SpellCheckingInspection,PyPep8Naming
    def create_pose_handle(self):
        if scene_selection():
            poselib_nodes = list_poselib_nodes()
            if not poselib_nodes:
                poselib = get_poselib_node(create_node=True)
                self.create_pose(poselib)
            elif len(poselib_nodes) == 1:
                poselib = poselib_nodes[0]
                self.create_pose(poselib)
            else:
                popupMenu = QtWidgets.QMenu('Select poselib', self)
                popupMenu.triggered.connect(lambda q: self.create_pose(q.text()))
                for lib in poselib_nodes:
                    popupMenu.addAction(lib)
                popupMenu.exec_(self.pose_button.mapToGlobal(QtCore.QPoint(0, 0)))

    def select_pose_handle(self):
        nodes = find_pose_nodes(self.pose_name + "*", recursive=True)
        if nodes:
            select_nodes(nodes)
