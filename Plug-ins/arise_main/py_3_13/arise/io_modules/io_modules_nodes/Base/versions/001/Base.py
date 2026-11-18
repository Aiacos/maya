"""Base module creates ctrls at root for the rest of the rig to be driven by. """

import logging

import maya.cmds as mc

from arise.data_types import node_data
from arise.utils import matrix_utils
from arise.utils.modules_utils import (
    secondary_ctrls_setup, create_grps, expose_rotation_order, SECONDARY_CTRL_ATTR, connect_vis_attr,
    SECONDARY_COLOR, JOINTS_VIS_ATTR, update_ctrls
)

LOGGER = logging.getLogger("node_rig_logger")
OPTIONS_DICT = {"Normal": 0, "Template": 1, "Reference": 2}

MAYA_VERSION = 2016  # the version of maya from which this module supports.
AUTHOR = "Etay Herz"  # name of person who created this module.
RIG_CATEGORY = "Basic"  # either 'Basic', 'Cartoon', 'Vfx', 'Game' or 'All'.
RIG_TYPE = "All"  # Biped, Car, Quadruped, ..., All.
TAGS = ["basic", "base", "root", "top", "origin"]
TOOL_TIP = (
    "A Base node is at the root of every rig.\n"
    "The base node creates the master ctrls that move the entire rig, which is why all connections lead to it.\n"
    "Each character should have only one Base node."
)

node_data.NodeData.update_ctrls = update_ctrls


class Base(node_data.NodeData):
    """Base module creates ctrls at root for the rest of the rig to be driven by. """
    sort_priority = 10  # appears first in inventory.

    def __init__(self, parent, docs, icon, module_dict):
        node_data.NodeData.__init__(
            self,
            parent=parent,
            icon=icon,
            docs=docs,
            module_dict=module_dict
        )

    def attributes_creation(self):  # REIMPLEMENTED!
        """Here you add the module attributes. """
        self.add_collapsible_layout(title="Settings", shown=True)
        self.ctrls_scale_attr = self.add_float_attribute(
            name="Ctrls Scale",
            default_value=1.0,
            annotation=(
                "Scale all the node's ctrls.\n"
                "Note that the attachments 'CtrlsSettings' and 'CtrlsShape' will override this."
            ),
            min_value=0.01,
            max_value=100,
            button=[
                self.update_ctrls,
                "Update",
                "resources/icons/sync_icon.png",
                "If the ctrls exist in the Maya scene, their shapes will update without requiring a rebuild.",
            ],
            help_link="https://youtu.be/-1fpRw6oJME?t=31",
        )

        self.expose_rotation_order_attr = self.add_boolean_attribute(
            name="Expose RotateOrder",
            default_value=True,
            annotation="Exposes all the ctrls 'RotateOrder' attribute in the Channel Box",
            help_link="https://youtu.be/-1fpRw6oJME?t=149",
        )

        self.add_separator()
        self.tag_skinning_attr = self.add_boolean_attribute(
            name="Skinning Joint",
            default_value=False,
            annotation=(
                "If checked, the 'Base' joint will be tagged as a skinning joint,\n"
                "which is necessary for attachments like 'FollowSkeleton' to operate correctly."
            ),
        )

        self.joints_vis_attr = self.add_boolean_attribute(
            name="Joints Visibility",
            default_value=True,
            annotation="Turn joints visibility on or off",
        )

        self.add_frame_layout("Geometry Display")
        self.is_geo_display_attr = self.add_boolean_attribute(
            name="Geometry Display",
            default_value=False,
            annotation="Add dropdown attribute to 'base_ctrl' that switches geometry to 'Template', 'Reference'",
        )
        self.geo_node_attr = self.add_node_attribute(
            name="Geometry Group",
            annotation="Specify the group under which the character meshes are located",
            node_type="transform",
        )
        self.geo_node_attr._value = "geometry_grp"  # an ugly way to set value but did not build another way.

        self.geo_display_dv_attr = self.add_drop_down_attribute(
            name="Display Value",
            items=["Normal", "Template", "Reference"],
            default_value="Normal",
            annotation="Select the value for 'Geometry Display'.",
        )
        self.close_layout()

        self.my_driver_attr = self.add_driver_attribute(name="Output", annotation="Output")
        self.close_layout()

    def evaluate_creation_methods(self):  # REIMPLEMENTED!
        """Reimplemented to enable/disable attrs. """
        self.geo_node_attr.set_disabled(False if self.is_geo_display_attr.value else True)
        self.geo_display_dv_attr.set_disabled(False if self.is_geo_display_attr.value else True)

        node_data.NodeData.evaluate_creation_methods(self)

    def guides_creation(self):
        """Create guides based on attributes values. """
        self.base_guide = self.add_guide(name="Base", translation=[0, 0, 0], rotation=[0, 0, 0])
        self.base_guide.size = 10

    def joints_creation(self):
        """Create joints based on attributes values and guides. (without positioning as this point). """
        self.base_joint = self.add_joint(
            name="main",
            skinning_jnt=self.tag_skinning_attr.value,
            radius=0.75,
        )

        # humanIK definition.
        self.base_joint.human_ik = "Reference"

    def ctrls_creation(self):
        """Create controls based on attributes values, guides and joints. (without positioning as this point). """
        scale_mult = self.ctrls_scale_attr.value * 4.0
        self.base_ctrl = self.add_ctrl(name="main", shape="global_1", size=25 * scale_mult)
        self.base_secondary_ctrl = self.add_ctrl(name="main_secondary", shape="global_1", size=19 * scale_mult)
        self.base_secondary_ctrl.color = SECONDARY_COLOR

        for attr in ["scaleY", "scaleZ"]:
            self.base_secondary_ctrl.add_locked_hidden_attr(attr)
            self.base_ctrl.add_locked_hidden_attr(attr)

    def rig_creation(self):
        """Using the attributes values, guides, joints, and ctrls, build the rig. """
        is_successful = True

        if self.is_mirrored:
            self.module_grp.set_attr("scaleX", -1)

        output_grp, jnts_grp, ctrl_grp = create_grps(self, ["output_grp", "jnts_grp", "ctrls_grp"])

        self.my_driver_attr.set_maya_object(output_grp)

        secondary_ctrls_setup([self.base_ctrl], [self.base_secondary_ctrl])

        base_jnt = self.base_joint.pointer
        base_ctrl = self.base_ctrl.pointer

        base_jnt.parent_relative(jnts_grp)
        base_ctrl.offset_grp.parent_relative(ctrl_grp)

        if self.expose_rotation_order_attr.value:
            expose_rotation_order([self.base_ctrl, self.base_secondary_ctrl])

        base_ctrl.set_attr(SECONDARY_CTRL_ATTR, 1)

        jnts_grp.set_matrix(self.base_guide.world_transformations["matrix"])
        ctrl_grp.match_transformation_to(jnts_grp)

        matrix_utils.matrix_constraint(base_ctrl.btm_ctrl, jnts_grp, maintain_offset=False)
        matrix_utils.matrix_constraint(base_jnt, output_grp, maintain_offset=False, force=False)

        base_jnt.lock_translation()
        base_jnt.lock_rotation()
        base_jnt.lock_scale()

        base_ctrl.scale_attrs_connect()
        base_ctrl.btm_ctrl.scale_attrs_connect()

        base_ctrl.add_spacer_attr()
        jnts_vis_attr = base_ctrl.add_attr(
            "joints_visibility",
            at="bool",
            dv=1,
            keyable=False,
            category="arise_base_main_ctrl_tag",  # category added so rigExporter can find this attr.
        )
        mc.setAttr(jnts_vis_attr, channelBox=True)
        connect_vis_attr("{0}.{1}".format(self.module_grp, JOINTS_VIS_ATTR), jnts_vis_attr)

        mc.setAttr(jnts_vis_attr, self.joints_vis_attr.value)

        # Geometry display.
        is_successful = self.setup_geo_dispaly(base_ctrl)

        return is_successful

    def setup_geo_dispaly(self, ctrl):
        """Create attr on main_ctrl that controls the display of geometry group.

        Args:
            ctrl (IoTransform): object to add on the attr
        """
        if not self.is_geo_display_attr.value:
            return True

        value_status = self.geo_node_attr.is_valid_object()

        if not value_status:
            msg = "invalid value for 'Geometry Group' attr on node '{0}'".format(self.name)
            LOGGER.warning(msg)

            return False

        transform = self.geo_node_attr.value
        if not mc.objExists("{0}.overrideDisplayType".format(transform)):
            msg = "[{0}] 'Geometry Group' node is not a transform '{1}'".format(self.name, transform)
            LOGGER.warning(msg)

            return False

        if mc.getAttr("{0}.overrideEnabled".format(transform), lock=True):
            msg = "[{0}] Geometry Group '{1}' 'overrideDisplayType' attr is locked".format(self.name, transform)
            LOGGER.warning(msg)

            return False

        connected = mc.listConnections("{0}.overrideDisplayType".format(transform), destination=False, source=True)
        if mc.getAttr("{0}.overrideDisplayType".format(transform), lock=True) or connected:
            msg = "[{0}] Geometry Group '{1}' 'overrideDisplayType' attr is ".format(self.name, transform)
            msg += "connected/locked"
            LOGGER.warning(msg)

            return False

        if not mc.getAttr("{0}.overrideEnabled".format(transform)):
            mc.setAttr("{0}.overrideEnabled".format(transform), 1)

        attr = ctrl.add_attr(
            "geometry_display",
            keyable=False,
            at="enum",
            en="Normal:Template:Reference:",
            dv=0,
            category="arise_base_main_ctrl_tag",  # category added so rigExporter can find this attr.
            )
        mc.setAttr(attr, channelBox=True)

        index = OPTIONS_DICT[self.geo_display_dv_attr.value]
        mc.setAttr(attr, index)

        mc.connectAttr(attr, "{0}.overrideDisplayType".format(transform), f=True)
