"""MovablePivot allows adding to ctrls a locator to move it's pivot. """
import logging

import maya.cmds as mc

from arise.data_types.attachment_data import AttachmentData
from arise.utils.modules_utils import movable_pivot_setup

LOGGER = logging.getLogger("node_rig_logger")

MAYA_VERSION = 2016
AUTHOR = "Etay Herz"
RIG_TYPE = "Ctrls"
RIG_CATEGORY = "Build"
TAGS = ["ctrl", "ctrls", "control", "pivot", "position", "animate",]
TOOL_TIP = (
    "MovablePivot allows animators to move ctrls pivots.\n"
    "(Does not work for every ctrl, depends on the ctrl setup)"
)


class MovablePivot(AttachmentData):
    """Here we will reimplement methods to 1) create attributes on the attachment
    2) create guides in the template module and 3) the rig method where the rig will be built.
    """
    sort_priority = 1300

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
        self.tree_attr = self.add_tree_attribute("Movable Pivot")
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
        self.tree_attr.update_model(self.movable_pivot_model())

    def attachment_creation(self):
        """Add locator pivot setup to ctrls. """
        names_to_info = {info.default_name: info for info in self.top_node_data.ctrls_manager}

        movable_pivot_ctrls = []
        for info_model in self.tree_attr.model.model_data:

            if not info_model["attrs"][0]["value"]:
                continue

            ctrl = names_to_info[info_model["name"]].pointer

            if mc.objExists("{0}.pivot".format(ctrl)):
                LOGGER.warning("Ctrl '%s' already has a 'pivot' attribute. Skipping ctrl.", ctrl.short_name)
                continue

            if info_model["attrs"][1]["value"]:
                ctrl.add_spacer_attr()

            pivot_attr = ctrl.add_attr("pivot", at="bool", dv=0, keyable=False)
            mc.setAttr(pivot_attr, channelBox=True)

            loc = movable_pivot_setup(ctrl, scale_pivot=False, attr=pivot_attr)
            movable_pivot_ctrls.append(ctrl)

            loc_size = info_model["attrs"][2]["value"]
            mc.setAttr("{0}.localScale".format(loc), loc_size, loc_size, loc_size)

        if not movable_pivot_ctrls:
            return "A movable pivot wasn't added to any ctrl. Check your setup configuration."

        return True

    def reset_changes(self):
        """Clear internal_database and refresh tree_attribute. """
        self.tree_attr.set_value_with_undo({})

    def movable_pivot_model(self):
        """Return a ctrls model that BaseTreeWidget can use. """
        model_data = []
        for ctrl_info in self.top_node_data.ctrls_manager:
            data = {
                "info_pointer": ctrl_info,
                "name": ctrl_info.data_dict["default_name"],
                "attrs": [
                    {
                        "name": "add_movable_pivot",
                        "type": bool,
                        "default_value": False,
                        "change_pointer": None,
                    },
                    {
                        "name": "add_spacer_attr",
                        "type": bool,
                        "default_value": True,
                        "change_pointer": None,
                    },
                    {
                        "name": "locator_size",
                        "type": float,
                        "range": [0.0, 1000.0],
                        "default_value": 1.0,
                        "change_pointer": None,
                    },
                ],
            }

            model_data.append(data)

        return model_data
