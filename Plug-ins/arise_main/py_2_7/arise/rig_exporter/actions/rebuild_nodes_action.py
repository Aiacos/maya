"""RebuildNodesAction rebuilds all enabled nodes. """

from arise.utils.decorators_utils import simple_catch_error_dec

class RebuildNodesAction(object):
    """RebuildNodesAction rebuilds all enabled nodes. """
    def __init__(self):
        self.name = "Rebuild All Nodes"
        self.info = (
            "Rebuild enabled nodes which insures all nodes are connected and not modified.\n"
            "Will also inform you of any errors during build."
        )
        self.position = 200
        self.is_checked = True
        self.post_action = False

    @staticmethod
    @simple_catch_error_dec
    def run_action(main_window):
        """Run rebuild all nodes.

        main_window (IORMainWindow): Arise main window
        """
        print("\n#########################################################")
        print("############# Action: 'Rebuild Nodes' START. ############")
        print("#########################################################\n")

        results = main_window.scene_ptr.build_manager.build_nodes(nodes=main_window.scene_ptr.enabled_nodes)

        if results:
            return "Action successful"

        return "Rebuild encountered some errors/warnings. Check log above for details //"
