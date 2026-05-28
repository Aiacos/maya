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

"""Checks for non-normalized skinCluster weights."""

import maya.cmds as mc
from arise.rig_exporter.checks.abstract_check.abstract_check import AbstractCheckData
from arise.utils.decorators_utils import simple_catch_error_dec

class SkinClusterNormalizedWeights(AbstractCheckData):
    """Check that all skinClusters have normalized weights (sum to 1 per vertex)."""

    def __init__(self, main):
        AbstractCheckData.__init__(self, main)

        self.name = "OPTIONAL: SkinClusters Normalized Weights"
        self.info = "Ensures all skinClusters have normalized weights per vertex."
        self.has_fix = True
        self.type = "warning"
        self.error_msg = ""
        self.position = 800

    def check(self):
        """Check for any non-normalized vertices in all skinClusters."""
        error_count = 0
        skin_clusters = []

        for sc in mc.ls(type="skinCluster"):
            user_attrs = mc.listAttr(sc, userDefined=True) or []
            if not any(attr.startswith("io_uuid") for attr in user_attrs):
                skin_clusters.append(sc)

        if not skin_clusters:
            return True

        for sc in skin_clusters:
            # Use normalizeWeights query
            normalize_attr = sc + ".normalizeWeights"
            normalize = mc.getAttr(normalize_attr) if mc.objExists(normalize_attr) else None

            if normalize == 0:
                error_count += 1

            mc.skinCluster(sc, edit=True, forceNormalizeWeights=True)

        if error_count:
            self.error_msg = "Found {0} skinClusters with non-normalized weights.".format(error_count)
            return False

        return True

    @simple_catch_error_dec
    def run_fix(self):
        self.fix()
        self._status = self.check()

    def fix(self):
        """Enable normalization for all skinClusters."""
        fixed_clusters = []
        skin_clusters = []

        for sc in mc.ls(type="skinCluster"):
            user_attrs = mc.listAttr(sc, userDefined=True) or []
            if not any(attr.startswith("io_uuid") for attr in user_attrs):
                skin_clusters.append(sc)

        if not skin_clusters:
            return

        for sc in skin_clusters:
            normalize_attr = sc + ".normalizeWeights"
            if mc.objExists(normalize_attr) and mc.getAttr(normalize_attr) == 0:
                mc.setAttr(normalize_attr, 1)
                fixed_clusters.append(sc)

            mc.skinCluster(sc, edit=True, forceNormalizeWeights=True)

        if fixed_clusters:
            print("Normalized weights on skinClusters: {0}".format(list(set(fixed_clusters))))
