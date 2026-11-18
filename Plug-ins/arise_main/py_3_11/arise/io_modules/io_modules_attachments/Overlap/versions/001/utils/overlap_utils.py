"""Overlap utils build a pure Maya node network that fakes secondary motion (lag, follow through and overshoot).

No expressions, no simulation and no stored state are used. Instead, the history of the driver joints is read with
'frameCache' nodes ('past[n]' = value n frames ago) and filtered with a short FIR kernel that is the sampled impulse
response of a damped spring. Because the result only depends on the animation of the drivers, it behaves the same when
scrubbing, jumping in time, playing back or baking.
"""

import math

import maya.api.OpenMaya as om
import maya.cmds as mc

from arise.utils.modules_utils import ADD_DL, MULT_DL, MULT_DL_INPUT1, MULT_DL_INPUT2

# frames (back in time) that are sampled. Dense close to the current frame, sparse far from it.
TAP_FRAMES = (0, 1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 18, 22, 26, 31, 36)
TAP_FRAMES_LOW = (0, 1, 2, 4, 7, 12, 20, 32)
TAPS_OPTIONS = (TAP_FRAMES, TAP_FRAMES_LOW)
MIN_PERIOD = 2.0
MIN_DAMPING = 0.05
MAX_DAMPING = 1.0
EPSILON = 0.0001


def spring_impulse_response(time, period, damping):
    """Return the impulse response of a damped spring at time (in frames).

    Arguments:
        time {float} -- time in frames after the impulse
        period {float} -- natural period of the spring in frames
        damping {float} -- damping ratio. 1.0 is critically damped (no overshoot). lower values overshoot

    Returns:
        float -- the response value
    """
    omega = 2.0 * math.pi / max(period, MIN_PERIOD)
    damping = min(max(damping, MIN_DAMPING), MAX_DAMPING)

    if damping >= MAX_DAMPING:  # critically damped.
        return omega * omega * time * math.exp(-omega * time)

    root = math.sqrt(1.0 - damping * damping)
    return (omega / root) * math.exp(-damping * omega * time) * math.sin(omega * root * time)


def spring_kernel(period, damping, taps=TAP_FRAMES):
    """Return the weight of each tap so that the weighted sum of past values behaves like a damped spring.

    The sum of the weights is always 1.0 so a still driver results in no offset what so ever.

    Arguments:
        period {float} -- natural period of the spring in frames
        damping {float} -- damping ratio between 0.05 and 1.0

    Keyword Arguments:
        taps {tuple} -- of ints, frames back in time to sample (default: {TAP_FRAMES})

    Returns:
        list -- of floats, one for each tap
    """
    weights = []
    for index, frame in enumerate(taps):
        lower = frame - (frame - taps[index - 1]) * 0.5 if index > 0 else frame
        upper = frame + (taps[index + 1] - frame) * 0.5 if index < len(taps) - 1 else frame + 1.0

        # simpson integration of the response over the cell the tap represents.
        mid = (lower + upper) * 0.5
        value = (
            spring_impulse_response(lower, period, damping)
            + 4.0 * spring_impulse_response(mid, period, damping)
            + spring_impulse_response(upper, period, damping)
        ) * (upper - lower) / 6.0
        weights.append(value)

    total = sum(weights)
    if abs(total) < EPSILON:
        weights = [1.0] + [0.0] * (len(taps) - 1)
        total = 1.0

    return [weight / total for weight in weights]


def _node(node_type, name, **kwargs):
    """Create a utility node and set the values passed as kwargs. """
    node = mc.createNode(node_type, name=name)
    for attr, value in kwargs.items():
        if isinstance(value, (tuple, list)):
            mc.setAttr("{0}.{1}".format(node, attr), *value, type="double3")
        else:
            mc.setAttr("{0}.{1}".format(node, attr), value)

    return node


def create_tap_weights(prefix, lag_attr, kernel_fast, kernel_slow, taps=TAP_FRAMES):
    """Create the nodes that blend between two kernels using 'lag_attr'. Shared by all joints of a chain.

    Arguments:
        prefix {str} -- name prefix of created nodes
        lag_attr {str} -- attribute (0 to 1) that blends from the fast kernel to the slow one
        kernel_fast {list} -- of floats, weights of the kernel used when lag is 0
        kernel_slow {list} -- of floats, weights of the kernel used when lag is 1

    Returns:
        list -- of 'node.outValue' attribute names, one for each tap
    """
    weight_attrs = []
    for index, frame in enumerate(taps):
        remap = _node(
            "remapValue",
            "{0}_tap_{1}_remapValue".format(prefix, frame),
            inputMin=0.0,
            inputMax=1.0,
            outputMin=kernel_fast[index],
            outputMax=kernel_slow[index],
        )
        mc.connectAttr(lag_attr, "{0}.inputValue".format(remap))
        weight_attrs.append("{0}.outValue".format(remap))

    return weight_attrs


def create_filtered_position(prefix, decompose, weight_attrs, taps=TAP_FRAMES):
    """Create the nodes that return the world position of a driver as it was filtered over the past frames.

    Arguments:
        prefix {str} -- name prefix of created nodes
        decompose {str} -- decomposeMatrix node of the driver world matrix
        weight_attrs {list} -- of attributes, the weight of each tap

    Returns:
        list -- of 3 'blendWeighted.output' attributes (X, Y, Z) of the filtered position
    """
    outputs = []
    for axis in "XYZ":
        source = "{0}.outputTranslate{1}".format(decompose, axis)
        cache = _node("frameCache", "{0}_{1}_frameCache".format(prefix, axis))
        mc.connectAttr(source, "{0}.stream".format(cache))

        # blendWeighted is a weighted sum in a single node.
        total = _node("blendWeighted", "{0}_{1}_filtered_blendWeighted".format(prefix, axis))
        for index, (frame, weight_attr) in enumerate(zip(taps, weight_attrs)):
            tap_source = source if frame == 0 else "{0}.past[{1}]".format(cache, frame)
            mc.connectAttr(tap_source, "{0}.input[{1}]".format(total, index))
            mc.connectAttr(weight_attr, "{0}.weight[{1}]".format(total, index))

        outputs.append("{0}.output".format(total))

    return outputs


def create_overlap_chain(prefix, points, joints, attrs, kernel_fast, kernel_slow, taps=TAP_FRAMES):
    """Create the network that drives 'joints' to follow 'points' with overlap.

    Each joint is a bone between two points (the last point is a tip transform extending the chain). The
    joints keep the length of the bones and lag behind the points according to the attributes.

    Arguments:
        prefix {str} -- name prefix of created nodes
        points {list} -- of transforms, the driver of each joint and a last tip transform. len(joints) + 1
        joints {list} -- of joints to drive. All have to be in the same space and zero joint orient
        attrs {dict} -- of attribute names: 'strength', 'lag', 'falloff' and 'max_swing'
        kernel_fast {list} -- weights of the fast kernel
        kernel_slow {list} -- weights of the slow kernel

    Keyword Arguments:
        taps {tuple} -- of ints, frames back in time to sample. kernels must be made for the same taps
            (default: {TAP_FRAMES})
    """
    count = len(joints)
    if len(points) != count + 1:
        raise ValueError("Overlap chain needs one more point than joints.")

    weight_attrs = create_tap_weights(prefix, attrs["lag"], kernel_fast, kernel_slow, taps=taps)

    decomposes = []
    for index, point in enumerate(points):
        decompose = _node("decomposeMatrix", "{0}_{1}_point_decomposeMatrix".format(prefix, index))
        mc.connectAttr("{0}.worldMatrix[0]".format(point), "{0}.inputMatrix".format(decompose))
        decomposes.append(decompose)

    # one distance node per bone, shared by the limit and the chain walk.
    bone_lengths = []
    for index in range(count):
        bone_length = _node("distanceBetween", "{0}_{1}_bone_distanceBetween".format(prefix, index))
        mc.connectAttr("{0}.worldMatrix[0]".format(points[index]), "{0}.inMatrix1".format(bone_length))
        mc.connectAttr("{0}.worldMatrix[0]".format(points[index + 1]), "{0}.inMatrix2".format(bone_length))
        bone_lengths.append("{0}.distance".format(bone_length))

    # where each point wants to be, pulled back towards its filtered position.
    targets = []
    for index in range(1, count + 1):
        point_prefix = "{0}_{1}".format(prefix, index)
        current = "{0}.outputTranslate".format(decomposes[index])
        filtered = create_filtered_position(point_prefix, decomposes[index], weight_attrs, taps=taps)

        offset_length = _node("distanceBetween", "{0}_offset_distanceBetween".format(point_prefix))
        for axis, filtered_attr in zip("XYZ", filtered):
            mc.connectAttr(filtered_attr, "{0}.point1{1}".format(offset_length, axis))
            mc.connectAttr("{0}{1}".format(current, axis), "{0}.point2{1}".format(offset_length, axis))

        max_offset = _node(MULT_DL, "{0}_max_offset_multDoubleLinear".format(point_prefix))
        mc.connectAttr(bone_lengths[index - 1], "{0}.{1}".format(max_offset, MULT_DL_INPUT1))
        mc.connectAttr(attrs["max_swing"], "{0}.{1}".format(max_offset, MULT_DL_INPUT2))

        safe_length = _node(ADD_DL, "{0}_safe_length_addDoubleLinear".format(point_prefix), input2=EPSILON)
        mc.connectAttr("{0}.distance".format(offset_length), "{0}.input1".format(safe_length))

        ratio = _node("multiplyDivide", "{0}_ratio_multiplyDivide".format(point_prefix), operation=2)
        mc.connectAttr("{0}.output".format(max_offset), "{0}.input1X".format(ratio))
        mc.connectAttr("{0}.output".format(safe_length), "{0}.input2X".format(ratio))

        limit = _node("clamp", "{0}_limit_clamp".format(point_prefix), minR=0.0, maxR=1.0)
        mc.connectAttr("{0}.outputX".format(ratio), "{0}.inputR".format(limit))

        falloff = _node(
            "multiplyDivide",
            "{0}_falloff_multiplyDivide".format(point_prefix),
            operation=3,
            input1X=float(index) / count,
        )
        mc.connectAttr(attrs["falloff"], "{0}.input2X".format(falloff))

        weight = _node(MULT_DL, "{0}_weight_multDoubleLinear".format(point_prefix))
        mc.connectAttr(attrs["strength"], "{0}.{1}".format(weight, MULT_DL_INPUT1))
        mc.connectAttr("{0}.outputX".format(falloff), "{0}.{1}".format(weight, MULT_DL_INPUT2))

        gain = _node(MULT_DL, "{0}_gain_multDoubleLinear".format(point_prefix))
        mc.connectAttr("{0}.outputR".format(limit), "{0}.{1}".format(gain, MULT_DL_INPUT1))
        mc.connectAttr("{0}.output".format(weight), "{0}.{1}".format(gain, MULT_DL_INPUT2))

        # target = current + (filtered - current) * gain
        target = _node("blendColors", "{0}_target_blendColors".format(point_prefix))
        mc.connectAttr("{0}.output".format(gain), "{0}.blender".format(target))
        for axis, filtered_attr in zip("XYZ", filtered):
            mc.connectAttr(filtered_attr, "{0}.color1{1}".format(target, {"X": "R", "Y": "G", "Z": "B"}[axis]))
            mc.connectAttr(
                "{0}{1}".format(current, axis),
                "{0}.color2{1}".format(target, {"X": "R", "Y": "G", "Z": "B"}[axis]),
            )
        targets.append("{0}.output".format(target))

    # the direction of each bone in the space of its driver (aimed at the target) and a perpendicular axis (kept
    # aligned with the driver so the twist is preserved).
    axes = []
    for index in range(count):
        driver_inverse = om.MMatrix(mc.getAttr("{0}.worldInverseMatrix[0]".format(points[index])))
        child_position = om.MPoint(*mc.xform(points[index + 1], query=True, worldSpace=True, translation=True))
        bone_direction = om.MVector(child_position * driver_inverse).normal()
        helper = om.MVector(0, 1, 0) if abs(bone_direction.y) < 0.9 else om.MVector(1, 0, 0)
        side = (bone_direction ^ helper).normal()
        side = (side ^ bone_direction).normal()
        axes.append(((bone_direction.x, bone_direction.y, bone_direction.z), (side.x, side.y, side.z)))
    # walk the chain. each joint aims from its pivot to its target and keeps the length of its bone.
    pivot = "{0}.outputTranslate".format(decomposes[0])
    for index, joint in enumerate(joints):
        bone_prefix = "{0}_{1}".format(prefix, index)

        aim = _node("plusMinusAverage", "{0}_aim_plusMinusAverage".format(bone_prefix), operation=2)
        mc.connectAttr(targets[index], "{0}.input3D[0]".format(aim))
        mc.connectAttr(pivot, "{0}.input3D[1]".format(aim))

        direction = _node(
            "vectorProduct",
            "{0}_direction_vectorProduct".format(bone_prefix),
            operation=0,
            normalizeOutput=1,
        )
        mc.connectAttr("{0}.output3D".format(aim), "{0}.input1".format(direction))

        step = _node("multiplyDivide", "{0}_step_multiplyDivide".format(bone_prefix))
        mc.connectAttr("{0}.output".format(direction), "{0}.input1".format(step))
        for axis in "XYZ":
            mc.connectAttr(bone_lengths[index], "{0}.input2{1}".format(step, axis))

        # the driver orientation placed at the pivot, then turned so the bone points at the overlap target.
        driver_matrix = _node(
            "composeMatrix",
            "{0}_driver_composeMatrix".format(bone_prefix),
            useEulerRotation=0,
        )
        mc.connectAttr("{0}.outputQuat".format(decomposes[index]), "{0}.inputQuat".format(driver_matrix))
        mc.connectAttr("{0}.outputScale".format(decomposes[index]), "{0}.inputScale".format(driver_matrix))
        mc.connectAttr(pivot, "{0}.inputTranslate".format(driver_matrix))

        primary_axis, secondary_axis = axes[index]
        aim_matrix = _node(
            "aimMatrix",
            "{0}_aimMatrix".format(bone_prefix),
            primaryInputAxis=primary_axis,
            secondaryMode=2,
            secondaryInputAxis=secondary_axis,
            secondaryTargetVector=secondary_axis,
        )
        mc.connectAttr("{0}.outputMatrix".format(driver_matrix), "{0}.inputMatrix".format(aim_matrix))
        mc.connectAttr(targets[index], "{0}.primaryTargetVector".format(aim_matrix))
        mc.connectAttr("{0}.worldMatrix[0]".format(points[index]), "{0}.secondaryTargetMatrix".format(aim_matrix))

        mult_matrix = _node("multMatrix", "{0}_multMatrix".format(bone_prefix))
        mc.connectAttr("{0}.outputMatrix".format(aim_matrix), "{0}.matrixIn[0]".format(mult_matrix))
        mc.connectAttr("{0}.parentInverseMatrix[0]".format(joint), "{0}.matrixIn[1]".format(mult_matrix))
        local = _node(
            "decomposeMatrix",
            "{0}_local_decomposeMatrix".format(bone_prefix),
            inputRotateOrder=mc.getAttr("{0}.rotateOrder".format(joint)),
        )
        mc.connectAttr("{0}.matrixSum".format(mult_matrix), "{0}.inputMatrix".format(local))

        for attr in ("Translate", "Rotate", "Scale"):
            for axis in "XYZ":
                mc.connectAttr(
                    "{0}.output{1}{2}".format(local, attr, axis),
                    "{0}.{1}{2}".format(joint, attr.lower(), axis),
                    force=True,
                )

        # the next pivot is one bone length away from this one along the overlap direction.
        next_pivot = _node("plusMinusAverage", "{0}_next_pivot_plusMinusAverage".format(bone_prefix), operation=1)
        mc.connectAttr(pivot, "{0}.input3D[0]".format(next_pivot))
        mc.connectAttr("{0}.output".format(step), "{0}.input3D[1]".format(next_pivot))
        pivot = "{0}.output3D".format(next_pivot)
