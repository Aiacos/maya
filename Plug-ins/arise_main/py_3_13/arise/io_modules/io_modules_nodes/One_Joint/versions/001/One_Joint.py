"""One_Joint module is one of the basic nodes that simply creates a joint with a ctrl. """

from arise.data_types import node_data
from arise.utils.matrix_utils import matrix_constraint
from arise.utils.modules_utils import (
    world_rotation, secondary_ctrls_setup, expose_rotation_order, create_grps, SECONDARY_COLOR, update_ctrls,
)

MAYA_VERSION = 2016  # the version of maya from which this module supports.
AUTHOR = "Etay Herz"  # name of person who created this module.
RIG_CATEGORY = "Basic"  # either 'Basic', 'Cartoon', 'Vfx', 'Game' or 'All'. (used when filtering).
RIG_TYPE = "All"  # Biped, Car, Quadruped, All, ... (for filtering modules in lists).
TAGS = ["basic", "simple", "prop", "joint", "ctrl"]
TOOL_TIP = "Create either a ctrl, a joint, or both."

CREATE_OPTIONS = ["Ctrl And Joint", "Only Ctrl", "Only Joint"]

node_data.NodeData.update_ctrls = update_ctrls


class One_Joint(node_data.NodeData):
    """One_Joint module is one of the basic nodes that simply creates a joint with a ctrl. """
    sort_priority = 500

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

        self.creation_attr = self.add_radio_attribute(
            name="Create",
            items=CREATE_OPTIONS,
            default_value=0,
            annotation=(
                "'Ctrl And Joint' - creates a ctrl that drives a joint.\n"
                "'Only Ctrl' - skip the joint creation.\n"
                "'Only Joint' - skip the ctrl creation.\n"
            ),
        )

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
                "if unchecked, when zeroing the ctrls, they will align with a world axis specified in the "
                "following two attributes."
            ),
            help_link="https://youtu.be/-1fpRw6oJME?t=61",
        )

        self.add_collapsible_layout(title="World Orientation", shown=False)
        items = ["+X", "+Y", "+Z", "-X", "-Y", "-Z"]
        self.world_orientation_attr = self.add_radio_attribute(
            name="World Orientation",
            items=items,
            default_value=items.index("+Y"),  # Spine points up.
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
            annotation="Exposes the ctrls 'RotateOrder' attribute in the Channel Box.",
            help_link="https://youtu.be/-1fpRw6oJME?t=149",
        )
        self.secondary_ctrls_attr = self.add_boolean_attribute(
            name="Secondary Ctrls",
            default_value=False,
            annotation="Secondary ctrl is added under the ctrl to help prevent gimbal lock.",
            help_link="https://youtu.be/-1fpRw6oJME?t=157",
        )

        self.add_separator()

        self.is_skinning_attr = self.add_boolean_attribute(
            name="Skinning Joint",
            default_value=True,
            annotation="The joint will be tagged as a skinning joint",
        )

        self.add_separator(title="Connections")
        self.driven_attr = self.add_driven_attribute(name="Input", annotation="Input")
        self.driver_attr = self.add_driver_attribute(name="Output", annotation="Output")

        self.close_layout()

    def evaluate_creation_methods(self):  # REIMPLEMENTED!
        """Reimplemented to enable/disable attrs. """
        no_ctrl = True if self.creation_attr.value == 2 else False
        no_jnt = True if self.creation_attr.value == 1 else False

        self.ctrls_scale_attr.set_disabled(no_ctrl)
        self.clean_transformations_attr.set_disabled(no_ctrl)
        self.world_orientation_attr.set_disabled(no_ctrl)
        self.world_twist_attr.set_disabled(no_ctrl)
        self.expose_rotation_order_attr.set_disabled(no_ctrl)
        self.secondary_ctrls_attr.set_disabled(no_ctrl)

        self.is_skinning_attr.set_disabled(no_jnt)

        if not no_ctrl:
            self.world_orientation_attr.set_disabled(True if self.clean_transformations_attr.value else False)
            self.world_twist_attr.set_disabled(True if self.clean_transformations_attr.value else False)

        node_data.NodeData.evaluate_creation_methods(self)

    def guides_creation(self):
        """Create guides based on attributes values. """
        self.guide = self.add_guide(name="01", translation=[0, 0, 0], rotation=[0, 0, 0])
        self.guide.shape = "sphere_with_arrow"
        self.guide.rotate_offset = [-90, 0, 0]

    def joints_creation(self):
        """Create joints based on attributes values and guides. (without positioning as this point). """
        self.joint = None
        if self.creation_attr.value != 1:
            self.joint = self.add_joint(
                name="01",
                skinning_jnt=self.is_skinning_attr.value,
                tag_parent_jnt=None,
                radius=0.5,
            )

    def ctrls_creation(self):
        """Create controls based on attributes values, guides and joints. (without positioning as this point). """
        self.ctrl = None
        self.secondary_ctrl = None
        if self.creation_attr.value != 2:
            ctrls_mult = self.ctrls_scale_attr.value * 3.5
            self.ctrl = self.add_ctrl(name="01", shape="circle", up_orient="+Y", size=1.2 * ctrls_mult)

            self.secondary_ctrl = None
            if self.secondary_ctrls_attr.value:
                self.secondary_ctrl = self.add_ctrl(name="01_secondary", shape="circle", size=1.0 * ctrls_mult)
                self.secondary_ctrl.color = SECONDARY_COLOR

            ctrls = [self.ctrl, self.secondary_ctrl] if self.secondary_ctrl else [self.ctrl]
            for ctrl in ctrls:
                ctrl.add_locked_hidden_attr("scaleY")
                ctrl.add_locked_hidden_attr("scaleZ")

    def rig_creation(self):
        """Using the attributes values, guides, joints, and ctrls, build the rig. """
        if self.is_mirrored:
            self.module_grp.set_attr("scaleX", -1)

        no_ctrl = True if self.creation_attr.value == 2 else False
        no_jnt = True if self.creation_attr.value == 1 else False

        input_grp, output_grp = create_grps(self, ["input_grp", "output_grp"])

        self.driven_attr.set_maya_object(input_grp)
        self.driver_attr.set_maya_object(output_grp)

        ctrl, ctrl_grp = None, None
        if not no_ctrl:
            ctrl, ctrl_grp = self._setup_ctrl()

        jnt, jnts_grp = None, None
        if not no_jnt:
            jnt, jnts_grp = self._setup_jnt()

            if not no_ctrl:
                matrix_constraint(ctrl.btm_ctrl, jnts_grp, maintain_offset=False)

        top_driver = ctrl_grp if ctrl_grp else jnts_grp
        btm_driven = jnt if jnt else ctrl.btm_ctrl
        input_grp.match_transformation_to(top_driver)
        matrix_constraint(input_grp, top_driver, maintain_offset=True)
        matrix_constraint(btm_driven, output_grp, maintain_offset=False)

    def _setup_ctrl(self):
        """Setup the ctrl.

        Returns:
            list -- of ctrl IoTransform and 'joints_grp' IoTransform
        """
        ctrls_grp = create_grps(self, ["ctrls_grp"])[0]

        ctrl = self.ctrl.pointer
        ctrl.offset_grp.parent_relative(ctrls_grp)

        secondary_ctrls_setup([self.ctrl], [self.secondary_ctrl])

        if self.expose_rotation_order_attr.value:
            expose_rotation_order([self.ctrl, self.secondary_ctrl])

        ctrls_grp.set_translation(self.guide.world_transformations["translate"], space="world")

        world_rotation(
            obj=ctrl.offset_grp,
            aim_direction=self.world_orientation_attr.display_value,
            flip_x_direction=False,
            twist=self.world_twist_attr.value,
        )

        if self.clean_transformations_attr.value:
            ctrl.offset_grp.set_matrix(self.guide.world_transformations["matrix"])
        else:
            ctrl.set_matrix(self.guide.world_transformations["matrix"])

        ctrl.offset_grp.set_scale([1, 1, 1])  # fix for when set_matrix gives -1 scaleX.
        ctrl.scale_attrs_connect()

        return ctrl, ctrls_grp

    def _setup_jnt(self):
        """Setup the joint.

        Returns:
            list -- of IoJoint and IoTransform 'joints_grp'
        """
        jnts_grp = create_grps(self, ["jnts_grp"])[0]

        jnt_ptr = self.joint.pointer
        jnt_ptr.parent_relative(jnts_grp)

        jnts_grp.set_matrix(self.guide.world_transformations["matrix"])
        jnts_grp.set_scale([1, 1, 1])  # fix for when set_matrix gives -1 scaleX.

        return jnt_ptr, jnts_grp
