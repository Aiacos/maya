"""CtrlsSettings exposes some settings of the ctrls infos such as
scaling, colors, line_width, ctrls shape,
"""
import logging

import maya.cmds as mc

from arise.data_types.attachment_data import AttachmentData
from arise.utils.ctrls_shapes_dict import CONTROLLER_SHAPES_DICT
from arise.utils.modules_utils import update_ctrls

LOGGER = logging.getLogger("node_rig_logger")

MAYA_VERSION = 2016
AUTHOR = "Etay Herz"
RIG_TYPE = "Ctrls"
RIG_CATEGORY = "Build"
TAGS = ["ctrl", "ctrls", "control", "color", "shape", "width", "line width", "scale"]
TOOL_TIP = """Change settings of the node's ctrls such as: 'scale', 'color', 'line width', 'shape'."""

UP_ORIENTS = ['+X', '-X', '+Y', '-Y', '+Z', '-Z']

AttachmentData.update_ctrls = update_ctrls


class CtrlsSettings(AttachmentData):
    """Here we will reimplement methods to 1) create attributes on the attachment
    2) create guides in the template module and 3) the rig method where the rig will be built.
    """
    sort_priority = 300

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
        if list(node.node_data.ctrls_manager):
            return True

        module = __file__.rsplit("\\", 1)[-1].rsplit("/", 1)[-1].rsplit(".", 1)[0]
        LOGGER.warning(
            "Cannot add attachment '%s' to node '%s'. Node has no ctrls to operate on.",
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
        self.tree_attr = self.add_tree_attribute("Ctrls Settings")
        self.add_button(
            buttons=[
                (
                    self.reset_changes,
                    "resources/icons/cancel_icon.png",
                    "Reset Changes",
                    "Reset any changes done on this attachment",
                ),
                (
                    self.update_ctrls,
                    "resources/icons/sync_icon.png",
                    "Update Ctrls",
                    "If the ctrls exist in the Maya scene, their shapes will update without requiring a rebuild.",
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
        enums = sorted([shape for shape in CONTROLLER_SHAPES_DICT.keys()], key=lambda x: (x != 'none', x))
        for ctrl_info in self.top_node_data.ctrls_manager:
            data = {
                "info_pointer": ctrl_info,
                "name": ctrl_info.data_dict["default_name"],
                "attrs": [
                    {
                        "name": "ctrl_shape",
                        "type": list,
                        "range": enums,
                        "default_value": ctrl_info.data_dict["shape"],
                        "change_pointer": (ctrl_info.data_dict, "shape"),
                    },
                    {
                        "name": "ctrl_color",
                        "type": tuple,
                        "default_value": ctrl_info.data_dict["color"],
                        "change_pointer": (ctrl_info.data_dict, "color"),
                    },
                    {
                        "name": "line_width",
                        "type": float,
                        "range": [-1.0, 100],
                        "default_value": ctrl_info.data_dict["line_width"],
                        "change_pointer": (ctrl_info.data_dict, "line_width"),
                    },
                    {
                        "name": "hide_history",
                        "type": bool,
                        "default_value": ctrl_info.data_dict["hide_history"],
                        "change_pointer": (ctrl_info.data_dict, "hide_history"),
                    },
                    {
                        "name": "ctrl_up_orient",
                        "type": list,
                        "range": UP_ORIENTS,
                        "default_value": ctrl_info.data_dict["up_orient"],
                        "change_pointer": (ctrl_info.data_dict, "up_orient"),
                    },
                    {
                        "name": "size_X",
                        "type": float,
                        "range": [0, 1000],
                        "default_value": ctrl_info.data_dict["size_x"],
                        "change_pointer": (ctrl_info.data_dict, "size_x"),
                    },
                    {
                        "name": "size_Y",
                        "type": float,
                        "range": [0, 1000],
                        "default_value": ctrl_info.data_dict["size_y"],
                        "change_pointer": (ctrl_info.data_dict, "size_y"),
                    },
                    {
                        "name": "size_Z",
                        "type": float,
                        "range": [0, 1000],
                        "default_value": ctrl_info.data_dict["size_z"],
                        "change_pointer": (ctrl_info.data_dict, "size_z"),
                    },
                    {
                        "name": "translate_X",
                        "type": float,
                        "range": [-1000, 1000],
                        "default_value": ctrl_info.data_dict["translate_offset_x"],
                        "change_pointer": (ctrl_info.data_dict, "translate_offset_x"),
                    },
                    {
                        "name": "translate_Y",
                        "type": float,
                        "range": [-1000, 1000],
                        "default_value": ctrl_info.data_dict["translate_offset_y"],
                        "change_pointer": (ctrl_info.data_dict, "translate_offset_y"),
                    },
                    {
                        "name": "translate_Z",
                        "type": float,
                        "range": [-1000, 1000],
                        "default_value": ctrl_info.data_dict["translate_offset_z"],
                        "change_pointer": (ctrl_info.data_dict, "translate_offset_z"),
                    },
                    {
                        "name": "rotate_X",
                        "type": float,
                        "range": [-1000, 1000],
                        "default_value": ctrl_info.data_dict["rotate_offset_x"],
                        "change_pointer": (ctrl_info.data_dict, "rotate_offset_x"),
                    },
                    {
                        "name": "rotate_Y",
                        "type": float,
                        "range": [-1000, 1000],
                        "default_value": ctrl_info.data_dict["rotate_offset_y"],
                        "change_pointer": (ctrl_info.data_dict, "rotate_offset_y"),
                    },
                    {
                        "name": "rotate_Z",
                        "type": float,
                        "range": [-1000, 1000],
                        "default_value": ctrl_info.data_dict["rotate_offset_z"],
                        "change_pointer": (ctrl_info.data_dict, "rotate_offset_z"),
                    },
                    {
                        "name": "tag_as_ctrl",
                        "type": bool,
                        "default_value": ctrl_info.data_dict["tag_as_ctrl"],
                        "change_pointer": (ctrl_info.data_dict, "tag_as_ctrl"),
                    },

                ],
            }

            model_data.append(data)

        return model_data
