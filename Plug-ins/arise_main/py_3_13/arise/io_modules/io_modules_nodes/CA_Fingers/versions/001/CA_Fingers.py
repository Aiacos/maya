"""Cartoon_A_Spine module creates a cartoon_complex spine module. """

import math

import maya.cmds as mc

from arise.data_types import node_data
from arise.utils import math_utils
from arise.utils.matrix_utils import matrix_constraint
from arise.utils.modules_utils import (
    world_rotation, expose_rotation_order, create_grps, update_ctrls, ADD_DL, MULT_DL, MULT_DL_INPUT1,
    MULT_DL_INPUT2,
)

MAYA_VERSION = 2016  # the version of Maya from which this module supports.
AUTHOR = "Etay Herz"  # name of person who created this module.
RIG_CATEGORY = "Cartoon"  # either 'Basic', 'Cartoon', 'Vfx', 'Game' or 'All'. (used when filtering).
RIG_TYPE = "Biped"  # Biped, Car, Quadruped, All, ... (for filtering modules in lists).
TAGS = ["cartoon", "complex", "advance", "finger", "hand", "digits", "arm", "palm",]
TOOL_TIP = "Cartoon fingers (digits). Features include fingers and thumbs behavior, master ctrl and more."

node_data.NodeData.update_ctrls = update_ctrls


class CA_Fingers(node_data.NodeData):
    """Cartoon_A_Fingers module creates a cartoon_complex fingers module. """
    sort_priority = 100

    def __init__(self, parent, docs, icon, module_dict):
        node_data.NodeData.__init__(
            self,
            parent=parent,
            icon=icon,
            docs=docs,
            module_dict=module_dict
        )

        self.body_part = "fingers"

    def attributes_creation(self):
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
            default_value=False,
            annotation=(
                "If checked, the zeroed pose will be the same as the bind pose;\n"
                "if unchecked, when zeroing the ctrls, they will align with a world axis "
                "specified in the following two attributes."
            ),
            help_link="https://youtu.be/-1fpRw6oJME?t=61",
        )
        self.rest_orient_guide_attr = self.add_boolean_attribute(
            name="Along Direction Guide",
            default_value=True,
            annotation="Each finger has a direction guide, the zeroed pose will be along their direction.",
        )

        self.add_collapsible_layout(title="World Orientation", shown=False)
        items = ["+X", "+Y", "+Z", "-X", "-Y", "-Z"]
        self.world_orientation_attr = self.add_radio_attribute(
            name="World Orientation",
            items=items,
            default_value=items.index("+X"),
            annotation=(
                "The world axis the ctrls will align with when zeroed.\n"
                "Usually, this attribute's default value is the correct value."
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

        self.add_separator()
        self.fingers_count_attr = self.add_integer_attribute(
            name="Fingers Count",
            default_value=4,
            dynamic_attribute=False,
            writable=True,
            readable=True,
            promoted=False,
            annotation="Number of fingers to create (default is 4).",
            min_value=1,
            max_value=50,
            add_slider=False,
        )
        self.fingers_jnts_count_attr = self.add_integer_attribute(
            name="Fingers Jnts Count",
            default_value=5,
            dynamic_attribute=False,
            writable=True,
            readable=True,
            promoted=False,
            annotation="Number of joints/guides per finger (default is 5); includes metacarpal joint.",
            min_value=3,
            max_value=10,
            add_slider=False,
        )

        self.thumb_count_attr = self.add_integer_attribute(
            name="Thumbs Count",
            default_value=1,
            dynamic_attribute=False,
            writable=True,
            readable=True,
            promoted=False,
            annotation="Number of thumbs to create (default is 1). Thumbs behave differently than fingers.",
            min_value=0,
            max_value=50,
            add_slider=False,
        )
        self.thumb_jnts_count_attr = self.add_integer_attribute(
            name="Thumbs Jnts Count",
            default_value=4,
            dynamic_attribute=False,
            writable=True,
            readable=True,
            promoted=False,
            annotation="Number of joints/guides per thumb (default is 4).",
            min_value=3,
            max_value=10,
            add_slider=False,
        )
        self.translate_ctrls_attr = self.add_boolean_attribute(
            name="Ctrls Translate",
            default_value=False,
            annotation="If checked, animators will also be able to translate the FK ctrls.",
        )
        self.scale_fix_attr = self.add_boolean_attribute(
            name="Scale Fix Jnts",
            default_value=False,
            annotation=(
                "Add extra skinning joints that do not scale with their ctrl, "
                "this prevents scaling vertices behind the joint in the wrong direction."
            ),
        )

        self.master_ctrl_attr = self.add_boolean_attribute(
            name="Master Ctrl",
            default_value=True,
            annotation="Create a master control that animates all the fingers when rotated and scaled.",
        )
        self.master_ctrl_offset_attr = self.add_xyz_attribute(
            name="Master Ctrl Offset",
            default_value=[0, 10, 0],
            dynamic_attribute=False,
            writable=True,
            readable=True,
            promoted=False,
            annotation="Position offset of the 'master_ctrl'.\nMultiplied by attribute 'Ctrls Scale'.",
        )

        ### connections.
        self.add_separator(title="Connections")
        self.driven_root_attr = self.add_driven_attribute(name="Root Input", annotation="Input")
        self.driver_root_attr = self.add_driver_attribute(name="Root Output", annotation="Output")

        self.close_layout()

    def evaluate_creation_methods(self):  # REIMPLEMENTED!
        """Reimplemented to enable/disable attrs. """
        disable = True if self.clean_transformations_attr.value else False
        self.rest_orient_guide_attr.set_disabled(disable)
        self.world_orientation_attr.set_disabled(disable or self.rest_orient_guide_attr.value)
        self.master_ctrl_offset_attr.set_disabled(False if self.master_ctrl_attr.value else True)

        node_data.NodeData.evaluate_creation_methods(self)

    def guides_creation(self):
        """Create guides based on attributes values. """
        self.sub_guide = self.add_guide(name="sub_parent", translation=[72, 140, 0])
        self.sub_guide.shape = "circle_half_closed"
        self.sub_guide.rotate_offset = [0, 90, 0]

        self.fingers_direction_guides = []
        self.fingers_guides_list = []
        for finger_index in range(self.fingers_count_attr.value):

            pos = [75, 140, 1 - (finger_index)*2]
            side_rotation = (0, 0, 90)
            side_pin_guide = None
            parent = self.sub_guide
            finger_list = []
            for jnt_index in range(self.fingers_jnts_count_attr.value):
                finger_guide = self.add_aim_guide(
                    name="finger_{0}_{1}".format(finger_index+1, jnt_index+1),
                    translation=pos,
                    parent=parent,
                    side_pin_rotation=side_rotation,
                    side_pin_guide=side_pin_guide if self.guides_up_shared_attr.value else None,
                )
                finger_guide.size = finger_guide.size / 8.0

                if side_pin_guide is None:
                    side_pin_guide = finger_guide

                pos = [pos[0]+2.5, pos[1], pos[2]]
                finger_list.append(finger_guide)
                parent = finger_guide
                side_rotation = (0, 0, 0)

            # aim finger guides at each other.
            for index, guide in enumerate(finger_list[:-1]):
                guide.aim_at = finger_list[index+1]

            finger_list[-1].aim_at = finger_list[-2]
            finger_list[-1].aim_rotation_offset = [180, 0, 0]

            # create direction guide per finger.
            direction_guide = self.add_direction_guide(
                name="finger_{0}_direction".format(finger_index+1),
                position_guide=finger_list[1],
                offset=(2, 0, 0),
            )
            direction_guide.rotation_follow = True

            self.fingers_direction_guides.append(direction_guide)
            self.fingers_guides_list.append(finger_list)

        # thumbs guides.
        self.thumbs_direction_guides = []
        self.thumbs_guides_list = []
        for thumb_index in range(self.thumb_count_attr.value):

            pos = [75, 140, 3 + (thumb_index)*2]
            side_rotation = (0, 0, 90)
            side_pin_guide = None
            parent = self.sub_guide
            thumb_list = []
            for jnt_index in range(self.thumb_jnts_count_attr.value):
                thumb_guide = self.add_aim_guide(
                    name="thumb_{0}_{1}".format(thumb_index+1, jnt_index+1),
                    translation=pos,
                    parent=parent,
                    side_pin_rotation=side_rotation,
                    side_pin_guide=side_pin_guide if self.guides_up_shared_attr.value else None,
                )
                thumb_guide.size = thumb_guide.size / 7.0

                if side_pin_guide is None:
                    side_pin_guide = thumb_guide

                pos = [pos[0]+2.5, pos[1], pos[2]]
                thumb_list.append(thumb_guide)
                parent = thumb_guide
                side_rotation = (0, 0, 0)

            # aim finger guides at each other.
            for index, guide in enumerate(thumb_list[:-1]):
                guide.aim_at = thumb_list[index+1]

            thumb_list[-1].aim_at = thumb_list[-2]
            thumb_list[-1].aim_rotation_offset = [180, 0, 0]

            # create direction guide per thumb.
            direction_guide = self.add_direction_guide(
                name="thumb_{0}_direction".format(thumb_index+1),
                position_guide=thumb_list[1],
                offset=(2, 0, 0),
            )
            # direction_guide.rotation = (0, 180, -90)
            direction_guide.rotation_follow = True

            self.thumbs_direction_guides.append(direction_guide)
            self.thumbs_guides_list.append(thumb_list)

    def joints_creation(self):
        """Create joints based on attributes values and guides. (without positioning as this point). """
        # fingers jnts.
        self.fingers_jnts_list = []
        self.fingers_scale_fix_jnts = []
        for finger_index in range(self.fingers_count_attr.value):
            finger_list = []
            parent_tag = None
            for jnt_index in range(self.fingers_jnts_count_attr.value):
                finger_jnt = self.add_joint(
                    name="finger_{0}_{1}".format(finger_index, jnt_index),
                    skinning_jnt=True,
                    tag_parent_jnt=parent_tag,
                    radius=0.4,
                )
                parent_tag = finger_jnt
                finger_list.append(finger_jnt)

            finger_list[-1].skinning_jnt = False
            self.fingers_jnts_list.append(finger_list)

            # fingers scale fix jnts.
            if self.scale_fix_attr.value:
                finger_scale_fix_list = []
                for jnt_index, _ in enumerate(finger_list[1:-1], 1):
                    scale_fix_jnt = self.add_joint(
                        name="finger_{0}_{1}_scale_fix".format(finger_index, jnt_index),
                        skinning_jnt=True,
                        tag_parent_jnt=finger_list[jnt_index-1],
                        radius=0.25,
                    )
                    finger_scale_fix_list.append(scale_fix_jnt)

                self.fingers_scale_fix_jnts.append(finger_scale_fix_list)

        # thumb jnts.
        self.thumbs_jnts_list = []
        self.thumb_scale_fix_jnts = []
        for thumb_index in range(self.thumb_count_attr.value):
            thumb_list = []
            parent_tag = None
            for jnt_index in range(self.thumb_jnts_count_attr.value):
                thumb_jnt = self.add_joint(
                    name="thumb_{0}_{1}".format(thumb_index, jnt_index),
                    skinning_jnt=True,
                    tag_parent_jnt=parent_tag,
                    radius=0.4,
                )
                parent_tag = thumb_jnt
                thumb_list.append(thumb_jnt)

            thumb_list[-1].skinning_jnt = False
            self.thumbs_jnts_list.append(thumb_list)

            # fingers scale fix jnts.
            if self.scale_fix_attr.value:
                thumb_scale_fix_list = []
                for jnt_index, _ in enumerate(thumb_list[1:-1], 1):
                    scale_fix_jnt = self.add_joint(
                        name="thumb_{0}_scale_fix_{1}".format(thumb_index, jnt_index),
                        skinning_jnt=True,
                        tag_parent_jnt=thumb_list[jnt_index-1],
                        radius=0.25,
                    )
                    thumb_scale_fix_list.append(scale_fix_jnt)

                self.thumb_scale_fix_jnts.append(thumb_scale_fix_list)

        # humanIK definition.
        if self.thumbs_jnts_list:
            thumb_tags = ["*HandThumb{0}".format(index) for index in range(1, 5)]
            for jnt, tag in zip(self.thumbs_jnts_list[0], thumb_tags):
                jnt.human_ik = tag

        fingers_tags_lists = [
            ["*InHandIndex"] + ["*HandIndex{0}".format(index) for index in range(1, 5)],
            ["*InHandMiddle"] + ["*HandMiddle{0}".format(index) for index in range(1, 5)],
            ["*InHandRing"] + ["*HandRing{0}".format(index) for index in range(1, 5)],
            ["*InHandPinky"] + ["*HandPinky{0}".format(index) for index in range(1, 5)],
            ["*InHandExtraFinger"] + ["*HandExtraFinger{0}".format(index) for index in range(1, 5)],
        ]

        for jnts_list, tags_list in zip(self.fingers_jnts_list, fingers_tags_lists):
            for jnt, tag in zip(jnts_list, tags_list):
                jnt.human_ik = tag

    def ctrls_creation(self):
        """Create controls based on attributes values, guides and joints. (without positioning as this point). """
        scale_mult = self.ctrls_scale_attr.value * 2.0

        # master ctrl.
        self.master_ctrl = None
        if self.master_ctrl_attr.value:
            size = (2.0 * scale_mult, 2.0 * scale_mult, 3.5 * scale_mult)
            self.master_ctrl = self.add_ctrl(name="master", shape="arch", up_orient="+Y", size=size)
            self.master_ctrl.translate_offset = [val * scale_mult for val in self.master_ctrl_offset_attr.value]
            self.master_ctrl.rotate_offset = [0, 90, 0]

            for attr in ["translateX", "translateY", "translateZ", "scaleX", "scaleY"]:
                self.master_ctrl.add_locked_hidden_attr(attr)

        # fingers ctrls.
        self.fingers_ctrls = []
        for finger_index in range(self.fingers_count_attr.value):
            root_ctrl = self.add_ctrl(
                name="finger_{0}_0".format(finger_index),
                shape="pin_circle",
                up_orient="+X",
                size=(0.8 * scale_mult),
            )
            finger_list = [root_ctrl]

            for jnt_index in range(self.fingers_jnts_count_attr.value)[1:-1]:
                ctrl = self.add_ctrl(
                    name="finger_{0}_{1}".format(finger_index, jnt_index),
                    shape="circle",
                    size=(0.6 * scale_mult),
                )
                finger_list.append(ctrl)

            if not self.translate_ctrls_attr.value:
                for ctrl in finger_list:
                    for attr in ["translateX", "translateY", "translateZ"]:
                        ctrl.add_locked_hidden_attr(attr)

            self.fingers_ctrls.append(finger_list)

        # thumbs ctrls.
        self.thumbs_ctrls = []
        for thumb_index in range(self.thumb_count_attr.value):
            root_ctrl = self.add_ctrl(
                name="thumb_{0}_0".format(thumb_index),
                shape="pin_circle",
                up_orient="+X",
                size=(0.8 * scale_mult),
            )
            thumb_list = [root_ctrl]

            for jnt_index in range(self.thumb_jnts_count_attr.value)[1:-1]:
                ctrl = self.add_ctrl(
                    name="thumb_{0}_{1}".format(thumb_index, jnt_index),
                    shape="circle",
                    size=(0.6 * scale_mult),
                )
                thumb_list.append(ctrl)

            if not self.translate_ctrls_attr.value:
                for ctrl in thumb_list:
                    for attr in ["translateX", "translateY", "translateZ"]:
                        ctrl.add_locked_hidden_attr(attr)

            self.thumbs_ctrls.append(thumb_list)

    def maya_attrs_creation(self):
        """Declare any Maya attributes that users should be able to modify. """
        if self.master_ctrl:
            self.master_ctrl.add_maya_attr("thumbs_mult", attr_type="float", default_value=0.3, min=-2, max=2)
            self.master_ctrl.add_maya_attr(name="fingers_root_ctrls", attr_type="bool", default_value=True)
            self.master_ctrl.add_maya_attr(name="thumbs_root_ctrls", attr_type="bool", default_value=True)

    def rig_creation(self):
        """Based on attributes value, guides (which now you can get global position from) joints and controls
        created in their methods you can build the rig.
        """
        if self.is_mirrored:
            self.module_grp.set_attr("scaleX", -1)

        grps = create_grps(self, ["input_root_grp", "output_root_grp"])
        input_root_grp, output_root_grp = grps

        self.driven_root_attr.set_maya_object(input_root_grp)
        self.driver_root_attr.set_maya_object(output_root_grp)

        self.ctrls_grp, self.jnts_grp = create_grps(self, ["ctrls_grp", "jnts_grp"])

        middle_finger_index = int(math.ceil(len(self.fingers_guides_list) / 2.0) - 1)
        middle_finger_matrix = self.fingers_guides_list[middle_finger_index][0].world_transformations["matrix"]
        for grp in [self.ctrls_grp, self.jnts_grp]:
            grp.set_matrix(middle_finger_matrix)
            grp.set_attr("scale", (1, 1, 1))

        # position fingers and thumbs jnts.
        fingers_lists = (self.fingers_guides_list, self.fingers_jnts_list, self.fingers_scale_fix_jnts)
        thumbs_lists = (self.thumbs_guides_list, self.thumbs_jnts_list, self.thumb_scale_fix_jnts)
        for lists in [fingers_lists, thumbs_lists]:
            for chain_guides, chain_jnts in zip(*lists[:-1]):
                parent = self.jnts_grp
                for guide, jnt in zip(chain_guides, chain_jnts):
                    jnt = jnt.pointer
                    jnt.parent_relative(parent)
                    jnt.set_matrix(guide.world_transformations["matrix"])
                    jnt.freeze_transformations()
                    jnt.add_joint_orient()
                    parent = jnt

            if lists[-1]:
                for finger_jnts, fingers_scale_jnts in zip(*lists[1:]):
                    parent = finger_jnts[0].pointer
                    for jnt, scale_jnt in zip(finger_jnts[1:-1], fingers_scale_jnts):
                        scale_jnt = scale_jnt.pointer
                        jnt = jnt.pointer
                        scale_jnt.parent_relative(parent)
                        scale_jnt.match_transformation_to(jnt)
                        scale_jnt.freeze_transformations()
                        scale_jnt.parent_constraint_to(jnt, maintainOffset=False)
                        parent = jnt

        # position ctrls.
        fingers_lists = (self.fingers_ctrls, self.fingers_direction_guides, self.fingers_jnts_list)
        thumbs_lists = (self.thumbs_ctrls, self.thumbs_direction_guides, self.thumbs_jnts_list)
        for lists in [fingers_lists, thumbs_lists]:
            for chain_ctrls, direction_guide, chain_jnts in zip(*lists):
                chain_jnts = [jnt.pointer for jnt in chain_jnts]
                chain_ctrls = [ctrl.pointer for ctrl in chain_ctrls]
                distances = self.get_chain_distance_list(chain_jnts[1:])

                chain_ctrls[0].offset_grp.parent_relative(self.ctrls_grp)
                chain_ctrls[0].offset_grp.set_matrix(chain_jnts[0].get_matrix())

                if self.clean_transformations_attr.value is False and self.rest_orient_guide_attr.value is True:
                    # when mirrored I can't simply get the rotation and apply to ctrl - must apply matrix.
                    chain_ctrls[1].offset_grp.set_matrix(direction_guide.world_transformations["matrix"])
                else:
                    world_rotation(
                        obj=chain_ctrls[1].offset_grp,
                        aim_direction=self.world_orientation_attr.display_value,
                        flip_x_direction=True,
                    )

                chain_ctrls[1].offset_grp.set_attr("scale", (1, 1, 1))
                chain_ctrls[1].offset_grp.match_translation_to(chain_jnts[1])
                chain_ctrls[1].offset_grp.parent(chain_ctrls[0])

                parent = chain_ctrls[1]
                for ctrl, distance in zip(chain_ctrls[2:], distances):
                    ctrl.offset_grp.parent_relative(parent)
                    ctrl.offset_grp.set_attr("translateY", distance)
                    parent = ctrl

                if self.clean_transformations_attr.value is True:
                    for ctrl, jnt in zip(chain_ctrls[1:], chain_jnts[1:-1]):
                        ctrl.offset_grp.match_transformation_to(jnt)

                else:
                    for ctrl, jnt in zip(chain_ctrls[1:], chain_jnts[1:-1]):
                        ctrl.match_transformation_to(jnt)

                # constrain jnts to ctrls.
                parent_ctrl = chain_ctrls[0]
                parent_jnt = chain_jnts[0]
                for ctrl, jnt in zip(chain_ctrls[1:], chain_jnts[1:-1]):
                    self.constrain_jnt_to_ctrl(parent_ctrl, parent_jnt, ctrl)
                    parent_ctrl = ctrl
                    parent_jnt = jnt

                matrix_constraint(driver=chain_ctrls[-1], driven=chain_jnts[-2], maintain_offset=False)

                if self.expose_rotation_order_attr.value:
                    expose_rotation_order(chain_ctrls)

        # ctrls chain attrs.
        for chain_ctrls in self.fingers_ctrls + self.thumbs_ctrls:
            chain_ctrls = [ctrl.pointer for ctrl in chain_ctrls]

            local_grps = []
            for ctrl in chain_ctrls:
                ctrl.add_group_above("{0}_manual_corrections_grp".format(ctrl.short_name))  # for users fixes.
                local_grps.append(ctrl.add_group_above("{0}_local_grp".format(ctrl.short_name)))

            chain_ctrls[1].add_spacer_attr()
            root_rotate_attr = chain_ctrls[1].add_attr("root_spread", dv=0, keyable=True)
            root_cup_attr = chain_ctrls[1].add_attr("root_cup", dv=0, keyable=True)
            curl_attr = chain_ctrls[1].add_attr("curl", dv=0, keyable=True)

            local_grps[0].connect_attr("rotateZ", root_cup_attr)
            local_grps[0].connect_attr("rotateX", root_rotate_attr)

            for grp in local_grps[1:]:
                grp.connect_attr("rotateZ", curl_attr)

        self.master_ctrl_setup()

        input_root_grp.match_transformation_to(self.ctrls_grp)
        matrix_constraint(driver=input_root_grp, driven=self.ctrls_grp, maintain_offset=True)
        matrix_constraint(driver=input_root_grp, driven=output_root_grp, maintain_offset=False)

    def master_ctrl_setup(self):
        """Position and connect master ctrl. """
        # TODO: clean the code in this method and in this node/module.
        if not self.master_ctrl:
            return

        master_ctrl = self.master_ctrl.pointer
        master_ctrl.offset_grp.parent_relative(self.ctrls_grp)
        master_ctrl.set_attr("rotateOrder", 1)

        master_ctrl.add_spacer_attr()
        relax_attr = master_ctrl.add_attr("fingers_relax", min=-10, max=10, dv=0, keyable=True)
        spread_attr = master_ctrl.add_attr("roots_spread", dv=0, k=True)
        master_ctrl.add_spacer_attr()
        thumb_mult_attr = master_ctrl.add_attr("thumbs_mult", min=-2, max=2, dv=0.3, keyable=True)
        master_ctrl.add_spacer_attr()
        finger_ctrls_attr = master_ctrl.add_attr("fingers_root_ctrls", at="bool", k=True, dv=1)
        thumbs_ctrls_attr = master_ctrl.add_attr("thumbs_root_ctrls", at="bool", k=True, dv=1)

        for ctrl in self.fingers_ctrls:
            for shape in ctrl[0].pointer.get_shapes():
                mc.connectAttr(finger_ctrls_attr, "{0}.visibility".format(shape))

        for ctrl in self.thumbs_ctrls:
            for shape in ctrl[0].pointer.get_shapes():
                mc.connectAttr(thumbs_ctrls_attr, "{0}.visibility".format(shape))

        fingers_grps = [[], []]
        thumbs_grps = [[], []]
        # TODO: can clean this code by instead of using fingers_grps and thumbs_grps, store the grps in the ctrl.
        for ctrls, global_grps in [(self.fingers_ctrls, fingers_grps), (self.thumbs_ctrls, thumbs_grps)]:
            for chain_ctrls in ctrls:
                grps_1, grps_2 = [], []
                for ctrl in chain_ctrls:
                    ctrl = ctrl.pointer
                    grps_1.append(ctrl.add_group_above("{0}_global_1_grp".format(ctrl.short_name)))
                    grps_2.append(ctrl.add_group_above("{0}_global_2_grp".format(ctrl.short_name)))

                global_grps[0].append(grps_1)
                global_grps[1].append(grps_2)

        for finger_ctrls in self.fingers_ctrls:
            for ctrl in finger_ctrls:
                ctrl = ctrl.pointer
                ctrl.relax_grp = ctrl.add_group_above("{0}_relax_grp".format(ctrl.short_name))

        damp_multi = mc.createNode(MULT_DL, n="{0}_damp".format(master_ctrl.short_name))
        mc.connectAttr(master_ctrl.attr("rotateZ"), "{0}.{1}".format(damp_multi, MULT_DL_INPUT1))
        mc.connectAttr(thumb_mult_attr, "{0}.{1}".format(damp_multi, MULT_DL_INPUT2))

        for chain_grps in fingers_grps[0]:
            chain_grps[1].connect_attr("rotateX", master_ctrl.attr("rotateX"))

            for grp in chain_grps[1:]:
                grp.connect_attr("rotateZ", master_ctrl.attr("rotateZ"))

        for chain_grps in thumbs_grps[0]:
            for grp in chain_grps[1:]:
                grp.connect_attr("rotateZ", "{0}.output".format(damp_multi))

        # analyze fingers grp.
        half_int = int(len(fingers_grps[1]) // 2.0)
        first_half = fingers_grps[1][0:half_int]
        first_half.reverse()

        if (len(fingers_grps[1]) % 2) != 0:
            second_half = fingers_grps[1][half_int+1:]
        else:
            second_half = fingers_grps[1][half_int:]

        scale_minus = mc.createNode(ADD_DL, n="{0}_scale_minus_one".format(master_ctrl.short_name))
        mc.connectAttr(master_ctrl.attr("scaleZ"), "{0}.input1".format(scale_minus))
        mc.setAttr("{0}.input2".format(scale_minus), -1)

        reverse_node = mc.createNode(MULT_DL, n="{0}_rotate_y_reverse".format(master_ctrl.short_name))
        mc.connectAttr(master_ctrl.attr("rotateY"), "{0}.{1}".format(reverse_node, MULT_DL_INPUT1))
        mc.setAttr("{0}.{1}".format(reverse_node, MULT_DL_INPUT2), -1)

        # spread fingers. (both root_spread attr and master_ctrl scale spread).
        value = -5.0
        add_value = -10.0
        for index, minus_chain in enumerate(first_half):
            for attr, grp in [("{0}.output".format(scale_minus), minus_chain[1]), (spread_attr, minus_chain[0])]:
                spread_multi = mc.createNode(MULT_DL, n="{0}_spread".format(grp.short_name))
                mc.connectAttr(attr, "{0}.{1}".format(spread_multi, MULT_DL_INPUT1))
                mc.setAttr("{0}.{1}".format(spread_multi, MULT_DL_INPUT2), value + (add_value * index))
                grp.connect_attr("rotateX", "{0}.output".format(spread_multi))

        for index, minus_chain in enumerate(thumbs_grps[1]):
            grp = minus_chain[1]
            spread_multi = mc.createNode(MULT_DL, n="{0}_spread".format(grp.short_name))
            mc.connectAttr("{0}.output".format(scale_minus), "{0}.{1}".format(spread_multi, MULT_DL_INPUT1))
            mc.setAttr("{0}.{1}".format(spread_multi, MULT_DL_INPUT2), value + (add_value * index))

            thumb_damp_multi = mc.createNode(MULT_DL, n="{0}_damp".format(grp.short_name))
            mc.connectAttr("{0}.output".format(spread_multi), "{0}.{1}".format(thumb_damp_multi, MULT_DL_INPUT1))
            mc.connectAttr(thumb_mult_attr, "{0}.{1}".format(thumb_damp_multi, MULT_DL_INPUT2))
            grp.connect_attr("rotateX", "{0}.output".format(thumb_damp_multi))

        value = 5.0
        add_value = 10.0
        for index, plus_chain in enumerate(second_half):
            for attr, grp in [("{0}.output".format(scale_minus), plus_chain[1]), (spread_attr, plus_chain[0])]:
                spread_multi = mc.createNode(MULT_DL, n="{0}_spread".format(grp.short_name))
                mc.connectAttr(attr, "{0}.{1}".format(spread_multi, MULT_DL_INPUT1))
                mc.setAttr("{0}.{1}".format(spread_multi, MULT_DL_INPUT2), value + (add_value * index))
                grp.connect_attr("rotateX", "{0}.output".format(spread_multi))

        # curl bias.
        multiplyer = -0.5
        for minus_chain in first_half:
            cup_multi = mc.createNode(MULT_DL, n="{0}_cup_bias".format(minus_chain[1].short_name))
            mc.connectAttr("{0}.output".format(reverse_node), "{0}.{1}".format(cup_multi, MULT_DL_INPUT1))
            mc.setAttr("{0}.{1}".format(cup_multi, MULT_DL_INPUT2), multiplyer)
            minus_chain[1].connect_attr("rotateZ", "{0}.output".format(cup_multi))

            root_multi = mc.createNode(MULT_DL, n="{0}_cup_bias".format(minus_chain[0].short_name))
            mc.connectAttr("{0}.output".format(reverse_node), "{0}.{1}".format(root_multi, MULT_DL_INPUT1))
            mc.setAttr("{0}.{1}".format(root_multi, MULT_DL_INPUT2), multiplyer * 0.35)
            minus_chain[0].connect_attr("rotateZ", "{0}.output".format(root_multi))

            multiplyer -= 1

        multiplyer = 0.5
        for plus_chain in second_half:
            cup_multi = mc.createNode(MULT_DL, n="{0}_cup_bias".format(plus_chain[1].short_name))
            mc.connectAttr("{0}.output".format(reverse_node), "{0}.{1}".format(cup_multi, MULT_DL_INPUT1))
            mc.setAttr("{0}.{1}".format(cup_multi, MULT_DL_INPUT2), multiplyer)
            plus_chain[1].connect_attr("rotateZ", "{0}.output".format(cup_multi))

            root_multi = mc.createNode(MULT_DL, n="{0}_cup_bias".format(plus_chain[0].short_name))
            mc.connectAttr("{0}.output".format(reverse_node), "{0}.{1}".format(root_multi, MULT_DL_INPUT1))
            mc.setAttr("{0}.{1}".format(root_multi, MULT_DL_INPUT2), multiplyer * 0.35)
            plus_chain[0].connect_attr("rotateZ", "{0}.output".format(root_multi))

            multiplyer += 1

        # relax.
        fingers_count = len(self.fingers_ctrls)
        for index, finger_ctrls in enumerate(self.fingers_ctrls):
            remap_node = mc.createNode("remapValue", n="{0}_finger_{1}_relax".format(self.name, index))
            mc.setAttr("{0}.inputMin".format(remap_node), -5.0)
            mc.setAttr("{0}.inputMax".format(remap_node), 5.0)
            mc.setAttr("{0}.outputMin".format(remap_node), 90.0)
            mc.setAttr("{0}.outputMax".format(remap_node), -90.0)

            value = (0.4 / fingers_count) * (index+1)
            mc.setAttr("{0}.value[0].value_Position".format(remap_node), 0.0)
            mc.setAttr("{0}.value[0].value_FloatValue".format(remap_node), value)
            mc.setAttr("{0}.value[0].value_Interp".format(remap_node), 3)  # spline.

            mc.setAttr("{0}.value[1].value_Position".format(remap_node), 0.5)
            mc.setAttr("{0}.value[1].value_FloatValue".format(remap_node), 0.5)
            mc.setAttr("{0}.value[1].value_Interp".format(remap_node), 3)  # spline.

            mc.setAttr("{0}.value[2].value_Position".format(remap_node), 1.0)
            mc.setAttr("{0}.value[2].value_FloatValue".format(remap_node), 0.5 - value)
            mc.setAttr("{0}.value[2].value_Interp".format(remap_node), 3)  # spline.

            mc.connectAttr(relax_attr, "{0}.inputValue".format(remap_node))

            for ctrl in finger_ctrls:
                ctrl.pointer.relax_grp.connect_attr("rotateZ", "{0}.outValue".format(remap_node))

    def constrain_jnt_to_ctrl(self, parent_ctrl, parent_jnt, next_ctrl):
        """Constrain jnt to ctrl based on values of attrs on node.

        Args:
            parent_ctrl (IoTransform): ctrl driver
            parent_jnt (IoJoint): to be driven
            next_ctrl (IoTransform): ctrl to aim at if it aim constraint
        """
        if self.translate_ctrls_attr.value is False:
            matrix_constraint(driver=parent_ctrl, driven=parent_jnt, maintain_offset=False)

        else:
            matrix_constraint(
                driver=parent_ctrl,
                driven=parent_jnt,
                maintain_offset=False,
                skip_attrs=[False, False, False, True, True, True, False, False, False],
                )

            mc.aimConstraint(
                next_ctrl,
                parent_jnt,
                aimVector=(0, 1, 0),
                upVector=(1, 0, 0),
                worldUpType="objectrotation",
                worldUpVector=(1, 0, 0),
                worldUpObject=parent_ctrl,
                maintainOffset=False,
                )

    @staticmethod
    def get_chain_distance_list(transforms):
        """Return a list of distances between transforms. return a list with same len as transforms-1.

        Args:
            transforms (list): of transforms names
        """
        distances_list = []
        pre_pos = transforms[0].get_translation()
        for item in transforms[1:]:
            distances_list.append(math_utils.distance_between(pre_pos, item.get_translation()))
            pre_pos = item.get_translation()

        return distances_list
