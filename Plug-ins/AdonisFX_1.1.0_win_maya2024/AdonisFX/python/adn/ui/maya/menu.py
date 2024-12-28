import maya.cmds as cmds

from adn.utils import path
from adn.utils.constants import UiConstants
from adn.ui.maya.window import main_window_name
from adn.commands.maya import menu as cmd_wrapper


""" AdonisFX Menu structure """
# AdonisFX:
# 1. Create -----
#   1.1 Locators >
#     1.1.1 Position [Opt. box]
#     1.1.2 Distance [Opt. box]
#     1.1.3 Rotation [Opt. box]
#   1.2 Sensors >
#     1.2.1 Position [Opt. box]
#     1.2.2 Distance [Opt. box]
#     1.2.3 Rotation [Opt. box]
#   1.3 Nodes >
#     1.3.1 Edge Evaluator  
#   1.4 Deformers >
#     1.4.1 Skin Merge  
#   1.5 Solvers >
#     1.5.1 Simshape      [Opt. box]
#     1.5.2 Skin          [Opt. box]
#     1.5.3 Ribbon Muscle [Opt. box]
#     1.5.4 Muscle Muscle [Opt. box]
# 2. Edit ------
#   2.1 Sensors >
#     2.1.1 Connect Output
#   2.2 Deformers >
#     2.2.1 Edit Skin Merge
#   2.3 Simshape >
#     2.3.1 Learn Muscle Patches UI
#     2.3.2 Debugger
#     ------------
#     2.3.3 Add Collider
#     2.3.4 Remove Collider
#     2.3.5 Add Rest Collider
#     2.3.6 Remove Rest Collider
#     ------------
#     2.3.7 Add Rest Mesh
#     2.3.8 Remove Rest Mesh
#     2.3.9 Add Deform Mesh
#     2.3.10 Remove Deform Mesh
#     2.3.11 Add Anim Mesh
#     2.3.12 Remove Anim Mesh
#     ------------
#     2.3.13 Connect Edge Evaluator
#     2.3.14 Disconnect Edge Evaluator
#   2.4 Muscle >
#     2.4.1 Draw Fibers
#     2.4.2 Hide Fibers
#     2.4.3 Add Attachments
#     2.4.4 Remove Attachments
#     2.4.5 Add Slide On Segment Constraint
#     2.4.6 Remove Slide On Segment Constraint
#   2.5 Debug >
#     2.5.1 Refresh Debugger
# 3. Tools ------
#   3.1 Import
#   3.2 Export
#   3.3 Paint Tool
#   3.4 Interactive Playback
# 4. Licensing ------
#   4.1 Activate License
# 5. Help ------
#   5.1 Documentation
#   5.2 Tutorials
#   5.3 About


def load_create_locators_menu(parent):
    """Function to populate all menu items related to actions with AdonisFX locators

    Args:
        parent (str): name of the parent menu item.
    """
    # Submenu 1.1
    locators_item = cmds.menuItem("locators_menu_item",
                                  subMenu=True,
                                  label="Locators",
                                  parent=parent)
    cmds.menuItem("create_loc_position_menu_item",
                  label="Position",
                  annotation="Create AdnLocatorPosition to visualize the "
                             "velocity and acceleration of a single transform node",
                  parent=locators_item,
                  command=cmd_wrapper.create_locator_position_cmd,
                  image=path.get_icon_path("adn_point_locator.png"))
    cmds.menuItem("create_loc_position_option_box",
                  optionBox=True,
                  command=cmd_wrapper.launch_locator_position_creator_cmd)
    cmds.menuItem("create_loc_distance_menu_item",
                  label="Distance",
                  annotation="Create AdnLocatorDistance to visualize the relative distance, "
                             "velocity and acceleration between two transform nodes",
                  parent=locators_item,
                  command=cmd_wrapper.create_locator_distance_cmd,
                  image=path.get_icon_path("adn_distance_locator.png"))
    cmds.menuItem("create_loc_distance_option_box",
                  optionBox=True,
                  command=cmd_wrapper.launch_locator_distance_creator_cmd)
    cmds.menuItem("create_loc_rotation_menu_item",
                  label="Rotation",
                  annotation="Create AdnLocatorRotation to visualize the angle, angular velocity "
                             "and angular acceleration between three transform nodes",
                  parent=locators_item,
                  command=cmd_wrapper.create_locator_rotation_cmd,
                  image=path.get_icon_path("adn_angle_locator.png"))
    cmds.menuItem("create_loc_rotation_option_box",
                  optionBox=True,
                  command=cmd_wrapper.launch_locator_rotation_creator_cmd)


def load_create_sensors_menu(parent):
    """Function to populate all menu items related to actions with AdonisFX sensors

    Args:
        parent (str): name of the parent menu item.
    """
    # Submenu 1.2
    sensors_item = cmds.menuItem("sensors_menu_item",
                                 subMenu=True,
                                 label="Sensors",
                                 parent=parent)
    cmds.menuItem("create_sen_position_menu_item",
                  label="Position",
                  annotation="Create AdnSensorPosition to compute and output the "
                             "velocity and acceleration of a single transform node",
                  parent=sensors_item,
                  command=cmd_wrapper.create_sensor_position_cmd,
                  image=path.get_icon_path("adn_point_sensor.png"))
    cmds.menuItem("create_sen_position_option_box",
                  optionBox=True,
                  command=cmd_wrapper.launch_sensor_position_creator_cmd)
    cmds.menuItem("create_sen_distance_menu_item",
                  label="Distance",
                  annotation="Create AdnSensorDistance to compute and output the relative distance, "
                             "velocity and acceleration between two transform nodes",
                  parent=sensors_item,
                  command=cmd_wrapper.create_sensor_distance_cmd,
                  image=path.get_icon_path("adn_distance_sensor.png"))
    cmds.menuItem("create_sen_distance_option_box",
                  optionBox=True,
                  command=cmd_wrapper.launch_sensor_distance_creator_cmd)
    cmds.menuItem("create_sen_rotation_menu_item",
                  label="Rotation",
                  annotation="Create AdnLocatorRotation to compute the angle, angular velocity "
                             "and angular acceleration represented by three transform nodes",
                  parent=sensors_item,
                  command=cmd_wrapper.create_sensor_rotation_cmd,
                  image=path.get_icon_path("adn_angle_sensor.png"))
    cmds.menuItem("create_sen_rotation_option_box",
                  optionBox=True,
                  command=cmd_wrapper.launch_sensor_rotation_creator_cmd)


def load_create_nodes_menu(parent):
    """Function to populate all menu items related to actions with AdonisFX evaluator nodes

    Args:
        parent (str): name of the parent menu item.
    """
    # Submenu 1.3
    evaluators_item = cmds.menuItem("nodes_menu_item",
                                    subMenu=True,
                                    label="Nodes",
                                    parent=parent)
    cmds.menuItem("create_edge_evaluator_menu_item",
                  label="Edge Evaluator",
                  annotation="Create an AdnEdgeEvaluator node to calculate the "
                             "edge compression map of a mesh",
                  parent=evaluators_item,
                  command=cmd_wrapper.create_edge_evaluator_cmd,
                  image=path.get_icon_path("adn_edge_evaluator.png"))


def load_create_deformers_menu(parent):
    """Function to populate all menu items related to actions with AdonisFX deformers.

    Args:
        parent (str): name of the parent menu item.
    """
    # Submenu 1.4
    deformers_menu_item = cmds.menuItem("deformers_menu_item",
                                        subMenu=True,
                                        label="Deformers",
                                        parent=parent)
    cmds.menuItem("skin_merge_menu_item",
                  label="Skin Merge",
                  annotation="Create a Skin Merge deformer to blend the results from "
                             "animation and simulation into a final mesh",
                  parent=deformers_menu_item,
                  command=cmd_wrapper.launch_skin_merge_cmd,
                  image=path.get_icon_path("adn_skin_merge.png"))


def load_create_solvers_menu(parent):
    """Function to populate all menu items related to actions with AdonisFX solvers.

    Args:
        parent (str): name of the parent menu item.
    """
    # Submenu 1.5
    solvers_menu_item = cmds.menuItem("solvers_menu_item",
                                      subMenu=True,
                                      label="Solvers",
                                      parent=parent)
    cmds.menuItem("create_simshape_menu_item",
                  label="Simshape",
                  annotation="Create an AdnSimshape deformer for facial simulation with "
                             "the ability to simulate muscle activations",
                  parent=solvers_menu_item,
                  command=cmd_wrapper.apply_simshape_cmd,
                  image=path.get_icon_path("adn_simshape.png"))
    cmds.menuItem("create_simshape_option_box",
                  optionBox=True,
                  command=cmd_wrapper.launch_simshape_creator_cmd)
    cmds.menuItem("create_skin_menu_item",
                  label="Skin",
                  annotation="Create an AdnSkin deformer to simulate a skin tissue and "
                             "produce realistic effects like wrinkles",
                  parent=solvers_menu_item,
                  command=cmd_wrapper.apply_skin_cmd,
                  image=path.get_icon_path("adn_skin.png"))
    cmds.menuItem("create_skin_option_box",
                  optionBox=True,
                  command=cmd_wrapper.launch_skin_creator_cmd)
    cmds.menuItem("create_ribbon_menu_item",
                  label="Ribbon Muscle",
                  annotation="Create an AdnRibbonMuscle deformer to simulate a planar "
                             "geometry with muscle dynamics like fibers activation",
                  parent=solvers_menu_item,
                  command=cmd_wrapper.apply_ribbon_muscle_cmd,
                  image=path.get_icon_path("adn_ribbon_muscle.png"))
    cmds.menuItem("create_ribbon_option_box",
                  optionBox=True,
                  command=cmd_wrapper.launch_ribbon_muscle_creator_cmd)
    cmds.menuItem("create_muscle_menu_item",
                  label="Muscle",
                  annotation="Create an AdnMuscle deformer to simulate a geometry "
                             "with muscle dynamics like fiber activation and volume gain",
                  parent=solvers_menu_item,
                  command=cmd_wrapper.apply_muscle_cmd,
                  image=path.get_icon_path("adn_muscle.png"))
    cmds.menuItem("create_muscle_option_box",
                  optionBox=True,
                  command=cmd_wrapper.launch_muscle_creator_cmd)


def load_edit_sensors_menu(parent):
    """Menu items that represents sensor additional actions apart from the
    creation. They hang from the parent menu.

    Args:
        parent (str): name of the parent menu item.
    """
    # Submenu 2.1
    edit_sensor_item = cmds.menuItem("edit_sensor_menu_item",
                                     subMenu=True,
                                     label="Sensors",
                                     parent=parent)
    cmds.menuItem("connect_sensor_menu_item",
                  label="Connection Editor",
                  annotation="Launch the Sensors Connection Editor UI to connect the output "
                             "from AdonisFX Sensors and Locators to other nodes like AdonisFX Muscles",
                  parent=edit_sensor_item,
                  command=cmd_wrapper.launch_sensor_connection_editor_cmd)


def load_edit_deformers_menu(parent):
    """Menu items that represents deformers additional actions
    apart from the creation. They hang from the parent menu.

    Args:
        parent (str): name of the parent menu item.
    """
    # Submenu 2.2
    edit_deformers_item = cmds.menuItem("edit_skin_menu_item",
                                        subMenu=True,
                                        label="Deformers",
                                        parent=parent)
    cmds.menuItem("edit_skin_merge_menu_item",
                  label="Edit Skin Merge",
                  annotation="Open the Skin Merge UI to edit the Skin Merge configuration. "
                             "Select the final mesh with the Skin Merge deformer.",
                  parent=edit_deformers_item,
                  command=cmd_wrapper.launch_skin_merge_edit_cmd)


def load_edit_simshape_menu(parent):
    """Menu items that represents simshape additional actions (ML, debug, adding/removing colliders) 
    apart from the creation. They hang from the parent menu.

    Args:
        parent (str): name of the parent menu item.
    """
    # Submenu 2.3
    edit_simshape_item = cmds.menuItem("simshape_menu_item",
                                       subMenu=True,
                                       label="Simshape",
                                       parent=parent)
    cmds.menuItem("ml_simshape_menu_item",
                  label="Learn Muscle Patches UI",
                  annotation="Launch Muscle Patches UI to generate an AdonisFX Muscle Patches file",
                  parent=edit_simshape_item,
                  command=cmd_wrapper.launch_learn_muscle_patches_cmd,
                  image=path.get_icon_path("adn_learn_muscle_patches.png"))
    cmds.menuItem("debug_simshape_menu_item",
                  label="Activations Debugger",
                  annotation="Toggle visualization of muscle patches activation on the selected "
                             "AdnSimshape deformer",
                  parent=edit_simshape_item,
                  command=cmd_wrapper.simshape_debug_toggle_cmd,
                  image=path.get_icon_path("adn_simshape_debugger.png"))

    cmds.menuItem(parent=edit_simshape_item, divider=True)

    cmds.menuItem("add_coll_simshape_menu_item",
                  label="Add Collider",
                  annotation="Add a collider to an AdnSimshape deformer. First select the geometry to "
                             "connect as collider, then the geometry with the deformer applied",
                  parent=edit_simshape_item,
                  command=cmd_wrapper.connect_collider_cmd,
                  image=path.get_icon_path("adn_add_collider.png"))
    cmds.menuItem("remove_coll_simshape_menu_item",
                  label="Remove Collider",
                  annotation="Remove the connection to selected collider mesh from the selected AdnSimshape deformer",
                  parent=edit_simshape_item,
                  command=cmd_wrapper.disconnect_collider_cmd,
                  image=path.get_icon_path("adn_remove_collider.png"))
    cmds.menuItem("add_rest_coll_simshape_menu_item",
                  label="Add Rest Collider",
                  annotation="Add a rest collider to an AdnSimshape deformer. First select the geometry to "
                             "connect as rest collider, then the geometry with the deformer applied",
                  parent=edit_simshape_item,
                  command=cmd_wrapper.connect_rest_collider_cmd)
    cmds.menuItem("remove_rest_coll_simshape_menu_item",
                  label="Remove Rest Collider",
                  annotation="Remove the connection to the rest collider mesh from the AdnSimshape deformer. "
                             "First select the collider mesh, then the geometry with the deformer applied",
                  parent=edit_simshape_item,
                  command=cmd_wrapper.disconnect_rest_collider_cmd)

    cmds.menuItem(parent=edit_simshape_item, divider=True)

    cmds.menuItem("add_rest_mesh_simshape_menu_item",
                  label="Add Rest Mesh",
                  annotation="Add a rest mesh to an AdnSimshape deformer. First select the "
                             "rest mesh to connect, then the geometry with the deformer applied",
                  parent=edit_simshape_item,
                  command=cmd_wrapper.add_rest_mesh_cmd)
    cmds.menuItem("remove_rest_mesh_simshape_menu_item",
                  label="Remove Rest Mesh",
                  annotation="Remove the input connection to the rest mesh from the AdnSimshape "
                             "deformer applied to the selected geometry",
                  parent=edit_simshape_item,
                  command=cmd_wrapper.remove_rest_mesh_cmd)
    cmds.menuItem("add_deform_mesh_simshape_menu_item",
                  label="Add Deform Mesh",
                  annotation="Add a deformed mesh to an AdnSimshape deformer. First select the "
                             "deformed mesh to connect, then the geometry with the deformer applied",
                  parent=edit_simshape_item,
                  command=cmd_wrapper.add_deform_mesh_cmd)
    cmds.menuItem("remove_deform_mesh_simshape_menu_item",
                  label="Remove Deform Mesh",
                  annotation="Remove the input connection to the deformed mesh from the AdnSimshape "
                             "deformer applied to the selected geometry",
                  parent=edit_simshape_item,
                  command=cmd_wrapper.remove_deform_mesh_cmd)
    cmds.menuItem("add_anim_mesh_simshape_menu_item",
                  label="Add Anim Mesh",
                  annotation="Add an animated mesh to an AdnSimshape deformer. First select the "
                             "animated mesh to connect, then the geometry with the deformer applied",
                  parent=edit_simshape_item,
                  command=cmd_wrapper.add_anim_mesh_cmd)
    cmds.menuItem("remove_anim_mesh_simshape_menu_item",
                  label="Remove Anim Mesh",
                  annotation="Remove the input connection to the animated mesh from the AdnSimshape "
                             "deformer applied to the selected geometry",
                  parent=edit_simshape_item,
                  command=cmd_wrapper.remove_anim_mesh_cmd)

    cmds.menuItem(parent=edit_simshape_item, divider=True)

    cmds.menuItem("connect_activations_simshape_menu_item",
                  label="Connect Activations Plug",
                  annotation="Connect an AdnEdgeEvaluator node to an AdnSimshape deformer to drive the activations map. "
                             "First select the evaluator, then the geometry with the deformer applied.",
                  parent=edit_simshape_item,
                  command=cmd_wrapper.connect_simshape_activations_cmd)
    cmds.menuItem("disconnect_activations_simshape_menu_item",
                  label="Disconnect Activations Plug",
                  annotation="Disconnect an AdnEdgeEvaluator node from an AdnSimshape deformer. "
                             "First select the evaluator, then the geometry with the deformer applied",
                  parent=edit_simshape_item,
                  command=cmd_wrapper.disconnect_simshape_activations_cmd)


def load_edit_muscle_menu(parent):
    """Menu items that represents muscle additional actions apart from the
    creation. They hang from the parent menu.

    Args:
        parent (str): name of the parent menu item.
    """
    # Submenu 2.4
    edit_muscle_item = cmds.menuItem("muscle_menu_item",
                                     subMenu=True,
                                     label="Muscle",
                                     parent=parent)
    cmds.menuItem("add_targets_menu_item",
                  label="Add Targets",
                  annotation="Add targets to an AdonisFX muscle deformer. First select the "
                             "objects to connect as attachments, then select the geometry with an "
                             "AdonisFX muscle deformer applied",
                  parent=edit_muscle_item,
                  image=path.get_icon_path("adn_add_attachment.png"),
                  command=cmd_wrapper.add_targets)
    cmds.menuItem("remove_targets_menu_item",
                  label="Remove Targets",
                  annotation="Remove targets from an AdonisFX muscle deformer. First select the "
                             "attachments to remove, then select the geometry with an AdonisFX muscle deformer applied. "
                             "To clear all the attachments, select the geometry only",
                  parent=edit_muscle_item,
                  image=path.get_icon_path("adn_remove_attachment.png"),
                  command=cmd_wrapper.remove_targets)
    cmds.menuItem("add_slide_segment_constraint_menu_item",
                  label="Add Slide On Segment Constraint",
                  annotation="Add segment for an AdonisFX muscle deformer to slide on. First select the root and tip "
                             "anchors of the segment to slide on in order. Then, select the geometry with an AdonisFX "
                             "muscle deformer applied",
                  parent=edit_muscle_item,
                  image=path.get_icon_path("adn_add_sliding_constraint.png"),
                  command=cmd_wrapper.add_slide_segment_constraint)
    cmds.menuItem("remove_slide_segment_constraint_menu_item",
                  label="Remove Slide On Segment Constraint",
                  annotation="Remove segment for an AdonisFX muscle deformer to slide on. Select only the mesh from "
                             "which to remove the segment constraint",
                  parent=edit_muscle_item,
                  image=path.get_icon_path("adn_remove_sliding_constraint.png"),
                  command=cmd_wrapper.remove_slide_segment_constraint)

    cmds.menuItem(parent=edit_muscle_item, divider=True)

    cmds.menuItem("show_all_fibers_menu_item",
                  label="Draw Fibers",
                  annotation="Enable the visualization of the fibers for all AdonisFX muscle deformers in the scene",
                  parent=edit_muscle_item,
                  command=cmd_wrapper.show_all_fibers)
    cmds.menuItem("hide_all_fibers_menu_item",
                  label="Hide Fibers",
                  annotation="Disable the visualization of the fibers for all AdonisFX muscle deformers in the scene",
                  parent=edit_muscle_item,
                  command=cmd_wrapper.hide_all_fibers)


def load_edit_debug_menu(parent):
    """Menu items with manipulation and maintenance utilities for the AdonisFX debugging system.

    Args:
        parent (str): name of the parent menu item.
    """
    # Submenu 2.5
    edit_debug_item = cmds.menuItem("debug_menu_item",
                                     subMenu=True,
                                     label="Debug",
                                     parent=parent)
    cmds.menuItem("refresh_debug_menu_item",
                  label="Refresh Debugger",
                  annotation="Refresh the graph for debugging purposes by making sure the AdnDataNode and AndDebugLocator"
                             " exist in the scene and are properly connected.",
                  parent=edit_debug_item,
                  command=cmd_wrapper.refresh_debug_graph_cmd)

def load_item_utils_menu(parent):
    """Menu items that represent tools and utils used at AdonisFX.

    Args:
        parent (str): name of the parent menu item.
    """
    cmds.menuItem(parent=parent, 
                  divider=True,
                  dividerLabel="Tools")
    cmds.menuItem("importer_menu_item",
                  label="Import",
                  parent=parent,
                  command=cmd_wrapper.launch_importer_cmd,
                  image=path.get_icon_path("adn_importer.png"))
    cmds.menuItem("exporter_menu_item",
                  label="Export",
                  annotation="Launch Export Tool UI to make a customizable export of the AdonisFX deformers "
                             "selected within an AdonisFX Asset Definition file",
                  parent=parent,
                  command=cmd_wrapper.launch_exporter_cmd,
                  image=path.get_icon_path("adn_exporter.png"))
    cmds.menuItem("paint_menu_item",
                  label="Paint Tool",
                  annotation="Launch AdonisFX Paint Tool UI to modify the weights map of deformer paintable attributes",
                  parent=parent,
                  command=cmd_wrapper.launch_paint_tool_cmd,
                  image=path.get_icon_path("adn_paint_tool.png"))
    cmds.menuItem("playback_menu_item",
                  label="Interactive Playback",
                  annotation="Enable interactive playback",
                  parent=parent,
                  command=cmd_wrapper.play_interactive_cmd,
                  image=path.get_icon_path("adn_interactive_playback.png"))


def load_create_menu(parent):
    """Menu that arranges all menus and menu items related to AdonisFX
    creation.

    Args:
        parent (str): name of the parent menu item.
    """
    cmds.menuItem(parent=parent, 
                  divider=True,
                  dividerLabel="Create")
    load_create_locators_menu(parent)
    load_create_sensors_menu(parent)
    load_create_nodes_menu(parent)
    load_create_deformers_menu(parent)
    load_create_solvers_menu(parent)


def load_edit_menu(parent):
    """Menu that arranges all menus and menu items related to AdonisFX
    edit operations.

    Args:
        parent (str): name of the parent menu item.
    """
    cmds.menuItem(parent=parent, 
                  divider=True,
                  dividerLabel="Edit")
    load_edit_sensors_menu(parent)
    load_edit_deformers_menu(parent)
    load_edit_simshape_menu(parent)
    load_edit_muscle_menu(parent)
    load_edit_debug_menu(parent)


def load_licensing_utils_menu(parent):
    """Menu that arranges all menu items related to the licensing system.

    Args:
        parent (str): name of the parent menu item.
    """
    cmds.menuItem(parent=parent,
                  divider=True,
                  dividerLabel="License")
    # 4.1 Activate License
    cmds.menuItem("activate_license_menu_item",
                  label="Activate License",
                  annotation="Launch a dialog to activate the license or the trial period",
                  parent=parent,
                  command=cmd_wrapper.activate_license_cmd)


def load_help_menu(parent):
    """Menu that encapsulates all help operations.

    Args:
        parent (str): name of the parent menu item.
    """
    cmds.menuItem(parent=parent,
                  divider=True,
                  dividerLabel="Help")
    cmds.menuItem("documentation_menu_item",
                  label="Documentation",
                  annotation="Go to AdonisFX technical documentation",
                  parent=parent,
                  command=cmd_wrapper.go_to_documentation_cmd)
    cmds.menuItem("tutorials_menu_item",
                  label="Tutorials",
                  annotation="Go to AdonisFX tutorials on YouTube",
                  parent=parent,
                  command=cmd_wrapper.go_to_tutorials_cmd)
    cmds.menuItem("about_menu_item",
                  label="About",
                  annotation="Launch the about dialog",
                  parent=parent,
                  command=cmd_wrapper.launch_about_cmd)


def load_menu():
    """AdonisFX maya main menu load. Called on plugin initialization.
    Creates the main menu (in case it exists, replaces it) and calls the
    creation of all the menu items and submenus.
    """
    # Clean and remove root menu if exists
    if cmds.menu(UiConstants.ROOT_MENU_NAME, exists=True):
        cmds.menu(UiConstants.ROOT_MENU_NAME, edit=True, deleteAllItems=True)
        cmds.deleteUI(UiConstants.ROOT_MENU_NAME)

    # AdonisFX root main menu
    root_menu = cmds.menu(UiConstants.ROOT_MENU_NAME,
                          parent=main_window_name(),
                          tearOff=True,
                          label=UiConstants.PLUGIN_NAME)
    
    # 1. Create
    load_create_menu(root_menu)

    # 2. Edit
    load_edit_menu(root_menu)

    # 3. Tools/Utils
    load_item_utils_menu(root_menu)

    # 4. License
    load_licensing_utils_menu(root_menu)

    # 5. Help
    load_help_menu(root_menu)


def unload_menu():
    """AdonisFX maya main menu unload. Called on plugin unitialization.
    Remove the AdonisFX menu in case it does exist.
    """
    # Clean and remove root menu if exists
    if cmds.menu(UiConstants.ROOT_MENU_NAME, exists=True):
        cmds.menu(UiConstants.ROOT_MENU_NAME, edit=True, deleteAllItems=True)
        cmds.deleteUI(UiConstants.ROOT_MENU_NAME)
