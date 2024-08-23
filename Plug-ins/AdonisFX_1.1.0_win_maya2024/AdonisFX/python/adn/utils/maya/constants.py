from adn.utils.constants import DeformerTypes

class AdnMayaNodeNames:
    """Constants used at the Maya Sensor editor."""
    ADN_LOCATORS  = ["AdnLocatorPosition", "AdnLocatorRotation", "AdnLocatorDistance"]
    ADN_SENSORS   = ["AdnSensorPosition", "AdnSensorRotation", "AdnSensorDistance"]
    ADN_DEFORMERS = [DeformerTypes.RIBBON, DeformerTypes.SIMSHAPE, DeformerTypes.SKIN, DeformerTypes.MUSCLE]

    ADN_SENSORS_LOCATORS_OUTPUTS = {
        "AdnSensorPosition": ["outAcceleration", "outVelocity"],
        "AdnSensorRotation": ["outAcceleration", "outAngle", "outVelocity"],
        "AdnSensorDistance": ["outAcceleration", "outDistance", "outVelocity"],
        "AdnLocatorPosition": ["activationAcceleration", "activationVelocity"],
        "AdnLocatorRotation": ["activationAcceleration", "activationAngle", "activationVelocity"],
        "AdnLocatorDistance": ["activationAcceleration", "activationDistance", "activationVelocity"]
    }
