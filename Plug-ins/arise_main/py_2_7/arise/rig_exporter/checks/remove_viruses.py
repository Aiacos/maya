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

"""Removes the known Maya viruses from the scene. This is a partial solution as it only removes the script nodes
and does not modifies the userSetup.py that might also be corrupted. """

import maya.cmds as mc

from arise.rig_exporter.checks.abstract_check.abstract_check import AbstractCheckData

INFECTED_SCRIPT_NODES_NAMES = ["vaccine_gene", "breed_gene", "MayaMelUIConfigurationFile"]


class RemoveViruses(AbstractCheckData):
    """Checks the Maya scene for the known viruses and removes them. """

    def __init__(self, main):
        AbstractCheckData.__init__(self, main)

        self.name = "Remove Viruses"
        self.info = (
            "Searches for script nodes that contain known viruses in Maya scenes.\n"
            "This is a partial solution and Maya's 'MayaScanner' plugin should be installed."
        )
        self.has_fix = True
        self.type = "warning"
        self.error_msg = ""
        self.position = 250

    def check(self):
        """Check logic subclasses will be placed here. (access IoMainWindow with self.main).

        Returns:
            bool: True if passed else False
        """
        error_msg = ""

        for infected_node in mc.ls(INFECTED_SCRIPT_NODES_NAMES, type="script") or []:
            error_msg += "found the virus '{0}' script node in the scene.".format(infected_node)

        if error_msg:
            self.error_msg = error_msg
            return False

        return True

    def fix(self):
        """Check fix logic subclasses will be placed here. (access IoMainWindow with self.main). """
        for infected_node in mc.ls(INFECTED_SCRIPT_NODES_NAMES, type="script") or []:
            mc.delete(infected_node)
            print("Deleted {0}".format(infected_node))
