import maya.cmds as cmds

import adn.tools.maya.simshape as adn_simshape
import adn.ui.maya.launchers as adn_launchers
import adn.commands.maya.scene as adn_scene
import adn.tools.maya.locators as adn_locators
import adn.tools.maya.sensors as adn_sensors
import adn.tools.maya.skin as adn_skin
import adn.tools.maya.ribbon_muscle as adn_ribbon_muscle
import adn.tools.maya.muscle as adn_muscle
import adn.tools.maya.fat as adn_fat
import adn.tools.maya.relax as adn_relax
import adn.tools.maya.glue as adn_glue
import adn.tools.maya.activation as adn_activation
import adn.tools.maya.evaluator_nodes as adn_eval_nodes
import adn.tools.maya.attachments as adn_attachments
import adn.tools.maya.paint as adn_paint
import adn.utils.maya.licensing as adn_licensing
import adn.scripts.maya.adnio as adn_io
from adn.utils.maya.checkers import plugin_check
from adn.utils.constants import DeformerTypes, LocatorTypes, OtherNodeTypes, SensorTypes
from adn.ui.utils.launchers import open_url
from adn.ui.widgets.dialogs import report_error, overwrite_connection_question


def launch_learn_muscle_patches_cmd(cmd_data):
    """Wrapper function to launch muscles patches learning tool. It is called from a menu item
    in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    adn_launchers.launch_learn_muscle_patches()


def launch_sensor_connection_editor_cmd(cmd_data):
    """Wrapper function to launch connect sensors tool. It is called from a menu item 
    in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    adn_launchers.launch_sensor_connection_editor()


def launch_locator_position_creator_cmd(cmd_data):
    """Wrapper function to launch creator of position locators with custom name. It is called from a
    menu item in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    adn_launchers.launch_sensors_locators_creator(adn_locators.create_locator_position, LocatorTypes.POSITION)


def launch_locator_distance_creator_cmd(cmd_data):
    """Wrapper function to launch creator of distance locators with custom name. It is called from a
    menu item in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    adn_launchers.launch_sensors_locators_creator(adn_locators.create_locator_distance, LocatorTypes.DISTANCE)


def launch_locator_rotation_creator_cmd(cmd_data):
    """Wrapper function to launch creator of rotation locators with custom name. It is called from a
    menu item in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    adn_launchers.launch_sensors_locators_creator(adn_locators.create_locator_rotation, LocatorTypes.ROTATION)


def launch_sensor_position_creator_cmd(cmd_data):
    """Wrapper function to launch creator of position sensors with custom name. It is called from a
    menu item in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    adn_launchers.launch_sensors_locators_creator(adn_sensors.create_sensor_position, SensorTypes.POSITION)


def launch_sensor_distance_creator_cmd(cmd_data):
    """Wrapper function to launch creator of distance sensors with custom name. It is called from a
    menu item in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    adn_launchers.launch_sensors_locators_creator(adn_sensors.create_sensor_distance, SensorTypes.DISTANCE)


def launch_sensor_rotation_creator_cmd(cmd_data):
    """Wrapper function to launch creator of rotation sensors with custom name. It is called from a
    menu item in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    adn_launchers.launch_sensors_locators_creator(adn_sensors.create_sensor_rotation, SensorTypes.ROTATION)


def launch_simshape_creator_cmd(cmd_data):
    """Wrapper function to launch the creator of a simshape deformer with custom settings.
    It is called from a menu item in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    adn_launchers.launch_deformer_creator(adn_simshape.apply_simshape, DeformerTypes.SIMSHAPE)


def launch_skin_creator_cmd(cmd_data):
    """Wrapper function to launch the creator of a skin deformer with custom settings.
    It is called from a menu item in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    adn_launchers.launch_deformer_creator(adn_skin.apply_skin, DeformerTypes.SKIN)


def launch_ribbon_muscle_creator_cmd(cmd_data):
    """Wrapper function to launch the creator of a ribbon muscle deformer with custom settings.
    It is called from a menu item in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    adn_launchers.launch_deformer_creator(adn_ribbon_muscle.apply_ribbon_muscle, DeformerTypes.RIBBON)


def launch_muscle_creator_cmd(cmd_data):
    """Wrapper function to launch the creator of a muscle deformer with custom settings.
    It is called from a menu item in the main menu bar.
    
    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    adn_launchers.launch_deformer_creator(adn_muscle.apply_muscle, DeformerTypes.MUSCLE)


def launch_fat_creator_cmd(cmd_data):
    """Wrapper function to launch the creator of a fat deformer with custom settings.
    It is called from a menu item in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    adn_launchers.launch_deformer_creator(adn_fat.apply_fat, DeformerTypes.FAT)


def apply_simshape_cmd(cmd_data):
    """Wrapper function to apply simshape. It is called from a menu item 
    in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.

    Return:
        deformer (str): Name of the deformer created.
    """
    deformer, result = adn_simshape.apply_simshape()
    report_error(result, "creating an {0} deformer".format(DeformerTypes.SIMSHAPE))
    return deformer


def simshape_debug_toggle_cmd(cmd_data):
    """Wrapper function to toggle Simshape debugging. It is called from a menu item 
    in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    result = adn_simshape.simshape_debug_toggle()
    report_error(result, "toggling the {0} debugger".format(DeformerTypes.SIMSHAPE))


def connect_collider_cmd(cmd_data):
    """Wrapper function to add a collider to a Simshape deformer. It is called from a menu item 
    in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    result = adn_simshape.connect_collider()
    report_error(result, "connecting collider to {0}".format(DeformerTypes.SIMSHAPE))


def disconnect_collider_cmd(cmd_data):
    """Wrapper function to remove a collider from a Simshape deformer. It is called from a menu 
    item in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    result = adn_simshape.disconnect_collider()
    report_error(result, "disconnecting collider from {0}".format(DeformerTypes.SIMSHAPE))


def connect_rest_collider_cmd(cmd_data):
    """Wrapper function to add a rest collider to a Simshape deformer. It is called from a menu
    item in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    result = adn_simshape.connect_collider(is_rest=True)
    report_error(result, "connecting rest collider to {0}".format(DeformerTypes.SIMSHAPE))


def disconnect_rest_collider_cmd(cmd_data):
    """Wrapper function to remove a rest collider from a Simshape deformer. It is called from a 
    menu item in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    result = adn_simshape.disconnect_collider(is_rest=True)
    report_error(result, "disconnecting rest collider from {0}".format(DeformerTypes.SIMSHAPE))


def add_rest_mesh_cmd(cmd_data):
    """Wrapper function to connect a given mesh to the rest mesh plug of a Simshape deformer.
    It is called from a menu item in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    mesh_plug = "rest"
    selection = cmds.ls(selection=True, long=True)
    inputs = adn_simshape.get_simshape_mesh_input(selection, mesh_plug)
    response = overwrite_connection_question(inputs, mesh_plug)
    # Abort the addition if the user does not want to override the connection
    if not response:
        return
    result = adn_simshape.add_mesh(mesh_plug, force=response)
    report_error(result, "adding a rest mesh to {0}".format(DeformerTypes.SIMSHAPE))


def remove_rest_mesh_cmd(cmd_data):
    """Wrapper function to disconnect the rest mesh from a Simshape deformer.
    It is called from a menu item in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    result = adn_simshape.remove_mesh("rest")
    report_error(result, "removing the rest mesh from {0}".format(DeformerTypes.SIMSHAPE))


def add_deform_mesh_cmd(cmd_data):
    """Wrapper function to connect a given mesh to the deform mesh plug of a Simshape deformer.
    It is called from a menu item in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    mesh_plug = "deform"
    selection = cmds.ls(selection=True, long=True)
    inputs = adn_simshape.get_simshape_mesh_input(selection, mesh_plug)
    response = overwrite_connection_question(inputs, mesh_plug)
    # Abort the addition if the user does not want to override the connection
    if not response:
        return
    result = adn_simshape.add_mesh(mesh_plug, force=response)
    report_error(result, "adding a deform mesh to {0}".format(DeformerTypes.SIMSHAPE))


def remove_deform_mesh_cmd(cmd_data):
    """Wrapper function to disconnect the deform mesh from a Simshape deformer.
    It is called from a menu item in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    result = adn_simshape.remove_mesh("deform")
    report_error(result, "removing the deform mesh from {0}".format(DeformerTypes.SIMSHAPE))


def add_anim_mesh_cmd(cmd_data):
    """Wrapper function to connect a given mesh to the anim mesh plug of a Simshape deformer.
    It is called from a menu item in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    mesh_plug = "anim"
    selection = cmds.ls(selection=True, long=True)
    inputs = adn_simshape.get_simshape_mesh_input(selection, mesh_plug)
    response = overwrite_connection_question(inputs, mesh_plug)
    # Abort the addition if the user does not want to override the connection
    if not response:
        return
    result = adn_simshape.add_mesh(mesh_plug, force=response)
    report_error(result, "adding an anim mesh to {0}".format(DeformerTypes.SIMSHAPE))


def remove_anim_mesh_cmd(cmd_data):
    """Wrapper function to disconnect the anim mesh from a Simshape deformer.
    It is called from a menu item in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    result = adn_simshape.remove_mesh("anim")
    report_error(result, "removing the anim mesh from {0}".format(DeformerTypes.SIMSHAPE))


def create_locator_distance_cmd(cmd_data):
    """Wrapper function to create a distance locator. It is called from a menu item 
    in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    result = adn_locators.create_locator_distance()
    report_error(result, "creating an {0}".format(LocatorTypes.DISTANCE))


def create_locator_position_cmd(cmd_data):
    """Wrapper function to create a position locator. It is called from a menu item 
    in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    result = adn_locators.create_locator_position()
    report_error(result, "creating an {0}".format(LocatorTypes.POSITION))


def create_locator_rotation_cmd(cmd_data):
    """Wrapper function to create a rotation locator. It is called from a menu item 
    in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    result = adn_locators.create_locator_rotation()
    report_error(result, "creating an {0}".format(LocatorTypes.ROTATION))
  

def create_sensor_distance_cmd(cmd_data):
    """Wrapper function to create a distance sensor. It is called from a menu item 
    in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    result = adn_sensors.create_sensor_distance()
    report_error(result, "creating an {0}".format(SensorTypes.DISTANCE))


def create_sensor_position_cmd(cmd_data):
    """Wrapper function to create a position sensor. It is called from a menu item 
    in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    result = adn_sensors.create_sensor_position()
    report_error(result, "creating an {0}".format(SensorTypes.POSITION))


def create_sensor_rotation_cmd(cmd_data):
    """Wrapper function to create a rotation sensor. It is called from a menu item 
    in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    result = adn_sensors.create_sensor_rotation()
    report_error(result, "creating an {0}".format(SensorTypes.ROTATION))


def apply_skin_cmd(cmd_data):
    """Wrapper function to apply a Skin deformer. It is called from a menu item 
    in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.

    Return:
        deformer (str): Name of the deformer created.
    """
    deformer, result = adn_skin.apply_skin()
    report_error(result, "creating an {0} deformer".format(DeformerTypes.SKIN))
    return deformer


def apply_ribbon_muscle_cmd(cmd_data):
    """Wrapper function to apply a Ribbon muscle deformer. It is called from a menu item 
    in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.

    Return:
        deformer (str): Name of the deformer created.
    """
    deformer, result = adn_ribbon_muscle.apply_ribbon_muscle()
    report_error(result, "creating an {0} deformer".format(DeformerTypes.RIBBON))
    return deformer


def apply_muscle_cmd(cmd_data):
    """Wrapper function to apply a muscle deformer. It is called from a menu item 
    in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.

    Return:
        deformer (str): Name of the deformer created.
    """
    deformer, result = adn_muscle.apply_muscle()
    report_error(result, "creating an {0} deformer".format(DeformerTypes.MUSCLE))
    return deformer


def apply_fat_cmd(cmd_data):
    """Wrapper function to apply a fat deformer. It is called from a menu item
    in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.

    Return:
        deformer (str): Name of the deformer created.
    """
    deformer, result = adn_fat.apply_fat()
    report_error(result, "creating an {0} deformer".format(DeformerTypes.FAT))
    return deformer


def apply_relax_cmd(cmd_data):
    """Wrapper function to apply a relax deformer. It is called from a menu item
    in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.

    Return:
        deformer (str): Name of the deformer created.
    """
    deformer, result = adn_relax.apply_relax()
    report_error(result, "creating an {0} deformer".format(DeformerTypes.RELAX))
    return deformer


def apply_glue_cmd(cmd_data):
    """Wrapper function to apply a glue node. It is called from a menu item
    in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.

    Return:
        node (str): Name of the node created.
    """
    node, result = adn_glue.apply_glue()
    report_error(result, "creating an {0} node".format(OtherNodeTypes.GLUE))
    return node


def add_glue_inputs(cmd_data):
    """Wrapper function to add inputs to a glue node. It is called from a menu item
    in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    result = adn_glue.add_inputs()
    report_error(result, "adding inputs to an {0} node".format(OtherNodeTypes.GLUE))


def remove_glue_inputs(cmd_data):
    """Wrapper function to remove inputs from a glue node. It is called from a menu item
    in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    result = adn_glue.remove_inputs()
    report_error(result, "removing inputs from an {0} node".format(OtherNodeTypes.GLUE))


def show_all_fibers(cmd_data):
    """Wrapper function to enable debug fibers option in all muscles in the scene.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    plugin_check()
    adn_muscle.draw_fibers(True)
    adn_ribbon_muscle.draw_fibers(True)


def hide_all_fibers(cmd_data):
    """Wrapper function to disable debug fibers option in all muscles in the scene.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    plugin_check()
    adn_muscle.draw_fibers(False)
    adn_ribbon_muscle.draw_fibers(False)


def launch_paint_tool_cmd(cmd_data):
    """Wrapper function to launch AdonisFX paint tool. It is called from a menu item 
    in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    adn_launchers.launch_paint_tool()


def launch_skin_merge_cmd(cmd_data):
    """Wrapper function to launch skin merge UI. It is called from a menu item 
    in the main menu bar and from a shelf button.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    adn_launchers.launch_skin_merge()


def play_interactive_cmd(cmd_data):
    """Wrapper function to enter interactive playback mode. It is called from a menu item 
    in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    adn_scene.play_interactive()


def create_edge_evaluator_cmd(cmd_data):
    """Wrapper function to create an edge evaluator. It is called from a menu item 
    in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    result = adn_eval_nodes.create_edge_evaluator()
    report_error(result, "creating an {0} node".format(OtherNodeTypes.EDGE_EVALUATOR))


def connect_simshape_activations_cmd(cmd_data):
    """Wrapper function to connect an edge evaluator to simshape. It is called from a menu item 
    in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    result = adn_simshape.connect_activations()
    report_error(result, "connecting {0} to {1}".format(OtherNodeTypes.EDGE_EVALUATOR, DeformerTypes.SIMSHAPE))


def disconnect_simshape_activations_cmd(cmd_data):
    """Wrapper function to disconnect an edge evaluator from simshape. It is called from a menu item 
    in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    result = adn_simshape.disconnect_activations()
    report_error(result, "disconnecting {0} from {1}".format(OtherNodeTypes.EDGE_EVALUATOR, DeformerTypes.SIMSHAPE))


def launch_skin_merge_edit_cmd(cmd_data):
    """Wrapper function to launch skin merge UI in edit mode. It is called from a menu item 
    in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    adn_launchers.launch_skin_merge(edit=True)


def add_targets(cmd_data):
    """Wrapper function to add targets to a muscle deformer. It is called from a menu item
    in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    result = adn_attachments.add_targets()
    report_error(result, "adding targets to {0}".format(DeformerTypes.MUSCLE))


def remove_targets(cmd_data):
    """Wrapper function to remove targets from a muscle deformer. It is called from a menu item
    in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    result = adn_attachments.remove_targets()
    report_error(result, "removing targets from {0}".format(DeformerTypes.MUSCLE))


def add_slide_segment_constraint(cmd_data):
    """Wrapper function to make the necessary connections to a muscle deformer to create slide on segment
    constraints. It is called from a menu item in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within maya commands in `menuItem` objects.
    """
    result = adn_attachments.add_slide_segment_constraint()
    report_error(result, "adding segments to {0}".format(DeformerTypes.MUSCLE))


def remove_slide_segment_constraint(cmd_data):
    """Wrapper function to remove the connections of slide on segment constraints from a muscle deformer.
    It is called from a menu item in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within maya commands in `menuItem` objects.
    """
    result = adn_attachments.remove_slide_segment_constraint()
    report_error(result, "removing segments from {0}".format(DeformerTypes.MUSCLE))


def activate_license_cmd(cmd_data):
    """Wrapper function to trigger the license activation process.

    Args:
        cmd_data (bool): data sent by default within maya commands in `menuItem` objects.
    """
    adn_licensing.activate_license()


def go_to_documentation_cmd(cmd_data):
    """Wrapper function to open the browser and go to the documentation page.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    open_url("https://www.inbibo.co.uk/docs/adonisfx")


def go_to_tutorials_cmd(cmd_data):
    """Wrapper function to open the browser and go to the tutorials playlist on YouTube.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    open_url("https://www.youtube.com/@inbibo/playlists")


def launch_about_cmd(cmd_data):
    """Wrapper function to open the about dialog from a menu item.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    adn_launchers.launch_about()


def refresh_debug_graph_cmd(cmd_data):
    """Wrapper function to refresh the debug graph for AdonisFX nodes.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    result = adn_locators.refresh_debug_graph()
    report_error(result, "refreshing the debug graph")


def upgrade_deprecated_nodes_cmd(cmd_data):
    """Wrapper function to refresh the node graph and upgrade all deprecated
    nodes making sure that the scene still works the same.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    result = adn_paint.remove_all_weights_display_nodes()
    report_error(result, "upgrading deprecated nodes")


def add_skin_targets(cmd_data):
    """Wrapper function to add targets to an AdnSkin deformer. It is called from a menu item
    in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    result = adn_skin.add_targets()
    report_error(result, "adding targets to {0}".format(DeformerTypes.SKIN))


def remove_skin_targets(cmd_data):
    """Wrapper function to remove targets from an AdnSkin deformer. It is called from a menu item
    in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    result = adn_skin.remove_targets()
    report_error(result, "removing targets from {0}".format(DeformerTypes.SKIN))


def add_fat_base_mesh(cmd_data):
    """Wrapper function to add a base mesh to an AdnFat deformer. It is called from a menu item
    in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    selection = cmds.ls(selection=True, long=True)
    inputs = adn_fat.get_fat_mesh_input(selection)
    response = overwrite_connection_question(inputs, "base mesh")
    # Abort the addition if the user does not want to override the connection
    if not response:
        return
    result = adn_fat.add_base_mesh(force=response)
    report_error(result, "adding a base mesh to {0}".format(DeformerTypes.FAT))


def remove_fat_base_mesh(cmd_data):
    """Wrapper function to remove the base mesh from an AdnFat deformer. It is called from a menu item
    in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    result = adn_fat.remove_base_mesh()
    report_error(result, "removing base mesh from {0}".format(DeformerTypes.FAT))


def create_activation_node_cmd(cmd_data):
    """Wrapper function to create an AdnActivation node. It is called from a menu item
    in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    selection = cmds.ls(selection=True, dagObjects=True, type="mesh", noIntermediate=True)
    muscle_deformers, _ = adn_muscle.find_muscles(selection)
    inputs = adn_activation.get_activation_inputs_from_muscles(muscle_deformers)
    response = overwrite_connection_question(inputs, "activation")
    # Abort the creation if the user does not want to override the connection
    if not response:
        return
    result = adn_activation.create_activation_node(force=response)
    report_error(result, "creating an {0} node".format(OtherNodeTypes.ACTIVATION))


def remove_activation_inputs_cmd(cmd_data):
    """Wrapper function to remove activation inputs from activation nodes or muscles. It is called from a menu item
    in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    result = adn_activation.remove_inputs()
    report_error(result, "removing activation inputs")


def launch_mirror_tool_cmd(cmd_data):
    """Wrapper function to launch mirror tool UI. It is called from a menu item
    in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    adn_launchers.launch_mirror_tool()


def launch_import_tool_cmd(cmd_data):
    """Wrapper function to launch import tool UI. It is called from a menu item
    in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    adn_launchers.launch_import_tool()


def launch_export_tool_cmd(cmd_data):
    """Wrapper function to launch export tool UI. It is called from a menu item
    in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    adn_launchers.launch_export_tool()


def clear_util_cmd(cmd_data):
    """Wrapper function to remove all AdonisFX nodes from the scene.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    adn_io.clear_scene()


def launch_turbo_tool_cmd(cmd_data):
    """Wrapper function to launch AdnTurbo tool UI. It is called from a menu item
    in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    adn_launchers.launch_turbo_tool()
