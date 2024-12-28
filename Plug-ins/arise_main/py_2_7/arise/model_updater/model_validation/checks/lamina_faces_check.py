"""LaminaFacesCheck checks if 2 faces share the same vertices and sit on top of each other with merged verts. """

import maya.cmds as mc

from .abstract_check.abstract_check import AbstractCheck


class LaminaFacesCheck(AbstractCheck):
    """Checks if 2 faces share the same vertices and sit on top of each other with merged verts.

    Args:
        namespace (str or None): str namespace to run checks on or None to search everything in the scene
    """

    def __init__(self, namespace):
        AbstractCheck.__init__(self, namespace)

        self.position = 10700
        self.check_type = "warning"
        self.name = "Lamina Faces"
        self.one_line = "Checks meshes for faces that share the same vertices"
        self.explanation = (
            "Lamina faces are two or more faces that share the same vertices and\n"
            "lie on top of each other with merged vertices. In other words, they\n"
            "occupy the exact same space in the object and are visually\n"
            "indistinguishable from each other.\n"
            "'Select' - selects lamina faces.\n"
            "'Fix' - delete lamina faces."
        )
        self.can_select = True
        self.can_fix = True

        self.selection_list = []

    def run_check(self):  # REIMPLEMENTED!
        """This method run the check on the scene. if this method returns True the check passed.
            returns False means the check failed. subclasses will reimplement this method.
        """
        self.selection_list = self._get_lamina_faces()

        return False if self.selection_list else True

    def _get_lamina_faces(self):
        """Return long names of faces that are lamina faces. """
        lamina_faces = []
        for mesh in self.get_all_meshes(True):
            results = mc.polyInfo(mesh, laminaFaces=True) or []

            if results:
                lamina_faces.extend(results)

        return lamina_faces

    def run_select(self):  # REIMPLEMENTED!
        """This method should select objects in Maya that failed the test. Subclasses will reimplement this. """
        self.selection_list = self._get_lamina_faces()
        mc.selectMode(component=True)
        mc.selectType(polymeshFace=True)
        mc.select(self.selection_list)

        print("[{0}] selected: <{1}> {2}".format(self, len(self.selection_list), self.selection_list))

    def run_fix(self):  # REIMPLEMENTED!
        """This method will fix objects in the scene so the check will pass. Subclasses will reimplement this. """
        self.selection_list = self._get_lamina_faces()
        mc.delete(self.selection_list)

        print("[{0}] fixed: <{1}> {2}".format(self, len(self.selection_list), self.selection_list))
