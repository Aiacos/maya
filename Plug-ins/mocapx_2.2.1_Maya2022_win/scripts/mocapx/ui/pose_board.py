import maya.cmds as mc
import maya.mel as mel
from maya import OpenMayaUI as omui

import mocapx
from mocapx import MODULE_NAME
from mocapx.ui.pose_board_pane import PoseBoard
from mocapx.lib.utils import long_constr
from mocapx.lib.uiutils import scaled
# pylint: disable=no-name-in-module
# noinspection PyUnresolvedReferences
from mocapx.vendor.Qt import QtWidgets

# pylint: enable=no-name-in-module

try:
    # noinspection PyUnresolvedReferences
    from shiboken2 import wrapInstance
except ImportError:
    # noinspection PyUnresolvedReferences
    from shiboken import wrapInstance

# noinspection SpellCheckingInspection
EDITOR_NAME = "MocapXPoseBoard"
# noinspection SpellCheckingInspection
WIDGET_NAME = "MocapXPoseBoardDockableWidget"
# noinspection SpellCheckingInspection
TITLE_LABEL = "MocapX Pose Board"

# noinspection SpellCheckingInspection
WORKSPACE_OV = "MocapXPoseBoardWorkspaceLayouts"  # Maya >2017, save only workspaces, states are kept in them
# noinspection SpellCheckingInspection
DOCKSTATE_OV = "MocapXPoseBoardDockState"  # Maya <2017, save state of widget
# noinspection SpellCheckingInspection
DOCKFLOAT_OV = "MocapXPoseBoardDockFloat"  # Maya <2017, used during editor creation (required, if it was floating)


def control_command(*args, **kwargs):
    if hasattr(mc, "workspaceControl"):
        return mc.workspaceControl(*args, **kwargs)
    return mc.dockControl(*args, **kwargs)


def get_current_workspace():
    if hasattr(mc, "workspaceLayoutManager"):
        return mc.workspaceLayoutManager(q=True, current=True)
    return None


# noinspection SpellCheckingInspection
class DockableWrapPanel(QtWidgets.QWidget):
    def __init__(self, widget):
        super(DockableWrapPanel, self).__init__()
        self.widget = widget
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(scaled(0), scaled(0), scaled(0), scaled(0))
        layout.setSpacing(6)
        layout.addWidget(self.widget)
        self.setLayout(layout)

    def wc_closed(self):
        # Save state in user preferences
        if not hasattr(mc, "workspaceControl"):
            mc.optionVar(sv=(DOCKSTATE_OV, mc.dockControl(WIDGET_NAME, q=True, state=True)))
        else:
            current_workspace = get_current_workspace()
            if current_workspace and (
                    not mc.optionVar(ex=WORKSPACE_OV) or current_workspace not in mc.optionVar(q=WORKSPACE_OV)):
                mc.optionVar(sva=(WORKSPACE_OV, current_workspace))

        # Delete all callbacks
        # self.widget.set_order_attribute()
        self.widget.clean_all_callbacks()
        mocapx.pose_board.detach_me()
        mocapx.pose_board.deleteLater()
        mocapx.pose_board = None

        # evalDeferred to prevent fatal error in Maya <2017
        mel.eval("evalDeferred \"deleteUI " + WIDGET_NAME + "\"")

    # only for Maya <2017
    # remember floating state to use it with next initialisation (new Maya session)
    # noinspection PyMethodMayBeStatic
    def wc_float_changed(self):
        mc.optionVar(iv=(DOCKFLOAT_OV, int(mc.dockControl(WIDGET_NAME, q=True, floating=True))))

    def detach_me(self):
        self.setParent(None)


def check_and_set_dock_state():
    # if first launch for Maya >2017 - tab to control
    if hasattr(mc, "workspaceLayoutManager"):
        current_workspace = get_current_workspace()
        if not mc.optionVar(ex=WORKSPACE_OV) or current_workspace not in mc.optionVar(q=WORKSPACE_OV):
            le_component = mel.eval(
                'getUIComponentDockControl("Channel Box / Layer Editor", false);')
            mc.workspaceControl(WIDGET_NAME, e=True, tabToControl=(le_component, -1))

    # if Maya <2017 - try to restore previous state
    elif mc.optionVar(ex=DOCKSTATE_OV):
        mc.dockControl(WIDGET_NAME, e=True, state=mc.optionVar(q=DOCKSTATE_OV))


# noinspection SpellCheckingInspection
def create_pose_board(show_it=True):
    if mocapx.pose_board is None:
        if control_command(WIDGET_NAME, q=True, ex=True):
            mc.deleteUI(WIDGET_NAME)

        mocapx.pose_board = DockableWrapPanel(PoseBoard())
        mocapx.pose_board.setObjectName(EDITOR_NAME)

    if show_it:
        if control_command(WIDGET_NAME, q=True, ex=True):
            check_and_set_dock_state()
            control_command(WIDGET_NAME, e=True, vis=True, r=True)
        else:
            command_template = "import mocapx\n" + \
                               "if mocapx.pose_board:" + \
                               "  mocapx.pose_board.{}()"

            # Maya >2017:
            if hasattr(mc, "workspaceControl"):
                mc.workspaceControl(WIDGET_NAME,
                                    requiredPlugin=MODULE_NAME,
                                    initialWidth=mc.optionVar(q='workspacesWidePanelInitialWidth'),
                                    minimumWidth=scaled(450),
                                    minimumHeight=scaled(350),
                                    label=TITLE_LABEL,
                                    uiScript='from mocapx.ui import pose_board\n'
                                             'pose_board.create_dock_control()',
                                    closeCommand=command_template.format("wc_closed"))
            # Maya <2017:
            else:
                mc.dockControl(WIDGET_NAME,
                               area="right",
                               visible=True,
                               content=EDITOR_NAME,
                               parent=mel.eval('$gMainPane=$gMainPane'),
                               floating=mc.optionVar(q=DOCKFLOAT_OV) if mc.optionVar(ex=DOCKFLOAT_OV) else 0,
                               label=TITLE_LABEL,
                               floatChangeCommand=command_template.format("wc_float_changed"),
                               closeCommand=command_template.format("wc_closed"))

            check_and_set_dock_state()
            control_command(WIDGET_NAME, e=True, r=True)

    return mocapx.pose_board


def create_dock_control():
    if mocapx.pose_board is None:
        mocapx.pose_board = DockableWrapPanel(PoseBoard())
        mocapx.pose_board.setObjectName(EDITOR_NAME)

    if mocapx.pose_board:
        parent = omui.MQtUtil.getCurrentParent()
        # noinspection PyCallByClass
        widget = omui.MQtUtil.findControl(EDITOR_NAME)

        # noinspection PyCompatibility,PyCallByClass
        omui.MQtUtil.addWidgetToMayaLayout(long_constr(widget), long_constr(parent))

        # Maya workspace control should never delete its content widget when
        # retain flag is true. But it still deletes in certain cases. We avoid
        # deleting the global widget by removing it from its parent's children.
        # destroyed signal is emitted right before deleting children.
        # noinspection PyCompatibility
        parent_widget = wrapInstance(long_constr(parent), QtWidgets.QWidget)
        if parent_widget:
            parent_widget.destroyed.connect(mocapx.pose_board.detach_me)
