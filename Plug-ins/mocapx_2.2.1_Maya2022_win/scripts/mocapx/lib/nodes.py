import os

import maya.cmds as mc

from mocapx.lib.uiutils import show_error
from mocapx.lib.utils import (filter_controls, filter_plugs, filter_poses, get_attributes, get_index, get_next_index,
                              get_restplugs, get_selected_attrs, request_module, shift_referenced_anim_curve,
                              has_attr_connection, round_value, is_attr_type_valid, is_node_anim_curve)


def node_exists(node):
    return mc.objExists(node)


def is_attr_settable(plug):
    return mc.getAttr(plug, settable=True)


def is_attr_manipulated(plug):
    if plug.count(".") != 1:
        return False

    manipulated = (
        "translate",
        "translateX",
        "translateY",
        "translateZ",
        "rotate",
        "rotateX",
        "rotateY",
        "rotateZ",
        "scale",
        "scaleX",
        "scaleY",
        "scaleZ")

    node_name, attr_name = plug.split(".")

    return mc.attributeQuery(attr_name, n=node_name, longName=True) in manipulated


def break_all_incoming_connections(node):
    if mc.objExists(node):
        connections = mc.listConnections(node, d=False, c=True, p=True) or []

        count = len(connections) / 2

        for i in range(count):
            source, target = connections[2 * i + 1], connections[2 * i]
            if mc.isConnected(source, target):
                try:
                    mc.disconnectAttr(source, target)
                except:
                    raise RuntimeError(
                        "Cannot disconnect \"{}\" and \"{}\".".format(source, target))


def break_incoming_connection(plug, remove_anim_curve=False):
    if mc.objExists(plug):
        in_connection = mc.connectionInfo(plug, sfd=True)
        if in_connection:
            mc.disconnectAttr(in_connection, plug)
            if remove_anim_curve:
                node = in_connection.split(".")[0]
                if is_node_anim_curve(node):
                    try:
                        mc.delete(node)
                    except:
                        pass


def remove_multi_element(plug):
    if mc.objExists(plug):
        return mc.removeMultiInstance(plug, b=True)
    raise AttributeError("'{}' plug doesn't exist.".format(plug))


def get_valid_poses(poses, selected_poses):
    if poses and selected_poses:
        raise AttributeError(
            '"poses" list and "selected_poses" flag cannot be supplied together')

    if poses or selected_poses:
        if poses:
            list_of_poses = filter_poses(poses)
        else:
            list_of_poses = filter_poses(mc.ls(sl=True))
    else:
        list_of_poses = list()

    return list_of_poses


def get_valid_plugs(controls=tuple(), selected_controls=False, plugs=tuple(), selected_plugs=False):
    if controls and selected_controls:
        raise AttributeError(
            '"controls" list and "selected_controls" flag cannot be supplied together')
    if plugs and selected_plugs:
        raise AttributeError(
            '"plugs" list and "selected_plugs" flag cannot be supplied together')
    if (controls or selected_controls) and (plugs or selected_plugs):
        raise AttributeError('controls and plugs cannot be supplied together')

    if controls or selected_controls:
        if controls:
            list_of_controls = filter_controls(controls)
        else:
            list_of_controls = filter_controls(mc.ls(sl=True))
        attribute_plugs = get_attributes(list_of_controls)

    elif plugs or selected_plugs:
        if plugs:
            attribute_plugs = filter_plugs(plugs)
        else:
            attribute_plugs = filter_plugs(get_selected_attrs())
    else:
        attribute_plugs = list()

    return attribute_plugs


def set_node(node_type, default_name):
    # noinspection PyUnusedLocal
    def decorator(func):
        def wrapper(create_node, node_name=None):
            if node_name:
                if mc.objExists(node_name):
                    if mc.objectType(node_name) == node_type:
                        return node_name
                    else:
                        raise AttributeError(
                            '{} should be {} node!'.format(node_name, node_type))
                else:
                    if not create_node:
                        raise AttributeError(
                            '{} doesnt exist!'.format(node_name))

            if create_node:
                if not node_name:
                    node_name = default_name
                try:
                    node = mc.createNode(node_type, name=node_name, ss=True)
                except RuntimeError as err:
                    raise RuntimeError(
                        'Error creation {} node\n{}'.format(node_type, err))
                if not node:
                    raise RuntimeError(
                        'Error creation {} node\nMaya returned empty result'.format(node_type))
                return node
            else:
                raise AttributeError(
                    'Parameters are wrong!\n "create_node" if "False" and "node_name" is not given')

        return wrapper

    return decorator


# noinspection PyUnusedLocal
@set_node('MCPXAttributeCollection', 'AttributeCollection')
def get_attr_collection_node(create_node, node_name=None):
    pass


# noinspection PyUnusedLocal
@set_node('MCPXPoselib', 'Poselib')
def get_poselib_node(create_node, node_name=None):
    pass


# noinspection PyUnusedLocal
@set_node('MCPXPose', 'Pose')
def get_pose_node(create_node, node_name=None):
    pass


# noinspection PyUnusedLocal
@set_node('MCPXRealTimeDevice', 'RealtimeDevice')
def get_realtime_device_node(create_node, node_name=None):
    pass


# noinspection PyUnusedLocal
@set_node('MCPXClipReader', 'ClipReader')
def get_clipreader_node(create_node, node_name=None):
    pass


# noinspection PyUnusedLocal
@set_node('MCPXAdapter', 'MocapX')
def get_adapter_node(create_node, node_name=None):
    pass


@request_module
def define_attr_collection(mode='add', collection_name=None, create_collection=False, controls=None,
                           selected_controls=False, plugs=None, selected_plugs=False):
    try:
        attribute_plugs = get_valid_plugs(
            controls, selected_controls, plugs, selected_plugs)
        attr_collection_node = get_attr_collection_node(
            create_collection, node_name=collection_name)
    except AttributeError as err:
        mc.error(err)
        return None
    except RuntimeError as err:
        mc.error(err)
        return None

    if attribute_plugs:
        col_attrs = attr_collection_node + ".attrs"

        if mode == 'add':
            attrs_index = get_next_index(col_attrs)
            for plug in attribute_plugs:
                # connect plug if not already in Attribute Collection
                current_collections = mc.listConnections(
                    plug, s=False, scn=True, type="MCPXAttributeCollection")
                if not (current_collections and attr_collection_node in current_collections):
                    indexedPlug = "{}[{}]".format(col_attrs, attrs_index)
                    mc.connectAttr(plug, indexedPlug + ".plug")
                    mc.setAttr(indexedPlug + ".restValue", mc.getAttr(plug))
                    attrs_index += 1

        elif mode == 'remove':
            for plug in attribute_plugs:
                for coll_plug in mc.listConnections(plug, s=True, p=True, scn=True,
                                                    type="MCPXAttributeCollection") or []:
                    if coll_plug.startswith(col_attrs):
                        remove_multi_element(coll_plug)
                        break

    return attr_collection_node


@request_module
def define_poselib(mode='add', poselib_name=None, create_poselib=False, poses=None,
                   selected_poses=False):
    try:
        pose_nodes = get_valid_poses(poses, selected_poses)
        poselib_node = get_poselib_node(create_poselib, node_name=poselib_name)

    except AttributeError as err:
        mc.error(err)
        return None
    except RuntimeError as err:
        mc.error(err)
        return None

    if pose_nodes:
        if mode == 'add':
            mc.sets(list(reversed(pose_nodes)), add=poselib_node)
        elif mode == 'remove':
            mc.sets(list(reversed(pose_nodes)), remove=poselib_node)

    return poselib_node


@request_module
def define_pose(mode='update', pose_name=None, create_pose=False,
                controls=None, selected_controls=False,
                plugs=None, selected_plugs=False):
    try:
        # list of all plugs which can be kept in pose
        attribute_plugs = get_valid_plugs(
            controls, selected_controls, plugs, selected_plugs)
        pose_node = get_pose_node(create_pose, node_name=pose_name)

    except AttributeError as err:
        mc.error(err)
        return None
    except RuntimeError as err:
        mc.error(err)
        return None

    to_process = list()
    # for each plug connected to attribute collection and this connection (.restValue)
    # collect all attrs with values different from rest
    for ctrl_plug, rest_plug in get_restplugs(attribute_plugs):
        ctrl_value = mc.getAttr(ctrl_plug)
        rest_value = mc.getAttr(rest_plug)

        if round_value(ctrl_value) != round_value(rest_value):
            to_process.append((ctrl_plug, ctrl_value, rest_plug, rest_value))

    # apply action for collected
    for ctrl_plug, ctrl_value, rest_plug, rest_value in to_process:
        is_already_connected = False
        index = 0
        for plug in mc.listConnections(rest_plug, p=True, s=False, scn=True, type='MCPXPose') or []:
            if plug.split('.')[0] == pose_node:
                is_already_connected = True
                index = get_index(plug)
                break
        if not is_already_connected:
            index = get_next_index('{}.attrs'.format(pose_node))

        pose_attrs_plug = '{}.attrs[{}]'.format(pose_node, index)

        if mode == 'remove':
            if is_already_connected:
                mc.removeMultiInstance(pose_attrs_plug, b=True)
        # earlier 'update' was the same as 'add' was for connected plugs
        # but real difference was in input parameters of the function, so 'update' was removed
        # 'add' was renamed to 'update' because of more common meaning
        elif mode == 'update':
            pose_value_plug = '{}.pose'.format(pose_attrs_plug)
            weight_value = get_pose_weight(pose_node)
            if weight_value != 0:
                # to calculate exact pose value according to pose weight
                multiplier = 1 / float(weight_value)
            else:
                multiplier = 1

            if is_already_connected:  # update existing pose
                anim_blend_node = get_anim_blend_node(ctrl_plug)

                incoming_plug = '{}.output'.format(anim_blend_node)
                incoming_value = mc.getAttr(incoming_plug)
                # exclude influences of all poses for this plug and
                # calculate only clean difference to add it to pose
                difference = ctrl_value - incoming_value

                if weight_value != 0:
                    mc.setAttr(pose_value_plug, mc.getAttr(pose_value_plug) + difference * multiplier)
                else:
                    # if weight is 0 we dont need to take pose value
                    # because this pose has no influence on current value
                    # instead we need to sum difference with rest value an set it as new pose value
                    mc.setAttr(pose_value_plug, rest_value + difference)

            else:  # as "add" mode
                # creating blend node - if rest not zero and animCurve - shift keys by rest value
                # to do shift or not - determined finally inside get_anim_blend_node if all conditions are true
                anim_blend_node = get_anim_blend_node(ctrl_plug, create=True, shift=-1 * rest_value)

                mc.setAttr(pose_value_plug, rest_value + (ctrl_value - rest_value) * multiplier)
                mc.connectAttr(rest_plug, '{}.rest'.format(pose_attrs_plug), f=True)

                pose_apply_node = get_pose_apply_node('{}.inputA'.format(anim_blend_node), create=True)
                if not mc.isConnected(rest_plug, '{}.rest'.format(pose_apply_node)):
                    mc.connectAttr(rest_plug, '{}.rest'.format(pose_apply_node))
                mc.connectAttr('{}.out'.format(pose_attrs_plug), '{}.values'.format(pose_apply_node), na=True)

    return pose_node


def get_anim_blend_node(plug, create=False, shift=0, rewire_to='inputB'):
    connected_node = None
    connection_plugs = mc.listConnections(plug, d=False, scn=True, p=True)

    if connection_plugs:
        connected_node = connection_plugs[0].split('.')[0]
        if mc.objectType(connected_node, isa="animBlendNodeBase"):
            return connected_node

    if not create:
        return None

    if mc.getAttr(plug, type=True) != "doubleAngle":
        node_type = 'animBlendNodeAdditiveDL'
    else:
        node_type = 'animBlendNodeAdditiveDA'
    anim_blend_node = mc.createNode(node_type)

    if connection_plugs:
        mc.connectAttr(connection_plugs[0], '{}.{}'.format(anim_blend_node, rewire_to))

        if shift:
            def __get_animCurve(plug):
                node = plug.split('.')[0]
                if mc.objectType(node, isa="animCurve"):
                    return node
                connection_plugs = mc.listConnections(plug, d=False, scn=True, p=True)
                return __get_animCurve(connection_plugs[0]) if connection_plugs else None

            # for cases when animation can go through chain of nodes
            # we try to find animation curve recursively
            # (implemented after character-set usage)
            animCurve = __get_animCurve(connection_plugs[0])
            if animCurve:
                # if incoming animation to plug - shift curve keys
                if not mc.referenceQuery(animCurve, inr=True):
                    mc.keyframe(animCurve, relative=True, valueChange=shift)
                else:
                    shift_referenced_anim_curve(animCurve, shift)

    mc.connectAttr('{}.output'.format(anim_blend_node), plug, f=True)
    return anim_blend_node


def get_pose_apply_node(plug, create=False):
    in_connections = mc.listConnections(plug, d=False, scn=True, type='MCPXPoseApply')
    if in_connections:
        return in_connections[0]

    if not create:
        return None

    pose_apply_node = mc.createNode('MCPXPoseApply')
    mc.connectAttr('{}.output'.format(pose_apply_node), plug, f=True)
    return pose_apply_node


def get_poses_connected_to_poseapply(pose_apply_node):
    nodes = mc.listConnections(
        '{}.values'.format(pose_apply_node), d=False, scn=True, type='MCPXPose')
    if nodes:
        return nodes
    else:
        return tuple()


def list_poselib_nodes():
    return mc.ls(type='MCPXPoselib')


def scene_selection():
    return mc.ls(sl=True, l=True)


def select_node(node_name):
    if mc.objExists(node_name):
        if mc.objectType(node_name, isAType='objectSet'):
            mc.select(node_name, r=True, ne=True)
        else:
            mc.select(node_name, r=True)


def select_nodes(nodes_list):
    mc.select(mc.ls(nodes_list), r=True)


def delete_node(node_name):
    if mc.objExists(node_name):
        # Remove node from sets before delete
        sets = mc.listSets(o=node_name)
        if sets:
            for obj_set in sets:
                mc.sets(node_name, remove=obj_set)

        # TODO: Come up with something better
        # Some poses cannot be deleted. First delete disconnects all attributes.
        # Second deletes node
        try:
            mc.delete(node_name)
        except RuntimeError:
            mc.delete(node_name)


def connect_attrs(source, dest, force=True, verbose=False):
    if mc.objExists(source) and mc.objExists(dest):
        if mc.connectionInfo(dest, sourceFromDestination=True) != source:
            try:
                mc.connectAttr(source, dest, f=force)
            except RuntimeError as e:
                show_error(str(e))
            else:
                if verbose:
                    print("connectAttr{} {} {};".format(" -f" * force, source, dest))
                return True
    return False


def connected_attrs(source, dest):
    if mc.objExists(source) and mc.objExists(dest):
        return mc.isConnected(source, dest)
    raise AttributeError("Attrs {} or {} does't exists".format(source, dest))


def disconnect_attrs(source, dest, verbose=False):
    if mc.objExists(source) and mc.objExists(dest):
        if mc.isConnected(source, dest):
            try:
                mc.disconnectAttr(source, dest)
            except RuntimeError as e:
                show_error(str(e))
            else:
                if verbose:
                    print("disconnectAttr {} {};".format(source, dest))
                return True
    return False


def get_pose_nodes(pose_lib_node=None):
    if not pose_lib_node is None:
        if mc.objExists(pose_lib_node) and mc.objectType(pose_lib_node) == 'MCPXPoselib':
            nodes = mc.listConnections(pose_lib_node, source=True, destination=False, type='MCPXPose')
            if nodes:
                return list(set(nodes))
    else:
        return mc.ls(et="MCPXPose")
    return list()


def find_pose_nodes(name, recursive=True):
    return mc.ls(name, r=recursive, type="MCPXPose")


def get_active_data_source(mocapx_node):
    if mc.objExists(mocapx_node) and mc.objectType(mocapx_node) == 'MCPXAdapter':
        plug = mc.connectionInfo('{}.activeSource'.format(mocapx_node), sourceFromDestination=True)
        if plug:
            return plug.split('.')[0]
        else:
            return None
    else:
        raise AttributeError(
            "{} node is doesn't exist or inappropriate type. Should be {}".format(
                mocapx_node, 'MCPXAdapter'))


def get_all_active_data_sources(source_type=None):
    sources = list()
    for adapter in mc.ls(et="MCPXAdapter"):
        active = get_active_data_source(adapter)
        if active and active not in sources:
            if not source_type or mc.objectType(active, i=source_type):
                sources.append(active)
    return sources


def set_active_source(adapter, data_source_node):
    if mc.objExists(adapter) and mc.objectType(adapter) == 'MCPXAdapter':
        if mc.objExists(data_source_node) and mc.objectType(data_source_node) in (
                'MCPXClipReader', 'MCPXRealTimeDevice'):
            if data_source_node in get_adapter_sources(adapter):
                mc.connectAttr('{}.message'.format(data_source_node),
                               '{}.activeSource'.format(adapter), f=True)
            else:
                raise RuntimeError(
                    "{} node is not part of adapter {}".format(data_source_node, adapter))
        else:
            raise AttributeError(
                "{} node is doesn't exist or inappropriate type. Should be {}".format(
                    data_source_node, 'MCPXClipReader or MCPXRealTimeDevice'))
    else:
        raise AttributeError(
            "{} node is doesn't exist or inappropriate type. Should be {}".format(
                adapter, 'MCPXAdapter'))


def if_data_source(test_node):
    return mc.objectType(test_node) in ('MCPXClipReader', 'MCPXRealTimeDevice')


def if_pose_node(test_node):
    return mc.objectType(test_node) == 'MCPXPose'


def if_attr_collection_node(test_node):
    return mc.objectType(test_node) == 'MCPXAttributeCollection'


def if_clipreader_node(test_node):
    if mc.objExists(test_node):
        return mc.objectType(test_node) == 'MCPXClipReader'


def realtime_device_node(test_node):
    if mc.objExists(test_node):
        return mc.objectType(test_node) == 'MCPXRealTimeDevice'


def get_pose_weight(pose_node):
    if mc.objExists(pose_node) and mc.attributeQuery('weight', node=pose_node, exists=True):
        return mc.getAttr('{}.weight'.format(pose_node))


def get_pose_weight_min(pose_node):
    if mc.objExists(pose_node) and mc.attributeQuery('weight_min', node=pose_node, exists=True):
        return mc.getAttr('{}.weight_min'.format(pose_node))


def get_pose_weight_max(pose_node):
    if mc.objExists(pose_node) and mc.attributeQuery('weight_max', node=pose_node, exists=True):
        return mc.getAttr('{}.weight_max'.format(pose_node))


def set_pose_weight_min(pose_node, value, force=True):
    attr_name = "weight_min"
    if mc.objExists(pose_node) and mc.attributeQuery(attr_name, node=pose_node, exists=True):
        _min, _max = mc.attributeQuery(attr_name, node=pose_node, range=True)
        value = float(max(min(value, _max), _min))
        plug = '{}.{}'.format(pose_node, attr_name)
        if force or value != mc.getAttr(plug):
            mc.setAttr(plug, value)
            return True
    return False


def set_pose_weight_max(pose_node, value, force=True):
    attr_name = "weight_max"
    if mc.objExists(pose_node) and mc.attributeQuery(attr_name, node=pose_node, exists=True):
        _min, _max = mc.attributeQuery(attr_name, node=pose_node, range=True)
        value = float(max(min(value, _max), _min))
        plug = '{}.{}'.format(pose_node, attr_name)
        if force or value != mc.getAttr(plug):
            mc.setAttr(plug, value)
            return True
    return False


def pose_weight_has_connection(pose_node):
    if mc.objExists(pose_node) and mc.attributeQuery('weight', node=pose_node, exists=True):
        return mc.connectionInfo('{}.weight'.format(pose_node), isDestination=True)


def pose_weight_locked(pose_node):
    if mc.objExists(pose_node) and mc.attributeQuery('weight', node=pose_node, exists=True):
        return mc.getAttr('{}.weight'.format(pose_node), lock=True)


def if_pose_mute_locked(pose_node):
    if mc.objExists(pose_node) and mc.attributeQuery('mute', node=pose_node, exists=True):
        return mc.getAttr('{}.mute'.format(pose_node), lock=True)


def get_pose_weight_connected_attr(pose_node):
    if pose_weight_has_connection(pose_node):
        return mc.listConnections('{}.weight'.format(pose_node), d=False, p=True, scn=True)[0]
    else:
        return False


def break_pose_weight_connection(pose_node):
    if pose_weight_has_connection(pose_node):
        return mc.connectionInfo('{}.weight'.format(pose_node), isDestination=True)


def change_pose_weight(pose_node, weight, force=True, verbose=False):
    attr_name = "weight"
    if mc.objExists(pose_node) and mc.attributeQuery(attr_name, node=pose_node, exists=True):
        _min, _max = mc.attributeQuery(attr_name, node=pose_node, range=True)
        value = float(max(min(weight, _max), _min))
        plug = '{}.{}'.format(pose_node, attr_name)
        if force or value != mc.getAttr(plug):
            if mc.getAttr(plug, settable=True):
                if verbose:
                    # represent value in general format
                    print("setAttr \"{}\" {:.12g};".format(plug, value))
                mc.setAttr(plug, value)
                return True
    return False


def set_mute_pose(pose_node, value, force=True, verbose=False):
    attr_name = "mute"
    if mc.objExists(pose_node):
        if mc.attributeQuery(attr_name, node=pose_node, exists=True):
            value = bool(value)
            plug = '{}.{}'.format(pose_node, attr_name)
            if force or value != mc.getAttr(plug):
                if mc.getAttr(plug, settable=True):
                    if verbose:
                        print("setAttr \"{}\" {};".format(plug, int(value)))
                    mc.setAttr(plug, value)
                    return True
            return False
        else:
            raise AttributeError("'{}' has no attribute called 'mute'".format(pose_node))
    else:
        raise AttributeError("'{}' node doesn't exist".format(pose_node))


def get_mute_pose(pose_node):
    if mc.objExists(pose_node) and mc.attributeQuery('mute', node=pose_node, exists=True):
        return mc.getAttr('{}.mute'.format(pose_node))


def get_realtime_device_ip(realtime_device_node):
    if mc.objExists(realtime_device_node) and mc.attributeQuery('ipAddress',
                                                                node=realtime_device_node,
                                                                exists=True):
        return mc.getAttr('{}.ipAddress'.format(realtime_device_node))


def set_realtime_device_ip(realtime_device_node, ip, force=True):
    if mc.objExists(realtime_device_node) and mc.attributeQuery('ipAddress',
                                                                node=realtime_device_node,
                                                                exists=True):
        value = str(ip)
        plug = '{}.ipAddress'.format(realtime_device_node)
        if force or value != mc.getAttr(plug):
            mc.setAttr(plug, value, type="string")
            return True
    return False


def get_realtime_device_port(realtime_device_node):
    if mc.objExists(realtime_device_node) \
            and mc.attributeQuery('wifiPort', node=realtime_device_node, exists=True) \
            and mc.attributeQuery('usbPort', node=realtime_device_node, exists=True):

        conn_type = get_realtime_device_conn_type(realtime_device_node)
        if conn_type == 0:
            return mc.getAttr('{}.wifiPort'.format(realtime_device_node))
        elif conn_type == 1:
            return mc.getAttr('{}.usbPort'.format(realtime_device_node))
        else:
            raise RuntimeError('Unknown connection type {} in node'.format(
                conn_type, realtime_device_node))


def set_realtime_device_port(realtime_device_node, port, force=True):
    if mc.objExists(realtime_device_node) \
            and mc.attributeQuery('wifiPort', node=realtime_device_node, exists=True) \
            and mc.attributeQuery('usbPort', node=realtime_device_node, exists=True):

        conn_type = get_realtime_device_conn_type(realtime_device_node)

        if conn_type == 0:
            plug = '{}.wifiPort'.format(realtime_device_node)
        elif conn_type == 1:
            plug = '{}.usbPort'.format(realtime_device_node)
        else:
            raise RuntimeError('Unknown connection type {} in node'.format(
                conn_type, realtime_device_node))

        value = int(port)
        if force or value != mc.getAttr(plug):
            mc.setAttr(plug, value)
            return True
    return False


def get_realtime_device_conn_status(realtime_device_node):
    if mc.objExists(realtime_device_node) and mc.attributeQuery('connectionStatus',
                                                                node=realtime_device_node,
                                                                exists=True):
        return mc.getAttr('{}.connectionStatus'.format(realtime_device_node))


def get_realtime_device_conn_type(realtime_device_node):
    if mc.objExists(realtime_device_node) and mc.attributeQuery('connectionType',
                                                                node=realtime_device_node,
                                                                exists=True):
        return mc.getAttr('{}.connectionType'.format(realtime_device_node))


def set_realtime_device_conn_type(realtime_device_node, value, force=True):
    if mc.objExists(realtime_device_node) and mc.attributeQuery('connectionType',
                                                                node=realtime_device_node,
                                                                exists=True):
        plug = '{}.connectionType'.format(realtime_device_node)
        if force or value != mc.getAttr(plug):
            mc.setAttr(plug, value)
            return True
    return False


def get_realtime_device_live(realtime_device_node):
    if mc.objExists(realtime_device_node) and mc.attributeQuery('live', node=realtime_device_node,
                                                                exists=True):
        return mc.getAttr('{}.live'.format(realtime_device_node))


def set_realtime_device_live(realtime_device_node, live, force=True):
    if mc.objExists(realtime_device_node) and mc.attributeQuery('live', node=realtime_device_node,
                                                                exists=True):
        value = bool(live)
        plug = '{}.live'.format(realtime_device_node)
        if force or value != mc.getAttr(plug):
            mc.setAttr(plug, value)
            return True
    return False


def clipreader_save_clip(clipreader_node, clippath, time, videopath):
    if mc.objExists(clipreader_node):
        # pylint: disable=no-member
        mc.saveMocapData(clipreader_node, clippath, time, videopath)
        # pylint: enable=no-member
        return True
    return False


def get_adapter_sources(adapter_node):
    if mc.objExists(adapter_node) and mc.objectType(adapter_node) == 'MCPXAdapter':
        content = mc.sets(adapter_node, q=True)
        if content:
            return content
        return list()
    else:
        raise AttributeError(
            "{} node doesn't exist or inappropriate type. Should be {}".format(
                adapter_node, 'MCPXAdapter'))


def get_adapter_by_source(source):
    if mc.objExists(source) and mc.objectType(source) in ("MCPXClipReader", "MCPXRealTimeDevice"):
        for each in (mc.listSets(o=source) or []):
            if mc.objectType(each, i="MCPXAdapter"):
                return each

    return None


def get_project_directory():
    return mc.workspace(q=True, rd=True).replace("\\", "/").rstrip("/")


def get_scene_directory():
    return os.path.dirname(mc.file(q=True, sn=True))


def get_scene_name():
    file_name = mc.file(q=True, sn=True, shn=True)
    if file_name:
        return os.path.splitext(file_name)[0]
    return "untitled"


def set_clip_reader_path(clip_node, clipfile, force=True):
    if mc.objExists(clip_node) and mc.attributeQuery('clipFilepath', node=clip_node, exists=True):
        value = str(clipfile).replace("\\", "/")
        plug = "{}.clipFilepath".format(clip_node)
        if force or value != mc.getAttr(plug):
            mc.setAttr(plug, value, type="string")
            return True
    return False


def get_clip_reader_path(clip_node):
    if mc.objExists(clip_node) and mc.attributeQuery('clipFilepath', node=clip_node, exists=True):
        return mc.getAttr('{}.clipFilepath'.format(clip_node))


def get_realtime_device_path_template(realtime_device_node):
    if mc.objExists(realtime_device_node) and mc.attributeQuery('clipPathTemplate',
                                                                node=realtime_device_node,
                                                                exists=True):
        return mc.getAttr('{}.clipPathTemplate'.format(realtime_device_node))


def get_realtime_device_clip_length(realtime_device_node):
    if mc.objExists(realtime_device_node) and mc.attributeQuery('clipLength',
                                                                node=realtime_device_node,
                                                                exists=True):
        return mc.getAttr('{}.clipLength'.format(realtime_device_node))


def set_realtime_device_path_template(realtime_device_node, path_template, force=True):
    if mc.objExists(realtime_device_node) and mc.attributeQuery('clipPathTemplate',
                                                                node=realtime_device_node,
                                                                exists=True):
        value = str(path_template)
        plug = '{}.clipPathTemplate'.format(realtime_device_node)
        if force or value != mc.getAttr(plug):
            mc.setAttr(plug, value, type="string")
            return True
    return False


def set_realtime_device_clip_length(realtime_device_node, clip_length, force=True):
    if mc.objExists(realtime_device_node) and mc.attributeQuery('clipLength',
                                                                node=realtime_device_node,
                                                                exists=True):
        plug = '{}.clipLength'.format(realtime_device_node)
        if force or clip_length != mc.getAttr(plug):
            mc.setAttr(plug, clip_length)
            return True
    return False


def get_realtime_device_save_video(realtime_device_node):
    if mc.objExists(realtime_device_node) and mc.attributeQuery('recordVideo',
                                                                node=realtime_device_node,
                                                                exists=True):
        return mc.getAttr('{}.recordVideo'.format(realtime_device_node))


def set_realtime_device_save_video(realtime_device_node, save_video, force=True):
    if mc.objExists(realtime_device_node) and mc.attributeQuery('recordVideo',
                                                                node=realtime_device_node,
                                                                exists=True):
        value = bool(save_video)
        plug = '{}.recordVideo'.format(realtime_device_node)
        if force or value != mc.getAttr(plug):
            mc.setAttr(plug, value)
            return True
    return False


def lock_attribute(plug, state, force=True, verbose=False):
    if mc.objExists(plug):
        value = bool(state)
        if force or value != mc.getAttr(plug, l=True):
            if verbose:
                print("setAttr -l {} \"{}\";".format(("false", "true")[value], plug))
            mc.setAttr(plug, lock=value)
            return True
    return False


def rename_node(old_name, new_name):
    if mc.objExists(old_name):
        try:
            mc.rename(old_name, new_name)
        except:
            raise Exception("Can't rename '{}'.".format(old_name))


def setOptionVarValue(option_var, value, mode="sv"):
    return eval('mc.optionVar({}=("{}", "{}"))'.format(mode, option_var, value))


def get_real_attr(rest_attr, short=True):
    collectionNodeRest = None
    if mc.objectType(rest_attr, i="MCPXPose"):
        collectionNodes = mc.listConnections(rest_attr, p=True, d=False)
        if collectionNodes:
            collectionNodeRest = collectionNodes[0]
    elif mc.objectType(rest_attr, i="MCPXAttributeCollection"):
        collectionNodeRest = rest_attr
    else:
        raise RuntimeError("Unsupported node type.")

    if collectionNodeRest:
        sourceAttr = collectionNodeRest.replace(".restValue", ".plug")

        input_attrs = mc.listConnections(sourceAttr, plugs=True, d=False, scn=True)
        if input_attrs:
            ctrlName = input_attrs[0]
            if short:
                node = ctrlName.split(".", 1)[0]
                attr = mc.attributeName(ctrlName, short=True, leaf=False)
                ctrlName = ".".join((node, attr))
        else:
            ctrlName = "empty[{}]".format(get_index(rest_attr))  # for attr collection node
    else:
        ctrlName = "custom[{}]".format(get_index(rest_attr))  # for pose node

    return ctrlName


def get_rest_real_attr(rest_attr):
    collectionNodeRest = None
    if mc.objectType(rest_attr, i="MCPXPose"):
        collectionNodes = mc.listConnections(rest_attr, p=True, d=False)
        if collectionNodes:
            collectionNodeRest = collectionNodes[0]
    elif mc.objectType(rest_attr, i="MCPXAttributeCollection"):
        collectionNodeRest = rest_attr
    else:
        raise RuntimeError("Unsupported node type.")

    return collectionNodeRest


def if_real_attr(rest_attr):
    collectionNodeRest = None
    if mc.objectType(rest_attr, i="MCPXPose"):
        collectionNodes = mc.listConnections(rest_attr, p=True, d=False)
        if collectionNodes:
            collectionNodeRest = collectionNodes[0]
    elif mc.objectType(rest_attr, i="MCPXAttributeCollection"):
        collectionNodeRest = rest_attr
    else:
        raise RuntimeError("Unsupported node type.")

    if collectionNodeRest:
        sourceAttr = collectionNodeRest.replace(".restValue", ".plug")

        input_attrs = mc.listConnections(sourceAttr, plugs=True, d=False, scn=True)
        if input_attrs:
            return True
        else:
            return False
    else:
        return False


def get_pose_attrs(node, include_node_name=True):
    if mc.objExists(node):
        attrs = list()
        plug = "{}.attrs".format(node)
        for index in (mc.getAttr(plug, multiIndices=True) or []):
            if mc.objectType(node) in ("MCPXPose", "MCPXAttributeCollection"):
                if include_node_name:
                    attrs.append("{}.attrs[{}]".format(node, index))
                else:
                    attrs.append("attrs[{}]".format(index))
            else:
                raise RuntimeError("Unsupported node type.")

        return attrs

    raise AttributeError("'{}' node doesn't exist.".format(node))


def get_pose_controls(pose_node):
    controls = list()
    if mc.objExists(pose_node) and mc.objectType(pose_node, i="MCPXPose"):
        for root in get_pose_attrs(pose_node):
            plug = get_real_attr(root + ".rest")
            node = plug.split(".")[0]
            if node not in controls and mc.objExists(node):
                controls.append(node)
    return controls


def get_rest_attr_value(plug):
    if mc.objExists(plug):
        return mc.getAttr(plug + ".rest")

    raise AttributeError("'{}' plug doesn't exist.".format(plug))


def set_attr_value(plug, value, force=True, verbose=False):
    if mc.objExists(plug):
        value = float(value)
        if force or value != mc.getAttr(plug):
            if mc.getAttr(plug, settable=True):
                if verbose:
                    # represent value in general format
                    print("setAttr \"{}\" {:.12g};".format(plug, value))
                mc.setAttr(plug, value)
                return True
        return False
    else:
        raise AttributeError("'{}' plug doesn't exist.".format(plug))


def get_attr_value(plug):
    if mc.objExists(plug):
        return mc.getAttr(plug)
    raise AttributeError("'{}' plug doesn't exist.".format(plug))


def is_attr_locked(plug):
    if mc.objExists(plug):
        return mc.getAttr(plug, lock=True)
    raise AttributeError("'{}' plug doesn't exist.".format(plug))


def if_attr_dirty(plug):
    if mc.objExists(plug) and has_attr_connection(plug):
        connected_plug = mc.connectionInfo(plug, sourceFromDestination=True)
        if connected_plug:
            plug_value = mc.getAttr(plug)
            connected_plug_value = mc.getAttr(connected_plug)
            if plug_value != connected_plug_value:
                return True
            else:
                return False
        else:
            return False
    else:
        return False


def get_pose_attrs_quantity(pose_node):
    if mc.objExists(pose_node) and mc.attributeQuery('attrs', node=pose_node, exists=True):
        return mc.getAttr("{}.attrs".format(pose_node), size=True)


def get_node_uuid(node):
    if mc.objExists(node):
        return mc.ls(node, uuid=True)[0]

    raise AttributeError("'{}' node doesn't exist.".format(node))


def is_node_locked(node):
    if mc.objExists(node):
        return mc.lockNode(node, q=True, l=True)[0]
    raise AttributeError("'{}' node doesn't exist.".format(node))


def is_node_referenced(node):
    if mc.objExists(node):
        return mc.referenceQuery(node, inr=True)
    raise AttributeError("'{}' node doesn't exist.".format(node))


def is_node_read_only(node):
    if mc.objExists(node):
        return is_node_locked(node) or is_node_referenced(node)
    raise AttributeError("'{}' node doesn't exist.".format(node))


def list_attrs(node, only_valid=False, *args, **kwargs):
    attributes = mc.listAttr(node, *args, **kwargs) or []
    if only_valid:
        attributes = [a for a in attributes if is_attr_type_valid(node + "." + a)]
    return attributes


def get_order_list(node):
    if mc.objExists(node) and mc.attributeQuery("order", n=node, ex=True):
        return mc.getAttr(node + ".order") or []
    return list()


def set_order_list(node, array, force=True):
    if mc.objExists(node) and mc.attributeQuery("order", n=node, ex=True):
        plug = "{}.order".format(node)
        if force or array != mc.getAttr(plug):
            mc.setAttr(plug, len(array), *array, type="stringArray")
            return True
    return False


def sort_nodes_by_order(nodes, order_array, check_nmsp=None):
    if check_nmsp:
        if check_nmsp.startswith(":"):
            check_nmsp = check_nmsp[1:]

    for name in order_array[::-1]:
        if name.startswith(":"):
            name = name[1:]

        for name in [name] + [":".join((check_nmsp, name))] * bool(check_nmsp):
            if name in nodes:
                nodes.remove(name)
                nodes.insert(0, name)
                break

    return nodes


def get_evaluated_source(plug):
    connection_plugs = mc.listConnections(plug, d=False, p=True)
    if not connection_plugs:
        return plug
    return get_evaluated_source(connection_plugs[0])


def list_connections(*args, **kwargs):
    return mc.listConnections(*args, **kwargs)
