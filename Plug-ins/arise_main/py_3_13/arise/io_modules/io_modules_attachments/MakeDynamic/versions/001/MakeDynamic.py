"""MakeDynamic add dynamic curve to result joints. """

import logging

import maya.cmds as mc

from arise.data_types.attachment_data import AttachmentData
from arise.utils.io_nodes.io_transform import IoTransform
from arise.utils.decorators_utils import undo_chunk_dec
from arise.utils.matrix_utils import matrix_constraint
from arise.utils.math_utils import distance_between

LOGGER = logging.getLogger("node_rig_logger")

MAYA_VERSION = 2016
AUTHOR = "Etay Herz"
RIG_TYPE = "Joints"
RIG_CATEGORY = "Build"
TAGS = ["joint", "joints", "nHair", "simulation", "curve"]
TOOL_TIP = "Add dynamic joints on top of the node joints, which can be simulated."

JOINTS_RADIUS = 3.0
DYN_JNTS_COLOR = [1.0, 0.3, 0.0]


class MakeDynamic(AttachmentData):
    """Here we will reimplement methods to 1) create attributes on the attachment
    2) create guides in the template module and 3) the rig method where the rig will be built.
    """
    sort_priority = 800

    def __init__(self, parent, icon, docs, module_dict):
        AttachmentData.__init__(
            self,
            parent=parent,
            icon=icon,
            docs=docs,
            module_dict=module_dict,
        )
        self.help_link = "https://www.youtube.com/watch?v=tDl2y0irYzY"

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
                "Switch the skinning tag to the dynamic joints (_DYN).\n"
                "The _DYN joints will now be used for skinning."
            ),
            help_link="https://youtu.be/tDl2y0irYzY?si=SoE52TGZ4TL0ZEoD&t=38",
        )

        self.enable_color_attr = self.add_boolean_attribute(
            name="Enable Joints Color",
            default_value=True,
            annotation="Check this box to enable dynamic joints color.",
            help_link="https://youtu.be/tDl2y0irYzY?si=J8zqaJsjv4PYCDVd&t=58",
        )

        self.jnts_color_attr = self.add_rgb_color_attribute(
            name="Joints Color",
            default_value=DYN_JNTS_COLOR,
            annotation="Color of dynamic joints.",
            help_link="https://youtu.be/tDl2y0irYzY?si=J8zqaJsjv4PYCDVd&t=58",
        )

        self.tree_attr = self.add_tree_attribute(
            name="Dynamic Joints",
            help_link="https://youtu.be/tDl2y0irYzY?si=ehuCAr0vvKt1kUSS&t=65",
        )

        self.add_button(
            buttons=[
                (
                    self.reset_changes,
                    "resources/icons/cancel_icon.png",
                    "Reset Changes",
                    "Reset changes done to the 'Dynamic Joints' table above.",
                ),
            ],
        )

        self.sim_ctrl_parent_attr = self.add_drop_down_attribute(
            name="Sim Ctrl Parent",
            items=["None"],
            annotation="Specify under which ctrl to parent the 'simulation_ctrl'.",
            help_link="https://youtu.be/tDl2y0irYzY?si=S1HZwIH3OlSgQCNB&t=85",
        )

        self.sim_offset_attr = self.add_xyz_attribute(
            name="Sim Ctrl Offset",
            default_value=[10, 3.5, 0],
            dynamic_attribute=False,
            writable=True,
            readable=True,
            promoted=False,
            annotation="Offset position of the 'simulation_ctrl' from its ctrl parent.",
            help_link="https://youtu.be/tDl2y0irYzY?si=S1HZwIH3OlSgQCNB&t=85",
        )

        self.driver_attr = self.add_driver_attribute(
            name="Dynamic Output",
            annotation="Tip joint of dynamic chain",
        )

        self.close_layout()

        self.add_collapsible_layout(title="Nucleus (Optional)", shown=False)
        self.add_button(
            buttons=[
                (
                    self.create_nucleus,
                    "resources/icons/attachments/nucleus.png",
                    "Create A Nucleus Node",
                    "Click to create a new Nucleus node in the Maya scene.",
                ),
            ],
        )

        self.nucleus_dropdown_attr = self.add_drop_down_attribute(
            name="Connect To Nucleus",
            items=["None"],
            annotation="Attach this 'MakeDynamic' to an existing Nucleus in the scene. (Rebuild required)",
            help_link="https://youtu.be/tDl2y0irYzY?si=NJNQ7uCq8xczqzYc&t=116",
        )

        self.close_layout()

    def reset_changes(self):
        """Clear internal_database and refresh tree_attribute. """
        self.tree_attr.set_value_with_undo({})

    @undo_chunk_dec
    def create_nucleus(self):
        """Create a new nucleus node to the Maya scene just like Maya does. """
        nucleus = mc.createNode("nucleus")
        mc.connectAttr("{0}.outTime".format(mc.ls(type="time")[0]), "{0}.currentTime".format(nucleus))
        mc.setAttr("{0}.spaceScale".format(nucleus), 0.01)  # defaults to 1 unit = 0.01 meter.

        if mc.upAxis(q=True, axis=True) == "z":
            mc.setAttr("{0}.gravityDirection".format(nucleus), 0, 0, -1)

        # refresh nucleus_dropdown_attr to include new nucleus on all nodes with MakeDynamic attachment.
        for node in self.scene_ptr.node_children:
            for attachment in node.node_data.attachments_data:
                if attachment.module_type == "MakeDynamic":
                    node.node_data.evaluate_creation_methods()

    def evaluate(self):  # REIMPLEMENTED!
        """Add joints_infos to node joints_info_list. """
        self.tree_attr.update_model(self.follow_joints_model())
        self.jnts_color_attr.set_disabled(False if self.enable_color_attr.value else True)
        self.nucleus_dropdown_attr.items = ["None"] + mc.ls(type="nucleus")
        AttachmentData.evaluate(self)

        options = [ctrl_info.default_name for ctrl_info in self.top_node_data.ctrls_manager if ctrl_info is not self.dyn_ctrl]
        self.sim_ctrl_parent_attr.items = options or ["None"]


    def joints_creation(self):
        """Create dynamic joints. """
        names_to_info = {info.default_name: info for info in self.get_joints()}

        self.dyn_jnts_list = []
        for info_model in self.tree_attr.model.model_data:

            if not info_model["attrs"][0]["value"]:
                continue

            drv_info = names_to_info[info_model["name"]]

            # make name unique since node joint and dyn joint might be skin jnts and we strip suffix on all.
            default_name = drv_info.default_name
            default_name = default_name.rsplit("_", 2)[0] if default_name.endswith("_SCALE_FS") else default_name
            default_name = default_name.rsplit("_", 1)[0] if default_name.endswith("_FS") else default_name

            dyn_info = self.top_node_data.add_joint(
                name="{0}_DYN".format(default_name),
                skinning_jnt=self.switch_skinning_tag_attr.value,
                radius=drv_info.radius * 1.8,
            )

            dyn_info.prefix = drv_info.prefix
            dyn_info.suffix = drv_info.suffix
            dyn_info.human_ik = drv_info.human_ik

            if self.enable_color_attr.value:
                dyn_info.enable_jnt_color = True
                dyn_info.color = self.jnts_color_attr.value

            drv_info.skinning_jnt = not self.switch_skinning_tag_attr.value
            drv_info.dyn_info = dyn_info

            dyn_info.drv_info = drv_info
            dyn_parent_dvr_info = names_to_info.get(info_model["attrs"][1]["value"], None)
            dyn_info.dyn_parent_dvr_info = dyn_parent_dvr_info

            self.dyn_jnts_list.append(dyn_info)

        for dyn_info in self.dyn_jnts_list:

            if hasattr(dyn_info.dyn_parent_dvr_info, "dyn_info"):
                dyn_info.parent_tag = dyn_info.dyn_parent_dvr_info.dyn_info

            else:
                dyn_info.parent_tag = None

    def ctrls_creation(self):
        """Create controls based on attributes values, guides and joints. (without positioning as this point). """
        scale_mult = 1.0
        if hasattr(self.top_node_data, "ctrls_scale_attr"):
            scale_mult = self.top_node_data.ctrls_scale_attr.value

        self.dyn_ctrl = self.top_node_data.add_ctrl(
            name="simulation",
            shape="gear",
            up_orient="+Z",
            size=4.0 * scale_mult,
        )

        for attr in ["rotateX", "rotateY", "rotateZ", "scaleX", "scaleY", "scaleZ"]:
            self.dyn_ctrl.add_hidden_attr(attr)

    def attachment_creation(self):   # REIMPLEMENTED!
        """Analyze tree data and create dynamic setup. """
        output_grp = IoTransform("{0}_sim_output_grp".format(self.top_node_data.name))
        output_grp.parent_relative(self.top_node_data.module_grp)
        self.driver_attr.set_maya_object(output_grp)

        if not self.dyn_jnts_list:
            return "Nothing to create."

        parent_tags_list = []
        for dyn_info in self.dyn_jnts_list:
            if dyn_info.parent_tag in parent_tags_list:
                return "'parent_joint' value cannot repeat ['{0}']".format(dyn_info.default_name)

            if dyn_info.parent_tag is not None:
                parent_tags_list.append(dyn_info.parent_tag)

        dyn_chains = []
        btm_dvrs_infos = [info for info in self.dyn_jnts_list if info not in parent_tags_list]
        if not btm_dvrs_infos:
            return "Loop detected. Check attachment 'parent_joint' values."

        for btm_dvr in btm_dvrs_infos:
            chain_infos = []
            current_info = btm_dvr
            while current_info is not None:
                if current_info in chain_infos:
                    return "Loop detected. Check attachment 'parent_joint' values."

                chain_infos.append(current_info)
                current_info = current_info.parent_tag

            if len(chain_infos) < 2:
                return "Dynamic chain has to have at least 2 joints."

            chain_infos.reverse()
            dyn_chains.append(chain_infos)

        sim_ctrl = self._setup_sim_ctrl()

        sim_top_grp = IoTransform("{0}_sim_grp".format(self.top_node_data.name))
        sim_top_grp.parent_relative(self.top_node_data.module_grp)
        sim_top_grp.lock_and_hide_transformations(vis=False)
        sim_top_grp.set_attr("inheritsTransform", 0)

        for index, chain in enumerate(dyn_chains):
            prefix_name = "{0}_{1}".format(self.top_node_data.name, index)
            dyn_chain_grp = IoTransform("{0}_chain_sim_grp".format(prefix_name))
            dyn_chain_grp.parent_relative(sim_top_grp)
            dyn_chain_grp.lock_and_hide_transformations(vis=False)

            jnts_grp = IoTransform("{0}_chain_jnts_grp".format(prefix_name))
            jnts_grp.parent_relative(dyn_chain_grp)
            jnts_grp.lock_and_hide_transformations(vis=False)

            input_curve = self._create_curve(curve_name="{0}_input".format(prefix_name), cv_count=len(chain)+1)
            input_curve.parent_relative(dyn_chain_grp)

            orig_jnts = [dyn_jnt.drv_info.pointer for dyn_jnt in chain]
            parent_jnts = orig_jnts + [orig_jnts[-1]]  # last jnt will have 2 locs, one will be offset.
            driver_locs = self._create_driver_locs(curve=input_curve, parents=parent_jnts, prefix_name=prefix_name)

            point_a = orig_jnts[-2].get_xform("world", translation=True)
            point_b = orig_jnts[-1].get_xform("world", translation=True)
            distance = max(distance_between(point_a, point_b) / 2.0, 0.2)
            driver_locs[-1].set_attr("translateY", distance)

            name = "{0}_DYN_node".format(prefix_name)
            follicle, hair_system, out_curve = self._create_sim_nodes(input_curve, dyn_chain_grp, name)

            self.connect_sim_attrs(hair_shape=hair_system.get_shapes()[0], folli_shape=follicle.get_shapes()[0])
            mc.connectAttr(sim_ctrl.show_attr, "{0}.visibility".format(input_curve))
            mc.connectAttr(sim_ctrl.show_attr, "{0}.visibility".format(out_curve))

            if self.nucleus_dropdown_attr.value != "None":
                if not self.connect_to_nucleus(hair_system.get_shapes()[0], self.nucleus_dropdown_attr.value):
                    return "Connecting to the specified nucleus node failed."

            for count, jnt_info in enumerate(chain):
                jnt = jnt_info.pointer
                jnt.parent_relative(jnts_grp)
                jnt.zero_joint_orient()
                jnt.connect_attr("translate", out_curve.attr("editPoints[{0}]".format(count)))
                jnt.scale_constraint_to(jnt_info.drv_info.pointer, mo=True)

            # tip output loc, last jnt will aim at (so last jnt orient will behave simulated too).
            name = "{0}_tip_DYN_output_loc".format(prefix_name)
            tip_output_loc = IoTransform(mc.spaceLocator(n=name)[0], existing=True)
            tip_output_loc.parent_relative(dyn_chain_grp)
            tip_output_loc.connect_attr("translate", out_curve.attr("editPoints[{0}]".format(count+1)))
            tip_output_loc.hide()
            tip_output_loc.lock_and_hide_transformations(vis=False)

            prev_jnt = chain[0].pointer
            prev_up_obj = orig_jnts[0]
            for jnt, up_obj in zip(chain[1:], orig_jnts[1:]):
                prev_jnt.aim_constraint_to(
                    jnt.pointer,
                    aimVector=(0, 1, 0),
                    upVector=(1, 0, 0),
                    worldUpType="objectrotation",
                    worldUpObject=prev_up_obj,
                    worldUpVector=(1, 0, 0),
                    maintainOffset=False,
                )
                prev_jnt = jnt.pointer
                prev_up_obj = up_obj

            prev_jnt.aim_constraint_to(
                tip_output_loc,
                aimVector=(0, 1, 0),
                upVector=(1, 0, 0),
                worldUpType="objectrotation",
                worldUpObject=prev_up_obj,
                worldUpVector=(1, 0, 0),
                maintainOffset=False,
            )

        matrix_constraint(dyn_chains[0][-1].pointer, output_grp, maintain_offset=False)

        return True

    def _setup_sim_ctrl(self):
        """Parent, offset and create attrs on sim_ctrl. """
        parent_name = self.sim_ctrl_parent_attr.value

        if parent_name == "None":
            raise ValueError("'Sim Ctrl Parent' value error")

        parent_ctrl = None
        for info in self.top_node_data.ctrls_manager:
            if info.default_name == parent_name:
                parent_ctrl = info.pointer
                break

        if parent_ctrl is None:
            raise ValueError("'Sim Ctrl Parent' value error")

        sim_ctrl = self.dyn_ctrl.pointer
        sim_ctrl.position_grp = sim_ctrl.offset_grp.add_group_above("{0}_pos_grp".format(sim_ctrl.short_name))
        sim_ctrl.position_grp.parent_relative(parent_ctrl)
        sim_ctrl.offset_grp.set_translation(self.sim_offset_attr.value, space="object")

        sim_ctrl.add_spacer_attr()
        sim_ctrl.enable_attr = sim_ctrl.add_attr("enable_dynamics", at="bool", dv=0, keyable=False)
        mc.setAttr(sim_ctrl.enable_attr, channelBox=True)
        sim_ctrl.show_attr = sim_ctrl.add_attr("display_sim_curves", at="bool", dv=0, keyable=False)
        mc.setAttr(sim_ctrl.show_attr, channelBox=True)
        enums = "No Attach:Base:Tip:BothEnds:"
        sim_ctrl.point_lock_attr = sim_ctrl.add_attr("point_lock", keyable=False, at="enum", en=enums, dv=1)
        mc.setAttr(sim_ctrl.point_lock_attr, channelBox=True)

        sim_ctrl.add_spacer_attr()
        sim_ctrl.start_attr = sim_ctrl.add_attr("start_frame", dv=1, keyable=True)
        sim_ctrl.base_pos_attr = sim_ctrl.add_attr("anim_follow_base_pos", dv=0, min=0, max=0.99, keyable=True)
        sim_ctrl.follow_base_attr = sim_ctrl.add_attr("anim_follow_base", dv=1, min=0, max=1, keyable=True)
        sim_ctrl.tip_pos_attr = sim_ctrl.add_attr("anim_follow_tip_pos", dv=1, min=0.01, max=1, keyable=True)
        sim_ctrl.follow_tip_attr = sim_ctrl.add_attr("anim_follow_tip", dv=0.2, min=0, max=1, keyable=True)
        sim_ctrl.follow_damp_attr = sim_ctrl.add_attr("anim_follow_damp", dv=0.2, min=0, keyable=True)
        sim_ctrl.add_spacer_attr()

        sim_ctrl.mass_attr = sim_ctrl.add_attr("mass", dv=1, min=0, keyable=True)
        sim_ctrl.drag_attr = sim_ctrl.add_attr("drag", dv=0.05, min=0, keyable=True)
        sim_ctrl.damp_attr = sim_ctrl.add_attr("damp", dv=0, min=0, keyable=True)
        sim_ctrl.stiffness_attr = sim_ctrl.add_attr("stiffness", dv=0.15, min=0, keyable=True)

        mc.addAttr(sim_ctrl, ln="__Turbulence__", at="enum", en="_______:")
        mc.setAttr("{0}.{1}".format(sim_ctrl, "__Turbulence__"), keyable=True, cb=True, lock=True)
        sim_ctrl.intensity_attr = sim_ctrl.add_attr("turbulence_intensity", dv=0, min=0, smx=4, keyable=True)
        sim_ctrl.frequency_attr = sim_ctrl.add_attr("turbulence_frequency", dv=0.2, min=0, smx=2, keyable=True)
        sim_ctrl.speed_attr = sim_ctrl.add_attr("turbulence_speed", dv=0.2, min=0, smx=2, keyable=True)

        remap_node = mc.createNode("remapValue", name="{0}_enable_remap".format(sim_ctrl.short_name))
        mc.connectAttr(sim_ctrl.enable_attr, "{0}.inputValue".format(remap_node))
        mc.setAttr("{0}.inputMin".format(remap_node), 0)
        mc.setAttr("{0}.inputMax".format(remap_node), 1)
        mc.setAttr("{0}.outputMin".format(remap_node), 1)
        mc.setAttr("{0}.outputMax".format(remap_node), 2)
        sim_ctrl.enable_remap_attr = "{0}.outValue".format(remap_node)

        return sim_ctrl

    def connect_sim_attrs(self, hair_shape, folli_shape):
        """Connect sim_ctrl attrs to drive hair_shape and follicle.

        Args:
            hair_shape (str): name of hair node
            folli_shape (str): name of follicle node
        """
        sim_ctrl = self.dyn_ctrl.pointer
        mc.connectAttr(sim_ctrl.enable_remap_attr, "{0}.simulationMethod".format(hair_shape))

        mc.connectAttr(sim_ctrl.start_attr, "{0}.startFrame".format(hair_shape))
        mc.connectAttr(sim_ctrl.point_lock_attr, "{0}.pointLock".format(folli_shape))
        mc.connectAttr(
            sim_ctrl.base_pos_attr,
            "{0}.attractionScale[0].attractionScale_Position".format(hair_shape),
        )
        mc.connectAttr(
            sim_ctrl.follow_base_attr,
            "{0}.attractionScale[0].attractionScale_FloatValue".format(hair_shape),
        )
        mc.connectAttr(
            sim_ctrl.follow_tip_attr,
            "{0}.attractionScale[1].attractionScale_FloatValue".format(hair_shape),
        )
        mc.connectAttr(
            sim_ctrl.tip_pos_attr,
            "{0}.attractionScale[1].attractionScale_Position".format(hair_shape),
        )
        mc.connectAttr(sim_ctrl.follow_damp_attr, "{0}.attractionDamp".format(hair_shape))
        mc.connectAttr(sim_ctrl.mass_attr, "{0}.mass".format(hair_shape))
        mc.connectAttr(sim_ctrl.drag_attr, "{0}.drag".format(hair_shape))
        mc.connectAttr(sim_ctrl.damp_attr, "{0}.damp".format(hair_shape))
        mc.connectAttr(sim_ctrl.stiffness_attr, "{0}.stiffness".format(hair_shape))

        mc.connectAttr(sim_ctrl.intensity_attr, "{0}.turbulenceStrength".format(hair_shape))
        mc.connectAttr(sim_ctrl.frequency_attr, "{0}.turbulenceFrequency".format(hair_shape))
        mc.connectAttr(sim_ctrl.speed_attr, "{0}.turbulenceSpeed".format(hair_shape))

    def _create_curve(self, curve_name, cv_count):
        """Create blank curve with cv at each guide position.

        Args:
            curve_name (str): how to name the curve
            cv_count (int): number of CVs on curve

        Returns:
            IoTransform: of the nurbsCurve parent transform
        """
        curve = mc.curve(
            degree=1,
            point=[(0, 0, 0)] * cv_count,
            knot=range(cv_count),
            worldSpace=True,
            name="{0}_DYN_curve".format(curve_name),
        )
        curve = IoTransform(curve, existing=True)
        curve.set_attr("overrideEnabled", 1)
        curve.set_attr("overrideDisplayType", 1)
        curve.lock_and_hide_transformations(vis=False)
        mc.rename(curve.get_shapes()[0], "{0}Shape".format(curve.short_name))

        return curve

    @staticmethod
    def _create_driver_locs(curve, parents, prefix_name):
        """Create locators under parents to drive the curve.

        Args:
            curve (IoTransform): transform parent of a nurbsCurve
            parents (list): of transforms to parent under
            prefix_name (str): prefix of locators

        Returns:
            list: of IoTransform locators
        """
        locs_list = []
        for index, orig_jnt in enumerate(parents):
            name = "{0}_{1}_DYN_input_loc".format(prefix_name, index)
            loc = IoTransform(mc.spaceLocator(n=name)[0], existing=True)
            loc.parent_relative(orig_jnt)
            mc.connectAttr(loc.attr("worldPosition[0]"), "{0}.controlPoints[{1}]".format(curve, index))
            loc.hide()
            loc.lock_and_hide_transformations(vis=False)
            locs_list.append(loc)

        return locs_list

    def _create_sim_nodes(self, input_curve, parent_grp, name_prefix):
        """manually create the nHair simulation nodes and connections including the output curve.

        Args:
            input_curve (IoTransform): parent transform of curve to turn dynamic
            parent_grp (IoTransform): transform to parent created nodes under
            name_prefix (str): prefix for naming dynamic nodes

        Returns:
            list: of dynamic nodes [follicle, hairSystem, output_curve]
        """
        folli_trans = IoTransform("{0}_folli".format(name_prefix))
        mc.createNode("follicle", name="{0}_folliShape".format(name_prefix), parent=folli_trans)
        folli_trans.parent_relative(parent_grp)
        folli_trans.hide()

        hair_sys_trans = IoTransform("{0}_hairSystem".format(name_prefix))
        mc.createNode("hairSystem", name="{0}_hairSystemShape".format(name_prefix), parent=hair_sys_trans)
        hair_sys_trans.parent_relative(parent_grp)
        hair_sys_trans.hide()

        time_node = mc.ls(type="time")[0]
        input_shape = input_curve.get_shapes(skip_intermediate=True)[0]
        folli_shape = folli_trans.get_shapes()[0]
        hair_shape = hair_sys_trans.get_shapes()[0]

        mc.connectAttr("{0}.local".format(input_shape), "{0}.startPosition".format(folli_shape))
        mc.connectAttr("{0}.worldMatrix".format(input_curve), "{0}.startPositionMatrix".format(folli_shape))
        mc.connectAttr("{0}.outTime".format(time_node), "{0}.currentTime".format(hair_shape))
        mc.connectAttr("{0}.outputHair[0]".format(hair_shape), "{0}.currentPosition".format(folli_shape))
        mc.connectAttr("{0}.outHair".format(folli_shape), "{0}.inputHair[0]".format(hair_shape))

        mc.setAttr("{0}.restPose".format(folli_shape), 1)
        mc.setAttr("{0}.startDirection".format(folli_shape), 1)
        mc.setAttr("{0}.degree".format(folli_shape), 1)
        mc.setAttr("{0}.collide".format(folli_shape), 0)

        mc.setAttr("{0}.collide".format(hair_shape), 0)
        mc.setAttr("{0}.simulationMethod".format(hair_shape), 2)
        mc.setAttr("{0}.disableFollicleAnim".format(hair_shape), 1)
        mc.setAttr("{0}.startCurveAttract".format(hair_shape), 1)
        mc.setAttr("{0}.gravity".format(hair_shape), 9.8)

        count = len(mc.ls("{0}.cv[:]".format(input_curve), fl=True))
        output_curve = self._create_curve("{0}_output".format(name_prefix), cv_count=count)
        output_curve.parent(parent_grp)
        output_curve.freeze_transformations()
        mc.connectAttr("{0}.outCurve".format(folli_shape), "{0}.create".format(output_curve.get_shapes()[0]))

        return [folli_trans, hair_sys_trans, output_curve]

    def connect_to_nucleus(self, hair_shape, nucleus):
        """Connect attributes between hair_shape and nucleus.

        Args:
            hair_shape (str): name of hairSystem node
            nucleus (str): name of nucleus node in scene
        """
        nucleus = mc.ls(nucleus, long=True)

        if not nucleus:
            return False

        nucleus = IoTransform(nucleus[0], existing=True)
        last_index = mc.getAttr("{0}.outputObjects".format(nucleus), multiIndices=True)
        last_index = last_index[-1] + 1 if last_index else 0

        for index in range(last_index):
            connection = mc.listConnections(
                "{0}.outputObjects[{1}]".format(nucleus, index),
                source=False,
                destination=True,
            )

            if not connection:
                last_index = index
                break

        mc.connectAttr(
            "{0}.outputObjects[{1}]".format(nucleus, last_index),
            "{0}.nextState".format(hair_shape),
            force=True,
        )

        mc.connectAttr(
            "{0}.startFrame".format(nucleus),
            "{0}.startFrame".format(hair_shape),
            force=True,
        )

        sim_ctrl = self.dyn_ctrl.pointer
        mc.setAttr(sim_ctrl.start_attr, lock=True, keyable=False, channelBox=False)
        mc.connectAttr(sim_ctrl.enable_attr, "{0}.active".format(hair_shape))
        mc.setAttr("{0}.collide".format(hair_shape), 1)
        mc.setAttr("{0}.disableFollicleAnim".format(hair_shape), 0)

        mc.connectAttr(
            "{0}.currentState".format(hair_shape),
            "{0}.inputActive[{1}]".format(nucleus, last_index),
            force=True,
        )

        mc.connectAttr(
            "{0}.startState".format(hair_shape),
            "{0}.inputActiveStart[{1}]".format(nucleus, last_index),
            force=True,
        )

        return True

    def get_joints(self):
        """Return a list of joints_info to operate on. """
        return [info for info in self.top_node_data.joints_manager if info.skinning_jnt]

    def follow_joints_model(self):
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
                        "name": "create_dynamic_joint",
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
