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

"""TurtleNodes checks for turtle nodes in scene. """

import maya.cmds as mc

from arise.rig_exporter.checks.abstract_check.abstract_check import AbstractCheckData
from arise.utils.decorators_utils import simple_catch_error_dec

class TurtleNodes(AbstractCheckData):
    """Check for turtle nodes in scene. """

    def __init__(self, main):
        AbstractCheckData.__init__(self, main)

        self.name = "Remove 'Turtle' plugin"
        self.info = (
            "Checks if 'Turtle' plugin is loaded and helps remove it.\n"
            "By unloading 'Turtle' we prevent scenes referencing the rig from creating 'Turtle' nodes."
        )
        self.has_fix = True
        self.type = "warning"
        self.error_msg = ""
        self.position = 100

    def check(self):
        """Check logic subclasses will be placed here. (access IoMainWindow with self.main).

        Returns:
            bool: True if passed else False
        """
        error_msg = ""

        if mc.pluginInfo('Turtle.mll', loaded=True, q=True):
            error_msg += "'Turtle' plugin loaded."

            types = mc.pluginInfo('Turtle.mll', dependNode=True, q=True)
            nodes = mc.ls(type=types, long=True)

            if nodes:
                error_msg += "\nalso found 'Turtle' nodes in the scene."

        if error_msg:
            self.error_msg = error_msg
            return False

        return True

    @simple_catch_error_dec
    def run_fix(self):  # REIMPLEMENTED (to override undo decorator since this fix doesn't support undo)
        """Run check fix by UI. """
        self.fix()
        self._status = self.check()


    def fix(self):
        """Check fix logic subclasses will be placed here. (access IoMainWindow with self.main). """
        types = mc.pluginInfo('Turtle.mll', dependNode=True, q=True)
        nodes = mc.ls(type=types, long=True)

        if nodes:
            mc.lockNode(nodes, lock=False)
            mc.delete(nodes)

        mc.flushUndo()
        mc.unloadPlugin('Turtle.mll')
        mc.flushUndo()
