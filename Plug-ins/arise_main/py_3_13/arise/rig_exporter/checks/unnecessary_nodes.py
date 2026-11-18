__LEGAL__ = """
# -----------------------------------------------------------------------------
#  Arise Rigging System 2026. All Rights Reserved.
#
#  This file is part of a proprietary software product. Unauthorized copying,
#  modification, distribution, decompiling, or use of this file, via any medium,
#  is strictly prohibited without explicit written permission from the copyright owner.
#
#  For licensing info, contact: info@ariserigging.com
# -----------------------------------------------------------------------------
"""

"""UnnecessaryNodes checks if there are any Maya nodes that should be removed. """

import maya.cmds as mc

from arise.rig_exporter.checks.abstract_check.abstract_check import AbstractCheckData
from arise.utils import module_loader_utils
from arise.utils.tagging_utils import CTRL_TAG

UNUSED_NODE_TYPES = (
    "constraint", "pairBlend", "groupId", "animCurve",
    "snapshot", "unitConversion",
)

class UnnecessaryNodes(AbstractCheckData):
    """Checks for Maya nodes that should be removed. """

    def __init__(self, main):
        AbstractCheckData.__init__(self, main)

        self.name = "Unnecessary Nodes"
        self.info = (
            "Checks for Maya nodes that should be removed like:\n"
            "animCurve<> nodes connected to ctrls, extra cameras, ngSkinTool nodes, unknown nodes,\n"
            "unassigned shaders, disconnected utility nodes, and empty display layers.\n"
            "Unloaded references are reported only."
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

        # animation nodes.
        for node_type in ["animCurveTL", "animCurveTA", "animCurveTU"]:
            anim_nodes = []
            for anim_node in mc.ls(type=node_type):
                output = mc.listConnections("{0}.output".format(anim_node), destination=True)

                if not output or mc.objExists("{0}.{1}".format(output[0], CTRL_TAG)):
                    anim_nodes.append(anim_node)
            if anim_nodes:
                error_msg += "found '{0}' (keyframe animation) nodes.\n".format(node_type)
                print("Found {0} nodes: {1}".format(node_type, anim_nodes))

        # camera nodes.
        extra_cameras = []
        for camera in mc.ls(type='camera', l=True):
            camera_transform = mc.listRelatives(camera, parent=True, fullPath=True)[0]
            if not mc.camera(camera_transform, startupCamera=True, q=True):
                extra_cameras.append(camera)
        if extra_cameras:
            error_msg += "found extra cameras in the scene.\n"
            print("Found extra cameras: {0}".format(extra_cameras))

        # ngSkinTool nodes.
        # TODO: add support for ngSkinTools2
        if 'ngSkinTools' in mc.pluginInfo(query=True, listPlugins=True):
            types = mc.pluginInfo('ngSkinTools.mll', dependNode=True, q=True)
            ng_nodes = mc.ls(type=types, long=True)
            if ng_nodes:
                error_msg += "found ngSkinTool nodes in the scene.\n"
                print("Found ngSkinTool nodes: {0}".format(ng_nodes))

        # unknown nodes.
        unknown_nodes = mc.ls(type="unknown")
        if unknown_nodes:
            error_msg += "found 'unknown' nodes in scene.\n"
            print("Found unknown nodes: {0}".format(unknown_nodes))

        unassigned_shaders = self.find_unassigned_shaders()
        if unassigned_shaders:
            error_msg += "found unassigned shaders in the scene.\n"
            print("Found unassigned shaders: {0}".format(unassigned_shaders))

        unused_nodes = self.find_unused_nodes()
        for node_type, nodes in unused_nodes.items():
            if nodes:
                error_msg += "found unused '{0}' nodes.\n".format(node_type)
                print("Found unused {0} nodes: {1}".format(node_type, nodes))

        empty_layers = self.find_empty_display_layers()
        if empty_layers:
            error_msg += "found empty display layers in the scene.\n"
            print("Found empty display layers: {0}".format(empty_layers))

        unloaded_references = self.find_unloaded_references()
        if unloaded_references:
            error_msg += "found unloaded references (report only).\n"
            print("Found unloaded references: {0}".format(unloaded_references))

        # TODO: unused deformers,
        # TODO: unused rendering nodes, empty transforms, empty render layers, empty sets,
        # TODO: unused referenced items, unused brushes (check File -> 'optimize Scene Size')
        # TODO: add check for unconnected nodes (?)

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
        self.delete_unassigned_shaders()
        self.delete_unused_nodes()
        self.delete_empty_display_layers()

    @staticmethod
    def find_empty_display_layers():
        """Find non-default, unlocked, local display layers without members. """
        empty_layers = []
        for layer in mc.ls(type="displayLayer", long=True):
            if mc.getAttr(layer + ".identification") == 0:
                continue
            if mc.lockNode(layer, query=True, lock=True)[0]:
                continue
            if mc.referenceQuery(layer, isNodeReferenced=True):
                continue
            if not mc.editDisplayLayerMembers(layer, query=True, ufe=True):
                empty_layers.append(layer)
        return empty_layers

    def delete_empty_display_layers(self):
        """Delete display layers that are still empty. """
        for layer in self.find_empty_display_layers():
            self.delete_node(layer)
            if not mc.objExists(layer):
                print("Deleted empty display layer: {0}".format(layer))

    @staticmethod
    def find_unused_nodes():
        """Find disconnected nodes, ignoring constraints' self-connections. """
        default_nodes = set(mc.ls(defaultNodes=True, long=True))
        unused = {}
        for node_type in UNUSED_NODE_TYPES:
            unused[node_type] = []
            for node in mc.ls(type=node_type, long=True):
                if node_type == "animCurve" and mc.nodeType(node) in (
                    "animCurveTL", "animCurveTA", "animCurveTU"
                ):
                    continue
                if node in default_nodes or mc.lockNode(node, query=True, lock=True)[0]:
                    continue
                if mc.referenceQuery(node, isNodeReferenced=True):
                    continue
                if mc.objectType(node, isAType="dagNode") and mc.listRelatives(node, children=True):
                    continue
                outputs = mc.listConnections(node, source=False, destination=True) or []
                if node_type == "constraint" and outputs:
                    outputs = [target for target in mc.ls(outputs, long=True) if target != node]
                if not outputs:
                    unused[node_type].append(node)
        return unused

    def delete_unused_nodes(self):
        """Delete nodes that still meet the unused-node criteria. """
        for nodes in self.find_unused_nodes().values():
            for node in nodes:
                self.delete_node(node)
                if not mc.objExists(node):
                    print("Deleted unused node: {0}".format(node))

    @staticmethod
    def find_unloaded_references():
        """Return unloaded references without modifying them. """
        unloaded = []
        for path in mc.file(query=True, reference=True) or []:
            reference = mc.referenceQuery(path, referenceNode=True)
            if not mc.referenceQuery(reference, isLoaded=True):
                unloaded.append(reference)
        return unloaded

    @staticmethod
    def find_unassigned_shaders():
        """Find non-default, unlocked materials with no populated downstream shading group. """
        default_nodes = set(mc.ls(defaultNodes=True, long=True))
        unassigned = []
        for shader in mc.ls(materials=True, long=True):
            if shader in default_nodes or mc.lockNode(shader, query=True, lock=True)[0]:
                continue
            history = mc.listHistory(shader, future=True, allFuture=True) or []
            shading_groups = mc.ls(history, type="shadingEngine", long=True) if history else []
            if not any(mc.sets(group, query=True) for group in shading_groups):
                unassigned.append(shader)
        return unassigned

    def delete_unassigned_shaders(self):
        """Delete non-default, unlocked shaders that have no assignments. """
        for shader in self.find_unassigned_shaders():
            self.delete_node(shader)
            if not mc.objExists(shader):
                print("Deleted unassigned shader: {0}".format(shader))

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

                if module_loader_utils.module_exists('ngSkinTools'):
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
