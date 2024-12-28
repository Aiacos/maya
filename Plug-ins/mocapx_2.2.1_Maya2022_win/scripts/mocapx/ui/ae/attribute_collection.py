from mocapx.lib.uiutils import get_widget
from mocapx.ui.attribute_collection_pane import MCPXAttributeCollectionPane
from mocapx.lib.nodes import get_node_uuid, get_pose_attrs


def attribute_collection_create_view(parent, attrs_plug):
    node = attrs_plug.split('.')[0]
    ae_widget = get_widget(parent)
    ae_layout = ae_widget.layout()
    attr_collection_pane_widget = MCPXAttributeCollectionPane(node)
    ae_layout.addWidget(attr_collection_pane_widget)


def attribute_collection_update_view(parent, attrs_plug, prev_uuid):
    ae_widget = get_widget(parent)
    ae_layout = ae_widget.layout()
    attr_collection_pane_widget = None
    for c in range(ae_layout.count()):
        attr_collection_pane_widget = ae_layout.itemAt(c).widget()
        if isinstance(attr_collection_pane_widget, MCPXAttributeCollectionPane):
            break
    node = attrs_plug.split('.')[0]
    if attr_collection_pane_widget:
        if get_node_uuid(node) != prev_uuid or node != attr_collection_pane_widget.node or \
                (not attr_collection_pane_widget.get_labels() and get_pose_attrs(node)):
            # after scene closed - node_attr_changed_cb clears labels (due to disconnections)
            # need to refresh AE after reopening
            attr_collection_pane_widget.node = node
            attr_collection_pane_widget.refresh_state()
