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

"""UniqueNamesCheck checks all transforms have a unique name. """

import maya.cmds as mc

from .abstract_check.abstract_check import AbstractCheck

SUFFIX = ["_geo", "_grp", "_mdl"]


class UniqueNamesCheck(AbstractCheck):
    """Checks all mesh, nurbsCurves and NurbsSurfaces don't have any history.

    Args:
        namespace (str or None): str namespace to run checks on or None to search everything in the scene
    """

    def __init__(self, namespace):
        AbstractCheck.__init__(self, namespace)

        self.position = 200
        self.check_type = "error"
        self.name = "Unique Names"
        self.one_line = "Check all transform nodes have a unique short name"
        self.explanation = (
            "All transform nodes must have a unique short name.\n"
            "The 'Model Updater' requires unique names to transfer data, such as\n"
            "weights, between models. Therefore, it is essential to pass this check.\n"
            "'Select' - selects transforms with repeating short names.\n"
            "'Fix' - automatically rename them with a unique name."
        )
        self.can_select = True
        self.can_fix = True

        self.selection_list = []

    def run_check(self):  # REIMPLEMENTED!
        """This method run the check on the scene. if this method returns True the check passed.
            returns False means the check failed. subclasses will reimplement this method.
        """
        self.selection_list = self._get_transforms_without_unique_names()

        return False if self.selection_list else True

    def _get_transforms_without_unique_names(self):
        """Return transforms nodes UUIDs that do not have a unique short name.

        Returns:
            list: of transforms UUIDs that don't have unique short name
        """
        transforms_list = []
        for long_name in self.get_deformable_and_empty_transforms():
            uuid = mc.ls(long_name, uuid=True)[0]

            if not self._is_name_unique(obj_uuid=uuid):
                transforms_list.append(uuid)

        return transforms_list

    @staticmethod
    def _is_name_unique(obj_uuid):
        """Return True or False if obj is unique.

        Args:
            obj_uuid (str): the uuid of the object to check

        Return:
            bool: True if unique False if not
        """
        short_name = mc.ls(obj_uuid, shortNames=True)[0]
        if "|" in short_name:
            return False

        return True

    def run_select(self):  # REIMPLEMENTED!
        """This method should select objects in Maya that failed the test. subclasses will reimplement this. """
        self.selection_list = self._get_transforms_without_unique_names()
        long_names = mc.ls(self.selection_list, long=True)
        mc.select(long_names)

        print("[{0}] selected: <{1}> {2}".format(self, len(long_names), long_names))

    def run_fix(self):  # REIMPLEMENTED!
        """This method will fix objects in the scene so the check will pass. subclasses will reimplement this. """
        self.selection_list = self._get_transforms_without_unique_names()

        renamed_list = []
        for uuid in self.selection_list:
            if self._is_name_unique(obj_uuid=uuid):
                continue

            renamed_list.append(self.fix_transform_name(uuid))

        print("[{0}] renamed: <{1}> {2}".format(self, len(renamed_list), renamed_list))

    def fix_transform_name(self, uuid):
        """For uuid of a transform renames it to a unique name.

        Args:
            uuid (str): uuid of transform

        Returns:
            list: of 2 str first is old name second is new name
        """
        long_name = mc.ls(uuid, long=True)[0]
        new_short_name = self._find_unique_short_name(format_name=self._format_name(uuid))

        mc.lockNode(long_name, lock=False)
        mc.rename(long_name, new_short_name, ignoreShape=False)[0]

        # rename shape because sometimes shape is not renamed.
        shapes = mc.listRelatives(mc.ls(uuid, long=True)[0], children=True, shapes=True, noIntermediate=True) or []
        if len(shapes) == 1:
            shape_name = "{0}Shape".format(new_short_name)

            if shapes[0] != shape_name:
                mc.rename(shapes[0], shape_name)

        return long_name, new_short_name

    def _format_name(self, uuid):
        """Return a ready for format str short name that the number can be inserted in the right place.

        Args:
            uuid (str): uuid of the transform node

        Returns:
            str: ready for format str
        """
        short_name = mc.ls(uuid, shortNames=True)[0].rsplit("|", 1)[-1]
        if len(short_name) > 5:
            if short_name.lower()[-4:] in SUFFIX:
                return "{0}_{1}{2}".format(short_name[:-4], "{0}", short_name[-4:])

        return "{0}_{1}".format(short_name, "{0}")

    def _find_unique_short_name(self, format_name, number=1):
        """Return a unique short name by adding a number to the name.

        Args:
            format_name (str): ready for format short name to add a number to
            number (int, optional): used internally by this method. should be changed. Defaults to 0.

        Returns:
            str: unique short name
        """
        namespace = "{0}::".format(self.namespace) if self.namespace else "::"
        short_name = format_name.format(str(number).zfill(3))
        if not mc.ls("{0}{1}".format(namespace, short_name), shortNames=True, type="transform"):
            return short_name

        return self._find_unique_short_name(format_name, number+1)
