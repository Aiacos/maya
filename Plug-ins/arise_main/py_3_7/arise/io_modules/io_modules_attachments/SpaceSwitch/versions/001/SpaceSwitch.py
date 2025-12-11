"""SpaceSwitch attachment allows adding a space switch to a ctrl. """

import logging
from functools import partial

import maya.cmds as mc

from arise.utils.io_nodes.io_transform import IoTransform
from arise.data_types.attachment_data import AttachmentData
from arise.utils.space_switch_utils import SearchReplaceUI, search_and_replace
from arise.utils import ui_utils

LOGGER = logging.getLogger("node_rig_logger")

MAYA_VERSION = 2016
AUTHOR = "Etay Herz"
RIG_TYPE = "Connection"
RIG_CATEGORY = "Post"
TAGS = ["space", "switch", "ctrl"]
TOOL_TIP = "SpaceSwitch enables you to create virtual parents for a ctrl to move and/or rotate with."

STYLES = ["enum_attr", "float_attrs"]
SPACE_CONNECTION_TYPES = ["parent_constraint", "point_constraint", "orient_constraint"]
SPACES_TYPES_DICT = {
    "parent_constraint": "parent_space_switch",
    "point_constraint": "point_space_switch",
    "orient_constraint": "orient_space_switch",
}

CTRL_TXT = " [ctrl]"
JNT_TXT = " [joint]"


class SpaceSwitch(AttachmentData):
    """Here we will reimplement methods to 1) create attributes on the attachment
    2) create guides in the template module and 3) the rig method where the rig will be built.
    """
    sort_priority = 100

    def __init__(self, parent, icon, docs, module_dict):
        AttachmentData.__init__(
            self,
            parent=parent,
            icon=icon,
            docs=docs,
            module_dict=module_dict
        )
        self.help_link = "https://youtu.be/J2dftWTx1s4?si=XQds5ipZvT-r7On_&t=4"

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
        if list(node.node_data.ctrls_manager):
            return True

        module = __file__.rsplit("\\", 1)[-1].rsplit("/", 1)[-1].rsplit(".", 1)[0]
        LOGGER.warning(
            "Cannot add attachment '%s' to node '%s'. Node has no ctrls to operate on.",
            module, node.name,
        )
        return False

    def add_qactions(self, menu):  # REIMPLEMENTED!
        """Add custom QActions to right-click context menu for this specific attachment. OPTIONAL.

        Args:
            menu (QMenu): This method will be passed the QMenu of the context menu
        """
        menu.addSection("SpaceSwitch Search & Replace")

        action_btn, action_B_btn, option_btn = ui_utils.action_with_options(
            menu=menu,
            action_label="Replace L > R",
            action_tooltip="Search & replace 'Spaces' attribute values on this SpaceSwitch from left to right",
            action_B_label="Replace R > L",
            action_B_tooltip="Search & replace 'Spaces' attribute values on this SpaceSwitch from right to left",
            options_tooltip="Options for searching & replacing",
            icon=self.main_window_ptr.swap_icon,
        )
        action_btn.released.connect(partial(search_and_replace, self, True))
        action_B_btn.released.connect(partial(search_and_replace, self, False))
        option_btn.released.connect(partial(SearchReplaceUI, self.main_window_ptr))

    def attributes_creation(self):  # REIMPLEMENTED!
        """Here you add the attributes. """
        self.add_collapsible_layout(
            title="Settings",
            shown=True,
        )

        self.switch_type_attr = self.add_drop_down_attribute(
            name="Switch Type",
            items=SPACE_CONNECTION_TYPES,
            default_value=SPACE_CONNECTION_TYPES[0],
            annotation=(
                "Should the switch affect position, rotation or both.\n"
                "'parent_constraint' - position + rotation\n"
                "'point_constraint' - position only\n"
                "'orient_constraint' - rotation only"
            ),
            help_link="https://youtu.be/J2dftWTx1s4?si=OL7N2sJ5Aj-cfLj0&t=39",
        )

        self.choose_ctrl_attr = self.add_drop_down_attribute(
            name="Ctrl",
            items=["None",],
            default_value="None",
            annotation="The ctrl to add the space switch to.",
            help_link="https://youtu.be/J2dftWTx1s4?si=dF-wNEtINsPfJGPa&t=58",
        )

        self.style_attr = self.add_radio_attribute(
            name="Style",
            items=STYLES,
            default_value=0,
            annotation=(
                "'enum_attr' - create a single dropdown attribute.\n"
                "'float_attrs' - create several float attributes allowing blending between spaces."
            ),
            help_link="https://youtu.be/J2dftWTx1s4?si=NjbS2Pn1T5yLEykd&t=65",
        )

        self.add_parent_space_attr = self.add_boolean_attribute(
            name="Add Parent Space",
            default_value=True,
            annotation="If checked, will add the parent of the ctrl as the first space called 'local'.",
            help_link="https://youtu.be/J2dftWTx1s4?si=XZk9oJkXvWlIamqC&t=88",
        )

        self.spaces_count_attr = self.add_integer_attribute(
            name="Number Of Extra Spaces",
            default_value=1,
            annotation="Number of spaces; this enables the space attributes below.",
            min_value=1,
            max_value=10,
            add_slider=True,
            help_link="https://youtu.be/J2dftWTx1s4?si=3ovz5iJRZ0KHv9wi&t=100",
        )

        self.default_space_attr = self.add_drop_down_attribute(
            name="Default Space",
            items=["None",],
            default_value="None",
            annotation="Select the space to set the spaceSwitch attribute(s) to when the rig is built.",
        )

        self.maintain_offset_attr = self.add_boolean_attribute(
            name="Maintain Offset",
            default_value=True,
            annotation=(
                "If checked (default), the space switch preserves the ctrl's offset from the space driver.\n"
                "When unchecked, the ctrl snaps to the space driver's position and rotation.\n"
                "Disable this option for actions like instantly attaching a 'weapon' to different 'holster' locations.\n"
                "Use with caution, as disabling it may cause unintended behavior!\n"
            ),
        )

        self.add_collapsible_layout(
            title="Spaces",
            shown=False,
        )
        # 1st.
        self.space_1_attr = self.add_string_attribute(
            name="Space 1 Name",
            default_value="space_1",
            annotation="Name of 1st space",
            help_link="https://youtu.be/J2dftWTx1s4?si=mbU9_Hw86MDDlZNA&t=107",
        )
        self.space_1_driven_attr = self.add_driven_attribute(
            name="Space 1",
            annotation="The transform that the ctrl will move/rotate within his space.",
            promoted=False,
            help_link="https://youtu.be/J2dftWTx1s4?si=mbU9_Hw86MDDlZNA&t=107",
        )
        self.space_1_driven_attr.connection_type = "parent"

        # 2nd.
        self.space_2_attr = self.add_string_attribute(
            name="Space 2 Name",
            default_value="space_2",
            annotation="Name of 2nd space",
            help_link="https://youtu.be/J2dftWTx1s4?si=mbU9_Hw86MDDlZNA&t=107",
        )
        self.space_2_driven_attr = self.add_driven_attribute(
            name="Space 2",
            annotation="The transform that the ctrl will move/rotate within his space.",
            promoted=False,
            help_link="https://youtu.be/J2dftWTx1s4?si=mbU9_Hw86MDDlZNA&t=107",
        )
        self.space_2_driven_attr.connection_type = "parent"

        # 3rd.
        self.space_3_attr = self.add_string_attribute(
            name="Space 3 Name",
            default_value="space_3",
            annotation="Name of 3rd space",
            help_link="https://youtu.be/J2dftWTx1s4?si=mbU9_Hw86MDDlZNA&t=107",
        )
        self.space_3_driven_attr = self.add_driven_attribute(
            name="Space 3",
            annotation="The transform that the ctrl will move/rotate within his space.",
            promoted=False,
            help_link="https://youtu.be/J2dftWTx1s4?si=mbU9_Hw86MDDlZNA&t=107",
        )
        self.space_3_driven_attr.connection_type = "parent"

        # 4th.
        self.space_4_attr = self.add_string_attribute(
            name="Space 4 Name",
            default_value="space_4",
            annotation="Name of 4th space",
            help_link="https://youtu.be/J2dftWTx1s4?si=mbU9_Hw86MDDlZNA&t=107",
        )
        self.space_4_driven_attr = self.add_driven_attribute(
            name="Space 4",
            annotation="The transform that the ctrl will move/rotate within his space.",
            promoted=False,
            help_link="https://youtu.be/J2dftWTx1s4?si=mbU9_Hw86MDDlZNA&t=107",
        )
        self.space_4_driven_attr.connection_type = "parent"

        # 5th.
        self.space_5_attr = self.add_string_attribute(
            name="Space 5 Name",
            default_value="space_5",
            annotation="Name of 5th space",
            help_link="https://youtu.be/J2dftWTx1s4?si=mbU9_Hw86MDDlZNA&t=107",
        )
        self.space_5_driven_attr = self.add_driven_attribute(
            name="Space 5",
            annotation="The transform that the ctrl will move/rotate within his space.",
            promoted=False,
            help_link="https://youtu.be/J2dftWTx1s4?si=mbU9_Hw86MDDlZNA&t=107",
        )
        self.space_5_driven_attr.connection_type = "parent"

        # 6th.
        self.space_6_attr = self.add_string_attribute(
            name="Space 6 Name",
            default_value="space_6",
            annotation="Name of 6th space",
            help_link="https://youtu.be/J2dftWTx1s4?si=mbU9_Hw86MDDlZNA&t=107",
        )
        self.space_6_driven_attr = self.add_driven_attribute(
            name="Space 6",
            annotation="The transform that the ctrl will move/rotate within his space.",
            promoted=False,
            help_link="https://youtu.be/J2dftWTx1s4?si=mbU9_Hw86MDDlZNA&t=107",
        )
        self.space_6_driven_attr.connection_type = "parent"

        # 7th.
        self.space_7_attr = self.add_string_attribute(
            name="Space 7 Name",
            default_value="space_7",
            annotation="Name of 7th space",
            help_link="https://youtu.be/J2dftWTx1s4?si=mbU9_Hw86MDDlZNA&t=107",
        )
        self.space_7_driven_attr = self.add_driven_attribute(
            name="Space 7",
            annotation="The transform that the ctrl will move/rotate within his space.",
            promoted=False,
            help_link="https://youtu.be/J2dftWTx1s4?si=mbU9_Hw86MDDlZNA&t=107",
        )
        self.space_7_driven_attr.connection_type = "parent"

        # 8th.
        self.space_8_attr = self.add_string_attribute(
            name="Space 8 Name",
            default_value="space_8",
            annotation="Name of 8th space",
            help_link="https://youtu.be/J2dftWTx1s4?si=mbU9_Hw86MDDlZNA&t=107",
        )
        self.space_8_driven_attr = self.add_driven_attribute(
            name="Space 8",
            annotation="The transform that the ctrl will move/rotate within his space.",
            promoted=False,
            help_link="https://youtu.be/J2dftWTx1s4?si=mbU9_Hw86MDDlZNA&t=107",
        )
        self.space_8_driven_attr.connection_type = "parent"

        # 9th.
        self.space_9_attr = self.add_string_attribute(
            name="Space 9 Name",
            default_value="space_9",
            annotation="Name of 9th space",
            help_link="https://youtu.be/J2dftWTx1s4?si=mbU9_Hw86MDDlZNA&t=107",
        )
        self.space_9_driven_attr = self.add_driven_attribute(
            name="Space 9",
            annotation="The transform that the ctrl will move/rotate within his space.",
            promoted=False,
            help_link="https://youtu.be/J2dftWTx1s4?si=mbU9_Hw86MDDlZNA&t=107",
        )
        self.space_9_driven_attr.connection_type = "parent"

        # 10th.
        self.space_10_attr = self.add_string_attribute(
            name="Space 10 Name",
            default_value="space_10",
            annotation="Name of 10th space",
            help_link="https://youtu.be/J2dftWTx1s4?si=mbU9_Hw86MDDlZNA&t=107",
        )
        self.space_10_driven_attr = self.add_driven_attribute(
            name="Space 10",
            annotation="The transform that the ctrl will move/rotate within his space.",
            promoted=False,
            help_link="https://youtu.be/J2dftWTx1s4?si=mbU9_Hw86MDDlZNA&t=107",
        )
        self.space_10_driven_attr.connection_type = "parent"

        self.names_attr_list = [
            self.space_1_attr, self.space_2_attr, self.space_3_attr, self.space_4_attr, self.space_5_attr,
            self.space_6_attr, self.space_7_attr, self.space_8_attr, self.space_9_attr, self.space_10_attr,
            ]
        self.driven_attrs_list = [
            self.space_1_driven_attr, self.space_2_driven_attr, self.space_3_driven_attr, self.space_4_driven_attr,
            self.space_5_driven_attr, self.space_6_driven_attr, self.space_7_driven_attr, self.space_8_driven_attr,
            self.space_9_driven_attr, self.space_10_driven_attr,
            ]

        self.close_layout()
        self.close_layout()

    def evaluate(self):  # REIMPLEMENTED!
        """Populate ctrls names drop-down and enable/disable space attrs. """
        AttachmentData.evaluate(self)
        ctrls = [ctrl.default_name + CTRL_TXT for ctrl in self.top_node_data.ctrls_manager]
        self.choose_ctrl_attr.items = ["None"] + ctrls

        up_to_index = self.spaces_count_attr.value
        for index, (name_attr, driven_attr) in enumerate(zip(self.names_attr_list, self.driven_attrs_list)):
            state = False  if index < up_to_index else True
            name_attr.set_disabled(state)
            driven_attr.set_disabled(state)

            driven_attr.maintain_offset = self.maintain_offset_attr.value

        spaces = []
        if self.add_parent_space_attr.value:
            spaces.append("local")

        for index in range(self.spaces_count_attr.value):
            spaces.append("space_{0}".format(index+1))

        self.default_space_attr.items = spaces or ["None"]


    def attachment_creation(self):  # REIMPLEMENTED!
        """Build the SpaceSwitch. """
        name = self.choose_ctrl_attr.value

        if not name.endswith(CTRL_TXT):
            return "No ctrl specified in the 'Ctrl' attribute. Skipping attachment build."

        names_to_info = {info.default_name: info for info in self.top_node_data.ctrls_manager}
        name = name[:-len(CTRL_TXT)]
        ctrl_ptr = names_to_info[name].pointer

        spaces_names = []
        if self.add_parent_space_attr.value:
            if self.style_attr.display_value == STYLES[0]:  # enum.
                spaces_names.append("local")

            else:  # float attrs.
                if self.switch_type_attr.display_value == "parent_constraint":
                    spaces_names.append("local")
                elif self.switch_type_attr.display_value == "point_constraint":
                    spaces_names.append("local_point")
                elif self.switch_type_attr.display_value == "orient_constraint":
                    spaces_names.append("local_orient")

        drivers_value_list = []
        for index in range(self.spaces_count_attr.value):
            name = self.names_attr_list[index].value
            if not name:
                name = "space_{0}".format(index+1)

            spaces_names.append(name)

            driver_name = self.driven_attrs_list[index].value
            drivers_value_list.append(driver_name)

            if driver_name == "":  # no value specified.
                msg = "No space driver specified for space: '{0}'. Skipping attachment build.".format(name)
                return msg

            # validate spaces are not driven by the ctrl which will cause a cycle.
            if self.driven_attrs_list[index].is_tracked_value:
                if self.driven_attrs_list[index]._value.is_tracked_on_this_node:
                    if self.driven_attrs_list[index]._value.get_tracked_item()[0] == ctrl_ptr:
                        msg = "Driven Ctrl can't drive itself; creates a cycle. '{0}'. ".format(name)
                        msg += "Attachment build skipped."
                        return msg

            elif self.driven_attrs_list[index].value == ctrl_ptr.unique_name:
                msg = "Driven Ctrl can't drive itself; creates a cycle. '{0}'. ".format(name)
                msg += "Attachment build skipped."
                return msg

        if len(drivers_value_list) != len(set(drivers_value_list)):  # repeating space driver.
            return "Found repeating space driver driving more then one space. Skipping attachment build."

        attr_name = SPACES_TYPES_DICT[self.switch_type_attr.value]
        if mc.objExists(ctrl_ptr.attr(attr_name)):
            msg = "# [space_switch] Ctrl: '{0}' already has the space switch attribute: '{1}'"
            msg = msg.format(ctrl_ptr.short_name, attr_name)
            LOGGER.error(msg)
            return False

        ctrl_name = ctrl_ptr.short_name
        spaces_groups_list = []
        if self.add_parent_space_attr.value:
            local_grp = ctrl_ptr.add_group_above(name="{0}__local__{1}_driver_grp".format(ctrl_name, attr_name))
            spaces_groups_list.append(local_grp)

        driven_grp = ctrl_ptr.add_group_above(name="{0}__{1}__driven_grp".format(ctrl_name, attr_name))

        for index, name in enumerate(spaces_names[1:] if self.add_parent_space_attr.value else spaces_names):
            # Maya constraints flip on mirrored unless we have an offset group to hold the values for drivers.
            name = "{0}__{1}__{2}_driver".format(ctrl_name, name, attr_name)
            space_grp_offset = IoTransform(name="{0}_offset_grp".format(name))
            space_grp_offset.parent_relative(driven_grp)
            space_grp_offset.parent(self.top_node_data.module_grp)

            space_grp = IoTransform(name="{0}_grp".format(name))
            space_grp.parent_relative(space_grp_offset)

            self.driven_attrs_list[index].set_maya_object(space_grp_offset)
            spaces_groups_list.append(space_grp)

        connection_type = self.switch_type_attr.value
        if connection_type == "parent_constraint":
            constraint = driven_grp.parent_constraint_to(
                transforms=spaces_groups_list,
                maintainOffset=False,
                name="{0}_space_switch_parentConstraint".format(ctrl_ptr.short_name),
            )
            attributes_list = mc.parentConstraint(constraint, q=True, weightAliasList=True)

        elif connection_type == "point_constraint":
            constraint = driven_grp.point_constraint_to(
                transforms=spaces_groups_list,
                maintainOffset=False,
                name="{0}_space_switch_pointConstraint".format(ctrl_ptr.short_name),
            )
            attributes_list = mc.pointConstraint(constraint, q=True, weightAliasList=True)

        elif connection_type == "orient_constraint":
            constraint = driven_grp.orient_constraint_to(
                transforms=spaces_groups_list,
                maintainOffset=False,
                name="{0}_space_switch_orientConstraint".format(ctrl_ptr.short_name),
            )
            attributes_list = mc.orientConstraint(constraint, q=True, weightAliasList=True)

        if self.style_attr.display_value == STYLES[0]:  # enum.
            attr_path = self.enum_style(ctrl_ptr, spaces_names, attributes_list, constraint)
            mc.setAttr(attr_path, self.default_space_attr.value_index)

        else:  # float attr.
            for space in spaces_names:  # Nodes can't have attrs with the same name.
                if mc.attributeQuery(space, node=ctrl_ptr, exists=True):
                    attr = "{0}.{1}".format(ctrl_ptr.short_name, space)
                    msg = "#[space_switch] Attribute: '{0}' already exists on ctrl".format(attr)
                    LOGGER.error(msg)
                    return False

            new_attrs = self.floats_style(ctrl_ptr, spaces_names, attributes_list, constraint)

            for index, attr in enumerate(new_attrs):
                mc.setAttr(attr, 1 if index == self.default_space_attr.value_index else 0)

        return True

    def enum_style(self, ctrl_ptr, spaces_names, attributes_list, constraint):
        """Create spaceSwitch that one enum attribute controls.

        Arguments:
            ctrl_ptr (IoCtrl): the ctrl getting the space switch
            spaces_names (list): of str names of spaces to create
            attributes_list (list): of attributes names on constraint
            constraint (str): name of constraint

        Returns:
            str -- the name of the enum attribute created
        """
        enums_str = ""
        for name in spaces_names:
            enums_str += "{0}:".format(name)

        ctrl_ptr.add_spacer_attr(char_min_length=6)
        attr_name = SPACES_TYPES_DICT[self.switch_type_attr.value]
        mc.addAttr(ctrl_ptr, ln=attr_name, at="enum", en=enums_str)
        mc.setAttr(ctrl_ptr.attr(attr_name), keyable=True)
        ctrl_ptr.add_spacer_attr(char_min_length=6)

        for index, const_attr in enumerate(attributes_list):
            for name_index in range(len(attributes_list)):
                mc.setDrivenKeyframe(
                    "{0}.{1}".format(constraint, const_attr),
                    currentDriver=ctrl_ptr.attr(attr_name),
                    value=1 if index == name_index else 0,
                    driverValue=name_index,
                    inTangentType="linear",
                    outTangentType="linear",
                )

        return ctrl_ptr.attr(attr_name)

    def floats_style(self, ctrl_ptr, spaces_names, attributes_list, constraint):
        """Create float attrs for each space.

        Arguments:
            ctrl_ptr (IoCtrl): the ctrl getting the space switch
            spaces_names (list): of str names of spaces to create
            attributes_list (list): of attributes names on constraint
            constraint (str): name of constraint

        Returns:
            list -- of created float attributes
        """
        attr_name = SPACES_TYPES_DICT[self.switch_type_attr.value]
        mc.addAttr(ctrl_ptr, ln=attr_name, at="enum", en="_______:")
        mc.setAttr("{0}.{1}".format(ctrl_ptr, attr_name), keyable=True, cb=True, lock=True)

        new_attrs = []
        default_value = 1
        for space, constraint_attr in zip(spaces_names, attributes_list):
            mc.addAttr(ctrl_ptr, ln=space, min=0, max=1, dv=default_value)
            new_attrs.append(ctrl_ptr.attr(space))
            mc.setAttr(ctrl_ptr.attr(space), keyable=True)
            default_value = 0

            mc.connectAttr(ctrl_ptr.attr(space), "{0}.{1}".format(constraint, constraint_attr))

        ctrl_ptr.add_spacer_attr(char_min_length=6)

        return new_attrs
