import sys

import maya.cmds as cmds
import maya.OpenMayaUI as OpenMayaUI

try:
    from PySide6 import QtWidgets
    from shiboken6 import wrapInstance
except ImportError:
    from PySide2 import QtWidgets
    from shiboken2 import wrapInstance

from adn.utils.constants import UiConstants


def main_window():
    """Gets the memory address of the maya main window and returns the wrapped
    instance as widget.

    Returns:
        :obj:`QWidget`: maya main window.
    """
    maya_main_window_ptr = OpenMayaUI.MQtUtil.mainWindow()
    if sys.version_info[0] >= 3:
        address = int(maya_main_window_ptr)
    else:
        address = long(maya_main_window_ptr)
    maya_main_window = wrapInstance(address, QtWidgets.QWidget)
    return maya_main_window


def main_window_name():
    """Returns the Maya window name.

    Raises:
        RuntimeError: Maya window name changed and we can not retrieve it
        using PyMel.

    Returns:
        str: Name of the maya main window.
    """
    if cmds.window("MayaWindow", exists=True):
        return "MayaWindow"
    else:
        # Maya software changed name of main window between versions.
        from pymel.core.language import melGlobals as mel_globals
        if "gMainWindow" not in mel_globals.keys():
            raise RuntimeError("{0} Could not retrieve maya main window "
                               "name".format(UiConstants.LOG_PREFIX))
        return mel_globals["gMainWindow"]
