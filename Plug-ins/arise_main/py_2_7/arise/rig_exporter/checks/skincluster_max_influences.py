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

"""Checks how many influences skinClusters have, if above 4 - gives warning. """

import maya.cmds as mc

from arise.rig_exporter.checks.abstract_check.abstract_check import AbstractCheckData
from arise.utils.decorators_utils import simple_catch_error_dec

class SkinClusterMaxInfluences(AbstractCheckData):
    """Check for 4 influences per skinCluster."""

    def __init__(self, main):
        AbstractCheckData.__init__(self, main)

        self.name = "OPTIONAL: SkinClusters Max 4 Influences"
        self.info = "Ensures all skinClusters enforce a max of 4 influences for optimized game rigs."
        self.has_fix = True
        self.type = "warning"
        self.error_msg = ""
        self.position = 700

    def check(self):
        """Check that each skinCluster enforces max 4 influences."""
        error_count = 0

        skin_clusters = []
        for sc in mc.ls(type="skinCluster"):
            user_attrs = mc.listAttr(sc, userDefined=True) or []
            if not any(attr.startswith("io_uuid") for attr in user_attrs):
                skin_clusters.append(sc)

        if not skin_clusters:
            return True

        for sc in skin_clusters:
            maintain_attr = sc + ".maintainMaxInfluences"
            max_inf_attr = sc + ".maxInfluences"

            maintain = mc.getAttr(maintain_attr) if mc.objExists(maintain_attr) else None
            max_inf = mc.getAttr(max_inf_attr) if mc.objExists(max_inf_attr) else None

            if maintain is not True or max_inf != 4:
                error_count += 1


        if error_count:
            self.error_msg = "Found {0} skinClusters not enforcing max 4 influences.".format(error_count)
            return False

        return True

    @simple_catch_error_dec
    def run_fix(self):
        self.fix()
        self._status = self.check()

    def fix(self):
        """Enable maintainMaxInfluences and set maxInfluences to 4 for all skinClusters."""
        fixed_clusters = []
        skin_clusters = []
        for sc in mc.ls(type="skinCluster"):
            user_attrs = mc.listAttr(sc, userDefined=True) or []
            if not any(attr.startswith("io_uuid") for attr in user_attrs):
                skin_clusters.append(sc)

        if not skin_clusters:
            return

        for sc in skin_clusters:
            maintain_attr = sc + ".maintainMaxInfluences"
            max_inf_attr = sc + ".maxInfluences"

            if mc.objExists(maintain_attr) and not mc.getAttr(maintain_attr):
                mc.setAttr(maintain_attr, True)
                fixed_clusters.append(sc)

            if mc.objExists(max_inf_attr) and mc.getAttr(max_inf_attr) != 4:
                mc.setAttr(max_inf_attr, 4)
                fixed_clusters.append(sc)

        if fixed_clusters:
            fixed_clusters = list(set(fixed_clusters))
            print("Fixed skinClusters to enforce max 4 influences: {0}".format(fixed_clusters))
