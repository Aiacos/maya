"""AttributesSettings allows user to modify custom Maya attributes on the node. """
import logging

from arise.data_types.attachment_data import AttachmentData

LOGGER = logging.getLogger("node_rig_logger")

MAYA_VERSION = 2016
AUTHOR = "Etay Herz"
RIG_TYPE = "Ctrls"
RIG_CATEGORY = "Build"
TAGS = ["ctrls", "control", "attribute", "custom", "modify", "value", "hide", "lock", "keyable", "default"]
TOOL_TIP = (
    "Modify Maya attributes on ctrls associated with the node.\n"
    "You can change the value, keyable, lock and hidden state of the attribute.\n"
    "For example, you can change the 'Ik_Fk_Switch' attribute value from 0 to 1."
)

TREE_STR_TO_DATA_TYPE = {
    "bool": bool,
    "long": float,  # TODO: tree attr doesn't support int type. Add support?
    "float": float,
    "enum": list,
}


class AttributesSettings(AttachmentData):
    """Here we will reimplement methods to 1) create attributes on the attachment
    2) create guides in the template module and 3) the rig method where the rig will be built.
    """
    sort_priority = 350

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
        self.tree_attr = self.add_tree_attribute("Attributes Settings")
        self.add_button(
            buttons=[
                (
                    self.reset_changes,
                    "resources/icons/cancel_icon.png",
                    "Reset Changes",
                    "Remove any changes done on this attachment",
                ),
            ],
        )

    def evaluate(self):  # REIMPLEMENTED!
        """Re-evaluate model. """
        AttachmentData.evaluate(self)
        self.tree_attr.update_model(self.ctrls_custom_attrs_model())

    def attachment_creation(self):
        """
        Some attachments with Tree attributes don't need to do anything since the tree attrs modify
        ctrls, joints and Maya attrs before they are built (modifying the infos).
        """
        return

    def reset_changes(self):
        """Clear internal_database and refresh tree_attribute. """
        self.tree_attr.set_value_with_undo({})

    def ctrls_custom_attrs_model(self):
        """Return a ctrls model that BaseTreeWidget can use. """
        model_data = []
        for attr_info in self.top_node_data.maya_attrs_manager:

            range = [attr_info.min_value, attr_info.max_value]
            default_value = attr_info.default_value
            if attr_info.attr_type == "enum":
                range = attr_info.enum_names
                default_value = attr_info.enum_names[attr_info.default_value]

            data = {
                "info_pointer": attr_info,
                "name": "{0} [{1}_ctrl]".format(attr_info.name, attr_info.parent.name),
                "attrs": [
                    {
                        "name": "attr_value",
                        "type": TREE_STR_TO_DATA_TYPE[attr_info.attr_type],
                        "default_value": default_value,
                        "range": range,
                        "change_pointer": (attr_info.data_dict, "default_value"),
                    },
                    {
                        "name": "lock",
                        "type": bool,
                        "default_value": attr_info.lock,
                        "change_pointer": (attr_info.data_dict, "lock"),
                    },
                    {
                        "name": "keyable",
                        "type": bool,
                        "default_value": attr_info.keyable,
                        "change_pointer": (attr_info.data_dict, "keyable"),
                    },
                    {
                        "name": "hidden",
                        "type": bool,
                        "default_value": attr_info.hidden,
                        "change_pointer": (attr_info.data_dict, "hidden"),
                    },
                ],
            }

            model_data.append(data)

        return model_data
