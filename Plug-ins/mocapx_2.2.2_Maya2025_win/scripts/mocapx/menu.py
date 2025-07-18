import mocapx
import mocapx.commands as mcpx_cmds
from mocapx.ui.about_dialog import AboutDialog
from mocapx.ui.poselib_editor import create_poselib_editor
from mocapx.ui.pose_board import create_pose_board
from mocapx.lib.utils import get_mobject, adapt_name, import_scene
from mocapx.lib.nodes import get_selected_attrs, select_node, get_adapter_node, get_adapter_by_source, \
    get_all_active_data_sources, \
    get_realtime_device_live, set_realtime_device_live, get_realtime_device_conn_status

import maya.cmds as mc
import maya.api.OpenMaya as OpenMaya


def _null():
    pass


def _sep(menu, label=""):
    return mc.menuItem(parent=menu, divider=True, label=label)


class SimpleItem(object):
    def __init__(self, menu, label, command, icon="", annotation_text=""):
        self.menu_button = mc.menuItem(
            parent=menu,
            label=label,
            image=icon,
            command=command,
            annotation=annotation_text,
        )


# noinspection SpellCheckingInspection
class DynamicItem(object):
    def __init__(self, menu, callback, nodes_type, menu_label, menu_icon="", menu_annotation_text="",
                 item_label="", item_icon="", item_annotation_text="", tear_off=True):
        self._callback = callback
        self._menu_button_subs = list()
        self._nodes_type = nodes_type
        self.node_add_cbid = None
        self.node_remove_cbid = None
        self.rename_callbacks = dict()

        self.menu_button = mc.menuItem(
            subMenu=True,
            parent=menu,
            label=menu_label,
            image=menu_icon,
            annotation=menu_annotation_text,
            tearOff=tear_off
        )
        self._constant_item = SimpleItem(
            menu=self.menu_button,
            label=item_label,
            icon=item_icon,
            command=self.get_callback(),
            annotation_text=item_annotation_text
        )
        self.update_menus()
        self.add_callbacks()

    # MENU
    def update_menus(self, nodes=None):
        for old in self._menu_button_subs:
            mc.deleteUI(old)
            self._menu_button_subs = list()

        if nodes is None:
            nodes = list(map(adapt_name, mc.ls(type=self._nodes_type)))

        if nodes:
            self._menu_button_subs.append(_sep(self.menu_button))

            for node in nodes:
                label = "Add to {}".format(node)
                command = self.get_callback(node)
                icon = ""
                annotation_text = ""

                item = SimpleItem(
                    menu=self.menu_button,
                    label=label,
                    icon=icon,
                    command=command,
                    annotation_text=annotation_text
                )
                self._menu_button_subs.append(item.menu_button)

    # CALLBACKS
    @staticmethod
    def bound_callback(callback, node_name=None):
        bound_name = node_name

        # noinspection PyUnusedLocal
        def bound(*args, **kwargs):
            callback(bound_name)

        # noinspection PyUnusedLocal
        def unbound(*args, **kwargs):
            callback()

        if bound_name:
            return bound
        else:
            return unbound

    def get_callback(self, node_name=None):
        return DynamicItem.bound_callback(self._callback, node_name)

    # noinspection PyPep8Naming,PyUnusedLocal
    def node_add_cb(self, node, clientData=None):
        if not mocapx.suppress_on_scene_loading:
            node_name = OpenMaya.MFnDependencyNode(node).name()

            cd_id = OpenMaya.MNodeMessage.addNameChangedCallback(
                node, self.node_rename_cb)
            self.rename_callbacks[node_name] = cd_id
            self.update_menus()

    # noinspection PyPep8Naming,PyUnusedLocal
    def node_remove_cb(self, node, clientData=None):
        if not mocapx.suppress_on_scene_loading:
            node_list = mc.ls(type=self._nodes_type)
            node_name = OpenMaya.MFnDependencyNode(node).name()

            cb_id = self.rename_callbacks[node_name]
            OpenMaya.MMessage.removeCallback(cb_id)
            del self.rename_callbacks[node_name]
            node_list.remove(node_name)
            self.update_menus(node_list)

    # noinspection PyPep8Naming,PyUnusedLocal
    def node_rename_cb(self, node, prevName, clientData=None):
        if not mocapx.suppress_on_scene_loading:
            new_name = OpenMaya.MFnDependencyNode(node).name()
            new_name = adapt_name(new_name)
            self.rename_callbacks[new_name] = self.rename_callbacks.pop(prevName)
            self.update_menus()

    def add_callbacks(self):
        node_list = mc.ls(type=self._nodes_type)
        for node_name in node_list:
            node_mobject = get_mobject(node_name)
            if node_mobject:
                cd_id = OpenMaya.MNodeMessage.addNameChangedCallback(
                    node_mobject, self.node_rename_cb)
                self.rename_callbacks[node_name] = cd_id

        self.node_add_cbid = OpenMaya.MDGMessage.addNodeAddedCallback(
            self.node_add_cb, self._nodes_type)

        self.node_remove_cbid = OpenMaya.MDGMessage.addNodeRemovedCallback(
            self.node_remove_cb, self._nodes_type)

    def refresh_callbacks(self):
        if self.rename_callbacks:
            for cb_id in list(self.rename_callbacks.values()):
                OpenMaya.MMessage.removeCallback(cb_id)
            self.rename_callbacks = dict()
        if self.node_add_cbid:
            OpenMaya.MMessage.removeCallback(self.node_add_cbid)
            self.node_add_cbid = None
        if self.node_remove_cbid:
            OpenMaya.MMessage.removeCallback(self.node_remove_cbid)
            self.node_remove_cbid = None

        self.update_menus()
        self.add_callbacks()


# noinspection SpellCheckingInspection
class MenuEditor(SimpleItem):
    # noinspection PyUnusedLocal
    @staticmethod
    def action_handler(*args, **kwargs):
        create_poselib_editor()

    def __init__(self, menu):
        super(MenuEditor, self).__init__(
            menu=menu,
            command=MenuEditor.action_handler,
            label="Show Poselib Editor",
            icon="MCPXEditor.png",
            annotation_text="Show MocapX Poselib Editor"
        )


# noinspection SpellCheckingInspection
class MenuBoard(SimpleItem):
    # noinspection PyUnusedLocal
    @staticmethod
    def action_handler(*args, **kwargs):
        create_pose_board()

    def __init__(self, menu):
        super(MenuBoard, self).__init__(
            menu=menu,
            command=MenuBoard.action_handler,
            label="Show Pose Board",
            icon="MCPXPoseBoard.png",
            annotation_text="Show MocapX Pose Board"
        )


# noinspection SpellCheckingInspection
class MenuAttrColl(DynamicItem):
    @staticmethod
    def action_handler(collection=None):
        selection = mc.ls(sl=True)
        if not collection:
            collection = mcpx_cmds.create_empty_collection()
            mc.select(selection, r=True)

        if selection:
            selected_attrs = get_selected_attrs()
            if selected_attrs:
                mcpx_cmds.add_plugs_to_collection(
                    collection, selected_plugs=True)
            else:
                mcpx_cmds.add_controls_to_collection(
                    collection, selected_controls=True)

    def __init__(self, menu):
        super(MenuAttrColl, self).__init__(
            menu=menu,
            callback=MenuAttrColl.action_handler,
            nodes_type='MCPXAttributeCollection',
            menu_label="Attribute Collection",
            menu_icon="MCPXCreateCollection.png",
            item_label="Create new Attribute Collection",
            item_icon="MCPXCreateCollection.png",
            item_annotation_text="Create MocapX Attribute Collection"
        )


# noinspection SpellCheckingInspection
class MenuPoselib(SimpleItem):
    # noinspection PyUnusedLocal
    @staticmethod
    def action_handler(*args, **kwargs):
        selection = mc.ls(sl=True)
        poselib = mcpx_cmds.create_empty_poselib()
        mc.select(selection, r=True)
        if selection:
            mcpx_cmds.add_pose_to_poselib(poselib, selected_poses=True)

    def __init__(self, menu):
        super(MenuPoselib, self).__init__(
            menu=menu,
            command=MenuPoselib.action_handler,
            label="Create new Poselib",
            icon="MCPXPoselib.png",
            annotation_text="Create MocapX Poselib"
        )


# noinspection SpellCheckingInspection
class MenuPose(DynamicItem):
    @staticmethod
    def action_handler(poselib=None):
        selection = mc.ls(sl=True)
        if selection:
            pose = mcpx_cmds.create_empty_pose(pose_name=None)
            mc.select(selection, r=True)
            selected_attrs = get_selected_attrs()
            if selected_attrs:
                # add plugs to empty pose
                mcpx_cmds.update_plugs_in_pose(pose, selected_plugs=True)
            else:
                # add controls to empty pose
                mcpx_cmds.update_controls_in_pose(pose, selected_controls=True)
            mcpx_cmds.add_pose_to_poselib(poselib, [pose])

    def __init__(self, menu):
        super(MenuPose, self).__init__(
            menu=menu,
            callback=MenuPose.action_handler,
            nodes_type='MCPXPoselib',
            menu_label="Pose",
            menu_icon="MCPXCreatePose.png",
            item_label="Create new Pose",
            item_icon="MCPXCreatePose.png",
            item_annotation_text="Create new MocapX Pose"
        )


# noinspection SpellCheckingInspection
class MenuAdapter(SimpleItem):
    # noinspection PyUnusedLocal
    @staticmethod
    def action_handler(*args, **kwargs):
        get_adapter_node(create_node=True)

    def __init__(self, menu):
        super(MenuAdapter, self).__init__(
            menu=menu,
            command=MenuAdapter.action_handler,
            label="Create new Adapter",
            annotation_text="Create MocapX Adapter"
        )


# noinspection SpellCheckingInspection
class MenuRealtimeDevice(DynamicItem):
    @staticmethod
    def action_handler(adapter=None):
        if not adapter:
            selection = mc.ls(sl=True)
            if selection:
                if mc.objectType(selection[0]) == 'MCPXAdapter':
                    adapter = selection[0]
                else:
                    adapter = get_adapter_by_source(selection[0])
        node = mcpx_cmds.create_realtime_device(adapter_name=adapter)
        select_node(node)

    def __init__(self, menu):
        super(MenuRealtimeDevice, self).__init__(
            menu=menu,
            callback=MenuRealtimeDevice.action_handler,
            nodes_type='MCPXAdapter',
            menu_label="RealTime Device",
            menu_icon="MCPXRealTimeDeviceCreate.png",
            item_label="Create new RealTime Device",
            item_icon="MCPXRealTimeDeviceCreate.png",
            item_annotation_text="Create MocapX RealTime Device"
        )


# noinspection SpellCheckingInspection
class MenuClipReader(DynamicItem):
    @staticmethod
    def action_handler(adapter=None):
        if not adapter:
            selection = mc.ls(sl=True)
            if selection:
                if mc.objectType(selection[0]) == 'MCPXAdapter':
                    adapter = selection[0]
                else:
                    adapter = get_adapter_by_source(selection[0])
        node = mcpx_cmds.create_clipreader(adapter_name=adapter)
        select_node(node)

    def __init__(self, menu):
        super(MenuClipReader, self).__init__(
            menu=menu,
            callback=MenuClipReader.action_handler,
            nodes_type='MCPXAdapter',
            menu_label="ClipReader",
            menu_icon="MCPXClipReaderCreate.png",
            item_label="Create new ClipReader",
            item_icon="MCPXClipReaderCreate.png",
            item_annotation_text="Create MocapX ClipReader"
        )


# noinspection SpellCheckingInspection
class MenuPlayAll(SimpleItem):
    # noinspection PyUnusedLocal
    @staticmethod
    def action_handler(*args, **kwargs):
        for device in get_all_active_data_sources("MCPXRealTimeDevice"):
            if get_realtime_device_conn_status(device) in (2, 3) and not get_realtime_device_live(device):
                set_realtime_device_live(device, True)

    def __init__(self, menu):
        super(MenuPlayAll, self).__init__(
            menu=menu,
            command=MenuPlayAll.action_handler,
            label="Play all active RealTime Devices",
            icon="MCPXPlayAll.png",
            annotation_text="Play all active MocapX Realtime Devices"
        )


# noinspection SpellCheckingInspection
class MenuPauseAll(SimpleItem):
    # noinspection PyUnusedLocal
    @staticmethod
    def action_handler(*args, **kwargs):
        for device in get_all_active_data_sources("MCPXRealTimeDevice"):
            if get_realtime_device_conn_status(device) in (2, 3) and get_realtime_device_live(device):
                set_realtime_device_live(device, False)

    def __init__(self, menu):
        super(MenuPauseAll, self).__init__(
            menu=menu,
            command=MenuPauseAll.action_handler,
            label="Pause all running Realtime Devices",
            icon="MCPXPauseAll.png",
            annotation_text="Pause all running MocapX Realtime Devices"
        )


class MenuBake(SimpleItem):
    # noinspection PyUnusedLocal
    @staticmethod
    def action_handler(*args, **kwargs):
        mcpx_cmds.bake_channels()

    def __init__(self, menu):
        super(MenuBake, self).__init__(
            menu=menu,
            command=MenuBake.action_handler,
            label="Bake Channels",
            icon="MCPXBake.png",
            annotation_text="Bake selected Channels"
        )


# noinspection SpellCheckingInspection
class MenuHead(SimpleItem):
    # noinspection PyUnusedLocal
    @staticmethod
    def action_handler(*args, **kwargs):
        import_scene(r'$MOCAPX_EXAMPLES/head_scene.ma', namespace='Natalie')

    def __init__(self, menu):
        super(MenuHead, self).__init__(
            menu=menu,
            command=MenuHead.action_handler,
            label="Get Natalie Head",
            icon="MCPXHeadCreate.png",
            annotation_text="Get Natalie Head"
        )


# noinspection SpellCheckingInspection
class MenuAbout(SimpleItem):
    # noinspection PyUnusedLocal
    @staticmethod
    def action_handler(*args, **kwargs):
        wgt = AboutDialog()
        wgt.show()

    def __init__(self, menu):
        super(MenuAbout, self).__init__(
            menu=menu,
            command=MenuAbout.action_handler,
            label="About MocapX",
            icon="MCPXInfo.png",
            annotation_text="About MocapX"
        )


# noinspection SpellCheckingInspection
class MocapxMenu(object):
    def __init__(self):
        self.menu_name = "Mocapx_Menu"
        # menu
        if mc.menu(self.menu_name, q=True, exists=True):
            mc.menu(self.menu_name, e=True, deleteAllItems=True)
        else:
            mc.menu(self.menu_name, label="MocapX", parent="MayaWindow", tearOff=True)

        # buttons
        self.buttons = (
            _sep(self.menu_name, "Poses"),
            MenuEditor(self.menu_name),
            MenuBoard(self.menu_name),
            _sep(self.menu_name),
            MenuAttrColl(self.menu_name),
            MenuPoselib(self.menu_name),
            MenuPose(self.menu_name),
            _sep(self.menu_name, "Data Sources"),
            MenuAdapter(self.menu_name),
            MenuRealtimeDevice(self.menu_name),
            MenuClipReader(self.menu_name),
            MenuPlayAll(self.menu_name),
            MenuPauseAll(self.menu_name),
            _sep(self.menu_name, "Tools"),
            MenuBake(self.menu_name),
            MenuHead(self.menu_name),
            _sep(self.menu_name),
            MenuAbout(self.menu_name)
        )


def create_menu():
    return MocapxMenu()
