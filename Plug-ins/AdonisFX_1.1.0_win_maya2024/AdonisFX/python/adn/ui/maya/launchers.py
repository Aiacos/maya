from adn.tools.maya import learn_muscle_patches
from adn.tools.maya import exporter, importer
from adn.tools.maya import sensors_connection_editor
from adn.tools.maya import skin_merge
from adn.tools.maya import attribute_handlers
from adn.tools.maya import paint
from adn.commands.maya import scene
from adn.ui.widgets import licensing
from adn.ui.widgets import learn_muscle_patches_ui as ui_learn_muscle_patches
from adn.ui.widgets import exporter_ui as ui_exporter
from adn.ui.widgets import importer_ui as ui_importer
from adn.ui.widgets import sensors_connection_editor_ui as ui_sensor_connection_editor
from adn.ui.widgets import sensors_locators_creator_ui as ui_sensors_locators_creator
from adn.ui.widgets import deformers_creator_ui as ui_deformers_creator
from adn.ui.widgets import skin_merge_ui as ui_skin_merge
from adn.ui.widgets import dialogs
from adn.ui.maya import paint_ui as ui_paint_tool
from adn.ui.maya.window import main_window
from adn.utils.constants import UiConstants
from adn.utils.maya.checkers import plugin_check


def launch_about():
    """Launches the About dialog."""
    dialog = dialogs.AboutDialog(main_window())
    dialog.show()


def launch_learn_muscle_patches():
    """Launches the LearnMusclePatchesUI."""
    plugin_check()
    global _ADN_LEARN_MUSCLE_PATCHES_UI
    
    try:
        _ADN_LEARN_MUSCLE_PATCHES_UI.deleteLater()
    except:
        pass
        
    _ADN_LEARN_MUSCLE_PATCHES_UI = ui_learn_muscle_patches.LearnMusclePatchesUI(
        dcc_tool=learn_muscle_patches,
        dcc_scene_commands=scene,
        parent=main_window())
    _ADN_LEARN_MUSCLE_PATCHES_UI.show()


def launch_sensor_connection_editor():
    """Launches the SensorsConnectionEditorUI."""
    plugin_check()
    global _ADN_CONNECT_SENSOR_UI

    try:
        _ADN_CONNECT_SENSOR_UI.deleteLater()
    except:
        pass

    _ADN_CONNECT_SENSOR_UI = ui_sensor_connection_editor.SensorsConnectionEditorUI(
        dcc_tool=sensors_connection_editor,
        parent=main_window())
    _ADN_CONNECT_SENSOR_UI.show()


def launch_sensors_locators_creator(creator_method=None, node_type=None):
    """Launches the SensorsLocatorsCreatorUI.

    Args:
        creator_method (str, optional): Method to create sensor or locator. Defaults to None.
        node_type (str, optional): Node type of sensor or locator. Defaults to None.
    """
    plugin_check()
    global _ADN_CREATE_SENSOR_LOCATOR_UI

    try:
        _ADN_CREATE_SENSOR_LOCATOR_UI.deleteLater()
    except:
        pass

    _ADN_CREATE_SENSOR_LOCATOR_UI = ui_sensors_locators_creator.SensorsLocatorsCreatorUI(
        node_creation_method=creator_method,
        node_type=node_type,
        parent=main_window())
    _ADN_CREATE_SENSOR_LOCATOR_UI.show()


def launch_deformer_creator(creator_method=None, node_type=None):
    """Launches the DeformersCreatorUI.

    Args:
        creator_method (str, optional): Method to create a deformer. Defaults to None.
        node_type (str, optional): Node type of deformer. Defaults to None.
    """
    plugin_check()
    global _ADN_CREATE_DEFORMER_UI

    try:
        _ADN_CREATE_DEFORMER_UI.deleteLater()
    except:
        pass

    _ADN_CREATE_DEFORMER_UI = ui_deformers_creator.DeformersCreatorUI(
        node_creation_method=creator_method,
        node_type=node_type,
        dcc_tool=attribute_handlers,
        dcc_scene_commands=scene,
        parent=main_window())
    _ADN_CREATE_DEFORMER_UI.show()


def launch_licensing_dialog(dialog_id, info=None):
    """Wrapper method to launch a custom dialog associated to the given id.

    Args:
        dialog_id (int): Identifier of the dialog to prompt.
        info (int, optional): Extra value to expose in the UI. Defaults to None.

    Returns:
        int or string: user response
    """
    return licensing.licensing_dialog(main_window(), dialog_id, info)


def launch_paint_tool():
    """Launches the PaintToolUI."""
    plugin_check()
    global _ADN_PAINT_TOOL

    try:
        _ADN_PAINT_TOOL.close()
        _ADN_PAINT_TOOL.deleteLater()
    except:
        pass

    result, deformer, node_type, paint_attr, multi_infl_attr, mesh_node = \
        paint.setup_paint_tool(main_window())
    if not result:
        return

    _ADN_PAINT_TOOL = ui_paint_tool.PaintToolUI(
        deformer=deformer,
        node_type=node_type,
        paintable_attributes=paint_attr,
        multi_infl_attr=multi_infl_attr,
        mesh_node=mesh_node,
        dcc_tool=paint,
        parent=main_window())
    _ADN_PAINT_TOOL.show()


def launch_skin_merge(edit=False):
    """Launches the SkinMergeUI.
    
    Args:
        edit (bool, optional): Flag to launch the UI in create or edit mode. Defaults to False.
    """
    plugin_check()
    global _ADN_SKIN_MERGE_UI
    
    try:
        _ADN_SKIN_MERGE_UI.deleteLater()
    except:
        pass

    # Check selection if in edit mode
    deformer = skin_merge.get_skin_merge_deformer() if edit else None
    if edit and not deformer:
        return
        
    _ADN_SKIN_MERGE_UI = ui_skin_merge.SkinMergeUI(
        dcc_tool=skin_merge,
        dcc_scene_commands=scene,
        parent=main_window(),
        edit=edit,
        deformer=deformer)
    _ADN_SKIN_MERGE_UI.show()


def show_paint_tool(cmd_data):
    """Shows the PaintToolUI.

    Args:
        cmd_data (bool): data sent by default within Maya commands.
    """
    plugin_check()
    global _ADN_PAINT_TOOL
    try:
        _ADN_PAINT_TOOL.show()
    except:
        pass


def launch_importer():
    """Launches the Importer Ui."""
    plugin_check()
    global _ADN_IMPORTER_UI

    try:
        _ADN_IMPORTER_UI.deleteLater()
    except:
        pass

    _ADN_IMPORTER_UI = ui_importer.AssetDefinitionImporterUi(
        dcc_tool=importer,
        dcc_scene_commands=scene,
        parent=main_window())
    _ADN_IMPORTER_UI.show()


def launch_exporter():
    """Launches the AssetDefinitionExporterUi."""
    plugin_check()
    global _ADN_EXPORTER_UI

    try:
        _ADN_EXPORTER_UI.deleteLater()
    except:
        pass

    _ADN_EXPORTER_UI = ui_exporter.AssetDefinitionExporterUi(
        dcc_tool=exporter,
        dcc_scene_commands=scene,
        parent=main_window())
    _ADN_EXPORTER_UI.show()