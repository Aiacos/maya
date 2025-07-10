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
#     1.3.2 Activation
#   1.4 Deformers >
#     1.4.1 Skin Merge  
#   1.5 Solvers >
#     1.5.1 Simshape      [Opt. box]
#     1.5.2 Skin          [Opt. box]
#     1.5.3 Fat           [Opt. box]
#     1.5.4 Ribbon Muscle [Opt. box]
#     1.5.5 Muscle Muscle [Opt. box]
#     1.5.6 Glue
# 2. Edit ------
#   2.1 Sensors >
#     2.1.1 Connect Output
#   2.2 Activation >
#     2.2.1 Remove Inputs
#   2.3 Deformers >
#     2.3.1 Edit Skin Merge
#   2.4 Simshape >
#     2.4.1 Learn Muscle Patches UI
#     2.4.2 Debugger
#     ------------
#     2.4.3 Add Collider
#     2.4.4 Remove Collider
#     2.4.5 Add Rest Collider
#     2.4.6 Remove Rest Collider
#     ------------
#     2.4.7 Add Rest Mesh
#     2.4.8 Remove Rest Mesh
#     2.4.9 Add Deform Mesh
#     2.4.10 Remove Deform Mesh
#     2.4.11 Add Anim Mesh
#     2.4.12 Remove Anim Mesh
#     ------------
#     2.4.13 Connect Edge Evaluator
#     2.4.14 Disconnect Edge Evaluator
#   2.5 Skin >
#     2.5.1 Add Targets
#     2.5.2 Remove Targets
#   2.6 Fat >
#     2.6.1 Add Base Mesh
#     2.6.2 Remove Base Mesh
#   2.7 Muscle >
#     2.7.1 Draw Fibers
#     2.7.2 Hide Fibers
#     2.7.3 Add Attachments
#     2.7.4 Remove Attachments
#     2.7.5 Add Slide On Segment Constraint
#     2.7.6 Remove Slide On Segment Constraint
#   2.8 Glue >
#     2.8.1 Add Inputs
#     2.8.2 Remove Inputs
#   2.9 Debug >
#     2.9.1 Refresh Debugger
# 3. Tools ------
#   3.1 Utils >
#       3.1.1 Upgrade Deprecated Nodes
#       3.1.2 Clear
#   3.2 Mirror
#   3.3 Turbo
#   3.4 Paint Tool
#   3.5 Interactive Playback
# 4. I/O
#   4.1 Import (beta)
#   4.2 Export (beta)
# 5. Licensing ------
#   5.1 Activate License
# 6. Help ------
#   6.1 Documentation
#   6.2 Tutorials
#   6.3 About


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
    cmds.menuItem("create_activation_node_menu_item",
                  label="Activation",
                  annotation="Create an AdnActivation node to merge values "
                             "from multiple sensors into a single final value",
                  parent=evaluators_item,
                  command=cmd_wrapper.create_activation_node_cmd)


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
    cmds.menuItem("relax_menu_item",
                  label="Relax",
                  annotation="Create a Relax deformer to remove and smooth "
                             "out creases on the surface",
                  parent=deformers_menu_item,
                  command=cmd_wrapper.apply_relax_cmd,
                  image=path.get_icon_path("adn_relax.png"))
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
    cmds.menuItem("create_fat_menu_item",
                  label="Fat",
                  annotation="Create an AdnFat deformer to simulate a fat tissue "
                             "and produce dynamics like jiggle",
                  parent=solvers_menu_item,
                  command=cmd_wrapper.apply_fat_cmd,
                  image=path.get_icon_path("adn_fat.png"))
    cmds.menuItem("create_fat_option_box",
                  optionBox=True,
                  command=cmd_wrapper.launch_fat_creator_cmd)
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
    cmds.menuItem("create_glue_menu_item",
                  label="Glue",
                  annotation="Create an AdnGlue node to glue geometries to each other to "
                             "make them behave more compact",
                  parent=solvers_menu_item,
                  command=cmd_wrapper.apply_glue_cmd,
                  image=path.get_icon_path("adn_glue.png"))


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


def load_edit_activation_menu(parent):
    """Menu items that represents AdnActivation additional actions apart from the
    creation. They hang from the parent menu.

    Args:
        parent (str): name of the parent menu item.
    """
    # Submenu 2.2
    edit_activation_item = cmds.menuItem("edit_activation_menu_item",
                                         subMenu=True,
                                         label="Activation",
                                         parent=parent)
    cmds.menuItem("remove_activation_input_menu_item",
                  label="Remove Inputs",
                  annotation="Remove inputs from an AdnActivation node. First select the "
                             "locators to remove, then select the AdnActivation node. "
                             "To remove all the inputs, select the AdnActivation node only.",
                  parent=edit_activation_item,
                  command=cmd_wrapper.remove_activation_inputs_cmd)


def load_edit_deformers_menu(parent):
    """Menu items that represents deformers additional actions
    apart from the creation. They hang from the parent menu.

    Args:
        parent (str): name of the parent menu item.
    """
    # Submenu 2.3
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
    # Submenu 2.4
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


def load_edit_skin_menu(parent):
    """Menu items that represents AdnSkin additional actions apart from the
    creation. They hang from the parent menu.

    Args:
        parent (str): name of the parent menu item.
    """
    # Submenu 2.5
    edit_muscle_item = cmds.menuItem("skin_menu_item",
                                     subMenu=True,
                                     label="Skin",
                                     parent=parent)
    cmds.menuItem("add_skin_targets_menu_item",
                  label="Add Targets",
                  annotation="Add targets to an AdonisFX skin deformer. First select the "
                             "objects to connect as targets, then select the geometry with an "
                             "AdonisFX skin deformer applied",
                  parent=edit_muscle_item,
                  image=path.get_icon_path("adn_add_skin_targets.png"),
                  command=cmd_wrapper.add_skin_targets)
    cmds.menuItem("remove_skin_targets_menu_item",
                  label="Remove Targets",
                  annotation="Remove targets from an AdonisFX skin deformer. First select the "
                             "targets to remove, then select the geometry with an AdonisFX skin deformer applied. "
                             "To clear all the targets, select the geometry only",
                  parent=edit_muscle_item,
                  image=path.get_icon_path("adn_remove_skin_targets.png"),
                  command=cmd_wrapper.remove_skin_targets)


def load_edit_fat_menu(parent):
    """Menu items that represents AdnFat additional actions apart from the
    creation. They hang from the parent menu.

    Args:
        parent (str): name of the parent menu item.
    """
    # Submenu 2.6
    edit_fat_item = cmds.menuItem("fat_menu_item",
                                  subMenu=True,
                                  label="Fat",
                                  parent=parent)
    cmds.menuItem("add_fat_base_mesh_menu_item",
                  label="Add Base Mesh",
                  annotation="Add a base mesh to an AdonisFX fat deformer. First select the "
                             "mesh to connect as base mesh, then select the geometry with an "
                             "AdonisFX fat deformer applied",
                  parent=edit_fat_item,
                  command=cmd_wrapper.add_fat_base_mesh)
    cmds.menuItem("remove_fat_base_mesh_menu_item",
                  label="Remove Base Mesh",
                  annotation="Remove the base mesh from the selected AdonisFX fat deformer",
                  parent=edit_fat_item,
                  command=cmd_wrapper.remove_fat_base_mesh)


def load_edit_muscle_menu(parent):
    """Menu items that represents muscle additional actions apart from the
    creation. They hang from the parent menu.

    Args:
        parent (str): name of the parent menu item.
    """
    # Submenu 2.7
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


def load_edit_glue_menu(parent):
    """Menu items that represents AdnGlue additional actions apart from the
    creation. They hang from the parent menu.

    Args:
        parent (str): name of the parent menu item.
    """
    # Submenu 2.8
    edit_glue_item = cmds.menuItem("glue_menu_item",
                                   subMenu=True,
                                   label="Glue",
                                   parent=parent)
    cmds.menuItem("add_glue_inputs_menu_item",
                  label="Add Inputs",
                  annotation="Add inputs to an AdonisFX glue node. First select the "
                             "meshes to connect as inputs, then select the geometry with an "
                             "AdonisFX glue node applied",
                  parent=edit_glue_item,
                  command=cmd_wrapper.add_glue_inputs)
    cmds.menuItem("remove_glue_inputs_menu_item",
                  label="Remove Inputs",
                  annotation="Remove inputs from an AdonisFX skin deformer. First select the "
                             "inputs to remove, then select the geometry with an AdonisFX glue node applied. "
                             "To clear all the inputs, select the geometry only",
                  parent=edit_glue_item,
                  command=cmd_wrapper.remove_glue_inputs)


def load_edit_debug_menu(parent):
    """Menu items with manipulation and maintenance utilities for the AdonisFX debugging system.

    Args:
        parent (str): name of the parent menu item.
    """
    # Submenu 2.9
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


def load_utils_menu(parent):
    """Menu items with secondary utilities.

    Args:
        parent (str): name of the parent menu item.
    """
    # Submenu 3.1
    utils_item = cmds.menuItem("utils_menu_item",
                               subMenu=True,
                               label="Utils",
                               parent=parent)
    cmds.menuItem("upgrade_deprecated_nodes_menu_item",
                  label="Upgrade Deprecated Nodes",
                  annotation="Upgrade all deprecated nodes making sure that "
                             "the scene still works properly. For example, "
                             "all AdnWeightsDisplayNodes will be deleted.",
                  parent=utils_item,
                  command=cmd_wrapper.upgrade_deprecated_nodes_cmd)
    cmds.menuItem("clear_menu_item",
                  label="Clear",
                  annotation="Remove all AdonisFX nodes from the scene.",
                  parent=utils_item,
                  command=cmd_wrapper.clear_util_cmd)


def load_item_utils_menu(parent):
    """Menu items that represent tools and utils used at AdonisFX.

    Args:
        parent (str): name of the parent menu item.
    """
    cmds.menuItem(parent=parent, 
                  divider=True,
                  dividerLabel="Tools")

    # Other utils
    load_utils_menu(parent)

    cmds.menuItem("mirror_menu_item",
                  label="Mirror",
                  annotation="Launch Mirror Tool UI to mirror the muscle setup from one side to the other.",
                  parent=parent,
                  command=cmd_wrapper.launch_mirror_tool_cmd)
    cmds.menuItem("turbo_menu_item",
                  label="Turbo",
                  annotation="Launch Turbo Tool UI to apply AdnTurbo and configure the simulation layers.",
                  parent=parent,
                  command=cmd_wrapper.launch_turbo_tool_cmd)
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


def load_item_io_menu(parent):
    """Menu items for I/O options like import and export.

    Args:
        parent (str): name of the parent menu item.
    """
    cmds.menuItem(parent=parent,
                  divider=True,
                  dividerLabel="I/O")
    cmds.menuItem("import_menu_item",
                  label="Import (beta)",
                  annotation="Import an AdonisFX rig into the scene.",
                  parent=parent,
                  command=cmd_wrapper.launch_import_tool_cmd)
    cmds.menuItem("export_menu_item",
                  label="Export (beta)",
                  annotation="Export an AdonisFX rig from the scene.",
                  parent=parent,
                  command=cmd_wrapper.launch_export_tool_cmd)


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
    load_edit_activation_menu(parent)
    load_edit_deformers_menu(parent)
    load_edit_simshape_menu(parent)
    load_edit_skin_menu(parent)
    load_edit_fat_menu(parent)
    load_edit_muscle_menu(parent)
    load_edit_glue_menu(parent)
    load_edit_debug_menu(parent)


def load_licensing_utils_menu(parent):
    """Menu that arranges all menu items related to the licensing system.

    Args:
        parent (str): name of the parent menu item.
    """
    cmds.menuItem(parent=parent,
                  divider=True,
                  dividerLabel="License")
    # 5.1 Activate License
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

    # 4. I/O
    load_item_io_menu(root_menu)

    # 5. License
    load_licensing_utils_menu(root_menu)

    # 6. Help
    load_help_menu(root_menu)


def unload_menu():
    """AdonisFX maya main menu unload. Called on plugin unitialization.
    Remove the AdonisFX menu in case it does exist.
    """
    # Clean and remove root menu if exists
    if cmds.menu(UiConstants.ROOT_MENU_NAME, exists=True):
        cmds.menu(UiConstants.ROOT_MENU_NAME, edit=True, deleteAllItems=True)
        cmds.deleteUI(UiConstants.ROOT_MENU_NAME)
