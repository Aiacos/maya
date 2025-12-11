"""PostScript allows the user to script his own modifications in python to the rig. """

import os
from functools import partial

from maya import cmds

from arise.data_types.attachment_data import AttachmentData
from arise.utils.decorators_utils import undo_chunk_dec, catch_and_print_error_dec, pause_maya_editors_dec
from arise.utils.post_script_utils import SearchReplaceUI, search_and_replace
from arise.utils import ui_utils

MAYA_VERSION = 2016
AUTHOR = "Etay Herz"
RIG_TYPE = "Script"
RIG_CATEGORY = "Post Script"
TAGS = ["post", "script", "scripting", "python", "code", "editor", ]
TOOL_TIP = "Modify the rig by running a Python script."

EXECTION_ORDERS = ["After Build Pass", "After Connection Pass (Default)", "Final Pass"]


class PostScript(AttachmentData):
    """Here we will reimplement methods to 1) create attributes on the attachment
    2) create guides in the template module and 3) the rig method where the rig will be built.
    """
    sort_priority = 700

    def __init__(self, parent, icon, docs, module_dict):
        AttachmentData.__init__(
            self,
            parent=parent,
            icon=icon,
            docs=docs,
            module_dict=module_dict
        )

    @property
    def category(self):  # REIMPLEMENTED!
        """Returns the category number. 1-'build', 2-'finalize', 3-'post', 4-'script'. """
        return 4

    @staticmethod
    def attachment_permissions(node):  # REIMPLEMENTED!
        """Return True or False if attachment allowed on node.

        Arguments:
            node {node_ptr} -- node to check permission with

        Returns:
            [bool] -- True if allowed or False if not
        """
        return True

    @staticmethod
    def support_multi_instences_on_node():  # REIMPLEMENTED!
        """Only one attachment of this type is allowed. """
        return False

    @staticmethod
    def support_copy_settings():  # REIMPLEMENTED!
        """Return True if this attachment supports copying settings between nodes of same module.
        Reimplemented by subclasses that do support copy settings to return True. default is to return False.
        """
        return True

    def add_qactions(self, menu):  # REIMPLEMENTED!
        """Add custom QActions to right-click context menu for this specific attachment. OPTIONAL.

        Args:
            menu (QMenu): This method will be passed the QMenu of the context menu
        """
        menu.addSection("PostScript Search & Replace")

        action_btn, action_B_btn, option_btn = ui_utils.action_with_options(
            menu=menu,
            action_label="Replace L > R",
            action_tooltip="Find and replace Left to Right text in this PostScript",
            action_B_label="Replace R > L",
            action_B_tooltip="Find and replace Right to Left text in this PostScript",
            options_tooltip="Options for searching & replacing",
            icon=self.main_window_ptr.swap_icon,
        )
        action_btn.released.connect(partial(search_and_replace, self, True))
        action_B_btn.released.connect(partial(search_and_replace, self, False))
        option_btn.released.connect(partial(SearchReplaceUI, self.main_window_ptr))

    def attributes_creation(self):  # REIMPLEMENTED!
        """Here you add the attributes. """

        self.add_collapsible_layout(
            title="Settings",
            shown=True,
        )
        self.exec_order_attr = self.add_drop_down_attribute(
            name="Execution Order",
            items=EXECTION_ORDERS,
            default_value=EXECTION_ORDERS[1],
            annotation=(
                "PostScripts can be executed at various stages:\n"
                "'After Build Pass' - After nodes creation pass, pre-connection pass.\n"
                "'After Connection Pass (Default)' - Post-connection pass, pre-weight transfer pass.\n"
                "'Final Pass' - Concluding step after Arise completes all passes, acting on the visible rig."
            ),
        )
        self.use_file_attr = self.add_boolean_attribute(
            name="Use File",
            default_value=False,
            annotation="Instead of using the code editor, load code from a '.py' file.",
        )
        self.script_path_attr = self.add_path_attribute(
            name="script file path",
            file_types="PY File (*.py)",
            annotation="Python script file path (.py)",
        )

        self.add_collapsible_layout(
            title="Script Editor",
            shown=True,
        )

        self.script_editor_attr = self.add_script_attribute(
            name="Post Script",
            default_value="",
            annotation="Add code to run at the end of build.",
        )

        self.close_layout()
        self.close_layout()

    def evaluate(self):  # REIMPLEMENTED!
        """Enable or disable editor based on checkbox. """
        AttachmentData.evaluate(self)
        if self.use_file_attr.value is True:
            self.script_path_attr.set_disabled(False)
            self.script_editor_attr.set_disabled(True)
        else:
            self.script_path_attr.set_disabled(True)
            self.script_editor_attr.set_disabled(False)

    def attachment_creation(self):  # REIMPLEMENTED!
        """Execute code in editor or from file. """
        if self.use_file_attr.value is True:  # file path.
            path = self.script_path_attr.value

            if not path.endswith(".py"):
                return "no python script file specified ('.py'). got '{0}' skipping attachment.".format(path)

            if not os.path.isfile(path):
                return "cannot find python script file '{0}'. skipping attachment.".format(path)

            with open(path, "r") as script_file:
                code_text = script_file.read()

        else:  # code editor.
            code_text = self.script_editor_attr.value

        print("#__________[postScript] '{0}' {1} __________#".format(self.long_name, "start:"))  # keep.
        result = self.execute_code(code_text=code_text)
        print("#__________[postScript] '{0}' {1} __________#\n".format(self.long_name, "end"))  # keep.

        if result is True:
            return True

        return False

    @pause_maya_editors_dec
    @undo_chunk_dec
    @catch_and_print_error_dec
    def execute_code(self, code_text):
        """Execute the code and pass the exec variables of node.

        Arguments:
            code_text {str} -- code to execute

        Returns:
            [bool] -- True if success
        """
        added_globals = globals().copy()
        added_globals.update(self.get_local_parms())

        exec(code_text, added_globals)

        return True

    def get_local_parms(self):
        """Return a dict with params that can be used by the code on execution. """
        local_parms = {
            "node_name": self.top_node_data.name,
            "module_grp": self.top_node_data.module_grp,
            "node_version": self.top_node_data.version_attribute.value,
            "ctrls_list": [ctrl.transform for ctrl in self.top_node_data.ctrls_manager.io_ctrls_list],
            "joints_list": self.top_node_data.joints_manager.io_joints_list,
            "ctrls_suffix": self.top_node_data.scene_ptr.ctrl_suffix,
            "joints_suffix": self.top_node_data.scene_ptr.jnt_suffix,
            "cmds": cmds,
            "mc": cmds,
        }

        return local_parms
