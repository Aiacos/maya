"""PivotsAtOriginCheck checks transforms of polygon objects are at the origin. """

import maya.cmds as mc

from .abstract_check.abstract_check import AbstractCheck


class PivotsAtOriginCheck(AbstractCheck):
    """PivotsAtOriginCheck checks transforms of polygon objects are at the origin.
        this is needed for some workflows for game rigs but is disabled by default.

    Args:
        namespace (str or None): str namespace to run checks on or None to search everything in the scene
    """

    def __init__(self, namespace):
        AbstractCheck.__init__(self, namespace)

        self.position = 10400
        self.check_type = "warning"
        self.name = "Pivot At Origin"
        self.one_line = "Checks if polygon objects pivot is at origin"
        self.explanation = (
            "Checks if 'mesh' parent transforms pivots are at the world origin.\n"
            "This is useful mostly for game rigs (but not only).\n"
            "Select' - Selects transforms with pivot not at world origin.\n"
            "'Fix' - moves the pivot to world origin."
        )
        self.can_select = True
        self.can_fix = True

        self.selection_list = []

    def run_check(self):  # REIMPLEMENTED!
        """This method run the check on the scene. if this method returns True the check passed.
            returns False means the check failed. subclasses will reimplement this method.
        """
        self.selection_list = self._get_mesh_transforms_with_wrong_pivot()

        return False if self.selection_list else True

    def _get_mesh_transforms_with_wrong_pivot(self):
        """Return UUIDs of polygon transforms that their pivot is not at world origin. """
        transforms_list = []

        for mesh in self.get_all_meshes(True):
            mesh_transform = mc.listRelatives(mesh, parent=True, fullPath=True)[0]
            for axis_pos in mc.xform(mesh_transform, q=True, ws=True, pivots=True):
                if round(float(axis_pos), 3) != 0.000:
                    transforms_list.append(mc.ls(mesh_transform, uuid=True)[0])

        return list(set(transforms_list))

    def run_select(self):  # REIMPLEMENTED!
        """This method should select objects in Maya that failed the test. subclasses will reimplement this. """
        self.selection_list = self._get_mesh_transforms_with_wrong_pivot()
        long_names = mc.ls(self.selection_list, long=True)
        mc.select(long_names)

        print("[{0}] selected: <{1}> {2}".format(self, len(long_names), long_names))

    def run_fix(self):  # REIMPLEMENTED!
        """This method will fix objects in the scene so the check will pass. subclasses will reimplement this. """
        self.selection_list = self._get_mesh_transforms_with_wrong_pivot()
        long_names = mc.ls(self.selection_list, long=True)

        for trans in long_names:
            mc.xform(trans, ws=True, pivots=[0, 0, 0])

        print("[{0}] fixed: <{1}> {2}".format(self, len(long_names), long_names))
