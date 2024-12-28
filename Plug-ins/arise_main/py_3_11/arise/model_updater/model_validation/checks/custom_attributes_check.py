"""
CustomAttributesCheck checks for user defined attributes.
those often appear when importing FBX files but might also be desired.
"""

import maya.cmds as mc

from .abstract_check.abstract_check import AbstractCheck


class CustomAttributesCheck(AbstractCheck):
    """CustomAttributesCheck checks for user defined attributes.
        those often appear when importing FBX files but might also be desired.

    Args:
        namespace (str or None): str namespace to run checks on or None to search everything in the scene
    """

    def __init__(self, namespace):
        AbstractCheck.__init__(self, namespace)

        self.position = 20100
        self.check_type = "minor_warning"
        self.name = "Custom Attributes"
        self.one_line = "Checks transforms for custom attributes"
        self.explanation = (
            "Checks if transforms have custom attributes.\n"
            "Unwanted custom attributes usually appear when importing\n"
            "FBX files from another program but not necessarily all custom\n"
            "attributes are unwanted.\n"
            "'Fix' - deletes all custom attributes."
        )
        self.can_select = True
        self.can_fix = True

        self.selection_list = []

    def run_check(self):  # REIMPLEMENTED!
        """This method run the check on the scene. if this method returns True the check passed.
            returns False means the check failed. subclasses will reimplement this method.
        """
        self.selection_list = self._get_transforms_with_custom_attributes()

        return False if self.selection_list else True

    def _get_transforms_with_custom_attributes(self):
        """Return UUIDs of transforms with custom attributes on them. """
        transforms_list = []

        for trans in self.get_all_transforms():
            if mc.listAttr(trans, userDefined=True):
                transforms_list.append(mc.ls(trans, uuid=True)[0])

        return transforms_list

    def run_select(self):  # REIMPLEMENTED!
        """This method should select objects in Maya that failed the test. subclasses will reimplement this. """
        self.selection_list = self._get_transforms_with_custom_attributes()
        long_names = mc.ls(self.selection_list, long=True)
        mc.select(long_names)

        print("[{0}] selected: <{1}> {2}".format(self, len(long_names), long_names))

    def run_fix(self):  # REIMPLEMENTED!
        """This method will fix objects in the scene so the check will pass. subclasses will reimplement this. """
        self.selection_list = self._get_transforms_with_custom_attributes()
        long_names = mc.ls(self.selection_list, long=True)

        for trans in long_names:
            mc.lockNode(trans, lock=False)
            for attr in mc.listAttr(trans, userDefined=True):
                attr_path = "{0}.{1}".format(trans, attr)
                mc.setAttr(attr_path, lock=False)
                mc.deleteAttr(attr_path)

        print("[{0}] fixed: <{1}> {2}".format(self, len(long_names), long_names))
