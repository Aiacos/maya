"""Dynamic_FK_Chain module creates an FK chain with optional dynamic simulation. """

import maya.cmds as mc

from arise.data_types import node_data
from arise.utils.io_nodes.io_transform import IoTransform
from arise.utils.matrix_utils import matrix_constraint
from arise.utils.math_utils import distance_between
from arise.utils.modules_utils import (
    world_rotation, secondary_ctrls_setup, expose_rotation_order, create_grps, SECONDARY_COLOR, update_ctrls
)

MAYA_VERSION = 2016  # the version of maya from which this module supports.
AUTHOR = "Etay Herz"  # name of person who created this module.
RIG_CATEGORY = "Basic"  # either 'Basic', 'Cartoon', 'Vfx', 'Game' or 'All'.
RIG_TYPE = "All"  # Biped, Car, Quadruped, ..., All.
TAGS = ["basic", "fk", "chain", "dynamic", "nHair", "simulation"]
TOOL_TIP = """FK chain with dynamic simulation.
The same as adding a 'MakeDynamic' attachment to an 'FK_Chain' node, but slightly faster
and with control over the simulation space."""

node_data.NodeData.update_ctrls = update_ctrls


class Dynamic_FK_Chain(node_data.NodeData):
    """FK chain with optional dynamic simulation. """
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
                "if unchecked, when zeroing the ctrls, they will align with a world axis "
                "specified in the following two attributes."
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
            default_value=4,
            dynamic_attribute=False,
            writable=True,
            readable=True,
            promoted=False,
            annotation="Number of joints/guides to create; modifying this attribute requires a 're-template'.",
            min_value=3,
            max_value=200,
            add_slider=False,
        )
        self.translate_ctrls_attr = self.add_boolean_attribute(
            name="Ctrls Translate",
            default_value=False,
            annotation="If checked, animators will also be able to translate the FK ctrls.",
        )
        self.sim_offset_attr = self.add_xyz_attribute(
            name="Sim Ctrl Offset",
            default_value=[13, 5, 0],
            dynamic_attribute=False,
            writable=True,
            readable=True,
            promoted=False,
            annotation=(
                "Position offset of 'simulation_ctrl' from first fk joint.\n"
                "multiplied by attribute 'Ctrls Scale'."
            ),
        )

        self.add_separator(title="Connections")
        self.driven_root_attr = self.add_driven_attribute(name="Root Input", annotation="Input")
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
                translation=[0, offset * index, 0],
                parent=parent,
                side_pin_rotation=(0, 0, 0),
                side_pin_guide=side_pin_guide if self.guides_up_shared_attr.value else None,
            )
            if side_pin_guide is None:
                side_pin_guide = guide

            self.guides_list.append(guide)
            parent = guide

        # aim guides at each other.
        for index, guide in enumerate(self.guides_list[:-1]):
            guide.aim_at = self.guides_list[index+1]

        self.guides_list[-1].aim_at = self.guides_list[-2]
        self.guides_list[-1].aim_rotation_offset = (180, 0, 0)

    def joints_creation(self):
        """Create joints based on attributes values and guides. (without positioning as this point). """
        self.joints_list = []
        parent = None
        for index in range(self.joint_count_attr.value):
            joint = self.add_joint(
                name="dyn_chain_{0}".format(index),
                skinning_jnt=True,
                tag_parent_jnt=parent,
                radius=0.5,
            )
            parent = joint
            self.joints_list.append(joint)

    def ctrls_creation(self):
        """Create controls based on attributes values, guides and joints. (without positioning as this point). """
        scale_mult = self.ctrls_scale_attr.value * 3.5

        self.ctrls_list = []
        self.secondary_list = []
        for index in range(len(self.joints_list)-1):
            # ctrls.
            ctrl = self.add_ctrl(
                name="dyn_chain_{0}".format(index),
                shape="circle",
                up_orient="+Y",
                size=1.5 * scale_mult,
            )
            self.ctrls_list.append(ctrl)

            # secondary ctrls.
            if self.secondary_ctrls_attr.value:
                secondary = self.add_ctrl(
                    name="dyn_chain_{0}_secondary".format(index),
                    shape="circle",
                    up_orient="+Y",
                    size=1.4 * scale_mult,
                )
                secondary.color = SECONDARY_COLOR
                self.secondary_list.append(secondary)

        # lock hide attrs on new ctrls.
        attrs = ["scaleY", "scaleZ"]
        if self.translate_ctrls_attr.value is False:
            attrs = ["translateX", "translateY", "translateZ", "scaleY", "scaleZ"]

        for ctrl in self.ctrls_list + self.secondary_list:
            for attr in attrs:
                ctrl.add_locked_hidden_attr(attr)

        self.dyn_ctrl = self.add_ctrl(
            name="simulation",
            shape="gear",
            up_orient="+Z",
            size=1.2 * scale_mult,
        )

        for attr in ["rotateX", "rotateY", "rotateZ", "scaleX", "scaleY", "scaleZ"]:
            self.dyn_ctrl.add_locked_hidden_attr(attr)

    def maya_attrs_creation(self):
        """Declare any Maya attributes that users should be able to modify. """
        self.dyn_ctrl.add_maya_attr("display_sim_curves", attr_type="bool", default_value=False)
        self.dyn_ctrl.add_maya_attr("sim_space", attr_type="enum", enum_names=["Local", "World"], default_value=1)
        self.dyn_ctrl.add_maya_attr(
            "point_lock", attr_type="enum", enum_names=["No Attach", "Base", "Tip", "BothEnds"], default_value=1,
        )
        self.dyn_ctrl.add_maya_attr("start_frame", attr_type="float", default_value=1, min=-10000, max=10000)
        self.dyn_ctrl.add_maya_attr("anim_follow_base", attr_type="float", default_value=1, min=0, max=1)
        self.dyn_ctrl.add_maya_attr("anim_follow_tip", attr_type="float", default_value=0.2, min=0, max=1)
        self.dyn_ctrl.add_maya_attr("anim_follow_damp", attr_type="float", default_value=0.2, min=0, max=10000)
        self.dyn_ctrl.add_maya_attr("mass", attr_type="float", default_value=1, min=0, max=10000)
        self.dyn_ctrl.add_maya_attr("drag", attr_type="float", default_value=0.05, min=0, max=10000)
        self.dyn_ctrl.add_maya_attr("damp", attr_type="float", default_value=0, min=0, max=10000)
        self.dyn_ctrl.add_maya_attr("stiffness", attr_type="float", default_value=0.15, min=0, max=10000)
        self.dyn_ctrl.add_maya_attr("turbulence_intensity", attr_type="float", default_value=0, min=0, max=4)
        self.dyn_ctrl.add_maya_attr("turbulence_frequency", attr_type="float", default_value=0.2, min=0, max=2)
        self.dyn_ctrl.add_maya_attr("turbulence_speed", attr_type="float", default_value=0.2, min=0, max=2)

    def rig_creation(self):
        """Based on attributes value, guides (which now you can get global position from) joints and controls
        created in their methods you can build the rig.
        """
        ctrls_scale = self.ctrls_scale_attr.value

        if self.is_mirrored:
            self.module_grp.set_attr("scaleX", -1)

        # last jnt doesn't have a ctrl but should behave like it does.
        ctrls_list = [ctrl.pointer for ctrl in self.ctrls_list]
        tip_trans = IoTransform("{0}_tip_twist_transform".format(self.name))
        tip_trans.btm_ctrl = tip_trans
        tip_trans.offset_grp = tip_trans
        ctrls_list.append(tip_trans)

        grps = create_grps(self, ["input_root_grp", "output_root_grp", "output_tip_grp"])
        input_root_grp, output_root_grp, output_tip_grp = grps

        self.driven_root_attr.set_maya_object(input_root_grp)
        self.driver_root_attr.set_maya_object(output_root_grp)
        self.driver_tip_attr.set_maya_object(output_tip_grp)

        jnts_grp, ctrls_grp = create_grps(self, ["jnts_grp", "ctrls_grp"])
        sim_grp, locs_grp = create_grps(self, ["sim_grp", "curve_follow_locs_grp"])

        if self.is_mirrored:
            sim_grp.set_attr("scaleX", -1)


        ctrls_grp.set_translation(self.guides_list[0].world_transformations["translate"])
        world_rotation(ctrls_grp, self.world_orientation_attr.display_value, twist=self.world_twist_attr.value)
        jnts_grp.set_translation(self.guides_list[0].world_transformations["translate"])

        secondary_ctrls_setup(self.ctrls_list, self.secondary_list)

        parent_jnt = self.joints_list[0].pointer
        parent_jnt.parent_relative(jnts_grp)
        parent_ctrl = ctrls_list[0]
        parent_ctrl.offset_grp.parent_relative(ctrls_grp)
        parent_pos = self.guides_list[0].world_transformations["translate"]

        scale_const = mc.scaleConstraint(parent_ctrl.btm_ctrl, parent_jnt, maintainOffset=False)[0]
        mc.disconnectAttr(parent_ctrl.btm_ctrl.attr("scale"), "{0}.target[0].targetScale".format(scale_const))
        mc.connectAttr(parent_ctrl.btm_ctrl.attr("scaleX"), "{0}.target[0].targetScaleX".format(scale_const))
        mc.connectAttr(parent_ctrl.btm_ctrl.attr("scaleX"), "{0}.target[0].targetScaleY".format(scale_const))
        mc.connectAttr(parent_ctrl.btm_ctrl.attr("scaleX"), "{0}.target[0].targetScaleZ".format(scale_const))

        for ctrl, guide, jnt in zip(ctrls_list[1:], self.guides_list[1:], self.joints_list[1:]):
            jnt = jnt.pointer

            jnt.parent_relative(parent_jnt)
            ctrl.offset_grp.parent_relative(parent_ctrl.btm_ctrl)
            distance = distance_between(parent_pos, guide.world_transformations["translate"])
            ctrl.offset_grp.set_attr("translateY", distance)

            scale_const = mc.scaleConstraint(ctrl.btm_ctrl, jnt, maintainOffset=False)[0]
            mc.disconnectAttr(ctrl.btm_ctrl.attr("scale"), "{0}.target[0].targetScale".format(scale_const))
            mc.connectAttr(ctrl.btm_ctrl.attr("scaleX"), "{0}.target[0].targetScaleX".format(scale_const))
            mc.connectAttr(ctrl.btm_ctrl.attr("scaleX"), "{0}.target[0].targetScaleY".format(scale_const))
            mc.connectAttr(ctrl.btm_ctrl.attr("scaleX"), "{0}.target[0].targetScaleZ".format(scale_const))

            parent_pos = guide.world_transformations["translate"]
            parent_ctrl = ctrl
            parent_jnt = jnt

        if self.clean_transformations_attr.value is True:
            for ctrl, guide in zip(ctrls_list, self.guides_list):
                ctrl.offset_grp.set_matrix(guide.world_transformations["matrix"])
                ctrl.offset_grp.set_scale([1, 1, 1])

        else:
            for ctrl, guide in zip(ctrls_list, self.guides_list):
                ctrl.set_matrix(guide.world_transformations["matrix"])
                ctrl.set_scale([1, 1, 1])

        for ctrl in self.ctrls_list + self.secondary_list:
            ctrl.pointer.scale_attrs_connect()

        input_curve = self._create_curve(curve_name="sim_input")
        input_curve.parent(sim_grp)
        input_curve.freeze_transformations()

        btm_ctrls = [ctrl.btm_ctrl for ctrl in ctrls_list]
        self._create_driver_locs(curve=input_curve, parents=btm_ctrls)

        follicle, hair_system, output_curve = self._create_sim_nodes(input_curve=input_curve, parent_grp=sim_grp)
        folli_shape = follicle.get_shapes()[0]
        hair_shape = hair_system.get_shapes()[0]

        dyn_ctrl = self.dyn_ctrl.pointer
        dyn_ctrl.offset_grp.parent_relative(ctrls_list[0].btm_ctrl)

        dyn_ctrl.offset_grp.set_translation(
            [value * ctrls_scale for value in self.sim_offset_attr.value],
            space="object"
        )

        dyn_ctrl.add_spacer_attr()
        enable_attr = dyn_ctrl.add_attr("enable_dynamics", at="bool", dv=0, keyable=False)
        mc.setAttr(enable_attr, channelBox=True)
        show_attr = dyn_ctrl.add_attr("display_sim_curves", at="bool", dv=0, keyable=False)
        mc.setAttr(show_attr, channelBox=True)
        enums = "Local:World:"
        space_attr = dyn_ctrl.add_attr("sim_space", keyable=False, at="enum", en=enums, dv=1)
        mc.setAttr(space_attr, channelBox=True)
        enums = "No Attach:Base:Tip:BothEnds:"
        lock_attr = dyn_ctrl.add_attr("point_lock", keyable=False, at="enum", en=enums, dv=1)
        mc.setAttr(lock_attr, channelBox=True)
        dyn_ctrl.add_spacer_attr()

        start_attr = dyn_ctrl.add_attr("start_frame", dv=1, keyable=True)
        follow_base_attr = dyn_ctrl.add_attr("anim_follow_base", dv=1, min=0, max=1, keyable=True)
        follow_tip_attr = dyn_ctrl.add_attr("anim_follow_tip", dv=0.2, min=0, max=1, keyable=True)
        follow_damp_attr = dyn_ctrl.add_attr("anim_follow_damp", dv=0.2, min=0, keyable=True)
        mass_attr = dyn_ctrl.add_attr("mass", dv=1, min=0, keyable=True)
        drag_attr = dyn_ctrl.add_attr("drag", dv=0.05, min=0, keyable=True)
        damp_attr = dyn_ctrl.add_attr("damp", dv=0, min=0, keyable=True)
        stiffness_attr = dyn_ctrl.add_attr("stiffness", dv=0.15, min=0, keyable=True)

        mc.addAttr(dyn_ctrl, ln="__Turbulence__", at="enum", en="_______:")
        mc.setAttr("{0}.{1}".format(dyn_ctrl, "__Turbulence__"), keyable=True, cb=True, lock=True)
        intensity_attr = dyn_ctrl.add_attr("turbulence_intensity", dv=0, min=0, softMaxValue=4, keyable=True)
        frequency_attr = dyn_ctrl.add_attr("turbulence_frequency", dv=0.2, min=0, softMaxValue=2, keyable=True)
        speed_attr = dyn_ctrl.add_attr("turbulence_speed", dv=0.2, min=0, softMaxValue=2, keyable=True)

        mc.connectAttr(show_attr, "{0}.visibility".format(input_curve))
        mc.connectAttr(show_attr, "{0}.visibility".format(output_curve))

        remap_node = mc.createNode("remapValue", name="{0}_enable_remap".format(self.name))
        mc.connectAttr(enable_attr, "{0}.inputValue".format(remap_node))
        mc.setAttr("{0}.inputMin".format(remap_node), 0)
        mc.setAttr("{0}.inputMax".format(remap_node), 1)
        mc.setAttr("{0}.outputMin".format(remap_node), 1)
        mc.setAttr("{0}.outputMax".format(remap_node), 2)
        mc.connectAttr("{0}.outValue".format(remap_node), "{0}.simulationMethod".format(hair_shape))

        mc.connectAttr(start_attr, "{0}.startFrame".format(hair_shape))
        mc.connectAttr(lock_attr, "{0}.pointLock".format(folli_shape))
        mc.connectAttr(follow_base_attr, "{0}.attractionScale[0].attractionScale_FloatValue".format(hair_shape))
        mc.connectAttr(follow_tip_attr, "{0}.attractionScale[1].attractionScale_FloatValue".format(hair_shape))
        mc.connectAttr(follow_damp_attr, "{0}.attractionDamp".format(hair_shape))
        mc.connectAttr(mass_attr, "{0}.mass".format(hair_shape))
        mc.connectAttr(drag_attr, "{0}.drag".format(hair_shape))
        mc.connectAttr(damp_attr, "{0}.damp".format(hair_shape))
        mc.connectAttr(stiffness_attr, "{0}.stiffness".format(hair_shape))

        mc.connectAttr(intensity_attr, "{0}.turbulenceStrength".format(hair_shape))
        mc.connectAttr(frequency_attr, "{0}.turbulenceFrequency".format(hair_shape))
        mc.connectAttr(speed_attr, "{0}.turbulenceSpeed".format(hair_shape))

        remove_transform_geo = mc.createNode("transformGeometry", name="{0}_remove_input_anim".format(self.name))
        mc.connectAttr(input_root_grp.attr("worldInverseMatrix[0]"), "{0}.transform".format(remove_transform_geo))
        mc.connectAttr(input_curve.attr("local"), "{0}.inputGeometry".format(remove_transform_geo))
        mc.connectAttr(space_attr, "{0}.nodeState".format(remove_transform_geo))
        mc.connectAttr(
            "{0}.outputGeometry".format(remove_transform_geo),
            "{0}.startPosition".format(folli_shape),
            f=True,
        )

        add_transform_geo = mc.createNode("transformGeometry", name="{0}_add_input_anim".format(self.name))
        mc.connectAttr(input_root_grp.attr("worldMatrix[0]"), "{0}.transform".format(add_transform_geo))
        mc.connectAttr("{0}.outCurve".format(folli_shape), "{0}.inputGeometry".format(add_transform_geo))
        mc.connectAttr(space_attr, "{0}.nodeState".format(add_transform_geo))
        mc.connectAttr("{0}.outputGeometry".format(add_transform_geo), "{0}.create".format(output_curve), f=True)

        locs_grp.parent_relative(output_curve)
        locators = self._create_follow_locs(curve=output_curve, aim_up=btm_ctrls, parent=locs_grp)

        for jnt, loc in zip(self.joints_list, locators):
            jnt.pointer.parent_constraint_to(loc, maintainOffset=False)

        # input output grps.
        input_root_grp.match_transformation_to(ctrls_grp)
        matrix_constraint(input_root_grp, ctrls_grp, maintain_offset=True)
        matrix_constraint(self.joints_list[-1], output_tip_grp, maintain_offset=False)
        matrix_constraint(self.joints_list[0], output_root_grp, maintain_offset=False)

        if self.expose_rotation_order_attr.value:
            expose_rotation_order(self.ctrls_list + self.secondary_list)

    def _create_curve(self, curve_name):
        """Create curve with cv at each guide position.

        Args:
            curve_name (str): how to name the curve

        Returns:
            IoTransform: of the nurbsCurve parent transform
        """
        positions = [guide.world_transformations["translate"] for guide in self.guides_list]
        curve = mc.curve(
            degree=1,
            point=positions,
            knot=range(len(positions)),
            worldSpace=True,
            name="{0}_{1}_curve".format(self.name, curve_name),
        )
        curve = IoTransform(curve, existing=True)
        curve.set_attr("overrideEnabled", 1)
        curve.set_attr("overrideDisplayType", 1)
        curve.lock_and_hide_transformations(vis=False)
        mc.rename(curve.get_shapes()[0], "{0}_{1}_curveShape".format(self.name, curve_name))

        return curve

    def _create_driver_locs(self, curve, parents):
        """Create locators under ctrls to drive the curve.

        Args:
            curve (IoTransform): transform parent of a nurbsCurve
            parents (list): of transforms to parent under
        """
        positions = [guide.world_transformations["translate"] for guide in self.guides_list]
        for index, position in enumerate(positions):
            loc = IoTransform(mc.spaceLocator(n="{0}_driver_{1}_loc".format(self.name, index))[0], existing=True)
            parent = parents[index] if len(parents)-1 >= index else parents[len(parents)-1]
            loc.parent_relative(parent)
            loc.set_translation(position, space="world")
            mc.connectAttr(loc.attr("worldPosition[0]"), "{0}.controlPoints[{1}]".format(curve, index))
            loc.hide()
            loc.lock_and_hide_transformations(vis=False)

    def _create_sim_nodes(self, input_curve, parent_grp):
        """manually create the nHair simulation nodes and connections including the output curve.

        Args:
            input_curve (IoTransform): parent transform of curve to turn dynamic
            parent_grp (IoTransform): transform to parent created nodes under

        Returns:
            list: of dynamic nodes [follicle, hairSystem, output_curve]
        """
        folli_trans = IoTransform("{0}_folli".format(self.name))
        mc.createNode("follicle", name="{0}_folliShape".format(self.name), parent=folli_trans)
        folli_trans.parent_relative(parent_grp)
        folli_trans.hide()

        hair_sys_trans = IoTransform("{0}_hairSystem".format(self.name))
        mc.createNode("hairSystem", name="{0}_hairSystemShape".format(self.name), parent=hair_sys_trans)
        hair_sys_trans.parent_relative(parent_grp)
        hair_sys_trans.hide()

        time_node = mc.ls(type="time")[0]
        input_shape = input_curve.get_shapes(skip_intermediate=True)[0]
        folli_shape = folli_trans.get_shapes()[0]
        hair_shape = hair_sys_trans.get_shapes()[0]

        mc.connectAttr("{0}.local".format(input_shape), "{0}.startPosition".format(folli_shape))
        mc.connectAttr("{0}.matrix".format(input_curve), "{0}.startPositionMatrix".format(folli_shape))
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

        output_curve = self._create_curve("sim_output")
        output_curve.parent(parent_grp)
        output_curve.freeze_transformations()
        mc.connectAttr("{0}.outCurve".format(folli_shape), "{0}.create".format(output_curve.get_shapes()[0]))

        return [folli_trans, hair_sys_trans, output_curve]

    def _create_follow_locs(self, curve, aim_up, parent):
        """Create locators on each cv and aim them at each other.

        Args:
            curve (IoTransform): the nurbsCurve parent transform
            aim_up (list): the 'objectRotation' for the aim constraint
            parent (IoTransform): group to parent locators under

        Returns:
            list: of created locators
        """
        locators = []
        for index, cv in enumerate(mc.ls("{0}.cv[:]".format(curve), long=True, flatten=True)):
            name = "{0}_follow_{1}_loc".format(self.name, index)
            loc = IoTransform(mc.spaceLocator(name=name)[0], existing=True)
            loc.parent_relative(parent)
            loc.connect_attr("translate", curve.attr("editPoints[{0}]".format(index)))
            loc.hide()
            locators.append(loc)


        prev_loc = locators[0]
        for loc, up_obj in zip(locators[1:], aim_up[:-1]):
            prev_loc.aim_constraint_to(
                loc,
                aimVector=(0, 1, 0),
                upVector=(1, 0, 0),
                worldUpType="objectrotation",
                worldUpObject=up_obj,
                worldUpVector=(1, 0, 0),
                maintainOffset=False,
            )
            prev_loc = loc

        locators[-1].aim_constraint_to(
            locators[-2],
            aimVector=(0, -1, 0),
            upVector=(1, 0, 0),
            worldUpType="objectrotation",
            worldUpObject=aim_up[-1],
            worldUpVector=(1, 0, 0),
            maintainOffset=False,
        )

        return locators
