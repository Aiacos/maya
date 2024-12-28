"""
ExtraNodesCheck checks for unknown nodes, disconnected nodes, display layer nodes, cameras, image planes,
annotations, distance nodes, lights, disconnected_shaders.
"""

import maya.cmds as mc
from maya import mel

from .abstract_check.abstract_check import AbstractCheck

NODES_DAG_TYPES = [
    "annotationShape", "distanceDimShape", "imagePlane", "paramDimension", "arcLengthDimension",
    "ambientLight", "directionalLight", "pointLight", "spotLight", "areaLight", "volumeLight",
    "greasePlaneRenderShape", 'sketchPlane',
]

NODES_DG_TYPES = [
    "animCurveTL", "animCurveTA", "animCurveTU",
]


# TODO: go over 'MLdeleteUnused' MEL command convert to python and only return the nodes not delete them.
# TODO: OR File->Optimize Scene Size has cleanup options I should look at for 'Unneeded Nodes'
class ExtraNodesCheck(AbstractCheck):
    """Check for disconnected nodes, display layer nodes, cameras, image planes, annotations,
        distance nodes, lights, disconnected_shaders.

    Args:
        namespace (str or None): str namespace to run checks on or None to search everything in the scene
    """

    def __init__(self, namespace):
        AbstractCheck.__init__(self, namespace)

        self.position = 10100
        self.check_type = "warning"
        self.name = "Extra Nodes"
        self.one_line = "Checks for extra nodes that should be removed"
        self.explanation = (
            "Checks for: unknown nodes, disconnected DG nodes, display layers, extra cameras,\n"
            "imagePlane, annotations, measurements, lights, disconnected shaders,\n"
            "and animation nodes.\n"
            "'Select' - selects the extra nodes (both DG and DAG nodes).\n"
            "'Fix' - deletes the extra nodes."
        )
        self.can_select = True
        self.can_fix = True

        self.selection_list = []

    def run_check(self):  # REIMPLEMENTED!
        """This method run the check on the scene. if this method returns True the check passed.
            returns False means the check failed. subclasses will reimplement this method.
        """
        self.selection_list = self._get_all_extra_nodes()

        return False if self.selection_list else True

    def _get_all_extra_nodes(self):
        """Return list of all extra nodes that shouldn't be in the scene.

        Returns:
            list: of UUIDs of those node
        """
        nodes_list = []
        nodes_list.extend(mc.ls(type="unknown"))
        nodes_list.extend(self._get_dag_dg_nodes())
        nodes_list.extend(self._get_cameras_nodes())
        nodes_list.extend(self._get_display_layers())
        nodes_list.extend(self._get_disconnected_shaders())

        return nodes_list

    def _get_dag_dg_nodes(self):
        """Return parent transform of all nodes types NODES_DAG_TYPES.

        Returns:
            list: of UUIDs of parent transform nodes
        """
        dag_dg_nodes = []
        for type_ in NODES_DAG_TYPES:
            for node in mc.ls(self.namespace_str(), type=type_, long=True) or []:
                parent_transform = mc.listRelatives(node, parent=True, fullPath=True, type="transform")

                if not parent_transform:
                    continue

                dag_dg_nodes.append(mc.ls(parent_transform[0], uuid=True)[0])

        for type_ in NODES_DG_TYPES:
            for node in mc.ls(self.namespace_str(), type=type_, long=True) or []:
                dag_dg_nodes.append(mc.ls(node, uuid=True)[0])

        return dag_dg_nodes

    def _get_cameras_nodes(self):
        """Return parent transform of all cameras that are not startup cameras.

        Returns:
            list: of UUIDs of parent transform nodes
        """
        dag_nodes = []
        for camera in mc.ls(self.namespace_str(), type='camera', l=True):
            camera_transform = mc.listRelatives(camera, parent=True, fullPath=True)[0]
            if not mc.camera(camera_transform, startupCamera=True, q=True):
                dag_nodes.append(mc.ls(camera_transform, uuid=True)[0])

        return dag_nodes

    def _get_display_layers(self):
        """Return all none default display layers nodes UUIDs.

        Returns:
            list: of UUIDs of display layers nodes
        """
        dag_nodes = []
        for layer in mc.ls(self.namespace_str(), type='displayLayer', l=True):
            if layer != "defaultLayer":
                dag_nodes.append(mc.ls(layer, uuid=True)[0])

        return dag_nodes

    def _get_disconnected_shaders(self):
        """Return all shaders that are disconnected from any meshes.

        Returns:
            list: of UUIDs of disconnected shaders
        """
        dag_nodes = []
        for set_ in mc.ls(sets=True, long=True):
            cmd = 'shadingGroupUnused("{0}");'.format(set_)
            if not mel.eval(cmd):
                continue

            shader = mc.listConnections("{0}.surfaceShader".format(set_), destination=False)
            if not shader:
                continue

            dag_nodes.append(shader[0])

        return dag_nodes

    def run_select(self):  # REIMPLEMENTED!
        """This method should select objects in Maya that failed the test. subclasses will reimplement this. """
        self.selection_list = self._get_all_extra_nodes()
        long_names = mc.ls(self.selection_list, long=True)
        mc.select(long_names)

        print("[{0}] selected: <{1}> {2}".format(self, len(long_names), long_names))

    def run_fix(self):  # REIMPLEMENTED!
        """This method will fix objects in the scene so the check will pass. subclasses will reimplement this. """
        count = 0
        names = []

        # Fix when deleting displayLayer using mc.delete leaves EnableOverrides as True on layer's objs.
        for display_layer in mc.ls(self._get_display_layers(), long=True):
            mc.lockNode(display_layer, lock=False)
            mel.eval('layerEditorDeleteLayer "{0}"'.format(display_layer))

            names.append(display_layer)
            count += 1

        self.selection_list = self._get_all_extra_nodes()
        long_names = mc.ls(self.selection_list, long=True)

        for node in long_names:
            mc.lockNode(node, lock=False)

            names.append(node)
            count += 1

        if long_names:
            mc.delete(long_names)

        count += mel.eval("MLdeleteUnused")

        print("[{0}] deleted nodes: <{1}> {2}".format(self, count, names))
