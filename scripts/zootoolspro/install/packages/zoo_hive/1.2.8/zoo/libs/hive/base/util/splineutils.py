from zoo.libs.maya import zapi
from zoo.libs.maya.api import curves
from zoo.libs.maya.utils import mayamath
from zoo.libs.utils import zoomath


def createCurveFromDefinition(definition, layer, influences, parent, attributeName,
                              curveName, namingObject, namingRule, curveVisControlAttr):
    compName = definition.name
    side = definition.side
    # generate the world space point positions for the curve
    points = []
    for guide in influences:
        points.append(guide.translate)

    splineAttr = layer.addAttribute(attributeName, Type=zapi.attrtypes.kMFnMessageAttribute)
    extraNodes = []
    # generate the spline curve only if it doesn't exist already
    splineCurveTransform = splineAttr.sourceNode()

    if not splineCurveTransform:
        splineCurveTransform, _ = zapi.nurbsCurveFromPoints(curveName, points)
        for shape in splineCurveTransform.iterShapes():
            shape.template.set(True)
            curveVisControlAttr.connect(shape.visibility)
        splineCurveTransform.rename(curveName)
        layer.connectToByPlug(splineAttr, splineCurveTransform)
        splineCurveTransform.setParent(parent)
        primaryCurveShape = splineCurveTransform.shapes()[0]
        controlPointsAttr = primaryCurveShape.attribute("controlPoints")
        for index, sceneGuide in enumerate(influences):
            decompName = namingObject.resolve(namingRule, {"componentName": compName,
                                                           "side": side,
                                                           "section": sceneGuide.name() + "worldCurve",
                                                           "type": "decomposeMatrix"})
            decompose = zapi.createDG(decompName, "decomposeMatrix")
            sceneGuide.attribute("worldMatrix")[0].connect(decompose.inputMatrix)
            decompose.outputTranslate.connect(controlPointsAttr[index])
            extraNodes.append(decompose)

    return splineCurveTransform, extraNodes


def createSquashGuideCurve(name, keyTimes, values):
    animCurve = zapi.createDG(name, "animCurveTU")  # type: zapi.AnimCurve
    animCurve.setPrePostInfinity(zapi.kInfinityConstant, zapi.kInfinityConstant)
    # squashCurve keys
    animCurve.addKeysWithTangents(
        keyTimes, values,
        tangentInTypeArray=[zapi.kTangentLinear, zapi.kTangentClamped, zapi.kTangentLinear],
        tangentOutTypeArray=[zapi.kTangentLinear, zapi.kTangentClamped, zapi.kTangentLinear],
        convertUnits=False,
        keepExistingKeys=False)
    return animCurve


def createSquash(naming, joints, lastAnimKey,
                 constantsNode, controlPanel,
                 stretchOutput, compName,
                 compSide, volumeAttrPrefix="volume"):
    jointCount = len(joints)
    scaleAttributeNames = ["scale{}".format(i) for i in mayamath.AXIS_IDX_BY_NAME.keys()]
    volumeBlend = zapi.createDG(naming.resolve("object", {"componentName": compName,
                                                          "side": compSide,
                                                          "section": "splineVolume",
                                                          "type": "blendTwoAttr"}), "blendTwoAttr")
    constantsNode.constants_one.connect(volumeBlend.input[0])
    stretchOutput.connect(volumeBlend.input[1])
    controlPanel.globalVolume.connect(volumeBlend.attributesBlender)

    volumeAttrs = [None] * jointCount  # type: zapi.Plug
    for i in range(lastAnimKey):
        volumeAttr = controlPanel.attribute("".join((volumeAttrPrefix, str(i).zfill(2))))
        volumeAttrs[i] = volumeAttr
    positionValues = [value for value in zoomath.lerpCount(0, 1, jointCount)]

    extraNodes = [volumeBlend]
    for i, jnt in enumerate(joints):
        remap = zapi.createDG("remap{}".format(jnt.name()), "remapValue")
        remap.inputValue.set(i)
        remap.inputMax.set(jointCount-1)
        # remap.
        powerOf = zapi.createDG(naming.resolve("object",
                                               {"componentName": compName,
                                                "side": compSide,
                                                "section": "".join((jnt.id(), "squashPower")),
                                                "type": "multiplyDivide"}), "multiplyDivide")
        powerOf.operation.set(3)
        volumeBlend.output.connect(powerOf.input1X)
        invert = zapi.createDG(naming.resolve("object",
                                              {"componentName": compName,
                                               "side": compSide,
                                               "section": "".join((jnt.id(), "volumeInvert")),
                                               "type": zapi.kMultDoubleLinearName}),
                               zapi.kMultDoubleLinearName)
        invert.input2.set(-1)
        remap.outValue.connect(invert.input1)
        for index, [pos, vol] in enumerate(zip(positionValues, volumeAttrs)):
            valueElement = remap.value[index]
            valueElement.child(0).set(pos)
            vol.connect(valueElement.child(1))
            valueElement.child(2).set(3)
        invert.output.connect(powerOf.input2X)

        for scaleAttrName in scaleAttributeNames:
            powerOf.outputX.connect(jnt.attribute(scaleAttrName))

        extraNodes.extend((powerOf, remap, invert))

    return extraNodes


def createIkSplineJoints(component, rigLayer, controlPanel,
                         parentInput, curve, jointCount,
                         aimVector, upVector,
                         parent, stretchOffLimitAttrName):
    skinParentJoint = parent
    ikSplineJoints = []
    naming = component.namingConfiguration()
    compName, compSide = component.name(), component.side()
    constantsNode = rigLayer.settingNode("constants")
    hipSwing = rigLayer.control("hipSwing")
    ctrl02 = rigLayer.control("ctrl02")
    # parent space srt which inherents the worldMatrix from the parent_in input node ie. parentcomponent
    parentSrt = zapi.createDag("parent_space_srt", "transform", parent=rigLayer.rootTransform())
    parentInput.attribute("worldMatrix")[0].connect(parentSrt.attribute("offsetParentMatrix"))
    # stretch related nodes
    curveInfoNode = zapi.createDG(naming.resolve("object", {"componentName": compName,
                                                            "side": compSide,
                                                            "section": "splineLength",
                                                            "type": "curveInfo"}), "curveInfo")
    globalScale = zapi.createDG(naming.resolve("object", {"componentName": compName,
                                                          "side": compSide,
                                                          "section": "splineLengthGlobalScale",
                                                          "type": "multiplyDivide"}), "multiplyDivide")
    globalScaleDecomp = zapi.createDG(naming.resolve("object", {"componentName": compName,
                                                                "side": compSide,
                                                                "section": "splineLengthGlobalScale",
                                                                "type": "decomposeMatrix"}), "decomposeMatrix")
    lengthScaleDiv = zapi.createDG(naming.resolve("object", {"componentName": compName,
                                                             "side": compSide,
                                                             "section": "splineLengthNormal",
                                                             "type": "multiplyDivide"}), "multiplyDivide")
    stretchBlend = zapi.createDG(naming.resolve("object", {"componentName": compName,
                                                           "side": compSide,
                                                           "section": "splineStretch",
                                                           "type": "blendTwoAttr"}), "blendTwoAttr")

    stretchOffLimitAdd = zapi.createDG(naming.resolve("object", {"componentName": compName,
                                                                 "side": compSide,
                                                                 "section": "stretchOffLimitMax",
                                                                 "type": zapi.kAddDoubleLinearName}), zapi.kAddDoubleLinearName)
    stretchOffLimitMinSub = zapi.createDG(naming.resolve("object",
                                                         {"componentName": compName,
                                                          "side": compSide,
                                                          "section": "stretchOffLimitMin",
                                                          "type": "plusMinusAverage"}), "plusMinusAverage")
    stretchOffLimitClamp = zapi.createDG(naming.resolve("object", {"componentName": compName,
                                                                   "side": compSide,
                                                                   "section": "stretchOffLimit",
                                                                   "type": "clamp"}), "clamp")

    lengthScaleDiv.operation.set(2)  # divide
    globalScale.operation.set(2)  # divide
    shapeNode = curve.shapes()[0]
    shapeNode.worldSpace[0].connect(curveInfoNode.inputCurve)
    constantsNode.initialCurveLength.set(curveInfoNode.arcLength.value().value)  # arclength value is a MDistance

    # setup stretch off limit
    constantsNode.initialCurveLength.connect(stretchOffLimitMinSub.input1D[0])
    controlPanel.attribute(stretchOffLimitAttrName).connect(stretchOffLimitMinSub.input1D[0])
    stretchOffLimitMinSub.output1D.connect(stretchOffLimitClamp.minR)
    stretchOffLimitMinSub.operation.set(2) # subtract
    constantsNode.initialCurveLength.connect(stretchOffLimitAdd.input1)

    controlPanel.attribute(stretchOffLimitAttrName).connect(stretchOffLimitAdd.input2)
    stretchOffLimitAdd.output.connect(stretchOffLimitClamp.maxR)
    globalScale.outputX.connect(stretchOffLimitClamp.inputR)

    # blend between stretch off limit and total stretch
    stretchOffLimitClamp.outputR.connect(stretchBlend.input[0])
    globalScale.outputX.connect(stretchBlend.input[1])
    controlPanel.stretch.connect(stretchBlend.attributesBlender)

    # global scale compensation
    curveInfoNode.arcLength.connect(globalScale.input1X)
    globalScaleDecomp.outputScaleY.connect(globalScale.input2X)
    hipSwing.attribute("worldMatrix")[0].connect(globalScaleDecomp.inputMatrix)

    # normalize the length
    stretchBlend.output.connect(lengthScaleDiv.input1X)
    constantsNode.initialCurveLength.connect(lengthScaleDiv.input2X)

    # all created nodes which will be added to the meta data as extras
    extraNodes = [curveInfoNode,
                  lengthScaleDiv,
                  stretchBlend,
                  stretchOffLimitAdd,
                  stretchOffLimitClamp]

    previousTranslation, previousRotation, previousRotateOrder = None, None, 0
    primaryAxisTranslate = "translate" + mayamath.primaryAxisNameFromVector(aimVector)
    for index, [position, rotation] in enumerate(curves.rotationsAlongCurve(shapeNode.dagPath(), jointCount,
                                                                            aimVector=aimVector,
                                                                            upVector=upVector,
                                                                            worldUpVector=zapi.Vector(0, 0, 1)
                                                                            )):
        jntId = component.ikSplineJointIdForNumber(index)
        name = naming.resolve("jointName", {"componentName": compName,
                                            "side": compSide,
                                            "id": jntId,
                                            "system": "ik",
                                            "type": "joint"})
        spineJoint = rigLayer.createJoint(name=name,
                                          id=jntId,
                                          translate=position,
                                          rotate=rotation,
                                          rotateOrder=previousRotateOrder,  # todo: rotateOrder
                                          parent=skinParentJoint)
        primaryAxisAttribute = spineJoint.attribute(primaryAxisTranslate)
        skinParentJoint.attribute("scale").connect(spineJoint.inverseScale)
        stretchComp = zapi.createDG("stretchComp", zapi.kMultDoubleLinearName)
        lengthScaleDiv.outputX.connect(stretchComp.input1)
        stretchComp.input2.set(primaryAxisAttribute.value().value)
        stretchComp.output.connect(primaryAxisAttribute)
        spineJoint.segmentScaleCompensate.set(1)
        skinParentJoint = spineJoint
        ikSplineJoints.append(spineJoint)
        extraNodes.append(stretchComp)
        previousTranslation, previousRotation, previousRotateOrder = position, rotation, 0

    name = naming.resolve("jointName", {"componentName": compName,
                                        "side": compSide,
                                        "id": "splineIkStart",
                                        "system": "ik",
                                        "type": "joint"})
    spineJoint = rigLayer.createJoint(name=name,
                                      id="splineIkStart",
                                      translate=ikSplineJoints[0].translation(),
                                      rotate=ikSplineJoints[0].rotation(),
                                      rotateOrder=previousRotateOrder,  # todo: rotateOrder
                                      parent=parentSrt)
    ikSplineJoints[0].setParent(spineJoint)
    const, _ = zapi.buildConstraint(spineJoint,
                                    drivers={"targets": ((hipSwing.name(includeNamespace=False),
                                                          hipSwing),)},
                                    constraintType="matrix", trace=False,
                                    decompose=True,
                                    maintainOffset=True
                                    )
    rigLayer.addExtraNodes(const.utilityNodes())
    name = naming.resolve("jointName", {"componentName": compName,
                                        "side": compSide,
                                        "id": "ikSplineEnd",
                                        "system": "ik",
                                        "type": "joint"})
    spineJoint = rigLayer.createJoint(name=name,
                                      id="ikSplineEnd",
                                      translate=ikSplineJoints[-1].translation(),
                                      rotate=ikSplineJoints[-1].rotation(),
                                      rotateOrder=previousRotateOrder,  # todo: rotateOrder
                                      parent=ikSplineJoints[-1])
    spineJoint.jointOrient.set((0, 0, 0))
    const, constUtilities = zapi.buildConstraint(spineJoint,
                                                 drivers={"targets": ((ctrl02.name(includeNamespace=False),
                                                                       ctrl02),)},
                                                 maintainOffset=True,
                                                 constraintType="orient",
                                                 trace=False)
    rigLayer.addExtraNodes(constUtilities)
    rigLayer.addExtraNodes(extraNodes)

    return ikSplineJoints + [spineJoint], parentSrt, globalScaleDecomp, lengthScaleDiv.outputX


def createIkSpline(name, parent, upVectorControl, endControl, curve, aimVector, upVector, ikJoints):
    perpendicular = zapi.Vector(aimVector) ^ zapi.Vector(upVector)
    ikHandle, ikEffector = zapi.createIkHandle(name, startJoint=ikJoints[0],
                                               endJoint=ikJoints[-2],
                                               solverType=zapi.kIkSplineSolveType,
                                               parent=parent,
                                               curve=curve.fullPathName(),
                                               parentCurve=False,
                                               rootOnCurve=True,
                                               simplifyCurve=False,
                                               createCurve=False)

    ikHandle.dTwistControlEnable = True
    ikHandle.dWorldUpType = zapi.IkHandle.OBJECT_ROTATION_UP_START_END
    ikHandle.dForwardAxis = ikHandle.vectorToForwardAxisEnum(aimVector)  # positive X
    ikHandle.dWorldUpAxis = ikHandle.vectorToUpAxisEnum(upVector)  # positive Y
    ikHandle.dWorldUpVector = perpendicular
    ikHandle.dWorldUpVectorEnd = perpendicular
    ikHandle.hide()
    upVectorControl.attribute("worldMatrix")[0].connect(ikHandle.dWorldUpMatrix)
    endControl.attribute("worldMatrix")[0].connect(ikHandle.dWorldUpMatrixEnd)
    return ikHandle, ikEffector
