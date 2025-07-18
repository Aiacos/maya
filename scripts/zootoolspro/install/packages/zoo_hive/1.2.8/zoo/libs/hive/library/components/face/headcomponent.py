import itertools
from collections import OrderedDict

from zoo.libs.hive import api
from zoo.libs.hive.library.subsystems import twistsubsystem
from zoo.libs.maya import zapi
from zoo.libs.maya.utils import mayamath


class HeadComponent(api.Component):
    creator = "David Sparrow"
    description = "This component contains the neck and head controls"
    definitionName = "headcomponent"
    uiData = {"icon": "head", "iconColor": (), "displayName": "Head"}

    def idMapping(self):
        deformIds = {"head": "head", "neck": "neck"}
        outputIds = {"head": "head", "neck": "neck"}
        inputIds = {"neck": "neck"}
        rigLayerIds = {"head": "head", "neck": "neck"}
        systems = self.subsystems()
        if systems["twists"].active():
            twistIds = systems["twists"].segmentTwistIds
            twistMapping = {k: k for k in itertools.chain(*twistIds)}
            deformIds.update(twistMapping)
            outputIds.update(twistMapping)
            rigLayerIds.update(twistMapping)
            rigLayerIds.update({k: k for k in systems["twists"].segmentTwistOffsetIds})
        return {
            api.constants.DEFORM_LAYER_TYPE: deformIds,
            api.constants.INPUT_LAYER_TYPE: inputIds,
            api.constants.OUTPUT_LAYER_TYPE: outputIds,
            api.constants.RIG_LAYER_TYPE: rigLayerIds,
        }

    def spaceSwitchUIData(self):

        drivers = [
            api.SpaceSwitchUIDriver(
                id_=api.pathAsDefExpression(("self", "inputLayer", "neck")),
                label="Parent Component",
                internal=True,
            ),
            api.SpaceSwitchUIDriver(
                id_=api.pathAsDefExpression(("self", "inputLayer", "world")),
                label="World Space",
                internal=True,
            ),
        ]
        driven = [
            api.SpaceSwitchUIDriven(
                id_=api.pathAsDefExpression(("self", "rigLayer", "head")), label="Head"
            ),
            api.SpaceSwitchUIDriven(
                id_=api.pathAsDefExpression(("self", "rigLayer", "neck")), label="Neck"
            ),
        ]
        drivers += [api.SpaceSwitchUIDriver(**i.serialize()) for i in driven]

        return {"driven": driven, "drivers": drivers}

    def createSubSystems(self):
        systems = OrderedDict()
        guideLayerDef = self.definition.guideLayer  # type: api.GuideLayerDefinition
        guideSettings = guideLayerDef.guideSettings("neckSegmentCount", "hasTwistRotation")
        twistSystem = twistsubsystem.TwistSubSystem(
            self,
            ["neck", "head"],
            rigDistributionStartIds=["neck"],
            segmentPrefixes=["neckTwist"],
            segmentCounts=[guideSettings["neckSegmentCount"].value],
            segmentSettingPrefixes=["neck"],
            twistReverseFractions=[False],
            buildTranslation=True,
            buildScale=True,
            floatingJoints=False,
            buildRotation=guideSettings["hasTwistRotation"].value
        )

        systems["twists"] = twistSystem
        return systems

    def twistIds(self, ignoreHasTwistsFlag=False):
        """Returns the internal hive ids for the twists.

        :param ignoreHasTwistsFlag: if True then we return a empty list for the upr and lwr /
        segments if there's hasTwists settings is False.

        :type ignoreHasTwistsFlag: bool
        :return:
        :rtype: list[list[str]]
        """
        twistSystem = self.subsystems().get("twists")
        if twistSystem is not None and twistSystem.active() or ignoreHasTwistsFlag:
            return twistSystem.segmentTwistIds
        return []

    def updateGuideSettings(self, settings):
        """Updates the vchain component which may require a rebuild.

        When any twist setting has changed we re-construct the twist guides from scratch.

        :todo: maintain existing twist guides to keep guide shape nodes.

        :param settings: The Guide setting name and the value to change.
        :type settings: dict[str, any]
        :return: Returns the the current settings on the definition before the change happened.
        :rtype: dict[str, any]
        """
        self.serializeFromScene(
            layerIds=(api.constants.GUIDE_LAYER_TYPE,)
        )  # ensure the definition contains the latest scene state.
        requiresRebuilds = []
        runPostUpdates = []
        # ensure the head is parented to the neck before update the twists just in
        # case deletion is called because the head is reparented to the top twist
        self.definition.deformLayer.setParentJoint("head", "neck")
        for subSystem in self.subsystems().values():
            requiresRebuild, runPostUpdate = subSystem.preUpdateGuideSettings(settings)
            if requiresRebuild:
                requiresRebuilds.append(subSystem)
            if runPostUpdate:
                runPostUpdates.append(subSystem)
        originalGuideSettings = super(HeadComponent, self).updateGuideSettings(settings)

        if requiresRebuilds:
            self.rig.buildGuides([self])

        for subSystem in runPostUpdates:
            subSystem.postUpdateGuideSettings(settings)

        return originalGuideSettings

    def preSetupGuide(self):
        for subSystem in self.subsystems().values():
            if subSystem.active():
                subSystem.preSetupGuide()
            else:
                subSystem.deleteGuides()

        super(HeadComponent, self).preSetupGuide()

    def setupGuide(self):
        super(HeadComponent, self).setupGuide()
        for subSystem in self.subsystems().values():
            if subSystem.active():
                subSystem.setupGuide()

    def postSetupGuide(self):
        for subSystem in self.subsystems().values():
            if subSystem.active():
                subSystem.postSetupGuide()

        super(HeadComponent, self).postSetupGuide()

    def validateGuides(self, validationInfo):
        """Called by UI or api on demand to validate the current state of the guides.
        If the component finds the state as invalid, the validationInfo object should be
        updated with a user error/warning message appended to it.

        :type validationInfo: :class:`api.ValidationInfo`
        """
        head = self.definition.deformLayer.joint("head")
        if not head:
            validationInfo.status = api.VALIDATION_ERROR
            validationInfo.message = ("Head Guide Meta data is Missing, This can occur due to an old bug "
                                      "in hive when toggling head twists on and off. Zoo version `2.9.4c+` "
                                      "Contains a fix for this, if this persists after an update please rebuild the "
                                      "Head Component and try again.")

    def alignGuides(self):
        systems = self.subsystems().values()
        head, neck = self.guideLayer().findGuides("head", "neck")  # type: api.Guide
        guides, matrices = [neck], []
        if neck.attribute(api.constants.AUTOALIGN_ATTR).value():
            neckRot = mayamath.lookAt(
                neck.translation(zapi.kWorldSpace),
                head.translation(zapi.kWorldSpace),
                head.attribute(api.constants.AUTOALIGNAIMVECTOR_ATTR).value(),
                head.attribute(api.constants.AUTOALIGNUPVECTOR_ATTR).value(),
            )
            transform = neck.transformationMatrix()
            transform.setRotation(neckRot)
            matrices.append(transform.asMatrix())
        else:
            matrices.append(neck.worldMatrix())

        for system in systems:
            gui, mats = system.preAlignGuides()
            guides.extend(gui)
            matrices.extend(mats)
        guides.append(head)
        if head.attribute(api.constants.AUTOALIGN_ATTR).value():
            headRot = mayamath.lookAt(
                head.translation(zapi.kWorldSpace),
                neck.translation(zapi.kWorldSpace),
                head.attribute(api.constants.AUTOALIGNAIMVECTOR_ATTR).value()*-1.0,
                head.attribute(api.constants.AUTOALIGNUPVECTOR_ATTR).value(),
            )
            transform = head.transformationMatrix()
            transform.setRotation(headRot)
            matrices.append(transform.asMatrix())
        else:
            matrices.append(head.worldMatrix())

        if guides and matrices:
            api.setGuidesWorldMatrix(guides, matrices)
        for system in systems:
            system.postAlignGuides()

        return True

    def setupInputs(self):
        super(HeadComponent, self).setupInputs()
        inputLayer = self.inputLayer()
        guideDef = self.definition
        worldIn, parentIn = inputLayer.findInputNodes("world", "neck")
        neckMat = guideDef.guideLayer.guide("neck").transformationMatrix(scale=False)
        neckMatrix = neckMat.asMatrix()
        parentIn.setWorldMatrix(neckMatrix)
        worldIn.setWorldMatrix(neckMatrix)

    def setupOutputs(self, parentNode):
        for subSystem in self.subsystems().values():
            if subSystem.active():
                subSystem.setupOutputs(parentNode)
        super(HeadComponent, self).setupOutputs(parentNode)
        # connect the outputs to deform layer
        layer = self.outputLayer()
        joints = {jnt.id(): jnt for jnt in self.deformLayer().joints()}
        for index, output in enumerate(layer.outputs()):
            driverJoint = joints.get(output.id())
            if not driverJoint:
                self.logger.warning("Missing joint: '{}', unable to build correctly, please "
                                    "rebuild the head component, this is likely due to an old bug".format(output.id()))
                continue
            # todo: fix matrix constraint not supporting constraining to driver which has a
            # different space to the driven.
            kwargs = {
                "driven": output,
                "drivers": {
                    "targets": (
                        (
                            driverJoint.fullPathName(
                                partialName=True, includeNamespace=False
                            ),
                            driverJoint,
                        ),
                    ),
                    "trace": True,
                },
            }
            if index == 0:
                const, constUtilities = api.buildConstraint(
                    constraintType="matrix", maintainOffset=False, **kwargs
                )
                layer.addExtraNodes(constUtilities)
            else:
                const, parentConstUtils = api.buildConstraint(
                    constraintType="parent", maintainOffset=False, **kwargs
                )
                const, scaleConstUtils = api.buildConstraint(
                    constraintType="scale", maintainOffset=False, **kwargs
                )
                layer.addExtraNodes(parentConstUtils + scaleConstUtils)

    def setupDeformLayer(self, parentNode=None):
        twists = self.twistIds(ignoreHasTwistsFlag=False)
        # ensure head is parented to the neck before head to ensure correct deletion
        # if needed
        deformLayer = self.definition.deformLayer
        if not deformLayer.setParentJoint("head", "neck"):
            self.logger.debug("Head or neck definition joint is missing or head and neck already parented")
        for subSystem in self.subsystems().values():
            subSystem.setupDeformLayer(parentNode)
        # post parent the head to the last twist
        if twists:
            deformLayer = self.definition.deformLayer
            deformLayer.setParentJoint("head", twists[0][-1])

        super(HeadComponent, self).setupDeformLayer(parentNode)

    def preSetupRig(self, parentNode):
        """Here we generate the constants node and attributes for the twists.

        Note: at this point no scene state is changed
        """
        for subSystem in self.subsystems().values():
            if subSystem.active():
                subSystem.preSetupRig(parentNode)

        super(HeadComponent, self).preSetupRig(parentNode)

    def setupRig(self, parentNode):
        inputLayer = self.inputLayer()
        rigLayer = self.rigLayer()
        definition = self.definition
        guideLayerDef = definition.guideLayer
        naming = self.namingConfiguration()
        compName, compSide = self.name(), self.side()
        # predefine nodes
        parentIn = inputLayer.inputNode("neck")
        ctrlRoot = zapi.createDag(
            naming.resolve(
                "object",
                {
                    "componentName": compName,
                    "side": compSide,
                    "section": "parentSpace",
                    "type": "srt",
                },
            ),
            "transform",
            parent=rigLayer.rootTransform(),
        )
        neckDef, headDef = guideLayerDef.findGuides("neck", "head")
        deformLayer = self.deformLayer()
        neckJnt, headJnt = deformLayer.findJoints("neck", "head")
        # related to the old bug(warnings above code in setupdeform etc) where deleting
        # twists would delete the head definition.
        if not neckJnt or not headJnt:
            return
        ctrlRoot.setWorldMatrix(neckDef.transformationMatrix(scale=False).asMatrix())
        rigLayer.addExtraNode(ctrlRoot)

        # bind the parent Space to the parent_in input
        const, constUtilities = zapi.buildConstraint(
            ctrlRoot,
            {
                "targets": (("", parentIn),),
            },
            constraintType="matrix",
            maintainOffset=True,
            trace=False,
        )
        rigLayer.addExtraNodes(constUtilities)

        # neck control
        neckDef.name = naming.resolve(
            "controlName",
            {
                "componentName": compName,
                "side": compSide,
                "id": neckDef.id,
                "type": "control",
            },
        )

        neckControl = rigLayer.createControl(
            name=neckDef.name,
            id=neckDef.id,
            rotateOrder=neckDef.get("rotateOrder", 0),
            translate=neckDef.get("translate", (0, 0, 0)),
            rotate=neckDef.get("rotate", (0, 0, 0, 1)),
            parent=ctrlRoot,
            shape=neckDef.get("shape"),
            selectionChildHighlighting=self.configuration.selectionChildHighlighting,
            srts=[{"id": neckDef.id, "name": "_".join([neckDef.name, "srt"])}],
        )
        # head control
        headDef.name = naming.resolve(
            "controlName",
            {
                "componentName": compName,
                "side": compSide,
                "id": headDef.id,
                "type": "control",
            },
        )
        headControl = rigLayer.createControl(
            name=headDef.name,
            id=headDef.id,
            rotateOrder=headDef.get("rotateOrder", 0),
            translate=headDef.get("translate", (0, 0, 0)),
            rotate=headDef.get("rotate", (0, 0, 0, 1)),
            parent=headDef.parent,
            shape=headDef.get("shape"),
            selectionChildHighlighting=self.configuration.selectionChildHighlighting,
            srts=[{"id": headDef.id, "name": "_".join([headDef.name, "srt"])}],
        )
        rigLayer.addTaggedNode(neckControl, "neck")
        rigLayer.addTaggedNode(headControl, "head")
        for subSystem in self.subsystems().values():
            subSystem.setupRig(parentNode)
        # bind the outputs to deform joints
        _buildConstraint(neckJnt, neckControl, rigLayer)
        _buildConstraint(headJnt, headControl, rigLayer)

    def deformationJointIds(self, deformLayer, deformJoints):
        """Overridden to ignore the jaw.

        :param deformLayer: The deformLayer instance
        :type deformLayer: :class:`layers.HiveDeformLayer`
        :param deformJoints: The joint id to joint map.
        :type deformJoints: dict[str, :class:`hnodes.Joint`]
        """
        settings = self.definition.guideLayer.guideSettings("hasTwists")
        nonSkin = []
        # when we have twist joints skip the upr/mid joints
        if settings["hasTwists"].value:
            ignoredSkinJoints = ("neck",)
            nonSkin.append(deformJoints.get("neck"))
            return [n for i, n in deformJoints.items() if i not in ignoredSkinJoints], nonSkin
        return list(deformJoints.values()), nonSkin


def _buildConstraint(driven, driver, rigLayer):
    _, constUtilities = api.buildConstraint(
        driven,
        drivers={"targets": (("", driver),)},
        constraintType="matrix",
        maintainOffset=True,
        decompose=True,
    )
    rigLayer.addExtraNodes(constUtilities)
