"""Maya RMB marking menu setup
"""

from .menu import (MarkingMenu,
                   Registry,
                   Layout,
                   findLayout,
                   InvalidJsonFileFormat,
                   MissingMarkingMenu,
                   MarkingMenuCommand)

removeAllActiveMenus = MarkingMenu.removeAllActiveMenus
removeExistingMenu = MarkingMenu.removeExistingMenu
