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

from maya import cmds

from zoo.libs.hive import api
from zoo.libs.maya.cmds.sets import selectionsets


class SelectionSetAllComponents(
    api.BaseBuildScript):  # Change (object) to (api.BaseBuildScript), change the class name to your name.
    """

    .. note::

        Best to read the properties method in the base class :func:`api.BaseBuildScript.properties`

    """
    # unique identifier for the plugin which will be referenced by the registry.
    id = "selectionSetAllComponents"  # change id to name that will appear in the hive UI.
    fingerThumbNames = ["finger", "thumb", "index", "middle", "ring", "pinky"]
    iconsDict = {"all": "st_starYellow",
                 "body": "st_starRed",
                 "spine": "st_pentagonAqua",
                 "leg": "st_triangleBlue",
                 "head": "st_circlePink",
                 "neck": "st_circlePink",
                 "god": "st_squarePink",
                 "arm": "st_triangleOrange",
                 "fingersAndThumb": "st_squarePink",
                 "hand": "st_squarePurple",
                 "finger": "st_squarePink",
                 "toe": "st_squareGreen",
                 "thumb": "st_squarePink",
                 "index": "st_squarePink",
                 "middle": "st_squarePink",
                 "ring": "st_squarePink",
                 "pinky": "st_squarePink",
                 "eye": "st_trianglePink",
                 "ear": "st_trianglePink",
                 "nose": "st_trianglePink",
                 "mouth": "st_trianglePink",
                 "jaw": "st_squarePink",
                 "teeth": "st_squarePink",
                 "tongue": "st_squarePink",
                 "brow": "st_circleOrange",
                 }
    defaultIcon = "st_squarePink"
    selSetSuffix = "sSet"

    def postPolishBuild(self, properties):
        """Executed after the polish stage.

        Useful for building space switching, optimizing the rig, binding asset meta data and
        preparing for the animator.
        """
        # SELECTION SETS --------------------------------------------------------
        # Create All and Body sets -------------------------------
        allSSet = selectionsets.addSSetZooOptions("all_sSet",
                                                  [],
                                                  icon="st_starYellow",
                                                  visibility=True)

        components = list(self.rig.iterComponents())
        autoSets = list()
        for comp in components:
            icon = self.defaultIcon
            ctrlSet = comp.rigLayer().selectionSet()
            sSet = selectionsets.addSelectionSet("_".join([comp.name(), comp.side(), self.selSetSuffix]),
                                                 [ctrlSet.fullPathName()], flattenSets=True)
            # iterate through the iconsDict keys to find the correct icon
            for key in self.iconsDict.keys():
                if key in sSet:
                    icon = self.iconsDict[key]
                    break
            selectionsets.markingMenuSetup(sSet, icon=icon, visibility=True, parentSet=allSSet)
            autoSets.append(sSet)
