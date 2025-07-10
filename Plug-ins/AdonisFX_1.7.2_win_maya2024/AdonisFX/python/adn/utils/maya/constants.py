from adn.utils.constants import DeformerTypes, LocatorTypes, SensorTypes, RampInterpolationMode


# Regex to filter valid alpha numeric object paths in Maya:
# - first character must be a letter or pipe
# - special characters not allowed other than underscore
# - pipe can't be followed by a number
OBJECT_PATH_DCC_REGEX = r"^(?:[A-Za-z]|\|[A-Za-z_])(?:(?:[A-Za-z0-9_])|(?:\|[A-Za-z_]))*(\|)?$"


class AdnMayaNodeNames:
    """Constants used at the Maya Sensor editor."""
    ADN_LOCATORS  = [LocatorTypes.POSITION, LocatorTypes.ROTATION, LocatorTypes.DISTANCE]
    ADN_SENSORS   = [SensorTypes.POSITION, SensorTypes.ROTATION, SensorTypes.DISTANCE]
    ADN_DEFORMERS = [DeformerTypes.RIBBON, DeformerTypes.SIMSHAPE, DeformerTypes.SKIN,
                     DeformerTypes.MUSCLE, DeformerTypes.FAT]

    ADN_SENSORS_LOCATORS_OUTPUTS = {
        SensorTypes.POSITION: ["outAcceleration", "outVelocity"],
        SensorTypes.ROTATION: ["outAcceleration", "outAngle", "outVelocity"],
        SensorTypes.DISTANCE: ["outAcceleration", "outDistance", "outVelocity"],
        LocatorTypes.POSITION: ["activationAcceleration", "activationVelocity"],
        LocatorTypes.ROTATION: ["activationAcceleration", "activationAngle", "activationVelocity"],
        LocatorTypes.DISTANCE: ["activationAcceleration", "activationDistance", "activationVelocity"]
    }


class GluePaintableMaps:
    MASS = "mass"
    GLUE_RESISTANCE = "glueResistance"
    STRETCHING_RESISTANCE = "stretchingResistance"
    COMPRESSION_RESISTANCE = "compressionResistance"
    SHAPE_PRESERVATION = "shapePreservation"
    MAX_GLUE_DISTANCE_MULTIPLIER = "maxGlueDistanceMultiplier"
    SC_WEIGHTS = "scWeights"
    SC_POINT_RADIUS_MULTIPLIER = "scPointRadiusMultiplier"
    SOFT_CONSTRAINTS = "softConstraints"
    GLOBAL_DAMPING = "globalDamping"

    DEFAULT_VALUES = {
        MASS : 1.0,
        GLUE_RESISTANCE : 1.0,
        STRETCHING_RESISTANCE : 1.0,
        COMPRESSION_RESISTANCE : 1.0,
        SHAPE_PRESERVATION : 0.0,
        MAX_GLUE_DISTANCE_MULTIPLIER : 1.0,
        SC_WEIGHTS: 1.0,
        SC_POINT_RADIUS_MULTIPLIER : 1.0,
        SOFT_CONSTRAINTS: 1.0,
        GLOBAL_DAMPING: 1.0
    }


class PaintableMaps:
    GLUE = [GluePaintableMaps.MASS,
            GluePaintableMaps.GLUE_RESISTANCE,
            GluePaintableMaps.STRETCHING_RESISTANCE,
            GluePaintableMaps.COMPRESSION_RESISTANCE,
            GluePaintableMaps.SHAPE_PRESERVATION,
            GluePaintableMaps.MAX_GLUE_DISTANCE_MULTIPLIER,
            GluePaintableMaps.SC_WEIGHTS,
            GluePaintableMaps.SC_POINT_RADIUS_MULTIPLIER,
            GluePaintableMaps.SOFT_CONSTRAINTS,
            GluePaintableMaps.GLOBAL_DAMPING]


class PaintToolAttrDisableRule:
    """This class allows to decide the rule to follow for disabling certain attributes
    in the AdonisFX paint tool UI. For example the kAttrOnLowestInitTimeOnly rule will be used
    to evaluate and disable attributes if not on the lowest init time (lowest between
    preroll and start time).
    """
    kAttrOnLowestInitTimeOnly = 0


class IOFeaturesData:
    """This class provides the names of the data attributes used to store the
    input/output features data in the AdonisFX nodes.
    """
    MUSCLE = "MUSCLE_DATA"
    GLUE = "GLUE_DATA"
    FAT = "FAT_DATA"
    SKIN = "SKIN_DATA"
    SKIN_MERGE = "SKIN_MERGE_DATA"
    SIMSHAPE = "SIMSHAPE_DATA"
    RELAX = "RELAX_DATA"
    SENSOR = "SENSOR_DATA"
    ACTIVATION = "ACTIVATION_DATA"
    EDGE_EVALUATOR = "EDGE_EVALUATOR_DATA"
    REMAP = "REMAP_DATA"

# Dictionary to convert Maya's ramp interpolation modes to Adonis' interpolation modes
# This is useful to extract the settings of a ramp attribute in Maya and store it in
# Adonis format DCC-agnostic (e.g. export data from Maya)
MAYA_TO_ADN_RAMP_INTERP_MODE = {
    0: RampInterpolationMode.NONE,
    1: RampInterpolationMode.LINEAR,
    2: RampInterpolationMode.SMOOTH,
    3: RampInterpolationMode.SPLINE
}

# Dictionary to convert Adonis' ramp interpolation modes to Maya' interpolation modes
# This is useful to configure a ramp attribute in Maya using data in 
# Adonis format DCC-agnostic (e.g. import data into Maya)
ADN_TO_MAYA_RAMP_INTERP_MODE = {
    RampInterpolationMode.NONE  : 0,
    RampInterpolationMode.LINEAR: 1,
    RampInterpolationMode.SMOOTH: 2,
    RampInterpolationMode.SPLINE: 3
}
