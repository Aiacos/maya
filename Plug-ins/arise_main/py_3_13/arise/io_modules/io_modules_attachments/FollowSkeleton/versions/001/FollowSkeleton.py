"""FollowSkeleton creates a joint chain where each joint is constraint to each of the node skinned joint.
this way the user can create a single chain rig of the whole character and transfer the skinning to it.
useful for game characters to bake anim to it, for transferring to other programs like Houdini and Bullet,
for pre-roll logic to avoid intersecting and for crowds. """

import logging

import maya.cmds as mc
from maya.api import OpenMaya as om

from arise.utils import matrix_utils
from arise.utils.modules_utils import JOINTS_VIS_ATTR
from arise.data_types.attachment_data import AttachmentData
from arise.utils.tagging_utils import get_maya_nodes_with_tag, SKELETON_GRP_NAME, ROOT_FOLDER_NAME

LOGGER = logging.getLogger("node_rig_logger")

MAYA_VERSION = 2016
AUTHOR = "Etay Herz"
RIG_TYPE = "Joints"
RIG_CATEGORY = "Build"
TAGS = ["crowd", "games", "pre roll", "single chain", "joint", "joints"]
TOOL_TIP = "Make your rig useable by other programs, such as game engines, by creating a single joint chain tree."

JOINTS_RADIUS = 3.0
FS_JNTS_COLOR = [0.5, 0.2, 0.0]

AXIS_OFFSETS = [
    [None, 0.0, 90.0],  # X
    [0.0, None, 0.0],  # Y
    [-90.0, None, 0.0],  # Z
    [None, 0.0, -90.0],  # -X
    [0.0, None, 180.0],  # -Y
    [90.0, None, 0.0],  # -Z
]


class FollowSkeleton(AttachmentData):
    """Here we will reimplement methods to 1) create attributes on the attachment
    2) create guides in the template module and 3) the rig method where the rig will be built.
    """
    sort_priority = 900

    def __init__(self, parent, icon, docs, module_dict):
        AttachmentData.__init__(
            self,
            parent=parent,
            icon=icon,
            docs=docs,
            module_dict=module_dict,
        )
        self.help_link = "https://youtu.be/1ADJMGOi62U?si=yb6PEdh5WzDqd7A0&t=3"

    @staticmethod
    def attachment_permissions(node):
        """Return True or False if attachment allowed on node.

        Arguments:
            node {node shape pointer} -- node shape to check permission with

        Returns:
            bool -- True if allowed or False if not
        """
        if node.node_data.joints_manager:
            return True

        module = __file__.rsplit("\\", 1)[-1].rsplit("/", 1)[-1].rsplit(".", 1)[0]
        LOGGER.warning(
            "Cannot add attachment '%s' to node '%s'. Node has no joints to operate on.",
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
        self.add_collapsible_layout(title="Settings", shown=True)

        self.scale_jnts_attr = self.add_boolean_attribute(
            name="Support Scale",
            default_value=False,
            annotation=(
                "An additional joint with the suffix '_SCALE_FS_JNT' will be created under every FS \n"
                "joint to support scaling within the rig."
            ),
            help_link="https://youtu.be/1ADJMGOi62U?si=E12zlNojoml-wpUx&t=70",
        )

        self.switch_skinning_tag_attr = self.add_boolean_attribute(
            name="Switch Skinning Tag",
            default_value=True,
            annotation=(
                "Switch the skinning tag to the FollowSkeleton joints (_FS).\n"
                "The _FS joints will now be used for skinning."
            ),
            help_link="https://youtu.be/1ADJMGOi62U?si=7Qb8oDDKBSe4KzDU&t=89",
        )

        self.enable_color_attr = self.add_boolean_attribute(
            name="Enable Joints Color",
            default_value=True,
            annotation="Check this box to enable FS joints color.",
            help_link="https://youtu.be/1ADJMGOi62U?si=Fh03T9mzLQxsmjbu&t=107",
        )

        self.jnts_color_attr = self.add_rgb_color_attribute(
            name="Joints Color",
            default_value=FS_JNTS_COLOR,
            annotation="Color of FS joints.",
            help_link="https://youtu.be/1ADJMGOi62U?si=Fh03T9mzLQxsmjbu&t=107",
        )

        self.forward_axis_attr = self.add_radio_attribute(
            name="Forward Axis",
            items=["X", "Y", "Z", "-X", "-Y", "-Z"],
            default_value=1,
            annotation=(
                "Arise is built with the Y axis facing down the chain.\nThis attribute allows you to change "
                "the orientation, so the X or Z axis can face down the chain instead."
            ),
            help_link="https://youtu.be/1ADJMGOi62U?si=7Qb8oDDKBSe4KzDU&t=114",
        )

        self.forward_axis_twist_attr = self.add_float_attribute(
            name="Forward Axis Twist",
            default_value=0.0,
            min_value=-180.0,
            max_value=180.0,
            annotation=(
                "After selecting the axis facing down the chain with the 'Forward Axis' attribute,\n"
                "this attribute allows you to control the orientation of the side-axis (twist axis) in degrees."
            ),
            help_link="https://youtu.be/1ADJMGOi62U?si=7Qb8oDDKBSe4KzDU&t=114",
        )

        self.tree_attr = self.add_tree_attribute(
            name="Follow Joints",
            help_link="https://youtu.be/1ADJMGOi62U?si=Hrc40DS6nVw31y1m&t=127",
            )

        self.add_button(
            buttons=[
                (
                    self.reset_changes,
                    "resources/icons/cancel_icon.png",
                    "Reset Changes",
                    "Reset changes done to the 'Follow Joints' table above.",
                ),
            ],
        )

        self.add_frame_layout(title="Connections")
        self.driven_attr = self.add_driven_attribute(
            name="FS Driven",
            connection_type="parent",
            parent_relative=True,  # so Maya won't create transforms above jnts when parenting.
            annotation=(
                "A connection attribute, the default value will be 'skeleton_grp', "
                "but to make the whole rig a single joint chain tree, \n"
                "it should be connected to another node's 'FollowSkeleton'."
            ),
            help_link="https://youtu.be/1ADJMGOi62U?si=41ChILQR2Prr6H_u&t=40",
        )

        self.add_separator()
        self.bottom_joint_attr = self.add_drop_down_attribute(
            name="FS Driver Joint",
            items=["None"],
            default_value="None",
            annotation=(
                "Choose a joint that will be the parent of other 'FollowSkeleton' attachments "
                "connected to the 'FS Driver' attribute."
            ),
            help_link="https://youtu.be/1ADJMGOi62U?si=kP5RWeZZbkxVmTF1&t=151",
        )
        self.driver_attr = self.add_driver_attribute(
            name="FS Driver",
            annotation="'Follow Skeleton' driver attribute",
        )

        self.close_layout()
        self.close_layout()

        self.driven_attr.value = SKELETON_GRP_NAME  # placed at end to prevent evaluate loop.

    def reset_changes(self):
        """Clear internal_database and refresh tree_attribute. """
        self.tree_attr.set_value_with_undo({})

    def evaluate(self):  # REIMPLEMENTED!
        """Add joints_infos to node joints_info_list. """
        self.tree_attr.update_model(self.follow_joints_model())
        self.jnts_color_attr.set_disabled(False if self.enable_color_attr.value else True)
        AttachmentData.evaluate(self)

    def joints_creation(self):
        """Create FS joints. """
        names_to_info = {info.default_name: info for info in self.top_node_data.joints_manager if info.skinning_jnt}

        self.fs_joints_list = []
        for model_item in self.tree_attr.model.model_data:

            if model_item["attrs"][0]["value"] is False:
                continue

            dvr_info = names_to_info[model_item["name"]]
            dvr_info.skinning_jnt = not self.switch_skinning_tag_attr.value

            # make name unique since node joint and dyn joint might be skin jnts and we strip suffix on all.
            default_name = dvr_info.default_name
            default_name = default_name.rsplit("_", 1)[0] if default_name.endswith("_DYN") else default_name

            fs_info = self.top_node_data.add_joint(
                name="{0}_FS".format(default_name),
                skinning_jnt=self.switch_skinning_tag_attr.value,
                radius=dvr_info.radius*2.0,
            )

            fs_info.prefix = dvr_info.prefix
            fs_info.suffix = dvr_info.suffix
            fs_info.human_ik = dvr_info.human_ik

            if self.enable_color_attr.value:
                fs_info.enable_jnt_color = True
                fs_info.color = self.jnts_color_attr.value

            fs_info.dvr_info = dvr_info
            dvr_info.fs_info = fs_info

            dvr_parent = model_item["attrs"][1]["value"]
            fs_info.dvr_parent_jnt = None if dvr_parent == "None" else names_to_info[dvr_parent]

            if self.scale_jnts_attr.value:
                fs_info.skinning_jnt = False

                fs_scale_info = self.top_node_data.add_joint(
                    name="{0}_SCALE_FS".format(default_name),
                    tag_parent_jnt=fs_info,
                    skinning_jnt=self.switch_skinning_tag_attr.value,
                    radius=dvr_info.radius*1.7,
                )

                fs_scale_info.prefix = dvr_info.prefix
                fs_scale_info.suffix = dvr_info.suffix
                fs_scale_info.human_ik = dvr_info.human_ik

                if self.enable_color_attr.value:
                    fs_scale_info.enable_jnt_color = True
                    fs_scale_info.color = self.jnts_color_attr.value

                fs_info.scale_jnt_info = fs_scale_info

            self.fs_joints_list.append(fs_info)

        # after all fs_infos are created find and assign the parent_tag.
        all_fs_parents_infos = set()
        for fs_info in self.fs_joints_list:
            if hasattr(fs_info.dvr_parent_jnt, "fs_info"):
                fs_info.parent_tag = fs_info.dvr_parent_jnt.fs_info
                all_fs_parents_infos.add(fs_info.dvr_parent_jnt.fs_info)

        # update connection attributes with bottom joints first.
        reversed_fs_joints = list(reversed(self.fs_joints_list))
        sorted_fs_joints = sorted(reversed_fs_joints, key=lambda x: 0 if x in all_fs_parents_infos else 1)
        fs_names = [fs_joint.data_dict["default_name"] for fs_joint in sorted_fs_joints] or ["None"]
        # sorting twice keeps the default bottom joint first so the value doesn't change randomly for user.
        self.bottom_joint_attr.items = list(reversed(fs_names))

    def attachment_creation(self):  # REIMPLEMENTED!
        """Setup parenting for FollowSkeleton joints and connect to driven and driver. """

        if not self.fs_joints_list:  # meaning all FS joints ticked off.
            return "[Follow Skeleton] You haven't specified any joints to create."

        skeleton_grp = "|{0}|{1}".format(ROOT_FOLDER_NAME, SKELETON_GRP_NAME)

        if not mc.objExists(skeleton_grp):
            tagged_grp = get_maya_nodes_with_tag(SKELETON_GRP_NAME)
            skeleton_grp = tagged_grp[0] if tagged_grp else None

        # calculate rotation matrix for the forward axis.
        rotation_degrees = AXIS_OFFSETS[self.forward_axis_attr.value][:]
        for index, axis in enumerate(rotation_degrees):
            if axis is None:
                rotation_degrees[index] = self.forward_axis_twist_attr.value

        rotation_radians = [om.MAngle(angle, om.MAngle.kDegrees).asRadians() for angle in rotation_degrees]
        matrix_4x4 = om.MEulerRotation(rotation_radians, om.MEulerRotation.kXYZ).asMatrix()
        matrix_list = [matrix_4x4[i] for i in range(16)]

        no_parent_jnts = []
        driver_jnt = None
        for fs_info in self.fs_joints_list:
            fs_jnt = fs_info.pointer
            fs_jnt.set_attr("segmentScaleCompensate", 0)
            fs_jnt.disconnect_attr("drawStyle")

            if skeleton_grp:  # parent to world or skeleton_grp to avoid flipped scaleZ on mirrored nodes.
                fs_jnt.parent_relative(skeleton_grp)

            else:
                mc.parent(fs_jnt, relative=True, world=True)

            matrix_utils.matrix_constraint(
                fs_info.dvr_info.pointer,
                fs_jnt,
                maintain_offset=False,
                skip_locked=False,
                skip_attrs=(False, False, False, False, False, False, True, True, True),
                manual_offset=matrix_list,
            )

            parent_info = fs_info.parent_tag
            if parent_info:
                fs_jnt.parent(parent_info.pointer)
                fs_jnt.disconnect_attr("inverseScale")

            else:
                fs_jnt.dvr_jnt = fs_info.dvr_info.pointer
                no_parent_jnts.append(fs_jnt)

            fs_jnt.zero_joint_orient()

            if fs_info.default_name == self.bottom_joint_attr.value:
                driver_jnt = fs_jnt

            if self.scale_jnts_attr.value:
                fs_scale_jnt = fs_info.scale_jnt_info.pointer
                fs_scale_jnt.set_attr("segmentScaleCompensate", 0)
                fs_scale_jnt.disconnect_attr("drawStyle")
                fs_scale_jnt.parent_relative(fs_jnt)

                matrix_utils.matrix_constraint(  # must be matrix_constraint, scale_constraint breaks some jnts.
                    fs_info.dvr_info.pointer,
                    fs_scale_jnt,
                    maintain_offset=True,
                    skip_locked=False,
                    skip_attrs=(True, True, True, True, True, True, False, False, False),
                )

        for top_jnt in no_parent_jnts:
            # Replace drawStyle attr with vis as HumanIK uses it.
            top_jnt.connect_attr("visibility", self.top_node_data.module_grp.attr(JOINTS_VIS_ATTR))

            for attr in ["jointOrientX", "jointOrientY", "jointOrientZ"]:
                top_jnt.lock_attr(attr)  # locking top jnts orient attrs prevents wrong orientations when parented.

            if self.top_node_data.module_type == "Base":  # Only base node to support global uniform scale.
                matrix_utils.matrix_constraint(
                    top_jnt.dvr_jnt,
                    top_jnt,
                    maintain_offset=True,
                    skip_locked=False,
                    skip_attrs=(True, True, True, True, True, True, False, False, False),
                )

        self.driven_attr.set_maya_object(no_parent_jnts)
        self.driver_attr.set_maya_object(driver_jnt)

        return True

    def follow_joints_model(self):
        """Return a joints skeleton model. """
        model_data = []
        infos = [info for info in self.top_node_data.joints_manager if info.skinning_jnt]
        options = ["None"] + [info.default_name for info in infos]

        for info in infos:
            info_options = list(options)
            if info.default_name in info_options:
                info_options.remove(info.default_name)

            data = {
                "info_pointer": info,
                "name": info.data_dict["default_name"],
                "attrs": [
                    {
                        "name": "create_follow_joint",
                        "type": bool,
                        "default_value": True,
                        "change_pointer": None,
                    },
                    {
                        "name": "parent_joint",
                        "type": list,
                        "range": info_options,
                        "default_value": info.parent_tag.default_name if info.parent_tag else info_options[0],
                        "change_pointer": None,
                    },
                ],
            }

            model_data.append(data)

        return model_data
