import mocapx
import mocapx.commands as mcpx_cmds
from mocapx.ui.about_dialog import AboutDialog
from mocapx.ui.poselib_editor import create_poselib_editor
from mocapx.ui.pose_board import create_pose_board
from mocapx.lib.utils import get_mobject, adapt_name, import_scene
from mocapx.lib.nodes import get_selected_attrs, select_node, get_adapter_by_source

import maya.cmds as mc
import maya.api.OpenMaya as OpenMaya


def _null():
    pass


class SimpleButton(object):
    def __init__(self, shelf, command=_null, icon="commandButton.png", annotation_text=""):
        self.shelf_button = mc.shelfButton(
            parent=shelf,
            width=32,
            height=32,
            image=icon,
            command=command,
            annotation=annotation_text
        )
        self._callback = _null

    def set_command(self, command):
        mc.shelfButton(self.shelf_button, edit=True, command=command)


# noinspection SpellCheckingInspection
class DynamicButton(SimpleButton):
    LMB = 1
    MMB = 2

    def __init__(self, shelf, command=_null, icon="commandButton.png", annotation_text=""):
        super(DynamicButton, self).__init__(shelf=shelf, command=command, icon=icon, annotation_text=annotation_text)
        self.node_add_cbid = None
        self.node_remove_cbid = None
        self.rename_callbacks = dict()
        self._popups = {}
        self._callback = _null
        self._nodes_type = None

    # MENU
    def delete_menu(self, button):
        old = self._popups.get(button, None)
        if old:
            mc.deleteUI(old)
            del self._popups[button]

    def create_menu(self, button, payload):
        if button not in (DynamicButton.LMB, DynamicButton.MMB):
            raise ValueError('Cannot create menu for button {}'.format(button))
        self.delete_menu(button)
        menu = mc.popupMenu(parent=self.shelf_button, button=button)
        for label, command in payload:
            mc.menuItem(p=menu, label=label, c=command)
        self._popups[button] = menu

    def update_menus(self, nodes=None):
        if nodes is None:
            nodes = list(map(adapt_name, mc.ls(type=self._nodes_type)))
        if not nodes:
            self.set_command(self.get_callback())
            self.delete_menu(DynamicButton.LMB)
        elif len(nodes) == 1:
            self.set_command(self.get_callback(nodes[0]))
            self.delete_menu(DynamicButton.LMB)
        else:
            self.set_command(_null)
            payload = [("Add to {}".format(node), self.get_callback(node))
                       for node in nodes]
            self.create_menu(DynamicButton.LMB, payload)

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
        return DynamicButton.bound_callback(self._callback, node_name)

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
class EditorButton(SimpleButton):
    @staticmethod
    def action_handler():
        create_poselib_editor()

    def __init__(self, shelf):
        super(EditorButton, self).__init__(
            shelf=shelf,
            command=EditorButton.action_handler,
            icon="MCPXEditor.png",
            annotation_text="Show MocapX Poselib Editor"
        )


# noinspection SpellCheckingInspection
class PoseBoardButton(SimpleButton):
    # noinspection PyUnusedLocal
    @staticmethod
    def action_handler(*args, **kwargs):
        create_pose_board()

    def __init__(self, shelf):
        super(PoseBoardButton, self).__init__(
            shelf=shelf,
            command=PoseBoardButton.action_handler,
            icon="MCPXPoseBoard.png",
            annotation_text="Show MocapX Pose Board"
        )


# noinspection SpellCheckingInspection
class AttrCollButton(DynamicButton):
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

    def __init__(self, shelf):
        super(AttrCollButton, self).__init__(
            shelf=shelf,
            command=_null,
            icon="MCPXCreateCollection.png",
            annotation_text="Create MocapX Attribute Collection",
        )
        self._callback = AttrCollButton.action_handler
        self._nodes_type = 'MCPXAttributeCollection'

        self.create_menu(DynamicButton.MMB, [("Create new Attribute Collection", self.get_callback())])

        self.update_menus()
        self.add_callbacks()


# noinspection SpellCheckingInspection
class PoseButton(DynamicButton):
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

    def __init__(self, shelf):
        super(PoseButton, self).__init__(
            shelf=shelf,
            command=_null,
            icon="MCPXCreatePose.png",
            annotation_text="Create MocapX Pose")
        self._callback = PoseButton.action_handler
        self._nodes_type = 'MCPXPoselib'

        self.update_menus()
        self.add_callbacks()


# noinspection SpellCheckingInspection
class RealtimeDeviceButton(SimpleButton):
    @staticmethod
    def action_handler():
        selection = mc.ls(sl=True)
        if selection:
            if mc.objectType(selection[0]) == 'MCPXAdapter':
                adapter = selection[0]
            else:
                adapter = get_adapter_by_source(selection[0])
        else:
            adapter = None
        node = mcpx_cmds.create_realtime_device(adapter_name=adapter)
        select_node(node)

    def __init__(self, shelf):
        super(RealtimeDeviceButton, self).__init__(
            shelf=shelf,
            command=RealtimeDeviceButton.action_handler,
            icon="MCPXRealTimeDeviceCreate.png",
            annotation_text="Create MocapX RealTime Device",
        )


# noinspection SpellCheckingInspection
class ClipreaderButton(SimpleButton):
    @staticmethod
    def action_handler():
        selection = mc.ls(sl=True)
        if selection:
            if mc.objectType(selection[0]) == 'MCPXAdapter':
                adapter = selection[0]
            else:
                adapter = get_adapter_by_source(selection[0])
        else:
            adapter = None
        node = mcpx_cmds.create_clipreader(adapter_name=adapter)
        select_node(node)

    def __init__(self, shelf):
        super(ClipreaderButton, self).__init__(
            shelf=shelf,
            command=ClipreaderButton.action_handler,
            icon="MCPXClipReaderCreate.png",
            annotation_text="Create MocapX ClipReader",
        )


class BakeButton(SimpleButton):
    @staticmethod
    def action_handler():
        mcpx_cmds.bake_channels()

    def __init__(self, shelf):
        super(BakeButton, self).__init__(
            shelf=shelf,
            command=BakeButton.action_handler,
            icon='MCPXBake.png',
            annotation_text="Bake selected Channels"
        )


# noinspection SpellCheckingInspection
class HeadCreate(SimpleButton):
    @staticmethod
    def action_handler():
        import_scene(r'$MOCAPX_EXAMPLES/head_scene.ma', namespace='Natalie')

    def __init__(self, shelf):
        super(HeadCreate, self).__init__(
            shelf=shelf,
            command=HeadCreate.action_handler,
            icon="MCPXHeadCreate.png",
            annotation_text="Get Natalie Head"
        )


# noinspection SpellCheckingInspection
class AboutButton(SimpleButton):
    @staticmethod
    def action_handler():
        wgt = AboutDialog()
        wgt.show()

    def __init__(self, shelf):
        super(AboutButton, self).__init__(
            shelf=shelf,
            command=AboutButton.action_handler,
            icon="MCPXInfo.png",
            annotation_text="About MocapX",
        )


# noinspection SpellCheckingInspection
class MocapxShelf(object):
    def __init__(self):
        # clear old misspelling shelf
        name = "Mocapx"
        if mc.shelfLayout(name, ex=True):
            # noinspection PyUnresolvedReferences
            import maya.mel as mel
            mel.eval("source \"MCPXutils.mel\"; MCPXDeleteShelfTab(\"{}\")".format(name))

        self.shelf_name = "MocapX"
        # shelf
        if mc.shelfLayout(self.shelf_name, ex=True):
            for each in mc.shelfLayout(self.shelf_name, q=True, ca=True) or []:
                mc.deleteUI(each)
        else:
            mc.shelfLayout(self.shelf_name, p="ShelfLayout")

        # buttons
        self.buttons = (
            EditorButton(self.shelf_name),
            PoseBoardButton(self.shelf_name),
            AttrCollButton(self.shelf_name),
            PoseButton(self.shelf_name),
            RealtimeDeviceButton(self.shelf_name),
            ClipreaderButton(self.shelf_name),
            BakeButton(self.shelf_name),
            HeadCreate(self.shelf_name),
            AboutButton(self.shelf_name)
        )


def create_shelf():
    return MocapxShelf()
