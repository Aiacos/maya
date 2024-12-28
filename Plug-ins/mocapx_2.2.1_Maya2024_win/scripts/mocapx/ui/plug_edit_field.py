import maya.mel as mel
from mocapx.vendor.Qt import QtWidgets, QtCore
from mocapx.ui.widgets import BaseLineEdit
from mocapx.lib.utils import is_node_anim_curve, is_node_expression
from mocapx.lib.uiutils import scaled, generate_style_sheet, get_indicator_color_from_plug
from mocapx.lib import nodes


# noinspection PyPep8Naming
class PlugEditField(BaseLineEdit):
    def __init__(self, plug, *args, **kwargs):
        super(PlugEditField, self).__init__(*args, **kwargs)

        self._move_data = None
        self._menu_on = True
        self._preview_template = None

        self.plug = plug

        self.set_preview_precision(4)
        self.set_float_validator()
        self.set_menu_validator(self.validate_context_menu)

        self._incoming_node = None
        # actions
        self.select_connection_action = self.add_action()
        self.edit_expression_action = self.add_action()
        self.delete_expression_action = self.add_action("Delete Expression")
        self.set_key_action = self.add_action("Set Key")
        self.set_driven_key_action = self.add_action("Set Driven Key...")
        self.break_connection_action = self.add_action("Break Connection")
        self.lock_action = self.add_action("Lock Attribute")
        self.unlock_action = self.add_action("Unlock Attribute")
        # set handlers
        self.editingFinished.connect(self.edit_change_handle)
        self.select_connection_action.triggered.connect(self.select_connection_handle)
        self.edit_expression_action.triggered.connect(self.edit_expression_handle)
        self.delete_expression_action.triggered.connect(self.delete_expression_handle)
        self.set_key_action.triggered.connect(self.set_key_handle)
        self.set_driven_key_action.triggered.connect(self.set_driven_key_handle)
        self.break_connection_action.triggered.connect(self.break_connection_handle)
        self.lock_action.triggered.connect(self.lock_handle)
        self.unlock_action.triggered.connect(self.unlock_handle)

    # private methods
    # noinspection PyMethodMayBeStatic
    def _format_preview(self, value):
        return self._preview_template.format(value) if self._preview_template else str(value)

    def _refresh_indicator_color(self):
        if self.plug:
            settings = get_indicator_color_from_plug(self.plug)
            settings.update({"border": "none", "border-radius": "{}px".format(scaled(2))})
            self.setStyleSheet(
                generate_style_sheet("QLineEdit", settings)
            )

    # events
    def mousePressEvent(self, event):
        if self.plug and nodes.is_attr_settable(self.plug):
            if QtWidgets.QApplication.keyboardModifiers() == QtCore.Qt.ControlModifier:
                if event.buttons() == QtCore.Qt.RightButton:
                    factor = 1.0
                elif event.buttons() == QtCore.Qt.MiddleButton:
                    factor = 0.1
                else:
                    factor = 0.01
                self._move_data = nodes.get_attr_value(self.plug), factor, event.pos().x()
                event.accept()
        super(PlugEditField, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._move_data:
            value, factor, init_x = self._move_data
            if self.plug:
                nodes.set_attr_value(self.plug, value + factor * (event.pos().x() - init_x), force=False, verbose=False)
            event.accept()
        else:
            super(PlugEditField, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._move_data:
            self._move_data = None
            if event.button() == QtCore.Qt.RightButton:
                self._menu_on = False
            event.accept()
        else:
            super(PlugEditField, self).mouseReleaseEvent(event)

    # setting methods
    def validate_context_menu(self):
        self._incoming_node = None
        if not self._menu_on:
            self._menu_on = True
            return False
        if self.plug:
            connections = nodes.list_connections(self.plug, d=False, p=True)
            if connections:
                connected = True
                incoming_plug = connections[0]
                self._incoming_node = incoming_plug.split('.')[0]
                is_anim_curve = is_node_anim_curve(self._incoming_node)
                is_expression = is_node_expression(self._incoming_node)
            else:
                connected = incoming_plug = is_anim_curve = is_expression = False
            self.select_connection_action.setVisible(connected and not is_expression)
            if incoming_plug:
                self.select_connection_action.setText('{}...'.format(incoming_plug))
            if not connected:
                self.edit_expression_action.setText("Create New Expression...")
                self.edit_expression_action.setVisible(True)
            elif is_expression:
                self.edit_expression_action.setText("Edit Expression...")
                self.edit_expression_action.setVisible(True)
            else:
                self.edit_expression_action.setVisible(False)
            self.delete_expression_action.setVisible(is_expression)
            self.set_key_action.setVisible(not connected or is_anim_curve)
            self.set_driven_key_action.setVisible(not connected or is_anim_curve)
            self.break_connection_action.setVisible(connected and not is_expression)
            locked = bool(nodes.is_attr_locked(self.plug))
            self.lock_action.setVisible(not locked)
            self.unlock_action.setVisible(locked)
            return True
        return False

    def setValue(self, value):
        self.setText(self._format_preview(value))
        self._refresh_indicator_color()

    def set_preview_precision(self, value):
        self._preview_template = "{{:.{}f}}".format(value)
        if self.plug:
            self.setValue(nodes.get_attr_value(self.plug))

    def edit_change_handle(self):
        if self.plug:
            text = self.text()
            valid_text = self._format_preview(nodes.get_attr_value(self.plug))
            if valid_text != text:
                try:
                    value = float(text)
                except ValueError:
                    pass
                else:
                    if nodes.set_attr_value(self.plug, value, force=False, verbose=True):
                        return True
                self.setText(valid_text)
        return False

    def select_connection_handle(self):
        if self._incoming_node:
            mel.eval('evalDeferred("showEditor {}");'.format(self._incoming_node))

    def edit_expression_handle(self):
        if self.plug:
            mel.eval('expressionEditor EE "{}" "{}";'.format(*self.plug.split('.', 1)))

    def delete_expression_handle(self):
        if self._incoming_node:
            nodes.delete_node(self._incoming_node)

    def set_key_handle(self):
        if self.plug:
            mel.eval('setKeyframe "{}";'.format(self.plug))

    def set_driven_key_handle(self):
        if self.plug:
            mel.eval('setDrivenKeyWindow "{}" {{"{}"}};'.format(*self.plug.split('.', 1)))

    def break_connection_handle(self):
        if self.plug:
            nodes.break_incoming_connection(self.plug, remove_anim_curve=True)

    def lock_handle(self):
        if self.plug:
            nodes.lock_attribute(self.plug, True, verbose=True)

    def unlock_handle(self):
        if self.plug:
            nodes.lock_attribute(self.plug, False, verbose=True)
