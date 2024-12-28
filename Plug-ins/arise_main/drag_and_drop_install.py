"""Create a Maya shelf button that will start the tool UI. """

import os
import sys

if "PySide2" in sys.modules: # pySide2. Maya 2018-2024
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
    import shiboken2
    import maya.OpenMayaUI as omui

    MAYA_MAIN_WINDOW = shiboken2.wrapInstance(int(omui.MQtUtil.mainWindow()), QWidget)

else: # PySide6. Maya 2025+
    from PySide6.QtGui import *
    from PySide6.QtCore import *
    from PySide6.QtWidgets import *

    MAYA_MAIN_WINDOW = None
    for widget in QApplication.instance().topLevelWidgets():
        if widget.objectName() == "MayaWindow":
            MAYA_MAIN_WINDOW = widget
            break


import maya.cmds as mc
from maya import mel

SHELF_NAME = "Arise"
START_PATH = ""
if __name__ != "__main__":  # support running from scriptEditor.
    START_PATH = os.path.split(__file__)[0].replace("\\", "/")


ARISE_CODE = """
import sys
import os

LOCAL_PATH = r"{0}"
version_folder = 'py_' + str(sys.version_info.major) + '_' + str(sys.version_info.minor)
path = os.path.join(LOCAL_PATH, version_folder)

if path not in sys.path:
    sys.path.append(path)

from arise.ui_elements import ior_main_window

# load UI.
try:
    Arise.deleteLater()
    print("deleting old UI")
except:
    pass

Arise = ior_main_window.IORMainWindow(
    parent_to_maya=None, # can be (True, False, None)
    always_on_top=None, # can be (True, False, None)
    log_feedback_level="info",
    default_settings=False,
    )
Arise.show_()
"""


VALIDATION_CODE = """
import sys
import os

LOCAL_PATH = r"{0}"
version_folder = 'py_' + str(sys.version_info.major) + '_' + str(sys.version_info.minor)
path = os.path.join(LOCAL_PATH, version_folder)

if path not in sys.path:
    sys.path.append(path)

from arise.model_updater.model_validation.ui import validation_main_window

# load UI.
try:
    validation_ui.deleteLater()
except:
    pass

validation_ui = validation_main_window.ValidationMainWindow()
"""


BIND_POSE_CODE = """
import sys
import os

LOCAL_PATH = r"{0}"
version_folder = 'py_' + str(sys.version_info.major) + '_' + str(sys.version_info.minor)
path = os.path.join(LOCAL_PATH, version_folder)

if path not in sys.path:
    sys.path.append(path)

from arise.utils.ctrls_utils import apply_bind_pose_all

apply_bind_pose_all(silent=True)
"""


BIND_POSE_TRANS_CODE = """
import sys
import os

LOCAL_PATH = r"{0}"
version_folder = 'py_' + str(sys.version_info.major) + '_' + str(sys.version_info.minor)
path = os.path.join(LOCAL_PATH, version_folder)

if path not in sys.path:
    sys.path.append(path)

from arise.utils.ctrls_utils import apply_bind_pose_all

apply_bind_pose_all(silent=True, only_trans=True)
"""


ZERO_POSE_CODE = """
import sys
import os

LOCAL_PATH = r"{0}"
version_folder = 'py_' + str(sys.version_info.major) + '_' + str(sys.version_info.minor)
path = os.path.join(LOCAL_PATH, version_folder)

if path not in sys.path:
    sys.path.append(path)

from arise.utils.ctrls_utils import apply_zero_pose_all

apply_zero_pose_all(silent=True)
"""


INFO_TEXT = (
    "To create the 'Arise' shelf insert the full path to the 'arise_main' folder.\n"
    "[<PATH>/arise_main]\n"
)


def onMayaDroppedPythonFile(_):
    """Not all versions of Maya support this but for 2022+ will popup again if dropped again. """
    if sys.version_info.major >= 3:
        shelf_ui = UiPathWidget()
        shelf_ui.show()


class UiPathWidget(QWidget):
    """Allows user to input path to 'arise' folder path to auto create shelf buttons. """
    def __init__(self):
        QWidget.__init__(self, parent=MAYA_MAIN_WINDOW, f=Qt.Dialog)
        self.setMinimumSize(QSize(350, 90))
        self.setWindowModality(Qt.WindowModal)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle("Enter the path to the 'arise_main' folder")

        self.main_layout = QGridLayout(self)
        self.setLayout(self.main_layout)

        self.main_layout.addWidget(QLabel(INFO_TEXT, self), 0, 0)

        self.line_edit = QLineEdit(self)
        self.main_layout.addWidget(self.line_edit, 1, 0)
        self.line_edit.setText(str(START_PATH))

        self.path_btn = QPushButton("Find Folder", self)
        self.path_btn.clicked.connect(self.open_search_window)
        self.main_layout.addWidget(self.path_btn, 1, 1)

        self.create_btn = QPushButton("Create Shelf Buttons", self)
        self.create_btn.clicked.connect(self.create_shelf_btn)
        self.main_layout.addWidget(self.create_btn, 2, 0)


    def open_search_window(self):
        """Open a search path to allow user to pick the folder. """
        new_path = QFileDialog.getExistingDirectory(
            self,
            "Select the 'arise_main' folder",
            None,
            QFileDialog.ShowDirsOnly | QFileDialog.ReadOnly,
        )

        if new_path:
            self.line_edit.setText(str(new_path))

    def create_shelf_btn(self):
        """Based on line_edit text create a shelf button. """
        path = self.line_edit.text().strip()
        ver_folder = "py_{0}_{1}".format(sys.version_info.major, sys.version_info.minor)
        version_path = os.path.join(path, ver_folder, "arise")

        # checks.
        if not path:
            mc.warning("Invalid path")
            return

        if not os.path.isdir(path):
            mc.warning("Invalid path. got '{0}'".format(path))
            return

        if not os.path.isfile(os.path.join(version_path, "ui_elements", "ior_main_window.pyc")):
            mc.warning("Couldn't find needed files in folder. aborting shelf creation!")
            return

        maya_shelf_top_lvl = mel.eval("$tmpVar=$gShelfTopLevel")

        # delete shelf if exists.
        if SHELF_NAME in mc.tabLayout(maya_shelf_top_lvl, q=True, childArray=True):
            mc.deleteUI(SHELF_NAME, layout=True)

        # create shelf.
        mc.shelfLayout(SHELF_NAME, parent=maya_shelf_top_lvl)

        mc.shelfButton(
            commandRepeatable=True,
            image1=os.path.join(version_path, "resources", "icons", "arise_logo_32pix.png"),
            label="Arise",
            annotation="Arise Rigging System",
            parent=SHELF_NAME,
            sourceType="python",
            command=ARISE_CODE.format(path),
            imageOverlayLabel="Arise",
            overlayLabelColor=(0.95, 0.95, 0.95),
            overlayLabelBackColor=(0.0, 0.0, 0.0, 0.4),
            font="tinyBoldLabelFont",
        )

        icon_path = os.path.join(
            version_path, "model_updater", "model_validation", "resources", "model_validation_icon.png"
        )
        mc.shelfButton(
            commandRepeatable=True,
            image1=icon_path,
            label="Model Validation",
            annotation="Model Validation Checks",
            parent=SHELF_NAME,
            sourceType="python",
            command=VALIDATION_CODE.format(path),
            imageOverlayLabel="Valid",
            overlayLabelColor=(0.95, 0.95, 0.95),
            overlayLabelBackColor=(0.0, 0.0, 0.0, 0.4),
            font="tinyBoldLabelFont",
        )

        mc.shelfButton(
            commandRepeatable=True,
            image1=os.path.join(version_path, "resources", "icons", "bind_pose_icon.png"),
            label="BindPose",
            annotation="Set all ctrls in scene to bind pose",
            parent=SHELF_NAME,
            sourceType="python",
            command=BIND_POSE_CODE.format(path),
            imageOverlayLabel="BindPose",
            overlayLabelColor=(0.95, 0.95, 0.95),
            overlayLabelBackColor=(0.0, 0.0, 0.0, 0.4),
            font="tinyBoldLabelFont",
        )

        mc.shelfButton(
            commandRepeatable=True,
            image1=os.path.join(version_path, "resources", "icons", "bind_pose_icon.png"),
            label="BP TRANS",
            annotation="Set all ctrls in scene to bind pose (Transformation values only)",
            parent=SHELF_NAME,
            sourceType="python",
            command=BIND_POSE_TRANS_CODE.format(path),
            imageOverlayLabel="BP (Trans)",
            overlayLabelColor=(0.95, 0.95, 0.95),
            overlayLabelBackColor=(0.0, 0.0, 0.0, 0.4),
            font="tinyBoldLabelFont",
        )

        mc.shelfButton(
            commandRepeatable=True,
            image1=os.path.join(version_path, "resources", "icons", "zero_pose_icon.png"),
            label="ZeroPose",
            annotation="Set all ctrls in scene to zero pose",
            parent=SHELF_NAME,
            sourceType="python",
            command=ZERO_POSE_CODE.format(path),
            imageOverlayLabel="ZeroPose",
            overlayLabelColor=(0.95, 0.95, 0.95),
            overlayLabelBackColor=(0.0, 0.0, 0.0, 0.4),
            font="tinyBoldLabelFont",
        )

        mc.saveShelf(SHELF_NAME, "{0}shelf_{1}".format(mc.internalVar(userShelfDir=True), SHELF_NAME))
        self.close()


if sys.version_info.major == 2 or __name__ == "__main__":  # support running from scriptEditor.
    SHELF_UI = UiPathWidget()
    SHELF_UI.show()
