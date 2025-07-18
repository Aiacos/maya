"""
from zoo.libs.maya.cmds.animation import speed
speed.createSpeedometer()
"""

import maya.cmds as cmds

from zoo.libs.utils import output
from zoo.libs.maya.cmds.objutils import attributes, namehandling

ZOO_SPEEDOMETER_NULL = "zooSpeedometer_null"
ZOO_SPEEDOMETER_EXP = "zooSpeedometer_exp"
ZOO_SPEEDOMETER_HUD = "zooSpeedometer_hud"

MEASUREMENT_UNITS = ["km", "mile", "mm", "millimeter", "cm", "centimeter", "m", "meter", "kilometer", "in", "inch",
                     "ft", "foot", "yd", "yard", "mi"]

UNIT_TO_CM = {
    "mm": 0.1,
    "millimeter": 0.1,
    "cm": 1.0,
    "centimeter": 1.0,
    "m": 100.0,
    "meter": 100.0,
    "km": 100000.0,
    "kilometer": 100000.0,
    "in": 2.54,
    "inch": 2.54,
    "ft": 30.48,
    "foot": 30.48,
    "yd": 91.44,
    "yard": 91.44,
    "mi": 160934.4,
    "mile": 160934.4
}


def get_current_fps():
    """Get the current frames per second (FPS) based on the current time unit"""
    # Query the current time unit
    time_unit = cmds.currentUnit(query=True, time=True)

    # Map the time unit to FPS
    fps_mapping = {
        "film": 24.0,
        "pal": 25.0,
        "ntsc": 30.0,
        "show": 48.0,
        "palf": 50.0,
        "ntscf": 60.0,
        "2fps": 2.0,
        "3fps": 3.0,
        "4fps": 4.0,
        "5fps": 5.0,
        "6fps": 6.0,
        "8fps": 8.0,
        "10fps": 10.0,
        "12fps": 12.0,
        "16fps": 16.0,
        "20fps": 20.0,
        "40fps": 40.0,
        "75fps": 75.0,
        "80fps": 80.0,
        "100fps": 100.0,
        "120fps": 120.0,
        "125fps": 125.0,
        "150fps": 150.0,
        "200fps": 200.0,
        "240fps": 240.0,
        "250fps": 250.0,
        "300fps": 300.0,
        "375fps": 375.0,
        "400fps": 400.0,
        "500fps": 500.0,
        "600fps": 600.0
    }

    # Get the FPS from the mapping, or default to 24 if the unit isn't found
    fps = fps_mapping.get(time_unit, 24.0)
    return fps


def convertToCentimeters():
    """Convert the current scene units to centimeters.

    :return: Meters are converted to centimeters 1 is 100.0, inches are converted to centimeters so 1 is 2.54, etc.
    :rtype: float
    """
    # Query the current linear unit of the scene
    current_unit = cmds.currentUnit(query=True, linear=True)
    # Get the conversion factor, default to 1 if unit isn't in the dictionary
    return UNIT_TO_CM.get(current_unit, 1.0)


def createSpeedometerHUD(object, displayUnits=MEASUREMENT_UNITS[0]):
    """Create the HUD display for the speedometer"""
    removeHUD()  # Remove existing HUD if it exists

    # Create the HUD display for the specified attribute
    cmds.headsUpDisplay(
        ZOO_SPEEDOMETER_HUD,
        section=1,
        block=0,
        blockSize="small",
        label=r"{} {}/hr".format(namehandling.getShortName(object), displayUnits),
        labelFontSize="large",
        dataFontSize="large",
        attachToRefresh=True,
        command=lambda: cmds.getAttr("{}.{}".format(ZOO_SPEEDOMETER_NULL, "{}Hr".format(displayUnits))),
        nodeChanges="attributeChange")

    #TODO add a scene callback that turns off the HUD when a new scene is opened.

    """cmds.headsUpDisplay(
        "{}_miles".format(ZOO_SPEEDOMETER_HUD),
        section=1,
        block=1,
        blockSize="small",
        label=r"{} miles/hr".format(object),
        labelFontSize="large",
        dataFontSize="large",
        attachToRefresh=True,
        command=lambda: cmds.getAttr("{}.{}".format(ZOO_SPEEDOMETER_NULL, "mHr")),
        nodeChanges="attributeChange")"""


def removeHUD():
    """Remove the speedometer HUD
    """
    if cmds.headsUpDisplay(ZOO_SPEEDOMETER_HUD, exists=True):
        cmds.headsUpDisplay(ZOO_SPEEDOMETER_HUD, remove=True)


def createSpeedometerNull(displayUnits=MEASUREMENT_UNITS[0]):
    """Create the speedometer null object with the expression and attributes"""
    # create a group to hold the speedometer attributes
    speedometerNull = cmds.group(empty=True, name=ZOO_SPEEDOMETER_NULL)
    attributes.createAttribute(speedometerNull, "frameDistance", attributeType="float", nonKeyable=True)
    attributes.createAttribute(speedometerNull, "{}Hr".format(displayUnits), attributeType="float", nonKeyable=True)
    return speedometerNull


def createSpeedometer(displayUnits=MEASUREMENT_UNITS[0]):
    """Create the speedometer null, expression and HUD
    """
    objects = cmds.ls(selection=True, flatten=True)

    if not objects:
        output.displayWarning("No objects selected to measure the speed from.")
        return

    # Determine frames per second based on the current time unit
    fps = get_current_fps()

    deleteSpeedometer()  # deletes only if exists
    speedometerNull = createSpeedometerNull(displayUnits=displayUnits)  # Create the null

    cmConversion = str(convertToCentimeters())
    unitMultiplier = UNIT_TO_CM[displayUnits]  # derived from cm

    # TODO: in seconds, minutes, hours, days, weeks, months, years

    # The expression
    expr = """// Zoo Speedometer
        float $time = `currentTime -q`;
        float $fps = {fps}; 
        float $lastFrame[] = `getAttr -time ($time-1.0) {obj}.translate`;
        float $x = ({obj}.tx - $lastFrame[0]) * {multiplier};
        float $y = ({obj}.ty - $lastFrame[1]) * {multiplier};
        float $z = ({obj}.tz - $lastFrame[2]) * {multiplier};
        float $distance = sqrt($x*$x + $y*$y + $z*$z);
        {locator}.frameDistance = $distance;
        {locator}.{displayUnits}Hr = $distance * $fps * 3600 / {unitMultiplier};
    """.format(fps=fps, obj=objects[0], multiplier=cmConversion, locator=speedometerNull, displayUnits=displayUnits,
               unitMultiplier=unitMultiplier)

    # Create the expression
    cmds.expression(string=expr,
                    object=speedometerNull,
                    name=ZOO_SPEEDOMETER_EXP,
                    alwaysEvaluate=False,
                    unitConversion="all")

    createSpeedometerHUD(objects[0], displayUnits=displayUnits)  # Create the HUD

    output.displayInfo("Success: Zoo Speedometer created from {}".format(objects[0]))


def deleteSpeedometer():
    """ Delete the speedometer expression and ull from the scene
    """
    # Attributes to delete
    if cmds.objExists(ZOO_SPEEDOMETER_EXP):
        # Delete the expression
        cmds.delete(ZOO_SPEEDOMETER_EXP)
    if cmds.objExists(ZOO_SPEEDOMETER_NULL):
        cmds.delete(ZOO_SPEEDOMETER_NULL)
    removeHUD()
