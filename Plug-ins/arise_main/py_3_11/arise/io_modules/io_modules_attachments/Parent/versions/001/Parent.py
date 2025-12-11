"""Parent will use parent_tags to any untagged node parented under this node tagged maya nodes and on rebuild will
reparent them.
"""

import logging

import maya.cmds as mc

from arise.utils.decorators_utils import reset_issue_indicator
from arise.data_types.attachment_data import AttachmentData
from arise.utils import tagging_utils

MAYA_VERSION = 2016
AUTHOR = "Etay Herz"
RIG_TYPE = "Connection"
RIG_CATEGORY = "Post"
TAGS = ["connection", "driven", "transform", "mesh", "rigid", "parent", "follow", ]
TOOL_TIP = "Parent attachment allows you to manually parent objects to the rig."

LOGGER = logging.getLogger("node_rig_logger")


class Parent(AttachmentData):
    """Here we will reimplement methods to 1) create attributes on the attachment
    2) create guides in the template module and 3) the rig method where the rig will be built.
    """
    sort_priority = 600

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
    def attachment_permissions(node):  # REIMPLEMENTED!
        """Return True or False if attachment allowed on node.

        Arguments:
            node {node_ptr} -- node to check permission with

        Returns:
            [bool] -- True if allowed or False if not
        """
        return True

    @staticmethod
    def support_multi_instences_on_node():  # REIMPLEMENTED!
        """Only one attachment of this type is allowed. """
        return False

    def attributes_creation(self):  # REIMPLEMENTED!
        """Here you add the attributes. """

        self.add_collapsible_layout(
            title="Settings",
            shown=True,
        )
        self.add_button(
            buttons=[
                (
                    self.store_modifications,
                    "resources/icons/attributes_icon.png",
                    "Add Parent Tags",
                    (
                        "Add a parent_tag to transforms/meshes parented to this node Maya nodes.\n"
                        "(Read docs for more information)."
                    ),
                ),
                (
                    self.remove_parent_tags,
                    "resources/icons/cancel_icon.png",
                    "Remove Parent Tags",
                    "Remove any parent tags associated with this node."
                ),
                (
                    self.print_pairs_list,
                    "resources/icons/attachments/print.png",
                    "Print Parent Tags",
                    "Print to log pairs of tagged nodes and their stored parent value."
                ),
            ],
        )

        self.close_layout()

    def evaluate(self):  # REIMPLEMENTED!
        """No evaluation is needed. """
        AttachmentData.evaluate(self)

    def attachment_creation(self):  # REIMPLEMENTED!
        """Find all tagged nodes and parent them according to parent_tag value. """
        is_successfull = True
        tag_name = "{0}{1}".format(tagging_utils.PARENT_TAG_PREFIX, self.top_node_data.uuid.hex)
        for node in tagging_utils.get_nodes_with_prefix_parent_tag(self.top_node_data.uuid.hex):
            parent_to = mc.getAttr("{0}.{1}".format(node, tag_name))

            if not mc.objExists(parent_to):
                parent_to = parent_to.rsplit("|")[-1]

                if not len(mc.ls(parent_to)) == 1:
                    msg = "[{0}] Unable to find the parent node '{1}' for '{2}'".format(
                        self.long_name, parent_to, node
                    )
                    LOGGER.warning(msg)

                    is_successfull = False
                    continue

            current_parent = mc.listRelatives(node, parent=True, fullPath=True)

            if not current_parent:  # TODO: might be parented to world. should it skip in that case?
                continue

            # if already parent - skip.
            if mc.ls(current_parent[0], uuid=True)[0] == mc.ls(parent_to, uuid=True)[0]:
                continue

            mc.parent(node, parent_to)

        msg = "Errors occurred while parenting nodes. Check log above for more information."
        return msg if not is_successfull else None

    @reset_issue_indicator
    def print_pairs_list(self):
        """Print to log pairs of 1- tagged parent_tag nodes and 2- their stored parent value. """
        tag_name = "{0}{1}".format(tagging_utils.PARENT_TAG_PREFIX, self.top_node_data.uuid.hex)
        tagged_nodes = tagging_utils.get_nodes_with_prefix_parent_tag(self.top_node_data.uuid.hex)

        if not tagged_nodes:
            LOGGER.info("Nothing tagged")
            return

        LOGGER.info("")
        LOGGER.info("Tags:")
        for index, node in enumerate(tagging_utils.get_nodes_with_prefix_parent_tag(self.top_node_data.uuid.hex)):

            if index != 0:  # make pretty print.
                LOGGER.info("")

            LOGGER.info("NODE: %s", mc.ls(node, shortNames=True)[0])
            LOGGER.info("PARENT VALUE: %s", mc.getAttr("{0}.{1}".format(node, tag_name)))

    @reset_issue_indicator
    def remove_parent_tags(self, log=True):
        """Remove any parent_tags of this node from any Maya node in the scene. """
        tagged_nodes = tagging_utils.remove_all_prefix_parent_tag(tag=self.top_node_data.uuid.hex)

        if log:
            LOGGER.info("Removed tags from: %s", mc.ls(tagged_nodes, long=False))

    @reset_issue_indicator
    def store_modifications(self):
        """Analyze the module structure and tag any untagged nodes with parent_tag. """
        if self.top_node_data.state_manager.state not in ["Rig", "Modified"]: # TODO: add popup if not in rig state.
            LOGGER.warning(
                "[parent_tag] '%s' can only parent_tag when the node is built. Switch to 'rig' first. Ignoring.",
                self.long_name,
            )
            return False

        tagged_nodes = tagging_utils.get_maya_nodes_with_tag(tag=self.top_node_data.uuid.hex)
        filter_list = tagging_utils.get_all_tagged_nodes()
        tagged_transforms = [node for node in tagged_nodes if "transform" in mc.nodeType(node, inherited=True)]

        if not tagged_transforms:
            LOGGER.warning(
                "[parent_tag] '%s' node has no Maya nodes in scene, is the node built? Ignoring.",
                self.long_name,
            )
            return False

        # remove any existing parent_tag of this node from any Maya node in scene.
        self.remove_parent_tags(log=False)

        untagged_nodes = self.get_untagged_nodes(nodes=tagged_transforms, filter_list=filter_list)

        if not untagged_nodes:
            msg = "[parent_tag] '%s' couldn't find any un-tagged nodes under any of this module nodes."
            LOGGER.warning(
                msg,
                self.long_name,
            )
            return False

        nodes_to_tag = []
        for node in untagged_nodes:
            parent_taggs = mc.listAttr(node, category=tagging_utils.PARENT_TAG_PREFIX) or []

            for attr in parent_taggs:  # remove any other parent_tag from untagged node.
                mc.deleteAttr(name=node, attribute=attr)

            parent_node = mc.listRelatives(node, parent=True, fullPath=True)[0]
            tagging_utils.tag_prefix_parent_tag(node=node, uuid=self.top_node_data.uuid.hex, value=parent_node)
            nodes_to_tag.append(mc.ls(node)[0])

        LOGGER.info("[parent_tag] '%s' tagging nodes: %s", self.long_name, nodes_to_tag)
        return True

    @staticmethod
    def get_untagged_nodes(nodes, filter_list):
        """Return untagged nodes parented under 'nodes'.

        Arguments:
            nodes {list} -- long names of maya nodes to check for unrelated transform child nodes under
            filter_list {list or set} -- long name of nodes that are node tagged.
        """
        all_children = []
        for node in nodes:
            if not mc.objExists(node):
                continue

            children = mc.listRelatives(node, children=True, fullPath=True)

            if not children:
                continue

            children = [child for child in children if "transform" in mc.nodeType(child, inherited=True)]

            for child in children:
                if child in filter_list:
                    continue

                all_children.append(child)

        return all_children
