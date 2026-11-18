"""CtrlsLimitAttributes exposes attributes of the ctrls infos to limit attributes. """

import logging

from arise.data_types.attachment_data import AttachmentData
from arise.utils.constant_variables import ATTRS_LIST

LOGGER = logging.getLogger("node_rig_logger")

MAYA_VERSION = 2016
AUTHOR = "Etay Herz"
RIG_TYPE = "Ctrls"
RIG_CATEGORY = "Build"
TAGS = ["ctrl", "ctrls", "control", "limit", "information", "transformations", "attributes"]
TOOL_TIP = (
    "CtrlsLimitAttributes lets you restrict the translation, rotation, and "
    "scaling values an animator can use when animating a ctrl."
)


class CtrlsLimitAttributes(AttachmentData):
    """Here we will reimplement methods to 1) create attributes on the attachment
    2) create guides in the template module and 3) the rig method where the rig will be built.
    """
    sort_priority = 1800

    def __init__(self, parent, icon, docs, module_dict):
        AttachmentData.__init__(
            self,
            parent=parent,
            icon=icon,
            docs=docs,
            module_dict=module_dict,
        )

    @staticmethod  # REIMPLEMENTED!
    def attachment_permissions(node):
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
        self.tree_attr = self.add_tree_attribute("Ctrls Limit Attributes")
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

    def evaluate(self):  # REIMPLEMENTED!
        """Re-evaluate model. """
        AttachmentData.evaluate(self)
        self.tree_attr.update_model(self.ctrls_limit_model())

    def attachment_creation(self):
        """
        Attachments with Tree attributes don't need to do anything since tree attrs modify ctrls and joints
        before they are built (modifying the infos).
        """
        return

    def reset_changes(self):
        """Clear internal_database and refresh tree_attribute. """
        self.tree_attr.set_value_with_undo({})

    def ctrls_limit_model(self):
        """Return a ctrls limit model that BaseTreeWidget can use. """
        model_data = []
        for ctrl_info in self.top_node_data.ctrls_manager:
            data = {
                "info_pointer": ctrl_info,
                "name": ctrl_info.data_dict["default_name"],
                "attrs": [],
            }

            for attr in ATTRS_LIST[:-1]:
                attr_data = {
                    "name": "{0} [Min Enable]".format(attr),
                    "type": bool,
                    "default_value": ctrl_info.limit_attrs_min_enable[attr],
                    "change_pointer": (ctrl_info.limit_attrs_min_enable, attr),
                }
                data["attrs"].append(attr_data)

                attr_data = {
                    "name": "{0} [Min value]".format(attr),
                    "type": float,
                    "range": [-1000.0, 1000.0],
                    "default_value": ctrl_info.limit_attrs_min_value[attr],
                    "change_pointer": (ctrl_info.limit_attrs_min_value, attr),
                }
                data["attrs"].append(attr_data)

                attr_data = {
                    "name": "{0} [Max Enable]".format(attr),
                    "type": bool,
                    "default_value": ctrl_info.limit_attrs_max_enable[attr],
                    "change_pointer": (ctrl_info.limit_attrs_max_enable, attr),
                }
                data["attrs"].append(attr_data)

                attr_data = {
                    "name": "{0} [Max value]".format(attr),
                    "type": float,
                    "range": [-1000.0, 1000.0],
                    "default_value": ctrl_info.limit_attrs_max_value[attr],
                    "change_pointer": (ctrl_info.limit_attrs_max_value, attr),
                }
                data["attrs"].append(attr_data)

            model_data.append(data)

        return model_data
