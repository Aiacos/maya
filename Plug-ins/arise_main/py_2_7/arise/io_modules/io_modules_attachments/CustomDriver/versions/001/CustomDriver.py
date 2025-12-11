"""CustomDriver attachment allows creating driver-driven connection between user specified transforms. """

import maya.cmds as mc

from arise.data_types.attachment_data import AttachmentData
from arise.utils.modules_utils import JOINTS_VIS_ATTR

MAYA_VERSION = 2016
AUTHOR = "Etay Herz"
RIG_TYPE = "Connection"
RIG_CATEGORY = "Post"
TAGS = ["connection", "driver", "custom"]
TOOL_TIP = "Using CustomDriver, any Maya transform can drive a connection."

LIST_TEXT = "List Of Ctrls And Joints"
STR_TEXT = "Input Driver Node"

CTRL_TXT = " [ctrl]"
JNT_TXT = " [joint]"

class CustomDriver(AttachmentData):
    """Here we will reimplement methods to 1) create attributes on the attachment
    2) create guides in the template module and 3) the rig method where the rig will be built.
    """
    sort_priority = 1100

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
            title="Driver Transform",
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
            annotation="Choose a ctrl or joint to be the driver.",
        )
        self.node_attr = self.add_node_attribute(
            name="Node Name",
            annotation="Enter the name of a Maya transform node to be the driver.",
            node_type="transform",
        )
        self.node_attr.set_disabled(True)
        self.close_layout()

        self.add_separator()
        self.driver_attr = self.add_driver_attribute(
            name="Custom Driver",
            annotation="Custom driver attribute"
        )

        self.close_layout()

    def evaluate(self):  # REIMPLEMENTED!
        """Add joints_infos to node joints_info_list. """
        AttachmentData.evaluate(self)

        if self.toggle_method_attr.value == LIST_TEXT:
            self.choose_ctrl_or_joint_attr.set_disabled(False)
            self.node_attr.set_disabled(True)

        else:
            self.choose_ctrl_or_joint_attr.set_disabled(True)
            self.node_attr.set_disabled(False)

        ctrls = [ctrl.default_name + CTRL_TXT for ctrl in self.top_node_data.ctrls_manager]
        jnts = [jnt.default_name + JNT_TXT for jnt in self.top_node_data.joints_manager]

        self.choose_ctrl_or_joint_attr.items = ["None"] + jnts + ctrls

    def attachment_creation(self):  # REIMPLEMENTED!
        """Setup the driver attribute based on values of the rest of the attrs and connection manager will
        take care of the rest.
        """
        driver = None
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

            else:  # when value is 'None' skip connection.
                return "'None' selected in 'Driver List'. Skipping attachment build."

            self.driver_attr.set_maya_object(node)
            driver = str(node)

        else:
            str_val = self.node_attr.value

            if str_val and mc.objExists(str_val):
                long_name = mc.ls(str_val, long=True, objectsOnly=True)

                if len(long_name) == 1:
                    self.driven_attr.set_maya_object(long_name[0])
                    driver = long_name[0]

        if driver:
            driver_vis_path = "{0}.{1}".format(driver, JOINTS_VIS_ATTR)

            if not mc.objExists(driver_vis_path):
                mc.addAttr(driver, ln=JOINTS_VIS_ATTR, at="bool", dv=1, keyable=False)

        return True
