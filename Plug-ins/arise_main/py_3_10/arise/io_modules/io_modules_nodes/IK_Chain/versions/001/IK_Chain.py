"""IK_Chain module creates a basic IK chain rig. """

import maya.cmds as mc

from arise.utils.io_nodes.io_transform import IoTransform
from arise.data_types import node_data
from arise.utils.matrix_utils import matrix_constraint
from arise.utils.math_utils import distance_between
from arise.utils.tagging_utils import tag_as_dont_tag
from arise.utils.modules_utils import (
    world_rotation, secondary_ctrls_setup, expose_rotation_order, create_grps, SECONDARY_COLOR, update_ctrls,
)

MAYA_VERSION = 2016  # the version of maya from which this module supports.
AUTHOR = "Etay Herz"  # name of person who created this module.
RIG_CATEGORY = "Basic"  # either 'Basic', 'Cartoon', 'Vfx', 'Game' or 'All'. (used when filtering).
RIG_TYPE = "All"  # Biped, Car, Quadruped, All, ... (for filtering modules in lists).
TAGS = ["basic", "simple", "ik", "chain", "springIk", "RotatePlaneIk", "RP solver"]
TOOL_TIP = "Simple IK chain."

node_data.NodeData.update_ctrls = update_ctrls


class IK_Chain(node_data.NodeData):
    """IK_Chain module creates a basic IK chain rig. """
    sort_priority = 500

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
        self.add_collapsible_layout(title="Guides", shown=False)
        self.guides_up_shared_attr = self.add_boolean_attribute(
            name="Single Side Guide",
            default_value=True,
            annotation=(
                "For some Aim Guides, the 'side_vector' (twist) is locked and driven by a single 'side_vector', "
                "which keeps the orientation consistent.\n"
                "Uncheck this attribute to unlock them if you need more control over the twist.\n"
                "Re-template is required when changes are made."
            ),
            help_link="https://youtu.be/-1fpRw6oJME?t=233",
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

        self.clean_transformations_attr = self.add_boolean_attribute(
            name="Clean Transformations",
            default_value=True,
            annotation=(
                "If checked, the zeroed pose will be the same as the bind pose;\n"
                "if unchecked, when zeroing the ctrls, they will align with a world axis specified "
                "in the following two attributes."
            ),
            help_link="https://youtu.be/-1fpRw6oJME?t=61",
        )

        self.add_collapsible_layout(title="World Orientation", shown=False)
        items = ["+X", "+Y", "+Z", "-X", "-Y", "-Z"]
        self.world_orientation_attr = self.add_radio_attribute(
            name="World Orientation",
            items=items,
            default_value=items.index("+Y"),
            annotation=(
                "The world axis the ctrls will align with when zeroed.\n"
                "Usually, this attribute's default value is the correct value."
            ),
            help_link="https://youtu.be/-1fpRw6oJME?t=61",
        )
        self.world_twist_attr = self.add_float_attribute(
            name="World Orient Twist",
            min_value=-360,
            max_value=360,
            annotation=(
                "Along with 'world Orientation', defines the ctrls zeroed pose.\n"
                "Usually, the default value of 0 is the correct value."
            ),
            help_link="https://youtu.be/-1fpRw6oJME?t=61",
        )
        self.close_layout()

        self.expose_rotation_order_attr = self.add_boolean_attribute(
            name="Expose RotateOrder",
            default_value=True,
            annotation="Exposes all the ctrls 'RotateOrder' attribute in the Channel Box.",
            help_link="https://youtu.be/-1fpRw6oJME?t=149",
        )
        self.secondary_ctrls_attr = self.add_boolean_attribute(
            name="Secondary Ctrls",
            default_value=False,
            annotation="Secondary ctrls are added under some ctrls to help prevent gimbal lock.",
            help_link="https://youtu.be/-1fpRw6oJME?t=157",
        )

        self.add_separator()
        self.joint_count_attr = self.add_integer_attribute(
            name="Joints",
            default_value=3,
            dynamic_attribute=False,
            writable=True,
            readable=True,
            promoted=False,
            annotation="The number of joints/guides; modifying this attribute requires a 're-template'.",
            min_value=2,
            max_value=40,
            add_slider=False,
        )

        self.add_separator(title="Connections")
        self.root_driven_attr = self.add_driven_attribute(name="Root Input", annotation="Input")
        self.tip_driven_attr = self.add_driven_attribute(name="Tip Input", annotation="Input")
        self.driver_root_attr = self.add_driver_attribute(name="Root Output", annotation="Output")
        self.driver_tip_attr = self.add_driver_attribute(name="Tip Output", annotation="Output")

        self.close_layout()

    def evaluate_creation_methods(self):  # REIMPLEMENTED!
        """Reimplemented to enable/disable attrs. """
        self.world_orientation_attr.set_disabled(True if self.clean_transformations_attr.value else False)
        self.world_twist_attr.set_disabled(True if self.clean_transformations_attr.value else False)

        node_data.NodeData.evaluate_creation_methods(self)

    def guides_creation(self):
        """Create guides based on attributes values. """
        offset = 15
        self.guides_list = []
        side_pin_guide = None
        parent = None
        for index in range(self.joint_count_attr.value):
            guide = self.add_aim_guide(
                name="{0}".format(str(index).zfill(4)),
                translation=[0, index * offset, 0],
                parent=parent,
                side_pin_rotation=(0, 0, 0),
                side_pin_guide=side_pin_guide if self.guides_up_shared_attr.value else None,
            )
            if side_pin_guide is None:
                side_pin_guide = guide

            self.guides_list.append(guide)
            parent = guide

        # have them aim at the next guide.
        for index, guide in enumerate(self.guides_list[:-1]):
            guide.aim_at = self.guides_list[index+1]

        # self.guides_list[-1].parent = self.guides_list[0]
        self.guides_list[-1].aim_at = self.guides_list[-2]
        self.guides_list[-1].aim_rotation_offset = (180, 0, 0)

        # create small plane between guides 0, 1 and 2.
        trans = self.guides_list[1].translation
        self.guides_list[1].translation = (trans[0], trans[1], trans[2] + 1.0)

    def joints_creation(self):
        """Create joints based on attributes values and guides. (without positioning as this point). """
        self.joints_list = []
        parent_tag = None
        for index in range(self.joint_count_attr.value):
            joint = self.add_joint(
                name="{0}".format(str(index).zfill(4)),
                skinning_jnt=True,
                tag_parent_jnt=parent_tag,
                radius=0.5,
            )
            parent_tag = joint
            self.joints_list.append(joint)

    def ctrls_creation(self):
        """Create controls based on attributes values, guides and joints. (without positioning as this point). """
        ctrls_mult = self.ctrls_scale_attr.value * 3.5

        self.root_ctrl = self.add_ctrl(name="root", size=2.0 * ctrls_mult)
        self.tip_ctrl = self.add_ctrl(name="tip", size=2.0 * ctrls_mult)

        for ctrl in [self.root_ctrl, self.tip_ctrl]:
            for attr in ["scaleY", "scaleZ"]:
                ctrl.add_locked_hidden_attr(attr)

        self.root_secondary_ctrl = None
        self.tip_secondary_ctrl = None
        if self.secondary_ctrls_attr.value:

            self.root_secondary_ctrl = self.add_ctrl(name="root_secondary", size=1.8 * ctrls_mult)
            self.root_secondary_ctrl.color = SECONDARY_COLOR

            self.tip_secondary_ctrl = self.add_ctrl(name="tip_secondary", size=1.8 * ctrls_mult)
            self.tip_secondary_ctrl.color = SECONDARY_COLOR

            for attr in ["scaleX", "scaleY", "scaleZ"]:
                for ctrl in [self.root_secondary_ctrl, self.tip_secondary_ctrl]:
                    ctrl.add_locked_hidden_attr(attr)

    def rig_creation(self):
        """Based on attributes value, guides (which now you can get global position from) joints and controls
        created in their methods you can build the rig.
        """
        if self.is_mirrored:
            self.module_grp.set_attr("scaleX", -1)

        grps = create_grps(self, ["input_root_grp", "input_tip_grp", "output_root_grp", "output_tip_grp"])
        input_root_grp, input_tip_grp, output_root_grp, output_tip_grp = grps

        jnts_grp, ctrls_grp, data_grp = create_grps(self, ["jnts_grp", "ctrls_grp", "data_grp"])

        data_grp.set_visibility(False)

        self.root_driven_attr.set_maya_object(input_root_grp)
        self.tip_driven_attr.set_maya_object(input_tip_grp)
        self.driver_root_attr.set_maya_object(output_root_grp)
        self.driver_tip_attr.set_maya_object(output_tip_grp)

        root_ctrl = self.root_ctrl.pointer
        root_jnt = self.joints_list[0].pointer
        tip_ctrl = self.tip_ctrl.pointer
        tip_jnt = self.joints_list[-1].pointer

        jnts_grp.set_matrix(self.guides_list[0].world_transformations["matrix"], space="world")
        mc.makeIdentity(jnts_grp, scale=True)

        # position joints.
        parent = jnts_grp
        for guide, jnt_info, in zip(self.guides_list, self.joints_list):
            jnt = jnt_info.pointer

            jnt.parent_relative(parent)
            jnt.set_matrix(guide.world_transformations["matrix"], space="world")
            jnt.freeze_transformations()
            parent = jnt

        # create ik handle.
        ik_handle_grp = IoTransform(name="{0}_ikHandle_grp".format(self.name))
        ik_handle_grp.parent_relative(data_grp)
        ik_handle_grp.match_transformation_to(tip_jnt)

        mc.select(clear=True)
        ik_handle, _ = mc.ikHandle(
            name="{0}_ikHandle".format(self.name),
            solver="ikSCsolver",
            startJoint=root_jnt,
            endEffector=tip_jnt,
        )
        tag_as_dont_tag(mc.ikHandle(ik_handle, q=True, solver=True))

        # fix for a bug in Maya IkHandle on joints that are mirrored.
        mc.dgdirty(ik_handle)
        root_jnt.set_attr("rotateX", 0)
        root_jnt.set_attr("rotateY", 0)
        root_jnt.set_attr("rotateZ", 0)

        ik_handle_obj = IoTransform(name=ik_handle, existing=True)
        ik_handle_obj.parent(ik_handle_grp)
        mc.hide(ik_handle)

        # ctrls positioning.
        secondary_ctrls_setup([self.root_ctrl, self.tip_ctrl], [self.root_secondary_ctrl, self.tip_secondary_ctrl])

        root_ctrl.offset_grp.parent_relative(ctrls_grp)
        tip_ctrl.offset_grp.parent_relative(ctrls_grp)

        ctrls_grp.match_translation_to(root_jnt)
        world_rotation(
            ctrls_grp,
            self.world_orientation_attr.display_value,
            flip_x_direction=False,
            twist=self.world_twist_attr.value,
        )

        tip_ctrl.offset_grp.set_attr("translateY", self.get_chain_distance(self.guides_list))

        if self.clean_transformations_attr.value:
            root_ctrl.offset_grp.match_transformation_to(root_jnt)
            tip_ctrl.offset_grp.match_transformation_to(tip_jnt)
        else:
            root_ctrl.match_transformation_to(root_jnt)
            tip_ctrl.match_transformation_to(tip_jnt)

        root_ctrl.scale_attrs_connect()

        tip_ctrl_scale_offset = IoTransform("{0}_scale_offset_grp".format(tip_ctrl.short_name))
        tip_ctrl_scale_offset.parent_relative(root_ctrl.btm_ctrl)
        tip_ctrl.offset_grp.parent(tip_ctrl_scale_offset)

        tip_ctrl.scale_attrs_connect()

        if self.expose_rotation_order_attr.value:
            expose_rotation_order(
                [self.root_ctrl, self.tip_ctrl, self.root_secondary_ctrl, self.tip_secondary_ctrl]
            )

        # constraints.
        matrix_constraint(root_ctrl.btm_ctrl, root_jnt, maintain_offset=False)
        matrix_constraint(tip_ctrl.btm_ctrl, ik_handle_grp, maintain_offset=True)
        matrix_constraint(  # scale constraint.
            tip_ctrl.btm_ctrl,
            tip_jnt,
            maintain_offset=True,
            skip_attrs=(True, True, True, True, True, True, False, False, False),
        )

        # input/output grps.
        matrix_constraint(root_jnt, output_root_grp, maintain_offset=False)
        matrix_constraint(tip_jnt, output_tip_grp, maintain_offset=False)

        input_root_grp.match_transformation_to(ctrls_grp)
        matrix_constraint(input_root_grp, ctrls_grp, maintain_offset=True)

        input_tip_grp.match_transformation_to(ctrls_grp)
        matrix_constraint(
            input_tip_grp,
            tip_ctrl_scale_offset,
            maintain_offset=True,
            skip_attrs=(False, False, False, False, False, False, True, True, True),
        )

    @staticmethod
    def get_chain_distance(guides):
        """Return a float distance of all guides.

        Arguments:
            guides {list} -- of guides to measure
        """
        distance_total = 0.0
        parent_pos = guides[0].world_transformations["translate"]
        for guide in guides[1:]:
            distance_total += distance_between(parent_pos, guide.world_transformations["translate"])
            parent_pos = guide.world_transformations["translate"]

        return distance_total
