"""Natalie Hive build script.

Handles
- Animator selection sets
- Custom Face integration on polish, skeleton and guides mode
- Visibility attributes for switching hair, toes, face etc
- Disables the ability to non-uniform scale certain rig parts.


------------ BUILD SCRIPT DOCUMENTATION ----------------

More Hive Build Script documentation found at:
    https://create3dcharacters.com/zoo-dev-documentation/packages/zoo_hive/buildscripting.html

Common build script code examples:
    https://create3dcharacters.com/zoo-dev-documentation/packages/zoo_hive/buildscripting_examples.html


"""

from maya import cmds

from zoo.libs.maya import zapi
from zoo.libs.hive import api
from zoo.libs.maya.cmds.objutils import attributes, layers, connections
from zoo.libs.maya.cmds.sets import selectionsets


class NatalieBuildScript(api.BaseBuildScript):
    """Post polish buildscript for Natalie rig.  Handles visibility and extra attributes and the custom face rig

    .. note::

        Best to read the properties method in the base class :func:`api.BaseBuildScript.properties`

    """
    # Unique identifier which will seen in the Hive settings UI drop-down.
    id = "natalie_buildscript"

    # ------------------------
    # Helper Methods
    # ------------------------

    def _faceExists(self):
        try:
            jawExists = cmds.objExists(self.rig.jaw_M.rigLayer().control("jaw").fullPathName())
        except:
            jawExists = cmds.objExists("jaw_M_jaw_jnt")
        return jawExists

    # ------------------------
    # Build Script Methods
    # ------------------------

    def postPolishBuild(self, properties):
        """Executed after the polish stage.

        Adds:
            - Hair, face, toeL and toeR visibility toggle attributes on the controls.
            - Face controls to the "natalie_ctrlLayer"
            - Hides non deformation joints and follicles on the face rig
            - Adds custom animator selection sets
        """
        rig = self.rig  # The current rig object from the hive API, in this case the Natalie rig.
        visDividerAttr = "VIS OTHER"
        faceVisAttr = "faceVis"

        faceExists = self._faceExists()
        toesExist = cmds.objExists("toe01_L_00_anim")
        hairExists = cmds.objExists("hairTop_C_00_anim")

        # Get Hive Controls ------------------------
        # Control name ID's are found on the control transform: Attribute Editor > Extra Attributes > Zoo Hive ID
        godNode = rig.god_M.rigLayer().control("godnode").fullPathName()  # fullPathName() returns a string name
        hipsNode = rig.spine_M.rigLayer().control("cog").fullPathName()
        headNode = rig.head_M.rigLayer().control("head").fullPathName()
        footLNode = rig.leg_L.rigLayer().control("endik").fullPathName()
        footRNode = rig.leg_R.rigLayer().control("endik").fullPathName()

        # Create visibility label attributes ----------------------------
        attributes.labelAttr(visDividerAttr, godNode)
        attributes.labelAttr(visDividerAttr, hipsNode)
        attributes.labelAttr(visDividerAttr, headNode)

        # Create face visibility attribute and connections ----------------------------
        if faceExists:
            attributes.visibilityConnectObjs(faceVisAttr,
                                             godNode,
                                             ["jaw_M_chin_jnt_customGrp"],
                                             nonKeyable=True,
                                             defaultValue=True)
            # Add face group to ctrl layer -------------------------
            displayLayerName = rig.controlDisplayLayer().fullPathName()
            if cmds.objExists("mouthShapes_ctrl_grp"):
                layers.addToLayer(displayLayerName, ["mouthShapes_ctrl_grp"], ref=False, playback=False)

            # Add hive face roots to the vis switch on the face.
            faceRoots = list()
            faceComponents = ["jaw", "teethlower", "teethupper", "tongue", "ear", "ear", "eye", "eye",
                              "nose", "eyesmain", "brow", "brow"]
            for comp in rig.iterComponents():  # Find all root transforms of components with "hair" in the name
                for compName in faceComponents:
                    if compName == comp.name().lower():
                        faceRoots.append(comp.rootTransform().fullPathName())

            if faceRoots:
                faceRoots = list(set(faceRoots))
                for grp in faceRoots:
                    cmds.connectAttr("{}.{}".format(str(godNode), faceVisAttr), "{}.visibility".format(grp))
                attributes.addProxyAttribute(str(headNode), str(godNode), faceVisAttr, proxyAttr="")
                attributes.addProxyAttribute(str(hipsNode), str(godNode), faceVisAttr, proxyAttr="")
            # Show the outer eye controls -------------------------
            """cmds.setAttr("eye_L_controlPanel_settings.outerCtrlVis", True)
            cmds.setAttr("eye_R_controlPanel_settings.outerCtrlVis", True)
            attributes.setAttCurrentDefault("eye_L_controlPanel_settings", "outerCtrlVis", report=False)
            attributes.setAttCurrentDefault("eye_R_controlPanel_settings", "outerCtrlVis", report=False)"""

        # Create hair visibility attribute and connections ----------------------------
        if hairExists:
            hairVisAttr = "hairVis"
            hairRoots = list()  # Root transform node of each hair component, there are 13 hair components.
            for comp in rig.iterComponents():  # Find all root transforms of components with "hair" in the name
                if "hair" in comp.name().lower():
                    hairRoots.append(comp.rootTransform().fullPathName())  # fullPathName() returns a string
            if hairRoots:
                attributes.visibilityConnectObjs(hairVisAttr, str(godNode), hairRoots,
                                                 channelBox=True, nonKeyable=True, defaultValue=True)
                attributes.addProxyAttribute(str(headNode), str(godNode), hairVisAttr, proxyAttr="")
                attributes.addProxyAttribute(str(hipsNode), str(godNode), hairVisAttr, proxyAttr="")

        # Create toes visibility attribute and connections ----------------------------
        if toesExist:
            toeLVisAttr = "toesVis"
            toeLObjs = [rig.toe01_L.rootTransform().fullPathName(), rig.toe02_L.rootTransform().fullPathName(),
                        rig.toe03_L.rootTransform().fullPathName(), rig.toe04_L.rootTransform().fullPathName(),
                        rig.toe05_L.rootTransform().fullPathName()]
            attributes.visibilityConnectObjs(toeLVisAttr, footLNode, toeLObjs,
                                             channelBox=True, nonKeyable=True, defaultValue=True)

            toeRVisAttr = "toesVis"
            toeRObjs = [rig.toe01_R.rootTransform().fullPathName(), rig.toe02_R.rootTransform().fullPathName(),
                        rig.toe03_R.rootTransform().fullPathName(), rig.toe04_R.rootTransform().fullPathName(),
                        rig.toe05_R.rootTransform().fullPathName()]
            attributes.visibilityConnectObjs(toeRVisAttr, footRNode, toeRObjs,
                                             channelBox=True, nonKeyable=True, defaultValue=True)

        # Custom animator selection sets ----------------------------
        # hair sets should already exist from the sel set biped build script.
        if hairExists:
            hair_sets = ["hairBack2_L_sSet", "hairBack2_R_sSet", "hairBack_C_sSet", "hairFront1_C_sSet",
                         "hairFront2_L_sSet", "hairFront2_R_sSet", "hairFront3_L_sSet", "hairFront3_R_sSet",
                         "hairSide1_L_sSet", "hairSide1_R_sSet", "hairSide2_L_sSet", "hairSide2_R_sSet",
                         "hairTop_C_sSet"]
            validSets = list()
            for sset in hair_sets:
                if cmds.objExists(sset):
                    validSets.append(sset)
                    selectionsets.setMarkingMenuVis(sset, visibility=False)
                    selectionsets.setIcon(sset, "st_squarePink")
                    selectionsets.unParentAll(sset)  # unparent the set, usually from the body set
            hair_sets = validSets
            selectionsets.addSSetZooOptions("hair_sSet", hair_sets,
                                            icon="st_trianglePink",
                                            visibility=True,
                                            parentSet="all_sSet", soloParent=True)

        if faceExists:  # create face sets and parent
            # Add proxy attributes to the Hive jaw controls ----------------------------
            jawShapeAttrs = ["inOut_divider", "lipsIn_L", "lipsIn_R", "lipsOut_L", "lipsOut_R", "rolls_divider",
                             "topLipRollIn_L", "topLipRollIn_R",
                             "botLipRollIn_L", "botLipRollIn_R", "topLipRollOut_L", "topLipRollOut_R",
                             "botLipRollOut_L", "botLipRollOut_R", "smiles_divider", "smile_L", "smile_R",
                             "negatives_divider", "sneer_L", "sneer_R",
                             "frown_L", "frown_R", "poutTopLip_L", "poutTopLip_R", "poutBotLip_R", "poutBotLip_L",
                             "other_divider",
                             "cheek_L", "cheek_R"]
            jawControls = ["rotAll", "jaw", "chin", "botLip", "topLip"]
            mouthBlendshapeCtrl = "mouthShapes_ctrl"
            for controlId in jawControls:
                jawCtrl = rig.jaw_M.rigLayer().control(controlId).fullPathName()
                for attr in jawShapeAttrs:
                    if "_divider" in attr:
                        attributes.labelAttr(attr.split("_divider")[0], jawCtrl)
                    else:
                        attributes.addProxyAttribute(jawCtrl,
                                                     mouthBlendshapeCtrl,
                                                     attr,
                                                     channelBox=True,
                                                     nonKeyable=False)

        # Add proxy attrs feet ----------------------------
        if toesExist:
            attributes.addProxyAttribute(godNode, footLNode, toeLVisAttr, proxyAttr="toesLVis", nonKeyable=True)
            attributes.addProxyAttribute(godNode, footRNode, toeRVisAttr, proxyAttr="toesRVis", nonKeyable=True)

        # Turn off .prepopulate attribute, solved cycle issues related to disabling non uniform scale ----------------
        for i in zapi.nodesByNames(cmds.ls(type="controller")):
            pre = i.prepopulate
            if not pre.isDestination:
                pre.set(0)

        # Foot break attributes default values to 65.0 -----------------------------------
        cmds.addAttr('{}.footBreak'.format(footLNode), edit=True, defaultValue=65.0)
        cmds.addAttr('{}.footBreak'.format(footRNode), edit=True, defaultValue=65.0)
        cmds.setAttr('{}.footBreak'.format(footLNode), 65.0)
        cmds.setAttr('{}.footBreak'.format(footRNode), 65.0)

        # Disable non-uniform scale ---------------------------
        attributes.disableNonUniformScale(headNode)
        attributes.disableNonUniformScale(godNode)
        attributes.disableNonUniformScale(footLNode)
        attributes.disableNonUniformScale(footRNode)
