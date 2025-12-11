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

"""ZeroedPoseAction sets the ctrls to their zeroed Pose. """

from arise.utils.decorators_utils import simple_catch_error_dec
from arise.utils.ctrls_utils import apply_zero_pose_all

class ZeroedPoseAction(object):
    """ZeroedPoseAction sets the ctrls to their zeroed Pose. """
    def __init__(self):
        self.name = "Set Ctrls To Zeroed Pose"
        self.info = "Set all the ctrls to their zeroed pose values (translate and rotate to 0.0 and scale to 1.0)"
        self.position = 500
        self.is_checked = False
        self.post_action = False

    @staticmethod
    @simple_catch_error_dec
    def run_action(_):
        """Run set bind pose. """
        apply_zero_pose_all()

        return "----"
