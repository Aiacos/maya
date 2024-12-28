"""GameFbxRigAction exports skeleton_grp and geometry_grp only as FBX file. """

import os

import maya.cmds as mc
from maya import mel

from arise.utils.decorators_utils import simple_catch_error_dec
from arise.utils.tagging_utils import (
    get_maya_nodes_with_tag, get_all_tagged_ctrl_item, MODELS_GRP_NAME, SKELETON_GRP_NAME,
)

CATEGORY = "arise_base_main_ctrl_tag"


class GameFbxRigAction(object):
    """Export skeleton_grp and geometry_grp only as FBX file. """
    def __init__(self):
        self.name = "Export Game FBX rig"
        self.info = (
            "Exports an FBX file containing only the 'geometry_grp' and the 'skeleton_grp'\n"
            "To the same path the rig gets exported to. only works with 'FollowSkeleton' or game nodes."
        )
        self.position = 1100
        self.is_checked = False
        self.post_action = True

    @staticmethod
    @simple_catch_error_dec
    def run_action(save_path):
        """Run export FBX rig.

        save_path (str): full save path
        """
        print("\n#########################################################")
        print("########## Action: 'Export Game FBX rig' START. #########")
        print("#########################################################\n")

        path = os.path.abspath(save_path).rsplit(".", 1)[0]
        fbx_path = "{0}.fbx".format(path)
        fbx_path = fbx_path.replace("\\", "/")

        mc.loadPlugin('fbxmaya.mll', quiet=True)

        for ctrl in get_all_tagged_ctrl_item():

            if not mc.listAttr(ctrl, category=CATEGORY):
                continue

            attr = "{0}.joints_visibility".format(ctrl)

            if not mc.objExists(attr):
                continue

            if mc.getAttr(attr, lock=True):
                continue

            if mc.listConnections(attr, source=True, destination=False):
                continue

            mc.setAttr(attr, 1)

        geo_grp = get_maya_nodes_with_tag(MODELS_GRP_NAME)
        skeleton_grp = get_maya_nodes_with_tag(SKELETON_GRP_NAME)
        if not geo_grp or not mc.objExists(geo_grp[0]) or not skeleton_grp or not mc.objExists(skeleton_grp[0]):
            return "'geometry_grp' or 'skeleton_grp' group does not exists. Aborting FBX export"

        if not mc.listRelatives(skeleton_grp, children=True):
            return "Empty 'skeleton_grp'. Aborting FBX export"

        mc.select(clear=True)
        mc.select(geo_grp[0])
        mc.select(skeleton_grp, add=True)

        mel.eval('FBXProperty "Export|IncludeGrp|Animation" -v false')
        mel.eval('FBXExportBakeComplexAnimation -v false')
        mel.eval('FBXExportAnimationOnly -v false')
        mel.eval('FBXExportInputConnections -v false')
        mel.eval('FBXExportInAscii -v false')
        mel.eval(('FBXExport -f \"{0}\" -s').format(fbx_path))

        print("FBX rig exported to: '{0}'".format(fbx_path))

        return "Action successful"
