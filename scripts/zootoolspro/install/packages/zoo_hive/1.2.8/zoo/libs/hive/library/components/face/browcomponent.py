from collections import OrderedDict

from zoo.libs.hive import api
from zoo.libs.hive.library.subsystems import browsubsystem
from maya.api import OpenMaya as om2


class BrowComponent(api.Component):
    creator = "David Sparrow"
    description = "This component contains the Brow controls"
    definitionName = "browcomponent"
    uiData = {"icon": "hive", "iconColor": (), "displayName": "Brow"}
    betaVersion = False

    def idMapping(self):
        subsystems = self.subsystems()
        browSubsystem = subsystems["brow"]  # type: browsubsystem.BrowSubsystem
        jointIds = browSubsystem.guideJointIds()

        rigLayerIds = {i: i for i in browSubsystem._primaryCtrlIds}
        rigLayerIds.update({i: i for i in browSubsystem._secondaryCtrlIds + browSubsystem._tangentCtrlIds})
        rigLayerIds[browSubsystem.mainCtrlId] = browSubsystem.mainCtrlId
        rigLayerIds[browSubsystem.railsMainId] = browSubsystem.railsMainId
        deformIds = {i: i for i in jointIds}

        return {
            api.constants.DEFORM_LAYER_TYPE: deformIds,
            api.constants.INPUT_LAYER_TYPE: {},
            api.constants.OUTPUT_LAYER_TYPE: {},
            api.constants.RIG_LAYER_TYPE: rigLayerIds,
        }

    def createSubSystems(self):
        systems = OrderedDict()
        systems["brow"] = browsubsystem.BrowSubsystem(
            self,
            jointIdPrefix="bind",
            mainCtrlId="main",
            ctrlIds=["Inner", "InnerTweaker", "Mid", "Outer"],
            primaryCtrlIdPrefix="primary",
            secondaryCtrlIdPrefix="secondary",
            tangentCtrlIds=["tweakerTangentIn", "tweakerTangentOut", "midTangentIn", "midTangentOut", "outerTangentIn"],
            curveId="browCurve"
        )
        return systems

    def updateGuideSettings(self, settings):
        self.serializeFromScene(
            layerIds=(api.constants.GUIDE_LAYER_TYPE,)
        )  # ensure the definition contains the latest scene state.

        requiresRebuilds = []
        runPostUpdates = []
        for subSystem in self.subsystems().values():
            requiresRebuild, runPostUpdate = subSystem.preUpdateGuideSettings(settings)
            if requiresRebuild:
                requiresRebuilds.append(subSystem)
            if runPostUpdate:
                runPostUpdates.append(subSystem)
        original = super(BrowComponent, self).updateGuideSettings(settings)
        if requiresRebuilds:
            self.rig.buildGuides([self])

        for subSystem in runPostUpdates:
            subSystem.postUpdateGuideSettings(settings)
        return original

    def alignGuides(self):
        guides, matrices = [], []
        systems = list(self.subsystems().values())
        for system in systems:
            gui, mats = system.preAlignGuides()
            guides.extend(gui)
            matrices.extend(mats)
        if guides and matrices:
            api.setGuidesWorldMatrix(guides, matrices)
        for system in systems:
            system.postAlignGuides()

        return True

    def preMirror(self, translate=("x",), rotate="yz", parent=om2.MObject.kNullObj):
        if not self.hasGuide():
            return []
        for system in self.subsystems().values():
            system.preMirror(translate, rotate, parent)

    def postMirror(self, translate=("x",), rotate="yz", parent=om2.MObject.kNullObj):
        if not self.hasGuide():
            return []
        for system in self.subsystems().values():
            system.postMirror(translate, rotate, parent)

    def validateGuides(self, validationInfo):
        """
        :type validationInfo: :class:`errors.ValidationComponentInfo`
        """
        for subSystem in self.subsystems().values():
            if subSystem.active():
                success = subSystem.validateGuides(validationInfo)
                if not success:
                    return

    def preSetupGuide(self):
        for system in self.subsystems().values():
            system.preSetupGuide()
        super(BrowComponent, self).preSetupGuide()

    def setupGuide(self):
        for system in self.subsystems().values():
            system.setupGuide()

    def postSetupGuide(self):
        for system in self.subsystems().values():
            system.postSetupGuide()
        super(BrowComponent, self).postSetupGuide()

    def setupInputs(self):
        super(BrowComponent, self).setupInputs()
        for system in self.subsystems().values():
            system.setupInputs()

    def setupOutputs(self, parentNode):
        for system in self.subsystems().values():
            system.setupOutputs(parentNode)
        super(BrowComponent, self).setupOutputs(parentNode)

    def setupDeformLayer(self, parentNode=None):
        for system in self.subsystems().values():
            system.setupDeformLayer(parentNode)
        super(BrowComponent, self).setupDeformLayer(parentNode)

    def postSetupDeform(self, parentJoint):
        for system in self.subsystems().values():
            system.postSetupDeform(parentJoint)
        super(BrowComponent, self).postSetupDeform(parentJoint)

    def preSetupRig(self, parentNode):
        for system in self.subsystems().values():
            system.preSetupRig(parentNode)
        super(BrowComponent, self).preSetupRig(parentNode)

    def setupRig(self, parentNode):
        for system in self.subsystems().values():
            system.setupRig(parentNode)

    def postSetupRig(self, parentNode):
        for subSystem in self.subsystems().values():
            subSystem.postSetupRig(parentNode)

        super(BrowComponent, self).postSetupRig(parentNode)

    def applyGuideScaleSettings(self):
        for guide in self.guideLayer().iterGuides():
            if guide.id() == "root":

                globalScaleAttr = guide.attribute("scaleY")
                if globalScaleAttr.isLocked:
                    continue
                mfn = guide.mfn()
                guide.setLockStateOnAttributes(("scaleX", "scaleY", "scaleZ"), False)
                mfn.setAlias("globalScale", "scaleY", globalScaleAttr.plug())
                globalScaleAttr.connect(guide.attribute("scaleX"))
                globalScaleAttr.connect(guide.attribute("scaleZ"))
                guide.setLockStateOnAttributes(("scaleX", "scaleZ"), True)
                guide.showHideAttributes(("scaleX", "scaleZ"), False)
