import os


class DeformerTypes:
    """Class to expose the names of all AdonisFX deformers supported."""
    SKIN       = "AdnSkin"
    RIBBON     = "AdnRibbonMuscle"
    MUSCLE     = "AdnMuscle"
    SIMSHAPE   = "AdnSimshape"
    SKIN_MERGE = "AdnSkinMerge"


class ConstraintTypesNiceNames:
    """Class to expose the nice names of AdonisFX constraint types"""
    SLIDE_SEGMENT       = "Slide On Segment"
    ATTACHMENT          = "Attachments To Transform"
    ATTACHMENT_GEOMETRY = "Attachments To Geometry"
    SLIDE_GEOMETRY      = "Slide On Geometry"


class AssetDefinitionImportStatusCode:
    """Enum class to format the error codes during the import process of
    an AdonisFX Asset Definition.
    """
    SUCCESS  = 0    # Fully succeeded
    WARNING  = 1    # Partially succeeded
    CRITICAL = 2    # Failed, error


class AssetDefinition:
    """Class to encapsulate constants related to AdonisFX Asset Definition."""
    TEMPLATE = {
        "__version__"   : None,
        "__dcc__"       : {"name": None},
        "assets"        : list()
    }

    ASSET_TEMPLATE = {
        "__asset__"         : None,
        "__asset_path__"    : None,
        "data"              : list()
    }

    DEFORMER_DATA_TEMPLATE = {
        "__type__"          : None,
        "__name__"          : None,
        "__full_name__"     : None,
        "__mesh_name__"     : None,
        "__num_vertices__"  : -1,
        "__num_poly__"      : -1,
        "data"              : dict()
    }

    NODE_TYPES = [
        DeformerTypes.MUSCLE,
        DeformerTypes.RIBBON,
        DeformerTypes.SKIN,
        DeformerTypes.SIMSHAPE,
        DeformerTypes.SKIN_MERGE
    ]

    NODE_FEATURES = {
        DeformerTypes.MUSCLE    : ["Settings", "Attachments", "Targets", "Slide On Segments", "Maps"],
        DeformerTypes.RIBBON    : ["Settings", "Attachments", "Targets", "Slide On Segments", "Maps"],
        DeformerTypes.SKIN      : ["Settings", "Maps"],
        DeformerTypes.SIMSHAPE  : ["Settings", "Maps"],
        DeformerTypes.SKIN_MERGE: ["Settings", "Animation Meshes", "Simulation Meshes", "Maps"]
    }


class UiConstants:
    """AdonisFX UI constants class"""
    
    ABOUT_INFO = """
    AdonisFX {adn_version}
    Inbibo LTD
    """.format(adn_version=os.getenv("ADONISFX_VERSION", None))

    ABOUT_EXTRA_INFO = """
    Copyright Inbibo Ltd, All rights reserved. Inbibo, AdonisFX
    and their respective logos are trademarks or registered
    trademarks of Inbibo Ltd.

    Developed by:
    Marco Romeo, Carlos Monteagudo, Lucas Ferry,
    Luis Albacete, Enrique Meseguer and Jose Manuel Valverde
    """

    PLUGIN_NAME = "AdonisFX"
    ROOT_MENU_NAME = "AdonisFXMenu"
    LOG_PREFIX = "[AdonisFX]"
    DIALOG_TITLE_PREFIX = "[AdonisFX]"

    TAGS_INFO = ["i", "info", "information"]
    TAGS_WARNING = ["w", "warn", "warning"]
    TAGS_ERROR = ["e", "err", "error"]
    TAGS_ABOUT = ["a", "abt", "about"]
    TAGS_QUESTION = ["q", "ques", "question"]

    MAX_SLIDING_WARNING = ("Sliding Distance value is very large relative to "
                           "the reference mesh. May take a while to "
                           "initialize or simulate. Do you want to continue "
                           "with this value?")

    MAX_COLLISION_SLIDING_WARNING = ("Sliding Distance value is very large relative "
                                     "to the collider mesh. May take a while "
                                     "to initialize or simulate. Do you want to "
                                     "continue with this value?")

    NO_COLLIDER_SLIDING_WARNING = ("Sliding Distance value set without providing "
                                   "a collision mesh. May take a while to "
                                   "initialize or simulate when adding the collision "
                                   "mesh and computing collisions. Do you want to "
                                   "continue with this value?")

class DebugDataDescriptor:
    """Class to evaluate the current debug data descriptor types 
    aligned with the debugger system.
    """
    kDefault                      = 0  # 0
    kAttachmentToGeoConstraints   = 1  # 1
    kAttachmentConstraints        = 2  # 2
    kHardConstraints              = 3  # 3
    kMuscleFibers                 = 4  # 4
    kShapePreservationConstraints = 5  # 5
    kSlideCollisionConstraints    = 6  # 6
    kSlideConstraints             = 7  # 7
    kSlideGeometryConstraints     = 8  # 8
    kSlideSegmentConstraints      = 9  # 9
    kSlidingSurface               = 10 # 10
    kSoftConstraints              = 11 # 11
