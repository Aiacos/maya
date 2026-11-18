"""Cartoon_A_Leg module creates a cartoon_complex leg module. """

import maya.cmds as mc

from arise.utils import matrix_utils
from arise.utils.modules_utils import (
    create_grps, movable_pivot_setup, ADD_DL, MULT_DL, MULT_DL_INPUT1, MULT_DL_INPUT2,
)
from arise.utils.io_nodes.io_transform import IoTransform
from arise.utils.subcomponents.limb_base import Limb

MAYA_VERSION = 2016  # the version of Maya from which this module supports.
AUTHOR = "Etay Herz"  # name of person who created this module.
RIG_CATEGORY = "Cartoon"  # either 'Basic', 'Cartoon', 'Vfx', 'Game' or 'All'. (used when filtering).
RIG_TYPE = "Biped"  # Biped, Car, Quadruped, All, ... (for filtering modules in lists).
TAGS = ["cartoon", "complex", "advance", "ribbon", "bendy bones", "ik", "fk", "leg"]
TOOL_TIP = "Cartoon leg and foot. Features include IK/FK, soft IK, stretch, foot roll, tilt, etc."


class CA_Leg(Limb):
    """Cartoon_A_Leg module creates a cartoon_complex leg module. """
    BODY_PART = "leg"
    WORLD_ORIENT_DEFAULT = "-Y"
    SWITCH_OFFSET_DEFAULT = [-13, 0, 0]
    MIRROR_DEFAULT = False
    MIRROR_ANNOTATION = (
        "Only affects mirrored nodes.\n\n"
        "Unchecked - The IK ctrls of mirrored nodes will align with the world,\n"
        "meaning that both legs will move and rotate in the same direction (default for legs).\n\n"
        "Checked - The IK ctrls of mirrored nodes will mirror orientations,\n"
        "meaning that both legs will reflect each other (default for arms)."
    )
    AUTO_CLAVICLE_DEFAULT = False
    AUTO_CLAVICLE_NOTE = "\nTurned off by default for legs."
    AUTO_CLAVICLE_Z_LIMITS = (-180, 180)
    BEZIER_OFFSET_DEFAULT = [-10, 0, 0]
    BEZIER_ANNOTATION = "Position offset of bezier ctrls from the ribbons.\nmultiplied by attribute 'Ctrls Scale'."
    GUIDES = {
        "base": {"translation": [9.5, 108.5, 1], "rotation": [0, 0, 180]},
        "root": {"translation": [12.0, 99, 0.5]},
        "mid": {"translation": [12.0, 55, 8.7]},
        "tip": {"translation": [12.0, 13, -3.0], "rotation": [0, 0, 180]},
    }
    BASE_SKINNING_JNT = False
    LIMB_JNT_RADIUS = 0.5
    TIP_HUMAN_IK = "*Foot"
    UPPER_ROLL_TAGS = ("*UpLeg", "Leaf*UpLegRoll{0}")
    LOWER_ROLL_TAGS = ("*Leg", "Leaf*LegRoll{0}")
    BASE_CTRL = {"shape": "pin_sphere", "up_orient": "-X", "size": 0.95}
    SECONDARY_CLEAN_ORIENT = "-Y"
    TIP_HUMAN_IK_CTRL = "*Ankle"
    PV_HUMAN_IK_CTRL = "*Knee"
    WORLD_DIRECTION_FLIP_X = False
    BASE_CTRL_VIS_ATTR = True
    OUTPUT_TIP_GRP = "output_ankle_grp"

    def _driver_attributes_creation(self):
        self.driver_ankle_attr = self.add_driver_attribute(name="Ankle Output", annotation="Output")
        self.driver_toes_start_attr = self.add_driver_attribute(name="Toes Start Output", annotation="Output")
        self.driver_toes_tip_attr = self.add_driver_attribute(name="Toes Tip Output", annotation="Output")

    def _foot_guides_creation(self):
        self.heel_guide = self.add_guide(
            name="heel",
            translation=[12, 0, -8.3],
            rotation=[90, 0, 180],
            parent=self.tip_guide,
        )
        self.heel_guide.shape = "sphere"
        self.heel_guide.size = self.heel_guide.size / 2.0

        self.toes_guide = self.add_guide(
            name="toes_root",
            translation=[12, 2.8, 6],
            rotation=[90, 0, 180],
            parent=self.tip_guide,
        )

        self.toes_tip_guide = self.add_guide(
            name="toes_tip",
            translation=[12, 2.8, 13],
            rotation=[90, 0, 180],
            parent=self.toes_guide,
        )
        self.toes_tip_guide.shape = "sphere"
        self.toes_tip_guide.size = self.toes_tip_guide.size / 2.0

        self.outer_tilt_guide = self.add_guide(
            name="outer_tilt",
            translation=[18, 0, 0],
            rotation=[90, 0, 180],
            parent=self.tip_guide,
        )
        self.outer_tilt_guide.shape = "sphere"
        self.outer_tilt_guide.size = self.outer_tilt_guide.size / 2.0

        self.inner_tilt_guide = self.add_guide(
            name="inner_tilt",
            translation=[6, 0, 0],
            rotation=[90, 0, 180],
            parent=self.tip_guide,
        )
        self.inner_tilt_guide.shape = "sphere"
        self.inner_tilt_guide.size = self.inner_tilt_guide.size / 2.0

    def _foot_joints_creation(self):
        self.toes_jnt = self.add_joint(
            name="toes_root", skinning_jnt=True, tag_parent_jnt=self.tip_jnt, radius=0.5
        )
        self.toes_tip_jnt = self.add_joint(
            name="toes_tip", skinning_jnt=False, tag_parent_jnt=self.toes_jnt, radius=0.25,
        )

    def _foot_joints_human_ik(self):
        self.toes_jnt.human_ik = "*ToeBase"

    def _foot_ctrls_creation(self, scale_mult):
        self.toes_ctrl = self.add_ctrl(name="toes", shape="circle", size=(1.3 * scale_mult))
        for attr in ["translateX", "translateY", "translateZ", "scaleY", "scaleZ"]:
            self.toes_ctrl.add_locked_hidden_attr(attr)

        self.master_ctrl = self.add_ctrl(name="ik_master", up_orient="+Z", size=(0.5 * scale_mult))
        self.master_ctrl.shape = "arrow_rotation_4_way"
        self.master_ctrl.translate_offset = (0, 0, 1.5 * scale_mult)

        for attr in ["translateX", "translateY", "translateZ", "rotateZ", "scaleX", "scaleY", "scaleZ"]:
            self.master_ctrl.add_locked_hidden_attr(attr)

        self.ik_toes_ball_ctrl = self.add_ctrl(
            name="ik_toes_ball",
            up_orient="+Z",
            shape="strap",
            size=1.0 * scale_mult,
        )
        self.ik_toes_ball_ctrl.translate_offset = (0, 0, 1.0 * scale_mult)

        self.ik_heel_ctrl = self.add_ctrl(name="ik_heel", up_orient="+Y", shape="box", size=(0.3 * scale_mult))
        self.ik_toes_tip_ctrl = self.add_ctrl(name="ik_toes_tip", shape="box", size=(0.3 * scale_mult))

        for ctrl in [self.ik_toes_ball_ctrl, self.ik_heel_ctrl, self.ik_toes_tip_ctrl]:
            for attr in ["translateX", "translateY", "translateZ", "scaleX", "scaleY", "scaleZ"]:
                ctrl.add_locked_hidden_attr(attr)

    def _foot_maya_attrs_creation(self):
        self.master_ctrl.add_maya_attr(name="foot_roll_angle", attr_type="float", default_value=30, min=0, max=180)
        self.master_ctrl.add_maya_attr(name="tilt_pivots", attr_type="bool", default_value=False)

    def _foot_output_grps_creation(self):
        self._toes_start_output, self._toes_tip_output = create_grps(
            self, ["output_toes_start_grp", "output_toes_tip_grp"]
        )

    def _set_driver_objects(self, output_tip_grp):
        self.driver_ankle_attr.set_maya_object(output_tip_grp)
        self.driver_toes_start_attr.set_maya_object(self._toes_start_output)
        self.driver_toes_tip_attr.set_maya_object(self._toes_tip_output)

    def _foot_rig_creation(self, ik_chain_obj, ik_fk_switch_obj):
        toes_start_output = self._toes_start_output
        toes_tip_output = self._toes_tip_output

        heel_pos_grp = IoTransform("{0}_heel_pos_grp".format(self.name))
        heel_pos_grp.offset_grp = heel_pos_grp.add_group_above("{0}_heel_pos_offset_grp".format(self.name))
        heel_pos_grp.offset_grp.parent_relative(ik_fk_switch_obj.tip_jnt)
        heel_pos_grp.offset_grp.set_matrix(self.heel_guide.world_transformations["matrix"])
        heel_pos_grp.offset_grp.set_scale([1, 1, 1])

        toes_jnt = self.toes_jnt.pointer
        toes_jnt.parent_relative(ik_fk_switch_obj.tip_jnt)
        toes_jnt.set_matrix(self.toes_guide.world_transformations["matrix"])
        toes_jnt.freeze_transformations()
        toes_jnt.add_joint_orient()

        toes_tip_jnt = self.toes_tip_jnt.pointer
        toes_tip_jnt.parent_relative(toes_jnt)
        toes_tip_jnt.set_matrix(self.toes_tip_guide.world_transformations["matrix"])
        toes_tip_jnt.freeze_transformations()
        toes_tip_jnt.add_joint_orient()

        loc_grp = ik_chain_obj.tip_ctrl.btm_ctrl.loc_grp
        loc_grp.add_group_above("{0}b_grp".format(loc_grp.short_name[:-3]), maintain_local_values=False)
        tilt_outer_grp = loc_grp.add_group_above("{0}_tilt_outer_grp".format(self.name))
        tilt_outer_grp.offset_grp = tilt_outer_grp.add_group_above("{0}_tilt_outer_offset_grp".format(self.name))
        tilt_inner_grp = loc_grp.add_group_above("{0}_tilt_inner_grp".format(self.name))
        tilt_inner_grp.offset_grp = tilt_inner_grp.add_group_above("{0}_tilt_inner_offset_grp".format(self.name))
        loc_grp.parent(self.module_grp)

        outer_tilt_pos = self.outer_tilt_guide.world_transformations["translate"]
        inner_tilt_pos = self.inner_tilt_guide.world_transformations["translate"]
        mc.xform(tilt_outer_grp.offset_grp, ws=True, translation=outer_tilt_pos)
        mc.xform(tilt_inner_grp.offset_grp, ws=True, translation=inner_tilt_pos)
        loc_grp.parent(tilt_inner_grp)

        ik_toes_tip_ctrl = self.ik_toes_tip_ctrl.pointer
        self._parent_ctrl_above(loc_grp, ik_toes_tip_ctrl, toes_tip_jnt.get_matrix())
        tip_driven_grp = ik_toes_tip_ctrl.add_group_above("{0}_driven_grp".format(ik_toes_tip_ctrl.short_name))
        ik_toes_ball_ctrl = self.ik_toes_ball_ctrl.pointer
        self._parent_ctrl_above(loc_grp, ik_toes_ball_ctrl, toes_jnt.get_matrix())
        toes_driven_grp = ik_toes_ball_ctrl.add_group_above("{0}_driven_grp".format(ik_toes_ball_ctrl.short_name))
        ik_heel_ctrl = self.ik_heel_ctrl.pointer
        self._parent_ctrl_above(loc_grp, ik_heel_ctrl, heel_pos_grp.get_matrix())
        heel_driven_grp = ik_heel_ctrl.add_group_above("{0}_driven_grp".format(ik_heel_ctrl.short_name))

        ik_toes_tip_ctrl.add_spacer_attr()
        movable_pivot_setup(ik_toes_tip_ctrl, scale_pivot=False, attr=None)
        tip_driven_grp.connect_attr("rotatePivot", ik_toes_tip_ctrl.attr("rotatePivot"))

        ik_heel_ctrl.add_spacer_attr()
        movable_pivot_setup(ik_heel_ctrl, scale_pivot=False, attr=None)
        heel_driven_grp.connect_attr("rotatePivot", ik_heel_ctrl.attr("rotatePivot"))

        # toes_ctrl and it's compensate.
        toes_ctrl = self.toes_ctrl.pointer
        comp_a_grp = toes_ctrl.offset_grp.add_group_above("{0}_comp_a_grp".format(toes_ctrl.short_name))
        comp_b_grp = toes_ctrl.offset_grp.add_group_above("{0}_comp_b_grp".format(toes_ctrl.short_name))
        comp_c_grp = toes_ctrl.offset_grp.add_group_above("{0}_comp_c_grp".format(toes_ctrl.short_name))

        comp_a_grp.parent_relative(ik_fk_switch_obj.ctrls_grp)
        comp_a_grp.set_matrix(ik_fk_switch_obj.tip_jnt.get_matrix())
        comp_b_grp.set_matrix(toes_jnt.get_matrix())
        toes_ctrl.scale_attrs_connect()
        matrix_utils.matrix_constraint(driver=toes_ctrl, driven=toes_jnt, maintain_offset=False)
        matrix_utils.matrix_constraint(driver=ik_fk_switch_obj.tip_jnt, driven=comp_a_grp, maintain_offset=False)

        rotate_mult_node = mc.createNode("multiplyDivide", n="{0}_rotate_comp".format(comp_c_grp.short_name))
        switch_node = mc.createNode("multiplyDivide", n="{0}_switch_comp".format(comp_c_grp.short_name))
        add_node = mc.createNode(ADD_DL, n="{0}_add_driven".format(tip_driven_grp.short_name))

        mc.connectAttr(ik_toes_ball_ctrl.attr("rotateX"), "{0}.input1".format(add_node))
        mc.connectAttr("{0}.rotateX".format(toes_driven_grp), "{0}.input2".format(add_node))
        mc.connectAttr("{0}.output".format(add_node), "{0}.input1X".format(rotate_mult_node))
        mc.connectAttr(ik_toes_ball_ctrl.attr("rotateY"), "{0}.input1Y".format(rotate_mult_node))
        mc.connectAttr(ik_toes_ball_ctrl.attr("rotateZ"), "{0}.input1Z".format(rotate_mult_node))

        for attr in ["input2X", "input2Y", "input2Z"]:
            mc.setAttr("{0}.{1}".format(rotate_mult_node, attr), -1)

        mc.connectAttr("{0}.outputX".format(rotate_mult_node), "{0}.input1X".format(switch_node))
        mc.connectAttr("{0}.outputY".format(rotate_mult_node), "{0}.input1Y".format(switch_node))
        mc.connectAttr("{0}.outputZ".format(rotate_mult_node), "{0}.input1Z".format(switch_node))

        mc.connectAttr("{0}.outputX".format(ik_fk_switch_obj.reverse_node), "{0}.input2X".format(switch_node))
        mc.connectAttr("{0}.outputX".format(ik_fk_switch_obj.reverse_node), "{0}.input2Y".format(switch_node))
        mc.connectAttr("{0}.outputX".format(ik_fk_switch_obj.reverse_node), "{0}.input2Z".format(switch_node))

        mc.connectAttr("{0}.outputX".format(switch_node), comp_c_grp.attr("rotateX"))
        mc.connectAttr("{0}.outputY".format(switch_node), comp_c_grp.attr("rotateY"))
        mc.connectAttr("{0}.outputZ".format(switch_node), comp_c_grp.attr("rotateZ"))

        minus_node = mc.createNode("plusMinusAverage", n="{0}_rotation_order_minus".format(comp_c_grp.short_name))
        mc.setAttr("{0}.operation".format(minus_node), 2)
        mc.setAttr("{0}.input3D[0].input3Dx".format(minus_node), 5)
        mc.connectAttr(ik_toes_ball_ctrl.attr("rotateOrder"), "{0}.input3D[1].input3Dx".format(minus_node))
        mc.connectAttr("{0}.output3Dx".format(minus_node), comp_c_grp.attr("rotateOrder"))

        master_ctrl = self.master_ctrl.pointer
        master_ctrl.offset_grp.parent_relative(ik_chain_obj.tip_ctrl.btm_ctrl)
        master_ctrl.offset_grp.set_matrix(toes_tip_jnt.get_matrix())

        master_ctrl.add_spacer_attr()
        foot_roll_attr = master_ctrl.add_attr("foot_roll_angle", dv=30, min=0, max=180, keyable=True)
        tilt_vis_attr = master_ctrl.add_attr("tilt_pivots", attributeType="bool", keyable=True, dv=0)
        movable_pivot_setup(tilt_outer_grp, scale_pivot=False, attr=tilt_vis_attr)
        movable_pivot_setup(tilt_inner_grp, scale_pivot=False, attr=tilt_vis_attr)

        # tilt.
        clamp = mc.createNode("clamp", n="{0}_tilt_clamp".format(master_ctrl.short_name))
        mc.connectAttr(master_ctrl.attr("rotateY"), "{0}.inputR".format(clamp))
        mc.connectAttr(master_ctrl.attr("rotateY"), "{0}.inputG".format(clamp))
        mc.setAttr("{0}.maxR".format(clamp), 360)
        mc.setAttr("{0}.minG".format(clamp), -360)
        mc.connectAttr("{0}.outputR".format(clamp), tilt_inner_grp.attr("rotateZ"))
        mc.connectAttr("{0}.outputG".format(clamp), tilt_outer_grp.attr("rotateZ"))

        # foot_roll and heel pivot.
        clamp = mc.createNode("clamp", n="{0}_foot_roll_clamp".format(master_ctrl.short_name))
        multi_a = mc.createNode(MULT_DL, n="{0}_foot_roll_inverse".format(master_ctrl.short_name))
        multi_b = mc.createNode(MULT_DL, n="{0}_toes_inverse".format(master_ctrl.short_name))
        remap = mc.createNode("remapValue", n="{0}_remap_foot_roll".format(master_ctrl.short_name))

        mc.connectAttr(master_ctrl.attr("rotateX"), "{0}.{1}".format(multi_a, MULT_DL_INPUT1))
        mc.setAttr("{0}.{1}".format(multi_a, MULT_DL_INPUT2), -1)

        mc.connectAttr("{0}.output".format(multi_a), "{0}.inputValue".format(remap))
        mc.connectAttr(foot_roll_attr, "{0}.inputMin".format(remap))
        mc.setAttr("{0}.inputMax".format(remap), 10000)
        mc.setAttr("{0}.outputMin".format(remap), 0)
        mc.setAttr("{0}.outputMax".format(remap), -10000)
        mc.connectAttr("{0}.outValue".format(remap), tip_driven_grp.attr("rotateX"))

        mc.connectAttr(master_ctrl.attr("rotateX"), "{0}.inputR".format(clamp))
        mc.connectAttr("{0}.output".format(multi_a), "{0}.inputG".format(clamp))
        mc.setAttr("{0}.minR".format(clamp), 0)
        mc.setAttr("{0}.maxR".format(clamp), 180)
        mc.setAttr("{0}.minG".format(clamp), 0)
        mc.connectAttr(foot_roll_attr, "{0}.maxG".format(clamp))
        mc.connectAttr("{0}.outputR".format(clamp), heel_driven_grp.attr("rotateX"))
        mc.connectAttr("{0}.outputG".format(clamp), "{0}.{1}".format(multi_b, MULT_DL_INPUT1))

        mc.setAttr("{0}.{1}".format(multi_b, MULT_DL_INPUT2), -1)
        mc.connectAttr("{0}.output".format(multi_b), toes_driven_grp.attr("rotateX"))

        matrix_utils.matrix_constraint(driver=toes_tip_jnt, driven=toes_tip_output, maintain_offset=False)
        matrix_utils.matrix_constraint(driver=toes_jnt, driven=toes_start_output, maintain_offset=False)

    @staticmethod
    def _parent_ctrl_above(child, new_parent_ctrl, matrix):
        """Parent new_parent_ctrl above child and below child current parent.

        Args:
            child (IoTransform): the child to add the new parent above
            new_parent_ctrl (IoTransform): the new parent ctrl to add above
            matrix (list): of matrix to position and orient new_parent_ctrl
        """
        grandparent = mc.listRelatives(child, parent=True, fullPath=True)[0]
        new_parent_ctrl.offset_grp.parent(grandparent)
        new_parent_ctrl.offset_grp.set_matrix(matrix)
        child.parent(new_parent_ctrl)
