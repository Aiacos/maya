import adn.tools.maya.attribute_handlers as attr_handler

from adn.tools.maya import muscle, ribbon_muscle, simshape, skin, skin_merge
from adn.utils.constants import DeformerTypes


class MayaAssetDefinition:
    """Class to encapsulate constants necessary to manipulate AdonisFX Asset
    Definitions from the exporter and importer tools in Maya."""
    DEFORMER_NODE_ATTRIBUTES = ["envelope"]

    ATTR_IGNORE_LIST = {
        DeformerTypes.MUSCLE    : ["currentInfluence"],
        DeformerTypes.RIBBON    : ["currentInfluence"],
        DeformerTypes.SKIN      : ["currentInfluence"],
        DeformerTypes.SIMSHAPE  : ["currentInfluence"],
        DeformerTypes.SKIN_MERGE: []
    }

    ###############################
    # Export Helpers Section
    ###############################
    ATTR_GET_COMMANDS = {
        # Types
        "TdataCompound": attr_handler.get_map_attribute,

        # Special attributes: require specific treatment to get the values
        # in the right format. All these attribute names need to stay here
        # even if they use the default `get_plain_attribute` because of the
        # order of checks followed during extraction process
        # See: `extract_map_attributes` and `get_node_definition`
        "attachmentConstraintsList": attr_handler.get_attachments_attribute,
        "targets": attr_handler.get_targets_attribute,
        "slideOnSegmentConstraintsList": attr_handler.get_slide_segments_attribute,
        "gravityDirection": attr_handler.get_plain_attribute,
        "activationRemap": attr_handler.get_ramp_attribute,
        "debugColor": attr_handler.get_plain_attribute,
        "simList": attr_handler.get_sim_mesh_list_attribute,
        "animList": attr_handler.get_anim_mesh_list_attribute
    }

    # Remap to check on dictionary if feature should be exported
    ATTR_EXPORT_FEATURES_REMAP = {
        # Types
        "TdataCompound": "Maps",

        # Special attributes
        "attachmentConstraintsList": "Attachments",
        "targets": "Targets",
        "slideOnSegmentConstraintsList": "Slide On Segments",
        "gravityDirection": "Settings",
        "simList": "Simulation Meshes",
        "animList": "Animation Meshes"
    }
    ATTR_EXPORT_FEATURES_REMAP_DEFAULT = "Settings"

    ###############################
    # Import Helpers Section
    ###############################
    ATTR_SET_COMMANDS = {
        # Types
        "TdataCompound": attr_handler.set_map_attribute,

        # Special attributes
        "attachmentConstraintsList": attr_handler.set_attachment_attributes,
        "targets": attr_handler.set_targets_attribute,
        "slideOnSegmentConstraintsList": attr_handler.set_slide_segments_attributes,
        "gravityDirection": attr_handler.set_numeric_compound_attribute,
        "activationRemap": attr_handler.set_ramp_attribute,
        "debugColor": attr_handler.set_numeric_compound_attribute,
        "fibersList": attr_handler.set_numeric_compound_map_attribute,
        "simList": attr_handler.set_sim_mesh_list_attribute,
        "animList": attr_handler.set_anim_mesh_list_attribute
    }

    ATTR_IMPORT_FEATURES_REMAP = {
        # Remap to check on dictionary if feature should be imported or not.
        # Types
        "TdataCompound": "Maps",
        "compound": "Maps",

        # Special attributes
        "attachmentConstraintsList": "Attachments",
        "targets": "Targets",
        "slideOnSegmentConstraintsList": "Slide On Segments",
        "gravityDirection": "Settings",
        "simList": "Simulation Meshes",
        "animList": "Animation Meshes"
    }
    ATTR_IMPORT_FEATURES_REMAP_DEFAULT = "Settings"

    NODE_CREATOR = {
        DeformerTypes.MUSCLE    : muscle.create_default_muscle,
        DeformerTypes.RIBBON    : ribbon_muscle.create_default_ribbon_muscle,
        DeformerTypes.SKIN      : skin.create_default_skin,
        DeformerTypes.SIMSHAPE  : simshape.create_default_simshape,
        DeformerTypes.SKIN_MERGE: skin_merge.create_default_skin_merge
    }

    NODE_CREATOR_CHECK = {
        DeformerTypes.MUSCLE    : lambda data : (True, ""), # Nothing to check
        DeformerTypes.RIBBON    : lambda data : (True, ""), # Nothing to check
        DeformerTypes.SKIN      : skin.check_dependencies_on_import,
        DeformerTypes.SIMSHAPE  : lambda data : (True, ""), # Nothing to check
        DeformerTypes.SKIN_MERGE: lambda data : (True, "")  # Nothing to check
    }
