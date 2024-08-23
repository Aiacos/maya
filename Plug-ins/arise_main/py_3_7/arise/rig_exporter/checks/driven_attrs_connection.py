"""DrivenAttrsConnection checks for nodes driven attributes without a connection or value. """

from arise.rig_exporter.checks.abstract_check.abstract_check import AbstractCheckData
from arise.data_types.attributes_data_types import driven_connection_attribute_data

class DrivenAttrsConnection(AbstractCheckData):
    """Check for nodes driven attributes without a connection or value. """

    def __init__(self, main):
        AbstractCheckData.__init__(self, main)

        self.name = "Driven Attributes Connected"
        self.info = (
            "Checks for driven attributes without a connection or value.\n"
            "For a rig to function correctly, it is recommended that all of its nodes be driven."
        )
        self.has_fix = False
        self.type = "error"
        self.error_msg = ""
        self.position = 500

    def check(self):
        """Check logic subclasses will be placed here. (access IoMainWindow with self.main).

        Returns:
            bool: True if passed else False
        """
        for node in self.main.scene_ptr.enabled_nodes:
            for attr in node.node_data.attributes_list:
                if isinstance(attr, (driven_connection_attribute_data.DrivenConnectionAttributeData)):
                    if not attr.value:
                        self.error_msg = "Attribute without a driver or value: '{0}'".format(attr.long_name)
                        return False

        return True
