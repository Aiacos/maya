"""UvSetsCheck checks empty or more then one UV set per 'mesh'. """

import maya.cmds as mc

from .abstract_check.abstract_check import AbstractCheck

DEFAULT_FIRST_SET = "map1"


class UvSetsCheck(AbstractCheck):
    """UvSetsCheck checks empty or more then one UV set per 'mesh'.

    Args:
        namespace (str or None): str namespace to run checks on or None to search everything in the scene
    """

    def __init__(self, namespace):
        AbstractCheck.__init__(self, namespace)

        self.position = 10200
        self.check_type = "warning"
        self.name = "UV Sets"
        self.one_line = "Checks UVs for errors"
        self.explanation = (
            "Checks all polygon meshes UvSets that:\n"
            "1) they are not empty\n"
            "2) the first UV set is named 'map1'\n"
            "(since some Maya scripts expect that name).\n"
            "'Select' - selects parent transforms of meshes with UvSet errors.\n"
            "'Fix' - TRIES to fix the UVs by renaming first UvSet and deleting\n"
            "any extra empty UvSets. but won't be able to fix empty first UvSet"
        )
        self.can_select = True
        self.can_fix = True

        self.selection_list = []

    def run_check(self):  # REIMPLEMENTED!
        """This method run the check on the scene. if this method returns True the check passed.
            returns False means the check failed. subclasses will reimplement this method.
        """
        self.selection_list = self._get_meshes_with_bad_uvs()

        return False if self.selection_list else True

    def _get_meshes_with_bad_uvs(self):
        """Return UUIDs of 'mesh' nodes with bad UVs sets.

        Returns:
            list: of UUIDs of 'mesh' nodes
        """
        meshes_list = []

        for mesh in self.get_all_meshes(True):
            sets_names = mc.polyUVSet(mesh, q=True, auv=True)

            if not sets_names:
                meshes_list.append(mc.ls(mesh, uuid=True)[0])
                continue

            if sets_names[0] != DEFAULT_FIRST_SET:
                meshes_list.append(mc.ls(mesh, uuid=True)[0])
                continue

            for name in sets_names:
                if mc.polyEvaluate(mesh, uv=True, uvs=name) == 0:
                    meshes_list.append(mc.ls(mesh, uuid=True)[0])
                    break

        return meshes_list

    def run_select(self):  # REIMPLEMENTED!
        """This method should select objects in Maya that failed the test. subclasses will reimplement this. """
        self.selection_list = self._get_meshes_with_bad_uvs()
        long_names = mc.ls(self.selection_list, long=True)

        mc.select(clear=True)
        for mesh in long_names:
            parent_transform = mc.listRelatives(mesh, parent=True, fullPath=True)[0]
            mc.select(parent_transform, add=True)

        print("[{0}] selected (parent transforms): <{1}> {2}".format(self, len(long_names), long_names))

    def run_fix(self):  # REIMPLEMENTED!
        """This method will fix objects in the scene so the check will pass. subclasses will reimplement this. """
        self.selection_list = self._get_meshes_with_bad_uvs()
        long_names = mc.ls(self.selection_list, long=True)

        for mesh in long_names:
            sets_names = mc.polyUVSet(mesh, q=True, auv=True)
            mc.lockNode(mesh, lock=False)

            if not sets_names:
                continue

            if sets_names[0] != DEFAULT_FIRST_SET:
                mc.polyUVSet(mesh, uvs=sets_names[0], rename=True, newUVSet=DEFAULT_FIRST_SET)

            for name in sets_names[1:]:
                if mc.polyEvaluate(mesh, uv=True, uvs=name) == 0:
                    mc.polyUVSet(mesh, delete=True, uvs=name)

        print("[{0}] attempted to fix: <{1}> {2}".format(self, len(long_names), long_names))
