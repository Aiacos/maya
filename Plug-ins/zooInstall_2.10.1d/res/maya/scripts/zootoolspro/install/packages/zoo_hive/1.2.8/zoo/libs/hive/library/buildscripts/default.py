from zoo.libs.hive import api
from zoo.libs.maya import zapi
from zoo.libs.maya.cmds.general import manipulators
from zoo.libs.maya.utils import prefs
from zoo.core.util import zlogging
from maya import cmds

logger = zlogging.getLogger(__name__)


class DefaultBuildScript(api.BaseBuildScript):
    """The Default build script plugin handles setting world space switching(godnode),
    Ensuring that preserveChildren manipulator option is off and hiding the deform layer.
    """

    id = "default"

    def __init__(self):
        super(DefaultBuildScript, self).__init__()
        self._evaluateControllers = False
        self._currentDisplayLayer = False

    def preGuideBuild(self, properties):
        zapi.clearSelection()
        manipulators.setPreserveChildren(False)
        state = self.rig.configuration.preferencesInterface.settings(
            name="containerOutlinerDisplayUnderParent"
        )
        api.sceneutils.setMayaUIContainerDisplaySettings(
            outlinerDisplayUnderParent=state
        )
        # ensure controller evaluation is off to avoid maya freezing
        self._evaluateControllers = prefs.isControllerPrepopulateActive()
        if self._evaluateControllers:
            logger.debug("Setting Controller evaluation to Off")
            prefs.setControllerPrepopulateActive(False)
        self._currentDisplayLayer = cmds.editDisplayLayerGlobals(query=True, useCurrent=True)
        if self._currentDisplayLayer:
            cmds.editDisplayLayerGlobals(useCurrent=not self._currentDisplayLayer)

    def postGuideBuild(self, properties):
        # set controller evaulation on so the user gets a speed up because guides are tagged.
        if self._evaluateControllers:
            logger.debug("Setting Controller evaluation to On")
            prefs.setControllerPrepopulateActive(True)
        cmds.editDisplayLayerGlobals(useCurrent=self._currentDisplayLayer)

    def preDeformBuild(self, properties):
        zapi.clearSelection()
        manipulators.setPreserveChildren(False)
        state = self.rig.configuration.preferencesInterface.settings(
            name="containerOutlinerDisplayUnderParent"
        )
        api.sceneutils.setMayaUIContainerDisplaySettings(
            outlinerDisplayUnderParent=state
        )
        self._currentDisplayLayer = cmds.editDisplayLayerGlobals(query=True, useCurrent=False)
        if self._currentDisplayLayer:
            cmds.editDisplayLayerGlobals(useCurrent=not self._currentDisplayLayer)

    def postDeformBuild(self, properties):
        cmds.editDisplayLayerGlobals(useCurrent=self._currentDisplayLayer)

    def preRigBuild(self, properties):
        zapi.clearSelection()
        manipulators.setPreserveChildren(False)
        state = self.rig.configuration.preferencesInterface.settings(
            name="containerOutlinerDisplayUnderParent"
        )
        api.sceneutils.setMayaUIContainerDisplaySettings(
            outlinerDisplayUnderParent=state
        )
        # ensure controller evaluation is off to avoid maya freezing
        self._evaluateControllers = prefs.isControllerPrepopulateActive()
        if self._evaluateControllers:
            logger.debug("Setting Controller evaluation to Off")
            prefs.setControllerPrepopulateActive(False)
        self._currentDisplayLayer = cmds.editDisplayLayerGlobals(query=True, useCurrent=False)
        if self._currentDisplayLayer:
            cmds.editDisplayLayerGlobals(useCurrent=not self._currentDisplayLayer)

    def postRigBuild(self, properties):
        components = []
        rootComponent = None

        for component in self.rig.iterComponents():
            if component.componentType == "godnodecomponent":
                rootComponent = component
                continue
            inputLayer = component.inputLayer()
            if inputLayer is None:
                continue
            worldInput = inputLayer.inputNode("world")
            if worldInput is None:
                continue
            components.append((component, worldInput))
        if not rootComponent or not components:
            return
        godNode = rootComponent.outputLayer().outputNode("offset")
        for component, worldInput in components:
            # we can just run the build again but this time with different another driver
            zapi.buildConstraint(
                worldInput,
                drivers={"targets": (("", godNode),)},
                constraintType="matrix",
                maintainOffset=True,
                bakeOffset=True
            )
        cmds.editDisplayLayerGlobals(useCurrent=self._currentDisplayLayer)

    def prePolish(self, properties):
        zapi.clearSelection()
        self._currentDisplayLayer = cmds.editDisplayLayerGlobals(query=True, useCurrent=False)
        if self._currentDisplayLayer:
            cmds.editDisplayLayerGlobals(useCurrent=not self._currentDisplayLayer)

    def postPolishBuild(self, properties):
        layer = self.rig.deformLayer()
        if layer is not None:
            layer.hide()
        # set controller evaluation back to original state if it was on
        if self._evaluateControllers:
            logger.debug("Setting Controller evaluation to On")
            prefs.setControllerPrepopulateActive(True)
        cmds.editDisplayLayerGlobals(useCurrent=self._currentDisplayLayer)
