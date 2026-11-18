"""The HumanIK attachment adds definitions for joints and ctrls according to HIK requirements. """

import logging

import maya.cmds as mc
import maya.mel as mel

from arise.utils.tagging_utils import tag_as_dont_tag
from arise.data_types.attachment_data import AttachmentData
from arise.utils.modules_utils import JOINTS_VIS_ATTR
from arise.utils.hik_name_id_dict import HUMANIK_JNTS_DICT, HUMANIK_CTRLS_DICT

LOGGER = logging.getLogger("node_rig_logger")

MAYA_VERSION = 2018
AUTHOR = "Etay Herz"
RIG_TYPE = "Customize"
RIG_CATEGORY = "Build"
TAGS = ["HIK", "games", "mocap", "ctrls", "joints", "MotionBuilder", "FullBodyIK", "Motion Capture", "Retargeting"]
TOOL_TIP = "Add HumanIK definitions to joints and ctrls."

CHARACTER_NAME = "Character_Arise"  # TODO: have this as a setting coming from scene setting window.


class HumanIK(AttachmentData):
    """Here we will reimplement methods to 1) create attributes on the attachment
    2) create guides in the template module and 3) the rig method where the rig will be built.
    """
    sort_priority = 1650

    def __init__(self, parent, icon, docs, module_dict):
        AttachmentData.__init__(
            self,
            parent=parent,
            icon=icon,
            docs=docs,
            module_dict=module_dict,
        )

    @staticmethod
    def attachment_permissions(node):
        """Return True or False if attachment allowed on node.

        Arguments:
            node {node shape pointer} -- node shape to check permission with

        Returns:
            bool -- True if allowed or False if not
        """
        if node.node_data.joints_manager:
            return True

        module = __file__.rsplit("\\", 1)[-1].rsplit("/", 1)[-1].rsplit(".", 1)[0]
        LOGGER.warning(
            "Cannot add attachment '%s' to node '%s'. Node has no joints to operate on.",
            module, node.name,
        )
        return False

    @staticmethod
    def support_copy_settings():  # REIMPLEMENTED!
        """Return True if this attachment supports copying settings between nodes of same module.
        Reimplemented by subclasses that do support copy settings to return True. default is to return False.
        """
        return True

    def attributes_creation(self):  # REIMPLEMENTED!
        """Here you add the attributes. """
        self.add_collapsible_layout(title="Settings", shown=True)

        self.add_collapsible_layout(title="HumanIK Joints", shown=True)
        self.humanik_jnts_attr = self.add_boolean_attribute(  # TODO: Do I need this checkbox? Shouldn't always be on?
            name="Define Joints",
            default_value=True,
            annotation="Define joints for HumanIK. You can modify the definition in the tree attribute below.",
        )
        self.filter_attr = self.add_boolean_attribute(
            name="Only Skinning Joints",
            default_value=True,
            annotation="When checked, only skinning joints will be displayed in the table below.",
        )

        self.jnts_tree_attr = self.add_tree_attribute("HumanIK Joints")

        self.add_button(
            buttons=[
                (
                    self.reset_hik_jnts_changes,
                    "resources/icons/cancel_icon.png",
                    "Reset Changes",
                    "Reset changes done to the 'HumanIK Joints' table above.",
                ),
            ],
        )
        self.close_layout()

        self.add_collapsible_layout(title="HumanIK Ctrls", shown=True)
        self.humanik_ctrls_attr = self.add_boolean_attribute(
            name="Define Ctrls",
            default_value=True,
            annotation=(
                "Define ctrls for HumanIK. You can modify the definition in the tree attribute below.\n"
                "Note: IK Ctrls tend to handle HumanIK in most situations."
            ),
        )
        self.ctrls_tree_attr = self.add_tree_attribute("HumanIK Ctrls")

        self.add_button(
            buttons=[
                (
                    self.reset_hik_ctrls_changes,
                    "resources/icons/cancel_icon.png",
                    "Reset Changes",
                    "Reset changes done to the 'HumanIK Ctrls' table above.",
                ),
            ],
        )
        self.close_layout()
        self.close_layout()

    def reset_hik_jnts_changes(self):
        """Clear internal_database and refresh tree_attribute. """
        self.jnts_tree_attr.set_value_with_undo({})

    def reset_hik_ctrls_changes(self):
        """Clear internal_database and refresh tree_attribute. """
        self.ctrls_tree_attr.set_value_with_undo({})

    def evaluate(self):  # REIMPLEMENTED!
        """Add joints_infos to node joints_info_list. """
        self.jnts_tree_attr.update_model(self.hik_joints_model())
        self.ctrls_tree_attr.update_model(self.hik_ctrls_model())

        self.jnts_tree_attr.set_disabled(False if self.humanik_jnts_attr.value else True)
        self.filter_attr.set_disabled(False if self.humanik_jnts_attr.value else True)
        self.ctrls_tree_attr.set_disabled(False if self.humanik_ctrls_attr.value else True)

        AttachmentData.evaluate(self)

    def on_delete_operation(self, silent=True):  # REIMPLEMENTED!
        """On cleanup un-define the joints, since deleting the joints that were the first to be assigned
        to a character HumanIK causes the whole character definition to be deleted. Same applies to ctrls. """
        unique_jnts_names = set([info.combined_name for info in self.top_node_data.joints_manager])
        self.init_hik_character()

        index_name_dict = {}
        count = mel.eval("hikGetNodeCount()")
        for index in range(count):
            curSKNode = mel.eval("hikGetSkNode(\"" + CHARACTER_NAME + "\", " + str(index) + ");")

            if curSKNode:
                index_name_dict[curSKNode] = index

        for jnt_name in unique_jnts_names:
            for sk_node, index in index_name_dict.items():
                if sk_node.endswith(jnt_name):
                    try:  # Maya HIK code is horrible and error on many edge cases. Have it error quietly.
                        mel.eval("hikRemoveSkFromCharacter(\"" + CHARACTER_NAME + "\", \"" + str(index) + "\");")
                        break

                    except:
                        break

        # Same for ctrls.
        retargeter = mel.eval("RetargeterGetName(\"" + str(CHARACTER_NAME) + "\");") or ""

        ctrls_dict = {}
        for part in mel.eval("RetargeterGetMappings(\"" + retargeter + "\");") or []:

            ctrl_definition = mc.getAttr("{0}.bodyPart".format(part))
            ctrl_name = mc.listConnections("{0}.destinationRig".format(part)) or []

            if not ctrl_name or not ctrl_definition:
                continue

            ctrls_dict[ctrl_name[0]] = ctrl_definition

        for ctrl in [info.combined_name for info in self.top_node_data.ctrls_manager]:
            for ctrl_name, ctrl_definition in ctrls_dict.items():
                if ctrl_name.endswith(ctrl):
                    try:  # Maya HIK code is horrible and error on many edge cases. Have it error quietly.
                        mel.eval("RetargeterDeleteMapping(\"" + str(retargeter) + "\", \"" + str(ctrl_definition) + "\", \"T\");")
                        mel.eval("RetargeterDeleteMapping(\"" + str(retargeter) + "\", \"" + str(ctrl_definition) + "\", \"R\");")

                    except:
                        pass

        self.update_hik_ui()

    def attachment_creation(self):  # REIMPLEMENTED!
        """Add HumanIK definitions to joints and ctrls according to UI settings. """
        is_successful = True

        result = self.define_joints()
        is_successful = False if result is False else is_successful

        result = self.define_ctrls()
        is_successful = False if result is False else is_successful

        self.update_hik_ui()

        if is_successful is False:
            return "Potential issues with HumanIK definitions. Refer to the log above for details. "

        return True

    def define_joints(self):
        """Define HumanIK joints. """

        if not self.humanik_jnts_attr.value:
            return True

        self.init_hik_character()
        names_to_info = {info.default_name: info for info in self.top_node_data.joints_manager}

        definitions_used = []
        none_definition = []
        for model_item in self.jnts_tree_attr.model.model_data:

            if model_item["attrs"][0]["value"] is False:
                continue

            jnt_info = names_to_info[model_item["name"]]
            definition = model_item["attrs"][1]["value"]

            if definition == "None":
                none_definition.append(jnt_info.combined_name)
                continue

            jnt_id = str(HUMANIK_JNTS_DICT[definition])
            definitions_used.append(jnt_id)
            jnt = str(jnt_info.pointer)

            source = mc.listConnections("{0}.drawStyle".format(jnt), source=True, plugs=True) or []
            if source:  # HumanIK code insists on controlling the joints drawStyle attribute.
                mc.disconnectAttr(source[0], "{0}.drawStyle".format(jnt))
                mc.connectAttr(
                    self.top_node_data.module_grp.attr(JOINTS_VIS_ATTR),
                    "{0}.lodVisibility".format(jnt),  # TODO: Not perfect as it will hide children too.
                    force=True,
                )

            mel.eval("setCharacterObject(\"" + jnt + "\", \"" + CHARACTER_NAME + "\", \"" + jnt_id + "\", 0);")

        is_successful = True
        if none_definition:
            LOGGER.warning("Some HumanIK enabled joints have 'None' definition: %s", none_definition)
            is_successful = False


        if len(set(definitions_used)) != len(definitions_used):
            LOGGER.warning("HumanIK joints definitions are used more than once on: %s", definitions_used)
            is_successful = False

        return is_successful

    def define_ctrls(self):
        """Define HumanIK ctrls. """

        self.init_hik_character()

        if not self.humanik_ctrls_attr.value:
            return True

        self.init_retargter()

        names_to_info = {info.default_name: info for info in self.top_node_data.ctrls_manager}

        definitions_used = []
        none_definition = []
        for model_item in self.ctrls_tree_attr.model.model_data:

            if model_item["attrs"][0]["value"] is False:
                continue

            ctrl_info = names_to_info[model_item["name"]]
            definition = model_item["attrs"][1]["value"]

            if definition == "None":
                none_definition.append(ctrl_info.combined_name)
                continue

            ctrl_id, ctrl_type = HUMANIK_CTRLS_DICT[definition]
            self.assign_effector_no_ui(ctrl_id, ctrl_type, ctrl_info.pointer)
            definitions_used.append(ctrl_id)

        is_successful = True
        if none_definition:
            LOGGER.warning("Some HumanIK enabled ctrls have 'None' definition: %s", none_definition)
            is_successful = False


        if len(set(definitions_used)) != len(definitions_used):
            LOGGER.warning("HumanIK ctrls definitions are used more than once on: %s", definitions_used)
            is_successful = False

        return is_successful

    def init_hik_character(self):
        """Initialize HumanIK character. """
        if not mc.pluginInfo("mayaHIK", q=True, loaded=True):
            mc.loadPlugin("mayaHIK", quiet=True)

        if CHARACTER_NAME not in mc.ls(type="HIKCharacterNode"):
            charachter_node = mel.eval('hikCreateCharacter("' + CHARACTER_NAME + '")')
            connected_nodes = mc.listConnections("{0}.propertyState".format(charachter_node)) or []
            tag_as_dont_tag([charachter_node] + connected_nodes)

    def init_retargter(self):
        """Initialize HumanIK retargeter. """
        if not mel.eval('hikHasCustomRig("' + CHARACTER_NAME + '")'):
            retargeter_node = mel.eval('RetargeterCreate("' + CHARACTER_NAME + '")')
            connected_nodes = mc.listConnections("{0}.source".format(retargeter_node)) or []
            tag_as_dont_tag([retargeter_node] + connected_nodes)

    def update_hik_ui(self):
        """Update HumanIK UI if it exists. """
        if mc.tabLayout('hikContextualTabs', q=True, exists=True):

            if mel.eval("hikIsDefinitionTabSelected()"):
                mel.eval("hikUpdateContextualUI();")

            elif mel.eval("hikIsCustomRigTabSelected()"):
                mel.eval("hikUpdateCustomRigUI;")

    def assign_effector_no_ui(self, ctrl_id, ctrl_type, ctrl_pointer):
        """Assign effector to HumanIK ctrl without using UI commands.

        Arguments:
            ctrl_id {str} -- HumanIK ctrl id
            ctrl_type {str} -- ctrl type used to determine if it's a button, fk or ik
            ctrl_pointer {str} -- ctrl pointer
        """
        # TODO: this method will error if for example spine has more ctrls then ribbon joints.
        # TODO: Can I handle it to print warning without failing completely?

        dest = ctrl_pointer

        try:
            body = mel.eval("hikCustomRigElementNameFromId(hikGetCurrentCharacter(), " + str(ctrl_id) + ");")
        except:
            LOGGER.warning("[HumanIK] Error finding body part. Rebuild might be needed.")
            return False

        if not body:
            LOGGER.warning("[HumanIK] Invalid ctrl assignment for %s", ctrl_pointer)
            return False

        character  = mel.eval("hikGetCurrentCharacter();")
        retargeter = mel.eval("RetargeterGetName(\"" + str(character) + "\");")


        success = 0
        if ctrl_type == "button":
            success = mel.eval("RetargeterValidateMapping(\"" + str(retargeter) + "\", \"" + str(body) + "\", \"TR\", \"" + str(dest) + "\");")

            if success == 0:
                return

            if success == 1 or success == 3:
                mel.eval("RetargeterAddMapping(\"" + str(retargeter) + "\", \"" + str(body) + "\", \"R\", \"" + str(dest) + "\", " + str(ctrl_id) + ");")

            if success == 2 or success == 3:
                mel.eval("RetargeterAddMapping(\"" + str(retargeter) + "\", \"" + str(body) + "\", \"T\", \"" + str(dest) + "\", " + str(ctrl_id) + ");")

        elif ctrl_type == "fk":
                success = mel.eval("RetargeterValidateMapping(\"" + str(retargeter) + "\", \"" + str(body) + "\", \"R\", \"" + str(dest) + "\");")

                if success != 1 and success != 3:
                    return

                mel.eval("RetargeterAddMapping(\"" + str(retargeter) + "\", \"" + str(body) + "\", \"R\", \"" + str(dest) + "\", " + str(ctrl_id) + ");")

        else:
            success = mel.eval("RetargeterValidateMapping(\"" + str(retargeter) + "\", \"" + str(body) + "\", \"T\", \"" + str(dest) + "\");")

            if success != 2 and success != 3:
                return

            mel.eval("RetargeterAddMapping(\"" + str(retargeter) + "\", \"" + str(body) + "\", \"T\", \"" + str(dest) + "\", " + str(ctrl_id) + ");")

        mel.eval('hikSetCurrentCharacter("' + CHARACTER_NAME + '")')

    def get_node_side(self):
        """Return the side of the node. If cannot find side return 'Left'.

        Returns:
            str -- side of the node
        """
        if self.top_node_data.name.startswith("R_"):
            return "Right"

        if self.top_node_data.name.startswith("L_"):
            return "Left"

        if self.top_node_data.is_mirrored:
            return "Right"

        return "Left"

    def hik_joints_model(self):
        """Return a HIK joints model. """
        model_data = []

        if self.filter_attr.value:
            infos = [info for info in self.top_node_data.joints_manager if info.skinning_jnt]
        else:
            infos = [info for info in self.top_node_data.joints_manager]

        hik_options = ["None"] + list(HUMANIK_JNTS_DICT.keys())
        side = self.get_node_side()

        for info in infos:
            humanik_value = info.human_ik.replace("*", side)

            data = {
                "info_pointer": info,
                "name": info.data_dict["default_name"],
                "attrs": [
                    {
                        "name": "define_HIK_joint",
                        "type": bool,
                        "default_value": True if info.skinning_jnt and humanik_value else False,
                        "change_pointer": None,
                    },
                    {
                        "name": "HIK_definition",
                        "type": list,
                        "range": hik_options,
                        "default_value": humanik_value if humanik_value in hik_options else hik_options[0],
                        "change_pointer": None,
                    }
                ],
            }

            model_data.append(data)

        return model_data

    def hik_ctrls_model(self):
        """Return a HIK ctrls model. """
        model_data = []
        infos = [info for info in self.top_node_data.ctrls_manager]

        hik_options = ["None"] + list(HUMANIK_CTRLS_DICT.keys())
        side = self.get_node_side()

        for info in infos:
            humanik_value = info.human_ik.replace("*", side)
            data = {
                "info_pointer": info,
                "name": info.data_dict["default_name"],
                "attrs": [
                    {
                        "name": "define_HIK_ctrl",
                        "type": bool,
                        "default_value": False if info.human_ik == "" else True,
                        "change_pointer": None,
                    },
                    {
                        "name": "HIK_definition",
                        "type": list,
                        "range": hik_options,
                        "default_value": humanik_value if humanik_value in hik_options else hik_options[0],
                        "change_pointer": None,
                    }
                ],
            }

            model_data.append(data)

        return model_data
