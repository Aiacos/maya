"""BlendshapesConn finds and stores connections to blendshapes nodes from the Arise Maya Nodes. """
import logging
import copy

import maya.cmds as mc

from arise.data_types.attachment_data import AttachmentData
from arise.utils.tagging_utils import TAGS_PREFIX, UUID_CATEGORY_TAG
from arise.utils.math_utils import chunker

LOGGER = logging.getLogger("node_rig_logger")

MAYA_VERSION = 2016
AUTHOR = "Etay Herz"
RIG_TYPE = "Ctrls"
RIG_CATEGORY = "Post"
TAGS = ["blendshapes", "bs", "store", "connection", "preserve", "correctives", "psd"]
TOOL_TIP = (
    "With BlendshapesConn, you can create blendshapes on your character and "
    "connect them to your rig manually.\n"
    "(Read the docs for more information)"
)
IGNORE_TYPES = [
    "skinCluster", "nodeGraphEditorInfo", "defaultRenderUtilityList", "shapeEditorManager", "dagPose",
    "groupId", "objectSet", "groupParts",
]


class BlendshapesConn(AttachmentData):
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
                        "Store any custom connections between blendshapes "
                        "(or the nodes in the blendshapes' connection tree)\n"
                        "and the Maya nodes belonging to the Arise node this attachment is on."
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

    def store_modifications(self):
        """Store connections info between Maya nodes belonging to this node and blendshape nodes. """
        if self.top_node_data.state_manager.state == "Template":
            LOGGER.warning("'%s' can only store connections info in 'Build' state", self.long_name)
            return False

        tag = self.top_node_data.uuid.hex
        uuid_attr = "{0}{1}".format(TAGS_PREFIX, tag.replace("-", "_"))

        connection_data = []
        for bs in [bs for bs in mc.ls(type="blendShape") if not mc.listAttr(bs, category=UUID_CATEGORY_TAG)]:
            connection_data.extend(self.scan_connections(bs, uuid_attr, forward=True, recursive=6))
            connection_data.extend(self.scan_connections(bs, uuid_attr, forward=False, recursive=7))

        if not connection_data:
            self.internal_database = []
            LOGGER.warning("'%s' No connections to Blendshapes found. Nothing to store", self.long_name)
            return False

        print_info = self.readable_connections_info(connection_data)

        self.internal_database = connection_data
        LOGGER.info("'%s' stored connections: %s", self.long_name, print_info)
        return True

    def scan_connections(self, node, uuid_attr, forward=True, recursive=5, scanned_list=None):
        """Search tree pattern for connected nodes from node for tagged nodes and return dict.

        Args:
            node (str or IoTransform): the node to search connections from.
            uuid_attr (str): name of attribute to search for.
            forward (bool, optional): search outgoing connections or incoming. Defaults to True.
            recursive (int, optional): depth to search for. Defaults to 5.
            scanned_list(list or None): nodes already scanned. used by the method internally should be left alone.

        returns:
            (list) of dicts with connection info to disconnect/connect nodes.
        """
        if scanned_list is None:
            scanned_list = []

        results = []

        conn_data = mc.listConnections(node, c=True, d=forward, p=True, source=not forward, sh=True) or []
        if not conn_data:
            return results

        for node_str, conn_str in chunker(conn_data, 2):
            conn_node = conn_str.split(".", 1)[0]

            if conn_node == node:  # if connects to itself.
                continue

            if mc.objectType(conn_node) in IGNORE_TYPES:
                continue

            if conn_node in scanned_list:  # avoid repeat scan of same node (except for tagged nodes).
                continue

            if mc.objExists("{0}.{1}".format(conn_node, uuid_attr)):

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

            elif recursive >= 1:
                scanned_list.append(conn_node)

                search_results = self.scan_connections(
                    node=conn_node,
                    uuid_attr=uuid_attr,
                    forward=forward,
                    recursive=recursive-1,
                    scanned_list=scanned_list,
                )

                if search_results:
                    results.extend(search_results)

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

    def remove_connection_info(self):
        """Simply removes any stored connection info data. """
        self.internal_database = {}
        LOGGER.info("'%s' Reset", self.long_name)

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
                mc.connectAttr(source_path, target_path, f=True)
                LOGGER.debug("'%s' connected: %s -> %s", self.long_name, source_path, target_path)

            except:
                LOGGER.warning("'%s' FAILED to connect: %s -> %s", self.long_name, source_path, target_path)
                is_successful = False

        if not is_successful:
            return "Errors reconnecting attributes."

        return True
