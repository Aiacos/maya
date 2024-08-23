"""
SymmetricalCheck checks for vertices on both sides of the X plane that
don't have a matching vertex on the other side.
"""

import maya.cmds as mc

from .abstract_check.abstract_check import AbstractCheck

ROUND = 2  # lower int less accurate.


class SymmetricalCheck(AbstractCheck):
    """Checks for vertices on both sides of the X plane that don't have a matching vertex on the other side.

    Args:
        namespace (str or None): str namespace to run checks on or None to search everything in the scene
    """

    def __init__(self, namespace):
        AbstractCheck.__init__(self, namespace)

        self.position = 20300
        self.check_type = "minor_warning"
        self.name = "Symmetrical"
        self.one_line = "Checks 'mesh' nodes vertices are symmetrical on the YZ plane"
        self.explanation = (
            "Checks if all vertices have a mirrored vertex on YZ plane.\n"
            "It's important the model will be on the world origin\n"
            "facing world +Z axis so it's sides are on the +X and -X axis.\n"
            "'Select' - selects unsymmetrical vertices.\n"
        )
        self.can_select = True
        self.can_fix = False

        self.selection_list = []

    def run_check(self):  # REIMPLEMENTED!
        """This method run the check on the scene. if this method returns True the check passed.
            returns False means the check failed. subclasses will reimplement this method.
        """
        self.selection_list = self._get_unsymmetrical_verts()

        return False if self.selection_list else True

    def _get_unsymmetrical_verts(self):
        """Return long names of unsymmetrical vertices. """
        # using nested dicts instead of a list of positions for speed as this check is slow.
        verts_list = []
        x_axis_dict = {}

        for mesh in self.get_all_meshes(True):
            all_verts = mc.ls("{0}.vtx[:]".format(mesh), flatten=True, long=True)

            for vert in all_verts:
                pos = mc.xform(vert, q=True, ws=True, t=True)
                y_axis_dict = x_axis_dict.setdefault(round(pos[0], ROUND), {})
                z_axis_dict = y_axis_dict.setdefault(round(pos[1], ROUND), {})
                z_axis_dict[round(pos[2], ROUND)] = vert

        for x_key in x_axis_dict:
            for y_key in x_axis_dict[x_key]:
                for z_key in x_axis_dict[x_key][y_key]:

                    oppsite_y_dict = x_axis_dict.get(x_key * -1.0, {})
                    oppsite_z_dict = oppsite_y_dict.get(y_key, {})
                    if not oppsite_z_dict.get(z_key, None):
                        verts_list.append(x_axis_dict[x_key][y_key][z_key])

        return verts_list

    def run_select(self):  # REIMPLEMENTED!
        """This method should select objects in Maya that failed the test. subclasses will reimplement this. """
        self.selection_list = self._get_unsymmetrical_verts()
        mc.selectMode(component=True)
        mc.selectType(polymeshVertex=True)
        mc.select(self.selection_list)

        print("[{0}] selected: <{1}> {2}".format(self, len(self.selection_list), self.selection_list))
