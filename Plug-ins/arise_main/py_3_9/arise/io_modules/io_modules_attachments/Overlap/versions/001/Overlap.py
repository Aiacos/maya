"""Overlap adds secondary motion (lag, follow through and overshoot) on top of the node joints using only Maya nodes. """

import logging

import maya.cmds as mc

from arise.data_types.attachment_data import AttachmentData
from arise.utils.io_nodes.io_transform import IoTransform
from arise.utils.matrix_utils import matrix_constraint

LOGGER = logging.getLogger("node_rig_logger")

MAYA_VERSION = 2022
AUTHOR = "Etay Herz"
RIG_TYPE = "Joints"
RIG_CATEGORY = "Build"
TAGS = ["joint", "joints", "overlap", "inertia", "lag", "overshoot", "secondary", "follow through", "spring", "jiggle"]
TOOL_TIP = (
    "Add overlap joints on top of the node joints. They lag behind the animation and overshoot "
    "using only Maya nodes (no simulation, no expressions)."
)

JOINTS_RADIUS_MULT = 1.8
OVL_JNTS_COLOR = [0.0, 0.6, 1.0]
DEFAULT_FAST_PERIOD = 6.0
DEFAULT_SLOW_PERIOD = 18.0
DEFAULT_DAMPING = 0.35


class Overlap(AttachmentData):
    """Here we will reimplement methods to 1) create attributes on the attachment
    2) create guides in the template module and 3) the rig method where the rig will be built.
    """
    sort_priority = 810

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
        if len(node.node_data.joints_manager[:]) >= 2:
            return True

        module = __file__.rsplit("\\", 1)[-1].rsplit("/", 1)[-1].rsplit(".", 1)[0]
        LOGGER.warning(
            "Cannot add attachment '%s' to node '%s'. Node has to have at least 2 joints.",
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

        self.switch_skinning_tag_attr = self.add_boolean_attribute(
            name="Switch Skinning Tag",
            default_value=True,
            annotation=(
                "Switch the skinning tag to the overlap joints (_OVL).\n"
                "The _OVL joints will now be used for skinning."
            ),
        )

        self.enable_color_attr = self.add_boolean_attribute(
            name="Enable Joints Color",
            default_value=True,
            annotation="Check this box to enable overlap joints color.",
        )

        self.jnts_color_attr = self.add_rgb_color_attribute(
            name="Joints Color",
            default_value=OVL_JNTS_COLOR,
            annotation="Color of overlap joints.",
        )

        self.tree_attr = self.add_tree_attribute(
            name="Overlap Joints",
            annotation=(
                "Choose which joints get an overlap joint and who is the parent of each.\n"
                "A chain is made of joints linked by 'parent_joint' and needs at least 2 joints."
            ),
        )

        self.add_button(
            buttons=[
                (
                    self.reset_changes,
                    "resources/icons/cancel_icon.png",
                    "Reset Changes",
                    "Reset changes done to the 'Overlap Joints' table above.",
                ),
            ],
        )

        self.ctrl_parent_attr = self.add_drop_down_attribute(
            name="Overlap Ctrl Parent",
            items=["None"],
            annotation="Specify under which ctrl to parent the 'overlap_ctrl'.",
        )

        self.ctrl_offset_attr = self.add_xyz_attribute(
            name="Overlap Ctrl Offset",
            default_value=[10, 3.5, 0],
            dynamic_attribute=False,
            writable=True,
            readable=True,
            promoted=False,
            annotation="Offset position of the 'overlap_ctrl' from its ctrl parent.",
        )

        self.driver_attr = self.add_driver_attribute(
            name="Overlap Output",
            annotation="Tip joint of the overlap chain.",
        )

        self.close_layout()

        self.add_collapsible_layout(title="Ctrl Defaults", shown=False)

        self.strength_attr = self.add_float_multiplier_attribute(
            name="Strength",
            default_value=1.0,
            annotation="Default of the ctrl 'strength' attribute. 0 is no overlap, 1 is full overlap.",
        )

        self.lag_attr = self.add_float_multiplier_attribute(
            name="Lag",
            default_value=0.5,
            annotation=(
                "Default of the ctrl 'lag' attribute. Blends from the 'Fast Period' (0) to the 'Slow Period' (1)."
            ),
        )

        self.falloff_attr = self.add_float_attribute(
            name="Falloff",
            default_value=1.0,
            min_value=0.0,
            max_value=5.0,
            annotation=(
                "Default of the ctrl 'falloff' attribute. How much more the tip of the chain moves than the base.\n"
                "0 is all joints move the same, higher values keep the base closer to the animation."
            ),
        )

        self.max_swing_attr = self.add_float_attribute(
            name="Max Swing",
            default_value=0.7,
            min_value=0.05,
            max_value=0.95,
            annotation=(
                "Default of the ctrl 'max_swing' attribute. Limits how far a joint is pulled off the animation "
                "as a ratio of its bone length. Keeps fast animation from folding the chain."
            ),
        )

        self.close_layout()

        self.add_collapsible_layout(title="Spring Rebuild Required", shown=False)

        self.quality_attr = self.add_radio_attribute(
            name="Samples",
            items=["16", "8"],
            default_value=0,
            annotation=(
                "How many past frames are sampled for each joint.\n"
                "16 - Smoother and more accurate spring.\n"
                "8 - About twice as fast to evaluate. Good for heavy rigs or many chains."
            ),
        )

        self.fast_period_attr = self.add_float_attribute(
            name="Fast Period",
            default_value=DEFAULT_FAST_PERIOD,
            min_value=2.0,
            max_value=60.0,
            annotation=(
                "Oscillation period in frames when ctrl attribute 'lag' is 0.\n"
                "Lower values result in a tighter and quicker spring."
            ),
        )

        self.slow_period_attr = self.add_float_attribute(
            name="Slow Period",
            default_value=DEFAULT_SLOW_PERIOD,
            min_value=2.0,
            max_value=60.0,
            annotation=(
                "Oscillation period in frames when ctrl attribute 'lag' is 1.\n"
                "Higher values result in a heavier and slower spring."
            ),
        )

        self.damping_attr = self.add_float_attribute(
            name="Damping",
            default_value=DEFAULT_DAMPING,
            min_value=0.05,
            max_value=1.0,
            annotation=(
                "How quickly the spring settles. 1 is no overshoot at all, lower values overshoot and bounce more.\n"
                "The simulated history is limited to the last 36 frames so very low values are cut short."
            ),
        )

        self.close_layout()

    def reset_changes(self):
        """Clear internal_database and refresh tree_attribute. """
        self.tree_attr.set_value_with_undo({})

    def evaluate(self):  # REIMPLEMENTED!
        """Update the joints table and ctrl parent options. """
        self.tree_attr.update_model(self.joints_model())
        self.jnts_color_attr.set_disabled(False if self.enable_color_attr.value else True)
        AttachmentData.evaluate(self)

        options = [info.default_name for info in self.top_node_data.ctrls_manager if info is not self.ovl_ctrl]
        self.ctrl_parent_attr.items = options or ["None"]

    def joints_creation(self):
        """Create the overlap joints. """
        names_to_info = {info.default_name: info for info in self.get_joints()}

        self.ovl_jnts_list = []
        for info_model in self.tree_attr.model.model_data:

            if not info_model["attrs"][0]["value"]:
                continue

            drv_info = names_to_info[info_model["name"]]

            # make name unique since node joint and overlap joint might be skin jnts and we strip suffix on all.
            default_name = drv_info.default_name
            default_name = default_name.rsplit("_", 2)[0] if default_name.endswith("_SCALE_FS") else default_name
            default_name = default_name.rsplit("_", 1)[0] if default_name.endswith("_FS") else default_name

            ovl_info = self.top_node_data.add_joint(
                name="{0}_OVL".format(default_name),
                skinning_jnt=self.switch_skinning_tag_attr.value,
                radius=drv_info.radius * JOINTS_RADIUS_MULT,
            )

            ovl_info.prefix = drv_info.prefix
            ovl_info.suffix = drv_info.suffix
            ovl_info.human_ik = drv_info.human_ik

            if self.enable_color_attr.value:
                ovl_info.enable_jnt_color = True
                ovl_info.color = self.jnts_color_attr.value

            drv_info.skinning_jnt = not self.switch_skinning_tag_attr.value
            drv_info.ovl_info = ovl_info

            ovl_info.drv_info = drv_info
            ovl_info.ovl_parent_drv_info = names_to_info.get(info_model["attrs"][1]["value"], None)

            self.ovl_jnts_list.append(ovl_info)

        for ovl_info in self.ovl_jnts_list:
            if hasattr(ovl_info.ovl_parent_drv_info, "ovl_info"):
                ovl_info.parent_tag = ovl_info.ovl_parent_drv_info.ovl_info

            else:
                ovl_info.parent_tag = None

    def ctrls_creation(self):
        """Create controls based on attributes values, guides and joints. (without positioning as this point). """
        scale_mult = 1.0
        if hasattr(self.top_node_data, "ctrls_scale_attr"):
            scale_mult = self.top_node_data.ctrls_scale_attr.value

        self.ovl_ctrl = self.top_node_data.add_ctrl(
            name="overlap",
            shape="gear",
            up_orient="+Z",
            size=4.0 * scale_mult,
        )

        for attr in ["rotateX", "rotateY", "rotateZ", "scaleX", "scaleY", "scaleZ"]:
            self.ovl_ctrl.add_hidden_attr(attr)

    def attachment_creation(self):   # REIMPLEMENTED!
        """Analyze tree data and create the overlap network. """
        output_grp = IoTransform("{0}_overlap_output_grp".format(self.top_node_data.name))
        output_grp.parent_relative(self.top_node_data.module_grp)
        self.driver_attr.set_maya_object(output_grp)

        if not self.ovl_jnts_list:
            return "Nothing to create."

        parent_tags_list = []
        for ovl_info in self.ovl_jnts_list:
            if ovl_info.parent_tag in parent_tags_list:
                return "'parent_joint' value cannot repeat ['{0}']".format(ovl_info.default_name)

            if ovl_info.parent_tag is not None:
                parent_tags_list.append(ovl_info.parent_tag)

        chains = []
        btm_infos = [info for info in self.ovl_jnts_list if info not in parent_tags_list]
        if not btm_infos:
            return "Loop detected. Check attachment 'parent_joint' values."

        for btm_info in btm_infos:
            chain_infos = []
            current_info = btm_info
            while current_info is not None:
                if current_info in chain_infos:
                    return "Loop detected. Check attachment 'parent_joint' values."

                chain_infos.append(current_info)
                current_info = current_info.parent_tag

            if len(chain_infos) < 2:
                return "Overlap chain has to have at least 2 joints."

            chain_infos.reverse()
            chains.append(chain_infos)

        ovl_ctrl = self._setup_ovl_ctrl()
        attrs = {
            "strength": ovl_ctrl.strength_attr,
            "lag": ovl_ctrl.lag_attr,
            "falloff": ovl_ctrl.falloff_attr,
            "max_swing": ovl_ctrl.max_swing_attr,
        }

        taps = overlap_utils.TAPS_OPTIONS[self.quality_attr.value]
        kernel_fast = overlap_utils.spring_kernel(self.fast_period_attr.value, self.damping_attr.value, taps)
        kernel_slow = overlap_utils.spring_kernel(self.slow_period_attr.value, self.damping_attr.value, taps)

        top_grp = IoTransform("{0}_overlap_grp".format(self.top_node_data.name))
        top_grp.parent_relative(self.top_node_data.module_grp)
        top_grp.lock_and_hide_transformations(vis=False)

        for index, chain in enumerate(chains):
            prefix_name = "{0}_{1}".format(self.top_node_data.name, index)

            chain_grp = IoTransform("{0}_chain_overlap_grp".format(prefix_name))
            chain_grp.parent_relative(top_grp)
            chain_grp.lock_and_hide_transformations(vis=False)

            orig_jnts = [ovl_info.drv_info.pointer for ovl_info in chain]
            tip_loc = self._create_tip_loc(orig_jnts, prefix_name)

            for ovl_info in chain:
                ovl_info.pointer.parent_relative(chain_grp)
                ovl_info.pointer.zero_joint_orient()

            overlap_utils.create_overlap_chain(
                prefix=prefix_name,
                points=[str(jnt) for jnt in orig_jnts] + [str(tip_loc)],
                joints=[str(ovl_info.pointer) for ovl_info in chain],
                attrs=attrs,
                kernel_fast=kernel_fast,
                kernel_slow=kernel_slow,
                taps=taps,
            )

        matrix_constraint(chains[0][-1].pointer, output_grp, maintain_offset=False)

        return True

    def _create_tip_loc(self, orig_jnts, prefix_name):
        """Create a locator under the last joint that extends the chain, so the last joint has a bone too.

        Args:
            orig_jnts (list): of IoJoint, the driving joints of the chain from base to tip
            prefix_name (str): prefix of the locator name

        Returns:
            IoTransform: the tip locator
        """
        point_a = orig_jnts[-2].get_xform("world", translation=True)
        point_b = orig_jnts[-1].get_xform("world", translation=True)
        tip_position = [b + (b - a) * 0.5 for a, b in zip(point_a, point_b)]

        tip_loc = IoTransform(mc.spaceLocator(n="{0}_tip_OVL_input_loc".format(prefix_name))[0], existing=True)
        tip_loc.parent_relative(orig_jnts[-1])
        mc.xform(tip_loc, worldSpace=True, translation=tip_position)
        tip_loc.hide()
        tip_loc.lock_and_hide_transformations(vis=False)

        return tip_loc

    def _setup_ovl_ctrl(self):
        """Parent, offset and create attrs on the overlap ctrl.

        Returns:
            IoCtrl: the ctrl with attribute names stored on it
        """
        parent_name = self.ctrl_parent_attr.value
        if parent_name == "None":
            raise ValueError("'Overlap Ctrl Parent' value error")

        parent_ctrl = None
        for info in self.top_node_data.ctrls_manager:
            if info.default_name == parent_name:
                parent_ctrl = info.pointer
                break

        if parent_ctrl is None:
            raise ValueError("'Overlap Ctrl Parent' value error")

        ovl_ctrl = self.ovl_ctrl.pointer
        ovl_ctrl.position_grp = ovl_ctrl.offset_grp.add_group_above("{0}_pos_grp".format(ovl_ctrl.short_name))
        ovl_ctrl.position_grp.parent_relative(parent_ctrl)
        ovl_ctrl.offset_grp.set_translation(self.ctrl_offset_attr.value, space="object")

        ovl_ctrl.add_spacer_attr()
        ovl_ctrl.strength_attr = ovl_ctrl.add_attr(
            "strength", dv=self.strength_attr.value, min=0, max=1, keyable=True,
        )
        ovl_ctrl.lag_attr = ovl_ctrl.add_attr("lag", dv=self.lag_attr.value, min=0, max=1, keyable=True)
        ovl_ctrl.falloff_attr = ovl_ctrl.add_attr("falloff", dv=self.falloff_attr.value, min=0, smx=5, keyable=True)
        ovl_ctrl.max_swing_attr = ovl_ctrl.add_attr(
            "max_swing", dv=self.max_swing_attr.value, min=0.05, max=0.95, keyable=True,
        )

        return ovl_ctrl

    def get_joints(self):
        """Return a list of joints_info to operate on. """
        return [info for info in self.top_node_data.joints_manager if info.skinning_jnt]

    def joints_model(self):
        """Return a joints skeleton model. """
        model_data = []
        node_infos = self.get_joints()
        options = ["None"] + [info.default_name for info in node_infos]

        for info in node_infos:
            info_options = list(options)
            if info.default_name in info_options:
                info_options.remove(info.default_name)

            data = {
                "info_pointer": info,
                "name": info.data_dict["default_name"],
                "attrs": [
                    {
                        "name": "create_overlap_joint",
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

        # Since can't repeat parent_joint value, have repeating value default to 'None' and 'create' False.
        # Does not apply to first instance of repeating value.
        all_values = []
        for data in model_data:
            value = data["attrs"][1]["default_value"]

            if value == options[0]:
                continue

            if value in all_values:
                data["attrs"][0]["default_value"] = False
                data["attrs"][1]["default_value"] = data["attrs"][1]["range"][0]  # set to 'None'.

            all_values.append(value)

        return model_data
