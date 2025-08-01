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

"""BaseNodeAction sets settings on Base node for animation. """

import maya.cmds as mc

from arise.utils.decorators_utils import simple_catch_error_dec
from arise.utils.tagging_utils import get_all_tagged_ctrl_item

CATEGORY = "arise_base_main_ctrl_tag"


class BaseNodeAction(object):
    """BaseNodeAction sets settings on Base node for animation. """
    def __init__(self):
        self.name = "Base Node Settings"
        self.info = (
            "Set 'Base' node settings: 'Joints Visibility'=off, 'Geometry Display'=on,'Display Value'=Reference"
        )
        self.position = 300
        self.is_checked = True
        self.post_action = False

    @staticmethod
    @simple_catch_error_dec
    def run_action(_):
        """Run base node settings change.

        main_window (IORMainWindow): Arise main window
        """
        print("\n#########################################################")
        print("########## Action: 'Base Node Settings' START. ##########")
        print("#########################################################\n")

        base_nodes_ctrls = []
        for ctrl in get_all_tagged_ctrl_item():

            if mc.listAttr(ctrl, category=CATEGORY):
                base_nodes_ctrls.append(ctrl)

        if not base_nodes_ctrls:
            return "Warning! No Base nodes found!"

        for ctrl in base_nodes_ctrls:
            for attr, value in [["joints_visibility", 0], ["geometry_display", 2]]:
                attr = "{0}.{1}".format(ctrl, attr)

                if not mc.objExists(attr):
                    print("does not exist")
                    continue

                if mc.getAttr(attr, lock=True):
                    print("locked")
                    continue

                if mc.listConnections(attr, source=True, destination=False):
                    print("connected")
                    continue

                mc.setAttr(attr, value)

        return "Action successful"
