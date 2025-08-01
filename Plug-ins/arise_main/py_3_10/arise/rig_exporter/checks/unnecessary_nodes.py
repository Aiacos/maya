__LEGAL__ = """
# -----------------------------------------------------------------------------
#  Arise Rigging System 2025. All Rights Reserved.
#
#  This file is part of a proprietary software product. Unauthorized copying,
#  modification, distribution, decompiling, or use of this file, via any medium,
#  is strictly prohibited without explicit written permission from the copyright owner.
#
#  For licensing info, contact: info@ariserigging.com
# -----------------------------------------------------------------------------
"""

"""UnnecessaryNodes checks if there are any Maya nodes that should be removed. """

import imp
import maya.cmds as mc

from arise.rig_exporter.checks.abstract_check.abstract_check import AbstractCheckData
from arise.utils.tagging_utils import CTRL_TAG

class UnnecessaryNodes(AbstractCheckData):
    """Checks for Maya nodes that should be removed. """

    def __init__(self, main):
        AbstractCheckData.__init__(self, main)

        self.name = "Unnecessary Nodes"
        self.info = (
            "Checks for Maya nodes that should be removed like:\n"
            "animCurve<> nodes connected to ctrls, extra cameras, no ngSkinTool nodes, unknown nodes"
        )
        self.has_fix = True
        self.type = "warning"
        self.error_msg = ""
        self.position = 200

    def check(self):
        """Check logic subclasses will be placed here. (access IoMainWindow with self.main).

        Returns:
            bool: True if passed else False
        """
        error_msg = ""

        # TODO: change code structure to collect nodes it found and print them in Maya scriptEditor when checking.
        # animation nodes.
        for node_type in ["animCurveTL", "animCurveTA", "animCurveTU"]:
            for anim_node in mc.ls(type=node_type):
                output = mc.listConnections("{0}.output".format(anim_node), destination=True)

                if not output:
                    error_msg += "found '{0}' (keyframe animation) nodes.\n".format(node_type)
                    break

                if mc.objExists("{0}.{1}".format(output[0], CTRL_TAG)):
                    error_msg += "found '{0}' (keyframe animation) nodes.\n".format(node_type)
                    break

        # camera nodes.
        for camera in mc.ls(type='camera', l=True):
            camera_transform = mc.listRelatives(camera, parent=True, fullPath=True)[0]
            if not mc.camera(camera_transform, startupCamera=True, q=True):
                error_msg += "found extra cameras in the scene.\n"
                break

        # ngSkinTool nodes.
        # TODO: add support for ngSkinTools2
        if 'ngSkinTools' in mc.pluginInfo(query=True, listPlugins=True):
            types = mc.pluginInfo('ngSkinTools.mll', dependNode=True, q=True)
            if mc.ls(type=types, long=True):
                error_msg += "found ngSkinTool nodes in the scene.\n"

        # unknown nodes.
        if mc.ls(type="unknown"):
            error_msg += "found 'unknown' nodes in scene.\n"

        # TODO: unused constraints, unused pairBlends, unused deformers, unused skin influences,
        # TODO: unused groupID nodes, unused animation curves, unused snapshot nodes, unused unit conversion nodes,
        # TODO: unused rendering nodes, empty transforms, empty display layers, empty render layers, empty sets,
        # TODO: unused referenced items, unused brushes (check File -> 'optimize Scene Size')
        # TODO: add check for unconnected nodes (?)
        # TODO: add check for disconnected shaders (?)

        if error_msg:
            self.error_msg = error_msg
            return False

        return True

    def fix(self):
        """Check fix logic subclasses will be placed here. (access IoMainWindow with self.main). """
        self.fix_anim_curves()
        self.delete_extra_cameras()
        self.delete_ngskintool_nodes()
        self.delete_unknown_nodes()

    def fix_anim_curves(self):
        """Find then delete any anim curve that is time depended. """
        del_anim_nodes = []
        for node_type in ["animCurveTL", "animCurveTA", "animCurveTU"]:
            for anim_node in mc.ls(type=node_type):
                output = mc.listConnections("{0}.output".format(anim_node), destination=True)
                if not output:
                    del_anim_nodes.append(anim_node)

                elif mc.objExists("{0}.{1}".format(output[0], CTRL_TAG)):
                    del_anim_nodes.append(anim_node)

        for node in del_anim_nodes:
            self.delete_node(node)

        if del_anim_nodes:
            print("Deleted anim nodes: {0}".format(del_anim_nodes))

    def delete_extra_cameras(self):
        """Find then delete any extra cameras in the scene. """
        del_cameras = []
        for camera in mc.ls(type='camera', long=True):
            camera_transform = mc.listRelatives(camera, parent=True, fullPath=True)[0]
            if not mc.camera(camera_transform, startupCamera=True, q=True):
                del_cameras.append(camera)

        for node in del_cameras:
            self.delete_node(node)

        if del_cameras:
            print("Deleted cameras: {0}".format(del_cameras))

    @staticmethod
    def delete_ngskintool_nodes():
        """Find then delete ngSkinTool nodes. """
        if 'ngSkinTools' in mc.pluginInfo(query=True, listPlugins=True):
            types = mc.pluginInfo('ngSkinTools.mll', dependNode=True, q=True)
            if mc.ls(type=types, long=True):

                try:
                    imp.find_module('ngSkinTools')
                    found = True
                except ImportError:
                    found = False

                if found:
                    from ngSkinTools.layerUtils import LayerUtils
                    LayerUtils.deleteCustomNodes()

                    print("Deleted ngSkinTool nodes.")

    def delete_unknown_nodes(self):
        """Find and delete unknown nodes. """
        unknown_nodes = mc.ls(type="unknown")

        for node in unknown_nodes:
            self.delete_node(node)

        if unknown_nodes:
            print("Deleted unknown nodes: {0}".format(unknown_nodes))

    @staticmethod
    def delete_node(node):
        """Check if node is referenced or locked, then delete it. """
        if not mc.objExists(node):
            return

        if mc.referenceQuery(node, isNodeReferenced=True):
            mc.warning("Cannot delete referenced node: '{0}'".format(node))
            return

        if mc.lockNode(node, q=True, lock=True):
            mc.lockNode(node, lock=False)

        mc.delete(node)
