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

"""NamespacesCheck checks there are no namespaces. """

import maya.cmds as mc

from .abstract_check.abstract_check import AbstractCheck

IGNORE_NAMESPACES = [":UI", ":shared"]


class NamespacesCheck(AbstractCheck):
    """Checks there are no namespaces.

    Args:
        namespace (str or None): str namespace to run checks on or None to search everything in the scene
    """

    def __init__(self, namespace):
        AbstractCheck.__init__(self, namespace)

        self.position = 100
        self.check_type = "error"
        self.name = "Namespaces"
        self.one_line = "Checks for namespaces"
        self.explanation = (
            "Checks if namespaces are used in the scene.\n"
            "Namespaces are usually used when referencing or importing.\n"
            "It is essential to pass this check to use the'Model Updater'.\n"
            "'Select' - selects nodes in the namespaces.\n"
            "'Fix' - either imports the reference or deletes the namespace."
        )
        self.can_select = True
        self.can_fix = True

        self.selection_list = []

    def run_check(self):  # REIMPLEMENTED!
        """This method run the check on the scene. if this method returns True the check passed.
            returns False means the check failed. subclasses will reimplement this method.
        """
        self.selection_list = self._get_namespaces()

        return False if self.selection_list else True

    def _get_namespaces(self):
        """Return names of namespaces.

        Returns:
            list: of namespaces
        """
        mc.namespace(setNamespace=":")
        namespace = ":{0}".format(self.namespace if self.namespace else "")
        existing_ns = mc.namespaceInfo(namespace, absoluteName=True, listOnlyNamespaces=True, recurse=True) or []
        existing_ns = [space for space in existing_ns if space not in IGNORE_NAMESPACES]
        existing_ns.sort(key=lambda a: len(a.split(":")))
        existing_ns.reverse()

        return existing_ns

    def import_or_remove_top_refs(self):
        """Imports or removes references in the scene based on if they are loaded. """
        for ref_path in mc.file(q=True, reference=True) or []:

            if mc.referenceQuery(ref_path, isLoaded=True):
                mc.file(ref_path, importReference=True)

            else:
                mc.file(ref_path, removeReference=True)

        if mc.file(q=True, reference=True) or []:
            self.import_or_remove_top_refs()

    def run_select(self):  # REIMPLEMENTED!
        """This method should select objects in Maya that failed the test. subclasses will reimplement this. """
        mc.select(clear=True)

        self.selection_list = self._get_namespaces()
        for namespace in self.selection_list:
            mc.select(mc.namespaceInfo(namespace, listOnlyDependencyNodes=True), add=True)

        print("[{0}] selected: <{1}> {2}".format(self, len(self.selection_list), self.selection_list))

    def run_fix(self):  # REIMPLEMENTED!
        """This method will fix objects in the scene so the check will pass. subclasses will reimplement this. """
        self.selection_list = self._get_namespaces()

        self.import_or_remove_top_refs()

        for space in self._get_namespaces():
            if mc.namespace(exists=space):
                mc.namespace(removeNamespace=space, mergeNamespaceWithRoot=True)

        print("[{0}] namespaces removed: <{1}> {2}".format(self, len(self.selection_list), self.selection_list))
