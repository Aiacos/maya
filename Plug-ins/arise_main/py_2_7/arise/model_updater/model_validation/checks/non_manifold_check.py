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

"""NonmanifoldCheck checks non-manifold edges. """

import maya.cmds as mc

from .abstract_check.abstract_check import AbstractCheck


class NonmanifoldCheck(AbstractCheck):
    """Checks non-manifold edges.

    Args:
        namespace (str or None): str namespace to run checks on or None to search everything in the scene
    """

    def __init__(self, namespace):
        AbstractCheck.__init__(self, namespace)

        self.position = 20500
        self.check_type = "minor_warning"
        self.name = "Non-Manifold"
        self.one_line = "Checks 'mesh' nodes for Non-Manifold edges"
        self.explanation = (
            "A non-manifold geometry is a 3D shape that cannot be unfolded into\n"
            "a 2D surface with all its normals pointing the same direction.\n"
            "Models can be non-manifold and rigged but it's good practice to\n"
            "check them before rigging starts.\n"
            "'Select' - selects non-manifold edges.\n"
        )
        self.can_select = True
        self.can_fix = False

        self.selection_list = []

    def run_check(self):  # REIMPLEMENTED!
        """This method run the check on the scene. if this method returns True the check passed.
            returns False means the check failed. subclasses will reimplement this method.
        """
        self.selection_list = self._get_non_manifold_edges()

        return False if self.selection_list else True

    def _get_non_manifold_edges(self):
        """Return long names of non-manifold edges. """
        edges_list = []

        for mesh in self.get_all_meshes(True):
            non_manifold_list = mc.polyInfo(mesh, nonManifoldEdges=True) or []
            non_manifold_list = mc.ls(non_manifold_list, long=True)
            edges_list.extend(non_manifold_list)

        return edges_list

    def run_select(self):  # REIMPLEMENTED!
        """This method should select objects in Maya that failed the test. subclasses will reimplement this. """
        self.selection_list = self._get_non_manifold_edges()
        mc.selectMode(component=True)
        mc.selectType(polymeshEdge=True)
        mc.select(self.selection_list)

        print("[{0}] selected: <{1}> {2}".format(self, len(self.selection_list), self.selection_list))
