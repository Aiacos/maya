import maya.cmds as cmds
import copy

from adn.utils.constants import UiConstants
from adn.utils.path import get_icon_path


ADONISFX_SHELF_BUTTONS = [
    {
        "label": "adnLocator",
        "annotation": "AdonisFX Locator",
        "image": "adn_adonisfx_locator.png",
        "command": "import adn.tools.maya.locators as adn_locators;"
                   "adn_locators.create_locator_logo()"
    },
    {
        "label": "adnPositionLocator",
        "annotation": "AdonisFX Position Locator",
        "image": "adn_point_locator.png",
        "command": "from adn.commands.maya import menu as adn_cmd;"
                   "adn_cmd.create_locator_position_cmd(True)",
        "doubleClickCommand": "from adn.commands.maya import menu as adn_cmd;"
                              "adn_cmd.launch_locator_position_creator_cmd(True)"
    },
    {
        "label": "adnLocatorDistance",
        "annotation": "AdonisFX Distance Locator",
        "image": "adn_distance_locator.png",
        "command": "from adn.commands.maya import menu as adn_cmd;"
                   "adn_cmd.create_locator_distance_cmd(True)",
        "doubleClickCommand": "from adn.commands.maya import menu as adn_cmd;"
                              "adn_cmd.launch_locator_distance_creator_cmd(True)"
    },
    {
        "label": "adnRotationLocator",
        "annotation": "AdonisFX Rotation Locator",
        "image": "adn_angle_locator.png",
        "command": "from adn.commands.maya import menu as adn_cmd;"
                   "adn_cmd.create_locator_rotation_cmd(True)",
        "doubleClickCommand": "from adn.commands.maya import menu as adn_cmd;"
                              "adn_cmd.launch_locator_rotation_creator_cmd(True)"
    },
    {
        "label": "adnSeparator1",
        "isSeparator": True
    },
    {
        "label": "adnSensorPosition",
        "annotation": "AdonisFX Position Sensor",
        "image": "adn_point_sensor.png",
        "command": "from adn.commands.maya import menu as adn_cmd;"
                   "adn_cmd.create_sensor_position_cmd(True)",
        "doubleClickCommand": "from adn.commands.maya import menu as adn_cmd;"
                              "adn_cmd.launch_sensor_position_creator_cmd(True)"
    },
    {
        "label": "adnSensorDistance",
        "annotation": "AdonisFX Distance Sensor",
        "image": "adn_distance_sensor.png",
        "command": "from adn.commands.maya import menu as adn_cmd;"
                   "adn_cmd.create_sensor_distance_cmd(True)",
        "doubleClickCommand": "from adn.commands.maya import menu as adn_cmd;"
                              "adn_cmd.launch_sensor_distance_creator_cmd(True)"
    },
    {
        "label": "adnSensorRotation",
        "annotation": "AdonisFX Rotation Sensor",
        "image": "adn_angle_sensor.png",
        "command": "from adn.commands.maya import menu as adn_cmd;"
                   "adn_cmd.create_sensor_rotation_cmd(True)",
        "doubleClickCommand": "from adn.commands.maya import menu as adn_cmd;"
                              "adn_cmd.launch_sensor_rotation_creator_cmd(True)"
    },
    {
        "label": "adnSeparator2",
        "isSeparator": True
    },
    {
        "label": "adnSimshapeApply",
        "annotation": "AdonisFX Simshape Apply",
        "image": "adn_simshape.png",
        "command": "from adn.commands.maya import menu as adn_cmd;"
                   "adn_cmd.apply_simshape_cmd(True)",
        "doubleClickCommand": "from adn.commands.maya import menu as adn_cmd;"
                              "adn_cmd.launch_simshape_creator_cmd(True)"
    },
    {
        "label": "adnAddCollider",
        "annotation": "AdonisFX Add Simshape Collider",
        "image": "adn_add_collider.png",
        "command": "from adn.commands.maya import menu as adn_cmd;"
                   "adn_cmd.connect_collider_cmd(True)"
    },
    {
        "label": "adnRemoveCollider",
        "annotation": "AdonisFX Remove Simshape Collider",
        "image": "adn_remove_collider.png",
        "command": "from adn.commands.maya import menu as adn_cmd;"
                   "adn_cmd.disconnect_collider_cmd(True)"
    },
    {
        "label": "adnSimshapeLearn",
        "annotation": "AdonisFX Simshape Learn Muscle Patches",
        "image": "adn_learn_muscle_patches.png",
        "command": "from adn.ui.maya import launchers;"
                   "launchers.launch_learn_muscle_patches()"
    },
    {
        "label": "adnSimshapeDebugger",
        "annotation": "AdonisFX Simshape Debugger",
        "image": "adn_simshape_debugger.png",
        "command": "from adn.commands.maya import menu as adn_cmd;"
                   "adn_cmd.simshape_debug_toggle_cmd(True)"
    },
    {
        "label": "adnSeparator3",
        "isSeparator": True
    },
    {
        "label": "adnSkinApply",
        "annotation": "AdonisFX Skin Apply",
        "image": "adn_skin.png",
        "command": "from adn.commands.maya import menu as adn_cmd;"
                   "adn_cmd.apply_skin_cmd(True)",
        "doubleClickCommand": "from adn.commands.maya import menu as adn_cmd;"
                              "adn_cmd.launch_skin_creator_cmd(True)"
    },
    {
        "label": "adnAddSkinTarget",
        "annotation": "AdonisFX Add Skin Target",
        "image": "adn_add_skin_targets.png",
        "command": "from adn.commands.maya import menu as adn_cmd;"
                   "adn_cmd.add_skin_targets(True)"
    },
    {
        "label": "adnRemoveSkinTarget",
        "annotation": "AdonisFX Remove Skin Target",
        "image": "adn_remove_skin_targets.png",
        "command": "from adn.commands.maya import menu as adn_cmd;"
                   "adn_cmd.remove_skin_targets(True)"
    },
    {
        "label": "adnSeparator4",
        "isSeparator": True
    },
    {
        "label": "adnRelaxApply",
        "annotation": "AdonisFX Relax Apply",
        "image": "adn_relax.png",
        "command": "from adn.commands.maya import menu as adn_cmd;"
                   "adn_cmd.apply_relax_cmd(True)",
    },
    {
        "label": "adnSkinMergeApply",
        "annotation": "AdonisFX Skin Merge",
        "image": "adn_skin_merge.png",
        "command": "from adn.ui.maya import launchers as adn_launchers;"
                   "adn_launchers.launch_skin_merge()"
    },
    {
        "label": "adnSeparator5",
        "isSeparator": True
    },
    {
        "label": "adnFatApply",
        "annotation": "AdonisFX Fat Apply",
        "image": "adn_fat.png",
        "command": "from adn.commands.maya import menu as adn_cmd;"
                   "adn_cmd.apply_fat_cmd(True)",
        "doubleClickCommand": "from adn.commands.maya import menu as adn_cmd;"
                              "adn_cmd.launch_fat_creator_cmd(True)"
    },
    {
        "label": "adnSeparator6",
        "isSeparator": True
    },
    {
        "label": "adnRibbonMuscleApply",
        "annotation": "AdonisFX Ribbon Muscle Apply",
        "image": "adn_ribbon_muscle.png",
        "command": "from adn.commands.maya import menu as adn_cmd;"
                   "adn_cmd.apply_ribbon_muscle_cmd(True)",
        "doubleClickCommand": "from adn.commands.maya import menu as adn_cmd;"
                              "adn_cmd.launch_ribbon_muscle_creator_cmd(True)"
    },
    {
        "label": "adnMuscleApply",
        "annotation": "AdonisFX Muscle Apply",
        "image": "adn_muscle.png",
        "command": "from adn.commands.maya import menu as adn_cmd;"
                   "adn_cmd.apply_muscle_cmd(True)",
        "doubleClickCommand": "from adn.commands.maya import menu as adn_cmd;"
                              "adn_cmd.launch_muscle_creator_cmd(True)"
    },
    {
        "label": "adnAddMuscleTarget",
        "annotation": "AdonisFX Add Muscle Target",
        "image": "adn_add_attachment.png",
        "command": "from adn.commands.maya import menu as adn_cmd;"
                   "adn_cmd.add_targets(True)"
    },
    {
        "label": "adnRemoveMuscleTarget",
        "annotation": "AdonisFX Remove Muscle Target",
        "image": "adn_remove_attachment.png",
        "command": "from adn.commands.maya import menu as adn_cmd;"
                   "adn_cmd.remove_targets(True)"
    },
    {
        "label": "adnAddSlideOnSegment",
        "annotation": "AdonisFX Add Slide On Segment",
        "image": "adn_add_sliding_constraint.png",
        "command": "from adn.commands.maya import menu as adn_cmd;"
                   "adn_cmd.add_slide_segment_constraint(True)"
    },
    {
        "label": "adnRemoveSlideOnSegment",
        "annotation": "AdonisFX Remove Slide On Segment",
        "image": "adn_remove_sliding_constraint.png",
        "command": "from adn.commands.maya import menu as adn_cmd;"
                   "adn_cmd.remove_slide_segment_constraint(True)"
    },
    {
        "label": "adnGlueApply",
        "annotation": "AdonisFX Glue Apply",
        "image": "adn_glue.png",
        "command": "from adn.commands.maya import menu as adn_cmd;"
                   "adn_cmd.apply_glue_cmd(True)",
    },
    {
        "label": "adnSeparator7",
        "isSeparator": True
    },
    {
        "label": "adnPaintTool",
        "annotation": "AdonisFX Paint Tool",
        "image": "adn_paint_tool.png",
        "command": "from adn.ui.maya import launchers;"
                   "launchers.launch_paint_tool()"
    },
    {
        "label": "adnInteractivePlayback",
        "annotation": "AdonisFX Interactive Playback",
        "image": "adn_interactive_playback.png",
        "command": "from adn.commands.maya import scene;"
                   "scene.play_interactive()"
    }
]


def clear_shelf():
    """Clears the AdonisFX shelf by removing all existing buttons."""
    if not cmds.shelfLayout(UiConstants.PLUGIN_NAME, exists=True):
        return
    # Clean shelf if it exists
    old_buttons = cmds.shelfLayout(UiConstants.PLUGIN_NAME,
                                   query=True,
                                   childArray=True) or []
    for old_button in old_buttons:
        cmds.deleteUI(old_button)


def load_shelf():
    """Loads AdonisFX shelf dynamically and adds the buttons defined in the
    ADONISFX_SHELF_BUTTONS dictionary. If the shelf already exists, it
    gets cleared by removing all existing buttons, and then it gets filled
    with the buttons defined in that dictionary."""
    if cmds.shelfLayout(UiConstants.PLUGIN_NAME, exists=True):
        clear_shelf()
    else:
        # Create shelf if it does not exist
        cmds.shelfLayout(UiConstants.PLUGIN_NAME, parent="ShelfLayout")

    # Double check    
    if not cmds.shelfLayout(UiConstants.PLUGIN_NAME, exists=True):
        print("{0} Failed to load {1} shelf".format(UiConstants.ERROR_PREFIX,
                                                    UiConstants.PLUGIN_NAME))
        return
        
    # Set the new shelf as parent to any button created from now on
    cmds.setParent(UiConstants.PLUGIN_NAME)

    for button in ADONISFX_SHELF_BUTTONS:
        if button.get("isSeparator", False):
            cmds.separator(button["label"],
                           width=8,
                           height=35,
                           style="shelf",
                           horizontal=False)
        else:
            data = copy.deepcopy(button)
            data["image"] = get_icon_path(data["image"])
            data["width"] = 35
            data["height"] = 34
            data["sourceType"] = "python"
            cmds.shelfButton(data["label"], **data)


def unload_shelf():
    """Unloads AdonisFX shelf, including the clearing of all the shelf buttons
    and the removal of the shelf tab itself."""
    if not cmds.shelfLayout(UiConstants.PLUGIN_NAME, exists=True):
        return
    clear_shelf()
    cmds.deleteUI(UiConstants.PLUGIN_NAME)
