import os
import re
from maya.api import OpenMaya
from mocapx.lib import nodes
from mocapx.lib.utils import get_mobject, adapt_name, is_path_abs
from mocapx.lib.uiutils import scaled
from mocapx.ui.widgets import DynamicLineEdit, LineEditStyled, BaseSpinBox, ToolButton
# noinspection PyUnresolvedReferences
# pylint: disable=no-name-in-module
from mocapx.vendor.Qt import QtCore, QtWidgets, QtGui


# pylint: enable=no-name-in-module


class ValidationException(Exception):
    pass


class Validator(object):
    @staticmethod
    def set_increment(hashed_path, extension, preview=False):
        hashes = re.findall(r'#+', hashed_path)
        if hashes:
            if len(hashes) > 1:
                raise ValidationException('Multiple usage of hashes.')

            path_template = hashed_path.replace(
                hashes[0],
                '{' + ':0{}d'.format(len(hashes[0])) + '}'
            )

            index = 1
            while True:
                hashed_path = path_template.format(index)
                if preview or not os.path.exists(hashed_path + extension):
                    break
                index += 1

        return hashed_path

    @staticmethod
    def validate(template, tokens=None):
        if not template:
            raise ValidationException('Empty path.')

        # Process system variables
        for item in set(re.findall(r'\${[a-zA-Z_][a-zA-Z0-9_]*}', template)):
            key = item
            for char in '${}':
                key = key.replace(char, '')

            value = os.getenv(key)
            if value is None:
                raise ValidationException('Variable {} isn\'t declared.'.format(key))
            template = template.replace(item, value)

        if re.search(r'[${}]', template):
            raise ValidationException('Wrong system variable use.')

        # Process tokens
        if tokens:
            for token in set(re.findall(r"<[^<>\r\n]+>", template)):
                if token.lower() in tokens:
                    if hasattr(tokens[token], '__call__'):
                        value = tokens[token]()
                    else:
                        value = tokens[token]
                    template = template.replace(token, value)
                else:
                    raise ValidationException('Unknown token {} used.'.format(token))

        # Validate path
        for char in '*?\"<>|;':
            if char in template:
                raise ValidationException('Wrong symbol in filepath {}.'.format(char))

        if ":" in os.path.splitdrive(template)[1]:
            raise ValidationException('Wrong place for colon sign.')
        dirname, filename = os.path.split(template)

        if not os.path.splitext(filename)[0]:
            raise ValidationException('No filename.')
        template = template.replace("\\", "/")

        return template


# noinspection SpellCheckingInspection
class MCPXRealTimeDeviceRecordPane(QtWidgets.QWidget):
    def __init__(self, node, parent=None):
        super(MCPXRealTimeDeviceRecordPane, self).__init__(parent)

        # State
        self.node = node
        self.connection_status = nodes.get_realtime_device_conn_status(self.node)

        self.scene_saved_cbid = None
        self.node_renamed_cbid = None
        self.connection_state_changed_cbid = None
        self.attrs_changed_cbid = None

        self.output_path = ''
        self.extensions = ('.mcpx', '.mp4')
        self.tokens = {
            '<scenedir>': nodes.get_scene_directory,
            '<scenename>': nodes.get_scene_name,
            '<nodename>': lambda: self.node}

        # Filepath template + file dialog
        self.path_template_line_edit = DynamicLineEdit(list(self.tokens.keys()))
        self.path_template_line_edit.setFixedHeight(scaled(20))
        self.file_browse_button = ToolButton(
            size=(scaled(20), scaled(20)),
            icon_name='MCPXOpen',
            alpha=True)
        self.file_dialog = QtWidgets.QFileDialog(
            parent=self,
            caption="Save clip",
            directory=nodes.get_project_directory(),
            filter="MocapX Clips (*{});;Movie Files (*{})".format(*self.extensions))
        self.file_dialog.setOptions(QtWidgets.QFileDialog.DontUseNativeDialog)
        self.file_dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)

        # Clip output filepath preview
        self.output_clip_label = QtWidgets.QLabel()
        self.output_clip_preview = LineEditStyled(editable=False)

        # Video output filepath preview
        self.output_video_label = QtWidgets.QLabel()
        self.output_video_preview = LineEditStyled(editable=False)

        # Clip duration
        self.time_label = QtWidgets.QLabel("sec:")
        self.time_label.setFixedSize(scaled(20), scaled(20))
        self.time_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.time_spin_box = BaseSpinBox()
        self.time_spin_box.setMinimumWidth(scaled(50))
        self.time_spin_box.setFixedHeight(scaled(20))
        self.time_spin_box.setRange(1, 3600)
        self.save_clip_button = QtWidgets.QPushButton("Save Clip")
        self.save_clip_button.setFixedHeight(scaled(20))

        # Setup handlers
        self.destroyed.connect(self.clean_callbacks)
        self.path_template_line_edit.textChanged.connect(self.path_template_handle)
        self.file_browse_button.clicked.connect(self.file_browse_handle)
        self.output_clip_preview.resized.connect(self.path_template_handle)
        self.time_spin_box.valueChanged.connect(self.clip_length_handle)
        self.save_clip_button.clicked.connect(self.save_clip_handle)

        # layout widgets
        clip_layout = QtWidgets.QHBoxLayout()
        clip_layout.setContentsMargins(scaled(0), scaled(0), scaled(0), scaled(0))
        clip_layout.setSpacing(scaled(6))
        clip_layout.addWidget(self.output_clip_label)
        clip_layout.addWidget(self.output_clip_preview)
        self.output_clip_group = QtWidgets.QGroupBox("")
        self.output_clip_group.setStyleSheet("QGroupBox {border: none}")
        self.output_clip_group.setMinimumHeight(scaled(20))
        self.output_clip_group.setLayout(clip_layout)

        video_layout = QtWidgets.QHBoxLayout()
        video_layout.setContentsMargins(scaled(0), scaled(0), scaled(0), scaled(0))
        video_layout.setSpacing(scaled(6))
        video_layout.addWidget(self.output_video_label)
        video_layout.addWidget(self.output_video_preview)
        self.output_video_group = QtWidgets.QGroupBox("")
        self.output_video_group.setStyleSheet("QGroupBox {border: none}")
        self.output_video_group.setMinimumHeight(scaled(20))
        self.output_video_group.setLayout(video_layout)

        template_layout = QtWidgets.QHBoxLayout()
        template_layout.setContentsMargins(scaled(6), scaled(6), scaled(6), scaled(6))
        template_layout.setSpacing(scaled(2))
        template_layout.addWidget(self.path_template_line_edit)
        template_layout.addWidget(self.file_browse_button)
        control_layout = QtWidgets.QHBoxLayout()
        control_layout.setContentsMargins(scaled(6), scaled(6), scaled(6), scaled(6))
        control_layout.setSpacing(scaled(6))
        control_layout.addLayout(template_layout)
        control_layout.addWidget(self.time_label)
        control_layout.addWidget(self.time_spin_box)
        control_layout.addWidget(self.save_clip_button)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(scaled(6), scaled(6), scaled(6), scaled(6))
        layout.setSpacing(scaled(6))
        layout.addWidget(self.output_clip_group)
        # layout.addWidget(self.output_video_group)
        layout.addLayout(control_layout)
        self.setLayout(layout)

        # Setup state according to the node
        # Setup maya callbacks
        self.refresh_state()

    def refresh_state(self):
        self.clean_callbacks()
        self.scene_saved_cbid = OpenMaya.MSceneMessage.addCallback(
            OpenMaya.MSceneMessage.kAfterSave, self.scene_saved_cb)
        node_mobject = get_mobject(self.node)
        if node_mobject:
            self.node_renamed_cbid = OpenMaya.MNodeMessage.addNameChangedCallback(
                node_mobject, self.maya_node_name_changed_cb)
            self.attrs_changed_cbid = OpenMaya.MNodeMessage.addAttributeChangedCallback(
                node_mobject, self.attrs_changed_cb)
        if not self.connection_state_changed_cbid:
            # noinspection PyCallByClass
            self.connection_state_changed_cbid = OpenMaya.MUserEventMessage.addUserEventCallback(
                'MCPXRltDvceConnStatusChanged', self.status_changed_cb)

        self.path_template_line_edit.setText(
            nodes.get_realtime_device_path_template(self.node))
        self.time_spin_box.setValue(
            nodes.get_realtime_device_clip_length(self.node))

        self.connection_status = nodes.get_realtime_device_conn_status(self.node)

        self.path_template_handle()

    # HANDLERS
    def save_clip_handle(self):
        if not is_path_abs(self.output_path):
            abs_path = nodes.get_project_directory() + "/" + self.output_path.lstrip("/")
        else:
            abs_path = self.output_path
        abs_path = Validator.set_increment(abs_path, self.extensions[0])

        nodes.clipreader_save_clip(
            self.node,
            abs_path + self.extensions[0],
            self.time_spin_box.value(),
            abs_path + self.extensions[1])

    def file_browse_handle(self):
        if self.file_dialog.exec_():
            selected = self.file_dialog.selectedFiles()[0]
            base, ext = os.path.splitext(selected)
            filename = base if (ext in self.extensions) else selected
            nodes.set_realtime_device_path_template(self.node, filename)

    def path_template_handle(self):
        template = self.path_template_line_edit.text()
        self.output_path = template
        preview_clip_path = ''
        preview_video_label = ''
        preview_video_path = ''

        try:
            self.output_path = Validator.validate(self.output_path, self.tokens)
            preview = Validator.set_increment(self.output_path, self.extensions[0], preview=True)
        except ValidationException as err:
            preview_clip_label = "Invalid path: " + str(err)
            self.save_clip_button.setEnabled(False)
            self.output_clip_preview.setVisible(False)
            self.output_video_preview.setVisible(False)
        else:
            allowed_length = int((self.output_clip_preview.width() - scaled(150)) * 0.2)
            actual_length = len(preview)
            if actual_length > allowed_length:
                preview = "..." + preview[actual_length - allowed_length:]

            preview_clip_label, preview_clip_path = "Clip Path: ", preview + self.extensions[0]
            preview_video_label, preview_video_path = "Video Path: ", preview + self.extensions[1]
            nodes.set_realtime_device_path_template(self.node, template)
            self.save_clip_button.setEnabled(True)
            self.output_clip_preview.setVisible(True)
            self.output_video_preview.setVisible(True)

        self.output_clip_label.setText(preview_clip_label)
        self.output_clip_preview.setText(preview_clip_path)
        self.output_video_label.setText(preview_video_label)
        self.output_video_preview.setText(preview_video_path)

    def clip_length_handle(self):
        nodes.set_realtime_device_clip_length(self.node, self.time_spin_box.value())

    # CALLBACKS
    # noinspection PyUnusedLocal
    def scene_saved_cb(self, *args, **kwargs):
        self.path_template_handle()

    # noinspection PyPep8Naming,PyUnusedLocal
    def maya_node_name_changed_cb(self, node, prev_name, clientData):
        new_name = OpenMaya.MFnDependencyNode(node).name()
        new_name = adapt_name(new_name)
        self.node = new_name
        self.path_template_handle()

    # noinspection PyPep8Naming,PyUnusedLocal
    def attrs_changed_cb(self, msg, plug, otherplug, clientData):
        attr_name = plug.partialName(includeNodeName=False)
        if msg & OpenMaya.MNodeMessage.kAttributeSet and attr_name == "clipPathTemplate":
            path_template = nodes.get_realtime_device_path_template(self.node)
            if path_template != self.path_template_line_edit.text():
                self.path_template_line_edit.setText(path_template)
        if msg & OpenMaya.MNodeMessage.kAttributeSet and attr_name == "clipLength":
            clip_length = nodes.get_realtime_device_clip_length(self.node)
            if clip_length != self.time_spin_box.value():
                self.time_spin_box.setValue(clip_length)

    # noinspection PyUnusedLocal
    def status_changed_cb(self, data):
        status = nodes.get_realtime_device_conn_status(self.node)
        if status != self.connection_status:
            self.connection_status = status

    def clean_callbacks(self):
        if self.scene_saved_cbid:
            OpenMaya.MMessage.removeCallback(self.scene_saved_cbid)
        if self.node_renamed_cbid:
            OpenMaya.MMessage.removeCallback(self.node_renamed_cbid)
        if self.attrs_changed_cbid:
            OpenMaya.MMessage.removeCallback(self.attrs_changed_cbid)
