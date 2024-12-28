import adn.tools.maya.simshape as adn_simshape
import adn.ui.maya.launchers as adn_launchers
import adn.commands.maya.scene as adn_scene
import adn.tools.maya.locators as adn_locators
import adn.tools.maya.sensors as adn_sensors
import adn.tools.maya.skin as adn_skin
import adn.tools.maya.skin_merge as adn_skin_merge
import adn.tools.maya.ribbon_muscle as adn_ribbon_muscle
import adn.tools.maya.muscle as adn_muscle
import adn.tools.maya.evaluator_nodes as adn_eval_nodes
import adn.tools.maya.attachments as adn_attachments
import adn.utils.maya.licensing as adn_licensing
from adn.utils.maya.checkers import plugin_check
from adn.utils.constants import DeformerTypes

from adn.ui.utils.launchers import open_url


def launch_learn_muscle_patches_cmd(cmd_data):
    """Wrapper function to launch muscles patches learning tool. It is called from a menu item 
    in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    adn_launchers.launch_learn_muscle_patches()


def launch_importer_cmd(cmd_data):
    """Wrapper function to launch importer tool. It is called from a menu item
    in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within maya commands in `menuItem` objects.
    """
    adn_launchers.launch_importer()


def launch_exporter_cmd(cmd_data):
    """Wrapper function to launch exporter tool. It is called from a menu item
    in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    adn_launchers.launch_exporter()


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
    adn_launchers.launch_sensors_locators_creator(adn_locators.create_locator_position, "AdnLocatorPosition")


def launch_locator_distance_creator_cmd(cmd_data):
    """Wrapper function to launch creator of distance locators with custom name. It is called from a
    menu item in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    adn_launchers.launch_sensors_locators_creator(adn_locators.create_locator_distance, "AdnLocatorDistance")


def launch_locator_rotation_creator_cmd(cmd_data):
    """Wrapper function to launch creator of rotation locators with custom name. It is called from a
    menu item in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    adn_launchers.launch_sensors_locators_creator(adn_locators.create_locator_rotation, "AdnLocatorRotation")


def launch_sensor_position_creator_cmd(cmd_data):
    """Wrapper function to launch creator of position sensors with custom name. It is called from a
    menu item in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    adn_launchers.launch_sensors_locators_creator(adn_sensors.create_sensor_position, "AdnSensorPosition")


def launch_sensor_distance_creator_cmd(cmd_data):
    """Wrapper function to launch creator of distance sensors with custom name. It is called from a
    menu item in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    adn_launchers.launch_sensors_locators_creator(adn_sensors.create_sensor_distance, "AdnSensorDistance")


def launch_sensor_rotation_creator_cmd(cmd_data):
    """Wrapper function to launch creator of rotation sensors with custom name. It is called from a
    menu item in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    adn_launchers.launch_sensors_locators_creator(adn_sensors.create_sensor_rotation, "AdnSensorRotation")


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


def apply_simshape_cmd(cmd_data):
    """Wrapper function to apply simshape. It is called from a menu item 
    in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    adn_simshape.apply_simshape()


def simshape_debug_toggle_cmd(cmd_data):
    """Wrapper function to toggle Simshape debugging. It is called from a menu item 
    in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    adn_simshape.simshape_debug_toggle()


def connect_collider_cmd(cmd_data):
    """Wrapper function to add a collider to a Simshape deformer. It is called from a menu item 
    in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    adn_simshape.connect_collider()


def disconnect_collider_cmd(cmd_data):
    """Wrapper function to remove a collider from a Simshape deformer. It is called from a menu 
    item in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    adn_simshape.disconnect_collider()


def connect_rest_collider_cmd(cmd_data):
    """Wrapper function to add a rest collider to a Simshape deformer. It is called from a menu
    item in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    adn_simshape.connect_collider(is_rest=True)


def disconnect_rest_collider_cmd(cmd_data):
    """Wrapper function to remove a  rest collider from a Simshape deformer. It is called from a 
    menu item in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    adn_simshape.disconnect_collider(is_rest=True)


def add_rest_mesh_cmd(cmd_data):
    """Wrapper function to connect a given mesh to the rest mesh plug of a Simshape deformer.
    It is called from a menu item in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    adn_simshape.add_mesh("rest")


def remove_rest_mesh_cmd(cmd_data):
    """Wrapper function to disconnect the rest mesh from a Simshape deformer.
    It is called from a menu item in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    adn_simshape.remove_mesh("rest")


def add_deform_mesh_cmd(cmd_data):
    """Wrapper function to connect a given mesh to the deform mesh plug of a Simshape deformer.
    It is called from a menu item in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    adn_simshape.add_mesh("deform")


def remove_deform_mesh_cmd(cmd_data):
    """Wrapper function to disconnect the deform mesh from a Simshape deformer.
    It is called from a menu item in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    adn_simshape.remove_mesh("deform")


def add_anim_mesh_cmd(cmd_data):
    """Wrapper function to connect a given mesh to the anim mesh plug of a Simshape deformer.
    It is called from a menu item in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    adn_simshape.add_mesh("anim")


def remove_anim_mesh_cmd(cmd_data):
    """Wrapper function to disconnect the anim mesh from a Simshape deformer.
    It is called from a menu item in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    adn_simshape.remove_mesh("anim")


def create_locator_distance_cmd(cmd_data):
    """Wrapper function to create a distance locator. It is called from a menu item 
    in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    adn_locators.create_locator_distance()


def create_locator_position_cmd(cmd_data):
    """Wrapper function to create a position locator. It is called from a menu item 
    in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    adn_locators.create_locator_position()


def create_locator_rotation_cmd(cmd_data):
    """Wrapper function to create a rotation locator. It is called from a menu item 
    in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    adn_locators.create_locator_rotation()
  

def create_sensor_distance_cmd(cmd_data):
    """Wrapper function to create a distance sensor. It is called from a menu item 
    in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    adn_sensors.create_sensor_distance()


def create_sensor_position_cmd(cmd_data):
    """Wrapper function to create a position sensor. It is called from a menu item 
    in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    adn_sensors.create_sensor_position()


def create_sensor_rotation_cmd(cmd_data):
    """Wrapper function to create a rotation sensor. It is called from a menu item 
    in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    adn_sensors.create_sensor_rotation()


def apply_skin_cmd(cmd_data):
    """Wrapper function to apply a Skin deformer. It is called from a menu item 
    in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    adn_skin.apply_skin()


def apply_ribbon_muscle_cmd(cmd_data):
    """Wrapper function to apply a Ribbon muscle deformer. It is called from a menu item 
    in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    adn_ribbon_muscle.apply_ribbon_muscle()


def apply_muscle_cmd(cmd_data):
    """Wrapper function to apply a muscle deformer. It is called from a menu item 
    in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    adn_muscle.apply_muscle()


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
    adn_eval_nodes.create_edge_evaluator()


def connect_simshape_activations_cmd(cmd_data):
    """Wrapper function to connect an edge evaluator to simshape. It is called from a menu item 
    in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    adn_simshape.connect_activations()


def disconnect_simshape_activations_cmd(cmd_data):
    """Wrapper function to disconnect an edge evaluator from simshape. It is called from a menu item 
    in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    adn_simshape.disconnect_activations()


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
    adn_attachments.add_targets()


def remove_targets(cmd_data):
    """Wrapper function to remove targets from a muscle deformer. It is called from a menu item
    in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within Maya commands in `menuItem` objects.
    """
    adn_attachments.remove_targets()


def add_slide_segment_constraint(cmd_data):
    """Wrapper function to make the necessary connections to a muscle deformer to create slide on segment
    constraints. It is called from a menu item in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within maya commands in `menuItem` objects.
    """
    adn_attachments.add_slide_segment_constraint()


def remove_slide_segment_constraint(cmd_data):
    """Wrapper function to remove the connections of slide on segment constraints from a muscle deformer.
    It is called from a menu item in the main menu bar.

    Args:
        cmd_data (bool): data sent by default within maya commands in `menuItem` objects.
    """
    adn_attachments.remove_slide_segment_constraint()


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
    adn_locators.refresh_debug_graph()
