"""AddAttribute attachment allows adding attribute on a ctrl or joint and have it drive or be driven by another
attribute.
"""

import logging

import maya.cmds as mc

from arise.data_types.attachment_data import AttachmentData
from arise.utils.decorators_utils import catch_and_print_error_dec

LOGGER = logging.getLogger("node_rig_logger")

MAYA_VERSION = 2016
AUTHOR = "Etay Herz"
RIG_TYPE = "Connection"
RIG_CATEGORY = "Post"
TAGS = ["connection", "attribute",]
TOOL_TIP = "Add an attribute to a ctrl or joint and have it driven and/or drive another attribute."

MAKE_ATTR_LIST = ["Keyable", "Displayable", "Hidden"]
DATA_TYPES_LIST = ["Vector", "Integer", "String", "Float", "Boolean", "Enum"]
DATA_TYPES_DICT = {
    "Vector": ["attributeType", "double3"],
    "Integer": ["attributeType", "long"],
    "String": ["dataType", "string"],
    "Float": ["attributeType", "double"],
    "Boolean": ["attributeType", "bool"],
    "Enum": ["attributeType", "enum"],
    }

CTRL_TXT = " [ctrl]"
JNT_TXT = " [joint]"


class AddAttribute(AttachmentData):
    """Here we will reimplement methods to 1) create attributes on the attachment
    2) create guides in the template module and 3) the rig method where the rig will be built.
    """
    sort_priority = 1400

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
        """Reimplemented to return True if more then one attachment of this type is allowed. """
        return True

    @staticmethod
    def support_copy_settings():  # REIMPLEMENTED!
        """Return True if this attachment supports copying settings between nodes of same module. Reimplemented
        by subclasses that do support copy settings to return True. default is to return False.
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
        if list(node.node_data.ctrls_manager) or list(node.node_data.joints_manager):
            return True

        return False

    def attributes_creation(self):  # REIMPLEMENTED!
        """Here you add the attributes. """

        self.add_collapsible_layout(
            title="Settings",
            shown=True,
        )
        self.choose_ctrl_or_joint_attr = self.add_drop_down_attribute(
            name="Choose Transform",
            items=["None"],
            default_value="None",
            annotation="Select a ctrl or joint to add an attribute to.",
        )
        self.attr_name_attr = self.add_string_attribute(
            name="Attribute Name",
            default_value="",
            annotation="New attribute name.",
        )

        self.make_attr_attr = self.add_radio_attribute(
            "Make Attribute",
            MAKE_ATTR_LIST,
            default_value=0,
            annotation=(
                "Keyable - Allows attribute to be keyed.\n"
                "Displayable - The attribute will not be keyable but will appear in the Channel Box.\n"
                "Hidden - The attribute will be hidden (and will not be keyable)."
            ),
        )
        self.add_separator()
        self.data_type_attr = self.add_radio_attribute(
            "Data Type",
            DATA_TYPES_LIST,
            default_value=3,
            annotation=(
                "Vector - Creates a vector attribute consisting of three floating point values.\n"
                "Float - Creates a floating point attribute (a fraction).\n"
                "Integer - Creates an integer attribute (a round number).\n"
                "Boolean - Creates an attribute consisting of a True/False toggle.\n"
                "String - Creates a string attribute that accepts alphanumeric entries as data entry.\n"
                "Enum - Creates an attribute that accepts selections from a drop-down list.\n"
            ),
        )

        self.add_collapsible_layout(
            title="Numeric Properties",
            shown=False,
        )

        self.default_attr = self.add_float_attribute(
            name="Default Value",
            default_value=0.0,
            annotation="The default value for the attribute.",
        )

        self.enable_minimum = self.add_boolean_attribute(
            name="Enable Minimum",
            default_value=False,
            annotation="Enable a minimum value for the attribute.",
        )
        self.minimum_attr = self.add_float_attribute(
            name="Minimum",
            default_value=0.0,
            annotation="The minimum value the attribute can accept.",
        )

        self.enable_maximum = self.add_boolean_attribute(
            name="Enable Maximum",
            default_value=False,
            annotation="Enable a maximum value for the attribute.",
        )
        self.maximum_attr = self.add_float_attribute(
            name="Maximum",
            default_value=1.0,
            annotation="The maximum value the attribute can accept.",
        )

        self.numeric_attrs = [
            self.default_attr, self.enable_minimum, self.minimum_attr, self.enable_maximum, self.maximum_attr
        ]

        self.close_layout()

        self.add_collapsible_layout(
            title="Enum Names",
            shown=False,
        )
        self.enum_count_attr = self.add_integer_attribute(
            name="Number Of Enum Values",
            default_value=2,
            annotation="How many options will appear in the enum drop-down list.",
            min_value=2,
            max_value=6,
            add_slider=True,
        )
        self.enum_1_attr = self.add_string_attribute(
            name="Enum name 1",
            default_value="enum_1",
            annotation="Name of 1st enum option.",
        )
        self.enum_2_attr = self.add_string_attribute(
            name="Enum name 2",
            default_value="enum_2",
            annotation="Name of 2nd enum option.",
        )
        self.enum_3_attr = self.add_string_attribute(
            name="Enum name 3",
            default_value="enum_3",
            annotation="Name of 3rd enum option.",
        )
        self.enum_4_attr = self.add_string_attribute(
            name="Enum name 4",
            default_value="enum_4",
            annotation="Name of 4th enum option.",
        )
        self.enum_5_attr = self.add_string_attribute(
            name="Enum name 5",
            default_value="enum_5",
            annotation="Name of 5th enum option.",
        )
        self.enum_6_attr = self.add_string_attribute(
            name="Enum name 6",
            default_value="enum_6",
            annotation="Name of 6th enum option.",
        )

        self.enum_attrs = [
            self.enum_count_attr, self.enum_1_attr, self.enum_2_attr, self.enum_3_attr, self.enum_4_attr,
            self.enum_5_attr, self.enum_6_attr,
        ]

        self.driver_attr = self.add_custom_driver_attribute(
            name="Attribute",
            str_connection_type="attr",
            slot_color=(50, 150, 150),
            writeable=True,
            annotation="",
            allow_same_node_conn=True,
        )

        self.close_layout()

        self.string_value_attr = self.add_string_attribute(
            name="String Value",
            default_value="",
            annotation="The value of the String attribute",
            set_str_validator=False,
        )
        self.close_layout()

    def evaluate(self):  # REIMPLEMENTED!
        """Find all joints and ctrls to drop-down. and implement disabled attrs logic. """
        AttachmentData.evaluate(self)
        ctrls = [ctrl.default_name + CTRL_TXT for ctrl in self.top_node_data.ctrls_manager]
        jnts = [jnt.default_name + JNT_TXT for jnt in self.top_node_data.joints_manager]

        self.choose_ctrl_or_joint_attr.items = ["None"] + ctrls + jnts

        data_type = DATA_TYPES_LIST[self.data_type_attr.value]

        if data_type == "String":
            for attr in self.numeric_attrs + self.enum_attrs:
                attr.set_disabled(True)

            self.string_value_attr.set_disabled(False)

        elif data_type in ["Vector", "Boolean"]:
            for attr in self.numeric_attrs + self.enum_attrs:
                attr.set_disabled(True)

            self.string_value_attr.set_disabled(True)

        elif data_type in ["Integer", "Float"]:
            for attr in self.numeric_attrs:
                attr.set_disabled(False)

            for attr in self.enum_attrs:
                attr.set_disabled(True)

            # enable min max attrs.
            if not self.enable_minimum.value:
                self.minimum_attr.set_disabled(True)

            if not self.enable_maximum.value:
                self.maximum_attr.set_disabled(True)

            self.string_value_attr.set_disabled(True)

        else:  # enum.
            for attr in self.numeric_attrs + self.enum_attrs:
                attr.set_disabled(True)

            self.enum_count_attr.set_disabled(False)

            # enable enums attrs.
            count = self.enum_count_attr.value + 1
            for attr in self.enum_attrs[1:count]:
                attr.set_disabled(False)

            self.string_value_attr.set_disabled(True)

    def attachment_creation(self):  # REIMPLEMENTED!
        """Setup the driver attribute based on values of the rest of the attrs and connection manager will
        take care of the rest.
        """
        # query attributes.
        name = self.choose_ctrl_or_joint_attr.value

        if name.endswith(CTRL_TXT):
            names_to_info = {info.default_name: info for info in self.top_node_data.ctrls_manager}
            name = name[:-len(CTRL_TXT)]
            node = names_to_info[name].pointer

        elif name.endswith(JNT_TXT):
            names_to_info = {info.default_name: info for info in self.top_node_data.joints_manager}
            name = name[:-len(JNT_TXT)]
            node = names_to_info[name].pointer

        else:  # when value is 'None' skip attachment.
            return "No transform specified in 'Choose Transform'. Attachment skipped."

        attr_name = self.attr_name_attr.value
        if attr_name.strip() == "":
            return "'Attribute Name' was not specified. Attachment skipped."

        args_dict = {}
        data_type = DATA_TYPES_LIST[self.data_type_attr.value]
        args_dict[DATA_TYPES_DICT[data_type][0]] = DATA_TYPES_DICT[data_type][1]

        if data_type in ["Integer", "Float"]:
            args_dict["defaultValue"] = self.default_attr.value

            if self.enable_minimum.value:
                args_dict["minValue"] = self.minimum_attr.value

            if self.enable_maximum.value:
                args_dict["maxValue"] = self.maximum_attr.value

        elif data_type == "Enum":
            enums_str = ""
            count = self.enum_count_attr.value + 1
            for attr in self.enum_attrs[1:count]:
                enums_str += attr.value
                enums_str += ":"

            args_dict["enumName"] = enums_str

        # create attribute.
        new_attrs = self.create_attr(node, attr_name, args_dict)

        if new_attrs is False:
            return False

        if data_type == "String":
            mc.setAttr(new_attrs, self.string_value_attr.value, type="string")

        new_attrs = [new_attrs]

        if data_type == "Vector":
            # XYZ attrs.
            args_dict["parent"] = attr_name
            args_dict["attributeType"] = "double"
            for axis in "XYZ":
                new_axis_attr = self.create_attr(node, "{0}{1}".format(attr_name, axis), args_dict)
                if new_axis_attr is False:
                    return False

                new_attrs.append(new_axis_attr)

        for attr in new_attrs:
            self.make_attribute(attr)

        self.driver_attr.set_maya_object([node, attr_name])

        return True

    def create_connections(self):  # REIMPLEMENTED!
        """Method called when custom connections on the attachment. Allows attachment to handle connections.
        To be reimplemented by some attachments.

        Returns:
            bool or None -- if False failed to build, True was successful
        """
        if not self.driver_attr.driver_attribute:
            LOGGER.debug("There are no incoming connections. '%s'", self.driver_attr)
            return None

        driver_list = self.driver_attr.driver_attribute.maya_object
        if not driver_list:
            LOGGER.warning("Error while making connection. '%s'", self.driver_attr)
            return False

        driver_attr = "{0}.{1}".format(driver_list[0], driver_list[1])
        if not mc.objExists(driver_attr):
            LOGGER.warning("Error making connection. Driver is not an attribute. '%s'", self.driver_attr)
            return False

        driven_list = self.driver_attr.maya_object
        driven_attr = "{0}.{1}".format(driven_list[0], driven_list[1])
        if not mc.objExists(driven_attr):
            LOGGER.error("Error making connection. Driven is not an attribute. '%s'", self.driver_attr)
            return False

        try:
            mc.connectAttr(driver_attr, driven_attr, f=True)

        except Exception as err:
            msg = "'{0}' attribute connection error. Check Script Editor for details".format(self.long_name)
            LOGGER.warning(msg)

            print("'{0}' attribute connection error:\n{1}".format(self.long_name, err))

            return False

        return True

    @catch_and_print_error_dec
    def create_attr(self, node, attr_name, args_dict):  # keep self, used by dec.
        """Create attribute using specified dict as arguments.

        Arguments:
            node {str} -- long name of node to add attr to
            attr_name {str} -- name of new attr
            args_dict {dict} -- of args. keys are arg names, values are their values

        Returns:
            str -- long path of attribute
        """
        mc.addAttr(node, ln=attr_name, **args_dict)

        return "{0}.{1}".format(node, attr_name)

    def make_attribute(self, attr):
        """Have the attr keyable, displayable or hidden based on the value of self.make_attr.

        Arguments:
            attr {str} -- long name of existing attr
        """
        make_value = self.make_attr_attr.value
        if make_value == 0:  # keyable.
            mc.setAttr(attr, keyable=True)

        elif make_value == 1:  # displayable.
            mc.setAttr(attr, channelBox=True)

        else:  # hidden.
            return
