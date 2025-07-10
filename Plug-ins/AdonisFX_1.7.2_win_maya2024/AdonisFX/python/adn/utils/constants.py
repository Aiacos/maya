import os


class DeformerTypes:
    """Class to expose the names of all AdonisFX deformers supported."""
    SKIN       = "AdnSkin"
    RIBBON     = "AdnRibbonMuscle"
    MUSCLE     = "AdnMuscle"
    SIMSHAPE   = "AdnSimshape"
    SKIN_MERGE = "AdnSkinMerge"
    FAT        = "AdnFat"
    RELAX      = "AdnRelax"


class LocatorTypes:
    """Class to expose the names of all AdonisFX locators supported."""
    POSITION = "AdnLocatorPosition"
    DISTANCE = "AdnLocatorDistance"
    ROTATION = "AdnLocatorRotation"
    DEFAULT  = "AdnLocator"


class SensorTypes:
    """Class to expose the names of all AdonisFX sensors supported."""
    POSITION = "AdnSensorPosition"
    DISTANCE = "AdnSensorDistance"
    ROTATION = "AdnSensorRotation"


class OtherNodeTypes:
    """Class to expose the names of the AdonisFX nodes that are not
       deformers, locators or sensors."""
    EDGE_EVALUATOR = "AdnEdgeEvaluator"
    GLUE           = "AdnGlue"
    ACTIVATION     = "AdnActivation"
    REMAP          = "AdnRemap"


class ConstraintTypesNiceNames:
    """Class to expose the nice names of AdonisFX constraint types"""
    SLIDE_SEGMENT       = "Slide On Segment"
    ATTACHMENT          = "Attachments To Transform"
    ATTACHMENT_GEOMETRY = "Attachments To Geometry"
    SLIDE_GEOMETRY      = "Slide On Geometry"


class UiConstants:
    """AdonisFX UI constants class"""
    
    ABOUT_INFO = """
    AdonisFX {adn_version}
    Inbibo Ltd
    """.format(adn_version=os.getenv("ADONISFX_VERSION", None))

    ABOUT_EXTRA_INFO = """
    Copyright Inbibo Ltd, All rights reserved. Inbibo, AdonisFX
    and their respective logos are trademarks or registered
    trademarks of Inbibo Ltd.

    Developed by:
    Marco Romeo, Carlos Monteagudo, Lucas Ferry,
    Luis Albacete, Enrique Meseguer, Jose Manuel Valverde
    and Julia Visser
    """

    PLUGIN_NAME = "AdonisFX"
    ROOT_MENU_NAME = "AdonisFXMenu"
    LOG_PREFIX = "[AdonisFX]"
    INFO_PREFIX = LOG_PREFIX + "[Info]"
    WARNING_PREFIX = LOG_PREFIX + "[Warning]"
    ERROR_PREFIX = LOG_PREFIX + "[Error]"
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
    kDefault                      = 0
    kAttachmentToGeoConstraints   = 1
    kAttachmentConstraints        = 2
    kDistanceConstraints          = 3
    kFiberConstraints             = 4
    kGlueConstraints              = 5
    kHardConstraints              = 6
    kMuscleFibers                 = 7
    kSelfCollisionsVolume         = 8
    kShapePreservationConstraints = 9
    kSlideCollisionConstraints    = 10
    kSlideConstraints             = 11
    kSlideGeometryConstraints     = 12
    kSlideSegmentConstraints      = 13
    kSlidingSurface               = 14
    kSoftConstraints              = 15
    kVolumeStructure              = 16


class StatusCode:
    """Enum class to store generic status codes."""
    SUCCESS = 0
    WARNING = 1
    ERROR = 2


class RampInterpolationMode:
    """Enum class to store DCC agnostic interpolation modes for ramp attributes."""
    NONE = 0    # None, Constant
    LINEAR = 1  # Linear
    SMOOTH = 2  # Smooth, MonotoneCubic
    SPLINE = 3  # Spline, Catmull-Rom


class TurboFeatures:
    """This class provides the names of the features/inputs that can be provided to the
    AdnTurbo script.
    """
    MUMMY = "Mummy"
    MUSCLES = "Muscles"
    LOCATORS = "Locators"
    GLUE = "Glue"
    FASCIA = "Fascia"
    FAT = "Fat"
    SKIN = "Skin"
    SPACE_SCALE = "Space Scale"
