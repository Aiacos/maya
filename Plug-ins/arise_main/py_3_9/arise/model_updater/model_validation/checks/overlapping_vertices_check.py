"""OverlappingVerticesCheck checks all mesh and nurbsCurves for overlapping verts. """

import maya.cmds as mc

from .abstract_check.abstract_check import AbstractCheck

MAX_DISTANCE = 0.0001


class OverlappingVerticesCheck(AbstractCheck):
    """Checks all mesh and nurbsCurves for overlapping verts.

    Args:
        namespace (str or None): str namespace to run checks on or None to search everything in the scene
    """

    def __init__(self, namespace):
        AbstractCheck.__init__(self, namespace)

        self.position = 10500
        self.check_type = "warning"
        self.name = "Overlapping Vertices"
        self.one_line = "Check for vertices on top of each other"
        self.explanation = (
            "Checks each 'mesh' node if they have vertices sharing the same\n"
            "point in space.\n"
            "'Select' - selects overlapping vertices.\n"
            "'Fix' - merges overlapping vertices."
        )
        self.can_select = True
        self.can_fix = True

        self.selection_list = []

    def run_check(self):  # REIMPLEMENTED!
        """This method run the check on the scene. if this method returns True the check passed.
            returns False means the check failed. subclasses will reimplement this method.
        """
        self.selection_list = self._get_overlapping_verts()

        return False if self.selection_list else True

    def _get_overlapping_verts(self):
        """Return list of all verts that are overlapping.

        Returns:
            list: of long names of verts
        """
        overlapping_list = []
        for mesh in self.get_all_meshes(True):
            mc.select("{0}.e[:]".format(mesh))

            result = mc.polySelectConstraint(
                length=1,  # activate by length.
                lengthbound=[0.0, MAX_DISTANCE],  # length of almost zero.
                mode=2,  # selected.
                type=0x8000,  # edges.
                returnSelection=True,  # returns list of edges with no length.
            )

            mc.polySelectConstraint(mode=0)  # turn off selection constraint.
            mc.select(clear=True)

            if not result:
                continue

            verts = mc.polyListComponentConversion(result, fromEdge=True, toVertex=True)
            if verts:
                overlapping_list.extend(verts)

        return overlapping_list

    def run_select(self):  # REIMPLEMENTED!
        """This method should select objects in Maya that failed the test. subclasses will reimplement this. """
        self.selection_list = self._get_overlapping_verts()
        mc.selectMode(component=True)
        mc.select(self.selection_list)

        print("[{0}] selected: <{1}> {2}".format(self, len(self.selection_list), self.selection_list))

    def run_fix(self):  # REIMPLEMENTED!
        """This method will fix objects in the scene so the check will pass. subclasses will reimplement this. """
        self.selection_list = self._get_overlapping_verts()
        for shape in mc.ls(self.selection_list, objectsOnly=True):
            mc.polyMergeVertex(shape, constructionHistory=False, distance=MAX_DISTANCE)

        print("[{0}] fixed: <{1}> {2}".format(self, len(self.selection_list), self.selection_list))
