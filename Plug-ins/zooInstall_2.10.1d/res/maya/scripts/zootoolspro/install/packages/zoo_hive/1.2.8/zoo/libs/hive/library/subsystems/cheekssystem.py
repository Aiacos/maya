from zoo.libs.hive.base.serialization import graphconstants
from zoo.libs.maya import zapi
from zoo.libs.maya.utils import mayamath
from zoo.libs.hive import api
from zoo.libs.hive.base import basesubsystem

CHEEK_GUIDE_ID = "cheek"
CHEEK_BONE_GUIDE_ID = "cheekBone"
CHEEK_NASOLABIAL_GUIDE_ID = "nasolabial"


class CheekSubsystem(basesubsystem.BaseSubsystem):
    """
    :param component: The component associated with this subsystem.
    :type component: :class:`zoo.libs.hive.base.component.Component`
    """

    def __init__(
            self,
            component
    ):
        super(CheekSubsystem, self).__init__(component)

    def preSetupRig(self, parentNode):
        rigLayerDef = self.component.definition.rigLayer
        defaultAttrValues = ((0.1, 0.0, 0.0), (0.0, 0.3, 0.0), (0.0, 0.0, 0.3))
        attrs = []
        for guideIdx, guideId in enumerate((CHEEK_GUIDE_ID,
                                            CHEEK_BONE_GUIDE_ID,
                                            CHEEK_NASOLABIAL_GUIDE_ID)):
            for index, axis in enumerate(mayamath.AXIS_NAMES):
                defaultValue = defaultAttrValues[index]
                attrs.append({"name": guideId + "Multiplier{}X".format(axis),
                              "default": defaultValue[0],
                              "channelBox": False,
                              "keyable": True,
                              "min": 0})
                attrs.append({"name": guideId + "Multiplier{}Y".format(axis),
                              "default": defaultValue[1],
                              "channelBox": False,
                              "keyable": True,
                              "min": 0})
                attrs.append({"name": guideId + "Multiplier{}Z".format(axis),
                              "default": defaultValue[2],
                              "channelBox": False,
                              "keyable": True,
                              "min": 0})
        rigLayerDef.addSettings(api.constants.CONTROL_PANEL_TYPE, attrs)

    def setupRig(self, parentNode):

        rigLayer = self.component.rigLayer()
        controlPanel = rigLayer.controlPanel()
        inputLayer = self.component.inputLayer()
        naming = self.component.namingConfiguration()
        graphRegistry = self.component.configuration.graphRegistry()
        localTGraphData = graphRegistry.graph(graphconstants.kCheekLocalMultiplier)
        localTGraphName = localTGraphData.name
        compName, compSide = self.component.name(), self.component.side()
        guideDefs = self.component.definition.guideLayer.findGuides(CHEEK_GUIDE_ID,
                                                                    CHEEK_BONE_GUIDE_ID,
                                                                    CHEEK_NASOLABIAL_GUIDE_ID)
        rigLayerRoot = rigLayer.rootTransform()
        inputLayerRootInput = inputLayer.rootInput()
        inputLayerRootInput.setWorldMatrix(parentNode.worldMatrix())
        parentSpace = api.componentutils.createParentSpaceTransform(
            naming, compName, compSide, rigLayerRoot, rigLayerRoot, rigLayer, inputLayerRootInput,
            maintainOffset=False
        )
        localInAttr = inputLayer.attribute("lipCornerLocalTranslate")

        for index, guidDef in enumerate(
                guideDefs
        ):
            ctrlName = naming.resolve(
                "controlName",
                {
                    "componentName": compName,
                    "side": compSide,
                    "id": guidDef.id,
                    "type": "control",
                },
            )
            ctrl = rigLayer.createControl(
                name=ctrlName,
                id=guidDef.id,
                translate=guidDef.translate,
                rotate=guidDef.rotate,
                scale=guidDef.mirrorScaleVector()[0],
                shape=guidDef.shape,
                rotateOrder=guidDef.rotateOrder,
                selectionChildHighlighting=self.component.configuration.selectionChildHighlighting,
                parent=parentSpace,
                srts=[{"name": ctrlName + "_srt", "id": guidDef.id}]
            )
            srt = ctrl.srt()
            srt.resetTransformToOffsetParent()
            localTGraphData.name = localTGraphName + guidDef.id
            sceneGraph = self.createGraph(rigLayer, localTGraphData)
            sceneGraph.connectToInput("localTranslateX", localInAttr[0])
            sceneGraph.connectToInput("localTranslateY", localInAttr[1])
            sceneGraph.connectToInput("localTranslateZ", localInAttr[2])
            xMultAttr = sceneGraph.inputAttr("localTranslateXMultiplier")[0]
            yMultAttr = sceneGraph.inputAttr("localTranslateYMultiplier")[0]
            zMultAttr = sceneGraph.inputAttr("localTranslateZMultiplier")[0]
            for graphAttr, axisName in zip((xMultAttr, yMultAttr, zMultAttr), mayamath.AXIS_NAMES):
                inXAttr = controlPanel.attribute(guidDef.id + "Multiplier{}X".format(axisName))
                inYAttr = controlPanel.attribute(guidDef.id + "Multiplier{}Y".format(axisName))
                inZAttr = controlPanel.attribute(guidDef.id + "Multiplier{}Z".format(axisName))
                inXAttr.connect(graphAttr[0])
                inYAttr.connect(graphAttr[1])
                inZAttr.connect(graphAttr[2])
            sceneGraph.connectFromOutput("localTranslate", [srt.attribute("translate")])

    def postSetupRig(self, parentNode):
        deformLayer = self.component.deformLayer()
        rigLayer = self.component.rigLayer()
        controls = rigLayer.findControls(CHEEK_GUIDE_ID, CHEEK_BONE_GUIDE_ID, CHEEK_NASOLABIAL_GUIDE_ID)
        joints = deformLayer.findJoints(CHEEK_GUIDE_ID, CHEEK_BONE_GUIDE_ID, CHEEK_NASOLABIAL_GUIDE_ID)

        for ctrl, jnt in zip(controls, joints):
            zapi.buildConstraint(
                jnt,
                drivers={"targets": (("", ctrl),)},
                constraintType="matrix",
                maintainOffset=True,
                decompose=True
            )
