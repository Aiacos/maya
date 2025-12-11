"""ManualConnections finds and stores connections to untagged nodes from and to the Arise Maya Nodes. """
import logging
import copy

import maya.cmds as mc

from arise.data_types.attachment_data import AttachmentData
from arise.utils.tagging_utils import UUID_CATEGORY_TAG, get_maya_nodes_with_tag
from arise.utils.decorators_utils import reset_issue_indicator
from arise.utils.math_utils import chunker

LOGGER = logging.getLogger("node_rig_logger")

MAYA_VERSION = 2016
AUTHOR = "Etay Herz"
RIG_TYPE = "Ctrls"
RIG_CATEGORY = "Post"
TAGS = ["blendshapes", "store", "connection", "preserve", "correctives", "psd", "setDrivenKey", "custom", "manual"]
TOOL_TIP = (
    "Preserve manual connections made between the node's components and other\n"
    "Maya nodes, like Blendshapes and SetDrivenKeys nodes.\n"
    "These connections will be automatically recreated during the node rebuild.\n"
    "(Read the docs for more information)"
)
IGNORE_TYPES = [
    "skinCluster", "nodeGraphEditorInfo", "defaultRenderUtilityList", "shapeEditorManager", "dagPose",
    "groupId", "objectSet", "groupParts", "shadingEngine", "ikRPsolver", "ikSCsolver", "ikSplineSolver",
    "hikSolver", "time", "HIKCharacterNode", "HIKState2GlobalSK", "CustomRigRetargeterNode",
]


class ManualConnections(AttachmentData):
    """Here we will reimplement methods to 1) create attributes on the attachment
    2) create guides in the template module and 3) the rig method where the rig will be built.
    """
    sort_priority = 650

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
    def attachment_permissions(node):
        """Return True or False if attachment allowed on node.

        Arguments:
            node {node_ptr} -- node to check permission with

        Returns:
            [bool] -- True if allowed or False if not
        """
        if list(node.node_data.ctrls_manager):
            return True

        if list(node.node_data.joints_manager):
            return True

        module = __file__.rsplit("\\", 1)[-1].rsplit("/", 1)[-1].rsplit(".", 1)[0]
        LOGGER.warning(
            "Cannot add attachment '%s' to node '%s'. Node has no ctrls or joints.",
            module, node.name,
        )
        return False

    def on_duplication(self):  # REIMPLEMENTED!
        """ Operations to do when a node is duplicated. By default does nothing but can be reimplemented by
        subclass.
        """
        self.set_internal_database_no_undo(value=copy.copy({}))

    def attributes_creation(self):  # REIMPLEMENTED!
        """Here you add the attributes. """
        self.add_separator(title="Settings")
        self.add_button(
            buttons=[
                (
                    self.store_modifications,
                    "resources/icons/save_icon.png",
                    "Save Connections Info",
                    (
                        "Save custom connections between the Maya components of the parent node\n"
                        "and untagged Maya nodes in the scene."
                    )
                ),
                (
                    self.remove_connection_info,
                    "resources/icons/cleanup_icon.png",
                    "Clear Stored Info",
                    "Remove any stored connection information.",
                ),
                (
                    self.print_connection_info,
                    "resources/icons/attachments/print.png",
                    "Print Stored Info",
                    "Print the stored connections information within this attachment.",
                ),
            ],
        )

    @reset_issue_indicator
    def store_modifications(self):
        """Store connections info between Maya nodes belonging to this node and untagged nodes. """
        if self.top_node_data.state_manager.state == "Template":
            LOGGER.warning("'%s' can only store connections info in 'Build' state", self.long_name)
            return False

        tagged_nodes = get_maya_nodes_with_tag(self.top_node_data.uuid.hex)

        connection_data = []
        for node in tagged_nodes:
            connection_data.extend(self.scan_connections(node, forward=True))
            connection_data.extend(self.scan_connections(node, forward=False))

        if not connection_data:
            self.internal_database = []
            LOGGER.warning("'%s' No connections to untagged nodes found. Nothing to store", self.long_name)
            return False

        print_info = self.readable_connections_info(connection_data)

        self.internal_database = connection_data
        LOGGER.info("'%s' stored connections: %s", self.long_name, print_info)
        return True

    def scan_connections(self, node, forward=True):
        """Search incoming connections or outgoing connections of a node.

        Args:
            node (str or IoTransform): the node to search connections from.
            forward (bool, optional): search outgoing connections or incoming. Defaults to True outgoing.

        returns:
            (list) of dicts with connection info to disconnect/connect nodes.
        """

        results = []

        conn_data = mc.listConnections(node, c=True, d=forward, p=True, source=not forward, sh=True) or []

        if not conn_data:
            return results

        for node_str, conn_str in chunker(conn_data, 2):
            conn_node = conn_str.split(".", 1)[0]

            obj_type = mc.objectType(conn_node)
            if obj_type in IGNORE_TYPES: # TODO: for sure there will be more node types to filter.
                continue

            if mc.listAttr(conn_node, category=UUID_CATEGORY_TAG):
                continue

            if obj_type == "unitConversion":

                if forward:
                    beyond_node = mc.listConnections("{0}.output".format(conn_node), d=True, p=False, sh=True)
                else:
                    beyond_node = mc.listConnections("{0}.input".format(conn_node), s=True, p=False, sh=True)

                if beyond_node:
                    if mc.listAttr(beyond_node[0], category=UUID_CATEGORY_TAG):
                        continue

            if forward:
                source_node, source_attr = node_str.split(".", 1)
                target_node, target_attr = conn_str.split(".", 1)
            else:
                source_node, source_attr = conn_str.split(".", 1)
                target_node, target_attr = node_str.split(".", 1)

            conn_info = {
                "source_node": source_node,
                "source_attr": source_attr,
                "target_node": target_node,
                "target_attr": target_attr,
            }
            results.append(conn_info)

        return results

    @staticmethod
    def readable_connections_info(conn_data):
        """Returns formatted string of connections stored.

        Args:
            conn_data (list): of dicts of connection info to format into readable text

        Returns:
            (str) readable text of connection info
        """
        print_info = ""
        for data in conn_data:
            source = data["source_node"].rsplit("|", 1)[-1]
            target = data["target_node"].rsplit("|", 1)[-1]
            print_info += "[{0}.{1} -> {2}.{3}] ".format(source, data["source_attr"], target, data["target_attr"])

        return print_info

    @reset_issue_indicator
    def remove_connection_info(self):
        """Simply removes any stored connection info data. """
        self.internal_database = {}
        LOGGER.info("'%s' Reset", self.long_name)

    @reset_issue_indicator
    def print_connection_info(self):
        """Prints to log and Maya script editor the stored connections in readable text. """
        if not self.internal_database:
            LOGGER.info("'%s' Has no stored connections info", self.long_name)
            return

        readable_info = self.readable_connections_info(self.internal_database)
        LOGGER.info(readable_info)

    def on_delete_operation(self, silent=True):  # REIMPLEMENTED!
        """Called on cleanup to disconnect attributes before nodes are deleted so no nodes will get deleted. """
        for conn_info in self.internal_database:
            source_path = "{0}.{1}".format(conn_info["source_node"], conn_info["source_attr"])
            target_path = "{0}.{1}".format(conn_info["target_node"], conn_info["target_attr"])

            warning_msg = "'%s' FAILED to disconnected: %s -> %s", self.long_name, source_path, target_path
            if len(mc.ls(conn_info["source_node"])) != 1 and len(mc.ls(conn_info["target_node"])) != 1:
                if not silent:
                    LOGGER.warning(warning_msg)

                continue

            if not mc.objExists(source_path) or not mc.objExists(target_path):
                if not silent:
                    LOGGER.warning(warning_msg)

                continue

            if not mc.isConnected(source_path, target_path):
                if not silent:
                    LOGGER.warning(warning_msg)

                continue

            try:
                mc.disconnectAttr(source_path, target_path)
                LOGGER.debug("'%s' disconnected: %s -> %s", self.long_name, source_path, target_path)

            except:
                LOGGER.warning("'%s' FAILED to disconnect: %s -> %s", self.long_name, source_path, target_path)

    def attachment_creation(self):
        """Search according to stored connection info recreate connections. """

        if not self.internal_database:
            return "No stored connection information. Skipping attachment."

        is_successful = True
        for conn_info in self.internal_database:
            source_path = "{0}.{1}".format(conn_info["source_node"], conn_info["source_attr"])
            target_path = "{0}.{1}".format(conn_info["target_node"], conn_info["target_attr"])

            error_msg = "'{0}' FAILED to reconnect: {1} -> {2}".format(self.long_name, source_path, target_path)
            if len(mc.ls(conn_info["source_node"])) != 1 and len(mc.ls(conn_info["target_node"])) != 1:
                is_successful = False
                LOGGER.warning(error_msg)
                continue

            if not mc.objExists(source_path) or not mc.objExists(target_path):
                is_successful = False
                LOGGER.warning(error_msg)
                continue

            try:
                # TODO: skip if connected already?
                mc.connectAttr(source_path, target_path, f=True)
                LOGGER.debug("'%s' connected: %s -> %s", self.long_name, source_path, target_path)

            except:
                LOGGER.warning("'%s' FAILED to connect: %s -> %s", self.long_name, source_path, target_path)
                is_successful = False

        if not is_successful:
            return "Errors reconnecting attributes."

        return True
