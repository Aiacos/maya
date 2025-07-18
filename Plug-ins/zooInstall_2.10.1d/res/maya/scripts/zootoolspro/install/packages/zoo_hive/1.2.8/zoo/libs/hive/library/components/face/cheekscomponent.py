from collections import OrderedDict

from zoo.libs.hive import api
from zoo.libs.hive.library.subsystems import cheekssystem
from maya.api import OpenMaya as om2


class CheekComponent(api.Component):
    creator = "David Sparrow"
    description = "This component contains the Cheek controls"
    definitionName = "cheekcomponent"
    uiData = {"icon": "hive", "iconColor": (), "displayName": "Cheek"}
    betaVersion = True

    def idMapping(self):
        ids = ("cheek", "cheekBone", "nasolabial")
        mapped = {k: k for k in ids}
        return {
            api.constants.DEFORM_LAYER_TYPE: mapped,
            api.constants.INPUT_LAYER_TYPE: {},
            api.constants.OUTPUT_LAYER_TYPE: mapped,
            api.constants.RIG_LAYER_TYPE: mapped,
        }

    def createSubSystems(self):
        systems = OrderedDict()
        systems["cheeks"] = cheekssystem.CheekSubsystem(
            self
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
        original = super(CheekComponent, self).updateGuideSettings(settings)
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
        super(CheekComponent, self).preSetupGuide()

    def setupGuide(self):
        for system in self.subsystems().values():
            system.setupGuide()

    def postSetupGuide(self):
        for system in self.subsystems().values():
            system.postSetupGuide()
        super(CheekComponent, self).postSetupGuide()

    def setupInputs(self):
        super(CheekComponent, self).setupInputs()
        for system in self.subsystems().values():
            system.setupInputs()

    def setupOutputs(self, parentNode):
        for system in self.subsystems().values():
            system.setupOutputs(parentNode)
        super(CheekComponent, self).setupOutputs(parentNode)

    def setupDeformLayer(self, parentNode=None):
        for system in self.subsystems().values():
            system.setupDeformLayer(parentNode)
        super(CheekComponent, self).setupDeformLayer(parentNode)

    def postSetupDeform(self, parentJoint):
        for system in self.subsystems().values():
            system.postSetupDeform(parentJoint)
        super(CheekComponent, self).postSetupDeform(parentJoint)

    def preSetupRig(self, parentNode):
        for system in self.subsystems().values():
            system.preSetupRig(parentNode)
        super(CheekComponent, self).preSetupRig(parentNode)

    def setupRig(self, parentNode):
        for system in self.subsystems().values():
            system.setupRig(parentNode)

    def postSetupRig(self, parentNode):
        for subSystem in self.subsystems().values():
            subSystem.postSetupRig(parentNode)

        super(CheekComponent, self).postSetupRig(parentNode)

    def applyGuideScaleSettings(self):
        pass