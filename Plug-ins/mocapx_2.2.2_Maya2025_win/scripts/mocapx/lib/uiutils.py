import os
import maya.cmds as mc
from maya import OpenMayaUI as omui
from maya.api import OpenMaya
from maya.api import OpenMayaAnim


# noinspection PyUnresolvedReferences
# pylint: disable=no-name-in-module
from mocapx.vendor.Qt import QtGui, QtWidgets, QtCore, QtCompat
from mocapx.lib.utils import get_mplug, long_constr
import mocapx

# pylint: enable=no-name-in-module

SCALE = None

COLOR_GROUPS = [
    "Disabled",
    "Active",
    "Inactive"]

# noinspection SpellCheckingInspection
COLOR_ROLES = [
    "Window",
    "WindowText",
    "Base",
    "AlternateBase",
    "ToolTipBase",
    "ToolTipText",
    "Text",
    "Button",
    "ButtonText",
    "BrightText",
    "Light",
    "Midlight",
    "Dark",
    "Shadow",
    "Highlight",
    "HighlightedText",
    "Link",
    "LinkVisited",
    "NoRole"]


class RegExValidator(QtGui.QRegExpValidator):
    def __init__(self, *args, **kwargs):
        super(RegExValidator, self).__init__(*args, **kwargs)

    def validate(self, _input, _pos):
        state = super(RegExValidator, self).validate(_input, _pos)
        if state[0] == QtGui.QValidator.State.Intermediate:
            return QtGui.QValidator.State.Acceptable, state[1], state[2]
        return state


def scale():
    global SCALE
    if SCALE is None:
        SCALE = mc.mayaDpiSetting(query=True, realScaleValue=True)
    return SCALE


def scaled(value):
    return int(round(value * (scale() or 1)))


def find_icon(icon_name):
    icon_path = os.path.join(mocapx.plugin_distr_root, 'icons')
    if os.path.exists(icon_path):
        files = os.listdir(icon_path)
        if files:
            if scale() >= 1.75:
                suffixes = ("_200", "_150", "_100")
            elif scale() >= 1.25:
                suffixes = ("_150", "_100")
            else:
                suffixes = ("_100",)
            found_file = None
            if suffixes:
                for suffix in suffixes:
                    if found_file:
                        break
                    suffixed_name = "{}{}".format(icon_name, suffix)
                    for filename in files:
                        if os.path.splitext(filename)[0] == suffixed_name:
                            found_file = filename
                            break
            if not found_file:
                for filename in files:
                    if os.path.splitext(filename)[0] == icon_name:
                        found_file = filename
            if found_file:
                return os.path.join(icon_path, found_file).replace('\\', '/')
    return None


def is_widget_minimized(widget):
    if widget.isMinimized():
        return True
    parent = widget.parent()
    if parent:
        return is_widget_minimized(parent)
    return False


def is_widget_really_visible(widget):
    if widget.isHidden():
        return False
    if widget.visibleRegion().isEmpty():
        return False
    if is_widget_minimized(widget):
        return False

    # is widget outside the screens area
    for screen in QtWidgets.QApplication.screens():
        screen_rect = screen.geometry()
        widget_rect = widget.geometry()
        widget_rect.moveTopLeft(widget.mapToGlobal(widget_rect.topLeft()))
        if screen_rect.intersects(widget_rect):
            return True
    return False


def generate_style_sheet(class_name=None, data=None):
    if data:
        settings = ";".join(["{}: {}".format(key, value) for key, value in data.items()])
        if class_name is not None:
            settings = "{} {{{}}}".format(class_name, settings)
        return settings
    return ""


def get_indicator_color_from_plug(plug):
    m_plug = get_mplug(plug)
    if not m_plug.isNull:
        if m_plug.isLocked:
            return {"color": "black", "background-color": "rgb(92, 104, 116)"}
        else:
            incoming_plug = m_plug.source()
            if not incoming_plug.isNull:
                incoming_m_object = incoming_plug.node()
                incoming_m_type = incoming_m_object.apiType()
                if incoming_m_type == OpenMaya.MFn.kMute:
                    return {"color": "black", "background-color": "rgb(191, 161, 130)"}
                elif incoming_m_type == OpenMaya.MFn.kAnimCurveTimeToAngular or \
                        incoming_m_type == OpenMaya.MFn.kAnimCurveTimeToDistance or \
                        incoming_m_type == OpenMaya.MFn.kAnimCurveTimeToTime or \
                        incoming_m_type == OpenMaya.MFn.kAnimCurveTimeToUnitless:
                    m_curve = OpenMayaAnim.MFnAnimCurve(incoming_m_object)
                    key_index = m_curve.find(OpenMayaAnim.MAnimControl.currentTime())
                    if key_index is not None:
                        if m_curve.value(key_index) == m_plug.asDouble():
                            return {"color": "rgb(187, 187, 165)", "background-color": "rgb(205, 39, 41)"}
                        else:
                            return {"color": "black", "background-color": "rgb(253, 203, 196)"}
                    else:
                        return {"color": "black", "background-color": "rgb(221, 114, 122)"}
                elif incoming_m_type == OpenMaya.MFn.kAnimCurveUnitlessToAngular or \
                        incoming_m_type == OpenMaya.MFn.kAnimCurveUnitlessToDistance or \
                        incoming_m_type == OpenMaya.MFn.kAnimCurveUnitlessToTime or \
                        incoming_m_type == OpenMaya.MFn.kAnimCurveUnitlessToUnitless:
                    return {"color": "black", "background-color": "rgb(80, 153, 218)"}
                elif incoming_m_type == OpenMaya.MFn.kExpression:
                    return {"color": "black", "background-color": "rgb(203, 165, 241)"}
                elif incoming_m_object.hasFn(OpenMaya.MFn.kConstraint):
                    return {"color": "black", "background-color": "rgb(163, 203, 240)"}
                elif incoming_m_type == OpenMaya.MFn.kPairBlend:
                    return {"color": "black", "background-color": "rgb(172, 241, 172)"}
                else:
                    return {"color": "black", "background-color": "rgb(241, 241, 165)"}
    return dict()


def draw_rounded_rect(painter, widget, margin, angle_factor):
    w = widget.width() - margin * 2
    h = widget.height() - margin * 2
    painter.drawRoundedRect(margin, margin, w, h, h * angle_factor, h * angle_factor)


def get_application_palette():
    # on Maya 2018 no service pack windows QtWidgets.QApplication.palette()
    # fails with the error : palette() takes exactly one argument (0 given)
    # so in case of the error we are trying to submit None as an argument
    try:
        palette = QtWidgets.QApplication.palette()
    except TypeError as er:
        palette = QtWidgets.QApplication.palette(None)
    return palette


# noinspection PyPep8Naming
def get_color_from_maya_palette(c_role, c_group="Active", palette=None, getRgb=False):
    if not palette:
        palette = get_application_palette()

    q_role = getattr(QtGui.QPalette, c_role)
    q_group = getattr(QtGui.QPalette, c_group)
    color = palette.color(q_group, q_role)

    if getRgb:
        color = color.getRgb()

    return color


# noinspection PyPep8Naming
def get_maya_palette(palette=None, getRgb=False):
    if not palette:
        palette = get_application_palette()

    p_colors = {}

    for c_role in COLOR_ROLES:
        for c_group in COLOR_GROUPS:
            p_colors[c_role + "." + c_group] = get_color_from_maya_palette(c_role, c_group, palette, getRgb)

    return p_colors


def set_color_palette(widget, c_role, q_color, c_group="Active", reset_palette=False):
    q_role = getattr(QtGui.QPalette, c_role)
    q_group = getattr(QtGui.QPalette, c_group)

    palette = QtGui.QPalette() if reset_palette else widget.palette()
    palette.setColor(q_group, q_role, q_color)

    widget.setAutoFillBackground(True)
    widget.setPalette(palette)


def set_color_palette_lighter(widget, c_role, factor, c_group="Active", reset_palette=False):
    palette = QtGui.QPalette() if reset_palette else widget.palette()
    q_color = get_color_from_maya_palette(c_role, c_group, palette).lighter(factor)
    set_color_palette(widget, c_role, q_color, c_group)


def set_color_palette_darker(widget, c_role, factor, c_group="Active", reset_palette=False):
    palette = QtGui.QPalette() if reset_palette else widget.palette()
    q_color = get_color_from_maya_palette(c_role, c_group, palette).darker(factor)
    set_color_palette(widget, c_role, q_color, c_group)


def get_widget(widget_name):
    ptr = omui.MQtUtil.findLayout(widget_name)
    widget = QtCompat.wrapInstance(int(ptr), QtWidgets.QWidget)
    return widget


# noinspection SpellCheckingInspection
def create_attr_outliner(select_command=None, close_command=None, state_option=None):
    pane = mc.window()
    if close_command:
        mc.window(pane, e=True, closeCommand=close_command)

    if state_option and mc.optionVar(exists=state_option):
        mc.window(pane, e=True, state=mc.optionVar(q=state_option))

    form = mc.formLayout(numberOfDivisions=100)
    outliner = mc.nodeOutliner(
        showOutputs=True,
        showNonKeyable=True,
        showHidden=False,
        showNonConnectable=False)

    if select_command:
        mc.nodeOutliner(outliner, e=True, selectCommand=select_command)

    mc.formLayout(
        form,
        edit=True,
        attachForm=[
            (outliner, "top", 5),
            (outliner, "left", 5),
            (outliner, "bottom", 5),
            (outliner, "right", 5)])

    return pane, outliner


def window_exists(window_name):
    return mc.window(window_name, exists=True)


# noinspection SpellCheckingInspection
def set_connected_plug(outliner, attached_plug):
    mc.nodeOutliner(outliner, e=True, connectivity=attached_plug)


# noinspection SpellCheckingInspection
def set_connected_node(outliner, node):
    mc.nodeOutliner(outliner, e=True, replace=node)


# noinspection SpellCheckingInspection
def selection(outliner):
    return mc.nodeOutliner(outliner, q=True, lastClickedNode=True)


def show(window):
    mc.showWindow(window)


def confirm_dialog(*args, **kwargs):
    return mc.confirmDialog(*args, **kwargs)


# noinspection PyCallByClass, SpellCheckingInspection
def create_sel_changed_cb(cd):
    cbid = OpenMaya.MEventMessage.addEventCallback("SelectionChanged", cd, clientData=None)
    return cbid


# noinspection SpellCheckingInspection
def remove_cb(cbid):
    OpenMaya.MMessage.removeCallback(cbid)


def set_window_title(window, title):
    return mc.window(window, e=True, title=title)


def save_window_state(window):
    return mc.window(window, q=True, state=True)


def load_window_state(window, state_info):
    return mc.window(window, e=True, state=state_info)


def get_maya_window():
    maya_main_window_ptr = omui.MQtUtil.mainWindow()
    # noinspection PyCompatibility
    return QtCompat.wrapInstance(long_constr(maya_main_window_ptr), QtWidgets.QWidget)


def ask_user_confirm(message):
    answer = mc.confirmDialog(
        title='Confirm',
        message=message,
        button=('Continue', 'Cancel'),
        defaultButton='Continue',
        cancelButton='Cancel',
        dismissString='Continue')

    if answer == 'Continue':
        return True
    else:
        return False


def show_warning(msg):
    mc.warning(msg)


def show_error(msg):
    OpenMaya.MGlobal.displayError(msg)


class DebugPane(QtWidgets.QDialog):
    def __init__(self, widget, parent=None):
        super(DebugPane, self).__init__(parent)
        self.widget = widget
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(scaled(6), scaled(6), scaled(6), scaled(6))
        layout.setSpacing(scaled(6))
        layout.addWidget(self.widget)
        self.setLayout(layout)

    # noinspection PyPep8Naming,PyUnusedLocal
    def closeEvent(self, event):
        self.widget.clean_callbacks()


def build_maya_pane(widget):
    return DebugPane(widget, parent=get_maya_window())
