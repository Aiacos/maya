import copy
import math

from zoo.libs.hive.base.serialization import graphconstants
from zoo.libs.maya import zapi
from zoo.libs.maya.api import mesh, curves, deformers
from zoo.libs.maya.utils import mayamath, mayaenv
from zoo.libs.utils import zoomath, general
from zoo.libs.hive import api
from zoo.libs.hive.base import basesubsystem, definition

from maya import cmds

SECONDARY_GUIDE_SHAPE = "sphere"
PRIMARY_GUIDE_SHAPE = "square_rounded"
TANGENT_GUIDE_SHAPE = "sphere"
TWEAKER_GUIDE_SHAPE = "pick_tri_fat"
META_EXTRA_ATTR = "brow" + api.constants.BS_META_EXTRA_ATTR_PREFIX
RAIL_MAIN_GUIDE_SHAPE = "pick_pin"
DEFAULT_GUIDE_CTRL_SCALE = (0.5, 0.5, 0.5)
DEFAULT_GUIDE_SHAPE_SCALE = (0.129, 0.129, 0.129)
DEFAULT_PRIMARY_GUIDE_CTRL_SCALE = (0.55, 0.55, 0.55)
DEFAULT_PRIMARY_GUIDE_SHAPE_SCALE = (0.375, 0.375, 0.375)
DEFAULT_RAILS_MAIN_SHAPE_SCALE = (0.656, 0.656, 0.656)
DEFAULT_PRIMARY_MID_GUIDE_SHAPE_SCALE = (0.375, 0.375, 0.188)
DEFAULT_GUIDE_JNT_SCALE = (0.1, 0.1, 0.1)
DEFAULT_TANGENT_CTRL_SCALE = (0.131, 0.131, 0.131)
DEFAULT_TWEAKER_TANGENT_CTRL_SCALE = (0.255, 0.255, 0.255)
DEFAULT_MAIN_CTRL_COLOR = (1.0, 0.182, 0.073)
DEFAULT_PRIMARY_CTRL_COLOR = (1.0, 0.350, 0.073)
DEFAULT_SECONDARY_CTRL_COLOR = (0.538, 1.0, 0.073)
DEFAULT_TWEAKER_CTRL_COLOR = (1.0, 0.897, 0.073)
CTRL_PARAM_POS = (0.15, 0.5)
# Guide cv indices where the secondary controls will be placed.
# Note the in/out tangents are -1/+1 respectably
CV_POS_INDICES = (0, 3, 6, 9)
# auto align rotation offsets
TWEAKER_TANGENT_DEFAULT_ROT = (0, 0.0, math.pi * -0.25)
# Rotation offset when first built which doesn't handle auto alignment
TWEAKER_TANGENT_GUIDE_DEFAULT_ROT = (0, math.pi, math.pi * 0.25)
TWEAKER_TANGENT_DEFAULT_ROT_SCALED = (0, 0, math.pi * 0.25)
RAIL_GUIDE_CURVE_MAX_POS = zapi.Vector(0, 3, 0)
RAIL_CURVE_SHAPE = {
    "curveShape1": {
        "overrideEnabled": True,
        "overrideColorRGB": (0.073, 0.984, 1.0),
        "overrideRGBColors": True,
        "knots": (0.0, 0.0, 0.0, 1.0, 2.0, 2.0, 2.0),
        "cvs": (
            [0.0, -1.0, 0.0, 1.0],
            [0.0, 0.0, 0.0, 1.0],
            [0.0, 1.0, 0.0, 1.0],
            [0.0, 2.0, 0.0, 1.0],
            [0.0, 3.0, 0.0, 1.0],
        ),
        "degree": 3,
        "form": 1,
    }
}


class BrowSubsystem(basesubsystem.BaseSubsystem):
    """
    :param component: The component associated with this subsystem.
    :type component: :class:`zoo.libs.hive.base.component.Component`
    :param jointIdPrefix: Deform joint id prefix, will have the index appended by this subsystem
    """

    def __init__(
            self,
            component,
            jointIdPrefix,
            mainCtrlId,
            ctrlIds,
            primaryCtrlIdPrefix,
            secondaryCtrlIdPrefix,
            tangentCtrlIds,
            curveId,
    ):
        super(BrowSubsystem, self).__init__(component)
        self.jointCountSettingName = "jointCount"
        self.separateCountsSettingName = "separateJointCounts"
        self.outerJointCountSettingName = "outerJointCount"
        self.curveId = curveId
        self.jointIdPrefix = jointIdPrefix
        # brow primary, the largest control for the brow
        self.mainCtrlId = mainCtrlId
        self.railsMainId = "railsMain"
        self.rigCurveIds = ("innerCurve", "midCurve", "outerCurve")

        # macro ctrl ids are the primaries for each section of the brow
        self.primaryCtrlIdPrefix = primaryCtrlIdPrefix
        # secondary Ctrl ids are the ones that are tweakers
        self.secondaryCtrlIdPrefix = secondaryCtrlIdPrefix
        self._ctrlCount = 4
        self._tweakerParamValue = 0.25
        # ctrl ids without the prefix for all ctrls except for the masterCtrl
        self._baseCtrlIds = ctrlIds
        self._secondaryCtrlIds = [secondaryCtrlIdPrefix + str(i) for i in ctrlIds]
        self._tangentCtrlIds = tangentCtrlIds
        # primaries only exist on 0, 2, 3 indices as the index 1 is the tweaker
        self._primaryCtrlIds = [
            primaryCtrlIdPrefix + str(ctrlId)
            for index, ctrlId in enumerate(ctrlIds)
            if index != 1
        ]
        # guide ids which are used to calculate the translation min/max for the rail ctrls
        self._primaryMinMaxIds = []
        for i in self._primaryCtrlIds:
            self._primaryMinMaxIds.extend((i + "min", i + "Max"))
        self._railIds = [self.guideRailId(i) for i in self._primaryCtrlIds]

        self._tweakerParamPosSettingName = self._secondaryCtrlIds[1] + "Pos"

    def guideJntParamPosSettingName(self, index):
        """Generate the setting name for the joint parameter position for a given index.

        :param index: int
        :type index: The index for the setting name.
        :return: str
        :rtype: The setting name for the joint parameter position for the given curve and index.
        """
        return "{}{}Pos".format(self.jointIdPrefix, str(index).zfill(2))

    def guideJntParams(self):
        """Returns all jnt position parameter names which are used to determine the location along the curve.

        :rtype: list[str]
        """
        settings = self.component.definition.guideLayer.guideSettings(
            self.jointCountSettingName, self.outerJointCountSettingName, self.separateCountsSettingName
        )
        jointCount = settings[self.jointCountSettingName]
        outerJointCount = settings[self.outerJointCountSettingName]
        separateCounts = settings[self.separateCountsSettingName]

        count = jointCount.value if not separateCounts.value else jointCount.value + outerJointCount.value
        return [self.guideJntParamPosSettingName(i) for i in range(count)]

    def guideSecondaryCtrlId(self, index):
        """Generate the control ID for a given curve and index.

        :param index: int
        :type index: The index for the control ID.
        :return: str
        :rtype: The control ID for the given curve and index.
        """
        return self._secondaryCtrlIds[index]

    def guideMinMaxCtrlIds(self, primaryCtrlId):
        """Returns the min max guide ids for the specified primary ctrl id.

        :param primaryCtrlId: The primary ctrl id to retrieve the min/max
        :type primaryCtrlId: str
        :rtype: tuple[str, str]
        """
        primaryIndex = self._primaryCtrlIds.index(primaryCtrlId)
        startIndex = primaryIndex * 2
        return (
            self._primaryMinMaxIds[startIndex],
            self._primaryMinMaxIds[startIndex + 1],
        )

    def guideJointId(self, index):
        """Generate the joint ID for a given curve and index.

        :param index: int
        :type index: The index for the joint ID.
        :return: str
        :rtype: The joint ID for the given curve and index.
        """
        return "{}{}".format(self.jointIdPrefix, str(index).zfill(2))

    def guideRailId(self, primaryGuideId):
        """ Returns the guide rail id for the specified primary guide id.
        :param primaryGuideId: The primary guide/ctrl id
        :type primaryGuideId: str
        :rtype: str
        """
        return "{}Rail".format(primaryGuideId)

    def guideJointIds(self):
        """Generate a list of joint IDs for a given curve.

        :return: list
        :rtype: A list of joint IDs for the given curve.
        """
        settings = self.component.definition.guideLayer.guideSettings(
            self.jointCountSettingName, self.outerJointCountSettingName, self.separateCountsSettingName
        )
        jointCount = settings[self.jointCountSettingName]
        outerJointCount = settings[self.outerJointCountSettingName]
        separateCounts = settings[self.separateCountsSettingName]

        count = jointCount.value if not separateCounts.value else jointCount.value + outerJointCount.value
        return [self.guideJointId(i) for i in range(count)]

    def createGuideCurve(self, meshObject, vertices):
        self.deleteGuideCurve()
        guideLayer = self.component.guideLayer()
        topVertsGraph = mesh.constructVerticeGraph(meshObject.dagPath(), vertices)
        topVertexLoops = mesh.sortLoops(topVertsGraph)
        positions = mesh.vertexPositions(
            meshObject.dagPath(), topVertexLoops[0], sortKey="x"
        )
        if len(positions) < 4:
            return
        # create the scene guide with no shape then create the shape from the positions
        curveGuide = guideLayer.createGuide(
            id=self.curveId,
            translate=positions[int(len(positions) * 0.5)],
            parent="root",
            scale=(0.3, 0.3, 0.3),
            shape="cube",
            pivotShape="sphere_arrow",
        )
        curve = _generateGuideCurve(self.curveId, positions, 8)

        curveGuide.setShapeNode(curve)
        curve.setParent(guideLayer.rootTransform())
        curve.setShapeColour((1.0, 0.897, 0.073), shapeIndex=-1)
        self.component.definition.guideLayer.createGuide(
            **curveGuide.serializeFromScene(
                extraAttributesOnly=True, includeNamespace=False, useShortNames=True
            )
        )
        container = self.component.container()
        if container:
            container.publishNodes([curveGuide, curveGuide.shapeNode()])

        _shiftCurvePoints(curve)
        self._createCurveGuides(curve)

        self.component.saveDefinition(self.component.definition)
        self.component.rig.buildGuides([self.component])
        return curveGuide

    def deleteGuideCurve(self):
        """Deletes a guide curve based on the provided curve ID."""
        guideLayer = self.component.guideLayer()

        ids = (
                [self.curveId, self.mainCtrlId, self.railsMainId]
                + self._primaryCtrlIds
                + self._railIds
                + self._secondaryCtrlIds
                + self.guideJointIds()
                + self._tangentCtrlIds
                + self._primaryMinMaxIds
        )

        guideLayer.deleteGuides(*ids)
        self.component.definition.guideLayer.deleteGuides(*ids)

    def preUpdateGuideSettings(self, settings):
        """First stage of updating guide settings. Intended to delete anything from.

        :type settings: dict
        :return: Whether to rebuild the guides and whether the post-update operations should be executed
        :rtype: tuple[bool, bool]
        """

        rebuild, runPostUpdate = False, False
        guideLayerDef = self.component.definition.guideLayer
        jointCount = settings.get(self.jointCountSettingName,
                                  guideLayerDef.guideSetting(self.jointCountSettingName).value)
        outerJointCount = settings.get(self.outerJointCountSettingName,
                                       guideLayerDef.guideSetting(self.outerJointCountSettingName).value)
        separateJointCounts = settings.get(self.separateCountsSettingName,
                                           guideLayerDef.guideSetting(self.separateCountsSettingName).value)
        for settingName, value in settings.items():
            if settingName in (
                    self.jointCountSettingName, self.outerJointCountSettingName, self.separateCountsSettingName):
                if len(self.guideJointIds()) == value:
                    rebuild = False
                else:
                    rebuild = self._handleGuideJointCountChanged(jointCount,
                                                                 outerJointCount,
                                                                 separateJointCounts
                                                                 )
            if settingName == "jointRotationFollowsCurve":
                rebuild = True  # force a rebuild to update the motion paths etc
        return rebuild, runPostUpdate

    def validateGuides(self, validationInfo):
        """

        :param validationInfo:
        :type validationInfo: :class:`api.ValidationInfo`
        """
        guideLayerDef = self.component.definition.guideLayer

        curveGuide = guideLayerDef.guide(self.curveId)
        if not curveGuide:
            validationInfo.status = api.VALIDATION_ERROR
            validationInfo.message += "Missing Brow Curve. Please create one through the artist UI.\n"

        return True

    def preAlignGuides(self):
        if not self.active():
            return [], []

        guideLayer = self.component.guideLayer()
        guides = []
        matrices = []

        guideMap = {i.id(): i for i in guideLayer.iterGuides()}
        # when the brow curve doesn't exist, this makes it possible to build
        # but without a brow. Useful where users either fucked up the workflow, intentional
        # didn't finish the brow.
        if not guideMap.get(self.curveId):
            return [], []
        curveShapeNode = guideMap[self.curveId].shapeNode()
        self._deleteGuideSkinCluster(curveShapeNode, curveShapeNode.shapes()[0])
        secondaryGuides = [guideMap[i] for i in self._secondaryCtrlIds]
        innerGuide, tweakerGuide, midGuide, outerGuide = secondaryGuides
        tangentIdsPairs = list(general.chunks(self._tangentCtrlIds, 2))
        for sourceGuide, targetGuide in (
                (innerGuide, tweakerGuide),
                (outerGuide, midGuide),
        ):
            if not sourceGuide.attribute(api.constants.AUTOALIGN_ATTR).value():
                continue
            guides.append(sourceGuide)
            matrices.append(
                _mirrorGuideAlign(
                    sourceGuide, targetGuide, flipAim=True, constraintAxis=False
                )
            )
        # for the mid guide we take the rotation alignment between the in and out mid tangents and copy
        # that to the mid guide, this allows an average and handles more angry default brow shapes eg. croc
        if (
                guideMap[tangentIdsPairs[1][0]]
                        .attribute(api.constants.AUTOALIGN_ATTR)
                        .value()
        ):
            inTangentMatrix = _mirrorGuideAlign(
                guideMap[tangentIdsPairs[1][0]],
                guideMap[tangentIdsPairs[1][1]],
                flipAim=True,
                constraintAxis=False,
                customAimVector=midGuide.aimVector(),
                customUpVector=midGuide.upVector(),
            )
            midGuideTransform = midGuide.transformationMatrix()
            midGuideTransform.setRotation(
                zapi.TransformationMatrix(inTangentMatrix).rotation(asQuaternion=True)
            )
            guides.append(midGuide)
            matrices.append(midGuideTransform.asMatrix())

        # tweaker requires an extra hardcoded rotation offset
        if tweakerGuide.attribute(api.constants.AUTOALIGN_ATTR).value():
            guides.append(tweakerGuide)
            matrices.append(
                _mirrorGuideAlign(
                    tweakerGuide,
                    innerGuide,
                    flipAim=True,
                    rotMultipier=(
                        TWEAKER_TANGENT_DEFAULT_ROT,
                        TWEAKER_TANGENT_DEFAULT_ROT_SCALED,
                    ),
                    constraintAxis=False,
                )
            )

        # we skip the end guide and do that tangent after the loop for code simplicity
        for index, secondaryGuide in enumerate(secondaryGuides[1:-1]):
            for tangIdx, tangentGuideId in enumerate(tangentIdsPairs[index]):
                tangentGuide = guideMap[tangentGuideId]
                if not tangentGuide.attribute(api.constants.AUTOALIGN_ATTR).value():
                    continue
                guides.append(tangentGuide)
                matrices.append(
                    _mirrorGuideAlign(
                        tangentGuide, secondaryGuide, flipAim=True, constraintAxis=False
                    )
                )
        # outer tangent
        tangentGuide = guideMap[self._tangentCtrlIds[-1]]
        if tangentGuide.attribute(api.constants.AUTOALIGN_ATTR).value():
            guides.append(tangentGuide)
            matrices.append(
                _mirrorGuideAlign(
                    tangentGuide, outerGuide, flipAim=True, constraintAxis=False
                )
            )
        return guides, matrices

    def postAlignGuides(self):
        if not self.active():
            return
        curveGuide = self.component.guideLayer().guide(self.curveId)
        if not curveGuide:
            return
        self.postSetupGuide()

    def preMirror(self, translate, rotate, parent):
        if not self.active():
            return
        guideLayer = self.component.guideLayer()
        # remove the connection first to avoid changes to transform
        guides = list(guideLayer.iterGuides())
        for guide in guides:
            offsetParent = guide.attribute("offsetParentMatrix")
            source = offsetParent.source()
            if source:
                source.disconnect(guide.attribute("offsetParentMatrix"))

        for guideId in self._secondaryCtrlIds + self.guideJointIds():
            graphName = graphconstants.kMotionPathGuide + guideId
            guideLayer.deleteNamedGraph(
                graphName, self.component.configuration.graphRegistry()
            )
        curveGuide = guideLayer.guide(self.curveId)
        if not curveGuide:
            return
        curveShapeNode = curveGuide.shapeNode()
        curveShape = curveShapeNode.shapes()[0]
        self._deleteGuideSkinCluster(curveShapeNode, curveShape)

    def postMirror(self, translate, rotate, parent):
        if not self.active():
            return
        self.postSetupGuide()

    def postSetupGuide(self):
        if not self.active():
            return
        guideLayer = self.component.guideLayer()
        guideSettings = guideLayer.guideSettings()

        guides = {i.id(): i for i in guideLayer.iterGuides(includeRoot=True)}
        try:
            curveGuide = guides[self.curveId]
            curve = guides[self.curveId].shapeNode()  # type: api.ControlNode
        except KeyError:
            return
        jointIds = self.guideJointIds()
        curveShape = curve.shapes()[0]
        tangentIdsPairs = list(general.chunks(self._tangentCtrlIds, 2))
        namingConfig = self.component.namingConfiguration()
        compName, compSide = self.component.name(), self.component.side()
        # otherwise the cluster will be double and to ensure correctness between updates.
        self._deleteGuideSkinCluster(curve, curveShape)
        # so we don't bloody create duplicates.
        for jnt in guideLayer.joints():
            jnt.delete()
        guideLayer.disconnectAllJoints()
        # we now bind the curve cvs positions to the secondary and tangent guides pos
        for index, guideId in enumerate(self._secondaryCtrlIds):
            guide = guides[guideId]
            _createGuideJoint(guideLayer, guide, namingConfig, compName, compSide)

            # bind the rail guide but only from the secondary translation, get the rotate/scale from the root
            # to ensure rotating the whole guide system does the right thing
            if index != 1:
                railGuideId = self.guideRailId(
                    self._primaryCtrlIds[index if index == 0 else index - 1]
                )
                railGuide = guides[railGuideId]  # type: api.Guide
                currentWorldMatrix = railGuide.worldMatrix()
                worldMatrixMult = zapi.createDG(
                    namingConfig.resolve(
                        "object",
                        {
                            "componentName": compName,
                            "side": compSide,
                            "section": railGuideId + "World",
                            "type": "multMatrix",
                        },
                    ),
                    "multMatrix",
                )
                secondaryGuideOut = zapi.createDG(
                    namingConfig.resolve(
                        "object",
                        {
                            "componentName": compName,
                            "side": compSide,
                            "section": guideId + "translateOnly",
                            "type": "pickMatrix",
                        },
                    ),
                    "pickMatrix",
                )
                secondaryGuideOut.useRotate.set(False)
                secondaryGuideOut.useScale.set(False)
                secondaryGuideOut.useShear.set(False)
                guide.worldMatrixPlug().connect(worldMatrixMult.matrixIn[0])
                guides["root"].worldInverseMatrix[0].connect(
                    worldMatrixMult.matrixIn[1]
                )
                worldMatrixMult.matrixSum.connect(secondaryGuideOut.inputMatrix)
                secondaryGuideOut.outputMatrix.connect(railGuide.offsetParentMatrix)
                # todo: why doesn't setWorldMatrix work for scale? investigate
                cmds.xform(
                    railGuide.fullPathName(),
                    absolute=True,
                    matrix=list(currentWorldMatrix),
                    worldSpace=True,
                )

            if index != 0:
                tangentIds = tangentIdsPairs[index - 1]
                tangentInGuide = guides[tangentIds[0]]
                _createGuideJoint(
                    guideLayer, tangentInGuide, namingConfig, compName, compSide
                )

                if index != len(self._secondaryCtrlIds) - 1:
                    tangentOutGuide = guides[tangentIds[1]]
                    _createGuideJoint(
                        guideLayer, tangentOutGuide, namingConfig, compName, compSide
                    )

        lockAttrs = [zapi.localTranslateAttr, zapi.localRotateAttr, zapi.localScaleAttr]
        graph = self.component.configuration.graphRegistry().graph(graphconstants.kMotionPathGuide)
        graphName = graph.name
        followCurve = guideSettings.attribute("jointRotationFollowsCurve").value()
        for index, guideId in enumerate(jointIds):
            paramSettingId = self.guideJntParamPosSettingName(index)
            attr = guideSettings.attribute(paramSettingId)
            guide = guides[guideId]
            graph.name = graphName + guideId
            with zapi.lockStateAttrContext(guide, lockAttrs, False):
                _bindGuideToCurve(self, guide, curveShape, attr, graph, follow=followCurve)
            guide.setLockStateOnAttributes(lockAttrs, True)
        # lock attributes of min/max guides
        lockAttrs = zapi.localRotateAttrs + zapi.localScaleAttrs
        for guideId in self._primaryCtrlIds:
            minId, maxId = self.guideMinMaxCtrlIds(guideId)
            for guide in (guides[minId], guides[maxId]):  # type: api.Guide
                guide.setLockStateOnAttributes(lockAttrs, True)
        curve.offsetParentMatrix.disconnectAll()
        self._skinGuideJoints(curve)

    def setupDeformLayer(self, parentJoint):
        if not self.active():
            return
        compDefinition = self.component.definition
        deformLayer = compDefinition.deformLayer
        guideLayer = compDefinition.guideLayer
        jointIds = self.guideJointIds()
        for index, guideId in enumerate(jointIds):
            guide = guideLayer.guide(guideId)
            if not guide:
                continue
            deformLayer.createJoint(
                id=guideId,
                rotateOrder=guide.get("rotateOrder", 0),
                translate=guide.get("translate", (0, 0, 0)),
                rotate=guide.rotate,
                attributes=[{"name": "radius", "value": 0.2}],
            )

    def postSetupDeform(self, parentNode):
        if not self.active():
            return

        deform = self.component.deformLayer()
        jointId = self.guideJointId(0)
        jnt = deform.joint(jointId)
        if not jnt:  # can happen if the curve wasn't built
            return
        self.createOutputBSNode(deform.rootTransform(), deform)

    def setupInputs(self):
        if not self.active():
            return
        inputLayer = self.component.inputLayer()
        parentIn = inputLayer.inputNode("parent")
        guideDef = self.component.definition.guideLayer.guide(self._primaryCtrlIds[0])
        if not guideDef:
            return
        parentIn.setWorldMatrix(
            guideDef.transformationMatrix(True, True, scale=False).asMatrix()
        )

    def setupRig(self, parentNode):
        if not self.active():
            return
        guideLayerDef = self.component.definition.guideLayer
        if not guideLayerDef.guide(self.curveId):
            return [], []
        rigLayer = self.component.rigLayer()
        rootTransform = rigLayer.rootTransform()
        inputLayer = self.component.inputLayer()
        parentIn = inputLayer.inputNode("parent")
        namingConfig = self.component.namingConfiguration()
        compName, compSide = self.component.name(), self.component.side()

        mainCtrl = self._createMainCtrl(
            rigLayer, guideLayerDef, parentIn, namingConfig, compName, compSide
        )

        extrasHrc = zapi.createDag(
            namingConfig.resolve(
                "object",
                {
                    "componentName": compName,
                    "side": compSide,
                    "section": "extras",
                    "type": "hrc",
                },
            ),
            "transform",
            parent=rootTransform,
        )

        builder = _CurveBuilder(
            self.curveId,
            self.rigCurveIds,
            self.component,
            self,
            hrcs={"extraHrc": extrasHrc, "ctrlHrc": mainCtrl},
        )
        builder.buildRig()
        self.setControlNaming()

    def _createMainCtrl(
            self, rigLayer, guideLayerDef, parentIn, namingConfig, compName, compSide
    ):
        """

        :param rigLayer:
        :type rigLayer: :class:`api.HiveRigLayer`
        """
        mainCtrlDef = guideLayerDef.guide(self.mainCtrlId)
        scaleVec, _ = mainCtrlDef.mirrorScaleVector()
        mainCtrl = rigLayer.createControl(
            id=mainCtrlDef.id,
            translate=mainCtrlDef.translate,
            rotate=mainCtrlDef.rotate,
            scale=scaleVec,
            parent=rigLayer.rootTransform(),
            rotateOrder=mainCtrlDef.rotateOrder,
            shape=mainCtrlDef.shape,
            selectionChildHighlighting=self.component.configuration.selectionChildHighlighting,
        )

        parentOffsetMult = zapi.createDG(
            namingConfig.resolve(
                "object",
                {
                    "componentName": compName,
                    "side": compSide,
                    "section": "parentSpaceOffset",
                    "type": "multMatrix",
                },
            ),
            "multMatrix",
        )
        parentOffsetMult.matrixIn[0].set(
            mainCtrl.worldMatrix() * parentIn.worldInverseMatrixPlug().value()
        )
        parentIn.worldMatrixPlug().connect(parentOffsetMult.matrixIn[1])
        parentOffsetMult.matrixSum.connect(mainCtrl.offsetParentMatrix)
        rigLayer.addExtraNode(parentOffsetMult)
        mainCtrl.resetTransform()
        return mainCtrl

    def postSetupRig(self, parentNode):
        if not self.active():
            return
        if not self.component.definition.guideLayer.guide(self.curveId):
            return [], []
        rigLayer = self.component.rigLayer()
        controlPanel = rigLayer.controlPanel()
        secondaryCtrlVisAttr = controlPanel.attribute("secondaryCtrlVis")
        primaryCtrlVisAttr = controlPanel.attribute("primaryCtrlVis")
        railMainCtrlVisAttr = controlPanel.attribute("railMainCtrlVis")
        secondaries = self._tangentCtrlIds
        secondaries.append(self._secondaryCtrlIds[0])
        secondaries.extend(self._secondaryCtrlIds[2:])
        ctrls = rigLayer.findControls(*secondaries)
        for ctrl in ctrls:
            ctrl.setLockStateOnAttributes([zapi.localScaleAttr], True)
            ctrl.showHideAttributes([zapi.localScaleAttr], False)
            for shape in ctrl.iterShapes():
                secondaryCtrlVisAttr.connect(shape.visibility)
                shape.setLockStateOnAttributes(["visibility"], True)
        railMainCtrl, tweakerCtrl = rigLayer.findControls(
            self.railsMainId, self._secondaryCtrlIds[1]
        )

        for ctrl in rigLayer.findControls(*self._primaryCtrlIds) + [tweakerCtrl]:
            ctrl.setLockStateOnAttributes([zapi.localScaleAttr], True)
            ctrl.showHideAttributes([zapi.localScaleAttr], False)
            for shape in ctrl.iterShapes():
                primaryCtrlVisAttr.connect(shape.visibility)
                shape.setLockStateOnAttributes(["visibility"], True)
        # rails main needs special attention to lock and hide everything except for the upVector axis
        mainCtrlGuide = self.component.definition.guideLayer.guide(self.railsMainId)
        upVector = mainCtrlGuide.upVector()
        upVectorIdx = mayamath.primaryAxisIndexFromVector(upVector)
        perpendIndex, _ = mayamath.perpendicularAxisFromAlignVectors(
            mainCtrlGuide.aimVector(), upVector
        )
        vectorNames = ["visibility"]
        for index in range(3):
            if index != upVectorIdx:
                vectorNames.append(zapi.localTranslateAttrs[index])
            if index != perpendIndex:
                vectorNames.append(zapi.localRotateAttrs[index])
        for shape in railMainCtrl.iterShapes():
            railMainCtrlVisAttr.connect(shape.visibility)
        railMainCtrl.setLockStateOnAttributes(zapi.localScaleAttrs + vectorNames, True)
        railMainCtrl.showHideAttributes(zapi.localScaleAttrs + vectorNames, False)

    def setControlNaming(self):
        compName, compSide = self.component.name(), self.component.side()
        namingConfig = self.component.namingConfiguration()
        rigLayer = self.component.rigLayer()
        controls = rigLayer.findControls(
            *(
                    self._primaryCtrlIds
                    + self._secondaryCtrlIds
                    + [self.railsMainId, self.mainCtrlId]
                    + self._tangentCtrlIds
            )
        )
        for ctrl in controls:
            if not ctrl:
                continue
            ctrlId = ctrl.id()
            ctrl.rename(
                namingConfig.resolve(
                    "controlName",
                    {
                        "componentName": compName,
                        "side": compSide,
                        "id": ctrlId,
                        "type": "control",
                    },
                )
            )
            srt = ctrl.srt()
            if srt:
                srt.rename(
                    namingConfig.resolve(
                        "controlName",
                        {
                            "componentName": compName,
                            "side": compSide,
                            "id": ctrlId,
                            "type": "srt",
                        },
                    )
                )

    def _createCurveGuides(self, curve):
        curveShape = curve.shapes()[0]
        crvMfn = curveShape.mfn()
        guideLayerDef = self.component.definition.guideLayer
        guideSettings = self.component.definition.guideLayer.guideSettings(
            self.jointCountSettingName, self.outerJointCountSettingName, self.separateCountsSettingName
        )
        separateCounts = guideSettings[self.separateCountsSettingName].value
        # create control curve guides  and attach to the curve
        crvLength = crvMfn.length()

        self._createCtrlGuides(guideLayerDef, curveShape)
        self._createRailGuides(guideLayerDef)
        point, midParam = curveShape.mfn().closestPoint(zapi.Point(
            guideLayerDef.guide(self._primaryCtrlIds[1]).translate))
        if guideSettings:
            midParam = curves.parametricSpaceFromParametricLength(curveShape.object(), midParam)
        self._configureAndGenerateJointGuides(guideLayerDef,
                                              curveShape,
                                              guideSettings["jointCount"].value,
                                              guideSettings["outerJointCount"].value,
                                              midParam,
                                              separateCounts)
        lengthParam = crvMfn.findParamFromLength(crvLength * 0.5)
        pos = zapi.Vector(crvMfn.getPointAtParam(lengthParam, space=zapi.kWorldSpace))
        primaryPosOffsetVec = zapi.worldFrontAxis()
        guideLayerDef.createGuide(
            name=self.curveId,
            pivotShape="locator",
            pivotColor=[0.477, 1, 0.073],
            shape=RAIL_MAIN_GUIDE_SHAPE,
            id=self.railsMainId,
            parent="root",
            color=DEFAULT_MAIN_CTRL_COLOR,
            translate=list(primaryPosOffsetVec + pos),
            scale=DEFAULT_PRIMARY_GUIDE_CTRL_SCALE,
            selectionChildHighlighting=self.component.configuration.selectionChildHighlighting,
            shapeTransform={
                "translate": list(primaryPosOffsetVec + pos),
                "scale": DEFAULT_RAILS_MAIN_SHAPE_SCALE,
                "rotate": (math.pi * 0.5, 0.0, 0.0),
            },
            attributes=[
                {
                    "name": api.constants.MIRROR_BEHAVIOUR_ATTR,
                    "value": mayamath.MIRROR_SCALE,
                    "Type": zapi.attrtypes.kMFnNumeric3Float,
                },
                {
                    "name": api.constants.AUTOALIGNAIMVECTOR_ATTR,
                    "value": [1.0, 0.0, 0.0],
                    "Type": zapi.attrtypes.kMFnNumeric3Float,
                },
                {
                    "name": api.constants.AUTOALIGNUPVECTOR_ATTR,
                    "value": [0.0, 1.0, 0.0],
                    "Type": zapi.attrtypes.kMFnNumeric3Float,
                },
            ],
        )
        cvPositions = crvMfn.cvPositions(zapi.kWorldSpace)
        lastPos = zapi.Vector(cvPositions[-1])
        normal = crvMfn.tangent(1.0, zapi.kWorldSpace)
        guideLayerDef.createGuide(
            name=self.curveId,
            pivotShape="locator",
            pivotColor=[0.477, 1, 0.073],
            shape="arrow_4way_roundFlat",
            id=self.mainCtrlId,
            parent="root",
            color=DEFAULT_MAIN_CTRL_COLOR,
            translate=list(primaryPosOffsetVec + pos),
            scale=DEFAULT_PRIMARY_GUIDE_CTRL_SCALE,
            selectionChildHighlighting=self.component.configuration.selectionChildHighlighting,
            shapeTransform={
                "translate": list(primaryPosOffsetVec + normal + lastPos),
                "scale": DEFAULT_PRIMARY_GUIDE_SHAPE_SCALE,
                "rotate": (math.pi * 0.5, 0.0, 0.0),
            },
            attributes=[
                {
                    "name": api.constants.MIRROR_BEHAVIOUR_ATTR,
                    "value": mayamath.MIRROR_SCALE,
                    "Type": zapi.attrtypes.kMFnNumeric3Float,
                },
                {
                    "name": api.constants.AUTOALIGNAIMVECTOR_ATTR,
                    "value": [1.0, 0.0, 0.0],
                    "Type": zapi.attrtypes.kMFnNumeric3Float,
                },
                {
                    "name": api.constants.AUTOALIGNUPVECTOR_ATTR,
                    "value": [0.0, 1.0, 0.0],
                    "Type": zapi.attrtypes.kMFnNumeric3Float,
                },
            ],
        )

        return True

    def _createCtrlGuides(self, guideLayerDef, curveShape):

        curveMfn = curveShape.mfn()
        cvPositions = curveMfn.cvPositions(zapi.kWorldSpace)
        tangentIdsPairs = list(general.chunks(self._tangentCtrlIds, 2))
        generalKwargs = {
            "selectionChildHighlighting": self.component.configuration.selectionChildHighlighting,
            "guideLayerDef": guideLayerDef,
            "upVector": (0.0, 1.0, 0.0),
        }
        primaryPosOffsetVec = zapi.worldFrontAxis()
        primaryPosOffsetVecHalf = primaryPosOffsetVec * 0.5
        for index, guideId in enumerate(self._secondaryCtrlIds):
            cvPos = zapi.Vector(cvPositions[CV_POS_INDICES[index]])
            ctrlRotation = () if index != 1 else TWEAKER_TANGENT_GUIDE_DEFAULT_ROT
            shapeRotation = (
                (math.pi * 0.5, 0, 0)
                if index != 1
                else (math.pi * 0.5, 0, math.pi * -0.25)
            )
            position = primaryPosOffsetVec + cvPos
            secondaryGuide = _createGuideDef(
                guideId=guideId,
                parent="root",
                ctrlColor=DEFAULT_SECONDARY_CTRL_COLOR if index != 1 else DEFAULT_TWEAKER_CTRL_COLOR,
                position=list(cvPos),
                ctrlScale=(
                    DEFAULT_GUIDE_SHAPE_SCALE
                    if index != 1
                    else DEFAULT_TWEAKER_TANGENT_CTRL_SCALE
                ),
                ctrlRotation=shapeRotation,
                rotation=ctrlRotation,
                shape=SECONDARY_GUIDE_SHAPE if index != 1 else TWEAKER_GUIDE_SHAPE,
                aimVector=(
                    zapi.Vector(1.0, 0.0, 0.0)
                    if index != 3
                    else zapi.Vector(-1.0, 0.0, 0.0)
                ),
                ctrlPosition=list(primaryPosOffsetVecHalf + cvPos) if index != 1 else list(position),
                **generalKwargs
            )

            if index != 0:
                # create the tangent guides
                tangentIds = tangentIdsPairs[index - 1]
                # create in Tangent
                _createGuideDef(
                    guideId=tangentIds[0],
                    parent=secondaryGuide.id,
                    ctrlColor=DEFAULT_SECONDARY_CTRL_COLOR,
                    position=list(cvPositions[CV_POS_INDICES[index] - 1])[:-1],
                    ctrlScale=DEFAULT_TANGENT_CTRL_SCALE,
                    shape=TANGENT_GUIDE_SHAPE,
                    aimVector=zapi.Vector(-1.0, 0.0, 0.0),
                    ctrlPosition=list(primaryPosOffsetVecHalf + zapi.Vector(cvPositions[CV_POS_INDICES[index] - 1])),
                    **generalKwargs
                )
                if index != len(self._secondaryCtrlIds) - 1:
                    # last cv only has one tangent
                    _createGuideDef(
                        guideId=tangentIds[1],
                        parent=secondaryGuide.id,
                        ctrlColor=DEFAULT_SECONDARY_CTRL_COLOR,
                        position=list(cvPositions[CV_POS_INDICES[index] + 1])[:-1],
                        ctrlScale=DEFAULT_TANGENT_CTRL_SCALE,
                        shape=TANGENT_GUIDE_SHAPE,
                        aimVector=zapi.Vector(-1.0, 0.0, 0.0),
                        ctrlPosition=list(
                            primaryPosOffsetVecHalf + zapi.Vector(cvPositions[CV_POS_INDICES[index] + 1])),
                        **generalKwargs
                    )

    def _configureAndGenerateJointGuides(self, guideLayerDef, curveShape,
                                         jointCount, outerJointCount,
                                         midParameter=0.5,
                                         separateJointCounts=False,
                                         ):
        """Based on the joint counts generate parameters and joint guides
        """
        if separateJointCounts:
            # todo: safetly check this to ensure no less than 2 joints exist.
            params = list(zoomath.lerpCount(0, midParameter, jointCount))
            _createGuideParamSettings(
                guideLayerDef,
                list(zoomath.lerpCount(0.000, midParameter, jointCount)),
                self.guideJntParamPosSettingName,
            )
            guideLayerDef.guideSetting(self.guideJntParamPosSettingName(0)).value = 0.001
            nextParam = midParameter + params[1]
            _createGuideParamSettings(
                guideLayerDef,
                list(zoomath.lerpCount(nextParam, 1.0, outerJointCount)),
                lambda index: self.guideJntParamPosSettingName(index + jointCount),
            )

            self._createJointGuides(guideLayerDef, curveShape, jointCount, 0.0, midParameter)
            self._createJointGuides(guideLayerDef, curveShape, outerJointCount,
                                    nextParam, 1.0, startIndex=jointCount)
        else:
            _createGuideParamSettings(
                guideLayerDef,
                list(zoomath.lerpCount(0.001, 1.0, jointCount)),
                self.guideJntParamPosSettingName,
            )
            self._createJointGuides(guideLayerDef, curveShape, jointCount, 0.0, 1.0)

    def _createJointGuides(self, guideLayerDef, curve, count, start, end, startIndex=0):
        curveMfn = curve.mfn()
        curveLength = curveMfn.length()
        iterator = list(zoomath.lerpCount(start, end, count))
        for index, param in enumerate(iterator):  # skip the first and last
            paramSetting = guideLayerDef.guideSetting(
                self.guideJntParamPosSettingName(index + startIndex)
            )
            lengthParam = curveMfn.findParamFromLength(curveLength * paramSetting.value)
            pos = zapi.Vector(
                curveMfn.getPointAtParam(lengthParam, space=zapi.kWorldSpace)
            )
            guideLayerDef.createGuide(
                id=self.guideJointId(index + startIndex),
                parent="root",
                translate=list(pos),
                pivotShape="sphere",
                scale=DEFAULT_GUIDE_JNT_SCALE,
                selectionChildHighlighting=self.component.configuration.selectionChildHighlighting,
            )

    def _createRailGuides(self, guideLayerDef):
        createRails = True
        if not createRails:
            return

        def _offsetCurveData(curveData, translation):
            for shape in curveData.values():
                for cv in shape["cvs"]:
                    cv[0] += translation.x
                    cv[1] += translation.y
                    cv[2] += translation.z

        generalKwargs = {
            "selectionChildHighlighting": self.component.configuration.selectionChildHighlighting,
            "guideLayerDef": guideLayerDef,
            "upVector": (0.0, 1.0, 0.0),
        }
        primaryPosOffsetVec = zapi.worldFrontAxis()
        for index, primaryGuideId in enumerate(self._primaryCtrlIds):
            secondaryGuide = guideLayerDef.guide(
                self.guideSecondaryCtrlId(index if index == 0 else index + 1)
            )
            shapeData = copy.deepcopy(RAIL_CURVE_SHAPE)
            _offsetCurveData(shapeData, secondaryGuide.translate)
            # create rail
            guideLayerDef.createGuide(
                id=self.guideRailId(primaryGuideId),
                parent="root",
                translate=list(secondaryGuide.translate),
                shape=shapeData,
                scale=DEFAULT_GUIDE_JNT_SCALE,
                selectionChildHighlighting=self.component.configuration.selectionChildHighlighting,
                shapeTransform={
                    "translate": list(secondaryGuide.translate),
                },
            )
            position = secondaryGuide.translate
            # primary
            _createGuideDef(
                guideId=primaryGuideId,
                parent="root",
                ctrlColor=DEFAULT_PRIMARY_CTRL_COLOR,
                position=list(primaryPosOffsetVec + position),
                ctrlScale=DEFAULT_PRIMARY_GUIDE_SHAPE_SCALE if index != 1 else DEFAULT_PRIMARY_MID_GUIDE_SHAPE_SCALE,
                shape=PRIMARY_GUIDE_SHAPE,
                aimVector=zapi.Vector(1.0, 0.0, 0.0),
                **generalKwargs
            )
            minId, maxId = self.guideMinMaxCtrlIds(primaryGuideId)
            _createGuideDef(
                guideId=minId,
                parent=primaryGuideId,
                ctrlColor=DEFAULT_MAIN_CTRL_COLOR,
                position=list(
                    primaryPosOffsetVec + position + (zapi.worldUpAxis() * -1)
                ),
                shape={},
                aimVector=zapi.Vector(1.0, 0.0, 0.0),
                **generalKwargs
            )
            _createGuideDef(
                guideId=maxId,
                parent=primaryGuideId,
                ctrlColor=DEFAULT_MAIN_CTRL_COLOR,
                position=list(
                    primaryPosOffsetVec + position + RAIL_GUIDE_CURVE_MAX_POS
                ),
                shape={},
                aimVector=zapi.Vector(1.0, 0.0, 0.0),
                **generalKwargs
            )

    def _handleGuideJointCountChanged(self, jointCount, outerJointCount, separateJointCounts=False):
        guideLayer = self.component.guideLayer()
        guideLayerDef = self.component.definition.guideLayer
        curveGuide = guideLayer.guide(self.curveId)
        if not curveGuide:
            return False
        existingGuideIds = self.guideJointIds()
        curveShapeNode = curveGuide.shapeNode()
        curveShape = curveShapeNode.shapes()[0]
        guideSettings = [
            self.guideJntParamPosSettingName(i) for i in range(len(existingGuideIds))
        ]
        self._deleteGuideSkinCluster(curveShapeNode, curveShape)
        curveShape = curveShapeNode.shapes()[0]
        point, midParam = curveShape.mfn().closestPoint(zapi.Point(
            guideLayer.guide(self._primaryCtrlIds[1]).translation(zapi.kWorldSpace)))
        if separateJointCounts:
            midParam = curves.parametricSpaceFromParametricLength(curveShape.object(), midParam)
        guideLayerDef.deleteSettings(guideSettings)
        guideLayer.deleteGuides(*existingGuideIds)
        guideLayerDef.deleteGuides(*existingGuideIds)
        self._configureAndGenerateJointGuides(guideLayerDef,
                                              curveShape,
                                              jointCount, outerJointCount, midParam, separateJointCounts)
        return True

    def _skinGuideJoints(self, curveNode):
        cmds.skinCluster(
            [i.fullPathName() for i in self.component.guideLayer().iterJoints()]
            + [curveNode.fullPathName()],
            maximumInfluences=2,
        )

    def _deleteGuideSkinCluster(self, curve, curveShape):
        # otherwise the cluster will be double and to ensure correctness between updates.
        if deformers.clusterUpstreamFromNode(curveShape.object()):
            currentCvPositions = curveShape.cvPositions(zapi.kWorldSpace)
            cmds.skinCluster(curve.fullPathName(), unbind=True, edit=True)
            # find tweak node and delete otherwise the cv update will propagate
            tweakNode = curveShape.tweakLocation.sourceNode()
            if tweakNode is not None:
                tweakNode.delete()
            # force the cv update which will be rebound in post
            curveShape.setCVPositions(currentCvPositions, zapi.kWorldSpace)

    def differentiatorExtraNode(self, layer):
        """
        :return:
        :rtype: tuple[:class:`zapi.Plug`, :class:`zapi.DagNode`]
        """
        extraAttr = layer.addAttribute(
            META_EXTRA_ATTR, Type=zapi.attrtypes.kMFnMessageAttribute, isFalse=True
        )
        return extraAttr, extraAttr.sourceNode()

    def createOutputBSNode(self, parent, layer):
        namingConfig = self.component.namingConfiguration()
        compName, compSide = self.component.name(), self.component.side()
        attr, valueOutput = self.differentiatorExtraNode(layer)
        if valueOutput is None:
            # create space locator which contains attributes for primary motion output
            valueOutput = zapi.createDag(
                namingConfig.resolve(
                    "object",
                    {
                        "componentName": compName,
                        "side": compSide,
                        "section": "differentiatorBS",
                        "type": "transform",
                    },
                ),
                "locator"
            )
        valueOutput.setShapeColour((1.000, 0.587, 0.073))
        valueOutput.setParent(parent)

        layer.addExtraNode(valueOutput)
        valueOutput.message.connect(attr)
        for attrName in (
                "primaryInnerRail",
                "primaryMidRail",
                "primaryOuterRail",
                "primaryInnerX",
                "primaryMidX",
                "primaryOuterX"
        ):
            valueOutput.addAttribute(attrName, channelBox=True, locked=False, keyable=False)
        attrs = [zapi.localRotateAttr, zapi.localScaleAttr]
        valueOutput.showHideAttributes(attrs, False)
        valueOutput.setLockStateOnAttributes(attrs, True)
        container = self.component.container()
        container.publishNode(valueOutput)


class _CurveBuilder(object):
    """
    :param curveId: The ID of the curve.
    :type curveId: str
    :param component: The component that owns the curve.
    :type component: :class:`api.Component`
    :param subsystem: The subsystem that owns the curve.
    :type subsystem: :class:`BrowSubsystem`
    :param hrcs: The hierarchical dag Nodes.
    :type hrcs: dict[str, :class:`zapi.Dag`]
    """

    def __init__(self, curveId, rigCurveIds, component, subsystem, hrcs):
        self.rigCurveIds = rigCurveIds
        self.curveId = curveId
        self.component = component
        self.rigLayer = component.rigLayer()
        self.guideLayer = self.component.guideLayer()
        self.namingConfig = self.component.namingConfiguration()
        self.definition = self.component.definition
        self.guideLayerDef = self.definition.guideLayer
        self.compName, self.compSide = self.component.name(), self.component.side()
        self.subsystem = subsystem
        self.outputCurves = []
        self.outputCurveShapes = []
        self.controls = {}  # type: dict[str, api.ControlNode]
        self.rails = {}
        self.extrasHrc = hrcs["extraHrc"]  # type: zapi.DagNode
        self.ctrlHrc = hrcs["ctrlHrc"]  # type: zapi.DagNode
        self.railGraphs = []  # type: list[api.serialization.NamedDGGraph]
        self._masterControl = None  # type: api.ControlNode or None
        self._tangentCtrlIds = subsystem._tangentCtrlIds
        self.jointRailOutGraphName = graphconstants.kJointRailOut
        self.midPointNoRotGraphName = graphconstants.kBrowMidPointNoRot

    def buildRig(self):
        self._generateCurves()
        self._createMasterControl()
        self._createControls()
        self._createRailSystem()
        self._createAimSystem()
        self._bindJointsToCurve()
        self._connectDifferentiator()

    def _connectDifferentiator(self):
        _, extraNode = self.subsystem.differentiatorExtraNode(self.component.deformLayer())
        if not extraNode:
            return
        _, utils = zapi.buildConstraint(
            extraNode,
            drivers={"targets": (("", self._masterControl),)},
            constraintType="matrix",
        )
        panel = self.component.controlPanel()
        panel.attribute("showBSDifferentiator").connect(extraNode.visibility)

    def _generateCurves(self):
        """
        Generates lid curves based on the guides.
        """
        # Retrieve shape data from the curve guide definition
        curveGuideDef = self.guideLayerDef.guide(self.curveId)
        shapeData = curveGuideDef.shape
        # convert a single curve to 3 curves
        cvs = list(shapeData.values())[0]["cvs"]
        controlPanel = self.rigLayer.controlPanel()
        curveTemplateAttr = controlPanel.attribute("showCurveTemplate")
        cvSegments = mayamath.bezierSegments(cvs)
        for index, segment in enumerate(cvSegments):
            curve = zapi.nodeByObject(
                curves.createCurveFromPoints(self.rigCurveIds[index], segment)[0]
            )
            curve.setParent(self.extrasHrc)
            curve.rename(
                self.namingConfig.resolve(
                    "object",
                    {
                        "componentName": self.compName,
                        "side": self.compSide,
                        "section": self.rigCurveIds[index],
                        "type": "nurbsCurve",
                    },
                )
            )
            self.outputCurves.append(curve)
            self.outputCurveShapes.append(curve.shapes()[0])
            curveTemplateAttr.connect(curve.visibility)
            curve.template.set(1)
        self.rigLayer.addExtraNodes(self.outputCurves)

    def _createMasterControl(self):
        """
        Creates primary controls for the upper and lower curve based on guide information.
        """
        # Get the ID of the primary guide control for the current curve
        primaryGuideId = self.subsystem.railsMainId
        # Retrieve the guide information for the primary guide control
        primaryGuide = self.guideLayerDef.guide(primaryGuideId)
        # Calculate the distance between the top and bottom points of the guide
        scale, _ = primaryGuide.mirrorScaleVector()
        # Create the control based on the guide information
        ctrl = self.rigLayer.createControl(
            id=primaryGuideId,
            translate=primaryGuide.translate,
            rotate=primaryGuide.rotate,
            scale=scale,
            parent=self.ctrlHrc,
            rotateOrder=primaryGuide.rotateOrder,
            shape=primaryGuide.shape,
            selectionChildHighlighting=self.component.configuration.selectionChildHighlighting,
        )
        # Reset the transform of the control to its offset parent
        ctrl.resetTransformToOffsetParent()
        # Store the created control in the controls dictionary
        self.controls[primaryGuide.id] = ctrl
        self._masterControl = ctrl

    def _createControls(self):
        """
        Creates micro controls for the upper and lower curve based on guide information.
        """
        primaryGuides = self.guideLayerDef.findGuides(*self.subsystem._primaryCtrlIds)
        secondaryGuides = self.guideLayerDef.findGuides(
            *self.subsystem._secondaryCtrlIds
        )

        for guide in primaryGuides:
            railId = self.subsystem.guideRailId(guide.id)
            scale, _ = guide.mirrorScaleVector()
            srtName = self.namingConfig.resolve(
                "controlName",
                {
                    "componentName": self.compName,
                    "side": self.compSide,
                    "id": guide.id,
                    "type": "srt",
                },
            )
            kwargs = dict(
                id=guide.id,
                translate=guide.translate,
                rotate=guide.rotate,
                scale=scale,
                parent=self.ctrlHrc,
                rotateOrder=guide.rotateOrder,
                shape=guide.shape,
                selectionChildHighlighting=self.component.configuration.selectionChildHighlighting,
                srts=[{"id": guide.id, "name": srtName}],
            )
            ctrl = self.rigLayer.createControl(**kwargs)
            self.controls[guide.id] = ctrl
            transform = zapi.createDag(
                self.namingConfig.resolve(
                    "object",
                    {
                        "componentName": self.compName,
                        "side": self.compSide,
                        "section": railId,
                        "type": "nurbsCurve",
                    },
                ),
                "transform",
            )
            transform.setParent(self.ctrlHrc)
            transform.setTranslation(guide.translate, zapi.kWorldSpace)
            # create the rail curves
            curves.createCurveShape(
                transform.object(),
                self.guideLayerDef.guide(railId).shape,
                space=zapi.kWorldSpace,
            )
            self.rails[railId] = transform
            self.rigLayer.addTaggedNode(transform, railId)

        tangentIdsPairs = list(general.chunks(self._tangentCtrlIds, 2))
        for index, guide in enumerate(secondaryGuides):
            parent = self.ctrlHrc
            if index == 1:
                parent = self.controls[secondaryGuides[index - 1].id]
            srtName = self.namingConfig.resolve(
                "controlName",
                {
                    "componentName": self.compName,
                    "side": self.compSide,
                    "id": guide.id,
                    "type": "srt",
                },
            )
            scale, _ = guide.mirrorScaleVector()
            control = self.rigLayer.createControl(
                id=guide.id,
                translate=guide.translate,
                rotate=guide.rotate,
                scale=scale,
                parent=parent,
                rotateOrder=guide.rotateOrder,
                shape=guide.shape,
                selectionChildHighlighting=self.component.configuration.selectionChildHighlighting,
                srts=[{"id": guide.id, "name": srtName}],
            )
            self.controls[guide.id] = control
            if index == 0:
                continue
            # create tangent controls
            tangentIds = tangentIdsPairs[index - 1]
            inGuide = self.guideLayerDef.guide(tangentIds[0])

            inControl = self.rigLayer.createControl(
                id=tangentIds[0],
                translate=inGuide.translate,
                rotate=inGuide.rotate,
                scale=inGuide.mirrorScaleVector()[0],
                parent=control,
                rotateOrder=inGuide.rotateOrder,
                shape=inGuide.shape,
                selectionChildHighlighting=self.component.configuration.selectionChildHighlighting,
            )
            self.controls[inGuide.id] = inControl
            if index != len(secondaryGuides) - 1:
                outGuide = self.guideLayerDef.guide(tangentIds[1])
                outControl = self.rigLayer.createControl(
                    id=tangentIds[1],
                    translate=outGuide.translate,
                    rotate=outGuide.rotate,
                    scale=outGuide.mirrorScaleVector()[0],
                    parent=control,
                    rotateOrder=outGuide.rotateOrder,
                    shape=outGuide.shape,
                    selectionChildHighlighting=self.component.configuration.selectionChildHighlighting,
                )
                self.controls[outGuide.id] = outControl

    def _createRailSystem(self):
        railGraphData = self.component.configuration.graphRegistry().graph(graphconstants.kBrowRail)
        midRailGraphData = self.component.configuration.graphRegistry().graph(graphconstants.kBrowRailMid)
        name = str(railGraphData.name)
        extras = []
        primaryGuides = [self.guideLayerDef.guide(guideId) for guideId in self.subsystem._primaryCtrlIds]
        primaryControls = [self.controls[guideId] for guideId in self.subsystem._primaryCtrlIds]
        _, differentiator = self.subsystem.differentiatorExtraNode(self.subsystem.component.deformLayer())
        differentiatorRailAttrs = ("primaryInnerRail",
                                   "primaryMidRail",
                                   "primaryOuterRail")
        differentiatorXAttrs = ("primaryInnerX",
                                "primaryMidX",
                                "primaryOuterX")

        for index, primaryGuide in enumerate(primaryGuides):
            primaryGuideId = primaryGuide.id
            primaryCtrl = primaryControls[index]
            railGuideId = self.subsystem.guideRailId(primaryGuideId)
            if index == 1:
                midRailGraphData.name = name + primaryGuideId
                sceneGraph = self.subsystem.createGraph(
                    self.rigLayer, midRailGraphData, suffix=primaryGuideId
                )

            else:
                railGraphData.name = name + primaryGuideId
                sceneGraph = self.subsystem.createGraph(
                    self.rigLayer, railGraphData, suffix=primaryGuideId
                )
            shapeNode = self.rails[railGuideId].shapes()[0]

            self.railGraphs.append(sceneGraph)
            self.rails[railGuideId].template.set(1)
            self.rails[railGuideId].hide()
            secondaryGuideId = self.subsystem.guideSecondaryCtrlId(
                index if index == 0 else index + 1
            )
            secondaryControl = self.controls[secondaryGuideId]
            secondaryGuide = self.guideLayerDef.guide(secondaryGuideId)
            primaryAimVector = primaryGuide.aimVector()
            primaryUpVector = primaryGuide.upVector()
            primaryScale, primaryIsMirrored = primaryGuide.mirrorScaleVector(
                mirrorAxisIndex=mayamath.primaryAxisIndexFromVector(primaryAimVector)
            )
            originalAimVector = secondaryGuide.aimVector()  # type: zapi.Vector

            if primaryIsMirrored:
                originalAimVector *= -1
            upVector = secondaryGuide.upVector()  # type: zapi.Vector
            perpendicularIndex, _ = mayamath.perpendicularAxisFromAlignVectors(
                originalAimVector, upVector
            )
            mfn = shapeNode.mfn()
            ctrlPoint, param = mfn.closestPoint(
                zapi.Point(secondaryControl.translation(zapi.kWorldSpace)),
                space=zapi.kWorldSpace,
            )

            # flip the inputTranslation to handle neg scale
            if primaryIsMirrored:
                inverseScale = zapi.createDG(
                    self.namingConfig.resolve(
                        "object",
                        {
                            "componentName": self.compName,
                            "side": self.compSide,
                            "section": railGuideId + "invertT",
                            "type": "multiplyDivide",
                        },
                    ),
                    "multiplyDivide",
                )
                primaryCtrl.attribute("translate").connect(inverseScale.input1)
                inverseScale.input2.set(primaryScale)
                inputTranslate = inverseScale.output
                extras.append(inverseScale)
            else:
                inputTranslate = primaryCtrl.attribute("translate")

            secondarySrt = secondaryControl.srt()
            primarySrt = primaryCtrl.srt()
            secondaryOriginalWorldMatrix = secondaryControl.worldMatrix()
            primaryOriginalWorldMatrix = primaryCtrl.worldMatrix()
            minGuideId, maxGuideId = self.subsystem.guideMinMaxCtrlIds(primaryGuideId)
            minGuide, maxGuide = self.guideLayerDef.findGuides(minGuideId, maxGuideId)
            minLength = (primaryGuide.translate - minGuide.translate).length()
            maxLength = (primaryGuide.translate - maxGuide.translate).length()

            sdk = sceneGraph.node("animCurve")
            _updateRailSdk(
                sdk,
                curves.parametricSpaceFromParametricLength(shapeNode.object(), param),
                minLength,
                maxLength,
            )
            parentInverseMatrixPlug = self.ctrlHrc.worldInverseMatrixPlug()
            motionPathNode = sceneGraph.node("railPos")
            geoAttr = motionPathNode.attribute("geometryPath")
            shapeNode.attribute("worldSpace")[0].connect(geoAttr)
            motionPathNode.fractionMode.set(True)
            sceneGraph.connectToInput(
                "masterControlTranslate", self._masterControl.translate
            )
            sceneGraph.connectToInput("primaryControlTranslate", inputTranslate)
            totalInput = sceneGraph.node("primaryTranslateInvert").attribute("input1")

            sceneGraph.connectToInput(
                "primaryControlRotate", primaryCtrl.attribute("rotate")
            )
            sceneGraph.connectToInput(
                "primaryControlScale", primaryCtrl.attribute("scale")
            )
            sceneGraph.connectToInput(
                "primaryControlWorldMatrix", primaryCtrl.worldMatrixPlug()
            )
            sceneGraph.connectToInput(
                "parentWorldInverseMtx", parentInverseMatrixPlug
            )
            sceneGraph.connectToInput(
                "masterControlWorldMtx", self._masterControl.worldMatrixPlug()
            )
            sceneGraph.connectToInput(
                "motionWorldUpMatrix", self.ctrlHrc.worldMatrixPlug()
            )
            inputTranslate[0].connect(totalInput[0])
            inputTranslate[2].connect(totalInput[2])

            primaryControlLocalOffsetOutputValue = (
                    secondaryOriginalWorldMatrix
                    * self._masterControl.worldInverseMatrixPlug().value()
            )
            # reset the main upVector for the offset to zero making it flush with the primary guide
            # this removes a small offset that occurs when using the mainRailTx
            primaryControlLocalOffsetOutputValue[
                12 + mayamath.primaryAxisIndexFromVector(primaryUpVector)
                ] = 0.0
            sceneGraph.setInputAttr(
                "primaryToControlOffsetMatrix", primaryControlLocalOffsetOutputValue
            )
            sceneGraph.setInputAttr("motionWorldUpType", 2)  # objectRotationUp
            sceneGraph.setInputAttr(
                "motionFrontAxis", mayamath.primaryAxisIndexFromVector(upVector)
            )
            sceneGraph.setInputAttr(
                "motionWorldUpVector", primaryAimVector
            )
            sceneGraph.setInputAttr("motionUpAxis", perpendicularIndex)
            upVectorIsNegative = mayamath.isVectorNegative(upVector)
            sceneGraph.setInputAttr("motionInverseFront", upVectorIsNegative)
            sceneGraph.setInputAttr("motionInverseUp", upVectorIsNegative)
            railWorldOut = sceneGraph.node("railWorldOut").outputMatrix.value().inverse()
            sceneGraph.setInputAttr(
                "controlOffsetMatrix", secondaryOriginalWorldMatrix * railWorldOut
            )
            # flip local translation to alignment difference
            translateMultiplier, rotateMult = _solveLocalTranslation(
                index,
                originalAimVector,
                secondaryGuide,
            )

            sceneGraph.setInputAttr("primaryTranslateMult", translateMultiplier)
            sceneGraph.setInputAttr("primaryRotateMult", rotateMult)
            # to not fuck with tangent controls which are children
            children = []
            for child in secondaryControl.children(nodeTypes=(zapi.kTransform,)):
                child.setParent(None)
                children.append(child)
            sceneGraph.connectFromOutput(
                "localMatrix",
                [secondarySrt.attribute("offsetParentMatrix")]
            )
            if index == 1:
                self._createMidControlAuto(
                    primaryGuideId, primaryOriginalWorldMatrix, secondaryOriginalWorldMatrix,
                    primaryAimVector, primaryUpVector,
                    primaryControls[index - 1], primaryControls[index + 1], self._masterControl,
                    parentInverseMatrixPlug, sceneGraph.inputAttr("midPointOffset")
                )

                sceneGraph.connectFromOutput(
                    "primaryLocalMatrix", [primarySrt.offsetParentMatrix]
                )
            else:
                sceneGraph.connectFromOutput(
                    "primaryLocalMatrix", [primarySrt.offsetParentMatrix]
                )
            diffRailAttr = differentiator.attribute(differentiatorRailAttrs[index])
            diffXAttr = differentiator.attribute(differentiatorXAttrs[index])

            sceneGraph.connectFromOutput("railUValue", [diffRailAttr])
            primaryCtrl.attribute("translateX").connect(diffXAttr)
            cmds.xform(
                primarySrt.fullPathName(),
                absolute=True,
                matrix=list(primaryOriginalWorldMatrix),
                worldSpace=True,
            )
            cmds.xform(
                secondarySrt.fullPathName(),
                absolute=True,
                matrix=list(secondaryOriginalWorldMatrix),
                worldSpace=True,
            )
            primarySrt.resetTransform(translate=False, rotate=False, scale=True)
            secondarySrt.resetTransform(translate=False, rotate=False, scale=True)
            secondaryControl.resetTransform()
            primaryCtrl.resetTransform()
            for child in children:
                child.setParent(secondaryControl)

        self.rigLayer.addExtraNodes(extras)

    def _createMidControlAuto(
            self, guideId, controlWorldMatrix, secondaryWorldMatrix, aimVector, upVector,
            innerPrimary, outerPrimary, railsMain, parentOutput, railGraphInput
    ):
        """

        :param guideId:
        :type guideId: str
        :param innerPrimary:
        :type innerPrimary: :class:`api.ControlNode`
        :param outerPrimary:
        :type outerPrimary:  :class:`api.ControlNode`
        :param railsMain:
        :type railsMain: :class:`api.ControlNode`
        :param parentOutput:
        :type parentOutput: :class:`zapi.Plug`
        :return:
        :rtype: :class:`zapi.Plug`
        """

        railGraphData = self.component.configuration.graphRegistry().graph(
            self.midPointNoRotGraphName
        )

        sceneGraph = self.subsystem.createGraph(
            self.rigLayer, railGraphData, suffix=guideId
        )
        sceneGraph.connectToInput(
            "innerControlLocalMatrix", innerPrimary.attribute("matrix")
        )
        sceneGraph.connectToInput(
            "outerControlLocalMatrix", outerPrimary.attribute("matrix")
        )
        sceneGraph.connectToInput(
            "railsMainLocalMatrix", railsMain.attribute("matrix")
        )

        sceneGraph.setInputAttr("blendWeight", 0.5)
        sceneGraph.setInputAttr("blendSR", 0)

        sceneGraph.connectFromOutput("outputMatrix", railGraphInput)

    def _createAimSystem(self):

        outerCtrlId = self.subsystem.guideSecondaryCtrlId(-1)
        midCtrlId = self.subsystem.guideSecondaryCtrlId(2)
        tweakerCtrlId = self.subsystem.guideSecondaryCtrlId(1)
        innerCtrlId = self.subsystem.guideSecondaryCtrlId(0)
        outerCtrl = self.controls[outerCtrlId]
        midCtrl = self.controls[midCtrlId]
        innerCtrl = self.controls[innerCtrlId]
        tweakerCtrl = self.controls[tweakerCtrlId]
        tweakerInTangentCtrl = self.controls[self._tangentCtrlIds[0]]
        tweakerOutTangentCtrl = self.controls[self._tangentCtrlIds[1]]
        midInTangentCtrl = self.controls[self._tangentCtrlIds[2]]
        midOutTangentCtrl = self.controls[self._tangentCtrlIds[3]]
        outerInTangentCtrl = self.controls[self._tangentCtrlIds[-1]]

        self._createTweakerCVSetup(
            self.controls[self.subsystem._primaryCtrlIds[0]],
            innerCtrl,
            tweakerInTangentCtrl,
            tweakerCtrl,
            tweakerOutTangentCtrl,
            midCtrl,
        )
        self._createMidRotationSetup(
            innerCtrl,
            midInTangentCtrl,
            midCtrl,
            midOutTangentCtrl,
            outerCtrl,
            midCtrlId,
            primaryCtrl=self.controls[self.subsystem._primaryCtrlIds[1]],
        )
        self._createOuterRotationSetup(
            outerCtrl,
            outerInTangentCtrl,
            outerCtrlId,
            midCtrl,
            primaryCtrl=self.controls[self.subsystem._primaryCtrlIds[-1]],
        )

    def _createTweakerCVSetup(
            self,
            primaryCtrl,
            innerCtrl,
            inTangentCtrl,
            tweakerCtrl,
            outTangentCtrl,
            midCtrl,
    ):
        """
        :param innerCtrl:
        :type innerCtrl: :class:`api.ControlNode`
        :param tweakerCtrl:
        :type tweakerCtrl: :class:`api.ControlNode`
        :return:
        :rtype:
        """

        tweakerSrt = tweakerCtrl.srt()
        innerCtrlId = innerCtrl.id()
        controlPanel = self.rigLayer.controlPanel()
        ctrlGuide = self.guideLayerDef.guide(innerCtrlId)
        aimVector = ctrlGuide.aimVector()
        currentWorldMatrix = tweakerCtrl.worldMatrix()
        inTangentWorldMatrix = inTangentCtrl.worldMatrix()
        outTangentWorldMatrix = outTangentCtrl.worldMatrix()
        graphData = self.component.configuration.graphRegistry().graph(
            graphconstants.kBrowInnerCtrlOut
        )
        graph = self.subsystem.createGraph(self.rigLayer, graphData, suffix=innerCtrlId)
        graph.connectToInput("ctrlLocalMatrix", innerCtrl.attribute("matrix"))
        graph.connectToInput(
            "ctrlWorldInvMatrix", innerCtrl.attribute("worldInverseMatrix")[0]
        )
        graph.connectToInput("midCtrlWorldMatrix", midCtrl.worldMatrixPlug())
        graph.connectToInput("ctrlWorldMatrix", innerCtrl.worldMatrixPlug())
        graph.connectToInput("primaryLocalMatrix", primaryCtrl.attribute("matrix"))
        graph.setInputAttr("aimVector", aimVector)
        graph.setInputAttr("upVector", ctrlGuide.upVector())
        graph.setInputAttr("tweakerAimMode", 1)  # aimMode

        graph.connectFromOutput("tweakerLocalMatrix", [tweakerSrt.offsetParentMatrix])
        tweakerSrt.resetTransform()
        cmds.xform(
            tweakerCtrl.fullPathName(),
            absolute=True,
            matrix=list(currentWorldMatrix),
            worldSpace=True,
        )
        tweakerCtrl.resetTransformToOffsetParent()
        parentInv = tweakerCtrl.worldInverseMatrixPlug().value()
        _setupTangentMultiplier(
            controlPanel.attribute("innerTweakerTangent"),
            inTangentCtrl,
            inTangentWorldMatrix * parentInv,
            self.namingConfig,
            self.compName,
            self.compSide,
            mayamath.primaryAxisIndexFromVector(aimVector),
        )
        _setupTangentMultiplier(
            controlPanel.attribute("innerTweakerTangent"),
            outTangentCtrl,
            outTangentWorldMatrix * parentInv,
            self.namingConfig,
            self.compName,
            self.compSide,
            mayamath.primaryAxisIndexFromVector(aimVector),
        )
        inTangentCtrl.resetTransform()
        outTangentCtrl.resetTransform()
        sectionNames = ("innerCvPos", "tweakerInTangentCvPos", "tweakerCvPos")
        indices = (0, 2, 3)
        outputComposes = []
        for index, attr in enumerate(
                (
                        innerCtrl.worldMatrixPlug(),
                        inTangentCtrl.worldMatrixPlug(),
                        tweakerCtrl.worldMatrixPlug(),
                )
        ):
            outputCompose = _attachMatrixPlugToCv(
                self.namingConfig.resolve(
                    "object",
                    {
                        "componentName": self.compName,
                        "side": self.compSide,
                        "section": sectionNames[index],
                        "type": "decomposeMatrix",
                    },
                ),
                self.outputCurveShapes[0],
                attr,
                indices[index],
            )
            outputComposes.append(outputCompose)
        # inner curve cv 1 requires a small offset to ensure that motion paths correct evaluate rotations
        # along curve otherwise constant flipping occurs. to handle this we offset the ctrls worldMatrix by the
        # cv rest pose and multiply together
        positions = self.outputCurveShapes[0].cvPositions(zapi.kWorldSpace)
        offsetTrans = zapi.Vector(positions[1]) - innerCtrl.translation(
            zapi.kWorldSpace
        )
        offsetMatrix = zapi.Matrix(
            (
                1,
                0,
                0,
                0,
                0,
                1,
                0,
                0,
                0,
                0,
                1,
                0,
                offsetTrans[0],
                offsetTrans[1],
                offsetTrans[2],
                1,
            )
        )
        matrixN = zapi.createDG(
            self.namingConfig.resolve(
                "object",
                {
                    "componentName": self.compName,
                    "side": self.compSide,
                    "section": "innerTangentCvPos",
                    "type": "multMatrix",
                },
            ),
            "multMatrix",
        )
        offsetDecomp = zapi.createDG(
            self.namingConfig.resolve(
                "object",
                {
                    "componentName": self.compName,
                    "side": self.compSide,
                    "section": "innerTangentCvPos",
                    "type": "decomposeMatrix",
                },
            ),
            "decomposeMatrix",
        )
        matrixN.matrixIn[0].set(offsetMatrix)
        innerCtrl.worldMatrixPlug().connect(matrixN.matrixIn[1])
        matrixN.matrixSum.connect(offsetDecomp.inputMatrix)
        offsetDecomp.outputTranslate.connect(self.outputCurveShapes[0].controlPoints[1])
        self.rigLayer.addExtraNodes((matrixN, offsetDecomp))

        sectionNames = (
            "tweakerCvPos",
            "tweakerOutTangentCvPos",
        )
        for index, attr in enumerate(
                (tweakerCtrl.worldMatrixPlug(), outTangentCtrl.worldMatrixPlug())
        ):
            _attachMatrixPlugToCv(
                self.namingConfig.resolve(
                    "object",
                    {
                        "componentName": self.compName,
                        "side": self.compSide,
                        "section": sectionNames[index],
                        "type": "decomposeMatrix",
                    },
                ),
                self.outputCurveShapes[1],
                attr,
                index,
            )

    def _createMidRotationSetup(
            self,
            innerCtrl,
            inTangentCtrl,
            midCtrl,
            outTangentCtrl,
            outerCtrl,
            midCtrlId,
            primaryCtrl,
    ):
        controlPanel = self.rigLayer.controlPanel()
        midGuide = self.guideLayerDef.guide(midCtrlId)
        graphData = self.component.configuration.graphRegistry().graph(graphconstants.kBrowMidCtrlOut)
        graph = self.subsystem.createGraph(self.rigLayer, graphData, suffix=midCtrlId)
        graph.connectToInput("startWorldMatrix", innerCtrl.worldMatrixPlug())
        graph.connectToInput("targetWorldMatrix", outerCtrl.worldMatrixPlug())
        graph.connectToInput("controlLocalMatrix", midCtrl.attribute("matrix"))
        graph.connectToInput("primaryLocalMatrix", primaryCtrl.attribute("matrix"))
        graph.connectToInput("parentWorldMatrix", self.ctrlHrc.worldMatrixPlug())
        tangentMult = controlPanel.attribute("midTangent")
        # compute the in tangent offset matrix
        inTangentMat = inTangentCtrl.worldMatrix()
        outTangentMat = outTangentCtrl.worldMatrix()

        graph.setInputAttr("aimVector", midGuide.aimVector())
        graph.setInputAttr("upVector", midGuide.upVector())
        graph.setInputAttr("aimUpVectorMode", 1)
        graph.connectToInput("tangentMultiplier", tangentMult)
        graph.node("subOne").input1D[1].set(1.0)
        graph.connectToInput(
            "controlInverseWorldMatrix", midCtrl.worldInverseMatrixPlug()
        )
        worldToLocal = graph.node("worldToLocalRot").matrixSum.value()
        parentWorldMat = (worldToLocal * midCtrl.worldMatrix()).inverse()
        graph.setInputAttr("inTangentOffsetMatrix", inTangentMat * parentWorldMat)
        graph.setInputAttr("outTangentOffsetMatrix", outTangentMat * parentWorldMat)
        graph.connectFromOutput(
            "inTangentWorldMatrix", [inTangentCtrl.offsetParentMatrix]
        )
        graph.connectFromOutput(
            "outTangentWorldMatrix", [outTangentCtrl.offsetParentMatrix]
        )
        inTangentCtrl.resetTransform()
        outTangentCtrl.resetTransform()
        sectionNames = ("midInTangentCvPos", "midCvPos", "midOutTangentCvPos")
        # bind the curves to the ctrls
        for index, attr in enumerate(
                (inTangentCtrl.worldMatrixPlug(), midCtrl.worldMatrixPlug())
        ):
            _attachMatrixPlugToCv(
                self.namingConfig.resolve(
                    "object",
                    {
                        "componentName": self.compName,
                        "side": self.compSide,
                        "section": sectionNames[index],
                        "type": "decomposeMatrix",
                    },
                ),
                self.outputCurveShapes[1],
                attr,
                index + 2,
            )
        for index, attr in enumerate(
                (midCtrl.worldMatrixPlug(), outTangentCtrl.worldMatrixPlug())
        ):
            _attachMatrixPlugToCv(
                self.namingConfig.resolve(
                    "object",
                    {
                        "componentName": self.compName,
                        "side": self.compSide,
                        "section": sectionNames[index],
                        "type": "decomposeMatrix",
                    },
                ),
                self.outputCurveShapes[-1],
                attr,
                index,
            )

    def _createOuterRotationSetup(
            self, outerCtrl, outTangentCtrl, outerCtrlId, midCtrl, primaryCtrl
    ):
        tangentMat = outTangentCtrl.worldMatrix()
        graphData = self.component.configuration.graphRegistry().graph(
            graphconstants.kBrowOuterCtrlOut
        )

        tangentGuide = self.guideLayerDef.guide(midCtrl.id())
        tangentMult = self.rigLayer.controlPanel().attribute("outerTangent")
        graph = self.subsystem.createGraph(self.rigLayer, graphData, suffix=outerCtrlId)
        graph.connectToInput("ctrlWorldMatrix", outerCtrl.worldMatrixPlug())
        graph.connectToInput("startWorldMatrix", outerCtrl.worldMatrixPlug())
        graph.connectToInput("targetWorldMatrix", midCtrl.worldMatrixPlug())
        graph.connectToInput("controlLocalMatrix", outerCtrl.attribute("matrix"))
        graph.connectToInput(
            "primaryControlLocalMatrix", primaryCtrl.attribute("matrix")
        )
        graph.connectToInput("tangentMultiplier", tangentMult)
        graph.node("subOne").input1D[1].set(1.0)
        aimVector = tangentGuide.aimVector() * -1.0
        upVector = tangentGuide.upVector()
        perpend = mayamath.perpendicularAxisFromAlignVectors(aimVector, upVector)[0]

        graph.connectToInput("parentWorldMatrix", outerCtrl.srt().worldMatrixPlug())
        graph.setInputAttr("aimVector", aimVector)
        graph.setInputAttr("upVector", mayamath.AXIS_VECTOR_BY_IDX[perpend])
        graph.setInputAttr("aimUpVectorMode", 1)
        offsetMatrix = (
                tangentMat * graph.node("controlLocalOut").matrixSum.value().inverse()
        )
        graph.setInputAttr("tangentOffsetMatrix", offsetMatrix)
        graph.connectToInput(
            "controlInverseWorldMatrix", outerCtrl.worldInverseMatrixPlug()
        )
        graph.connectFromOutput(
            "tangentWorldMatrix", [outTangentCtrl.offsetParentMatrix]
        )

        outTangentCtrl.resetTransform()
        extras = []
        for attr, index, name in zip(
                (outTangentCtrl.worldMatrixPlug(), outerCtrl.worldMatrixPlug()),
                (2, 3),
                ("outerCvPos", "outerTangentCvPos"),
        ):
            extras.append(
                _attachMatrixPlugToCv(
                    self.namingConfig.resolve(
                        "object",
                        {
                            "componentName": self.compName,
                            "side": self.compSide,
                            "section": name,
                            "type": "decomposeMatrix",
                        },
                    ),
                    self.outputCurveShapes[-1],
                    attr,
                    index,
                )
            )

        self.rigLayer.addExtraNodes(extras)

    def _bindJointsToCurve(self):
        graphRegistry = self.subsystem.component.configuration.graphRegistry()
        guideLayerDef = self.subsystem.component.definition.guideLayer
        curvefollowValue = guideLayerDef.guideSetting("jointRotationFollowsCurve").value
        mainCtrlScaleDecomp = zapi.createDG(
            name=self.namingConfig.resolve(
                "object",
                {
                    "componentName": self.compName,
                    "side": self.compSide,
                    "section": self.subsystem.railsMainId + "_aimTrsWorldScale",
                    "type": "decomposeMatrix",
                },
            ),
            nodeType="decomposeMatrix",
        )
        self.controls[self.subsystem.railsMainId].worldMatrixPlug().connect(
            mainCtrlScaleDecomp.inputMatrix
        )
        deformLayer = self.component.deformLayer()
        bindJntIds = self.subsystem.guideJointIds()
        jnts = deformLayer.findJoints(*bindJntIds)
        guideDefs = {i.id: i for i in guideLayerDef.findGuides(*bindJntIds)}

        parentSpaceNodeWorldPlug = self.ctrlHrc.worldMatrixPlug()
        parentSpaceNodeWorldInvPlug = self.ctrlHrc.worldInverseMatrixPlug()
        extras = []
        # rail graph indices which a jnt will have it's rotation influenced by
        railGraphIndexGroups = ((0, 2), (0, 2), (2, 3))
        matched = _matchCurveToNodes(self.outputCurveShapes, jnts)
        firstSecondCrvValues = list(zoomath.lerpCount(0.0, 1.0, len(matched[0]) + len(matched[1])))
        # note the first and second curve rail rot blend is between 0.0-1.0 instead of per curve
        for crvIndex, (crv, outJoints) in enumerate(zip(self.outputCurveShapes, matched)):
            railCurveIndices = railGraphIndexGroups[crvIndex]
            startNode = self.controls[self.subsystem.guideSecondaryCtrlId(railCurveIndices[0])]
            endNode = self.controls[self.subsystem.guideSecondaryCtrlId(railCurveIndices[1])]
            values = firstSecondCrvValues[:len(matched[0])]
            if crvIndex == 1:
                values = firstSecondCrvValues[len(matched[0]):]
            for index, outJoint in enumerate(outJoints):
                # recalculate the param value for the curve section
                jntId = outJoint.id()
                guideDef = guideDefs[jntId]
                _, paramValue = crv.mfn().closestPoint(
                    zapi.Point(guideDef.translate), space=zapi.kWorldSpace
                )
                if crvIndex == 2:
                    paramValueBlend = curves.parametricSpaceFromParametricLength(
                        crv.object(), paramValue
                    )
                else:
                    paramValueBlend = values[index]
                aimVector = guideDef.aimVector()
                upVector = guideDef.upVector()
                prep, _ = mayamath.perpendicularAxisFromAlignVectors(aimVector, upVector)
                jointGraph = graphRegistry.graph(self.jointRailOutGraphName)
                jointGraph.name += jntId
                sceneGraph = self.subsystem.createGraph(
                    self.rigLayer, namedGraphData=jointGraph, suffix=jntId
                )
                motionPath = sceneGraph.node("motionPath")
                motionPath.fractionMode.set(True)
                railRotNode = sceneGraph.node("quatToEuler1")
                primaryIndex = mayamath.primaryAxisIndexFromVector(aimVector)
                upIndex = mayamath.primaryAxisIndexFromVector(upVector)
                twistAttr = railRotNode.outputRotate[primaryIndex]
                # to grab rotation(if needed) and scale from the parent
                parentDecomp = zapi.createDG(self.namingConfig.resolve("object", {
                    "componentName": self.compName,
                    "side": self.compSide,
                    "section": jntId + "_parentRot",
                    "type": "decomposeMatrix"
                }), "decomposeMatrix")
                worldIn = sceneGraph.node("worldIn")
                parentSpaceNodeWorldPlug.connect(parentDecomp.inputMatrix)
                if curvefollowValue:
                    motionPath.follow.set(1)
                    motionPath.attribute("rotate").connect(
                        worldIn.inputRotate
                    )
                    # we want the motionpath to also be affected by the rail twist blend
                    twistAttr.connect(motionPath.frontTwist)
                else:
                    worldIn.inputRotate.disconnectAll()

                    additiveRot = zapi.createDG(self.namingConfig.resolve("object", {
                        "componentName": self.compName,
                        "side": self.compSide,
                        "section": jntId + "_parentRotAdd",
                        "type": zapi.kAddDoubleLinearName
                    }), zapi.kAddDoubleLinearName)
                    invertMult = zapi.createDG(self.namingConfig.resolve("object", {
                        "componentName": self.compName,
                        "side": self.compSide,
                        "section": jntId + "_parentRotInvert",
                        "type": zapi.kMultDoubleLinearName
                    }), zapi.kMultDoubleLinearName)
                    twistAttr.connect(invertMult.input1)
                    parentDecomp.outputRotate[primaryIndex].connect(additiveRot.input2)
                    additiveRot.output.connect(sceneGraph.node("worldIn").inputRotate[primaryIndex])
                    invertMult.input2.set(-1 if mayamath.isVectorNegative(upVector) else 1)
                    invertMult.output.connect(additiveRot.input1)

                    parentDecomp.outputRotate[upIndex].connect(worldIn.inputRotate[upIndex])
                    parentDecomp.outputRotate[prep].connect(worldIn.inputRotate[prep])
                    extras.append(additiveRot)
                    extras.append(invertMult)
                parentDecomp.outputScale.connect(worldIn.inputScale)
                parentDecomp.outputShear.connect(worldIn.inputShear)

                sceneGraph.connectToInput(
                    "rotationDriverAWorldMatrix",
                    startNode.worldMatrixPlug(),
                )
                sceneGraph.connectToInput(
                    "rotationDriverBWorldMatrix", endNode.worldMatrixPlug()
                )
                sceneGraph.connectToInput("parentWorldMatrix", parentSpaceNodeWorldPlug)
                sceneGraph.connectToInput(
                    "parentWorldInverseMatrix", parentSpaceNodeWorldInvPlug
                )
                sceneGraph.setInputAttr("motionUValue",
                                        zoomath.clamp(curves.parametricSpaceFromParametricLength(crv.object(), paramValue), 0.0, 1.0))
                sceneGraph.setInputAttr("rotationOutBlendWeight", paramValueBlend)
                sceneGraph.setInputAttr("rotationOutTranslateBlend", 0)
                sceneGraph.setInputAttr("rotationOutScaleBlend", 0)

                sceneGraph.setInputAttr("rotationDriverMultVec", upVector)
                sceneGraph.setInputAttr("motionWorldUpType", 2)  # objectRotationUp
                sceneGraph.setInputAttr(
                    "motionWorldUpVector", mayamath.AXIS_VECTOR_BY_IDX[prep]
                )
                sceneGraph.connectToInput(
                    "motionWorldUpMatrix", self.ctrlHrc.worldMatrixPlug()
                )
                sceneGraph.setInputAttr(
                    "motionFrontAxis", primaryIndex
                )
                sceneGraph.setInputAttr(
                    "motionUpAxis", mayamath.primaryAxisIndexFromVector(upVector)
                )
                sceneGraph.setInputAttr(
                    "motionInverseFront", mayamath.isVectorNegative(aimVector)
                )
                sceneGraph.setInputAttr(
                    "motionInverseUp", mayamath.isVectorNegative(upVector)
                )

                crv.worldSpace[0].connect(motionPath.geometryPath)
                extras.extend(
                    _bindAimToCurve(
                        self.subsystem,
                        jointId=outJoint.id(),
                        outJoint=outJoint,
                        driverMatrixPlug=sceneGraph.outputAttr("worldMatrix"),
                    )
                )
        self.rigLayer.addExtraNodes(extras)


def _createGuideParamSettings(guideLayerDef, paramMultipliers, idGenerator):
    # creates definition settings for controlGuides and joints

    for i, param in enumerate(paramMultipliers):
        attrName = idGenerator(i)
        setting = definition.AttributeDefinition(
            name=attrName,
            Type=zapi.attrtypes.kMFnNumericFloat,
            value=param,
            default=param,
            keyable=False,
            channelBox=True,
            min=0.0,
            max=1.0,
        )
        guideLayerDef.addGuideSetting(setting)


def _generateGuideCurve(curveId, positions, ctrlCount):
    curve = zapi.nurbsCurveFromPoints(
        curveId, positions, shapeData={"form": 1, "degree": 3}
    )[0]
    curve.rename(curveId)
    cmds.rebuildCurve(
        curve.fullPathName(),
        constructionHistory=False,
        replaceOriginal=True,
        rebuildType=0,
        endKnots=1,
        keepRange=0,
        keepControlPoints=0,
        keepEndPoints=1,
        keepTangents=0,
        spans=ctrlCount - 1,
        degree=3,
        tolerance=0.004,
    )

    return curve


def _bindAimToCurve(subsystem, jointId, outJoint, driverMatrixPlug):
    """

    :param subsystem:
    :type subsystem: :class:`BrowSubsystem`
    """
    jointParent = outJoint.parent()

    graph = subsystem.component.configuration.graphRegistry().graph(graphconstants.kJointConstraint)
    graph.name += jointId
    namingConfig = subsystem.component.namingConfiguration()
    sceneGraph = subsystem.createGraph(
        subsystem.component.rigLayer(), graph, suffix=jointId
    )

    parentMatrix = jointParent.worldMatrixPlug()
    parentInverseMatrix = jointParent.attribute("worldInverseMatrix")[0]
    mOutputMatrix = outJoint.worldMatrix() * driverMatrixPlug.value().inverse()

    jntOrient = zapi.EulerRotation(outJoint.jointOrient.value())
    transform = zapi.TransformationMatrix()
    transform.setRotation(jntOrient)
    sceneGraph.connectToInput("driverWorldMatrix", driverMatrixPlug)
    sceneGraph.connectToInput("jointParentWorldMatrix", parentMatrix)
    sceneGraph.connectToInput("jointParentWorldInverseMatrix", parentInverseMatrix)
    sceneGraph.setInputAttr("drivenJointOrientMatrix", transform.asMatrix())
    sceneGraph.setInputAttr("offsetMatrix", mOutputMatrix)

    rotationOut = zapi.createDG(
        namingConfig.resolve(
            "object",
            {
                "componentName": subsystem.component.name(),
                "side": subsystem.component.side(),
                "section": "rotationOut" + jointId,
                "type": "decomposeMatrix",
            },
        ),
        "decomposeMatrix",
    )
    tsOut = zapi.createDG(
        namingConfig.resolve(
            "object",
            {
                "componentName": subsystem.component.name(),
                "side": subsystem.component.side(),
                "section": "tsOut" + jointId,
                "type": "decomposeMatrix",
            },
        ),
        "decomposeMatrix",
    )
    tsOut.attribute("outputTranslate").connect(outJoint.translate)
    rotationOut.attribute("outputRotate").connect(outJoint.rotate)
    tsOut.attribute("outputScale").connect(outJoint.attribute("scale"))
    sceneGraph.connectFromOutput("rotationMatrix", [rotationOut.inputMatrix])
    sceneGraph.connectFromOutput("translateScaleMatrix", [tsOut.inputMatrix])
    return tsOut, rotationOut


def _bindGuideToCurve(subsystem, guide, curve, param, graph, follow=True):
    """
    :param subsystem:
    :param subsystem: :class:`BrowSubsystem`
    :param guide:
    :type guide: :class:`api.Guide`
    :param curve:
    :type curve: :class:`zapi.NurbsCurve`
    :param param:
    :type param:
    :return:
    :rtype: :class:`api.serialization.NamedDGGraph`
    """
    guideLayer = subsystem.component.guideLayer()
    root = guideLayer.guide("root")
    aimVector = guide.autoAlignAimVector.value()
    upVector = guide.autoAlignUpVector.value()

    sceneGraph = subsystem.createGraph(guideLayer, graph, suffix=guide.id())

    sceneGraph.connectToInput("motionUValue", param)
    sceneGraph.connectToInput("parentWorldMatrix", root.worldMatrixPlug())
    sceneGraph.connectToInput(
        "parentWorldInverseMatrix", root.attribute("worldInverseMatrix")[0]
    )

    sceneGraph.setInputAttr("motionWorldFrontAxis", mayamath.primaryAxisIndexFromVector(aimVector))
    sceneGraph.setInputAttr("motionWorldUpAxis", mayamath.primaryAxisIndexFromVector(upVector))
    sceneGraph.setInputAttr("motionWorldUpVector", upVector)
    sceneGraph.connectToInput("motionWorldUpMatrix", root.worldMatrixPlug())
    sceneGraph.setInputAttr(
        "motionFrontAxis", mayamath.primaryAxisIndexFromVector(aimVector)
    )
    sceneGraph.setInputAttr(
        "motionUpAxis", mayamath.primaryAxisIndexFromVector(upVector)
    )
    sceneGraph.setInputAttr("motionFollow", follow)
    motionPathNode = sceneGraph.node("curvePos")
    sceneGraph.setInputAttr("motionInverseUp", mayamath.isVectorNegative(upVector))
    sceneGraph.setInputAttr("motionInverseFront", mayamath.isVectorNegative(aimVector))
    sceneGraph.setInputAttr("motionWorldUpType", 2)
    if follow:
        motionPathNode.attribute("rotate").connect(sceneGraph.node("aimTrs").inputRotate)
    curve.attribute("worldSpace")[0].connect(motionPathNode.attribute("geometryPath"))
    sceneGraph.connectFromOutput("localMatrix", [guide.offsetParentMatrix])
    guide.resetTransform(scale=False)

    return sceneGraph


def _attachMatrixPlugToCv(name, curveShape, matrixPlug, index):
    comp = zapi.createDG(name, "decomposeMatrix")
    matrixPlug.connect(comp.inputMatrix)
    comp.outputTranslate.connect(curveShape.controlPoints[index])
    return comp


def _matchCurveToNodes(curveShapes, nodes):
    matched = [[], [], []]

    for i in nodes:
        for index, crv in enumerate(curveShapes):
            mfn = crv.mfn()
            point = zapi.Point(i.translation(zapi.kWorldSpace))
            if mfn.isPointOnCurve(point, 0.03, space=zapi.kWorldSpace):
                matched[index].append(i)
                break
            # back up plan, when point is to far away from the curve
            else:
                closestPoint, param = mfn.closestPoint(point, space=zapi.kWorldSpace)
                if param != 1.0 and param != 0.0:
                    matched[index].append(i)
                    break
    return matched


def _createGuideDef(
        guideLayerDef,
        guideId,
        parent,
        ctrlColor,
        position,
        aimVector,
        upVector,
        ctrlScale=DEFAULT_GUIDE_SHAPE_SCALE,
        ctrlRotation=(math.pi * 0.5, 0, 0),
        shape=SECONDARY_GUIDE_SHAPE,
        rotation=(),
        selectionChildHighlighting=False,
        attributes=None,
        ctrlPosition=None
):
    """
    :rtype: :class:`api.Guide`
    """
    attrs = [
        {
            "name": api.constants.MIRROR_BEHAVIOUR_ATTR,
            "value": mayamath.MIRROR_SCALE,
            "Type": zapi.attrtypes.kMFnNumeric3Float,
        },
        {
            "name": api.constants.AUTOALIGNAIMVECTOR_ATTR,
            "value": [1.0, 0.0, 0.0],
            "Type": zapi.attrtypes.kMFnNumeric3Float,
        },
        {
            "name": api.constants.AUTOALIGNUPVECTOR_ATTR,
            "value": upVector,
            "Type": zapi.attrtypes.kMFnNumeric3Float,
        },
    ]
    if attributes:
        attrs.extend(attributes)
    return guideLayerDef.createGuide(
        name="controlGuide",
        pivotShape="locator",
        pivotColor=[0.477, 1, 0.073],
        shape=shape,
        id=guideId,
        parent=parent,
        color=ctrlColor,
        translate=position,
        rotate=rotation,
        scale=DEFAULT_GUIDE_CTRL_SCALE,
        selectionChildHighlighting=selectionChildHighlighting,
        shapeTransform={
            "translate": ctrlPosition or position,
            "scale": ctrlScale,
            "rotate": ctrlRotation,
        },
        attributes=[
            {
                "name": api.constants.MIRROR_BEHAVIOUR_ATTR,
                "value": mayamath.MIRROR_SCALE,
                "Type": zapi.attrtypes.kMFnNumeric3Float,
            },
            {
                "name": api.constants.AUTOALIGNAIMVECTOR_ATTR,
                "value": list(aimVector),
                "Type": zapi.attrtypes.kMFnNumeric3Float,
            },
            {
                "name": api.constants.AUTOALIGNUPVECTOR_ATTR,
                "value": list(upVector),
                "Type": zapi.attrtypes.kMFnNumeric3Float,
            },
        ],
    )


def _mirrorGuideAlign(
        sourceGuide,
        targetGuide,
        flipAim=False,
        rotMultipier=None,
        constraintAxis=True,
        customAimVector=None,
        customUpVector=None,
):
    transform = sourceGuide.transformationMatrix()
    if customAimVector is not None:
        inAimVector = customAimVector
    else:
        inAimVector = sourceGuide.attribute(
            api.constants.AUTOALIGNAIMVECTOR_ATTR
        ).value()
    if customUpVector is not None:
        inUpVector = customUpVector
    else:
        inUpVector = sourceGuide.attribute(api.constants.AUTOALIGNUPVECTOR_ATTR).value()
    isScaledMirrored = sourceGuide.attribute(api.constants.MIRROR_SCALED_ATTR).value()
    if flipAim and isScaledMirrored:
        inAimVector = inAimVector * -1.0
    rot = mayamath.lookAt(
        sourceGuide.translation(zapi.kWorldSpace),
        targetGuide.translation(zapi.kWorldSpace),
        aimVector=inAimVector,
        upVector=inUpVector,
        worldUpVector=zapi.worldUpAxis(),
        constrainAxis=inUpVector if constraintAxis else zapi.Vector(1, 1, 1),
    )
    if rotMultipier is not None:
        rotMultipierValue = rotMultipier[0]
        if isScaledMirrored:
            rotMultipierValue = rotMultipier[1]
        rot = zapi.EulerRotation(rotMultipierValue).asQuaternion() * rot
    transform.setRotation(rot)
    if isScaledMirrored:
        scale = transform.scale(zapi.kWorldSpace)
        mirrorPlanePlug = sourceGuide.attribute(api.constants.MIRROR_PLANE_ATTR).value()
        mirrorPlaneName = mayamath.MIRROR_AXIS_BY_PLANE_INDEX[mirrorPlanePlug]
        axisIdx, _ = mayamath.perpendicularAxisFromAlignVectors(inAimVector, inUpVector)
        scale[mirrorPlaneName] *= -1.0
        scale[axisIdx] *= -1.0
        transform.setScale(scale, zapi.kWorldSpace)

    return transform.asMatrix()


def _createGuideJoint(guideLayer, parentGuide, namingConfig, compName, compSide):
    jnt = zapi.createDag(
        namingConfig.resolve(
            "object",
            {
                "componentName": compName,
                "side": compSide,
                "section": parentGuide.id() + "Skin",
                "type": "jnt",
            },
        ),
        "joint",
        parent=parentGuide,
    )
    transform = parentGuide.transformationMatrix()
    transform.setScale((1, 1, 1), zapi.kWorldSpace)
    jnt.setWorldMatrix(transform.asMatrix())
    guideLayer.addJoint(jnt, parentGuide.id() + "Skin")
    jnt.hide()
    jnt.setLockStateOnAttributes(["visibility"], True)
    return jnt


def _shiftCurvePoints(curveShape):
    """Rebuilds curve positions in such that curve points are grouped together to fit
    curve tangent.

    :param curveShape:
    :type curveShape:
    :return:
    :rtype:
    """
    mfn = curveShape.shapes()[0].mfn()
    positions = mfn.cvPositions(zapi.kWorldSpace)
    cvPosIndex = 2
    midPointLength = mfn.findLengthFromParam(0.5)
    # skip first and last because they can be maintained
    for param in CTRL_PARAM_POS:
        centerPos = mfn.getPointAtParam(param, space=zapi.kWorldSpace)
        outTangentPos = mfn.getPointAtParam(param * 1.3, space=zapi.kWorldSpace)
        inTangentPos = centerPos + (centerPos - outTangentPos)
        positions[cvPosIndex] = inTangentPos
        positions[cvPosIndex + 1] = centerPos
        positions[cvPosIndex + 2] = outTangentPos
        cvPosIndex += 3
    # modify the last tangent point to be 75% along the curve between midtangent and end
    newLength = midPointLength + ((mfn.length() - midPointLength) * 0.75)
    newPoint = mfn.getPointAtParam(mfn.findParamFromLength(newLength), zapi.kWorldSpace)
    positions[-2] = newPoint

    pos0 = zapi.Vector(positions[0])
    positions[1] = pos0 + ((zapi.Vector(positions[2] - pos0) * 0.1))
    mfn.setCVPositions(positions, zapi.kWorldSpace)
    mfn.updateCurve()  # ensure the view to redraw this curve


def _solveLocalTranslation(loopIndex, aimVector, guide):
    # flip local translation to alignment difference
    aimIsNeg = mayamath.isVectorNegative(aimVector)
    mirrorVec, isMirrored = guide.mirrorScaleVector()
    rotateOut = zapi.Vector(1, 1, 1)
    primaryIndex = mayamath.primaryAxisIndexFromVector(aimVector)

    if loopIndex == 2:  # outer
        if not aimIsNeg:
            mirrorVec *= -1

    # first 2 controls need to flip only the aim vector ie. YZ plane == -X
    else:
        if isMirrored:
            mirrorVec = guide.mirrorScaleVector(mirrorAxisIndex=primaryIndex)[0]
    return mirrorVec, rotateOut


def _updateRailSdk(sdkNode, value, minValue, maxValue):
    sdkNode.addKeysWithTangents(
        [-minValue, 0, maxValue],
        [
            0,
            value,
            1.0,
        ],
        tangentInTypeArray=[
            zapi.kTangentLinear,
            zapi.kTangentLinear,
            zapi.kTangentLinear,
        ],
        tangentOutTypeArray=[
            zapi.kTangentLinear,
            zapi.kTangentLinear,
            zapi.kTangentLinear,
        ],
        convertUnits=False,
        keepExistingKeys=False,
    )


def _setupTangentMultiplier(
        animAttr, outputNode, offsetMatrix, namingConfig, compName, compSide, aimVectorIndex
):
    pma = zapi.createDG(
        namingConfig.resolve(
            "object",
            {
                "componentName": compName,
                "side": compSide,
                "section": "tangentMultiplier",
                "type": "plusMinusAverage",
            },
        ),
        "plusMinusAverage",
    )
    compose = zapi.createDG(
        namingConfig.resolve(
            "object",
            {
                "componentName": compName,
                "side": compSide,
                "section": "tangentMat",
                "type": "composeMatrix",
            },
        ),
        "composeMatrix",
    )
    mult = zapi.createDG(
        namingConfig.resolve(
            "object",
            {
                "componentName": compName,
                "side": compSide,
                "section": "tangentOffset",
                "type": "multMatrix",
            },
        ),
        "multMatrix",
    )
    animAttr.connect(pma.input1D[0])
    pma.input1D[1].set(1.0)
    pma.operation.set(2)
    pma.output1D.connect(compose.inputTranslate[aimVectorIndex])
    compose.outputMatrix.connect(mult.matrixIn[0])
    mult.matrixIn[1].set(offsetMatrix)
    mult.matrixSum.connect(outputNode.offsetParentMatrix)
    return pma, compose, mult
