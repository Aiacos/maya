from maya.api import OpenMaya
from mocapx.lib import nodes
# pylint: enable=no-name-in-module
# noinspection PyUnresolvedReferences
from mocapx.vendor.Qt import QtWidgets, QtCore
from mocapx.ui.widgets import LineEditStyled, ToolButton, Container, BaseLineEdit
from mocapx.lib.utils import get_mobject
from mocapx.lib.uiutils import scaled, generate_style_sheet, get_indicator_color_from_plug


class SingleAttrViewAC(QtWidgets.QFrame):
    def __init__(self, root_attr, parent=None):
        super(SingleAttrViewAC, self).__init__(parent)

        self.root_attr = root_attr
        self.rest_attr = root_attr + ".restValue"

        # edit-fields show round values according to formatting
        # so, need to prevent set this round values after every editingFinished signal
        # for this we keep actual values to be able to check before setAttr
        self.rest_value = None

        self.attr_lbl = LineEditStyled(editable=False)
        self.attr_lbl.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        self.attr_rest_edit = BaseLineEdit(select_all_by_DoubleClick=True)
        self.attr_rest_edit.setTextMargins(scaled(3), scaled(0), scaled(0), scaled(0))
        self.attr_rest_edit.setMaximumWidth(scaled(100))
        self.attr_rest_edit.set_float_validator()

        self.delete = ToolButton(
            size=(scaled(18), scaled(18)),
            icon_name='MCPXDelete',
            alpha=True,
            icon_size=(scaled(16), scaled(16))
        )
        self.delete.setToolTip("Remove Attribute from the Collection")

        self.attr_rest_edit.editingFinished.connect(self.set_rest_value_handle)
        self.delete.clicked.connect(self.delete_attr_handle)

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(scaled(0), scaled(0), scaled(0), scaled(0))
        layout.setSpacing(scaled(2))
        layout.addWidget(self.attr_lbl)
        layout.addWidget(self.attr_rest_edit)
        layout.addWidget(self.delete)
        self.setLayout(layout)

        self.refresh_state()

    # noinspection PyMethodMayBeStatic
    def _format_preview(self, value):
        return "{:.4f}".format(value)

    def refresh_state(self):
        self.set_state_label()
        self.set_state_value()

    def set_state_label(self):
        self.attr_lbl.setText(nodes.get_real_attr(self.rest_attr, short=True))

    def set_state_value(self):
        self.rest_value = nodes.get_attr_value(self.rest_attr)
        self.attr_rest_edit.setText(self._format_preview(self.rest_value))
        self.attr_rest_edit.setStyleSheet(
            generate_style_sheet(
                "QLineEdit", get_indicator_color_from_plug(self.rest_attr)
            )
        )

    def set_rest_value_handle(self):
        text = self.attr_rest_edit.text()
        if self._format_preview(self.rest_value) != text:
            try:
                new_value = float(text)
            except ValueError:
                pass
            else:
                try:
                    if nodes.set_attr_value(self.rest_attr, new_value, force=False, verbose=True):
                        return
                except RuntimeError:
                    pass
        self.set_state_value()

    def delete_attr_handle(self):
        nodes.remove_multi_element(self.root_attr)


# noinspection PyPep8Naming, SpellCheckingInspection
class MCPXAttributeCollectionPane(QtWidgets.QFrame):
    def __init__(self, node, numElements=16, parent=None):
        super(MCPXAttributeCollectionPane, self).__init__(parent)

        self.node = node
        self.node_attr_changed_cbid = None

        self.page = None
        self.lastPage = None
        self.size = numElements

        self.all_entities = list()
        self.shown_entities = list()

        self.page_view = Container(self.shown_entities, SingleAttrViewAC)

        self.page_number_label = QtWidgets.QLabel("")
        self.page_number_label.setAlignment(QtCore.Qt.AlignCenter)
        self.page_number_label.setMinimumWidth(scaled(50))

        self.first_button = QtWidgets.QPushButton("<<")
        self.first_button.setFixedWidth(scaled(60))
        self.prev_button = QtWidgets.QPushButton("<")
        self.prev_button.setFixedWidth(scaled(30))
        self.next_button = QtWidgets.QPushButton(">")
        self.next_button.setFixedWidth(scaled(30))
        self.last_button = QtWidgets.QPushButton(">>")
        self.last_button.setFixedWidth(scaled(60))

        self.page_control_group = QtWidgets.QGroupBox("")
        self.page_control_group.setStyleSheet("QGroupBox {border: none}")
        b_layout = QtWidgets.QHBoxLayout()
        b_layout.setContentsMargins(scaled(6), scaled(6), scaled(6), scaled(6))
        b_layout.setSpacing(scaled(6))
        b_layout.addItem(QtWidgets.QSpacerItem(
            scaled(10), scaled(10), QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
        b_layout.addWidget(self.first_button)
        b_layout.addWidget(self.prev_button)
        b_layout.addWidget(self.page_number_label)
        b_layout.addWidget(self.next_button)
        b_layout.addWidget(self.last_button)
        self.page_control_group.setLayout(b_layout)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(scaled(0), scaled(0), scaled(0), scaled(0))
        layout.setSpacing(scaled(6))
        layout.addWidget(self.page_view)
        layout.addWidget(self.page_control_group)
        self.setLayout(layout)

        self.first_button.clicked.connect(self.first_page)
        self.prev_button.clicked.connect(self.prev_page)
        self.next_button.clicked.connect(self.next_page)
        self.last_button.clicked.connect(self.last_page)

        self.refresh_state()

    def first_page(self):
        self.page = 0
        self.update_page()

    def last_page(self):
        self.page = self.lastPage
        self.update_page()

    def next_page(self):
        self.page += 1
        self.update_page()

    def prev_page(self):
        self.page -= 1
        self.update_page()

    def update_page(self):
        self.page = max(0, min(self.page, self.lastPage))

        self.first_button.setEnabled(self.page != 0)
        self.prev_button.setEnabled(self.page != 0)
        self.next_button.setEnabled(self.page != self.lastPage)
        self.last_button.setEnabled(self.page != self.lastPage)

        self.page_number_label.setText("{}/{}".format(self.page + 1, self.lastPage + 1))

        self.shown_entities = self.all_entities[self.page * self.size: (self.page + 1) * self.size]

        self.page_view.replace_content(self.shown_entities)

    def update_content(self):
        self.all_entities = nodes.get_pose_attrs(self.node)

        self.lastPage = max(0, len(self.all_entities) // self.size + bool(len(self.all_entities) % self.size) - 1)

        self.page_control_group.setVisible(self.lastPage != 0)

        self.update_page()

    def refresh_state(self):
        self.page = 0
        self.update_content()

        self.clean_callbacks()
        node_mobject = get_mobject(self.node)
        if node_mobject:
            self.node_attr_changed_cbid = OpenMaya.MNodeMessage.addAttributeChangedCallback(
                node_mobject, self.node_attr_changed_cb)

    def get_labels(self, skip_empty=True):  # aux method to check if need AE to refresh
        labels = list()
        for item in self.page_view.items:
            label = item.attr_lbl.text()
            if not skip_empty or "." in label:  # empty[\d] doesn't contain dot
                labels.append(label)
        return labels

    def node_attr_changed_cb(self, msg, plug, otherplug, clientData):
        attr_name = plug.partialName(includeNodeName=False)

        if attr_name.startswith("attrs["):
            if msg & OpenMaya.MNodeMessage.kAttributeArrayAdded or \
                    msg & OpenMaya.MNodeMessage.kAttributeArrayRemoved:
                self.update_content()
            elif msg & OpenMaya.MNodeMessage.kAttributeSet or \
                    msg & OpenMaya.MNodeMessage.kConnectionMade or \
                    msg & OpenMaya.MNodeMessage.kConnectionBroken:
                root_attr = "{}.attrs[{}]".format(self.node, nodes.get_index(attr_name))
                if root_attr in self.page_view.items_dict:
                    if attr_name.endswith(".plug"):
                        self.page_view.items_dict[root_attr].set_state_label()
                    elif attr_name.endswith(".restValue"):
                        self.page_view.items_dict[root_attr].set_state_value()

    def clean_callbacks(self):
        if self.node_attr_changed_cbid:
            OpenMaya.MMessage.removeCallback(self.node_attr_changed_cbid)
            self.node_attr_changed_cbid = None
