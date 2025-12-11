"""Rename ctrls and joints. """

from arise.external_modules import six
import logging

from arise.pyside.QtCore import QRegExp

from arise.data_types.attachment_data import AttachmentData
from arise.node_data.info_and_io_data.ctrl_info import CtrlInfo
from arise.node_data.info_and_io_data.joint_info import JointInfo

LOGGER = logging.getLogger("node_rig_logger")

MAYA_VERSION = 2016
AUTHOR = "Etay Herz"
RIG_TYPE = "Customize"
RIG_CATEGORY = "Build"
TAGS = ["ctrls", "joints", "rename", "modify", "prefix", "name", "change"]
TOOL_TIP = """Rename ctrls and joints."""

CTRL_TXT = " [ctrl]"
JNT_TXT = " [joint]"

class Rename(AttachmentData):
    """Here we will reimplement methods to 1) create attributes on the attachment
    2) create guides in the template module and 3) the rig method where the rig will be built.
    """
    sort_priority = 400

    def __init__(self, parent, icon, docs, module_dict):
        AttachmentData.__init__(
            self,
            parent=parent,
            icon=icon,
            docs=docs,
            module_dict=module_dict,
        )

    @staticmethod
    def attachment_permissions(node):  # REIMPLEMENTED!
        """Return True or False if attachment allowed on node.

        Arguments:
            node {node shape pointer} -- node shape to check permission with

        Returns:
            bool -- True if allowed or False if not
        """
        if list(node.node_data.ctrls_manager) or list(node.node_data.joints_manager):
            return True

        module = __file__.rsplit("\\", 1)[-1].rsplit("/", 1)[-1].rsplit(".", 1)[0]
        LOGGER.warning(
            "Cannot add attachment '%s' to node '%s'. Node has no ctrls or joints to operate on.",
            module, node.name,
        )
        return False

    @staticmethod
    def support_copy_settings():  # REIMPLEMENTED!
        """Return True if this attachment supports copying settings between nodes of same module.
        Reimplemented by subclasses that do support copy settings to return True. default is to return False.
        """
        return True

    def attributes_creation(self):  # REIMPLEMENTED!
        """Here you add the attributes. """
        self.tree_attr = self.add_tree_attribute("Rename")
        self.add_button(
            buttons=[
                (
                    self.reset_changes,
                    "resources/icons/cancel_icon.png",
                    "Reset Changes",
                    "Reset any changes done on this attachment",
                ),
            ],
        )

    def evaluate(self):  # REIMPLEMENTED!
        """Re-evaluate model. """
        AttachmentData.evaluate(self)
        self.tree_attr.update_model(self.ctrls_settings_model())

    def attachment_creation(self):
        """Attachments with Tree attributes don't need to do anything since tree attrs modify ctrls and joints
        before they are built (modifying the infos).
        """
        return

    def reset_changes(self):
        """Clear internal_database and refresh tree_attribute. """
        self.tree_attr.set_value_with_undo({})

    def ctrls_settings_model(self):
        """Return a ctrls settings model that BaseTreeWidget can use. """
        model_data = []

        ctrls_manager = self.top_node_data.ctrls_manager
        joints_manager = self.top_node_data.joints_manager
        for manager, suffix in [[ctrls_manager, CTRL_TXT], [joints_manager, JNT_TXT]]:
            for info in manager:
                data = {
                    "info_pointer": info,
                    "name": "{0} {1}".format(info.data_dict["default_name"], suffix),
                    "attrs": [
                        {
                            "name": "prefix",
                            "type": str,
                            "default_value": info.data_dict["prefix"],
                            "change_pointer": (info.data_dict, "prefix"),
                            "range": QRegExp("^$|^[A-Za-z_][A-Za-z0-9_]{0,45}$"),
                        },
                        {
                            "name": "name",
                            "type": str,
                            "default_value": info.data_dict["default_name"],
                            "change_pointer": (self.change_name_with_checks, [info]),
                            "range": QRegExp("[A-Za-z_][A-Za-z0-9_]{2,45}")
                        },
                        {
                            "name": "suffix",
                            "type": str,
                            "default_value": info.data_dict["suffix"],
                            "change_pointer": (info.data_dict, "suffix"),
                            "range": QRegExp("^$|^[A-Za-z_][A-Za-z0-9_]{0,45}$"),
                        },
                    ],
                }

                model_data.append(data)

        return model_data

    @staticmethod
    def change_name_with_checks(value, info):
        """Change name with checks.

        Arguments:
            value {str} -- New name. Automatically passed by the tree attribute.
            info {CtrlInfo or JointInfo} -- Info to change name on. extra vars passed by the tree attribute.

        Returns:
            bool -- True if name was changed successfully. False if not. So tree can remove modifications.
        """
        if value == info.name:
            return False

        if not isinstance(value, six.string_types) and not len(value) >= 3:
            msg = "[Rename] 'name' argument must be at least 3 characters. Got '{0}'".format(value)
            LOGGER.warning(msg)
            return False

        if value in info.manager.get_info_names():
            type_txt = "Ctrl" if isinstance(info, CtrlInfo) else "Joint"
            LOGGER.warning("[Rename] %s with name '%s' already exists. Reverting to default", type_txt, value)
            return False

        info.name = value
        return True
