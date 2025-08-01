"""Hive post buildscript template.  Blueprint for creating Hive buildscripts.


------------ TO CREATE YOUR NEW BUILD SCRIPT ----------------
Copy/paste this file and rename the `filename`, `class name` and the `id` ( id = "example" )

To enable the buildscript:

Change:

    class ExampleBuildScript(object):

To:

    class YourBuildScript(api.BaseBuildScript):

To assign to your rig in the Hive UI, reload Zoo Tools:

    ZooToolsPro (shelf) > Dev (purple icon) > Reload (menu item)

Open Hive UI and set the build script under:

    Settings (right top cog icon) >  Scripts > Build Scripts (dropdown combo box)

Be sure to reload Zoo Tools with any script changes.


------------ BUILD SCRIPT DOCUMENTATION ----------------

More Hive Build Script documentation found at:
    https://create3dcharacters.com/zoo-dev-documentation/packages/zoo_hive/buildscripting.html

Common build script code examples:
    https://create3dcharacters.com/zoo-dev-documentation/packages/zoo_hive/buildscripting_examples.html

"""
from zoo.libs.hive import api
from zoo.libs.maya.cmds.sets import selectionsets


class SelectionSetBuildFromSaved(api.BaseBuildScript):
    """

    .. note::

        Best to read the properties method in the base class :func:`api.BaseBuildScript.properties`

    """
    # unique identifier for the plugin which will be referenced by the registry.
    id = "selectionSetBuildFromSaved"  # change id to name that will appear in the hive UI.

    def postPolishBuild(self, properties):
        """Executed after the polish stage.

        Builds selections sets as saved in the scene, from the Zoo Selection Sets UI
        The node with the settings will try to import and load on polish from the node "zooHiveExportSettings"
        """
        selectionsets.loadselSetHierarchyScene()
