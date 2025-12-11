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

"""ReferencesAction is the operations done when saving to import namespaces. """

import maya.cmds as mc

from arise.utils.decorators_utils import simple_catch_error_dec

class ReferencesAction(object):
    """ReferencesAction is the operation to import namespaces into the scene. """
    def __init__(self):
        self.name = "Import References"
        self.info = "Import any references in scene on export"
        self.position = 100
        self.is_checked = True
        self.post_action = False

    @staticmethod
    @simple_catch_error_dec
    def run_action(_):
        """Run import references operation. """
        for ref_path in mc.file(q=True, reference=True):
            namespace = mc.referenceQuery(ref_path, namespace=True, shortName=True)
            mc.file(ref_path, importReference=True)
            mc.namespace(removeNamespace=namespace, mergeNamespaceWithRoot=True)

        return "Action successful"
