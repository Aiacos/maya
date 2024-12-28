"""
#todo: clean up the mess
"""
import logging
import pprint

from zoo.core.util import zlogging

from zoo.libs.maya import zapi
from zoo.libs.maya.utils import files, general
from zoo.libs.maya.cmds.filemanage import saveexportimport
from zoo.libs.hive import api
from maya import cmds
from zoo.libs.utils import output

logger = zlogging.getLogger(__name__)

NO_GEOM_MSG = "Export Meshes is checked but no geometry has been found.\n" \
              "Please parent all geometry into the rig's 'geo_hrc' group."


class ExportSettings(object):
    """Handles All Currently available fbx export settings
    """

    def __init__(self):
        self.outputPath = ""
        self.skeletonDefinition = True
        self.constraints = False
        self.tangents = True
        self.hardEdges = False
        self.smoothMesh = False
        self.smoothingGroups = True
        self.version = "FBX201800"
        self.shapes = True
        self.skins = True
        self.lights = False
        self.cameras = False
        self.animation = False
        self.startEndFrame = []
        self.ascii = False
        self.triangulate = True
        self.includeChildren = True
        self.axis = "Y"
        # if True then the scene will not be reset, good for debugging the output skeleton.
        self.debugScene = False
        # If True then scale attributes will be included in the export
        self.includeScale = True
        self.meshes = True
        # If True then if there's user errors/warnings etc then they will be shown in a popup dialog.
        self.interactive = False

    def pprint(self):
        pprint.pprint({"outputPath": self.outputPath,
                       "skeletonDefinition": self.skeletonDefinition,
                       "constraints": self.constraints,
                       "tangents": self.tangents,
                       "hardEdges": self.hardEdges,
                       "smoothMesh": self.smoothMesh,
                       "smoothingGroups": self.smoothingGroups,
                       "version": self.version,
                       "shapes": self.shapes,
                       "skins": self.skins,
                       "lights": self.lights,
                       "cameras": self.cameras,
                       "animation": self.animation,
                       "ascii": self.ascii,
                       "triangulate": self.triangulate,
                       "includeChildren": self.includeChildren,
                       "startEndFrame": self.startEndFrame,
                       "includeScale": self.includeScale,
                       "debugScene": self.debugScene,
                       "axis": self.axis,
                       "meshes": self.meshes,
                       "interactive": self.interactive})


class FbxExporterPlugin(api.ExporterPlugin):
    """

    FBX Export hierarchy
    | ------------------- |
    | geometry transform  |
    |    geo              |
    | skeleton root       |
    | ------------------- |

    .. code-block:: python
        from zoo.libs.hive import api as hiveapi
        rigInstance = r.rig()
        rigInstance.startSession("rig")
        exporter = hiveapi.Configuration().exportPluginForId("fbxExport")()
        settings = exporter.exportSettings()  # type: zoo.libs.hive.library.exporters.fbxexporter
        settings.outputPath = outputPath

        # the actual FBX not the display label
        settings.version = "FBX201800"
        settings.shapes = True
        settings.axis = "y"
        settings.triangulate = True
        settings.ascii = True
        settings.animation = True
        settings.startEndFrame = [0.0, 40.0]
        settings.meshes = True
        settings.skins = False

        exporter.execute(rigInstance, settings)
    """
    id = "fbxExport"

    def exportSettings(self):
        return ExportSettings()

    def export(self, rig, exportOptions):
        """

        :param rig:
        :type rig: :class:`zoo.libs.hive.base.rig.Rig`
        :param exportOptions:
        :type exportOptions: :class:`ExportSettings`
        :return:
        :rtype:
        """

        self.onProgressCallbackFunc(10, "Prepping scene for rig export")

        general.loadPlugin("fbxmaya")
        if exportOptions.animation:
            self._exportAnimationRig(rig, exportOptions)
        else:
            self._exportBindPoseRig(rig, exportOptions)

    def _exportAnimationRig(self, rig, exportOptions):
        """
        :param rig:
        :type rig:
        :param exportOptions:
        :type exportOptions:
        :return:
        :rtype:

        Steps for exporting animation.
        We only need the skeleton and blend shapes. For the sake of simplicity the first solution
        we  have is to export blendshapes with the shapes=True option but later we should do a optimised
        version. We go with a simple solution here basically just straight use FBX bake animation instead of
        bakeResults command even though i don't trust fbx bake but to avoid reopening a complex animation
        scene since we would be baking blendshapes weights in this version.


        1. Duplicate the skeleton, this is so the hierarchy for the joints is the same as the bindPose.
            We don't care about the geometry as long as the blendshapes go out and only the weight attribute
            alias names matter. todo: check maya->unity
        2. Clean the skeleton, deleting constraints, attributes etc.
        3. Constraint the duplicate skeleton to the original.
        4. export fbx
        5. delete the duplicate skeleton.


        """
        components = [comp for comp in rig.iterComponents()]
        if not any(comp.hasSkeleton() for comp in components):
            output.displayError("Missing Skeleton please build the skeleton before exporting.")
            return
        currentScenePath = saveexportimport.currentSceneFilePath()
        exportOptions.pprint()
        deformLayer = rig.deformLayer()

        geoLayer = rig.geometryLayer()
        geoRoot = geoLayer.rootTransform()
        deformRoot = deformLayer.rootTransform()

        skelRoots = list(deformRoot.iterChildren(recursive=False, nodeTypes=(zapi.kJoint,)))

        if not exportOptions.skins:
            rootJoints = self._exportAnimNoSkin(skelRoots, exportOptions)
        else:
            rootJoints = self._exportAnimSkin(skelRoots, exportOptions)

        exportNodes = rootJoints
        # un parent the geometry layer so we can reuse it
        if exportOptions.meshes and geoRoot:

            geoParent = geoRoot.parent()
            geoRoot.lock(False)
            geoRoot.setParent(None)
            modifier = zapi.dgModifier()
            geoRoot.removeNamespace(modifier=modifier, apply=False)
            for mesh in geoRoot.iterChildren(recursive=True):
                mesh.removeNamespace(modifier=modifier, apply=False)
            modifier.doIt()
            exportNodes.append(geoRoot)

        self.onProgressCallbackFunc(50, "Starting FBX export")
        _exportFbx(exportNodes, exportOptions)
        self.onProgressCallbackFunc(80, "Completed export to : {}".format(exportOptions.outputPath))

        if not exportOptions.debugScene:
            self.onProgressCallbackFunc(85, "Reopening previous scene")
            files.openFile(currentScenePath)

    def _exportBindPoseRig(self, rig, exportOptions):
        """Exports a the rig at bind pose.

        :param rig:
        :type rig: :class:`api.Rig`
        :param exportOptions:
        :type exportOptions: :class:`ExportSettings`

        Necessary Steps for exporting bind pose.
        FBX can be flaky in all sorts of ways and it doesn't flatten or remove namespaces. Asset
         containers always end up in the FBX as well so we do some extra work here to purge.

        1. import any file references. as the skeleton maybe be a ref and we need to remove namespaces
        2. un-parent geometry layer root transform
        3. un-parent joints
        4. clean the skeleton, removing constraints(based on settings), remove namespaces
        5. disconnect the geo layer root transform so we don't delete it when the rig is deleted.
        6. delete the rig. This purges containers and anything random FBX likes to add.
        7. export FBX
        8. reopen the scene.
        """

        components = [comp for comp in rig.iterComponents()]
        if not any(comp.hasSkeleton() for comp in components):
            output.displayError("Missing Skeleton please build the skeleton before exporting.")
            return
        exportOptions.pprint()
        currentScenePath = saveexportimport.currentSceneFilePath()

        deformLayer = rig.deformLayer()
        exportNodes = []
        deformRoot = deformLayer.rootTransform()

        rootGeoTransform, success = self.validate(exportOptions, rig)
        if not success:
            return
        if rootGeoTransform:
            exportNodes.append(rootGeoTransform)
        # import the current scene references so we can blow away nodes and clean namespaces
        saveexportimport.importAllReferences()

        if exportOptions.meshes:
            self._prepGeometry(rig)
        for comp in components:
            compDeform = comp.deformLayer()
            compDeform.disconnectAllJoints()

        skelRoots = list(deformRoot.iterChildren(recursive=False, nodeTypes=(zapi.kJoint,)))

        api.skeletonutils.cleanSkeletonBeforeExport(skelRoots)
        exportNodes.extend(skelRoots)
        # remove the rig in the scene without deleting the joints. This creates a clean FBX file.
        # note: we reopen the scene at the end

        rig.delete()
        try:
            displayLayers = zapi.displayLayers(default=False)
            cmds.delete(displayLayers)
        except RuntimeError:
            pass  # it's erroring because theres no displaylayers left
        self.onProgressCallbackFunc(50, "Exporting Rig as FBX")
        _exportFbx(exportNodes,
                   exportOptions)
        self.onProgressCallbackFunc(75,
                                    "Finished Exporting to :{}, reopening original Scene".format(
                                        exportOptions.outputPath))
        self._resetScene(exportOptions, currentScenePath)

    def validate(self, exportOptions, rig):
        if not exportOptions.meshes:
            return "", True

        _, rootTransform = self._rootGeoHrc(rig)
        if rootTransform is None:
            self.showUserMessage("Missing Geometry", logging.WARNING, NO_GEOM_MSG)
            return "", False
        for _ in rootTransform.iterChildren(recursive=True, nodeTypes=(zapi.kNodeTypes.kMesh,)):
            return rootTransform, True

        if exportOptions.interactive:
            self.showUserMessage("Missing Geometry", logging.WARNING, NO_GEOM_MSG)
            return "", False
        else:
            logging.warning(NO_GEOM_MSG)

    def _resetScene(self, exportOptions, currentScenePath):
        if not exportOptions.debugScene:
            if currentScenePath:
                files.openFile(currentScenePath)
            else:
                files.newScene(force=True)

    def _rootGeoHrc(self, rig):
        geoLayer = rig.geometryLayer()
        if geoLayer is None:
            return
        return geoLayer, geoLayer.rootTransform()

    def _prepGeometry(self, rig):
        """

        :param rig:
        :type rig:
        :return:
        :rtype: :class:`zapi.DagNode`
        """
        geoLayer, geoRoot = self._rootGeoHrc(rig)
        if geoRoot is None:
            return
        geoRoot.setParent(None)
        modifier = zapi.dgModifier()
        modifier.setNodeLockState(geoRoot.object(), False)
        modifier.doIt()
        geoRoot.removeNamespace(modifier=modifier, apply=False)
        for mesh in geoRoot.iterChildren(recursive=True):
            mesh.removeNamespace(modifier=modifier, apply=False)
        modifier.doIt()

        geoLayer.attribute(api.constants.ROOTTRANSFORM_ATTR).disconnectAll()
        return geoRoot

    def _exportAnimNoSkin(self, skeletonRoots, exportOptions):
        # duplicate and constrain the skeleton will need to create temp namespace as mapping
        # the 2 skeleton will need to be done by node name not hive ids since we don't have all the
        # necessary data to do so.
        with zapi.tempNamespaceContext("tempNamespace"):
            self.onProgressCallbackFunc(15, "Prepping skeleton for export")
            duplicateSkeletonJoints = cmds.duplicate([i.fullPathName() for i in skeletonRoots],
                                                     returnRootsOnly=True,
                                                     inputConnections=False,
                                                     renameChildren=False)
            rootJoints = list(zapi.nodesByNames(duplicateSkeletonJoints))

            api.skeletonutils.cleanSkeletonBeforeExport(rootJoints, constraints=False)
            # generate a lookup table for the duplicate skeleton with the shortName: node
            # which will be used to create a constraints between the 2
            joints = {}
            for root in rootJoints:
                joints[root.name(includeNamespace=False)] = root
                for childJnt in root.iterChildren(nodeTypes=(zapi.kNodeTypes.kJoint,)):
                    joints[childJnt.name(includeNamespace=False)] = childJnt
            self.onProgressCallbackFunc(40, "Binding duplicate skeleton to original before exporting")
            # generate constraints between the duplicate and original skeleton
            for skelRoot in skeletonRoots:
                originalName = skelRoot.name(includeNamespace=False)
                matchedDupJnt = joints.get(originalName)
                zapi.buildConstraint(matchedDupJnt, {"targets": [("", skelRoot)]}, constraintType="parent",
                                     trace=False, maintainOffset=False)
                if exportOptions.includeScale:
                    zapi.buildConstraint(matchedDupJnt, {"targets": [("", skelRoot)]}, constraintType="scale",
                                         trace=False, maintainOffset=True)

                for originalChildJnt in skelRoot.iterChildren(nodeTypes=(zapi.kNodeTypes.kJoint,)):
                    originalName = originalChildJnt.name(includeNamespace=False)
                    matchedDupJnt = joints.get(originalName)
                    zapi.buildConstraint(matchedDupJnt, {"targets": [("", originalChildJnt)]}, constraintType="parent",
                                         trace=False, maintainOffset=False)
                    if exportOptions.includeScale:
                        zapi.buildConstraint(matchedDupJnt, {"targets": [("", originalChildJnt)]},
                                             constraintType="scale",
                                             trace=False, maintainOffset=True)
        return rootJoints

    def _exportAnimSkin(self, skeletonRoots, exportOptions):
        # to export with skin at the animation level and still be compatible with the bindpose
        # we need to flatten the references first
        # and then unparent, clean then export.
        # import the current scene references so we can blow away nodes and clean namespaces
        self.onProgressCallbackFunc(15, "Importing all references so we can correctly export skinning")
        saveexportimport.importAllReferences()
        self.onProgressCallbackFunc(30, "Cleaning skeleton data")
        # now unparent the joints and geometry root
        api.skeletonutils.cleanSkeletonBeforeExport(skeletonRoots, constraints=True, onlyHiveAttrs=True)
        try:
            displayLayers = zapi.displayLayers(default=False)
            cmds.delete(displayLayers)
        except RuntimeError:
            pass  # it's erroring because theres no displaylayers left
        return skeletonRoots


def _exportFbx(nodeNames, exportOptions):
    frames = exportOptions.startEndFrame
    startFrame, endFrame = None, None
    if frames:
        startFrame, endFrame = frames
    files.exportFbx(exportOptions.outputPath, [i.fullPathName() for i in nodeNames if i],
                    skeletonDefinition=exportOptions.skeletonDefinition,
                    constraints=exportOptions.constraints,
                    tangents=exportOptions.tangents,
                    hardEdges=exportOptions.hardEdges,
                    smoothMesh=exportOptions.smoothMesh,
                    smoothingGroups=exportOptions.smoothingGroups,
                    version=exportOptions.version,
                    shapes=exportOptions.shapes,
                    skins=exportOptions.skins,
                    lights=exportOptions.lights,
                    cameras=exportOptions.cameras,
                    animation=exportOptions.animation,
                    includeChildren=exportOptions.includeChildren,
                    startFrame=startFrame,
                    endFrame=endFrame,
                    triangulate=exportOptions.triangulate,
                    meshes=exportOptions.meshes
                    )
