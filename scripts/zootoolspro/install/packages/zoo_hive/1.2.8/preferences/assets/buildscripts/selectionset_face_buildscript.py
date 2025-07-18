"""Face Selection Sets Build Script for adding custom selection sets to the rig after Polish.

Handles
- Animator selection sets


------------ BUILD SCRIPT UI DOCUMENTATION ----------------

More Hive Build Script documentation found at:
    https://create3dcharacters.com/zoo-dev-documentation/packages/zoo_hive/buildscripting.html

Common build script code examples:
    https://create3dcharacters.com/zoo-dev-documentation/packages/zoo_hive/buildscripting_examples.html

Author: David Sparrow, Andrew Silke
"""
from maya import cmds

from zoo.libs.hive import api
from zoo.libs.maya.cmds.sets import selectionsets


class SelectionSetFaceBuildScript(api.BaseBuildScript):
    """
    """
    # unique identifier for the plugin which will be referenced by the registry.
    id = "selectionSetFaceBuildScript"

    def _validateSets(self, sets):
        """Validates the sets exist, if not they are removed from the list

        :param sets: A list of sets to validate
        :type sets: list[str]
        """
        newSet = []
        for s in sets:
            if cmds.objExists(s):
                newSet.append(s)
        return newSet

    def postPolishBuild(self, properties):
        """Executed after the polish stage.

        # TODO make the set names more generic and not hard coded
        """
        # r = self.rig  # use later

        # Container Set Names -------------------------------------------------------------------------------------
        face_all_set = "face_all_set"
        eyeAll_sSet = "eyeAll_sSet"
        browAll_sSet = "browAll_sSet"
        earAll_sSet = "earAll_sSet"
        teethAll_sSet = "teethAll_sSet"
        mouthAll_sSet = "mouthAll_sSet"
        mouthJaw_sSet = "mouthJaw_sSet"

        # Component Set Names -------------------------------------------------------------------------------------
        eye_L_sSet = "eye_L_sSet"
        eye_R_sSet = "eye_R_sSet"
        eyesMain_M_sSet = "eyesMain_M_sSet"
        brow_L_sSet = "brow_L_sSet"
        brow_R_sSet = "brow_R_sSet"
        mouth_sSet = "mouth_M_sSet"
        ear_L_sSet = "ear_L_sSet"
        ear_R_sSet = "ear_R_sSet"
        jaw_M_sSet = "jaw_M_sSet"
        teethLower_M_sSet = "teethLower_M_sSet"
        teethUpper_M_sSet = "teethUpper_M_sSet"
        tongue_M_sSet = "tongue_M_sSet"
        nose_M_sSet = "nose_M_sSet"

        # Create the sets as a list of names, also checks if they exist ------------------------------
        eye_sets = self._validateSets([eye_L_sSet, eye_R_sSet, eyesMain_M_sSet])
        brow_sets = self._validateSets([brow_L_sSet, brow_R_sSet])
        ear_sets = self._validateSets([ear_L_sSet, ear_R_sSet])
        mouthJaw_sets = self._validateSets([mouth_sSet, jaw_M_sSet])
        teethAll_sSets = self._validateSets([teethLower_M_sSet, teethUpper_M_sSet])
        mouthAll_sets = self._validateSets([tongue_M_sSet])
        nose_sets = self._validateSets([nose_M_sSet])
        face_sets = eye_sets + ear_sets + mouthAll_sets + nose_sets + brow_sets + mouthJaw_sets + teethAll_sSets

        if not cmds.objExists(face_all_set):  # create the face_all_set if it doesn't exist --------------------------
            selectionsets.addSSetZooOptions(face_all_set, [],
                                            icon="st_circlePurple",
                                            visibility=False,
                                            parentSet="all_sSet", soloParent=True)
        # Create the container selection sets, children, and parents to the face_all_set ------------------------------
        for sset in face_sets:
            selectionsets.setMarkingMenuVis(sset, visibility=False)
            selectionsets.setIcon(sset, "st_squarePink")
            # unparent set, usually from the body set
            selectionsets.unParentAll(sset)
        if nose_sets:
            selectionsets.parentSelectionSets(nose_sets, face_all_set)
        if eye_sets:
            selectionsets.addSSetZooOptions(eyeAll_sSet, eye_sets,
                                            icon="st_trianglePink",
                                            visibility=False,
                                            parentSet=face_all_set, soloParent=True)
        if brow_sets:
            selectionsets.addSSetZooOptions(browAll_sSet, brow_sets,
                                            icon="st_circleOrange",
                                            visibility=False,
                                            parentSet=face_all_set, soloParent=True)
        if ear_sets:
            selectionsets.addSSetZooOptions(earAll_sSet, ear_sets,
                                            icon="st_trianglePink",
                                            visibility=False,
                                            parentSet=face_all_set, soloParent=True)
        if mouthAll_sets:
            selectionsets.addSSetZooOptions(mouthAll_sSet, mouthAll_sets,
                                            icon="st_trianglePink",
                                            visibility=False,
                                            parentSet=face_all_set, soloParent=True)
        if nose_sets:
            selectionsets.parentSelectionSets(nose_sets, face_all_set)
        if mouthJaw_sets:
            selectionsets.addSSetZooOptions(mouthJaw_sSet, mouthJaw_sets,
                                            icon="st_trianglePink",
                                            visibility=False,
                                            parentSet=mouthAll_sSet, soloParent=True)
        if teethAll_sSets:
            selectionsets.addSSetZooOptions(teethAll_sSet, teethAll_sSets,
                                            icon="st_circlePink",
                                            visibility=False,
                                            parentSet=mouthAll_sSet, soloParent=True)

