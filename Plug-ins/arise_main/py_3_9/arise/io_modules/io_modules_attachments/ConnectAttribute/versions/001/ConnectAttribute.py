"""ConnectAttribute attachment simply connects between 2 attributes. """
import logging

import maya.cmds as mc

from arise.data_types.attachment_data import AttachmentData
from arise.utils.io_nodes.io_track_node import IoTrackNode

LOGGER = logging.getLogger("node_rig_logger")

MAYA_VERSION = 2016
AUTHOR = "Etay Herz"
RIG_TYPE = "Connection"
RIG_CATEGORY = "Post"
TAGS = ["connection", "attribute",]
TOOL_TIP = "The ConnectAttribute attachment connects between existing Maya attributes."

LIST_TEXT = "List Of Ctrls And Joints"
STR_TEXT = "Input Node Name"

CTRL_TXT = " [ctrl]"
JNT_TXT = " [joint]"


class ConnectAttribute(AttachmentData):
    """Here we will reimplement methods to 1) create attributes on the attachment
    2) create guides in the template module and 3) the rig method where the rig will be built.
    """
    sort_priority = 1500

    def __init__(self, parent, icon, docs, module_dict):
        AttachmentData.__init__(
            self,
            parent=parent,
            icon=icon,
            docs=docs,
            module_dict=module_dict,
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
        if list(node.node_data.ctrls_manager) or list(node.node_data.joints_manager):
            return True

        return False

    def attributes_creation(self):  # REIMPLEMENTED!
        """Here you add the attributes. """

        self.add_collapsible_layout(
            title="Settings",
            shown=True,
        )
        self.add_frame_layout(
            title="Attribute",
        )
        self.toggle_method_attr = self.add_drop_down_attribute(
            name="Method",
            items=[LIST_TEXT, STR_TEXT],
            default_value=LIST_TEXT,
            annotation="Choose between selecting a ctrl/joint from a list or inputting a node's name.",
        )

        self.add_separator()
        self.choose_ctrl_or_joint_attr = self.add_drop_down_attribute(
            name="List",
            items=["None"],
            default_value="None",
            annotation="Choose a ctrl or joint.",
        )
        self.node_attr = self.add_node_attribute(
            name="Node Name",
            annotation="Enter the name of a Maya node.",
            node_type="node",  # any type node.
        )
        self.node_attr.set_disabled(True)

        self.add_separator()
        self.attribute_attr = self.add_string_attribute(
            name="Attribute Name",
            default_value="",
            annotation="Type the name of an existing attribute on the node you specified above.",
            set_str_validator=False,
        )
        self.add_separator()

        self.hide_attr = self.add_boolean_attribute(
            name="Hide Attribute",
            default_value=False,
            annotation="Hide the attribute from the ChannelBox.",
        )
        self.close_layout()

        self.driver_attr = self.add_custom_driver_attribute(
            name="Attribute",
            str_connection_type="attr",
            slot_color=(50, 150, 150),
            writeable=True,
            annotation="",
            allow_same_node_conn=True,
        )

        self.close_layout()

    def evaluate(self):  # REIMPLEMENTED!
        """Find all joints and ctrls to drop-down. and implement disabled attrs logic. """
        AttachmentData.evaluate(self)
        ctrls = [ctrl.default_name + CTRL_TXT for ctrl in self.top_node_data.ctrls_manager]
        jnts = [jnt.default_name + JNT_TXT for jnt in self.top_node_data.joints_manager]

        self.choose_ctrl_or_joint_attr.items = ["None"] + ctrls + jnts

        if self.toggle_method_attr.value == LIST_TEXT:
            self.choose_ctrl_or_joint_attr.set_disabled(False)
            self.node_attr.set_disabled(True)

        else:
            self.choose_ctrl_or_joint_attr.set_disabled(True)
            self.node_attr.set_disabled(False)

    def attachment_creation(self):  # REIMPLEMENTED!
        """Put attr in connection maya_object. """
        attr = None

        if not self.attribute_attr.value:
            return "Attribute 'Attribute Name' has no value. Attachment skipped."

        attr_value = self.attribute_attr.value
        attr_value = attr_value[1:] if attr_value.startswith(".") else attr_value

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
                return "Attribute 'Driven List' has been set to 'None'. Attachment skipped."

            self.driver_attr.set_maya_object([node, attr_value])
            attr = "{0}.{1}".format(str(node), attr_value)

        else:
            str_val = self.node_attr.value

            if not str_val:
                return "Attribute 'Node Name' has no value. Attachment skipped."

            if not mc.objExists(str_val):
                return "Attribute 'Node Name' value does not exist. Attachment skipped."

            long_name = mc.ls(str_val, long=True, objectsOnly=True)
            if len(long_name) != 1:
                return "Attribute 'Node Name' value is not unique. Attachment skipped."

            self.driver_attr.set_maya_object([IoTrackNode(long_name[0]), self.attribute_attr.value])
            attr = "{0}.{1}".format(long_name[0], self.attribute_attr.value)

        if attr and self.hide_attr.value and mc.objExists(attr):
            mc.setAttr(attr, keyable=False, channelBox=False)

        return True

    def create_connections(self):  # REIMPLEMENTED!
        """Method called when custom connections on the attachment, allows attachment to handle connections.
        to be reimplemented by some attachments.

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
            LOGGER.warning("Error while making connection. Driver is not an attribute. '%s'", self.driver_attr)
            return False

        driven_list = self.driver_attr.maya_object
        driven_attr = "{0}.{1}".format(driven_list[0], driven_list[1])
        if not mc.objExists(driven_attr):
            LOGGER.error("Error while making the connection. Driven is not an attribute. '%s'", self.driver_attr)
            return False

        if mc.getAttr(driver_attr, lock=True) or mc.getAttr(driven_attr, lock=True):
            LOGGER.error("Error while making the connection. The driver or driven attribute is locked.")
            return False

        try:
            mc.connectAttr(driver_attr, driven_attr, f=True)

        except Exception as err:
            msg = "'{0}' attribute connection error. Check Script Editor for details".format(self.long_name)
            LOGGER.warning(msg)

            print("'{0}' attribute connection error:\n{1}".format(self.long_name, err))

            return False

        return True
