"""DumpAndPlaceholdersGrps checks if there are any objects in dump_grp and placeholders_grp. """

from arise.rig_exporter.checks.abstract_check.abstract_check import AbstractCheckData
from arise.utils.maya_manage_utils import is_dump_grp_empty, is_placeholder_grp_empty

class DumpAndPlaceholdersGrps(AbstractCheckData):
    """Check if there are any objects in dump_grp and placeholders_grp. """

    def __init__(self, main):
        AbstractCheckData.__init__(self, main)

        self.name = "Dump And Placeholder Grps"
        self.info = "Checks if 'dump_grp' and 'placeholders_grp' have objects in them."
        self.has_fix = False
        self.type = "error"
        self.error_msg = ""
        self.position = 300

    def check(self):
        """Check logic subclasses will be placed here. (access IoMainWindow with self.main).

        Returns:
            bool: True if passed else False
        """
        dump_empty = is_dump_grp_empty()
        placeholder_empty = is_placeholder_grp_empty()
        if dump_empty and placeholder_empty:
            return True

        if not dump_empty and not placeholder_empty:
            self.error_msg = "Both 'dump_grp' and 'placeholders_grp' have objects in them."

        elif not dump_empty:
            self.error_msg = "'dump_grp' has objects in it."

        else:
            self.error_msg = "'placeholders_grp' has objects in it."

        return False
