"""
from zoo.libs.hive.universalmesh import universalmesh
universalmesh.buildPivots()

from zoo.libs.hive.universalmesh import universalmesh
buildBipedInstc = universalmesh.BuildBipedFromUniversalMesh()
buildBipedInstc.setMeshName("skinProxy:skinProxy_geo")
buildBipedInstc.buildSkeleton()
buildBipedInstc.buildGuides(cleanup=True)

from zoo.libs.hive.universalmesh import universalmesh
universalmesh.templateCurveObjList(objList)

"""

from maya import cmds

from zoo.libs.maya import zapi
from zoo.libs.maya.cmds.objutils import namehandling, joints

from zoo.libs.utils import output
from zoo.libs.hive.universalmesh import umeshconstants as mc
from zoo.libs.hive.library.matching import matchconstants
from zoo.libs.maya.cmds.modeling import create
from zoo.libs.hive.library.matching import buildskinfromskele
from zoo.libs.maya.cmds.objutils import selection

ZOO_SKIN_PROXY_DICT = mc.ZOO_SKIN_PROXY_DICT
LOCATOR_BIPED_DEFAULT = mc.LOCATOR_BIPED_DEFAULT
SKELETON_NAME_DICT = matchconstants.HIVE_BIPED_SKELETON
JOINT_NAMES = mc.JOINT_NAMES
LRA_JOINTS = mc.LRA_JOINTS

PIVOT_SUFFIX = "zooPivot"


def vertextSelection():
    """Returns the vertices selected on the skin proxy mesh.

    :return: The vertices selected on the skin proxy mesh
    :rtype: list(int)
    """
    verts = list()
    selVerts = selection.convertSelection(type="vertices", flatten=True)
    if not selVerts:
        output.displayWarning("Please select some vertices, edges or faces. Nothing is selected.")
        return verts
    for s in selVerts:
        if ".vtx[" in s:
            verts.append(int(s.split("[")[-1].split("]")[0]))
    return verts


def universalMeshUI():
    """Returns the skin proxy mesh and then automatically finds the root joint of the skeleton.

    If nothing is selected it will try to find the skin proxy mesh and root joint automatically.

    :return: The skin proxy mesh and the root joint of the skeleton
    :rtype: tuple(str, str)
    """
    universalMeshes = []
    selGeo = cmds.ls(selection=True, type="transform")
    if not selGeo:
        universalMeshes = cmds.ls("*skinProxy_geo*", type="transform")
        if not universalMeshes:
            output.displayWarning("Please select the universal or skin proxy mesh.")
            return ""
        if len(universalMeshes) > 1:
            output.displayWarning("Please select the universal or skin proxy mesh, more than one mesh found.")
            return ""
    if universalMeshes:
        selGeo = universalMeshes
    mesh = selGeo[0]
    return mesh


def createTemplatedCurve(obj1, obj2, alwaysDrawOnTop=True):
    """Creates a curve between two objects, the curve is templated.

    :param obj1: The first object to create the curve between
    :type obj1: str
    :param obj2: The second object to create the curve between
    :type obj2: str
    :param alwaysDrawOnTop: If True the curve will always draw on top
    :type alwaysDrawOnTop: bool
    :return curve: The curve name created, the two clusters created for the curve
    :rtype curve: tuple(str, str, str)
    """
    # Draw a linear curve between the two joints
    curve = cmds.curve(degree=1, point=[[0, 0, 0], [0, 1, 0]], name="jointCurve")

    # Create clusters for each CV and constrain the clusters to the joints
    curve_cvs = cmds.ls("{}.cv[*]".format(curve), flatten=True)

    # Create a cluster and constrain
    cluster1 = cmds.cluster(curve_cvs[0], name="cluster1")
    cmds.parentConstraint(obj1, cluster1, maintainOffset=False)

    cluster2 = cmds.cluster(curve_cvs[1], name="cluster2")
    cmds.parentConstraint(obj2, cluster2, maintainOffset=False)

    cmds.setAttr("{}.visibility".format(cluster1[1]), False)
    cmds.setAttr("{}.visibility".format(cluster2[1]), False)

    # Template the curve
    cmds.setAttr("{}.template".format(curve), 1)

    curveShape = cmds.listRelatives(curve, shapes=True)[0]

    if cmds.attributeQuery("alwaysDrawOnTop", node=curveShape, exists=True) and alwaysDrawOnTop:
        cmds.setAttr("{}.alwaysDrawOnTop".format(curve), 1)

    return curve, cluster1, cluster2


def templateCurveObjList(objList):
    """Creates a curve between each object in the list, the curve is templated.

    :param objList: A list of objects to create a curve between
    :type objList: list(str)
    :return curveList: A list of the curve names created
    :rtype curveList: list(str)
    """
    curveList = list()
    clusterList = list()
    for i, obj in enumerate(objList):
        if i == len(objList) - 1:
            break
        curve, cluster1, cluster2 = createTemplatedCurve(obj, objList[i + 1])
        curveList.append(curve)
        clusterList.append(cluster1)
        clusterList.append(cluster2)
    return curveList, clusterList


def buildPivots(vertDict=ZOO_SKIN_PROXY_DICT, mesh="skinProxy:skinProxy_geo"):
    """Creates locator pivots from the given vertice dictionary, pivots are placed at the average center of the verts.

    From a vert dictionary::

        vertDict = {"neck": [1123, 123, 1231],
                   "head": [1123, 123, 1231]}

    Creates a list of locators named:

        ["neck_pivot", "head_pivot"]

    :param vertDict: A dictionary of named pivots and their vertex indices.  see umeshconstants.ZOO_SKIN_PROXY_DICT
    :type vertDict: dict(str: list(int))
    :param mesh: The name of the mesh to create the locators from.
    :type mesh: str
    :return: A list of locators created with pivot names
    :rtype: list(str)
    """
    from zoo.libs.maya.cmds.objutils import locators
    pivotLocList = list()
    for key, value in vertDict.items():
        selectedVertList = []
        for vertex in value:
            selectedVertList.append("{}.vtx[{}]".format(mesh, vertex))
        locName = "{}_pivot".format(key)
        if cmds.objExists(locName):  # delete the locator if it already exists
            cmds.delete(locName)
        pivotLocList.append(locators.createLocatorsMatchObjList(selectedVertList,
                                                                name="{}_{}".format(key, PIVOT_SUFFIX),
                                                                handle=True,
                                                                locatorSize=0.1,
                                                                message=False))
    return pivotLocList


class BuildBipedFromUniversalMesh(object):
    """
    """

    def __init__(self,
                 meshName="skinProxy:skinProxy_geo",
                 pivotLocList=None,
                 ):
        """
        """
        super(BuildBipedFromUniversalMesh, self).__init__()
        self.meshName = meshName
        self.pivotLocList = pivotLocList
        self.skeletonJointsZapi = list()
        self.jntNamespace = "hive"
        self.rigName = "biped"
        self.spineBaseJntZapi = None
        self.vertDict = ZOO_SKIN_PROXY_DICT

    def setRigName(self, rigName):
        """Sets the name of the rig Eg. "biped"
        """
        self.rigName = rigName

    def setMeshName(self, meshName, message=True):
        """Sets the name of the skin proxy mesh Eg. "skinProxy:skinProxy_geo"
        """
        if not meshName:
            if message:
                output.displayWarning("Please enter a mesh into the UI")
            return False
        if cmds.objExists(meshName):
            self.meshName = meshName
            return True
        if message:
            output.displayWarning("Mesh does not exist: {}".format(meshName))
        return False

    def setVertDict(self, vertDict):
        """Sets the vert dictionary for the skin proxy mesh
        """
        self.vertDict = vertDict

    def _buildOnePivot(self, name, transRot):
        loc = cmds.spaceLocator(name=name, )[0]
        trans = transRot[0]
        rot = transRot[1]
        cmds.setAttr("{}.translate".format(loc), trans[0], trans[1], trans[2])
        cmds.setAttr("{}.rotate".format(loc), rot[0], rot[0], rot[0])
        cmds.setAttr(".displayHandle".format(loc), 1)
        return loc

    def deleteLocators(self):
        delList = list()
        if cmds.objExists(mc.LOCATOR_PIVOTS_GRP):
            delList.append(mc.LOCATOR_PIVOTS_GRP)
        if cmds.objExists(mc.LOCATOR_TEMPLATE_GRP):
            delList.append(mc.LOCATOR_TEMPLATE_GRP)
        for name, transRot in LOCATOR_BIPED_DEFAULT.items():
            if cmds.objExists(name):
                delList.append(name)
        if delList:
            cmds.delete(delList)

    def deleteSkeleton(self):
        if cmds.objExists(JOINT_NAMES[0]):
            cmds.delete(JOINT_NAMES)
            return True
        return False

    def validateMesh(self):
        if not self.meshName:
            sel = cmds.ls(selection=True, type="transform")
            if sel:
                self.meshName = cmds.ls(selection=True)[0]
            else:
                return ""
        if not cmds.objExists(self.meshName):
            self.meshName = ""
            return ""
        return self.meshName

    def _locatorHierarchy(self):
        # From the pivot locators create joints ---------------------------------------
        pivotsLists = list()
        pivotsLists.append(self._addPivSfx([mc.K_SPLINE_SPINE_BASE, mc.K_SPLINE_SPINE_TOP, mc.K_NECK_BASE, mc.K_HEAD]))
        pivotsLists.append(self._addPivSfx([mc.K_CLAVICLE_L, mc.K_UPPERARM_L, mc.K_ELBOW_L, mc.K_WRIST_L]))
        pivotsLists.append(self._addPivSfx([mc.K_THIGH_L, mc.K_KNEE_L, mc.K_ANKLE_L, mc.K_BALL_L]))
        pivotsLists.append(self._addPivSfx([mc.K_THUMB00_L, mc.K_THUMB01_L, mc.K_THUMB02_L]))
        pivotsLists.append(self._addPivSfx([mc.K_POINTERMETA_L, mc.K_POINTER00_L, mc.K_POINTER01_L, mc.K_POINTER02_L]))
        pivotsLists.append(self._addPivSfx([mc.K_MIDDLEMETA_L, mc.K_MIDDLE00_L, mc.K_MIDDLE01_L, mc.K_MIDDLE02_L]))
        pivotsLists.append(self._addPivSfx([mc.K_RINGMETA_L, mc.K_RING00_L, mc.K_RING01_L, mc.K_RING02_L]))
        pivotsLists.append(self._addPivSfx([mc.K_PINKYMETA_L, mc.K_PINKY00_L, mc.K_PINKY01_L, mc.K_PINKY02_L]))

        jointParents = list()
        jointParents.append((mc.K_CLAVICLE_L, mc.K_SPLINE_SPINE_TOP))
        jointParents.append((mc.K_THIGH_L, mc.K_SPLINE_SPINE_BASE))
        jointParents.append((mc.K_THUMB00_L, mc.K_WRIST_L))
        jointParents.append((mc.K_POINTERMETA_L, mc.K_WRIST_L))
        jointParents.append((mc.K_MIDDLEMETA_L, mc.K_WRIST_L))
        jointParents.append((mc.K_RINGMETA_L, mc.K_WRIST_L))
        jointParents.append((mc.K_PINKYMETA_L, mc.K_WRIST_L))

        return pivotsLists, jointParents

    def buildPivots(self, message=True):
        """Builds the pivot locators from the ZOO_SKIN_PROXY_DICT for the given mesh
        """
        curves = list()
        clusterPairs = list()

        self.deleteLocators()
        if not self.meshName:  # build the pivots from the default locations as no mesh was given
            self.pivotLocList = list()
            for name, transRot in LOCATOR_BIPED_DEFAULT.items():
                loc = self._buildOnePivot(name, transRot)
                self.pivotLocList.append(loc)
        else:
            if not cmds.objExists(self.meshName):
                output.displayWarning("Mesh does not exist: {}".format(self.meshName))
            self.pivotLocList = buildPivots(vertDict=self.vertDict, mesh=self.meshName)
        cmds.select(deselect=True)

        pivotsLists, jointParents = self._locatorHierarchy()  # get the pivots for each chain and joint parents

        for pivots in pivotsLists:  # create the curves and clusters for each chain
            curveList, clusterList = templateCurveObjList(pivots)
            curves += curveList
            clusterPairs += clusterList

        for i, joints in enumerate(jointParents):  # create the curves and clusters for each branch
            locs = self._addPivSfx(joints)
            curveList, clusterList = templateCurveObjList(locs)
            curves += curveList
            clusterPairs += clusterList

        # create a group and add the curves and clusters to it
        templateGroup = cmds.group(empty=True, name=mc.LOCATOR_TEMPLATE_GRP)
        cmds.parent(curves, templateGroup)
        for clusterPair in clusterPairs:
            cmds.parent(clusterPair, templateGroup)

        # create a group and add the group and locators to it
        locGroup = cmds.group(empty=True, name=mc.LOCATOR_PIVOTS_GRP)
        cmds.parent(self.pivotLocList, locGroup)
        cmds.parent(templateGroup, locGroup)

        # deselect all
        cmds.select(deselect=True)

        output.displayInfo("Success: Created Hive Pivot Locators")

    def _addPivSfx(self, strList):
        """ adds "_zooPivot_jnt" to the end of each string in the list
        """
        sfxList = list()
        for s in strList:
            sfxList.append("{}_{}".format(s, PIVOT_SUFFIX))
        return sfxList

    def _locatorsExist(self, autoBuild=True):
        """Checks if the locators exist, if not builds them, creates self.pivotLocList
        """
        pivList = list()

        if not cmds.objExists(mc.LOCATOR_PIVOTS_GRP) and autoBuild:
            self.buildPivots()
        elif not cmds.objExists(mc.LOCATOR_PIVOTS_GRP) and not autoBuild:
            return False

        # pivots exist, check any have been deleted and add to self.pivotLocList
        for name, transRot in LOCATOR_BIPED_DEFAULT.items():
            if cmds.objExists(name):
                pivList.append(name)
                continue
            if autoBuild:
                loc = self._buildOnePivot(name, transRot)
                pivList.append(loc)
            else:
                return False
        self.pivotLocList = pivList
        return True

    def _skeletonExists(self):
        if cmds.objExists(JOINT_NAMES[0]):
            return True
        return False

    def _validSkeleton(self):
        for jnt in JOINT_NAMES:
            if not cmds.objExists(jnt):
                return False
        return True

    def _LRAJoints(self):
        # Turn on LRA for fingers and neck/head
        joints.displayLocalRotationAxisJointList(LRA_JOINTS, children=True, display=True, message=False)
        joints.alignJointZoo(LRA_JOINTS,
                             primaryAxisVector=(1, 0, 0),
                             secondaryAxisVector=(0, 1, 0),
                             worldUpAxisVector=(0, 1, 0),
                             orientChildren=True,
                             ignoreConnectedJoints=False,
                             freezeJoints=False,
                             message=False)
        # Align the neck (and head) Y to world neg Z
        neckJoint = LRA_JOINTS[-1]  # is the neck joint
        joints.alignJointZoo([neckJoint],
                             primaryAxisVector=(1, 0, 0),
                             secondaryAxisVector=(0, 1, 0),
                             worldUpAxisVector=(0, 0, -1),
                             orientChildren=True,
                             ignoreConnectedJoints=False,
                             freezeJoints=False,
                             message=False)

    def buildSkeleton(self, message=True):
        """Builds the middle and left side skeleton with Hive naming convention
        """
        allJoints = list()
        if not self._locatorsExist(autoBuild=True):  # creates self.pivotLocList
            if not self.meshName:  # rebuild the default pivots
                self.buildPivots(message=False)
            else:  # Build the pivots from mesh if they don't exist yet ------------------------------------
                self.deleteLocators()
                self.buildPivots()
        if not self.pivotLocList:
            output.displayWarning("No pivot locators found, cannot build skeleton")
            return

        if self._skeletonExists():
            self.deleteSkeleton()

        # From the pivot locators create joints ---------------------------------------
        pivotsLists, jointParents = self._locatorHierarchy()
        for pivots in pivotsLists:
            allJoints += create.createPrimitiveAndMatchMulti(pivots,
                                                             primitive="joint",
                                                             parent=True,
                                                             inheritName=True,
                                                             suffix="_jnt",
                                                             message=False)
        self.spineBaseJntZapi = zapi.nodeByName("{}_{}_jnt".format(mc.K_SPLINE_SPINE_BASE, PIVOT_SUFFIX))

        allJointsZapi = list(zapi.nodesByNames(allJoints))

        # Rename all joints by stripping _zooPivot_jnt --------------------------------
        for i, jntZapi in enumerate(allJointsZapi):
            shortName = namehandling.getShortName(jntZapi.fullPathName())
            newJointName = shortName.replace("_{}_jnt".format(PIVOT_SUFFIX), "")
            namehandling.safeRename(jntZapi.fullPathName(), newJointName, message=False)

        # parent roots together ------------------------------------------------------
        for jointPair in jointParents:
            cmds.parent(jointPair[0], jointPair[1])  # Note hardcoded names

        # Rename all joints to the Hive skeleton naming convention ---------------------
        for i, jntZapi in enumerate(allJointsZapi):
            shortName = namehandling.getShortName(jntZapi.fullPathName())
            # check key exists in dict SKELETON_NAME_DICT
            if shortName not in SKELETON_NAME_DICT:
                continue
            namehandling.safeRename(jntZapi.fullPathName(), SKELETON_NAME_DICT[shortName], message=False)
        self.skeletonJointsZapi = allJointsZapi
        self._namespaceProxyJoints()
        # Turn on LRA for fingers and neck/head and align to world up -------------------
        self._LRAJoints()
        # delete the locators ---------------------------------------------------------
        self.deleteLocators()
        if message:
            output.displayInfo("Success: Created Hive Proxy Joints")
        return self.skeletonJointsZapi

    def _namespaceProxyJoints(self):
        """Adds a namespace to all joints if there isn't one.
        """
        jnts = list(zapi.fullNames(self.skeletonJointsZapi))
        if ":" in jnts[0]:
            return  # already has a namespace
        renameList = list()
        for i, jnt in enumerate(jnts):
            if cmds.objExists(jnt):
                renameList.append(jnt)
        if renameList:
            namehandling.createAssignNamespaceList(renameList, self.jntNamespace)

    def buildGuides(self, cleanup=True):
        if not self._skeletonExists():
            output.displayWarning("No skeleton found. Please build the Proxy Joints first.")
            return

        self.sourceMatchJntsList = list()

        if not self.spineBaseJntZapi or not self.skeletonJointsZapi:  # Joints aren't loaded in the class
            if self._skeletonExists():
                if not self._validSkeleton():
                    self.deleteSkeleton()
                    self.buildSkeleton()
            else:
                self.buildSkeleton()
            # Skeleton exists now ----------------------------------------------
            self.spineBaseJntZapi = zapi.nodeByName(JOINT_NAMES[0])
            self.skeletonJointsZapi = zapi.nodesByNames(JOINT_NAMES)

        # Build the rig
        buildInstance = buildskinfromskele.BuildAndSkinFromSkeleton(skinProxyGeo="",
                                                                    skinTargetGeoList=list())
        buildInstance.stage1_basicChecks(self.spineBaseJntZapi.fullPathName())  # auto detect skeleton
        buildInstance.stage3_buildRig(self.spineBaseJntZapi.fullPathName(), True)  # build biped
        buildInstance.stage4_matchGuides()  # match guides
        buildInstance.stage5_FinalAlignment()  # final alignment symmetry

        buildInstance.stage7_buildHiveSkeleton()  # build the skeleton
        buildInstance.stage9_polishRig(self.spineBaseJntZapi.fullPathName(),
                                       False,
                                       False,
                                       False)
        if cleanup:
            self.deleteLocators()
            if self.skeletonJointsZapi:
                cmds.delete(zapi.fullNames(self.skeletonJointsZapi))
            self.deleteSkeleton()

        output.displayInfo("Success: Created Hive Biped Rig")
