import maya.api.OpenMaya as OpenMaya
import maya.cmds as mc

import mocapx
from mocapx.lib.utils import adapt_name, get_mobject, get_parent_plug


class ControlWatcher(object):
    def __init__(self, ctrl):
        self.node = ctrl.split('.')[0]
        self.renamed_cbid = None
        self.rename_callbacs = list()
        self.attr_changed_cbid = None
        self.attrs_clean = dict()
        self.attrs_dirty = dict()

    def _node_name_changed_cb(self, node, prev_name, clientData):
        new_name = OpenMaya.MFnDependencyNode(node).name()
        new_name = adapt_name(new_name)

        for widget, callback in self.rename_callbacs:
            callback(widget, new_name)
        self.node = new_name

    def _attr_changed_cb(self, msg, plug, otherplug, clientData):
        if msg & OpenMaya.MNodeMessage.kAttributeSet or msg & OpenMaya.MNodeMessage.kAttributeEval:
            if msg & OpenMaya.MNodeMessage.kAttributeSet:
                clean = False
            elif msg & OpenMaya.MNodeMessage.kAttributeEval:
                clean = True

            plug_name = plug.partialName(includeNodeName=True, useLongNames=True)
            attr = plug_name.partition('.')[2]

            if clean:
                if attr in self.attrs_clean:
                    for widget, callback in self.attrs_clean[attr]:
                        callback(widget, clean)
            else:
                if attr in self.attrs_dirty:
                    for widget, callback in self.attrs_dirty[attr]:
                        callback(widget, clean)

    def add_name_changed(self, wght, cb):
        if not self.renamed_cbid:
            node_mobject = get_mobject(self.node)
            if node_mobject:
                renamed_cbid = OpenMaya.MNodeMessage.addNameChangedCallback(
                    node_mobject, self._node_name_changed_cb)
                self.renamed_cbid = renamed_cbid
        self.rename_callbacs.append((wght, cb))

    def add_value_changed(self, attr, wght, cb, clean=True, dirty=True):
        if not self.attr_changed_cbid:
            node_mobject = get_mobject(self.node)
            if node_mobject:
                attr_changed_cbid = OpenMaya.MNodeMessage.addAttributeChangedCallback(
                    node_mobject, self._attr_changed_cb)
                self.attr_changed_cbid = attr_changed_cbid
        if mc.objExists('{}.{}'.format(self.node, attr)):
            if clean:
                if attr not in self.attrs_clean:
                    self.attrs_clean[attr] = list()
                self.attrs_clean[attr].append((wght, cb))

            if dirty:
                if attr not in self.attrs_dirty:
                    self.attrs_dirty[attr] = list()
                self.attrs_dirty[attr].append((wght, cb))

    def remove_callbacks(self, wght, remove_rename=True, remove_plugs=True, plugs=None):
        if remove_rename:
            self.rename_callbacs = list(filter(
                (lambda widget_callback_pair: widget_callback_pair[0] != wght),
                self.rename_callbacs))
            if len(self.rename_callbacs) == 0:
                if self.renamed_cbid:
                    OpenMaya.MMessage.removeCallback(self.renamed_cbid)
                    self.renamed_cbid = None

        if remove_plugs:
            for attr in self.attrs_clean:
                if plugs and attr not in plugs:
                    continue
                self.attrs_clean[attr] = list(filter(
                    (lambda widget_callback_pair: widget_callback_pair[0] != wght),
                    self.attrs_clean[attr]))
            for attr in list(self.attrs_clean)[:]:
                if len(self.attrs_clean[attr]) == 0:
                    del self.attrs_clean[attr]

            for attr in self.attrs_dirty:
                if plugs and attr not in plugs:
                    continue
                self.attrs_dirty[attr] = list(filter(
                    (lambda widget_callback_pair: widget_callback_pair[0] != wght),
                    self.attrs_dirty[attr]))
            for attr in list(self.attrs_dirty)[:]:
                if len(self.attrs_dirty[attr]) == 0:
                    del self.attrs_dirty[attr]

            # if no callback left in attrs_clean and attr_dirty list
            # delete Maya attribute change callback
            if len(self.attrs_dirty) == 0 and len(self.attrs_clean) == 0:
                if self.attr_changed_cbid:
                    OpenMaya.MMessage.removeCallback(self.attr_changed_cbid)
                    self.attr_changed_cbid = None


class Watcher(object):
    def __init__(self):
        self.callback_list = list()

    def get_ctr_watcher(self, ctrl):
        for each in self.callback_list:
            if each.node == ctrl:
                return each
        ctr_watcher = ControlWatcher(ctrl)
        self.callback_list.append(ctr_watcher)
        return ctr_watcher

    def add_ctrl_name_changed(self, wght, plug, cb):
        ctrl = plug.split('.')[0]
        ctr_watcher = self.get_ctr_watcher(ctrl)
        ctr_watcher.add_name_changed(wght, cb)

    def add_ctrl_value_changed(self, wght, plug, cb, clean=True, dirty=True,
                               propagate_to_parent=True):
        ctrl, _, attr = plug.partition('.')
        ctr_watcher = self.get_ctr_watcher(ctrl)
        ctr_watcher.add_value_changed(attr, wght, cb, clean=clean, dirty=dirty)
        if dirty and propagate_to_parent:
            parent_attr = get_parent_plug(plug)
            if parent_attr:
                ctr_watcher.add_value_changed(parent_attr, wght, cb, clean=False, dirty=dirty)

    # TODO implement this
    def call_callbacks_for_plug(self, plug):
        node, _, attr = plug.partition('.')

    def remove_rename_callbacks(self, wght):
        for each in self.callback_list:
            each.remove_callbacks(wght, remove_plugs=False)

    def remove_plug_callbacks(self, wght, plugs=None):
        for each in self.callback_list:
            each.remove_callbacks(wght, remove_rename=False, plugs=plugs)


def get_scene_watcher():
    if not mocapx.scene_watcher:
        mocapx.scene_watcher = Watcher()
    return mocapx.scene_watcher
