"""CA_Mouth module creates lips and jaw rig for the face. """

import logging

import maya.cmds as mc

from arise.data_types import node_data
from arise.utils import tagging_utils
from arise.utils.subcomponents.complex_ribbon import ComplexRibbon
from arise.utils.math_utils import distance_between, mid_point
from arise.utils.modules_utils import (
    create_grps, SECONDARY_COLOR, create_module_scale, update_ctrls, ADD_DL, MULT_DL, MULT_DL_INPUT1,
    MULT_DL_INPUT2,
)
from arise.utils.matrix_utils import matrix_constraint
from arise.utils.io_nodes.io_transform import IoTransform
from arise.utils.decorators_utils import undo_chunk_dec

MAYA_VERSION = 2016  # the version of maya from which this module is supported.
AUTHOR = "Etay Herz"  # name of person who created this module.
RIG_CATEGORY = "Cartoon"  # either 'Basic', 'Cartoon', 'VFX', 'Game' or 'All'. (used when filtering).
RIG_TYPE = "Biped"  # Biped, Car, Quadruped, All, ... (for filtering modules in lists).
TAGS = ["cartoon", "complex", "advance", "lips", "mouth", "jaw", "face"]
TOOL_TIP = "Cartoon jaw and lips."

LOGGER = logging.getLogger("node_rig_logger")

node_data.NodeData.update_ctrls = update_ctrls


class CA_Mouth(node_data.NodeData):
    """CA_Mouth module creates lips and jaw rig for the face. """
    sort_priority = 100

    def __init__(self, parent, docs, icon, module_dict):
        node_data.NodeData.__init__(self, parent=parent, icon=icon, docs=docs, module_dict=module_dict)
        self.body_part = "mouth"

    def attributes_creation(self):
        """Here you add the module attributes. """
        self.add_collapsible_layout(title="Guides", shown=True)
        self.mirror_guides_btn = self.add_button(
            buttons=[
                (
                    self.mirror_the_guides,
                    "resources/icons/mirror_l_to_r_icon.png",
                    "Mirror Mouth Guides",
                    "Mirror right side guides to reflect left side.\nIn 'Solo' mode will mirror in world space.",
                ),
            ],
        )
        self.close_layout()

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
        self.offset_attr = self.add_float_attribute(
            name="Ctrls Offset Position",
            default_value=1.0,
            annotation="Offset of lips ctrls for when the ctrls are hidden inside the lips mesh.",
            min_value=0.01,
            max_value=100,
        )
        self.jaw_offset_attr = self.add_xyz_attribute(
            name="Jaw Ctrl Offset",
            default_value=(0, -6, 5),
            annotation="Offset 'jaw_ctrl' shape from its pivot. Use this to position 'jaw_ctrl' under the chin.",
        )
        self.skin_jnts_attr = self.add_integer_attribute(
            name="Lips Skinning Joints",
            default_value=14,
            annotation="The number of skinning joints per lip, not including corner joints.",
            min_value=5,
            max_value=30,
            add_slider=True,
        )
        self.bias_attr = self.add_float_attribute(
            name="Lips Bias",
            default_value=1.3,
            annotation="Use this to control how much the lips move with 'M_(upper/lower)_lip_ctrl'.",
            min_value=0.0,
            max_value=2.0,
        )

        self.add_separator()
        self.enable_roll_attr = self.add_boolean_attribute(
            name="Create Roll",
            default_value=False,
            annotation=(
                "All minor and mid controls will have the 'Roll' and 'Roll loc Vis' attributes, "
                "which allow them to be rotated from a different position.\n"
                "The 'Roll Loc Vis' attribute will display a locator that controls from where the roll rotates."
            ),
        )
        self.up_roll_attr = self.add_xyz_attribute(
            name="Upper Roll Offset",
            default_value=(0, 1, 0),
            annotation=(
                "The initial roll offset position for the upper ctrls.\n"
                "In other words, translation values of the roll locators."
            ),
        )

        self.low_roll_attr = self.add_xyz_attribute(
            name="Lower Roll Offset",
            default_value=(0, -1, 0),
            annotation=(
                "The initial roll offset position for the lower ctrls.\n"
                "In other words, translation values of the roll locators."
            ),
        )

        self.add_separator()
        self.up_push_attr = self.add_boolean_attribute(
            name="Upper Lip Push",
            default_value=False,
            annotation=(
                "The lower lip will push the upper lip when they collide.\n"
                "Has an on/off attribute on 'M_upper_lip_ctrl'."
            ),
        )

        self.micro_ctrls_attr = self.add_boolean_attribute(
            name="Micro Ctrls",
            default_value=False,
            annotation="Add a ctrl for every lip skinning joint.",
        )

        ### connections.
        self.add_separator(title="Connections")
        self.driven_root_attr = self.add_driven_attribute(name="Root Input", annotation="Input")
        self.driver_head_attr = self.add_driver_attribute(name="Head Output", annotation="Cranium Output")
        self.driver_jaw_attr = self.add_driver_attribute(name="Jaw Output", annotation="Output")

        self.close_layout()

    def evaluate_creation_methods(self):  # REIMPLEMENTED!
        """Reimplemented to enable/disable attrs. """
        self.up_roll_attr.set_disabled(False if self.enable_roll_attr.value else True)
        self.low_roll_attr.set_disabled(False if self.enable_roll_attr.value else True)

        node_data.NodeData.evaluate_creation_methods(self)

    @undo_chunk_dec
    def mirror_the_guides(self):
        """Mirror right side guides to match left side. called by a button attribute. """
        if self.state_manager.state != "Template":
            LOGGER.warning("'%s' must be in 'Template' mode to mirror guides", self.name)
            return

        # must find guides by name as nodes value change recreates guidesInfos.
        guides_dict = {}
        source_guides = [
            self.l_corner_guide.name, self.l_up_minor_guide.name, self.l_low_minor_guide.name,
            self.l_shape_a_guide.name, self.l_shape_b_guide.name,
        ]
        target_guides = [
            self.r_corner_guide.name, self.r_up_minor_guide.name, self.r_low_minor_guide.name,
            self.r_shape_a_guide.name, self.r_shape_b_guide.name,
        ]

        for guide in self.guide_manager.io_guides_list:
            if guide.info.name in source_guides + target_guides:
                guides_dict[guide.info.name] = guide

        if not guides_dict[source_guides[0]].transform.is_exists():
            LOGGER.warning("'%s' couldn't find guides. Aborting mirror guides.", self.name)
            return

        for source, target in zip(source_guides, target_guides):
            values = mc.getAttr("{0}.translate".format(guides_dict[source].transform))[0]
            mc.setAttr(
                "{0}.translate".format(guides_dict[target].transform),
                *[values[0] * -1.0, values[1], values[2]]
            )

            values = guides_dict[source].transform.get_rotation(space="object")
            guides_dict[target].transform.set_rotation([values[0], values[1] * -1, values[2] * -1], space="object")

    def guides_creation(self):
        """Create guides based on attributes values. """
        self.jaw_guide = self.add_guide(name="jaw", translation=[0.0, 161.4, 1])
        self.jaw_guide.shape = "box"
        self.jaw_guide.size = 0.2

        self.l_corner_guide = self.add_guide(
            name="L_mouth_corner",
            translation=[3.411, 160.0, 5.044],
            rotation=[0, 30, 0],
            parent=self.jaw_guide,
        )
        self.l_corner_guide.shape = "triangle"
        self.l_corner_guide.rotate_offset = [90, 0, -90]
        self.l_corner_guide.size = 0.2

        self.r_corner_guide = self.add_guide(
            name="R_mouth_corner",
            translation=[-3.411, 160.0, 5.044],
            rotation=[0, -30, 0],
            parent=self.jaw_guide,
        )
        self.r_corner_guide.shape = "triangle"
        self.r_corner_guide.rotate_offset = [90, 0, 90]
        self.r_corner_guide.size = 0.2

        self.up_mid_guide = self.add_guide(
            name="M_upper_lip",
            translation=[0, 160.2, 5.822],
            parent=self.jaw_guide,
        )
        self.up_mid_guide.shape = "circle_half_closed"
        self.up_mid_guide.size = 0.25

        self.l_up_minor_guide = self.add_guide(
            name="L_upper_lip_minor",
            translation=[1.73, 160.2, 5.726],
            rotation=[0, 15, 0],
            parent=self.jaw_guide,
        )
        self.l_up_minor_guide.rotate_offset = [90, 0, 0]
        self.l_up_minor_guide.size = 0.12

        self.r_up_minor_guide = self.add_guide(
            name="R_upper_lip_minor",
            translation=[-1.73, 160.2, 5.726],
            rotation=[0, -15, 0],
            parent=self.jaw_guide,
        )
        self.r_up_minor_guide.rotate_offset = [90, 0, 0]
        self.r_up_minor_guide.size = 0.12

        self.low_mid_guide = self.add_guide(
            name="M_lower_lip",
            translation=[0, 159.8, 5.822],
            parent=self.jaw_guide,
        )
        self.low_mid_guide.shape = "circle_half_closed"
        self.low_mid_guide.rotate_offset = [0, 0, 180]
        self.low_mid_guide.size = 0.25

        self.l_low_minor_guide = self.add_guide(
            name="L_lower_lip_minor",
            translation=[1.73, 159.8, 5.726],
            rotation=[0, 15, 0],
            parent=self.jaw_guide,
        )
        self.l_low_minor_guide.rotate_offset = [90, 0, 0]
        self.l_low_minor_guide.size = 0.12

        self.r_low_minor_guide = self.add_guide(
            name="R_lower_lip_minor",
            translation=[-1.73, 159.8, 5.726],
            rotation=[0, -15, 0],
            parent=self.jaw_guide,
        )
        self.r_low_minor_guide.rotate_offset = [90, 0, 0]
        self.r_low_minor_guide.size = 0.12

        self.l_shape_a_guide = self.add_guide(
            name="L_mouth_shape_A",
            translation=[5.351, 160, 2.753],
            parent=self.jaw_guide,
        )
        self.l_shape_a_guide.shape = "sphere"
        self.l_shape_a_guide.size = 0.2

        self.l_shape_b_guide = self.add_guide(
            name="L_mouth_shape_B",
            translation=[4.658, 160, 4.066],
            parent=self.jaw_guide,
        )
        self.l_shape_b_guide.shape = "sphere"
        self.l_shape_b_guide.size = 0.2

        self.r_shape_a_guide = self.add_guide(
            name="R_mouth_shape_A",
            translation=[-5.351, 160, 2.753],
            parent=self.jaw_guide,
        )
        self.r_shape_a_guide.shape = "sphere"
        self.r_shape_a_guide.size = 0.2

        self.r_shape_b_guide = self.add_guide(
            name="R_mouth_shape_B",
            translation=[-4.658, 160, 4.066],
            parent=self.jaw_guide,
        )
        self.r_shape_b_guide.shape = "sphere"
        self.r_shape_b_guide.size = 0.2

        self.l_shape_b_guide.visual_parent = self.l_corner_guide
        self.l_shape_a_guide.visual_parent = self.l_shape_b_guide
        self.r_shape_b_guide.visual_parent = self.r_corner_guide
        self.r_shape_a_guide.visual_parent = self.r_shape_b_guide
        self.l_corner_guide.visual_parent = self.l_up_minor_guide
        self.l_up_minor_guide.visual_parent = self.up_mid_guide
        self.up_mid_guide.visual_parent = self.r_up_minor_guide
        self.r_up_minor_guide.visual_parent = self.r_corner_guide
        self.r_corner_guide.visual_parent = self.r_low_minor_guide
        self.r_low_minor_guide.visual_parent = self.low_mid_guide
        self.low_mid_guide.visual_parent = self.l_low_minor_guide
        self.l_low_minor_guide.visual_parent = self.l_corner_guide


    def post_guides_creation(self):  # REIMPLEMENTED!
        """Optional code to run after guides are created during 'Template' stage. (create display curve). """
        new_nodes = []
        up_infs = [self.l_up_minor_guide, self.up_mid_guide, self.r_up_minor_guide]
        low_infs = [self.l_low_minor_guide, self.low_mid_guide, self.r_low_minor_guide]
        for suffix, influences in [["upper_lip", up_infs], ["lower_lip", low_infs]]:
            curve = mc.curve(
                degree=3,
                point=[(0, 0, 0)] * 5,
                knot=[0, 0, 0, 1, 2, 2, 2],
                worldSpace=True,
                name="{0}_{1}_curve".format(self.name, suffix),
            )
            curve = IoTransform(curve, existing=True)
            curve.parent_relative(self.guide_manager.io_guides_list[0])
            curve.set_attr("inheritsTransform", 0)
            curve.set_attr("template", 1)
            curve.set_attr("lineWidth", 4)
            curve.lock_and_hide_transformations()

            new_nodes.append(curve)
            for index, inf in enumerate([self.l_corner_guide] + influences + [self.r_corner_guide]):
                decomp = mc.createNode("decomposeMatrix", n="{0}_{1}_decomp".format(suffix, index))
                mc.connectAttr("{0}.worldMatrix[0]".format(inf), "{0}.inputMatrix".format(decomp))
                mc.connectAttr("{0}.outputTranslate".format(decomp), "{0}.controlPoints[{1}]".format(curve, index))
                new_nodes.append(decomp)

        # mouth curvature curve.
        shape_crv = mc.curve(
            degree=3,
            point=[(0, 0, 0)] * 9,
            knot=[0, 0, 0, 1, 2, 3, 4, 5, 6, 6, 6],
            worldSpace=True,
            name="{0}_curvature_curve".format(self.name),
        )
        shape_crv = IoTransform(shape_crv, existing=True)
        shape_crv.parent_relative(self.guide_manager.io_guides_list[0])
        shape_crv.set_attr("inheritsTransform", 0)
        shape_crv.set_attr("template", 1)
        shape_crv.set_attr("lineWidth", 0.1)
        shape_crv.lock_and_hide_transformations()
        new_nodes.append(shape_crv)

        add_nodes = []
        for index, (inf_a, inf_b) in enumerate(zip(up_infs, low_infs)):
            add_node = mc.createNode("wtAddMatrix", n="average_pos_{0}_addMatrix".format(index))
            mc.connectAttr("{0}.worldMatrix[0]".format(inf_a), "{0}.wtMatrix[0].matrixIn".format(add_node))
            mc.setAttr("{0}.wtMatrix[0].weightIn".format(add_node), 0.5)
            mc.connectAttr("{0}.worldMatrix[0]".format(inf_b), "{0}.wtMatrix[1].matrixIn".format(add_node))
            mc.setAttr("{0}.wtMatrix[1].weightIn".format(add_node), 0.5)
            add_nodes.append(add_node)
            new_nodes.append(add_node)

        guides = [self.l_shape_a_guide, self.l_shape_b_guide, self.l_corner_guide] + add_nodes
        guides = guides + [self.r_corner_guide, self.r_shape_b_guide, self.r_shape_a_guide]
        for index, inf in enumerate(guides):
            decomp = mc.createNode("decomposeMatrix", n="mouth_curvature_{0}_decomp".format(index))
            attr = "worldMatrix[0]" if mc.objExists("{0}.worldMatrix[0]".format(inf)) else "matrixSum"
            mc.connectAttr("{0}.{1}".format(inf, attr), "{0}.inputMatrix".format(decomp))
            mc.connectAttr("{0}.outputTranslate".format(decomp), "{0}.controlPoints[{1}]".format(shape_crv, index))
            new_nodes.append(decomp)

        tagging_utils.tag_nodes(new_nodes, tag=self.uuid.hex)

    def joints_creation(self):
        """Create joints based on attributes values and guides. (without positioning as this point). """
        self.jaw_jnt = self.add_joint(name="jaw", skinning_jnt=True, tag_parent_jnt=None, radius=1)

        self.m_up_jnt = self.add_joint(name="M_upper_lip", skinning_jnt=False, radius=1)
        self.m_low_jnt = self.add_joint(name="M_lower_lip", skinning_jnt=False, radius=1)

        self.l_corner_jnt = self.add_joint(name="L_corner", skinning_jnt=True, tag_parent_jnt=self.jaw_jnt)
        self.l_corner_jnt.radius = 0.4

        self.r_corner_jnt = self.add_joint(name="R_corner", skinning_jnt=True, tag_parent_jnt=self.jaw_jnt)
        self.r_corner_jnt.radius = 0.4

        self.up_driver_jnts = []
        for index in range(5):
            name = "upper_lip_driver_{0}".format(index)
            self.up_driver_jnts.append(self.add_joint(name=name, skinning_jnt=False, radius=0.35))

        self.low_driver_jnts = []
        for index in range(5):
            name = "lower_lip_driver_{0}".format(index)
            self.low_driver_jnts.append(self.add_joint(name=name, skinning_jnt=False, radius=0.35))

        self.up_driven_jnts = []
        self.low_driven_jnts = []
        self.ctrls_names_assist = []  # used to name ctrls later.
        count = self.skin_jnts_attr.value
        uneven = count % 2 != 0
        half = int(count / 2)
        # create joints in order so they appear in order in tree attributes.
        for jnts_list, prefix in zip([self.up_driven_jnts, self.low_driven_jnts], ["upper", "lower"]):
            for index in range(count):

                if index + 1 <= half:
                    side = "L"
                    index = index + 1

                elif index + 1 == half + 1 and uneven:
                    side = "M"
                    index = 0

                else:
                    side = "R"
                    index = count - index

                self.ctrls_names_assist.append([prefix, side, index])
                name = "{0}_lip_driven_{1}_{2}".format(prefix, side, index)
                jnts_list.append(
                    self.add_joint(name=name, skinning_jnt=True, tag_parent_jnt=self.jaw_jnt, radius=0.2)
                )

    def ctrls_creation(self):
        """Create controls based on attributes values, guides and joints. (without positioning as this point). """
        scale_mult = self.ctrls_scale_attr.value * 0.5
        offset_mult = self.offset_attr.value

        self.jaw_ctrl = self.add_ctrl(name="jaw", shape="arrow_rotation_4_way", size=1.8 * scale_mult)
        self.jaw_ctrl.rotate_offset = [180, 0, 0]
        self.jaw_ctrl.translate_offset = self.jaw_offset_attr.value

        self.master_ctrl = self.add_ctrl(name="master", shape="circle_half", size=1.5 * scale_mult)
        self.master_ctrl.rotate_offset = [0, 0, -90]
        self.master_ctrl.translate_offset = [5, 0, 0.9 * offset_mult]
        self.master_ctrl.line_width = 2

        self.l_mouth_corner_ctrl = self.add_ctrl(name="L_mouth_corner", shape="triangle", size=1.1 * scale_mult)
        self.r_mouth_corner_ctrl = self.add_ctrl(name="R_mouth_corner", shape="triangle", size=1.1 * scale_mult)

        for corner_ctrl in [self.l_mouth_corner_ctrl, self.r_mouth_corner_ctrl]:
            corner_ctrl.rotate_offset = [90, 0, -90]
            corner_ctrl.translate_offset = [0, 0, 1.0 * offset_mult]

            for attr in ["translateZ", "rotateX", "scaleX", "scaleY", "scaleZ"]:
                corner_ctrl.add_locked_hidden_attr(attr)

        self.l_lips_corner_ctrl = self.add_ctrl(name="L_lips_corner", size=0.4 * scale_mult)
        self.r_lips_corner_ctrl = self.add_ctrl(name="R_lips_corner", size=0.4 * scale_mult)

        for corner_ctrl in [self.l_lips_corner_ctrl, self.r_lips_corner_ctrl]:
            corner_ctrl.rotate_offset = [90, 0, -90]
            corner_ctrl.translate_offset = [0, 0, 1.0 * offset_mult]

        self.m_up_ctrl = self.add_ctrl(name="M_upper_lip", shape="circle_half_closed")
        self.m_up_ctrl.size = [1.5 * scale_mult, 0.5 * scale_mult, 0.5 * scale_mult]
        self.m_up_ctrl.rotate_offset = [0, 0, 0]
        self.m_up_ctrl.translate_offset = [0, 0, 1.0 * offset_mult]

        self.m_low_ctrl = self.add_ctrl(name="M_lower_lip", shape="circle_half_closed")
        self.m_low_ctrl.size = [1.5 * scale_mult, 0.5 * scale_mult, 0.5 * scale_mult]
        self.m_low_ctrl.rotate_offset = [0, 0, 180]
        self.m_low_ctrl.translate_offset = [0, 0, 1.0 * offset_mult]

        self.l_up_minor_ctrl = self.add_ctrl(name="L_upper_lip_minor", size=0.55 * scale_mult)
        self.m_up_minor_ctrl = self.add_ctrl(name="M_upper_lip_minor", size=0.55 * scale_mult)
        self.r_up_minor_ctrl = self.add_ctrl(name="R_upper_lip_minor", size=0.55 * scale_mult)
        self.l_low_minor_ctrl = self.add_ctrl(name="L_lower_lip_minor", size=0.55 * scale_mult)
        self.m_low_minor_ctrl = self.add_ctrl(name="M_lower_lip_minor", size=0.55 * scale_mult)
        self.r_low_minor_ctrl = self.add_ctrl(name="R_lower_lip_minor", size=0.55 * scale_mult)

        ctrls = [
            self.m_up_ctrl, self.m_low_ctrl, self.jaw_ctrl, self.master_ctrl, self.l_lips_corner_ctrl,
            self.r_lips_corner_ctrl,
            ]
        up_minor = [self.l_up_minor_ctrl, self.m_up_minor_ctrl, self.r_up_minor_ctrl]
        low_minor = [self.l_low_minor_ctrl, self.m_low_minor_ctrl, self.r_low_minor_ctrl]
        for ctrl in ctrls + up_minor + low_minor:
            for attr in ["scaleX", "scaleY", "scaleZ"]:
                ctrl.add_limit_attr(attr, min_active=True, min_value=0.01)

        for up_ctrl, low_ctrl in zip(up_minor, low_minor):
            up_ctrl.translate_offset = [0, 0.3, 1.0 * offset_mult]
            low_ctrl.translate_offset = [0, -0.3, 1.0 * offset_mult]

            for ctrl in [up_ctrl, low_ctrl]:
                ctrl.rotate_offset = [90, 0, -90]

                for attr in ["scaleX", "scaleZ"]:
                    ctrl.add_locked_hidden_attr(attr)

        self.micro_up_ctrls = []
        self.micro_low_ctrls = []
        if self.micro_ctrls_attr.value:

            for prefix, side, index in self.ctrls_names_assist:
                name = "{0}_lip_micro_{1}_{2}".format(prefix, side, index)
                micro = self.add_ctrl(name=name, size=0.4 * scale_mult, shape="box")
                micro.color = SECONDARY_COLOR

                if prefix == "upper":
                    self.micro_up_ctrls.append(micro)
                else:
                    self.micro_low_ctrls.append(micro)

    def maya_attrs_creation(self):
        """Declare any Maya attributes that users should be able to modify. """
        self.master_ctrl.add_maya_attr(name="auto_volume", attr_type="float", default_value=1, min=0, max=1)

        if self.micro_ctrls_attr.value:
            self.master_ctrl.add_maya_attr(name="micro_ctrls", attr_type="bool", default_value=False)

        self.jaw_ctrl.add_maya_attr(name="jaw_auto_forward", attr_type="float", default_value=0, min=0, max=1000)
        self.jaw_ctrl.add_maya_attr(name="lips_seal_height", attr_type="float", default_value=0.5, min=0, max=1)

        self.l_mouth_corner_ctrl.add_maya_attr(name="follow_jaw", attr_type="float", default_value=0.3, min=0, max=1)
        self.r_mouth_corner_ctrl.add_maya_attr(name="follow_jaw", attr_type="float", default_value=0.3, min=0, max=1)
        self.m_low_ctrl.add_maya_attr(name="follow_jaw", attr_type="float", default_value=1, min=0, max=1)
        self.m_up_ctrl.add_maya_attr(name="follow_jaw", attr_type="float", default_value=0, min=0, max=1)

        if self.up_push_attr.value:
            self.m_up_ctrl.add_maya_attr(name="upper_lip_push", attr_type="float", default_value=0, min=0, max=1)

    def rig_creation(self):
        """Based on attributes value, guides (which now you can get global position from) joints and controls
        created in their methods you can build the rig.
        """
        if self.is_mirrored:
            LOGGER.error("[node] '%s' does not support mirroring. Skipping node build!", self.name)
            return False  # need to return False to return failed error during build.

        grps = create_grps(self, ["input_grp", "head_output_grp", "jaw_output_grp"])
        input_grp, head_output_grp, jaw_output_grp = grps
        ctrls_grp, jnts_grp, data_grp = create_grps(self, ["ctrls_grp", "jnts_grp", "module_data_grp"])

        data_grp.set_attr("inheritsTransform", 0)
        data_grp.set_attr("visibility", 0)
        data_grp.lock_and_hide_transformations(vis=False)

        self.driven_root_attr.set_maya_object(input_grp)
        self.driver_head_attr.set_maya_object(head_output_grp)
        self.driver_jaw_attr.set_maya_object(jaw_output_grp)

        l_corner_jnt = self.l_corner_jnt.pointer
        r_corner_jnt = self.r_corner_jnt.pointer
        m_up_jnt = self.m_up_jnt.pointer
        m_low_jnt = self.m_low_jnt.pointer
        jaw_jnt = self.jaw_jnt.pointer

        m_up_jnt.set_attr("visibility", 0)
        m_low_jnt.set_attr("visibility", 0)

        jnt_guide_pairs = [
            [l_corner_jnt, self.l_corner_guide],
            [m_up_jnt, self.up_mid_guide],
            [m_low_jnt, self.low_mid_guide],
            [jaw_jnt, self.jaw_guide],
        ]

        for jnt, guide in jnt_guide_pairs:
            jnt.parent_relative(jnts_grp)
            jnt.set_matrix(guide.world_transformations["matrix"], space="world")
            jnt.freeze_transformations()
            jnt.add_joint_orient()

        r_corner_jnt.offset_grp = r_corner_jnt.add_group_above("{0}_offset_grp".format(r_corner_jnt.short_name))
        r_corner_jnt.offset_grp.parent_relative(jnts_grp)
        r_corner_jnt.offset_grp.set_attr("scaleX", -1)
        r_corner_jnt.freeze_transformations()
        r_corner_jnt.add_joint_orient()
        r_corner_jnt.set_translation(self.r_corner_guide.world_transformations["translate"], space="world")
        rotation = self.r_corner_guide.world_transformations["rotate"]
        rotation = [value*mult for value, mult in zip(rotation, [1, -1, -1])]  # mirror values.
        r_corner_jnt.set_rotation(rotation, space="object")

        ctrls_grp.match_transformation_to(jaw_jnt)

        name = "{0}_offset_grp".format(jaw_jnt.short_name)
        jaw_jnt.offset_grp = jaw_jnt.add_group_above(name, maintain_local_values=False)
        jaw_jnt.zero_joint_orient()

        # jaw ctrl setup.
        jaw_ctrl = self.jaw_ctrl.pointer
        jaw_ctrl.forward_grp = jaw_ctrl.offset_grp.add_group_above("{0}_forward_grp".format(jaw_ctrl.short_name))
        jaw_ctrl.forward_grp.parent_relative(ctrls_grp)

        matrix_constraint(jaw_ctrl, jaw_jnt, maintain_offset=False)

        jaw_ctrl.add_spacer_attr()
        jaw_ctrl.forward_attr = jaw_ctrl.add_attr("jaw_auto_forward", dv=0, min=0, keyable=True)
        jaw_ctrl.add_spacer_attr()
        jaw_ctrl.seal_attr = jaw_ctrl.add_attr("lips_seal", dv=0, min=0, max=1, keyable=True)
        jaw_ctrl.seal_height_attr = jaw_ctrl.add_attr("lips_seal_height", dv=0.5, min=0, max=1, keyable=True)

        remap = mc.createNode("remapValue", n="{0}_push_forward_remapValue".format(self.name))
        mc.connectAttr(jaw_ctrl.attr("rotateX"), "{0}.inputValue".format(remap))
        mc.connectAttr(jaw_ctrl.forward_attr, "{0}.outputMax".format(remap))
        mc.setAttr("{0}.inputMin".format(remap), 5)
        mc.setAttr("{0}.inputMax".format(remap), 125)
        mc.setAttr("{0}.outputMin".format(remap), 0)
        mc.connectAttr("{0}.outValue".format(remap), jaw_ctrl.forward_grp.attr("translateZ"))

        # lips ctrls setup.
        l_mouth_ctrl = self.l_mouth_corner_ctrl.pointer
        r_mouth_ctrl = self.r_mouth_corner_ctrl.pointer
        l_lips_ctrl = self.l_lips_corner_ctrl.pointer
        r_lips_ctrl = self.r_lips_corner_ctrl.pointer

        m_up_ctrl = self.m_up_ctrl.pointer
        m_low_ctrl = self.m_low_ctrl.pointer

        l_mouth_ctrl.jnt = l_lips_ctrl.jnt = l_corner_jnt
        r_mouth_ctrl.jnt = r_lips_ctrl.jnt = r_corner_jnt
        m_low_ctrl.jnt = m_low_jnt
        m_up_ctrl.jnt = m_up_jnt

        l_up_minor_ctrl = self.l_up_minor_ctrl.pointer
        m_up_minor_ctrl = self.m_up_minor_ctrl.pointer
        r_up_minor_ctrl = self.r_up_minor_ctrl.pointer

        l_low_minor_ctrl = self.l_low_minor_ctrl.pointer
        m_low_minor_ctrl = self.m_low_minor_ctrl.pointer
        r_low_minor_ctrl = self.r_low_minor_ctrl.pointer

        master_ctrl = self.master_ctrl.pointer

        name = "{0}_scale_offset".format(master_ctrl.short_name)
        master_ctrl.scale_grp = master_ctrl.offset_grp.add_group_above(name)
        master_ctrl.scale_grp.parent_relative(ctrls_grp)
        mc.connectAttr(jaw_ctrl.attr("scale"), master_ctrl.scale_grp.attr("scale"))

        master_pos = mid_point(r_corner_jnt.get_translation(), l_corner_jnt.get_translation())
        master_ctrl.offset_grp.set_translation(master_pos, space="world")

        module_scale_attr = create_module_scale(parent_to=master_ctrl, name_prefix=self.name)

        lips_ctrls_grp = IoTransform("lips_ctrls_grp", existing=False)
        lips_ctrls_grp.parent_relative(master_ctrl)
        lips_ctrls_grp.match_transformation_to(jaw_jnt)

        ctrls = [l_mouth_ctrl, r_mouth_ctrl, m_up_ctrl, m_low_ctrl]
        for ctrl, value, max_value in zip(ctrls, [0.3, 0.3, 0, 1], [0.6, 0.6, 1, 1]):
            ctrl.driver_grp = ctrl.offset_grp.add_group_above("{0}_driver_grp".format(ctrl.short_name))
            ctrl.driver_grp.parent_relative(lips_ctrls_grp)

            ctrl.add_spacer_attr()
            ctrl.follow_attr = ctrl.add_attr("follow_jaw", dv=value, min=0, max=max_value, keyable=True)

            mult_trans = mc.createNode("multiplyDivide", n="{0}_translate_mult".format(ctrl.short_name))
            mc.connectAttr(jaw_jnt.attr("translate"), "{0}.input1".format(mult_trans))
            mc.connectAttr(ctrl.follow_attr, "{0}.input2X".format(mult_trans))
            mc.connectAttr(ctrl.follow_attr, "{0}.input2Y".format(mult_trans))
            mc.connectAttr(ctrl.follow_attr, "{0}.input2Z".format(mult_trans))
            mc.connectAttr("{0}.output".format(mult_trans), ctrl.driver_grp.attr("translate"))

            mult_rotate = mc.createNode("multiplyDivide", n="{0}_rotate_mult".format(ctrl.short_name))
            mc.connectAttr(jaw_jnt.attr("rotate"), "{0}.input1".format(mult_rotate))
            mc.connectAttr(ctrl.follow_attr, "{0}.input2X".format(mult_rotate))
            mc.connectAttr(ctrl.follow_attr, "{0}.input2Y".format(mult_rotate))
            mc.connectAttr(ctrl.follow_attr, "{0}.input2Z".format(mult_rotate))
            mc.connectAttr("{0}.output".format(mult_rotate), ctrl.driver_grp.attr("rotate"))

        for ctrl in [l_mouth_ctrl, m_up_ctrl, m_low_ctrl]:
            ctrl.offset_grp.match_transformation_to(ctrl.jnt)

        # R side is mirrored.
        r_mouth_ctrl.mirror_grp = IoTransform("{0}_mirror_grp".format(r_mouth_ctrl.short_name))
        r_mouth_ctrl.mirror_grp.parent_relative(self.module_grp)
        r_mouth_ctrl.mirror_grp.set_attr("scaleX", -1)
        r_mouth_ctrl.mirror_grp.parent(r_mouth_ctrl.driver_grp)

        r_mouth_ctrl.offset_grp.parent_relative(r_mouth_ctrl.mirror_grp)
        r_mouth_ctrl.offset_grp.match_transformation_to(r_mouth_ctrl.jnt)

        l_lips_ctrl.offset_grp.parent_relative(l_mouth_ctrl)
        r_lips_ctrl.offset_grp.parent_relative(r_mouth_ctrl)

        matrix_constraint(l_lips_ctrl, l_lips_ctrl.jnt, maintain_offset=False)
        matrix_constraint(r_lips_ctrl, r_lips_ctrl.jnt, maintain_offset=False)

        # curves setup.
        curves_grp = IoTransform("lips_curves_grp", existing=False)
        curves_grp.parent_relative(data_grp)
        curves_grp.lock_and_hide_transformations()

        up_guides = [
            self.l_corner_guide, self.l_up_minor_guide, self.up_mid_guide, self.r_up_minor_guide,
            self.r_corner_guide,
        ]
        low_guides = [
            self.l_corner_guide, self.l_low_minor_guide, self.low_mid_guide, self.r_low_minor_guide,
            self.r_corner_guide,
        ]
        up_jnts = [l_corner_jnt, m_up_jnt, r_corner_jnt]
        low_jnts = [l_corner_jnt, m_low_jnt, r_corner_jnt]
        all_curves = []
        for prefix, guides, jnts in [["upper", up_guides, up_jnts], ["lower", low_guides, low_jnts]]:
            skin_curve = mc.curve(
                name="{0}_{1}_skinning_curve".format(self.name, prefix),
                degree=3,
                point=[guide.world_transformations["translate"] for guide in guides],
                knot=[0, 0, 0, 1, 2, 2, 2],
                worldSpace=True,
            )
            skin_curve = IoTransform(skin_curve, existing=True)
            mc.rename(skin_curve.get_shapes()[0], "{0}Shape".format(skin_curve.short_name))

            bs_curve = mc.duplicate(skin_curve, n="{0}_{1}_with_bs_curve".format(self.name, prefix))[0]
            bs_curve = IoTransform(bs_curve, existing=True)
            bs_curve.set_attr("visibility", 0)

            all_curves.append([skin_curve, bs_curve])

            skin_curve.parent_relative(curves_grp)
            bs_curve.parent_relative(curves_grp)

            # skin curve.
            skin_cluster = mc.skinCluster(
                jnts,
                skin_curve,
                name="{0}_skin_cluster".format(skin_curve.short_name),
                skinMethod=0,  # classic linear.
            )[0]

            # fix skinning weights of curve.
            mc.setAttr("{0}.normalizeWeights".format(skin_cluster), 0)
            for index, value in zip([0, 2, 4], [[1, 0, 0], [0, 1, 0], [0, 0, 1]]):
                curve_cv = "{0}.cv[{1}]".format(skin_curve, index)
                mc.skinPercent(skin_cluster, curve_cv, normalize=False, pruneWeights=100)
                mc.skinPercent(
                    skin_cluster,
                    curve_cv,
                    transformValue=[(jnts[0], value[0]), (jnts[1], value[1]), (jnts[2], value[2])],
                )

            mid_pos = jnts[1].get_translation()
            for cv_index, corner_jnt in [[1, l_corner_jnt], [3, r_corner_jnt]]:
                curve_cv = "{0}.cv[{1}]".format(skin_curve, cv_index)
                cv_pos = mc.xform(curve_cv, q=True, ws=True, translation=True)

                corner_pos = corner_jnt.get_translation()
                distance_from_corner = distance_between(corner_pos, cv_pos)
                distance_from_mid = distance_between(mid_pos, cv_pos)
                total_distance = distance_from_mid + distance_from_corner

                mc.skinPercent(skin_cluster, curve_cv, normalize=False, pruneWeights=100)
                mc.skinPercent(
                    skin_cluster,
                    curve_cv,
                    transformValue=[
                        # bias attribute where values above 1 give more control to M_lip_ctrl.
                        (corner_jnt, distance_from_corner * (2.0 - self.bias_attr.value) / total_distance),
                        (jnts[1], distance_from_mid * self.bias_attr.value / total_distance),
                    ],
                )

            mc.setAttr("{0}.normalizeWeights".format(skin_cluster), 1)
            mc.skinCluster(skin_cluster, e=True, forceNormalizeWeights=True)
            mc.connectAttr(skin_curve.attr("local"), bs_curve.attr("create"))

        up_skin_crv, up_bs_crv = all_curves[0]
        low_skin_crv, low_bs_crv = all_curves[1]

        lips_close_crv = mc.duplicate(up_bs_crv, n="{0}_lips_closed_curve".format(self.name))[0]
        lips_close_crv = IoTransform(lips_close_crv, existing=True)
        lips_close_crv.set_attr("visibility", 0)
        mc.connectAttr(up_skin_crv.attr("local"), lips_close_crv.attr("create"))

        name = "{0}_BS".format(lips_close_crv.short_name)
        lips_close_crv.bs = mc.blendShape(low_skin_crv, lips_close_crv, automatic=True, name=name)[0]
        mc.connectAttr(jaw_ctrl.seal_height_attr, "{0}.weight[0]".format(lips_close_crv.bs))

        name = "{0}_BS".format(up_bs_crv.short_name)
        up_bs_crv.bs = mc.blendShape(lips_close_crv, up_bs_crv, automatic=True, name=name)[0]
        mc.connectAttr(jaw_ctrl.seal_attr, "{0}.weight[0]".format(up_bs_crv.bs))

        name = "{0}_BS".format(low_bs_crv.short_name)
        low_bs_crv.bs = mc.blendShape(lips_close_crv, low_bs_crv, automatic=True, name=name)[0]
        mc.connectAttr(jaw_ctrl.seal_attr, "{0}.weight[0]".format(low_bs_crv.bs))

        # connect minor ctrls to curve.
        minor_ctrls_grp = IoTransform("minor_ctrls_grp", existing=False)
        minor_ctrls_grp.parent_relative(ctrls_grp)
        minor_ctrls_grp.set_attr("inheritsTransform", 0)

        up_ctrls = [l_up_minor_ctrl, m_up_minor_ctrl, r_up_minor_ctrl]
        low_ctrls = [l_low_minor_ctrl, m_low_minor_ctrl, r_low_minor_ctrl]
        for prefix, curve, ctrls in [["upper", up_bs_crv, up_ctrls], ["lower", low_bs_crv, low_ctrls]]:
            curve_info = mc.createNode("curveInfo", n="{0}_curveInfo".format(curve.short_name))
            mc.connectAttr(curve.attr("worldSpace[0]"), "{0}.inputCurve".format(curve_info))

            sect_minor_grp = IoTransform("{0}_minor_ctrls_grp".format(prefix), existing=False)
            sect_minor_grp.parent_relative(minor_ctrls_grp)
            sect_minor_grp.lock_and_hide_transformations()

            for index, ctrl in zip([1, 2, 3], ctrls):
                ctrl.offset_grp.parent_relative(sect_minor_grp)
                mc.connectAttr(
                    "{0}.controlPoints[{1}]".format(curve_info, index),
                    ctrl.offset_grp.attr("translate"),
                )

                mc.connectAttr(module_scale_attr, ctrl.offset_grp.attr("scaleX"))
                mc.connectAttr(module_scale_attr, ctrl.offset_grp.attr("scaleY"))
                mc.connectAttr(module_scale_attr, ctrl.offset_grp.attr("scaleZ"))

        # roll setup.
        up_ctrls = [m_up_ctrl, l_up_minor_ctrl, m_up_minor_ctrl, r_up_minor_ctrl]
        low_ctrls = [m_low_ctrl, l_low_minor_ctrl, m_low_minor_ctrl, r_low_minor_ctrl]
        for ctrls, pos in [[up_ctrls, self.up_roll_attr.value], [low_ctrls, self.low_roll_attr.value]]:
            for ctrl in ctrls:
                if self.enable_roll_attr.value:
                    ctrl.add_spacer_attr()
                    ctrl.roll_attr = ctrl.add_attr("roll", keyable=True, dv=0)
                    ctrl.vis_attr = ctrl.add_attr("roll_loc_vis", attributeType="bool", keyable=True, dv=0)

                    loc = IoTransform(mc.spaceLocator(n="{0}_roll_loc".format(ctrl.short_name))[0], existing=True)
                    loc.set_attr("displayHandle", 1)
                    loc.set_attr("localScale", [0.5, 0.5, 0.5])
                    loc.set_color([1, 1, 1])

                    loc.parent_relative(ctrl)
                    loc.set_translation(pos, space="object")
                    loc.connect_attr("visibility", ctrl.vis_attr)

                    if ctrl in low_ctrls:
                        loc.connect_attr("rotateX", ctrl.roll_attr)

                    else:
                        mult = mc.createNode(MULT_DL, n="{0}_roll_reverse_mult".format(ctrl.short_name))
                        mc.connectAttr(ctrl.roll_attr, "{0}.{1}".format(mult, MULT_DL_INPUT1))
                        mc.setAttr("{0}.{1}".format(mult, MULT_DL_INPUT2), -1)
                        loc.connect_attr("rotateX", "{0}.output".format(mult))

                    loc.lock_and_hide_rotation()
                    loc.lock_and_hide_scale()
                    loc.lock_and_hide_vis()

                    ctrl.reverse_grp = IoTransform("{0}_loc_reverse_grp".format(ctrl.short_name), existing=False)
                    ctrl.reverse_grp.parent_relative(loc)

                    rev_mult = mc.createNode("multiplyDivide", n="{0}_roll_reverse_mult".format(ctrl.short_name))
                    mc.setAttr("{0}.operation".format(rev_mult), 1)  # multiply.
                    mc.connectAttr(loc.attr("translate"), "{0}.input1".format(rev_mult))
                    mc.setAttr("{0}.input2".format(rev_mult), *[-1, -1, -1])
                    mc.connectAttr("{0}.output".format(rev_mult), ctrl.reverse_grp.attr("translate"))

                    ctrl.holder_grp = IoTransform("{0}_constraint_holder_grp".format(ctrl.short_name))
                    ctrl.holder_grp.parent_relative(ctrl.reverse_grp)

                else:
                    ctrl.holder_grp = IoTransform("{0}_constraint_holder_grp".format(ctrl.short_name))
                    ctrl.holder_grp.parent_relative(ctrl)

        matrix_constraint(m_up_ctrl.holder_grp, m_up_ctrl.jnt, maintain_offset=False)
        matrix_constraint(m_low_ctrl.holder_grp, m_low_ctrl.jnt, maintain_offset=False)

        # minor ctrls orient setup (by positioning driver grps at driven pos we avoid potential flipping).
        constraint = m_up_minor_ctrl.offset_grp.orient_constraint_to(m_up_ctrl.holder_grp, mo=False)
        mc.setAttr("{0}.interpType".format(constraint), 2)  # shortest.
        constraint = m_low_minor_ctrl.offset_grp.orient_constraint_to(m_low_ctrl.holder_grp, mo=False)
        mc.setAttr("{0}.interpType".format(constraint), 2)  # shortest.

        ctrls_and_drivers = [
            [l_up_minor_ctrl, [l_mouth_ctrl, m_up_ctrl]],
            [r_up_minor_ctrl, [r_mouth_ctrl, m_up_ctrl]],
            [l_low_minor_ctrl, [l_mouth_ctrl, m_low_ctrl]],
            [r_low_minor_ctrl, [r_mouth_ctrl, m_low_ctrl]],
        ]
        # minor follow evenly between mid and corner (solution for flipping when corners move close to mid).
        for ctrl, drivers in ctrls_and_drivers:
            ctrl.pos_grp = ctrl.add_group_above("{0}_pos_grp".format(ctrl.short_name))
            ctrl.pos_grp.point_constraint_to(drivers, maintainOffset=True, skip=["y", "z"])

        r_lips_ctrl.reverse_scale = IoTransform("{0}_reverse_scale_grp".format(r_lips_ctrl.short_name))
        r_lips_ctrl.reverse_scale.parent_relative(r_lips_ctrl)
        r_lips_ctrl.reverse_scale.set_attr("scaleX", -1)

        driver_ctrls = [
            [l_lips_ctrl, m_up_ctrl.holder_grp],
            [m_up_ctrl.holder_grp, r_lips_ctrl.reverse_scale],
            [l_lips_ctrl, m_low_ctrl.holder_grp],
            [m_low_ctrl.holder_grp, r_lips_ctrl.reverse_scale],
        ]
        ctrls = [l_up_minor_ctrl, r_up_minor_ctrl, l_low_minor_ctrl, r_low_minor_ctrl]
        guides = [self.l_up_minor_guide, self.r_up_minor_guide, self.l_low_minor_guide, self.r_low_minor_guide]
        for ctrl, drivers, guide in zip(ctrls, driver_ctrls, guides):
            ctrl.offset_grp.set_rotation(guide.world_transformations["rotate"])

            driver_grps = []
            for driver in drivers:
                drive_grp = IoTransform("{0}_{1}_orient_grp".format(driver.short_name, ctrl.short_name))
                drive_grp.parent_relative(ctrl)
                drive_grp.parent(driver)
                driver_grps.append(drive_grp)

            constraint = ctrl.offset_grp.orient_constraint_to(driver_grps)
            mc.setAttr("{0}.interpType".format(constraint), 2)  # shortest.

        if self.up_push_attr.value:
            self.push_up()

        # ribbons setup.
        r_corner_jnt.scale_grp = IoTransform("{0}_scale_reverse_grp".format(r_corner_jnt.short_name))
        r_corner_jnt.scale_grp.parent_relative(r_corner_jnt)
        r_corner_jnt.scale_grp.set_attr("scaleX", -1)

        up_ribbon = ComplexRibbon(
            driver_joints=[jnt.pointer for jnt in self.up_driver_jnts],
            driven_joints=[jnt.pointer for jnt in self.up_driven_jnts],
            rest_length=mc.arclen(up_skin_crv, constructionHistory=False),
            name_prefix="{0}_upper_lip_ribbon".format(self.name),
            parent_to=data_grp,
            is_mirrored=self.is_mirrored,
        )

        low_ribbon = ComplexRibbon(
            driver_joints=[jnt.pointer for jnt in self.low_driver_jnts],
            driven_joints=[jnt.pointer for jnt in self.low_driven_jnts],
            rest_length=mc.arclen(low_skin_crv, constructionHistory=False),
            name_prefix="{0}_lower_lip_ribbon".format(self.name),
            parent_to=data_grp,
            is_mirrored=self.is_mirrored,
        )

        up_drivers = [
            l_corner_jnt, l_up_minor_ctrl.holder_grp, m_up_minor_ctrl.holder_grp, r_up_minor_ctrl.holder_grp,
            r_corner_jnt.scale_grp,
        ]
        low_drivers = [
            l_corner_jnt, l_low_minor_ctrl.holder_grp, m_low_minor_ctrl.holder_grp, r_low_minor_ctrl.holder_grp,
            r_corner_jnt.scale_grp,
        ]
        for drivers, ribbon in [[up_drivers, up_ribbon], [low_drivers, low_ribbon]]:
            for driver, driver_jnt in zip(drivers, ribbon.driver_joints):
                driver_jnt.offset_grp.parent_relative(driver)
                driver_jnt.offset_grp.zero_local_transformations()
                driver_jnt.offset_grp.set_attr("rotateX", 90)
                driver_jnt.offset_grp.set_attr("rotateY", -90)

        # pinch setup.
        l_mouth_ctrl.add_spacer_attr()
        l_mouth_ctrl.pinch_attr = l_mouth_ctrl.add_attr("corner_pinch", dv=0, keyable=True)
        mc.connectAttr(l_mouth_ctrl.pinch_attr, low_ribbon.driver_joints[0].offset_grp.attr("translateY"))

        mult_node = mc.createNode(MULT_DL, n="{0}_reverse_pinch_mult".format(l_mouth_ctrl.short_name))
        mc.connectAttr(l_mouth_ctrl.pinch_attr, "{0}.{1}".format(mult_node, MULT_DL_INPUT1))
        mc.setAttr("{0}.{1}".format(mult_node, MULT_DL_INPUT2), -1)
        mc.connectAttr("{0}.output".format(mult_node), up_ribbon.driver_joints[0].offset_grp.attr("translateY"))

        r_mouth_ctrl.add_spacer_attr()
        r_mouth_ctrl.pinch_attr = r_mouth_ctrl.add_attr("corner_pinch", dv=0, keyable=True)
        mc.connectAttr(r_mouth_ctrl.pinch_attr, low_ribbon.driver_joints[-1].offset_grp.attr("translateY"))

        mult_node = mc.createNode(MULT_DL, n="{0}_reverse_pinch_mult".format(r_mouth_ctrl.short_name))
        mc.connectAttr(r_mouth_ctrl.pinch_attr, "{0}.{1}".format(mult_node, MULT_DL_INPUT1))
        mc.setAttr("{0}.{1}".format(mult_node, MULT_DL_INPUT2), -1)
        mc.connectAttr("{0}.output".format(mult_node), up_ribbon.driver_joints[-1].offset_grp.attr("translateY"))

        # zipper setup.
        for surface in [up_ribbon.nurb_surface, low_ribbon.nurb_surface]:
            bs_surface = mc.nurbsPlane(constructionHistory=False, n="{0}_BsSurf".format(surface.short_name))
            surface.bs_surface = IoTransform(bs_surface, existing=True)
            plugs = mc.listConnections(surface.attr("local"), destination=True, plugs=True)
            surface.bs_surface.connect_attr("create", surface.attr("local"))
            surface.bs_surface.parent(surface.get_parent())

            for plug in plugs:
                mc.connectAttr(surface.bs_surface.attr("local"), plug, f=True)

        up_ribbon.bs = mc.blendShape(
            low_ribbon.nurb_surface,
            up_ribbon.nurb_surface.bs_surface,
            weight=[(0, 0.5)],
            n="{0}_BS".format(up_ribbon.nurb_surface.bs_surface.short_name),
        )[0]

        low_ribbon.bs = mc.blendShape(
            up_ribbon.nurb_surface,
            low_ribbon.nurb_surface.bs_surface,
            weight=[(0, 0.5)],
            n="{0}_BS".format(low_ribbon.nurb_surface.bs_surface.short_name),
        )[0]

        l_mouth_ctrl.zip_attr = l_mouth_ctrl.add_attr("zipper", dv=0, min=0, max=1, keyable=True)
        r_mouth_ctrl.zip_attr = r_mouth_ctrl.add_attr("zipper", dv=0, min=0, max=1, keyable=True)

        self.zipper_setup(
            jnts_count=len(self.up_driven_jnts),
            bs_nodes=[up_ribbon.bs, low_ribbon.bs],
            root_attr=l_mouth_ctrl.zip_attr,
            tip_attr=r_mouth_ctrl.zip_attr,
        )

        master_ctrl.add_spacer_attr()
        volume_attr = master_ctrl.add_attr("auto_volume", dv=1, min=0, max=1, keyable=True)
        thick_attr = master_ctrl.add_attr("thickness", dv=1, min=0.001, keyable=True)

        self.volume_setup(
            ribbon=up_ribbon,
            auto_attr=volume_attr,
            thick_attr=thick_attr,
            module_scale_attr=module_scale_attr,
        )
        self.volume_setup(
            ribbon=low_ribbon,
            auto_attr=volume_attr,
            thick_attr=thick_attr,
            module_scale_attr=module_scale_attr,
        )

        if self.micro_ctrls_attr.value:
            self.micro_setup(up_ribbon=up_ribbon, low_ribbon=low_ribbon, module_scale_attr=module_scale_attr)

        self.corner_ctrls_curvature(data_grp=data_grp)

        for ribbon in [up_ribbon, low_ribbon]:
            ribbon.driven_jnts_grp.parent_relative(jnts_grp)
            ribbon.driven_jnts_grp.set_attr("inheritsTransform", 0)
            ribbon.driver_jnts_grp.set_attr("visibility", 0)
            mc.connectAttr(module_scale_attr, ribbon.driven_jnts_grp.attr("scaleX"))
            mc.connectAttr(module_scale_attr, ribbon.driven_jnts_grp.attr("scaleY"))
            mc.connectAttr(module_scale_attr, ribbon.driven_jnts_grp.attr("scaleZ"))
            mc.delete([ribbon.jnts_grp, ribbon.ctrls_grp])

        input_grp.match_transformation_to(ctrls_grp)
        matrix_constraint(driver=input_grp, driven=ctrls_grp, maintain_offset=True)
        matrix_constraint(driver=input_grp, driven=jnts_grp, maintain_offset=True)
        head_output_grp.parent_relative(input_grp)
        head_output_grp.direct_connect(jaw_jnt, translate=False, rotate=False, scale=True)
        matrix_constraint(driver=jaw_jnt, driven=jaw_output_grp, maintain_offset=False)

    def push_up(self):
        """Create push upper lip setup. """
        up_ctrl = self.m_up_ctrl.pointer
        low_ctrl = self.m_low_ctrl.pointer
        master_ctrl = self.master_ctrl.pointer

        up_ctrl.add_spacer_attr()
        up_ctrl.push_attr = up_ctrl.add_attr("upper_lip_push", keyable=True, dv=0, min=0, max=1)

        loc_up = IoTransform(mc.spaceLocator(n="{0}_push_loc".format(up_ctrl.short_name))[0], existing=True)
        loc_up.parent_relative(master_ctrl)
        loc_up.set_attr("visibility", 0)
        loc_up.point_constraint_to(up_ctrl, maintainOffset=False)

        loc_low = IoTransform(mc.spaceLocator(n="{0}_push_loc".format(low_ctrl.short_name))[0], existing=True)
        loc_low.parent_relative(master_ctrl)
        loc_low.set_attr("visibility", 0)
        loc_low.point_constraint_to(low_ctrl, maintainOffset=False)

        minus_node = mc.createNode("plusMinusAverage", n="{0}_push_plusMinusAverage".format(loc_up.short_name))
        mc.setAttr("{0}.operation".format(minus_node), 2)  # subtract.
        mc.connectAttr("{0}.translateY".format(loc_low), "{0}.input3D[0].input3Dx".format(minus_node))
        mc.connectAttr("{0}.translateY".format(loc_up), "{0}.input3D[1].input3Dx".format(minus_node))

        clamp = mc.createNode("clamp", n="{0}_push_clamp".format(loc_up.short_name))
        mc.setAttr("{0}.minR".format(clamp), 0)
        mc.setAttr("{0}.maxR".format(clamp), 1000)
        mc.connectAttr("{0}.output3Dx".format(minus_node), "{0}.inputR".format(clamp))

        mult_node = mc.createNode(MULT_DL, n="{0}_push_multDoubleLinear".format(loc_up.short_name))
        mc.connectAttr("{0}.outputR".format(clamp), "{0}.{1}".format(mult_node, MULT_DL_INPUT1))
        mc.connectAttr(up_ctrl.push_attr, "{0}.{1}".format(mult_node, MULT_DL_INPUT2))

        up_ctrl.push_grp = up_ctrl.holder_grp.add_group_above("{0}_push_grp".format(up_ctrl.short_name))
        mc.connectAttr("{0}.output".format(mult_node), up_ctrl.push_grp.attr("translateY"))

    @staticmethod
    def zipper_setup(jnts_count, bs_nodes, root_attr, tip_attr):
        """Create zipper setup for lips ribbons.

        Args:
            jnts_count (int): number of driven joints on a ribbon
            bs_nodes (list): of 2 str names of blendShape nodes
            root_attr (str): long name of attribute to activate zipper from root
            tip_attr (str): long name of attribute to activate zipper from tip
        """
        total_vrts = (jnts_count + 3) * 4
        half = int(total_vrts / 2)
        fraction = 1.0 / round((half-4) / 4.0)

        min_value = 0
        max_value = fraction
        for idx in range(half):

            if idx in [0, 1, 2, 3]:
                continue

            if idx % 4 == 0:
                index_str = int(idx / 4)
                remap_a = mc.createNode("remapValue", n="{0}_zipper_{1}_remapValue".format(bs_nodes[0], index_str))
                mc.connectAttr(root_attr, "{0}.inputValue".format(remap_a))
                mc.setAttr("{0}.inputMin".format(remap_a), min_value)
                mc.setAttr("{0}.inputMax".format(remap_a), max_value)

            for bs_node in bs_nodes:
                mc.connectAttr(
                    "{0}.outValue".format(remap_a),
                    "{0}.inputTarget[0].inputTargetGroup[0].targetWeights[{1}]".format(bs_node, idx),
                )

            if idx % 4 == 0:
                index_str = int(idx / 4)
                remap_b = mc.createNode("remapValue", n="{0}_zipper_{1}_remapValue".format(bs_nodes[1], index_str))
                mc.connectAttr(tip_attr, "{0}.inputValue".format(remap_b))
                mc.setAttr("{0}.inputMin".format(remap_b), min_value)
                mc.setAttr("{0}.inputMax".format(remap_b), max_value)
                min_value = max_value
                max_value += fraction

            for bs_node in bs_nodes:
                mc.connectAttr(
                    "{0}.outValue".format(remap_b),
                    "{0}.inputTarget[0].inputTargetGroup[0].targetWeights[{1}]".format(bs_node, total_vrts-idx-1),
                )

    @staticmethod
    def volume_setup(ribbon, auto_attr, thick_attr, module_scale_attr):
        """Create volume setup for provided ribbon skinning joints.

        Args:
            ribbon (SimpleRibbon): a ribbon object
            auto_attr (str): long name of auto volume
            thick_attr (str): long name of thickness attr
            module_scale_attr (str): long name of attribute from module scale to support rig scale
        """
        arch_node = mc.createNode("arcLengthDimension", n="{0}_ribbon_length".format(ribbon.name_prefix))

        arch_parent = IoTransform(mc.listRelatives(arch_node, parent=True)[0], existing=True)
        arch_parent.rename("{0}_archLengthDim".format(ribbon.name_prefix))
        arch_parent.set_attr("visibility", 0)
        arch_parent.parent_relative(ribbon.ribbon_shape_grp)

        mc.connectAttr(
            "{0}.worldSpace[0]".format(ribbon.nurb_surface.bs_surface),
            "{0}.nurbsGeometry".format(arch_node),
        )
        mc.setAttr("{0}.uParamValue".format(arch_node), 1)
        mc.setAttr("{0}.vParamValue".format(arch_node), 0.5)

        scale_mult = mc.createNode(MULT_DL, n="{0}_normalize_scale_mult".format(ribbon.name_prefix))
        mc.setAttr("{0}.{1}".format(scale_mult, MULT_DL_INPUT1), mc.getAttr("{0}.arcLength".format(arch_node)))
        mc.connectAttr(module_scale_attr, "{0}.{1}".format(scale_mult, MULT_DL_INPUT2))

        blend = mc.createNode("blendTwoAttr", n="{0}_volume_enable_blendTwoAttr".format(ribbon.name_prefix))
        mc.connectAttr("{0}.arcLength".format(arch_node), "{0}.input[0]".format(blend))
        mc.connectAttr("{0}.output".format(scale_mult), "{0}.input[1]".format(blend))
        mc.connectAttr(auto_attr, "{0}.attributesBlender".format(blend))

        divide_node = mc.createNode("multiplyDivide", n="{0}_volume_divide".format(ribbon.name_prefix))
        mc.setAttr("{0}.operation".format(divide_node), 2)  # divide.
        mc.connectAttr("{0}.arcLength".format(arch_node), "{0}.input2X".format(divide_node))
        mc.connectAttr("{0}.output".format(blend), "{0}.input1X".format(divide_node))

        remap = mc.createNode("remapValue", n="{0}_volume_remapValue".format(ribbon.name_prefix))
        mc.connectAttr("{0}.outputX".format(divide_node), "{0}.inputValue".format(remap))
        mc.setAttr("{0}.inputMin".format(remap), 0.5)
        mc.setAttr("{0}.inputMax".format(remap), 1.5)
        mc.setAttr("{0}.outputMin".format(remap), 0.5)
        mc.setAttr("{0}.outputMax".format(remap), 1.5)

        mc.setAttr("{0}.value[1].value_FloatValue".format(remap), 0.5)
        mc.setAttr("{0}.value[1].value_Position".format(remap), 0.5)

        mc.setAttr("{0}.value[2].value_FloatValue".format(remap), 1.0)
        mc.setAttr("{0}.value[2].value_Position".format(remap), 1.0)

        mc.setAttr("{0}.value[0].value_Interp".format(remap), 2)  # smooth.
        mc.setAttr("{0}.value[1].value_Interp".format(remap), 2)  # smooth.
        mc.setAttr("{0}.value[2].value_Interp".format(remap), 2)  # smooth.

        thick_z_minus = mc.createNode(ADD_DL, n="{0}_thickness_Z_minus".format(ribbon.name_prefix))
        thick_z_mult = mc.createNode(ADD_DL, n="{0}_thickness_Z_mult".format(ribbon.name_prefix))
        thick_z_add = mc.createNode(ADD_DL, n="{0}_thickness_Z_add".format(ribbon.name_prefix))
        mc.connectAttr(thick_attr, "{0}.input1".format(thick_z_minus))
        mc.setAttr("{0}.input2".format(thick_z_minus), -1.0)
        mc.connectAttr("{0}.output".format(thick_z_minus), "{0}.input1".format(thick_z_mult))
        mc.setAttr("{0}.input2".format(thick_z_mult), 0.25)
        mc.connectAttr("{0}.output".format(thick_z_mult), "{0}.input1".format(thick_z_add))
        mc.setAttr("{0}.input2".format(thick_z_add), 1.0)

        for jnt in ribbon.driven_joints:
            jnt.thickness_grp = jnt.add_group_above("{0}_thickness_grp".format(jnt.short_name))

            mc.connectAttr(thick_attr, jnt.thickness_grp.attr("scaleX"))
            mc.connectAttr("{0}.output".format(thick_z_add), jnt.thickness_grp.attr("scaleZ"))

        jnts_count = len(ribbon.driven_joints)
        is_even = jnts_count % 2 == 0

        if is_even:
            middle_jnts = [ribbon.driven_joints[int(jnts_count/2) - 1], ribbon.driven_joints[int(jnts_count/2)]]

        else:
            middle_jnts = [ribbon.driven_joints[int(jnts_count/2)]]

        for mid_jnt in middle_jnts:
            mc.connectAttr("{0}.outValue".format(remap), mid_jnt.offset_grp.attr("scaleX"))
            mc.connectAttr("{0}.outValue".format(remap), mid_jnt.offset_grp.attr("scaleZ"))

        remaining_half_count = int((jnts_count - len(middle_jnts)) / 2)
        fraction = 1.0 / (remaining_half_count + 1)
        value = fraction
        for index in range(remaining_half_count):

            mult = mc.createNode(MULT_DL, n="{0}_volume_{1}_mult".format(ribbon.name_prefix, index))
            mc.connectAttr("{0}.outValue".format(remap), "{0}.{1}".format(mult, MULT_DL_INPUT1))
            mc.setAttr("{0}.{1}".format(mult, MULT_DL_INPUT2), value)

            add = mc.createNode(ADD_DL, n="{0}_volume_{1}_add".format(ribbon.name_prefix, index))
            mc.connectAttr("{0}.output".format(mult), "{0}.input1".format(add))
            mc.setAttr("{0}.input2".format(add), abs(1.0 - value))
            value += fraction

            mc.connectAttr("{0}.output".format(add), ribbon.driven_joints[index].offset_grp.attr("scaleX"))
            mc.connectAttr("{0}.output".format(add), ribbon.driven_joints[index].offset_grp.attr("scaleZ"))

            index = jnts_count - 1 - index
            mc.connectAttr("{0}.output".format(add), ribbon.driven_joints[index].offset_grp.attr("scaleX"))
            mc.connectAttr("{0}.output".format(add), ribbon.driven_joints[index].offset_grp.attr("scaleZ"))

    def micro_setup(self, up_ribbon, low_ribbon, module_scale_attr):
        """Create the micro ctrls for each skinning joint setup.

        Args:
            up_ribbon (SimpleRibbon): upper lip ribbon object
            low_ribbon (SimpleRibbon): lower lip ribbon object
            module_scale_attr (str): long name of module scale attribute
        """
        micro_ctrls_grp = IoTransform("micro_ctrls_grp")
        micro_ctrls_grp.parent_relative(self.master_ctrl.pointer)

        micro_ctrls_grp.set_attr("inheritsTransform", 0)
        mc.connectAttr(module_scale_attr, micro_ctrls_grp.attr("scaleX"))
        mc.connectAttr(module_scale_attr, micro_ctrls_grp.attr("scaleY"))
        mc.connectAttr(module_scale_attr, micro_ctrls_grp.attr("scaleZ"))

        micro_attr = self.master_ctrl.pointer.add_attr("micro_ctrls", at="bool", dv=0, keyable=True)
        mc.connectAttr(micro_attr, micro_ctrls_grp.attr("visibility"))

        up_elements = [self.micro_up_ctrls, up_ribbon.jnts_locs, up_ribbon.driven_joints]
        low_elements = [self.micro_low_ctrls, low_ribbon.jnts_locs, low_ribbon.driven_joints]
        for elements in [up_elements, low_elements]:
            for ctrl, loc, jnt in zip(*elements):
                ctrl = ctrl.pointer
                ctrl.offset_grp.parent_relative(micro_ctrls_grp)

                mult_matrix = mc.listConnections("{0}.worldMatrix[0]".format(loc))[0]
                decomp_matrix = mc.listConnections("{0}.matrixSum".format(mult_matrix))[0]

                mc.connectAttr("{0}.outputRotate".format(decomp_matrix), ctrl.offset_grp.attr("rotate"))
                mc.connectAttr("{0}.outputTranslate".format(decomp_matrix), ctrl.offset_grp.attr("translate"))

                jnt.micro_grp = jnt.add_group_above("{0}_micro_driven_grp".format(jnt.short_name))
                jnt.micro_grp.direct_connect(ctrl)

    def corner_ctrls_curvature(self, data_grp):
        """When moving lips corner ctrls translateX, have it curve around the 'teeth'. """
        l_corner_ctrl = self.l_mouth_corner_ctrl.pointer
        r_corner_ctrl = self.r_mouth_corner_ctrl.pointer

        positions = [
            self.l_shape_a_guide.world_transformations["translate"],
            self.l_shape_b_guide.world_transformations["translate"],
            l_corner_ctrl.get_translation(),
            mid_point(
                self.l_low_minor_ctrl.pointer.get_translation(),
                self.l_up_minor_ctrl.pointer.get_translation(),
            ),
            mid_point(
                self.m_up_ctrl.pointer.get_translation(),
                self.m_low_ctrl.pointer.get_translation(),
            ),
            mid_point(
                self.r_low_minor_ctrl.pointer.get_translation(),
                self.r_up_minor_ctrl.pointer.get_translation(),
            ),
            r_corner_ctrl.get_translation(),
            self.r_shape_b_guide.world_transformations["translate"],
            self.r_shape_a_guide.world_transformations["translate"],
        ]

        for prefix, ctrl in [["L", l_corner_ctrl, ], ["R", r_corner_ctrl, ]]:
            shape_crv = mc.curve(
                degree=3,
                point=positions,
                knot=[0, 0, 0, 1, 2, 3, 4, 5, 6, 6, 6],
                worldSpace=True,
                name="{0}_{1}_mouth_curvature_curve".format(self.name, prefix),
            )
            shape_crv = IoTransform(shape_crv, existing=True)
            shape_crv.parent(ctrl.driver_grp)
            shape_crv.set_attr("visibility", 0)

            if prefix == "R":
                mc.reverseCurve(shape_crv, ch=False, replaceOriginal=True)

            ctrl.reverse_grp = ctrl.add_group_above("{0}_reverse_grp".format(ctrl.short_name))
            ctrl.pos_grp = ctrl.reverse_grp.add_group_above("{0}_pos_grp".format(ctrl.short_name))

            reverse_node = mc.createNode(MULT_DL, n="{0}_reverse_x_mult".format(ctrl.short_name))
            mc.connectAttr("{0}.translateX".format(ctrl), "{0}.{1}".format(reverse_node, MULT_DL_INPUT1))
            mc.setAttr("{0}.{1}".format(reverse_node, MULT_DL_INPUT2), -1.0)
            mc.connectAttr("{0}.output".format(reverse_node), "{0}.translateX".format(ctrl.reverse_grp))

            follow_grp = IoTransform("{0}_follow_crv_grp".format(ctrl.short_name), existing=False)
            follow_grp.parent_relative(ctrl.offset_grp)

            loc = IoTransform(mc.spaceLocator(n="{0}_follow_loc".format(ctrl.short_name))[0], existing=True)
            loc.set_attr("inheritsTransform", 0)
            loc.set_attr("visibility", 0)
            loc.parent_relative(data_grp)

            point_info = mc.createNode("pointOnCurveInfo", n="{0}_poci".format(shape_crv.short_name))
            crv_shape = shape_crv.get_shapes()[0]
            mc.connectAttr("{0}.worldSpace[0]".format(crv_shape), "{0}.inputCurve".format(point_info))
            mc.setAttr("{0}.turnOnPercentage".format(point_info), 1)
            mc.connectAttr("{0}.position".format(point_info), "{0}.translate".format(loc))

            divide_node = mc.createNode("multiplyDivide", n="{0}_normalize_divide".format(shape_crv.short_name))
            mc.connectAttr("{0}.translateX".format(ctrl), "{0}.input1X".format(divide_node))
            mc.setAttr("{0}.input2X".format(divide_node), mc.arclen(shape_crv) * -1.0)
            mc.setAttr("{0}.operation".format(divide_node), 2)  # divide operation.
            add_node = mc.createNode(ADD_DL, n="{0}_normalize_add".format(shape_crv.short_name))
            mc.setAttr("{0}.input2".format(add_node), 0.16666)
            mc.connectAttr("{0}.outputX".format(divide_node), "{0}.input1".format(add_node))
            mc.connectAttr("{0}.output".format(add_node), "{0}.parameter".format(point_info))

            mc.pointConstraint(loc, follow_grp, maintainOffset=False)
            ctrl.pos_grp.parent(follow_grp)
