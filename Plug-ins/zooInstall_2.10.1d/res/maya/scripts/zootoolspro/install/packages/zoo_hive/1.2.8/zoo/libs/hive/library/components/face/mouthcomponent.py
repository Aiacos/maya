from collections import OrderedDict

from zoo.libs.hive import api
from zoo.libs.hive.library.subsystems import lipSystem
from maya.api import OpenMaya as om2


class MouthComponent(api.Component):
    creator = "David Sparrow"
    description = "This component contains the Mouth controls"
    definitionName = "mouthcomponent"
    uiData = {"icon": "hive", "iconColor": (), "displayName": "Mouth"}
    betaVersion = True

    def idMapping(self):
        subsystems = self.subsystems()
        mouthSystem = subsystems["lips"]  # type: lipSystem.MouthSubsystem
        jointIds = mouthSystem.guideJointIds()
        ctrlIds = (mouthSystem.guideCtrlIdsForCurve(lipSystem.UPR_LIP_CURVE_ID) +
                   mouthSystem.guideCtrlIdsForCurve(lipSystem.LWR_LIP_CURVE_ID) +
                   [lipSystem.OUTER_L_TERTIARY_CTRL_ID, lipSystem.OUTER_R_TERTIARY_CTRL_ID,
                    lipSystem.OUTER_L_PRIMARY_CTRL_ID, lipSystem.OUTER_R_PRIMARY_CTRL_ID,
                    mouthSystem.guidePrimaryCtrlIdForCurve(lipSystem.UPR_LIP_CURVE_ID),
                    mouthSystem.guidePrimaryCtrlIdForCurve(lipSystem.LWR_LIP_CURVE_ID)]
                   )
        rigLayerIds = {i: i for i in ctrlIds}
        deformIds = {i: i for i in jointIds}
        return {
            api.constants.DEFORM_LAYER_TYPE: deformIds,
            api.constants.INPUT_LAYER_TYPE: {},
            api.constants.OUTPUT_LAYER_TYPE: {},
            api.constants.RIG_LAYER_TYPE: rigLayerIds,
        }

    def createSubSystems(self):
        systems = OrderedDict()

        systems["lips"] = lipSystem.MouthSubsystem(
            self
        )

        return systems

    def driverGuides(self):
        return self.guideLayer().findGuides(lipSystem.OUTER_L_PRIMARY_CTRL_ID,
                                            lipSystem.OUTER_R_PRIMARY_CTRL_ID)

    def updateGuideSettings(self, settings):
        self.serializeFromScene(
            layerIds=(api.constants.GUIDE_LAYER_TYPE,)
        )  # ensure the definition contains the latest scene state.

        requiresRebuilds = []
        runPostUpdates = []
        for name, value in settings.items():
            if name in ("lipJointCount", "lipCtrlCount"):
                settings[name] = value + 1 if value % 2 == 0 else value
        for subSystem in self.subsystems().values():
            requiresRebuild, runPostUpdate = subSystem.preUpdateGuideSettings(settings)
            if requiresRebuild:
                requiresRebuilds.append(subSystem)
            if runPostUpdate:
                runPostUpdates.append(subSystem)

        original = super(MouthComponent, self).updateGuideSettings(settings)
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

    def applyGuideScaleSettings(self):
        pass

    def mirrorData(self, translate=("x",), rotate=None):
        """Overridden to handle Mirroring/symmetry of the M/Ctr component style. This
        Function redesigns the behaviour so it's localized and doesn't flip the component
        but instead mirrors the curves and transforms from left to right
        """
        name, side = self.name(), self.side()
        mirroredSide = self.namingConfiguration().field("sideSymmetry").valueForKey(side)
        oppositeComponent = self.rig.component(name, mirroredSide)
        if oppositeComponent:
            return super(MouthComponent, self).mirrorData(translate, rotate)
        mirrorDat = {}

        for system in self.subsystems().values():
            mirrorDat.update(system.mirrorData(translate, rotate))
        if mirrorDat:
            mirrorDat["opposite"] = self
        return mirrorDat

    def preMirror(self, translate=("x",), rotate="yz", parent=om2.MObject.kNullObj):
        if not self.hasGuide():
            return
        for system in self.subsystems().values():
            system.preMirror(translate, rotate, parent)

    def postMirror(self, translate=("x",), rotate="yz", parent=om2.MObject.kNullObj):
        if not self.hasGuide():
            return
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
        super(MouthComponent, self).preSetupGuide()

    def setupGuide(self):
        for system in self.subsystems().values():
            system.setupGuide()

    def postSetupGuide(self):
        for system in self.subsystems().values():
            system.postSetupGuide()
        super(MouthComponent, self).postSetupGuide()

    def setupInputs(self):
        super(MouthComponent, self).setupInputs()
        for system in self.subsystems().values():
            system.setupInputs()

    def setupOutputs(self, parentNode):
        for system in self.subsystems().values():
            system.setupOutputs(parentNode)
        super(MouthComponent, self).setupOutputs(parentNode)

    def setupDeformLayer(self, parentNode=None):
        for system in self.subsystems().values():
            system.setupDeformLayer(parentNode)
        super(MouthComponent, self).setupDeformLayer(parentNode)

    def postSetupDeform(self, parentJoint):
        for system in self.subsystems().values():
            system.postSetupDeform(parentJoint)
        super(MouthComponent, self).postSetupDeform(parentJoint)

    def postDeformDriverSetup(self, parentNode):
        lips = self.subsystems()["lips"]
        if lips.active():
            lips.postDeformDriverSetup(parentNode)

    def preSetupRig(self, parentNode):
        for system in self.subsystems().values():
            system.preSetupRig(parentNode)
        super(MouthComponent, self).preSetupRig(parentNode)

    def setupRig(self, parentNode):
        for system in self.subsystems().values():
            system.setupRig(parentNode)

    def postSetupRig(self, parentNode):
        for subSystem in self.subsystems().values():
            subSystem.postSetupRig(parentNode)

        super(MouthComponent, self).postSetupRig(parentNode)

    def deleteRig(self):
        # get the mouth PSD nodes and disconnect the transforms to avoid unwanted
        # propagation of values when deleting extra math nodes in random orders
        systems = self.subsystems()
        lips = systems["lips"]
        if not lips.active():
            super(MouthComponent, self).deleteRig()
            return
        ids = (
            lipSystem.OUTER_L_PRIMARY_CTRL_ID,
            lipSystem.OUTER_R_PRIMARY_CTRL_ID,
            lips.guidePrimaryCtrlIdForCurve(lipSystem.UPR_LIP_CURVE_ID),
            lips.guidePrimaryCtrlIdForCurve(lipSystem.LWR_LIP_CURVE_ID),
        )
        deformLayer = self.deformLayer()
        if not deformLayer:
            super(MouthComponent, self).deleteRig()
            return
        for primaryId in ids:
            psdId = primaryId + "PSD"

            psdNode = deformLayer.taggedNode(psdId)
            if not psdNode:
                continue
            rotSource = psdNode.rotate.source()
            if rotSource:
                rotSource.disconnect(psdNode.rotate)
        super(MouthComponent, self).deleteRig()
