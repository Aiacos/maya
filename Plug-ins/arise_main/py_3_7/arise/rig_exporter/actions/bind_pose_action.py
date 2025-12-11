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

"""BindPoseAction sets the ctrls to their Bind Pose. """

from arise.utils.decorators_utils import simple_catch_error_dec
from arise.utils.ctrls_utils import apply_bind_pose_all

class BindPoseAction(object):
    """BindPoseAction sets the ctrls to their Bind Pose. """
    def __init__(self):
        self.name = "Set Ctrls To Bind Pose"
        self.info = "Set all the ctrls to their bind pose values"
        self.position = 400
        self.is_checked = True
        self.post_action = False

    @staticmethod
    @simple_catch_error_dec
    def run_action(_):
        """Run set bind pose. """
        apply_bind_pose_all(silent=False, only_trans=True)

        return "----"
