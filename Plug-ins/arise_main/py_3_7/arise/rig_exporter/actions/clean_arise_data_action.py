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
from arise.utils.tagging_utils import get_maya_nodes_with_tag, ROOT_FOLDER_NAME
from arise.utils.constant_variables import AUTOSAVE_ATTR


class CleanAriseDataAction(object):
    """Clean Arise data from scene. delete stored Arise saved scene to make the scene smaller. """
    def __init__(self):
        self.name = "Clean Arise Data"
        self.info = "Reduce the exported rig file size by deleting Arise Saved scene data."
        self.position = 250
        self.is_checked = False
        self.post_action = False

    @staticmethod
    @simple_catch_error_dec
    def run_action(_):
        """Delete save scene attribute on root rig group. """
        root_grp = get_maya_nodes_with_tag(ROOT_FOLDER_NAME)

        if not root_grp or not mc.objExists(root_grp[0]):
            return "Warning! No Root group found. Arise data not cleaned."

        save_attr = "{0}.{1}".format(root_grp[0], AUTOSAVE_ATTR)
        if mc.objExists(save_attr):
            mc.setAttr(save_attr, lock=False)
            mc.deleteAttr(save_attr)

        return "Action successful"
