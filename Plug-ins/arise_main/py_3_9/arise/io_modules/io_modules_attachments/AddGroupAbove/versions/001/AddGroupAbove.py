"""AddGroupAbove attachment allows adding a group above a ctrl. """

import logging

from arise.data_types.attachment_data import AttachmentData

LOGGER = logging.getLogger("node_rig_logger")

MAYA_VERSION = 2016
AUTHOR = "Etay Herz"
RIG_TYPE = "Ctrls"
RIG_CATEGORY = "Post"
TAGS = ["group", "transform", "custom",]
TOOL_TIP = "AddGroupAbove simply adds an empty group above specified ctrls."

DEFAULT_SUFFIX = "buffer_grp"

class AddGroupAbove(AttachmentData):
    """Here we will reimplement methods to 1) create attributes on the attachment
    2) create guides in the template module and 3) the rig method where the rig will be built.
    """
    sort_priority = 1200

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
        """Returns the category number. 1-'build', 2-'finalize', 3-'post'. """
        return 3

    @staticmethod
    def support_multi_instences_on_node():  # REIMPLEMENTED!
        """Return True to allow more then one attachment of this type. """
        return True

    @staticmethod
    def support_copy_settings():  # REIMPLEMENTED!
        """Return True if this attachment supports copying settings between nodes of same module.
        Reimplemented by subclasses that do support copy settings to return True. default is to return False.
        """
        return True

    @staticmethod
    def attachment_permissions(node):  # REIMPLEMENTED!
        """Return True or False if attachment allowed on node.

        Arguments:
            node {node_ptr} -- node to check permission with

        Returns:
            [bool] -- True if allowed or False if not
        """
        if list(node.node_data.ctrls_manager):
            return True

        module = __file__.rsplit("\\", 1)[-1].rsplit("/", 1)[-1].rsplit(".", 1)[0]
        LOGGER.warning(
            "Cannot add attachment '%s' to node '%s'. Node has no ctrls to operate on.",
            module, node.name,
        )
        return False

    def attributes_creation(self):  # REIMPLEMENTED!
        """Here you add the attributes. """

        self.add_collapsible_layout(
            title="Settings",
            shown=True,
        )

        self.groups_suffix_attr = self.add_string_attribute(
            name="Groups Suffix",
            default_value=DEFAULT_SUFFIX[:],
            annotation="Groups name suffix (will use '{0}' if empty)".format(DEFAULT_SUFFIX),
        )

        self.tree_attr = self.add_tree_attribute("Add Groups")

        self.add_button(
            buttons=[
                (
                    self.reset_changes,
                    "resources/icons/cancel_icon.png",
                    "Reset Changes",
                    "Remove any changes done to the 'Add Groups' table above.",
                ),
            ],
        )

        self.close_layout()

    def reset_changes(self):
        """Clear internal_database and refresh tree_attribute. """
        self.tree_attr.set_value_with_undo({})

    def evaluate(self):  # REIMPLEMENTED!
        """Populate tree. """
        AttachmentData.evaluate(self)
        self.tree_attr.update_model(self.add_group_model())

    def attachment_creation(self):  # REIMPLEMENTED!
        """Add to display layer based on attrs. """
        names_to_info = {info.default_name: info for info in self.top_node_data.ctrls_manager}

        grps_count = 0
        for info_data in self.tree_attr.model.model_data:

            if not info_data["attrs"][0]["value"]:
                continue

            ctrl_info = names_to_info.get(info_data["name"], None)

            if not ctrl_info:
                return "Unable to locate matching ctrl."

            suffix = self.groups_suffix_attr.value.strip()
            suffix = suffix if suffix else DEFAULT_SUFFIX
            new_grp_name = "{0}{1}_{2}".format(ctrl_info.prefix, ctrl_info.name, suffix)

            ctrl = ctrl_info.pointer
            ctrl.add_group_above(new_grp_name, maintain_local_values=True)
            grps_count += 1

        if grps_count == 0:
            return "No groups created. Check your setup configuration."

        return True

    def add_group_model(self):
        """Return a model. """
        model_data = []
        for ctrl_info in [ctrl_info for ctrl_info in self.top_node_data.ctrls_manager]:
            data = {
                "info_pointer": ctrl_info,
                "name": ctrl_info.data_dict["default_name"],
                "attrs": [
                    {
                        "name": "add group above",
                        "type": bool,
                        "default_value": False,
                        "change_pointer": None,
                    },
                ],
            }

            model_data.append(data)

        return model_data
