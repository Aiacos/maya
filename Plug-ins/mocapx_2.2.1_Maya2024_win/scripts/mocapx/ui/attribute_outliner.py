import mocapx
from mocapx.lib.nodes import scene_selection, connect_attrs, connected_attrs, disconnect_attrs, setOptionVarValue
from mocapx.lib.utils import is_attr_type_valid
from mocapx.lib import uiutils

# noinspection SpellCheckingInspection
OPTION_NAME = "AttributeOutlinerHolderState"


# noinspection SpellCheckingInspection,PyPep8Naming
class AttributeOutlinerHolder(object):
    # noinspection PyUnusedLocal
    @staticmethod
    def node_change_handler(clientData):
        sel = scene_selection()
        if sel:
            node = sel[-1]
            mocapx.attr_outliner.set_attached_node(node)

    @staticmethod
    def click_handler():
        source = mocapx.attr_outliner.selection()
        if is_attr_type_valid(source):
            dest = mocapx.attr_outliner.plug
            if connected_attrs(source, dest):
                disconnect_attrs(source, dest, verbose=True)
            else:
                connect_attrs(source, dest, verbose=True)
        # Update pane by setting same attached plug again
        mocapx.attr_outliner.set_attached_plug(mocapx.attr_outliner.plug)

    @staticmethod
    def close_palette():
        if mocapx.attr_outliner.sel_watcher_cbid:
            uiutils.remove_cb(mocapx.attr_outliner.sel_watcher_cbid)

        setOptionVarValue(OPTION_NAME, uiutils.save_window_state(mocapx.attr_outliner.pane))

    @staticmethod
    def display_pane(attached_plug):
        if mocapx.attr_outliner:
            # If outliner attribute holder exists window is shown or was closed
            if not uiutils.window_exists(mocapx.attr_outliner.pane):
                # If window was closed create outliner and use last element in selection as node
                mocapx.attr_outliner.create_pane()

                sel = scene_selection()
                if sel:
                    mocapx.attr_outliner.set_attached_node(sel[-1])
            # Just change attached plug
            mocapx.attr_outliner.set_attached_plug(attached_plug)
        else:
            # First lunch.
            # Get last selection and set as node
            sel = scene_selection()
            if sel:
                node = sel[-1]
            else:
                node = None
            # Creating holder attache to plug and node
            mocapx.attr_outliner = AttributeOutlinerHolder(attached_plug, node)
        mocapx.attr_outliner.show()

    def __init__(self, attached_plug, attached_node=None):
        self.outliner = None
        self.pane = None
        self.sel_watcher_cbid = None
        self.plug = attached_plug
        self.create_pane()
        if attached_node:
            self.node = attached_node
            self.set_attached_node(self.node)
        else:
            self.node = None
        self.set_attached_plug(attached_plug)
        uiutils.set_window_title(self.pane, self.title)

    @property
    def title(self):
        if self.node:
            return '{} <- {}'.format(self.plug, self.selection())
        else:
            return '{}'.format(self.plug)

    def create_pane(self):
        self.pane, self.outliner = uiutils.create_attr_outliner(
            select_command='python("'
                           'from mocapx.ui.attribute_outliner import AttributeOutlinerHolder;'
                           'AttributeOutlinerHolder.click_handler()'
                           '")',
            close_command=AttributeOutlinerHolder.close_palette,
            state_option=OPTION_NAME)

        self.sel_watcher_cbid = uiutils.create_sel_changed_cb(AttributeOutlinerHolder.node_change_handler)

    def set_attached_plug(self, plug):
        uiutils.set_connected_plug(self.outliner, plug)
        self.plug = plug
        uiutils.set_window_title(self.pane, self.title)

    def set_attached_node(self, node):
        uiutils.set_connected_node(self.outliner, node)
        self.node = node
        uiutils.set_window_title(self.pane, self.title)

    def selection(self):
        return uiutils.selection(self.outliner)

    def show(self):
        uiutils.show(self.pane)
