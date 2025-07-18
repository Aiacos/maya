"""Keyframe related scripts.

Author: Andrew Silke

from zoo.libs.maya.cmds.animation import keyframes
keyframes.transferAnimationSelected()

"""

import maya.cmds as cmds

from zoo.libs.utils import output
from zoo.libs.maya.cmds.objutils import attributes, namehandling
from zoo.libs.maya.cmds.animation import timerange, animlayers



# -------------------
# TURNTABLE
# -------------------


def createTurntable(rotateGrp, start=0, end=200, spinValue=360, startValue=0, attr='rotateY',
                    tangent="spline", prePost="linear", setTimerange=True, reverse=False, angleOffset=0):
    """Creates a spinning object 360 degrees, useful for turntables

    :param rotateGrp: the group name to animate
    :type rotateGrp: str
    :param start: the start frame
    :type start: float
    :param end: the end frame
    :type end: float
    :param spinValue: the value to spin, usually 360
    :type spinValue: float
    :param startValue: the start value usually 0
    :type startValue: float
    :param attr: the attribute to animate, usually "rotateY"
    :type attr: str
    :param tangent: the tangent type "spline", "linear", "fast", "slow", "flat", "stepped", "step next" etc
    :type tangent: str
    :param prePost: the infinity option, linear forever?  "constant", "linear", "cycle", "cycleRelative" etc
    :type prePost: str
    :param setTimerange: do you want to set Maya's timerange to the in (+1) and out at the same time?
    :type setTimerange: bool
    :param angleOffset: the angle offset of the keyframes in degrees, will change the start rotation of the asset
    :type angleOffset: float
    :param reverse: reverses the spin direction
    :type reverse: bool
    :return rotateGrp: the grp/object now with keyframes
    :rtype rotateGrp: str
    """
    cmds.cutKey(rotateGrp, time=(), attribute=attr)  # delete if any keys on that attr
    startValue = startValue + angleOffset
    if reverse:  # spins the other way -360
        spinValue *= -1
    endValue = spinValue + angleOffset
    cmds.setKeyframe(rotateGrp, time=start, value=startValue, breakdown=0, attribute=attr,
                     inTangentType=tangent, outTangentType=tangent)
    cmds.setKeyframe(rotateGrp, time=end, value=endValue, breakdown=0, attribute=attr,
                     inTangentType=tangent, outTangentType=tangent)
    cmds.setInfinity(rotateGrp, preInfinite=prePost, postInfinite=prePost)
    if setTimerange:
        cmds.playbackOptions(minTime=start + 1, maxTime=end)  # +1 makes sure the cycle plays without repeated frame
    return rotateGrp


def turntableSelectedObj(start=0, end=200, spinValue=360, startValue=0, attr='rotateY', tangent="spline",
                         prePost="linear", setTimerange=True, angleOffset=0, reverse=False, message=True):
    """Creates a turntable by spinning the selected object/s by 360 degrees

    :param rotateGrp: the group name to animate
    :type rotateGrp: str
    :param start: the start frame
    :type start: float
    :param end: the end frame
    :type end: float
    :param spinValue: the value to spin, usually 360
    :type spinValue: float
    :param startValue: the start value usually 0
    :type startValue: float
    :param attr: the attribute to animate, usually "rotateY"
    :type attr: str
    :param tangent: the tangent type "spline", "linear", "fast", "slow", "flat", "stepped", "step next" etc
    :type tangent: str
    :param prePost: the infinity option, linear forever?  "constant", "linear", "cycle", "cycleRelative" etc
    :type prePost: str
    :param setTimerange: do you want to set Maya's timerange to the in (+1) and out at the same time?
    :type setTimerange: bool
    :param angleOffset: the angle offset of the keyframes in degrees, will change the start rotation of the asset
    :type angleOffset: float
    :param reverse: reverses the spin direction
    :type reverse: bool
    :param message: report the message to the user in Maya
    :type message: bool
    :return rotateObjs: the grp/objects now with keyframes
    :rtype rotateGrp: list
    """
    selObjs = cmds.ls(selection=True)
    if not selObjs:
        output.displayWarning("No Objects Selected. Please Select An Object/s")
        return
    for obj in selObjs:
        createTurntable(obj, start=start, end=end, spinValue=spinValue, startValue=startValue, attr=attr,
                        tangent=tangent, prePost=prePost, setTimerange=setTimerange, angleOffset=angleOffset,
                        reverse=reverse)
    if message:
        output.displayInfo("Turntable Create on:  {}".format(selObjs))
    return selObjs


def deleteTurntableSelected(attr="rotateY", returnToZeroRot=True, message=True):
    """Deletes a turntable animation of the selected obj/s. Ie. Simply deletes the animation on the rot y attribute

    :param attr: The attribute to delete all keys
    :type attr: str
    :param returnToZeroRot: Return the object to default zero?
    :type returnToZeroRot: bool
    :param message: Report the messages to the user in Maya?
    :type message: bool
    :return assetGrps: The group/s now with animation
    :rtype assetGrps: list
    """
    selObjs = cmds.ls(selection=True)
    if not selObjs:
        output.displayWarning("No Objects Selected. Please Select An Object/s")
        return
    for obj in selObjs:
        cmds.cutKey(obj, time=(-10000, 100000), attribute=attr)  # delete all keys rotY
    if returnToZeroRot:
        cmds.setAttr(".".join([obj, attr]), 0)
    if message:
        output.displayInfo("Turntable Keyframes deleted on:  {}".format(selObjs))
    return selObjs


# -------------------
# KEYS
# -------------------

def animCurves(operationMode="selectedObjs", currentAnimLayer=True):
    """ Returns all the animation curves with options for selected objects or all objects.

    :param operationMode: The operation mode, either "selectedObjs" or "allObjs".
    :type operationMode: str
    :param currentAnimLayer: Use the current animation layer, otherwise use all animation layers
    :type currentAnimLayer: bool
    :return: The animation curves as a list of string names
    :rtype: list(str)
    """
    anim_curves = list()
    if operationMode == "selectedObjs":  # selected objects
        layers = animlayers.getAllAnimationLayers()
        selLayers = animlayers.selectedAnimationLayers()
        selObjs = cmds.ls(selection=True)
        if len(layers) <= 1:
            anim_curves = cmds.keyframe(selObjs, query=True, name=True)  # Now add the curves from default layer
        elif not selLayers:
            anim_curves = animlayers.animCurvesAllLayers(cmds.ls(selection=True))
            # todo could fix this, seems like other layers are sometimes selected.
            animlayers.deselectAnimLayer("BaseAnimation")  # deselect BaseAnimation default as it is selected
        elif currentAnimLayer:
            anim_curves = animlayers.animCurvesInSelLayers(selObjs)
        else:
            anim_curves = animlayers.animCurvesAllLayers(cmds.ls(selection=True))
    elif operationMode == "allObjs":  # all objects
        # Get all animation curves in the scene
        anim_curves = cmds.ls(type="animCurve") or []
    return anim_curves


def graphKeysSelected():
    """Returns True if any graph keys are selected in the Graph Editor. Otherwise False."""
    # List all animation curves
    anim_curves = cmds.ls(type="animCurve")
    # Check if any animation curve has selected keys
    for anim_curve in anim_curves:
        selected_keys = cmds.keyframe(anim_curve, query=True, selected=True)
        if selected_keys:
            return True  # Return True if any selected key is found
    return False  # Return False if no selected keys are found


def selListsGraphKeys():
    """Returns the selected animation curves and their selected keys in the Graph Editor.

    :return keepCurves: A list of animation curves with selected keys.
    :rtype keepCurves: list(str)
    :return keepSelKeyTimeLists: A list of lists of selected key times.
    :rtype keepSelKeyTimeLists: list(list(float))
    """
    animCurves = list()
    selKeyTimeLists = list()
    for anim_curve in cmds.ls(type="animCurve"):
        animCurves.append(anim_curve)
        selected_keys = cmds.keyframe(anim_curve, query=True, selected=True)
        selKeyTimeLists.append(selected_keys)
    # only keep curves with selected keys
    keepCurves = list()
    keepSelKeyTimeLists = list()
    for i, selKeyTimeList in enumerate(selKeyTimeLists):
        if selKeyTimeList:
            keepCurves.append(animCurves[i])
            keepSelKeyTimeLists.append(selKeyTimeList)

    return keepCurves, keepSelKeyTimeLists


# -------------------
# MOVE KEYS
# -------------------

def safeMoveGraphKeys(animCurves, selKeyTimeLists, offset=1.0, safetyCheck=True):
    """Moves the selected keys in the graph editor by the offset amount with a safety check.

    :param animCurves: A list of animation curves.
    :type animCurves: list(str)
    :param selKeyTimeLists: A list of lists of selected key times.
    :type selKeyTimeLists: list(list(float))
    :param offset: The amount to move the keys by.
    :type offset: float
    :param safetyCheck: Check if keys will be overwritten.
    :type safetyCheck: bool
    :return: Success message as a string, "existingKeys" if keys will be overwritten. "success" if successful.
    :rtype: string
    """
    if safetyCheck:
        # Check that all keys can be moved without overwriting.  Ignore other selected keys, maya seems to fail at this
        for animCurve, selKeyTimeList in zip(animCurves, selKeyTimeLists):
            # get the highest and lowest time in selKeyTimeList
            if not selKeyTimeList:
                continue
            firstKeyTime = selKeyTimeList[0]
            lastKeyTime = selKeyTimeList[-1]

            # For the offset (like 20 frames) check if any keys will be overwritten, does not check for float keys
            multiplier = 1
            keyToCheck = lastKeyTime
            if offset < 0:
                multiplier = -1
                keyToCheck = firstKeyTime

            for i in range(1, int(abs(offset))):  # could round better
                if cmds.keyframe(animCurve, query=True, time=(keyToCheck + i * multiplier,)):
                    output.displayWarning("Can't Move: Keys on {} will be overwritten "
                                          "at frame {}.".format(animCurve, keyToCheck + i * multiplier))
                    return "error existingKeys"

            # Check if any keys will be overwritten
            for time in selKeyTimeList:
                if cmds.keyframe(animCurve, query=True, time=(time + offset,)):
                    if time + offset not in selKeyTimeList:
                        output.displayWarning("Can't Move: Keys on {} will be "
                                              "overwritten at frame {}.".format(animCurve, time + offset))
                        return "error existingKeys"  # Failed, keys will be overwritten

    # Move the keys -----------------------------------------
    for animCurve, selKeyTimeList in zip(animCurves, selKeyTimeLists):
        if not selKeyTimeList:
            continue
        if offset < 0:
            for time in selKeyTimeList:
                cmds.keyframe(animCurve, edit=True, time=(time,), relative=True, timeChange=offset)
        else:
            for time in reversed(selKeyTimeList):
                cmds.keyframe(animCurve, edit=True, time=(time,), relative=True, timeChange=offset)
    return "success"


def safeMoveObjKeys(current_time, operationMode="selectedObjs", moveAfter=True, offset=1.0, safetyCheck=True,
                    currentAnimLayer=True, message=True):
    """Moves the selected keys in the graph editor by the offset amount with a safety check.

    :param current_time: The current time in the scene.
    :type current_time: float
    :param selectedObjs: Move the keys of the selected objects only.  Otherwise the whole scene
    :type selectedObjs: bool
    :param moveAfter: Move the keys after the current time, otherwise move the keys before the current time.
    :type moveAfter: bool
    :param offset: The amount to move the keys by.
    :type offset: float
    :param safetyCheck: Check if keys will be overwritten before moving them.
    :type safetyCheck: bool
    :param currentAnimLayer: Use the current animation layer, otherwise use all animation layers
    :type currentAnimLayer: bool
    :param message: Report a message to the user.
    :type message: bool
    :return: result
    :rtype: str
    """
    filteredCurves = list()
    keyTimeLists = list()

    # Prepare the animation curves to move keys -----------------------------------------
    animation_curves = animCurves(operationMode=operationMode, currentAnimLayer=currentAnimLayer)

    if not animation_curves:
        if message:
            output.displayWarning("No keys found to move.")
        return "error noKeys"

    # Get the keylists to move -------------------------------------------------------------
    for anim_curve in animation_curves:  # get the key lists for each curve
        key_times = cmds.keyframe(anim_curve, query=True, timeChange=True)
        if moveAfter:  # Get all keyframe times for the current curve that are after the current time
            keys = [time for time in key_times if time >= current_time]  # Filter keys after the specified frame
        else:
            keys = [time for time in key_times if time <= current_time]
        if keys:  # there are keys so record them
            filteredCurves.append(anim_curve)
            keyTimeLists.append(keys)

    if not filteredCurves:
        if message:
            output.displayWarning("No keys found to move.")
        return "error noKeys"

    return safeMoveGraphKeys(filteredCurves, keyTimeLists, offset=offset, safetyCheck=safetyCheck)


def safeMoveSelGraphKeys(offset=1.0):
    """Moves the selected keys in the graph editor by the offset amount with a safety check
    so other keys are not overwritten.

    :param offset: The amount to move the keys by.
    :type offset: float
    :return: result
    :rtype: str
    """
    animCurves, selKeyTimeLists = selListsGraphKeys()
    if not selKeyTimeLists or not animCurves:
        return "error noKeys"
    return safeMoveGraphKeys(animCurves, selKeyTimeLists, offset=offset)


# -------------------
# NUDGE KEYS
# -------------------


def nudgeKeys(offset=1.0, operationMode="selectedObjs", moveAfter=True, autoNudgeScene=False, message=True):
    """Nudges the selected keys by the offset amount.

    If graph keys are selected, only the selected keys will be nudged and this overrides all behaviour except "allObjs".

    If a range is selected in the timeline, only the keys inside of the range will be nudged.
    Otherwise all the keys at and after the current time will be nudged.

    # TODO shift 9 and shift 0 in default Maya

    #TODO: Could add channel box selection filter

    :param offset: The amount to nudge the keys by.
    :type offset: float
    :param operationMode: The operation mode, either "selectedObjs" or "allObjs".
    :type operationMode: str
    :param moveAfter: Move the keys after the current time, otherwise move the keys before the current time.
    :type moveAfter: bool
    :param autoNudgeScene: If True nudges the whole scene keys if no objects are selected.
    :type autoNudgeScene: bool
    :param message: Report a message to the user.
    :type message: bool
    """
    rangeSelected = False
    range = timerange.getSelectedFrameRange()
    current_time = range[0]
    selectedRange = range[1] - range[0]
    if selectedRange > 1.0:
        rangeSelected = True

    if offset == 0.0:
        output.displayWarning("Offset is 0.0, so no keys will be nudged")
        return
    if operationMode not in ["selectedObjs", "allObjs"]:
        output.displayWarning("operationMode must be either 'selectedObjs' or 'allObjs'")
        return
    if not cmds.ls(selection=True) and operationMode == "selectedObjs":
        if autoNudgeScene:  # No objs selected so switch to nudge the whole scene.
            operationMode = "allObjs"
        else:
            output.displayWarning("Please make a selection to nudge keys.")
            return

    # If graph keys selected, then nudge them, overrides other nudge types -----------------------------------------
    if graphKeysSelected() and operationMode == "selectedObjs":
        result = safeMoveSelGraphKeys(offset=offset)  # safely move the selected keys
        if message and not result.startswith("error"):
            output.displayInfo("Keys nudged by {} - Selected Graph Keys".format(offset))
        return

    if not rangeSelected:
        # No range is selected in the timeline and no graph keys are selected, so nudge the keys ---------------
        safetyCheck = False
        if (offset > 0 and not moveAfter) or (offset < 0 and moveAfter):  # Keys can crunch so safe move keys
            safetyCheck = True
        result = safeMoveObjKeys(current_time,
                                 operationMode=operationMode,
                                 moveAfter=moveAfter,
                                 offset=offset,
                                 safetyCheck=safetyCheck,
                                 message=True)
        if message and not result.startswith("error"):
            output.displayInfo("Keys nudged by {}".format(offset))
        return

    # Range is selected -----------------------------
    anim_curves = animCurves(operationMode="selectedObjs", currentAnimLayer=True)

    if not anim_curves:
        if message:
            output.displayWarning("No keys found to move.")
        return

    for anim_curve in anim_curves:
        # Get all keyframe times for the current curve that are after the current time
        key_times = cmds.keyframe(anim_curve, query=True, timeChange=True)
        if not key_times:
            if message:
                output.displayWarning("No keys found to move.")
            continue
        # Move each key that is after the current time by the specified offset positive or negative
        # TODO no safety checks here, could be added
        cmds.keyframe(anim_curve, edit=True, time=(range[0], range[1]), relative=True, timeChange=offset)

    # update the timeline selection, will not work if animation layers are used
    # mel.eval('animLayerEditorOnSelect "{}" 1;'.format("BaseAnimation"))  # kills timeline selection
    try:
        if offset > 0:
            cmds.playbackOptions(selectionStartTime=range[0] + offset, selectionEndTime=range[1] + offset - 1,
                                 selectionVisible=True)
        else:
            cmds.playbackOptions(selectionStartTime=range[0] + offset, selectionEndTime=range[1] + offset - 1,
                                 selectionVisible=True)
    except TypeError:  # fails in earlier versions of Maya 2022 and below
        pass
    if message:
        output.displayInfo("Keys nudged by {} - Selected Range Timeline".format(offset))


# -------------------
# TOGGLE KEY VISIBILITY
# -------------------


def toggleAndKeyVisibility(message=True):
    """Inverts the visibility of an object in Maya and keys it's visibility attribute
    Works on selected objects. Example:

        "cube1.visibility True"
        becomes
        "cube1.visibility False"
        and the visibility attribute is also keyed

    """
    selObjs = cmds.ls(selection=True)
    for obj in selObjs:
        if not attributes.isSettable(obj, "visibility"):
            if message:
                output.displayWarning("The visibility of the object {} is locked or connected. "
                                      "Keyframe toggle skipped.".format(obj))
            continue
        if cmds.getAttr("{}.visibility".format(obj)):  # if visibility is True
            cmds.setAttr("{}.visibility".format(obj), 0)
        else:  # False so set visibility to True
            cmds.setAttr("{}.visibility".format(obj), 1)
        cmds.setKeyframe(obj, breakdown=False, hierarchy=False, attribute="visibility")


def transferAnimationLists(oldObjList, newObjList, message=True):
    """Transfers animation from one object list to another.

    :param oldObjList: Object/node list, the old objects with current animation
    :type oldObjList: list(str)
    :param newObjList: Object/node list, the new objects that will receive the animation.
    :type newObjList: list(str)
    :param message: Report a message to the user.
    :type message: bool
    """
    for i, oldNode in enumerate(oldObjList):
        if cmds.copyKey(oldNode):
            cmds.cutKey(newObjList[i], clear=True)
            cmds.pasteKey(newObjList[i])
    if message:
        output.displayInfo("Success: See Script Editor. Animation copied to "
                           "{}".format(namehandling.getShortNameList(newObjList)))


def transferAnimationSelected(message=True):
    """Transfers the animation of the first half of selected objects to the second half.

    Objects must be selected in order.

    :param message: Report a message to the user?
    :type message: bool
    """
    selObjs = cmds.ls(selection=True)

    if not selObjs:
        output.displayWarning("No objects were selected with animation to transfer")
        return False

    if (len(selObjs) % 2) != 0:  # Not even
        output.displayWarning("There is an odd number of objects selected, must be even")
        return False

    oldObjList = selObjs[:len(selObjs) // 2]
    newObjList = selObjs[len(selObjs) // 2:]

    if message:
        for i, jnt in enumerate(oldObjList):
            try:
                output.displayInfo("Animation Transfer: {} >> {}".format(jnt, newObjList[i]))
            except:
                pass

    transferAnimationLists(oldObjList, newObjList, message=True)


def copyPasteKeysCurveNode(sourceCurveNode, target, attr):
    """Copy from a maya animation curve node name to a target object and the given attribute.

    Curve node, target and attr must exist.

    :param sourceCurveNode: The name of the source curve node name "pCube1_translateX"
    :type sourceCurveNode: str
    :param target: The target object to paste the keys to
    :type target: str
    :param attr: The attribute to paste the anim to
    :type attr: str
    :return: Succeeded or not
    :rtype: bool
    """
    # Check attr not locked/connected
    if not attributes.isSettable(target, attr):
        return False
    # COpy/Paste keys
    cmds.copyKey(sourceCurveNode, time=(), option="curve")
    cmds.pasteKey(target, attribute=attr, option="replaceCompletely")
    return True


def copyPasteKeys(source, target, attr, targetAttr=None, start=0, end=1000, mode="replace",
                  maintainStartEnd=True, includeStaticValues=True):
    """Copy Paste keyframes with error checking if fails.

    paste modes are:
        "insert", "replace", "replaceCompletely", "merge", "scaleInsert," "scaleReplace", "scaleMerge",
        "fitInsert", "fitReplace", and "fitMerge"

    :param source: The source obj/node to have copied keys
    :type source: str
    :param target: The target obj/node to have pasted keys
    :type target: str
    :param attr: the attribute to copy and paste
    :type attr: str
    :param targetAttr: Optional target attribute if different from the attr
    :type targetAttr: str
    :param start: The start frame, ignored if maintainStartEnd
    :type start: float
    :param end: The end frame, ignored if maintainStartEnd
    :type end: float
    :param mode: The copy paste mode. "insert", "replace", "merge" etc see description.
    :type mode: str
    :param maintainStartEnd: Copies only the time-range from the copied attr, otherwise use start end
    :type maintainStartEnd: bool
    :param includeStaticValues: Will copy values that do not have keyframes
    :type includeStaticValues: bool

    :return keyPasted: True if keys were successfully pasted, False if not.
    :rtype keyPasted: bool
    """
    if not targetAttr:
        targetAttr = attr
    if maintainStartEnd:
        keys = cmds.keyframe(".".join([source, attr]), query=True)
        if keys:
            start = keys[0]
            end = keys[-1]
        else:  # No keyframes
            if includeStaticValues:
                if not attributes.isSettable(target, attr):
                    return False
                try:  # TODO more robust code for set attribute values
                    value = cmds.getAttr(".".join([source, attr]))
                    cmds.setAttr(".".join([target, attr]), value)
                except:  # attribute could not be set.
                    pass
            return False
    if not cmds.copyKey(source, time=(start, end), attribute=attr, option="curve"):
        return False
    # Check attr not locked/connected
    if not attributes.isSettable(target, attr):
        return False
    # Paste keys
    cmds.pasteKey(target, time=("{}:".format(start),), attribute=targetAttr, option=mode)
    return True
