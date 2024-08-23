import os
import mocapx.config

MODULE_NAME = 'mocapx_plugin'
ATTRIBUTE_TYPES = ('doubleLinear', 'doubleAngle', 'double', 'float')

TRANSFORM_ATTRS = (
    'leftEyeTransformRotateX',
    'leftEyeTransformRotateY',
    'leftEyeTransformRotateZ',
    'leftEyeTransformTranslateX',
    'leftEyeTransformTranslateY',
    'leftEyeTransformTranslateZ',
    'rightEyeTransformRotateX',
    'rightEyeTransformRotateY',
    'rightEyeTransformRotateZ',
    'rightEyeTransformTranslateX',
    'rightEyeTransformTranslateY',
    'rightEyeTransformTranslateZ',
    'transformTranslateX',
    'transformTranslateY',
    'transformTranslateZ',
    'transformRotateX',
    'transformRotateY',
    'transformRotateZ',
    'lookAtPointX',
    'lookAtPointY',
    'lookAtPointZ')

# Global state
attr_outliner = None
plugin_cleanup_cb = None
suppress_on_scene_loading = False
suppress_on_attr_refresh = False

clipreader_added_cbid = None
clipreader_removed_cbid = None
clipreader_renamed_cbids = dict()
clipreader_onconnect_cbids = dict()

adapter_added_cbid = None
adapter_removed_cbid = None
adapter_renamed_cbids = dict()
adapter_active_change_cbids = dict()

poseLib_added_cbid = None
poseLib_removed_cbid = None
poseLib_renamed_cbids = dict()
poseLib_before_delete_cbids = dict()

pose_added_cbid = None
pose_removed_cbid = None
pose_attr_changed_cbids = dict()
pose_solo_mode = False
pose_unmutes_before_solo = list()

poseApply_added_cbid = None
poseApply_removed_cbid = None
poseApply_renamed_cbids = dict()
poseApply_attr_changed_cbids = dict()
poseApply_before_delete_cbids = dict()

scene_state_cbids = list()
poselib_editor = None
pose_board = None
mocapx_menu = None
mocapx_shelf = None
plugin_distr_root = os.path.normpath(os.path.join(os.path.dirname(__file__), '../..'))

platform = mocapx.config.SYSTEM
version = mocapx.config.VERSION

scene_watcher = None
