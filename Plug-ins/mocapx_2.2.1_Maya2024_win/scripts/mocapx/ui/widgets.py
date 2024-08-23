import re
import os
# pylint: disable=no-name-in-module
# noinspection PyUnresolvedReferences
from mocapx.vendor.Qt import QtCore, QtGui, QtWidgets
from mocapx.lib.uiutils import COLOR_GROUPS, RegExValidator, scaled, find_icon, set_color_palette_darker, \
    draw_rounded_rect, get_color_from_maya_palette
from mocapx.lib.utils import round_value


# noinspection PyPep8Naming
class BaseLabel(QtWidgets.QLabel):
    clicked = QtCore.Signal()
    mouseEntered = QtCore.Signal()
    mouseLeft = QtCore.Signal()

    def __init__(self, parent=None):
        super(BaseLabel, self).__init__(parent)
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        self.clicked.emit()
        QtWidgets.QLabel.mousePressEvent(self, event)

    def enterEvent(self, event):
        self.mouseEntered.emit()
        QtWidgets.QLabel.enterEvent(self, event)

    def leaveEvent(self, event):
        self.mouseLeft.emit()
        QtWidgets.QLabel.leaveEvent(self, event)


# noinspection PyPep8Naming
class ToolButton(QtWidgets.QPushButton):
    def __init__(self, size, icon_name=None, highlighted_icon=None, alpha=False, icon_size=None,
                 label=None, toggle=False):
        super(ToolButton, self).__init__()

        self._normal_icon = self._highlighted_icon = None
        self._hover_cursor = None

        self.alpha = alpha
        self.size = size
        self.icon_size = icon_size
        self.setFixedSize(size[0], size[1])

        self.action_context_menu = QtWidgets.QMenu()

        # Set Icon
        if icon_name:
            self.set_icon(icon_name, highlighted_icon, alpha, icon_size)
        if label:
            self.setText(label)

        if toggle:
            self.setCheckable(True)
            self.update_check_state()

    def event(self, event):
        if not self.isEnabled() and event.type() == QtCore.QEvent.Type.ContextMenu:
            self.contextMenuEvent(event)
            # This function returns true if the event was recognized (documentation)
            return True
        return super(ToolButton, self).event(event)

    def contextMenuEvent(self, event):
        if self.actions():
            self.action_context_menu.exec_(event.globalPos())

    # noinspection PyUnusedLocal
    def enterEvent(self, event):
        if self.isEnabled() and self.alpha and self._highlighted_icon:
            self.show_icon(self._highlighted_icon)
            if self._hover_cursor:
                self.setCursor(self._hover_cursor)

    # noinspection PyUnusedLocal
    def leaveEvent(self, event):
        if self.isEnabled() and self.alpha and self._normal_icon:
            self.show_icon(self._normal_icon)
            if self._hover_cursor:
                self.unsetCursor()

    def setChecked(self, value):
        super(ToolButton, self).setChecked(value)
        self.update_check_state()

    def actions(self):
        return self.action_context_menu.actions()

    def add_action(self, label=""):
        action = QtWidgets.QAction(self)
        action.setText(label)
        self.action_context_menu.addAction(action)
        return action

    def set_icon(self, icon_name, highlighted_icon=None, alpha=None, icon_size=None):
        self._normal_icon = find_icon(icon_name)
        if highlighted_icon:
            self._highlighted_icon = find_icon(highlighted_icon)
        else:
            self._highlighted_icon = self.generate_highlighted_icon(self._normal_icon)

        if alpha is not None:
            self.alpha = alpha

        if icon_size:
            self.icon_size = icon_size

        self.show_icon(self._normal_icon)
        self.update_check_state()

    def show_icon(self, icon_resource):
        icon = QtGui.QIcon(icon_resource)
        self.setIcon(icon)
        size = self.icon_size or self.size
        self.setIconSize(QtCore.QSize(*size))

    def update_check_state(self):
        if self.alpha:
            if not self.isCheckable() or not self.isChecked():
                self.setStyleSheet("QPushButton {border: none}")
            else:
                self.setStyleSheet("QPushButton {border: none; background-color: rgb(29, 29, 29)}")

    # noinspection PyMethodMayBeStatic
    def generate_highlighted_icon(self, icon_resource):
        img = QtGui.QImage(icon_resource)
        img = img.convertToFormat(QtGui.QImage.Format_ARGB32)
        for y in range(img.height()):
            for x in range(img.width()):
                pixel = img.pixel(x, y)
                color = QtGui.QColor(pixel)
                h, s, v, _ = color.getHsv()
                color.setHsv(h, s, min(v + 50, 255) if v > 30 else v)
                img.setPixel(x, y,
                             QtGui.qRgba(color.red(), color.green(), color.blue(), QtGui.qAlpha(pixel)))
        return QtGui.QPixmap.fromImage(img)

    def set_hover_cursor(self, cursor_shape):
        self._hover_cursor = cursor_shape


class ContainerMixin(object):
    def __init__(self):
        super(ContainerMixin, self).__init__()

    # noinspection PyAttributeOutsideInit
    def build_container(self, entities, constructor, stretch=False):
        # set up state
        self.constructor = constructor
        self.stretch = stretch
        self.items = list()
        self.items_dict = dict()

        # fill content
        self._add_widgets(entities)

        # If stretch add stretcher
        if self.stretch:
            self._add_stretch()

    def _add_widgets(self, entities):
        for entity in entities:
            widget = self.constructor(entity, self)
            self.items_dict[entity] = widget
            self.items.append(widget)
            # noinspection PyUnresolvedReferences
            self.layout.addWidget(widget)

    # noinspection PyAttributeOutsideInit, PyUnresolvedReferences
    def replace_content(self, entities):
        item = self.layout.takeAt(0)
        while item:
            if item:
                # get widget at given item
                widget = item.widget()
                if widget:
                    # if widget has cleanup method call it
                    if hasattr(widget, 'clean_callbacks') and callable(
                            getattr(widget, 'clean_callbacks')):
                        # noinspection PyCallingNonCallable
                        widget.clean_callbacks()
                    # delete widget
                    self.layout.removeWidget(widget)
                    widget.deleteLater()
                # delete item
                del item
                item = self.layout.takeAt(0)

        # reset state
        self.items = list()
        self.items_dict = dict()

        # fill content
        self._add_widgets(entities)

        # If stretch add stretcher
        if self.stretch:
            self._add_stretch()

    def _add_stretch(self):
        if self.stretch:
            # noinspection PyUnresolvedReferences
            self.layout.addStretch()

    # noinspection PyUnresolvedReferences
    def add_item(self, entity, index=None):
        widget = self.constructor(entity, self)
        self.items_dict[entity] = widget
        if index is None:
            # ignore stretch element if exists
            index = self.layout.count() - self.stretch
        # insert as last or by index
        self.items.insert(index, widget)
        self.layout.insertWidget(index, widget)
        return widget

    def remove_item(self, entity):
        if entity in self.items_dict:
            widget = self.items_dict[entity]
            # if widget has cleanup method call it
            if hasattr(widget, 'clean_callbacks') and callable(getattr(widget, 'clean_callbacks')):
                # noinspection PyCallingNonCallable
                widget.clean_callbacks()
            # noinspection PyUnresolvedReferences
            self.layout.removeWidget(widget)
            widget.deleteLater()
            self.items_dict[entity] = None
            del self.items_dict[entity]
            self.items.remove(widget)


class ContainerMixinDrag(ContainerMixin):
    def __init__(self):
        super(ContainerMixinDrag, self).__init__()

        self.floating_widget = None
        self.drag_start_position = 0
        self.prev_y = 0
        self.click_y = 0

    # noinspection PyUnresolvedReferences
    def _set_connections(self, item):
        if hasattr(item, "drag_started"):
            item.drag_started.connect(self.start_drag_handle)
        if hasattr(item, "drag_moved"):
            item.drag_moved.connect(self.move_drag_handle)
        if hasattr(item, "drag_finished"):
            item.drag_finished.connect(self.finish_drag_handle)

    def build_container(self, entities, constructor, stretch=False):
        super(ContainerMixinDrag, self).build_container(entities, constructor, stretch)
        for item in self.items:
            self._set_connections(item)

    def replace_content(self, entities):
        super(ContainerMixinDrag, self).replace_content(entities)
        for item in self.items:
            self._set_connections(item)

    def add_item(self, entity, index=None):
        item = super(ContainerMixinDrag, self).add_item(entity, index)
        self._set_connections(item)

        return item

    def start_drag_handle(self, widget, drag_start_position, prev_y, click_y):
        self.floating_widget = widget

        self.drag_start_position = drag_start_position
        self.prev_y = prev_y
        self.click_y = click_y

    # noinspection PyPep8Naming
    def move_drag_handle(self, eventPos, eventGlobalY):
        if self.floating_widget:
            if not self.floating_widget.styleSheet():
                self.floating_widget.setStyleSheet(
                    self.floating_widget.metaObject().className() + " {background-color: rgb(60, 96, 119)}")

            if (eventPos - self.drag_start_position).manhattanLength() >= QtWidgets.QApplication.startDragDistance():
                const_pos_x = self.floating_widget.geometry().x()
                # noinspection PyUnresolvedReferences
                float_height = self.floating_widget.geometry().height() + self.layout.spacing()

                # determine position for draggable widget:
                float_pos_y = eventGlobalY - self.click_y + self.prev_y

                # noinspection PyCallingNonCallable
                v_scroll_bar = self.verticalScrollBar() if hasattr(self, "verticalScrollBar") else None

                # noinspection PyUnresolvedReferences
                bottom_border = self.geometry().height() - float_height
                if v_scroll_bar:
                    top_border = v_scroll_bar.value()
                    bottom_border += v_scroll_bar.value()
                else:
                    top_border = 0

                float_pos_y = min(max(top_border, float_pos_y), bottom_border)

                # auto-scroll: need to do better
                if v_scroll_bar:
                    if v_scroll_bar.value() < v_scroll_bar.maximum() and float_pos_y == bottom_border:
                        v_scroll_bar.setValue(v_scroll_bar.value() + 5)
                    elif float_pos_y > 0 and float_pos_y == v_scroll_bar.value():
                        v_scroll_bar.setValue(v_scroll_bar.value() - 5)

                # move draggable widget
                # widget moves only for preview, in layout it stays at same position
                self.floating_widget.move(const_pos_x, float_pos_y)

                # correct positions of other widgets according to drag if required:
                new_order = ([], [])  # widgets above + widgets below the draggable widget
                # noinspection PyUnresolvedReferences
                free_position = self.layout.contentsMargins().top()
                check_above = True

                for widget in self.items:
                    if widget != self.floating_widget:
                        # noinspection PyUnresolvedReferences
                        widget_height = widget.geometry().height() + self.layout.spacing()
                        if check_above and (widget_height // 2) < (float_pos_y - free_position):
                            target_position = free_position
                            new_order[0].append(widget)
                        else:
                            check_above = False
                            target_position = free_position + float_height
                            new_order[1].append(widget)

                        if widget.pos().y() != target_position:
                            # widget moves only for preview, in layout it stays at same position
                            widget.move(const_pos_x, target_position)

                        free_position += widget_height

                # update list of widgets according to their preview positions
                # noinspection PyAttributeOutsideInit
                self.items = new_order[0] + [self.floating_widget] + new_order[1]

    # noinspection PyUnresolvedReferences
    def finish_drag_handle(self):
        if self.floating_widget:
            self.floating_widget.setStyleSheet("")

            new_index = self.items.index(self.floating_widget)
            self.layout.removeWidget(self.floating_widget)
            self.layout.insertWidget(new_index, self.floating_widget)
            self.floating_widget = None


class Container(ContainerMixin, QtWidgets.QFrame):
    def __init__(self, entities, constructor, spacing=2, margins=(4, 4, 4, 4)):
        super(Container, self).__init__()

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(*margins)
        self.layout.setSpacing(spacing)
        self.setLayout(self.layout)

        self.build_container(entities, constructor, stretch=False)


class ContainerDrag(ContainerMixinDrag, QtWidgets.QFrame):
    def __init__(self, entities, constructor):
        super(ContainerDrag, self).__init__()

        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setFrameShadow(QtWidgets.QFrame.Plain)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(scaled(2), scaled(2), scaled(2), scaled(2))
        self.layout.setSpacing(scaled(2))
        self.setLayout(self.layout)

        self.build_container(entities, constructor, stretch=False)


class ScrolledContainer(ContainerMixin, QtWidgets.QScrollArea):
    def __init__(self, entities, constructor):
        super(ScrolledContainer, self).__init__()

        self.setWidgetResizable(True)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setFrameShadow(QtWidgets.QFrame.Plain)

        # Widget
        inner = QtWidgets.QFrame(self)

        # Lay out
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(scaled(0), scaled(0), scaled(0), scaled(0))
        self.layout.setSpacing(scaled(2))
        inner.setLayout(self.layout)

        # Set main widget
        self.setWidget(inner)

        self.build_container(entities, constructor, stretch=True)


class ScrolledContainerDrag(ContainerMixinDrag, QtWidgets.QScrollArea):
    def __init__(self, entities, constructor):
        super(ScrolledContainerDrag, self).__init__()

        self.setWidgetResizable(True)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setFrameShadow(QtWidgets.QFrame.Plain)

        # Widget
        inner = QtWidgets.QFrame(self)

        # Lay out
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(scaled(0), scaled(0), scaled(0), scaled(0))
        self.layout.setSpacing(scaled(2))
        inner.setLayout(self.layout)

        # Set main widget
        self.setWidget(inner)

        self.build_container(entities, constructor, stretch=True)


class ActionButtonsRTD(QtWidgets.QFrame):
    connect_signal = QtCore.Signal()
    disconnect_signal = QtCore.Signal()
    start_session_signal = QtCore.Signal()
    pause_signal = QtCore.Signal()

    def __init__(self, state=0, pause_state=0, frame=True):
        super(ActionButtonsRTD, self).__init__()

        self.state = None

        # self.setFixedSize(42, 22)
        self.setFixedHeight(scaled(22))
        if frame:
            for c_group in COLOR_GROUPS:
                set_color_palette_darker(self, c_role="Background", c_group=c_group, factor=121)

        self.connect_button = QtWidgets.QPushButton("Connect")
        # self.connect_button.setFixedSize(38, 18)
        self.connect_button.clicked.connect(self.connect_handler)
        self.disconnect_button = QtWidgets.QPushButton("Disconnect")
        # self.disconnect_button.setFixedSize(18, 18)
        self.disconnect_button.clicked.connect(self.disconnect_handler)
        self.start_session_button = QtWidgets.QPushButton("Start")
        # self.start_session_button.setFixedSize(18, 18)
        self.start_session_button.clicked.connect(self.start_session_handler)
        self.start_session_button.setFixedWidth(scaled(38))
        self.pause_button = QtWidgets.QPushButton()
        self.pause_button.setFixedWidth(scaled(38))
        self.set_pause_label(pause_state)
        # self.pause_button.setFixedSize(18, 18)
        self.pause_button.clicked.connect(self.pause_handler)

        self.layout = QtWidgets.QHBoxLayout()
        self.layout.setContentsMargins(scaled(2), scaled(2), scaled(2), scaled(2))
        self.layout.setSpacing(scaled(2))
        self.layout.addWidget(self.connect_button)
        self.layout.addWidget(self.disconnect_button)
        self.layout.addWidget(self.start_session_button)
        self.layout.addWidget(self.pause_button)
        self.setLayout(self.layout)

        self.set_state(state)

    def set_pause_label(self, state):
        label = ("Play", "Pause")[state]
        self.pause_button.setText(label)

    def set_state(self, state):
        if state in (2, 3):
            self.connect_button.setVisible(False)
            self.disconnect_button.setVisible(True)
            self.start_session_button.setVisible(False)
            self.pause_button.setVisible(True)
        elif state == 1:
            self.connect_button.setVisible(False)
            self.disconnect_button.setVisible(True)
            self.start_session_button.setVisible(True)
            self.pause_button.setVisible(False)
        else:
            state = 0
            self.connect_button.setVisible(True)
            self.disconnect_button.setVisible(False)
            self.start_session_button.setVisible(False)
            self.pause_button.setVisible(False)

        self.state = state

    def connect_handler(self):
        self.connect_signal.emit()

    def disconnect_handler(self):
        self.disconnect_signal.emit()

    def start_session_handler(self):
        self.start_session_signal.emit()

    def pause_handler(self):
        self.pause_signal.emit()


class ActionButtonsClip(QtWidgets.QFrame):
    browse_signal = QtCore.Signal()
    reload_signal = QtCore.Signal()

    def __init__(self, frame=True):
        super(ActionButtonsClip, self).__init__()

        self.setFixedHeight(scaled(22))
        if frame:
            for c_group in COLOR_GROUPS:
                set_color_palette_darker(self, c_role="Background", c_group=c_group, factor=121)

        self.browse_button = ToolButton(
            size=(scaled(18), scaled(18)),
            icon_name='MCPXOpen',
            alpha=True
        )
        self.browse_button.clicked.connect(self.browse_handler)
        self.reload_button = ToolButton(
            size=(scaled(18), scaled(18)),
            icon_name='MCPXRefresh',
            alpha=True
        )
        self.reload_button.clicked.connect(self.reload_handler)

        self.layout = QtWidgets.QHBoxLayout()
        self.layout.setContentsMargins(scaled(2), scaled(2), scaled(2), scaled(2))
        self.layout.setSpacing(scaled(2))
        self.layout.addWidget(self.browse_button)
        self.layout.addWidget(self.reload_button)
        self.setLayout(self.layout)

    def browse_handler(self):
        self.browse_signal.emit()

    def reload_handler(self):
        self.reload_signal.emit()


# noinspection PyPep8Naming
class BaseSpinBox(QtWidgets.QSpinBox):
    def __init__(self, *args, **kwargs):
        super(BaseSpinBox, self).__init__(*args, **kwargs)

    def keyPressEvent(self, event):
        if not (event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return):
            super(BaseSpinBox, self).keyPressEvent(event)
        else:
            self.clearFocus()
            self.editingFinished.emit()


# noinspection PyPep8Naming
class BaseLineEdit(QtWidgets.QLineEdit):
    resized = QtCore.Signal()
    mouse_pressed = QtCore.Signal(object, object)
    mouse_moved = QtCore.Signal(object, object)
    mouse_released = QtCore.Signal(object, object)

    def __init__(self, text="", parent=None, default_context_menu=False, select_all_by_DoubleClick=False):
        super(BaseLineEdit, self).__init__(text, parent)

        self.__edit_mode = True
        self.__tab_focus_reason = True
        self.__default_context_menu = default_context_menu
        self.__select_all_by_DoubleClick = select_all_by_DoubleClick

        self.action_context_menu = QtWidgets.QMenu()
        self.action_context_menu_validator = None

    def focusInEvent(self, event):
        if self.__tab_focus_reason or event.reason() != QtCore.Qt.FocusReason.TabFocusReason:
            return super(BaseLineEdit, self).focusInEvent(event)

    def validateContextMenu(self):
        if self.action_context_menu_validator is None:
            return True
        return self.action_context_menu_validator()

    def contextMenuEvent(self, event):
        if self.__default_context_menu:
            return super(BaseLineEdit, self).contextMenuEvent(event)
        if self.actions() and self.validateContextMenu():
            self.action_context_menu.exec_(event.globalPos())

    def keyPressEvent(self, event):
        if not (event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return):
            return super(BaseLineEdit, self).keyPressEvent(event)
        self.clearFocus()

    def mousePressEvent(self, event):
        self.mouse_pressed.emit(event, self)
        if self.__edit_mode:
            return super(BaseLineEdit, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        self.mouse_moved.emit(event, self)
        if self.__edit_mode:
            return super(BaseLineEdit, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.mouse_released.emit(event, self)
        if self.__edit_mode:
            return super(BaseLineEdit, self).mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if not self.__select_all_by_DoubleClick:
            return super(BaseLineEdit, self).mouseDoubleClickEvent(event)
        self.selectAll()

    # noinspection PyPep8Naming
    def resizeEvent(self, event):
        self.resized.emit()
        return super(BaseLineEdit, self).resizeEvent(event)

    def setReadOnly(self, state):
        super(BaseLineEdit, self).setReadOnly(state)
        if not state:
            # need to simulate key press to fix Qt bug (caret cursor is hidden after readOnly switching)
            key_event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress, QtCore.Qt.Key_End, QtCore.Qt.NoModifier)
            QtCore.QCoreApplication.sendEvent(self, key_event)
            key_event = QtGui.QKeyEvent(QtCore.QEvent.KeyRelease, QtCore.Qt.Key_End, QtCore.Qt.NoModifier)
            QtCore.QCoreApplication.sendEvent(self, key_event)

    def actions(self):
        return self.action_context_menu.actions()

    def set_float_validator(self):
        value_regex = QtCore.QRegExp(r"^[+-]?([0-9]*[.])?[0-9]+$")
        self.setValidator(RegExValidator(value_regex))

    def set_menu_validator(self, validator):
        self.action_context_menu_validator = validator

    def add_action(self, label=""):
        action = QtWidgets.QAction(self)
        action.setText(label)
        self.action_context_menu.addAction(action)
        return action

    def block_tab_focus(self, state):
        self.__tab_focus_reason = not state


class DynamicLineEdit(BaseLineEdit):
    def __init__(self, tokens=()):
        super(DynamicLineEdit, self).__init__(default_context_menu=not bool(tokens))

        if tokens:
            for key in tokens:
                action = self.add_action(key)
                action.triggered.connect(self.get_handler(key))

    def adapt_position(self):
        position = self.cursorPosition()
        r_shift = l_shift = 0
        found = False

        for r_shift, char in enumerate(self.text()[position:]):
            if char == ">":
                found = True
                break
            elif char == "<":
                break
        for l_shift, char in enumerate(self.text()[:position][::-1]):
            if char == "<":
                found = True
                break
            elif char == ">":
                break

        if found and (r_shift or l_shift):
            if r_shift < l_shift:
                self.setCursorPosition(position + r_shift + 1)
            else:
                self.setCursorPosition(position - l_shift - 1)

    def get_handler(self, key):
        def handler():
            self.adapt_position()
            self.insert(key)

        return handler


# noinspection PyPep8Naming
class LineEditStyled(BaseLineEdit):
    edit_restricted = QtCore.Signal()

    def __init__(self, text="", editable=True, check_command=None, parent=None):
        super(LineEditStyled, self).__init__(text, parent)

        self.__style_setting = ""
        self.__editable = editable
        self.__check_command = check_command

        self.setFocusPolicy(QtCore.Qt.FocusPolicy.ClickFocus)
        self.refresh()

        if self.__editable:
            self.editingFinished.connect(self.refresh)

    def contextMenuEvent(self, event):
        font_metrics = QtGui.QFontMetrics(self.font())
        text_width = font_metrics.tightBoundingRect(self.text()).width()
        if event.pos().x() <= (text_width + 4):
            super(LineEditStyled, self).contextMenuEvent(event)

    def mouseDoubleClickEvent(self, event):
        if self.__edit_mode:
            return super(LineEditStyled, self).mouseDoubleClickEvent(event)

        if self.__editable and (not self.__check_command or self.__check_command()):
            self.__edit_mode = True
            super(LineEditStyled, self).setStyleSheet("")
            self.setReadOnly(False)
            self.selectAll()
        else:
            self.edit_restricted.emit()

    def setStyleSheet(self, setting_string=None):
        self.__style_setting = setting_string

        settings = {"QLineEdit": {"border": "none", "background-color": "rgba(0, 0, 0, 0)"}}

        if setting_string:
            parsed = re.findall("([a-z0-9]+)\s*{([^{}]+)}", setting_string, re.I)
            if not parsed:
                parsed = [("QLineEdit", setting_string)]
            for key, raw_value in parsed:
                if key not in settings:
                    settings[key] = dict()
                for sub_key, value in re.findall("([a-z0-9-]+)\s*:\s*([^:;]+)", raw_value, re.I):
                    settings[key][sub_key] = value

        setting_string = str()
        for key, raw_value in settings.items():
            if setting_string:
                setting_string += "; "
            value = str()
            for sub_key, sub_value in raw_value.items():
                if value:
                    value += "; "
                value += sub_key + ": " + sub_value
            setting_string += key + " {" + value + "}"

        super(LineEditStyled, self).setStyleSheet(setting_string)

    def refresh(self):
        self.__edit_mode = False
        self.setStyleSheet(self.__style_setting)
        self.setReadOnly(True)
        self.deselect()


# noinspection PyPep8Naming
class SliderBase(QtWidgets.QSlider):
    def __init__(self, orientation):
        super(SliderBase, self).__init__(orientation)

        self.__blocked = False

    # noinspection PyMethodMayBeStatic
    def wheelEvent(self, event):
        event.ignore()

    def mousePressEvent(self, event):
        if not self.__blocked:
            return super(SliderBase, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if not self.__blocked:
            return super(SliderBase, self).mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if not self.__blocked:
            return super(SliderBase, self).mouseMoveEvent(event)

    def set_blocked(self, state):
        self.__blocked = state


# noinspection PyPep8Naming
class DynamicSlider(QtWidgets.QFrame):
    valueChanged = QtCore.Signal(int)
    sliderPressed = QtCore.Signal()
    sliderReleased = QtCore.Signal()
    weight_min_set = QtCore.Signal(float)
    weight_max_set = QtCore.Signal(float)

    def __init__(self, orientation, f1=0.0, f2=1.0, factor=100, px_radius=6):
        super(DynamicSlider, self).__init__()

        self.factor = float(factor)

        self.slider = SliderBase(orientation=orientation)

        # min and max fields
        color_group = ("Disabled", "Active")[self.isEnabled()]
        border_color = get_color_from_maya_palette("Button", color_group).darker(108)
        style_template = "QLineEdit {{{{" \
                         "border: {BORDER_WIDTH}px solid rgb{BORDER_COLOR}; " \
                         "border-top-{{0}}-radius: {BORDER_RADIUS}px; " \
                         "border-bottom-{{0}}-radius: {BORDER_RADIUS}px;" \
                         "}}}}" \
                         "QLineEdit:focus {{{{" \
                         "border:{FOCUS_WIDTH}px solid rgba{FOCUS_COLOR}" \
                         "}}}}" \
                         .format(
                            BORDER_WIDTH=scaled(1),
                            BORDER_COLOR=tuple(border_color.getRgb()),
                            BORDER_RADIUS=px_radius,
                            FOCUS_WIDTH=2,  # do not scale to look as others
                            FOCUS_COLOR=(75, 110, 138, 1.0)
                          )
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                            QtWidgets.QSizePolicy.Minimum)

        self.min_field = BaseLineEdit(select_all_by_DoubleClick=True)
        self.min_field.set_float_validator()
        self.min_field.setMaximumWidth(scaled(40))
        self.min_field.setFixedHeight(scaled(20))
        self.min_field.setSizePolicy(size_policy)
        self.min_field.setStyleSheet(style_template.format("left"))
        self.min_field.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        self.max_field = BaseLineEdit(select_all_by_DoubleClick=True)
        # by sight margins for min- and max-field look the same now
        self.max_field.setTextMargins(scaled(2), scaled(0), scaled(0), scaled(0))
        self.max_field.set_float_validator()
        self.max_field.setMaximumWidth(scaled(40))
        self.max_field.setFixedHeight(scaled(20))
        self.max_field.setSizePolicy(size_policy)
        self.max_field.setStyleSheet(style_template.format("right"))
        self.max_field.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

        self.setRange(f1, f2)

        # layout
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(scaled(4), scaled(0), scaled(4), scaled(0))
        layout.setSpacing(scaled(4))
        layout.addWidget(self.min_field)
        layout.addWidget(self.slider)
        layout.addWidget(self.max_field)
        self.setLayout(layout)

        self.setFixedHeight(scaled(24))

        self.slider.valueChanged.connect(lambda value: self.valueChanged.emit(value))
        self.slider.sliderPressed.connect(self.sliderPressed.emit)
        self.slider.sliderReleased.connect(self.sliderReleased.emit)
        self.min_field.editingFinished.connect(self.set_min_handle)
        self.max_field.editingFinished.connect(self.set_max_handle)

    # noinspection PyMethodMayBeStatic
    def _format_preview(self, value):
        return str(round(value, 2))

    def _set_value_state(self, edit_field, value):
        text_value = self._format_preview(value)
        if text_value != edit_field.text():
            edit_field.setText(text_value)

    def value(self):
        return self.slider.value() / self.factor

    def minimum(self):
        return self.slider.minimum() / self.factor

    def maximum(self):
        return self.slider.maximum() / self.factor

    def setValue(self, value):
        self.slider.setValue(value * self.factor)

    # noinspection PyTypeChecker
    def setMinimum(self, value):
        self.slider.setMinimum(value * self.factor)
        self._set_value_state(self.min_field, value)

    # noinspection PyTypeChecker
    def setMaximum(self, value):
        self.slider.setMaximum(value * self.factor)
        self._set_value_state(self.max_field, value)

    def setRange(self, f1, f2):
        self.setMinimum(f1)
        self.setMaximum(f2)

    # noinspection PyTypeChecker
    def set_min_handle(self):
        text = self.min_field.text()
        if self._format_preview(self.minimum()) != text:
            try:
                value = float(text)
            except ValueError:
                pass
            else:
                return self.weight_min_set.emit(value)
        self._set_value_state(self.min_field, self.minimum())

    # noinspection PyTypeChecker
    def set_max_handle(self):
        text = self.max_field.text()
        if self._format_preview(self.maximum()) != text:
            try:
                value = float(text)
            except ValueError:
                pass
            else:
                return self.weight_max_set.emit(value)
        self._set_value_state(self.max_field, self.maximum())

    def block_tab_focus(self, state):
        self.min_field.block_tab_focus(state)
        self.max_field.block_tab_focus(state)

    def set_blocked(self, state):
        self.slider.set_blocked(state)
        self.min_field.setDisabled(state)
        self.max_field.setDisabled(state)


# noinspection PyPep8Naming
class FrameArea(QtWidgets.QFrame):
    mouse_pressed = QtCore.Signal(object, object)
    mouse_moved = QtCore.Signal(object, object)
    mouse_released = QtCore.Signal(object, object)
    mouse_entered = QtCore.Signal()
    mouse_left = QtCore.Signal()

    def __init__(self, parent=None):
        super(FrameArea, self).__init__(parent)

    def enterEvent(self, event):
        self.mouse_entered.emit()
        super(FrameArea, self).enterEvent(event)

    def leaveEvent(self, event):
        self.mouse_left.emit()
        super(FrameArea, self).leaveEvent(event)

    def mousePressEvent(self, event):
        self.mouse_pressed.emit(event, self)
        super(FrameArea, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        self.mouse_moved.emit(event, self)
        super(FrameArea, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.mouse_released.emit(event, self)
        super(FrameArea, self).mouseReleaseEvent(event)


# noinspection PyPep8Naming
class ArrowRadioButton(QtWidgets.QRadioButton):
    def __init__(self, color=(189, 189, 189), *args, **kwargs):
        super(ArrowRadioButton, self).__init__(*args, **kwargs)

        self.color = color
        self.setFixedSize(scaled(9), scaled(9))

    # noinspection PyUnusedLocal
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setBrush(QtGui.QColor(*self.color))
        if self.isChecked():
            points = (
                QtCore.QPointF(scaled(0.0), scaled(2.0)),
                QtCore.QPointF(scaled(8.0), scaled(2.0)),
                QtCore.QPointF(scaled(4.0), scaled(6.0))
            )
        else:
            points = (
                QtCore.QPointF(scaled(2.0), scaled(0.0)),
                QtCore.QPointF(scaled(6.0), scaled(4.0)),
                QtCore.QPointF(scaled(2.0), scaled(8.0))
            )
        painter.drawPolygon(points)
        painter.end()


# noinspection PyPep8Naming
class SwitcherPull(QtWidgets.QWidget):
    def __init__(self, size, angle_factor, label="", bold_font=True, parent=None):
        super(SwitcherPull, self).__init__(parent)
        self.label = label
        self.bold_font = bold_font
        self.angle_factor = angle_factor
        self.setFixedSize(*size)

    def set_label(self, text, bold_font=None):
        self.label = text
        if bold_font is not None:
            self.bold_font = bool(bold_font)

    # noinspection PyUnusedLocal
    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.setRenderHint(QtGui.QPainter.Antialiasing, True)
        qp.setPen(QtCore.Qt.NoPen)
        color_group = ("Disabled", "Active")[self.isEnabled()]
        qp.setBrush(get_color_from_maya_palette("Background", color_group))
        draw_rounded_rect(qp, self, 0, self.angle_factor)
        qp.setBrush(get_color_from_maya_palette("Button", color_group))
        draw_rounded_rect(qp, self, 1, self.angle_factor)
        qp.setPen(get_color_from_maya_palette("ButtonText", color_group))
        font = QtGui.QFont()
        font.setBold(self.bold_font)
        qp.setFont(font)
        qp.drawText(self.rect(), QtCore.Qt.AlignCenter, self.label)
        qp.end()


# noinspection PyPep8Naming
class ToggledSwitcher(QtWidgets.QWidget):
    toggled = QtCore.Signal()

    def __init__(self, value=0, labels=("WiFi", "USB"), bold_font=False, size=(54, 38, 24),
                 angle_factor=0.5, parent=None):
        super(ToggledSwitcher, self).__init__(parent)

        self.setFixedSize(size[0], size[2])

        self.labels = labels
        self.bold_font = bold_font
        self.angle_factor = angle_factor

        self.switcher_pull = SwitcherPull(
            size=(size[1], size[2] - 2),
            angle_factor=self.angle_factor,
            parent=self)
        self.switcher_pull_pos = ((self.height() - self.switcher_pull.height()) // 2,) * 2
        self.switcher_pull.move(*self.switcher_pull_pos)

        self.value = None
        self.blockSignals(True)  # to not emit signal during value init
        self.setValue(value)
        self.blockSignals(False)

    # noinspection PyUnusedLocal
    def setValue(self, value, silent=False):
        value = bool(value)
        if value != self.value:
            self.value = value
            self.switcher_pull.set_label(self.labels[self.value], self.bold_font)

            animation = QtCore.QPropertyAnimation(self.switcher_pull, b"pos")
            x = [self.switcher_pull_pos[0], self.width() - (self.switcher_pull.width() + self.switcher_pull_pos[0])]
            animation.setStartValue(QtCore.QPoint(x[self.value], self.switcher_pull_pos[1]))
            animation.setEndValue(QtCore.QPoint(x[1 - self.value], self.switcher_pull_pos[1]))
            animation.start()

            self.toggled.emit()

    # noinspection PyUnusedLocal
    def mouseReleaseEvent(self, event):
        if QtWidgets.QApplication.widgetAt(QtGui.QCursor.pos()) in (self, self.switcher_pull):
            self.setValue(1 - self.value)

    # noinspection PyUnusedLocal
    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.setRenderHint(QtGui.QPainter.Antialiasing, True)
        qp.setPen(QtGui.QPen(QtCore.Qt.NoPen))
        color_group = ("Disabled", "Active")[self.isEnabled()]
        qp.setBrush(get_color_from_maya_palette("Button", color_group).darker(112))
        draw_rounded_rect(qp, self, 0, self.angle_factor)
        bg_color = get_color_from_maya_palette("Base", color_group)
        qp.setBrush(bg_color.lighter(130))
        draw_rounded_rect(qp, self, 1, self.angle_factor)
        qp.setBrush(bg_color)
        draw_rounded_rect(qp, self, 2, self.angle_factor)
        qp.end()


# noinspection PyPep8Naming
class Liner(QtWidgets.QWidget):
    valueChanged = QtCore.Signal(object, float)
    rangeChanged = QtCore.Signal(object, float, float)

    def __init__(self, value=0.0, preview_precision=1, label="", editable=True):
        super(Liner, self).__init__()

        self.__editable = editable

        self.__i_width = 2
        self.__i_spacing = 1
        self.__l_margin = 6
        self.__r_margin = 6

        self.__label = label
        self.__value = value
        self.__preview_precision = max(0, preview_precision)

        self.__min = -0.1
        self.__pivot = 0.0
        self.__pivot_x = 16  # fixed x position of pivot or None
        self.__max = 1.0

        self.__threshold = 0.01

        self.__value_color = QtGui.QColor(72, 72, 72, 200), QtGui.QColor(67, 170, 181, 200)
        self.__peak_color = QtGui.QColor(96, 96, 96), QtGui.QColor(50, 210, 225)

    # private methods
    def __refresh_state_by_click(self, event):
        margin = self.__i_width + self.__i_spacing
        value_width = self.width() - 2 * margin
        pos_x = event.pos().x() - margin
        if self.__pivot_x is None:
            new_value = self.__min + (self.__max - self.__min) * (float(pos_x) / value_width)
        else:
            if pos_x > self.__pivot_x:
                new_value = self.__pivot + (self.__max - self.__pivot) * (
                        float(pos_x - self.__pivot_x) / (value_width - self.__pivot_x))
            elif pos_x < self.__pivot_x:
                new_value = self.__pivot - (self.__pivot - self.__min) * (
                        float(self.__pivot_x - pos_x) / self.__pivot_x)
            else:
                new_value = self.__pivot
        if new_value != self.__value:
            self.__value = new_value
            self.valueChanged.emit(self, new_value)
            self.update()

    # events
    # noinspection PyUnusedLocal
    def paintEvent(self, event):
        margin = self.__i_width + self.__i_spacing
        v_range = self.__max - self.__min
        value_width = self.width() - 2 * margin
        if self.__pivot_x is None:
            pivot_x = int(round(margin + value_width * (self.__pivot - self.__min) / v_range))
        else:
            pivot_x = margin + self.__pivot_x

        # paint
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.setRenderHint(QtGui.QPainter.Antialiasing, True)
        qp.setPen(QtGui.QPen(QtCore.Qt.NoPen))

        # background
        color_group = ("Disabled", "Active")[self.isEnabled()]
        bg_color = get_color_from_maya_palette("Base", color_group).lighter(130)
        qp.setBrush(bg_color)
        qp.drawRect(margin, 0, value_width, self.height())

        if self.__value is not None:
            if abs(self.__pivot - self.__value) < self.__threshold:
                value_x = pivot_x
            else:
                if self.__value >= self.__max:
                    value_x = margin + value_width
                elif self.__value <= self.__min:
                    value_x = margin
                else:
                    if self.__pivot_x is None:
                        value_x = int(round(margin + value_width * (self.__value - self.__min) / v_range))
                    else:
                        if self.__value >= self.__pivot:
                            value_x = int(round(
                                pivot_x + (value_width - self.__pivot_x) * (self.__value - self.__pivot) / (
                                        self.__max - self.__pivot)))
                        else:
                            value_x = int(round(pivot_x - self.__pivot_x * (self.__pivot - self.__value) / (
                                    self.__pivot - self.__min)))

            # value slider
            bar_width = abs(pivot_x - value_x)
            value_color = self.__value_color[self.isEnabled()]

            if bar_width < 2:
                pen = QtGui.QPen()
                pen.setWidth(1)
                pen.setColor(value_color)
                qp.setPen(pen)
                qp.drawLine(pivot_x, 0, pivot_x, self.height())
            else:
                gradient_width = max(pivot_x, self.width() - pivot_x)

                if self.__value > self.__pivot:
                    # ---BASE
                    gradient = QtGui.QLinearGradient(pivot_x, 0, pivot_x + gradient_width, 0)
                    gradient.setColorAt(0, value_color.darker(150))
                    gradient.setColorAt(1, value_color.lighter(120))
                    qp.setBrush(gradient)
                    qp.drawRect(pivot_x, 0, bar_width, self.height())
                    # ---TOP BORDER
                    gradient.setColorAt(0, value_color.lighter(110))
                    gradient.setColorAt(1, value_color.lighter(140))
                else:
                    # ---BASE
                    gradient = QtGui.QLinearGradient(pivot_x - gradient_width, 0, pivot_x, 0)
                    gradient.setColorAt(0, value_color.lighter(120))
                    gradient.setColorAt(1, value_color.darker(150))
                    qp.setBrush(gradient)
                    qp.drawRect(value_x, 0, bar_width, self.height())
                    # ---TOP BORDER
                    gradient.setColorAt(0, value_color.lighter(140))
                    gradient.setColorAt(1, value_color.lighter(110))

                # borders
                stoke_width = min(self.width(), self.height()) * 0.05
                # ---TOP BORDER
                qp.setBrush(gradient)
                points = (
                    QtCore.QPointF(pivot_x, 0.0),
                    QtCore.QPointF(value_x, 0.0),
                    QtCore.QPointF(value_x + stoke_width, stoke_width),
                    QtCore.QPointF(pivot_x, stoke_width))
                qp.drawPolygon(points)
                # ---BOTTOM and EDGE BORDER
                if self.__value > self.__pivot:
                    gradient.setColorAt(0, value_color.darker(130))
                    gradient.setColorAt(1, value_color.darker(110))
                else:
                    gradient.setColorAt(0, value_color.darker(110))
                    gradient.setColorAt(1, value_color.darker(130))
                qp.setBrush(gradient)
                points = (
                    QtCore.QPointF(value_x, self.height()),
                    QtCore.QPointF(pivot_x, self.height()),
                    QtCore.QPointF(pivot_x, self.height() - stoke_width),
                    QtCore.QPointF(value_x + stoke_width, self.height() - stoke_width),
                    QtCore.QPointF(value_x + stoke_width, stoke_width),
                    QtCore.QPointF(value_x, 0.0))
                qp.drawPolygon(points)

            # clamping indicators
            if (self.__min - self.__value) > self.__threshold:
                qp.setBrush(self.__peak_color[self.isEnabled()])
                qp.drawRect(0, 0, self.__i_width, self.height())
            if (self.__value - self.__max) > self.__threshold:
                qp.setBrush(self.__peak_color[self.isEnabled()])
                qp.drawRect(self.width() - self.__i_width, 0, self.__i_width, self.height())

        # text
        qp.setPen(get_color_from_maya_palette("Text", color_group))
        widget_rect = self.rect() - QtCore.QMargins(self.__l_margin + pivot_x, 0, self.__r_margin + margin, 0)
        # ---LABEL
        if self.__label:
            qp.drawText(
                widget_rect, QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter, self.__label)
        # ---VALUE
        if self.__value is not None:
            value_text = ("{0:." + str(self.__preview_precision) + "f}").format(
                round_value(self.__value, self.__preview_precision))
        else:
            value_text = "inf"
        qp.drawText(
            widget_rect, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter, value_text)
        qp.end()

    def mousePressEvent(self, event):
        if self.__editable and event.buttons() == QtCore.Qt.LeftButton:
            self.__refresh_state_by_click(event)

    def mouseMoveEvent(self, event):
        if self.__editable and event.buttons() == QtCore.Qt.LeftButton:
            self.__refresh_state_by_click(event)

    # query
    def value(self):
        return self.__value

    def minimum(self):
        return self.__min

    def maximum(self):
        return self.__max

    def label(self):
        return self.__label

    # setting
    def setEditable(self, editable):
        self.__editable = editable

    def setLeftMargin(self, l_value):
        self.__l_margin = l_value

    def setRightMargin(self, r_value):
        self.__r_margin = r_value

    def setMargins(self, l_value, r_value):
        self.__l_margin = l_value
        self.__r_margin = r_value

    def setPivot(self, new_value):
        self.__pivot = new_value

    def setValue(self, new_value):
        if new_value != self.__value:
            _range = 10000000
            self.__value = float(new_value) if (-_range < new_value < _range) else None
            self.valueChanged.emit(self, new_value)
            self.update()

    def setMinimum(self, value_min):
        if value_min != self.__min:
            self.__min = float(value_min)
            self.rangeChanged.emit(self, self.__min, self.__max)
            self.update()

    def setMaximum(self, value_max):
        if value_max != self.__max:
            self.__max = float(value_max)
            self.rangeChanged.emit(self, self.__min, self.__max)
            self.update()

    def setRange(self, value_min, value_max):
        if value_min != self.__min or value_max != self.__max:
            self.__min = float(value_min)
            self.__max = float(value_max)
            self.rangeChanged.emit(self, self.__min, self.__max)
            self.update()

    def setLabel(self, label):
        self.__label = str(label)
