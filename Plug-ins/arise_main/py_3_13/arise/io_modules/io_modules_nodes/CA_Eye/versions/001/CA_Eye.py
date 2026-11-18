"""CA_Eye module creates an eye and eyelids rig. """

from collections import OrderedDict

import maya.cmds as mc

from arise.data_types import node_data
from arise.utils.math_utils import distance_between, mid_point
from arise.utils.modules_utils import (
    create_grps, SECONDARY_COLOR, secondary_ctrls_setup, update_ctrls, ADD_DL, MULT_DL, MULT_DL_INPUT1,
    MULT_DL_INPUT2,
)
from arise.utils.matrix_utils import matrix_constraint
from arise.utils.io_nodes.io_transform import IoTransform

MAYA_VERSION = 2016  # the version of maya from which this module is supported.
AUTHOR = "Etay Herz"  # name of person who created this module.
RIG_CATEGORY = "Cartoon"  # either 'Basic', 'Cartoon', 'Vfx', 'Game' or 'All'. (used when filtering).
RIG_TYPE = "Biped"  # Biped, Car, Quadruped, All, ... (for filtering modules in lists).
TAGS = ["cartoon", "complex", "advance", "lids", "eyelids", "eyeball", "face", "pupil"]
TOOL_TIP = "Cartoon eye and eyelids."

node_data.NodeData.update_ctrls = update_ctrls


class CA_Eye(node_data.NodeData):
    """CA_Eye module creates an eye and eyelids rig. """
    sort_priority = 100

    def __init__(self, parent, docs, icon, module_dict):
        node_data.NodeData.__init__(
            self,
            parent=parent,
            icon=icon,
            docs=docs,
            module_dict=module_dict
        )

        self.body_part = "eye"

    def attributes_creation(self):
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
        self.add_separator()

        self.up_skin_jnts_attr = self.add_integer_attribute(
            name="Upper Lid Jnts",
            default_value=10,
            dynamic_attribute=False,
            writable=True,
            readable=True,
            promoted=False,
            annotation=(
                "Number of guides/skinning joints for the upper eyelid.\n"
                "Each edge loop should have a guide."
            ),
            min_value=7,
            max_value=40,
            add_slider=True,
        )
        self.low_skin_jnts_attr = self.add_integer_attribute(
            name="Lower Lid Jnts",
            default_value=10,
            dynamic_attribute=False,
            writable=True,
            readable=True,
            promoted=False,
            annotation=(
                "Number of guides/skinning joints for the lower eyelid.\n"
                "Each edge loop should have a guide."
            ),
            min_value=7,
            max_value=40,
            add_slider=True,
        )
        self.minor_ctrls_attr = self.add_integer_attribute(
            name="Minor Ctrls",
            default_value=5,
            dynamic_attribute=False,
            writable=True,
            readable=True,
            promoted=False,
            annotation="Number of Minor ctrls for EACH eyelid.",
            min_value=5,
            max_value=10,
            add_slider=True,
        )

        self.micro_ctrls_attr = self.add_boolean_attribute(
            name="Micro Ctrls",
            default_value=False,
            annotation="Add ctrls for every skinning jnt.",
        )

        ### connections.
        self.add_separator(title="Connections")
        self.driven_roots_attr = self.add_driven_attribute(name="Root Input", annotation="Input")
        self.driven_aim_attr = self.add_driven_attribute(name="Aim Ctrl Input", annotation="Input")
        self.driver_eyeball_attr = self.add_driver_attribute(name="Eyeball Output", annotation="Output")

        self.close_layout()

    def guides_creation(self):
        """Create guides based on attributes values. """
        self.eyeball_guide = self.add_guide(name="eyeball_center", translation=[8, 180, 5], rotation=[90, 0, 90])
        self.eyeball_guide.shape = "sphere_with_arrow"
        self.eyeball_guide.up_orient = "-X"

        self.eyes_aim_guide = self.add_guide(name="eye_aim_at", translation=[8, 180, 60])
        self.eyes_aim_guide.shape = "crystal"
        self.eyes_aim_guide.rotate_offset = [90, 0, 90]
        self.eyes_aim_guide.size = 2.5

        self.inner_corner_guide = self.add_guide(
            name="inner_corner",
            translation=[3, 180, 9],
            parent=self.eyeball_guide,
        )
        self.inner_corner_guide.shape = "triangle"
        self.inner_corner_guide.rotate_offset = [90, 0, 90]
        self.inner_corner_guide.size = 0.3
        self.inner_corner_guide.translate_offset = [0, 0, 0.4]

        self.outer_corner_guide = self.add_guide(
            name="outer_corner",
            translation=[14, 180, 9],
            parent=self.eyeball_guide,
        )
        self.outer_corner_guide.shape = "triangle"
        self.outer_corner_guide.rotate_offset = [-90, 0, 90]
        self.outer_corner_guide.size = 0.3
        self.outer_corner_guide.translate_offset = [0, 0, 0.4]

        self.up_guides = []
        for index in range(self.up_skin_jnts_attr.value):
            guide = self.add_guide(
                name="upper_{0}".format(str(index).zfill(2)),
                translation=[4 + index, 183, 10],
                parent=self.eyeball_guide,
            )

            guide.shape = "sphere"
            guide.size = 0.2

            if index != 0:
                guide.visual_parent = self.up_guides[-1]

            self.up_guides.append(guide)

        self.low_guides = []
        for index in range(self.low_skin_jnts_attr.value):
            guide = self.add_guide(
                name="lower_{0}".format(str(index).zfill(2)),
                translation=[4 + index, 177, 10],
                parent=self.eyeball_guide,
            )

            guide.shape = "sphere"
            guide.size = 0.2

            if index != 0:
                self.low_guides[-1].visual_parent = guide

            self.low_guides.append(guide)

        self.up_guides[0].visual_parent = self.inner_corner_guide
        self.low_guides[-1].visual_parent = self.outer_corner_guide
        self.inner_corner_guide.visual_parent = self.low_guides[0]
        self.outer_corner_guide.visual_parent = self.up_guides[-1]

    def joints_creation(self):
        """Create joints based on attributes values and guides. (without positioning as this point). """
        self.eye_jnt = self.add_joint(name="eyeball", skinning_jnt=True, tag_parent_jnt=None, radius=1)

        # driver joints.
        self.corner_in_jnt = self.add_joint(name="inner_corner_driver", skinning_jnt=False)
        self.corner_out_jnt = self.add_joint(name="outer_corner_driver", skinning_jnt=False)

        self.mid_up_jnt = self.add_joint(name="upper_mid_driver", skinning_jnt=False, tag_parent_jnt=self.eye_jnt)
        self.mid_low_jnt = self.add_joint(name="lower_mid_driver", skinning_jnt=False, tag_parent_jnt=self.eye_jnt)

        # driven joints.
        name = "inner_corner_driven"
        self.driven_in_jnt = self.add_joint(name=name, skinning_jnt=True, tag_parent_jnt=self.eye_jnt, radius=0.2)
        name = "outer_corner_driven"
        self.driven_out_jnt = self.add_joint(name=name, skinning_jnt=True, tag_parent_jnt=self.eye_jnt, radius=0.2)

        self.up_skin_jnts = []
        for index in range(self.up_skin_jnts_attr.value):
            name = "upper_driven_{0}".format(index)
            jnt = self.add_joint(name=name, skinning_jnt=True, tag_parent_jnt=self.eye_jnt, radius=0.12)
            self.up_skin_jnts.append(jnt)

        self.low_skin_jnts = []
        for index in range(self.low_skin_jnts_attr.value):
            name = "lower_driven_{0}".format(index)
            jnt = self.add_joint(name=name, skinning_jnt=True, tag_parent_jnt=self.eye_jnt, radius=0.12)
            self.low_skin_jnts.append(jnt)

    def ctrls_creation(self):
        """Create controls based on attributes values, guides and joints. (without positioning as this point). """
        scale_mult = self.ctrls_scale_attr.value #* 0.5

        self.eye_ctrl = self.add_ctrl(name="eyeball", shape="circle", up_orient="+Y", size=1.8 * scale_mult)
        self.eye_ctrl.translate_offset = [0, (5.0 * scale_mult), 0]

        self.eye_ctrl_secondary = self.add_ctrl(name="eyeball_secondary", size=(1.4 * scale_mult))
        self.eye_ctrl_secondary.translate_offset = [0, (5.0 * scale_mult), 0]
        self.eye_ctrl_secondary.color = SECONDARY_COLOR

        for attr in ["translateX", "translateY", "translateZ", "scaleX", "scaleY", "scaleZ"]:
            self.eye_ctrl_secondary.add_locked_hidden_attr(attr)

        self.aim_at_ctrl = self.add_ctrl(name="eye_aim_at", shape="crystal", size=5.0 * scale_mult)
        self.aim_at_ctrl.rotate_offset = [90, 0, 90]
        self.aim_at_ctrl.line_width = 2

        self.master_ctrl = self.add_ctrl(name="master", shape="circle_half")
        self.master_ctrl.translate_offset = [0, 7.5 * scale_mult, 8.5 * scale_mult]
        self.master_ctrl.rotate_offset = [90, 0, 0]
        self.master_ctrl.line_width = 2
        self.master_ctrl.size = [3.0 * scale_mult, 1.5 * scale_mult, 3.0 * scale_mult]

        self.in_ctrl = self.add_ctrl(name="inner_corner", shape="triangle")
        self.in_ctrl.size = [(0.5 * scale_mult), (0.3 * scale_mult), (0.3 * scale_mult)]
        self.in_ctrl.rotate_offset = [90, 0, 90]
        self.in_ctrl.translate_offset = [0, 0, (1.0 * scale_mult)]

        self.out_ctrl = self.add_ctrl(name="outer_corner", shape="triangle")
        self.out_ctrl.size = [0.5 * scale_mult, 0.3 * scale_mult, 0.3 * scale_mult]
        self.out_ctrl.rotate_offset = [-90, 0, 90]
        self.out_ctrl.translate_offset = [0, 0, (1.0 * scale_mult)]

        self.up_mid_ctrl = self.add_ctrl(name="upper_mid", shape="sphere", size=(0.5 * scale_mult))
        self.up_mid_ctrl.translate_offset = [0, 0, (1.0 * scale_mult)]
        self.low_mid_ctrl = self.add_ctrl(name="lower_mid", shape="sphere", size=(0.5 * scale_mult))
        self.low_mid_ctrl.translate_offset = [0, 0, (1.0 * scale_mult)]

        self.up_minor_ctrls = []
        for index in range(self.minor_ctrls_attr.value):
            ctrl_up = self.add_ctrl(name="upper_minor_{0}".format(index), up_orient="+Z", size=(0.3 * scale_mult))
            ctrl_up.translate_offset = [0, 0, (0.3 * scale_mult)]
            self.up_minor_ctrls.append(ctrl_up)

        self.low_minor_ctrls = []
        for index in range(self.minor_ctrls_attr.value):
            ctrl_low = self.add_ctrl(name="lower_minor_{0}".format(index), up_orient="+Z", size=(0.3 * scale_mult))
            ctrl_low.translate_offset = [0, 0, (0.3 * scale_mult)]
            self.low_minor_ctrls.append(ctrl_low)

            for attr in ["scaleX", "scaleY", "scaleZ"]:
                ctrl_up.add_locked_hidden_attr(attr)
                ctrl_low.add_locked_hidden_attr(attr)

        self.up_micro_ctrls, self.low_micro_ctrls, self.corner_micro_ctrls = [], [], []
        if self.micro_ctrls_attr.value:

            in_ctrl = self.add_ctrl(name="inner_corner_micro", shape="box", size=(0.2 * scale_mult))
            in_ctrl.translate_offset = [0, (0.2 * scale_mult), 0]
            in_ctrl.line_width = 2
            in_ctrl.color = SECONDARY_COLOR

            out_ctrl = self.add_ctrl(name="outer_corner_micro", shape="box", size=(0.2 * scale_mult))
            out_ctrl.translate_offset = [0, (0.2 * scale_mult), 0]
            out_ctrl.color = SECONDARY_COLOR
            out_ctrl.line_width = 2
            self.corner_micro_ctrls = [in_ctrl, out_ctrl]

            for index in range(self.up_skin_jnts_attr.value):
                name = "upper_micro_{0}".format(index)
                ctrl = self.add_ctrl(name=name, shape="box", size=(0.2 * scale_mult))
                ctrl.translate_offset = [0, (0.2 * scale_mult), 0]
                ctrl.color = SECONDARY_COLOR
                ctrl.line_width = 2
                self.up_micro_ctrls.append(ctrl)

            for index in range(self.low_skin_jnts_attr.value):
                name = "lower_micro_{0}".format(index)
                ctrl = self.add_ctrl(name=name, shape="box", size=(0.2 * scale_mult))
                ctrl.translate_offset = [0, (0.2 * scale_mult), 0]
                ctrl.color = SECONDARY_COLOR
                ctrl.line_width = 2
                self.low_micro_ctrls.append(ctrl)

    def maya_attrs_creation(self):
        """Declare any Maya attributes that users should be able to modify. """
        self.master_ctrl.add_maya_attr("minor_ctrls", attr_type="bool", default_value=True)

        if self.micro_ctrls_attr.value:
            self.master_ctrl.add_maya_attr("micro_ctrls", attr_type="bool", default_value=False)

        self.master_ctrl.add_maya_attr("blink_mid", attr_type="float", default_value=0.5, min=0, max=1)
        self.master_ctrl.add_maya_attr("lid_follow", attr_type="float", default_value=0, min=0, max=10)

    def rig_creation(self):
        """Using the attributes values, guides, joints, and ctrls, build the rig. """
        if self.is_mirrored:
            self.module_grp.set_attr("scaleX", -1)

        input_grp, input_aim_grp, output_grp = create_grps(self, ["input_grp", "input_aim_grp", "output_grp"])
        ctrls_grp, jnts_grp, lids_data_grp = create_grps(self, ["ctrls_grp", "jnts_grp", "lids_data_grp"])

        lids_data_grp.set_attr("inheritsTransform", 0)
        lids_data_grp.set_attr("visibility", 0)
        lids_data_grp.lock_and_hide_transformations(vis=False)

        self.driven_roots_attr.set_maya_object(input_grp)
        self.driven_aim_attr.set_maya_object(input_aim_grp)
        self.driver_eyeball_attr.set_maya_object(output_grp)

        blink_curve, blink_mid_pos, _, eye_center_aim_matrix = self.create_blink_curve(
            point_a=self.inner_corner_guide.world_transformations["translate"],
            point_b=self.outer_corner_guide.world_transformations["translate"],
            eye_center_pos=self.eyeball_guide.world_transformations["translate"],
        )

        ctrls_grp.set_matrix(eye_center_aim_matrix)
        ctrls_grp.set_scale([1, 1, 1])
        jnts_grp.set_matrix(eye_center_aim_matrix)
        jnts_grp.set_scale([1, 1, 1])

        eye_jnt = self.eye_jnt.pointer
        eye_ctrl = self.eye_ctrl.pointer
        eye_secondary_ctrl = self.eye_ctrl_secondary.pointer
        master_ctrl = self.master_ctrl.pointer
        aim_at_ctrl = self.aim_at_ctrl.pointer
        in_ctrl = self.in_ctrl.pointer
        out_ctrl = self.out_ctrl.pointer
        corner_in_jnt = self.corner_in_jnt.pointer
        corner_out_jnt = self.corner_out_jnt.pointer

        eye_jnt.parent_relative(jnts_grp)
        eye_jnt.set_matrix(self.eyeball_guide.world_transformations["matrix"], space="world")
        eye_jnt.freeze_transformations()
        eye_jnt.add_joint_orient()

        master_ctrl.offset_grp.parent_relative(ctrls_grp)
        matrix_constraint(master_ctrl, jnts_grp, maintain_offset=True)

        master_ctrl.add_spacer_attr()
        minor_vis_attr = master_ctrl.add_attr("minor_ctrls", at="bool", k=True, dv=1)

        if self.micro_ctrls_attr.value:  # created here to be next to minor_ctrls attr.
            micro_ctrls_attr = master_ctrl.add_attr("micro_ctrls", at="bool", k=True, dv=0)

        master_decom_node = mc.createNode("decomposeMatrix", n="{0}_decomp".format(master_ctrl.short_name))
        mc.connectAttr("{0}.worldMatrix[0]".format(master_ctrl), "{0}.inputMatrix".format(master_decom_node))

        # setup aim_at_ctrl.
        name = "{0}_driven_grp".format(aim_at_ctrl.short_name)
        aim_at_ctrl.driven_grp = aim_at_ctrl.offset_grp.add_group_above(name)
        aim_at_ctrl.driven_grp.set_matrix(self.eyes_aim_guide.world_transformations["matrix"], space="world")
        aim_at_ctrl.driven_grp.set_scale([1, 1, 1])
        aim_at_ctrl.driven_grp.parent(ctrls_grp)

        # eyeball ctrl setup.
        secondary_ctrls_setup([eye_ctrl], [eye_secondary_ctrl])

        name = "{0}_reverse_grp".format(eye_ctrl.short_name)
        eye_ctrl.reverse_grp = eye_ctrl.offset_grp.add_group_above(name)
        name = "{0}_orient_grp".format(eye_ctrl.short_name)
        eye_ctrl.orient_grp = eye_ctrl.reverse_grp.add_group_above(name)
        eye_ctrl.orient_grp.match_transformation_to(eye_jnt)

        aim_grp = IoTransform("{0}_aim_grp".format(eye_ctrl.short_name), existing=False)
        aim_grp.offset_grp = aim_grp.add_group_above("{0}_aim_offset_grp".format(eye_ctrl.short_name))
        aim_grp.offset_grp.parent_relative(master_ctrl)

        eye_loc = IoTransform(
            mc.spaceLocator(n="{0}_eyeball_aim_up_vector_loc".format(self.name))[0],
            existing=True,
        )
        eye_loc.grp = eye_loc.add_group_above("{0}_eyeball_aim_up_vector_move_grp".format(self.name))
        eye_loc.pos_grp = eye_loc.grp.add_group_above("{0}_eyeball_aim_up_vector_pos_grp".format(self.name))
        eye_loc.pos_grp.parent_relative(master_ctrl)
        eye_loc.pos_grp.parent(ctrls_grp)
        eye_loc.set_attr("translateX", 50)
        eye_loc.set_attr("visibility", 0)

        aim_grp.aim_constraint_to(
            aim_at_ctrl,
            aimVector=(0, 1, 0),
            upVector=(1, 0, 0),
            worldUpType="object",
            worldUpObject=eye_loc,
            maintainOffset=False,
        )

        eye_ctrl.orient_grp.parent(aim_grp)
        mult_node = mc.createNode("multiplyDivide", n="{0}_reverse_trans".format(eye_ctrl.short_name))
        mc.setAttr("{0}.operation".format(mult_node), 1)  # multiply.
        for axis in "XYZ":
            mc.connectAttr("{0}.translate{1}".format(eye_ctrl, axis), "{0}.input1{1}".format(mult_node, axis))
            mc.setAttr("{0}.input2{1}".format(mult_node, axis), -1.0)
            mc.connectAttr(
                "{0}.output{1}".format(mult_node, axis),
                "{0}.translate{1}".format(eye_ctrl.reverse_grp, axis),
            )
            mc.connectAttr("{0}.translate{1}".format(eye_ctrl, axis), "{0}.translate{1}".format(aim_grp, axis))
            mc.connectAttr("{0}.translate{1}".format(eye_ctrl, axis), "{0}.translate{1}".format(eye_loc.grp, axis))

        matrix_constraint(eye_ctrl.btm_ctrl, eye_jnt, maintain_offset=False)

        # setup corner ctrls.
        in_ctrl.offset_grp.parent_relative(master_ctrl)
        in_ctrl.offset_grp.set_matrix(self.inner_corner_guide.world_transformations["matrix"], space="world")
        in_ctrl.offset_grp.set_attr("scale", [1, 1, 1])
        out_ctrl.offset_grp.parent_relative(master_ctrl)
        out_ctrl.offset_grp.set_matrix(self.outer_corner_guide.world_transformations["matrix"], space="world")
        out_ctrl.offset_grp.set_attr("scale", [1, 1, 1])

        corner_in_jnt.parent_relative(jnts_grp)
        matrix_constraint(in_ctrl, corner_in_jnt, maintain_offset=False)
        corner_in_jnt.set_attr("visibility", 0)

        corner_out_jnt.parent_relative(jnts_grp)
        matrix_constraint(out_ctrl, corner_out_jnt, maintain_offset=False)
        corner_out_jnt.set_attr("visibility", 0)

        master_ctrl.add_spacer_attr()
        blink_attr = master_ctrl.add_attr("blink", dv=0, min=0, max=1, keyable=True)
        blink_mid_attr = master_ctrl.add_attr("blink_mid", dv=0.5, min=0, max=1, keyable=True)

        # fleshy eyelids setup.
        mid_ctrls_grp = IoTransform("{0}_mid_ctrls_fleshy_eye_grp".format(self.name), existing=False)
        mid_ctrls_grp.set_attr("rotateOrder", 1)  # YZX since we will not orient constraint rotateY.
        mid_ctrls_grp.parent_relative(master_ctrl)

        fleshy_driver_grp = IoTransform("{0}_fleshy_eye_driver_grp".format(self.name), existing=False)
        fleshy_driver_grp.parent_relative(eye_jnt)
        fleshy_driver_grp.match_transformation_to(master_ctrl)

        ori_constraint = mid_ctrls_grp.orient_constraint_to([master_ctrl, fleshy_driver_grp], skip="y")
        mc.setAttr("{0}.interpType".format(ori_constraint), 2)  # shortest (avoids flipping).

        master_ctrl.add_spacer_attr()
        lid_follow_attr = master_ctrl.add_attr("lid_follow", dv=0, min=0, max=10, keyable=True)
        remap_node = mc.createNode("remapValue", n="{0}_fleshy_eyelids_remap".format(self.name))
        mc.connectAttr(lid_follow_attr, "{0}.inputValue".format(remap_node))
        mc.setAttr("{0}.inputMin".format(remap_node), 0)
        mc.setAttr("{0}.inputMax".format(remap_node), 10)
        mc.setAttr("{0}.outputMin".format(remap_node), 0)
        mc.setAttr("{0}.outputMax".format(remap_node), 1)

        fleshy_alias = mc.orientConstraint(ori_constraint, q=True, weightAliasList=True)[1]
        mc.connectAttr("{0}.outValue".format(remap_node), "{0}.{1}".format(ori_constraint, fleshy_alias))

        # mid ctrls setup.
        up_mid_ctrl = self.up_mid_ctrl.pointer
        up_mid_ctrl.offset_grp.parent_relative(mid_ctrls_grp)
        up_mid_ctrl.jnt = self.mid_up_jnt.pointer
        up_mid_ctrl.jnt.parent_relative(jnts_grp)
        matrix_constraint(up_mid_ctrl, up_mid_ctrl.jnt, maintain_offset=False)
        up_mid_ctrl.jnt.set_attr("visibility", 0)

        low_mid_ctrl = self.low_mid_ctrl.pointer
        low_mid_ctrl.offset_grp.parent_relative(mid_ctrls_grp)
        low_mid_ctrl.jnt = self.mid_low_jnt.pointer
        low_mid_ctrl.jnt.parent_relative(jnts_grp)
        matrix_constraint(low_mid_ctrl, low_mid_ctrl.jnt, maintain_offset=False)
        low_mid_ctrl.jnt.set_attr("visibility", 0)

        # eyeLids:
        lids_loc = IoTransform(mc.spaceLocator(n="{0}_lids_up_vector_loc".format(self.name))[0], existing=True)
        lids_loc.set_visibility(False)
        lids_loc.parent_relative(jnts_grp)
        lids_loc.set_attr("translateX", 50)

        upper_items = [self.up_guides, "upper", up_mid_ctrl, self.up_minor_ctrls, self.up_skin_jnts]
        low_items = [self.low_guides, "lower", low_mid_ctrl, self.low_minor_ctrls, self.low_skin_jnts]
        for lid_guides, prefix, mid_ctrl, minor_ctrls, skin_jnts in [upper_items, low_items]:
            minor_ctrls = [minor_ctrl.pointer for minor_ctrl in minor_ctrls]

            # create 3 curves.
            positions = []
            for guide in [self.inner_corner_guide] + lid_guides + [self.outer_corner_guide]:
                positions.append(guide.world_transformations["translate"])

            linear_crv = mc.curve(
                name="{0}_{1}_linear_curve".format(self.name, prefix),
                degree=1,
                point=positions,
                knot=range(len(positions)),
                worldSpace=True,
            )
            mc.parent(linear_crv, lids_data_grp)

            mid_curve_a = mc.duplicate(linear_crv, name="{0}_{1}_mid_a_curve".format(self.name, prefix))[0]
            mc.rebuildCurve(
                mid_curve_a,
                degree=3,
                endKnots=0,  # uniform end knots.
                constructionHistory=False,
                replaceOriginal=True,
                rebuildType=0,  # uniform.
                keepRange=2,  # 0 to number of spans.
                keepControlPoints=False,
                keepEndPoints=True,
                keepTangents=False,
                spans=len(minor_ctrls) - 1,
            )

            mid_curve_b = mc.duplicate(mid_curve_a, name="{0}_{1}_mid_b_curve".format(self.name, prefix))[0]

            # create distance dict that will help to skinning the curve.
            near_node = mc.createNode("nearestPointOnCurve")
            mc.connectAttr("{0}.worldSpace[0]".format(blink_curve), "{0}.inputCurve".format(near_node))

            far_point = 0.0
            distance_dict = OrderedDict()  # dict of distances each cv from closed eyelid.
            for curve_cv in mc.ls("{0}.cv[:]".format(mid_curve_a), flatten=True)[1:-1]:
                cv_pos = mc.xform(curve_cv, q=True, ws=True, translation=True)
                mc.setAttr("{0}.inPosition".format(near_node), *cv_pos, type="double3")
                nearest_point = mc.getAttr("{0}.position".format(near_node))[0]
                distance = distance_between(cv_pos, nearest_point)
                distance_dict[curve_cv] = distance_between(cv_pos, nearest_point)

                if distance >= far_point:
                    far_point = distance

            # position and orient mid ctrl.
            temp_on_curve_node = mc.createNode("pointOnCurveInfo")
            mc.connectAttr("{0}.worldSpace[0]".format(mid_curve_a), "{0}.inputCurve".format(temp_on_curve_node))
            mc.setAttr("{0}.turnOnPercentage".format(temp_on_curve_node), 1)
            mc.setAttr("{0}.parameter".format(temp_on_curve_node), 0.5)
            mid_ctrl.pos_grp = mid_ctrl.offset_grp.add_group_above("{0}_pos_grp".format(mid_ctrl.short_name))
            mid_ctrl.pos_grp.set_translation(mc.getAttr("{0}.position".format(temp_on_curve_node))[0])
            mc.delete(temp_on_curve_node)

            temp_loc = mc.spaceLocator()[0]
            mc.xform(temp_loc, ws=True, translation=blink_mid_pos)
            constraint = mid_ctrl.pos_grp.aim_constraint_to(
                temp_loc,
                aimVector=(0, -1, 0)if mid_ctrl is self.up_mid_ctrl.pointer else (0, 1, 0),
                upVector=(0, 0, -1),
                worldUpType="object",
                worldUpObject=eye_jnt,
                maintainOffset=False,
            )
            mc.delete(constraint, temp_loc)

            skin_cluster = mc.skinCluster(
                [corner_in_jnt, mid_ctrl.jnt, corner_out_jnt],
                mid_curve_a,
                name="{0}_skin_cluster".format(mid_curve_a),
                skinMethod=0,  # classic linear.
            )[0]

            # fix skinning weights of curve.
            corner_in_pos = corner_in_jnt.get_translation()
            corner_out_pos = corner_out_jnt.get_translation()
            mc.setAttr("{0}.normalizeWeights".format(skin_cluster), 0)
            for curve_cv, distance in distance_dict.items():
                cv_pos = mc.xform(curve_cv, q=True, ws=True, translation=True)

                nearest_corner_jnt = corner_in_jnt
                if distance_between(corner_in_pos, cv_pos) > distance_between(corner_out_pos, cv_pos):
                    nearest_corner_jnt = corner_out_jnt

                value = distance / far_point
                mc.skinPercent(skin_cluster, curve_cv, normalize=False, pruneWeights=100)
                mc.skinPercent(
                    skin_cluster,
                    curve_cv,
                    transformValue=[(mid_ctrl.jnt, value), (nearest_corner_jnt, 1.0 - value)],
                )

            mc.setAttr("{0}.normalizeWeights".format(skin_cluster), 1)

            # have curve_a drive minor ctrl.
            info_node = mc.createNode("curveInfo", n="{0}_{1}_curveInfo".format(self.name, mid_curve_a))
            mc.connectAttr("{0}.worldSpace[0]".format(mid_curve_a), "{0}.inputCurve".format(info_node))

            follow_grps_grp = IoTransform("{0}_{1}_follow_grps".format(self.name, prefix), existing=False)
            follow_grps_grp.parent_relative(ctrls_grp)
            follow_grps_grp.set_attr("inheritsTransform", 0)
            follow_grps_grp.connect_attr("visibility", minor_vis_attr)
            follow_grps_grp.lock_and_hide_transformations()

            previous_ctrl = in_ctrl
            for index, minor_ctrl in enumerate(minor_ctrls):
                name = "{0}_orient_offset_grp".format(minor_ctrl.short_name)
                minor_ctrl.ori_offset_grp = minor_ctrl.offset_grp.add_group_above(name)
                name = "{0}_follow_grp".format(minor_ctrl.short_name)
                minor_ctrl.follow_grp = minor_ctrl.ori_offset_grp.add_group_above(name)
                minor_ctrl.follow_grp.parent_relative(follow_grps_grp)

                mc.connectAttr(
                    "{0}.controlPoints[{1}]".format(info_node, index+1),
                    "{0}.translate".format(minor_ctrl.follow_grp),
                )

                # orient minor ctrls.
                constraint = minor_ctrl.follow_grp.aim_constraint_to(
                    eye_jnt,
                    aimVector=(0, 0, -1),
                    upVector=(-1, 0, 0),
                    worldUpType="object",
                    worldUpObject=previous_ctrl,
                    maintainOffset=False,
                )
                mc.delete(constraint)
                previous_ctrl = minor_ctrl

                matrix_constraint(
                    master_ctrl,
                    minor_ctrl.follow_grp,
                    maintain_offset=True,
                    skip_attrs=(True, True, True, False, False, False, False, False, False),
                )

            # connect minor ctrls to drive curve_b.
            for index, driver in enumerate([corner_in_jnt] + minor_ctrls + [corner_out_jnt]):
                decom_node = mc.createNode("decomposeMatrix", n="{0}_decom_node".format(driver.short_name))
                mc.connectAttr("{0}.worldMatrix[0]".format(driver), "{0}.inputMatrix".format(decom_node))
                mc.connectAttr(
                    "{0}.outputTranslate".format(decom_node),
                    "{0}.controlPoints[{1}]".format(mid_curve_b, index),
                )

            # create wire that curve_b drives linear_crv.
            wire_node, _ = mc.wire(
                linear_crv,
                wire=mid_curve_b,
                groupWithBase=False,
                crossingEffect=0,
                localInfluence=0,
                name="{0}_wire".format(linear_crv),
            )
            mc.setAttr("{0}.dropoffDistance[0]".format(wire_node), 9999)

            # setup eye blink amount drives wire scale[0].
            name = "{0}_{1}_blink_aim".format(self.name, prefix)
            aim_center_grp = IoTransform("{0}_offset_grp".format(name), existing=False)
            aim_loc = IoTransform(mc.spaceLocator(n="{0}_loc".format(name))[0], existing=True)
            aim_center_grp.parent_relative(master_ctrl)
            aim_center_grp.set_attr("visibility", 0)
            aim_loc.parent_relative(aim_center_grp)
            aim_loc.set_attr("rotateOrder", 1)  # YZX.

            aim_loc.aim_constraint_to(
                mid_ctrl,
                aimVector=(0, 1, 0),
                upVector=(1, 0, 0),
                worldUpType="objectrotation",
                worldUpVector=(1, 0, 0),
                worldUpObject=aim_center_grp,
                maintainOffset=False,
            )

            remap_node = mc.createNode("remapValue", n="{0}_remapValue".format(name))
            mult_node = mc.createNode(MULT_DL, n="{0}_multDoubleLinear".format(name))

            mc.connectAttr(aim_loc.attr("rotateY"), "{0}.inputValue".format(remap_node))
            mc.setAttr("{0}.inputMin".format(remap_node), 0)
            mc.setAttr("{0}.inputMax".format(remap_node), mc.getAttr(aim_loc.attr("rotateY")))
            mc.setAttr("{0}.outputMin".format(remap_node), 0)
            mc.setAttr("{0}.outputMax".format(remap_node), 1)
            mc.connectAttr("{0}.outValue".format(remap_node), "{0}.{1}".format(mult_node, MULT_DL_INPUT2))
            mc.connectAttr("{0}.outputScaleX".format(master_decom_node), "{0}.{1}".format(mult_node, MULT_DL_INPUT1))
            mc.connectAttr("{0}.output".format(mult_node), "{0}.scale[0]".format(wire_node))

            # connect skinning joints to aim at grps on linear_curve.
            mid_ctrl.add_spacer_attr()
            bulge_attr = mid_ctrl.add_attr("bulge", dv=0, min=0, keyable=True)
            depth_attr = mid_ctrl.add_attr("depth", dv=0, min=0, keyable=True)

            info_node = mc.createNode("curveInfo", n="{0}_{1}_curveInfo".format(self.name, linear_crv))
            mc.connectAttr("{0}.worldSpace[0]".format(linear_crv), "{0}.inputCurve".format(info_node))

            attach_grps_grp = IoTransform("{0}_{1}_attach_grps".format(self.name, prefix), existing=False)
            attach_grps_grp.parent_relative(lids_data_grp)

            jnts_grps_grp = IoTransform("{0}_{1}_driven_jnts_grps".format(self.name, prefix), existing=False)
            jnts_grps_grp.parent_relative(jnts_grp)

            for index, (skin_jnt, guide) in enumerate(zip(skin_jnts, lid_guides)):
                offset_grp, attach_grp = self.setup_aim_joint(
                    skin_jnt=skin_jnt,
                    guide=guide,
                    cv_index=index+1,
                    info_node=info_node,
                    lids_loc=lids_loc,
                    near_node=near_node,
                )
                offset_grp.parent(jnts_grps_grp)
                offset_grp.zero_local_transformations()
                attach_grp.parent_relative(attach_grps_grp)

                skin_jnt = skin_jnt.pointer
                skin_pos = mc.xform(skin_jnt, q=True, ws=True, translation=True)
                dist = min(distance_between(corner_in_pos, skin_pos), distance_between(corner_out_pos, skin_pos))
                value = dist / (dist + distance_between(mid_ctrl.get_translation(), skin_pos))

                depth_mult = mc.createNode(MULT_DL, n="{0}_depth_mult".format(skin_jnt.short_name))
                mc.connectAttr(depth_attr, "{0}.{1}".format(depth_mult, MULT_DL_INPUT1))
                mc.setAttr("{0}.{1}".format(depth_mult, MULT_DL_INPUT2), min(value * 1.2, 1)) # more exponential the linear.
                mc.connectAttr("{0}.output".format(depth_mult), skin_jnt.attr("translateY"))

                bulge_mult = mc.createNode(MULT_DL, n="{0}_bulge_mult".format(skin_jnt.short_name))
                mc.connectAttr(bulge_attr, "{0}.{1}".format(bulge_mult, MULT_DL_INPUT1))
                mc.setAttr("{0}.{1}".format(bulge_mult, MULT_DL_INPUT2), min(value * 1.2, 1))  # more exponential the linear.

                add_node = mc.createNode(ADD_DL, n="{0}_bulge_add".format(skin_jnt.short_name))
                mc.connectAttr("{0}.output".format(bulge_mult), "{0}.input1".format(add_node))
                mc.setAttr("{0}.input2".format(add_node), 1)
                mc.connectAttr("{0}.output".format(add_node), skin_jnt.attr("scaleY"))


        # connect corner skinning joints.
        inner_corner_objs = [self.driven_in_jnt, self.inner_corner_guide, 0]
        outer_corner_objs = [self.driven_out_jnt, self.outer_corner_guide, index+2]
        for skin_jnt, guide, index in [inner_corner_objs, outer_corner_objs]:

            offset_grp, attach_grp = self.setup_aim_joint(
                skin_jnt,
                guide=guide,
                cv_index=index,
                info_node=info_node,
                lids_loc=lids_loc,
                near_node=near_node,
            )
            offset_grp.parent(jnts_grps_grp)
            offset_grp.zero_local_transformations()
            attach_grp.parent_relative(attach_grps_grp)

        # create blink setup.
        mid_curve_positions = [
            self.up_mid_ctrl.pointer.get_translation(),
            mc.xform("{0}.cv[1]".format(blink_curve), q=True, ws=True, translation=True),
            self.low_mid_ctrl.pointer.get_translation(),
        ]

        mid_ctrls_curve = mc.curve(
            name="{0}_blink_mid_ctrls_curve".format(self.name),
            degree=2,
            point=mid_curve_positions,
            knot=[0, 0, 1, 1],
            worldSpace=True,
        )
        mc.parent(mid_ctrls_curve, master_ctrl)
        mc.makeIdentity(mid_ctrls_curve, apply=True, translate=True, rotate=True, scale=True, preserveNormals=True)
        mc.setAttr("{0}.visibility".format(mid_ctrls_curve), 0)

        remap_node = mc.createNode("remapValue", n="{0}_blink_remapValue".format(self.name))
        mc.setAttr("{0}.inputMin".format(remap_node), 0)
        mc.setAttr("{0}.inputMax".format(remap_node), 1)
        mc.setAttr("{0}.outputMin".format(remap_node), 0.15)
        mc.setAttr("{0}.outputMax".format(remap_node), 0.85)
        mc.connectAttr(blink_mid_attr, "{0}.inputValue".format(remap_node))

        # upper blink.
        up_point_node = mc.createNode("pointOnCurveInfo", n="{0}_blink_up_pointOnCurveInfo".format(self.name))
        mc.connectAttr("{0}.local".format(mid_ctrls_curve), "{0}.inputCurve".format(up_point_node))

        up_mult_a_node = mc.createNode(MULT_DL, n="{0}_blink_up_A_multDoubleLinear".format(self.name))
        mc.connectAttr(blink_attr, "{0}.{1}".format(up_mult_a_node, MULT_DL_INPUT1))
        mc.connectAttr("{0}.outValue".format(remap_node), "{0}.{1}".format(up_mult_a_node, MULT_DL_INPUT2))

        up_mult_b_node = mc.createNode(MULT_DL, n="{0}_blink_up_B_multDoubleLinear".format(self.name))
        mc.connectAttr("{0}.output".format(up_mult_a_node), "{0}.{1}".format(up_mult_b_node, MULT_DL_INPUT1))
        mc.setAttr("{0}.{1}".format(up_mult_b_node, MULT_DL_INPUT2), 1.135) # TODO: does this value works for all eyes?
        mc.connectAttr("{0}.output".format(up_mult_b_node), "{0}.parameter".format(up_point_node))

        mc.connectAttr("{0}.position".format(up_point_node), up_mid_ctrl.pos_grp.attr("translate"))

        # lower blink.
        low_point_node = mc.createNode("pointOnCurveInfo", n="{0}_blink_low_pointOnCurveInfo".format(self.name))
        mc.connectAttr("{0}.local".format(mid_ctrls_curve), "{0}.inputCurve".format(low_point_node))

        reverse_a_node = mc.createNode("reverse", n="{0}_low_A_blink_reverse".format(self.name))
        mc.connectAttr("{0}.outValue".format(remap_node), "{0}.inputX".format(reverse_a_node))

        low_mult_a_node = mc.createNode(MULT_DL, n="{0}_blink_low_A_multDoubleLinear".format(self.name))
        mc.connectAttr(blink_attr, "{0}.{1}".format(low_mult_a_node, MULT_DL_INPUT1))
        mc.connectAttr("{0}.outputX".format(reverse_a_node), "{0}.{1}".format(low_mult_a_node, MULT_DL_INPUT2))

        low_mult_b_node = mc.createNode(MULT_DL, n="{0}_blink_low_B_multDoubleLinear".format(self.name))
        mc.connectAttr("{0}.output".format(low_mult_a_node), "{0}.{1}".format(low_mult_b_node, MULT_DL_INPUT1))
        mc.setAttr("{0}.{1}".format(low_mult_b_node, MULT_DL_INPUT2), 1.135)  # TODO: does this value works for all eyes?

        reverse_b_node = mc.createNode("reverse", n="{0}_low_B_blink_reverse".format(self.name))
        mc.connectAttr("{0}.output".format(low_mult_b_node), "{0}.inputX".format(reverse_b_node))
        mc.connectAttr("{0}.outputX".format(reverse_b_node), "{0}.parameter".format(low_point_node))

        mc.connectAttr("{0}.position".format(low_point_node), low_mid_ctrl.pos_grp.attr("translate"))

        # setup micro ctrls if enabled.
        if self.micro_ctrls_attr.value:
            # micro_ctrls_attr = master_ctrl.add_attr("micro_ctrls", at="bool", k=True, dv=0)
            micro_grp = IoTransform("{0}_micro_ctrls_grp".format(self.name), existing=False)
            micro_grp.parent_relative(master_ctrl)
            micro_grp.connect_attr("visibility", micro_ctrls_attr)
            micro_grp.lock_and_hide_transformations()

            ctrls_list = self.up_micro_ctrls + self.low_micro_ctrls + self.corner_micro_ctrls
            jnts_list = self.up_skin_jnts + self.low_skin_jnts + [self.driven_in_jnt, self.driven_out_jnt]
            for ctrl, jnt in zip(ctrls_list, jnts_list):
                self.setup_micro_ctrl(ctrl=ctrl, joint=jnt, parent_grp=micro_grp)

        #finalize.
        mc.delete(blink_curve, near_node)

        input_grp.match_transformation_to(ctrls_grp)
        matrix_constraint(input_grp, ctrls_grp, maintain_offset=True)
        input_aim_grp.match_transformation_to(aim_at_ctrl.driven_grp)
        matrix_constraint(input_aim_grp, aim_at_ctrl.driven_grp, maintain_offset=True)
        matrix_constraint(eye_jnt, output_grp, maintain_offset=False)

    def create_blink_curve(self, point_a, point_b, eye_center_pos):
        """Return a 3 CVs curve that represents the blink middle line, also returns middle point.

        Args:
            point_a (list): of XYZ position in cartesian space
            point_b (list): of XYZ position in cartesian space
            eye_center_pos (list): of XYZ position in cartesian space

        Returns:
            list: name of curve, XYZ mid blink pos, matrix mid blink, eye center oriented to blink center
        """
        mid_pos = mid_point(point_a, point_b)
        radius = distance_between(eye_center_pos, point_a)

        temp_loc_a = IoTransform(mc.spaceLocator(n="{0}_temp_a_loc".format(self.name))[0], existing=True)
        temp_loc_a.parent(self.module_grp)
        temp_loc_a.set_translation(eye_center_pos)

        temp_loc_b = IoTransform(mc.spaceLocator(n="{0}_temp_b_loc".format(self.name))[0], existing=True)
        temp_loc_b.parent(self.module_grp)
        temp_loc_b.set_translation(mid_pos)

        temp_loc_c = IoTransform(mc.spaceLocator(n="{0}_temp_c_loc".format(self.name))[0], existing=True)
        temp_loc_c.parent(self.module_grp)
        temp_loc_c.set_translation(point_b)

        mc.delete(
            temp_loc_a.aim_constraint_to(
                temp_loc_b,
                aimVector=(0, 1, 0),
                upVector=(0, 0, 1),
                worldUpType="object",
                worldUpObject=temp_loc_c,
                maintainOffset=False,
            )
        )
        temp_loc_b.reset_transformations()
        temp_loc_b.parent_relative(temp_loc_a)
        eye_center_aim_matrix = temp_loc_b.get_matrix()
        temp_loc_b.set_attr("translateY", radius)
        mid_pos = temp_loc_b.get_translation()
        mid_matrix = temp_loc_b.get_matrix()
        temp_loc_b.set_attr("translateY", radius * 1.333) # since curve doesn't match CV position because degree 2.
        curve_mid_pos = temp_loc_b.get_translation()
        mc.delete(temp_loc_a, temp_loc_b, temp_loc_c)

        blink_curve = mc.curve(
            name="{0}_line_curve".format(self.name),
            degree=2,
            point=[point_a, curve_mid_pos, point_b],
            knot=[0, 0, 1, 1],
            worldSpace=True,
        )

        return [blink_curve, mid_pos, mid_matrix, eye_center_aim_matrix]

    def setup_aim_joint(self, skin_jnt, guide, cv_index, info_node, lids_loc, near_node):
        """Have joint aim at a group that is attached to info node.

        Args:
            skin_jnt (IoJoint): The joint that will move along a radius
            guide (IoGuide): Guide with position for joint
            cv_index (int): the curve cv index the joint need to aim follow
            info_node (str): the name of a curveInfo node connected to curve
            lids_loc (IoTransform or str): up vector object
            near_node (str): nearestPointOnCurve node connected to blink_line_curve

        Returns:
            list: of 2 groups
        """
        skin_jnt = skin_jnt.pointer
        skin_jnt.aim_grp = IoTransform("{0}_aim_grp".format(skin_jnt.short_name), existing=False)
        skin_jnt.offset_grp = skin_jnt.aim_grp.add_group_above("{0}_offset_grp".format(skin_jnt.short_name))
        skin_jnt.offset_grp.match_transformation_to(self.master_ctrl.pointer)

        attach_grp = IoTransform("{0}_attach_grp".format(skin_jnt.short_name), existing=False)
        mc.connectAttr(
            "{0}.controlPoints[{1}]".format(info_node, cv_index),
            "{0}.translate".format(attach_grp),
        )

        skin_jnt.aim_grp.aim_constraint_to(
            attach_grp,
            aimVector=(0, 1, 0),
            upVector=(1, 0, 0),
            worldUpType="object",
            worldUpObject=lids_loc,
            maintainOffset=False,
        )

        skin_jnt.pos_grp = skin_jnt.add_group_above("{0}_pos_offset_grp".format(skin_jnt.short_name))
        skin_jnt.driven_grp = skin_jnt.add_group_above("{0}_driven_grp".format(skin_jnt.short_name))
        skin_jnt.pos_grp.set_translation(guide.world_transformations["translate"], space="world")
        skin_jnt.pos_grp.parent(skin_jnt.aim_grp)
        skin_jnt.pos_grp.set_attr("rotate", [0, 0, 0])

        # orient jnts, used by micro ctrls.
        mc.setAttr("{0}.inPosition".format(near_node), *guide.world_transformations["translate"], type="double3")
        temp_loc = IoTransform(mc.spaceLocator(n="{0}_temp_jnt_loc".format(self.name))[0], existing=True)
        temp_loc.set_translation(mc.getAttr("{0}.position".format(near_node))[0])
        temp_constraint = skin_jnt.pos_grp.aim_constraint_to(
            temp_loc,
            aimVector=(-1, 0, 0),
            upVector=(0, 1, 0),
            worldUpType="none",
            skip=["x", "z"],
            maintainOffset=False,
        )
        mc.delete(temp_constraint, temp_loc)

        skin_jnt.zero_joint_orient()

        return [skin_jnt.offset_grp, attach_grp]

    @staticmethod
    def setup_micro_ctrl(ctrl, joint, parent_grp):
        """Connect micro ctrl to drive a joint.

        Args:
            ctrl (IoCtrl): ctrl to drive joint
            joint (IoJoint): driven joint
            parent_grp (str or IoTransform): the parent of ctrl grps
        """
        ctrl, jnt = ctrl.pointer, joint.pointer
        ctrl.orient_grp = ctrl.offset_grp.add_group_above("{0}_orient_grp".format(ctrl.short_name))
        ctrl.orient_grp.parent_relative(parent_grp)
        ctrl.orient_grp.direct_connect(jnt.aim_grp, translate=False, rotate=True, scale=False)
        ctrl.orient_grp.lock_and_hide_transformations()
        ctrl.offset_grp.set_attr("translateY", jnt.pos_grp.get_attr("translateY"))
        ctrl.offset_grp.set_attr("rotateY", jnt.pos_grp.get_attr("rotateY"))
        ctrl.offset_grp.lock_and_hide_transformations()
        jnt.driven_grp.direct_connect(ctrl, translate=True, rotate=True, scale=True)
