"""AddJoints allows you to add joints, with the optional ability to include ctrls, to enhance your rig. """
import logging

import maya.cmds as mc

from arise.data_types.attachment_data import AttachmentData
from arise.utils.modules_utils import create_grps, SECONDARY_COLOR
from arise.utils.matrix_utils import matrix_constraint

LOGGER = logging.getLogger("node_rig_logger")

MAYA_VERSION = 2016
AUTHOR = "Etay Herz"
RIG_TYPE = "Joints"
RIG_CATEGORY = "Build"
TAGS = ["joint", "ctrls", "micro", "secondary", "tertiary", "extra"]
TOOL_TIP = "Add joints, with the optional ability to include ctrls, to enhance your rig."

JNTS_COLOR = [0.0, 0.5, 0.65]
DEFAULT_NAME = "extra_joint"


class AddJoints(AttachmentData):
    """Here we will reimplement methods to 1) create attributes on the attachment
    2) create guides in the template module and 3) the rig method where the rig will be built.
    """
    sort_priority = 950

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
            annotation="Check this box to enable joints color.",
        )

        self.jnts_color_attr = self.add_rgb_color_attribute(
            name="Joints Color",
            default_value=JNTS_COLOR,
            annotation="Color of the new joints.",
        )

        self.ctrls_color_attr = self.add_rgb_color_attribute(
            name="Ctrls Color",
            default_value=SECONDARY_COLOR,
            annotation="Color of the optional ctrls.",
        )

        self.joints_count_attr = self.add_integer_attribute(
            name="Joints Count",
            default_value=1,
            annotation="Number of joints to add.",
            min_value=1,
            max_value=100,
            add_slider=True,
        )

        self.tree_attr = self.add_tree_attribute("Add Joints")

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

        self.add_separator()

        self.enable_vis_attr = self.add_boolean_attribute(
            name="Visibility Attribute",
            default_value=False,
            annotation="Enable adding an attribute to control the visibility of the custom ctrls.",
        )

        self.vis_ctrl_attr = self.add_drop_down_attribute(
            name="Add Attribute On",
            items=[""],
            default_value="None",
            annotation="Select the ctrl to which the visibility attribute would be added to.",
        )

    def evaluate(self):  # REIMPLEMENTED!
        """Re-evaluate model. """
        self.jnts_color_attr.set_disabled(False if self.enable_color_attr.value else True)
        self.vis_ctrl_attr.set_disabled(False if self.enable_vis_attr.value else True)

        ctrls_names = [info.default_name for info in self.top_node_data.ctrls_manager]
        self.vis_ctrl_attr.items = ["{0} [ctrl]".format(ctrl) for ctrl in ctrls_names]

        self.tree_attr.update_model(self.add_joints_model())

        AttachmentData.evaluate(self)

    def guides_creation(self):
        """Create guides for new joints. """
        self.extra_add_jnts_dict = {}
        position = [0.0, 0.0, 0.0]

        for index, jnt_dict in enumerate(self.tree_attr.model.model_data):
            guide = self.top_node_data.add_guide(
                name="extra_joint_{0:03}".format(index),
                translation=position[:],
            )
            guide.shape = "sphere"
            guide.size = 0.4

            self.extra_add_jnts_dict[jnt_dict["name"]] = {
                "guide": guide,
                "joint_info": None,
                "ctrl_info": None,
                "ctrl_parent": None,
            }

            position[0] += 2.0

    def joints_creation(self):
        """Create joints here based on joints count attribute. """
        color = self.jnts_color_attr.value if self.enable_color_attr.value else None
        jnts_dict = {info.default_name: info for info in self.top_node_data.joints_manager}

        for jnt_dict in self.tree_attr.model.model_data:

            joint = self.top_node_data.add_joint(
                name=jnt_dict["name"],
                skinning_jnt=True,
                tag_parent_jnt=None,
                radius=0.35,
            )
            self.extra_add_jnts_dict[jnt_dict["name"]]["joint_info"] = joint

            joint_parent = jnt_dict["attrs"][0]["value"].split(" [")[0]
            joint.parent_tag = jnts_dict.get(joint_parent, None)

            if color:
                joint.enable_jnt_color = True
                joint.color = color

    def ctrls_creation(self):
        """Create ctrls here based on tree attribute. """
        parent_dict = {info.default_name: info for info in self.top_node_data.ctrls_manager}
        parent_dict.update({info.default_name: info for info in self.top_node_data.joints_manager})

        scale_mult = 1.0
        if hasattr(self.top_node_data, "ctrls_scale_attr"):
            scale_mult = self.top_node_data.ctrls_scale_attr.value

        for jnt_dict in self.tree_attr.model.model_data:

            if not jnt_dict["attrs"][1]["value"]:
                continue

            ctrl_info = self.top_node_data.add_ctrl(name=jnt_dict["name"], shape="circle", size=1.0 * scale_mult)
            ctrl_info.color = self.ctrls_color_attr.value
            self.extra_add_jnts_dict[jnt_dict["name"]]["ctrl_info"] = ctrl_info

            parent_name = jnt_dict["attrs"][2]["value"].split(" [")[0]
            self.extra_add_jnts_dict[jnt_dict["name"]]["ctrl_parent"] = parent_dict.get(parent_name, None)

    def attachment_creation(self):  # REIMPLEMENTED!
        """Position the jnts and optional ctrls at guides position and parent/constraint accordingly. """
        extra_jnts_grp, extra_ctrls_grp = create_grps(self.top_node_data, ["extra_jnts_grp", "extra_ctrls_grp"])
        extra_ctrls_grp.parent(extra_jnts_grp)

        for extra_jnt_dict in self.extra_add_jnts_dict.values():
            guide_matrix = extra_jnt_dict["guide"].world_transformations["matrix"]

            jnt_info = extra_jnt_dict["joint_info"]
            jnt_info.pointer.parent_relative(extra_jnts_grp)
            jnt_info.pointer.set_matrix(guide_matrix)

            if jnt_info.parent_tag:
                jnt_info.pointer.parent(jnt_info.parent_tag.pointer)

            jnt_info.pointer.add_joint_orient()

            if extra_jnt_dict.get("ctrl_info", None):
                ctrl_info = extra_jnt_dict["ctrl_info"]
                ctrl_info.pointer.add_group_above("{0}{1}_buffer_grp".format(ctrl_info.prefix, ctrl_info.name))

                ctrl_info.pointer.offset_grp.parent_relative(extra_ctrls_grp)
                ctrl_info.pointer.offset_grp.set_matrix(guide_matrix)

                matrix_constraint(ctrl_info.pointer, jnt_info.pointer, maintain_offset=False)

                if extra_jnt_dict["ctrl_parent"]:
                    matrix_constraint(
                        extra_jnt_dict["ctrl_parent"].pointer,
                        ctrl_info.pointer.offset_grp,
                        maintain_offset=True,
                    )

        if self.enable_vis_attr.value:
            attr_ctrl = self.vis_ctrl_attr.value.split(" [")[0]
            ctrl_dict = {info.default_name: info for info in self.top_node_data.ctrls_manager}
            ctrl = ctrl_dict.get(attr_ctrl, None)

            if not ctrl:
                LOGGER.warning("Unable to find visibility ctrl '%s'. Skipping visibility setup.", attr_ctrl)
                return False

            if mc.objExists("{0}.extra_vis".format(ctrl.pointer)):
                LOGGER.warning("Attribute 'extra_vis' already exists on '%s'. Skipping visibility setup.", ctrl.pointer)
                return False

            attr = ctrl.pointer.add_attr("extra_vis", attributeType="bool", keyable=True, dv=1)
            mc.connectAttr(attr, "{0}.visibility".format(extra_ctrls_grp))


        return True

    def reset_changes(self):
        """Clear internal_database and refresh tree_attribute. """
        self.tree_attr.set_value_with_undo({})

    def add_joints_model(self):
        """Return a joints model that BaseTreeWidget can use. """
        jnts_names = ["{0} [joint]".format(info.default_name) for info in self.top_node_data.joints_manager]
        ctrl_names = ["{0} [ctrl]".format(info.default_name) for info in self.top_node_data.ctrls_manager]
        name_prefix = DEFAULT_NAME

        model_data = []
        for index in range(self.joints_count_attr.value):
            data = {
                "name": "{0}_{1:03}".format(name_prefix, index+1),
                "attrs": [
                    {
                        "name": "joint_parent",
                        "type": list,
                        "range": ["None"] + jnts_names,
                        "default_value": "None",
                        "change_pointer": None,
                    },
                    {
                        "name": "create_ctrl",
                        "type": bool,
                        "default_value": False,
                        "change_pointer": None,
                    },
                    {
                        "name": "ctrl_parent",
                        "type": list,
                        "range": ["None"] + ctrl_names + jnts_names,
                        "default_value": "None",
                        "change_pointer": None,
                    },
                ],
            }

            model_data.append(data)

        return model_data
