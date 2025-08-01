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

"""FlippedNormalsCheck checks if polygon objects have flipped normals. """

import maya.cmds as mc

from .abstract_check.abstract_check import AbstractCheck

TEMP_NAME = "temp_duplicate_flipped_normal_check"


class FlippedNormalsCheck(AbstractCheck):
    """Checks if polygon objects have flipped normals.
        it's important to note that this check might give false positives.

    Args:
        namespace (str or None): str namespace to run checks on or None to search everything in the scene
    """

    def __init__(self, namespace):
        AbstractCheck.__init__(self, namespace)

        self.position = 10600
        self.check_type = "warning"
        self.name = "Flipped Normals"
        self.one_line = "Checks meshes for flipped polygons"
        self.explanation = (
            "Checks 'mesh' nodes for polygons that are facing in the opposite\n"
            "direction from the rest of the polygons.\n"
            "Please note that in some cases, this check may provide false positives.\n"
            "To see flipped polygons more clearly, it is recommended that you turn\n"
            "off the 'Two-Sided Lighting' option in the Lighting menu.\n"
            "'Select' - selects flipped polygons.\n"
            "'Fix' - conforms the mesh which MIGHT fix flipped polygons."
        )
        self.can_select = True
        self.can_fix = True

        self.selection_list = []

    def run_check(self):  # REIMPLEMENTED!
        """This method run the check on the scene. if this method returns True the check passed.
            returns False means the check failed. subclasses will reimplement this method.
        """
        self.selection_list = self._get_flipped_polygons()

        return False if self.selection_list else True

    def _get_flipped_polygons(self):
        """Return long names of polygon components with flipped normals (might give false results). """
        mc.select(cl=True)
        poly_list = []

        mesh_transforms = set()
        for mesh in self.get_all_meshes(True):
            mesh_transforms.add(mc.listRelatives(mesh, parent=True, fullPath=True)[0])

        for transform in mesh_transforms:
            original_meshes = mc.listRelatives(transform, children=True, fullPath=True, type="mesh")

            temp_duplicate = mc.duplicate(transform, name=TEMP_NAME, renameChildren=True)[0]
            temp_meshes = mc.listRelatives(temp_duplicate, children=True, fullPath=True, type="mesh")

            for temp_mesh, original_mesh in zip(temp_meshes, original_meshes):
                mc.select(cl=True)
                mc.polyNormal(temp_mesh, normalMode=2)
                selection = mc.ls(sl=True)

                if selection:
                    for poly in selection:
                        poly_list.append("{0}.{1}".format(original_mesh, poly.rsplit(".", 1)[-1]))

            mc.select(cl=True)
            mc.delete(temp_duplicate)

        return poly_list

    def run_select(self):  # REIMPLEMENTED!
        """This method should select objects in Maya that failed the test. subclasses will reimplement this. """
        self.selection_list = self._get_flipped_polygons()
        mc.selectMode(component=True)
        mc.selectType(polymeshFace=True)
        mc.select(self.selection_list)

        print("[{0}] selected: <{1}> {2}".format(self, len(self.selection_list), self.selection_list))

    def run_fix(self):  # REIMPLEMENTED!
        """This method will fix objects in the scene so the check will pass. subclasses will reimplement this. """
        mc.select(clear=True)
        self.selection_list = self._get_flipped_polygons()
        mc.selectMode(object=True)

        mesh_list = list(set(mc.ls(self.selection_list, objectsOnly=True, long=True)))
        for mesh in mesh_list:
            mc.select(clear=True)
            mc.polyNormal(mesh, normalMode=2, constructionHistory=False)  # conform mesh.

        print("[{0}] fixed: <{1}> {2}".format(self, len(mesh_list), mesh_list))
