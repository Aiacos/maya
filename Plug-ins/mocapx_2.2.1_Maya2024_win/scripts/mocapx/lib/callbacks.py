import maya.api.OpenMaya as OpenMaya
import maya.cmds as mc
import maya.mel as mel

import mocapx
from mocapx.lib.nodes import get_anim_blend_node
from mocapx.lib.utils import shift_referenced_anim_curve, get_mobject, adapt_name, \
    switch_data_source, transplant_outs_to_adapter, clipreader_load_clip


def preload_clipreader_clips():
    for clip_node in mc.ls(type="MCPXClipReader"):
        filepath = mc.getAttr('{}.clipFilepath'.format(clip_node))
        if filepath:
            clipreader_load_clip(clip_node, filepath)


def refresh_plugin_global_callbacks():
    # noinspection PyUnusedLocal
    def surpass_on(clientData):
        mocapx.suppress_on_scene_loading = True

    # noinspection PyUnusedLocal
    def surpass_off(clientData):
        mocapx.suppress_on_scene_loading = False

        if mocapx.mocapx_menu:
            for button in mocapx.mocapx_menu.buttons:
                if hasattr(button, "refresh_callbacks"):
                    button.refresh_callbacks()
        if mocapx.mocapx_shelf:
            for button in mocapx.mocapx_shelf.buttons:
                if hasattr(button, "refresh_callbacks"):
                    button.refresh_callbacks()
        if mocapx.poselib_editor:
            picker = mocapx.poselib_editor.widget.poselib_picker
            picker.refresh_state()

        preload_clipreader_clips()

        refresh_plugin_nodes_callbacks()

    messages = ((OpenMaya.MSceneMessage.kBeforeNew,
                 OpenMaya.MSceneMessage.kAfterNew),
                (OpenMaya.MSceneMessage.kBeforeOpen,
                 OpenMaya.MSceneMessage.kAfterOpen),
                (OpenMaya.MSceneMessage.kBeforeImport,
                 OpenMaya.MSceneMessage.kAfterImport),
                (OpenMaya.MSceneMessage.kBeforeCreateReference,
                 OpenMaya.MSceneMessage.kAfterCreateReference),
                (OpenMaya.MSceneMessage.kBeforeLoadReference,
                 OpenMaya.MSceneMessage.kAfterLoadReference))

    for on_message, off_message in messages:
        cbid = OpenMaya.MSceneMessage.addCallback(on_message, surpass_on)
        mocapx.scene_state_cbids.append(cbid)
        cbid = OpenMaya.MSceneMessage.addCallback(off_message, surpass_off)
        mocapx.scene_state_cbids.append(cbid)


def clean_plugin_global_callbacks():
    # remove scene callbacks
    if mocapx.scene_state_cbids:
        for each in mocapx.scene_state_cbids:
            OpenMaya.MMessage.removeCallback(each)
        mocapx.scene_state_cbids = list()


def refresh_plugin_nodes_callbacks():
    clean_plugin_nodes_callbacks()

    # set clipreader callbacks
    nodes_type = 'MCPXClipReader'
    for node_name in mc.ls(et=nodes_type):
        _set_clipreader_callbacks(node_name)

    if not mocapx.clipreader_added_cbid:
        mocapx.clipreader_added_cbid = OpenMaya.MDGMessage.addNodeAddedCallback(
            clipreader_added_cb, nodes_type)
    if not mocapx.clipreader_removed_cbid:
        mocapx.clipreader_removed_cbid = OpenMaya.MDGMessage.addNodeRemovedCallback(
            adapter_removed_cb, nodes_type)

    # set adapter callbacks
    nodes_type = 'MCPXAdapter'
    for node_name in mc.ls(et=nodes_type):
        _set_adapter_callbacks(node_name)

    if not mocapx.adapter_added_cbid:
        mocapx.adapter_added_cbid = OpenMaya.MDGMessage.addNodeAddedCallback(
            adapter_added_cb, nodes_type)
    if not mocapx.adapter_removed_cbid:
        mocapx.adapter_removed_cbid = OpenMaya.MDGMessage.addNodeRemovedCallback(
            adapter_removed_cb, nodes_type)

    # set poseLib callbacks
    nodes_type = 'MCPXPoselib'
    for node_name in mc.ls(et=nodes_type):
        _set_poseLib_callbacks(node_name)

    if not mocapx.poseLib_added_cbid:
        mocapx.poseLib_added_cbid = OpenMaya.MDGMessage.addNodeAddedCallback(
            poseLib_added_cb, nodes_type)
    if not mocapx.poseLib_removed_cbid:
        mocapx.poseLib_removed_cbid = OpenMaya.MDGMessage.addNodeRemovedCallback(
            poseLib_removed_cb, nodes_type)

    # set pose callbacks
    nodes_type = 'MCPXPose'
    for node_name in mc.ls(et=nodes_type):
        _set_pose_callbacks(node_name)

    if not mocapx.pose_added_cbid:
        mocapx.pose_added_cbid = OpenMaya.MDGMessage.addNodeAddedCallback(
            pose_added_cb, nodes_type)
    if not mocapx.pose_removed_cbid:
        mocapx.pose_removed_cbid = OpenMaya.MDGMessage.addNodeRemovedCallback(
            pose_removed_cb, nodes_type)

    # set poseApply callbacks
    nodes_type = 'MCPXPoseApply'
    for node_name in mc.ls(et=nodes_type):
        _set_poseApply_callbacks(node_name)

    if not mocapx.poseApply_added_cbid:
        mocapx.poseApply_added_cbid = OpenMaya.MDGMessage.addNodeAddedCallback(
            poseApply_added_cb, nodes_type)
    if not mocapx.poseApply_removed_cbid:
        mocapx.poseApply_removed_cbid = OpenMaya.MDGMessage.addNodeRemovedCallback(
            poseApply_removed_cb, nodes_type)


def clean_plugin_nodes_callbacks():
    # remove clipreader callbacks
    if mocapx.clipreader_added_cbid:
        OpenMaya.MMessage.removeCallback(mocapx.clipreader_added_cbid)
        mocapx.clipreader_added_cbid = None
    if mocapx.clipreader_removed_cbid:
        OpenMaya.MMessage.removeCallback(mocapx.clipreader_removed_cbid)
        mocapx.clipreader_removed_cbid = None
    if mocapx.clipreader_onconnect_cbids:
        for each in mocapx.clipreader_onconnect_cbids:
            OpenMaya.MMessage.removeCallback(mocapx.clipreader_onconnect_cbids[each])
        mocapx.clipreader_onconnect_cbids = dict()
    if mocapx.clipreader_renamed_cbids:
        for each in mocapx.clipreader_renamed_cbids:
            OpenMaya.MMessage.removeCallback(mocapx.clipreader_renamed_cbids[each])
        mocapx.clipreader_renamed_cbids = dict()

    # remove adapter callbacks
    if mocapx.adapter_added_cbid:
        OpenMaya.MMessage.removeCallback(mocapx.adapter_added_cbid)
        mocapx.adapter_added_cbid = None
    if mocapx.adapter_removed_cbid:
        OpenMaya.MMessage.removeCallback(mocapx.adapter_removed_cbid)
        mocapx.adapter_removed_cbid = None
    if mocapx.adapter_active_change_cbids:
        for each in mocapx.adapter_active_change_cbids:
            OpenMaya.MMessage.removeCallback(mocapx.adapter_active_change_cbids[each])
        mocapx.adapter_active_change_cbids = dict()
    if mocapx.adapter_renamed_cbids:
        for each in mocapx.adapter_renamed_cbids:
            OpenMaya.MMessage.removeCallback(mocapx.adapter_renamed_cbids[each])
        mocapx.adapter_renamed_cbids = dict()

    # remove poseLib callbacks
    if mocapx.poseLib_added_cbid:
        OpenMaya.MMessage.removeCallback(mocapx.poseLib_added_cbid)
        mocapx.poseLib_added_cbid = None
    if mocapx.poseLib_removed_cbid:
        OpenMaya.MMessage.removeCallback(mocapx.poseLib_removed_cbid)
        mocapx.poseLib_removed_cbid = None
    if mocapx.poseLib_before_delete_cbids:
        for each in mocapx.poseLib_before_delete_cbids:
            OpenMaya.MMessage.removeCallback(mocapx.poseLib_before_delete_cbids[each])
        mocapx.poseLib_before_delete_cbids = dict()
    if mocapx.poseLib_renamed_cbids:
        for each in mocapx.poseLib_renamed_cbids:
            OpenMaya.MMessage.removeCallback(mocapx.poseLib_renamed_cbids[each])
        mocapx.poseLib_renamed_cbids = dict()

    # remove pose callbacks
    if mocapx.pose_added_cbid:
        OpenMaya.MMessage.removeCallback(mocapx.pose_added_cbid)
        mocapx.pose_added_cbid = None
    if mocapx.pose_removed_cbid:
        OpenMaya.MMessage.removeCallback(mocapx.pose_removed_cbid)
        mocapx.pose_removed_cbid = None
    if mocapx.pose_attr_changed_cbids:
        for each in mocapx.pose_attr_changed_cbids:
            OpenMaya.MMessage.removeCallback(mocapx.pose_attr_changed_cbids[each])
        mocapx.pose_attr_changed_cbids = dict()

    # remove poseApply callbacks
    if mocapx.poseApply_added_cbid:
        OpenMaya.MMessage.removeCallback(mocapx.poseApply_added_cbid)
        mocapx.poseApply_added_cbid = None
    if mocapx.poseApply_removed_cbid:
        OpenMaya.MMessage.removeCallback(mocapx.poseApply_removed_cbid)
        mocapx.poseApply_removed_cbid = None
    if mocapx.poseApply_attr_changed_cbids:
        for each in mocapx.poseApply_attr_changed_cbids:
            OpenMaya.MMessage.removeCallback(mocapx.poseApply_attr_changed_cbids[each])
        mocapx.poseApply_attr_changed_cbids = dict()
    if mocapx.poseApply_before_delete_cbids:
        for each in mocapx.poseApply_before_delete_cbids:
            OpenMaya.MMessage.removeCallback(mocapx.poseApply_before_delete_cbids[each])
        mocapx.poseApply_before_delete_cbids = dict()
    if mocapx.poseApply_renamed_cbids:
        for each in mocapx.poseApply_renamed_cbids:
            OpenMaya.MMessage.removeCallback(mocapx.poseApply_renamed_cbids[each])
        mocapx.poseApply_renamed_cbids = dict()


def parse_attr_changed_cb(msg, plug):
    if isinstance(plug, (str, unicode)):
        plug_name = plug
    else:
        plug_name = plug.name()

    __messages = (
        "kAttributeAdded",
        "kAttributeArrayAdded",
        "kAttributeArrayRemoved",
        "kAttributeEval",
        "kAttributeKeyable",
        "kAttributeLocked",
        "kAttributeRemoved",
        "kAttributeRenamed",
        "kAttributeSet",
        "kAttributeUnkeyable",
        "kAttributeUnlocked",
        "kConnectionBroken",
        "kConnectionMade",
        "kIncomingDirection",
        "kKeyChangeInvalid",
        "kKeyChangeLast",
        "kLast",
        "kMakeKeyable",
        "kMakeUnkeyable",
        "kOtherPlugSet")

    for each in __messages:
        if msg & eval("OpenMaya.MNodeMessage.{}".format(each)):
            return (plug_name, each)


def _set_clipreader_callbacks(node_name):
    node_mobject = get_mobject(node_name)
    if node_mobject:
        if node_name not in mocapx.clipreader_onconnect_cbids:
            callback_id = OpenMaya.MNodeMessage.addAttributeChangedCallback(
                node_mobject, clipreader_onconnect_cb)
            mocapx.clipreader_onconnect_cbids[node_name] = callback_id
        if node_name not in mocapx.clipreader_renamed_cbids:
            callback_id = OpenMaya.MNodeMessage.addNameChangedCallback(
                node_mobject, clipreader_renamed_cb)
            mocapx.clipreader_renamed_cbids[node_name] = callback_id


def _set_adapter_callbacks(node_name):
    node_mobject = get_mobject(node_name)
    if node_mobject:
        if node_name not in mocapx.adapter_active_change_cbids:
            callback_id = OpenMaya.MNodeMessage.addAttributeChangedCallback(
                node_mobject, adapter_active_source_changed_cb)
            mocapx.adapter_active_change_cbids[node_name] = callback_id
        if node_name not in mocapx.adapter_renamed_cbids:
            callback_id = OpenMaya.MNodeMessage.addNameChangedCallback(
                node_mobject, adapter_renamed_cb)
            mocapx.adapter_renamed_cbids[node_name] = callback_id


def _set_poseLib_callbacks(node_name):
    node_mobject = get_mobject(node_name)
    if node_mobject:
        if node_name not in mocapx.poseLib_before_delete_cbids:
            callback_id = OpenMaya.MNodeMessage.addNodeAboutToDeleteCallback(
                node_mobject, poseLib_about_to_delete_cb)
            mocapx.poseLib_before_delete_cbids[node_name] = callback_id
        if node_name not in mocapx.poseLib_renamed_cbids:
            callback_id = OpenMaya.MNodeMessage.addNameChangedCallback(
                node_mobject, poseLib_renamed_cb)
            mocapx.poseLib_renamed_cbids[node_name] = callback_id


def _set_pose_callbacks(node_name):
    if node_name not in mocapx.pose_attr_changed_cbids:
        node_mobject = get_mobject(node_name)
        if node_mobject:
            callback_id = OpenMaya.MNodeMessage.addAttributeChangedCallback(
                node_mobject, pose_attr_changed_cb)
            mocapx.pose_attr_changed_cbids[node_name] = callback_id


def _set_poseApply_callbacks(node_name):
    if node_name:
        node_mobject = get_mobject(node_name)
        if node_mobject:
            if node_name not in mocapx.poseApply_before_delete_cbids:
                callback_id = OpenMaya.MNodeMessage.addNodeAboutToDeleteCallback(
                    node_mobject, poseApply_about_to_delete_cb)
                mocapx.poseApply_before_delete_cbids[node_name] = callback_id
            if node_name not in mocapx.poseApply_renamed_cbids:
                callback_id = OpenMaya.MNodeMessage.addNameChangedCallback(
                    node_mobject, poseApply_renamed_cb)
                mocapx.poseApply_renamed_cbids[node_name] = callback_id
            if node_name not in mocapx.poseApply_attr_changed_cbids:
                callback_id = OpenMaya.MNodeMessage.addAttributeChangedCallback(
                    node_mobject, poseApply_attr_changed_cb)
                mocapx.poseApply_attr_changed_cbids[node_name] = callback_id


# noinspection PyUnusedLocal,PyArgumentList
def clipreader_added_cb(node, clientData=None):
    if not mocapx.suppress_on_scene_loading:
        node_name = OpenMaya.MFnDependencyNode(node).name()
        _set_clipreader_callbacks(node_name)


# noinspection PyUnusedLocal,PyArgumentList
def adapter_added_cb(node, clientData=None):
    if not mocapx.suppress_on_scene_loading:
        node_name = OpenMaya.MFnDependencyNode(node).name()
        _set_adapter_callbacks(node_name)


# noinspection PyUnusedLocal,PyArgumentList
def poseLib_added_cb(node, clientData=None):
    if not mocapx.suppress_on_scene_loading:
        node_name = OpenMaya.MFnDependencyNode(node).name()
        _set_poseLib_callbacks(node_name)


# noinspection PyUnusedLocal,PyArgumentList
def pose_added_cb(node, clientData=None):
    if not mocapx.suppress_on_scene_loading:
        node_name = OpenMaya.MFnDependencyNode(node).name()
        _set_pose_callbacks(node_name)


# noinspection PyUnusedLocal,PyArgumentList
def poseApply_added_cb(node, clientData=None):
    if not mocapx.suppress_on_scene_loading:
        node_name = OpenMaya.MFnDependencyNode(node).name()
        _set_poseApply_callbacks(node_name)


# noinspection PyUnusedLocal,PyArgumentList
def clipreader_renamed_cb(node, prevName, clientData=None):
    if not mocapx.suppress_on_scene_loading:
        new_name = OpenMaya.MFnDependencyNode(node).name()
        new_name = adapt_name(new_name)
        mocapx.clipreader_onconnect_cbids[new_name] = mocapx.clipreader_onconnect_cbids.pop(
            prevName)
        mocapx.clipreader_renamed_cbids[new_name] = mocapx.clipreader_renamed_cbids.pop(prevName)


# noinspection PyUnusedLocal,PyArgumentList
def adapter_renamed_cb(node, prevName, clientData=None):
    if not mocapx.suppress_on_scene_loading:
        new_name = OpenMaya.MFnDependencyNode(node).name()
        new_name = adapt_name(new_name)
        mocapx.adapter_active_change_cbids[new_name] = mocapx.adapter_active_change_cbids.pop(
            prevName)
        mocapx.adapter_renamed_cbids[new_name] = mocapx.adapter_renamed_cbids.pop(prevName)


# noinspection PyUnusedLocal,PyArgumentList
def poseLib_renamed_cb(node, prevName, clientData=None):
    if not mocapx.suppress_on_scene_loading:
        new_name = OpenMaya.MFnDependencyNode(node).name()
        new_name = adapt_name(new_name)
        mocapx.poseLib_before_delete_cbids[new_name] = mocapx.poseLib_before_delete_cbids.pop(
            prevName)
        mocapx.poseLib_renamed_cbids[new_name] = mocapx.poseLib_renamed_cbids.pop(prevName)


# noinspection PyUnusedLocal,PyArgumentList
def poseApply_renamed_cb(node, prevName, clientData=None):
    if not mocapx.suppress_on_scene_loading:
        new_name = OpenMaya.MFnDependencyNode(node).name()
        new_name = adapt_name(new_name)
        mocapx.poseApply_attr_changed_cbids[new_name] = mocapx.poseApply_attr_changed_cbids.pop(
            prevName)
        mocapx.poseApply_before_delete_cbids[new_name] = mocapx.poseApply_before_delete_cbids.pop(
            prevName)
        mocapx.poseApply_renamed_cbids[new_name] = mocapx.poseApply_renamed_cbids.pop(prevName)


# noinspection PyUnusedLocal,PyArgumentList
def clipreader_removed_cb(node, clientData=None):
    if not mocapx.suppress_on_scene_loading:
        node_name = OpenMaya.MFnDependencyNode(node).name()
        if node_name in mocapx.clipreader_onconnect_cbids:
            OpenMaya.MMessage.removeCallback(mocapx.clipreader_onconnect_cbids[node_name])
            del mocapx.clipreader_onconnect_cbids[node_name]
        if node_name in mocapx.clipreader_renamed_cbids:
            OpenMaya.MMessage.removeCallback(mocapx.clipreader_renamed_cbids[node_name])
            del mocapx.clipreader_renamed_cbids[node_name]


# noinspection PyUnusedLocal,PyArgumentList
def adapter_removed_cb(node, clientData=None):
    if not mocapx.suppress_on_scene_loading:
        node_name = OpenMaya.MFnDependencyNode(node).name()
        if node_name in mocapx.adapter_active_change_cbids:
            OpenMaya.MMessage.removeCallback(mocapx.adapter_active_change_cbids[node_name])
            del mocapx.adapter_active_change_cbids[node_name]
        if node_name in mocapx.adapter_renamed_cbids:
            OpenMaya.MMessage.removeCallback(mocapx.adapter_renamed_cbids[node_name])
            del mocapx.adapter_renamed_cbids[node_name]


# noinspection PyUnusedLocal,PyArgumentList
def poseLib_removed_cb(node, clientData=None):
    if not mocapx.suppress_on_scene_loading:
        node_name = OpenMaya.MFnDependencyNode(node).name()
        if node_name in mocapx.poseLib_before_delete_cbids:
            OpenMaya.MMessage.removeCallback(mocapx.poseLib_before_delete_cbids[node_name])
            del mocapx.poseLib_before_delete_cbids[node_name]
        if node_name in mocapx.poseLib_renamed_cbids:
            OpenMaya.MMessage.removeCallback(mocapx.poseLib_renamed_cbids[node_name])
            del mocapx.poseLib_renamed_cbids[node_name]


# noinspection PyUnusedLocal,PyArgumentList
def pose_removed_cb(node, clientData=None):
    if not mocapx.suppress_on_scene_loading:
        node_name = OpenMaya.MFnDependencyNode(node).name()
        if node_name in mocapx.pose_attr_changed_cbids:
            OpenMaya.MMessage.removeCallback(mocapx.pose_attr_changed_cbids[node_name])
            del mocapx.pose_attr_changed_cbids[node_name]


# noinspection PyUnusedLocal,PyArgumentList
def poseApply_removed_cb(node, clientData=None):
    if not mocapx.suppress_on_scene_loading:
        node_name = OpenMaya.MFnDependencyNode(node).name()
        if node_name in mocapx.poseApply_attr_changed_cbids:
            OpenMaya.MMessage.removeCallback(mocapx.poseApply_attr_changed_cbids[node_name])
            del mocapx.poseApply_attr_changed_cbids[node_name]
        if node_name in mocapx.poseApply_before_delete_cbids:
            OpenMaya.MMessage.removeCallback(mocapx.poseApply_before_delete_cbids[node_name])
            del mocapx.poseApply_before_delete_cbids[node_name]
        if node_name in mocapx.poseApply_renamed_cbids:
            OpenMaya.MMessage.removeCallback(mocapx.poseApply_renamed_cbids[node_name])
            del mocapx.poseApply_renamed_cbids[node_name]


# noinspection PyUnusedLocal
def clipreader_onconnect_cb(msg, plug, otherplug, clientData):
    if not mocapx.suppress_on_scene_loading:
        plug_name = str(plug.partialName(includeNodeName=True))
        _, attr_name = plug_name.split('.', 1)
        if msg & OpenMaya.MNodeMessage.kConnectionMade:
            otherplug_node = str(otherplug.partialName(includeNodeName=True)).split('.')[0]
            if otherplug.isDestination and attr_name in mocapx.TRANSFORM_ATTRS:
                if otherplug.isKeyable and otherplug.node().apiTypeStr not in (
                        'kBlendNodeDoubleLinear',
                        'kBlendNodeDoubleAngle',
                        'kUnitConversion',
                        'kPluginObjectSet'):
                    get_anim_blend_node(otherplug, create=True, rewire_to='inputA')


# noinspection PyUnusedLocal
# TODO: change name. Put anim blend insertion into separate function
def adapter_active_source_changed_cb(msg, plug, otherplug, clientData):
    if not mocapx.suppress_on_scene_loading:
        plug_name = str(plug.partialName(includeNodeName=True))
        plug_node, attr_name = plug_name.split('.', 1)
        otherplug_node = str(otherplug.partialName(includeNodeName=True)).split('.')[0]
        if msg & OpenMaya.MNodeMessage.kConnectionMade:
            if attr_name == 'activeSource':
                switch_data_source(otherplug_node, plug_node)

            otherplug_node = str(otherplug.partialName(includeNodeName=True)).split('.')[0]
            if otherplug.isDestination and attr_name in mocapx.TRANSFORM_ATTRS:
                if otherplug.isKeyable and otherplug.node().apiTypeStr not in (
                        'kBlendNodeDoubleLinear',
                        'kBlendNodeDoubleAngle',
                        'kUnitConversion',
                        'kPluginObjectSet'):
                    get_anim_blend_node(otherplug, create=True, rewire_to='inputA')

        elif msg & OpenMaya.MNodeMessage.kConnectionBroken:
            if attr_name == 'activeSource':
                if otherplug_node in (mc.sets(plug_node, q=True) or []):
                    transplant_outs_to_adapter(otherplug_node, plug_node)


# noinspection PyUnusedLocal,PyArgumentList
def poseLib_about_to_delete_cb(node, modifier, clientData=None):
    if not mocapx.suppress_on_scene_loading:
        node_name = OpenMaya.MFnDependencyNode(node).name()
        for pose_node in mc.sets(node_name, q=True) or []:
            to_delete = True
            for each in mc.listConnections(pose_node, s=False, type="MCPXPoselib") or []:
                if each != node_name:
                    to_delete = False
                    break
            if to_delete:
                mc.delete(pose_node)


def pose_attr_changed_cb(msg, plug, otherplug, clientData):
    if not mocapx.suppress_on_scene_loading:
        plug_name = str(plug.partialName(includeNodeName=True))
        node_name, attr_name = plug_name.split('.', 1)
        if msg & OpenMaya.MNodeMessage.kAttributeSet:
            if attr_name == "mute":
                if mocapx.poselib_editor:
                    mocapx.poselib_editor.widget.refresh_buttons_state()


def poseApply_attr_changed_cb(msg, plug, otherplug, clientData):
    if not mocapx.suppress_on_scene_loading:
        plug_name = str(plug.partialName(includeNodeName=True))
        node_name, attr_name = plug_name.split('.', 1)
        if msg & OpenMaya.MNodeMessage.kConnectionBroken:
            if attr_name == "values":
                if not mc.listConnections(plug_name, d=False, scn=True, type="MCPXPose"):
                    if mc.lockNode(node_name, q=True)[0]:
                        mc.lockNode(node_name, l=False)
                    # to prevent maya freezing before new scene opened
                    command = "if (`objExists " + node_name + "`) delete " + node_name + ";"
                    mel.eval("evalDeferred \"{}\"".format(command))


# noinspection PyUnusedLocal,PyArgumentList
def poseApply_about_to_delete_cb(node, modifier, clientData=None):
    if not mocapx.suppress_on_scene_loading:
        node_name = OpenMaya.MFnDependencyNode(node).name()
        rest_value = mc.getAttr("{}.rest".format(node_name))
        anim_blend_nodes = mc.listConnections(
            "{}.output".format(node_name), s=False, scn=True, type="animBlendNodeBase")
        if anim_blend_nodes:
            for anim_blend_node in anim_blend_nodes:
                anim_blend_input = "{}.inputB".format(anim_blend_node)
                in_connection = mc.connectionInfo(anim_blend_input, sfd=True)
                if in_connection:
                    mc.disconnectAttr(in_connection, anim_blend_input)
                    for out_connection in mc.listConnections(
                            "{}.output".format(anim_blend_node), s=False, p=True) or []:
                        if not mc.isConnected(in_connection, out_connection):
                            mc.connectAttr(in_connection, out_connection, f=True)

                    if rest_value:
                        in_node = in_connection.split(".")[0]
                        # if incoming animation - shift curve keys back
                        if mc.objectType(in_node, isa="animCurve"):
                            if not mc.referenceQuery(in_node, inr=True):
                                mc.keyframe(in_node, relative=True, valueChange=rest_value)
                            else:
                                shift_referenced_anim_curve(in_node, rest_value)
                        # for some rare case: if our addDoubleLinear used - try to reconnect or reset shift
                        elif mc.objectType(in_node, isa="addDoubleLinear"):
                            add_node_input1 = "{}.input1".format(in_node)
                            if mc.listConnections(add_node_input1, d=False, scn=True,
                                                  type="animCurve"):
                                add_node_input2 = "{}.input2".format(in_node)
                                if mc.getAttr(add_node_input2) == -1 * rest_value:
                                    if not mc.referenceQuery(in_node, inr=True):
                                        source = mc.connectionInfo(add_node_input1, sfd=True)
                                        mc.disconnectAttr(source, add_node_input1)
                                        for out_connection in mc.listConnections(
                                                "{}.output".format(in_node), s=False, p=True) or []:
                                            if not mc.isConnected(source, out_connection):
                                                mc.connectAttr(source, out_connection, f=True)
                                        if mc.lockNode(in_node, q=True)[0]:
                                            mc.lockNode(in_node, l=False)
                                        mc.delete(in_node)
                                    else:
                                        if not mc.getAttr(add_node_input2, l=True):
                                            mc.setAttr(add_node_input2, 0)

                if mc.lockNode(anim_blend_node, q=True)[0]:
                    mc.lockNode(anim_blend_node, l=False)
                mc.delete(anim_blend_node)
