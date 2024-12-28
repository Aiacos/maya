import os

import maya.api.OpenMaya as OpenMaya
import maya.cmds as mc
import maya.mel as mel
import sys

import mocapx


def request_module(func):
    def wrapped(*args, **kwargs):
        plugin_name = '{}.mll'.format(mocapx.MODULE_NAME)
        if not mc.pluginInfo(plugin_name, query=True, loaded=True):
            try:
                mc.loadPlugin(plugin_name)
            except RuntimeError as error:
                mc.error('Error on loading {} module\n{}'.format(
                    mocapx.MODULE_NAME, error))
                return None
        return func(*args, **kwargs)

    return wrapped


def unload_module_on_fail(func):
    def wrapped(*args, **kwargs):
        plugin_name = '{}.mll'.format(mocapx.MODULE_NAME)
        try:
            return func(*args, **kwargs)
        except Exception as error:
            if mc.pluginInfo(plugin_name, query=True, loaded=True):
                mc.unloadPlugin(mocapx.MODULE_NAME)
            mc.error('Initialize procedures for module {} failed with error\n{}'.format(
                mocapx.MODULE_NAME, error))

    return wrapped


def existence_check(func):
    def wrapped(obj_list, *args, **kwargs):
        if not isinstance(obj_list, (list,)):
            raise ValueError('parameter should be a list')
        existing = list(filter((lambda el: mc.objExists(el)), obj_list))
        return func(existing, *args, **kwargs)

    return wrapped


def shift_referenced_anim_curve(anim_curve, shift):
    anim_curve_output = "{}.output".format(anim_curve)

    out_connections = mc.connectionInfo(anim_curve_output, dfs=True)
    if out_connections:
        add_node = mc.createNode("addDoubleLinear", n="{}_shift".format(anim_curve.split(":")[-1]),
                                 ss=True)
        add_node_output = "{}.output".format(add_node)

        mc.connectAttr(anim_curve_output, "{}.input1".format(add_node))
        mc.setAttr("{}.input2".format(add_node), shift)

        for each in out_connections:
            mc.connectAttr(add_node_output, each, f=True)


def transplant_outs_to_adapter(data_source, adapter):
    # reconnect out connections from data_source to adapter
    for attr_name in mc.listAttr(data_source, userDefined=True) or []:
        # Do not connect multipliers
        if attr_name == 'multipliers':
            continue
        attr_parents = mc.attributeQuery(attr_name, node=data_source, listParent=True)
        if attr_parents and 'multipliers' in attr_parents:
            continue

        source_plug = data_source + "." + attr_name
        if not mc.attributeQuery(attr_name, node=adapter, ex=True):
            data_type = mc.getAttr(source_plug, type=True)
            try:
                mc.addAttr(adapter, ln=attr_name, at=data_type)
            except RuntimeError:
                mc.addAttr(adapter, ln=attr_name, dt=data_type)

        adapter_plug = adapter + "." + attr_name
        for out_connection in mc.connectionInfo(source_plug, dfs=True) or []:
            if out_connection != adapter_plug:
                mc.disconnectAttr(source_plug, out_connection)
                mc.connectAttr(adapter_plug, out_connection)
        if not (mc.isConnected(source_plug, adapter_plug) or mc.getAttr(adapter_plug, lock=True)):
            mc.connectAttr(source_plug, adapter_plug)


def get_adapters_where_source_active(source):
    if mc.objExists(source) and mc.objectType(source) in ("MCPXClipReader", "MCPXRealTimeDevice"):
        adapters = set()
        for plug in mc.listConnections(source + ".message", s=False, type="MCPXAdapter", p=True) or []:
            adapter, attr_name = plug.split(".")
            if attr_name == "activeSource":
                adapters.add(adapter)
        return list(adapters)
    raise AttributeError("'{}' node doesn't exist or inappropriate type.".format(source))


def switch_data_source(data_source, adapter):
    # break incoming for each dynamic attribute if it is not locked
    for attr_name in mc.listAttr(adapter, userDefined=True) or []:
        adapter_plug = adapter + "." + attr_name
        if not mc.getAttr(adapter_plug, lock=True):
            in_connection = mc.connectionInfo(adapter_plug, sfd=True)
            if in_connection:
                mc.disconnectAttr(in_connection, adapter_plug)
                if mc.getAttr(adapter_plug):
                    mc.setAttr(adapter_plug, 0)

    # reconnect out connections from data_source to adapter
    transplant_outs_to_adapter(data_source, adapter)


def get_time_node():
    time_nodes = mc.ls(type='time')
    if time_nodes:
        return time_nodes[0]
    else:
        raise RuntimeError('No time node can be found!')


def clipreader_load_clip(clipreader_node, clipfile):
    if not clipfile:
        mc.warning("Filepath not specified.")

    elif os.path.exists(clipfile):
        if mc.objExists(clipreader_node):
            out = mc.loadClipFromFile(clipreader_node, clipfile)
            # TODO: Find a better way how to invalidate EG/DG
            # When new data fetcher from file we need to invalidate
            # Evaluation Graph in EG evaluation mode.
            # When DG evaluation mode is used it will force maya to call setDependetsDirty again
            # Reconnection time to clipreader do causing this.
            if out:
                time_out_plug = '{}.outTime'.format(get_time_node())
                time_in_plug = '{}.time'.format(clipreader_node)
                if mc.isConnected(time_out_plug, time_in_plug):
                    mc.disconnectAttr(time_out_plug, time_in_plug)
                mc.connectAttr(time_out_plug, time_in_plug, f=True)

                for adapter in get_adapters_where_source_active(clipreader_node):
                    switch_data_source(clipreader_node, adapter)

            return out
    else:
        mc.warning("'{}' doesn't exist.".format(clipfile))

    return False


def get_channelbox_selection():
    channel_box = mel.eval(
        'global string $gChannelBoxName; $temp=$gChannelBoxName;')
    channels = mc.channelBox(channel_box, q=True, sma=True)
    if not channels:
        return list()
    return channels


def get_selected_attrs():
    channels = get_channelbox_selection()
    selection = mc.ls(sl=True)
    selected_plugs = filter_plugs(selection)
    selected_nodes = filter_controls(selection)
    if channels and selected_nodes:
        plugs = list()
        for ctrl in selected_nodes:
            plugs.extend(['{}.{}'.format(ctrl, attr) for attr in channels])
        correct_plugs = filter_plugs(plugs)
        selected_plugs.extend(correct_plugs)
    return selected_plugs


@existence_check
def filter_controls(input_list):
    nodes = list(filter((lambda el: '.' not in el), input_list))
    controls = list(filter((lambda el: mc.objectType(el) in ('transform', 'joint')), nodes))
    return controls


@existence_check
def filter_plugs(input_list):
    plugs = list(filter((lambda el: '.' in el), input_list))
    plugs_on_transforms = list(filter(
        (lambda el: mc.objectType(el) in ('transform', 'joint')), plugs))
    plugs_keyable = list(filter(
        (lambda el: mc.getAttr(el, keyable=True)), plugs_on_transforms))
    unlocked_plugs = list(filter(lambda el: not mc.getAttr(el, lock=True), plugs_keyable))
    return unlocked_plugs


@existence_check
def filter_poses(input_list):
    poses = list(filter((lambda el: mc.objectType(el) == 'MCPXPose'), input_list))
    return poses


def is_attr_type_valid(plug):
    return mc.getAttr(plug, type=True) in mocapx.ATTRIBUTE_TYPES


def get_attributes(input_list):
    full_attr_list = list()
    for ctrl in filter_controls(input_list):
        attrs = mc.listAttr(ctrl, keyable=True)
        if attrs:
            plugs = ['{}.{}'.format(ctrl, attr) for attr in attrs]
            attrs = list(filter(is_attr_type_valid, plugs))
            full_attr_list.extend(attrs)
    return filter_plugs(full_attr_list)


def get_restplugs(plug_list):
    valueplug_restplug_pairs = list()
    for valueplug in plug_list:
        connected_plugs = mc.listConnections(valueplug, plugs=True, source=False, destination=True,
                                             skipConversionNodes=True,
                                             type='MCPXAttributeCollection')
        if connected_plugs:
            connected_plug = connected_plugs[0]
            restplug = connected_plug.replace(".plug", ".restValue")
            valueplug_restplug_pairs.append((valueplug, restplug))
    return valueplug_restplug_pairs


def round_value(value, threshold=4):
    if threshold > 0:
        temp = 10.0 ** threshold
        return round(int(value * temp) / temp, threshold)
    else:
        return round(value, threshold)


def get_next_index(plug):
    indexes = mc.getAttr(plug, multiIndices=True)
    if indexes:
        new_index = int(max(indexes)) + 1
    else:
        new_index = 0
    return new_index


def get_index(plug):
    if '[' in plug and ']' in plug:
        index = plug.split('[')[1].split(']')[0]
        return int(index)
    else:
        raise AttributeError('Trying to get index fro not array plug!')


def adapt_name(name):
    return name[1:] if name.startswith(":") else name


def get_mobject(node_name):
    sel = OpenMaya.MSelectionList()
    try:
        sel.add(node_name)
    except RuntimeError as er:
        # TODO Show warning message in caller
        mc.warning('Cannot get MObject for {}'.format(node_name))
        return None
    node = sel.getDependNode(0)
    return node


def get_mplug(plug):
    elements = plug.split(".")
    m_object = get_mobject(elements.pop(0))
    m_dag_node = OpenMaya.MFnDependencyNode(m_object)
    m_plug = None
    for element in elements:
        parsed = element.replace("]", "").split("[")
        if m_plug is None:
            m_plug = m_dag_node.findPlug(parsed[0], False)
        else:
            attr = m_dag_node.attribute(parsed[0])
            if not attr:
                return None
            m_plug = m_plug.child(attr)
        if m_plug:
            if len(parsed) == 2:
                m_plug = m_plug.elementByLogicalIndex(int(parsed[1]))
    return m_plug


def is_path_abs(filepath):
    filepath = filepath.replace("\\", "/")
    drive_or_network = os.path.splitdrive(filepath)[0]

    if drive_or_network:
        if not os.path.exists(drive_or_network):
            return False
    else:
        if mocapx.platform == "Windows":
            return False
        # for systems which do not use drive specifications need to check root directory
        dirs = list(filter(None, filepath.split("/")))
        root = filepath.split("/".join(dirs[1:]))[0]  # first dir with keeping slashes
        if not os.path.exists(root):
            # e.g. "/home" on Linux - absolute, "home" - not
            return False

    return True


def import_scene(filepath, namespace):
    try:
        mc.file(filepath, i=True, ns=namespace)
    except:
        raise RuntimeError('Cannot import {}!'.format(filepath))


def get_parent_plug(plug):
    node = plug.split('.')[0]
    attr = plug.split('.')[-1]
    try:
        parent = mc.attributeQuery(attr, node=node, listParent=True)[0]
    except:
        return None
    return parent


def get_frame_range():
    start_frame = mc.playbackOptions(q=True, animationStartTime=True)
    end_frame = mc.playbackOptions(q=True, animationEndTime=True)
    return start_frame, end_frame


def get_depend_on(plug, node_names=tuple(), node_types=tuple()):
    if (not node_names and not node_types) or (node_names and node_types):
        raise AttributeError('Provide ether specific node name or node type!')
    sel_list = OpenMaya.MSelectionList()
    sel_list.add(plug)
    mplug = sel_list.getPlug(0)
    this_node = sel_list.getDependNode(0)
    depend_iter = OpenMaya.MItDependencyGraph(
        mplug, OpenMaya.MFn.kInvalid, OpenMaya.MItDependencyGraph.kUpstream)
    out = list()
    while not depend_iter.isDone():
        node = depend_iter.currentNode()
        if this_node == node:
            pass
        elif node.hasFn(OpenMaya.MFn.kDagNode):
            fn = OpenMaya.MFnDagNode(node)
            if node_names and fn.fullPathName() in node_names:
                out.append(fn.fullPathName())
            if node_types and fn.typeName in node_types:
                out.append(fn.fullPathName())
        elif node.hasFn(OpenMaya.MFn.kDependencyNode):
            fn = OpenMaya.MFnDependencyNode(node)
            if node_names and fn.name() in node_names:
                out.append(fn.name())
            if node_types and fn.typeName in node_types:
                out.append(fn.name())
        depend_iter.next()
    if len(out):
        return list(set(out))
    else:
        return None


def has_attr_connection(plug):
    if mc.objExists(plug):
        return mc.connectionInfo(plug, isDestination=True)

    raise AttributeError("'{}' plug doesn't exist.".format(plug))


def is_node_anim_curve(node, subtype=""):
    if mc.objExists(node):
        return mc.objectType(node).startswith("animCurve" + subtype)

    raise AttributeError("'{}' node doesn't exist.".format(node))


def is_node_expression(node):
    if mc.objExists(node):
        return mc.objectType(node) == "expression"

    raise AttributeError("'{}' node doesn't exist.".format(node))


def is_node_constraint(node):
    if mc.objExists(node):
        return mc.objectType(node, isa="constraint")

    raise AttributeError("'{}' node doesn't exist.".format(node))


def is_node_pair_blend(node):
    if mc.objExists(node):
        return mc.objectType(node, isa="pairBlend")

    raise AttributeError("'{}' node doesn't exist.".format(node))


def long_constr(input_val):
    if sys.version_info > (3,):
        return int(input_val)
    else:
        return long(input_val)
