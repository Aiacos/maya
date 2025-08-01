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

"""HolesInMeshesCheck checks for edges on border of 'mesh' objects. """

import maya.cmds as mc

from .abstract_check.abstract_check import AbstractCheck


class HolesInMeshesCheck(AbstractCheck):
    """Checks for edges on border of 'mesh' objects.

    Args:
        namespace (str or None): str namespace to run checks on or None to search everything in the scene
    """

    def __init__(self, namespace):
        AbstractCheck.__init__(self, namespace)

        self.position = 20200
        self.check_type = "minor_warning"
        self.name = "Holes In Meshes"
        self.one_line = "Checks 'mesh' nodes for border edges"
        self.explanation = (
            "Looks for border edges indicating the 'mesh' isn't a closed mesh.\n"
            "Models with holes are common and can be rigged but it's good practice\n"
            "to check there are no unwanted holes.\n"
            "'Select' - selects all border edges.\n"
        )
        self.can_select = True
        self.can_fix = False

        self.selection_list = []

    def run_check(self):  # REIMPLEMENTED!
        """This method run the check on the scene. if this method returns True the check passed.
            returns False means the check failed. subclasses will reimplement this method.
        """
        self.selection_list = self._get_border_edges()

        return False if self.selection_list else True

    def _get_border_edges(self):
        """Return long names of border edges. """
        edges_list = []

        for mesh in self.get_all_meshes(True):
            edges = mc.polyListComponentConversion("{0}.f[:]".format(mesh), ff=True, te=True, border=True) or []
            edges_list.extend(edges)

        return edges_list

    def run_select(self):  # REIMPLEMENTED!
        """This method should select objects in Maya that failed the test. subclasses will reimplement this. """
        self.selection_list = self._get_border_edges()
        mc.selectMode(component=True)
        mc.selectType(polymeshEdge=True)
        mc.select(self.selection_list)

        print("[{0}] selected: <{1}> {2}".format(self, len(self.selection_list), self.selection_list))
