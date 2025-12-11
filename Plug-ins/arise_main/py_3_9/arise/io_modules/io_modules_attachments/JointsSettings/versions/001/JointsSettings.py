"""JointsSettings exposes some settings of the joints infos such as
tagging it as skinning joint, it's radius, to template joint.
"""
import logging

from arise.data_types.attachment_data import AttachmentData

LOGGER = logging.getLogger("node_rig_logger")

MAYA_VERSION = 2016
AUTHOR = "Etay Herz"
RIG_TYPE = "Joints"
RIG_CATEGORY = "Build"
TAGS = ["joint", "joints", "radius", "template", "skinning", "attributes"]
TOOL_TIP = "Change settings of the node's joints such as: 'radius', 'skinning_jnt', 'template'."


class JointsSettings(AttachmentData):
    """Here we will reimplement methods to 1) create attributes on the attachment
    2) create guides in the template module and 3) the rig method where the rig will be built.
    """
    sort_priority = 1600

    def __init__(self, parent, icon, docs, module_dict):
        AttachmentData.__init__(
            self,
            parent=parent,
            icon=icon,
            docs=docs,
            module_dict=module_dict,
        )

    @staticmethod
    def attachment_permissions(node):
        """Return True or False if attachment allowed on node.

        Arguments:
            node {node shape pointer} -- node shape to check permission with

        Returns:
            bool -- True if allowed or False if not
        """
        if node.node_data.joints_manager.joints_info_list:
            return True

        module = __file__.rsplit("\\", 1)[-1].rsplit("/", 1)[-1].rsplit(".", 1)[0]
        LOGGER.warning(
            "Cannot add attachment '%s' to node '%s'. Node has no joints to operate on.",
            module, node.name,
        )
        return False

    @staticmethod
    def support_copy_settings():  # REIMPLEMENTED!
        """Return True if this attachment supports copying settings between nodes of same module.
        Reimplemented by subclasses that do support copy settings to return True. default is to return False.
        """
        return True

    def evaluate(self):  # REIMPLEMENTED!
        """Re-evaluate model. """
        AttachmentData.evaluate(self)
        self.tree_attr.update_model(self.joints_settings_model())

    def attributes_creation(self):  # REIMPLEMENTED!
        """Here you add the attributes. """
        self.tree_attr = self.add_tree_attribute("Joints Settings")

        self.add_button(
            buttons=[
                (
                    self.reset_changes,
                    "resources/icons/cancel_icon.png",
                    "Reset Changes",
                    "Remove any modifications done to this attachment.",
                ),
            ],
        )

    def attachment_creation(self):  # REIMPLEMENTED!
        """
        Attachments with Tree attributes don't need to do anything since tree attrs modify ctrls and joints
        before they are built (modifying the infos).
        """
        return

    def reset_changes(self):
        """Clear internal_database and refresh tree_attribute. """
        self.tree_attr.set_value_with_undo({})

    def joints_settings_model(self):
        """Return a joints model that BaseTreeWidget can use. """
        model_data = []
        for jnt_info in self.top_node_data.joints_manager:
            data = {
                "info_pointer": jnt_info,
                "name": jnt_info.default_name,
                "attrs": [
                    {
                        "name": "skinning_jnt",
                        "type": bool,
                        "default_value": jnt_info.data_dict["skinning_jnt"],
                        "change_pointer": (jnt_info.data_dict, "skinning_jnt"),
                    },
                    {
                        "name": "radius",
                        "type": float,
                        "range": [0, 1000],
                        "default_value": jnt_info.data_dict["radius"],
                        "change_pointer": (jnt_info.data_dict, "radius"),
                    },
                    {
                        "name": "template",
                        "type": bool,
                        "default_value": jnt_info.data_dict["template"],
                        "change_pointer": (jnt_info.data_dict, "template"),
                    },
                    {
                        "name": "label_side",
                        "type": list,
                        "range": ["Center", "Left", "Right", "None"],
                        "default_value": jnt_info.data_dict["label_side"],
                        "change_pointer": (jnt_info.data_dict, "label_side"),
                    },
                    {
                        "name": "enable_color",
                        "type": bool,
                        "default_value": jnt_info.data_dict["enable_jnt_color"],
                        "change_pointer": (jnt_info.data_dict, "enable_jnt_color"),
                    },
                    {
                        "name": "jnt_color",
                        "type": tuple,
                        "default_value": jnt_info.data_dict["color"],
                        "change_pointer": (jnt_info.data_dict, "color"),
                    },
                ],
            }

            model_data.append(data)

        return model_data
