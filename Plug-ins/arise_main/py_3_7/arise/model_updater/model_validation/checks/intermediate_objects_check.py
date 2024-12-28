"""IntermediateObjects checks for nodes with the attribute 'intermediateObject' ticked on. """

import maya.cmds as mc

from .abstract_check.abstract_check import AbstractCheck


class IntermediateObjectsCheck(AbstractCheck):
    """checks for nodes with the attribute 'intermediateObject' ticked on..

    Args:
        namespace (str or None): str namespace to run checks on or None to search everything in the scene
    """

    def __init__(self, namespace):
        AbstractCheck.__init__(self, namespace)

        self.position = 500
        self.check_type = "error"
        self.name = "Intermediate Objects"
        self.one_line = "Checks for IntermediateObjects"
        self.explanation = (
            "Checks if there are objects with the attribute IntermediateObjects=1.\n"
            "Also check for more then one 'mesh' node under the same 'transform' node.\n"
            "Objects with IntermediateObjects usually are created when\n"
            "deformers have been used at some point.\n"
            "Intermediate Objects are hidden.\n"
            "This check must pass to use 'Model Updater'.\n"
            "'Select' - selects parent transforms.\n"
            "'Fix' - deletes 'IntermediateObjects' and combines 'mesh' nodes."
        )
        self.can_select = True
        self.can_fix = True

        self.selection_list = []

    def run_check(self):  # REIMPLEMENTED!
        """This method run the check on the scene. if this method returns True the check passed.
            returns False means the check failed. subclasses will reimplement this method.
        """
        self.selection_list = self._get_intermediate_objects()

        return False if self.selection_list or self._get_meshes_sharing_same_transform() else True

    def _get_intermediate_objects(self):
        """Return all objects that are intermediateObjects. """
        return mc.ls(self.namespace_str(), type="mesh", intermediateObjects=True, long=True)

    def _get_meshes_sharing_same_transform(self):
        """Return meshes under same transform but with intermediateObject=0.

        Return:
            list: of lists of meshes sharing the same parent transform
        """
        return_list = []

        parent_transforms = set()
        for mesh in mc.ls(self.namespace_str(), type="mesh", long=True):
            parent_transforms.add(mc.listRelatives(mesh, parent=True, fullPath=True)[0])

        for trans in parent_transforms:
            meshes = mc.listRelatives(
                trans,
                children=True,
                fullPath=True,
                type="mesh",
                shapes=True,
                noIntermediate=True,
            )
            if len(meshes) > 1:
                return_list.append(meshes)

        return return_list

    def run_select(self):  # REIMPLEMENTED!
        """This method should select objects in Maya that failed the test. subclasses will reimplement this. """
        self.selection_list = self._get_intermediate_objects()

        mc.select(clear=True)
        for obj in self.selection_list:
            mc.select(mc.listRelatives(obj, parent=True, fullPath=True), add=True)

        for meshes in self._get_meshes_sharing_same_transform():
            mc.select(mc.listRelatives(meshes[0], parent=True, fullPath=True), add=True)

        sel = self.selection_list + self._get_meshes_sharing_same_transform()
        print("[{0}] selected (parent transforms): <{1}> {2}".format(self, len(sel), sel))

    def run_fix(self):  # REIMPLEMENTED!
        """This method will fix objects in the scene so the check will pass. subclasses will reimplement this. """
        self.selection_list = self._get_intermediate_objects()

        for mesh in self.selection_list:
            mc.lockNode(mesh, lock=False)

            parent_transform = mc.listRelatives(mesh, parent=True, fullPath=True)[0]
            if len(mc.listRelatives(parent_transform, children=True)) > 1:
                mc.delete(mesh)
            else:
                mc.delete(parent_transform)

        meshes_merged = []
        for meshes in self._get_meshes_sharing_same_transform():
            transform = mc.listRelatives(meshes[0], parent=True, fullPath=True)[0]
            transform_short_name = transform.rsplit("|", 1)[-1]
            grandparent = mc.listRelatives(transform, parent=True, fullPath=True)

            mc.lockNode(transform, lock=False)
            for mesh in meshes:
                mc.lockNode(mesh, lock=False)

            meshes_merged.append(meshes)
            new_mesh = mc.polyUnite(meshes, ch=0, mergeUVSets=1)[0]
            uuid = mc.ls(new_mesh, uuid=True)[0]

            mc.rename(new_mesh, transform_short_name)

            if grandparent:
                if mc.objExists(grandparent[0]):  # Maya deletes grandparent transform if empty with polyUnite.
                    mc.parent(mc.ls(uuid)[0], grandparent[0])

        print("[{0}] deleted: <{1}> {2}".format(self, len(self.selection_list), self.selection_list))
        print("[{0}] ...and merged: <{1}> {2}".format(self, len(meshes_merged), meshes_merged))
