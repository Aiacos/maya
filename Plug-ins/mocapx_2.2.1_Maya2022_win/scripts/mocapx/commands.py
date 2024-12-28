from mocapx.lib.nodes import define_attr_collection, define_poselib, define_pose, get_valid_plugs, \
    get_poses_connected_to_poseapply, get_mute_pose, get_realtime_device_conn_status, \
    get_adapter_node, get_clipreader_node, get_active_data_source, set_active_source, \
    get_realtime_device_node
from mocapx.lib.uiutils import ask_user_confirm
from mocapx.lib.utils import get_frame_range, get_depend_on, get_time_node

import maya.cmds as mc


def create_empty_collection(collection_name=None):
    return define_attr_collection(collection_name=collection_name, create_collection=True)


def add_controls_to_collection(collection_name, control_list=None, selected_controls=False):
    return define_attr_collection('add', collection_name, controls=control_list,
                                  selected_controls=selected_controls)


def add_plugs_to_collection(collection_name, plug_list=None, selected_plugs=False):
    return define_attr_collection('add', collection_name, plugs=plug_list,
                                  selected_plugs=selected_plugs)


def remove_controls_from_collection(collection_name, control_list=None, selected_controls=False):
    return define_attr_collection('remove', collection_name, controls=control_list,
                                  selected_controls=selected_controls)


def remove_plugs_from_collection(collection_name, plug_list=None, selected_plugs=False):
    return define_attr_collection('remove', collection_name, plugs=plug_list,
                                  selected_plugs=selected_plugs)


def create_empty_poselib(poselib_name=None):
    return define_poselib(poselib_name=poselib_name, create_poselib=True)


def add_pose_to_poselib(poselib_name, pose_list=None, selected_poses=False):
    return define_poselib('add', poselib_name, poses=pose_list, selected_poses=selected_poses,
                          create_poselib=True)


def remove_pose_from_poselib(poselib_name, pose_list=None, selected_poses=False):
    return define_poselib('remove', poselib_name, poses=pose_list, selected_poses=selected_poses)


def create_empty_pose(pose_name=None):
    return define_pose(pose_name=pose_name, create_pose=True)


# update existing in pose or add new
def update_controls_in_pose(pose_name, control_list=None, selected_controls=False):
    return define_pose('update', pose_name, controls=control_list,
                       selected_controls=selected_controls)


# update existing in pose or add new
def update_plugs_in_pose(pose_name, plug_list=None, selected_plugs=False):
    return define_pose('update', pose_name, plugs=plug_list, selected_plugs=selected_plugs)


def remove_controls_from_pose(pose_name, control_list=None, selected_controls=False):
    return define_pose('remove', pose_name, controls=control_list,
                       selected_controls=selected_controls)


def remove_plugs_from_pose(pose_name, plug_list=None, selected_plugs=False):
    return define_pose('remove', pose_name, plugs=plug_list, selected_plugs=selected_plugs)


def create_realtime_device(adapter_name=None):
    try:
        if adapter_name:
            adapter_node = get_adapter_node(create_node=False, node_name=adapter_name)
        else:
            adapter_node = get_adapter_node(create_node=True)
        realtime_device = get_realtime_device_node(create_node=True)
    except AttributeError as err:
        mc.error(err)
        return None
    except RuntimeError as err:
        mc.error(err)
        return None

    mc.sets(realtime_device, add=adapter_node)

    if not get_active_data_source(adapter_node):
        set_active_source(adapter_node, realtime_device)
    return realtime_device


def create_clipreader(adapter_name=None):
    try:
        if adapter_name:
            adapter_node = get_adapter_node(create_node=False, node_name=adapter_name)
        else:
            adapter_node = get_adapter_node(create_node=True)
        clipreader = get_clipreader_node(create_node=True)
        time_node = get_time_node()
    except AttributeError as err:
        mc.error(err)
        return None
    except RuntimeError as err:
        mc.error(err)
        return None

    mc.connectAttr('{}.outTime'.format(time_node), '{}.time'.format(clipreader))
    mc.sets(clipreader, add=adapter_node)
    if not get_active_data_source(adapter_node):
        set_active_source(adapter_node, clipreader)
    return clipreader


def establish_connection(realtime_device):
    if mc.objExists(realtime_device):
        if get_realtime_device_conn_status(realtime_device) == 0:
            # pylint: disable=no-member
            # noinspection PyUnresolvedReferences
            return mc.establishConnection(realtime_device)
            # pylint: enable=no-member
    return False


def start_session(realtime_device):
    if mc.objExists(realtime_device):
        if get_realtime_device_conn_status(realtime_device) == 1:
            # pylint: disable=no-member
            # noinspection PyUnresolvedReferences
            return mc.startMocapSession(realtime_device)
            # pylint: enable=no-member
    return False


def break_connection(realtime_device):
    if mc.objExists(realtime_device):
        if get_realtime_device_conn_status(realtime_device) in (1, 2, 3):
            # pylint: disable=no-member
            return mc.stopMocapSession(realtime_device)
            # pylint: enable=no-member
    return True


def bake_channels():
    selected_channels = get_valid_plugs(selected_controls=True)
    start_frame, end_frame = get_frame_range()
    bake_canceled = False

    # Get all channels depend on poses
    # Create a mapping pose -> channel list
    pose_to_channels_map = dict()
    for channel in selected_channels:
        poseapplies = get_depend_on(channel, node_types=('MCPXPoseApply',))
        pose_nodes = list()
        if not poseapplies:
            continue
        for each in poseapplies:
            pose_nodes.extend(get_poses_connected_to_poseapply(each))
        for pose_node in pose_nodes:
            if pose_node not in pose_to_channels_map:
                pose_to_channels_map[pose_node] = list()
            pose_to_channels_map[pose_node].append(channel)

    # Iterate over poses and form flat list of channels need to be baked
    # On first occurrence of a muted pose as uses if he'd like to continue or cancel'
    channels_dep_on_poses = list()
    muted_confirm = False
    for pose in pose_to_channels_map.keys():
        if get_mute_pose(pose):
            if muted_confirm or ask_user_confirm(
                    'At least one the poses is muted.\n'
                    'Data from muted poses will be ignored'):
                muted_confirm = True
                continue
            else:
                bake_canceled = True
                break
        else:
            channels_dep_on_poses.extend(pose_to_channels_map[pose])
    channels_dep_on_poses = list(set(channels_dep_on_poses))

    # Get all channels depend on Clipreader adapter or realtime device
    channels_dep_on_clips = list()
    for channel in set(selected_channels) - set(channels_dep_on_poses):
        if get_depend_on(
                channel, node_types=('MCPXAdapter', 'MCPXClipReader', 'MCPXRealTimeDevice')):
            channels_dep_on_clips.append(channel)

    # If at the end there is nothing to bake set bake_canceled=True
    if len(channels_dep_on_poses + channels_dep_on_clips) == 0:
        bake_canceled = True

    if not bake_canceled:
        # prepare animation curves for each channel to store values in
        channel_animcurve_pairs = list()
        for channel in channels_dep_on_poses + channels_dep_on_clips:
            if mc.getAttr(channel, type=True) != 'doubleAngle':
                node_type = 'animCurveTL'
            else:
                node_type = 'animCurveTA'
            anim_curve_node = mc.createNode(node_type)
            anim_curve_node = mc.rename(
                anim_curve_node, '{}_mcpxBake'.format(channel.replace('.', '_')))

            # Important! Set one key while preparing channel nodes.
            # Otherwise maya crash when setting keys while traveling timeline if cache is on
            value = mc.getAttr(channel)
            mc.setKeyframe(anim_curve_node, v=value)

            channel_animcurve_pairs.append((channel, anim_curve_node))

        # Go through the timeline. Collect values and store them in corresponding anim curves
        for frame in range(int(start_frame), int(end_frame) + 1):
            mc.currentTime(frame, edit=True)
            for channel, anim_curve_node in channel_animcurve_pairs:
                value = mc.getAttr(channel)
                mc.setKeyframe(anim_curve_node, t=frame, v=value)

        # Iterate over baked curves and connect them to corresponding channels
        for channel, anim_curve_node in channel_animcurve_pairs:
            mc.connectAttr('{}.output'.format(anim_curve_node), channel, f=True)
