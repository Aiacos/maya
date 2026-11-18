"""The Path node enables objects or characters to follow a specific path in a controlled manner. """

import logging

from arise.data_types import node_data
from arise.utils import tagging_utils
from arise.utils.math_utils import distance_between
from arise.utils.matrix_utils import matrix_constraint
from arise.utils.io_nodes.io_transform import IoTransform
from arise.utils.modules_utils import (
    create_grps, create_annotation, update_ctrls, ADD_DL, MULT_DL, MULT_DL_INPUT1, MULT_DL_INPUT2,
)

import maya.cmds as mc

LOGGER = logging.getLogger("node_rig_logger")

MAYA_VERSION = 2016  # the version of maya from which this module supports.
AUTHOR = "Etay Herz"  # name of person who created this module.
RIG_CATEGORY = "Basic"  # either 'Basic', 'Cartoon', 'Vfx', 'Game' or 'All'. (used when filtering).
RIG_TYPE = "All"  # Biped, Vehicle, Quadruped, All, ... (for filtering modules in lists).
TAGS = ["basic", "curve", "road", "motion",]
TOOL_TIP = "The Path node enables objects or characters to follow a specific path in a controlled manner."

node_data.NodeData.update_ctrls = update_ctrls


class Path(node_data.NodeData):
    """The Path node enables objects or characters to follow a specific path in a controlled manner. """
    sort_priority = 600

    def __init__(self, parent, docs, icon, module_dict):
        node_data.NodeData.__init__(
            self,
            parent=parent,
            icon=icon,
            docs=docs,
            module_dict=module_dict
        )

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

        self.bezier_ctrls_count_attr = self.add_integer_attribute(
            name="Bezier Ctrls Count",
            default_value=8,
            dynamic_attribute=False,
            annotation="The number of bezier ctrls along the curve.",
            min_value=3,
            max_value=80,
            add_slider=False,
        )

        self.pos_ctrl_attr = self.add_boolean_attribute(
            name="Add Position Ctrl",
            default_value=False,
            annotation="Add another ctrl called 'position_ctrl' that lets you move all the bezier ctrls.",
        )

        self.add_separator()
        self.auto_steer_attr = self.add_boolean_attribute(
            name="Auto Steer",
            default_value=True,
            annotation="Pass front wheels steering to child nodes. Use with 'Vehicle_Body' node.",
        )

        self.wheels_pos_offset_attr = self.add_float_attribute(
            name="Wheels Pos Offset",
            default_value=5.0,
            annotation=(
                "Measure the distance from the front wheels axle to the root guide and set this attribute\n"
                "to that value. This will insure the steering passed to the 'Vehicle_Body' node is calculated correctly"
            ),
            min_value=0.01,
        )

        self.add_separator(title="Connections")
        self.driven_attr = self.add_driven_attribute(name="Input", annotation="Input")
        self.driver_attr = self.add_driver_attribute(name="Output", annotation="Output")

        self.close_layout()

    def evaluate_creation_methods(self):  # REIMPLEMENTED!
        """Reimplemented to enable/disable attrs. """
        self.wheels_pos_offset_attr.set_disabled(False if self.auto_steer_attr.value else True)

        node_data.NodeData.evaluate_creation_methods(self)

    def guides_creation(self):
        """Create guides based on attributes values. """
        self.root_guide = self.add_aim_guide(
            name="curve_root",
            translation=[0, 0, 0],
            side_pin_rotation=(0, 0, 180),
        )
        self.root_guide.shape = "box"

        self.tip_guide = self.add_aim_guide(
            name="curve_tip",
            aim_at_guide=self.root_guide,
            parent=self.root_guide,
            translation=[0, 0, 1800],
            side_pin_guide=self.root_guide,
        )
        self.tip_guide.shape = "box"
        self.tip_guide.aim_rotation_offset = (180, 0, 0)

        self.root_guide.aim_at = self.tip_guide

    def post_guides_creation(self):  # REIMPLEMENTED!
        """Create visual objects to indicate bezier ctrls evenly along the guides curve. """
        self.visual_curve = mc.curve(
            name="{0}_visual_curve".format(self.name),
            degree=1,
            point=[
                self.root_guide.guide_ptr.joint.get_translation(),
                self.tip_guide.guide_ptr.joint.get_translation(),
            ],
        )
        self.visual_curve = IoTransform(self.visual_curve, existing=True)
        tagging_utils.tag_nodes([self.visual_curve], tag=self.uuid.hex)
        self.visual_curve.set_line_width(2)
        self.visual_curve.set_attr("inheritsTransform", 0)
        self.visual_curve.set_templated(True)
        self.visual_curve.parent_relative(self.guide_manager.io_guides_list[0].offset_grp)
        self.visual_curve.lock_and_hide_transformations()

        self.visual_curve_skin_cluster = mc.skinCluster(
            self.root_guide.guide_ptr.joint,
            self.tip_guide.guide_ptr.joint,
            self.visual_curve,
            name="{0}_visual_curve_skinCluster".format(self.name),
            toSelectedBones=True,
            maximumInfluences=1,
            dropoffRate=2,
            obeyMaxInfluences=True,
            weight=1,
        )[0]

        visual_curve_shape = self.visual_curve.get_shapes()[0]
        mc.skinPercent(
            self.visual_curve_skin_cluster,
            "{0}.cv[0]".format(visual_curve_shape),
            transformValue=[(self.root_guide.guide_ptr.joint, 1)],
        )

        mc.skinPercent(
            self.visual_curve_skin_cluster,
            "{0}.cv[1]".format(visual_curve_shape),
            transformValue=[(self.tip_guide.guide_ptr.joint, 1)],
        )

        size = self.ctrls_scale_attr.value
        for index in range(self.bezier_ctrls_count_attr.value):
            poci_node = mc.createNode("pointOnCurveInfo", name="{0}_visual_{1}_POCI".format(self.name, index))
            mc.connectAttr("{0}.worldSpace".format(visual_curve_shape), "{0}.inputCurve".format(poci_node))
            mc.setAttr("{0}.parameter".format(poci_node), float(index) / (self.bezier_ctrls_count_attr.value - 1))

            shape = IoTransform("{0}_bezier_ctrl_{1}_visual_shape".format(self.name, index), existing=False)
            shape.create_shape(shape="sphere", up_orient="+Y", size=size * 3.0)
            shape.set_templated(True)
            shape.set_attr("inheritsTransform", 0)
            shape.parent_relative(self.guide_manager.io_guides_list[0].offset_grp)

            mc.connectAttr("{0}.position".format(poci_node), "{0}.translate".format(shape))
            shape.lock_and_hide_transformations()

            tagging_utils.tag_nodes([poci_node, shape], tag=self.uuid.hex)

    def joints_creation(self):
        """Create joints based on attributes values and guides. (without positioning as this point). """
        pass

    def ctrls_creation(self):
        """Create controls based on attributes values, guides and joints. (without positioning as this point). """
        ctrls_mult = self.ctrls_scale_attr.value * 2.0

        self.motion_ctrl = self.add_ctrl(name="motion", shape="triangle", size=ctrls_mult * 10.0)
        self.motion_ctrl.rotate_offset = [0, 180, 0]
        self.motion_ctrl.add_locked_hidden_attr("scaleY")
        self.motion_ctrl.add_locked_hidden_attr("scaleZ")

        self.position_ctrl = None
        if self.pos_ctrl_attr.value:
            self.position_ctrl = self.add_ctrl(name="position", shape="circle", size=ctrls_mult * 10.0)
            self.position_ctrl.add_locked_hidden_attr("scaleY")
            self.position_ctrl.add_locked_hidden_attr("scaleZ")

        self.bezier_ctrls_list = []
        self.bezier_ctrls_list.append(
            self.add_ctrl(
                name="bezier_point_0",
                up_orient="+Z",
                shape="box",
                size=[1.35*ctrls_mult, 1.35*ctrls_mult, 3.95*ctrls_mult],
            )
        )
        self.bezier_ctrls_list.append(
            self.add_ctrl(
                name="bezier_tangent_a_0",
                shape="sphere",
                size=(1.2 * ctrls_mult),
            )
        )

        for index in range(self.bezier_ctrls_count_attr.value-2):
            tangent_a = self.add_ctrl(
                name="bezier_tangent_a_{0}".format(index+1),
                up_orient="+Z",
                shape="sphere",
                size=(1.2 * ctrls_mult),
            )
            self.bezier_ctrls_list.append(tangent_a)

            point = self.add_ctrl(
                name="bezier_point_{0}".format(index+1),
                up_orient="+Z",
                shape="box",
                size=[1.35*ctrls_mult, 1.35*ctrls_mult, 3.95*ctrls_mult],
            )
            self.bezier_ctrls_list.append(point)

            tangent_b = self.add_ctrl(
                name="bezier_tangent_b_{0}".format(index+1),
                up_orient="+Z",
                shape="sphere",
                size=(1.2 * ctrls_mult),
            )
            self.bezier_ctrls_list.append(tangent_b)

            point.children_guides_list = [tangent_a, tangent_b]

        self.bezier_ctrls_list.append(
            self.add_ctrl(
                name="bezier_tangent_a_{0}".format(self.bezier_ctrls_count_attr.value-1),
                up_orient="+Z",
                shape="sphere",
                size=(1.2 * ctrls_mult),
            )
        )

        self.bezier_ctrls_list.append(
            self.add_ctrl(
                name="bezier_point_{0}".format(self.bezier_ctrls_count_attr.value - 1),
                up_orient="+Z",
                shape="box",
                size=[1.35*ctrls_mult, 1.35*ctrls_mult, 3.95*ctrls_mult],
            )
        )

    def maya_attrs_creation(self):
        """Declare any Maya attributes that users should be able to modify. """
        self.motion_ctrl.add_maya_attr("primary_ctrls_vis", attr_type="bool", default_value=True)

        if self.auto_steer_attr.value:
            self.motion_ctrl.add_maya_attr("auto_steer", attr_type="float", default_value=0.0, min=0.0, max=1.0)

    def rig_creation(self):
        """Using the attributes values, guides, joints, and ctrls, build the rig. """

        if self.is_mirrored:
            LOGGER.error("[node] '%s' does not support mirroring. Skipping node build!", self.name)
            return False  # need to return False to return failed error during build.

        input_grp, output_grp, ctrls_grp = create_grps(self, ["input_grp", "output_grp", "ctrls_grp"])
        data_grp, bezier_ctrls_grp = create_grps(self, ["data_grp", 'bezier_ctrls_grp'])

        output_grp.add_attr("steer", dv=0, keyable=True)
        bezier_ctrls_grp.parent_relative(ctrls_grp)

        self.driven_attr.set_maya_object(input_grp)
        self.driver_attr.set_maya_object(output_grp)

        loc_aim = IoTransform(mc.spaceLocator(name="{0}_loc_aim_temp".format(self.name)), existing=True)
        loc_aim.set_matrix(self.tip_guide.world_transformations["matrix"], space="world")
        loc_up = IoTransform(mc.spaceLocator(name="{0}_loc_up_temp".format(self.name)), existing=True)
        loc_up.set_matrix(self.root_guide.world_transformations["matrix"], space="world")

        input_grp.set_translation(self.root_guide.world_transformations["translate"], space="world")
        temp_constraint = input_grp.aim_constraint_to(
            loc_aim,
            aimVector=(0, 0, 1),
            upVector=(0, 1, 0),
            worldUpType="object",
            worldUpObject=loc_up,
            worldUpVector=(0, 0, 1),
        )
        mc.delete(temp_constraint, loc_aim, loc_up)

        ctrls_grp.match_transformation_to(input_grp)
        data_grp.match_transformation_to(input_grp)
        data_grp.lock_and_hide_transformations()

        motion_ctrl = self.motion_ctrl.pointer
        bezier_ctrls_list = [ctrl.pointer for ctrl in self.bezier_ctrls_list]

        short_name = motion_ctrl.short_name
        motion_ctrl.pos_grp = motion_ctrl.offset_grp.add_group_above("{0}_driven_grp".format(short_name))
        motion_ctrl.pos_grp.parent_relative(ctrls_grp)
        motion_ctrl.scale_attrs_connect()
        motion_ctrl.pos_grp.set_attr("inheritsTransform", 0)

        if self.pos_ctrl_attr.value:
            position_ctrl = self.position_ctrl.pointer
            position_ctrl.offset_grp.parent_relative(ctrls_grp)
            position_ctrl.scale_attrs_connect()
            matrix_constraint(position_ctrl, bezier_ctrls_grp, maintain_offset=False)

        root_pos = self.root_guide.world_transformations["translate"]
        tip_pos = self.tip_guide.world_transformations["translate"]
        count = (((self.bezier_ctrls_count_attr.value - 2) * 3) + 4)
        step = 1.0 / (count - 1)

        curve_points = []
        for cv, bezier_ctrl in zip(range(count), bezier_ctrls_list):
            x = root_pos[0] + (tip_pos[0] - root_pos[0]) * cv * step
            y = root_pos[1] + (tip_pos[1] - root_pos[1]) * cv * step
            z = root_pos[2] + (tip_pos[2] - root_pos[2]) * cv * step
            curve_points.append((x, y, z))

            bezier_ctrl.offset_grp.parent_relative(bezier_ctrls_grp)
            bezier_ctrl.offset_grp.set_translation((x, y, z))

        # parent bezier ctrls to each other and add annotation visual.
        bezier_ctrls_list[1].offset_grp.parent(bezier_ctrls_list[0])
        create_annotation(
            parent_to=bezier_ctrls_list[0],
            aim_at=bezier_ctrls_list[1],
            move_with=bezier_ctrls_list[0],
            name="{0}_annotation".format(bezier_ctrls_list[1].short_name),
        )

        bezier_ctrls_list[-2].offset_grp.parent(bezier_ctrls_list[-1])
        create_annotation(
            parent_to=bezier_ctrls_list[-1],
            aim_at=bezier_ctrls_list[-2],
            move_with=bezier_ctrls_list[-1],
            name="{0}_annotation".format(bezier_ctrls_list[-2].short_name),
        )

        for ctrl_info in self.bezier_ctrls_list:
            if hasattr(ctrl_info, "children_guides_list"):

                for child_info in ctrl_info.children_guides_list:
                    child_info.pointer.offset_grp.parent(ctrl_info.pointer)

                    create_annotation(
                        parent_to=ctrl_info.pointer,
                        aim_at=child_info.pointer,
                        move_with=ctrl_info.pointer,
                        name="{0}_annotation".format(child_info.pointer.short_name),
                    )

        bezier_curve = mc.curve(
            bezier=True,
            degree=3,
            point=curve_points,
            knot=[int(index / 3) for index in range(count + 2)],
            name="{0}_bezier_drive_curve".format(self.name),
        )
        bezier_curve = IoTransform(bezier_curve, existing=True)
        bezier_curve.set_templated(True)
        bezier_curve.parent(data_grp)

        for index, ctrl in enumerate(bezier_ctrls_list):
            decomp_node = mc.createNode("decomposeMatrix", name="{0}_decomposeMatrix".format(ctrl.short_name))
            mc.connectAttr("{0}.worldMatrix[0]".format(ctrl), "{0}.inputMatrix".format(decomp_node))
            mc.connectAttr(
                "{0}.outputTranslate".format(decomp_node),
                "{0}.controlPoints[{1}]".format(bezier_curve, index),
            )

        motion_path_node = mc.pathAnimation(
            motion_ctrl.pos_grp,
            bank=False,
            curve=bezier_curve,
            fractionMode=True,
            follow=True,
            followAxis="z",
            upAxis="y",
            worldUpObject=bezier_ctrls_list[0],
            worldUpType="objectrotation",
            worldUpVector=[0, 1, 0],
            name="{0}_drive_motionPath".format(self.name),
        )

        # remove unnecessary animation node.
        mc.delete(mc.listConnections("{0}.uValue".format(motion_path_node), source=True, destination=False))

        motion_ctrl.add_spacer_attr()
        motion_ctrl.vis_attr = motion_ctrl.add_attr("primary_ctrls_vis", at="bool", dv=1, keyable=True)
        bezier_ctrls_grp.connect_attr("visibility", motion_ctrl.vis_attr)
        bezier_curve.connect_attr("visibility", motion_ctrl.vis_attr)
        bezier_curve.lock_and_hide_transformations()

        if self.pos_ctrl_attr.value:
            self.position_ctrl.pointer.offset_grp.connect_attr("visibility", motion_ctrl.vis_attr)

        motion_ctrl.path_pos_attr = motion_ctrl.add_attr("path_position", min=0, max=100, dv=0, keyable=True)
        mult_node = mc.createNode(MULT_DL, name="{0}_path_position_mult".format(self.name))
        mc.connectAttr(motion_ctrl.path_pos_attr, "{0}.{1}".format(mult_node, MULT_DL_INPUT1))
        mc.setAttr("{0}.{1}".format(mult_node, MULT_DL_INPUT2), 0.01)
        mc.connectAttr("{0}.output".format(mult_node), "{0}.uValue".format(motion_path_node))

        if self.auto_steer_attr.value:
            self.auto_steer_setup(data_grp, bezier_curve, output_grp)

        matrix_constraint(
            input_grp,
            motion_ctrl.pos_grp,
            maintain_offset=False,
            skip_locked=True,
            force=False,
            skip_attrs=(True, True, True, True, True, True, False, False, False),
        )
        matrix_constraint(input_grp, ctrls_grp, maintain_offset=False)
        matrix_constraint(motion_ctrl, output_grp, maintain_offset=False)

    def auto_steer_setup(self, data_grp, bezier_curve, output_grp):
        """Create the auto steer setup that passes the steering from the curve to the child nodes.

        Arguments:
            data_grp {IoTransform} -- the data_grp of the node.
            bezier_curve {IoTransform} -- the bezier curve that drives the motion.
            output_grp {IoTransform} -- the output_grp of the node.

        """
        motion_ctrl = self.motion_ctrl.pointer
        motion_ctrl.add_spacer_attr()
        auto_steer_attr = motion_ctrl.add_attr("auto_steer", min=0, max=1, dv=0, keyable=True)
        offset_distance = self.wheels_pos_offset_attr.value

        distance = distance_between(
            self.root_guide.world_transformations["translate"],
            self.tip_guide.world_transformations["translate"],
        )
        aim_dis = ((offset_distance / distance) * 100)
        steer_aim_dis_attr = motion_ctrl.add_attr(
            "steer_aim_dis",
            min=0.01,
            max=100,
            dv=aim_dis + 1,
            keyable=True,
        )

        ctrls_scale = self.ctrls_scale_attr.value
        aim_driven_grp = IoTransform("{0}_aim_driven_grp".format(self.name), existing=False)
        aim_driven_grp.parent_relative(motion_ctrl.pos_grp)
        aim_driven_grp.set_attr("translateZ", offset_distance)
        aim_driven_grp.create_shape(shape="arrow", up_orient="+Z", size=2 * ctrls_scale)
        aim_driven_grp.connect_attr("visibility", motion_ctrl.vis_attr)
        aim_driven_grp.lock_and_hide_scale()
        aim_driven_grp.set_templated(True)

        auto_steer_off_grp = IoTransform("{0}_auto_steer_off_grp".format(self.name), existing=False)
        auto_steer_off_grp.parent_relative(motion_ctrl.pos_grp)
        auto_steer_off_grp.set_attr("translateZ", offset_distance + 10)

        steer_aim_at_grp = IoTransform("{0}_steer_aim_at_grp".format(self.name), existing=False)
        steer_aim_at_grp.parent_relative(data_grp)
        steer_aim_at_grp.create_shape(shape="locator_fat", up_orient="+Z", size=3 * ctrls_scale)
        steer_aim_at_grp.connect_attr("visibility", motion_ctrl.vis_attr)
        steer_aim_at_grp.set_templated(True)
        steer_aim_at_grp.set_attr("inheritsTransform", 0)

        aim_motion_path_node = mc.pathAnimation(
            steer_aim_at_grp,
            bank=False,
            curve=bezier_curve,
            fractionMode=True,
            follow=False,
            name="{0}_aim_at_motionPath".format(self.name),
        )
        # remove unnecessary animation node.
        mc.delete(mc.listConnections("{0}.uValue".format(aim_motion_path_node), source=True, destination=False))

        add_node = mc.createNode(ADD_DL, name="{0}_steer_aim_at_add".format(self.name))
        mc.connectAttr(steer_aim_dis_attr, "{0}.input1".format(add_node))
        mc.connectAttr(motion_ctrl.path_pos_attr, "{0}.input2".format(add_node))

        mult_node = mc.createNode(MULT_DL, name="{0}_aim_at_path_position_mult".format(self.name))
        mc.connectAttr("{0}.output".format(add_node), "{0}.{1}".format(mult_node, MULT_DL_INPUT1))
        mc.setAttr("{0}.{1}".format(mult_node, MULT_DL_INPUT2), 0.01)
        mc.connectAttr("{0}.output".format(mult_node), "{0}.uValue".format(aim_motion_path_node))

        aim_constraint = aim_driven_grp.aim_constraint_to(
            [steer_aim_at_grp, auto_steer_off_grp],
            aimVector=(0, 0, 1),
            upVector=(0, 1, 0),
            worldUpType="objectrotation",
            worldUpObject=motion_ctrl,
            worldUpVector=(0, 1, 0),
            maintainOffset=False,
            skip=["x", "z"],
        )

        steer_attr, off_attr = mc.aimConstraint(aim_constraint, q=True, weightAliasList=True)
        condition_node = mc.createNode("condition", name="{0}_auto_steer_condition".format(self.name))
        mc.connectAttr("{0}.uValue".format(aim_motion_path_node), "{0}.firstTerm".format(condition_node))
        mc.setAttr("{0}.secondTerm".format(condition_node), 1.0)
        mc.setAttr("{0}.operation".format(condition_node), 3)  # greater or equal.
        mc.setAttr("{0}.colorIfTrueR".format(condition_node), 0.0)
        mc.setAttr("{0}.colorIfTrueG".format(condition_node), 1.0)
        mc.connectAttr(auto_steer_attr, "{0}.colorIfFalseR".format(condition_node))
        reverse_node = mc.createNode("reverse", name="{0}_auto_steer_reverse".format(self.name))
        mc.connectAttr(auto_steer_attr, "{0}.inputX".format(reverse_node))
        mc.connectAttr("{0}.outputX".format(reverse_node), "{0}.colorIfFalseG".format(condition_node))
        mc.connectAttr("{0}.outColorR".format(condition_node), "{0}.{1}".format(aim_constraint, steer_attr))
        mc.connectAttr("{0}.outColorG".format(condition_node), "{0}.{1}".format(aim_constraint, off_attr))

        output_grp.connect_attr("steer", aim_driven_grp.attr("rotateY"))
