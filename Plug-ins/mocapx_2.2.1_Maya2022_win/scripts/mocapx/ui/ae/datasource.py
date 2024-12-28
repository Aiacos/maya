from mocapx.lib.uiutils import get_widget
from mocapx.ui.rltdvce_playback_pane import MCPXRealTimeDevicePlaybackPane
from mocapx.ui.rltdvce_record_pane import MCPXRealTimeDeviceRecordPane
from mocapx.ui.datasource_attr_pane import DataSourceAttrPane
from mocapx.lib.nodes import get_node_uuid, get_realtime_device_conn_status


def realtime_device_create_view(parent, ip_address_plug):
    node = ip_address_plug.split('.')[0]
    ae_widget = get_widget(parent)
    ae_layout = ae_widget.layout()
    playback_pane = MCPXRealTimeDevicePlaybackPane(node)
    ae_layout.addWidget(playback_pane)


def realtime_device_update_view(parent, ip_address_plug, prev_uuid):
    ae_widget = get_widget(parent)
    ae_layout = ae_widget.layout()
    playback_pane_widget = None
    for c in range(ae_layout.count()):
        widget = ae_layout.itemAt(c).widget()
        if isinstance(widget, MCPXRealTimeDevicePlaybackPane):
            playback_pane_widget = widget
            break

    node = ip_address_plug.split('.')[0]
    if playback_pane_widget:
        if get_node_uuid(node) != prev_uuid or node != playback_pane_widget.node or \
                get_realtime_device_conn_status(node) != playback_pane_widget.action_buttons.state:
            playback_pane_widget.node = node
            playback_pane_widget.refresh_state()


def realtime_device_records_create_view(parent, clipPathTemplate):
    node = clipPathTemplate.split('.')[0]
    ae_widget = get_widget(parent)
    ae_layout = ae_widget.layout()
    record_video_pane = MCPXRealTimeDeviceRecordPane(node)
    ae_layout.addWidget(record_video_pane)


def realtime_device_records_update_view(parent, clipPathTemplate, prev_uuid):
    ae_widget = get_widget(parent)
    ae_layout = ae_widget.layout()
    record_video_pane_widget = None

    node = clipPathTemplate.split('.')[0]

    for c in range(ae_layout.count()):
        record_video_pane_widget = ae_layout.itemAt(c).widget()
        if isinstance(record_video_pane_widget, MCPXRealTimeDeviceRecordPane):
            break

    if record_video_pane_widget:
        if get_node_uuid(node) != prev_uuid or node != record_video_pane_widget.node:
            record_video_pane_widget.node = node
            record_video_pane_widget.refresh_state()


def attr_list_create_view(parent, plug):
    node = plug.split('.')[0]
    ae_widget = get_widget(parent)
    ae_layout = ae_widget.layout()
    pane = DataSourceAttrPane(node)
    ae_layout.addWidget(pane)


def attr_list_update_view(parent, plug, prev_uuid):
    ae_widget = get_widget(parent)
    ae_layout = ae_widget.layout()
    pane_widget = None
    for c in range(ae_layout.count()):
        widget = ae_layout.itemAt(c).widget()
        if isinstance(widget, DataSourceAttrPane):
            pane_widget = widget
            break

    node = plug.split('.')[0]
    if pane_widget:
        if get_node_uuid(node) != prev_uuid or node != pane_widget.node:
            pane_widget.node = node
            pane_widget.refresh_state()
