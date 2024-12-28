"""InstancesCheck Checks for instances in the scene. """

import maya.cmds as mc
import maya.OpenMaya as om

from .abstract_check.abstract_check import AbstractCheck


class InstancesCheck(AbstractCheck):
    """Checks for instances in the scene.

    Args:
        namespace (str or None): str namespace to run checks on or None to search everything in the scene
    """

    def __init__(self, namespace):
        AbstractCheck.__init__(self, namespace)

        self.position = 600
        self.check_type = "error"
        self.name = "Instances"
        self.one_line = "Checks for instances"
        self.explanation = (
            "Checks if there are instances as 'Model Updater' doesn't work well with them.\n"
            "'Select' - selects instances.\n"
            "'Fix' - un-instance those objects and renames them (does not delete them)."
        )
        self.can_select = True
        self.can_fix = True

        self.selection_list = []

    def run_check(self):  # REIMPLEMENTED!
        """This method run the check on the scene. if this method returns True the check passed.
            returns False means the check failed. subclasses will reimplement this method.
        """
        self.selection_list = self._get_instances()

        return False if self.selection_list else True

    def _get_instances(self):
        """Return list of all objects that are instances. """
        instances_list = []
        iter_dag = om.MItDag(om.MItDag.kBreadthFirst)
        while not iter_dag.isDone():
            instanced = om.MItDag.isInstanced(iter_dag)

            if instanced:
                instances_list.append(iter_dag.fullPathName())

            iter_dag.next()

        ns_instances = [inst for inst in instances_list if inst in mc.ls(self.namespace_str(), long=True)]

        return ns_instances

    def run_select(self):  # REIMPLEMENTED!
        """This method should select objects in Maya that failed the test. subclasses will reimplement this. """
        self.selection_list = self._get_instances()
        mc.select(self.selection_list)

        print("[{0}] selected: <{1}> {2}".format(self, len(self.selection_list), self.selection_list))

    def run_fix(self):  # REIMPLEMENTED!
        """This method will fix objects in the scene so the check will pass. subclasses will reimplement this. """
        self.selection_list = self._get_instances()

        for _ in [0, 1, 2, 3, 4]:  # run 5 iteration of un-instancing.
            self.uninstance_nodes(self._get_instances())

        print("[{0}] un-instanced: <{1}> {2}".format(self, len(self.selection_list), self.selection_list))

    @staticmethod
    def uninstance_nodes(nodes):
        """Un-instance provided nodes

        Args:
            nodes (list): of long name nodes to un-instance
        """
        for node in nodes:
            if not mc.objExists(node):
                continue

            parent = mc.listRelatives(node, parent=True, fullPath=True) or []

            to_duplicate = parent[0] if parent else node
            mc.lockNode(to_duplicate, lock=False)
            mc.duplicate(to_duplicate, renameChildren=True)
            mc.delete(to_duplicate)
