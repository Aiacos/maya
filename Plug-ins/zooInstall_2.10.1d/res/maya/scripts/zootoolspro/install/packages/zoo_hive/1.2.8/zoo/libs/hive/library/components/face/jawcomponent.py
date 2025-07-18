from zoo.libs.hive import api
from zoo.libs.hive.base.serialization import graphconstants
from zoo.libs.maya import zapi
from zoo.libs.maya.cmds.rig import twists
from zoo.libs.maya.utils import mayamath
from zoo.libs.hive.base.util import componentutils

META_EXTRA_ATTR = "browDifferentiatorBSExtras"
BSDIFF_ATTR_NAMES = ["headTopLipRot", "botTopLipRot", "chinBotLipRot", "chinHeadRot"]
BSDIFF_TRANSLATE_ATTR_NAMES = ["headTopLipPos", "botTopLipPos", "chinBotLipPos", "chinHeadPos"]


class JawComponent(api.Component):
    creator = "DavidSparrow"
    description = "The Triple Jaw component which contains top lip, bottom lip and jaw"
    definitionName = "jaw"
    uiData = {
        "icon": "componentJaw",
        "iconColor": (),
        "displayName": "Jaw",
        "tooltip": description,
    }

    def idMapping(self):
        deformIds = {
            "topLip": "topLip",
            "jaw": "jaw",
            "chin": "chin",
            "botLip": "botLip",
        }
        outputIds = {
            "topLip": "topLip",
            "jaw": "jaw",
            "chin": "chin",
            "botLip": "botLip",
        }
        inputIds = {"jaw": "rootIn"}
        rigLayerIds = {
            "topLip": "topLip",
            "jaw": "jaw",
            "chin": "chin",
            "rotAll": "rotAll",
            "botLip": "botLip",
        }
        return {
            api.constants.DEFORM_LAYER_TYPE: deformIds,
            api.constants.INPUT_LAYER_TYPE: inputIds,
            api.constants.OUTPUT_LAYER_TYPE: outputIds,
            api.constants.RIG_LAYER_TYPE: rigLayerIds,
        }

    def lipGuides(self):
        guideLayer = self.guideLayer()
        if not guideLayer:
            return []
        return guideLayer.findGuides("topLip",
                                     "botLip")

    def spaceSwitchUIData(self):

        return {
            "driven": [
                api.SpaceSwitchUIDriven(
                    id_=api.pathAsDefExpression(("self", "rigLayer", "rotAll")),
                    label="Rotate All",
                ),
                api.SpaceSwitchUIDriven(
                    id_=api.pathAsDefExpression(("self", "rigLayer", "Jaw")),
                    label="Jaw",
                ),
                api.SpaceSwitchUIDriven(
                    id_=api.pathAsDefExpression(("self", "rigLayer", "topLip")),
                    label="Top Lip",
                ),
                api.SpaceSwitchUIDriven(
                    id_=api.pathAsDefExpression(("self", "rigLayer", "botLip")),
                    label="Bottom Lip",
                ),
                api.SpaceSwitchUIDriven(
                    id_=api.pathAsDefExpression(("self", "rigLayer", "chin")),
                    label="Chin",
                ),
            ],
            "drivers": [
                api.SpaceSwitchUIDriver(
                    id_=api.pathAsDefExpression(("self", "inputLayer", "root")),
                    label="Parent Component",
                    internal=True,
                ),
                api.SpaceSwitchUIDriver(
                    id_=api.pathAsDefExpression(("self", "rigLayer", "rotAll")),
                    label="Rotate All",
                ),
                api.SpaceSwitchUIDriver(
                    id_=api.pathAsDefExpression(("self", "rigLayer", "Jaw")),
                    label="Jaw",
                ),
                api.SpaceSwitchUIDriver(
                    id_=api.pathAsDefExpression(("self", "rigLayer", "topLip")),
                    label="Top Lip",
                ),
                api.SpaceSwitchUIDriver(
                    id_=api.pathAsDefExpression(("self", "rigLayer", "botLip")),
                    label="Bottom Lip",
                ),
                api.SpaceSwitchUIDriver(
                    id_=api.pathAsDefExpression(("self", "rigLayer", "chin")),
                    label="Chin",
                ),
            ],
        }

    def alignGuides(self):
        guideLayer = self.guideLayer()
        guidesToModify, matrices = [], []
        guides = {i.id(): i for i in guideLayer.iterGuides(includeRoot=True)}
        aimMapping = (
            (guides["jaw"], guides["chin"]),
            (guides["chin"], guides["jaw"]),
            (guides["topLip"], guides["jaw"]),
            (guides["botLip"], guides["jaw"]),
        )

        rootRotation = guides["root"].rotation(zapi.kWorldSpace, asQuaternion=True)
        for sourceGuide, targetGuide in aimMapping:
            if not sourceGuide.autoAlign.asBool():
                continue
            currentMatrix = sourceGuide.transformationMatrix()
            currentMatrix.setRotation(rootRotation)
            matrices.append(currentMatrix.asMatrix())
            guidesToModify.append(sourceGuide)
        if matrices:
            matrices.append(matrices[0])
            guidesToModify.append(guides["rotAll"])
            api.setGuidesWorldMatrix(guidesToModify, matrices)

    def setupInputs(self):
        super(JawComponent, self).setupInputs()
        inputLayer = self.inputLayer()
        guideDef = self.definition
        worldIn = inputLayer.inputNode("root")
        trans = guideDef.guideLayer.guide("jaw").transformationMatrix(scale=False)
        worldIn.setWorldMatrix(trans.asMatrix())

    def postSetupDeform(self, parentNode):
        deform = self.deformLayer()
        if self._createDifferentiator():
            self.createOutputBSNode(deform.rootTransform(), deform.joint("jaw"), deform)
        else:
            self._deleteDifferentiator()
        super(JawComponent, self).postSetupDeform(parentNode)

    def setupOutputs(self, parentNode):
        super(JawComponent, self).setupOutputs(parentNode)
        outputLayer = self.outputLayer()
        outputs = {i.id(): i for i in outputLayer.outputs()}
        jawWorld = self.definition.guideLayer.guide("jaw").transformationMatrix(scale=False).asMatrix()

        outputs["jaw"].setWorldMatrix(jawWorld)
        outputs["topLip"].setWorldMatrix(jawWorld)
        outputs["botLip"].resetTransform(jawWorld)
        outputs["chin"].resetTransform(jawWorld)

    def preSetupRig(self, parentNode):
        if not self._createDifferentiator():
            self.definition.rigLayer.deleteSettings(api.constants.CONTROL_PANEL_TYPE,
                                                    ("VISIBILITY", "showBSDifferentiator"))
            super(JawComponent, self).preSetupRig(parentNode)
            return
        self.definition.rigLayer.insertSettings(api.constants.CONTROL_PANEL_TYPE,
                                                self.definition.rigLayer.settingIndex(api.constants.CONTROL_PANEL_TYPE,
                                                                                      "autoTopLip") + 1,
                                                [
                                                    {
                                                        "channelBox": True,
                                                        "enums": [
                                                            "VISIBILITY"
                                                        ],
                                                        "isDynamic": True,
                                                        "keyable": False,
                                                        "locked": True,
                                                        "name": "___",
                                                        "Type": 12
                                                    },
                                                    {
                                                        "channelBox": True,
                                                        "default": False,
                                                        "keyable": False,
                                                        "locked": False,
                                                        "name": "showBSDifferentiator",
                                                        "Type": 0,
                                                        "value": False
                                                    }
                                                ]
                                                )

        super(JawComponent, self).preSetupRig(parentNode)

    def setupRig(self, parentNode):
        rigLayer = self.rigLayer()
        deformLayer = self.deformLayer()
        inputLayer = self.inputLayer()
        outputLayer = self.outputLayer()
        guideLayerDef = self.definition.guideLayer
        naming = self.namingConfiguration()
        outputs = {i.id(): i for i in outputLayer.outputs()}
        compName, compSide = self.name(), self.side()
        _ctrls = {}
        guides = {i.id: i for i in guideLayerDef.iterGuides(includeRoot=False)}
        controlTranslation = guides["jaw"].translate
        # bool is to ignore creating constraint which is handled in the Differentiator
        parentMap = (
            ("rotAll", "root", True),
            ("jaw", "rotAll", True),
            ("topLip", "rotAll", False),
            ("chin", "jaw", True),
            ("botLip", "jaw", True),
        )
        joints = deformLayer.findJoints(*[i[0] for i in parentMap])
        jointMap = {jnt.id(): jnt for jnt in joints if jnt is not None}
        for guideId, parent, createConst in parentMap:
            guidDef = guides[guideId]
            # create the control
            guidDef.name = naming.resolve(
                "controlName",
                {
                    "componentName": compName,
                    "side": compSide,
                    "id": guidDef.id,
                    "type": "control",
                },
            )
            ctrl = rigLayer.createControl(
                name=guidDef.name,
                id=guideId,
                rotateOrder=guidDef.get("rotateOrder", 0),
                translate=controlTranslation,
                rotate=guidDef.rotate,
                parent=parent,
                shape=guidDef.get("shape"),
                selectionChildHighlighting=self.configuration.selectionChildHighlighting
            )
            _ctrls[guideId] = ctrl
            jnt = jointMap.get(guideId)
            # jnt = deformLayer.joint(guideId)
            if not jnt or not createConst:
                continue

            const, constUtilities = api.buildConstraint(
                jnt,
                drivers={
                    "targets": (
                        (
                            ctrl.fullPathName(partialName=True, includeNamespace=False),
                            ctrl,
                        ),
                    )
                },
                constraintType="matrix",
                decompose=True,
                maintainOffset=True,
            )
            rigLayer.addExtraNodes(constUtilities)

        _ctrls["botLip"].attribute("matrix").connect(outputs["botLip"].offsetParentMatrix)
        _ctrls["chin"].attribute("matrix").connect(outputs["chin"].offsetParentMatrix)
        _ctrls["jaw"].worldMatrixPlug().connect(outputs["jaw"].offsetParentMatrix)
        outputs["botLip"].resetTransform()
        outputs["chin"].resetTransform()
        outputs["jaw"].resetTransform()

        self.setupBSDifferentiator()

        rootCtrl = _ctrls["rotAll"]
        # bind the root input node
        rootInput = inputLayer.inputNode("root")
        zapi.buildConstraint(
            rootCtrl,
            drivers={"targets": ((rootInput.name(includeNamespace=False), rootInput),)},
            maintainOffset=True,
            constraintType="matrix",
            trace=False,
        )

    def _createDifferentiator(self):
        return self.definition.guideLayer.guideSetting("createBSDifferentiator").value

    def _deleteDifferentiator(self):
        deformLayer = self.deformLayer()
        diffAttr, diffNode = self.differentiatorExtraNode(deformLayer)
        if not diffNode:
            return
        diffNode.delete()
        diffAttr.delete()

    def createLipsMovers(self, controlPanel, rigLayer, quaternionOutputXPlug, topLipCtrl, outputJoint,
                         topLipOutputNode):
        """Creates top lip mover as such that the top lip rotates up when total rotation off bot-lip and jaw
        is greater than 0.

        :param controlPanel: The controlPanel instance
        :type controlPanel: :class:`api.SettingsNode`
        :param rigLayer: The rigLayer instance
        :type rigLayer: :class:`api.HiveRigLayer`
        :param topLipCtrl: The top lip control
        :type topLipCtrl: :class:`api.ControlNode`
        """
        graphRegistry = self.configuration.graphRegistry()
        graphData = graphRegistry.graph(graphconstants.kJawMover)
        sceneGraph = componentutils.createGraphForComponent(
            self,
            rigLayer,
            graphData,
            track=True,
            sectionNameSuffix="",
            createIONodes=False
        )
        sceneGraph.connectToInput("topLipWorldMatrix",
                                  topLipCtrl.worldMatrixPlug())
        sceneGraph.connectToInput("botTopUpRotate",
                                  quaternionOutputXPlug)
        sceneGraph.connectToInput("valueMultiplier", controlPanel.attribute("autoTopLip"))
        sceneGraph.connectToInput("valueMin", controlPanel.attribute("topLipMoverOffset"))

        _, constUtilities = api.buildConstraint(
            outputJoint,
            drivers={"targets": (("",topLipCtrl,),)},
            constraintType="matrix",
            decompose=True,
            maintainOffset=True,
        )
        rigLayer.addExtraNodes(constUtilities)
        # find and cummulate the multMatrix inputPlugs we need to connect to from the constraint
        outputAttrs = [topLipOutputNode.offsetParentMatrix]
        for dest in topLipCtrl.worldMatrixPlug().destinations():
            node = dest.node()
            if node.apiType() == zapi.kNodeTypes.kMatrixMult and node in constUtilities:
                outputAttrs.append(dest)

        sceneGraph.connectFromOutput("outputMatrix", outputAttrs)
        topLipOutputNode.resetTransform()

    def setupBSDifferentiator(self):
        rigLayer = self.rigLayer()
        deformLayer = self.deformLayer()
        inputNode = self.inputLayer().inputNode("root")
        topLipOutputNode = self.outputLayer().outputNode("topLip")
        topLipJnt = deformLayer.joint("topLip")
        controls = {i.id(): i for i in rigLayer.findControls("rotAll", "topLip", "botLip", "chin", "jaw")}
        chinJoint = controls["chin"].fullPathName()
        topLipJoint = controls["topLip"].fullPathName()
        botLipJoint = controls["botLip"].fullPathName()
        outputQuat = None
        if self._createDifferentiator():
            outputNode = self.createOutputBSNode(deformLayer.rootTransform(),
                                                 deformLayer.joint("jaw"),
                                                 deformLayer)
            self.controlPanel().attribute("showBSDifferentiator").connect(outputNode.visibility)
            graphRegistry = self.rig.configuration.graphRegistry()
            dataGraphRep = graphRegistry.graph(graphconstants.kJawDifferentiatorBS)
            jawDiffPosGraph = componentutils.createGraphForComponent(
                self,
                rigLayer,
                dataGraphRep,
                track=True,
                sectionNameSuffix="",
                createIONodes=False
            )

            jawDiffPosGraph.connectToInput("topLipWorldMatrix", controls["topLip"].worldMatrixPlug())
            jawDiffPosGraph.connectToInput("botLipWorldMatrix", controls["botLip"].worldMatrixPlug())
            jawDiffPosGraph.connectToInput("chinWorldMatrix", controls["chin"].worldMatrixPlug())
            jawDiffPosGraph.connectToInput("rotAllWorldMatrix", controls["rotAll"].worldInverseMatrixPlug())
            jawDiffPosGraph.connectFromOutput("botTopLipPos", [outputNode.attribute("botTopLipPos")])
            jawDiffPosGraph.connectFromOutput("chinBotLipPos", [outputNode.attribute("chinBotLipPos")])
            jawDiffPosGraph.connectFromOutput("headTopLipPos", [outputNode.attribute("headTopLipPos")])
            jawDiffPosGraph.connectFromOutput("chinHeadPos", [outputNode.attribute("chinHeadPos")])

            parentNodeFullName = inputNode.fullPathName()

            for index, [inputNodeA, inputNodeB, setOutput] in enumerate(((topLipJoint, parentNodeFullName, False),
                                                                         (botLipJoint, topLipJoint, True),
                                                                         (chinJoint, botLipJoint, False),
                                                                         (parentNodeFullName, chinJoint, False))):
                rotAttrs = [BSDIFF_ATTR_NAMES[index] + axis for axis in mayamath.AXIS_NAMES]
                differentiator = twists.XyzRotDifferentiator(inputNode1=inputNodeA, inputNode2=inputNodeB,
                                                             outputNode=outputNode.fullPathName(),
                                                             attrs=rotAttrs)
                if setOutput:
                    outputQuat = zapi.nodeByName(differentiator.quatToEulerX).outputRotateX
                rigLayer.addExtraNodes(zapi.nodesByNames((differentiator.multMatrix,
                                                          differentiator.decomposeMatrix,
                                                          differentiator.quatToEulerX,
                                                          differentiator.quatToEulerY,
                                                          differentiator.quatToEulerZ)))
        else:
            inputNodeA, inputNodeB = botLipJoint, topLipJoint
            rotAttrs = [BSDIFF_ATTR_NAMES[1] + mayamath.AXIS_NAMES[0]]
            differentiator = twists.XyzRotDifferentiator(inputNode1=inputNodeA, inputNode2=inputNodeB,
                                                         attrs=rotAttrs)
            outputQuat = zapi.nodeByName(differentiator.quatToEulerX).outputRotateX
        self.createLipsMovers(self.controlPanel(),
                              rigLayer,
                              outputQuat,
                              controls["topLip"],
                              topLipJnt,
                              topLipOutputNode)

    def differentiatorExtraNode(self, layer):
        """
        :return:
        :rtype: tuple[:class:`zapi.Plug`, :class:`zapi.DagNode`]
        """
        extraAttr = layer.addAttribute(
            META_EXTRA_ATTR, Type=zapi.attrtypes.kMFnMessageAttribute, isFalse=True
        )
        return extraAttr, extraAttr.sourceNode()

    def createOutputBSNode(self, parent, worldDriver, layer):
        namingConfig = self.namingConfiguration()
        compName, compSide = self.name(), self.side()
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

        valueOutput.setParent(parent, maintainOffset=False)

        layer.addExtraNode(valueOutput)
        worldDriver.worldMatrixPlug().connect(valueOutput.offsetParentMatrix)
        valueOutput.message.connect(attr)
        for attrName in BSDIFF_ATTR_NAMES + BSDIFF_TRANSLATE_ATTR_NAMES:
            valueOutput.addAttribute(attrName, Type=zapi.attrtypes.kMFnNumeric3Float,
                                     channelBox=True, locked=False, keyable=False)
        attrs = [zapi.localRotateAttr, zapi.localScaleAttr]
        valueOutput.showHideAttributes(attrs, False)
        valueOutput.setLockStateOnAttributes(attrs, True)
        container = self.container()
        container.publishNode(valueOutput)
        return valueOutput

    def deformationJointIds(self, deformLayer, deformJoints):
        """Overridden to ignore the jaw.

        :param deformLayer: The deformLayer instance
        :type deformLayer: :class:`layers.HiveDeformLayer`
        :param deformJoints: The joint id to joint map.
        :type deformJoints: dict[str, :class:`hnodes.Joint`]
        """
        return [v for k, v in deformJoints.items() if k != "jaw"], [deformJoints.get("jaw")]
