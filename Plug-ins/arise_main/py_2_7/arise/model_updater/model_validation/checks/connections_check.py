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

"""Connections checks for incoming connections into transforms. """

import maya.cmds as mc

from .abstract_check.abstract_check import AbstractCheck

ATTRIBUTES = [
    "translate", "rotate", "scale",
    "translateX", "translateY", "translateZ",
    "rotateX", "rotateY", "rotateZ",
    "scaleX", "scaleY", "scaleZ",
]

CONVERSION = "unitConversion"


class ConnectionsCheck(AbstractCheck):
    """Checks for transforms values on transforms.

    Args:
        namespace (str or None): str namespace to run checks on or None to search everything in the scene
    """

    def __init__(self, namespace):
        AbstractCheck.__init__(self, namespace)

        self.position = 10300
        self.check_type = "warning"
        self.name = "Connections"
        self.one_line = "Checks for incoming connections"
        self.explanation = (
            "Checks 'mesh', nurbsCurve', 'nurbsSurface' parent transforms and\n"
            "empty transforms for incoming connections driving transformations.\n"
            "'Select' - selects those transforms.\n"
            "'Fix' - disconnects incoming connections."
        )
        self.can_select = True
        self.can_fix = True

        self.selection_list = []

    def run_check(self):  # REIMPLEMENTED!
        """This method run the check on the scene. if this method returns True the check passed.
            returns False means the check failed. subclasses will reimplement this method.
        """
        self.selection_list = self._get_transforms_with_connections()

        return False if self.selection_list else True

    def _get_transforms_with_connections(self):
        """Return UUIDs of transforms with incoming connections.

        Returns:
            list: of UUIDs of transforms
        """
        transforms_list = []

        for transform in self.get_deformable_and_empty_transforms():
            for attr in ATTRIBUTES:
                attr = "{0}.{1}".format(transform, attr)
                if mc.listConnections(attr, destination=False, source=True):
                    transforms_list.append(mc.ls(transform, uuid=True)[0])
                    break

        return list(set(transforms_list))

    def run_select(self):  # REIMPLEMENTED!
        """This method should select objects in Maya that failed the test. subclasses will reimplement this. """
        self.selection_list = self._get_transforms_with_connections()
        long_names = mc.ls(self.selection_list, long=True)
        mc.select(long_names)

        print("[{0}] selected: <{1}> {2}".format(self, len(long_names), long_names))

    def run_fix(self):  # REIMPLEMENTED!
        """This method will fix objects in the scene so the check will pass. subclasses will reimplement this. """
        self.selection_list = self._get_transforms_with_connections()
        long_names = mc.ls(self.selection_list, long=True)

        for transform in long_names:
            for attr in ATTRIBUTES:
                attr = "{0}.{1}".format(transform, attr)
                source = mc.listConnections(attr, destination=False, source=True, plugs=True)

                if not source:
                    continue

                mc.setAttr(attr, lock=False)
                mc.setAttr(source[0], lock=False)

                mc.disconnectAttr(source[0], attr)

                source_node = mc.ls(source[0], objectsOnly=True, long=True)[0]
                if mc.objectType(source_node) == CONVERSION:
                    mc.lockNode(source_node, lock=False)
                    mc.delete(source_node)

        print("[{0}] fixed: <{1}> {2}".format(self, len(long_names), long_names))
