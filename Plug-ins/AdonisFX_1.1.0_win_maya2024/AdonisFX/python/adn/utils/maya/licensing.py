import os

import maya.cmds as cmds

from adn.ui.widgets.dialogs import msg_box
from adn.ui.maya.window import main_window
from adn.ui.utils import cursor


def activate_license():
    """This method provides the ability to activate the product from the UI.
    This is a functionality for manual activation, meaning that it is only
    supported in node-locked interactive licenses.
    Before launching the activation dialogs, it checks if the
    license is already activated and valid. If so, the activation process
    is skipped. This check is supported in node-locked and floating licenses.
    """
    # Check if license is active and valid (node-locked and floating)
    with cursor.wait_cursor_context():
        result = cmds.AdnLicense(query=True)
    if result:
        msg_box(main_window(), "info", "Your license is already activated.")
        return

    # In floating mode, there is nothing to activate from this context
    if os.getenv("ADN_LICENSE_MODE", "0") == "1":
        msg_box(main_window(), "error",
                "Could not validate your floating license. "
                "Please, check the console for more information.")
        return

    # Check if license is in trial period (node-locked only)
    with cursor.wait_cursor_context():
        result = cmds.AdnLicense(query=True, trial=True)
    if result:
        activate_now = msg_box(main_window(), "question",
                               "Your license is in trial period. "
                               "Do you want to activate your product now?")
        if not activate_now:
            return

    # Launch interactive dialogs to activate the full license
    cmds.AdnLicense()


def check_license():
    """Checks if the license is valid including node-locked and floating, as
    well as trial period. This method does not require UI which means that
    it can be executed in batch mode too.

    Returns:
        bool: True if the license has been verified, False otherwise.
    """
    # Check if license is active and valid (node-locked and floating)
    with cursor.wait_cursor_context():
        result = cmds.AdnLicense(query=True)
    if result:
        return True
    # Check if license is in trial period (node-locked only)
    if os.getenv("ADN_LICENSE_MODE", "0") != "1":
        with cursor.wait_cursor_context():
            result = cmds.AdnLicense(query=True, trial=True)
        if result:
            return True

    # Extra check: confirm that AdonisFX nodes are registered
    return cmds.pluginInfo("AdonisFX", query=True, dependNode=True) != None
