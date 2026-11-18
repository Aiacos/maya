"""CustomDriven attachment allows creating driver-driven connection between user specified transforms. """

import maya.cmds as mc

from arise.data_types.attachment_data import AttachmentData
from arise.scene_data.connection_manager import CONNECTION_TYPES

MAYA_VERSION = 2016
AUTHOR = "Etay Herz"
RIG_TYPE = "Connection"
RIG_CATEGORY = "Post"
TAGS = ["connection", "driven", "custom"]
TOOL_TIP = "Using CustomDriven, any Maya transform can be driven via a connection."

LIST_TEXT = "List Of Ctrls And Joints"
STR_TEXT = "Input Driven Node"
WORLD_UP_TYPE = {
    "Scene Up": "scene",
    "Object Up": "object",
    "Object Rotation Up": "objectrotation",
    "Vector": "vector",
    "None": "none",
    }

CTRL_TXT = " [ctrl]"
JNT_TXT = " [joint]"

class CustomDriven(AttachmentData):
    """Here we will reimplement methods to 1) create attributes on the attachment
    2) create guides in the template module and 3) the rig method where the rig will be built.
    """
    sort_priority = 1000

    def __init__(self, parent, icon, docs, module_dict):
        AttachmentData.__init__(
            self,
            parent=parent,
            icon=icon,
            docs=docs,
            module_dict=module_dict
        )

    @property
    def category(self):  # REIMPLEMENTED!
        """Returns the category number. 1-'build', 2-'finalize', 3-'post'. """
        return 3

    @staticmethod
    def support_multi_instences_on_node():  # REIMPLEMENTED!
        """Reimplemented to return True as more then one attachment of this type is allowed. """
        return True

    @staticmethod
    def support_copy_settings():  # REIMPLEMENTED!
        """Return True if this attachment supports copying settings between nodes of same module.
        Reimplemented by subclasses that do support copy settings to return True. default is to return False.
        """
        return True

    @staticmethod
    def attachment_permissions(node):  # REIMPLEMENTED!
        """Return True or False if attachment allowed on node.

        Arguments:
            node {node_ptr} -- node to check permission with

        Returns:
            [bool] -- True if allowed or False if not
        """
        return True

    def attributes_creation(self):  # REIMPLEMENTED!
        """Here you add the attributes. """

        self.add_collapsible_layout(
            title="Settings",
            shown=True,
        )

        self.add_frame_layout(
            title="Driven Transform",
        )
        self.toggle_method_attr = self.add_drop_down_attribute(
            name="Method",
            items=[LIST_TEXT, STR_TEXT],
            default_value=LIST_TEXT,
            annotation="Choose between selecting a ctrl/joint from a list or inputting a transform node name.",
        )

        self.add_separator()
        self.choose_ctrl_or_joint_attr = self.add_drop_down_attribute(
            name="List",
            items=["None"],
            default_value="None",
            annotation="Choose a ctrl or joint to be driven.",
        )
        self.node_attr = self.add_node_attribute(
            name="Node Name",
            annotation="Enter the name of the Maya transform node to be driven.",
            node_type="transform",
        )
        self.node_attr.set_disabled(True)
        self.close_layout()

        self.driven_attr = self.add_driven_attribute(
            name="Custom Driven",
            annotation=(
                "Also appears on the attachment shape. Will appear yellow once the attribute is connected.\n"
                "You can also input the name of a transform driver."
            ),
        )

        self.add_frame_layout(
            title="Connection Settings",
        )
        self.connection_type_attr = self.add_drop_down_attribute(
            name="Connection Type",
            items=CONNECTION_TYPES,
            default_value=CONNECTION_TYPES[0],
            annotation=(
                "Select the type of connection you want.\n"
                "Depending on your selection, the attributes below will either be enabled or disabled."
            ),
        )

        self.maintain_offset_attr = self.add_boolean_attribute(
            name="Maintain Offset",
            default_value=True,
            annotation="Maintains the current position/rotation of the driven transform.",
        )
        self.force_connection_attr = self.add_boolean_attribute(
            name="Force Connection",
            default_value=False,
            annotation=(
                "Disconnect any existing connections.\n"
                "When unchecked, any attribute already connected will be skipped."
            ),
        )
        self.force_when_locked_attr = self.add_boolean_attribute(
            name="Force When Locked",
            default_value=False,
            annotation="When unchecked, locked attributes are skipped.",
        )

        # skip attrs.
        self.add_collapsible_layout(
            title="Attributes",
            shown=False,
        )
        self.translate_x_attr = self.add_boolean_attribute(
            name="TranslateX",
            default_value=True,
            annotation="If unchecked will skip translateX.",
        )
        self.translate_y_attr = self.add_boolean_attribute(
            name="TranslateY",
            default_value=True,
            annotation="If unchecked will skip translateY.",
        )
        self.translate_z_attr = self.add_boolean_attribute(
            name="TranslateZ",
            default_value=True,
            annotation="If unchecked will skip translateZ.",
        )
        self.rotate_x_attr = self.add_boolean_attribute(
            name="RotateX",
            default_value=True,
            annotation="If unchecked will skip RotateX.",
        )
        self.rotate_y_attr = self.add_boolean_attribute(
            name="RotateY",
            default_value=True,
            annotation="If unchecked will skip RotateY.",
        )
        self.rotate_z_attr = self.add_boolean_attribute(
            name="RotateZ",
            default_value=True,
            annotation="If unchecked will skip RotateZ.",
        )
        self.scale_x_attr = self.add_boolean_attribute(
            name="ScaleX",
            default_value=True,
            annotation="If unchecked will skip ScaleX.",
        )
        self.scale_y_attr = self.add_boolean_attribute(
            name="ScaleY",
            default_value=True,
            annotation="If unchecked will skip ScaleY.",
        )
        self.scale_z_attr = self.add_boolean_attribute(
            name="ScaleZ",
            default_value=True,
            annotation="If unchecked will skip ScaleZ.",
        )
        self.close_layout()

        # aim constraint settings.
        self.add_collapsible_layout(
            title="Aim Constraint Settings",
            shown=False,
        )
        self.offset_attr = self.add_xyz_attribute(
            name="Offset",
            default_value=(0, 0, 0),
            annotation="Offset aim direction (degrees).",
        )
        self.aim_vector_attr = self.add_xyz_attribute(
            name="Aim Vector",
            default_value=(0, 1, 0),
            annotation="Direction of the aim vector relative to the driven object's local space (vector).",
        )
        self.up_vector_attr = self.add_xyz_attribute(
            name="Up Vector",
            default_value=(0, 0, 1),
            annotation="Direction of the up vector relative to the driven object's local space (vector).",
        )
        self.world_up_type_attr = self.add_drop_down_attribute(
            name="World Up Type",
            items=list(WORLD_UP_TYPE.keys()),
            default_value="Vector",
            annotation="Choose how the world up vector is being calculated.",
        )
        self.world_up_vector_attr = self.add_xyz_attribute(
            name="World Up Vector",
            default_value=(0, 0, 1),
            annotation="The vector in world coordinates that up vector should align with (vector).",
        )
        self.world_up_obj_attr = self.add_node_attribute(
            name="World Up Object",
            annotation="Set the DAG object used for worldUpType 'object' and 'objectrotation'.",
            node_type="transform",
        )

        self.close_layout()
        self.close_layout()
        self.close_layout()

        self.force_attrs_list = [self.force_connection_attr, self.force_when_locked_attr]

        self.trans_attrs_list = [self.translate_x_attr, self.translate_y_attr, self.translate_z_attr]
        self.rotate_attrs_list = [self.rotate_x_attr, self.rotate_y_attr, self.rotate_z_attr]
        self.scale_attrs_list = [self.scale_x_attr, self.scale_y_attr, self.scale_z_attr]
        self.all_axis_attrs_list = self.trans_attrs_list + self.rotate_attrs_list + self.scale_attrs_list

        self.aim_attrs_list = [
            self.offset_attr, self.aim_vector_attr, self.up_vector_attr, self.world_up_type_attr,
            self.world_up_vector_attr, self.world_up_obj_attr,
        ]

    def evaluate(self):  # REIMPLEMENTED!
        """Add joints_infos to node joints_info_list and manage attrs enable states. """
        AttachmentData.evaluate(self)

        if self.toggle_method_attr.value == LIST_TEXT:
            self.choose_ctrl_or_joint_attr.set_disabled(False)
            self.node_attr.set_disabled(True)

        else:
            self.choose_ctrl_or_joint_attr.set_disabled(True)
            self.node_attr.set_disabled(False)

        # populate transform list.
        ctrls = [ctrl.default_name + CTRL_TXT for ctrl in self.top_node_data.ctrls_manager]
        jnts = [jnt.default_name + JNT_TXT for jnt in self.top_node_data.joints_manager]

        self.choose_ctrl_or_joint_attr.items = ["None"] + jnts + ctrls

        # manage enable state of attrs.
        con_type = self.connection_type_attr.value
        if con_type in ["matrix_constraint", "parent_and_scale_constraint", "direct_connect"]:
            for attr in self.force_attrs_list + self.all_axis_attrs_list:
                attr.set_disabled(False)
            for attr in self.aim_attrs_list:
                attr.set_disabled(True)

        elif con_type == "parent":
            for attr in self.force_attrs_list + self.all_axis_attrs_list + self.aim_attrs_list:
                attr.set_disabled(True)

        elif con_type == "parent_constraint":
            for attr in self.force_attrs_list + self.trans_attrs_list + self.rotate_attrs_list:
                attr.set_disabled(False)
            for attr in self.scale_attrs_list + self.aim_attrs_list:
                attr.set_disabled(True)

        elif con_type == "point_constraint":
            for attr in self.force_attrs_list + self.trans_attrs_list:
                attr.set_disabled(False)
            for attr in self.rotate_attrs_list + self.scale_attrs_list + self.aim_attrs_list:
                attr.set_disabled(True)

        elif con_type == "scale_constraint":
            for attr in self.force_attrs_list + self.scale_attrs_list:
                attr.set_disabled(False)
            for attr in self.trans_attrs_list + self.rotate_attrs_list + self.aim_attrs_list:
                attr.set_disabled(True)

        elif con_type == "orient_constraint":
            for attr in self.force_attrs_list + self.rotate_attrs_list:
                attr.set_disabled(False)
            for attr in self.trans_attrs_list + self.scale_attrs_list + self.aim_attrs_list:
                attr.set_disabled(True)

        elif con_type == "aim_constraint":
            for attr in self.force_attrs_list + self.rotate_attrs_list + self.aim_attrs_list:
                attr.set_disabled(False)
            for attr in self.trans_attrs_list + self.scale_attrs_list:
                attr.set_disabled(True)

            if self.maintain_offset_attr.value is True:
                self.offset_attr.set_disabled(True)

            up_type = self.world_up_type_attr.value
            if up_type == "Vector":
                self.world_up_obj_attr.set_disabled(True)

            elif up_type in ["Scene Up", "None"]:
                self.world_up_vector_attr.set_disabled(True)
                self.world_up_obj_attr.set_disabled(True)

            elif up_type == "Object Up":
                self.world_up_vector_attr.set_disabled(True)

    def attachment_creation(self):  # REIMPLEMENTED!
        """Setup the driven attribute based on values of the rest of the attrs and connection manager will
        take care of the rest.
        """
        if self.toggle_method_attr.value == LIST_TEXT:
            name = self.choose_ctrl_or_joint_attr.value

            if name.endswith(CTRL_TXT):
                names_to_info = {info.default_name: info for info in self.top_node_data.ctrls_manager}
                name = name[:-len(CTRL_TXT)]
                node = names_to_info[name].pointer

            elif name.endswith(JNT_TXT):
                names_to_info = {info.default_name: info for info in self.top_node_data.joints_manager}
                name = name[:-len(JNT_TXT)]
                node = names_to_info[name].pointer

            else:
                return "'None' selected in 'Driven List' attribute. Skipping attachment build."

            self.driven_attr.set_maya_object(node)

        else:
            str_val = self.node_attr.value
            if str_val and mc.objExists(str_val):
                long_name = mc.ls(str_val, long=True, objectsOnly=True)

                if len(long_name) == 1:
                    self.driven_attr.set_maya_object(long_name[0])

        # connection settings. store settings on connection attribute.
        connection_type = self.connection_type_attr.value
        self.driven_attr.connection_type = connection_type

        self.driven_attr.maintain_offset = self.maintain_offset_attr.value
        self.driven_attr.force_connection = self.force_connection_attr.value
        self.driven_attr.force_when_locked = self.force_when_locked_attr.value

        skip_axis_list = []
        for attr in self.all_axis_attrs_list:
            skip_axis_list.append(not attr.value)

        self.driven_attr.skip_attrs = skip_axis_list

        self.driven_attr.offset = self.offset_attr.value
        self.driven_attr.aim_vector = self.aim_vector_attr.value
        self.driven_attr.up_vector = self.up_vector_attr.value
        self.driven_attr.world_up_type = WORLD_UP_TYPE[self.world_up_type_attr.value]
        self.driven_attr.world_up_vector = self.world_up_vector_attr.value
        self.driven_attr.world_up_object = self.world_up_obj_attr.value

        return True
