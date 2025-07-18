import collections
import math
from maya.api import OpenMaya as om2
from maya import cmds
from zoovendor import six
from zoo.libs.hive.base.serialization import graphconstants
from zoo.libs.maya import zapi
from zoo.libs.maya.api import mesh, curves, nodes
from zoo.libs.maya.cmds.shaders import createshadernetwork, shaderutils
from zoo.libs.maya.utils import mayamath
from zoo.libs.utils import zoomath
from zoo.libs.hive import api
from zoo.libs.hive.base import basesubsystem, definition
from zoo.libs.utils import output

META_EXTRA_ATTR = "lips" + api.constants.BS_META_EXTRA_ATTR_PREFIX
MASK_GUIDE_ID = "mouthMask"
UPR_LIP_CURVE_ID = "uprCurve"
LWR_LIP_CURVE_ID = "lwrCurve"
OUTER_L_PRIMARY_CTRL_ID = "outerPrimaryL"
OUTER_R_PRIMARY_CTRL_ID = "outerPrimaryR"
OUTER_L_TERTIARY_CTRL_ID = "outerTertiaryL"
OUTER_R_TERTIARY_CTRL_ID = "outerTertiaryR"
OUTER_L_BIND_ID = "outerLBind"
OUTER_R_BIND_ID = "outerRBind"
UPR_LIP_CTR_ID = "uprCtr"
LWR_LIP_CTR_ID = "lwrCtr"
PRIMARY_GUIDE_SHAPE = "triangle_round"
SECONDARY_GUIDE_SHAPE = "triangle_round"
TERTIARY_GUIDE_SHAPE = "sphere"
UPR_LIP_ROLL_ATTR_NAME = "uprLipRoll"
LWR_LIP_ROLL_ATTR_NAME = "lwrLipRoll"
MAIN_CTRL_ID = "lipsGlobal"
MAIN_CTRL_DRIVER_ID = "primaryCtrlMainDriver"
DEFAULT_GUIDE_CTRL_SCALE = (1.0, 1.0, 1.0)
DEFAULT_GUIDE_SHAPE_SCALE = (0.250, 0.250, 0.250)
DEFAULT_PRIMARY_GUIDE_CTRL_SCALE = (0.250, 0.250, 0.250)
DEFAULT_PRIMARY_GUIDE_SHAPE_SCALE = (0.250, 0.250, 0.250)
DEFAULT_GUIDE_JNT_SCALE = (0.1, 0.1, 0.1)
# ctrl colors for tertiary ctrls
CURVE_COLOR_MAP = {
    UPR_LIP_CURVE_ID: (1.0, 0.182, 0.073),
    LWR_LIP_CURVE_ID: (1.0, 0.350, 0.073)
}
DEFAULT_SECONDARY_CTRL_COLOR = (0.538, 1.0, 0.073)
DEFAULT_PRIMARY_CTRL_GUIDE_ROT_MAP = {
    UPR_LIP_CURVE_ID: (math.pi * -0.5, 0.0, 0.0),
    LWR_LIP_CURVE_ID: (math.pi * 0.5, 0.0, 0.0),
}
CURVE_STARTEND_COLOR = (0.432, 0.223, 1.0)
# skin weights for the lowres curve ctr, LeftCtrl, rightCtrl
LOW_RES_CURVE_SKIN = [
    [0, 0.0, 1.0],  # cv[0]
    [0.2, 0.0, 0.8],  # cv[1]
    [0.8, 0.0, 0.2],  # cv[2]
    [1.0, 0.0, 0.0],  # cv[3]
    [0.8, 0.2, 0.0],  # cv[4]
    [0.2, 0.8, 0.0],  # cv[5]
    [0.0, 1, 0.0],  # cv[6]
]
BIND_JNT_ID_MAP = {
    UPR_LIP_CURVE_ID: "uprBind",
    LWR_LIP_CURVE_ID: "lwrBind"
}
MACRO_CTRL_ID_MAP = {
    UPR_LIP_CURVE_ID: "uprTertiary",
    LWR_LIP_CURVE_ID: "lwrTertiary"
}
SECONDARY_CTRL_ID_MAP = {
    UPR_LIP_CURVE_ID: "uprSecondary",
    LWR_LIP_CURVE_ID: "lwrSecondary"
}
LIPS_ZIP_L_ATTR = "lZip"
LIPS_ZIP_OFFSET_L_ATTR = "lZipFalloff"
LIPS_ZIP_OFFSET_R_ATTR = "rZipFalloff"
LIPS_ZIP_R_ATTR = "rZip"

LIPS_UPR_ZROLL_MULT_ATTR = "uprRollZMultiplier"
LIPS_LWR_ZROLL_MULT_ATTR = "lwrRollZMultiplier"
LIPS_UPR_YROLL_MULT_ATTR = "uprRollYMultiplier"
LIPS_LWR_YROLL_MULT_ATTR = "lwrRollYMultiplier"


class MouthSubsystem(basesubsystem.BaseSubsystem):
    """
    :param component: The component associated with this subsystem.
    :type component: :class:`zoo.libs.hive.base.component.Component`
    """

    def __init__(
            self,
            component
    ):
        super(MouthSubsystem, self).__init__(component)

        self.outerLipCtrlPrefixId = "outer"
        self.jointCountSettingName = "lipJointCount"
        self.ctrlCountSettingName = "lipCtrlCount"

        guideLayer = self.component.definition.guideLayer
        settings = guideLayer.guideSettings(self.jointCountSettingName, self.ctrlCountSettingName)
        self.jointCount = settings[self.jointCountSettingName].value
        self.ctrlCount = settings[self.ctrlCountSettingName].value
        self.jointCount = self.jointCount + 1 if self.jointCount % 2 == 0 else self.jointCount
        self.ctrlCount = self.ctrlCount + 1 if self.ctrlCount % 2 == 0 else self.ctrlCount

    def guidePrimaryCtrlIdForCurve(self, curveId):
        """Generate the primary control ID for a given curve ID.

        :param curveId: str
        :type curveId: The ID of the curve.
        :return: str
        :rtype: The primary control ID for the given curve ID.
        """
        return {
            UPR_LIP_CURVE_ID: UPR_LIP_CTR_ID,
            LWR_LIP_CURVE_ID: LWR_LIP_CTR_ID,
        }[curveId]

    def guideJointIdForCurve(self, curveId, index):
        """Generate the joint ID for a given curve and index.

        :param curveId: str
        :type curveId: The ID of the curve.
        :param index: int
        :type index: The index for the joint ID.
        :return: str
        :rtype: The joint ID for the given curve and index.
        """
        # note ids are split between L/R and center
        suffix = self._idIndexForIndex(index, self.jointCount)

        return BIND_JNT_ID_MAP[curveId] + "{}".format(suffix)

    def guideJntParamPosSettingName(self, curveId, index):
        """Generate the setting name for the joint parameter position for a given curve and index.

        :param curveId: str
        :type curveId: The ID of the curve.
        :param index: int
        :type index: The index for the setting name.
        :return: str
        :rtype: The setting name for the joint parameter position for the given curve and index.
        """
        suffix = self._idIndexForIndex(index, self.jointCount)
        return curveId + "Jnt{}Pos".format(suffix)

    def guideCtrlIdForCurve(self, curveId, index):
        """Generate the control ID for a given curve and index.

        :param curveId: str
        :type curveId: The ID of the curve.
        :param index: int
        :type index: The index for the control ID.
        :return: str
        :rtype: The control ID for the given curve and index.
        """
        suffix = self._idIndexForIndex(index, self.ctrlCount)

        return MACRO_CTRL_ID_MAP[curveId] + "{}".format(suffix)

    def guideCtrlSecondaryIdForCurve(self, curveId, index):
        return SECONDARY_CTRL_ID_MAP[curveId] + ("R", "L")[index]

    def guideCtrlIdsForCurve(self, curveId):
        return [self.guideCtrlIdForCurve(curveId, index) for index in six.moves.range(self.ctrlCount)]

    def guideJointIdsForCurve(self, curveId):
        return [self.guideJointIdForCurve(curveId, index) for index in six.moves.range(self.jointCount)]

    def guideJointIds(self):

        ids = [self.outerLipCtrlPrefixId + "RBind"]
        for curveId in [UPR_LIP_CURVE_ID, LWR_LIP_CURVE_ID]:
            for index in six.moves.range(self.jointCount):
                ids.append(self.guideJointIdForCurve(curveId, index))
        ids.append(self.outerLipCtrlPrefixId + "LBind")
        return ids

    def jointParamNames(self, curveId=None):
        ids = []
        curveIds = [curveId] if curveId else [UPR_LIP_CURVE_ID, LWR_LIP_CURVE_ID]
        for curveId in curveIds:
            for index in six.moves.range(self.jointCount):
                ids.append(self.guideJntParamPosSettingName(curveId, index))
        return ids

    def createGuideCurve(self, meshObject, vertices, curveId):
        self.deleteGuideCurve(curveId)

        topVertsGraph = mesh.constructVerticeGraph(meshObject.dagPath(), vertices)
        topVertexLoops = mesh.sortLoops(topVertsGraph)
        positions = mesh.vertexPositions(
            meshObject.dagPath(), topVertexLoops[0], sortKey="x"
        )
        if len(positions) < 4:
            return False
        curve = _generateGuideCurve(curveId, positions)
        return self.setGuideCurve(curveId, curve, translation=positions[int(len(positions) * 0.5)],
                                  duplicate=False)

    def setGuideCurve(self, curveId, curve, translation=None, duplicate=True):
        guideLayer = self.component.guideLayer()
        self.component.logger.debug("Updating Lip curve: {}".format(curveId))
        newCurve = _updateGuideCurve(curveId, curve, self.ctrlCount, duplicate=duplicate)
        if translation is None:
            positions = newCurve.shapes()[0].cvPositions(zapi.kWorldSpace)
            translation = positions[int(len(positions) * 0.5)]
        # First check if the guide exists and create a one if not.
        # setShapeNode will delete the existing shapeNodes
        curveGuide = guideLayer.guide(curveId)
        if curveGuide is None:
            self.component.logger.debug("Creating lip curve: {}".format(curveId))
            # create the scene guide with no shape then create the shape from the positions
            curveGuide = guideLayer.createGuide(
                id=curveId,
                translate=translation,
                parent="root",
                scale=(0.3, 0.3, 0.3),
                shape="cube",
                pivotShape="sphere_arrow",
            )
        curveGuide.setShapeNode(newCurve)
        newCurve.setParent(guideLayer.rootTransform())
        newCurve.setShapeColour((1.0, 0.897, 0.073), shapeIndex=-1)
        self.component.definition.guideLayer.createGuide(
            **curveGuide.serializeFromScene(
                extraAttributesOnly=True, includeNamespace=False, useShortNames=True
            )
        )
        container = self.component.container()
        if container:
            container.publishNodes([curveGuide, curveGuide.shapeNode()])
        # generate joint params
        self.component.logger.debug("Creating Guide params for: {}".format(curveId))
        self._createGuideParamSettings(
            curveId,
            list(zoomath.lerpCount(0, 1, self.jointCount + 2))[1:-1],
            self.guideJntParamPosSettingName,
        )
        guideLayerDef = self.component.definition.guideLayer
        self._createCurveGuides(guideLayerDef, newCurve, curveId, self.jointCount)
        # recompute orientations to match auto alignment code

        toAlignInfo = {}
        for guide in guideLayerDef.iterGuides(includeRoot=True):
            worldTrans = guide.transformationMatrix()
            toAlignInfo[guide.id] = GuideMapInfo(
                guide.aimVector(),
                guide.upVector(),
                worldTrans.translation(zapi.kWorldSpace),
                worldTrans.scale(zapi.kWorldSpace),
                worldTrans.asMatrix()
            )

        guideIdMap = {i.id: i for i in guideLayerDef.iterGuides(includeRoot=True)}
        curveGuides = [None, None]  #type: zapi.DagNode or None
        if curveId == UPR_LIP_CURVE_ID:
            curveGuides[0] = curveGuide
        else:
            curveGuides[1] = curveGuide

        alignInfo = _gatherGuideAlignData(self, toAlignInfo, curveGuides)
        for outId, outMatrix in alignInfo.items():
            guide = guideIdMap[outId]
            guide.worldMatrix = outMatrix

        self.component.saveDefinition(self.component.definition)
        self.component.rig.buildGuides([self.component])
        return True

    def setSurfaceMask(self, surfaceTransform):
        guideLayer = self.component.guideLayer()
        surfaceMask = guideLayer.guide(MASK_GUIDE_ID)
        if not surfaceMask:
            self.component.logger.error("Missing surface mask guide, was it deleted?")
            return False
        surfaceMask.setPivotShape(api.constants.GUIDE_TYPE_NURBS_SURFACE, surfaceTransform)

        return True

    def deleteGuideCurve(self, curveId):
        """Deletes a guide curve based on the provided curve ID."""
        guideLayer = self.component.guideLayer()
        jntIds = self.guideJointIdsForCurve(curveId)
        ctrlIds = self.guideCtrlIdsForCurve(curveId)
        primaryGuideId = self.guidePrimaryCtrlIdForCurve(curveId)
        ids = [curveId, primaryGuideId] + jntIds + ctrlIds

        if curveId == UPR_LIP_CURVE_ID:
            ids.extend([OUTER_L_TERTIARY_CTRL_ID,
                        OUTER_R_TERTIARY_CTRL_ID,
                        OUTER_L_PRIMARY_CTRL_ID,
                        OUTER_R_PRIMARY_CTRL_ID,
                        self.guideCtrlSecondaryIdForCurve(UPR_LIP_CURVE_ID, 0),
                        self.guideCtrlSecondaryIdForCurve(UPR_LIP_CURVE_ID, 1),
                        self.outerLipCtrlPrefixId + "RBind",
                        self.outerLipCtrlPrefixId + "LBind"
                        ])
        else:
            ids.extend([self.guideCtrlSecondaryIdForCurve(LWR_LIP_CURVE_ID, 0),
                        self.guideCtrlSecondaryIdForCurve(LWR_LIP_CURVE_ID, 1)])

        guides = guideLayer.findGuides(*ids)
        graphRegistry = self.component.configuration.graphRegistry()
        for guide in guides:
            if not guide:
                continue
            offsetParent = guide.attribute("offsetParentMatrix")
            source = offsetParent.source()
            if source:
                source.disconnect(offsetParent)
            guideLayer.deleteNamedGraph("motionPathGuide" + guide.id(), graphRegistry)
        guideLayer.deleteGuides(*ids)
        self.component.definition.guideLayer.deleteGuides(*ids)

    def validateGuides(self, validationInfo):
        """

        :param validationInfo:
        :type validationInfo: :class:`api.ValidationInfo`
        """
        guideLayerDef = self.component.definition.guideLayer

        mask, uprCurve, lwrCurve = guideLayerDef.findGuides(MASK_GUIDE_ID, UPR_LIP_CURVE_ID, LWR_LIP_CURVE_ID)
        message = "\n"
        if not mask:
            validationInfo.status = api.VALIDATION_ERROR
            message += "Missing surface Mask Guide which is Required"
        if not uprCurve:
            if message:
                message += "\n"
            validationInfo.status = api.VALIDATION_ERROR
            message += "Missing upper lip curve guide which is Required"
        if not lwrCurve:
            if message:
                message += "\n"
            validationInfo.status = api.VALIDATION_ERROR
            message += "Missing lower lip curve guide which is Required"
        validationInfo.message = message
        return True

    def setLipDriver(self, drivenId, driverExpression):
        defini = self.component.definition
        existingDriver = None  # type: hiveapi.DriverDef or None
        for driver in defini.drivers:
            if driver.label == drivenId:
                existingDriver = driver
        if existingDriver:
            existingDriver.params = api.DriverMatrixConstParams(
                drivers=[("", driverExpression)],
                driven=api.pathAsDefExpression(("self", "inputLayer", drivenId)),
                maintainOffset=False
            )
        else:
            defini.drivers.append(api.DriverDef("matrixConstraint", drivenId,
                                                params={
                                                    "drivers": [("", driverExpression)],
                                                    "driven": api.pathAsDefExpression(("self", "inputLayer", drivenId)),
                                                    "maintainOffset": False
                                                }))
        self.component.saveDefinition(defini)

    def preUpdateGuideSettings(self, settings):
        """First stage of updating guide settings. Intended to delete anything from.

        :type settings: dict
        :return: Whether to rebuild the guides and whether the post-update operations should be executed
        :rtype: tuple[bool, bool]
        """

        rebuild, runPostUpdate = False, False
        for settingName, value in settings.items():
            if settingName == self.jointCountSettingName:
                value = max(value, 0)
                if self.jointCount == value:
                    rebuild = False
                else:
                    rebuild = self._onGuideJointCountChanged(value)
            elif settingName == self.ctrlCountSettingName:
                value = max(value, 0)
                if value == self.ctrlCount:
                    rebuild = False
                else:
                    rebuild = self._onGuideCtrlCountChanged(value)

        return rebuild, runPostUpdate

    def preAlignGuides(self):
        guides, matrices = [], []
        if not self.active():
            return guides, matrices
        # return guides, matrices
        self.component.logger.debug("AutoAlign lips")
        guideLayer = self.component.guideLayer()
        toAlignInfo = {}
        for guide in guideLayer.iterGuides():
            worldTrans = guide.transformationMatrix()
            toAlignInfo[guide.id()] = GuideMapInfo(guide.aimVector(),
                                                   guide.upVector(),
                                                   worldTrans.translation(zapi.kWorldSpace),
                                                   worldTrans.scale(zapi.kWorldSpace),
                                                   worldTrans.asMatrix())

        guideIdMap = {i.id(): i for i in guideLayer.iterGuides()}
        curveGuides = guideIdMap.get(UPR_LIP_CURVE_ID), guideIdMap.get(LWR_LIP_CURVE_ID)
        alignInfo = _gatherGuideAlignData(self,
                                          toAlignInfo,
                                          curveGuides
                                          )
        for outId, outMatrix in alignInfo.items():
            guide = guideIdMap[outId] #type: api.Guide
            guide.setLockStateOnAttributes(zapi.localTransformAttrs, False)
            guides.append(guide)
            matrices.append(outMatrix)
        return guides, matrices

    def postAlignGuides(self):
        if not self.active():
            return
        guideIdsToLock = self.guideJointIds() + [OUTER_L_PRIMARY_CTRL_ID, OUTER_R_PRIMARY_CTRL_ID]
        for curveId in (UPR_LIP_CURVE_ID, LWR_LIP_CURVE_ID):
            guideIdsToLock.extend(self.guideCtrlIdsForCurve(curveId))
            guideIdsToLock.append(self.guideCtrlSecondaryIdForCurve(curveId, 0))
            guideIdsToLock.append(self.guideCtrlSecondaryIdForCurve(curveId, 1))
        guides = self.component.guideLayer().findGuides(*guideIdsToLock)
        attrsToLock = zapi.localTranslateAttrs+zapi.localRotateAttrs
        for guide in guides:
            if guide is None:
                continue
            guide.setLockStateOnAttributes(attrsToLock, True)


    def mirrorData(self, translate, rotate):
        guideLayer = self.component.guideLayer()
        guideMap = {i.id(): i for i in guideLayer.iterGuides()}
        # gather the guide data from the left side first, store the guide info for undo
        # then create the symmetry data for the opposite guide
        #     "undo": componentRecoveryData,
        #     "mirrorData": componentMirrorData,

        # map Left To right
        mirrorMap = {}  # type: dict[str, tuple[api.Guide, api.GuideDefinition, api.Guide]]
        guideLayerDef = self.component.definition.guideLayer
        guideDefs = {i.id: i for i in guideLayerDef.iterGuides(includeRoot=True)}
        curveGuides = guideMap.get(UPR_LIP_CURVE_ID), guideMap.get(LWR_LIP_CURVE_ID)
        lipCurveData = []

        def computeCurveSym(curveGuide, curveGuideDef):
            # lip curves need special attention and needs to be prepended so it gets symmetrized instead of mirrored.
            oppositeGuideShape = curveGuide.shapeNode()
            curveTransform = oppositeGuideShape.transformationMatrix()
            curveTransform.setScale(
                oppositeGuideShape.scale(zapi.kObjectSpace), zapi.kObjectSpace
            )
            mirroredState, undoStateData = api.mirrorutils.mirrorGuideData(curveId, curveGuide, curveGuideDef,
                                                                           curveGuide, translate, rotate)
            mirroredState["transform"] = curveGuide.transformationMatrix()
            mirroredState["shape"]["transform"] = curveTransform
            for shape, data in curves.getMirrorCurveCvs(
                    oppositeGuideShape.object(), axis="xyz", space=zapi.kObjectSpace
            ):
                shapeData = mirroredState["shape"]["shape"]
                name = shape.fullPathName().split("|")[-1]
                data = mirrorCvsLocal(data)
                shapeData[om2.MNamespace.stripNamespaceFromName(name)]["cvs"] = data

            return mirroredState, undoStateData

        for curveGuide, curveId in zip(
                curveGuides, [UPR_LIP_CURVE_ID, LWR_LIP_CURVE_ID]
        ):
            if not curveGuide:
                continue
            # shapeMfn = curveGuide.shapeNode().shapes()[0].mfn()
            secondaryId = self.guideCtrlSecondaryIdForCurve(curveId, 1)
            mirrorMap[secondaryId] = (guideMap[secondaryId],
                                      guideDefs[secondaryId],
                                      guideMap[self.guideCtrlSecondaryIdForCurve(curveId, 0)]
                                      )
            # jnts require specialised mirroring where we only want to mirror translation but keeps it's
            # rotation on touched
            jntIds = self.guideJointIdsForCurve(curveId)
            for rJntId, lJntId in zip(jntIds[:int((len(jntIds) / 2) + 1)],
                                      reversed(jntIds[int((len(jntIds) / 2) + 1):])):
                lJntGuide, rJntGuide = guideMap[lJntId], guideMap[rJntId]
                lJntGuideDef = guideDefs[lJntId]

                mirroredState, undoStateData = api.mirrorutils.mirrorGuideData(
                    lJntId, lJntGuide, lJntGuideDef, rJntGuide, translate, rotate
                )

                mirroredTransform = mirroredState["transform"]
                mirroredTransform.setRotation(rJntGuide.rotation(zapi.kWorldSpace))
                lipCurveData.append((mirroredState, undoStateData))

            for index in six.moves.range(int((self.ctrlCount* 0.5)) + 1, self.ctrlCount):
                guideId = self.guideCtrlIdForCurve(curveId, index)
                mirrorMap[guideId] = (guideMap[guideId], guideDefs[guideId], guideMap[guideId.replace("L", "R")])
            mirrorMap[OUTER_L_PRIMARY_CTRL_ID] = (guideMap[OUTER_L_PRIMARY_CTRL_ID],
                                                  guideDefs[OUTER_L_PRIMARY_CTRL_ID],
                                                  guideMap[OUTER_R_PRIMARY_CTRL_ID]
                                                  )
            mirrorMap[OUTER_L_TERTIARY_CTRL_ID] = (guideMap[OUTER_L_TERTIARY_CTRL_ID],
                                                   guideDefs[OUTER_L_TERTIARY_CTRL_ID],
                                                   guideMap[OUTER_R_TERTIARY_CTRL_ID]
                                                   )
            curveGuide = guideMap[curveId]
            curveGuideDef = guideDefs[curveId]
            lipCurveData.append(computeCurveSym(curveGuide, curveGuideDef))

        mirrorDat = api.mirrorutils.mirrorGuidesData(mirrorMap, translate, rotate)
        componentMirrorData = []
        componentRecoveryData = []
        for currentInfo, undoRecoveryData in lipCurveData:
            componentMirrorData.append(currentInfo)
            if undoRecoveryData:
                componentRecoveryData.append(undoRecoveryData)
        for currentInfo, undoRecoveryData in mirrorDat:
            componentMirrorData.append(currentInfo)
            if undoRecoveryData:
                componentRecoveryData.append(undoRecoveryData)

        return {
            "undo": componentRecoveryData,
            "mirrorData": componentMirrorData,
        }

    def preMirror(self, translate, rotate, parent):
        if not self.active():
            return
        guideLayer = self.component.guideLayer()
        graphRegistry = self.component.configuration.graphRegistry()
        guideIds = []
        guides = {i.id(): i for i in guideLayer.iterGuides()}
        for guideId in (
                self.outerLipCtrlPrefixId + "RBind",
                OUTER_R_TERTIARY_CTRL_ID,
                OUTER_R_PRIMARY_CTRL_ID,
                self.outerLipCtrlPrefixId + "LBind",
                OUTER_L_TERTIARY_CTRL_ID,
                OUTER_L_PRIMARY_CTRL_ID,
        ):
            guideIds.append(guideId)
        # for graph in guideLayer.graph
        for curveId in (UPR_LIP_CURVE_ID, LWR_LIP_CURVE_ID):
            guideIds.extend(guideId for guideId in self.guideJointIdsForCurve(curveId))
            guideIds.extend(guideId for guideId in self.guideCtrlIdsForCurve(curveId))
            guideIds.append(self.guideCtrlSecondaryIdForCurve(curveId, 0))
            guideIds.append(self.guideCtrlSecondaryIdForCurve(curveId, 1))
        for guideId in guideIds:
            guide = guides.get(guideId)
            if not guide:
                continue
            offsetParent = guide.attribute("offsetParentMatrix")
            source = offsetParent.source()
            if source:
                source.disconnect(offsetParent)
            guideLayer.deleteNamedGraph("motionPathGuide" + guideId, graphRegistry)

    def postMirror(self, translate, rotate, parent):
        if not self.active():
            return
        self.postSetupGuide()

    def preSetupGuide(self):
        """Performs pre-setup operations on the guide."""
        if not self.active():
            return
        self.component.logger.debug("PreSetup guides")
        guideLayerDef = self.component.definition.guideLayer
        guideLayerDef.createGuide(
            id=MASK_GUIDE_ID,
            parent="root",
            pivotShape="nurbsSphere",
            shape=None,
            color=CURVE_STARTEND_COLOR,
            pivotColor=[0.477, 1, 0.073],
            pivotShapeType=api.constants.GUIDE_TYPE_NURBS_SURFACE,
            selectionChildHighlighting=self.component.configuration.selectionChildHighlighting
        )
        constants = []
        for curveId in (UPR_LIP_CURVE_ID, LWR_LIP_CURVE_ID):
            constants.append(api.AttributeDefinition(
                name=curveId + "CtrlPositions",
                Type=zapi.attrtypes.kMFnNumericFloat,
                keyable=False,
                channelBox=False,
                isArray=True
            ))
        guideLayerDef.addGuideSettings(constants)

    def postSetupGuide(self):
        if not self.active():
            return
        self.component.logger.debug("PostSetup guides")
        guideLayer = self.component.guideLayer()

        uprCurve, lwrCurve = guideLayer.findGuides(UPR_LIP_CURVE_ID, LWR_LIP_CURVE_ID)
        guideSettings = guideLayer.guideSettings()
        compName, compSide = self.component.name(), self.component.side()
        naming = self.component.namingConfiguration()
        guides = {i.id(): i for i in guideLayer.iterGuides(False)}
        surfaceMask = guides[MASK_GUIDE_ID]
        attrsToLock = zapi.localTranslateAttrs + zapi.localRotateAttrs
        for curveGuide, curveId in zip((uprCurve, lwrCurve), (UPR_LIP_CURVE_ID, LWR_LIP_CURVE_ID)):
            if not curveGuide:
                continue
            guideShape = curveGuide.shapeNode().shapes()[0]
            shapeMfn = guideShape.mfn()
            cvPositions = guideShape.cvPositions(zapi.kWorldSpace)[1:-1]
            ctrlPositionsArray = guideSettings.attribute(curveId + "CtrlPositions")
            for index, jntGuide in enumerate(self.guideJointIdsForCurve(curveId)):
                guide = guides[jntGuide]  # type: zapi.DagNode
                paramName = self.guideJntParamPosSettingName(curveId, index)
                param = guideSettings.attribute(paramName)
                _bindGuideToCurve(self, guideLayer, guide, guideShape, param)
                guide.setLockStateOnAttributes(attrsToLock, True)

            # bind first and last
            if curveId == UPR_LIP_CURVE_ID:
                for rGuideId, lGuideId, lock in zip((self.outerLipCtrlPrefixId + "RBind",
                                                     OUTER_R_TERTIARY_CTRL_ID,
                                                     OUTER_R_PRIMARY_CTRL_ID),
                                                    (self.outerLipCtrlPrefixId + "LBind",
                                                     OUTER_L_TERTIARY_CTRL_ID,
                                                     OUTER_L_PRIMARY_CTRL_ID),
                                                    (False, True, False)
                                                    ):
                    rGuide = guides[rGuideId]
                    lGuide = guides[lGuideId]
                    _bindGuideToCurve(self, guideLayer, rGuide,
                                      guideShape, 0.0)
                    _bindGuideToCurve(self, guideLayer, lGuide,
                                      guideShape, 1.0, invertAim=True)
                    if lock:
                        rGuide.hide()
                        lGuide.hide()
                    rGuide.setLockStateOnAttributes(attrsToLock + ["visibility"], True)
                    lGuide.setLockStateOnAttributes(attrsToLock + ["visibility"], True)

            rSecondGuide = guides[self.guideCtrlSecondaryIdForCurve(curveId, 0)]
            lSecondGuide = guides[self.guideCtrlSecondaryIdForCurve(curveId, 1)]
            _bindGuideToCurve(self, guideLayer, rSecondGuide,
                              guideShape, 0.25)
            _bindGuideToCurve(self, guideLayer, lSecondGuide,
                              guideShape, 0.75)
            rSecondGuide.setLockStateOnAttributes(attrsToLock + ["visibility"], True)
            lSecondGuide.setLockStateOnAttributes(attrsToLock + ["visibility"], True)

            for index, ctrlId in enumerate(self.guideCtrlIdsForCurve(curveId)):
                guide = guides[ctrlId]
                cvPos, param = shapeMfn.closestPoint(cvPositions[index], space=zapi.kWorldSpace)
                ctrlPositionsArray[index].set(param)
                _bindGuideToCurve(self, guideLayer, guide, guideShape, param,
                                  invertAim=index < (self.ctrlCount - 1) / 2)
                if index == (self.ctrlCount - 1) / 2:
                    guide.hide()
                guide.setLockStateOnAttributes(attrsToLock, True)

        mat = self.component.meta.taggedNode("surfaceMaskMaterial")
        if mat is None:
            mat = createshadernetwork.createLambertMaterial(naming.resolve("object", {
                "componentName": compName,
                "side": compSide,
                "section": "surfaceMask",
                "type": "material"
            }),
                                                            message=False,
                                                            rgbColor=(0.15, 0.7, 1.0))
            mat = zapi.nodeByName(mat)
        self.component.meta.addTaggedNode(mat, "surfaceMaskMaterial")
        mat.attribute("transparency").set((0.95, 0.95, 0.95))
        shaderutils.assignShader((surfaceMask.fullPathName(),), mat.fullPathName())

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

    def setupInputs(self):
        if not self.active():
            return

    def setupOutputs(self, parentNode):
        if not self.active():
            return
        self.component.logger.debug("Setup Outputs")
        deformLayer = self.component.deformLayer()
        inputLayer = self.component.inputLayer()
        outputLayerDef = self.component.definition.outputLayer
        guideLayerDef = self.component.definition.guideLayer
        namingConfig = self.component.namingConfiguration()
        compName, compSide = self.component.name(), self.component.side()
        uprCtrlId = self.guidePrimaryCtrlIdForCurve(UPR_LIP_CURVE_ID)
        lwrCtrlId = self.guidePrimaryCtrlIdForCurve(LWR_LIP_CURVE_ID)
        primaryGuides = guideLayerDef.findGuides(OUTER_R_PRIMARY_CTRL_ID,
                                                 OUTER_L_PRIMARY_CTRL_ID,
                                                 uprCtrlId,
                                                 lwrCtrlId)
        parentIn = inputLayer.inputNode("parent")
        parentIn.setWorldMatrix(parentNode.worldMatrix())
        root = deformLayer.taggedNode("parentSpaceIn")
        if root is None:
            root = zapi.createDag(namingConfig.resolve(
                "object",
                {"componentName": compName,
                 "side": compSide,
                 "section": "parentSpace",
                 "type": "jnt"}
            ), "transform", parent=deformLayer.rootTransform())
            deformLayer.addTaggedNode(root, "parentSpaceIn")
        root.setWorldMatrix(parentIn.worldMatrix())
        zapi.buildConstraint(root, {"targets": (("", parentIn),)},
                             constraintType="matrix", maintainOffset=False)
        nameMap = {
            OUTER_R_PRIMARY_CTRL_ID: OUTER_R_PRIMARY_CTRL_ID.replace("R", "") + "PSD_R",
            OUTER_L_PRIMARY_CTRL_ID: OUTER_L_PRIMARY_CTRL_ID.replace("L", "") + "PSD_L",
            uprCtrlId: uprCtrlId.replace("Ctr", "") + "PSD_M",
            lwrCtrlId: lwrCtrlId.replace("Ctr", "") + "PSD_M"
        }
        for primaryGuide in primaryGuides:
            if not primaryGuide:
                continue
            primaryId = primaryGuide.id
            psdId = primaryId + "PSD"
            valueOutput = deformLayer.taggedNode(psdId)
            rotation = mayamath.lookAt(
                root.translation(zapi.kWorldSpace),
                primaryGuide.translate,
                zapi.Vector(0, 0, 1),
                zapi.Vector(0, 1, 0)
            )
            if not valueOutput:
                # create space locator which contains attributes for primary motion output
                valueOutput = zapi.createDag(
                    "PSD",
                    "locator"
                )
                valueOutput.setParent(root)
                valueOutput.setTranslation(root.translation(zapi.kWorldSpace))
                valueOutput.setRotation(rotation)
                valueOutput.setShapeColour((1.000, 0.587, 0.073))
                deformLayer.addTaggedNode(valueOutput, psdId)
            else:
                valueOutput.setRotation(rotation, space=zapi.kWorldSpace)
                valueOutput.setRotation((0, 0, 0), zapi.kTransformSpace)
            name = namingConfig.resolve(
                "object",
                {
                    "componentName": compName,
                    "side": compSide,
                    "section": nameMap.get(primaryId),
                    "type": "transform",
                },
            )
            valueOutput.rename(name)

            outputLayerDef.createOutput(
                id=primaryGuide.id,
                name=namingConfig.resolve(
                    "outputName",
                    {
                        "id": primaryId,
                        "componentName": compName,
                        "side": compSide,
                        "type": "hiveOutput",
                    },
                ),
                rotateOrder=primaryGuide.rotateOrder,
                worldMatrix=primaryGuide.worldMatrix,
            )

    def postDeformDriverSetup(self, parentNode):
        if not self.active():
            return
        uprGuide, lwrGuide = self.component.definition.guideLayer.findGuides(
            self.guidePrimaryCtrlIdForCurve(UPR_LIP_CURVE_ID),
            self.guidePrimaryCtrlIdForCurve(LWR_LIP_CURVE_ID),
        )
        if not uprGuide or not lwrGuide:
            return
        inputLayer = self.component.inputLayer()
        uprIn, lwrIn = inputLayer.findInputNodes("upperLip", "lowerLip")
        uprSet, lwrSet = False, False
        for driverDef in self.component.definition.drivers:
            inNode = uprIn
            if driverDef.label == "lowerLip":
                inNode = lwrIn
            for driverLabel, driverExpr in driverDef.params.drivers:
                _, inDriver = api.attributeRefToSceneNode(
                    self.component.rig, self.component, driverExpr
                )
                if inDriver:
                    inNode.setWorldMatrix(inDriver.transformationMatrix().asMatrix())
                    if driverDef.label == "upperLip":
                        uprSet = True
                    else:
                        lwrSet = True
        if not uprSet:
            uprIn.setWorldMatrix(uprGuide.transformationMatrix(scale=False).asMatrix())
        if not lwrSet:
            lwrIn.setWorldMatrix(lwrGuide.transformationMatrix(scale=False).asMatrix())

    def setupRig(self, parentNode):
        if not self.active():
            return [], []
        guideLayerDef = self.component.definition.guideLayer
        guideDefs = {i.id: i for i in self.component.definition.guideLayer.iterGuides(includeRoot=False)}

        uprLipCurveDef, lwrLipCurveDef = guideDefs.get(UPR_LIP_CURVE_ID), guideDefs.get(LWR_LIP_CURVE_ID)
        if not uprLipCurveDef or not lwrLipCurveDef:
            return [], []
        rigLayer = self.component.rigLayer()
        controlPanel = rigLayer.controlPanel()
        rootTransform = rigLayer.rootTransform()
        inputLayer = self.component.inputLayer()
        outputLayer = self.component.outputLayer()

        inputNodes = {i.id(): i for i in inputLayer.inputs()}
        outputNodes = {i.id(): i for i in outputLayer.outputs()}
        parentIn = inputNodes["parent"]
        parentIn.setWorldMatrix(parentNode.worldMatrix())
        namingConfig = self.component.namingConfiguration()
        compName, compSide = self.component.name(), self.component.side()
        maskSurfaceDef = guideLayerDef.guide(MASK_GUIDE_ID)
        constantsNode = rigLayer.createSettingsNode(namingConfig.resolve("object",
                                                                         {"componentName": self.component.name(),
                                                                          "side": self.component.side(),
                                                                          "section": "constants",
                                                                          "type": "network"}),
                                                    "constants")
        parentSpaceHrc = api.componentutils.createParentSpaceTransform(
            namingConfig, compName, compSide, rootTransform,
            rootTransform, rigLayer, parentIn, maintainOffset=False
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
            parent=rootTransform
        )
        ctrls = {}

        topSurfaceMask, botSurfaceMask = self._generateSurfaceMask(rigLayer,
                                                                   maskSurfaceDef,
                                                                   parentSpaceHrc,
                                                                   extrasHrc,
                                                                   namingConfig,
                                                                   compName, compSide)
        mainCtrl, mainCtrlDriver, uprLipDriver, lwrLipDriver = self._generatePrimaryCtrls(parentSpaceHrc,
                                                                                          topSurfaceMask,
                                                                                          ctrls, inputNodes,
                                                                                          outputNodes)
        uprProxyPinGraph, lwrProxyPinGraph = self._bindTertiaryCtrlsToMask(rigLayer, topSurfaceMask, botSurfaceMask,
                                                                           ctrls, parentSpaceHrc)

        rootPushJnt = rigLayer.createJoint(
            id="rootPushJnt",
            name=namingConfig.resolve("object", {
                "componentName": compName,
                "side": compSide,
                "section": "rootPushJnt",
                "type": "joint"
            }),
            translate=parentSpaceHrc.translation(zapi.kWorldSpace),
            rotate=parentSpaceHrc.rotation()
        )
        rootPushJnt.setParent(extrasHrc, maintainOffset=False)
        uprBuilder = LipBuilder(
            self,
            constantsNode,
            topSurfaceMask,
            uprLipCurveDef,
            ctrls,
            guideDefs,
            self.ctrlCount,
            self.jointCount,
            parentSpaceHrc,
            extrasHrc,
            uprLipDriver,
            rootTransform,
            uprProxyPinGraph,
            rootPushJnt,
            createEndCtrls=True

        )
        lwrBuilder = LipBuilder(
            self,
            constantsNode,
            botSurfaceMask,
            lwrLipCurveDef,
            ctrls,
            guideDefs,
            self.ctrlCount,
            self.jointCount,
            parentSpaceHrc,
            extrasHrc,
            lwrLipDriver,
            rootTransform,
            lwrProxyPinGraph,
            rootPushJnt
        )
        uprBuilder.build()
        lwrBuilder.build()

        self._bindJointsToCurve(uprBuilder,
                                lwrBuilder,
                                ctrls,
                                rigLayer,
                                self.component.deformLayer(),
                                controlPanel,
                                namingConfig,
                                uprBuilder._extras)

        rotMult = zapi.createDG(namingConfig.resolve("object", {
            "componentName": compName,
            "side": compSide,
            "section": "rotMult",
            "type": zapi.kMultDoubleLinearName,
        }),
                                zapi.kMultDoubleLinearName)
        rotMult.input2.set(10)
        mainCtrl.attribute("scale").connect(mainCtrlDriver.attribute("scale"))
        mainCtrl.attribute("rotateZ").connect(mainCtrlDriver.attribute("rotateZ"))
        mainCtrl.attribute("translateX").connect(rotMult.attribute("input1"))
        rotMult.output.connect(mainCtrlDriver.attribute("rotateY"))
        mainCtrl.attribute("translateY").connect(mainCtrlDriver.attribute("translateY"))
        mainCtrl.attribute("translateZ").connect(mainCtrlDriver.attribute("translateZ"))
        rigLayer.addExtraNodes(uprBuilder._extras + lwrBuilder._extras + [rotMult])
        # skin the high/res curves
        halfJntCount = int((self.ctrlCount - 1) / 2)
        uprCtrCtrlId = self.guideCtrlIdForCurve(UPR_LIP_CURVE_ID, halfJntCount) + "LowresJnt"
        lwrCtrCtrlId = self.guideCtrlIdForCurve(LWR_LIP_CURVE_ID, halfJntCount) + "LowresJnt"
        lowLJnt = uprBuilder.curveLowSkinJoints[OUTER_L_TERTIARY_CTRL_ID + "LowresJnt"]
        lowRJnt = uprBuilder.curveLowSkinJoints[OUTER_R_TERTIARY_CTRL_ID + "LowresJnt"]
        self._setLowresSkinWeights(ctrls[uprBuilder._curveLowResId].shapes()[0],
                                   [uprBuilder.curveLowSkinJoints[uprCtrCtrlId],
                                    lowLJnt,
                                    lowRJnt])
        self._setLowresSkinWeights(ctrls[lwrBuilder._curveLowResId].shapes()[0],
                                   [lwrBuilder.curveLowSkinJoints[lwrCtrCtrlId],
                                    lowLJnt,
                                    lowRJnt
                                    ])

        uprSurfaceJnts = list(uprBuilder.curveSurfaceFollowJoints.values())
        lwrSurfaceJnts = list(lwrBuilder.curveSurfaceFollowJoints.values())
        uprJnts = list(uprBuilder.curveHighSkinJoints.values())
        lwrJnts = list(lwrBuilder.curveHighSkinJoints.values())
        uprSurfaceJnts = uprSurfaceJnts[:halfJntCount] + [uprBuilder.curveLowSkinJoints[uprCtrCtrlId]] + uprSurfaceJnts[
                                                                                                         halfJntCount:]
        lwrSurfaceJnts = lwrSurfaceJnts[:halfJntCount] + [lwrBuilder.curveLowSkinJoints[lwrCtrCtrlId]] + lwrSurfaceJnts[
                                                                                                         halfJntCount:]
        self._setHighresSkinWeights(uprBuilder.ctrls[uprBuilder._curveSurfaceId],
                                    [uprJnts[-2]] +
                                    uprSurfaceJnts +
                                    [uprJnts[-1]]
                                    )
        self._setHighresSkinWeights(lwrBuilder.ctrls[lwrBuilder._curveSurfaceId],
                                    [uprJnts[-2]] +
                                    lwrSurfaceJnts +
                                    [uprJnts[-1]]
                                    )
        self._setPushCurveSkinWeights(uprBuilder.ctrls[uprBuilder._curvePuffId],
                                      [uprBuilder.curvePushJoints[1],
                                       uprBuilder.curvePushJoints[0],
                                       uprBuilder.curvePushJoints[2]],
                                      rootPushJnt
                                      )
        self._setPushCurveSkinWeights(lwrBuilder.ctrls[lwrBuilder._curvePuffId],
                                      [uprBuilder.curvePushJoints[1],
                                       lwrBuilder.curvePushJoints[0],
                                       uprBuilder.curvePushJoints[2]],
                                      rootPushJnt
                                      )

        self._setHighresSkinWeights(uprBuilder.ctrls[uprBuilder._curveHighresSkinId],
                                    [uprJnts[-2]] +
                                    uprJnts[:-2] +
                                    [uprJnts[-1]]
                                    )

        self._setHighresSkinWeights(lwrBuilder.ctrls[lwrBuilder._curveHighresSkinId],
                                    [uprJnts[-2]] +
                                    lwrJnts +
                                    [uprJnts[-1]]
                                    )
        self.setControlNaming()

    def postSetupRig(self, parentNode):
        if not self.active():
            return
        rigLayer = self.component.rigLayer()
        controlPanel = rigLayer.controlPanel()
        primaryIds = [OUTER_L_PRIMARY_CTRL_ID,
                      OUTER_R_PRIMARY_CTRL_ID]
        secondaryIds = (self.guideCtrlSecondaryIdForCurve(UPR_LIP_CURVE_ID, 0),
                        self.guideCtrlSecondaryIdForCurve(UPR_LIP_CURVE_ID, 1),
                        self.guideCtrlSecondaryIdForCurve(LWR_LIP_CURVE_ID, 0),
                        self.guideCtrlSecondaryIdForCurve(LWR_LIP_CURVE_ID, 1)
                        )
        uprLwrCenterCtrls = rigLayer.findControls(self.guidePrimaryCtrlIdForCurve(UPR_LIP_CURVE_ID),
                                                  self.guidePrimaryCtrlIdForCurve(LWR_LIP_CURVE_ID))
        for i in uprLwrCenterCtrls:
            if not i:
                output.displayWarning("Unable to build lips due to missing lip curves")
                return
        _setupPSDAims(primaryIds + [self.guidePrimaryCtrlIdForCurve(UPR_LIP_CURVE_ID),
                                    self.guidePrimaryCtrlIdForCurve(LWR_LIP_CURVE_ID)],
                      rigLayer, self.component.deformLayer(),
                      self.component.namingConfiguration(),
                      self.component.name(), self.component.side())
        mainCtrl = rigLayer.control(MAIN_CTRL_ID)
        tertiaryCtrls = rigLayer.findControls(*(self.guideCtrlIdsForCurve(UPR_LIP_CURVE_ID) +
                                                self.guideCtrlIdsForCurve(LWR_LIP_CURVE_ID) +
                                                [OUTER_L_TERTIARY_CTRL_ID,
                                                 OUTER_R_TERTIARY_CTRL_ID]))
        secondaryCtrls = rigLayer.findControls(*secondaryIds)
        tertiaryVis = controlPanel.attribute("tertiaryLipCtrlVis")
        centerCtrlVis = controlPanel.attribute("centerLipCtrlVis")
        mainVis = controlPanel.attribute("globalCtrlVis")
        secondaryVis = controlPanel.attribute("secondaryLipCtrlVis")

        for ctrl in tertiaryCtrls:
            for shape in ctrl.iterShapes():
                tertiaryVis.connect(shape.attribute("visibility"))
        for ctrl in secondaryCtrls:
            for shape in ctrl.iterShapes():
                secondaryVis.connect(shape.attribute("visibility"))
        for ctrl in uprLwrCenterCtrls:
            for shape in ctrl.iterShapes():
                centerCtrlVis.connect(shape.attribute("visibility"))

        for shape in mainCtrl.iterShapes():
            mainVis.connect(shape.attribute("visibility"))
        mainGuideDef = self.component.definition.guideLayer.guide(MAIN_CTRL_ID)
        aimAxis = mainGuideDef.perpendicularVectorIndex()[0]
        mainRotateAttrs = list(zapi.localRotateAttrs)
        del mainRotateAttrs[aimAxis]
        mainCtrlsToHandle = [
                                zapi.localScaleAttrs[aimAxis],
                                zapi.localTranslateAttrs[aimAxis]] + mainRotateAttrs
        mainCtrl.setLockStateOnAttributes(mainCtrlsToHandle, True)
        mainCtrl.showHideAttributes(mainCtrlsToHandle, False)

        uprLwrCenterGuideDefs = self.component.definition.guideLayer.findGuides(
            self.guidePrimaryCtrlIdForCurve(UPR_LIP_CURVE_ID),
            self.guidePrimaryCtrlIdForCurve(LWR_LIP_CURVE_ID))
        # # handle locking attributes
        for index, ctrl in enumerate(uprLwrCenterCtrls):
            aimAxis = uprLwrCenterGuideDefs[index].perpendicularVectorIndex()[0]
            rotAxisToLock = list(zapi.localRotateAttrs)
            del rotAxisToLock[aimAxis]
            attrsToLock = rotAxisToLock + [zapi.localScaleAttrs[aimAxis]]
            ctrl.setLockStateOnAttributes(attrsToLock, True)
            ctrl.showHideAttributes(attrsToLock, False)

        for index, ctrl in enumerate(tertiaryCtrls + secondaryCtrls):
            attrs = zapi.localRotateAttrs + zapi.localScaleAttrs
            ctrl.setLockStateOnAttributes(attrs, True)
            ctrl.showHideAttributes(attrs, False)

    def setControlNaming(self):
        compName, compSide = self.component.name(), self.component.side()
        namingConfig = self.component.namingConfiguration()
        rigLayer = self.component.rigLayer()

        for ctrl in rigLayer.iterControls():
            ctrlId = ctrl.id()
            args = {"componentName": compName,
                    "side": compSide,
                    "id": ctrlId,
                    "type": "control",
                    }
            ctrl.rename(
                namingConfig.resolve(
                    "controlName",
                    args
                )
            )
            args["type"] = "srt"
            srt = ctrl.srt()
            if srt:
                srt.rename(
                    namingConfig.resolve(
                        "controlName",
                        args
                    )
                )

    def _generatePrimaryCtrls(self, parent, surfaceMask, ctrls, inputNodes, outputNodes):
        guides = self.component.definition.guideLayer.findGuides(MAIN_CTRL_ID,
                                                                 self.guidePrimaryCtrlIdForCurve(UPR_LIP_CURVE_ID),
                                                                 self.guidePrimaryCtrlIdForCurve(LWR_LIP_CURVE_ID),
                                                                 OUTER_L_PRIMARY_CTRL_ID,
                                                                 OUTER_R_PRIMARY_CTRL_ID)
        rigLayer = self.component.rigLayer()
        driver = zapi.createDag(self.component.namingConfiguration().resolve("object",
                                                                             {
                                                                                 "componentName": self.component.name(),
                                                                                 "side": self.component.name(),
                                                                                 "section": "primaryCtrlMainDriver",
                                                                                 "type": "transform"
                                                                             }),
                                "transform", parent=parent)
        extras = [driver]
        driver.setWorldMatrix(surfaceMask.worldMatrix())
        driver.resetTransformToOffsetParent()
        rigLayer.addTaggedNode(driver, MAIN_CTRL_DRIVER_ID)
        mainCtrl = None
        for index, (guide, negate, createSrt) in enumerate(zip(guides,
                                                               (False, False, False, False, True),
                                                               (False, True, True, True, True))):
            # because the transform is serialized in worldSpace we need to flip the z axis to
            # get X mirror as the rotation will likely be 180ish on Y
            scale = [1.0, 1.0, 1.0]

            if negate:
                scale[2] *= -1.0
            kwargs = dict(
                id=guide.id,
                translate=guide.translate,
                rotate=guide.rotate,
                scale=scale,
                parent=parent if index == 0 else driver,
                rotateOrder=guide.rotateOrder,
                shape=guide.shape,
                selectionChildHighlighting=self.component.configuration.selectionChildHighlighting
            )
            if createSrt:
                kwargs["srts"] = [
                    {"name": guide.id + "inDriver_srt", "id": guide.id}
                ]
            ctrl = rigLayer.createControl(**kwargs)
            if index == 0:
                mainCtrl = ctrl
            ctrls[guide.id] = ctrl
            ctrl.resetTransformToOffsetParent()
            outputNode = outputNodes.get(guide.id)
            if not outputNode:
                continue
            _, utils = zapi.buildConstraint(outputNode, drivers={"targets": (("", ctrl),)},
                                            constraintType="matrix",
                                            maintainOffset=False)
            extras.extend(utils)

        rigLayer = self.component.rigLayer()
        ctrls = [ctrls[i] for i in (OUTER_L_PRIMARY_CTRL_ID,
                                    OUTER_R_PRIMARY_CTRL_ID,
                                    self.guidePrimaryCtrlIdForCurve(UPR_LIP_CURVE_ID),
                                    self.guidePrimaryCtrlIdForCurve(LWR_LIP_CURVE_ID)
                                    )]
        lwrSurfaceMask = rigLayer.taggedNode("lwrFaceMask")
        self._bindPrimariesToDrivers(rigLayer, inputNodes["upperLip"], inputNodes["lowerLip"], lwrSurfaceMask, *ctrls)
        # create 2 multMatrix nodes one for the upper and lower and mult them with the mainDriver so they can then
        # drive ctrl and joint rotations
        lipMultOutputs = [mainCtrl, driver]
        for name, inputNode in zip(("upperLipInCombine", "lowerLipInCombine"),
                                   (inputNodes["upperLip"], inputNodes["lowerLip"])):
            lipCombineMult = zapi.createDG(self.component.namingConfiguration().resolve("object", {
                "componentName": self.component.name(),
                "side": self.component.side(),
                "section": name,
                "type": "multMatrix"
            }), "multMatrix")
            driver.attribute("matrix").connect(lipCombineMult.matrixIn[0])
            inputNode.worldMatrixPlug().connect(lipCombineMult.matrixIn[1])
            lipMultOutputs.append(lipCombineMult.matrixSum)
            extras.append(lipCombineMult)

        rigLayer.addExtraNodes(extras)
        return lipMultOutputs

    def _generateSurfaceMask(self, rigLayer, maskSurfaceDef, parentTransform, lwrParent,
                             namingConfig,
                             compName, compSide
                             ):

        uprSurfaceTransform = zapi.createDag(namingConfig.resolve("object",
                                                                  {
                                                                      "componentName": compName,
                                                                      "side": compSide,
                                                                      "section": "uprfaceMask",
                                                                      "type": "nurbsSurface"
                                                                  }),
                                             "transform", parent=parentTransform)
        lwrSurfaceTransform = zapi.createDag(namingConfig.resolve("object", {
            "componentName": compName,
            "side": compSide,
            "section": "uprfaceMask",
            "type": "nurbsSurface"
        }),
                                             "transform", parent=lwrParent)
        curves.createCurveSurface(uprSurfaceTransform.object(), maskSurfaceDef.pivotShape, space=zapi.kWorldSpace)
        curves.createCurveSurface(lwrSurfaceTransform.object(), maskSurfaceDef.pivotShape, space=zapi.kWorldSpace)
        uprSurfaceTransform.hide()
        lwrSurfaceTransform.hide()
        uprSurfaceTransform.setLockStateOnAttributes(("visibility",), False)
        lwrSurfaceTransform.setLockStateOnAttributes(("visibility",), False)
        rigLayer.addTaggedNode(uprSurfaceTransform, "uprFaceMask")
        rigLayer.addTaggedNode(lwrSurfaceTransform, "lwrFaceMask")

        return uprSurfaceTransform, lwrSurfaceTransform

    def _createZipGraphs(self, rigLayer, controlPanel, namingConfig, compName, compSide):
        # create global upr and lwr falloff
        lZipAttr = controlPanel.attribute(LIPS_ZIP_L_ATTR)
        rZipAttr = controlPanel.attribute(LIPS_ZIP_R_ATTR)
        lZipOffsetAttr = controlPanel.attribute(LIPS_ZIP_OFFSET_L_ATTR)
        rZipOffsetAttr = controlPanel.attribute(LIPS_ZIP_OFFSET_R_ATTR)
        falloffOutputs = [None, None]

        for index, (side, falloffAttr) in enumerate(zip(("L", "R"), (lZipOffsetAttr, rZipOffsetAttr))):
            pma = zapi.createDG(namingConfig.resolve("object", {
                "componentName": compName,
                "side": compSide,
                "section": "zipFallOffSub" + side,
                "type": "plusMinusAverage",
            }), "plusMinusAverage")
            factor = zapi.createDG(namingConfig.resolve("object", {
                "componentName": compName,
                "side": compSide,
                "section": "zipFallFactor" + side,
                "type": zapi.kMultDoubleLinearName,
            }), zapi.kMultDoubleLinearName)
            pma.operation.set(2)  # subtract
            pma.input1D[0].set(10.0)
            falloffAttr.connect(pma.input1D[1])
            pma.output1D.connect(factor.input1)
            factor.input2.set(0.1)
            falloffOutputs[index] = factor.output
        globalLFalloffOutput, globalRFalloffOutput = falloffOutputs
        # for each joint pair(upr/lwr) from right to left create the zip network.
        # output the graphs in order and they will provided to the lip builder for connection
        graphReg = self.component.configuration.graphRegistry()
        graphData = graphReg.graph(graphconstants.klipZipper)
        graphName = graphData.name
        graphOutputs = []
        maxIndex = self.jointCount + 1
        for i in six.moves.range(1, maxIndex):
            graphData.name = graphName + "_" + str(i).zfill(2)
            sceneGraph = self.createGraph(rigLayer, graphData)
            sceneGraph.connectToInput("zipLValue", lZipAttr)
            sceneGraph.connectToInput("zipRValue", rZipAttr)
            sceneGraph.connectToInput("zipLFalloff", lZipOffsetAttr)
            sceneGraph.connectToInput("zipLModifiedFalloff", globalLFalloffOutput)
            sceneGraph.connectToInput("zipRFalloff", rZipOffsetAttr)
            sceneGraph.connectToInput("zipRModifiedFalloff", globalRFalloffOutput)
            sceneGraph.setInputAttr("zipLIndex", maxIndex - i)
            sceneGraph.setInputAttr("zipRIndex", i)
            zipBlender = zapi.createDG(namingConfig.resolve("object",
                                                            {
                                                                "componentName": compName,
                                                                "side": compSide,
                                                                "section": "LipMidPoint" + str(i).zfill(2),
                                                                "type": "blendMatrix",
                                                            }), "blendMatrix")

            graphOutputs.append((sceneGraph.outputAttr("zipBlend"), zipBlender))
        return graphOutputs

    def _idIndexForIndex(self, index, count):
        """Generates the L/R/Ctr index id for the given index.
        Generation is based on the control count.
        mid index is ctrlCount-1 /2
        indexing occurs from ctr out ie closet to center is 00

        :param index: The index along the curve.
        :type index: int
        :return:
        :rtype: str
        """
        midIndex = int((count - 1) * 0.5)
        if index > midIndex:
            return "{}L".format(str(index - midIndex - 1).zfill(2))
        # center ctrl or joint has no index
        elif index == midIndex:
            return "Ctr"
        return "{}R".format(str(midIndex - 1 - index).zfill(2))

    def _isIndexCenterTertiaryCtrl(self, index, count):
        return index == int((count - 1) * 0.5)

    def _createCurveGuides(self, guideLayerDef, curve, curveId, jointCount):
        curveShape = curve.shapes()[0]
        crvMfn = curveShape.mfn()

        cvPositions = curveShape.cvPositions(zapi.kWorldSpace)

        primaryPosOffsetVec = _guideShapeOffset()
        ctrlColor = CURVE_COLOR_MAP[curveId]
        generalKwargs = {
            "selectionChildHighlighting": self.component.configuration.selectionChildHighlighting,
            "upVector": (0.0, 1.0, 0.0),
            "aimVector": (1.0, 0.0, 0.0)
        }
        self.component.logger.debug("Computing L Tertiary guide def for curve: {}".format(curveId))
        cvPos = zapi.Vector(cvPositions[-1])
        shapeRotation = (math.pi * 0.5, 0, 0)
        scale = list(DEFAULT_GUIDE_CTRL_SCALE)
        shapeScale = list(DEFAULT_GUIDE_SHAPE_SCALE)

        _createGuideDef(
            guideLayerDef=guideLayerDef,
            guideId=OUTER_L_TERTIARY_CTRL_ID,
            parent="root",
            ctrlColor=DEFAULT_SECONDARY_CTRL_COLOR,
            position=list(cvPos),
            scale=scale,
            ctrlScale=shapeScale,
            ctrlRotation=shapeRotation,
            shape=TERTIARY_GUIDE_SHAPE,
            ctrlPosition=list(primaryPosOffsetVec + cvPos),
            **generalKwargs
        )
        mirroredTranslation = zapi.Vector(cvPositions[0])
        _createGuideDef(
            guideLayerDef=guideLayerDef,
            guideId=OUTER_R_TERTIARY_CTRL_ID,
            parent="root",
            ctrlColor=DEFAULT_SECONDARY_CTRL_COLOR,
            position=list(mirroredTranslation),
            scale=scale,
            ctrlScale=shapeScale,
            ctrlRotation=shapeRotation,
            shape=TERTIARY_GUIDE_SHAPE,
            ctrlPosition=list(primaryPosOffsetVec + mirroredTranslation),
            **generalKwargs
        )
        if curveId == UPR_LIP_CURVE_ID:
            self._createInnerOuterGuides(
                curveShape
            )
        # create control curve guides for the lip
        self._createCtrlGuides(guideLayerDef, curveId, crvMfn,
                               cvPositions=cvPositions,
                               shapePositionOffset=primaryPosOffsetVec,
                               **generalKwargs)
        self._createJointGuides(guideLayerDef, curveShape, curveId, jointCount)
        pos = zapi.Vector(crvMfn.getPointAtParam(0.5, space=zapi.kWorldSpace))
        _createGuideDef(
            guideLayerDef=guideLayerDef,
            guideId=self.guidePrimaryCtrlIdForCurve(curveId),
            parent="root",
            ctrlColor=ctrlColor,
            position=list(pos),
            scale=scale,
            ctrlScale=DEFAULT_PRIMARY_GUIDE_SHAPE_SCALE,
            ctrlRotation=DEFAULT_PRIMARY_CTRL_GUIDE_ROT_MAP[curveId],
            shape=PRIMARY_GUIDE_SHAPE,
            ctrlPosition=list(pos),
            **generalKwargs
        )
        return True

    def _createInnerOuterGuides(self, curve):
        crvMfn = curve.mfn()
        guideLayerDef = self.component.definition.guideLayer
        upVector = [0.0, 1.0, 0.0]
        primaryPosOffsetVec = _guideShapeOffset()
        endParamAim = zapi.Vector(crvMfn.getPointAtParam(0.98, space=zapi.kWorldSpace))
        firstGuide = None
        for guideId, bindId, param, negate in zip((OUTER_L_PRIMARY_CTRL_ID, OUTER_R_PRIMARY_CTRL_ID),
                                                  (OUTER_L_BIND_ID, OUTER_R_BIND_ID), [1.0, 0.0], (False, True)):
            if negate:
                mat = firstGuide.worldMatrix
                mirroredTransform = mayamath.mirrorMatrix(mat, translate=("x",),
                                                          rotate=mayamath.MIRROR_PLANE_BY_AXIS["x"],
                                                          mirrorFunction=mayamath.MIRROR_SCALE)
                orient = mirroredTransform.rotation(asQuaternion=True)
                scale = mirroredTransform.scale(zapi.kWorldSpace)
                position = mirroredTransform.translation(zapi.kWorldSpace)
            else:
                param = crvMfn.findParamFromLength(crvMfn.length() * param)
                position = zapi.Vector(crvMfn.getPointAtParam(param, space=zapi.kWorldSpace))
                scale = list(DEFAULT_GUIDE_CTRL_SCALE)
                shapeScale = zapi.Vector(DEFAULT_GUIDE_SHAPE_SCALE)
                orient = mayamath.lookAt(
                    position,
                    endParamAim,
                    zapi.Vector(-1.0, 0, 0),
                    zapi.Vector(0, 1, 0),
                    constrainAxis=zapi.Vector(0.0, 1.0, 0.0)
                )

            guide = guideLayerDef.createGuide(
                id=guideId,
                parent="root",
                translate=list(position),
                rotate=orient,
                scale=scale,
                pivotShape="locator",
                shape=PRIMARY_GUIDE_SHAPE,
                color=CURVE_STARTEND_COLOR,
                pivotColor=[0.477, 1, 0.073],
                selectionChildHighlighting=self.component.configuration.selectionChildHighlighting,
                shapeTransform={
                    "translate": list(primaryPosOffsetVec + position),
                    "scale": list(shapeScale),
                    "rotate": [math.pi * 0.5, 0, 0],
                },
                attributes=[
                    {
                        "name": api.constants.MIRROR_BEHAVIOUR_ATTR,
                        "value": mayamath.MIRROR_SCALE,
                    },
                    {
                        "name": api.constants.AUTOALIGNAIMVECTOR_ATTR,
                        "value": [1.0, 0.0, 0.0],
                    },
                    {"name": api.constants.AUTOALIGNUPVECTOR_ATTR, "value": upVector},
                ],
            )
            firstGuide = guide
            guideLayerDef.createGuide(
                shape={},
                id=bindId,
                parent="root",
                translate=list(position),
                pivotShape="sphere",
                scale=DEFAULT_GUIDE_JNT_SCALE,
                rotate=orient,
                selectionChildHighlighting=self.component.configuration.selectionChildHighlighting,
            )

    def _createCtrlGuides(self, guideLayerDef, curveId, crvMfn, cvPositions, shapePositionOffset, **kwargs):
        ctrlColor = CURVE_COLOR_MAP[curveId]
        newGuides = []  # type: list[api.GuideDefinition]

        def _createCurveGuide(guideId, position, param, ctrlShape=TERTIARY_GUIDE_SHAPE):
            return _createGuideDef(
                guideLayerDef,
                guideId=guideId,
                parent="root",
                ctrlColor=ctrlColor,
                position=list(position),
                scale=list(DEFAULT_GUIDE_CTRL_SCALE),
                ctrlScale=list(DEFAULT_GUIDE_SHAPE_SCALE),
                ctrlRotation=(math.pi * 0.5, 0, 0),
                shape=ctrlShape,
                ctrlPosition=list(shapePositionOffset + position),
                **kwargs
            )

        # loop only the last half then will mirror the guides to create the right side.
        for index in six.moves.range(int((len(cvPositions) / 2)) + 1, len(cvPositions) - 1):
            cvPosition = cvPositions[index]
            guideId = self.guideCtrlIdForCurve(curveId, index - 1)
            cvPos, param = crvMfn.closestPoint(cvPosition, space=zapi.kWorldSpace)
            newGuides.append(_createCurveGuide(guideId, zapi.Vector(cvPos), param))

        _createCurveGuide(self.guideCtrlSecondaryIdForCurve(curveId, 1),
                          zapi.Vector(crvMfn.getPointAtParam(0.75, space=zapi.kWorldSpace)),
                          0.75,
                          SECONDARY_GUIDE_SHAPE)
        translation = zapi.Vector(crvMfn.getPointAtParam(0.25, space=zapi.kWorldSpace))
        _createGuideDef(
            guideLayerDef,
            guideId=self.guideCtrlSecondaryIdForCurve(curveId, 0),
            parent="root",
            ctrlColor=ctrlColor,
            position=list(translation),
            scale=DEFAULT_GUIDE_CTRL_SCALE,
            ctrlScale=list(DEFAULT_GUIDE_SHAPE_SCALE),
            ctrlRotation=(math.pi * 0.5, 0, 0),
            shape=SECONDARY_GUIDE_SHAPE,
            ctrlPosition=list(shapePositionOffset + translation),
            **kwargs
        )
        newGuides.reverse()
        # mirror the guides
        for index, leftGuide in enumerate(newGuides):
            guideId = self.guideCtrlIdForCurve(curveId, index)
            mirrorTransform = mayamath.mirrorMatrix(leftGuide.worldMatrix, translate=("x",),
                                                    rotate=mayamath.MIRROR_PLANE_BY_AXIS["x"],
                                                    mirrorFunction=mayamath.MIRROR_SCALE)

            translation = mirrorTransform.translation(zapi.kWorldSpace)
            _createGuideDef(
                guideLayerDef,
                guideId=guideId,
                parent="root",
                ctrlColor=ctrlColor,
                position=list(translation),
                scale=DEFAULT_GUIDE_CTRL_SCALE,
                ctrlScale=list(DEFAULT_GUIDE_SHAPE_SCALE),
                ctrlRotation=(math.pi * 0.5, 0, 0),
                shape=TERTIARY_GUIDE_SHAPE,
                ctrlPosition=list(shapePositionOffset + translation),
                **kwargs
            )
        # create the center guide
        halfIndex = int((len(cvPositions) / 2)) - 1
        cvPos = zapi.Vector(crvMfn.getPointAtParam(0.5, space=zapi.kWorldSpace))
        _createGuideDef(
            guideLayerDef,
            guideId=self.guideCtrlIdForCurve(curveId, halfIndex),
            parent="root",
            ctrlColor=ctrlColor,
            position=list(cvPos),
            scale=list(DEFAULT_GUIDE_CTRL_SCALE),
            ctrlScale=list(DEFAULT_GUIDE_SHAPE_SCALE),
            ctrlRotation=(math.pi * 0.5, 0, 0),
            shape=TERTIARY_GUIDE_SHAPE,
            ctrlPosition=list(shapePositionOffset + cvPos),
            **kwargs
        )

    def _createJointGuides(self, guideLayerDef, curve, curveId, count):
        self.component.logger.debug("Creating joint definitions")
        curveMfn = curve.mfn()
        curveLength = curveMfn.length()
        iterator = list(zoomath.lerpCount(0, 1.0, count))
        for index, param in enumerate(iterator):  # skip the first and last
            paramSetting = guideLayerDef.guideSetting(
                self.guideJntParamPosSettingName(curveId, index)
            )
            lengthParam = curveMfn.findParamFromLength(curveLength * paramSetting.value)
            pos = zapi.Vector(
                curveMfn.getPointAtParam(lengthParam, space=zapi.kWorldSpace)
            )
            guideLayerDef.createGuide(
                id=self.guideJointIdForCurve(curveId, index),
                parent="root",
                translate=list(pos),
                pivotShape="sphere",
                scale=DEFAULT_GUIDE_JNT_SCALE,
                selectionChildHighlighting=self.component.configuration.selectionChildHighlighting,
            )

    def _createGuideParamSettings(self, curveId, paramMultipliers, idGenerator):
        # creates definition settings for controlGuides and joints
        guideLayer = self.component.definition.guideLayer
        for i, param in enumerate(paramMultipliers):
            attrName = idGenerator(curveId, i)
            setting = definition.AttributeDefinition(
                name=attrName,
                Type=zapi.attrtypes.kMFnNumericFloat,
                value=param,
                default=param,
                keyable=False,
                channelBox=True,
            )
            guideLayer.addGuideSetting(setting)

    def _onGuideJointCountChanged(self, jointCount):
        guideLayer = self.component.guideLayer()
        guideLayerDef = self.component.definition.guideLayer
        existingGuideIds = self.guideJointIds()[1:-1]
        guideSettings = self.jointParamNames()

        guideLayerDef.deleteSettings(guideSettings)
        guideLayer.deleteGuides(*existingGuideIds)
        guideLayerDef.deleteGuides(*existingGuideIds)
        # ensure odd number so it's even on both sides of the curve + 1 for center
        self.jointCount = jointCount

        for curveId in (UPR_LIP_CURVE_ID, LWR_LIP_CURVE_ID):
            curveGuide = guideLayer.guide(curveId)
            if not curveGuide:
                continue
            shapeNode = curveGuide.shapeNode()
            self._createGuideParamSettings(
                curveId,
                list(zoomath.lerpCount(0, 1, self.jointCount + 2))[1:-1],
                self.guideJntParamPosSettingName,
            )
            self._createJointGuides(guideLayerDef, shapeNode.shapes()[0], curveId, self.jointCount)
        return True

    def _onGuideCtrlCountChanged(self, ctrlCount):
        guideLayer = self.component.guideLayer()
        guideLayerDef = self.component.definition.guideLayer
        existingGuideIds = []
        for curveId in (UPR_LIP_CURVE_ID, LWR_LIP_CURVE_ID):
            existingGuideIds.extend(self.guideCtrlIdsForCurve(curveId))
        guideLayer.deleteGuides(*existingGuideIds)
        guideLayerDef.deleteGuides(*existingGuideIds)

        rebuild = False
        shapePositionOffset = _guideShapeOffset()
        generalKwargs = {
            "selectionChildHighlighting": self.component.configuration.selectionChildHighlighting,
            "aimVector": (1.0, 0.0, 0.0),
            "upVector": (0.0, 1.0, 0.0),
        }
        self.ctrlCount = ctrlCount
        for curveId in (UPR_LIP_CURVE_ID, LWR_LIP_CURVE_ID):
            curveGuide = guideLayer.guide(curveId)
            if not curveGuide:
                continue
            rebuild = True
            curveShape = curveGuide.shapeNode()
            cmds.rebuildCurve(
                curveShape.fullPathName(),
                constructionHistory=False,
                replaceOriginal=True,
                rebuildType=0,
                endKnots=1,
                keepRange=0,
                keepControlPoints=0,
                keepEndPoints=1,
                keepTangents=0,
                spans=self.ctrlCount - 1,
                degree=3,
                tolerance=0.004,
            )
            shape = curveShape.shapes()[0]
            mfn = shape.mfn()
            self._createCtrlGuides(guideLayerDef,
                                   curveId,
                                   mfn,
                                   cvPositions=mfn.cvPositions(space=zapi.kWorldSpace),
                                   shapePositionOffset=shapePositionOffset, **generalKwargs)

        return rebuild

    def _skinGuideJoints(self, curveNode, guides):
        controlPoints = curveNode.controlPoints
        extras = []
        for index, guide in enumerate(guides):
            decomp = zapi.createDG("", "decomposeMatrix")
            guide.worldMatrixPlug().connect(decomp.inputMatrix)
            decomp.outputTranslate.connect(controlPoints[index])
            extras.append(decomp)
        self.component.guideLayer().addExtraNodes(extras)

    def _disconnectGuidesFromCurve(self, curveNode):
        for attr in curveNode.controlPoints:
            if attr.isConnected():
                attr.disconnectAll()

    def _bindTertiaryCtrlsToMask(self, rigLayer, uprSurfaceMask, lwrSurfaceMask,
                                 ctrls, parentSpace):
        lCtrlId = OUTER_L_PRIMARY_CTRL_ID
        rCtrlId = OUTER_R_PRIMARY_CTRL_ID
        topCtrId = self.guidePrimaryCtrlIdForCurve(UPR_LIP_CURVE_ID)
        botCtrId = self.guidePrimaryCtrlIdForCurve(LWR_LIP_CURVE_ID)

        uprGraphData = self.component.configuration.graphRegistry().graph(graphconstants.kMouthFourWayProxyPin)
        lwrGraphData = self.component.configuration.graphRegistry().graph(graphconstants.kLwrMouthFourWayProxyPin)

        uprCtrl = ctrls[topCtrId]
        lwrCtrl = ctrls[botCtrId]
        lCtrl = ctrls[lCtrlId]
        rCtrl = ctrls[rCtrlId]

        uprProxyGraph = self.createGraph(
            rigLayer,
            uprGraphData,
            suffix="upr"
        )
        proxyPin = uprProxyGraph.node("faceMaskProxy")
        parentWorldInvPlug = parentSpace.worldInverseMatrixPlug()
        uprSurfaceMask.shapes()[0].worldSpace[0].connect(proxyPin.deformedGeometry)
        uprProxyGraph.connectToInput("topLipWorldMatrix", uprCtrl.worldMatrixPlug())
        uprProxyGraph.connectToInput("topLipLocalMatrix", uprCtrl.attribute("matrix"))
        uprProxyGraph.connectToInput("outerRWorldMatrix", rCtrl.worldMatrixPlug())
        uprProxyGraph.connectToInput("outerRLocalMatrix", rCtrl.attribute("matrix"))
        uprProxyGraph.connectToInput("outerLLocalMatrix", lCtrl.attribute("matrix"))
        uprProxyGraph.connectToInput("outerLWorldMatrix", lCtrl.worldMatrixPlug())
        uprProxyGraph.connectToInput("parentWorldInverseMatrix", parentWorldInvPlug)
        uprProxyGraph.setInputAttr("offsetOrientation", 1)
        uprProxyGraph.setInputAttr("offsetTranslation", 0)
        uprProxyGraph.setInputAttr("tangentAxis", mayamath.YAXIS)
        uprProxyGraph.setInputAttr("normalAxis", mayamath.ZAXIS)
        uprProxyGraph.setInputAttr("coordMode", 1)  # uv mode

        lwrProxyGraph = self.createGraph(
            rigLayer,
            lwrGraphData,
            suffix="lwr"
        )
        proxyPin = lwrProxyGraph.node("faceMaskProxy")
        lwrSurfaceMask.shapes()[0].worldSpace[0].connect(proxyPin.deformedGeometry)
        lwrProxyGraph.connectToInput("lipWorldMatrix", lwrCtrl.worldMatrixPlug())
        lwrProxyGraph.connectToInput("lipLocalMatrix", lwrCtrl.attribute("matrix"))
        lwrProxyGraph.connectToInput("parentWorldInverseMatrix", parentWorldInvPlug)
        lwrProxyGraph.setInputAttr("offsetOrientation", 1)
        lwrProxyGraph.setInputAttr("offsetTranslation", 0)
        lwrProxyGraph.setInputAttr("tangentAxis", mayamath.YAXIS)
        lwrProxyGraph.setInputAttr("normalAxis", mayamath.ZAXIS)
        lwrProxyGraph.setInputAttr("coordMode", 1)  # uv mode
        return [uprProxyGraph, lwrProxyGraph]

    def _bindPrimariesToDrivers(self, rigLayer, upperLipIn, lowerLipIn, lwrSurfaceMask,
                                lCtrl, rCtrl, uprCtrl, lwrCtrl):
        blendAttr = rigLayer.controlPanel().attribute("lipsCornerBlender")
        namingCfg = self.component.namingConfiguration()
        compName, compSide = self.component.name(), self.component.side()
        extras = []
        driverNode = rigLayer.taggedNode(MAIN_CTRL_DRIVER_ID)
        if not driverNode:
            self.component.logger.warning("Missing main control driver node as a tag, unable to setup lip drivers")
            return
        _, utils = zapi.buildConstraint(lwrSurfaceMask,
                                        drivers={"targets": (("", lowerLipIn),)},
                                        maintainOffset=True,
                                        constraintType="matrix")
        extras.extend(utils)
        matrixAttr = driverNode.attribute("matrix")
        drivers = (upperLipIn, lowerLipIn)
        blendOutput = zapi.createDG(namingCfg.resolve(
            "object",
            {
                "componentName": compName, "side": compSide,
                "section": "cornerBlendLips", "type": "blendMatrix",
            }),
            "blendMatrix")

        firstDriver = drivers[0]
        firstDriver.worldMatrixPlug().connect(blendOutput.inputMatrix)
        # setup up targets
        for index, driver in enumerate(drivers[1:]):
            targetAttr = blendOutput.target[index]
            driver.worldMatrixPlug().connect(targetAttr.child(0))
            blendAttr.connect(targetAttr.child(2))
        blendOutput = blendOutput.outputMatrix
        extras.append(_matrixBlendConstraint(
            namingCfg,
            compName,
            compSide,
            rCtrl,
            matrixAttr,
            blendOutputAttr=blendOutput
        ))

        extras.append(_matrixBlendConstraint(
            namingCfg,
            compName,
            compSide,
            lCtrl,
            matrixAttr,
            blendOutputAttr=blendOutput
        ))
        extras.append(_matrixBlendConstraint(
            namingCfg,
            compName,
            compSide,
            uprCtrl,
            matrixAttr,
            blendOutputAttr=upperLipIn.worldMatrixPlug()
        ))
        extras.append(_matrixBlendConstraint(
            namingCfg,
            compName,
            compSide,
            lwrCtrl,
            matrixAttr,
            blendOutputAttr=lowerLipIn.worldMatrixPlug()
        ))
        rigLayer.addExtraNodes(extras)

    def _setLowresSkinWeights(self, curveShape, objects):
        skinCluster = zapi.SkinCluster()
        skinCluster.create("lowResSkinCluster", objects=objects + [curveShape],
                           maximumInfluences=3,
                           bindMethod=0, normalizeWeights=1, weightDistribution=0,
                           obeyMaxInfluences=True, removeUnusedInfluence=False,
                           toSelectedBones=True
                           )
        _setSkinWeights(skinCluster, curveShape, LOW_RES_CURVE_SKIN)

    def _setHighresSkinWeights(self, curveShape, objects):
        skin = zapi.SkinCluster()
        skin.create("highResSkinCluster", objects=objects + [curveShape],
                    maximumInfluences=1,
                    bindMethod=0, normalizeWeights=1, weightDistribution=0,
                    obeyMaxInfluences=True, removeUnusedInfluence=False,
                    toSelectedBones=True
                    )
        influenceWeights = [0.0] * len(objects)
        # object count == cv count so this is fine
        allWeights = []
        for index, obj in enumerate(objects):
            inflWeights = list(influenceWeights)
            inflWeights[index] = 1.0
            allWeights.append(inflWeights)
        _setSkinWeights(skin, curveShape, allWeights)

    def _setPushCurveSkinWeights(self, curveShape, objects, rootJnt):
        skin = zapi.SkinCluster()
        skin.create("pushSkinCluster", objects=[rootJnt] + objects + [curveShape],
                    maximumInfluences=1,
                    bindMethod=0, normalizeWeights=1, weightDistribution=0,
                    obeyMaxInfluences=True, removeUnusedInfluence=False,
                    toSelectedBones=True
                    )
        # 4 influences where 0 is the root joint which weights the first and last index as 1.0 to avoid
        # double transforms
        curveShapeMfn = curveShape.shapes()[0].mfn()
        cvCount = curveShapeMfn.numCVs
        allWeights = []
        halfIndex = int(cvCount / 2)
        centerWeights = [float(zoomath.round(i, 1)) for i in list(zoomath.lerpCount(0.0, 1.0, halfIndex + 1))]
        endWeights = list(reversed(centerWeights))
        firstSet = endWeights + [0.0] * halfIndex
        secondSet = centerWeights + endWeights[1:]
        thirdSet = [0.0] * halfIndex + centerWeights
        for weightIndex in six.moves.range(cvCount):
            weight = [0.0, 0.0, 0.0, 0.0]
            for index, weightSet in enumerate((firstSet, secondSet, thirdSet)):
                weight[index + 1] = weightSet[weightIndex]
            allWeights.append(weight)
        # weight to the root the first and last cv
        allWeights[0][0] = 1.0
        allWeights[0][1] = 0.0
        allWeights[-1][0] = 1.0
        allWeights[-1][-1] = 0.0
        _setSkinWeights(skin, curveShape, allWeights)

    def _bindJointsToCurve(self,
                           uprBuilder,
                           lwrBuilder,
                           ctrls,
                           rigLayer,
                           deformLayer,
                           controlPanel,
                           namingConfig,
                           extras):
        compName, compSide = self.component.name(), self.component.side()
        graphData = self.component.configuration.graphRegistry().graph(uprBuilder.jointRailOutGraphName)
        graphName = str(graphData.name)
        zipGraphs = self._createZipGraphs(rigLayer, controlPanel, namingConfig, compName, compSide)
        jointBlendGraphs = []
        for builder in (uprBuilder, lwrBuilder):
            curve = ctrls[builder._curveHighresSkinId]
            shape = curve.shapes()[0]
            jointIds = self.guideJointIdsForCurve(builder.curveDef.id)
            joints = deformLayer.findJoints(*jointIds)
            jntParamNames = self.jointParamNames(builder.curveDef.id)
            jntSettings = self.component.definition.guideLayer.guideSettings(*jntParamNames)

            lipRollAttr = controlPanel.attribute(builder._lipRollAttrName)

            remapRoll = zapi.createDG(namingConfig.resolve("object", {
                "componentName": compName,
                "side": compSide,
                "section": builder.curveDef.id + "Roll",
                "type": "remapValue"
            }),
                                      "remapValue")
            extras.append(remapRoll)
            remapRoll.inputMin.set(-10)
            remapRoll.outputMin.set(-90)
            remapRoll.inputMax.set(10)
            remapRoll.outputMax.set(90)
            remapRollOut = remapRoll.outValue
            # invert the lwr lip roll.
            if builder.curveDef.id == LWR_LIP_CURVE_ID:
                flipRoll = zapi.createDG(namingConfig.resolve("object", {
                    "componentName": compName,
                    "side": compSide,
                    "section": builder.curveDef.id + "InvertRoll",
                    "type": zapi.kMultDoubleLinearName
                }), zapi.kMultDoubleLinearName)
                lipRollAttr.connect(flipRoll.input1)
                flipRoll.input2.set(-1)
                flipRoll.output.connect(remapRoll.inputValue)
                extras.append(flipRoll)
            else:
                lipRollAttr.connect(remapRoll.inputValue)
            # pre config settings for lerping roll values from end to center
            perSideCount = int((len(joints) / 2))
            sideFraction = 1.0 / perSideCount
            lerpValues = list(zoomath.lerpCount(0.0, 1.0 - sideFraction, perSideCount))
            lerpIndex = 0
            curveJointGraphs = []
            for index, (paramName, jnt) in enumerate(zip(jntParamNames, joints)):
                jntPosSetting = jntSettings[paramName]
                if index == perSideCount:
                    lerpIndex = 0
                    lerpValues.reverse()
                    currentFraction = 0.9
                else:
                    currentFraction = lerpValues[lerpIndex]
                    lerpIndex += 1
                jntId = jnt.id()
                graphData.name = graphName + jntId
                guideDef = builder.guideDefs[jntId]
                sceneGraph = self.createGraph(
                    rigLayer,
                    graphData,
                    jntId
                )
                sceneGraph.connectToInput("parentWorldMatrix", builder.lipDriverPlug)
                sceneGraph.connectToInput("parentWorldInverseMatrix", builder.parentSpaceHrc.worldInverseMatrixPlug())
                sceneGraph.setInputAttr("motionWorldUpType", 2)
                sceneGraph.setInputAttr("motionUValue", jntPosSetting.value)
                mp = sceneGraph.node("motionPath")
                mp.fractionMode.set(False)
                shape.worldSpace[0].connect(mp.geometryPath)
                localOffset = jnt.worldMatrix() * sceneGraph.node("worldIn").outputMatrix.value().inverse()
                sceneGraph.setInputAttr("localOffset", localOffset)
                multRoll = zapi.createDG(namingConfig.resolve("object", {
                    "componentName": compName,
                    "side": compSide,
                    "section": builder.curveDef.id + "Roll",
                    "type": zapi.kMultDoubleLinearName
                }),
                                         zapi.kMultDoubleLinearName)
                remapRollOut.connect(multRoll.input1)
                rollInput = sceneGraph.inputAttr("lipRollRotation")[0][
                    mayamath.primaryAxisIndexFromVector(guideDef.aimVector())]
                multRoll.output.connect(rollInput)
                attr = builder.constantsNode.addAttribute(jnt.id() + "RollRotMultiplier",
                                                          Type=zapi.attrtypes.kMFnNumericFloat,
                                                          keyable=True, channelBox=False)
                attr.set(currentFraction)
                attr.connect(multRoll.input2)
                currentFraction += sideFraction
                extras.append(multRoll)
                curveJointGraphs.append((sceneGraph, jnt))
            jointBlendGraphs.append(curveJointGraphs)
        uprJntGraph, lwrJntGraph = jointBlendGraphs
        for index in six.moves.range(self.jointCount):
            uprGraph, uprJnt = uprJntGraph[index][0], uprJntGraph[index][1]
            lwrGraph, lwrJnt = lwrJntGraph[index][0], lwrJntGraph[index][1]
            uprDriverMatrixPlug, lwrDriverMatrixPlug = self._createZipperBlend(builder,
                                                                               uprGraph.outputAttr("worldMatrix"),
                                                                               lwrGraph.outputAttr("worldMatrix"),
                                                                               zipGraphs[index],
                                                                               namingConfig,
                                                                               compName,
                                                                               compSide,
                                                                               extras)

            _bindAimToCurve(self,
                            jointId=uprJnt.id(),
                            outJoint=uprJnt,
                            driverMatrixPlug=uprDriverMatrixPlug)
            _bindAimToCurve(self,
                            jointId=lwrJnt.id(),
                            outJoint=lwrJnt,
                            driverMatrixPlug=lwrDriverMatrixPlug)

        rCtrlId = self.outerLipCtrlPrefixId + "RBind"
        lCtrlId = self.outerLipCtrlPrefixId + "LBind"
        rJnt, lJnt = deformLayer.findJoints(rCtrlId, lCtrlId)
        _, utils = zapi.buildConstraint(rJnt,
                                        drivers={"targets": (("",
                                                              ctrls[
                                                                  OUTER_R_TERTIARY_CTRL_ID]),)},
                                        constraintType="matrix", maintainOffset=True, decompose=True)
        extras.extend(utils)
        _, utils = zapi.buildConstraint(lJnt,
                                        drivers={"targets": (("",
                                                              ctrls[
                                                                  OUTER_L_TERTIARY_CTRL_ID]),)},
                                        constraintType="matrix", maintainOffset=True, decompose=True)
        extras.extend(utils)

    def _createZipperBlend(self, builder,
                           uprWorldMatrixIn,
                           lwrWorldMatrixIn,
                           graph,
                           namingConfig,
                           compName,
                           compSide,
                           extras
                           ):
        graphOutputBlendNode = graph[1]
        lwrWorldMatrixIn.connect(graphOutputBlendNode.inputMatrix)
        uprWorldMatrixIn.connect(graphOutputBlendNode.target[0][0])
        graphOutputBlendNode.target[0][2].set(0.5)
        graphOutputBlendNode.target[0][3].set(0.0)
        graphOutputBlendNode.target[0][5].set(0.0)
        graphOutputBlendNode.target[0][6].set(0.0)
        outDriverPlugs = []
        for worldIn in (uprWorldMatrixIn, lwrWorldMatrixIn):
            zipBlender = zapi.createDG(namingConfig.resolve("object", {
                "componentName": compName,
                "side": compSide,
                "section": builder.curveDef.id + "Zipper",
                "type": "blendMatrix"
            }),
                                       "blendMatrix")
            zipOffset = zapi.createDG(namingConfig.resolve("object",
                                                           {
                                                               "componentName": compName,
                                                               "side": compSide,
                                                               "section": builder.curveDef.id + "zipOffset",
                                                               "type": "multMatrix",
                                                           }), "multMatrix")
            # connect upr/lwr blender to target
            zipOffset.matrixSum.connect(zipBlender.target[0][0])

            graphOutputBlendNode.outputMatrix.connect(zipOffset.matrixIn[1])
            worldIn.connect(zipBlender.inputMatrix)
            graph[0].connect(zipBlender.target[0][2])
            zipBlender.target[0][3].set(0.0)
            zipBlender.target[0][5].set(0.0)
            zipBlender.target[0][6].set(0.0)
            zipOffset.matrixIn[0].set(
                worldIn.value() * graphOutputBlendNode.outputMatrix.value().inverse())
            extras.extend((zipBlender, zipOffset))
            outDriverPlugs.append(zipBlender.outputMatrix)
        # return zipBlender.outputMatrix, (zipBlender, zipOffset)
        return outDriverPlugs


class LipBuilder(object):
    """
    :param system: The subsystem is being set up.
    :type system: :class:`MouthSubsystem`
    :param surfaceMask: The nurbsSurface mask for the lip.
    :type surfaceMask: :class:`zapi.DagNode`
    """

    def __init__(self,
                 system,
                 constantsNode,
                 surfaceMask,
                 curveDef,
                 ctrls,
                 guideDefs,
                 ctrlCount,
                 jointCount,
                 parentSpaceHrc,
                 extrasHrc,
                 lipDriverPlug,
                 rootTransform,
                 proxyPinNodeGraph,
                 parentPushJnt,
                 createEndCtrls=False,
                 ):
        self.constantsNode = constantsNode
        self.system = system
        self.surfaceMask = surfaceMask
        self.curveDef = curveDef
        self.ctrls = ctrls
        self.ctrlCount = ctrlCount
        self.jointCount = jointCount
        self.rootTransform = rootTransform
        self.lipDriverPlug = lipDriverPlug
        self.rootPushJnt = parentPushJnt
        self.extrasHrc = zapi.createDag(self.curveDef.id + "Extras", "transform", parent=extrasHrc)
        self.parentSpaceHrc = parentSpaceHrc
        self.proxyPinNodeGraph = proxyPinNodeGraph
        self.rigLayer = self.system.component.rigLayer()  # type: api.HiveRigLayer
        self.deformLayer = self.system.component.deformLayer()
        self.namingConfig = self.system.component.namingConfiguration()
        self.configuration = self.system.component.configuration
        self.controlPanel = self.rigLayer.controlPanel()
        self.guideDefs = guideDefs
        self.createEndCtrls = createEndCtrls
        self.curveHighSkinJoints = collections.OrderedDict()
        self.curveSurfaceFollowJoints = collections.OrderedDict()
        self.curveLowSkinJoints = collections.OrderedDict()
        self.curvePushJoints = []
        self.tertiaryCtrls = []
        # curve id for blendShape output
        self._curveShapeHighResId = self.curveDef.id + "Highres"
        # curve id for high res which follow surface
        self._curveSurfaceId = self.curveDef.id + "SurfaceHighres"
        # curve id for high res which is used to output skin joints
        self._curveHighresSkinId = self.curveDef.id + "Skin"
        # curve id for high res which pushes out from surface
        self._curvePuffId = self.curveDef.id + "Puff"
        # low res which output surface follow from 4 points
        self._curveLowResId = self.curveDef.id + "Lowres"
        self.jointRailOutGraphName = graphconstants.kBlendedJointRot
        self._lipRollAttrName = "uprLipRoll" if curveDef.id == UPR_LIP_CURVE_ID else "lwrLipRoll"
        self._invertTangent = False if curveDef.id == UPR_LIP_CURVE_ID else True
        self._extras = []

    def build(self):
        self.generateCurvesAndSurfaceMask()
        self._generateTertiaryCtrls()
        self._bindTertiaryCtrlsToLowResCurve()
        self._bindToSurfaceMask()
        # self._bindJointsToCurve()

    def generateCurvesAndSurfaceMask(self):
        compName, compSide = self.system.component.name(), self.system.component.side()
        lipCurveNode, _ = nodes.deserializeNode(self.curveDef, self.extrasHrc.object(), includeAttributes=False)
        curves.createCurveShape(lipCurveNode, self.curveDef.shape, space=zapi.kWorldSpace)
        highResCurveName = self.namingConfig.resolve("object", {
            "componentName": compName,
            "side": compSide,
            "section": self.curveDef.id + "HighRes",
            "type": "nurbsCurve"
        })

        lipCurveNode = zapi.nodeByObject(lipCurveNode)
        lipCurveNode.rename(highResCurveName)
        self.ctrls[self._curveShapeHighResId] = lipCurveNode
        self.rigLayer.addTaggedNode(lipCurveNode, self._curveShapeHighResId)
        # compute the lowres curve for the bind joints
        lowUprResCurve = cmds.rebuildCurve(
            lipCurveNode.fullPathName(),
            constructionHistory=False,
            replaceOriginal=False,
            rebuildType=0,
            endKnots=1,
            keepRange=0,
            keepControlPoints=0,
            keepEndPoints=1,
            keepTangents=0,
            spans=4,
            degree=3,
            tolerance=0.004,
        )
        lowResCurve = zapi.nodeByName(lowUprResCurve[0])
        lowResCurve.setParent(self.extrasHrc)
        lowResCurve.setShapeColour((0.073, 0.627, 1.0))
        self.ctrls[self._curveLowResId] = lowResCurve
        self.rigLayer.addTaggedNode(lowResCurve, self._curveLowResId)
        lowResCurveName = self.namingConfig.resolve("object", {
            "componentName": compName,
            "side": compSide,
            "section": self.curveDef.id + "LowRes",
            "type": "nurbsCurve"
        })

        lowResCurve.rename(lowResCurveName)

        curveNodes = [lipCurveNode, lowResCurve]
        for curveId in (self._curvePuffId, self._curveSurfaceId, self._curveHighresSkinId):
            curve = zapi.nodeByName(cmds.duplicate(lipCurveNode.fullPathName())[0])
            curve.setParent(self.extrasHrc)
            curve.setShapeColour((0.073, 0.627, 1.0))
            self.ctrls[curveId] = curve
            self.rigLayer.addTaggedNode(curve, curveId)
            curveName = self.namingConfig.resolve("object", {
                "componentName": compName,
                "side": compSide,
                "section": curveId,
                "type": "nurbsCurve"
            })
            curve.rename(curveName)
            curveNodes.append(curve)

        blendShape = zapi.nodeByName(cmds.blendShape(
            self.ctrls[self._curvePuffId].fullPathName(),
            self.ctrls[self._curveSurfaceId].fullPathName(),
            self.ctrls[self._curveShapeHighResId].fullPathName(),
            name=self.curveDef.id + "_BS"
        )[0])  # type: zapi.BlendShape
        blendShape.setTargetWeights([(0, 1.0), (1, 1.0)])
        self._extras.extend(curveNodes + [blendShape])
        self.controlPanel.attribute("showCurveTemplate").connect(curveNodes[-1].attribute("visibility"))
        curveNodes[-1].template.set(True)
        for curve in curveNodes[:-1]:
            curve.hide()
            curve.setLockStateOnAttributes(["visibility"], True)

    def _generateTertiaryCtrls(self):
        controlPanel = self.controlPanel
        leftPrimaryCtrl = self.ctrls[OUTER_L_PRIMARY_CTRL_ID]
        ctrPrimaryCtrl = self.ctrls[self.system.guidePrimaryCtrlIdForCurve(self.curveDef.id)]
        rightPrimaryCtrl = self.ctrls[OUTER_R_PRIMARY_CTRL_ID]

        halfCount = int((self.ctrlCount - 1) * 0.5)
        if self.curveDef.id == UPR_LIP_CURVE_ID:
            rollZMultAttr = controlPanel.attribute(LIPS_UPR_ZROLL_MULT_ATTR)
            rollYMultAttr = controlPanel.attribute(LIPS_UPR_YROLL_MULT_ATTR)
        else:
            rollZMultAttr = controlPanel.attribute(LIPS_LWR_ZROLL_MULT_ATTR)
            rollYMultAttr = controlPanel.attribute(LIPS_LWR_YROLL_MULT_ATTR)
        lipRollAttr = self.controlPanel.attribute(self._lipRollAttrName)
        pushAttr = ctrPrimaryCtrl.attribute("translate")[2]

        rollMultInvert = zapi.createDG(self.namingConfig.resolve("object",
                                                                 {
                                                                     "componentName": self.system.component.name(),
                                                                     "side": self.system.component.side(),
                                                                     "section": self.curveDef.id + "RollPosInvert",
                                                                     "type": "multiplyDivide"
                                                                 }),
                                       "multiplyDivide")
        rollMult = zapi.createDG(self.namingConfig.resolve("object",
                                                           {
                                                               "componentName": self.system.component.name(),
                                                               "side": self.system.component.side(),
                                                               "section": self.curveDef.id + "RollPosMultiplier",
                                                               "type": "multiplyDivide"
                                                           }),
                                 "multiplyDivide")
        rollSum = zapi.createDG(self.namingConfig.resolve("object",
                                                          {
                                                              "componentName": self.system.component.name(),
                                                              "side": self.system.component.side(),
                                                              "section": self.curveDef.id + "RollPosZMultiplier",
                                                              "type": "plusMinusAverage"
                                                          }),
                                "plusMinusAverage")
        # invert the roll multiplier
        rollZMultAttr.connect(rollMultInvert.input1X)
        rollYMultAttr.connect(rollMultInvert.input1Y)
        rollMultInvert.input2.set((-0.01, -0.01 if self.curveDef.id == UPR_LIP_CURVE_ID else 0.01, 0.0))

        lipRollAttr.connect(rollMult.input1X)
        lipRollAttr.connect(rollMult.input1Y)
        rollMultInvert.output.connect(rollMult.input2)
        # X is Z aim perpendicular axis
        rollMult.outputX.connect(rollSum.input1D[0])
        pushAttr.connect(rollSum.input1D[1])
        rollPrimaryPushAttr = rollSum.output1D
        rollUpPushAttr = rollMult.outputY
        secondaryCtrls = []
        for index in six.moves.range(2):
            guideId = self.system.guideCtrlSecondaryIdForCurve(self.curveDef.id, index)
            guideDef = self.guideDefs[guideId]
            scale = [1.0, 1.0, -1.0] if index == 0 else [1.0, 1.0, 1.0]
            ctrl = self.rigLayer.createControl(
                id=guideId,
                translate=guideDef.translate,
                rotate=guideDef.rotate,
                scale=scale,
                parent=self.parentSpaceHrc,
                rotateOrder=guideDef.rotateOrder,
                shape=guideDef.shape,
                selectionChildHighlighting=self.system.component.configuration.selectionChildHighlighting,
                srts=[{"name": guideId, "id": guideId},
                      ]
            )
            self.ctrls[guideId] = ctrl
            secondaryCtrls.append(ctrl)

        # create control curve guides for the lid and attach to the curve
        for index in six.moves.range(self.ctrlCount):
            negate = _requiresNegativeScale(index, self.ctrlCount)
            guideId = self.system.guideCtrlIdForCurve(self.curveDef.id, index)
            guideDef = self.guideDefs[guideId]
            scale = [1.0, 1.0, -1.0] if negate else [1.0, 1.0, 1.0]
            kwargs = dict(
                id=guideId,
                translate=guideDef.translate,
                rotate=guideDef.rotate,
                scale=scale,
                parent=self.parentSpaceHrc,
                rotateOrder=guideDef.rotateOrder,
                shape=guideDef.shape,
                selectionChildHighlighting=self.system.component.configuration.selectionChildHighlighting,
                srts=[{"name": guideId, "id": guideId},
                      ]
            )
            ctrIndex = index == halfCount
            if ctrIndex:
                kwargs["srts"].append({"name": guideId + "Push_srt", "id": guideId})
            ctrl = self.rigLayer.createControl(**kwargs)
            self.ctrls[guideId] = ctrl
            self.tertiaryCtrls.append(ctrl)
            # generate skinJoints for the highres curve
            jntId = guideId + "HighresJnt"
            jnt = self.rigLayer.createJoint(
                id=jntId,
                name=jntId,
                translate=guideDef.translate,
                rotate=guideDef.rotate
            )
            jnt.setParent(ctrl, maintainOffset=False)
            jnt.resetTransform()
            self.curveHighSkinJoints[jntId] = jnt
            if ctrIndex:
                jntId = guideId + "LowresJnt"
                jnt = self.rigLayer.createJoint(
                    id=jntId,
                    name=jntId,
                    translate=guideDef.translate,
                    rotate=guideDef.rotate
                )
                jnt.setParent(ctrl.srt(), maintainOffset=False)
                jnt.resetTransform()
                pushJnt = zapi.duplicate(jnt, name=guideId + "pushJnt",
                                         parent=self.rootPushJnt)
                pushJnt.resetTransformToOffsetParent()
                self.curveLowSkinJoints[jntId] = jnt
                self.curvePushJoints.append(pushJnt)
                pushAxis = guideDef.perpendicularVectorIndex()[0]
                upAxis = mayamath.primaryAxisIndexFromVector(guideDef.upVector())

                rollPrimaryPushAttr.connect(pushJnt.attribute("translate")[pushAxis])
                rollPrimaryPushAttr.connect(ctrl.srt(1).attribute("translate")[pushAxis])
                rollUpPushAttr.connect(pushJnt.attribute("translate")[upAxis])
                rollUpPushAttr.connect(ctrl.srt(1).attribute("translate")[upAxis])

        if self.createEndCtrls:
            primaryCtrls = (rightPrimaryCtrl, leftPrimaryCtrl)

            for index, (negate, guideId) in enumerate(zip((True, False),
                                                          (OUTER_R_TERTIARY_CTRL_ID,
                                                           OUTER_L_TERTIARY_CTRL_ID))):
                guideDef = self.guideDefs[guideId]
                scale = [1.0, 1.0, -1.0] if negate else [1.0, 1.0, 1.0]
                kwargs = dict(
                    id=guideId,
                    translate=guideDef.translate,
                    rotate=guideDef.rotate,
                    scale=scale,
                    parent=self.parentSpaceHrc,
                    rotateOrder=guideDef.rotateOrder,
                    shape=guideDef.shape,
                    selectionChildHighlighting=self.configuration.selectionChildHighlighting,
                    srts=[{"name": guideId + "Proxy_srt", "id": guideId},
                          {"name": guideId + "Push_srt", "id": guideId}]
                )
                ctrl = self.rigLayer.createControl(**kwargs)
                self.ctrls[guideId] = ctrl
                jnts = []
                count = 2
                for jntIndex, (guideSuffix, jntParent) in enumerate(zip(("HighresJnt", "LowresJnt", "pushJnt"),
                                                                        (ctrl, ctrl.srt(), self.rootPushJnt))):
                    jnt = self.rigLayer.createJoint(
                        id=guideId + guideSuffix,
                        name=guideId + guideSuffix,
                        translate=guideDef.translate,
                        rotate=guideDef.rotate,
                        scale=scale
                    )
                    jnts.append(jnt)
                    jnt.setParent(jntParent, maintainOffset=False)

                    if jntIndex != count:
                        jnt.resetTransform()
                    else:
                        jnt.setWorldMatrix(ctrl.worldMatrix())
                        jnt.resetTransformToOffsetParent()
                ctrl.rotate.connect(jnts[1].rotate)
                self.curveHighSkinJoints[jnts[0].id()] = jnts[0]
                self.curveLowSkinJoints[jnts[1].id()] = jnts[1]
                self.curvePushJoints.append(jnts[2])
                pushAxis = guideDef.perpendicularVectorIndex()[0]
                pushAttr = primaryCtrls[index].attribute("translate")[pushAxis]
                pushAttr.connect(jnts[2].attribute("translate")[pushAxis])
                pushAttr.connect(ctrl.srt(1).attribute("translate")[pushAxis])

    def _bindTertiaryCtrlsToLowResCurve(self):
        graphRegistry = self.system.component.configuration.graphRegistry()
        lowResGraphData = graphRegistry.graph(graphconstants.kMotionPathLipCtrl)
        highResGraphData = graphRegistry.graph(graphconstants.kMotionPathGuide)
        tertiaryPin = zapi.createDG(self.namingConfig.resolve("object",
                                                              {
                                                                  "componentName": self.system.component.name(),
                                                                  "side": self.system.component.side(),
                                                                  "section": self.curveDef.id + "tertiary",
                                                                  "type": "proximityPin"
                                                              }),
                                    "proximityPin")
        tertiaryPin.offsetOrientation.set(0.0)
        tertiaryPin.offsetTranslation.set(0.0)
        tertiaryPin.coordMode.set(1)  # uv
        tertiaryPin.normalAxis.set(2)  # Z up
        tertiaryPin.tangentAxis.set(1)  # Y up
        self.surfaceMask.shapes()[0].worldSpace[0].connect(tertiaryPin.deformedGeometry)

        graphLowName = str(lowResGraphData.name)
        graphHighName = str(highResGraphData.name)
        curveLowShape = self.ctrls[self._curveLowResId].shapes()[0]
        curveLowGeometryAttr = curveLowShape.worldSpace[0]
        curveHighShape = self.ctrls[self._curveShapeHighResId].shapes()[0]
        curveHighGeometryAttr = curveHighShape.worldSpace[0]
        ctrlPositions = self.system.component.definition.guideLayer.guideSetting(self.curveDef.id + "CtrlPositions")
        panel = self.rigLayer.controlPanel()
        rTangentAttr = panel.attribute("outerRTangent")
        lTangentAttr = panel.attribute("outerLTangent")

        posIndex = 0
        # split the lips curve ctrls into half, ignoring center ctrl
        # generate multidivide + compose matrix, outputting the compose matrix plug for each
        halfPoint = int((len(self.tertiaryCtrls)) * 0.5)
        rightSide = self.tertiaryCtrls[:halfPoint]
        rightSide.reverse()
        # skip first but connect the first ctrl to the second
        distributedSecondFractions = _distributeAlong3PointLinearCurve(halfPoint)
        # 0.0 is appended here to match the number of ctrls even though it's not used(center index)
        distributedSecondFractions += [0.0] + distributedSecondFractions
        secondaryCtrls = [self.ctrls[self.system.guideCtrlSecondaryIdForCurve(self.curveDef.id, 0)],
                          self.ctrls[self.system.guideCtrlSecondaryIdForCurve(self.curveDef.id, 1)]]
        secondaryCtrlIndex = 0
        for ctrl, param in zip(secondaryCtrls, (0.25, 0.75)):
            ctrlId = ctrl.id()
            srt = ctrl.srt()
            originalWorldMatrix = srt.worldMatrix()
            highResGraphData.name = graphHighName + ctrlId
            motionPathGraph = self.system.createGraph(
                self.rigLayer,
                highResGraphData,
                ctrlId
            )
            mp = motionPathGraph.node("curvePos")
            mp.fractionMode.set(False)
            curveHighGeometryAttr.connect(mp.geometryPath)
            motionPathGraph.setInputAttr("motionUValue", param)
            motionPathGraph.setInputAttr("motionWorldUpType", 2)
            motionPathGraph.connectToInput("parentWorldMatrix", self.lipDriverPlug)
            motionPathGraph.connectToInput("parentWorldInverseMatrix", self.parentSpaceHrc.worldInverseMatrixPlug())
            # compute local offset matrix
            ctrlWorldMat = ctrl.transformationMatrix()
            ctrlWorldMat.setScale([abs(i) for i in ctrlWorldMat.scale(zapi.kWorldSpace)], zapi.kWorldSpace)
            motionPathGraph.setInputAttr("localOffsetMatrix", ctrlWorldMat.asMatrix() * motionPathGraph.node(
                "aimTrs").outputMatrix.value().inverse())
            motionPathGraph.connectFromOutput("localMatrix", [srt.offsetParentMatrix])
            srt.setWorldMatrix(originalWorldMatrix)

        for index, tertiaryCtrl in enumerate(self.tertiaryCtrls):
            ctrlId = tertiaryCtrl.id()
            # skip binding the center ctrl to the curve because the proxyPin will do bind the ctrl later on
            if self.system._isIndexCenterTertiaryCtrl(index, self.ctrlCount):
                posIndex += 1
                secondaryCtrlIndex = 1
                continue
            srt = tertiaryCtrl.srt()
            originalWorldMatrix = srt.worldMatrix()
            param = ctrlPositions.value[posIndex]
            guideDef = self.guideDefs[ctrlId]

            surfaceJnt = self._bindSurfaceJntToLowCurve(lowResGraphData, graphLowName, tertiaryPin, index,
                                                        tertiaryCtrl, ctrlId, param, curveLowGeometryAttr)
            self.curveSurfaceFollowJoints[ctrlId] = surfaceJnt

            highResGraphData.name = graphHighName + ctrlId
            motionPathGraph = self.system.createGraph(
                self.rigLayer,
                highResGraphData,
                ctrlId
            )
            mp = motionPathGraph.node("curvePos")
            mp.fractionMode.set(False)
            curveHighGeometryAttr.connect(mp.geometryPath)
            motionPathGraph.setInputAttr("motionUValue", param)
            motionPathGraph.setInputAttr("motionWorldUpType", 2)
            motionPathGraph.connectToInput("parentWorldMatrix", self.lipDriverPlug)
            motionPathGraph.connectToInput("parentWorldInverseMatrix", self.parentSpaceHrc.worldInverseMatrixPlug())
            # compute local offset matrix
            ctrlWorldMat = tertiaryCtrl.transformationMatrix()
            ctrlWorldMat.setScale([abs(i) for i in ctrlWorldMat.scale(zapi.kWorldSpace)], zapi.kWorldSpace)
            motionPathGraph.setInputAttr("localOffsetMatrix", ctrlWorldMat.asMatrix() * motionPathGraph.node(
                "aimTrs").outputMatrix.value().inverse())
            # # handle tangent controls multipliers
            isTangentIndex = index in (0, self.ctrlCount - 1)

            if isTangentIndex:
                tertiaryLocalSum = zapi.createDG(self.namingConfig.resolve("object",
                                                                           {
                                                                               "componentName": self.system.component.name(),
                                                                               "side": self.system.component.side(),
                                                                               "section": self.curveDef.id + "localSum",
                                                                               "type": "multMatrix"
                                                                           }),
                                                 "multMatrix")
                compose = zapi.createDG(self.namingConfig.resolve("object",
                                                                  {
                                                                      "componentName": self.system.component.name(),
                                                                      "side": self.system.component.side(),
                                                                      "section": ctrlId + "Tangent",
                                                                      "type": "composeMatrix",
                                                                  }),
                                        "composeMatrix")
                tangentIn = lTangentAttr if index != 0 else rTangentAttr
                if self._invertTangent:
                    invertMut = zapi.createDG(self.namingConfig.resolve("object",
                                                                        {
                                                                            "componentName": self.system.component.name(),
                                                                            "side": self.system.component.side(),
                                                                            "section": ctrlId + "InvertTangent",
                                                                            "type": zapi.kMultDoubleLinearName,
                                                                        }),
                                              zapi.kMultDoubleLinearName)
                    invertMut.input2.set(-1.0)
                    tangentIn.connect(invertMut.input1)
                    tangentIn = invertMut.output
                    self._extras.append(invertMut)
                upVectorIndex = mayamath.primaryAxisIndexFromVector(guideDef.upVector())
                tangentIn.connect(compose.inputTranslate[upVectorIndex])
                compose.outputMatrix.connect(tertiaryLocalSum.matrixIn[0])
                motionPathGraph.outputAttr("localMatrix").connect(tertiaryLocalSum.matrixIn[1])
                tertiaryLocalSum.matrixSum.connect(srt.offsetParentMatrix)
                self._extras.extend((tertiaryLocalSum, compose))
            else:
                motionPathGraph.connectFromOutput("localMatrix", [srt.offsetParentMatrix])
            srt.setWorldMatrix(originalWorldMatrix)
            secondaryFraction = distributedSecondFractions[index]
            secCompose = zapi.createDG(self.namingConfig.resolve("object", {
                "componentName": self.system.component.name(),
                "side": self.system.component.side(),
                "section": ctrlId + "SecondaryOffset",
                "type": "composeMatrix"
            }), "composeMatrix")

            if secondaryFraction != 1.0:
                secMult = zapi.createDG(self.namingConfig.resolve("object", {
                    "componentName": self.system.component.name(),
                    "side": self.system.component.side(),
                    "section": ctrlId + "SecondaryOffset",
                    "type": "multiplyDivide"
                }), "multiplyDivide")
                secondaryCtrls[secondaryCtrlIndex].attribute("translate").connect(secMult.input1)
                secMult.input2.set(zapi.Vector(secondaryFraction, secondaryFraction, secondaryFraction))
                secMult.output.connect(secCompose.inputTranslate)
                self._extras.append(secMult)
            else:
                secondaryCtrls[secondaryCtrlIndex].attribute("translate").connect(secCompose.inputTranslate)
            self._extras.append(secCompose)
            secCompose.outputMatrix.connect(tertiaryCtrl.offsetParentMatrix)
            posIndex += 1

    def _bindSurfaceJntToLowCurve(self, graphData, graphName, tertiaryPin, index, tertiaryCtrl, ctrlId, param,
                                  geometryAttr):
        graphData.name = graphName + ctrlId
        motionPathGraph = self.system.createGraph(
            self.rigLayer,
            graphData,
            ctrlId
        )

        compName, compSide = self.system.component.name(), self.system.component.side()
        mp = motionPathGraph.node("motionPath")
        mp.fractionMode.set(False)
        geometryAttr.connect(mp.geometryPath)
        motionPathGraph.setInputAttr("motionUValue", param)
        motionPathGraph.setInputAttr("motionWorldUpType", 2)
        motionPathGraph.setInputAttr("motionWorldUpMatrix", self.parentSpaceHrc.worldMatrixPlug())

        motionPathGraph.connectFromOutput("outputWorldMatrix", [tertiaryPin.inputMatrix[index]])

        tertiaryLocalMtx = zapi.createDG(self.namingConfig.resolve("object",
                                                                   {
                                                                       "componentName": compName,
                                                                       "side": compSide,
                                                                       "section": self.curveDef.id + "TertiaryLocalMtx",
                                                                       "type": "composeMatrix"
                                                                   }),
                                         "multMatrix")
        surfaceJntOut = zapi.createDag(self.namingConfig.resolve("object",
                                                                 {
                                                                     "componentName": compName,
                                                                     "side": compSide,
                                                                     "section": ctrlId + "SurfaceFollow",
                                                                     "type": "joint"
                                                                 }),
                                       "joint")
        surfaceJntOut.setParent(self.parentSpaceHrc)
        surfaceJntOut.hide()
        surfaceJntOut.setLockStateOnAttributes(["visibility"], True)
        # compute local offset matrix
        pinExportAttr = tertiaryPin.outputMatrix[index]
        tertiaryLocalMtx.matrixIn[0].set(tertiaryCtrl.worldMatrix() * pinExportAttr.value().inverse())
        pinExportAttr.connect(tertiaryLocalMtx.matrixIn[1])

        self.parentSpaceHrc.worldInverseMatrixPlug().connect(tertiaryLocalMtx.matrixIn[2])
        tertiaryLocalMtx.matrixSum.connect(surfaceJntOut.offsetParentMatrix)
        surfaceJntOut.resetTransform()
        return surfaceJntOut

    def _bindToSurfaceMask(self):
        centerIndex = int((self.ctrlCount - 1) * 0.5)
        ctrCtrlId = self.system.guideCtrlIdForCurve(self.curveDef.id, centerIndex)
        rCtrl, lCtrl, ctrCtrl = [i.srt() for i in
                                 self.rigLayer.findControls(OUTER_R_TERTIARY_CTRL_ID, OUTER_L_TERTIARY_CTRL_ID,
                                                            ctrCtrlId)]
        proxyPinNode = self.proxyPinNodeGraph.node("faceMaskProxy")
        ctrWorld = ctrCtrl.worldMatrix()
        if self.createEndCtrls:
            outerLWorld = proxyPinNode.outputMatrix[0].value()
            outerRWorld = proxyPinNode.outputMatrix[2].value()
            self.proxyPinNodeGraph.setInputAttr("outerLRestPoseMatrix", lCtrl.worldMatrix() * outerLWorld.inverse())
            self.proxyPinNodeGraph.setInputAttr("outerRRestPoseMatrix", rCtrl.worldMatrix() * outerRWorld.inverse())
            self.proxyPinNodeGraph.connectFromOutput("outerLLocalMatrix", [lCtrl.offsetParentMatrix])
            self.proxyPinNodeGraph.connectFromOutput("outerRLocalMatrix", [rCtrl.offsetParentMatrix])
            lCtrl.resetTransform()
            rCtrl.resetTransform()
        if self.curveDef.id == UPR_LIP_CURVE_ID:
            topLipWorld = proxyPinNode.outputMatrix[1].value()
            self.proxyPinNodeGraph.setInputAttr("topLipRestPoseMatrix", ctrWorld * topLipWorld.inverse())
            self.proxyPinNodeGraph.connectFromOutput("topLipLocalMatrix", [ctrCtrl.offsetParentMatrix])
        else:
            botLipWorld = proxyPinNode.outputMatrix[0].value()
            self.proxyPinNodeGraph.setInputAttr("lipRestPoseMatrix", ctrWorld * botLipWorld.inverse())
            self.proxyPinNodeGraph.connectFromOutput("lipLocalMatrix", [ctrCtrl.offsetParentMatrix])
        ctrCtrl.resetTransform()


def _findClosestCtrls(param, ctrlParams):
    distances = [abs(param - ctrlParam) for ctrlParam in ctrlParams]
    minParam = min(distances)
    firstIndex = distances.index(minParam)
    newDistances = [i for i in distances if i != minParam]
    endIndex = distances.index(min(newDistances))

    return firstIndex, endIndex, abs(ctrlParams[firstIndex] - ctrlParams[endIndex])


def _createGuideDef(
        guideLayerDef,
        guideId,
        parent,
        ctrlColor,
        position,
        aimVector,
        upVector,
        scale=DEFAULT_GUIDE_CTRL_SCALE,
        ctrlScale=DEFAULT_GUIDE_SHAPE_SCALE,
        ctrlRotation=(math.pi * 0.5, 0, 0),
        shape=TERTIARY_GUIDE_SHAPE,
        rotation=(0, 0, 0, 1),
        selectionChildHighlighting=False,
        attributes=None,
        ctrlPosition=None
):
    """
    :rtype: :class:`api.GuideDefinition`
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
        scale=scale,
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


def _updateGuideCurve(curveId, curve, ctrlCount, duplicate=False):
    curve.rename(curveId)
    dup = cmds.rebuildCurve(
        curve.fullPathName(),
        constructionHistory=False,
        replaceOriginal=not duplicate,
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
    if dup:
        return zapi.nodeByName(dup[0])
    return curve


def _generateGuideCurve(curveId, positions):
    curve = zapi.nurbsCurveFromPoints(
        curveId, positions, shapeData={"form": 1, "degree": 3}
    )[0]
    return curve


def _requiresNegativeScale(index, count):
    return index < int((count - 1) / 2)


def _guideShapeOffset():
    return zapi.worldFrontAxis() * 0.5


def _bindGuideToCurve(system, guideLayer, guide, curve, param, invertAim=False):
    """
    :param system:
    :type system: :class:`MouthSubsystem`
    :param guide:
    :type guide: :class:`api.Guide`
    :param curve:
    :type curve: :class:`zapi.NurbsCurve`
    :param param:
    :type param:
    :return:
    :rtype:
    """
    currentWorldMat = guide.worldMatrix()
    guide.setLockStateOnAttributes(
        zapi.localTransformAttrs, False
    )
    root = guideLayer.guide("root")
    graphData = system.component.configuration.graphRegistry().graph(graphconstants.kMotionPathGuide)
    graphData.name += guide.id()
    graph = system.createGraph(
        guideLayer, graphData, guide.id()
    )
    curve.worldSpace[0].connect(graph.node("curvePos").geometryPath)
    if isinstance(param, zapi.Plug):
        graph.connectToInput("motionUValue", param)
    else:
        graph.setInputAttr("motionUValue", param)

    graph.connectToInput("parentWorldMatrix", root.worldMatrixPlug())
    graph.connectToInput("parentWorldInverseMatrix", root.worldInverseMatrixPlug())
    graph.setInputAttr("localOffsetMatrix", currentWorldMat * graph.node("aimTrs").outputMatrix.value().inverse())
    graph.connectFromOutput("localMatrix", [guide.offsetParentMatrix])
    transform = zapi.TransformationMatrix(currentWorldMat)
    transform.setScale((1, 1, 1), zapi.kWorldSpace)
    guide.resetTransform(scale=True)
    guide.setWorldMatrix(transform)
    return graph


def _bindAimToCurve(subsystem, jointId, outJoint, driverMatrixPlug):
    """

    :param subsystem:
    :type subsystem: :class:`MouthSubsystem`
    """
    jointParent = outJoint.parent()

    graph = subsystem.component.configuration.graphRegistry().graph("jointConstraint")
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


def _matrixBlendConstraint(namingCfg, compName, compSide, ctrl, localMatrixAttr, blendOutputAttr):
    drivenId = ctrl.id()
    drivenObj = ctrl.srt()
    drivenWorld = drivenObj.worldMatrix()
    # setup offset and transform into local space
    multOffset = zapi.createDG(namingCfg.resolve(
        "object",
        {
            "componentName": compName,
            "side": compSide,
            "section": drivenId + "LocalOffset",
            "type": "multMatrix",
        }), "multMatrix")
    parent = drivenObj.parent()
    parentInv = parent.worldInverseMatrixPlug()
    multOffset.matrixIn[0].set(drivenWorld * blendOutputAttr.value().inverse())
    localMatrixAttr.connect(multOffset.matrixIn[1])
    blendOutputAttr.connect(multOffset.matrixIn[2])
    parentInv.connect(multOffset.matrixIn[3])
    multOffset.matrixSum.connect(drivenObj.offsetParentMatrix)
    drivenObj.resetTransform()
    return multOffset


def _setSkinWeights(skin, curve, weightsData):
    """
    Sets the skin weights for a given curve using a skin cluster.

    :param skin: :class:`zapi.SkinCluster`, the skin cluster node.
    :param curve: :class:`zapi.NurbsCurve`, the curve shape node.
    :param weightsData: List[List[float]], weight values per CV for each influence.
    """
    mfnSkin = skin.mfn()
    # Get influence count and ensure dimensions match
    influences = mfnSkin.influenceObjects()
    numInfluences = len(influences)
    numCvs = len(weightsData)

    if any(len(w) != numInfluences for w in weightsData):
        raise ValueError("Each CV must have weights for all influences., Influence Count: {}".format(numInfluences))
    # Create CV component
    comp = om2.MFnSingleIndexedComponent()
    cvComp = comp.create(om2.MFn.kCurveCVComponent)
    comp.addElements(range(numCvs))

    # Flatten weight data into a single array
    weights = om2.MDoubleArray(numCvs * numInfluences, 0.0)
    for cvIdx, cvWeights in enumerate(weightsData):
        for infIdx, weight in enumerate(cvWeights):
            weights[cvIdx * numInfluences + infIdx] = weight

    # Set weights
    influenceIndices = om2.MIntArray(range(numInfluences))
    mfnSkin.setWeights(curve.dagPath(), cvComp, influenceIndices, weights, normalize=True)


def _distributeAlong3PointLinearCurve(count):
    """Generates a list of fractions for a 3 point linear curve where a count of
    3 returns [0.5, 1.0, 0.5]
    5 returns [0.25, 0.5, 1.0, 0.5, 0.25].
    7 returns [0.16, 0.33, 0.5, 1.0, 0.5, 0.33, 0.16].
    etc

    :param count:
    :type count: int
    :return:
    :rtype: list[float]
    """
    assert count >= 3, "Count must be at least 3"
    assert count % 2 == 1, "Count must be odd"
    primaryFraction = 1.0 / float(count - 1)
    currentFraction = 0.0
    halfCount = int(count * 0.5) + 1
    outputValues = [0.0] * halfCount
    for i in six.moves.range(halfCount):
        currentFraction += primaryFraction
        outputValues[i] = currentFraction

    outputValues = outputValues + list(reversed(outputValues[:-1]))
    outputValues[halfCount - 1] = 1.0
    return outputValues


def _setupPSDAims(primaryIds, rigLayer, deformLayer, namingConfig, compName, compSide):
    parentNode = deformLayer.taggedNode("parentSpaceIn")
    parentWorld = parentNode.worldMatrixPlug()
    parentWorldInv = parentNode.worldInverseMatrixPlug()
    extras = []
    controls = rigLayer.findControls(*primaryIds)
    visAttr = rigLayer.controlPanel().attribute("showBSDifferentiator")
    for index, primaryId in enumerate(primaryIds):
        psdId = primaryId + "PSD"
        psdNode = deformLayer.taggedNode(psdId)
        control = controls[index]
        if not control:
            continue
        mult = zapi.createDG(namingConfig.resolve("object", {
            "componentName": compName,
            "side": compSide,
            "section": psdId + "aimLocalOffset",
            "type": "multMatrix",
        }), "multMatrix")
        invMult = zapi.createDG(
            namingConfig.resolve(
                "object",
                {
                    "componentName": compName,
                    "side": compSide,
                    "section": psdId + "aimLocalInvOffset",
                    "type": "multMatrix",
                },
            ),
            "multMatrix",
        )
        aim = zapi.createDG(namingConfig.resolve("object", {
            "componentName": compName,
            "side": compSide,
            "section": psdId,
            "type": "aimMatrix",
        }), "aimMatrix")
        aim.primaryMode.set(1)
        aim.secondaryMode.set(1)
        aim.primaryInputAxis.set(zapi.Vector(0, 0, 1))
        aim.secondaryInputAxis.set(zapi.Vector(0, 1, 0))
        aim.secondaryTargetVector.set(zapi.Vector(1, 0, 0))
        decomp = zapi.createDG(
            namingConfig.resolve(
                "object",
                {
                    "componentName": compName,
                    "side": compSide,
                    "section": psdId,
                    "type": "decomposeMatrix",
                },
            ),
            "decomposeMatrix",
        )
        parentWorld.connect(aim.inputMatrix)
        control.worldMatrixPlug().connect(aim.primaryTargetMatrix)
        parentWorld.connect(aim.secondaryTargetMatrix)
        aim.outputMatrix.connect(mult.matrixIn[0])
        parentWorldInv.connect(mult.matrixIn[1])
        localMat = mult.matrixSum.value()
        mult.matrixSum.connect(invMult.matrixIn[0])
        invMult.matrixIn[1].set(localMat.inverse())
        psdNode.offsetParentMatrix.set(localMat)
        invMult.matrixSum.connect(decomp.inputMatrix)
        decomp.outputRotate.connect(psdNode.rotate)
        psdNode.attribute("translate").set(zapi.Vector())
        visAttr.connect(psdNode.visibility)
        extras.extend((mult, aim, invMult, decomp))
    rigLayer.addExtraNodes(extras)


def mirrorCvsLocal(cvPositions):
    """Mirrors the CVs (Control Vertices) of a given curve shape along the
    local X-axis.

    The function retains symmetry by flipping the
    displacement vector of each control point on one side of the curve,
    relative to the center, and applies the mirrored positions back
    to the curve.

    :param cvPositions: Curve cv positions.
    :type cvPositions: :class:`om2.MPoint`
    """
    # cvPositions = curveShape.cvPositions(zapi.kObjectSpace)

    centerPosition = zapi.Vector(cvPositions[int(len(cvPositions) / 2)])
    centerPosition[0] = 0
    newPositions = [centerPosition]
    for index in six.moves.range(int((len(cvPositions) / 2) + 1), len(cvPositions)):
        cvPosition = cvPositions[index]
        vec = zapi.Vector(cvPosition) - centerPosition
        vec[0] *= -1
        vec = centerPosition + vec
        newPositions.append(vec)
    newPositions.reverse()

    newPositions += [zapi.Vector(i) for i in cvPositions[int(len(cvPositions) / 2) + 1:]]
    return newPositions


def computeGuideMirrorScaleValue(worldMatrix):
    trans = zapi.TransformationMatrix(worldMatrix)
    scale = trans.scale(zapi.kWorldSpace)
    for index, var in enumerate(scale):
        scale[index] = abs(var)
    scale[0] *= -1.0
    trans.setScale(scale, zapi.kWorldSpace)
    return trans.asMatrix()


class GuideMapInfo:
    def __init__(self, aimVector=mayamath.XAXIS_VECTOR,
                 upVector=mayamath.YAXIS_VECTOR,
                 translation=zapi.Vector(),
                 scale=zapi.Vector(),
                 worldMatrix=zapi.Matrix()
                 ):
        self.aimVector = aimVector
        self.upVector = upVector
        self.translation = translation
        self.scale = scale
        self.worldMatrix = worldMatrix


def _gatherGuideAlignData(subsystem, inGuideMap, ctrlGuides):
    """

    :param subsystem:
    :type subsystem: :class:`MouthSubsystem`
    :param inGuideMap: matrix is the current computed guide matrix.
    :type inGuideMap: dict[str: :class:`GuideMapInfo`]
    :return:
    :rtype:
    """
    outInfo = {}
    # create plane which will be used to determine guide orientions
    rootGuideInfo = inGuideMap["root"]
    rootWorldBasis = mayamath.basisVectorsFromMatrix(rootGuideInfo.worldMatrix)
    rootPosition = rootGuideInfo.translation
    worldUpVector = rootWorldBasis[
        mayamath.primaryAxisIndexFromVector(rootGuideInfo.upVector)
    ].normal()
    worldAimVector = rootWorldBasis[
        mayamath.primaryAxisIndexFromVector(rootGuideInfo.aimVector)
    ].normal()
    orientPlane = zapi.Plane()
    orientPlane.setPlane(worldUpVector, -worldUpVector * rootPosition)

    for curveGuide, curveId in zip(ctrlGuides, [UPR_LIP_CURVE_ID, LWR_LIP_CURVE_ID]):
        if not curveGuide:
            continue
        shapeMfn = curveGuide.shapeNode().shapes()[0].mfn()
        centerPrimaryId = subsystem.guidePrimaryCtrlIdForCurve(curveId)
        centerPrimaryInfo = inGuideMap.get(centerPrimaryId)
        # figure out the orientation for the main lip curve
        centerPos = centerPrimaryInfo.translation
        centerWorld = zapi.TransformationMatrix(centerPrimaryInfo.worldMatrix)
        centerBasis = mayamath.basisVectorsFromMatrix(centerPrimaryInfo.worldMatrix)
        aimVector = (
                centerPos
                + centerBasis[
                    mayamath.primaryAxisIndexFromVector(centerPrimaryInfo.aimVector)
                ]
        )
        centerQuat = mayamath.lookAt(
            centerPos,
            aimVector,
            centerPrimaryInfo.aimVector,
            centerPrimaryInfo.upVector,
            worldUpVector=worldUpVector,
        )
        centerWorld.setRotation(centerQuat)
        outInfo[centerPrimaryId] = centerWorld.asMatrix()
        outInfo[subsystem.guideCtrlIdForCurve(curveId, int((subsystem.ctrlCount - 1) * 0.5))] = centerWorld.asMatrix()
        ctrlCount = subsystem.ctrlCount
        # loop the second half
        for index in six.moves.range(int(ctrlCount * 0.5)+1, ctrlCount):
            guideId = subsystem.guideCtrlIdForCurve(curveId, index)
            guideInfo = inGuideMap[guideId]
            worldMat = _computeCtrlAlignmentWorldMat(
                guideInfo,
                shapeMfn,
                orientPlane,
                worldUpVector,
                paramOffset=-0.05,
                aimVectorMult=-1.0,
            )
            outInfo[guideId] = worldMat
        # right side
        for index in six.moves.range(int((ctrlCount * 0.5))):
            guideId = subsystem.guideCtrlIdForCurve(curveId, index)
            guideInfo = inGuideMap[guideId]
            worldMat = _computeCtrlAlignmentWorldMat(
                guideInfo, shapeMfn,
                orientPlane,
                worldUpVector, paramOffset=0.05, aimVectorMult=1.0
            )
            worldMat = computeGuideMirrorScaleValue(worldMat)
            outInfo[guideId] = worldMat
        primarySecondaryGuidesToAlign = (
            subsystem.guideCtrlSecondaryIdForCurve(curveId, 1),
            OUTER_L_PRIMARY_CTRL_ID,
            OUTER_L_TERTIARY_CTRL_ID,
            subsystem.guideCtrlSecondaryIdForCurve(curveId, 0),
            OUTER_R_PRIMARY_CTRL_ID,
            OUTER_R_TERTIARY_CTRL_ID,
        )
        for negate, secondId in zip(
                (False, False, False, True, True, True), primarySecondaryGuidesToAlign
        ):
            guideInfo = inGuideMap.get(secondId)
            if guideInfo is None:
                continue
            param = 0.05 if negate else -0.05
            worldMat = _computeCtrlAlignmentWorldMat(
                guideInfo,
                shapeMfn,
                orientPlane,
                worldUpVector,
                paramOffset=param,
                aimVectorMult=1.0 if negate else -1.0
            )
            if negate:
                worldMat = computeGuideMirrorScaleValue(worldMat)
            outInfo[secondId] = worldMat
        jntsForCurve = subsystem.guideJointIdsForCurve(curveId)
        if curveId == UPR_LIP_CURVE_ID:
            jntsForCurve += [OUTER_L_BIND_ID, OUTER_R_BIND_ID]
        for jntId in jntsForCurve:
            worldMat = _computeJntAlignmentWorldMat(inGuideMap[jntId], shapeMfn, orientPlane,
                                                    worldUpVector, worldAimVector
                                                    )
            outInfo[jntId] = worldMat
    return outInfo


def _computeJntAlignmentWorldMat(
        targetGuideInfo, curveShapeMfn, orientPlane, worldUpVector, worldAimVector
):
    """Computes the worldMatrix quaternion for the guide by projecting the
    current guide pos and the closest point on curve + paramOffset on too the
    root guides upVector Plane allowing for a more stable orientation.

    :param targetGuideInfo:
    :type targetGuideInfo: :class:`GuideMapInfo`
    :param curveShapeMfn:
    :type curveShapeMfn: :class:`om2.MFnNurbsCurve`
    :return:
    :rtype:
    """
    currentPos = targetGuideInfo.translation
    closestPoint, param = curveShapeMfn.closestPoint(
        zapi.Point(currentPos), space=zapi.kWorldSpace
    )
    planeSourcePoint = mayamath.closestPointOnPlane(
        zapi.Vector(closestPoint), orientPlane
    )

    aimPosition = zapi.Vector(planeSourcePoint) + worldAimVector
    aimPosition = mayamath.closestPointOnPlane(
        zapi.Vector(aimPosition), orientPlane
    )

    worldTransform = zapi.TransformationMatrix(targetGuideInfo.worldMatrix)

    orient = mayamath.lookAt(
        zapi.Vector(planeSourcePoint),
        zapi.Vector(aimPosition),
        zapi.Vector(targetGuideInfo.aimVector),
        targetGuideInfo.upVector,
        worldUpVector=worldUpVector,
    )
    worldTransform.setTranslation(currentPos, zapi.kWorldSpace)
    worldTransform.setRotation(orient)
    return worldTransform.asMatrix()


def _computeCtrlAlignmentWorldMat(
        targetGuideInfo, curveShapeMfn, orientPlane, worldUpVector, paramOffset=1.05, aimVectorMult=1.0
):
    """Computes the worldMatrix quaternion for the guide by projecting the
    current guide pos and the closest point on curve + paramOffset on too the
    root guides upVector Plane allowing for a more stable orientation.

    :param targetGuideInfo:
    :type targetGuideInfo: :class:`GuideMapInfo`
    :param curveShapeMfn:
    :type curveShapeMfn: :class:`om2.MFnNurbsCurve`
    :param paramOffset:
    :type paramOffset: float
    :param aimVectorMult:
    :type aimVectorMult: float
    :return:
    :rtype:
    """
    currentPos = targetGuideInfo.translation
    closestPoint, param = curveShapeMfn.closestPoint(
        zapi.Point(currentPos), space=zapi.kWorldSpace
    )
    param = zoomath.clamp(round(param, 3), 0.0, 1.0) + paramOffset
    planeSourcePoint = mayamath.closestPointOnPlane(
        zapi.Vector(closestPoint), orientPlane
    )
    aimPosition = curveShapeMfn.getPointAtParam(param, space=zapi.kWorldSpace)
    aimPosition = mayamath.closestPointOnPlane(
        zapi.Vector(aimPosition), orientPlane
    )

    worldTransform = zapi.TransformationMatrix(targetGuideInfo.worldMatrix)

    orient = mayamath.lookAt(
        zapi.Vector(planeSourcePoint),
        zapi.Vector(aimPosition),
        zapi.Vector(targetGuideInfo.aimVector) * aimVectorMult,
        targetGuideInfo.upVector,
        worldUpVector=worldUpVector,
    )
    worldTransform.setTranslation(currentPos, zapi.kWorldSpace)
    worldTransform.setRotation(orient)
    return worldTransform.asMatrix()
