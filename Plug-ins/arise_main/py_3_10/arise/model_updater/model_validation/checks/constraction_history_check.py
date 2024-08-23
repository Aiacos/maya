"""ConstructionHistoryCheck checks all mesh, nurbsCurves and NurbsSurfaces don't have any history. """

import maya.cmds as mc

from .abstract_check.abstract_check import AbstractCheck

HISTORY_CLASSES = ["polyBase", "geometryFilter", "abstractBaseCreate"]


class ConstructionHistoryCheck(AbstractCheck):
    """Checks all mesh, nurbsCurves and NurbsSurfaces don't have any history.

    Args:
        namespace (str or None): str namespace to run checks on or None to search everything in the scene
    """

    def __init__(self, namespace):
        AbstractCheck.__init__(self, namespace)

        self.position = 300
        self.check_type = "error"
        self.name = "Construction History"
        self.one_line = "Check for construction history on objects"
        self.explanation = (
            "Checks all 'mesh', 'nurbsCurve', and 'nurbsSurface' nodes\n"
            "for construction history.\n"
            "This check must pass to use 'Model Updater'.\n"
            "'Select' - selects parent transforms with history.\n"
            "'Fix' - deletes their history."
        )
        self.can_select = True
        self.can_fix = True

        self.selection_list = []

    def run_check(self):  # REIMPLEMENTED!
        """This method run the check on the scene. if this method returns True the check passed.
            returns False means the check failed. subclasses will reimplement this method.
        """
        self.selection_list = self._get_transforms_with_history()

        return False if self.selection_list else True

    def _get_transforms_with_history(self):
        """Return transforms nodes UUIDs that have history in a list.

        Returns:
            list: of transforms UUIDs that have history
        """
        transforms_list = []
        for mesh in self.get_all_deformables(False):
            connection_nodes = mc.listConnections(mesh)
            if not connection_nodes:
                continue

            for node in connection_nodes:
                for inherit_type in mc.nodeType(node, inherited=True):
                    if inherit_type in HISTORY_CLASSES:
                        transform = mc.listRelatives(mesh, parent=True, fullPath=True)[0]
                        transforms_list.append(mc.ls(transform, uuid=True)[0])

        return list(set(transforms_list))

    def run_select(self):  # REIMPLEMENTED!
        """This method should select objects in Maya that failed the test. subclasses will reimplement this. """
        long_names = mc.ls(self.selection_list, long=True)
        mc.select(long_names)

        print("[{0}] selected: <{1}> {2}".format(self, len(long_names), long_names))

    def run_fix(self):  # REIMPLEMENTED!
        """This method will fix objects in the scene so the check will pass. subclasses will reimplement this. """
        long_names = mc.ls(self.selection_list, long=True)
        mc.delete(long_names, constructionHistory=True)

        print("[{0}] fixed: <{1}> {2}".format(self, len(long_names), long_names))
