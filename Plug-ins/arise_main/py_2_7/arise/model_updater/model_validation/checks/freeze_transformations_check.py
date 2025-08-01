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

"""FreezeTransformations checks for transforms values on transforms. """

import maya.cmds as mc

from .abstract_check.abstract_check import AbstractCheck

FROZEN_MATRIX = [1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0]
ATTRIBUTES = [
    "translateX", "translateY", "translateZ",
    "rotateX", "rotateY", "rotateZ",
    "scaleX", "scaleY", "scaleZ",
]
CONVERSION = "unitConversion"


class FreezeTransformationsCheck(AbstractCheck):
    """Checks for transforms values on transforms.

    Args:
        namespace (str or None): str namespace to run checks on or None to search everything in the scene
    """

    def __init__(self, namespace):
        AbstractCheck.__init__(self, namespace)

        self.position = 400
        self.check_type = "error"
        self.name = "Freeze Transformations"
        self.one_line = "Checks for transformation values on transforms"
        self.explanation = (
            "Checks for transformation values like translation, rotation, and scale.\n"
            "Transformations should be frozen before rigging starts.\n"
            "This check must pass to use 'Model Updater'.\n"
            "'Select' - selects transforms with transformation values.\n"
            "'Fix' - freeze transformations. will disconnect/unlock attributes\n"
            "before freezing."
        )
        self.can_select = True
        self.can_fix = True

        self.selection_list = []

    def run_check(self):  # REIMPLEMENTED!
        """This method run the check on the scene. if this method returns True the check passed.
            returns False means the check failed. subclasses will reimplement this method.
        """
        self.selection_list = self._get_objects_with_transformations()

        return False if self.selection_list else True

    def _get_objects_with_transformations(self):
        """Return UUIDs of objects with transformations values.

        Returns:
            list: of UUIDs of transforms
        """
        transforms_list = []

        for transform in self.get_all_deformables_transforms():
            for value, frozen_val in zip(mc.xform(transform, q=True, os=True, matrix=True), FROZEN_MATRIX):
                if round(value, 5) != frozen_val:
                    transforms_list.append(mc.ls(transform, uuid=True)[0])

        return transforms_list

    def run_select(self):  # REIMPLEMENTED!
        """This method should select objects in Maya that failed the test. subclasses will reimplement this. """
        self.selection_list = self._get_objects_with_transformations()
        long_names = mc.ls(self.selection_list, long=True)
        mc.select(long_names)

        print("[{0}] selected: <{1}> {2}".format(self, len(long_names), long_names))

    def run_fix(self):  # REIMPLEMENTED!
        """This method will fix objects in the scene so the check will pass. subclasses will reimplement this. """
        self.selection_list = self._get_objects_with_transformations()
        long_names = mc.ls(self.selection_list, long=True)

        for transform in long_names:
            child_transforms = mc.listRelatives(transform, allDescendents=True, fullPath=True, type="transform")
            trans_list = child_transforms + [transform] if child_transforms else [transform]
            for trans in trans_list:
                for attr in ATTRIBUTES:
                    attr = "{0}.{1}".format(trans, attr)
                    if mc.getAttr(attr, lock=True):
                        mc.setAttr(attr, lock=False)

                    source = mc.listConnections(attr, plugs=True, destination=False, source=True) or []

                    if source:
                        mc.disconnectAttr(source[0], attr)

                        source_node = mc.ls(source[0], objectsOnly=True, long=True)[0]
                        if mc.objectType(source_node) == CONVERSION:
                            mc.lockNode(source_node, lock=False)
                            mc.delete(source_node)

            mc.makeIdentity(transform, apply=True)
            mc.delete(long_names, constructionHistory=True)

        print("[{0}] frozen: <{1}> {2}".format(self, len(long_names), long_names))
