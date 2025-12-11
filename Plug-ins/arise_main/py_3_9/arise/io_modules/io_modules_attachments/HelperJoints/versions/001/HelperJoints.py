"""HelperJoints adds a joint that rotates only partially with its parent. """
import logging

import maya.cmds as mc

from arise.data_types.attachment_data import AttachmentData

LOGGER = logging.getLogger("node_rig_logger")

MAYA_VERSION = 2016
AUTHOR = "Etay Herz"
RIG_TYPE = "Joints"
RIG_CATEGORY = "Build"
TAGS = ["joint", "rotation", "partial", "volume", "candy wrapper", "helper"]
TOOL_TIP = "Adds joints that only partially rotate with their parent."

DEFAULT_ROTATE = 0.5
DEFAULT_OFFSET = [0.001, 0.0, 0.0]
HELPER_JNTS_COLOR = [0.5, 0.0, 0.65]


class HelperJoints(AttachmentData):
    """Here we will reimplement methods to 1) create attributes on the attachment
    2) create guides in the template module and 3) the rig method where the rig will be built.
    """
    sort_priority = 750

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
        if len(node.node_data.joints_manager.joints_info_list) > 2:
            return True

        module = __file__.rsplit("\\", 1)[-1].rsplit("/", 1)[-1].rsplit(".", 1)[0]
        LOGGER.warning(
            "Cannot add attachment '%s' to node '%s'. Node needs to have more than 2 joints.",
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
        self.enable_color_attr = self.add_boolean_attribute(
            name="Enable Joints Color",
            default_value=True,
            annotation="Check this box to enable helper joints color.",
        )

        self.jnts_color_attr = self.add_rgb_color_attribute(
            name="Helper Joints Color",
            default_value=HELPER_JNTS_COLOR,
            annotation="Color of the new helper joints.",
        )

        self.filter_attr = self.add_boolean_attribute(
            name="Only Skinning Joints",
            default_value=True,
            annotation="When checked, only skinning joints will be displayed in the table below.",
        )

        self.tree_attr = self.add_tree_attribute("Helper Joints")

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
        self.tree_attr.update_model(self.helper_joints_model())
        self.jnts_color_attr.set_disabled(False if self.enable_color_attr.value else True)
        AttachmentData.evaluate(self)

    def joints_creation(self):
        """Create joints here based on info from module attributes and modules guides. """
        self.helper_jnts_dict = {}
        for helper_dict in self.tree_attr.model.model_data:

            if helper_dict["attrs"][0]["value"] is False:
                continue

            self.helper_jnts_dict[helper_dict["name"]] = {
                "rotation_amount": helper_dict["attrs"][1]["value"],
                "skip_attrs": [
                    helper_dict["attrs"][2]["value"],
                    helper_dict["attrs"][3]["value"],
                    helper_dict["attrs"][4]["value"],
                ],
                "offset": [
                    helper_dict["attrs"][5]["value"],
                    helper_dict["attrs"][6]["value"],
                    helper_dict["attrs"][7]["value"],
                ],
            }

        for jnt_info in self.top_node_data.joints_manager:

            if jnt_info.default_name not in self.helper_jnts_dict.keys():
                continue

            helper_info = self.top_node_data.add_joint(
                name="{0}_helper".format(jnt_info.default_name),
                skinning_jnt=True,
                radius=jnt_info.radius * 0.6,
                tag_parent_jnt=jnt_info,
            )

            helper_info.prefix = jnt_info.prefix
            helper_info.suffix = jnt_info.suffix

            if self.enable_color_attr.value:
                helper_info.enable_jnt_color = True
                helper_info.color = self.jnts_color_attr.value

            self.helper_jnts_dict[jnt_info.default_name]["jnt_info"] = helper_info
            self.helper_jnts_dict[jnt_info.default_name]["parent_info"] = jnt_info
            self.helper_jnts_dict[jnt_info.default_name]["grandparent_info"] = jnt_info.parent_tag

    def attachment_creation(self):  # REIMPLEMENTED!
        """
        Attachments with Tree attributes don't need to do anything since tree attrs modify ctrls and joints
        before they are built (modifying the infos).
        """
        is_successful = True

        if not self.helper_jnts_dict:
            return "Nothing to create."

        for helper_dict in self.helper_jnts_dict.values():
            helper_jnt = (helper_dict)["jnt_info"].pointer
            helper_jnt.parent_relative(helper_dict["parent_info"].pointer)
            helper_jnt.set_translation(helper_dict["offset"], space="object")

            skip_axis = []
            for axis, value in zip(["x", "y", "z"], helper_dict["skip_attrs"]):
                if value:
                    skip_axis.append(axis)

            if len(skip_axis) == 3:
                jnt = helper_jnt.short_name
                LOGGER.warning("[%s] For joint '%s' cannot skip all axis. Ignoring skip.", self.module_type, jnt)
                is_successful = False
                continue

            ori_constraint = mc.orientConstraint(
                helper_dict["parent_info"].pointer,
                helper_jnt,
                maintainOffset=True,
                weight=helper_dict["rotation_amount"],
                skip=skip_axis,
            )[0]
            mc.setAttr("{0}.interpType".format(ori_constraint), 2)  # shortest.

            mc.orientConstraint(  # Add grandparent to orient constraint with correct weight and offset.
                helper_dict["grandparent_info"].pointer,
                helper_jnt,
                maintainOffset=True,
                weight=1.0 - helper_dict["rotation_amount"],
            )

        if not is_successful:
            return "Helper joints issues found."

        return True

    def reset_changes(self):
        """Clear internal_database and refresh tree_attribute. """
        self.tree_attr.set_value_with_undo({})

    def helper_joints_model(self):
        """Return a joints model that BaseTreeWidget can use. """
        model_data = []
        for info in self.top_node_data.joints_manager:
            if self.filter_attr.value:

                if not info.skinning_jnt:
                    continue

            if info.parent_tag is None:
                continue

            data = {
                "info_pointer": info,
                "name": info.default_name,
                "attrs": [
                    {
                        "name": "create_jnt",
                        "type": bool,
                        "default_value": False,
                        "change_pointer": None,
                    },
                    {
                        "name": "rotation_amount",
                        "type": float,
                        "range": [0.01, 0.99],
                        "default_value": DEFAULT_ROTATE,
                        "change_pointer": None,
                    },
                    {
                        "name": "skip_rotate_X",
                        "type": bool,
                        "default_value": False,
                        "change_pointer": None,
                    },
                    {
                        "name": "skip_rotate_Y",
                        "type": bool,
                        "default_value": False,
                        "change_pointer": None,
                    },
                    {
                        "name": "skip_rotate_Z",
                        "type": bool,
                        "default_value": False,
                        "change_pointer": None,
                    },
                    {
                        "name": "translate_X",
                        "type": float,
                        "range": [-1000, 1000],
                        "default_value": DEFAULT_OFFSET[0],
                        "change_pointer": None,
                    },
                    {
                        "name": "translate_Y",
                        "type": float,
                        "range": [-1000, 1000],
                        "default_value": DEFAULT_OFFSET[1],
                        "change_pointer": None,
                    },
                    {
                        "name": "translate_Z",
                        "type": float,
                        "range": [-1000, 1000],
                        "default_value": DEFAULT_OFFSET[2],
                        "change_pointer": None,
                    },
                ],
            }

            model_data.append(data)

        return model_data
