from maya.api import OpenMaya
from maya.api import OpenMayaAnim
# pylint: enable=no-name-in-module
# noinspection PyUnresolvedReferences
import mocapx
from mocapx.vendor.Qt import QtWidgets, QtCore
from mocapx.ui.widgets import Liner
from mocapx.ui.plug_edit_field import PlugEditField
from mocapx.lib import nodes
from mocapx.lib.utils import get_mobject
from mocapx.lib.uiutils import scaled, is_widget_really_visible


# noinspection SpellCheckingInspection
class DataSourceAttrPane(QtWidgets.QScrollArea):
    def __init__(self, source_node, parent=None):
        super(DataSourceAttrPane, self).__init__(parent)

        self.node = source_node
        self.widgets = list()

        if nodes.realtime_device_node(self.node):
            self.rd_connection_status = nodes.get_realtime_device_conn_status(self.node)
        else:
            self.rd_connection_status = None

        self.attr_changed_cbid = None
        self.anim_changed_cbid = None
        self.rd_connection_changed_cbid = None
        self.cr_time_change_cbid = None

        self.setWidgetResizable(True)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setFrameShadow(QtWidgets.QFrame.Plain)

        inner = QtWidgets.QFrame(self)
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(scaled(0), scaled(0), scaled(0), scaled(0))
        self.layout.setSpacing(scaled(3))
        inner.setLayout(self.layout)
        # Set main widget
        self.setWidget(inner)

        self.setFixedHeight(scaled(400))

        self.refresh_state()

    def refresh_state(self):
        self.clean_callbacks()
        self.set_callbacks()
        self.update_view(refresh_list=True, force=True)

    def update_view(self, refresh_list=True, force=False):
        if not (is_widget_really_visible(self) or force):
            return
        if not refresh_list:
            if not nodes.node_exists(self.node):
                return
        else:
            # clear all
            while True:
                item = self.layout.takeAt(0)
                if not item:
                    break
                widget = item.widget()
                if widget:
                    self.layout.removeWidget(widget)
                    widget.deleteLater()
                del item
            self.widgets = list()

            # update attributes list
            if nodes.node_exists(self.node):
                attr_list = sorted(nodes.list_attrs(self.node, only_valid=True, userDefined=True))
            else:
                return

            # create new widgets
            for attr in attr_list:
                if attr.endswith('_mlt'):
                    continue
                mult_attr = '{}_mlt'.format(attr)
                if mult_attr not in attr_list:
                    mult_attr = None
                widget = AttrWidget(self.node, attr, mult_attr, self)
                self.layout.addWidget(widget)
                self.widgets.append(widget)
            self.layout.addStretch()

        # update values
        node_mobject = get_mobject(self.node)
        if node_mobject:
            d_node = OpenMaya.MFnDependencyNode(node_mobject)
            for widget in self.widgets:
                if widget.mult:
                    widget.set_multiplier(d_node.findPlug(widget.mult, False).asDouble())
                widget.set_value(d_node.findPlug(widget.attr, False).asDouble())

    # callbacks
    # noinspection PyUnusedLocal
    def status_changed_cb(self, data):
        status = nodes.get_realtime_device_conn_status(self.node)
        if status != self.rd_connection_status:
            self.rd_connection_status = status
            self.refresh_state()

    # noinspection PyPep8Naming, PyUnusedLocal
    def attr_changed_cb(self, msg, plug, otherplug, clientData):
        if not mocapx.suppress_on_attr_refresh:
            attr_name = plug.partialName(includeNodeName=False)
            if attr_name in ("refreshNode", "refresh", "clipFrameOffset") or (
                    plug.isChild and plug.parent().partialName() == "multipliers"):
                self.update_view(refresh_list=False)
            else:
                if msg & OpenMaya.MNodeMessage.kAttributeAdded or \
                        msg & OpenMaya.MNodeMessage.kAttributeRemoved:
                    self.update_view(refresh_list=True)

    # noinspection PyPep8Naming, PyUnusedLocal
    def anim_changed_cb(self, editedCurves, clientData):
        self.update_view(refresh_list=False)
        # toDo: Failure: MFnDependencyNode object doesn't exists when try to access its methods
        # for m_object in editedCurves:
        #     d_node = OpenMaya.MFnDependencyNode(m_object)
        #     print('>>>', d_node)
        #     print('>>>', d_node.absoluteName())
        #     connections = nodes.list_connections(d_node.absoluteName(), s=False, type='MCPXClipReader')
        #     if connections and connections[0] == self.node:
        #         self.update_view(refresh_list=False)
        #         return

    # noinspection PyUnusedLocal
    def time_changed_cb(self, *args, **kwargs):
        self.update_view(refresh_list=False)

    def clean_callbacks(self):
        if self.rd_connection_changed_cbid:
            OpenMaya.MMessage.removeCallback(self.rd_connection_changed_cbid)
            self.rd_connection_changed_cbid = None
        if self.attr_changed_cbid:
            OpenMaya.MMessage.removeCallback(self.attr_changed_cbid)
            self.attr_changed_cbid = None
        if self.anim_changed_cbid:
            OpenMayaAnim.MAnimMessage.removeCallback(self.anim_changed_cbid)
            self.anim_changed_cbid = None
        if self.cr_time_change_cbid:
            OpenMaya.MMessage.removeCallback(self.cr_time_change_cbid)
            self.cr_time_change_cbid = None

    def set_callbacks(self):
        node_mobject = get_mobject(self.node)

        if node_mobject:
            self.attr_changed_cbid = OpenMaya.MNodeMessage.addAttributeChangedCallback(
                node_mobject, self.attr_changed_cb)

        self.anim_changed_cbid = OpenMayaAnim.MAnimMessage.addAnimKeyframeEditedCallback(
            self.anim_changed_cb)

        if nodes.realtime_device_node(self.node):
            self.rd_connection_changed_cbid = OpenMaya.MUserEventMessage.addUserEventCallback(
                'MCPXRltDvceConnStatusChanged', self.status_changed_cb)
        self.cr_time_change_cbid = OpenMaya.MDGMessage.addForceUpdateCallback(self.time_changed_cb)


# noinspection SpellCheckingInspection
class AttrWidget(QtWidgets.QFrame):
    def __init__(self, node, value_attr, mult_attr, parent=None):
        super(AttrWidget, self).__init__(parent)

        self.node = node
        self.attr = value_attr
        self.mult = mult_attr
        self.multiplier = PlugEditField(
            plug='{}.{}'.format(self.node, self.mult) if self.mult else None,
            select_all_by_DoubleClick=True,
            parent=self
        )
        self.multiplier.set_preview_precision(2)
        self.multiplier.setFixedSize(scaled(36), scaled(18))
        if self.mult is None:
            self.multiplier.setEnabled(False)
        self.liner = Liner(label=self.attr, preview_precision=3)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(scaled(3), scaled(0), scaled(0), scaled(0))
        layout.setSpacing(scaled(1))
        layout.addWidget(self.multiplier)
        layout.addWidget(self.liner)

        self.setFixedHeight(scaled(18))

        # set handlers
        self.liner.valueChanged.connect(self.set_value_handle)

    def set_multiplier(self, value):
        self.multiplier.setValue(value)

    def set_value(self, value):
        self.liner.setValue(value)

    # noinspection PyUnusedLocal
    def set_value_handle(self, widget, value):
        self.liner.blockSignals(True)
        nodes.set_attr_value(self.node + "." + self.attr, value=value, force=False, verbose=False)
        self.liner.blockSignals(False)
