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

"""Checks for unused influences on skinClusters."""

import maya.cmds as mc
from arise.rig_exporter.checks.abstract_check.abstract_check import AbstractCheckData
from arise.utils.decorators_utils import simple_catch_error_dec

class SkinClusterUnusedInfluences(AbstractCheckData):
    """Check for unused influences in all skinClusters."""

    def __init__(self, main):
        AbstractCheckData.__init__(self, main)

        self.name = "OPTIONAL: SkinClusters Unused Influences"
        self.info = "Ensures no skinCluster has influences that do not affect any vertices."
        self.has_fix = True
        self.type = "warning"
        self.error_msg = ""
        self.position = 600

    def check(self):
        """Check for unused influences in all skinClusters using weightedInfluence."""
        skin_clusters = []
        unused_count = 0

        for sc in mc.ls(type="skinCluster"):
            user_attrs = mc.listAttr(sc, userDefined=True) or []
            if not any(attr.startswith("io_uuid") for attr in user_attrs):
                skin_clusters.append(sc)

        if not skin_clusters:
            return True

        for sc in skin_clusters:
            all_influences = mc.skinCluster(sc, query=True, influence=True) or []
            weighted_influences = mc.skinCluster(sc, query=True, weightedInfluence=True) or []
            unused_influences = [inf for inf in all_influences if inf not in weighted_influences]

            if unused_influences:
                unused_count += len(unused_influences)

        if unused_count > 0:
            self.error_msg = "Found {0} unused influences across all skinClusters.".format(unused_count)
            return False

        return True

    @simple_catch_error_dec
    def run_fix(self):
        self.fix()
        self._status = self.check()

    def fix(self):
        """Remove unused influences from skinClusters."""
        skin_clusters = []

        for sc in mc.ls(type="skinCluster"):
            user_attrs = mc.listAttr(sc, userDefined=True) or []
            if not any(attr.startswith("io_uuid") for attr in user_attrs):
                skin_clusters.append(sc)

        if not skin_clusters:
            return True

        for sc in skin_clusters:
            all_influences = mc.skinCluster(sc, query=True, influence=True) or []
            weighted_influences = mc.skinCluster(sc, query=True, weightedInfluence=True) or []
            unused_influences = [inf for inf in all_influences if inf not in weighted_influences]

            if unused_influences:
                for inf in unused_influences:
                    mc.skinCluster(sc, e=True, removeInfluence=inf)

                print("Removed {0} unused influences from skinCluster: ''{1}''".format(len(unused_influences), sc))
