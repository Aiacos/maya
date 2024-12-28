from mocapx.lib.uiutils import get_widget
from mocapx.ui.adapter_datasources_pane import MCPXAdapterDataSourcesPane
from mocapx.lib.nodes import get_node_uuid, get_adapter_sources


def adapter_datasouces_create_view(parent, dn_set_members_plug):
    node = dn_set_members_plug.split('.')[0]
    ae_widget = get_widget(parent)
    ae_layout = ae_widget.layout()
    datasources_pane = MCPXAdapterDataSourcesPane(node)
    ae_layout.addWidget(datasources_pane)


def adapter_datasouces_update_view(parent, dn_set_members_plug, prev_uuid):
    ae_widget = get_widget(parent)
    ae_layout = ae_widget.layout()
    datasouces_pane_widget = None
    for c in range(ae_layout.count()):
        datasouces_pane_widget = ae_layout.itemAt(c).widget()
        if isinstance(datasouces_pane_widget, MCPXAdapterDataSourcesPane):
            break
    node = dn_set_members_plug.split('.')[0]
    if datasouces_pane_widget:
        if get_node_uuid(node) != prev_uuid or node != datasouces_pane_widget.node or \
                (not datasouces_pane_widget.sources and get_adapter_sources(node)): # after scene closed - AE clean
                                                                                    # need to refresh AE after reopening
            datasouces_pane_widget.node = node
            datasouces_pane_widget.refresh_state()
