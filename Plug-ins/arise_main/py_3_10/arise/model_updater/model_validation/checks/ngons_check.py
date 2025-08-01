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

"""NgonsCheck checks for polygons with more then 4 sides. """

import maya.cmds as mc

from .abstract_check.abstract_check import AbstractCheck


class NgonsCheck(AbstractCheck):
    """Checks for polygons with five or more sides.

    Args:
        namespace (str or None): str namespace to run checks on or None to search everything in the scene
    """

    def __init__(self, namespace):
        AbstractCheck.__init__(self, namespace)

        self.position = 20400
        self.check_type = "minor_warning"
        self.name = "Ngons"
        self.one_line = "Checks for polygons with five or more sides"
        self.explanation = (
            "Models with ngons can be rigged but usually don't deform well.\n"
            "'Select' - selects ngons faces.\n"
            "'Fix' - tries to fix the ngons by adding edges.\n"
            "It's best to fix ngons manually."
        )
        self.can_select = True
        self.can_fix = True

        self.selection_list = []

    def run_check(self):  # REIMPLEMENTED!
        """This method run the check on the scene. if this method returns True the check passed.
            returns False means the check failed. subclasses will reimplement this method.
        """
        self.selection_list = self._get_ngons_faces()

        return False if self.selection_list else True

    def _get_ngons_faces(self):
        """Return list of lists of ngons polygons long names. """
        ngons_list = []

        mc.select(clear=True)
        for mesh in self.get_all_meshes(True):
            mc.select("{0}.f[:]".format(mesh))
            result = mc.polySelectConstraint(
                mode=2,  # selected.
                type=0x0008,  # faces.
                returnSelection=True,  # return a list of faces.
                size=3,  # Ngons faces.
            )

            mc.polySelectConstraint(mode=0)  # turn off selection constraint.
            mc.select(clear=True)

            if result:
                ngons_list.append(mc.ls(result, long=True))

        return ngons_list

    def run_select(self):  # REIMPLEMENTED!
        """This method should select objects in Maya that failed the test. subclasses will reimplement this. """
        self.selection_list = self._get_ngons_faces()
        mc.selectMode(component=True)
        mc.selectType(polymeshFace=True)
        mc.select(clear=True)

        for mesh_polygons in self.selection_list:
            mc.select(mesh_polygons, add=True)

        print("[{0}] selected: <{1}> {2}".format(self, len(self.selection_list), self.selection_list))

    def run_fix(self):  # REIMPLEMENTED!
        """This method will fix objects in the scene so the check will pass. subclasses will reimplement this. """
        self.selection_list = self._get_ngons_faces()

        for mesh_polygons in self.selection_list:
            mc.polyTriangulate(mesh_polygons, constructionHistory=False)

        print("[{0}] fixed: <{1}> {2}".format(self, len(self.selection_list), self.selection_list))
